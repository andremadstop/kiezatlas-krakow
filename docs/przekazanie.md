# Przekazanie / Handover

Co musi zrobić instytucja (np. katedra uczelni), która przejmuje Kiezatlas Kraków, żeby działał bez dotychczasowej
wydawczyni (Stiebitz Souverain Systems UG, dalej: UG). Uruchomienie: [`uruchomienie.md`](uruchomienie.md) /
[`running.md`](running.md). English version below.

Stan: 14.11.2026.

## PL

### Co jest potrzebne do działania

- **Strony** są statyczne: wystarczy dowolny serwer WWW (także serwer uczelni). W czasie działania strony nie
  odwołują się do UG ani do innych obcych usług; podkład mapowy i pliki 3D leżą obok stron.
- **Liczenie** odbywa się na osobnym komputerze z Dockerem (PostGIS) i danymi surowymi w `$KIEZ_DATEN`; po
  przeliczeniu baza nie jest potrzebna.
- **Archiwum**: kod w publicznym repozytorium <https://github.com/andremadstop/kiezatlas-krakow> (publiczne
  repozytoria archiwizuje Software Heritage), wersje jako tagi, rekord Zenodo z DOI dla każdej wersji (`.zenodo.json`;
  DOI 10.5281/zenodo.24254005 dla wszystkich wersji, 10.5281/zenodo.24254006 dla 1.0.0) i osobno migawka danych
  surowych (`skripte/schnappschuss.py`). UG może w każdej chwili wyłączyć swój serwer bez utraty czegokolwiek.
- **Otwarta przeszkoda:** migawka danych surowych nie ma jeszcze rekordu Zenodo ani DOI; przed przekazaniem wydawca
  musi ją opublikować (`uruchomienie.md`, ramka na początku). Repozytoria są publiczne (Apache-2.0, sprawdzone
  15.11.2026): Kiezatlas Kraków <https://github.com/andremadstop/kiezatlas-krakow>, Geodaten-Import-Pipeline
  <https://github.com/andremadstop/geodaten-import-pipeline> (ustalony commit i DOI: `uruchomienie.md`, punkt 1) i
  Kiezatlas Potsdam <https://github.com/andremadstop/kiezatlas-potsdam> (tylko porównanie). Do czasu publikacji
  migawki wszystko, co wymaga tylko otwartych źródeł, można policzyć samodzielnie (drogi A i B); na migawkę trzeba
  poczekać albo zapytać o nią wydawcę.

### Zadania operatora

1. Przejąć repozytorium (fork albo przeniesienie) i własny adres strony.
2. Raz uruchomić łańcuch według `uruchomienie.md` (drogą C, z migawki, plus pięć plików drogą A) i sprawdzić
   `./pruefen.sh`: zielony poza listami sum kontrolnych, które wymieniają pliki z `SCHNAPPSCHUSS/AUSGESCHLOSSEN.md`
   (oczekiwane po drodze C: `./atlas.sh alles` kończy się wtedy komunikatem `HALT: Schritt pruefen …` i kodem 3,
   `uruchomienie.md` punkt 5); bez danych surowych zestaw kontroli z `.github/workflows/pruefen.yml`.
3. Zastąpić odwołania do UG (lista niżej) i opublikować pierwszą własną wersję z wpisem w `CHANGELOG.md`.
4. Aktualizować dane według tabeli niżej; każda nowa wersja źródła według „Neuer Datenstand“ w `rundgang.md`
   (nowy folder z datą, nowa lista sum `belege/rohdaten-<źródło>-<stan>.sha256`, `./pruefen.sh` zielony, wpis w
   `CHANGELOG.md` z liczbami, które się zmieniły).
5. Przy każdej publikowanej wersji: tag, rekord Zenodo (DOI), migawka danych surowych jako osobny rekord, jeśli
   zmieniły się dane surowe.
6. Odpowiadać na zgłoszenia błędów (adres w `config/<miasto>.yaml`, klucz `meldeweg`).
7. Przed każdą publikacją: `./atlas.sh oeffentlich` i `./atlas.sh oeffentlich --historie`.

### Aktualizacja danych według źródeł

„Rytm źródła“ podaje tylko to, co wynika z plików lub z `QUELLEN.md`; reszta to propozycja.

| Źródło | Rytm źródła | Propozycja aktualizacji | Uwagi |
|---|---|---|---|
| OpenStreetMap (wyciąg Małopolska) | zmienia się na bieżąco | raz w roku, razem z BDOT10k | pobranie ręczne (droga B); zmienione granice dzielnic zmieniają wszystkie pliki `_odbl` |
| BDOT10k, powiat 1261 | nie sprawdzono | raz w roku | nowa suma w `skripte/27_grundkarte.py` (`BDOT_SHA256`) |
| Modele 3D LoD2 (stan 2017), LoD1 2024 | LoD1 2024 jeszcze nie pobrany | gdy pojawi się LoD1 dla powiatu | pobranie ręczne |
| Siatka Eurostat 2021 | wydanie spisu 2021 | przy następnym spisie | nie sprawdzono, kiedy |
| NSP 2021 (GUS) | wydanie spisu 2021 | przy następnym spisie | geometria rejonów nadal brakuje |
| GTFS ZTP | plik obowiązuje około tygodnia (`feed_version` 20261109_20261114) | przed każdym przeliczeniem | dzień odniesienia `stichtag` w `config/richtwerte.yaml` musi leżeć w okresie ważności pliku |
| Lista budynków ZBK | wydanie „na dzień 2025-12-01“ | raz w roku | dane osobowe tylko w pliku surowym; publikowane są tylko klasy (uzasadnienie w `docs/entscheidungen.md`) |
| EEA, statystyki roczne jakości powietrza | roczne | raz w roku | pobrane ręcznie 14.11.2026 (instrukcja w `quellen-D7.md`); eksport obejmuje tylko stacje w Krakowie |
| Rejestr cen nieruchomości | nie sprawdzono | raz w roku | pobrane ręcznie 14.11.2026 (instrukcja w `quellen-DW.md`); publikowane tylko lata od 2019 i mediany od 10 transakcji |
| Rejestr zabytków NID, gminna ewidencja, Wikidata | nie sprawdzono | raz w roku | Wikidane: pobrane ręcznie 14.11.2026 (zapytanie w `quellen-DZ.md`), nowa próbka do kontroli na ortofotomapie przy każdym nowym pobraniu; NID i gminna ewidencja: pobranie ręczne jeszcze nie wykonane |
| Czcionki Barlow, Noto Sans | tylko przy nowej wersji | gdy potrzebne | nowe sumy w `skripte/schriften.py` i `skripte/27_grundkarte.py` |

### Punkty kontaktowe (bez danych osobowych)

- Projekt: system zgłoszeń publicznego repozytorium (gdy powstanie) oraz adres z klucza `meldeweg`; do przekazania jest
  to adres funkcyjny UG z `config/krakow.yaml`.
- Źródła: instytucje wymienione w `QUELLEN.md` (GUGiK przez geoportal.gov.pl, GUS, ZTP Kraków, Gmina Miejska Kraków
  przez BIP, EEA, NID) przez ich oficjalne formularze lub adresy funkcyjne na ich stronach. Otwarta sprawa licencji
  granic MSIP jest skierowana do adresu funkcyjnego miasta podanego w `docs/entscheidungen.md` (KR34).
- Decyzje: `docs/entscheidungen.md` (KR1 i dalej), każda z uzasadnieniem i „Neu prüfen, wenn“.

### Zastąpienie odwołań do UG

Wyszukane `grep` w plikach repozytorium (bez stron generowanych i bez `belege/`, które pozostają historycznym zapisem).
Zmiany w `config/krakow.yaml` przenoszą się na strony przez `skripte/31_ort.py` i `skripte/30_seiten.py`
(`./atlas.sh alles --nur ort --nur export --nur bloecke --nur seiten`; `export` odświeża zdanie cytowania i adres
zgłoszeń w `daten/pobierz/`).

| Miejsce | Co | Jak zastąpić |
|---|---|---|
| `config/krakow.yaml` | `basis_url`, `zitierzeile` (pl/en/de), `herausgeber`, `meldeweg` | własny adres, nazwa instytucji, adres funkcyjny |
| `vorlagen/_rahmen.html` | odnośniki do noty prawnej i ochrony danych UG w stopce każdej strony (54 + 54 wystąpienia: 18 plików HTML łącznie z 404.html × 3 języki) | odnośniki do stron instytucji |
| `skripte/16_export_krakow.py` | nazwa UG w zdaniu cytowania plików do pobrania (pl/en/de) | z `herausgeber` w konfiguracji albo nowa nazwa |
| `skripte/abruf.py` (`KENNUNG`), `skripte/lauf.sh` (`PIPELINE_KENNUNG`) | identyfikator programu z adresem UG przy pobieraniu | własny identyfikator z adresem kontaktowym |
| `texte/<język>/bloecke/quelle/metoda.html` | kto rozstrzygał (autor) | uzupełnić o nowy zespół, autora nie usuwać |
| `CITATION.cff`, `.zenodo.json` | autor, kontakt, adres | dopisać nowy zespół; dotychczasowych autorów zostawić |
| `NOTICE` | prawa autorskie UG | zostaje (wymóg Apache-2.0); dopisać własną linię dla zmian |
| `README.md` | wydawczyni, adres zgłoszeń | nowa instytucja |
| `skripte/deploy_kopie.py`, `docs/auslieferung.md` | serwer i ścieżka UG | własny serwer |
| `pruefen/gegenprobe_potsdam/ort.yaml` | konfiguracja Poczdamu (UG) | zostaje, to zapis kontroli krzyżowej |

## EN

### What it takes to run

- **Pages** are static; any web server will do (a university server included). At run time they call neither the UG
  nor any other third-party service; the base map and 3D files sit next to the pages.
- **Computing** happens on a separate machine with Docker (PostGIS) and raw data in `$KIEZ_DATEN`; afterwards the
  database is not needed.
- **Archive**: code in a public repository <https://github.com/andremadstop/kiezatlas-krakow> (Software Heritage
  archives public repositories), versions as tags, a Zenodo record with a DOI per version (`.zenodo.json`;
  DOI 10.5281/zenodo.24254005 for all versions, 10.5281/zenodo.24254006 for 1.0.0)
  and a separate raw-data snapshot (`skripte/schnappschuss.py`). The UG can switch off its server at any time without
  anything being lost.
- **Open obstacle:** the raw-data snapshot has no Zenodo record or DOI yet; the publisher has to publish it before the
  handover (`running.md`, box at the top). The repositories are public (Apache-2.0, checked 15 November 2026):
  Kiezatlas Kraków <https://github.com/andremadstop/kiezatlas-krakow>, the Geodaten-Import-Pipeline
  <https://github.com/andremadstop/geodaten-import-pipeline> (pinned commit and DOI: `running.md`, section 1) and
  Kiezatlas Potsdam <https://github.com/andremadstop/kiezatlas-potsdam> (comparison only). Until the snapshot is
  published, everything that needs only open sources can be computed independently (ways A and B); for the snapshot,
  wait or ask the publisher.

### Operator tasks

1. Take over the repository (fork or transfer) and your own web address.
2. Run the chain once following `running.md` (way C, from the snapshot, plus five files by way A) and check
   `./pruefen.sh`: green except the checksum lists that name files from `SCHNAPPSCHUSS/AUSGESCHLOSSEN.md` (expected
   after way C: `./atlas.sh alles` then ends with `HALT: Schritt pruefen …` and exit code 3, `running.md` section 5);
   without raw data use the checks in `.github/workflows/pruefen.yml`.
3. Replace the UG references (table above, section “Zastąpienie odwołań do UG”) and publish a first own version with
   a `CHANGELOG.md` entry.
4. Update the data as in the table above; every new source state follows “Neuer Datenstand” in `rundgang.md`.
5. For every published version: tag, Zenodo record (DOI), and a new raw-data snapshot record if raw data changed.
6. Answer error reports (address in `config/<city>.yaml`, key `meldeweg`).
7. Before publishing: `./atlas.sh oeffentlich` and `./atlas.sh oeffentlich --historie`.

### Contact points (no personal data)

The project’s issue tracker once public, and the `meldeweg` address (until the handover: the UG’s role address); the
institutions in `QUELLEN.md` through their official forms or role addresses; the decisions in
`docs/entscheidungen.md`. The update table and the list of UG references are in the Polish section above (same
content; file and key names are identical).
