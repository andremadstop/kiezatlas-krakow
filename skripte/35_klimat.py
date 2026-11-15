"""Klima: Bodenbedeckung nach BDOT10k je Stadt, Delegatur, dzielnica und 1-km-Zelle; Grün je Einwohner.

Regeln, Zuordnung der Schichten und Schwellen: pruefen/dk_protokoll.md (vor dem ersten Lauf festgelegt).

Liest (kein Netz, keine Datenbank):
  $KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip     BDOT10k Powiat 1261 (Schichten OT_PT??_A, OT_ADJA_A)
  $KIEZ_DATEN/2026-11-13/10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html   nur Gegenprobe der Fläche;
                                                      fehlt sie, entfällt nur die Gegenprobe
  daten/stadtteile_odbl.js, daten/kennzahlen_odbl.json     Grenzen und Einwohner (Paket Gliederung und Bevölkerung)
  config/krakow.yaml                                  rechen_srid, Gruppen der dzielnice
Schreibt:
  daten/klimat.js                Stadt und vier Delegaturen (window.KIEZ_KLIMAT)
  daten/klimat_zellen.js         1-km-Zellen (window.KIEZ_KLIMAT_ZELLEN)
  daten/klimat_stadtteile_odbl.js  dzielnice (window.KIEZ_KLIMAT_STADTTEILE), ODbL wegen der Grenzen
  belege/dk_klimat.md            Zählungen je Schritt, Summen, Gegenprobe

Aufruf:
  python -I skripte/35_klimat.py [--bdot ZIP] [--pruefen]
  --pruefen  nichts schreiben, alles neu rechnen und byteweise mit den vorhandenen Dateien vergleichen
Rückgabe 0 = geschrieben bzw. gleich, 1 = Abweichung (--pruefen) oder Befund nach Protokoll, 2 = Abbruch.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import platform
import re
import struct
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pyproj
import shapely
import shapely.prepared
from pyproj import CRS, Transformer
from shapely.geometry import Polygon, box, shape

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402

DATEN = WURZEL / "daten"
KIEZ_DATEN = Path(os.environ.get("KIEZ_DATEN", WURZEL.parent / "kiezatlas-daten" / "krakow"))
BDOT_STD = KIEZ_DATEN / "2026-11-13" / "03_gebaeude" / "1261_SHP.zip"
BIP = KIEZ_DATEN / "2026-11-13" / "10_statistik" / "bip_dok242410_mieszkancy_dzielnice_2025.html"

TERYT_POWIAT = "1261"
TERYT_GMINA = "1261011"
GITTER = 1000                      # Zellgröße in Metern (INSPIRE, EPSG:3035)
MIN_ZELLE_HA = 10.0                # Regel 7
MIN_EW = 1000                      # Regel 8
SCHWELLE_ABDECKUNG = 0.005         # Regel 3
SCHWELLE_DELEG = 0.001             # Regel 5
SCHWELLE_ZELLEN_FL = 0.0001        # Regel 5
SCHWELLE_ZELLEN_KL = 0.001         # Regel 5
SCHWELLE_STADTTEILE = 0.005        # Regel 5 (nur mit echten Grenzen)
SCHWELLE_BIP = 0.005               # Regel 6

KLASSEN = ["bebauung", "verkehr", "gruen", "wald", "wasser", "acker", "sonstige"]
ABGELEITET = {"bebauung_verkehr": ["bebauung", "verkehr"], "gruen_wald": ["gruen", "wald"]}
# Schicht -> Klasse; PTTR nach RODZAJ (Protokoll, Tabelle „Zuordnung Schicht → Klasse“)
SCHICHT_KLASSE = {"PTZB": "bebauung", "PTKM": "verkehr", "PTPL": "verkehr", "PTRK": "gruen", "PTUT": "gruen",
                  "PTLZ": "wald", "PTWP": "wasser", "PTGN": "sonstige", "PTSO": "sonstige", "PTWZ": "sonstige",
                  "PTNZ": "sonstige", "PTTR": None}
PTTR_RODZAJ = {"roślinność trawiasta": "gruen", "uprawa na gruntach ornych": "acker"}

QUELLE = {
    "quelle": "Baza Danych Obiektów Topograficznych (BDOT10k), Główny Urząd Geodezji i Kartografii, powiat 1261",
    "vermerk": "Źródło: GUGiK, BDOT10k (art. 40c ust. 3 ustawy Prawo geodezyjne i kartograficzne)",
    "url": "https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip",
}
KOPF_ECHT = ("/* Klima: Bodenbedeckung nach BDOT10k (GUGiK, Źródło: GUGiK, BDOT10k), erzeugt von skripte/35_klimat.py; "
             "Regeln: pruefen/dk_protokoll.md. Nicht von Hand ändern. */\n")
KOPF_ODBL = ("/* Klima je dzielnica, erzeugt von skripte/35_klimat.py. Flächen: Źródło: GUGiK, BDOT10k. Grenzen der "
             "dzielnice: © OpenStreetMap-Mitwirkende, Open Database License 1.0 "
             "(https://opendatacommons.org/licenses/odbl/1-0/); diese Datei steht daher unter der ODbL. */\n")
HINWEIS_STADTTEILE = ("Beispieldaten: Grenzen der Stadtteile und Einwohner sind unecht; die Flächenanteile darin "
                      "sagen nichts über die Stadtteile aus.")


class Abbruch(Exception):
    pass


# ---------------------------------------------------------------- Shapefile lesen (ohne Fremdpakete außer shapely)
def dbf_lesen(b: bytes) -> tuple[list[dict | None], int]:
    """Sätze einer DBF-Datei als Liste (gelöschte Sätze als None) und Zahl der gelöschten."""
    nrec, hlen, rlen = struct.unpack("<IHH", b[4:12])
    felder, o = [], 32
    while b[o] != 0x0D:
        name = b[o:o + 11].split(b"\0")[0].decode("ascii")
        felder.append((name, b[o + 16]))
        o += 32
    saetze, geloescht = [], 0
    for i in range(nrec):
        r = b[hlen + i * rlen: hlen + (i + 1) * rlen]
        if r[:1] == b"*":
            saetze.append(None)
            geloescht += 1
            continue
        p, d = 1, {}
        for name, ln in felder:
            d[name] = r[p:p + ln].decode("utf-8").strip()
            p += ln
        saetze.append(d)
    return saetze, geloescht


def ringflaeche(xy: np.ndarray) -> float:
    x, y = xy[:, 0], xy[:, 1]
    return 0.5 * float(np.dot(x[:-1], y[1:]) - np.dot(x[1:], y[:-1]))


def shp_lesen(b: bytes) -> tuple[list, Counter]:
    """Polygone einer SHP-Datei (Formtyp 5). Außenringe im Uhrzeigersinn, Löcher dagegen (Shapefile-Norm)."""
    z = Counter()
    if struct.unpack("<i", b[32:36])[0] != 5:
        raise Abbruch(f"Formtyp {struct.unpack('<i', b[32:36])[0]}, erwartet 5 (Polygon)")
    geoms, o = [], 100
    while o < len(b):
        _, laenge = struct.unpack(">ii", b[o:o + 8])
        inhalt = b[o + 8: o + 8 + 2 * laenge]
        o += 8 + 2 * laenge
        typ = struct.unpack("<i", inhalt[:4])[0]
        if typ == 0:
            geoms.append(None)
            z["leer"] += 1
            continue
        if typ != 5:
            raise Abbruch(f"Satz mit Formtyp {typ}")
        nparts, npts = struct.unpack("<ii", inhalt[36:44])
        teile = list(struct.unpack(f"<{nparts}i", inhalt[44:44 + 4 * nparts])) + [npts]
        pkt = np.frombuffer(inhalt[44 + 4 * nparts: 44 + 4 * nparts + 16 * npts], dtype="<f8").reshape(-1, 2)
        aussen, loecher = [], []
        for a, e in zip(teile, teile[1:]):
            ring = pkt[a:e]
            if len(ring) < 4:
                z["ring_zu_kurz"] += 1
                continue
            (aussen if ringflaeche(ring) < 0 else loecher).append(ring)
        z["loecher"] += len(loecher)
        polys = [[r, []] for r in aussen]
        huellen = [Polygon(r) for r in aussen]
        for loch in loecher:
            punkt = shapely.Point(loch[0])
            ziel = next((i for i, h in enumerate(huellen) if h.covers(punkt)), None)
            if ziel is None:
                z["loch_ohne_aussenring"] += 1
                polys.append([loch[::-1], []])
            else:
                polys[ziel][1].append(loch)
        if not polys:
            geoms.append(None)
            z["ohne_ring"] += 1
            continue
        g = shapely.MultiPolygon([Polygon(a, l) for a, l in polys]) if len(polys) > 1 else Polygon(*polys[0])
        if len(polys) > 1:
            z["mehrteilig"] += 1
        geoms.append(g)
    return geoms, z


def schicht_lesen(zf: zipfile.ZipFile, kuerzel: str) -> tuple[list[tuple], dict, str]:
    namen = {n.rsplit("__OT_", 1)[1]: n for n in zf.namelist() if "__OT_" in n}
    basis = namen[f"{kuerzel}.shp"][:-4]
    geoms, z = shp_lesen(zf.read(basis + ".shp"))
    saetze, geloescht = dbf_lesen(zf.read(basis + ".dbf"))
    if len(geoms) != len(saetze):
        raise Abbruch(f"{kuerzel}: {len(geoms)} Formen in .shp, {len(saetze)} Sätze in .dbf")
    zaehl = {"saetze": len(saetze), "geloescht": geloescht, "fremd_teryt": 0, "ohne_geometrie": 0,
             "ungueltig": 0, "reparatur_m2": 0.0, **{k: v for k, v in z.items()}}
    aus = []
    for g, d in zip(geoms, saetze):
        if d is None:
            continue
        if d.get("TERYT") != TERYT_POWIAT:
            zaehl["fremd_teryt"] += 1
            continue
        if g is None:
            zaehl["ohne_geometrie"] += 1
            continue
        if not g.is_valid:
            zaehl["ungueltig"] += 1
            vorher = g.area
            g = shapely.make_valid(g)
            g = shapely.union_all([p for p in shapely.get_parts(g) if p.geom_type in ("Polygon", "MultiPolygon")])
            zaehl["reparatur_m2"] += g.area - vorher
        aus.append((g, d))
    return aus, zaehl, zf.read(basis + ".prj").decode("ascii")


# ---------------------------------------------------------------- Hilfen
def r1(x: float) -> float:
    return round(x + 0.0, 1)


def transformer(von: CRS, nach: CRS):
    tr = Transformer.from_crs(von, nach, always_xy=True)

    def f(g):
        return shapely.transform(g, lambda c: np.column_stack(tr.transform(c[:, 0], c[:, 1])))
    return f


def js_lesen(pfad: Path) -> tuple[str, object]:
    text = pfad.read_text(encoding="utf-8")
    m = re.search(r"window\.([A-Za-z0-9_]+)\s*=\s*", text)
    return m.group(1), json.loads(text[m.end():].rstrip().rstrip(";"))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for teil in iter(lambda: f.read(1 << 20), b""):
            h.update(teil)
    return h.hexdigest()


def flaechen(teile_geom, features, baum) -> dict[str, float]:
    """Klassenflächen (m²) innerhalb einer Geometrie."""
    ha = dict.fromkeys(KLASSEN, 0.0)
    if teile_geom.is_empty:
        return ha
    prep = shapely.prepared.prep(teile_geom)
    for i in baum.query(teile_geom):
        g, klasse = features[i]
        if prep.contains(g):
            ha[klasse] += g.area
        elif prep.intersects(g):
            ha[klasse] += shapely.intersection(g, teile_geom).area
    return ha


def einheit(fl_m2: float, kl_m2: dict[str, float], mit_anteil: bool = True) -> dict:
    s = sum(kl_m2.values())
    e = {"flaeche_ha": r1(fl_m2 / 1e4), "abdeckung": r1(100 * s / fl_m2) if fl_m2 else None,
         "ha": {k: r1(v / 1e4) for k, v in kl_m2.items()}}
    if mit_anteil and s > 0:
        a = {k: 100 * v / s for k, v in kl_m2.items()}
        for k, teile in ABGELEITET.items():
            a[k] = sum(a[t] for t in teile)
        e["anteil"] = {k: r1(v) for k, v in a.items()}
    else:
        e["anteil"] = None
    return e


def gruen_je_ew(kl_m2: dict[str, float], ew, ew_fixture: bool) -> tuple:
    if ew_fixture:
        return None, "einwohner_beispieldaten"
    if ew is None or ew < MIN_EW:
        return None, "unter_mindestzahl"
    return round(sum(kl_m2[k] for k in ABGELEITET["gruen_wald"]) / ew), None


def js_text(kopf: str, name: str, obj) -> str:
    return kopf + f"window.{name}=" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n"


def proz(x: float) -> str:
    return f"{100 * x:.3f} %".replace(".", ",")


def zahl(x: float, st: int = 1) -> str:
    return f"{x:,.{st}f}".replace(",", " ").replace(".", ",")


# ---------------------------------------------------------------- Lauf
def rechnen(bdot: Path) -> tuple[dict[str, str], list[str]]:
    k = ort_konfig.lade()
    befunde: list[str] = []
    rechen = CRS.from_epsg(ort_konfig.RECHEN_SRID)
    gitter_crs = CRS.from_epsg(3035)
    wgs = CRS.from_epsg(4326)
    zf = zipfile.ZipFile(bdot)
    stand_daten = max(i.date_time for i in zf.infolist() if "__OT_PT" in i.filename)
    stand_daten = f"{stand_daten[0]:04d}-{stand_daten[1]:02d}-{stand_daten[2]:02d}"
    pt_schichten = sorted(n.rsplit("__OT_", 1)[1][:-4] for n in zf.namelist()
                          if re.search(r"__OT_PT.._A\.shp$", n))
    unbekannt = [s for s in pt_schichten if s[:4] not in SCHICHT_KLASSE]
    if unbekannt:
        raise Abbruch(f"Schichten ohne Zuordnung im Protokoll: {unbekannt}")
    fehlend = [s for s in SCHICHT_KLASSE if f"{s}_A" not in pt_schichten]
    if fehlend:
        raise Abbruch(f"Schichten aus dem Protokoll fehlen im Paket: {fehlend}")

    # Verwaltungseinheiten
    adja, z_adja, prj = schicht_lesen(zf, "ADJA_A")
    quell_crs = CRS.from_wkt(prj)
    nach_rechen = transformer(quell_crs, rechen)
    gmina = [g for g, d in adja if d["RODZAJ"] == "gmina" and d["IDTERYTJED"] == TERYT_GMINA]
    if len(gmina) != 1:
        raise Abbruch(f"{len(gmina)} Gemeindeflächen mit IDTERYTJED {TERYT_GMINA}")
    stadt = nach_rechen(gmina[0])
    deleg = sorted(((d["IDTERYTJED"], d["NAZWA"], nach_rechen(g)) for g, d in adja
                    if d["RODZAJ"] == "dzielnica lub delegatura"), key=lambda x: x[0])
    stadt_prep = shapely.prepared.prep(stadt)

    # Bodenbedeckung, auf die Stadt zugeschnitten
    features: list[tuple] = []
    je_schicht: dict[str, dict] = {}
    je_rodzaj: dict[tuple, float] = defaultdict(float)
    zb_roslinnosc: dict[str, float] = defaultdict(float)
    ausserhalb = 0
    for s in pt_schichten:
        teile, z, prj_s = schicht_lesen(zf, s)
        if CRS.from_wkt(prj_s) != quell_crs:
            raise Abbruch(f"{s}: anderes Koordinatensystem als OT_ADJA_A")
        z["in_stadt"] = 0
        z["flaeche_m2"] = 0.0
        kurz = s[:4]
        for g, d in teile:
            if kurz == "PTTR":
                if d.get("RODZAJ") not in PTTR_RODZAJ:
                    raise Abbruch(f"PTTR mit unbekanntem RODZAJ {d.get('RODZAJ')!r}")
                klasse = PTTR_RODZAJ[d["RODZAJ"]]
            else:
                klasse = SCHICHT_KLASSE[kurz]
            g = nach_rechen(g)
            if not stadt_prep.contains(g):
                if not stadt_prep.intersects(g):
                    ausserhalb += 1
                    continue
                g = shapely.intersection(g, stadt)
                if g.is_empty or g.area == 0:
                    ausserhalb += 1
                    continue
            z["in_stadt"] += 1
            z["flaeche_m2"] += g.area
            je_rodzaj[(kurz, d.get("RODZAJ", ""), klasse)] += g.area
            if kurz == "PTZB":
                zb_roslinnosc[d.get("ROSLINNOSC", "")] += g.area
            features.append((g, klasse))
        je_schicht[s] = z
    geoms = [g for g, _ in features]
    baum = shapely.STRtree(geoms)

    # Abdeckung (Regel 3)
    A = stadt.area
    S = sum(g.area for g in geoms)
    U = shapely.union_all(geoms, grid_size=0.01).intersection(stadt).area
    ueberlappung, luecke = (S - U) / A, (A - U) / A
    if ueberlappung > SCHWELLE_ABDECKUNG:
        befunde.append(f"Überlappung {proz(ueberlappung)} > {proz(SCHWELLE_ABDECKUNG)}")
    if luecke > SCHWELLE_ABDECKUNG:
        befunde.append(f"Lücke {proz(luecke)} > {proz(SCHWELLE_ABDECKUNG)}")

    stadt_kl = flaechen(stadt, features, baum)

    # Delegaturen (Regel 5)
    gruppen = {g["name"]: g["id"] for g in k["gliederung"]["gruppen"]}
    deleg_aus, deleg_kl, deleg_fl = {}, dict.fromkeys(KLASSEN, 0.0), 0.0
    for teryt, name, g in deleg:
        kl = flaechen(g, features, baum)
        e = einheit(g.area, kl)
        e = {"name": name, "gruppe_nach_name": gruppen.get(name.removeprefix("Kraków-")), **e}
        deleg_aus[teryt] = e
        deleg_fl += g.area
        for kk in KLASSEN:
            deleg_kl[kk] += kl[kk]
    abw_deleg_fl = abs(deleg_fl - A) / A
    abw_deleg_kl = {kk: abs(deleg_kl[kk] - stadt_kl[kk]) / max(stadt_kl[kk], 1) for kk in KLASSEN}
    if len(deleg) != 4:
        befunde.append(f"{len(deleg)} Delegaturen statt 4")
    if abw_deleg_fl > SCHWELLE_DELEG or max(abw_deleg_kl.values()) > SCHWELLE_DELEG:
        befunde.append("Σ Delegaturen weicht von der Stadt ab")

    # Einwohner (Gliederung und Bevölkerung)
    K = json.loads((DATEN / "kennzahlen_odbl.json").read_text(encoding="utf-8"))
    ew_fixture = K.get("fixture") is True

    def ew_aus(G):
        return next((x["wert"] for x in G["kacheln"] if x["id"] == "einwohner"), None)
    g_ew, g_grund = gruen_je_ew(stadt_kl, ew_aus(K["stadt"]), ew_fixture)
    stadt_e = {"teryt": TERYT_GMINA, **einheit(A, stadt_kl), "gruen_je_ew": g_ew}
    if g_grund:
        stadt_e["gruen_je_ew_grund"] = g_grund

    # Zellen (Regel 7)
    nach_gitter = transformer(rechen, gitter_crs)
    gitter_nach_rechen = transformer(gitter_crs, rechen)
    gitter_nach_wgs = transformer(gitter_crs, wgs)
    x0, y0, x1, y1 = nach_gitter(stadt).bounds
    zellen, zell_fl, zell_kl = [], 0.0, dict.fromkeys(KLASSEN, 0.0)
    n_klein = 0
    for n in range(int(y0 // GITTER) * GITTER, int(y1 // GITTER + 1) * GITTER, GITTER):
        for e in range(int(x0 // GITTER) * GITTER, int(x1 // GITTER + 1) * GITTER, GITTER):
            q = box(e, n, e + GITTER, n + GITTER)
            zr = gitter_nach_rechen(q)
            if not stadt_prep.intersects(zr):
                continue
            teil = zr if stadt_prep.contains(zr) else shapely.intersection(zr, stadt)
            if teil.is_empty or teil.area == 0:
                continue
            kl = flaechen(teil, features, baum)
            zell_fl += teil.area
            for kk in KLASSEN:
                zell_kl[kk] += kl[kk]
            klein = teil.area / 1e4 < MIN_ZELLE_HA
            n_klein += klein
            ein = einheit(teil.area, kl, mit_anteil=not klein)
            ring = [[round(x, 5), round(y, 5)] for x, y in gitter_nach_wgs(q).exterior.coords]
            p = {"id": f"CRS3035RES1000mN{n}E{e}", "flaeche_stadt_ha": ein["flaeche_ha"],
                 "anteil_stadt": r1(100 * teil.area / zr.area), "abdeckung": ein["abdeckung"], "ha": ein["ha"],
                 "anteil": ein["anteil"]}
            if klein:
                p["anteil_grund"] = "bezugsflaeche_zu_klein"
            zellen.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                           "properties": p})
    zellen.sort(key=lambda f: f["properties"]["id"])
    abw_zell_fl = abs(zell_fl - A) / A
    abw_zell_kl = {kk: abs(zell_kl[kk] - stadt_kl[kk]) / max(stadt_kl[kk], 1) for kk in KLASSEN}
    if abw_zell_fl > SCHWELLE_ZELLEN_FL or max(abw_zell_kl.values()) > SCHWELLE_ZELLEN_KL:
        befunde.append("Σ Zellen weicht von der Stadt ab")

    # dzielnice (Regel 5, 8, 9, 10)
    _, ST = js_lesen(DATEN / "stadtteile_odbl.js")
    st_fixture = ST.get("fixture") is True
    von_wgs = transformer(wgs, rechen)
    st_aus, st_fl, st_kl_summe = {}, 0.0, dict.fromkeys(KLASSEN, 0.0)
    st_bericht = []
    for f in sorted(ST["features"], key=lambda f: f["properties"]["nr"]):
        nr = f["properties"]["nr"]
        g = von_wgs(shape(f["geometry"]))
        if not g.is_valid:
            g = shapely.make_valid(g)
        teil = shapely.intersection(g, stadt)
        kl = flaechen(teil, features, baum)
        G = K["stadtteile"].get(nr)
        ew = ew_aus(G) if G else None
        # Regel 8, Ergänzung: diese Datei ist mit Beispieleinwohnern selbst Beispieldaten, also hier mit ihnen rechnen
        gw, grund = gruen_je_ew(kl, ew, False)
        klein = teil.area / 1e4 < MIN_ZELLE_HA
        if klein and not st_fixture:   # Regel 7, Ergänzung: echte Grenzen unter der Mindestfläche sind ein Befund
            befunde.append(f"dzielnica {nr}: nur {r1(teil.area / 1e4)} ha in der Stadt (unter {MIN_ZELLE_HA} ha)")
        if klein:
            gw, grund = None, "bezugsflaeche_zu_klein"
        e = {"name": f["properties"].get("name"), **einheit(teil.area, kl, mit_anteil=not klein),
             "einwohner": ew, "gruen_je_ew": gw}
        if klein:
            e["anteil_grund"] = "bezugsflaeche_zu_klein"
        if grund:
            e["gruen_je_ew_grund"] = grund
        st_aus[nr] = e
        st_fl += teil.area
        for kk in KLASSEN:
            st_kl_summe[kk] += kl[kk]
        st_bericht.append((nr, f["properties"].get("name"), g.area, teil.area))
    abw_st_fl = abs(st_fl - A) / A
    if not st_fixture and abw_st_fl > SCHWELLE_STADTTEILE:
        befunde.append(f"Σ dzielnice weicht um {proz(abw_st_fl)} von der Stadt ab")

    # Gegenprobe BIP (Regel 6); die Seite hat keine Lizenzangabe und fehlt im Rohdaten-Schnappschuss. Fehlt sie,
    # entfällt nur diese Gegenprobe (Vermerk im Beleg), die Datendateien hängen nicht von ihr ab.
    bip_ha = abw_bip = None
    bip_teile = {}
    if BIP.exists():
        bip_text = html.unescape(re.sub(r"<[^>]+>", " ", BIP.read_text(encoding="utf-8")))
        bip_text = re.sub(r"\s+", " ", bip_text)
        m = re.search(r"RAZEM ([\d ]+,\d+)", bip_text)
        if not m:
            raise Abbruch("Gegenprobe: Zeile RAZEM im BIP-Abzug nicht gefunden")
        bip_ha = float(m.group(1).replace(" ", "").replace(",", "."))
        abw_bip = (A / 1e4 - bip_ha) / bip_ha
        if abs(abw_bip) > SCHWELLE_BIP:
            befunde.append(f"Stadtfläche weicht um {proz(abw_bip)} von der BIP-Fläche ab")
        for rz, fl in re.findall(r"\b([IVX]{1,5}) (\d+,\d+) \d+\b", bip_text):
            bip_teile[rz] = float(fl.replace(",", "."))

    # Ausgaben
    meta = {"stand_daten": stand_daten, "quelle": QUELLE, "abzeichen": "orientierung", "klassen": KLASSEN,
            "abgeleitet": ABGELEITET, "rechen_srid": ort_konfig.RECHEN_SRID}
    if befunde:
        meta["befund"] = befunde
    klimat = {**meta, "mindest_einwohner": MIN_EW, "stadt": stadt_e, "delegaturen": deleg_aus}
    klimat_zellen = {"type": "FeatureCollection", **meta, "mindestflaeche_ha": MIN_ZELLE_HA, "features": zellen}
    klimat_st = {**({"fixture": True, "hinweis": HINWEIS_STADTTEILE} if (st_fixture or ew_fixture) else {}),
                 **meta, "mindest_einwohner": MIN_EW, "mindestflaeche_ha": MIN_ZELLE_HA,
                 "quelle_grenzen": {"quelle": "OpenStreetMap", "vermerk": k["karte"]["teile_bildzeile"]["pl"],
                                    "fixture": st_fixture},
                 "stadtteile": st_aus}
    if not (st_fixture or ew_fixture):
        klimat_st.pop("fixture", None)

    aus = {
        "daten/klimat.js": js_text(KOPF_ECHT, "KIEZ_KLIMAT", klimat),
        "daten/klimat_zellen.js": js_text(KOPF_ECHT, "KIEZ_KLIMAT_ZELLEN", klimat_zellen),
        "daten/klimat_stadtteile_odbl.js": js_text(KOPF_ODBL, "KIEZ_KLIMAT_STADTTEILE", klimat_st),
    }

    # Beleg
    rz = {t["nr"]: t["roemisch"] for t in k["gliederung"]["teile"]}
    L = []
    w = L.append
    w("# Beleg Klima: Versiegelung und Grün (Bodenbedeckung BDOT10k)")
    w("")
    w("Erzeugt von `skripte/35_klimat.py` (nicht von Hand ändern; `--pruefen` vergleicht byteweise). Regeln und "
      "Schwellen: `pruefen/dk_protokoll.md`, vor dem ersten Lauf festgelegt. Quellen und Lizenz: `quellen-dk.md`.")
    w("")
    w("## Eingaben")
    w("")
    w("| Datei | SHA256 |")
    w("|---|---|")
    w(f"| `$KIEZ_DATEN/{bdot.relative_to(KIEZ_DATEN) if bdot.is_relative_to(KIEZ_DATEN) else bdot.name}` | `{sha256(bdot)}` |")
    w(f"| `$KIEZ_DATEN/{BIP.relative_to(KIEZ_DATEN)}` (nur Gegenprobe) | "
      + (f"`{sha256(BIP)}` |" if BIP.exists() else "fehlt, Gegenprobe übersprungen |"))
    for rel in ("daten/stadtteile_odbl.js", "daten/kennzahlen_odbl.json"):
        w(f"| `{rel}` | `{sha256(WURZEL / rel)}` |")
    w("")
    w(f"Stand der BDOT10k-Dateien laut Zip-Verzeichnis: {stand_daten}. Koordinatensystem der Dateien: "
      f"{quell_crs.name}; gerechnet in {ort_konfig.srs_name()}. Werkzeuge: Python {platform.python_version()}, "
      f"shapely {shapely.__version__} (GEOS {shapely.geos_version_string}), pyproj {pyproj.__version__} "
      f"(PROJ {pyproj.proj_version_str}), numpy {np.__version__}.")
    w("")
    w("## Schritt 1: Lesen je Schicht")
    w("")
    w("| Schicht | Sätze | gelöscht | anderer TERYT | ohne Geometrie | ungültig, repariert | Flächenänderung durch Reparatur (m²) | in der Stadt | Fläche in der Stadt (ha) |")
    w("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for s, z in je_schicht.items():
        w(f"| `{s}` | {z['saetze']} | {z['geloescht']} | {z['fremd_teryt']} | {z['ohne_geometrie']} | {z['ungueltig']} "
          f"| {zahl(z['reparatur_m2'])} | {z['in_stadt']} | {zahl(z['flaeche_m2'] / 1e4)} |")
    w(f"| `ADJA_A` | {z_adja['saetze']} | {z_adja['geloescht']} | {z_adja['fremd_teryt']} | {z_adja['ohne_geometrie']} "
      f"| {z_adja['ungueltig']} | {zahl(z_adja['reparatur_m2'])} | – | – |")
    w("")
    sonder = {s: {kk: v for kk, v in z.items() if kk in ("leer", "ring_zu_kurz", "loch_ohne_aussenring", "ohne_ring",
                                                         "mehrteilig", "loecher")} for s, z in je_schicht.items()}
    w("Ringe (Löcher, mehrteilige Polygone, Löcher ohne Außenring, zu kurze Ringe, leere Formen): "
      + ("; ".join(f"`{s}` {', '.join(f'{kk} {v}' for kk, v in sorted(d.items()))}" for s, d in sonder.items() if d)
         or "keine") + ".")
    w(f"Flächen der Bodenbedeckung ganz außerhalb der Stadtgrenze (verworfen): {ausserhalb}.")
    w("")
    w("## Schritt 2: Fläche je Schicht und RODZAJ in der Stadt")
    w("")
    w("| Schicht | RODZAJ | Klasse | Fläche (ha) |")
    w("|---|---|---|---:|")
    for (s, rodzaj, klasse), fl in sorted(je_rodzaj.items()):
        w(f"| `{s}` | {rodzaj or '(ohne)'} | `{klasse}` | {zahl(fl / 1e4)} |")
    w("")
    w("Bebauung (`PTZB`) nach dem Merkmal `ROSLINNOSC` (Bewuchs innerhalb der bebauten Fläche), zur Einordnung der "
      "Näherung für Versiegelung:")
    w("")
    w("| ROSLINNOSC | Fläche (ha) |")
    w("|---|---:|")
    for r, fl in sorted(zb_roslinnosc.items()):
        w(f"| {r or '(ohne)'} | {zahl(fl / 1e4)} |")
    w("")
    w("## Schritt 3: Abdeckung der Stadtfläche (Regel 3)")
    w("")
    w(f"- Stadtfläche A (`OT_ADJA_A`, gmina {TERYT_GMINA}): {zahl(A / 1e4)} ha")
    w(f"- Summe der Klassenflächen S: {zahl(S / 1e4)} ha")
    w(f"- Vereinigung U (Raster 1 cm): {zahl(U / 1e4)} ha")
    w(f"- Überlappung S − U: {zahl((S - U) / 1e4, 2)} ha = {proz(ueberlappung)} von A (Schwelle {proz(SCHWELLE_ABDECKUNG)})")
    w(f"- Lücke A − U: {zahl((A - U) / 1e4, 2)} ha = {proz(luecke)} von A (Schwelle {proz(SCHWELLE_ABDECKUNG)})")
    w("")
    w("## Schritt 4: Stadt")
    w("")
    w("| Klasse | Fläche (ha) | Anteil (%) |")
    w("|---|---:|---:|")
    for kk in KLASSEN:
        w(f"| `{kk}` | {zahl(stadt_kl[kk] / 1e4)} | {zahl(stadt_e['anteil'][kk])} |")
    for kk in ABGELEITET:
        w(f"| `{kk}` (abgeleitet) | – | {zahl(stadt_e['anteil'][kk])} |")
    w("")
    w(f"Grün je Einwohner der Stadt: {stadt_e['gruen_je_ew'] if stadt_e['gruen_je_ew'] is not None else 'null'}"
      + (f" (Grund `{g_grund}`; `daten/kennzahlen_odbl.json` trägt fixture: true)" if g_grund else " m²") + ".")
    w("")
    w("## Schritt 5: Delegaturen (Regel 5)")
    w("")
    w("| IDTERYTJED | Name | Gruppe nach Namen | Fläche (ha) | " + " | ".join(f"`{kk}` (%)" for kk in KLASSEN) + " |")
    w("|---|---|---|---:|" + "---:|" * len(KLASSEN))
    for teryt, e in deleg_aus.items():
        w(f"| {teryt} | {e['name']} | {e['gruppe_nach_name']} | {zahl(e['flaeche_ha'])} | "
          + " | ".join(zahl(e['anteil'][kk]) for kk in KLASSEN) + " |")
    w("")
    w(f"- Σ Fläche der Delegaturen: {zahl(deleg_fl / 1e4)} ha, Abweichung von A {proz(abw_deleg_fl)} "
      f"(Schwelle {proz(SCHWELLE_DELEG)})")
    w(f"- größte Abweichung einer Klassensumme: {proz(max(abw_deleg_kl.values()))}")
    w("- Die Gruppe ist nur über den Namen zugeordnet (`Kraków-<Name>` = Name der Gruppe in `config/krakow.yaml`); "
      "welche dzielnice zu welcher Delegatur gehören, ist hier nicht geprüft.")
    w("")
    w("## Schritt 6: 1-km-Zellen (Regel 7)")
    w("")
    w(f"- Zellen, die die Stadt schneiden: {len(zellen)}")
    w(f"- davon mit weniger als {zahl(MIN_ZELLE_HA, 0)} ha in der Stadt (Anteile null): {n_klein}")
    w(f"- davon ganz in der Stadt: {sum(1 for f in zellen if f['properties']['anteil_stadt'] == 100.0)}")
    w(f"- Σ Zellteile in der Stadt: {zahl(zell_fl / 1e4)} ha, Abweichung von A {proz(abw_zell_fl)} "
      f"(Schwelle {proz(SCHWELLE_ZELLEN_FL)})")
    w(f"- größte Abweichung einer Klassensumme über die Zellen: {proz(max(abw_zell_kl.values()))} "
      f"(Schwelle {proz(SCHWELLE_ZELLEN_KL)})")
    w("")
    w("## Schritt 7: dzielnice (Regel 5, 9, 10)")
    w("")
    w(f"- Grenzen aus `daten/stadtteile_odbl.js`: {'**Beispieldaten** (fixture: true)' if st_fixture else 'echt'}; "
      f"Einwohner aus `daten/kennzahlen_odbl.json`: {'**Beispieldaten** (fixture: true)' if ew_fixture else 'echt'}.")
    w(f"- Ausgabe `daten/klimat_stadtteile_odbl.js`: {'fixture: true' if (st_fixture or ew_fixture) else 'echt'}.")
    n_st_klein = [nr for nr, e in st_aus.items() if e["anteil"] is None]
    w(f"- dzielnice mit weniger als {zahl(MIN_ZELLE_HA, 0)} ha in der Stadt: {len(n_st_klein)}"
      + (f" ({', '.join(n_st_klein)}; " + ("Anteile null mit Grund `bezugsflaeche_zu_klein`)" if st_fixture
                                          else "Befund nach Regel 7)") if n_st_klein else ""))
    gruende = {}
    for e in st_aus.values():
        gruende[e.get("gruen_je_ew_grund", "Wert")] = gruende.get(e.get("gruen_je_ew_grund", "Wert"), 0) + 1
    w(f"- Grün je Einwohner je dzielnica (Regel 8, Ergänzung; Einwohner "
      f"{'Beispieldaten' if ew_fixture else 'echt'}): mit Wert {gruende.pop('Wert', 0)}"
      + "".join(f", null mit Grund `{g}` {n}" for g, n in sorted(gruende.items())))
    w(f"- Σ Fläche der dzielnice innerhalb der Stadt: {zahl(st_fl / 1e4)} ha, Abweichung von A {proz(abw_st_fl)}"
      + (" (mit Beispieldaten nur berichtet)" if st_fixture else f" (Schwelle {proz(SCHWELLE_STADTTEILE)})"))
    if not st_fixture:
        w("")
        w("| nr | Name | Fläche Grenze (ha) | davon in der Stadt (ha) | BIP-Fläche (ha) | Abweichung |")
        w("|---|---|---:|---:|---:|---:|")
        for nr, name, fg, ft in st_bericht:
            b = bip_teile.get(rz.get(nr))
            w(f"| {nr} | {name} | {zahl(fg / 1e4)} | {zahl(ft / 1e4)} | {zahl(b) if b else '–'} | "
              f"{proz((ft / 1e4 - b) / b) if b else '–'} |")
    w("")
    w("## Schritt 8: Gegenprobe Stadtfläche (Regel 6)")
    w("")
    if bip_ha is None:
        w("- BIP-Abzug fehlt (Seite ohne Lizenzangabe, nicht im Rohdaten-Schnappschuss): Gegenprobe übersprungen")
        w(f"- BDOT10k `OT_ADJA_A`: {zahl(A / 1e4, 2)} ha")
    else:
        w(f"- BIP der Stadt, Zeile „RAZEM“: {zahl(bip_ha, 2)} ha (Wydział Geodezji Urzędu Miasta Krakowa)")
        w(f"- BDOT10k `OT_ADJA_A`: {zahl(A / 1e4, 2)} ha")
        w(f"- Abweichung: {proz(abw_bip)} (Schwelle {proz(SCHWELLE_BIP)})")
        w(f"- Zeilen je dzielnica im BIP-Abzug gefunden: {len(bip_teile)} (nur mit echten Grenzen verglichen)")
    w("")
    w("## Ergebnis")
    w("")
    if befunde:
        w("**Befund nach Protokoll, nicht veröffentlichen:**")
        for b in befunde:
            w(f"- {b}")
    else:
        w("Alle Regeln des Protokolls eingehalten (0 Befunde).")
    w("")
    w("## Grenzen")
    w("")
    w("- Bebauung + Verkehr ist eine Näherung für Versiegelung, keine Messung: `PTZB` enthält Höfe und Gärten "
      "innerhalb bebauter Flächen, `PTPL` auch unbefestigte Plätze. Abzeichen „orientacyjnie“.")
    w("- Bodenbedeckung nach Stand der BDOT10k-Dateien (siehe oben), Einwohner nach dem Stand der Einwohnerdatei; "
      "die Zeitpunkte fallen auseinander.")
    w("- Hitze (Oberflächentemperatur), gemessene Versiegelung, Baumkronen: nicht berechnet, siehe `quellen-dk.md`.")
    w("- Nicht geprüft: die Genauigkeit der BDOT10k-Bodenbedeckung gegen Luftbild oder Begehung.")
    aus["belege/dk_klimat.md"] = "\n".join(L) + "\n"
    return aus, befunde


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bdot", type=Path, default=BDOT_STD)
    ap.add_argument("--pruefen", action="store_true")
    a = ap.parse_args()
    try:
        aus, befunde = rechnen(a.bdot)
    except Abbruch as e:
        print(f"Abbruch: {e}")
        return 2
    if a.pruefen:
        abw = [p for p, t in aus.items() if not (WURZEL / p).exists() or (WURZEL / p).read_text(encoding="utf-8") != t]
        for p in aus:
            print(("  ok    " if p not in abw else "  FEHLT ") + f"{p} gleich der Neuberechnung")
        print(f"\n{len(abw)} Abweichung(en)" if abw else "\n0 Abweichungen")
        return 1 if abw or befunde else 0
    for p, t in aus.items():
        (WURZEL / p).write_text(t, encoding="utf-8")
        print(f"geschrieben: {p} ({len(t.encode('utf-8'))} B)")
    if befunde:
        print("Befund nach Protokoll:", *befunde, sep="\n  ")
        return 1
    print("0 Befunde")
    return 0


if __name__ == "__main__":
    sys.exit(main())
