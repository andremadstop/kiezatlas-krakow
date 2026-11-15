# Beleg ÖPNV-Haltestellen und Taktklasse

Erzeugt von `skripte/13_oepnv_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). Regeln vor dem Lauf: `pruefen/D6_protokoll.md`, Regeln 1–7. Eingaben und Prüfsummen: `belege/rohdaten-D6-2026-11-13.sha256`.

Stichtag 18.11.2026 (Mittwoch), Fenster 06:00 bis 09:00 Uhr, Gegenprobe-Tag 13.11.2026 (Freitag).

## Schritt 1: Steige und Haltestellen

| Feed | Steige (`stops.txt`, location_type 0) |
|---|---|
| A | 2.983 |
| T | 355 |
| M | 765 |

- Haltestellen (Stämme des `stop_code`): 1.544
- davon in mehr als einem Feed: 372
- Stämme mit mehr als einem Namen: 0 (Befund wäre > 0)
- Steige weiter als 300 m vom Mittelpunkt ihres Stamms: 0

## Schritt 2: Fahrten am Stichtag (Abbruchregel 3)

| Feed | Fahrten gezählt | Gegenprobe Machbarkeit | gleich |
|---|---|---|---|
| A | 10.280 | 10.280 | ja |
| T | 3.710 | 3.710 | ja |
| M | 2.590 | 2.590 | ja |

- Linien mit `route_type` außerhalb von Bus und Tram: 0
- Haltestellen mit mindestens einer Abfahrt am Stichtag: 1.542
- ohne Abfahrt (fallen weg): 2

## Schritt 3: Lage zur Gemeinde Kraków (BDOT10k OT_ADJA_A, TERYT 1261011)

- Fläche der Gemeinde im Rechen-System (ETRS89 / Poland CS2000 zone 7 (EPSG:2178)): 32.685,96 ha; Gegenprobe: BIP Kraków, „Liczba mieszkańców w poszczególnych dzielnicach (wg. stanu na 31 grudnia 2025) oraz powierzchnia dzielnic“, Zeile RAZEM 32683,90 ha (https://www.bip.krakow.pl/?dok_id=242410, Abzug `2026-11-13/10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html`, gelesen 13.11.2026)
- weiter als 1.000 m außerhalb (fallen weg): 598
- veröffentlicht: 944, davon in der Stadt 813, bis 1.000 m außerhalb 131
- Zuordnung zu dzielnice: keine in dieser Datei (st: null; die Zuordnung beruht auf den OSM-Grenzen und steht nur in daten/zellen_odbl.js)

## Schritt 4: Taktklassen (veröffentlichte Haltestellen)

| Taktklasse | in der Stadt | außerhalb | zusammen |
|---|---|---|---|
| I | 498 | 11 | 509 |
| II | 232 | 52 | 284 |
| III | 67 | 47 | 114 |
| unter III | 16 | 21 | 37 |

| Verkehrsmittel | Haltestellen |
|---|---|
| bus | 782 |
| bus+tram | 139 |
| tram | 23 |

## Gegenprobe 13.11.2026

- Fahrten je Feed am Gegenprobe-Tag: A 10.293, T 3.750, M 2.594
- veröffentlichte Haltestellen mit gleicher Taktklasse an beiden Tagen: 944 von 944
- am Gegenprobe-Tag ohne Abfahrt: 0
- Taktklassen am Gegenprobe-Tag: I 509, II 284, III 114, unter III 37

## Grenzen

- Die Klassengrenzen (6, 2, 1 Abfahrten je Stunde und Richtung) sind das Muster des Kiezatlas Potsdam, keine polnische Norm; ein Krakauer Gegenstück (Plan transportowy) wurde nicht gesucht.
- Der Schultag am Stichtag ist aus Wissen angenommen, der Schulkalender ist nicht geprüft.
- Ob der Fahrplan des Stichtags nach dem nächsten wöchentlichen Feed noch gilt, ist nicht geprüft (`feed_version` des Bus-Feeds: 20261109_20261114).
- Haltestellen-Code-Stamm als Haltestelle: nicht gegen eine amtliche Haltestellenliste geprüft.
