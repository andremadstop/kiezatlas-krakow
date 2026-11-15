"""Prüfung Denkmale und Kamienice: Regeln aus pruefen/DZ_protokoll.md an den erzeugten Dateien, ohne Rohdaten.

Liest nur daten/denkmale.js, daten/denkmale_bdot.js, daten/denkmale_odbl.js (kein Netz, keine Datenbank). Prüft:
  1. Teilmenge und keine Flächenaussage (teilmenge: true, flaechenaussage: false) in allen drei Dateien.
  2. Summen: je Delegatura + nicht zugeordnet = Stadt; Σ KAT_ISTNIE = Gebäude; Punkte mit Namensbezug = Zählung;
     Komplexe je Art = Zählung; Kamienice je Delegatura = Punkte mit Mehrfamilienhaus (Register und OSM).
  3. Datenschutzgrenze: keine Kennung (LOKALNYID, id, oid, gml_id, qid), kein Adress- oder Namensfeld an Punkten,
     kein Einzeljahr (keine Zahl 1000 … 2100 in den Eigenschaften der Punkte außer Geschossen), Bauzeit nur als Klasse.
  4. Mehrfamilienhaus nur bei Wohngebäude; ohne Gebäudetreffer beides null.
  5. Beispieldaten sichtbar: fixture: true genau dann, wenn kein Eingang vorhanden ist, und dann „BEISPIELDATEN“
     im Kopf; Ortsmarke nur mit Lage, wenn eine Quelle sie trägt.
  6. Zweite Stichprobe (Protokoll, Nachtrag 3) in belege/DZ_sichtpruefung_stichprobe.json: je 20 Punkte aus Wikidata
     und OSM, je Punkt nur lon, lat, quelle, id (Kennung ohne Namen), jeder Punkt aus der Menge der Karte (alle
     Registerpunkte, OSM nur mit heritage); Startwert der Runde in beiden Dateien.
     Sichtprüfung (Nachtrag 4): ohne belege/DZ_sichtpruefung.json sichtpruefung.geprueft false in beiden Dateien und in
     der Stichprobe; mit der Datei geprueft true und die Quoten aus den Antworten nachgezählt (Lage = ja / alle,
     Ansicht = ja / (ja + nein), Wilson 95 %), Wikidata in denkmale.js, OSM und gesamt nur in denkmale_odbl.js, kein
     Name des Prüfers in daten/.
  7. Mit --mit-rohdaten zusätzlich: skripte/dz_denkmale.py --pruefen (braucht $KIEZ_DATEN mit BDOT10k 1261).

Aufruf: python -I pruefen/DZ_denkmale.py [--mit-rohdaten]   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "daten"
KLASSEN = ["vor_1800", "1800_1866", "1867_1918", "1919_1945", "1946_1989", "ab_1990"]
VERBOTEN = {"lokalnyid", "id", "oid", "gml_id", "qid", "item", "nazwa", "name", "strasse", "ulica", "adres",
            "adresse", "hausnr", "nr_domu", "addr", "numer", "nr_rejestru"}
befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def lesen(name: str) -> tuple[str, dict]:
    text = (DATEN / name).read_text(encoding="utf-8")
    m = re.search(r"window\.[A-Z_]+\s*=\s*", text)
    return text[:m.start()], json.loads(text[m.end():].rstrip().rstrip(";"))


def schluessel(obj, aus: set) -> set:
    if isinstance(obj, dict):
        for k, v in obj.items():
            aus.add(k.lower())
            schluessel(v, aus)
    elif isinstance(obj, list):
        for v in obj:
            schluessel(v, aus)
    return aus


def punkte_pruefen(name: str, feats: list[dict], mit_ep: bool) -> None:
    jahr, klasse, nutzung, felder = [], [], [], set()
    for i, f in enumerate(feats):
        p = f["properties"]
        felder |= set(p)
        for k, v in p.items():
            if k != "gs" and isinstance(v, int) and not isinstance(v, bool) and 1000 <= v <= 2100:
                jahr.append(f"{i}.{k}")
            if isinstance(v, str) and re.search(r"\b1[0-9]{3}\b|\b20[0-9]{2}\b", v) and k != "ep":
                jahr.append(f"{i}.{k}")
        if mit_ep and p.get("ep") not in KLASSEN + [None]:
            klasse.append(i)
        if p.get("mfh") and p.get("w") is not True:
            nutzung.append(i)
        if (p.get("w") is None) != (p.get("mfh") is None):
            nutzung.append(i)
    pruef(not jahr, f"{name}: kein Einzeljahr in {len(feats)} Punkten{': ' + ', '.join(jahr[:5]) if jahr else ''}")
    if mit_ep:
        pruef(not klasse, f"{name}: Bauzeit nur als Klasse ({len(KLASSEN)} Klassen oder null)")
    pruef(not nutzung, f"{name}: Mehrfamilienhaus nur bei Wohngebäude, ohne Gebäudetreffer beides null"
          + (f" (Punkte {nutzung[:5]})" if nutzung else ""))
    pruef(not (felder & VERBOTEN), f"{name}: Felder der Punkte {sorted(felder)} ohne Kennung, Name, Adresse")


def kamienice_pruefen(name: str, d: dict, bedingung) -> None:
    zaehl = Counter((f["properties"]["del"] or "-") for f in d["objekte"]["features"] if bedingung(f["properties"]))
    pruef(dict(zaehl) == d["kamienice"] or (d.get("fixture") and d["kamienice"] == {}),
          f"{name}: Kamienice je Delegatura = Punkte mit Mehrfamilienhaus ({sum(d['kamienice'].values())})")


def ortsmarke_pruefen(name: str, d: dict) -> None:
    falsch = [o for o in d["ortsmarken"] if o["geometry"] is not None and o["quelle"] is None]
    pruef(not falsch and len(d["ortsmarken"]) == 1,
          f"{name}: Ortsmarke ul. Kościuszki 18 nur mit Quelle verortet "
          f"(Lage {'offen' if d['ortsmarken'][0]['geometry'] is None else 'aus ' + str(d['ortsmarken'][0]['quelle'])})")


def wilson(k: int, n: int, z: float = 1.959964) -> list[float] | None:
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    m = (p + z * z / (2 * n)) / d
    h = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / d
    return [round(100 * (m - h), 1), round(100 * (m + h), 1)]


def soll_quoten(antworten: list[dict]) -> dict:
    """Unabhängig nachgezählt (Protokoll, Nachtrag 4): Lage = ja / alle, Ansicht = ja / (ja + nein)."""
    lj = sum(a["lage"] == "ja" for a in antworten)
    aj, an = sum(a["ansicht"] == "ja" for a in antworten), sum(a["ansicht"] == "nein" for a in antworten)
    n = len(antworten)
    return {"n": n,
            "lage": {"ja": lj, "daneben": sum(a["lage"] == "daneben" for a in antworten),
                     "nein": sum(a["lage"] == "nein" for a in antworten),
                     "quote": round(100 * lj / n, 1) if n else None, "wilson95": wilson(lj, n)},
            "ansicht": {"ja": aj, "nein": an, "unklar": sum(a["ansicht"] == "unklar" for a in antworten),
                        "entschieden": aj + an, "quote": round(100 * aj / (aj + an), 1) if aj + an else None,
                        "wilson95": wilson(aj, aj + an)}}


def sicht_nachzaehlen(e: dict, sp: dict, r: dict, o: dict) -> None:
    aw = e["antworten"]
    paare = [(a["quelle"], a["id"]) for a in aw]
    soll = {(x["quelle"], x["id"]) for x in sp["punkte"]}
    pruef(e["startwert"] == sp["startwert"] and len(paare) == len(set(paare)) and set(paare) == soll,
          f"Eingabe der Sichtprüfung: {len(paare)} Antworten, jede genau ein Punkt der Stichprobe")
    pruef(all(a["lage"] in ("ja", "daneben", "nein") and a["ansicht"] in ("ja", "nein", "unklar") for a in aw),
          "Eingabe der Sichtprüfung: Werte aus den erlaubten Listen")
    for name, d, q in (("Register", r, "wd"), ("OSM", o, "osm")):
        si = d["sichtpruefung"]
        s = soll_quoten([a for a in aw if a["quelle"] == q])
        pruef(si.get("ergebnis") == s, f"{name}: Quoten nachgezählt (Lage {s['lage']['ja']}/{s['n']} = "
              f"{s['lage']['quote']} %, Ansicht {s['ansicht']['ja']}/{s['ansicht']['entschieden']} = {s['ansicht']['quote']} %)")
        pruef(si.get("datum") == e["datum"] and si.get("pruefer_rolle") == "sichtpruefung_luftbild",
              f"{name}: Datum der Prüfung {si.get('datum')}, Art der Prüfung statt Name")
    g = soll_quoten(aw)
    pruef(o["sichtpruefung"].get("gesamt") == g and "gesamt" not in r["sichtpruefung"],
          f"gesamt nur in denkmale_odbl.js (Lage {g['lage']['ja']}/{g['n']} = {g['lage']['quote']} %)")
    namen = {str(e.get("pruefer", "")).lower()} - {""}
    text = ((DATEN / "denkmale.js").read_text(encoding="utf-8") + (DATEN / "denkmale_odbl.js").read_text(encoding="utf-8")).lower()
    pruef(not any(n in text for n in namen), "kein Name des Prüfers in daten/denkmale*.js")


def main() -> int:
    print("Teil BDOT10k (daten/denkmale_bdot.js)")
    kopf, b = lesen("denkmale_bdot.js")
    z = b["zaehlung"]
    pruef(b["teilmenge"] is True and b["flaechenaussage"] is False and "fixture" not in b,
          "Teilmenge, keine Flächenaussage, echte Daten")
    pruef(sum(z["kat_istnie"].values()) == z["gebaeude"], f"Σ KAT_ISTNIE = Gebäude ({z['gebaeude']})")
    for k in ("wohngebaeude", "mehrfamilienhaeuser", "namensbezug"):
        s = sum(v[k] for v in b["delegaturen"].values()) + b["nicht_zugeordnet"][k]
        pruef(s == z[k], f"Σ Delegaturen + nicht zugeordnet = Stadt, {k} ({s} = {z[k]})")
    pruef(z["mehrfamilienhaeuser"] <= z["wohngebaeude"] <= z["gebaeude"],
          "Mehrfamilienhäuser ≤ Wohngebäude ≤ Gebäude")
    pruef(len(b["namensbezug"]["features"]) == z["namensbezug"],
          f"Punkte mit Namensbezug = Zählung ({z['namensbezug']})")
    arten = Counter(f["properties"]["r"] for f in b["komplexe"]["features"])
    pruef(dict(arten) == z["komplexe"], f"Komplexe je Art = Zählung ({sum(arten.values())})")
    pruef(len(b["delegaturen"]) == 4, f"vier Delegaturen ({', '.join(b['delegaturen'])})")
    punkte_pruefen("Namensbezug", b["namensbezug"]["features"], mit_ep=False)
    pruef(not (schluessel(b, set()) & (VERBOTEN - {"name"})), "keine Kennung oder Adresse in der ganzen Datei")
    pruef("BDOT10k" in b["quelle"]["vermerk"] and "Źródło" in b["quelle"]["vermerk"],
          "Quellenangabe nach art. 40c ust. 3 im Feld quelle.vermerk")

    print("Teil Register (daten/denkmale.js)")
    kopf, r = lesen("denkmale.js")
    vorhanden = any(q["vorhanden"] for q in r["quellen"].values())
    pruef(r["teilmenge"] is True and r["flaechenaussage"] is False, "Teilmenge, keine Flächenaussage")
    pruef((r.get("fixture") is True) == (not vorhanden), f"fixture genau dann, wenn kein Eingang da ist "
          f"(Eingänge: {[k for k, q in r['quellen'].items() if q['vorhanden']] or 'keine'})")
    pruef(("BEISPIELDATEN" in kopf) == bool(r.get("fixture")), "Kopf nennt Beispieldaten genau bei fixture")
    pruef(r["klassen"] == KLASSEN, "Klassenliste wie im Protokoll")
    punkte_pruefen("Registerpunkte", r["objekte"]["features"], mit_ep=True)
    kamienice_pruefen("Register", r, lambda p: p["mfh"])
    ortsmarke_pruefen("Register", r)

    print("Teil OSM (daten/denkmale_odbl.js)")
    kopf, o = lesen("denkmale_odbl.js")
    pruef(o["teilmenge"] is True and o["flaechenaussage"] is False, "Teilmenge, keine Flächenaussage")
    pruef((o.get("fixture") is True) == (o["eingang"] is None), "fixture genau dann, wenn kein OSM-Auszug da ist")
    pruef(("BEISPIELDATEN" in kopf) == bool(o.get("fixture")), "Kopf nennt Beispieldaten genau bei fixture")
    pruef("ODbL" in kopf and "OpenStreetMap" in kopf, "ODbL-Vermerk im Kopf")
    punkte_pruefen("OSM-Punkte", o["objekte"]["features"], mit_ep=True)
    kamienice_pruefen("OSM", o, lambda p: p["mfh"] and p["h"])
    ortsmarke_pruefen("OSM", o)

    print("Zweite Stichprobe (belege/DZ_sichtpruefung_stichprobe.json)")
    sp = json.loads((WURZEL / "belege" / "DZ_sichtpruefung_stichprobe.json").read_text(encoding="utf-8"))
    menge = {"wd": {tuple(f["geometry"]["coordinates"]) for f in r["objekte"]["features"] if "wd" in f["properties"]["q"]},
             "osm": {tuple(f["geometry"]["coordinates"]) for f in o["objekte"]["features"] if f["properties"]["h"] is True}}
    je = Counter(x["quelle"] for x in sp["punkte"])
    pruef(je == Counter({"wd": min(20, len(menge["wd"])), "osm": min(20, len(menge["osm"]))}),
          f"je 20 Punkte aus Wikidata und OSM ({dict(je)})")
    pruef(all(set(x) == {"lon", "lat", "quelle", "id"} for x in sp["punkte"]), "je Punkt nur lon, lat, quelle, id")
    kenn = re.compile(r"^(Q[0-9]+|[nwr][0-9]+)$")
    pruef(all(kenn.match(str(x["id"])) for x in sp["punkte"]), "Kennung ist Wikidata-Q oder OSM-Typ mit Nummer, kein Name")
    fremd = [x for x in sp["punkte"] if (x["lon"], x["lat"]) not in menge.get(x["quelle"], set())]
    pruef(not fremd, f"jeder Punkt aus der Menge der Karte{': ' + str(fremd[:2]) if fremd else ''}")
    eingabe = WURZEL / "belege" / "DZ_sichtpruefung.json"
    ausgewertet = eingabe.is_file() and not r.get("fixture") and not o.get("fixture")
    pruef(sp["geprueft"] is ausgewertet and sp["startwert"] == 20261114,
          f"Stichprobe {'ausgewertet' if ausgewertet else 'ungeprüft'} (geprueft {sp['geprueft']}), Startwert 20261114")
    for name, d in (("Register", r), ("OSM", o)):
        si = d.get("sichtpruefung")
        if d.get("fixture"):
            continue
        pruef(bool(si) and si["geprueft"] is ausgewertet and si["startwert"] == sp["startwert"],
              f"{name}: sichtpruefung.geprueft {str(ausgewertet).lower()}, Startwert der Runde")
    if ausgewertet:
        sicht_nachzaehlen(json.loads(eingabe.read_text(encoding="utf-8")), sp, r, o)
    pruef(r.get("fixture") or r["quellen"]["wd"].get("vermerk") == "Wikidata, CC0 1.0", "Register: Vermerk Wikidata, CC0 1.0")

    if "--mit-rohdaten" in sys.argv:
        print("Reproduzierbarkeit aus Rohdaten (skripte/dz_denkmale.py --pruefen)")
        rc = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / "dz_denkmale.py"), "--pruefen"]).returncode
        pruef(rc == 0, f"neu gerechnet byte-gleich (Rückgabe {rc})")

    print(f"\n{len(befunde)} Befund(e)" if befunde else "\n0 Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
