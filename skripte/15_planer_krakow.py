"""Planer Kraków: Versorgungskennzahlen je dzielnica (Luftlinie) aus Zellen, Einrichtungen, Haltestellen und Parks.

Kein Netz, keine Datenbank. Regeln vor dem Lauf: pruefen/D6_protokoll.md (Regeln 11–15). Radien, Fundstellen,
Klassen und Geheimhaltung stehen in config/richtwerte.yaml (bildung, planer, geheimhaltung).

Eingang:  daten/zellen_odbl.js, daten/einrichtungen.js, daten/haltestellen.js (Zuordnung zur dzielnica über das Feld
          st der Zelle; st beruht auf den OSM-Grenzen, darum ist die Ausgabe eine _odbl-Datei)
          $KIEZ_DATEN/<einrichtungen.bdot10k.zip>   Parkflächen (OT_KUSK_A „park lub skwer“), mit den Zellen verschnitten
Ausgang:  daten/planer_odbl.js   (KIEZ_PLANER, Vertrag daten/schema/planer_odbl.json), belege/D6_planer.md

Kennzahlen je dzielnica (Regel 13): anteil_in_radius (szkola 3.000 und 4.000 m, przedszkole 3.000 m; Orientierung,
vorläufig), ew_je_einrichtung (szkola, przedszkole, zlobek), oepnv_takt (Haltestelle Taktklasse I/II in 500 m),
gruen_m2_je_ew. Unter geheimhaltung.min_ew_raumeinheit Einwohnern kein Wert (Regel 14).

Aufruf:
    uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
        python -I skripte/15_planer_krakow.py [--pruefen]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from shapely import STRtree
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import versorgung_werkzeug as vw  # noqa: E402

# Werte je dzielnica hängen über st an den OSM-Grenzen: nach der Entscheidung vom 13.11.2026 (Lizenzfolge, Variante a)
# als _odbl-Datei unter der ODbL (Vertrag daten/schema/planer_odbl.json).
AUS_JS = vw.DATEN / "planer_odbl.js"
AUS_BELEG = vw.WURZEL / "belege" / "D6_planer.md"
EW_ARTEN = ("szkola", "przedszkole", "zlobek")
# Vorbehalte als Schlüssel (Vertrag daten/schema/planer_odbl.json, Feld vorbehalte); keine Sätze in den Daten
UNS_ZELLE = ["zelle_1km_mittelpunkt"]
EINHEIT_TEXT = {"%": "%", "ew_je_einrichtung": "EW je Einrichtung", "m2_je_ew": "m² je EW"}   # nur für den Beleg


def zahl_de(x) -> str:
    """Zahl für den deutschen Beleg: Tausenderpunkt, Dezimalkomma, – für fehlende Werte."""
    if x is None:
        return "–"
    if isinstance(x, int) or float(x).is_integer():
        return vw.tausender(int(x))
    return f"{x:,.1f}".replace(",", " ").replace(".", ",").replace(" ", ".")


def runde(x: float, auf: int) -> int:
    return int(round(x / auf) * auf)


def parks_je_zelle(daten: Path, zip_rel: str, zellen: list[dict]) -> tuple[dict[int, float], float, int]:
    """Parkfläche (m², Rechen-System) je Zellindex; dazu Gesamtfläche aller Parks und Zahl der Parks."""
    e = vw.Ebene(daten / zip_rel, "OT_KUSK_A")
    t = e.nach(vw.RECHEN)
    parks = [vw.transformiere(g, t) for s, g in e if s and g is not None and s.get("RODZAJ") == "park lub skwer"
             and s.get("KAT_ISTNIE", "") in ("", "eksploatowany")]
    baum = STRtree([z["geom_r"] for z in zellen])
    je: dict[int, float] = defaultdict(float)
    for p in parks:
        for i in baum.query(p, predicate="intersects"):
            je[int(i)] += p.intersection(zellen[i]["geom_r"]).area
    return je, sum(p.area for p in parks), len(parks)


def rechnen() -> tuple[str, str]:
    rw = yaml.safe_load(ort_konfig.RICHTWERTE.read_text(encoding="utf-8"))
    pl, bi, gh, q = rw["planer"], rw["bildung"], rw["geheimhaltung"], rw["quellen"]
    stand = str(rw["stand"])
    min_ew, r_ew, r_ant = int(gh["min_ew_raumeinheit"]), int(gh["rundung_ew"]), int(gh["rundung_anteil_prozent"])
    teile = {t["nr"]: t["name"] for t in ort_konfig.lade()["gliederung"]["teile"]}
    zinhalt, zellen = vw.zellen_lesen()
    ein = vw.js_lesen(vw.DATEN / "einrichtungen.js")
    hst = vw.js_lesen(vw.DATEN / "haltestellen.js")
    eingaben = {"zellen_odbl.js": zinhalt, "einrichtungen.js": ein, "haltestellen.js": hst}
    beispiel = sorted(n for n, d in eingaben.items() if d.get("fixture") is True)
    ziele = vw.ziele_je_art(ein, hst, list(pl["oepnv_klassen"]))
    mitten = [z["mitte_r"] for z in zellen]
    abst = {a: vw.naechste(ziele[a], mitten) for a in ("szkola", "przedszkole", "haltestelle_takt")}

    # Einwohner je dzielnica
    ew_st: dict[str, int] = Counter()
    for z in zellen:
        if z["st"] in teile and z["ew"]:
            ew_st[z["st"]] += int(z["ew"])
    ohne_st = sum(int(z["ew"] or 0) for z in zellen if z["st"] not in teile)

    # Einrichtungen je dzielnica über die Zelle, in der sie liegen
    zbaum = STRtree([z["geom_w"] for z in zellen])
    ein_st: dict[tuple[str, str], int] = Counter()
    ohne_zelle = Counter()
    for f in ein["features"]:
        p = f["properties"]
        if p["art"] not in EW_ARTEN or p.get("hinweis"):
            continue
        treffer = [int(i) for i in zbaum.query(Point(*f["geometry"]["coordinates"]), predicate="intersects")]
        st = zellen[min(treffer)]["st"] if treffer else None
        if st in teile:
            ein_st[(st, p["art"])] += 1
        else:
            ohne_zelle[p["art"]] += 1

    park_je_zelle, park_gesamt, n_parks = parks_je_zelle(vw.kiez_daten(), rw["einrichtungen"]["bdot10k"]["zip"], zellen)
    gruen_st: dict[str, float] = defaultdict(float)
    for i, m2 in park_je_zelle.items():
        if zellen[i]["st"] in teile:
            gruen_st[zellen[i]["st"]] += m2

    def in_radius(art: str, radius: float) -> dict[str, int]:
        aus: dict[str, int] = Counter()
        for z, d in zip(zellen, abst[art]):
            if z["st"] in teile and z["ew"] and d is not None and d <= radius:
                aus[z["st"]] += int(z["ew"])
        return aus

    kennzahlen = []   # (Vorlage des Werts, Zähler je st, Nenner je st, Art der Rechnung)
    for art, schl, wert_m, seite in (("szkola", "szkola_podstawowa_droga", bi["szkola_podstawowa_droga"]["werte_m"]["klassen_1_4"], None),
                                     ("szkola", "szkola_podstawowa_droga", bi["szkola_podstawowa_droga"]["werte_m"]["klassen_5_8"], None),
                                     ("przedszkole", "przedszkole_droga", bi["przedszkole_droga"]["wert_m"], None)):
        rq = bi[schl]
        vorlage = {"kennzahl": "anteil_in_radius", "art": art, "einheit": "%", "methode": "luftlinie",
                   "status": "orientierung", "vorlaeufig": True,
                   "richtwert": {"wert": wert_m, "einheit": "m", "q": rq["quelle"], "seite": rq["seite"]},
                   "q": "bdot10k", "radius_m": int(wert_m)}
        unsich = ["norm_eigener_bezirk", *UNS_ZELLE]
        kennzahlen.append((vorlage, in_radius(art, float(wert_m)), ew_st, "anteil", unsich))
    for art in EW_ARTEN:
        vorlage = {"kennzahl": "ew_je_einrichtung", "art": art, "einheit": "ew_je_einrichtung", "methode": "luftlinie",
                   "status": "orientierung", "q": "bdot10k"}
        kennzahlen.append((vorlage, ew_st, {st: ein_st.get((st, art), 0) for st in teile}, "je",
                           ["ohne_richtwert", "bdot10k_nur_komplexe"]))
    radius = float(pl["oepnv_radius_m"]["wert"])
    vorlage = {"kennzahl": "oepnv_takt", "art": "haltestelle_takt", "einheit": "%", "methode": "luftlinie",
               "status": "orientierung", "q": "ztp", "radius_m": int(radius), "taktklassen": list(pl["oepnv_klassen"])}
    kennzahlen.append((vorlage, in_radius("haltestelle_takt", radius), ew_st, "anteil",
                       ["ohne_richtwert", "eigene_festlegung", *UNS_ZELLE]))
    vorlage = {"kennzahl": "gruen_m2_je_ew", "art": "park", "einheit": "m2_je_ew", "methode": "luftlinie",
               "status": "orientierung", "q": "bdot10k"}
    kennzahlen.append((vorlage, {st: gruen_st.get(st, 0.0) for st in teile}, ew_st, "gruen",
                       ["ohne_richtwert", "nur_park_lub_skwer"]))

    def wert_bauen(vorlage, z, n, rechnung, unsich, geheim: bool) -> dict:
        w = dict(vorlage)
        w["stand"] = stand
        if geheim:
            w.update(wert=None, zaehler=None, nenner=None, vorbehalte=["geheimhaltung"])
            return w
        if rechnung == "anteil":
            w.update(wert=round(100 * z / n / r_ant) * r_ant if n else None, zaehler=runde(z, r_ew), nenner=runde(n, r_ew))
        elif rechnung == "je":
            w.update(wert=round(z / n) if n else None, zaehler=runde(z, r_ew), nenner=n)
            if not n:
                unsich = ["keine_einrichtung", *unsich]
        else:
            w.update(wert=round(z / n, 1) if n else None, zaehler=int(round(z)), nenner=runde(n, r_ew))
        w["vorbehalte"] = list(unsich)
        return w

    raeume, verborgen = {}, []
    for st, name in teile.items():
        ew = ew_st.get(st, 0)
        geheim = ew < min_ew
        if geheim:
            verborgen.append(st)
        raeume[st] = {"name": name, "ew": None if geheim else runde(ew, r_ew),
                      "werte": [wert_bauen(v, z.get(st, 0), n.get(st, 0), r, u, geheim) for v, z, n, r, u in kennzahlen]}

    # gesamt: Summen der veröffentlichten Zähler und Nenner
    gesamt_werte = []
    for k, (v, _, _, r, u) in enumerate(kennzahlen):
        zs = [raeume[st]["werte"][k] for st in teile if raeume[st]["werte"][k]["zaehler"] is not None]
        z, n = sum(w["zaehler"] for w in zs), sum(w["nenner"] for w in zs)
        w = dict(v)
        w["stand"] = stand
        if r == "anteil":
            w.update(wert=round(100 * z / n / r_ant) * r_ant if n else None, zaehler=z, nenner=n)
        elif r == "je":
            w.update(wert=round(z / n) if n else None, zaehler=z, nenner=n)
        else:
            w.update(wert=round(z / n, 1) if n else None, zaehler=z, nenner=n)
        w["vorbehalte"] = list(u) + (["ohne_geheime_raeume"] if verborgen else [])
        gesamt_werte.append(w)
    ew_ges = sum(raeume[st]["ew"] for st in teile if raeume[st]["ew"] is not None)

    qk = ("bdot10k", "ztp", "prawo_oswiatowe")
    inhalt = {"stand": stand, "raumebene": "stadtteil", "rundung": {"ew": r_ew}, "geheimhaltung_min_ew": min_ew,
              "vorbehalte": ["orientierung_kein_amtlicher_wert"],
              "quellen": {k: {kk: q[k][kk] for kk in ("quelle", "lizenz", "vermerk", "url")} | {"stand": stand} for k in qk},
              "raeume": raeume,
              "gesamt": {"name": "Kraków", "ew": ew_ges, "raeume_ohne_wert": len(verborgen), "werte": gesamt_werte}}
    if beispiel:
        inhalt = {"fixture": True, "beispiel_eingaben": beispiel, **inhalt}
    kopf = ("Beispieldaten (Fixture): Einwohner und Zellen unecht. " if beispiel else "") + \
        "Planer je dzielnica (Luftlinie), erzeugt von skripte/15_planer_krakow.py. Quellen: " + \
        "; ".join(q[k]["vermerk"] for k in qk) + ". Zuordnung zur dzielnica über die Grenzen aus OpenStreetMap: " + \
        "© OpenStreetMap-Mitwirkende, Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/); " + \
        "die Datei als Ganzes steht unter der ODbL 1.0. ODbL"
    js = vw.js_text("KIEZ_PLANER", inhalt, kopf)

    T = vw.tausender
    b = ["# Beleg Planer je dzielnica (Luftlinie)", "",
         "Erzeugt von `skripte/15_planer_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). "
         "Regeln vor dem Lauf: `pruefen/D6_protokoll.md`, Regeln 11–15.", ""]
    if beispiel:
        b += ["> **Beispieldaten-Lauf.** " + ", ".join(f"`daten/{n}`" for n in beispiel) + " trägt `fixture: true`. "
              "Einwohner und Zuordnung der Zellen zu den dzielnice sind unecht; die Zählungen unten belegen nur, dass das "
              "Skript läuft, und dürfen nicht zitiert werden. `daten/planer_odbl.js` trägt deshalb selbst `fixture: true`.", ""]
    b += ["## Schritt 1: Zuordnung", "",
          f"- Einwohner in Zellen mit dzielnica: {T(sum(ew_st.values()))}; in Zellen ohne gültige dzielnica: {T(ohne_st)}",
          "- Einrichtungen (szkola, przedszkole, zlobek) einer dzielnica zugeordnet: "
          + ", ".join(f"{a} {T(sum(n for (s, x), n in ein_st.items() if x == a))}" for a in EW_ARTEN)
          + "; ohne Zelle mit dzielnica: " + (", ".join(f"{a} {n}" for a, n in sorted(ohne_zelle.items())) or "0"),
          f"- Parks (BDOT10k „park lub skwer“): {n_parks}, Fläche {T(int(round(park_gesamt)))} m², davon in Zellen mit "
          f"dzielnica {T(int(round(sum(gruen_st.values()))))} m²",
          f"- dzielnice unter {min_ew} Einwohnern (kein Wert): {len(verborgen)}"
          + (f" ({', '.join(verborgen)})" if verborgen else ""), "",
          "## Schritt 2: Werte ganz Kraków (Summe der veröffentlichten Zähler und Nenner)", "",
          "| Kennzahl | Art | Richtwert | Zähler | Nenner | Wert |", "|---|---|---|---|---|---|"]
    for w in gesamt_werte:
        rwt = f"{T(w['richtwert']['wert'])} m ({w['richtwert']['seite']})" if "richtwert" in w else "ohne"
        b.append(f"| `{w['kennzahl']}` | `{w['art']}` | {rwt} | {T(int(w['zaehler']))} | {T(int(w['nenner']))} | "
                 f"{zahl_de(w['wert'])} {EINHEIT_TEXT[w['einheit']]} |")
    b += ["", "## Grenzen", "",
          "- Luftlinie, kein Fußweg; alle Einwohner einer Zelle am Zellmittelpunkt.",
          "- Bildungsradien: Die Fundstellen (art. 39 ust. 2 und art. 32 ust. 3 Prawo oświatowe) meinen den Weg zur "
          "Schule des eigenen Schulbezirks; gerechnet ist die Luftlinie zur nächsten Schule jeder Art. Deshalb "
          "Orientierung und vorläufig, nie „standard urzędowy“.",
          "- Kein Richtwert für Einwohner je Einrichtung, ÖPNV und Grün: keine polnische amtliche Fundstelle gesucht oder "
          "gefunden (nicht geprüft).",
          "- Einwohner insgesamt statt Kinder je Altersgruppe (die Zellen tragen keine Kinderzahlen).",
          "- Wilson-Intervalle entfallen (Vollerhebung über Zellen, Regel 15).", ""]
    return js, "\n".join(b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pruefen", action="store_true", help="neu rechnen und byte-genau vergleichen, nichts schreiben")
    a = ap.parse_args()
    js, beleg = rechnen()
    ok = vw.ausgeben(AUS_JS, js, a.pruefen)
    ok = vw.ausgeben(AUS_BELEG, beleg, a.pruefen) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
