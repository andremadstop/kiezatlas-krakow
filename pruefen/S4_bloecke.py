"""Prüfung der Langtexte (Methoden- und Datenseiten) gegen die Regeln in pruefen/S4_protokoll.md.

Liest texte/<lang>/bloecke/quelle/*.html und die erzeugten Blöcke texte/<lang>/bloecke/*.html. Prüft:
  1. Jeder Quelltext in pl, en und de; jeder erzeugte Block entspricht Quelltext und Datendateien
     (skripte/16_bloecke_krakow.py --pruefen, im selben Lauf).
  2. Dieselben Datenfelder (data-feld) in allen drei Sprachen eines Blocks: keine Zahl fällt beim Übersetzen weg.
  3. Keine Zahl von Hand: Im sichtbaren Text ohne die Spannen data-feld steht keine Ziffer, außer in den Kennungen der
     Liste ERLAUBT (Namen von Datensätzen, Lizenzen und Systemen, Rechtsfundstellen, EPSG, TERYT; je mit Grund).
  4. Falschsätze: pruefen/d3_falschsaetze.json (alle und je Sprache; die eigene Liste des Pakets ist seit dem
     14.11.2026 dort unter „alle“); kein Treffer.
  5. In pl und en keine Wörter aus der deutschen Wortliste von pruefen/seiten.mjs (ohne Elemente mit lang="de").
  6. Keine internen Plankennungen, kein Pfad zu einzelnen Belegen oder Prüfskripten im Text (erlaubt: belege/README.md,
     docs/rundgang.md, docs/entscheidungen.md, pruefen.sh, CITATION.cff).
  7. Nur bekannte Platzhalter des Seitengenerators ({{wurzel}}, {{meldeweg}}); Verweise auf Downloads zeigen auf
     vorhandene Dateien unter daten/pobierz/, Verweise auf Seiten auf Seiten aus config/krakow.yaml oder auf die
     Methoden- und Datenseite (Vorschlag in docs/entscheidungen/S4.md).
  9. Rückfall ohne Handeingaben: Ohne Ergebnis der Sichtprüfungen (Denkmale ohne belege/DZ_sichtpruefung.json, Typologie
     ohne belege/DS_sichtpruefung.json) lassen sich die Blöcke erzeugen, nennen „ungeprüft“ bzw. „noch nicht
     ausgewertet“ und haben in pl, en, de dieselben Datenfelder. Mit gesetzter Adresse repository in config/krakow.yaml
     verlinken Methoden- und Datenseite das Repository und lassen den Satz „noch nicht öffentlich“ weg, ohne Adresse
     steht er wieder; eine Adresse ohne https bricht ab. Geprüft an Kopien der Daten im Speicher, nichts wird geschrieben.
  8. ODbL-Vermerk: Jeder Block mit einem Wert aus einer _odbl-Datei (data-feld="…_odbl:…") trägt den Vermerk kern.odbl
     mit dem Link auf openstreetmap.org/copyright; ebenso jede erzeugte Seite (Wurzel, en/, de/), die einen solchen Wert
     zeigt (Lizenzfolge der OSM-Grenzen, Variante a).

Aufruf: python -I pruefen/S4_bloecke.py    Rückgabe 0 = 0 Befunde. Kein Netz, keine Datenbank.
"""
from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SPRACHEN = ("pl", "en", "de")
befunde: list[str] = []

ERLAUBT = [
    (r"BDOT10k", "Name der Datenbank"),
    (r"LoD[12]\b", "Detailstufen der Gebäudemodelle"),
    (r"\bPM10\b|\bPM2[,.]5\b|\bNO2\b", "Schadstoffnamen"),
    (r"\b(NSP|Census|census|spisu?|Zensus|Mieszkań) 2021\b", "Name der Volkszählung und des Gitters"),
    (r"EPSG:\d{4,5}", "Kennung des Koordinatensystems"),
    (r"CC BY 4\.0|ODbL 1\.0|Open Database License 1\.0|OFL 1\.1|Apache-2\.0|UTF-8", "Namen von Lizenzen und Zeichensatz"),
    (r"\bsiatka_1km(_odbl|_pokrycie)?\b", "Namen der Ebenen in den Downloads"),
    (r"\bpowiat 1261\b|\bTERYT 1261\b", "TERYT-Kennung der Stadt (Teil des Datensatznamens)"),
    (r"\bart\. \d+[a-z]* ust\. \d+( i \d+)?", "Rechtsfundstelle"),
    (r"\b1[ -]km\b|\b1-km-", "Name des Eurostat-Gitters (Auflösung vom Export geprüft)"),
    (r"Wilson[\w-]*[ -]95[ -]?%", "Name des Konfidenzintervalls"),
    (r"95-procentowy przedział ufności", "Name des Konfidenzintervalls (polnisch)"),
    (r"\b3D\b", "Ansicht in drei Dimensionen"),
]
ERLAUBT = [(re.compile(m), g) for m, g in ERLAUBT]
DEUTSCH = re.compile(r"\b(und|nicht|oder|Stadtteile?|Einwohner|Karte|Daten|Quelle|Stand der|zeigen|Gebäude|für|über|Seite)\b", re.I)
KENNUNG = re.compile(r"\b(?:P[0-9]|D[0-9]{1,2}|KR[0-9]+|Tor M)\b")
PFAD = re.compile(r"\b(belege|pruefen|docs)/[\w./-]+")
PFAD_FREI = {"belege/README.md", "docs/rundgang.md", "docs/entscheidungen.md"}
ODBL_LINK = "https://www.openstreetmap.org/copyright"
NEUE_SEITEN = {"metoda", "dane"}   # Vorschlag docs/entscheidungen/S4.md


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def sichtbar(block: str, lang: str) -> tuple[str, str]:
    """(Text ohne Datenfelder, Text mit Datenfeldern); ohne Kommentare, Tags, Attribute; Elemente mit lang="de"
    in pl/en zählen für die Wortliste nicht."""
    t = re.sub(r"<!--.*?-->", "", block, flags=re.S)
    mit = t
    ohne = re.sub(r'<span data-feld="[^"]*"[^>]*>[^<]*</span>', " ", t)

    def roh(x: str, ohne_de: bool) -> str:
        if ohne_de:
            x = re.sub(r'<(\w+)[^>]*\blang="de"[^>]*>.*?</\1>', " ", x, flags=re.S)
        x = re.sub(r"\{\{[^}]*\}\}", " ", x)
        x = re.sub(r"<[^>]+>", " ", x)
        return re.sub(r"\s+", " ", html.unescape(x))
    return roh(ohne, lang != "de"), roh(mit, lang != "de")


def generator():
    spec = importlib.util.spec_from_file_location("bloecke", WURZEL / "skripte" / "16_bloecke_krakow.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rueckfall(g) -> None:
    """9. Ohne Sichtprüfungen fallen die Blöcke auf „ungeprüft“ zurück; Repository-Link nur mit Adresse in der Konfiguration."""
    print("Rückfall ohne Handeingaben (Daten im Speicher)")
    import yaml
    cache: dict = {}
    for n in ("denkmale", "denkmale_odbl", "sanierung"):
        g.daten(n, cache)
    for n in ("denkmale", "denkmale_odbl"):
        sp = cache[n]["sichtpruefung"]
        cache[n]["sichtpruefung"] = {"geprueft": False, "stichprobe": sp["stichprobe"], "startwert": sp["startwert"]}
    cache["sanierung"]["typologie"].pop("sichtpruefung", None)
    try:
        ohne = g.erzeugen(cache)
    except g.Fehler as x:
        pruef(False, f"ohne Sichtprüfungen erzeugbar: {x}")
        return
    pruef(True, "ohne Sichtprüfungen erzeugbar (Denkmale geprueft false, Typologie ohne Ergebnis)")
    # Wortlaut der Hinweise vor der Sichtprüfung (Lage der Denkmalpunkte; Typologie)
    marke = {"de": (r"Lage ungeprüft|nicht am Luftbild geprüft", "noch nicht ausgewertet"),
             "en": (r"location (unchecked|not checked)|not been checked against aerial imagery", "not been assessed"),
             "pl": (r"położenie niesprawdzone|nie zostało sprawdzone na ortofotomapie", "nie jest jeszcze oceniona")}
    for name in ("kamienice_metoda", "kamienice_dane", "metoda"):
        felder = {}
        for lang in SPRACHEN:
            b = ohne[WURZEL / "texte" / lang / "bloecke" / f"{name}.html"]
            felder[lang] = sorted({re.sub(rf"\.{lang}$", ".<lang>", f) for f in re.findall(r'data-feld="([^"]*)"', b)})
            rest = [f for f in felder[lang] if "sichtpruefung.ergebnis" in f or "sichtpruefung.gesamt" in f
                    or "typologie.sichtpruefung" in f]
            text = sichtbar(b, lang)[1]
            lage = re.search(marke[lang][0], text)
            typ = marke[lang][1] in text if name != "kamienice_dane" else True
            pruef(not rest and bool(lage) and typ, f"{lang}/{name}: ohne Ergebnis Hinweis „ungeprüft“"
                  + (f": Felder {rest[:2]}" if rest else "") + ("" if lage else ": Hinweis zur Lage fehlt")
                  + ("" if typ else ": Hinweis zur Typologie fehlt"))
        pruef(felder["pl"] == felder["en"] == felder["de"], f"{name}: ohne Ergebnis dieselben Datenfelder in pl, en, de")
    konfig = yaml.safe_load((WURZEL / "config" / "krakow.yaml").read_text(encoding="utf-8"))
    pruef(not konfig.get("repository") or all('href="' + html.escape(konfig["repository"]) + '"' in
                                               (WURZEL / "texte" / l / "bloecke" / "metoda.html").read_text(encoding="utf-8")
                                               for l in SPRACHEN),
          f"repository in config/krakow.yaml: {konfig.get('repository')!r}")
    adresse = "https://example.org/kiezatlas-krakow"
    mit = g.erzeugen({"konfig": {**konfig, "repository": adresse}})
    leer = g.erzeugen({"konfig": {**konfig, "repository": None}})   # Fork ohne Adresse: Satz „auf Anfrage“
    nicht_oeffentlich = {"pl": "niepubliczn", "en": "not public", "de": "nicht öffentlich"}
    for lang in SPRACHEN:
        p = WURZEL / "texte" / lang / "bloecke" / "metoda.html"
        b, ohne_adresse = mit[p], leer[p]
        pruef(b.count(f'href="{adresse}"') == 2 and b.count("mailto:") == ohne_adresse.count("mailto:") - 1
              and adresse not in ohne_adresse,
              f"{lang}/metoda: mit Adresse zwei Verweise auf das Repository, Satz „auf Anfrage“ entfällt")
        p = WURZEL / "texte" / lang / "bloecke" / "dane.html"
        b, ohne_adresse = mit[p], leer[p]
        pruef(b.count(f'href="{adresse}"') == 1 and nicht_oeffentlich[lang] not in b
              and nicht_oeffentlich[lang] in ohne_adresse and adresse not in ohne_adresse,
              f"{lang}/dane: mit Adresse ein Verweis auf das Repository, ohne Adresse der Satz „noch nicht öffentlich“")
    try:
        g.erzeugen({"konfig": {**konfig, "repository": "http://example.org/x"}})
        pruef(False, "Adresse ohne https bricht ab")
    except g.Fehler:
        pruef(True, "Adresse ohne https bricht ab")


def main() -> int:
    g = generator()
    print("Quelltexte und erzeugte Blöcke")
    try:
        neu = g.erzeugen()
    except g.Fehler as x:
        pruef(False, f"Langtexte lassen sich erzeugen: {x}")
        return 1
    namen = sorted({p.stem for p in neu})
    pruef(bool(namen), f"{len(namen)} Blöcke × {len(SPRACHEN)} Sprachen: {', '.join(namen)}")
    alt = [p for p, t in neu.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
    pruef(not alt, "erzeugte Blöcke aktuell (skripte/16_bloecke_krakow.py)" + (f": {[str(p.relative_to(WURZEL)) for p in alt]}" if alt else ""))

    fl = json.loads((WURZEL / "pruefen" / "d3_falschsaetze.json").read_text(encoding="utf-8"))
    ohne_grund = [e["muster"] for q in (fl,) for k, v in q.items() if not k.startswith("_") for e in v
                  if not str(e.get("grund", "")).strip()]
    pruef(not ohne_grund, "jedes Falschsatz-Muster mit Grund")
    seiten = {str(s) for s in __import__("yaml").safe_load((WURZEL / "config" / "krakow.yaml").read_text(encoding="utf-8"))["seiten"]}
    pobierz = WURZEL / "daten" / "pobierz"

    for name in namen:
        print(f"Block {name}")
        felder = {}
        for lang in SPRACHEN:
            p = WURZEL / "texte" / lang / "bloecke" / f"{name}.html"
            b = neu[p]
            # sprachabhängige Werte der Ortskonfiguration (z. B. ort:zitierzeile.pl) zählen als ein Feld
            felder[lang] = sorted({re.sub(rf"\.{lang}$", ".<lang>", f) for f in re.findall(r'data-feld="([^"]*)"', b)})
            ohne, mit = sichtbar(b, lang)
            # 3. Ziffern außerhalb der Datenfelder
            rest = ohne
            for rx, _ in ERLAUBT:
                rest = rx.sub(" ", rest)
            ziffern = [m.group(0) for m in re.finditer(r"\S*\d\S*", rest)]
            pruef(not ziffern, f"{lang}/{name}: keine Zahl von Hand ({len(felder[lang])} Datenfelder)"
                  + (f": {ziffern[:5]}" if ziffern else ""))
            # 4. Falschsätze
            treffer = []
            for e in fl.get("alle", []) + fl.get(lang, []):
                m = re.search(e["muster"], mit)
                if m:
                    treffer.append(m.group(0))
            pruef(not treffer, f"{lang}/{name}: kein Falschsatz" + (f": {treffer[:3]}" if treffer else ""))
            # 5. deutsche Reste
            if lang != "de":
                d = DEUTSCH.search(mit)
                pruef(not d, f"{lang}/{name}: keine Wörter der deutschen Wortliste" + (f": „{d.group(0)}“" if d else ""))
            # 6. Kennungen und Pfade
            k = KENNUNG.search(mit)
            pfade = sorted({m.group(0).rstrip(".,;:") for m in PFAD.finditer(mit)} - PFAD_FREI)
            pruef(not k and not pfade, f"{lang}/{name}: keine Plankennung, keine Pfade zu einzelnen Belegen"
                  + (f": {k.group(0) if k else ''} {pfade}" if k or pfade else ""))
            # 7. Platzhalter und Verweise
            platz = sorted(set(re.findall(r"\{\{([^}]*)\}\}", b)) - {"wurzel", "meldeweg"})
            pruef(not platz, f"{lang}/{name}: nur bekannte Platzhalter" + (f": {platz}" if platz else ""))
            links = re.findall(r'href="([^"]+)"', b)
            kaputt = []
            for h in links:
                if h.startswith(("http://", "https://", "mailto:")):
                    continue
                if h.startswith("{{wurzel}}daten/pobierz/"):
                    if not (pobierz / h.removeprefix("{{wurzel}}daten/pobierz/")).is_file():
                        kaputt.append(h)
                    continue
                s = h.split("#")[0].removesuffix(".html")
                if s not in seiten and s not in NEUE_SEITEN:
                    kaputt.append(h)
            pruef(not kaputt, f"{lang}/{name}: {len(links)} Verweise auf vorhandene Dateien und Seiten" + (f": {kaputt}" if kaputt else ""))
            # 8. ODbL-Vermerk bei Werten aus _odbl-Dateien
            odbl = sorted({f.split(":")[0] for f in re.findall(r'data-feld="([a-z0-9_]*_odbl):', b)})
            if odbl:
                pruef(ODBL_LINK in b and g.odbl_vermerk(lang) in b,
                      f"{lang}/{name}: ODbL-Vermerk bei Werten aus {', '.join(odbl)}")
        pruef(felder["pl"] == felder["en"] == felder["de"],
              f"{name}: dieselben Datenfelder in pl, en, de" + ("" if felder["pl"] == felder["en"] == felder["de"] else
              f" (nur pl: {sorted(set(felder['pl']) - set(felder['en']) | set(felder['pl']) - set(felder['de']))[:3]}, "
              f"fehlt in pl: {sorted((set(felder['en']) | set(felder['de'])) - set(felder['pl']))[:3]})"))
    print("Erzeugte Seiten mit Werten aus _odbl-Dateien")
    seiten_odbl = 0
    for ordner in (WURZEL, WURZEL / "en", WURZEL / "de"):
        for p in sorted(ordner.glob("*.html")):
            t = p.read_text(encoding="utf-8")
            if re.search(r'data-feld="[a-z0-9_]*_odbl:', t):
                seiten_odbl += 1
                pruef(ODBL_LINK in t, f"{p.relative_to(WURZEL)}: Vermerk mit Link auf openstreetmap.org/copyright")
    pruef(seiten_odbl > 0, f"{seiten_odbl} Seiten zeigen Werte aus _odbl-Dateien")
    rueckfall(g)
    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
