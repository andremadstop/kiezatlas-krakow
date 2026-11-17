# Kiezatlas Kraków: Downloads

Datenstand: erzeugt aus den Datendateien des Atlas (Ordner `daten/`), jüngstes Datum in den Daten: 2026-11-14. Skript: `skripte/16_export_krakow.py`.

## Dateien

- `kiezatlas_krakow.gpkg`: GeoPackage ohne Daten aus OpenStreetMap. Lizenzen der Quellen in der Tabelle `licencje`.
- `kiezatlas_krakow_odbl.gpkg`: GeoPackage mit den Daten aus OpenStreetMap und allem, was über die OSM-Grenzen einer dzielnica zugeordnet ist. Ganze Datei: Open Database License 1.0, © OpenStreetMap-Mitwirkende (https://opendatacommons.org/licenses/odbl/1-0/).
- `csv/`, `csv_odbl/`: Dieselben Ebenen als CSV (UTF-8 mit BOM, Semikolon, Dezimalpunkt).
- `csv_pl/`, `csv_odbl_pl/`: Dasselbe mit **Dezimalkomma** und ohne Tausendertrenner, für Excel und LibreOffice mit polnischer (oder deutscher) Ländereinstellung.
- `kiezatlas_krakow.qgz`: QGIS-Projekt (relative Pfade; beide GeoPackages im selben Ordner lassen).
- `licencje.csv`: Lizenz und wörtlicher Quellenvermerk je Ebene.
- `pola.csv`, `wartosci.csv`: Bedeutung jedes Felds (`pola.csv`) und jedes kodierten Werts (`wartosci.csv`) auf Polnisch, Englisch und Deutsch; auch als Tabellen `pola` und `wartosci` in beiden GeoPackages.
- `kiezatlas_krakow_csv.zip`: Alle CSV mit `licencje.csv`, `pola.csv`, `wartosci.csv` und den Liesmich-Dateien in einem Archiv.

## Ebenen

| Ebene | Datei | Geometrie | Zeilen | Aus den Atlas-Dateien |
|---|---|---|---:|---|
| `miasto`: Krakau: Zahlen der ganzen Stadt | `kiezatlas_krakow.gpkg` | keine | 1 | `steckbrief`, `gebaeude_kennzahlen`, `klimat`, `sanierung` |
| `delegatury`: Vier delegatury (historische Stadtbezirke) | `kiezatlas_krakow.gpkg` | keine | 4 | `steckbrief`, `gebaeude_kennzahlen`, `klimat`, `sanierung`, `denkmale_bdot` |
| `siatka_1km`: 1-km-Gitter: Einwohner und Luftlinie | `kiezatlas_krakow.gpkg` | polygon | 327 | `zellen_odbl`, `erreichbar` |
| `siatka_1km_pokrycie`: 1-km-Gitter: Bodenbedeckung | `kiezatlas_krakow.gpkg` | polygon | 397 | `klimat_zellen` |
| `rejony_statystyczne`: Statistische Bezirke (rejony): Bevölkerung nach NSP 2021 | `kiezatlas_krakow.gpkg` | multipolygon | 749 | `rejony` |
| `placowki_bdot`: Einrichtungen aus BDOT10k | `kiezatlas_krakow.gpkg` | point | 321 | `einrichtungen` |
| `przystanki`: Haltestellen mit Taktklasse | `kiezatlas_krakow.gpkg` | point | 944 | `haltestellen` |
| `bdot_kompleksy`: BDOT10k-Komplexe (Museen, Forts, Bauensembles) | `kiezatlas_krakow.gpkg` | polygon | 59 | `denkmale_bdot` |
| `bdot_kamienica_nazwa`: Gebäude mit dem Namen „Kamienica …“ in BDOT10k | `kiezatlas_krakow.gpkg` | point | 28 | `denkmale_bdot` |
| `rejestr_zabytkow`: Registerpunkte aus Wikidata: Objekte mit gleicher Registernummer als ein Punkt (Lage in Stichprobe geprüft) | `kiezatlas_krakow.gpkg` | point | 1214 | `denkmale` |
| `zbk_wykaz_dzielnice`: ZBK-Liste: Zählungen je dzielnica laut Liste | `kiezatlas_krakow.gpkg` | keine | 19 | `sanierung` |
| `dzielnice`: 18 dzielnice: Grenzen und Kennzahlen | `kiezatlas_krakow_odbl.gpkg` | multipolygon | 18 | `stadtteile_odbl`, `steckbrief_dzielnice_odbl`, `gebaeude_dzielnice_odbl`, `klimat_stadtteile_odbl` |
| `siatka_1km_odbl`: 1-km-Gitter mit dzielnica und Fußweg | `kiezatlas_krakow_odbl.gpkg` | polygon | 327 | `zellen_odbl`, `erreichbar_fuss_odbl` |
| `dostepnosc`: Versorgung je dzielnica | `kiezatlas_krakow_odbl.gpkg` | keine | 247 | `planer_odbl`, `planer_fuss_odbl` |
| `placowki_osm`: Ärzte und Apotheken aus OpenStreetMap | `kiezatlas_krakow_odbl.gpkg` | point | 604 | `einrichtungen_odbl` |
| `osm_heritage_start_date`: OSM-Objekte mit heritage oder start_date (Lage der Objekte mit heritage in Stichprobe geprüft) | `kiezatlas_krakow_odbl.gpkg` | point | 929 | `denkmale_odbl` |
| `zbk_budynki`: ZBK-Gebäude in öffentlichem Eigentum (Lage) | `kiezatlas_krakow_odbl.gpkg` | point | 126 | `sanierung_odbl` |
| `zbk_typologia_dzielnice`: Typologie der Blöcke je dzielnica (Schätzung) | `kiezatlas_krakow_odbl.gpkg` | keine | 18 | `sanierung_odbl` |

Die Ebene `siatka_1km` übernimmt aus `zellen_odbl` nur Einwohner und Altersanteile (Eurostat), ohne Zuordnung zur dzielnica (`st`); die Geometrie der Zelle entsteht aus ihrer Kennung im Eurostat-Gitter. Es sind die Zellen mit Mittelpunkt in der Stadtgrenze aus BDOT10k, deshalb enthält die Ebene keine Daten aus OpenStreetMap.

Koordinatensystem: ETRS89 / Poland CS2000 zone 7 (EPSG:2178). Koordinaten auf 0,01 m gerundet; Geometrien nicht vereinfacht. Feldnamen wie in den Atlas-Dateien; ihre Bedeutung steht in den Abschnitten unten und in `pola.csv` und `wartosci.csv`. Wahrheitswerte in der CSV: 1 = ja, 0 = nein; leeres Feld = keine Angabe.

## Nicht im Export

Keine Atlas-Datei enthält noch Beispieldaten.

Noch ohne eigene Ebene im Export sind (echte Daten, nur als Atlas-Dateien im Ordner `daten/`):

- Wohnungsmarkt: `mieszkania_odbl.js`
- Luft: `powietrze.js`

## Grenzen

- Keine Baujahre und keine Heizungsdaten: Das Baujahr im Kataster ist kostenpflichtig, das Register CEEB nicht offen. Eine Bauzeitklasse (`ep`) haben nur einzelne Objekte: mit `start_date` in OSM (Ebene `osm_heritage_start_date`) und mit Entstehungsdatum in Wikidata (Ebene `rejestr_zabytkow`), ungeprüft und nie für Flächen.
- Die Bevölkerung stammt aus dem Eurostat-Gitter (Eurostat, Census 2021 population grid, Datei PL_PD_3035_GPKG.zip); Werte je dzielnica summieren Zellen nach ihrem Mittelpunkt und sind an den Grenzen eine Näherung.
- Die Typologie der Blöcke (`typ_*`) ist eine Schätzung aus BDOT10k (Geschosse, Grundfläche, Rechteckigkeit), kein Verzeichnis der Plattenbauten.
- Entfernungen sind Luftlinie oder Fußweg vom Mittelpunkt einer 1-km-Zelle zur nächsten Einrichtung; Orientierung, kein amtlicher Wert.
- Die Lage ist am Luftbild nur in einer Zufallsstichprobe geprüft (2026-11-15): Registerpunkte (Wikidata) 17 von 20 auf dem Objekt (85 %, 95-%-Wilson-Intervall 64 %–95 %), OSM-Objekte mit `heritage` 16 von 20 (80 %, 58 %–92 %); „knapp daneben“ zählt nicht als „auf dem Objekt“. Das ist ein Ergebnis für die Ebene, nicht für den Punkt: `polozenie_sprawdzone` = 0 an jedem Punkt. Die Zuordnung zum Gebäude ist nicht geprüft.

## Bedeutung der Felder

### `miasto`

| Feld | Bedeutung |
|---|---|
| `teryt` | TERYT-Kennung |
| `nazwa` | Name (polnischer Eigenname) |
| `flaeche_km2` | Fläche, km² |
| `flaeche_quelle` | Quelle der Fläche |
| `nsp_einwohner` | NSP 2021: Einwohner |
| `nsp_maenner` | NSP 2021: Männer |
| `nsp_frauen` | NSP 2021: Frauen |
| `nsp_alter_10_a0_9` | NSP 2021: Einwohner von 0 bis 9 Jahren |
| `nsp_alter_10_a10_19` | NSP 2021: Einwohner von 10 bis 19 Jahren |
| `nsp_alter_10_a20_29` | NSP 2021: Einwohner von 20 bis 29 Jahren |
| `nsp_alter_10_a30_39` | NSP 2021: Einwohner von 30 bis 39 Jahren |
| `nsp_alter_10_a40_49` | NSP 2021: Einwohner von 40 bis 49 Jahren |
| `nsp_alter_10_a50_59` | NSP 2021: Einwohner von 50 bis 59 Jahren |
| `nsp_alter_10_a60_69` | NSP 2021: Einwohner von 60 bis 69 Jahren |
| `nsp_alter_10_a70_79` | NSP 2021: Einwohner von 70 bis 79 Jahren |
| `nsp_alter_10_a80p` | NSP 2021: Einwohner ab 80 Jahren |
| `nsp_oekonomisch_vor` | NSP 2021: Einwohner im vorerwerbsfähigen Alter |
| `nsp_oekonomisch_erwerb` | NSP 2021: Einwohner im erwerbsfähigen Alter |
| `nsp_oekonomisch_nach` | NSP 2021: Einwohner im nacherwerbsfähigen Alter |
| `nsp_q_u20` | NSP 2021: Anteil unter 20 Jahren, % |
| `nsp_q_60p` | NSP 2021: Anteil ab 60 Jahren, % |
| `nsp_q_nach` | NSP 2021: Anteil im nacherwerbsfähigen Alter, % |
| `nsp_rejony` | NSP 2021: Zahl der rejony statystyczne |
| `nsp_weg` | Herkunft der Werte aus dem NSP 2021 |
| `gitter_zellen` | Eurostat-Gitter: Zahl der 1-km-Zellen mit Mittelpunkt in der Einheit |
| `gitter_einwohner` | Eurostat-Gitter: Einwohner (Summe der Zellen nach ihrem Mittelpunkt) |
| `gitter_u15` | Eurostat-Gitter: Einwohner unter 15 Jahren |
| `gitter_a15_64` | Eurostat-Gitter: Einwohner von 15 bis 64 Jahren |
| `gitter_a65p` | Eurostat-Gitter: Einwohner ab 65 Jahren |
| `gitter_a_ges` | Eurostat-Gitter: Summe der drei Altersgruppen (kann leicht von den Einwohnern abweichen) |
| `gitter_q_u15` | Eurostat-Gitter: Anteil unter 15 Jahren an der Summe der Altersgruppen, % |
| `gitter_q_65p` | Eurostat-Gitter: Anteil ab 65 Jahren an der Summe der Altersgruppen, % |
| `gitter_einwohner_flaechenanteil` | Eurostat-Gitter: Einwohner nach Flächenanteil der Zellen (Vergleich) |
| `gitter_abweichung_nsp_proz` | Abweichung der Gitter-Einwohner vom NSP 2021, %; leer ohne NSP |
| `dichte_nsp` | Einwohnerdichte nach NSP 2021, Einwohner je km² |
| `dichte_gitter` | Einwohnerdichte nach Eurostat-Gitter, Einwohner je km² |
| `geb_anzahl` | BDOT10k: Gebäude (OT_BUBD_A) mit innerem Punkt in der Einheit, jeder Bestandsstatus |
| `geb_zustand_eksploatowany` | BDOT10k: Gebäude mit Bestandsstatus: in Nutzung (eksploatowany) |
| `geb_zustand_w_budowie` | BDOT10k: Gebäude mit Bestandsstatus: im Bau (w budowie) |
| `geb_zustand_nieczynny` | BDOT10k: Gebäude mit Bestandsstatus: außer Betrieb (nieczynny) |
| `geb_zustand_zniszczony` | BDOT10k: Gebäude mit Bestandsstatus: zerstört (zniszczony) |
| `geb_zustand_leer` | BDOT10k: Gebäude mit Bestandsstatus: ohne Angabe |
| `geb_funktion_101` | BDOT10k: Gebäude mit KŚT-Code 101: Industriegebäude |
| `geb_funktion_102` | BDOT10k: Gebäude mit KŚT-Code 102: Verkehrs- und Fernmeldegebäude |
| `geb_funktion_103` | BDOT10k: Gebäude mit KŚT-Code 103: Handels- und Dienstleistungsgebäude |
| `geb_funktion_104` | BDOT10k: Gebäude mit KŚT-Code 104: Behälter, Silos und Lagergebäude |
| `geb_funktion_105` | BDOT10k: Gebäude mit KŚT-Code 105: Bürogebäude |
| `geb_funktion_106` | BDOT10k: Gebäude mit KŚT-Code 106: Krankenhäuser und andere Gesundheitsbauten |
| `geb_funktion_107` | BDOT10k: Gebäude mit KŚT-Code 107: Bildungs-, Wissenschafts-, Kultur- und Sportgebäude |
| `geb_funktion_108` | BDOT10k: Gebäude mit KŚT-Code 108: landwirtschaftliche Betriebs- und Wirtschaftsgebäude |
| `geb_funktion_109` | BDOT10k: Gebäude mit KŚT-Code 109: sonstige Nichtwohngebäude |
| `geb_funktion_110` | BDOT10k: Gebäude mit KŚT-Code 110: Wohngebäude |
| `geb_funktion_unbekannt` | BDOT10k: Gebäude ohne KŚT-Code |
| `geb_wohngebaeude` | BDOT10k: Wohngebäude (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: Einfamilienhäuser (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: Mehrfamilienhäuser (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: sonstige Wohngebäude (PFBUD) |
| `geb_geschosse_1` | BDOT10k: Gebäude: 1 Geschoss |
| `geb_geschosse_2` | BDOT10k: Gebäude: 2 Geschosse |
| `geb_geschosse_3_4` | BDOT10k: Gebäude: 3–4 Geschosse |
| `geb_geschosse_5_10` | BDOT10k: Gebäude: 5–10 Geschosse |
| `geb_geschosse_11p` | BDOT10k: Gebäude: 11 und mehr Geschosse |
| `geb_geschosse_unbekannt` | BDOT10k: Gebäude: Geschosszahl unbekannt |
| `geb_geschosse_wohn_1` | BDOT10k: Wohngebäude: 1 Geschoss |
| `geb_geschosse_wohn_2` | BDOT10k: Wohngebäude: 2 Geschosse |
| `geb_geschosse_wohn_3_4` | BDOT10k: Wohngebäude: 3–4 Geschosse |
| `geb_geschosse_wohn_5_10` | BDOT10k: Wohngebäude: 5–10 Geschosse |
| `geb_geschosse_wohn_11p` | BDOT10k: Wohngebäude: 11 und mehr Geschosse |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: Wohngebäude: Geschosszahl unbekannt |
| `geb_geschosse_median` | BDOT10k: Median der oberirdischen Geschosse; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_mittel` | BDOT10k: Mittel der oberirdischen Geschosse; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_median_wohn` | BDOT10k: Median der oberirdischen Geschosse der Wohngebäude; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_mittel_wohn` | BDOT10k: Mittel der oberirdischen Geschosse der Wohngebäude; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_grundflaeche_m2` | BDOT10k: Summe der Grundflächen ohne zerstörte Gebäude, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: Summe der Grundflächen der Wohngebäude, m² |
| `geb_flaeche_m2` | Fläche der Einheit, m² |
| `geb_bebauungsdichte_wert` | Bebauungsdichte: 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | Zähler: Grundfläche der Gebäude, m² |
| `geb_bebauungsdichte_nenner` | Nenner: Fläche der Einheit, m² |
| `geb_bebauungsdichte_anzeige` | Darstellung des Werts |
| `geb_geschossflaeche_naeherung_wert` | Näherung der Geschossflächenzahl: Σ(Grundfläche × Geschosse) / Fläche; Orientierung, keine amtliche GFZ |
| `geb_geschossflaeche_naeherung_zaehler` | Zähler: Σ(Grundfläche × Geschosse), m² |
| `geb_geschossflaeche_naeherung_nenner` | Nenner: Fläche der Einheit, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | Kennzeichnung des Werts |
| `klimat_flaeche_ha` | Fläche der Einheit in der Stadtgrenze, ha |
| `klimat_abdeckung` | Anteil der Einheit, den die Bodenbedeckungsklassen der BDOT10k abdecken, % |
| `klimat_ha_bebauung` | BDOT10k: Fläche der Bodenbedeckungsklasse: Bebauung (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: Fläche der Bodenbedeckungsklasse: Verkehrsflächen und Plätze (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: Fläche der Bodenbedeckungsklasse: Grün (PTRK, PTUT, Grasland aus PTTR), ha |
| `klimat_ha_wald` | BDOT10k: Fläche der Bodenbedeckungsklasse: Wald und Gehölze (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: Fläche der Bodenbedeckungsklasse: Wasser (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: Fläche der Bodenbedeckungsklasse: Acker (Anbau aus PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: Fläche der Bodenbedeckungsklasse: Sonstiges (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Bebauung (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Verkehrsflächen und Plätze (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Grün (PTRK, PTUT, Grasland aus PTTR), % |
| `klimat_anteil_wald` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Wald und Gehölze (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Wasser (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Acker (Anbau aus PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Sonstiges (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Bebauung und Verkehr zusammen, % |
| `klimat_anteil_gruen_wald` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Grün und Wald zusammen, % |
| `klimat_gruen_je_ew` | Grün und Wald je Einwohner, m² |
| `typ_mfh` | Mehrfamilienhäuser in Nutzung (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `typ_blok` | Schätzung: Block-Kandidaten darunter (mindestens 4 Geschosse, Grundfläche mindestens 250 m², Rechteckigkeit mindestens 0,85); einschließlich osiedle |
| `typ_osiedle` | Schätzung: Block-Kandidaten in einer Großsiedlung (mindestens 9 weitere Kandidaten im Umkreis von 150 m) |
| `typ_blok_angebaut` | Hinweis, keine Regel: Block-Kandidaten mit mindestens 3 m gemeinsamer Grenze zu einem anderen BDOT10k-Gebäude (Blockrand, typisch für kamienice) |
| `typ_osiedle_angebaut` | wie blok_angebaut, nur Kandidaten in einer Großsiedlung |

### `delegatury`

| Feld | Bedeutung |
|---|---|
| `gruppe` | Nummer der delegatura im Atlas: 1 = Kraków-Śródmieście, 2 = Kraków-Krowodrza, 3 = Kraków-Podgórze, 4 = Kraków-Nowa Huta |
| `teryt` | TERYT-Kennung |
| `nazwa` | Name (polnischer Eigenname) |
| `flaeche_km2` | Fläche, km² |
| `flaeche_quelle` | Quelle der Fläche |
| `nsp_einwohner` | NSP 2021: Einwohner |
| `nsp_maenner` | NSP 2021: Männer |
| `nsp_frauen` | NSP 2021: Frauen |
| `nsp_alter_10_a0_9` | NSP 2021: Einwohner von 0 bis 9 Jahren |
| `nsp_alter_10_a10_19` | NSP 2021: Einwohner von 10 bis 19 Jahren |
| `nsp_alter_10_a20_29` | NSP 2021: Einwohner von 20 bis 29 Jahren |
| `nsp_alter_10_a30_39` | NSP 2021: Einwohner von 30 bis 39 Jahren |
| `nsp_alter_10_a40_49` | NSP 2021: Einwohner von 40 bis 49 Jahren |
| `nsp_alter_10_a50_59` | NSP 2021: Einwohner von 50 bis 59 Jahren |
| `nsp_alter_10_a60_69` | NSP 2021: Einwohner von 60 bis 69 Jahren |
| `nsp_alter_10_a70_79` | NSP 2021: Einwohner von 70 bis 79 Jahren |
| `nsp_alter_10_a80p` | NSP 2021: Einwohner ab 80 Jahren |
| `nsp_oekonomisch_vor` | NSP 2021: Einwohner im vorerwerbsfähigen Alter |
| `nsp_oekonomisch_erwerb` | NSP 2021: Einwohner im erwerbsfähigen Alter |
| `nsp_oekonomisch_nach` | NSP 2021: Einwohner im nacherwerbsfähigen Alter |
| `nsp_q_u20` | NSP 2021: Anteil unter 20 Jahren, % |
| `nsp_q_60p` | NSP 2021: Anteil ab 60 Jahren, % |
| `nsp_q_nach` | NSP 2021: Anteil im nacherwerbsfähigen Alter, % |
| `nsp_rejony` | NSP 2021: Zahl der rejony statystyczne |
| `nsp_weg` | Herkunft der Werte aus dem NSP 2021 |
| `gitter_zellen` | Eurostat-Gitter: Zahl der 1-km-Zellen mit Mittelpunkt in der Einheit |
| `gitter_einwohner` | Eurostat-Gitter: Einwohner (Summe der Zellen nach ihrem Mittelpunkt) |
| `gitter_u15` | Eurostat-Gitter: Einwohner unter 15 Jahren |
| `gitter_a15_64` | Eurostat-Gitter: Einwohner von 15 bis 64 Jahren |
| `gitter_a65p` | Eurostat-Gitter: Einwohner ab 65 Jahren |
| `gitter_a_ges` | Eurostat-Gitter: Summe der drei Altersgruppen (kann leicht von den Einwohnern abweichen) |
| `gitter_q_u15` | Eurostat-Gitter: Anteil unter 15 Jahren an der Summe der Altersgruppen, % |
| `gitter_q_65p` | Eurostat-Gitter: Anteil ab 65 Jahren an der Summe der Altersgruppen, % |
| `gitter_einwohner_flaechenanteil` | Eurostat-Gitter: Einwohner nach Flächenanteil der Zellen (Vergleich) |
| `gitter_abweichung_nsp_proz` | Abweichung der Gitter-Einwohner vom NSP 2021, %; leer ohne NSP |
| `dichte_nsp` | Einwohnerdichte nach NSP 2021, Einwohner je km² |
| `dichte_gitter` | Einwohnerdichte nach Eurostat-Gitter, Einwohner je km² |
| `geb_anzahl` | BDOT10k: Gebäude (OT_BUBD_A) mit innerem Punkt in der Einheit, jeder Bestandsstatus |
| `geb_zustand_eksploatowany` | BDOT10k: Gebäude mit Bestandsstatus: in Nutzung (eksploatowany) |
| `geb_zustand_w_budowie` | BDOT10k: Gebäude mit Bestandsstatus: im Bau (w budowie) |
| `geb_zustand_nieczynny` | BDOT10k: Gebäude mit Bestandsstatus: außer Betrieb (nieczynny) |
| `geb_zustand_zniszczony` | BDOT10k: Gebäude mit Bestandsstatus: zerstört (zniszczony) |
| `geb_zustand_leer` | BDOT10k: Gebäude mit Bestandsstatus: ohne Angabe |
| `geb_funktion_101` | BDOT10k: Gebäude mit KŚT-Code 101: Industriegebäude |
| `geb_funktion_102` | BDOT10k: Gebäude mit KŚT-Code 102: Verkehrs- und Fernmeldegebäude |
| `geb_funktion_103` | BDOT10k: Gebäude mit KŚT-Code 103: Handels- und Dienstleistungsgebäude |
| `geb_funktion_104` | BDOT10k: Gebäude mit KŚT-Code 104: Behälter, Silos und Lagergebäude |
| `geb_funktion_105` | BDOT10k: Gebäude mit KŚT-Code 105: Bürogebäude |
| `geb_funktion_106` | BDOT10k: Gebäude mit KŚT-Code 106: Krankenhäuser und andere Gesundheitsbauten |
| `geb_funktion_107` | BDOT10k: Gebäude mit KŚT-Code 107: Bildungs-, Wissenschafts-, Kultur- und Sportgebäude |
| `geb_funktion_108` | BDOT10k: Gebäude mit KŚT-Code 108: landwirtschaftliche Betriebs- und Wirtschaftsgebäude |
| `geb_funktion_109` | BDOT10k: Gebäude mit KŚT-Code 109: sonstige Nichtwohngebäude |
| `geb_funktion_110` | BDOT10k: Gebäude mit KŚT-Code 110: Wohngebäude |
| `geb_funktion_unbekannt` | BDOT10k: Gebäude ohne KŚT-Code |
| `geb_wohngebaeude` | BDOT10k: Wohngebäude (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: Einfamilienhäuser (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: Mehrfamilienhäuser (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: sonstige Wohngebäude (PFBUD) |
| `geb_geschosse_1` | BDOT10k: Gebäude: 1 Geschoss |
| `geb_geschosse_2` | BDOT10k: Gebäude: 2 Geschosse |
| `geb_geschosse_3_4` | BDOT10k: Gebäude: 3–4 Geschosse |
| `geb_geschosse_5_10` | BDOT10k: Gebäude: 5–10 Geschosse |
| `geb_geschosse_11p` | BDOT10k: Gebäude: 11 und mehr Geschosse |
| `geb_geschosse_unbekannt` | BDOT10k: Gebäude: Geschosszahl unbekannt |
| `geb_geschosse_wohn_1` | BDOT10k: Wohngebäude: 1 Geschoss |
| `geb_geschosse_wohn_2` | BDOT10k: Wohngebäude: 2 Geschosse |
| `geb_geschosse_wohn_3_4` | BDOT10k: Wohngebäude: 3–4 Geschosse |
| `geb_geschosse_wohn_5_10` | BDOT10k: Wohngebäude: 5–10 Geschosse |
| `geb_geschosse_wohn_11p` | BDOT10k: Wohngebäude: 11 und mehr Geschosse |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: Wohngebäude: Geschosszahl unbekannt |
| `geb_geschosse_median` | BDOT10k: Median der oberirdischen Geschosse; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_mittel` | BDOT10k: Mittel der oberirdischen Geschosse; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_median_wohn` | BDOT10k: Median der oberirdischen Geschosse der Wohngebäude; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_mittel_wohn` | BDOT10k: Mittel der oberirdischen Geschosse der Wohngebäude; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_grundflaeche_m2` | BDOT10k: Summe der Grundflächen ohne zerstörte Gebäude, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: Summe der Grundflächen der Wohngebäude, m² |
| `geb_flaeche_m2` | Fläche der Einheit, m² |
| `geb_bebauungsdichte_wert` | Bebauungsdichte: 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | Zähler: Grundfläche der Gebäude, m² |
| `geb_bebauungsdichte_nenner` | Nenner: Fläche der Einheit, m² |
| `geb_bebauungsdichte_anzeige` | Darstellung des Werts |
| `geb_geschossflaeche_naeherung_wert` | Näherung der Geschossflächenzahl: Σ(Grundfläche × Geschosse) / Fläche; Orientierung, keine amtliche GFZ |
| `geb_geschossflaeche_naeherung_zaehler` | Zähler: Σ(Grundfläche × Geschosse), m² |
| `geb_geschossflaeche_naeherung_nenner` | Nenner: Fläche der Einheit, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | Kennzeichnung des Werts |
| `klimat_flaeche_ha` | Fläche der Einheit in der Stadtgrenze, ha |
| `klimat_abdeckung` | Anteil der Einheit, den die Bodenbedeckungsklassen der BDOT10k abdecken, % |
| `klimat_ha_bebauung` | BDOT10k: Fläche der Bodenbedeckungsklasse: Bebauung (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: Fläche der Bodenbedeckungsklasse: Verkehrsflächen und Plätze (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: Fläche der Bodenbedeckungsklasse: Grün (PTRK, PTUT, Grasland aus PTTR), ha |
| `klimat_ha_wald` | BDOT10k: Fläche der Bodenbedeckungsklasse: Wald und Gehölze (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: Fläche der Bodenbedeckungsklasse: Wasser (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: Fläche der Bodenbedeckungsklasse: Acker (Anbau aus PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: Fläche der Bodenbedeckungsklasse: Sonstiges (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Bebauung (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Verkehrsflächen und Plätze (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Grün (PTRK, PTUT, Grasland aus PTTR), % |
| `klimat_anteil_wald` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Wald und Gehölze (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Wasser (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Acker (Anbau aus PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Sonstiges (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Bebauung und Verkehr zusammen, % |
| `klimat_anteil_gruen_wald` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Grün und Wald zusammen, % |
| `typ_mfh` | Mehrfamilienhäuser in Nutzung (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `typ_blok` | Schätzung: Block-Kandidaten darunter (mindestens 4 Geschosse, Grundfläche mindestens 250 m², Rechteckigkeit mindestens 0,85); einschließlich osiedle |
| `typ_osiedle` | Schätzung: Block-Kandidaten in einer Großsiedlung (mindestens 9 weitere Kandidaten im Umkreis von 150 m) |
| `typ_blok_angebaut` | Hinweis, keine Regel: Block-Kandidaten mit mindestens 3 m gemeinsamer Grenze zu einem anderen BDOT10k-Gebäude (Blockrand, typisch für kamienice) |
| `typ_osiedle_angebaut` | wie blok_angebaut, nur Kandidaten in einer Großsiedlung |
| `bdot_wohngebaeude` | BDOT10k: Wohngebäude (FOBUD) |
| `bdot_mehrfamilienhaeuser` | BDOT10k: Mehrfamilienhäuser (PFBUD) |
| `bdot_namensbezug` | BDOT10k: Gebäude mit dem Namen „Kamienica …“ |

### `siatka_1km`

| Feld | Bedeutung |
|---|---|
| `id` | Kennung der 1-km-Zelle im Eurostat-Gitter (EPSG:3035, Südwestecke) |
| `ew` | Einwohner (Eurostat-Gitter 2021) |
| `a_ges` | Summe der drei Altersgruppen der Zelle |
| `q_u15` | Anteil unter 15 Jahren, % |
| `q_65p` | Anteil ab 65 Jahren, % |
| `luftlinie_m_haltestelle_takt` | Luftlinie vom Mittelpunkt der Zelle zum nächsten Ziel: Haltestelle der Taktklasse I oder II, m |
| `luftlinie_m_park` | Luftlinie vom Mittelpunkt der Zelle zum nächsten Ziel: Park oder Grünanlage (BDOT10k, park lub skwer), m |
| `luftlinie_m_przedszkole` | Luftlinie vom Mittelpunkt der Zelle zum nächsten Ziel: Kindergarten (przedszkole), m |
| `luftlinie_m_szkola` | Luftlinie vom Mittelpunkt der Zelle zum nächsten Ziel: Schule jeder Art (BDOT10k trennt nicht), m |
| `luftlinie_m_szpital` | Luftlinie vom Mittelpunkt der Zelle zum nächsten Ziel: Krankenhaus (szpital), m |
| `luftlinie_m_zlobek` | Luftlinie vom Mittelpunkt der Zelle zum nächsten Ziel: Krippe (żłobek), m |
| `wkt` | Geometrie als WKT in EPSG:2178 |

### `siatka_1km_pokrycie`

| Feld | Bedeutung |
|---|---|
| `id` | Kennung der 1-km-Zelle im Eurostat-Gitter (EPSG:3035, Südwestecke) |
| `flaeche_stadt_ha` | Fläche der Zelle in der Stadtgrenze, ha |
| `anteil_stadt` | Anteil der Zelle in der Stadtgrenze, % |
| `abdeckung` | Anteil der Einheit, den die Bodenbedeckungsklassen der BDOT10k abdecken, % |
| `ha_bebauung` | BDOT10k: Fläche der Bodenbedeckungsklasse: Bebauung (PTZB), ha |
| `ha_verkehr` | BDOT10k: Fläche der Bodenbedeckungsklasse: Verkehrsflächen und Plätze (PTKM, PTPL), ha |
| `ha_gruen` | BDOT10k: Fläche der Bodenbedeckungsklasse: Grün (PTRK, PTUT, Grasland aus PTTR), ha |
| `ha_wald` | BDOT10k: Fläche der Bodenbedeckungsklasse: Wald und Gehölze (PTLZ), ha |
| `ha_wasser` | BDOT10k: Fläche der Bodenbedeckungsklasse: Wasser (PTWP), ha |
| `ha_acker` | BDOT10k: Fläche der Bodenbedeckungsklasse: Acker (Anbau aus PTTR), ha |
| `ha_sonstige` | BDOT10k: Fläche der Bodenbedeckungsklasse: Sonstiges (PTGN, PTSO, PTWZ, PTNZ), ha |
| `anteil` | technisches Feld, immer leer; die Anteile stehen in den Spalten anteil_* |
| `anteil_grund` | Grund für leere Anteile (Fläche in der Stadt unter 10 ha) |
| `anteil_bebauung` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Bebauung (PTZB), % |
| `anteil_verkehr` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Verkehrsflächen und Plätze (PTKM, PTPL), % |
| `anteil_gruen` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Grün (PTRK, PTUT, Grasland aus PTTR), % |
| `anteil_wald` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Wald und Gehölze (PTLZ), % |
| `anteil_wasser` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Wasser (PTWP), % |
| `anteil_acker` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Acker (Anbau aus PTTR), % |
| `anteil_sonstige` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Sonstiges (PTGN, PTSO, PTWZ, PTNZ), % |
| `anteil_bebauung_verkehr` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Bebauung und Verkehr zusammen, % |
| `anteil_gruen_wald` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Grün und Wald zusammen, % |
| `wkt` | Geometrie als WKT in EPSG:2178 |

### `rejony_statystyczne`

| Feld | Bedeutung |
|---|---|
| `rejon` | Kennung des statistischen Bezirks des GUS (6 Ziffern) |
| `delegatura_teryt` | TERYT-Kennung der delegatura laut GUS |
| `nsp_einwohner` | NSP 2021: Einwohner des Bezirks; leer = keine Zeile in der Zensustabelle |
| `flaeche_km2` | Fläche, km² |
| `dichte_nsp` | Einwohnerdichte nach NSP 2021, Einwohner je km² |
| `nsp_q_u20` | NSP 2021: Anteil unter 20 Jahren, ganze %; leer unter 100 Personen |
| `nsp_q_60p` | NSP 2021: Anteil ab 60 Jahren, ganze %; leer unter 100 Personen |
| `nsp_q_nach` | NSP 2021: Anteil im nacherwerbsfähigen Alter, ganze %; leer unter 100 Personen |
| `ohne_zeile` | 1 = Bezirk ohne Zeile in der Zensustabelle (ohne Werte) |
| `wkt` | Geometrie als WKT in EPSG:2178 |

### `placowki_bdot`

| Feld | Bedeutung |
|---|---|
| `id` | Objektkennung in BDOT10k (LOKALNYID) |
| `art` | Art der Einrichtung |
| `unterart` | Unterart: leer (nicht in BDOT10k) |
| `q` | Quelle (Schlüssel in der Tabelle licencje) |
| `name` | Name der Einrichtung aus BDOT10k (amtlich, kein Personenname) |
| `plaetze` | Plätze: leer (nicht in BDOT10k) |
| `schueler` | Schüler: leer (nicht in BDOT10k) |
| `schueler_stand` | Stand der Schülerzahl: leer |
| `status` | Umfang der Angaben zur Einrichtung |
| `in_stadt` | in der Gemeinde Kraków (BDOT10k); 1 = ja, 0 = nein |
| `x` | x-Koordinate (Ost) in EPSG:2178, m |
| `y` | y-Koordinate (Nord) in EPSG:2178, m |

### `przystanki`

| Feld | Bedeutung |
|---|---|
| `id` | Stamm des Haltestellen-Codes der ZTP (stop_code vor dem Bindestrich) |
| `name` | Name der Haltestelle (stop_name) |
| `verkehrsmittel` | Verkehrsmittel mit Abfahrten am Zähltag |
| `fahrten_hvz_je_richtung` | Abfahrten je Stunde im Fenster 06:00–09:00, stärkere Richtung |
| `taktklasse` | Taktklasse (eigene Klassifikation, keine Norm) |
| `in_stadt` | in der Gemeinde Kraków (BDOT10k); 1 = ja, 0 = nein |
| `x` | x-Koordinate (Ost) in EPSG:2178, m |
| `y` | y-Koordinate (Nord) in EPSG:2178, m |

### `bdot_kompleksy`

| Feld | Bedeutung |
|---|---|
| `r` | Art des Komplexes (BDOT10k RODZAJ) |
| `n` | Name des Komplexes (BDOT10k NAZWA) |
| `del` | delegatura (Name aus BDOT10k); leer = nicht zugeordnet |
| `wkt` | Geometrie als WKT in EPSG:2178 |

### `bdot_kamienica_nazwa`

| Feld | Bedeutung |
|---|---|
| `w` | Wohngebäude (FOBUD); leer = kein Gebäude; 1 = ja, 0 = nein |
| `mfh` | Mehrfamilienhaus (PFBUD); leer = kein Gebäude; 1 = ja, 0 = nein |
| `gs` | oberirdische Geschosse (BDOT10k LICZ_KONDY) |
| `del` | delegatura (Name aus BDOT10k); leer = nicht zugeordnet |
| `x` | x-Koordinate (Ost) in EPSG:2178, m |
| `y` | y-Koordinate (Nord) in EPSG:2178, m |

### `rejestr_zabytkow`

| Feld | Bedeutung |
|---|---|
| `q` | Quelle des Punkts (wd = Wikidata, nid = NID-Register, gez = gminna ewidencja zabytków; mehrere durch Komma) |
| `ep` | Bauzeitklasse aus dem Entstehungsdatum in Wikidata (nie ein Einzeljahr); leer = keines oder mehrdeutig |
| `w` | Wohngebäude (FOBUD); leer = kein Gebäude; 1 = ja, 0 = nein |
| `mfh` | Mehrfamilienhaus (PFBUD); leer = kein Gebäude; 1 = ja, 0 = nein |
| `del` | delegatura (Name aus BDOT10k); leer = nicht zugeordnet |
| `polozenie_sprawdzone` | Lage dieses Punkts einzeln am Luftbild geprüft (überall 0: geprüft ist höchstens eine Zufallsstichprobe der Ebene, Ergebnis in LIESMICH.md); 1 = ja, 0 = nein |
| `x` | x-Koordinate (Ost) in EPSG:2178, m |
| `y` | y-Koordinate (Nord) in EPSG:2178, m |

### `zbk_wykaz_dzielnice`

| Feld | Bedeutung |
|---|---|
| `dzielnica_z_wykazu` | dzielnica laut ZBK-Liste (Nummer 01–18; poza = außerhalb Krakóws) |
| `n` | Zahl der Einträge (ein Eintrag ist nicht immer ein Gebäude) |
| `art_M` | Einträge der Art: Wohnen (M) |
| `art_MP` | Einträge der Art: Wohnen und Ambulanz (MP) |
| `art_MU` | Einträge der Art: Wohnen und Nutzung (MU) |
| `art_MUP` | Einträge der Art: Wohnen, Nutzung und Ambulanz (MUP) |
| `art_P` | Einträge der Art: Ambulanz (P) |
| `art_U` | Einträge der Art: Nutzung ohne Wohnen (U) |
| `eigentum_gmina` | Einträge, Eigentum: Stadt Kraków (Gmina Miejska Kraków) |
| `eigentum_skarb_panstwa` | Einträge, Eigentum: Staatskasse (Skarb Państwa) |
| `eigentum_publiczne_mieszane` | Einträge, Eigentum: mehrere öffentliche Eigentümer oder die Woiwodschaft |
| `eigentum_z_prywatnymi` | Einträge, Eigentum: öffentlich mit privaten Miteigentümern |
| `eigentum_prywatne` | Einträge, Eigentum: nur private Eigentümer |
| `eigentum_brak` | Einträge, Eigentum: Eigentum nicht zuzuordnen |
| `art_UP` | Einträge der Art: Nutzung und Ambulanz (UP) |

### `dzielnice`

| Feld | Bedeutung |
|---|---|
| `nr` | Nummer der dzielnica (01–18) |
| `rzymska` | Nummer der dzielnica in römischen Ziffern |
| `nazwa` | Name (polnischer Eigenname) |
| `gruppe` | delegatura, zu der die dzielnica gehört: 1 = Kraków-Śródmieście, 2 = Kraków-Krowodrza, 3 = Kraków-Podgórze, 4 = Kraków-Nowa Huta |
| `flaeche_km2` | Fläche, km² |
| `osm_id` | Grenzrelation in OpenStreetMap |
| `gitter_zellen` | Eurostat-Gitter: Zahl der 1-km-Zellen mit Mittelpunkt in der Einheit |
| `gitter_einwohner` | Eurostat-Gitter: Einwohner (Summe der Zellen nach ihrem Mittelpunkt) |
| `gitter_u15` | Eurostat-Gitter: Einwohner unter 15 Jahren |
| `gitter_a15_64` | Eurostat-Gitter: Einwohner von 15 bis 64 Jahren |
| `gitter_a65p` | Eurostat-Gitter: Einwohner ab 65 Jahren |
| `gitter_a_ges` | Eurostat-Gitter: Summe der drei Altersgruppen (kann leicht von den Einwohnern abweichen) |
| `gitter_q_u15` | Eurostat-Gitter: Anteil unter 15 Jahren an der Summe der Altersgruppen, % |
| `gitter_q_65p` | Eurostat-Gitter: Anteil ab 65 Jahren an der Summe der Altersgruppen, % |
| `gitter_einwohner_flaechenanteil` | Eurostat-Gitter: Einwohner nach Flächenanteil der Zellen (Vergleich) |
| `gitter_abweichung_nsp_proz` | Abweichung der Gitter-Einwohner vom NSP 2021, %; leer ohne NSP |
| `gitter_zellen_beruehrt` | Zahl der Zellen, die wenigstens teilweise in der Einheit liegen |
| `gitter_spanne_proz` | Spanne zwischen Flächenanteil und Mittelpunkt, % (Unschärfe an den Grenzen, kein Fehler) |
| `dichte_gitter` | Einwohnerdichte nach Eurostat-Gitter, Einwohner je km² |
| `nsp_einwohner` | NSP 2021: Einwohner |
| `nsp_maenner` | NSP 2021: Männer |
| `nsp_frauen` | NSP 2021: Frauen |
| `nsp_alter_10_a0_9` | NSP 2021: Einwohner von 0 bis 9 Jahren |
| `nsp_alter_10_a10_19` | NSP 2021: Einwohner von 10 bis 19 Jahren |
| `nsp_alter_10_a20_29` | NSP 2021: Einwohner von 20 bis 29 Jahren |
| `nsp_alter_10_a30_39` | NSP 2021: Einwohner von 30 bis 39 Jahren |
| `nsp_alter_10_a40_49` | NSP 2021: Einwohner von 40 bis 49 Jahren |
| `nsp_alter_10_a50_59` | NSP 2021: Einwohner von 50 bis 59 Jahren |
| `nsp_alter_10_a60_69` | NSP 2021: Einwohner von 60 bis 69 Jahren |
| `nsp_alter_10_a70_79` | NSP 2021: Einwohner von 70 bis 79 Jahren |
| `nsp_alter_10_a80p` | NSP 2021: Einwohner ab 80 Jahren |
| `nsp_oekonomisch_vor` | NSP 2021: Einwohner im vorerwerbsfähigen Alter |
| `nsp_oekonomisch_erwerb` | NSP 2021: Einwohner im erwerbsfähigen Alter |
| `nsp_oekonomisch_nach` | NSP 2021: Einwohner im nacherwerbsfähigen Alter |
| `nsp_q_u20` | NSP 2021: Anteil unter 20 Jahren, % |
| `nsp_q_60p` | NSP 2021: Anteil ab 60 Jahren, % |
| `nsp_q_nach` | NSP 2021: Anteil im nacherwerbsfähigen Alter, % |
| `nsp_rejony` | NSP 2021: Zahl der rejony statystyczne |
| `nsp_weg` | Herkunft der Werte aus dem NSP 2021 |
| `dichte_nsp` | Einwohnerdichte nach NSP 2021, Einwohner je km² |
| `geb_anzahl` | BDOT10k: Gebäude (OT_BUBD_A) mit innerem Punkt in der Einheit, jeder Bestandsstatus |
| `geb_zustand_eksploatowany` | BDOT10k: Gebäude mit Bestandsstatus: in Nutzung (eksploatowany) |
| `geb_zustand_w_budowie` | BDOT10k: Gebäude mit Bestandsstatus: im Bau (w budowie) |
| `geb_zustand_nieczynny` | BDOT10k: Gebäude mit Bestandsstatus: außer Betrieb (nieczynny) |
| `geb_zustand_zniszczony` | BDOT10k: Gebäude mit Bestandsstatus: zerstört (zniszczony) |
| `geb_zustand_leer` | BDOT10k: Gebäude mit Bestandsstatus: ohne Angabe |
| `geb_funktion_101` | BDOT10k: Gebäude mit KŚT-Code 101: Industriegebäude |
| `geb_funktion_102` | BDOT10k: Gebäude mit KŚT-Code 102: Verkehrs- und Fernmeldegebäude |
| `geb_funktion_103` | BDOT10k: Gebäude mit KŚT-Code 103: Handels- und Dienstleistungsgebäude |
| `geb_funktion_104` | BDOT10k: Gebäude mit KŚT-Code 104: Behälter, Silos und Lagergebäude |
| `geb_funktion_105` | BDOT10k: Gebäude mit KŚT-Code 105: Bürogebäude |
| `geb_funktion_106` | BDOT10k: Gebäude mit KŚT-Code 106: Krankenhäuser und andere Gesundheitsbauten |
| `geb_funktion_107` | BDOT10k: Gebäude mit KŚT-Code 107: Bildungs-, Wissenschafts-, Kultur- und Sportgebäude |
| `geb_funktion_108` | BDOT10k: Gebäude mit KŚT-Code 108: landwirtschaftliche Betriebs- und Wirtschaftsgebäude |
| `geb_funktion_109` | BDOT10k: Gebäude mit KŚT-Code 109: sonstige Nichtwohngebäude |
| `geb_funktion_110` | BDOT10k: Gebäude mit KŚT-Code 110: Wohngebäude |
| `geb_funktion_unbekannt` | BDOT10k: Gebäude ohne KŚT-Code |
| `geb_wohngebaeude` | BDOT10k: Wohngebäude (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: Einfamilienhäuser (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: Mehrfamilienhäuser (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: sonstige Wohngebäude (PFBUD) |
| `geb_geschosse_1` | BDOT10k: Gebäude: 1 Geschoss |
| `geb_geschosse_2` | BDOT10k: Gebäude: 2 Geschosse |
| `geb_geschosse_3_4` | BDOT10k: Gebäude: 3–4 Geschosse |
| `geb_geschosse_5_10` | BDOT10k: Gebäude: 5–10 Geschosse |
| `geb_geschosse_11p` | BDOT10k: Gebäude: 11 und mehr Geschosse |
| `geb_geschosse_unbekannt` | BDOT10k: Gebäude: Geschosszahl unbekannt |
| `geb_geschosse_wohn_1` | BDOT10k: Wohngebäude: 1 Geschoss |
| `geb_geschosse_wohn_2` | BDOT10k: Wohngebäude: 2 Geschosse |
| `geb_geschosse_wohn_3_4` | BDOT10k: Wohngebäude: 3–4 Geschosse |
| `geb_geschosse_wohn_5_10` | BDOT10k: Wohngebäude: 5–10 Geschosse |
| `geb_geschosse_wohn_11p` | BDOT10k: Wohngebäude: 11 und mehr Geschosse |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: Wohngebäude: Geschosszahl unbekannt |
| `geb_geschosse_median` | BDOT10k: Median der oberirdischen Geschosse; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_mittel` | BDOT10k: Mittel der oberirdischen Geschosse; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_median_wohn` | BDOT10k: Median der oberirdischen Geschosse der Wohngebäude; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_geschosse_mittel_wohn` | BDOT10k: Mittel der oberirdischen Geschosse der Wohngebäude; leer unter 30 Gebäuden mit bekannter Geschosszahl |
| `geb_grundflaeche_m2` | BDOT10k: Summe der Grundflächen ohne zerstörte Gebäude, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: Summe der Grundflächen der Wohngebäude, m² |
| `geb_flaeche_m2` | Fläche der Einheit, m² |
| `geb_bebauungsdichte_wert` | Bebauungsdichte: 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | Zähler: Grundfläche der Gebäude, m² |
| `geb_bebauungsdichte_nenner` | Nenner: Fläche der Einheit, m² |
| `geb_bebauungsdichte_anzeige` | Darstellung des Werts |
| `geb_geschossflaeche_naeherung_wert` | Näherung der Geschossflächenzahl: Σ(Grundfläche × Geschosse) / Fläche; Orientierung, keine amtliche GFZ |
| `geb_geschossflaeche_naeherung_zaehler` | Zähler: Σ(Grundfläche × Geschosse), m² |
| `geb_geschossflaeche_naeherung_nenner` | Nenner: Fläche der Einheit, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | Kennzeichnung des Werts |
| `klimat_flaeche_ha` | Fläche der Einheit in der Stadtgrenze, ha |
| `klimat_abdeckung` | Anteil der Einheit, den die Bodenbedeckungsklassen der BDOT10k abdecken, % |
| `klimat_ha_bebauung` | BDOT10k: Fläche der Bodenbedeckungsklasse: Bebauung (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: Fläche der Bodenbedeckungsklasse: Verkehrsflächen und Plätze (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: Fläche der Bodenbedeckungsklasse: Grün (PTRK, PTUT, Grasland aus PTTR), ha |
| `klimat_ha_wald` | BDOT10k: Fläche der Bodenbedeckungsklasse: Wald und Gehölze (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: Fläche der Bodenbedeckungsklasse: Wasser (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: Fläche der Bodenbedeckungsklasse: Acker (Anbau aus PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: Fläche der Bodenbedeckungsklasse: Sonstiges (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Bebauung (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Verkehrsflächen und Plätze (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Grün (PTRK, PTUT, Grasland aus PTTR), % |
| `klimat_anteil_wald` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Wald und Gehölze (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Wasser (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Acker (Anbau aus PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Sonstiges (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Bebauung und Verkehr zusammen, % |
| `klimat_anteil_gruen_wald` | BDOT10k: Anteil an der Summe der Bodenbedeckung: Grün und Wald zusammen, % |
| `klimat_einwohner` | Einwohner aus dem Eurostat-Gitter, Bezug für Grün je Einwohner |
| `klimat_gruen_je_ew` | Grün und Wald je Einwohner, m² |
| `wkt` | Geometrie als WKT in EPSG:2178 |

### `siatka_1km_odbl`

| Feld | Bedeutung |
|---|---|
| `id` | Kennung der 1-km-Zelle im Eurostat-Gitter (EPSG:3035, Südwestecke) |
| `st` | dzielnica nach dem Mittelpunkt der Zelle (OSM-Grenzen) |
| `ew` | Einwohner (Eurostat-Gitter 2021) |
| `a_ges` | Summe der drei Altersgruppen der Zelle |
| `q_u15` | Anteil unter 15 Jahren, % |
| `q_65p` | Anteil ab 65 Jahren, % |
| `fussweg_m_apotheke` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Apotheke (OSM), m |
| `fussweg_m_arzt` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Arzt oder Praxis (OSM amenity=doctors), m |
| `fussweg_m_haltestelle_takt` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Haltestelle der Taktklasse I oder II, m |
| `fussweg_m_park` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Park oder Grünanlage (BDOT10k, park lub skwer), m |
| `fussweg_m_pflege` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Pflegeheim (OSM), m |
| `fussweg_m_przedszkole` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Kindergarten (przedszkole), m |
| `fussweg_m_spielplatz` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: öffentlicher Spielplatz (OSM), m |
| `fussweg_m_supermarkt` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Supermarkt oder Lebensmittelladen (OSM), m |
| `fussweg_m_szkola` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Schule jeder Art (BDOT10k trennt nicht), m |
| `fussweg_m_szpital` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Krankenhaus (szpital), m |
| `fussweg_m_zlobek` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: Krippe (żłobek), m |
| `wkt` | Geometrie als WKT in EPSG:2178 |

### `dostepnosc`

| Feld | Bedeutung |
|---|---|
| `st` | dzielnica (01–18); leer = ganze Stadt |
| `nazwa` | Name der dzielnica oder der Stadt |
| `ew` | Einwohner des Gebiets (Eurostat-Gitter, gerundet) |
| `kennzahl` | Kennzahl |
| `art` | Art des Ziels |
| `methode` | Art der Entfernungsmessung |
| `einheit` | Einheit des Werts |
| `status` | Status des Werts |
| `vorlaeufig` | 1 = vorläufig (Schulen ohne Schulbezirke); leer = trifft nicht zu |
| `q` | Quelle (Schlüssel in der Tabelle licencje) |
| `richtwert_wert` | Radius aus der amtlichen Vorgabe, mit der verglichen wird |
| `richtwert_einheit` | Einheit des Radius |
| `richtwert_q` | Quelle der Vorgabe (Schlüssel in der Tabelle licencje) |
| `richtwert_seite` | Fundstelle im Gesetz (Artikel, Seite) |
| `radius_m` | Radius in Metern, in dem gezählt wurde (Anteil im Radius, Haltestellen, Parks); leer = trifft nicht zu |
| `wert` | Wert der Kennzahl; leer unter der Geheimhaltungsschwelle |
| `zaehler` | Zähler der Kennzahl (z. B. Einwohner im Radius, Parkfläche) |
| `nenner` | Nenner der Kennzahl (z. B. Einwohner, Zahl der Einrichtungen) |
| `stand` | Datenstand (Datum) |

### `placowki_osm`

| Feld | Bedeutung |
|---|---|
| `id` | OSM-Kennung (n = Knoten, w = Weg oder Fläche) |
| `art` | Art der Einrichtung |
| `unterart` | Fachrichtung aus dem OSM-Tag healthcare:speciality (OSM-Werte, englisch); leer = ohne Tag |
| `q` | Quelle (Schlüssel in der Tabelle licencje) |
| `x` | x-Koordinate (Ost) in EPSG:2178, m |
| `y` | y-Koordinate (Nord) in EPSG:2178, m |

### `osm_heritage_start_date`

| Feld | Bedeutung |
|---|---|
| `h` | Objekt trägt heritage; 1 = ja, 0 = nein |
| `ep` | Bauzeitklasse aus start_date (nie ein Einzeljahr); leer = keine oder mehrdeutig |
| `w` | Wohngebäude (FOBUD); leer = kein Gebäude; 1 = ja, 0 = nein |
| `mfh` | Mehrfamilienhaus (PFBUD); leer = kein Gebäude; 1 = ja, 0 = nein |
| `del` | delegatura (Name aus BDOT10k); leer = nicht zugeordnet |
| `polozenie_sprawdzone` | Lage dieses Punkts einzeln am Luftbild geprüft (überall 0: geprüft ist höchstens eine Zufallsstichprobe der Ebene, Ergebnis in LIESMICH.md); 1 = ja, 0 = nein |
| `x` | x-Koordinate (Ost) in EPSG:2178, m |
| `y` | y-Koordinate (Nord) in EPSG:2178, m |

### `zbk_budynki`

| Feld | Bedeutung |
|---|---|
| `art` | Art des Gebäudes laut ZBK-Liste |
| `eig` | Eigentum laut ZBK-Liste (Punkte nur ohne private Eigentümer) |
| `st` | dzielnica laut ZBK-Liste |
| `gs` | oberirdische Geschosse (BDOT10k LICZ_KONDY) |
| `fn` | überwiegende Funktion des verknüpften BDOT10k-Gebäudes (PFBUD); leer = keine |
| `h` | Gebäudehöhe, m (siehe hq) |
| `hq` | Herkunft der Höhe |
| `typ` | Typologie (Schätzung); leer = kein Kandidat |
| `x` | x-Koordinate (Ost) in EPSG:2178, m |
| `y` | y-Koordinate (Nord) in EPSG:2178, m |

### `zbk_typologia_dzielnice`

| Feld | Bedeutung |
|---|---|
| `st` | Nummer der dzielnica (01–18) |
| `szacunek` | Werte sind eine Schätzung; 1 = ja, 0 = nein |
| `mfh` | Mehrfamilienhäuser in Nutzung (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `blok` | Schätzung: Block-Kandidaten darunter (mindestens 4 Geschosse, Grundfläche mindestens 250 m², Rechteckigkeit mindestens 0,85); einschließlich osiedle |
| `osiedle` | Schätzung: Block-Kandidaten in einer Großsiedlung (mindestens 9 weitere Kandidaten im Umkreis von 150 m) |
| `blok_angebaut` | Hinweis, keine Regel: Block-Kandidaten mit mindestens 3 m gemeinsamer Grenze zu einem anderen BDOT10k-Gebäude (Blockrand, typisch für kamienice) |
| `osiedle_angebaut` | wie blok_angebaut, nur Kandidaten in einer Großsiedlung |

### `licencje`

| Feld | Bedeutung |
|---|---|
| `plik` | GeoPackage-Datei |
| `warstwa` | Ebene |
| `licencja_pliku` | Lizenz der Ebene in dieser Datei |
| `licencja_zrodla` | Lizenz der Quelle |
| `zrodlo` | Quelle |
| `nota` | anzugebender Quellenvermerk (wörtlich) |

## Kodierte Werte

| Feld | Wert | Bedeutung |
|---|---|---|
| `flaeche_quelle` | `bdot10k` | Grenze aus BDOT10k (PRG) |
| `nsp_weg` | `tabelle` | GUS-Tabelle für die ganze Einheit |
| `geb_bebauungsdichte_anzeige` | `anteil` | als Anteil in % gezeigt |
| `geb_geschossflaeche_naeherung_abzeichen` | `orientacyjnie` | Orientierung |
| `anteil_grund` | `bezugsflaeche_zu_klein` | Bezugsfläche zu klein |
| `art` | `park` | Park oder Grünanlage (BDOT10k, park lub skwer) |
| `art` | `przedszkole` | Kindergarten (przedszkole) |
| `art` | `szkola` | Schule jeder Art (BDOT10k trennt nicht) |
| `art` | `szpital` | Krankenhaus (szpital) |
| `art` | `zlobek` | Krippe (żłobek) |
| `q` | `bdot10k` | BDOT10k (GUGiK) |
| `status` | `lage_ohne_kapazitaet` | nur Lage, ohne Plätze und Schüler |
| `verkehrsmittel` | `bus` | Bus |
| `verkehrsmittel` | `bus+tram` | Bus und Straßenbahn |
| `verkehrsmittel` | `tram` | Straßenbahn |
| `taktklasse` | `I` | Abfahrten je Stunde und Richtung: mindestens 6 |
| `taktklasse` | `II` | Abfahrten je Stunde und Richtung: mindestens 2 |
| `taktklasse` | `III` | Abfahrten je Stunde und Richtung: mindestens 1 |
| `taktklasse` | `unter III` | Abfahrten je Stunde und Richtung: weniger als 1 |
| `r` | `muzeum` | Museumskomplex (zespół muzealny) |
| `r` | `pamiec` | nationale Gedenkstätte (miejsce pamięci narodowej) |
| `r` | `twierdza` | Festung (twierdza lub forteca) |
| `r` | `zabudowa` | historisches Bauensemble (zespół zabudowy historycznej) |
| `q` | `wd` | Wikidata (CC0 1.0) |
| `ep` | `1800_1866` | 1800–1866 |
| `ep` | `1867_1918` | 1867–1918 |
| `ep` | `1919_1945` | 1919–1945 |
| `ep` | `1946_1989` | 1946–1989 |
| `ep` | `ab_1990` | ab 1990 |
| `ep` | `vor_1800` | vor 1800 |
| `nsp_weg` | `rejony` | Summe der rejony statystyczne |
| `kennzahl` | `anteil_in_radius` | Anteil der Einwohner mit Einrichtung im Radius der amtlichen Vorgabe (richtwert_wert), % |
| `kennzahl` | `ew_je_einrichtung` | Einwohner je Einrichtung |
| `kennzahl` | `gruen_in_radius` | Anteil der Einwohner mit Park oder Grünanlage in 500 m Fußweg, % |
| `kennzahl` | `gruen_m2_je_ew` | Park- und Grünanlagenfläche (BDOT10k) je Einwohner, m² |
| `kennzahl` | `oepnv_takt` | Anteil der Einwohner mit Haltestelle der Taktklasse I oder II in 500 m, % |
| `art` | `haltestelle_takt` | Haltestelle der Taktklasse I oder II |
| `methode` | `fussweg` | Fußweg über das OSM-Wegenetz vom Mittelpunkt der 1-km-Zelle |
| `methode` | `luftlinie` | Luftlinie vom Mittelpunkt der 1-km-Zelle |
| `einheit` | `%` | Prozent |
| `einheit` | `ew_je_einrichtung` | Einwohner je Einrichtung |
| `einheit` | `m2_je_ew` | m² je Einwohner |
| `status` | `orientierung` | Orientierung, kein amtlicher Wert |
| `q` | `ztp` | GTFS der ZTP Kraków |
| `richtwert_einheit` | `m` | Meter |
| `richtwert_q` | `prawo_oswiatowe` | Schulgesetz (Prawo oświatowe) |
| `art` | `apotheke` | Apotheke (OSM) |
| `art` | `arzt` | Arzt oder Praxis (OSM amenity=doctors) |
| `q` | `osm` | OpenStreetMap |
| `art` | `M` | Wohnen (M) |
| `art` | `MP` | Wohnen und Ambulanz (MP) |
| `art` | `MU` | Wohnen und Nutzung (MU) |
| `art` | `P` | Ambulanz (P) |
| `art` | `U` | Nutzung ohne Wohnen (U) |
| `eig` | `gmina` | Stadt Kraków (Gmina Miejska Kraków) |
| `eig` | `publiczne_mieszane` | mehrere öffentliche Eigentümer oder die Woiwodschaft |
| `eig` | `skarb_panstwa` | Staatskasse (Skarb Państwa) |
| `hq` | `geschosse` | Geschosse × 3 m (Schätzung) |
| `hq` | `lod2` | LoD2-Modell (GUGiK, Stand 2017) |
| `typ` | `blok` | Block-Kandidat (Schätzung) |
| `typ` | `osiedle` | Block-Kandidat in einer Großsiedlung (Schätzung) |

## Zitieren

Kiezatlas Kraków, Stiebitz Souverain Systems UG (haftungsbeschränkt), https://souverain-systems.de/kiezatlas/krakow/, Datenstand 2026-11-14 (Downloads). Einzelheiten: `CITATION.cff` im Repository. Zu jeder Ebene gehören die Quellenvermerke aus der Tabelle `licencje`.

Fehler gefunden? kontakt@souverain-systems.de
