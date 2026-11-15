# Beleg Echtlauf der Daten (13.11.2026)

Alle Themen mit den vorhandenen echten Daten neu gerechnet, Zweig `Arbeitszweig de`, Ausgangsstand `Arbeitszweig integration` 2fcba71.
Zählungen vorher und nachher je Datei unter `daten/`; die Zahlen je Schritt stehen in den erzeugten Belegen der Pakete,
die hier genannt sind. Zustand gemessen mit einem Zählskript außerhalb des Repos (Datei lesen, `fixture`, Zahl der
Features, Stadtteile bzw. Räume, Bytes).

## Eingänge (Prüfsummen in `belege/rohdaten-DE-2026-11-13.sha256`)

| Datei unter `$KIEZ_DATEN` | SHA256 | Herkunft |
|---|---|---|
| `eingang/malopolskie-261112.osm.pbf` | `525d0d227cb9c876c4df02278e7fac870f0825ab0ae2c7228af6dc5c9e0f5a7e` | Handdownload Geofabrik, Stand 12.11.2026 (`eingang/HERKUNFT.md`); gleich `eingang/SHA256SUMS` |
| `osm/2026-11-12/malopolskie-261112.osm.pbf` | gleich | Kopie durch `skripte/12_osm.py --uebernehmen`, SHA256 beim Kopieren verglichen |
| `eingang/lod2_1261_gml.zip` | `de14ed1860865d58b5b4c57b256e1a0da7218680effe19be66a885c290091356` | Handdownload Geoportal, LoD2 Stand 2017; gleich `eingang/SHA256SUMS` |

Die übrigen Eingänge (BDOT10k 1261, Eurostat-Gitter, NSP-Tabelle, GTFS) sind unverändert und in den Listen der
Pakete gehasht (`belege/rohdaten-D4-…`, `-D5-…`, `-D6-…`, `-dz-…`).

## Reihenfolge und Ergebnis

| Nr | Schritt | Skript | Ergebnis | Beleg |
|---|---|---|---|---|
| 1 | dzielnice aus dem OSM-Auszug, Zellen und Kennzahlen als `_odbl` | `skripte/02_bevoelkerung.py` | 18 dzielnice, 327 Zellen, Regel 3: Fläche −0,01 %, symmetrische Differenz 0,01 %; Regel 4 grün mit dokumentierter Ausnahme III (98,53 %) und XV (98,64 %) | `belege/D4_bevoelkerung.md` |
| 2 | Zelltabelle und Grenzen in die Datenbank | `sql/003_zellen.sql`, `skripte/05_db_gliederung.sh` | `public.stadtteil` 0 → 18, `public.zensus_zelle` 0 → 327, gleich `daten/zellen_odbl.js` und der Zellauswahl der Fußweg-Rechnung | `belege/DE_db_gliederung.md` |
| 3 | OSM laden | `skripte/12_osm.sh laden --uebernehmen --pbf …` | `auswertung.osm_poi` 0 → 3.001 (apotheke 321, arzt 283, pflege 20, spielplatz 1.107, supermarkt 1.270); Netz 0 → 626.425 Knoten, 691.029 Kanten; größte Komponente 98,2 % der Knoten im Stadtgebiet | `belege/DE_osm_netz.md` |
| 4 | Ziele der Fußweg-Rechnung | `skripte/14a_ziele_db_krakow.py` | `auswertung.einrichtung` 0 → 231, `gruenflaeche` 0 → 90, `haltestelle` 0 → 793 (Taktklasse I 509, II 284) | `belege/DE_ziele_db.md` |
| 5 | Fußwegnetz rechnen | `skripte/14b_fussweg.sh rechnen` | 11 Arten × 327 Zellen, 0 Verstöße Fußweg < Luftlinie, Median Fußweg/Luftlinie 1,40; `14b_fussweg.sh pruefen` grün | `belege/DE_fussweg.md` |
| 6 | Versorgung, Erreichbarkeit, Planer | `skripte/11_…`, `13_…`, `14_…`, `15_…_krakow.py`, `14c_fussweg_export_krakow.py` | `einrichtungen_odbl.js` 604 OSM-Punkte; `erreichbar.js` 327 Zellen (Luftlinie); `erreichbar_fuss_odbl.js` 11 Arten; `planer_odbl.js` und `planer_fuss_odbl.js` je 18 dzielnice | `belege/D6_*.md`, `belege/DE_fussweg_export.md` |
| 7 | Gebäude je dzielnica und LoD2-Höhen | `skripte/20_bdot10k.py` | 90.563 Gebäude, alle in genau einer dzielnica; Höhe aus lod2 74.320, geschosse 16.230, ersatz 13 | `belege/D5_gebaeude_lauf.md` |
| 8 | Klima je dzielnica | `skripte/35_klimat.py` | `klimat_stadtteile_odbl.js` echt; Grün je Einwohner der Stadt 194 m² | `belege/dk_klimat.md` |
| 9 | Denkmale aus OSM | `skripte/dz_denkmale.py` | 906 Objekte in der Stadt (heritage 167, start_date 813), 427 mit Gebäude; Stichprobe 20 aufgelistet, nicht ausgewertet | `belege/DZ_denkmale_lauf.md` |

## Dateien unter `daten/`, vorher und nachher

| Datei | vorher (`Arbeitszweig integration` 2fcba71) | nachher |
|---|---|---|
| `denkmale_odbl.js` | Beispiel, 1.953 B | echt, 153.602 B |
| `einrichtungen_odbl.js` | Beispiel, 15 Punkte, 3.206 B | echt, 604 Punkte, 96.652 B |
| `erreichbar.js` | Beispiel, 18.520 B (582 Beispielzellen) | echt, 10.534 B (327 Zellen) |
| `erreichbar_fuss_odbl.js` | fehlte | echt, 19.502 B |
| `gebaeude_dzielnice_odbl.js` | Beispiel, 18 Stadtteile, 16.549 B | echt, 18, 16.895 B |
| `gebaeude_kennzahlen.js` | echt, 5.775 B | echt, 6.081 B (Höhenherkunft mit LoD2) |
| `haltestellen.js` | echt, 944 Haltestellen, 216.722 B | echt, 944, 216.759 B (nur der Hinweistext; `st` bleibt `null`) |
| `kennzahlen.js`, `kennzahlen.json` | Beispiel, 18 Stadtteile | entfallen (neuer Name, Lizenzfolge Variante a) |
| `kennzahlen_odbl.js`, `kennzahlen_odbl.json` | fehlten | echt, 18 Stadtteile, 9.065 B bzw. 12.408 B |
| `klimat.js` | echt, 2.627 B | echt, 2.580 B (Grün je Einwohner der Stadt mit echten Einwohnern) |
| `klimat_stadtteile_odbl.js` | Beispiel, 18, 7.579 B | echt, 18, 7.507 B |
| `ort.js` | echt, 9.522 B | echt, 9.521 B (`zuordnung_geprueft` = `true`) |
| `planer.js` | Beispiel, 18 Räume, 76.195 B | entfällt (neuer Name `planer_odbl.js`) |
| `planer_odbl.js` | fehlte | echt, 18 Räume, 75.884 B |
| `planer_fuss_odbl.js` | fehlte | echt, 18 Räume, 59.845 B |
| `stadtteile_odbl.js` | Beispiel, 18 Rechtecke, 5.198 B | echt, 18 Grenzen (auf 3 m vereinfacht), 215.028 B, gzip 50.943 B |
| `steckbrief.js` | echt, 14.772 B | echt, 14.603 B (je dzielnica weiter `null` mit Grund) |
| `steckbrief_dzielnice_odbl.js` | echt, 10.787 B | echt, 11.170 B (Vermerk zur Gruppenzuordnung) |
| `zellen.js` | Beispiel, 582 Zellen, 162.055 B | entfällt (neuer Name) |
| `zellen_odbl.js` | fehlte | echt, 327 Zellen, 90.973 B |

Unverändert: `denkmale.js` (Beispiel), `denkmale_bdot.js`, `einrichtungen.js`, `grundkarte.js`, `klimat_zellen.js`,
`mieszkania.js` (Beispiel), `powietrze.js` (Beispiel).

Beispieldateien danach: `denkmale.js`, `mieszkania.js`, `powietrze.js` (vorher 12). NSP je dzielnica bleibt `null` mit
Grund (Geometrie der rejony fehlt). `denkmale.js` ist die eine Beispieldatei über den Auftrag hinaus: kein Register und
kein Wikidata-Abzug im Eingang (`docs/entscheidungen/DE.md`, DE5).

Startseite (`index.html` mit Skripten und Stylesheets, gzip -9): 77.028 B, davon `stadtteile_odbl.js` 50.943 B.

## Abnahmen

| Prüfung | Ergebnis |
|---|---|
| `pruefen/D4_bevoelkerung.py` | 0 Befunde |
| `pruefen/D5_gebaeude.py` | 0 Befunde |
| `pruefen/D6_versorgung.py` (mit PG-Umgebung, Rolle `mosidi_lesen`) | 0 Befunde |
| `pruefen/dk_klimat.py` | 0 Befunde |
| `pruefen/DZ_denkmale.py`, `pruefen/DZ_test_eingang.py` | 0 Befunde |
| `skripte/12_osm.sh pruefen`, `skripte/14b_fussweg.sh pruefen`, `skripte/05_db_gliederung.sh pruefen` | grün |
| `pruefen/daten.py` | 0 Abweichungen, 3 Beispieldateien |
| `./pruefen.sh` (Lauf auf fefeb95) | 27 Prüfungen, 20 grün, 0 Befund, 7 übersprungen. Kopf: „Arbeitsstand: offene Änderungen“, weil `berichte/` (Laufberichte von `12_osm.sh`, `14b_fussweg.sh`, `lauf.sh rechte`) nicht versioniert und nicht ignoriert ist. Erster Lauf scheiterte nur an fehlendem `node_modules` im Worktree (Verweis auf den Haupt-Checkout gesetzt) |
| `pruefen/gegenprobe_potsdam.sh` (auf 4516bfe) | 0 Abweichungen; A7 nur Ausnahme KR10 (327 KB gz, wie bisher) |
| `pruefen/DW_mieszkania.py`, `D7_powietrze.py`, `D8_grundkarte.py` | 0 Befunde (`mieszkania.js` als Beispiel auf die echten Grenzen neu erzeugt) |
| `pruefen/D2_wegwerf_db.sh` | Abnahme 0, 31 Tests grün (Beleg außerhalb des Repos, `belege/D2_fussweg.md` unverändert) |
| `skripte/lauf.sh rechte` | 49 Prüfungen, 0 Fehler |

## Grenzen

- Die Stichprobe der OSM-Denkmale ist nicht am Luftbild geprüft (`sichtpruefung.geprueft: false`).
- Die 3D-Dateien je dzielnica liegen außerhalb des Repos unter
  `kiezatlas-daten/krakow/abgeleitet/gebaeude/2026-11-13-odbl/` (`<nr>_odbl.js`, ODbL-Vermerk im Kopf, `SHA256SUMS`):
  18 Dateien, 90.563 Gebäude (= lod2 74.320 + geschosse 16.230 + ersatz 13), 32.484.980 B, gzip 5.702.953 B.
  Nachbesserung: ab der zweiten Zeile Byte für Byte gleich mit dem ersten Lauf (`../2026-11-13/`, 32.471.966 B, ohne
  ODbL-Vermerk, dort in `HERKUNFT.md` als ersetzt markiert); `daten/gebaeude_kennzahlen.js`,
  `daten/gebaeude_dzielnice_odbl.js` und `belege/D5_gebaeude_lauf.md` blieben beim Neulauf unverändert (Prüfsummen
  vor/nach gleich). Schema `daten/schema/gebaeude_odbl.json` geprüft: 0 Fehler.
- Die Regel-Nachträge in `pruefen/D4_protokoll.md` stehen im selben Commit wie der Lauf, nicht davor (offengelegt in
  `docs/entscheidungen/DE.md`).

## Nachbesserung nach der Gegenprüfung (13.11.2026 abends)

| Fund | Behebung | Zählung / Beleg |
|---|---|---|
| `stand` in `denkmale_odbl.js` war das BDOT10k-Datum | `skripte/dz_denkmale.py` liest den Zeitstempel aus dem Kopf des Auszugs | `stand` 2026-10-03 → 2026-11-12; JSON-Vergleich vorher/nachher: nur `stand` anders; `DZ_denkmale.py` 0 Befunde |
| ODbL-Vermerk fehlte im sichtbaren Seitenfuß | `skripte/30_seiten.py` setzt `kern.odbl` (pl, en, de) mit Link auf openstreetmap.org/copyright in den Fuß jeder Seite, deren Kopfzeile `daten:` eine `_odbl`-Datei nennt | 9 Seiten (index, dzielnica, karta × 3 Sprachen); 360/390 px ohne Überstand, axe ohne Verstoß (`pruefen/seiten.mjs`) |
| 3D-Dateien ohne `_odbl` und ohne Vermerk | `<nr>_odbl.js` mit Vermerk, Vertrag `daten/schema/gebaeude_odbl.json` | 18 Dateien, 90.563 Gebäude, Inhalt ab Zeile 2 gleich dem ersten Lauf; neu unter `abgeleitet/gebaeude/2026-11-13-odbl/` |
| Zellmenge: Kommentar widersprach DE3 | IDs beider Mengen in `skripte/02_bevoelkerung.py` verglichen, Kommentar in `sql/003_zellen.sql` berichtigt und eingespielt | 327 / 327, 0 nur über die dzielnice; Fußweg neu: 3.597 Zeilen wie vorher, Exporte Byte für Byte gleich |
| Beispieldaten nicht mehr auf Reproduzierbarkeit geprüft | `pruefen.sh` prüft jede Datei mit `fixture: true` über ihren Erzeuger (`--pruefen`) | 3 Dateien (denkmale.js, mieszkania.js, powietrze.js), 3 Erzeuger, 0 Befunde |
| `config/krakow.yaml` nannte die Zuordnung „zu prüfen“ | Kommentar berichtigt, `daten/ort.js` neu (Prüfsumme der Quelle) | `31_ort.py --pruefen` grün |
| Wikidata nicht abgerufen | Probeabfrage über `skripte/abruf.py`: `robots.txt` von query.wikidata.org sperrt `/sparql`, Abfrage nicht gestellt | Abrufprotokoll 13.11.2026 21:17:22 UTC (nur robots.txt, 95 B); `denkmale.js` bleibt Beispiel (DE5) |
| Schrift ohne polnische Zeichen | nicht hier: auf `Arbeitszweig df` erledigt (`adcb6cf`) | fontTools: 5 von 5 Schnitten mit allen 18 Zeichen |

Prüfungen nach der Nachbesserung: `./pruefen.sh` (auf d4de768) 27 Prüfungen, 21 grün, 0 Befund, 6 übersprungen;
`D4_bevoelkerung.py`, `D5_gebaeude.py`, `dk_klimat.py`, `DZ_denkmale.py`, `DZ_test_eingang.py`, `D6_versorgung.py`
(Rolle `mosidi_lesen`) je 0 Befunde; `14b_fussweg.sh pruefen` grün; `pruefen/gegenprobe_potsdam.sh` (auf d4de768): 0 Abweichungen, Rückgabe 0; A7 nur Ausnahme KR10
(327 KB gz wie bisher), Textschicht 8.247 B gz zusätzlich (vorher 8.191 B, +56 B durch `kern.odbl`).

## Zweite Nachbesserung (13.11.2026 spät)

| Fund | Behebung | Zählung / Beleg |
|---|---|---|
| `denkmale.js` Beispieldaten (blockierend) | nicht behebbar: `robots.txt` von query.wikidata.org sperrt `/sparql` (DE5); kein Ausweichen | Suche nach Handdownloads in `kiezatlas-daten/` (`*wikidata*`, `*zabytk*`, `*nid*`): nur Potsdamer Dateien und der robots-Befund, kein Kraków-Eingang. Bleibt rot bis zum Handdownload |
| Schrift ohne polnische Zeichen auf diesem Zweig (wichtig) | nicht auf `Arbeitszweig de` übernommen (Dateien des Pakets Schrift und Grundkarte, Merge über die Integration); stattdessen eigene Glyphenprüfung ohne brotli | siehe Tabelle unten: `Arbeitszweig de` je Schnitt 225 Zeichen, 16 von 18 fehlen (nur ó/Ó); `Arbeitszweig df` (d39019a) je Schnitt 387 Zeichen, 0 fehlen |
| `stand` von `denkmale.js` nach dem Wikidata-Eingang | Abruftag aus `eingang/HERKUNFT.md`, Abbruch ohne ihn (DE5) | `dz_denkmale.py --pruefen`: 4 von 4 Dateien gleich; Testdateien: 2 Abruftage gelesen (Zeile mit Größenangabe hinter dem Namen), 3 Abbrüche (Zeile fehlt, Zeile ohne Datum, Datei fehlt) |
| `berichte/` weder versioniert noch ignoriert | `berichte/` in `.gitignore` wie in kiezatlas-potsdam; Zahlen daraus stehen in `belege/` (`DE_fussweg.md`, diese Datei) | `git status` danach leer |

Glyphenprüfung: `fc-query --format=%{charset}` (fontconfig 2.18.3, FreeType liest die cmap der WOFF2), verlangt
ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ (18 Zeichen). Blob-Kennungen aus `git rev-parse <zweig>:fonts/<datei>` (erste 12 Stellen).

| Schnitt | `Arbeitszweig de` Blob | Zeichen | fehlend | `Arbeitszweig df` Blob | Zeichen | fehlend |
|---|---|---:|---|---|---:|---|
| barlow-400-normal | 3914af46036a | 225 | ąćęłńśźżĄĆĘŁŃŚŹŻ | 460eb4e8d010 | 387 | keine |
| barlow-500-normal | b1d06c6db025 | 225 | ąćęłńśźżĄĆĘŁŃŚŹŻ | 912c902dcc51 | 387 | keine |
| barlow-600-normal | b1a019f9d0eb | 225 | ąćęłńśźżĄĆĘŁŃŚŹŻ | 108a233b03fd | 387 | keine |
| barlow-semi-condensed-500-normal | ccb4b3a028e1 | 225 | ąćęłńśźżĄĆĘŁŃŚŹŻ | dedbc89404a0 | 387 | keine |
| barlow-semi-condensed-600-normal | 613e861ac598 | 225 | ąćęłńśźżĄĆĘŁŃŚŹŻ | d0561c2a2121 | 387 | keine |

Weiter offen und an andere Pakete übergeben (unverändert): Luftbild-Stichprobe der OSM-Denkmale nicht ausgewertet
(`sichtpruefung.geprueft: false`, DE6); `atlas.js`/`karte.js` laden fest `daten/gebaeude/<nr>.js`, die Dateien heißen
`<nr>_odbl.js` und liegen außerhalb des Repos unter `kiezatlas-daten/krakow/abgeleitet/gebaeude/2026-11-13-odbl/`
(Ablage und Name sind Sache der Integration und des Seitenpakets, DE7).


Prüfungen nach der zweiten Nachbesserung, beide auf 6a908b7, Arbeitsstand sauber, Läufe unter
`systemd-run --user --scope -p MemoryMax=8G`: `./pruefen.sh` 27 Prüfungen, 21 grün, 0 Befund, 6 übersprungen
(Browserprüfung `pruefen/seiten.mjs` in pl, en und de grün, 46 s). `./pruefen.sh --gegenprobe` 27 Prüfungen, 22 grün,
0 Befund, 5 übersprungen; Gegenprobe Potsdam 0 Abweichungen, Rückgabe 0. A7 hat nur die Ausnahme KR10 (327 KB gz),
die Textschicht ist 8.247 B gz groß.
