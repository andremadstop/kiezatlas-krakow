# Uruchom u siebie

Instrukcja dla zespołu, który chce samodzielnie uruchomić i rozwijać Kiezatlas Kraków na własnym serwerze, od pustego
komputera do gotowych stron. Wersja angielska: [`running.md`](running.md). Nowe miasto: [`nowe-miasto.md`](nowe-miasto.md).
Przejęcie projektu: [`przekazanie.md`](przekazanie.md).

Stan: 14.11.2026. Wszystkie czasy i rozmiary poniżej są zmierzone (źródło w każdej tabeli); to, czego nie zmierzono,
jest oznaczone jako „nie zmierzono”. Polecenia i nazwy plików są takie jak w repozytorium; komunikaty skryptów są po
niemiecku, bo tak powstał kod.

> **Brakuje jeszcze migawki danych surowych (stan 15.11.2026).** Repozytoria są publiczne (Apache-2.0): to
> repozytorium <https://github.com/andremadstop/kiezatlas-krakow> (`git clone` w punkcie 2), Geodaten-Import-Pipeline <https://github.com/andremadstop/geodaten-import-pipeline> (kroki z bazą danych, punkt 3)
> i Kiezatlas Potsdam <https://github.com/andremadstop/kiezatlas-potsdam> (opcjonalne, tylko porównanie). Migawka danych surowych (droga C) nie ma jeszcze
> rekordu Zenodo ani DOI; do tego czasu można o nią zapytać wydawcę pod adresem z `config/krakow.yaml`, klucz
> `meldeweg`. Bez migawki źródła pobiera się drogami A i B.

## W skrócie

```sh
./atlas.sh trocken --ohne-datenbank   # sprawdza narzędzia i pliki wejściowe kroków bez bazy danych; niczego nie zapisuje
./atlas.sh alles --ohne-datenbank     # bez bazy: liczenie, pliki do pobrania, strony i wszystkie kontrole (./pruefen.sh)
./atlas.sh liste                      # lista 25 kroków
# z bazą danych (najpierw punkt 3: .env, Docker, Geodaten-Import-Pipeline):
./atlas.sh trocken                    # sprawdza także bazę danych
./atlas.sh alles                      # cały łańcuch razem z krokami bazodanowymi
```

Bez `--ohne-datenbank` oba polecenia zatrzymują się od razu, gdy brakuje `.env`, Dockera albo bazy danych
(`Umgebungsdatei … fehlt`, `docker nicht gefunden`); wyniki kroków bazodanowych w `daten/` zostają wtedy takie, jakie
są w repozytorium.

`./atlas.sh trocken` kończy się kodem 0, gdy są wszystkie obowiązkowe pliki wejściowe, a kodem 2 z listą braków, gdy
czegoś brakuje. Brak pliku pobieranego ręcznie, bez którego krok sobie radzi (powietrze, rynek mieszkaniowy, rejestry
zabytków, rejony statystyczne), to tylko wskazówka: odpowiedni plik zostaje danymi przykładowymi (`fixture: true`), a
strony to mówią. `./atlas.sh alles` zatrzymuje się na pierwszym błędzie i podaje, od którego kroku wznowić
(`./atlas.sh alles --ab <krok>`). Protokół każdego przebiegu: `berichte/kette/<czas UTC>.log`.

## 1. Wymagania

| Narzędzie | Wersja (sprawdzona) | Do czego |
|---|---|---|
| Linux x86_64, `sh`, `git`, `tar`, `sha256sum` | – | wszystko |
| Python 3.11 lub nowszy w systemie | – | sam łańcuch `skripte/kette.py` i `skripte/schnappschuss.py` (tylko biblioteka standardowa) |
| uv | 0.11.3 | Python 3.13 i pakiety z `requirements*.txt` (z sumami kontrolnymi), w łańcuchu zawsze `--offline` |
| Node.js | 22 (ostatnio v22.23.4) | kontrole w przeglądarce, `node --check` |
| npm, pakiety z `package-lock.json` | Playwright 1.64.1, axe-core 4.14.0 | kontrole w przeglądarce (Chromium) |
| Docker z `docker compose` | – | PostGIS `postgis/postgis:16-3.6` (digest w `docker-compose.yml`), tylko do liczenia |
| Poppler `pdftotext` | 26.10.0 | wykaz budynków ZBK (atlas modernizacji) |
| Czcionka Noto Sans (Regular, Medium, Italic) | w repozytorium w `schriften/noto/` (SIL OFL 1.1, licencja obok plików; bajt w bajt jak pakiet Arch `noto-fonts 1:2026.10.01-1`), nic nie trzeba instalować | podpisy na podkładzie mapowym; `skripte/27_grundkarte.py` sprawdza SHA256 każdego pliku |
| Repozytorium Geodaten-Import-Pipeline (<https://github.com/andremadstop/geodaten-import-pipeline>) | commit `12bae5bc96cf34355c8c5a723eb444e66f776f2d` (Apache-2.0) | kroki bazodanowe `skripte/lauf.sh` (`einrichten`: role i uprawnienia w bazie; także `laden`, `auswerten`, `rechte`) |
| Repozytorium Kiezatlas Potsdam (<https://github.com/andremadstop/kiezatlas-potsdam>, opcjonalnie) | – (Apache-2.0) | tylko porównanie Kraków–Poczdam (`skripte/41_porownanie.py`) i kontrola krzyżowa Poczdamu (do niej także GSAP 3.15.1 w `vendor/`, którego nie ma w repozytorium; patrz `NOTICE`) |

**Skąd wziąć dwa pozostałe repozytoria:** oba są publiczne na GitHubie, na licencji Apache-2.0 (sprawdzone
15.11.2026). Geodaten-Import-Pipeline: <https://github.com/andremadstop/geodaten-import-pipeline>, w commicie `12bae5bc96cf34355c8c5a723eb444e66f776f2d` (ten stan ma
też DOI [10.5281/zenodo.24073612](https://doi.org/10.5281/zenodo.24073612)); obok tego repozytorium jako
`../geodaten-import-pipeline` (inna ścieżka: zmienna `PIPELINE_DIR`), polecenia w punkcie 3. W innym commicie
`skripte/lauf.sh` przerywa pracę. Kiezatlas Potsdam: <https://github.com/andremadstop/kiezatlas-potsdam>, obok jako `../kiezatlas-potsdam` (inna ścieżka:
`KIEZ_POTSDAM`). Bez Geodaten-Import-Pipeline nie da się przygotować bazy danych; pliki, które jej potrzebują (dojścia
piesze, `erreichbar_fuss_odbl.js`, `planer_fuss_odbl.js`), zostają wtedy takie, jakie są w repozytorium.

### Miejsce na dysku (zmierzone 14.11.2026)

| Co | Rozmiar | Jak zmierzono |
|---|---|---|
| Repozytorium (pliki w git) | 26,5 MB | `git ls-files` i `du -cb` |
| Dane surowe `$KIEZ_DATEN` po wszystkich przebiegach | 672 MB, w tym 70 MB danych pochodnych (`abgeleitet/`) i 194 MB drugiej kopii wyciągu OSM (`osm/`) | `du -sh` |
| Migawka danych surowych (archiwum tar) | około 404 MB (zawartość 404 127 036 B, próba 15.11.2026) | `skripte/schnappschuss.py`, poniżej |
| Obraz Docker PostGIS | 950 576 003 B | `docker image inspect` |
| Wolumen bazy danych po pełnym przebiegu | 469,1 MB | `docker system df -v` |
| `node_modules` | 81 MB | `du -shL` |
| Chromium dla Playwright (przeglądarka, powłoka bez okna, ffmpeg) | 681 MB | `du -shc` w `~/.cache/ms-playwright` |
| Pamięć podręczna uv | nie zmierzono osobno | |

Suma tabeli (bez pamięci podręcznej uv): około 3,3 GB. Pamięć RAM: najcięższy zmierzony krok (atlas modernizacji)
potrzebował 938 MB (tabela czasów niżej); długie przebiegi warto ograniczać, np.
`KETTE_PRAEFIX="systemd-run --user --scope -p MemoryMax=8G" ./atlas.sh alles`.

## 2. Kod i środowisko

```sh
# narzędzia (jak w .github/workflows/pruefen.yml): uv 0.11.3, Python zarządzany przez uv, Node.js 22
pipx install uv==0.11.3
export UV_PYTHON_PREFERENCE=only-managed     # własny Python uv, nigdy systemowy
uv python install 3.13.12                    # wersja z plików potwierdzeń z 14.11.2026
node --version                               # v22.x (z dystrybucji albo z nodejs.org)
git clone https://github.com/andremadstop/kiezatlas-krakow kiezatlas-krakow
cd kiezatlas-krakow
export KIEZ_DATEN="$(cd .. && pwd)/kiezatlas-daten/krakow"; mkdir -p "$KIEZ_DATEN"
# jednorazowo, z siecią: pakiety do pamięci podręcznej uv
uv run --python 3.13 --no-project --with-requirements requirements.txt python -c pass
uv run --python 3.13 --no-project --with-requirements requirements.txt --with-requirements requirements-pruefen.txt python -c pass
uv run --python 3.13 --no-project --with-requirements requirements.txt --with-requirements requirements-schriften.txt python -c pass
npm ci                                         # pakiety z package-lock.json
npx playwright install --with-deps chromium    # kontrole w przeglądarce; instaluje też biblioteki systemowe (wymaga sudo/root)
```

**Wszystkie dalsze polecenia zakładają, że `KIEZ_DATEN` i `UV_PYTHON_PREFERENCE` są ustawione** (najlepiej w profilu
powłoki). Skrypty same przyjmują `../kiezatlas-daten/krakow`, ale polecenia powłoki w punkcie 4 używają wprost
`"$KIEZ_DATEN/…"`; przy pustej zmiennej zapisałyby do `/2026-11-13/…`. Bez `UV_PYTHON_PREFERENCE=only-managed` uv
może wziąć dowolny systemowy Python 3.13 z inną wersją poprawek, a ta wersja trafia potem do plików potwierdzeń (np.
`belege/DS_sanierung_lauf.md`); tak samo wersja Popplera z dystrybucji (sprawdzona: 26.10.0). Bez uprawnień root
samo `npx playwright install chromium` pobiera tylko przeglądarkę; potrzebne biblioteki systemowe (np.
`libglib-2.0.so.0`) musi wtedy zainstalować administrator. Potem łańcuch nie potrzebuje już sieci.

## 3. Baza danych (tylko do liczenia)

Strony są statyczne; baza PostGIS jest potrzebna tylko w krokach oznaczonych `[Datenbank]` (granice i komórki,
sieć dróg pieszych z OSM, odległości piesze).

```sh
cp .env.beispiel .env && chmod 600 .env    # dla każdej roli długie losowe hasło, np.:
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
docker compose up -d --wait db             # tylko 127.0.0.1, port 55462
git clone https://github.com/andremadstop/geodaten-import-pipeline ../geodaten-import-pipeline
git -C ../geodaten-import-pipeline checkout 12bae5bc96cf34355c8c5a723eb444e66f776f2d   # ustalony commit
skripte/lauf.sh einrichten                 # role i uprawnienia; potrzebuje ../geodaten-import-pipeline we wskazanym commicie
skripte/lauf.sh rechte                     # kontrola uprawnień, niczego nie zmienia
```

Bez bazy: `./atlas.sh alles --ohne-datenbank` liczy wszystko inne; pliki odległości pieszych w `daten/` zostają takie,
jakie są w repozytorium.

## 4. Źródła: trzy drogi

Każde źródło ma licencję, notę o źródle i drogę w [`QUELLEN.md`](../QUELLEN.md). Pliki leżą w `$KIEZ_DATEN` w
ścieżkach, których oczekują skrypty (ścieżki są zależne od miasta, zob. [`nowe-miasto.md`](nowe-miasto.md)).

### Droga A: automatycznie przez `skripte/abruf.py`

Jedyna droga sieciowa projektu: lista blokad, robots.txt, odstęp między zapytaniami i protokół
`$KIEZ_DATEN/abrufprotokoll.tsv`.

```sh
P="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt python -I"
# Foldery z datą, które łańcuch czyta dziś (lista miejsc w kodzie: rundgang.md, „Neuer Datenstand”).
# Nowy stan: ustawić datę pobrania, np. STAND=$(date +%F), i przestawić te miejsca.
STAND=2026-11-13
STAND_VERGLEICH=2026-11-14
$P skripte/abruf.py --abstand 30 https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip "$KIEZ_DATEN/$STAND/03_gebaeude/1261_SHP.zip"
$P skripte/abruf.py --abstand 30 https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/PL_PD_3035_GPKG.zip "$KIEZ_DATEN/$STAND/02_zensus/PL_PD_3035_GPKG.zip"
$P skripte/abruf.py --abstand 30 https://stat.gov.pl/download/gfx/portalinformacyjny/pl/defaultaktualnosci/6536/12/1/1/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx "$KIEZ_DATEN/$STAND/02_zensus/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx"
for f in A T M; do $P skripte/abruf.py --abstand 30 https://gtfs.ztp.krakow.pl/GTFS_KRK_$f.zip "$KIEZ_DATEN/$STAND/06_oepnv/GTFS_KRK_$f.zip"; done
$P skripte/abruf.py --abstand 30 "https://www.bip.krakow.pl/plik.php?zid=635620&wer=1&new=t&mode=shw" "$KIEZ_DATEN/zbk/$STAND/zbk_wykaz_2025-12.pdf"
$P skripte/abruf.py --abstand 30 "https://www.bip.krakow.pl/?dok_id=48482" "$KIEZ_DATEN/zbk/$STAND/bip_dok48482_ponowne.html"
$P skripte/abruf.py --abstand 30 "https://www.bip.krakow.pl/?dok_id=242410" "$KIEZ_DATEN/$STAND/10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html"
$P skripte/abruf.py --abstand 30 https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/DE_PD_3035_GPKG.zip "$KIEZ_DATEN/$STAND_VERGLEICH/41_vergleich/DE_PD_3035_GPKG.zip"
$P skripte/abruf.py --abstand 30 https://registry.npmjs.org/@fontsource/barlow/-/barlow-5.3.0.tgz "$KIEZ_DATEN/schriften/$STAND/barlow-5.3.0.tgz"
$P skripte/abruf.py --abstand 30 https://registry.npmjs.org/@fontsource/barlow-semi-condensed/-/barlow-semi-condensed-5.3.0.tgz "$KIEZ_DATEN/schriften/$STAND/barlow-semi-condensed-5.3.0.tgz"
$P skripte/abruf.py --abstand 30 https://registry.npmjs.org/@fontsource%2fbarlow/5.3.0 "$KIEZ_DATEN/schriften/$STAND/npm-barlow-latest.json"
$P skripte/abruf.py --abstand 30 https://registry.npmjs.org/@fontsource%2fbarlow-semi-condensed/5.3.0 "$KIEZ_DATEN/schriften/$STAND/npm-barlow-semi-condensed-latest.json"
```

Uwaga: adresy podają zawsze najnowszy stan źródła. Jeśli źródło się zmieniło (BDOT10k, GTFS co tydzień), sumy
kontrolne w `belege/rohdaten*.sha256` się nie zgadzają, a `skripte/27_grundkarte.py` przerywa działanie (zapisana suma SHA256
BDOT10k). Wtedy obowiązuje procedura „Neuer Datenstand” w [`rundgang.md`](rundgang.md) (nowy folder z datą, nowa lista
sum, nowy przebieg). Do dokładnego odtworzenia stanu z 14.11.2026 służy droga C. Dla pakietów czcionek w łańcuchu
użyto plików `…/latest` z 13.11.2026 (wtedy wersja 5.3.0); adres z numerem wersji `…/5.3.0` daje te same bajty
(sprawdzone 14.11.2026 przez `skripte/abruf.py`, `belege/fix-offen_npm_versioniert.log`: SHA256 `534c5006…` i `96a07a94…`, jak w
`belege/rohdaten-DF-schriften.sha256`), dlatego zapis pod nazwą `*-latest.json` przechodzi kontrolę sum. Strona BIP
`bip_dok242410_…` (bez informacji o licencji, brak w migawce) służy tylko kontroli powierzchni miasta; bez niej
`skripte/35_klimat.py` liczy dane tak samo i zaznacza w zapisie weryfikacji, że kontrola została pominięta.

### Droga B: ręcznie do `eingang/`, z `HERKUNFT.md`

Źródła, których nie wolno lub nie da się pobrać automatycznie, pobiera się w przeglądarce do `$KIEZ_DATEN/eingang/`. Dla
każdego pliku wpis w `$KIEZ_DATEN/eingang/HERKUNFT.md` (plik, adres, licencja z miejscem jej podania, data pobrania
`DD.MM.RRRR` w ostatniej kolumnie) i suma w `eingang/SHA256SUMS` (`sha256sum PLIK >> SHA256SUMS`).

| Plik w `eingang/` | Źródło | Bez niego |
|---|---|---|
| `*.osm.pbf` | wyciąg OpenStreetMap dla Małopolski (Geofabrik `malopolskie`), ODbL 1.0 | brak granic dzielnic; przebieg zostaje przerwany (krok `osm`, `sanierung`) |
| `lod2_1261_gml.zip` | GUGiK, Modele 3D budynków LoD2, powiat 1261 | krok `sanierung` zostaje przerwany; w kroku `gebaeude` wysokość tylko z liczby kondygnacji |
| `eea/*.geojson.zip` (tak pobrano 14.11.2026; działają też `*.geojson` lub `*.csv`) | EEA, „Air quality annual statistics” (instrukcja w `quellen-D7.md`) | `powietrze.js` zostaje danymi przykładowymi |
| `rcn/*.gpkg` | Rejestr cen nieruchomości, powiat 1261 (instrukcja w `quellen-DW.md`) | krok `wohnungsmarkt` pominięty, `mieszkania_odbl.js` zostaje danymi przykładowymi |
| `wikidata_zabytki_krakow.json`, `nid_rejestr_zabytkow.csv`, `gez_krakow.csv` | Wikidata, rejestr zabytków NID, gminna ewidencja zabytków (zapytanie i format w `quellen-DZ.md`) | `denkmale.js` zostaje danymi przykładowymi |
| `rejony_statystyczne.*` | geometria rejonów statystycznych GUS (wydanie 2021 nie zostało znalezione) | NSP dla dzielnic zostaje `null` |

Wyciąg OSM kopiuje krok `osm` (z `--uebernehmen`) do `$KIEZ_DATEN/osm/<stan>/` z sumą kontrolną.

### Droga C: migawka danych surowych

`skripte/schnappschuss.py` pakuje tylko te dane surowe, które wolno dalej rozpowszechniać (BDOT10k, LoD2, OSM, siatki
Eurostatu, NSP 2021, GTFS, wyciąg EEA o jakości powietrza, wynik zapytania do Wikidanych, pakiety czcionek Barlow, czcionka mapowa Noto Sans), z `SCHNAPPSCHUSS/SHA256SUMS`,
`LIZENZEN.md` (źródło, licencja, nota dosłownie) i `AUSGESCHLOSSEN.md` (każdy pominięty plik z powodem i sumą).
Archiwum jest powtarzalne bajt w bajt.

```sh
./atlas.sh schnappschuss --ziel /ścieżka/poza/repozytorium      # tworzy archiwum (zawartość 15.11.2026: 404 127 036 B)
python3 -I skripte/schnappschuss.py --pruefen ARCHIWUM.tar        # sprawdza archiwum według jego SHA256SUMS
mkdir -p "$KIEZ_DATEN" && tar -xf ARCHIWUM.tar -C "$KIEZ_DATEN"   # rozpakować do pustego folderu
```

Poza migawką zostają (powód w `AUSGESCHLOSSEN.md`): plik transakcji RCN (pojedyncze transakcje z położeniem, datą
i ceną; pobrać ręcznie według `quellen-DW.md`), wykaz ZBK (dane osobowe w metadanych PDF i udziały osób
prywatnych), strona BIP z powierzchnią miasta (brak licencji), dane pakietów npm (adresy e-mail opiekunów), strony
internetowe i dokumenty prawne jako potwierdzenia, granice MSIP (licencja nie pozwala na dalsze udostępnianie). Pięciu z nich łańcuch
potrzebuje: wykaz ZBK, stronę BIP z zasadami ponownego wykorzystywania, stronę BIP z powierzchnią miasta i oba pliki
npm trzeba po rozpakowaniu pobrać drogą A (polecenia wyżej);
`./atlas.sh trocken` je wymienia. Sprawdzone 14.11.2026 na rozpakowanej migawce z tymi pięcioma plikami:
`./atlas.sh trocken --ohne-datenbank` zielony; `02_bevoelkerung.py`, `20_bdot10k.py`, `dz_denkmale.py`,
`13_oepnv_krakow.py`, `15_planer_krakow.py`, `35_klimat.py`, `36_sanierung.py`, `41_porownanie.py` i
`skripte/schriften.py` z `--pruefen` dają te same pliki co w repozytorium; `27_grundkarte.py` z czcionką z migawki
(`--schrift-ordner`) daje ten sam `MANIFEST.sha256`. Wyciąg EEA i wynik Wikidanych są w migawce od 15.11.2026;
`32_powietrze.py` i `dz_denkmale.py` nie zostały jeszcze uruchomione na rozpakowanej migawce, która je zawiera.

**Powtarzalność jest potwierdzona tylko na komputerze wydawcy.** W świeżym kontenerze Debian (14.11.2026, te same
pakiety z sumami kontrolnymi, Python 3.13.12 zarządzany przez uv) `02_bevoelkerung.py --pruefen` zgłosił różnicę w
`daten/stadtteile_odbl.js`: współrzędne granic różniły się na 5. miejscu po przecinku (np. 19,98267 → 19,98268), a
wraz z nimi pliki liczone z granic (np. Prądnik Czerwony 643,6 → 643,7 ha w `belege/dk_klimat.md`, pliki klimatu,
budynków i mieszkań według dzielnic, pliki do pobrania). Pliki 3D i ich manifest były identyczne bajt w bajt.
Przyczyny nie zawężono (przypuszczenie, niesprawdzone: inna systemowa biblioteka matematyczna). W innym środowisku
należy się liczyć z takimi różnicami na ostatnim miejscu po przecinku; obraz referencyjny (Dockerfile z
przypiętą bazą), w którym powtarzalność byłaby potwierdzona, jest sprawą otwartą.

## 5. Uruchomienie łańcucha

```sh
./atlas.sh trocken
./atlas.sh alles                 # z kontrolą w przeglądarce na końcu
./atlas.sh alles --ohne-browser  # kontrole bez przeglądarki
```

Kolejność kroków jest taka jak w [`rundgang.md`](rundgang.md) („Schritte”): pakiety danych, potem porównanie, pliki do
pobrania, długie teksty i na końcu strony (`skripte/30_seiten.py`), inaczej pliki do pobrania i teksty po cichu się
starzeją. Pliki 3D budynków trafiają do nowego folderu z datą `$KIEZ_DATEN/abgeleitet/gebaeude/<data>-odbl/`, kafle
podkładu do `$KIEZ_DATEN/abgeleitet/grundkarte/<początek SHA256 BDOT10k>/`.

Ten krok zapisuje obok plików manifest `MANIFEST.sha256` (folder z 13 listopada 2026 ma tę samą listę jako `SHA256SUMS`). Serwer deweloperski i `skripte/deploy_kopie.py` biorą folder
podany w `config/gebaeude_3d.json` (obecnie `2026-11-13-odbl/`); jeśli nie ma w nim manifestu, biorą najnowszy folder
`*-odbl/` z manifestem. Inny folder: `--gebaeude <folder>` w obu, np.
`node skripte/entwicklung_server.mjs --gebaeude "$KIEZ_DATEN/abgeleitet/gebaeude/<data>-odbl"`. Kopia do publikacji
przyjmuje tylko manifest z sumą kontrolną z `config/gebaeude_3d.json`; ponowne, bajtowo identyczne przeliczenie daje
dokładnie tę sumę. Sprawdzenie bez zapisu: `python -I skripte/20_bdot10k.py --pruefen --geometrie <folder>`.

Podgląd lokalny z podkładem mapowym: `node skripte/entwicklung_server.mjs --port 8080` (tylko 127.0.0.1). Do
publikacji wystarczy dowolny serwer WWW plików statycznych; strony nie odwołują się w czasie działania do żadnych
obcych usług. Co trzeba skopiować obok stron (kafle podkładu, pliki 3D), opisuje `skripte/deploy_kopie.py` i
`docs/auslieferung.md` (ten opis dotyczy obecnego serwera wydawcy; adres docelowy trzeba zastąpić własnym).

**Oczekiwany koniec po drodze C:** `./atlas.sh alles` zatrzymuje się w ostatnim kroku komunikatem

```
HALT: Schritt pruefen mit Rückgabe 1 nach … s; volle Ausgabe im Protokoll berichte/kette/. Weiter nach der Behebung mit: ./atlas.sh alles --ab pruefen
```

i kodem wyjścia 3. Wszystkie wcześniejsze kroki zostały wykonane, strony są zapisane. Przyczyną są listy sum
kontrolnych `belege/rohdaten*.sha256`, które wymieniają pliki surowe pominięte w migawce (`AUSGESCHLOSSEN.md` w
archiwum); w przebiegu z 14.11.2026 było to sześć list (D5, D6, D7, DE, DS, DW). W protokole w `berichte/kette/`
należy sprawdzić, czy zgłoszenia dotyczą tylko tych list; przyczynę każdego innego zgłoszenia trzeba najpierw usunąć. Wyjątek poza
komputerem wydawcy: kontrole, które przeliczają granice lub pliki z nich liczone (np. `02_bevoelkerung.py --pruefen`),
mogą zgłosić różnice na 5. miejscu po przecinku we współrzędnych (punkt 4, droga C); `git diff` pokazuje, czy
zmieniły się tylko takie ostatnie cyfry. Pliki brakujące w migawce pobiera się drogą A lub B; potem uruchomić `./atlas.sh alles --ab pruefen` (nie sprawdzono, czy kończy się wtedy na zielono).

Nagłówki bezpieczeństwa (propozycja): strony ładują wszystko z własnego serwera, więc można ustawić wąską politykę
Content-Security-Policy, np. w nginx:

```nginx
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'sha256-…'; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none'" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

Jedynym skryptem wbudowanym jest wiersz `window.KIEZ_V="…"` dodawany przez `skripte/deploy_kopie.py`; jego skrót
(`'sha256-…'`) zmienia się przy każdej kopii i `deploy_kopie.py` go wypisuje, trzeba go więc odnawiać przy każdej
publikacji. MapLibre potrzebuje `worker-src blob:`, okienka mapy ustawiają kolory atrybutem `style`. Uzasadnienie i
zakres sprawdzenia: `docs/auslieferung.md`, sekcja „Sicherheits-Header”.

## 6. Czas (zmierzony)

Komputer pomiarowy: x86_64, 8 rdzeni / 16 wątków, 62 GB RAM. Czas kroku liczącego zmierzono jego trybem
`--pruefen` (liczy całość, porównuje bajt w bajt, niczego nie zapisuje) 14.11.2026; RAM = maksymalna pamięć
rezydentna procesu.

| Krok | Czas | RAM | Źródło |
|---|---|---|---|
| `bevoelkerung` (`02_bevoelkerung.py`) | 88,3 s | 473 MB | pomiar 14.11.2026 |
| `gebaeude` (`20_bdot10k.py`) | 46,8 s | 689 MB | pomiar 14.11.2026 |
| `grundkarte` (`27_grundkarte.py`) | 23,6 s | 490 MB | pomiar 14.11.2026; pierwszy przebieg 24,0 s (`belege/D8_grundkarte.md`) |
| `klima` (`35_klimat.py`) | 9,7 s | 166 MB | pomiar 14.11.2026 |
| `sanierung` (`36_sanierung.py`) | 194,2 s | 938 MB | pomiar 14.11.2026 |
| `denkmale` (`dz_denkmale.py`) | 46,4 s | 573 MB | pomiar 14.11.2026 |
| `oepnv` (`13_oepnv_krakow.py`) | 12,4 s | 180 MB | pomiar 14.11.2026 |
| `planer` (`15_planer_krakow.py`) | 0,5 s | 105 MB | pomiar 14.11.2026 |
| `fussweg` (`14b_fussweg.sh rechnen`) | 14,8 s | nie zmierzono | raport przebiegu z 13.11.2026 (`belege/DE_fussweg.md`) |
| `osm`, `db_gliederung`, `einrichtungen`, `ziele_db`, `fussweg_export` | nie zmierzono | nie zmierzono | |
| `./pruefen.sh --voll` z przeglądarką | suma czasów kroków 1039 s (ok. 17 min) | – | `belege/pruefstand-20261114-5f5bf50/pruefen.log` |
| `./atlas.sh alles --ohne-datenbank` do kroku `pruefen` | suma czasów kroków 1123 s (ok. 19 min) | – | świeży kontener Debian, 16 wątków, 14.11.2026 (`bevoelkerung` 243 s, `sanierung` 298 s, `denkmale` 160 s); sam krok `pruefen` niewliczony (brakowało bibliotek przeglądarki) |
| `./pruefen.sh` z przeglądarką (bez `--voll`) | 939 s (ok. 16 min) | – | komputer wydawcy, 16 wątków, 15.11.2026; wynik: 60 kontroli, 53 zielone, 0 ustaleń, 7 pominiętych |
| `./atlas.sh trocken` | 0,3 s | – | pomiar 14.11.2026 |
| migawka (`schnappschuss.py`, 403 MB) | 3,5 s | – | pomiar 14.11.2026 |

## 7. Błędy i rozwiązania

Komunikaty są dosłowne (narzędzia systemowe z `LC_ALL=C.UTF-8`).

| Komunikat | Przyczyna | Rozwiązanie |
|---|---|---|
| `error: No interpreter found for Python 3.13 in virtual environments, managed installations, or search path` / `hint: A managed Python download is available for Python 3.13, but uv is set to offline mode` | pamięć podręczna uv pusta | krok 2 (raz z siecią) |
| `× No solution found when resolving --with dependencies:` … `Because certifi was not found in the cache` | pakiety z `requirements.txt` nie leżą w pamięci podręcznej | krok 2 |
| `Umgebungsdatei … fehlt (Vorlage .env.beispiel, chmod 600)` | brak `.env` | krok 3 |
| `Container kiezatlas-krakow-db-1 läuft nicht oder ist nicht gesund …` (z `./atlas.sh trocken`) | baza nie działa | `docker compose up -d --wait db`, potem raz `skripte/lauf.sh einrichten` |
| `Pipeline weicht vom festgeschriebenen Stand ab (…). Abbruch; zum Prüfen PIPELINE_ABWEICHUNG=1 setzen.` | repozytorium Geodaten-Import-Pipeline w innym commicie | `git -C ../geodaten-import-pipeline checkout 12bae5bc96cf34355c8c5a723eb444e66f776f2d` |
| `…/1261_SHP.zip: SHA256 … statt 68b6ff47… (Regel G1). Neuer Stand: docs/rundgang.md, …` (`27_grundkarte.py`) | nowsza wersja BDOT10k | drogą C albo „Neuer Datenstand” |
| `…: SHA256 …, erwartet … (andere Schriftdatei)` (`27_grundkarte.py`) | `--schrift-ordner` wskazuje inną wersję Noto Sans | pominąć `--schrift-ordner`: domyślnie `schriften/noto/` w repozytorium (łańcuch używa go sam) |
| `FileNotFoundError: … 10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html` (`35_klimat.py`) | strona BIP poza migawką | pobrać drogą A |
| `sha256sum: zbk/2026-11-13/bip_32.html: No such file or directory` / `FAILED open or read` (`./pruefen.sh`) | listy sum w `belege/` wymieniają też potwierdzenia spoza migawki | oczekiwane po drodze C; lista w `SCHNAPPSCHUSS/AUSGESCHLOSSEN.md` |
| `chrome-headless-shell: error while loading shared libraries: libglib-2.0.so.0: cannot open shared object file` (`./pruefen.sh`) | Chromium zainstalowany bez bibliotek systemowych | `npx playwright install-deps chromium` jako root (albo `--with-deps` w punkcie 2) |
| `HALT: Schritt <krok> mit Rückgabe <n> …` (`./atlas.sh alles`) | krok się nie powiódł | protokół w `berichte/kette/`, po naprawie `./atlas.sh alles --ab <krok>` |

## 8. Kontrole

`./pruefen.sh` uruchamia wszystkie kontrole bez sieci i bez bazy danych (czas w punkcie 6), `./pruefen.sh --voll` dodatkowo liczy pakiety danych od nowa z danych surowych. Bez danych surowych
(`$KIEZ_DATEN` pusty) `./pruefen.sh` zgłasza listy sum kontrolnych jako błąd (po drodze C tylko listy plików pominiętych, zob. punkt 5). Powietrze i rynek mieszkaniowy (`pruefen/D7_powietrze.py`, `pruefen/DW_mieszkania.py`) sprawdzają wtedy tylko pliki
w repozytorium (`--ohne-lauf`); przeliczenie z danych surowych liczy się jako pominięte, nie jako błąd. Dla tego przypadku jest zestaw w
`.github/workflows/pruefen.yml` (kontrole bez danych surowych, bez bazy i bez przeglądarki). Przed publikacją:
`./atlas.sh oeffentlich` (ścieżki osobiste, adresy e-mail, nazwy komputerów, sekrety, duże pliki, licencje) i
`./atlas.sh oeffentlich --historie` (cała historia git).
