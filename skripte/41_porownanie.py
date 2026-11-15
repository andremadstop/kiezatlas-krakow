"""Vergleich Kraków–Potsdam (Seite porownanie): Kennzahlen gleicher Definition aus demselben Datensatz.

Beide Städte aus dem Eurostat Census 2021 population grid (1 km, CC BY 4.0), dieselben Merkmale (T, Y_LT15, Y_1564,
Y_GE65) und dieselbe Zuordnungsregel (Zelle zählt zur Stadt, wenn ihr Mittelpunkt in der Stadt liegt):
  Kraków   daten/steckbrief.js (stadt.gitter, gerechnet von skripte/02_bevoelkerung.py aus PL_PD_3035_GPKG.zip),
           Fläche stadt.flaeche_km2 (PRG in BDOT10k)
  Potsdam  $KIEZ_DATEN/2026-11-14/41_vergleich/DE_PD_3035_GPKG.zip, Stadtgrenze = Vereinigung der Stadtteile aus
           ../kiezatlas-potsdam (daten/stadtteile.js, © Landeshauptstadt Potsdam, dl-de/zero-2-0, gelesen per
           git show <commit>, Commit steht in der Ausgabe); Fläche aus derselben Grenze in EPSG:3035 (flächentreu)
Anteile nach derselben Regel wie Kraków (raum_bevoelkerung.anteil: Nenner = Summe der Altersgruppen, unter der
Mindestfallzahl None). Gegenprobe Potsdam: Fläche gegen daten/kennzahlen.js des Potsdamer Atlas (dort amtlich
gerechnet); die Einwohnerzahl des Zensus-100-m-Gitters (dl-de/by-2-0) steht nur im Beleg, nicht in den Daten.

Schreibt daten/porownanie.js (Vertrag daten/schema/porownanie.json, Vorschlag) und belege/S1_porownanie.md.
Aufruf:
  python -I skripte/41_porownanie.py [--potsdam ../kiezatlas-potsdam] [--commit HEAD]
  python -I skripte/41_porownanie.py --pruefen     neu rechnen und mit daten/porownanie.js vergleichen
Kein Netz, keine Datenbank. Braucht $KIEZ_DATEN (Standard ../kiezatlas-daten/krakow) und das Potsdamer Repo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
import raum_bevoelkerung as rb  # noqa: E402
import numpy as np  # noqa: E402
import shapely  # noqa: E402
from pyproj import Transformer  # noqa: E402
from shapely.geometry import shape  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from collections import Counter  # noqa: E402

STAND = "2026-11-14"
DE_ZIP = f"{STAND}/41_vergleich/DE_PD_3035_GPKG.zip"
DE_URL = "https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/DE_PD_3035_GPKG.zip"
DE_STICHTAG = "2022-05-15"     # Zensus 2022, Zensusrunde 2021 der EU; nicht am Primärdokument geprüft
AUS_JS = WURZEL / "daten" / "porownanie.js"
AUS_BELEG = WURZEL / "belege" / "S1_porownanie.md"
FLAECHE_TOLERANZ_PROZ = 0.5     # Gegenprobe Fläche Potsdam gegen den Potsdamer Atlas


def js_lesen(text: str) -> dict:
    m = re.search(r"=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if not m:
        raise rb.Abbruch("JavaScript-Datei ohne Objekt")
    return json.loads(m.group(1))


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(potsdam: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(potsdam), *args], check=True, capture_output=True, text=True).stdout.strip()


def kennzahlen(s: dict, flaeche_km2: float) -> dict:
    a = s["u15"] + s["a15_64"] + s["a65p"]
    return {"zellen": s["zellen"], "einwohner": s["einwohner"], "u15": s["u15"], "a15_64": s["a15_64"], "a65p": s["a65p"],
            "a_ges": a, "q_u15": rb.anteil(s["u15"], a), "q_15_64": rb.anteil(s["a15_64"], a), "q_65p": rb.anteil(s["a65p"], a),
            "flaeche_km2": flaeche_km2, "dichte": round(s["einwohner"] / flaeche_km2) if flaeche_km2 else None}


def rechnen(potsdam: Path, commit: str) -> tuple[dict, list[str]]:
    d = rb.daten_ordner()
    zip_pfad = d / DE_ZIP
    if not zip_pfad.exists():
        raise rb.EingangFehlt(f"{DE_ZIP} fehlt unter {d}")
    zip_sha = sha256(zip_pfad.read_bytes())
    beleg: list[str] = []

    # Kraków: Werte des Atlas (gleiche Regel, gleicher Datensatz)
    sb_text = (WURZEL / "daten" / "steckbrief.js").read_text(encoding="utf-8")
    sb = js_lesen(sb_text)
    g = sb["stadt"]["gitter"]
    kr = kennzahlen({k: g[k] for k in ("zellen", "einwohner", "u15", "a15_64", "a65p")}, sb["stadt"]["flaeche_km2"])
    if kr["q_65p"] != g["q_65p"] or kr["q_u15"] != g["q_u15"] or kr["a_ges"] != g["a_ges"]:
        raise rb.Abbruch("Kraków: Anteile weichen von daten/steckbrief.js ab (andere Rechenregel?)")

    # Potsdam: Stadtgrenze aus dem Potsdamer Atlas (fester Commit)
    sha_commit = git(potsdam, "rev-parse", commit)
    beschreibung = git(potsdam, "describe", "--always", "--tags", sha_commit)
    st_text = git(potsdam, "show", f"{sha_commit}:daten/stadtteile.js")
    st = js_lesen(st_text)
    stadt = unary_union([shape(f["geometry"]) for f in st["features"]]).buffer(0)
    tr = Transformer.from_crs(4326, 3035, always_xy=True)
    stadt_3035 = shapely.transform(stadt, lambda xy: np.column_stack(tr.transform(xy[:, 0], xy[:, 1])))
    flaeche = round(stadt_3035.area / 1e6, 2)
    w, s, o, n = stadt_3035.bounds
    zellen, info = rb.gitter_lesen(zip_pfad, (w, s, o, n))
    mitte, anteile = rb.gitter_zuordnen(zellen, {"potsdam": stadt})
    summen = rb.summen_gitter(zellen, mitte, anteile)["potsdam"]
    pd = kennzahlen(summen, flaeche)
    drin = [z for z in zellen if mitte.get(z.gid) == "potsdam"]
    def leer(x) -> bool:   # GeoPackage liefert fehlende Werte als None, NaN oder Text „nan“ (DE-Lieferung)
        return x is None or x == "" or x == "nan" or (isinstance(x, float) and x != x)
    status = Counter("leer" if leer(z.status[0]) else str(z.status[0]) for z in drin)
    sonderwert = sum(1 for z in drin if not leer(z.status[1]))
    ohne_alter = sum(1 for z in drin if None in (z.u15, z.a15_64, z.a65p))

    # Gegenprobe: Fläche und Zensus-100-m-Summe des Potsdamer Atlas
    kz = js_lesen(git(potsdam, "show", f"{sha_commit}:daten/kennzahlen.js"))
    fl_atlas = kz["stadt"]["flaeche_km2"]
    fl_abw = round((flaeche - fl_atlas) / fl_atlas * 100, 2)
    ew_100m = next(k["wert"] for k in kz["stadt"]["kacheln"] if k["id"] == "einwohner")
    ew_100m_vermerk = next(k["quelle"] for k in kz["stadt"]["kacheln"] if k["id"] == "einwohner")
    ew_abw = round((pd["einwohner"] - ew_100m) / ew_100m * 100, 2)
    if abs(fl_abw) > FLAECHE_TOLERANZ_PROZ:
        raise rb.Abbruch(f"Potsdam: Fläche {flaeche} km² weicht um {fl_abw} % vom Potsdamer Atlas ({fl_atlas} km²) ab")

    daten = {
        "stand_auswertung": STAND,
        # Vergleich nur bei gleicher Definition (Felder statt Satz): Datensatz, Merkmale, Zuordnung (methode)
        "vergleich": {"gleicher_datensatz": True, "gleiche_merkmale": True,
                      "stichtage_gleich": sb["quellen"]["eurostat2021"]["stichtag"] == DE_STICHTAG},
        "quellen": {
            "eurostat_pl": {"quelle": "Eurostat, Census 2021 population grid, PL, 1 km (PL_PD_3035_GPKG.zip)",
                            "url": sb["quellen"]["eurostat2021"]["url"], "lizenz": "CC BY 4.0",
                            "vermerk": sb["quellen"]["eurostat2021"]["vermerk"],
                            "stichtag": sb["quellen"]["eurostat2021"]["stichtag"], "stichtag_geprueft": False},
            "eurostat_de": {"quelle": "Eurostat, Census 2021 population grid, DE, 1 km (DE_PD_3035_GPKG.zip)",
                            "url": DE_URL, "lizenz": "CC BY 4.0",
                            "vermerk": "EU copyright rules apply, while the licence would be under CC-BY 4.0.",
                            "sha256": zip_sha, "stichtag": DE_STICHTAG, "stichtag_geprueft": False},
            "flaeche_krakow": {"quelle": sb["quellen"]["bdot10k"]["quelle"], "vermerk": sb["quellen"]["bdot10k"]["vermerk"]},
            "grenze_potsdam": {"quelle": "Landeshauptstadt Potsdam, Stadtteile (Kiezatlas Potsdam, daten/stadtteile.js)",
                               "lizenz": "dl-de/zero-2-0", "commit": sha_commit, "stand": beschreibung,
                               "sha256": sha256(st_text.encode("utf-8"))},
        },
        "methode": {"gitter_zuordnung": "mittelpunkt", "mindestfallzahl": rb.MINDESTFALLZAHL, "gitter_srid": 3035,
                    "flaeche_potsdam_srid": 3035},
        "staedte": {"krakow": kr, "potsdam": pd},
        "kontrolle": {"potsdam_zellen_im_rahmen": info["zellen_im_rahmen"], "potsdam_zellen_mittelpunkt": pd["zellen"],
                      "potsdam_zellen_ohne_altersangabe": ohne_alter, "potsdam_flaeche_atlas_km2": fl_atlas,
                      "potsdam_flaeche_abweichung_proz": fl_abw},
    }
    beleg += [
        "# Vergleich Kraków–Potsdam: Rechnung und Gegenprobe",
        "",
        "Erzeugt von `skripte/41_porownanie.py` (nicht von Hand ändern). Datei: `daten/porownanie.js`.",
        "",
        "## Eingänge",
        "",
        f"- `$KIEZ_DATEN/{DE_ZIP}`, SHA256 `{zip_sha}` (Prüfsumme beim Abruf: `belege/rohdaten-S1-2026-11-14.sha256`)",
        f"- `daten/steckbrief.js` (Kraków, Stadtwerte des Gitters), SHA256 `{sha256(sb_text.encode('utf-8'))}`",
        f"- Potsdamer Atlas `{potsdam.name}`, Commit `{sha_commit}` (`{beschreibung}`): `daten/stadtteile.js` "
        f"(SHA256 `{sha256(st_text.encode('utf-8'))}`), `daten/kennzahlen.js` (nur Gegenprobe)",
        "",
        "## Zählungen Potsdam",
        "",
        f"- Gitterdatei DE: Tabelle `{info['tabelle']}`, {info['zellen_gesamt']} Zellen; im Rahmen der Stadtgrenze "
        f"{info['zellen_im_rahmen']}, davon mit Mittelpunkt in der Stadt {pd['zellen']}",
        f"- Zellen mit Mittelpunkt in der Stadt nach T_OBS_STATUS: {dict(sorted(status.items()))}; mit T_SPECIAL_VALUE: {sonderwert}; "
        f"mit fehlender Altersgruppe: {ohne_alter}",
        f"- Einwohner {pd['einwohner']}; Altersgruppen unter 15 {pd['u15']}, 15–64 {pd['a15_64']}, 65+ {pd['a65p']}, "
        f"Summe {pd['a_ges']}",
        f"- Anteile: unter 15 {pd['q_u15']} %, 15–64 {pd['q_15_64']} %, 65+ {pd['q_65p']} %",
        f"- Fläche (Vereinigung der Stadtteile, EPSG:3035): {flaeche} km²; Dichte {pd['dichte']} je km²",
        "",
        "## Zählungen Kraków (aus `daten/steckbrief.js`, nachgerechnet)",
        "",
        f"- Zellen {kr['zellen']}, Einwohner {kr['einwohner']}; unter 15 {kr['u15']}, 15–64 {kr['a15_64']}, 65+ {kr['a65p']}, "
        f"Summe {kr['a_ges']}",
        f"- Anteile: unter 15 {kr['q_u15']} %, 15–64 {kr['q_15_64']} %, 65+ {kr['q_65p']} % (gleich den Werten in steckbrief.js: geprüft)",
        f"- Fläche {kr['flaeche_km2']} km² (PRG in BDOT10k); Dichte {kr['dichte']} je km²",
        "",
        "## Gegenprobe",
        "",
        f"- Fläche Potsdam: {flaeche} km² gegen {fl_atlas} km² im Potsdamer Atlas, Abweichung {fl_abw} % "
        f"(Grenze {FLAECHE_TOLERANZ_PROZ} %)",
        f"- Einwohner Potsdam: {pd['einwohner']} (Eurostat 1 km) gegen {ew_100m} (Zensus 2022, 100-m-Gitter, Potsdamer Atlas), "
        f"Abweichung {ew_abw} %. Unterschied erwartet: andere Zellgröße, andere Geheimhaltung; die 100-m-Zahl erscheint "
        "nicht auf der Seite (Lizenz dl-de/by-2-0, Vermerk nur deutsch).",
        f"  Quellenangabe der 100-m-Zahl (wörtlich aus dem Potsdamer Atlas): {ew_100m_vermerk}; Lizenztext "
        "https://www.govdata.de/dl-de/by-2-0",
        "",
        "## Grenzen",
        "",
        f"- Stichtage verschieden: Kraków {sb['quellen']['eurostat2021']['stichtag']}, Potsdam {DE_STICHTAG}; beide nicht am "
        "Primärdokument geprüft (die INSPIRE-Metadaten in DE_PD_3035_GPKG.zip nennen nur den Zeitraum ab 2021-01-01).",
        f"- Die Fläche Krakaus stammt aus der PRG (Rechen-SRID des Atlas, EPSG:{sb['methode']['flaechen_srid']}), die Potsdams aus der Stadtteilgrenze (EPSG:3035); beide flächentreu "
        "genug für eine Dichte in ganzen Personen je km².",
        "- Nicht verglichen (auf der Seite benannt): Gebäude (BDOT10k gegen ALKIS), Bauzeit und Heizung (für Kraków keine offenen "
        "Daten), Taktklassen (Kraków nur in 1-km-Zellen), Werte je Stadtteil (Zellgröße zu grob, Grenzen Krakaus unter ODbL).",
    ]
    return daten, beleg


def js_text(daten: dict) -> str:
    kopf = ("/* Vergleich Kraków–Potsdam: Kennzahlen gleicher Definition (Eurostat Census 2021 population grid, 1 km, "
            "CC BY 4.0; Zuordnung nach Mittelpunkt). Erzeugt von skripte/41_porownanie.py, Vertrag daten/schema/porownanie.json. */\n")
    return kopf + "window.KIEZ_POROWNANIE=" + json.dumps(daten, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + ";\n"


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("--potsdam", type=Path, default=WURZEL.parent / "kiezatlas-potsdam")
    a.add_argument("--commit", default="HEAD")
    a.add_argument("--pruefen", action="store_true")
    o = a.parse_args()
    if o.pruefen and o.commit == "HEAD" and AUS_JS.exists():
        o.commit = js_lesen(AUS_JS.read_text(encoding="utf-8"))["quellen"]["grenze_potsdam"]["commit"]
    try:
        daten, beleg = rechnen(o.potsdam.resolve(), o.commit)
    except (rb.EingangFehlt, rb.Abbruch, subprocess.CalledProcessError) as x:
        print(f"  FEHLT Vergleich: {x}")
        return 1
    text = js_text(daten)
    if o.pruefen:
        alt = AUS_JS.read_text(encoding="utf-8") if AUS_JS.exists() else ""
        if alt != text:
            print("  FEHLT daten/porownanie.js ist nicht aus den Eingängen nachrechenbar (python -I skripte/41_porownanie.py)")
            return 1
        print("  ok    daten/porownanie.js aus den Eingängen nachgerechnet, byte-gleich")
        return 0
    AUS_JS.write_text(text, encoding="utf-8")
    AUS_BELEG.write_text("\n".join(beleg) + "\n", encoding="utf-8")
    p = daten["staedte"]["potsdam"]
    print(f"daten/porownanie.js geschrieben: Potsdam {p['einwohner']} Einwohner in {p['zellen']} Zellen, {p['flaeche_km2']} km²")
    return 0


if __name__ == "__main__":
    sys.exit(main())
