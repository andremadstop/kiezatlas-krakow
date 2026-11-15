"""Prüfung Gliederung und Bevölkerung: Bausteine, Ausgaben, Datenschutz, Textvorschlag, Reproduktion.

Ohne Netz und ohne Datenbank. Regeln: pruefen/D4_protokoll.md. Teile:
  A  Zuordnung der dzielnice an selbst gebauten Kandidaten (keine echten Grenzen): Treffer über ref, über die
     römische Ziffer im Namen, nur über den Namen; Verwechslungsgefahr III/XI/XIII, „Podgórze“ gegen „Podgórze
     Duchackie“, „Nowa Huta“ (XVIII) gegen die delegatura „Kraków-Nowa Huta“; Ziffer und Name widersprechen sich;
     fehlende und doppelte Fläche; gleichnamige Fläche ohne Ziffer neben der Grenzrelation; osmtogeojson-Format.
  B  Rechenbausteine an selbst gebauten Flächen und Zellen: Mittelpunktregel, Flächenanteil, Summen, Überlappung,
     rejon → dzielnica mit innerem Punkt und Zählung der Schneider, Mindestfallzahl, gemeinsame Grenzvereinfachung.
  C  daten/steckbrief.js: Vertrag daten/schema/steckbrief.json (Prüfer aus pruefen/daten.py), Summen delegatury =
     Stadt (NSP und Gitter), Stadt = 800.653 (NSP 2021), Dichte = Einwohner / Fläche, Anteile = Zähler / Nenner und
     null unter der Mindestfallzahl (Regel 13), null nur mit Grund (Regel 15), keine Kennung eines rejon oder obwód
     (Regel 12); Beispieldaten genau dann, wenn die dzielnice fehlen.
  D  Textvorschlag docs/entscheidungen/D4/texte/<lang>/bevoelkerung.js: gleiche Schlüssel, Pluralformen, Platzhalter.
  E  Mit Rohdaten unter $KIEZ_DATEN: skripte/02_bevoelkerung.py --pruefen (neu rechnen, byte-gleich, keine Befunde).
     Fehlen die Rohdaten, wird E übersprungen und das gesagt.

Aufruf: python -I pruefen/D4_bevoelkerung.py [--ohne-rohdaten]   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import importlib.util
import warnings
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
import ort_konfig  # noqa: E402
import raum_bevoelkerung as rb  # noqa: E402
import textschicht  # noqa: E402
from shapely.geometry import box, mapping  # noqa: E402
from shapely.ops import transform, unary_union  # noqa: E402

befunde: list[str] = []
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*shapely.ops.transform")   # wie in skripte/
NSP_STADT = 800653          # NSP 2021, Zeile „miasto na prawach powiatu“, Symbol 1261 (belege/D4_bevoelkerung.md)


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


def wirft(f, *a) -> str | None:
    try:
        f(*a)
    except rb.Abbruch as e:
        return str(e)
    return None


def daten_modul():
    spec = importlib.util.spec_from_file_location("daten_pruefung", WURZEL / "pruefen" / "daten.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------- A
def kacheln(konfig: dict) -> dict[str, object]:
    """18 aneinanderliegende Rechtecke (WGS 84) bei Kraków, Schlüssel nr; keine echten Grenzen."""
    aus = {}
    for i, t in enumerate(konfig["gliederung"]["teile"]):
        x, y = 19.80 + (i % 6) * 0.06, 49.98 + (i // 6) * 0.04
        aus[t["nr"]] = box(x, y, x + 0.06, y + 0.04)
    return aus


def teil_a(konfig: dict) -> None:
    print("A  Zuordnung der dzielnice (selbst gebaute Kandidaten)")
    teile = konfig["gliederung"]["teile"]
    g = kacheln(konfig)
    pruef(rb.roemisch_aus("XIII") == "XIII" and rb.roemisch_aus("Dzielnica XIII Podgórze") == "XIII"
          and rb.roemisch_aus("Dzielnica XI Podgórze Duchackie") == "XI" and rb.roemisch_aus("III") == "III"
          and rb.roemisch_aus("Dzielnica Podgórze") is None and rb.roemisch_aus("XIX") is None
          and rb.roemisch_aus("Kraków-Nowa Huta") is None,
          "roemisch_aus: XIII/XI/III ganz, kein Teilwort, nichts aus „Kraków-Nowa Huta“ oder „XIX“")

    def kand(form: str) -> list[tuple[dict, object]]:
        aus = []
        for t in teile:
            if form == "ref":
                tags = {"boundary": "administrative", "ref": t["roemisch"], "name": t["name"]}
            elif form == "name_ziffer":
                tags = {"boundary": "administrative", "name": f"Dzielnica {t['roemisch']} {t['name']}"}
            else:
                tags = {"boundary": "administrative", "name": f"Dzielnica {t['name']}"}
            aus.append((tags, g[t["nr"]]))
        return aus

    for form in ("ref", "name_ziffer", "name"):
        erg, z = rb.dzielnice_zuordnen(kand(form), konfig)
        richtig = all(erg[t["nr"]].geom.equals(g[t["nr"]]) for t in teile)
        pruef(len(erg) == 18 and richtig and z["ohne_zuordnung"] == 0,
              f"Form {form}: 18 von 18 richtig zugeordnet (Fläche je nr gleich der gebauten)")

    k = kand("name_ziffer")
    erg, _z = rb.dzielnice_zuordnen(k, konfig)
    pruef(erg["13"].geom.equals(g["13"]) and erg["11"].geom.equals(g["11"]) and erg["03"].geom.equals(g["03"]),
          "XIII Podgórze, XI Podgórze Duchackie und III Prądnik Czerwony nicht verwechselt")
    erg, z = rb.dzielnice_zuordnen(k + [({"boundary": "administrative", "name": "Kraków-Nowa Huta", "admin_level": "9"},
                                         box(20.0, 50.0, 20.2, 50.1))], konfig)
    pruef(erg["18"].geom.equals(g["18"]) and z["ohne_zuordnung"] == 1,
          "delegatura „Kraków-Nowa Huta“ wird nicht zu XVIII Nowa Huta (ohne Zuordnung gezählt)")
    erg, z = rb.dzielnice_zuordnen(k + [({"place": "suburb", "name": "Nowa Huta"}, box(20.0, 50.0, 20.1, 50.1)),
                                         ({"boundary": "administrative", "name": "Podgórze"}, box(19.9, 50.0, 20.0, 50.1))],
                                   konfig)
    pruef(erg["18"].geom.equals(g["18"]) and erg["13"].geom.equals(g["13"]) and z["nur_name_verdraengt"] == 2,
          "gleichnamige Flächen ohne Ziffer verdrängen die Grenzrelation mit Ziffer nicht (2 verdrängt gezählt)")
    falsch = [({"boundary": "administrative", "ref": "XIII", "name": "Dzielnica XIII Podgórze Duchackie"}, g["13"])]
    pruef(wirft(rb.dzielnice_zuordnen, falsch + k[:12] + k[13:], konfig) is not None,
          "Ziffer XIII mit Namen „Podgórze Duchackie“: Abbruch (Name enthält „Podgórze“, ist es aber nicht)")
    pruef(wirft(rb.dzielnice_zuordnen, k[:-1], konfig) is not None, "17 Flächen: Abbruch")
    pruef(wirft(rb.dzielnice_zuordnen, k + [k[4]], konfig) is not None, "zwei Flächen mit Ziffer V: Abbruch")
    nur_name = kand("name")
    pruef(wirft(rb.dzielnice_zuordnen, nur_name + [nur_name[0]], konfig) is not None,
          "zwei Flächen nur über den Namen „Stare Miasto“: Abbruch")
    ohne_name = [({"boundary": "administrative", "ref": t["roemisch"]}, g[t["nr"]]) for t in teile]
    erg, _z = rb.dzielnice_zuordnen(ohne_name, konfig)
    pruef(len(erg) == 18, "nur ref ohne Namen: 18 zugeordnet")

    # osmtogeojson-Format und einfaches GeoJSON lesen
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "osm_dzielnice_krakow.geojson"
        feats = []
        for i, (tags, geom) in enumerate(k):
            props = {"id": f"relation/{i}", "tags": tags} if i % 2 else {**tags, "@id": f"relation/{i}"}
            feats.append({"type": "Feature", "properties": props, "geometry": mapping(geom)})
        feats.append({"type": "Feature", "properties": {"name": "Linie"},
                      "geometry": {"type": "LineString", "coordinates": [[19.9, 50.0], [19.95, 50.05]]}})
        p.write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
        kd = rb.osm_geojson_kandidaten(p)
        erg, _z = rb.dzielnice_zuordnen(kd, konfig)
        pruef(len(kd) == 18 and len(erg) == 18 and all(e.extra["osm_id"] for e in erg.values()),
              "GeoJSON (flach und osmtogeojson): 18 Flächen, Linie übergangen, OSM-Kennung je dzielnica")

    # Form wie im OSM-Auszug Małopolska (Stand 12.11.2026): name ohne Ziffer, official_name „dzielnica X …“ bzw.
    # „Dzielnica XIV …“, admin_level 9; dazu historische Viertel gleichen Namens mit admin_level 11 und ein
    # „Osiedle Stare Miasto“ mit admin_level 9 aus einem anderen Ort
    echt = []
    for i, t in enumerate(teile):
        wort = "dzielnica" if i % 2 else "Dzielnica"
        echt.append(({"boundary": "administrative", "admin_level": "9", "name": t["name"],
                      "official_name": f"{wort} {t['roemisch']} {t['name']}"}, g[t["nr"]]))
    stoer = [({"boundary": "administrative", "admin_level": "11", "name": n}, box(19.9, 50.0, 19.95, 50.05))
             for n in ("Krowodrza", "Bronowice", "Nowa Huta", "Stare Miasto")]
    stoer.append(({"boundary": "administrative", "admin_level": "9", "name": "Osiedle Stare Miasto"},
                  box(20.5, 49.6, 20.6, 49.7)))
    erg, z = rb.dzielnice_zuordnen(echt + stoer, konfig)
    pruef(all(erg[t["nr"]].geom.equals(g[t["nr"]]) for t in teile) and z["andere_ebene"] == 4
          and z["ohne_zuordnung"] == 1 and z["nur_name_verdraengt"] == 0,
          "OSM-Form (official_name, admin_level 9): 18 richtig; 4 Viertel admin_level 11 übergangen, Osiedle ohne Zuordnung")
    falsch = [({"boundary": "administrative", "admin_level": "9", "name": "Podgórze",
                "official_name": "dzielnica XI Podgórze"}, g["11"])]
    pruef(wirft(rb.dzielnice_zuordnen, echt[:10] + falsch + echt[11:], konfig) is not None,
          "official_name „dzielnica XI Podgórze“ (Ziffer und Name widersprechen sich): Abbruch")
    teil_a_pbf(konfig, teile, g)


def teil_a_pbf(konfig: dict, teile: list[dict], g: dict[str, object]) -> None:
    """PBF-Weg an einer selbst geschriebenen Datei (Kodierer aus pruefen/a3_pbf_schreiben.py, Inhalt ersetzt)."""
    spec = importlib.util.spec_from_file_location("a3_pbf", WURZEL / "pruefen" / "a3_pbf_schreiben.py")
    a3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a3)
    a3.KNOTEN.clear()
    a3.WEGE.clear()
    a3.RELATIONEN.clear()
    nid, wid = 1, 1

    def ring(x0, y0, x1, y1, geteilt=False) -> list[int]:
        nonlocal nid, wid
        ids = []
        for lon, lat in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            a3.k(nid, lon, lat)
            ids.append(nid)
            nid += 1
        wege = [[ids[0], ids[1], ids[2]], [ids[2], ids[3], ids[0]]] if geteilt else [ids + [ids[0]]]
        aus = []
        for refs in wege:
            a3.w(wid, refs)
            aus.append(wid)
            wid += 1
        return aus
    loch = None
    for i, t in enumerate(teile):
        x0, y0, x1, y1 = g[t["nr"]].bounds
        mitglieder = [(1, w_, "outer") for w_ in ring(x0, y0, x1, y1, geteilt=(i == 0))]
        if i == 7:                                  # VIII mit Loch
            loch = box(x0 + 0.02, y0 + 0.01, x0 + 0.03, y0 + 0.02)
            mitglieder += [(1, w_, "inner") for w_ in ring(*loch.bounds)]
        if i == 3:
            mitglieder.insert(0, (0, 1, "admin_centre"))   # Knoten als Mitglied wird übergangen
        a3.RELATIONEN[1000 + i] = (mitglieder, {"type": "boundary", "boundary": "administrative", "admin_level": "9",
                                                "name": t["name"], "official_name": f"dzielnica {t['roemisch']} {t['name']}"})
    # gleichnamige Grenze weit außerhalb des Rahmens (anderer Ort) und ein Viertel ohne Ziffer
    a3.RELATIONEN[2000] = ([(1, w_, "outer") for w_ in ring(21.0, 49.5, 21.05, 49.55)],
                           {"type": "boundary", "boundary": "administrative", "admin_level": "9",
                            "name": "Stare Miasto", "official_name": "dzielnica I Stare Miasto"})
    a3.RELATIONEN[2001] = ([(1, w_, "outer") for w_ in ring(19.9, 50.0, 19.95, 50.05)],
                           {"type": "boundary", "boundary": "administrative", "admin_level": "11", "name": "Krowodrza"})
    with tempfile.TemporaryDirectory() as tmp:
        p = a3.schreiben(Path(tmp) / "test.osm.pbf")
        kand = rb.osm_pbf_kandidaten(p, tuple(konfig["karte"]["rahmen"]))
        erg, z = rb.dzielnice_zuordnen(kand, konfig)
    rc = rb._tr(4326, rb.rechen_crs())
    flaeche_ok = all(abs(transform(rc, erg[t["nr"]].geom).area - transform(rc, g[t["nr"]]).area
                         + (transform(rc, loch).area if t["nr"] == "08" else 0)) < 1.0 for t in teile)
    pruef(len(kand) == 18 and len(erg) == 18 and flaeche_ok
          and all(erg[t["nr"]].extra["osm_id"] == f"relation/{1000 + i}" for i, t in enumerate(teile)),
          "PBF: 18 Relationen (Ring aus zwei Wegen, Loch, Knoten-Mitglied), Fläche je dzielnica wie gebaut, "
          "Grenze außerhalb des Rahmens und Viertel ohne Ziffer nicht unter den Kandidaten")


# ------------------------------------------------------------------------------------------- B
def teil_b(konfig: dict) -> None:
    print("B  Rechenbausteine (selbst gebaute Flächen und Zellen)")
    hin = rb._tr(3035, 4326)
    e0, n0 = 5040000, 3070000          # EPSG:3035, Raum Kraków (nur als Rahmen, keine Messwerte)
    zellen = []
    for i in range(4):
        for j in range(2):
            zellen.append(rb.Zelle(f"z{i}{j}", e0 + i * 1000, n0 + j * 1000, 1000, 100 + 10 * i + j, 20, 60,
                                   20 + 10 * i + j, ()))
    # zwei Flächen: West = Spalten 0 und 1 plus 400 m von Spalte 2, Ost = Rest
    west = transform(hin, box(e0, n0, e0 + 2400, n0 + 2000))
    ost = transform(hin, box(e0 + 2400, n0, e0 + 4000, n0 + 2000))
    mitte, anteile = rb.gitter_zuordnen(zellen, {"w": west, "o": ost})
    pruef(sorted(g for g, k in mitte.items() if k == "w") == ["z00", "z01", "z10", "z11"]
          and sorted(g for g, k in mitte.items() if k == "o") == ["z20", "z21", "z30", "z31"],
          "Mittelpunktregel: Spalte 2 (Mittelpunkt bei 2,5 km) ganz nach Ost")
    a = anteile["w"].get("z20", 0)
    pruef(abs(a - 0.4) < 0.01, f"Flächenanteil Zelle z20 im Westen 0,40 (gerechnet {a:.3f})")
    s = rb.summen_gitter(zellen, mitte, anteile)
    ew = {k: sum(z.t for z in zellen if mitte[z.gid] == k) for k in ("w", "o")}
    pruef(s["w"]["einwohner"] == ew["w"] and s["o"]["einwohner"] == ew["o"]
          and s["w"]["einwohner"] + s["o"]["einwohner"] == sum(z.t for z in zellen),
          "Summen nach Mittelpunkt: West + Ost = alle Zellen")
    pruef(s["w"]["einwohner_flaechenanteil"] + s["o"]["einwohner_flaechenanteil"] == sum(z.t for z in zellen),
          "Summen nach Flächenanteil: West + Ost = alle Zellen")
    pruef(s["o"]["zellen"] == 4 and s["o"]["zellen_beruehrt"] == 4 and s["w"]["zellen_beruehrt"] == 6,
          "Zellen je Fläche: Ost 4 / 4 berührt, West 6 berührt")
    ueber = transform(hin, box(e0, n0, e0 + 3000, n0 + 2000))
    pruef(wirft(rb.gitter_zuordnen, zellen, {"w": ueber, "o": ost}) is not None,
          "überlappende Flächen (Mittelpunkt in zwei): Abbruch")

    # rejon -> dzielnica
    dz = {"01": rb.Einheit("01", "A", transform(hin, box(e0, n0, e0 + 2000, n0 + 2000))),
          "02": rb.Einheit("02", "B", transform(hin, box(e0 + 2000, n0, e0 + 4000, n0 + 2000)))}
    rej = {"r1": transform(hin, box(e0 + 100, n0 + 100, e0 + 900, n0 + 900)),
           "r2": transform(hin, box(e0 + 2100, n0 + 100, e0 + 2900, n0 + 900)),
           "r3": transform(hin, box(e0 + 1000, n0 + 1000, e0 + 2300, n0 + 1900))}   # 23 % in 02
    zu, schneider = rb.rejony_zuordnen(rej, dz)
    pruef(zu == {"r1": "01", "r2": "02", "r3": "01"} and schneider == ["r3"],
          "rejon → dzielnica über den inneren Punkt; r3 (23 % in der Nachbar-dzielnica) als Schneider gezählt")

    pruef(rb.anteil(5, 99) is None and rb.anteil(5, 100) == 5.0 and rb.anteil(1, 3000) == 0.0,
          "Anteile: null unter 100 Personen, eine Nachkommastelle")

    # gemeinsame Grenzvereinfachung: Vereinigung bleibt ohne Lücken
    k = kacheln(konfig)
    v = rb.grenzen_vereinfachen(k)
    rc = rb._tr(4326, rb.rechen_crs())
    vor = unary_union([transform(rc, x) for x in k.values()]).area
    nach = unary_union([transform(rc, x) for x in v.values()]).area
    summe = sum(transform(rc, x).area for x in v.values())
    pruef(set(v) == set(k) and abs(nach - vor) / vor < 1e-6 and abs(summe - nach) / nach < 1e-6,
          "Grenzvereinfachung: gleiche Schlüssel, keine Lücke und keine Überlappung zwischen Nachbarn")


# ------------------------------------------------------------------------------------------- C
def teil_c(konfig: dict) -> None:
    print("C  daten/steckbrief.js und die abhängigen Seitendaten")
    dm = daten_modul()
    schema = json.loads((WURZEL / "daten" / "schema" / "steckbrief.json").read_text(encoding="utf-8"))
    _kopf, name, s = dm.js_lesen(WURZEL / "daten" / "steckbrief.js")
    fehler: list[str] = []
    dm.validieren(s, schema, schema, "$", fehler, {})
    pruef(not fehler and re.search(schema["x-global"], name) is not None,
          f"Vertrag daten/schema/steckbrief.json ({len(fehler)} Abweichungen{': ' + fehler[0] if fehler else ''})")
    st, gr, tl = s["stadt"], s["gruppen"], s["stadtteile"]
    pruef(st["nsp"]["einwohner"] == NSP_STADT, f"Stadt nach NSP 2021 = {NSP_STADT} (Symbol 1261)")
    pruef(sum(g["nsp"]["einwohner"] for g in gr.values()) == st["nsp"]["einwohner"], "Σ delegatury = Stadt (NSP)")
    pruef(sum(g["nsp"]["rejony"] for g in gr.values()) == st["nsp"]["rejony"], "Σ rejony je delegatura = rejony der Stadt")
    pruef(sum(g["gitter"]["einwohner"] for g in gr.values()) == st["gitter"]["einwohner"]
          and sum(g["gitter"]["zellen"] for g in gr.values()) == st["gitter"]["zellen"],
          "Σ delegatury = Stadt (Gitter, Mittelpunktregel: Einwohner und Zellen)")
    pruef(abs(sum(g["flaeche_km2"] for g in gr.values()) - st["flaeche_km2"]) <= 0.05,
          "Σ Flächen der delegatury = Stadtfläche (±0,05 km², Rundung)")
    teile = {t["nr"]: t for t in konfig["gliederung"]["teile"]}
    pruef(set(tl) == set(teile) and all(tl[n]["roemisch"] == teile[n]["roemisch"] and tl[n]["name"] == teile[n]["name"]
                                        and tl[n]["gruppe"] == teile[n]["gruppe"] for n in teile),
          "18 dzielnice mit römischer Ziffer, Name und Gruppe wie config/krakow.yaml")

    raeume = [("Stadt", st)] + [(f"Gruppe {k}", v) for k, v in gr.items()] + [(f"dzielnica {k}", v) for k, v in tl.items()]
    f_dichte, f_anteil, f_grund, f_min = [], [], [], []
    for n, r in raeume:
        if r["nsp"] is not None and r["flaeche_km2"]:
            if r["dichte_nsp"] != round(r["nsp"]["einwohner"] / r["flaeche_km2"]):
                f_dichte.append(n)
        if r["gitter"] is not None and r["flaeche_km2"]:
            if r["dichte_gitter"] != round(r["gitter"]["einwohner"] / r["flaeche_km2"]):
                f_dichte.append(n)
        if r["nsp"] is None and not r.get("nsp_grund"):
            f_grund.append(n + " nsp")
        if r["gitter"] is None and not r.get("gitter_grund"):
            f_grund.append(n + " gitter")
        if r["nsp"] is not None:
            w = r["nsp"]
            a = w["alter_10"]
            soll = {"q_u20": rb.anteil(a["a0_9"] + a["a10_19"], w["einwohner"]),
                    "q_60p": rb.anteil(a["a60_69"] + a["a70_79"] + a["a80p"], w["einwohner"]),
                    "q_nach": rb.anteil(w["oekonomisch"]["nach"], w["einwohner"])}
            if any(w[k] != v for k, v in soll.items()):
                f_anteil.append(n + " nsp")
            if w["einwohner"] < rb.MINDESTFALLZAHL and any(w[k] is not None for k in soll):
                f_min.append(n)
        if r["gitter"] is not None:
            gz = r["gitter"]
            if gz["q_u15"] != rb.anteil(gz["u15"], gz["a_ges"]) or gz["q_65p"] != rb.anteil(gz["a65p"], gz["a_ges"]):
                f_anteil.append(n + " gitter")
            if gz["a_ges"] != gz["u15"] + gz["a15_64"] + gz["a65p"]:
                f_anteil.append(n + " a_ges")
    pruef(not f_dichte, f"Dichte = Einwohner / Fläche, ganzzahlig gerundet ({len(f_dichte)} Abweichungen {f_dichte[:3]})")
    pruef(not f_anteil, f"Anteile = Zähler / Nenner, eine Nachkommastelle ({len(f_anteil)} Abweichungen {f_anteil[:3]})")
    pruef(not f_min, f"Regel 13: keine Anteile unter {rb.MINDESTFALLZAHL} Personen ({len(f_min)} Räume)")
    pruef(not f_grund, f"Regel 15: null nur mit Grund ({len(f_grund)} ohne Grund {f_grund[:3]})")

    text = (WURZEL / "daten" / "steckbrief.js").read_text(encoding="utf-8")
    verboten = re.findall(r'"(rejon_id|rejon|obwod\w*|obwód\w*|symbol_rejonu|id_rejonu)"\s*:', text)
    pruef(not verboten and not re.search(r'"\d{7}\d+"', text),
          "Regel 12: keine Kennung oder Einzelwert eines rejon oder obwód in steckbrief.js (nur die Zahl „rejony“)")

    ohne_dz = all(t["flaeche_km2"] is None for t in tl.values())
    mit_dz = all(t["flaeche_km2"] is not None for t in tl.values())
    pruef(ohne_dz or mit_dz, "dzielnice entweder alle mit Fläche oder alle ohne (kein halber Stand)")
    fixtures = {}
    odbl_kopf = {}
    for datei in ("stadtteile_odbl.js", "zellen_odbl.js", "kennzahlen_odbl.js"):
        p = WURZEL / "daten" / datei
        if p.exists():
            kopf, _n, inhalt = dm.js_lesen(p)
            fixtures[datei] = inhalt.get("fixture") is True
            odbl_kopf[datei] = "ODbL" in kopf and "OpenStreetMap" in kopf
    kj = WURZEL / "daten" / "kennzahlen_odbl.json"
    if kj.exists():
        fixtures["kennzahlen_odbl.json"] = json.loads(kj.read_text(encoding="utf-8")).get("fixture") is True
    dzp = WURZEL / "daten" / "steckbrief_dzielnice_odbl.js"
    if dzp.exists():
        teil_c_odbl(dm, dzp, st, teile)
    else:
        print("  (daten/steckbrief_dzielnice_odbl.js fehlt: Grenzen der dzielnice noch nicht eingelesen)")
    # Regel 15 seit der Entscheidung vom 13.11.2026 zur Lizenzfolge (Variante a, Nachtrag im Prüfprotokoll): steckbrief.js
    # (ohne _odbl) trägt je dzielnica immer null; mit den Grenzen der dzielnice (steckbrief_dzielnice_odbl.js da) sind
    # die vier Seitendateien echte _odbl-Dateien mit ODbL-Vermerk im Kopf, sonst alle vier Beispieldaten.
    pruef(ohne_dz, "Regel 15: steckbrief.js ohne Werte je dzielnica (die stehen in den _odbl-Dateien)")
    if not dzp.exists():
        pruef(all(fixtures.values()) and len(fixtures) == 4,
              "Regel 15: ohne Grenzen der dzielnice bleiben stadtteile_odbl.js, zellen_odbl.js, kennzahlen_odbl.* "
              f"Beispieldaten (fixture: true bei {sum(fixtures.values())} von {len(fixtures)})")
    else:
        pruef(len(fixtures) == 4 and not any(fixtures.values()),
              "Regel 15: mit Grenzen der dzielnice sind stadtteile_odbl.js, zellen_odbl.js, kennzahlen_odbl.* echt "
              f"(fixture: true bei {sum(fixtures.values())} von {len(fixtures)})")
        pruef(all(odbl_kopf.values()) and len(odbl_kopf) == 3,
              "Regel 15: die drei _odbl-Seitendateien tragen den Vermerk OpenStreetMap/ODbL im Kopf")
    for alt in ("zellen.js", "kennzahlen.js", "kennzahlen.json"):
        pruef(not (WURZEL / "daten" / alt).exists(), f"Regel 15: daten/{alt} (alter Name ohne _odbl) gibt es nicht mehr")


def teil_c_odbl(dm, pfad: Path, stadt: dict, teile: dict) -> None:
    """daten/steckbrief_dzielnice_odbl.js: Vertrag, Summen dzielnice = Stadt (Gitter), Flächen, Anteile, Dichte."""
    schema = json.loads((WURZEL / "daten" / "schema" / "steckbrief_dzielnice_odbl.json").read_text(encoding="utf-8"))
    kopf, name, d = dm.js_lesen(pfad)
    fehler: list[str] = []
    dm.validieren(d, schema, schema, "$", fehler, {})
    pruef(not fehler and re.search(schema["x-global"], name) is not None and "ODbL" in kopf and "OpenStreetMap" in kopf,
          f"steckbrief_dzielnice_odbl.js: Vertrag und ODbL-Vermerk im Kopf ({len(fehler)} Abweichungen"
          f"{': ' + fehler[0] if fehler else ''})")
    tl = d["stadtteile"]
    pruef(set(tl) == set(teile) and all(tl[n]["roemisch"] == teile[n]["roemisch"] and tl[n]["name"] == teile[n]["name"]
                                        for n in teile), "18 dzielnice mit römischer Ziffer und Name wie config/krakow.yaml")
    ew = sum(t["gitter"]["einwohner"] for t in tl.values())
    zn = sum(t["gitter"]["zellen"] for t in tl.values())
    pruef(ew == stadt["gitter"]["einwohner"] == d["kontrolle"]["einwohner_summe_dzielnice"]
          == d["kontrolle"]["einwohner_mittelpunkt_stadt"],
          f"Σ dzielnice = Stadt (Gitter, Mittelpunktregel): {ew} Einwohner, exakt")
    pruef(zn == stadt["gitter"]["zellen"] == d["kontrolle"]["zellen_summe_dzielnice"],
          f"Σ Zellen der dzielnice = Zellen der Stadt ({zn})")
    fl = sum(t["flaeche_km2"] for t in tl.values())
    pruef(abs(fl - stadt["flaeche_km2"]) / stadt["flaeche_km2"] <= 0.01,
          f"Σ Flächen der dzielnice gegen die Stadtfläche höchstens ±1 % ({fl:.2f} / {stadt['flaeche_km2']} km²)")
    f = []
    for n, t in tl.items():
        gz = t["gitter"]
        if t["dichte_gitter"] != round(gz["einwohner"] / t["flaeche_km2"]):
            f.append(f"{n} Dichte")
        if gz["q_u15"] != rb.anteil(gz["u15"], gz["a_ges"]) or gz["q_65p"] != rb.anteil(gz["a65p"], gz["a_ges"]):
            f.append(f"{n} Anteil")
        if gz["a_ges"] != gz["u15"] + gz["a15_64"] + gz["a65p"] or gz["zellen_beruehrt"] < gz["zellen"]:
            f.append(f"{n} Zählung")
        soll = round((gz["einwohner_flaechenanteil"] - gz["einwohner"]) / gz["einwohner"] * 100, 1) if gz["einwohner"] else None
        if gz["spanne_proz"] != soll:
            f.append(f"{n} Spanne")
        if t["nsp"] is None and not t.get("nsp_grund"):
            f.append(f"{n} ohne Grund")
    pruef(not f, f"je dzielnica: Dichte, Anteile (Mindestfallzahl), Zählungen, Spanne, Grund bei null ({f[:3]})")


# ------------------------------------------------------------------------------------------- D
def teil_d() -> None:
    print("D  Textvorschlag docs/entscheidungen/D4/texte/<lang>/bevoelkerung.js")
    basis = WURZEL / "docs" / "entscheidungen" / "D4" / "texte"
    T = {l: textschicht.datei_lesen(basis / l / "bevoelkerung.js") for l in ("pl", "en", "de")}
    pruef(all(s.startswith("bevoelkerung.") and textschicht.SCHLUESSEL.match(s) for l in T for s in T[l]),
          "nur Namensraum bevoelkerung.*, Schlüsselform")
    pruef(set(T["pl"]) == set(T["en"]) == set(T["de"]), f"gleiche Schlüssel in pl, en, de ({len(T['pl'])})")
    platz = re.compile(r"\{(\w+)\}")
    fehler = []
    for s in T["pl"]:
        for l in ("pl", "en", "de"):
            w = T[l].get(s)
            if isinstance(w, dict):
                if set(w) != set(textschicht.PLURALFORMEN[l]) or not all("{n}" in x for x in w.values()):
                    fehler.append(f"{l}:{s} Pluralformen")
            elif not w:
                fehler.append(f"{l}:{s} leer")
        def pl_satz(v):
            return set(platz.findall(json.dumps(v, ensure_ascii=False)))
        if not pl_satz(T["pl"][s]) == pl_satz(T["en"].get(s)) == pl_satz(T["de"].get(s)):
            fehler.append(f"{s} Platzhalter")
    pruef(not fehler, f"Pluralformen je Sprache, keine leeren Texte, gleiche Platzhalter ({fehler[:3]})")
    deutsch = re.compile(r"\b(und|nicht|oder|Stadtteile?|Einwohner|Karte|Daten|Quelle|für|über|Seite)\b", re.I)
    treffer = [f"{l}:{s}" for l in ("pl", "en") for s, v in T[l].items() if deutsch.search(json.dumps(v, ensure_ascii=False))]
    pruef(not treffer, f"keine deutschen Wörter in pl und en ({treffer[:3]})")


# ------------------------------------------------------------------------------------------- E
def teil_e() -> None:
    print("E  Reproduktion mit Rohdaten")
    d = rb.daten_ordner()
    fehlt = [rel for rel in (rb.BDOT_ZIP, rb.GITTER_ZIP, rb.NSP_XLSX) if not (d / rel).exists()]
    if fehlt:
        print(f"  übersprungen: Rohdaten fehlen unter {d}: {', '.join(fehlt)}")
        return
    r = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / "02_bevoelkerung.py"), "--pruefen"],
                       capture_output=True, text=True, env={**os.environ, "KIEZ_DATEN": str(d)})
    for z in r.stdout.splitlines()[-3:]:
        print("   " + z)
    pruef(r.returncode == 0, f"skripte/02_bevoelkerung.py --pruefen: Ausgaben byte-gleich, keine Befunde (Rückgabe {r.returncode})")


def main(argv: list[str]) -> int:
    konfig = ort_konfig.lade()
    teil_a(konfig)
    teil_b(konfig)
    teil_c(konfig)
    teil_d()
    if "--ohne-rohdaten" in argv:
        print("E  übersprungen (--ohne-rohdaten)")
    else:
        teil_e()
    print(f"\n{len(befunde)} Befund(e)")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
