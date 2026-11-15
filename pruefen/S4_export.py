"""Prüfung der Downloads (daten/pobierz/) gegen die Regeln in pruefen/S4_protokoll.md.

Liest die Downloads und, unabhängig vom Exportskript, die Datendateien unter daten/. Prüft:
  1. Vollständig: beide GeoPackages, QGIS-Projekt, licencje.csv, Liesmich pl/en/de, je Ebene vier CSV.
  2. GeoPackage gültig: application_id, user_version, integrity_check, gpkg_contents = gpkg_geometry_columns,
     SRS = rechen_srid in Kopf und Tabellen, WKB-Typ wie erklärt, Hülle im Kopf = Hülle der Koordinaten, alle
     Objekte im Raum Kraków.
  3. Inhalt gleich Quelle, je Ebene mit eigener Zuordnung (Zeilen, Kennungen, Werte, Lage der Punkte, Flächen der
     dzielnice, Summen Zelle → dzielnica → Stadt und delegatura → Stadt); dazu für jede Ebene: jede Zahl kommt in
     ihren Quelldateien vor (keine ausgedachte Zahl).
  4. CSV gleich GeoPackage (Zeilen, Spalten, Werte, Lage); *_pl mit Dezimalkomma ohne Tausendertrenner, sonst gleich.
  5. Trennung der Lizenzen: in der Datei ohne ODbL kein Feld st, kein Fußweg, kein OSM-Objekt, kein Text mit
     OpenStreetMap oder ODbL; in der ODbL-Datei trägt jede Ebene die ODbL und einen OSM-Vermerk.
  6. Vermerke wörtlich: jeder Vermerk in licencje steht so in den Datendateien (Werte oder Kopfkommentar).
  7. Kein Personenbezug: keine Spalte für Adresse, Telefon, E-Mail, Personennamen; kein Wert mit Hausnummer,
     Postleitzahl, Telefonnummer oder E-Mail.
  8. Keine Beispieldaten: keine Ebene aus einer Datei mit fixture: true; das Liesmich nennt genau diese Dateien.
  9. QGIS-Projekt: ein wohlgeformtes .qgs, jede Ebene zeigt relativ auf eine vorhandene Datei und Tabelle, Stile
     wohlgeformt, keine Orange- oder Gelbtöne.
 10. Liesmich: jede Ebene mit der Zeilenzahl aus dem GeoPackage, Hinweis auf das Dezimalkomma, Meldeweg.
 11. Bedeutung der Felder (Nachtrag 14.11.2026): jede Spalte jeder Ebene, der CSV (x, y, wkt) und der Tabelle
     licencje hat in der Tabelle pola ihres GeoPackages genau eine Erklärung auf pl, en und de; jeder Wert der
     Kategorienfelder (Liste in skripte/export_pola_krakow.py) steht in wartosci; pola.csv und wartosci.csv gleich
     den Tabellen; jede Ebene hat im Liesmich einen Abschnitt mit ihren Feldern.
 13. Quellen vollständig (Nachtrag 14.11.2026): jede Quelle einer Ebene (Schlüssel unter quellen der Herkunftsdateien,
     Feld quelle, Spalten aus Eurostat-Gitter, BDOT10k oder NSP) hat eine Zeile in licencje.
 12. Sprache (Nachtrag 14.11.2026): Erklärungen pl und en, CZYTAJ.md, README.md und die Spalten zrodlo,
     licencja_* der Tabelle licencje ohne deutsche Wörter (Feldnamen, Werte in Backticks und wörtliche Vermerke
     ausgenommen).

Aufruf: python -I pruefen/S4_export.py [--ziel daten/pobierz]    Rückgabe 0 = 0 Befunde.
Kein Netz, keine Datenbank.
"""
from __future__ import annotations

import argparse
import colorsys
import csv
import io
import json
import math
import re
import sqlite3
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
import ort_konfig  # noqa: E402
import export_pola_krakow as pola  # noqa: E402

DATEN = WURZEL / "daten"
SRID = ort_konfig.RECHEN_SRID
FREI, ODBL = "kiezatlas_krakow.gpkg", "kiezatlas_krakow_odbl.gpkg"
befunde: list[str] = []
zaehl = {"ok": 0}


def pruef(ok: bool, text: str) -> bool:
    if ok:
        zaehl["ok"] += 1
    else:
        befunde.append(text)
        print("  FEHLT " + text)
    return ok


def ok_zeile(text: str) -> None:
    print("  ok    " + text)


# ------------------------------------------------------------------------------------------- Quellen
def lade(name: str) -> tuple[str, dict]:
    t = (DATEN / f"{name}.js").read_text(encoding="utf-8")
    m = re.search(r"window\.[A-Za-z0-9_]+\s*=\s*", t)
    return t[: m.start()], json.loads(t[m.end():].rstrip().rstrip(";"))


Q: dict[str, dict] = {}
KOPF: dict[str, str] = {}
for _p in sorted(DATEN.glob("*.js")):
    KOPF[_p.stem], Q[_p.stem] = lade(_p.stem)
BEISPIEL = sorted(n for n, v in Q.items() if isinstance(v, dict) and v.get("fixture") is True)


def zahlen(o, aus: set, ohne_geo: bool = True) -> set:
    if isinstance(o, dict):
        for k, v in o.items():
            if ohne_geo and k in ("geometry", "coordinates"):
                continue
            zahlen(v, aus, ohne_geo)
    elif isinstance(o, list):
        for v in o:
            zahlen(v, aus, ohne_geo)
    elif isinstance(o, bool):
        aus.add(float(o))   # Wahrheitswerte stehen im GeoPackage als 0/1
    elif isinstance(o, (int, float)):
        aus.add(round(float(o), 9))
    elif isinstance(o, str) and re.fullmatch(r"-?\d+(\.\d+)?", o):
        aus.add(round(float(o), 9))
    return aus


def texte(o, aus: list) -> list:
    if isinstance(o, dict):
        for v in o.values():
            texte(v, aus)
    elif isinstance(o, list):
        for v in o:
            texte(v, aus)
    elif isinstance(o, str):
        aus.append(o)
    return aus


ALLE_TEXTE = "\n".join(texte(Q, []) + list(KOPF.values()))
ZUSAMMEN = re.compile(r"^(.+) \((https?://[^)\s]+)\)$")


def woertlich(s: str) -> bool:
    """Wörtlich aus den Datendateien: ganzer Text, oder „Name (Adresse)“ mit Name als Teil eines Datentexts und der
    Adresse als eigenem Wert (Quellenzeile für Eurostat und OpenStreetMap, Nachtrag im Protokoll)."""
    if s in ALLE_TEXTE:
        return True
    m = ZUSAMMEN.match(s)
    return bool(m) and m.group(1) in ALLE_TEXTE and f'"{m.group(2)}"' in ALLE_JSON


ALLE_JSON = "\n".join(json.dumps(v, ensure_ascii=False) for v in Q.values())
BEILAGEN = ("pola", "wartosci")
DEUTSCH = re.compile(r"[äöüßÄÖÜ]|\b(und|oder|der|die|das|des|dem|den|mit|ohne|nicht|nur|je|aus|für|über|nach|bei|"
                     r"Einwohner|Gebäude|Fläche|Zelle|Anteil|Grenze|Grenzen|Gitter|Mitwirkende|Datei|Polen|erzeugt|Quelle|Lizenz|Stadt)\b")


# ------------------------------------------------------------------------------------------- Geometrie
def wkb_lesen(blob: bytes):
    import shapely
    pruef(blob[:2] == b"GP", "GeoPackage-Kopf GP")
    flags = blob[3]
    srs = struct.unpack("<i", blob[4:8])[0]
    env = (flags >> 1) & 0x07
    n = {0: 0, 1: 4, 2: 6, 3: 6, 4: 8}[env]
    h = struct.unpack(f"<{n}d", blob[8:8 + 8 * n]) if n else None
    wkb = blob[8 + 8 * n:]
    return srs, h, wkb, shapely.from_wkb(wkb)


def gpkg_tabellen(c) -> dict:
    return {r[0]: r[1] for r in c.execute("SELECT table_name, data_type FROM gpkg_contents")}


def tabelle_lesen(c, name: str) -> tuple[list[str], list[dict], list]:
    cur = c.execute(f'SELECT * FROM "{name}" ORDER BY fid')
    spalten = [d[0] for d in cur.description]
    zeilen, geos = [], []
    for r in cur.fetchall():
        d = dict(zip(spalten, r))
        if "geom" in d:
            geos.append(d.pop("geom"))
        d.pop("fid")
        zeilen.append(d)
    return [s for s in spalten if s not in ("fid", "geom")], zeilen, geos


def gleich(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return (None if a is None else int(a)) == (None if b is None else int(b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(float(a), float(b), rel_tol=0, abs_tol=1e-9)
    return a == b


# ------------------------------------------------------------------------------------------- Prüfungen
def pruefe_gpkg(pfad: Path, raum) -> dict[str, tuple]:
    import shapely
    c = sqlite3.connect(pfad)
    pruef(c.execute("PRAGMA application_id").fetchone()[0] == 1196444487, f"{pfad.name}: application_id GPKG")
    pruef(c.execute("PRAGMA user_version").fetchone()[0] == 10400, f"{pfad.name}: user_version 10400")
    pruef(c.execute("PRAGMA integrity_check").fetchone()[0] == "ok", f"{pfad.name}: integrity_check")
    srs = {r[0] for r in c.execute("SELECT srs_id FROM gpkg_spatial_ref_sys")}
    pruef({SRID, 4326} <= srs, f"{pfad.name}: SRS {SRID} und 4326 eingetragen")
    inhalt = gpkg_tabellen(c)
    geomcols = {r[0]: (r[2], r[3]) for r in c.execute("SELECT * FROM gpkg_geometry_columns")}
    pruef(set(geomcols) == {t for t, a in inhalt.items() if a == "features"},
          f"{pfad.name}: gpkg_geometry_columns = Feature-Tabellen in gpkg_contents")
    pruef("licencje" in inhalt, f"{pfad.name}: Tabelle licencje")
    aus = {}
    typnr = {"POINT": 1, "POLYGON": 3, "MULTIPOLYGON": 6}
    for t in sorted(inhalt):
        if t == "layer_styles":
            continue
        spalten, zeilen, geos = tabelle_lesen(c, t)
        geom = None
        if t in geomcols:
            gtyp, gsrs = geomcols[t]
            pruef(gsrs == SRID, f"{t}: SRS {SRID} in gpkg_geometry_columns")
            geom = []
            schlecht = 0
            for b in geos:
                s, h, wkb, g = wkb_lesen(b)
                wt = struct.unpack("<I", wkb[1:5])[0]
                x1, y1, x2, y2 = g.bounds
                if s != SRID or wt != typnr[gtyp] or not raum.contains(g):
                    schlecht += 1
                if h is not None and max(abs(h[0] - x1), abs(h[1] - x2), abs(h[2] - y1), abs(h[3] - y2)) > 1e-6:
                    schlecht += 1
                geom.append(g)
            pruef(schlecht == 0, f"{t}: {len(geom)} Geometrien mit SRS {SRID}, Typ {gtyp}, Hülle stimmt, im Raum Kraków"
                  + (f" ({schlecht} Abweichungen)" if schlecht else ""))
            cmin = c.execute("SELECT min_x, min_y, max_x, max_y FROM gpkg_contents WHERE table_name=?", (t,)).fetchone()
            u = shapely.GeometryCollection(geom).bounds
            pruef(cmin[0] <= u[0] + 1e-6 and cmin[1] <= u[1] + 1e-6 and cmin[2] >= u[2] - 1e-6 and cmin[3] >= u[3] - 1e-6,
                  f"{t}: Hülle in gpkg_contents umfasst alle Objekte")
        aus[t] = (spalten, zeilen, geom)
    c.close()
    return aus


def nach(zeilen: list[dict], schl: str) -> dict:
    return {z[schl]: z for z in zeilen}


def vergleiche(name: str, paare: list[tuple], text: str) -> None:
    falsch = [(a, b, w) for a, b, w in paare if not gleich(a, b)]
    pruef(not falsch, f"{name}: {text} ({len(paare)} Werte)" + (f", Abweichung z. B. {falsch[:2]}" if falsch else ""))


def inhalt(F: dict, O: dict, tr) -> None:
    import shapely
    from shapely.geometry import shape
    alle = {**F, **O}
    # Zellen
    zo = Q["zellen_odbl"]["features"]
    er, ef = Q["erreichbar"], Q["erreichbar_fuss_odbl"]
    for tab, extra, werte_q, st in (("siatka_1km", "luftlinie_m_", er, False), ("siatka_1km_odbl", "fussweg_m_", ef, True)):
        sp, ze, ge = alle[tab]
        pruef(len(ze) == len(zo), f"{tab}: {len(ze)} Zeilen = {len(zo)} Zellen in zellen_odbl.js")
        paare = []
        z_nach = nach(ze, "id")
        for i, f in enumerate(zo):
            p = f["properties"]
            z = z_nach.get(p["id"], {})
            for k in ("ew", "a_ges", "q_u15", "q_65p") + (("st",) if st else ()):
                paare.append((z.get(k), p.get(k), (p["id"], k)))
            for a in werte_q["arten"]:
                paare.append((z.get(extra + a), werte_q["werte"][a][i], (p["id"], a)))
        vergleiche(tab, paare, "Werte gleich zellen_odbl.js und " + ("erreichbar_fuss_odbl.js" if st else "erreichbar.js"))
        pruef(("st" in sp) == st, f"{tab}: Feld st {'vorhanden' if st else 'fehlt (keine OSM-Zuordnung)'}")
        mitte = [shapely.transform(shape(f["geometry"]).centroid, tr) for f in zo]
        drin = sum(g.contains(m) for g, m in zip(ge, mitte))
        pruef(drin == len(zo), f"{tab}: Zellgeometrie aus der Kennung enthält den Mittelpunkt der Zelle aus zellen_odbl.js ({drin}/{len(zo)})")
        flaechen = {round(g.area / 1e4) for g in ge}
        pruef(all(abs(a - 100) <= 1 for a in flaechen), f"{tab}: jede Zelle rund 100 ha ({sorted(flaechen)[:3]} …)")
        summe = sum(z["ew"] for z in ze)
        pruef(summe == Q["kennzahlen_odbl"]["kontrolle"]["einwohner_mittelpunkt_stadt"],
              f"{tab}: Summe Einwohner {summe} = kennzahlen_odbl.json (Stadt)")
    # dzielnice
    sp, ze, ge = O["dzielnice"]
    st = {f["properties"]["nr"]: f for f in Q["stadtteile_odbl"]["features"]}
    sd, gd, ks = (Q["steckbrief_dzielnice_odbl"]["stadtteile"], Q["gebaeude_dzielnice_odbl"]["stadtteile"],
                  Q["klimat_stadtteile_odbl"]["stadtteile"])
    pruef(sorted(z["nr"] for z in ze) == sorted(st), f"dzielnice: {len(ze)} Zeilen, Nummern wie stadtteile_odbl.js")
    paare = []
    for z in ze:
        nr = z["nr"]
        paare += [(z["nazwa"], st[nr]["properties"]["name"], (nr, "name")),
                  (z["gitter_einwohner"], sd[nr]["gitter"]["einwohner"], (nr, "einwohner")),
                  (z["gitter_q_65p"], sd[nr]["gitter"]["q_65p"], (nr, "q_65p")),
                  (z["dichte_gitter"], sd[nr]["dichte_gitter"], (nr, "dichte")),
                  (z["geb_anzahl"], gd[nr]["anzahl"], (nr, "geb")),
                  (z["geb_wohn_art_mehr"], gd[nr]["wohn_art"]["mehr"], (nr, "mfh")),
                  (z["klimat_anteil_bebauung_verkehr"], ks[nr]["anteil"]["bebauung_verkehr"], (nr, "bv")),
                  (z["klimat_gruen_je_ew"], ks[nr].get("gruen_je_ew"), (nr, "gje"))]
    vergleiche("dzielnice", paare, "Werte gleich steckbrief_dzielnice, gebaeude_dzielnice, klimat_stadtteile")
    abw = [(z["nr"], round(g.area / 1e6, 2), z["flaeche_km2"]) for z, g in zip(ze, ge)
           if abs(g.area / 1e6 - z["flaeche_km2"]) > 0.01 * z["flaeche_km2"] + 0.02]
    pruef(not abw, "dzielnice: Fläche der Geometrie im Rechensystem = flaeche_km2 (±1 %)" + (f": {abw[:3]}" if abw else ""))
    s_ew = sum(z["gitter_einwohner"] for z in ze)
    pruef(s_ew == Q["kennzahlen_odbl"]["kontrolle"]["einwohner_mittelpunkt_stadt"],
          f"Summe dzielnice {s_ew} = Summe der Zellen (Stadt)")
    s_geb = sum(z["geb_anzahl"] for z in ze)
    pruef(s_geb == Q["gebaeude_kennzahlen"]["stadt"]["anzahl"], f"Summe Gebäude der dzielnice {s_geb} = Stadt")
    # miasto, delegatury
    m = F["miasto"][1][0]
    sb = Q["steckbrief"]
    vergleiche("miasto", [(m["nsp_einwohner"], sb["stadt"]["nsp"]["einwohner"], "nsp"),
                          (m["gitter_einwohner"], sb["stadt"]["gitter"]["einwohner"], "gitter"),
                          (m["flaeche_km2"], sb["stadt"]["flaeche_km2"], "flaeche"),
                          (m["geb_anzahl"], Q["gebaeude_kennzahlen"]["stadt"]["anzahl"], "geb"),
                          (m["klimat_anteil_gruen_wald"], Q["klimat"]["stadt"]["anteil"]["gruen_wald"], "gw"),
                          (m["typ_blok"], Q["sanierung"]["typologie"]["stadt"]["blok"], "blok")], "Werte gleich Stadtwerten")
    de = F["delegatury"][1]
    pruef(len(de) == len(sb["gruppen"]) == 4, f"delegatury: {len(de)} Zeilen")
    pruef(sum(z["nsp_einwohner"] for z in de) == sb["stadt"]["nsp"]["einwohner"], "Summe NSP der delegatury = Stadt")
    vergleiche("delegatury", [(z["geb_anzahl"], Q["gebaeude_kennzahlen"]["delegatury"][z["teryt"]]["anzahl"], z["teryt"])
                              for z in de], "Gebäude gleich gebaeude_kennzahlen.js")
    # Punkte
    for tab, datei, weg in (("placowki_bdot", "einrichtungen", ("features",)), ("przystanki", "haltestellen", ("features",)),
                            ("bdot_kamienica_nazwa", "denkmale_bdot", ("namensbezug", "features")),
                            ("rejestr_zabytkow", "denkmale", ("objekte", "features")),
                            ("placowki_osm", "einrichtungen_odbl", ("features",)),
                            ("osm_heritage_start_date", "denkmale_odbl", ("objekte", "features")),
                            ("zbk_budynki", "sanierung_odbl", ("punkte", "features"))):
        sp, ze, ge = alle[tab]
        feats = Q[datei]
        for k in weg:
            feats = feats[k]
        pruef(len(ze) == len(feats), f"{tab}: {len(ze)} Punkte = {datei}.js")
        weit = sum(g.distance(shapely.transform(shape(f["geometry"]), tr)) > 0.01 for g, f in zip(ge, feats))
        pruef(weit == 0, f"{tab}: Lage gleich {datei}.js (umgerechnet, ≤ 0,01 m)")
        paare = [(z.get(k), v, k) for z, f in zip(ze, feats) for k, v in f["properties"].items()
                 if not isinstance(v, (dict, list)) and k in sp]
        vergleiche(tab, paare, f"Merkmale gleich {datei}.js")
    sp, ze, ge = F["bdot_kompleksy"]
    pruef(len(ze) == len(Q["denkmale_bdot"]["komplexe"]["features"]), f"bdot_kompleksy: {len(ze)} Flächen")
    # Versorgung
    sp, ze, _ = O["dostepnosc"]
    erwartet = {}
    for datei in ("planer_odbl", "planer_fuss_odbl"):
        P = Q[datei]
        for nr, r in [*P["raeume"].items(), (None, P["gesamt"])]:
            for w in r["werte"]:
                k = (nr, w["kennzahl"], w["art"], w["methode"], (w.get("richtwert") or {}).get("wert"))
                erwartet[k] = (w.get("wert"), w.get("zaehler"), w.get("nenner"))
    ist = {(z["st"], z["kennzahl"], z["art"], z["methode"], z["richtwert_wert"]): (z["wert"], z["zaehler"], z["nenner"])
           for z in ze}
    pruef(len(ze) == len(erwartet) == len(ist), f"dostepnosc: {len(ze)} Zeilen = Werte in planer_odbl.js und planer_fuss_odbl.js")
    vergleiche("dostepnosc", [(ist.get(k, (None,) * 3)[i], v[i], k) for k, v in erwartet.items() for i in range(3)],
               "Wert, Zähler, Nenner gleich")
    # ZBK
    sp, ze, _ = F["zbk_wykaz_dzielnice"]
    li = Q["sanierung"]["liste"]
    pruef(sum(z["n"] for z in ze) == sum(v["n"] for v in li["je_dzielnica"].values()), "zbk_wykaz_dzielnice: Summe n wie sanierung.js")
    sp, ze, _ = O["zbk_typologia_dzielnice"]
    td = Q["sanierung_odbl"]["typologie_dzielnice"]["je_dzielnica"]
    vergleiche("zbk_typologia_dzielnice", [(z[k], td[z["st"]][k], (z["st"], k)) for z in ze for k in ("mfh", "blok", "osiedle")],
               "gleich sanierung_odbl.js")
    pruef(all(z["szacunek"] == 1 for z in ze), "zbk_typologia_dzielnice: als Schätzung gekennzeichnet")


HERKUNFT = {
    "miasto": ["steckbrief", "gebaeude_kennzahlen", "klimat", "sanierung"],
    "delegatury": ["steckbrief", "gebaeude_kennzahlen", "klimat", "sanierung", "denkmale_bdot"],
    "siatka_1km": ["zellen_odbl", "erreichbar"], "siatka_1km_pokrycie": ["klimat_zellen"],
    "placowki_bdot": ["einrichtungen"], "przystanki": ["haltestellen"], "bdot_kompleksy": ["denkmale_bdot"],
    "bdot_kamienica_nazwa": ["denkmale_bdot"], "rejestr_zabytkow": ["denkmale"], "zbk_wykaz_dzielnice": ["sanierung"],
    "dzielnice": ["stadtteile_odbl", "steckbrief_dzielnice_odbl", "gebaeude_dzielnice_odbl", "klimat_stadtteile_odbl"],
    "siatka_1km_odbl": ["zellen_odbl", "erreichbar_fuss_odbl"], "dostepnosc": ["planer_odbl", "planer_fuss_odbl"],
    "placowki_osm": ["einrichtungen_odbl"], "osm_heritage_start_date": ["denkmale_odbl"],
    "zbk_budynki": ["sanierung_odbl"], "zbk_typologia_dzielnice": ["sanierung_odbl"],
}


# Jede Quelle einer Ebene braucht eine Zeile in licencje (Nachtrag 14.11.2026). Quellen ergeben sich aus den Schlüsseln
# unter quellen der Herkunftsdateien, aus deren Feld quelle und aus den Spalten (Werte aus dem Eurostat-Gitter oder aus
# Gebäudemerkmalen der BDOT10k stehen auch in Dateien, die die Quelle nicht unter quellen führen).
QUELLE_MUSTER = {
    "GUGiK": re.compile(r"GUGiK|Główny Urząd Geodezji"), "ZTP": re.compile(r"\bZTP\b"),
    "OpenStreetMap": re.compile(r"OpenStreetMap"), "Eurostat": re.compile(r"Eurostat"),
    "GUS": re.compile(r"Główny Urząd Statystyczny"), "Prawo oświatowe": re.compile(r"Prawo oświatowe"),
    "ZBK": re.compile(r"Zarząd Budynków Komunalnych"), "Wikidata": re.compile(r"Wikidata"),
}
SCHLUESSEL_QUELLE = {"bdot10k": "GUGiK", "bdot": "GUGiK", "delegatury": "GUGiK", "hoehen": "GUGiK", "lod2": "GUGiK",
                     "ztp": "ZTP", "osm": "OpenStreetMap", "eurostat2021": "Eurostat", "nsp2021": "GUS",
                     "prawo_oswiatowe": "Prawo oświatowe", "zbk": "ZBK",
                     "wd": "Wikidata"}


# Ebenen, die aus einer Herkunftsdatei nur einen Teil übernehmen, der die Quelle nicht nutzt (mit Grund)
QUELLE_AUSNAHMEN = {
    ("miasto", "ZBK"): "aus sanierung.js nur die Typologie (BDOT10k), nicht die ZBK-Liste",
    ("delegatury", "ZBK"): "aus sanierung.js nur die Typologie (BDOT10k), nicht die ZBK-Liste",
    ("zbk_typologia_dzielnice", "ZBK"): "aus sanierung_odbl.js nur die Typologie je dzielnica (BDOT10k, OSM-Grenzen)",
    ("zbk_wykaz_dzielnice", "GUGiK"): "nur Zählungen der ZBK-Liste je dzielnica laut Liste, ohne Gebäudeverknüpfung",
    ("siatka_1km", "OpenStreetMap"): "aus zellen_odbl.js nur Eurostat-Werte ohne st (Lesart in docs/entscheidungen/S4.md, S4-6)",
    ("dzielnice", "GUS"): "Felder nsp und nsp_grund ohne NSP-Wert (leer mit Grund)",
}


def noetige_quellen(t: str, spalten: list[str]) -> set[str]:
    n = set()
    for d in HERKUNFT.get(t, []):
        q = Q[d]
        for k, w in (q.get("quellen") or {}).items():
            if isinstance(w, dict) and w.get("vorhanden") is False:   # Register ohne Eingang (denkmale.js: nid, gez)
                continue
            if k not in SCHLUESSEL_QUELLE:
                n.add(f"unbekannter Schlüssel {d}.quellen.{k}")
            else:
                n.add(SCHLUESSEL_QUELLE[k])
        txt = json.dumps(q.get("quelle") or "", ensure_ascii=False) + KOPF[d]
        if "BDOT10k" in txt:
            n.add("GUGiK")
        if d.endswith("_odbl"):
            n.add("OpenStreetMap")
    for s in spalten:
        if s in ("ew", "a_ges", "q_u15", "q_65p", "dichte_gitter", "klimat_einwohner", "klimat_gruen_je_ew") or s.startswith("gitter_"):
            n.add("Eurostat")
        if s in ("w", "mfh", "del", "gs", "fn", "flaeche_quelle") or s.startswith(("geb_", "bdot_", "typ_", "klimat_ha_")):
            n.add("GUGiK")
        if s.startswith("nsp_"):
            n.add("GUS")
    return n


def quellen_vollstaendig(F: dict, O: dict) -> None:
    for gp, n in ((F, FREI), (O, ODBL)):
        lic = defaultdict(str)
        for z in gp["licencje"][1]:
            lic[z["warstwa"]] += " " + (z["zrodlo"] or "") + " " + (z["nota"] or "")
        for t, (sp, _, _) in sorted(gp.items()):
            if t == "licencje":
                continue
            noetig = {q for q in noetige_quellen(t, sp) if (t, q) not in QUELLE_AUSNAHMEN}
            fehlt = sorted(q for q in noetig if q not in QUELLE_MUSTER or not QUELLE_MUSTER[q].search(lic[t]))
            pruef(not fehlt, f"{n}/{t}: jede Quelle mit Zeile in licencje ({', '.join(sorted(noetig))})"
                  + (f"; fehlt: {fehlt}" if fehlt else ""))


def keine_ausgedachte_zahl(alle: dict) -> None:
    for t, (sp, ze, _) in sorted(alle.items()):
        if t == "licencje":
            continue
        if t not in HERKUNFT:
            pruef(False, f"{t}: Ebene ohne bekannte Herkunft in dieser Prüfung")
            continue
        erlaubt: set = set()
        for d in HERKUNFT[t]:
            pruef(d not in BEISPIEL, f"{t}: Quelle {d}.js ist keine Beispieldatei")
            zahlen(Q[d], erlaubt)
        fremd = sorted({(k, v) for z in ze for k, v in z.items()
                        if isinstance(v, (int, float)) and not isinstance(v, bool) and round(float(v), 9) not in erlaubt
})
        pruef(not fremd, f"{t}: jede Zahl kommt in {', '.join(HERKUNFT[t])} vor" + (f"; fremd: {fremd[:4]}" if fremd else ""))


def pruefe_csv(ziel: Path, F: dict, O: dict) -> None:
    import shapely
    for gp, ordner in ((F, "csv"), (O, "csv_odbl")):
        for t, (sp, ze, ge) in sorted(gp.items()):
            if t == "licencje":
                continue
            roh = {}
            for o in (ordner, ordner + "_pl"):
                p = ziel / o / f"{t}.csv"
                if not pruef(p.exists(), f"{o}/{t}.csv vorhanden"):
                    continue
                b = p.read_bytes()
                pruef(b.startswith(b"\xef\xbb\xbf"), f"{o}/{t}.csv: UTF-8 mit BOM")
                roh[o] = list(csv.reader(io.StringIO(b.decode("utf-8-sig")), delimiter=";"))
            if len(roh) < 2:
                continue
            a, b = roh[ordner], roh[ordner + "_pl"]
            geo_sp = ["x", "y"] if ge and ge[0].geom_type == "Point" else (["wkt"] if ge else [])
            if not pruef(a[0] == sp + geo_sp == b[0], f"{ordner}/{t}.csv: Spalten wie GeoPackage, auch in _pl"):
                continue
            if not pruef(len(a) - 1 == len(ze) == len(b) - 1, f"{ordner}/{t}.csv: {len(ze)} Zeilen wie GeoPackage, auch in _pl"):
                continue
            falsch, komma_falsch = [], []
            for i, z in enumerate(ze):
                for j, k in enumerate(sp):
                    v = z[k]
                    s, s_pl = a[i + 1][j], b[i + 1][j]
                    if v is None:
                        ok = s == "" and s_pl == ""
                    elif isinstance(v, float):
                        ok = gleich(float(s), v) and gleich(float(s_pl.replace(",", ".")), v)
                        if not re.fullmatch(r"-?\d+(,\d+)?", s_pl) or "." in s_pl:
                            komma_falsch.append((t, k, s_pl))
                    elif isinstance(v, int):
                        ok = s == str(v) == s_pl
                    else:
                        ok = s == str(v) == s_pl
                    if not ok:
                        falsch.append((t, i, k, v, s, s_pl))
                if ge:
                    g = ge[i]
                    if g.geom_type == "Point":
                        for jj, kk in enumerate(("x", "y")):
                            w = float(a[i + 1][len(sp) + jj])
                            w_pl = float(b[i + 1][len(sp) + jj].replace(",", "."))
                            c0 = g.x if kk == "x" else g.y
                            if abs(w - c0) > 0.006 or abs(w_pl - c0) > 0.006:
                                falsch.append((t, i, kk))
                    else:
                        gw = shapely.from_wkt(a[i + 1][-1])
                        if not gw.equals_exact(g, 0.006) or a[i + 1][-1] != b[i + 1][-1]:
                            falsch.append((t, i, "wkt"))
            pruef(not falsch, f"{ordner}/{t}.csv = GeoPackage (Werte, Lage)" + (f": {falsch[:2]}" if falsch else ""))
            pruef(not komma_falsch, f"{ordner}_pl/{t}.csv: Dezimalkomma ohne Tausendertrenner" + (f": {komma_falsch[:2]}" if komma_falsch else ""))


OSM_TEXT = re.compile(r"OpenStreetMap|ODbL|\bosm\b", re.I)
ADRESS_SPALTE = re.compile(r"adres|ulica|street|strasse|haus|nr_domu|kod_poczt|telefon|phone|e_?mail|www|osoba|nazwisko|vorname|nachname", re.I)
ADRESS_WERT = [re.compile(r"\b\d{2}-\d{3}\b"), re.compile(r"\bul\.\s*\S+(\s+\S+)?\s+\d+\w?\b"), re.compile(r"@"),
               re.compile(r"\+48|\b\d{3}[ -]\d{3}[ -]\d{3}\b")]


def lizenz_und_schutz(F: dict, O: dict) -> None:
    for t, (sp, ze, _) in sorted(F.items()):
        if t == "licencje":
            continue
        pruef("st" not in sp and not any(s.startswith("fussweg") for s in sp), f"{FREI}/{t}: kein st, kein Fußweg")
        treffer = [v for z in ze for v in z.values() if isinstance(v, str) and OSM_TEXT.search(v)]
        pruef(not treffer, f"{FREI}/{t}: kein Text mit OpenStreetMap/ODbL/osm" + (f": {treffer[:2]}" if treffer else ""))
    for z in F["licencje"][1]:
        pruef(not OSM_TEXT.search(z["nota"] + z["zrodlo"] + z["licencja_pliku"] + z["licencja_zrodla"]), f"{FREI}/licencje: {z['warstwa']} ohne OSM-Vermerk")
    lo = defaultdict(list)
    for z in O["licencje"][1]:
        lo[z["warstwa"]].append(z)
    for t in sorted(O):
        if t == "licencje":
            continue
        zs = lo.get(t, [])
        pruef(bool(zs) and all(z["licencja_pliku"] == "ODbL 1.0" for z in zs) and any("OpenStreetMap" in z["nota"] for z in zs),
              f"{ODBL}/{t}: Lizenz ODbL 1.0 mit OSM-Vermerk in licencje")
    lf = defaultdict(list)
    for z in F["licencje"][1]:
        lf[z["warstwa"]].append(z)
    pruef(all(lf.get(t) for t in F if t != "licencje"), f"{FREI}: jede Ebene hat Zeilen in licencje")
    for gp, n in ((F, FREI), (O, ODBL)):
        fehlt = [(z[k] or "")[:60] for z in gp["licencje"][1] for k in ("zrodlo", "nota") if not woertlich(z[k] or "")]
        pruef(not fehlt, f"{n}/licencje: jeder Vermerk steht wörtlich in den Datendateien" + (f": {fehlt[:2]}" if fehlt else ""))
    for gp, n in ((F, FREI), (O, ODBL)):
        for t, (sp, ze, _) in sorted(gp.items()):
            if t == "licencje":
                continue
            s = [x for x in sp if ADRESS_SPALTE.search(x)]
            pruef(not s, f"{n}/{t}: keine Spalte für Adresse, Kontakt oder Person" + (f": {s}" if s else ""))
            w = [v for z in ze for v in z.values() if isinstance(v, str) and not v.startswith("[")
                 and any(r.search(v) for r in ADRESS_WERT)]
            pruef(not w, f"{n}/{t}: kein Wert mit Hausnummer, PLZ, Telefon oder E-Mail" + (f": {w[:2]}" if w else ""))


ORANGE = (20 / 360, 65 / 360)


def pruefe_qgis(ziel: Path, F: dict, O: dict) -> None:
    p = ziel / "kiezatlas_krakow.qgz"
    with zipfile.ZipFile(p) as z:
        namen = z.namelist()
        pruef(namen == ["kiezatlas_krakow.qgs"], f"{p.name}: genau eine .qgs ({namen})")
        x = ET.fromstring(z.read(namen[0]))
    lay = x.findall(".//maplayer")
    gp = {FREI: F, ODBL: O}
    falsch = []
    for m in lay:
        ds = m.findtext("datasource")
        mm = re.fullmatch(r"\./(kiezatlas_krakow(?:_odbl)?\.gpkg)\|layername=(\w+)", ds or "")
        if not mm or mm.group(2) not in gp[mm.group(1)] or not (ziel / mm.group(1)).exists():
            falsch.append(ds)
    geo_tabs = sorted(t for g in gp.values() for t, v in g.items() if v[2])
    pruef(not falsch and len(lay) == len(geo_tabs), f"{p.name}: {len(lay)} Ebenen, relativ auf vorhandene Tabellen" + (f": {falsch}" if falsch else ""))
    farben = re.findall(r'name="(?:color|outline_color)" value="(\d+),(\d+),(\d+),(\d+)"', ET.tostring(x, encoding="unicode"))
    bunt = []
    for r, g, b, a in farben:
        h, l, s = colorsys.rgb_to_hls(int(r) / 255, int(g) / 255, int(b) / 255)
        if int(a) > 0 and s > 0.35 and ORANGE[0] <= h <= ORANGE[1]:
            bunt.append((r, g, b))
    pruef(not bunt, f"{p.name}: keine Orange- oder Gelbtöne in {len(farben)} Farben" + (f": {bunt[:3]}" if bunt else ""))
    for n in (FREI, ODBL):
        c = sqlite3.connect(ziel / n)
        st = c.execute("SELECT f_table_name, styleQML FROM layer_styles").fetchall()
        c.close()
        kaputt = []
        for t, qml in st:
            try:
                ET.fromstring(re.sub(r"^<!DOCTYPE[^>]*>\s*", "", qml))
            except ET.ParseError:
                kaputt.append(t)
        pruef(not kaputt and {t for t, _ in st} == {t for t, v in gp[n].items() if v[2]},
              f"{n}: Stil je Feature-Ebene, wohlgeformt" + (f": {kaputt}" if kaputt else ""))


def pruefe_liesmich(ziel: Path, F: dict, O: dict) -> None:
    meldeweg = ort_konfig.lade()["meldeweg"]
    for datei, komma in (("CZYTAJ.md", "przecinkiem dziesiętnym"), ("README.md", "decimal comma"), ("LIESMICH.md", "Dezimalkomma")):
        p = ziel / datei
        if not pruef(p.exists(), f"{datei} vorhanden"):
            continue
        t = p.read_text(encoding="utf-8")
        falsch = []
        for gp in (F, O):
            for tab, (_, ze, _) in gp.items():
                if tab == "licencje":
                    continue
                m = re.search(rf"^\| `{tab}`:.*\| (\d+) \|", t, re.M)
                if not m or int(m.group(1)) != len(ze):
                    falsch.append(tab)
        pruef(not falsch, f"{datei}: jede Ebene mit der Zeilenzahl aus dem GeoPackage" + (f": {falsch}" if falsch else ""))
        pruef(komma in t and meldeweg in t, f"{datei}: Hinweis Dezimalkomma und Meldeweg")
        genannt = sorted(re.findall(r"`daten/(\w+)\.js`", t))
        pruef(genannt == BEISPIEL, f"{datei}: nennt genau die Beispieldateien {BEISPIEL}")
        # Themen ohne eigene Ebene (Liste „- Thema: `name.js`“): echte Atlas-Dateien, aus keiner Ebene gelesen
        ohne = sorted(re.findall(r"^- [^`\n]+: `(\w+)\.js`$", t, re.M))
        quellen = {d for h in HERKUNFT.values() for d in h}
        falsch = [n for n in ohne if n not in Q or n in BEISPIEL or n in quellen]
        pruef(not falsch, f"{datei}: Themen ohne Ebene ({', '.join(ohne) or 'keine'}) sind echte Dateien ohne Ebene"
              + (f"; falsch: {falsch}" if falsch else ""))


def pruefe_pola(ziel: Path, F: dict, O: dict, BF: dict, BO: dict) -> None:
    alle_p, alle_w = [], []
    for gp, B, n in ((F, BF, FREI), (O, BO, ODBL)):
        if not pruef(all(B.get(b) for b in BEILAGEN), f"{n}: Tabellen pola und wartosci"):
            continue
        sp, pz, _ = B["pola"]
        spw, wz, _ = B["wartosci"]
        pruef(sp == ["warstwa", "pole", "opis_pl", "opis_en", "opis_de"] and
              spw == ["warstwa", "pole", "wartosc", "opis_pl", "opis_en", "opis_de"], f"{n}: Spalten von pola und wartosci")
        da = defaultdict(list)
        for z in pz:
            da[(z["warstwa"], z["pole"])].append(z)
        fehlt, leer, doppelt = [], [], []
        for t, (spalten, ze, geom) in sorted(gp.items()):
            extra = []
            if geom is not None:
                extra = ["x", "y"] if geom and geom[0].geom_type == "Point" else ["wkt"]
            for s in spalten + extra:
                zs = da.get((t, s), [])
                if not zs:
                    fehlt.append(f"{t}.{s}")
                elif len(zs) > 1:
                    doppelt.append(f"{t}.{s}")
                elif not all((zs[0][f"opis_{l}"] or "").strip() for l in ("pl", "en", "de")):
                    leer.append(f"{t}.{s}")
        pruef(not fehlt, f"{n}: jede Spalte jeder Ebene hat eine Erklärung in pola" + (f": {fehlt[:5]}" if fehlt else ""))
        pruef(not doppelt and not leer, f"{n}: genau eine, nicht leere Erklärung je Spalte auf pl, en, de"
              + (f": {(doppelt + leer)[:5]}" if doppelt or leer else ""))
        dw = {(z["warstwa"], z["pole"], z["wartosc"]) for z in wz if all((z[f"opis_{l}"] or "").strip() for l in ("pl", "en", "de"))}
        ohne = []
        for t, (spalten, ze, _) in sorted(gp.items()):
            for s in spalten:
                if s not in pola.KATEGORIEN:
                    continue
                for v in sorted({z[s] for z in ze if z[s] is not None}, key=str):
                    if (t, s, str(v)) not in dw:
                        ohne.append(f"{t}.{s}={v}")
        pruef(not ohne, f"{n}: jeder Wert der Kategorienfelder hat eine Erklärung in wartosci" + (f": {ohne[:5]}" if ohne else ""))
        alle_p += [[z[c] for c in sp] for z in pz]
        alle_w += [[z[c] for c in spw] for z in wz]
    for datei, alle in (("pola.csv", alle_p), ("wartosci.csv", alle_w)):
        p = ziel / datei
        if not pruef(p.is_file(), f"{datei} vorhanden"):
            continue
        rows = list(csv.reader(io.StringIO(p.read_text(encoding="utf-8-sig")), delimiter=";"))[1:]
        # licencje steht in beiden GeoPackages, in der CSV einmal
        pruef(sorted(map(tuple, rows)) == sorted(set(map(tuple, alle))), f"{datei} = Tabellen beider GeoPackages ({len(rows)} Zeilen)")
    for datei in ("CZYTAJ.md", "README.md", "LIESMICH.md"):
        t = (ziel / datei).read_text(encoding="utf-8")
        ohne = [e for e in list(F) + list(O) if f"### `{e}`" not in t]
        pruef(not ohne, f"{datei}: Abschnitt mit den Feldern je Ebene" + (f": {ohne}" if ohne else ""))


def _deutsch(text: str, namen: set) -> list[str]:
    t = re.sub(r"`[^`]*`", " ", text)
    t = " ".join(w for w in re.split(r"(\s+)", t) if w.strip("(),;:.") not in namen)
    return sorted({m.group(0) for m in DEUTSCH.finditer(t)})


def pruefe_sprache(ziel: Path, F: dict, O: dict) -> None:
    namen = {s for gp in (F, O) for sp, _, _ in gp.values() for s in sp} | {"zaehler", "nenner", "anteil_*", "richtwert_wert"}
    namen |= {str(v) for gp in (F, O) for sp, ze, _ in gp.values() for s in sp if s in pola.KATEGORIEN
              for v in {z[s] for z in ze if z[s] is not None}}
    for n in ("pola.csv", "wartosci.csv"):
        rows = list(csv.DictReader(io.StringIO((ziel / n).read_text(encoding="utf-8-sig")), delimiter=";"))
        treffer = sorted({w for r in rows for l in ("pl", "en") for w in _deutsch(r[f"opis_{l}"], namen)})
        pruef(not treffer, f"{n}: Erklärungen pl und en ohne deutsche Wörter" + (f": {treffer[:8]}" if treffer else ""))
    for n in (FREI, ODBL):
        c = sqlite3.connect(ziel / n)
        treffer = sorted({w for tab in BEILAGEN for r in c.execute(f'SELECT opis_pl, opis_en FROM "{tab}"')
                          for x in r for w in _deutsch(x or "", namen)})
        c.close()
        pruef(not treffer, f"{n}: pola und wartosci, pl und en ohne deutsche Wörter" + (f": {treffer[:8]}" if treffer else ""))
    verbatim = [z["nota"] for gp in (F, O) for z in gp["licencje"][1]]
    for datei in ("CZYTAJ.md", "README.md"):
        t = (ziel / datei).read_text(encoding="utf-8")
        for v in verbatim + ["UG (haftungsbeschränkt)"]:   # wörtliche Vermerke und die Rechtsform im Firmennamen
            t = t.replace(v, " ")
        treffer = _deutsch(t, namen)
        pruef(not treffer, f"{datei}: ohne deutsche Wörter außerhalb von Backticks" + (f": {treffer[:8]}" if treffer else ""))
    treffer = sorted({w for gp in (F, O) for z in gp["licencje"][1] for k in ("zrodlo", "licencja_pliku", "licencja_zrodla", "nota")
                      for w in _deutsch(z[k] or "", namen)})
    pruef(not treffer, "licencje: zrodlo, licencja_*, nota ohne deutsche Wörter" + (f": {treffer[:8]}" if treffer else ""))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ziel", type=Path, default=DATEN / "pobierz")
    a = ap.parse_args()
    ziel = a.ziel
    import shapely
    from pyproj import Transformer
    from shapely.geometry import box
    t = Transformer.from_crs(4326, SRID, always_xy=True)

    def tr(xy):
        import numpy as np
        x, y = t.transform(xy[:, 0], xy[:, 1])
        return np.column_stack([x, y])

    # Raum Kraków: Hülle der Stadtteile aus der Datei, 5 km Rand
    gs = [__import__("shapely.geometry", fromlist=["shape"]).shape(f["geometry"]) for f in Q["stadtteile_odbl"]["features"]]
    raum = shapely.transform(box(*shapely.GeometryCollection(gs).bounds), tr).buffer(5000)
    print(f"Downloads {ziel}")
    for n in (FREI, ODBL, "kiezatlas_krakow.qgz", "licencje.csv", "pola.csv", "wartosci.csv", "kiezatlas_krakow_csv.zip",
              "CZYTAJ.md", "README.md", "LIESMICH.md"):
        pruef((ziel / n).is_file(), f"{n} vorhanden")
    if befunde:
        print(f"{zaehl['ok']} ok, {len(befunde)} Befunde")
        return 1
    F, O = pruefe_gpkg(ziel / FREI, raum), pruefe_gpkg(ziel / ODBL, raum)
    BF = {b: F.pop(b, None) for b in BEILAGEN}
    BO = {b: O.pop(b, None) for b in BEILAGEN}
    pruef(not (set(F) & set(O)) - {"licencje"}, "jede Ebene in genau einer Datei")
    inhalt(F, O, tr)
    keine_ausgedachte_zahl({**{k: v for k, v in F.items()}, **{k: v for k, v in O.items()}})
    pruefe_csv(ziel, F, O)
    lizenz_und_schutz(F, O)
    quellen_vollstaendig(F, O)
    pruefe_qgis(ziel, F, O)
    pruefe_liesmich(ziel, F, O)
    pruefe_pola(ziel, F, O, BF, BO)
    pruefe_sprache(ziel, F, O)
    with zipfile.ZipFile(ziel / "kiezatlas_krakow_csv.zip") as z:
        drin = {n: z.read(n) for n in z.namelist()}
    lose = {str(p.relative_to(ziel)): p.read_bytes() for p in sorted(ziel.rglob("*")) if p.suffix in (".csv", ".md")}
    pruef(drin == lose, f"kiezatlas_krakow_csv.zip = alle CSV und Liesmich ({len(drin)} Dateien, byte-gleich)")
    lc = list(csv.reader(io.StringIO((ziel / "licencje.csv").read_text(encoding="utf-8-sig")), delimiter=";"))
    pruef(len(lc) - 1 == len(F["licencje"][1]) + len(O["licencje"][1]), "licencje.csv = Tabellen licencje beider GeoPackages")
    gp_lic = sorted(tuple("" if z[k] is None else str(z[k]) for k in lc[0]) for gp in (F, O) for z in gp["licencje"][1])
    pruef(sorted(map(tuple, lc[1:])) == gp_lic, "licencje.csv: Inhalt gleich den Tabellen licencje (Nachtrag 14.11.2026)")
    print(f"{zaehl['ok']} ok, {len(befunde)} Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
