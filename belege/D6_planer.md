# Beleg Planer je dzielnica (Luftlinie)

Erzeugt von `skripte/15_planer_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). Regeln vor dem Lauf: `pruefen/D6_protokoll.md`, Regeln 11–15.

## Schritt 1: Zuordnung

- Einwohner in Zellen mit dzielnica: 793.392; in Zellen ohne gültige dzielnica: 0
- Einrichtungen (szkola, przedszkole, zlobek) einer dzielnica zugeordnet: szkola 170, przedszkole 35, zlobek 2; ohne Zelle mit dzielnica: 0
- Parks (BDOT10k „park lub skwer“): 90, Fläche 5.375.029 m², davon in Zellen mit dzielnica 5.370.968 m²
- dzielnice unter 100 Einwohnern (kein Wert): 0

## Schritt 2: Werte ganz Kraków (Summe der veröffentlichten Zähler und Nenner)

| Kennzahl | Art | Richtwert | Zähler | Nenner | Wert |
|---|---|---|---|---|---|
| `anteil_in_radius` | `szkola` | 3.000 m (art. 39 ust. 2, s. 40) | 788.730 | 793.390 | 99 % |
| `anteil_in_radius` | `szkola` | 4.000 m (art. 39 ust. 2, s. 40) | 792.080 | 793.390 | 100 % |
| `anteil_in_radius` | `przedszkole` | 3.000 m (art. 32 ust. 3, s. 36) | 742.800 | 793.390 | 94 % |
| `ew_je_einrichtung` | `szkola` | ohne | 793.390 | 170 | 4.667 EW je Einrichtung |
| `ew_je_einrichtung` | `przedszkole` | ohne | 793.390 | 35 | 22.668 EW je Einrichtung |
| `ew_je_einrichtung` | `zlobek` | ohne | 793.390 | 2 | 396.695 EW je Einrichtung |
| `oepnv_takt` | `haltestelle_takt` | ohne | 760.290 | 793.390 | 96 % |
| `gruen_m2_je_ew` | `park` | ohne | 5.370.967 | 793.390 | 6,8 m² je EW |

## Grenzen

- Luftlinie, kein Fußweg; alle Einwohner einer Zelle am Zellmittelpunkt.
- Bildungsradien: Die Fundstellen (art. 39 ust. 2 und art. 32 ust. 3 Prawo oświatowe) meinen den Weg zur Schule des eigenen Schulbezirks; gerechnet ist die Luftlinie zur nächsten Schule jeder Art. Deshalb Orientierung und vorläufig, nie „standard urzędowy“.
- Kein Richtwert für Einwohner je Einrichtung, ÖPNV und Grün: keine polnische amtliche Fundstelle gesucht oder gefunden (nicht geprüft).
- Einwohner insgesamt statt Kinder je Altersgruppe (die Zellen tragen keine Kinderzahlen).
- Wilson-Intervalle entfallen (Vollerhebung über Zellen, Regel 15).
