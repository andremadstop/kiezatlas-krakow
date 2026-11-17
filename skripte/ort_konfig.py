"""Ortskonfiguration für Skripte: liest config/<ort>.yaml und stellt das Rechen-Koordinatensystem bereit.

Welche Datei gilt: $KIEZ_CONFIG (Pfad), sonst die einzige Ortskonfiguration unter config/, sonst config/krakow.yaml. Für die Gegenprobe Potsdam zeigt
KIEZ_CONFIG auf pruefen/gegenprobe_potsdam/ort.yaml.

  RECHEN_SRID   EPSG-Code, in dem Abstände und Flächen gerechnet werden (Schlüssel rechen_srid)
  RICHTWERTE    Pfad der Richtwerte (Schlüssel richtwerte, relativ zur Ortskonfiguration; Standard
                richtwerte.yaml daneben). Die Gegenprobe Potsdam liest so die Potsdamer Richtwerte.
  SRS_NAMEN     lesbare Namen der zugelassenen Systeme (wie im EPSG-Register geführt)
  srs_name()    Name und Code, z. B. für Berichte und GeoPackage-Metadaten
  proj4()       PROJ-Zeichenkette und Projektionskürzel, aus pyproj berechnet (nicht von Hand getippt)

Kein Netz, keine Datenbank.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

WURZEL = Path(__file__).resolve().parent.parent

SRS_NAMEN = {
    2178: "ETRS89 / Poland CS2000 zone 7",
    2180: "ETRS89 / Poland CS92",
    25832: "ETRS89 / UTM zone 32N",
    25833: "ETRS89 / UTM zone 33N",
    25834: "ETRS89 / UTM zone 34N",
}


def pfad() -> Path:
    """$KIEZ_CONFIG, sonst die einzige Ortskonfiguration unter config/ (ohne richtwerte.yaml), sonst config/krakow.yaml."""
    p = os.environ.get("KIEZ_CONFIG")
    if p:
        return Path(p).resolve()
    orte = sorted(x for x in (WURZEL / "config").glob("*.yaml") if x.name != "richtwerte.yaml")
    return orte[0] if len(orte) == 1 else WURZEL / "config" / "krakow.yaml"


@lru_cache(maxsize=None)
def lade() -> dict:
    with pfad().open(encoding="utf-8") as f:
        k = yaml.safe_load(f)
    srid = k.get("rechen_srid")
    if not isinstance(srid, int) or srid not in SRS_NAMEN:
        raise SystemExit(f"{pfad()}: rechen_srid fehlt oder ist unbekannt ({srid!r}); zugelassen: {sorted(SRS_NAMEN)}")
    return k


def srs_name(srid: int | None = None) -> str:
    s = RECHEN_SRID if srid is None else srid
    return f"{SRS_NAMEN[s]} (EPSG:{s})"


def proj4(srid: int | None = None) -> tuple[str, str]:
    """(PROJ-Zeichenkette, Projektionskürzel wie „utm“ oder „tmerc“) für die QGIS-Projektdatei."""
    from pyproj import CRS
    c = CRS.from_epsg(RECHEN_SRID if srid is None else srid)
    return c.to_proj4(), c.to_dict().get("proj", "")


def richtwerte_pfad() -> Path:
    p = Path(lade().get("richtwerte", "richtwerte.yaml"))
    return p if p.is_absolute() else (pfad().parent / p).resolve()


RECHEN_SRID: int = lade()["rechen_srid"]
RICHTWERTE: Path = richtwerte_pfad()
