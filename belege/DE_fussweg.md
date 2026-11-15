# Fußweg je Zelle

Lauf 13.11.2026 22:21, Netz aus `auswertung.netz_*`, 14,8 s.

Lizenz: Alle Werte sind aus dem OSM-Wegenetz abgeleitet, ODbL 1.0, © OpenStreetMap-Mitwirkende (https://opendatacommons.org/licenses/odbl/1-0/). Veröffentlichung nur in `*_odbl`-Dateien.

## Netz und Zellen

- Knoten 626.425, davon in der größten Komponente 614.104 (98,0 %); Kanten 691.029
- Zellen aus `public.zensus_zelle` mit Mittelpunkt in einem der 18 Stadtteile (`public.stadtteil`): 327, davon bewohnt (ew > 0) 314 mit zusammen 793.392 Einwohnern; ew leer (als 0 gezählt): 0
- Lizenzvermerk der Zellen (Tabellenkommentar): Eurostat, Census 2021 population grid, 1 km (CC BY 4.0, https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution). Auswahl der Zellen: Mittelpunkt in der Stadtgrenze (BDOT10k/PRG, gmina 1261011); dieselben IDs wie über die Grenzen der dzielnice (geprüft in skripte/02_bevoelkerung.py). Zuordnung zur dzielnica (© OpenStreetMap-Mitwirkende, ODbL 1.0) nur in *_odbl-Dateien.
- Anbindung Zellmittelpunkt → Netzknoten: Median 29,0 m, 95 % ≤ 170,7 m; über 300 m (kein Wert): 7 Zellen
- Gehgeschwindigkeit 4,8 km/h (Standard des Skripts, fehlt in config/richtwerte.yaml)

## Je Art

| Art | Ziele | davon außerhalb der Stadtgrenze | Zugangspunkte | Zellen mit Wert | nächstes Ziel außerhalb | Fußweg < Luftlinie | Median Fußweg/Luftlinie | 90 % ≤ m |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| apotheke | 321 | 40 | 321 | 320 von 327 | 63 | 0 | 1,43 | 6.117 |
| arzt | 283 | 25 | 283 | 320 von 327 | 67 | 0 | 1,41 | 6.321 |
| gruen | 90 | 0 | 8.549 | 320 von 327 | 0 | 0 | 1,36 | 4.196 |
| haltestelle | 793 | 63 | 793 | 320 von 327 | 7 | 0 | 1,55 | 1.469 |
| pflege | 20 | 5 | 20 | 320 von 327 | 55 | 0 | 1,35 | 6.224 |
| przedszkole | 35 | 0 | 35 | 320 von 327 | 0 | 0 | 1,34 | 8.705 |
| spielplatz | 1.107 | 107 | 1.107 | 320 von 327 | 14 | 0 | 1,62 | 2.065 |
| supermarkt | 1.270 | 155 | 1.270 | 320 von 327 | 18 | 0 | 1,53 | 2.050 |
| szkola | 170 | 0 | 170 | 320 von 327 | 0 | 0 | 1,51 | 3.557 |
| szpital | 24 | 0 | 24 | 320 von 327 | 0 | 0 | 1,34 | 9.792 |
| zlobek | 2 | 0 | 2 | 320 von 327 | 0 | 0 | 1,26 | 16.656 |

Median Fußweg/Luftlinie über alle Arten (Luftlinie ≥ 100 m): **1,40**

## Grün im Fußweg-Umkreis

- Flächen: gruenanlage, park (Standard des Skripts, fehlt in config/richtwerte.yaml)
- Radius 500 m (Standard des Skripts, fehlt in config/richtwerte.yaml)
- Zugang über Randpunkte im Abstand von 20 m
- Zellen mit Wert 320 von 327; ohne erreichbare Fläche in 500 m: 268; Median 0 m²
- `m2_je_ew` bleibt leer: Fläche je Einwohner teilt jede Fläche auf alle Einwohner ihres Einzugsbereichs auf; das rechnet das Paket Versorgung je Raumeinheit, nicht je Zelle.

## Methode

- Graph aus `netz_kante`, ungerichtet; Gewicht = max(`laenge_m`, gerader Abstand der Endknoten).
- Nur die größte zusammenhängende Komponente. Zelle und Ziel hängen je am nächsten Knoten, beide Anbindungsstrecken zählen mit. Damit ist jeder Fußweg ein Streckenzug von der Zelle zum Ziel und nie kürzer als die Luftlinie.
- Je Art eine Dijkstra-Suche mit allen Zielen als Quellen (scipy). Ziele außerhalb der Stadtgrenze (Vereinigung von `public.stadtteil`) zählen mit, ohne Landes- oder Gemeindefilter; das Netz reicht 2 km über die Stadtgrenze (`skripte/12_osm.py`).
- Meter auf 0,1 m aufgerundet, Minuten = Meter / (km/h · 1000 / 60).

## Grenzen

- Amtliche Ziellisten (Einrichtungen, Grün, Haltestellen) decken womöglich nur das Stadtgebiet ab; dann fehlen Ziele jenseits der Grenze, und Randzellen bekommen zu lange Wege. Das prüft das Paket, das die Liste lädt (nicht hier geprüft).
- Nicht geprüft: Begehbarkeit einzelner Wege (Zugangsbeschränkungen, Treppen, Barrierefreiheit).
