"""Gemeinsame Werkzeuge der Kraków-Skripte für Versorgung und Takt (11_, 13_, 14_, 15_*_krakow.py).

Kein Netz, keine Datenbank. Enthält:
  - Pfade: $KIEZ_DATEN (Standard ../kiezatlas-daten/krakow), Eingangsordner für Handdownloads
  - einen kleinen Shapefile-Leser für Zip-Archive (Polygon, Punkt; DBF mit UTF-8) ohne GDAL, weil GDAL, pyshp und
    fiona auf der Workstation nicht vorhanden und nicht in requirements.txt sind
  - Umrechnung über pyproj: Quell-System aus der .prj-Datei, Ziel WGS 84 oder das Rechen-System aus
    config/<ort>.yaml (skripte/ort_konfig.py); keine EPSG-Nummer steht hier fest
  - Lesen und byte-gleiches Schreiben der Daten-Dateien daten/*.js (window.KIEZ_… = {…};) mit --pruefen
  - Gemeindegrenze Kraków aus BDOT10k OT_ADJA_A

Eigentümer: Paket Versorgung und Takt (Vorschlag in docs/entscheidungen/D6.md).
"""
from __future__ import annotations

import json
import os
import struct
import sys
import zipfile
from pathlib import Path

from pyproj import CRS, Transformer
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.validation import make_valid

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "daten"
WGS84 = CRS.from_epsg(4326)
RECHEN = CRS.from_epsg(ort_konfig.RECHEN_SRID)

# Gemeinde Kraków in BDOT10k OT_ADJA_A (TERYT-Kennung der Gemeinde)
GEMEINDE_TERYT = "1261011"


def kiez_daten() -> Path:
    return Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")


def eingang() -> Path:
    """Ablage der Handdownloads (Andre): $KIEZ_DATEN/eingang/."""
    return kiez_daten() / "eingang"


# ------------------------------------------------------------------------------------------- Shapefile im Zip
class Ebene:
    """Eine Shapefile-Ebene aus einem Zip: Datensätze (dict), Geometrien (shapely), Koordinatensystem (pyproj)."""

    def __init__(self, zip_pfad: Path, endung: str):
        self.zip_pfad = zip_pfad
        z = zipfile.ZipFile(zip_pfad)
        namen = {n.rsplit(".", 1)[0]: n for n in z.namelist() if n.lower().endswith(".shp")}
        basis = [b for b in namen if b.endswith(endung)]
        if len(basis) != 1:
            raise SystemExit(f"{zip_pfad}: Ebene *{endung} nicht eindeutig gefunden ({basis})")
        self.name = basis[0]
        self.crs = CRS.from_wkt(z.read(self.name + ".prj").decode("utf-8", "replace"))
        cpg = self.name + ".cpg"
        kod = z.read(cpg).decode().strip() if cpg in z.namelist() else "utf-8"
        self.kodierung = "utf-8" if kod.upper().replace("-", "") in ("UTF8", "65001") else kod
        self.saetze = _dbf(z.read(self.name + ".dbf"), self.kodierung)
        self.geometrien = _shp(z.read(self.name + ".shp"))
        if len(self.saetze) != len(self.geometrien):
            raise SystemExit(f"{self.name}: {len(self.saetze)} DBF-Sätze, aber {len(self.geometrien)} Geometrien")

    def __iter__(self):
        return iter(zip(self.saetze, self.geometrien))

    def nach(self, ziel: CRS) -> Transformer:
        return Transformer.from_crs(self.crs, ziel, always_xy=True)


def _dbf(b: bytes, kodierung: str) -> list[dict]:
    n, kopf, laenge = struct.unpack("<IHH", b[4:12])
    felder, p = [], 32
    while b[p] != 0x0D:
        name = b[p:p + 11].split(b"\0")[0].decode("ascii")
        felder.append((name, b[p + 16]))
        p += 32
    saetze = []
    for i in range(n):
        s = b[kopf + i * laenge: kopf + (i + 1) * laenge]
        if s[:1] == b"*":                      # gelöschter Satz
            saetze.append(None)
            continue
        o, d = 1, {}
        for name, fl in felder:
            d[name] = s[o:o + fl].decode(kodierung, "replace").strip()
            o += fl
        saetze.append(d)
    return saetze


def _ringe_zu_flaeche(ringe: list[list[tuple[float, float]]]):
    """Shapefile-Ringe (außen im Uhrzeigersinn, Löcher dagegen) zu Polygon/MultiPolygon."""
    def flaeche(r):
        return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:])) / 2
    aussen, loecher = [], []
    for r in ringe:
        if len(r) < 4:
            continue
        (aussen if flaeche(r) < 0 else loecher).append(r)
    if not aussen:                             # falsch orientierte Datei: alles als Außenring
        aussen, loecher = loecher, []
    polys = [[Polygon(a), []] for a in aussen]
    for h in loecher:
        hp = Polygon(h)
        for eintrag in polys:
            if eintrag[0].contains(hp.representative_point()):
                eintrag[1].append(h)
                break
    teile = [Polygon(a.exterior.coords, l) for a, l in polys]
    g = teile[0] if len(teile) == 1 else MultiPolygon(teile)
    return g if g.is_valid else make_valid(g)


def _shp(b: bytes) -> list:
    geoms, p = [], 100
    while p < len(b):
        _, laenge = struct.unpack(">II", b[p:p + 8])
        inhalt = b[p + 8: p + 8 + laenge * 2]
        p += 8 + laenge * 2
        typ = struct.unpack("<i", inhalt[:4])[0]
        if typ == 0:
            geoms.append(None)
        elif typ in (1, 11, 21):
            x, y = struct.unpack("<2d", inhalt[4:20])
            geoms.append(Point(x, y))
        elif typ in (5, 15, 25):
            n_teile, n_punkte = struct.unpack("<2i", inhalt[36:44])
            teile = list(struct.unpack(f"<{n_teile}i", inhalt[44:44 + 4 * n_teile])) + [n_punkte]
            o = 44 + 4 * n_teile
            pkt = struct.unpack(f"<{2 * n_punkte}d", inhalt[o:o + 16 * n_punkte])
            xy = list(zip(pkt[0::2], pkt[1::2]))
            geoms.append(_ringe_zu_flaeche([xy[teile[i]:teile[i + 1]] for i in range(n_teile)]))
        else:
            raise SystemExit(f"Shapefile-Typ {typ} wird nicht gelesen")
    return geoms


def transformiere(g, t: Transformer):
    from shapely.ops import transform
    return transform(t.transform, g)


def gemeinde_krakow(bdot_zip: Path):
    """(Fläche im Rechen-System, Fläche in WGS 84) der Gemeinde Kraków aus OT_ADJA_A."""
    e = Ebene(bdot_zip, "OT_ADJA_A")
    treffer = [g for s, g in e if s and s.get("RODZAJ") == "gmina" and s.get("IDTERYTJED") == GEMEINDE_TERYT]
    if len(treffer) != 1:
        raise SystemExit(f"OT_ADJA_A: Gemeinde {GEMEINDE_TERYT} {len(treffer)}-mal gefunden")
    return transformiere(treffer[0], e.nach(RECHEN)), transformiere(treffer[0], e.nach(WGS84))


# ------------------------------------------------------------------------------------------- Daten-Dateien
def js_lesen(pfad: Path) -> dict:
    t = pfad.read_text(encoding="utf-8")
    i = t.index("=", t.index("window.")) + 1
    return json.loads(t[i:].strip().rstrip(";"))


def js_text(global_name: str, inhalt: dict, kopf: str) -> str:
    return (f"/* {kopf} */\nwindow.{global_name}="
            + json.dumps(inhalt, ensure_ascii=False, separators=(",", ":")) + ";\n")


def ausgeben(pfad: Path, text: str, pruefen: bool) -> bool:
    """Schreibt text nach pfad oder vergleicht byte-genau (--pruefen). True = gleich bzw. geschrieben."""
    if pruefen:
        alt = pfad.read_text(encoding="utf-8") if pfad.exists() else None
        gleich = alt == text
        print(f"  {'ok    ' if gleich else 'FEHLT '}{pfad.relative_to(WURZEL)} {'aktuell' if gleich else 'weicht ab oder fehlt'}")
        return gleich
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(text, encoding="utf-8")
    print(f"  geschrieben: {pfad.relative_to(WURZEL)} ({len(text.encode())} Byte)")
    return True


def ist_beispiel(pfad: Path) -> bool:
    return pfad.exists() and js_lesen(pfad).get("fixture") is True


def tausender(n: int) -> str:
    """Ganzzahl mit Punkt als Tausendertrenner (deutsche Belege)."""
    return f"{n:,}".replace(",", ".")


# ------------------------------------------------------------------------------------------- Zellen und Abstände
def zellen_lesen() -> tuple[dict, list[dict]]:
    """(Inhalt von daten/zellen_odbl.js, Liste je Zelle mit id, st, ew, Mittelpunkt im Rechen-System, Fläche WGS 84)."""
    from shapely.geometry import shape
    inhalt = js_lesen(DATEN / "zellen_odbl.js")
    t = Transformer.from_crs(WGS84, RECHEN, always_xy=True)
    aus = []
    for f in inhalt["features"]:
        g = shape(f["geometry"])
        p = f["properties"]
        aus.append({"id": p["id"], "st": p.get("st"), "ew": p.get("ew"), "geom_w": g,
                    "geom_r": transformiere(g, t), "mitte_r": transformiere(g, t).centroid})
    return inhalt, aus


def punkte_rechen(features: list[dict]) -> list[Point]:
    """GeoJSON-Punkte (WGS 84) im Rechen-System."""
    t = Transformer.from_crs(WGS84, RECHEN, always_xy=True)
    return [Point(*t.transform(*f["geometry"]["coordinates"])) for f in features]


def naechste(ziele: list[Point], von: list[Point]) -> list[float | None]:
    """Luftlinie in m im Rechen-System von jedem Punkt in von zum nächsten Ziel; None ohne Ziel."""
    from shapely import STRtree
    if not ziele:
        return [None] * len(von)
    baum = STRtree(ziele)
    return [float(p.distance(ziele[baum.nearest(p)])) for p in von]


def ziele_je_art(einrichtungen: dict, haltestellen: dict, oepnv_klassen: list[str]) -> dict[str, list[Point]]:
    """art → Punkte im Rechen-System. Einrichtungen mit hinweis (strittige Lage) zählen nicht; dazu haltestelle_takt."""
    je: dict[str, list[dict]] = {}
    for f in einrichtungen["features"]:
        if f["properties"].get("hinweis"):
            continue
        je.setdefault(f["properties"]["art"], []).append(f)
    je["haltestelle_takt"] = [f for f in haltestellen["features"] if f["properties"]["taktklasse"] in oepnv_klassen]
    return {a: punkte_rechen(v) for a, v in sorted(je.items())}
