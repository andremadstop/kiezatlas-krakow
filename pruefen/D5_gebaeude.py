"""Prüfung Gebäude und 3D: Leser, Ausgaben und Abnahmekriterien aus pruefen/D5_protokoll.md.

Ohne Netz und ohne Datenbank. Teile:
  A  Shapefile- und DBF-Leser an einer selbst geschriebenen Datei (Loch, mehrteiliges Polygon, gelöschter Satz).
  B  CityGML-Leser (skripte/20_lod.py) an selbst geschriebenen Dateien: measuredHeight, z-Spanne, BuildingPart,
     fehlende Kennung, unplausible Höhe, ZIP.
  C  Ausgaben daten/gebaeude_kennzahlen.js und daten/gebaeude_dzielnice_odbl.js: Summen Delegaturen = Stadt,
     Kontrollfelder, Anteile = Zähler/Nenner, Datenschutzgrenze (V5), Quellenvermerk art. 40c ust. 3,
     fixture genau dann, wenn die Stadtteilgrenzen Beispieldaten sind (V8).
  D  Textvorschlag docs/entscheidungen/D5/texte/<lang>/gebaeude.js: gleiche Schlüssel, Pluralformen, Platzhalter.
  E  Mit Rohdaten ($KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip): neu rechnen, V1 gegen die unabhängige Zählung
     der Machbarkeitsprobe, V2/V3, Gebäude je dzielnica gegen den Vertrag daten/schema/gebaeude.json (Herkunft
     lod1/lod2 als vorgeschlagene Vertragsänderung zugelassen), byte-gleiche Ausgaben (V6). Fehlen die Rohdaten,
     wird E übersprungen und das gesagt.

Aufruf: python -I pruefen/D5_gebaeude.py [--ohne-rohdaten]   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import ast
import gzip
import importlib.util
import io
import json
import re
import struct
import sys
import tempfile
import zipfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
import textschicht  # noqa: E402

befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def modul(name: str, pfad: Path):
    spec = importlib.util.spec_from_file_location(name, pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


BD = modul("bdot", WURZEL / "skripte" / "20_bdot10k.py")
LOD = modul("lod", WURZEL / "skripte" / "20_lod.py")
DP = modul("daten_pruefen", WURZEL / "pruefen" / "daten.py")


# ---------------------------------------------------------------- A
def shp_schreiben(polys: list[list[list[tuple[float, float]]] | None]) -> bytes:
    saetze = b""
    for i, ringe in enumerate(polys, 1):
        if ringe is None:
            inhalt = struct.pack("<i", 0)
        else:
            pkt = [p for r in ringe for p in r]
            teile, a = [], 0
            for r in ringe:
                teile.append(a)
                a += len(r)
            xs, ys = [p[0] for p in pkt], [p[1] for p in pkt]
            inhalt = struct.pack("<i4d2i", 5, min(xs), min(ys), max(xs), max(ys), len(ringe), len(pkt))
            inhalt += struct.pack(f"<{len(teile)}i", *teile) + b"".join(struct.pack("<2d", *p) for p in pkt)
        saetze += struct.pack(">ii", i, len(inhalt) // 2) + inhalt
    kopf = struct.pack(">i5i i", 9994, 0, 0, 0, 0, 0, (100 + len(saetze)) // 2)
    kopf += struct.pack("<ii4d4d", 1000, 5, 0, 0, 1, 1, 0, 0, 0, 0)
    return kopf + saetze


def dbf_schreiben(felder: list[tuple[str, int]], saetze: list[tuple[bool, list[str]]]) -> bytes:
    laenge = 1 + sum(b for _, b in felder)
    kopf_l = 32 + 32 * len(felder) + 1
    b = struct.pack("<B3BIHH20x", 3, 126, 11, 13, len(saetze), kopf_l, laenge)
    for name, breite in felder:
        b += name.encode().ljust(11, b"\0") + b"C" + b"\0" * 4 + bytes([breite]) + b"\0" * 15
    b += b"\x0d"
    for geloescht, werte in saetze:
        b += (b"*" if geloescht else b" ") + b"".join(w.encode("utf-8").ljust(br)[:br] for w, (_, br) in zip(werte, felder))
    return b + b"\x1a"


def teil_a() -> None:
    print("A  Shapefile- und DBF-Leser")
    cw = lambda x0, y0, x1, y1: [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]     # Uhrzeigersinn = außen
    ccw = lambda x0, y0, x1, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]    # gegen = Loch
    g = BD.shp_polygone(shp_schreiben([[cw(0, 0, 10, 10), ccw(2, 2, 4, 4)],
                                       [cw(0, 0, 1, 1), cw(5, 5, 6, 6)], None]))
    pruef(len(g) == 3, f"drei Sätze gelesen ({len(g)})")
    pruef(g[0].geom_type == "Polygon" and len(g[0].interiors) == 1 and abs(g[0].area - 96) < 1e-9,
          f"Polygon mit Loch, Fläche 100 − 4 = 96 ({g[0].area})")
    pruef(g[1].geom_type == "MultiPolygon" and abs(g[1].area - 2) < 1e-9, f"zwei Außenringe = MultiPolygon, Fläche 2 ({g[1].area})")
    pruef(g[2] is None, "Nullgeometrie als None")
    d = BD.dbf_lesen(dbf_schreiben([("A", 5), ("B", 12)], [(False, ["x", "żółć"]), (True, ["y", "z"]), (False, ["", "3"])]),
                     ["A", "B"])
    pruef(d[0] == {"A": "x", "B": "żółć"} and d[1] is None and d[2] == {"A": "", "B": "3"},
          f"DBF: UTF-8, gelöschter Satz als None, Leerwert ({d})")


# ---------------------------------------------------------------- B
GML = """<?xml version="1.0" encoding="UTF-8"?>
<core:CityModel xmlns:core="http://www.opengis.net/citygml/2.0" xmlns:bldg="http://www.opengis.net/citygml/building/2.0"
 xmlns:gen="http://www.opengis.net/citygml/generics/2.0" xmlns:gml="http://www.opengis.net/gml">
 <core:cityObjectMember><bldg:Building gml:id="b1">
  <gen:stringAttribute name="buildingId"><gen:value>ID-1</gen:value></gen:stringAttribute>
  <gen:stringAttribute name="wersjaId"><gen:value>20240101</gen:value></gen:stringAttribute>
  <bldg:measuredHeight uom="m">12.4</bldg:measuredHeight>
  <bldg:consistsOfBuildingPart><bldg:BuildingPart><bldg:measuredHeight uom="m">99</bldg:measuredHeight></bldg:BuildingPart></bldg:consistsOfBuildingPart>
 </bldg:Building></core:cityObjectMember>
 <core:cityObjectMember><bldg:Building gml:id="b2"><bldg:buildingId>ID-2</bldg:buildingId>
  <bldg:lod2Solid><gml:posList srsDimension="3">0 0 210.5 1 0 210.5 1 1 222.0 0 0 210.5</gml:posList></bldg:lod2Solid>
 </bldg:Building></core:cityObjectMember>
 <core:cityObjectMember><bldg:Building gml:id="b3"><bldg:measuredHeight uom="m">7</bldg:measuredHeight></bldg:Building></core:cityObjectMember>
 <core:cityObjectMember><bldg:Building gml:id="b4"><gen:stringAttribute name="buildingId"><gen:value>ID-4</gen:value></gen:stringAttribute>
  <bldg:measuredHeight uom="m">0</bldg:measuredHeight></bldg:Building></core:cityObjectMember>
 <core:cityObjectMember><bldg:Building gml:id="b5"><gen:stringAttribute name="buildingId"><gen:value>ID-1</gen:value></gen:stringAttribute>
  <bldg:measuredHeight uom="m">50</bldg:measuredHeight></bldg:Building></core:cityObjectMember>
</core:CityModel>
"""


def teil_b() -> None:
    print("B  CityGML-Leser (skripte/20_lod.py)")
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "lod1_2024_1261_a.gml").write_text(GML, encoding="utf-8")
        with zipfile.ZipFile(t / "lod2_1261.zip", "w") as z:
            z.writestr("teil/x.gml", GML)
        pfade = LOD.eingangsdateien(t, "lod1")
        pruef([p.name for p in pfade] == ["lod1_2024_1261_a.gml"], f"Dateimuster lod1 ({[p.name for p in pfade]})")
        h, z = LOD.hoehen_lesen(pfade)
        pruef(h.get("ID-1") == (12.4, "20240101"), f"measuredHeight des Gebäudes, nicht des BuildingPart; Version ({h.get('ID-1')})")
        pruef(abs(h.get("ID-2", (0,))[0] - 11.5) < 1e-9, f"ohne measuredHeight: z-Spanne 222,0 − 210,5 = 11,5 ({h.get('ID-2')})")
        pruef(z["gebaeude"] == 5 and z["ohne_kennung"] == 1 and z["unplausibel"] == 1 and z["doppelt"] == 1,
              f"Zählung: 5 Gebäude, 1 ohne Kennung, 1 unplausibel (0 m), 1 doppelt, erste Fundstelle gilt ({z})")
        h2, z2 = LOD.hoehen_lesen(LOD.eingangsdateien(t, "lod2"))
        pruef(h2 == h and z2["dateien"][0]["datei"] == "lod2_1261.zip:teil/x.gml", "ZIP wird gelesen wie GML")


# ---------------------------------------------------------------- C
ZAEHL = ["anzahl", "funktion_unbekannt", "wohngebaeude", "grundflaeche_m2", "grundflaeche_wohn_m2", "flaeche_m2"]
UNTER = ["zustand", "funktion", "wohn_art", "geschosse", "geschosse_wohn"]
VERBOTEN = {"lokalnyid", "nazwa", "info_dodat", "uwagi", "idbudynku", "buildingid", "gml_id", "id", "oid"}


def summe_gleich(teile: list[dict], ganz: dict, ort: str) -> None:
    # Flächen sind je Einheit auf ganze m² gerundet: Abweichung bis zur Zahl der Teile ist Rundung, keine Lücke
    abw = [k for k in ZAEHL if abs(sum(t[k] for t in teile) - ganz[k]) > (len(teile) if k.endswith("_m2") else 0)]
    abw += [f"{u}.{k}" for u in UNTER for k in ganz[u] if sum(t[u][k] for t in teile) != ganz[u][k]]
    pruef(not abw, f"{ort}: Σ Teile = Ganzes für {len(ZAEHL)} Zahlen (Flächen ± Rundung auf m²) und {sum(len(ganz[u]) for u in UNTER)} Unterzahlen"
          + (f" (Abweichung: {abw[:5]})" if abw else ""))


def block_pruefen(B: dict, ort: str) -> list[str]:
    f = []
    if sum(B["zustand"].values()) != B["anzahl"]:
        f.append("zustand ≠ anzahl")
    if sum(B["funktion"].values()) + B["funktion_unbekannt"] != B["anzahl"]:
        f.append("funktion ≠ anzahl")
    if B["funktion"]["110"] != B["wohngebaeude"] or sum(B["wohn_art"].values()) != B["wohngebaeude"]:
        f.append("Wohngebäude")
    if sum(B["geschosse"].values()) != B["anzahl"] or sum(B["geschosse_wohn"].values()) != B["wohngebaeude"]:
        f.append("Geschossklassen")
    bd = B["bebauungsdichte"]
    if bd["nenner"] and bd["wert"] != round(100 * bd["zaehler"] / bd["nenner"], 1):
        f.append("bebauungsdichte")
    n_bek = B["anzahl"] - B["geschosse"]["unbekannt"]
    if (B["geschosse_median"] is None) != (n_bek < BD.MINDESTFALLZAHL):
        f.append("Mindestfallzahl Median")
    return [f"{ort}: {x}" for x in f]


def js(p: Path):
    return BD.js_lesen(p)


def teil_c() -> None:
    print("C  Ausgaben")
    nk, K = js(WURZEL / "daten" / "gebaeude_kennzahlen.js")
    nd, D = js(WURZEL / "daten" / "gebaeude_dzielnice_odbl.js")
    _, ST = js(WURZEL / "daten" / "stadtteile_odbl.js")
    S = K["stadt"]
    summe_gleich(list(K["delegatury"].values()), S, "Delegaturen → Stadt")
    kt = K["kontrolle"]
    pruef(kt["in_stadt"] == S["anzahl"] and kt["datensaetze"] == kt["in_stadt"] + kt["ausserhalb_stadt"]
          and kt["in_stadt_ohne_delegatur"] == 0,
          f"Kontrolle: Datensätze {kt['datensaetze']} = in der Stadt {kt['in_stadt']} + außerhalb {kt['ausserhalb_stadt']}; keine Lücke zwischen den Delegaturen")
    f = block_pruefen(S, "Stadt")
    for k, B in K["delegatury"].items():
        f += block_pruefen(B, k)
    for k, B in D["stadtteile"].items():
        f += block_pruefen(B, k)
    pruef(not f, f"innere Stimmigkeit je Einheit ({1 + len(K['delegatury']) + len(D['stadtteile'])} Einheiten)" + (f": {f[:4]}" if f else ""))
    pruef(sum(B["anzahl"] for B in D["stadtteile"].values()) == D["kontrolle"]["in_dzielnica"] <= S["anzahl"],
          f"Σ dzielnice = kontrolle.in_dzielnica ({D['kontrolle']['in_dzielnica']}) ≤ Stadt ({S['anzahl']})")
    pruef(D["kontrolle"]["in_stadt"] == S["anzahl"], "dzielnice und Kennzahlen aus demselben Lauf (in_stadt gleich)")
    pruef((D.get("fixture") is True) == (ST.get("fixture") is True),
          f"V8: fixture je dzielnica = fixture der Stadtteilgrenzen ({D.get('fixture')} / {ST.get('fixture')})")
    for name, inhalt in (("gebaeude_kennzahlen.js", K), ("gebaeude_dzielnice_odbl.js", D)):
        k = {x.lower() for x in DP.schluessel(inhalt, set())}
        pruef(not (k & VERBOTEN), f"V5: {name} ohne Gebäudekennung, Namen, Zusatzinformation ({sorted(k & VERBOTEN)})")
        pruef("art. 40c ust. 3" in inhalt["quellen"]["bdot10k"]["vermerk"], f"{name}: Quellenvermerk nach art. 40c ust. 3")
        pruef(inhalt["stand_daten"] == K["stand_daten"], f"{name}: Stand {inhalt['stand_daten']}")
    pruef(K["stadt"]["geschosse_median"] is not None, "Stadt: Median der Geschosse vorhanden (n ≥ Mindestfallzahl)")


# ---------------------------------------------------------------- D
def teil_d() -> None:
    print("D  Textvorschlag gebaeude.*")
    basis = WURZEL / "docs" / "entscheidungen" / "D5" / "texte"
    T = {l: textschicht.datei_lesen(basis / l / "gebaeude.js") for l in ("pl", "en", "de")}
    pruef(all(set(T[l]) == set(T["pl"]) for l in T), f"gleiche Schlüssel in pl, en, de ({len(T['pl'])})")
    pruef(all(s.startswith("gebaeude.") and textschicht.SCHLUESSEL.match(s) for s in T["pl"]), "nur Namensraum gebaeude.*, Schlüsselform")
    falsch = []
    for s, v in T["pl"].items():
        for l in T:
            w = T[l][s]
            if isinstance(w, dict):
                if set(w) != set(textschicht.PLURALFORMEN[l]) or not all("{n}" in x for x in w.values()):
                    falsch.append(f"{l}:{s}")
            platz = lambda x: set(re.findall(r"\{(\w+)\}", json.dumps(x, ensure_ascii=False)))
            if platz(w) != platz(v):
                falsch.append(f"{l}:{s} Platzhalter")
    pruef(not falsch, f"Pluralformen und Platzhalter ({falsch[:4]})")
    kst = {f"gebaeude.kst.{k}" for k in BD.KST}
    pruef(kst <= set(T["pl"]), "Beschriftung für alle zehn Klassen KŚT")
    deutsch = re.compile(r"\b(und|nicht|oder|Gebäude|Geschoss\w*|Höhe|Fläche)\b")
    reste = [f"{l}:{s}" for l in ("pl", "en") for s, v in T[l].items() if deutsch.search(json.dumps(v, ensure_ascii=False))]
    pruef(not reste, f"keine deutschen Wörter in pl und en ({reste[:4]})")


# ---------------------------------------------------------------- E
def machbarkeit_zaehlung(p: Path) -> dict:
    aus = {}
    for z in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(FOBUD|KAT_ISTNIE|ZRO_DANYCH|LICZ_KONDY) (\[.*\])$", z)
        if m:
            aus[m.group(1)] = dict(ast.literal_eval(m.group(2)))
        m = re.match(r"^Datensätze: (\d+)$", z)
        if m:
            aus["n"] = int(m.group(1))
    return aus


def teil_e() -> None:
    print("E  Mit Rohdaten")
    bdot = BD.daten_ordner() / "2026-11-13" / "03_gebaeude" / "1261_SHP.zip"
    if not bdot.exists() or "--ohne-rohdaten" in sys.argv:
        print(f"  übersprungen: {bdot} fehlt oder --ohne-rohdaten")
        return
    K, D, Z, kach = BD.rechnen(bdot, True)
    mb = machbarkeit_zaehlung(BD.daten_ordner() / "2026-11-13" / "_auswertung" / "bdot10k_bubd_1261.txt")
    pruef(mb.get("n") == Z["datensaetze"], f"V1: Datensätze = Machbarkeitsprobe ({Z['datensaetze']} / {mb.get('n')})")
    for k in ("FOBUD", "KAT_ISTNIE", "ZRO_DANYCH"):
        pruef(mb.get(k) == Z["roh"][k], f"V1: Verteilung {k} = Machbarkeitsprobe ({len(mb.get(k, {}))} Werte)")
    lk = {a: b for a, b in mb.get("LICZ_KONDY", {}).items()}
    pruef(bool(lk) and all(Z["roh"]["LICZ_KONDY"].get(a) == b for a, b in lk.items()),
          f"V1: die {len(lk)} häufigsten Werte LICZ_KONDY = Machbarkeitsprobe")
    pruef(Z["in_delegatur"] + Z["ausserhalb_stadt"] == Z["datensaetze"] and Z["mehrfach_delegatur"] == 0,
          f"V2: jedes Gebäude genau einer Delegatur oder außerhalb ({Z['in_delegatur']} + {Z['ausserhalb_stadt']})")
    pruef(0.9999 <= Z["deckung"] <= 1.0001 and Z["ueberlappung_max_m2"] < 1,
          f"V3: Delegaturen decken die Gemeinde ({Z['deckung']}), Überlappung {Z['ueberlappung_max_m2']} m²")
    print(f"  info  V4: ohne Geometrie {Z['ohne_geometrie']}, ungültig repariert {Z['ungueltig_repariert']}, ohne Fläche {Z['flaeche_null']} (gezählt, im Lauf-Beleg)")
    schema = json.loads((WURZEL / "daten" / "schema" / "gebaeude.json").read_text(encoding="utf-8"))
    hq = schema["properties"]["features"]["items"]["properties"]["properties"]["properties"]["hq"]
    hq["enum"] = sorted(set(hq["enum"]) | {"lod1", "lod2"})           # Vorschlag Vertragsänderung
    fehler, n, roh_b, gz_b = [], 0, 0, 0
    for nr, inhalt in kach.items():
        DP.validieren(inhalt, schema, schema, f"gebaeude/{nr}", fehler, {})
        n += len(inhalt["features"])
        t = BD.js_text(f"KIEZ_GEB_{nr}", "x", inhalt).encode()
        roh_b += len(t)
        gz_b += len(gzip.compress(t, 9, mtime=0))
        k = {x.lower() for x in DP.schluessel(inhalt, set())}
        if k & VERBOTEN:
            fehler.append(f"{nr}: {sorted(k & VERBOTEN)}")
    pruef(not fehler, f"Gebäude je dzielnica gegen daten/schema/gebaeude.json (+ lod1/lod2), ohne Kennung ({len(kach)} Dateien)"
          + (f": {fehler[:3]}" if fehler else ""))
    pruef(n == Z["in_dzielnica"], f"Gebäude in den Dateien = in einer dzielnica ({n})")
    print(f"  info  Umfang der Gebäudedateien: {roh_b} Bytes, gzip {gz_b} Bytes")
    ausgaben = {WURZEL / "daten" / "gebaeude_kennzahlen.js": BD.js_text("KIEZ_GEB_KENNZAHLEN", BD.KOPF_K, K),
                WURZEL / "daten" / "gebaeude_dzielnice_odbl.js": BD.js_text("KIEZ_GEB_DZIELNICE", BD.KOPF_D, D),
                WURZEL / "belege" / "D5_gebaeude_lauf.md": BD.lauf_md(Z, K)}
    abw = [p.name for p, t in ausgaben.items() if p.read_text(encoding="utf-8") != t]
    pruef(not abw, f"V6: neu gerechnet byte-gleich mit den eingecheckten Ausgaben ({abw})")


def main() -> int:
    for t in (teil_a, teil_b, teil_c, teil_d, teil_e):
        try:
            t()
        except Exception as e:  # noqa: BLE001 – jede Ausnahme ist ein Befund, die übrigen Teile laufen weiter
            pruef(False, f"{t.__name__}: {type(e).__name__}: {e}"[:300])
    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
