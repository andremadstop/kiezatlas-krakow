# Zählungen der Kartenseiten Erreichbarkeit, Kamienice und Wohnungsbestand

Erzeugt von `pruefen/S2_zaehlungen.py` aus den Datendateien (keine Datenbank, kein Netz). Jede Zahl, die die
Seiten `planer`, `kamienice` und `modernizacja` zeigen, steht hier mit der Regel, nach der die Seite sie aus
derselben Datei liest oder rechnet. `--pruefen` vergleicht byte-gleich.

## Eingänge

| Datei | SHA-256 |
|---|---|
| `daten/erreichbar.js` | `a0c99211b589a7999cd44629b0b85655e116c4ebc911718df6bbdda0a87d1a5c` |
| `daten/erreichbar_fuss_odbl.js` | `91aeedf86a2c94722f515602683d80a3cad7bb4bf5240c3fa9fe98cb15c677bf` |
| `daten/einrichtungen.js` | `51eff068411be127e466b90345129b1c20b925b242b237998dd68bd844ebdc42` |
| `daten/einrichtungen_odbl.js` | `6b8692e55dd70b0f95a2bebe1a4c04cb4695d796fb147d5787e11ebfc98c1d1e` |
| `daten/haltestellen.js` | `48f0c874acc2ac78c867372e16613014714d4c6c53913385a2c4bbc53cc5f2c2` |
| `daten/planer_odbl.js` | `10d832f0152873f8bf3bc90ded621ed35cda584912d8a0b326e92c7ef2dd0a19` |
| `daten/planer_fuss_odbl.js` | `36041f2c3498aadbe671b8f98288634ea6b24c7ec50c6f42806f8aba48eff270` |
| `daten/zellen_odbl.js` | `a5f3914c590a99258fccfaa29ab30212f1c3612ccdb3483cae130f60aab98862` |
| `daten/denkmale_odbl.js` | `f5cc71aedefe3c3a1678f0cb9b9c418f286cbe5a0fd1afeceefce5cbc7c42573` |
| `daten/denkmale_bdot.js` | `946d38aa1ecab8aeffc364e95cc679fd9af07de329372a60ba3a3248ef6b6b65` |
| `daten/sanierung.js` | `ff01bf2d5c7bbf1794fe23408a0c5e0dd51ea0d90f013eabe495b38b00ff06a0` |
| `daten/sanierung_odbl.js` | `9b09a2778ad4871f092c4a880bc0f8e068eb4c9e4a35a568ec53383ea5d855b9` |

## Erreichbarkeit (`planer`, Modul `erreichbarkeit.js`)

Zellen: 327 (`zellen_odbl.js`); Reihenfolge geprüft wie im Modul (anzahl, erste_id, letzte_id):
- Luftlinie, erreichbar.js: passt = ja; Zellen mit Wert je Ziel (Zellen ohne Wert sind auf der Karte grau):
  haltestelle_takt 314, park 314, przedszkole 314, szkola 314, szpital 314, zlobek 314
- Fußweg, erreichbar_fuss_odbl.js: passt = ja; Zellen mit Wert je Ziel (Zellen ohne Wert sind auf der Karte grau):
  apotheke 313, arzt 313, haltestelle_takt 313, park 313, pflege 313, przedszkole 313, spielplatz 313, supermarkt 313, szkola 313, szpital 313, zlobek 313

Punkte je Ziel, wie die Legende sie zählt (Filter `art` in der Datei):
- BDOT10k (`einrichtungen.js`): park 90, przedszkole 35, szkola 170, szpital 24, zlobek 2
- OpenStreetMap (`einrichtungen_odbl.js`): apotheke 321, arzt 283

Haltestellen (`haltestellen.js`, Fahrplantag 2026-11-18, Fenster 06:00–09:00): 944; je Taktklasse I 509, II 284, III 114, unter III 37; außerhalb der Stadt 131. Klassengrenzen (Abfahrten je Stunde, Legende): I ≥ 6, II ≥ 2, III ≥ 1.

Kennzahlen je Stadtteil, Luftlinie (`planer_odbl.js`, Stand 2026-11-13, Einwohner gerundet auf 10): 18 Stadtteile, je Stadtteil [8] Kennzahlen; ganze Stadt:
- anteil_in_radius / szkola, Richtwert 3000 m: Wert 99 %, Zähler 788730, Nenner 793390, Status orientierung
- anteil_in_radius / szkola, Richtwert 4000 m: Wert 100 %, Zähler 792080, Nenner 793390, Status orientierung
- anteil_in_radius / przedszkole, Richtwert 3000 m: Wert 94 %, Zähler 742800, Nenner 793390, Status orientierung
- ew_je_einrichtung / szkola: Wert 4667 ew_je_einrichtung, Zähler 793390, Nenner 170, Status orientierung
- ew_je_einrichtung / przedszkole: Wert 22668 ew_je_einrichtung, Zähler 793390, Nenner 35, Status orientierung
- ew_je_einrichtung / zlobek: Wert 396695 ew_je_einrichtung, Zähler 793390, Nenner 2, Status orientierung
- oepnv_takt / haltestelle_takt: Wert 96 %, Zähler 760290, Nenner 793390, Status orientierung
- gruen_m2_je_ew / park: Wert 6.8 m2_je_ew, Zähler 5370967, Nenner 793390, Status orientierung

Kennzahlen je Stadtteil, Fußweg (`planer_fuss_odbl.js`, Stand 2026-11-13, Einwohner gerundet auf 10): 18 Stadtteile, je Stadtteil [5] Kennzahlen; ganze Stadt:
- anteil_in_radius / szkola, Richtwert 3000 m: Wert 99 %, Zähler 784590, Nenner 793390, Status orientierung
- anteil_in_radius / szkola, Richtwert 4000 m: Wert 99 %, Zähler 789320, Nenner 793390, Status orientierung
- anteil_in_radius / przedszkole, Richtwert 3000 m: Wert 90 %, Zähler 710470, Nenner 793390, Status orientierung
- oepnv_takt / haltestelle_takt: Wert 78 %, Zähler 622690, Nenner 793390, Status orientierung
- gruen_in_radius / park: Wert 37 %, Zähler 291580, Nenner 793390, Status orientierung

## Kamienice (`kamienice`, Modul `kamienice.js`)

OpenStreetMap (`denkmale_odbl.js`, Stand 2026-11-12): Objekte 929 (Feld zaehlung.objekte = 929).
- Standardansicht (Denkmalangabe, h = true): 184; je Bauzeitklasse 1800_1866 6, 1867_1918 24, 1919_1945 5, 1946_1989 3, null 132, vor_1800 14
- „Auch Objekte ohne Denkmalangabe“ (alle): 929; je Bauzeitklasse 1800_1866 17, 1867_1918 77, 1919_1945 32, 1946_1989 89, ab_1990 525, null 162, vor_1800 27
- „Nur Kamienice“ (h = true und mfh = true): 9; je Delegatur Kraków-Nowa Huta 1, Kraków-Podgórze 2, Kraków-Śródmieście 6; Feld kamienice der Datei: Summe 9 = Kraków-Nowa Huta 1, Kraków-Podgórze 2, Kraków-Śródmieście 6
- Objekte mit Denkmalangabe je Delegatur (Tabelle): Kraków-Krowodrza 15, Kraków-Nowa Huta 42, Kraków-Podgórze 43, Kraków-Śródmieście 84
- Feld zaehlung (Blatt): aus_relationen 23, ausserhalb_stadt 334, bauzeit_lesbar 767, bauzeit_nicht_lesbar 55, davon_mfh 102, mit_heritage 184, mit_start_date 822, objekte 929, relationen_gelesen 46, relationen_ohne_flaeche 0, relationen_ohne_lage 21, relationen_unvollstaendig 1, treffer_gebaeude 441, wege_als_teil_einer_relation 2
- Sichtprüfung: geprüft = True, Stichprobe 20; Lage auf dem Objekt 16 von 20 = 80.0 %, beide Quellen 33 von 40 = 82.5 %
- Ortsmarke: kosciuszki_18, Quelle osm, lage_geprueft = False

BDOT10k (`denkmale_bdot.js`, Stand 2026-10-03): gebaeude 90563, wohngebaeude 61199, mehrfamilienhaeuser 13739, namensbezug 28, mfh_in_zespol_zabudowy 0; Komplexe muzeum 3, pamiec 1, twierdza 38, zabudowa 17 (Polygone in der Datei: 59)
- je Delegatur: Kraków-Krowodrza: Mehrfamilienhäuser 3764, Name „Kamienica“ 0; Kraków-Nowa Huta: Mehrfamilienhäuser 1733, Name „Kamienica“ 0; Kraków-Podgórze: Mehrfamilienhäuser 4441, Name „Kamienica“ 0; Kraków-Śródmieście: Mehrfamilienhäuser 3801, Name „Kamienica“ 28

## Wohnungsbestand und Sanierung (`modernizacja`, Modul `sanierungsatlas.js`)

Liste (`sanierung.js`, Stand 2025-12-01): Einträge 508; je Art M 159, MP 6, MU 96, MUP 2, P 43, U 196, UP 6; je Eigentum gmina 410, skarb_panstwa 34, publiczne_mieszane 4, z_prywatnymi 46, prywatne 14, brak 0; samoistne posiadanie 15; Orte krakow 500, wieliczka 8.
- Punkte in der Karte (`sanierung_odbl.js`): 126; Eigentum gmina 122, publiczne_mieszane 1, skarb_panstwa 3 (nur gmina, skarb_panstwa, publiczne_mieszane); weggelassene Einfamilienhäuser 44, unter 3 Geschossen oder ohne Geschosszahl 171
- Punkte je Art (Legende): M 51, MP 4, MU 41, P 13, U 17
- Punkte mit Typ (violetter Ring): blok 19, osiedle 8
- Höhenherkunft der Punkte: geschosse 18, lod2 108
- Verortung: Quote 79.6 % von 500 (Wilson 95 %: 75.8–82.9); Klassen verortet 398, beschreibung 36, poza_krakowem 8, ulica_nie_znaleziona 34, numer_nie_znaleziony 20, mehrdeutig_ulica 0, mehrdeutig_punkt 4, abweichung_dzielnica 8
- Gegenprobe dzielnica: 398 von 406 = 98.0 % (Wilson 95 %: 96.2–99.0)
- Verknüpfung: verortet 398, umriss 228, punkt 167, ohne 3, gebaeude_einzeln 376, hoehe_lod2 370, hoehe_geschosse 25, typ_blok 21, typ_osiedle 8

Typologie (Schätzung = True, Baujahr = False); Kriterien geschosse_min 4, flaeche_min_m2 250, rechteckigkeit_min 0.85, umkreis_m 150, nachbarn_min 9.
- Stadt: Mehrfamilienhäuser 13573, Kandidaten 3341 (24,6 %), in Großsiedlungen 943 (6,9 %)
- Anteile je Stadtteil, wie die Karte sie färbt (Kandidaten / Mehrfamilienhäuser, Stufen 10/20/30/40 %):
  - 01: ZBK-Einträge 82, Punkte 31, Mehrfamilienhäuser 2259, Kandidaten 238 (10,5 %), Großsiedlung 65 (2,9 %)
  - 02: ZBK-Einträge 21, Punkte 3, Mehrfamilienhäuser 936, Kandidaten 202 (21,6 %), Großsiedlung 49 (5,2 %)
  - 03: ZBK-Einträge 25, Punkte 4, Mehrfamilienhäuser 604, Kandidaten 242 (40,1 %), Großsiedlung 46 (7,6 %)
  - 04: ZBK-Einträge 24, Punkte 2, Mehrfamilienhäuser 1265, Kandidaten 470 (37,2 %), Großsiedlung 188 (14,9 %)
  - 05: ZBK-Einträge 18, Punkte 4, Mehrfamilienhäuser 1207, Kandidaten 280 (23,2 %), Großsiedlung 166 (13,8 %)
  - 06: ZBK-Einträge 9, Punkte 2, Mehrfamilienhäuser 496, Kandidaten 156 (31,5 %), Großsiedlung 44 (8,9 %)
  - 07: ZBK-Einträge 23, Punkte 0, Mehrfamilienhäuser 729, Kandidaten 92 (12,6 %), Großsiedlung 43 (5,9 %)
  - 08: ZBK-Einträge 45, Punkte 22, Mehrfamilienhäuser 1122, Kandidaten 248 (22,1 %), Großsiedlung 51 (4,5 %)
  - 09: ZBK-Einträge 17, Punkte 4, Mehrfamilienhäuser 302, Kandidaten 41 (13,6 %), Großsiedlung 0 (0,0 %)
  - 10: ZBK-Einträge 19, Punkte 2, Mehrfamilienhäuser 443, Kandidaten 50 (11,3 %), Großsiedlung 21 (4,7 %)
  - 11: ZBK-Einträge 8, Punkte 2, Mehrfamilienhäuser 576, Kandidaten 221 (38,4 %), Großsiedlung 42 (7,3 %)
  - 12: ZBK-Einträge 21, Punkte 8, Mehrfamilienhäuser 655, Kandidaten 224 (34,2 %), Großsiedlung 60 (9,2 %)
  - 13: ZBK-Einträge 74, Punkte 17, Mehrfamilienhäuser 1272, Kandidaten 192 (15,1 %), Großsiedlung 18 (1,4 %)
  - 14: ZBK-Einträge 7, Punkte 2, Mehrfamilienhäuser 353, Kandidaten 83 (23,5 %), Großsiedlung 8 (2,3 %)
  - 15: ZBK-Einträge 6, Punkte 1, Mehrfamilienhäuser 435, Kandidaten 175 (40,2 %), Großsiedlung 35 (8,0 %)
  - 16: ZBK-Einträge 17, Punkte 5, Mehrfamilienhäuser 220, Kandidaten 143 (65,0 %), Großsiedlung 35 (15,9 %)
  - 17: ZBK-Einträge 35, Punkte 10, Mehrfamilienhäuser 174, Kandidaten 87 (50,0 %), Großsiedlung 39 (22,4 %)
  - 18: ZBK-Einträge 49, Punkte 7, Mehrfamilienhäuser 525, Kandidaten 197 (37,5 %), Großsiedlung 33 (6,3 %)
  - Einträge außerhalb Krakaus (poza): 8
- Summen: Kandidaten je Stadtteil 3341 (Stadt 3341), Mehrfamilienhäuser je Stadtteil 13573 (Stadt 13573)
- Ortsmarke: in der Liste = True, Art MU, Eigentum gmina, Stadtteil laut Liste 07; Lage geprüft = False
- Literatur (nur bibliographisch): Barnaś, Jeleński, Nowak-Ocłoń, Racoń-Leja, Energy 263 (2023) 125774, DOI 10.1016/j.energy.2022.125774

Bezug Erreichbarkeit in der Tabelle (`planer_fuss_odbl.js`, Wert der Kennzahl je Stadtteil):
  - 01: Haltestelle Taktklasse I/II 87 %, Park 89 %
  - 02: Haltestelle Taktklasse I/II 86 %, Park 15 %
  - 03: Haltestelle Taktklasse I/II 100 %, Park 26 %
  - 04: Haltestelle Taktklasse I/II 82 %, Park 26 %
  - 05: Haltestelle Taktklasse I/II 74 %, Park 46 %
  - 06: Haltestelle Taktklasse I/II 72 %, Park 0 %
  - 07: Haltestelle Taktklasse I/II 91 %, Park 34 %
  - 08: Haltestelle Taktklasse I/II 51 %, Park 15 %
  - 09: Haltestelle Taktklasse I/II 54 %, Park 28 %
  - 10: Haltestelle Taktklasse I/II 76 %, Park 7 %
  - 11: Haltestelle Taktklasse I/II 100 %, Park 0 %
  - 12: Haltestelle Taktklasse I/II 69 %, Park 55 %
  - 13: Haltestelle Taktklasse I/II 48 %, Park 31 %
  - 14: Haltestelle Taktklasse I/II 87 %, Park 48 %
  - 15: Haltestelle Taktklasse I/II 74 %, Park 72 %
  - 16: Haltestelle Taktklasse I/II 100 %, Park 53 %
  - 17: Haltestelle Taktklasse I/II 79 %, Park 39 %
  - 18: Haltestelle Taktklasse I/II 89 %, Park 84 %
