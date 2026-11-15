# Rundgang: vom Rohdatensatz zur Seite

Stand: Gerüst vom 13.11.2026, Datenpakete der Phase Datenpakete übernommen am 13.11.2026, am Abend der Echtlauf der Daten,
der Sanierungsatlas und das Paket Schrift und Grundkarte; am 14.11.2026 die vier Seitenpakete der Phase Seitenbau
(Erzählung, Karte, Steckbrief, Vergleich; Planer, Kamienice, Sanierungsatlas; Themenseiten Luft, Wohnungsmarkt,
Klima; Methode, Daten, Downloads); am Abend des 14.11.2026 die Handdownloads für Luft (EEA), Wohnungsmarkt (RCN)
und Denkmalregister (Wikidata). Alle Themen sind mit echten Daten gerechnet; keine Datei trägt mehr Beispieldaten
(`fixture: true`; die Kennzeichnung bleibt für den Fall ohne Rohdaten, `docs/entscheidungen.md`, KR6, KR40). Alle 18 Seiten laden ihre Daten aus
`daten/`; `denkmale.js` (Register aus Wikidata) laden seit dem 14.11.2026 `kamienice` und `karta` (Ebene `rejestr`). Welche Datei echt ist,
steht unten unter „Datenstand je Thema“. Fehlende Angaben stehen
unten ausdrücklich als „nicht angegeben“. Die Vorlage ist der Kiezatlas Potsdam (Stand `7b6eb08`, Tag
`stand-2026-11-07b`); der Code ist ohne dessen Historie und ohne dessen Daten übernommen.

## Was man braucht

| Werkzeug | Version | Wofür |
|---|---|---|
| uv | 0.11.3 (Kopf jedes Prüfprotokolls) | Python-Umgebung aus `requirements.txt`, nur aus dem Zwischenspeicher (`--offline`) |
| Python | 3.13 (zuletzt 3.13.12, Kopf jedes Prüfprotokolls) | `skripte/`, `pruefen/*.py` |
| Python-Pakete | `requirements.txt` (mit Hashes, Stand 06.11.2026 aus Potsdam) | pyyaml, pyproj, numpy, scipy, shapely, psycopg, pillow |
| Python-Pakete für Prüfungen und Schriften | `requirements-pruefen.txt` (pytest 9.2.0), `requirements-schriften.txt` (fontTools 4.68.0, brotli 1.2.1), je mit Hashes | Abrufwerkzeug-Tests, Schriften erzeugen und prüfen |
| Poppler `pdftotext` | 26.10.0 (Systempaket, Version im Beleg `belege/DS_sanierung_lauf.md`) | ZBK-Liste lesen (Sanierungsatlas) |
| Node.js | 22 (zuletzt v22.23.4, Kopf jedes Prüfprotokolls) | `pruefen/*.mjs` |
| Playwright, axe-core | 1.64.1 und 4.14.0 laut `package-lock.json` | Browserprüfungen, Chromium unter `~/.cache/ms-playwright` |
| PostGIS | `postgis/postgis:16-3.6` per Digest (`docker-compose.yml`) | Auswertung; nur auf 127.0.0.1, Projekt `kiezatlas-krakow`, Port 55462 |
| Geodaten-Import-Pipeline | nicht angegeben (Stand wird ab dem ersten Lauf mit `git describe` im Laufbericht festgehalten) | `pipeline.laden` |

Rohdaten liegen unter `$KIEZ_DATEN`, Standard `../kiezatlas-daten/krakow`, je Quelle `HERKUNFT.md`, Prüfsummen beim
Abruf in `belege/rohdaten*.sha256`.

## Schritte

Python-Aufrufe immer als `uv run --offline --python 3.13 --no-project --with-requirements requirements.txt python -I …`.

| Nr | Schritt | Skript, Aufruf | liest | schreibt | Prüfung |
|---|---|---|---|---|---|
| 0 | Ortskonfiguration für die Seiten | `skripte/31_ort.py` | `config/krakow.yaml` | `daten/ort.js` | `31_ort.py --pruefen`, `pruefen/daten.py` (Vertrag `ort.json`) |
| 1 | Beispieldaten der Gliederung (nur ohne Rohdaten; seit dem Echtlauf nicht mehr im Repo) | `pruefen/fixtures_krakow.py` | `config/krakow.yaml` | `daten/stadtteile_odbl.js`, `zellen_odbl.js`, `kennzahlen_odbl.js` und `.json` | `pruefen/daten.py`; in `pruefen.sh` je Datei mit `fixture: true` über ihren Erzeuger mit `--pruefen` |
| 2 | Seiten in allen Sprachen | `skripte/30_seiten.py` | `vorlagen/`, `texte/<lang>/`, `config/krakow.yaml` | `*.html`, `en/*.html`, `de/*.html` | `30_seiten.py --pruefen`, `pruefen/texte.py`, `pruefen/seiten.mjs` |
| 3 | Datenbank einrichten | `skripte/lauf.sh einrichten` | `sql/`, `.env` | Schema `auswertung`, Rollen | nicht angegeben (Paket Infrastruktur) |
| 4 | Rohdaten laden, je Lauf eine Quelle | `skripte/lauf.sh laden --nur QUELLE` | `config/krakow.yaml` (`quellen`, noch leer) | `public.*` | nicht angegeben |
| 5 | Gliederung (Potsdamer Skripte) | `skripte/01_vorbereiten.py`, `02_auswerten.py`, `03_planungsraeume.py`, `17_planungsraeume_js.py` (Potsdamer Stand, für Kraków ersetzt durch 5a) | nicht angegeben | nicht angegeben | nicht angegeben |
| 5a | Gliederung und Bevölkerung: Grenzen, Zellen, Kennzahlen, Steckbrief (KR3 Variante a, KR13, KR17) | `skripte/02_bevoelkerung.py` | BDOT10k 1261, Eurostat-Gitter 2021, NSP 2021, OSM-PBF aus `eingang/` | `daten/stadtteile_odbl.js`, `zellen_odbl.js`, `kennzahlen_odbl.*`, `steckbrief.js`, `steckbrief_dzielnice_odbl.js`, `belege/D4_bevoelkerung.md` | `pruefen/D4_bevoelkerung.py --ohne-rohdaten` in `pruefen.sh`, voll (rund 90 s) mit `--voll` |
| 5b | Grenzen und Zellen in die Datenbank (KR29) | `skripte/05_db_gliederung.sh ddl`, `laden` (Rolle `admin`) | `sql/003_zellen.sql`, OSM-PBF, Eurostat-Gitter | `public.stadtteil`, `public.zensus_zelle`, `belege/DE_db_gliederung.md` | `05_db_gliederung.sh pruefen` (Datenbank, nicht in `pruefen.sh`) |
| 5c | Übersichtsgrenzen der Startseite (KR39): vereinfacht, Abdeckung topologisch sauber | `skripte/02a_stadtteile_uebersicht.py` | `daten/stadtteile_odbl.js` | `daten/stadtteile_uebersicht_odbl.js`, `belege/N1_stadtteile_uebersicht.md` | `02a_stadtteile_uebersicht.py --pruefen` in `pruefen.sh` |
| 6 | OSM und Fußwegnetz | `skripte/12_osm.sh laden --uebernehmen --pbf …` (KR16, KR25) | OSM-Auszug aus `eingang/` (Kopie nach `osm/<stand>/` mit Prüfsumme) | `auswertung.osm_poi`, `netz_*`, `belege/DE_osm_netz.md` | `12_osm.sh test` (ohne DB, in `pruefen.sh`) |
| 6a | Ziele der Fußweg-Rechnung (KR29) | `skripte/14a_ziele_db_krakow.py` (Rolle `kiezatlas_rechnen`) | `daten/einrichtungen.js`, BDOT10k-Parks, `daten/haltestellen.js` | `auswertung.einrichtung`, `gruenflaeche`, `haltestelle`, `belege/DE_ziele_db.md` | nicht angegeben (Datenbank) |
| 6b | Fußweg je Zelle | `skripte/14b_fussweg.sh rechnen` | Netz, Zellen (`public.zensus_zelle`), Ziele (Kopf von `skripte/14b_fussweg.py`) | Fußweg-Zeilen in `auswertung.zelle_erreichbar` und `zelle_gruen`, `belege/DE_fussweg.md` | `14b_fussweg.sh test` (ohne DB, in `pruefen.sh`); `14b_fussweg.sh pruefen` und `pruefen/D2_wegwerf_db.sh` (nicht in `pruefen.sh`) |
| 6c | Fußweg-Export (KR29) | `skripte/14c_fussweg_export_krakow.py` | Fußweg-Zeilen der Datenbank | `daten/erreichbar_fuss_odbl.js`, `planer_fuss_odbl.js`, `belege/DE_fussweg_export.md` | `--pruefen` braucht die Datenbank; in `pruefen/D6_versorgung.py` übersprungen mit Grund |
| 7 | Versorgung und Takt | `skripte/11_einrichtungen_krakow.py` (mit `--osm-db` für `einrichtungen_odbl.js`), `13_oepnv_krakow.py`, `14_erreichbarkeit_krakow.py`, `15_planer_krakow.py` (KR19, KR28; die Potsdamer Fassungen bleiben für die Gegenprobe) | GTFS der ZTP, BDOT10k 1261, `auswertung.osm_poi`, `daten/zellen_odbl.js`, `config/richtwerte.yaml` | `daten/haltestellen.js`, `einrichtungen.js`, `einrichtungen_odbl.js`, `erreichbar.js`, `planer_odbl.js`, `belege/D6_*.md` | `pruefen/D6_versorgung.py` in `pruefen.sh` (Skripte mit Datenbank übersprungen) |
| 7a | Gebäude und 3D | `skripte/20_bdot10k.py`, `skripte/20_lod.py` (KR18, KR28); `--geometrie` für die 3D-Dateien | BDOT10k 1261, LoD2 aus `eingang/` (LoD1 ausstehend), `daten/stadtteile_odbl.js` | `daten/gebaeude_kennzahlen.js`, `gebaeude_dzielnice_odbl.js`, `belege/D5_gebaeude_lauf.md`; 3D außerhalb des Repos `abgeleitet/gebaeude/<Ordner>/<nr>_odbl.js` und `SHA256SUMS` (die Kette schreibt nach `<heute>-odbl/`; ausgeliefert wird der Stand aus `config/gebaeude_3d.json`, heute `2026-11-13-odbl/`, ohne Manifest dort der jüngste `*-odbl/` mit Manifest) | `pruefen/D5_gebaeude.py --ohne-rohdaten` in `pruefen.sh`, voll mit `--voll`; 3D byte-gleich nachgerechnet mit `20_bdot10k.py --pruefen --geometrie $KIEZ_DATEN/abgeleitet/gebaeude/2026-11-13-odbl` (schreibt nichts, `belege/N2_3d_reproduzierbar.log`; in `pruefen.sh --voll`, wenn der Ordner da ist) |
| 7b | Grundkarte | `skripte/27_grundkarte.py`, Sichtprobe `skripte/27_grundkarte_vorschau.mjs` (KR21, KR32) | BDOT10k 1261 | Kacheln unter `$KIEZ_DATEN/abgeleitet/grundkarte/<SHA-Anfang>/`, `daten/grundkarte.js` | `pruefen/D8_grundkarte.py` und `pruefen/DF_grundkarte.mjs` (Browser) in `pruefen.sh` |
| 7c | Luft | `skripte/32_powietrze.py` (KR20) | EEA-Statistik als GeoJSON-ZIP aus `eingang/eea/` (Handdownload 14.11.2026; das Skript liest auch CSV) | `daten/powietrze.js`, `belege/D7_luft_lauf.md` | `pruefen/D7_powietrze.py` in `pruefen.sh` |
| 7d | Klima | `skripte/35_klimat.py` (KR23) | BDOT10k 1261, `daten/stadtteile_odbl.js`, `daten/kennzahlen_odbl.json` | `daten/klimat.js`, `klimat_zellen.js`, `klimat_stadtteile_odbl.js`, `belege/dk_klimat.md` | `pruefen/dk_klimat.py`, `35_klimat.py --pruefen` in `pruefen.sh` |
| 7e | Wohnungsmarkt | `skripte/40_mieszkania.py` (KR22) | RCN-GeoPackage aus `eingang/rcn/` (Handdownload 14.11.2026) | `daten/mieszkania_odbl.js` (KR43), `belege/DW_mieszkania.md` | `pruefen/DW_mieszkania.py` in `pruefen.sh` |
| 7f | Denkmale | `skripte/dz_denkmale.py` (KR24, KR33) | BDOT10k 1261, Register, gminna ewidencja, Wikidata, OSM aus `eingang/` mit Abruftag in `eingang/HERKUNFT.md`; Ergebnis der Sichtprüfung `belege/DZ_sichtpruefung.json` (Eingabe von Hand, Rückgabe 5, wenn sie nicht zur Stichprobe passt) | `daten/denkmale.js`, `denkmale_bdot.js`, `denkmale_odbl.js`, `belege/DZ_denkmale_lauf.md` | `pruefen/DZ_denkmale.py`, `pruefen/DZ_test_eingang.py` in `pruefen.sh`; `--mit-rohdaten` mit `--voll` |
| 7g | Sanierungsatlas (KR27, KR31) | `skripte/36_sanierung.py` | ZBK-Liste und Regeln der Weiterverwendung aus `zbk/2026-11-13/`, BDOT10k 1261, LoD2 und OSM aus `eingang/` | `daten/sanierung.js`, `sanierung_odbl.js`, `belege/DS_sanierung_lauf.md`; Rohtext nur intern unter `$KIEZ_DATEN/abgeleitet/sanierung/` | `pruefen/DS_sanierung.py` in `pruefen.sh`; `--neu` (rund drei Minuten, byte-gleich) mit `--voll` |
| 7h | Schriften (KR26, KR30): `latin` und `latin-ext` zusammengefügt, Kerning der polnischen Sonderzeichen aus den Grundbuchstaben übertragen | `skripte/schriften.py` (mit `requirements-schriften.txt`) | Fontsource-Pakete unter `$KIEZ_DATEN/schriften/` | `fonts/*.woff2`, `fonts/einbettung.js` | `pruefen/DF_schriften.py`, `skripte/schriften.py --pruefen`, `pruefen/DF_kerning.py` (Lücke geschlossen, Rückgabe 1 sonst) in `pruefen.sh`; im Browser `pruefen/N2_auslieferung.mjs` (Teil 4) |
| 7i | Entwicklungsserver mit Grundkarte und 3D (KR32, KR42) | `node skripte/entwicklung_server.mjs [--port 8080] [--ziel KACHELORDNER] [--gebaeude ORDNER]` | Atlas-Wurzel (nur die Dateien, die auch die Deploy-Kopie ausliefert; Host-Kopf nur 127.0.0.1 oder localhost), Kachelordner, Gebäudeordner nach `config/gebaeude_3d.json` (heute `abgeleitet/gebaeude/2026-11-13-odbl/`, sonst der jüngste `*-odbl/` mit Manifest; nur Dateien aus dessen Manifest, deren SHA256 beim Start passt) | nichts (liefert auf 127.0.0.1 aus) | `pruefen/N2_auslieferung.mjs` im Browserteil von `pruefen.sh` |
| 7j | Vergleich Kraków–Potsdam (KR37) | `skripte/41_porownanie.py` | Eurostat-Gitter DE aus `$KIEZ_DATEN/2026-11-14/41_vergleich/`, `daten/steckbrief.js`, `../kiezatlas-potsdam` (`daten/stadtteile.js`, `kennzahlen.js` per `git show`) | `daten/porownanie.js`, `belege/S1_porownanie.md` | `41_porownanie.py --pruefen` in `pruefen.sh` (übersprungen ohne Eingänge) |
| 8a | Export (KR44) | `skripte/16_export_krakow.py` (Feldbedeutungen in `skripte/export_pola_krakow.py`; `skripte/16_export.py` bleibt Potsdamer Stand für die Gegenprobe) | `daten/*.js` | `daten/pobierz/`, `belege/S4_downloads.md` | `16_export_krakow.py --pruefen`, `pruefen/S4_export.py` in `pruefen.sh` |
| 8b | Langtexte (KR44) | `skripte/16_bloecke_krakow.py` | `texte/<lang>/bloecke/quelle/`, `daten/*.js`, `config/richtwerte.yaml` | `texte/<lang>/bloecke/*.html` | `16_bloecke_krakow.py --pruefen`, `pruefen/S4_bloecke.py` in `pruefen.sh` |
| 9 | Bildschirmfotos aller Seiten für die Belege | `node skripte/bildschirmfotos.mjs --ziel belege/bildschirm-<datum> [--lang pl]` | erzeugte Seiten, Kachelordner (über `skripte/entwicklung_server.mjs`), `seiten` aus `config/krakow.yaml` | `belege/bildschirm-<datum>/*.png`, `README.md` | nicht angegeben (Konsolenfehler je Seite in der Übersicht) |
| 9a | Drei kurze Filme auf Polnisch (ohne Ton, Untertitel eingeblendet, WebVTT pl/en/de) | `node skripte/filme.mjs --ziel belege/filme [--nur 1,2,3] [--standbilder ORDNER]` | erzeugte Seiten über `skripte/entwicklung_server.mjs` mit Kachelordner, ffmpeg (libx264, libvpx-vp9) | `belege/filme/*.mp4`, `*.webm`, `*.vtt`, `README.md` (Drehbuch, Dauer, Größe, SHA256) | im Skript: Dauer 50 bis 75 s, je Datei höchstens 5 MB, 1280 × 720 ohne Ton, keine Konsolenfehler; Standbilder je Untertitel von Hand angesehen |

Reihenfolge beim Neurechnen: Datenpakete, dann 7j, 8a, 8b und zuletzt Schritt 2 (`skripte/30_seiten.py`), sonst
werden Downloads und Langtexte still alt.

Die Skripte 20 bis 26 (Gebäude aus ALKIS, Bauzeiten-Kaskade) sind Potsdamer Stand; die Kaskade entfällt für Kraków
(KR4). Ein Gebäudeleser für BDOT10k ersetzt `20_alkis_nas.py` im Paket Gebäude und Kamienice.

## Datenstand je Thema (nach den Seitenpaketen, der Nacharbeit, der Behebung und den Handdownloads, 14.11.2026)

„echt“ heißt: aus der genannten Quelle gerechnet, ohne `fixture`. „Beispiel“ heißt: `fixture: true`, erfundene oder
aus Beispieldaten gerechnete Werte. Abgelesen am Feld `fixture` jeder Datei nach dem Merge; Zahlen und Zählungen
stehen in den Belegen der Pakete. Welche Seite welche Datei lädt, steht in der Kopfzeile ihrer Vorlage
(`vorlagen/<seite>.html`, Zeile `daten:` und die Nachladeliste des Seitenmoduls); die Prüfstände stehen in
`belege/README.md`.

| Thema | Datei | Stand | Grund, wenn Beispiel, und Grenzen |
|---|---|---|---|
| Gliederung | `stadtteile_odbl.js`, `zellen_odbl.js`, `kennzahlen_odbl.*` | echt | |
| Gliederung, Übersicht | `stadtteile_uebersicht_odbl.js` | echt | aus `stadtteile_odbl.js` vereinfacht (10 m, Abdeckung gültig), nur für die Startseite (KR39) |
| Bevölkerung | `steckbrief.js` (Stadt, delegatury) | echt | Werte je dzielnica nur in den `_odbl`-Dateien; NSP je dzielnica `null`, solange die rejony fehlen |
| Bevölkerung | `steckbrief_dzielnice_odbl.js` | echt | NSP je dzielnica `null` (rejony fehlen) |
| Fußweg | Datenbank-Zeilen (`auswertung.netz_*`, `zelle_erreichbar`, `zelle_gruen`) | echt | |
| Gebäude | `gebaeude_kennzahlen.js`, `gebaeude_dzielnice_odbl.js` | echt | Höhen aus LoD2 (Stand 2017), LoD1 fehlt |
| Gebäude, 3D | `gebaeude/<nr>_odbl.js` | echt, außerhalb des Repos | die Kartenseiten laden sie auf Wunsch (KR42); Entwicklungsserver und `skripte/deploy_kopie.py` liefern sie unter `daten/gebaeude/` aus, beide prüfen jede Datei gegen das Manifest; Stand und Prüfsumme des Manifests in `config/gebaeude_3d.json` |
| Versorgung | `haltestellen.js`, `einrichtungen.js`, `einrichtungen_odbl.js`, `erreichbar.js`, `erreichbar_fuss_odbl.js`, `planer_odbl.js`, `planer_fuss_odbl.js` | echt | `st` nur in den `_odbl`-Dateien; RSPO (Schulen) fehlt |
| Luft | `powietrze.js` | echt | EEA-Statistik, Handdownload 14.11.2026 mit Filter `City = Kraków`: 10 Stationen in der Stadt, 0 im Umland (der Export enthält das Umland nicht; Seite und Methode sagen das), 337 Jahreswerte 2010–2025; `potentialOutlier` fehlt im Export, die Regel greift nicht (`pruefen/D7_protokoll.md`, Abweichung 2); Abzeichen „orientacyjnie“ |
| Grundkarte | `grundkarte.js` (Kacheln außerhalb des Repos) | echt | |
| Wohnungsmarkt | `mieszkania_odbl.js` | echt | RCN Powiat 1261, Handdownload (laut Geoportal zuletzt aktualisiert am 21.09.2026, die Datei enthält trotzdem Dokumente bis 29.09.2026, Unterschied ungeklärt); nach F10 45.701 Käufe, nur Jahre ab 2019 (F11, KR55) 45.687, 371 Mediane je dzielnica, Jahr und Markt (dazu 24 der Stadt), Fallzahl unter 10 nur als „n < 10“, 27 sekundär verdeckte Fallzahlen (KR43; `pruefen/N1_protokoll.md`, Regel 4, Nachträge 2 bis 5; KR56), Spannenprobe 0 von 32 unterdrückten Fallzahlen mit höchstens zwei Werten (`belege/DW_spannenprobe.md`); Stadtwerte erst ab 2021 weitgehend vollständig (2019 rund 2 %, 2020 rund 26 % der Käufe mit Lage), je dzielnica erst ab 2021 (Lage fehlt 2016–2020); `belege/DW_mieszkania.md` |
| Klima | `klimat.js`, `klimat_zellen.js`, `klimat_stadtteile_odbl.js` | echt | |
| Denkmale | `denkmale_bdot.js`, `denkmale_odbl.js` | echt | OSM mit Relationen (Multipolygonen); Lage der OSM-Objekte mit `heritage` in einer Zufallsstichprobe am Luftbild geprüft (15.11.2026, 16 von 20 auf dem Objekt, 3 knapp daneben, 1 nicht dort; `sichtpruefung.geprueft: true`, Nachtrag 4), Zuordnung zum Gebäude ungeprüft; Kennzahl ist die OSM-Kennzeichnung, keine Zahl der kamienice (dafür fehlt das NID-Register) |
| Denkmale | `denkmale.js` | echt (nur Wikidata) | Wikidata-Handabruf 14.11.2026 (1.909 Objekte aus 2.078 Zeilen der Abfrage; Objekte mit gleicher Registernummer sind ein Punkt, 1.214 Punkte in der Stadt; der Zähler `zaehlung.wd.zeilen` zählt Objekte); NID-Register und gminna ewidencja fehlen im Eingang; Lage aus den Wikidata-Koordinaten in einer Zufallsstichprobe am Luftbild geprüft (15.11.2026, 17 von 20 auf dem Objekt, 3 knapp daneben; `sichtpruefung.geprueft: true`; Stichprobe `belege/DZ_sichtpruefung_stichprobe.json`, Ergebnis `belege/DZ_sichtpruefung.json`, `pruefen/DZ_protokoll.md` Nachträge 3 und 4); gezeigt auf `kamienice` (je Delegatura) und `karta` (Ebene `rejestr`, CC0, getrennt von `zabytki`, ODbL); `belege/DZ_denkmale_lauf.md` |
| Sanierungsatlas | `sanierung.js`, `sanierung_odbl.js` | echt | Liste vom 01.12.2025 (ohne Verwalter und Registernummer); private Einträge nur gezählt, Punkte nur öffentliches Eigentum ab 3 Geschossen (KR31); Typologie ist eine Schätzung nach Geometrie, angebaute Kandidaten gesondert ausgewiesen; Sichtprüfung der Stichprobe nur als Zählung (`belege/DS_sichtpruefung.json`) |
| Schriften | `fonts/*.woff2` | echt | Kerning der polnischen Sonderzeichen aus den Grundbuchstaben übertragen (KR30); typografische Sichtprüfung offen |
| Vergleich | `porownanie.js` | echt | Stichtage beider Gitter an der Quelle nicht geprüft (KR37) |
| Downloads | `daten/pobierz/` | echt | nur aus den echten Datendateien; Denkmalregister als Ebene `rejestr_zabytkow` (Wikidata, CC0, im GeoPackage ohne OSM-Anteil); Luft und Wohnungsmarkt haben noch keine eigene Ebene (Liesmich, Abschnitt „Nicht im Export“; KR44) |

## Neuer Datenstand

Wenn eine Quelle einen neuen Stand veröffentlicht:

1. Neue Fassung unter `$KIEZ_DATEN/<quelle>/<stand>/` ablegen (Stand = Datum der Veröffentlichung oder des Abrufs,
   `JJJJ-MM-TT`), mit eigener `HERKUNFT.md`. Die alte Fassung bleibt liegen.
2. Prüfsummen beim Abruf in eine **neue** Liste `belege/rohdaten-<quelle>-<stand>.sha256` schreiben. Alte Listen
   bleiben unverändert stehen, auch wenn ihre Dateien nicht mehr gelesen werden; `pruefen.sh` prüft jede Liste gegen
   `$KIEZ_DATEN`.
3. Bezugs-Snapshots (etwa der Gebäudestand, auf den sich Zuordnungen beziehen) als Datei außerhalb der Datenbank
   sichern, gehasht wie Rohdaten.
4. Pfade und Stände im Code auf den neuen Ordner umstellen, als Vertragsänderung über die Integration. Der Schlüssel
   `quellen` in `config/krakow.yaml` ist noch leer; Pfade und Stände stehen heute fest in Skripten, Prüfungen und
   `config/richtwerte.yaml` (Liste unten, gesucht am 14.11.2026 mit `grep -rn '2026-11-1[34]' skripte/ pruefen/
   pruefen.sh config/`; Kommentare, Kopftexte und Testordner nicht aufgeführt). Vor dem Umstellen dieselbe Suche
   wiederholen. Sie zentral in `config/krakow.yaml` zu führen, ist offen.
5. Betroffene Schritte neu rechnen, `./pruefen.sh` grün, Prüfstand unter `belege/pruefstand-<datum>-<commit>/`,
   Eintrag in `CHANGELOG.md` mit der geänderten Quelle und den Zahlen, die sich bewegt haben.

Wo der Stand jeder Quelle festgeschrieben ist, mindestens (Schritt 4; Pfade relativ zu `$KIEZ_DATEN`):

| Quelle | heutiger Ort | festgeschrieben in |
|---|---|---|
| BDOT10k 1261 | `2026-11-13/03_gebaeude/1261_SHP.zip` | `skripte/kette.py` (`BDOT`), `02_bevoelkerung.py` (`STAND`), `raum_bevoelkerung.py` (`STAND_ROH`), `20_bdot10k.py` (Standard von `--bdot`), `13_oepnv_krakow.py` (`BDOT`), `35_klimat.py` (`BDOT_STD`), `dz_denkmale.py` (`BDOT_REL`, auch für `36_sanierung.py`), `27_grundkarte.py` (Suchpfad und `BDOT_SHA256`), `schnappschuss.py` (Liste), `config/richtwerte.yaml` (`einrichtungen.bdot10k.zip`), `pruefen.sh` (`BDOT`), `pruefen/D5_gebaeude.py`; Abrufdatum im Vermerk von `dz_denkmale.py` („pobrano“) |
| Eurostat-Gitter Polen, NSP 2021 je rejon | `2026-11-13/02_zensus/…` | `kette.py` (`GITTER_PL`, `NSP`), `02_bevoelkerung.py` (`STAND`), `raum_bevoelkerung.py` (`STAND_ROH`), `schnappschuss.py` |
| GTFS der ZTP | `2026-11-13/06_oepnv/GTFS_KRK_{A,T,M}.zip` | `kette.py` (`GTFS`), `config/richtwerte.yaml` (`oepnv.gtfs`, `gegenprobe_tag`; `stand`), `schnappschuss.py` |
| ZBK-Liste und Regeln der Weiterverwendung | `zbk/2026-11-13/…` | `kette.py` (`ZBK`, `ZBK_REGELN`), `36_sanierung.py` (`ZBK_REL`, `ZBK_REGELN_REL`, `ABRUF` und die Erstellungs- und Abrufzeit im Vermerk; Abrufdatum auch im LoD2-Vermerk), `pruefen/DS_sanierung.py` |
| BIP-Seite Einwohner je dzielnica (nur Gegenprobe) | `2026-11-13/10_statistik/bip_dok242410_….html` | `kette.py` (`BIP_FLAECHE`), `35_klimat.py` (`BIP`) |
| Eurostat-Gitter Deutschland (Vergleich) | `2026-11-14/41_vergleich/DE_PD_3035_GPKG.zip` | `kette.py` (`GITTER_DE`), `41_porownanie.py` (`STAND`), `schnappschuss.py`, `pruefen.sh` |
| Schriften (Fontsource) | `schriften/2026-11-13/…` | `kette.py` (`SCHRIFT_PAKETE`, `SCHRIFT_ANGABEN`), `schriften.py` (`STAND`) |
| 3D-Dateien (Ausgabe) | `abgeleitet/gebaeude/2026-11-13-odbl/` | `entwicklung_server.mjs` (`GEBAEUDE_STAND`), `deploy_kopie.py` (`GEB_STAND`, `GEB_MANIFEST_SHA256`), `pruefen.sh` (`GEB3D`), `pruefen/S2_seiten.mjs` (`GEB`) |

Der Kachelordner der Grundkarte heißt nach dem Anfang der SHA256 der BDOT10k und folgt `BDOT_SHA256` von selbst.
Handdownloads unter `eingang/` (OSM, LoD2, EEA, RCN) tragen ihren Stand in `eingang/HERKUNFT.md`. Die Abrufbefehle in
`docs/uruchomienie.md` (Weg A) schreiben in einen Ordner `$STAND`, der vor dem Abruf auf das heutige Datum zu setzen
ist.

**Wohnungsmarkt (RCN), bei neuer Datei prüfen:** Einige Jahresangaben sind an der GUGiK-Datei vom 14.11.2026
gesehen und stehen fest im Text, nicht aus den Daten:

- `texte/<lang>/mieszkania.js`, `mieszkania.g.zeitreihe` („erst ab 2021 weitgehend vollständig“, „2019 und 2020“,
  „2019 ein sehr kleiner Teil“) und `mieszkania.g.lage` („2016 bis 2020“, „ab 2021, für 2020 nur zum Teil“). Mit der
  neuen Datei gegen den Abschnitt „Grenzen“ in `belege/DW_mieszkania.md` abgleichen.
- `skripte/40_mieszkania.py`, `beleg_text`: die Angabe des Geoportals „Data ostatniej aktualizacji 2026-09-21“ und
  das Datum des Handdownloads (aus `eingang/HERKUNFT.md` übernehmen).
- `skripte/40_mieszkania.py`, `ERSTES_JAHR = 2019` (KR55): bleibt, solange die Spannenprobe im Beleg 0 ergibt; ist
  sie größer, nicht weiter umbauen, sondern melden (`pruefen/DW_protokoll.md`, Änderung KR55).

Aus den Zählungen jedes Laufs abgeleitet sind dagegen die Jahre im Abschnitt „Grenzen“ des Belegs (vollständig ab,
Jahre ohne Geometrie, Anteil am Recht fehlt bis) und auf der Seite das erste Jahr (`mieszkania.g.od_roku` aus
`regeln.erstes_jahr`).

## Datenbank und mehrere Arbeitskopien

Hinweise für die Arbeit mit Worktrees, aus `.env.beispiel` und dem Kopf von `docker-compose.yml` hierher verschoben
(dort steht nur noch, was eine Betreiberin mit einem einzigen Klon braucht):

- Die `.env` liegt im Haupt-Checkout (`../kiezatlas-krakow/.env`). Worktrees lesen sie über `skripte/lauf.sh` und
  `skripte/kette.py` aus dem Haupt-Checkout (`KIEZ_ENV`), docker compose über `--env-file` (`belege/D1_infrastruktur.md`).
- `docker compose up -d --wait db` nur im Haupt-Checkout starten: `./sql` wird beim ersten Start eines leeren Volumes
  eingespielt und als Pfad eingebunden; aus einem Worktree hinge der Container an dessen Ordner.
- Der Kiezatlas Potsdam nutzt Port 55461, Kraków 55462; eigener Projektname und eigenes Volume, damit beide
  nebeneinander laufen.

## Prüfungen

`./pruefen.sh` läuft ohne Netz und ohne Datenbank (PG-Variablen werden entfernt) und zählt am Ende grün, Befund und
übersprungen; Übersprungenes steht mit Grund in der Zählung. Darin:

- Syntax (JavaScript, Shell, Python), `pruefen/geruest.py` (Rechen-SRID in DDL und Skripten, keine internen
  Plankennungen in ausgelieferten Dateien), `skripte/31_ort.py --pruefen`, `skripte/30_seiten.py --pruefen`,
  `pruefen/texte.py`, `pruefen/daten.py`, `skripte/12_osm.sh test`, `skripte/14b_fussweg.sh test`;
- `pruefen/hreflang.py`: hreflang, canonical, `og:locale` und Sprachschalter aller erzeugten Seiten ohne Browser,
  damit die Sprachverweise auch mit `--ohne-browser` geprüft sind;
- `pruefen/belege.py`: Belegschicht in sich stimmig (jede Datei unter `belege/` beschrieben und umgekehrt, angegebene
  Zahlen gegen die Dateien, Prüfstand im README-Kasten grün, Übersicht der Entscheidungen gegen ihre Abschnitte,
  Meldeweg überall gleich, Belegspalte der Checkliste). Lieferungen der Pakete, die noch nicht übernommen sind,
  meldet sie als Hinweis; mit `--veroeffentlichung` sind sie ein Befund;
- `pruefen/seiten.mjs`: alle 18 Seiten in pl, en, de per file:// und HTTP (Konsole, Platzhalter, deutsche Reste,
  hreflang, Hinweis Beispieldaten, axe, 360 px), Sprachschalter mit Hash, Sprachhinweis, i18n-Formate;
- `pruefen/DF_grundkarte.mjs` (Browser): Grundkarte auf den Kartenseiten, polnische Sonderzeichen ohne Ersatzschrift,
  Startgewicht des Planers; `pruefen/DF_schriften.py`, `skripte/schriften.py --pruefen`;
- die Prüfungen der Datenpakete (Spalte „Prüfung“ in den Schritten): Abrufwerkzeug (pytest), Gliederung, Gebäude,
  Versorgung, Luft, Grundkarte, Klima, Wohnungsmarkt, Denkmale, Sanierungsatlas, je in der schnellen Fassung; mit
  `./pruefen.sh --voll` zusätzlich die Neurechnung aus den Rohdaten (Gliederung, Gebäude, Denkmale, Sanierungsatlas,
  dazu die 3D-Dateien außerhalb des Repos, wenn ihr Ordner da ist);
- die Prüfungen der Nacharbeit vom 14.11.2026: `pruefen/N1_daten.py` (keine Sätze in Datenpaketen, Ortsmarke, `radius_m`,
  JavaScript-Startgewicht der Startseite, ohne CSS, HTML, Schriften und Kacheln; Gesamtgewicht mit HTML und CSS zur Information), `skripte/02a_stadtteile_uebersicht.py --pruefen`, `skripte/oeffentlich_pruefen.py`
  (Prüfung vor Veröffentlichung: bekannte Stellen anderer Eigentümer als Hinweis, mit `--veroeffentlichung` als
  Befund); im Browser `pruefen/N2_auslieferung.mjs` (3D über den Entwicklungsserver, Kopfleiste aller Seiten bis 360 px,
  Kerning; Deploy-Teil nur mit `--deploy`);
- die Prüfungen der Seitenpakete: ohne Browser der Vergleich (`skripte/41_porownanie.py --pruefen`), die Zählungen der
  Kartenseiten (`pruefen/S2_zaehlungen.py --pruefen`), Downloads und Langtexte (`skripte/16_export_krakow.py
  --pruefen`, `pruefen/S4_export.py`, `skripte/16_bloecke_krakow.py --pruefen`, `pruefen/S4_bloecke.py`); im Browser
  `pruefen/S1_seiten.mjs` (Start, Karte, Steckbrief, Vergleich), `pruefen/S2_seiten.mjs` (Erreichbarkeit, Kamienice,
  Wohnungsbestand, 3D; 3D übersprungen ohne den Ordner der Gebäudedateien) und `pruefen/S3_themenseiten.mjs`.

Die Wortprüfung auf deutsche Reste in den JavaScript-Modulen und die Falschsatz-Listen je Sprache gehören zum Paket
Oberflächen-Texte (`pruefen/texte.py` prüft bisher `texte/` und den sichtbaren Text der erzeugten Seiten).

Nicht in `pruefen.sh`: die Teile der Paketprüfungen, die die Datenbank brauchen (`11_einrichtungen_krakow.py
--pruefen`, `14c_fussweg_export_krakow.py --pruefen`, `05_db_gliederung.sh pruefen`, `14b_fussweg.sh pruefen`,
`pruefen/D1_rechte.py` über `skripte/lauf.sh rechte`), die Messung `pruefen/DF_kerning.py` (Rückgabe immer 0; Stand
14.11.2026: „Grundpaar mit Wert, polnisches Paar ohne: 0“ in allen fünf Schriften), der Deploy-Teil von
`pruefen/N2_auslieferung.mjs` (`--deploy <Deploy-Kopie>`), `pruefen/N2_touch.mjs`, die Probe
`pruefen/D2_wegwerf_db.sh` (braucht Docker), die Gegenprobe Potsdam (`./pruefen.sh --gegenprobe` oder `pruefen/gegenprobe_potsdam.sh`,
siehe „Bau“) und alle Abnahmen mit Datenbank (kommen mit den Datenpaketen).

## Bau

Gilt für den parallelen Bau in Paketen. Jede Datei hat genau einen Eigentümer; nur er ändert sie. Verträge sind mit
dem Gerüst eingefroren und ändern sich nur als Vertragsänderung über die Integration (Projektleitung), nie in einem
Paket. DDL schreibt nur die Integration; Pakete schreiben nur Zeilen in ihre eigenen `auswertung.*`-Tabellen und
laden mit `--nur <quelle>`. Gemeinsame Dokumente (README, `docs/*.md`, QUELLEN, CITATION, CHANGELOG,
`belege/README.md`, `pruefen.sh`) schreibt nur die Belegschicht; Pakete liefern `quellen-<paket>.md`,
`belege/<paket>_*.md`, `pruefen/<paket>_protokoll.md` und `docs/entscheidungen/<paket>.md`. Je Paket ein Worktree
`../kiezatlas-krakow-wt-<PAKET>`; Merge nach `main` erst bei grünem `pruefen.sh`.

### Einsammeln durch die Belegschicht

Pakete schreiben keine gemeinsamen Dokumente. Sie legen ab, die Belegschicht übernimmt:

| Lieferung des Pakets | übernommen nach |
|---|---|
| `quellen-<paket>.md` (Wurzelordner) | Zeilen in `QUELLEN.md`, Lizenzzeile in `daten/LIZENZ.md` |
| `belege/<paket>_*.md`, `belege/rohdaten*.sha256` | Zeile in `belege/README.md` (belegt, erzeugt von) |
| `pruefen/<paket>_protokoll.md` | Zeile in `belege/README.md` mit dem Commit, der das Protokoll vor dem Lauf festlegt |
| `docs/entscheidungen/<paket>.md` | neuer Eintrag `KR<n>` in `docs/entscheidungen.md`, Vorschlag bleibt als Herkunft stehen |
| neue Prüfung | Schritt in `pruefen.sh`, Zeile in `docs/rundgang.md` |
| erste Kernzahl | Zeile im README-Kasten, Status in `docs/checkliste.md` |

`pruefen/belege.py` listet Lieferungen, die noch nicht übernommen sind, als Hinweis. So bleibt `pruefen.sh` beim
Merge eines Pakets grün, und die Liste zeigt, was als Nächstes einzusammeln ist.

### Eigentümer je Datei

| Datei oder Ordner | Eigentümer | Vertrag |
|---|---|---|
| `i18n.js`, `daten/schema/texte.md` | Gerüst, danach Integration | ja |
| `daten/ort.js`, `skripte/31_ort.py`, `daten/schema/ort.json` | Gerüst, danach Integration | ja |
| `config/krakow.yaml` | Integration; Abschnitt `karte` Paket Grundkarte und Luftbild; `quellen` je Paket über die Integration | ja |
| `themen.js`, `kopf.js`, `rahmen.js`, `rahmen.css` | Gerüst, danach Integration | ja |
| `vorlagen/_rahmen.html`, `skripte/30_seiten.py`, `skripte/textschicht.py`, `skripte/ort_konfig.py` | Gerüst, danach Integration | ja |
| `daten/schema/*.json` | Gerüst, danach Integration | ja |
| `sql/*` | Gerüst, danach Integration (DDL nur hier) | ja |
| `texte/<lang>/seiten.js` | Gerüst, danach Integration (neue Seiten nur über die Integration) | ja |
| `pruefen/geruest.py`, `texte.py`, `seiten.mjs`, `daten.py`, `fixtures_krakow.py`, `gegenprobe_potsdam.sh`, `gegenprobe_text.mjs` | Gerüst, danach Belegschicht | |
| `pruefen/hreflang.py`, `pruefen/belege.py`, `docs/checkliste.md`, `skripte/bildschirmfotos.mjs`, `skripte/filme.mjs`, `belege/bildschirm-*/`, `belege/filme/`, `belege/pruefstand-*/`, `belege/gegenprobe_*` | Belegschicht | |
| `texte/<lang>/kern.js`, `texte/<lang>/karte.js`, `docs/glossar-pl.md` | Paket Oberflächen-Texte (Gerüst hat `kern.js` angelegt) | |
| `docker-compose.yml`, `.env.beispiel`, `skripte/abruf.py`, `skripte/lauf.sh`, `requirements*` | Paket Infrastruktur | |
| `skripte/12_*`, `skripte/14b_*`, `skripte/osm_pbf.py`; `auswertung.osm_poi`, `auswertung.netz_*` | Paket OSM und Fußwegnetz | |
| `pruefen/D2_*` (`D2_fussweg_pruefen.py`, `D2_test_fussweg.py`, `D2_beispielwelt.py`, `D2_wegwerf_db.sh`, `D2_protokoll.md`), `pruefen/a3_test_osm.py`, `belege/D2_*.md`, `quellen-D2.md` | Paket OSM und Fußwegnetz (Vorschlag, Master bestätigt, KR16) | |
| `README.md`, `docs/*.md`, `QUELLEN.md`, `CITATION.cff`, `CHANGELOG.md`, `belege/README.md`, `daten/LIZENZ.md`, `NOTICE`, `pruefen.sh` | Belegschicht (Gerüst hat sie leer angelegt) | |
| `skripte/deploy_kopie.py`, `skripte/28_*`, `vorlagen/404.html`, `docs/auslieferung.md` | Paket Deploy | |
| `skripte/01_*`, `02_*`, `03_*`, `17_*`; `daten/stadtteile_odbl.js`, `zellen_odbl.js`, `kennzahlen_odbl.*`, `planungsraeume.js` | Paket Gliederung und Bevölkerung (seit dem Echtlauf echte Daten, KR28) | Verträge `zellen_odbl.json`, `kennzahlen_odbl.json` bei der Integration |
| `sql/003_zellen.sql`, `skripte/05_db_gliederung.py`, `05_db_gliederung.sh`, `belege/DE_*.md`, `belege/rohdaten-DE-*.sha256`, `quellen-DE.md`, `docs/entscheidungen/DE.md`; `package.json`, `package-lock.json` | Integration (Vorschlag aus dem Echtlauf und dem Paket Deploy, KR29, KR35) | `public.stadtteil`, `public.zensus_zelle` schreibt die Integration als `admin` (Ausnahme, nicht bestätigt) |
| `skripte/raum_bevoelkerung.py`, `daten/steckbrief.js`, `daten/steckbrief_dzielnice_odbl.js`, `pruefen/D4_*`, `belege/D4_*.md`, `belege/rohdaten-D4-*.sha256`, `quellen-D4.md`, `docs/entscheidungen/D4/` | Paket Gliederung und Bevölkerung (Vorschlag, Master bestätigt, KR17) | Verträge `steckbrief*.json` bei der Integration |
| `skripte/20_*` bis `26_*`, `daten/gebaeude/` | Paket Gebäude und Kamienice (ohne Kaskade, KR4) | |
| `daten/gebaeude_kennzahlen.js`, `daten/gebaeude_dzielnice_odbl.js`, `pruefen/D5_*`, `belege/D5_*.md`, `belege/rohdaten-D5-*.sha256`, `quellen-D5.md`, `docs/entscheidungen/D5/` | Paket Gebäude und 3D (Vorschlag, Master bestätigt, KR18) | Verträge `gebaeude_kennzahlen.json`, `gebaeude_dzielnice_odbl.json` bei der Integration |
| `skripte/11_*`, `13_*`, `14_*`, `15_*`, `config/richtwerte.yaml`, `daten/planer*`, `erreichbar*`, `einrichtungen*` | Paket Versorgung und Takt | |
| `skripte/versorgung_werkzeug.py`, `daten/haltestellen.js`, `pruefen/D6_*`, `belege/D6_*.md`, `belege/rohdaten-D6-*.sha256`, `quellen-D6.md` | Paket Versorgung und Takt (bestätigt, KR19) | Vertrag `haltestellen.json` bei der Integration |
| `skripte/14a_ziele_db_krakow.py`, `skripte/14c_fussweg_export_krakow.py`; `auswertung.einrichtung`, `gruenflaeche`, `haltestelle`; `daten/planer_odbl.js`, `planer_fuss_odbl.js`, `erreichbar_fuss_odbl.js` | Paket Versorgung und Takt (Vorschlag aus dem Echtlauf, KR29) | Vertrag `planer_odbl.json` bei der Integration |
| `skripte/27_*`, `daten/grundkarte.js` | Paket Grundkarte und Luftbild | |
| `pruefen/D8_*`, `belege/D8_grundkarte.md`, `belege/D8_vorschau/`, `quellen-D8.md`; Kachelordner `$KIEZ_DATEN/abgeleitet/grundkarte/` (außerhalb des Repos) | Paket Grundkarte und Luftbild (bestätigt, KR21) | |
| `fonts/*.woff2`, `fonts/einbettung.js`, `skripte/schriften.py`, `skripte/entwicklung_server.mjs`, `kartenfeld.js`, `kartenfeld.css`, `pruefen/DF_*`, `belege/DF_*`, `belege/rohdaten-DF-*.sha256`, `quellen-DF.md`, `docs/entscheidungen/DF.md`, `requirements-schriften.*` | Paket Schrift und Grundkarte (Vorschlag, KR30, KR32); `kartenfeld.*` danach Seitenpakete, `requirements-schriften.*` Paket Infrastruktur, Prüfungen Belegschicht | |
| `skripte/36_*`, `daten/sanierung.js`, `daten/sanierung_odbl.js`, `pruefen/DS_*`, `belege/DS_*.md` (erzeugt), `belege/rohdaten-DS-*.sha256`, `quellen-DS.md`, `docs/entscheidungen/DS.md` | Paket Sanierungsatlas Wohnungsbestand (Vorschlag, KR31) | Verträge `sanierung.json`, `sanierung_odbl.json` bei der Integration |
| `skripte/32_*`, `daten/powietrze.js`, `pruefen/D7_*`, `belege/D7_*.md`, `belege/rohdaten_D7.sha256`, `quellen-D7.md` (Texte seit 14.11.2026 unter `texte/`, Seitenpaket) | Paket Luft (Vorschlag, Master bestätigt, KR20) | Vertrag `powietrze.json` bei der Integration |
| `skripte/35_*`, `daten/klimat.js`, `klimat_zellen.js`, `klimat_stadtteile_odbl.js`, `pruefen/dk_*`, `belege/dk_*.md`, `quellen-dk.md`, `docs/entscheidungen/dk.md` (Texte seit 14.11.2026 unter `texte/`, Seitenpaket) | Paket Klima (Vorschlag, Master bestätigt, KR23) | Verträge `klimat*.json` bei der Integration |
| `skripte/40_*`, `daten/mieszkania_odbl.js`, `pruefen/DW_*`, `belege/DW_*.md`, `belege/rohdaten_DW.sha256`, `quellen-DW.md` (Texte unter `texte/`, KR43) | Paket Wohnungsmarkt (Vorschlag, Master bestätigt, KR22) | Vertrag `mieszkania.json` bei der Integration |
| `skripte/dz_*`, `daten/denkmale.js`, `denkmale_bdot.js`, `denkmale_odbl.js`, `pruefen/DZ_*`, `belege/DZ_*.md`, `belege/DZ_sichtpruefung_stichprobe.json`, `belege/DZ_sichtpruefung.json` (Eingabe von Hand), `belege/rohdaten-dz-*.sha256`, `quellen-DZ.md` (Texte `denkmale.*` seit 14.11.2026 unter `texte/`, Seitenpaket) | Paket Denkmale und Kamienice (Vorschlag, Master bestätigt, KR24) | Verträge `denkmale*.json` bei der Integration |
| `vorlagen/index.html`, `karta.html`, `dzielnica.html`, `porownanie.html`, `erzaehlung.js`, `karta.js`, `dzielnica.js`, `vergleich.js`, `stadtatlas.css`, `kartenfeld.js`, `kartenfeld.css`, `texte/<lang>/erzaehlung.js`, `skripte/41_porownanie.py`, `daten/porownanie.js`, `pruefen/S1_seiten.mjs`, `belege/S1_*.md`, `belege/rohdaten-S1-*.sha256`, `quellen-S1.md`, `docs/entscheidungen/S1.md`, `$KIEZ_DATEN/2026-11-14/41_vergleich/` | Paket Seiten Erzählung, Karte, Steckbrief, Vergleich (Vorschlag, KR36, KR37) | Vertrag `porownanie.json` bei der Integration |
| `atlas.js`, `karte.js`, `schaugrafik.js`, `atlas.css`, `karte.css`, `planer.js`, `planer.css`, `jahre.js`, `jahre.css`, `skripte/16_export.py` | Potsdamer Stand, unverändert für die Gegenprobe (KR36); Änderungen nur über die Integration | |
| `vorlagen/kamienice.html`, `planer.html`, `modernizacja.html`, `kartenseite.js`, `kartenseite.css`, `erreichbarkeit.js`, `kamienice.js`, `sanierungsatlas.js`, `texte/<lang>/kamienice.js`, `sanierung.js`, `denkmale.js`, in `texte/<lang>/planer.js` die Schlüssel `planer.e.*` und `planer.ks_*`, `pruefen/S2_*`, `belege/S2_*`, `docs/entscheidungen/S2.md` | Paket Seiten Planer, Denkmale und Sanierungsatlas (Vorschlag, KR36, KR41) | |
| `vorlagen/klimat.html`, `powietrze.html`, `mieszkania.html`, `themenseite.js`, `themenseite.css`, `seite_klimat.js`, `seite_powietrze.js`, `seite_mieszkania.js`, `texte/<lang>/klimat.js`, `powietrze.js`, `mieszkania.js`, `pruefen/S3_themenseiten.mjs`, `belege/S3_*`, `docs/entscheidungen/S3.md` | Paket Themenseiten Luft, Wohnungsmarkt, Klima (Vorschlag, KR36, KR43) | |
| `vorlagen/punktualnosc.html` und ihre Texte | Paket Pünktlichkeit (noch nicht vergeben) | |
| `vorlagen/kamienice-*.html`, `planer-*.html`, `metoda.html`, `dane.html`, in `texte/<lang>/bloecke/` die Blöcke `metoda`, `dane`, `kamienice_metoda`, `kamienice_dane`, `planer_metoda`, `planer_dane` und `quelle/`, `skripte/16_export_krakow.py`, `export_pola_krakow.py`, `16_bloecke_krakow.py`, `daten/pobierz/`, `pruefen/S4_*`, `belege/S4_*`, `docs/entscheidungen/S4*` | Paket Methode, Daten, Downloads (Vorschlag, KR44); die übrigen Blöcke bei den Seitenpaketen | |
| `pruefen/N2_*`, `belege/N2_*`, `docs/entscheidungen/N2.md` | Paket Oberfläche und Auslieferung (Vorschlag) | |
| `skripte/ortsmarke.py` | Paket Denkmale und Kamienice (Vorschlag aus der Daten-Nacharbeit) | |
| `skripte/02a_stadtteile_uebersicht.py`, `daten/stadtteile_uebersicht_odbl.js`, `belege/N1_stadtteile_uebersicht.md` | Paket Gliederung und Bevölkerung (Vorschlag aus der Daten-Nacharbeit) | Vertrag `stadtteile_uebersicht_odbl.json` bei der Integration |
| `pruefen/N1_*`, `belege/N1_*`, `docs/entscheidungen/N1.md` | Belegschicht (Vorschlag aus der Daten-Nacharbeit) | |
| `atlas.sh`, `skripte/atlas.sh`, `skripte/kette.py`, `skripte/schnappschuss.py` | Paket Offene Wissenschaft, danach Integration (Vorschlag) | |
| `config/gebaeude_3d.json` | Paket Gebäude und 3D, gepflegt mit jedem neuen Lauf von `skripte/20_bdot10k.py --geometrie` (Vorschlag aus der Behebung Daten) | gelesen von `skripte/entwicklung_server.mjs`, `skripte/deploy_kopie.py`, `pruefen.sh` |
| `belege/DS_sichtpruefung.json` | Paket Sanierungsatlas Wohnungsbestand, von Hand (Eingabe der Sichtprüfung) | gelesen von `skripte/36_sanierung.py` |
| `docs/entscheidungen/fix-daten.md`, `fix-oberflaeche.md`, `fix-offen.md`, `review-20261114.md` | Integration (Behebung und Durchsicht vom 14.11.2026) | |
| `skripte/oeffentlich_pruefen.py`, `skripte/oeffentlich_ausnahmen.tsv`, `.github/workflows/pruefen.yml`, `.zenodo.json`, `docs/entscheidungen/O.md` | Paket Offene Wissenschaft, danach Belegschicht (Vorschlag) | |
| erzeugte Seiten `*.html`, `en/`, `de/` | niemand von Hand; nur `skripte/30_seiten.py` | |

### Schlüssel-Namensräume

- **Texte** (`window.KIEZ_TEXTE`): je Namensraum eine Datei `texte/<lang>/<ns>.js`, nur Schlüssel `<ns>.…`
  (`pruefen/texte.py`). Namensräume und Eigentümer: `daten/schema/texte.md`.
- **Daten** (`window.KIEZ_*`): Gerüst `KIEZ_ORT`, `KIEZ_I18N`, `KIEZ_LANG`, `KIEZ_TEXTE`; Gliederung und Bevölkerung
  `KIEZ_STADTTEILE`, `KIEZ_ZELLEN`, `KIEZ_KENNZAHLEN`, `KIEZ_PLANUNGSRAEUME`; Gebäude `KIEZ_GEB_<nr>`; Versorgung
  `KIEZ_PLANER`, `KIEZ_PLANER_FUSS`, `KIEZ_ERREICHBAR`, `KIEZ_ERREICHBAR_FUSS`, `KIEZ_EINRICHTUNGEN`,
  `KIEZ_EINRICHTUNGEN_ODBL`, `KIEZ_HALTESTELLEN`; Grundkarte `KIEZ_GRUNDKARTE`; seit Phase Datenpakete (KR15) außerdem
  Gliederung und Bevölkerung `KIEZ_STECKBRIEF`, `KIEZ_STECKBRIEF_DZIELNICE`; Gebäude `KIEZ_GEB_KENNZAHLEN`,
  `KIEZ_GEB_DZIELNICE`; Luft `KIEZ_POWIETRZE`; Wohnungsmarkt `KIEZ_MIESZKANIA`; Klima `KIEZ_KLIMAT`,
  `KIEZ_KLIMAT_ZELLEN`, `KIEZ_KLIMAT_STADTTEILE`; Denkmale `KIEZ_DENKMALE`, `KIEZ_DENKMALE_BDOT`,
  `KIEZ_DENKMALE_ODBL`; seit dem Abend des 13.11.2026 Sanierungsatlas `KIEZ_SANIERUNG`, `KIEZ_SANIERUNG_ODBL`; seit
  dem 14.11.2026 Vergleich `KIEZ_POROWNANIE`. Bibliotheken der Seitenmodule (keine Daten): `KIEZ_KARTENFELD`
  (`kartenfeld.js`, setzt weiter `KIEZ_KARTE`), `KIEZ_KS` (`kartenseite.js`), `KIEZ_TS` (`themenseite.js`). Die
  Dateien `zellen.js`, `kennzahlen.*` und `planer.js` heißen seit KR28 `zellen_odbl.js`, `kennzahlen_odbl.*` und
  `planer_odbl.js`; die globalen Namen sind gleich geblieben. Jede Datei unter `daten/` hat ein Schema mit `x-datei`
  und `x-global` in `daten/schema/` (`pruefen/daten.py`); neue Dateien nur mit neuem Schema über die Integration.
- **Hash** (Zustand der Seite, teilbar): Schlüssel bleiben deutsch und unsichtbar, u. a. `thema`, `st`
  (Stadtteil-`nr`, KR2), `k` (Kamera), `3d`, `luft`, `geb` (Karte), `raum`, `r`, `weg`, `zu` (Planer); seit dem 14.11.2026 auf der Karte `dz`
  (Färbung der Stadtteile) und `pkt` (Punktebenen, durch Komma getrennt), `thema` auch `fuss:<ziel>` und
  `klima:<anteil>` (KR36). Der Hash wird nur nach einer Handlung geschrieben, nie beim Laden. Der
  Sprachschalter nimmt den ganzen Hash mit.
- **Datenbank:** `public.*` schreibt nur die Pipeline, `auswertung.*` je Tabelle das Paket, das sie rechnet; die
  Tabellen legt nur `sql/` an.
- **Entscheidungen:** `KR<n>` in `docs/entscheidungen.md`; Pakete schlagen in `docs/entscheidungen/<paket>.md` vor.

### Übergabe an die Pakete

Im übernommenen JavaScript stehen noch rund 400 deutsche Textstellen; sie zieht das Paket Oberflächen-Texte in
`texte/`. Ortsgebunden und noch fest im Code (alles deutsche Satzteile, darum dort und nicht im Gerüst):
`atlas.js` und `karte.js` („ganz Potsdam“ im Kartenstatus, „Stadtteil … der Landeshauptstadt Potsdam“, Legende mit
der Potsdamer Bildzeile), `planer.js` (Planungsräume © Landeshauptstadt Potsdam, „ganz Potsdam“ in Vergleichstexten),
`schaugrafik.js` (Untertitel „Landeshauptstadt Potsdam“, Zensus 2022 als Quelle), `jahre.js` (Hinweistexte zu
Beispieldaten). `grep -n Potsdam *.js` zeigt die Stellen. In `jahre.js` (Liesmich-Text der Downloads) steht außerdem das Potsdamer
Koordinatensystem EPSG:25833 fest im Text; für Kraków gilt `rechen_srid` (KR1). `pruefen/texte.py` prüft die
Wortliste bisher auf den Texten unter `texte/` und dem sichtbaren Text der erzeugten Seiten, nicht auf den
JavaScript-Modulen; diese Prüfung ergänzt das Paket Oberflächen-Texte, sobald die Module ihre Texte aus `texte/`
holen. Impressum und Datenschutz verlinken je Sprache auf die polnische, englische bzw. deutsche Fassung der UG-Website
(Adressen in `config/krakow.yaml`, `impressum` und `datenschutz`; verbindlich ist die deutsche Fassung). Seit den Seitenpaketen (14.11.2026) haben `karta`, `dzielnica`, `index`, `planer`, `kamienice`, `modernizacja`
und `klimat` eine Kartenfläche über `kartenfeld.js` bzw. `kartenseite.js`; die Krakauer Module lesen die Namen
`zellen_odbl.js`, `planer_odbl.js` und `gebaeude/<nr>_odbl.js` (KR28), die Potsdamer Module `atlas.js`, `karte.js`
und `planer.js` bleiben unverändert und laden in der Gegenprobe weiter die alten Namen (KR36). Die Voraussetzung
`karte.grundkarte` ist erfüllt, `karte.luftbild` bleibt `null` und wird von `themen.js` abgefangen (KR32).

### Gegenprobe Potsdam

`pruefen/gegenprobe_potsdam.sh` baut aus `git archive HEAD` von `../kiezatlas-potsdam` zwei Wurzeln in einem
Wegwerf-Ordner: den unveränderten Potsdamer Stand und denselben Stand mit JavaScript, Stylesheets, `skripte/` und
`pruefen/*.py` aus diesem Repo, dazu `daten/ort.js` aus `pruefen/gegenprobe_potsdam/ort.yaml`. Angepasst wird
mechanisch nur die Skriptzeile für `ort.js`, `i18n.js` und `texte/de/kern.js` in jeder Seite und der Feldname
`in_potsdam` → `in_stadt` in den Daten (KR7). In beiden Wurzeln laufen die unveränderten Potsdamer Prüfungen
`seiten.mjs`, `A7_planer.mjs`, `B5_jahre.mjs`, die Codepfad-Prüfungen `A6_test_pfade.py`, `A8_test_pfade.py` und
ein Textabzug aller Seiten. Grün heißt: gleiche Rückgabe, gleiche Zahl an „ok“, gleiche „FEHLT“-Zeilen, gleicher
sichtbarer Text. Einzige zugelassene Abweichung ist das Startgewicht des Planers mit echten Daten unter den
nachgerechneten Bedingungen von KR10; die Gegenprobe meldet sie als „Ausnahme KR10“ mit den Bytewerten.

Ergebnis: siehe Abschnitt „Ergebnis der Gegenprobe“ unten.

### Ergebnis der Gegenprobe

Maßgeblich ist der Lauf vom 14.11.2026 nach den Merges der Seitenpakete `Arbeitszweig s1` bis `Arbeitszweig s4`, Potsdam
`stand-2026-11-07b-4-g7b6eb08` gegen dieses Repo `19634c3` (Protokoll:
`belege/gegenprobe_potsdam-20261114-19634c3.log`, Rückgabe 0, „0 Abweichungen“). Danach ist nur `pruefen/seiten.mjs`
geändert worden; die Gegenprobe startet die Potsdamer Fassung dieser Prüfung, ihr Ergebnis gilt weiter.

| Prüfung | Potsdam | umgebaut | gleich |
|---|---|---|---|
| `A6_test_pfade.py` | Rückgabe 0, 56 ok | Rückgabe 0, 56 ok | ja |
| `A8_test_pfade.py` | Rückgabe 1, 19 ok, 21 Zeilen mit FEHLT (der Fixture-Export braucht eine Datenbank, die in der Gegenprobe fehlt; im unveränderten Potsdamer Abzug genauso) | gleich | ja |
| `seiten.mjs` | Rückgabe 0, 120 ok | Rückgabe 0, 120 ok | ja |
| `B5_jahre.mjs` | Rückgabe 0, 251 ok | Rückgabe 0, 251 ok | ja |
| Textabzug, 9 Seiten | 89.664 Byte | gleich | ja |
| `A7_planer.mjs` | Rückgabe 0, 121 ok | Rückgabe 1, 119 ok, 2 × „Startgewicht mit echten Daten“ (331 KB gz gegen die Grenze 320) | Ausnahme KR10 |

Die einzige Abweichung ist die zugelassene Ausnahme KR10. Gegenüber dem Lauf `830e5d3` (328 KB gz) ist das
Startgewicht um 3 KB gz gestiegen, weil die Textschicht der Gegenprobe (`texte/de/planer.js` laut Kopfzeile der
Krakauer Vorlage) die Schlüssel der Krakauer Seite `planer` mitbringt (Textschicht 11.673 B gz statt 8.247 B gz,
KR39); der gemeinsame Code (`kopf.js`, `themen.js`, `planer.js`) ist unverändert 23.327 B gz und damit 559 B gz
leichter als in Potsdam. Die Auslieferung muss das Startgewicht live unter 320 KB gz halten (Auflage in KR10, KR35).

Frühere Läufe, abgelöst: `830e5d3` (nach den Merges `Arbeitszweig de`, `Arbeitszweig ds`, `Arbeitszweig df`, 328 KB gz), `13d7eba` (nach Phase Datenpakete, 327 KB gz), `d3d3b18` (nach KR12, 327 KB gz), `291befb`
(323 KB gz, Grundlage von KR10), `2593f02` (324 KB gz, damals als offene Abweichung gemeldet) und `8dd5a1b` (323 KB gz,
vor der Ausnahme KR10); auf dem Zweig des Pakets Schrift und Grundkarte die Läufe `DF_gegenprobe_potsdam-*.log`. Ihre
Protokolle bleiben unter `belege/` stehen.
