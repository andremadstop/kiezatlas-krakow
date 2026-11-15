# Beleg Fußweg-Export (erzeugt)

Erzeugt von `skripte/14c_fussweg_export_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau gegen die Datenbank). Grundlage: `auswertung.zelle_erreichbar` und `zelle_gruen` (methode fussweg) aus `skripte/14b_fussweg.py`, Bericht `belege/DE_fussweg.md`.

- Zellen: 327, bewohnt 314, Einwohner 793.392
- dzielnice unter 100 Einwohnern (kein Wert): 0

| Art (je Zelle) | Zellen mit Wert | bewohnte Zellen ohne Wert | Median m (bewohnte Zellen) |
|---|---|---|---|
| `apotheke` | 313 | 1 | 1.380 |
| `arzt` | 313 | 1 | 1.740 |
| `haltestelle_takt` | 313 | 1 | 480 |
| `park` | 313 | 1 | 1.500 |
| `pflege` | 313 | 1 | 3.640 |
| `przedszkole` | 313 | 1 | 3.110 |
| `spielplatz` | 313 | 1 | 790 |
| `supermarkt` | 313 | 1 | 740 |
| `szkola` | 313 | 1 | 1.400 |
| `szpital` | 313 | 1 | 3.290 |
| `zlobek` | 313 | 1 | 9.530 |

## Ganz Kraków (Summe der veröffentlichten Zähler und Nenner)

| Kennzahl | Art | Richtwert | Zähler | Nenner | Wert |
|---|---|---|---|---|---|
| `anteil_in_radius` | `szkola` | 3.000 m (art. 39 ust. 2, s. 40) | 784.590 | 793.390 | 99 % |
| `anteil_in_radius` | `szkola` | 4.000 m (art. 39 ust. 2, s. 40) | 789.320 | 793.390 | 99 % |
| `anteil_in_radius` | `przedszkole` | 3.000 m (art. 32 ust. 3, s. 36) | 710.470 | 793.390 | 90 % |
| `oepnv_takt` | `haltestelle_takt` | ohne | 622.690 | 793.390 | 78 % |
| `gruen_in_radius` | `park` | ohne | 291.580 | 793.390 | 37 % |

## Grenzen

- Ziele: Schulen, Kindergärten, Krippen und Krankenhäuser nur aus BDOT10k (Komplexe mit eigener Fläche, keine Plätze, Vollständigkeit gegen das Schulregister nicht geprüft); Krippen: nur 2 Einträge.
- Gehgeschwindigkeit, Grün-Radius und Grünarten sind Standards der Fußweg-Rechnung, solange `config/richtwerte.yaml` sie nicht nennt.
