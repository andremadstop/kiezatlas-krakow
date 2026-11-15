"""Prüfung Gerüst: Ortskonfiguration, Rechen-SRID in der DDL, keine internen Plankennungen in Auslieferungen.

Liest nur Dateien im Repo (kein Netz, keine Datenbank). Prüft:
  1. config/krakow.yaml (bzw. $KIEZ_CONFIG) lesbar, rechen_srid zugelassen (skripte/ort_konfig.py).
  2. Jede metrische SRID in sql/*.sql (geometry(…, N) und ST_Transform(…, N)) ist gleich rechen_srid.
     Erlaubt sind daneben nur 4326 (WGS 84, Vorgabe der Pipeline) und 3035 (INSPIRE-Gitter).
  3. In keinem Python-Skript unter skripte/ und pruefen/ steht noch eine feste metrische SRID (25833, 2178,
     2180, 25834) außerhalb von skripte/ort_konfig.py.
  4. Keine internen Plankennungen (P0, D3, DF, S2, N1, KR1, „Tor M“ …) in ausgelieferten Dateien: erzeugte Seiten (*.html im
     Wurzelordner und in den Sprachordnern), vorlagen/, texte/, *.js und *.css im Wurzelordner, daten/**/*.js.

Aufruf: python -I pruefen/geruest.py   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # ort_konfig; python -I lässt Skriptverzeichnisse weg
import ort_konfig  # noqa: E402

FREI = {4326, 3035}
METRISCH = ("25833", "2178", "2180", "25834")
# Plankennungen: Phasen P0 …, Datenpakete D1 … und DF, DK, DS, DW, DZ, Seitenpakete S1 bis S4, Nacharbeiten N1 …,
# Entscheidungen KR1 …, „Tor M“. Nicht dabei: DE (Kürzel des Sprachschalters), und weil sie in Kraków echte Namen
# sind, A1 … (Autobahnen, etwa A4),
# S7 und S52 (Schnellstraßen; S5 und höher fallen deshalb nicht unter die Seitenpakete), DK 79 (Landesstraßen, nur mit
# Leerzeichen und Zahl). DK, DS, DW und DZ zählen nur ohne folgende Zahl.
KENNUNG = re.compile(r"\b(?:P[0-9]|D[0-9]{1,2}|D[FKSWZ](?!\s?[0-9])|S[1-4]|N[0-9]|KR[0-9]+|Tor M)\b")
befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def auslieferung() -> list[Path]:
    sprachen = ort_konfig.lade().get("sprachen", [])
    dateien = sorted(WURZEL.glob("*.html"))
    for s in sprachen[1:]:
        dateien += sorted((WURZEL / s).glob("*.html"))
    for ordner in ("vorlagen", "texte"):
        dateien += sorted(p for p in (WURZEL / ordner).rglob("*") if p.is_file())
    dateien += sorted([*WURZEL.glob("*.js"), *WURZEL.glob("*.css")])
    dateien += sorted(p for p in (WURZEL / "daten").rglob("*.js"))
    return dateien


def main() -> int:
    srid = ort_konfig.RECHEN_SRID
    print(f"Ortskonfiguration {ort_konfig.pfad().relative_to(WURZEL) if ort_konfig.pfad().is_relative_to(WURZEL) else ort_konfig.pfad()}")
    pruef(True, f"rechen_srid = {ort_konfig.srs_name()}")

    print("Rechen-SRID in sql/")
    for p in sorted((WURZEL / "sql").glob("*.sql")):
        text = p.read_text(encoding="utf-8")
        gefunden = [int(x) for x in re.findall(r"geometry\(\s*\w+\s*,\s*(\d+)\s*\)", text, re.I)]
        gefunden += [int(x) for x in re.findall(r"ST_Transform\([^;]*?,\s*(\d{4,5})\s*\)", text, re.I)]
        falsch = sorted({s for s in gefunden if s not in FREI and s != srid})
        pruef(not falsch, f"{p.name}: {len(gefunden)} SRID-Angaben, metrische = {srid}"
              + (f" (abweichend: {falsch})" if falsch else ""))

    print("Keine feste metrische SRID in Python-Skripten")
    fest = []
    for p in sorted([*(WURZEL / "skripte").glob("*.py"), *(WURZEL / "pruefen").glob("*.py")]):
        if p.name in ("ort_konfig.py", "geruest.py"):
            continue
        for i, zeile in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            code = zeile.split("#", 1)[0]
            if any(re.search(rf"(?<![\d.]){s}(?![\d])", code) for s in METRISCH):
                fest.append(f"{p.relative_to(WURZEL)}:{i}")
    pruef(not fest, f"skripte/ und pruefen/ ohne 25833/2178/2180/25834 im Code (Treffer: {fest[:6]})")

    print("Keine internen Plankennungen in ausgelieferten Dateien")
    treffer = []
    dateien = auslieferung()
    for p in dateien:
        for i, zeile in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            m = KENNUNG.search(zeile)
            if m:
                treffer.append(f"{p.relative_to(WURZEL)}:{i} „{m.group(0)}“")
    pruef(not treffer, f"{len(dateien)} Dateien ohne P0/D3/DF/S2/N1/KR1/„Tor M“" + (f" (Treffer: {treffer[:6]})" if treffer else ""))

    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
