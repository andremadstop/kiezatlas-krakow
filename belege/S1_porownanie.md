# Vergleich Kraków–Potsdam: Rechnung und Gegenprobe

Erzeugt von `skripte/41_porownanie.py` (nicht von Hand ändern). Datei: `daten/porownanie.js`.

## Eingänge

- `$KIEZ_DATEN/2026-11-14/41_vergleich/DE_PD_3035_GPKG.zip`, SHA256 `a48d945bd23981e74098228cc947509d413e5514b5e603e5ffc2c706fb08b262` (Prüfsumme beim Abruf: `belege/rohdaten-S1-2026-11-14.sha256`)
- `daten/steckbrief.js` (Kraków, Stadtwerte des Gitters), SHA256 `f29afafa087fad4d9958c9ca64e3f0bc4f4800cf815fd283f5e51bda4c781cc1`
- Potsdamer Atlas `kiezatlas-potsdam`, Commit `7b6eb08d9790d9235fa524f3925d1bbac20593c9` (`stand-2026-11-08b`): `daten/stadtteile.js` (SHA256 `bfb89ab27870776d75c933295155397e8db16772012d0ad3b0be66fc3b79a833`), `daten/kennzahlen.js` (nur Gegenprobe)

## Zählungen Potsdam

- Gitterdatei DE: Tabelle `DE_ESTAT_DF_CENSUS_GRID_2021_20240711122558`, 361699 Zellen; im Rahmen der Stadtgrenze 400, davon mit Mittelpunkt in der Stadt 190
- Zellen mit Mittelpunkt in der Stadt nach T_OBS_STATUS: {'leer': 190}; mit T_SPECIAL_VALUE: 0; mit fehlender Altersgruppe: 0
- Einwohner 180339; Altersgruppen unter 15 27244, 15–64 116559, 65+ 36579, Summe 180382
- Anteile: unter 15 15.1 %, 15–64 64.6 %, 65+ 20.3 %
- Fläche (Vereinigung der Stadtteile, EPSG:3035): 188.24 km²; Dichte 958 je km²

## Zählungen Kraków (aus `daten/steckbrief.js`, nachgerechnet)

- Zellen 327, Einwohner 793392; unter 15 110865, 15–64 530314, 65+ 152118, Summe 793297
- Anteile: unter 15 14.0 %, 15–64 66.8 %, 65+ 19.2 % (gleich den Werten in steckbrief.js: geprüft)
- Fläche 326.86 km² (PRG in BDOT10k); Dichte 2427 je km²

## Gegenprobe

- Fläche Potsdam: 188.24 km² gegen 188.2 km² im Potsdamer Atlas, Abweichung 0.02 % (Grenze 0.5 %)
- Einwohner Potsdam: 180339 (Eurostat 1 km) gegen 182673 (Zensus 2022, 100-m-Gitter, Potsdamer Atlas), Abweichung -1.28 %. Unterschied erwartet: andere Zellgröße, andere Geheimhaltung; die 100-m-Zahl erscheint nicht auf der Seite (Lizenz dl-de/by-2-0, Vermerk nur deutsch).
  Quellenangabe der 100-m-Zahl (wörtlich aus dem Potsdamer Atlas): Zensus 2022, Stichtag 15.05.2022, 100-m-Gitter; © Statistische Ämter des Bundes und der Länder, 2024, dl-de/by-2-0; eigene Auswertung (Bevölkerungszahl); Lizenztext https://www.govdata.de/dl-de/by-2-0

## Grenzen

- Stichtage verschieden: Kraków 2021-03-31, Potsdam 2022-05-15; beide nicht am Primärdokument geprüft (die INSPIRE-Metadaten in DE_PD_3035_GPKG.zip nennen nur den Zeitraum ab 2021-01-01).
- Die Fläche Krakaus stammt aus der PRG (Rechen-SRID des Atlas, EPSG:2178), die Potsdams aus der Stadtteilgrenze (EPSG:3035); beide flächentreu genug für eine Dichte in ganzen Personen je km².
- Nicht verglichen (auf der Seite benannt): Gebäude (BDOT10k gegen ALKIS), Bauzeit und Heizung (für Kraków keine offenen Daten), Taktklassen (Kraków nur in 1-km-Zellen), Werte je Stadtteil (Zellgröße zu grob, Grenzen Krakaus unter ODbL).
