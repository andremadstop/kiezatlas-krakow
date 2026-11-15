"""Vereinfachte Stadtteilgrenzen für die Übersicht der Startseite (pruefen/N1_protokoll.md, Regel 5).

Liest daten/stadtteile_odbl.js (Kartengeometrie der dzielnice, skripte/02_bevoelkerung.py) und schreibt
daten/stadtteile_uebersicht_odbl.js (window.KIEZ_STADTTEILE, Vertrag daten/schema/stadtteile_uebersicht_odbl.json)
und den Beleg belege/N1_stadtteile_uebersicht.md. Kein Netz, keine Datenbank, keine Rohdaten.

Verfahren: shapely.coverage_simplify (gemeinsame Kanten werden gemeinsam vereinfacht, die Abdeckung bleibt ohne
Lücken und Überlappungen) im Rechen-Koordinatensystem (ort_konfig.RECHEN_SRID), Toleranz TOLERANZ_M, danach WGS 84
mit 5 Nachkommastellen. Eigenschaften der Features unverändert. Abnahme nach dem Runden (bricht sonst ab): jede
Geometrie gültig, Abdeckung gültig (coverage_is_valid), Vereinigung gleich der Vereinigung der genauen Grenzen bis
auf Rundung, Flächenabweichung je dzielnica höchstens MAX_FLAECHE_PROZ, Hausdorff-Abstand höchstens MAX_HAUSDORFF_M,
gleiche Zahl an Teilflächen.

Nur die Startseite lädt die Datei; Karte und Steckbrief laden die genauen Grenzen (daten/stadtteile_odbl.js).

Aufruf: python -I skripte/02a_stadtteile_uebersicht.py [--pruefen]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

import shapely
from pyproj import CRS, Transformer
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import unary_union
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "daten" / "stadtteile_odbl.js"
AUS = WURZEL / "daten" / "stadtteile_uebersicht_odbl.js"
BELEG = WURZEL / "belege" / "N1_stadtteile_uebersicht.md"
TOLERANZ_M = 10.0   # Nachtrag 1 zu Regel 5 (pruefen/N1_protokoll.md): 20 m verfehlte die Hausdorff-Grenze
STELLEN = 5
MAX_FLAECHE_PROZ = 1.0
MAX_HAUSDORFF_M = 40.0
KOPF = ("/* Vereinfachte Grenzen der dzielnice Krakaus für die Übersicht der Startseite, erzeugt von "
        "skripte/02a_stadtteile_uebersicht.py aus daten/stadtteile_odbl.js. © OpenStreetMap-Mitwirkende, Open Database "
        "License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/). ODbL */\n")


class Abbruch(Exception):
    pass


def js_lesen(p: Path) -> dict:
    t = p.read_text(encoding="utf-8")
    m = re.search(r"window\.[A-Za-z0-9_]+\s*=\s*", t)
    return json.loads(t[m.end():].rstrip().rstrip(";"))


def runden(g) -> dict:
    def ring(r):
        return [[round(x, STELLEN), round(y, STELLEN)] for x, y in r.coords]

    def poly(p: Polygon):
        return [ring(p.exterior), *[ring(i) for i in p.interiors]]
    if isinstance(g, Polygon):
        return {"type": "Polygon", "coordinates": poly(g)}
    if isinstance(g, MultiPolygon):
        return {"type": "MultiPolygon", "coordinates": [poly(p) for p in g.geoms]}
    raise Abbruch(f"Geometrietyp {g.geom_type} nicht erwartet")


def transform(tr: Transformer, g):
    return shapely.transform(g, lambda c: np.column_stack(tr.transform(c[:, 0], c[:, 1])))


def dez(x: float, f: str) -> str:
    return format(x, f).replace(".", ",")


def teile(g) -> int:
    return len(g.geoms) if isinstance(g, MultiPolygon) else 1


def punkte(g) -> int:
    return int(shapely.get_num_coordinates(g))


def rechnen() -> tuple[str, str]:
    st = js_lesen(QUELLE)
    rechen = CRS.from_epsg(ort_konfig.RECHEN_SRID)
    hin = Transformer.from_crs(CRS.from_epsg(4326), rechen, always_xy=True)
    zurueck = Transformer.from_crs(rechen, CRS.from_epsg(4326), always_xy=True)
    genau_w = [shape(f["geometry"]) for f in st["features"]]
    genau = [transform(hin, g) for g in genau_w]
    if not all(g.is_valid for g in genau) or not shapely.coverage_is_valid(genau):
        raise Abbruch("Eingabe daten/stadtteile_odbl.js ist keine gültige Abdeckung")
    einfach = shapely.coverage_simplify(genau, TOLERANZ_M)
    feats, zeilen = [], []
    gerundet_r = []
    for f, g0, g1 in zip(st["features"], genau, einfach):
        geo = runden(transform(zurueck, g1))
        g2 = transform(hin, shape(geo))          # nach dem Runden noch einmal im Rechen-System prüfen
        gerundet_r.append(g2)
        nr = f["properties"]["nr"]
        if not g2.is_valid:
            raise Abbruch(f"{nr}: Geometrie nach dem Runden ungültig")
        abw = (g2.area - g0.area) / g0.area * 100
        hd = g0.hausdorff_distance(g2)
        if abs(abw) > MAX_FLAECHE_PROZ or hd > MAX_HAUSDORFF_M or teile(g2) != teile(g0):
            raise Abbruch(f"{nr}: Fläche {abw:+.3f} %, Hausdorff {hd:.1f} m, Teile {teile(g0)} -> {teile(g2)}")
        feats.append({"type": "Feature", "geometry": geo, "properties": f["properties"]})
        zeilen.append((nr, f["properties"]["name"], punkte(g0), punkte(g2), abw, hd))
    if not shapely.coverage_is_valid(gerundet_r):
        raise Abbruch("Abdeckung nach dem Runden ungültig (Überlappung oder ungleiche gemeinsame Kanten)")
    u0, u2 = unary_union(genau), unary_union(gerundet_r)
    sym = u0.symmetric_difference(u2).area / u0.area * 100
    loecher0 = sum(len(p.interiors) for p in (u0.geoms if isinstance(u0, MultiPolygon) else [u0]))
    loecher2 = sum(len(p.interiors) for p in (u2.geoms if isinstance(u2, MultiPolygon) else [u2]))
    if loecher2 != loecher0:
        raise Abbruch(f"Löcher in der Vereinigung: {loecher0} -> {loecher2} (Lücke zwischen dzielnice?)")
    if sym > MAX_FLAECHE_PROZ:
        raise Abbruch(f"Vereinigung weicht um {sym:.3f} % der Stadtfläche ab")
    inhalt = {k: v for k, v in st.items() if k != "features"}
    inhalt["vereinfachung"] = {"verfahren": "coverage_simplify", "toleranz_m": TOLERANZ_M,
                               "srid": ort_konfig.RECHEN_SRID, "stellen": STELLEN,
                               "quelle": "stadtteile_odbl.js",
                               "quelle_sha256": hashlib.sha256(QUELLE.read_bytes()).hexdigest()}
    inhalt["features"] = feats
    js = KOPF + "window.KIEZ_STADTTEILE=" + json.dumps(inhalt, ensure_ascii=False, separators=(",", ":")) + ";\n"

    gz0 = len(gzip.compress(QUELLE.read_bytes(), 9, mtime=0))
    gz1 = len(gzip.compress(js.encode("utf-8"), 9, mtime=0))
    T = lambda x: f"{x:,}".replace(",", ".")  # noqa: E731
    b = ["# Vereinfachte Stadtteilgrenzen für die Übersicht (erzeugt)", "",
         "Erzeugt von `skripte/02a_stadtteile_uebersicht.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). "
         "Regeln vor dem Lauf: `pruefen/N1_protokoll.md`, Regel 5.", "",
         f"- Eingabe: `daten/stadtteile_odbl.js`, SHA256 `{inhalt['vereinfachung']['quelle_sha256']}`, "
         f"{T(QUELLE.stat().st_size)} B, gzip -9 (Python, ohne Dateiname) {T(gz0)} B",
         f"- Ausgabe: `daten/stadtteile_uebersicht_odbl.js`, {T(len(js.encode('utf-8')))} B, gzip -9 (Python, ohne "
         f"Dateiname) {T(gz1)} B",
         f"- Verfahren: `shapely.coverage_simplify` {shapely.__version__} (GEOS {'.'.join(map(str, shapely.geos_version))}) "
         f"in EPSG:{ort_konfig.RECHEN_SRID}, Toleranz {TOLERANZ_M:g} m, Koordinaten auf {STELLEN} Nachkommastellen",
         "- Abnahme nach dem Runden: alle Geometrien gültig, Abdeckung gültig (`coverage_is_valid`), Löcher der "
         f"Vereinigung {loecher0} wie vorher, symmetrische Differenz der Vereinigungen {dez(sym, '.3f')} % der "
         f"Stadtfläche (Grenze {dez(MAX_FLAECHE_PROZ, 'g')} %)",
         "", "| dzielnica | Name | Punkte vorher | Punkte nachher | Fläche | Hausdorff |", "|---|---|---|---|---|---|"]
    for nr, name, p0, p2, abw, hd in zeilen:
        b.append(f"| {nr} | {name} | {T(p0)} | {T(p2)} | {dez(abw, '+.3f')} % | {dez(hd, '.1f')} m |")
    b += ["", f"Grenzen je dzielnica: Fläche höchstens ±{dez(MAX_FLAECHE_PROZ, 'g')} %, Hausdorff höchstens "
          f"{dez(MAX_HAUSDORFF_M, 'g')} m, gleiche Zahl an Teilflächen.", ""]
    return js, "\n".join(b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pruefen", action="store_true", help="neu rechnen und byte-genau vergleichen, nichts schreiben")
    a = ap.parse_args()
    try:
        js, beleg = rechnen()
    except Abbruch as e:
        print(f"Abbruch: {e}")
        return 1
    ok = True
    for p, t in ((AUS, js), (BELEG, beleg)):
        if a.pruefen:
            gleich = p.exists() and p.read_text(encoding="utf-8") == t
            print(("  ok    " if gleich else "  FEHLT ") + f"{p.relative_to(WURZEL)} byte-gleich neu erzeugt")
            ok = ok and gleich
        else:
            p.write_text(t, encoding="utf-8")
            print(f"  geschrieben: {p.relative_to(WURZEL)} ({len(t.encode('utf-8'))} Byte)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
