# Beleg Daten-Nacharbeit (14.11.2026)

Regeln vor dem Lauf: `pruefen/N1_protokoll.md` (Commit 4b58965, Nachtrag 1 zu Regel 5). Prüfung:
`python -I pruefen/N1_daten.py [--vergleich REV]`. Ausgangsstand `acba5f7` (Zweig `Arbeitszweig integration`).
Vorschläge und Offenes: `docs/entscheidungen/N1.md`.

## 1. Zahlen vorher und nachher (alle `daten/*.js`)

`pruefen/N1_daten.py --vergleich acba5f7` liest jede Datendatei im Ausgangsstand (`git show`) und heute und
vergleicht jede Zahl über ihren vollen Pfad. Ergebnis (Zählzeile der Prüfung: 28 Dateien, gleich 21, mit
Abweichung 5, neu 2):

| Datei | Zahlen vorher → nachher | weg / neu / geändert | Grund |
|---|---|---|---|
| 21 Dateien | gleich | 0 / 0 / 0 | |
| `planer_odbl.js` | 510 → 588 | 0 / 78 / 0 | neue Felder `radius_m`, `geheimhaltung_min_ew`, `gesamt.raeume_ohne_wert` |
| `planer_fuss_odbl.js` | 362 → 459 | 0 / 97 / 0 | dieselben Felder |
| `steckbrief_dzielnice_odbl.js` | 241 → 244 | 0 / 3 / 0 | `zuordnung.schwelle_proz` 99, Anteile 03 = 98,53 und 15 = 98,64 |
| `denkmale_odbl.js` | 1.827 → 1.827 | 0 / 0 / 3 | Ortsmarke (2 Koordinaten), `zaehlung.ausserhalb_stadt` 338 → 334 (Altfehler, Abschnitt 4) |
| `sanierung_odbl.js` | 1.286 → 610 | 678 / 2 / 474 | Punkte nur ab 3 Geschossen (Abschnitt 2) |
| `mieszkania.js` → `mieszkania_odbl.js` | umbenannt | | Abschnitt 3 |
| `stadtteile_uebersicht_odbl.js` | neu | | Abschnitt 5 |

Keine Zahl der Versorgung, der Gliederung, des Vergleichs, der Gebäude, des Klimas oder der Luft hat sich bewegt;
geändert sind dort nur Sätze, die Felder geworden sind.

## 2. Sanierungsatlas: Punkte nur an Gebäuden mit mindestens 3 Geschossen

Erzeuger `skripte/36_sanierung.py`, Beleg `belege/DS_sanierung_lauf.md`, Zählungen der Seite
`belege/S2_seiten_zaehlungen.md`. Erwartung vor dem Lauf (Protokoll Regel 2.5): 297 − 96 − 72 − 3 = 126.

| | vorher (`acba5f7`) | nachher |
|---|---|---|
| Punkte | 297 | 126 |
| Eigentum gmina / skarb_panstwa / publiczne_mieszane | 290 / 4 / 3 | 122 / 3 / 1 |
| ausgelassen als Kleinhaus | 44 | 44 |
| ausgelassen unter 3 Geschossen oder ohne Geschosszahl | – | 171 |
| Höhe aus LoD2 / aus Geschossen / ohne | 269 / 25 / 3 | 108 / 18 / 0 |

Punkte je dzielnica (vorher → nachher): 01 49 → 31, 02 12 → 3, 03 13 → 4, 04 14 → 2, 05 7 → 4, 06 7 → 2,
07 10 → 0, 08 27 → 22, 09 9 → 4, 10 9 → 2, 11 5 → 2, 12 15 → 8, 13 37 → 17, 14 7 → 2, 15 4 → 1, 16 15 → 5,
17 22 → 10, 18 35 → 7. Die Zählungen der Liste je dzielnica in `daten/sanierung.js` sind unverändert
(508 Einträge). Private Einträge bleiben nur gezählt, ohne Vergröberung.

Die abgeleitete Tabelle `$KIEZ_DATEN/abgeleitet/sanierung/zbk_tabelle.tsv` schreibt der Erzeuger bei jedem Lauf
neu. Vor und nach dem zweiten Lauf dieses Pakets: SHA256 `1d712c7707b1cb8aaaedeb5a47f88fd7447d340fb4ab509e23ddf257794f0a26`
(byte-gleich).

Ortsmarke ul. Kościuszki 18 (`skripte/ortsmarke.py`): [19.92538, 50.05421] in `denkmale_odbl.js` und
`sanierung_odbl.js` (vorher in `denkmale_odbl.js` [19.92536, 50.05426], der Adressknoten im Haus); OSM-Weg
`w233092542`, 2 Kandidaten in der Stadt. Geprüft von `pruefen/DS_sanierung.py` und `pruefen/N1_daten.py`.

## 3. Wohnungsmarkt: Fallzahlen unter der Mindestzahl

`daten/mieszkania_odbl.js` (Beispieldaten, `fixture: true`), Erzeuger `skripte/40_mieszkania.py --beispiel`, Beleg
`belege/DW_mieszkania.md`. Feldvergleich gegen `acba5f7` (`daten/mieszkania.js`), 342 Felder je Ort, Jahr und
Markt: 254 gleich (Median, n und Grund), 87 mit `n_unter_minimum`, davon 87 jetzt mit `n: null` und
`median: null`, 1 mit verdeckter Fallzahl (Stadt, 2025, ogolem; Median gleich), 0 anders. Die Seite zeigt unter der
Mindestzahl „n < 10“, bei verdeckter Fallzahl „k. A.“.

Differenzprobe (Protokoll Regel 4.5): Auf den Beispieldaten ließ sich zuerst 1 unterdrückte Fallzahl aus
veröffentlichten Summen zurückrechnen (Stadt minus Summe der dzielnice). Seit Nachtrag 2 verdeckt der Erzeuger die
Fallzahl der Summe (sekundäre Unterdrückung, 1 Feld); `pruefen/DW_mieszkania.py` rechnet unabhängig nach: 0
zurückrechenbare Fallzahlen, Gegenprobe ohne Verdeckung schlägt an.

## 4. Denkmale: Altfehler in `zaehlung.ausserhalb_stadt`

Die Auswahl des OSM-Lesers in `skripte/dz_denkmale.py` las die Adresse „Kościuszki 18“ mit, damit die Ortsmarke
gefunden wird; Adressobjekte dieses Namens außerhalb Krakaus zählten deshalb unter `ausserhalb_stadt`. Seit die
Ortsmarke aus `skripte/ortsmarke.py` kommt, liest die Auswahl nur `heritage` und `start_date`: 338 → 334. Alle
anderen Zahlen der Datei gleich.

## 5. Startseite: vereinfachte Stadtteilgrenzen und Startgewicht

Erzeuger `skripte/02a_stadtteile_uebersicht.py`, Beleg `belege/N1_stadtteile_uebersicht.md` (Toleranz 10 m,
größter Hausdorff-Abstand 10,7 m, größte Flächenabweichung 0,014 %). Startgewicht nach der Methode von
`belege/S1_seiten.md` (je Skript der erzeugten Seite `gzip -9 -c`, Summe), gemessen von `pruefen/N1_daten.py`:

| Seite | vorher (`acba5f7`) | nachher |
|---|---|---|
| `index.html` (pl) | 309.817 B | 285.782 B |
| `en/index.html` | – | 285.069 B |
| `de/index.html` | – | 285.121 B |
| `karta.html` (pl, genaue Grenzen) | 310.672 B | 310.651 B |
| `dzielnica.html` (pl, genaue Grenzen) | 321.929 B | 321.271 B |

Grenze der Bauvorlage für die Startseite: 307.200 B. Die Methode reproduziert die Einzelwerte des Belegs S1
(`vendor/maplibre-gl.js` 210.896 B, `daten/stadtteile_odbl.js` 50.943 B).

## 6. Keine Sätze in den Datendateien

`pruefen/N1_daten.py`, Prüfung 1: jede Zeichenkette mit drei oder mehr Wörtern in `daten/*.js` (ohne `ort.js`)
steht an einem Feldpfad der Positivliste (Quellen- und Lizenzvermerke, Eigennamen, Rohwerte der Quellen, Zitate aus
Rechtsakten, bibliographische Angaben). Ergebnis: 0 Befunde in 27 Dateien; keine Paketbezeichnung in den Daten.
Gegenprobe: Vor diesem Paket meldete dieselbe Prüfung Sätze in `planer_odbl.js`, `planer_fuss_odbl.js`,
`erreichbar.js`, `erreichbar_fuss_odbl.js`, `einrichtungen.js`, `einrichtungen_odbl.js`, `haltestellen.js`,
`steckbrief.js`, `steckbrief_dzielnice_odbl.js`, `porownanie.js`, `denkmale_odbl.js` und `mieszkania.js`, dazu die
Paketbezeichnung „Paket OSM und Fußwegnetz“ in `einrichtungen_odbl.js`, `erreichbar_fuss_odbl.js` und
`planer_fuss_odbl.js`, die verschiedenen Ortsmarken, fehlendes `radius_m` und das Startgewicht 309.817 B (Lauf der
Prüfung auf einem Abzug von `acba5f7`).

## 7. 3D-Dateien reproduzierbar

Befehl (Speichergrenze 8 GB über `systemd-run --user --scope -p MemoryMax=8G`):

```sh
uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
  python -I skripte/20_bdot10k.py --pruefen --geometrie "$KIEZ_DATEN/abgeleitet/gebaeude/2026-11-13-odbl"
```

Ergebnis am Stand `f185e70`: Rückgabe 0, 52 s, „byte-gleich“ für `gebaeude_kennzahlen.js`,
`gebaeude_dzielnice_odbl.js`, `D5_gebaeude_lauf.md` und alle 18 Dateien `01_odbl.js` bis `18_odbl.js`. Die
Prüfsummenliste `SHA256SUMS` im Ordner stimmt (`sha256sum -c --quiet SHA256SUMS`: 18 Einträge, kein Fehler). Derselbe Befehl lief schon vor dem Protokoll-Commit am
Ausgangsstand mit demselben Ergebnis (51 s).

## 8. Erzeuger mit Datenbank und ohne Platz in `pruefen.sh`

`pruefen.sh` überspringt die Erzeuger, die die Datenbank brauchen. Am Endstand dieses Pakets mit der Leserolle
`mosidi_lesen` (Umgebung wie `skripte/lauf.sh auswerten`) byte-genau nachgerechnet, alle „aktuell“, Rückgabe 0:
`skripte/11_einrichtungen_krakow.py --osm-db --pruefen` (`einrichtungen.js`, `einrichtungen_odbl.js`,
`belege/D6_einrichtungen.md`) und `skripte/14c_fussweg_export_krakow.py --pruefen` (`erreichbar_fuss_odbl.js`,
`planer_fuss_odbl.js`, `belege/DE_fussweg_export.md`). Ebenso ohne Datenbank `13_oepnv_krakow.py`,
`14_erreichbarkeit_krakow.py`, `15_planer_krakow.py` und `02a_stadtteile_uebersicht.py`, je mit `--pruefen`.

## 9. Prüfstand

`./pruefen.sh --voll --gegenprobe` am Stand `1996f49` (mit Browser, Neurechnung aus den Rohdaten, Gegenprobe
Potsdam): 58 Prüfungen, 53 grün, 0 mit Befund, 5 übersprungen mit Grund; Gegenprobe Potsdam 0 Abweichungen (nur die
zugelassene Ausnahme KR10, Startgewicht 331 KB gz). Protokoll: `belege/N1_pruefen-voll-gegenprobe-1996f49.log`
(persönliche Pfade durch `../` ersetzt). Der Lauf davor am Stand `bcfd2cf` hatte 2 Befunde (Plankennung in einem
Kommentar, Klima-Beleg mit alter Prüfsumme), beide behoben: `belege/N1_pruefen-voll-gegenprobe-bcfd2cf.log`.
