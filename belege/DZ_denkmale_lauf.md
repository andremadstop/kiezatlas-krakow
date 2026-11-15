# Lauf Denkmale und Kamienice (erzeugt von `skripte/dz_denkmale.py`, nicht von Hand ändern)

Regeln: `pruefen/DZ_protokoll.md`. Diese Datei entsteht bei jedem Lauf neu und ist Teil der Reproduzierbarkeitsprüfung (`--pruefen`).

## Eingänge

| Eingang | Datei | SHA256 |
|---|---|---|
| BDOT10k 1261 | `$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip` | `68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d` |
| wd | `eingang/wikidata_zabytki_krakow.json` | `926fd1830fd1002a28b618289e971c1ce2525e78a44217da95ccfcd198f53a5e` |
| nid | `eingang/nid_rejestr_zabytkow.csv` | fehlt (Beispieldaten, solange alle drei fehlen) |
| gez | `eingang/gez_krakow.csv` | fehlt (Beispieldaten, solange alle drei fehlen) |
| osm | `eingang/malopolskie-261112.osm.pbf` | `525d0d227cb9c876c4df02278e7fac870f0825ab0ae2c7228af6dc5c9e0f5a7e` |

## Schritt 1: BDOT10k (echte Daten)

| Zählung | Wert |
|---|---|
| gebaeude | 90563 |
| wohngebaeude | 61199 |
| mehrfamilienhaeuser | 13739 |
| namensbezug | 28 |
| mfh_in_zespol_zabudowy | 0 |

`kat_istnie`:

| Wert | Anzahl |
|---|---|
| eksploatowany | 88998 |
| nieczynny | 255 |
| w budowie | 1155 |
| zniszczony | 155 |
| Summe | 90563 |

`komplexe`:

| Wert | Anzahl |
|---|---|
| muzeum | 3 |
| pamiec | 1 |
| twierdza | 38 |
| zabudowa | 17 |
| Summe | 59 |

Je Delegatura (Schwerpunkt im Umriss aus `OT_ADJA_A`):

| Delegatura | Wohngebäude | Mehrfamilienhäuser | Namensbezug |
|---|---|---|---|
| Kraków-Krowodrza | 15568 | 3764 | 0 |
| Kraków-Nowa Huta | 9691 | 1733 | 0 |
| Kraków-Podgórze | 29518 | 4441 | 0 |
| Kraków-Śródmieście | 6422 | 3801 | 28 |
| keiner zugeordnet | 0 | 0 | 0 |
| Summe | 61199 | 13739 | 28 |

## Schritt 2: Register (Wikidata, NID, Gminna ewidencja)

`wd`:

| Zählung | Wert |
|---|---|
| ausserhalb_stadt | 2 |
| bauzeit_lesbar | 873 |
| bauzeit_nicht_lesbar | 16 |
| davon_mfh | 571 |
| doppelt_ueber_nummer | 684 |
| in_stadt | 1214 |
| mit_lage | 1216 |
| ohne_lage | 9 |
| treffer_gebaeude | 1125 |
| zeilen | 1909 |


## Schritt 3: OSM heritage/start_date

| Zählung | Wert |
|---|---|
| aus_relationen | 23 |
| ausserhalb_stadt | 334 |
| bauzeit_lesbar | 767 |
| bauzeit_nicht_lesbar | 55 |
| davon_mfh | 102 |
| mit_heritage | 184 |
| mit_start_date | 822 |
| objekte | 929 |
| relationen_gelesen | 46 |
| relationen_ohne_flaeche | 0 |
| relationen_ohne_lage | 21 |
| relationen_unvollstaendig | 1 |
| treffer_gebaeude | 441 |
| wege_als_teil_einer_relation | 2 |

Ortsmarke ul. Kościuszki 18 (`skripte/ortsmarke.py`, dieselbe Koordinate wie in `daten/sanierung_odbl.js`): OSM `w233092542` (umriss, 2 Kandidaten in der Stadt), Punkt 19.92538, 50.05421; Lage nicht von Hand geprüft

## Stichprobe zur Sichtprüfung, erste Runde (Startwert 20261113)

Ausgewertet: nein. Diese Runde ist von keinem Menschen geprüft; abgelöst durch die zweite Runde (unten, ausgewertet), nach der sich `sichtpruefung` in den Datendateien richtet. OSM-Punkte nur aus Gebäudetreffern mit `heritage` (`pruefen/DZ_protokoll.md`, Nachtrag 2).

| Quelle | Lage (Länge, Breite) | Mehrfamilienhaus | Delegatura | Bauzeitklasse |
|---|---|---|---|---|
| wd | 19.95089, 50.04364 | True | Kraków-Podgórze | 1867_1918 |
| wd | 19.9408, 50.0619 | False | Kraków-Śródmieście | None |
| wd | 19.9393, 50.0638 | True | Kraków-Śródmieście | vor_1800 |
| wd | 19.94544, 50.05881 | True | Kraków-Śródmieście | 1867_1918 |
| wd | 19.86157, 50.08486 | False | Kraków-Krowodrza | 1867_1918 |
| wd | 19.93506, 50.06344 | False | Kraków-Śródmieście | 1867_1918 |
| wd | 19.9253, 50.0542 | True | Kraków-Krowodrza | None |
| wd | 19.93985, 50.06133 | False | Kraków-Śródmieście | vor_1800 |
| wd | 19.94494, 50.04979 | False | Kraków-Śródmieście | vor_1800 |
| wd | 19.94453, 50.05298 | False | Kraków-Śródmieście | 1800_1866 |
| wd | 19.9374, 50.0575 | False | Kraków-Śródmieście | None |
| wd | 19.94292, 50.06154 | False | Kraków-Śródmieście | 1867_1918 |
| wd | 19.94279, 50.0504 | True | Kraków-Śródmieście | vor_1800 |
| wd | 19.93094, 50.062 | True | Kraków-Śródmieście | None |
| wd | 19.93469, 50.06198 | True | Kraków-Śródmieście | 1867_1918 |
| wd | 19.9542, 50.0739 | False | Kraków-Śródmieście | 1800_1866 |
| wd | 19.9515, 50.05903 | False | Kraków-Śródmieście | 1867_1918 |
| wd | 19.93753, 50.05923 | False | Kraków-Śródmieście | vor_1800 |
| wd | 19.9386, 50.0614 | False | Kraków-Śródmieście | None |
| wd | 19.93479, 50.06212 | True | Kraków-Śródmieście | vor_1800 |
| osm | 19.93776, 50.0609 | False | Kraków-Śródmieście | None |
| osm | 19.86589, 50.04846 | False | Kraków-Krowodrza | None |
| osm | 19.93594, 50.05755 | False | Kraków-Śródmieście | None |
| osm | 19.95789, 50.04275 | False | Kraków-Podgórze | 1800_1866 |
| osm | 19.84544, 50.08442 | False | Kraków-Krowodrza | None |
| osm | 20.05531, 50.08185 | False | Kraków-Nowa Huta | None |
| osm | 19.92718, 50.07163 | False | Kraków-Krowodrza | 1919_1945 |
| osm | 20.10875, 50.06914 | False | Kraków-Nowa Huta | 1800_1866 |
| osm | 19.93186, 50.06505 | False | Kraków-Śródmieście | None |
| osm | 19.88368, 50.0062 | False | Kraków-Podgórze | None |
| osm | 19.96795, 50.03177 | False | Kraków-Podgórze | None |
| osm | 19.91268, 50.05256 | False | Kraków-Krowodrza | None |
| osm | 20.17904, 50.09585 | False | Kraków-Nowa Huta | vor_1800 |
| osm | 19.9334, 50.06166 | False | Kraków-Śródmieście | None |
| osm | 19.9472, 49.99402 | False | Kraków-Podgórze | 1867_1918 |
| osm | 19.88271, 50.00645 | True | Kraków-Podgórze | None |
| osm | 19.947, 50.07819 | False | Kraków-Śródmieście | None |
| osm | 20.10531, 50.06795 | False | Kraków-Nowa Huta | None |
| osm | 19.85923, 50.06819 | False | Kraków-Krowodrza | None |
| osm | 19.94705, 50.06547 | False | Kraków-Śródmieście | 1800_1866 |

## Stichprobe zur Sichtprüfung, zweite Runde (Startwert 20261114)

Regel: `pruefen/DZ_protokoll.md`, Nachtrag 3. Geprüft werden nur Lage und Ansicht. Grundgesamtheit ist die Menge der Karte: 1214 Registerpunkte aus Wikidata und 184 OSM-Objekte mit `heritage`. Ausgewertet: ja (Abschnitt „Sichtprüfung Runde 2, ausgewertet“). Dieselbe Liste maschinenlesbar: `belege/DZ_sichtpruefung_stichprobe.json`.

| Nr. | Quelle | Kennung | Lage (Länge, Breite) | Lage stimmt | Ansicht passt |
|---|---|---|---|---|---|
| 1 | wd | Q30168587 | 19.92728, 50.06703 | ja | ja |
| 2 | wd | Q30168712 | 19.93768, 50.05876 | ja | ja |
| 3 | wd | Q30162015 | 19.95606, 50.04476 | ja | ja |
| 4 | wd | Q8512319 | 20.10074, 50.11035 | daneben | unklar |
| 5 | wd | Q3109262 | 19.94667, 50.05167 | ja | ja |
| 6 | wd | Q11787595 | 19.9482, 50.0532 | ja | ja |
| 7 | wd | Q30171408 | 19.93222, 50.06021 | ja | ja |
| 8 | wd | Q11828765 | 19.94757, 50.06479 | ja | ja |
| 9 | wd | Q122187417 | 19.90956, 50.07573 | ja | ja |
| 10 | wd | Q30170057 | 19.94337, 50.06307 | ja | ja |
| 11 | wd | Q9294055 | 19.93762, 50.05622 | ja | ja |
| 12 | wd | Q3527492 | 19.94306, 50.06389 | ja | ja |
| 13 | wd | Q30172017 | 19.93453, 50.06049 | ja | ja |
| 14 | wd | Q125524675 | 19.91091, 50.05353 | daneben | ja |
| 15 | wd | Q30169866 | 19.94273, 50.05056 | ja | unklar |
| 16 | wd | Q30161657 | 19.95345, 50.04204 | daneben | ja |
| 17 | wd | Q30171746 | 19.94123, 50.06311 | ja | ja |
| 18 | wd | Q30162679 | 19.94186, 50.04883 | ja | ja |
| 19 | wd | Q30168851 | 19.93825, 50.05775 | ja | ja |
| 20 | wd | Q30169476 | 19.93733, 50.05656 | ja | ja |
| 21 | osm | w136657671 | 19.90405, 50.04144 | daneben | unklar |
| 22 | osm | w243432610 | 19.93939, 50.05928 | ja | ja |
| 23 | osm | w911299568 | 19.99696, 50.01047 | daneben | unklar |
| 24 | osm | w128616563 | 20.05531, 50.08185 | ja | ja |
| 25 | osm | n1500744003 | 19.96136, 50.029 | ja | ja |
| 26 | osm | w111250379 | 19.96902, 49.98891 | nein | unklar |
| 27 | osm | w143916299 | 19.93248, 50.05957 | ja | ja |
| 28 | osm | w276339026 | 19.96748, 50.08644 | ja | ja |
| 29 | osm | w140560836 | 19.88049, 50.00329 | ja | ja |
| 30 | osm | w347660889 | 19.95783, 49.98712 | daneben | ja |
| 31 | osm | w39357573 | 19.93891, 50.06313 | ja | ja |
| 32 | osm | w137276375 | 19.95716, 50.04331 | ja | ja |
| 33 | osm | w85151350 | 19.9355, 50.05467 | ja | ja |
| 34 | osm | w348252385 | 19.95594, 50.06365 | ja | ja |
| 35 | osm | w123993275 | 20.10434, 50.0684 | ja | ja |
| 36 | osm | w219172195 | 20.10865, 50.06809 | ja | ja |
| 37 | osm | w244542996 | 19.99214, 49.99484 | ja | ja |
| 38 | osm | w152301900 | 19.94731, 50.06065 | ja | ja |
| 39 | osm | w152330075 | 19.9488, 50.06207 | ja | ja |
| 40 | osm | w227963540 | 20.14699, 50.0878 | ja | ja |

## Sichtprüfung Runde 2, ausgewertet

Eingabe `belege/DZ_sichtpruefung.json` (von Hand, Prüfung am 2026-11-15, Ortofotomapa Geoportal, Quelle je Punkt verdeckt), vom Skript gegen die Stichprobe geprüft: jede Kennung aus der Stichprobe, jeder Punkt genau einmal, Werte aus den erlaubten Listen. Regel vor dem Rechnen festgelegt (`pruefen/DZ_protokoll.md`, Nachtrag 4): Lage-Quote = ja / alle (daneben zählt nicht als ja), Ansicht-Quote = ja / entschiedene (ja + nein, unklar nicht im Nenner); 95-%-Intervall nach Wilson.

| Quelle | n | Lage ja | daneben | nein | Lage-Quote % | Wilson 95 % | Ansicht ja | nein | unklar | Ansicht-Quote % (ja von entschiedenen) | Wilson 95 % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Wikidata | 20 | 17 | 3 | 0 | 85,0 | 64,0–94,8 | 18 | 0 | 2 | 100,0 (18 von 18) | 82,4–100,0 |
| OSM | 20 | 16 | 3 | 1 | 80,0 | 58,4–91,9 | 17 | 0 | 3 | 100,0 (17 von 17) | 81,6–100,0 |
| gesamt | 40 | 33 | 6 | 1 | 82,5 | 68,1–91,3 | 35 | 0 | 5 | 100,0 (35 von 35) | 90,1–100,0 |

Die Quote beschreibt die Ebene, gewonnen aus einer Zufallsstichprobe von je 20 Punkten; sie sagt nichts über einen einzelnen Punkt außerhalb der Stichprobe. Bauzeitklasse und Zuordnung zum Gebäude waren nicht Gegenstand der Runde. In `daten/` steht kein Name des Prüfers, nur `pruefer_rolle: sichtpruefung_luftbild`, Grundlage und Datum; `denkmale.js` trägt nur das Ergebnis der Wikidata-Punkte, `denkmale_odbl.js` das der OSM-Punkte und das Gesamtergebnis.
