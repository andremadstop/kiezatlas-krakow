# Vorschläge des Pakets Klima: Versiegelung und Grün

Stand 13.11.2026. Vorschläge ohne Nummer; die Belegschicht vergibt bei Übernahme die nächste freie `KR<n>`.
Grundlage: `pruefen/dk_protokoll.md` (vor dem ersten Lauf festgelegt), Zählungen in `belege/dk_klimat.md`,
Quellen in `quellen-dk.md`.

## 1. Bebauung + Verkehr als Näherung für Versiegelung, mit Abzeichen „orientacyjnie“

- **Anlass:** Eine gemessene Versiegelung liegt für Kraków nicht frei und geprüft vor; die BDOT10k-Bodenbedeckung
  schon.
- **Vorschlag:** `bebauung_verkehr` = `PTZB` + `PTKM` + `PTPL` als Anteil der Klassenflächen, immer mit Abzeichen
  `orientierung` („orientacyjnie“), nie als Messung bezeichnet. Der Beleg nennt die Teilfläche von `PTZB` mit Bewuchs
  (`ROSLINNOSC` = trawa, drzewa), damit Leser die Größe des Fehlers einschätzen können.
- **Begründung:** `PTZB` enthält Höfe und Gärten innerhalb bebauter Flächen, `PTPL` auch unbefestigte Plätze. Die
  Richtung des Fehlers ist bekannt (eher zu hoch), seine Größe nicht gemessen.
- **Verworfen:** (a) Copernicus Imperviousness: Lizenz und Bezugsweg nicht geprüft, als Raster (Auflösung nach Wissen 10 m, nicht geprüft) gröber als die
  BDOT10k. (b) Bebauung allein ohne Verkehr: Straßen und Gleise sind meist versiegelt, ohne sie wäre die Näherung
  systematisch zu niedrig.
- **Neu prüfen, wenn** eine gemessene Versiegelung mit klarer Lizenz vorliegt; dann als Gegenprobe je dzielnica.

## 2. Acker zählt nicht als Grün; Grün je Einwohner = Grün + Wald

- **Vorschlag:** `PTTR` mit `RODZAJ = uprawa na gruntach ornych` wird eigene Klasse `acker`. `gruen_wald` = `gruen` +
  `wald` ist die Grundlage für Grün je Einwohner, nur ab 1 000 Einwohnern und nicht je 1-km-Zelle. Solange die
  Einwohner Beispieldaten sind, rechnet nur die Beispieldatei `klimat_stadtteile_odbl.js` mit ihnen (Protokoll Regel 8,
  Ergänzung, Commit 977c7d3); der Stadtwert in `klimat.js` bleibt `null` mit Grund, damit diese Datei echt bleibt.
- **Begründung:** Acker ist nicht allgemein zugänglich und liegt einen Teil des Jahres ohne Bewuchs. Kraków hat laut
  Beleg 3 649,6 ha Acker (11,2 % der Klassenflächen); als Grün gezählt, wäre der Grünanteil der Stadt um diesen
  Betrag höher, besonders in Nowa Huta (20,5 % Acker). Kleingärten (`ogródki działkowe`) zählen dagegen als Grün.
- **Verworfen:** Grün je Einwohner je Zelle: Zellen mischen Wald und Wohnen, der Wert hätte keine Aussage.

## 3. Werte je dzielnica nur in `klimat_stadtteile_odbl.js`

- **Vorschlag:** Stadt, Delegaturen und Zellen (nur BDOT10k) in `klimat.js` und `klimat_zellen.js`; alles je dzielnica
  in einer eigenen `_odbl`-Datei.
- **Begründung:** Die Grenzen der dzielnice kommen aus OpenStreetMap (KR3). Ob daraus abgeleitete Flächenanteile unter
  die ODbL fallen, ist nicht geklärt; die vorsichtige Lesart trennt sie. So bleiben die übrigen Dateien frei nach
  art. 40c ust. 3 (nur Quellenangabe).
- **Neu prüfen, wenn** die Frage zur ODbL abgeleiteter Kennzahlen (KR3) entschieden ist oder die dzielnice aus einer
  amtlichen Quelle (PRG, MSIP nach Lizenzklärung) kommen.

## 4. Hitze als Grenze, nicht im Paket

- **Vorschlag:** Keine Oberflächentemperatur in dieser Ausgabe; auf der Seite steht die Grenze (`klimat.grenze.hitze`).
- **Begründung:** eigenes Messverfahren mit eigenem Protokoll, grobe Thermalauflösung, Lizenz und Bezugsweg ohne
  Anmeldung nicht geprüft (Einzelheiten `quellen-dk.md`, Abschnitt 4). Ein Netzabruf zur Prüfung lag außerhalb
  des vertretbaren Aufwands dieses Laufs.
- **Neu prüfen, wenn** eine Quelle mit wörtlich belegter offener Lizenz und Abruf ohne Anmeldung gefunden ist; dann
  als eigenes Paket mit Protokoll vor dem Lauf.

## 5. Regel 7 für dzielnice (Ergänzung des Protokolls, Commit bd5e851)

- **Anlass:** Die Beispielgrenzen von dzielnica 17 und 18 liegen außerhalb der Stadt (0,0 ha).
- **Vorschlag:** Mit Beispielgrenzen: Anteile `null` mit `anteil_grund = bezugsflaeche_zu_klein`. Mit echten Grenzen:
  jede dzielnica unter 10 ha in der Stadt ist ein Befund (kleinste dzielnica im BIP-Abzug 369,90 ha).
- **Verworfen:** stilles `null` auch bei echten Grenzen: Eine kaputte Geometrie fiele dann nicht auf.

## 6. Aufnahme in `pruefen.sh` (nicht im Paket geändert)

- **Vorschlag:** Die Integration ergänzt nach „Datenverträge und Summen“:

  ```sh
  pruef "Klima: Daten gegen Protokoll, ohne Rohdaten (pruefen/dk_klimat.py)" py pruefen/dk_klimat.py
  if [ -f "$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip" ]; then
    pruef "Klima aktuell (skripte/35_klimat.py --pruefen)" py skripte/35_klimat.py --pruefen
  else
    ueberspringe "Klima aktuell (skripte/35_klimat.py --pruefen)" "BDOT10k 1261 nicht unter \$KIEZ_DATEN"
  fi
  ```

  `35_klimat.py --pruefen` braucht rund 10 s und die BDOT10k-Datei, `dk_klimat.py` unter 1 s und nichts außer dem
  Repo. Heute laufen beide nur von Hand; beide sind am Paketende grün.
- **Folge für andere Pakete:** Ändert D2 `daten/stadtteile_odbl.js` oder D4 `daten/kennzahlen.json`, wird
  `35_klimat.py --pruefen` rot, bis `skripte/35_klimat.py` neu gelaufen ist. Das ist gewollt (die Klima-Werte je
  dzielnica hängen davon ab); die Integration lässt das Skript nach jedem solchen Merge laufen.

## 7. Einträge in gemeinsame Dateien (Vorschlag)

- **`QUELLEN.md`:** Zeile aus `quellen-dk.md`, Abschnitt 5.
- **`daten/LIZENZ.md`:**

  | Datei | Inhalt | Lizenz |
  |---|---|---|
  | `klimat.js`, `klimat_zellen.js` | Bodenbedeckung je Stadt, Delegatur und 1-km-Zelle aus BDOT10k | keine Lizenz (art. 40c ust. 5 Prawo geodezyjne i kartograficzne), Quellenangabe: Źródło: GUGiK, BDOT10k |
  | `klimat_stadtteile_odbl.js` | Bodenbedeckung je dzielnica (BDOT10k in OSM-Grenzen); Beispieldaten, solange Grenzen oder Einwohner Beispieldaten sind | ODbL 1.0 (vorsichtige Lesart, KR3), dazu Quellenangabe GUGiK |

- **`config/krakow.yaml`, `quellen`:** ein Eintrag `bdot10k` mit Vermerk `Źródło: GUGiK, BDOT10k (art. 40c ust. 3
  ustawy Prawo geodezyjne i kartograficzne)` und der Adresse aus `quellen-dk.md`. Heute steht der Vermerk als
  Konstante `QUELLE` in `skripte/35_klimat.py`; nach Aufnahme in die Ortskonfiguration liest das Skript ihn von dort.
- **`belege/README.md`:** `belege/dk_klimat.md` unter den Paketbelegen (`<paket>_*.md`, schon durch das Muster abgedeckt;
  `pruefen/belege.py` ist grün).
- **Texte:** `docs/entscheidungen/dk/texte/<lang>/klimat.js` (23 Schlüssel je Sprache) wandert nach
  `texte/<lang>/klimat.js`, sobald die Klima-Seite (Phase Seitenbau) die Schlüssel nutzt. Vorher meldete `pruefen/texte.py`
  sie als unbenutzt (Regel 6 der Textprüfung).

## 8. Eigentum (für die Tabelle in `docs/rundgang.md`)

| Datei | Eigentümer |
|---|---|
| `skripte/35_klimat.py` | Paket Klima |
| `pruefen/dk_klimat.py`, `pruefen/dk_protokoll.md` | Paket Klima |
| `daten/klimat.js`, `daten/klimat_zellen.js`, `daten/klimat_stadtteile_odbl.js` | Paket Klima (erzeugt von `35_klimat.py`) |
| `daten/schema/klimat.json`, `daten/schema/klimat_zellen.json`, `daten/schema/klimat_stadtteile_odbl.json` | Paket Klima (Datenvertrag; Änderung nach Einfrieren über die Integration) |
| `belege/dk_klimat.md` | Paket Klima (erzeugt) |
| `quellen-dk.md`, `docs/entscheidungen/dk.md`, `docs/entscheidungen/dk/texte/*` | Paket Klima, bis die Belegschicht übernimmt |
| `texte/<lang>/klimat.js` (später) | Paket der Klima-Seite (Namensraum `klimat.*` laut `daten/schema/texte.md`) |
