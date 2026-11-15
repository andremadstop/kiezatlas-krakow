# New city (short version)

How to move the Kiezatlas recipe to another city in Poland or the EU. Full Polish version: [`nowe-miasto.md`](nowe-miasto.md).

As of 14 November 2026 the same code runs for two cities: Kraków (`config/krakow.yaml`) and Potsdam
(`pruefen/gegenprobe_potsdam/ort.yaml`, cross-check `pruefen/gegenprobe_potsdam.sh`, last result 0 deviations, see
[`rundgang.md`](rundgang.md)). Kraków is not fully parameterised yet: some paths and codes are written into the
scripts.

## What depends on the city

| Layer | Where | Configuration or code |
|---|---|---|
| Name, languages, address, computing CRS, map, districts, topics, pages, navigation | `config/<city>.yaml` (variable `KIEZ_CONFIG`) | configuration |
| Thresholds, radii, timetable reference day, GTFS and BDOT10k paths | `config/richtwerte.yaml` | configuration |
| County code (TERYT `1261`), OSM level of the districts (`admin_level` 9) | `skripte/raum_bevoelkerung.py` (`TERYT_POWIAT`, `OSM_EBENE`) | code |
| Raw-data paths (`2026-11-13/03_gebaeude/1261_SHP.zip`, `eingang/lod2_1261*` …) | script headers in `skripte/`, list in `skripte/kette.py` | code (14 computing scripts name `1261`) |
| SHA256 of BDOT10k and of the map fonts | `skripte/27_grundkarte.py` (`BDOT_SHA256`, `SCHRIFTEN`) | code |
| Page texts | `texte/<lang>/*.js`, `texte/<lang>/bloecke/quelle/` | content |
| Sources and licences | `QUELLEN.md`, `daten/LIZENZ.md`, `daten/pobierz/licencje.csv` | documentation and code |
| Database tables | `sql/*.sql`; SRID = `rechen_srid` (checked by `pruefen/geruest.py`) | code |

## Kraków and Potsdam

| Key | Kraków | Potsdam |
|---|---|---|
| `sprachen` | `[pl, en, de]` | `[de]` |
| `rechen_srid` | `2178` (ETRS89 / Poland CS2000 zone 7) | `25833` (ETRS89 / UTM zone 33N) |
| `karte.grundkarte` | own vector tiles from BDOT10k | basemap.de raster tiles (BKG service) |
| `karte.luftbild` | `null` (GUGiK orthophoto: tile harvesting not allowed) | Brandenburg DOP20 WMS |
| `gliederung` | 18 dzielnice in four historic boroughs, list `teile` | districts from the data, eight boroughs, `teile: []` |
| `themen` | population and age shares from the Eurostat 1 km grid 2021 | Zensus 2022 (100 m grid): age, buildings, heating |

## Steps for a Polish city

1. Copy `config/krakow.yaml` to `config/<city>.yaml`, set `KIEZ_CONFIG`.
2. `rechen_srid`: PL-2000 zone of the city; the code must be in `SRS_NAMEN` (`skripte/ort_konfig.py`) and in
   `sql/*.sql`.
3. `karte`, `gliederung.teile` (with `OSM_EBENE` for the OSM boundary level).
4. TERYT county code in `skripte/raum_bevoelkerung.py` and the raw-data paths (`grep -n 1261 skripte/*.py`).
5. Data: BDOT10k and LoD2 for the county, Eurostat grid, NSP 2021, the operator’s GTFS (check the licence first),
   OSM extract of the voivodeship; each source with licence and verbatim notice in `QUELLEN.md` before use.
6. Review texts for Kraków-specific names and sentences (`grep -rn Krak texte/`).
7. `./atlas.sh trocken`, `./atlas.sh alles`, `./pruefen.sh` green, new state under `belege/`.

## Another EU country

The Eurostat 1 km grid 2021 and OpenStreetMap cover the whole EU; everything computed from them (density, age shares,
walking distances, two-city comparison) moves with configuration only. BDOT10k, GUGiK LoD2, NSP and the price
register are Polish: another country needs its own readers (example: Potsdam with ALKIS buildings and basemap.de).

## Still missing

Paths and the county code live in the scripts, not in the configuration; the `quellen` section of
`config/krakow.yaml` is empty (scripts read `$KIEZ_DATEN` directly); `package.json` still carries the Kiezatlas
Potsdam name and description (same packages, `npm ci` works).
