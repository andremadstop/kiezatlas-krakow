"""Prüfung hreflang ohne Browser: Sprachfassungen der erzeugten Seiten verweisen vollständig und gegenseitig aufeinander.

Ergänzt pruefen/seiten.mjs, damit die Sprachverweise auch mit ./pruefen.sh --ohne-browser geprüft sind. Liest nur
die erzeugten Seiten und die Ortskonfiguration (kein Netz, keine Datenbank, kein Browser). Prüft je Seite:
  1. Jede Sprache der Ortskonfiguration hat dieselben Seitendateien (Wurzelordner = erste Sprache, sonst <lang>/).
  2. <html lang> ist die Sprache des Ordners.
  3. Seiten mit robots noindex tragen weder hreflang noch canonical.
  4. Alle anderen tragen genau einen alternate-Verweis je Sprache plus x-default, jeweils die erwartete absolute
     Adresse unter basis_url (Startseite ohne Dateinamen), x-default = erste Sprache, canonical = eigene Fassung.
     Weil jede Fassung dieselbe vollständige Liste trägt, sind die Verweise damit gegenseitig.
  5. Jede verwiesene Adresse gehört zu einer vorhandenen Datei im Repo.
  6. og:locale ist die eigene Sprache, og:locale:alternate genau die übrigen.
  7. Der Sprachschalter (a[data-sprache]) führt relativ auf dieselbe Datei in jeder Sprache.

Aufruf: python -I pruefen/hreflang.py   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt Skriptverzeichnisse weg
import ort_konfig  # noqa: E402

OG_LOCALE = {"pl": "pl_PL", "en": "en_GB", "de": "de_DE"}   # wie skripte/30_seiten.py
befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


class Kopf(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.alt: list[tuple[str, str]] = []
        self.canon: list[str] = []
        self.noindex = False
        self.og = None
        self.og_alt: list[str] = []
        self.schalter: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "link" and a.get("rel") == "alternate" and "hreflang" in a:
            self.alt.append((a["hreflang"], a.get("href", "")))
        elif tag == "link" and a.get("rel") == "canonical":
            self.canon.append(a.get("href", ""))
        elif tag == "meta" and a.get("name") == "robots":
            self.noindex = "noindex" in (a.get("content") or "")
        elif tag == "meta" and a.get("property") == "og:locale":
            self.og = a.get("content")
        elif tag == "meta" and a.get("property") == "og:locale:alternate":
            self.og_alt.append(a.get("content", ""))
        elif tag == "a" and "data-sprache" in a and a["data-sprache"] not in self.schalter:
            # erster Treffer je Sprache ist der Schalter in der Kopfzeile; der Sprachhinweis zeigt auf dasselbe Ziel
            self.schalter[a["data-sprache"]] = a.get("href", "")


def main() -> int:
    k = ort_konfig.lade()
    sprachen: list[str] = k["sprachen"]
    basis: str = k["basis_url"]
    ordner = {l: ("" if i == 0 else l + "/") for i, l in enumerate(sprachen)}
    print(f"Sprachen {', '.join(sprachen)}, Basis {basis}")

    dateien = {l: sorted(p.name for p in (WURZEL / ordner[l]).glob("*.html")) for l in sprachen}
    erste = dateien[sprachen[0]]
    for l in sprachen[1:]:
        fehlt = sorted(set(erste) ^ set(dateien[l]))
        pruef(not fehlt, f"{l}: dieselben {len(erste)} Seiten wie {sprachen[0]}" + (f" (Unterschied: {fehlt})" if fehlt else ""))
    pruef(len(erste) > 0, f"{len(erste)} Seiten je Sprache gefunden")

    def absolut(datei: str, lang: str) -> str:
        return basis + ordner[lang] + ("" if datei == "index.html" else datei)

    def lokal(url: str) -> Path | None:
        if not url.startswith(basis):
            return None
        rest = url[len(basis):]
        if rest == "" or rest.endswith("/"):
            rest += "index.html"
        return WURZEL / rest

    n_index = n_noindex = 0
    for lang in sprachen:
        for datei in dateien[lang]:
            kurz = f"{ordner[lang]}{datei}"
            p = Kopf()
            p.feed((WURZEL / ordner[lang] / datei).read_text(encoding="utf-8"))
            fehler = []
            if p.lang != lang:
                fehler.append(f"html lang={p.lang!r}")
            if p.noindex:
                n_noindex += 1
                if p.alt or p.canon:
                    fehler.append("noindex mit hreflang oder canonical")
            else:
                n_index += 1
                erwartet = {l: absolut(datei, l) for l in sprachen}
                erwartet["x-default"] = absolut(datei, sprachen[0])
                ist = dict(p.alt)
                if len(p.alt) != len(ist):
                    fehler.append("hreflang doppelt")
                if ist != erwartet:
                    fehler.append(f"hreflang {sorted(ist)} statt {sorted(erwartet)} oder Adresse abweichend")
                if p.canon != [absolut(datei, lang)]:
                    fehler.append(f"canonical {p.canon}")
                for l, url in ist.items():
                    z = lokal(url)
                    if z is None or not z.is_file():
                        fehler.append(f"Ziel {l} ohne Datei ({url})")
            if p.og != OG_LOCALE.get(lang) or sorted(p.og_alt) != sorted(OG_LOCALE[l] for l in sprachen if l != lang):
                fehler.append(f"og:locale {p.og} / {p.og_alt}")
            hoch = "../" if ordner[lang] else ""
            soll = {l: hoch + ordner[l] + datei for l in sprachen}
            if p.schalter != soll:
                fehler.append(f"Sprachschalter {p.schalter}")
            pruef(not fehler, f"{kurz}: " + ("; ".join(fehler) if fehler else
                  ("noindex, ohne hreflang" if p.noindex else f"hreflang {len(sprachen)}+x-default, canonical, gegenseitig")))

    print(f"\n{n_index} Fassungen mit hreflang, {n_noindex} noindex")
    print(f"{len(befunde)} Befund(e)" if befunde else "0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
