"""Prüfung Schriften: alle polnischen Sonderzeichen in jeder ausgelieferten Schrift (maschinell mit fontTools).

Prüft ohne Netz:
  1. Jede Schriftdatei, die atlas.css, rahmen.css oder skripte/16_export.py per @font-face einbindet, liegt unter
     fonts/; kein @font-face teilt eine Schrift per unicode-range auf (dann wäre die Datei allein nicht das, was der
     Browser für einen Schnitt bekommt, und die Prüfung je Datei reichte nicht).
  2. In jeder dieser Dateien und in jeder Data-URI aus fonts/einbettung.js (Schaugrafik) hat jedes der 18 Zeichen
     ąćęłńóśźżĄĆĘŁŃÓŚŹŻ einen Eintrag in der Zeichentabelle (cmap) und eine Glyphe mit Umriss (glyf mit Konturen
     oder zusammengesetzt), also kein leeres Kästchen.
  3. Die Data-URIs in fonts/einbettung.js sind byte-gleich mit den Dateien daneben.
  4. fonts/OFL.txt enthält die Lizenz (SIL Open Font License 1.1) und den Copyright-Vermerk der Barlow-Autoren.
  5. Gegenprobe der Prüfung selbst: Eine Schrift ohne die Zeichen muss als Befund erkannt werden. Dazu wird mit
     fontTools.subset eine Kopie von barlow-400-normal ohne Latin Extended-A gebildet (nur im Speicher).

Aufruf (fontTools und brotli mit Hashes in requirements-schriften.txt):
    uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
        --with-requirements requirements-schriften.txt python -I pruefen/DF_schriften.py
Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import base64
import io
import json
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

WURZEL = Path(__file__).resolve().parent.parent
POLNISCH = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
EINBINDER = ("atlas.css", "rahmen.css", "skripte/16_export.py")
BEFUNDE: list[str] = []


def pruef(ok: bool, text: str) -> None:
    print(f"{'ok    ' if ok else 'BEFUND'} {text}")
    if not ok:
        BEFUNDE.append(text)


def fehlende(roh: bytes) -> list[str]:
    """Zeichen ohne cmap-Eintrag oder ohne Umriss."""
    f = TTFont(io.BytesIO(roh))
    cmap = f.getBestCmap()
    glyf = f["glyf"] if "glyf" in f else None
    aus = []
    for c in POLNISCH:
        name = cmap.get(ord(c))
        if name is None:
            aus.append(c)
            continue
        if glyf is not None:
            g = glyf[name]
            if getattr(g, "numberOfContours", 0) == 0:
                aus.append(c)
    return aus


def main() -> int:
    print("1. Eingebundene Schriftdateien")
    dateien: set[str] = set()
    for rel in EINBINDER:
        p = WURZEL / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for block in re.findall(r"@font-face\s*\{[^}]*\}", text):
            pruef("unicode-range" not in block, f"{rel}: @font-face ohne unicode-range ({block[:70]}…)")
            for url in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", block):
                name = url.split("/")[-1]
                dateien.add(name)
                pruef((WURZEL / "fonts" / name).exists(), f"{rel}: {url} liegt als fonts/{name} vor")
    pruef(len(dateien) > 0, f"{len(dateien)} Schriftdateien eingebunden: {', '.join(sorted(dateien))}")

    print("2. Polnische Sonderzeichen (18) je Datei")
    for name in sorted(dateien):
        p = WURZEL / "fonts" / name
        if not p.exists():
            continue
        f = fehlende(p.read_bytes())
        pruef(not f, f"fonts/{name}: {18 - len(f)} von 18" + (f", es fehlen {''.join(f)}" if f else ""))

    print("2b/3. Schaugrafik (fonts/einbettung.js)")
    s = (WURZEL / "fonts" / "einbettung.js").read_text(encoding="utf-8")
    eingebettet = json.loads(s[s.index("{"):s.rindex("}") + 1])
    pruef(len(eingebettet) > 0, f"{len(eingebettet)} Schriften eingebettet: {', '.join(eingebettet)}")
    for k, uri in eingebettet.items():
        roh = base64.b64decode(uri.split(",", 1)[1])
        f = fehlende(roh)
        pruef(not f, f"einbettung.js {k}: {18 - len(f)} von 18" + (f", es fehlen {''.join(f)}" if f else ""))
        datei = WURZEL / "fonts" / f"{k}.woff2"
        pruef(datei.exists() and datei.read_bytes() == roh, f"einbettung.js {k} byte-gleich mit fonts/{k}.woff2")

    print("4. Lizenz")
    ofl = (WURZEL / "fonts" / "OFL.txt").read_text(encoding="utf-8")
    pruef("SIL OPEN FONT LICENSE Version 1.1" in ofl, "fonts/OFL.txt: SIL Open Font License 1.1")
    pruef("The Barlow Project Authors" in ofl, "fonts/OFL.txt: Copyright The Barlow Project Authors")

    print("5. Gegenprobe der Prüfung")
    opt = subset.Options()
    opt.flavor = None
    opt.notdef_outline = True
    roh = (WURZEL / "fonts" / "barlow-400-normal.woff2").read_bytes()
    f = TTFont(io.BytesIO(roh))
    sub = subset.Subsetter(opt)
    sub.populate(unicodes=[u for u in f.getBestCmap() if not 0x0100 <= u <= 0x017F])
    sub.subset(f)
    aus = io.BytesIO()
    f.save(aus)
    f = fehlende(aus.getvalue())
    pruef(len(f) == 16, f"Kopie ohne Latin Extended-A: {len(f)} Zeichen als fehlend erkannt (erwartet 16, ó/Ó liegen in Latin-1)")

    print(f"\n{'grün' if not BEFUNDE else f'{len(BEFUNDE)} Befund(e)'}")
    return 1 if BEFUNDE else 0


if __name__ == "__main__":
    sys.exit(main())
