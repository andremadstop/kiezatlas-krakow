"""Wohnungsmarkt: Median Preis je m² Wohnfläche je dzielnica, Jahr und Markt aus dem Rejestr cen nieruchomości.

Regeln (vor dem ersten Lauf festgelegt): pruefen/DW_protokoll.md. Quelle, Lizenz und erwartete Eingabe:
quellen-DW.md. Prüfung der Ausgabe: pruefen/DW_mieszkania.py.

Eingabe:  $KIEZ_DATEN/eingang/rcn/*.gpkg (Handdownload GeoPackage Powiat 1261 aus geoportal.gov.pl, genau eine
          Datei), daten/stadtteile_odbl.js (Stadtteilgrenzen, WGS 84).
Ausgabe:  daten/mieszkania_odbl.js (window.KIEZ_MIESZKANIA, Vertrag daten/schema/mieszkania_odbl.json),
          belege/DW_mieszkania.md (Zählungen je Schritt, aus demselben Lauf).
Kein Netz, keine Datenbank. Liest die Rohdatei nur; schreibt nichts nach $KIEZ_DATEN.

Aufruf (aus der Projektumgebung):
  python -I skripte/40_mieszkania.py              echte Daten aus eingang/rcn/ (fehlt die Datei: Rückgabe 3)
  python -I skripte/40_mieszkania.py --beispiel   Beispieldatei im erwarteten Format erzeugen (Zufall mit fester
                                                  Saat, erfundene Preise) und dieselbe Kette darauf rechnen;
                                                  Ausgabe mit fixture: true
  python -I skripte/40_mieszkania.py --pruefen    neu rechnen wie im vorhandenen daten/mieszkania_odbl.js angegeben
                                                  (Beispiel oder echte Datei mit gleichem SHA256) und byte-genau
                                                  mit daten/mieszkania_odbl.js und belege/DW_mieszkania.md vergleichen
  --spalten                                       nur die Tabellen und Spalten der Eingabedatei zeigen
Rückgabe: 0 gut, 1 Abweichung (--pruefen), 2 falscher Aufruf, 3 Eingabe fehlt, 4 Eingabe passt nicht zum
erwarteten Format (Spalte oder Codewert unbekannt; das Skript nennt, was es gefunden hat).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sqlite3
import statistics
import struct
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import shapely
from pyproj import CRS, Transformer
from shapely.geometry import Point, box, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))   # eigener Code; python -I lässt das Skriptverzeichnis weg
from ort_konfig import RECHEN_SRID, srs_name  # noqa: E402  Koordinatensystem der Beispieldatei aus config/<ort>.yaml

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "daten"
AUSGABE = DATEN / "mieszkania_odbl.js"
BELEG = WURZEL / "belege" / "DW_mieszkania.md"
STADTTEILE = DATEN / "stadtteile_odbl.js"
SAAT = 20261113

MINDESTFALLZAHL = 10
ERSTES_JAHR = 2019                # F11: frühere Jahre nicht veröffentlicht (pruefen/DW_protokoll.md, Änderung KR55)
FLAECHE = (8.0, 400.0)            # m², F8
PREIS_JE_M2 = (1000.0, 100000.0)  # zł/m², F8
MAERKTE = ("ogolem", "pierwotny", "wtorny")

QUELLE = {
    "vermerk": ("Rejestr cen nieruchomości, Prezydent Miasta Krakowa (powiat 1261); dane udostępnione przez "
                "Główny Urząd Geodezji i Kartografii w serwisie www.geoportal.gov.pl; opracowanie własne "
                "(mediany, bez danych jednostkowych)"),
    "rechtsgrundlage": ("art. 40a ust. 2 pkt 1 lit. k oraz art. 40c ust. 3 i 5 ustawy – Prawo geodezyjne i "
                        "kartograficzne (Dz.U. 2026 poz. 1389)"),
    "url": "https://www.geoportal.gov.pl/pl/dane/rejestr-cen-nieruchomosci-rcn/",
}

# Bedeutung -> mögliche Spaltennamen (verglichen ohne Groß-/Kleinschreibung, Unterstriche und Diakritika).
# Annahme nach den Attributen des RCN-Modells (Rozporządzenie w sprawie EGiB, 27.07.2021) und der Attributliste
# auf geoportal.gov.pl (Meldung 18.02.2026); jeweils zuerst die Namen der GUGiK-Datei vom 14.11.2026
# (pruefen/DW_protokoll.md, „Änderung 14.11.2026“). Erweitern = Protokolländerung.
SPALTEN = {
    "transaktion": ["tran_oznaczenie_trans", "oznaczenieTransakcji", "oznaczenie_transakcji", "idTransakcji"],
    "lokal_id": ["lok_id_lokalu", "idLokalu", "identyfikatorLokalu", "id_lokalu"],
    "art_transaktion": ["tran_rodzaj_trans", "rodzajTransakcji", "rodzaj_transakcji"],
    "markt": ["tran_rodzaj_rynku", "rodzajRynku", "rodzaj_rynku"],
    "anteil": ["nier_udzial", "udzialWPrawieDoNieruchomosci", "udzialWPrawie", "udzial"],
    "datum": ["dok_data", "dataSporzadzeniaDokumentu", "data_sporzadzenia_dokumentu", "dataDokumentu"],
    "funktion": ["lok_funkcja", "funkcjaLokalu", "funkcja_lokalu"],
    "flaeche": ["lok_pow_uzyt", "polePowierzchniUzytkowejLokalu", "powierzchniaUzytkowaLokalu", "polePowUzytkowejLokalu",
                "pow_uzytkowa_lokalu"],
    "preis_lokal": ["lok_cena_brutto", "cenaLokaluBrutto", "cena_lokalu_brutto"],
    "preis_transaktion": ["tran_cena_brutto", "cenaTransakcjiBrutto", "cena_transakcji_brutto"],
}
PFLICHT_LOKAL = ("transaktion", "art_transaktion", "markt", "anteil", "datum", "funktion", "flaeche",
                 "preis_lokal", "preis_transaktion")
# Codelisten: normierter Wert -> Bedeutung. Unbekannte, nicht leere Werte führen zum Abbruch.
FUNKTION = {"lokalmieszkalny": "wohnung", "mieszkalny": "wohnung", "mieszkalna": "wohnung", "mieszkalne": "wohnung",
            "lokaluzytkowy": "andere", "uzytkowy": "andere", "uzytkowa": "andere", "garaz": "andere",
            "lokalgarazowy": "andere", "garazowy": "andere", "pracowniatworcza": "andere", "inny": "andere",
            "inna": "andere", "handlowouslugowa": "andere", "biurowa": "andere", "produkcyjna": "andere"}  # Änderung 14.11.
ART = {"wolnyrynek": "frei", "sprzedazbezprzetargowa": "andere", "bezprzetargowa": "andere",
       "sprzedazprzetargowa": "andere", "przetargowa": "andere", "przetarg": "andere", "inna": "andere",
       "innatransakcja": "andere", "sprzedazzbonifikata": "andere",
       "sprzedazwpostepowaniuegzekucyjnym": "andere", "sprzedaznacelpubliczny": "andere"}  # Änderung 14.11.
MARKT = {"pierwotny": "pierwotny", "rynekpierwotny": "pierwotny", "wtorny": "wtorny", "rynekwtorny": "wtorny"}

# Schritte: Nummer, Schlüssel in den Daten (keine Sätze in daten/, KR43), Beschreibung nur für den Beleg
SCHRITTE = [
    ("F0", "lokale", "Zeilen der Lokal-Ebene"),
    ("F1", "ohne_dubletten", "ohne Dubletten (Transaktion und Lokal)"),
    ("F2", "funktion_wohnung", "Funktion Wohnung"),
    ("F3", "freier_markt", "freier Markt"),
    ("F4", "volles_recht", "volles Recht (Anteil 1/1)"),
    ("F5", "eine_wohnung_je_transaktion", "genau eine Wohnung je Transaktion"),
    ("F6", "preis_vorhanden", "Preis vorhanden"),
    ("F7", "flaeche_vorhanden", "Nutzfläche vorhanden"),
    ("F8", "plausibel", "Fläche und Preis je m² in den Plausibilitätsgrenzen"),
    ("F9", "datum_vorhanden", "Datum des Dokuments vorhanden"),
    ("F10", "dzielnica_zugeordnet", "einer dzielnica zugeordnet"),
    ("F11", "ab_erstem_jahr", f"Dokumentjahr ab {ERSTES_JAHR} (Jahre davor nicht veröffentlicht, KR55)"),
]
SCHRITT_TEXT = {k: t for _, k, t in SCHRITTE}


class FormatFehler(Exception):
    """Eingabe passt nicht zum erwarteten Format (Rückgabe 4)."""


def norm(s) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s).replace("ł", "l").replace("Ł", "L"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[\s_\-./]", "", s.lower())


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def js_lesen(pfad: Path):
    text = pfad.read_text(encoding="utf-8")
    m = re.search(r"window\.([A-Za-z0-9_]+)\s*=\s*", text)
    return json.loads(text[m.end():].rstrip().rstrip(";"))


# ---------------------------------------------------------------- Stadtteile
def stadtteile_laden() -> list[tuple[str, object]]:
    fc = js_lesen(STADTTEILE)
    teile = [(f["properties"]["nr"], shape(f["geometry"])) for f in fc["features"]]
    for _, g in teile:
        shapely.prepare(g)
    return sorted(teile)


# ---------------------------------------------------------------- GeoPackage lesen
def gpkg_geometrie(blob: bytes):
    """GeoPackage-Geometrie (Kopf 'GP' + Hülle + WKB) -> shapely; None bei leer oder fehlend."""
    if blob is None:
        return None
    if blob[:2] != b"GP":
        raise FormatFehler("Geometriespalte ohne GeoPackage-Kopf 'GP'")
    flags = blob[3]
    if flags & 0b10000:          # leere Geometrie
        return None
    huelle = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}.get((flags >> 1) & 0b111)
    if huelle is None:
        raise FormatFehler("unbekannter Hüllentyp im GeoPackage-Kopf")
    return shapely.from_wkb(bytes(blob[8 + huelle:]))


def tabellen(con) -> list[dict]:
    aus = []
    zeilen = con.execute("SELECT c.table_name, g.column_name, g.srs_id FROM gpkg_contents c "
                         "JOIN gpkg_geometry_columns g ON g.table_name = c.table_name "
                         "WHERE c.data_type = 'features' ORDER BY c.table_name").fetchall()
    for name, geom, srs in zeilen:
        spalten = [r[1] for r in con.execute(f'PRAGMA table_info("{name}")')]
        aus.append({"name": name, "geom": geom, "srs": srs, "spalten": spalten})
    return aus


def zuordnen(spalten: list[str]) -> dict[str, str]:
    n = {norm(s): s for s in spalten}
    return {bed: next((n[norm(k)] for k in kand if norm(k) in n), None) for bed, kand in SPALTEN.items()}


def crs_von(con, srs_id: int) -> CRS:
    r = con.execute("SELECT organization, organization_coordsys_id, definition FROM gpkg_spatial_ref_sys "
                    "WHERE srs_id = ?", (srs_id,)).fetchone()
    if r is None or srs_id in (0, -1):
        raise FormatFehler(f"Bezugssystem {srs_id} nicht in gpkg_spatial_ref_sys oder undefiniert")
    org, code, wkt = r
    if org and org.upper() == "EPSG":
        return CRS.from_epsg(int(code))
    return CRS.from_wkt(wkt)


def zahl(x) -> float | None:
    if x is None or x == "":
        return None
    try:
        return float(str(x).replace(",", ".").replace(" ", ""))
    except ValueError:
        return None


def anteil_voll(x) -> bool:
    s = str(x).strip().replace(" ", "") if x is not None else ""
    if not s:
        return False
    if "/" in s:
        a, _, b = s.partition("/")
        try:
            return int(a) == int(b) and int(b) > 0
        except ValueError:
            return False
    z = zahl(s)
    return z is not None and abs(z - 1.0) < 1e-9


def datum(x) -> date | None:
    m = re.match(r"^\s*(\d{4})-(\d{2})-(\d{2})", str(x)) if x is not None else None
    if not m:
        return None
    try:
        return date(int(m[1]), int(m[2]), int(m[3]))
    except ValueError:
        return None


def code(wert, liste: dict, bedeutung: str, unbekannt: set) -> str | None:
    n = norm(wert)
    if not n:
        return None
    if n not in liste:
        unbekannt.add(f"{bedeutung}: {wert!r}")
        return None
    return liste[n]


def lesen(gpkg: Path) -> tuple[list[dict], set, dict]:
    """Lokal-Zeilen (Bedeutungen statt Spaltennamen, Punkt in WGS 84) und Transaktionen anderer Objekte."""
    con = sqlite3.connect(f"file:{gpkg}?mode=ro", uri=True)
    try:
        tabs = tabellen(con)
        lokal = [t for t in tabs if (z := zuordnen(t["spalten"]))["funktion"] and z["flaeche"]]
        if len(lokal) != 1:
            raise FormatFehler(f"{len(lokal)} Tabellen mit Spalten für Funktion und Nutzfläche des Lokals; "
                               f"vorhanden: " + "; ".join(f"{t['name']}: {', '.join(t['spalten'])}" for t in tabs))
        t = lokal[0]
        z = zuordnen(t["spalten"])
        fehlt = [b for b in PFLICHT_LOKAL if not z[b]]
        if fehlt:
            raise FormatFehler(f"Tabelle {t['name']}: keine Spalte für {fehlt}; vorhanden: {', '.join(t['spalten'])}")
        nach_wgs = Transformer.from_crs(crs_von(con, t["srs"]), CRS.from_epsg(4326), always_xy=True)
        bed = [b for b in SPALTEN if z[b]]
        sql = ", ".join(f'"{z[b]}"' for b in bed) + f', "{t["geom"]}"'
        zeilen = []
        for r in con.execute(f'SELECT {sql} FROM "{t["name"]}" ORDER BY rowid'):
            d = dict(zip(bed, r[:-1]))
            g = gpkg_geometrie(r[-1])
            if g is not None and not g.is_empty:
                p = g.representative_point()
                d["lon"], d["lat"] = nach_wgs.transform(p.x, p.y)
            else:
                d["lon"] = d["lat"] = None
            zeilen.append(d)
        andere = set()       # Transaktionen, zu denen in der Datei auch eine Parzelle oder ein Gebäude gehört
        # Datenstand nach Protokoll: jüngstes Dokumentdatum der Datei, über alle Tabellen und vor den Filtern
        daten = [x for d in zeilen if (x := datum(d.get("datum"))) is not None]
        for o in tabs:
            if o is t:
                continue
            zo = zuordnen(o["spalten"])
            if zo["transaktion"]:
                andere |= {r[0] for r in con.execute(f'SELECT "{zo["transaktion"]}" FROM "{o["name"]}"')
                           if r[0] not in (None, "")}
            if zo["datum"]:
                daten += [x for (w,) in con.execute(f'SELECT DISTINCT "{zo["datum"]}" FROM "{o["name"]}"')
                          if (x := datum(w)) is not None]
        info = {"tabelle": t["name"], "spalten": {b: z[b] for b in bed}, "datum_datei": max(daten, default=None)}
        return zeilen, andere, info
    finally:
        con.close()


# ---------------------------------------------------------------- Rechnung
def rechnen(zeilen: list[dict], andere: set, teile: list) -> tuple[dict, dict]:
    zaehl = {}
    unbekannt: set = set()
    zaehl["F0"] = len(zeilen)
    gesehen, f1 = set(), []
    for d in zeilen:
        schl = (d.get("transaktion"), d.get("lokal_id")) if d.get("lokal_id") not in (None, "") else None
        if schl is not None and schl in gesehen:
            continue
        if schl is not None:
            gesehen.add(schl)
        f1.append(d)
    zaehl["F1"] = len(f1)
    for d in f1:      # Codelisten einmal ganz lesen, damit jeder unbekannte Wert gemeldet wird
        d["_funktion"] = code(d.get("funktion"), FUNKTION, "Funktion des Lokals", unbekannt)
        d["_art"] = code(d.get("art_transaktion"), ART, "Art der Transaktion", unbekannt)
        d["_markt"] = code(d.get("markt"), MARKT, "Art des Marktes", unbekannt)
    if unbekannt:
        raise FormatFehler("unbekannte Codewerte (Protokoll erweitern): " + "; ".join(sorted(unbekannt)[:30]))
    f2 = [d for d in f1 if d["_funktion"] == "wohnung"]
    zaehl["F2"] = len(f2)
    f3 = [d for d in f2 if d["_art"] == "frei"]
    zaehl["F3"] = len(f3)
    f4 = [d for d in f3 if anteil_voll(d.get("anteil"))]
    zaehl["F4"] = len(f4)
    je_transaktion = defaultdict(int)       # Lokale aller Funktionen je Transaktion (nach F1)
    for d in f1:
        je_transaktion[d.get("transaktion")] += 1
    f5 = [d for d in f4 if d.get("transaktion") not in (None, "") and je_transaktion[d["transaktion"]] == 1]
    zaehl["F5"] = len(f5)
    f6, aus_lokal, aus_trans = [], 0, 0
    for d in f5:
        p = zahl(d.get("preis_lokal"))
        if p is not None and p > 0:
            d["_preis"] = p
            aus_lokal += 1
        else:
            p = zahl(d.get("preis_transaktion"))
            if p is None or p <= 0 or d["transaktion"] in andere:
                continue
            d["_preis"] = p
            aus_trans += 1
        f6.append(d)
    zaehl["F6"] = len(f6)
    f7 = [d for d in f6 if (zahl(d.get("flaeche")) or 0) > 0]
    zaehl["F7"] = len(f7)
    f8 = []
    for d in f7:
        fl = zahl(d["flaeche"])
        d["_m2"] = d["_preis"] / fl
        if FLAECHE[0] <= fl <= FLAECHE[1] and PREIS_JE_M2[0] <= d["_m2"] <= PREIS_JE_M2[1]:
            f8.append(d)
    zaehl["F8"] = len(f8)
    f9 = []
    for d in f8:
        d["_datum"] = datum(d.get("datum"))
        if d["_datum"] is not None:
            f9.append(d)
    zaehl["F9"] = len(f9)
    f10, ausserhalb = [], 0
    for d in f9:
        nr = None
        if d["lon"] is not None:
            treffer = [n for n, g in teile if g.contains(Point(d["lon"], d["lat"]))]
            nr = treffer[0] if len(treffer) == 1 else None
        if nr is None:
            ausserhalb += 1
            continue
        d["_nr"] = nr
        f10.append(d)
    zaehl["F10"] = len(f10)
    f11 = [d for d in f10 if d["_datum"].year >= ERSTES_JAHR]       # Änderung KR55: frühere Jahre nie veröffentlicht
    zaehl["F11"] = len(f11)
    ohne_markt = sum(1 for d in f11 if d["_markt"] is None)
    kontrolle = {"schritte": [{"nr": k, "schritt": s, "n": zaehl[k]} for k, s, _ in SCHRITTE],
                 "ausserhalb": ausserhalb, "ohne_markt": ohne_markt,
                 "preis_aus_lokal": aus_lokal, "preis_aus_transaktion": aus_trans}
    return {"zeilen": f11}, kontrolle


def runden(x: float) -> int:
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def wert(werte: list[float]) -> dict:
    n = len(werte)
    if n == 0:
        return {"median": None, "n": 0, "grund": "keine_transaktionen"}
    if n < MINDESTFALLZAHL:
        return {"median": None, "n": n, "grund": "n_unter_minimum"}
    return {"median": runden(statistics.median(werte)), "n": n}


def zusammenfassen(zeilen: list[dict], teile: list) -> tuple[list[int], dict, dict]:
    jahre = sorted({d["_datum"].year for d in zeilen})
    sammel = defaultdict(list)    # (nr|"stadt", jahr, markt) -> Preise je m²
    for d in zeilen:
        for ort in (d["_nr"], "stadt"):
            sammel[(ort, d["_datum"].year, "ogolem")].append(d["_m2"])
            if d["_markt"]:
                sammel[(ort, d["_datum"].year, d["_markt"])].append(d["_m2"])

    def reihe(ort):
        return {str(j): {m: wert(sammel.get((ort, j, m), [])) for m in MAERKTE} for j in jahre}
    return jahre, reihe("stadt"), {nr: reihe(nr) for nr, _ in teile}


# ---------------------------------------------------------------- Beispieldatei im erwarteten Format
def _gp_kopf(srs: int) -> bytes:
    return b"GP" + bytes([0, 0b00000001]) + struct.pack("<i", srs)   # Version 0, little endian, ohne Hülle


def beispiel_schreiben(ziel: Path, teile: list) -> None:
    """Erfundene Transaktionen im erwarteten GeoPackage-Format (metrisches System
    `rechen_srid` der Ortskonfiguration; die GUGiK-Datei bringt ihr eigenes mit, der Leser nimmt es aus der Datei), mit Fällen für jeden Filter.

    Fest eingebaut: dzielnica 07 hat 2024 genau 9 gültige Wohnungen (Median muss leer bleiben), dzielnica 08
    genau 10 (Median muss gesetzt sein). Alle Preise sind erfunden.
    """
    rnd = random.Random(SAAT)
    srs = RECHEN_SRID
    nach_metrisch = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(srs), always_xy=True)
    con = sqlite3.connect(ziel)
    con.executescript("""
      CREATE TABLE gpkg_spatial_ref_sys (srs_name TEXT, srs_id INTEGER PRIMARY KEY, organization TEXT,
        organization_coordsys_id INTEGER, definition TEXT, description TEXT);
      CREATE TABLE gpkg_contents (table_name TEXT PRIMARY KEY, data_type TEXT, identifier TEXT, description TEXT,
        last_change TEXT, min_x REAL, min_y REAL, max_x REAL, max_y REAL, srs_id INTEGER);
      CREATE TABLE gpkg_geometry_columns (table_name TEXT, column_name TEXT, geometry_type_name TEXT,
        srs_id INTEGER, z INTEGER, m INTEGER);
      CREATE TABLE rcn_lokale (fid INTEGER PRIMARY KEY, geom BLOB, oznaczenieTransakcji TEXT, rodzajTransakcji TEXT,
        rodzajRynku TEXT, udzialWPrawieDoNieruchomosci TEXT, dataSporzadzeniaDokumentu TEXT, idLokalu TEXT,
        funkcjaLokalu TEXT, polePowierzchniUzytkowejLokalu REAL, cenaLokaluBrutto REAL, cenaTransakcjiBrutto REAL);
      CREATE TABLE rcn_dzialki (fid INTEGER PRIMARY KEY, geom BLOB, oznaczenieTransakcji TEXT, cenaTransakcjiBrutto REAL);
    """)
    con.execute("INSERT INTO gpkg_spatial_ref_sys VALUES (?, ?, 'EPSG', ?, ?, '')",
                (srs_name(srs), srs, srs, CRS.from_epsg(srs).to_wkt()))
    for t in ("rcn_lokale", "rcn_dzialki"):
        con.execute("INSERT INTO gpkg_contents VALUES (?, 'features', ?, 'Beispieldaten', '2026-11-13', "
                    "NULL, NULL, NULL, NULL, ?)", (t, t, srs))
        con.execute("INSERT INTO gpkg_geometry_columns VALUES (?, 'geom', 'GEOMETRY', ?, 0, 0)", (t, srs))

    def punkt_in(g):
        x0, y0, x1, y1 = g.bounds
        while True:
            p = Point(rnd.uniform(x0, x1), rnd.uniform(y0, y1))
            if g.contains(p):
                return p

    def geom(lon, lat, flaeche_form: bool) -> bytes:
        x, y = nach_metrisch.transform(lon, lat)
        g = box(x - 6, y - 6, x + 6, y + 6) if flaeche_form else Point(x, y)
        return _gp_kopf(srs) + shapely.to_wkb(g, byte_order=1)

    nr_t = [0]

    def zeile(nr_geom, jahr, markt="wtórny", art="wolny rynek", funktion="lokal mieszkalny", anteil="1/1",
              flaeche=None, preis=None, preis_t=None, mit_lokalpreis=True, datum_txt=None, transaktion=None,
              lokal=None, lonlat=None):
        nr_t[0] += 1
        tr = transaktion or f"T/{nr_t[0]:06d}"
        g = dict(teile)[nr_geom] if nr_geom else None
        lon, lat = lonlat if lonlat else (punkt_in(g).coords[0])
        fl = flaeche if flaeche is not None else round(rnd.uniform(28, 95), 2)
        basis = 9000 + 500 * int(nr_geom or "09") + 900 * (jahr - 2021)
        pr = preis if preis is not None else round(fl * basis * rnd.lognormvariate(0, 0.18), -2)
        tag = datum_txt if datum_txt is not None else f"{jahr}-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}"
        if jahr == 2026 and datum_txt is None:
            tag = f"2026-{rnd.randint(1, 10):02d}-{rnd.randint(1, 28):02d}"
        con.execute("INSERT INTO rcn_lokale (geom, oznaczenieTransakcji, rodzajTransakcji, rodzajRynku, "
                    "udzialWPrawieDoNieruchomosci, dataSporzadzeniaDokumentu, idLokalu, funkcjaLokalu, "
                    "polePowierzchniUzytkowejLokalu, cenaLokaluBrutto, cenaTransakcjiBrutto) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (geom(lon, lat, nr_t[0] % 2 == 0), tr, art, markt, anteil, tag,
                     lokal or f"126101_1.0001.{nr_t[0]}_BUD.1_LOK", funktion, fl,
                     pr if mit_lokalpreis else None, preis_t if preis_t is not None else pr))
        return tr

    nrs = [nr for nr, _ in teile]
    for nr in nrs:
        for jahr in range(2021, 2027):
            if (nr, jahr) == ("07", 2024):
                n = 9
            elif (nr, jahr) == ("08", 2024):
                n = 10
            else:
                n = rnd.randint(4, 60)
            for i in range(n):
                markt = "" if i % 17 == 16 else ("pierwotny" if rnd.random() < 0.35 else "wtórny")
                zeile(nr, jahr, markt=markt)
    # Fälle, an denen je ein Filter greifen muss
    a = nrs[0]
    t = zeile(a, 2023)
    con.execute("INSERT INTO rcn_lokale (geom, oznaczenieTransakcji, rodzajTransakcji, rodzajRynku, "
                "udzialWPrawieDoNieruchomosci, dataSporzadzeniaDokumentu, idLokalu, funkcjaLokalu, "
                "polePowierzchniUzytkowejLokalu, cenaLokaluBrutto, cenaTransakcjiBrutto) "
                "SELECT geom, oznaczenieTransakcji, rodzajTransakcji, rodzajRynku, udzialWPrawieDoNieruchomosci, "
                "dataSporzadzeniaDokumentu, idLokalu, funkcjaLokalu, polePowierzchniUzytkowejLokalu, "
                "cenaLokaluBrutto, cenaTransakcjiBrutto FROM rcn_lokale WHERE oznaczenieTransakcji = ?", (t,))  # F1
    for _ in range(5):
        zeile(a, 2023, funktion="lokal użytkowy")                                   # F2
        zeile(a, 2023, art="sprzedaż bezprzetargowa")                              # F3
        zeile(a, 2023, anteil="1/2")                                                # F4
    for _ in range(3):                                                              # F5: Wohnung und Garage
        t = zeile(a, 2023)
        zeile(a, 2023, funktion="lokal garażowy", transaktion=t)
    zeile(a, 2023, mit_lokalpreis=False)                                            # F6: Preis aus Transaktion
    t = zeile(a, 2023, mit_lokalpreis=False)                                        # F6: mit Parzelle, raus
    con.execute("INSERT INTO rcn_dzialki (geom, oznaczenieTransakcji, cenaTransakcjiBrutto) VALUES (NULL, ?, 1)",
                (t,))
    zeile(a, 2023, mit_lokalpreis=False, preis_t=0)                                 # F6: kein Preis
    zeile(a, 2023, flaeche=0, preis=400000)                                         # F7
    zeile(a, 2023, flaeche=50, preis=1000)                                          # F8: 20 zł/m²
    zeile(a, 2023, datum_txt="")                                                    # F9
    zeile(None, 2023, lonlat=(19.40, 49.80))                                        # F10: außerhalb
    zeile(a, ERSTES_JAHR - 1)                                                       # F11: vor dem ersten Jahr
    con.commit()
    con.close()


# ---------------------------------------------------------------- Ausgabe
def js_text(obj: dict, fixture: bool) -> str:
    kopf = ("/* Wohnungsmarkt Kraków: Median Preis je m² Wohnfläche je dzielnica, Jahr und Markt. "
            + ("BEISPIELDATEN mit erfundenen Preisen, keine Aussage über Kraków. " if fixture else "")
            + "Źródło: " + QUELLE["vermerk"] + ". Podstawa: " + QUELLE["rechtsgrundlage"]
            + ". Przypisanie do dzielnic: granice © OpenStreetMap-Mitwirkende / autorzy OpenStreetMap, Open Database "
            "License (ODbL) 1.0 (https://www.openstreetmap.org/copyright); die Datei als Ganzes steht unter der ODbL 1.0. "
            "Erzeugt von skripte/40_mieszkania.py, Regeln pruefen/DW_protokoll.md. */\n")
    return kopf + "window.KIEZ_MIESZKANIA=" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n"


def beleg_text(obj: dict, info: dict) -> str:
    fx = obj.get("fixture") is True
    e, k = obj["eingabe"], obj["kontrolle"]
    z = []
    z.append("# Beleg Wohnungsmarkt (Paket Wohnungsmarkt): Zählungen je Schritt\n")
    z.append("Erzeugt von `skripte/40_mieszkania.py` im selben Lauf wie `daten/mieszkania_odbl.js`; nicht von Hand ändern. "
             "Regeln: `pruefen/DW_protokoll.md`. Prüfung: `pruefen/DW_mieszkania.py`.\n")
    if fx:
        z.append("**BEISPIELDATEN.** Die Eingabe ist eine erzeugte Datei im erwarteten Format mit erfundenen Preisen "
                 f"(Saat {e.get('saat')}); die Zahlen unten belegen nur, dass Leser, Filter, Mindestfallzahl und "
                 "Ausgabe arbeiten. Keine Aussage über Kraków.\n")
    z.append("## Eingabe\n")
    datei = f"`{e['datei']}`" if e["datei"] else f"nicht abgelegt (erzeugt mit `{e['erzeuger']}`)"
    z.append(f"- Art: `{e['art']}`; Datei: {datei}; SHA256: `{e['sha256'] or 'nicht festgehalten (Beispiel)'}`")
    z.append(f"- Tabelle der Lokale: `{info['tabelle']}`; Spalten: "
             + ", ".join(f"{b} = `{s}`" for b, s in info["spalten"].items()))
    z.append(f"- jüngstes Dokumentdatum der Datei (alle Tabellen, vor den Filtern; `datenstand`): {e['datenstand']}; "
             f"unvollständiges Jahr: {e['jahr_teilweise'] or 'keins'}")
    if not fx:     # Angabe des Geoportals beim Handdownload (eingang/HERKUNFT.md)
        z.append(f"- Geoportal nennt beim Handdownload vom 14.11.2026 (`eingang/HERKUNFT.md`) „Data ostatniej aktualizacji 2026-09-21“; die Datei enthält "
                 f"trotzdem Dokumente bis {e['datenstand']}. Der Unterschied ist nicht geklärt.")
    z.append(f"- Stadtteilgrenzen: {e['grenzen']}")
    z.append(f"- Stand der Auswertung: {obj['stand_auswertung']}\n")
    z.append("## Zählung je Schritt\n")
    z.append("| Nr | Schritt | Zeilen danach |")
    z.append("|---|---|---|")
    for s in k["schritte"]:
        z.append(f"| {s['nr']} | {SCHRITT_TEXT[s['schritt']]} | {s['n']} |")
    z.append("")
    z.append(f"- Preis aus dem Lokal: {k['preis_aus_lokal']}; Preis aus der Transaktion (ein Lokal, kein anderes Objekt): "
             f"{k['preis_aus_transaktion']}")
    z.append(f"- nach F9 keiner dzielnica zugeordnet: {k['ausserhalb']}")
    f10, f11 = (next(s["n"] for s in k["schritte"] if s["nr"] == nr) for nr in ("F10", "F11"))
    z.append(f"- vor {obj['regeln']['erstes_jahr']} nicht veröffentlicht (F11, KR55): {f10 - f11}")
    z.append(f"- ohne Angabe des Marktes (nur in `ogolem`): {k['ohne_markt']}\n")
    z.append("## Veröffentlichte Werte\n")
    zellen = [(nr, j, m, w) for nr, r in obj["stadtteile"].items() for j, mm in r.items() for m, w in mm.items()]
    mit = sum(1 for *_, w in zellen if w["median"] is not None)
    unter = sum(1 for *_, w in zellen if w.get("grund") == "n_unter_minimum")
    leer = sum(1 for *_, w in zellen if w.get("grund") == "keine_transaktionen")
    z.append(f"Mindestfallzahl {obj['regeln']['mindestfallzahl']}. Felder je dzielnica, Jahr und Markt: {len(zellen)}; "
             f"mit Median {mit}; leer wegen n < {obj['regeln']['mindestfallzahl']}: {unter}; ohne Transaktion: {leer}.\n")
    # Fallzahlen unter der Mindestzahl stehen nirgends (pruefen/N1_protokoll.md, Regel 4); die Abstimmung der Summe
    # gegen die letzte Zählung (F11) rechnet lauf() vor dem Unterdrücken und hält nur das Ergebnis fest
    z.append(f"Abstimmung: Summe n (`ogolem`) über alle dzielnice und Jahre gegen die Zählung nach F11, vor dem "
             f"Unterdrücken gerechnet: {'stimmt' if info['summe_stimmt'] else 'ABWEICHUNG'}.\n")
    z.append(f"Sekundäre Unterdrückung (Nachträge 2 bis 4), damit sich keine unterdrückte Fallzahl aus veröffentlichten "
             f"Summen zurückrechnen lässt: verdeckte Fallzahlen {info['verdeckt']} (Median bleibt).\n")
    z.append(f"Spannenprobe (`pruefen/DW_protokoll.md`, Änderung KR55): unterdrückte Fallzahlen, die im ganzen "
             f"veröffentlichten System höchstens zwei ganzzahlige Werte haben: {info['spanne_eng']} von "
             f"{info['primaer']}" + (" (offen, gemeldet)" if info["spanne_eng"] else "") + ".\n")

    def n_text(w):
        if w.get("grund") == "n_unter_minimum":
            return f"n < {obj['regeln']['mindestfallzahl']}"
        return "verdeckt" if w.get("n_verdeckt") else str(w["n"])
    z.append("| Jahr | n Stadt (ogolem) | Median Stadt ogolem (zł/m²) | n pierwotny | n wtórny |")
    z.append("|---|---|---|---|---|")
    for j, mm in obj["stadt"].items():
        med = mm["ogolem"]["median"]
        z.append(f"| {j} | {n_text(mm['ogolem'])} | {med if med is not None else '–'} | {n_text(mm['pierwotny'])} | "
                 f"{n_text(mm['wtorny'])} |")
    z.append("")
    z.append("## Grenzen\n")
    z.append("- Kaufverträge, keine Angebote und keine Mieten. Brutto wie im Register (Erstverkauf meist mit "
             "Umsatzsteuer).")
    z.append("- Vollständigkeit des Registers für Kraków und Richtigkeit der Geometrie: nicht geprüft.")
    if not fx:     # Jahresgrenzen aus den Zählungen dieses Laufs (pruefen/DW_protokoll.md, Hinweise 14.11.2026)
        anteil = "; ".join(f"{j}: {n} von {g} ({math.floor(1000 * n / g) / 10:.1f} %)".replace(".", ",")
                           for j, (n, g) in sorted(info["anteil_lage"].items()))
        gf = info["geometrie_fehlt"]
        gf_text = ("kein veröffentlichtes Jahr" if not gf else f"{gf[0]} bis {gf[-1]}"
                   if gf == list(range(gf[0], gf[-1] + 1)) else ", ".join(map(str, gf)))
        z.append(f"- **Werte der ganzen Stadt erst ab {info['voll_ab'] or 'keinem Jahr'} weitgehend vollständig** "
                 "(ab da in jedem Jahr mindestens 90 % der Käufe mit Datum auch mit Lage): Anteil der Käufe mit Lage "
                 "(nach F10) an den Käufen mit Datum (nach F9) je Jahr mit veröffentlichter Stadtzahl (Anteil "
                 f"abgerundet): {anteil}. **Werte je dzielnica erst ab {info['voll_ab'] or 'keinem Jahr'}, davor "
                 f"nur zum Teil:** In den veröffentlichten Jahren {gf_text} fehlt mehr als der Hälfte der Zeilen "
                 f"nach F9 die Geometrie, F10 schließt sie aus (nach F9 ohne Geometrie {info['ohne_geometrie']} "
                 f"Zeilen über alle Jahre, mit Geometrie außerhalb der dzielnice "
                 f"{k['ausserhalb'] - info['ohne_geometrie']}). Bis {info['anteil_fehlt_bis']} fehlt in der Datei "
                 "außerdem den meisten Zeilen der Anteil am Recht, F4 schließt sie aus. Jahre vor "
                 f"{obj['regeln']['erstes_jahr']} sind nicht veröffentlicht (F11, KR55).")
    z.append("- Zuordnung zur dzielnica über `daten/stadtteile_odbl.js`; Lizenzfolge für abgeleitete Werte offen "
             "(docs/entscheidungen.md, KR3).")
    z.append("- Keine Extremwerte, keine Perzentile, keine Einzelfälle veröffentlicht (Datenschutz).")
    return "\n".join(z) + "\n"


def lauf(beispiel: bool, stand: str, saat: int = SAAT) -> tuple[str, str, dict]:
    teile = stadtteile_laden()
    grenzen = f"daten/stadtteile_odbl.js (SHA256 {sha256(STADTTEILE)}, {len(teile)} dzielnice)"
    with tempfile.TemporaryDirectory(prefix="kiez_dw_") as tmp:
        if beispiel:
            gpkg = Path(tmp) / "rcn_1261_beispiel.gpkg"
            beispiel_schreiben(gpkg, teile)
            datei, sha = None, None    # erzeugt mit --beispiel, nicht abgelegt
        else:
            gpkg = eingabe_finden()
            datei, sha = f"eingang/rcn/{gpkg.name}", sha256(gpkg)
        zeilen, andere, info = lesen(gpkg)
    erg, kontrolle = rechnen(zeilen, andere, teile)
    info["ohne_geometrie"] = sum(1 for d in zeilen if d.get("_datum") is not None and d["lon"] is None)  # nur Beleg
    jahre, stadt, stadtteile = zusammenfassen(erg["zeilen"], teile)
    info["summe_stimmt"] = (sum(w["n"] for r in stadtteile.values() for mm in r.values() for m, w in mm.items()
                                if m == "ogolem") == kontrolle["schritte"][-1]["n"])
    for mm_alle in [stadt, *stadtteile.values()]:      # Regel 4: Fallzahl unter der Mindestzahl nie veröffentlichen
        for mm in mm_alle.values():
            for w in mm.values():
                if w.get("grund") == "n_unter_minimum":
                    w["n"] = None
    info["verdeckt"] = verdecken(stadt, stadtteile, kontrolle)
    info["primaer"], info["spanne_eng"] = spannen_eng(stadt, stadtteile, kontrolle)
    # nur Beleg: Anteil der Käufe mit Lage (nach F10) an denen nach F9, nur in Jahren mit veröffentlichter Stadtzahl
    f9_jahr = Counter(d["_datum"].year for d in zeilen if d.get("_datum") is not None)
    info["anteil_lage"] = {j: (stadt[str(j)]["ogolem"]["n"], f9_jahr[j]) for j in jahre
                           if stadt[str(j)]["ogolem"]["n"] is not None and f9_jahr[j]}
    # nur Beleg, aus den Zählungen statt fest geschrieben (Punkt 4 vom 14.11.2026): erstes Jahr, ab dem jedes Jahr
    # mindestens 90 % Käufe mit Lage hat; veröffentlichte Jahre, in denen mehr als der Hälfte die Geometrie fehlt;
    # letztes Jahr, in dem nach F3 mehr als der Hälfte der Anteil am Recht fehlt
    ok = [j for j, (n, g) in sorted(info["anteil_lage"].items()) if 10 * n >= 9 * g]
    info["voll_ab"] = next((j for j in ok if all(x in ok for x in info["anteil_lage"] if x >= j)), None)
    ohne_geo = Counter(d["_datum"].year for d in zeilen if d.get("_datum") is not None and d["lon"] is None)
    info["geometrie_fehlt"] = [j for j in jahre if 2 * ohne_geo[j] > f9_jahr[j] > 0]
    f3_jahr, ohne_anteil = Counter(), Counter()
    for d in zeilen:
        if d.get("_funktion") == "wohnung" and d.get("_art") == "frei" and (x := datum(d.get("datum"))) is not None:
            f3_jahr[x.year] += 1
            ohne_anteil[x.year] += not str(d.get("anteil") or "").strip()
    info["anteil_fehlt_bis"] = max((j for j in f3_jahr if 2 * ohne_anteil[j] > f3_jahr[j]), default=None)
    juengst = info["datum_datei"]     # jüngstes Dokumentdatum der Datei (pruefen/DW_protokoll.md, Ausgabe)
    teilweise = juengst.year if juengst and (juengst.month, juengst.day) != (12, 31) else None
    obj = {}
    if beispiel:
        obj["fixture"] = True
    obj |= {
        "stand_auswertung": stand,
        "quelle": QUELLE,
        "eingabe": {"art": "beispiel" if beispiel else "rcn_gpkg", "datei": datei, "sha256": sha,
                    "erzeuger": "skripte/40_mieszkania.py --beispiel" if beispiel else None,
                    "datenstand": juengst.isoformat() if juengst else None, "jahr_teilweise": teilweise,
                    "grenzen": grenzen} | ({"saat": saat} if beispiel else {}),
        "regeln": {"mindestfallzahl": MINDESTFALLZAHL, "kennzahl": "median_preis_je_m2_brutto",
                   "protokoll": "pruefen/DW_protokoll.md", "flaeche_m2": list(FLAECHE),
                   "preis_je_m2": list(PREIS_JE_M2), "erstes_jahr": ERSTES_JAHR},
        "jahre": jahre,
        "maerkte": list(MAERKTE),
        "einheit": "zl_m2",
        "stadt": stadt,
        "stadtteile": stadtteile,
        "kontrolle": kontrolle,
    }
    return js_text(obj, beispiel), beleg_text(obj, info), obj


def _system(stadt: dict, stadtteile: dict, kontrolle: dict):
    """Veröffentlichtes Gleichungssystem (pruefen/N1_protokoll.md, Nachtrag 3): Variablen, Gleichungen, Schranken.

    Variablen: Fallzahl je Ort (dzielnica oder Stadt), Jahr und Markt, dazu je Ort und Jahr die nie veröffentlichte
    Zahl der Käufe ohne Marktangabe. Rückgabe: (index, A, b, schranken); index bildet (ort, jahr, markt) auf die
    Spalte ab, markt "o" = ohne Marktangabe."""
    import numpy as np
    orte = [("stadt", stadt), *sorted(stadtteile.items())]
    jahre = list(stadt)
    index: dict[tuple, int] = {}
    for ort, r in orte:
        for j in jahre:
            for m in (*MAERKTE, "o"):
                index[(ort, j, m)] = len(index)
    zeilen, rechts = [], []

    def gleichung(terme: dict, wert: int) -> None:
        z = np.zeros(len(index))
        for k, c in terme.items():
            z[index[k]] += c
        zeilen.append(z)
        rechts.append(wert)
    for j in jahre:
        for m in (*MAERKTE, "o"):
            gleichung({("stadt", j, m): 1, **{(nr, j, m): -1 for nr, _ in orte[1:]}}, 0)
        for ort, _ in orte:
            gleichung({(ort, j, "ogolem"): 1, (ort, j, "pierwotny"): -1, (ort, j, "wtorny"): -1, (ort, j, "o"): -1}, 0)
    letzte = kontrolle["schritte"][-1]["n"]      # Summe über die Jahre = letzte Zählung (F11 seit KR55)
    gleichung({("stadt", j, "ogolem"): 1 for j in jahre}, letzte)
    gleichung({(nr, j, "o"): 1 for nr, _ in orte[1:] for j in jahre}, kontrolle["ohne_markt"])
    schranken = []
    for (ort, j, m), _ in sorted(index.items(), key=lambda kv: kv[1]):
        if m == "o":
            schranken.append((0, None))
            continue
        w = dict(orte)[ort][j][m]
        if w.get("n") is not None:
            schranken.append((w["n"], w["n"]))
        elif w.get("grund") == "n_unter_minimum":
            schranken.append((1, MINDESTFALLZAHL - 1))
        else:                                  # verdeckt: Median gezeigt, also mindestens die Mindestzahl
            schranken.append((MINDESTFALLZAHL, None))
    return index, np.array(zeilen), np.array(rechts, dtype=float), schranken


def _spanne(A, b, schranken, spalte: int) -> tuple[int, int]:
    """Kleinster und größter ganzzahliger Wert einer Spalte im System (HiGHS über scipy.optimize.milp)."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    lo = np.array([s[0] for s in schranken], dtype=float)
    hi = np.array([np.inf if s[1] is None else s[1] for s in schranken], dtype=float)
    werte = []
    for vorzeichen in (1, -1):
        c = np.zeros(len(schranken))
        c[spalte] = vorzeichen
        r = milp(c, constraints=LinearConstraint(A, b, b), bounds=Bounds(lo, hi), integrality=np.ones(len(schranken)))
        if r.status != 0:
            raise FormatFehler(f"veröffentlichte Fallzahlen widersprechen sich (milp: {r.message})")
        werte.append(round(vorzeichen * r.fun))
    return werte[0], werte[1]


def spannen_eng(stadt: dict, stadtteile: dict, kontrolle: dict) -> tuple[int, int]:
    """Spannenprobe (pruefen/DW_protokoll.md, Änderung KR55): Zahl der unterdrückten Fallzahlen und Zahl derer, die
    im veröffentlichten System höchstens zwei ganzzahlige Werte haben. Nur Zählungen, keine Werte."""
    orte = {"stadt": stadt, **stadtteile}
    index, A, b, schranken = _system(stadt, stadtteile, kontrolle)
    primaer = [k for k in index if k[2] != "o" and orte[k[0]][k[1]][k[2]].get("grund") == "n_unter_minimum"]
    eng = 0
    for k in primaer:
        lo, hi = _spanne(A, b, schranken, index[k])
        eng += hi - lo + 1 <= 2
    return len(primaer), eng


def verdecken(stadt: dict, stadtteile: dict, kontrolle: dict) -> int:
    """Sekundäre Unterdrückung (pruefen/N1_protokoll.md, Nachtrag 2 und 3): solange eine unterdrückte Fallzahl im
    ganzen veröffentlichten System (Stadt = Summe der dzielnice, ogolem = pierwotny + wtorny + ohne Marktangabe,
    Summe über die Jahre = letzte Zählung (F11), Summe ohne Marktangabe = kontrolle.ohne_markt, Schranken) genau einen
    zulässigen Wert hat, wird eine weitere Fallzahl verdeckt (n null, n_verdeckt true; der Median bleibt).
    Reihenfolge der Kandidaten: gleiches Jahr und gleicher Markt, dann gleiches Jahr, dann alle übrigen; je Stufe die
    kleinste Fallzahl, bei Gleichstand nach Ort, Jahr und Markt; reicht keine einzelne Zelle, mehrere (Nachtrag 4).
    Rückgabe: Zahl der verdeckten Felder."""
    orte = {"stadt": stadt, **stadtteile}
    n_verdeckt = 0
    while True:
        index, A, b, schranken = _system(stadt, stadtteile, kontrolle)
        primaer = sorted(k for k in index if k[2] != "o" and orte[k[0]][k[1]][k[2]].get("grund") == "n_unter_minimum")
        offen = next((k for k in primaer if len(set(_spanne(A, b, schranken, index[k]))) == 1), None)
        if offen is None:
            return n_verdeckt
        _, j0, m0 = offen
        kand = sorted((k for k in index if k[2] != "o" and orte[k[0]][k[1]][k[2]].get("n")),
                      key=lambda k: (0 if (k[1], k[2]) == (j0, m0) else 1 if k[1] == j0 else 2,
                                     orte[k[0]][k[1]][k[2]]["n"], k))
        for k in kand:
            w = orte[k[0]][k[1]][k[2]]
            alt = w["n"]
            w["n"], w["n_verdeckt"] = None, True
            index, A, b, schranken = _system(stadt, stadtteile, kontrolle)
            lo, hi = _spanne(A, b, schranken, index[offen])
            if lo != hi:
                n_verdeckt += 1
                break
            w["n"] = alt
            del w["n_verdeckt"]
        else:
            n_verdeckt += _mehrere_verdecken(orte, stadt, stadtteile, kontrolle, offen, kand)


def _unbestimmt(stadt: dict, stadtteile: dict, kontrolle: dict, offen: tuple) -> bool:
    index, A, b, schranken = _system(stadt, stadtteile, kontrolle)
    lo, hi = _spanne(A, b, schranken, index[offen])
    return lo != hi


def _mehrere_verdecken(orte: dict, stadt: dict, stadtteile: dict, kontrolle: dict, offen: tuple, kand: list) -> int:
    """Nachtrag 4 (pruefen/N1_protokoll.md): reicht keine einzelne Zelle, Kandidaten in derselben Reihenfolge
    nacheinander verdecken, bis `offen` unbestimmt ist; dann in umgekehrter Reihenfolge jede wieder veröffentlichen,
    ohne die `offen` unbestimmt bleibt. Rückgabe: Zahl der verdeckt gebliebenen Felder."""
    dazu: list[tuple[tuple, int]] = []
    for k in kand:
        w = orte[k[0]][k[1]][k[2]]
        dazu.append((k, w["n"]))
        w["n"], w["n_verdeckt"] = None, True
        if _unbestimmt(stadt, stadtteile, kontrolle, offen):
            break
    else:
        raise FormatFehler(f"{offen}: auch die Verdeckung aller Kandidaten macht die Fallzahl nicht unbestimmt")
    for k, alt in reversed(dazu):
        w = orte[k[0]][k[1]][k[2]]
        w["n"] = alt
        del w["n_verdeckt"]
        if not _unbestimmt(stadt, stadtteile, kontrolle, offen):
            w["n"], w["n_verdeckt"] = None, True
    return sum(1 for k, _ in dazu if orte[k[0]][k[1]][k[2]].get("n_verdeckt"))


def eingabe_finden() -> Path:
    ordner = daten_ordner() / "eingang" / "rcn"
    dateien = sorted(ordner.glob("*.gpkg")) if ordner.is_dir() else []
    if len(dateien) != 1:
        raise FileNotFoundError(f"{ordner}: {len(dateien)} GeoPackage-Dateien gefunden, erwartet genau eine "
                                f"(Handdownload, siehe quellen-DW.md); ohne echte Daten: --beispiel")
    return dateien[0]


def spalten_zeigen() -> None:
    gpkg = eingabe_finden()
    con = sqlite3.connect(f"file:{gpkg}?mode=ro", uri=True)
    for t in tabellen(con):
        print(f"{t['name']} (Geometrie {t['geom']}, srs {t['srs']}): {', '.join(t['spalten'])}")
        z = zuordnen(t["spalten"])
        print("  zugeordnet: " + ", ".join(f"{b}={s}" for b, s in z.items() if s))
    con.close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--beispiel", action="store_true")
    g.add_argument("--pruefen", action="store_true")
    g.add_argument("--spalten", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.spalten:
            spalten_zeigen()
            return 0
        if a.pruefen:
            alt = js_lesen(AUSGABE)
            beispiel = alt["eingabe"]["art"] == "beispiel"
            if not beispiel:
                gpkg = eingabe_finden()
                if sha256(gpkg) != alt["eingabe"]["sha256"]:
                    print(f"Eingabe {gpkg.name} hat einen anderen SHA256 als daten/mieszkania_odbl.js; neu rechnen")
                    return 1
            js, md, _ = lauf(beispiel, alt["stand_auswertung"], alt["eingabe"].get("saat", SAAT))
            ok_js = js == AUSGABE.read_text(encoding="utf-8")
            ok_md = BELEG.is_file() and md == BELEG.read_text(encoding="utf-8")
            print(("  ok    " if ok_js else "  FEHLT ") + "daten/mieszkania_odbl.js byte-gleich neu erzeugt"
                  + ("" if ok_js else " (Stadtteilgrenzen geändert? dann neu erzeugen)"))
            print(("  ok    " if ok_md else "  FEHLT ") + "belege/DW_mieszkania.md byte-gleich neu erzeugt")
            return 0 if ok_js and ok_md else 1
        js, md, obj = lauf(a.beispiel, date.today().isoformat())
    except FileNotFoundError as e:
        print(f"Eingabe fehlt: {e}", file=sys.stderr)
        return 3
    except FormatFehler as e:
        print(f"Eingabe passt nicht zum erwarteten Format: {e}", file=sys.stderr)
        return 4
    AUSGABE.write_text(js, encoding="utf-8")
    BELEG.write_text(md, encoding="utf-8")
    k = obj["kontrolle"]
    print(" -> ".join(f"{s['nr']} {s['n']}" for s in k["schritte"]))
    print(f"geschrieben: {AUSGABE.relative_to(WURZEL)} ({len(js)} Zeichen), {BELEG.relative_to(WURZEL)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
