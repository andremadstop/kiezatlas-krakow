# Kiezatlas Kraków: downloads

Data state: built from the atlas data files (`daten/` folder), latest date in the data: 2026-11-14. Script: `skripte/16_export_krakow.py`.

## Files

- `kiezatlas_krakow.gpkg`: GeoPackage without OpenStreetMap data. Source licences in the table `licencje`.
- `kiezatlas_krakow_odbl.gpkg`: GeoPackage with OpenStreetMap data and everything assigned to districts via the OSM boundaries. Whole file: Open Database License 1.0, © OpenStreetMap contributors (https://opendatacommons.org/licenses/odbl/1-0/).
- `csv/`, `csv_odbl/`: The same layers as CSV (UTF-8 with BOM, semicolon separator, decimal point).
- `csv_pl/`, `csv_odbl_pl/`: The same with a **decimal comma** and no thousands separator, for Polish-locale Excel and LibreOffice.
- `kiezatlas_krakow.qgz`: QGIS project (relative paths; keep both GeoPackage files in the same folder).
- `licencje.csv`: Licence and verbatim source notice for every layer.
- `pola.csv`, `wartosci.csv`: Meaning of every field (`pola.csv`) and every coded value (`wartosci.csv`) in Polish, English and German; also as the tables `pola` and `wartosci` in both GeoPackages.
- `kiezatlas_krakow_csv.zip`: All CSV files with `licencje.csv`, `pola.csv`, `wartosci.csv` and the read-me files in one archive.

## Layers

| Layer | File | Geometry | Rows | From atlas files |
|---|---|---|---:|---|
| `miasto`: Kraków: city-wide figures | `kiezatlas_krakow.gpkg` | none | 1 | `steckbrief`, `gebaeude_kennzahlen`, `klimat`, `sanierung` |
| `delegatury`: Four delegatury (historic boroughs) | `kiezatlas_krakow.gpkg` | none | 4 | `steckbrief`, `gebaeude_kennzahlen`, `klimat`, `sanierung`, `denkmale_bdot` |
| `siatka_1km`: 1 km grid: population and straight-line distances | `kiezatlas_krakow.gpkg` | polygon | 327 | `zellen_odbl`, `erreichbar` |
| `siatka_1km_pokrycie`: 1 km grid: land cover | `kiezatlas_krakow.gpkg` | polygon | 397 | `klimat_zellen` |
| `rejony_statystyczne`: Statistical areas: population from NSP 2021 | `kiezatlas_krakow.gpkg` | multipolygon | 749 | `rejony` |
| `placowki_bdot`: Facilities from BDOT10k | `kiezatlas_krakow.gpkg` | point | 321 | `einrichtungen` |
| `przystanki`: Stops with frequency class | `kiezatlas_krakow.gpkg` | point | 944 | `haltestellen` |
| `bdot_kompleksy`: BDOT10k complexes (museums, forts, building ensembles) | `kiezatlas_krakow.gpkg` | polygon | 59 | `denkmale_bdot` |
| `bdot_kamienica_nazwa`: Buildings named “Kamienica …” in BDOT10k | `kiezatlas_krakow.gpkg` | point | 28 | `denkmale_bdot` |
| `rejestr_zabytkow`: Heritage register points from Wikidata: objects with the same register number as one point (location checked on a sample) | `kiezatlas_krakow.gpkg` | point | 1214 | `denkmale` |
| `zbk_wykaz_dzielnice`: ZBK list: counts by district as listed | `kiezatlas_krakow.gpkg` | none | 19 | `sanierung` |
| `dzielnice`: 18 districts: boundaries and indicators | `kiezatlas_krakow_odbl.gpkg` | multipolygon | 18 | `stadtteile_odbl`, `steckbrief_dzielnice_odbl`, `gebaeude_dzielnice_odbl`, `klimat_stadtteile_odbl` |
| `siatka_1km_odbl`: 1 km grid with district and walking distance | `kiezatlas_krakow_odbl.gpkg` | polygon | 327 | `zellen_odbl`, `erreichbar_fuss_odbl` |
| `dostepnosc`: Access to facilities by district | `kiezatlas_krakow_odbl.gpkg` | none | 247 | `planer_odbl`, `planer_fuss_odbl` |
| `placowki_osm`: Doctors and pharmacies from OpenStreetMap | `kiezatlas_krakow_odbl.gpkg` | point | 604 | `einrichtungen_odbl` |
| `osm_heritage_start_date`: OSM objects with heritage or start_date (location of heritage objects checked on a sample) | `kiezatlas_krakow_odbl.gpkg` | point | 929 | `denkmale_odbl` |
| `zbk_budynki`: ZBK buildings in public ownership (location) | `kiezatlas_krakow_odbl.gpkg` | point | 126 | `sanierung_odbl` |
| `zbk_typologia_dzielnice`: Block typology by district (estimate) | `kiezatlas_krakow_odbl.gpkg` | none | 18 | `sanierung_odbl` |

The layer `siatka_1km` takes from `zellen_odbl` only population and age shares (Eurostat), without the district assignment (`st`); the cell geometry is built from its Eurostat grid code. The cells are those whose centre lies within the city boundary from BDOT10k, so the layer holds no OpenStreetMap data.

Coordinate reference system: ETRS89 / Poland CS2000 zone 7 (EPSG:2178). Coordinates rounded to 0.01 m; geometries are not simplified. Field names are those of the atlas files (partly German abbreviations); their meaning is given in the sections below and in `pola.csv` and `wartosci.csv`. Logical values in the CSV: 1 = yes, 0 = no; an empty field means no data.

## Not in the export

No atlas file holds sample data any more.

Not yet a layer of their own in the export (real data, only as atlas files in the `daten/` folder):

- housing market: `mieszkania_odbl.js`
- air quality: `powietrze.js`

## Limits

- No construction years and no heating data: the year of construction in the cadastre is paid, the CEEB register is not open. A construction period (`ep`) exists only for single objects: with a `start_date` tag in OSM (layer `osm_heritage_start_date`) and with an inception date in Wikidata (layer `rejestr_zabytkow`), unchecked and never for areas.
- Population comes from the Eurostat grid (Eurostat, Census 2021 population grid, file PL_PD_3035_GPKG.zip); district values add up cells by their centre and are approximate at the boundaries.
- The block typology (`typ_*`) is an estimate from BDOT10k (storeys, footprint, rectangularity), not a register of prefabricated buildings.
- Distances are straight-line or walking distances from the centre of a 1 km cell to the nearest facility; orientation, not an official value.
- The location was checked on the orthophoto only for a random sample (2026-11-15): register points (Wikidata) 17 of 20 on the object (85%, 95% Wilson interval 64%–95%), OSM objects with `heritage` 16 of 20 (80%, 58%–92%); “just beside” does not count as “on the object”. This is a result for the layer, not for the point: `polozenie_sprawdzone` = 0 at every point. The assignment to a building has not been checked.

## Field meanings

### `miasto`

| Field | Meaning |
|---|---|
| `teryt` | TERYT code |
| `nazwa` | name (Polish proper name) |
| `flaeche_km2` | area, km² |
| `flaeche_quelle` | source of the area |
| `nsp_einwohner` | NSP 2021: residents |
| `nsp_maenner` | NSP 2021: men |
| `nsp_frauen` | NSP 2021: women |
| `nsp_alter_10_a0_9` | NSP 2021: residents aged 0–9 |
| `nsp_alter_10_a10_19` | NSP 2021: residents aged 10–19 |
| `nsp_alter_10_a20_29` | NSP 2021: residents aged 20–29 |
| `nsp_alter_10_a30_39` | NSP 2021: residents aged 30–39 |
| `nsp_alter_10_a40_49` | NSP 2021: residents aged 40–49 |
| `nsp_alter_10_a50_59` | NSP 2021: residents aged 50–59 |
| `nsp_alter_10_a60_69` | NSP 2021: residents aged 60–69 |
| `nsp_alter_10_a70_79` | NSP 2021: residents aged 70–79 |
| `nsp_alter_10_a80p` | NSP 2021: residents aged 80 and over |
| `nsp_oekonomisch_vor` | NSP 2021: residents of pre-working age |
| `nsp_oekonomisch_erwerb` | NSP 2021: residents of working age |
| `nsp_oekonomisch_nach` | NSP 2021: residents of post-working age |
| `nsp_q_u20` | NSP 2021: share of residents under 20, % |
| `nsp_q_60p` | NSP 2021: share of residents aged 60 and over, % |
| `nsp_q_nach` | NSP 2021: share of residents of post-working age, % |
| `nsp_rejony` | NSP 2021: number of statistical areas (rejony statystyczne) |
| `nsp_weg` | where the NSP 2021 values come from |
| `gitter_zellen` | Eurostat grid: number of 1 km cells whose centre lies in the unit |
| `gitter_einwohner` | Eurostat grid: residents (sum of cells by their centre) |
| `gitter_u15` | Eurostat grid: residents under 15 |
| `gitter_a15_64` | Eurostat grid: residents aged 15–64 |
| `gitter_a65p` | Eurostat grid: residents aged 65 and over |
| `gitter_a_ges` | Eurostat grid: sum of the three age groups (may differ slightly from the residents) |
| `gitter_q_u15` | Eurostat grid: share under 15 in the sum of age groups, % |
| `gitter_q_65p` | Eurostat grid: share aged 65 and over in the sum of age groups, % |
| `gitter_einwohner_flaechenanteil` | Eurostat grid: residents by the area share of cells in the unit (comparison) |
| `gitter_abweichung_nsp_proz` | difference of grid residents from NSP 2021, %; empty without NSP |
| `dichte_nsp` | population density from NSP 2021, residents per km² |
| `dichte_gitter` | population density from the Eurostat grid, residents per km² |
| `geb_anzahl` | BDOT10k: buildings (OT_BUBD_A) with their inner point in the unit, all statuses |
| `geb_zustand_eksploatowany` | BDOT10k: buildings with status: in use (eksploatowany) |
| `geb_zustand_w_budowie` | BDOT10k: buildings with status: under construction (w budowie) |
| `geb_zustand_nieczynny` | BDOT10k: buildings with status: disused (nieczynny) |
| `geb_zustand_zniszczony` | BDOT10k: buildings with status: destroyed (zniszczony) |
| `geb_zustand_leer` | BDOT10k: buildings with status: no value |
| `geb_funktion_101` | BDOT10k: buildings with KŚT code 101: industrial buildings |
| `geb_funktion_102` | BDOT10k: buildings with KŚT code 102: transport and communication buildings |
| `geb_funktion_103` | BDOT10k: buildings with KŚT code 103: retail and service buildings |
| `geb_funktion_104` | BDOT10k: buildings with KŚT code 104: tanks, silos and warehouses |
| `geb_funktion_105` | BDOT10k: buildings with KŚT code 105: office buildings |
| `geb_funktion_106` | BDOT10k: buildings with KŚT code 106: hospitals and other healthcare buildings |
| `geb_funktion_107` | BDOT10k: buildings with KŚT code 107: education, science, culture and sports buildings |
| `geb_funktion_108` | BDOT10k: buildings with KŚT code 108: agricultural buildings (production, service, utility) |
| `geb_funktion_109` | BDOT10k: buildings with KŚT code 109: other non-residential buildings |
| `geb_funktion_110` | BDOT10k: buildings with KŚT code 110: residential buildings |
| `geb_funktion_unbekannt` | BDOT10k: buildings without a KŚT code |
| `geb_wohngebaeude` | BDOT10k: residential buildings (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: single-family residential buildings (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: multi-family residential buildings (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: other residential buildings (PFBUD) |
| `geb_geschosse_1` | BDOT10k: buildings: 1 storey |
| `geb_geschosse_2` | BDOT10k: buildings: 2 storeys |
| `geb_geschosse_3_4` | BDOT10k: buildings: 3–4 storeys |
| `geb_geschosse_5_10` | BDOT10k: buildings: 5–10 storeys |
| `geb_geschosse_11p` | BDOT10k: buildings: 11 or more storeys |
| `geb_geschosse_unbekannt` | BDOT10k: buildings: number of storeys unknown |
| `geb_geschosse_wohn_1` | BDOT10k: residential buildings: 1 storey |
| `geb_geschosse_wohn_2` | BDOT10k: residential buildings: 2 storeys |
| `geb_geschosse_wohn_3_4` | BDOT10k: residential buildings: 3–4 storeys |
| `geb_geschosse_wohn_5_10` | BDOT10k: residential buildings: 5–10 storeys |
| `geb_geschosse_wohn_11p` | BDOT10k: residential buildings: 11 or more storeys |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: residential buildings: number of storeys unknown |
| `geb_geschosse_median` | BDOT10k: median number of storeys above ground; empty below 30 buildings with known storeys |
| `geb_geschosse_mittel` | BDOT10k: mean number of storeys above ground; empty below 30 buildings with known storeys |
| `geb_geschosse_median_wohn` | BDOT10k: median number of storeys above ground of residential buildings; empty below 30 buildings with known storeys |
| `geb_geschosse_mittel_wohn` | BDOT10k: mean number of storeys above ground of residential buildings; empty below 30 buildings with known storeys |
| `geb_grundflaeche_m2` | BDOT10k: total building footprint without destroyed buildings, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: total footprint of residential buildings, m² |
| `geb_flaeche_m2` | area of the unit, m² |
| `geb_bebauungsdichte_wert` | building coverage: 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | numerator: building footprint, m² |
| `geb_bebauungsdichte_nenner` | denominator: area of the unit, m² |
| `geb_bebauungsdichte_anzeige` | how the value is shown |
| `geb_geschossflaeche_naeherung_wert` | approximate floor area ratio: Σ(footprint × storeys) / area of the unit; for orientation, not an official value |
| `geb_geschossflaeche_naeherung_zaehler` | numerator: Σ(footprint × storeys), m² |
| `geb_geschossflaeche_naeherung_nenner` | denominator: area of the unit, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | label of the value |
| `klimat_flaeche_ha` | area of the unit within the city, ha |
| `klimat_abdeckung` | share of the unit covered by BDOT10k land cover classes, % |
| `klimat_ha_bebauung` | BDOT10k: area of land cover class: built-up land (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: area of land cover class: transport land and squares (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: area of land cover class: green space (PTRK, PTUT, grassland from PTTR), ha |
| `klimat_ha_wald` | BDOT10k: area of land cover class: woodland (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: area of land cover class: water (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: area of land cover class: arable land (crops from PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: area of land cover class: other (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: share of the land cover total: built-up land (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: share of the land cover total: transport land and squares (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: share of the land cover total: green space (PTRK, PTUT, grassland from PTTR), % |
| `klimat_anteil_wald` | BDOT10k: share of the land cover total: woodland (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: share of the land cover total: water (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: share of the land cover total: arable land (crops from PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: share of the land cover total: other (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: share of the land cover total: built-up and transport land together, % |
| `klimat_anteil_gruen_wald` | BDOT10k: share of the land cover total: green space and woodland together, % |
| `klimat_gruen_je_ew` | green space and woodland per resident, m² |
| `typ_mfh` | multi-family buildings in use (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `typ_blok` | estimate: block candidates among them (at least 4 storeys, footprint at least 250 m², rectangularity at least 0.85); includes osiedle |
| `typ_osiedle` | estimate: block candidates in a large housing estate (at least 9 other candidates within 150 m) |
| `typ_blok_angebaut` | indicator, not a rule: block candidates sharing at least 3 m of boundary with another BDOT10k building (perimeter block, typical of kamienice) |
| `typ_osiedle_angebaut` | as blok_angebaut, only candidates in a large housing estate |

### `delegatury`

| Field | Meaning |
|---|---|
| `gruppe` | number of the delegatura in the atlas: 1 = Kraków-Śródmieście, 2 = Kraków-Krowodrza, 3 = Kraków-Podgórze, 4 = Kraków-Nowa Huta |
| `teryt` | TERYT code |
| `nazwa` | name (Polish proper name) |
| `flaeche_km2` | area, km² |
| `flaeche_quelle` | source of the area |
| `nsp_einwohner` | NSP 2021: residents |
| `nsp_maenner` | NSP 2021: men |
| `nsp_frauen` | NSP 2021: women |
| `nsp_alter_10_a0_9` | NSP 2021: residents aged 0–9 |
| `nsp_alter_10_a10_19` | NSP 2021: residents aged 10–19 |
| `nsp_alter_10_a20_29` | NSP 2021: residents aged 20–29 |
| `nsp_alter_10_a30_39` | NSP 2021: residents aged 30–39 |
| `nsp_alter_10_a40_49` | NSP 2021: residents aged 40–49 |
| `nsp_alter_10_a50_59` | NSP 2021: residents aged 50–59 |
| `nsp_alter_10_a60_69` | NSP 2021: residents aged 60–69 |
| `nsp_alter_10_a70_79` | NSP 2021: residents aged 70–79 |
| `nsp_alter_10_a80p` | NSP 2021: residents aged 80 and over |
| `nsp_oekonomisch_vor` | NSP 2021: residents of pre-working age |
| `nsp_oekonomisch_erwerb` | NSP 2021: residents of working age |
| `nsp_oekonomisch_nach` | NSP 2021: residents of post-working age |
| `nsp_q_u20` | NSP 2021: share of residents under 20, % |
| `nsp_q_60p` | NSP 2021: share of residents aged 60 and over, % |
| `nsp_q_nach` | NSP 2021: share of residents of post-working age, % |
| `nsp_rejony` | NSP 2021: number of statistical areas (rejony statystyczne) |
| `nsp_weg` | where the NSP 2021 values come from |
| `gitter_zellen` | Eurostat grid: number of 1 km cells whose centre lies in the unit |
| `gitter_einwohner` | Eurostat grid: residents (sum of cells by their centre) |
| `gitter_u15` | Eurostat grid: residents under 15 |
| `gitter_a15_64` | Eurostat grid: residents aged 15–64 |
| `gitter_a65p` | Eurostat grid: residents aged 65 and over |
| `gitter_a_ges` | Eurostat grid: sum of the three age groups (may differ slightly from the residents) |
| `gitter_q_u15` | Eurostat grid: share under 15 in the sum of age groups, % |
| `gitter_q_65p` | Eurostat grid: share aged 65 and over in the sum of age groups, % |
| `gitter_einwohner_flaechenanteil` | Eurostat grid: residents by the area share of cells in the unit (comparison) |
| `gitter_abweichung_nsp_proz` | difference of grid residents from NSP 2021, %; empty without NSP |
| `dichte_nsp` | population density from NSP 2021, residents per km² |
| `dichte_gitter` | population density from the Eurostat grid, residents per km² |
| `geb_anzahl` | BDOT10k: buildings (OT_BUBD_A) with their inner point in the unit, all statuses |
| `geb_zustand_eksploatowany` | BDOT10k: buildings with status: in use (eksploatowany) |
| `geb_zustand_w_budowie` | BDOT10k: buildings with status: under construction (w budowie) |
| `geb_zustand_nieczynny` | BDOT10k: buildings with status: disused (nieczynny) |
| `geb_zustand_zniszczony` | BDOT10k: buildings with status: destroyed (zniszczony) |
| `geb_zustand_leer` | BDOT10k: buildings with status: no value |
| `geb_funktion_101` | BDOT10k: buildings with KŚT code 101: industrial buildings |
| `geb_funktion_102` | BDOT10k: buildings with KŚT code 102: transport and communication buildings |
| `geb_funktion_103` | BDOT10k: buildings with KŚT code 103: retail and service buildings |
| `geb_funktion_104` | BDOT10k: buildings with KŚT code 104: tanks, silos and warehouses |
| `geb_funktion_105` | BDOT10k: buildings with KŚT code 105: office buildings |
| `geb_funktion_106` | BDOT10k: buildings with KŚT code 106: hospitals and other healthcare buildings |
| `geb_funktion_107` | BDOT10k: buildings with KŚT code 107: education, science, culture and sports buildings |
| `geb_funktion_108` | BDOT10k: buildings with KŚT code 108: agricultural buildings (production, service, utility) |
| `geb_funktion_109` | BDOT10k: buildings with KŚT code 109: other non-residential buildings |
| `geb_funktion_110` | BDOT10k: buildings with KŚT code 110: residential buildings |
| `geb_funktion_unbekannt` | BDOT10k: buildings without a KŚT code |
| `geb_wohngebaeude` | BDOT10k: residential buildings (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: single-family residential buildings (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: multi-family residential buildings (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: other residential buildings (PFBUD) |
| `geb_geschosse_1` | BDOT10k: buildings: 1 storey |
| `geb_geschosse_2` | BDOT10k: buildings: 2 storeys |
| `geb_geschosse_3_4` | BDOT10k: buildings: 3–4 storeys |
| `geb_geschosse_5_10` | BDOT10k: buildings: 5–10 storeys |
| `geb_geschosse_11p` | BDOT10k: buildings: 11 or more storeys |
| `geb_geschosse_unbekannt` | BDOT10k: buildings: number of storeys unknown |
| `geb_geschosse_wohn_1` | BDOT10k: residential buildings: 1 storey |
| `geb_geschosse_wohn_2` | BDOT10k: residential buildings: 2 storeys |
| `geb_geschosse_wohn_3_4` | BDOT10k: residential buildings: 3–4 storeys |
| `geb_geschosse_wohn_5_10` | BDOT10k: residential buildings: 5–10 storeys |
| `geb_geschosse_wohn_11p` | BDOT10k: residential buildings: 11 or more storeys |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: residential buildings: number of storeys unknown |
| `geb_geschosse_median` | BDOT10k: median number of storeys above ground; empty below 30 buildings with known storeys |
| `geb_geschosse_mittel` | BDOT10k: mean number of storeys above ground; empty below 30 buildings with known storeys |
| `geb_geschosse_median_wohn` | BDOT10k: median number of storeys above ground of residential buildings; empty below 30 buildings with known storeys |
| `geb_geschosse_mittel_wohn` | BDOT10k: mean number of storeys above ground of residential buildings; empty below 30 buildings with known storeys |
| `geb_grundflaeche_m2` | BDOT10k: total building footprint without destroyed buildings, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: total footprint of residential buildings, m² |
| `geb_flaeche_m2` | area of the unit, m² |
| `geb_bebauungsdichte_wert` | building coverage: 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | numerator: building footprint, m² |
| `geb_bebauungsdichte_nenner` | denominator: area of the unit, m² |
| `geb_bebauungsdichte_anzeige` | how the value is shown |
| `geb_geschossflaeche_naeherung_wert` | approximate floor area ratio: Σ(footprint × storeys) / area of the unit; for orientation, not an official value |
| `geb_geschossflaeche_naeherung_zaehler` | numerator: Σ(footprint × storeys), m² |
| `geb_geschossflaeche_naeherung_nenner` | denominator: area of the unit, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | label of the value |
| `klimat_flaeche_ha` | area of the unit within the city, ha |
| `klimat_abdeckung` | share of the unit covered by BDOT10k land cover classes, % |
| `klimat_ha_bebauung` | BDOT10k: area of land cover class: built-up land (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: area of land cover class: transport land and squares (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: area of land cover class: green space (PTRK, PTUT, grassland from PTTR), ha |
| `klimat_ha_wald` | BDOT10k: area of land cover class: woodland (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: area of land cover class: water (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: area of land cover class: arable land (crops from PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: area of land cover class: other (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: share of the land cover total: built-up land (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: share of the land cover total: transport land and squares (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: share of the land cover total: green space (PTRK, PTUT, grassland from PTTR), % |
| `klimat_anteil_wald` | BDOT10k: share of the land cover total: woodland (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: share of the land cover total: water (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: share of the land cover total: arable land (crops from PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: share of the land cover total: other (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: share of the land cover total: built-up and transport land together, % |
| `klimat_anteil_gruen_wald` | BDOT10k: share of the land cover total: green space and woodland together, % |
| `typ_mfh` | multi-family buildings in use (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `typ_blok` | estimate: block candidates among them (at least 4 storeys, footprint at least 250 m², rectangularity at least 0.85); includes osiedle |
| `typ_osiedle` | estimate: block candidates in a large housing estate (at least 9 other candidates within 150 m) |
| `typ_blok_angebaut` | indicator, not a rule: block candidates sharing at least 3 m of boundary with another BDOT10k building (perimeter block, typical of kamienice) |
| `typ_osiedle_angebaut` | as blok_angebaut, only candidates in a large housing estate |
| `bdot_wohngebaeude` | BDOT10k: residential buildings (FOBUD) |
| `bdot_mehrfamilienhaeuser` | BDOT10k: multi-family buildings (PFBUD) |
| `bdot_namensbezug` | BDOT10k: buildings named “Kamienica …” |

### `siatka_1km`

| Field | Meaning |
|---|---|
| `id` | code of the 1 km Eurostat grid cell (EPSG:3035, south-west corner) |
| `ew` | residents (Eurostat grid 2021) |
| `a_ges` | sum of the three age groups in the cell |
| `q_u15` | share of residents under 15, % |
| `q_65p` | share of residents aged 65 and over, % |
| `luftlinie_m_haltestelle_takt` | straight-line distance from the cell centre to the nearest: stop of service frequency class I or II, m |
| `luftlinie_m_park` | straight-line distance from the cell centre to the nearest: park or square (BDOT10k), m |
| `luftlinie_m_przedszkole` | straight-line distance from the cell centre to the nearest: kindergarten (przedszkole), m |
| `luftlinie_m_szkola` | straight-line distance from the cell centre to the nearest: school of any type (BDOT10k does not distinguish), m |
| `luftlinie_m_szpital` | straight-line distance from the cell centre to the nearest: hospital (szpital), m |
| `luftlinie_m_zlobek` | straight-line distance from the cell centre to the nearest: nursery (żłobek), m |
| `wkt` | geometry as WKT in EPSG:2178 |

### `siatka_1km_pokrycie`

| Field | Meaning |
|---|---|
| `id` | code of the 1 km Eurostat grid cell (EPSG:3035, south-west corner) |
| `flaeche_stadt_ha` | area of the cell within the city, ha |
| `anteil_stadt` | share of the cell within the city, % |
| `abdeckung` | share of the unit covered by BDOT10k land cover classes, % |
| `ha_bebauung` | BDOT10k: area of land cover class: built-up land (PTZB), ha |
| `ha_verkehr` | BDOT10k: area of land cover class: transport land and squares (PTKM, PTPL), ha |
| `ha_gruen` | BDOT10k: area of land cover class: green space (PTRK, PTUT, grassland from PTTR), ha |
| `ha_wald` | BDOT10k: area of land cover class: woodland (PTLZ), ha |
| `ha_wasser` | BDOT10k: area of land cover class: water (PTWP), ha |
| `ha_acker` | BDOT10k: area of land cover class: arable land (crops from PTTR), ha |
| `ha_sonstige` | BDOT10k: area of land cover class: other (PTGN, PTSO, PTWZ, PTNZ), ha |
| `anteil` | technical field, always empty; shares are in the anteil_* columns |
| `anteil_grund` | reason for empty shares (area within the city below 10 ha) |
| `anteil_bebauung` | BDOT10k: share of the land cover total: built-up land (PTZB), % |
| `anteil_verkehr` | BDOT10k: share of the land cover total: transport land and squares (PTKM, PTPL), % |
| `anteil_gruen` | BDOT10k: share of the land cover total: green space (PTRK, PTUT, grassland from PTTR), % |
| `anteil_wald` | BDOT10k: share of the land cover total: woodland (PTLZ), % |
| `anteil_wasser` | BDOT10k: share of the land cover total: water (PTWP), % |
| `anteil_acker` | BDOT10k: share of the land cover total: arable land (crops from PTTR), % |
| `anteil_sonstige` | BDOT10k: share of the land cover total: other (PTGN, PTSO, PTWZ, PTNZ), % |
| `anteil_bebauung_verkehr` | BDOT10k: share of the land cover total: built-up and transport land together, % |
| `anteil_gruen_wald` | BDOT10k: share of the land cover total: green space and woodland together, % |
| `wkt` | geometry as WKT in EPSG:2178 |

### `rejony_statystyczne`

| Field | Meaning |
|---|---|
| `rejon` | GUS statistical area identifier (6 digits) |
| `delegatura_teryt` | TERYT code of the delegatura according to GUS |
| `nsp_einwohner` | NSP 2021: residents of the area; empty = no row in the census table |
| `flaeche_km2` | area, km² |
| `dichte_nsp` | population density from NSP 2021, residents per km² |
| `nsp_q_u20` | NSP 2021: share under 20, whole %; empty below 100 people |
| `nsp_q_60p` | NSP 2021: share aged 60 and over, whole %; empty below 100 people |
| `nsp_q_nach` | NSP 2021: share of post-working age, whole %; empty below 100 people |
| `ohne_zeile` | 1 = area without a row in the census table (no values) |
| `wkt` | geometry as WKT in EPSG:2178 |

### `placowki_bdot`

| Field | Meaning |
|---|---|
| `id` | object identifier in BDOT10k (LOKALNYID) |
| `art` | type of facility |
| `unterart` | subtype: empty (not in BDOT10k) |
| `q` | source (key in the licencje table) |
| `name` | facility name from BDOT10k (official, not a person) |
| `plaetze` | places: empty (not in BDOT10k) |
| `schueler` | pupils: empty (not in BDOT10k) |
| `schueler_stand` | date of the pupil count: empty |
| `status` | what is known about the facility |
| `in_stadt` | within Kraków (BDOT10k); 1 = yes, 0 = no |
| `x` | x coordinate (east) in EPSG:2178, m |
| `y` | y coordinate (north) in EPSG:2178, m |

### `przystanki`

| Field | Meaning |
|---|---|
| `id` | stem of the ZTP stop code (stop_code before the hyphen) |
| `name` | stop name (stop_name) |
| `verkehrsmittel` | modes with departures on the counting day |
| `fahrten_hvz_je_richtung` | departures per hour in the window 06:00–09:00, busier direction |
| `taktklasse` | service frequency class (own classification, not a standard) |
| `in_stadt` | within Kraków (BDOT10k); 1 = yes, 0 = no |
| `x` | x coordinate (east) in EPSG:2178, m |
| `y` | y coordinate (north) in EPSG:2178, m |

### `bdot_kompleksy`

| Field | Meaning |
|---|---|
| `r` | type of complex (BDOT10k RODZAJ) |
| `n` | name of the complex (BDOT10k NAZWA) |
| `del` | delegatura (name from BDOT10k); empty = not assigned |
| `wkt` | geometry as WKT in EPSG:2178 |

### `bdot_kamienica_nazwa`

| Field | Meaning |
|---|---|
| `w` | residential building (FOBUD); empty = no building; 1 = yes, 0 = no |
| `mfh` | multi-family building (PFBUD); empty = no building; 1 = yes, 0 = no |
| `gs` | storeys above ground (BDOT10k LICZ_KONDY) |
| `del` | delegatura (name from BDOT10k); empty = not assigned |
| `x` | x coordinate (east) in EPSG:2178, m |
| `y` | y coordinate (north) in EPSG:2178, m |

### `rejestr_zabytkow`

| Field | Meaning |
|---|---|
| `q` | source of the point (wd = Wikidata, nid = NID register, gez = gminna ewidencja zabytków; several separated by commas) |
| `ep` | construction period from the inception date in Wikidata (class, never a single year); empty = none or ambiguous |
| `w` | residential building (FOBUD); empty = no building; 1 = yes, 0 = no |
| `mfh` | multi-family building (PFBUD); empty = no building; 1 = yes, 0 = no |
| `del` | delegatura (name from BDOT10k); empty = not assigned |
| `polozenie_sprawdzone` | location of this point checked individually on aerial imagery (0 everywhere: at most a random sample of the layer was checked, result in README.md); 1 = yes, 0 = no |
| `x` | x coordinate (east) in EPSG:2178, m |
| `y` | y coordinate (north) in EPSG:2178, m |

### `zbk_wykaz_dzielnice`

| Field | Meaning |
|---|---|
| `dzielnica_z_wykazu` | district as listed by ZBK (number 01–18; poza = outside Kraków) |
| `n` | number of list entries (an entry is not always a building) |
| `art_M` | list entries of type: residential (M) |
| `art_MP` | list entries of type: residential and clinic (MP) |
| `art_MU` | list entries of type: residential and non-residential (MU) |
| `art_MUP` | list entries of type: residential, non-residential and clinic (MUP) |
| `art_P` | list entries of type: health clinic (P) |
| `art_U` | list entries of type: non-residential use (U) |
| `eigentum_gmina` | list entries, ownership: City of Kraków (Gmina Miejska Kraków) |
| `eigentum_skarb_panstwa` | list entries, ownership: State Treasury (Skarb Państwa) |
| `eigentum_publiczne_mieszane` | list entries, ownership: several public owners or the voivodeship |
| `eigentum_z_prywatnymi` | list entries, ownership: public ownership with private co-owners |
| `eigentum_prywatne` | list entries, ownership: private owners only |
| `eigentum_brak` | list entries, ownership: ownership cannot be classified |
| `art_UP` | list entries of type: non-residential and clinic (UP) |

### `dzielnice`

| Field | Meaning |
|---|---|
| `nr` | district number (01–18) |
| `rzymska` | district number in Roman numerals |
| `nazwa` | name (Polish proper name) |
| `gruppe` | delegatura the district belongs to: 1 = Kraków-Śródmieście, 2 = Kraków-Krowodrza, 3 = Kraków-Podgórze, 4 = Kraków-Nowa Huta |
| `flaeche_km2` | area, km² |
| `osm_id` | boundary relation in OpenStreetMap |
| `gitter_zellen` | Eurostat grid: number of 1 km cells whose centre lies in the unit |
| `gitter_einwohner` | Eurostat grid: residents (sum of cells by their centre) |
| `gitter_u15` | Eurostat grid: residents under 15 |
| `gitter_a15_64` | Eurostat grid: residents aged 15–64 |
| `gitter_a65p` | Eurostat grid: residents aged 65 and over |
| `gitter_a_ges` | Eurostat grid: sum of the three age groups (may differ slightly from the residents) |
| `gitter_q_u15` | Eurostat grid: share under 15 in the sum of age groups, % |
| `gitter_q_65p` | Eurostat grid: share aged 65 and over in the sum of age groups, % |
| `gitter_einwohner_flaechenanteil` | Eurostat grid: residents by the area share of cells in the unit (comparison) |
| `gitter_abweichung_nsp_proz` | difference of grid residents from NSP 2021, %; empty without NSP |
| `gitter_zellen_beruehrt` | number of cells that lie at least partly in the unit |
| `gitter_spanne_proz` | difference between the area rule and the centre rule, % (blur at the boundaries, not an error) |
| `dichte_gitter` | population density from the Eurostat grid, residents per km² |
| `nsp_einwohner` | NSP 2021: residents |
| `nsp_maenner` | NSP 2021: men |
| `nsp_frauen` | NSP 2021: women |
| `nsp_alter_10_a0_9` | NSP 2021: residents aged 0–9 |
| `nsp_alter_10_a10_19` | NSP 2021: residents aged 10–19 |
| `nsp_alter_10_a20_29` | NSP 2021: residents aged 20–29 |
| `nsp_alter_10_a30_39` | NSP 2021: residents aged 30–39 |
| `nsp_alter_10_a40_49` | NSP 2021: residents aged 40–49 |
| `nsp_alter_10_a50_59` | NSP 2021: residents aged 50–59 |
| `nsp_alter_10_a60_69` | NSP 2021: residents aged 60–69 |
| `nsp_alter_10_a70_79` | NSP 2021: residents aged 70–79 |
| `nsp_alter_10_a80p` | NSP 2021: residents aged 80 and over |
| `nsp_oekonomisch_vor` | NSP 2021: residents of pre-working age |
| `nsp_oekonomisch_erwerb` | NSP 2021: residents of working age |
| `nsp_oekonomisch_nach` | NSP 2021: residents of post-working age |
| `nsp_q_u20` | NSP 2021: share of residents under 20, % |
| `nsp_q_60p` | NSP 2021: share of residents aged 60 and over, % |
| `nsp_q_nach` | NSP 2021: share of residents of post-working age, % |
| `nsp_rejony` | NSP 2021: number of statistical areas (rejony statystyczne) |
| `nsp_weg` | where the NSP 2021 values come from |
| `dichte_nsp` | population density from NSP 2021, residents per km² |
| `geb_anzahl` | BDOT10k: buildings (OT_BUBD_A) with their inner point in the unit, all statuses |
| `geb_zustand_eksploatowany` | BDOT10k: buildings with status: in use (eksploatowany) |
| `geb_zustand_w_budowie` | BDOT10k: buildings with status: under construction (w budowie) |
| `geb_zustand_nieczynny` | BDOT10k: buildings with status: disused (nieczynny) |
| `geb_zustand_zniszczony` | BDOT10k: buildings with status: destroyed (zniszczony) |
| `geb_zustand_leer` | BDOT10k: buildings with status: no value |
| `geb_funktion_101` | BDOT10k: buildings with KŚT code 101: industrial buildings |
| `geb_funktion_102` | BDOT10k: buildings with KŚT code 102: transport and communication buildings |
| `geb_funktion_103` | BDOT10k: buildings with KŚT code 103: retail and service buildings |
| `geb_funktion_104` | BDOT10k: buildings with KŚT code 104: tanks, silos and warehouses |
| `geb_funktion_105` | BDOT10k: buildings with KŚT code 105: office buildings |
| `geb_funktion_106` | BDOT10k: buildings with KŚT code 106: hospitals and other healthcare buildings |
| `geb_funktion_107` | BDOT10k: buildings with KŚT code 107: education, science, culture and sports buildings |
| `geb_funktion_108` | BDOT10k: buildings with KŚT code 108: agricultural buildings (production, service, utility) |
| `geb_funktion_109` | BDOT10k: buildings with KŚT code 109: other non-residential buildings |
| `geb_funktion_110` | BDOT10k: buildings with KŚT code 110: residential buildings |
| `geb_funktion_unbekannt` | BDOT10k: buildings without a KŚT code |
| `geb_wohngebaeude` | BDOT10k: residential buildings (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: single-family residential buildings (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: multi-family residential buildings (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: other residential buildings (PFBUD) |
| `geb_geschosse_1` | BDOT10k: buildings: 1 storey |
| `geb_geschosse_2` | BDOT10k: buildings: 2 storeys |
| `geb_geschosse_3_4` | BDOT10k: buildings: 3–4 storeys |
| `geb_geschosse_5_10` | BDOT10k: buildings: 5–10 storeys |
| `geb_geschosse_11p` | BDOT10k: buildings: 11 or more storeys |
| `geb_geschosse_unbekannt` | BDOT10k: buildings: number of storeys unknown |
| `geb_geschosse_wohn_1` | BDOT10k: residential buildings: 1 storey |
| `geb_geschosse_wohn_2` | BDOT10k: residential buildings: 2 storeys |
| `geb_geschosse_wohn_3_4` | BDOT10k: residential buildings: 3–4 storeys |
| `geb_geschosse_wohn_5_10` | BDOT10k: residential buildings: 5–10 storeys |
| `geb_geschosse_wohn_11p` | BDOT10k: residential buildings: 11 or more storeys |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: residential buildings: number of storeys unknown |
| `geb_geschosse_median` | BDOT10k: median number of storeys above ground; empty below 30 buildings with known storeys |
| `geb_geschosse_mittel` | BDOT10k: mean number of storeys above ground; empty below 30 buildings with known storeys |
| `geb_geschosse_median_wohn` | BDOT10k: median number of storeys above ground of residential buildings; empty below 30 buildings with known storeys |
| `geb_geschosse_mittel_wohn` | BDOT10k: mean number of storeys above ground of residential buildings; empty below 30 buildings with known storeys |
| `geb_grundflaeche_m2` | BDOT10k: total building footprint without destroyed buildings, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: total footprint of residential buildings, m² |
| `geb_flaeche_m2` | area of the unit, m² |
| `geb_bebauungsdichte_wert` | building coverage: 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | numerator: building footprint, m² |
| `geb_bebauungsdichte_nenner` | denominator: area of the unit, m² |
| `geb_bebauungsdichte_anzeige` | how the value is shown |
| `geb_geschossflaeche_naeherung_wert` | approximate floor area ratio: Σ(footprint × storeys) / area of the unit; for orientation, not an official value |
| `geb_geschossflaeche_naeherung_zaehler` | numerator: Σ(footprint × storeys), m² |
| `geb_geschossflaeche_naeherung_nenner` | denominator: area of the unit, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | label of the value |
| `klimat_flaeche_ha` | area of the unit within the city, ha |
| `klimat_abdeckung` | share of the unit covered by BDOT10k land cover classes, % |
| `klimat_ha_bebauung` | BDOT10k: area of land cover class: built-up land (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: area of land cover class: transport land and squares (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: area of land cover class: green space (PTRK, PTUT, grassland from PTTR), ha |
| `klimat_ha_wald` | BDOT10k: area of land cover class: woodland (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: area of land cover class: water (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: area of land cover class: arable land (crops from PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: area of land cover class: other (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: share of the land cover total: built-up land (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: share of the land cover total: transport land and squares (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: share of the land cover total: green space (PTRK, PTUT, grassland from PTTR), % |
| `klimat_anteil_wald` | BDOT10k: share of the land cover total: woodland (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: share of the land cover total: water (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: share of the land cover total: arable land (crops from PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: share of the land cover total: other (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: share of the land cover total: built-up and transport land together, % |
| `klimat_anteil_gruen_wald` | BDOT10k: share of the land cover total: green space and woodland together, % |
| `klimat_einwohner` | residents from the Eurostat grid, basis for green space per resident |
| `klimat_gruen_je_ew` | green space and woodland per resident, m² |
| `wkt` | geometry as WKT in EPSG:2178 |

### `siatka_1km_odbl`

| Field | Meaning |
|---|---|
| `id` | code of the 1 km Eurostat grid cell (EPSG:3035, south-west corner) |
| `st` | district by the cell centre (OSM boundaries) |
| `ew` | residents (Eurostat grid 2021) |
| `a_ges` | sum of the three age groups in the cell |
| `q_u15` | share of residents under 15, % |
| `q_65p` | share of residents aged 65 and over, % |
| `fussweg_m_apotheke` | walking route along the OSM network from the cell centre to the nearest: pharmacy (OSM), m |
| `fussweg_m_arzt` | walking route along the OSM network from the cell centre to the nearest: doctor or practice (OSM amenity=doctors), m |
| `fussweg_m_haltestelle_takt` | walking route along the OSM network from the cell centre to the nearest: stop of service frequency class I or II, m |
| `fussweg_m_park` | walking route along the OSM network from the cell centre to the nearest: park or square (BDOT10k), m |
| `fussweg_m_pflege` | walking route along the OSM network from the cell centre to the nearest: care home (OSM), m |
| `fussweg_m_przedszkole` | walking route along the OSM network from the cell centre to the nearest: kindergarten (przedszkole), m |
| `fussweg_m_spielplatz` | walking route along the OSM network from the cell centre to the nearest: public playground (OSM), m |
| `fussweg_m_supermarkt` | walking route along the OSM network from the cell centre to the nearest: supermarket or convenience store (OSM), m |
| `fussweg_m_szkola` | walking route along the OSM network from the cell centre to the nearest: school of any type (BDOT10k does not distinguish), m |
| `fussweg_m_szpital` | walking route along the OSM network from the cell centre to the nearest: hospital (szpital), m |
| `fussweg_m_zlobek` | walking route along the OSM network from the cell centre to the nearest: nursery (żłobek), m |
| `wkt` | geometry as WKT in EPSG:2178 |

### `dostepnosc`

| Field | Meaning |
|---|---|
| `st` | district (01–18); empty = whole city |
| `nazwa` | name of the district or city |
| `ew` | residents of the area (Eurostat grid, rounded) |
| `kennzahl` | indicator |
| `art` | type of destination |
| `methode` | how distance is measured |
| `einheit` | unit of the value |
| `status` | status of the value |
| `vorlaeufig` | 1 = provisional (schools without catchment areas); empty = not applicable |
| `q` | source (key in the licencje table) |
| `richtwert_wert` | radius from the official standard used for comparison |
| `richtwert_einheit` | unit of the radius |
| `richtwert_q` | source of the standard (key in the licencje table) |
| `richtwert_seite` | location in the legal act (article, page) |
| `radius_m` | radius in metres used for the count (share within radius, stops, parks); empty = not applicable |
| `wert` | value of the indicator; empty below the confidentiality threshold |
| `zaehler` | numerator of the indicator (e.g. residents within the radius, park area) |
| `nenner` | denominator of the indicator (e.g. residents, number of facilities) |
| `stand` | data as of (date) |

### `placowki_osm`

| Field | Meaning |
|---|---|
| `id` | OSM object identifier (n = node, w = way) |
| `art` | type of facility |
| `unterart` | doctor's speciality from the OSM tag healthcare:speciality (OSM values); empty = no tag |
| `q` | source (key in the licencje table) |
| `x` | x coordinate (east) in EPSG:2178, m |
| `y` | y coordinate (north) in EPSG:2178, m |

### `osm_heritage_start_date`

| Field | Meaning |
|---|---|
| `h` | object has a heritage tag; 1 = yes, 0 = no |
| `ep` | construction period from the start_date tag (class, never a single year); empty = none or ambiguous |
| `w` | residential building (FOBUD); empty = no building; 1 = yes, 0 = no |
| `mfh` | multi-family building (PFBUD); empty = no building; 1 = yes, 0 = no |
| `del` | delegatura (name from BDOT10k); empty = not assigned |
| `polozenie_sprawdzone` | location of this point checked individually on aerial imagery (0 everywhere: at most a random sample of the layer was checked, result in README.md); 1 = yes, 0 = no |
| `x` | x coordinate (east) in EPSG:2178, m |
| `y` | y coordinate (north) in EPSG:2178, m |

### `zbk_budynki`

| Field | Meaning |
|---|---|
| `art` | building type in the ZBK list |
| `eig` | ownership in the ZBK list (points only without private owners) |
| `st` | district as listed by ZBK |
| `gs` | storeys above ground (BDOT10k LICZ_KONDY) |
| `fn` | main use of the linked BDOT10k building (PFBUD); empty = none |
| `h` | building height, m (see hq) |
| `hq` | origin of the height |
| `typ` | typology (estimate); empty = no candidate |
| `x` | x coordinate (east) in EPSG:2178, m |
| `y` | y coordinate (north) in EPSG:2178, m |

### `zbk_typologia_dzielnice`

| Field | Meaning |
|---|---|
| `st` | district number (01–18) |
| `szacunek` | values are an estimate; 1 = yes, 0 = no |
| `mfh` | multi-family buildings in use (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `blok` | estimate: block candidates among them (at least 4 storeys, footprint at least 250 m², rectangularity at least 0.85); includes osiedle |
| `osiedle` | estimate: block candidates in a large housing estate (at least 9 other candidates within 150 m) |
| `blok_angebaut` | indicator, not a rule: block candidates sharing at least 3 m of boundary with another BDOT10k building (perimeter block, typical of kamienice) |
| `osiedle_angebaut` | as blok_angebaut, only candidates in a large housing estate |

### `licencje`

| Field | Meaning |
|---|---|
| `plik` | GeoPackage file |
| `warstwa` | layer |
| `licencja_pliku` | licence of the layer in this file |
| `licencja_zrodla` | licence of the source |
| `zrodlo` | source |
| `nota` | source notice to give (verbatim) |

## Coded values

| Field | Value | Meaning |
|---|---|---|
| `flaeche_quelle` | `bdot10k` | boundary from BDOT10k (PRG) |
| `nsp_weg` | `tabelle` | GUS table for the whole unit |
| `geb_bebauungsdichte_anzeige` | `anteil` | shown as a share in % |
| `geb_geschossflaeche_naeherung_abzeichen` | `orientacyjnie` | for orientation |
| `anteil_grund` | `bezugsflaeche_zu_klein` | reference area too small |
| `art` | `park` | park or square (BDOT10k) |
| `art` | `przedszkole` | kindergarten (przedszkole) |
| `art` | `szkola` | school of any type (BDOT10k does not distinguish) |
| `art` | `szpital` | hospital (szpital) |
| `art` | `zlobek` | nursery (żłobek) |
| `q` | `bdot10k` | BDOT10k (GUGiK) |
| `status` | `lage_ohne_kapazitaet` | location only, no places or pupils |
| `verkehrsmittel` | `bus` | bus |
| `verkehrsmittel` | `bus+tram` | bus and tram |
| `verkehrsmittel` | `tram` | tram |
| `taktklasse` | `I` | departures per hour and direction: at least 6 |
| `taktklasse` | `II` | departures per hour and direction: at least 2 |
| `taktklasse` | `III` | departures per hour and direction: at least 1 |
| `taktklasse` | `unter III` | departures per hour and direction: fewer than 1 |
| `r` | `muzeum` | museum complex (zespół muzealny) |
| `r` | `pamiec` | national memorial site (miejsce pamięci narodowej) |
| `r` | `twierdza` | fortress (twierdza lub forteca) |
| `r` | `zabudowa` | historic building ensemble (zespół zabudowy historycznej) |
| `q` | `wd` | Wikidata (CC0 1.0) |
| `ep` | `1800_1866` | 1800–1866 |
| `ep` | `1867_1918` | 1867–1918 |
| `ep` | `1919_1945` | 1919–1945 |
| `ep` | `1946_1989` | 1946–1989 |
| `ep` | `ab_1990` | from 1990 |
| `ep` | `vor_1800` | before 1800 |
| `nsp_weg` | `rejony` | sum of statistical areas |
| `kennzahl` | `anteil_in_radius` | share of residents with a facility within the radius of the official standard (richtwert_wert), % |
| `kennzahl` | `ew_je_einrichtung` | residents per facility |
| `kennzahl` | `gruen_in_radius` | share of residents with a park or square within 500 m walking, % |
| `kennzahl` | `gruen_m2_je_ew` | park and square area (BDOT10k) per resident, m² |
| `kennzahl` | `oepnv_takt` | share of residents with a class I or II stop within 500 m, % |
| `art` | `haltestelle_takt` | stop of service frequency class I or II |
| `methode` | `fussweg` | walking route along the OSM network from the centre of the 1 km cell |
| `methode` | `luftlinie` | straight-line distance from the centre of the 1 km cell |
| `einheit` | `%` | per cent |
| `einheit` | `ew_je_einrichtung` | residents per facility |
| `einheit` | `m2_je_ew` | m² per resident |
| `status` | `orientierung` | guide value, not official |
| `q` | `ztp` | GTFS of ZTP Kraków |
| `richtwert_einheit` | `m` | metres |
| `richtwert_q` | `prawo_oswiatowe` | Education Law (Prawo oświatowe) |
| `art` | `apotheke` | pharmacy (OSM) |
| `art` | `arzt` | doctor or practice (OSM amenity=doctors) |
| `q` | `osm` | OpenStreetMap |
| `art` | `M` | residential (M) |
| `art` | `MP` | residential and clinic (MP) |
| `art` | `MU` | residential and non-residential (MU) |
| `art` | `P` | health clinic (P) |
| `art` | `U` | non-residential use (U) |
| `eig` | `gmina` | City of Kraków (Gmina Miejska Kraków) |
| `eig` | `publiczne_mieszane` | several public owners or the voivodeship |
| `eig` | `skarb_panstwa` | State Treasury (Skarb Państwa) |
| `hq` | `geschosse` | storeys × 3 m (estimate) |
| `hq` | `lod2` | LoD2 3D model (GUGiK, as of 2017) |
| `typ` | `blok` | block candidate (estimate) |
| `typ` | `osiedle` | block candidate in a large housing estate (estimate) |

## How to cite

Kiezatlas Kraków, Stiebitz Souverain Systems UG (haftungsbeschränkt), https://souverain-systems.de/kiezatlas/krakow/, data state 2026-11-14 (downloads). Details: `CITATION.cff` in the repository. Each layer must carry the source notices listed in the table `licencje`.

Found an error? kontakt@souverain-systems.de
