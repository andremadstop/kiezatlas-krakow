# Nowe miasto

Jak przenieść przepis Kiezatlas na inne miasto w Polsce lub w UE. Wersja angielska (skrót): [`new-city.md`](new-city.md).
Uruchomienie: [`uruchomienie.md`](uruchomienie.md).

Stan: 14.11.2026. Ten sam kod działa dziś dla dwóch miast: Krakowa (`config/krakow.yaml`) i Poczdamu
(`pruefen/gegenprobe_potsdam/ort.yaml`, kontrola krzyżowa `pruefen/gegenprobe_potsdam.sh`, ostatnio 0 odchyleń, zob.
[`rundgang.md`](rundgang.md), „Ergebnis der Gegenprobe“). Kraków nie jest jednak jeszcze w pełni sparametryzowany:
część ścieżek i kodów jest wpisana w skryptach. Ta strona mówi uczciwie, co jest konfiguracją, a co trzeba zmienić w
kodzie.

## 1. Co zależy od miasta

| Warstwa | Gdzie | Konfiguracja czy kod |
|---|---|---|
| Nazwa, języki, adres, układ współrzędnych do obliczeń, mapa, podział na dzielnice, tematy, strony, nawigacja | `config/<miasto>.yaml` (zmienna `KIEZ_CONFIG`) | konfiguracja |
| Progi, promienie, dzień odniesienia rozkładu jazdy, ścieżki GTFS i BDOT10k | `config/richtwerte.yaml` | konfiguracja |
| Kod powiatu (TERYT `1261`), poziom OSM dzielnic (`admin_level` 9) | `skripte/raum_bevoelkerung.py` (`TERYT_POWIAT`, `OSM_EBENE`) | kod |
| Ścieżki danych surowych (`2026-11-13/03_gebaeude/1261_SHP.zip`, `eingang/lod2_1261*` …) | nagłówki skryptów w `skripte/`, lista w `skripte/kette.py` | kod (14 skryptów obliczeniowych wymienia `1261`) |
| Suma SHA256 BDOT10k i czcionek mapowych | `skripte/27_grundkarte.py` (`BDOT_SHA256`, `SCHRIFTEN`) | kod |
| Teksty stron (krótkie i długie) | `texte/<język>/*.js`, `texte/<język>/bloecke/quelle/` | treść |
| Strony | `vorlagen/<strona>.html`, lista `seiten` w konfiguracji | treść i konfiguracja |
| Źródła i licencje | `QUELLEN.md`, `daten/LIZENZ.md`, `daten/pobierz/licencje.csv` (z `skripte/16_export_krakow.py`) | dokumentacja i kod |
| Tabele bazy danych | `sql/*.sql`; SRID = `rechen_srid` (sprawdza `pruefen/geruest.py`) | kod |

## 2. Kraków i Poczdam obok siebie

Wartości dosłownie z obu plików konfiguracji.

| Klucz | Kraków (`config/krakow.yaml`) | Poczdam (`pruefen/gegenprobe_potsdam/ort.yaml`) |
|---|---|---|
| `ort` | `krakow` | `potsdam` |
| `sprachen` | `[pl, en, de]` | `[de]` |
| `rechen_srid` | `2178` (ETRS89 / Poland CS2000 zone 7) | `25833` (ETRS89 / UTM zone 33N) |
| `karte.mitte` | `[19.94, 50.06]` | `[13.06, 52.4]` |
| `karte.grundkarte` | własne kafle wektorowe z BDOT10k (`daten/grundkarte/kacheln/…`) | kafle rastrowe basemap.de (usługa BKG) |
| `karte.luftbild` | `null` (ortofotomapa GUGiK: pobieranie kafli zabronione) | WMS DOP20 Brandenburgii |
| `gliederung` | 18 dzielnic w czterech dzielnicach historycznych, lista `teile` | dzielnice z danych, osiem okręgów, `teile: []` |
| `themen` | ludność i udziały wieku z siatki Eurostat 1 km 2021 | Zensus 2022 (siatka 100 m): wiek, budynki, ogrzewanie |
| `seiten` | 18 stron | 9 stron |

W Poczdamie (repozytorium Kiezatlas Potsdam, osobne) dane pochodzą z innych źródeł: niemiecki spis 2022 w siatce
100 m, granice dzielnic miasta (dl-de/zero-2-0), budynki z ALKIS. To pokazuje, gdzie przebiega granica: kod stron i
konfiguracja są wspólne, a czytniki źródeł są zależne od kraju.

## 3. Kroki dla nowego miasta w Polsce

1. Skopiować `config/krakow.yaml` na `config/<miasto>.yaml`, ustawić `KIEZ_CONFIG=config/<miasto>.yaml`.
2. `rechen_srid`: strefa układu PL-2000 dla miasta (5–8, południki 15°, 18°, 21°, 24° E). Kod musi być w
   `SRS_NAMEN` w `skripte/ort_konfig.py`, a ten sam SRID w `sql/*.sql` (inaczej `pruefen/geruest.py` zgłasza błąd).
3. `karte`: środek i ramka (WGS 84), `grundkarte` zostaje (własne kafle z BDOT10k), `luftbild: null`.
4. `gliederung.teile`: jednostki pomocnicze miasta (dzielnice, osiedla) z numerem i nazwą; `gruppen` jeśli istnieją.
   Granice z OSM: sprawdzić, na jakim `admin_level` leżą w OSM, i ustawić `OSM_EBENE`.
5. Kod TERYT powiatu w `skripte/raum_bevoelkerung.py` i ścieżki `…/<TERYT>_SHP.zip`, `lod2_<TERYT>*` w skryptach
   (lista: `grep -n 1261 skripte/*.py`).
6. Dane: BDOT10k i LoD2 dla powiatu (geoportal.gov.pl, te same warunki co dla Krakowa), siatka Eurostat (cała UE),
   NSP 2021 (GUS), GTFS przewoźnika (licencja do sprawdzenia przed pobraniem), wyciąg OSM województwa. Każde
   źródło z licencją i notą dosłowną do `QUELLEN.md`, zanim zostanie użyte; licencja niejasna: nie używać.
7. Teksty w `texte/<język>/` przejrzeć pod kątem nazw i zdań o Krakowie (`grep -rn Krak texte/`).
8. `./atlas.sh trocken`, potem `./atlas.sh alles`, na końcu `./pruefen.sh` na zielono i nowy stan w `belege/`.

## 4. Miasto w innym kraju UE

Siatka Eurostat 1 km 2021 i OpenStreetMap są dostępne w całej UE; wszystko, co z nich liczone (gęstość, udziały
wieku, odległości piesze, porównanie dwóch miast), przenosi się bez zmian w kodzie poza konfiguracją. BDOT10k, LoD2
GUGiK, NSP i rejestr cen nieruchomości są polskie: dla innego kraju trzeba napisać własne czytniki (wzór: Poczdam,
gdzie dane budynków pochodzą z ALKIS, a podkład z basemap.de). Podkład z usługi zewnętrznej (jak w Poczdamie)
oznacza zapytania do obcego serwera w czasie działania strony; przepis krakowski unika tego dzięki własnym kaflom.

## 5. Czego jeszcze brakuje (uczciwie)

- Ścieżki i kod powiatu są wpisane w skryptach (punkt 5 wyżej), a nie w konfiguracji.
- `config/krakow.yaml`, sekcja `quellen`, jest pusta: dane nie są ładowane przez `pipeline.laden`, lecz czytane
  przez skrypty z `$KIEZ_DATEN`.
- `package.json` nosi jeszcze nazwę i opis Kiezatlas Potsdam (pakiety są takie same, `npm ci` działa).
