# Lizenzen der Daten

Jede Datei unter `daten/` behält die Lizenz ihrer Quelle; Code und eigene Texte stehen unter Apache-2.0 (`LICENSE`),
Grafiken aus der Schaugrafik unter CC BY 4.0 mit der Bildzeile auf der Grafik. Daten mit Anteil aus OpenStreetMap
(ODbL 1.0) stehen nur in Dateien mit `_odbl` im Namen; `pruefen/daten.py` prüft das. Seit der Entscheidung vom
13.11.2026 abends (Folgefrage zu KR3, Variante a) gilt das auch für alles, was nur über die OSM-Grenzen einer
dzielnica zugeordnet ist: Zellen mit Stadtteil, Kennzahlen je dzielnica, Planer, Gebäude je dzielnica.

Stand 14.11.2026 (neu: `porownanie.js`, Downloads unter `pobierz/`, `stadtteile_uebersicht_odbl.js`; `mieszkania.js` heißt
`mieszkania_odbl.js`, KR43). Seit dem Echtlauf vom 14.11.2026 abends ist keine Datei mehr **Beispieldaten**
(`fixture: true`): `powietrze.js` (EEA), `mieszkania_odbl.js` (RCN) und `denkmale.js` (Wikidata) sind aus den
Handdownloads gerechnet. Quellen, Vermerke im Original und Wege: `QUELLEN.md`.

| Datei | Inhalt | Lizenz |
|---|---|---|
| `ort.js` | Ortskonfiguration aus `config/krakow.yaml` (Namen, Kartenausschnitt, Bildzeilen als Text) | Apache-2.0 (eigene Angaben) |
| `stadtteile_odbl.js` | Grenzen der 18 dzielnice aus OpenStreetMap | ODbL 1.0, © OpenStreetMap-Mitwirkende |
| `stadtteile_uebersicht_odbl.js` | vereinfachte Grenzen der 18 dzielnice für die Übersicht der Startseite (KR39; Vereinfachung in `belege/N1_stadtteile_uebersicht.md`) | ODbL 1.0, © OpenStreetMap-Mitwirkende (abgeleitet aus `stadtteile_odbl.js`) |
| `zellen_odbl.js` | Zellen des Eurostat-Gitters (1 km) mit Einwohnern, Altersanteilen und Zuordnung `st` | ODbL 1.0 (Zuordnung über die OSM-Grenzen); Einwohner Eurostat, CC BY 4.0 |
| `kennzahlen_odbl.js`, `kennzahlen_odbl.json` | Kennzahlen je dzielnica und Stadt | ODbL 1.0; Einwohner Eurostat, CC BY 4.0; Vermerk im Kopf bzw. Feld `lizenz` |
| `steckbrief.js` | Stadt und vier delegatury: NSP 2021, Gitter, Fläche, Dichte; dzielnice `null` mit Grund | Quellenangaben GUS, Eurostat (CC BY 4.0), GUGiK (BDOT10k/PRG); keine OSM-Werte |
| `steckbrief_dzielnice_odbl.js` | je dzielnica: Fläche, Gitter, Dichte, OSM-Kennung; NSP 2021 als Summe der rejony | ODbL 1.0; Einwohner Eurostat, CC BY 4.0; NSP und Grenzen der rejony GUS, Quellenangabe |
| `rejony.js` | je rejon statystyczny: Grenze, Einwohner, Fläche, Dichte, drei Altersanteile (ganze Prozent, ab 100 Personen) | Grenzen GUS BREC 2021 („Brak warunków dostępu i użytkowania“), Werte GUS NSP 2021, Quellenangabe; keine OSM-Werte |
| `gebaeude_kennzahlen.js` | Gebäude der Stadt und der delegatury mit Höhenherkunft | BDOT10k, Quellenangabe nach art. 40c ust. 3 Prawo geodezyjne i kartograficzne; Höhen GUGiK LoD2 (Stand 2017) mit wörtlicher Freigabe im Feld `quellen.hoehen.vermerk` |
| `gebaeude_dzielnice_odbl.js` | Gebäude je dzielnica | ODbL 1.0 (Zuordnung); BDOT10k und LoD2 wie oben |
| `gebaeude/<nr>_odbl.js` (außerhalb des Repos, `kiezatlas-daten/krakow/abgeleitet/gebaeude/2026-11-13-odbl/`, Stand und Manifest in `config/gebaeude_3d.json`) | Grundrisse für 3D je dzielnica mit Höhe und Herkunft `hq` | ODbL 1.0 (Aufteilung); BDOT10k und LoD2 wie oben |
| `haltestellen.js` | Haltestellen mit Taktklasse, ohne `st` | CC BY 4.0 (ZTP); Gemeindegrenze BDOT10k |
| `einrichtungen.js` | Einrichtungen aus BDOT10k, ohne `st` | BDOT10k, Quellenangabe |
| `einrichtungen_odbl.js` | Ärzte und Apotheken aus OpenStreetMap | ODbL 1.0 |
| `erreichbar.js` | Erreichbarkeit je Zelle, Luftlinie, ohne Zuordnung zur dzielnica | BDOT10k, ZTP (CC BY 4.0), Eurostat (CC BY 4.0); keine ODbL, weil die 327 Zellen genau die Zellen mit Mittelpunkt in der BDOT10k-Stadtgrenze sind (`belege/D4_bevoelkerung.md`) |
| `erreichbar_fuss_odbl.js` | Fußweg je Zelle und Art | ODbL 1.0 (OSM-Wegenetz und OSM-Ziele); BDOT10k, ZTP |
| `planer_odbl.js` | Versorgung je dzielnica, Luftlinie | ODbL 1.0 (Zuordnung `st`); BDOT10k, ZTP (CC BY 4.0) |
| `planer_fuss_odbl.js` | Versorgung je dzielnica, Fußweg | ODbL 1.0 (OSM-Wegenetz und Zuordnung); BDOT10k, ZTP |
| `grundkarte.js` | Stil und Pfade der eigenen Grundkarte (Kacheln außerhalb des Repos) | BDOT10k, Quellenangabe; Kartenschrift Noto Sans, OFL 1.1 |
| `klimat.js`, `klimat_zellen.js` | Bodenbedeckung der Stadt und je Zelle | BDOT10k, Quellenangabe; keine ODbL (Zellen wie bei `erreichbar.js`) |
| `klimat_stadtteile_odbl.js` | Bodenbedeckung je dzielnica | ODbL 1.0 (Zuordnung); BDOT10k |
| `denkmale_bdot.js` | Zählungen der Gebäude, Komplexe und Gebäudenamen „Kamienica“ aus BDOT10k | BDOT10k, Quellenangabe |
| `denkmale_odbl.js` | OSM-Objekte (auch Relationen) mit `heritage` oder `start_date`, Lage der Objekte mit `heritage` in einer Zufallsstichprobe am Luftbild geprüft (`sichtpruefung`, Quote für die Ebene, nicht je Punkt) | ODbL 1.0 |
| `denkmale.js` | Register-Teil der Denkmale, bisher nur aus Wikidata (NID-Register und gminna ewidencja fehlen im Eingang); Lage in einer Zufallsstichprobe am Luftbild geprüft (`sichtpruefung`); geladen von `kamienice` und `karta` | Wikidata: CC0 1.0 für strukturierte Daten (KR24; wörtlich in `eingang/wikidata_licensing_20261114.txt`) |
| `powietrze.js` | Jahreskennwerte der EEA-Statistik für die Stationen mit `City = Kraków` (Umland fehlt im Export), Grenzwerte (Dz.U. 2021 poz. 845), Zitat der Uchwała | EEA: CC BY 4.0, Nennung „EEA; Daten: GIOŚ“ (KR20); Rechtsakte urheberrechtsfrei |
| `mieszkania_odbl.js` | Mediane des RCN je dzielnica, Jahr und Markt ab 10 Käufen, Fallzahl unter 10 nur als „n < 10“ ohne Wert, sekundär verdeckte Fallzahlen (KR43; `pruefen/N1_protokoll.md`, Regel 4) | RCN: keine Lizenz, Quellenangabe nach art. 40c ust. 3 Prawo geodezyjne i kartograficzne; ODbL 1.0, weil die Zuordnung zur dzielnica über die OSM-Grenzen läuft (Variante a; Dateiname seit KR43) |
| `sanierung.js` | ZBK-Liste je Art, Eigentumsklasse und dzielnica laut Liste; Typologie-Schätzung aus BDOT10k je delegatura | Weiterverwendung nach den Regeln der Gmina Miejska Kraków (Vermerk und Haftungsklausel im Feld `quellen.zbk`); BDOT10k, Quellenangabe |
| `sanierung_odbl.js` | Verortung über OSM-Adressen, Verknüpfung mit BDOT10k und LoD2, Punkte nur für öffentliches Eigentum, Typologie je dzielnica | ODbL 1.0; dazu die Vermerke von ZBK, BDOT10k und LoD2 im Feld `quellen` |
| `porownanie.js` | Stadtwerte Kraków und Potsdam aus dem Eurostat-Gitter 2021 (Einwohner, Altersanteile, Fläche, Dichte), Quellen, Kontrollzahlen (KR37) | Eurostat, CC BY 4.0, Nennung „Eurostat, Census 2021 population grid“; Fläche Krakaus aus der PRG (BDOT10k), Quellenangabe nach art. 40c ust. 3; Stadtgrenze Potsdam dl-de/zero-2-0 |
| `pobierz/` | Downloads aus den Datendateien: `kiezatlas_krakow.gpkg`, `csv/`, `csv_pl/` ohne OSM-Anteil; `kiezatlas_krakow_odbl.gpkg`, `csv_odbl/`, `csv_odbl_pl/` mit OSM-Anteil; QGIS-Projekt, Liesmich, `pola.csv`, `wartosci.csv`; keine Beispieldaten (KR44) | je Ebene nach `pobierz/licencje.csv`; `_odbl`-Teile ODbL 1.0, © OpenStreetMap-Mitwirkende; Ebene `siatka_1km` ohne `st` wie `erreichbar.js` |
