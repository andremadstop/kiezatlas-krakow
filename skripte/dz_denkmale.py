"""Denkmale und Kamienice: Denkmal-Teilmenge und Mehrfamilienhäuser mit Denkmalbezug für Kraków.

Liest nur Dateien (kein Netz, keine Datenbank):
  BDOT10k Paket 1261   $KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip (Gebäude OT_BUBD_A, Komplexe OT_KUZA_A,
                       Stadt und Delegaturen OT_ADJA_A), Koordinatensystem aus der .prj der Lieferung
  Handdownloads        $KIEZ_DATEN/eingang/ (Dateinamen und Format: quellen-DZ.md)
                         wikidata_zabytki_krakow.json   Ergebnis der WDQS-Abfrage als SPARQL-JSON
                         nid_rejestr_zabytkow.csv       Rejestr zabytków (NID), Format nicht geprüft
                         gez_krakow.csv                 Gminna ewidencja zabytków, Format nicht geprüft
                         *.osm.pbf                      OSM-Auszug Małopolska (Geofabrik oder BBBike)
Schreibt:
  daten/denkmale_bdot.js   window.KIEZ_DENKMALE_BDOT   echte Daten aus BDOT10k (Zählungen, Komplexe, Namensbezug)
  daten/denkmale.js        window.KIEZ_DENKMALE        Registerpunkte (Wikidata, NID, GEZ); ohne Eingang Beispieldaten
  daten/denkmale_odbl.js   window.KIEZ_DENKMALE_ODBL   OSM heritage/start_date; ohne Eingang Beispieldaten
  belege/DZ_denkmale_lauf.md   Zählungen je Schritt, Prüfsummen der Eingänge, Stichproben
  belege/DZ_sichtpruefung_stichprobe.json   zweite Stichprobe (Protokoll, Nachtrag 3): je Punkt lon, lat, quelle, id
Liest außerdem, wenn vorhanden:
  belege/DZ_sichtpruefung.json   Ergebnis der zweiten Sichtprüfung (Eingabe von Hand, Protokoll Nachtrag 4): je Punkt
                                 der Stichprobe lage ja/daneben/nein, ansicht ja/nein/unklar. Dann trägt sichtpruefung
                                 in denkmale.js und denkmale_odbl.js geprueft true mit Quoten und Wilson-Intervall;
                                 ohne die Datei bleibt geprueft false.

Regeln: pruefen/DZ_protokoll.md (vor dem ersten Lauf festgelegt). Kein Einzeljahr, nur Bauzeitklassen; keine
Gebäudekennung, keine Adresse, kein Name an Wohngebäuden; OSM-Werte nur in der _odbl-Datei.

Aufruf: python -I skripte/dz_denkmale.py [--pruefen]
  --pruefen  rechnet alles neu und vergleicht byte-genau mit den Dateien im Repo, schreibt nichts.
Rückgabe 0 = geschrieben bzw. gleich, 1 = Abweichung (--pruefen), 2 = BDOT10k fehlt, 3 = Eingang in fremdem Format,
  4 = Abruftag eines Registereingangs fehlt in eingang/HERKUNFT.md (stand von denkmale.js ist der jüngste Abruftag der
  vorhandenen Register, nicht das BDOT10k-Datum), 5 = Ergebnis der Sichtprüfung passt nicht zur Stichprobe.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import random
import re
import struct
import sys
import zipfile
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

from pyproj import CRS, Transformer
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.ops import polygonize, unary_union
from shapely.prepared import prep
from shapely.strtree import STRtree

WURZEL = Path(__file__).resolve().parent.parent
BDOT_REL = "2026-11-13/03_gebaeude/1261_SHP.zip"
BDOT_STAND = "2026-10-03"          # Dateidatum der Shapefiles im Paket (unzip -l), Abruf 13.11.2026
PRAEFIX = "PL.PZGiK.283.BDOT10k.1261__"
EINGANG = {"wd": "wikidata_zabytki_krakow.json", "nid": "nid_rejestr_zabytkow.csv", "gez": "gez_krakow.csv"}
KLASSEN = [("vor_1800", -9999, 1799), ("1800_1866", 1800, 1866), ("1867_1918", 1867, 1918),
           ("1919_1945", 1919, 1945), ("1946_1989", 1946, 1989), ("ab_1990", 1990, 9999)]
TREFFER_M = 10.0                   # nächstes Gebäude bis 10 m (Protokoll)
STICHPROBE = 20
STARTWERT = 20261113
STARTWERT_2 = 20261114             # zweite Runde der Sichtprüfung (Protokoll, Nachtrag 3): Lage und Ansicht
WOHN = "budynki mieszkalne"
MFH = "budynek wielorodzinny"
ZESPOL = "zespół zabudowy historycznej"
# Kurzschlüssel der Komplexarten für die Seiten (Texte in der Textschicht, Namen der Art bleiben polnisch im Beleg)
KUZA_ART = {"zespół zabudowy historycznej": "zabudowa", "twierdza lub forteca": "twierdza",
            "zespół muzealny": "muzeum", "miejsce pamięci narodowej": "pamiec"}
VERMERK_BDOT = ("Źródło: Baza Danych Obiektów Topograficznych BDOT10k, Główny Urząd Geodezji i Kartografii "
                "(geoportal.gov.pl), stan plików 2026-10-03, pobrano 2026-11-13; dane przetworzone.")
VERMERK_WD = "Wikidata, CC0 1.0"
VERMERK_OSM = "© OpenStreetMap-Mitwirkende, ODbL 1.0 (https://www.openstreetmap.org/copyright)"
SICHT_EINGABE = "belege/DZ_sichtpruefung.json"   # Ergebnis der zweiten Runde (Protokoll, Nachtrag 4), von Hand
SICHT_PFAD = WURZEL / SICHT_EINGABE              # pruefen/DZ_test_eingang.py setzt einen Wegwerf-Pfad
SICHT_WERTE = {"lage": ("ja", "daneben", "nein"), "ansicht": ("ja", "nein", "unklar")}


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")


# ------------------------------------------------------------------------------------- Shapefile ohne GDAL
def dbf_zeilen(roh: io.BufferedIOBase):
    """Zeilen einer dBASE-Datei als dict (Zeichensatz UTF-8 laut .cpg der Lieferung); gelöschte als None."""
    kopf = roh.read(32)
    anzahl, kopflaenge, satzlaenge = struct.unpack("<IHH", kopf[4:12])
    rest = roh.read(kopflaenge - 32)
    felder, pos, off = [], 0, 1
    while rest[pos] != 0x0D:
        name = rest[pos:pos + 11].split(b"\0")[0].decode("ascii")
        laenge = rest[pos + 16]
        felder.append((name, off, laenge))
        off += laenge
        pos += 32
    for _ in range(anzahl):
        satz = roh.read(satzlaenge)
        if satz[:1] == b"*":
            yield None
            continue
        yield {n: satz[o:o + ln].decode("utf-8").strip() for n, o, ln in felder}


def shp_formen(roh: io.BufferedIOBase):
    """Flächen (Typ 5/15/25) einer .shp als shapely-Geometrie, Ringe nach Umlaufsinn (außen im Uhrzeigersinn)."""
    kopf = roh.read(100)
    typ = struct.unpack("<i", kopf[32:36])[0]
    if typ not in (5, 15, 25):
        raise ValueError(f"Shapefile-Typ {typ} statt Fläche")
    while True:
        rk = roh.read(8)
        if len(rk) < 8:
            return
        laenge = struct.unpack(">i", rk[4:8])[0] * 2
        inhalt = roh.read(laenge)
        styp = struct.unpack("<i", inhalt[:4])[0]
        if styp == 0:
            yield None
            continue
        teile_n, punkte_n = struct.unpack("<ii", inhalt[36:44])
        teile = list(struct.unpack(f"<{teile_n}i", inhalt[44:44 + 4 * teile_n])) + [punkte_n]
        p0 = 44 + 4 * teile_n
        xy = struct.unpack(f"<{2 * punkte_n}d", inhalt[p0:p0 + 16 * punkte_n])
        ringe = [[(xy[2 * j], xy[2 * j + 1]) for j in range(teile[i], teile[i + 1])] for i in range(teile_n)]
        yield ringe_zu_flaeche(ringe)


def ringe_zu_flaeche(ringe: list[list[tuple[float, float]]]):
    def flaeche2(r):
        return sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1))
    aussen = [r for r in ringe if len(r) >= 4 and flaeche2(r) < 0]
    innen = [r for r in ringe if len(r) >= 4 and flaeche2(r) >= 0]
    if not aussen:                      # Umlaufsinn verdreht: alle Ringe als Außenringe nehmen
        aussen, innen = innen, []
    polys = []
    for a in aussen:
        pa = Polygon(a)
        loecher = [i for i in innen if pa.contains(Point(i[0]))]
        polys.append(Polygon(a, loecher))
    g = polys[0] if len(polys) == 1 else MultiPolygon(polys)
    return g if g.is_valid else g.buffer(0)


def schicht(z: zipfile.ZipFile, name: str):
    """(Geometrie, Attribute) je Objekt einer BDOT10k-Schicht."""
    with z.open(f"{PRAEFIX}{name}.dbf") as d, z.open(f"{PRAEFIX}{name}.shp") as s:
        for attr, geom in zip(dbf_zeilen(d), shp_formen(s), strict=True):
            if attr is not None and geom is not None:
                yield geom, attr


# ------------------------------------------------------------------------------------- Bauzeitklassen
def klasse_jahr(j: int) -> str:
    return next(k for k, a, b in KLASSEN if a <= j <= b)


def klasse_spanne(a: int, b: int) -> str | None:
    ka, kb = klasse_jahr(a), klasse_jahr(b)
    return ka if ka == kb else None


def bauzeitklasse(text: str | None) -> str | None:
    """Klasse aus einer Datumsangabe (Wikidata-Zeitwert, OSM start_date); None, wenn nicht eindeutig."""
    if not text:
        return None
    t = text.strip().lower()
    m = re.fullmatch(r"\+?(\d{4})-\d{2}-\d{2}t.*", t)                          # Wikidata 1890-01-01T00:00:00Z
    if m:
        return klasse_jahr(int(m.group(1)))
    m = re.fullmatch(r"c(\d{1,2})", t)                                      # Jahrhundert C19
    if m:
        jh = int(m.group(1))
        return klasse_spanne(100 * (jh - 1), 100 * jh - 1)
    m = re.fullmatch(r"(\d{3})0s", t)                                       # Jahrzehnt 1890s
    if m:
        return klasse_spanne(int(m.group(1)) * 10, int(m.group(1)) * 10 + 9)
    m = re.fullmatch(r"(\d{4})\s*(?:\.\.|-|–)\s*(\d{4})", t)                 # Spanne
    if m:
        return klasse_spanne(int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(r"(?:~|ca\.?\s*)?(\d{4})(?:-\d{2}(?:-\d{2})?)?", t)      # Jahr, auch ~1890 oder 1890-05
    if m:
        return klasse_jahr(int(m.group(1)))
    return None


# ------------------------------------------------------------------------------------- BDOT10k
class Bdot:
    def __init__(self, pfad: Path):
        self.pfad = pfad
        with zipfile.ZipFile(pfad) as z:
            prj = z.read(f"{PRAEFIX}OT_BUBD_A.prj").decode("ascii")
            self.crs = CRS.from_wkt(prj)
            self.nach_wgs = Transformer.from_crs(self.crs, CRS.from_epsg(4326), always_xy=True)
            self.von_wgs = Transformer.from_crs(CRS.from_epsg(4326), self.crs, always_xy=True)
            self.stadt, self.delegaturen = None, {}
            for g, a in schicht(z, "OT_ADJA_A"):
                if a["RODZAJ"] == "gmina" and a["NAZWA"] == "Kraków":
                    self.stadt = g
                elif a["RODZAJ"] == "dzielnica lub delegatura":
                    self.delegaturen[a["NAZWA"]] = g
            self.komplexe = [(g, a) for g, a in schicht(z, "OT_KUZA_A")]
            self.gebaeude = [(g, a) for g, a in schicht(z, "OT_BUBD_A")]
        if self.stadt is None or len(self.delegaturen) != 4:
            raise ValueError(f"OT_ADJA_A: Stadt {'fehlt' if self.stadt is None else 'da'}, "
                             f"{len(self.delegaturen)} Delegaturen statt 4")
        self.stadt_p = prep(self.stadt)
        self.del_p = {n: prep(g) for n, g in sorted(self.delegaturen.items())}
        self.baum = STRtree([g for g, _ in self.gebaeude])

    def delegatura(self, p: Point) -> str | None:
        return next((n for n, g in self.del_p.items() if g.contains(p)), None)

    def gebaeude_bei(self, p: Point) -> int | None:
        """Index des Gebäudes, das den Punkt enthält, sonst das nächste bis TREFFER_M, sonst None."""
        for i in self.baum.query(p, predicate="intersects"):
            return int(i)
        i = self.baum.query_nearest(p, max_distance=TREFFER_M)
        return int(i[0]) if len(i) else None

    def wgs(self, x: float, y: float, stellen: int = 5) -> list[float]:
        lon, lat = self.nach_wgs.transform(x, y)
        return [round(lon, stellen), round(lat, stellen)]


def ist_wohn(a: dict) -> bool:
    return a["FOBUD"] == WOHN


def ist_mfh(a: dict) -> bool:
    return a["FOBUD"] == WOHN and a["PFBUD"] == MFH


def bdot_rechnen(b: Bdot) -> tuple[dict, dict]:
    """daten/denkmale_bdot.js und die Zählungen für den Beleg."""
    z: dict = {"gebaeude": len(b.gebaeude), "kat_istnie": dict(sorted(Counter(a["KAT_ISTNIE"] for _, a in b.gebaeude).items()))}
    zespol = prep(MultiPolygon([p for g, a in b.komplexe if a["RODZAJ"] == ZESPOL
                                for p in (g.geoms if isinstance(g, MultiPolygon) else [g])]))
    je_del = {n: {"wohngebaeude": 0, "mehrfamilienhaeuser": 0, "namensbezug": 0} for n in b.del_p}
    ohne = {"wohngebaeude": 0, "mehrfamilienhaeuser": 0, "namensbezug": 0}
    wohn = mfh = name_n = mfh_zespol = 0
    punkte = []
    for g, a in b.gebaeude:
        w, m = ist_wohn(a), ist_mfh(a)
        nb = a["NAZWA"].lower().startswith("kamienica")
        if not (w or nb):
            continue
        c = g.centroid
        d = b.delegatura(c)
        ziel = je_del[d] if d else ohne
        if w:
            wohn += 1
            ziel["wohngebaeude"] += 1
        if m:
            mfh += 1
            ziel["mehrfamilienhaeuser"] += 1
            if zespol.contains(c):
                mfh_zespol += 1
        if nb:
            name_n += 1
            ziel["namensbezug"] += 1
            gs = int(float(a["LICZ_KONDY"])) if a["LICZ_KONDY"] else None
            punkte.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": b.wgs(c.x, c.y)},
                           "properties": {"w": w, "mfh": m, "gs": gs, "del": d}})
    punkte.sort(key=lambda f: f["geometry"]["coordinates"])
    z.update({"wohngebaeude": wohn, "mehrfamilienhaeuser": mfh, "namensbezug": name_n,
              "mfh_in_zespol_zabudowy": mfh_zespol})
    arten = Counter(a["RODZAJ"] for _, a in b.komplexe)
    z["komplexe"] = dict(sorted((KUZA_ART[k], v) for k, v in arten.items()))
    komplexe = []
    for g, a in b.komplexe:
        e = g.simplify(1.0, preserve_topology=True)
        polys = e.geoms if isinstance(e, MultiPolygon) else [e]
        koord = [[[b.wgs(x, y, 6) for x, y in r.coords] for r in [p.exterior, *p.interiors]] for p in polys]
        geom = ({"type": "Polygon", "coordinates": koord[0]} if len(koord) == 1
                else {"type": "MultiPolygon", "coordinates": koord})
        komplexe.append({"type": "Feature", "geometry": geom,
                         "properties": {"r": KUZA_ART[a["RODZAJ"]], "n": a["NAZWA"] or None, "del": b.delegatura(g.centroid)}})
    komplexe.sort(key=lambda f: (f["properties"]["r"], f["properties"]["n"] or "", json.dumps(f["geometry"])[:80]))
    daten = {"stand": BDOT_STAND, "teilmenge": True, "flaechenaussage": False,
             "quelle": {"name": "BDOT10k 1261", "vermerk": VERMERK_BDOT},
             "zaehlung": z, "delegaturen": je_del, "nicht_zugeordnet": ohne,
             "komplexe": {"type": "FeatureCollection", "features": komplexe},
             "namensbezug": {"type": "FeatureCollection", "features": punkte}}
    return daten, z


# ------------------------------------------------------------------------------------- Register (Handdownloads)
def normnr(t: str) -> str:
    """Registernummer zum Vergleich: ohne Leerraum und Bindestriche, groß („A 1“, „a-1“ → „A1“; Protokoll)."""
    return re.sub(r"[\s\-‐–]+", "", t or "").upper()


def wikidata_lesen(pfad: Path) -> list[dict]:
    """SPARQL-JSON der WDQS-Abfrage aus quellen-DZ.md; je Objekt Registernummern, Lage, Bauzeitklasse."""
    j = json.loads(pfad.read_text(encoding="utf-8"))
    vars_ = set(j.get("head", {}).get("vars", []))
    if not {"item", "nr"} <= vars_:
        raise FormatFehler(f"{pfad.name}: Variablen {sorted(vars_)}, erwartet mindestens item, nr")
    obj: dict[str, dict] = {}
    for z in j["results"]["bindings"]:
        q = z["item"]["value"].rsplit("/", 1)[-1]
        o = obj.setdefault(q, {"nr": set(), "lage": None, "klassen": set(), "zeilen": 0})
        o["zeilen"] += 1
        o["nr"].add(normnr(z["nr"]["value"]))
        if "coord" in z and o["lage"] is None:
            m = re.fullmatch(r"Point\(([-\d.]+) ([-\d.]+)\)", z["coord"]["value"])
            if m:
                o["lage"] = (float(m.group(1)), float(m.group(2)))
        if "inception" in z:
            o["klassen"].add(bauzeitklasse(z["inception"]["value"]))
    aus = []
    for q, o in sorted(obj.items()):
        kl = o["klassen"]
        aus.append({"q": q, "nr": sorted(o["nr"]), "lage": o["lage"],
                    "ep": next(iter(kl)) if len(kl) == 1 else None, "ep_angabe": bool(kl), "zeilen": o["zeilen"]})
    return aus


def csv_lesen(pfad: Path, brauche_nr: bool) -> tuple[list[dict], dict]:
    """Register als CSV (Format nicht geprüft): Spalten nach Namensmuster; bricht ab, wenn die Nummer fehlt."""
    text = pfad.read_text(encoding="utf-8-sig")
    dialekt = csv.Sniffer().sniff(text[:20000], delimiters=";,\t")
    zeilen = list(csv.DictReader(io.StringIO(text), dialect=dialekt))
    spalten = list(zeilen[0].keys()) if zeilen else []

    def spalte(muster: str) -> str | None:
        return next((s for s in spalten if re.search(muster, s or "", re.I)), None)
    s_nr, s_lat, s_lon = spalte(r"rejestr|nr_rej|numer"), spalte(r"szeroko|^lat|latitude"), spalte(r"długo|dlugo|^lon|longitude")
    s_dat = spalte(r"datowanie|data_powst|czas_powst")
    if brauche_nr and not s_nr:
        raise FormatFehler(f"{pfad.name}: keine Spalte mit Registernummer unter {spalten[:12]}")
    aus = []
    for z in zeilen:
        lage = None
        try:
            if s_lat and s_lon and z[s_lat] and z[s_lon]:
                lage = (float(z[s_lon].replace(",", ".")), float(z[s_lat].replace(",", ".")))
        except ValueError:
            lage = None
        aus.append({"nr": [normnr(z[s_nr])] if s_nr and z[s_nr] else [], "lage": lage,
                    "ep": bauzeitklasse(z[s_dat]) if s_dat else None, "ep_angabe": bool(s_dat and z[s_dat])})
    return aus, {"spalten": spalten, "nr": s_nr, "lat": s_lat, "lon": s_lon, "datierung": s_dat}


class AbruftagFehlt(Exception):
    pass


def abruftag(eingang: Path, datei: str) -> str:
    """Abruftag einer Eingangsdatei aus ihrer Zeile in eingang/HERKUNFT.md (letzte Spalte, TT.MM.JJJJ) als JJJJ-MM-TT.

    Die Zeile beginnt mit „| <Dateiname>“. Ohne Zeile oder ohne Datum bricht der Lauf ab; kein Ersatz durch das
    BDOT10k-Datum oder die Dateizeit.
    """
    herkunft = eingang / "HERKUNFT.md"
    zeilen = herkunft.read_text(encoding="utf-8").splitlines() if herkunft.is_file() else []
    for z in zeilen:
        zellen = [c.strip() for c in z.strip().strip("|").split("|")]
        if len(zellen) >= 2 and (zellen[0] == datei or zellen[0].startswith(datei + " ")):
            m = re.search(r"\b(\d{2})\.(\d{2})\.(\d{4})\b", zellen[-1])
            if m:
                return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
            break
    raise AbruftagFehlt(f"{datei}: kein Abruftag (TT.MM.JJJJ in der letzten Spalte) in {herkunft}")


class FormatFehler(Exception):
    pass


def punkt_einordnen(b: Bdot, lon: float, lat: float) -> dict | None:
    """Lage in der Stadt, Gebäudetreffer, Wohnnutzung, Delegatura; None außerhalb der Stadt."""
    x, y = b.von_wgs.transform(lon, lat)
    p = Point(x, y)
    if not b.stadt_p.contains(p):
        return None
    i = b.gebaeude_bei(p)
    a = b.gebaeude[i][1] if i is not None else None
    return {"lage": [round(lon, 5), round(lat, 5)], "geb": i, "w": ist_wohn(a) if a else None,
            "mfh": ist_mfh(a) if a else None, "del": b.delegatura(p)}


def register_rechnen(b: Bdot, eingang: Path) -> tuple[dict, dict, list]:
    quellen, zaehl, objekte, stich = {}, {}, {}, []
    nr_index: dict[str, str] = {}
    for kurz in ("wd", "nid", "gez"):
        pfad = eingang / EINGANG[kurz]
        if not pfad.is_file():
            quellen[kurz] = {"vorhanden": False}
            continue
        if kurz == "wd":
            zeilen, info = wikidata_lesen(pfad), {}
        else:
            zeilen, info = csv_lesen(pfad, brauche_nr=(kurz == "nid"))
        z = Counter()
        z["zeilen"] = len(zeilen)
        treffer = []
        for n, o in enumerate(zeilen):
            schl = next((nr_index[x] for x in o["nr"] if x in nr_index), None)
            if schl:
                z["doppelt_ueber_nummer"] += 1
                objekte[schl]["q"].add(kurz)
                if objekte[schl]["ep"] is None and o["ep"]:
                    objekte[schl]["ep"] = o["ep"]
                continue
            if o["lage"] is None:
                z["ohne_lage"] += 1
                continue
            z["mit_lage"] += 1
            e = punkt_einordnen(b, *o["lage"])
            if e is None:
                z["ausserhalb_stadt"] += 1
                continue
            z["in_stadt"] += 1
            z["treffer_gebaeude"] += e["geb"] is not None
            z["davon_mfh"] += bool(e["mfh"])
            z["bauzeit_lesbar"] += o["ep"] is not None
            z["bauzeit_nicht_lesbar"] += o["ep_angabe"] and o["ep"] is None
            schl = f"{kurz}:{n:06d}"
            objekte[schl] = {"q": {kurz}, "ep": o["ep"], "kenn": o.get("q"), **e}
            for x in o["nr"]:
                nr_index.setdefault(x, schl)
            if e["geb"] is not None:
                treffer.append(schl)
        quellen[kurz] = {"vorhanden": True, "datei": EINGANG[kurz], "sha256": sha256(pfad),
                         "abruf": abruftag(eingang, EINGANG[kurz]), **({"spalten": info} if info else {}),
                         **({"vermerk": VERMERK_WD} if kurz == "wd" else {})}
        zaehl[kurz] = dict(sorted(z.items()))
        rnd = random.Random(STARTWERT)
        stich += [(kurz, s) for s in rnd.sample(treffer, min(STICHPROBE, len(treffer)))]
    feats, kam = [], Counter()
    # Grundgesamtheit der zweiten Stichprobe (Nachtrag 3): alle Registerpunkte aus Wikidata, wie die Karte sie zeigt
    pool_wd = sorted(({"lage": o["lage"], "id": o["kenn"]} for o in objekte.values() if "wd" in o["q"]),
                     key=lambda x: (x["lage"], x["id"] or ""))
    for schl, o in sorted(objekte.items(), key=lambda kv: kv[1]["lage"]):
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": o["lage"]},
                      "properties": {"q": sorted(o["q"]), "ep": o["ep"], "w": o["w"], "mfh": o["mfh"], "del": o["del"]}})
        if o["mfh"]:
            kam[o["del"] or "-"] += 1
    stich_text = [(k, objekte[s]) for k, s in stich]
    return ({"quellen": quellen, "zaehlung": zaehl, "objekte": feats, "kamienice": dict(sorted(kam.items())),
             "pool_wd": pool_wd}, zaehl, stich_text)


# ------------------------------------------------------------------------------------- OSM (ODbL)
def osm_rechnen(b: Bdot, pbf: Path) -> tuple[dict, dict]:
    sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
    import osm_pbf  # noqa: E402  (Leser des Pakets OSM und Fußwegnetz, nur gelesen)

    def wahl(t: dict) -> bool:   # die Ortsmarke liest skripte/ortsmarke.py selbst
        return "heritage" in t or "start_date" in t
    w, s, o, n = b.stadt.bounds
    (lw, ls), (lo, ln) = b.nach_wgs.transform(w, s), b.nach_wgs.transform(o, n)
    def rel_wahl(t: dict) -> bool:  # Flächen als Relation (Multipolygon), z. B. große Bauten mit Innenhof
        return t.get("type") == "multipolygon" and wahl(t)
    rahmen = (lw - 0.01, ls - 0.01, lo + 0.01, ln + 0.01)
    erg = osm_pbf.lies(pbf, rechteck=rahmen, knoten_wahl=wahl, weg_wahl=wahl, relation_wahl=rel_wahl)
    # Zweiter Durchgang: Wege der Relationen (meist ohne eigene Tags, in der Datei vor den Relationen)
    mitglied_ids = {ref for _rid, _t, m in erg.relationen for (art, ref, _rolle) in m if art == "w"}
    zweit = osm_pbf.lies(pbf, rechteck=None, knoten_wahl=lambda t: False, weg_wahl=lambda t: False,
                         relation_wahl=lambda t: False, knoten_lesen=False, weg_ids=mitglied_ids)
    mitglied_wege = {wid: ids for wid, _t, ids in zweit.wege}
    z = Counter({"relationen_gelesen": len(erg.relationen), "relationen_ohne_lage": 0, "relationen_ohne_flaeche": 0,
                 "relationen_unvollstaendig": 0, "wege_als_teil_einer_relation": 0, "aus_relationen": 0})
    rel_kandidaten, aussen_ids = [], set()
    for rid, t, mitglieder in erg.relationen:
        ringe = {"outer": [], "inner": []}
        vollstaendig = True
        for art, ref, rolle in mitglieder:
            if art != "w":
                continue
            ids = mitglied_wege.get(ref)
            lon, lat, ok = erg.koordinaten(ids) if ids is not None else (None, None, None)
            if ids is None or not ok.all():
                vollstaendig = False
                continue
            ringe["inner" if rolle == "inner" else "outer"].append(LineString(list(zip(lon, lat))))
        if not ringe["outer"]:
            z["relationen_ohne_lage"] += 1          # ganz außerhalb des Rahmens oder ohne äußeren Ring
            continue
        aussen = unary_union(list(polygonize(unary_union(ringe["outer"]))))
        innen = unary_union(list(polygonize(unary_union(ringe["inner"])))) if ringe["inner"] else None
        g = aussen.difference(innen) if innen is not None and not innen.is_empty else aussen
        if g.is_empty:
            z["relationen_ohne_flaeche"] += 1
            continue
        z["relationen_unvollstaendig"] += not vollstaendig
        aussen_ids |= {ref for art, ref, rolle in mitglieder if art == "w" and rolle != "inner"}
        p = g.representative_point()                 # liegt sicher in der Fläche, nicht im Innenhof
        rel_kandidaten.append((t, float(p.x), float(p.y), True, f"r{rid}"))
    kandidaten = [(t, lon, lat, False, f"n{nid}") for nid, lon, lat, t in erg.getaggte_knoten]
    for wid, t, ids in erg.wege:
        lon, lat, ok = erg.koordinaten(ids)
        if not ok.any():
            continue
        if wid in aussen_ids:                         # derselbe Bau wie seine Relation: nur einmal zählen
            z["wege_als_teil_einer_relation"] += 1
            continue
        kandidaten.append((t, float(lon[ok].mean()), float(lat[ok].mean()), False, f"w{wid}"))
    kandidaten += rel_kandidaten
    feats, orte, kam, treffer, pool = [], [], Counter(), [], []
    for t, lon, lat, aus_rel, kenn in kandidaten:
        e = punkt_einordnen(b, lon, lat)
        if e is None:
            z["ausserhalb_stadt"] += 1
            continue
        if not ("heritage" in t or "start_date" in t):
            continue
        z["objekte"] += 1
        z["aus_relationen"] += aus_rel
        z["mit_heritage"] += "heritage" in t
        z["mit_start_date"] += "start_date" in t
        z["treffer_gebaeude"] += e["geb"] is not None
        z["davon_mfh"] += bool(e["mfh"])
        ep = bauzeitklasse(t.get("start_date"))
        z["bauzeit_lesbar"] += ep is not None
        z["bauzeit_nicht_lesbar"] += "start_date" in t and ep is None
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": e["lage"]},
                      "properties": {"h": "heritage" in t, "ep": ep, "w": e["w"], "mfh": e["mfh"], "del": e["del"]}})
        if "heritage" in t:                            # zweite Stichprobe: alle Denkmale der Karte (Nachtrag 3)
            pool.append({"lage": e["lage"], "id": kenn})
        if e["geb"] is not None and "heritage" in t:   # Stichprobe nur aus Denkmal-Treffern (Protokoll, Nachtrag 2)
            treffer.append({"lage": e["lage"], "mfh": e["mfh"], "del": e["del"], "ep": ep})
        if e["mfh"] and "heritage" in t:
            kam[e["del"] or "-"] += 1
    feats.sort(key=lambda f: (f["geometry"]["coordinates"], json.dumps(f["properties"], sort_keys=True)))
    # Ortsmarke ul. Kościuszki 18: ein Punkt für alle Dateien (skripte/ortsmarke.py, pruefen/N1_protokoll.md Regel 3)
    import ortsmarke  # noqa: E402
    om = ortsmarke.kosciuszki_18(pbf, (lw - 0.01, ls - 0.01, lo + 0.01, ln + 0.01),
                                 lambda x, y: b.stadt_p.contains(Point(*b.von_wgs.transform(x, y))))
    if om:
        orte.append({"schluessel": ortsmarke.SCHLUESSEL, "geometry": {"type": "Point", "coordinates": [om["lon"], om["lat"]]},
                     "lage_geprueft": False, "quelle": "osm"})
    # Stichprobe zur Sichtprüfung (Protokoll Regel 7, auch für OSM): 20 Treffer mit Gebäude und heritage, fester
    # Startwert (vorher aus allen Treffern, auch solchen nur mit start_date; die sind keine Denkmale)
    treffer.sort(key=lambda x: (x["lage"], json.dumps(x, sort_keys=True)))
    stich = random.Random(STARTWERT).sample(treffer, min(STICHPROBE, len(treffer)))
    # Stand = osmosis_replication_timestamp aus dem Kopf des Auszugs (UTC-Tag), nicht das BDOT10k-Datum
    kopf = osm_pbf.kopf_lesen(pbf)
    if not (kopf and kopf.zeitstempel):
        raise SystemExit(f"{pbf.name}: Kopf ohne osmosis_replication_timestamp, Stand der OSM-Daten unbekannt")
    stand = datetime.fromtimestamp(kopf.zeitstempel, UTC).strftime("%Y-%m-%d")
    return ({"objekte": feats, "kamienice": dict(sorted(kam.items())), "ortsmarken": orte[:1], "stand": stand,
             "eingang": {"datei": pbf.name, "sha256": sha256(pbf)}, "stichprobe": stich, "ortsmarke_osm": om,
             "pool": sorted(pool, key=lambda x: (x["lage"], x["id"]))},
            dict(sorted(z.items())))


# ------------------------------------------------------------------------------------- Beispieldaten
def beispielpunkte(b: Bdot, n: int, startwert: int, felder) -> list[dict]:
    """Erfundene Punkte in der Stadt (gleichmäßig zufällig, fester Startwert), sichtbar als Beispieldaten."""
    rnd = random.Random(startwert)
    w, s, o, nn = b.stadt.bounds
    aus = []
    while len(aus) < n:
        x, y = rnd.uniform(w, o), rnd.uniform(s, nn)
        p = Point(x, y)
        if not b.stadt_p.contains(p):
            continue
        aus.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": b.wgs(x, y)},
                    "properties": felder(rnd, b.delegatura(p))})
    aus.sort(key=lambda f: f["geometry"]["coordinates"])
    return aus


def _bsp_nutzung(rnd) -> tuple[bool, bool]:
    w = rnd.choice([True, False])
    return w, w and rnd.choice([True, False])


def bsp_register(rnd, d):
    q, ep = [rnd.choice(["nid", "wd"])], rnd.choice([k for k, _, _ in KLASSEN] + [None])
    w, m = _bsp_nutzung(rnd)
    return {"q": q, "ep": ep, "w": w, "mfh": m, "del": d}


def bsp_osm(rnd, d):
    ep = rnd.choice([k for k, _, _ in KLASSEN] + [None])
    w, m = _bsp_nutzung(rnd)
    return {"h": True, "ep": ep, "w": w, "mfh": m, "del": d}


ORTSMARKE_LEER = {"schluessel": "kosciuszki_18", "geometry": None, "lage_geprueft": False, "quelle": None}


# ------------------------------------------------------------------------------------- Ausgabe
def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for teil in iter(lambda: f.read(1 << 20), b""):
            h.update(teil)
    return h.hexdigest()


def js(name: str, kopf: str, inhalt: dict) -> str:
    return f"/* {kopf} */\nwindow.{name}=" + json.dumps(inhalt, ensure_ascii=False, separators=(",", ":")) + ";\n"


def beleg(z_bdot: dict, z_reg: dict, z_osm: dict | None, quellen: dict, stich: list, bdot_sha: str,
          osm_eingang: dict | None, d_bdot: dict, ortsmarke_osm: dict | None = None, stich2: dict | None = None,
          sicht: dict | None = None) -> str:
    def tab(d: dict) -> str:
        return "\n".join(f"| {k} | {v} |" for k, v in d.items())
    t = ["# Lauf Denkmale und Kamienice (erzeugt von `skripte/dz_denkmale.py`, nicht von Hand ändern)", "",
         "Regeln: `pruefen/DZ_protokoll.md`. Diese Datei entsteht bei jedem Lauf neu und ist Teil der "
         "Reproduzierbarkeitsprüfung (`--pruefen`).", "",
         "## Eingänge", "", "| Eingang | Datei | SHA256 |", "|---|---|---|",
         f"| BDOT10k 1261 | `$KIEZ_DATEN/{BDOT_REL}` | `{bdot_sha}` |"]
    for k in ("wd", "nid", "gez"):
        q = quellen[k]
        t.append(f"| {k} | `eingang/{EINGANG[k]}` | `{q['sha256']}` |" if q["vorhanden"]
                 else f"| {k} | `eingang/{EINGANG[k]}` | fehlt (Beispieldaten, solange alle drei fehlen) |")
    t.append(f"| osm | `eingang/{osm_eingang['datei']}` | `{osm_eingang['sha256']}` |" if osm_eingang
             else "| osm | `eingang/*.osm.pbf` | fehlt (Beispieldaten in `daten/denkmale_odbl.js`) |")
    t += ["", "## Schritt 1: BDOT10k (echte Daten)", "", "| Zählung | Wert |", "|---|---|"]
    flach = {k: v for k, v in z_bdot.items() if not isinstance(v, dict)}
    t.append(tab(flach))
    for k in ("kat_istnie", "komplexe"):
        t += ["", f"`{k}`:", "", "| Wert | Anzahl |", "|---|---|", tab(z_bdot[k]),
              f"| Summe | {sum(z_bdot[k].values())} |"]
    t += ["", "Je Delegatura (Schwerpunkt im Umriss aus `OT_ADJA_A`):", "",
          "| Delegatura | Wohngebäude | Mehrfamilienhäuser | Namensbezug |", "|---|---|---|---|"]
    summe = Counter()
    for n, v in [*d_bdot["delegaturen"].items(), ("keiner zugeordnet", d_bdot["nicht_zugeordnet"])]:
        t.append(f"| {n} | {v['wohngebaeude']} | {v['mehrfamilienhaeuser']} | {v['namensbezug']} |")
        summe.update(v)
    t.append(f"| Summe | {summe['wohngebaeude']} | {summe['mehrfamilienhaeuser']} | {summe['namensbezug']} |")
    t += ["", "## Schritt 2: Register (Wikidata, NID, Gminna ewidencja)", ""]
    if not z_reg:
        t.append("Kein Eingang vorhanden. `daten/denkmale.js` trägt Beispieldaten (`fixture: true`).")
    for k, z in z_reg.items():
        t += [f"`{k}`:", "", "| Zählung | Wert |", "|---|---|", tab(z), ""]
        if quellen[k].get("spalten"):
            t += [f"Spalten erkannt: `{json.dumps(quellen[k]['spalten'], ensure_ascii=False)}`", ""]
    t += ["", "## Schritt 3: OSM heritage/start_date", ""]
    t += (["| Zählung | Wert |", "|---|---|", tab(z_osm)] if z_osm is not None
          else ["Kein Eingang vorhanden. `daten/denkmale_odbl.js` trägt Beispieldaten (`fixture: true`)."])
    if z_osm is not None:
        om = ortsmarke_osm
        t += ["", "Ortsmarke ul. Kościuszki 18 (`skripte/ortsmarke.py`, dieselbe Koordinate wie in "
              "`daten/sanierung_odbl.js`): " + (f"OSM `{om['osm']}` ({om['art']}, {om['kandidaten']} Kandidaten in "
              f"der Stadt), Punkt {om['lon']}, {om['lat']}; Lage nicht von Hand geprüft" if om else "keine")]
    t += ["", "## Stichprobe zur Sichtprüfung, erste Runde (Startwert 20261113)", ""]
    if not stich:
        t.append("Keine Registertreffer, keine Stichprobe.")
    else:
        t += [("Ausgewertet: nein. Niemand hat die Punkte bisher am Luftbild geprüft; `daten/denkmale_odbl.js` trägt "
               "deshalb `sichtpruefung.geprueft: false`." if not sicht else
               "Ausgewertet: nein. Diese Runde ist von keinem Menschen geprüft; abgelöst durch die zweite Runde "
               "(unten, ausgewertet), nach der sich `sichtpruefung` in den Datendateien richtet.")
              + " OSM-Punkte nur aus Gebäudetreffern mit `heritage` (`pruefen/DZ_protokoll.md`, Nachtrag 2).", "",
              "| Quelle | Lage (Länge, Breite) | Mehrfamilienhaus | Delegatura | Bauzeitklasse |", "|---|---|---|---|---|"]
        t += [f"| {k} | {o['lage'][0]}, {o['lage'][1]} | {o['mfh']} | {o['del']} | {o['ep']} |" for k, o in stich]
    if stich2:
        g = stich2["grundgesamtheit"]
        t += ["", f"## Stichprobe zur Sichtprüfung, zweite Runde (Startwert {stich2['startwert']})", "",
              "Regel: `pruefen/DZ_protokoll.md`, Nachtrag 3. Geprüft werden nur Lage und Ansicht. Grundgesamtheit ist "
              f"die Menge der Karte: {g.get('wd', 0)} Registerpunkte aus Wikidata und {g.get('osm', 0)} OSM-Objekte mit "
              + ("`heritage`. Ausgewertet: nein; `sichtpruefung.geprueft` bleibt `false`. " if not sicht else
                 "`heritage`. Ausgewertet: ja (Abschnitt „Sichtprüfung Runde 2, ausgewertet“). ")
              + "Dieselbe Liste maschinenlesbar: `belege/DZ_sichtpruefung_stichprobe.json`.", "",
              "| Nr. | Quelle | Kennung | Lage (Länge, Breite) | Lage stimmt | Ansicht passt |", "|---|---|---|---|---|---|"]
        aw = sicht["antworten"] if sicht else {}
        t += [f"| {i} | {x['quelle']} | {x['id']} | {x['lon']}, {x['lat']} | "
              + (f"{aw[(x['quelle'], x['id'])]['lage']} | {aw[(x['quelle'], x['id'])]['ansicht']} |" if sicht else "| |")
              for i, x in enumerate(stich2["punkte"], 1)]
    if sicht:
        t += ["", "## Sichtprüfung Runde 2, ausgewertet", "",
              f"Eingabe `{SICHT_EINGABE}` (von Hand, Prüfung am {sicht['datum']}, Ortofotomapa Geoportal, Quelle je "
              "Punkt verdeckt), vom Skript gegen die Stichprobe geprüft: jede Kennung aus der Stichprobe, jeder Punkt "
              "genau einmal, Werte aus den erlaubten Listen. Regel vor dem Rechnen festgelegt (`pruefen/DZ_protokoll.md`, "
              "Nachtrag 4): Lage-Quote = ja / alle (daneben zählt nicht als ja), Ansicht-Quote = ja / entschiedene "
              "(ja + nein, unklar nicht im Nenner); 95-%-Intervall nach Wilson.", "",
              "| Quelle | n | Lage ja | daneben | nein | Lage-Quote % | Wilson 95 % | Ansicht ja | nein | unklar | "
              "Ansicht-Quote % (ja von entschiedenen) | Wilson 95 % |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        def zahl1(x) -> str:
            return "–" if x is None else f"{x:.1f}".replace(".", ",")
        def spanne(w: list | None) -> str:   # None, wenn der Nenner 0 ist (etwa alle Ansichten „unklar“)
            return "–" if w is None else f"{zahl1(w[0])}–{zahl1(w[1])}"
        for name, e in [*((("Wikidata" if q == "wd" else "OSM"), v) for q, v in sicht["je"].items()),
                        ("gesamt", sicht["gesamt"])]:
            la, an = e["lage"], e["ansicht"]
            t.append(f"| {name} | {e['n']} | {la['ja']} | {la['daneben']} | {la['nein']} | {zahl1(la['quote'])} | "
                     f"{spanne(la['wilson95'])} | {an['ja']} | {an['nein']} | {an['unklar']} | "
                     f"{zahl1(an['quote'])} ({an['ja']} von {an['entschieden']}) | {spanne(an['wilson95'])} |")
        t += ["", "Die Quote beschreibt die Ebene, gewonnen aus einer Zufallsstichprobe von je 20 Punkten; sie sagt nichts "
              "über einen einzelnen Punkt außerhalb der Stichprobe. Bauzeitklasse und Zuordnung zum Gebäude waren nicht "
              "Gegenstand der Runde. In `daten/` steht kein Name des Prüfers, nur `pruefer_rolle: sichtpruefung_luftbild`, "
              "Grundlage und Datum; `denkmale.js` trägt nur das Ergebnis der Wikidata-Punkte, `denkmale_odbl.js` das der "
              "OSM-Punkte und das Gesamtergebnis."]
    return "\n".join(t) + "\n"


def stichprobe_2(pool_wd: list[dict], pool_osm: list[dict] | None, stand: dict) -> dict:
    """Zweite Runde (Protokoll, Nachtrag 3): je 20 Punkte aus der Menge der Karte, Startwert 20261114."""
    punkte, grund = [], {}
    for quelle, pool in (("wd", pool_wd), ("osm", pool_osm)):
        if pool is None:
            continue
        grund[quelle] = len(pool)
        for x in random.Random(STARTWERT_2).sample(pool, min(STICHPROBE, len(pool))):
            punkte.append({"lon": x["lage"][0], "lat": x["lage"][1], "quelle": quelle, "id": x["id"]})
    return {"hinweis": "Zweite Stichprobe zur Sichtprüfung der Denkmalpunkte (pruefen/DZ_protokoll.md, Nachtrag 3). "
                       "Zu prüfen sind nur Lage und Ansicht am Luftbild. Erzeugt von skripte/dz_denkmale.py, nicht von "
                       "Hand ändern; das Ergebnis der Prüfung kommt in eine eigene Datei.",
            "startwert": STARTWERT_2, "geprueft": False, "pruefen": ["lage", "ansicht"],
            "stand": stand, "grundgesamtheit": grund,
            "vermerk": {"wd": VERMERK_WD, "osm": VERMERK_OSM}, "punkte": punkte}


class SichtFehler(Exception):
    pass


def wilson(k: int, n: int, z: float = 1.959964) -> list[float] | None:
    """95-%-Intervall nach Wilson in Prozent, eine Nachkommastelle (Protokoll, Nachtrag 4)."""
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    m = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (m - h), 1), round(100 * (m + h), 1)]


def quoten(antworten: list[dict]) -> dict:
    """Lage-Quote = ja / alle, Ansicht-Quote = ja / (ja + nein); unklar nicht im Nenner (Protokoll, Nachtrag 4)."""
    lage = {w: sum(a["lage"] == w for a in antworten) for w in SICHT_WERTE["lage"]}
    ans = {w: sum(a["ansicht"] == w for a in antworten) for w in SICHT_WERTE["ansicht"]}
    n, ent = len(antworten), ans["ja"] + ans["nein"]
    return {"n": n,
            "lage": {**lage, "quote": round(100 * lage["ja"] / n, 1) if n else None, "wilson95": wilson(lage["ja"], n)},
            "ansicht": {**ans, "entschieden": ent, "quote": round(100 * ans["ja"] / ent, 1) if ent else None,
                        "wilson95": wilson(ans["ja"], ent)}}


def sichtpruefung_lesen(stich2: dict) -> dict | None:
    """Ergebnis der zweiten Sichtprüfung aus belege/DZ_sichtpruefung.json gegen die Stichprobe prüfen und auswerten;
    None, solange es die Datei nicht gibt. Abbruch (SichtFehler), wenn sie nicht genau zur Stichprobe passt."""
    p = SICHT_PFAD
    if not p.is_file():
        return None
    try:
        e = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as x:
        raise SichtFehler(f"kein lesbares JSON ({x})") from None
    if not isinstance(e, dict) or not isinstance(e.get("antworten"), list):
        raise SichtFehler("erwartet ein Objekt mit der Liste antworten")
    if e.get("startwert") != STARTWERT_2 or stich2["startwert"] != STARTWERT_2:
        raise SichtFehler(f"Startwert {e.get('startwert')}, Stichprobe mit {stich2['startwert']}")
    try:
        date.fromisoformat(str(e.get("datum", "")))
        ok = re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(e.get("datum", ""))) is not None
    except ValueError:
        ok = False
    if not ok:
        raise SichtFehler(f"Datum {e.get('datum')!r} nicht als gültiges JJJJ-MM-TT")
    soll = {(x["quelle"], x["id"]) for x in stich2["punkte"]}
    gesehen, je = set(), {}
    for a in e["antworten"]:
        if not isinstance(a, dict) or not all(isinstance(a.get(k), str) for k in ("quelle", "id", "lage", "ansicht")):
            raise SichtFehler(f"Antwort {a!r}: erwartet ein Objekt mit den Texten quelle, id, lage, ansicht")
        schl = (a.get("quelle"), a.get("id"))
        if set(a) != {"quelle", "id", "lage", "ansicht"}:
            raise SichtFehler(f"{schl}: Felder {sorted(a)}, erwartet quelle, id, lage, ansicht")
        if schl not in soll:
            raise SichtFehler(f"{schl}: nicht in der Stichprobe")
        if schl in gesehen:
            raise SichtFehler(f"{schl}: doppelt")
        for k, erlaubt in SICHT_WERTE.items():
            if a[k] not in erlaubt:
                raise SichtFehler(f"{schl}: {k} = {a[k]!r}, erlaubt {erlaubt}")
        gesehen.add(schl)
        je.setdefault(a["quelle"], []).append(a)
    if gesehen != soll:
        raise SichtFehler(f"{len(soll - gesehen)} Punkte der Stichprobe ohne Antwort")
    folge = [q for q in ("wd", "osm") if q in je]
    alle = [a for q in folge for a in je[q]]
    return {"datum": e["datum"], "je": {q: quoten(je[q]) for q in folge}, "gesamt": quoten(alle),
            "antworten": {(a["quelle"], a["id"]): a for a in alle}}


def sicht_feld(sicht: dict | None, quelle: str, stichprobe: int, mit_gesamt: bool) -> dict:
    """Feld sichtpruefung einer Datendatei: ohne Ergebnis wie bisher (geprueft false), sonst Quoten der Quelle."""
    ok = bool(sicht) and quelle in sicht["je"]   # ohne Punkt dieser Quelle in der Stichprobe kein Ergebnis
    f = {"geprueft": ok, "stichprobe": stichprobe, "startwert": STARTWERT_2}
    if ok:
        f.update({"datum": sicht["datum"], "pruefer_rolle": "sichtpruefung_luftbild", "grundlage": "ortofotomapa",
                  "ergebnis": sicht["je"][quelle], **({"gesamt": sicht["gesamt"]} if mit_gesamt else {})})
    return f


def rechnen() -> dict[str, str]:
    d = daten_ordner()
    bdot_pfad = d / BDOT_REL
    if not bdot_pfad.is_file():
        print(f"BDOT10k fehlt: {bdot_pfad}", file=sys.stderr)
        sys.exit(2)
    b = Bdot(bdot_pfad)
    d_bdot, z_bdot = bdot_rechnen(b)
    eingang = d / "eingang"
    reg, z_reg, stich = register_rechnen(b, eingang)
    alle_fehlen = not any(q["vorhanden"] for q in reg["quellen"].values())
    kopf_bsp = "BEISPIELDATEN (fixture: true): erfundene Punkte, keine Quelle. "
    # stand = jüngster Abruftag der vorhandenen Register (eingang/HERKUNFT.md), nicht das BDOT10k-Datum
    stand_reg = None if alle_fehlen else max(q["abruf"] for q in reg["quellen"].values() if q["vorhanden"])
    d_reg = {"stand": stand_reg, **({"fixture": True} if alle_fehlen else {}), "teilmenge": True,
             "flaechenaussage": False, "klassen": [k for k, _, _ in KLASSEN], "quellen": reg["quellen"],
             "zaehlung": reg["zaehlung"],
             "objekte": {"type": "FeatureCollection",
                         "features": beispielpunkte(b, 12, STARTWERT, bsp_register) if alle_fehlen else reg["objekte"]},
             "kamienice": {} if alle_fehlen else reg["kamienice"], "ortsmarken": [ORTSMARKE_LEER]}
    pool_wd = [] if alle_fehlen else reg["pool_wd"]
    pbfs = sorted(eingang.glob("*.osm.pbf")) if eingang.is_dir() else []
    if pbfs:
        o, z_osm = osm_rechnen(b, pbfs[0])
        stich += [("osm", s) for s in o["stichprobe"]]
        d_osm = {"stand": o["stand"], "teilmenge": True, "flaechenaussage": False, "vermerk": VERMERK_OSM,
                 "eingang": o["eingang"], "zaehlung": z_osm,
                 # Luftbild-Stichprobe aufgelistet (belege/DZ_denkmale_lauf.md), von keinem Menschen geprüft
                 "sichtpruefung": None,      # nach der Stichprobe gesetzt (zweite Runde, Nachtrag 3 und 4)
                 "objekte": {"type": "FeatureCollection", "features": o["objekte"]},
                 "kamienice": o["kamienice"], "ortsmarken": o["ortsmarken"] or [ORTSMARKE_LEER]}
    else:
        z_osm = None
        d_osm = {"stand": None, "fixture": True, "teilmenge": True, "flaechenaussage": False,
                 "vermerk": VERMERK_OSM, "eingang": None, "zaehlung": {},
                 "objekte": {"type": "FeatureCollection", "features": beispielpunkte(b, 8, STARTWERT + 1, bsp_osm)},
                 "kamienice": {}, "ortsmarken": [ORTSMARKE_LEER]}
    stich2 = stichprobe_2(pool_wd, o["pool"] if pbfs else None, {"wd": d_reg["stand"], "osm": d_osm["stand"]})
    sicht = sichtpruefung_lesen(stich2) if not alle_fehlen and pbfs else None
    stich2["geprueft"] = bool(sicht)
    if not alle_fehlen:   # zweite Runde (Nachtrag 3); ausgewertet nur mit belege/DZ_sichtpruefung.json (Nachtrag 4)
        d_reg["sichtpruefung"] = sicht_feld(sicht, "wd", min(STICHPROBE, len(pool_wd)), mit_gesamt=False)
    if pbfs:
        d_osm["sichtpruefung"] = sicht_feld(sicht, "osm", min(STICHPROBE, len(o["pool"])), mit_gesamt=True)
    bdot_sha = sha256(bdot_pfad)
    return {
        "daten/denkmale_bdot.js": js("KIEZ_DENKMALE_BDOT", "Denkmale und Kamienice, Teil BDOT10k: Zählungen, Komplexe "
                                     "zabytkowo-historyczne, Gebäude mit Namen „Kamienica“. Quelle siehe Feld quelle. "
                                     "Erzeugt von skripte/dz_denkmale.py", d_bdot),
        "daten/denkmale.js": js("KIEZ_DENKMALE", (kopf_bsp if alle_fehlen else "") + "Denkmale und Kamienice, Teil "
                                "Register (Wikidata CC0, NID, Gminna ewidencja zabytków); Teilmenge, keine "
                                "Flächenaussage zu Baujahren. Erzeugt von skripte/dz_denkmale.py", d_reg),
        "daten/denkmale_odbl.js": js("KIEZ_DENKMALE_ODBL", (kopf_bsp if not pbfs else "") + "Denkmale aus "
                                     "OpenStreetMap (heritage, start_date). " + VERMERK_OSM + ". Erzeugt von "
                                     "skripte/dz_denkmale.py", d_osm),
        "belege/DZ_denkmale_lauf.md": beleg(z_bdot, z_reg, z_osm, reg["quellen"], stich, bdot_sha,
                                            d_osm["eingang"], d_bdot, o["ortsmarke_osm"] if pbfs else None, stich2,
                                            sicht),
        "belege/DZ_sichtpruefung_stichprobe.json": json.dumps(stich2, ensure_ascii=False, indent=1) + "\n",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pruefen", action="store_true", help="nur vergleichen, nichts schreiben")
    args = ap.parse_args()
    try:
        aus = rechnen()
    except FormatFehler as e:
        print(f"Eingang in fremdem Format, Leser anpassen (quellen-DZ.md): {e}", file=sys.stderr)
        return 3
    except AbruftagFehlt as e:
        print(f"Abruftag fehlt, Zeile in eingang/HERKUNFT.md ergänzen (quellen-DZ.md): {e}", file=sys.stderr)
        return 4
    except SichtFehler as e:
        print(f"{SICHT_EINGABE} passt nicht zur Stichprobe (pruefen/DZ_protokoll.md, Nachtrag 4): {e}", file=sys.stderr)
        return 5
    abw = 0
    for rel, text in aus.items():
        p = WURZEL / rel
        if args.pruefen:
            gleich = p.is_file() and p.read_text(encoding="utf-8") == text
            print(("  ok    " if gleich else "  FEHLT ") + f"{rel} gleich neu gerechnet ({len(text.encode())} B)")
            abw += not gleich
        else:
            p.write_text(text, encoding="utf-8")
            print(f"  geschrieben {rel} ({len(text.encode())} B)")
    return 1 if abw else 0


if __name__ == "__main__":
    sys.exit(main())
