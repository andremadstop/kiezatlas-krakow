"""Fußweg-Ergebnisse als Seitendaten: daten/erreichbar_fuss_odbl.js (je Zelle) und daten/planer_fuss_odbl.js (je dzielnica).

Kein Netz. Liest (Rolle mosidi_lesen oder kiezatlas_rechnen, nur lesend):
  auswertung.zelle_erreichbar (methode = fussweg)   aus skripte/14b_fussweg.py
  auswertung.zelle_gruen      (methode = fussweg)   Parkfläche, deren Rand in gruen.radius_m Fußweg erreichbar ist
  daten/zellen_odbl.js        Reihenfolge der Zellen, Einwohner, Zuordnung st (OSM-Grenzen)
  config/richtwerte.yaml      Radien der Bildung, ÖPNV-Radius, Rundung, Geheimhaltung, Quellen
Schreibt:
  daten/erreichbar_fuss_odbl.js   KIEZ_ERREICHBAR_FUSS, Vertrag daten/schema/erreichbar_fuss_odbl.json
  daten/planer_fuss_odbl.js       KIEZ_PLANER_FUSS, Vertrag daten/schema/planer_fuss_odbl.json
  belege/DE_fussweg_export.md     Zählungen und Werte ganz Kraków

Arten im Export: wie in der Datenbank, außer „haltestelle“ → „haltestelle_takt“ (die Tabelle enthält nur Haltestellen
der Taktklassen aus planer.oepnv_klassen, skripte/14a_ziele_db_krakow.py) und „gruen“ → „park“ (BDOT10k „park lub
skwer“, Weg bis zum Rand der Fläche). Werte in m, auf planer.rundung_entfernung_m gerundet; unbewohnte Zellen und Zellen
ohne Netzanbindung = null.

Kennzahlen je dzielnica (alle Fußweg, Status orientierung): anteil_in_radius (szkola 3.000 und 4.000 m, przedszkole
3.000 m; vorläufig, weil zur nächsten Einrichtung jeder Art statt zur Einrichtung des eigenen Bezirks), oepnv_takt
(Haltestelle Taktklasse I/II in planer.oepnv_radius_m), gruen_in_radius (Park in gruen.radius_m, Standard 500 m).
Unter geheimhaltung.min_ew_raumeinheit Einwohnern kein Wert. Alles ODbL (OSM-Wegenetz und OSM-Grenzen).

Aufruf: uv run … python -I skripte/14c_fussweg_export_krakow.py [--pruefen]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import psycopg
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import versorgung_werkzeug as vw  # noqa: E402

AUS_E = vw.DATEN / "erreichbar_fuss_odbl.js"
AUS_P = vw.DATEN / "planer_fuss_odbl.js"
AUS_BELEG = vw.WURZEL / "belege" / "DE_fussweg_export.md"
UMBENENNEN = {"haltestelle": "haltestelle_takt", "gruen": "park"}
ODBL = ("Fußweg über das Wegenetz aus OpenStreetMap, Zuordnung zur dzielnica über die Grenzen aus OpenStreetMap: "
        "© OpenStreetMap-Mitwirkende, Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/); "
        "die Datei als Ganzes steht unter der ODbL 1.0. ODbL")
# Vorbehalte als Schlüssel (Vertrag daten/schema/planer_fuss_odbl.json, Feld vorbehalte); keine Sätze in den Daten
UNS_ZELLE = ["zelle_1km_mittelpunkt", "fussweg_osm_netz"]


def runde(x: float, auf: int) -> int:
    return int(round(x / auf) * auf)


def lesen(cur) -> tuple[dict, dict, int]:
    cur.execute("SELECT gitter_id, art, meter::float8 FROM auswertung.zelle_erreichbar WHERE methode = 'fussweg'")
    m: dict[str, dict[str, float | None]] = {}
    for gid, art, meter in cur.fetchall():
        m.setdefault(UMBENENNEN.get(art, art), {})[gid] = meter
    cur.execute("SELECT gitter_id, m2_gruen::float8, radius_m FROM auswertung.zelle_gruen WHERE methode = 'fussweg'")
    gr, radius = {}, set()
    for gid, m2, r in cur.fetchall():
        gr[gid] = m2
        radius.add(int(r))
    if len(radius) != 1:
        raise SystemExit(f"auswertung.zelle_gruen: Radien {sorted(radius)}; erwartet genau einen")
    return m, gr, radius.pop()


def rechnen(cur) -> tuple[str, str, str]:
    rw = yaml.safe_load(ort_konfig.RICHTWERTE.read_text(encoding="utf-8"))
    pl, bi, gh, q = rw["planer"], rw["bildung"], rw["geheimhaltung"], rw["quellen"]
    stand, rund = str(rw["stand"]), int(pl["rundung_entfernung_m"])
    min_ew, r_ew, r_ant = int(gh["min_ew_raumeinheit"]), int(gh["rundung_ew"]), int(gh["rundung_anteil_prozent"])
    teile = {t["nr"]: t["name"] for t in ort_konfig.lade()["gliederung"]["teile"]}
    zinhalt, zellen = vw.zellen_lesen()
    if zinhalt.get("fixture") is True:
        raise SystemExit("daten/zellen_odbl.js ist eine Beispieldatei; Fußweg-Export nur mit echten Zellen")
    meter, gruen, g_radius = lesen(cur)
    ids = [z["id"] for z in zellen]
    fehlend = sorted({a for a, w in meter.items() if set(w) != set(ids)})
    if fehlend or set(gruen) != set(ids):
        raise SystemExit(f"Fußweg-Zeilen passen nicht zu daten/zellen_odbl.js (Arten {fehlend}, Grün "
                         f"{len(gruen)} gegen {len(ids)} Zellen); erst skripte/14b_fussweg.sh rechnen")
    quellen = {k: {kk: q[k][kk] for kk in ("quelle", "lizenz", "vermerk", "url")} | {"stand": stand}
               for k in ("osm", "bdot10k", "ztp", "prawo_oswiatowe")}
    quellen_e = {k: v for k, v in quellen.items() if k != "prawo_oswiatowe"}

    # ---- je Zelle
    arten = sorted(meter)
    werte = {a: [None if not z["ew"] or meter[a][z["id"]] is None else runde(meter[a][z["id"]], rund) for z in zellen]
             for a in arten}
    e_inhalt = {"stand": stand, "methode": "fussweg", "einheit": "m", "quellen": quellen_e, "arten": arten,
                "anzahl": len(ids), "erste_id": ids[0], "letzte_id": ids[-1], "schluessel": "zellen.js-Reihenfolge",
                "werte": werte, "bezug": "zellmittelpunkt", "ziele_ausserhalb_stadt": True,
                "taktklassen": list(pl["oepnv_klassen"]), "park_bis": "rand_der_flaeche",
                "osm_arten": sorted(a for a in arten if a not in ("haltestelle_takt", "park", "szkola", "przedszkole",
                                                                  "zlobek", "szpital")),
                "vorbehalte": ["osm_vollstaendigkeit_ungeprueft"]}
    e_js = vw.js_text("KIEZ_ERREICHBAR_FUSS", e_inhalt, "Erreichbarkeit je Zelle (Fußweg), erzeugt von "
                      "skripte/14c_fussweg_export_krakow.py. Quellen: " + "; ".join(q[k]["vermerk"] for k in ("bdot10k", "ztp"))
                      + ". " + ODBL)

    # ---- je dzielnica
    ew_st: dict[str, int] = Counter()
    for z in zellen:
        if z["st"] in teile and z["ew"]:
            ew_st[z["st"]] += int(z["ew"])

    def zaehler(bed) -> dict[str, int]:
        aus: dict[str, int] = Counter()
        for z in zellen:
            if z["st"] in teile and z["ew"] and bed(z["id"]):
                aus[z["st"]] += int(z["ew"])
        return aus

    def in_radius(art: str, r: float):
        return zaehler(lambda g: meter[art][g] is not None and meter[art][g] <= r)

    kennzahlen = []
    for art, schl, wert_m in (("szkola", "szkola_podstawowa_droga", bi["szkola_podstawowa_droga"]["werte_m"]["klassen_1_4"]),
                              ("szkola", "szkola_podstawowa_droga", bi["szkola_podstawowa_droga"]["werte_m"]["klassen_5_8"]),
                              ("przedszkole", "przedszkole_droga", bi["przedszkole_droga"]["wert_m"])):
        rq = bi[schl]
        kennzahlen.append(({"kennzahl": "anteil_in_radius", "art": art, "einheit": "%", "methode": "fussweg",
                            "status": "orientierung", "vorlaeufig": True,
                            "richtwert": {"wert": wert_m, "einheit": "m", "q": rq["quelle"], "seite": rq["seite"]},
                            "q": "bdot10k", "radius_m": int(wert_m)},
                           in_radius(art, float(wert_m)), ["norm_eigener_bezirk", *UNS_ZELLE]))
    r_oe = float(pl["oepnv_radius_m"]["wert"])
    kennzahlen.append(({"kennzahl": "oepnv_takt", "art": "haltestelle_takt", "einheit": "%", "methode": "fussweg",
                        "status": "orientierung", "q": "ztp", "radius_m": int(r_oe), "taktklassen": list(pl["oepnv_klassen"])},
                       in_radius("haltestelle_takt", r_oe), ["ohne_richtwert", "eigene_festlegung", *UNS_ZELLE]))
    kennzahlen.append(({"kennzahl": "gruen_in_radius", "art": "park", "einheit": "%", "methode": "fussweg",
                        "status": "orientierung", "q": "bdot10k", "radius_m": int(g_radius)},
                       zaehler(lambda g: gruen[g] is not None and gruen[g] > 0),
                       ["ohne_richtwert", "eigene_festlegung", "nur_park_lub_skwer", *UNS_ZELLE]))

    def wert(vorlage, z, n, unsich, geheim):
        w = dict(vorlage)
        w["stand"] = stand
        if geheim:
            w.update(wert=None, zaehler=None, nenner=None, vorbehalte=["geheimhaltung"])
        else:
            w.update(wert=round(100 * z / n / r_ant) * r_ant if n else None, zaehler=runde(z, r_ew), nenner=runde(n, r_ew),
                     vorbehalte=list(unsich))
        return w

    raeume, verborgen = {}, []
    for st, name in teile.items():
        ew = ew_st.get(st, 0)
        geheim = ew < min_ew
        if geheim:
            verborgen.append(st)
        raeume[st] = {"name": name, "ew": None if geheim else runde(ew, r_ew),
                      "werte": [wert(v, zz.get(st, 0), ew, u, geheim) for v, zz, u in kennzahlen]}
    gesamt_werte = []
    for k, (v, _zz, u) in enumerate(kennzahlen):
        zs = [raeume[st]["werte"][k] for st in teile if raeume[st]["werte"][k]["zaehler"] is not None]
        z, n = sum(w["zaehler"] for w in zs), sum(w["nenner"] for w in zs)
        w = dict(v)
        w.update(stand=stand, wert=round(100 * z / n / r_ant) * r_ant if n else None, zaehler=z, nenner=n,
                 vorbehalte=list(u) + (["ohne_geheime_raeume"] if verborgen else []))
        gesamt_werte.append(w)
    p_inhalt = {"stand": stand, "raumebene": "stadtteil", "rundung": {"ew": r_ew}, "geheimhaltung_min_ew": min_ew,
                "vorbehalte": ["orientierung_kein_amtlicher_wert"], "quellen": quellen,
                "raeume": raeume,
                "gesamt": {"name": "Kraków", "ew": sum(r["ew"] for r in raeume.values() if r["ew"] is not None),
                           "raeume_ohne_wert": len(verborgen), "werte": gesamt_werte}}
    p_js = vw.js_text("KIEZ_PLANER_FUSS", p_inhalt, "Planer je dzielnica (Fußweg), erzeugt von "
                      "skripte/14c_fussweg_export_krakow.py. Quellen: " + "; ".join(q[k]["vermerk"] for k in ("bdot10k", "ztp", "prawo_oswiatowe"))
                      + ". " + ODBL)

    T = vw.tausender
    b = ["# Beleg Fußweg-Export (erzeugt)", "",
         "Erzeugt von `skripte/14c_fussweg_export_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau "
         "gegen die Datenbank). Grundlage: `auswertung.zelle_erreichbar` und `zelle_gruen` (methode fussweg) aus "
         "`skripte/14b_fussweg.py`, Bericht `belege/DE_fussweg.md`.", "",
         f"- Zellen: {len(ids)}, bewohnt {sum(1 for z in zellen if z['ew'])}, Einwohner {T(sum(int(z['ew'] or 0) for z in zellen))}",
         f"- dzielnice unter {min_ew} Einwohnern (kein Wert): {len(verborgen)}", "",
         "| Art (je Zelle) | Zellen mit Wert | bewohnte Zellen ohne Wert | Median m (bewohnte Zellen) |", "|---|---|---|---|"]
    for a in arten:
        vals = sorted(x for x in werte[a] if x is not None)
        med = vals[len(vals) // 2] if vals else None
        ohne = sum(1 for z, x in zip(zellen, werte[a]) if z["ew"] and x is None)
        b.append(f"| `{a}` | {len(vals)} | {ohne} | {T(med) if med is not None else '–'} |")
    b += ["", "## Ganz Kraków (Summe der veröffentlichten Zähler und Nenner)", "",
          "| Kennzahl | Art | Richtwert | Zähler | Nenner | Wert |", "|---|---|---|---|---|---|"]
    for w in gesamt_werte:
        rwt = f"{T(w['richtwert']['wert'])} m ({w['richtwert']['seite']})" if "richtwert" in w else "ohne"
        b.append(f"| `{w['kennzahl']}` | `{w['art']}` | {rwt} | {T(int(w['zaehler']))} | {T(int(w['nenner']))} | "
                 f"{w['wert']} % |")
    b += ["", "## Grenzen", "",
          "- Ziele: Schulen, Kindergärten, Krippen und Krankenhäuser nur aus BDOT10k (Komplexe mit eigener Fläche, keine "
          "Plätze, Vollständigkeit gegen das Schulregister nicht geprüft); Krippen: nur 2 Einträge.",
          "- Gehgeschwindigkeit, Grün-Radius und Grünarten sind Standards der Fußweg-Rechnung, solange "
          "`config/richtwerte.yaml` sie nicht nennt.", ""]
    return e_js, p_js, "\n".join(b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pruefen", action="store_true", help="neu rechnen und byte-genau vergleichen, nichts schreiben")
    a = ap.parse_args()
    with psycopg.connect() as con, con.cursor() as cur:
        e_js, p_js, beleg = rechnen(cur)
    ok = vw.ausgeben(AUS_E, e_js, a.pruefen)
    ok = vw.ausgeben(AUS_P, p_js, a.pruefen) and ok
    ok = vw.ausgeben(AUS_BELEG, beleg, a.pruefen) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
