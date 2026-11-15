"""Erzeugt die Beispieldaten für Kraków: daten/stadtteile_odbl.js, daten/zellen_odbl.js, daten/kennzahlen_odbl.js (+ .json).

Die Werte sind ausdrücklich unecht: fixture: true in jeder Datei, die Seiten zeigen den Hinweis „Beispieldaten“
(kopf.js, #beispieldaten). Die Stadtteile sind Rechtecke in einem 6 × 3-Raster über dem Kartenrahmen aus
config/krakow.yaml, keine echten Grenzen; die Zellen sind ein 1-km-Gitter nach INSPIRE-Muster (EPSG:3035) über
demselben Rahmen. Einwohner und Anteile kommen aus einem festen Zufallsgenerator (Saat 2026), sind also
reproduzierbar und erkennbar ohne Bezug zur Wirklichkeit. Namen, Nummern und Gruppen der 18 dzielnice stammen
aus der Ortskonfiguration. Echte Dateien ersetzen diese, sobald das Paket Gliederung und Bevölkerung liefert.

Aufruf: python -I pruefen/fixtures_krakow.py [--pruefen]   (--pruefen: nichts schreiben, nur vergleichen)
Kein Netz, keine Datenbank.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

from pyproj import Transformer

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402

DATEN = WURZEL / "daten"
STAND = "2026-11-13"
SAAT = 2026
SPALTEN, ZEILEN = 6, 3
HINWEIS = "Beispieldaten mit unechten Werten, nur zum Bauen der Seiten; keine Aussage über Kraków."
ODBL_KOPF = ("/* Beispieldaten (Fixture): Rechtecke statt Stadtteilgrenzen, keine echten Geometrien. Echte Dateien dieser "
             "Art stehen unter der Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/), "
             "© OpenStreetMap-Mitwirkende. ODbL */\n")
Q_BEISPIEL = {"quelle": "Beispielquelle (unecht)", "lizenz": "keine (Beispieldaten)", "vermerk": HINWEIS}


def r5(x: float) -> float:
    return round(x, 5)


def flaeche_km2(ring: list[list[float]]) -> float:
    """Fläche eines Rings (Länge/Breite) in km², sphärisch genähert (Gauß'sche Trapezformel)."""
    R = 6371.0088
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        s += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return abs(s * R * R / 2)


def erzeugen() -> dict[str, str]:
    k = ort_konfig.lade()
    w, s, o, n = k["karte"]["rahmen"]
    teile = k["gliederung"]["teile"]
    if len(teile) != SPALTEN * ZEILEN:
        raise SystemExit(f"{len(teile)} Stadtteile, das Raster hat {SPALTEN * ZEILEN} Felder")
    rnd = random.Random(SAAT)

    # Stadtteile: Rechtecke, Zeile für Zeile von Nordwest nach Südost
    dx, dy = (o - w) / SPALTEN, (n - s) / ZEILEN
    boxen, st_feat = {}, []
    for i, t in enumerate(teile):
        sp, ze = i % SPALTEN, i // SPALTEN
        x0, x1 = w + sp * dx, w + (sp + 1) * dx
        y1, y0 = n - ze * dy, n - (ze + 1) * dy
        ring = [[r5(x0), r5(y0)], [r5(x1), r5(y0)], [r5(x1), r5(y1)], [r5(x0), r5(y1)], [r5(x0), r5(y0)]]
        boxen[t["nr"]] = (x0, y0, x1, y1)
        st_feat.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                        "properties": {"nr": t["nr"], "name": t["name"], "flaeche_km2": round(flaeche_km2(ring), 1),
                                       "bezirk": t["gruppe"], "lx": r5((x0 + x1) / 2), "ly": r5((y0 + y1) / 2)}})
    stadtteile = {"type": "FeatureCollection", "fixture": True, "hinweis": HINWEIS, "features": st_feat}

    # Zellen: 1-km-Gitter in EPSG:3035 über dem Rahmen, Zuordnung nach dem Mittelpunkt
    hin = Transformer.from_crs(4326, 3035, always_xy=True)
    rueck = Transformer.from_crs(3035, 4326, always_xy=True)
    ecken = [hin.transform(x, y) for x, y in ((w, s), (w, n), (o, s), (o, n))]
    e0 = math.floor(min(e for e, _ in ecken) / 1000) * 1000
    e1 = math.ceil(max(e for e, _ in ecken) / 1000) * 1000
    n0 = math.floor(min(nn for _, nn in ecken) / 1000) * 1000
    n1 = math.ceil(max(nn for _, nn in ecken) / 1000) * 1000
    zellen = []
    for nn in range(n0, n1, 1000):
        for ee in range(e0, e1, 1000):
            mx, my = rueck.transform(ee + 500, nn + 500)
            st = next((nr for nr, (x0, y0, x1, y1) in boxen.items() if x0 <= mx < x1 and y0 <= my < y1), None)
            if st is None:
                continue
            ring = [list(map(r5, rueck.transform(a, b))) for a, b in
                    ((ee, nn), (ee + 1000, nn), (ee + 1000, nn + 1000), (ee, nn + 1000), (ee, nn))]
            ew = rnd.choice([None, 0, *range(40, 9000, 37)])
            p = {"id": f"CRS3035RES1000mN{nn}E{ee}", "st": st, "ew": ew}
            if ew:
                p["a_ges"] = ew
                p["q_u15"] = round(rnd.uniform(9, 21), 1)
                p["q_65p"] = round(rnd.uniform(12, 31), 1)
            zellen.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]}, "properties": p})
    zellen.sort(key=lambda f: f["properties"]["id"])
    zfc = {"type": "FeatureCollection", "fixture": True, "hinweis": HINWEIS, "features": zellen}

    # Kennzahlen: Summen aus den Zellen (damit pruefen/daten.py die Summen prüfen kann)
    def kacheln(fs: list[dict]) -> list[dict]:
        ew = sum(f["properties"]["ew"] or 0 for f in fs)
        a = sum(f["properties"].get("a_ges") or 0 for f in fs)
        z65 = round(sum((f["properties"].get("a_ges") or 0) * f["properties"].get("q_65p", 0) / 100 for f in fs))
        return [{"id": "einwohner", "wert": ew, "anzeige": "summe", "quelle": Q_BEISPIEL["quelle"]},
                {"id": "q_65p", "wert": round(100 * z65 / a, 1) if a else 0, "zaehler": z65, "nenner": a,
                 "anzeige": "anteil", "quelle": Q_BEISPIEL["quelle"]}]
    teil_kz = {}
    for f in st_feat:
        nr = f["properties"]["nr"]
        fs = [z for z in zellen if z["properties"]["st"] == nr]
        teil_kz[nr] = {"name": f["properties"]["name"], "zellen": len(fs), "flaeche_km2": f["properties"]["flaeche_km2"],
                       "kacheln": kacheln(fs), "gebaeude": {"anzahl": 0}}
    kz = {"stand_auswertung": STAND, "fixture": True, "hinweis": HINWEIS, "quellen": {"beispiel": Q_BEISPIEL},
          "stadt": {"zellen": len(zellen), "flaeche_km2": round(sum(t["flaeche_km2"] for t in teil_kz.values()), 1),
                    "kacheln": kacheln(zellen), "verteilungen": {}, "gebaeude": {"anzahl": 0}},
          "stadtteile": teil_kz, "kontrolle": {"gebaeude_im_rechteck": 0, "gebaeude_in_stadt": 0}}

    def js(kopf: str, name: str, inhalt: dict) -> str:
        return kopf + f"window.{name}=" + json.dumps(inhalt, ensure_ascii=False, separators=(",", ":")) + ";\n"
    return {
        "stadtteile_odbl.js": js(ODBL_KOPF, "KIEZ_STADTTEILE", stadtteile),
        "zellen_odbl.js": js(ODBL_KOPF, "KIEZ_ZELLEN", zfc),
        "kennzahlen_odbl.js": js(ODBL_KOPF, "KIEZ_KENNZAHLEN", kz),
        "kennzahlen_odbl.json": json.dumps(kz, ensure_ascii=False, indent=1) + "\n",
    }


def main() -> int:
    neu = erzeugen()
    if "--pruefen" in sys.argv:
        alt = [n for n, t in neu.items() if not (DATEN / n).exists() or (DATEN / n).read_text(encoding="utf-8") != t]
        for n in alt:
            print(f"  FEHLT daten/{n} entspricht nicht pruefen/fixtures_krakow.py")
        if not alt:
            print(f"  ok    {len(neu)} Beispieldateien entsprechen pruefen/fixtures_krakow.py")
        return 1 if alt else 0
    for n, t in neu.items():
        (DATEN / n).write_text(t, encoding="utf-8")
        print(f"daten/{n}  {len(t.encode()) // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
