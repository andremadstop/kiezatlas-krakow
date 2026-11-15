# Vereinfachte Stadtteilgrenzen für die Übersicht (erzeugt)

Erzeugt von `skripte/02a_stadtteile_uebersicht.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). Regeln vor dem Lauf: `pruefen/N1_protokoll.md`, Regel 5.

- Eingabe: `daten/stadtteile_odbl.js`, SHA256 `561dd8d8923cbb51e4876da74bc14ecd774b6f2e8ca20b78746c5238f47ef89e`, 215.028 B, gzip -9 (Python, ohne Dateiname) 50.902 B
- Ausgabe: `daten/stadtteile_uebersicht_odbl.js`, 114.154 B, gzip -9 (Python, ohne Dateiname) 27.515 B
- Verfahren: `shapely.coverage_simplify` 2.2.0 (GEOS 3.14.1) in EPSG:2178, Toleranz 10 m, Koordinaten auf 5 Nachkommastellen
- Abnahme nach dem Runden: alle Geometrien gültig, Abdeckung gültig (`coverage_is_valid`), Löcher der Vereinigung 0 wie vorher, symmetrische Differenz der Vereinigungen 0,016 % der Stadtfläche (Grenze 1 %)

| dzielnica | Name | Punkte vorher | Punkte nachher | Fläche | Hausdorff |
|---|---|---|---|---|---|
| 01 | Stare Miasto | 253 | 139 | -0,006 % | 7,8 m |
| 02 | Grzegórzki | 261 | 143 | -0,012 % | 9,3 m |
| 03 | Prądnik Czerwony | 320 | 186 | +0,003 % | 9,3 m |
| 04 | Prądnik Biały | 795 | 357 | +0,003 % | 8,2 m |
| 05 | Krowodrza | 264 | 129 | +0,006 % | 6,7 m |
| 06 | Bronowice | 439 | 207 | +0,008 % | 6,1 m |
| 07 | Zwierzyniec | 609 | 339 | -0,003 % | 5,3 m |
| 08 | Dębniki | 1.116 | 592 | +0,001 % | 10,0 m |
| 09 | Łagiewniki-Borek Fałęcki | 345 | 179 | -0,012 % | 9,6 m |
| 10 | Swoszowice | 1.402 | 614 | +0,001 % | 10,6 m |
| 11 | Podgórze Duchackie | 500 | 265 | +0,001 % | 10,7 m |
| 12 | Bieżanów-Prokocim | 698 | 346 | +0,007 % | 10,7 m |
| 13 | Podgórze | 657 | 424 | +0,000 % | 10,1 m |
| 14 | Czyżyny | 431 | 262 | +0,000 % | 7,6 m |
| 15 | Mistrzejowice | 352 | 191 | -0,014 % | 7,8 m |
| 16 | Bieńczyce | 311 | 143 | +0,004 % | 7,8 m |
| 17 | Wzgórza Krzesławickie | 861 | 422 | +0,001 % | 9,8 m |
| 18 | Nowa Huta | 1.059 | 624 | +0,003 % | 8,0 m |

Grenzen je dzielnica: Fläche höchstens ±1 %, Hausdorff höchstens 40 m, gleiche Zahl an Teilflächen.
