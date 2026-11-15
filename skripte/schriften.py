"""Schriften unter fonts/ mit vollständigem Latin Extended-A (polnische Sonderzeichen) erzeugen.

Quelle: die npm-Pakete @fontsource/barlow und @fontsource/barlow-semi-condensed 5.3.0 (SIL OFL 1.1), abgerufen mit
skripte/abruf.py nach $KIEZ_DATEN/schriften/2026-11-13/ (HERKUNFT.md dort, Prüfsummen in
belege/rohdaten-DF-schriften.sha256). Fontsource teilt jede Schrift in Zeichenvorrats-Teilmengen; „latin“ enthält
von den 18 polnischen Sonderzeichen nur ó und Ó, „latin-ext“ die übrigen 16. Bis zu diesem Skript lagen unter
fonts/ genau die latin-Dateien (byte-gleich mit 5.3.0).

Das Skript prüft beide Pakete gegen die festgeschriebene SHA256 und gegen die sha512-Integrität aus den
Paketangaben der Registry, liest je Schnitt die latin- und die latin-ext-Datei (WOFF2) aus dem Paket, fügt sie mit
fontTools.merge zu einer Datei zusammen und schreibt sie unter dem bisherigen Namen nach fonts/. Damit bleiben
atlas.css, schaugrafik.js und der Export unverändert. Die Zeitstempel head.created und head.modified werden aus der latin-Datei
übernommen, damit die Ausgabe byte-gleich reproduzierbar ist. Daneben entsteht fonts/einbettung.js (Data-URIs für
die Schaugrafik) aus denselben Dateien.

Das Zusammenfügen ist eine Änderung im Sinne der OFL (erlaubt, kein Reserved Font Name in fonts/OFL.txt); die
Glyphen selbst bleiben unverändert. Kerning-Paare gibt es in den Teilmengen nur innerhalb jeder Teilmenge; ein Paar
aus „Ł“ (latin-ext) und „T“ (latin) hätte nach dem Zusammenfügen keinen Wert. Deshalb überträgt das Skript die
Kerning-Werte der Grundbuchstaben auf die polnischen Sonderzeichen (Ą←A, Ć←C, Ę←E, Ł←L, Ń←N, Ó←O, Ś←S, Ź←Z, Ż←Z, klein
ebenso; Auftrag der Projektleitung vom 14.11.2026, docs/entscheidungen.md KR30): Für jedes Paar aus einem dieser
Zeichen und einem beliebigen Zeichen der Schrift (beide Reihenfolgen, auch zwei Sonderzeichen nebeneinander) gilt der
Wert des Paars der Grundbuchstaben, aber nur, wenn das Paar selbst noch keinen Wert hat. Die übertragenen Paare stehen
in einem eigenen Lookup (PairPos), das allen Einträgen des Features „kern“ angehängt wird; vorhandene Lookups bleiben
unverändert. Gelesen werden die Werte so, wie ein Textsatzprogramm sie anwendet: je Lookup die erste Subtabelle, die
das Paar trifft, Summe über die Lookups.

Aufruf (fontTools und brotli mit Hashes in requirements-schriften.txt):
    uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
        --with-requirements requirements-schriften.txt python -I skripte/schriften.py [--pruefen]
Rückgabe 0 = geschrieben bzw. (mit --pruefen) byte-gleich, 1 = Befund.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import sys
import tarfile
from pathlib import Path

from fontTools.merge import Merger
from fontTools.otlLib.builder import buildPairPosGlyphs, buildValue
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables

WURZEL = Path(__file__).resolve().parent.parent
STAND = "2026-11-13"
# Prüfsummen beim Abruf (skripte/abruf.py, belege/rohdaten-DF-schriften.sha256), nicht von Hand ausgedacht
PAKETE = {
    "barlow": ("barlow-5.3.0.tgz", "8ad808291f807367d10eadf915791608bd04cc393882e7e86e290daeeadd843c",
               "npm-barlow-latest.json"),
    "barlow-semi-condensed": ("barlow-semi-condensed-5.3.0.tgz",
                              "94991ed2fc3fe0e11d8af5129932bdd94d29b6a7355859ebfba9a19d6610cc77",
                              "npm-barlow-semi-condensed-latest.json"),
}
# Ausgabe unter fonts/ -> (Paket, Schnitt); dieselben Namen wie bisher
SCHNITTE = {
    "barlow-400-normal": ("barlow", "400-normal"),
    "barlow-500-normal": ("barlow", "500-normal"),
    "barlow-600-normal": ("barlow", "600-normal"),
    "barlow-semi-condensed-500-normal": ("barlow-semi-condensed", "500-normal"),
    "barlow-semi-condensed-600-normal": ("barlow-semi-condensed", "600-normal"),
}
# Die Schaugrafik bettet nur diese drei ein (schaugrafik.js, Funktion für den SVG-Export)
EINBETTEN = ("barlow-400-normal", "barlow-600-normal", "barlow-semi-condensed-600-normal")
POLNISCH = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
GRUNDBUCHSTABE = dict(zip(POLNISCH, "acelnoszzACELNOSZZ"))
KOPF_EINBETTUNG = ("// Schriften als Data-URI für die Schaugrafik (SVG/PNG-Export), erzeugt von skripte/schriften.py "
                   "aus den woff2-Dateien daneben. SIL OFL 1.1, siehe OFL.txt\n")


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")


def paket_lesen(name: str) -> tarfile.TarFile:
    datei, sha, angaben = PAKETE[name]
    ordner = daten_ordner() / "schriften" / STAND
    roh = (ordner / datei).read_bytes()
    ist = hashlib.sha256(roh).hexdigest()
    if ist != sha:
        raise SystemExit(f"{datei}: SHA256 {ist}, erwartet {sha}")
    soll = json.loads((ordner / angaben).read_text(encoding="utf-8"))["dist"]["integrity"]
    ist = "sha512-" + base64.b64encode(hashlib.sha512(roh).digest()).decode()
    if ist != soll:
        raise SystemExit(f"{datei}: Integrität {ist}, laut Registry {soll}")
    return tarfile.open(fileobj=io.BytesIO(roh), mode="r:gz")


def kern_lookups(schrift: TTFont) -> list[int]:
    """Indizes der Lookups, die ein Feature „kern“ (in irgendeiner Schrift/Sprache) nutzt, aufsteigend."""
    gpos = schrift["GPOS"].table
    return sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == "kern" for i in fr.Feature.LookupListIndex})


def paarwert(schrift: TTFont, lookups: list[int]):
    """(links, rechts) -> XAdvance, wie ein Textsatzprogramm ihn anwendet: je Lookup die erste Subtabelle, die das
    Paar trifft (Format 1: Paar steht in der Liste; Format 2: linker Glyph in der Abdeckung), Summe über die Lookups."""
    gpos = schrift["GPOS"].table
    tabellen = []
    for i in lookups:
        lk, sts = gpos.LookupList.Lookup[i], []
        for st in lk.SubTable:
            if lk.LookupType == 9:
                if st.ExtensionLookupType != 2:
                    continue
                st = st.ExtSubTable
            elif lk.LookupType != 2:
                continue
            abd = {g: n for n, g in enumerate(st.Coverage.glyphs)}
            if st.Format == 1:
                paare = [{pv.SecondGlyph: getattr(pv.Value1, "XAdvance", 0) or 0 for pv in ps.PairValueRecord}
                         for ps in st.PairSet]
                sts.append((1, abd, paare))
            else:
                sts.append((2, abd, st))
        tabellen.append(sts)

    def wert(l: str, r: str) -> int:
        summe = 0
        for sts in tabellen:
            for fmt, abd, inhalt in sts:
                if l not in abd:
                    continue
                if fmt == 1:
                    v = inhalt[abd[l]].get(r)
                    if v is None:
                        continue
                    summe += v
                else:
                    k1 = inhalt.ClassDef1.classDefs.get(l, 0)
                    k2 = inhalt.ClassDef2.classDefs.get(r, 0)
                    vr = inhalt.Class1Record[k1].Class2Record[k2].Value1
                    summe += (getattr(vr, "XAdvance", 0) or 0) if vr else 0
                break
        return summe
    return wert


def kerning_uebertragen(schrift: TTFont) -> int:
    """Hängt ein PairPos-Lookup mit den Werten der Grundbuchstaben an (nur Paare ohne eigenen Wert); Anzahl Paare."""
    cmap = schrift.getBestCmap()
    if not all(ord(c) in cmap for c in GRUNDBUCHSTABE.keys() | set(GRUNDBUCHSTABE.values())):
        raise SystemExit("Kerning: Sonderzeichen oder Grundbuchstabe fehlt in der Zeichentabelle")
    grund = {cmap[ord(p)]: cmap[ord(b)] for p, b in GRUNDBUCHSTABE.items()}
    alle = sorted(set(cmap.values()), key=schrift.getGlyphID)
    lookups = kern_lookups(schrift)
    w = paarwert(schrift, lookups)
    paare = {}
    for p in sorted(grund, key=schrift.getGlyphID):
        for b in alle:
            for l, r in ((p, b), (b, p)):
                if (l, r) in paare:
                    continue
                gl, gr = grund.get(l, l), grund.get(r, r)
                v = w(gl, gr)
                if v and not w(l, r):
                    paare[(l, r)] = v
    if not paare:
        return 0
    wert1 = {k: (buildValue({"XAdvance": v}), None) for k, v in sorted(paare.items(),
             key=lambda kv: (schrift.getGlyphID(kv[0][0]), schrift.getGlyphID(kv[0][1])))}
    lk = otTables.Lookup()
    lk.LookupType, lk.LookupFlag = 2, 0
    lk.SubTable = buildPairPosGlyphs(wert1, schrift.getReverseGlyphMap())
    lk.SubTableCount = len(lk.SubTable)
    gpos = schrift["GPOS"].table
    gpos.LookupList.Lookup.append(lk)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    neu = gpos.LookupList.LookupCount - 1
    gesehen = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern" and id(fr.Feature) not in gesehen:
            gesehen.add(id(fr.Feature))
            fr.Feature.LookupListIndex.append(neu)
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
    # Gegenprobe: jedes übertragene Paar hat jetzt den Wert seines Grundpaars
    w2 = paarwert(schrift, kern_lookups(schrift))
    falsch = [k for k, v in paare.items() if w2(*k) != v]
    if falsch:
        raise SystemExit(f"Kerning: {len(falsch)} Paare nach dem Übertragen falsch, etwa {falsch[:3]}")
    return len(paare)


def zusammenfuegen(tar: tarfile.TarFile, paket: str, schnitt: str) -> bytes:
    teile = []
    for teil in ("latin", "latin-ext"):
        glied = tar.extractfile(f"package/files/{paket}-{teil}-{schnitt}.woff2")
        if glied is None:
            raise SystemExit(f"{paket}-{teil}-{schnitt}.woff2 fehlt im Paket")
        teile.append(io.BytesIO(glied.read()))
    latin, ext = TTFont(teile[0]), TTFont(teile[1])
    created, modified = latin["head"].created, latin["head"].modified
    # Hinting-Tabellen gelten für alle Glyphen; das Zusammenfügen übernimmt sie aus einer Teilmenge. Nur zulässig,
    # wenn beide Teilmengen dieselben haben.
    for tab in ("fpgm", "prep", "cvt ", "gasp"):
        if (tab in latin) != (tab in ext) or (tab in latin and latin.reader[tab] != ext.reader[tab]):
            raise SystemExit(f"{paket} {schnitt}: Tabelle {tab!r} unterscheidet sich zwischen latin und latin-ext")
    for t in teile:
        t.seek(0)
    schrift = Merger().merge(teile)
    kerning_uebertragen(schrift)
    # fontTools.merge setzt created und modified auf die Laufzeit; beide aus der latin-Datei übernehmen
    schrift["head"].created, schrift["head"].modified = created, modified
    schrift.recalcTimestamp = False
    # Erst als TrueType speichern, dann ohne Zeitstempel-Neuberechnung neu laden und als WOFF2 schreiben: direkt
    # als WOFF2 gespeichert setzt fontTools head.modified auf die Laufzeit (gemessen, nicht reproduzierbar).
    ttf = io.BytesIO()
    schrift.save(ttf, reorderTables=True)
    schrift = TTFont(io.BytesIO(ttf.getvalue()), recalcTimestamp=False)
    schrift.flavor = "woff2"
    aus = io.BytesIO()
    schrift.save(aus, reorderTables=True)
    # Laden ohne Neuberechnung des Zeitstempels, damit die Ausgabe nicht vom Laufdatum abhängt
    probe = TTFont(io.BytesIO(aus.getvalue()), recalcTimestamp=False)
    if (probe["head"].created, probe["head"].modified) != (created, modified):
        raise SystemExit(f"{paket} {schnitt}: Zeitstempel nicht übernommen")
    fehlt = [c for c in POLNISCH if ord(c) not in probe.getBestCmap()]
    if fehlt:
        raise SystemExit(f"{paket} {schnitt}: es fehlen {''.join(fehlt)}")
    return aus.getvalue()


def erzeugen() -> dict[str, bytes]:
    tars = {name: paket_lesen(name) for name in PAKETE}
    aus = {f"fonts/{ziel}.woff2": zusammenfuegen(tars[p], p, s) for ziel, (p, s) in SCHNITTE.items()}
    einbettung = {k: "data:font/woff2;base64," + base64.b64encode(aus[f"fonts/{k}.woff2"]).decode()
                  for k in EINBETTEN}
    aus["fonts/einbettung.js"] = (KOPF_EINBETTUNG + "window.KIEZ_SCHRIFTEN="
                                  + json.dumps(einbettung, separators=(",", ":")) + ";\n").encode()
    return aus


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pruefen", action="store_true", help="nur vergleichen, nichts schreiben")
    a = ap.parse_args()
    aus = erzeugen()
    befund = 0
    for rel, inhalt in aus.items():
        ziel = WURZEL / rel
        if a.pruefen:
            gleich = ziel.exists() and ziel.read_bytes() == inhalt
            print(f"{'ok' if gleich else 'BEFUND'}  {rel} ({len(inhalt)} B, sha256 {hashlib.sha256(inhalt).hexdigest()})")
            befund |= not gleich
        else:
            ziel.write_bytes(inhalt)
            print(f"geschrieben {rel} ({len(inhalt)} B, sha256 {hashlib.sha256(inhalt).hexdigest()})")
    return 1 if befund else 0


if __name__ == "__main__":
    sys.exit(main())
