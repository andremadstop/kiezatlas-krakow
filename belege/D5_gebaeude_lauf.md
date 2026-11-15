# Lauf Gebäude BDOT10k (erzeugt von `skripte/20_bdot10k.py`, nicht von Hand ändern)

Eingabe `1261_SHP.zip`, Dateidatum im Archiv 2026-10-03, jüngste `WERSJA` 2026-05-18.
Koordinatensystem der Quelle: ETRF2000-PL / CS92; Flächen in ETRS89 / Poland CS2000 zone 7 (EPSG:2178).

## Schritte

| Schritt | Zahl |
|---|---|
| Datensätze `OT_BUBD_A` (DBF) | 90563 |
| davon als gelöscht markiert | 0 |
| ohne Geometrie | 0 |
| ungültige Grundrisse, mit make_valid gerechnet | 0 |
| Grundriss ohne Fläche | 0 |
| mit Vermerk „Duplikaty …“ in `UWAGI` (nicht entfernt) | 466 |
| innerer Punkt in der Gemeinde Kraków | 90563 |
| außerhalb der Gemeinde | 0 |
| in einer Delegatur | 90563 |
| in der Gemeinde, aber in keiner Delegatur | 0 |
| in mehr als einer Delegatur (nur die erste gezählt) | 0 |
| in einer dzielnica (Grenzen aus daten/stadtteile_odbl.js) | 90563 |
| in mehr als einer dzielnica (nur die erste gezählt) | 0 |

## Gemeinde und Delegaturen (`OT_ADJA_A`)

| Größe | Wert |
|---|---|
| Delegaturen | 4 |
| Fläche Gemeinde (m²) | 326859586 |
| Fläche Vereinigung der Delegaturen (m²) | 326859586 |
| Deckung Vereinigung / Gemeinde | 1.0 |
| größte Überlappung zweier Delegaturen (m²) | 0.0 |

## Verteilungen in der Quelle (alle Datensätze mit Geometrie)

- `FOBUD`: budynki mieszkalne 61199; budynki produkcyjne, usługowe i gospodarcze dla rolnictwa 13993; budynki handlowo-usługowe 3371; budynki transportu i łączności 2996; budynki biurowe 2185; budynki przemysłowe 2006; budynki oświaty, nauki i kultury oraz budynki sportowe 1550; zbiorniki, silosy i budynki magazynowe 1473; pozostałe budynki niemieszkalne 1305; budynki szpitali i inne budynki opieki zdrowotnej 485
- `KAT_ISTNIE`: eksploatowany 88998; w budowie 1155; nieczynny 255; zniszczony 155
- `ZRO_DANYCH`: EGiB 82859; ortofotomapa 4480; inne 2450; BDOT500 550; mapa zasadnicza 224
- `LICZ_KONDY`: 2 35371; 1 32872; 3 11666; 4 4669; 5 3224; 6 883; 11 441; 7 385; 12 258; 8 246; (leer) 197; 9 160; 10 129; 14 24; 16 13; 15 10; 13 9; 17 4; 18 1; 26 1

## Höhe für 3D

| Herkunft | Gebäude |
|---|---|
| lod1 | 0 |
| lod2 | 74320 |
| geschosse | 16230 |
| ersatz | 13 |

- lod1: keine Datei unter `$KIEZ_DATEN/eingang/` (Handdownload ausstehend)

- lod2: Dateien lod2_1261_gml.zip; Zählung {"dateien": [{"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-a-4-2.gml", "gebaeude": 1}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-a-4-3.gml", "gebaeude": 51}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-a-4-4.gml", "gebaeude": 581}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-1-3.gml", "gebaeude": 1}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-3-1.gml", "gebaeude": 788}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-3-2.gml", "gebaeude": 189}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-3-3.gml", "gebaeude": 1975}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-3-4.gml", "gebaeude": 2008}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-4-1.gml", "gebaeude": 419}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-4-2.gml", "gebaeude": 56}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-4-3.gml", "gebaeude": 2608}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-b-4-4.gml", "gebaeude": 1107}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-1-2.gml", "gebaeude": 97}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-1-4.gml", "gebaeude": 5}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-2-1.gml", "gebaeude": 840}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-2-2.gml", "gebaeude": 1825}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-2-3.gml", "gebaeude": 810}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-2-4.gml", "gebaeude": 551}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-3-2.gml", "gebaeude": 0}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-3-4.gml", "gebaeude": 588}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-4-1.gml", "gebaeude": 352}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-4-2.gml", "gebaeude": 905}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-4-3.gml", "gebaeude": 642}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-c-4-4.gml", "gebaeude": 1005}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-1-1.gml", "gebaeude": 3024}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-1-2.gml", "gebaeude": 3292}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-1-3.gml", "gebaeude": 1031}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-1-4.gml", "gebaeude": 2498}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-2-1.gml", "gebaeude": 3182}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-2-2.gml", "gebaeude": 1637}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-2-3.gml", "gebaeude": 3205}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-2-4.gml", "gebaeude": 1422}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-3-1.gml", "gebaeude": 926}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-3-2.gml", "gebaeude": 2022}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-3-3.gml", "gebaeude": 2025}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-3-4.gml", "gebaeude": 2892}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-4-1.gml", "gebaeude": 1735}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-4-2.gml", "gebaeude": 2716}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-4-3.gml", "gebaeude": 2143}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-64-D-d-4-4.gml", "gebaeude": 1915}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-a-3-1.gml", "gebaeude": 75}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-a-3-2.gml", "gebaeude": 347}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-a-3-3.gml", "gebaeude": 1283}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-a-3-4.gml", "gebaeude": 1621}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-a-4-1.gml", "gebaeude": 179}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-a-4-2.gml", "gebaeude": 580}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-a-4-3.gml", "gebaeude": 1525}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-a-4-4.gml", "gebaeude": 493}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-b-3-1.gml", "gebaeude": 98}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-b-3-2.gml", "gebaeude": 280}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-b-3-3.gml", "gebaeude": 463}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-b-3-4.gml", "gebaeude": 616}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-b-4-1.gml", "gebaeude": 88}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-b-4-3.gml", "gebaeude": 23}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-1-1.gml", "gebaeude": 1239}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-1-2.gml", "gebaeude": 1025}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-1-3.gml", "gebaeude": 883}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-1-4.gml", "gebaeude": 1470}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-2-1.gml", "gebaeude": 533}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-2-2.gml", "gebaeude": 514}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-2-3.gml", "gebaeude": 369}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-2-4.gml", "gebaeude": 270}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-3-1.gml", "gebaeude": 1195}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-3-2.gml", "gebaeude": 590}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-3-3.gml", "gebaeude": 1485}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-3-4.gml", "gebaeude": 1878}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-4-1.gml", "gebaeude": 129}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-4-2.gml", "gebaeude": 1}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-c-4-3.gml", "gebaeude": 72}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-d-1-1.gml", "gebaeude": 346}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-d-1-2.gml", "gebaeude": 687}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-d-1-3.gml", "gebaeude": 377}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-d-1-4.gml", "gebaeude": 401}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-d-2-1.gml", "gebaeude": 147}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-d-2-3.gml", "gebaeude": 402}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-65-C-d-3-1.gml", "gebaeude": 0}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-a-1-2.gml", "gebaeude": 5}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-a-2-1.gml", "gebaeude": 76}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-a-2-2.gml", "gebaeude": 756}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-a-2-4.gml", "gebaeude": 83}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-b-1-1.gml", "gebaeude": 683}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-b-1-2.gml", "gebaeude": 1924}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-b-1-3.gml", "gebaeude": 206}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-b-1-4.gml", "gebaeude": 2}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-b-2-1.gml", "gebaeude": 2441}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-b-2-2.gml", "gebaeude": 968}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-b-2-3.gml", "gebaeude": 644}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-76-B-b-2-4.gml", "gebaeude": 185}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-77-A-a-1-1.gml", "gebaeude": 122}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-77-A-a-1-2.gml", "gebaeude": 25}, {"datei": "lod2_1261_gml.zip:Modele_3D/1261_M-34-77-A-a-1-3.gml", "gebaeude": 8}], "gebaeude": 82881, "ohne_kennung": 0, "ohne_hoehe": 0, "doppelt": 0, "measuredHeight": 0, "z_spanne": 82881, "unplausibel": 0}

## Stadt (Kurzfassung, vollständig in `daten/gebaeude_kennzahlen.js`)

- Gebäude 90563, Wohngebäude 61199 (Einfamilien 46817, Mehrfamilien 13739, sonst 643)
- Geschosse bekannt bei 90366; Median 2.0, Mittel 2.2
- Grundfläche 23078948 m² von 326859586 m², Bebauungsdichte 7.1 %
