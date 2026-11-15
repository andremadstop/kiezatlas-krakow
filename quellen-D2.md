# Quellen des Pakets OSM und Fußwegnetz (Teil Fußweg je Zelle)

Stand 13.11.2026. Zulieferung für `QUELLEN.md` und `daten/LIZENZ.md` (übernimmt die Belegschicht).

## Quellen

| Quelle | Nutzer | Adresse | Lizenz | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| OpenStreetMap, Auszug Woiwodschaft Małopolska (Geofabrik „malopolskie“) | `skripte/12_osm.py` → `auswertung.netz_*`, `osm_poi`; daraus `skripte/14b_fussweg.py` → Fußweg-Zeilen in `auswertung.zelle_erreichbar`, `zelle_gruen`; veröffentlicht nur in `daten/erreichbar_fuss_odbl.js`, `daten/planer_fuss_odbl.js` | https://www.openstreetmap.org/copyright | ODbL 1.0 | „OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF).“ | H (Handdownload durch den Betreiber, noch ausstehend) | Datenstand der PBF, steht nach dem Lauf in `berichte/osm_netz.md` |
| GTFS der ZTP Kraków (Haltestellen als Ziele) | nur der Vermerk in den Fußweg-Zeilen der Art `haltestelle`; geladen werden die Haltestellen im Paket Versorgung und Takt (`skripte/13_oepnv.py`) | https://gtfs.ztp.krakow.pl/ | CC BY 4.0 | „Licencja: Creative Commons (CC BY 4.0)“ | A (Paket Versorgung und Takt) | wie dort |

### Fundstellen

- OSM: Seite https://www.openstreetmap.org/copyright, abgerufen 2026-11-13T09:39:21Z über das Abrufskript der
  Machbarkeitsprobe (robots.txt ausgewertet, Status 200), Datei
  `kiezatlas-daten/krakow/2026-11-13/08_fussweg/osm_copyright.html`, SHA256
  `226baa199d8471191c56cdbe340ec39ea5b9f4500be61b3e69fdaa387f4bcd07` (nachgerechnet 13.11.2026; der Vermerk steht so im
  sichtbaren Text, im HTML ist „open data“ kursiv ausgezeichnet). Auf derselben
  Seite wörtlich zur Namensnennung: „Where you use OpenStreetMap data, you are required to do the following two things:
  Provide credit to OpenStreetMap by displaying our attribution notice. Make clear that the data is available under
  the Open Database License.“ Daraus der Vermerk in jeder Fußweg-Zeile: „ODbL 1.0, © OpenStreetMap-Mitwirkende
  (https://opendatacommons.org/licenses/odbl/1-0/)“.
- ZTP: Indexseite `kiezatlas-daten/krakow/2026-11-13/06_oepnv/gtfs_index.html` (Lizenz-Nachtrag in der
  `HERKUNFT.md` dort). Vermerk in den Fußweg-Zeilen: „ZTP Kraków (Zarząd Transportu Publicznego), GTFS, CC BY 4.0
  (https://creativecommons.org/licenses/by/4.0/), Daten verändert (eigene Berechnung)“.
- Zellen: Der Vermerk der Zellen wird nicht hier festgelegt, sondern aus dem Tabellenkommentar der Zelltabelle
  gelesen (Paket Gliederung und Bevölkerung). Ohne Kommentar rechnet das Skript nicht.

## Ausgaben und ihre Lizenz

| Ausgabe | Lizenz |
|---|---|
| Fußweg-Zeilen in `auswertung.zelle_erreichbar` und `auswertung.zelle_gruen` (`methode = 'fussweg'`) | ODbL 1.0 (CHECK in `sql/002_ausbau.sql`); dazu die Lizenzen der Ziele und der Zellen, je Zeile in `quelle_lizenz` |
| `daten/erreichbar_fuss_odbl.js`, `daten/planer_fuss_odbl.js` (erzeugt im Paket Versorgung und Takt) | ODbL 1.0; Verträge `daten/schema/*_fuss_odbl.json` mit `x-odbl: true` |
| `berichte/fussweg.md` (nicht im Repo) | ODbL 1.0 für die Kennzahlen |

## Erwartete Handdownloads

| Datei | Ablage | Format | Wer liest |
|---|---|---|---|
| `malopolskie-latest.osm.pbf` (Geofabrik), dazu `malopolskie-latest.osm.pbf.md5`, wenn vorhanden | Der Betreiber legt sie nach `kiezatlas-daten/krakow/eingang/`. `skripte/12_osm.sh laden --pbf $KIEZ_DATEN/eingang/malopolskie-latest.osm.pbf --uebernehmen` kopiert sie (und die `.md5`) nach `kiezatlas-daten/krakow/osm/<stand>/` (stand = Datenstand aus dem Dateikopf, JJJJ-MM-TT; fehlt er, `--stand`), legt dort `HERKUNFT.md` mit der SHA256 an und rechnet auf der Kopie; der Eingang bleibt unverändert. Ohne `--uebernehmen` läuft aus `eingang/` nur `--trockenlauf`. Ein BBBike-Auszug (Machbarkeitsbericht, offene Handdownloads Nr. 5: „Geofabrik oder BBBike“) geht mit seinem eigenen Dateinamen genauso; der Name ist frei (das Skript liest den Dateikopf, nicht den Namen). | OSM-PBF (Protocol Buffers), Größe nicht geprüft | `skripte/12_osm.sh laden --pbf …` |

`skripte/14b_fussweg.py` liest keine Datei aus `eingang/`: Es rechnet nur auf der Datenbank (Netz aus
`skripte/12_osm.py`, Zellen aus dem Paket Gliederung und Bevölkerung, Ziele aus dem Paket Versorgung und Takt).

## Nicht genutzt

- Overpass-API: `overpass-api.de` steht in der Sperrliste von `skripte/abruf.py` („OSM nur aus dem Handdownload“);
  kein Abruf.
- Geofabrik und BBBike automatisch: ebenso gesperrt, nur Handdownload.
