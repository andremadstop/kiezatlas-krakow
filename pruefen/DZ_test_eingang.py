"""Codepfade der Handdownload-Leser in skripte/dz_denkmale.py mit erfundenen Eingängen (Beispieldaten, kein Netz).

Baut in einem Wegwerf-Ordner ein $KIEZ_DATEN mit dem echten BDOT10k-Paket (Verweis, nur gelesen) und erfundenen
Dateien unter eingang/: Wikidata-SPARQL-JSON, NID-CSV, GEZ-CSV und eine winzige OSM-PBF (Schreiber aus
pruefen/a3_pbf_schreiben.py, um Denkmal-Knoten ergänzt). Die erfundenen Punkte liegen auf Schwerpunkten echter
BDOT10k-Gebäude, damit Gebäudetreffer und Mehrfamilienhaus-Zuordnung geprüft werden. Schreibt nichts ins Repo.

Prüft: Zählungen je Quelle, Zusammenführung über die Registernummer, Bauzeitklassen (auch uneindeutig → null),
Kamienice je Delegatura, Ortsmarke aus OSM nur mit Quelle, Abbruch bei fremdem CSV-Format, Lesarten der Datumsangaben,
Sichtprüfung (Protokoll, Nachtrag 4): ohne Eingabe geprueft false, mit erfundener Eingabe Quoten nach der Regel, ohne
entschiedene Ansicht leere Quote, Abbruch mit Meldung bei einer Antwort außerhalb der Stichprobe, einem fremden Wert,
ungültigem Datum, kaputtem JSON oder falscher Form. Die echte Eingabe belege/DZ_sichtpruefung.json bleibt
unberührt (Wegwerf-Pfad).

Aufruf: python -I pruefen/DZ_test_eingang.py   Rückgabe 0 = grün, 1 = Befund, 77 = BDOT10k fehlt (übersprungen).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
sys.path.insert(0, str(WURZEL / "pruefen"))
import dz_denkmale as dz  # noqa: E402

befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def lesen(text: str) -> dict:
    return json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))


def main() -> int:
    echt = dz.daten_ordner() / dz.BDOT_REL
    if not echt.is_file():
        print(f"übersprungen: BDOT10k fehlt ({echt})")
        return 77

    print("Lesarten der Datumsangaben")
    faelle = {"1890": "1867_1918", "~1890": "1867_1918", "ca. 1700": "vor_1800", "1890s": "1867_1918",
              "1860s": None, "C19": None, "C17": "vor_1800", "1890..1910": "1867_1918", "1910-1925": None,
              "+1955-01-01T00:00:00Z": "1946_1989", "1999-05": "ab_1990", "przed 1900": None, "": None}
    falsch = {k: (dz.bauzeitklasse(k), v) for k, v in faelle.items() if dz.bauzeitklasse(k) != v}
    pruef(not falsch, f"{len(faelle)} Fälle{': ' + str(falsch) if falsch else ''}")

    b = dz.Bdot(echt)
    mfh = next(g for g, a in b.gebaeude if dz.ist_mfh(a))
    andere = next(g for g, a in b.gebaeude if a["FOBUD"] == "budynki biurowe")
    dritte = next(g for g, a in b.gebaeude if a["FOBUD"] == "budynki handlowo-usługowe")
    p_mfh = b.wgs(mfh.centroid.x, mfh.centroid.y, 7)
    p_and = b.wgs(andere.centroid.x, andere.centroid.y, 7)
    p_dr = b.wgs(dritte.centroid.x, dritte.centroid.y, 7)
    del_mfh = b.delegatura(mfh.centroid)

    with tempfile.TemporaryDirectory(prefix="dz_test_") as tmp:
        t = Path(tmp)
        (t / dz.BDOT_REL).parent.mkdir(parents=True)
        (t / dz.BDOT_REL).symlink_to(echt)
        e = t / "eingang"
        e.mkdir()

        def zeile(q, nr, lage=None, inc=None):
            z = {"item": {"value": f"http://www.wikidata.org/entity/{q}"}, "nr": {"value": nr}}
            if lage:
                z["coord"] = {"value": f"Point({lage[0]} {lage[1]})"}
            if inc:
                z["inception"] = {"value": inc}
            return z
        wd = {"head": {"vars": ["item", "nr", "coord", "inception"]}, "results": {"bindings": [
            zeile("Q1", "A-1", p_mfh, "1890-01-01T00:00:00Z"), zeile("Q1", "A-1", p_mfh, "1890-01-01T00:00:00Z"),
            zeile("Q2", "A-2"), zeile("Q3", "A-3", (21.0, 51.0)),
            zeile("Q4", "A-4", p_and, "1850-01-01T00:00:00Z"), zeile("Q4", "A-4", p_and, "1950-01-01T00:00:00Z")]}}
        (e / dz.EINGANG["wd"]).write_text(json.dumps(wd), encoding="utf-8")
        (e / dz.EINGANG["nid"]).write_text("numer_rejestru;nazwa;datowanie\nA 1;Przykład;1890\nA-9;Przykład;XIX w.\n",
                                           encoding="utf-8")
        (e / dz.EINGANG["gez"]).write_text(f"szerokosc,dlugosc,datowanie\n{p_dr[1]},{p_dr[0]},1925\n", encoding="utf-8")
        # Abruftag je Registerdatei aus eingang/HERKUNFT.md (Pflicht seit dem Echtlauf); Daten erfunden
        (e / "HERKUNFT.md").write_text(
            "| Datei | Quelle | Abruf |\n|---|---|---|\n"
            f"| {dz.EINGANG['wd']} | Test | 10.11.2026 |\n| {dz.EINGANG['nid']} | Test | 12.11.2026 |\n"
            f"| {dz.EINGANG['gez']} | Test | 11.11.2026 |\n", encoding="utf-8")

        import a3_pbf_schreiben as pbf
        pbf.k(900, p_mfh[0], p_mfh[1], heritage="4", start_date="1895")
        pbf.k(901, p_and[0], p_and[1], start_date="C19")
        pbf.k(902, p_dr[0], p_dr[1], addr__street="Tadeusza Kościuszki", addr__housenumber="18", building="yes")
        pbf.schreiben(e / "test.osm.pbf")

        os.environ["KIEZ_DATEN"] = str(t)
        dz.SICHT_PFAD = t / "sicht.json"                    # gibt es zuerst nicht: geprueft false
        aus = dz.rechnen()
        r = lesen(aus["daten/denkmale.js"])
        o = lesen(aus["daten/denkmale_odbl.js"])
        stich2 = json.loads(aus["belege/DZ_sichtpruefung_stichprobe.json"])
        sicht_ohne = (r["sichtpruefung"]["geprueft"], o["sichtpruefung"]["geprueft"], stich2["geprueft"])
        # erfundene Antworten: jede Antwort nacheinander aus festen Listen, damit jede Kategorie vorkommt
        lagen, ansichten = ["ja", "daneben", "nein"], ["ja", "unklar", "nein"]
        antw = [{"quelle": x["quelle"], "id": x["id"], "lage": lagen[i % 3], "ansicht": ansichten[i % 3]}
                for i, x in enumerate(stich2["punkte"])]
        dz.SICHT_PFAD.write_text(json.dumps({"datum": "2026-11-15", "pruefer": "Test", "startwert": dz.STARTWERT_2,
                                             "antworten": antw}), encoding="utf-8")
        aus2 = dz.rechnen()
        r2, o2 = lesen(aus2["daten/denkmale.js"]), lesen(aus2["daten/denkmale_odbl.js"])
        beleg2 = aus2["belege/DZ_denkmale_lauf.md"]
        # alle Ansichten „unklar“: Ansicht-Quote ohne Nenner (None), Beleg trotzdem schreibbar
        unklar = [{**a, "ansicht": "unklar"} for a in antw]
        dz.SICHT_PFAD.write_text(json.dumps({"datum": "2026-11-15", "startwert": dz.STARTWERT_2, "antworten": unklar}),
                                 encoding="utf-8")
        try:
            aus3 = dz.rechnen()
            o3 = lesen(aus3["daten/denkmale_odbl.js"])["sichtpruefung"]["gesamt"]["ansicht"]
            ohne_nenner = (o3["entschieden"], o3["quote"], o3["wilson95"]) == (0, None, None) \
                and "## Sichtprüfung Runde 2, ausgewertet" in aus3["belege/DZ_denkmale_lauf.md"]
        except (TypeError, KeyError) as x:
            ohne_nenner = repr(x)
        fehler = {}
        def setzen(roh: str) -> None:
            dz.SICHT_PFAD.write_text(roh, encoding="utf-8")
        def mit(antworten: list, **mehr) -> str:
            return json.dumps({"datum": "2026-11-15", "startwert": dz.STARTWERT_2, "antworten": antworten, **mehr})
        def kaputt(aendern) -> list:
            k = json.loads(json.dumps(antw))
            aendern(k)
            return k
        for name, roh in (("fremde Kennung", mit(kaputt(lambda a: a[0].update(id="Q0")))),
                          ("fremder Wert", mit(kaputt(lambda a: a[0].update(lage="vielleicht")))),
                          ("Antwort fehlt", mit(kaputt(lambda a: a.pop()))),
                          ("Antwort kein Objekt", mit(kaputt(lambda a: a.__setitem__(0, "ja")))),
                          ("Kennung keine Zeichenkette", mit(kaputt(lambda a: a[0].update(id=["Q1"])))),
                          ("Datum ungültig", mit(antw, datum="2026-13-45")),
                          ("kein JSON", "{antworten: ["),
                          ("Liste statt Objekt", json.dumps(antw))):
            setzen(roh)
            try:
                dz.rechnen()
                fehler[name] = False
            except dz.SichtFehler:
                fehler[name] = True
            except Exception as x:   # Abbruch ja, aber ohne Meldung der Sichtprüfung (Rückgabe 5)
                fehler[name] = type(x).__name__

    print("Register")
    pruef("fixture" not in r, "mit Eingang keine Beispieldaten")
    pruef(r["stand"] == "2026-11-12" and r["quellen"]["wd"]["abruf"] == "2026-11-10",
          f"Stand = jüngster Abruftag aus eingang/HERKUNFT.md ({r['stand']})")
    pruef(r["zaehlung"]["wd"] == {"ausserhalb_stadt": 1, "bauzeit_lesbar": 1, "bauzeit_nicht_lesbar": 1,
                                  "davon_mfh": 1, "in_stadt": 2, "mit_lage": 3, "ohne_lage": 1,
                                  "treffer_gebaeude": 2, "zeilen": 4},
          f"Wikidata: vier Objekte, Zeilen je Objekt zusammengefasst ({r['zaehlung']['wd']})")
    pruef(r["zaehlung"]["nid"] == {"doppelt_ueber_nummer": 1, "ohne_lage": 1, "zeilen": 2},
          f"NID: „A 1“ über die Nummer mit Wikidata zusammengeführt, „A-9“ ohne Lage ({r['zaehlung']['nid']})")
    pruef(r["zaehlung"]["gez"].get("in_stadt") == 1 and r["zaehlung"]["gez"].get("davon_mfh", 0) == 0,
          f"GEZ: Punkt aus Breite/Länge gelesen ({r['zaehlung']['gez']})")
    feats = r["objekte"]["features"]
    a = next(f for f in feats if f["properties"]["mfh"])
    pruef(a["properties"] == {"q": ["nid", "wd"], "ep": "1867_1918", "w": True, "mfh": True, "del": del_mfh},
          f"Treffer im Mehrfamilienhaus mit beiden Quellen und Klasse ({a['properties']})")
    pruef(any(f["properties"]["ep"] is None and f["properties"]["q"] == ["wd"] for f in feats),
          "zwei Inception-Werte in verschiedenen Klassen → Klasse null")
    pruef(r["kamienice"] == {del_mfh: 1}, f"Kamienice je Delegatura ({r['kamienice']})")
    pruef(r["quellen"]["nid"]["spalten"]["nr"] == "numer_rejestru", "NID-Spalte der Registernummer erkannt")

    print("OSM")
    pruef("fixture" not in o and o["eingang"]["datei"] == "test.osm.pbf", "mit PBF keine Beispieldaten")
    pruef(o["zaehlung"].get("objekte") == 2 and o["zaehlung"].get("mit_heritage") == 1
          and o["zaehlung"].get("bauzeit_nicht_lesbar") == 1, f"heritage und start_date gezählt ({o['zaehlung']})")
    pruef(o["kamienice"] == {del_mfh: 1}, f"Kamienice aus heritage im Mehrfamilienhaus ({o['kamienice']})")
    om = o["ortsmarken"][0]
    pruef(om["quelle"] == "osm" and om["geometry"] is not None and om["lage_geprueft"] is False,
          "Ortsmarke ul. Kościuszki 18 aus OSM verortet, als ungeprüft markiert")

    print("Sichtprüfung (Nachtrag 4)")
    pruef(sicht_ohne == (False, False, False), f"ohne Eingabe geprueft false in beiden Dateien und der Stichprobe {sicht_ohne}")
    def soll(antw: list[dict]) -> tuple:
        n = len(antw)
        lj, aj, an = (sum(a["lage"] == "ja" for a in antw), sum(a["ansicht"] == "ja" for a in antw),
                      sum(a["ansicht"] == "nein" for a in antw))
        return n, lj, round(100 * lj / n, 1), aj + an, round(100 * aj / (aj + an), 1) if aj + an else None
    def ist(e: dict) -> tuple:
        return e["n"], e["lage"]["ja"], e["lage"]["quote"], e["ansicht"]["entschieden"], e["ansicht"]["quote"]
    for name, d, q in (("Register", r2, "wd"), ("OSM", o2, "osm")):
        sp = d["sichtpruefung"]
        pruef(sp["geprueft"] is True and ist(sp["ergebnis"]) == soll([a for a in antw if a["quelle"] == q])
              and sp["pruefer_rolle"] == "sichtpruefung_luftbild" and "Test" not in json.dumps(d),
              f"{name}: Lage = ja / alle, Ansicht = ja / (ja + nein), kein Name ({ist(sp['ergebnis'])})")
    pruef(ist(o2["sichtpruefung"]["gesamt"]) == soll(antw) and "gesamt" not in r2["sichtpruefung"],
          f"gesamt nur in der ODbL-Datei ({ist(o2['sichtpruefung']['gesamt'])})")
    pruef("## Sichtprüfung Runde 2, ausgewertet" in beleg2, "Beleg mit Abschnitt „Sichtprüfung Runde 2, ausgewertet“")
    pruef(ohne_nenner is True, f"alle Ansichten unklar: Quote und Intervall leer, Beleg geschrieben ({ohne_nenner})")
    pruef(all(v is True for v in fehler.values()),
          f"Abbruch mit Meldung (SichtFehler) bei kaputter Eingabe ({fehler})")

    print("Fremdes Format")
    with tempfile.TemporaryDirectory(prefix="dz_test_") as tmp:
        p = Path(tmp) / "x.csv"
        p.write_text("a;b\n1;2\n", encoding="utf-8")
        try:
            dz.csv_lesen(p, brauche_nr=True)
            pruef(False, "NID ohne Spalte Registernummer bricht ab")
        except dz.FormatFehler:
            pruef(True, "NID ohne Spalte Registernummer bricht ab (Rückgabe 3 im Skript)")

    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
