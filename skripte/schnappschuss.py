"""Rohdaten-Schnappschuss: nur weiterverbreitbare Rohdaten als ein Archiv, mit Prüfsummen und Lizenzliste.

Dritter Quellweg der Kette (docs/uruchomienie.md, docs/running.md): Wer den Schnappschuss in einen leeren Ordner
auspackt und $KIEZ_DATEN darauf zeigen lässt, kann die Kette rechnen, auch wenn eine Quelle verschwindet oder umzieht.
Das Archiv wird nur lokal geschrieben; hochladen (etwa als eigener Zenodo-Eintrag) ist ein eigener, freizugebender
Schritt.

Aufgenommen wird nur, was eine Regel in AUFNEHMEN ausdrücklich erlaubt (Quelle, Lizenz, Vermerk). Alles andere bleibt
draußen und steht mit Grund in AUSGESCHLOSSEN.md (Regeln in AUSSCHLIESSEN, sonst „nicht eingeordnet“). Vorsichtig
gilt: Lizenz nicht geprüft, Lizenz-STOPP, Personenbezug, Webseiten Dritter → draußen. Die Kartenschrift (Noto Sans,
SIL OFL 1.1) liegt nicht unter $KIEZ_DATEN, sondern im Repository unter schriften/noto/; sie kommt mit, wenn ihre
Prüfsummen zu skripte/27_grundkarte.py passen, unter schriften/noto/ (Aufruf dann mit --schrift-ordner).

Archiv (GNU-tar-Format, unkomprimiert, weil die Dateien schon gepackt sind), byte-gleich wiederholbar: Dateien
sortiert, Besitzer 0, Rechte 0644, Zeit = --stand 00:00 UTC. Pfade wie unter $KIEZ_DATEN; dazu im Ordner
SCHNAPPSCHUSS/: SHA256SUMS (jede Datei), LIZENZEN.md (Quelle, Lizenz, Vermerk wörtlich), AUSGESCHLOSSEN.md (Datei,
Grund, SHA256). Neben das Archiv schreibt das Skript <archiv>.sha256.

Vor dem Schreiben: jede aufgenommene Datei, die in belege/rohdaten*.sha256 steht, muss dort dieselbe Prüfsumme haben
(sonst Abbruch); freier Platz am Ziel muss reichen.

Aufruf (nur Standardbibliothek):
  python3 -I skripte/schnappschuss.py --ziel ORDNER [--stand JJJJ-MM-TT] [--trocken]
  python3 -I skripte/schnappschuss.py --pruefen ARCHIV     Archiv gegen sein SCHNAPPSCHUSS/SHA256SUMS prüfen
Umgebung: KIEZ_DATEN (Standard ../kiezatlas-daten/krakow).
Rückgabe 0 = geschrieben bzw. stimmig, 1 = Abweichung, 2 = falscher Aufruf oder zu wenig Platz.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import io
import os
import re
import shutil
import struct
import sys
import tarfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATEN = Path(os.environ.get("KIEZ_DATEN") or (WURZEL.parent / "kiezatlas-daten" / "krakow"))
NOTO_QUELLE = WURZEL / "schriften" / "noto"
NOTO_ZIEL = "schriften/noto"

GUGIK = ("kostenfrei, ohne Lizenz (art. 40a ust. 2 pkt 1, art. 40c ust. 5), Quellenangabe nach art. 40c ust. 3 "
         "Prawo geodezyjne i kartograficzne (Dz.U. 2026 poz. 1389)")
# Muster relativ zu $KIEZ_DATEN -> (Quelle, Lizenz, Vermerk wörtlich, wie in QUELLEN.md)
AUFNEHMEN = [
    ("2026-11-13/03_gebaeude/1261_SHP.zip", "GUGiK, BDOT10k, Powiat 1261 (Kraków), Schema 2021, SHP", GUGIK,
     "Źródło: Baza Danych Obiektów Topograficznych (BDOT10k), państwowy zasób geodezyjny i kartograficzny, Główny "
     "Urząd Geodezji i Kartografii; Geoportal: „Baza BDOT10k jest dostępna bezpłatnie i możliwa do dowolnego "
     "wykorzystania.“"),
    ("eingang/lod2_1261*.zip", "GUGiK, Modele 3D budynków LoD2, Powiat 1261 (Stand 2017)", GUGIK,
     "„Modele 3D budynków są dostępne bezpłatnie i możliwe do dowolnego wykorzystania.“ "
     "(https://www.geoportal.gov.pl/pl/dane/inne-dane/modele-3d-budynkow/)"),
    ("eingang/*.osm.pbf", "OpenStreetMap, Auszug Małopolska (Geofabrik)", "ODbL 1.0, © OpenStreetMap-Mitwirkende",
     "„OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the "
     "OpenStreetMap Foundation (OSMF).“ (https://www.openstreetmap.org/copyright)"),
    ("2026-11-13/02_zensus/PL_PD_3035_GPKG.zip", "Eurostat, Census 2021 population grid, Polen, 1 km", "CC BY 4.0",
     "„EU copyright rules apply, while the licence would be under CC-BY 4.0.“ Nennung: Eurostat, Census 2021 "
     "population grid"),
    ("2026-11-14/41_vergleich/DE_PD_3035_GPKG.zip", "Eurostat, Census 2021 population grid, Deutschland, 1 km",
     "CC BY 4.0", "„EU copyright rules apply, while the licence would be under CC-BY 4.0.“ Nennung: Eurostat, "
     "Census 2021 population grid"),
    ("2026-11-13/02_zensus/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx",
     "Główny Urząd Statystyczny, NSP 2021 je rejon statystyczny und obwód spisowy", "Kopieren mit Quellenangabe",
     "„Główny Urząd Statystyczny: nie ma zastrzeżeń co do kopiowania plików i stron oraz dokonywania wydruków, w tym "
     "do własnych opracowań, pod warunkiem, że będzie podane ich źródło“"),
    ("2026-11-13/06_oepnv/GTFS_KRK_*.zip", "Zarząd Transportu Publicznego w Krakowie, GTFS (Bus, Tram, Mobilis)",
     "CC BY 4.0", "„Licencja: Creative Commons (CC BY 4.0)“ (https://gtfs.ztp.krakow.pl/)"),
    ("schriften/*/barlow-*.tgz", "Fontsource @fontsource/barlow, @fontsource/barlow-semi-condensed 5.3.0",
     "SIL Open Font License 1.1 (Lizenztext im Paket, package/LICENSE)",
     "„Copyright 2017 The Barlow Project Authors (https://github.com/jpt/barlow)“"),
    ("eingang/gus_brec/AreaStatisticalUnit_12.zip",
     "Główny Urząd Statystyczny, Jednostki statystyczne 2021 (BREC), województwo małopolskie (INSPIRE, EPSG:4258)",
     "keine Bedingungen (Feed INSPIRE des GUS, <rights>)",
     "„Brak warunków dostępu i użytkowania; Brak ograniczeń w publicznym dostępie“"),
    ("eingang/SHA256SUMS", "eigene Prüfsummenliste der Handdownloads", "Apache-2.0 (eigene Angabe)", "–"),
    ("eingang/eea/eea_aq_statistik_krakow_*.geojson.zip",
     "European Environment Agency, Air quality annual statistics (Auszug City = Kraków); Messwerte der GIOŚ",
     "CC BY 4.0", "„License CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Copyright holder: European "
     "Commission.“ Nennung: EEA; Daten: GIOŚ"),
    ("eingang/wikidata_zabytki_krakow.json",
     "Wikidata, Objekte mit polnischer Denkmal-Registernummer in Kraków (Ergebnis der Abfrage in quellen-DZ.md)",
     "CC0 1.0", "„All structured data (i.e. the main, Property, Lexeme, and EntitySchema namespaces) is released into "
     "the public domain under Creative Commons Zero.“ (https://www.wikidata.org/wiki/Wikidata:Licensing)"),
]
NOTO_REGEL = ("Noto Sans Regular, Medium, Italic (Kartenschrift der Grundkarte)", "SIL Open Font License 1.1",
              "Copyright aus der name-Tabelle der Schrift (Eintrag 0), Lizenzvermerk Eintrag 13; Lizenztext in OFL.txt")

PERSONEN_ZBK = ("Personenbezug: das Autorfeld der PDF nennt Bearbeiter, die Spalte „Własność“ Bruchteile von "
                "Privatpersonen (Sanierungsatlas, nur Klassen veröffentlicht); Weiterverwendung an sich erlaubt, aber "
                "die Rohdatei wird nicht weitergegeben. Handabruf über die Adresse in QUELLEN.md, Prüfsumme hier")
# Muster -> Grund; erste passende Regel gilt. Was keine Regel trifft: „nicht eingeordnet“ (bleibt draußen).
AUSSCHLIESSEN = [
    ("eingang/rcn/*", "Rejestr cen nieruchomości: Einzeltransaktionen mit Lage, Datum und Preis (möglicher "
                      "Personenbezug), keine Lizenz erteilt; veröffentlicht werden nur Mediane ab 10 Käufen (KR55). "
                      "Handdownload nach quellen-DW.md, Prüfsumme hier"),
    ("eingang/_wartend/*", "Wartebereich der Handdownloads; Inhalt nach eingang/ übernommen (eingang/HERKUNFT.md)"),
    ("eingang/wikidata_licensing_*.txt", "Abschrift der Lizenzseite von Wikidata (Seitentext unter CC BY-SA 4.0) als "
                                         "Beleg; Fundstelle in QUELLEN.md"),
    ("zbk/*/zbk_wykaz_*.pdf", PERSONEN_ZBK),
    ("zbk/*/bip_dok48482_ponowne.html", "Seite des BIP (Regeln der Weiterverwendung der Gmina Miejska Kraków) als "
                                        "Beleg; skripte/36_sanierung.py liest den Vermerk daraus: nach dem Auspacken mit "
                                        "skripte/abruf.py holen (docs/uruchomienie.md)"),
    ("2026-11-13/01_stadtteile/*", "Grenzen aus dem städtischen Portal MSIP und Seiten des BIP: Lizenz-STOPP "
                                   "(Nutzungsbedingungen nur nicht kommerziell, ohne Weitergabe)"),
    ("osm/*/*.osm.pbf", "Kopie des OSM-Auszugs aus eingang/ (gleiche Prüfsumme, KR25); nur einmal aufgenommen"),
    ("*/HERKUNFT.md", "Arbeitsvermerke des Abrufs; Quelle, Lizenz und Vermerk stehen in SCHNAPPSCHUSS/LIZENZEN.md"),
    ("HERKUNFT.md", "Arbeitsvermerke des Abrufs; Quelle, Lizenz und Vermerk stehen in SCHNAPPSCHUSS/LIZENZEN.md"),
    ("abgeleitet/*", "abgeleitete Ausgaben (Grundkarte, Gebäude in 3D, Rohtext der ZBK-Liste); die Kette erzeugt sie "
                     "neu"),
    ("abrufprotokoll.*", "Abrufprotokoll des Betreibers; jeder Betreiber führt sein eigenes"),
    ("_robots/*", "robots.txt-Befunde gelten 30 Tage; jeder Betreiber erhebt sie neu"),
    ("*/.abruf/*", "Sperr- und Zeitdateien des Abrufs"),
    ("2026-11-13/_werkzeug/*", "Hilfsskripte der Machbarkeitsprobe, nicht Teil der Kette"),
    ("2026-11-13/_auswertung/*", "Zwischenauswertungen der Machbarkeitsprobe, nicht Teil der Kette"),
    ("2026-11-13/04_bauzeit/*", "Probe der Machbarkeitsprüfung (robots.txt von zabytek.pl), nicht Teil der Kette"),
    ("2026-11-13/10_statistik/*.json", "Antworten der GUS-Datenbank BDL, nur Gegenprobe; Lizenz nicht geprüft"),
    ("eea/*/viewer/*", "Code und Einstellungen des EEA-Betrachters (Dritte), nur Beleg"),
    ("eea/*/test/*", "Probeabfragen an den EEA-Betrachter, nur Beleg"),
    ("schriften/*/npm-*.json", "Paketangaben der npm-Registry mit E-Mail-Adressen der Paketbetreuer (Personenbezug); "
                               "skripte/schriften.py braucht sie: nach dem Auspacken mit skripte/abruf.py holen, "
                               "Fassung 5.3.0 (docs/uruchomienie.md)"),
    ("2026-11-13/10_statistik/bip_dok242410_*.html", "Seite des BIP ohne Lizenzangabe, nur Gegenprobe der "
                                                    "Stadtfläche; skripte/35_klimat.py braucht sie: nach dem Auspacken "
                                                    "mit skripte/abruf.py holen (docs/uruchomienie.md)"),
    ("*.html", "Abzug einer Webseite Dritter als Beleg (Lizenz, Fundstelle); nicht von einer Datenlizenz gedeckt"),
    ("*.xml", "Metadaten oder Capabilities eines Dienstes als Beleg; für die Kette nicht nötig"),
    ("*.json", "Metadaten (ELI, Registry) als Beleg; für die Kette nicht nötig"),
    ("*.pdf", "Rechtstext oder Dokumentation als Beleg; für die Kette nicht nötig, Fundstelle in QUELLEN.md"),
    ("*.png", "Abbildung einer Webseite Dritter als Beleg"),
    ("*.lock", "Sperrdatei"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def zahl(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def passt(rel: str, muster: str) -> bool:
    return fnmatch.fnmatchcase(rel, muster)


def belege_summen() -> dict[str, set[str]]:
    summen: dict[str, set[str]] = {}
    for liste in sorted((WURZEL / "belege").glob("rohdaten*.sha256")):
        for z in liste.read_text(encoding="utf-8").splitlines():
            teile = z.split(None, 1)
            if len(teile) == 2:
                summen.setdefault(teile[1].lstrip("*").strip(), set()).add(teile[0].lower())
    return summen


def noto_soll() -> dict[str, str]:
    """Datei -> SHA256 der Kartenschrift aus skripte/27_grundkarte.py (SCHRIFTEN), ohne das Skript zu importieren."""
    text = (WURZEL / "skripte" / "27_grundkarte.py").read_text(encoding="utf-8")
    return dict(re.findall(r'\("(NotoSans-[A-Za-z]+\.ttf)",\s*"([0-9a-f]{64})"\)', text))


def ttf_copyright(p: Path) -> str | None:
    """Eintrag 0 (Copyright) der name-Tabelle, Windows-Plattform (UTF-16BE)."""
    d = p.read_bytes()
    n = struct.unpack(">H", d[4:6])[0]
    for i in range(n):
        tag, _, off, _ = struct.unpack(">4sIII", d[12 + 16 * i: 28 + 16 * i])
        if tag == b"name":
            _, cnt, start = struct.unpack(">HHH", d[off:off + 6])
            for j in range(cnt):
                pid, eid, lid, nid, ln, so = struct.unpack(">HHHHHH", d[off + 6 + 12 * j: off + 18 + 12 * j])
                if nid == 0 and pid == 3:
                    return d[off + start + so: off + start + so + ln].decode("utf-16-be")
    return None


def ofl_text(copyright_zeile: str) -> str:
    ofl = (WURZEL / "fonts" / "OFL.txt").read_text(encoding="utf-8")
    i = ofl.index("SIL OPEN FONT LICENSE")
    return (f"{copyright_zeile}\n\nThis Font Software is licensed under the SIL Open Font License, Version 1.1.\n"
            "This license is copied below, and is also available with a FAQ at:\nhttps://scripts.sil.org/OFL\n\n\n"
            + ofl[i:])


def einordnen() -> tuple[list[tuple[str, Path, tuple]], list[tuple[str, str, str]]]:
    """(aufgenommen: rel, Pfad, Regel), (ausgeschlossen: rel, Grund, SHA256)."""
    rein, raus = [], []
    eingang_pbf = {p.name: sha256(p) for p in DATEN.glob("eingang/*.osm.pbf")}
    for p in sorted(x for x in DATEN.rglob("*") if x.is_file()):
        rel = p.relative_to(DATEN).as_posix()
        regel = next((r for r in AUFNEHMEN if passt(rel, r[0])), None)
        if regel:
            rein.append((rel, p, regel))
            continue
        grund = next((g for m, g in AUSSCHLIESSEN if passt(rel, m)), None)
        if rel.startswith("osm/") and rel.endswith(".osm.pbf") and eingang_pbf.get(p.name) != sha256(p):
            grund = None    # andere Fassung als im Eingang: nicht still verwerfen
        raus.append((rel, grund or "nicht eingeordnet (keine Regel in skripte/schnappschuss.py); vorsichtshalber "
                                    "ausgeschlossen", sha256(p)))
    return rein, raus


def schreiben(args) -> int:
    stand = args.stand
    zeit = int(dt.datetime.fromisoformat(stand).replace(tzinfo=dt.UTC).timestamp())
    rein, raus = einordnen()
    summen = belege_summen()
    eintraege: list[tuple[str, bytes | Path]] = []
    lizenz_zeilen = []
    abweichung = []
    geprueft = 0
    for rel, p, regel in rein:
        h = sha256(p)
        if rel in summen:
            geprueft += 1
            if h not in summen[rel]:
                abweichung.append(f"{rel}: {h} nicht in belege/rohdaten*.sha256")
        eintraege.append((rel, p))
        lizenz_zeilen.append((rel, h, p.stat().st_size, *regel[1:]))
    soll = noto_soll()
    noto_dateien = []
    if soll and all((NOTO_QUELLE / f).is_file() and sha256(NOTO_QUELLE / f) == h for f, h in soll.items()):
        cr = ttf_copyright(NOTO_QUELLE / sorted(soll)[0]) or "Copyright The Noto Project Authors"
        for f in sorted(soll):
            noto_dateien.append(f"{NOTO_ZIEL}/{f}")
            eintraege.append((f"{NOTO_ZIEL}/{f}", NOTO_QUELLE / f))
            lizenz_zeilen.append((f"{NOTO_ZIEL}/{f}", soll[f], (NOTO_QUELLE / f).stat().st_size, *NOTO_REGEL))
        ofl = ofl_text(cr).encode("utf-8")
        eintraege.append((f"{NOTO_ZIEL}/OFL.txt", ofl))
        lizenz_zeilen.append((f"{NOTO_ZIEL}/OFL.txt", hashlib.sha256(ofl).hexdigest(), len(ofl),
                              "Lizenztext der Kartenschrift", "SIL Open Font License 1.1", cr))
        noto_hinweis = f"Kartenschrift aufgenommen ({len(soll)} Dateien, Prüfsummen wie skripte/27_grundkarte.py)"
    else:
        noto_hinweis = ("Kartenschrift NICHT aufgenommen: Dateien unter schriften/noto/ fehlen oder Prüfsummen passen nicht zu "
                        "skripte/27_grundkarte.py")
    if abweichung:
        print("Abbruch: Prüfsummen weichen von belege/ ab:", *abweichung, sep="\n  ")
        return 1
    # Begleitdateien
    lz = ["# Rohdaten-Schnappschuss Kiezatlas Kraków: Lizenzen", "",
          f"Stand {stand}. Jede Datei behält die Lizenz ihrer Quelle; Quellenangaben bei jeder Weitergabe mitführen. "
          "Mehr in QUELLEN.md und daten/LIZENZ.md des Repositorys.", "",
          "| Datei | Bytes | SHA256 | Quelle | Lizenz | Vermerk (Original) |", "|---|---|---|---|---|---|"]
    for rel, h, groesse, quelle, lizenz, vermerk in lizenz_zeilen:
        lz.append(f"| `{rel}` | {zahl(groesse)} | `{h}` | {quelle} | {lizenz} | {vermerk} |")
    au = ["# Rohdaten-Schnappschuss Kiezatlas Kraków: ausgeschlossen", "",
          f"Stand {stand}. Diese Dateien liegen beim Betreiber unter $KIEZ_DATEN, gehen aber nicht in den Schnappschuss. "
          "Wer sie braucht, holt sie nach docs/uruchomienie.md (Abschnitt „Quellen“) und vergleicht die Prüfsumme.",
          "Die Prüfsummenlisten belege/rohdaten*.sha256 nennen einige davon; `./pruefen.sh` meldet sie als fehlend, "
          "solange sie nicht von Hand ergänzt sind.", "",
          "| Datei | SHA256 | Grund |", "|---|---|---|"]
    for rel, grund, h in raus:
        au.append(f"| `{rel}` | `{h}` | {grund} |")
    lz_b = ("\n".join(lz) + "\n").encode("utf-8")
    au_b = ("\n".join(au) + "\n").encode("utf-8")
    eintraege += [("SCHNAPPSCHUSS/LIZENZEN.md", lz_b), ("SCHNAPPSCHUSS/AUSGESCHLOSSEN.md", au_b)]
    sums = []
    for rel, quelle in sorted(eintraege):
        h = hashlib.sha256(quelle).hexdigest() if isinstance(quelle, bytes) else next(
            (z[1] for z in lizenz_zeilen if z[0] == rel), None) or sha256(quelle)
        sums.append(f"{h}  {rel}")
    sums_b = ("\n".join(sums) + "\n").encode("utf-8")
    eintraege.append(("SCHNAPPSCHUSS/SHA256SUMS", sums_b))
    eintraege.sort(key=lambda e: e[0])
    bytes_gesamt = sum(len(q) if isinstance(q, bytes) else q.stat().st_size for _, q in eintraege)
    print(f"Rohdaten: {DATEN}")
    print(f"aufgenommen: {len(rein)} Dateien unter $KIEZ_DATEN, {len(noto_dateien)} Schriftdateien, 4 Begleitdateien")
    print(f"ausgeschlossen: {len(raus)} Dateien (Gründe in SCHNAPPSCHUSS/AUSGESCHLOSSEN.md)")
    print(f"gegen belege/rohdaten*.sha256 geprüft: {geprueft} von {len(rein)} aufgenommenen Dateien, 0 Abweichungen")
    print(noto_hinweis)
    print(f"Inhalt: {zahl(bytes_gesamt)} Byte")
    for rel, h, groesse, quelle, lizenz, _ in lizenz_zeilen:
        print(f"  + {rel}  ({zahl(groesse)} B; {lizenz})")
    nicht_eingeordnet = [r for r in raus if r[1].startswith("nicht eingeordnet")]
    for rel, _, _ in nicht_eingeordnet:
        print(f"  ? {rel}: nicht eingeordnet, ausgeschlossen")
    if args.trocken:
        print("Trockenlauf: nichts geschrieben.")
        return 0
    ziel = args.ziel.resolve()
    ziel.mkdir(parents=True, exist_ok=True)
    frei = shutil.disk_usage(ziel).free
    if frei < bytes_gesamt * 1.05 + 10 * 1024 * 1024:
        print(f"Zu wenig Platz unter {ziel}: frei {zahl(frei)} B, gebraucht etwa {zahl(int(bytes_gesamt))} B")
        return 2
    archiv = ziel / f"kiezatlas-krakow-rohdaten-{stand}.tar"
    with tarfile.open(archiv, "w", format=tarfile.GNU_FORMAT) as tar:
        for rel, quelle in eintraege:
            info = tarfile.TarInfo(rel)
            info.mtime, info.mode, info.uid, info.gid, info.uname, info.gname = zeit, 0o644, 0, 0, "", ""
            if isinstance(quelle, bytes):
                info.size = len(quelle)
                tar.addfile(info, io.BytesIO(quelle))
            else:
                info.size = quelle.stat().st_size
                with quelle.open("rb") as f:
                    tar.addfile(info, f)
    h = sha256(archiv)
    (ziel / (archiv.name + ".sha256")).write_text(f"{h}  {archiv.name}\n", encoding="utf-8")
    print(f"\nArchiv: {archiv}\n  {zahl(archiv.stat().st_size)} Byte, SHA256 {h}")
    print(f"Prüfsumme: {ziel / (archiv.name + '.sha256')}")
    return 0


def pruefen(archiv: Path) -> int:
    with tarfile.open(archiv) as tar:
        namen = {m.name: m for m in tar.getmembers() if m.isfile()}
        if "SCHNAPPSCHUSS/SHA256SUMS" not in namen:
            print("SCHNAPPSCHUSS/SHA256SUMS fehlt im Archiv")
            return 1
        soll = {}
        for z in tar.extractfile(namen["SCHNAPPSCHUSS/SHA256SUMS"]).read().decode().splitlines():
            h, rel = z.split("  ", 1)
            soll[rel] = h
        fehler = 0
        for rel, h in sorted(soll.items()):
            m = namen.get(rel)
            ist = hashlib.sha256(tar.extractfile(m).read()).hexdigest() if m else None
            if ist != h:
                print(f"  FEHLT/ABWEICHUNG {rel}")
                fehler += 1
        fremd = sorted(set(namen) - set(soll) - {"SCHNAPPSCHUSS/SHA256SUMS"})
        for rel in fremd:
            print(f"  nicht in SHA256SUMS: {rel}")
        print(f"{len(soll)} Dateien in SHA256SUMS, {fehler} Abweichungen, {len(fremd)} ohne Prüfsumme")
        return 1 if fehler or fremd else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ziel", type=Path)
    ap.add_argument("--stand", default=dt.date.today().isoformat())
    ap.add_argument("--trocken", action="store_true")
    ap.add_argument("--pruefen", type=Path, metavar="ARCHIV")
    a = ap.parse_args()
    if a.pruefen:
        return pruefen(a.pruefen)
    if not DATEN.is_dir():
        print(f"$KIEZ_DATEN = {DATEN} fehlt")
        return 2
    if not a.ziel and not a.trocken:
        print("--ziel ORDNER fehlt (oder --trocken)")
        return 2
    if a.ziel and a.ziel.resolve().is_relative_to(WURZEL):
        print("--ziel darf nicht im Repository liegen (das Archiv gehört nicht ins Repo)")
        return 2
    return schreiben(a)


if __name__ == "__main__":
    sys.exit(main())
