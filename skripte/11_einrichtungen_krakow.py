"""Einrichtungen in Kraków: Schulen, Kindergärten, Krippen, Krankenhäuser, Parks aus BDOT10k; Ärzte und Apotheken aus OSM.

Kein Netzabruf. Regeln vor dem Lauf: pruefen/D6_protokoll.md (Regeln 8–10). Zuordnung Ebene/RODZAJ → art und alle
Pfade stehen in config/richtwerte.yaml, Abschnitt einrichtungen.

Eingang:  $KIEZ_DATEN/<einrichtungen.bdot10k.zip>   BDOT10k Powiat 1261 (OT_KUOS_A, OT_KUOZ_A, OT_KUSK_A, OT_ADJA_A)
          $KIEZ_DATEN/<einrichtungen.rspo.datei>    RSPO-Export (Handdownload), nur mit lizenz_geprueft: true
          auswertung.osm_poi                        nur mit --osm-db (Leserolle mosidi_lesen, PG*-Umgebung)
Ausgang:  daten/einrichtungen.js        (KIEZ_EINRICHTUNGEN, Vertrag daten/schema/einrichtungen.json)
          daten/einrichtungen_odbl.js   (KIEZ_EINRICHTUNGEN_ODBL; ohne --osm-db oder bei leerer Tabelle Beispieldatei)
          belege/D6_einrichtungen.md    Zählungen je Schritt

Lage = Punkt in der Fläche (point_on_surface) im Koordinatensystem der .prj-Datei, danach nach WGS 84. Namen nur aus
NAZWA (Name der Einrichtung), keine Adresse. BDOT10k nennt keine Plätze und keine Schülerzahlen.

Aufruf:
    uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
        python -I skripte/11_einrichtungen_krakow.py [--osm-db] [--pruefen]
--pruefen rechnet neu und vergleicht alle Ausgaben byte-genau, ohne zu schreiben (Rückgabe 1 bei Abweichung).
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

import yaml
from shapely.geometry import Point
from shapely.prepared import prep

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import versorgung_werkzeug as vw  # noqa: E402

AUS_JS = vw.DATEN / "einrichtungen.js"
AUS_ODBL = vw.DATEN / "einrichtungen_odbl.js"
AUS_BELEG = vw.WURZEL / "belege" / "D6_einrichtungen.md"
ODBL_KOPF = ("Echte Dateien dieser Art stehen unter der Open Database License 1.0 "
             "(https://opendatacommons.org/licenses/odbl/1-0/), © OpenStreetMap-Mitwirkende. ODbL")


def bdot_lesen(cfg: dict, daten: Path, gem_r) -> tuple[list[dict], list[str]]:
    zip_pfad = daten / cfg["zip"]
    gueltig = set(cfg["kat_istnie_gueltig"])
    gem = prep(gem_r)
    feats, b = [], []
    b += ["## Schritt 1: BDOT10k-Komplexe", "",
          "| Ebene | RODZAJ | Sätze | übernommen als | weg (KAT_ISTNIE) |", "|---|---|---|---|---|"]
    ausserhalb = 0
    for ebene, zuordnung in cfg["ebenen"].items():
        e = vw.Ebene(zip_pfad, ebene)
        nach_w, nach_r = e.nach(vw.WGS84), e.nach(vw.RECHEN)
        z, weg = Counter(), Counter()
        for s, g in e:
            if s is None or g is None:
                z[("(gelöscht oder leer)",)] += 1
                continue
            rod = s.get("RODZAJ", "")
            z[rod] += 1
            art = zuordnung.get(rod)
            if art is None:
                continue
            if s.get("KAT_ISTNIE", "") not in gueltig:
                weg[rod] += 1
                continue
            p = g.representative_point()
            pw, pr = vw.transformiere(p, nach_w), vw.transformiere(p, nach_r)
            in_stadt = gem.contains(pr)
            ausserhalb += 0 if in_stadt else 1
            feats.append({"type": "Feature",
                          "geometry": {"type": "Point", "coordinates": [round(pw.x, 5), round(pw.y, 5)]},
                          "properties": {"id": s["LOKALNYID"], "art": art, "unterart": None, "q": "bdot10k",
                                         "name": s.get("NAZWA") or None, "plaetze": None, "schueler": None,
                                         "schueler_stand": None, "status": "lage_ohne_kapazitaet",
                                         "in_stadt": in_stadt}})
        for rod, n in sorted(z.items(), key=lambda kv: (-kv[1], str(kv[0]))):
            b.append(f"| `{ebene}` | {rod if isinstance(rod, str) else rod[0]} | {vw.tausender(n)} | "
                     f"{('`' + zuordnung[rod] + '`') if isinstance(rod, str) and rod in zuordnung else 'nicht übernommen'} | "
                     f"{weg.get(rod, 0) if isinstance(rod, str) else '–'} |")
    ids = [f["properties"]["id"] for f in feats]
    if len(set(ids)) != len(ids):
        raise SystemExit("Befund: LOKALNYID nicht eindeutig")
    b += ["", f"- übernommen: {vw.tausender(len(feats))}, davon außerhalb der Gemeindegrenze (Punkt in der Fläche): "
          f"{ausserhalb}", f"- mit Name (NAZWA): {sum(1 for f in feats if f['properties']['name'])}", ""]
    return feats, b


def rspo_lesen(cfg: dict, daten: Path) -> tuple[list[dict], list[str]]:
    pfad = daten / cfg["datei"]
    b = ["## Schritt 2: RSPO (Schulregister)", ""]
    if not pfad.exists():
        b += [f"- Datei `$KIEZ_DATEN/{cfg['datei']}` fehlt (Handdownload ausstehend): kein RSPO-Teil.", ""]
        return [], b
    if not cfg.get("lizenz_geprueft"):
        b += [f"- Datei `$KIEZ_DATEN/{cfg['datei']}` vorhanden, aber `lizenz_geprueft` ist nicht true: STOPP, kein "
              "RSPO-Teil (Lizenz der RSPO-Daten nicht geprüft).", ""]
        return [], b
    # Spaltennamen des Exports sind nicht geprüft; ohne Zuordnung in config/richtwerte.yaml kein Lesen.
    raise SystemExit("RSPO-Datei vorhanden und Lizenz geprüft: Spaltenzuordnung einrichtungen.rspo.spalten "
                     "festlegen und den Leser hier ergänzen (quellen-D6.md, erwartetes Format)")


def osm_lesen(arten: list[str]) -> list[tuple[str, str, str | None, float, float]]:
    import psycopg
    if os.environ.get("PGUSER") != "mosidi_lesen":
        raise SystemExit("--osm-db: erwartet PGUSER=mosidi_lesen (nur Lesen)")
    with psycopg.connect() as con, con.cursor() as cur:
        cur.execute("SELECT osm_id, art, unterart, ST_X(g), ST_Y(g) FROM "
                    "(SELECT osm_id, art, unterart, ST_Transform(geom, 4326) g FROM auswertung.osm_poi "
                    " WHERE art = ANY(%s)) x ORDER BY art, osm_id", (arten,))
        return cur.fetchall()


def osm_beispiel(arten: list[str]) -> list[dict]:
    """Klar unechte Punkte: regelmäßiges Raster im Kartenrahmen der Ortskonfiguration, Arten abwechselnd."""
    w, s, o, n = ort_konfig.lade()["karte"]["rahmen"]
    feats, i = [], 0
    for zi in range(1, 4):
        for si in range(1, 6):
            lon, lat = w + (o - w) * si / 6, s + (n - s) * zi / 4
            feats.append({"type": "Feature",
                          "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
                          "properties": {"id": f"beispiel-{i + 1:02d}", "art": arten[i % len(arten)],
                                         "unterart": None, "q": "osm"}})
            i += 1
    return feats


def rechnen(osm_db: bool) -> tuple[str, str, str]:
    rw = yaml.safe_load(ort_konfig.RICHTWERTE.read_text(encoding="utf-8"))
    cfg, q = rw["einrichtungen"], rw["quellen"]
    stand = str(rw["stand"])
    daten = vw.kiez_daten()
    gem_r, _ = vw.gemeinde_krakow(daten / cfg["bdot10k"]["zip"])

    b = ["# Beleg Einrichtungen", "",
         "Erzeugt von `skripte/11_einrichtungen_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). "
         "Regeln vor dem Lauf: `pruefen/D6_protokoll.md`, Regeln 8–10. Eingaben und Prüfsummen: "
         "`belege/rohdaten-D6-2026-11-13.sha256`.", ""]
    feats, bb = bdot_lesen(cfg["bdot10k"], daten, gem_r)
    b += bb
    rspo, bb = rspo_lesen(cfg["rspo"], daten)
    feats += rspo
    b += bb
    feats.sort(key=lambda f: (f["properties"]["art"], f["properties"]["id"]))
    arten_z = Counter(f["properties"]["art"] for f in feats)

    quellen = {"bdot10k": {k: q["bdot10k"][k] for k in ("quelle", "lizenz", "vermerk", "url")} | {"stand": stand}}
    inhalt = {"type": "FeatureCollection", "stand": stand,
              "lage": "punkt_in_flaeche", "ohne_angabe": ["plaetze", "schueler"],
              "vorbehalte": ["szkola_alle_schularten", "rspo_ungeprueft"],
              "quellen": quellen, "features": feats}
    js = vw.js_text("KIEZ_EINRICHTUNGEN", inhalt,
                    f"Einrichtungen, erzeugt von skripte/11_einrichtungen_krakow.py. Quelle: {q['bdot10k']['vermerk']}.")

    # OSM (nur *_odbl)
    arten = list(cfg["osm"]["arten"])
    b += ["## Schritt 3: Ärzte und Apotheken aus OSM (nur `daten/einrichtungen_odbl.js`)", ""]
    zeilen = osm_lesen(arten) if osm_db else []
    oq = {"osm": {k: q["osm"][k] for k in ("quelle", "lizenz", "vermerk", "url")} | {"stand": stand}}
    if zeilen:
        of = [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(x, 5), round(y, 5)]},
               "properties": {"id": oid, "art": art, "unterart": ua, "q": "osm"}} for oid, art, ua, x, y in zeilen]
        odbl = {"type": "FeatureCollection", "stand": stand,
                "ohne_angabe": ["name"], "vorbehalte": ["osm_vollstaendigkeit_ungeprueft"],
                "quellen": oq, "features": of}
        okopf = f"Einrichtungen aus OSM, erzeugt von skripte/11_einrichtungen_krakow.py. {ODBL_KOPF}"
        b += [f"- aus `auswertung.osm_poi`: {vw.tausender(len(of))} ("
              + ", ".join(f"{a} {vw.tausender(n)}" for a, n in sorted(Counter(f['properties']['art'] for f in of).items()))
              + ")", ""]
    else:
        of = osm_beispiel(arten)
        odbl = {"type": "FeatureCollection", "fixture": True, "stand": stand,
                "ohne_angabe": ["name"], "vorbehalte": ["beispiel_raster"],
                "quellen": oq, "features": of}
        okopf = ("Beispieldaten (Fixture): Punkte im Raster statt Einrichtungen, erzeugt von "
                 f"skripte/11_einrichtungen_krakow.py. {ODBL_KOPF}")
        grund = ("ohne `--osm-db` gerechnet" if not osm_db else "`auswertung.osm_poi` enthält keine Zeile der Arten "
                 + ", ".join(arten))
        b += [f"- {grund}: Beispieldatei mit `fixture: true`, {len(of)} Rasterpunkte. Overpass ist im Abrufskript "
              "gesperrt (`skripte/abruf.py`, „OSM nur aus dem Handdownload“).", ""]
    ojs = vw.js_text("KIEZ_EINRICHTUNGEN_ODBL", odbl, okopf)

    b += ["## Ergebnis `daten/einrichtungen.js`", "", "| art | Einrichtungen |", "|---|---|"]
    b += [f"| `{a}` | {vw.tausender(n)} |" for a, n in sorted(arten_z.items())]
    b += [f"| zusammen | {vw.tausender(len(feats))} |", "",
          "## Grenzen", "",
          "- BDOT10k erfasst Komplexe (Flächen mit eigener Abgrenzung), kein Register: Schulen und Kindergärten ohne eigene "
          "Fläche fehlen. Vollständigkeit gegen RSPO oder eine städtische Liste: nicht geprüft.",
          "- `szkola` umfasst Grund- und weiterführende Schulen (BDOT10k trennt sie nicht); Schulbezirke (obwody) fehlen.",
          "- Keine Plätze, keine Schülerzahlen, keine Öffnungs- oder Trägerangaben.",
          "- `szpital` umfasst laut BDOT10k-Wert auch Sanatorien; ambulante Ärzte nur über OSM (derzeit Beispieldaten).",
          "- Aktualität: Stand der BDOT10k-Lieferung für Powiat 1261 laut Datei, nicht gegen die Wirklichkeit geprüft.", ""]
    return js, ojs, "\n".join(b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--osm-db", action="store_true", help="Ärzte/Apotheken aus auswertung.osm_poi lesen (Leserolle)")
    ap.add_argument("--pruefen", action="store_true", help="neu rechnen und byte-genau vergleichen, nichts schreiben")
    a = ap.parse_args()
    js, ojs, beleg = rechnen(a.osm_db)
    ok = vw.ausgeben(AUS_JS, js, a.pruefen)
    ok = vw.ausgeben(AUS_ODBL, ojs, a.pruefen) and ok
    ok = vw.ausgeben(AUS_BELEG, beleg, a.pruefen) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
