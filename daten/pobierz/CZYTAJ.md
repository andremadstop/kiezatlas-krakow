# Kiezatlas Kraków: dane do pobrania

Stan danych: wyliczono z plików atlasu (katalog `daten/`), ostatnia data w danych: 2026-11-14. Skrypt: `skripte/16_export_krakow.py`.

## Pliki

- `kiezatlas_krakow.gpkg`: GeoPackage bez danych z OpenStreetMap. Licencje źródeł w tabeli `licencje`.
- `kiezatlas_krakow_odbl.gpkg`: GeoPackage z danymi z OpenStreetMap i wszystkim, co przypisano do dzielnic według granic z OSM. Cały plik: Open Database License 1.0, © OpenStreetMap contributors (https://opendatacommons.org/licenses/odbl/1-0/).
- `csv/`, `csv_odbl/`: Te same warstwy jako CSV (UTF-8 z BOM, separator średnik, kropka dziesiętna).
- `csv_pl/`, `csv_odbl_pl/`: To samo z **przecinkiem dziesiętnym** i bez separatora tysięcy: otwiera się poprawnie w polskim Excelu i LibreOffice (liczby jako liczby).
- `kiezatlas_krakow.qgz`: Projekt QGIS (ścieżki względne, oba pliki GeoPackage obok w tym samym katalogu).
- `licencje.csv`: Licencja i dosłowna nota o źródle dla każdej warstwy.
- `pola.csv`, `wartosci.csv`: Znaczenie każdego pola (`pola.csv`) i każdej wartości kodowanej (`wartosci.csv`) po polsku, angielsku i niemiecku; także jako tabele `pola` i `wartosci` w obu plikach GeoPackage.
- `kiezatlas_krakow_csv.zip`: Wszystkie pliki CSV z `licencje.csv`, `pola.csv`, `wartosci.csv` i plikami CZYTAJ, README, LIESMICH w jednym archiwum.

## Warstwy

| Warstwa | Plik | Geometria | Wiersze | Z plików atlasu |
|---|---|---|---:|---|
| `miasto`: Kraków: liczby dla całego miasta | `kiezatlas_krakow.gpkg` | bez | 1 | `steckbrief`, `gebaeude_kennzahlen`, `klimat`, `sanierung` |
| `delegatury`: Cztery delegatury (dawne dzielnice) | `kiezatlas_krakow.gpkg` | bez | 4 | `steckbrief`, `gebaeude_kennzahlen`, `klimat`, `sanierung`, `denkmale_bdot` |
| `siatka_1km`: Siatka 1 km: ludność i odległości w linii prostej | `kiezatlas_krakow.gpkg` | polygon | 327 | `zellen_odbl`, `erreichbar` |
| `siatka_1km_pokrycie`: Siatka 1 km: pokrycie terenu | `kiezatlas_krakow.gpkg` | polygon | 397 | `klimat_zellen` |
| `rejony_statystyczne`: Rejony statystyczne: ludność według NSP 2021 | `kiezatlas_krakow.gpkg` | multipolygon | 749 | `rejony` |
| `placowki_bdot`: Placówki z BDOT10k | `kiezatlas_krakow.gpkg` | point | 321 | `einrichtungen` |
| `przystanki`: Przystanki z klasą częstotliwości | `kiezatlas_krakow.gpkg` | point | 944 | `haltestellen` |
| `bdot_kompleksy`: Kompleksy BDOT10k (muzea, forty, zespoły zabudowy) | `kiezatlas_krakow.gpkg` | polygon | 59 | `denkmale_bdot` |
| `bdot_kamienica_nazwa`: Budynki o nazwie „Kamienica …” w BDOT10k | `kiezatlas_krakow.gpkg` | point | 28 | `denkmale_bdot` |
| `rejestr_zabytkow`: Punkty rejestru zabytków z Wikidanych: obiekty o tym samym numerze rejestru jako jeden punkt (położenie sprawdzone na próbie) | `kiezatlas_krakow.gpkg` | point | 1214 | `denkmale` |
| `zbk_wykaz_dzielnice`: Wykaz ZBK: liczby według dzielnicy z wykazu | `kiezatlas_krakow.gpkg` | bez | 19 | `sanierung` |
| `dzielnice`: 18 dzielnic: granice i wskaźniki | `kiezatlas_krakow_odbl.gpkg` | multipolygon | 18 | `stadtteile_odbl`, `steckbrief_dzielnice_odbl`, `gebaeude_dzielnice_odbl`, `klimat_stadtteile_odbl` |
| `siatka_1km_odbl`: Siatka 1 km z przypisaniem do dzielnicy i drogą pieszą | `kiezatlas_krakow_odbl.gpkg` | polygon | 327 | `zellen_odbl`, `erreichbar_fuss_odbl` |
| `dostepnosc`: Dostępność placówek według dzielnicy | `kiezatlas_krakow_odbl.gpkg` | bez | 247 | `planer_odbl`, `planer_fuss_odbl` |
| `placowki_osm`: Lekarze i apteki z OpenStreetMap | `kiezatlas_krakow_odbl.gpkg` | point | 604 | `einrichtungen_odbl` |
| `osm_heritage_start_date`: Obiekty OSM z heritage lub start_date (położenie obiektów z heritage sprawdzone na próbie) | `kiezatlas_krakow_odbl.gpkg` | point | 929 | `denkmale_odbl` |
| `zbk_budynki`: Budynki ZBK w zasobie publicznym (położenie) | `kiezatlas_krakow_odbl.gpkg` | point | 126 | `sanierung_odbl` |
| `zbk_typologia_dzielnice`: Typologia bloków według dzielnicy (szacunek) | `kiezatlas_krakow_odbl.gpkg` | bez | 18 | `sanierung_odbl` |

Warstwa `siatka_1km` przejmuje z `zellen_odbl` tylko liczbę mieszkańców i udziały grup wieku (Eurostat), bez przypisania do dzielnicy (`st`); geometria komórki powstaje z jej kodu w siatce Eurostatu. Komórki to te, których środek leży w granicach miasta z BDOT10k, dlatego warstwa nie zawiera danych z OpenStreetMap.

Układ współrzędnych: ETRS89 / Poland CS2000 zone 7 (EPSG:2178). Współrzędne zaokrąglone do 0,01 m; geometrie nie są upraszczane. Nazwy pól są takie jak w plikach atlasu (częściowo niemieckie skróty); ich znaczenie opisują sekcje poniżej oraz `pola.csv` i `wartosci.csv`. Wartości logiczne w CSV: 1 = tak, 0 = nie; puste pole = brak danych.

## Czego nie ma w eksporcie

Żaden plik atlasu nie zawiera już danych przykładowych.

Bez własnej warstwy w eksporcie są jeszcze (dane rzeczywiste, tylko jako pliki atlasu w katalogu `daten/`):

- rynek mieszkaniowy: `mieszkania_odbl.js`
- jakość powietrza: `powietrze.js`

## Ograniczenia

- Brak lat budowy i danych o ogrzewaniu: rok budowy w ewidencji jest płatny, rejestr CEEB nie jest otwarty. Okres budowy (`ep`) mają tylko pojedyncze obiekty: ze znacznikiem `start_date` w OSM (warstwa `osm_heritage_start_date`) i z datą powstania w Wikidanych (warstwa `rejestr_zabytkow`), niesprawdzony i nigdy dla obszarów.
- Ludność pochodzi z siatki Eurostatu (Eurostat, Census 2021 population grid, plik PL_PD_3035_GPKG.zip); wartości dla dzielnic powstają przez sumowanie danych z komórek przypisanych według ich środka i są przybliżeniem na granicach.
- Typologia bloków (`typ_*`) to szacunek z BDOT10k (kondygnacje, powierzchnia, prostokątność), nie spis budynków z wielkiej płyty.
- Odległości to linia prosta albo droga piesza od środka komórki 1 km do najbliższej placówki; to wartości orientacyjne, nie urzędowe.
- Położenie sprawdzono na ortofotomapie tylko na losowej próbie (2026-11-15): punkty rejestru (Wikidane) 17 z 20 na obiekcie (85%, 95-procentowy przedział Wilsona 64%–95%), obiekty OSM z `heritage` 16 z 20 (80%, 58%–92%); „tuż obok” nie liczy się jako „na obiekcie”. To wynik dla warstwy, nie dla punktu: `polozenie_sprawdzone` = 0 przy każdym punkcie. Przypisania do budynku nie sprawdzano.

## Znaczenie pól

### `miasto`

| Pole | Znaczenie |
|---|---|
| `teryt` | identyfikator TERYT |
| `nazwa` | nazwa (polska nazwa własna) |
| `flaeche_km2` | powierzchnia, km² |
| `flaeche_quelle` | źródło powierzchni |
| `nsp_einwohner` | NSP 2021: liczba mieszkańców |
| `nsp_maenner` | NSP 2021: mężczyźni |
| `nsp_frauen` | NSP 2021: kobiety |
| `nsp_alter_10_a0_9` | NSP 2021: mieszkańcy w wieku 0–9 lat |
| `nsp_alter_10_a10_19` | NSP 2021: mieszkańcy w wieku 10–19 lat |
| `nsp_alter_10_a20_29` | NSP 2021: mieszkańcy w wieku 20–29 lat |
| `nsp_alter_10_a30_39` | NSP 2021: mieszkańcy w wieku 30–39 lat |
| `nsp_alter_10_a40_49` | NSP 2021: mieszkańcy w wieku 40–49 lat |
| `nsp_alter_10_a50_59` | NSP 2021: mieszkańcy w wieku 50–59 lat |
| `nsp_alter_10_a60_69` | NSP 2021: mieszkańcy w wieku 60–69 lat |
| `nsp_alter_10_a70_79` | NSP 2021: mieszkańcy w wieku 70–79 lat |
| `nsp_alter_10_a80p` | NSP 2021: mieszkańcy w wieku 80 lat i więcej |
| `nsp_oekonomisch_vor` | NSP 2021: mieszkańcy w wieku przedprodukcyjnym |
| `nsp_oekonomisch_erwerb` | NSP 2021: mieszkańcy w wieku produkcyjnym |
| `nsp_oekonomisch_nach` | NSP 2021: mieszkańcy w wieku poprodukcyjnym |
| `nsp_q_u20` | NSP 2021: udział mieszkańców poniżej 20 lat, % |
| `nsp_q_60p` | NSP 2021: udział mieszkańców w wieku 60 lat i więcej, % |
| `nsp_q_nach` | NSP 2021: udział mieszkańców w wieku poprodukcyjnym, % |
| `nsp_rejony` | NSP 2021: liczba rejonów statystycznych |
| `nsp_weg` | skąd pochodzą wartości NSP 2021 |
| `gitter_zellen` | siatka Eurostatu: liczba komórek 1 km, których środek leży w jednostce |
| `gitter_einwohner` | siatka Eurostatu: mieszkańcy (suma liczby mieszkańców komórek przypisanych według ich środka) |
| `gitter_u15` | siatka Eurostatu: mieszkańcy poniżej 15 lat |
| `gitter_a15_64` | siatka Eurostatu: mieszkańcy w wieku 15–64 lata |
| `gitter_a65p` | siatka Eurostatu: mieszkańcy w wieku 65 lat i więcej |
| `gitter_a_ges` | siatka Eurostatu: suma trzech grup wieku (może nieznacznie odbiegać od liczby mieszkańców) |
| `gitter_q_u15` | siatka Eurostatu: udział mieszkańców poniżej 15 lat w sumie grup wieku, % |
| `gitter_q_65p` | siatka Eurostatu: udział mieszkańców w wieku 65 lat i więcej w sumie grup wieku, % |
| `gitter_einwohner_flaechenanteil` | siatka Eurostatu: mieszkańcy według udziału powierzchni komórek w jednostce (porównanie) |
| `gitter_abweichung_nsp_proz` | różnica liczby mieszkańców z siatki względem NSP 2021, %; puste bez NSP |
| `dichte_nsp` | gęstość zaludnienia według NSP 2021, mieszkańcy na km² |
| `dichte_gitter` | gęstość zaludnienia według siatki Eurostatu, mieszkańcy na km² |
| `geb_anzahl` | BDOT10k: budynki (OT_BUBD_A) z punktem wewnętrznym w jednostce, wszystkie kategorie istnienia |
| `geb_zustand_eksploatowany` | BDOT10k: budynki o kategorii istnienia: eksploatowany |
| `geb_zustand_w_budowie` | BDOT10k: budynki o kategorii istnienia: w budowie |
| `geb_zustand_nieczynny` | BDOT10k: budynki o kategorii istnienia: nieczynny |
| `geb_zustand_zniszczony` | BDOT10k: budynki o kategorii istnienia: zniszczony |
| `geb_zustand_leer` | BDOT10k: budynki o kategorii istnienia: brak wartości |
| `geb_funktion_101` | BDOT10k: budynki o kodzie KŚT 101: budynki przemysłowe |
| `geb_funktion_102` | BDOT10k: budynki o kodzie KŚT 102: budynki transportu i łączności |
| `geb_funktion_103` | BDOT10k: budynki o kodzie KŚT 103: budynki handlowo-usługowe |
| `geb_funktion_104` | BDOT10k: budynki o kodzie KŚT 104: zbiorniki, silosy i budynki magazynowe |
| `geb_funktion_105` | BDOT10k: budynki o kodzie KŚT 105: budynki biurowe |
| `geb_funktion_106` | BDOT10k: budynki o kodzie KŚT 106: budynki szpitali i inne budynki opieki zdrowotnej |
| `geb_funktion_107` | BDOT10k: budynki o kodzie KŚT 107: budynki oświaty, nauki i kultury oraz budynki sportowe |
| `geb_funktion_108` | BDOT10k: budynki o kodzie KŚT 108: budynki produkcyjne, usługowe i gospodarcze dla rolnictwa |
| `geb_funktion_109` | BDOT10k: budynki o kodzie KŚT 109: pozostałe budynki niemieszkalne |
| `geb_funktion_110` | BDOT10k: budynki o kodzie KŚT 110: budynki mieszkalne |
| `geb_funktion_unbekannt` | BDOT10k: budynki bez kodu KŚT |
| `geb_wohngebaeude` | BDOT10k: budynki mieszkalne (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: budynki mieszkalne jednorodzinne (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: budynki mieszkalne wielorodzinne (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: pozostałe budynki mieszkalne (PFBUD) |
| `geb_geschosse_1` | BDOT10k: budynki: 1 kondygnacja |
| `geb_geschosse_2` | BDOT10k: budynki: 2 kondygnacje |
| `geb_geschosse_3_4` | BDOT10k: budynki: 3–4 kondygnacje |
| `geb_geschosse_5_10` | BDOT10k: budynki: 5–10 kondygnacji |
| `geb_geschosse_11p` | BDOT10k: budynki: 11 i więcej kondygnacji |
| `geb_geschosse_unbekannt` | BDOT10k: budynki: liczba kondygnacji nieznana |
| `geb_geschosse_wohn_1` | BDOT10k: budynki mieszkalne: 1 kondygnacja |
| `geb_geschosse_wohn_2` | BDOT10k: budynki mieszkalne: 2 kondygnacje |
| `geb_geschosse_wohn_3_4` | BDOT10k: budynki mieszkalne: 3–4 kondygnacje |
| `geb_geschosse_wohn_5_10` | BDOT10k: budynki mieszkalne: 5–10 kondygnacji |
| `geb_geschosse_wohn_11p` | BDOT10k: budynki mieszkalne: 11 i więcej kondygnacji |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: budynki mieszkalne: liczba kondygnacji nieznana |
| `geb_geschosse_median` | BDOT10k: mediana liczby kondygnacji nadziemnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_mittel` | BDOT10k: średnia liczby kondygnacji nadziemnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_median_wohn` | BDOT10k: mediana liczby kondygnacji nadziemnych budynków mieszkalnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_mittel_wohn` | BDOT10k: średnia liczby kondygnacji nadziemnych budynków mieszkalnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_grundflaeche_m2` | BDOT10k: suma powierzchni obrysów budynków bez zniszczonych, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: suma powierzchni obrysów budynków mieszkalnych, m² |
| `geb_flaeche_m2` | powierzchnia jednostki, m² |
| `geb_bebauungsdichte_wert` | wskaźnik zabudowy (udział powierzchni zabudowy w powierzchni jednostki): 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | licznik: powierzchnia obrysów budynków, m² |
| `geb_bebauungsdichte_nenner` | mianownik: powierzchnia jednostki, m² |
| `geb_bebauungsdichte_anzeige` | sposób prezentacji wartości |
| `geb_geschossflaeche_naeherung_wert` | przybliżona intensywność zabudowy: Σ(powierzchnia obrysu × liczba kondygnacji) / powierzchnia jednostki; orientacyjnie, nie wartość urzędowa |
| `geb_geschossflaeche_naeherung_zaehler` | licznik: Σ(powierzchnia obrysu × liczba kondygnacji), m² |
| `geb_geschossflaeche_naeherung_nenner` | mianownik: powierzchnia jednostki, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | oznaczenie wartości |
| `klimat_flaeche_ha` | powierzchnia jednostki w granicach miasta, ha |
| `klimat_abdeckung` | udział powierzchni jednostki objęty klasami pokrycia terenu BDOT10k, % |
| `klimat_ha_bebauung` | BDOT10k: powierzchnia klasy pokrycia terenu: zabudowa (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: powierzchnia klasy pokrycia terenu: tereny komunikacyjne i place (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: powierzchnia klasy pokrycia terenu: zieleń (PTRK, PTUT, roślinność trawiasta z PTTR), ha |
| `klimat_ha_wald` | BDOT10k: powierzchnia klasy pokrycia terenu: lasy i zadrzewienia (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: powierzchnia klasy pokrycia terenu: wody (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: powierzchnia klasy pokrycia terenu: grunty orne (uprawy z PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: powierzchnia klasy pokrycia terenu: pozostałe (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: udział w sumie klas pokrycia terenu: zabudowa (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: udział w sumie klas pokrycia terenu: tereny komunikacyjne i place (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: udział w sumie klas pokrycia terenu: zieleń (PTRK, PTUT, roślinność trawiasta z PTTR), % |
| `klimat_anteil_wald` | BDOT10k: udział w sumie klas pokrycia terenu: lasy i zadrzewienia (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: udział w sumie klas pokrycia terenu: wody (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: udział w sumie klas pokrycia terenu: grunty orne (uprawy z PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: udział w sumie klas pokrycia terenu: pozostałe (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: udział w sumie klas pokrycia terenu: zabudowa i tereny komunikacyjne razem, % |
| `klimat_anteil_gruen_wald` | BDOT10k: udział w sumie klas pokrycia terenu: zieleń i lasy razem, % |
| `klimat_gruen_je_ew` | zieleń i lasy na mieszkańca, m² |
| `typ_mfh` | budynki wielorodzinne eksploatowane (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `typ_blok` | szacunek: w tym kandydaci na bloki (liczba kondygnacji co najmniej 4, powierzchnia obrysu co najmniej 250 m², prostokątność co najmniej 0,85); łącznie z kategorią osiedle |
| `typ_osiedle` | szacunek: kandydaci na blok na osiedlu blokowym (liczba innych kandydatów w promieniu 150 m co najmniej 9) |
| `typ_blok_angebaut` | wskazówka, nie reguła: kandydaci na blok ze wspólną granicą o długości co najmniej 3 m z innym budynkiem BDOT10k (zabudowa pierzejowa, typowa dla kamienic) |
| `typ_osiedle_angebaut` | jak blok_angebaut, tylko kandydaci na osiedlu blokowym |

### `delegatury`

| Pole | Znaczenie |
|---|---|
| `gruppe` | numer delegatury w atlasie: 1 = Kraków-Śródmieście, 2 = Kraków-Krowodrza, 3 = Kraków-Podgórze, 4 = Kraków-Nowa Huta |
| `teryt` | identyfikator TERYT |
| `nazwa` | nazwa (polska nazwa własna) |
| `flaeche_km2` | powierzchnia, km² |
| `flaeche_quelle` | źródło powierzchni |
| `nsp_einwohner` | NSP 2021: liczba mieszkańców |
| `nsp_maenner` | NSP 2021: mężczyźni |
| `nsp_frauen` | NSP 2021: kobiety |
| `nsp_alter_10_a0_9` | NSP 2021: mieszkańcy w wieku 0–9 lat |
| `nsp_alter_10_a10_19` | NSP 2021: mieszkańcy w wieku 10–19 lat |
| `nsp_alter_10_a20_29` | NSP 2021: mieszkańcy w wieku 20–29 lat |
| `nsp_alter_10_a30_39` | NSP 2021: mieszkańcy w wieku 30–39 lat |
| `nsp_alter_10_a40_49` | NSP 2021: mieszkańcy w wieku 40–49 lat |
| `nsp_alter_10_a50_59` | NSP 2021: mieszkańcy w wieku 50–59 lat |
| `nsp_alter_10_a60_69` | NSP 2021: mieszkańcy w wieku 60–69 lat |
| `nsp_alter_10_a70_79` | NSP 2021: mieszkańcy w wieku 70–79 lat |
| `nsp_alter_10_a80p` | NSP 2021: mieszkańcy w wieku 80 lat i więcej |
| `nsp_oekonomisch_vor` | NSP 2021: mieszkańcy w wieku przedprodukcyjnym |
| `nsp_oekonomisch_erwerb` | NSP 2021: mieszkańcy w wieku produkcyjnym |
| `nsp_oekonomisch_nach` | NSP 2021: mieszkańcy w wieku poprodukcyjnym |
| `nsp_q_u20` | NSP 2021: udział mieszkańców poniżej 20 lat, % |
| `nsp_q_60p` | NSP 2021: udział mieszkańców w wieku 60 lat i więcej, % |
| `nsp_q_nach` | NSP 2021: udział mieszkańców w wieku poprodukcyjnym, % |
| `nsp_rejony` | NSP 2021: liczba rejonów statystycznych |
| `nsp_weg` | skąd pochodzą wartości NSP 2021 |
| `gitter_zellen` | siatka Eurostatu: liczba komórek 1 km, których środek leży w jednostce |
| `gitter_einwohner` | siatka Eurostatu: mieszkańcy (suma liczby mieszkańców komórek przypisanych według ich środka) |
| `gitter_u15` | siatka Eurostatu: mieszkańcy poniżej 15 lat |
| `gitter_a15_64` | siatka Eurostatu: mieszkańcy w wieku 15–64 lata |
| `gitter_a65p` | siatka Eurostatu: mieszkańcy w wieku 65 lat i więcej |
| `gitter_a_ges` | siatka Eurostatu: suma trzech grup wieku (może nieznacznie odbiegać od liczby mieszkańców) |
| `gitter_q_u15` | siatka Eurostatu: udział mieszkańców poniżej 15 lat w sumie grup wieku, % |
| `gitter_q_65p` | siatka Eurostatu: udział mieszkańców w wieku 65 lat i więcej w sumie grup wieku, % |
| `gitter_einwohner_flaechenanteil` | siatka Eurostatu: mieszkańcy według udziału powierzchni komórek w jednostce (porównanie) |
| `gitter_abweichung_nsp_proz` | różnica liczby mieszkańców z siatki względem NSP 2021, %; puste bez NSP |
| `dichte_nsp` | gęstość zaludnienia według NSP 2021, mieszkańcy na km² |
| `dichte_gitter` | gęstość zaludnienia według siatki Eurostatu, mieszkańcy na km² |
| `geb_anzahl` | BDOT10k: budynki (OT_BUBD_A) z punktem wewnętrznym w jednostce, wszystkie kategorie istnienia |
| `geb_zustand_eksploatowany` | BDOT10k: budynki o kategorii istnienia: eksploatowany |
| `geb_zustand_w_budowie` | BDOT10k: budynki o kategorii istnienia: w budowie |
| `geb_zustand_nieczynny` | BDOT10k: budynki o kategorii istnienia: nieczynny |
| `geb_zustand_zniszczony` | BDOT10k: budynki o kategorii istnienia: zniszczony |
| `geb_zustand_leer` | BDOT10k: budynki o kategorii istnienia: brak wartości |
| `geb_funktion_101` | BDOT10k: budynki o kodzie KŚT 101: budynki przemysłowe |
| `geb_funktion_102` | BDOT10k: budynki o kodzie KŚT 102: budynki transportu i łączności |
| `geb_funktion_103` | BDOT10k: budynki o kodzie KŚT 103: budynki handlowo-usługowe |
| `geb_funktion_104` | BDOT10k: budynki o kodzie KŚT 104: zbiorniki, silosy i budynki magazynowe |
| `geb_funktion_105` | BDOT10k: budynki o kodzie KŚT 105: budynki biurowe |
| `geb_funktion_106` | BDOT10k: budynki o kodzie KŚT 106: budynki szpitali i inne budynki opieki zdrowotnej |
| `geb_funktion_107` | BDOT10k: budynki o kodzie KŚT 107: budynki oświaty, nauki i kultury oraz budynki sportowe |
| `geb_funktion_108` | BDOT10k: budynki o kodzie KŚT 108: budynki produkcyjne, usługowe i gospodarcze dla rolnictwa |
| `geb_funktion_109` | BDOT10k: budynki o kodzie KŚT 109: pozostałe budynki niemieszkalne |
| `geb_funktion_110` | BDOT10k: budynki o kodzie KŚT 110: budynki mieszkalne |
| `geb_funktion_unbekannt` | BDOT10k: budynki bez kodu KŚT |
| `geb_wohngebaeude` | BDOT10k: budynki mieszkalne (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: budynki mieszkalne jednorodzinne (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: budynki mieszkalne wielorodzinne (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: pozostałe budynki mieszkalne (PFBUD) |
| `geb_geschosse_1` | BDOT10k: budynki: 1 kondygnacja |
| `geb_geschosse_2` | BDOT10k: budynki: 2 kondygnacje |
| `geb_geschosse_3_4` | BDOT10k: budynki: 3–4 kondygnacje |
| `geb_geschosse_5_10` | BDOT10k: budynki: 5–10 kondygnacji |
| `geb_geschosse_11p` | BDOT10k: budynki: 11 i więcej kondygnacji |
| `geb_geschosse_unbekannt` | BDOT10k: budynki: liczba kondygnacji nieznana |
| `geb_geschosse_wohn_1` | BDOT10k: budynki mieszkalne: 1 kondygnacja |
| `geb_geschosse_wohn_2` | BDOT10k: budynki mieszkalne: 2 kondygnacje |
| `geb_geschosse_wohn_3_4` | BDOT10k: budynki mieszkalne: 3–4 kondygnacje |
| `geb_geschosse_wohn_5_10` | BDOT10k: budynki mieszkalne: 5–10 kondygnacji |
| `geb_geschosse_wohn_11p` | BDOT10k: budynki mieszkalne: 11 i więcej kondygnacji |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: budynki mieszkalne: liczba kondygnacji nieznana |
| `geb_geschosse_median` | BDOT10k: mediana liczby kondygnacji nadziemnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_mittel` | BDOT10k: średnia liczby kondygnacji nadziemnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_median_wohn` | BDOT10k: mediana liczby kondygnacji nadziemnych budynków mieszkalnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_mittel_wohn` | BDOT10k: średnia liczby kondygnacji nadziemnych budynków mieszkalnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_grundflaeche_m2` | BDOT10k: suma powierzchni obrysów budynków bez zniszczonych, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: suma powierzchni obrysów budynków mieszkalnych, m² |
| `geb_flaeche_m2` | powierzchnia jednostki, m² |
| `geb_bebauungsdichte_wert` | wskaźnik zabudowy (udział powierzchni zabudowy w powierzchni jednostki): 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | licznik: powierzchnia obrysów budynków, m² |
| `geb_bebauungsdichte_nenner` | mianownik: powierzchnia jednostki, m² |
| `geb_bebauungsdichte_anzeige` | sposób prezentacji wartości |
| `geb_geschossflaeche_naeherung_wert` | przybliżona intensywność zabudowy: Σ(powierzchnia obrysu × liczba kondygnacji) / powierzchnia jednostki; orientacyjnie, nie wartość urzędowa |
| `geb_geschossflaeche_naeherung_zaehler` | licznik: Σ(powierzchnia obrysu × liczba kondygnacji), m² |
| `geb_geschossflaeche_naeherung_nenner` | mianownik: powierzchnia jednostki, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | oznaczenie wartości |
| `klimat_flaeche_ha` | powierzchnia jednostki w granicach miasta, ha |
| `klimat_abdeckung` | udział powierzchni jednostki objęty klasami pokrycia terenu BDOT10k, % |
| `klimat_ha_bebauung` | BDOT10k: powierzchnia klasy pokrycia terenu: zabudowa (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: powierzchnia klasy pokrycia terenu: tereny komunikacyjne i place (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: powierzchnia klasy pokrycia terenu: zieleń (PTRK, PTUT, roślinność trawiasta z PTTR), ha |
| `klimat_ha_wald` | BDOT10k: powierzchnia klasy pokrycia terenu: lasy i zadrzewienia (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: powierzchnia klasy pokrycia terenu: wody (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: powierzchnia klasy pokrycia terenu: grunty orne (uprawy z PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: powierzchnia klasy pokrycia terenu: pozostałe (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: udział w sumie klas pokrycia terenu: zabudowa (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: udział w sumie klas pokrycia terenu: tereny komunikacyjne i place (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: udział w sumie klas pokrycia terenu: zieleń (PTRK, PTUT, roślinność trawiasta z PTTR), % |
| `klimat_anteil_wald` | BDOT10k: udział w sumie klas pokrycia terenu: lasy i zadrzewienia (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: udział w sumie klas pokrycia terenu: wody (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: udział w sumie klas pokrycia terenu: grunty orne (uprawy z PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: udział w sumie klas pokrycia terenu: pozostałe (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: udział w sumie klas pokrycia terenu: zabudowa i tereny komunikacyjne razem, % |
| `klimat_anteil_gruen_wald` | BDOT10k: udział w sumie klas pokrycia terenu: zieleń i lasy razem, % |
| `typ_mfh` | budynki wielorodzinne eksploatowane (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `typ_blok` | szacunek: w tym kandydaci na bloki (liczba kondygnacji co najmniej 4, powierzchnia obrysu co najmniej 250 m², prostokątność co najmniej 0,85); łącznie z kategorią osiedle |
| `typ_osiedle` | szacunek: kandydaci na blok na osiedlu blokowym (liczba innych kandydatów w promieniu 150 m co najmniej 9) |
| `typ_blok_angebaut` | wskazówka, nie reguła: kandydaci na blok ze wspólną granicą o długości co najmniej 3 m z innym budynkiem BDOT10k (zabudowa pierzejowa, typowa dla kamienic) |
| `typ_osiedle_angebaut` | jak blok_angebaut, tylko kandydaci na osiedlu blokowym |
| `bdot_wohngebaeude` | BDOT10k: budynki mieszkalne (FOBUD) |
| `bdot_mehrfamilienhaeuser` | BDOT10k: budynki wielorodzinne (PFBUD) |
| `bdot_namensbezug` | BDOT10k: budynki o nazwie „Kamienica …” |

### `siatka_1km`

| Pole | Znaczenie |
|---|---|
| `id` | kod komórki siatki Eurostatu 1 km (EPSG:3035, narożnik południowo-zachodni) |
| `ew` | mieszkańcy (siatka Eurostatu 2021) |
| `a_ges` | suma trzech grup wieku w komórce |
| `q_u15` | udział mieszkańców poniżej 15 lat, % |
| `q_65p` | udział mieszkańców w wieku 65 lat i więcej, % |
| `luftlinie_m_haltestelle_takt` | odległość w linii prostej od środka komórki do najbliższego celu: przystanek klasy częstotliwości kursowania I lub II, m |
| `luftlinie_m_park` | odległość w linii prostej od środka komórki do najbliższego celu: park lub skwer (BDOT10k), m |
| `luftlinie_m_przedszkole` | odległość w linii prostej od środka komórki do najbliższego celu: przedszkole, m |
| `luftlinie_m_szkola` | odległość w linii prostej od środka komórki do najbliższego celu: szkoła dowolnego typu (BDOT10k nie rozróżnia typów), m |
| `luftlinie_m_szpital` | odległość w linii prostej od środka komórki do najbliższego celu: szpital, m |
| `luftlinie_m_zlobek` | odległość w linii prostej od środka komórki do najbliższego celu: żłobek, m |
| `wkt` | geometria jako WKT w EPSG:2178 |

### `siatka_1km_pokrycie`

| Pole | Znaczenie |
|---|---|
| `id` | kod komórki siatki Eurostatu 1 km (EPSG:3035, narożnik południowo-zachodni) |
| `flaeche_stadt_ha` | powierzchnia komórki w granicach miasta, ha |
| `anteil_stadt` | udział komórki leżący w granicach miasta, % |
| `abdeckung` | udział powierzchni jednostki objęty klasami pokrycia terenu BDOT10k, % |
| `ha_bebauung` | BDOT10k: powierzchnia klasy pokrycia terenu: zabudowa (PTZB), ha |
| `ha_verkehr` | BDOT10k: powierzchnia klasy pokrycia terenu: tereny komunikacyjne i place (PTKM, PTPL), ha |
| `ha_gruen` | BDOT10k: powierzchnia klasy pokrycia terenu: zieleń (PTRK, PTUT, roślinność trawiasta z PTTR), ha |
| `ha_wald` | BDOT10k: powierzchnia klasy pokrycia terenu: lasy i zadrzewienia (PTLZ), ha |
| `ha_wasser` | BDOT10k: powierzchnia klasy pokrycia terenu: wody (PTWP), ha |
| `ha_acker` | BDOT10k: powierzchnia klasy pokrycia terenu: grunty orne (uprawy z PTTR), ha |
| `ha_sonstige` | BDOT10k: powierzchnia klasy pokrycia terenu: pozostałe (PTGN, PTSO, PTWZ, PTNZ), ha |
| `anteil` | pole techniczne, zawsze puste; udziały są w kolumnach anteil_* |
| `anteil_grund` | powód pustych udziałów (powierzchnia w mieście poniżej 10 ha) |
| `anteil_bebauung` | BDOT10k: udział w sumie klas pokrycia terenu: zabudowa (PTZB), % |
| `anteil_verkehr` | BDOT10k: udział w sumie klas pokrycia terenu: tereny komunikacyjne i place (PTKM, PTPL), % |
| `anteil_gruen` | BDOT10k: udział w sumie klas pokrycia terenu: zieleń (PTRK, PTUT, roślinność trawiasta z PTTR), % |
| `anteil_wald` | BDOT10k: udział w sumie klas pokrycia terenu: lasy i zadrzewienia (PTLZ), % |
| `anteil_wasser` | BDOT10k: udział w sumie klas pokrycia terenu: wody (PTWP), % |
| `anteil_acker` | BDOT10k: udział w sumie klas pokrycia terenu: grunty orne (uprawy z PTTR), % |
| `anteil_sonstige` | BDOT10k: udział w sumie klas pokrycia terenu: pozostałe (PTGN, PTSO, PTWZ, PTNZ), % |
| `anteil_bebauung_verkehr` | BDOT10k: udział w sumie klas pokrycia terenu: zabudowa i tereny komunikacyjne razem, % |
| `anteil_gruen_wald` | BDOT10k: udział w sumie klas pokrycia terenu: zieleń i lasy razem, % |
| `wkt` | geometria jako WKT w EPSG:2178 |

### `rejony_statystyczne`

| Pole | Znaczenie |
|---|---|
| `rejon` | identyfikator rejonu statystycznego GUS (6 cyfr) |
| `delegatura_teryt` | kod TERYT delegatury według GUS |
| `nsp_einwohner` | NSP 2021: liczba mieszkańców rejonu; puste = brak wiersza w tabeli spisu |
| `flaeche_km2` | powierzchnia, km² |
| `dichte_nsp` | gęstość zaludnienia według NSP 2021, mieszkańcy na km² |
| `nsp_q_u20` | NSP 2021: udział osób poniżej 20 lat, pełne %; puste poniżej 100 osób |
| `nsp_q_60p` | NSP 2021: udział osób w wieku 60 lat i więcej, pełne %; puste poniżej 100 osób |
| `nsp_q_nach` | NSP 2021: udział osób w wieku poprodukcyjnym, pełne %; puste poniżej 100 osób |
| `ohne_zeile` | 1 = rejon bez wiersza w tabeli spisu (bez wartości) |
| `wkt` | geometria jako WKT w EPSG:2178 |

### `placowki_bdot`

| Pole | Znaczenie |
|---|---|
| `id` | identyfikator obiektu w BDOT10k (LOKALNYID) |
| `art` | rodzaj placówki |
| `unterart` | podtyp: puste (BDOT10k go nie podaje) |
| `q` | źródło (klucz w tabeli licencje) |
| `name` | nazwa placówki z BDOT10k (nazwa urzędowa, nie osoba) |
| `plaetze` | liczba miejsc: puste (BDOT10k nie podaje) |
| `schueler` | liczba uczniów: puste (BDOT10k nie podaje) |
| `schueler_stand` | stan liczby uczniów: puste |
| `status` | zakres informacji o placówce |
| `in_stadt` | w granicach Krakowa (BDOT10k); 1 = tak, 0 = nie |
| `x` | współrzędna x (wschód) w EPSG:2178, m |
| `y` | współrzędna y (północ) w EPSG:2178, m |

### `przystanki`

| Pole | Znaczenie |
|---|---|
| `id` | rdzeń kodu przystanku ZTP (stop_code przed myślnikiem) |
| `name` | nazwa przystanku (stop_name) |
| `verkehrsmittel` | środki transportu z odjazdami w dniu liczenia |
| `fahrten_hvz_je_richtung` | odjazdy na godzinę w oknie 06:00–09:00, kierunek z większą liczbą odjazdów |
| `taktklasse` | klasa częstotliwości kursowania (własna klasyfikacja, nie norma) |
| `in_stadt` | w granicach Krakowa (BDOT10k); 1 = tak, 0 = nie |
| `x` | współrzędna x (wschód) w EPSG:2178, m |
| `y` | współrzędna y (północ) w EPSG:2178, m |

### `bdot_kompleksy`

| Pole | Znaczenie |
|---|---|
| `r` | rodzaj kompleksu (BDOT10k RODZAJ) |
| `n` | nazwa kompleksu (BDOT10k NAZWA) |
| `del` | delegatura (nazwa z BDOT10k); puste = bez przypisania |
| `wkt` | geometria jako WKT w EPSG:2178 |

### `bdot_kamienica_nazwa`

| Pole | Znaczenie |
|---|---|
| `w` | budynek mieszkalny (FOBUD); puste = brak budynku; 1 = tak, 0 = nie |
| `mfh` | budynek wielorodzinny (PFBUD); puste = brak budynku; 1 = tak, 0 = nie |
| `gs` | liczba kondygnacji nadziemnych (BDOT10k LICZ_KONDY) |
| `del` | delegatura (nazwa z BDOT10k); puste = bez przypisania |
| `x` | współrzędna x (wschód) w EPSG:2178, m |
| `y` | współrzędna y (północ) w EPSG:2178, m |

### `rejestr_zabytkow`

| Pole | Znaczenie |
|---|---|
| `q` | źródło punktu (wd = Wikidane, nid = rejestr NID, gez = gminna ewidencja zabytków; kilka po przecinku) |
| `ep` | okres budowy z daty powstania w Wikidanych (klasa, nigdy pojedynczy rok); puste = brak lub niejednoznaczne |
| `w` | budynek mieszkalny (FOBUD); puste = brak budynku; 1 = tak, 0 = nie |
| `mfh` | budynek wielorodzinny (PFBUD); puste = brak budynku; 1 = tak, 0 = nie |
| `del` | delegatura (nazwa z BDOT10k); puste = bez przypisania |
| `polozenie_sprawdzone` | położenie tego punktu sprawdzone osobno na ortofotomapie (wszędzie 0: sprawdzono co najwyżej losową próbę warstwy, wynik w CZYTAJ.md); 1 = tak, 0 = nie |
| `x` | współrzędna x (wschód) w EPSG:2178, m |
| `y` | współrzędna y (północ) w EPSG:2178, m |

### `zbk_wykaz_dzielnice`

| Pole | Znaczenie |
|---|---|
| `dzielnica_z_wykazu` | dzielnica według wykazu ZBK (numer 01–18; poza = poza Krakowem) |
| `n` | liczba pozycji w wykazie (pozycja to nie zawsze budynek) |
| `art_M` | pozycje wykazu o rodzaju: mieszkalny |
| `art_MP` | pozycje wykazu o rodzaju: mieszkalny i przychodnia |
| `art_MU` | pozycje wykazu o rodzaju: mieszkalny i użytkowy |
| `art_MUP` | pozycje wykazu o rodzaju: mieszkalny, użytkowy i przychodnia |
| `art_P` | pozycje wykazu o rodzaju: przychodnia |
| `art_U` | pozycje wykazu o rodzaju: użytkowy |
| `eigentum_gmina` | pozycje wykazu, własność: Gmina Miejska Kraków |
| `eigentum_skarb_panstwa` | pozycje wykazu, własność: Skarb Państwa |
| `eigentum_publiczne_mieszane` | pozycje wykazu, własność: kilku właścicieli publicznych albo województwo |
| `eigentum_z_prywatnymi` | pozycje wykazu, własność: własność publiczna z udziałem osób prywatnych |
| `eigentum_prywatne` | pozycje wykazu, własność: tylko właściciele prywatni |
| `eigentum_brak` | pozycje wykazu, własność: własności nie da się przypisać |
| `art_UP` | pozycje wykazu o rodzaju: użytkowy i przychodnia |

### `dzielnice`

| Pole | Znaczenie |
|---|---|
| `nr` | numer dzielnicy (01–18) |
| `rzymska` | numer dzielnicy cyframi rzymskimi |
| `nazwa` | nazwa (polska nazwa własna) |
| `gruppe` | delegatura, do której należy dzielnica: 1 = Kraków-Śródmieście, 2 = Kraków-Krowodrza, 3 = Kraków-Podgórze, 4 = Kraków-Nowa Huta |
| `flaeche_km2` | powierzchnia, km² |
| `osm_id` | relacja granicy w OpenStreetMap |
| `gitter_zellen` | siatka Eurostatu: liczba komórek 1 km, których środek leży w jednostce |
| `gitter_einwohner` | siatka Eurostatu: mieszkańcy (suma liczby mieszkańców komórek przypisanych według ich środka) |
| `gitter_u15` | siatka Eurostatu: mieszkańcy poniżej 15 lat |
| `gitter_a15_64` | siatka Eurostatu: mieszkańcy w wieku 15–64 lata |
| `gitter_a65p` | siatka Eurostatu: mieszkańcy w wieku 65 lat i więcej |
| `gitter_a_ges` | siatka Eurostatu: suma trzech grup wieku (może nieznacznie odbiegać od liczby mieszkańców) |
| `gitter_q_u15` | siatka Eurostatu: udział mieszkańców poniżej 15 lat w sumie grup wieku, % |
| `gitter_q_65p` | siatka Eurostatu: udział mieszkańców w wieku 65 lat i więcej w sumie grup wieku, % |
| `gitter_einwohner_flaechenanteil` | siatka Eurostatu: mieszkańcy według udziału powierzchni komórek w jednostce (porównanie) |
| `gitter_abweichung_nsp_proz` | różnica liczby mieszkańców z siatki względem NSP 2021, %; puste bez NSP |
| `gitter_zellen_beruehrt` | liczba komórek, które choćby częściowo leżą w jednostce |
| `gitter_spanne_proz` | różnica między wynikami przypisania według powierzchni i według środka, % (miara niepewności na granicach, nie błąd) |
| `dichte_gitter` | gęstość zaludnienia według siatki Eurostatu, mieszkańcy na km² |
| `nsp_einwohner` | NSP 2021: liczba mieszkańców |
| `nsp_maenner` | NSP 2021: mężczyźni |
| `nsp_frauen` | NSP 2021: kobiety |
| `nsp_alter_10_a0_9` | NSP 2021: mieszkańcy w wieku 0–9 lat |
| `nsp_alter_10_a10_19` | NSP 2021: mieszkańcy w wieku 10–19 lat |
| `nsp_alter_10_a20_29` | NSP 2021: mieszkańcy w wieku 20–29 lat |
| `nsp_alter_10_a30_39` | NSP 2021: mieszkańcy w wieku 30–39 lat |
| `nsp_alter_10_a40_49` | NSP 2021: mieszkańcy w wieku 40–49 lat |
| `nsp_alter_10_a50_59` | NSP 2021: mieszkańcy w wieku 50–59 lat |
| `nsp_alter_10_a60_69` | NSP 2021: mieszkańcy w wieku 60–69 lat |
| `nsp_alter_10_a70_79` | NSP 2021: mieszkańcy w wieku 70–79 lat |
| `nsp_alter_10_a80p` | NSP 2021: mieszkańcy w wieku 80 lat i więcej |
| `nsp_oekonomisch_vor` | NSP 2021: mieszkańcy w wieku przedprodukcyjnym |
| `nsp_oekonomisch_erwerb` | NSP 2021: mieszkańcy w wieku produkcyjnym |
| `nsp_oekonomisch_nach` | NSP 2021: mieszkańcy w wieku poprodukcyjnym |
| `nsp_q_u20` | NSP 2021: udział mieszkańców poniżej 20 lat, % |
| `nsp_q_60p` | NSP 2021: udział mieszkańców w wieku 60 lat i więcej, % |
| `nsp_q_nach` | NSP 2021: udział mieszkańców w wieku poprodukcyjnym, % |
| `nsp_rejony` | NSP 2021: liczba rejonów statystycznych |
| `nsp_weg` | skąd pochodzą wartości NSP 2021 |
| `dichte_nsp` | gęstość zaludnienia według NSP 2021, mieszkańcy na km² |
| `geb_anzahl` | BDOT10k: budynki (OT_BUBD_A) z punktem wewnętrznym w jednostce, wszystkie kategorie istnienia |
| `geb_zustand_eksploatowany` | BDOT10k: budynki o kategorii istnienia: eksploatowany |
| `geb_zustand_w_budowie` | BDOT10k: budynki o kategorii istnienia: w budowie |
| `geb_zustand_nieczynny` | BDOT10k: budynki o kategorii istnienia: nieczynny |
| `geb_zustand_zniszczony` | BDOT10k: budynki o kategorii istnienia: zniszczony |
| `geb_zustand_leer` | BDOT10k: budynki o kategorii istnienia: brak wartości |
| `geb_funktion_101` | BDOT10k: budynki o kodzie KŚT 101: budynki przemysłowe |
| `geb_funktion_102` | BDOT10k: budynki o kodzie KŚT 102: budynki transportu i łączności |
| `geb_funktion_103` | BDOT10k: budynki o kodzie KŚT 103: budynki handlowo-usługowe |
| `geb_funktion_104` | BDOT10k: budynki o kodzie KŚT 104: zbiorniki, silosy i budynki magazynowe |
| `geb_funktion_105` | BDOT10k: budynki o kodzie KŚT 105: budynki biurowe |
| `geb_funktion_106` | BDOT10k: budynki o kodzie KŚT 106: budynki szpitali i inne budynki opieki zdrowotnej |
| `geb_funktion_107` | BDOT10k: budynki o kodzie KŚT 107: budynki oświaty, nauki i kultury oraz budynki sportowe |
| `geb_funktion_108` | BDOT10k: budynki o kodzie KŚT 108: budynki produkcyjne, usługowe i gospodarcze dla rolnictwa |
| `geb_funktion_109` | BDOT10k: budynki o kodzie KŚT 109: pozostałe budynki niemieszkalne |
| `geb_funktion_110` | BDOT10k: budynki o kodzie KŚT 110: budynki mieszkalne |
| `geb_funktion_unbekannt` | BDOT10k: budynki bez kodu KŚT |
| `geb_wohngebaeude` | BDOT10k: budynki mieszkalne (KŚT 110) |
| `geb_wohn_art_ein` | BDOT10k: budynki mieszkalne jednorodzinne (PFBUD) |
| `geb_wohn_art_mehr` | BDOT10k: budynki mieszkalne wielorodzinne (PFBUD) |
| `geb_wohn_art_sonst` | BDOT10k: pozostałe budynki mieszkalne (PFBUD) |
| `geb_geschosse_1` | BDOT10k: budynki: 1 kondygnacja |
| `geb_geschosse_2` | BDOT10k: budynki: 2 kondygnacje |
| `geb_geschosse_3_4` | BDOT10k: budynki: 3–4 kondygnacje |
| `geb_geschosse_5_10` | BDOT10k: budynki: 5–10 kondygnacji |
| `geb_geschosse_11p` | BDOT10k: budynki: 11 i więcej kondygnacji |
| `geb_geschosse_unbekannt` | BDOT10k: budynki: liczba kondygnacji nieznana |
| `geb_geschosse_wohn_1` | BDOT10k: budynki mieszkalne: 1 kondygnacja |
| `geb_geschosse_wohn_2` | BDOT10k: budynki mieszkalne: 2 kondygnacje |
| `geb_geschosse_wohn_3_4` | BDOT10k: budynki mieszkalne: 3–4 kondygnacje |
| `geb_geschosse_wohn_5_10` | BDOT10k: budynki mieszkalne: 5–10 kondygnacji |
| `geb_geschosse_wohn_11p` | BDOT10k: budynki mieszkalne: 11 i więcej kondygnacji |
| `geb_geschosse_wohn_unbekannt` | BDOT10k: budynki mieszkalne: liczba kondygnacji nieznana |
| `geb_geschosse_median` | BDOT10k: mediana liczby kondygnacji nadziemnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_mittel` | BDOT10k: średnia liczby kondygnacji nadziemnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_median_wohn` | BDOT10k: mediana liczby kondygnacji nadziemnych budynków mieszkalnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_geschosse_mittel_wohn` | BDOT10k: średnia liczby kondygnacji nadziemnych budynków mieszkalnych; puste poniżej 30 budynków o znanej liczbie kondygnacji |
| `geb_grundflaeche_m2` | BDOT10k: suma powierzchni obrysów budynków bez zniszczonych, m² |
| `geb_grundflaeche_wohn_m2` | BDOT10k: suma powierzchni obrysów budynków mieszkalnych, m² |
| `geb_flaeche_m2` | powierzchnia jednostki, m² |
| `geb_bebauungsdichte_wert` | wskaźnik zabudowy (udział powierzchni zabudowy w powierzchni jednostki): 100 × zaehler / nenner, % |
| `geb_bebauungsdichte_zaehler` | licznik: powierzchnia obrysów budynków, m² |
| `geb_bebauungsdichte_nenner` | mianownik: powierzchnia jednostki, m² |
| `geb_bebauungsdichte_anzeige` | sposób prezentacji wartości |
| `geb_geschossflaeche_naeherung_wert` | przybliżona intensywność zabudowy: Σ(powierzchnia obrysu × liczba kondygnacji) / powierzchnia jednostki; orientacyjnie, nie wartość urzędowa |
| `geb_geschossflaeche_naeherung_zaehler` | licznik: Σ(powierzchnia obrysu × liczba kondygnacji), m² |
| `geb_geschossflaeche_naeherung_nenner` | mianownik: powierzchnia jednostki, m² |
| `geb_geschossflaeche_naeherung_abzeichen` | oznaczenie wartości |
| `klimat_flaeche_ha` | powierzchnia jednostki w granicach miasta, ha |
| `klimat_abdeckung` | udział powierzchni jednostki objęty klasami pokrycia terenu BDOT10k, % |
| `klimat_ha_bebauung` | BDOT10k: powierzchnia klasy pokrycia terenu: zabudowa (PTZB), ha |
| `klimat_ha_verkehr` | BDOT10k: powierzchnia klasy pokrycia terenu: tereny komunikacyjne i place (PTKM, PTPL), ha |
| `klimat_ha_gruen` | BDOT10k: powierzchnia klasy pokrycia terenu: zieleń (PTRK, PTUT, roślinność trawiasta z PTTR), ha |
| `klimat_ha_wald` | BDOT10k: powierzchnia klasy pokrycia terenu: lasy i zadrzewienia (PTLZ), ha |
| `klimat_ha_wasser` | BDOT10k: powierzchnia klasy pokrycia terenu: wody (PTWP), ha |
| `klimat_ha_acker` | BDOT10k: powierzchnia klasy pokrycia terenu: grunty orne (uprawy z PTTR), ha |
| `klimat_ha_sonstige` | BDOT10k: powierzchnia klasy pokrycia terenu: pozostałe (PTGN, PTSO, PTWZ, PTNZ), ha |
| `klimat_anteil_bebauung` | BDOT10k: udział w sumie klas pokrycia terenu: zabudowa (PTZB), % |
| `klimat_anteil_verkehr` | BDOT10k: udział w sumie klas pokrycia terenu: tereny komunikacyjne i place (PTKM, PTPL), % |
| `klimat_anteil_gruen` | BDOT10k: udział w sumie klas pokrycia terenu: zieleń (PTRK, PTUT, roślinność trawiasta z PTTR), % |
| `klimat_anteil_wald` | BDOT10k: udział w sumie klas pokrycia terenu: lasy i zadrzewienia (PTLZ), % |
| `klimat_anteil_wasser` | BDOT10k: udział w sumie klas pokrycia terenu: wody (PTWP), % |
| `klimat_anteil_acker` | BDOT10k: udział w sumie klas pokrycia terenu: grunty orne (uprawy z PTTR), % |
| `klimat_anteil_sonstige` | BDOT10k: udział w sumie klas pokrycia terenu: pozostałe (PTGN, PTSO, PTWZ, PTNZ), % |
| `klimat_anteil_bebauung_verkehr` | BDOT10k: udział w sumie klas pokrycia terenu: zabudowa i tereny komunikacyjne razem, % |
| `klimat_anteil_gruen_wald` | BDOT10k: udział w sumie klas pokrycia terenu: zieleń i lasy razem, % |
| `klimat_einwohner` | mieszkańcy z siatki Eurostatu, podstawa dla zieleni na mieszkańca |
| `klimat_gruen_je_ew` | zieleń i lasy na mieszkańca, m² |
| `wkt` | geometria jako WKT w EPSG:2178 |

### `siatka_1km_odbl`

| Pole | Znaczenie |
|---|---|
| `id` | kod komórki siatki Eurostatu 1 km (EPSG:3035, narożnik południowo-zachodni) |
| `st` | dzielnica według środka komórki (granice z OSM) |
| `ew` | mieszkańcy (siatka Eurostatu 2021) |
| `a_ges` | suma trzech grup wieku w komórce |
| `q_u15` | udział mieszkańców poniżej 15 lat, % |
| `q_65p` | udział mieszkańców w wieku 65 lat i więcej, % |
| `fussweg_m_apotheke` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: apteka (OSM), m |
| `fussweg_m_arzt` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: lekarz lub przychodnia (OSM amenity=doctors), m |
| `fussweg_m_haltestelle_takt` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: przystanek klasy częstotliwości kursowania I lub II, m |
| `fussweg_m_park` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: park lub skwer (BDOT10k), m |
| `fussweg_m_pflege` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: dom opieki (OSM), m |
| `fussweg_m_przedszkole` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: przedszkole, m |
| `fussweg_m_spielplatz` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: plac zabaw ogólnodostępny (OSM), m |
| `fussweg_m_supermarkt` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: supermarket lub sklep spożywczy (OSM), m |
| `fussweg_m_szkola` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: szkoła dowolnego typu (BDOT10k nie rozróżnia typów), m |
| `fussweg_m_szpital` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: szpital, m |
| `fussweg_m_zlobek` | dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: żłobek, m |
| `wkt` | geometria jako WKT w EPSG:2178 |

### `dostepnosc`

| Pole | Znaczenie |
|---|---|
| `st` | dzielnica (01–18); puste = całe miasto |
| `nazwa` | nazwa dzielnicy albo miasta |
| `ew` | liczba mieszkańców obszaru (siatka Eurostatu, wartość zaokrąglona) |
| `kennzahl` | wskaźnik |
| `art` | rodzaj celu |
| `methode` | sposób pomiaru odległości |
| `einheit` | jednostka wartości |
| `status` | status wartości |
| `vorlaeufig` | 1 = wartość wstępna (szkoły bez obwodów szkolnych); puste = nie dotyczy |
| `q` | źródło (klucz w tabeli licencje) |
| `richtwert_wert` | promień ze standardu urzędowego, z którym porównano |
| `richtwert_einheit` | jednostka promienia |
| `richtwert_q` | źródło standardu (klucz w tabeli licencje) |
| `richtwert_seite` | miejsce w akcie prawnym (artykuł, strona) |
| `radius_m` | promień w metrach, w którym liczono (przy udziale w promieniu, przystankach i parkach); puste = nie dotyczy |
| `wert` | wartość wskaźnika; puste poniżej progu tajemnicy statystycznej |
| `zaehler` | licznik wskaźnika (np. mieszkańcy w promieniu, powierzchnia parków) |
| `nenner` | mianownik wskaźnika (np. mieszkańcy, liczba placówek) |
| `stand` | stan danych (data) |

### `placowki_osm`

| Pole | Znaczenie |
|---|---|
| `id` | identyfikator obiektu OSM (n = węzeł, w = linia lub obszar) |
| `art` | rodzaj placówki |
| `unterart` | specjalność lekarza z tagu OSM healthcare:speciality (wartości OSM, po angielsku); puste = brak tagu |
| `q` | źródło (klucz w tabeli licencje) |
| `x` | współrzędna x (wschód) w EPSG:2178, m |
| `y` | współrzędna y (północ) w EPSG:2178, m |

### `osm_heritage_start_date`

| Pole | Znaczenie |
|---|---|
| `h` | obiekt ma tag heritage; 1 = tak, 0 = nie |
| `ep` | okres budowy z tagu start_date (klasa, nigdy pojedynczy rok); puste = brak lub niejednoznaczne |
| `w` | budynek mieszkalny (FOBUD); puste = brak budynku; 1 = tak, 0 = nie |
| `mfh` | budynek wielorodzinny (PFBUD); puste = brak budynku; 1 = tak, 0 = nie |
| `del` | delegatura (nazwa z BDOT10k); puste = bez przypisania |
| `polozenie_sprawdzone` | położenie tego punktu sprawdzone osobno na ortofotomapie (wszędzie 0: sprawdzono co najwyżej losową próbę warstwy, wynik w CZYTAJ.md); 1 = tak, 0 = nie |
| `x` | współrzędna x (wschód) w EPSG:2178, m |
| `y` | współrzędna y (północ) w EPSG:2178, m |

### `zbk_budynki`

| Pole | Znaczenie |
|---|---|
| `art` | rodzaj budynku według wykazu ZBK |
| `eig` | własność według wykazu ZBK (punkty tylko bez udziału osób prywatnych) |
| `st` | dzielnica według wykazu ZBK |
| `gs` | liczba kondygnacji nadziemnych (BDOT10k LICZ_KONDY) |
| `fn` | przeważająca funkcja przypisanego budynku BDOT10k (PFBUD); puste = brak |
| `h` | wysokość budynku, m (zob. hq) |
| `hq` | pochodzenie wysokości |
| `typ` | typologia (szacunek); puste = brak kandydata |
| `x` | współrzędna x (wschód) w EPSG:2178, m |
| `y` | współrzędna y (północ) w EPSG:2178, m |

### `zbk_typologia_dzielnice`

| Pole | Znaczenie |
|---|---|
| `st` | numer dzielnicy (01–18) |
| `szacunek` | wartości są szacunkiem; 1 = tak, 0 = nie |
| `mfh` | budynki wielorodzinne eksploatowane (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny) |
| `blok` | szacunek: w tym kandydaci na bloki (liczba kondygnacji co najmniej 4, powierzchnia obrysu co najmniej 250 m², prostokątność co najmniej 0,85); łącznie z kategorią osiedle |
| `osiedle` | szacunek: kandydaci na blok na osiedlu blokowym (liczba innych kandydatów w promieniu 150 m co najmniej 9) |
| `blok_angebaut` | wskazówka, nie reguła: kandydaci na blok ze wspólną granicą o długości co najmniej 3 m z innym budynkiem BDOT10k (zabudowa pierzejowa, typowa dla kamienic) |
| `osiedle_angebaut` | jak blok_angebaut, tylko kandydaci na osiedlu blokowym |

### `licencje`

| Pole | Znaczenie |
|---|---|
| `plik` | plik GeoPackage |
| `warstwa` | warstwa |
| `licencja_pliku` | licencja warstwy w tym pliku |
| `licencja_zrodla` | licencja źródła |
| `zrodlo` | źródło |
| `nota` | nota o źródle do podania (dosłownie) |

## Wartości kodowane

| Pole | Wartość | Znaczenie |
|---|---|---|
| `flaeche_quelle` | `bdot10k` | granica z BDOT10k (PRG) |
| `nsp_weg` | `tabelle` | tabela GUS dla całej jednostki |
| `geb_bebauungsdichte_anzeige` | `anteil` | pokazywane jako udział w % |
| `geb_geschossflaeche_naeherung_abzeichen` | `orientacyjnie` | orientacyjnie |
| `anteil_grund` | `bezugsflaeche_zu_klein` | powierzchnia odniesienia za mała |
| `art` | `park` | park lub skwer (BDOT10k) |
| `art` | `przedszkole` | przedszkole |
| `art` | `szkola` | szkoła dowolnego typu (BDOT10k nie rozróżnia typów) |
| `art` | `szpital` | szpital |
| `art` | `zlobek` | żłobek |
| `q` | `bdot10k` | BDOT10k (GUGiK) |
| `status` | `lage_ohne_kapazitaet` | tylko położenie, bez liczby miejsc i uczniów |
| `verkehrsmittel` | `bus` | autobus |
| `verkehrsmittel` | `bus+tram` | autobus i tramwaj |
| `verkehrsmittel` | `tram` | tramwaj |
| `taktklasse` | `I` | odjazdy na godzinę w kierunku: co najmniej 6 |
| `taktklasse` | `II` | odjazdy na godzinę w kierunku: co najmniej 2 |
| `taktklasse` | `III` | odjazdy na godzinę w kierunku: co najmniej 1 |
| `taktklasse` | `unter III` | odjazdy na godzinę w kierunku: mniej niż 1 |
| `r` | `muzeum` | zespół muzealny |
| `r` | `pamiec` | miejsce pamięci narodowej |
| `r` | `twierdza` | twierdza lub forteca |
| `r` | `zabudowa` | zespół zabudowy historycznej |
| `q` | `wd` | Wikidane (CC0 1.0) |
| `ep` | `1800_1866` | 1800–1866 |
| `ep` | `1867_1918` | 1867–1918 |
| `ep` | `1919_1945` | 1919–1945 |
| `ep` | `1946_1989` | 1946–1989 |
| `ep` | `ab_1990` | od 1990 |
| `ep` | `vor_1800` | przed 1800 |
| `nsp_weg` | `rejony` | suma rejonów statystycznych |
| `kennzahl` | `anteil_in_radius` | udział mieszkańców z placówką w promieniu ze standardu urzędowego (richtwert_wert), % |
| `kennzahl` | `ew_je_einrichtung` | mieszkańcy na jedną placówkę |
| `kennzahl` | `gruen_in_radius` | udział mieszkańców z parkiem lub skwerem w odległości 500 m dojścia pieszego, % |
| `kennzahl` | `gruen_m2_je_ew` | powierzchnia parków i skwerów (BDOT10k) na mieszkańca, m² |
| `kennzahl` | `oepnv_takt` | udział mieszkańców z przystankiem klasy I lub II w odległości 500 m, % |
| `art` | `haltestelle_takt` | przystanek klasy częstotliwości kursowania I lub II |
| `methode` | `fussweg` | dojście piesze siecią dróg OSM od środka komórki 1 km |
| `methode` | `luftlinie` | odległość w linii prostej od środka komórki 1 km |
| `einheit` | `%` | procent |
| `einheit` | `ew_je_einrichtung` | mieszkańcy na placówkę |
| `einheit` | `m2_je_ew` | m² na mieszkańca |
| `status` | `orientierung` | wartość orientacyjna, nie urzędowa |
| `q` | `ztp` | GTFS ZTP Kraków |
| `richtwert_einheit` | `m` | metry |
| `richtwert_q` | `prawo_oswiatowe` | ustawa Prawo oświatowe |
| `art` | `apotheke` | apteka (OSM) |
| `art` | `arzt` | lekarz lub przychodnia (OSM amenity=doctors) |
| `q` | `osm` | OpenStreetMap |
| `art` | `M` | mieszkalny |
| `art` | `MP` | mieszkalny i przychodnia |
| `art` | `MU` | mieszkalny i użytkowy |
| `art` | `P` | przychodnia |
| `art` | `U` | użytkowy |
| `eig` | `gmina` | Gmina Miejska Kraków |
| `eig` | `publiczne_mieszane` | kilku właścicieli publicznych albo województwo |
| `eig` | `skarb_panstwa` | Skarb Państwa |
| `hq` | `geschosse` | kondygnacje × 3 m (szacunek) |
| `hq` | `lod2` | model 3D LoD2 (GUGiK, stan 2017) |
| `typ` | `blok` | kandydat na blok (szacunek) |
| `typ` | `osiedle` | kandydat na blok na osiedlu blokowym (szacunek) |

## Jak cytować

Kiezatlas Kraków, Stiebitz Souverain Systems UG (haftungsbeschränkt), https://souverain-systems.de/kiezatlas/krakow/, stan danych 2026-11-14 (dane do pobrania). Szczegóły: `CITATION.cff` w repozytorium. Do każdej warstwy należy podać noty o źródłach z tabeli `licencje`.

Błąd w danych? kontakt@souverain-systems.de
