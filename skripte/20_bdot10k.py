"""Gebäude aus BDOT10k (Powiat 1261 = Kraków): Kennzahlen je Stadt, Delegatur und dzielnica, Gebäude für 3D.

Ersetzt für Kraków den ALKIS-Leser (20_alkis_nas.py bleibt für die Gegenprobe Potsdam). Regeln und Abnahme stehen
vorab in pruefen/D5_protokoll.md; Begriffe nach dem Rozporządzenie BDOT10k (Dz.U. 2021 poz. 1412, Tabelle 25/26).

Liest (kein Netz, keine Datenbank):
  $KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip   OT_BUBD_A (Gebäude), OT_ADJA_A (Gemeinde, Delegaturen; aus PRG)
  daten/stadtteile_odbl.js                          dzielnice (Paket Gliederung; solange Beispieldaten, ist auch
                                                    das Ergebnis je dzielnica Beispieldaten)
  $KIEZ_DATEN/eingang/lod1_2024_1261*, lod2_1261*    Höhen (skripte/20_lod.py), wenn vorhanden

Schreibt:
  daten/gebaeude_kennzahlen.js        window.KIEZ_GEB_KENNZAHLEN: Stadt und Delegaturen (nur BDOT10k/PRG)
  daten/gebaeude_dzielnice_odbl.js    window.KIEZ_GEB_DZIELNICE: je dzielnica (Grenzen aus OpenStreetMap, ODbL)
  belege/D5_gebaeude_lauf.md          Zählungen je Schritt (Beleg, erzeugt)
  mit --geometrie DIR: DIR/<nr>_odbl.js  window.KIEZ_GEB_<nr> im Vertrag daten/schema/gebaeude_odbl.json (f, gs, h,
                                      hq); Zuordnung über die OSM-Grenzen, daher ODbL. Mit Beispielgrenzen DIR/<nr>.js;
                                      dazu DIR/MANIFEST.sha256 (Format sha256sum; --pruefen vergleicht im Ordner vom
                                      13.11.2026 stattdessen SHA256SUMS, KR42)

Aufruf (Projektumgebung, siehe docs/rundgang.md):
  python -I skripte/20_bdot10k.py [--bdot ZIP] [--geometrie DIR]
  python -I skripte/20_bdot10k.py --pruefen      neu rechnen und byte-gleich mit den Dateien vergleichen
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import statistics
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from pyproj import CRS, Transformer
from shapely.geometry import MultiPolygon, Polygon, shape

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402

DATEN = WURZEL / "daten"
SCHICHT = "PL.PZGiK.283.BDOT10k.1261__OT_{}"
GESCHOSS_HOEHE_M = 3          # Konvention aus Potsdam (Herkunft „geschosse“), keine Messung
ERSATZ_HOEHE_M = 3
MINDESTFALLZAHL = 30          # Median und Mittel der Geschosse nur ab so vielen Gebäuden mit bekannter Zahl
KST = [str(k) for k in range(101, 111)]
ZUSTAENDE = ["eksploatowany", "w budowie", "nieczynny", "zniszczony", ""]
ZUSTAND_SCHLUESSEL = {"eksploatowany": "eksploatowany", "w budowie": "w_budowie", "nieczynny": "nieczynny",
                      "zniszczony": "zniszczony", "": "leer"}
GESCHOSS_KLASSEN = ["1", "2", "3_4", "5_10", "11p", "unbekannt"]
EIN, MEHR = "budynek jednorodzinny", "budynek wielorodzinny"
DUPLIKAT = re.compile(r"^Duplikaty wyst", re.I)
FELDER_BUBD = ["LOKALNYID", "WERSJA", "ZRO_DANYCH", "KAT_ISTNIE", "UWAGI", "KODKST", "FOBUD", "PFBUD", "LICZ_KONDY"]
FELDER_ADJA = ["RODZAJ", "NAZWA", "IDTERYTJED"]
VERMERK = ("Źródło: Baza Danych Obiektów Topograficznych (BDOT10k), państwowy zasób geodezyjny i kartograficzny, "
           "Główny Urząd Geodezji i Kartografii; dane opracowane (art. 40c ust. 3 ustawy Prawo geodezyjne i "
           "kartograficzne, Dz.U. 2026 poz. 1389)")
VERMERK_PRG = ("Granice delegatur: państwowy rejestr granic (PRG) w BDOT10k, Główny Urząd Geodezji i Kartografii")
# Wörtliche Freigabe des Herausgebers (Geoportal, Seite „Modele 3D budynków“, abgerufen 13.11.2026); nach der
# Entscheidung vom 13.11.2026 genügt sie als Grundlage für die Veröffentlichung der LoD-Höhen.
FREIGABE_LOD = ("„Modele 3D budynków są dostępne bezpłatnie i możliwe do dowolnego wykorzystania.” "
                "(https://www.geoportal.gov.pl/pl/dane/inne-dane/modele-3d-budynkow/)")


def vermerk_lod(Z: dict) -> str:
    """Vermerk nur für die tatsächlich gelesenen Modelle, mit Stand und wörtlicher Freigabe."""
    teile = [t for t, a in (("LoD1, stan 2024", "lod1"), ("LoD2, stan 2017", "lod2")) if Z.get(f"{a}_dateien")]
    return ("Wysokości: Modele 3D budynków (" + "; ".join(teile) + "), Główny Urząd Geodezji i Kartografii. "
            + FREIGABE_LOD)


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN", WURZEL.parent / "kiezatlas-daten" / "krakow")).resolve()


# ---------------------------------------------------------------- Shapefile und DBF (Standardbibliothek + shapely)
def dbf_lesen(b: bytes, felder: list[str]) -> list[dict | None]:
    """Datensätze als dict der gewünschten Felder; gelöschte Datensätze als None (Position bleibt für die .shp)."""
    n, kopf, laenge = struct.unpack("<xxxxIHH", b[:12])
    lage, o, pos = {}, 32, 1
    while b[o] != 0x0D:
        name = b[o:o + 11].split(b"\0")[0].decode("ascii")
        breite = b[o + 16]
        lage[name] = (pos, breite)
        pos += breite
        o += 32
    fehlt = [f for f in felder if f not in lage]
    if fehlt:
        raise SystemExit(f"DBF ohne Felder {fehlt}")
    aus: list[dict | None] = []
    for i in range(n):
        r = b[kopf + i * laenge: kopf + (i + 1) * laenge]
        if r[:1] == b"*":
            aus.append(None)
            continue
        aus.append({f: r[lage[f][0]:lage[f][0] + lage[f][1]].decode("utf-8").strip() for f in felder})
    return aus


def shp_polygone(b: bytes) -> list:
    """Polygone (Typ 5, 15, 25) als shapely-Geometrie; Außenringe im Uhrzeigersinn, Löcher gegen ihn (ESRI)."""
    typ = struct.unpack("<i", b[32:36])[0]
    if typ not in (5, 15, 25):
        raise SystemExit(f"Shapefile-Typ {typ}, erwartet Polygon")
    aus, o = [], 100
    while o < len(b):
        _, laenge = struct.unpack(">ii", b[o:o + 8])
        inhalt = b[o + 8:o + 8 + 2 * laenge]
        o += 8 + 2 * laenge
        if struct.unpack("<i", inhalt[:4])[0] == 0:
            aus.append(None)
            continue
        nteile, npunkte = struct.unpack("<ii", inhalt[36:44])
        teile = list(struct.unpack(f"<{nteile}i", inhalt[44:44 + 4 * nteile])) + [npunkte]
        xy = np.frombuffer(inhalt, "<f8", 2 * npunkte, 44 + 4 * nteile).reshape(-1, 2)
        aussen, loecher = [], []
        for a, e in zip(teile, teile[1:]):
            ring = xy[a:e]
            if len(ring) < 4:
                continue
            (loecher if shapely.LinearRing(ring).is_ccw else aussen).append(ring)
        polys = []
        for ring in aussen:
            p = Polygon(ring)
            eigene = [h for h in loecher if p.contains(shapely.Point(h[0]))]
            polys.append(Polygon(ring, eigene))
        aus.append(polys[0] if len(polys) == 1 else MultiPolygon(polys) if polys else None)
    return aus


def schicht_lesen(z: zipfile.ZipFile, name: str, felder: list[str]):
    stamm = SCHICHT.format(name)
    attr = dbf_lesen(z.read(stamm + ".dbf"), felder)
    geom = shp_polygone(z.read(stamm + ".shp"))
    if len(attr) != len(geom):
        raise SystemExit(f"{name}: {len(attr)} DBF-Datensätze, {len(geom)} Geometrien")
    crs = CRS.from_wkt(z.read(stamm + ".prj").decode("ascii"))
    info = z.getinfo(stamm + ".dbf").date_time
    return attr, geom, crs, "%04d-%02d-%02d" % info[:3]


# ---------------------------------------------------------------- Kennzahlen
def leerer_block() -> dict:
    return {"n": 0, "zustand": Counter(), "kst": Counter(), "wohn": 0, "wohn_art": Counter(),
            "gs_alle": [], "gs_wohn": [], "kl_alle": Counter(), "kl_wohn": Counter(),
            "gf": 0.0, "gf_wohn": 0.0, "gfz_z": 0.0}


def klasse(gs: int | None) -> str:
    if not gs:
        return "unbekannt"
    return "1" if gs == 1 else "2" if gs == 2 else "3_4" if gs <= 4 else "5_10" if gs <= 10 else "11p"


def zaehlen(B: dict, g: dict) -> None:
    B["n"] += 1
    B["zustand"][g["zustand"]] += 1
    B["kst"][g["kst"]] += 1
    B["kl_alle"][klasse(g["gs"])] += 1
    if g["gs"]:
        B["gs_alle"].append(g["gs"])
    if g["kst"] == "110":
        B["wohn"] += 1
        B["wohn_art"]["ein" if g["pf"] == EIN else "mehr" if g["pf"] == MEHR else "sonst"] += 1
        B["kl_wohn"][klasse(g["gs"])] += 1
        if g["gs"]:
            B["gs_wohn"].append(g["gs"])
    if g["zustand"] != "zniszczony":
        B["gf"] += g["flaeche"]
        if g["kst"] == "110":
            B["gf_wohn"] += g["flaeche"]
        if g["gs"]:
            B["gfz_z"] += g["flaeche"] * g["gs"]


def lage(werte: list[int]) -> tuple[float | None, float | None]:
    if len(werte) < MINDESTFALLZAHL:
        return None, None
    return float(statistics.median(werte)), round(sum(werte) / len(werte), 1)


def block_ausgeben(B: dict, flaeche: float, name: str | None = None) -> dict:
    med, mit = lage(B["gs_alle"])
    med_w, mit_w = lage(B["gs_wohn"])
    gf, fl = round(B["gf"]), round(flaeche)
    aus = {"name": name} if name is not None else {}
    aus.update({
        "anzahl": B["n"],
        "zustand": {ZUSTAND_SCHLUESSEL[z]: B["zustand"].get(z, 0) for z in ZUSTAENDE},
        "funktion": {k: B["kst"].get(k, 0) for k in KST},
        "funktion_unbekannt": B["n"] - sum(B["kst"].get(k, 0) for k in KST),
        "wohngebaeude": B["wohn"],
        "wohn_art": {k: B["wohn_art"].get(k, 0) for k in ("ein", "mehr", "sonst")},
        "geschosse": {k: B["kl_alle"].get(k, 0) for k in GESCHOSS_KLASSEN},
        "geschosse_wohn": {k: B["kl_wohn"].get(k, 0) for k in GESCHOSS_KLASSEN},
        "geschosse_median": med, "geschosse_mittel": mit,
        "geschosse_median_wohn": med_w, "geschosse_mittel_wohn": mit_w,
        "grundflaeche_m2": gf,
        "grundflaeche_wohn_m2": round(B["gf_wohn"]),
        "flaeche_m2": fl,
        "bebauungsdichte": {"wert": round(100 * gf / fl, 1) if fl else None, "zaehler": gf, "nenner": fl,
                            "anzeige": "anteil"},
        "geschossflaeche_naeherung": {"wert": round(B["gfz_z"] / fl, 2) if fl else None,
                                      "zaehler": round(B["gfz_z"]), "nenner": fl, "abzeichen": "orientacyjnie"},
    })
    return aus


# ---------------------------------------------------------------- Lesen der Eingaben
def js_lesen(pfad: Path):
    t = pfad.read_text(encoding="utf-8")
    m = re.search(r"window\.([A-Za-z0-9_]+)\s*=\s*", t)
    return m.group(1), json.loads(t[m.end():].rstrip().rstrip(";"))


def lod_modul():
    spec = importlib.util.spec_from_file_location("lod", WURZEL / "skripte" / "20_lod.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rechnen(bdot: Path, geometrie: bool):
    z = zipfile.ZipFile(bdot)
    attr, geom, crs_q, zipdatum = schicht_lesen(z, "BUBD_A", FELDER_BUBD)
    a_adja, g_adja, crs_a, _ = schicht_lesen(z, "ADJA_A", FELDER_ADJA)
    if crs_a != crs_q:
        raise SystemExit("OT_ADJA_A und OT_BUBD_A in verschiedenen Koordinatensystemen")
    rechen = CRS.from_epsg(ort_konfig.RECHEN_SRID)
    nach_rechen = Transformer.from_crs(crs_q, rechen, always_xy=True)
    nach_wgs = Transformer.from_crs(crs_q, CRS.from_epsg(4326), always_xy=True)
    von_wgs = Transformer.from_crs(CRS.from_epsg(4326), crs_q, always_xy=True)

    def in_rechen(g):
        return shapely.transform(g, lambda xy: np.column_stack(nach_rechen.transform(xy[:, 0], xy[:, 1])))

    Z: dict = {"bdot_datei": bdot.name, "zip_datum": zipdatum, "crs_quelle": crs_q.name,
               "rechen": ort_konfig.srs_name()}
    # Stadt und Delegaturen
    stadt = [(a, g) for a, g in zip(a_adja, g_adja) if a and a["RODZAJ"] == "gmina" and a["NAZWA"] == "Kraków"]
    dele = sorted([(a, g) for a, g in zip(a_adja, g_adja) if a and a["RODZAJ"] == "dzielnica lub delegatura"],
                  key=lambda x: x[0]["IDTERYTJED"])
    if len(stadt) != 1 or not dele:
        raise SystemExit(f"OT_ADJA_A: {len(stadt)} Gemeinde-Polygone Kraków, {len(dele)} Delegaturen")
    g_stadt = shapely.make_valid(stadt[0][1])
    g_dele = [shapely.make_valid(g) for _, g in dele]
    fl_stadt = in_rechen(g_stadt).area
    fl_dele = [in_rechen(g).area for g in g_dele]
    vereinigung = in_rechen(shapely.union_all(g_dele)).area
    ueberlapp = max([in_rechen(shapely.intersection(g_dele[i], g_dele[j])).area
                     for i in range(len(g_dele)) for j in range(i + 1, len(g_dele))] or [0.0])
    Z.update({"delegaturen": len(dele), "flaeche_stadt_m2": round(fl_stadt),
              "flaeche_vereinigung_m2": round(vereinigung), "ueberlappung_max_m2": round(ueberlapp, 3),
              "deckung": round(vereinigung / fl_stadt, 6)})

    # dzielnice
    name_st, ST = js_lesen(DATEN / "stadtteile_odbl.js")
    st_fixture = ST.get("fixture") is True
    st = []
    for f in sorted(ST["features"], key=lambda f: f["properties"]["nr"]):
        g = shapely.make_valid(shape(f["geometry"]))
        g = shapely.transform(g, lambda xy: np.column_stack(von_wgs.transform(xy[:, 0], xy[:, 1])))
        st.append((f["properties"]["nr"], f["properties"].get("name"), g))
    fl_st = [in_rechen(g).area for _, _, g in st]

    # Höhen aus LoD (Handdownload)
    lod = lod_modul()
    eingang = daten_ordner() / "eingang"
    hoehen = {}
    for art in ("lod1", "lod2"):
        pfade = lod.eingangsdateien(eingang, art)
        h, zl = lod.hoehen_lesen(pfade) if pfade else ({}, None)
        hoehen[art] = h
        Z[f"{art}_dateien"] = [p.name for p in pfade]
        Z[f"{art}_zaehlung"] = zl

    # Gebäude
    gueltig = [i for i, a in enumerate(attr) if a is not None]
    Z["datensaetze"] = len(attr)
    Z["geloescht"] = len(attr) - len(gueltig)
    Z["ohne_geometrie"] = sum(1 for i in gueltig if geom[i] is None)
    idx = [i for i in gueltig if geom[i] is not None]
    gs_ = np.array([geom[i] for i in idx], dtype=object)
    ungueltig = ~shapely.is_valid(gs_)
    Z["ungueltig_repariert"] = int(ungueltig.sum())
    gs_[ungueltig] = shapely.make_valid(gs_[ungueltig])
    flaechen = shapely.area(in_rechen(gs_))
    Z["flaeche_null"] = int((flaechen <= 0).sum())
    punkte = shapely.point_on_surface(gs_)
    px, py = shapely.get_x(punkte), shapely.get_y(punkte)
    shapely.prepare(g_stadt)
    in_stadt = shapely.contains_xy(g_stadt, px, py)
    zu_dele = np.full(len(idx), -1)
    for k, g in enumerate(g_dele):
        shapely.prepare(g)
        treffer = shapely.contains_xy(g, px, py)
        Z.setdefault("mehrfach_delegatur", 0)
        Z["mehrfach_delegatur"] += int((treffer & (zu_dele >= 0)).sum())
        zu_dele[treffer & (zu_dele < 0)] = k
    zu_st = np.full(len(idx), -1)
    Z["mehrfach_dzielnica"] = 0
    for k, (_, _, g) in enumerate(st):
        shapely.prepare(g)
        treffer = shapely.contains_xy(g, px, py)
        Z["mehrfach_dzielnica"] += int((treffer & (zu_st >= 0)).sum())
        zu_st[treffer & (zu_st < 0)] = k

    B_stadt, B_dele, B_st = leerer_block(), [leerer_block() for _ in dele], [leerer_block() for _ in st]
    roh = {k: Counter() for k in ("FOBUD", "KAT_ISTNIE", "ZRO_DANYCH", "LICZ_KONDY")}
    hq_z, kacheln = Counter(), {nr: [] for nr, _, _ in st}
    Z["duplikat_vermerk"] = 0
    for j, i in enumerate(idx):
        a = attr[i]
        for k in roh:
            roh[k][a[k]] += 1
        if DUPLIKAT.match(a["UWAGI"]):
            Z["duplikat_vermerk"] += 1
        try:
            gs = int(float(a["LICZ_KONDY"])) if a["LICZ_KONDY"] else None
        except ValueError:
            gs = None
        g = {"zustand": a["KAT_ISTNIE"], "kst": a["KODKST"], "pf": a["PFBUD"], "gs": gs or None,
             "flaeche": float(flaechen[j])}
        if in_stadt[j]:
            zaehlen(B_stadt, g)
        if zu_dele[j] >= 0:
            zaehlen(B_dele[zu_dele[j]], g)
        if zu_st[j] >= 0:
            zaehlen(B_st[zu_st[j]], g)
        # Höhe
        if a["LOKALNYID"] in hoehen["lod1"]:
            h, hq = hoehen["lod1"][a["LOKALNYID"]][0], "lod1"
        elif a["LOKALNYID"] in hoehen["lod2"]:
            h, hq = hoehen["lod2"][a["LOKALNYID"]][0], "lod2"
        elif gs:
            h, hq = gs * GESCHOSS_HOEHE_M, "geschosse"
        else:
            h, hq = ERSATZ_HOEHE_M, "ersatz"
        hq_z[hq] += 1
        if geometrie and zu_st[j] >= 0:
            kacheln[st[zu_st[j]][0]].append((gs_[j], {"f": a["KODKST"] or "unbekannt", "gs": gs or None,
                                                      "h": int(round(h)), "hq": hq}))
    Z["roh"] = {k: dict(sorted(v.items(), key=lambda x: (-x[1], x[0]))) for k, v in roh.items()}
    Z["in_stadt"] = int(in_stadt.sum())
    Z["ausserhalb_stadt"] = len(idx) - Z["in_stadt"]
    Z["in_delegatur"] = int((zu_dele >= 0).sum())
    Z["in_stadt_ohne_delegatur"] = int((in_stadt & (zu_dele < 0)).sum())
    Z["in_dzielnica"] = int((zu_st >= 0).sum())
    Z["hoehe_herkunft"] = {k: hq_z.get(k, 0) for k in ("lod1", "lod2", "geschosse", "ersatz")}
    Z["max_wersja"] = max(attr[i]["WERSJA"] for i in idx)[:8]
    Z["stadtteile_fixture"] = st_fixture
    Z["stadtteile_global"] = name_st

    stand = f"{Z['max_wersja'][:4]}-{Z['max_wersja'][4:6]}-{Z['max_wersja'][6:8]}"
    quellen = {"bdot10k": {"datei": bdot.name, "stand_juengste_wersja": stand, "dateidatum": zipdatum,
                           "vermerk": VERMERK},
               "delegatury": {"vermerk": VERMERK_PRG}}
    if any(Z[f"{a}_dateien"] for a in ("lod1", "lod2")):
        quellen["hoehen"] = {"vermerk": vermerk_lod(Z), "dateien": Z["lod1_dateien"] + Z["lod2_dateien"]}
    methode = {"zuordnung": "punkt_im_polygon", "rechen_srid": ort_konfig.RECHEN_SRID,
               "mindestfallzahl": MINDESTFALLZAHL, "geschoss_hoehe_m": GESCHOSS_HOEHE_M}
    K = {"stand_daten": stand, "quellen": quellen, "methode": methode,
         "stadt": block_ausgeben(B_stadt, fl_stadt, "Kraków"),
         "delegatury": {a["IDTERYTJED"]: block_ausgeben(B, fl, a["NAZWA"])
                        for (a, _), B, fl in zip(dele, B_dele, fl_dele)},
         "kontrolle": {"datensaetze": Z["datensaetze"], "in_stadt": Z["in_stadt"],
                       "ausserhalb_stadt": Z["ausserhalb_stadt"], "in_stadt_ohne_delegatur": Z["in_stadt_ohne_delegatur"],
                       "ungueltig_repariert": Z["ungueltig_repariert"], "duplikat_vermerk": Z["duplikat_vermerk"],
                       "deckung_delegatury": Z["deckung"]}}
    D = {"stand_daten": stand}
    if st_fixture:
        D["fixture"] = True
        D["hinweis"] = ("Beispieldaten: echte Gebäude, aber Rechtecke statt Stadtteilgrenzen; keine Aussage über "
                        "die dzielnice.")
    D.update({"quellen": quellen, "methode": methode,
              "stadtteile": {nr: block_ausgeben(B, fl, name) for (nr, name, _), B, fl in zip(st, B_st, fl_st)},
              "kontrolle": {"in_dzielnica": Z["in_dzielnica"], "in_stadt": Z["in_stadt"],
                            "mehrfach_dzielnica": Z["mehrfach_dzielnica"]}})
    kach = {}
    if geometrie:
        for nr, liste in kacheln.items():
            if not liste:
                continue
            gg = np.array([x[0] for x in liste], dtype=object)
            gg = shapely.transform(gg, lambda xy: np.column_stack(nach_wgs.transform(xy[:, 0], xy[:, 1])))
            gg = shapely.set_precision(gg, 1e-6)
            feats = []
            for g, p in zip(gg, (x[1] for x in liste)):
                if g.is_empty:
                    continue
                feats.append({"type": "Feature", "geometry": json.loads(shapely.to_geojson(g)), "properties": p})
            kach[nr] = {"type": "FeatureCollection", **({"fixture": True} if st_fixture else {}), "features": feats}
    return K, D, Z, kach


# ---------------------------------------------------------------- Ausgabe
def js_text(name: str, kopf: str, inhalt) -> str:
    return f"/* {kopf} */\nwindow.{name}=" + json.dumps(inhalt, ensure_ascii=False, separators=(",", ":")) + ";\n"


KOPF_K = ("Gebäudekennzahlen Kraków je Stadt und Delegatur, erzeugt von skripte/20_bdot10k.py; nicht von Hand ändern. "
          + VERMERK + ". " + VERMERK_PRG + ".")
KOPF_D = ("Gebäudekennzahlen je dzielnica, erzeugt von skripte/20_bdot10k.py; nicht von Hand ändern. " + VERMERK
          + ". Stadtteilgrenzen: Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/), "
          "© OpenStreetMap-Mitwirkende (ODbL).")


def lauf_md(Z: dict, K: dict) -> str:
    z = [f"# Lauf Gebäude BDOT10k (erzeugt von `skripte/20_bdot10k.py`, nicht von Hand ändern)", "",
         f"Eingabe `{Z['bdot_datei']}`, Dateidatum im Archiv {Z['zip_datum']}, jüngste `WERSJA` {K['stand_daten']}.",
         f"Koordinatensystem der Quelle: {Z['crs_quelle']}; Flächen in {Z['rechen']}.", "",
         "## Schritte", "", "| Schritt | Zahl |", "|---|---|"]
    zeilen = [("Datensätze `OT_BUBD_A` (DBF)", Z["datensaetze"]), ("davon als gelöscht markiert", Z["geloescht"]),
              ("ohne Geometrie", Z["ohne_geometrie"]), ("ungültige Grundrisse, mit make_valid gerechnet", Z["ungueltig_repariert"]),
              ("Grundriss ohne Fläche", Z["flaeche_null"]), ("mit Vermerk „Duplikaty …“ in `UWAGI` (nicht entfernt)", Z["duplikat_vermerk"]),
              ("innerer Punkt in der Gemeinde Kraków", Z["in_stadt"]), ("außerhalb der Gemeinde", Z["ausserhalb_stadt"]),
              ("in einer Delegatur", Z["in_delegatur"]), ("in der Gemeinde, aber in keiner Delegatur", Z["in_stadt_ohne_delegatur"]),
              ("in mehr als einer Delegatur (nur die erste gezählt)", Z["mehrfach_delegatur"]),
              ("in einer dzielnica (" + ("Beispielrechtecke" if Z["stadtteile_fixture"] else "Grenzen aus daten/stadtteile_odbl.js") + ")", Z["in_dzielnica"]),
              ("in mehr als einer dzielnica (nur die erste gezählt)", Z["mehrfach_dzielnica"])]
    z += [f"| {a} | {b} |" for a, b in zeilen]
    z += ["", "## Gemeinde und Delegaturen (`OT_ADJA_A`)", "", "| Größe | Wert |", "|---|---|",
          f"| Delegaturen | {Z['delegaturen']} |", f"| Fläche Gemeinde (m²) | {Z['flaeche_stadt_m2']} |",
          f"| Fläche Vereinigung der Delegaturen (m²) | {Z['flaeche_vereinigung_m2']} |",
          f"| Deckung Vereinigung / Gemeinde | {Z['deckung']} |", f"| größte Überlappung zweier Delegaturen (m²) | {Z['ueberlappung_max_m2']} |",
          "", "## Verteilungen in der Quelle (alle Datensätze mit Geometrie)", ""]
    for k, v in Z["roh"].items():
        z.append(f"- `{k}`: " + "; ".join(f"{a or '(leer)'} {b}" for a, b in v.items()))
    z += ["", "## Höhe für 3D", "", "| Herkunft | Gebäude |", "|---|---|"]
    z += [f"| {k} | {v} |" for k, v in Z["hoehe_herkunft"].items()]
    for art in ("lod1", "lod2"):
        z.append("")
        z.append(f"- {art}: " + (f"Dateien {', '.join(Z[art + '_dateien'])}; Zählung {json.dumps(Z[art + '_zaehlung'], ensure_ascii=False)}"
                                 if Z[art + "_dateien"] else "keine Datei unter `$KIEZ_DATEN/eingang/` (Handdownload ausstehend)"))
    S = K["stadt"]
    z += ["", "## Stadt (Kurzfassung, vollständig in `daten/gebaeude_kennzahlen.js`)", "",
          f"- Gebäude {S['anzahl']}, Wohngebäude {S['wohngebaeude']} (Einfamilien {S['wohn_art']['ein']}, "
          f"Mehrfamilien {S['wohn_art']['mehr']}, sonst {S['wohn_art']['sonst']})",
          f"- Geschosse bekannt bei {S['anzahl'] - S['geschosse']['unbekannt']}; Median {S['geschosse_median']}, Mittel {S['geschosse_mittel']}",
          f"- Grundfläche {S['grundflaeche_m2']} m² von {S['flaeche_m2']} m², Bebauungsdichte {S['bebauungsdichte']['wert']} %",
          ""]
    return "\n".join(z)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bdot", type=Path, default=None)
    ap.add_argument("--geometrie", type=Path, default=None, help="Ordner für <nr>.js je dzielnica")
    ap.add_argument("--pruefen", action="store_true")
    a = ap.parse_args()
    bdot = a.bdot or daten_ordner() / "2026-11-13" / "03_gebaeude" / "1261_SHP.zip"
    if not bdot.exists():
        print(f"BDOT10k-Datei fehlt: {bdot}")
        return 2
    K, D, Z, kach = rechnen(bdot, a.geometrie is not None)
    ausgaben = {DATEN / "gebaeude_kennzahlen.js": js_text("KIEZ_GEB_KENNZAHLEN", KOPF_K, K),
                DATEN / "gebaeude_dzielnice_odbl.js": js_text("KIEZ_GEB_DZIELNICE", KOPF_D, D),
                WURZEL / "belege" / "D5_gebaeude_lauf.md": lauf_md(Z, K)}
    if a.geometrie:
        # Welche Gebäude in welche Datei kommen, entscheiden die OSM-Grenzen: echte Grenzen -> <nr>_odbl.js mit Vermerk
        odbl = not Z["stadtteile_fixture"]
        kopf_g = ("Gebäude je dzielnica für 3D, erzeugt von skripte/20_bdot10k.py. " + VERMERK
                  + (". " + vermerk_lod(Z) if Z["hoehe_herkunft"]["lod1"] + Z["hoehe_herkunft"]["lod2"] else "")
                  + (". Przypisanie do dzielnic: granice © OpenStreetMap-Mitwirkende / autorzy OpenStreetMap, "
                     "Open Database License (ODbL) 1.0 (https://www.openstreetmap.org/copyright)" if odbl else
                     ". Beispiel-Zuordnung über Rechtecke, keine Stadtteilgrenzen"))
        for nr, inhalt in kach.items():
            ausgaben[a.geometrie / f"{nr}{'_odbl' if odbl else ''}.js"] = js_text(f"KIEZ_GEB_{nr}", kopf_g, inhalt)
        # Manifest wie bei der Grundkarte (Format von sha256sum), gelesen von skripte/deploy_kopie.py und
        # skripte/entwicklung_server.mjs
        geo = sorted(p for p in ausgaben if p.parent == a.geometrie)
        ausgaben[a.geometrie / "MANIFEST.sha256"] = "".join(
            f"{hashlib.sha256(ausgaben[p].encode('utf-8')).hexdigest()}  {p.name}\n" for p in geo)
    if a.pruefen:
        man = a.geometrie / "MANIFEST.sha256" if a.geometrie else None
        if man and not man.exists() and (a.geometrie / "SHA256SUMS").exists():
            # Ordner vom 13.11.2026: das Manifest heißt dort SHA256SUMS (gleiches Format), docs/entscheidungen.md KR42
            ausgaben[a.geometrie / "SHA256SUMS"] = ausgaben.pop(man)
        abw = [str(p.relative_to(WURZEL) if p.is_relative_to(WURZEL) else p) for p, t in ausgaben.items()
               if not p.exists() or p.read_text(encoding="utf-8") != t]
        print("byte-gleich: " + ", ".join(p.name for p in ausgaben) if not abw else f"Abweichung: {abw}")
        return 1 if abw else 0
    for p, t in ausgaben.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t, encoding="utf-8")
        print(f"geschrieben {p} ({len(t.encode())} Bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
