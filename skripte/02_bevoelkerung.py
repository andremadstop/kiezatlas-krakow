"""Bevölkerung je Stadt, historischem Stadtbezirk und dzielnica: Steckbrief, Gitterzellen, Kennzahlen, Beleg.

Kraków, ohne Netz und ohne Datenbank. Regeln: pruefen/D4_protokoll.md (vor dem ersten Lauf festgelegt).

Liest (unter $KIEZ_DATEN, Beschreibung und Lizenzen in quellen-D4.md):
  2026-11-13/03_gebaeude/1261_SHP.zip       BDOT10k OT_ADJA_A: Stadtgrenze und vier delegatury (frei, Quellenangabe)
  2026-11-13/02_zensus/PL_PD_3035_GPKG.zip  Eurostat Census-Gitter 2021, 1 km (CC BY 4.0)
  2026-11-13/02_zensus/ludnosc_w_rejonach_…nsp_2021.xlsx   GUS NSP 2021 je rejon statystyczny (Quellenangabe)
  eingang/osm_dzielnice_krakow.geojson oder eingang/*.osm.pbf     Grenzen der 18 dzielnice (ODbL), Handdownload
  eingang/rejony_statystyczne.*            Geometrie der 748 rejony (GUS), Handdownload

Schreibt:
  daten/steckbrief.js       immer: echte Werte für Stadt und delegatury; je dzielnica die Werte, deren Eingang da
                            ist, sonst null mit Grund (Vertrag daten/schema/steckbrief.json)
  belege/D4_bevoelkerung.md immer: Zählungen je Schritt, Gegenproben, Regelprüfung (erzeugt, nicht von Hand ändern)
  daten/steckbrief_dzielnice_odbl.js  mit den Grenzen der dzielnice: Werte je dzielnica (ODbL)
  daten/stadtteile_odbl.js, daten/zellen_odbl.js, daten/kennzahlen_odbl.js und .json
                            nur wenn die Grenzen der dzielnice da sind; alle hängen an den OSM-Grenzen und stehen
                            deshalb unter der ODbL (Entscheidung vom 13.11.2026 zur Lizenzfolge, Variante a); sonst
                            bleiben die Beispieldaten aus pruefen/fixtures_krakow.py stehen

Aufruf:
  python -I skripte/02_bevoelkerung.py              rechnen und schreiben
  python -I skripte/02_bevoelkerung.py --pruefen    nichts schreiben, Dateien mit einer neuen Rechnung vergleichen
  python -I skripte/02_bevoelkerung.py --intern-msip ORDNER
        Probelauf mit den städtischen MSIP-Grenzen anstelle der OSM-Grenzen, nur zum Testen des Rechenwegs; schreibt
        ausschließlich nach ORDNER (muss außerhalb des Repos liegen). MSIP steht unter Lizenz-STOPP: nichts davon
        ausliefern, nichts davon ins Repo.
  python -I skripte/02_bevoelkerung.py --msip-gegenprobe
        Regel 5 des Prüfprotokolls: Schnitt durch Vereinigung je dzielnica zwischen den OSM-Grenzen aus eingang/ und
        den MSIP-Grenzen, nur auf dem Bildschirm (schreibt nichts). Braucht die OSM-Grenzen.
Rückgabe 0 = geschrieben bzw. aktuell, 1 = Befund nach Prüfprotokoll oder Abweichung (--pruefen), 2 = Eingang fehlt.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import raum_bevoelkerung as rb  # noqa: E402

WURZEL = rb.WURZEL
DATEN = WURZEL / "daten"
STAND = "2026-11-13"
STICHTAG_NSP = "2021-03-31"
TOL_STADT, TOL_DELEG = 2.0, 5.0

QUELLEN = {
    "nsp2021": {
        "quelle": "Główny Urząd Statystyczny, Narodowy Spis Powszechny Ludności i Mieszkań 2021: „Ludność w rejonach "
                  "statystycznych i obwodach spisowych według płci, ekonomicznych i 10-letnich grup wieku”",
        "url": "https://stat.gov.pl/spisy-powszechne/nsp-2021/nsp-2021-wyniki-ostateczne/ludnosc-w-rejonach-"
               "statystycznych-i-obwodach-spisowych-wedlug-plci-ekonomicznych-i-10-letnich-grup-wieku,12,1.html",
        "lizenz": "z podaniem źródła (warunki GUS)",
        "vermerk": "Główny Urząd Statystyczny: nie ma zastrzeżeń co do kopiowania plików i stron oraz dokonywania "
                   "wydruków, w tym do własnych opracowań, pod warunkiem, że będzie podane ich źródło",
        "fundstelle": "https://stat.gov.pl/copyright",
        "stichtag": STICHTAG_NSP,
        "stichtag_geprueft": False,
    },
    "eurostat2021": {
        "quelle": "Eurostat, Census 2021 population grid, Poland, 1 km (PL_PD_3035_GPKG.zip)",
        "url": "https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/PL_PD_3035_GPKG.zip",
        "lizenz": "CC BY 4.0",
        "vermerk": "EU copyright rules apply, while the licence would be under CC-BY 4.0.",
        "fundstelle": "https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution",
        "stichtag": STICHTAG_NSP,
        "stichtag_geprueft": False,
    },
    "bdot10k": {
        "quelle": "Główny Urząd Geodezji i Kartografii, BDOT10k, powiat 1261, warstwa OT_ADJA_A (granice z PRG)",
        "url": "https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip",
        "lizenz": "bez licencji (art. 40a ust. 2 pkt 1 lit. h, art. 40c ust. 5 Prawo geodezyjne i "
                  "kartograficzne), z podaniem źródła (art. 40c ust. 3)",
        "vermerk": "Baza BDOT10k jest dostępna bezpłatnie i możliwa do dowolnego wykorzystania.",
        "fundstelle": "https://www.geoportal.gov.pl/pl/dane/baza-danych-obiektow-topograficznych-bdot10k/",
        "stichtag": None,
        "stichtag_geprueft": False,
    },
}
# Stand der Werte je dzielnica als Schlüssel (Vertrag daten/schema/steckbrief.json, Feld je_dzielnica); keine Sätze
def je_dzielnica(mit_dzielnice: bool, mit_rejony: bool, getrennt: bool = False) -> str:
    """Stand je nach vorhandenen Eingängen (Grenzen der dzielnice aus OSM, Geometrie der rejony) und KR3."""
    if mit_dzielnice and getrennt:
        return "nur_in_odbl_datei"      # Werte je dzielnica nur in steckbrief_dzielnice_odbl.js, hier null mit Grund
    if not mit_dzielnice:
        return "ohne_grenzen"           # erst mit den Grenzen der dzielnice bzw. der Geometrie der rejony
    if not mit_rejony:
        return "nur_gitter"             # nur das Gitter, NSP erst mit der Geometrie der rejony
    return "nsp_und_gitter"             # NSP als Summe der rejony und das Gitter


# Gründe für fehlende Werte als Schlüssel; die Texte der Eingangsleser (skripte/raum_bevoelkerung.py) werden über
# ihren Anfang zugeordnet, ein unbekannter Text bricht ab (kein Satz rutscht in die Daten)
GRUND_ANFANG = {
    "rejony_geometrie_fehlt": "Geometrie der rejony statystyczne fehlt",
    "rejony_erst_mit_dzielnice": "Geometrie der rejony erst nach den Grenzen der dzielnice",
    "nsp_erst_ueber_rejony": "NSP je dzielnica erst über die rejony",
    "dzielnice_grenzen_fehlen": "Grenzen der dzielnice fehlen",
    "nicht_angefordert": "nicht angefordert",
}
GRUND_KR3 = "grenzen_odbl"   # aus den OSM-Grenzen abgeleitet, steht deshalb nur in steckbrief_dzielnice_odbl.js


def grund(text: str | None) -> str | None:
    if text is None or text in GRUND_ANFANG or text == GRUND_KR3:
        return text
    for k, anfang in GRUND_ANFANG.items():
        if text.startswith(anfang):
            return k
    raise ValueError(f"Grund ohne Schlüssel: {text[:80]}")


KOPF_STECKBRIEF = ("/* Steckbrief je Raum, erzeugt von skripte/02_bevoelkerung.py. Quellen: GUS NSP 2021 (Quellenangabe), "
                   "Eurostat Census-Gitter 2021 (CC BY 4.0), GUGiK BDOT10k (Quellenangabe). */\n")
KOPF_ZELLEN = ("/* Gitterzellen 1 km, erzeugt von skripte/02_bevoelkerung.py. Einwohner: Eurostat, Census 2021 population "
               "grid (CC BY 4.0); Zuordnung zur dzielnica nach dem Mittelpunkt der Zelle in den Grenzen der dzielnice: "
               "© OpenStreetMap-Mitwirkende, Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/). "
               "Die Datei als Ganzes steht unter der ODbL 1.0. ODbL */\n")
KOPF_KENNZAHLEN = ("/* Kennzahlen je dzielnica und Stadt, erzeugt von skripte/02_bevoelkerung.py (gleicher Inhalt wie "
                   "kennzahlen_odbl.json). Einwohner: Eurostat, Census 2021 population grid (CC BY 4.0); Grenzen der "
                   "dzielnice: © OpenStreetMap-Mitwirkende, Open Database License 1.0 "
                   "(https://opendatacommons.org/licenses/odbl/1-0/). Die Datei als Ganzes steht unter der ODbL 1.0. ODbL */\n")
KOPF_ODBL = ("/* Grenzen der dzielnice Krakaus, erzeugt von skripte/02_bevoelkerung.py. © OpenStreetMap-Mitwirkende, "
             "Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/). ODbL */\n")
KOPF_DZ_ODBL = ("/* Steckbrief je dzielnica, erzeugt von skripte/02_bevoelkerung.py. Grenzen: © OpenStreetMap-Mitwirkende, "
                "Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/); Einwohner: Eurostat, Census "
                "2021 population grid (CC BY 4.0); die Datei als Ganzes steht unter der ODbL 1.0 (strengste Lesart, "
                "solange die Lizenzfolge abgeleiteter Werte offen ist). ODbL */\n")

# Lizenzfolge der OSM-Grenzen, entschieden am 13.11.2026 (Variante a): Werte, die auf den OSM-Grenzen beruhen (Zuordnung
# Zelle → dzielnica, Kennzahlen je dzielnica, die Grenzen selbst, Steckbrief je dzielnica), werden als _odbl-Dateien unter
# der ODbL mit dem Vermerk „© OpenStreetMap-Mitwirkende, ODbL“ ausgeliefert: stadtteile_odbl.js, zellen_odbl.js,
# kennzahlen_odbl.js/.json, steckbrief_dzielnice_odbl.js. steckbrief.js (ohne _odbl) trägt je dzielnica weiter null
# mit Grund. False schriebe nur steckbrief.js und steckbrief_dzielnice_odbl.js (Stand vor der Entscheidung).
SEITENDATEN_AUS_OSM = True
# Gruppenzuordnung (Regel 4) als Zahlen: Schwelle und die Anteile der dokumentierten Ausnahmen
# (skripte/raum_bevoelkerung.py AUSNAHMEN_REGEL4, Entscheidung vom 13.11.2026)
ZUORDNUNG_SCHWELLE_PROZ = 99


# ------------------------------------------------------------------------------------------- Bausteine

def nsp_block(w: dict, rejony: int | None = None) -> dict:
    a60 = w["a60_69"] + w["a70_79"] + w["a80p"]
    a019 = w["a0_9"] + w["a10_19"]
    b = {"einwohner": w["ogolem"], "maenner": w["m"], "frauen": w["k"],
         "alter_10": {k: w[k] for k in rb.ALTER_10},
         "oekonomisch": {"vor": w["oek_vor"], "erwerb": w["oek_erwerb"], "nach": w["oek_nach"]},
         "q_u20": rb.anteil(a019, w["ogolem"]), "q_60p": rb.anteil(a60, w["ogolem"]),
         "q_nach": rb.anteil(w["oek_nach"], w["ogolem"])}
    if rejony is not None:
        b["rejony"] = rejony
    return b


def gitter_block(s: dict, nsp_ew: int | None) -> dict:
    a = s["u15"] + s["a15_64"] + s["a65p"]
    return {"zellen": s["zellen"], "einwohner": s["einwohner"], "u15": s["u15"], "a15_64": s["a15_64"],
            "a65p": s["a65p"], "a_ges": a, "q_u15": rb.anteil(s["u15"], a), "q_65p": rb.anteil(s["a65p"], a),
            "einwohner_flaechenanteil": s["einwohner_flaechenanteil"],
            "abweichung_nsp_proz": round((s["einwohner"] - nsp_ew) / nsp_ew * 100, 2) if nsp_ew else None}


def dichte(ew: int | None, km2: float | None) -> int | None:
    return round(ew / km2) if ew is not None and km2 else None


def summe_nsp(werte: list[dict]) -> dict:
    felder = ["ogolem", "m", "k", *rb.OEK, *rb.ALTER_10]
    return {f: sum(w[f] for w in werte) for f in felder}


# ------------------------------------------------------------------------------------------- Rechnung

def rechnen(konfig: dict, dzielnice_ersatz=None) -> dict:
    d = rb.daten_ordner()
    for rel in (rb.BDOT_ZIP, rb.GITTER_ZIP, rb.NSP_XLSX):
        if not (d / rel).exists():
            raise rb.EingangFehlt(f"{rel} fehlt unter {d}")
    befunde: list[str] = []
    regeln: list[tuple[str, bool, str]] = []

    gl = rb.gliederung_laden(konfig, dzielnice_ersatz=dzielnice_ersatz)
    regeln += rb.gliederung_pruefen(gl, konfig)

    nsp = rb.nsp_lesen(d / rb.NSP_XLSX)
    gleichungen = rb.nsp_gleichungen(nsp)
    for text, links, rechts in gleichungen:
        regeln.append((f"Regel 10: {text}", links == rechts, f"{links} / {rechts}"))
    gruppe_deleg = {g: e.teryt for g, e in gl.gruppen.items()}
    for g, sym in gruppe_deleg.items():
        if sym not in nsp.delegatury:
            raise rb.Abbruch(f"delegatura {sym} der Gruppe {g} fehlt in der NSP-Tabelle")

    zellen, ginfo = rb.gitter_lesen(d / rb.GITTER_ZIP, rb.rahmen_3035(gl.stadt.geom))
    m_stadt, a_stadt = rb.gitter_zuordnen(zellen, {"stadt": gl.stadt.geom})
    m_gr, a_gr = rb.gitter_zuordnen(zellen, {g: e.geom for g, e in gl.gruppen.items()})
    s_stadt = rb.summen_gitter(zellen, m_stadt, a_stadt)["stadt"]
    s_gr = rb.summen_gitter(zellen, m_gr, a_gr)
    in_stadt = [z for z in zellen if m_stadt.get(z.gid) == "stadt"]
    status: dict[str, int] = {}
    for z in in_stadt:
        for name, wert in zip(("T_OBS_STATUS", "T_SPECIAL_VALUE", "konventionell verortet > 0", "nicht gezählt > 0"),
                              z.status):
            k = f"{name} = {wert}"
            status[k] = status.get(k, 0) + 1
    unstimmig = sorted(z.gid for z in in_stadt if None not in (z.t, z.u15, z.a15_64, z.a65p)
                       and z.u15 + z.a15_64 + z.a65p != z.t)
    ohne_t = sum(1 for z in in_stadt if z.t is None)

    abw_stadt = (s_stadt["einwohner"] - nsp.stadt["ogolem"]) / nsp.stadt["ogolem"] * 100
    regeln.append((f"Regel 7: Gitter Stadt gegen NSP höchstens ±{TOL_STADT:g} %", abs(abw_stadt) <= TOL_STADT,
                   _p(abw_stadt)))
    for g, e in sorted(gl.gruppen.items()):
        ew_nsp = nsp.delegatury[e.teryt]["ogolem"]
        abw = (s_gr[g]["einwohner"] - ew_nsp) / ew_nsp * 100
        regeln.append((f"Regel 8: Gitter {e.name} gegen NSP höchstens ±{TOL_DELEG:g} %", abs(abw) <= TOL_DELEG,
                       _p(abw)))

    # dzielnice (wenn Grenzen da)
    teile = konfig["gliederung"]["teile"]
    s_dz, m_dz, rejon_zu, schneider, rejon_info, rejon_grund = {}, {}, None, [], {}, None
    if gl.dzielnice:
        m_dz, a_dz = rb.gitter_zuordnen(zellen, {nr: e.geom for nr, e in gl.dzielnice.items()})
        s_dz = rb.summen_gitter(zellen, m_dz, a_dz)
        ausserhalb = sorted(set(m_stadt) - set(m_dz))
        regeln.append(("Gitter: jede Zelle mit Mittelpunkt in der Stadt liegt in genau einer dzielnica",
                       not ausserhalb, f"{len(ausserhalb)} Zellen ohne dzielnica"))
        # Umkehrung: Zellenmenge über die dzielnice (OSM) = Zellenmenge über die Stadtgrenze (BDOT10k/PRG), gleiche IDs;
        # nur dann hängt die Zellauswahl (erreichbar.js, klimat_zellen.js ohne _odbl) nicht an den OSM-Grenzen
        nur_dz = sorted(set(m_dz) - set(m_stadt))
        regeln.append(("Gitter: Zellen mit Mittelpunkt in den dzielnice = Zellen mit Mittelpunkt in der Stadt (gleiche IDs)",
                       not nur_dz and set(m_dz) == set(m_stadt),
                       f"{len(m_dz)} / {len(m_stadt)} Zellen, {len(nur_dz)} nur über die dzielnice"))
        geo, rq, rejon_grund, rejon_info = rb.rejony_aus_eingang(set(nsp.rejony))
        if geo is not None:
            fehlend = sorted(set(nsp.rejony) - set(geo))
            regeln.append(("Regel 11: jeder rejon der Tabelle hat eine Geometrie", not fehlend,
                           f"{len(fehlend)} ohne Geometrie"))
            rejon_zu, schneider = rb.rejony_zuordnen(geo, gl.dzielnice)
            rejon_info["quelle"] = rq
            summe = sum(nsp.rejony[r]["ogolem"] for r in rejon_zu)
            regeln.append(("Regel 11: Σ rejony über alle dzielnice = Stadt", summe == nsp.stadt["ogolem"],
                           f"{summe} / {nsp.stadt['ogolem']}"))
    else:
        rejon_grund = "Geometrie der rejony erst nach den Grenzen der dzielnice verwendbar"

    # Regel 4 hat im Prüfprotokoll eine eigene Folge („zuordnung_geprueft bleibt dann false“) und sperrt die Ausgaben
    # nicht: Werte je dzielnica hängen nicht an der Gruppenzuordnung. Alle anderen Befunde sperren das Schreiben.
    befunde_r4: list[str] = []
    for text, ok, angabe in regeln:
        if not ok:
            (befunde_r4 if text.startswith("Regel 4:") else befunde).append(f"{text}: {angabe}")

    # ---- Steckbrief
    rc_km2 = rb.flaeche_km2
    stadt_km2 = round(rc_km2(gl.stadt.geom), 2)
    # steckbrief.js hat kein _odbl im Namen: Werte je dzielnica nur in steckbrief_dzielnice_odbl.js (außer im internen
    # Probelauf, der nie ausgeliefert wird)
    getrennt = dzielnice_ersatz is None
    stb = {"stand_auswertung": STAND, "je_dzielnica": je_dzielnica(bool(gl.dzielnice), rejon_zu is not None, getrennt),
           "quellen": QUELLEN,
           "methode": {"gitter_zuordnung": "mittelpunkt", "mindestfallzahl": rb.MINDESTFALLZAHL,
                       "flaechen_srid": ort_konfig.RECHEN_SRID, "gitter_srid": rb.GITTER_SRID},
           "stadt": {"name": konfig["stadt"]["pl"], "teryt": rb.TERYT_POWIAT, "flaeche_km2": stadt_km2,
                     "flaeche_quelle": "bdot10k", "nsp": nsp_block(nsp.stadt, len(nsp.rejony)), "nsp_weg": "tabelle",
                     "gitter": gitter_block(s_stadt, nsp.stadt["ogolem"]),
                     "dichte_nsp": dichte(nsp.stadt["ogolem"], stadt_km2),
                     "dichte_gitter": dichte(s_stadt["einwohner"], stadt_km2)},
           "gruppen": {}, "stadtteile": {}}
    for g, e in sorted(gl.gruppen.items()):
        w = nsp.delegatury[e.teryt]
        km2 = round(rc_km2(e.geom), 2)
        n_rej = sum(1 for r in nsp.rejony.values() if r["delegatura"] == e.teryt)
        stb["gruppen"][g] = {"name": e.name, "teryt": e.teryt, "flaeche_km2": km2, "flaeche_quelle": "bdot10k",
                             "nsp": nsp_block(w, n_rej), "nsp_weg": "tabelle",
                             "gitter": gitter_block(s_gr[g], w["ogolem"]),
                             "dichte_nsp": dichte(w["ogolem"], km2), "dichte_gitter": dichte(s_gr[g]["einwohner"], km2)}
    voll = SEITENDATEN_AUS_OSM or dzielnice_ersatz is not None     # Probelauf (außerhalb des Repos) immer voll
    dz_odbl: dict[str, dict] = {}
    for t in teile:
        nr = t["nr"]
        eintrag = {"name": t["name"], "roemisch": t["roemisch"], "gruppe": t["gruppe"], "teryt": None}
        if gl.dzielnice and getrennt:
            echt = dict(eintrag)
            km2 = round(rc_km2(gl.dzielnice[nr].geom), 2)
            s = s_dz[nr]
            echt.update({"osm_id": gl.dzielnice[nr].extra.get("osm_id"), "flaeche_km2": km2,
                         "gitter": {**gitter_block(s, None), "zellen_beruehrt": s["zellen_beruehrt"],
                                    "spanne_proz": (round((s["einwohner_flaechenanteil"] - s["einwohner"])
                                                          / s["einwohner"] * 100, 1) if s["einwohner"] else None)},
                         "dichte_gitter": dichte(s["einwohner"], km2),
                         "nsp": None, "nsp_grund": grund(rejon_grund) or "nsp_erst_ueber_rejony"})
            del echt["teryt"]
            dz_odbl[nr] = echt
            eintrag.update({"flaeche_km2": None, "flaeche_quelle": None, "gitter": None, "gitter_grund": GRUND_KR3,
                            "nsp": None, "nsp_weg": None, "nsp_grund": grund(rejon_grund) or GRUND_KR3,
                            "dichte_gitter": None, "dichte_nsp": None})
        elif gl.dzielnice:
            km2 = round(rc_km2(gl.dzielnice[nr].geom), 2)
            eintrag.update({"flaeche_km2": km2, "flaeche_quelle": "datei:stadtteile_odbl.js",
                            "gitter": gitter_block(s_dz[nr], None), "dichte_gitter": dichte(s_dz[nr]["einwohner"], km2)})
            if rejon_zu is not None:
                rs = [nsp.rejony[r] for r, z in rejon_zu.items() if z == nr]
                w = summe_nsp(rs)
                eintrag.update({"nsp": nsp_block(w, len(rs)), "nsp_weg": "rejony",
                                "dichte_nsp": dichte(w["ogolem"], km2)})
                eintrag["gitter"]["abweichung_nsp_proz"] = (round((s_dz[nr]["einwohner"] - w["ogolem"]) / w["ogolem"]
                                                                  * 100, 2) if w["ogolem"] else None)
            else:
                eintrag.update({"nsp": None, "nsp_weg": None, "nsp_grund": grund(rejon_grund), "dichte_nsp": None})
        else:
            eintrag.update({"flaeche_km2": None, "flaeche_quelle": None, "gitter": None,
                            "gitter_grund": grund(gl.dzielnice_grund), "nsp": None, "nsp_weg": None,
                            "nsp_grund": grund(gl.dzielnice_grund), "dichte_gitter": None, "dichte_nsp": None})
        stb["stadtteile"][nr] = eintrag

    dateien = {"steckbrief.js": rb.js_datei(KOPF_STECKBRIEF, "KIEZ_STECKBRIEF", stb)}
    if dz_odbl:
        dz = {"stand_auswertung": STAND, "stand_osm": gl.zaehlung.get("dzielnice_stand_osm"),
              "quelle_grenzen": gl.dzielnice_quelle,
              "vergleich": "flaechenanteil", "spanne_ist_fehlergrenze": False,
              "quellen": {k: QUELLEN[k] for k in ("eurostat2021",)},
              "lizenz": "ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/), © OpenStreetMap-Mitwirkende; "
                        "Eurostat, CC BY 4.0",
              "methode": {"gitter_zuordnung": "mittelpunkt", "mindestfallzahl": rb.MINDESTFALLZAHL,
                          "flaechen_srid": ort_konfig.RECHEN_SRID, "gitter_srid": rb.GITTER_SRID},
              "zuordnung_geprueft": not befunde_r4,
              "zuordnung": {"vergleich": "delegatury_bdot10k", "schwelle_proz": ZUORDNUNG_SCHWELLE_PROZ,
                            "ausnahmen": {nr: {"anteil_proz": a, "rest": "grenzsplitter"}
                                          for nr, a in sorted(rb.AUSNAHMEN_REGEL4.items())}},
              "kontrolle": {"einwohner_mittelpunkt_stadt": s_stadt["einwohner"], "zellen_mittelpunkt_stadt": s_stadt["zellen"],
                            "einwohner_summe_dzielnice": sum(v["gitter"]["einwohner"] for v in dz_odbl.values()),
                            "zellen_summe_dzielnice": sum(v["gitter"]["zellen"] for v in dz_odbl.values())},
              "stadtteile": dz_odbl}
        dateien["steckbrief_dzielnice_odbl.js"] = rb.js_datei(KOPF_DZ_ODBL, "KIEZ_STECKBRIEF_DZIELNICE", dz)

    # ---- Vertragsdateien der Seiten, nur mit echten Grenzen und nach der Entscheidung zu KR3
    if gl.dzielnice and voll:
        dateien.update(vertragsdateien(konfig, gl, zellen, m_dz, s_dz, s_stadt, stadt_km2))

    erg = {"gl": gl, "nsp": nsp, "gleichungen": gleichungen, "ginfo": ginfo, "s_stadt": s_stadt, "s_gr": s_gr,
           "s_dz": s_dz, "status": status, "unstimmig": unstimmig, "ohne_t": ohne_t, "in_stadt": len(in_stadt),
           "abw_stadt": abw_stadt, "regeln": regeln, "befunde": befunde, "befunde_r4": befunde_r4,
           "steckbrief": stb, "dateien": dateien,
           "rejon_zu": rejon_zu, "schneider": schneider, "rejon_info": rejon_info, "rejon_grund": rejon_grund,
           "stadt_km2": stadt_km2, "intern": dzielnice_ersatz is not None, "voll": voll}
    erg["beleg"] = beleg(erg, konfig)
    return erg


def vertragsdateien(konfig, gl, zellen, m_dz, s_dz, s_stadt, stadt_km2) -> dict[str, str]:
    teile = konfig["gliederung"]["teile"]
    vereinfacht = rb.grenzen_vereinfachen({t["nr"]: gl.dzielnice[t["nr"]].geom for t in teile})
    st_feat = []
    for t in teile:
        e = gl.dzielnice[t["nr"]]
        lp = e.geom.representative_point()
        st_feat.append({"type": "Feature", "geometry": rb.runden_geom(vereinfacht[t["nr"]]),
                        "properties": {"nr": t["nr"], "roemisch": t["roemisch"], "name": t["name"],
                                       "flaeche_km2": round(rb.flaeche_km2(e.geom), 2), "bezirk": t["gruppe"],
                                       "lx": round(lp.x, 5), "ly": round(lp.y, 5)}})
    stadtteile = {"type": "FeatureCollection", "stand": gl.zaehlung.get("dzielnice_stand_osm") or None,
                  "stand_auswertung": STAND, "quelle": gl.dzielnice_quelle, "features": st_feat}

    zfeat = []
    for z in sorted((z for z in zellen if z.gid in m_dz), key=lambda z: z.gid):
        a = (z.u15 or 0) + (z.a15_64 or 0) + (z.a65p or 0)
        p = {"id": z.gid, "st": m_dz[z.gid], "ew": z.t}
        if None not in (z.u15, z.a15_64, z.a65p):
            p["a_ges"] = a
            p["q_u15"] = rb.anteil(z.u15, a)
            p["q_65p"] = rb.anteil(z.a65p, a)
        zfeat.append({"type": "Feature", "geometry": rb.gitter_quadrat_wgs84(z), "properties": p})
    zfc = {"type": "FeatureCollection", "stand": STAND, "features": zfeat}

    def kacheln(s: dict) -> list[dict]:
        a = s["u15"] + s["a15_64"] + s["a65p"]
        k = [{"id": "einwohner", "wert": s["einwohner"], "anzeige": "summe", "quelle": "eurostat2021"}]
        for kid, z in (("u15", s["u15"]), ("65p", s["a65p"])):
            w = rb.anteil(z, a)
            k.append({"id": kid, "wert": w, "zaehler": z, "nenner": a, "anzeige": "anteil", "quelle": "eurostat2021"}
                     if w is not None else {"id": kid, "wert": None, "anzeige": "anteil", "quelle": "eurostat2021",
                                            "grund": f"weniger als {rb.MINDESTFALLZAHL} Personen"})
        return k
    teil_kz = {}
    for t in teile:
        nr = t["nr"]
        s = {**s_dz[nr], "einwohner": sum(z.t or 0 for z in zellen if m_dz.get(z.gid) == nr)}
        teil_kz[nr] = {"name": t["name"], "roemisch": t["roemisch"], "zellen": s_dz[nr]["zellen"],
                       "flaeche_km2": round(rb.flaeche_km2(gl.dzielnice[nr].geom), 2), "kacheln": kacheln(s),
                       "gebaeude": {"anzahl": 0}}
    s_alle = {"einwohner": sum(v["einwohner"] for v in s_dz.values()), "u15": sum(v["u15"] for v in s_dz.values()),
              "a15_64": sum(v["a15_64"] for v in s_dz.values()), "a65p": sum(v["a65p"] for v in s_dz.values())}
    kz = {"stand_auswertung": STAND,
          "lizenz": "ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/), © OpenStreetMap-Mitwirkende; "
                    "Eurostat, CC BY 4.0",
          "quellen": {k: {"quelle": v["quelle"], "lizenz": v["lizenz"], "vermerk": v["vermerk"]}
                      for k, v in QUELLEN.items()},
          "stadt": {"zellen": len(zfeat), "flaeche_km2": stadt_km2, "kacheln": kacheln(s_alle), "verteilungen": {},
                    "gebaeude": {"anzahl": 0}},
          "stadtteile": teil_kz,
          "kontrolle": {"gebaeude_im_rechteck": 0, "gebaeude_in_stadt": 0,
                        "zellen_mittelpunkt_stadt": s_stadt["zellen"], "einwohner_mittelpunkt_stadt": s_stadt["einwohner"]}}
    return {"stadtteile_odbl.js": rb.js_datei(KOPF_ODBL, "KIEZ_STADTTEILE", stadtteile),
            "zellen_odbl.js": rb.js_datei(KOPF_ZELLEN, "KIEZ_ZELLEN", zfc),
            "kennzahlen_odbl.js": rb.js_datei(KOPF_KENNZAHLEN, "KIEZ_KENNZAHLEN", kz),
            "kennzahlen_odbl.json": json.dumps(kz, ensure_ascii=False, indent=1) + "\n"}


# ------------------------------------------------------------------------------------------- Beleg

def _z(n) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner (wie in den übrigen Belegen)."""
    return f"{n:,}".replace(",", ".") if isinstance(n, int) else str(n)


def _p(x: float, stellen: int = 2) -> str:
    return f"{x:+.{stellen}f}".replace(".", ",") + " %"


def beleg(e: dict, konfig: dict) -> str:
    d = rb.daten_ordner()
    gl, nsp = e["gl"], e["nsp"]
    L = ["# Beleg Gliederung und Bevölkerung (erzeugt)", "",
         "Erzeugt von `skripte/02_bevoelkerung.py`; nicht von Hand ändern. `skripte/02_bevoelkerung.py --pruefen` "
         "rechnet neu und vergleicht. Regeln: `pruefen/D4_protokoll.md`. Stand der Auswertung: " + STAND + ".", ""]
    if e["intern"]:
        L += ["**Probelauf mit MSIP-Grenzen (Lizenz-STOPP): nur intern, nicht ausliefern.**", ""]
    L += ["## Eingaben", "", "| Datei (unter `$KIEZ_DATEN`) | Bytes | SHA256 |", "|---|---|---|"]
    osm_rel = (f"eingang/{gl.zaehlung['dzielnice_datei']}" if gl.dzielnice and gl.zaehlung.get("dzielnice_datei")
               else None)
    for rel in (rb.BDOT_ZIP, rb.GITTER_ZIP, rb.NSP_XLSX) + ((osm_rel,) if osm_rel else ()):
        p = d / rel
        L.append(f"| `{rel}` | {_z(p.stat().st_size)} | `{rb.sha256(p)}` |")
    L += ["", "Prüfsummen beim Abruf: `2026-11-13/HERKUNFT.md` und `2026-11-13/02_zensus/HERKUNFT.md` (Machbarkeitsprobe)"
          + (", Handdownload OSM: `eingang/HERKUNFT.md` und `eingang/SHA256SUMS`" if osm_rel else "")
          + "; zum Nachprüfen in `belege/rohdaten-D4-2026-11-13.sha256`.", ""]

    L += ["## Schritt 1: Stadt und historische Stadtbezirke (BDOT10k `OT_ADJA_A`)", "",
          f"- Sätze in der Schicht: {e['gl'].zaehlung['bdot_saetze']}; Koordinatensystem laut .prj: "
          f"{e['gl'].zaehlung['srs_bdot']}; Flächen gerechnet in {ort_konfig.srs_name()}.",
          f"- Stadt: {gl.stadt.name} (TERYT {gl.stadt.teryt}), {str(e['stadt_km2']).replace('.', ',')} km², "
          f"Datenquelle laut Attribut `ZRO_DANYCH`: {gl.stadt.extra.get('zrodlo')}, Version {gl.stadt.extra.get('wersja')}.",
          "", "| Gruppe | delegatura | TERYT | Fläche km² |", "|---|---|---|---|"]
    for g, x in sorted(e["steckbrief"]["gruppen"].items()):
        L.append(f"| {g} | {x['name']} | {x['teryt']} | {str(x['flaeche_km2']).replace('.', ',')} |")
    L += ["", "## Schritt 2: Grenzen der dzielnice", ""]
    if gl.dzielnice:
        L += [f"- Quelle: `{gl.dzielnice_quelle}`, Datenstand laut Dateikopf "
              f"{gl.zaehlung.get('dzielnice_stand_osm') or 'nicht angegeben'}; Grenzrelationen mit römischer Ziffer in "
              f"`ref`, `official_name` oder `name` (Kandidaten); zugeordnet {len(gl.dzielnice)} von 18 "
              f"(Kandidaten {gl.zaehlung.get('dzielnice_kandidaten', 'nicht angegeben')}, andere Verwaltungsebene "
              f"{gl.zaehlung.get('dzielnice_andere_ebene', 'nicht angegeben')}, ohne Zuordnung "
              f"{gl.zaehlung.get('dzielnice_ohne_zuordnung', 'nicht angegeben')}, nur über den Namen getroffen und "
              f"von einem Treffer mit Ziffer verdrängt {gl.zaehlung.get('dzielnice_nur_name_verdraengt', 'nicht angegeben')}).",
              "", "| Nr | dzielnica | Gruppe | OSM-Objekt | Name in OSM | Fläche km² |", "|---|---|---|---|---|---|"]
        for t in konfig["gliederung"]["teile"]:
            x = gl.dzielnice[t["nr"]]
            L.append(f"| {t['roemisch']} | {t['name']} | {t['gruppe']} | {x.extra.get('osm_id') or '–'} | "
                     f"{x.extra.get('osm_name') or '–'} | {str(round(rb.flaeche_km2(x.geom), 2)).replace('.', ',')} |")
    else:
        L += [f"- Nicht vorhanden: {gl.dzielnice_grund}. `daten/stadtteile_odbl.js`, `zellen_odbl.js` und `kennzahlen_odbl.*` "
              "bleiben Beispieldaten (`fixture: true`)."]
    L += ["", "## Schritt 3: NSP 2021 je rejon statystyczny (GUS-Tabelle, Blatt „Małopolskie“)", "",
          f"- Kopfzellen geprüft: {', '.join(nsp.kopf_geprueft)}.",
          f"- Zeilen für Kraków: 1 Stadt, {len(nsp.delegatury)} delegatury, {_z(len(nsp.rejony))} rejony, "
          f"{_z(nsp.obwody_zahl)} obwody; Zellen mit „-“ (als 0 gelesen): {_z(nsp.striche)}.",
          f"- Einwohner Stadt: {_z(nsp.stadt['ogolem'])} (Symbol {nsp.stadt['symbol']}); rejon kleinster/größter: "
          f"{_z(min(r['ogolem'] for r in nsp.rejony.values()))} / {_z(max(r['ogolem'] for r in nsp.rejony.values()))}; "
          f"rejony unter {rb.MINDESTFALLZAHL} Personen: "
          f"{_z(sum(1 for r in nsp.rejony.values() if r['ogolem'] < rb.MINDESTFALLZAHL))} (werden nie einzeln ausgeliefert).",
          "", "| Gleichung (Regel 10) | links | rechts | erfüllt |", "|---|---|---|---|"]
    for text, a, b in e["gleichungen"]:
        L.append(f"| {text} | {_z(a)} | {_z(b)} | {'ja' if a == b else 'NEIN'} |")
    gi = e["ginfo"]
    L += ["", "## Schritt 4: Eurostat-Gitter 2021 (1 km)", "",
          f"- Datei im Zip: `{gi['datei']}`, SRS {gi['srs_id']}, Zellen gesamt {_z(gi['zellen_gesamt'])}, im Rahmen "
          f"der Stadt (Hülle plus 1 km) {_z(gi['zellen_im_rahmen'])}.",
          f"- Mittelpunkt in der Stadt: {_z(e['in_stadt'])} Zellen; ohne Wert `T`: {_z(e['ohne_t'])}; mit "
          f"`Y_LT15 + Y15-64 + Y_GE65 ≠ T`: {_z(len(e['unstimmig']))} (nicht korrigiert).",
          "- Statusfelder der Zellen mit Mittelpunkt in der Stadt: "
          + "; ".join(f"{k}: {_z(v)}" for k, v in sorted(e["status"].items())) + ".",
          "", "| Raum | NSP 2021 | Gitter, Mittelpunkt | Abweichung | Gitter, Flächenanteil | Abweichung | Zellen (Mittelpunkt / berührt) |",
          "|---|---|---|---|---|---|---|"]

    def zeile(name, nsp_ew, s):
        a1 = (s["einwohner"] - nsp_ew) / nsp_ew * 100
        a2 = (s["einwohner_flaechenanteil"] - nsp_ew) / nsp_ew * 100
        return (f"| {name} | {_z(nsp_ew)} | {_z(s['einwohner'])} | {_p(a1)} | {_z(s['einwohner_flaechenanteil'])} | "
                f"{_p(a2)} | {_z(s['zellen'])} / {_z(s['zellen_beruehrt'])} |")
    L.append(zeile(gl.stadt.name, nsp.stadt["ogolem"], e["s_stadt"]))
    for g, x in sorted(gl.gruppen.items()):
        L.append(zeile(x.name, nsp.delegatury[x.teryt]["ogolem"], e["s_gr"][g]))
    L += ["", "Der Unterschied zwischen Gitter und NSP mischt drei Dinge, die sich hier nicht trennen lassen: die "
          "Zuordnung ganzer 1-km-Zellen an der Grenze, die Verortung im Gitter (Eurostat) und mögliche Unterschiede im "
          "Stichtag oder in der Abgrenzung der Bevölkerung (nicht geprüft).", ""]
    if e["s_dz"]:
        L += ["| Nr | dzielnica | Gitter, Mittelpunkt | Gitter, Flächenanteil | Spanne | Zellen (Mittelpunkt / berührt) |",
              "|---|---|---|---|---|---|"]
        for t in konfig["gliederung"]["teile"]:
            s = e["s_dz"][t["nr"]]
            sp = (s["einwohner_flaechenanteil"] - s["einwohner"]) / s["einwohner"] * 100 if s["einwohner"] else 0
            L.append(f"| {t['roemisch']} | {t['name']} | {_z(s['einwohner'])} | {_z(s['einwohner_flaechenanteil'])} | "
                     f"{_p(sp, 1)} | {_z(s['zellen'])} / {_z(s['zellen_beruehrt'])} |")
        L.append("")
    L += ["## Schritt 5: rejony → dzielnica", ""]
    if e["rejon_zu"] is not None:
        L += [f"- Quelle `{e['rejon_info'].get('quelle')}`, Sätze {_z(e['rejon_info'].get('saetze'))}, Kennungsfeld "
              f"`{e['rejon_info'].get('kennungsfeld')}`, zugeordnet {_z(len(e['rejon_zu']))}.",
              f"- rejony mit mehr als 5 % Fläche in einer anderen dzielnica: {_z(len(e['schneider']))}"
              + (f" ({', '.join(e['schneider'][:40])}{' …' if len(e['schneider']) > 40 else ''})" if e["schneider"] else "")
              + "."]
    else:
        L += [f"- Nicht gerechnet: {e['rejon_grund']}."]
    L += ["", "## Regeln des Prüfprotokolls", "", "| Regel | erfüllt | Angabe |", "|---|---|---|"]
    for text, ok, angabe in e["regeln"]:
        if text.startswith("Regel 10:"):
            continue      # stehen oben einzeln
        L.append(f"| {text} | {'ja' if ok else 'NEIN'} | {angabe} |")
    n10 = sum(1 for t, ok, _a in e["regeln"] if t.startswith("Regel 10:"))
    n10_ok = sum(1 for t, ok, _a in e["regeln"] if t.startswith("Regel 10:") and ok)
    L.append(f"| Regel 10: Gleichungen der NSP-Tabelle (oben) | {'ja' if n10 == n10_ok else 'NEIN'} | {n10_ok} von {n10} |")
    L += ["", f"Befunde, die das Schreiben sperren: {len(e['befunde'])}."
          + (" " + "; ".join(e["befunde"]) if e["befunde"] else ""), ""]
    n_ausn = sum(1 for t, ok, a in e["regeln"] if t.startswith("Regel 4:") and ok and "dokumentierte Ausnahme" in a)
    if n_ausn and not e["befunde_r4"]:
        L += [f"Regel 4: {n_ausn} dzielnice unter 99 % mit dokumentierter Ausnahme (Entscheidung vom 13.11.2026, "
              "Nachtrag in `pruefen/D4_protokoll.md`): III Prądnik Czerwony und XV Mistrzejowice gelten mit 98,53 % "
              "bzw. 98,64 % als ihrer delegatura zugeordnet; der Rest ist ein Grenzsplitter zwischen den delegatury "
              "der BDOT10k und den dzielnice (Gegenprobe mit den städtischen Grenzen, nur intern). Die Schwelle 99 % "
              "bleibt; die Ausnahme gilt nur für genau diese Anteile. `zuordnung_geprueft` = `true`.", ""]
    if e["befunde_r4"]:
        L += [f"Befunde nach Regel 4: {len(e['befunde_r4'])}. Folge laut Prüfprotokoll: `zuordnung_geprueft` bleibt "
              "`false` (config/krakow.yaml); die Ausgaben werden trotzdem geschrieben, weil Einwohner, Fläche und "
              "Dichte je dzielnica nicht von der Gruppenzuordnung abhängen. Offengelegt: Dass Regel 4 das Schreiben "
              "nicht sperrt, ist nach dem ersten Lauf mit OSM-Grenzen festgelegt worden (vorher sperrte das Skript "
              "bei jedem Befund; das Protokoll nennt für Regel 4 nur die Folge oben). Entscheidung über die "
              "Gruppenzuordnung: docs/entscheidungen/D4.md.", ""]
    L += ["## Ausgaben", ""]
    for name in sorted(e["dateien"]):
        L.append(f"- `daten/{name}`")
    if not e["s_dz"] or not e["voll"]:
        L.append("- nicht geschrieben (Beispieldaten bleiben): `daten/stadtteile_odbl.js`, `daten/zellen_odbl.js`, "
                 "`daten/kennzahlen_odbl.js`, `daten/kennzahlen_odbl.json`"
                 + ("; Grund: Grenzen der dzielnice fehlen" if not e["s_dz"] else
                    "; Grund: Lizenzfolge der aus OSM-Grenzen abgeleiteten Werte in `zellen.js` und `kennzahlen.*` "
                    "offen (KR3, `SEITENDATEN_AUS_OSM = False` in `skripte/02_bevoelkerung.py`); `stadtteile_odbl.js` "
                    "wäre lizenzrechtlich eindeutig, bleibt aber mit, weil `pruefen/fixtures_krakow.py --pruefen` und "
                    "die Summen in `pruefen/daten.py` alle vier Dateien nur gemeinsam als Beispiel- oder als echte "
                    "Daten zulassen. Werte je dzielnica stehen in `daten/steckbrief_dzielnice_odbl.js`"))
    L += ["", "## Grenzen", "",
          "- Stichtag des NSP 2021 (31.03.2021) und des Gitters aus Vorwissen, nicht an einer Fundstelle geprüft.",
          "- Das Gitter hat 1 km Weite; je dzielnica fallen nur wenige Zellen ganz hinein. Die Spanne zwischen "
          "Mittelpunkt- und Flächenanteilsregel ist das Maß der Unschärfe, keine Fehlergrenze.",
          "- Altersgruppen sind zwischen den Quellen nicht gleich geschnitten: Gitter unter 15 / 15–64 / 65 und älter, "
          "NSP 10-Jahres-Gruppen und ökonomische Gruppen (vor, im, nach dem Erwerbsalter, Grenzen nach Geschlecht "
          "verschieden). Sie werden nicht ineinander umgerechnet.",
          ("- Die Zuordnung der dzielnice zu den historischen Stadtbezirken ist erst mit den Grenzen der dzielnice "
           "prüfbar (Regel 4)." if not e["s_dz"] else
           "- Regel 4 vergleicht mit den delegatury der BDOT10k (aus PRG); ob deren Grenzen die amtliche Gruppierung "
           "der dzielnice abbilden, ist nicht amtlich geprüft. Die Reste von III und XV gelten nach der Gegenprobe mit "
           "den städtischen Grenzen als Grenzsplitter (Entscheidung vom 13.11.2026)."),
          "- NSP-Werte je dzielnica fehlen, solange die Geometrie der rejony fehlt (Handdownload, Ausgabe 2021 laut "
          "`eingang/HERKUNFT.md` nicht gefunden; Lizenz der Geometrie nicht geprüft).",
          "- Lizenz des Eurostat-Gitters in der strengsten Lesart (CC BY 4.0); Bestätigung durch Eurostat offen.",
          "- Gemeldete Einwohner der Stadt (BIP Kraków) sind ein anderes Konzept und werden nicht verwendet "
          "(Lizenzangabe fehlt).", ""]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------- Hauptteil

def main(argv: list[str]) -> int:
    konfig = ort_konfig.lade()
    pruefen = "--pruefen" in argv
    intern = None
    if "--intern-msip" in argv:
        i = argv.index("--intern-msip")
        if i + 1 >= len(argv):
            print("Aufruf: --intern-msip ORDNER", file=sys.stderr)
            return 2
        intern = Path(argv[i + 1]).resolve()
        if intern == WURZEL or WURZEL in intern.parents:
            print("--intern-msip: Ordner muss außerhalb des Repos liegen (MSIP-Lizenz-STOPP)", file=sys.stderr)
            return 2
    if "--msip-gegenprobe" in argv:
        try:
            gl = rb.gliederung_laden(konfig)
            if not gl.dzielnice:
                print(f"Gegenprobe nicht möglich: {gl.dzielnice_grund}", file=sys.stderr)
                return 2
            werte = rb.msip_gegenprobe(gl, konfig)
        except (rb.EingangFehlt, rb.Abbruch) as x:
            print(f"Gegenprobe nicht möglich: {x}", file=sys.stderr)
            return 2
        if not werte:
            print(f"Gegenprobe nicht möglich: {rb.MSIP_ZIP} fehlt", file=sys.stderr)
            return 2
        print("Regel 5 (nur Hinweis, MSIP Stand 01.04.2014, nichts gespeichert): Schnitt / Vereinigung je dzielnica")
        for name, q in werte:
            print(f"  {'ok     ' if q >= 0.98 else 'Hinweis'} {name}: {q:.3f}".replace(".", ","))
        return 0
    try:
        ersatz = None
        if intern:
            teile, _z = rb.dzielnice_zuordnen(rb.msip_kandidaten(), konfig)
            ersatz = (teile, "MSIP (nur intern)")
        e = rechnen(konfig, ersatz)
    except rb.EingangFehlt as x:
        print(f"Eingang fehlt: {x}", file=sys.stderr)
        return 2
    except rb.Abbruch as x:
        print(f"Abbruch: {x}", file=sys.stderr)
        return 1
    dateien = dict(e["dateien"])
    belegpfad = WURZEL / "belege" / "D4_bevoelkerung.md"
    for text, ok, angabe in e["regeln"]:
        if not text.startswith("Regel 10:") or not ok:
            print(f"  {'ok   ' if ok else 'FEHLT'} {text}: {angabe}")
    print(f"  Regel 10: {sum(1 for t, ok, _a in e['regeln'] if t.startswith('Regel 10:') and ok)} Gleichungen erfüllt")
    if intern:
        intern.mkdir(parents=True, exist_ok=True)
        for n, t in dateien.items():
            (intern / n).write_text(t, encoding="utf-8")
        (intern / "beleg_intern.md").write_text(e["beleg"], encoding="utf-8")
        print(f"Probelauf (intern, MSIP) nach {intern}: {', '.join(sorted(dateien))}, beleg_intern.md")
        return 1 if e["befunde"] else 0
    if pruefen:
        abw = []
        for n, t in dateien.items():
            if not (DATEN / n).exists() or (DATEN / n).read_text(encoding="utf-8") != t:
                abw.append(f"daten/{n}")
        if not belegpfad.exists() or belegpfad.read_text(encoding="utf-8") != e["beleg"]:
            abw.append("belege/D4_bevoelkerung.md")
        for a in abw:
            print(f"  FEHLT {a} entspricht nicht skripte/02_bevoelkerung.py")
        if not abw:
            print(f"  ok    {len(dateien) + 1} Dateien entsprechen skripte/02_bevoelkerung.py")
        if e["befunde"]:
            print(f"  {len(e['befunde'])} Befund(e) nach Prüfprotokoll")
        return 1 if abw or e["befunde"] else 0
    if e["befunde"]:
        belegpfad.write_text(e["beleg"], encoding="utf-8")
        print(f"{len(e['befunde'])} Befund(e): daten/ nicht geschrieben, Beleg unter belege/D4_bevoelkerung.md")
        return 1
    for n, t in dateien.items():
        (DATEN / n).write_text(t, encoding="utf-8")
        print(f"daten/{n}  {len(t.encode()) // 1024} KB")
    belegpfad.write_text(e["beleg"], encoding="utf-8")
    print("belege/D4_bevoelkerung.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
