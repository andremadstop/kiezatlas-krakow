# Quellen des Pakets Seiten Erzählung, Karte, Steckbrief, Vergleich

Stand 14.11.2026. Zulieferung für `QUELLEN.md` und `daten/LIZENZ.md` (übernimmt die Belegschicht). Die Seiten index,
karta und dzielnica lesen nur Dateien anderer Pakete (Quellen dort); neu ist allein der Vergleich Kraków–Potsdam.
Rechnung und Zählungen: `belege/S1_porownanie.md` (erzeugt von `skripte/41_porownanie.py`).

## Quellen

| Quelle | Nutzer | Adresse | Lizenz | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| Eurostat, Census 2021 population grid, Deutschland, 1 km (`DE_PD_3035_GPKG.zip`) | `skripte/41_porownanie.py` → `daten/porownanie.js` (Potsdam) | https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/DE_PD_3035_GPKG.zip | CC BY 4.0 (strengste Lesart, wie die polnische Lieferung) | „EU copyright rules apply, while the licence would be under CC-BY 4.0.“ | A (`skripte/abruf.py`, 2026-11-13T23:36:32Z, robots-Befund der Machbarkeitsprobe) | Tabelle `DE_ESTAT_DF_CENSUS_GRID_2021_20240711122558`; Stichtag 15.05.2022 aus Vorwissen, nicht geprüft (Metadaten im Zip nennen nur den Zeitraum ab 2021-01-01) |
| Eurostat, Census 2021 population grid, Polen, 1 km | über `daten/steckbrief.js` (Paket Gliederung und Bevölkerung) | siehe `quellen-D4.md` | CC BY 4.0 | wie oben | – | wie dort |
| Stadtteile Potsdam (Kiezatlas Potsdam, `daten/stadtteile.js`) | `skripte/41_porownanie.py`: Stadtgrenze Potsdam (Vereinigung der Stadtteile) und Fläche | Repo `../kiezatlas-potsdam`, gelesen mit `git show <commit>:daten/stadtteile.js` (Commit in `daten/porownanie.js`) | dl-de/zero-2-0 (laut `kiezatlas-potsdam/daten/LIZENZ.md`) | keine Quellenangabe verlangt; die Seite nennt „Stadt Potsdam, dl-de/zero-2-0“ | L (lokales Repo) | Potsdamer Stand `stand-2026-11-08b` |
| Kennzahlen Potsdam (Kiezatlas Potsdam, `daten/kennzahlen.js`) | nur Gegenprobe in `belege/S1_porownanie.md` (Fläche; Zensus-100-m-Summe) | wie oben | Zensus-Werte dl-de/by-2-0 | nicht auf den Seiten; die 100-m-Zahl steht nur im Beleg, dort mit wörtlicher Quellenangabe und Link zum Lizenztext | L | wie oben |

Prüfsumme der Rohdatei beim Abruf: `belege/rohdaten-S1-2026-11-14.sha256`; Herkunft:
`$KIEZ_DATEN/2026-11-14/41_vergleich/HERKUNFT.md`. Die Eurostat-Fundstelle ist dieselbe wie für die polnische
Lieferung (`quellen-D4.md`, Fundstellen).

## Ausgaben und ihre Lizenz

| Ausgabe | Inhalt | Lizenz |
|---|---|---|
| `daten/porownanie.js` | Stadtwerte Kraków und Potsdam aus dem Eurostat-Gitter (Einwohner, Altersgruppen, Anteile, Fläche, Dichte), Quellen, Kontrollzahlen | CC BY 4.0 (Eurostat) mit Nennung „Eurostat, Census 2021 population grid“; Fläche Krakaus aus der PRG (BDOT10k, Quellenangabe nach art. 40c ust. 3) |
| Seiten index, karta, dzielnica, porownanie (pl, en, de) | Texte und Grafiken | Code Apache-2.0, Texte und Grafiken CC BY 4.0; Daten nach den Lizenzen der geladenen Dateien (Fußvermerk ODbL, wo `_odbl`-Dateien geladen werden) |
