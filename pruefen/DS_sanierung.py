"""Prüfung Sanierungsatlas Wohnungsbestand: Abnahmeregeln aus pruefen/DS_protokoll.md, ohne Netz und ohne Datenbank.

Liest daten/sanierung.js, daten/sanierung_odbl.js und belege/DS_sanierung_lauf.md. Prüft:
  1. Summen: Einträge je Art = je Eigentum = je dzielnica = N, auch innerhalb jeder dzielnica; Ergebnisklassen der
     Verortung = N; verortet = Umriss + Punkt + ohne; Typologie je Delegatur bzw. je dzielnica + nicht zugeordnet =
     Stadt; Block ≤ Mehrfamilienhäuser, Großsiedlung ≤ Block; Quoten und Wilson-Intervalle nachgerechnet.
  2. Datenschutz: keine Felder für Adresse, L.p., Gebäudekennung oder Namen; keine Werte, die wie eine Adresse
     („ul. …“) oder eine BDOT10k-Kennung aussehen.
  3. Punkte nur für Eigentum gmina, skarb_panstwa, publiczne_mieszane; Höhe nur mit Herkunft; Lage in Kraków.
  4. OSM-Spur nur in der _odbl-Datei, ODbL-Vermerk in deren Kopf.
  5. Typologie als Schätzung (schaetzung true, baujahr false), keine Energie- oder Baujahrwerte.
  6. Weiterverwendung: Vermerk mit Quelle, Datum der Erstellung und des Abrufs, Hinweis auf Verarbeitung und die
     Haftungsklausel wörtlich in beiden Dateien gleich.
  7. Beleg nennt N, die Zahl der verorteten Einträge und die Gegenprobe wie die Daten.
Mit --neu zusätzlich skripte/36_sanierung.py --pruefen (byte-gleich aus den Rohdaten, rund vier Minuten; ohne
Rohdaten übersprungen mit Grund).

Aufruf: python -I pruefen/DS_sanierung.py [--neu]   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "daten"
OSM_SPUR = re.compile(r"OpenStreetMap|\bODbL\b|\"osm_id\"")
VERBOTEN = {"adres", "adresse", "ulica", "strasse", "street", "nr", "hausnr", "numer", "lp", "l_p", "lokalnyid",
            "id", "oid", "gml_id", "gebaeude_id", "name", "nazwa", "wlasnosc_tekst", "baujahr_wert", "rok_budowy",
            "energie", "verbrauch", "kwh"}
ADRESSE = re.compile(r"\b(ul|al|os|pl)\.\s+[A-ZĄĆĘŁŃÓŚŹŻ]")
GUID = re.compile(r"[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}")
EIG_PUNKTE = ["gmina", "skarb_panstwa", "publiczne_mieszane"]
KLEINHAUS = ("budynek jednorodzinny",)
RAHMEN = (19.78, 49.96, 20.23, 50.13)

befunde: list[str] = []


def pruef(ok: bool, text: str) -> None:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)


def lesen(name: str):
    text = (DATEN / name).read_text(encoding="utf-8")
    m = re.search(r"window\.([A-Za-z0-9_]+)\s*=\s*", text)
    return text[:m.start()], text, json.loads(text[m.end():].rstrip().rstrip(";"))


def schluessel(o, aus: set) -> set:
    if isinstance(o, dict):
        for k, v in o.items():
            aus.add(k.lower())
            schluessel(v, aus)
    elif isinstance(o, list):
        for v in o:
            schluessel(v, aus)
    return aus


def werte(o, aus: list) -> list:
    if isinstance(o, dict):
        for v in o.values():
            werte(v, aus)
    elif isinstance(o, list):
        for v in o:
            werte(v, aus)
    elif isinstance(o, str):
        aus.append(o)
    return aus


KLEINES_N = 100   # darunter ohne Nachkommastelle (pruefen/DS_protokoll.md, Nachtrag 2)


def wilson(k: int, n: int, z: float = 1.959964):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    m = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    st = 1 if n >= KLEINES_N else None
    return [round(100 * (m - h), st), round(100 * (m + h), st)]


def anteil(k: int, n: int):
    return (round(100 * k / n, 1) if n >= KLEINES_N else round(100 * k / n)) if n else None


def main() -> int:
    print("Sanierungsatlas Wohnungsbestand (pruefen/DS_protokoll.md)")
    kopf_s, text_s, S = lesen("sanierung.js")
    kopf_o, text_o, O = lesen("sanierung_odbl.js")
    li = S["liste"]
    N = li["eintraege"]

    print("1. Summen")
    pruef(sum(li["je_art"].values()) == N, f"Σ je Art = N ({N})")
    pruef(sum(li["je_eigentum"].values()) == N, "Σ je Eigentum = N")
    pruef(sum(v["n"] for v in li["je_dzielnica"].values()) == N, "Σ je dzielnica = N")
    pruef(all(sum(v["art"].values()) == v["n"] == sum(v["eigentum"].values()) for v in li["je_dzielnica"].values()),
          "je dzielnica: Σ Art = n = Σ Eigentum")
    pruef(sum(li["miejscowosc"].values()) == N, "Σ Miejscowość = N")
    pruef(all(sum(v["art"].get(a, 0) for v in li["je_dzielnica"].values()) == c for a, c in li["je_art"].items()),
          "Σ Art über die dzielnice = Art gesamt")
    ve = O["verortung"]
    poza = li["je_dzielnica"].get("poza", {"n": 0})["n"]
    pruef(ve["eintraege"] == N and sum(ve["je_klasse"].values()) == N, "Σ Ergebnisklassen der Verortung = N")
    pruef(ve["in_krakow"] == N - poza and ve["je_klasse"]["poza_krakowem"] == poza,
          f"in Kraków = N − poza Krakowem ({N} − {poza})")
    pruef(all(ve["je_art"][a]["n"] == c for a, c in li["je_art"].items())
          and sum(v["verortet"] for v in ve["je_art"].values()) == ve["je_klasse"]["verortet"],
          "Verortung je Art passt zu Liste und Summe")
    vt = ve["je_klasse"]["verortet"]
    pruef(ve["quote"] == anteil(vt, ve["in_krakow"]) and ve["wilson95"] == wilson(vt, ve["in_krakow"]),
          f"Quote {ve['quote']} % und Wilson {ve['wilson95']} nachgerechnet")
    gp = O["gegenprobe_dzielnica"]
    ab = ve["je_klasse"]["abweichung_dzielnica"]
    pruef(gp["n"] == vt + ab and gp["gleich"] == vt and gp["quote"] == anteil(gp["gleich"], gp["n"])
          and gp["wilson95"] == wilson(gp["gleich"], gp["n"]),
          f"Gegenprobe über alle Treffer: n = verortet + abweichend ({vt} + {ab}), nachgerechnet")
    o1 = ve["ohne_namensregeln"]
    pruef(o1["verortet"] <= o1["treffer"] and o1["verortet"] <= vt, "Vergleichslauf ohne Namensregeln stimmig")
    vk = O["verknuepfung"]
    pruef(vk["verortet"] == vt == vk["umriss"] + vk["punkt"] + vk["ohne"], "verortet = Umriss + Punkt + ohne")
    pruef(vk["gebaeude_einzeln"] <= vk["umriss"] + vk["punkt"], "verschiedene Gebäude ≤ verknüpfte Einträge")
    pruef(vk["hoehe_lod2"] + vk["hoehe_geschosse"] <= vk["umriss"] + vk["punkt"], "Höhen ≤ verknüpfte Einträge")
    ty = S["typologie"]
    for k in ("mfh", "blok", "osiedle"):
        pruef(sum(v[k] for v in ty["delegaturen"].values()) + ty["nicht_zugeordnet"][k] == ty["stadt"][k],
              f"Typologie {k}: Σ Delegaturen + nicht zugeordnet = Stadt ({ty['stadt'][k]})")
        td = O["typologie_dzielnice"]
        pruef(sum(v[k] for v in td["je_dzielnica"].values()) + td["nicht_zugeordnet"][k] == ty["stadt"][k],
              f"Typologie {k}: Σ dzielnice + nicht zugeordnet = Stadt")
    raeume = [ty["stadt"], ty["nicht_zugeordnet"], *ty["delegaturen"].values(),
              *O["typologie_dzielnice"]["je_dzielnica"].values()]
    pruef(all(r["osiedle"] <= r["blok"] <= r["mfh"] for r in raeume), "Großsiedlung ≤ Block ≤ Mehrfamilienhäuser")

    print("2. Datenschutz")
    for name, D, text in (("sanierung.js", S, text_s), ("sanierung_odbl.js", O, text_o)):
        k = schluessel(D, set()) & VERBOTEN
        pruef(not k, f"{name}: keine Felder für Adresse, L.p., Kennung, Name ({sorted(k)})")
        adr = [w for w in werte(D, []) if ADRESSE.search(w)]
        pruef(not adr, f"{name}: keine Werte in Adressform ({adr[:2]})")
        pruef(not GUID.search(text), f"{name}: keine BDOT10k-Kennung")

    print("3. Punkte")
    f = O["punkte"]["features"]
    pruef(all(x["properties"]["eig"] in EIG_PUNKTE for x in f), f"{len(f)} Punkte nur mit Eigentum {EIG_PUNKTE}")
    pruef(len(f) <= vt, "Punkte ≤ verortete Einträge")
    pruef(not any(x["properties"]["fn"] in KLEINHAUS or ("M" in x["properties"]["art"] and x["properties"]["fn"] is None)
                  for x in f), "kein Punkt an Einfamilienhäusern, keiner mit Wohnnutzung ohne Gebäudefunktion")
    pruef(all(isinstance(x["properties"]["gs"], int) and x["properties"]["gs"] >= O["punkte"]["geschosse_min"] == 3
              for x in f), "jeder Punkt an einem Gebäude mit mindestens 3 Geschossen laut BDOT10k (Nachtrag 4)")
    pruef(len(f) + O["punkte"]["ausgelassen_kleinhaus"] + O["punkte"]["ausgelassen_unter_3_geschosse"] <= vt,
          "Punkte + ausgelassene ≤ verortete Einträge")
    pruef(not any("dm" in x["properties"] for x in f) and "dm" not in (O["ortsmarke"] or {}),
          "kein Denkmalfeld, solange das Register fehlt")
    pruef(all((x["properties"]["h"] is None) == (x["properties"]["hq"] is None) for x in f),
          "Höhe genau dann, wenn ihre Herkunft angegeben ist")
    w, s, o, n = RAHMEN
    pruef(all(w <= x["geometry"]["coordinates"][0] <= o and s <= x["geometry"]["coordinates"][1] <= n for x in f),
          "alle Punkte im Rahmen um Kraków")
    om = O["ortsmarke"]
    pruef(om is None or (om["lage_geprueft"] is False and S["ortsmarke"]["in_liste"]),
          "Ortsmarke nur aus der Liste verortet, Lage ungeprüft gekennzeichnet")
    dm = lesen("denkmale_odbl.js")[2]["ortsmarken"][0]
    pruef(om is None or (dm["geometry"] or {}).get("coordinates") == om["geometry"]["coordinates"],
          "Ortsmarke an derselben Koordinate wie in denkmale_odbl.js (skripte/ortsmarke.py)")

    print("4. ODbL als Dateigrenze")
    pruef(not OSM_SPUR.search(text_s), "sanierung.js ohne OSM-Spur")
    pruef("ODbL" in kopf_o and "OpenStreetMap" in kopf_o, "sanierung_odbl.js mit ODbL-Vermerk im Kopf")

    print("5. Typologie als Schätzung")
    pruef(ty["schaetzung"] is True and ty["baujahr"] is False and O["typologie_dzielnice"]["schaetzung"] is True,
          "schaetzung = true, baujahr = false")
    pruef(not re.search(r"\d+\s*%", json.dumps(ty["literatur"], ensure_ascii=False)),
          "Literatur nur bibliographisch (keine Zahlenangabe daraus)")

    print("6. Weiterverwendung (BIP Kraków, Zasady ponownego wykorzystywania)")
    zs, zo = S["quellen"]["zbk"], O["quellen"]["zbk"]
    pruef(zs["odpowiedzialnosc"] == zo["odpowiedzialnosc"], "Haftungsklausel in beiden Dateien gleich")
    quelle = lambda v: v.split("Informacja przetworzona:")[0]
    pruef(quelle(zs["vermerk"]) == quelle(zo["vermerk"]), "Quellenangabe vor dem Verarbeitungshinweis in beiden gleich")
    for name, v in (("sanierung.js", zs["vermerk"]), ("sanierung_odbl.js", zo["vermerk"])):
        pruef(all(t in v for t in ("bip.krakow.pl", "data wytworzenia", "data pozyskania", "Informacja przetworzona:")),
              f"{name}: Vermerk nennt Quelle, Erstellung, Abruf und Verarbeitung")
    pruef("nie zawiera adresów" in zs["vermerk"], "sanierung.js: Verarbeitungshinweis ohne Adressen")
    pruef(all(t in zo["vermerk"] for t in ("geokodowanie adresów", "OpenStreetMap", "BDOT10k", "LoD2"))
          and "bez adresów" not in zo["vermerk"],
          "sanierung_odbl.js: Verarbeitungshinweis nennt Geokodierung und Verknüpfung")
    osp = O["quellen"]["osm"].get("vermerk_sprachen", {})
    pruef(set(osp) == {"pl", "en", "de"} and all("OpenStreetMap" in t and "ODbL" in t for t in osp.values()),
          "OSM-Nennung in pl, en, de")

    print("7. Beleg")
    beleg = (WURZEL / "belege" / "DS_sanierung_lauf.md").read_text(encoding="utf-8")
    pruef(f"Einträge N = {N};" in beleg, "Beleg nennt N wie die Daten")
    pruef(f"verortet {vt} =" in beleg, "Beleg nennt die verorteten Einträge wie die Daten")
    pruef(f"n = {gp['n']} Treffer, gleich {gp['gleich']}" in beleg, "Beleg nennt die Gegenprobe wie die Daten")
    pruef(f"Treffer {o1['treffer']}, davon verortet (dzielnica gleich) {o1['verortet']}, ulica_nie_znaleziona "
          f"{o1['ulica_nie_znaleziona']}" in beleg, "Beleg nennt den Vergleichslauf wie die Daten (gerechnet)")
    pruef(beleg.count(" m, ja") + beleg.count(" m, nein") == ab, "Beleg nennt Abstand jedes abweichenden Treffers")

    if "--neu" in sys.argv:
        print("8. Reproduzierbar aus den Rohdaten")
        roh = Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")
        if not (roh / "zbk/2026-11-13/zbk_wykaz_2025-12.pdf").exists():
            print("  übersprungen: Rohdaten fehlen unter $KIEZ_DATEN")
        else:
            r = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / "36_sanierung.py"), "--pruefen"],
                               capture_output=True, text=True)
            print(r.stdout.rstrip())
            pruef(r.returncode == 0, "skripte/36_sanierung.py --pruefen byte-gleich")

    print(f"Ergebnis: {len(befunde)} Befunde")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
