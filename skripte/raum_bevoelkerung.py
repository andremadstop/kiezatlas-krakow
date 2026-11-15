"""Leser und Rechenbausteine für Gliederung und Bevölkerung (Kraków), ohne Netz und ohne Datenbank.

Genutzt von skripte/02_bevoelkerung.py und pruefen/D4_bevoelkerung.py. Nur Pakete aus
requirements.txt (pyproj, shapely, numpy über skripte/osm_pbf.py) und die Standardbibliothek; XLSX, DBF, SHP und
GeoPackage werden hier selbst gelesen, damit keine weiteren Pakete nötig sind.

Eingänge (Pfade relativ zu $KIEZ_DATEN, Standard ../kiezatlas-daten/krakow; Beschreibung in quellen-D4.md):
  2026-11-13/03_gebaeude/1261_SHP.zip     BDOT10k Powiat 1261, Schicht OT_ADJA_A (Stadt und vier delegatury)
  2026-11-13/02_zensus/PL_PD_3035_GPKG.zip Eurostat Census-Gitter 2021, Polen, 1 km
  2026-11-13/02_zensus/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx   GUS NSP 2021
  eingang/                                Handdownloads (OSM-Grenzen der dzielnice, Geometrie der rejony)

Koordinatensysteme: Flächen in rechen_srid (skripte/ort_konfig.py), Gitterzuordnung in EPSG:3035 (INSPIRE-Gitter,
flächentreu), Ausgabe für die Seiten in EPSG:4326 auf 5 Stellen. Das System der BDOT10k-Dateien steht in der .prj
und wird von dort gelesen, nicht im Code festgelegt.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import struct
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from pyproj import CRS, Transformer
from shapely import wkb as shapely_wkb
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box, shape
from shapely.ops import polygonize, transform, unary_union
from shapely.prepared import prep

import ort_konfig

WURZEL = Path(__file__).resolve().parent.parent
STAND_ROH = "2026-11-13"
BDOT_ZIP = f"{STAND_ROH}/03_gebaeude/1261_SHP.zip"
BDOT_ADJA = "PL.PZGiK.283.BDOT10k.1261__OT_ADJA_A"
GITTER_ZIP = f"{STAND_ROH}/02_zensus/PL_PD_3035_GPKG.zip"
NSP_XLSX = f"{STAND_ROH}/02_zensus/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx"
MSIP_ZIP = f"{STAND_ROH}/01_stadtteile/Dzielnice_JSON.zip"   # nur Gegenprobe, nie ausliefern
TERYT_STADT_GMINA = "1261011"
TERYT_POWIAT = "1261"
GITTER_SRID = 3035
MINDESTFALLZAHL = 100
OSM_EBENE = "9"            # admin_level der 18 dzielnice in OSM (Auszug Małopolska, Stand 12.11.2026)

ROEMISCH = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI",
            "XVII", "XVIII"]


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")


def eingang_ordner() -> Path:
    return daten_ordner() / "eingang"


class EingangFehlt(Exception):
    """Eine Eingabedatei fehlt (Handdownload ausstehend); kein Fehler der Rechnung."""


class Abbruch(Exception):
    """Eingabe vorhanden, aber nicht verwendbar (Zuordnung nicht eindeutig, Pflichtangabe fehlt)."""


# ------------------------------------------------------------------------------------------- Koordinaten

def _tr(von: CRS | int, nach: CRS | int):
    return Transformer.from_crs(von, nach, always_xy=True).transform


def rechen_crs() -> CRS:
    return CRS.from_epsg(ort_konfig.RECHEN_SRID)


def flaeche_km2(geom_wgs84) -> float:
    return transform(_tr(4326, rechen_crs()), geom_wgs84).area / 1e6


def runden_geom(g, stellen: int = 5) -> dict:
    """GeoJSON-Geometrie mit gerundeten Koordinaten (Ringe bleiben geschlossen)."""
    def ring(r):
        return [[round(x, stellen), round(y, stellen)] for x, y in r.coords]

    def poly(p: Polygon):
        return [ring(p.exterior), *[ring(i) for i in p.interiors]]
    if isinstance(g, Polygon):
        return {"type": "Polygon", "coordinates": poly(g)}
    if isinstance(g, MultiPolygon):
        return {"type": "MultiPolygon", "coordinates": [poly(p) for p in g.geoms]}
    raise ValueError(f"Geometrietyp {g.geom_type} nicht erwartet")


VEREINFACHUNG_M = 3.0   # Toleranz für die Kartengeometrie der dzielnice (gerechnet wird mit der vollen Geometrie)


def grenzen_vereinfachen(flaechen: dict[str, object], toleranz_m: float = VEREINFACHUNG_M) -> dict[str, object]:
    """Gemeinsame Grenzen bleiben gemeinsam (shapely.coverage_simplify in rechen_srid); nur für die Karte."""
    import shapely
    schluessel = list(flaechen)
    hin, zurueck = _tr(4326, rechen_crs()), _tr(rechen_crs(), 4326)
    geo = shapely.coverage_simplify([transform(hin, flaechen[k]) for k in schluessel], toleranz_m)
    return {k: transform(zurueck, g) for k, g in zip(schluessel, geo)}


def nur_flaechen(g):
    """Polygon/MultiPolygon aus einer beliebigen Geometrie (Linien und Punkte aus Schnitten entfallen)."""
    if isinstance(g, (Polygon, MultiPolygon)):
        return g
    teile = [x for x in getattr(g, "geoms", []) if isinstance(x, (Polygon, MultiPolygon))]
    return unary_union(teile) if teile else Polygon()


# ------------------------------------------------------------------------------------------- DBF und SHP

def _zip_oder_ordner(quelle: Path, name: str) -> bytes:
    if quelle.suffix.lower() == ".zip":
        with zipfile.ZipFile(quelle) as z:
            treffer = [n for n in z.namelist() if n.endswith(name)]
            if len(treffer) != 1:
                raise Abbruch(f"{quelle.name}: {len(treffer)} Einträge auf {name}")
            return z.read(treffer[0])
    return (quelle / name).read_bytes() if quelle.is_dir() else quelle.with_name(name).read_bytes()


def dbf_lesen(daten: bytes, kodierung: str = "utf-8") -> list[dict]:
    n, laenge_kopf, laenge_satz = struct.unpack("<IHH", daten[4:12])
    felder = []
    for i in range(32, laenge_kopf - 1, 32):
        f = daten[i:i + 32]
        if f[0] == 0x0D:
            break
        felder.append((f[:11].split(b"\0")[0].decode("ascii"), chr(f[11]), f[16]))
    saetze = []
    for r in range(n):
        s = daten[laenge_kopf + r * laenge_satz: laenge_kopf + (r + 1) * laenge_satz]
        if s[:1] == b"*":       # gelöscht
            continue
        pos, werte = 1, {}
        for name, typ, laenge in felder:
            roh = s[pos:pos + laenge].decode(kodierung, "replace").strip()
            pos += laenge
            if typ in "NF" and roh:
                try:
                    werte[name] = int(roh) if re.fullmatch(r"-?\d+", roh) else float(roh)
                except ValueError:
                    werte[name] = roh
            else:
                werte[name] = roh
        saetze.append(werte)
    return saetze


def _signierte_flaeche(punkte: list[tuple[float, float]]) -> float:
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(punkte, punkte[1:])) / 2


def shp_polygone(daten: bytes) -> list:
    """Shapefile-Polygone (Typ 5, auch 15/25 ohne Z/M) als shapely-Geometrien; Außenringe im Uhrzeigersinn."""
    aus = []
    pos = 100
    while pos < len(daten):
        _nr, laenge = struct.unpack(">ii", daten[pos:pos + 8])
        inhalt = daten[pos + 8: pos + 8 + 2 * laenge]
        pos += 8 + 2 * laenge
        typ = struct.unpack("<i", inhalt[:4])[0]
        if typ == 0:
            aus.append(None)
            continue
        if typ not in (5, 15, 25):
            raise Abbruch(f"Shapefile-Typ {typ} statt Polygon")
        n_teile, n_punkte = struct.unpack("<ii", inhalt[36:44])
        teile = list(struct.unpack(f"<{n_teile}i", inhalt[44:44 + 4 * n_teile]))
        start = 44 + 4 * n_teile
        xy = struct.unpack(f"<{2 * n_punkte}d", inhalt[start:start + 16 * n_punkte])
        punkte = list(zip(xy[0::2], xy[1::2]))
        ringe = [punkte[a:b] for a, b in zip(teile, teile[1:] + [n_punkte])]
        aussen = [Polygon(r) for r in ringe if _signierte_flaeche(r) < 0]
        innen = [Polygon(r) for r in ringe if _signierte_flaeche(r) >= 0]
        polys = []
        for a in aussen:
            loecher = [i.exterior.coords for i in innen if a.contains(i.representative_point())]
            polys.append(Polygon(a.exterior.coords, loecher))
        aus.append(polys[0] if len(polys) == 1 else MultiPolygon(polys))
    return aus


def shp_lesen(quelle: Path, stamm: str) -> tuple[list[dict], list, CRS]:
    """Attribute, Geometrien und Koordinatensystem (aus .prj) einer Shapefile-Schicht in einem Zip oder Ordner."""
    try:
        kodierung = _zip_oder_ordner(quelle, stamm + ".cpg").decode("ascii").strip() or "utf-8"
    except (KeyError, FileNotFoundError, Abbruch):
        kodierung = "utf-8"
    kodierung = {"UTF-8": "utf-8", "65001": "utf-8"}.get(kodierung.upper(), kodierung)
    attr = dbf_lesen(_zip_oder_ordner(quelle, stamm + ".dbf"), kodierung)
    geom = shp_polygone(_zip_oder_ordner(quelle, stamm + ".shp"))
    crs = CRS.from_wkt(_zip_oder_ordner(quelle, stamm + ".prj").decode("utf-8", "replace"))
    if len(attr) != len(geom):
        raise Abbruch(f"{stamm}: {len(attr)} Sätze in .dbf, {len(geom)} in .shp")
    return attr, geom, crs


# ------------------------------------------------------------------------------------------- XLSX (nur lesen)

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_NS_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def xlsx_zeilen(pfad: Path, blatt: str):
    """Zeilen eines Tabellenblatts als dict Spalte -> Wert (Text oder Zahl als Text)."""
    with zipfile.ZipFile(pfad) as z:
        geteilt = []
        if "xl/sharedStrings.xml" in z.namelist():
            for _, el in ET.iterparse(z.open("xl/sharedStrings.xml")):
                if el.tag == _NS + "si":
                    geteilt.append("".join(t.text or "" for t in el.iter(_NS + "t")))
                    el.clear()
        mappe = ET.fromstring(z.read("xl/workbook.xml"))
        rid = next((s.get(_NS_REL + "id") for s in mappe.iter(_NS + "sheet") if s.get("name") == blatt), None)
        if rid is None:
            raise Abbruch(f"{pfad.name}: kein Blatt {blatt!r}")
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        ziel = next(r.get("Target") for r in rels if r.get("Id") == rid)
        for _, el in ET.iterparse(z.open("xl/" + ziel.lstrip("/").removeprefix("xl/"))):
            if el.tag != _NS + "row":
                continue
            zeile = {"_r": int(el.get("r", 0))}
            for c in el.findall(_NS + "c"):
                spalte = re.match(r"[A-Z]+", c.get("r")).group()
                v = c.find(_NS + "v")
                if c.get("t") == "inlineStr":
                    zeile[spalte] = "".join(t.text or "" for t in c.iter(_NS + "t"))
                elif v is not None:
                    zeile[spalte] = geteilt[int(v.text)] if c.get("t") == "s" else v.text
            yield zeile
            el.clear()


# ------------------------------------------------------------------------------------------- NSP 2021 je rejon

NSP_SPALTEN = {   # Spalte -> Feld; Kopf der Tabelle in Zeile 3 bis 5 (wird beim Lesen geprüft)
    "F": "ogolem", "G": "m", "H": "k",
    "I": "oek_vor", "J": "oek_erwerb", "M": "oek_nach",
    "N": "a0_9", "O": "a10_19", "P": "a20_29", "Q": "a30_39", "R": "a40_49", "S": "a50_59", "T": "a60_69",
    "U": "a70_79", "V": "a80p",
}
NSP_KOPF = {"F3": "Ogółem", "G4": "mężczyźni", "H4": "kobiety", "I4": "przed-produk-cyjny", "J4": "produkcyjny",
            "M4": "poproduk-cyjny", "N4": "0-9 lat", "O4": "10-19", "P4": "20-29", "Q4": "30-39", "R4": "40-49",
            "S4": "50-59", "T4": "60-69", "U4": "70-79", "V4": "80 lat i więcej"}
ALTER_10 = ["a0_9", "a10_19", "a20_29", "a30_39", "a40_49", "a50_59", "a60_69", "a70_79", "a80p"]
OEK = ["oek_vor", "oek_erwerb", "oek_nach"]


@dataclass
class Nsp:
    stadt: dict
    delegatury: dict[str, dict]          # Symbol (7 Stellen) -> Werte, mit name
    rejony: dict[str, dict]              # Kennung (6 Stellen) -> Werte, mit delegatura
    obwody_summe: int
    obwody_zahl: int
    kopf_geprueft: list[str]
    striche: int                          # Zellen mit „-“ in den Kraków-Zeilen (als 0 gelesen)


def nsp_lesen(pfad: Path) -> Nsp:
    stadt, deleg, rejony = None, {}, {}
    obw_summe = obw_zahl = striche = 0
    kopf: dict[str, str] = {}
    aktuelle_deleg = None
    for z in xlsx_zeilen(pfad, "Małopolskie"):
        if z["_r"] <= 5:
            for zelle, erwartet in NSP_KOPF.items():
                sp, zeile_soll = re.match(r"([A-Z]+)(\d+)", zelle).groups()
                if int(zeile_soll) == z["_r"] and z.get(sp) == erwartet:
                    kopf[zelle] = erwartet
        if z.get("B") != "Kraków":
            continue
        werte = {}
        for sp, f in NSP_SPALTEN.items():
            roh = (z.get(sp) or "").strip()
            if roh == "-":            # GUS-Zeichen „zjawisko nie wystąpiło“ (Erscheinung kam nicht vor) = 0
                striche += 1
                werte[f] = 0
            elif re.fullmatch(r"\d+", roh):
                werte[f] = int(roh)
            else:
                raise Abbruch(f"NSP-Tabelle Zeile {z['_r']}, Spalte {sp}: Wert {roh!r} nicht lesbar")
        art = z.get("D")
        if art == "miasto na prawach powiatu":
            stadt = {"symbol": z.get("E"), **werte}
        elif art == "delegatura":
            aktuelle_deleg = z.get("E")
            deleg[aktuelle_deleg] = {"name": z.get("C"), **werte}
        elif art == "rejon statystyczny":
            rid = z.get("E")
            if rid in rejony:
                raise Abbruch(f"rejon {rid} doppelt")
            rejony[rid] = {"delegatura": aktuelle_deleg, "delegatura_name": z.get("C"), **werte}
        elif art == "obwód spisowy":
            obw_summe += werte["ogolem"]
            obw_zahl += 1
    fehlend = sorted(set(NSP_KOPF) - set(kopf))
    if fehlend:
        raise Abbruch(f"Kopf der NSP-Tabelle anders als erwartet, fehlt: {fehlend}")
    if stadt is None:
        raise Abbruch("Zeile „miasto na prawach powiatu“ für Kraków fehlt")
    return Nsp(stadt, deleg, rejony, obw_summe, obw_zahl, sorted(kopf), striche)


def nsp_gleichungen(nsp: Nsp) -> list[tuple[str, int, int]]:
    """(Gleichung, links, rechts) der Regel 10 des Prüfprotokolls."""
    g = []
    s = nsp.stadt["ogolem"]
    g.append(("Σ rejony = Stadt", sum(r["ogolem"] for r in nsp.rejony.values()), s))
    g.append(("Σ obwody = Stadt", nsp.obwody_summe, s))
    g.append(("Σ delegatury = Stadt", sum(d["ogolem"] for d in nsp.delegatury.values()), s))
    for sym, d in sorted(nsp.delegatury.items()):
        g.append((f"Σ rejony in {d['name']} = Zeile {sym}",
                  sum(r["ogolem"] for r in nsp.rejony.values() if r["delegatura"] == sym), d["ogolem"]))
    einheiten = [("Stadt", nsp.stadt)] + [(d["name"], d) for _, d in sorted(nsp.delegatury.items())]
    for name, w in einheiten:
        g.append((f"{name}: m + k = ogółem", w["m"] + w["k"], w["ogolem"]))
        g.append((f"{name}: Σ 10-Jahres-Gruppen = ogółem", sum(w[a] for a in ALTER_10), w["ogolem"]))
        g.append((f"{name}: Σ ökonomische Gruppen = ogółem", sum(w[a] for a in OEK), w["ogolem"]))
    rej_m = sum(1 for r in nsp.rejony.values() if r["m"] + r["k"] != r["ogolem"])
    rej_a = sum(1 for r in nsp.rejony.values() if sum(r[a] for a in ALTER_10) != r["ogolem"])
    rej_o = sum(1 for r in nsp.rejony.values() if sum(r[a] for a in OEK) != r["ogolem"])
    g.append(("rejony mit m + k ≠ ogółem", rej_m, 0))
    g.append(("rejony mit Σ 10-Jahres-Gruppen ≠ ogółem", rej_a, 0))
    g.append(("rejony mit Σ ökonomische Gruppen ≠ ogółem", rej_o, 0))
    return g


# ------------------------------------------------------------------------------------------- Eurostat-Gitter

@dataclass
class Zelle:
    gid: str
    e: int          # Ecke unten links, EPSG:3035
    n: int
    res: int
    t: int | None
    u15: int | None
    a15_64: int | None
    a65p: int | None
    status: tuple

    @property
    def quadrat(self) -> Polygon:
        return box(self.e, self.n, self.e + self.res, self.n + self.res)

    @property
    def mitte(self) -> Point:
        return Point(self.e + self.res / 2, self.n + self.res / 2)


def gitter_lesen(zip_pfad: Path, rahmen_3035: tuple[float, float, float, float]) -> tuple[list[Zelle], dict]:
    """Zellen des Census-Gitters, deren Quadrat den Rahmen (EPSG:3035) berührt, und Zählungen zur Datei."""
    with zipfile.ZipFile(zip_pfad) as z, tempfile.TemporaryDirectory(prefix="kiez-gitter-") as tmp:
        namen = [n for n in z.namelist() if n.lower().endswith(".gpkg")]
        if len(namen) != 1:
            raise Abbruch(f"{zip_pfad.name}: {len(namen)} GeoPackage-Dateien")
        ziel = Path(tmp) / "gitter.gpkg"
        with z.open(namen[0]) as q, ziel.open("wb") as f:
            while block := q.read(1 << 22):
                f.write(block)
        con = sqlite3.connect(f"file:{ziel}?mode=ro", uri=True)
        tabellen = [r[0] for r in con.execute("select table_name from gpkg_contents where data_type='features'")]
        if len(tabellen) != 1:
            raise Abbruch(f"GeoPackage mit {len(tabellen)} Feature-Tabellen")
        t = tabellen[0]
        srs = con.execute("select srs_id from gpkg_geometry_columns where table_name=?", (t,)).fetchone()[0]
        gesamt = con.execute(f'select count(*) from "{t}"').fetchone()[0]
        w, s, o, n = rahmen_3035
        zellen = []
        for gid, T, a, b, c, st, sv, kl, nz in con.execute(
                f'select GRD_ID, T, Y_LT15, "Y_1564", Y_GE65, T_OBS_STATUS, T_SPECIAL_VALUE, '
                f'T_CONVENTIONALLY_LOCATED_PROPORTION, T_NOT_COUNTED_PROPORTION from "{t}"'
                if _spalte(con, t, "Y_1564") else
                f'select GRD_ID, T_OBS_VALUE, Y_LT15_OBS_VALUE, "Y15-64_OBS_VALUE", Y_GE65_OBS_VALUE, T_OBS_STATUS, '
                f'T_SPECIAL_VALUE, T_CONVENTIONALLY_LOCATED_PROPORTION, T_NOT_COUNTED_PROPORTION from "{t}"'):
            m = re.fullmatch(r"CRS3035RES(\d+)mN(\d+)E(\d+)", gid)
            if not m:
                raise Abbruch(f"Gitterkennung {gid!r} nicht im INSPIRE-Muster")
            res, nn, ee = map(int, m.groups())
            if ee + res < w or ee > o or nn + res < s or nn > n:
                continue
            zellen.append(Zelle(gid, ee, nn, res, _int(T), _int(a), _int(b), _int(c),
                                (st, sv, (kl or 0) > 0, (nz or 0) > 0)))
        con.close()
    return zellen, {"datei": namen[0], "tabelle": t, "srs_id": srs, "zellen_gesamt": gesamt,
                    "zellen_im_rahmen": len(zellen)}


def _spalte(con, t, name) -> bool:
    return any(r[1] == name for r in con.execute(f'pragma table_info("{t}")'))


def _int(x) -> int | None:
    if x is None:
        return None
    return int(round(float(x)))


# ------------------------------------------------------------------------------------------- Gliederung

@dataclass
class Einheit:
    schluessel: str            # nr der dzielnica, Gruppen-id oder "stadt"
    name: str
    geom: object               # EPSG:4326
    teryt: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class Gliederung:
    stadt: Einheit
    gruppen: dict[str, Einheit]          # Gruppen-id aus der Ortskonfiguration -> delegatura
    dzielnice: dict[str, Einheit] | None  # nr -> dzielnica, None solange der Handdownload fehlt
    dzielnice_quelle: str | None
    dzielnice_grund: str | None
    zaehlung: dict


def bdot_verwaltung(bdot_zip: Path, konfig: dict) -> tuple[Einheit, dict[str, Einheit], dict]:
    attr, geom, crs = shp_lesen(bdot_zip, BDOT_ADJA)
    nach_wgs = _tr(crs, 4326)
    stadt = None
    deleg = {}
    for a, g in zip(attr, geom):
        if a.get("RODZAJ") == "gmina" and a.get("IDTERYTJED") == TERYT_STADT_GMINA:
            stadt = Einheit("stadt", a["NAZWA"], transform(nach_wgs, g), a["IDTERYTJED"],
                            {"wersja": a.get("WERSJA"), "zrodlo": a.get("ZRO_DANYCH")})
        elif a.get("RODZAJ") == "dzielnica lub delegatura" and a.get("IDTERYTNAD") == TERYT_POWIAT:
            deleg[a["IDTERYTJED"]] = Einheit(a["IDTERYTJED"], a["NAZWA"], transform(nach_wgs, g), a["IDTERYTJED"],
                                             {"wersja": a.get("WERSJA"), "zrodlo": a.get("ZRO_DANYCH")})
    if stadt is None:
        raise Abbruch(f"BDOT10k {BDOT_ADJA}: keine gmina {TERYT_STADT_GMINA}")
    if len(deleg) != 4:
        raise Abbruch(f"BDOT10k {BDOT_ADJA}: {len(deleg)} delegatury statt 4")
    gruppen = {}
    for gr in konfig["gliederung"]["gruppen"]:
        treffer = [d for d in deleg.values() if d.name == f"Kraków-{gr['name']}"]
        if len(treffer) != 1:
            raise Abbruch(f"Gruppe {gr['id']} ({gr['name']}): {len(treffer)} delegatury in BDOT10k")
        gruppen[gr["id"]] = Einheit(gr["id"], treffer[0].name, treffer[0].geom, treffer[0].teryt, treffer[0].extra)
    return stadt, gruppen, {"bdot_saetze": len(attr), "srs_bdot": crs.name}


# ---- OSM-Grenzen der dzielnice

def roemisch_aus(text: str) -> str | None:
    """Römische Ziffer I…XVIII aus ref oder „Dzielnica XIV Czyżyny“ / „dzielnica X Swoszowice“ (OSM `official_name`,
    Groß- und Kleinschreibung des Worts „dzielnica“ wechseln in OSM, Stand 12.11.2026); sonst None."""
    if not text:
        return None
    t = text.strip()
    if t in ROEMISCH:
        return t
    m = re.match(r"^\s*dzielnica\s+([IVXL]+)\b", t, re.IGNORECASE)
    return m.group(1) if m and m.group(1) in ROEMISCH else None


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("–", "-").replace("—", "-")).strip().casefold()


def dzielnice_zuordnen(kandidaten: list[tuple[dict, object]], konfig: dict) -> tuple[dict[str, Einheit], dict]:
    """Ordnet Flächen (Tags, Geometrie in 4326) den 18 dzielnice der Ortskonfiguration zu; Abbruch bei Mehrdeutigkeit."""
    teile = konfig["gliederung"]["teile"]
    nach_roem = {t["roemisch"]: t for t in teile}
    nach_name = {_norm(t["name"]): t for t in teile}
    # Rang 0: Treffer über die römische Ziffer (ref oder „Dzielnica XIV …“), Rang 1: nur über den Namen. Je dzielnica
    # zählen nur die Treffer des besten Rangs, damit gleichnamige Flächen ohne Ziffer (z. B. ein Osiedle „Nowa Huta“)
    # die Grenzrelation mit Ziffer nicht verdrängen; zwei Treffer gleichen Rangs bleiben ein Abbruch.
    # Flächen mit admin_level ungleich OSM_EBENE (in Kraków tragen auch historische Viertel, admin_level 11, die Namen
    # der dzielnice, etwa „Krowodrza“ oder „Bronowice“) zählen als andere Ebene und werden übergangen.
    zu: dict[str, list] = {t["nr"]: [] for t in teile}
    ohne = verdraengt = andere_ebene = 0
    for tags, g in kandidaten:
        if tags.get("boundary") not in (None, "administrative"):
            continue
        if tags.get("admin_level") not in (None, OSM_EBENE):
            andere_ebene += 1
            continue
        r = (roemisch_aus(tags.get("ref", "")) or roemisch_aus(tags.get("official_name", ""))
             or roemisch_aus(tags.get("name", "")))
        t = nach_roem.get(r) if r else None
        rang = 0
        if t is None:
            name = _norm(tags.get("name", "")).removeprefix("dzielnica ").strip()
            t, rang = nach_name.get(name), 1
        if t is None:
            ohne += 1
            continue
        for feld in ("name", "official_name"):
            if r and tags.get(feld):
                # Name ohne „Dzielnica <Ziffer>“ muss genau der Name der Ortskonfiguration sein (nicht nur enthalten:
                # „Podgórze“ steckt auch in „Podgórze Duchackie“); ein Name nur aus Ziffer bleibt erlaubt.
                rest = re.sub(r"^[ivxl]+\b", "", _norm(tags[feld]).removeprefix("dzielnica ").strip()).strip(" -.")
                if rest and rest != _norm(t["name"]):
                    raise Abbruch(f"Ziffer {r} passt nicht zu {feld} {tags[feld]!r} (erwartet {t['name']})")
        zu[t["nr"]].append((rang, tags, g))
    for nr, l in zu.items():
        if l:
            best = min(x[0] for x in l)
            verdraengt += sum(1 for x in l if x[0] != best)
            zu[nr] = [(tags, g) for rang, tags, g in l if rang == best]
    fehlt = [nr for nr, l in zu.items() if not l]
    doppelt = [nr for nr, l in zu.items() if len(l) > 1]
    if fehlt or doppelt:
        raise Abbruch(f"dzielnice nicht eindeutig: ohne Fläche {fehlt}, mehrfach {doppelt}")
    aus = {}
    for t in teile:
        tags, g = zu[t["nr"]][0]
        g = g.buffer(0) if not g.is_valid else g
        aus[t["nr"]] = Einheit(t["nr"], t["name"], g, None, {"osm_id": tags.get("@id") or tags.get("id"),
                                                             "osm_name": tags.get("name")})
    return aus, {"kandidaten": len(kandidaten), "andere_ebene": andere_ebene, "ohne_zuordnung": ohne,
                 "nur_name_verdraengt": verdraengt, "zugeordnet": len(aus)}


def osm_geojson_kandidaten(pfad: Path) -> list[tuple[dict, object]]:
    fc = json.loads(pfad.read_text(encoding="utf-8"))
    aus = []
    for f in fc.get("features", []):
        g = f.get("geometry")
        if not g or g.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        p = dict(f.get("properties") or {})
        if isinstance(p.get("tags"), dict):          # Format von osmtogeojson mit verschachtelten Tags
            p = {**p["tags"], "@id": p.get("id")}
        if "id" in f and "@id" not in p:
            p["@id"] = f["id"]
        aus.append((p, shape(g)))
    return aus


def osm_pbf_kandidaten(pfad: Path, rahmen: tuple[float, float, float, float]) -> list[tuple[dict, object]]:
    """Grenzrelationen „Dzielnica …“ aus einer OSM-PBF (zwei Durchgänge, Ringe über polygonize)."""
    import osm_pbf

    def rel_wahl(t):
        return (t.get("boundary") == "administrative" and t.get("type") in ("boundary", "multipolygon")
                and any(roemisch_aus(t.get(k, "")) is not None for k in ("ref", "official_name", "name")))
    erst = osm_pbf.lies(pfad, rechteck=None, knoten_wahl=lambda t: False, weg_wahl=lambda t: False,
                        relation_wahl=rel_wahl, knoten_lesen=False)
    # Mitglieder kommen als (Art, Kennung, Rolle), Art „n“, „w“ oder „r“ (skripte/osm_pbf.py)
    weg_ids = {ref for _rid, _t, m in erst.relationen for (art, ref, _rolle) in m if art == "w"}
    w, s, o, n = rahmen
    zweit = osm_pbf.lies(pfad, rechteck=(w - 0.05, s - 0.05, o + 0.05, n + 0.05), knoten_wahl=lambda t: False,
                         weg_wahl=lambda t: False, relation_wahl=lambda t: False, weg_ids=weg_ids)
    wege = {wid: refs for wid, _t, refs in zweit.wege}
    aus = []
    for rid, tags, mitglieder in erst.relationen:
        linien = {"outer": [], "inner": []}
        ringwege = [(ref, rolle) for art, ref, rolle in mitglieder if art == "w"]
        fehlend = [ref for ref, _rolle in ringwege if ref not in wege]
        koord = {ref: zweit.koordinaten(wege[ref]) for ref, _rolle in ringwege if ref in wege}
        if not any(ok.any() for _lon, _lat, ok in koord.values()):
            continue                        # ganz außerhalb des Rahmens: gleich benannte Grenze in einem anderen Ort
        if fehlend:
            raise Abbruch(f"Relation {rid}: {len(fehlend)} Wege fehlen im Auszug (z. B. {fehlend[0]})")
        for ref, rolle in ringwege:
            lon, lat, ok = koord[ref]
            if not ok.all():
                raise Abbruch(f"Relation {rid}: Weg {ref} mit Knoten außerhalb des Leserechtecks")
            linien["inner" if rolle == "inner" else "outer"].append(LineString(list(zip(lon, lat))))
        aussen = unary_union(list(polygonize(unary_union(linien["outer"])))) if linien["outer"] else Polygon()
        innen = unary_union(list(polygonize(unary_union(linien["inner"])))) if linien["inner"] else Polygon()
        g = aussen.difference(innen) if not innen.is_empty else aussen
        if g.is_empty:
            continue
        aus.append(({**tags, "@id": f"relation/{rid}"}, g))
    return aus


def dzielnice_aus_eingang(konfig: dict) -> tuple[dict[str, Einheit] | None, str | None, str | None, dict]:
    """OSM-Grenzen aus eingang/: zuerst osm_dzielnice_krakow.geojson, sonst *.osm.pbf. (None, None, Grund, {}) wenn keins da."""
    ein = eingang_ordner()
    gj = ein / "osm_dzielnice_krakow.geojson"
    pbfs = sorted(ein.glob("*.osm.pbf")) if ein.is_dir() else []
    stand = None
    if gj.exists():
        kand, quelle = osm_geojson_kandidaten(gj), f"eingang/{gj.name}"
    elif len(pbfs) > 1:
        raise Abbruch(f"mehrere OSM-Auszüge in eingang/ ({', '.join(p.name for p in pbfs)}): genau einen liegen lassen "
                      "oder eingang/osm_dzielnice_krakow.geojson anlegen")
    elif pbfs:
        import osm_pbf
        from datetime import UTC, datetime
        kopf = osm_pbf.kopf_lesen(pbfs[0])
        if kopf and kopf.zeitstempel:          # osmosis_replication_timestamp des Auszugs
            stand = datetime.fromtimestamp(kopf.zeitstempel, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        kand, quelle = osm_pbf_kandidaten(pbfs[0], tuple(konfig["karte"]["rahmen"])), f"eingang/{pbfs[0].name}"
    else:
        return None, None, ("Grenzen der dzielnice fehlen: Handdownload OSM (eingang/osm_dzielnice_krakow.geojson "
                            "oder eingang/*.osm.pbf) steht aus"), {}
    teile, z = dzielnice_zuordnen(kand, konfig)
    return teile, quelle, None, {**z, "stand_osm": stand, "datei": quelle.removeprefix("eingang/")}


def gliederung_laden(konfig: dict, mit_dzielnice: bool = True,
                     dzielnice_ersatz: tuple[dict[str, Einheit], str] | None = None) -> Gliederung:
    d = daten_ordner()
    if not (d / BDOT_ZIP).exists():
        raise EingangFehlt(f"{BDOT_ZIP} fehlt unter {d}")
    stadt, gruppen, z = bdot_verwaltung(d / BDOT_ZIP, konfig)
    teile, quelle, grund, zt = (None, None, "nicht angefordert", {})
    if dzielnice_ersatz is not None:
        teile, quelle = dzielnice_ersatz
        grund, zt = None, {"zugeordnet": len(teile)}
    elif mit_dzielnice:
        teile, quelle, grund, zt = dzielnice_aus_eingang(konfig)
    return Gliederung(stadt, gruppen, teile, quelle, grund, {**z, **{f"dzielnice_{k}": v for k, v in zt.items()}})


# Regel 4, dokumentierte Ausnahme (Entscheidung vom 13.11.2026, pruefen/D4_protokoll.md, Nachtrag): III und XV liegen zu
# 98,53 % bzw. 98,64 % in der delegatura ihrer Gruppe; der Rest ist ein Grenzsplitter zwischen den delegatury der
# BDOT10k und den dzielnice (MSIP-Gegenprobe). Die Ausnahme gilt nur für genau diesen gemessenen Anteil (auf zwei
# Stellen); ändert er sich mit neuen Grenzen, ist es wieder ein Befund. Die Schwelle 99 % bleibt.
AUSNAHMEN_REGEL4 = {"03": 98.53, "15": 98.64}


def gliederung_pruefen(gl: Gliederung, konfig: dict) -> list[tuple[str, bool, str]]:
    """Regeln 3 und 4 des Prüfprotokolls: (Regel, erfüllt, Angabe)."""
    if not gl.dzielnice:
        return []
    erg = []
    rc = _tr(4326, rechen_crs())
    stadt = transform(rc, gl.stadt.geom)
    vereinigt = unary_union([transform(rc, e.geom) for e in gl.dzielnice.values()])
    abw = (vereinigt.area - stadt.area) / stadt.area * 100
    sym = vereinigt.symmetric_difference(stadt).area / stadt.area * 100
    erg.append(("Regel 3: Fläche der Vereinigung gegen die Stadt höchstens ±1 %", abs(abw) <= 1, f"{abw:+.2f} %".replace(".", ",")))
    erg.append(("Regel 3: symmetrische Differenz höchstens 2 % der Stadtfläche", sym <= 2, f"{sym:.2f} %".replace(".", ",")))
    gruppe_von = {t["nr"]: t["gruppe"] for t in konfig["gliederung"]["teile"]}
    for nr, e in sorted(gl.dzielnice.items()):
        g = transform(rc, e.geom)
        d = transform(rc, gl.gruppen[gruppe_von[nr]].geom)
        anteil = g.intersection(d).area / g.area * 100 if g.area else 0
        angabe = f"{anteil:.2f} %"
        if anteil < 99 and g.area:
            # wohin der Rest fällt (andere delegatura, außerhalb der Stadt), damit die Ursache sichtbar ist
            rest = [(gl.gruppen[k].name, g.intersection(transform(rc, x.geom)).area / g.area * 100)
                    for k, x in sorted(gl.gruppen.items()) if k != gruppe_von[nr]]
            rest.append(("außerhalb der Stadt", g.difference(stadt).area / g.area * 100))
            angabe += "; Rest: " + ", ".join(f"{n} {a:.2f} %" for n, a in rest if a >= 0.005)
        ausnahme = anteil < 99 and AUSNAHMEN_REGEL4.get(nr) == round(anteil, 2)
        angabe = angabe.replace(".", ",")
        if ausnahme:
            angabe += ("; dokumentierte Ausnahme (Grenzsplitter zwischen delegatury der BDOT10k und dzielnice, "
                       "MSIP-Gegenprobe; Entscheidung vom 13.11.2026)")
        erg.append((f"Regel 4: {nr} {e.name} in {gl.gruppen[gruppe_von[nr]].name} zu mindestens 99 %",
                    anteil >= 99 or ausnahme, angabe))
    return erg


def msip_kandidaten() -> list[tuple[dict, object]]:
    """MSIP-Grenzen als (Tags, Geometrie in 4326), nur für interne Gegenproben (Lizenz-STOPP, nie ausliefern)."""
    pfad = daten_ordner() / MSIP_ZIP
    if not pfad.exists():
        raise EingangFehlt(f"{MSIP_ZIP} fehlt")
    with zipfile.ZipFile(pfad) as z:
        name = next(n for n in z.namelist() if n.lower().endswith((".json", ".geojson")))
        fc = json.loads(z.read(name).decode("utf-8"))
    nach_wgs = _tr(_crs_aus_geojson(fc), 4326)
    return [({"name": f["properties"].get("nazwa_peln"), "ref": f["properties"].get("nr_dzielni")},
             transform(nach_wgs, shape(f["geometry"]))) for f in fc["features"]]


def msip_gegenprobe(gl: Gliederung, konfig: dict) -> list[tuple[str, float]]:
    """Regel 5: Schnitt durch Vereinigung je dzielnica gegen die MSIP-Grenzen (nur intern, nichts wird gespeichert)."""
    if not gl.dzielnice or not (daten_ordner() / MSIP_ZIP).exists():
        return []
    msip, _z = dzielnice_zuordnen(msip_kandidaten(), konfig)
    rc = _tr(4326, rechen_crs())
    aus = []
    for nr, e in sorted(gl.dzielnice.items()):
        a, b = transform(rc, e.geom), transform(rc, msip[nr].geom)
        aus.append((f"{nr} {e.name}", a.intersection(b).area / a.union(b).area))
    return aus


def _crs_aus_geojson(fc: dict) -> CRS:
    name = (fc.get("crs") or {}).get("properties", {}).get("name")
    return CRS.from_user_input(name) if name else CRS.from_epsg(4326)


# ---- Geometrie der rejony statystyczne (Handdownload GUS)

def _gpkg_geometrie(blob: bytes):
    """GeoPackage-Binärgeometrie (Kopf GP + WKB)."""
    if blob[:2] != b"GP":
        return shapely_wkb.loads(blob)
    flags = blob[3]
    hull = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(flags >> 1) & 0x07]
    return shapely_wkb.loads(blob[8 + hull:])


def _gml_polygone(pfad: Path) -> list[tuple[dict, object, CRS]]:
    """Einfache GML-3.2-Flächen (gml:posList) mit allen einfachen Kindelementen als Attribute."""
    gml = "{http://www.opengis.net/gml/3.2}"
    baum = ET.parse(pfad)
    aus = []
    for mitglied in baum.getroot():
        for obj in mitglied:
            attr = {}
            for el in obj.iter():
                if len(el) == 0 and el.text and el.text.strip() and not el.tag.startswith(gml):
                    attr.setdefault(el.tag.split("}")[-1], el.text.strip())
            polys, srs = [], None
            for p in obj.iter(gml + "Polygon"):
                srs = srs or p.get("srsName")
                ringe = []
                for pl in p.iter(gml + "posList"):
                    z = list(map(float, pl.text.split()))
                    ringe.append(list(zip(z[0::2], z[1::2])))
                if ringe:
                    polys.append(Polygon(ringe[0], ringe[1:]))
            if polys:
                crs = CRS.from_user_input(srs) if srs else CRS.from_epsg(4326)
                g = polys[0] if len(polys) == 1 else MultiPolygon(polys)
                if crs.axis_info and crs.axis_info[0].direction in ("north", "up") and crs.is_geographic:
                    g = transform(lambda x, y: (y, x), g)     # GML: Breite vor Länge
                aus.append((attr, g, crs))
    return aus


def rejony_aus_eingang(nsp_ids: set[str]) -> tuple[dict[str, object] | None, str | None, str | None, dict]:
    """Geometrie der rejony aus eingang/rejony_statystyczne.* (zip mit SHP, .gpkg, .geojson, .gml); Kennungsfeld wird
    über die Übereinstimmung mit den 6-stelligen Kennungen der NSP-Tabelle gefunden. Rückgabe (rejon -> Geometrie
    in 4326, Quelle, Grund wenn nicht da, Zählungen)."""
    ein = eingang_ordner()
    kand = sorted(p for p in ein.glob("rejony_statystyczne*") if p.suffix.lower() in
                  (".zip", ".gpkg", ".geojson", ".json", ".gml", ".shp")) if ein.is_dir() else []
    if not kand:
        return None, None, ("Geometrie der rejony statystyczne fehlt: Handdownload GUS „Jednostki statystyczne 2021“ "
                            "(eingang/rejony_statystyczne.*) steht aus"), {}
    p = kand[0]
    saetze: list[tuple[dict, object, CRS]] = []
    suf = p.suffix.lower()
    if suf in (".zip", ".shp"):
        if suf == ".zip":
            with zipfile.ZipFile(p) as z:
                staemme = sorted({n[:-4] for n in z.namelist() if n.lower().endswith(".shp")})
        else:
            staemme = [p.stem]
        for st in staemme:
            stamm = st.split("/")[-1]
            attr, geom, crs = shp_lesen(p, stamm)
            saetze += [(a, g, crs) for a, g in zip(attr, geom) if g is not None]
    elif suf == ".gpkg":
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        for (t,) in con.execute("select table_name from gpkg_contents where data_type='features'").fetchall():
            gcol, srs = con.execute("select column_name, srs_id from gpkg_geometry_columns where table_name=?",
                                    (t,)).fetchone()
            crs = CRS.from_epsg(srs) if srs > 0 else CRS.from_epsg(4326)
            spalten = [r[1] for r in con.execute(f'pragma table_info("{t}")')]
            for zeile in con.execute(f'select * from "{t}"'):
                d = dict(zip(spalten, zeile))
                g = d.pop(gcol)
                if g:
                    saetze.append((d, _gpkg_geometrie(g), crs))
        con.close()
    elif suf in (".geojson", ".json"):
        fc = json.loads(p.read_text(encoding="utf-8"))
        crs = _crs_aus_geojson(fc)
        saetze = [(f.get("properties") or {}, shape(f["geometry"]), crs) for f in fc["features"] if f.get("geometry")]
    else:
        saetze = _gml_polygone(p)
    if not saetze:
        raise Abbruch(f"{p.name}: keine Flächen gelesen")

    def kennung(v) -> str | None:
        m = re.search(r"(\d{6})$", str(v).strip())
        return m.group(1) if m else None
    beste, treffer_max = None, 0
    for feld in saetze[0][0]:
        n = len({kennung(a.get(feld)) for a, _g, _c in saetze} & nsp_ids)
        if n > treffer_max:
            beste, treffer_max = feld, n
    if beste is None or treffer_max < 0.9 * len(nsp_ids):
        raise Abbruch(f"{p.name}: kein Feld mit den Kennungen der NSP-Tabelle (beste Übereinstimmung {treffer_max} "
                      f"von {len(nsp_ids)})")
    geo: dict[str, list] = {}
    for a, g, crs in saetze:
        k = kennung(a.get(beste))
        if k in nsp_ids:
            geo.setdefault(k, []).append(transform(_tr(crs, 4326), g))
    doppelt = sorted(k for k, v in geo.items() if len(v) > 1)
    if doppelt:
        raise Abbruch(f"{p.name}: rejony mit mehreren Geometrien: {doppelt[:10]}")
    return ({k: v[0] for k, v in geo.items()}, f"eingang/{p.name}", None,
            {"saetze": len(saetze), "kennungsfeld": beste, "treffer": len(geo)})


# ------------------------------------------------------------------------------------------- Zuordnung

def gitter_zuordnen(zellen: list[Zelle], flaechen: dict[str, object]) -> tuple[dict[str, str], dict[str, dict]]:
    """Mittelpunktregel und Flächenanteile. flaechen: Schlüssel -> Geometrie in 4326.
    Rückgabe: (gid -> Schlüssel nach Mittelpunkt, Schlüssel -> {gid: Flächenanteil})."""
    nach_3035 = _tr(4326, GITTER_SRID)
    fl = {k: transform(nach_3035, g) for k, g in flaechen.items()}
    vorb = {k: prep(g) for k, g in fl.items()}
    mitte: dict[str, str] = {}
    anteile: dict[str, dict] = {k: {} for k in fl}
    for z in zellen:
        q = z.quadrat
        for k, g in fl.items():
            if vorb[k].contains(z.mitte):
                if z.gid in mitte:
                    raise Abbruch(f"Zelle {z.gid}: Mittelpunkt in {mitte[z.gid]} und {k} (Flächen überlappen)")
                mitte[z.gid] = k
            if vorb[k].intersects(q):
                a = g.intersection(q).area / q.area
                if a > 0:
                    anteile[k][z.gid] = a
    return mitte, anteile


def summen_gitter(zellen: list[Zelle], mitte: dict[str, str], anteile: dict[str, dict]) -> dict[str, dict]:
    nach_gid = {z.gid: z for z in zellen}
    aus = {}
    for k in anteile:
        zs = [z for z in zellen if mitte.get(z.gid) == k]
        werte = {"zellen": len(zs), "einwohner": sum(z.t or 0 for z in zs),
                 "u15": sum(z.u15 or 0 for z in zs), "a15_64": sum(z.a15_64 or 0 for z in zs),
                 "a65p": sum(z.a65p or 0 for z in zs)}
        werte["einwohner_flaechenanteil"] = round(sum((nach_gid[g].t or 0) * a for g, a in anteile[k].items()))
        werte["zellen_beruehrt"] = len(anteile[k])
        aus[k] = werte
    return aus


def anteil(zaehler: int, nenner: int) -> float | None:
    """Prozent mit einer Nachkommastelle, None unter der Mindestfallzahl (Prüfprotokoll Regel 13)."""
    if not nenner or nenner < MINDESTFALLZAHL:
        return None
    return round(100 * zaehler / nenner, 1)


def rejony_zuordnen(rejony_geo: dict[str, object], dzielnice: dict[str, Einheit]) -> tuple[dict[str, str], list[str]]:
    """Regel 11: rejon -> nr über einen inneren Punkt; dazu rejony mit mehr als 5 % Fläche in einer anderen dzielnica."""
    rc = _tr(4326, rechen_crs())
    dz = {nr: transform(rc, e.geom) for nr, e in dzielnice.items()}
    vorb = {nr: prep(g) for nr, g in dz.items()}
    zu, schneider = {}, []
    for rid, g0 in sorted(rejony_geo.items()):
        g = transform(rc, g0)
        p = g.representative_point()
        treffer = [nr for nr, v in vorb.items() if v.contains(p)]
        if len(treffer) != 1:
            raise Abbruch(f"rejon {rid}: innerer Punkt in {len(treffer)} dzielnice")
        zu[rid] = treffer[0]
        fremd = sum(g.intersection(dz[nr]).area for nr in dz if nr != treffer[0] and vorb[nr].intersects(g))
        if g.area and fremd / g.area > 0.05:
            schneider.append(rid)
    return zu, schneider


# ------------------------------------------------------------------------------------------- Ausgabe

def js_datei(kopf: str, name: str, inhalt: dict) -> str:
    return kopf + f"window.{name}=" + json.dumps(inhalt, ensure_ascii=False, separators=(",", ":")) + ";\n"


def gitter_quadrat_wgs84(z: Zelle) -> dict:
    zurueck = _tr(GITTER_SRID, 4326)
    ring = [list(map(lambda v: round(v, 5), zurueck(a, b))) for a, b in
            ((z.e, z.n), (z.e + z.res, z.n), (z.e + z.res, z.n + z.res), (z.e, z.n + z.res), (z.e, z.n))]
    return {"type": "Polygon", "coordinates": [ring]}


def rahmen_3035(geom_wgs84, puffer_m: float = 1000) -> tuple[float, float, float, float]:
    w, s, o, n = transform(_tr(4326, GITTER_SRID), geom_wgs84).bounds
    return w - puffer_m, s - puffer_m, o + puffer_m, n + puffer_m


def sha256(pfad: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with pfad.open("rb") as f:
        while b := f.read(1 << 22):
            h.update(b)
    return h.hexdigest()

