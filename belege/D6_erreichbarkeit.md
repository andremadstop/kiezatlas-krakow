# Beleg Erreichbarkeit je Zelle (Luftlinie)

Erzeugt von `skripte/14_erreichbarkeit_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). Regeln vor dem Lauf: `pruefen/D6_protokoll.md`, Regeln 11 und 12.

## Eingaben

- Zellen: 327, davon bewohnt (ew > 0): 314
- Ziele je Art (Einrichtungen mit strittiger Lage zählen nicht): `haltestelle_takt` 793, `park` 90, `przedszkole` 35, `szkola` 170, `szpital` 24, `zlobek` 2

## Entfernungen bewohnter Zellen (m, auf 10 m gerundet)

| Art | Zellen mit Wert | Median | größter Wert |
|---|---|---|---|
| `haltestelle_takt` | 314 | 300 | 3.090 |
| `park` | 314 | 1.220 | 5.720 |
| `przedszkole` | 314 | 2.285 | 11.670 |
| `szkola` | 314 | 870 | 5.190 |
| `szpital` | 314 | 2.275 | 11.740 |
| `zlobek` | 314 | 7.615 | 17.150 |

## Grenzen

- Luftlinie, kein Fußweg: Flüsse (Wisła), Bahntrassen und Schnellstraßen sind nicht berücksichtigt. Der Fußweg folgt mit dem Netz des Pakets OSM und Fußwegnetz in `daten/erreichbar_fuss_odbl.js`.
- Alle Einwohner einer Zelle stehen am Zellmittelpunkt (1-km-Gitter).
- Nächste Einrichtung jeder Art, nicht die zuständige (Schulbezirke fehlen).
- Einrichtungen außerhalb der Stadtgrenze fehlen in BDOT10k Powiat 1261; Zellen am Stadtrand werden dadurch zu weit gerechnet (nicht beziffert).
