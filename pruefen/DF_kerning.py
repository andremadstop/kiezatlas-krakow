"""Prüfung: Kerning der polnischen Sonderzeichen in den zusammengefügten Schriften unter fonts/ (fontTools, ohne Netz).

skripte/schriften.py fügt je Schnitt die Fontsource-Teilmengen „latin“ und „latin-ext“ zusammen. Kerning-Paare
gibt es nur innerhalb einer Teilmenge; ein Paar aus „Ł“ (latin-ext) und „a“ (latin) hat deshalb keinen Wert. Wie viel
davon sichtbar war, misst dieses Skript stellvertretend: Für jedes Paar aus einem der 16 Zeichen aus Latin
Extended-A (ąćęłńśźżĄĆĘŁŃŚŹŻ) und einem Buchstaben a–z, A–Z (beide Reihenfolgen) wird der Kerning-Wert in der
zusammengefügten Datei gelesen und mit dem Wert des Grundbuchstabens verglichen (Ł→L, ż→z, Ś→S …). Barlow kerne
Akzentbuchstaben in der Regel wie ihren Grundbuchstaben (gleiche Klasse); weicht der Wert ab, ist das ein Hinweis
auf ein verlorenes Paar, kein Beweis. Seit der Auflage zu KR30 (14.11.2026) überträgt skripte/schriften.py die
Paare der Grundbuchstaben auf die polnischen Zeichen; diese Prüfung misst, dass die Lücke geschlossen bleibt.

Gezählt werden:
  1. Paare über die Teilmengen hinweg mit einem Wert ungleich 0 (vor der Übertragung 0, danach je Schrift einige
     hundert; nur zur Information);
  2. Paare, deren Grundpaar einen Wert hat (|Wert| ≥ 1 Einheit) und deren polnisches Paar keinen (erwartet 0);
  3. davon die mit |Wert| ≥ 20 Einheiten (bei 1000 Einheiten je Geviert und 32 px Schriftgrad 0,64 px).

Aufruf:
    uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
        --with-requirements requirements-schriften.txt python -I pruefen/DF_kerning.py
Rückgabe 0, wenn in keiner Schrift ein polnisches Paar fehlt (Zählung 2 = 0), sonst 1; Ausgabe ist die Zählung für
belege/DF_schriften_grundkarte.md. Läuft in pruefen.sh ohne Browser; im Browser prüft pruefen/N2_auslieferung.mjs
(Teil 4) zusätzlich die gesetzte Breite.
"""
from __future__ import annotations

import string
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

WURZEL = Path(__file__).resolve().parent.parent
EXT_A = "ąćęłńśźżĄĆĘŁŃŚŹŻ"
GRUND = dict(zip(EXT_A, "acelnszzACELNSZZ"))
LATEIN = string.ascii_letters


def paarwerte(font: TTFont):
    """Liefert eine Funktion (links, rechts) -> XAdvance aus allen PairPos-Lookups des Features kern."""
    gpos = font["GPOS"].table
    lookups = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            lookups.update(fr.Feature.LookupListIndex)
    tabellen = []
    for i in sorted(lookups):
        lk = gpos.LookupList.Lookup[i]
        for st in lk.SubTable:
            if lk.LookupType == 9:
                if st.ExtensionLookupType != 2:
                    continue
                st = st.ExtSubTable
            elif lk.LookupType != 2:
                continue
            tabellen.append(st)

    def wert(l: str, r: str) -> int:
        for st in tabellen:
            abd = st.Coverage.glyphs
            if l not in abd:
                continue
            if st.Format == 1:
                ps = st.PairSet[abd.index(l)]
                for pv in ps.PairValueRecord:
                    if pv.SecondGlyph == r:
                        return getattr(pv.Value1, "XAdvance", 0) or 0
            elif st.Format == 2:
                k1 = st.ClassDef1.classDefs.get(l, 0)
                k2 = st.ClassDef2.classDefs.get(r, 0)
                v = st.Class1Record[k1].Class2Record[k2].Value1
                x = getattr(v, "XAdvance", 0) if v else 0
                if x:
                    return x
        return 0
    return wert


def main() -> int:
    dateien = sorted((WURZEL / "fonts").glob("*.woff2"))
    print(f"Kerning der polnischen Sonderzeichen, {len(dateien)} Schriften unter fonts/")
    summe = 0
    for d in dateien:
        f = TTFont(d)
        cmap = f.getBestCmap()
        upm = f["head"].unitsPerEm
        w = paarwerte(f)
        quer = verloren = gross = 0
        beispiele = []
        for p in EXT_A:
            for b in LATEIN:
                for l, r, gl, gr in ((p, b, GRUND[p], b), (b, p, b, GRUND[p])):
                    v = w(cmap[ord(l)], cmap[ord(r)])
                    g = w(cmap[ord(gl)], cmap[ord(gr)])
                    if v:
                        quer += 1
                    if g and not v:
                        verloren += 1
                        if abs(g) >= 20:
                            gross += 1
                            beispiele.append((abs(g), f"{l}{r} (wie {gl}{gr}: {g})"))
        beispiele.sort(reverse=True)
        summe += verloren
        n = len(EXT_A) * len(LATEIN) * 2
        print(f"{d.name}: {upm} Einheiten je Geviert, {n} Paare gemessen; über die Teilmengen mit Wert: {quer}; "
              f"Grundpaar mit Wert, polnisches Paar ohne: {verloren}, davon |Wert| ≥ 20: {gross}")
        if beispiele:
            print("    größte: " + ", ".join(t for _, t in beispiele[:8]))
    if not dateien:
        print("keine Schriften unter fonts/")
        return 1
    print(f"polnische Paare ohne Wert des Grundpaars, alle Schriften: {summe} ({'Lücke geschlossen' if summe == 0 else 'BEFUND'})")
    return 1 if summe else 0


if __name__ == "__main__":
    sys.exit(main())
