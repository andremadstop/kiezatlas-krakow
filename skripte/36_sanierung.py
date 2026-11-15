"""Sanierungsatlas Wohnungsbestand: ZBK-Gebäudeliste, Verortung, Verknüpfung mit BDOT10k/LoD2, Typologie-Schätzung.

Liest nur Dateien (kein Netz, keine Datenbank):
  ZBK-Liste      $KIEZ_DATEN/zbk/2026-11-13/zbk_wykaz_2025-12.pdf  („Wykaz budynków i obiektów w zarządzie ZBK na
                 dzień 2025-12-01“, BIP des ZBK, Anhang 635620) und bip_dok48482_ponowne.html (Regeln der
                 Weiterverwendung, daraus wörtlich die Haftungsklausel). PDF-Text über pdftotext (Poppler).
  BDOT10k 1261   $KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip (Gebäude, Stadt, Delegaturen; Leser aus
                 skripte/dz_denkmale.py, nur gelesen)
  LoD2 2017      $KIEZ_DATEN/eingang/lod2_1261*.zip (Leser skripte/20_lod.py, nur gelesen)
  OSM            $KIEZ_DATEN/eingang/*.osm.pbf (Adressen, heritage; Grenzen der dzielnice über
                 skripte/raum_bevoelkerung.py, nur gelesen)
Schreibt:
  daten/sanierung.js        window.KIEZ_SANIERUNG       Zählungen aus der Liste, Typologie je Delegatura (ohne OSM)
  daten/sanierung_odbl.js   window.KIEZ_SANIERUNG_ODBL  Verortung, Verknüpfung, Punkte, Typologie je dzielnica (ODbL)
  belege/DS_sanierung_lauf.md   Zählungen je Schritt, nicht verortete Einträge, Gegenprobe, Stichprobe
  $KIEZ_DATEN/abgeleitet/sanierung/zbk_tabelle.tsv   gelesene Tabelle mit Rohtext (nur außerhalb des Repos)

Regeln: pruefen/DS_protokoll.md (vor dem ersten Lauf festgelegt). Keine Adresse, keine L.p., keine Gebäudekennung
in daten/; Punkte nur für Einträge ohne Anteil von Privatpersonen; die Typologie ist eine Schätzung.

Aufruf: python -I skripte/36_sanierung.py [--pruefen]
  --pruefen  rechnet alles neu und vergleicht byte-genau mit den Dateien im Repo, schreibt nichts.
Rückgabe 0 = geschrieben bzw. gleich, 1 = Abweichung oder Befund beim Lesen, 2 = Eingang fehlt.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import math
import os
import platform
import random
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from pyproj import CRS, Transformer
from shapely.geometry import Point, Polygon
from shapely.prepared import prep
from shapely.strtree import STRtree

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402

ZBK_REL = "zbk/2026-11-13/zbk_wykaz_2025-12.pdf"
ZBK_REGELN_REL = "zbk/2026-11-13/bip_dok48482_ponowne.html"
ZBK_URL = "https://www.bip.krakow.pl/?bip_id=32&mmi=10127"
ZBK_PLIK = "https://www.bip.krakow.pl/plik.php?zid=635620&wer=1&new=t&mode=shw"
ZBK_TITEL = "Wykaz budynków i obiektów w zarządzie ZBK na dzień 2025-12-01"
ZBK_STAND = "2025-12-01"
ABRUF = "2026-11-13"
FUTURHIST_URL = "https://futurhist.eu/demonstrators/krakow/"
ZBK_QUELLE = ("Źródło: Zarząd Budynków Komunalnych w Krakowie, „Wykaz budynków i obiektów w zarządzie ZBK na dzień "
              "2025-12-01”, Biuletyn Informacji Publicznej (https://www.bip.krakow.pl/?bip_id=32&mmi=10127), "
              "załącznik nr 635620 z dnia 2025-12-18; data wytworzenia: 2025-12-18 (plik PDF), data pozyskania: 2026-11-13. ")
# Hinweis auf die Verarbeitung je Datei (Zasady ponownego wykorzystywania, II): die Zählungen enthalten keine
# Adressen; die Punkte geben die Lage der Adresse wieder und beruhen auf Geokodierung und Verknüpfung.
VERMERK_ZBK = (ZBK_QUELLE + "Informacja przetworzona: odczyt tabeli z PDF, ujednolicenie rodzaju budynku i "
               "własności, zliczenia; plik nie zawiera adresów.")
VERMERK_ZBK_ODBL = (ZBK_QUELLE + "Informacja przetworzona: odczyt tabeli z PDF, ujednolicenie rodzaju budynku i "
                    "własności, geokodowanie adresów (OpenStreetMap), powiązanie z budynkami BDOT10k i modelami LoD2, "
                    "zliczenia; punkty wskazują położenie budynku (adres nie jest podany jako tekst), bez budynków "
                    "jednorodzinnych.")
VERMERK_LOD2 = ("„Modele 3D budynków są dostępne bezpłatnie i możliwe do dowolnego wykorzystania.” "
                "(https://www.geoportal.gov.pl/pl/dane/inne-dane/modele-3d-budynkow/). Źródło: Główny Urząd "
                "Geodezji i Kartografii, Modele 3D budynków LoD2, powiat 1261, stan 2017, pobrano 2026-11-13; "
                "wysokość przetworzona (najwyższy minus najniższy punkt bryły).")
VERMERK_OSM = "© OpenStreetMap-Mitwirkende, ODbL 1.0 (https://www.openstreetmap.org/copyright)"
VERMERK_OSM_SPRACHEN = {"pl": "© współtwórcy OpenStreetMap, ODbL 1.0 (https://www.openstreetmap.org/copyright)",
                        "en": "© OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright)",
                        "de": VERMERK_OSM}
# Datenschutz: kein Punkt an Einfamilienhäusern laut BDOT10k (die Lieferung 1261 hat keine eigene Klasse für zwei
# Wohnungen) und keiner für Wohnnutzung (Art enthält M) ohne bekannte Gebäudefunktion; sie bleiben Zählung je
# dzielnica (docs/entscheidungen/DS.md, Nr. 3)
KLEINHAUS = ("budynek jednorodzinny",)
LITERATUR = {"autoren": "Barnaś, Jeleński, Nowak-Ocłoń, Racoń-Leja", "weitere_autoren": True, "zeitschrift": "Energy", "band": 263,
             "jahr": 2023, "artikel": "125774", "doi": "10.1016/j.energy.2022.125774"}

# Spalten nach x in pt (pruefen/DS_protokoll.md, „Lesen der PDF-Tabelle“)
SPALTEN = [("lp", 0, 36), ("name", 36, 205), ("vorsatz", 205, 234), ("nr", 234, 316), ("ort", 316, 361),
           ("rodzaj", 361, 403), ("wlasnosc", 403, 488), ("samoistne", 488, 528), ("dzielnica", 528, 10_000)]
KOPF = {"L.p.": 19.56, "ADRES": 163.94, "Miejscowość": 317.59, "Rodzaj": 363.07, "Własność": 428.86,
        "Dzielnica": 539.76}
KOPF_TOLERANZ = 2.0
ZEILENABSTAND_MAX = 4.0       # Abstand zweier Textzeilen derselben Zelle
LEERE_ZEILE_KOSTEN = 3.0
MITTE_TOLERANZ = 6.0
ROEMISCH = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI",
            "XVII", "XVIII"]
ART_REIHE = "MUP"
EIG_PUNKTE = ("gmina", "skarb_panstwa", "publiczne_mieszane")
EIG_KLASSEN = ("gmina", "skarb_panstwa", "publiczne_mieszane", "z_prywatnymi", "prywatne", "brak")
PUNKT_STREUUNG_M = 50.0
UMRISS_ANTEIL = 0.5
GESCHOSS_M = 3.0
PUNKT_GESCHOSSE_MIN = 3   # Punkte nur an Gebäuden mit mindestens 3 Geschossen laut BDOT10k (DS_protokoll.md, Nachtrag 4)
# Typologie (Schätzung)
TYP = {"geschosse_min": 4, "flaeche_min_m2": 250, "rechteckigkeit_min": 0.85, "umkreis_m": 150, "nachbarn_min": 9}
# Angebaut (Hinweis, keine Regel; DS_protokoll.md, Nachtrag 5): gemeinsame Grenze mit anderen BDOT10k-Gebäuden, gemessen
# als Länge des Umrisses innerhalb von ANGEBAUT_TOL_M um die Nachbarn; ab ANGEBAUT_MIN_M gilt der Kandidat als angebaut
# (Blockrandbebauung, typisch für kamienice, untypisch für freistehende Blöcke)
ANGEBAUT_TOL_M = 0.5
ANGEBAUT_MIN_M = 3.0
MFH = "budynek wielorodzinny"
STICHPROBE = {"osiedle": 30, "kein_kandidat": 10}
STARTWERT = 20261113
VERORTUNG_KLASSEN = ("verortet", "beschreibung", "poza_krakowem", "ulica_nie_znaleziona", "numer_nie_znaleziony",
                     "mehrdeutig_ulica", "mehrdeutig_punkt", "abweichung_dzielnica")
KLEINES_N = 100                # darunter Quoten ohne Nachkommastelle (Nachtrag 2)


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")


def modul(name: str, datei: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / "skripte" / datei)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def wilson(k: int, n: int, z: float = 1.959964) -> list[float] | None:
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    m = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    st = 1 if n >= KLEINES_N else None
    return [round(100 * (m - h), st), round(100 * (m + h), st)]


def anteil(k: int, n: int) -> float | int | None:
    return (round(100 * k / n, 1) if n >= KLEINES_N else round(100 * k / n)) if n else None


def dez(x) -> str:
    """Zahl für den deutschen Beleg: Tausenderpunkt, Dezimalkomma; Intervall als „a–b“."""
    if x is None:
        return "–"
    if isinstance(x, list):
        return "–".join(dez(v) for v in x)
    if isinstance(x, int):
        return f"{x:,}".replace(",", ".")
    return str(x).replace(".", ",")


# ------------------------------------------------------------------------------------- PDF lesen
def pdftotext(args: list[str]) -> str:
    return subprocess.run(["pdftotext", *args], check=True, capture_output=True).stdout.decode("utf-8")


def poppler_version() -> str:
    r = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True)
    m = re.search(r"pdftotext version (\S+)", r.stderr + r.stdout)
    return m.group(1) if m else "unbekannt"


def spalte(x: float) -> str:
    return next(n for n, a, b in SPALTEN if a <= x < b)


def zellen_zuordnen(zeilen: list[tuple[float, float, list]], lps: list[tuple[str, float]]):
    """Gruppen zusammenhängender Textzeilen je L.p.; Rückgabe [(von, bis, lp_index, abstand)]."""
    n, m = len(zeilen), len(lps)
    inf = float("inf")
    # best[i][j]: Kosten für Zeilen i.. ab L.p. j; dynamische Programmierung von hinten
    best = [[(inf, None)] * (m + 1) for _ in range(n + 1)]
    for j in range(m + 1):
        best[n][j] = (0.0, None)
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            kosten, wahl = best[i][j + 1][0] + LEERE_ZEILE_KOSTEN, None
            for k in range(i + 1, n + 1):
                if k - 1 > i and zeilen[k - 1][0] - zeilen[k - 2][1] > ZEILENABSTAND_MAX:
                    break
                mitte = (zeilen[i][0] + zeilen[k - 1][1]) / 2
                d = abs(mitte - lps[j][1])
                c = d + best[k][j + 1][0]
                if c < kosten:
                    kosten, wahl = c, (k, d)
            best[i][j] = (kosten, wahl)
    gruppen, i, j = [], 0, 0
    while i < n:
        if j >= m:
            raise ValueError("Textzeilen ohne L.p.")
        wahl = best[i][j][1]
        if wahl is None:
            j += 1
            continue
        k, d = wahl
        gruppen.append((i, k, j, d))
        i, j = k, j + 1
    return gruppen


def tabelle_lesen(pdf: Path) -> tuple[list[dict], dict]:
    """Einträge der Liste und Zählungen des Lesens (Pflichtprüfungen siehe Protokoll)."""
    bbox = pdftotext(["-bbox", str(pdf), "-"])
    seiten = re.split(r"<page ", bbox)[1:]
    eintraege: list[dict] = []
    z: dict = {"seiten": len(seiten), "je_seite": [], "max_abstand_pt": 0.0, "befunde": []}
    wort = re.compile(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)<')
    for nr, s in enumerate(seiten, 1):
        w = [(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in wort.findall(s)]
        if not w:
            continue
        for k, x in KOPF.items():
            treffer = [q[0] for q in w if q[4] == k and q[1] < 200]
            if not treffer or abs(treffer[0] - x) > KOPF_TOLERANZ:
                raise ValueError(f"Seite {nr}: Kopfwort {k} fehlt oder liegt anders ({treffer[:1]} statt {x})")
        # Kopf der Spalte Rodzaj: zusammenhängende Zeilen ab dem Wort „Rodzaj“ (Abstand höchstens 4 pt)
        rz = sorted((q for q in w if 361 <= q[0] < 403), key=lambda q: q[1])
        i0 = next(i for i, q in enumerate(rz) if q[4] == "Rodzaj")
        kopf_ende = rz[i0][3]
        for q in rz[i0 + 1:]:
            if q[1] - kopf_ende > ZEILENABSTAND_MAX:
                break
            kopf_ende = max(kopf_ende, q[3])
        fuss = [q for q in w if q[4] == "Strona"]
        fuss_y = min(q[1] for q in fuss) if fuss else 10_000
        daten = [q for q in w if kopf_ende < q[1] < fuss_y - 1]
        lps = sorted(((q[4], (q[1] + q[3]) / 2) for q in daten if spalte(q[0]) == "lp"), key=lambda t: t[1])
        if any(not re.fullmatch(r"\d+", t) for t, _ in lps):
            raise ValueError(f"Seite {nr}: Text in der Spalte L.p.: {[t for t, _ in lps]}")
        zeilen_je = {int(t): {"seite": nr, "lp": int(t)} for t, _ in lps}
        je_spalte: dict[str, list] = {}
        for q in daten:
            c = spalte(q[0])
            if c != "lp":
                je_spalte.setdefault(c, []).append(q)
        for c, ws in sorted(je_spalte.items()):
            ws.sort(key=lambda q: (q[1], q[0]))
            zeilen: list[list] = []          # [yMin, yMax, wörter]
            for q in ws:
                if zeilen and abs(zeilen[-1][0] - q[1]) < 2:
                    zeilen[-1][2].append(q)
                    zeilen[-1][1] = max(zeilen[-1][1], q[3])
                else:
                    zeilen.append([q[1], q[3], [q]])
            for i, k, j, d in zellen_zuordnen(zeilen, lps):
                text = " ".join(" ".join(q[4] for q in sorted(zeilen[x][2], key=lambda q: q[0])) for x in range(i, k))
                z["max_abstand_pt"] = max(z["max_abstand_pt"], round(d, 1))
                if d > MITTE_TOLERANZ:
                    z["befunde"].append(f"Seite {nr}, Spalte {c}, L.p. {lps[j][0]}: Abstand {d:.1f} pt")
                zeilen_je[int(lps[j][0])][c] = text
        z["je_seite"].append(len(lps))
        eintraege.extend(zeilen_je[k] for k in sorted(zeilen_je))
    # zweiter Leseweg: Zeilen mit L.p. am Zeilenanfang in pdftotext -layout
    layout = pdftotext(["-layout", str(pdf), "-"]).split("\f")
    zweit = [[int(m.group(1)) for l in p.splitlines() for m in [re.match(r"^\s{0,2}(\d{1,3})\s+\S", l)] if m]
             for p in layout][:len(seiten)]
    z["zweiter_leseweg_je_seite"] = [len(x) for x in zweit]
    z["zweiter_leseweg_gleich"] = z["zweiter_leseweg_je_seite"] == z["je_seite"] and \
        [n for p in zweit for n in p] == [e["lp"] for e in eintraege]
    titel = re.sub(r"\s+", " ", layout[0]).strip()
    z["titel_gefunden"] = ZBK_TITEL in titel
    lp = [e["lp"] for e in eintraege]
    z["lp_lueckenlos"] = lp == list(range(1, len(lp) + 1))
    return eintraege, z


# ------------------------------------------------------------------------------------- Vereinheitlichen
def art_von(rodzaj: str | None) -> tuple[str | None, bool]:
    if not rodzaj:
        return None, False
    m = re.match(r"([MUP](?:\s*/\s*[MUP])*)", rodzaj)
    if not m:
        return None, False
    buchst = set(re.findall(r"[MUP]", m.group(1)))
    return "".join(b for b in ART_REIHE if b in buchst), rodzaj.strip() != m.group(1)


def eigentum_von(text: str) -> tuple[str, bool]:
    gmina = bool(re.search(r"Gm\.?\s*Kr|GMK|Miasto Kraków", text))
    sp = bool(re.search(r"(?<![A-Za-z])SP(?![A-Za-z])", text))
    woj = "Województw" in text
    pr = bool(re.search(r"(?<![A-Za-z])PR(?![A-Za-z])", text))
    samoistne = bool(re.search(r"samoi", text, re.I))
    oeff = sum((gmina, sp, woj))
    if pr:
        klasse = "z_prywatnymi" if oeff else "prywatne"
    elif oeff > 1:
        klasse = "publiczne_mieszane"
    elif gmina:
        klasse = "gmina"
    elif sp:
        klasse = "skarb_panstwa"
    elif woj:
        klasse = "publiczne_mieszane"
    else:
        klasse = "brak"
    return klasse, samoistne


def dzielnica_von(text: str | None) -> str | None:
    if not text:
        return None
    if text.startswith("poza Krakowem"):
        return "poza"
    m = re.match(r"([IVX]+)\s*-\s", text)
    if m and m.group(1) in ROEMISCH:
        return f"{ROEMISCH.index(m.group(1)) + 1:02d}"
    return None


def nummer_von(nr: str | None) -> tuple[str, list[str]]:
    """(Klasse, Kandidaten) nach dem Protokoll; Kandidaten in der Reihenfolge des Textes."""
    s = (nr or "").strip()
    if not s or re.match(r"(obok|za\b|dz\.|dz\s|budynek|garaż|Str\.)", s, re.I) or not re.match(r"\d", s):
        return "beschreibung", []
    s = re.sub(r"(\d)\s+([A-Za-z])\b", r"\1\2", s)
    kopf = re.split(r"\(|,|\s+bud|\s+dz", s)[0].strip()
    teile = [t for t in re.split(r"\s*[-/]\s*", kopf) if t]
    if not teile or not all(re.fullmatch(r"\d*[A-Za-z]{0,2}", t) for t in teile) or not teile[0][0].isdigit():
        m = re.match(r"(\d+[A-Za-z]?)\b", s)
        return ("zusatz", [m.group(1)]) if m else ("beschreibung", [])
    basis = re.match(r"\d+", teile[0]).group(0)
    kand = [t if t[0].isdigit() else basis + t for t in teile]
    if kopf != s:
        return "zusatz", kand
    return ("standard" if len(kand) == 1 else "bereich"), kand


def name_von(name: str | None) -> str:
    s = name or ""
    s = re.sub(r"\"[^\"]*\"|„[^”]*”|\([^)]*\)?", " ", s)
    s = s.split(" - ")[0]
    if "/" in s:
        s = re.sub(r"\s+\d+[A-Za-z]?\s*$", "", s.split("/")[0])
    return norm(s)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.casefold().replace(".", " ")).strip()


SW = re.compile(r"św|świętego|świętej|świętych")


def name_passt(osm: str, zbk: str, nachtrag1: bool = True) -> bool:
    """OSM-Name (ohne Vorsatz) endet mit dem ZBK-Namen, Wort für Wort.

    Grundregel des Protokolls; Nachtrag 1 (13.11.2026, nach dem ersten Lauf): ein ZBK-Name aus zwei Wörtern gilt
    auch umgekehrt („Dietla Józefa“ = „Józefa Dietla“), und das Wort „św“ passt auf „świętego“, „świętej“,
    „świętych“.
    """
    o, z = osm.split(), zbk.split()
    if not z or len(z) > len(o):
        return False

    def gleich(a: list[str], b: list[str]) -> bool:
        return all(x == y or (y == "św" and SW.fullmatch(x)) for x, y in zip(a, b))

    if not nachtrag1:
        return o[-len(z):] == z
    if gleich(o[-len(z):], z):
        return True
    return len(z) == 2 and gleich(o[-2:], z[::-1])


def osm_strasse(name: str) -> tuple[str, str]:
    n = norm(name)
    for vorsatz, wort in (("os", "osiedle "), ("pl", "plac "), ("al", "aleja "), ("al", "al ")):
        if n.startswith(wort):
            return vorsatz, n[len(wort):]
    return "ul", n


def vorsatz_von(v: str | None) -> str | None:
    if not v:
        return None
    m = re.match(r"(ul|os|al|pl)\.", v.strip())
    return m.group(1) if m else None


# ------------------------------------------------------------------------------------- OSM
def osm_lesen(pbf: Path, b, rahmen) -> dict:
    import osm_pbf  # noqa: E402  (Leser des Pakets OSM und Fußwegnetz, nur gelesen)

    def k_wahl(t):
        return "addr:housenumber" in t or "heritage" in t

    def w_wahl(t):
        return "addr:housenumber" in t or "heritage" in t

    erg = osm_pbf.lies(pbf, rechteck=rahmen, knoten_wahl=k_wahl, weg_wahl=w_wahl,
                       relation_wahl=lambda t: "addr:housenumber" in t)
    zu = Transformer.from_crs(CRS.from_epsg(4326), b.crs, always_xy=True)
    objekte = []   # (tags, punkt BDOT-CRS, umriss BDOT-CRS oder None)
    z = Counter()
    for _, lon, lat, t in erg.getaggte_knoten:
        x, y = zu.transform(lon, lat)
        objekte.append((t, Point(x, y), None))
    for _, t, ids in erg.wege:
        lon, lat, ok = erg.koordinaten(ids)
        if not ok.any():
            continue                     # ganz außerhalb des Rahmens um die Stadt
        if not ok.all() or len(ids) < 4 or ids[0] != ids[-1]:
            z["wege_offen_oder_am_rahmen"] += 1
            continue
        xs, ys = zu.transform(lon, lat)
        poly = Polygon(list(zip(xs, ys)))
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty:
            z["wege_ungueltig"] += 1
            continue
        objekte.append((t, poly.representative_point(), poly if "building" in t else None))
    z["relationen_mit_adresse_nicht_gelesen"] = len(erg.relationen)
    adressen, heritage = [], []
    for t, p, poly in objekte:
        if not b.stadt_p.contains(p):
            z["ausserhalb_stadt"] += 1
            continue
        if "heritage" in t:
            heritage.append((p, poly))
        if "addr:housenumber" in t:
            strasse = t.get("addr:street") or t.get("addr:place")
            if not strasse:
                z["adresse_ohne_strasse"] += 1
                continue
            v, rest = osm_strasse(strasse)
            adressen.append({"v": v, "rest": rest, "nr": norm(t["addr:housenumber"]).replace(" ", ""),
                             "p": p, "poly": poly, "heritage": "heritage" in t})
    z["adressen_in_stadt"] = len(adressen)
    z["heritage_in_stadt"] = len(heritage)
    kopf = erg.kopf
    stand = None
    if kopf and getattr(kopf, "zeitstempel", None):
        from datetime import UTC, datetime
        stand = datetime.fromtimestamp(kopf.zeitstempel, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"adressen": adressen, "heritage": heritage, "zaehlung": dict(sorted(z.items())), "stand": stand}


def verorten(e: dict, index: dict, nachtrag1: bool = True) -> tuple[str, dict | None]:
    if e["st"] == "poza":
        return "poza_krakowem", None
    klasse_nr, kand = nummer_von(e.get("nr"))
    if "/" in (e.get("name") or "") and "/" in (e.get("nr") or ""):
        kand = kand[:1]            # Eckadresse: Nummer nach „/“ gehört zur zweiten Straße (Protokoll, Eckadresse)
    e["nr_klasse"] = klasse_nr
    if klasse_nr == "beschreibung":
        return "beschreibung", None
    zbk = name_von(e.get("name"))
    v = vorsatz_von(e.get("vorsatz"))
    if nachtrag1 and zbk.endswith(" plac"):       # Nachtrag 1 zum Protokoll: „… Plac“ am Ende = Vorsatz pl.
        zbk, v = zbk[:-5].strip(), "pl"
    erlaubt = {"os": {"os"}, "pl": {"pl"}, "al": {"al", "ul"}, "ul": {"ul"}}.get(v, {"ul"})
    strassen = {rest for (vv, rest) in index if vv in erlaubt and name_passt(rest, zbk, nachtrag1)}
    if not strassen:
        return "ulica_nie_znaleziona", None
    for nr in kand:
        nr_n = nr.casefold()
        mit = {s for s in strassen if any(a["nr"] == nr_n for vv in erlaubt for a in index.get((vv, s), []))}
        if not mit:
            continue
        if len(mit) > 1:
            return "mehrdeutig_ulica", None
        s = mit.pop()
        objs = [a for vv in sorted(erlaubt) for a in index.get((vv, s), []) if a["nr"] == nr_n]
        pts = [a["p"] for a in objs]
        if max(p.distance(q) for p in pts for q in pts) > PUNKT_STREUUNG_M:
            return "mehrdeutig_punkt", None
        geb = [a for a in objs if a["poly"] is not None]
        wahl = max(geb, key=lambda a: a["poly"].area) if geb else objs[0]
        return "verortet", {**wahl, "heritage_any": any(a["heritage"] for a in objs)}
    return "numer_nie_znaleziony", None


# ------------------------------------------------------------------------------------- Rechnen
def rechnen() -> dict[str, str]:
    d = daten_ordner()
    pdf = d / ZBK_REL
    regeln = d / ZBK_REGELN_REL
    for p in (pdf, regeln):
        if not p.exists():
            raise FileNotFoundError(str(p))
    dz = modul("dz_denkmale", "dz_denkmale.py")
    lod = modul("lod", "20_lod.py")
    import raum_bevoelkerung as rb  # noqa: E402  (Grenzen der dzielnice, Paket Gliederung und Bevölkerung)

    # Schritt 1: Liste lesen
    eintraege, zl = tabelle_lesen(pdf)
    if not (zl["lp_lueckenlos"] and zl["zweiter_leseweg_gleich"] and zl["titel_gefunden"]) or zl["befunde"]:
        raise ValueError(f"Lesen der Liste nicht sauber: {json.dumps(zl, ensure_ascii=False)[:600]}")
    roh = {k: Counter(e.get(k) for e in eintraege) for k in ("vorsatz", "ort", "rodzaj", "dzielnica")}
    fehlend = Counter()
    for e in eintraege:
        for k in ("name", "rodzaj", "wlasnosc", "dzielnica"):
            fehlend[k] += not e.get(k)
        e["art"], e["art_zusatz"] = art_von(e.get("rodzaj"))
        e["eig"], e["samoistne_pos"] = eigentum_von(" ".join(filter(None, (e.get("wlasnosc"), e.get("samoistne")))))
        e["st"] = dzielnica_von(e.get("dzielnica"))
    if any(e["st"] is None or e["art"] is None for e in eintraege):
        raise ValueError("Dzielnica oder Art nicht lesbar: "
                         + str([e["lp"] for e in eintraege if e["st"] is None or e["art"] is None]))

    # Haftungsklausel wörtlich aus den Regeln der Weiterverwendung
    rtext = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", regeln.read_text(encoding="utf-8"))))
    m = re.search(r"o treści: „(Gmina Miejska Kraków nie ponosi odpowiedzialności za:.*?)”", rtext)
    if not m:
        raise ValueError("Haftungsklausel in bip_dok48482_ponowne.html nicht gefunden")
    haftung = m.group(1)

    # Schritt 2: BDOT10k, LoD2, OSM, dzielnice
    b = dz.Bdot(d / dz.BDOT_REL)
    lod_pfade = lod.eingangsdateien(d / "eingang", "lod2")
    lod2, lod_z = lod.hoehen_lesen(lod_pfade) if lod_pfade else ({}, None)
    konfig = ort_konfig.lade()
    pbfs = sorted((d / "eingang").glob("*.osm.pbf"))
    if len(pbfs) != 1:
        raise FileNotFoundError(f"genau ein OSM-Auszug in eingang/ erwartet, gefunden {len(pbfs)}")
    w, s, o, n = b.stadt.bounds
    (lw, ls), (lo, ln) = b.nach_wgs.transform(w, s), b.nach_wgs.transform(o, n)
    osm = osm_lesen(pbfs[0], b, (lw - 0.01, ls - 0.01, lo + 0.01, ln + 0.01))
    import ortsmarke as om_modul  # noqa: E402  (ein Punkt für ul. Kościuszki 18 in allen Dateien, pruefen/N1_protokoll.md Regel 3)
    om = om_modul.kosciuszki_18(pbfs[0], (lw - 0.01, ls - 0.01, lo + 0.01, ln + 0.01),
                                 lambda x, y: b.stadt_p.contains(Point(*b.von_wgs.transform(x, y))))
    dzielnice, dz_quelle, dz_grund, dz_z = rb.dzielnice_aus_eingang(konfig)
    if dzielnice is None:
        raise FileNotFoundError(dz_grund)
    dz_prep = {k: prep(v.geom) for k, v in sorted(dzielnice.items())}

    def dzielnica_bei(lon: float, lat: float) -> str | None:
        p = Point(lon, lat)
        return next((k for k, g in dz_prep.items() if g.contains(p)), None)

    index: dict[tuple[str, str], list] = {}
    for a in osm["adressen"]:
        index.setdefault((a["v"], a["rest"]), []).append(a)
    her_geb: set[int] = set()
    for p, _poly in osm["heritage"]:
        for i in b.baum.query(p, predicate="intersects"):
            if b.gebaeude[int(i)][0].contains(p):
                her_geb.add(int(i))

    # Vergleichslauf ohne Nachtrag 1 (Namensregeln aus), nur gezählt
    ohne_n1 = Counter()
    for e in eintraege:
        k, t = verorten(dict(e), index, nachtrag1=False)
        if t is not None:
            ohne_n1["treffer"] += 1
            ohne_n1["gegenprobe_gleich"] += dzielnica_bei(*b.wgs(t["p"].x, t["p"].y)) == e["st"]
        ohne_n1[k] += 1
    rechen_crs = CRS.from_epsg(ort_konfig.RECHEN_SRID)
    wgs_rechen = Transformer.from_crs(CRS.from_epsg(4326), rechen_crs, always_xy=True)

    def in_rechen(g):
        return shapely.transform(g, lambda xy: np.column_stack(wgs_rechen.transform(xy[:, 0], xy[:, 1])))

    dz_rechen = {k: in_rechen(v.geom) for k, v in sorted(dzielnice.items())}

    # Schritt 3: verorten und verknüpfen
    for e in eintraege:
        e["vk"], treffer = verorten(e, index)
        e["geb"], e["link"], e["dm"] = None, None, None
        if treffer is None:
            continue
        e["lage"] = b.wgs(treffer["p"].x, treffer["p"].y)
        e["st_osm"] = dzielnica_bei(*e["lage"])
        e["treffer"] = True
        if e["st_osm"] != e["st"]:                 # Nachtrag 2: abweichende dzielnica, kein Punkt, keine Verknüpfung
            e["vk"] = "abweichung_dzielnica"
            e["abstand_m"] = round(dz_rechen[e["st"]].distance(in_rechen(Point(*e["lage"]))))
            e["grenzt"] = bool(e["st_osm"] and dz_rechen[e["st"]].intersects(dz_rechen[e["st_osm"]]))
            continue
        idx = None
        if treffer["poly"] is not None:
            bester, wert = None, 0.0
            for i in b.baum.query(treffer["poly"], predicate="intersects"):
                g = b.gebaeude[int(i)][0]
                schnitt = g.intersection(treffer["poly"]).area / min(g.area, treffer["poly"].area)
                if schnitt > wert:
                    bester, wert = int(i), schnitt
            if bester is not None and wert >= UMRISS_ANTEIL:
                idx, e["link"] = bester, "umriss"
        if idx is None:
            idx = b.gebaeude_bei(treffer["p"])
            e["link"] = "punkt" if idx is not None else "ohne"
        e["geb"] = idx
        e["dm"] = bool(treffer["heritage_any"] or (idx is not None and idx in her_geb))

    # Schritt 4: Typologie (Schätzung) auf BDOT10k
    rechen = CRS.from_epsg(ort_konfig.RECHEN_SRID)
    nach_rechen = Transformer.from_crs(b.crs, rechen, always_xy=True)
    mfh_idx = [i for i, (g, a) in enumerate(b.gebaeude) if a["KAT_ISTNIE"] == "eksploatowany" and a["PFBUD"] == MFH]
    geoms = shapely.transform(np.array([b.gebaeude[i][0] for i in mfh_idx], dtype=object),
                              lambda xy: np.column_stack(nach_rechen.transform(xy[:, 0], xy[:, 1])))
    flaeche = shapely.area(geoms)
    mrr = shapely.area(shapely.minimum_rotated_rectangle(geoms))
    recht = np.divide(flaeche, mrr, out=np.zeros_like(flaeche), where=mrr > 0)
    gs = np.array([int(float(b.gebaeude[i][1]["LICZ_KONDY"])) if b.gebaeude[i][1]["LICZ_KONDY"] else -1
                   for i in mfh_idx])
    blok = (gs >= TYP["geschosse_min"]) & (flaeche >= TYP["flaeche_min_m2"]) & (recht >= TYP["rechteckigkeit_min"])
    mitte = shapely.centroid(geoms)
    alle_rechen = shapely.transform(np.array([g for g, _ in b.gebaeude], dtype=object),
                                    lambda xy: np.column_stack(nach_rechen.transform(xy[:, 0], xy[:, 1])))
    alle_baum = STRtree(alle_rechen)
    angebaut = np.zeros(len(mfh_idx), dtype=bool)
    for j in np.flatnonzero(blok):
        nachbarn = [int(k) for k in alle_baum.query(geoms[j], predicate="dwithin", distance=ANGEBAUT_TOL_M)
                    if int(k) != mfh_idx[j]]
        gemeinsam = sum(geoms[j].boundary.intersection(alle_rechen[k].buffer(ANGEBAUT_TOL_M)).length for k in nachbarn)
        angebaut[j] = gemeinsam >= ANGEBAUT_MIN_M
    blok_pos = np.flatnonzero(blok)
    baum = STRtree(mitte[blok_pos])
    osiedle = np.zeros(len(mfh_idx), dtype=bool)
    for j, pos in enumerate(blok_pos):
        nachbarn = baum.query(mitte[pos], predicate="dwithin", distance=TYP["umkreis_m"])
        osiedle[pos] = len(nachbarn) - 1 >= TYP["nachbarn_min"]
    typ_von = {}
    leer = {"mfh": 0, "blok": 0, "osiedle": 0, "blok_angebaut": 0, "osiedle_angebaut": 0}
    je_del = {k: dict(leer) for k in b.del_p}
    je_dz = {k: dict(leer) for k in sorted(dzielnice)}
    ohne_del, ohne_dz = dict(leer), dict(leer)
    stadt = dict(leer)
    lagen = []
    for j, i in enumerate(mfh_idx):
        g = b.gebaeude[i][0]
        c = g.centroid
        lon, lat = b.wgs(c.x, c.y)
        de = b.delegatura(c)
        dzn = dzielnica_bei(lon, lat)
        lagen.append((lon, lat, de, int(gs[j])))
        t = "osiedle" if osiedle[j] else ("blok" if blok[j] else None)
        typ_von[i] = t
        for ziel in (stadt, je_del[de] if de else ohne_del, je_dz[dzn] if dzn else ohne_dz):
            ziel["mfh"] += 1
            ziel["blok"] += bool(blok[j])
            ziel["osiedle"] += bool(osiedle[j])
            ziel["blok_angebaut"] += bool(blok[j] and angebaut[j])
            ziel["osiedle_angebaut"] += bool(osiedle[j] and angebaut[j])
    rnd = random.Random(STARTWERT)
    kand = sorted(j for j in range(len(mfh_idx)) if osiedle[j])
    nicht = sorted(j for j in range(len(mfh_idx)) if not blok[j] and gs[j] >= TYP["geschosse_min"])
    stich = {"osiedle": [lagen[j] for j in sorted(rnd.sample(kand, min(STICHPROBE["osiedle"], len(kand))))],
             "kein_kandidat": [lagen[j] for j in sorted(rnd.sample(nicht, min(STICHPROBE["kein_kandidat"], len(nicht))))]}
    stich["osiedle_ab"] = {}            # Großsiedlungs-Kandidaten bei strengerer Untergrenze (nur Beleg)
    for m in (4, 5, 6):
        b_m = np.flatnonzero(blok & (gs >= m))
        baum_m = STRtree(mitte[b_m])
        stich["osiedle_ab"][m] = sum(1 for pos in b_m if len(baum_m.query(mitte[pos], predicate="dwithin",
                                                                           distance=TYP["umkreis_m"])) - 1 >= TYP["nachbarn_min"])
    sicht = sichtpruefung_lesen(stich)

    # Schritt 5: Zusammenstellen
    N = len(eintraege)
    je_art = dict(sorted(Counter(e["art"] for e in eintraege).items()))
    je_eig = {k: sum(e["eig"] == k for e in eintraege) for k in EIG_KLASSEN}
    raeume = [f"{i:02d}" for i in range(1, 19)] + ["poza"]
    je_st = {}
    for r in raeume:
        es = [e for e in eintraege if e["st"] == r]
        je_st[r] = {"n": len(es), "art": dict(sorted(Counter(e["art"] for e in es).items())),
                    "eigentum": {k: sum(e["eig"] == k for e in es) for k in EIG_KLASSEN}}
    miejsc = Counter("krakow" if (e.get("ort") or "").startswith(("Kraków", "od 01-01")) else
                     ("wieliczka" if (e.get("ort") or "") == "Wieliczka" else "inne") for e in eintraege)
    k18 = [e for e in eintraege if name_von(e.get("name")) == "kościuszki" and nummer_von(e.get("nr"))[1][:1] == ["18"]]
    # ohne Quelle des Ausgangsprojekts: KR24 bleibt, kein Projektname an der Ortsmarke (Bestätigung 14.11. zu KR31)
    ortsmarke = {"schluessel": "kosciuszki_18", "in_liste": bool(k18)}
    if k18:
        ortsmarke.update({"st": k18[0]["st"], "art": k18[0]["art"], "eigentum": k18[0]["eig"]})
    bdot_vermerk = dz.VERMERK_BDOT
    san = {
        "stand": ZBK_STAND, "stand_bdot": dz.BDOT_STAND,
        "quellen": {"zbk": {"vermerk": VERMERK_ZBK, "odpowiedzialnosc": haftung, "url": ZBK_URL,
                            "plik": ZBK_PLIK, "sha256": sha256(pdf)},
                    "bdot": {"vermerk": bdot_vermerk}},
        "liste": {"eintraege": N, "je_art": je_art, "je_eigentum": je_eig,
                  "samoistne_posiadanie": sum(e["samoistne_pos"] for e in eintraege),
                  "art_mit_zusatz": sum(e["art_zusatz"] for e in eintraege),
                  "miejscowosc": dict(sorted(miejsc.items())), "je_dzielnica": je_st,
                  "spalten_fehlen": ["zarzadca", "nr_rejestru_zabytkow"]},
        "typologie": {"schaetzung": True, "baujahr": False, "kriterien": TYP,
                      "angebaut": {"toleranz_m": ANGEBAUT_TOL_M, "grenze_min_m": ANGEBAUT_MIN_M},
                      "grundgesamtheit": "BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny",
                      "stadt": stadt, "delegaturen": je_del, "nicht_zugeordnet": ohne_del,
                      "literatur": LITERATUR, **({"sichtpruefung": sicht} if sicht else {})},
        "ortsmarke": ortsmarke,
    }
    # ODbL-Teil
    vk_je = {k: sum(e["vk"] == k for e in eintraege) for k in VERORTUNG_KLASSEN}
    vk_art = {a: {"n": sum(e["art"] == a for e in eintraege),
                  "verortet": sum(e["art"] == a and e["vk"] == "verortet" for e in eintraege)} for a in je_art}
    kr = [e for e in eintraege if e["st"] != "poza"]
    vt = [e for e in eintraege if e["vk"] == "verortet"]
    gp = [e for e in eintraege if e.get("treffer")]
    gleich = sum(e["st_osm"] == e["st"] for e in gp)
    lod_n = geschoss_n = kleinhaus_n = unter_gs_n = 0
    feats = []
    for e in vt:
        h, hq, gsz, fn, typ = None, None, None, None, None
        if e["geb"] is not None:
            g, a = b.gebaeude[e["geb"]]
            gsz = int(float(a["LICZ_KONDY"])) if a["LICZ_KONDY"] else None
            fn = a["PFBUD"] or None
            typ = typ_von.get(e["geb"])
            if a["LOKALNYID"] in lod2:
                h, hq = round(lod2[a["LOKALNYID"]][0], 1), "lod2"
            elif gsz:
                h, hq = round(gsz * GESCHOSS_M, 1), "geschosse"
        e["hq"] = hq
        lod_n += hq == "lod2"
        geschoss_n += hq == "geschosse"
        if e["eig"] not in EIG_PUNKTE or e["samoistne_pos"]:
            continue
        if fn in KLEINHAUS or ("M" in e["art"] and fn is None):
            kleinhaus_n += 1
            continue
        if gsz is None or gsz < PUNKT_GESCHOSSE_MIN:
            unter_gs_n += 1
            continue
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": e["lage"]},
                      "properties": {"art": e["art"], "eig": e["eig"], "st": e["st"], "gs": gsz, "fn": fn,
                                     "h": h, "hq": hq, "typ": typ}})
    feats.sort(key=lambda f: (f["geometry"]["coordinates"], json.dumps(f["properties"], sort_keys=True)))
    geb_einzeln = len({e["geb"] for e in vt if e["geb"] is not None})
    k18_ort = None
    if k18 and k18[0]["vk"] == "verortet" and om:
        k18_ort = {"schluessel": om_modul.SCHLUESSEL, "geometry": {"type": "Point", "coordinates": [om["lon"], om["lat"]]},
                   "lage_geprueft": False, "st_osm": k18[0].get("st_osm"), "hq": k18[0]["hq"]}
    odbl = {
        "stand": ZBK_STAND, "stand_osm": osm["stand"],
        "quellen": {"zbk": {"vermerk": VERMERK_ZBK_ODBL, "odpowiedzialnosc": haftung},
                    "bdot": {"vermerk": bdot_vermerk}, "lod2": {"vermerk": VERMERK_LOD2},
                    "osm": {"vermerk": VERMERK_OSM, "vermerk_sprachen": VERMERK_OSM_SPRACHEN,
                            "datei": pbfs[0].name}},
        "verortung": {"eintraege": N, "in_krakow": len(kr), "je_klasse": vk_je, "je_art": vk_art,
                      "quote": anteil(len(vt), len(kr)), "wilson95": wilson(len(vt), len(kr)),
                      "ohne_namensregeln": {"verortet": ohne_n1["gegenprobe_gleich"], "treffer": ohne_n1["treffer"],
                                         "ulica_nie_znaleziona": ohne_n1["ulica_nie_znaleziona"]}},
        "gegenprobe_dzielnica": {"n": len(gp), "gleich": gleich, "quote": anteil(gleich, len(gp)),
                                 "wilson95": wilson(gleich, len(gp))},
        "verknuepfung": {"verortet": len(vt),
                         "umriss": sum(e["link"] == "umriss" for e in vt),
                         "punkt": sum(e["link"] == "punkt" for e in vt),
                         "ohne": sum(e["link"] == "ohne" for e in vt),
                         "gebaeude_einzeln": geb_einzeln, "hoehe_lod2": lod_n, "hoehe_geschosse": geschoss_n,
                         "typ_blok": sum(typ_von.get(e["geb"]) == "blok" for e in vt if e["geb"] is not None),
                         "typ_osiedle": sum(typ_von.get(e["geb"]) == "osiedle" for e in vt if e["geb"] is not None)},
        "punkte": {"type": "FeatureCollection", "features": feats,
                   "nur_eigentum": list(EIG_PUNKTE), "geschosse_min": PUNKT_GESCHOSSE_MIN,
                   "ausgelassen_kleinhaus": kleinhaus_n, "ausgelassen_unter_3_geschosse": unter_gs_n},
        "typologie_dzielnice": {"schaetzung": True, "je_dzielnica": je_dz, "nicht_zugeordnet": ohne_dz},
        "ortsmarke": k18_ort,
    }
    werkzeuge = {"python": platform.python_version(), "poppler": poppler_version(),
                 "shapely": shapely.__version__}
    tabelle_schreiben = (eintraege, d / "abgeleitet" / "sanierung" / "zbk_tabelle.tsv")
    dateien = {
        "daten/sanierung.js": js("KIEZ_SANIERUNG",
                                 "Sanierungsatlas Wohnungsbestand: Zählungen aus der ZBK-Liste (Stand 2025-12-01) und "
                                 "Typologie-Schätzung aus BDOT10k. Quellen und Vermerke im Feld quellen. Erzeugt von "
                                 "skripte/36_sanierung.py", san),
        "daten/sanierung_odbl.js": js("KIEZ_SANIERUNG_ODBL",
                                      "Sanierungsatlas Wohnungsbestand, verortete Einträge der ZBK-Liste. Adressen über "
                                      "OpenStreetMap verortet und Grenzen der dzielnice aus OpenStreetMap: "
                                      + VERMERK_OSM + "; diese Datei steht daher unter der Open Database License "
                                      "(ODbL) 1.0. Erzeugt von skripte/36_sanierung.py", odbl),
        "belege/DS_sanierung_lauf.md": beleg(eintraege, zl, roh, fehlend, san, odbl, osm, lod_z, dz_z, dz_quelle,
                                             stich, werkzeuge, pdf, len(mfh_idx), b, om),
    }
    return dateien, tabelle_schreiben


def sichtpruefung_lesen(stich: dict) -> dict | None:
    """Ergebnis der Sichtprüfung der Typologie-Stichprobe aus belege/DS_sichtpruefung.json (Eingabe, von Hand);
    None, solange es keines gibt. Abbruch, wenn die Zählungen nicht zur Stichprobe passen."""
    p = WURZEL / "belege" / "DS_sichtpruefung.json"
    if not p.is_file():
        return None
    e = json.loads(p.read_text(encoding="utf-8"))
    if e["startwert"] != STARTWERT:
        raise ValueError(f"{p.name}: Startwert {e['startwert']}, Stichprobe mit {STARTWERT}")
    aus = {"datum": e["datum"], "grundlage": "ortofotomapa"}
    for k in ("osiedle", "kein_kandidat"):
        z = e[k]
        if z["n"] != len(stich[k]) or z["ja"] + z["nein"] + z["unklar"] != z["n"]:
            raise ValueError(f"{p.name}: {k} passt nicht zur Stichprobe ({z}, gezogen {len(stich[k])})")
        ent = z["ja"] + z["nein"]
        aus[k] = {"n": z["n"], "ja": z["ja"], "nein": z["nein"], "unklar": z["unklar"],
                  "quote": anteil(z["ja"], ent), "wilson95": wilson(z["ja"], ent)}
    return aus


def js(name: str, kopf: str, inhalt: dict) -> str:
    return f"/* {kopf} */\nwindow.{name}=" + json.dumps(inhalt, ensure_ascii=False, separators=(",", ":")) + ";\n"


def zahl(x) -> str:
    return f"{x:,}".replace(",", ".") if isinstance(x, int) else str(x)


def beleg(eintraege, zl, roh, fehlend, san, odbl, osm, lod_z, dz_z, dz_quelle, stich, werkzeuge, pdf, n_mfh, b,
          om_osm=None) -> str:
    L = []
    w = L.append
    N = len(eintraege)
    w("# Beleg Sanierungsatlas Wohnungsbestand: Lauf")
    w("")
    w("Erzeugt von `skripte/36_sanierung.py` nach `pruefen/DS_protokoll.md`. Kein Netz, keine Datenbank. "
      f"Werkzeuge: Python {werkzeuge['python']}, Poppler pdftotext {werkzeuge['poppler']}, shapely "
      f"{werkzeuge['shapely']}. Rechen-Koordinatensystem der Typologie: {ort_konfig.srs_name()}; Verknüpfung im "
      "Koordinatensystem der BDOT10k-Lieferung.")
    w("")
    w("## Eingänge")
    w("")
    w("| Eingang | Datei | SHA256 |")
    w("|---|---|---|")
    w(f"| ZBK-Liste ({ZBK_STAND}) | `$KIEZ_DATEN/{ZBK_REL}` | `{sha256(pdf)}` |")
    w(f"| Regeln der Weiterverwendung | `$KIEZ_DATEN/{ZBK_REGELN_REL}` | `{sha256(daten_ordner() / ZBK_REGELN_REL)}` |")
    w(f"| BDOT10k 1261 (Stand {san['stand_bdot']}) | `$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip` | siehe `belege/rohdaten-D5-2026-11-13.sha256` |")
    w(f"| OSM | `$KIEZ_DATEN/eingang/{odbl['quellen']['osm']['datei']}` (Stand {odbl['stand_osm']}) | siehe `$KIEZ_DATEN/eingang/SHA256SUMS` |")
    w("| LoD2 2017 | `$KIEZ_DATEN/eingang/lod2_1261_gml.zip` | siehe `$KIEZ_DATEN/eingang/SHA256SUMS` |")
    w("")
    w("## Schritt 1: PDF → Tabelle")
    w("")
    w(f"- Titel im PDF gefunden: „{ZBK_TITEL}“ = {zl['titel_gefunden']}")
    w(f"- Seiten mit Einträgen: {sum(1 for x in zl['je_seite'] if x)} von {zl['seiten']}; Einträge je Seite: "
      f"{', '.join(map(str, zl['je_seite']))}")
    w(f"- Einträge N = {N}; L.p. lückenlos 1 … {N}: {zl['lp_lueckenlos']}")
    w(f"- Zweiter Leseweg (`pdftotext -layout`, Zeilen mit L.p. am Anfang) je Seite gleich und L.p. in gleicher "
      f"Reihenfolge: {zl['zweiter_leseweg_gleich']}")
    w(f"- größter Abstand Zellmitte – Mitte der L.p.: {zl['max_abstand_pt']} pt (Grenze {MITTE_TOLERANZ} pt); "
      f"Befunde: {len(zl['befunde'])}")
    w(f"- leere Pflichtfelder: " + ", ".join(f"{k} {v}" for k, v in sorted(fehlend.items())))
    w("")
    w("Rohwerte vor dem Vereinheitlichen (Anzahl Einträge):")
    w("")
    for k, titel in (("vorsatz", "Vorsatz"), ("rodzaj", "Rodzaj"), ("ort", "Miejscowość"), ("dzielnica", "Dzielnica")):
        werte = sorted(roh[k].items(), key=lambda t: (-t[1], str(t[0])))
        w(f"- {titel}: " + "; ".join(f"„{v}“ {c}" if v else f"(leer) {c}" for v, c in werte))
    w("")
    w("## Schritt 2: Vereinheitlicht (`daten/sanierung.js`)")
    w("")
    li = san["liste"]
    w(f"- je Art: " + ", ".join(f"{k} {v}" for k, v in li["je_art"].items()) + f" (Σ {sum(li['je_art'].values())})")
    w(f"- je Eigentum: " + ", ".join(f"{k} {v}" for k, v in li["je_eigentum"].items())
      + f" (Σ {sum(li['je_eigentum'].values())}); davon mit samoistne posiadanie: {li['samoistne_posiadanie']}")
    w(f"- Art mit Zusatz im Rohtext (nicht veröffentlicht): {li['art_mit_zusatz']}")
    w(f"- Miejscowość: " + ", ".join(f"{k} {v}" for k, v in li["miejscowosc"].items()))
    w(f"- Σ je Dzielnica: {sum(v['n'] for v in li['je_dzielnica'].values())} = N")
    w("")
    w("| Dzielnica | Einträge | M | U | P | MU | andere | gmina | skarb_panstwa | publiczne_mieszane | z_prywatnymi | prywatne | brak |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r, v in li["je_dzielnica"].items():
        a = v["art"]
        andere = sum(c for k, c in a.items() if k not in ("M", "U", "P", "MU"))
        e = v["eigentum"]
        w(f"| {r} | {v['n']} | {a.get('M', 0)} | {a.get('U', 0)} | {a.get('P', 0)} | {a.get('MU', 0)} | {andere} | "
          + " | ".join(str(e[k]) for k in EIG_KLASSEN) + " |")
    w("")
    w("Nicht in der Liste: ein Verwalter je Eintrag (Verwalter ist laut Titel der ZBK) und eine Nummer im "
      "Denkmalregister. Beides wird nicht nachgetragen.")
    w("")
    w("## Schritt 3: Tabelle → verortet (`daten/sanierung_odbl.js`)")
    w("")
    oz = osm["zaehlung"]
    w(f"- OSM-Adressen in der Stadtgrenze (BDOT10k): {dez(oz.get('adressen_in_stadt', 0))}; Objekte mit heritage: "
      f"{oz.get('heritage_in_stadt', 0)}; nicht gelesen: Relationen mit Adresse {oz.get('relationen_mit_adresse_nicht_gelesen', 0)}, "
      f"offene oder am Rahmen abgeschnittene Wege {oz.get('wege_offen_oder_am_rahmen', 0)}, Adressen ohne Straße "
      f"{oz.get('adresse_ohne_strasse', 0)}")
    ve = odbl["verortung"]
    w(f"- Einträge in Kraków (Dzielnica I–XVIII): {ve['in_krakow']}; verortet {ve['je_klasse']['verortet']} = "
      f"{dez(ve['quote'])} % (Wilson 95 %: {dez(ve['wilson95'])} %)")
    w("- je Ergebnisklasse: " + ", ".join(f"{k} {v}" for k, v in ve["je_klasse"].items())
      + f" (Σ {sum(ve['je_klasse'].values())} = N)")
    w("- Klassen der Hausnummer: " + ", ".join(
        f"{k} {v}" for k, v in sorted(Counter(e.get('nr_klasse', '(poza)') for e in eintraege).items())))
    w("")
    w("| Art | Einträge | verortet | Quote % | Wilson 95 % |")
    w("|---|---|---|---|---|")
    for a, v in ve["je_art"].items():
        w(f"| {a} | {v['n']} | {v['verortet']} | {dez(anteil(v['verortet'], v['n']))} | {dez(wilson(v['verortet'], v['n']))} |")
    w("")
    gp = odbl["gegenprobe_dzielnica"]
    w(f"Gegenprobe Dzielnica der Liste gegen OSM-dzielnica am Punkt (Grenzen aus {dz_quelle}, OSM-Stand {dz_z.get('stand_osm')}): "
      f"n = {gp['n']} Treffer, gleich {gp['gleich']} = {dez(gp['quote'])} % (Wilson 95 %: {dez(gp['wilson95'])} %). "
      "Abweichende Treffer sind nach Nachtrag 2 die Klasse abweichung_dzielnica (kein Punkt, keine Verknüpfung).")
    abw = [e for e in eintraege if e["vk"] == "abweichung_dzielnica"]
    if abw:
        w("")
        w("Abweichende Treffer (L.p., Art, Dzielnica Liste → OSM, Abstand des Punkts zum Polygon der Liste, "
          "Polygone grenzen aneinander): " + "; ".join(
              f"{e['lp']} {e['art']} {e['st']}→{e['st_osm'] or 'keine'}, {dez(e['abstand_m'])} m, "
              f"{'ja' if e['grenzt'] else 'nein'}" for e in abw)
          + ". Ob Liste oder Verortung irrt, ist nicht geprüft.")
    o1 = ve["ohne_namensregeln"]
    w("")
    w(f"Vergleichslauf ohne Nachtrag 1 (Namensregeln aus, im selben Lauf gerechnet): Treffer {o1['treffer']}, davon "
      f"verortet (dzielnica gleich) {o1['verortet']}, ulica_nie_znaleziona {o1['ulica_nie_znaleziona']}. Mit Nachtrag 1: "
      f"Treffer {gp['n']}, verortet {ve['je_klasse']['verortet']}, ulica_nie_znaleziona "
      f"{ve['je_klasse']['ulica_nie_znaleziona']}.")
    w("")
    w("Nicht verortete Einträge (L.p. Art Dzielnica, je Klasse; ohne Adresse, nachprüfbar am PDF):")
    w("")
    for k in VERORTUNG_KLASSEN[1:]:
        es = [e for e in eintraege if e["vk"] == k]
        w(f"- {k} ({len(es)}): " + ("; ".join(f"{e['lp']} {e['art']} {e['st']}" for e in es) or "keine"))
    w("")
    w("## Schritt 4: verortet → verknüpft")
    w("")
    vk = odbl["verknuepfung"]
    w(f"- verortet {vk['verortet']} (ohne abweichende Treffer): über OSM-Umriss (Schnitt ≥ {int(UMRISS_ANTEIL * 100)} %) {vk['umriss']}, "
      f"über Punkt (im Gebäude oder bis 10 m) {vk['punkt']}, ohne Gebäude {vk['ohne']} (Σ {vk['umriss'] + vk['punkt'] + vk['ohne']})")
    w(f"- verschiedene BDOT10k-Gebäude: {vk['gebaeude_einzeln']} (mehrere Einträge je Adresse, etwa Vorderhaus und "
      "Oficyna, treffen dasselbe Gebäude)")
    if lod_z:
        w(f"- LoD2 2017 gelesen: {dez(lod_z['gebaeude'])} Gebäude mit Kennung; Höhe aus LoD2 bei {vk['hoehe_lod2']} "
          f"verorteten Einträgen, aus Geschossen × {GESCHOSS_M:g} m bei {vk['hoehe_geschosse']}")
    vt_e = [e for e in eintraege if e["vk"] == "verortet"]
    w(f"- Denkmalangabe in OSM (heritage am Treffer oder im verknüpften Gebäude): {sum(bool(e['dm']) for e in vt_e)} von "
      f"{vk['verortet']} (keine Angabe heißt nicht „kein Denkmal“; das Feld steht deshalb nicht in den Daten, bis das "
      "Denkmalregister vorliegt)")
    w(f"- verknüpfte Gebäude, die Typologie-Kandidat sind: Block {vk['typ_blok']}, Großsiedlung {vk['typ_osiedle']}")
    w(f"- Punkte in der Datei (nur Eigentum {', '.join(EIG_PUNKTE)}, ohne samoistne posiadanie, ohne Einfamilienhäuser "
      f"laut BDOT10k, ohne Wohnnutzung ohne Gebäudefunktion, nur Gebäude mit mindestens {PUNKT_GESCHOSSE_MIN} "
      f"Geschossen laut BDOT10k): {len(odbl['punkte']['features'])}; ausgelassen (nur gezählt) als Kleinhaus "
      f"{odbl['punkte']['ausgelassen_kleinhaus']}, unter {PUNKT_GESCHOSSE_MIN} Geschossen oder ohne Geschosszahl "
      f"{odbl['punkte']['ausgelassen_unter_3_geschosse']}")
    if odbl["ortsmarke"]:
        om = odbl["ortsmarke"]
        w(f"- Ortsmarke ul. Kościuszki 18: in der Liste (Dzielnica {san['ortsmarke'].get('st')}, Art "
          f"{san['ortsmarke'].get('art')}, Eigentum {san['ortsmarke'].get('eigentum')}), verortet bei "
          f"{om['geometry']['coordinates']}, OSM-dzielnica {om['st_osm']}, Höhe {om['hq']}, Denkmalangabe in OSM {'ja' if any(e['dm'] for e in vt_e if name_von(e.get('name')) == 'kościuszki' and nummer_von(e.get('nr'))[1][:1] == ['18']) else 'nein'}; "
          "Lage nicht von Hand geprüft; Punkt der Ortsmarke aus `skripte/ortsmarke.py` (gleich in "
          "`daten/denkmale_odbl.js`)" + (f", OSM `{om_osm['osm']}` ({om_osm['art']}, {om_osm['kandidaten']} Kandidaten "
          "in der Stadt)" if om_osm else ""))
    else:
        w(f"- Ortsmarke ul. Kościuszki 18: in der Liste {san['ortsmarke']['in_liste']}, nicht verortet")
    w("")
    w("Fremde Vergleichsangabe (nicht eigene Zahl): Die FuturHist-Seite nennt für den ZBK „over 500 buildings“ und "
      "„Over 130 buildings managed by ZBK are under conservation protection“ (" + FUTURHIST_URL + ", abgerufen "
      f"{ABRUF}). Die Liste hat {N} Einträge; Einträge sind keine Gebäude (Schritt 4).")
    w("")
    w("## Schritt 5: Typologie (Schätzung)")
    w("")
    ty = san["typologie"]
    w(f"- Grundgesamtheit: {ty['grundgesamtheit']}: {zahl(n_mfh)} Gebäude")
    w(f"- Kriterien: {json.dumps(TYP, ensure_ascii=False)}")
    w(f"- Stadt: Mehrfamilienhäuser {zahl(ty['stadt']['mfh'])}, Kandidat Block {zahl(ty['stadt']['blok'])}, "
      f"Kandidat Großsiedlung {zahl(ty['stadt']['osiedle'])}")
    w("")
    w("| Raum | Mehrfamilienhäuser | Block | Großsiedlung |")
    w("|---|---|---|---|")
    for k, v in ty["delegaturen"].items():
        w(f"| {k} | {zahl(v['mfh'])} | {zahl(v['blok'])} | {zahl(v['osiedle'])} |")
    v = ty["nicht_zugeordnet"]
    w(f"| keiner Delegatur zugeordnet | {v['mfh']} | {v['blok']} | {v['osiedle']} |")
    sd = sum(x["mfh"] for x in ty["delegaturen"].values()) + v["mfh"]
    w("")
    w(f"Σ Delegaturen + nicht zugeordnet = {zahl(sd)} (Stadt {zahl(ty['stadt']['mfh'])}). Je dzielnica (OSM-Grenzen) "
      "nur in `daten/sanierung_odbl.js`.")
    w("")
    ab = ty["angebaut"]
    w(f"Angebaut (Hinweis, keine Regel; `pruefen/DS_protokoll.md`, Nachtrag 5): Kandidaten, deren Umriss auf mindestens "
      f"{dez(ab['grenze_min_m'])} m Länge an ein anderes Gebäude der BDOT10k grenzt (Toleranz {dez(ab['toleranz_m'])} m). "
      "Blockrandbebauung mit gemeinsamen Brandwänden ist typisch für kamienice, freistehende Blöcke sind es nicht. Stadt: "
      f"{zahl(ty['stadt']['blok_angebaut'])} von {zahl(ty['stadt']['blok'])} Kandidaten angebaut, in Großsiedlungen "
      f"{zahl(ty['stadt']['osiedle_angebaut'])} von {zahl(ty['stadt']['osiedle'])}. Je dzielnica:")
    w("")
    w("| dzielnica | Kandidaten | davon angebaut | Großsiedlung | davon angebaut |")
    w("|---|---|---|---|---|")
    for k, v in odbl["typologie_dzielnice"]["je_dzielnica"].items():
        w(f"| {k} | {zahl(v['blok'])} | {zahl(v['blok_angebaut'])} | {zahl(v['osiedle'])} | {zahl(v['osiedle_angebaut'])} |")
    w("")
    w("Grenze: Die Zahlen zählen die Merkmalskombination, keine Plattenbauten; sie sind weder Ober- noch Untergrenze "
      "und ungeprüft. Ohne Baujahr fallen rechteckige Wohnblöcke nach 1990 mit hinein, ebenso Mietshäuser "
      "(kamienice) der Blockrandbebauung mit mindestens 4 Geschossen, etwa im Stadtkern (dzielnica I: Altstadt, "
      "Kazimierz, Kleparz, Wesoła), und die Ziegelbauten des Sozialistischen Realismus in Nowa Huta. Plattenbauten "
      "mit unregelmäßigem Grundriss, aus mehreren Teilpolygonen oder mit weniger Nachbarn im Umkreis (lange "
      "Scheiben) fallen heraus. Bezug nur bibliographisch: "
      f"{LITERATUR['autoren']}, {LITERATUR['zeitschrift']} {LITERATUR['band']} ({LITERATUR['jahr']}) "
      f"{LITERATUR['artikel']}, DOI {LITERATUR['doi']}; keine Zahl daraus wird hier verwendet.")
    w("")
    sp = ty.get("sichtpruefung")
    w(f"Stichprobe zur Sichtprüfung (Startwert {STARTWERT}; Lage lon, lat; Delegatur; Geschosse). Prüfung am Luftbild "
      + ("**offen (Andre)**, deshalb keine Trefferquote:" if not sp else
         f"am {sp['datum']} (Andre, Ortofotomapa Geoportal, Gruppen verdeckt; Eingabe `belege/DS_sichtpruefung.json`):"))
    w("")
    for k, titel in (("osiedle", "Kandidat Großsiedlung"), ("kein_kandidat", "kein Kandidat, ≥ 4 Geschosse")):
        w(f"- {titel} ({len(stich[k])}): " + "; ".join(f"{lon}, {lat} ({de}, {g})" for lon, lat, de, g in stich[k]))
    w("")
    if sp:
        w("| Gruppe | gezogen | ja | nein | unklar | ja unter den entschiedenen | Wilson 95 % |")
        w("|---|---|---|---|---|---|---|")
        for k, titel in (("osiedle", "Kandidat Großsiedlung"), ("kein_kandidat", "Kontrolle: kein Kandidat")):
            z = sp[k]
            w(f"| {titel} | {z['n']} | {z['ja']} | {z['nein']} | {z['unklar']} | {dez(z['quote'])} % "
              f"({z['ja']} von {z['ja'] + z['nein']}) | {dez(z['wilson95'])} % |")
        w("")
        w("Bewertet wurde, ob am Luftbild ein Wohnblock zu sehen ist (Form, Lage, Umgebung), nicht die Bauweise; Großtafel "
          "und Ziegel lassen sich von oben nicht unterscheiden. Einzelergebnisse je Punkt sind nicht abgelegt. "
          "Bemerkungen des Prüfers: alle 5 Kandidaten mit „nein“ haben 4 oder 5 Geschosse und liegen in Krowodrza; unter "
          "den Kontrollen mit „ja“ sind Bauten in Nowa Huta mit 9 und 11 Geschossen.")
        w("")
        g = [x[3] for x in stich["osiedle"]]
        z = sp["osiedle"]
        w("Strengere Untergrenze der Geschosse, nachträglich an derselben Stichprobe gerechnet (keine Regeländerung; "
          "eine an der Stichprobe gewählte Grenze wäre an sie angepasst). „ja“ darunter: kleinster und größter möglicher "
          "Wert, weil die Einzelergebnisse fehlen.")
        w("")
        w("| Untergrenze Geschosse | Punkte der Stichprobe | „ja“ darunter | Kandidaten Großsiedlung in der Stadt |")
        w("|---|---|---|---|")
        for m, n_stadt in sorted(stich["osiedle_ab"].items()):
            bleibt = sum(1 for x in g if x >= m)
            w(f"| {m} | {bleibt} von {len(g)} | {max(0, z['ja'] - (len(g) - bleibt))}–{min(z['ja'], bleibt)} | "
              f"{zahl(n_stadt)} |")
        w("")
        w("Laut Prüfer haben alle 5 „nein“ 4 oder 5 Geschosse. Eine Untergrenze von 6 Geschossen entfernt sie also, "
          "entfernt aber auch mindestens so viele „ja“, wie die Tabelle zeigt, und senkt die Zahl der Kandidaten in der "
          "Stadt. Ob 5 Geschosse die Quote verbessert, lässt sich ohne Einzelergebnisse nicht sagen. Die Regel bleibt; "
          "eine nach dzielnica geschichtete Stichprobe ist offen.")
        w("")
    w("## Datenschutz")
    w("")
    w("In `daten/sanierung*.js` stehen keine Adresse, keine L.p., keine Gebäudekennung und kein Name. Punkte nur für "
      "Einträge ohne Anteil von Privatpersonen und ohne samoistne posiadanie; Rohtext der Spalte Własność nur unter "
      "`$KIEZ_DATEN/abgeleitet/sanierung/` (außerhalb des Repos). Die Liste nennt nur Adressen und Eigentumsklassen, "
      "keine Mieter.")
    w("")
    return "\n".join(L)


def tabelle_tsv(eintraege: list[dict]) -> str:
    spalten = ["lp", "seite", "name", "vorsatz", "nr", "ort", "rodzaj", "wlasnosc", "samoistne", "dzielnica", "art",
               "eig", "st", "nr_klasse", "vk", "link"]
    zeilen = ["\t".join(spalten)]
    for e in eintraege:
        zeilen.append("\t".join(str(e.get(k) if e.get(k) is not None else "").replace("\t", " ") for k in spalten))
    return "\n".join(zeilen) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pruefen", action="store_true")
    a = ap.parse_args()
    try:
        dateien, (eintraege, tsv) = rechnen()
    except FileNotFoundError as f:
        print(f"Eingang fehlt: {f}")
        return 2
    except ValueError as f:
        print(f"Befund: {f}")
        return 1
    if a.pruefen:
        abw = [p for p, t in dateien.items() if (WURZEL / p).read_text(encoding="utf-8") != t] \
            if all((WURZEL / p).exists() for p in dateien) else list(dateien)
        for p in dateien:
            print(("  ok    " if p not in abw else "  FEHLT ") + f"{p} byte-gleich")
        return 1 if abw else 0
    for p, t in dateien.items():
        (WURZEL / p).write_text(t, encoding="utf-8")
        print(f"geschrieben {p} ({len(t.encode('utf-8'))} B)")
    tsv.parent.mkdir(parents=True, exist_ok=True)
    tsv.write_text(tabelle_tsv(eintraege), encoding="utf-8")
    print(f"geschrieben {tsv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
