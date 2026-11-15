"""Abnahme Versorgung und Takt: Ausgaben der Skripte 11_, 13_, 14_, 15_*_krakow.py gegen Belege, Regeln und Rohdaten.

Kein Netz, keine Datenbank. Prüft (Abnahme in pruefen/D6_protokoll.md):
  1. Jedes Skript mit --pruefen byte-gleich (rechnet neu). Ohne $KIEZ_DATEN-Rohdaten: übersprungen mit Grund.
  2. Beispieldaten pflanzen sich fort (Regel 12): Liest erreichbar.js/planer_odbl.js eine Beispieldatei, tragen sie
     selbst fixture: true; einrichtungen_odbl.js ohne echte OSM-Zeilen trägt fixture: true. Lizenzfolge der
     OSM-Grenzen entschieden (13.11.2026, Variante a): Werte je dzielnica nur in _odbl-Dateien, also haltestellen.js
     und einrichtungen.js ohne st-Werte, Planer je dzielnica nur als planer_odbl.js (Luftlinie) und
     planer_fuss_odbl.js (Fußweg); planer.js gibt es nicht mehr. Die Fußweg-Dateien passen zur Zellreihenfolge.
  3. Keine OSM-Spur (OpenStreetMap, ODbL, osm_id, Fußweg) in den Dateien ohne _odbl; die _odbl-Dateien tragen den
     ODbL-Vermerk im Kopf. Keine internen Plankennungen (Muster aus pruefen/geruest.py).
  4. Zählungen der Belege gleich den Dateien (Haltestellen je Taktklasse und Lage, Einrichtungen je Art, Zellen).
  5. Taktklasse unabhängig nachgerechnet (eigener Code, kein Import aus skripte/13_oepnv_krakow.py) für eine feste
     Stichprobe von Haltestellen: Abfahrten im Fenster je Richtung aus den GTFS-Zips, stärkere Richtung, Klasse.
  6. Kein Richtwert mit Status „amtlich“ in planer_odbl.js und planer_fuss_odbl.js; jeder Richtwert nennt q und seite (Bauvorlage, Punkt 20),
     und die seite steht so in config/richtwerte.yaml.
  7. Jede Fundstelle aus Prawo oświatowe im gehashten Abzug nachgelesen: Prüfsumme gleich dem Beleg, auf der
     genannten Seite stehen Seitenkopf „– P –“, „Art. N.“, Absatz „M.“ und der ganze Wortlaut (pdftotext).
     Ohne Abzug oder pdftotext: übersprungen mit Grund.

Aufruf: python -I pruefen/D6_versorgung.py   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "daten"
BELEGE = WURZEL / "belege"
KIEZ_DATEN = Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")
STICHPROBE_JEDE = 37          # jede 37. veröffentlichte Haltestelle (nach id sortiert)

befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def js(name: str) -> dict:
    t = (DATEN / name).read_text(encoding="utf-8")
    return json.loads(t[t.index("=", t.index("window.")) + 1:].strip().rstrip(";"))


def zahl(s: str) -> int:
    return int(s.replace(".", ""))


def yaml_lesen() -> dict:
    import yaml
    return yaml.safe_load((WURZEL / "config" / "richtwerte.yaml").read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------- 1
def skripte_byte_gleich(rw: dict) -> None:
    print("1. Skripte mit --pruefen byte-gleich")
    roh = [KIEZ_DATEN / p for p in rw["oepnv"]["gtfs"].values()] + [KIEZ_DATEN / rw["einrichtungen"]["bdot10k"]["zip"]]
    fehlt = [str(p) for p in roh if not p.exists()]
    if fehlt:
        print(f"  übersprungen: Rohdaten fehlen ({fehlt[0]} …)")
        return
    # Mit echten OSM-Punkten bzw. Fußweg-Zeilen lesen 11_ (--osm-db) und 14c_ die Datenbank (nur lesend, PG*-Umgebung,
    # Rolle mosidi_lesen); ohne PG*-Umgebung werden diese beiden übersprungen und das gesagt.
    odbl_echt = js("einrichtungen_odbl.js").get("fixture") is not True
    for s in ("11_einrichtungen_krakow.py", "13_oepnv_krakow.py", "14_erreichbarkeit_krakow.py", "15_planer_krakow.py",
              "14c_fussweg_export_krakow.py"):
        arg = ["--pruefen"]
        braucht_db = s.startswith("14c_") or (s.startswith("11_") and odbl_echt)
        if braucht_db and not os.environ.get("PGUSER"):
            print(f"  übersprungen: skripte/{s} --pruefen braucht die Datenbank (PG*-Umgebung, Rolle mosidi_lesen)")
            continue
        if s.startswith("11_") and odbl_echt:
            arg.append("--osm-db")
        r = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / s), *arg],
                           capture_output=True, text=True)
        pruef(r.returncode == 0, f"skripte/{s} --pruefen" + ("" if r.returncode == 0 else f": {r.stdout[-300:]}{r.stderr[-300:]}"))


# ------------------------------------------------------------------------------------------- 2, 3
def fixture_und_lizenzgrenze() -> None:
    print("2. Beispieldaten pflanzen sich fort")
    zellen_bsp = js("zellen_odbl.js").get("fixture") is True
    for n in ("erreichbar.js", "planer_odbl.js"):
        d = js(n)
        pruef(not zellen_bsp or d.get("fixture") is True, f"{n}: fixture {d.get('fixture')} bei zellen_odbl.js fixture {zellen_bsp}")
        if d.get("fixture"):
            pruef(bool(d.get("beispiel_eingaben")), f"{n}: beispiel_eingaben nennt die unechten Eingaben")
    o = js("einrichtungen_odbl.js")
    echt = [f for f in o["features"] if not f["properties"]["id"].startswith("beispiel-")]
    pruef(bool(echt) == (o.get("fixture") is not True), "einrichtungen_odbl.js: fixture genau dann, wenn keine echten OSM-Punkte")
    pruef(js("einrichtungen.js").get("fixture") is None and js("haltestellen.js").get("fixture") is None,
          "einrichtungen.js und haltestellen.js aus echten Rohdaten (ohne fixture)")

    # Lizenzfolge entschieden (13.11.2026, Variante a): st der Zelle beruht auf den OSM-Grenzen, darum stehen Werte je
    # dzielnica nur in _odbl-Dateien. Dateien ohne _odbl tragen kein st.
    for n in ("haltestellen.js", "einrichtungen.js"):
        st_echt = [f["properties"]["id"] for f in js(n)["features"] if f["properties"].get("st") is not None]
        pruef(not st_echt, f"{n}: ohne st-Werte ({len(st_echt)} gesetzt; Zuordnung nur über daten/zellen_odbl.js)")
    pruef(not (DATEN / "planer.js").exists(), "daten/planer.js gibt es nicht mehr (Werte je dzielnica in planer_odbl.js)")
    if not zellen_bsp:
        z = js("zellen_odbl.js")["features"]
        for n in ("planer_odbl.js", "planer_fuss_odbl.js", "erreichbar_fuss_odbl.js"):
            pruef(js(n).get("fixture") is None, f"{n}: echt (ohne fixture), weil zellen_odbl.js echt ist")
        for n in ("erreichbar.js", "erreichbar_fuss_odbl.js"):
            d = js(n)
            pruef((d["anzahl"], d["erste_id"], d["letzte_id"]) == (len(z), z[0]["properties"]["id"], z[-1]["properties"]["id"])
                  and all(len(v) == len(z) for v in d["werte"].values()),
                  f"{n}: Zellreihenfolge gleich daten/zellen_odbl.js ({d['anzahl']} Zellen, {len(d['werte'])} Arten)")
        teile = {f["properties"]["nr"] for f in js("stadtteile_odbl.js")["features"]}
        for n in ("planer_odbl.js", "planer_fuss_odbl.js"):
            pruef(set(js(n)["raeume"]) == teile, f"{n}: Räume = die {len(teile)} dzielnice aus stadtteile_odbl.js")
        f = js("erreichbar_fuss_odbl.js")
        bew = [bool(x["properties"]["ew"]) for x in z]
        pruef(all(v is None for a in f["werte"].values() for v, b in zip(a, bew) if not b),
              "erreichbar_fuss_odbl.js: unbewohnte Zellen ohne Wert")
        b = (BELEGE / "DE_fussweg_export.md").read_text(encoding="utf-8")
        for a, v in f["werte"].items():
            mm = re.search(rf"^\| `{re.escape(a)}` \| (\d+) \|", b, re.M)
            pruef(mm is not None and int(mm[1]) == sum(1 for x in v if x is not None),
                  f"DE_fussweg_export.md: {a} {sum(1 for x in v if x is not None)} Zellen mit Wert")

    print("3. Lizenzgrenze ODbL und Plankennungen")
    spur = re.compile(r"OpenStreetMap|\bODbL\b|\"methode\":\s*\"fussweg\"|\"osm_id\"")
    sys.path.insert(0, str(WURZEL / "pruefen"))
    import geruest  # noqa: E402
    for n in ("haltestellen.js", "einrichtungen.js", "erreichbar.js", "planer_odbl.js", "einrichtungen_odbl.js",
              "planer_fuss_odbl.js", "erreichbar_fuss_odbl.js"):
        t = (DATEN / n).read_text(encoding="utf-8")
        if "_odbl" in n:
            pruef("ODbL" in t.splitlines()[0], f"{n}: ODbL-Vermerk im Kopf")
        else:
            pruef(not spur.search(t), f"{n}: keine OSM-Spur")
        pruef(not geruest.KENNUNG.search(t), f"{n}: keine Plankennung")


# ------------------------------------------------------------------------------------------- 4
def belege_gleich_dateien() -> None:
    print("4. Zählungen der Belege gleich den Dateien")
    h = js("haltestellen.js")["features"]
    b = (BELEGE / "D6_oepnv.md").read_text(encoding="utf-8")
    m = re.search(r"veröffentlicht: ([\d.]+), davon in der Stadt ([\d.]+), bis [\d.]+ m außerhalb ([\d.]+)", b)
    inn = sum(1 for f in h if f["properties"]["in_stadt"])
    pruef(m is not None and (zahl(m[1]), zahl(m[2]), zahl(m[3])) == (len(h), inn, len(h) - inn),
          f"D6_oepnv.md: veröffentlicht {len(h)}, in der Stadt {inn}")
    z = Counter((f["properties"]["taktklasse"], f["properties"]["in_stadt"]) for f in h)
    for k in ("I", "II", "III", "unter III"):
        mm = re.search(rf"^\| {re.escape(k)} \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|$", b, re.M)
        pruef(mm is not None and (zahl(mm[1]), zahl(mm[2])) == (z[(k, True)], z[(k, False)]),
              f"D6_oepnv.md: Taktklasse {k} in der Stadt {z[(k, True)]}, außerhalb {z[(k, False)]}")
    e = Counter(f["properties"]["art"] for f in js("einrichtungen.js")["features"])
    b = (BELEGE / "D6_einrichtungen.md").read_text(encoding="utf-8")
    for a, n in e.items():
        mm = re.search(rf"^\| `{a}` \| ([\d.]+) \|$", b, re.M)
        pruef(mm is not None and zahl(mm[1]) == n, f"D6_einrichtungen.md: {a} {n}")
    er = js("erreichbar.js")
    b = (BELEGE / "D6_erreichbarkeit.md").read_text(encoding="utf-8")
    mm = re.search(r"- Zellen: ([\d.]+), davon bewohnt", b)
    pruef(mm is not None and zahl(mm[1]) == er["anzahl"] == len(js("zellen_odbl.js")["features"]),
          f"D6_erreichbarkeit.md: Zellen {er['anzahl']}")


# ------------------------------------------------------------------------------------------- 5
def _zeilen(z: zipfile.ZipFile, name: str):
    with z.open(name) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            yield r


def _dienste(z: zipfile.ZipFile, tag: date) -> set[str]:
    t, wt = tag.strftime("%Y%m%d"), tag.strftime("%A").lower()
    an = set()
    for r in _zeilen(z, "calendar.txt"):
        if r.get(wt) == "1" and r["start_date"] <= t <= r["end_date"]:
            an.add(r["service_id"])
    for r in _zeilen(z, "calendar_dates.txt"):
        if r["date"] == t:
            if r["exception_type"] == "1":
                an.add(r["service_id"])
            elif r["exception_type"] == "2":
                an.discard(r["service_id"])
    return an


def taktklasse_nachrechnen(rw: dict) -> None:
    print("5. Taktklasse unabhängig nachgerechnet (Stichprobe)")
    oe = rw["oepnv"]
    zips = {k: KIEZ_DATEN / p for k, p in oe["gtfs"].items()}
    if not all(p.exists() for p in zips.values()):
        print("  übersprungen: GTFS-Zips fehlen unter $KIEZ_DATEN")
        return
    h = sorted(js("haltestellen.js")["features"], key=lambda f: f["properties"]["id"])
    probe = {f["properties"]["id"]: f["properties"] for f in h[::STICHPROBE_JEDE]}
    tag = date.fromisoformat(str(oe["messung"]["stichtag"]))
    a, e = (int(x[:2]) * 3600 + int(x[3:]) * 60 for x in oe["messung"]["hvz_fenster"])
    zaehl: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    for k, p in zips.items():
        z = zipfile.ZipFile(p)
        stamm = {r["stop_id"]: r["stop_code"].split("-")[0] for r in _zeilen(z, "stops.txt")}
        heute, gestern = _dienste(z, tag), _dienste(z, tag - timedelta(days=1))
        fahrt = {}
        for r in _zeilen(z, "trips.txt"):
            if r["service_id"] in heute:
                fahrt[r["trip_id"]] = (r["direction_id"], 0)
            elif r["service_id"] in gestern:
                fahrt[r["trip_id"]] = (r["direction_id"], -86400)
        halte = defaultdict(list)
        for r in _zeilen(z, "stop_times.txt"):
            if r["trip_id"] in fahrt:
                halte[r["trip_id"]].append(r)
        for tid, liste in halte.items():
            liste.sort(key=lambda r: int(r["stop_sequence"]))
            richtung, versatz = fahrt[tid]
            for r in liste[:-1]:                                  # ohne letzten Halt
                if (r.get("pickup_type") or "0") == "1":
                    continue
                s = stamm[r["stop_id"]]
                if s not in probe:
                    continue
                hh, mi, se = (int(x) for x in (r["departure_time"] or r["arrival_time"]).split(":"))
                t = hh * 3600 + mi * 60 + se + versatz
                if a <= t < e:
                    zaehl[s][richtung].add((k, tid))
    grenzen = sorted(((kk, float(oe["taktklassen"][kk]["fahrten_hvz_je_richtung_min"])) for kk in ("I", "II", "III")),
                     key=lambda x: -x[1])
    abw = []
    for hid, p in probe.items():
        je = max((len(v) for v in zaehl[hid].values()), default=0) / ((e - a) / 3600)
        kl = next((kk for kk, g in grenzen if je >= g), "unter III")
        if kl != p["taktklasse"] or round(je, 1) != p["fahrten_hvz_je_richtung"]:
            abw.append(f"{hid}: Datei {p['taktklasse']}/{p['fahrten_hvz_je_richtung']}, nachgerechnet {kl}/{round(je, 1)}")
    kl_probe = Counter(p["taktklasse"] for p in probe.values())
    pruef(len(kl_probe) >= 3, "Stichprobe enthält mindestens drei Taktklassen: "
          + ", ".join(f"{k} {n}" for k, n in sorted(kl_probe.items())))
    pruef(not abw, f"{len(probe)} Haltestellen (jede {STICHPROBE_JEDE}.) nachgerechnet, Abweichungen {len(abw)}"
          + (": " + "; ".join(abw[:5]) if abw else ""))


# ------------------------------------------------------------------------------------------- 6
def richtwerte_planer() -> None:
    print("6. Richtwerte im Planer")
    p = js("planer_odbl.js")
    pf = js("planer_fuss_odbl.js")
    werte = [w for d in (p, pf) for r in d["raeume"].values() for w in r["werte"]] + p.get("gesamt", {}).get("werte", []) \
        + pf.get("gesamt", {}).get("werte", [])
    pruef(all(w["status"] != "amtlich" for w in werte), "kein Wert mit Status amtlich (Luftlinie statt Weg)")
    mit = [w for w in werte if "richtwert" in w]
    pruef(all(w["richtwert"].get("q") in (p["quellen"].keys() & pf["quellen"].keys()) and w["richtwert"].get("seite")
              for w in mit),
          f"{len(mit)} Werte mit Richtwert, jeder mit Quelle und Fundstelle")
    pruef(all(w["kennzahl"] == "anteil_in_radius" for w in mit), "Richtwerte nur an Bildungsradien (Prawo oświatowe)")
    rw_seiten = {e["seite"] for e in yaml_lesen()["bildung"].values()}
    pruef(all(w["richtwert"]["seite"] in rw_seiten for w in mit),
          "jede Fundstelle in planer_odbl.js und planer_fuss_odbl.js steht so in config/richtwerte.yaml (bildung)")


# ------------------------------------------------------------------------------------------- 7
def _norm(t: str) -> str:
    """Text für den Vergleich: Silbentrennung am Zeilenende entfernt, Leerraum zusammengefasst."""
    t = re.sub(r"(\w)-\s+(\w)", r"\1\2", t)
    return re.sub(r"\s+", " ", t).strip()


def fundstellen_im_abzug(rw: dict) -> None:
    """Jede Fundstelle (art. N ust. M, s. P) wird im gehashten Abzug auf genau dieser Seite gesucht."""
    print("7. Fundstellen im Abzug nachgelesen (Seite, Artikel, Wortlaut)")
    import hashlib
    import shutil
    eintraege = [(k, e) for k, e in rw["bildung"].items() if e.get("quelle") == "prawo_oswiatowe"]
    manifest = {}
    for z in (BELEGE / "rohdaten-D6-2026-11-13.sha256").read_text(encoding="utf-8").splitlines():
        if z.strip():
            h, name = z.split(None, 1)
            manifest[name.strip()] = h
    pdf = [n for n in manifest if "prawo_oswiatowe" in n and n.endswith(".pdf")]
    if len(pdf) != 1:
        pruef(False, f"Abzug Prawo oświatowe im Prüfsummen-Beleg nicht eindeutig ({len(pdf)} Einträge)")
        return
    pfad = KIEZ_DATEN / pdf[0]
    if not pfad.exists() or shutil.which("pdftotext") is None:
        print(f"  übersprungen: {pdf[0]} unter $KIEZ_DATEN oder pdftotext fehlt")
        return
    pruef(hashlib.sha256(pfad.read_bytes()).hexdigest() == manifest[pdf[0]],
          f"Prüfsumme {pdf[0]} gleich dem Beleg")
    for k, e in eintraege:
        m = re.fullmatch(r"art\. (\d+[a-z]?) ust\. (\d+), s\. (\d+)", e["seite"])
        if not pruef(m is not None, f"{k}: Fundstelle „{e['seite']}“ hat die Form „art. N ust. M, s. P“"):
            continue
        art, ust, s = m.group(1), m.group(2), int(m.group(3))
        roh = subprocess.run(["pdftotext", "-layout", "-f", str(s), "-l", str(s), str(pfad), "-"],
                             capture_output=True, text=True, check=True).stdout
        text = _norm(roh)
        teile = [_norm(t) for t in e["wortlaut"].split("[…]") if _norm(t)]
        fehlt = [t[:40] for t in teile if t not in text]
        # Absatz: nach „Art. N.“ steht „M. “, danach der Wortlaut, ohne dass dazwischen Absatz „M+1. “ beginnt
        i_art = text.find(f"Art. {art}.")
        i_ust = text.find(f" {ust}. ", i_art) if i_art >= 0 else -1
        i_w = text.find(teile[0], i_ust) if i_ust >= 0 else -1
        im_absatz = i_w >= 0 and f" {int(ust) + 1}. " not in text[i_ust:i_w]
        pruef(f"– {s} –" in text and i_art >= 0 and im_absatz and not fehlt,
              f"{k}: s. {s} trägt den Seitenkopf „– {s} –“, „Art. {art}.“, ust. {ust} und den Wortlaut"
              + (f" (fehlt: {'; '.join(fehlt)})" if fehlt else ""))


def main() -> int:
    rw = yaml_lesen()
    skripte_byte_gleich(rw)
    fixture_und_lizenzgrenze()
    belege_gleich_dateien()
    taktklasse_nachrechnen(rw)
    richtwerte_planer()
    fundstellen_im_abzug(rw)
    print(f"\n{len(befunde)} Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
