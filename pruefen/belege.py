"""Prüfung Belegschicht: Die gemeinsamen Dokumente stimmen in sich und mit den Dateien überein.

Liest nur Dateien im Repo (kein Netz, keine Datenbank). Streng geprüft (Befund) wird, was die Belegschicht selbst
schreibt:
  1. belege/README.md: Jede Datei, die die Tabelle nennt, existiert. Jedes Prüfprotokoll unter belege/
     (pruefstand-*/, gegenprobe_*) steht in der Tabelle.
  2. Angegebene Zahlen stimmen: „N Prüfungen, G grün, … U übersprungen“ in einer Zeile zu einem Prüfstand gegen die
     Zählung am Ende von dessen pruefen.log; „N Dateien“ in einer Zeile zu einer rohdaten*.sha256 gegen deren Zeilen.
  3. README-Kasten „Do weryfikacji / Zur Prüfung“ nennt einen Prüfstand belege/pruefstand-<datum>-<commit>/pruefen.log;
     er existiert, seine Zählung hat 0 mit Befund, der Arbeitsstand war sauber und der Commit im Ordnernamen ist der
     Commit im Protokoll.
  4. docs/entscheidungen.md: Die Übersicht nennt genau die KR-Nummern, die einen Abschnitt „## KRn:“ haben, lückenlos
     ab KR1; jeder Abschnitt hat die Punkte Anlass, Entscheidung, Begründung, Verworfen, Neu prüfen, wenn.
  5. Meldeweg: meldeweg aus config/krakow.yaml steht gleich in CITATION.cff (contact) und README.md.
  6. docs/checkliste.md: Punkte 1 bis 36, L1 bis L10 und Z1 bis Z5 je genau einmal; jede Zeile mit Status aus
     erfüllt / teilweise / offen / entfällt und mit Beleg; jede Datei in Backticks der Belegspalte existiert; eine
     Zeile „erfüllt“ nennt mindestens eine vorhandene Datei.
Nur als Hinweis (mit --veroeffentlichung ein Befund) gelten Lieferungen der Pakete, die noch nicht übernommen sind:
  7. quellen-<paket>.md im Wurzelordner, die QUELLEN.md nicht nennt; Dateien unter belege/ außer den Prüfprotokollen,
     die belege/README.md nicht nennt; pruefen/<paket>_protokoll.md, die belege/README.md nicht nennt;
     docs/entscheidungen/<paket>.md, die docs/entscheidungen.md nicht nennt.
  So bleibt pruefen.sh beim Merge eines Pakets grün, und die Hinweise sind die Liste zum Einsammeln.

Aufruf: python -I pruefen/belege.py [--veroeffentlichung]   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt Skriptverzeichnisse weg
import ort_konfig  # noqa: E402

VEROEFFENTLICHUNG = "--veroeffentlichung" in sys.argv
STATUS = ("erfüllt", "teilweise", "offen", "entfällt")
LABEL = ("Anlass", "Entscheidung", "Begründung", "Verworfen", "Neu prüfen, wenn")
ZAEHLUNG = re.compile(r"== Zählung: (\d+) Prüfungen, (\d+) grün, (\d+) mit Befund, (\d+) übersprungen")
befunde: list[str] = []
hinweise: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def hinweis(text: str) -> None:
    if VEROEFFENTLICHUNG:
        pruef(False, text)
    else:
        print("  Hinweis " + text)
        hinweise.append(text)


def lesen(rel: str) -> str:
    return (WURZEL / rel).read_text(encoding="utf-8")


def zeilen(text: str) -> list[list[str]]:
    """Tabellenzeilen einer Markdown-Datei als Zellen (ohne Kopf- und Trennzeilen)."""
    aus = []
    for z in text.splitlines():
        if z.startswith("|") and not re.match(r"^\|[\s|:-]+\|$", z):
            aus.append([c.strip() for c in z.strip().strip("|").split("|")])
    return aus


def pfade(zelle: str) -> list[str]:
    """Dateiangaben in Backticks: erstes Wort, mit / oder Dateiendung, ohne Platzhalter <…> und Muster *."""
    aus = []
    for b in re.findall(r"`([^`]+)`", zelle):
        w = b.split()[0] if b.split() else ""
        w = w.removeprefix("./").rstrip(",;")
        if not w or "<" in w or "*" in w or "$" in w or w.startswith("-"):
            continue
        if "/" in w or re.search(r"\.(md|py|sh|mjs|js|json|yaml|cff|html|log|sha256|txt|in)$", w) or w in ("LICENSE", "NOTICE"):
            aus.append(w)
    return aus


def zaehlung(log: Path) -> tuple[int, int, int, int] | None:
    m = None
    for z in log.read_text(encoding="utf-8").splitlines():
        m = ZAEHLUNG.search(z) or m
    return tuple(int(x) for x in m.groups()) if m else None


def belege_readme() -> str:
    print("belege/README.md gegen die Dateien unter belege/")
    text = lesen("belege/README.md")
    genannt = {}
    for c in zeilen(text):
        for p in pfade(c[0]):
            genannt[p] = c
    for p, c in sorted(genannt.items()):
        pruef((WURZEL / "belege" / p).is_file(), f"belege/{p} existiert")
        rest = " ".join(c[1:])
        m = re.search(r"(\d+) Prüfungen, (\d+) grün,(?: (\d+) (?:mit Befund|Befund),)? (\d+) übersprungen", rest)
        if p.startswith("pruefstand-") and (WURZEL / "belege" / p).is_file():
            z = zaehlung(WURZEL / "belege" / p)
            if m and z:
                n, g, b, u = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0), int(m.group(4))
                pruef((n, g, b, u) == z, f"belege/{p}: Angabe {n}/{g}/{b}/{u} = Zählung im Protokoll {z[0]}/{z[1]}/{z[2]}/{z[3]} (Prüfungen/grün/Befund/übersprungen)")
            else:
                pruef(z is not None, f"belege/{p}: Zählung im Protokoll vorhanden")
        if p.endswith(".sha256") and (WURZEL / "belege" / p).is_file():
            m2 = re.search(r"(\d+) Dateien", rest)
            n_zeilen = sum(1 for z in (WURZEL / "belege" / p).read_text(encoding="utf-8").splitlines() if z.strip())
            pruef(bool(m2) and int(m2.group(1)) == n_zeilen, f"belege/{p}: Angabe „{m2.group(0) if m2 else 'ohne Zahl'}“ = {n_zeilen} Zeilen")
    for f in sorted(p for p in (WURZEL / "belege").rglob("*") if p.is_file() and p.name != "README.md"):
        rel = str(f.relative_to(WURZEL / "belege"))
        if rel in genannt:
            continue
        if rel.startswith("pruefstand-") or rel.startswith("gegenprobe_"):
            pruef(False, f"belege/{rel} steht nicht in belege/README.md")
        else:
            hinweis(f"belege/{rel} noch nicht in belege/README.md übernommen")
    for f in sorted((WURZEL / "pruefen").glob("*_protokoll.md")):
        if f"pruefen/{f.name}" not in text:
            hinweis(f"pruefen/{f.name} noch nicht in belege/README.md übernommen")
    return text


def kasten() -> None:
    print("README-Kasten nennt einen grünen Prüfstand")
    t = lesen("README.md")
    teil = t.split("## Do weryfikacji / Zur Prüfung", 1)
    if not pruef(len(teil) == 2, "README.md hat den Abschnitt „Do weryfikacji / Zur Prüfung“"):
        return
    abschnitt = teil[1].split("\n## ", 1)[0]
    m = re.search(r"belege/(pruefstand-(\d{8})-([0-9a-f]{7,40}))/pruefen\.log", abschnitt)
    if not pruef(bool(m), "Kasten nennt belege/pruefstand-<datum>-<commit>/pruefen.log"):
        return
    log = WURZEL / "belege" / m.group(1) / "pruefen.log"
    if not pruef(log.is_file(), f"{log.relative_to(WURZEL)} existiert"):
        return
    inhalt = log.read_text(encoding="utf-8")
    z = zaehlung(log)
    pruef(bool(z) and z[2] == 0, f"Prüfstand {m.group(1)}: 0 mit Befund (Zählung {z})")
    pruef("Arbeitsstand: sauber" in inhalt, f"Prüfstand {m.group(1)}: Arbeitsstand sauber")
    c = re.search(r"^Commit: ([0-9a-f]{40})", inhalt, re.M)
    pruef(bool(c) and c.group(1).startswith(m.group(3)), f"Prüfstand {m.group(1)}: Commit im Ordnernamen = Commit im Protokoll")
    d = m.group(2)
    pruef(f"{d[6:8]}.{d[4:6]}.{d[0:4]}" in abschnitt, f"Kasten nennt das Datum des Prüfstands ({d[6:8]}.{d[4:6]}.{d[0:4]})")


def entscheidungen() -> str:
    print("docs/entscheidungen.md: Übersicht gegen Abschnitte")
    t = lesen("docs/entscheidungen.md")
    uebersicht = {int(c[0][2:]) for c in zeilen(t) if re.fullmatch(r"KR\d+", c[0])}
    abschnitte = [int(x) for x in re.findall(r"^## KR(\d+):", t, re.M)]
    pruef(len(abschnitte) == len(set(abschnitte)), f"{len(abschnitte)} Abschnitte, keiner doppelt")
    pruef(uebersicht == set(abschnitte), f"Übersicht KR{sorted(uebersicht)} = Abschnitte KR{sorted(set(abschnitte))}")
    pruef(set(abschnitte) == set(range(1, max(abschnitte, default=0) + 1)), "Nummern lückenlos ab KR1")
    teile = re.split(r"^(?=## )", t, flags=re.M)
    ohne = []
    for s in teile:
        m = re.match(r"## (KR\d+):", s)
        if m:
            fehlt = [l for l in LABEL if f"- **{l}:**" not in s]
            if fehlt:
                ohne.append(f"{m.group(1)} ohne {', '.join(fehlt)}")
    pruef(not ohne, f"jeder Eintrag mit {', '.join(LABEL)}" + (f" ({'; '.join(ohne)})" if ohne else ""))
    for f in sorted((WURZEL / "docs" / "entscheidungen").glob("*.md")):
        if f.name != "README.md" and f"docs/entscheidungen/{f.name}" not in t:
            hinweis(f"docs/entscheidungen/{f.name} noch nicht in docs/entscheidungen.md übernommen")
    return t


def meldeweg() -> None:
    print("Meldeweg überall gleich")
    m = ort_konfig.lade().get("meldeweg")
    if not pruef(isinstance(m, str) and "@" in m, f"config: meldeweg = {m}"):
        return
    cit = lesen("CITATION.cff")
    mails = re.findall(r"^\s*email:\s*(\S+)", cit, re.M)
    pruef(mails == [m], f"CITATION.cff contact email {mails} = {m}")
    pruef(m in lesen("README.md"), f"README.md nennt {m}")
    pruef("{{meldeweg}}" in lesen("vorlagen/_rahmen.html"), "Seitenfuß (vorlagen/_rahmen.html) setzt {{meldeweg}} ein")


def checkliste() -> None:
    print("docs/checkliste.md: Punkte, Status, Belege")
    t = lesen("docs/checkliste.md")
    soll = [str(i) for i in range(1, 37)] + [f"L{i}" for i in range(1, 11)] + [f"Z{i}" for i in range(1, 6)]
    gesehen: dict[str, int] = {}
    fehlend_pfad = []
    fehler = []
    for c in zeilen(t):
        if c[0] not in soll:
            continue
        gesehen[c[0]] = gesehen.get(c[0], 0) + 1
        if len(c) != 4:
            fehler.append(f"{c[0]}: {len(c)} Spalten statt 4")
            continue
        status, beleg = c[2], c[3]
        if not status.startswith(STATUS):
            fehler.append(f"{c[0]}: Status „{status[:20]}“")
        if not beleg:
            fehler.append(f"{c[0]}: ohne Beleg")
        ps = pfade(beleg)
        da = [p for p in ps if (WURZEL / p).exists()]
        fehlend_pfad += [f"{c[0]}: {p}" for p in ps if p not in da]
        if status.startswith("erfüllt") and not da:
            fehler.append(f"{c[0]}: erfüllt ohne vorhandene Datei im Beleg")
    doppelt = [k for k, n in gesehen.items() if n > 1]
    fehlt = [k for k in soll if k not in gesehen]
    pruef(not fehlt and not doppelt, f"{len(soll)} Punkte je genau einmal" + (f" (fehlt {fehlt}, doppelt {doppelt})" if fehlt or doppelt else ""))
    pruef(not fehler, "jede Zeile mit Status und Beleg, erfüllt nur mit vorhandener Datei" + (f": {fehler}" if fehler else ""))
    pruef(not fehlend_pfad, "jede Datei der Belegspalte existiert" + (f": {fehlend_pfad}" if fehlend_pfad else ""))
    n = {s: sum(1 for c in zeilen(t) if c[0] in soll and len(c) == 4 and c[2].startswith(s)) for s in STATUS}
    print("  Stand: " + ", ".join(f"{v} {k}" for k, v in n.items()))


def quellen() -> None:
    print("Lieferungen quellen-<paket>.md")
    t = lesen("QUELLEN.md")
    for f in sorted(WURZEL.glob("quellen-*.md")):
        if f.name not in t:
            hinweis(f"{f.name} noch nicht in QUELLEN.md übernommen")


def main() -> int:
    belege_readme()
    kasten()
    entscheidungen()
    meldeweg()
    checkliste()
    quellen()
    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde", end="")
    print(f", {len(hinweise)} Hinweis(e) zum Einsammeln" if hinweise else "")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
