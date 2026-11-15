"""Abnahme OSM-Einrichtungen und Fußwegnetz gegen die Datenbank. Schreibt nichts außer TEMP-Tabellen.

Kriterien:
  1  auswertung.osm_poi hat keine Spalte für Namen, Adressen oder Kontakte
  2  Bericht berichte/osm_netz.md stammt aus einem echten Lauf (kein Trockenlauf), nennt die volle SHA256 der PBF,
     und diese steht in HERKUNFT.md neben der PBF (Rohdaten-Hash)
  3  Netz zusammenhängend: größte Komponente ≥ 95 % der Knoten im Stadtgebiet, und der Bericht nennt den Anteil
  4  jede Tabelle mit OSM-Anteil hat den Kommentar ODbL
  Hinweise (kein Kriterium, solange die Daten fehlen): Abstand der bewohnten Zellmittelpunkte zum Netz (braucht die
  Zelltabelle), Abgleich mit einer amtlichen Liste (braucht die Liste)

Aufruf: skripte/12_osm.sh pruefen --pbf PBF [--bericht berichte/osm_netz.md]
Ausgang 0 nur, wenn alle Kriterien erfüllt sind.
"""
from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
osm = importlib.import_module("12_osm")

OSM_TABELLEN = ("osm_poi", "netz_knoten", "netz_kante")
MIN_ANTEIL = 0.95


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pbf", type=Path, required=True, help="die geladene PBF (für den Abgleich der SHA256)")
    ap.add_argument("--bericht", type=Path, default=WURZEL / "berichte" / "osm_netz.md")
    a = ap.parse_args()
    ergebnisse: list[tuple[bool, str, str]] = []
    with osm.verbinden() as conn, conn.cursor() as cur:
        cur.execute(osm.PUFFER_SQL)
        # 1. keine Spalte name (auch keine Adress- oder Kontaktspalte)
        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_schema = 'auswertung' AND table_name = 'osm_poi' ORDER BY ordinal_position""")
        spalten = [r[0] for r in cur.fetchall()]
        verboten = [s for s in spalten if re.search(r"name|addr|adresse|strasse|ulica|phone|telefon|mail|website", s)]
        ergebnisse.append((not verboten, "auswertung.osm_poi hat keine Spalte name",
                           f"Spalten: {', '.join(spalten)}"))
        # 2. Rohdaten-Hash: Bericht, PBF und HERKUNFT.md stimmen überein
        text = a.bericht.read_text(encoding="utf-8") if a.bericht.is_file() else ""
        summe = osm.sha256(a.pbf) if a.pbf.is_file() else None
        hk = a.pbf.parent / "HERKUNFT.md"
        hk_text = hk.read_text(encoding="utf-8") if hk.is_file() else ""
        ok2 = bool(text and summe and f"SHA256: `{summe}`" in text and summe in hk_text and "TROCKENLAUF" not in text)
        beleg2 = (f"{a.bericht.name}: {'vorhanden' if text else 'fehlt'}; SHA256 der PBF {summe or 'PBF fehlt'}; "
                  f"im Bericht {'ja' if summe and summe in text else 'nein'}; in {hk.name} "
                  f"{'ja' if summe and summe in hk_text else 'nein'}"
                  + ("; Bericht stammt aus einem Trockenlauf" if "TROCKENLAUF" in text else ""))
        ergebnisse.append((ok2, "Rohdaten-Hash in Bericht und HERKUNFT.md gleich der PBF", beleg2))
        # 3. Netz zusammenhängend, Anteil im Bericht
        kz = osm.kennzahlen(cur)
        im_bericht = re.search(r"Anteil der größten Komponente (\d+,\d) %", text)
        if kz.get("knoten", 0) == 0:
            ergebnisse.append((False, f"größte Komponente ≥ {MIN_ANTEIL:.0%} der Knoten im Stadtgebiet", "Netz leer"))
        else:
            ergebnisse.append((kz["anteil_groesste_komponente"] >= MIN_ANTEIL and bool(im_bericht),
                               f"größte Komponente ≥ {MIN_ANTEIL:.0%} der Knoten im Stadtgebiet, Anteil im Bericht",
                               (f"{kz['groesste_komponente_im_stadtgebiet']} von {kz['knoten_im_stadtgebiet']} "
                                f"({100 * kz['anteil_groesste_komponente']:.2f} %), {kz['komponenten']} Komponenten; "
                                f"Bericht: {im_bericht.group(1) + ' %' if im_bericht else 'Anteil fehlt'}")))
        # 4. ODbL-Kommentar
        fehlt = []
        for t in OSM_TABELLEN:
            cur.execute("SELECT obj_description(%s::regclass, 'pg_class')", (f"auswertung.{t}",))
            if "ODbL" not in (cur.fetchone()[0] or ""):
                fehlt.append(t)
        ergebnisse.append((not fehlt, "jede Tabelle mit OSM-Anteil hat den Kommentar ODbL",
                           "alle drei" if not fehlt else f"fehlt: {', '.join(fehlt)}"))
        conn.rollback()
    hinweise = []
    if "zellen_grund" in kz:
        hinweise.append(f"Abstand Zelle → Netz: nicht prüfbar, {kz['zellen_grund']}")
    elif kz.get("knoten"):
        hinweise.append(f"Abstand Zelle → Netz: {kz['zellen_le_150m']} von {kz['bewohnte_zellen']} bewohnten Zellen "
                        f"≤ 150 m ({100 * kz['anteil_zellen_le_150m']:.2f} %)")
    if "nicht geprüft" in text:
        hinweise.append("Abgleich mit amtlicher Liste: nicht geprüft (siehe Bericht)")
    for ok, was, beleg in ergebnisse:
        print(f"{'✓' if ok else '✗'} {was}: {beleg}")
    for h in hinweise:
        print(f"· Hinweis: {h}")
    return 0 if all(ok for ok, _w, _b in ergebnisse) else 1


if __name__ == "__main__":
    sys.exit(main())
