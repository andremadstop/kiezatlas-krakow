"""Erreichbarkeit je Zelle in Kraków: Luftlinie vom Zellmittelpunkt zur nächsten Einrichtung je Art.

Kein Netz, keine Datenbank. Regeln vor dem Lauf: pruefen/D6_protokoll.md (Regeln 11 und 12). Fußweg erst mit dem
Netz des Pakets OSM und Fußwegnetz, dann in daten/erreichbar_fuss_odbl.js (nicht dieses Skript).

Eingang:  daten/zellen_odbl.js      Zellen mit Einwohnern; gelesen werden nur Kennung, Einwohner und Quadrat (Eurostat),
                                    nicht die Zuordnung st (die beruht auf den OSM-Grenzen). Die Zellen sind genau die
                                    mit Mittelpunkt in der BDOT10k-Stadtgrenze (belege/D4_bevoelkerung.md, Schritt 4)
          daten/einrichtungen.js    aus skripte/11_einrichtungen_krakow.py (BDOT10k)
          daten/haltestellen.js     aus skripte/13_oepnv_krakow.py; Ziel „haltestelle_takt“ = Taktklassen aus
                                    config/richtwerte.yaml, planer.oepnv_klassen
Ausgang:  daten/erreichbar.js       (KIEZ_ERREICHBAR, Vertrag daten/schema/erreichbar.json)
          belege/D6_erreichbarkeit.md

Werte in der Reihenfolge von daten/zellen_odbl.js (Schlüssel „zellen.js-Reihenfolge“ laut Vertrag), in m, auf planer.rundung_entfernung_m gerundet; unbewohnte Zellen
(ew 0 oder fehlt) = null. Liest die Datei eine Beispieldatei, ist die Ausgabe selbst eine Beispieldatei (Regel 12).

Aufruf:
    uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
        python -I skripte/14_erreichbarkeit_krakow.py [--pruefen]
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import versorgung_werkzeug as vw  # noqa: E402

AUS_JS = vw.DATEN / "erreichbar.js"
AUS_BELEG = vw.WURZEL / "belege" / "D6_erreichbarkeit.md"


def rechnen() -> tuple[str, str]:
    rw = yaml.safe_load(ort_konfig.RICHTWERTE.read_text(encoding="utf-8"))
    pl, q = rw["planer"], rw["quellen"]
    stand, rund = str(rw["stand"]), int(pl["rundung_entfernung_m"])
    zinhalt, zellen = vw.zellen_lesen()
    ein = vw.js_lesen(vw.DATEN / "einrichtungen.js")
    hst = vw.js_lesen(vw.DATEN / "haltestellen.js")
    eingaben = {"zellen_odbl.js": zinhalt, "einrichtungen.js": ein, "haltestellen.js": hst}
    beispiel = sorted(n for n, d in eingaben.items() if d.get("fixture") is True)
    ziele = vw.ziele_je_art(ein, hst, list(pl["oepnv_klassen"]))
    arten = list(ziele)
    mitten = [z["mitte_r"] for z in zellen]
    bewohnt = [bool(z["ew"]) for z in zellen]

    werte = {}
    for a in arten:
        d = vw.naechste(ziele[a], mitten)
        werte[a] = [None if (not b or x is None) else int(round(x / rund) * rund) for x, b in zip(d, bewohnt)]

    ids = [z["id"] for z in zellen]
    inhalt = {"stand": stand, "methode": "luftlinie", "einheit": "m",
              "quellen": {k: {kk: q[k][kk] for kk in ("quelle", "lizenz", "vermerk", "url")} | {"stand": stand}
                          for k in ("bdot10k", "ztp")},
              "arten": arten, "anzahl": len(ids), "erste_id": ids[0], "letzte_id": ids[-1],
              "schluessel": "zellen.js-Reihenfolge", "werte": werte, "bezug": "zellmittelpunkt",
              "taktklassen": list(pl["oepnv_klassen"]), "vorbehalte": ["eigene_klassifikation_takt"]}
    if beispiel:
        inhalt = {"fixture": True, "beispiel_eingaben": beispiel, **inhalt}
    kopf = ("Beispieldaten (Fixture): Zellen unecht. " if beispiel else "") + \
        "Erreichbarkeit je Zelle (Luftlinie), erzeugt von skripte/14_erreichbarkeit_krakow.py."
    js = vw.js_text("KIEZ_ERREICHBAR", inhalt, kopf)

    T = vw.tausender
    b = ["# Beleg Erreichbarkeit je Zelle (Luftlinie)", "",
         "Erzeugt von `skripte/14_erreichbarkeit_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). "
         "Regeln vor dem Lauf: `pruefen/D6_protokoll.md`, Regeln 11 und 12.", ""]
    if beispiel:
        b += ["> **Beispieldaten-Lauf.** " + ", ".join(f"`daten/{n}`" for n in beispiel) + " trägt `fixture: true`. "
              "Die Zählungen unten belegen nur, dass das Skript läuft; sie sind keine Aussage über Kraków und dürfen "
              "nicht zitiert werden. `daten/erreichbar.js` trägt deshalb selbst `fixture: true`.", ""]
    b += ["## Eingaben", "",
          f"- Zellen: {T(len(zellen))}, davon bewohnt (ew > 0): {T(sum(bewohnt))}",
          f"- Ziele je Art (Einrichtungen mit strittiger Lage zählen nicht): "
          + ", ".join(f"`{a}` {T(len(ziele[a]))}" for a in arten), "",
          f"## Entfernungen bewohnter Zellen (m, auf {rund} m gerundet)", "",
          "| Art | Zellen mit Wert | Median | größter Wert |", "|---|---|---|---|"]
    for a in arten:
        v = [x for x in werte[a] if x is not None]
        b.append(f"| `{a}` | {T(len(v))} | {T(int(statistics.median(v))) if v else '–'} | {T(max(v)) if v else '–'} |")
    b += ["", "## Grenzen", "",
          "- Luftlinie, kein Fußweg: Flüsse (Wisła), Bahntrassen und Schnellstraßen sind nicht berücksichtigt. Der Fußweg "
          "folgt mit dem Netz des Pakets OSM und Fußwegnetz in `daten/erreichbar_fuss_odbl.js`.",
          "- Alle Einwohner einer Zelle stehen am Zellmittelpunkt (1-km-Gitter).",
          "- Nächste Einrichtung jeder Art, nicht die zuständige (Schulbezirke fehlen).",
          "- Einrichtungen außerhalb der Stadtgrenze fehlen in BDOT10k Powiat 1261; Zellen am Stadtrand werden dadurch "
          "zu weit gerechnet (nicht beziffert).", ""]
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
