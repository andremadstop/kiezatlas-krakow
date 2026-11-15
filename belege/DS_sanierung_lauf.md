# Beleg Sanierungsatlas Wohnungsbestand: Lauf

Erzeugt von `skripte/36_sanierung.py` nach `pruefen/DS_protokoll.md`. Kein Netz, keine Datenbank. Werkzeuge: Python 3.13.12, Poppler pdftotext 26.10.0, shapely 2.2.0. Rechen-Koordinatensystem der Typologie: ETRS89 / Poland CS2000 zone 7 (EPSG:2178); Verknüpfung im Koordinatensystem der BDOT10k-Lieferung.

## Eingänge

| Eingang | Datei | SHA256 |
|---|---|---|
| ZBK-Liste (2025-12-01) | `$KIEZ_DATEN/zbk/2026-11-13/zbk_wykaz_2025-12.pdf` | `dffd7cb572d1bb9e1094824991d6b4b932923f44f56f545140effe740bf02de6` |
| Regeln der Weiterverwendung | `$KIEZ_DATEN/zbk/2026-11-13/bip_dok48482_ponowne.html` | `29cf66e42695f1dc119e0aba7fdb25204ae7f007f49ceb961c08767aad3e2391` |
| BDOT10k 1261 (Stand 2026-10-03) | `$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip` | siehe `belege/rohdaten-D5-2026-11-13.sha256` |
| OSM | `$KIEZ_DATEN/eingang/malopolskie-261112.osm.pbf` (Stand 2026-11-12T21:23:05Z) | siehe `$KIEZ_DATEN/eingang/SHA256SUMS` |
| LoD2 2017 | `$KIEZ_DATEN/eingang/lod2_1261_gml.zip` | siehe `$KIEZ_DATEN/eingang/SHA256SUMS` |

## Schritt 1: PDF → Tabelle

- Titel im PDF gefunden: „Wykaz budynków i obiektów w zarządzie ZBK na dzień 2025-12-01“ = True
- Seiten mit Einträgen: 26 von 26; Einträge je Seite: 18, 20, 22, 20, 22, 17, 20, 21, 16, 22, 19, 17, 20, 22, 20, 22, 21, 26, 17, 22, 21, 20, 18, 19, 23, 3
- Einträge N = 508; L.p. lückenlos 1 … 508: True
- Zweiter Leseweg (`pdftotext -layout`, Zeilen mit L.p. am Anfang) je Seite gleich und L.p. in gleicher Reihenfolge: True
- größter Abstand Zellmitte – Mitte der L.p.: 5.2 pt (Grenze 6.0 pt); Befunde: 0
- leere Pflichtfelder: dzielnica 0, name 0, rodzaj 0, wlasnosc 0

Rohwerte vor dem Vereinheitlichen (Anzahl Einträge):

- Vorsatz: „ul.“ 425; „os.“ 65; „al.“ 9; „pl.“ 7; (leer) 1; „al..“ 1
- Rodzaj: „U“ 194; „M“ 159; „M/U“ 82; „P“ 43; „U/M“ 12; „P/M“ 6; „U/P“ 6; „U/M/P“ 2; „U-Konsulat Francji“ 1; „U-Konsulat Niemiec“ 1; „U/M - w ZBK lokal mieszkalny“ 1; „U/M - w ZBK lokale mieszkalne“ 1
- Miejscowość: „Kraków“ 490; „Wieliczka“ 8; „Kraków - Barycz“ 3; „Kraków - dz.160/2 obr.14“ 2; „Kraków - dz.719/6 obr.10“ 2; „Kraków - dz. 152“ 1; „Kraków - dz.62 obr.9“ 1; „od 01-01- 2013 w Krakowie (dawniej Gmina - Kocmyrzów Luborzyca - do 31-12- 2012 r.)“ 1
- Dzielnica: „I - Stare Miasto“ 82; „XIII - Podgórze“ 74; „XVIII - Nowa Huta“ 49; „VIII - Dębniki“ 45; „XVII - Wzgórza Krzesławickie“ 35; „III - Prądnik Czerwony“ 25; „IV - Prądnik Biały“ 24; „VII - Zwierzyniec“ 23; „II - Grzegórzki“ 21; „XII - Bieżanów- Prokocim“ 21; „X - Swoszowice“ 19; „V - Krowodrza“ 18; „IX - Łagiewniki- Borek Fałęcki“ 17; „XVI - Bieńczyce“ 17; „VI - Bronowice“ 9; „XI - Podgórze Duchackie“ 8; „poza Krakowem - Wieliczka“ 8; „XIV - Czyżyny“ 7; „XV - Mistrzejowice“ 6

## Schritt 2: Vereinheitlicht (`daten/sanierung.js`)

- je Art: M 159, MP 6, MU 96, MUP 2, P 43, U 196, UP 6 (Σ 508)
- je Eigentum: gmina 410, skarb_panstwa 34, publiczne_mieszane 4, z_prywatnymi 46, prywatne 14, brak 0 (Σ 508); davon mit samoistne posiadanie: 15
- Art mit Zusatz im Rohtext (nicht veröffentlicht): 4
- Miejscowość: krakow 500, wieliczka 8
- Σ je Dzielnica: 508 = N

| Dzielnica | Einträge | M | U | P | MU | andere | gmina | skarb_panstwa | publiczne_mieszane | z_prywatnymi | prywatne | brak |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 82 | 14 | 23 | 5 | 37 | 3 | 50 | 3 | 1 | 24 | 4 | 0 |
| 02 | 21 | 6 | 8 | 1 | 5 | 1 | 14 | 0 | 0 | 6 | 1 | 0 |
| 03 | 25 | 8 | 9 | 4 | 4 | 0 | 25 | 0 | 0 | 0 | 0 | 0 |
| 04 | 24 | 2 | 14 | 4 | 3 | 1 | 20 | 2 | 0 | 1 | 1 | 0 |
| 05 | 18 | 7 | 8 | 1 | 2 | 0 | 13 | 2 | 2 | 1 | 0 | 0 |
| 06 | 9 | 2 | 3 | 3 | 0 | 1 | 8 | 1 | 0 | 0 | 0 | 0 |
| 07 | 23 | 5 | 13 | 2 | 3 | 0 | 20 | 2 | 0 | 1 | 0 | 0 |
| 08 | 45 | 30 | 9 | 2 | 4 | 0 | 42 | 2 | 0 | 1 | 0 | 0 |
| 09 | 17 | 11 | 2 | 1 | 3 | 0 | 15 | 1 | 0 | 0 | 1 | 0 |
| 10 | 19 | 3 | 9 | 1 | 5 | 1 | 16 | 3 | 0 | 0 | 0 | 0 |
| 11 | 8 | 3 | 1 | 2 | 2 | 0 | 5 | 3 | 0 | 0 | 0 | 0 |
| 12 | 21 | 7 | 6 | 1 | 5 | 2 | 19 | 0 | 1 | 0 | 1 | 0 |
| 13 | 74 | 32 | 20 | 2 | 19 | 1 | 55 | 2 | 0 | 11 | 6 | 0 |
| 14 | 7 | 1 | 3 | 2 | 1 | 0 | 7 | 0 | 0 | 0 | 0 | 0 |
| 15 | 6 | 0 | 5 | 1 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 |
| 16 | 17 | 4 | 10 | 3 | 0 | 0 | 17 | 0 | 0 | 0 | 0 | 0 |
| 17 | 35 | 9 | 19 | 2 | 3 | 2 | 26 | 9 | 0 | 0 | 0 | 0 |
| 18 | 49 | 13 | 28 | 6 | 0 | 2 | 44 | 4 | 0 | 1 | 0 | 0 |
| poza | 8 | 2 | 6 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 |

Nicht in der Liste: ein Verwalter je Eintrag (Verwalter ist laut Titel der ZBK) und eine Nummer im Denkmalregister. Beides wird nicht nachgetragen.

## Schritt 3: Tabelle → verortet (`daten/sanierung_odbl.js`)

- OSM-Adressen in der Stadtgrenze (BDOT10k): 73.093; Objekte mit heritage: 167; nicht gelesen: Relationen mit Adresse 284, offene oder am Rahmen abgeschnittene Wege 111, Adressen ohne Straße 27
- Einträge in Kraków (Dzielnica I–XVIII): 500; verortet 398 = 79,6 % (Wilson 95 %: 75,8–82,9 %)
- je Ergebnisklasse: verortet 398, beschreibung 36, poza_krakowem 8, ulica_nie_znaleziona 34, numer_nie_znaleziony 20, mehrdeutig_ulica 0, mehrdeutig_punkt 4, abweichung_dzielnica 8 (Σ 508 = N)
- Klassen der Hausnummer: (poza) 8, bereich 10, beschreibung 36, standard 401, zusatz 53

| Art | Einträge | verortet | Quote % | Wilson 95 % |
|---|---|---|---|---|
| M | 159 | 144 | 90,6 | 85,0–94,2 |
| MP | 6 | 6 | 100 | 61–100 |
| MU | 96 | 93 | 97 | 91–99 |
| MUP | 2 | 0 | 0 | 0–66 |
| P | 43 | 43 | 100 | 92–100 |
| U | 196 | 108 | 55,1 | 48,1–61,9 |
| UP | 6 | 4 | 67 | 30–90 |

Gegenprobe Dzielnica der Liste gegen OSM-dzielnica am Punkt (Grenzen aus eingang/malopolskie-261112.osm.pbf, OSM-Stand 2026-11-12T21:23:05Z): n = 406 Treffer, gleich 398 = 98,0 % (Wilson 95 %: 96,2–99,0 %). Abweichende Treffer sind nach Nachtrag 2 die Klasse abweichung_dzielnica (kein Punkt, keine Verknüpfung).

Abweichende Treffer (L.p., Art, Dzielnica Liste → OSM, Abstand des Punkts zum Polygon der Liste, Polygone grenzen aneinander): 54 M 13→12, 466 m, ja; 152 M 05→07, 903 m, ja; 190 M 08→10, 160 m, ja; 224 U 06→05, 1.157 m, ja; 271 M 09→10, 391 m, ja; 356 M 05→08, 3.165 m, nein; 468 M 01→03, 75 m, ja; 508 M 03→04, 201 m, ja. Ob Liste oder Verortung irrt, ist nicht geprüft.

Vergleichslauf ohne Nachtrag 1 (Namensregeln aus, im selben Lauf gerechnet): Treffer 394, davon verortet (dzielnica gleich) 386, ulica_nie_znaleziona 46. Mit Nachtrag 1: Treffer 406, verortet 398, ulica_nie_znaleziona 34.

Nicht verortete Einträge (L.p. Art Dzielnica, je Klasse; ohne Adresse, nachprüfbar am PDF):

- beschreibung (36): 11 U 04; 41 U 18; 43 U 18; 84 U 03; 88 U 08; 101 U 07; 102 U 07; 105 U 08; 109 U 04; 121 U 08; 147 U 09; 177 U 05; 186 U 08; 188 U 18; 194 U 07; 195 U 09; 210 U 05; 233 U 13; 252 U 13; 257 U 17; 295 U 18; 297 U 18; 298 U 18; 306 U 02; 327 U 13; 335 U 18; 382 U 07; 383 U 07; 390 U 04; 409 U 03; 423 MU 01; 430 U 18; 470 U 13; 474 U 05; 475 U 05; 476 U 05
- poza_krakowem (8): 371 M poza; 372 M poza; 373 U poza; 374 U poza; 375 U poza; 376 U poza; 377 U poza; 378 U poza
- ulica_nie_znaleziona (34): 10 U 04; 103 U 01; 106 U 07; 107 U 13; 108 U 06; 110 U 15; 111 U 15; 112 U 18; 113 U 17; 114 U 13; 115 U 10; 116 U 13; 117 U 10; 118 U 10; 119 U 10; 120 U 10; 122 U 07; 136 M 05; 164 U 16; 206 U 01; 208 MU 08; 244 U 07; 281 U 18; 282 U 18; 333 U 02; 415 U 03; 429 MUP 01; 449 U 05; 455 U 18; 490 U 13; 491 U 13; 492 U 13; 493 U 13; 494 U 13
- numer_nie_znaleziony (20): 24 MU 10; 39 U 18; 55 U 04; 86 MUP 01; 146 U 16; 149 U 03; 181 M 13; 182 M 13; 251 M 07; 262 U 17; 263 U 17; 264 U 17; 265 U 17; 266 U 17; 267 U 17; 268 U 17; 269 U 17; 285 UP 17; 287 U 17; 334 U 12
- mehrdeutig_ulica (0): keine
- mehrdeutig_punkt (4): 258 M 12; 284 UP 17; 447 M 08; 448 U 08
- abweichung_dzielnica (8): 54 M 13; 152 M 05; 190 M 08; 224 U 06; 271 M 09; 356 M 05; 468 M 01; 508 M 03

## Schritt 4: verortet → verknüpft

- verortet 398 (ohne abweichende Treffer): über OSM-Umriss (Schnitt ≥ 50 %) 228, über Punkt (im Gebäude oder bis 10 m) 167, ohne Gebäude 3 (Σ 398)
- verschiedene BDOT10k-Gebäude: 376 (mehrere Einträge je Adresse, etwa Vorderhaus und Oficyna, treffen dasselbe Gebäude)
- LoD2 2017 gelesen: 82.881 Gebäude mit Kennung; Höhe aus LoD2 bei 370 verorteten Einträgen, aus Geschossen × 3 m bei 25
- Denkmalangabe in OSM (heritage am Treffer oder im verknüpften Gebäude): 2 von 398 (keine Angabe heißt nicht „kein Denkmal“; das Feld steht deshalb nicht in den Daten, bis das Denkmalregister vorliegt)
- verknüpfte Gebäude, die Typologie-Kandidat sind: Block 21, Großsiedlung 8
- Punkte in der Datei (nur Eigentum gmina, skarb_panstwa, publiczne_mieszane, ohne samoistne posiadanie, ohne Einfamilienhäuser laut BDOT10k, ohne Wohnnutzung ohne Gebäudefunktion, nur Gebäude mit mindestens 3 Geschossen laut BDOT10k): 126; ausgelassen (nur gezählt) als Kleinhaus 44, unter 3 Geschossen oder ohne Geschosszahl 171
- Ortsmarke ul. Kościuszki 18: in der Liste (Dzielnica 07, Art MU, Eigentum gmina), verortet bei [19.92538, 50.05421], OSM-dzielnica 07, Höhe lod2, Denkmalangabe in OSM nein; Lage nicht von Hand geprüft; Punkt der Ortsmarke aus `skripte/ortsmarke.py` (gleich in `daten/denkmale_odbl.js`), OSM `w233092542` (umriss, 2 Kandidaten in der Stadt)

Fremde Vergleichsangabe (nicht eigene Zahl): Die FuturHist-Seite nennt für den ZBK „over 500 buildings“ und „Over 130 buildings managed by ZBK are under conservation protection“ (https://futurhist.eu/demonstrators/krakow/, abgerufen 2026-11-13). Die Liste hat 508 Einträge; Einträge sind keine Gebäude (Schritt 4).

## Schritt 5: Typologie (Schätzung)

- Grundgesamtheit: BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny: 13.573 Gebäude
- Kriterien: {"geschosse_min": 4, "flaeche_min_m2": 250, "rechteckigkeit_min": 0.85, "umkreis_m": 150, "nachbarn_min": 9}
- Stadt: Mehrfamilienhäuser 13.573, Kandidat Block 3.341, Kandidat Großsiedlung 943

| Raum | Mehrfamilienhäuser | Block | Großsiedlung |
|---|---|---|---|
| Kraków-Krowodrza | 3.697 | 998 | 441 |
| Kraków-Nowa Huta | 1.721 | 687 | 150 |
| Kraków-Podgórze | 4.370 | 976 | 192 |
| Kraków-Śródmieście | 3.785 | 680 | 160 |
| keiner Delegatur zugeordnet | 0 | 0 | 0 |

Σ Delegaturen + nicht zugeordnet = 13.573 (Stadt 13.573). Je dzielnica (OSM-Grenzen) nur in `daten/sanierung_odbl.js`.

Angebaut (Hinweis, keine Regel; `pruefen/DS_protokoll.md`, Nachtrag 5): Kandidaten, deren Umriss auf mindestens 3,0 m Länge an ein anderes Gebäude der BDOT10k grenzt (Toleranz 0,5 m). Blockrandbebauung mit gemeinsamen Brandwänden ist typisch für kamienice, freistehende Blöcke sind es nicht. Stadt: 919 von 3.341 Kandidaten angebaut, in Großsiedlungen 299 von 943. Je dzielnica:

| dzielnica | Kandidaten | davon angebaut | Großsiedlung | davon angebaut |
|---|---|---|---|---|
| 01 | 238 | 223 | 65 | 65 |
| 02 | 202 | 72 | 49 | 8 |
| 03 | 242 | 38 | 46 | 5 |
| 04 | 470 | 51 | 188 | 14 |
| 05 | 280 | 176 | 166 | 113 |
| 06 | 156 | 26 | 44 | 10 |
| 07 | 92 | 62 | 43 | 34 |
| 08 | 248 | 47 | 51 | 11 |
| 09 | 41 | 6 | 0 | 0 |
| 10 | 50 | 6 | 21 | 2 |
| 11 | 221 | 30 | 42 | 19 |
| 12 | 224 | 12 | 60 | 2 |
| 13 | 192 | 53 | 18 | 2 |
| 14 | 83 | 10 | 8 | 0 |
| 15 | 175 | 14 | 35 | 0 |
| 16 | 143 | 10 | 35 | 1 |
| 17 | 87 | 2 | 39 | 0 |
| 18 | 197 | 81 | 33 | 13 |

Grenze: Die Zahlen zählen die Merkmalskombination, keine Plattenbauten; sie sind weder Ober- noch Untergrenze und ungeprüft. Ohne Baujahr fallen rechteckige Wohnblöcke nach 1990 mit hinein, ebenso Mietshäuser (kamienice) der Blockrandbebauung mit mindestens 4 Geschossen, etwa im Stadtkern (dzielnica I: Altstadt, Kazimierz, Kleparz, Wesoła), und die Ziegelbauten des Sozialistischen Realismus in Nowa Huta. Plattenbauten mit unregelmäßigem Grundriss, aus mehreren Teilpolygonen oder mit weniger Nachbarn im Umkreis (lange Scheiben) fallen heraus. Bezug nur bibliographisch: Barnaś, Jeleński, Nowak-Ocłoń, Racoń-Leja, Energy 263 (2023) 125774, DOI 10.1016/j.energy.2022.125774; keine Zahl daraus wird hier verwendet.

Stichprobe zur Sichtprüfung (Startwert 20261113; Lage lon, lat; Delegatur; Geschosse). Prüfung am Luftbild am 2026-11-14 (Andre, Ortofotomapa Geoportal, Gruppen verdeckt; Eingabe `belege/DS_sichtpruefung.json`):

- Kandidat Großsiedlung (30): 19.88866, 50.09189 (Kraków-Krowodrza, 4); 20.01788, 50.08162 (Kraków-Nowa Huta, 5); 19.93458, 50.09838 (Kraków-Krowodrza, 4); 19.98, 50.05799 (Kraków-Śródmieście, 11); 19.95344, 50.09491 (Kraków-Krowodrza, 5); 19.97912, 50.06021 (Kraków-Śródmieście, 5); 19.99562, 50.04296 (Kraków-Podgórze, 12); 19.97964, 50.06046 (Kraków-Śródmieście, 5); 19.93549, 50.07418 (Kraków-Krowodrza, 6); 19.88911, 50.09515 (Kraków-Krowodrza, 4); 19.90638, 50.09612 (Kraków-Krowodrza, 4); 19.97994, 50.02092 (Kraków-Podgórze, 5); 19.90031, 50.07609 (Kraków-Krowodrza, 4); 19.92263, 50.05609 (Kraków-Krowodrza, 5); 19.92755, 50.07087 (Kraków-Krowodrza, 6); 19.96358, 50.09063 (Kraków-Śródmieście, 11); 19.93234, 50.07429 (Kraków-Krowodrza, 4); 19.91192, 50.02057 (Kraków-Podgórze, 4); 19.90252, 50.09562 (Kraków-Krowodrza, 4); 19.97695, 50.05814 (Kraków-Śródmieście, 5); 20.04796, 50.02609 (Kraków-Podgórze, 5); 19.91675, 50.08805 (Kraków-Krowodrza, 5); 20.06434, 50.09522 (Kraków-Nowa Huta, 4); 20.06234, 50.09593 (Kraków-Nowa Huta, 11); 19.93938, 50.08767 (Kraków-Krowodrza, 5); 19.91886, 50.05299 (Kraków-Krowodrza, 5); 19.96136, 50.00868 (Kraków-Podgórze, 7); 19.92491, 50.07093 (Kraków-Krowodrza, 5); 20.05352, 50.09493 (Kraków-Nowa Huta, 5); 19.91527, 50.07556 (Kraków-Krowodrza, 5)
- kein Kandidat, ≥ 4 Geschosse (10): 19.91485, 50.07391 (Kraków-Krowodrza, 4); 19.94474, 50.04786 (Kraków-Śródmieście, 6); 19.92316, 50.07144 (Kraków-Krowodrza, 5); 19.94085, 50.05212 (Kraków-Śródmieście, 4); 19.93568, 50.09752 (Kraków-Krowodrza, 6); 20.01155, 50.07686 (Kraków-Nowa Huta, 9); 19.93677, 50.07127 (Kraków-Śródmieście, 4); 19.85102, 50.08522 (Kraków-Krowodrza, 4); 20.02718, 50.08811 (Kraków-Nowa Huta, 11); 19.93776, 50.04919 (Kraków-Śródmieście, 6)

| Gruppe | gezogen | ja | nein | unklar | ja unter den entschiedenen | Wilson 95 % |
|---|---|---|---|---|---|---|
| Kandidat Großsiedlung | 30 | 21 | 5 | 4 | 81 % (21 von 26) | 62–91 % |
| Kontrolle: kein Kandidat | 10 | 4 | 4 | 2 | 50 % (4 von 8) | 22–78 % |

Bewertet wurde, ob am Luftbild ein Wohnblock zu sehen ist (Form, Lage, Umgebung), nicht die Bauweise; Großtafel und Ziegel lassen sich von oben nicht unterscheiden. Einzelergebnisse je Punkt sind nicht abgelegt. Bemerkungen des Prüfers: alle 5 Kandidaten mit „nein“ haben 4 oder 5 Geschosse und liegen in Krowodrza; unter den Kontrollen mit „ja“ sind Bauten in Nowa Huta mit 9 und 11 Geschossen.

Strengere Untergrenze der Geschosse, nachträglich an derselben Stichprobe gerechnet (keine Regeländerung; eine an der Stichprobe gewählte Grenze wäre an sie angepasst). „ja“ darunter: kleinster und größter möglicher Wert, weil die Einzelergebnisse fehlen.

| Untergrenze Geschosse | Punkte der Stichprobe | „ja“ darunter | Kandidaten Großsiedlung in der Stadt |
|---|---|---|---|
| 4 | 30 von 30 | 21–21 | 943 |
| 5 | 21 von 30 | 12–21 | 354 |
| 6 | 7 von 30 | 0–7 | 33 |

Laut Prüfer haben alle 5 „nein“ 4 oder 5 Geschosse. Eine Untergrenze von 6 Geschossen entfernt sie also, entfernt aber auch mindestens so viele „ja“, wie die Tabelle zeigt, und senkt die Zahl der Kandidaten in der Stadt. Ob 5 Geschosse die Quote verbessert, lässt sich ohne Einzelergebnisse nicht sagen. Die Regel bleibt; eine nach dzielnica geschichtete Stichprobe ist offen.

## Datenschutz

In `daten/sanierung*.js` stehen keine Adresse, keine L.p., keine Gebäudekennung und kein Name. Punkte nur für Einträge ohne Anteil von Privatpersonen und ohne samoistne posiadanie; Rohtext der Spalte Własność nur unter `$KIEZ_DATEN/abgeleitet/sanierung/` (außerhalb des Repos). Die Liste nennt nur Adressen und Eigentumsklassen, keine Mieter.
