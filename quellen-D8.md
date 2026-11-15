# Quellen Paket Grundkarte (D8)

Stand 13.11.2026. Vorlage für `QUELLEN.md` (Übernahme durch die Belegschicht). Weg: A = Abruf über
`skripte/abruf.py`, H = Handdownload durch den Betreiber, L = lokal installiert. Wörtliche Vermerke in Originalsprache.
Zählungen und Größen: `belege/D8_grundkarte.md`.

## Quellen

| Quelle | Nutzer | Adresse | Lizenz | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| BDOT10k (Baza Danych Obiektów Topograficznych), Paket Powiat 1261 Miasto Kraków, Schema 2021, Shapefile; Główny Urząd Geodezji i Kartografii (GUGiK) | Kacheln unter `daten/grundkarte/kacheln/`, Stil `daten/grundkarte.js` | https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip | keine Lizenz vorgesehen (art. 40c ust. 5), kostenfrei (art. 40a ust. 2 pkt 1 lit. h), Quellenangabe Pflicht (art. 40c ust. 3) Prawo geodezyjne i kartograficzne, Dz.U. 2026 poz. 1389 | `Podkład: BDOT10k, Główny Urząd Geodezji i Kartografii (stan plików 2026-10-03), opracowanie własne` (Wortlaut eigener Vorschlag; das Gesetz schreibt keinen vor) | A (geladen vor diesem Paket, `kiezatlas-daten/krakow/2026-11-13/03_gebaeude/HERKUNFT.md`) | Dateien vom 03.10.2026 (Datum im Kopf jeder DBF), Abruf 13.11.2026 09:22 UTC, SHA256 `68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d` |
| Noto Sans Regular, Medium, Italic (The Noto Project Authors), Paket `noto-fonts 1:2026.10.01-1` | Kartenschrift unter `daten/grundkarte/schrift/` (SDF-Glyphen, abgeleitet) | `/usr/share/fonts/noto/NotoSans-{Regular,Medium,Italic}.ttf` | SIL Open Font License 1.1 | Eintrag 0 der name-Tabelle: „Copyright 2022 The Noto Project Authors (https://github.com/notofonts/latin-greek-cyrillic)“; Eintrag 13: „This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://scripts.sil.org/OFL“ | L | SHA256 je Datei in `skripte/27_grundkarte.py` (`SCHRIFTEN`) |

### Wörtliche Fundstellen BDOT10k

Aus `kiezatlas-daten/krakow/2026-11-13/03_gebaeude/pgik_DU_2026_1389.pdf` (Prawo geodezyjne i kartograficzne,
tekst jednolity Dz.U. 2026 poz. 1389), wiedergegeben nach `HERKUNFT.md` und dem Machbarkeitsbericht (Zeile 3):

- art. 40a ust. 2: „Nie pobiera się opłaty za: 1) udostępnianie zbiorów danych: … h) obiektów topograficznych o
  szczegółowości zapewniającej tworzenie standardowych opracowań kartograficznych w skalach 1:10 000–1:100 000“
- art. 40c ust. 5: „Licencji nie wydaje się … w przypadku udostępnienia materiałów zasobu, o których mowa w art. 40a
  ust. 2 pkt 1 i 3.“
- art. 40c ust. 3: „Podmioty, które wykorzystują materiały zasobu, zamieszczają w publikowanych opracowaniach
  informacje o źródle pochodzenia użytego materiału.“

Aus `kiezatlas-daten/krakow/2026-11-13/03_gebaeude/geoportal_bdot10k.html` (Abruf 13.11.2026 09:32 UTC):
„Baza BDOT10k jest dostępna bezpłatnie i możliwa do dowolnego wykorzystania.“

Gegenprobe in diesem Paket (13.11.2026, `pdftotext -layout` auf das PDF): art. 40a ust. 2 pkt 1 lit. h steht in
Zeile 1590 f. der Textfassung, art. 40c ust. 3 in Zeile 1680 f., art. 40c ust. 5 in Zeile 1684 f. (vollständig:
„Licencji nie wydaje się w przypadku udostępnienia materiałów zasobu w związku ze zgłoszeniem prac lub jego
uzupełnieniem oraz w przypadku udostępnienia materiałów zasobu, o których mowa w art. 40a ust. 2 pkt 1 i 3.“). Der
Satz der Geoportal-Seite steht wörtlich in `geoportal_bdot10k.html`.

### Nicht genutzt, mit Grund

| Quelle | Grund | Fundstelle |
|---|---|---|
| GUGiK WMTS „Mapa podkładowa BDOO i BDOT10k“ und Orthofoto-WMTS/WMS | nur EPSG:2180 (MapLibre braucht Web-Mercator); Vorrendern in Web-Mercator wäre „harvesting“ | Capabilities laut Machbarkeitsbericht Zeile 9: „Wykorzystanie usługi nie podlega żadnym ograniczeniom z wyłączeniem automatycznego pobierania i kolekcjonowania obrazów … (tzw. harvesting).“ Nicht angefasst. |
| OpenStreetMap (ODbL) | nicht nötig, BDOT10k reicht für Flächen, Linien und Namen im Stadtgebiet; OSM in der Grundkarte zöge die ODbL-Dateigrenze (`pruefen/daten.py` Punkt 4) in jede Seite mit Karte | – |
| basemap.de (Potsdamer Grundkarte) | deckt nur Deutschland ab | – |

## Eingang (Handdownload) — nicht nötig

Dieses Paket braucht keinen der ausstehenden Handdownloads. Das Skript liest die BDOT10k-Lieferung in dieser
Reihenfolge:

1. `kiezatlas-daten/krakow/eingang/bdot10k/1261_SHP.zip`
2. `kiezatlas-daten/krakow/2026-11-13/03_gebaeude/1261_SHP.zip` (liegt vor)

**Format:** ZIP der GUGiK wie unter der Adresse oben, Dateinamen `PL.PZGiK.283.BDOT10k.1261__OT_<SCHICHT>.{shp,shx,dbf,prj,cpg}`,
gelesen werden die Schichten PTWP_A, PTLZ_A, PTRK_A, PTTR_A, PTUT_A, PTZB_A, PTKM_A, PTPL_A, SWRS_L, SKTR_L, SKJZ_L,
SKRP_L, ADMS_P. Koordinatensystem aus der `.prj` jeder Schicht (alle gleich, sonst Abbruch), Zeichensatz aus der
`.cpg`.

**Neuer Stand:** Eine Datei mit anderer SHA256 als `BDOT_SHA256` im Skript führt zum **Abbruch** (Regel G1), auch
unter `eingang/`. Neuen Stand ablegen, `HERKUNFT.md` daneben schreiben, dann `BDOT_SHA256` im Skript ändern, Lauf und
Prüfung wiederholen, Beleg nachziehen.

Der OSM-Auszug Małopolska (ausstehender Handdownload) wird für die Grundkarte **nicht** gebraucht.
