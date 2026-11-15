"""Grundkarte Kraków: eigene Vektorkacheln und Kartenschrift aus BDOT10k, dazu der Stil als daten/grundkarte.js.

Ersetzt den Potsdamer Auszug aus basemap.de (deckt nur Deutschland ab). Kein Netzabruf: liest die schon geladene
BDOT10k-Lieferung für Powiat 1261 (Miasto Kraków, GUGiK) und eine lokal installierte Schrift. Die GUGiK-Kartendienste
(WMTS/WMS) werden nicht angefasst, ihr Vorrendern gilt als „harvesting“ und ist untersagt.

Eingaben
  BDOT10k   $KIEZ_DATEN/eingang/bdot10k/1261_SHP.zip, sonst $KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip;
            nur mit der SHA256 in BDOT_SHA256 (sonst Abbruch). Herkunft: HERKUNFT.md neben der Datei.
  Schrift   Noto Sans Regular, Medium, Italic aus schriften/noto/ im Repository (SIL OFL 1.1, Lizenz daneben),
            byte-gleich mit dem Arch-Paket noto-fonts 1:2026.10.01-1; Prüfsummen in SCHRIFTEN;
            andere Dateien nur mit --schrift-ordner und passenden Prüfsummen (sonst Abbruch).
  Rahmen    karte.rahmen aus config/krakow.yaml (über skripte/ort_konfig.py).

Ausgaben (Ziel: --ziel, Standard $KIEZ_DATEN/abgeleitet/grundkarte/<SHA256-Anfang der Eingabe>/)
  kacheln/{z}/{x}/{y}.pbf      Mapbox Vector Tile 2.1, EPSG:3857, Ausdehnung 4096, unkomprimiert, z9 bis z14,
                               jede Kachel im Rahmen (auch leere, damit der Browser keine 404 sieht)
  schrift/<stapel>/<a>-<b>.pbf SDF-Glyphen im MapLibre-Format (Bereiche 0-255, 256-511, 8192-8447)
  schrift/OFL.txt              Copyright von Noto Sans und Wortlaut der SIL OFL 1.1 (geht mit den Glyphen mit)
  MANIFEST.sha256              SHA256 und Pfad jeder .pbf-Datei, sortiert (Gegenprobe byte-gleich: --pruefen)
  lauf.json                    Zählungen je Schritt für den Beleg
  daten/grundkarte.js          window.KIEZ_GRUNDKARTE (Stil, Quelle, Vermerk), im Repo; Pfade relativ zur Atlas-Wurzel

Kartenschichten (source-layer) und Attribute: siehe regeln() und SCHICHTEN. Nur die Attribute k (Klasse), nazwa
(Name), most; keine Gebäude (die Seiten zeichnen eigene), keine Adressen, keine Kennungen.

Aufruf (Python aus requirements.txt, siehe docs/rundgang.md):
  python -I skripte/27_grundkarte.py [--ziel DIR] [--schrift-ordner DIR]
  python -I skripte/27_grundkarte.py --pruefen [--ziel DIR]   rechnet neu in einen Zwischenordner und vergleicht
                                                              Manifest und daten/grundkarte.js (byte-gleich)
Lange Läufe: systemd-run --user --scope -p MemoryMax=8G uv run … python -I skripte/27_grundkarte.py
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import shutil
import struct
import sys
import tempfile
import time
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import shapely
from PIL import Image, ImageDraw, ImageFont
from pyproj import CRS, Transformer
from scipy.ndimage import distance_transform_edt
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402

KIEZ_DATEN = Path(os.environ.get("KIEZ_DATEN") or (WURZEL.parent / "kiezatlas-daten" / "krakow"))
BDOT_ORTE = [KIEZ_DATEN / "eingang" / "bdot10k" / "1261_SHP.zip",
             KIEZ_DATEN / "2026-11-13" / "03_gebaeude" / "1261_SHP.zip"]
BDOT_SHA256 = "68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d"
BDOT_PRAEFIX = "PL.PZGiK.283.BDOT10k.1261__OT_"
ZIEL_JS = WURZEL / "daten" / "grundkarte.js"

SCHRIFT_ORDNER = WURZEL / "schriften" / "noto"   # im Repository, damit die Kette nicht an einer Distribution hängt
SCHRIFTEN = {   # Schriftstapel -> (Datei, SHA256); Herkunft Paket noto-fonts 1:2026.10.01-1 (pacman -Qo), SIL OFL 1.1
    "Noto Sans Regular": ("NotoSans-Regular.ttf", "478c558ea716033cd60c03438f628dfa75694dcf6b5f6d505a2f05fd2b4f3823"),
    "Noto Sans Medium": ("NotoSans-Medium.ttf", "635d93d1131d791f2576de90b3bb0f7cdf61929906e8420a61b5f7f8e76420bb"),
    "Noto Sans Italic": ("NotoSans-Italic.ttf", "467e3f89eeca4108bb8710a2b9e0cf2281ac56d5b0609211a83776d0505eecb5"),
}
GLYPH_BEREICHE = [(0, 255), (256, 511), (8192, 8447)]

ZMIN, ZMAX = 9, 14
EXTENT = 4096
PUFFER = 64                      # Kachelpuffer in Kacheleinheiten (Linien und Flächen über den Rand)
UMFANG = 40075016.685578488      # Erdumfang in Web-Mercator-Metern (2 * pi * 6378137)
HALB = UMFANG / 2
ZIEL_CRS = "EPSG:3857"           # Web-Mercator, Kachelsystem von MapLibre

# Pfade der Kacheln und der Schrift auf dem Server, relativ zur Atlas-Wurzel (Seiten in Sprachordnern setzen ../
# davor; Vorschlag in docs/entscheidungen/D8.md)
PFAD_KACHELN = "daten/grundkarte/kacheln/{z}/{x}/{y}.pbf"
PFAD_SCHRIFT = "daten/grundkarte/schrift/{fontstack}/{range}.pbf"

# ---------------------------------------------------------------- Kartenschichten
DROGI_KLASSE = {   # KLASA_DROG -> (k, ab Zoom)
    "autostrada": ("autostrada", 9), "droga ekspresowa": ("ekspresowa", 9),
    "droga główna ruchu przyśpieszonego": ("gp", 9), "droga główna": ("glowna", 10),
    "droga zbiorcza": ("zbiorcza", 11), "droga lokalna": ("lokalna", 12),
    "droga dojazdowa": ("dojazdowa", 13), "droga wewnętrzna": ("wewnetrzna", 14),
}
TEREN_ZB = {"wielorodzinna": "wielorodzinna", "jednorodzinna": "jednorodzinna",
            "przemysłowo-składowa": "przemyslowa", "handlowo-usługowa": "uslugowa",
            "pozostała zabudowa": "pozostala"}


def regeln():
    """Liste (Kartenschicht, BDOT10k-Schicht, Regel(Attribute) -> (k, ab Zoom) oder None, Namensfeld)."""
    return [
        ("woda", "PTWP_A", lambda a: (("plynaca" if a["RODZAJ"] == "woda płynąca" else "stojaca"), ZMIN), None),
        ("zielen", "PTLZ_A", lambda a: ("las" if a["RODZAJ"] in ("las", "zagajnik") else "zadrzewienie", ZMIN), None),
        ("zielen", "PTRK_A", lambda a: ("krzewy", 11), None),
        ("zielen", "PTTR_A", lambda a: (("trawa", 11) if a["RODZAJ"] == "roślinność trawiasta" else ("pole", 11)), None),
        ("zielen", "PTUT_A", lambda a: ("uprawy_trwale", 11), None),
        ("teren", "PTZB_A", lambda a: (TEREN_ZB.get(a["RODZAJ"], "pozostala"), 11), None),
        ("teren", "PTKM_A", lambda a: ("komunikacja", 12), None),
        ("teren", "PTPL_A", lambda a: ("plac", 13), None),
        ("cieki", "SWRS_L", lambda a: (("rzeka", 11) if a["RODZAJ"] == "rzeka" else ("strumien", 13)), "NAZWA"),
        ("tory", "SKTR_L", lambda a: (("bocznica", 13) if a["FUNK_TORU"] == "bocznica" else ("tor", 11)), None),
        ("drogi", "SKJZ_L", lambda a: DROGI_KLASSE.get(a["KLASA_DROG"]) if a["KAT_ISTNIE"] == "eksploatowany" else None,
         "ULICA"),
        ("sciezki", "SKRP_L", lambda a: ("sciezka", 14), None),
        ("miejsca", "ADMS_P", lambda a: (("miasto", ZMIN) if a["RODZAJ"] == "miasto" else ("czesc", 12)), "NAZWA"),
    ]


SCHICHTEN = ["teren", "zielen", "woda", "cieki", "tory", "sciezki", "drogi", "miejsca"]   # Reihenfolge in der Kachel
NAMEN_AB = {"drogi": 13, "cieki": 12, "miejsca": ZMIN}   # Name in der Kachel erst ab dieser Zoomstufe


# ---------------------------------------------------------------- Shapefile und DBF lesen (ohne GDAL)
def dbf_lesen(b: bytes, kodierung: str) -> list[dict]:
    nrec, hl, rl = struct.unpack("<IHH", b[4:12])
    felder, o = [], 32
    while b[o] != 0x0D:
        felder.append((b[o:o + 11].split(b"\0")[0].decode("ascii"), b[o + 16]))
        o += 32
    zeilen = []
    for i in range(nrec):
        r = b[hl + i * rl: hl + (i + 1) * rl]
        p, d = 1, {}
        for name, laenge in felder:
            d[name] = r[p:p + laenge].decode(kodierung).strip()
            p += laenge
        zeilen.append(d)
    return zeilen


def ringe_zu_polygon(ringe: list[np.ndarray]):
    """Shapefile-Ringe: außen im Uhrzeigersinn, Löcher dagegen (Y nach oben). Löcher dem umgebenden Außenring zuordnen."""
    aussen, loecher = [], []
    for r in ringe:
        if len(r) < 4:
            continue
        x, y = r[:, 0], r[:, 1]
        flaeche = 0.5 * float(np.dot(x[:-1], y[1:]) - np.dot(x[1:], y[:-1]))
        (aussen if flaeche < 0 else loecher).append(r)
    if not aussen:          # falsch orientierte Lieferung: alle Ringe als Außenringe
        aussen, loecher = loecher, []
    if not aussen:
        return None
    teile = [[a, []] for a in aussen]
    huellen = [Polygon(a) for a in aussen]
    for h in loecher:
        pt = Point(h[0])
        for i, p in enumerate(huellen):
            if p.covers(pt):
                teile[i][1].append(h)
                break
    polys = [Polygon(a, lo) for a, lo in teile]
    g = polys[0] if len(polys) == 1 else MultiPolygon(polys)
    return g if g.is_valid else shapely.make_valid(g)


def shp_lesen(b: bytes) -> list:
    """Punkte (1, 11, 21), Linien (3, 13, 23), Flächen (5, 15, 25); Z und M werden verworfen."""
    geos, o = [], 100
    while o < len(b):
        _, laenge = struct.unpack(">ii", b[o:o + 8])
        inhalt = b[o + 8: o + 8 + laenge * 2]
        o += 8 + laenge * 2
        typ = struct.unpack("<i", inhalt[:4])[0]
        if typ == 0:
            geos.append(None)
        elif typ in (1, 11, 21):
            geos.append(Point(struct.unpack("<2d", inhalt[4:20])))
        elif typ in (3, 5, 13, 15, 23, 25):
            nparts, npts = struct.unpack("<2i", inhalt[36:44])
            parts = list(struct.unpack(f"<{nparts}i", inhalt[44:44 + 4 * nparts])) + [npts]
            xy = np.frombuffer(inhalt, dtype="<f8", count=2 * npts, offset=44 + 4 * nparts).reshape(-1, 2)
            stuecke = [xy[parts[i]:parts[i + 1]] for i in range(nparts)]
            if typ in (3, 13, 23):
                ls = [LineString(s) for s in stuecke if len(s) >= 2]
                geos.append(ls[0] if len(ls) == 1 else MultiLineString(ls) if ls else None)
            else:
                geos.append(ringe_zu_polygon(stuecke))
        else:
            raise SystemExit(f"Shapefile-Typ {typ} nicht unterstützt")
    return geos


class Bdot:
    def __init__(self, pfad: Path):
        self.zip = zipfile.ZipFile(pfad)
        self.namen = {n.removeprefix(BDOT_PRAEFIX)[:-4] for n in self.zip.namelist() if n.endswith(".shp")}
        self.crs = None
        self.dbf_datum: set[str] = set()

    def schicht(self, name: str):
        basis = BDOT_PRAEFIX + name
        crs = CRS.from_wkt(self.zip.read(basis + ".prj").decode("ascii"))
        if self.crs is None:
            self.crs = crs
        elif not crs.equals(self.crs):
            raise SystemExit(f"{name}: anderes Koordinatensystem als die übrigen Schichten (Regel G2)")
        kodierung = self.zip.read(basis + ".cpg").decode("ascii").strip()
        dbf = self.zip.read(basis + ".dbf")
        self.dbf_datum.add(f"{1900 + dbf[1]:04d}-{dbf[2]:02d}-{dbf[3]:02d}")
        zeilen = dbf_lesen(dbf, kodierung)
        geos = shp_lesen(self.zip.read(basis + ".shp"))
        if len(zeilen) != len(geos):
            raise SystemExit(f"{name}: {len(geos)} Geometrien, aber {len(zeilen)} DBF-Zeilen")
        return zeilen, geos


# ---------------------------------------------------------------- Kachelmathematik
def lonlat_zu_kachel(lon: float, lat: float, z: int) -> tuple[int, int]:
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)
    return min(max(x, 0), n - 1), min(max(y, 0), n - 1)


def kachel_grenzen(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    groesse = UMFANG / 2 ** z
    minx = -HALB + x * groesse
    maxy = HALB - y * groesse
    return minx, maxy - groesse, minx + groesse, maxy


def kacheln_im_rahmen(rahmen, z):
    x0, y0 = lonlat_zu_kachel(rahmen[0], rahmen[3], z)
    x1, y1 = lonlat_zu_kachel(rahmen[2], rahmen[1], z)
    return [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]


# ---------------------------------------------------------------- Protobuf (MVT 2.1 und MapLibre-Glyphen)
def varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def zz(n: int) -> int:
    return (n << 1) ^ (n >> 63)


def feld_varint(nr: int, wert: int) -> bytes:
    return varint(nr << 3) + varint(wert)


def feld_bytes(nr: int, daten: bytes) -> bytes:
    return varint((nr << 3) | 2) + varint(len(daten)) + daten


def gepackt(nr: int, werte: list[int]) -> bytes:
    return feld_bytes(nr, b"".join(varint(w) for w in werte))


def befehl(cmd: int, anzahl: int) -> int:
    return (cmd & 0x7) | (anzahl << 3)


def ring_flaeche(pts: list[tuple[int, int]]) -> int:
    """Doppelte Fläche nach der Gaußschen Trapezformel in Kachelkoordinaten (Y nach unten): > 0 = außen."""
    s = 0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return s


class Kodierer:
    """Geometrie in Kachelkoordinaten zu MVT-Befehlen (Zigzag, Delta)."""

    def __init__(self):
        self.cx = self.cy = 0
        self.befehle: list[int] = []

    def _punkte(self, pts):
        for x, y in pts:
            self.befehle += [zz(x - self.cx), zz(y - self.cy)]
            self.cx, self.cy = x, y

    def punkte(self, pts):
        self.befehle.append(befehl(1, len(pts)))
        self._punkte(pts)

    def linie(self, pts):
        self.befehle.append(befehl(1, 1))
        self._punkte(pts[:1])
        self.befehle.append(befehl(2, len(pts) - 1))
        self._punkte(pts[1:])

    def ring(self, pts):
        self.linie(pts)
        self.befehle.append(befehl(7, 1))


def quantisiere(koord: np.ndarray, grenzen) -> list[tuple[int, int]]:
    minx, miny, maxx, maxy = grenzen
    s = EXTENT / (maxx - minx)
    xs = np.rint((koord[:, 0] - minx) * s).astype(np.int64)
    ys = np.rint((maxy - koord[:, 1]) * s).astype(np.int64)
    pts, letzter = [], None
    for p in zip(xs.tolist(), ys.tolist()):
        if p != letzter:
            pts.append(p)
            letzter = p
    return pts


def kodiere_geometrie(g, grenzen) -> tuple[int, list[int]] | None:
    k = Kodierer()
    if g.geom_type in ("Point", "MultiPoint"):
        pts = []
        for p in getattr(g, "geoms", [g]):
            pts += quantisiere(np.array(p.coords), grenzen)
        if not pts:
            return None
        k.punkte(pts)
        return 1, k.befehle
    if g.geom_type in ("LineString", "MultiLineString"):
        for teil in getattr(g, "geoms", [g]):
            pts = quantisiere(np.array(teil.coords), grenzen)
            if len(pts) >= 2:
                k.linie(pts)
        return (2, k.befehle) if k.befehle else None
    if g.geom_type in ("Polygon", "MultiPolygon"):
        for p in getattr(g, "geoms", [g]):
            aussen = quantisiere(np.array(p.exterior.coords), grenzen)[:-1]
            if len(aussen) < 3 or ring_flaeche(aussen) == 0:
                continue
            if ring_flaeche(aussen) < 0:
                aussen.reverse()
            k.ring(aussen)
            for innen in p.interiors:
                pts = quantisiere(np.array(innen.coords), grenzen)[:-1]
                if len(pts) < 3 or ring_flaeche(pts) == 0:
                    continue
                if ring_flaeche(pts) > 0:
                    pts.reverse()
                k.ring(pts)
        return (3, k.befehle) if k.befehle else None
    return None


def kodiere_schicht(name: str, objekte: list[tuple[object, dict]], grenzen) -> bytes | None:
    schluessel: dict[str, int] = {}
    werte: dict[tuple, int] = {}
    features = []
    for g, attr in objekte:
        kod = kodiere_geometrie(g, grenzen)
        if kod is None:
            continue
        typ, befehle = kod
        tags = []
        for s in sorted(attr):
            v = (type(attr[s]).__name__, attr[s])
            schluessel.setdefault(s, len(schluessel))
            werte.setdefault(v, len(werte))
            tags += [schluessel[s], werte[v]]
        features.append(gepackt(2, tags) + feld_varint(3, typ) + gepackt(4, befehle))
    if not features:
        return None
    out = feld_varint(15, 2) + feld_bytes(1, name.encode("utf-8"))
    out += b"".join(feld_bytes(2, f) for f in features)
    out += b"".join(feld_bytes(3, s.encode("utf-8")) for s in schluessel)
    for typname, v in werte:
        if typname == "str":
            out += feld_bytes(4, feld_bytes(1, v.encode("utf-8")))
        elif typname == "bool":
            out += feld_bytes(4, feld_varint(7, int(v)))
        else:
            raise SystemExit(f"Attributtyp {typname} nicht vorgesehen")
    out += feld_varint(5, EXTENT)
    return feld_bytes(3, out)


# ---------------------------------------------------------------- Daten vorbereiten
def strassenname(a: dict) -> str:
    """ul. Floriańska -> „Floriańska“, pl. Matejki -> „pl. Matejki“ (Merkmal ul. weggelassen). Steht das Merkmal
    schon ausgeschrieben im Namen (al. + „Aleja Adama Mickiewicza“), wird es nicht noch einmal davorgesetzt."""
    name = " ".join(t for t in (a.get("ULI_NAZW_2", ""), a.get("ULI_NAZW_1", "")) if t)
    cecha = a.get("ULI_CECHA", "")
    doppelt = name.lower().startswith(cecha.rstrip(".").lower()) if cecha else False
    if name and cecha and cecha not in ("ul.", "inne") and not doppelt:
        name = f"{cecha} {name}"
    return name


def objekte_laden(bdot: Bdot, nach_3857: Transformer, zaehler: dict) -> dict[str, list]:
    """Rückgabe: Kartenschicht -> Liste (Geometrie in Web-Mercator, k, ab Zoom, nazwa, most)."""
    roh = defaultdict(list)
    for karte, quelle, regel, namefeld in regeln():
        if quelle not in bdot.namen:
            raise SystemExit(f"BDOT10k-Schicht {quelle} fehlt in der Lieferung")
        zeilen, geos = bdot.schicht(quelle)
        zaehler["gelesen"][quelle] = len(zeilen)
        n = 0
        for a, g in zip(zeilen, geos):
            if g is None or g.is_empty:
                continue
            r = regel(a)
            if r is None:
                continue
            k, ab = r
            nazwa = strassenname(a) if namefeld == "ULICA" else (a.get(namefeld, "") if namefeld else "")
            most = quelle == "SKJZ_L" and a.get("POLOZENIE", "").startswith("ponad")
            roh[karte].append((g, k, ab, nazwa, most))
            n += 1
        zaehler["uebernommen"][f"{karte} <- {quelle}"] = n
    for karte, liste in roh.items():
        geos = shapely.transform([o[0] for o in liste],
                                 lambda xy: np.column_stack(nach_3857.transform(xy[:, 0], xy[:, 1])))
        roh[karte] = [(g, *o[1:]) for g, o in zip(geos, liste)]
    # Linien gleicher Klasse und gleichen Namens verbinden (weniger Objekte, Beschriftung folgt der ganzen Straße)
    for karte in ("drogi", "cieki", "tory", "sciezki"):
        gruppen = defaultdict(list)
        for g, k, ab, nazwa, most in roh[karte]:
            gruppen[(k, ab, nazwa, most)].append(g)
        neu = []
        for schl in sorted(gruppen, key=lambda t: (t[0], t[2], t[3])):
            gs = gruppen[schl]
            m = shapely.line_merge(shapely.union_all(gs)) if len(gs) > 1 else gs[0]
            for teil in getattr(m, "geoms", [m]):
                if teil.geom_type == "LineString" and not teil.is_empty:
                    neu.append((teil, *schl))
        zaehler["verbunden"][karte] = {"vorher": len(roh[karte]), "nachher": len(neu)}
        roh[karte] = neu
    return roh


def zoom_auswahl(roh: dict[str, list], z: int, zaehler: dict) -> dict[str, tuple]:
    """Je Kartenschicht für Zoomstufe z: Geometrien vereinfacht (1 Kacheleinheit), zu kleine weggelassen."""
    einheit = UMFANG / 2 ** z / EXTENT           # Meter je Kacheleinheit
    aus = {}
    for karte in SCHICHTEN:
        geos, attr = [], []
        for g, k, ab, nazwa, most in roh.get(karte, []):
            if z < ab:
                continue
            if g.geom_type in ("Polygon", "MultiPolygon"):
                if g.area < (4 * einheit) ** 2:
                    continue
                g = shapely.simplify(g, einheit, preserve_topology=True)
            elif g.geom_type in ("LineString", "MultiLineString"):
                if g.length < 2 * einheit:
                    continue
                g = shapely.simplify(g, einheit, preserve_topology=False)
            if g.is_empty:
                continue
            a = {"k": k}
            if nazwa and z >= NAMEN_AB.get(karte, 99):
                a["nazwa"] = nazwa
            if most:
                a["most"] = True
            geos.append(g)
            attr.append(a)
        zaehler["je_zoom"].setdefault(str(z), {})[karte] = len(geos)
        aus[karte] = (geos, attr, shapely.STRtree(geos) if geos else None)
    return aus


def teile_nach_art(g) -> tuple[list, list]:
    flaechen, linien = [], []
    for t in getattr(g, "geoms", [g]):
        if t.geom_type in ("Polygon", "MultiPolygon"):
            flaechen.append(t)
        elif t.geom_type in ("LineString", "MultiLineString"):
            linien.append(t)
        elif t.geom_type == "GeometryCollection":
            f, li = teile_nach_art(t)
            flaechen += f
            linien += li
    return flaechen, linien


def kachel_bauen(auswahl: dict[str, tuple], grenzen) -> bytes:
    minx, miny, maxx, maxy = grenzen
    p = (maxx - minx) / EXTENT * PUFFER
    rahmen = shapely.box(minx - p, miny - p, maxx + p, maxy + p)
    innen = shapely.box(minx, miny, maxx, maxy)
    schichten = []
    for karte in SCHICHTEN:
        geos, attr, baum = auswahl[karte]
        if baum is None:
            continue
        idx = sorted(baum.query(rahmen, predicate="intersects").tolist())
        flaechen = defaultdict(list)
        objekte = []
        for i in idx:
            g = geos[i]
            if g.geom_type == "Point":
                if innen.covers(g):          # Punkte nur in ihrer eigenen Kachel (keine doppelten Namen)
                    objekte.append((g, attr[i]))
                continue
            c = shapely.clip_by_rect(g, minx - p, miny - p, maxx + p, maxy + p)
            if c.is_empty:
                continue
            f, li = teile_nach_art(c)
            if f:
                flaechen[tuple(sorted(attr[i].items()))].extend(f)
            for teil in li:
                objekte.append((teil, attr[i]))
        # Flächen gleicher Klasse in der Kachel verschmelzen (keine Nähte, weniger Objekte), unten im Stapel
        verschmolzen = []
        for schl in sorted(flaechen):
            u = shapely.union_all(flaechen[schl])
            u = u if u.is_valid else shapely.make_valid(u)
            polys = [t for t in teile_nach_art(u)[0] for t in getattr(t, "geoms", [t])]
            if polys:
                verschmolzen.append((MultiPolygon(polys) if len(polys) > 1 else polys[0], dict(schl)))
        kod = kodiere_schicht(karte, verschmolzen + objekte, grenzen)
        if kod:
            schichten.append(kod)
    return b"".join(schichten)


# ---------------------------------------------------------------- Kartenschrift (SDF-Glyphen wie MapLibre/fontnik)
SDF_GROESSE, SDF_PUFFER, SDF_RADIUS, SDF_SCHNITT, UEBERABTASTUNG = 24, 3, 8, 0.25, 4
EINFACH = ImageFont.Layout.BASIC   # Einzelzeichen ohne raqm/HarfBuzz: gleiches Ergebnis auf jedem Rechner


def glyph_sdf(font_hoch, cp: int, aufstieg: int, ersatz: bytes) -> bytes | None:
    """Ein Glyph als protobuf-Nachricht; None, wenn die Schrift das Zeichen nicht hat."""
    ch = chr(cp)
    s = UEBERABTASTUNG
    vorschub = int(round(font_hoch.getlength(ch) / s))
    x0, y0, x1, y1 = font_hoch.getbbox(ch, anchor="ls")
    if x1 <= x0 or y1 <= y0:          # Leerzeichen und Steuerzeichen: nur Vorschub
        if vorschub <= 0:
            return None
        return (feld_varint(1, cp) + feld_varint(3, 0) + feld_varint(4, 0) + feld_varint(5, zz(0))
                + feld_varint(6, zz(-aufstieg)) + feld_varint(7, vorschub))
    if bytes(font_hoch.getmask(ch)) == ersatz:
        return None
    links = math.floor(x0 / s)
    oben = math.ceil(-y0 / s)           # Pixel über der Grundlinie
    rechts = math.ceil(x1 / s)
    unten = math.ceil(y1 / s)
    b, h = rechts - links, oben + unten
    bb, hh = b + 2 * SDF_PUFFER, h + 2 * SDF_PUFFER
    bild = Image.new("L", (bb * s, hh * s), 0)
    ImageDraw.Draw(bild).text(((SDF_PUFFER - links) * s, (oben + SDF_PUFFER) * s), ch, font=font_hoch, fill=255,
                              anchor="ls")
    a = np.asarray(bild) > 127
    abstand = (distance_transform_edt(~a) - distance_transform_edt(a)) / s     # > 0 außerhalb, in Ausgabepixeln
    mitte = abstand[s // 2::s, s // 2::s][:hh, :bb]
    wert = np.clip(np.rint(255 - 255 * (mitte / SDF_RADIUS + SDF_SCHNITT)), 0, 255).astype(np.uint8)
    return (feld_varint(1, cp) + feld_bytes(2, wert.tobytes()) + feld_varint(3, b) + feld_varint(4, h)
            + feld_varint(5, zz(links)) + feld_varint(6, zz(oben - aufstieg)) + feld_varint(7, vorschub))


def schrift_bauen(ordner: Path, ziel: Path, zaehler: dict) -> None:
    for stapel, (datei, _) in SCHRIFTEN.items():
        pfad = ordner / datei
        zaehler["schrift"][stapel] = {"datei": datei, "sha256": sha256(pfad.read_bytes())}
        font_hoch = ImageFont.truetype(str(pfad), SDF_GROESSE * UEBERABTASTUNG, layout_engine=EINFACH)
        aufstieg = int(round(ImageFont.truetype(str(pfad), SDF_GROESSE, layout_engine=EINFACH).getmetrics()[0]))
        ersatz = bytes(font_hoch.getmask("\U0010FFFD"))
        for a, e in GLYPH_BEREICHE:
            glyphen = [g for g in (glyph_sdf(font_hoch, cp, aufstieg, ersatz) for cp in range(a, e + 1)) if g]
            rng = f"{a}-{e}"
            stack = (feld_bytes(1, stapel.encode()) + feld_bytes(2, rng.encode())
                     + b"".join(feld_bytes(3, g) for g in glyphen))
            d = ziel / "schrift" / stapel / f"{rng}.pbf"
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(feld_bytes(1, stack))
            zaehler["schrift"][stapel][rng] = len(glyphen)
    ofl_schreiben(ordner, ziel / "schrift" / "OFL.txt")


def font_copyright(pfad: Path) -> str:
    """Eintrag 0 (Copyright) der name-Tabelle, Windows-Plattform, Englisch (USA)."""
    b = pfad.read_bytes()
    for i in range(struct.unpack(">H", b[4:6])[0]):
        tag, _, off, _ = struct.unpack(">4sIII", b[12 + 16 * i: 28 + 16 * i])
        if tag == b"name":
            anzahl, start = struct.unpack(">2xHH", b[off:off + 6])
            for j in range(anzahl):
                pid, _, lid, nid, laenge, o = struct.unpack(">6H", b[off + 6 + 12 * j: off + 18 + 12 * j])
                if (pid, lid, nid) == (3, 0x409, 0):
                    return b[off + start + o: off + start + o + laenge].decode("utf-16-be")
    raise SystemExit(f"{pfad.name}: kein Copyright-Eintrag in der name-Tabelle")


def ofl_schreiben(ordner: Path, ziel: Path) -> None:
    """Die Glyphen sind aus Noto Sans abgeleitet (SIL OFL 1.1): Lizenztext und Copyright gehen mit. Den Wortlaut der
    Lizenz nimmt das Skript aus fonts/OFL.txt (Barlow, gleiche Lizenz), ab der Überschrift „SIL OPEN FONT LICENSE“.
    Einen Reserved Font Name nennt der Copyright-Eintrag von Noto Sans nicht."""
    zeilen = sorted({font_copyright(ordner / datei) for datei, _ in SCHRIFTEN.values()})
    ofl = (WURZEL / "fonts" / "OFL.txt").read_text(encoding="utf-8")
    i = ofl.index("-----------------------------------------------------------\nSIL OPEN FONT LICENSE Version 1.1")
    kopf = ("\n".join(zeilen) + "\n\n"
            "Signed-distance glyphs (MapLibre PBF) derived by skripte/27_grundkarte.py from Noto Sans Regular,\n"
            "Medium and Italic (" + ", ".join(d for d, _ in SCHRIFTEN.values()) + ").\n\n"
            "This Font Software is licensed under the SIL Open Font License, Version 1.1.\n"
            "This license is copied below, and is also available with a FAQ at:\n"
            "https://scripts.sil.org/OFL\n\n\n")
    ziel.write_text(kopf + ofl[i:], encoding="utf-8")


# ---------------------------------------------------------------- Stil (Potsdam-Look, DESIGN.md: Kartenpapier, kein Orange)
PAPIER, TINTE, NEBEN, LINIE = "#f1f2ee", "#13212a", "#4f5d64", "#cdd1cc"
WASSER, WASSER_TEXT = "#cddde1", "#3b7684"


def stil() -> tuple[list, list]:
    def zoom(*paare):
        return ["interpolate", ["exponential", 1.6], ["zoom"], *paare]

    def je_klasse(*stufen):
        """Breite je Zoomstufe und Klasse k. MapLibre erlaubt ["zoom"] nur im obersten interpolate, darum steht
        match in jeder Stufe und nicht umgekehrt. Stufe = (Zoom, {Klasse oder Klassenliste: Wert}, sonst)."""
        aus = []
        for z, werte, sonst in stufen:
            m = ["match", ["get", "k"]]
            for k, v in werte.items():
                m += [list(k) if isinstance(k, tuple) else k, v]
            aus += [z, m + [sonst]]
        return zoom(*aus)

    SCHNELL, HAUPT = ("autostrada", "ekspresowa", "gp"), ("glowna", "zbiorcza")

    unten = [
        {"id": "bm-teren", "type": "fill", "source": "bm", "source-layer": "teren", "minzoom": 11,
         "paint": {"fill-color": ["match", ["get", "k"], "przemyslowa", "#e4e5e1", "uslugowa", "#e6e6e2",
                                  ["komunikacja", "plac"], "#ebebe7", "#e8e9e4"],
                   "fill-opacity": zoom(11, 0.4, 14, 0.9)}},
        {"id": "bm-zielen", "type": "fill", "source": "bm", "source-layer": "zielen",
         "paint": {"fill-color": ["match", ["get", "k"], "las", "#d6e1d3", "zadrzewienie", "#dbe5d8",
                                  "krzewy", "#dfe7dc", "pole", "#eceee6", "#e2eadf"],
                   "fill-opacity": zoom(9, 0.7, 13, 1)}},
        {"id": "bm-woda", "type": "fill", "source": "bm", "source-layer": "woda", "paint": {"fill-color": WASSER}},
        {"id": "bm-cieki", "type": "line", "source": "bm", "source-layer": "cieki",
         "layout": {"line-cap": "round", "line-join": "round"},
         "paint": {"line-color": WASSER,
                   "line-width": je_klasse((11, {"rzeka": 1}, 0.4), (13, {"rzeka": 1.6}, 0.6),
                                           (16, {"rzeka": 3}, 1.5))}},
        {"id": "bm-sciezki", "type": "line", "source": "bm", "source-layer": "sciezki", "minzoom": 14,
         "paint": {"line-color": LINIE, "line-width": 0.8, "line-dasharray": [2, 1.5]}},
        {"id": "bm-tory", "type": "line", "source": "bm", "source-layer": "tory",
         "paint": {"line-color": "#b4babc",
                   "line-width": je_klasse((11, {"bocznica": 0.6}, 0.7), (16, {"bocznica": 0.6}, 1.6))}},
        {"id": "bm-drogi-obrys", "type": "line", "source": "bm", "source-layer": "drogi", "minzoom": 12,
         "filter": ["!=", ["get", "k"], "wewnetrzna"],
         "layout": {"line-cap": "round", "line-join": "round"},
         "paint": {"line-color": LINIE,
                   "line-width": je_klasse((12, {SCHNELL: 3.5, HAUPT: 2.8}, 1.6),
                                           (16, {SCHNELL: 12, HAUPT: 10}, 7))}},
        {"id": "bm-drogi", "type": "line", "source": "bm", "source-layer": "drogi",
         "layout": {"line-cap": "round", "line-join": "round"},
         "paint": {"line-color": ["step", ["zoom"], "#d9dcd7", 12, "#ffffff"],
                   "line-width": je_klasse((9, {SCHNELL: 0.8, HAUPT: 0.6, "wewnetrzna": 0.3}, 0.4),
                                           (12, {SCHNELL: 2.2, HAUPT: 1.6, "wewnetrzna": 0.4}, 0.6),
                                           (14, {SCHNELL: 4.4, HAUPT: 3.4, "wewnetrzna": 0.6}, 2),
                                           (16, {SCHNELL: 10, HAUPT: 8, "wewnetrzna": 2.5}, 5.5))}},
    ]
    halo = {"text-halo-color": PAPIER, "text-halo-width": 1.4, "text-halo-blur": 0.4}
    oben = [
        {"id": "bm-cieki-nazwy", "type": "symbol", "source": "bm", "source-layer": "cieki", "minzoom": 12,
         "filter": ["has", "nazwa"],
         "layout": {"symbol-placement": "line", "text-field": ["get", "nazwa"], "text-font": ["Noto Sans Italic"],
                    "text-size": 11, "symbol-spacing": 400, "text-letter-spacing": 0.05},
         "paint": {"text-color": WASSER_TEXT, **halo}},
        {"id": "bm-drogi-nazwy", "type": "symbol", "source": "bm", "source-layer": "drogi", "minzoom": 13,
         "filter": ["has", "nazwa"],
         "layout": {"symbol-placement": "line", "text-field": ["get", "nazwa"], "text-font": ["Noto Sans Regular"],
                    "text-size": zoom(13, 10, 17, 13), "symbol-spacing": 300, "text-max-angle": 30},
         "paint": {"text-color": NEBEN, **halo}},
        {"id": "bm-miejsca", "type": "symbol", "source": "bm", "source-layer": "miejsca", "minzoom": 12,
         "filter": ["==", ["get", "k"], "czesc"],
         "layout": {"text-field": ["get", "nazwa"], "text-font": ["Noto Sans Medium"],
                    "text-size": zoom(12, 11, 16, 14), "text-letter-spacing": 0.04, "text-padding": 6},
         "paint": {"text-color": TINTE, "text-opacity": 0.75, **halo}},
    ]
    return unten, oben


# ---------------------------------------------------------------- Hilfen
def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def manifest(ziel: Path) -> str:
    return "".join(f"{sha256(p.read_bytes())}  {p.relative_to(ziel).as_posix()}\n" for p in sorted(ziel.rglob("*.pbf")))


def bdot_finden() -> Path:
    for p in BDOT_ORTE:
        if p.exists():
            h = sha256(p.read_bytes())
            if h != BDOT_SHA256:
                raise SystemExit(f"{p}: SHA256 {h} statt {BDOT_SHA256} (Regel G1). Neuer Stand: docs/rundgang.md, "
                                 "„Neuer Datenstand“; BDOT_SHA256 erst nach Prüfung ändern.")
            return p
    raise SystemExit("BDOT10k 1261 nicht gefunden: " + ", ".join(str(p) for p in BDOT_ORTE))


def vermerk(stand: str) -> str:
    # art. 40c ust. 3 Prawo geodezyjne i kartograficzne verlangt die Angabe der Quelle, schreibt aber keinen Wortlaut vor
    return ('Podkład: <a href="https://www.geoportal.gov.pl/pl/dane/baza-danych-obiektow-topograficznych-bdot10k/">'
            f"BDOT10k</a>, Główny Urząd Geodezji i Kartografii (stan plików {stand}), opracowanie własne")


def js_schreiben(stand: str, rahmen, ziel_js: Path) -> None:
    unten, oben = stil()
    v = vermerk(stand)
    inhalt = {
        "stand": f"BDOT10k 1261 (Miasto Kraków), pliki z {stand}",
        "quelle": {"type": "vector", "tiles": [PFAD_KACHELN], "minzoom": ZMIN, "maxzoom": ZMAX,
                   "bounds": rahmen, "attribution": v},
        "glyphs": PFAD_SCHRIFT,
        "unten": unten,
        "oben": oben,
        "vermerk": v,
    }
    text = json.dumps(inhalt, ensure_ascii=False, separators=(",", ":"))
    kopf = ("/* Grundkarte Kraków: Stil der eigenen Vektorkacheln (skripte/27_grundkarte.py), nicht von Hand ändern.\n"
            "   Quelle der Kacheln: BDOT10k, Główny Urząd Geodezji i Kartografii; Pfade relativ zur Atlas-Wurzel. */\n")
    ziel_js.write_text(kopf + f"window.KIEZ_GRUNDKARTE={text};\n", encoding="utf-8")


# ---------------------------------------------------------------- Lauf
def bauen(ziel: Path, schrift_ordner: Path, ziel_js: Path | None) -> dict:
    t0 = time.time()
    zaehler = {"gelesen": {}, "uebernommen": {}, "verbunden": {}, "je_zoom": {}, "kacheln": {}, "schrift": {}}
    rahmen = ort_konfig.lade()["karte"]["rahmen"]
    for datei, soll in SCHRIFTEN.values():
        if not (schrift_ordner / datei).exists():
            raise SystemExit(f"Schrift fehlt: {schrift_ordner / datei}")
        ist = sha256((schrift_ordner / datei).read_bytes())
        if ist != soll:
            raise SystemExit(f"{datei}: SHA256 {ist}, erwartet {soll} (andere Schriftdatei)")
    pfad = bdot_finden()
    zaehler["eingabe"] = {"datei": pfad.name, "sha256": BDOT_SHA256}
    bdot = Bdot(pfad)
    bdot.schicht("ADMS_P")       # liest die erste .prj; jede weitere Schicht wird dagegen geprüft (Regel G2)
    nach_3857 = Transformer.from_crs(bdot.crs, CRS.from_user_input(ZIEL_CRS), always_xy=True)
    zaehler["crs_quelle"] = bdot.crs.name
    roh = objekte_laden(bdot, nach_3857, zaehler)
    stand = max(bdot.dbf_datum)
    zaehler["dbf_datum"] = sorted(bdot.dbf_datum)
    shutil.rmtree(ziel / "kacheln", ignore_errors=True)
    shutil.rmtree(ziel / "schrift", ignore_errors=True)
    for z in range(ZMIN, ZMAX + 1):
        auswahl = zoom_auswahl(roh, z, zaehler)
        groessen, leer = [], 0
        for x, y in kacheln_im_rahmen(rahmen, z):
            daten = kachel_bauen(auswahl, kachel_grenzen(z, x, y))
            d = ziel / "kacheln" / str(z) / str(x) / f"{y}.pbf"
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(daten)
            groessen.append(len(daten))
            leer += not daten
        zaehler["kacheln"][str(z)] = {"anzahl": len(groessen), "leer": leer, "bytes": sum(groessen),
                                      "groesste": max(groessen)}
        print(f"z{z}: {len(groessen)} Kacheln, {sum(groessen)} B, größte {max(groessen)} B", file=sys.stderr)
    schrift_bauen(schrift_ordner, ziel, zaehler)
    (ziel / "MANIFEST.sha256").write_text(manifest(ziel), encoding="utf-8")
    zaehler["manifest_sha256"] = sha256((ziel / "MANIFEST.sha256").read_bytes())
    alle = sorted(ziel.rglob("*.pbf"))
    zaehler["gesamt"] = {"dateien": len(alle), "bytes": sum(p.stat().st_size for p in alle),
                         "gzip_bytes": sum(len(gzip.compress(p.read_bytes(), 6, mtime=0)) for p in alle)}
    zaehler["stand"] = stand
    zaehler["sekunden"] = round(time.time() - t0, 1)
    (ziel / "lauf.json").write_text(json.dumps(zaehler, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if ziel_js:
        js_schreiben(stand, rahmen, ziel_js)
    return zaehler


def standard_ziel() -> Path:
    return KIEZ_DATEN / "abgeleitet" / "grundkarte" / BDOT_SHA256[:12]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ziel", type=Path, default=None)
    ap.add_argument("--schrift-ordner", type=Path, default=SCHRIFT_ORDNER)
    ap.add_argument("--pruefen", action="store_true", help="neu rechnen und Manifest vergleichen (byte-gleich)")
    arg = ap.parse_args()
    ziel = (arg.ziel or standard_ziel()).resolve()
    if arg.pruefen:
        alt = ziel / "MANIFEST.sha256"
        if not alt.exists():
            print(f"kein Manifest unter {ziel}: erst ohne --pruefen laufen lassen", file=sys.stderr)
            return 1
        with tempfile.TemporaryDirectory(prefix="grundkarte-") as tmp:
            z = bauen(Path(tmp), arg.schrift_ordner, None)
            neu = (Path(tmp) / "MANIFEST.sha256").read_text(encoding="utf-8")
            gleich = neu == alt.read_text(encoding="utf-8")
            js_tmp = Path(tmp) / "grundkarte.js"
            js_schreiben(z["stand"], ort_konfig.lade()["karte"]["rahmen"], js_tmp)
            js_gleich = ZIEL_JS.exists() and js_tmp.read_text(encoding="utf-8") == ZIEL_JS.read_text(encoding="utf-8")
        print(("ok    " if gleich else "FEHLT ") + f"Kacheln und Schrift byte-gleich ({len(neu.splitlines())} Dateien)")
        print(("ok    " if js_gleich else "FEHLT ") + "daten/grundkarte.js gleich")
        return 0 if gleich and js_gleich else 1
    ziel.mkdir(parents=True, exist_ok=True)
    z = bauen(ziel, arg.schrift_ordner, ZIEL_JS)
    print(f"geschrieben: {ziel} ({z['gesamt']['dateien']} Dateien, {z['gesamt']['bytes']} B, gzip "
          f"{z['gesamt']['gzip_bytes']} B) und {ZIEL_JS.relative_to(WURZEL)}; {z['sekunden']} s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
