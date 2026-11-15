"""Prüfung Paket Wohnungsmarkt (DW): daten/mieszkania_odbl.js gegen Vertrag, Protokoll und Datenschutzgrenze.

Ohne Netz und ohne Datenbank. Prüft (Regeln: pruefen/DW_protokoll.md):
  1. Vertrag daten/schema/mieszkania_odbl.json (mit dem Prüfer aus pruefen/daten.py).
  2. Mindestfallzahl: kein Median bei n < mindestfallzahl; jeder leere Median mit dem passenden Grund
     (n = 0 -> keine_transaktionen, unter dem Minimum -> n_unter_minimum); kein Grund neben einem Median.
     Unter dem Minimum steht auch keine Fallzahl (n = null; pruefen/N1_protokoll.md, Regel 4).
  3. Datenschutz: keine Felder für Extremwerte, Perzentile, Mittelwerte, Kennungen, Adressen oder Dokumente.
  4. Summen (soweit die Fallzahlen veröffentlicht sind): n(ogolem) >= n(pierwotny) + n(wtorny); Stadt = Summe der
     dzielnice je Jahr und Markt, mit unterdrückten Feldern Stadt >= Summe der gezeigten; Zählungen F0…F11 in
     Reihenfolge und nie steigend; letzte Zählung = Summe n(ogolem), mit unterdrückten Feldern >= Summe;
     außerhalb = F9 − F10; Preis aus Lokal + aus Transaktion = F6.
  5. Jahre und dzielnice: Jahresschlüssel = jahre; kein Jahr vor regeln.erstes_jahr (Änderung KR55);
     dzielnice = nr in daten/stadtteile_odbl.js.
  6. Beispieldaten: eingabe.art „beispiel“ genau dann, wenn fixture: true; echte Eingabe mit SHA256;
     Kopf mit Quellenangabe (art. 40c ust. 3) und dem Wort BEISPIELDATEN genau bei Beispieldaten.
  7. Gegenprobe: dieselben Prüfungen auf absichtlich verfälschten Kopien müssen anschlagen (sonst ist die
     Prüfung wirkungslos).
  8. Reproduzierbar: skripte/40_mieszkania.py --pruefen (byte-gleich, auch belege/DW_mieszkania.md).
  9. Texte texte/<lang>/mieszkania.js (seit dem 14.11.2026 nur noch dort, KR43): Namensraum, gleiche Schlüssel,
     Platzhalter, Pluralformen, keine leeren Texte, mit Gegenprobe; Text für „n < Mindestzahl“ vorhanden.
 10. Differenzprobe (pruefen/N1_protokoll.md, Regel 4.5, Nachträge 2 und 3): im ganzen veröffentlichten System
     (Stadt = Summe der dzielnice, ogolem = pierwotny + wtorny + ohne Marktangabe, Summe über die Jahre = letzte
     Zählung (F11),
     Summe ohne Marktangabe = kontrolle.ohne_markt, Schranken) hat keine Fallzahl unter der Mindestzahl genau einen
     ganzzahligen Wert (Befund sonst, auch bei unlösbarem System); eigene Rechnung mit scipy.optimize.linprog, nicht
     die des Erzeugers; verdeckte Fallzahlen (n_verdeckt) nur neben einem Median; Gegenproben auf kleinen erfundenen
     Tabellen, je ein Rückrechenweg.

Aufruf: python -I pruefen/DW_mieszkania.py [--ohne-lauf]   Rückgabe 0 = 0 Befunde, 1 = Befund.
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "pruefen"))   # python -I lässt das Skriptverzeichnis weg
from daten import js_lesen, validieren  # noqa: E402

DATEI = WURZEL / "daten" / "mieszkania_odbl.js"
SCHEMA = WURZEL / "daten" / "schema" / "mieszkania_odbl.json"
STADTTEILE = WURZEL / "daten" / "stadtteile_odbl.js"
MAERKTE = ("ogolem", "pierwotny", "wtorny")
VERBOTEN = re.compile(r"^(min|max|minimum_preis|maximum|p\d+|q\d|perzentil.*|quantil.*|quartil.*|mittel.*|mean|"
                      r"avg|sd|std.*|adres.*|ulica|strasse|hausnr|numer.*|nr_dzialki|dzialka|id_.*|.*_id|"
                      r"identyfikator.*|teryt|oznaczenie.*|dokument.*|lon|lat|x|y|geometry|transakcje|einzel.*)$",
                      re.IGNORECASE)
ERLAUBT = {"datei", "sha256", "erzeuger"}  # Felder, die VERBOTEN berühren könnten, aber Metadaten der Eingabe sind
# Texte der Seite (Namensraum mieszkania.*); die Verwendung prüft pruefen/texte.py
TEXTE = WURZEL / "texte"
PLURAL = {"pl": {"one", "few", "many", "other"}, "en": {"one", "other"}, "de": {"one", "other"}}
TEXT_ZEILE = re.compile(r'^\s*T\["([^"]+)"\]\s*=\s*(.+);\s*$')
PLATZ = re.compile(r"\{([a-z_]+)\}")


def texte_befunde(ordner: Path = TEXTE) -> list[str]:
    """Befunde der Texte: Namensraum, gleiche Schlüssel, Platzhalter, Pluralformen, keine leeren Texte."""
    bf, je = [], {}
    for lang in PLURAL:
        p = ordner / lang / "mieszkania.js"
        if not p.is_file():
            bf.append(f"{p} fehlt")
            continue
        werte = {}
        for z in p.read_text(encoding="utf-8").splitlines():
            m = TEXT_ZEILE.match(z)
            if m:
                werte[m.group(1)] = json.loads(m.group(2))
        je[lang] = werte
        for k, v in werte.items():
            if not re.fullmatch(r"mieszkania\.[a-z0-9_]+(\.[a-z0-9_]+)*", k):
                bf.append(f"{lang}: Schlüssel {k} außerhalb des Namensraums mieszkania.*")
            if isinstance(v, dict):
                if set(v) != PLURAL[lang]:
                    bf.append(f"{lang}: {k} Pluralformen {sorted(v)}")
                if any("{n}" not in str(x) for x in v.values()):
                    bf.append(f"{lang}: {k} Pluralform ohne {{n}}")
            if not v or (isinstance(v, dict) and not all(v.values())):
                bf.append(f"{lang}: {k} leer")
    if len(je) == len(PLURAL):
        alle = set().union(*(set(w) for w in je.values()))
        for lang, w in je.items():
            if set(w) != alle:
                bf.append(f"{lang}: Schlüssel fehlen {sorted(alle - set(w))}")
        for k in alle:
            mengen = {frozenset(PLATZ.findall(json.dumps(w.get(k), ensure_ascii=False))) for w in je.values()}
            if len(mengen) > 1:
                bf.append(f"{k}: Platzhalter je Sprache verschieden")
    return bf


def schluessel(o, aus: set) -> set:
    if isinstance(o, dict):
        for k, v in o.items():
            aus.add(k)
            schluessel(v, aus)
    elif isinstance(o, list):
        for v in o:
            schluessel(v, aus)
    return aus


def zellen(o: dict):
    for ort, reihe in [("stadt", o.get("stadt", {})), *o.get("stadtteile", {}).items()]:
        for j, mm in reihe.items():
            for m, w in mm.items():
                yield ort, j, m, w


def befunde_fuer(o: dict, kopf: str, schema: dict, nrs: set) -> list[str]:
    b: list[str] = []
    f: list[str] = []
    validieren(o, schema, schema, "$", f, {})
    b += [f"Vertrag: {x}" for x in f[:5]]
    if f:
        return b
    mind = o["regeln"]["mindestfallzahl"]
    for ort, j, m, w in zellen(o):
        wo = f"{ort}/{j}/{m}"
        if w.get("n_verdeckt") is not None and (w["n_verdeckt"] is not True or w["n"] is not None
                                                 or w["median"] is None or "grund" in w):
            b.append(f"{wo}: n_verdeckt nur mit Median, ohne Grund und mit n = null")
        if w["median"] is not None and ((w["n"] is None and not w.get("n_verdeckt")) or (w["n"] is not None and w["n"] < mind)):
            b.append(f"{wo}: Median bei n = {w['n']} < {mind}")
        if w["median"] is not None and "grund" in w:
            b.append(f"{wo}: Grund neben einem Median")
        if w["n"] is not None and 0 < w["n"] < mind:
            b.append(f"{wo}: Fallzahl {w['n']} unter der Mindestzahl veröffentlicht")
        if w.get("grund") == "n_unter_minimum" and w["n"] is not None:
            b.append(f"{wo}: n_unter_minimum mit Fallzahl")
        if w["median"] is None:
            soll = ("n_unter_minimum" if w["n"] is None else "keine_transaktionen" if w["n"] == 0
                    else ("n_unter_minimum" if w["n"] < mind else None))
            if soll is None:
                b.append(f"{wo}: Median leer bei n = {w['n']} >= {mind}")
            elif w.get("grund") != soll:
                b.append(f"{wo}: Grund {w.get('grund')!r}, erwartet {soll!r}")
    verb = sorted(k for k in schluessel(o, set()) - ERLAUBT if VERBOTEN.match(k))
    if verb:
        b.append(f"verbotene Felder (Datenschutz): {verb[:6]}")
    for ort, reihe in [("stadt", o["stadt"]), *o["stadtteile"].items()]:
        for j, mm in reihe.items():
            if None not in (mm["ogolem"]["n"], mm["pierwotny"]["n"], mm["wtorny"]["n"]) \
                    and mm["ogolem"]["n"] < mm["pierwotny"]["n"] + mm["wtorny"]["n"]:
                b.append(f"{ort}/{j}: n(ogolem) < n(pierwotny) + n(wtorny)")
    for j in o["stadt"]:
        for m in MAERKTE:
            ns = [r[j][m]["n"] for r in o["stadtteile"].values() if j in r]
            s, st = sum(x for x in ns if x is not None), o["stadt"][j][m]["n"]
            if st is not None and (s != st if None not in ns else s > st):
                b.append(f"stadt/{j}/{m}: n = {st}, Summe der dzielnice {s}")
    k = o["kontrolle"]
    nrn = [s["nr"] for s in k["schritte"]]
    if nrn != [f"F{i}" for i in range(12)]:
        b.append(f"Schritte {nrn}, erwartet F0…F11")
    werte = [s["n"] for s in k["schritte"]]
    if any(a < c for a, c in zip(werte, werte[1:])):
        b.append(f"Zählungen steigen zwischen zwei Schritten: {werte}")
    ns = [w["n"] for ort, _, m, w in zellen(o) if ort != "stadt" and m == "ogolem"]
    summe = sum(x for x in ns if x is not None)
    if werte and (werte[-1] != summe if None not in ns else werte[-1] < summe):
        b.append(f"letzte Zählung = {werte[-1]}, Summe n(ogolem) der dzielnice = {summe}")
    if len(werte) == 12:
        if k["ausserhalb"] != werte[9] - werte[10]:
            b.append(f"außerhalb = {k['ausserhalb']}, F9 − F10 = {werte[9] - werte[10]}")
        if k["preis_aus_lokal"] + k["preis_aus_transaktion"] != werte[6]:
            b.append("Preis aus Lokal + aus Transaktion ≠ Zählung nach F6")
    jahre = [str(j) for j in o["jahre"]]
    if jahre != sorted(jahre) or any(list(r) != jahre for r in [o["stadt"], *o["stadtteile"].values()]):
        b.append("Jahresschlüssel weichen von jahre ab oder sind nicht sortiert")
    frueh = [j for j in o["jahre"] if j < o["regeln"]["erstes_jahr"]]
    if frueh:
        b.append(f"Jahre vor dem ersten Jahr {o['regeln']['erstes_jahr']} veröffentlicht: {frueh}")
    if set(o["stadtteile"]) != nrs:
        b.append(f"dzielnice {sorted(o['stadtteile'])} ≠ nr in stadtteile_odbl.js {sorted(nrs)}")
    beispiel = o["eingabe"]["art"] == "beispiel"
    if beispiel != (o.get("fixture") is True):
        b.append("eingabe.art und fixture passen nicht zusammen")
    if not beispiel and not o["eingabe"]["sha256"]:
        b.append("echte Eingabe ohne SHA256")
    if "Źródło:" not in kopf or "art. 40c" not in kopf:
        b.append("Kopf ohne Quellenangabe (Źródło, art. 40c ust. 3)")
    if ("BEISPIELDATEN" in kopf) != beispiel:
        b.append("Kopf: Wort BEISPIELDATEN passt nicht zur Art der Eingabe")
    return b


def zurueckrechenbar(o: dict) -> int:
    """Unabhängig vom Erzeuger (pruefen/N1_protokoll.md, Nachtrag 3): Zahl der Fallzahlen unter der Mindestzahl, deren
    zulässiger Bereich im veröffentlichten System höchstens eine ganze Zahl enthält. Gerechnet mit der stetigen
    Lockerung (scipy.optimize.linprog); ein unlösbares System zählt als Befund (Rückgabe −1)."""
    import numpy as np
    from scipy.optimize import linprog
    mind = o["regeln"]["mindestfallzahl"]
    jahre = list(o["stadt"])
    dz = sorted(o["stadtteile"])
    spalten: list[tuple] = []          # (ort, jahr, markt); markt "rest" = Käufe ohne Marktangabe, nie veröffentlicht
    for ort in ["stadt", *dz]:
        for j in jahre:
            spalten += [(ort, j, m) for m in ("ogolem", "pierwotny", "wtorny", "rest")]
    pos = {k: i for i, k in enumerate(spalten)}
    gl, rs = [], []

    def summe(plus, minus, wert):
        z = [0.0] * len(spalten)
        for k in plus:
            z[pos[k]] += 1
        for k in minus:
            z[pos[k]] -= 1
        gl.append(z)
        rs.append(wert)
    for j in jahre:
        for m in ("ogolem", "pierwotny", "wtorny", "rest"):
            summe([("stadt", j, m)], [(d, j, m) for d in dz], 0)          # Stadt = Summe der dzielnice
        for ort in ["stadt", *dz]:                                       # ogolem = pierwotny + wtorny + rest
            summe([(ort, j, "ogolem")], [(ort, j, "pierwotny"), (ort, j, "wtorny"), (ort, j, "rest")], 0)
    schritte = {s["nr"]: s["n"] for s in o["kontrolle"]["schritte"]}
    if schritte:          # fehlt nur in den Gegenproben, die einen Weg allein prüfen
        letzte = o["kontrolle"]["schritte"][-1]["n"]          # Summe über die Jahre = letzte Zählung (F11, KR55)
        summe([("stadt", j, "ogolem") for j in jahre], [], letzte)
    if "ohne_markt" in o["kontrolle"]:
        summe([(d, j, "rest") for d in dz for j in jahre], [], o["kontrolle"]["ohne_markt"])
    grenzen, ziele = [], []
    for ort, j, m in spalten:
        if m == "rest":
            grenzen.append((0, None))
            continue
        w = (o["stadt"] if ort == "stadt" else o["stadtteile"][ort])[j][m]
        if w.get("n") is not None:
            grenzen.append((w["n"], w["n"]))
        elif w.get("grund") == "n_unter_minimum":
            grenzen.append((1, mind - 1))
            ziele.append(pos[(ort, j, m)])
        else:
            grenzen.append((mind, None))
    A, b = np.array(gl), np.array(rs, dtype=float)
    treffer = 0
    for i in ziele:
        c = np.zeros(len(spalten))
        c[i] = 1
        unten = linprog(c, A_eq=A, b_eq=b, bounds=grenzen, method="highs")
        oben = linprog(-c, A_eq=A, b_eq=b, bounds=grenzen, method="highs")
        if unten.status != 0 or oben.status != 0:
            return -1
        if np.floor(-oben.fun + 1e-6) - np.ceil(unten.fun - 1e-6) < 1:
            treffer += 1
    return treffer


def tabelle_klein(stadt_ogolem: dict, dz_werte: dict, f10: int, ohne_markt: int, mind: int = 10) -> dict:
    """Erfundene kleine Tabelle für die Gegenproben der Differenzprobe: dz_werte[(nr, jahr)] = (ogolem, pierwotny,
    wtorny), Zahl unter der Mindestzahl -> n_unter_minimum; Stadt = Summe; stadt_ogolem[jahr] = "verdeckt" verdeckt."""
    def zelle(n):
        if n == "verdeckt":
            return {"median": 1, "n": None, "n_verdeckt": True}
        if n == 0:
            return {"median": None, "n": 0, "grund": "keine_transaktionen"}
        return {"median": None, "n": None, "grund": "n_unter_minimum"} if n < mind else {"median": 1, "n": n}
    jahre = sorted({j for _, j in dz_werte})
    nrs = sorted({nr for nr, _ in dz_werte})
    o = {"regeln": {"mindestfallzahl": mind}, "kontrolle": {"schritte": [{"nr": "F10", "n": f10}], "ohne_markt": ohne_markt},
         "stadtteile": {nr: {j: dict(zip(("ogolem", "pierwotny", "wtorny"), map(zelle, dz_werte[(nr, j)])))
                             for j in jahre} for nr in nrs}, "stadt": {}}
    for j in jahre:
        o["stadt"][j] = {m: zelle(sum(dz_werte[(nr, j)][i] for nr in nrs)) for i, m in
                         enumerate(("ogolem", "pierwotny", "wtorny"))}
        if stadt_ogolem.get(j) == "verdeckt":
            o["stadt"][j]["ogolem"] = zelle("verdeckt")
    return o


def gegenprobe_differenz() -> list[tuple[str, bool]]:
    """Kleine erfundene Tabellen (2 dzielnice, 2 Jahre), je ein gepflanzter Rückrechenweg; die Differenzprobe muss
    jeden finden. Der Weg über F10 und der über ohne_markt werden je allein geprüft (die andere Summe fehlt in der
    Kopie); ohne beide Summen und mit ausreichender Verdeckung darf nichts anschlagen."""
    # dzielnica b, Jahr 2: ogolem 7 (unter der Mindestzahl); pierwotny und wtorny dort 0 (veröffentlicht)
    werte = {("a", "1"): (40, 15, 20), ("b", "1"): (30, 12, 14), ("a", "2"): (50, 20, 25), ("b", "2"): (7, 0, 0)}
    rest = sum(og - p - w for og, p, w in werte.values())
    f10 = sum(og for og, _, _ in werte.values())

    def ohne(t, was):
        if was == "F10":
            t["kontrolle"]["schritte"] = []
        else:
            t["kontrolle"].pop("ohne_markt")
        return t
    erg = [("Weg Stadt minus dzielnica", zurueckrechenbar(tabelle_klein({}, werte, f10, rest)) > 0)]
    # Stadt 2 (ogolem) verdeckt: der alte Weg ist zu, F10 minus Jahr 1 bzw. ohne_markt öffnen ihn wieder
    erg.append(("Weg über F10 (Summe über die Jahre)",
                zurueckrechenbar(ohne(tabelle_klein({"2": "verdeckt"}, werte, f10, rest), "ohne_markt")) > 0))
    erg.append(("Weg über ohne_markt",
                zurueckrechenbar(ohne(tabelle_klein({"2": "verdeckt"}, werte, f10, rest), "F10")) > 0))
    t = ohne(ohne(tabelle_klein({"2": "verdeckt"}, werte, f10, rest), "F10"), "ohne_markt")
    erg.append(("ohne F10 und ohne_markt bleibt die verdeckte Tabelle ohne Befund", zurueckrechenbar(t) == 0))
    # ausreichend verdeckt: zusätzlich dzielnica a, Jahr 2 (ogolem), mit beiden Summen
    t = tabelle_klein({"2": "verdeckt"}, werte, f10, rest)
    t["stadtteile"]["a"]["2"]["ogolem"] = {"median": 1, "n": None, "n_verdeckt": True}
    erg.append(("ausreichend verdeckte Tabelle bleibt ohne Befund", zurueckrechenbar(t) == 0))
    return erg


def gegenprobe(o: dict, kopf: str, schema: dict, nrs: set) -> list[tuple[str, bool, list]]:
    """Verfälschte Kopien; jede muss einen Befund mit dem erwarteten Wortlaut ergeben."""
    erg = []
    nr0 = sorted(o["stadtteile"])[0]
    j0 = str(o["jahre"][0])

    def fall(name, erwartet, aendern, k=kopf):
        x = copy.deepcopy(o)
        aendern(x)
        bf = befunde_fuer(x, k, schema, nrs)
        erg.append((name, any(erwartet in t for t in bf), bf))

    def median_bei_9(x):
        x["stadtteile"][nr0][j0]["pierwotny"] = {"median": 12345, "n": 9}
    fall("Median bei n = 9", "Median bei n = 9", median_bei_9)

    def maximum(x):
        x["stadtteile"][nr0][j0]["ogolem"]["max"] = 99999
    fall("Feld max in einer Zelle", "Feld max nicht im Vertrag", maximum)

    def ohne_grund(x):
        for _, _, _, w in zellen(x):     # erste Zelle mit leerem Median: Grund entfernen
            if w["median"] is None:
                w.pop("grund", None)
                return
        x["stadtteile"][nr0][j0]["ogolem"] = {"median": None, "n": 1}   # keine leere Zelle: eine erzeugen
    fall("leerer Median ohne Grund", "Grund None", ohne_grund)

    # erstes Jahr mit veröffentlichter Stadtzahl (echte Daten: frühe Jahre liegen unter der Mindestzahl)
    j_stadt = next((str(j) for j in o["jahre"] if o["stadt"][str(j)]["ogolem"].get("n")), j0)

    def stadt_falsch(x):
        x["stadt"][j_stadt]["ogolem"]["n"] = 0      # kleiner als die Summe der gezeigten dzielnice
    fall("Stadt ≠ Summe der dzielnice", "Summe der dzielnice", stadt_falsch)

    def ohne_fixture(x):
        x.pop("fixture", None)
        x["eingabe"]["art"] = "beispiel"
    fall("Beispiel ohne fixture", "eingabe.art und fixture", ohne_fixture)

    def einzelfall(x):
        x["einzelfaelle"] = [{"adres": "ul. Przykładowa 1", "cena": 500000}]
    fall("Liste von Einzelfällen", "Feld einzelfaelle nicht im Vertrag", einzelfall)

    fall("Kopf ohne Quellenangabe", "Kopf ohne Quellenangabe", lambda x: None, k="/* ohne */")

    def kleine_fallzahl(x):
        x["stadtteile"][nr0][j0]["pierwotny"] = {"median": None, "n": 4, "grund": "n_unter_minimum"}
    fall("Fallzahl unter der Mindestzahl veröffentlicht", "unter der Mindestzahl veröffentlicht", kleine_fallzahl)

    def frueheres_jahr(x):         # Änderung KR55: ein Jahr vor erstes_jahr eingepflanzt, mit leeren Feldern
        jf = x["regeln"]["erstes_jahr"] - 1
        leer = {m: {"median": None, "n": 0, "grund": "keine_transaktionen"} for m in MAERKTE}
        x["jahre"] = [jf, *x["jahre"]]
        for r in [x["stadt"], *x["stadtteile"].values()]:
            alt = dict(r)
            r.clear()
            r[str(jf)] = copy.deepcopy(leer)
            r.update(alt)
    fall("Jahr vor dem ersten Jahr", "vor dem ersten Jahr", frueheres_jahr)
    return erg


def main() -> int:
    befunde: list[str] = []

    def pruef(ok: bool, text: str) -> None:
        print(("  ok    " if ok else "  FEHLT ") + text)
        if not ok:
            befunde.append(text)

    text = DATEI.read_text(encoding="utf-8")
    kopf, name, o = js_lesen(DATEI, text)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    _, _, st = js_lesen(STADTTEILE)
    nrs = {f["properties"]["nr"] for f in st["features"]}
    pruef(name == "KIEZ_MIESZKANIA", f"globaler Name {name}")
    b = befunde_fuer(o, kopf, schema, nrs)
    pruef(not b, "Vertrag, Mindestfallzahl, Datenschutz, Summen, Jahre, Kennzeichnung"
          + (": " + "; ".join(b[:6]) if b else ""))
    mit = sum(1 for _, _, _, w in zellen(o) if w["median"] is not None)
    leer = sum(1 for _, _, _, w in zellen(o) if w["median"] is None)
    print(f"        {mit} Werte mit Median, {leer} leer (Mindestfallzahl {o['regeln']['mindestfallzahl']}); "
          f"Eingabe: {o['eingabe']['art']}" + (" (BEISPIELDATEN)" if o.get("fixture") else ""))
    print("Gegenprobe mit verfälschten Kopien")
    for fall, ok, bf in gegenprobe(o, kopf, schema, nrs):
        pruef(ok, f"erkannt: {fall}" + ("" if ok else f" (Befunde: {bf[:3]})"))
    print("Texte texte/<lang>/mieszkania.js")
    tb = texte_befunde()
    pruef(not tb, "Namensraum, gleiche Schlüssel in pl/en/de, Platzhalter, Pluralformen, keine leeren Texte"
          + (": " + "; ".join(tb[:4]) if tb else ""))
    pruef(all('T["mieszkania.n_unter_min"]' in (TEXTE / l / "mieszkania.js").read_text(encoding="utf-8") for l in PLURAL),
          "Text für „n < Mindestzahl“ in pl, en, de")
    print("Differenzprobe (Nachträge 2 und 3: Befund, wenn eine unterdrückte Fallzahl zurückrechenbar ist)")
    zr = zurueckrechenbar(o)
    pruef(zr == 0, "aus veröffentlichten Summen zurückrechenbare unterdrückte Fallzahlen: "
          + ("System unlösbar (veröffentlichte Zahlen widersprechen sich)" if zr < 0 else str(zr)))
    nv = sum(1 for _, _, _, w in zellen(o) if w.get("n_verdeckt"))
    print(f"        verdeckte Fallzahlen (sekundäre Unterdrückung): {nv}")
    for fall, ok in gegenprobe_differenz():
        pruef(ok, f"Gegenprobe Differenzprobe: {fall}")
    with tempfile.TemporaryDirectory() as tmp:   # Gegenprobe: verfälschte Kopie (pl ohne einen Schlüssel, en mit pl-Pluralformen)
        for lang in PLURAL:
            (Path(tmp) / lang).mkdir()
            zeilen = (TEXTE / lang / "mieszkania.js").read_text(encoding="utf-8").splitlines()
            if lang == "pl":
                zeilen = [z for z in zeilen if '"mieszkania.einheit"' not in z]
            if lang == "en":
                zeilen = [z.replace('{"one":', '{"few": "{n} x", "one":') for z in zeilen]
            (Path(tmp) / lang / "mieszkania.js").write_text("\n".join(zeilen), encoding="utf-8")
        tg = texte_befunde(Path(tmp))
    pruef(any("Schlüssel fehlen" in t for t in tg) and any("Pluralformen" in t for t in tg),
          "Gegenprobe Text: fehlender Schlüssel und falsche Pluralformen erkannt")
    if "--ohne-lauf" not in sys.argv:
        print("Reproduzierbar (skripte/40_mieszkania.py --pruefen)")
        r = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / "40_mieszkania.py"), "--pruefen"],
                           capture_output=True, text=True)
        print(r.stdout.rstrip() + (("\n" + r.stderr.rstrip()) if r.stderr.strip() else ""))
        pruef(r.returncode == 0, f"40_mieszkania.py --pruefen, Rückgabe {r.returncode}")
    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
