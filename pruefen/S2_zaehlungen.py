"""Zählungen der Kartenseiten Erreichbarkeit (planer), Kamienice (kamienice) und Wohnungsbestand (modernizacja).

Die Seiten setzen keine Zahl von Hand: Sie lesen jede Zahl aus daten/*.js oder rechnen sie im Browser aus diesen
Dateien (Anzahl Punkte je Art, Anteile). Dieses Skript rechnet dieselben Zahlen mit denselben Regeln aus denselben
Dateien nach und schreibt sie nach belege/S2_seiten_zaehlungen.md, damit jede Zahl auf den Seiten einen Beleg hat.
Die Regeln stehen je Abschnitt dabei (Fundstelle im Code: erreichbarkeit.js, kamienice.js, sanierungsatlas.js).

Aufruf:
  python -I pruefen/S2_zaehlungen.py            Beleg schreiben
  python -I pruefen/S2_zaehlungen.py --pruefen  neu rechnen und mit dem eingecheckten Beleg vergleichen (Rückgabe 1 bei Abweichung)
Kein Netz, keine Datenbank, nur Standardbibliothek.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
BELEG = WURZEL / "belege" / "S2_seiten_zaehlungen.md"


def lade(name: str) -> dict:
    t = (WURZEL / "daten" / name).read_text(encoding="utf-8")
    i = t.index("=", t.index("window."))
    return json.loads(t[i + 1:].strip().rstrip(";"))


def sha(name: str) -> str:
    return hashlib.sha256((WURZEL / "daten" / name).read_bytes()).hexdigest()


def proz(z: float, n: float, stellen: int = 1) -> str:
    return f"{100 * z / n:.{stellen}f}".replace(".", ",") + " %" if n else "k. A."


def erzeugen() -> str:
    dateien = ["erreichbar.js", "erreichbar_fuss_odbl.js", "einrichtungen.js", "einrichtungen_odbl.js", "haltestellen.js",
               "planer_odbl.js", "planer_fuss_odbl.js", "zellen_odbl.js", "denkmale_odbl.js", "denkmale_bdot.js",
               "sanierung.js", "sanierung_odbl.js"]
    z = ["# Zählungen der Kartenseiten Erreichbarkeit, Kamienice und Wohnungsbestand", "",
         "Erzeugt von `pruefen/S2_zaehlungen.py` aus den Datendateien (keine Datenbank, kein Netz). Jede Zahl, die die",
         "Seiten `planer`, `kamienice` und `modernizacja` zeigen, steht hier mit der Regel, nach der die Seite sie aus",
         "derselben Datei liest oder rechnet. `--pruefen` vergleicht byte-gleich.", "", "## Eingänge", "",
         "| Datei | SHA-256 |", "|---|---|"]
    z += [f"| `daten/{d}` | `{sha(d)}` |" for d in dateien]

    # ---------------- Erreichbarkeit
    E, F, ZE = lade("erreichbar.js"), lade("erreichbar_fuss_odbl.js"), lade("zellen_odbl.js")
    EIN, EO, HS = lade("einrichtungen.js"), lade("einrichtungen_odbl.js"), lade("haltestellen.js")
    z += ["", "## Erreichbarkeit (`planer`, Modul `erreichbarkeit.js`)", "",
          f"Zellen: {len(ZE['features'])} (`zellen_odbl.js`); Reihenfolge geprüft wie im Modul (anzahl, erste_id, letzte_id):"]
    for name, d in (("Luftlinie, erreichbar.js", E), ("Fußweg, erreichbar_fuss_odbl.js", F)):
        f = ZE["features"]
        ok = d["anzahl"] == len(f) and d["erste_id"] == f[0]["properties"]["id"] and d["letzte_id"] == f[-1]["properties"]["id"]
        z.append(f"- {name}: passt = {'ja' if ok else 'NEIN'}; Zellen mit Wert je Ziel (Zellen ohne Wert sind auf der Karte grau):")
        z.append("  " + ", ".join(f"{a} {sum(1 for v in d['werte'][a] if v is not None)}" for a in d["arten"]))
    z += ["", "Punkte je Ziel, wie die Legende sie zählt (Filter `art` in der Datei):",
          "- BDOT10k (`einrichtungen.js`): " + ", ".join(f"{a} {n}" for a, n in sorted(Counter(x["properties"]["art"] for x in EIN["features"]).items())),
          "- OpenStreetMap (`einrichtungen_odbl.js`): " + ", ".join(f"{a} {n}" for a, n in sorted(Counter(x["properties"]["art"] for x in EO["features"]).items())),
          "", f"Haltestellen (`haltestellen.js`, Fahrplantag {HS['stichtag']}, Fenster {HS['fenster'][0]}–{HS['fenster'][1]}): {len(HS['features'])}; je Taktklasse "
          + ", ".join(f"{k} {n}" for k, n in sorted(Counter(x["properties"]["taktklasse"] for x in HS["features"]).items()))
          + f"; außerhalb der Stadt {sum(1 for x in HS['features'] if x['properties']['in_stadt'] is False)}. Klassengrenzen (Abfahrten je Stunde, Legende): "
          + ", ".join(f"{k} ≥ {v:g}" for k, v in HS["klassen"]["grenzen"].items()) + "."]
    for name, datei in (("Luftlinie", "planer_odbl.js"), ("Fußweg", "planer_fuss_odbl.js")):
        P = lade(datei)
        z += ["", f"Kennzahlen je Stadtteil, {name} (`{datei}`, Stand {P['stand']}, Einwohner gerundet auf {P['rundung']['ew']}): "
              f"{len(P['raeume'])} Stadtteile, je Stadtteil {sorted({len(r['werte']) for r in P['raeume'].values()})} Kennzahlen; ganze Stadt:"]
        for w in P["gesamt"]["werte"]:
            r = f", Richtwert {w['richtwert']['wert']} {w['richtwert']['einheit']}" if w.get("richtwert") else ""
            z.append(f"- {w['kennzahl']} / {w['art']}{r}: Wert {w['wert']} {w['einheit']}, Zähler {w['zaehler']}, Nenner {w['nenner']}, Status {w['status']}")

    # ---------------- Kamienice
    O, B = lade("denkmale_odbl.js"), lade("denkmale_bdot.js")
    feat = O["objekte"]["features"]
    kl = lambda ep: "null" if ep is None else ep
    h = [x for x in feat if x["properties"]["h"] is True]
    kam = [x for x in feat if x["properties"]["h"] is True and x["properties"]["mfh"] is True]
    z += ["", "## Kamienice (`kamienice`, Modul `kamienice.js`)", "",
          f"OpenStreetMap (`denkmale_odbl.js`, Stand {O['stand']}): Objekte {len(feat)} (Feld zaehlung.objekte = {O['zaehlung']['objekte']}).",
          f"- Standardansicht (Denkmalangabe, h = true): {len(h)}; je Bauzeitklasse " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(kl(x['properties']['ep']) for x in h).items())),
          f"- „Auch Objekte ohne Denkmalangabe“ (alle): {len(feat)}; je Bauzeitklasse " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(kl(x['properties']['ep']) for x in feat).items())),
          f"- „Nur Kamienice“ (h = true und mfh = true): {len(kam)}; je Delegatur " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(x['properties']['del'] for x in kam).items()))
          + f"; Feld kamienice der Datei: Summe {sum(O['kamienice'].values())} = {', '.join(f'{k} {v}' for k, v in sorted(O['kamienice'].items()))}",
          "- Objekte mit Denkmalangabe je Delegatur (Tabelle): " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(x['properties']['del'] for x in h).items())),
          "- Feld zaehlung (Blatt): " + ", ".join(f"{k} {v}" for k, v in O["zaehlung"].items()),
          f"- Sichtprüfung: geprüft = {O['sichtpruefung']['geprueft']}, Stichprobe {O['sichtpruefung']['stichprobe']}"
          + (f"; Lage auf dem Objekt {O['sichtpruefung']['ergebnis']['lage']['ja']} von {O['sichtpruefung']['ergebnis']['n']}"
             f" = {O['sichtpruefung']['ergebnis']['lage']['quote']} %, beide Quellen {O['sichtpruefung']['gesamt']['lage']['ja']}"
             f" von {O['sichtpruefung']['gesamt']['n']} = {O['sichtpruefung']['gesamt']['lage']['quote']} %"
             if O["sichtpruefung"]["geprueft"] else ""),
          f"- Ortsmarke: {O['ortsmarken'][0]['schluessel']}, Quelle {O['ortsmarken'][0]['quelle']}, lage_geprueft = {O['ortsmarken'][0]['lage_geprueft']}",
          "", f"BDOT10k (`denkmale_bdot.js`, Stand {B['stand']}): " + ", ".join(f"{k} {v}" for k, v in B["zaehlung"].items() if not isinstance(v, dict))
          + "; Komplexe " + ", ".join(f"{k} {v}" for k, v in B["zaehlung"]["komplexe"].items()) + f" (Polygone in der Datei: {len(B['komplexe']['features'])})",
          "- je Delegatur: " + "; ".join(f"{k}: Mehrfamilienhäuser {v['mehrfamilienhaeuser']}, Name „Kamienica“ {v['namensbezug']}" for k, v in sorted(B["delegaturen"].items()))]

    # ---------------- Wohnungsbestand
    SL, SO = lade("sanierung.js"), lade("sanierung_odbl.js")
    P = SO["punkte"]["features"]
    Y, TD = SL["typologie"], SO["typologie_dzielnice"]["je_dzielnica"]
    z += ["", "## Wohnungsbestand und Sanierung (`modernizacja`, Modul `sanierungsatlas.js`)", "",
          f"Liste (`sanierung.js`, Stand {SL['stand']}): Einträge {SL['liste']['eintraege']}; je Art " + ", ".join(f"{k} {v}" for k, v in SL["liste"]["je_art"].items())
          + "; je Eigentum " + ", ".join(f"{k} {v}" for k, v in SL["liste"]["je_eigentum"].items())
          + f"; samoistne posiadanie {SL['liste']['samoistne_posiadanie']}; Orte " + ", ".join(f"{k} {v}" for k, v in SL["liste"]["miejscowosc"].items()) + ".",
          f"- Punkte in der Karte (`sanierung_odbl.js`): {len(P)}; Eigentum " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(x['properties']['eig'] for x in P).items()))
          + f" (nur {', '.join(SO['punkte']['nur_eigentum'])}); weggelassene Einfamilienhäuser {SO['punkte']['ausgelassen_kleinhaus']}, unter {SO['punkte']['geschosse_min']} Geschossen oder ohne Geschosszahl {SO['punkte']['ausgelassen_unter_3_geschosse']}",
          "- Punkte je Art (Legende): " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(x['properties']['art'] for x in P).items())),
          "- Punkte mit Typ (violetter Ring): " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(x['properties']['typ'] for x in P if x['properties']['typ']).items())),
          "- Höhenherkunft der Punkte: " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(str(x['properties']['hq']) for x in P).items())),
          f"- Verortung: Quote {SO['verortung']['quote']} % von {SO['verortung']['in_krakow']} (Wilson 95 %: {SO['verortung']['wilson95'][0]}–{SO['verortung']['wilson95'][1]}); Klassen "
          + ", ".join(f"{k} {v}" for k, v in SO["verortung"]["je_klasse"].items()),
          f"- Gegenprobe dzielnica: {SO['gegenprobe_dzielnica']['gleich']} von {SO['gegenprobe_dzielnica']['n']} = {SO['gegenprobe_dzielnica']['quote']} % (Wilson 95 %: {SO['gegenprobe_dzielnica']['wilson95'][0]}–{SO['gegenprobe_dzielnica']['wilson95'][1]})",
          "- Verknüpfung: " + ", ".join(f"{k} {v}" for k, v in SO["verknuepfung"].items()),
          "", f"Typologie (Schätzung = {Y['schaetzung']}, Baujahr = {Y['baujahr']}); Kriterien " + ", ".join(f"{k} {v}" for k, v in Y["kriterien"].items()) + ".",
          f"- Stadt: Mehrfamilienhäuser {Y['stadt']['mfh']}, Kandidaten {Y['stadt']['blok']} ({proz(Y['stadt']['blok'], Y['stadt']['mfh'])}), in Großsiedlungen {Y['stadt']['osiedle']} ({proz(Y['stadt']['osiedle'], Y['stadt']['mfh'])})",
          "- Anteile je Stadtteil, wie die Karte sie färbt (Kandidaten / Mehrfamilienhäuser, Stufen 10/20/30/40 %):"]
    for nr, d in sorted(TD.items()):
        j = SL["liste"]["je_dzielnica"].get(nr, {})
        z.append(f"  - {nr}: ZBK-Einträge {j.get('n', 0)}, Punkte {sum(1 for x in P if x['properties']['st'] == nr)}, Mehrfamilienhäuser {d['mfh']}, Kandidaten {d['blok']} ({proz(d['blok'], d['mfh'])}), Großsiedlung {d['osiedle']} ({proz(d['osiedle'], d['mfh'])})")
    z += [f"  - Einträge außerhalb Krakaus (poza): {SL['liste']['je_dzielnica'].get('poza', {}).get('n', 0)}",
          f"- Summen: Kandidaten je Stadtteil {sum(d['blok'] for d in TD.values())} (Stadt {Y['stadt']['blok']}), Mehrfamilienhäuser je Stadtteil {sum(d['mfh'] for d in TD.values())} (Stadt {Y['stadt']['mfh']})",
          f"- Ortsmarke: in der Liste = {SL['ortsmarke']['in_liste']}, Art {SL['ortsmarke']['art']}, Eigentum {SL['ortsmarke']['eigentum']}, Stadtteil laut Liste {SL['ortsmarke']['st']}; Lage geprüft = {SO['ortsmarke']['lage_geprueft']}",
          f"- Literatur (nur bibliographisch): {Y['literatur']['autoren']}, {Y['literatur']['zeitschrift']} {Y['literatur']['band']} ({Y['literatur']['jahr']}) {Y['literatur']['artikel']}, DOI {Y['literatur']['doi']}"]
    PF = lade("planer_fuss_odbl.js")
    z += ["", "Bezug Erreichbarkeit in der Tabelle (`planer_fuss_odbl.js`, Wert der Kennzahl je Stadtteil):"]
    for nr in sorted(PF["raeume"]):
        w = {(x["kennzahl"], x["art"]): x["wert"] for x in PF["raeume"][nr]["werte"]}
        z.append(f"  - {nr}: Haltestelle Taktklasse I/II {w.get(('oepnv_takt', 'haltestelle_takt'))} %, Park {w.get(('gruen_in_radius', 'park'))} %")
    return "\n".join(z) + "\n"


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("--pruefen", action="store_true")
    o = a.parse_args()
    neu = erzeugen()
    if o.pruefen:
        alt = BELEG.read_text(encoding="utf-8") if BELEG.exists() else ""
        if alt == neu:
            print(f"  ok    {BELEG.relative_to(WURZEL)} entspricht den Datendateien")
            return 0
        print(f"  FEHLT {BELEG.relative_to(WURZEL)} ist nicht aktuell; python -I pruefen/S2_zaehlungen.py neu ausführen")
        return 1
    BELEG.write_text(neu, encoding="utf-8")
    print(f"{BELEG.relative_to(WURZEL)} geschrieben")
    return 0


if __name__ == "__main__":
    sys.exit(main())
