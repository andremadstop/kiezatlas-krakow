# Beleg Klima: Versiegelung und Grün (Bodenbedeckung BDOT10k)

Erzeugt von `skripte/35_klimat.py` (nicht von Hand ändern; `--pruefen` vergleicht byteweise). Regeln und Schwellen: `pruefen/dk_protokoll.md`, vor dem ersten Lauf festgelegt. Quellen und Lizenz: `quellen-dk.md`.

## Eingaben

| Datei | SHA256 |
|---|---|
| `$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip` | `68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d` |
| `$KIEZ_DATEN/2026-11-13/10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html` (nur Gegenprobe) | `297b2944c3b24eba2e61abeec85c9e0a0ab704fb6d5c7936f7268c7e20095c69` |
| `daten/stadtteile_odbl.js` | `561dd8d8923cbb51e4876da74bc14ecd774b6f2e8ca20b78746c5238f47ef89e` |
| `daten/kennzahlen_odbl.json` | `29392de541ab6279239604d39176051f5ba3f73ffbf6f55e4f40bd49eab2b86a` |

Stand der BDOT10k-Dateien laut Zip-Verzeichnis: 2026-10-03. Koordinatensystem der Dateien: ETRF2000-PL / CS92; gerechnet in ETRS89 / Poland CS2000 zone 7 (EPSG:2178). Werkzeuge: Python 3.13.12, shapely 2.2.0 (GEOS 3.14.1), pyproj 3.8.0 (PROJ 9.8.1), numpy 2.5.4.

## Schritt 1: Lesen je Schicht

| Schicht | Sätze | gelöscht | anderer TERYT | ohne Geometrie | ungültig, repariert | Flächenänderung durch Reparatur (m²) | in der Stadt | Fläche in der Stadt (ha) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `PTGN_A` | 9 | 0 | 0 | 0 | 0 | 0,0 | 9 | 9,3 |
| `PTKM_A` | 117 | 0 | 0 | 0 | 0 | 0,0 | 117 | 1 549,0 |
| `PTLZ_A` | 1946 | 0 | 0 | 0 | 0 | 0,0 | 1946 | 3 984,6 |
| `PTNZ_A` | 549 | 0 | 0 | 0 | 0 | 0,0 | 549 | 595,8 |
| `PTPL_A` | 1413 | 0 | 0 | 0 | 0 | 0,0 | 1413 | 531,5 |
| `PTRK_A` | 68 | 0 | 0 | 0 | 0 | 0,0 | 68 | 96,1 |
| `PTSO_A` | 5 | 0 | 0 | 0 | 0 | 0,0 | 5 | 136,4 |
| `PTTR_A` | 5555 | 0 | 0 | 0 | 0 | 0,0 | 5555 | 14 076,1 |
| `PTUT_A` | 1174 | 0 | 0 | 0 | 0 | 0,0 | 1174 | 914,6 |
| `PTWP_A` | 342 | 0 | 0 | 0 | 0 | 0,0 | 342 | 679,2 |
| `PTWZ_A` | 7 | 0 | 0 | 0 | 0 | 0,0 | 7 | 23,9 |
| `PTZB_A` | 11546 | 0 | 0 | 0 | 0 | 0,0 | 11546 | 10 089,4 |
| `ADJA_A` | 8 | 0 | 0 | 0 | 0 | 0,0 | – | – |

Ringe (Löcher, mehrteilige Polygone, Löcher ohne Außenring, zu kurze Ringe, leere Formen): `PTGN_A` loecher 0; `PTKM_A` loecher 164; `PTLZ_A` loecher 141; `PTNZ_A` loecher 16; `PTPL_A` loecher 8; `PTRK_A` loecher 1; `PTSO_A` loecher 0; `PTTR_A` loecher 1267; `PTUT_A` loecher 29; `PTWP_A` loecher 16; `PTWZ_A` loecher 0; `PTZB_A` loecher 781.
Flächen der Bodenbedeckung ganz außerhalb der Stadtgrenze (verworfen): 0.

## Schritt 2: Fläche je Schicht und RODZAJ in der Stadt

| Schicht | RODZAJ | Klasse | Fläche (ha) |
|---|---|---|---:|
| `PTGN` | pozostałe grunty nieużytkowane | `sonstige` | 6,7 |
| `PTGN` | teren piaszczysty lub żwirowy | `sonstige` | 2,6 |
| `PTKM` | (ohne) | `verkehr` | 1 549,0 |
| `PTLZ` | las | `wald` | 2 653,0 |
| `PTLZ` | zadrzewienie | `wald` | 1 305,4 |
| `PTLZ` | zagajnik | `wald` | 26,2 |
| `PTNZ` | teren pod urządzeniami technicznymi lub budowlami | `sonstige` | 344,1 |
| `PTNZ` | teren przemysłowo-składowy | `sonstige` | 251,7 |
| `PTPL` | (ohne) | `verkehr` | 531,5 |
| `PTRK` | krzewy | `gruen` | 96,1 |
| `PTSO` | odpady komunalne | `sonstige` | 22,3 |
| `PTSO` | odpady przemysłowe | `sonstige` | 114,2 |
| `PTTR` | roślinność trawiasta | `gruen` | 10 426,5 |
| `PTTR` | uprawa na gruntach ornych | `acker` | 3 649,6 |
| `PTUT` | ogródki działkowe | `gruen` | 511,6 |
| `PTUT` | plantacja | `gruen` | 31,2 |
| `PTUT` | sad | `gruen` | 351,9 |
| `PTUT` | szkółka roślin | `gruen` | 19,9 |
| `PTWP` | woda płynąca | `wasser` | 365,4 |
| `PTWP` | woda stojąca | `wasser` | 313,7 |
| `PTWZ` | wyrobisko | `sonstige` | 21,8 |
| `PTWZ` | zwałowisko | `sonstige` | 2,1 |
| `PTZB` | handlowo-usługowa | `bebauung` | 516,9 |
| `PTZB` | jednorodzinna | `bebauung` | 4 417,1 |
| `PTZB` | pozostała zabudowa | `bebauung` | 1 487,2 |
| `PTZB` | przemysłowo-składowa | `bebauung` | 1 029,1 |
| `PTZB` | wielorodzinna | `bebauung` | 2 639,1 |

Bebauung (`PTZB`) nach dem Merkmal `ROSLINNOSC` (Bewuchs innerhalb der bebauten Fläche), zur Einordnung der Näherung für Versiegelung:

| ROSLINNOSC | Fläche (ha) |
|---|---:|
| brak | 6 840,3 |
| brak – plac twardy | 1 097,0 |
| drzewa | 301,4 |
| trawa | 1 850,8 |

## Schritt 3: Abdeckung der Stadtfläche (Regel 3)

- Stadtfläche A (`OT_ADJA_A`, gmina 1261011): 32 686,0 ha
- Summe der Klassenflächen S: 32 686,0 ha
- Vereinigung U (Raster 1 cm): 32 685,9 ha
- Überlappung S − U: 0,01 ha = 0,000 % von A (Schwelle 0,500 %)
- Lücke A − U: 0,02 ha = 0,000 % von A (Schwelle 0,500 %)

## Schritt 4: Stadt

| Klasse | Fläche (ha) | Anteil (%) |
|---|---:|---:|
| `bebauung` | 10 089,4 | 30,9 |
| `verkehr` | 2 080,5 | 6,4 |
| `gruen` | 11 437,2 | 35,0 |
| `wald` | 3 984,6 | 12,2 |
| `wasser` | 679,2 | 2,1 |
| `acker` | 3 649,6 | 11,2 |
| `sonstige` | 765,5 | 2,3 |
| `bebauung_verkehr` (abgeleitet) | – | 37,2 |
| `gruen_wald` (abgeleitet) | – | 47,2 |

Grün je Einwohner der Stadt: 194 m².

## Schritt 5: Delegaturen (Regel 5)

| IDTERYTJED | Name | Gruppe nach Namen | Fläche (ha) | `bebauung` (%) | `verkehr` (%) | `gruen` (%) | `wald` (%) | `wasser` (%) | `acker` (%) | `sonstige` (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1261029 | Kraków-Krowodrza | 2 | 6 733,1 | 31,6 | 5,4 | 29,6 | 17,1 | 1,7 | 14,2 | 0,5 |
| 1261039 | Kraków-Nowa Huta | 4 | 11 075,8 | 22,8 | 6,5 | 36,6 | 7,2 | 2,1 | 20,5 | 4,3 |
| 1261049 | Kraków-Podgórze | 3 | 13 090,5 | 33,8 | 6,2 | 38,4 | 14,8 | 2,2 | 3,2 | 1,4 |
| 1261059 | Kraków-Śródmieście | 1 | 1 786,5 | 57,0 | 10,8 | 20,0 | 5,7 | 2,1 | 0,1 | 4,3 |

- Σ Fläche der Delegaturen: 32 686,0 ha, Abweichung von A 0,000 % (Schwelle 0,100 %)
- größte Abweichung einer Klassensumme: 0,000 %
- Die Gruppe ist nur über den Namen zugeordnet (`Kraków-<Name>` = Name der Gruppe in `config/krakow.yaml`); welche dzielnice zu welcher Delegatur gehören, ist hier nicht geprüft.

## Schritt 6: 1-km-Zellen (Regel 7)

- Zellen, die die Stadt schneiden: 397
- davon mit weniger als 10 ha in der Stadt (Anteile null): 29
- davon ganz in der Stadt: 263
- Σ Zellteile in der Stadt: 32 686,0 ha, Abweichung von A 0,000 % (Schwelle 0,010 %)
- größte Abweichung einer Klassensumme über die Zellen: 0,000 % (Schwelle 0,100 %)

## Schritt 7: dzielnice (Regel 5, 9, 10)

- Grenzen aus `daten/stadtteile_odbl.js`: echt; Einwohner aus `daten/kennzahlen_odbl.json`: echt.
- Ausgabe `daten/klimat_stadtteile_odbl.js`: echt.
- dzielnice mit weniger als 10 ha in der Stadt: 0
- Grün je Einwohner je dzielnica (Regel 8, Ergänzung; Einwohner echt): mit Wert 18
- Σ Fläche der dzielnice innerhalb der Stadt: 32 682,0 ha, Abweichung von A 0,012 % (Schwelle 0,500 %)

| nr | Name | Fläche Grenze (ha) | davon in der Stadt (ha) | BIP-Fläche (ha) | Abweichung |
|---|---|---:|---:|---:|---:|
| 01 | Stare Miasto | 556,7 | 556,7 | 556,8 | -0,009 % |
| 02 | Grzegórzki | 584,6 | 584,6 | 584,5 | 0,019 % |
| 03 | Prądnik Czerwony | 643,6 | 643,6 | 643,8 | -0,022 % |
| 04 | Prądnik Biały | 2 342,0 | 2 341,7 | 2 341,9 | -0,006 % |
| 05 | Krowodrza | 562,0 | 562,0 | 561,9 | 0,015 % |
| 06 | Bronowice | 956,0 | 955,9 | 956,0 | -0,002 % |
| 07 | Zwierzyniec | 2 873,1 | 2 872,9 | 2 873,1 | -0,007 % |
| 08 | Dębniki | 4 618,8 | 4 618,5 | 4 618,9 | -0,007 % |
| 09 | Łagiewniki-Borek Fałęcki | 541,4 | 541,4 | 541,5 | -0,020 % |
| 10 | Swoszowice | 2 560,5 | 2 560,1 | 2 560,4 | -0,013 % |
| 11 | Podgórze Duchackie | 954,0 | 954,0 | 954,0 | 0,002 % |
| 12 | Bieżanów-Prokocim | 1 847,4 | 1 847,2 | 1 847,4 | -0,011 % |
| 13 | Podgórze | 2 566,8 | 2 566,7 | 2 566,7 | -0,001 % |
| 14 | Czyżyny | 1 225,6 | 1 225,6 | 1 225,7 | -0,010 % |
| 15 | Mistrzejowice | 559,2 | 559,2 | 559,0 | 0,030 % |
| 16 | Bieńczyce | 369,9 | 369,9 | 369,9 | -0,001 % |
| 17 | Wzgórza Krzesławickie | 2 381,5 | 2 381,3 | 2 381,6 | -0,011 % |
| 18 | Nowa Huta | 6 541,1 | 6 540,6 | 6 541,0 | -0,006 % |

## Schritt 8: Gegenprobe Stadtfläche (Regel 6)

- BIP der Stadt, Zeile „RAZEM“: 32 683,90 ha (Wydział Geodezji Urzędu Miasta Krakowa)
- BDOT10k `OT_ADJA_A`: 32 685,96 ha
- Abweichung: 0,006 % (Schwelle 0,500 %)
- Zeilen je dzielnica im BIP-Abzug gefunden: 18 (nur mit echten Grenzen verglichen)

## Ergebnis

Alle Regeln des Protokolls eingehalten (0 Befunde).

## Grenzen

- Bebauung + Verkehr ist eine Näherung für Versiegelung, keine Messung: `PTZB` enthält Höfe und Gärten innerhalb bebauter Flächen, `PTPL` auch unbefestigte Plätze. Abzeichen „orientacyjnie“.
- Bodenbedeckung nach Stand der BDOT10k-Dateien (siehe oben), Einwohner nach dem Stand der Einwohnerdatei; die Zeitpunkte fallen auseinander.
- Hitze (Oberflächentemperatur), gemessene Versiegelung, Baumkronen: nicht berechnet, siehe `quellen-dk.md`.
- Nicht geprüft: die Genauigkeit der BDOT10k-Bodenbedeckung gegen Luftbild oder Begehung.
