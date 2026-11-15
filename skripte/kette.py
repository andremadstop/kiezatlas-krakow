"""Die ganze Kette des Kiezatlas Kraków mit einem Befehl: Eingänge prüfen, rechnen, Seiten erzeugen, prüfen.

Ruft nur vorhandene Schritte auf, in der Reihenfolge aus docs/rundgang.md („Schritte“, „Reihenfolge beim
Neurechnen“). Vor dem ersten Schritt prüft die Kette alle Eingänge der gewählten Schritte und hält an, wenn ein
Pflichteingang fehlt; nichts wird dann geschrieben. Fehlt nur ein Handdownload, mit dessen Fehlen ein Schritt
umgehen kann (Luft, Wohnungsmarkt, Denkmalregister, rejony), meldet sie das und rechnet weiter; die betroffene
Datei bleibt dann Beispieldatei (fixture: true) und die Seiten sagen das.

Nur Python-Standardbibliothek, damit der Trockenlauf auch vor dem ersten `uv` läuft. Kein Netz: die Schritte rufen
uv mit --offline auf; Rohdaten kommen vorher über skripte/abruf.py, von Hand nach $KIEZ_DATEN/eingang/ oder aus
einem Rohdaten-Schnappschuss (docs/uruchomienie.md, docs/running.md).

Aufruf (meist über ./atlas.sh, das nur hierher weiterreicht):
  python3 -I skripte/kette.py trocken [--ohne-datenbank] [--ab SCHRITT] [--nur SCHRITT …]
        zeigt die Schritte, prüft Werkzeuge, Datenbank und Eingänge, schreibt nichts
  python3 -I skripte/kette.py alles [--ohne-datenbank] [--ab SCHRITT] [--nur SCHRITT …] [--ohne-browser]
        dasselbe, dann jeden Schritt ausführen; hält beim ersten Fehler an
  python3 -I skripte/kette.py liste     nur die Schritte mit Kurzbeschreibung
--ohne-datenbank lässt die Schritte mit Datenbank aus (ihre Ergebnisse unter daten/ bleiben, wie sie sind).
--ohne-browser gibt der abschließenden Prüfung ./pruefen.sh denselben Schalter.

Umgebung: KIEZ_DATEN (Standard ../kiezatlas-daten/krakow), KIEZ_ENV (Datei mit den Passwörtern der Rollen,
Standard ./.env, in Worktrees ../kiezatlas-krakow/.env), KIEZ_POTSDAM (Standard ../kiezatlas-potsdam, nur für den
Vergleich), KETTE_PRAEFIX (wird jedem Schritt vorangestellt, z. B. „systemd-run --user --scope -p MemoryMax=8G“).
Protokoll jedes Laufs: berichte/kette/<Zeit UTC>.log (berichte/ ist nicht versioniert).

Rückgabe: 0 = alles gut (trocken: alle Pflichteingänge da), 2 = Pflichteingang oder Werkzeug fehlt (nichts
geschrieben), 3 = ein Schritt ist fehlgeschlagen (Name und Rückgabe in der Meldung), 4 = falscher Aufruf.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATEN = Path(os.environ.get("KIEZ_DATEN") or (WURZEL.parent / "kiezatlas-daten" / "krakow"))
POTSDAM = Path(os.environ.get("KIEZ_POTSDAM") or (WURZEL.parent / "kiezatlas-potsdam"))
CONTAINER = "kiezatlas-krakow-db-1"           # Projektname aus docker-compose.yml + Dienst db
HEUTE = dt.date.today().isoformat()

UV = ["uv", "run", "-q", "--offline", "--python", "3.13", "--no-project", "--with-requirements", "requirements.txt"]
PY = [*UV, "python", "-I"]
PY_SCHRIFT = [*UV, "--with-requirements", "requirements-schriften.txt", "python", "-I"]

# Eingänge relativ zu $KIEZ_DATEN (ortsabhängig; Herkunft und Lizenz je Datei in QUELLEN.md)
BDOT = "2026-11-13/03_gebaeude/1261_SHP.zip"
GITTER_PL = "2026-11-13/02_zensus/PL_PD_3035_GPKG.zip"
NSP = "2026-11-13/02_zensus/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx"
OSM = "eingang/*.osm.pbf"
LOD2 = "eingang/lod2_1261*"
GTFS = ["2026-11-13/06_oepnv/GTFS_KRK_A.zip", "2026-11-13/06_oepnv/GTFS_KRK_T.zip",
        "2026-11-13/06_oepnv/GTFS_KRK_M.zip"]
ZBK = "zbk/2026-11-13/zbk_wykaz_2025-12.pdf"
ZBK_REGELN = "zbk/2026-11-13/bip_dok48482_ponowne.html"   # Regeln der Weiterverwendung, Vermerk wörtlich daraus
SCHRIFT_PAKETE = ["schriften/2026-11-13/barlow-5.3.0.tgz", "schriften/2026-11-13/barlow-semi-condensed-5.3.0.tgz"]
SCHRIFT_ANGABEN = ["schriften/2026-11-13/npm-barlow-latest.json", "schriften/2026-11-13/npm-barlow-semi-condensed-latest.json"]
GITTER_DE = "2026-11-14/41_vergleich/DE_PD_3035_GPKG.zip"
BIP_FLAECHE = "2026-11-13/10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html"   # Gegenprobe der Stadtfläche
NOTO = ["NotoSans-Regular.ttf", "NotoSans-Medium.ttf", "NotoSans-Italic.ttf"]
NOTO_REPO = WURZEL / "schriften" / "noto"     # Kartenschrift im Repository (SIL OFL 1.1)


@dataclass
class Schritt:
    name: str
    titel: str
    befehl: list[str]
    pflicht: list[str] = field(default_factory=list)      # Muster relativ zu $KIEZ_DATEN; fehlt eins: Halt
    wahl: list[tuple[str, str]] = field(default_factory=list)  # (Muster, Folge, wenn es fehlt)
    datenbank: bool = False
    auslassen_ohne_wahl: bool = False   # fehlt ein Wahl-Eingang, den Schritt auslassen (Datei bleibt, wie sie ist)
    werkzeuge: list[str] = field(default_factory=list)
    extern: list[tuple[Path, str]] = field(default_factory=list)  # (Pfad, wofür); fehlt er: Schritt auslassen


def mit_rolle(rolle: str, schluessel: str, befehl: list[str]) -> list[str]:
    """Befehl mit Datenbankumgebung wie die Shell-Hüllen (12_osm.sh, 14b_fussweg.sh): .env aus $KIEZ_ENV lesen,
    PG*-Variablen für die Rolle setzen, die übrigen Passwörter entfernen. Im Protokoll stehen nur Variablennamen."""
    skript = ('set -a; . "$KIEZ_ENV"; set +a; '
              'export PGHOST=127.0.0.1 PGPORT="${PG_PORT:-55462}" PGDATABASE="${PG_DATABASE:-kiezatlas}" '
              f'PGUSER={rolle} PGPASSWORD="${schluessel}"; '
              'unset POSTGRES_PASSWORD IMPORT_PASSWORD LESE_PASSWORD RECHNEN_PASSWORD; exec "$@"')
    return ["sh", "-c", skript, "kette", *befehl]


def finde(muster: str) -> list[Path]:
    """Dateien zu einem Muster relativ zu $KIEZ_DATEN; „a | b“ sind Alternativen (eine genügt)."""
    if " | " in muster:
        return sorted({p for m in muster.split(" | ") for p in finde(m)})
    if any(c in muster for c in "*?["):
        return sorted(p for p in DATEN.glob(muster) if p.is_file())
    p = DATEN / muster
    return [p] if p.is_file() else []


def osm_pbf_befehl() -> list[str]:
    """12_osm.sh laden: die übernommene Kopie unter osm/<stand>/, sonst aus eingang/ mit --uebernehmen (KR25)."""
    eingang = finde(OSM)
    if eingang:
        kopie = sorted(DATEN.glob(f"osm/*/{eingang[-1].name}"))
        if kopie:
            return ["sh", "skripte/12_osm.sh", "laden", "--pbf", str(kopie[-1])]
        return ["sh", "skripte/12_osm.sh", "laden", "--uebernehmen", "--pbf", str(eingang[-1])]
    return ["sh", "skripte/12_osm.sh", "laden", "--uebernehmen", "--pbf", f"{DATEN}/{OSM}"]


def noto_ordner() -> Path:
    """Kartenschrift: die Kopie im Repository (schriften/noto/), sonst die aus dem Rohdaten-Schnappschuss
    ($KIEZ_DATEN/schriften/noto/)."""
    if all((NOTO_REPO / n).is_file() for n in NOTO):
        return NOTO_REPO
    kopien = sorted(p for p in DATEN.glob("schriften/noto*") if p.is_dir())
    return kopien[-1] if kopien else NOTO_REPO


def schritte() -> list[Schritt]:
    geb = DATEN / "abgeleitet" / "gebaeude" / f"{HEUTE}-odbl"
    return [
        Schritt("ort", "Ortskonfiguration für die Seiten (config/krakow.yaml → daten/ort.js)",
                [*PY, "skripte/31_ort.py"]),
        Schritt("bevoelkerung", "Gliederung und Bevölkerung: Grenzen, Zellen, Kennzahlen, Steckbrief",
                [*PY, "skripte/02_bevoelkerung.py"], pflicht=[BDOT, GITTER_PL, NSP],
                wahl=[(OSM, "ohne OSM-Auszug keine Grenzen der dzielnice: Gliederung bleibt Beispieldaten"),
                      ("eingang/rejony_statystyczne.*", "ohne Geometrie der rejony bleibt NSP je dzielnica null")]),
        Schritt("uebersicht", "Übersichtsgrenzen der Startseite aus den Grenzen der dzielnice (vereinfacht)",
                [*PY, "skripte/02a_stadtteile_uebersicht.py"]),
        Schritt("db_gliederung", "Grenzen und Zellen in die Datenbank (Rolle admin)",
                ["sh", "-c", "sh skripte/05_db_gliederung.sh ddl && sh skripte/05_db_gliederung.sh laden"],
                datenbank=True, pflicht=[GITTER_PL, OSM]),
        Schritt("osm", "OSM-Einrichtungen und Fußwegnetz in die Datenbank", osm_pbf_befehl(),
                datenbank=True, pflicht=[OSM]),
        Schritt("einrichtungen", "Einrichtungen aus BDOT10k, Ärzte und Apotheken aus OSM",
                mit_rolle("mosidi_lesen", "LESE_PASSWORD", [*PY, "skripte/11_einrichtungen_krakow.py", "--osm-db"]),
                datenbank=True, pflicht=[BDOT]),
        Schritt("oepnv", "Haltestellen und Taktklassen aus dem GTFS", [*PY, "skripte/13_oepnv_krakow.py"],
                pflicht=[*GTFS, BDOT]),
        Schritt("ziele_db", "Ziele der Fußweg-Rechnung in die Datenbank",
                mit_rolle("kiezatlas_rechnen", "RECHNEN_PASSWORD", [*PY, "skripte/14a_ziele_db_krakow.py"]),
                datenbank=True, pflicht=[BDOT]),
        Schritt("fussweg", "Fußweg je Zelle über das OSM-Wegenetz", ["sh", "skripte/14b_fussweg.sh", "rechnen"],
                datenbank=True),
        Schritt("fussweg_export", "Fußweg-Ergebnisse als Seitendaten",
                mit_rolle("mosidi_lesen", "LESE_PASSWORD", [*PY, "skripte/14c_fussweg_export_krakow.py"]),
                datenbank=True),
        Schritt("erreichbarkeit", "Erreichbarkeit je Zelle (Luftlinie)",
                [*PY, "skripte/14_erreichbarkeit_krakow.py"]),
        Schritt("planer", "Versorgung je dzielnica (Luftlinie)", [*PY, "skripte/15_planer_krakow.py"],
                pflicht=[BDOT]),
        Schritt("gebaeude", f"Gebäude, Kennzahlen und 3D-Dateien (nach abgeleitet/gebaeude/{HEUTE}-odbl/)",
                [*PY, "skripte/20_bdot10k.py", "--geometrie", str(geb)], pflicht=[BDOT],
                wahl=[(LOD2, "ohne LoD2 Höhen nur aus der Geschosszahl")]),
        Schritt("grundkarte", "Grundkarte: Vektorkacheln aus BDOT10k (nach abgeleitet/grundkarte/)",
                [*PY, "skripte/27_grundkarte.py", "--schrift-ordner", str(noto_ordner())], pflicht=[BDOT],
                werkzeuge=[f"datei:{noto_ordner() / n}" for n in NOTO]),
        Schritt("luft", "Luft (EEA-Jahresstatistik)", [*PY, "skripte/32_powietrze.py"],
                wahl=[("eingang/eea/*.geojson.zip | eingang/eea/*.geojson | eingang/eea/*.csv",
                       "Handdownload EEA fehlt: powietrze.js bleibt Beispieldaten")]),
        Schritt("klima", "Bodenbedeckung der Stadt, je Zelle und je dzielnica", [*PY, "skripte/35_klimat.py"],
                pflicht=[BDOT], wahl=[(BIP_FLAECHE, "ohne BIP-Seite (keine Lizenzangabe, nicht im Schnappschuss) "
                                                    "entfällt nur die Gegenprobe der Stadtfläche im Beleg")]),
        Schritt("wohnungsmarkt", "Wohnungsmarkt (Mediane des RCN ab 10 Käufen)", [*PY, "skripte/40_mieszkania.py"],
                wahl=[("eingang/rcn/*.gpkg", "Handdownload RCN fehlt: Schritt ausgelassen, mieszkania_odbl.js bleibt "
                                             "Beispieldaten")],
                auslassen_ohne_wahl=True),
        Schritt("denkmale", "Denkmale: BDOT10k, OSM, Register", [*PY, "skripte/dz_denkmale.py"], pflicht=[BDOT],
                wahl=[(OSM, "ohne OSM-Auszug bleibt denkmale_odbl.js Beispieldaten"),
                      ("eingang/wikidata_zabytki_krakow.json", "Handdownload Wikidata fehlt: denkmale.js bleibt "
                                                               "Beispieldaten"),
                      ("eingang/nid_rejestr_zabytkow.csv", "Handdownload NID-Register fehlt"),
                      ("eingang/gez_krakow.csv", "Handdownload gminna ewidencja fehlt")]),
        Schritt("sanierung", "Sanierungsatlas Wohnungsbestand", [*PY, "skripte/36_sanierung.py"],
                pflicht=[ZBK, ZBK_REGELN, BDOT, LOD2, OSM], werkzeuge=["pdftotext"]),
        Schritt("schriften", "Schriften aus den Fontsource-Paketen", [*PY_SCHRIFT, "skripte/schriften.py"],
                pflicht=[*SCHRIFT_PAKETE, *SCHRIFT_ANGABEN]),
        Schritt("vergleich", "Vergleich Kraków–Potsdam (Eurostat-Gitter)",
                [*PY, "skripte/41_porownanie.py", "--potsdam", str(POTSDAM)], pflicht=[GITTER_DE],
                extern=[(POTSDAM / ".git", "Repository des Kiezatlas Potsdam (Stadtgrenze Potsdams); fehlt es, "
                                           "bleibt porownanie.js, wie es ist")]),
        Schritt("export", "Downloads aus den Datendateien (daten/pobierz/)", [*PY, "skripte/16_export_krakow.py"]),
        Schritt("bloecke", "Langtexte aus Quelltexten und Daten", [*PY, "skripte/16_bloecke_krakow.py"]),
        Schritt("seiten", "Seiten in allen Sprachen", [*PY, "skripte/30_seiten.py"]),
        Schritt("pruefen", "alle Prüfungen ohne Netz und Datenbank (./pruefen.sh)", ["sh", "./pruefen.sh"]),
    ]


def env_datei() -> Path:
    if os.environ.get("KIEZ_ENV"):
        return Path(os.environ["KIEZ_ENV"])
    return WURZEL / ".env" if (WURZEL / ".env").is_file() else WURZEL.parent / "kiezatlas-krakow" / ".env"


def datenbank_pruefen() -> list[str]:
    """Voraussetzungen der Datenbank-Schritte; liest nur (keine Verbindung zur Datenbank, keine Werte ausgeben)."""
    fehlt = []
    env = env_datei()
    if not env.is_file():
        fehlt.append(f"Umgebungsdatei {env} fehlt (Vorlage .env.beispiel, chmod 600; docs/uruchomienie.md, Schritt 3)")
    else:
        gesetzt = set()
        for z in env.read_text(encoding="utf-8", errors="replace").splitlines():
            name, _, wert = z.strip().partition("=")
            if name and not name.startswith("#") and wert.strip():
                gesetzt.add(name.strip())
        for n in ("POSTGRES_PASSWORD", "LESE_PASSWORD", "RECHNEN_PASSWORD"):
            if n not in gesetzt:
                fehlt.append(f"{n} in {env} leer oder fehlt")
    if shutil.which("docker") is None:
        fehlt.append("docker nicht gefunden (Datenbank: docker compose up -d --wait db)")
    else:
        r = subprocess.run(["docker", "inspect", "-f", "{{.State.Health.Status}}", CONTAINER],
                           capture_output=True, text=True)
        if r.returncode != 0 or r.stdout.strip() != "healthy":
            fehlt.append(f"Container {CONTAINER} läuft nicht oder ist nicht gesund "
                         f"(„{(r.stdout or r.stderr).strip()[:80]}“); im Wurzelordner des Repositorys (bei Worktrees im "
                         "Haupt-Checkout): docker compose up -d --wait db, "
                         "danach einmal skripte/lauf.sh einrichten")
    return fehlt


def werkzeuge_pruefen(auswahl: list[Schritt], ohne_browser: bool) -> list[str]:
    fehlt = []
    for w in ("uv", "node", "git", "sh"):
        if shutil.which(w) is None:
            fehlt.append(f"Werkzeug {w} nicht gefunden")
    if shutil.which("uv"):
        r = subprocess.run([*UV, "python", "-c", "import yaml, pyproj, shapely, numpy"], cwd=WURZEL,
                           capture_output=True, text=True)
        if r.returncode != 0:
            letzte = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["?"]
            fehlt.append("uv findet Python 3.13 oder die Pakete aus requirements.txt nicht im Zwischenspeicher "
                         f"(„{letzte[0][:160]}“); einmalig mit Netz vorbereiten, docs/uruchomienie.md, Schritt 2")
        namen = {s.name for s in auswahl}
        zusatz = [("schriften", "requirements-schriften.txt", "fontTools"), ("pruefen", "requirements-pruefen.txt", "pytest")]
        for schritt, datei, modul in zusatz:
            if schritt in namen:
                r = subprocess.run([*UV, "--with-requirements", datei, "python", "-c", f"import {modul}"], cwd=WURZEL,
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    fehlt.append(f"{schritt}: Pakete aus {datei} nicht im uv-Zwischenspeicher (docs/uruchomienie.md, Schritt 2)")
    if any(s.name == "pruefen" for s in auswahl) and not (WURZEL / "node_modules").exists():
        fehlt.append("node_modules fehlt (npm ci; für die Browserprüfungen dazu npx playwright install chromium)")
    for s in auswahl:
        for w in s.werkzeuge:
            if w.startswith("datei:"):
                if not Path(w[6:]).is_file():
                    fehlt.append(f"{s.name}: Datei {w[6:]} fehlt (Kartenschrift Noto Sans; liegt im Repository "
                                 "unter schriften/noto/, ersatzweise aus dem Rohdaten-Schnappschuss "
                                 "unter $KIEZ_DATEN/schriften/noto/)")
            elif shutil.which(w) is None:
                fehlt.append(f"{s.name}: Werkzeug {w} nicht gefunden")
    return fehlt


def auswaehlen(alle: list[Schritt], args) -> list[Schritt]:
    namen = [s.name for s in alle]
    for n in [*(args.nur or []), *([args.ab] if args.ab else [])]:
        if n not in namen:
            raise SystemExit(f"unbekannter Schritt „{n}“; Schritte: {', '.join(namen)}")
    auswahl = alle
    if args.ab:
        auswahl = auswahl[namen.index(args.ab):]
    if args.nur:
        auswahl = [s for s in auswahl if s.name in args.nur]
    if args.ohne_datenbank:
        auswahl = [s for s in auswahl if not s.datenbank]
    return auswahl


def planen(auswahl: list[Schritt], args) -> tuple[list[str], list[str], dict[str, str]]:
    """(fehlt: Halt, hinweise, auslassen: name -> Grund)."""
    fehlt: list[str] = []
    hinweise: list[str] = []
    auslassen: dict[str, str] = {}
    if not DATEN.is_dir():
        fehlt.append(f"Rohdatenordner $KIEZ_DATEN = {DATEN} fehlt")
    fehlende: dict[str, list[str]] = {}
    for s in auswahl:
        for m in s.pflicht:
            if not finde(m):
                fehlende.setdefault(m, []).append(s.name)
        for m, folge in s.wahl:
            if not finde(m):
                hinweise.append(f"{s.name}: $KIEZ_DATEN/{m} fehlt → {folge}")
                if s.auslassen_ohne_wahl:
                    auslassen[s.name] = folge
        for pfad, wofuer in s.extern:
            if not pfad.exists():
                auslassen[s.name] = f"{pfad.parent} fehlt: {wofuer}"
                hinweise.append(f"{s.name}: {pfad.parent} fehlt → {wofuer}")
    fehlt += [f"Pflichteingang $KIEZ_DATEN/{m} fehlt (gebraucht von: {', '.join(n)})" for m, n in fehlende.items()]
    if any(s.datenbank for s in auswahl):
        fehlt += [f"Datenbank: {f}" for f in datenbank_pruefen()]
    fehlt += werkzeuge_pruefen(auswahl, args.ohne_browser)
    return fehlt, hinweise, auslassen


def zeige(text: str, log) -> None:
    print(text, flush=True)
    if log:
        log.write(text + "\n")
        log.flush()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("modus", choices=["trocken", "alles", "liste"])
    ap.add_argument("--ohne-datenbank", action="store_true")
    ap.add_argument("--ohne-browser", action="store_true")
    ap.add_argument("--ab", metavar="SCHRITT")
    ap.add_argument("--nur", metavar="SCHRITT", action="append")
    try:
        args = ap.parse_args()
    except SystemExit as e:
        return 4 if e.code else 0
    os.chdir(WURZEL)
    os.environ["KIEZ_ENV"] = str(env_datei().resolve()) if env_datei().exists() else str(env_datei())
    alle = schritte()
    if args.modus == "liste":
        for i, s in enumerate(alle, 1):
            print(f"{i:2}. {s.name:15} {'[Datenbank] ' if s.datenbank else ''}{s.titel}")
        return 0
    try:
        auswahl = auswaehlen(alle, args)
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 4
    log = None
    if args.modus == "alles":
        (WURZEL / "berichte" / "kette").mkdir(parents=True, exist_ok=True)
        log = open(WURZEL / "berichte" / "kette" / f"{dt.datetime.now(dt.UTC):%Y%m%dT%H%M%SZ}.log", "w",
                   encoding="utf-8")
    zeige(f"Kiezatlas Kraków, Kette ({args.modus}), {dt.datetime.now():%d.%m.%Y %H:%M}", log)
    zeige(f"Repository: {WURZEL.name}, Commit {subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip() or 'unbekannt'}", log)
    zeige(f"Rohdaten ($KIEZ_DATEN): {DATEN}", log)
    praefix = shlex.split(os.environ.get("KETTE_PRAEFIX", ""))
    fehlt, hinweise, auslassen = planen(auswahl, args)
    zeige(f"\nSchritte ({len(auswahl)} von {len(alle)}):", log)
    for i, s in enumerate(auswahl, 1):
        mark = "auslassen" if s.name in auslassen else "ausführen"
        zeige(f"  {i:2}. {s.name:15} {mark:9} {'[Datenbank] ' if s.datenbank else ''}{s.titel}", log)
    if hinweise:
        zeige(f"\nHinweise ({len(hinweise)}), kein Halt:", log)
        for h in hinweise:
            zeige(f"  - {h}", log)
    if fehlt:
        zeige(f"\nHALT: {len(fehlt)} Voraussetzung(en) fehlen, nichts wurde geschrieben:", log)
        for f in fehlt:
            zeige(f"  - {f}", log)
        zeige("Wege zu den Eingängen: docs/uruchomienie.md bzw. docs/running.md, Abschnitt „Quellen“.", log)
        return 2
    if args.modus == "trocken":
        zeige("\nTrockenlauf grün: alle Pflichteingänge und Werkzeuge der gewählten Schritte sind da.", log)
        return 0
    for i, s in enumerate(auswahl, 1):
        if s.name in auslassen:
            zeige(f"\n[{i}/{len(auswahl)}] {s.name}: ausgelassen ({auslassen[s.name]})", log)
            continue
        befehl = [*praefix, *s.befehl] if s.name != "pruefen" else [*s.befehl, *(["--ohne-browser"] if args.ohne_browser else [])]
        zeige(f"\n[{i}/{len(auswahl)}] {s.name}: {s.titel}\n  $ {shlex.join(befehl)}", log)
        start = dt.datetime.now()
        r = subprocess.run(befehl, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if log:
            log.write(r.stdout)
        print("\n".join("  | " + z for z in r.stdout.rstrip().splitlines()[-8:]))
        dauer = (dt.datetime.now() - start).total_seconds()
        if r.returncode != 0:
            zeige(f"HALT: Schritt {s.name} mit Rückgabe {r.returncode} nach {dauer:.0f} s; volle Ausgabe im Protokoll "
                  f"berichte/kette/. Weiter nach der Behebung mit: ./atlas.sh alles --ab {s.name}", log)
            return 3
        zeige(f"  fertig in {dauer:.0f} s", log)
    zeige("\nKette fertig. Neue Rohdatenstände und bewegte Zahlen gehören ins CHANGELOG (docs/rundgang.md, "
          "„Neuer Datenstand“).", log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
