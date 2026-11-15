"""ÖPNV-Haltestellen in Kraków mit Verkehrsmittel und Taktklasse aus dem GTFS der ZTP (Bus, Tram, Mobilis).

Kein Netz, keine Datenbank. Regeln vor dem Lauf: pruefen/D6_protokoll.md (Regeln 1–7). Alle Werte (Feeds, Stichtag,
Fenster, Klassengrenzen, Puffer) stehen in config/richtwerte.yaml, Abschnitt oepnv.

Eingang:  $KIEZ_DATEN/<oepnv.gtfs.*>                GTFS-Zips der ZTP (CC BY 4.0), direkt aus dem Zip gestreamt
          $KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip   BDOT10k, Gemeindegrenze aus OT_ADJA_A
          (kein st: die Zuordnung zur dzielnica beruht auf den OSM-Grenzen und steht nach der Entscheidung vom
                                                    13.11.2026 (Lizenzfolge, Variante a) nur in _odbl-Dateien; die
                                                    Seite holt st über daten/zellen_odbl.js)
Ausgang:  daten/haltestellen.js   (window.KIEZ_HALTESTELLEN, Vertrag daten/schema/haltestellen.json)
          belege/D6_oepnv.md      Zählungen je Schritt, Gegenprobe Fahrten und Freitag 13.11.2026

Taktklasse: Abfahrten je Stunde in der stärkeren Richtung im Fenster, gemessen an den Untergrenzen I/II/III. Das ist
eine eigene Klassifikation nach dem Muster des Kiezatlas Potsdam ohne polnische Fundstelle (Status orientierung).

Aufruf:
    uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
        python -I skripte/13_oepnv_krakow.py [--pruefen]
--pruefen rechnet neu und vergleicht beide Ausgaben byte-genau, ohne zu schreiben (Rückgabe 1 bei Abweichung).
"""
from __future__ import annotations

import argparse
import csv
import io
import math
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

import yaml
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.prepared import prep

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import versorgung_werkzeug as vw  # noqa: E402

AUS_JS = vw.DATEN / "haltestellen.js"
AUS_BELEG = vw.WURZEL / "belege" / "D6_oepnv.md"
BDOT = "2026-11-13/03_gebaeude/1261_SHP.zip"
KLASSEN = ("I", "II", "III", "unter III")


def verkehrsmittel_von(route_type: int) -> str:
    if route_type == 0 or 900 <= route_type < 1000:
        return "tram"
    if route_type == 3 or 700 <= route_type < 800:
        return "bus"
    return "sonstige"


def sekunden(hhmmss: str) -> int:
    h, m, s = hhmmss.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def lies(z: zipfile.ZipFile, name: str):
    with z.open(name) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline=""))


def dienste_am(z: zipfile.ZipFile, tag: date) -> set[str]:
    """service_id, die am Tag fahren: calendar (Wochentag, Zeitraum) plus/minus calendar_dates."""
    wt = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")[tag.weekday()]
    t = tag.strftime("%Y%m%d")
    aktiv = {r["service_id"] for r in lies(z, "calendar.txt") if r[wt] == "1" and r["start_date"] <= t <= r["end_date"]}
    for r in lies(z, "calendar_dates.txt"):
        if r["date"] == t:
            (aktiv.add if r["exception_type"] == "1" else aktiv.discard)(r["service_id"])
    return aktiv


def meter(lon0, lat0, lon1, lat1) -> float:
    """Kugelabstand (nur für die Streuungsprüfung der Steige; Abstände der Auswertung rechnen im Rechen-System)."""
    r = 6371008.8
    p0, p1 = math.radians(lat0), math.radians(lat1)
    a = math.sin((p1 - p0) / 2) ** 2 + math.cos(p0) * math.cos(p1) * math.sin(math.radians(lon1 - lon0) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def zaehle_tag(feeds: dict, tag: date, fenster: tuple[int, int], steig_zu: dict):
    """Je Haltestelle: Verkehrsmittel mit Abfahrten am Tag und Fahrten im Fenster je Richtung. Dazu Fahrten je Feed."""
    von, bis = fenster
    abfahrt_tag: dict[str, set[str]] = defaultdict(set)
    im_fenster: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    fahrten_je_feed, sonstige = {}, Counter()
    for k, z in feeds.items():
        art = {r["route_id"]: verkehrsmittel_von(int(r["route_type"])) for r in lies(z, "routes.txt")}
        sonstige.update(a for a in art.values() if a == "sonstige")
        heute, gestern = dienste_am(z, tag), dienste_am(z, tag - timedelta(days=1))
        fahrt = {}
        for r in lies(z, "trips.txt"):
            if r["service_id"] in heute:
                fahrt[r["trip_id"]] = (r["route_id"], r["direction_id"], True)
            elif r["service_id"] in gestern:
                fahrt[r["trip_id"]] = (r["route_id"], r["direction_id"], False)
        fahrten_je_feed[k] = sum(1 for v in fahrt.values() if v[2])
        letzte: dict[str, int] = {}
        halte = []
        for r in lies(z, "stop_times.txt"):
            t = r["trip_id"]
            if t not in fahrt:
                continue
            seq = int(r["stop_sequence"])
            if seq > letzte.get(t, -1):
                letzte[t] = seq
            halte.append((t, f"{k}:{r['stop_id']}", seq, r.get("pickup_type") or "0",
                          sekunden(r["departure_time"] or r["arrival_time"])))
        for t, sid, seq, pickup, sek in halte:
            if pickup == "1" or seq == letzte[t]:
                continue
            route, richtung, ist_heute = fahrt[t]
            h = steig_zu[sid]
            s = sek if ist_heute else sek - 86400
            if ist_heute:
                abfahrt_tag[h].add(art[route])
            if von <= s < bis:
                im_fenster[h][richtung].add(f"{k}:{t}")
    return abfahrt_tag, im_fenster, fahrten_je_feed, sonstige


def klasse_von(f: float, grenzen: list[tuple[str, float]]) -> str:
    return next((k for k, g in grenzen if f >= g), "unter III")


def rechnen() -> tuple[str, str]:
    rw = yaml.safe_load(ort_konfig.RICHTWERTE.read_text(encoding="utf-8"))
    oe, q = rw["oepnv"], rw["quellen"]["ztp"]
    m = oe["messung"]
    tag, tag2 = date.fromisoformat(str(m["stichtag"])), date.fromisoformat(str(m["gegenprobe_tag"]))
    fenster = tuple(sekunden(x + ":00") for x in m["hvz_fenster"])
    stunden = (fenster[1] - fenster[0]) / 3600
    grenzen = sorted(((k, float(oe["taktklassen"][k]["fahrten_hvz_je_richtung_min"])) for k in KLASSEN[:3]),
                     key=lambda kv: -kv[1])
    daten = vw.kiez_daten()
    feeds = {k: zipfile.ZipFile(daten / p) for k, p in oe["gtfs"].items()}
    b: list[str] = []   # Beleg-Zeilen

    # 1. Steige → Haltestelle (Stamm des stop_code)
    steig_zu, lage, namen, feeds_je_h, steige_je_feed = {}, defaultdict(list), defaultdict(set), defaultdict(set), {}
    for k, z in feeds.items():
        n = 0
        for s in lies(z, "stops.txt"):
            if (s.get("location_type") or "0") != "0":
                continue
            n += 1
            h = s["stop_code"].split("-")[0]
            steig_zu[f"{k}:{s['stop_id']}"] = h
            lage[h].append((float(s["stop_lon"]), float(s["stop_lat"])))
            namen[h].add(s["stop_name"])
            feeds_je_h[h].add(k)
        steige_je_feed[k] = n
    mehrnamig = sorted(h for h in namen if len(namen[h]) > 1)
    mitte = {h: (sum(p[0] for p in v) / len(v), sum(p[1] for p in v) / len(v)) for h, v in lage.items()}
    streu = sum(1 for h, v in lage.items() for p in v if meter(*p, *mitte[h]) > float(m["streuung_warn_m"]))
    if mehrnamig:
        raise SystemExit(f"Befund: Haltestellen-Stämme mit mehreren Namen: {mehrnamig[:10]}")

    # 2. Abfahrten zählen (Stichtag und Gegenprobe-Tag)
    tage = {}
    for t in (tag, tag2):
        tage[t] = zaehle_tag(feeds, t, fenster, steig_zu)
    abfahrt_tag, im_fenster, fahrten, sonstige = tage[tag]
    soll = {k: int(v) for k, v in oe["fahrten_gegenprobe"].items()}
    if fahrten != soll:
        raise SystemExit(f"Befund (Abbruchregel 3): Fahrten am {tag} {fahrten}, Gegenprobe {soll}")

    def werte(af, imf):
        aus = {}
        for h in af:
            je = max((len(v) for v in imf[h].values()), default=0) / stunden
            aus[h] = (round(je, 1), klasse_von(je, grenzen))
        return aus
    w1, w2 = werte(abfahrt_tag, im_fenster), werte(tage[tag2][0], tage[tag2][1])

    # 3. Lage zur Gemeinde
    gem_r, gem_w = vw.gemeinde_krakow(daten / BDOT)
    puffer = float(m["randpuffer_m"])
    nach_r = Transformer.from_crs(vw.WGS84, vw.RECHEN, always_xy=True)
    gem_p, gem_puffer = prep(gem_r), prep(gem_r.buffer(puffer))

    # 4. Stadtteile: nie in dieser Datei (ohne _odbl im Namen). st der Zelle beruht auf den OSM-Grenzen; nach der
    # Entscheidung vom 13.11.2026 stehen solche Werte nur in _odbl-Dateien (daten/zellen_odbl.js).
    z_pfad = vw.DATEN / "zellen_odbl.js"
    st_echt = False
    st_flaechen = []
    if st_echt:
        for f in vw.js_lesen(z_pfad)["features"]:
            st_flaechen.append((f["properties"].get("st"), prep(shape(f["geometry"]))))

    features, weg_puffer, lage_zaehl = [], 0, Counter()
    for h in sorted(abfahrt_tag, key=lambda x: (len(x), x)):
        lon, lat = mitte[h]
        pr = Point(*nach_r.transform(lon, lat))
        if gem_p.contains(pr):
            in_stadt = True
        elif gem_puffer.contains(pr):
            in_stadt = False
        else:
            weg_puffer += 1
            continue
        st = None
        if st_echt and in_stadt:
            pw = Point(lon, lat)
            st = next((nr for nr, g in st_flaechen if g.contains(pw)), None)
        f, k = w1[h]
        vm = "+".join(sorted(abfahrt_tag[h]))
        lage_zaehl[(in_stadt, k)] += 1
        features.append({"type": "Feature",
                         "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
                         "properties": {"id": h, "name": sorted(namen[h])[0], "verkehrsmittel": vm,
                                        "fahrten_hvz_je_richtung": f, "taktklasse": k, "in_stadt": in_stadt,
                                        "st": st}})

    stand = str(rw["stand"])
    inhalt = {
        "type": "FeatureCollection", "stand": stand,
        "stichtag": tag.isoformat(), "fenster": list(m["hvz_fenster"]),
        "haltestelle": "stamm_des_codes", "lage": "mittel_der_steige",
        "st_ueber": None if st_echt else "zellen_odbl",
        "klassen": {"status": oe["taktklassen"]["status"], "mass": "abfahrten_je_stunde_staerkere_richtung",
                    "vorbehalte": ["eigene_klassifikation_takt"],
                    "grenzen": {k: float(oe["taktklassen"][k]["fahrten_hvz_je_richtung_min"]) for k in KLASSEN[:3]}},
        "quellen": {"ztp": {kk: q[kk] for kk in ("quelle", "lizenz", "vermerk", "url")} | {"stand": stand}},
        "features": features,
    }
    kopf = (f"Haltestellen mit Taktklasse, erzeugt von skripte/13_oepnv_krakow.py. Quelle: {q['vermerk']}. "
            "Gemeindegrenze: Główny Urząd Geodezji i Kartografii, BDOT10k.")
    js = vw.js_text("KIEZ_HALTESTELLEN", inhalt, kopf)

    # Beleg
    T = vw.tausender
    b += ["# Beleg ÖPNV-Haltestellen und Taktklasse", "",
          "Erzeugt von `skripte/13_oepnv_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). "
          "Regeln vor dem Lauf: `pruefen/D6_protokoll.md`, Regeln 1–7. Eingaben und Prüfsummen: "
          "`belege/rohdaten-D6-2026-11-13.sha256`.", "",
          f"Stichtag {tag.strftime('%d.%m.%Y')} (Mittwoch), Fenster {m['hvz_fenster'][0]} bis {m['hvz_fenster'][1]} Uhr, "
          f"Gegenprobe-Tag {tag2.strftime('%d.%m.%Y')} (Freitag).", "",
          "## Schritt 1: Steige und Haltestellen", "",
          "| Feed | Steige (`stops.txt`, location_type 0) |", "|---|---|"]
    b += [f"| {k} | {T(n)} |" for k, n in steige_je_feed.items()]
    b += ["", f"- Haltestellen (Stämme des `stop_code`): {T(len(lage))}",
          f"- davon in mehr als einem Feed: {T(sum(1 for v in feeds_je_h.values() if len(v) > 1))}",
          f"- Stämme mit mehr als einem Namen: {len(mehrnamig)} (Befund wäre > 0)",
          f"- Steige weiter als {m['streuung_warn_m']} m vom Mittelpunkt ihres Stamms: {T(streu)}", "",
          "## Schritt 2: Fahrten am Stichtag (Abbruchregel 3)", "",
          "| Feed | Fahrten gezählt | Gegenprobe Machbarkeit | gleich |", "|---|---|---|---|"]
    b += [f"| {k} | {T(fahrten[k])} | {T(soll[k])} | {'ja' if fahrten[k] == soll[k] else 'nein'} |" for k in soll]
    b += ["", f"- Linien mit `route_type` außerhalb von Bus und Tram: {sum(sonstige.values())}",
          f"- Haltestellen mit mindestens einer Abfahrt am Stichtag: {T(len(abfahrt_tag))}",
          f"- ohne Abfahrt (fallen weg): {T(len(lage) - len(abfahrt_tag))}", "",
          "## Schritt 3: Lage zur Gemeinde Kraków (BDOT10k OT_ADJA_A, TERYT 1261011)", "",
          f"- Fläche der Gemeinde im Rechen-System ({ort_konfig.srs_name()}): "
          + f"{gem_r.area / 1e4:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")
          + " ha; Gegenprobe: BIP Kraków, „Liczba mieszkańców w poszczególnych dzielnicach (wg. stanu na 31 grudnia "
          "2025) oraz powierzchnia dzielnic“, Zeile RAZEM 32683,90 ha (https://www.bip.krakow.pl/?dok_id=242410, "
          "Abzug `2026-11-13/10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html`, gelesen 13.11.2026)",
          f"- weiter als {T(int(puffer))} m außerhalb (fallen weg): {T(weg_puffer)}",
          f"- veröffentlicht: {T(len(features))}, davon in der Stadt {T(sum(1 for f in features if f['properties']['in_stadt']))}, "
          f"bis {T(int(puffer))} m außerhalb {T(sum(1 for f in features if not f['properties']['in_stadt']))}",
          f"- Zuordnung zu dzielnice: {'st der Zelle aus daten/zellen_odbl.js' if st_echt else 'keine in dieser Datei (st: null; die Zuordnung beruht auf den OSM-Grenzen und steht nur in daten/zellen_odbl.js)'}", "",
          "## Schritt 4: Taktklassen (veröffentlichte Haltestellen)", "",
          "| Taktklasse | in der Stadt | außerhalb | zusammen |", "|---|---|---|---|"]
    for k in KLASSEN:
        a, c = lage_zaehl[(True, k)], lage_zaehl[(False, k)]
        b.append(f"| {k} | {T(a)} | {T(c)} | {T(a + c)} |")
    vm_z = Counter(f["properties"]["verkehrsmittel"] for f in features)
    b += ["", "| Verkehrsmittel | Haltestellen |", "|---|---|"] + [f"| {k} | {T(v)} |" for k, v in sorted(vm_z.items())]
    # Gegenprobe Freitag
    ids = [f["properties"]["id"] for f in features]
    gleich = sum(1 for h in ids if h in w2 and w2[h][1] == w1[h][1])
    fehlt = sum(1 for h in ids if h not in w2)
    kl2 = Counter(w2[h][1] for h in ids if h in w2)
    b += ["", f"## Gegenprobe {tag2.strftime('%d.%m.%Y')}", "",
          f"- Fahrten je Feed am Gegenprobe-Tag: " + ", ".join(f"{k} {T(v)}" for k, v in tage[tag2][2].items()),
          f"- veröffentlichte Haltestellen mit gleicher Taktklasse an beiden Tagen: {T(gleich)} von {T(len(ids))}",
          f"- am Gegenprobe-Tag ohne Abfahrt: {T(fehlt)}",
          "- Taktklassen am Gegenprobe-Tag: " + ", ".join(f"{k} {T(kl2[k])}" for k in KLASSEN), "",
          "## Grenzen", "",
          "- Die Klassengrenzen (6, 2, 1 Abfahrten je Stunde und Richtung) sind das Muster des Kiezatlas Potsdam, keine "
          "polnische Norm; ein Krakauer Gegenstück (Plan transportowy) wurde nicht gesucht.",
          "- Der Schultag am Stichtag ist aus Wissen angenommen, der Schulkalender ist nicht geprüft.",
          "- Ob der Fahrplan des Stichtags nach dem nächsten wöchentlichen Feed noch gilt, ist nicht geprüft "
          "(`feed_version` des Bus-Feeds: 20261109_20261114).",
          "- Haltestellen-Code-Stamm als Haltestelle: nicht gegen eine amtliche Haltestellenliste geprüft.", ""]
    return js, "\n".join(b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pruefen", action="store_true", help="neu rechnen und byte-genau vergleichen, nichts schreiben")
    a = ap.parse_args()
    js, beleg = rechnen()
    ok = vw.ausgeben(AUS_JS, js, a.pruefen) & vw.ausgeben(AUS_BELEG, beleg, a.pruefen)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
