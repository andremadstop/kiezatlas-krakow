"""Prüfung Paket Luft (D7): daten/powietrze.js gegen Vertrag, Protokoll, Zählung und Textregeln.

Prüft (kein Netz, keine Datenbank, kein Browser):
  1. Vertrag daten/schema/powietrze.json (Prüfer aus pruefen/daten.py).
  2. Festlegungen aus pruefen/D7_protokoll.md: Jahre 2010–2025, Fenster 2016–2018 / 2019 / 2020–2022, Umland 30 km,
     Deckung 75 / 85 %, Grenzwerte und Fundstellen (Dz.U. 2021 poz. 845, załącznik nr 1, von Hand aus dem PDF
     abgelesen und hier ein zweites Mal eingetragen), Stichtag 2019-09-01, Abzeichen „orientacyjnie“.
  3. Zählung in sich stimmig: Eingabe = verwendet + Summe der Verwerfungsgründe; Werte, Stationen, `niepelne`
     und Vorher/Nachher-Paare nachgezählt aus `stacje`.
  4. Je Wert: Deckung ≥ 75 %, `niepelne` genau bei Deckung < 85 %, Jahr in `lata`, ganze Zahl bei Tagen/Stunden.
  5. Vorher/Nachher nur, wenn alle drei Jahre des Fensters einen Wert haben; das Mittel passt zu den gerundeten
     Jahreswerten (Abweichung ≤ 0,1: das Mittel wird nach Regel 5 des Protokolls aus den ungerundeten Werten
     gerechnet und erst dann gerundet; die Prüfung kennt nur die gerundeten Jahreswerte, deren Mittel bis 0,05
     abweicht, dazu bis 0,05 aus der Rundung des Mittels); fehlt ein Jahr, steht `null` mit Grund.
  6. Stationen: Umland höchstens 30 km, Abstand zum Mittelpunkt nachgerechnet; Beispieldaten nur mit
     Kennungen FIKCJA-… und umgekehrt.
  7. Reproduzierbar: skripte/32_powietrze.py --pruefen (byte-gleich, Rückgabe 0).
  8. Texte des Namensraums powietrze.* (texte/<lang>/powietrze.js, solange die Seite fehlt der Vorschlag unter
     docs/entscheidungen/D7_texte/<lang>/powietrze.js): Textformat, gleiche Schlüssel und Platzhalter in pl/en/de,
     Pluralformen, Begriffe für alle Kennwerte, Typen und Gebietstypen der Daten, keine deutschen Wörter in pl/en,
     keine Kausalwendung (Liste KAUSAL, Protokoll Abschnitt 5) und keine Treffer aus pruefen/d3_falschsaetze.json.

  --selbsttest  verfälscht Kopien der Daten und Texte im Speicher und erwartet je Fall einen Befund
                (prüft, dass die Prüfungen greifen).

Aufruf: python -I pruefen/D7_powietrze.py [--selbsttest] [--ohne-lauf]   Rückgabe 0 = grün, 1 = Befund.
  --ohne-lauf   Punkt 7 auslassen (braucht die Rohdaten unter $KIEZ_DATEN; für die CI)
"""
from __future__ import annotations

import copy
import json
import math
import re
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
sys.path.insert(0, str(WURZEL / "pruefen"))
import daten as datenpruefung  # noqa: E402
import textschicht  # noqa: E402

DATEI = WURZEL / "daten" / "powietrze.js"
SCHEMA = WURZEL / "daten" / "schema" / "powietrze.json"
SPRACHEN = ("pl", "en", "de")

# ---------------------------------------------------------------- Protokoll (zweite, unabhängige Abschrift)
JAHRE = list(range(2010, 2026))
OKNA = {"przed": [2016, 2018], "przejscie": 2019, "po": [2020, 2022]}
UMLAND_KM, DECKUNG_MIN, DECKUNG_VOLL = 30.0, 75.0, 85.0
# Mittel aus ungerundeten Werten, gerundet auf 0,1 (Protokoll Regel 5); nachgerechnet aus Werten auf 0,1 gerundet:
# je Jahreswert bis 0,05 Rundungsfehler, im Mittel also bis 0,05, dazu bis 0,05 aus der Rundung des Mittels
TOLERANZ_MITTEL = 0.1
FELDER = ("pm10_srednia", "pm10_dni", "pm25_srednia", "no2_srednia", "no2_godziny")
GANZ = {"pm10_dni", "no2_godziny"}
# Feld -> Liste (Wert, Okres, dopuszczalna częstość oder None, ab Jahr, Lp. mit Fußnote)
GRENZEN = {
    "pm10_srednia": [(40, "rok kalendarzowy", None, 2005, "lp. 7")],
    "pm10_dni": [(50, "24 godziny", 35, 2005, "lp. 7")],
    "pm25_srednia": [(25, "rok kalendarzowy", None, 2015, "lp. 6, przypis j"),
                     (20, "rok kalendarzowy", None, 2020, "lp. 6, przypis k")],
    "no2_srednia": [(40, "rok kalendarzowy", None, 2010, "lp. 2")],
    "no2_godziny": [(200, "jedna godzina", 18, 2010, "lp. 2")],
}
KAUSAL = {
    "pl": r"(?i)dzięki zakaz|z powodu zakaz|zakaz\w* spowodował|w wyniku zakaz|zakaz\w* sprawił",
    "en": r"(?i)because of the ban|thanks to the ban|due to the ban|the ban caused|as a result of the ban|"
          r"the ban (led|has led) to",
    "de": r"(?i)wegen des Verbots|dank des Verbots|durch das Verbot|das Verbot bewirkte|infolge des Verbots|"
          r"das Verbot führte",
}

befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def haversine(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------- Daten
def daten_pruefen(d: dict, kopf: str, name: str) -> None:
    print("Vertrag")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    fehler: list[str] = []
    if not re.search(schema["x-global"], name):
        fehler.append(f"globaler Name {name}")
    datenpruefung.validieren(d, schema, schema, "$", fehler, {})
    pruef(not fehler, "powietrze.js passt zu daten/schema/powietrze.json" + (f": {'; '.join(fehler[:4])}" if fehler else ""))

    print("Festlegungen aus pruefen/D7_protokoll.md")
    pruef(d.get("lata") == JAHRE, f"Jahre {JAHRE[0]}–{JAHRE[-1]}")
    pruef(d.get("okna") == OKNA, "Fenster vorher 2016–2018, Übergang 2019, nachher 2020–2022")
    r = d.get("reguly", {})
    pruef((r.get("okolica_km"), r.get("pokrycie_min"), r.get("pokrycie_pelne")) == (UMLAND_KM, DECKUNG_MIN, DECKUNG_VOLL),
          "Umland 30 km, Deckung 75 % / 85 %")
    pruef(d.get("abzeichen") == "orientacyjnie", "Abzeichen „orientacyjnie“ (EEA-Jahreswerte, keine amtliche Jahresbewertung)")
    pruef(d.get("kontekst", {}).get("wejscie_w_zycie") == "2019-09-01"
          and "1 września 2019" in d.get("kontekst", {}).get("cytat_wejscie", ""),
          "Stichtag 2019-09-01 mit wörtlichem Zitat aus § 6 ust. 2 der Uchwała")
    pruef("pm25_dni" in d.get("bez_wartosci", {}) and "pm25_dni" not in d.get("kennwerte", {}),
          "keine PM2.5-Überschreitungstage (kein Tagesgrenzwert)")
    abw = []
    for feld, soll in GRENZEN.items():
        ist = d.get("grenzwerte", {}).get(feld, [])
        if len(ist) != len(soll):
            abw.append(f"{feld}: {len(ist)} statt {len(soll)} Einträge")
            continue
        for g, (w, okres, cz, od, lp) in zip(ist, soll):
            if (g.get("wartosc"), g.get("okres"), g.get("dopuszczalna_czestosc"), g.get("od_roku")) != (w, okres, cz, od) \
                    or not g.get("fundstelle", "").endswith(lp):
                abw.append(f"{feld}: {g}")
    pruef(not abw, "Grenzwerte und Fundstellen wie im Protokoll" + (f": {'; '.join(abw[:3])}"[:300] if abw else ""))

    print("Zählung")
    z = d.get("zaehlung", {})
    st = d.get("stacje", [])
    summe = z.get("werte_verwendet", 0) + sum(z.get("verworfen", {}).values())
    pruef(summe == z.get("zeilen_gesamt"), f"Eingabe = verwendet + verworfen ({z.get('zeilen_gesamt')} = {summe})")
    werte = [(s, f, j, e) for s in st for f, reihe in s.get("serie", {}).items() for j, e in reihe.items()]
    pruef(len(werte) == z.get("werte_verwendet"), f"Werte in stacje = werte_verwendet ({len(werte)} = {z.get('werte_verwendet')})")
    rollen = {k: sum(1 for s in st if s["rola"] == k) for k in ("miasto", "okolica")}
    pruef(rollen == z.get("stationen"), f"Stationen je Rolle nachgezählt ({rollen})")
    pruef(len({s["kod"] for s in st}) == len(st), "keine Station doppelt")
    n_niep = sum(1 for *_x, e in werte if e.get("niepelne"))
    pruef(n_niep == z.get("niepelne"), f"niepelne nachgezählt ({n_niep})")
    paare = [(s, f, p) for s in st for f, p in s.get("przed_po", {}).items()]
    voll = sum(1 for *_x, p in paare if "powod" not in p)
    pruef((voll, len(paare) - voll) == (z.get("przed_po_pelne"), z.get("przed_po_brak")),
          f"Vorher/Nachher-Paare nachgezählt ({voll} vollständig, {len(paare) - voll} ohne)")

    print("Werte")
    falsch = []
    for s, f, j, e in werte:
        if int(j) not in JAHRE:
            falsch.append(f"{s['kod']} {f} {j}: Jahr")
        if e["pokrycie"] < DECKUNG_MIN:
            falsch.append(f"{s['kod']} {f} {j}: Deckung {e['pokrycie']}")
        if bool(e.get("niepelne")) != (e["pokrycie"] < DECKUNG_VOLL):
            falsch.append(f"{s['kod']} {f} {j}: niepelne bei Deckung {e['pokrycie']}")
        if f in GANZ and not isinstance(e["w"], int):
            falsch.append(f"{s['kod']} {f} {j}: keine ganze Zahl")
    pruef(not falsch, f"{len(werte)} Werte: Jahr, Deckung, Kennzeichen, ganze Zahlen" + (f": {'; '.join(falsch[:3])}" if falsch else ""))

    falsch = []
    for s, f, p in paare:
        reihe = s.get("serie", {}).get(f, {})
        for okno in ("przed", "po"):
            a, b = OKNA[okno]
            jw = [reihe.get(str(j), {}).get("w") for j in range(a, b + 1)]
            if all(w is not None for w in jw):
                if p[okno] is None or abs(p[okno] - sum(jw) / len(jw)) > TOLERANZ_MITTEL + 1e-9:
                    falsch.append(f"{s['kod']} {f} {okno}: {p[okno]} statt Mittel {sum(jw) / len(jw):.2f}")
            elif p[okno] is not None:
                falsch.append(f"{s['kod']} {f} {okno}: Wert trotz fehlendem Jahr")
        if (p["przed"] is None or p["po"] is None) != (p.get("powod") == "brak_pelnego_okna"):
            falsch.append(f"{s['kod']} {f}: Grund passt nicht")
    pruef(not falsch, f"{len(paare)} Vorher/Nachher-Paare nur mit vollem Fenster, Mittel nachgerechnet" + (f": {'; '.join(falsch[:3])}" if falsch else ""))

    print("Stationen")
    lon0, lat0 = r.get("srodek", [0, 0])
    falsch = []
    for s in st:
        km = haversine(lat0, lon0, s["lat"], s["lon"])
        if abs(km - s["odleglosc_km"]) > 0.2:
            falsch.append(f"{s['kod']}: Abstand {s['odleglosc_km']} statt {km:.1f}")
        if s["rola"] == "okolica" and s["odleglosc_km"] > UMLAND_KM:
            falsch.append(f"{s['kod']}: Umland weiter als {UMLAND_KM:g} km")
    pruef(not falsch, f"{len(st)} Stationen: Abstand nachgerechnet, Umland ≤ {UMLAND_KM:g} km" + (f": {'; '.join(falsch[:3])}" if falsch else ""))
    fik = d.get("fixture") is True
    kennungen_fik = [s["kod"].startswith("FIKCJA-") for s in st]
    pruef(all(kennungen_fik) if fik else not any(kennungen_fik),
          "Beispieldaten genau dann, wenn alle Kennungen FIKCJA-… sind" + (" (fixture: true)" if fik else ""))
    pruef(("BEISPIELDATEN" in kopf) == fik and (d.get("quelle", {}).get("pliki") == []) == fik,
          "Kopfvermerk und Dateiliste passen zu fixture")


# ---------------------------------------------------------------- Texte
def texte_ordner() -> tuple[Path, str]:
    echt = WURZEL / "texte"
    if all((echt / l / "powietrze.js").exists() for l in SPRACHEN):
        return echt, "texte/<lang>/powietrze.js"
    return WURZEL / "docs" / "entscheidungen" / "D7_texte", "Vorschlag docs/entscheidungen/D7_texte/<lang>/powietrze.js"


def texte_lesen(ordner: Path) -> dict[str, dict]:
    aus = {}
    for l in SPRACHEN:
        p = ordner / l / "powietrze.js"
        if not p.exists():
            aus[l] = None
            continue
        try:
            aus[l] = textschicht.datei_lesen(p)
        except textschicht.Textfehler as e:
            aus[l] = e
    return aus


def texte_pruefen(t: dict[str, dict], d: dict, wo: str) -> None:
    import texte as textpruefung  # noqa: PLC0415  (erst hier: Modul liest beim Import nichts)

    print(f"Texte ({wo})")
    lesbar = {l: v for l, v in t.items() if isinstance(v, dict)}
    pruef(len(lesbar) == len(SPRACHEN), "pl, en, de vorhanden und im Textformat"
          + "".join(f"; {l}: {v}" for l, v in t.items() if not isinstance(v, dict)))
    if len(lesbar) != len(SPRACHEN):
        return
    fremd = [k for v in lesbar.values() for k in v if not k.startswith("powietrze.") or not textschicht.SCHLUESSEL.match(k)]
    pruef(not fremd, f"nur Schlüssel powietrze.* ({len(lesbar['pl'])})" + (f": fremd {fremd[:4]}" if fremd else ""))
    pruef(set(lesbar["pl"]) == set(lesbar["en"]) == set(lesbar["de"]), "dieselben Schlüssel in pl, en, de")
    falsch_p, falsch_pl, leer = [], [], []
    for k in lesbar["pl"]:
        mengen = set()
        for l in SPRACHEN:
            v = lesbar[l].get(k)
            if isinstance(v, dict):
                if set(v) != set(textschicht.PLURALFORMEN[l]) or not all("{n}" in str(x) for x in v.values()):
                    falsch_pl.append(f"{l}:{k}")
                mengen.add(frozenset().union(*(textpruefung.PLATZ.findall(str(x)) for x in v.values())))
            elif isinstance(v, str) and v.strip():
                mengen.add(frozenset(textpruefung.PLATZ.findall(v)))
            else:
                leer.append(f"{l}:{k}")
        if len(mengen) > 1:
            falsch_p.append(k)
    pruef(not falsch_p, "gleiche Platzhalter je Schlüssel" + (f": {falsch_p[:4]}" if falsch_p else ""))
    pruef(not falsch_pl, "Pluraltexte mit den Formen der Sprache und {n}" + (f": {falsch_pl[:4]}" if falsch_pl else ""))
    pruef(not leer, "keine leeren Texte" + (f": {leer[:4]}" if leer else ""))

    noetig = {"powietrze.pm25_bez_dni", "powietrze.bez_przyczyny", "powietrze.stichtag", "powietrze.zrodlo_kurz",
              "powietrze.abzeichen." + d.get("abzeichen", ""), "powietrze.niepelne", "powietrze.brak_pelnego_okna"}
    noetig |= {f"powietrze.kennwert.{f}" for f in d.get("kennwerte", {})}
    noetig |= {f"powietrze.rola.{s['rola']}" for s in d.get("stacje", [])}
    noetig |= {f"powietrze.typ.{s['typ'].lower()}" for s in d.get("stacje", []) if s.get("typ")}
    noetig |= {f"powietrze.obszar.{s['obszar'].lower()}" for s in d.get("stacje", []) if s.get("obszar")}
    if d.get("fixture"):
        noetig.add("powietrze.beispieldaten")
    fehlt = sorted(noetig - set(lesbar["pl"]))
    pruef(not fehlt, f"Begriffe für alle Kennwerte, Rollen, Typen und Gebietstypen der Daten ({len(noetig)})"
          + (f": fehlt {fehlt[:5]}" if fehlt else ""))

    deutsch = [f"{l}:{k}" for l in ("pl", "en") for k, v in lesbar[l].items()
               if textpruefung.DEUTSCH.search(json.dumps(v, ensure_ascii=False))]
    pruef(not deutsch, "keine deutschen Wörter in pl und en" + (f": {deutsch[:4]}" if deutsch else ""))
    listen = json.loads((WURZEL / "pruefen" / "d3_falschsaetze.json").read_text(encoding="utf-8"))
    treffer = []
    for l in SPRACHEN:
        text = "\n".join(json.dumps(v, ensure_ascii=False) for v in lesbar[l].values())
        if re.search(KAUSAL[l], text):
            treffer.append(f"{l}: Kausalwendung")
        for e in [*listen.get("alle", []), *listen.get(l, [])]:
            if re.search(e["muster"], text):
                treffer.append(f"{l}: {e['muster'][:40]}")
    pruef(not treffer, "keine Kausalwendung (Protokoll Abschnitt 5) und keine Falschsätze (pruefen/d3_falschsaetze.json)"
          + (f": {treffer[:4]}" if treffer else ""))
    hinweis = all(re.search(r"2020", lesbar[l]["powietrze.bez_przyczyny"]) for l in SPRACHEN) \
        if "powietrze.bez_przyczyny" in lesbar["pl"] else False
    pruef(hinweis, "Hinweis auf andere Einflüsse (Wetter, Pandemiejahr 2020, weitere Maßnahmen) in allen Sprachen")


# ---------------------------------------------------------------- Ablauf
def alles(d: dict, kopf: str, name: str, t: dict, wo: str) -> list[str]:
    befunde.clear()
    daten_pruefen(d, kopf, name)
    texte_pruefen(t, d, wo)
    return list(befunde)


def selbsttest(d: dict, kopf: str, name: str, t: dict, wo: str) -> int:
    def f_summe(x, _t):
        x["zaehlung"]["zeilen_gesamt"] += 1

    def f_grenz(x, _t):
        x["grenzwerte"]["pm10_dni"][0]["dopuszczalna_czestosc"] = 36

    def f_fenster(x, _t):
        s = next(s for s in x["stacje"] if all(p.get("przed") is not None for p in s["przed_po"].values()))
        del s["serie"]["pm10_srednia"]["2017"]
        x["zaehlung"]["werte_verwendet"] -= 1
        x["zaehlung"]["verworfen"]["deckung"] += 1

    def f_niepelne(x, _t):
        e = next(e for s in x["stacje"] for r in s["serie"].values() for e in r.values() if not e.get("niepelne"))
        e["pokrycie"] = 80.0

    def f_umland(x, _t):
        s = next((s for s in x["stacje"] if s["rola"] == "okolica"), None)
        if s is None:      # echte Daten ohne Umland-Station: eine Stadtstation als Umland ausgeben, Zählung nachziehen
            s = x["stacje"][0]
            s["rola"] = "okolica"
            x["zaehlung"]["stationen"]["miasto"] -= 1
            x["zaehlung"]["stationen"]["okolica"] += 1
        s["lat"] += 0.5

    def f_mittel(x, _t):
        p = next(p for s in x["stacje"] for p in s.get("przed_po", {}).values() if p.get("przed") is not None)
        p["przed"] = round(p["przed"] + 0.2, 1)

    def f_kausal(_x, tt):
        tt["en"]["powietrze.bez_przyczyny"] = "Air improved thanks to the ban."

    def f_schluessel(_x, tt):
        del tt["de"]["powietrze.stichtag"]

    def f_fixture(x, _t):     # Beispieldaten mit echter Kennung, echte Daten mit Beispielkennung
        x["stacje"][0]["kod"] = "PL0012A" if x.get("fixture") is True else "FIKCJA-M1"

    def f_vertrag(x, _t):
        x["stacje"][0]["adres"] = "ul. Przykładowa 1"

    faelle = [("Summe der Zählung", f_summe), ("Grenzwert", f_grenz), ("Vorher-Fenster mit Lücke", f_fenster),
              ("Mittel um 0,2 verschoben", f_mittel),
              ("niepelne fehlt", f_niepelne), ("Umland-Abstand", f_umland), ("Kausalwendung en", f_kausal),
              ("Schlüssel fehlt in de", f_schluessel), ("Kennung passt nicht zu fixture", f_fixture),
              ("Feld nicht im Vertrag", f_vertrag)]
    gefangen = []
    for titel, aendern in faelle:
        x, tt = copy.deepcopy(d), copy.deepcopy(t)
        aendern(x, tt)
        aus = sys.stdout
        sys.stdout = open("/dev/null", "w", encoding="utf-8")  # noqa: SIM115
        try:
            b = alles(x, kopf, name, tt, wo)
        finally:
            sys.stdout.close()
            sys.stdout = aus
        gefangen.append(bool(b))
        print(("  ok    " if b else "  FEHLT ") + f"Selbsttest „{titel}“: " + (f"Befund ({b[0][:90]})" if b else "kein Befund"))
    befunde.clear()
    ok = all(gefangen)
    print(f"\n{sum(gefangen)} von {len(faelle)} Verfälschungen erkannt")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    kopf, name, d = datenpruefung.js_lesen(DATEI)
    ordner, wo = texte_ordner()
    t = texte_lesen(ordner)
    if "--selbsttest" in argv:
        rc = alles(d, kopf, name, t, wo)
        if rc:
            print("Selbsttest abgebrochen: die unveränderten Dateien haben schon Befunde")
            return 1
        return selbsttest(d, kopf, name, t, wo)
    alles(d, kopf, name, t, wo)
    if "--ohne-lauf" not in argv:   # ohne Rohdaten (CI): Neurechnung auslassen, wie pruefen/DW_mieszkania.py
        print("Reproduzierbar")
        lauf = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / "32_powietrze.py"), "--pruefen"],
                              capture_output=True, text=True, check=False)
        pruef(lauf.returncode == 0,
              f"skripte/32_powietrze.py --pruefen: {lauf.stdout.strip() or lauf.stderr.strip()[:200]}")
    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
