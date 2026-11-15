"""Prüfung ohne Browser: Das Abzeichen „Beispieldaten“ (Klasse fl-beispiel) steht nie fest im Seiten-HTML.

Ob eine Ebene Beispieldaten zeigt, steht allein in ihrer Datendatei (Feld "fixture": true). Die Seitenmodule setzen
das Abzeichen zur Laufzeit aus diesem Feld (karta.js, Legende und Popup). Ein fest in einer Vorlage stehendes
Abzeichen bliebe stehen, wenn die Daten längst echt sind, und würde echte Werte als erfunden ausgeben.

Prüft:
  1. Keine Vorlage unter vorlagen/ und keine erzeugte Seite (Wurzelordner und Sprachordner) trägt die Klasse
     fl-beispiel im Markup.
  2. Zählung der Datendateien mit "fixture":true zur Auskunft (kein Befund, die Kennzeichnung ist dort gewollt).

Aufruf: python -I pruefen/beispielmarke.py   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt Skriptverzeichnisse weg
import ort_konfig  # noqa: E402

MUSTER = re.compile(r"""class\s*=\s*["'][^"']*\bfl-beispiel\b""")


def main() -> int:
    sprachen = ort_konfig.lade()["sprachen"]
    dateien = sorted((WURZEL / "vorlagen").glob("*.html")) + sorted(WURZEL.glob("*.html"))
    for lang in sprachen[1:]:
        dateien += sorted((WURZEL / lang).glob("*.html"))
    befunde = []
    for d in dateien:
        for nr, zeile in enumerate(d.read_text(encoding="utf-8").splitlines(), 1):
            if MUSTER.search(zeile):
                befunde.append(f"{d.relative_to(WURZEL)}:{nr}")
    mit_fixture = [d.name for d in sorted((WURZEL / "daten").glob("*.js"))
                   if '"fixture":true' in d.read_text(encoding="utf-8")]
    print(f"  {len(dateien)} Vorlagen und Seiten geprüft, {len(befunde)} mit festem Abzeichen")
    for b in befunde:
        print(f"  FEHLT  festes Abzeichen fl-beispiel in {b} (Abzeichen nur aus dem Feld fixture der Daten setzen)")
    print(f"  Datendateien mit \"fixture\":true: {', '.join(mit_fixture) if mit_fixture else 'keine'}")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
