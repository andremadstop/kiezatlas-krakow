# Beleg Ziele der Fußweg-Rechnung in der Datenbank (erzeugt)

Erzeugt von `skripte/14a_ziele_db_krakow.py`; nicht von Hand ändern. Quellen: `daten/einrichtungen.js` (BDOT10k), BDOT10k `OT_KUSK_A` (`$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip`), `daten/haltestellen.js` (GTFS der ZTP, Taktklassen I, II).

| Tabelle | Art bzw. Klasse | Zeilen vorher | Zeilen nachher |
|---|---|---|---|
| `auswertung.einrichtung` | przedszkole | 0 | 35 |
| `auswertung.einrichtung` | szkola | 0 | 170 |
| `auswertung.einrichtung` | szpital | 0 | 24 |
| `auswertung.einrichtung` | zlobek | 0 | 2 |
| `auswertung.gruenflaeche` | park | 0 | 90 |
| `auswertung.haltestelle` | I | 0 | 509 |
| `auswertung.haltestelle` | II | 0 | 284 |

Nicht übernommen aus `daten/einrichtungen.js`: art park: 90.
Haltestellen in `daten/haltestellen.js`: 944, davon Taktklasse I oder II: 793.
