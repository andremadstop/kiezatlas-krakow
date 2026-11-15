"""Luft: Jahreskennwerte der amtlichen Messstationen in und um Kraków -> daten/powietrze.js.

Regeln stehen in pruefen/D7_protokoll.md (vor dem ersten Lauf festgelegt); dieses Skript setzt sie um und
schreibt die Zählung je Schritt nach belege/D7_luft_lauf.md.

Quelle (Handdownload, siehe quellen-D7.md): CSV-Export des EEA-Betrachters „Annual AQ statistics (AirBase &
e-Reporting merged)“ unter $KIEZ_DATEN/eingang/eea/*.csv. Fehlt er, rechnet das Skript mit erfundenen
Beispielzeilen im selben Format (Kennungen FIKCJA-…) und schreibt fixture: true. Gegenprobe, sobald vorhanden:
GIOŚ-Jahresstatistik unter $KIEZ_DATEN/eingang/gios/*.xlsx (nur Abgleich, ersetzt nichts).

Aufruf (Python aus der Projektumgebung, ohne Netz und ohne Datenbank):
    python -I skripte/32_powietrze.py              daten/powietrze.js und belege/D7_luft_lauf.md schreiben
    python -I skripte/32_powietrze.py --pruefen    beide neu erzeugen und byte-gleich vergleichen (Rückgabe 1 bei Abweichung)
    python -I skripte/32_powietrze.py --beispiel   Beispieldaten erzwingen, auch wenn ein Export vorliegt
Rückgabe: 0 gut, 1 Abweichung (--pruefen), 2 Eingabe unlesbar oder unvollständig.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

WURZEL = Path(__file__).resolve().parent.parent
AUSGABE = WURZEL / "daten" / "powietrze.js"
BELEG = WURZEL / "belege" / "D7_luft_lauf.md"

# ---------------------------------------------------------------- Festlegungen (pruefen/D7_protokoll.md)
JAHRE = list(range(2010, 2026))                    # Abschnitt 3
STADT = "Kraków"                                   # Abschnitt 2, Feld City
UMLAND_KM = 30.0                                   # Abschnitt 2
ERDRADIUS_KM = 6371.0
DECKUNG_MIN, DECKUNG_VOLL = 75.0, 85.0             # Abschnitt 4, Regeln 1 und 2
FLUESSE = {"E1a/validated data AQ e-Reporting", "Reporting within EoI/AirBase 8"}
FENSTER = {"przed": [2016, 2018], "przejscie": 2019, "po": [2020, 2022]}   # Abschnitt 5
# Feld -> (Schadstoff, DataAggregationProcess, Einheit, ganzzahlig)
KENNWERTE = {
    "pm10_srednia": ("PM10", "Annual mean / 1 calendar year", "µg/m³", False),
    "pm10_dni": ("PM10", "1 year day exceed 50", "dni", True),
    "pm25_srednia": ("PM2.5", "Annual mean / 1 calendar year", "µg/m³", False),
    "no2_srednia": ("NO2", "Annual mean / 1 calendar year", "µg/m³", False),
    "no2_godziny": ("NO2", "1 year hour exceed 200", "godziny", True),
}
# Rozporządzenie Ministra Środowiska w sprawie poziomów niektórych substancji w powietrzu, tekst jednolity
# Dz.U. 2021 poz. 845, Załącznik nr 1 (abgerufen 13.11.2026 über api.sejm.gov.pl, ELI-Status IN_FORCE)
_RZ = "Dz.U. 2021 poz. 845, załącznik nr 1"
GRENZWERTE = {
    "pm10_srednia": [{"wartosc": 40, "jednostka": "µg/m³", "okres": "rok kalendarzowy", "od_roku": 2005,
                      "fundstelle": _RZ + ", lp. 7"}],
    "pm10_dni": [{"wartosc": 50, "jednostka": "µg/m³", "okres": "24 godziny", "dopuszczalna_czestosc": 35,
                  "od_roku": 2005, "fundstelle": _RZ + ", lp. 7"}],
    "pm25_srednia": [{"wartosc": 25, "jednostka": "µg/m³", "okres": "rok kalendarzowy", "od_roku": 2015,
                      "faza": "I", "fundstelle": _RZ + ", lp. 6, przypis j"},
                     {"wartosc": 20, "jednostka": "µg/m³", "okres": "rok kalendarzowy", "od_roku": 2020,
                      "faza": "II", "fundstelle": _RZ + ", lp. 6, przypis k"}],
    "no2_srednia": [{"wartosc": 40, "jednostka": "µg/m³", "okres": "rok kalendarzowy", "od_roku": 2010,
                     "fundstelle": _RZ + ", lp. 2"}],
    "no2_godziny": [{"wartosc": 200, "jednostka": "µg/m³", "okres": "jedna godzina", "dopuszczalna_czestosc": 18,
                     "od_roku": 2010, "fundstelle": _RZ + ", lp. 2"}],
}
KONTEKST = {
    "akt": "Uchwała Nr XVIII/243/16 Sejmiku Województwa Małopolskiego z dnia 15 stycznia 2016 roku w sprawie "
           "wprowadzenia na obszarze Gminy Miejskiej Kraków ograniczeń w zakresie eksploatacji instalacji, "
           "w których następuje spalanie paliw",
    "publikacja": "Dziennik Urzędowy Województwa Małopolskiego, 1 lutego 2016 r., poz. 812",
    "wejscie_w_zycie": "2019-09-01",
    "cytat_wejscie": "Uchwała wchodzi w życie z dniem 1 września 2019 r.",
    "cytat_paliwa": "W instalacjach wskazanych w § 2 dopuszcza się wyłącznie stosowanie następujących rodzajów "
                    "paliw: 1) gazu ziemnego wysokometanowego lub zaazotowanego (w tym skroplonego gazu ziemnego), "
                    "propan-butanu, biogazu rolniczego lub innego rodzaju gazu palnego, 2) lekkiego oleju "
                    "opałowego",
    "url": "https://sprawyspoleczne.krakow.pl/zalacznik/424838",
    "zmiany_pozniejsze": "nie sprawdzono",
}
QUELLE = {
    "nazwa": "EEA, Air Quality e-Reporting: Air quality annual statistics calculated by the EEA",
    "pochodzenie": "Pomiary Państwowego Monitoringu Środowiska (GIOŚ) przekazane do EEA; wartości roczne "
                   "obliczone przez EEA",
    "licencja": "CC BY 4.0",
    "vermerk": "License CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Copyright holder: "
               "European Commission.",
    "metadane": "https://sdi.eea.europa.eu/catalogue/srv/api/records/6e191a3b-258d-491e-b636-6cbb15cf473b",
}
# Spalten des Betrachter-Exports, die das Skript braucht (Namen wie FieldOrder in viewer/init_aqstat.json;
# ob der CSV-Export genau diese Kopfzeile trägt: nicht geprüft, das Skript meldet fehlende Spalten)
SPALTEN = ["Country", "AirQualityStationEoICode", "AQStationName", "SamplingPoint", "AirPollutant",
           "DataAggregationProcess", "ReportingYear", "AirPollutionLevel", "DataCoverage", "SourceDataFlow",
           "potentialOutlier", "AirQualityStationType", "AirQualityStationArea", "Longitude", "Latitude", "City"]


class Eingabefehler(Exception):
    pass


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")


# ---------------------------------------------------------------- Eingaben
def eea_lesen(dateien: list[Path]) -> tuple[list[dict], list[dict]]:
    """CSV-Export(e) lesen; Rückgabe (Zeilen, Dateien mit Prüfsumme beim Lesen)."""
    zeilen, pliki = [], []
    for p in dateien:
        roh = p.read_bytes()
        pliki.append({"nazwa": p.name, "sha256": hashlib.sha256(roh).hexdigest()})
        text = roh.decode("utf-8-sig")
        kopf = text.splitlines()[0] if text else ""
        trenner = ";" if kopf.count(";") > kopf.count(",") else ","
        leser = csv.DictReader(io.StringIO(text), delimiter=trenner)
        fehlt = [s for s in SPALTEN if s not in [f.strip() for f in (leser.fieldnames or [])]]
        if fehlt:
            raise Eingabefehler(f"{p.name}: Spalten fehlen: {', '.join(fehlt)}; Kopf: {kopf[:300]}")
        for z in leser:
            zeilen.append({(k or "").strip(): (v or "").strip() for k, v in z.items()})
    return zeilen, pliki


def zahl(s: str) -> float | None:
    s = (s or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def beispiel_zeilen() -> list[dict]:
    """Erfundene Zeilen im Exportformat. Werte sind Formeln, keine Messungen; Lage um karte.mitte der Ortskonfiguration."""
    sys.path.insert(0, str(WURZEL / "skripte"))
    import ort_konfig
    lon0, lat0 = ort_konfig.lade()["karte"]["mitte"]
    stationen = [  # Kennung, Rolle (für City), Versatz Breite/Länge in Grad, Typ, Gebiet
        ("FIKCJA-M1", STADT, 0.00, 0.00, "Traffic", "Urban"),
        ("FIKCJA-M2", STADT, 0.03, -0.05, "Background", "Urban"),
        ("FIKCJA-M3", STADT, -0.02, 0.08, "Industrial", "Urban"),
        ("FIKCJA-M4", STADT, 0.04, 0.02, "Background", "Suburban"),
        ("FIKCJA-O1", "", 0.12, -0.15, "Background", "Rural"),
        ("FIKCJA-O2", "", -0.15, 0.10, "Background", "Suburban"),
        ("FIKCJA-D1", "", 0.60, 0.60, "Background", "Rural"),     # weiter als 30 km: fällt heraus
    ]
    aus = []
    for si, (kod, city, dlat, dlon, typ, obszar) in enumerate(stationen):
        for jahr in range(2009, 2027):
            for feld, (stoff, agg, _e, ganz) in KENNWERTE.items():
                if kod == "FIKCJA-M4" and jahr == 2017:
                    continue                                       # Lücke: Vorher-Fenster unvollständig
                basis = {"pm10_srednia": 60, "pm10_dni": 120, "pm25_srednia": 40, "no2_srednia": 45,
                         "no2_godziny": 30}[feld] * (0.55 if city == "" else 1.0)
                wert = basis * (1 - 0.035 * (jahr - 2009)) * (1 + 0.04 * si)
                deckung, fluss, ausreisser = 95.0, "E1a/validated data AQ e-Reporting", "N"
                if jahr < 2013:
                    fluss = "Reporting within EoI/AirBase 8"
                if jahr == 2026:
                    fluss = "E2a/UTD AQ e-Reporting"
                if kod == "FIKCJA-M2" and jahr == 2014:
                    deckung = 70.0                                 # Regel 1: verworfen
                if kod == "FIKCJA-M3" and jahr == 2021:
                    deckung = 80.0                                 # Regel 2: niepelne
                if kod == "FIKCJA-O1" and jahr == 2012 and feld == "no2_srednia":
                    ausreisser = "Y"                               # Regel 3
                zeile = {"Country": "Poland", "AirQualityStationEoICode": kod, "AQStationName": f"Stacja {kod}",
                         "SamplingPoint": f"SPO-{kod}-{stoff}-1", "AirPollutant": stoff,
                         "DataAggregationProcess": agg, "ReportingYear": str(jahr),
                         "AirPollutionLevel": str(round(wert) if ganz else round(wert, 3)),
                         "DataCoverage": str(deckung), "SourceDataFlow": fluss, "potentialOutlier": ausreisser,
                         "AirQualityStationType": typ, "AirQualityStationArea": obszar,
                         "Longitude": f"{lon0 + dlon:.5f}", "Latitude": f"{lat0 + dlat:.5f}", "City": city}
                aus.append(zeile)
                if kod == "FIKCJA-M1" and jahr == 2018 and feld == "pm10_srednia":   # Regel 4: Dublette
                    aus.append({**zeile, "SamplingPoint": f"SPO-{kod}-{stoff}-2", "DataCoverage": "90.0",
                                "AirPollutionLevel": str(round(wert * 1.1, 3))})
        aus.append({**aus[-1], "AirPollutant": "O3", "DataAggregationProcess": "Annual mean / 1 calendar year"})
    return aus


# ---------------------------------------------------------------- Rechnung
def haversine(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * ERDRADIUS_KM * math.asin(math.sqrt(a))


def geojson_lesen(dateien: list[Path]) -> tuple[list[dict], list[dict]]:
    """GeoJSON-Export(e) des Betrachters lesen, auch als ZIP (Abweichung 2 in pruefen/D7_protokoll.md).

    Feldnamen wie im CSV; SamplingPoint fehlt und wird durch AssessmentMethodId ersetzt, potentialOutlier fehlt
    und bleibt leer. Rückgabe wie eea_lesen.
    """
    zeilen, pliki = [], []
    for p in dateien:
        roh = p.read_bytes()
        pliki.append({"nazwa": p.name, "sha256": hashlib.sha256(roh).hexdigest()})
        if p.name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(roh)) as z:
                namen = sorted(n for n in z.namelist() if n.lower().endswith(".geojson"))
                if len(namen) != 1:
                    raise Eingabefehler(f"{p.name}: erwartet genau eine .geojson-Datei, gefunden {namen}")
                roh = z.read(namen[0])
        try:
            merkmale = json.loads(roh.decode("utf-8-sig"))["features"]
        except (ValueError, KeyError, TypeError) as e:
            raise Eingabefehler(f"{p.name}: kein lesbares GeoJSON ({e})") from None
        pflicht = [s for s in SPALTEN if s not in ("SamplingPoint", "potentialOutlier")] + ["AssessmentMethodId"]
        for m in merkmale:
            pr = m.get("properties") or {}
            fehlt = [s for s in pflicht if s not in pr]
            if fehlt:
                raise Eingabefehler(f"{p.name}: Felder fehlen: {', '.join(fehlt)}")
            z = {k: ("" if v is None else str(v)).strip() for k, v in pr.items()}
            z["SamplingPoint"] = z.get("SamplingPoint") or z["AssessmentMethodId"]
            z.setdefault("potentialOutlier", "")
            zeilen.append(z)
    return zeilen, pliki


def rechnen(zeilen: list[dict]) -> tuple[dict, dict]:
    z = {"zeilen_gesamt": len(zeilen)}
    if zeilen and all("potentialOutlier" in r and r["potentialOutlier"] == "" for r in zeilen) and \
            any("AssessmentMethodId" in r for r in zeilen):
        z["ausreisser_nicht_geliefert"] = True
    namen = {}
    for r in zeilen:
        if r.get("AQStationName"):
            namen.setdefault(r["AirQualityStationEoICode"], r["AQStationName"])
    feld_von = {(s, a): f for f, (s, a, _e, _g) in KENNWERTE.items()}
    verworfen = {k: 0 for k in ("land", "kennwert", "jahr", "datenfluss", "deckung", "ausreisser", "wert",
                                "koordinate", "entfernung", "dublette")}
    kandidaten = []
    for r in zeilen:
        if r["Country"] != "Poland":
            verworfen["land"] += 1; continue
        feld = feld_von.get((r["AirPollutant"], r["DataAggregationProcess"]))
        if feld is None:
            verworfen["kennwert"] += 1; continue
        jahr = int(zahl(r["ReportingYear"]) or 0)
        if jahr not in JAHRE:
            verworfen["jahr"] += 1; continue
        if r["SourceDataFlow"] not in FLUESSE:
            verworfen["datenfluss"] += 1; continue
        deckung = zahl(r["DataCoverage"])
        if deckung is None or deckung < DECKUNG_MIN:
            verworfen["deckung"] += 1; continue
        if r["potentialOutlier"].upper() in ("Y", "YES", "TRUE", "1"):
            verworfen["ausreisser"] += 1; continue
        wert = zahl(r["AirPollutionLevel"])
        if wert is None:
            verworfen["wert"] += 1; continue
        lat, lon = zahl(r["Latitude"]), zahl(r["Longitude"])
        if lat is None or lon is None:
            verworfen["koordinate"] += 1; continue
        kandidaten.append((r, feld, jahr, deckung, wert, lat, lon))

    stadt_kod = {r["AirQualityStationEoICode"] for r, *_x in kandidaten if r["City"] == STADT}
    if not stadt_kod:
        raise Eingabefehler(f"keine gültige Zeile mit City = {STADT}")
    # Mittelpunkt über die Stationen (nicht über die Zeilen): je Station die erste gültige Koordinate
    erste = {}
    for r, *_x, lat, lon in kandidaten:
        erste.setdefault(r["AirQualityStationEoICode"], (lat, lon))
    mlat = sum(erste[k][0] for k in stadt_kod) / len(stadt_kod)
    mlon = sum(erste[k][1] for k in stadt_kod) / len(stadt_kod)

    beste: dict[tuple, tuple] = {}
    stationen: dict[str, dict] = {}
    for r, feld, jahr, deckung, wert, lat, lon in kandidaten:
        kod = r["AirQualityStationEoICode"]
        km = haversine(mlat, mlon, *erste[kod])
        rola = "miasto" if kod in stadt_kod else ("okolica" if km <= UMLAND_KM else None)
        if rola is None:
            verworfen["entfernung"] += 1; continue
        stationen.setdefault(kod, {"kod": kod, "nazwa": namen.get(kod) or r["AQStationName"], "rola": rola,
                                        "typ": r["AirQualityStationType"], "obszar": r["AirQualityStationArea"],
                                        "lat": round(erste[kod][0], 5), "lon": round(erste[kod][1], 5),
                                        "odleglosc_km": round(km, 1)})
        schluessel = (kod, feld, jahr)
        neu = (deckung, r["SamplingPoint"], wert)
        alt = beste.get(schluessel)
        if alt is not None:
            verworfen["dublette"] += 1
            # höchste Deckung, bei Gleichstand der lexikografisch kleinste SamplingPoint (Regel 4)
            if not (neu[0] > alt[0] or (neu[0] == alt[0] and neu[1] < alt[1])):
                continue
        beste[schluessel] = neu

    for (kod, feld, jahr), (deckung, _sp, wert) in sorted(beste.items()):
        ganz = KENNWERTE[feld][3]
        eintrag = {"w": round(wert) if ganz else round(wert, 1), "pokrycie": round(deckung, 1)}
        if deckung < DECKUNG_VOLL:
            eintrag["niepelne"] = True
        stationen[kod].setdefault("serie", {}).setdefault(feld, {})[str(jahr)] = eintrag

    for st in stationen.values():
        st["przed_po"] = {}
        for feld in sorted(st.get("serie", {})):
            s = st["serie"][feld]
            fenster = {}
            for name in ("przed", "po"):
                a, b = FENSTER[name]
                # ungerundete Werte (Regel 5: Rundung erst bei der Ausgabe), nur Jahre mit gültigem Wert
                werte = [beste[(st["kod"], feld, j)][2] if str(j) in s else None for j in range(a, b + 1)]
                fenster[name] = round(sum(werte) / len(werte), 1) if all(w is not None for w in werte) else None
            if fenster["przed"] is None or fenster["po"] is None:
                fenster["powod"] = "brak_pelnego_okna"
            st["przed_po"][feld] = fenster

    liste = sorted(stationen.values(), key=lambda s: (s["rola"] != "miasto", s["odleglosc_km"], s["kod"]))
    z["verworfen"] = verworfen
    z["werte_verwendet"] = len(beste)
    z["stationen"] = {"miasto": sum(s["rola"] == "miasto" for s in liste),
                      "okolica": sum(s["rola"] == "okolica" for s in liste)}
    z["przed_po_pelne"] = sum(1 for s in liste for f in s["przed_po"].values() if "powod" not in f)
    z["przed_po_brak"] = sum(1 for s in liste for f in s["przed_po"].values() if "powod" in f)
    z["niepelne"] = sum(1 for s in liste for f in s.get("serie", {}).values() for e in f.values() if e.get("niepelne"))
    z["srodek_stacji_miejskich"] = [round(mlon, 5), round(mlat, 5)]
    return {"stacje": liste}, z


# ---------------------------------------------------------------- Gegenprobe GIOŚ (xlsx, Format nicht geprüft)
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def xlsx_zeilen(p: Path) -> dict[str, list[list[str]]]:
    """Blattname -> Zeilen (Zeichenketten), nur Standardbibliothek."""
    with zipfile.ZipFile(p) as z:
        geteilt = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
                geteilt.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        mappe = ET.fromstring(z.read("xl/workbook.xml"))
        namen = [b.get("name") for b in mappe.find("m:sheets", NS)]
        aus = {}
        for i, name in enumerate(namen, 1):
            pfad = f"xl/worksheets/sheet{i}.xml"
            if pfad not in z.namelist():
                continue
            zeilen = []
            for row in ET.fromstring(z.read(pfad)).iter(f"{{{NS['m']}}}row"):
                zeile = {}
                for c in row.findall("m:c", NS):
                    spalte = re.match(r"[A-Z]+", c.get("r", "A")).group(0)
                    v = c.find("m:v", NS)
                    t = c.get("t")
                    if t == "s" and v is not None:
                        wert = geteilt[int(v.text)]
                    elif t == "inlineStr":
                        wert = "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
                    else:
                        wert = v.text if v is not None else ""
                    zeile[spalte] = wert
                if zeile:
                    breite = max(_spalte_nr(s) for s in zeile)
                    zeilen.append([zeile.get(_spalte_name(k), "") for k in range(1, breite + 1)])
            aus[name] = zeilen
        return aus


def _spalte_nr(s: str) -> int:
    n = 0
    for c in s:
        n = n * 26 + ord(c) - 64
    return n


def _spalte_name(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def gios_gegenprobe(ordner: Path) -> list[str]:
    """Zeilen für den Beleg. Liest nur, gleicht nichts automatisch ab, solange das Format nicht geprüft ist."""
    dateien = sorted(ordner.glob("*.xlsx")) if ordner.is_dir() else []
    if not dateien:
        return ["- GIOŚ-Gegenprobe: nicht geprüft (keine Datei unter `eingang/gios/`)."]
    aus = []
    for p in dateien:
        try:
            blaetter = xlsx_zeilen(p)
        except (zipfile.BadZipFile, KeyError, ET.ParseError) as e:
            aus.append(f"- `{p.name}`: nicht lesbar ({type(e).__name__}).")
            continue
        for name, zeilen in blaetter.items():
            kopf = next((z for z in zeilen if sum(1 for x in z if x.strip()) >= 3), [])
            aus.append(f"- `{p.name}`, Blatt „{name}“: {len(zeilen)} Zeilen, erste Kopfzeile: "
                       f"{' | '.join(x for x in kopf[:12] if x)}")
    aus.append("- Abgleich der Werte: nicht geprüft (Spaltenbelegung erst nach Sichtung festlegen, als Abweichung im Protokoll).")
    return aus


# ---------------------------------------------------------------- Ausgabe
def bauen(beispiel_erzwingen: bool) -> tuple[str, str]:
    ordner = daten_ordner() / "eingang" / "eea"
    dateien = sorted(ordner.glob("*.csv")) if ordner.is_dir() and not beispiel_erzwingen else []
    gj = sorted([*ordner.glob("*.geojson"), *ordner.glob("*.geojson.zip")]) \
        if ordner.is_dir() and not beispiel_erzwingen else []
    if dateien or gj:
        zeilen, pliki = eea_lesen(dateien) if dateien else ([], [])
        z2, p2 = geojson_lesen(gj)
        zeilen, pliki, dateien = zeilen + z2, pliki + p2, dateien + gj
        fixture = False
    else:
        zeilen, pliki, fixture = beispiel_zeilen(), [], True
    ergebnis, z = rechnen(zeilen)
    daten = {}
    if fixture:
        daten["fixture"] = True
    daten.update({
        "quelle": {**QUELLE, "pliki": pliki},
        "abzeichen": "orientacyjnie",
        "lata": JAHRE,
        "okna": FENSTER,
        "kennwerte": {f: {"zanieczyszczenie": s, "agregacja": a, "jednostka": e}
                      for f, (s, a, e, _g) in KENNWERTE.items()},
        "bez_wartosci": {"pm25_dni": "brak_dobowego_poziomu_dopuszczalnego"},
        "grenzwerte": GRENZWERTE,
        "kontekst": KONTEKST,
        "reguly": {"miasto": f"City = {STADT}", "okolica_km": UMLAND_KM, "pokrycie_min": DECKUNG_MIN,
                   "pokrycie_pelne": DECKUNG_VOLL, "srodek": z["srodek_stacji_miejskich"]},
        "stacje": ergebnis["stacje"],
        "zaehlung": {k: v for k, v in z.items() if k != "srodek_stacji_miejskich"},
    })
    umland = any(s["rola"] != "miasto" for s in ergebnis["stacje"])
    kopf = ("/* Luft: Jahreskennwerte der Messstationen " + ("in und um Kraków" if umland else "in Kraków")
            + ". Erzeugt von skripte/32_powietrze.py, "
            "nicht von Hand ändern. Quelle: EEA (Daten GIOŚ), CC BY 4.0."
            + (" BEISPIELDATEN: erfundene Werte und Stationen." if fixture else "") + " */\n")
    js = kopf + "window.KIEZ_POWIETRZE=" + json.dumps(daten, ensure_ascii=False, sort_keys=True,
                                                      separators=(",", ":")) + ";\n"
    return js, beleg_text(daten, z, fixture, dateien)


def beleg_text(daten: dict, z: dict, fixture: bool, dateien: list[Path]) -> str:
    v = z["verworfen"]
    summe = z["werte_verwendet"] + sum(v.values())
    zeilen = [
        "# Luft: Zählung des letzten Laufs (erzeugt von `skripte/32_powietrze.py`, nicht von Hand ändern)",
        "",
        ("**Beispieldaten** (`fixture: true`): Stationen `FIKCJA-…` und alle Werte sind erfunden; die Zählung "
         "belegt nur, dass die Regeln aus `pruefen/D7_protokoll.md` greifen." if fixture else
         "Eingabe: " + ", ".join(f"`eingang/eea/{p.name}`" for p in dateien) + "; Prüfsummen beim Lesen in "
         "`daten/powietrze.js` (`quelle.pliki`)."),
        "",
        "## Zeilen je Schritt",
        "",
        "| Schritt | Zeilen |",
        "|---|---|",
        f"| Eingabe gesamt | {z['zeilen_gesamt']} |",
        f"| verworfen: Land nicht Polen | {v['land']} |",
        f"| verworfen: anderer Schadstoff oder Kennwert | {v['kennwert']} |",
        f"| verworfen: Jahr außerhalb {JAHRE[0]}–{JAHRE[-1]} | {v['jahr']} |",
        f"| verworfen: Datenfluss nicht validiert (E2a u. a.) | {v['datenfluss']} |",
        f"| verworfen: Deckung unter {DECKUNG_MIN:g} % oder leer | {v['deckung']} |",
        f"| verworfen: potentialOutlier{' (Feld im Export nicht geliefert, Regel greift nicht; Abweichung 2)' if z.get('ausreisser_nicht_geliefert') else ''} | {v['ausreisser']} |",
        f"| verworfen: Wert leer | {v['wert']} |",
        f"| verworfen: Koordinate leer | {v['koordinate']} |",
        f"| verworfen: weiter als {UMLAND_KM:g} km und nicht {STADT} | {v['entfernung']} |",
        f"| verworfen: Dublette (zweiter Messpunkt) | {v['dublette']} |",
        f"| **verwendet** (Station × Kennwert × Jahr) | {z['werte_verwendet']} |",
        f"| Summe verwendet + verworfen | {summe} |",
        "",
        "## Ergebnis",
        "",
        (f"- Stationen: {z['stationen']['miasto']} in {STADT}, {z['stationen']['okolica']} im Umland (≤ {UMLAND_KM:g} km "
         f"vom Mittel der Stadt-Stationen, Länge/Breite {z['srodek_stacji_miejskich'][0]} / {z['srodek_stacji_miejskich'][1]})."),
        f"- Werte mit Deckung {DECKUNG_MIN:g}–{DECKUNG_VOLL:g} % (gekennzeichnet `niepelne`): {z['niepelne']}.",
        (f"- Vorher/Nachher ({FENSTER['przed'][0]}–{FENSTER['przed'][1]} gegen {FENSTER['po'][0]}–{FENSTER['po'][1]}, "
         f"Übergang {FENSTER['przejscie']}): {z['przed_po_pelne']} Paare vollständig, {z['przed_po_brak']} ohne volles Fenster (`null`)."),
        "",
        "## Gegenprobe GIOŚ",
        "",
        *gios_gegenprobe(daten_ordner() / "eingang" / "gios"),
        "",
    ]
    return "\n".join(zeilen)


def main(argv: list[str]) -> int:
    pruefen = "--pruefen" in argv
    try:
        js, beleg = bauen("--beispiel" in argv)
    except Eingabefehler as e:
        print(f"Eingabe: {e}", file=sys.stderr)
        return 2
    if pruefen:
        abw = [p.relative_to(WURZEL).as_posix() for p, t in ((AUSGABE, js), (BELEG, beleg))
               if not p.exists() or p.read_text(encoding="utf-8") != t]
        print("aktuell: daten/powietrze.js, belege/D7_luft_lauf.md" if not abw else f"nicht aktuell: {', '.join(abw)}")
        return 1 if abw else 0
    AUSGABE.write_text(js, encoding="utf-8")
    BELEG.write_text(beleg, encoding="utf-8")
    print(f"geschrieben: {AUSGABE.relative_to(WURZEL)} ({len(js.encode())} Byte), {BELEG.relative_to(WURZEL)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
