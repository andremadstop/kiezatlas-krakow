# Kiezatlas Kraków

**PL** Atlas 18 dzielnic Krakowa z otwartych danych publicznych: liczby, mapy i źródło przy każdej wartości.
Interfejs po polsku, z wersją angielską i niemiecką.

**DE** Ein Atlas der 18 Krakauer Stadtteile (dzielnice) aus offenen amtlichen Daten, mit Quelle bei jeder Zahl.
Oberfläche polnisch, dazu englische und deutsche Fassung. Belegstandard wie beim Kiezatlas Potsdam: jede Zahl mit
Beleg und Skript, Prüfkette ohne Netz, Entscheidungen mit Begründung.

Prototyp der Stiebitz Souverain Systems UG (haftungsbeschränkt), Potsdam. **Stand: 15.11.2026, Daten echt
gerechnet, alle 18 Seiten mit Daten.** Seit den Handdownloads vom 14.11.2026 sind alle Datendateien echt, auch Luft
(EEA), Wohnungsmarkt (RCN) und Denkmalregister (Wikidata; auf `kamienice` je Delegatura, auf der Karte als eigene
Ebene neben der OSM-Kennzeichnung). Downloads (GeoPackage, CSV, QGIS-Projekt) unter `daten/pobierz/`, das
Denkmalregister als Ebene `rejestr_zabytkow`; Luft und Wohnungsmarkt haben dort noch keine eigene Ebene.

## Do weryfikacji / Zur Prüfung, Stand 15.11.2026

Jede Kernzahl mit dem Beleg, der sie trägt, und dem Skript, das sie erzeugt. Der Weg aller Skripte steht in
[`docs/rundgang.md`](docs/rundgang.md), alle Belege in [`belege/README.md`](belege/README.md), die Entscheidungen
(KR1 ff., mit „Nie sprawdzono / Nicht geprüft sind …“) in [`docs/entscheidungen.md`](docs/entscheidungen.md), die Quellen in
[`QUELLEN.md`](QUELLEN.md), der Stand gegen den Belegstandard Punkt für Punkt in [`docs/checkliste.md`](docs/checkliste.md).
Jüngster grüner Prüfstand: 15.11.2026, Commit `7ef6874`, Protokoll
[`belege/pruefstand-20261115-7ef6874/pruefen.log`](belege/pruefstand-20261115-7ef6874/pruefen.log) (nach dem
Gegenlesen der polnischen Texte durch drei Sprachmodelle, Gemini, Claude Sonnet und Codex: 178 Stellen, 119
übernommen, 58 verworfen, ein Sachfehler berichtigt, [`docs/entscheidungen/p4b-polnisch.md`](docs/entscheidungen/p4b-polnisch.md);
ein muttersprachliches Lektorat ist das nicht; davor `aff3130`, nach der
Nacharbeit zur Sichtprüfung: Langtexte fallen ohne Eingabe der Sichtprüfung auf „ungeprüft“ zurück, die Methode nennt
das Ergebnis der Typologie-Stichprobe, Repository-Link aus `config/krakow.yaml`; davor `d5f70c0`, zweite Sichtprüfung
der Denkmalpunkte am Luftbild mit Lage auf dem Objekt 33 von 40 Punkten, und `e04b0d9`, Behebung der Sichtung, Verbleib
der Funde in [`docs/entscheidungen/review-p4a.md`](docs/entscheidungen/review-p4a.md); ohne Beispieldaten, mit Browser,
Neurechnung aus den Rohdaten und Gegenprobe Potsdam im selben Lauf, `./pruefen.sh --voll --gegenprobe`;
65 Prüfungen, 60 grün, 0 mit Befund, 5 übersprungen mit Grund; der Commit danach legt nur das
Protokoll ab und ändert Dokumentation). Gegenprobe Potsdam: 0 Abweichungen (im selben Protokoll). Alle Seiten auf
Polnisch als Bildschirmfoto: [`belege/bildschirm-20261115/README.md`](belege/bildschirm-20261115/README.md).

| Angabe | Beleg | Skript |
|---|---|---|
| Kraków hat 800.653 Einwohner (NSP 2021, Gemeinde 1261) | `belege/D4_bevoelkerung.md`, Schritt 3 (Σ rejony = Σ obwody = Stadt) | `skripte/02_bevoelkerung.py` |
| Fläche der Stadt 326,86 km² (PRG in BDOT10k) | `belege/D4_bevoelkerung.md`, Schritt 1 | `skripte/02_bevoelkerung.py` |
| 90.563 Gebäude in BDOT10k 1261, jedes genau einer delegatura zugeordnet | `belege/D5_gebaeude_lauf.md`, Schritte | `skripte/20_bdot10k.py` |
| 508 Einträge in der Gebäudeliste des ZBK zum 01.12.2025 | `belege/DS_sanierung_lauf.md`, Schritt 1 | `skripte/36_sanierung.py` |
| 10 Luftmessstationen der EEA-Statistik in Kraków, 337 Jahreswerte 2010–2025 (Umland nicht im Export) | `belege/D7_luft_lauf.md` | `skripte/32_powietrze.py` |
| 45.701 Wohnungskäufe aus dem RCN einer dzielnica zugeordnet, davon 45.687 ab 2019 veröffentlicht (KR55); 371 Mediane je dzielnica, Jahr und Markt ab 10 Käufen; keine unterdrückte Fallzahl mit nur zwei möglichen Werten | `belege/DW_mieszkania.md`, Zählung je Schritt; `belege/DW_spannenprobe.md` | `skripte/40_mieszkania.py` |

**Dotąd niepotwierdzone / Nicht belegt sind bisher:**

**PL** Jakość powietrza: eksport EEA obejmuje tylko stacje w Krakowie, brak stacji w okolicy. Ceny mieszkań: wartości dla
całego miasta w dużej mierze kompletne dopiero od 2021 r. (2019 r. około 2 %, 2020 r. około 26 % transakcji), dla dzielnic
dopiero od 2021 r. (w pliku RCN brakuje udziału, potem położenia). Rejestr zabytków: tylko Wikidane (część rejestru), bez rejestru NID i gminnej ewidencji. Położenie punktów rejestru i
obiektów OSM ze znacznikiem `heritage` sprawdzono na ortofotomapie tylko na losowej próbie 40 punktów (33 na obiekcie,
6 tuż obok, 1 poza obiektem; `belege/DZ_denkmale_lauf.md`), nie dla każdego punktu; przypisania do budynku nie
sprawdzano. Wartości NSP 2021 dla dzielnic i typologia bloków (szacunek) nie są potwierdzone.
Przypisanie dzielnic do czterech delegatur (dawnych dzielnic) sprawdzono tylko względem delegatur BDOT10k.

**DE** Luft: Der EEA-Export enthält nur die Stationen in Kraków, das Umland fehlt. Wohnungsmarkt: Werte der ganzen Stadt
erst ab 2021 weitgehend vollständig (2019 rund 2 %, 2020 rund 26 % der Käufe), Werte je dzielnica erst ab 2021 (in der
RCN-Datei fehlen erst der Anteil, dann die Lage).
Denkmalregister: nur Wikidata (Teilmenge des Registers), NID-Register und gminna ewidencja fehlen. Die Lage der
Registerpunkte und der OSM-Objekte mit `heritage` ist am Luftbild nur in einer Zufallsstichprobe von 40 Punkten geprüft
(33 auf dem Objekt, 6 knapp daneben, 1 nicht dort; `belege/DZ_denkmale_lauf.md`), nicht je Punkt; die Zuordnung zum
Gebäude ist ungeprüft. Nicht belegt ist außerdem die
Typologie der Plattenbauten (Schätzung). Die Zuordnung der dzielnice zu den historischen Stadtbezirken ist nur gegen die
delegatury der BDOT10k geprüft ([`docs/entscheidungen.md`](docs/entscheidungen.md), KR17).

Błąd w danych lub tekście? / Fehler gefunden? **kontakt@souverain-systems.de**

## Aufbau

- Statische Seiten ohne Build: Polnisch im Wurzelordner, Englisch in `en/`, Deutsch in `de/`, gleiche Dateinamen.
  Erzeugt von `skripte/30_seiten.py` aus `vorlagen/` und `texte/<lang>/`; nicht von Hand ändern.
- Daten nur als `daten/*.js` per `<script>` (läuft auch per file://), sprachneutral; je Datei ein Vertrag in
  `daten/schema/`.
- Ortskonfiguration `config/krakow.yaml` → `daten/ort.js` (`skripte/31_ort.py`): Namen je Sprache, Gliederung,
  Kartenquellen, Themen, Rechen-Koordinatensystem (EPSG:2178).
- Textschicht `i18n.js`: `t()`, Plural nach `Intl.PluralRules`, Zahlen und Daten nach Landesbrauch.

## Prüfen

```sh
./pruefen.sh                 # alle Prüfungen ohne Netz und Datenbank, mit Browser (Dauer: docs/running.md, Abschnitt 6)
./pruefen.sh --ohne-browser  # ohne Playwright
./pruefen.sh --voll          # zusätzlich: Datenpakete aus den Rohdaten neu rechnen (braucht $KIEZ_DATEN; mit Browser 1.039 s laut docs/running.md)
./pruefen.sh --gegenprobe    # zusätzlich: der umgebaute Code zeigt die Potsdamer Seiten wie Potsdam
```

Seiten und Ortskonfiguration neu erzeugen:

```sh
uv run --offline --python 3.13 --no-project --with-requirements requirements.txt python -I skripte/31_ort.py
uv run --offline --python 3.13 --no-project --with-requirements requirements.txt python -I skripte/30_seiten.py
```

## Uruchom u siebie / Run it yourself / Selbst betreiben

Ein Befehl für die ganze Kette: `./atlas.sh trocken` (prüft Werkzeuge, Datenbank und Eingänge, schreibt nichts),
`./atlas.sh alles` (rechnen, Downloads, Seiten, `./pruefen.sh`). Anleitung vom leeren Rechner bis zur Seite mit
gemessenem Platz- und Zeitbedarf und drei Quellwegen (Abruf, Handdownload, Rohdaten-Schnappschuss):
[`docs/uruchomienie.md`](docs/uruchomienie.md) (PL), [`docs/running.md`](docs/running.md) (EN). Andere Stadt:
[`docs/nowe-miasto.md`](docs/nowe-miasto.md), [`docs/new-city.md`](docs/new-city.md). Übernahme durch eine
Hochschule: [`docs/przekazanie.md`](docs/przekazanie.md) (PL/EN).

## Lizenz

| Teil | Lizenz | Wo steht es |
|---|---|---|
| Code (`*.js`, `*.css`, `skripte/`, `pruefen/`, `sql/`, `vorlagen/`, Konfiguration) und eigene Texte (`texte/`, `docs/`, `belege/`) | Apache-2.0 | [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) |
| Grafiken aus der Schaugrafik | CC BY 4.0 mit Bildzeile | Bildzeile auf der Grafik |
| Daten unter `daten/` | Lizenz der jeweiligen Quelle; OpenStreetMap-Anteile (ODbL 1.0) nur in `*_odbl`-Dateien | [`daten/LIZENZ.md`](daten/LIZENZ.md), [`QUELLEN.md`](QUELLEN.md) |
| Downloads unter `daten/pobierz/` | je Ebene | [`daten/pobierz/licencje.csv`](daten/pobierz/licencje.csv) |
| Rohdaten (nicht im Repo) | je Quelle; weitergegeben wird nur, was die Lizenz erlaubt | `skripte/schnappschuss.py` (`LIZENZEN.md`, `AUSGESCHLOSSEN.md` im Archiv) |
| MapLibre GL JS (`vendor/`) | BSD-3-Clause | [`vendor/MAPLIBRE-LICENSE.txt`](vendor/MAPLIBRE-LICENSE.txt) |
| GSAP (`vendor/`) | GreenSock Standard License, keine Open-Source-Lizenz; nur für die Gegenprobe Potsdam | [`NOTICE`](NOTICE) |
| Schriften Barlow (`fonts/`), Kartenschrift Noto Sans (Auslieferung) | SIL Open Font License 1.1 | [`fonts/OFL.txt`](fonts/OFL.txt), [`NOTICE`](NOTICE) |

Zitieren: [`CITATION.cff`](CITATION.cff) (gültig nach CFF 1.2.0), Zenodo: DOI
[10.5281/zenodo.24254005](https://doi.org/10.5281/zenodo.24254005) (alle Versionen; Version 1.0.0:
[10.5281/zenodo.24254006](https://doi.org/10.5281/zenodo.24254006), Version 1.1.0:
[10.5281/zenodo.24306257](https://doi.org/10.5281/zenodo.24306257)), Metadaten in [`.zenodo.json`](.zenodo.json);
der Rohdaten-Schnappschuss folgt. Öffentliche Repositorys archiviert Software Heritage; die Kennung (SWHID) kann
nach der Archivierung in `CITATION.cff` (`identifiers`) eingetragen werden. Änderungen: [`CHANGELOG.md`](CHANGELOG.md). Vor einer
Veröffentlichung: `./atlas.sh oeffentlich` (Arbeitsbaum) und `./atlas.sh oeffentlich --historie` (Git-Historie).
