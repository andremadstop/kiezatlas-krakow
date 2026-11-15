"""Prüfung Textschicht: texte/<lang>/*.js nach dem Vertrag daten/schema/texte.md.

Prüft (kein Netz, keine Datenbank, kein Browser):
  1. Jede Datei ist im Textformat lesbar (eine Zeile T["…"] = JSON; je Schlüssel, skripte/textschicht.py).
  2. Namensraum = Dateiname: texte/<lang>/<ns>.js enthält nur Schlüssel "<ns>.…"; Schlüssel in Kleinschreibung.
     Namensräume nur aus der Liste in daten/schema/texte.md (Abschnitt „Namensräume und Eigentum“).
  3. Alle Sprachen der Ortskonfiguration haben dieselben Dateien und je Datei dieselben Schlüssel.
  4. Je Schlüssel dieselben Platzhalter {name} in allen Sprachen (bei Pluraltexten in jeder Form).
  5. Pluraltexte haben genau die Formen der Sprache (pl: one, few, many, other; en, de: one, other) und {n}.
     Objektwerte ohne Plural nur bei kern.karte_locale, dort dieselben Schlüssel in allen Sprachen.
  6. Kein Schlüssel ohne Verwendung: Der Schlüssel steht wörtlich in vorlagen/, in einem *.js im Wurzelordner
     oder in skripte/30_seiten.py, oder er wird vom Seitengenerator je Seite gebildet (seiten.<seite>.nav|h1|beschreibung).
  7. Keine leeren Texte; in pl und en keine deutschen Wörter aus einer kurzen Wortliste.
  8. Dieselbe Wortliste auf dem sichtbaren Text der erzeugten Seiten in pl und en (ohne Skripte, Stile, Meta-Zeilen
     und ohne Elemente mit lang="de"), damit auch fest in vorlagen/ stehende Wörter auffallen.
  9. Jeder Schlüssel, den ein Modul im Wurzelordner mit t() abfragt (tt("…"), I18N.t("…"), KIEZ_I18N.t("…")), steht
     in den Texten; jede erzeugte Seite lädt die Namensräume der Module, die sie lädt (Kopfzeile „texte:“ der Vorlage).
 10. Keine deutschen Satzteile in den Zeichenketten der Module im Wurzelordner, gleich ob eine Seite sie schon lädt
     (Kommentare und Schlüssel als erstes Argument von t() zählen nicht; Wortliste, Umlaute, „rund “, „ganz “, „k. A.“). Ausnahmen
     stehen einzeln mit Grund in JS_AUSNAHMEN (Lizenz- und Quellenvermerke zu Potsdamer Daten, die mit den
     Datenpaketen ersetzt werden); eine Ausnahme ohne Treffer ist selbst ein Befund. Ganz ausgenommen sind die
     Module in JS_ENTFAELLT, solange keine Seite sie lädt.
 11. Falschsatz-Listen je Sprache (pruefen/d3_falschsaetze.json, je Eintrag Muster und Grund, wahlweise „ausser“ mit
     Fundorten und Grund): kein Treffer in den
     Texten der Sprache und im sichtbaren Text ihrer erzeugten Seiten.

Aufruf: python -I pruefen/texte.py   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt Skriptverzeichnisse weg
import ort_konfig  # noqa: E402
import textschicht  # noqa: E402

PLATZ = re.compile(r"\{(\w+)\}")
DEUTSCH = re.compile(r"\b(und|nicht|oder|Stadtteile?|Einwohner|Karte|Daten|Quelle|zeigen|Gebäude|für|über|Seite|Impressum|Datenschutz)\b", re.I)
OBJEKT_ERLAUBT = {"kern.karte_locale"}
# Zeichenketten in JavaScript: Wörter, die in pl/en nie vorkommen (neben Bindestrich oder # sind es Klassen- und Kennungsnamen). Kleingeschriebene Funktionswörter nur in Zeichenketten
# mit Leerzeichen (sonst wären Pfade, IDs und Hash-Schlüssel wie "daten/…" Treffer), Substantive nur großgeschrieben.
JS_KLEIN = re.compile(r"(?<![-#\w])(und|nicht|oder|für|über|der|die|das|dem|den|des|mit|kein|keine|keinen|zeigen|zeigt|ausgewählt|gibt|sind|ist|als|aus|nach|je|ein|eine|einer|wird|werden|alle|nur|auf|bei)(?![-\w])")
JS_GROSS = re.compile(r"\b(Stadtteile?|Stadtteils|Einwohner\w*|Karte|Daten|Quelle|Gebäude\w*|Seite|Impressum|Datenschutz|Zellen?|Wohnungen|Anteil|Stichtag|Luftlinie|Fußweg\w*|Planungsr[aä]um\w*|Haltestellen?|Einrichtungen?|Lizenztext|Herkunft|Höhe|Werte?|Legende|Bauzeit|Stadtbezirk|Landeshauptstadt)\b")
# Weitere Merkmale deutscher Satzteile (Umlaute, „rund “, „ganz “, „k. A.“), aus der früheren Paketprüfung übernommen.
JS_MERKMAL = re.compile(r"[äöüßÄÖÜ]|\b(?:rund|ganz) |\bk\. ?A\.")
# Zeichenketten direkt als erstes Argument von t() sind Schlüssel, kein Text („kern.rund“).
JS_SCHLUESSEL_VOR = re.compile(r"(?:\btt|\bt|\bI18N\.t|\bKIEZ_I18N\.t)\(\s*$")
JS_AUFRUF = re.compile(r'(?:\btt|\bI18N\.t|\bKIEZ_I18N\.t)\(\s*"([^"]+)"')
# Module, die für Kraków entfallen (Bauzeiten-Kaskade, docs/entscheidungen.md): keine Übersetzung, aber keine Seite darf sie laden.
JS_ENTFAELLT = {"jahre.js"}
# (Datei, Anfang der Zeichenkette) → Grund. Nur wörtlich bleibende Vermerke; die Datenpakete ersetzen sie mit den Krakauer Quellen.
_LIZ = "Lizenz- bzw. Quellenvermerk zu Potsdamer Daten, bleibt wörtlich (daten/schema/texte.md); ersetzt das Datenpaket"
JS_AUSNAHMEN: dict[tuple[str, str], str] = {
    ("atlas.js", "Zensus 2022 © Statistische Ämter des Bundes und der Länder, <a href="): _LIZ + " (Attribution Zellen)",
    ("atlas.js", "Gebäude © GeoBasis-DE/LGB, <a href="): _LIZ + " (Attribution Gebäude)",
    ("atlas.js", " Stadtteile © Landeshauptstadt Potsdam, dl-de/zero-2-0."): _LIZ + " (Legende Stadtteile)",
    ("atlas.js", "<div class='pop-q'>Zensus 2022, 15.05.2022, © Statistische Ämter"): _LIZ + " (Popup Zelle)",
    ("atlas.js", "Zensus 2022, © Statistische Ämter des Bundes und der Länder, dl-de/by-2-0; Stadtteile ©"): _LIZ + " (Bildzeile Grenzzelle)",
    ("karte.js", "Zensus 2022 © Statistische Ämter des Bundes und der Länder, <a href="): _LIZ + " (Attribution Zellen)",
    ("karte.js", "Gebäude © GeoBasis-DE/LGB, <a href="): _LIZ + " (Attribution Gebäude)",
    ("karte.js", " Stadtteile © Landeshauptstadt Potsdam, dl-de/zero-2-0."): _LIZ + " (Legende Stadtteile)",
    ("karte.js", "<div class='pop-q'>Zensus 2022, 15.05.2022, © Statistische Ämter"): _LIZ + " (Popup Zelle)",
    ("schaugrafik.js", "Gebäude: ALKIS vereinfacht, © GeoBasis-DE/LGB"): _LIZ + " (Fußzeile Schaugrafik)",
    ("planer.js", "Planungsräume © Landeshauptstadt Potsdam, <a href="): _LIZ + " (Attribution Planungsräume)",
    ("planer.js", "\">dl-de/by-2-0</a>, Daten verändert"): _LIZ + " (Attribution Planungsräume, Pflichtvermerk dl-de)",
    ("planer.js", "; © Statistische Ämter des Bundes und der Länder, dl-de/by-2-0, "): _LIZ + " (Einwohnerzeile)",
    ("planer.js", " Zensus 2022, © Statistische Ämter des Bundes und der Länder"): _LIZ + " (Popup Zelle)",
}
befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def namensraeume_aus_vertrag() -> set[str]:
    t = (WURZEL / "daten" / "schema" / "texte.md").read_text(encoding="utf-8")
    abschnitt = t.split("## Namensräume und Eigentum", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"`([a-z_]+)\.\*`", abschnitt))


def platzhalter(v) -> set[str] | None:
    if isinstance(v, str):
        return set(PLATZ.findall(v))
    return None


def js_zeichenketten(text: str):
    """(Zeile, Inhalt) aller Zeichenketten eines Moduls, ohne Kommentare und Regex-Literale (einfacher Zerleger)."""
    i, n, zeile, vorher = 0, len(text), 1, ""
    while i < n:
        c = text[i]
        if c == "\n":
            zeile += 1; i += 1; continue
        if c in " \t\r":
            i += 1; continue
        if text.startswith("//", i):
            j = text.find("\n", i); i = n if j < 0 else j; continue
        if text.startswith("/*", i):
            j = text.find("*/", i + 2); j = n if j < 0 else j + 2
            zeile += text.count("\n", i, j); i = j; continue
        if c in "\"'`":
            j, buf = i + 1, []
            while j < n and text[j] != c:
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j:j + 2]); j += 2; continue
                buf.append(text[j]); j += 1
            inhalt = "".join(buf)
            if not JS_SCHLUESSEL_VOR.search(text[max(0, i - 20):i]):
                yield zeile, inhalt
            zeile += inhalt.count("\n"); i = j + 1; vorher = "a"; continue
        if c == "/" and (not vorher or vorher in "(,=:[!&|?{};+-*%<>~^" or text[max(0, i - 7):i].rstrip().endswith("return")):
            j, klasse = i + 1, False
            while j < n and text[j] != "\n":
                if text[j] == "\\": j += 2; continue
                if text[j] == "[": klasse = True
                elif text[j] == "]": klasse = False
                elif text[j] == "/" and not klasse: break
                j += 1
            i = j + 1; vorher = "a"; continue
        vorher = c; i += 1


def sichtbar(seite: Path, ohne_de: bool = True) -> str:
    """Sichtbarer Text einer erzeugten Seite: ohne Skripte, Stile, Meta-Zeilen und (in pl/en) ohne Elemente mit lang="de"."""
    h = seite.read_text(encoding="utf-8")
    h = re.sub(r"<(script|style)\b.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<(meta|link)\b[^>]*>", " ", h, flags=re.I)
    if ohne_de:
        h = re.sub(r'<(a|span|p)\b[^>]*\blang="de"[^>]*>.*?</\1>', " ", h, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", h)


def main() -> int:
    k = ort_konfig.lade()
    sprachen = k["sprachen"]
    print(f"Sprachen: {', '.join(sprachen)}")
    try:
        texte = {l: textschicht.sprache_lesen(l) for l in sprachen}
    except textschicht.Textfehler as e:
        pruef(False, f"Textformat: {e}")
        return 1
    pruef(True, "Textformat aller Dateien lesbar (" + ", ".join(f"{l}: {sum(len(d) for d in texte[l].values())} Schlüssel" for l in sprachen) + ")")

    print("Namensraum = Datei")
    erlaubt = namensraeume_aus_vertrag()
    for l in sprachen:
        for ns, d in texte[l].items():
            fremd = [s for s in d if not s.startswith(ns + ".") or not textschicht.SCHLUESSEL.match(s)]
            pruef(not fremd and ns in erlaubt, f"texte/{l}/{ns}.js: {len(d)} Schlüssel im Namensraum {ns}.*"
                  + ("" if ns in erlaubt else ", Namensraum nicht in daten/schema/texte.md") + (f", fremd: {fremd[:4]}" if fremd else ""))

    print("Gleiche Dateien und Schlüssel in allen Sprachen")
    basis = sprachen[0]
    for l in sprachen[1:]:
        pruef(set(texte[l]) == set(texte[basis]), f"{l}: dieselben Dateien wie {basis} ({sorted(texte[l])})")
        for ns in sorted(set(texte[l]) & set(texte[basis])):
            a, b = set(texte[basis][ns]), set(texte[l][ns])
            pruef(a == b, f"{l}/{ns}.js: dieselben Schlüssel wie {basis}" + (f" (fehlt: {sorted(a - b)[:4]}, zu viel: {sorted(b - a)[:4]})" if a != b else ""))

    flach = {l: textschicht.flach(l) for l in sprachen}
    print("Platzhalter, Pluralformen, leere Texte")
    falsch_p, falsch_pl, leer, objekt = [], [], [], []
    for s, v0 in flach[basis].items():
        for l in sprachen:
            v = flach[l].get(s)
            if v is None:
                continue
            if isinstance(v, dict) and s not in OBJEKT_ERLAUBT:
                formen = textschicht.PLURALFORMEN[l]
                if set(v) != set(formen) or not all(isinstance(x, str) and "{n}" in x for x in v.values()):
                    falsch_pl.append(f"{l}:{s} {sorted(v)}")
                if any(not str(x).strip() for x in v.values()):
                    leer.append(f"{l}:{s}")
            elif isinstance(v, dict):
                if set(v) != set(flach[basis][s]):
                    objekt.append(f"{l}:{s}")
            elif not isinstance(v, str) or not v.strip():
                leer.append(f"{l}:{s}")
        # Platzhalter je Sprache gleich (Plural: Vereinigung über die Formen)
        def menge(v):
            if isinstance(v, str):
                return set(PLATZ.findall(v))
            if isinstance(v, dict) and s not in OBJEKT_ERLAUBT:
                return set().union(*(set(PLATZ.findall(str(x))) for x in v.values()))
            return set()
        mengen = {l: menge(flach[l].get(s)) for l in sprachen if s in flach[l]}
        if len({frozenset(m) for m in mengen.values()}) > 1:
            falsch_p.append(f"{s} {({l: sorted(m) for l, m in mengen.items()})}")
    pruef(not falsch_p, f"gleiche Platzhalter je Schlüssel in allen Sprachen{': ' + '; '.join(falsch_p[:3]) if falsch_p else ''}")
    pruef(not falsch_pl, f"Pluraltexte mit genau den Formen der Sprache und {{n}}{': ' + '; '.join(falsch_pl[:3]) if falsch_pl else ''}")
    pruef(not objekt, f"Objektwerte (kern.karte_locale) mit denselben Schlüsseln{': ' + ', '.join(objekt) if objekt else ''}")
    pruef(not leer, f"keine leeren Texte{': ' + ', '.join(leer[:5]) if leer else ''}")

    print("Verwendung")
    quellen = [*(WURZEL / "vorlagen").glob("*.html"), *WURZEL.glob("*.js"), WURZEL / "skripte" / "30_seiten.py"]
    korpus = "\n".join(p.read_text(encoding="utf-8") for p in quellen)
    dynamisch = {f"seiten.{s.replace('-', '_')}.{f}" for s in k["seiten"] for f in ("nav", "h1", "beschreibung")}
    unbenutzt = sorted(s for s in flach[basis] if s not in dynamisch and s not in korpus)
    pruef(not unbenutzt, f"{len(flach[basis])} Schlüssel, alle verwendet{': unbenutzt ' + ', '.join(unbenutzt[:6]) if unbenutzt else ''}")
    seiten_fehlt = sorted(s for s in dynamisch if s not in flach[basis])
    pruef(not seiten_fehlt, f"Titel, Überschrift, Beschreibung und Navigation für alle {len(k['seiten'])} Seiten{': fehlt ' + ', '.join(seiten_fehlt[:6]) if seiten_fehlt else ''}")
    vorlagen = "\n".join(p.read_text(encoding="utf-8") for p in (WURZEL / "vorlagen").glob("*.html"))
    benutzt = set(re.findall(r"\{\{(?:t|plural):([a-z0-9_.]+)", vorlagen))
    fehlt = sorted(s for s in benutzt if s not in flach[basis])
    pruef(not fehlt, f"jeder Schlüssel aus vorlagen/ vorhanden{': fehlt ' + ', '.join(fehlt) if fehlt else ''}")

    print("Keine deutschen Reste in pl und en")
    for l in [x for x in sprachen if x != "de"]:
        treffer = []
        for s, v in flach[l].items():
            for x in ([v] if isinstance(v, str) else list(v.values()) if isinstance(v, dict) else []):
                m = DEUTSCH.search(str(x))
                if m and s != "kern.sprache_auch":
                    treffer.append(f"{s}: „{m.group(0)}“")
        pruef(not treffer, f"{l}: keine Wörter aus der deutschen Wortliste{': ' + '; '.join(treffer[:4]) if treffer else ''}")
    for l in [x for x in sprachen if x != "de"]:
        ordner = WURZEL if l == k.get("standardsprache", "pl") else WURZEL / l
        treffer = []
        seiten = sorted(ordner.glob("*.html"))
        for seite in seiten:
            h = sichtbar(seite)
            m = DEUTSCH.search(h)
            if m:
                treffer.append(f"{seite.relative_to(WURZEL)}: „{m.group(0)}“")
        pruef(bool(seiten) and not treffer,
              f"{l}: sichtbarer Text der {len(seiten)} erzeugten Seiten ohne Wörter aus der deutschen Wortliste"
              f"{': ' + '; '.join(treffer[:4]) if treffer else ''}")

    print("Module im Wurzelordner: Schlüssel und Namensräume")
    module = {p.name: p.read_text(encoding="utf-8") for p in sorted(WURZEL.glob("*.js"))}
    abgefragt = {m: set(JS_AUFRUF.findall(t)) for m, t in module.items()}
    fehlt_js = sorted(f"{m}: {s}" for m, ks in abgefragt.items() for s in ks if s not in flach[basis])
    pruef(not fehlt_js, f"{sum(len(v) for v in abgefragt.values())} Abfragen in {sum(1 for v in abgefragt.values() if v)} Modulen, jeder Schlüssel vorhanden"
          + (f": fehlt {', '.join(fehlt_js[:6])}" if fehlt_js else ""))
    std = k.get("standardsprache", sprachen[0])
    ohne_ns, entfaellt_geladen = [], []
    for l in sprachen:
        for seite in sorted((WURZEL if l == std else WURZEL / l).glob("*.html")):
            h = seite.read_text(encoding="utf-8")
            srcs = [x.split("?")[0].replace("../", "") for x in re.findall(r'<script[^>]*\bsrc="([^"]+)"', h)]
            ns_geladen = {x.split("/")[-1][:-3] for x in srcs if x.startswith(f"texte/{l}/")}
            for x in srcs:
                if x in JS_ENTFAELLT:
                    entfaellt_geladen.append(f"{seite.relative_to(WURZEL)}: {x}")
                fehlend = sorted({s.split(".")[0] for s in abgefragt.get(x, ())} - ns_geladen)
                if fehlend:
                    ohne_ns.append(f"{seite.relative_to(WURZEL)}: {x} braucht {', '.join(fehlend)}")
    pruef(not ohne_ns, "jede Seite lädt die Namensräume ihrer Module" + (f": {'; '.join(ohne_ns[:4])}" if ohne_ns else ""))
    pruef(not entfaellt_geladen, f"keine Seite lädt entfallene Module ({', '.join(sorted(JS_ENTFAELLT))})"
          + (f": {'; '.join(entfaellt_geladen[:4])}" if entfaellt_geladen else ""))

    print("Keine deutschen Satzteile in den Zeichenketten der Module")
    benutzt_aus: set[tuple[str, str]] = set()
    for m, t in module.items():
        if m in JS_ENTFAELLT:
            continue
        treffer = []
        for z, inhalt in js_zeichenketten(t):
            w = JS_GROSS.search(inhalt) or JS_MERKMAL.search(inhalt) or (JS_KLEIN.search(inhalt) if re.search(r"\s", inhalt) else None)
            if not w:
                continue
            aus = next((a for a in JS_AUSNAHMEN if a[0] == m and inhalt.startswith(a[1])), None)
            if aus:
                benutzt_aus.add(aus); continue
            treffer.append(f"{m}:{z} „{w.group(0)}“ in „{inhalt[:50]}“")
        pruef(not treffer, f"{m}: keine deutschen Satzteile in Zeichenketten" + (f" ({len(treffer)}: {'; '.join(treffer[:3])})" if treffer else ""))
    veraltet = sorted(f"{a[0]}: „{a[1]}“" for a in JS_AUSNAHMEN if a not in benutzt_aus)
    pruef(not veraltet, f"{len(JS_AUSNAHMEN)} begründete Ausnahmen, alle noch nötig" + (f": veraltet {'; '.join(veraltet[:4])}" if veraltet else ""))

    print("Falschsatz-Listen je Sprache")
    fl = json.loads((WURZEL / "pruefen" / "d3_falschsaetze.json").read_text(encoding="utf-8"))
    for l in sprachen:
        eintraege = fl.get("alle", []) + fl.get(l, [])
        ohne_grund = [e.get("muster") for e in eintraege if not str(e.get("grund", "")).strip()]
        texte_l = [(s, str(x)) for s, v in flach[l].items()
                   for x in ([v] if isinstance(v, str) else list(v.values()) if isinstance(v, dict) else [])]
        ordner = WURZEL if l == std else WURZEL / l
        seiten_l = [(str(p.relative_to(WURZEL)), sichtbar(p, l != "de")) for p in sorted(ordner.glob("*.html"))]
        treffer = []
        for e in eintraege:
            rx = re.compile(e["muster"])
            # „ausser“: Fundorte (Textschlüssel oder Seite), an denen das Muster sachlich richtig ist, mit Grund
            aus = e.get("ausser") or {}
            if aus and not str(aus.get("grund", "")).strip():
                ohne_grund.append(e.get("muster") + " (ausser)")
            arx = re.compile(aus["fundorte"]) if aus else None
            treffer += [f"{wo}: „{m.group(0)}“" for wo, tx in texte_l + seiten_l for m in [rx.search(tx)]
                        if m and not (arx and arx.fullmatch(wo))]
        pruef(not ohne_grund and not treffer, f"{l}: {len(eintraege)} Falschsatz-Muster ohne Treffer in {len(texte_l)} Texten und {len(seiten_l)} Seiten"
              + (f": ohne Grund {ohne_grund}" if ohne_grund else "") + (f": {'; '.join(treffer[:4])}" if treffer else ""))

    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
