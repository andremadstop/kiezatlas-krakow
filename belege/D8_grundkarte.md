# Beleg Grundkarte Kraków (Paket Grundkarte)

Stand 13.11.2026, Zweig `Arbeitszweig d8`. Regeln und Prüfplan: `pruefen/D8_protokoll.md` (vor dem ersten Lauf festgelegt,
Änderungen danach dort unten). Quellen und Lizenz: `quellen-D8.md`. Entscheidungen: `docs/entscheidungen/D8.md`.
Alle Zahlen unten stammen aus `lauf.json` des maßgeblichen Laufs oder aus den genannten Befehlen; nichts ist
geschätzt.

**Datenstand: echt.** Eingabe ist die BDOT10k-Lieferung Powiat 1261 (Miasto Kraków), keine Beispieldaten.

## 1. Lauf

| Angabe | Wert |
|---|---|
| Skript | `skripte/27_grundkarte.py`, Stand Commit `3753299` |
| Aufruf | `systemd-run --user --scope -p MemoryMax=8G uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt python -I skripte/27_grundkarte.py` |
| Eingabe | `kiezatlas-daten/krakow/2026-11-13/03_gebaeude/1261_SHP.zip`, 32.403.983 B, SHA256 `68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d` (G1) |
| Stand der Quelle | Datum im Kopf aller 13 gelesenen DBF-Dateien: 2026-10-03 (nur dieses eine Datum) |
| Koordinatensystem der Quelle | aus den `.prj`: „ETRF2000-PL / CS92“, in allen gelesenen Schichten gleich (G2) |
| Ziel | EPSG:3857, Kacheln z9 bis z14, Ausdehnung 4096, Puffer 64 Einheiten |
| Ausgabe | `kiezatlas-daten/krakow/abgeleitet/grundkarte/68b6ff47ed37/` (außerhalb des Repos) und `daten/grundkarte.js` |
| Laufzeit | 24,0 s (`lauf.json`, `sekunden`) |
| Manifest | `MANIFEST.sha256` mit 396 Zeilen, SHA256 der Manifestdatei `8244af19141d476ec01dca4bd0f922a9fb2fd1613507cca2003249661a79a27e` |
| Reproduzierbar (G10) | `skripte/27_grundkarte.py --pruefen` rechnet in einen Wegwerf-Ordner: „ok Kacheln und Schrift byte-gleich (396 Dateien)“, „ok daten/grundkarte.js gleich“ |

## 2. Zählungen je Schritt

### Gelesen und übernommen je BDOT10k-Schicht

| BDOT10k-Schicht | gelesen | übernommen | Kartenschicht | Filter |
|---|---:|---:|---|---|
| PTWP_A (Wasserflächen) | 342 | 342 | woda | – |
| PTLZ_A (Wald, Gehölz) | 1.946 | 1.946 | zielen | – |
| PTRK_A (Gebüsch) | 68 | 68 | zielen | – |
| PTTR_A (Gras, Acker) | 5.555 | 5.555 | zielen | – |
| PTUT_A (Dauerkulturen) | 1.174 | 1.174 | zielen | – |
| PTZB_A (Bebauungsflächen) | 11.546 | 11.546 | teren | – |
| PTKM_A (Verkehrsflächen) | 117 | 117 | teren | – |
| PTPL_A (Plätze) | 1.413 | 1.413 | teren | – |
| SWRS_L (Fließgewässer) | 1.143 | 1.143 | cieki | – |
| SKTR_L (Gleise) | 4.343 | 4.343 | tory | – |
| SKJZ_L (Fahrbahnen) | 33.585 | 33.564 | drogi | nur `KAT_ISTNIE = eksploatowany` und bekannte `KLASA_DROG`; 21 weggelassen |
| SKRP_L (Fuß- und Radwege) | 21.893 | 21.893 | sciezki | – |
| ADMS_P (Ortsnamen) | 102 | 102 | miejsca | – |

### Linien gleicher Klasse und gleichen Namens verbunden

| Kartenschicht | vorher | nachher |
|---|---:|---:|
| drogi | 33.564 | 19.812 |
| cieki | 1.143 | 691 |
| tory | 4.343 | 3.947 |
| sciezki | 21.893 | 20.199 |

### Objekte je Zoomstufe (nach Ab-Zoom, Vereinfachung um 1 Kacheleinheit, Mindestgröße)

| Zoom | teren | zielen | woda | cieki | tory | sciezki | drogi | miejsca |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 9 | 0 | 1.467 | 92 | 0 | 0 | 0 | 315 | 1 |
| 10 | 0 | 1.926 | 183 | 0 | 0 | 0 | 571 | 1 |
| 11 | 11.514 | 8.684 | 304 | 32 | 1.371 | 0 | 1.345 | 1 |
| 12 | 11.651 | 8.715 | 338 | 33 | 1.391 | 0 | 2.271 | 102 |
| 13 | 13.071 | 8.732 | 342 | 689 | 3.941 | 0 | 4.195 | 102 |
| 14 | 13.074 | 8.739 | 342 | 690 | 3.941 | 20.168 | 19.799 | 102 |

### Kacheln je Zoomstufe (Größe des Kachelsatzes)

| Zoom | Kacheln | davon leer | Bytes | größte Kachel (B) |
|---|---:|---:|---:|---:|
| 9 | 1 | 0 | 48.879 | 48.879 |
| 10 | 4 | 0 | 84.481 | 46.760 |
| 11 | 8 | 1 | 720.996 | 310.146 |
| 12 | 24 | 7 | 921.954 | 133.327 |
| 13 | 77 | 24 | 1.407.069 | 66.211 |
| 14 | 273 | 97 | 2.818.697 | 46.779 |
| **gesamt** | **387** | **129** | **6.002.076** | 310.146 (z11) |

Leer heißt: Kachel im Rahmen `karte.rahmen` = [19.79, 49.96, 20.22, 50.13], aber außerhalb des Stadtgebiets
(0 Byte, damit der Browser keine 404 sieht).

### Kartenschrift (SDF-Glyphen, MapLibre-Format)

| Schriftstapel | 0–255 | 256–511 | 8192–8447 | zusammen |
|---|---:|---:|---:|---:|
| Noto Sans Regular | 192 | 256 | 180 | 628 |
| Noto Sans Medium | 192 | 256 | 180 | 628 |
| Noto Sans Italic | 192 | 256 | 183 | 631 |

9 Glyphen-Dateien, 952.423 B; dazu `schrift/OFL.txt` 4.579 B.

### Gesamtgröße

| Teil | Dateien | Bytes | gzip (Stufe 6, je Datei) |
|---|---:|---:|---:|
| Kacheln | 387 | 6.002.076 | 4.565.660 |
| Kacheln + Glyphen (`lauf.json`, `gesamt`) | 396 | 6.954.499 | 4.927.736 |

## 3. Straßennamen

Gezählt mit den Lesern des Skripts über SKJZ_L (nur übernommene Abschnitte, 33.564):

| Merkmal `ULI_CECHA` | Abschnitte mit Name | davon Merkmal schon ausgeschrieben im Namen |
|---|---:|---:|
| ul. | 15.820 | (Merkmal wird nie gezeigt) |
| al. | 654 | 654 |
| rondo | 112 | 112 |
| pl. | 76 | 75 |
| inne | 61 | (Merkmal wird nie gezeigt) |
| rynek | 24 | 23 |
| os. | 8 | 8 |
| bulw. | 2 | 2 |
| skwer | 2 | 2 |
| ohne Namen | 16.805 | – |

Bei den 876 Abschnitten der rechten Spalte setzt das Skript das Merkmal nicht davor (vorher: „al. Aleja Adama
Mickiewicza“). Namen sonst unverändert aus der Quelle (UTF-8 laut `.cpg`).

## 4. Prüfung `pruefen/D8_grundkarte.py` (G1, G3 bis G9, G11, G12)

Gegen den maßgeblichen Lauf: **0 Befunde**. Auszug:

- G1: 396 Dateien im Manifest, Prüfsummen stimmen, keine Datei außerhalb; Eingabe-SHA = `BDOT_SHA256`.
- G4: z9 1, z10 4, z11 8, z12 24, z13 77, z14 273 Kacheln, je gleich der Zahl, die der Rahmen verlangt.
- G3: 387 Kacheln mit eigenem Dekoder gelesen, gültiges MVT 2.1 (Version 2, Ausdehnung 4096, nur MoveTo/LineTo/
  ClosePath, erster Ring jedes Polygons positiv, kein Ring mit Fläche 0).
- G5: keine Kachel über 500 KB (größte 310.146 B).
- G6: Schichten nur cieki, drogi, miejsca, sciezki, teren, tory, woda, zielen; Attribute nur k, nazwa, most.
- G7: Straßenname mit polnischem Sonderzeichen in den Kacheln gefunden (erster Treffer „Krzyżówka“).
- G8: alle drei Stapel mit allen 18 polnischen Sonderzeichen als eigene, verschiedene Glyphen.
- G9: Zeichen aus den Namen vorhanden: Regular 77 (drogi), Medium 52 (miejsca), Italic 42 (cieki).
- G11/G12: `daten/grundkarte.js` ohne OpenStreetMap/ODbL, Vermerk nennt BDOT10k und den GUGiK, Pfade relativ; jede
  der 11 Stilebenen verweist auf eine vorhandene Quellschicht, jeder Schriftstapel ist vorhanden; `schrift/OFL.txt`
  vorhanden.
- `pruefen/daten.py`: „ok grundkarte.js: Vertrag grundkarte.json“.

**Gegenprobe der Prüfung** (Kopie des Kachelordners, eine z14-Kachel gelöscht, die größte z13-Kachel auf 1.000 B
abgeschnitten): Rückgabe 1 mit 3 Befunden: Manifest falsch für `kacheln/13/4549/2776.pbf` und
`kacheln/14/9092/5547.pbf`; „z14: 272 Kacheln, Rahmen verlangt 273 (fehlen 1)“; „G3 … 13/4549/2776: abgeschnittenes
Feld“. (Der erste Versuch stürzte an der fehlenden Datei ab; behoben in `607bf62`.)

## 5. Sichtprobe G13 (`node skripte/27_grundkarte_vorschau.mjs`)

Chromium (Playwright aus `node_modules`), MapLibre 4.7.1 aus `vendor/`, eigener Server auf 127.0.0.1, jeder
Abruf außerhalb 127.0.0.1 wird abgebrochen. Ergebnis: **0 Befunde**, Laufzeit 6,5 s.

| Ansicht | gezeichnete Objekte je Schicht (queryRenderedFeatures, Kachelteile zählen einzeln) | Beschriftungen | davon mit poln. Sonderzeichen |
|---|---|---:|---:|
| `stadt_z11` | drogi 1318, tory 1290, cieki 31, woda 12, zielen 36, teren 30 | 0 | 0 |
| `altstadt_z14` | miejsca 11, drogi 1310, tory 163, sciezki 1051, cieki 3, woda 6, zielen 17, teren 41 | 88 | 38 |
| `kazimierz_z16` (Überzoom) | miejsca 1, drogi 141, tory 29, sciezki 65, zielen 5, teren 11 | 29 | 11 |
| `en_altstadt_z14` (Seite in `en/`) | wie `altstadt_z14` | 88 | 38 |

Bildzeile auf der Karte: „Podkład: BDOT10k, Główny Urząd Geodezji i Kartografii (stan plików 2026-10-03),
opracowanie własne“. Keine MapLibre-Fehler, keine Konsolenfehler, keine fehlgeschlagenen Abrufe, kein Abruf außerhalb
127.0.0.1. Bildschirmfotos: `belege/D8_vorschau/*.png` (zwei Läufe ergaben byte-gleiche Bilder; das Bild aus `en/` war
byte-gleich mit `altstadt_z14.png` und wird darum nicht mehr abgelegt).

**Einschränkung:** Die Vorschau macht Kachel- und Schrift-URL absolut (MapLibre 4.7.1 löst relative URLs im Worker
nicht auf, gemessen: „Failed to parse URL from daten/grundkarte/kacheln/11/1137/694.pbf“). `themen.js` tut das heute
nicht; bis die Integration den Vorschlag aus `docs/entscheidungen/D8.md` übernimmt, zeigen die Atlas-Seiten die
Grundkarte nicht. Ob MapLibre eine relative Schrift-URL allein auflösen würde, ist nicht einzeln geprüft (die
Vorschau macht beide absolut).

Erster Versuch der Sichtprobe (Stand `5d44ce9`): MapLibre lehnte drei Linienbreiten des Stils ab (zoom nicht im
obersten `interpolate`); behoben in `607bf62`.

## 6. Werkzeugprüfung

Befehle am 13.11.2026: `command -v tippecanoe planetiler ogr2ogr ogrinfo pmtiles` → keiner gefunden;
`pacman -Qs 'gdal|tippecanoe'` → keine Treffer; `java -version` → „openjdk version "27" 2026-09-15“ (planetiler nicht
vorhanden). In `node_modules` liegen `geojson-vt`, `vt-pbf`, `pbf` nur als Unterabhängigkeiten von MapLibre. Darum
eigener Kodierer (Begründung `docs/entscheidungen/D8.md`).

## 7. Farben gegen DESIGN.md

| Stil | Wert | DESIGN.md |
|---|---|---|
| Papier (Halo der Schrift, Hintergrund der Vorschau) | `#f1f2ee` | ground |
| Ortsnamen | `#13212a` | ink |
| Straßennamen | `#4f5d64` | muted |
| Straßenkontur, Fußwege | `#cdd1cc` | line |
| Gewässernamen | `#3b7684` | vierte Stufe der Klassenfarben „Wasser bis Tiefe“ |
| Wasserflächen und -linien `#cddde1`; Grün `#d6e1d3 #dbe5d8 #dfe7dc #e2eadf #eceee6`; Bebauung `#e4e5e1 #e6e6e2 #e8e9e4 #ebebe7`; Gleise `#b4babc`; Straßen `#d9dcd7`/`#ffffff` | – | **keine Token**; eigene, sehr helle Töne nahe ground, damit die Themenfarben darüber tragen. Abweichung bewusst, kein Orange |

## 8. Grenzen (nicht geprüft oder nicht abgedeckt)

- **Außerhalb von Powiat 1261 bleibt die Karte leer** (129 leere Kacheln im Rahmen, siehe Bild `stadt_z11.png`).
- Lagegenauigkeit der BDOT10k-Geometrie: übernommen wie geliefert (Maßstab 1:10 000), nicht geprüft.
- Vollständigkeit der Straßennamen gegen TERYT ULIC: nicht geprüft. 16.805 übernommene Fahrbahnabschnitte haben
  in BDOT10k keinen Namen.
- Darstellung nur in Chromium (Playwright) geprüft, nicht in Firefox oder Safari, nicht auf einem echten Handy.
- Atlas-Seiten nicht geprüft: Sie binden die Karte erst in Phase Seitenbau ein; Voraussetzungen in
  `docs/entscheidungen/D8.md` (`themen.js`, `karte.grundkarte`, Deploy der Kacheln).
- Ladezeit über das Netz: nicht gemessen (nur Größen oben).
- Ob die Glyphen-PBF als „Modified Version“ im Sinn der OFL gelten: nicht rechtlich geprüft; `OFL.txt` geht
  vorsorglich mit, ein Reserved Font Name steht im Copyright-Eintrag von Noto Sans nicht.
- Die mitgelieferten Barlow-Schriften unter `fonts/` haben 16 der 18 polnischen Sonderzeichen nicht (gemessen, nur
  ó/Ó vorhanden); betrifft nicht die Kartenschrift, aber die Oberfläche (Hinweis in `docs/entscheidungen/D8.md`).
