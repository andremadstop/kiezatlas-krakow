"""Ortsmarke ul. Kościuszki 18: ein gemeinsamer Punkt für alle Datendateien (pruefen/N1_protokoll.md, Regel 3).

Gerufen von skripte/dz_denkmale.py (daten/denkmale_odbl.js) und skripte/36_sanierung.py (daten/sanierung_odbl.js),
damit beide Dateien dieselbe Koordinate tragen. Kein Netz, keine Datenbank.

Regel: aus dem OSM-Auszug in eingang/ alle Objekte mit addr:housenumber = 18 und „Kościuszki“ in addr:street, deren
Punkt in der Stadt liegt. Gewählt wird der flächengrößte Gebäudeumriss (geschlossener Weg mit building); Punkt =
representative_point() des Umrisses im Rechen-Koordinatensystem (ort_konfig.RECHEN_SRID), zurück nach WGS 84 mit
5 Nachkommastellen. Ohne Umriss: der Adressknoten. Liegen die Kandidaten weiter als STREUUNG_M auseinander, gibt
es keine Ortsmarke. Die OSM-Kennung geht nur in den Beleg, nicht in die Daten (KR31: keine Gebäudekennung in daten/).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from pyproj import CRS, Transformer
from shapely.geometry import Point, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402

STREUUNG_M = 25.0
SCHLUESSEL = "kosciuszki_18"


def _passt(t: dict) -> bool:
    return t.get("addr:housenumber") == "18" and "Kościuszki" in (t.get("addr:street") or "")


def kosciuszki_18(pbf: Path, rechteck: tuple[float, float, float, float],
                  in_stadt: Callable[[float, float], bool]) -> dict | None:
    """Punkt der Ortsmarke als {"lon", "lat", "osm", "art", "kandidaten"} oder None.

    rechteck: (west, süd, ost, nord) in WGS 84 für den Leser; in_stadt(lon, lat): Punkt in der Stadtgrenze.
    """
    import osm_pbf  # noqa: E402  (Leser des Pakets OSM und Fußwegnetz, nur gelesen)

    rechen = CRS.from_epsg(ort_konfig.RECHEN_SRID)
    hin = Transformer.from_crs(CRS.from_epsg(4326), rechen, always_xy=True)
    zurueck = Transformer.from_crs(rechen, CRS.from_epsg(4326), always_xy=True)
    erg = osm_pbf.lies(pbf, rechteck=rechteck, knoten_wahl=_passt, weg_wahl=_passt, relation_wahl=lambda t: False)
    kand = []   # (art, osm, punkt im Rechen-CRS, fläche)
    for oid, lon, lat, t in erg.getaggte_knoten:
        if in_stadt(lon, lat):
            kand.append(("knoten", f"n{oid}", Point(*hin.transform(lon, lat)), 0.0))
    for oid, t, ids in erg.wege:
        lon, lat, ok = erg.koordinaten(ids)
        if not ok.all() or len(ids) < 4 or ids[0] != ids[-1] or "building" not in t:
            continue
        xs, ys = hin.transform(lon, lat)
        poly = Polygon(list(zip(xs, ys)))
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty:
            continue
        p = poly.representative_point()
        if in_stadt(*zurueck.transform(p.x, p.y)):
            kand.append(("umriss", f"w{oid}", p, poly.area))
    if not kand:
        return None
    if max(a[2].distance(b[2]) for a in kand for b in kand) > STREUUNG_M:
        return None
    umrisse = [k for k in kand if k[0] == "umriss"]
    art, osm, p, _ = max(umrisse, key=lambda k: (k[3], k[1])) if umrisse else min(kand, key=lambda k: k[1])
    lon, lat = zurueck.transform(p.x, p.y)
    return {"lon": round(lon, 5), "lat": round(lat, 5), "osm": osm, "art": art, "kandidaten": len(kand)}
