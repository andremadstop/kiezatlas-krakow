# Quellen und Ausgaben des Echtlaufs der Daten (Lieferung zur Übernahme in QUELLEN.md und daten/LIZENZ.md)

Neue Quellen kommen nicht hinzu; gelesen werden die Handdownloads im gemeinsamen Eingang und die Rohdaten der Pakete.
Neu sind Ausgaben und deren Lizenz nach der Entscheidung vom 13.11.2026 zur Lizenzfolge der OSM-Grenzen (Variante a).

## Quellen (gelesen)

| Quelle | Nutzer | Fundstelle der Lizenz (wörtlich) | Weg | Stand |
|---|---|---|---|---|
| OpenStreetMap, Auszug Małopolska (Geofabrik) | `skripte/02_bevoelkerung.py`, `05_db_gliederung.py`, `12_osm.py`, `dz_denkmale.py` | „OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF).“ (https://www.openstreetmap.org/copyright) | H (`eingang/`, Kopie nach `osm/2026-11-12/`) | Datenstand 12.11.2026 |
| GUGiK, Modele 3D budynków LoD2, Powiat 1261 | `skripte/20_bdot10k.py` über `20_lod.py` | „Modele 3D budynków są dostępne bezpłatnie i możliwe do dowolnego wykorzystania.“ (https://www.geoportal.gov.pl/pl/dane/inne-dane/modele-3d-budynkow/); nach der Entscheidung vom 13.11.2026 ausreichende Grundlage | H (`eingang/lod2_1261_gml.zip`) | 2017 (Last-Modified der Datei 01.03.2019) |

## Ausgaben und ihre Lizenz

| Datei | Inhalt | Lizenz, Vermerk |
|---|---|---|
| `daten/stadtteile_odbl.js` | Grenzen der 18 dzielnice (echt, auf 3 m vereinfacht) | ODbL 1.0, © OpenStreetMap-Mitwirkende |
| `daten/zellen_odbl.js` (neuer Name statt `zellen.js`) | 327 Zellen des Eurostat-Gitters mit Einwohnern, Altersanteilen und Zuordnung `st` | ODbL 1.0 (Zuordnung aus den OSM-Grenzen); Einwohner Eurostat, CC BY 4.0 |
| `daten/kennzahlen_odbl.js`, `.json` (statt `kennzahlen.*`) | Kennzahlen je dzielnica und Stadt | ODbL 1.0; Einwohner Eurostat, CC BY 4.0; Vermerk im Kopf bzw. Feld `lizenz` |
| `daten/planer_odbl.js` (statt `planer.js`) | Versorgung je dzielnica, Luftlinie | ODbL 1.0 (Zuordnung `st`); BDOT10k (Quellenangabe), GTFS ZTP (CC BY 4.0) |
| `daten/planer_fuss_odbl.js` | Versorgung je dzielnica, Fußweg | ODbL 1.0 (OSM-Wegenetz und Zuordnung); BDOT10k, GTFS ZTP |
| `daten/erreichbar_fuss_odbl.js` | Fußweg je Zelle und Art | ODbL 1.0 (OSM-Wegenetz, OSM-Ziele); BDOT10k, GTFS ZTP |
| `daten/einrichtungen_odbl.js` | Ärzte und Apotheken aus OSM (echt) | ODbL 1.0 |
| `daten/gebaeude_dzielnice_odbl.js` | Gebäude je dzielnica (echt) | ODbL 1.0 (Zuordnung); BDOT10k (Quellenangabe nach art. 40c ust. 3) |
| `daten/klimat_stadtteile_odbl.js` | Bodenbedeckung je dzielnica (echt) | ODbL 1.0 (Zuordnung); BDOT10k |
| `daten/denkmale_odbl.js` | OSM-Objekte mit heritage/start_date (echt, Lage ungeprüft) | ODbL 1.0 |
| `daten/gebaeude_kennzahlen.js` | Stadt und delegatury, mit Höhenherkunft | BDOT10k (Quellenangabe); Höhen GUGiK LoD2 mit wörtlicher Freigabe im Feld `quellen.hoehen.vermerk` |
| `daten/erreichbar.js`, `daten/klimat.js` | je Zelle bzw. Stadt, ohne Zuordnung zur dzielnica | ohne ODbL: die 327 Zellen sind genau die mit Mittelpunkt in der BDOT10k-Stadtgrenze (`belege/D4_bevoelkerung.md`, Schritt 4: 327) |
| `kiezatlas-daten/krakow/abgeleitet/gebaeude/2026-11-13-odbl/<nr>_odbl.js` (außerhalb des Repos) | Gebäude für 3D je dzielnica mit Höhe und Herkunft | BDOT10k, GUGiK LoD2 (Freigabe wörtlich), Aufteilung ODbL 1.0 |
