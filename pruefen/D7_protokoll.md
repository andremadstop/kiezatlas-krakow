# Protokoll Paket Luft (D7): Festlegungen vor dem ersten Lauf

Stand 13.11.2026, festgelegt **bevor** ein Messwert abgerufen oder angesehen wurde (Belegstandard, Punkt 18). Bis
zu diesem Commit wurden nur Lizenz- und Metadatenseiten geladen (Liste in `belege/D7_luft.md`, Abschnitt 1) und die
Feldliste des EEA-Betrachters (`init`, enthält Filterwerte und Zeilenzahlen je Land, keine Messwerte von Kraków).
Änderungen an diesen Regeln nach dem Lauf nur als neuer Abschnitt „Abweichung“ mit Grund und Commit, nie still.

## 1. Quelle und Weg

- **Hauptweg (automatisch):** EEA „Air Quality e-Reporting: Air quality annual statistics calculated by the EEA“
  (Metadatensatz `6e191a3b-258d-491e-b636-6cbb15cf473b`), Tabelle `Airquality_Dissem.b2g.AirQualityStatistics`
  („Annual AQ statistics (AirBase & e-Reporting merged)“). Die Werte sind Messungen der polnischen Staatlichen
  Umweltüberwachung (GIOŚ), an die EEA gemeldet; die Jahreskennwerte hat die EEA aus den gemeldeten Zeitreihen
  berechnet. Abruf nur über `skripte/abruf.py`.
- **Gegenprobe (Handdownload, sobald da):** GIOŚ „Bank danych pomiarowych“, Jahresstatistiken, Ablage
  `$KIEZ_DATEN/eingang/gios/`. Der Rechner `powietrze.gios.gov.pl` war am 13.11.2026 automatisch nicht erreichbar
  (siehe `quellen-D7.md`). Die GIOŚ-Werte ersetzen die EEA-Werte nicht, sie prüfen sie.
- Abzeichen auf der Seite: **„orientacyjnie / Orientierung“**, nicht „standard urzędowy“. Grund: Die Jahreswerte
  sind von der EEA berechnet, nicht die amtliche Jahresbewertung der GIOŚ (ocena roczna).

## 2. Stationsauswahl

- **Stadt (`rola = "miasto"`):** alle Messstellen mit Feld `City` = „Kraków“ (Zuordnung der EEA nach Urban Audit).
  Ob diese Zuordnung genau der Gemeindegrenze entspricht: nicht geprüft, steht unter Grenzen.
- **Umland (`rola = "okolica"`):** Messstellen in Polen mit `City` ≠ „Kraków“ (oder leer), deren Koordinate höchstens
  **30 km** vom Mittelpunkt der Stadt-Messstellen liegt (arithmetisches Mittel von Länge und Breite aller
  Stadt-Messstellen, aus den Daten gerechnet, keine handgetippte Koordinate). Abstand nach Haversine,
  Erdradius 6371 km. 30 km ist eine Festlegung dieses Protokolls, kein Fachmaß.
- Stationstyp (Hintergrund, Verkehr, Industrie) und Gebietstyp werden mitgeführt und angezeigt, nicht gefiltert.

## 3. Schadstoffe, Kennwerte, Jahre

| Feld | Schadstoff | `DataAggregationProcess` | Einheit | Grenzwert laut Rozporządzenie (Dz.U. 2021 poz. 845, Załącznik nr 1) |
|---|---|---|---|---|
| `pm10_srednia` | PM10 | „Annual mean / 1 calendar year“ | µg/m³ | 40, rok kalendarzowy (Lp. 7) |
| `pm10_dni` | PM10 | „1 year day exceed 50“ | Tage | 50 µg/m³ je 24 godziny, dopuszczalnie 35 razy (Lp. 7) |
| `pm25_srednia` | PM2.5 | „Annual mean / 1 calendar year“ | µg/m³ | 25 (faza I, ab 2015), 20 (faza II, ab 2020) (Lp. 6) |
| `no2_srednia` | NO2 | „Annual mean / 1 calendar year“ | µg/m³ | 40, rok kalendarzowy (Lp. 2) |
| `no2_godziny` | NO2 | „1 year hour exceed 200“ | **Stunden** | 200 µg/m³ je jedna godzina, dopuszczalnie 18 razy (Lp. 2) |

- **Keine „PM2.5-Überschreitungstage“:** Die Verordnung kennt für PM2.5 nur einen Jahreswert. Das Feld entfällt,
  die Seite sagt das (Schlüssel `powietrze.pm25_bez_dni`). Bei NO2 sind es Stunden, nicht Tage.
- **Jahre:** 2010 bis 2025. 2026 (nur vorläufige Daten E2a) und früher als 2010 werden nicht verwendet.
- **Datenfluss:** nur „E1a/validated data AQ e-Reporting“ und „Reporting within EoI/AirBase 8“; „E2a/UTD“ (nicht
  validiert) wird gezählt und verworfen.

## 4. Qualitätsregeln

1. `DataCoverage` < 75 %: Wert verworfen (gezählt). Grund: Feldbeschreibung der EEA („If Data Coverage < 75% for
   averaging period of a year, annual statistics should not be included in air quality assessments“).
2. 75 % ≤ `DataCoverage` < 85 %: Wert bleibt, Kennzeichen `niepelne: true` (EEA: „< 85% … should not be included
   in compliance checks“). Ein solcher Wert zählt nie als Grenzwertüberschreitung im Text.
3. `potentialOutlier` = „Y“ (oder wahr): verworfen, gezählt.
4. Mehrere Messpunkte derselben Station, desselben Schadstoffs, Jahres und Kennwerts: der mit der höchsten
   `DataCoverage`; bei Gleichstand der lexikografisch kleinste `SamplingPoint`. Anzahl der Dubletten im Beleg.
5. Rundung erst bei der Anzeige; `daten/powietrze.js` trägt die Werte mit höchstens einer Nachkommastelle
   (Tage und Stunden ganzzahlig).

## 5. Vorher und Nachher

- **Stichtag:** 1. September 2019, Inkrafttreten der Uchwała Nr XVIII/243/16 Sejmiku Województwa Małopolskiego
  (Dz. Urz. Woj. Małop. 2016 poz. 812, § 6 ust. 2: „Uchwała wchodzi w życie z dniem 1 września 2019 r.“).
- **Vorher** = Mittel der Jahre 2016–2018, **Übergang** = 2019 (nicht gewertet), **Nachher** = Mittel 2020–2022.
  Je Station und Kennwert nur, wenn alle drei Jahre des Fensters einen gültigen Wert haben, sonst `null` mit Grund.
- Dieselbe Rechnung für die Umland-Stationen. Der Vergleich Stadt/Umland wird gezeigt, ohne ihn zu deuten.
- **Keine Kausalaussage.** Erlaubt: „vor dem Stichtag … nach dem Stichtag …“. Verboten (Falschsatz-Liste
  `pruefen/D7_powietrze.py`, alle drei Sprachen): Wendungen wie „dzięki zakazowi“, „z powodu zakazu“, „zakaz
  spowodował“, „because of the ban“, „thanks to the ban“, „due to the ban“, „the ban caused“, „wegen des Verbots“,
  „dank des Verbots“, „durch das Verbot“, „das Verbot bewirkte“. Genannt werden müssen andere Einflüsse ohne Zahl:
  Wetter, Pandemiejahr 2020, weitere Maßnahmen (nicht geprüft).

## 6. Ausgabe und Abnahme

- `daten/powietrze.js` (`window.KIEZ_POWIETRZE`) gegen `daten/schema/powietrze.json`; keine Personenbezüge (nur
  Messstationen), keine Adressfelder.
- `skripte/32_powietrze.py --pruefen` erzeugt die Datei aus den Rohdaten neu und vergleicht byte-gleich.
- `pruefen/D7_powietrze.py`: Vertrag, Grenzwerte gegen dieses Protokoll, Zählungen in sich stimmig
  (Rohzeilen = verwendet + verworfen je Grund), Vorher/Nachher nur bei drei Jahren, Falschsätze in
  `texte/*/powietrze.js`.
- Fehlen die Rohdaten, entsteht `daten/powietrze.js` als Beispieldatei mit `fixture: true` (erfundene Werte,
  sichtbar gekennzeichnet).

## Abweichung 1 (13.11.2026, Weg, nicht Regeln)

- **Anlass:** Der automatische Hauptweg aus Abschnitt 1 trägt nicht. Die Tabelle der EEA-Jahresstatistik ist über
  GET nicht abfragbar: Der Betrachter filtert und lädt nur per POST, Discodata kennt die Tabelle nicht
  („Invalid object name“), die ArcGIS-Dienste auf `air.discomap.eea.europa.eu` und das Portal
  `aqportal.discomap.eea.europa.eu` sind nach robots-Regel gesperrt (Weiterleitung auf robots.txt). Die
  GIOŚ-Rechner lösen lokal nicht auf. Einzelheiten: `quellen-D7.md`, `belege/D7_luft.md`.
- **Neu:** Hauptweg ist ein **Handdownload** (CSV-Export aus dem EEA-Betrachter „Annual AQ statistics“, Ablage
  `$KIEZ_DATEN/eingang/eea/`, Filter und Dateiformat in `quellen-D7.md`). Gegenprobe bleibt der GIOŚ-Handdownload.
  Bis dahin erzeugt `skripte/32_powietrze.py` Beispielzeilen im selben Format und schickt sie durch dieselbe
  Rechnung (`fixture: true`, erfundene Kennungen `FIKCJA-…`).
- **Unverändert:** Abschnitte 2 bis 6. Kein Messwert wurde bis zu diesem Commit gesehen.

## Abweichung 2 (14.11.2026, Format des Handdownloads, vor dem ersten echten Lauf)

- **Anlass:** Der Betrachter bietet den Export als GeoJSON an (Handdownload 14.11.2026,
  `eingang/eea/eea_aq_statistik_krakow_20261114.geojson.zip`, Zeile in `eingang/HERKUNFT.md`), nicht als CSV. Die
  Merkmale tragen dieselben Feldnamen wie die FieldOrder des Betrachters, mit zwei Ausnahmen.
- **Neu:** `skripte/32_powietrze.py` liest neben `*.csv` auch `*.geojson` und `*.geojson.zip` unter `eingang/eea/`
  (Prüfsumme der gelesenen Datei, bei ZIP der ZIP-Datei). Je Merkmal zählen nur die `properties`.
  - `SamplingPoint` fehlt; an seine Stelle tritt `AssessmentMethodId` (bei der EEA je Messstelle und Methode
    eindeutig, Form `SPO_<Station>_<Schadstoff>_<Nr>`). Er dient nur dem Gleichstand in Regel 4.
  - `potentialOutlier` fehlt; die Regel „Ausreißer verwerfen“ greift damit nicht. Das steht in der Zählung als
    `ausreisser_nicht_geliefert`, nicht still.
  - Fehlt einer Station in manchen Zeilen der Name (AirBase-Altdaten), gilt der erste vorhandene Name derselben
    `AirQualityStationEoICode`.
- **Grenze:** Der Export ist auf `City = Kraków` gefiltert. Umland-Stationen (Abschnitt 2) enthält er nicht; die
  Ausgabe hat deshalb 0 Umland-Stationen, bis ein zweiter Export ohne Stadtfilter vorliegt (offen, Andre).
- **Unverändert:** Abschnitte 2 bis 6, Jahre 2010–2025, Datenflüsse (E2a vorläufig bleibt ausgeschlossen),
  Deckungsgrenzen. Ein erster Blick auf die Feldnamen und Zählungen je Kennwert ging diesem Abschnitt voraus, kein
  Blick auf Werte einzelner Stationen und Jahre.
