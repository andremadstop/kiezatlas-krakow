# Beleg Fußweg je Zelle: Probe mit Beispieldaten

**Beispieldaten (fixture: true).** Netz, Zellen und Ziele sind erfunden (`pruefen/D2_beispielwelt.py`, fester
Zufallsstartwert). Keine Zahl hier beschreibt Kraków. Belegt ist nur, dass Rechnung und Abnahme durchlaufen
und die Kriterien aus `pruefen/D2_protokoll.md` greifen.

- Lauf: 13.11.2026 17:22:09 CET, Commit `5800795bcb17365c7758317f5fb601a783766904`, offene Änderungen in skripte/, pruefen/, sql/, config/: 0
- Aufruf: `pruefen/D2_wegwerf_db.sh` (Wegwerf-PostGIS `postgis/postgis:16-3.6@sha256:d07ce3f06f657b6516c7511412232e97174d7e9dcf4c9fe520109b682b44a201`, 127.0.0.1, Datenbank `kiezatlas_wegwerf` auf tmpfs)
- Werkzeuge: uv 0.11.3 (x86_64-unknown-linux-gnu), Python 3.13.12

## Schritt 1: Beispielwelt (Zeilen je Tabelle nach dem Anlegen)

| Tabelle | Zeilen |
|---|---:|
| `public.stadtteil` | 2 |
| `public.zensus_zelle` | 782 |
| `auswertung.netz_knoten` | 38477 |
| `auswertung.netz_kante` | 76555 |
| `auswertung.einrichtung` | 63 |
| `auswertung.gruenflaeche` | 17 |
| `auswertung.osm_poi` | 52 |
| `auswertung.haltestelle` | 33 |
| `auswertung.zelle_erreichbar` | 10 |

## Schritt 2: Rechnung (Bericht von `skripte/14b_fussweg.py`, Überschriften eine Ebene tiefer)


Lauf 13.11.2026 17:22, Netz aus `auswertung.netz_*`, 0,5 s.

Lizenz: Alle Werte sind aus dem OSM-Wegenetz abgeleitet, ODbL 1.0, © OpenStreetMap-Mitwirkende (https://opendatacommons.org/licenses/odbl/1-0/). Veröffentlichung nur in `*_odbl`-Dateien.

### Netz und Zellen

- Knoten 38.477, davon in der größten Komponente 38.475 (100,0 %); Kanten 76.555
- Zellen aus `public.zensus_zelle` mit Mittelpunkt in einem der 2 Stadtteile (`public.stadtteil`): 505, davon bewohnt (ew > 0) 430 mit zusammen 24.900 Einwohnern; ew leer (als 0 gezählt): 29
- Lizenzvermerk der Zellen (Tabellenkommentar): Beispieldaten (fixture: true), frei erfunden für die Probe in der Wegwerf-Datenbank, keine Quelle
- Anbindung Zellmittelpunkt → Netzknoten: Median 29,5 m, 95 % ≤ 29,5 m; über 300 m (kein Wert): 0 Zellen
- Gehgeschwindigkeit 4,8 km/h (Standard des Skripts, fehlt in config/richtwerte.yaml)

### Je Art

| Art | Ziele | davon außerhalb der Stadtgrenze | Zugangspunkte | Zellen mit Wert | nächstes Ziel außerhalb | Fußweg < Luftlinie | Median Fußweg/Luftlinie | 90 % ≤ m |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| apotheke | 23 | 3 | 23 | 505 von 505 | 12 | 0 | 1,35 | 1.555 |
| gruen | 15 | 3 | 581 | 505 von 505 | 29 | 0 | 1,29 | 1.792 |
| haltestelle | 33 | 4 | 33 | 505 von 505 | 10 | 0 | 1,38 | 1.247 |
| kita | 45 | 8 | 45 | 505 von 505 | 27 | 0 | 1,39 | 998 |
| schule | 18 | 3 | 18 | 505 von 505 | 5 | 0 | 1,36 | 1.843 |
| supermarkt | 29 | 6 | 29 | 505 von 505 | 14 | 0 | 1,35 | 1.526 |

Median Fußweg/Luftlinie über alle Arten (Luftlinie ≥ 100 m): **1,36**

### Grün im Fußweg-Umkreis

- Flächen: gruenanlage, park (Standard des Skripts, fehlt in config/richtwerte.yaml)
- Radius 500 m (Standard des Skripts, fehlt in config/richtwerte.yaml)
- Zugang über Randpunkte im Abstand von 20 m
- Zellen mit Wert 505 von 505; ohne erreichbare Fläche in 500 m: 374; Median 0 m²
- `m2_je_ew` bleibt leer: Fläche je Einwohner teilt jede Fläche auf alle Einwohner ihres Einzugsbereichs auf; das rechnet das Paket Versorgung je Raumeinheit, nicht je Zelle.

### Methode

- Graph aus `netz_kante`, ungerichtet; Gewicht = max(`laenge_m`, gerader Abstand der Endknoten).
- Nur die größte zusammenhängende Komponente. Zelle und Ziel hängen je am nächsten Knoten, beide Anbindungsstrecken zählen mit. Damit ist jeder Fußweg ein Streckenzug von der Zelle zum Ziel und nie kürzer als die Luftlinie.
- Je Art eine Dijkstra-Suche mit allen Zielen als Quellen (scipy). Ziele außerhalb der Stadtgrenze (Vereinigung von `public.stadtteil`) zählen mit, ohne Landes- oder Gemeindefilter; das Netz reicht 2 km über die Stadtgrenze (`skripte/12_osm.py`).
- Meter auf 0,1 m aufgerundet, Minuten = Meter / (km/h · 1000 / 60).

### Grenzen

- Amtliche Ziellisten (Einrichtungen, Grün, Haltestellen) decken womöglich nur das Stadtgebiet ab; dann fehlen Ziele jenseits der Grenze, und Randzellen bekommen zu lange Wege. Das prüft das Paket, das die Liste lädt (nicht hier geprüft).
- Nicht geprüft: Begehbarkeit einzelner Wege (Zugangsbeschränkungen, Treppen, Barrierefreiheit).

## Schritt 3: Abnahme (`skripte/14b_fussweg.sh pruefen`, Rückgabe 0)

```
[ok] K1 je Zelle und Art eine Fußweg-Zeile: 6 Arten × 505 Zellen (davon 430 bewohnt); vollständig; bewohnte Zellen ohne Wert: 0
[ok] K2 Fußweg ≥ Luftlinie (0 Verstöße): 3030 Zellwerte verglichen, 0 Verstöße
[ok] K3 Median Fußweg/Luftlinie zwischen 1,1 und 1,6: gesamt 1.356; je Art: apotheke 1.35 (n=497), gruen 1.29 (n=477), haltestelle 1.38 (n=488), kita 1.39 (n=487), schule 1.36 (n=496), supermarkt 1.35 (n=497)
[ok] K4 methode gesetzt, Fußweg-Zeilen tragen ODbL und den Zellvermerk: zelle_erreichbar 3040 Zeilen, ohne methode 0, Fußweg ohne ODbL 0, ohne Zellvermerk 0; zelle_gruen Fußweg 505 Zeilen, ohne ODbL 0, ohne Zellvermerk 0; Tabellenkommentar nennt ODbL: True
[ok] K5 jedes Ziel einer Fußweg-Zeile steht im Zielbestand: 3030 Zeilen mit Ziel, davon nicht im Zielbestand: 0
[ok] Hinweis: Ziele außerhalb der Stadtgrenze (zählen mit): apotheke 3 von 23 Zielen außerhalb, nächstes Ziel außerhalb für 12 Zellen; gruen 3 von 15 Zielen außerhalb, nächstes Ziel außerhalb für 29 Zellen; haltestelle 4 von 33 Zielen außerhalb, nächstes Ziel außerhalb für 10 Zellen; kita 8 von 45 Zielen außerhalb, nächstes Ziel außerhalb für 27 Zellen; schule 3 von 18 Zielen außerhalb, nächstes Ziel außerhalb für 5 Zellen; supermarkt 6 von 29 Zielen außerhalb, nächstes Ziel außerhalb für 14 Zellen
[ok] Hinweis: Vergleich mit Luftlinie-Zeilen: 10 Paare, davon Fußweg < Luftlinie: 0
```

## Schritt 4: Tests mit Datenbank (`A5B_DB_TEST=1 skripte/14b_fussweg.sh test`, Rückgabe 0)

```
...............................                                          [100%]
31 passed in 1.99s
```
