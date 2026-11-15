# Quellen Paket Luft (D7)

Stand 13.11.2026. Vorlage für `QUELLEN.md` (Übernahme durch die Belegschicht). Weg: A = Abruf über
`skripte/abruf.py`, H = Handdownload durch den Betreiber. Wörtliche Vermerke in Originalsprache; Abrufliste mit Zeiten und
Prüfsummen in `belege/D7_luft.md`, Prüfsummen der Rohdateien in `belege/rohdaten_D7.sha256`.

## Quellen

| Quelle | Nutzer | Adresse | Lizenz | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| EEA, „Air quality annual statistics calculated by the EEA“ (Tabelle „Annual AQ statistics (AirBase & e-Reporting merged)“); Messwerte der GIOŚ (Państwowy Monitoring Środowiska), an die EEA gemeldet, Jahreskennwerte von der EEA berechnet | `daten/powietrze.js` | Metadaten https://sdi.eea.europa.eu/catalogue/srv/api/records/6e191a3b-258d-491e-b636-6cbb15cf473b, Betrachter https://discomap.eea.europa.eu/App/AQViewer/index.html?fqn=Airquality_Dissem.b2g.AirQualityStatistics | CC BY 4.0 | „License CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Copyright holder: European Commission.“ | H (Export aus dem Betrachter, siehe unten); Lizenz- und Metadatenseiten A | Lizenz geprüft 13.11.2026; Daten **noch nicht da** (Beispieldaten) |
| Rozporządzenie Ministra Środowiska z dnia 24 sierpnia 2012 r. w sprawie poziomów niektórych substancji w powietrzu, tekst jednolity Dz.U. 2021 poz. 845, Załącznik nr 1 | Grenzwerte in `daten/powietrze.js` | https://api.sejm.gov.pl/eli/acts/DU/2021/845/text.pdf, Status https://api.sejm.gov.pl/eli/acts/DU/2012/1031 | Rechtsakt; urheberrechtsfrei nach art. 4 pkt 1 ustawy o prawie autorskim (aus Wissen, Wortlaut nicht geprüft) | entfällt | A | ELI-Status „IN_FORCE“ am 13.11.2026; spätere Änderungen nach diesem Tag nicht geprüft |
| Uchwała Nr XVIII/243/16 Sejmiku Województwa Małopolskiego z dnia 15 stycznia 2016 roku (Dz. Urz. Woj. Małop. 2016 poz. 812) | `kontekst` in `daten/powietrze.js`, Text `powietrze.stichtag` | Abzug auf https://sprawyspoleczne.krakow.pl/zalacznik/424838 | Rechtsakt (wie oben, nicht geprüft) | entfällt | A | Abzug des Dziennik mit elektronischer Signatur MUW vom 1.2.2016; Änderungen der Uchwała nach 2016 nicht geprüft |

Wörtliche Fundstellen zu Lizenz, Grenzwerten und Stichtag: `belege/D7_luft.md`, Abschnitt 2.

## Handdownloads (Ablage `kiezatlas-daten/krakow/eingang/`)

Das Skript `skripte/32_powietrze.py` liest diese Dateien, sobald sie da sind; fehlen sie, rechnet es mit
Beispieldaten (`fixture: true`). Seit 14.11.2026 liegt der Export als GeoJSON vor (Filter `City = Kraków`, ohne
Umland; `pruefen/D7_protokoll.md`, Abweichung 2). Nach dem Ablegen: `python -I skripte/32_powietrze.py`, dann
`python -I pruefen/D7_powietrze.py`.

### 1. EEA-Jahresstatistik (Hauptquelle): `eingang/eea/*.csv`

- **Wo:** Betrachter https://discomap.eea.europa.eu/App/AQViewer/index.html?fqn=Airquality_Dissem.b2g.AirQualityStatistics
  im Browser öffnen (der Download läuft dort per POST; `abruf.py` kann nur GET).
- **Filter:** Country = Poland; AirPollutant = PM10, PM2.5, NO2; ReportingYear 2010 bis 2025 (mehr schadet nicht,
  das Skript verwirft und zählt); DataAggregationProcess mindestens „Annual mean / 1 calendar year“,
  „1 year day exceed 50“ und „1 year hour exceed 200“. Eine Einschränkung auf Kraków ist **nicht** nötig und nicht
  erwünscht: das Umland (30 km) ergibt sich erst aus den Koordinaten. Wenn der Betrachter eine Zeilengrenze hat,
  mehrere Exporte (z. B. je Schadstoff) ablegen; das Skript liest alle `*.csv` im Ordner.
- **Format:** CSV, UTF-8 (mit oder ohne BOM), Trenner Komma oder Semikolon (das Skript erkennt beides an der
  Kopfzeile), Dezimalpunkt oder -komma. Pflichtspalten (Namen wie in der Feldliste `FieldOrder` des Betrachters):
  `Country`, `AirQualityStationEoICode`, `AQStationName`, `SamplingPoint`, `AirPollutant`, `DataAggregationProcess`,
  `ReportingYear`, `AirPollutionLevel`, `DataCoverage`, `SourceDataFlow`, `potentialOutlier`, `AirQualityStationType`,
  `AirQualityStationArea`, `Longitude`, `Latitude`, `City`. Fehlt eine, bricht das Skript mit Rückgabe 2 ab und
  nennt die Kopfzeile. Ob der Export genau diese Kopfzeile trägt: **nicht geprüft** (kein Export gesehen).
- **Dateiname:** frei, empfohlen `aqstat_PL_<schadstoff>_<JJJJ-MM-TT>.csv`. Die Prüfsumme jeder gelesenen Datei steht
  danach in `daten/powietrze.js` (`quelle.pliki`); bitte zusätzlich mit Abrufdatum und Filtern in
  `eingang/eea/HERKUNFT.md` notieren.
- **Größe:** nicht geprüft; die Feldliste des Betrachters (`viewer/init_aqstat.json`) nennt Zeilenzahlen je Land.

### 2. GIOŚ „Bank danych pomiarowych“ (Gegenprobe): `eingang/gios/*.xlsx`

- **Wo:** https://powietrze.gios.gov.pl/pjp/archives (Archiv der Messdaten, „Statystyki“ je Jahr). Adresse aus
  Wissen, **nicht geprüft**: Der Rechner war am 13.11.2026 automatisch nicht erreichbar (DNS ohne Antwort), robots.txt
  und Nutzungsbedingungen konnten nicht gelesen werden.
- **Vorher prüfen (Betreiber, im Browser):** Nutzungsbedingungen bzw. Lizenz der GIOŚ-Daten. Solange sie nicht wörtlich
  belegt sind, dient die Datei **nur intern als Gegenprobe**; nichts aus ihr geht in `daten/`.
- **Format:** Excel-Arbeitsmappe (`.xlsx`), Blattaufbau nicht geprüft. Das Skript liest sie nur ein und schreibt
  Blattnamen, Zeilenzahl und Kopfzeile in `belege/D7_luft_lauf.md`; der Wertevergleich wird erst nach Sichtung
  festgelegt (als Abweichung im Protokoll `pruefen/D7_protokoll.md`).
- **Dateiname:** frei, empfohlen `gios_statystyki_<JJJJ>.xlsx`.

## Geprüfte und gesperrte Wege (13.11.2026)

| Weg | Befund | Folge |
|---|---|---|
| api.gios.gov.pl (GIOŚ-API, aktuelle Messwerte) | robots.txt antwortet mit 302 (Machbarkeitsprobe 13.11.2026, Befund in `kiezatlas-daten/_robots/`); Sperrliste in `skripte/abruf.py` | kein Abruf; die API liefert ohnehin nur die letzten Tage, keine Jahresreihen (aus Wissen, nicht geprüft) |
| powietrze.gios.gov.pl (Rechner, Archiv) | DNS ohne Antwort („No address associated with hostname“), robots.txt nicht prüfbar, gesperrt nach Regel | Handdownload 2 |
| discomap.eea.europa.eu (Betrachter) | keine robots.txt (404), erlaubt; Filter und Download nur per POST | Feldliste per GET geladen, Daten als Handdownload 1 |
| discodata.eea.europa.eu (SQL-Schnittstelle) | keine robots.txt (404); Tabelle `[Airquality_Dissem].[b2g].[AirQualityStatistics]` dort unbekannt („Invalid object name“), Systemtabellen gesperrt | kein Weg |
| air.discomap.eea.europa.eu (ArcGIS), aqportal.discomap.eea.europa.eu | robots.txt leitet auf fremde Adressen weiter (302, 301), gesperrt nach Regel | kein Abruf |
| sdi.eea.europa.eu (Metadaten) | robots.txt `Allow: /` | Metadaten und Lizenzzeile abgerufen |
| www.eea.europa.eu | robots.txt ausgewertet, `/en/legal-notice` nicht gesperrt | Copyright notice abgerufen |
| edziennik.malopolska.uw.gov.pl (Dziennik Urzędowy) | TLS-Kette nicht prüfbar, robots.txt nicht lesbar, gesperrt nach Regel | Uchwała aus dem Abzug auf sprawyspoleczne.krakow.pl (robots.txt nur `AhrefsBot` gesperrt) |
| eur-lex.europa.eu | robots.txt mit Status 202 ohne Inhalt, gesperrt nach Regel | Richtlinie 2008/50/WE nicht verwendet; Grenzwerte aus der polnischen Verordnung |
