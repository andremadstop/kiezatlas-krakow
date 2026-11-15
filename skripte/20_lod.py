"""Höhen je Gebäude aus den GUGiK-Modellen 3D budynków (LoD1 2024, LoD2 Stand 2017), Handdownload.

Liest CityGML 2.0 (einzelne .gml/.xml oder .zip mit solchen Dateien) aus $KIEZ_DATEN/eingang/ und liefert je
Gebäude die Kennung des BDOT10k-Objekts und eine Höhe in Metern:

  LoD1 2024  bldg:measuredHeight („przybliżona wysokość“, Geoportal, Seite „Modele 3D budynków“)
  LoD2       keine measuredHeight dokumentiert: Höhe = höchster minus tiefster z-Wert der Gebäudegeometrie
             (First über dem tiefsten Geländepunkt), als eigene Herkunft gekennzeichnet

Verknüpfung mit BDOT10k über das Attribut buildingId („identyfikator obiektu BDOT10k (buildingId)“, ebd.), das als
gen:stringAttribute name="buildingId" oder als Element buildingId vorliegen kann; Version (wersjaId) wird mitgelesen.
Eine räumliche Verknüpfung gibt es nicht: Gebäude ohne passende Kennung bekommen im Gebäudeleser die Höhe aus den
Geschossen (skripte/20_bdot10k.py, Herkunft „geschosse“).

Erwartete Dateinamen (quellen-D5.md): eingang/lod1_2024_1261*.zip|.gml|.xml, eingang/lod2_1261*.zip|.gml|.xml.

Aufruf:  python -I skripte/20_lod.py [--eingang DIR]      Zählung je Datei auf stdout, Rückgabe 0
Als Modul: hoehen_lesen(pfade) -> (dict buildingId -> (hoehe_m, version), zaehlung)
Kein Netz, keine Datenbank, nur Standardbibliothek.
"""
from __future__ import annotations

import argparse
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
KENNUNG_NAMEN = {"buildingId", "buildingid", "idBudynku"}
VERSION_NAMEN = {"wersjaId", "wersjaid"}


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN", WURZEL.parent / "kiezatlas-daten" / "krakow")).resolve()


def lokal(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def eingangsdateien(eingang: Path, art: str) -> list[Path]:
    """art = "lod1" oder "lod2"; sortiert, damit die Reihenfolge (und bei doppelten Kennungen der Sieger) fest ist."""
    muster = {"lod1": "lod1_2024_1261*", "lod2": "lod2_1261*"}[art]
    return sorted(p for p in eingang.glob(muster) if p.suffix.lower() in (".zip", ".gml", ".xml"))


def _stroeme(pfad: Path):
    if pfad.suffix.lower() == ".zip":
        with zipfile.ZipFile(pfad) as z:
            for name in sorted(z.namelist()):
                if name.lower().endswith((".gml", ".xml")):
                    with z.open(name) as f:
                        yield f"{pfad.name}:{name}", f
    else:
        with pfad.open("rb") as f:
            yield pfad.name, f


def _attribut(el, namen: set[str]) -> str | None:
    for x in el.iter():
        ln = lokal(x.tag)
        if ln in namen and (x.text or "").strip():
            return x.text.strip()
        if ln == "stringAttribute" and x.get("name") in namen:
            for v in x:
                if lokal(v.tag) == "value" and (v.text or "").strip():
                    return v.text.strip()
    return None


def _z_spanne(el) -> float | None:
    zmin = zmax = None
    for x in el.iter():
        ln = lokal(x.tag)
        if ln not in ("posList", "pos") or not (x.text or "").strip():
            continue
        dim = int(x.get("srsDimension") or 3)
        werte = x.text.split()
        if dim < 3 or len(werte) % dim:
            continue
        for z in werte[dim - 1::dim]:
            z = float(z)
            zmin = z if zmin is None or z < zmin else zmin
            zmax = z if zmax is None or z > zmax else zmax
    return None if zmin is None else zmax - zmin


def gebaeude_lesen(strom, quelle: str):
    """Ergibt (kennung, version, hoehe, art_der_hoehe) je bldg:Building der obersten Ebene."""
    tiefe = 0
    for ereignis, el in ET.iterparse(strom, events=("start", "end")):
        if lokal(el.tag) != "Building":
            continue
        if ereignis == "start":
            tiefe += 1
            continue
        tiefe -= 1
        if tiefe:
            continue          # BuildingPart oder verschachteltes Building: gehört zum äußeren
        kennung = _attribut(el, KENNUNG_NAMEN)
        version = _attribut(el, VERSION_NAMEN)
        hoehe, art = None, None
        for x in el.iter():
            if lokal(x.tag) == "measuredHeight" and (x.text or "").strip():
                try:
                    hoehe, art = float(x.text), "measuredHeight"
                except ValueError:
                    pass
                break
        if hoehe is None:
            sp = _z_spanne(el)
            if sp is not None:
                hoehe, art = sp, "z_spanne"
        yield kennung, version, hoehe, art
        el.clear()


def hoehen_lesen(pfade: list[Path]) -> tuple[dict[str, tuple[float, str | None]], dict]:
    hoehen: dict[str, tuple[float, str | None]] = {}
    z = {"dateien": [], "gebaeude": 0, "ohne_kennung": 0, "ohne_hoehe": 0, "doppelt": 0,
         "measuredHeight": 0, "z_spanne": 0, "unplausibel": 0}
    for p in pfade:
        for name, strom in _stroeme(p):
            n0 = z["gebaeude"]
            for kennung, version, hoehe, art in gebaeude_lesen(strom, name):
                z["gebaeude"] += 1
                if not kennung:
                    z["ohne_kennung"] += 1
                    continue
                if hoehe is None:
                    z["ohne_hoehe"] += 1
                    continue
                if not 0 < hoehe <= 300:
                    z["unplausibel"] += 1
                    continue
                z[art] += 1
                if kennung in hoehen:
                    z["doppelt"] += 1
                    continue          # erste Fundstelle gilt (Dateien sortiert)
                hoehen[kennung] = (hoehe, version)
            z["dateien"].append({"datei": name, "gebaeude": z["gebaeude"] - n0})
    return hoehen, z


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--eingang", type=Path, default=None)
    a = ap.parse_args()
    eingang = a.eingang or daten_ordner() / "eingang"
    for art in ("lod1", "lod2"):
        pfade = eingangsdateien(eingang, art)
        if not pfade:
            print(f"{art}: keine Datei unter {eingang} (Handdownload ausstehend)")
            continue
        h, z = hoehen_lesen(pfade)
        print(f"{art}: {len(h)} Höhen mit Kennung; Zählung {z}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
