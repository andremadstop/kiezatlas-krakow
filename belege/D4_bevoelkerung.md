# Beleg Gliederung und Bevölkerung (erzeugt)

Erzeugt von `skripte/02_bevoelkerung.py`; nicht von Hand ändern. `skripte/02_bevoelkerung.py --pruefen` rechnet neu und vergleicht. Regeln: `pruefen/D4_protokoll.md`. Stand der Auswertung: 2026-11-13.

## Eingaben

| Datei (unter `$KIEZ_DATEN`) | Bytes | SHA256 |
|---|---|---|
| `2026-11-13/03_gebaeude/1261_SHP.zip` | 32.403.983 | `68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d` |
| `2026-11-13/02_zensus/PL_PD_3035_GPKG.zip` | 19.867.756 | `293af7549bbf44138ae3c29ab6c62064bae0078edf750b12fb26cd1b77df46c4` |
| `2026-11-13/02_zensus/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx` | 27.012.607 | `72bcef42c30f307249097cd03657d7f46ec06b1203cf82122d9a7415e49c4ce8` |
| `eingang/malopolskie-261112.osm.pbf` | 203.717.015 | `525d0d227cb9c876c4df02278e7fac870f0825ab0ae2c7228af6dc5c9e0f5a7e` |
| `eingang/gus_brec/AreaStatisticalUnit_12.zip` | 26.482.011 | `d6de48e2d821019d11260d71f90cf8cda3fa18e6bd15b4aab3a7f3239fe59c34` |

Prüfsummen beim Abruf: `2026-11-13/HERKUNFT.md` und `2026-11-13/02_zensus/HERKUNFT.md` (Machbarkeitsprobe), Handdownload OSM: `eingang/HERKUNFT.md` und `eingang/SHA256SUMS`, Handdownload GUS BREC: `eingang/gus_brec/HERKUNFT.md`; zum Nachprüfen in `belege/rohdaten-D4-2026-11-13.sha256`.

## Schritt 1: Stadt und historische Stadtbezirke (BDOT10k `OT_ADJA_A`)

- Sätze in der Schicht: 8; Koordinatensystem laut .prj: ETRF2000-PL / CS92; Flächen gerechnet in ETRS89 / Poland CS2000 zone 7 (EPSG:2178).
- Stadt: Kraków (TERYT 1261011), 326,86 km², Datenquelle laut Attribut `ZRO_DANYCH`: PRG, Version 20251002000000.

| Gruppe | delegatura | TERYT | Fläche km² |
|---|---|---|---|
| 1 | Kraków-Śródmieście | 1261059 | 17,87 |
| 2 | Kraków-Krowodrza | 1261029 | 67,33 |
| 3 | Kraków-Podgórze | 1261049 | 130,91 |
| 4 | Kraków-Nowa Huta | 1261039 | 110,76 |

## Schritt 2: Grenzen der dzielnice

- Quelle: `eingang/malopolskie-261112.osm.pbf`, Datenstand laut Dateikopf 2026-11-12T21:23:05Z; Grenzrelationen mit römischer Ziffer in `ref`, `official_name` oder `name` (Kandidaten); zugeordnet 18 von 18 (Kandidaten 18, andere Verwaltungsebene 0, ohne Zuordnung 0, nur über den Namen getroffen und von einem Treffer mit Ziffer verdrängt 0).

| Nr | dzielnica | Gruppe | OSM-Objekt | Name in OSM | Fläche km² |
|---|---|---|---|---|---|
| I | Stare Miasto | 1 | relation/2642241 | Stare Miasto | 5,57 |
| II | Grzegórzki | 1 | relation/2648849 | Grzegórzki | 5,85 |
| III | Prądnik Czerwony | 1 | relation/2650730 | Prądnik Czerwony | 6,44 |
| IV | Prądnik Biały | 2 | relation/2650662 | Prądnik Biały | 23,42 |
| V | Krowodrza | 2 | relation/2649407 | Krowodrza | 5,62 |
| VI | Bronowice | 2 | relation/2650430 | Bronowice | 9,56 |
| VII | Zwierzyniec | 2 | relation/2642242 | Zwierzyniec | 28,73 |
| VIII | Dębniki | 3 | relation/2398482 | Dębniki | 46,19 |
| IX | Łagiewniki-Borek Fałęcki | 3 | relation/2398480 | Łagiewniki-Borek Fałęcki | 5,41 |
| X | Swoszowice | 3 | relation/2398484 | Swoszowice | 25,6 |
| XI | Podgórze Duchackie | 3 | relation/2645869 | Podgórze Duchackie | 9,54 |
| XII | Bieżanów-Prokocim | 3 | relation/2647604 | Bieżanów-Prokocim | 18,47 |
| XIII | Podgórze | 3 | relation/2398485 | Podgórze | 25,67 |
| XIV | Czyżyny | 4 | relation/2648668 | Czyżyny | 12,26 |
| XV | Mistrzejowice | 4 | relation/2650961 | Mistrzejowice | 5,59 |
| XVI | Bieńczyce | 4 | relation/2651178 | Bieńczyce | 3,7 |
| XVII | Wzgórza Krzesławickie | 4 | relation/2648584 | Wzgórza Krzesławickie | 23,81 |
| XVIII | Nowa Huta | 4 | relation/2648045 | Nowa Huta | 65,41 |

## Schritt 3: NSP 2021 je rejon statystyczny (GUS-Tabelle, Blatt „Małopolskie“)

- Kopfzellen geprüft: F3, G4, H4, I4, J4, M4, N4, O4, P4, Q4, R4, S4, T4, U4, V4.
- Zeilen für Kraków: 1 Stadt, 4 delegatury, 748 rejony, 4.592 obwody; Zellen mit „-“ (als 0 gelesen): 1.272.
- Einwohner Stadt: 800.653 (Symbol 1261); rejon kleinster/größter: 9 / 3.627; rejony unter 100 Personen: 4 (werden nie einzeln ausgeliefert).

| Gleichung (Regel 10) | links | rechts | erfüllt |
|---|---|---|---|
| Σ rejony = Stadt | 800.653 | 800.653 | ja |
| Σ obwody = Stadt | 800.653 | 800.653 | ja |
| Σ delegatury = Stadt | 800.653 | 800.653 | ja |
| Σ rejony in Kraków-Krowodrza = Zeile 1261029 | 171.427 | 171.427 | ja |
| Σ rejony in Kraków-Nowa Huta = Zeile 1261039 | 207.168 | 207.168 | ja |
| Σ rejony in Kraków-Podgórze = Zeile 1261049 | 301.550 | 301.550 | ja |
| Σ rejony in Kraków-Śródmieście = Zeile 1261059 | 120.508 | 120.508 | ja |
| Stadt: m + k = ogółem | 800.653 | 800.653 | ja |
| Stadt: Σ 10-Jahres-Gruppen = ogółem | 800.653 | 800.653 | ja |
| Stadt: Σ ökonomische Gruppen = ogółem | 800.653 | 800.653 | ja |
| Kraków-Krowodrza: m + k = ogółem | 171.427 | 171.427 | ja |
| Kraków-Krowodrza: Σ 10-Jahres-Gruppen = ogółem | 171.427 | 171.427 | ja |
| Kraków-Krowodrza: Σ ökonomische Gruppen = ogółem | 171.427 | 171.427 | ja |
| Kraków-Nowa Huta: m + k = ogółem | 207.168 | 207.168 | ja |
| Kraków-Nowa Huta: Σ 10-Jahres-Gruppen = ogółem | 207.168 | 207.168 | ja |
| Kraków-Nowa Huta: Σ ökonomische Gruppen = ogółem | 207.168 | 207.168 | ja |
| Kraków-Podgórze: m + k = ogółem | 301.550 | 301.550 | ja |
| Kraków-Podgórze: Σ 10-Jahres-Gruppen = ogółem | 301.550 | 301.550 | ja |
| Kraków-Podgórze: Σ ökonomische Gruppen = ogółem | 301.550 | 301.550 | ja |
| Kraków-Śródmieście: m + k = ogółem | 120.508 | 120.508 | ja |
| Kraków-Śródmieście: Σ 10-Jahres-Gruppen = ogółem | 120.508 | 120.508 | ja |
| Kraków-Śródmieście: Σ ökonomische Gruppen = ogółem | 120.508 | 120.508 | ja |
| rejony mit m + k ≠ ogółem | 0 | 0 | ja |
| rejony mit Σ 10-Jahres-Gruppen ≠ ogółem | 0 | 0 | ja |
| rejony mit Σ ökonomische Gruppen ≠ ogółem | 0 | 0 | ja |

## Schritt 4: Eurostat-Gitter 2021 (1 km)

- Datei im Zip: `PL_ESTAT_DF_CENSUS_GRID_2021_20240711162252.gpkg`, SRS 3035, Zellen gesamt 310.819, im Rahmen der Stadt (Hülle plus 1 km) 759.
- Mittelpunkt in der Stadt: 327 Zellen; ohne Wert `T`: 0; mit `Y_LT15 + Y15-64 + Y_GE65 ≠ T`: 14 (nicht korrigiert).
- Statusfelder der Zellen mit Mittelpunkt in der Stadt: T_OBS_STATUS = nan: 327; T_SPECIAL_VALUE = nan: 327; konventionell verortet > 0 = False: 327; nicht gezählt > 0 = False: 327.

| Raum | NSP 2021 | Gitter, Mittelpunkt | Abweichung | Gitter, Flächenanteil | Abweichung | Zellen (Mittelpunkt / berührt) |
|---|---|---|---|---|---|---|
| Kraków | 800.653 | 793.392 | -0,91 % | 791.825 | -1,10 % | 327 / 397 |
| Kraków-Śródmieście | 120.508 | 119.564 | -0,78 % | 116.128 | -3,63 % | 18 / 31 |
| Kraków-Krowodrza | 171.427 | 171.878 | +0,26 % | 171.076 | -0,20 % | 68 / 95 |
| Kraków-Podgórze | 301.550 | 300.353 | -0,40 % | 300.138 | -0,47 % | 132 / 174 |
| Kraków-Nowa Huta | 207.168 | 201.597 | -2,69 % | 204.483 | -1,30 % | 109 / 149 |

Der Unterschied zwischen Gitter und NSP mischt drei Dinge, die sich hier nicht trennen lassen: die Zuordnung ganzer 1-km-Zellen an der Grenze, die Verortung im Gitter (Eurostat) und mögliche Unterschiede im Stichtag oder in der Abgrenzung der Bevölkerung (nicht geprüft).

| Nr | dzielnica | Gitter, Mittelpunkt | Gitter, Flächenanteil | Spanne | Zellen (Mittelpunkt / berührt) |
|---|---|---|---|---|---|
| I | Stare Miasto | 38.588 | 33.992 | -11,9 % | 6 / 12 |
| II | Grzegórzki | 40.274 | 34.343 | -14,7 % | 7 / 14 |
| III | Prądnik Czerwony | 40.702 | 47.489 | +16,7 % | 5 / 15 |
| IV | Prądnik Biały | 82.609 | 79.284 | -4,0 % | 25 / 40 |
| V | Krowodrza | 32.468 | 39.981 | +23,1 % | 5 / 13 |
| VI | Bronowice | 30.271 | 28.822 | -4,8 % | 11 / 19 |
| VII | Zwierzyniec | 26.530 | 22.996 | -13,3 % | 27 / 46 |
| VIII | Dębniki | 83.179 | 78.058 | -6,2 % | 48 / 71 |
| IX | Łagiewniki-Borek Fałęcki | 14.888 | 21.262 | +42,8 % | 5 / 13 |
| X | Swoszowice | 29.541 | 32.152 | +8,8 % | 24 / 43 |
| XI | Podgórze Duchackie | 67.758 | 55.524 | -18,1 % | 11 / 18 |
| XII | Bieżanów-Prokocim | 58.052 | 63.260 | +9,0 % | 20 / 32 |
| XIII | Podgórze | 46.935 | 49.884 | +6,3 % | 24 / 46 |
| XIV | Czyżyny | 33.487 | 43.132 | +28,8 % | 13 / 24 |
| XV | Mistrzejowice | 55.623 | 51.518 | -7,4 % | 5 / 17 |
| XVI | Bieńczyce | 35.783 | 40.228 | +12,4 % | 4 / 12 |
| XVII | Wzgórza Krzesławickie | 19.584 | 21.421 | +9,4 % | 23 / 42 |
| XVIII | Nowa Huta | 57.120 | 48.479 | -15,1 % | 64 / 97 |

## Schritt 5: rejony → dzielnica

- Quelle `eingang/gus_brec/AreaStatisticalUnit_12.zip`, Sätze 749, Kennungsfeld `thematicId (sechsstellig, exakt)`, zugeordnet 748.
- obwody in der Geometrie: 4.614 (Tabelle: 4.592); Σ Fläche der rejony 326,84 km² (Stadt 326,86 km²).
- rejony der Geometrie ohne Zeile in der Tabelle (keine Werte, nicht zugeordnet; ob unbewohnt, ist nicht geprüft): 390570 (delegatura 1261029).
- rejony mit mehr als 5 % Fläche in einer anderen dzielnica: 42 (390052, 390562, 390610, 390620, 391050, 391060, 391080, 391411, 391462, 391600, 391621, 391631, 391641, 391682, 392032, 392370, 392582, 392620, 392696, 392840, 392860, 393091, 393172, 393211, 393230, 393241, 393242, 393252, 393274, 393370, 393400, 393772, 393791, 393801, 393810, 393850, 393861, 393882, 393883, 394451 …).

## Regeln des Prüfprotokolls

| Regel | erfüllt | Angabe |
|---|---|---|
| Regel 3: Fläche der Vereinigung gegen die Stadt höchstens ±1 % | ja | -0,01 % |
| Regel 3: symmetrische Differenz höchstens 2 % der Stadtfläche | ja | 0,01 % |
| Regel 4: 01 Stare Miasto in Kraków-Śródmieście zu mindestens 99 % | ja | 100,00 % |
| Regel 4: 02 Grzegórzki in Kraków-Śródmieście zu mindestens 99 % | ja | 99,47 % |
| Regel 4: 03 Prądnik Czerwony in Kraków-Śródmieście zu mindestens 99 % | ja | 98,53 %; Rest: Kraków-Nowa Huta 1,47 %; dokumentierte Ausnahme (Grenzsplitter zwischen delegatury der BDOT10k und dzielnice, MSIP-Gegenprobe; Entscheidung vom 13.11.2026) |
| Regel 4: 04 Prądnik Biały in Kraków-Krowodrza zu mindestens 99 % | ja | 99,99 % |
| Regel 4: 05 Krowodrza in Kraków-Krowodrza zu mindestens 99 % | ja | 99,99 % |
| Regel 4: 06 Bronowice in Kraków-Krowodrza zu mindestens 99 % | ja | 100,00 % |
| Regel 4: 07 Zwierzyniec in Kraków-Krowodrza zu mindestens 99 % | ja | 99,99 % |
| Regel 4: 08 Dębniki in Kraków-Podgórze zu mindestens 99 % | ja | 99,99 % |
| Regel 4: 09 Łagiewniki-Borek Fałęcki in Kraków-Podgórze zu mindestens 99 % | ja | 100,00 % |
| Regel 4: 10 Swoszowice in Kraków-Podgórze zu mindestens 99 % | ja | 99,99 % |
| Regel 4: 11 Podgórze Duchackie in Kraków-Podgórze zu mindestens 99 % | ja | 100,00 % |
| Regel 4: 12 Bieżanów-Prokocim in Kraków-Podgórze zu mindestens 99 % | ja | 99,99 % |
| Regel 4: 13 Podgórze in Kraków-Podgórze zu mindestens 99 % | ja | 99,99 % |
| Regel 4: 14 Czyżyny in Kraków-Nowa Huta zu mindestens 99 % | ja | 99,48 % |
| Regel 4: 15 Mistrzejowice in Kraków-Nowa Huta zu mindestens 99 % | ja | 98,64 %; Rest: Kraków-Śródmieście 1,36 %; dokumentierte Ausnahme (Grenzsplitter zwischen delegatury der BDOT10k und dzielnice, MSIP-Gegenprobe; Entscheidung vom 13.11.2026) |
| Regel 4: 16 Bieńczyce in Kraków-Nowa Huta zu mindestens 99 % | ja | 100,00 % |
| Regel 4: 17 Wzgórza Krzesławickie in Kraków-Nowa Huta zu mindestens 99 % | ja | 100,00 % |
| Regel 4: 18 Nowa Huta in Kraków-Nowa Huta zu mindestens 99 % | ja | 99,99 % |
| Regel 7: Gitter Stadt gegen NSP höchstens ±2 % | ja | -0,91 % |
| Regel 8: Gitter Kraków-Śródmieście gegen NSP höchstens ±5 % | ja | -0,78 % |
| Regel 8: Gitter Kraków-Krowodrza gegen NSP höchstens ±5 % | ja | +0,26 % |
| Regel 8: Gitter Kraków-Podgórze gegen NSP höchstens ±5 % | ja | -0,40 % |
| Regel 8: Gitter Kraków-Nowa Huta gegen NSP höchstens ±5 % | ja | -2,69 % |
| Gitter: jede Zelle mit Mittelpunkt in der Stadt liegt in genau einer dzielnica | ja | 0 Zellen ohne dzielnica |
| Gitter: Zellen mit Mittelpunkt in den dzielnice = Zellen mit Mittelpunkt in der Stadt (gleiche IDs) | ja | 327 / 327 Zellen, 0 nur über die dzielnice |
| Regel 11: jeder rejon der Tabelle hat eine Geometrie | ja | 0 ohne Geometrie |
| Regel 11 (Rückrichtung): rejony der Geometrie ohne Tabellenzeile höchstens 2 von 1000 | ja | 1 von 749 (390570) |
| Regel 11: delegatura der Geometrie = delegatura der Tabelle | ja | 0 abweichend |
| Plausibilität: Σ Fläche der rejony gegen die Stadtfläche (BDOT10k) höchstens ±1 % | ja | -0,01 % |
| Regel 11: Σ rejony über alle dzielnice = Stadt | ja | 800653 / 800653 |
| Karte je rejon: Σ Einwohner = Stadt (NSP) | ja | 800653 / 800653 |
| Karte je rejon: jede Kennung der Tabelle genau einmal | ja | 749 Flächen, 749 Kennungen |
| Karte je rejon: kein Anteil unter 100 Personen | ja | 4 rejony unter 100, 0 mit Anteil |
| Karte je rejon: Differenzprobe, kein unterdrückter Anteil eingrenzbar | ja | 0 eingrenzbar |
| Regel 10: Gleichungen der NSP-Tabelle (oben) | ja | 25 von 25 |

Befunde, die das Schreiben sperren: 0.

Regel 4: 2 dzielnice unter 99 % mit dokumentierter Ausnahme (Entscheidung vom 13.11.2026, Nachtrag in `pruefen/D4_protokoll.md`): III Prądnik Czerwony und XV Mistrzejowice gelten mit 98,53 % bzw. 98,64 % als ihrer delegatura zugeordnet; der Rest ist ein Grenzsplitter zwischen den delegatury der BDOT10k und den dzielnice (Gegenprobe mit den städtischen Grenzen, nur intern). Die Schwelle 99 % bleibt; die Ausnahme gilt nur für genau diese Anteile. `zuordnung_geprueft` = `true`.

## Ausgaben

- `daten/kennzahlen_odbl.js`
- `daten/kennzahlen_odbl.json`
- `daten/rejony.js`
- `daten/stadtteile_odbl.js`
- `daten/steckbrief.js`
- `daten/steckbrief_dzielnice_odbl.js`
- `daten/zellen_odbl.js`

## Grenzen

- Stichtag des NSP 2021 (31.03.2021) und des Gitters aus Vorwissen, nicht an einer Fundstelle geprüft.
- Das Gitter hat 1 km Weite; je dzielnica fallen nur wenige Zellen ganz hinein. Die Spanne zwischen Mittelpunkt- und Flächenanteilsregel ist das Maß der Unschärfe, keine Fehlergrenze.
- Altersgruppen sind zwischen den Quellen nicht gleich geschnitten: Gitter unter 15 / 15–64 / 65 und älter, NSP 10-Jahres-Gruppen und ökonomische Gruppen (vor, im, nach dem Erwerbsalter, Grenzen nach Geschlecht verschieden). Sie werden nicht ineinander umgerechnet.
- Regel 4 vergleicht mit den delegatury der BDOT10k (aus PRG); ob deren Grenzen die amtliche Gruppierung der dzielnice abbilden, ist nicht amtlich geprüft. Die Reste von III und XV gelten nach der Gegenprobe mit den städtischen Grenzen als Grenzsplitter (Entscheidung vom 13.11.2026).
- NSP je dzielnica ist die Summe der rejony mit innerem Punkt in der dzielnica (Schritt 5); rejony an den Grenzen zählen ganz zu einer dzielnica. Lizenz der Geometrie: Feed INSPIRE des GUS (`quellen-D4.md`).
- Lizenz des Eurostat-Gitters in der strengsten Lesart (CC BY 4.0); Bestätigung durch Eurostat offen.
- Gemeldete Einwohner der Stadt (BIP Kraków) sind ein anderes Konzept und werden nicht verwendet (Lizenzangabe fehlt).
