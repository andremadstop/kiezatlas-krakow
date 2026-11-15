"""Ziele der Fußweg-Rechnung in die Datenbank: Einrichtungen, Parkflächen und Takt-Haltestellen aus den echten Dateien.

Kein Netz. Füllt die Tabellen, die skripte/14b_fussweg.py liest und die bisher nur das Potsdamer 11_/13_ füllten:
  auswertung.einrichtung   aus daten/einrichtungen.js (BDOT10k): szkola, przedszkole, zlobek, szpital; ohne Punkte mit
                           Hinweis (strittige Lage) und ohne „park“ (Parks kommen als Fläche, unten)
  auswertung.gruenflaeche  BDOT10k OT_KUSK_A „park lub skwer“ (KAT_ISTNIE leer oder eksploatowany), art = park,
                           gleiche Auswahl wie skripte/15_planer_krakow.py
  auswertung.haltestelle   aus daten/haltestellen.js nur Taktklassen laut config/richtwerte.yaml planer.oepnv_klassen
                           (in der Fußweg-Rechnung heißt die Art „haltestelle“; im Export „haltestelle_takt“)
Rolle kiezatlas_rechnen (PG*-Umgebung, siehe skripte/14b_fussweg.sh). Jede Tabelle wird vorher geleert (TRUNCATE).
Schreibt belege/DE_ziele_db.md (Zählungen vorher/nachher je Tabelle und Art).

Aufruf: uv run … python -I skripte/14a_ziele_db_krakow.py [--trockenlauf]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import psycopg
import yaml
from pyproj import Transformer
from shapely.geometry import MultiPolygon, Point

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import versorgung_werkzeug as vw  # noqa: E402

ARTEN = ("szkola", "przedszkole", "zlobek", "szpital")
BELEG = vw.WURZEL / "belege" / "DE_ziele_db.md"
TABELLEN = ("auswertung.einrichtung", "auswertung.gruenflaeche", "auswertung.haltestelle")


def zaehlen(cur) -> dict[str, dict[str, int]]:
    erg = {}
    for t, spalte in zip(TABELLEN, ("art", "art", "klasse")):
        cur.execute(f"SELECT {spalte}, count(*) FROM {t} GROUP BY 1 ORDER BY 1")
        erg[t] = {str(a): int(n) for a, n in cur.fetchall()}
    return erg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trockenlauf", action="store_true", help="alles schreiben, am Ende ROLLBACK")
    a = ap.parse_args()
    rw = yaml.safe_load(ort_konfig.RICHTWERTE.read_text(encoding="utf-8"))
    q, klassen = rw["quellen"], list(rw["planer"]["oepnv_klassen"])
    ein = vw.js_lesen(vw.DATEN / "einrichtungen.js")
    hst = vw.js_lesen(vw.DATEN / "haltestellen.js")
    for n, d in (("einrichtungen.js", ein), ("haltestellen.js", hst)):
        if d.get("fixture") is True:
            raise SystemExit(f"daten/{n} ist eine Beispieldatei; die Fußweg-Ziele kommen nur aus echten Daten")
    nach_r = Transformer.from_crs(vw.WGS84, vw.RECHEN, always_xy=True)
    srid = ort_konfig.RECHEN_SRID

    e_zeilen, e_weg = [], Counter()
    for f in ein["features"]:
        p = f["properties"]
        if p["art"] not in ARTEN:
            e_weg[f"art {p['art']}"] += 1
            continue
        if p.get("hinweis"):
            e_weg["mit Hinweis (strittige Lage)"] += 1
            continue
        x, y = nach_r.transform(*f["geometry"]["coordinates"])
        e_zeilen.append((p["id"], p["art"], p.get("name"), q["bdot10k"]["quelle"], q["bdot10k"]["vermerk"],
                         ein["stand"], bool(p.get("in_stadt", True)), f"SRID={srid};{Point(x, y).wkt}"))

    zip_rel = rw["einrichtungen"]["bdot10k"]["zip"]
    ebene = vw.Ebene(vw.kiez_daten() / zip_rel, "OT_KUSK_A")
    t = ebene.nach(vw.RECHEN)
    g_zeilen = []
    for s, g in ebene:
        if not s or g is None or s.get("RODZAJ") != "park lub skwer" or s.get("KAT_ISTNIE", "") not in ("", "eksploatowany"):
            continue
        gr = vw.transformiere(g, t)
        if not gr.is_valid:
            gr = gr.buffer(0)
        mp = gr if isinstance(gr, MultiPolygon) else MultiPolygon([gr])
        g_zeilen.append((s["LOKALNYID"], "park", s.get("NAZWA") or None, round(mp.area, 1), q["bdot10k"]["quelle"],
                         q["bdot10k"]["vermerk"], f"SRID={srid};{mp.wkt}"))

    h_zeilen = []
    for f in hst["features"]:
        p = f["properties"]
        if p["taktklasse"] not in klassen:
            continue
        x, y = nach_r.transform(*f["geometry"]["coordinates"])
        h_zeilen.append((p["id"], p["name"], p["verkehrsmittel"], p["fahrten_hvz_je_richtung"], p["taktklasse"],
                         p["in_stadt"], f"SRID={srid};{Point(x, y).wkt}"))

    with psycopg.connect() as con, con.cursor() as cur:
        vorher = zaehlen(cur)
        cur.execute("TRUNCATE auswertung.einrichtung, auswertung.gruenflaeche, auswertung.haltestelle")
        with cur.copy("COPY auswertung.einrichtung (id, art, name, quelle, lizenz, stand, in_stadt, geom) FROM STDIN") as cp:
            for z in e_zeilen:
                cp.write_row(z)
        cur.execute("UPDATE auswertung.einrichtung SET status = 'lage_ohne_kapazitaet'")
        with cur.copy("COPY auswertung.gruenflaeche (id, art, bez, flaeche_m2, quelle, lizenz, geom) FROM STDIN") as cp:
            for z in g_zeilen:
                cp.write_row(z)
        with cur.copy("COPY auswertung.haltestelle (stop_id, name, verkehrsmittel, fahrten_hvz_je_richtung, klasse, "
                      "in_stadt, geom) FROM STDIN") as cp:
            for z in h_zeilen:
                cp.write_row(z)
        nachher = zaehlen(cur)
        if a.trockenlauf:
            con.rollback()
        else:
            con.commit()

    L = ["# Beleg Ziele der Fußweg-Rechnung in der Datenbank (erzeugt)", "",
         "Erzeugt von `skripte/14a_ziele_db_krakow.py`" + (" (Trockenlauf, ROLLBACK)" if a.trockenlauf else "")
         + "; nicht von Hand ändern. Quellen: `daten/einrichtungen.js` (BDOT10k), BDOT10k `OT_KUSK_A` "
         f"(`$KIEZ_DATEN/{zip_rel}`), `daten/haltestellen.js` (GTFS der ZTP, Taktklassen {', '.join(klassen)}).", "",
         "| Tabelle | Art bzw. Klasse | Zeilen vorher | Zeilen nachher |", "|---|---|---|---|"]
    for tab in TABELLEN:
        for k in sorted(set(vorher[tab]) | set(nachher[tab])):
            L.append(f"| `{tab}` | {k} | {vorher[tab].get(k, 0)} | {nachher[tab].get(k, 0)} |")
    L += ["", "Nicht übernommen aus `daten/einrichtungen.js`: "
          + ("; ".join(f"{k}: {n}" for k, n in sorted(e_weg.items())) or "nichts") + ".",
          f"Haltestellen in `daten/haltestellen.js`: {len(hst['features'])}, davon Taktklasse {' oder '.join(klassen)}: "
          f"{len(h_zeilen)}.", ""]
    BELEG.write_text("\n".join(L), encoding="utf-8")
    for z in L[6:]:
        print(z)
    return 0


if __name__ == "__main__":
    sys.exit(main())
