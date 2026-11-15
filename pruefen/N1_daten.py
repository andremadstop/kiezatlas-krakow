"""Prüfung Daten-Nacharbeit: Felder statt Sätze, gemeinsame Ortsmarke, JavaScript-Startgewicht, Zahlenvergleich.

Regeln: pruefen/N1_protokoll.md. Kein Netz, keine Datenbank.

  1. Keine Sätze in daten/*.js (Regel 1): jede Zeichenkette mit drei oder mehr Wörtern muss an einem Feldpfad der
     Positivliste ERLAUBT stehen (Quellen- und Lizenzvermerke, Eigennamen, Rohwerte der Quellen, wörtliche Zitate
     aus Rechtsakten). daten/ort.js trägt Werte je Sprache und ist ausgenommen; Kopfkommentare sind Quellvermerke.
  2. Keine internen Paketbezeichnungen („Paket …“) in daten/*.js.
  3. Ortsmarke ul. Kościuszki 18 an derselben Koordinate in denkmale_odbl.js und sanierung_odbl.js (Regel 3).
  4. Radius als Feld: jede Kennzahl mit Radius in planer*_odbl.js trägt radius_m (Regel 1.3).
  5. JavaScript-Startgewicht (Regel 5, Methode von belege/S1_seiten.md): je <script src> der erzeugten Seite
     `gzip -9 -c`, Summe; das JavaScript von index.html unter 307.200 B. Gemessen wird nur JavaScript, nicht das
     Gesamtgewicht der Seite. Zur Information stehen dabei: die Werte von karta.html und dzielnica.html sowie für
     index.html das Gewicht mit HTML und Stylesheets (<link rel="stylesheet">), ohne Schriften und Kacheln.

Aufruf:
  python -I pruefen/N1_daten.py                     Prüfungen 1 bis 5, Rückgabe 0 = grün
  python -I pruefen/N1_daten.py --vergleich REV     zusätzlich: alle Zahlen jeder daten/*.js gegen den Stand REV
                                                    (git show), je Datei die geänderten Zahlenpfade
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "daten"
GRENZE_START_B = 307200

# Feldpfade (Listenindizes als [], Stadtteil- und Jahresschlüssel als .N), an denen längere Zeichenketten stehen dürfen
ERLAUBT = [re.compile(x) for x in (
    r"(^|\.)quellen?(_grenzen)?(\.[a-z0-9_]+)?\.(quelle|lizenz|licencja|vermerk|url|odpowiedzialnosc|rechtsgrundlage|"
    r"nazwa|pochodzenie|attribution|plik|fundstelle)$",
    r"(^|\.)quellen\.[a-z0-9_]+\.vermerk_sprachen\.[a-z]+$",
    r"^\.(vermerk|lizenz)$",
    r"\.properties\.(name|n|fn|unterart)$",          # Eigennamen und Rohwerte der Quelle (BDOT10k, OSM)
    r"\.richtwert\.seite$",                          # Fundstelle im Gesetz („art. 39 ust. 2, s. 40“)
    r"^\.(oben|unten|stil|ebenen)\[\]\..*text-font\[\]$",   # Schriftnamen der Grundkarte
    r"^\.stand$",                                    # Stand der Grundkarte („BDOT10k 1261 (Miasto Kraków), …“)
    r"^\.kontekst\.[a-z_]+$",                        # Luft: Rechtsakt, Fundstelle, wörtliche Zitate
    r"^\.stacje\[\]\.nazwa$",                          # Luft: Stationsnamen der EEA (Eigennamen, „Kraków, Aleja …“)
    r"^\.grenzwerte\.[a-z0-9_]+\[\]\.fundstelle$",
    r"^\.kennwerte\.[a-z0-9_]+\.agregacja$",         # Luft: Rohwerte der EEA-Statistik
    r"^\.reguly\.[a-z_]+$",
    r"^\.typologie\.grundgesamtheit$",               # Filterausdruck der BDOT10k
    r"^\.typologie\.literatur\.[a-z_]+$",            # bibliographische Angaben
    r"^\.eingabe\.grenzen$",                         # Dateiname mit Prüfsumme
)]
WORT = re.compile(r"\S+")


def js_lesen(text: str):
    m = re.search(r"window\.[A-Za-z0-9_]+\s*=\s*", text)
    return json.loads(text[m.end():].rstrip().rstrip(";"))


def blaetter(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            k2 = ".N" if re.fullmatch(r"\d{2,4}", str(k)) else "." + str(k)
            yield from blaetter(v, p + k2)
    elif isinstance(o, list):
        for v in o:
            yield from blaetter(v, p + "[]")
    else:
        yield p, o


def zahlen(o, p=""):
    """Alle Zahlen mit vollem Pfad (Indizes ausgeschrieben)."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from zahlen(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from zahlen(v, f"{p}[{i}]")
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield p, o


befunde: list[str] = []


def pruef(ok: bool, text: str) -> None:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)


def gz(datei: Path) -> int:
    return len(subprocess.run(["gzip", "-9", "-c", str(datei)], check=True, capture_output=True).stdout)


def gewicht(seite: str) -> int:
    """JavaScript beim Laden: Summe gzip -9 je <script src> der Seite."""
    p = WURZEL / seite
    return sum(gz((p.parent / src).resolve())
               for src in re.findall(r'<script[^>]*src="([^"]+)"', p.read_text(encoding="utf-8")))


def gewicht_html_css(seite: str) -> int:
    """Zur Information: HTML der Seite und ihre Stylesheets, gzip -9 je Datei (ohne Schriften und Kacheln)."""
    p = WURZEL / seite
    css = re.findall(r'<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"', p.read_text(encoding="utf-8"))
    return gz(p) + sum(gz((p.parent / h).resolve()) for h in css)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vergleich", metavar="REV")
    a = ap.parse_args()

    print("1. Keine Sätze in daten/*.js (Positivliste der Feldpfade)")
    dateien = sorted(p for p in DATEN.glob("*.js") if p.name != "ort.js")
    print(f"  info  {len(dateien)} Dateien geprüft (daten/*.js ohne ort.js)")
    for p in dateien:
        text = p.read_text(encoding="utf-8")
        d = js_lesen(text)
        frei = sorted({(pf, w[:70]) for pf, w in blaetter(d) if isinstance(w, str) and len(WORT.findall(w)) >= 3
                       and not any(r.search(pf) for r in ERLAUBT)})
        pruef(not frei, f"{p.name}: keine Sätze" + (f" ({len(frei)}: {frei[:3]})" if frei else ""))
        pruef("Paket " not in text.split("*/", 1)[-1], f"{p.name}: keine Paketbezeichnung in den Daten")

    print("2. Ortsmarke ul. Kościuszki 18")
    dm = js_lesen((DATEN / "denkmale_odbl.js").read_text(encoding="utf-8"))["ortsmarken"][0]
    so = js_lesen((DATEN / "sanierung_odbl.js").read_text(encoding="utf-8"))["ortsmarke"]
    k1 = (dm.get("geometry") or {}).get("coordinates")
    k2 = ((so or {}).get("geometry") or {}).get("coordinates")
    pruef(k1 is not None and k1 == k2, f"denkmale_odbl.js {k1} = sanierung_odbl.js {k2}")

    print("3. Radius als Feld")
    for n in ("planer_odbl.js", "planer_fuss_odbl.js"):
        d = js_lesen((DATEN / n).read_text(encoding="utf-8"))
        werte = [w for r in [*d["raeume"].values(), d["gesamt"]] for w in r["werte"]]
        mit = [w for w in werte if w["kennzahl"] in ("anteil_in_radius", "oepnv_takt", "gruen_in_radius")]
        pruef(mit and all(isinstance(w.get("radius_m"), int) for w in mit)
              and all(w["radius_m"] == w["richtwert"]["wert"] for w in mit if w.get("richtwert")),
              f"{n}: radius_m an {len(mit)} Kennzahlen mit Radius, gleich richtwert.wert, wo es einen gibt")

    print("4. JavaScript-Startgewicht (gzip -9 -c je Skript der erzeugten pl-Seite; nur JavaScript)")
    for s in ("index.html", "karta.html", "dzielnica.html"):
        b = gewicht(s)
        if s == "index.html":
            pruef(b < GRENZE_START_B, f"{s}: JavaScript {b} B gz < {GRENZE_START_B} B")
            hc = gewicht_html_css(s)
            print(f"  info  {s}: mit HTML und Stylesheets {b + hc} B gz (HTML und CSS {hc} B; "
                  "ohne Schriften und Kacheln, nicht Teil der Grenze)")
        else:
            print(f"  info  {s}: JavaScript {b} B gz")

    if a.vergleich:
        print(f"5. Zahlen gegen {a.vergleich}")
        zaehl = {"gleich": 0, "diff": 0, "neu": 0}
        for p in sorted(DATEN.glob("*.js")):
            rel = p.relative_to(WURZEL).as_posix()
            r = subprocess.run(["git", "-C", str(WURZEL), "show", f"{a.vergleich}:{rel}"], capture_output=True, text=True)
            if r.returncode:
                print(f"  neu   {rel}")
                zaehl["neu"] += 1
                continue
            alt, neu = dict(zahlen(js_lesen(r.stdout))), dict(zahlen(js_lesen(p.read_text(encoding="utf-8"))))
            weg = sorted(set(alt) - set(neu))
            dazu = sorted(set(neu) - set(alt))
            anders = sorted(k for k in set(alt) & set(neu) if alt[k] != neu[k])
            zaehl["diff" if (weg or dazu or anders) else "gleich"] += 1
            if weg or dazu or anders:
                print(f"  diff  {rel}: {len(alt)} → {len(neu)} Zahlen; weg {len(weg)}, neu {len(dazu)}, geändert {len(anders)}")
                for k in (weg[:3] + dazu[:3] + anders[:3]):
                    print(f"          {k}: {alt.get(k)} → {neu.get(k)}")
            else:
                print(f"  gleich {rel}: {len(alt)} Zahlen")
    if a.vergleich:
        print(f"  Summe: {sum(zaehl.values())} Dateien, gleich {zaehl['gleich']}, mit Abweichung {zaehl['diff']}, "
              f"neu {zaehl['neu']}")
    print(f"\n{len(befunde)} Befunde" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
