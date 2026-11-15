"""Prüfung Klima: daten/klimat.js, klimat_zellen.js, klimat_stadtteile_odbl.js ohne Rohdaten und ohne Datenbank.

Prüft die veröffentlichten Dateien gegen die Regeln aus pruefen/dk_protokoll.md:
  1. Vertrag: jede Datei gegen ihr Schema (Validator aus pruefen/daten.py); dazu Gegenproben, dass der Vertrag
     verfälschte Werte wirklich ablehnt (Anteil über 100, fehlende Klasse, unbekannter Grund).
  2. Je Einheit: Anteil = Klassenfläche / Summe der Klassenflächen (Rundung), Anteile ergeben 100 (± 0,5),
     abgeleitete Anteile = Summe ihrer Teile, Abdeckung = Summe der Klassenflächen / Fläche.
  3. Summen: Delegaturen = Stadt, Zellen = Stadt (Fläche und jede Klasse; Toleranz aus Protokoll plus Rundung).
  4. Zellen: Kennungen sortiert und eindeutig, Anteile null genau unter der Mindestfläche, Ringe geschlossen;
     dzielnice: Anteile null genau unter der Mindestfläche, mit echten Grenzen nie (Regel 7, Ergänzung).
  5. Beispieldaten: klimat_stadtteile_odbl.js trägt fixture genau dann, wenn stadtteile_odbl.js oder kennzahlen_odbl.json
     es tragen; Stadt (klimat.js): Grün je Einwohner null mit Grund einwohner_beispieldaten genau dann, wenn die
     Einwohner Beispieldaten sind; dzielnice: einwohner = Kachel aus kennzahlen_odbl.json, auch Beispieldaten (Regel 8,
     Ergänzung), ohne Anteile null mit Grund bezugsflaeche_zu_klein; sonst Grün je Einwohner = (gruen + wald) /
     Einwohner, unter der Mindestzahl null mit Grund unter_mindestzahl.
  6. Keine Datei trägt befund; Stadtteile der Datei = Stadtteile der Ortskonfiguration.

Aufruf: python -I pruefen/dk_klimat.py   Rückgabe 0 = grün, 1 = Befund. Kein Netz, keine Datenbank.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "pruefen"))
sys.path.insert(0, str(WURZEL / "skripte"))
import daten as vertrag  # noqa: E402  (Validator und Leser aus pruefen/daten.py)
import ort_konfig  # noqa: E402

DATEN = WURZEL / "daten"
befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def lesen(name: str):
    return vertrag.js_lesen(DATEN / name)[2]


def schema(name: str) -> dict:
    return json.loads((DATEN / "schema" / name).read_text(encoding="utf-8"))


def fehler(obj, s) -> list:
    f: list = []
    vertrag.validieren(obj, s, s, "$", f, {})
    return f


def einheit_pruefen(ort: str, e: dict, klassen: list, abgeleitet: dict, falsch: list) -> None:
    ha = e["ha"]
    s = sum(ha[k] for k in klassen)
    fl = e.get("flaeche_ha", e.get("flaeche_stadt_ha"))
    if fl and e["abdeckung"] is not None and abs(100 * s / fl - e["abdeckung"]) > 0.05 + 100 * 0.05 * len(klassen) / fl:
        falsch.append(f"{ort}: Abdeckung {e['abdeckung']} ≠ {100 * s / fl:.2f}")
    a = e["anteil"]
    if a is None:
        return
    if s <= 0:
        falsch.append(f"{ort}: Anteile ohne Fläche")
        return
    for k in klassen:
        # Klassenfläche auf 0,05 ha gerundet: Fehler des Quotienten höchstens 0,05·(1 + Anteil) / s · 100
        tol = 0.05 + 100 * 0.05 * len(klassen) / s
        if abs(100 * ha[k] / s - a[k]) > tol:
            falsch.append(f"{ort}: Anteil {k} {a[k]} ≠ {100 * ha[k] / s:.2f}")
    summe = sum(a[k] for k in klassen)
    if abs(summe - 100) > 0.5:
        falsch.append(f"{ort}: Σ Anteile {summe:.1f}")
    for k, teile in abgeleitet.items():
        if abs(a[k] - sum(a[t] for t in teile)) > 0.05 * (len(teile) + 1) + 1e-9:
            falsch.append(f"{ort}: {k} {a[k]} ≠ Σ {teile}")


def main() -> int:
    K = lesen("klimat.js")
    Z = lesen("klimat_zellen.js")
    S = lesen("klimat_stadtteile_odbl.js")
    ST = lesen("stadtteile_odbl.js")
    KZ = json.loads((DATEN / "kennzahlen_odbl.json").read_text(encoding="utf-8"))
    sk, sz, ss = schema("klimat.json"), schema("klimat_zellen.json"), schema("klimat_stadtteile_odbl.json")

    print("1. Verträge")
    for name, obj, s in (("klimat.js", K, sk), ("klimat_zellen.js", Z, sz), ("klimat_stadtteile_odbl.js", S, ss)):
        f = fehler(obj, s)
        pruef(not f, f"{name} erfüllt {s['x-datei'].replace('.js', '.json')}" + (f": {f[:3]}" if f else ""))
    gegen = []
    x = copy.deepcopy(K); x["stadt"]["anteil"]["gruen"] = 100.5; gegen.append(("Anteil über 100", x, sk))
    x = copy.deepcopy(K); del x["stadt"]["ha"]["wald"]; gegen.append(("fehlende Klasse", x, sk))
    x = copy.deepcopy(K); x["stadt"]["gruen_je_ew_grund"] = "unbekannt"; gegen.append(("unbekannter Grund", x, sk))
    x = copy.deepcopy(Z); x["features"][0]["properties"]["id"] = "CRS3035RES100mN1E1"; gegen.append(("Zellkennung 100 m", x, sz))
    x = copy.deepcopy(S); x["stadtteile"]["01"]["strasse"] = "x"; gegen.append(("Feld außerhalb des Vertrags", x, ss))
    for text, obj, s in gegen:
        pruef(bool(fehler(obj, s)), f"Gegenprobe: Vertrag lehnt ab ({text})")

    klassen, abgeleitet = K["klassen"], K["abgeleitet"]
    print("2. Anteile je Einheit")
    falsch: list = []
    einheit_pruefen("stadt", K["stadt"], klassen, abgeleitet, falsch)
    for t, e in K["delegaturen"].items():
        einheit_pruefen(f"delegatur {t}", e, klassen, abgeleitet, falsch)
    for f in Z["features"]:
        einheit_pruefen(f"zelle {f['properties']['id']}", f["properties"], klassen, abgeleitet, falsch)
    for nr, e in S["stadtteile"].items():
        einheit_pruefen(f"dzielnica {nr}", e, klassen, abgeleitet, falsch)
        if (e["anteil"] is None) != (e["flaeche_ha"] < S["mindestflaeche_ha"]) \
                or (e["anteil"] is None) != ("anteil_grund" in e):
            falsch.append(f"dzielnica {nr}: Anteile null nicht genau unter der Mindestfläche")
        if e["anteil"] is None and ST.get("fixture") is not True:   # Regel 7, Ergänzung: echte Grenzen
            falsch.append(f"dzielnica {nr}: echte Grenze mit {e['flaeche_ha']} ha unter der Mindestfläche")
    n = 1 + len(K["delegaturen"]) + len(Z["features"]) + len(S["stadtteile"])
    pruef(not falsch, f"{n} Einheiten: Anteile, Summe 100, abgeleitete Anteile, Abdeckung" + (f": {falsch[:4]}" if falsch else ""))

    print("3. Summen")
    st = K["stadt"]
    d = K["delegaturen"]
    pruef(len(d) == 4, f"vier Delegaturen ({len(d)})")
    rund = 0.05 * len(d)
    dfl = sum(e["flaeche_ha"] for e in d.values())
    pruef(abs(dfl - st["flaeche_ha"]) <= 0.001 * st["flaeche_ha"] + rund,
          f"Σ Fläche Delegaturen = Stadt ({dfl:.1f} / {st['flaeche_ha']} ha)")
    abw = [k for k in klassen if abs(sum(e["ha"][k] for e in d.values()) - st["ha"][k]) > 0.001 * st["ha"][k] + rund]
    pruef(not abw, f"Σ Klassenflächen Delegaturen = Stadt (Abweichungen: {abw})")
    feats = Z["features"]
    rund = 0.05 * len(feats)
    zfl = sum(f["properties"]["flaeche_stadt_ha"] for f in feats)
    pruef(abs(zfl - st["flaeche_ha"]) <= 0.0001 * st["flaeche_ha"] + rund,
          f"Σ Zellteile in der Stadt = Stadtfläche ({zfl:.1f} / {st['flaeche_ha']} ha, {len(feats)} Zellen)")
    abw = [k for k in klassen
           if abs(sum(f["properties"]["ha"][k] for f in feats) - st["ha"][k]) > 0.001 * st["ha"][k] + rund]
    pruef(not abw, f"Σ Klassenflächen Zellen = Stadt (Abweichungen: {abw})")

    print("4. Zellen")
    ids = [f["properties"]["id"] for f in feats]
    pruef(ids == sorted(ids) and len(set(ids)) == len(ids), f"Kennungen sortiert und eindeutig ({len(ids)})")
    m = Z["mindestflaeche_ha"]
    falsch = [f["properties"]["id"] for f in feats
              if (f["properties"]["anteil"] is None) != (f["properties"]["flaeche_stadt_ha"] < m)
              or (f["properties"]["anteil"] is None) != ("anteil_grund" in f["properties"])]
    n_null = sum(1 for f in feats if f["properties"]["anteil"] is None)
    pruef(not falsch, f"Anteile null genau unter {m} ha in der Stadt, mit Grund ({n_null} Zellen; Abweichungen: {falsch[:3]})")
    falsch = [f["properties"]["id"] for f in feats
              if len(f["geometry"]["coordinates"][0]) != 5 or f["geometry"]["coordinates"][0][0] != f["geometry"]["coordinates"][0][-1]]
    pruef(not falsch, f"Ringe der Zellen geschlossen, vier Ecken (Abweichungen: {falsch[:3]})")

    print("5. Beispieldaten und Grün je Einwohner")
    ew_fix = KZ.get("fixture") is True
    st_fix = ST.get("fixture") is True
    pruef((S.get("fixture") is True) == (ew_fix or st_fix),
          f"klimat_stadtteile_odbl.js fixture = {S.get('fixture') is True}, Eingaben: Grenzen {st_fix}, Einwohner {ew_fix}")
    pruef(S["quelle_grenzen"]["fixture"] == st_fix, "quelle_grenzen.fixture = fixture der Grenzen")
    pruef("fixture" not in K and "fixture" not in Z, "klimat.js und klimat_zellen.js ohne fixture (nur BDOT10k)")

    def ew_aus(G):
        return next((x["wert"] for x in G["kacheln"] if x["id"] == "einwohner"), None)
    falsch = []
    paare = [("stadt", K["stadt"], ew_aus(KZ["stadt"]))]
    paare += [(f"dzielnica {nr}", e, ew_aus(KZ["stadtteile"][nr]) if nr in KZ["stadtteile"] else None)
              for nr, e in S["stadtteile"].items()]
    for ort, e, ew in paare:
        stadt = ort == "stadt"
        if not stadt and e.get("einwohner") != ew:
            falsch.append(f"{ort} einwohner")
        if ew_fix and stadt:   # klimat.js bleibt echt: Stadtwert null mit Grund
            if e["gruen_je_ew"] is not None or e.get("gruen_je_ew_grund") != "einwohner_beispieldaten":
                falsch.append(ort)
        elif not stadt and e["anteil"] is None:   # Regel 8, Ergänzung: ohne Anteile kein Grün je Einwohner
            if e["gruen_je_ew"] is not None or e.get("gruen_je_ew_grund") != "bezugsflaeche_zu_klein":
                falsch.append(ort)
        elif ew is None or ew < K["mindest_einwohner"]:
            if e["gruen_je_ew"] is not None or e.get("gruen_je_ew_grund") != "unter_mindestzahl":
                falsch.append(ort)
        else:
            soll = (e["ha"]["gruen"] + e["ha"]["wald"]) * 1e4 / ew
            if e["gruen_je_ew"] is None or abs(e["gruen_je_ew"] - soll) > 0.5 + 0.1 * 1e4 / ew:
                falsch.append(ort)
    pruef(not falsch, f"Grün je Einwohner nach Regel 8 ({len(paare)} Einheiten, Einwohner Beispieldaten: {ew_fix}; "
                      f"Abweichungen: {falsch[:4]})")

    print("6. Befund, Stadtteile")
    pruef(not any("befund" in x for x in (K, Z, S)), "keine Datei trägt befund")
    nrs = {t["nr"] for t in ort_konfig.lade()["gliederung"]["teile"]}
    pruef(set(S["stadtteile"]) == nrs, f"Stadtteile = Ortskonfiguration ({len(nrs)})")

    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
