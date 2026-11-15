# Quellen des Pakets Gebäude und 3D

Stand 13.11.2026. Zulieferung für `QUELLEN.md` und `daten/LIZENZ.md` (übernimmt die Belegschicht).

## Quellen

| Quelle | Nutzer | Adresse | Rechtsgrundlage | Vermerk (Original, so in den Ausgaben) | Weg | Stand |
|---|---|---|---|---|---|---|
| BDOT10k, Paket Powiat 1261 (Kraków), Schema 2021, SHP; Schichten `OT_BUBD_A` (Gebäude) und `OT_ADJA_A` (Gemeinde, Delegaturen aus PRG) | `skripte/20_bdot10k.py` → `daten/gebaeude_kennzahlen.js`, `daten/gebaeude_dzielnice_odbl.js`, mit `--geometrie` die Gebäude je dzielnica | https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip | kostenfrei nach art. 40a ust. 2 pkt 1 lit. h, keine Lizenz nach art. 40c ust. 5, Quellenangabe nach art. 40c ust. 3 Prawo geodezyjne i kartograficzne (Dz.U. 2026 poz. 1389) | „Źródło: Baza Danych Obiektów Topograficznych (BDOT10k), państwowy zasób geodezyjny i kartograficzny, Główny Urząd Geodezji i Kartografii; dane opracowane (art. 40c ust. 3 ustawy Prawo geodezyjne i kartograficzne, Dz.U. 2026 poz. 1389)“ | A (Abrufskript der Machbarkeitsprobe, schon geladen) | Dateidatum im Archiv 2026-10-03, jüngste `WERSJA` 2026-05-18 (`belege/D5_gebaeude_lauf.md`) |
| Grenzen der Delegaturen (PRG, in BDOT10k `OT_ADJA_A` enthalten) | dieselben Ausgaben, Ebene `delegatury` | wie oben | art. 40a ust. 2 pkt 1 lit. a (PRG) und lit. h | „Granice delegatur: państwowy rejestr granic (PRG) w BDOT10k, Główny Urząd Geodezji i Kartografii“ | A | wie oben |
| Modele 3D budynków LoD1 2024 (`measuredHeight`) | `skripte/20_lod.py`, aufgerufen von `skripte/20_bdot10k.py` | Geoportal, Modul „Pobierz dane“, Gruppe „Dane do pobrania“ → „Topografia → Modele 3D budynków“ | siehe „Offen“ unten: nur die Aussage der Geoportal-Seite, art. 40a ust. 2 pkt 1 nennt die Modelle nicht ausdrücklich | „Wysokości: Modele 3D budynków LoD1 2024 / LoD2, Główny Urząd Geodezji i Kartografii“ (erscheint nur, wenn eine Datei gelesen wurde) | H (Handdownload durch den Betreiber, ausstehend) | LoD1 Stand 2024 |
| Modele 3D budynków LoD2 („opracowane wg stanu na 2017 rok“) | wie LoD1, nur für Gebäude ohne LoD1-Höhe | wie LoD1 | wie LoD1 | wie LoD1 | H (ausstehend) | Stand 2017 |
| Stadtteilgrenzen (18 dzielnice) | Zuordnung je dzielnica | `daten/stadtteile_odbl.js` (Paket Gliederung und Bevölkerung) | ODbL 1.0 (OpenStreetMap), Vermerk aus jener Datei | „ODbL 1.0, © OpenStreetMap-Mitwirkende“ (von dort übernommen) | Paket Gliederung | zur Zeit Beispielrechtecke (`fixture: true`), daher auch die Ausgabe je dzielnica |
| Rozporządzenie BDOT10k (Dz.U. 2021 poz. 1412) | Begriffe: Tabellen der Klassen KŚT 101 … 110, Erfassungsregeln | https://api.sejm.gov.pl/eli/acts/DU/2021/1412/text.pdf | amtlicher Text | – (nur Beleg) | A (`skripte/abruf.py`) | 2026-11-13 |

### Fundstellen (wörtlich)

Gesetzestext: Obwieszczenie Marszałka Sejmu z dnia 18 września 2026 r., tekst jednolity ustawy Prawo geodezyjne i
kartograficzne, Dz.U. 2026 poz. 1389. Datei `kiezatlas-daten/krakow/2026-11-13/03_gebaeude/pgik_DU_2026_1389.pdf`,
abgerufen 2026-11-13T09:21:46Z von https://api.sejm.gov.pl/eli/acts/DU/2026/1389/text.pdf, SHA256
`f7b4ac608d0737a50bf59729d04ea7100f9e64728affcf3fd7582cbfcfaa0c24` (in `belege/rohdaten-D5-2026-11-13.sha256`).

- **art. 40a ust. 1** (S. 33): „Organy prowadzące państwowy zasób geodezyjny i kartograficzny udostępniają materiały
  zasobu odpłatnie.“
- **art. 40a ust. 2 pkt 1** (S. 33): „Nie pobiera się opłaty za: 1) udostępnianie zbiorów danych: a) państwowego
  rejestru granic i powierzchni jednostek podziałów terytorialnych kraju, … h) obiektów topograficznych o
  szczegółowości zapewniającej tworzenie standardowych opracowań kartograficznych w skalach 1:10 000–1:100 000,
  … j) dotyczących budynków w zakresie ich identyfikatorów, geometrii i rodzaju według Klasyfikacji Środków
  Trwałych,“
- **art. 40c ust. 3** (S. 35): „Podmioty, które wykorzystują materiały zasobu, zamieszczają w publikowanych
  opracowaniach informacje o źródle pochodzenia użytego materiału.“
- **art. 40c ust. 5** (S. 35): „Licencji nie wydaje się w przypadku udostępnienia materiałów zasobu w związku ze
  zgłoszeniem prac lub jego uzupełnieniem oraz w przypadku udostępnienia materiałów zasobu, o których mowa w art. 40a
  ust. 2 pkt 1 i 3.“
- **Geoportal, Seite BDOT10k** (Datei `03_gebaeude/geoportal_bdot10k.html`, abgerufen 2026-11-13T09:32:31Z, SHA256
  `58fe5cf154ec9006845bce4d4227513f630022b439643e5113efe114496840e4`): „Baza BDOT10k jest dostępna bezpłatnie i
  możliwa do dowolnego wykorzystania.“ und „Wprowadzone od 31 lipca 2020 r. uwolnienie danych BDOT10k powoduje, że
  dzisiaj każdy może w łatwy sposób wykorzystywać te dane do dowolnych celów.“
- **Geoportal, Seite Modele 3D budynków** (Datei `03_gebaeude/geoportal_modele3d.html`, abgerufen
  2026-11-13T09:20:30Z, SHA256 `1490126acb841e9d4bdce19fc90d44e1c2e1ca5b3071fb7ca88f55b6dc98cd95`): „Modele 3D
  budynków są dostępne bezpłatnie i możliwe do dowolnego wykorzystania.“; zu den Feldern: „każdy model 3D budynku
  posiada poniższe atrybuty: identyfikator obiektu BDOT10k (buildingId), przestrzeń nazw obiektu BDOT10k (przestNazw)
  wersja obiektu BDOT10k (wersjaId)“ und „Modele budynków 3D z 2024 r. posiadają dodatkowo atrybut przybliżonej
  wysokości (measuredHeight).“; zu LoD2: „Budynki LoD2 – opracowane wg stanu na 2017 rok“.
- **BDOT10k-Paket**: `03_gebaeude/1261_SHP.zip`, abgerufen 2026-11-13T09:22:20Z, robots.txt 404 (keine Regeln),
  SHA256 `68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d`.

Die Zitate sind gegen die Dateien nachgelesen (13.11.2026, Text aus dem PDF mit `pdftotext -layout`, aus den
HTML-Seiten nach Entfernen der Auszeichnung).

## Ausgaben und ihre Lizenz

| Ausgabe | Lizenz bzw. Vermerk |
|---|---|
| `daten/gebaeude_kennzahlen.js` (Stadt, 4 Delegaturen) | nur BDOT10k/PRG: Quellenangabe nach art. 40c ust. 3, keine ODbL; Vertrag `daten/schema/gebaeude_kennzahlen.json` |
| `daten/gebaeude_dzielnice_odbl.js` (je dzielnica) | Zuordnung über die OSM-Grenzen, daher ODbL 1.0 für die Datei, dazu der BDOT10k-Vermerk; Vertrag `daten/schema/gebaeude_dzielnice_odbl.json` |
| `--geometrie DIR`: `DIR/<nr>.js` (Grundrisse mit `f`, `gs`, `h`, `hq`) | BDOT10k-Vermerk; Vertrag `daten/schema/gebaeude.json` (Vorschlag Erweiterung um `lod1`/`lod2`, `docs/entscheidungen/D5.md`); die Datei liegt je dzielnica, also mit ODbL-Zuordnung wie oben |

## Erwartete Handdownloads

Alle Dateien legt der Betreiber nach `kiezatlas-daten/krakow/eingang/`. Der Ordner existiert am 13.11.2026 noch nicht.

| Datei (Muster) | Inhalt | Format | Wer liest | Was bei Fehlen passiert |
|---|---|---|---|---|
| `lod1_2024_1261*.zip`, `.gml` oder `.xml` | Modele 3D budynków LoD1 2024, Powiat 1261 | CityGML 2.0, je Gebäude `bldg:Building` mit `bldg:measuredHeight` und `buildingId` (als `gen:stringAttribute name="buildingId"` oder als Element), `wersjaId`; ZIP mit beliebig vielen `.gml`/`.xml` | `skripte/20_lod.py` | Höhe aus Geschossen (`hq = geschosse`), im Lauf-Beleg vermerkt |
| `lod2_1261*.zip`, `.gml` oder `.xml` | Modele 3D budynków LoD2, Stand 2017 | CityGML 2.0, Verknüpfung wie LoD1; Höhe = höchster minus tiefster z-Wert der Gebäudegeometrie | `skripte/20_lod.py` | wie oben |

Mehrere Dateien je Muster sind erlaubt (Kacheln); sie werden nach Namen sortiert gelesen, bei doppelter Kennung gilt
die erste Fundstelle (gezählt). Probe ohne den Gebäudelauf: `python -I skripte/20_lod.py` (Zählung je Datei). Danach
`skripte/20_bdot10k.py` neu laufen lassen und die Prüfsummen der neuen Dateien in eine neue
`belege/rohdaten-D5-<datum>.sha256` schreiben.

Für das Paket nicht nötig: GUS-Gitter, rejony, OSM-Auszug, NID, RSPO (andere Pakete).

## Nicht genutzt

- EGiB-Gebäude (Kataster): nur Kennung, Geometrie und Art KŚT frei (art. 40a ust. 2 pkt 1 lit. j), alles andere
  kostenpflichtig (ust. 1); Baujahr damit nicht frei, die Bauzeiten-Kaskade ist gestrichen (KR4).
- MSIP-Gebäude (`03_gebaeude/budynki_metadane.xml`): Lizenz-STOPP wie die MSIP-Stadtteile (KR3).
- Kein eigener Netzabruf in diesem Paket; das Rozporządzenie BDOT10k kam über `skripte/abruf.py`.

## Offen

- **LoD1/LoD2, Rechtsgrundlage:** Die Freiheit stützt sich nur auf die Geoportal-Seite („dostępne bezpłatnie i
  możliwe do dowolnego wykorzystania“). art. 40a ust. 2 pkt 1 nennt die Modelle nicht ausdrücklich; ob sie unter
  lit. h fallen (Grundriss aus BDOT10k, Höhe aus ALS), ist nicht geprüft. Kein Widerspruch in den Texten, aber vor
  der Veröffentlichung der Höhen zu klären (Vorschlag: Nachfrage bei GUGiK oder Lesart in `docs/entscheidungen/D5.md`).
  Der Leser ist gebaut; ohne Datei entsteht nichts aus dieser Quelle.
- Dass Kraków im LoD2-Gebiet liegt, ist nur aus einer Abbildung gelesen (Machbarkeitsbericht), nicht geprüft.
