# Quellen Paket Klima: Versiegelung und Grün

Stand 13.11.2026. Vorschlag zur Übernahme in `QUELLEN.md` durch die Belegschicht (Zeilenvorschlag am Ende).
Regeln und Schwellen: `pruefen/dk_protokoll.md`; Zählungen: `belege/dk_klimat.md`.

## 1. BDOT10k, Paket Powiat 1261 (verwendet)

| Feld | Angabe |
|---|---|
| Nutzer im Atlas | `daten/klimat.js`, `daten/klimat_zellen.js`, `daten/klimat_stadtteile_odbl.js` (Bodenbedeckung `OT_PT??_A`, Stadtgrenze und Delegaturen `OT_ADJA_A`) |
| Adresse | `https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip` |
| Weg | A (Abruf der Machbarkeitsprobe, 13.11.2026 09:22 UTC, Herkunft in `$KIEZ_DATEN/2026-11-13/03_gebaeude/HERKUNFT.md`; robots.txt 404, also keine Regeln; ob dabei schon `skripte/abruf.py` lief, nicht geprüft) |
| Datei | `$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip`, 32 403 983 Bytes, SHA256 `68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d` |
| Stand | Dateien im Zip vom 2026-10-03 (`belege/dk_klimat.md`) |
| Lizenz | keine Lizenz, freie Nutzung mit Quellenangabe (Fundstellen unten) |
| Vermerk (Original) | `Źródło: GUGiK, BDOT10k (art. 40c ust. 3 ustawy Prawo geodezyjne i kartograficzne)` (so in den Daten unter `quelle.vermerk`) |

**Fundstellen, wörtlich.** Gesetzestext: Prawo geodezyjne i kartograficzne, tekst jednolity Dz.U. 2026 poz. 1389
(`$KIEZ_DATEN/2026-11-13/03_gebaeude/pgik_DU_2026_1389.pdf`, von `https://api.sejm.gov.pl/eli/acts/DU/2026/1389/text.pdf`,
SHA256 `f7b4ac608d0737a50bf59729d04ea7100f9e64728affcf3fd7582cbfcfaa0c24`):

- art. 40a ust. 2: „Nie pobiera się opłaty za: 1) udostępnianie zbiorów danych: … h) obiektów topograficznych o
  szczegółowości zapewniającej tworzenie standardowych opracowań kartograficznych w skalach 1:10 000–1:100 000,“
- art. 40c ust. 3: „Podmioty, które wykorzystują materiały zasobu, zamieszczają w publikowanych opracowaniach
  informacje o źródle pochodzenia użytego materiału.“
- art. 40c ust. 5: „Licencji nie wydaje się w przypadku udostępnienia materiałów zasobu w związku ze zgłoszeniem prac
  lub jego uzupełnieniem oraz w przypadku udostępnienia materiałów zasobu, o których mowa w art. 40a ust. 2 pkt 1 i 3.“

Geoportal, Seite zur BDOT10k (`$KIEZ_DATEN/2026-11-13/03_gebaeude/geoportal_bdot10k.html`, von
`https://www.geoportal.gov.pl/pl/dane/baza-danych-obiektow-topograficznych-bdot10k/`, SHA256
`58fe5cf154ec9006845bce4d4227513f630022b439643e5113efe114496840e4`): „Baza BDOT10k jest dostępna bezpłatnie i możliwa do
dowolnego wykorzystania“ und „uwolnienie danych BDOT10k powoduje, że dzisiaj każdy może w łatwy sposób wykorzystywać te
dane do dowolnych celów“.

**Lesart.** Lit. h deckt die BDOT10k (Maßstab 1:10 000). Die freie Nutzung folgt aus dem Geoportal-Satz; das Gesetz
selbst sagt nur, dass keine Gebühr anfällt und keine Lizenz erteilt wird. Das ist dieselbe Lesart wie im
Machbarkeitsbericht (offene Lizenzfrage 4); Pflicht ist allein die Quellenangabe. Kein Widerspruch zwischen den
Fundstellen, daher kein STOPP.

## 2. BIP Miasta Krakowa, Fläche der Stadt (nur Gegenprobe, nicht veröffentlicht)

| Feld | Angabe |
|---|---|
| Nutzer | nur `skripte/35_klimat.py`, Regel 6 (Gegenprobe Stadtfläche) |
| Adresse | `https://www.bip.krakow.pl/?dok_id=242410` |
| Datei | `$KIEZ_DATEN/2026-11-13/10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html`, SHA256 `297b2944c3b24eba2e61abeec85c9e0a0ab704fb6d5c7936f7268c7e20095c69` |
| Lizenz | keine Lizenzangabe gefunden (Machbarkeitsbericht, offene Lizenzfrage 3) |
| Folge | Keine Zahl daraus steht in `daten/`. Zitiert werden nur Prüfwerte: die Summe „RAZEM“ (32 683,90 ha) in `belege/dk_klimat.md` und `pruefen/dk_protokoll.md` (Regel 6) sowie die kleinste dzielnica (369,90 ha, Zeile XVI) in `pruefen/dk_protokoll.md` (Regel 7) und `docs/entscheidungen/dk.md` (Begründung der 10-ha-Schwelle). |

## 3. Eingaben aus anderen Paketen

Dieses Paket braucht **keine Datei aus `$KIEZ_DATEN/eingang/`** und keinen Handdownload. Seine weiteren Eingaben
kommen aus dem Repo:

| Datei | Paket | Erwartung |
|---|---|---|
| `daten/stadtteile_odbl.js` | Gliederung und Bevölkerung (D2) | FeatureCollection, je Feature `properties.nr` (zweistellig wie in `config/krakow.yaml`) und `name`, Geometrie in WGS 84; `fixture: true`, solange Beispieldaten |
| `daten/kennzahlen.json` | Gliederung und Bevölkerung (D4) | `stadt.kacheln[]` und `stadtteile.<nr>.kacheln[]` mit einer Kachel `id = "einwohner"` und Zahl in `wert`; `fixture: true`, solange Beispieldaten |

Bis dahin rechnet `klimat_stadtteile_odbl.js` (Beispieldaten) Grün je Einwohner mit den Beispieleinwohnern
(Regel 8, Ergänzung); der Stadtwert in `klimat.js` bleibt `null`. Sobald beide echt sind, `skripte/35_klimat.py` neu
laufen lassen; Grün je Einwohner und die Werte je dzielnica werden dann echt (Regeln 5, 8, 9 des Protokolls), die Summenprüfung Σ dzielnice = Stadt wird scharf (0,5 %), und eine
dzielnica unter 10 ha ist dann ein Befund.

## 4. Geprüft und nicht verwendet

- **Geländemodell (NMT) und Orthofoto:** frei nach art. 40a ust. 2 pkt 1 lit. d und e (Wortlaut oben im Gesetz). Für
  Flächenanteile nicht nötig, deshalb nicht geladen. Ein NMT bräuchte man erst für Abfluss oder Kaltluft.
- **Oberflächentemperatur (Hitze):** nicht berechnet. Gründe, die ohne Netzabruf feststehen:
  1. Eine Hitzekarte aus Satellitendaten ist ein eigenes Messverfahren: Szenenwahl (wolkenfreie Sommertage),
     Emissivität je Bodenbedeckung, Umrechnung von Strahlungs- in Oberflächentemperatur und die Aussage
     „Oberfläche, nicht Lufttemperatur“. Dafür bräuchte es ein eigenes Protokoll vor dem Lauf.
  2. Thermalkanäle haben eine grobe Auflösung (Landsat-Thermal liegt nach Wissen bei rund 100 m, nicht geprüft),
     also gröber als die Bodenbedeckung der BDOT10k; je dzielnica wäre das tragfähig, je Block nicht.
  3. Lizenz und Bezugsweg sind für dieses Paket **nicht geprüft**: Landsat (USGS) und Copernicus (Sentinel-3 SLSTR) gelten nach Wissen als offen; ob ein
     Bezug ohne Anmeldung und über `skripte/abruf.py` möglich ist, und der genaue Lizenzwortlaut, sind offen.
  Folge: als Grenze benannt (Text `klimat.grenze.hitze` im Vorschlag `docs/entscheidungen/dk/texte/`).
- **Gemessene Versiegelung** (z. B. Copernicus High Resolution Layer Imperviousness) und **Baumkronen** (GUGiK „Modele
  3D drzew“): nicht geprüft. Bebauung + Verkehr bleibt eine Näherung (Abzeichen „orientacyjnie“).
- **MSIP Kraków** („Kierunki Rozwoju i Zarządzania Terenami Zieleni 2017–2030“, „Potencjał solarny“): Lizenz-STOPP laut
  Machbarkeitsbericht, nicht verwendet.

## 5. Zeilenvorschlag für `QUELLEN.md`

| Quelle | Nutzer | Adresse | Lizenz | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| BDOT10k, Powiat 1261 (GUGiK) | Klima (`klimat*.js`) | `https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip` | keine Lizenz (art. 40c ust. 5), frei mit Quellenangabe (art. 40c ust. 3; Geoportal „możliwa do dowolnego wykorzystania“) | Źródło: GUGiK, BDOT10k (art. 40c ust. 3 ustawy Prawo geodezyjne i kartograficzne) | A | 2026-10-03 |
