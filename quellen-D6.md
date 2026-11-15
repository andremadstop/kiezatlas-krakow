# Quellen des Pakets Versorgung und Takt

Stand 13.11.2026. Zulieferung für `QUELLEN.md` und `daten/LIZENZ.md` (übernimmt die Belegschicht). Prüfsummen der
Rohdaten: `belege/rohdaten-D6-2026-11-13.sha256` (von `pruefen.sh` gegen `$KIEZ_DATEN` geprüft).

## Quellen

| Quelle | Nutzer | Adresse | Lizenz | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| GTFS der ZTP Kraków: Bus (`GTFS_KRK_A`), Tram (`GTFS_KRK_T`), Mobilis (`GTFS_KRK_M`) | `skripte/13_oepnv_krakow.py` → `daten/haltestellen.js`; Ziel `haltestelle_takt` in `14_`, `15_` | https://gtfs.ztp.krakow.pl/ | CC BY 4.0 | „Licencja: Creative Commons (CC BY 4.0)“ | A (Machbarkeitsprobe, `2026-11-13/06_oepnv/`) | Abruf 13.11.2026, `feed_version` Bus 20261109_20261114 |
| BDOT10k Powiat 1261 (Kraków), Ebenen `OT_KUOS_A`, `OT_KUOZ_A`, `OT_KUSK_A`, `OT_ADJA_A` | `skripte/11_einrichtungen_krakow.py` → `daten/einrichtungen.js`; Gemeindegrenze in `13_`; Parkflächen in `15_` | https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip | frei, mit Quellenangabe | „Baza BDOT10k jest dostępna bezpłatnie i możliwa do dowolnego wykorzystania.“ | A (Machbarkeitsprobe, `2026-11-13/03_gebaeude/`) | Abruf 13.11.2026 |
| Prawo oświatowe, tekst jednolity Dz.U. 2026 poz. 820 | Bildungsradien in `config/richtwerte.yaml` (`bildung`), Richtwerte in `daten/planer.js` | https://api.sejm.gov.pl/eli/acts/DU/2026/820/text.pdf | amtlicher Text (art. 4 pkt 2 ustawy o prawie autorskim) | – | A (`skripte/abruf.py`, `d6_recht/2026-11-13/`) | Abruf 13.11.2026 |
| OpenStreetMap (Ärzte, Apotheken) über `auswertung.osm_poi` | `11_einrichtungen_krakow.py --osm-db` → `daten/einrichtungen_odbl.js` | https://www.openstreetmap.org/copyright | ODbL 1.0 | „OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF).“ | über das Paket OSM und Fußwegnetz (Handdownload liegt seit 13.11.2026 17:15 vor: `eingang/malopolskie-261112.osm.pbf`, mit `eingang/HERKUNFT.md` und `SHA256SUMS`; Laden nach `auswertung.osm_poi` steht beim Paket OSM und Fußwegnetz aus) | noch keine Daten in `auswertung.osm_poi`: Beispieldatei |
| RSPO (Rejestr Szkół i Placówek Oświatowych) | vorgesehen in `11_einrichtungen_krakow.py` | https://rspo.gov.pl/ | **nicht geprüft** | – | H (Handdownload durch den Betreiber, ausstehend) | STOPP bis Lizenz geprüft |

### Fundstellen (wörtlich)

- **GTFS ZTP:** Indexseite https://gtfs.ztp.krakow.pl/, Abzug `2026-11-13/06_oepnv/gtfs_index.html`
  (SHA256 in `belege/rohdaten-D6-2026-11-13.sha256`): „Licencja: Creative Commons (CC BY 4.0)“. Vermerk in den
  Daten: „ZTP Kraków, GTFS, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), dane zmienione (opracowanie
  własne)“.
- **BDOT10k:** Geoportal, Abzug `2026-11-13/03_gebaeude/geoportal_bdot10k.html`: „Baza BDOT10k jest dostępna
  bezpłatnie i możliwa do dowolnego wykorzystania.“ Pflicht zur Quellenangabe: art. 40c ust. 3 Prawo geodezyjne i
  kartograficzne (Dz.U. 2026 poz. 1389, Abzug `2026-11-13/03_gebaeude/pgik_DU_2026_1389.pdf`): „Podmioty, które
  wykorzystują materiały zasobu, zamieszczają w publikowanych opracowaniach informacje o źródle pochodzenia użytego
  materiału.“ Vermerk in den Daten: „Źródło: Główny Urząd Geodezji i Kartografii, BDOT10k (PZGiK), dane zmienione
  (opracowanie własne)“.
- **Prawo oświatowe** (`d6_recht/2026-11-13/prawo_oswiatowe_DU_2026_820.pdf`, am 13.11.2026 mit `pdftotext`
  nachgelesen):
  - art. 39 ust. 2 (Abzug s. 40, Seitenkopf „– 40 –“): „Droga dziecka z domu do szkoły nie może przekraczać: 1) 3 km – w przypadku uczniów klas I–IV
    szkół podstawowych; 2) 4 km – w przypadku uczniów klas V–VIII szkół podstawowych.“
  - art. 32 ust. 3 (Abzug s. 36, Seitenkopf „– 36 –“; der Satz ist der zweite des Absatzes 3): „Droga dziecka spełniającego obowiązek, o którym mowa w art. 31 ust. 4, i dziecka pięcioletniego
    z domu do publicznego przedszkola, […] nie powinna przekraczać 3 km.“
  - Lesart: Das Gesetz meint den **Weg** (droga) zur Schule des eigenen Schulbezirks. Gerechnet wird die Luftlinie
    zur nächsten Einrichtung jeder Art. Deshalb steht jeder dieser Werte als Orientierung und vorläufig da, nie als
    „standard urzędowy“.
  - Seitenzahlen: Bis Commit 30d4bfa standen in `config/richtwerte.yaml`, `daten/planer.js` und
    `belege/D6_planer.md` s. 41 und s. 37, beide eine Seite zu spät (Fund der Nachprüfung; berichtigt in `4fda5ff`). `pruefen/D6_versorgung.py` (Schritt 7) liest jede Fundstelle seitdem im
    gehashten Abzug auf der genannten Seite nach.
- **OSM:** wie `quellen-D2.md` (Abzug `2026-11-13/08_fussweg/osm_copyright.html`).
- **Taktklassen:** keine polnische Fundstelle. Die Grenzen 6, 2 und 1 Abfahrten je Stunde und Richtung sind das Muster
  des Kiezatlas Potsdam (dort Nahverkehrsplan Potsdam 2019). Ein Krakauer Gegenstück (Plan zrównoważonego rozwoju
  publicznego transportu zbiorowego) wurde nicht gesucht.

## Handdownloads: erwartete Dateien unter `$KIEZ_DATEN/eingang/`

| Datei | Inhalt | Format | Was das Skript dann tut |
|---|---|---|---|
| `rspo_krakow.csv` | RSPO-Export der Schulen und Kindergärten mit Sitz in der Gemeinde Kraków (TERYT 1261011) | CSV, UTF-8, eine Kopfzeile; je Einrichtung mindestens RSPO-Nummer, Typ (z. B. „Szkoła podstawowa“, „Przedszkole“), Name, Breite und Länge (WGS 84) oder Adresse, Status (aktiv/zlikwidowana) | Erst wenn in `config/richtwerte.yaml` `einrichtungen.rspo.lizenz_geprueft: true` steht und `einrichtungen.rspo.spalten` die Spalten zuordnet. Bis dahin meldet `11_einrichtungen_krakow.py` im Beleg „STOPP“. Die Spaltennamen des Browser-Exports sind nicht geprüft, deshalb steht noch kein Leser im Skript (der Aufruf bricht mit Hinweis ab, statt zu raten). |
| OSM-Auszug Małopolska (liegt vor: `malopolskie-261112.osm.pbf`, 13.11.2026) | Fußwegnetz und Ärzte/Apotheken | `.osm.pbf` | Liest das Paket OSM und Fußwegnetz (`skripte/12_osm.py`) in `auswertung.osm_poi` und `auswertung.netz_*`. Danach `11_einrichtungen_krakow.py --osm-db` mit der Leserolle. Den Fußweg je Zelle rechnet `14b_fussweg.py` (Paket OSM und Fußwegnetz). |

Die übrigen Handdownloads (rejony-Geometrie GUS, 1-km-Gitter, LoD1/LoD2, NID) liest dieses Paket nicht. Mit dem
1-km-Gitter des Pakets Gliederung und Bevölkerung werden `daten/zellen.js` und damit `erreichbar.js` und `planer.js`
echt. Dann reicht für `erreichbar.js` ein Neulauf von `14_`; die Skripte nehmen `fixture` selbst heraus. Für
`planer.js` (Kennzahlen je dzielnica über `st` der Zelle) und `st` in `haltestellen.js` muss vorher die
KR3-Folgefrage geklärt sein (ODbL für Werte aus OSM-Grenzen; `docs/entscheidungen/D6.md`), sonst meldet
`pruefen/D6_versorgung.py` einen Befund.

## Ausgaben und ihre Lizenz

| Datei | Lizenz der Daten | Vermerk |
|---|---|---|
| `daten/haltestellen.js` | CC BY 4.0 (ZTP), Gemeindegrenze BDOT10k | ZTP-Vermerk und „Gemeindegrenze: Główny Urząd Geodezji i Kartografii, BDOT10k“ im Kopf |
| `daten/einrichtungen.js` | BDOT10k (frei, Quellenangabe) | BDOT10k-Vermerk in `quellen` |
| `daten/einrichtungen_odbl.js` | ODbL 1.0 (derzeit Beispieldaten) | ODbL-Vermerk im Kopf |
| `daten/erreichbar.js`, `daten/planer.js` | abgeleitet aus BDOT10k, ZTP und den Zellen | Vermerke in `quellen`; keine OSM-Daten, keine Stadtteilgeometrie; ob `st` der Zelle ODbL-abgeleitet ist, ist offen (KR3) |
