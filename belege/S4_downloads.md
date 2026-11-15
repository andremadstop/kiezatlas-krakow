# Beleg: Downloads (GeoPackage, CSV, QGIS-Projekt, Liesmich)

Erzeugt von `skripte/16_export_krakow.py` aus den Datendateien unter `daten/` (Stand der Daten: 13.11.2026, jüngstes
Datum in den Stand-Feldern der exportierten Dateien), Ziel `daten/pobierz/`. Regeln vorab: `pruefen/S4_protokoll.md`
(Commit `b20d6ba`, vor dem ersten Lauf). Prüfung: `pruefen/S4_export.py`. Kein Netz, keine Datenbank.

## Was nicht im Export ist

- `daten/denkmale.js`, `daten/mieszkania.js`, `daten/powietrze.js`: Beispieldaten (`fixture: true`); das Skript
  bricht ab, wenn eine Ebene aus ihnen gebaut würde, und das Liesmich nennt sie.
- `daten/kennzahlen_odbl.*`: dieselben Einwohnerwerte wie `steckbrief_dzielnice_odbl.js` (Ebene `dzielnice`); nicht
  doppelt exportiert.
- `daten/grundkarte.js`, `daten/ort.js`: Stil und Ortskonfiguration, keine Daten.
- Texte der Versorgungswerte (`zaehler_text`, `nenner_text`, `unsicherheit`, deutsch in den Daten): in der Ebene
  `dostepnosc` nur die Felder mit Zahl, Art, Methode, Richtwert und Status.
- Die 3D-Gebäudedateien (außerhalb des Repos).

## Ebenen

Zeilen und Spalten abgelesen aus den GeoPackages (alle Tabellen aus `gpkg_contents`, Spalten ohne `fid` und `geom`, Zeilen mit `count(*)`); Lizenz der Datei laut Tabelle `licencje` (alle Werte von `licencja_pliku` der Ebene). Neu abgelesen am 14.11.2026 nach dem Ergänzen der Quellenzeilen (cee1ef5); seitdem auch mit den Tabellen `pola`, `wartosci` und `layer_styles`, die vorher fehlten.

| Datei | Ebene | Geometrie | Zeilen | Spalten | Lizenz der Datei |
|---|---|---|---:|---:|---|
| `kiezatlas_krakow.gpkg` | `bdot_kamienica_nazwa` | POINT | 28 | 4 | bez licencji (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), z podaniem źródła |
| `kiezatlas_krakow.gpkg` | `bdot_kompleksy` | POLYGON | 59 | 3 | bez licencji (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), z podaniem źródła |
| `kiezatlas_krakow.gpkg` | `delegatury` | - | 4 | 109 | kopiowanie dozwolone z podaniem źródła (warunki GUS); CC BY 4.0; bez licencji (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), z podaniem źródła |
| `kiezatlas_krakow.gpkg` | `layer_styles` | - | 6 | 13 | - |
| `kiezatlas_krakow.gpkg` | `licencje` | - | 24 | 6 | - |
| `kiezatlas_krakow.gpkg` | `miasto` | - | 1 | 106 | kopiowanie dozwolone z podaniem źródła (warunki GUS); CC BY 4.0; bez licencji (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), z podaniem źródła |
| `kiezatlas_krakow.gpkg` | `placowki_bdot` | POINT | 321 | 10 | bez licencji (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), z podaniem źródła |
| `kiezatlas_krakow.gpkg` | `pola` | - | 301 | 5 | - |
| `kiezatlas_krakow.gpkg` | `przystanki` | POINT | 944 | 6 | CC BY 4.0; bez licencji (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), z podaniem źródła |
| `kiezatlas_krakow.gpkg` | `siatka_1km` | POLYGON | 327 | 11 | CC BY 4.0; bez licencji (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), z podaniem źródła |
| `kiezatlas_krakow.gpkg` | `siatka_1km_pokrycie` | POLYGON | 397 | 22 | bez licencji (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), z podaniem źródła |
| `kiezatlas_krakow.gpkg` | `wartosci` | - | 27 | 6 | - |
| `kiezatlas_krakow.gpkg` | `zbk_wykaz_dzielnice` | - | 19 | 15 | ponowne wykorzystywanie informacji sektora publicznego (Gmina Miejska Kraków) |
| `kiezatlas_krakow_odbl.gpkg` | `dostepnosc` | - | 247 | 18 | ODbL 1.0 |
| `kiezatlas_krakow_odbl.gpkg` | `dzielnice` | MULTIPOLYGON | 18 | 89 | ODbL 1.0 |
| `kiezatlas_krakow_odbl.gpkg` | `layer_styles` | - | 5 | 13 | - |
| `kiezatlas_krakow_odbl.gpkg` | `licencje` | - | 23 | 6 | - |
| `kiezatlas_krakow_odbl.gpkg` | `osm_heritage_start_date` | POINT | 906 | 6 | ODbL 1.0 |
| `kiezatlas_krakow_odbl.gpkg` | `placowki_osm` | POINT | 604 | 4 | ODbL 1.0 |
| `kiezatlas_krakow_odbl.gpkg` | `pola` | - | 161 | 5 | - |
| `kiezatlas_krakow_odbl.gpkg` | `siatka_1km_odbl` | POLYGON | 327 | 17 | ODbL 1.0 |
| `kiezatlas_krakow_odbl.gpkg` | `wartosci` | - | 45 | 6 | - |
| `kiezatlas_krakow_odbl.gpkg` | `zbk_budynki` | POINT | 297 | 8 | ODbL 1.0 |
| `kiezatlas_krakow_odbl.gpkg` | `zbk_typologia_dzielnice` | - | 18 | 5 | ODbL 1.0 |

## Prüfungen

- Nachbesserung 14.11.2026: `python -I skripte/16_export_krakow.py --pruefen`: 42 Dateien neu erzeugt, 0 Abweichungen
  (zwei Läufe byte-gleich). `python -I pruefen/S4_export.py`: 4646 ok, 0 Befunde. Neu: `pola.csv` mit 456 Zeilen
  (jede Spalte jeder Ebene, x/y/wkt der CSV und die Spalten von `licencje`), `wartosci.csv` mit 72 Zeilen (jeder Wert der
  Kategorienfelder), `licencje.csv` mit 47 Zeilen (OSM-Anteile je Ebene in einer Zeile mit englischem Vermerk; ergänzt um
  Eurostat bei `dostepnosc` und BDOT10k bei `osm_heritage_start_date` und `przystanki`, die seit dem ersten Lauf fehlten).
- Gegenprobe der neuen Prüfungen mit einer verfälschten Kopie (Erklärung `przystanki.taktklasse` und Wert `II`
  gelöscht, deutscher Text in `pola` pl, deutsche Wörter in `README.md`, „Polen“ in `licencje.csv`): 8 Befunde, jede
  der fünf Verfälschungen gefunden (Zip und CSV-Gleichheit melden zusätzlich).
- Erster Lauf (vor der Nachbesserung): 40 Dateien, 0 Abweichungen; `python -I pruefen/S4_export.py`: 4603 ok, 0 Befunde. Darin unter anderem: Werte der Zellen gleich
  `zellen_odbl.js`, `erreichbar.js` und `erreichbar_fuss_odbl.js`; Summe der Einwohner der Zellen und der dzielnice
  gleich `kennzahlen_odbl.json` (Stadt); Summe der Gebäude der dzielnice gleich Stadt; Summe NSP der delegatury gleich
  Stadt; Fläche jeder dzielnica im Rechensystem gleich `flaeche_km2` (±1 %); jede Zelle rund 100 ha; Lage jedes
  Punkts gleich der Datendatei (≤ 0,01 m); jede Zahl jeder Ebene kommt in ihren Quelldateien vor; CSV gleich
  GeoPackage, `*_pl` mit Dezimalkomma; kein Feld `st`, kein Fußweg und kein OSM-Text in der Datei ohne ODbL; jeder
  Vermerk in `licencje` wörtlich in den Datendateien; keine Adress- oder Kontaktspalte; QGIS-Projekt relativ, ohne
  Orange; Archiv `kiezatlas_krakow_csv.zip` byte-gleich mit den losen Dateien.
- Gegenprobe der Prüfung mit einer verfälschten Kopie (eine Einwohnerzahl +1 im GeoPackage, Feld `st` in
  `przystanki`, Dezimalpunkt in `csv_pl/miasto.csv`, Meldeweg aus `README.md` entfernt): 8 Befunde (die Zip-Prüfung meldet die veränderten losen Dateien zusätzlich), jede Verfälschung
  gefunden, also nicht tautologisch.
- Nachbesserung: `./pruefen.sh` (mit Browser) auf Commit `fae0ace`: 45 Prüfungen, 38 grün, 0 mit Befund, 7 übersprungen.
- `./pruefen.sh` (mit Browser) auf Commit `9d4bebf`: 45 Prüfungen, 38 grün, 0 mit Befund, 7 übersprungen (Prüfungen
  aus Rohdaten und Gegenprobe Potsdam, eigene Läufe). Die Prüfungen dieses Pakets sind noch nicht Teil von
  `pruefen.sh` (Vorschlag in `docs/entscheidungen/S4.md`).

## Grenzen

- Die Ebene `siatka_1km` steht ohne ODbL, weil ihre Werte nicht aus OSM stammen und die Zellen die Zellen mit
  Mittelpunkt in der BDOT10k-Stadtgrenze sind (Lesart wie bei `daten/erreichbar.js` in `daten/LIZENZ.md`). Die
  Lesart ist nicht rechtlich geprüft.
- Die Felder heißen wie in den Datendateien (meist deutsch); ihre Bedeutung steht seit der Nachbesserung auf pl, en und
  de im Liesmich und in `pola.csv`/`wartosci.csv`. Die Erklärungen sind von Hand aus Schemas und Skripten geschrieben,
  nicht von Muttersprachlern gegengelesen.
- Die Downloads liegen unter `daten/` und gehen deshalb mit `skripte/deploy_kopie.py` mit (rund 3 MB).

## Prüfsummen (SHA-256)

    506c35a044a94ff183cd24ddf5a28d94ca80d9e97104be381e957fd1b9d89bea  daten/pobierz/CZYTAJ.md  (48943 Byte)
    f2febf66a4eabe5fe43e9b44ec112d0d83efba42db434a3e97dc5271fda58c3d  daten/pobierz/LIESMICH.md  (47053 Byte)
    194988f8f0ebd88a16817ba668d50300c4582b939ccce12718ff07958f2b09b4  daten/pobierz/README.md  (46349 Byte)
    24d1bfa4aa53c97fc73956cbce1ecf3f32ca989b48abc8f2f7c94e78d4cf9189  daten/pobierz/csv/bdot_kamienica_nazwa.csv  (1444 Byte)
    134aa7fb550c435c0e8b33b16f48c8d97acf9833e318b948a4d99e517cb6ce35  daten/pobierz/csv/bdot_kompleksy.csv  (35200 Byte)
    707e944b7de7915cc89f1fa5e750a02ee45904d3698565d2f1a669163a56f858  daten/pobierz/csv/delegatury.csv  (4478 Byte)
    010d4b98851d0e2b37f6d593e5432813d44415218ca37dfed9bbbd992345dca2  daten/pobierz/csv/miasto.csv  (2638 Byte)
    13ec410a6cebf852f5c234f31fd24f5378414b45eea5112197c7571acb70dd51  daten/pobierz/csv/placowki_bdot.csv  (48859 Byte)
    5a899d14d16199db1f026a97aaac95fa5115adebfee299d4b462c59bd05c1b6b  daten/pobierz/csv/przystanki.csv  (51410 Byte)
    f23cf4c5d60a50d8b30864170d661da722205997928201d885625661d29e0e88  daten/pobierz/csv/siatka_1km.csv  (65780 Byte)
    981973c6c393349ff887f3c3e725400a089edd6f023c354dee7c07edef486a2e  daten/pobierz/csv/siatka_1km_pokrycie.csv  (98104 Byte)
    b8a54cc0bf7effae79a321225bd894dca70cb68a40df0fd0842a6be849f923cb  daten/pobierz/csv/zbk_wykaz_dzielnice.csv  (773 Byte)
    20e55ad9e32b3b5874decf43f4e4544a936ff6cdd3ab6850a432f3d115b546ef  daten/pobierz/csv_odbl/dostepnosc.csv  (33769 Byte)
    100ad6b9efaec4671376b2dc562306c88b250580b67fb3688b1c54978da5aa05  daten/pobierz/csv_odbl/dzielnice.csv  (255162 Byte)
    463db57e534b81a9101a3aabbfb3fc1b3dc39bbe1669816bb648172882647b00  daten/pobierz/csv_odbl/osm_heritage_start_date.csv  (50275 Byte)
    9598f61ada3b42efb620f34fe8d5a44d90fea0b39577e796ad3e0621a2f380c9  daten/pobierz/csv_odbl/placowki_osm.csv  (29762 Byte)
    dfc168e8479bde924778e0581bd1e495a712d1993bcb18e8b7ff97de3b3ef3df  daten/pobierz/csv_odbl/siatka_1km_odbl.csv  (74408 Byte)
    b4055ab23c5bde11e5a6f969ce5e2499f7f7fc238db717c76edee9d238da05c0  daten/pobierz/csv_odbl/zbk_budynki.csv  (20425 Byte)
    149e7834bac6ce1ada9c09a301a3c04b391037abc06b5f23900a57c12a57e6bd  daten/pobierz/csv_odbl/zbk_typologia_dzielnice.csv  (320 Byte)
    96a3c94529fd4ba7088021611450b39e38c3ee1ec671a2e98727510b0075f6a4  daten/pobierz/csv_odbl_pl/dostepnosc.csv  (33769 Byte)
    cfff3760bbf918619ce9364d43a82b012309de85eed84d64370e344cf8093fc0  daten/pobierz/csv_odbl_pl/dzielnice.csv  (255162 Byte)
    ac3d201661475f1013c29e4cbce4e1ed64e603760123cfc5b2064aa836902556  daten/pobierz/csv_odbl_pl/osm_heritage_start_date.csv  (50275 Byte)
    f818e210e9511f205e7464d6ad6aaf4ec86bd46c95ee42aaa292be44c187a53c  daten/pobierz/csv_odbl_pl/placowki_osm.csv  (29762 Byte)
    911cf4aa1c1a581d988bd852e920831d75f9193f4dac5641a3d0c40e979a351f  daten/pobierz/csv_odbl_pl/siatka_1km_odbl.csv  (74408 Byte)
    b8d5d9ea288fe26ba79b37a2ba0a0b3b360d448757928a07bd597934eaca77a3  daten/pobierz/csv_odbl_pl/zbk_budynki.csv  (20425 Byte)
    149e7834bac6ce1ada9c09a301a3c04b391037abc06b5f23900a57c12a57e6bd  daten/pobierz/csv_odbl_pl/zbk_typologia_dzielnice.csv  (320 Byte)
    0eeacf8cc920d7c17b48e76642628745f788f25315dd5c853c48b0b8d7e35b49  daten/pobierz/csv_pl/bdot_kamienica_nazwa.csv  (1444 Byte)
    134aa7fb550c435c0e8b33b16f48c8d97acf9833e318b948a4d99e517cb6ce35  daten/pobierz/csv_pl/bdot_kompleksy.csv  (35200 Byte)
    7ab7ee1e72aa0ec0661208ddd1993e42184cbb0643198aaaa016791684f7010e  daten/pobierz/csv_pl/delegatury.csv  (4478 Byte)
    8d56729cee8d1084d4d57250d152e09f7a5b48bb768595e3bd1a05dd2ac1ca43  daten/pobierz/csv_pl/miasto.csv  (2638 Byte)
    08202d85ffeafefa0b1eb8324be4047659693baf54cd8fb6cc39c77c4eff2139  daten/pobierz/csv_pl/placowki_bdot.csv  (48859 Byte)
    f4c028ff508627b065c262ff534ca4b0f69fb296c3822ec73cfbd77323120bf2  daten/pobierz/csv_pl/przystanki.csv  (51410 Byte)
    cd9196db4fa41210936850133c3a89de10ae5f0dd2c806854f87ae127391c49c  daten/pobierz/csv_pl/siatka_1km.csv  (65780 Byte)
    aaa8034b80ac9b7f585cdf8fc08c5e9a3343653ecec4182de2e2f7775ad6b51d  daten/pobierz/csv_pl/siatka_1km_pokrycie.csv  (98104 Byte)
    b8a54cc0bf7effae79a321225bd894dca70cb68a40df0fd0842a6be849f923cb  daten/pobierz/csv_pl/zbk_wykaz_dzielnice.csv  (773 Byte)
    17cd49df59019b356f9f16027a4f75704b3052c9f75b86fab626f926f10a49ab  daten/pobierz/kiezatlas_krakow.gpkg  (569344 Byte)
    e19301c2c2b035d7a86af5cfcbf0bd4cb18ed5822865b25b5b4cd26170618f98  daten/pobierz/kiezatlas_krakow.qgz  (4081 Byte)
    a3ad5c3a08a6c7790324a2a50b2b93a814f06cdce0a72457e9c64058e8c596b9  daten/pobierz/kiezatlas_krakow_csv.zip  (463852 Byte)
    a3910b2a779b50142fe07f4b804a14d00121a971860467c327e02a4d35957eb2  daten/pobierz/kiezatlas_krakow_odbl.gpkg  (614400 Byte)
    b9959b9a841a7fb6b5d6756eb306058580ba10da900ba7267055a56ec21d7f73  daten/pobierz/licencje.csv  (18382 Byte)
    3c5e134f81cc7227e0a438a3870604c887858f78f050c9a287050bd69e66a3c1  daten/pobierz/pola.csv  (91016 Byte)
    184846b93b2c581ba71c7ea8c3b9f263eb779fb570916397e369c7147289bbb0  daten/pobierz/wartosci.csv  (8934 Byte)
