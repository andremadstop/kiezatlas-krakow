# Quellen des Pakets Gliederung und Bevölkerung

Stand 13.11.2026. Zulieferung für `QUELLEN.md` und `daten/LIZENZ.md` (übernimmt die Belegschicht). Zählungen und
Prüfsummen je Lauf: `belege/D4_bevoelkerung.md` (erzeugt von `skripte/02_bevoelkerung.py`).

## Quellen

| Quelle | Nutzer | Adresse | Lizenz | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| GUS, NSP 2021: „Ludność w rejonach statystycznych i obwodach spisowych według płci, ekonomicznych i 10-letnich grup wieku“ (XLSX) | `skripte/02_bevoelkerung.py` → `daten/steckbrief.js` (Stadt, delegatury) | https://stat.gov.pl/spisy-powszechne/nsp-2021/nsp-2021-wyniki-ostateczne/ludnosc-w-rejonach-statystycznych-i-obwodach-spisowych-wedlug-plci-ekonomicznych-i-10-letnich-grup-wieku,12,1.html | Quellenangabe | „Główny Urząd Statystyczny: nie ma zastrzeżeń co do kopiowania plików i stron oraz dokonywania wydruków, w tym do własnych opracowań, pod warunkiem, że będzie podane ich źródło“ | A (Machbarkeitsprobe) | Stichtag 31.03.2021 aus Vorwissen, nicht geprüft |
| Eurostat, Census 2021 population grid, Polen, 1 km (`PL_PD_3035_GPKG.zip`) | `skripte/02_bevoelkerung.py` → `daten/steckbrief.js`, `daten/steckbrief_dzielnice_odbl.js` | https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/PL_PD_3035_GPKG.zip | CC BY 4.0 (strengste Lesart) | „EU copyright rules apply, while the licence would be under CC-BY 4.0.“ | A (Machbarkeitsprobe) | Datei vom 11.07.2024 laut Machbarkeitsbericht |
| GUGiK, BDOT10k Powiat 1261, Schicht `OT_ADJA_A` (Stadtgrenze und vier delegatury, Geometrie aus PRG) | `skripte/02_bevoelkerung.py` → Flächen und Gitterzuordnung für Stadt und delegatury | https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip | frei, ohne Lizenz (art. 40a ust. 2 pkt 1 lit. h, art. 40c ust. 5 Prawo geodezyjne i kartograficzne), Quellenangabe nach art. 40c ust. 3 | „Baza BDOT10k jest dostępna bezpłatnie i możliwa do dowolnego wykorzystania.“ | A (Machbarkeitsprobe) | Version laut Attribut 20251002000000 (Beleg) |
| OpenStreetMap, Auszug Woiwodschaft Małopolska (Geofabrik `malopolskie`) | `skripte/02_bevoelkerung.py` → Grenzen der 18 dzielnice (admin_level 9) → `daten/steckbrief_dzielnice_odbl.js`; nach der Entscheidung zu KR3 auch `daten/stadtteile_odbl.js`, `zellen.js`, `kennzahlen.*` | https://www.openstreetmap.org/copyright | ODbL 1.0 | „OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF).“ | H (Handdownload durch den Betreiber, 13.11.2026, `eingang/HERKUNFT.md`) | Dateikopf: 2026-11-12T21:23:05Z |
| MSIP Kraków, „Podział administracyjny – dzielnice“ | nur intern: `skripte/02_bevoelkerung.py --msip-gegenprobe` und `--intern-msip ORDNER` (außerhalb des Repos) | https://msip.um.krakow.pl/Dane/Dzielnice_JSON.zip | **STOPP** (widersprüchlich, KR3) | Regulamin 2016 Pkt. 4: „Korzystanie z treści prezentowanych na Portalu MSIP Obserwatorium jest możliwe tylko do celów niezarobkowych i niekomercyjnych.“ | A (Machbarkeitsprobe), nie ausgeliefert | Attribut `data_aktua` 01.04.2014 |

### Fundstellen (lokal, unter `kiezatlas-daten/krakow/2026-11-13/`)

| Vermerk | Datei | SHA256 |
|---|---|---|
| GUS | `02_zensus/gus_copyright.html` (https://stat.gov.pl/copyright), Wortlaut im sichtbaren Text nachgelesen 13.11.2026 | `5eea00a116e88c9b9d9e1b5c567ca7eb98ecffb62d25056b0d0f0a8ccfe2d39e` |
| Eurostat | `02_zensus/eurostat_population_distribution_rules.html` (https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution, Abschnitt „Eurostat census grid 2021“; im Text steht ein Leerzeichen vor dem Punkt) | `5a41852d9774f0db6d350fa57e2bf16968e210f0da41861987fd7fea3b644616` |
| BDOT10k | `03_gebaeude/geoportal_bdot10k.html` (https://www.geoportal.gov.pl/pl/dane/baza-danych-obiektow-topograficznych-bdot10k/) | `58fe5cf154ec9006845bce4d4227513f630022b439643e5113efe114496840e4` |
| OSM | `08_fussweg/osm_copyright.html` (https://www.openstreetmap.org/copyright; Nachweis im Paket OSM und Fußwegnetz) | `226baa199d8471191c56cdbe340ec39ea5b9f4500be61b3e69fdaa387f4bcd07` |

Die Prüfsummen der Rohdateien stehen in `belege/rohdaten-D4-2026-11-13.sha256` (prüft `pruefen.sh`).

## Ausgaben und ihre Lizenz

| Ausgabe | Inhalt | Lizenz |
|---|---|---|
| `daten/steckbrief.js` (Vertrag `daten/schema/steckbrief.json`) | Stadt und vier delegatury: NSP 2021, Gitter, Fläche, Dichte; dzielnice `null` mit Grund | Quellenangaben GUS, Eurostat (CC BY 4.0), GUGiK; keine OSM-Werte |
| `daten/steckbrief_dzielnice_odbl.js` (Vertrag `daten/schema/steckbrief_dzielnice_odbl.json`, `x-odbl`) | je dzielnica: Fläche, Gitter nach Mittelpunkt und Flächenanteil, Spanne, Dichte, OSM-Kennung | ODbL 1.0 für die Datei als Ganzes (strengste Lesart, siehe `docs/entscheidungen/D4.md`), Einwohner zusätzlich Eurostat CC BY 4.0 |
| `daten/stadtteile_odbl.js`, `daten/zellen.js`, `daten/kennzahlen.js`, `daten/kennzahlen.json` | bleiben Beispieldaten (`fixture: true`): `zellen.js` und `kennzahlen.*` bis zur Entscheidung zu KR3, `stadtteile_odbl.js` (lizenzrechtlich eindeutig) nur mit, weil die Prüfungen alle vier gemeinsam als Beispiel- oder als echte Daten verlangen | – |

## Erwartete Handdownloads unter `kiezatlas-daten/krakow/eingang/`

| Datei | Format | Stand | Wer liest |
|---|---|---|---|
| `*.osm.pbf` (genau eine; liegen mehrere da, bricht das Skript ab; jetzt `malopolskie-261112.osm.pbf`) | OSM-PBF, zlib; Grenzrelationen `boundary=administrative`, `admin_level=9`, römische Ziffer in `ref`, `official_name` („dzielnica X Swoszowice“) oder `name` | **da** (13.11.2026) | `skripte/raum_bevoelkerung.py`, `osm_pbf_kandidaten` |
| ersatzweise `osm_dzielnice_krakow.geojson` (hat Vorrang vor der PBF) | GeoJSON FeatureCollection in EPSG:4326, Polygon/MultiPolygon, Tags flach oder verschachtelt (`properties.tags`, Format von osmtogeojson); dieselben Tags wie oben | nicht nötig | `osm_geojson_kandidaten` |
| `rejony_statystyczne.zip` / `.shp` / `.gpkg` / `.geojson` / `.gml` | Geometrie der 748 rejony statystyczne (GUS „Jednostki statystyczne“, Ausgabe 2021); ein Feld, dessen Werte auf die sechsstelligen Kennungen der NSP-Tabelle enden (das Skript sucht es selbst, mindestens 90 % Treffer); Koordinatensystem aus .prj, GeoPackage oder GeoJSON-`crs` | **fehlt**: laut `eingang/HERKUNFT.md` Ausgabe 2021 nicht gefunden, INSPIRE-Feed zeigt Stand 2014, geo.stat.gov.pl antwortet 401 | `rejony_aus_eingang` |

Lizenz der rejony-Geometrie: **nicht geprüft** (Machbarkeitsbericht, Zeile 1b). Bevor NSP-Werte je dzielnica aus
den rejony ausgeliefert werden, muss die Lizenz der gelieferten Datei mit wörtlicher Fundstelle hier stehen; bis
dahin STOPP für diese Quelle, die NSP-Felder je dzielnica bleiben `null` mit Grund.

Nicht gebraucht für dieses Paket: GUS-1-km-Gitter (das Eurostat-Gitter deckt dieselben Zählungen, Lizenz klarer),
LoD1/LoD2, NID, RSPO.

## Nicht genutzt

- Overpass-API: `overpass-api.de` steht in der Sperrliste von `skripte/abruf.py` („OSM nur aus dem Handdownload“);
  kein Abruf, auch nicht über andere Overpass-Rechner. Seit dem Handdownload vom 13.11.2026 nicht mehr nötig.
- Gemeldete Einwohner der Stadt (BIP Kraków): anderes Konzept, Lizenzangabe fehlt.
