# Entscheidungsvorschläge des Pakets Echtlauf der Daten (13.11.2026)

Auftrag: alle Themen mit den vorhandenen echten Daten neu rechnen, nach den Entscheidungen vom 13.11.2026 abends
(Bestätigung der Vorschläge der Phase Datenpakete, Lizenzfolge der OSM-Grenzen Variante a, Regel 4 mit Ausnahme, LoD-Freigabe,
Luft und Wohnungsmarkt bleiben Beispiel, WDQS mit wenigen Abfragen erlaubt, ein gemeinsamer Ort für die PBF).
Beleg aller Zählungen vorher/nachher: `belege/DE_echtlauf.md`. Quellen und Ausgaben: `quellen-DE.md`.

Diese Datei schreibt keine gemeinsamen Dokumente. Was in `docs/entscheidungen.md` (Bestätigung KR13 bis KR24, neue
KR-Einträge) und `docs/rundgang.md` gehört, steht unten als Vorschlag für die Belegschicht.

## DE1: Seitendateien mit OSM-Grenzen heißen `_odbl` (Vertragsänderung)

- **Anlass:** Nach der Entscheidung zur Lizenzfolge (Variante a) werden Werte, die auf den OSM-Grenzen beruhen, als
  `_odbl`-Dateien unter der ODbL ausgeliefert. `pruefen/daten.py` erlaubt den ODbL-Vermerk nur in Dateien mit `_odbl`
  im Namen.
- **Umgesetzt:** `daten/zellen.js` → `zellen_odbl.js`, `kennzahlen.js/.json` → `kennzahlen_odbl.js/.json`,
  `planer.js` → `planer_odbl.js`; Verträge `daten/schema/zellen.json` → `zellen_odbl.json`, `kennzahlen.json` →
  `kennzahlen_odbl.json`, `planer.json` → `planer_odbl.json`, je mit `x-odbl: true`. Globale Namen bleiben
  (`KIEZ_ZELLEN`, `KIEZ_KENNZAHLEN`, `KIEZ_PLANER`). Der Schlüssel `zellen.js-Reihenfolge` in `erreichbar*.js` bleibt als
  Name der Zellreihenfolge stehen (Vertrag und Potsdamer Daten nutzen ihn).
- **Nachgezogen (Dateien anderer Eigentümer, kleinste Änderung):** `vorlagen/index.html`, `karta.html`,
  `dzielnica.html` (Kopfzeile `daten:`; Seiten neu erzeugt), `pruefen/daten.py` (Summen), `pruefen.sh` (Zeile zu den
  Beispieldaten), `pruefen/fixtures_krakow.py` (Namen und ODbL-Kopf), `config/krakow.yaml` (DE2).
- **Nicht angefasst, Übergabe an die Seitenpakete:** `planer.js` (Modul) lädt `daten/zellen.js` fest
  (`DATEI.zellen`) und erwartet `planer.js` als Datendatei; die Kraków-Seiten laden das Modul noch nicht. Beim Einbau
  den Dateinamen aus der Ortskonfiguration lesen, weil die Gegenprobe Potsdam dasselbe Modul mit `zellen.js` braucht.
  `skripte/16_export.py` (Potsdamer Stand) liest weiter `zellen.js`; Umbau im Paket Langtexte und Export.
  `daten/schema/themen.md` nennt noch `zellen.js`/`kennzahlen.js` als Beispiel. `jahre.js` (Bauzeiten, in Kraków
  gestrichen, KR4) meldet in einem Fehlertext `daten/zellen.js`; bleibt für die Gegenprobe Potsdam so.
- **Verworfen:** Namen behalten und die Prüfung lockern (bricht die Dateigrenze der ODbL); `st` aus `zellen.js`
  herausnehmen und nur die Zuordnung als `_odbl` liefern (die Seiten färben Zellen nach dzielnica, zwei Dateien für
  eine Ebene).
- **Neu prüfen, wenn:** amtliche Grenzen mit klarer Lizenz vorliegen (dann zurück zu Namen ohne `_odbl`).

## DE2: Regel 4 mit dokumentierter Ausnahme, `zuordnung_geprueft` = `true`

- **Umgesetzt wie entschieden:** `AUSNAHMEN_REGEL4 = {"03": 98.53, "15": 98.64}` in `skripte/raum_bevoelkerung.py`;
  die Ausnahme greift nur bei genau diesen Anteilen auf zwei Stellen, die Schwelle 99 % bleibt. Vermerk mit Zahlen in
  `config/krakow.yaml` (Kommentar), in `daten/steckbrief_dzielnice_odbl.js` (Feld `hinweis`) und in
  `belege/D4_bevoelkerung.md`. Nachtrag in `pruefen/D4_protokoll.md`.
- **Offengelegt:** Der Nachtrag im Protokoll steht im selben Commit wie der erste Lauf mit echten Seitendaten
  (f017be1), nicht als eigener Commit davor. Inhaltlich gibt er nur die Entscheidung vom Abend wieder.

## DE3: `st` nur in `_odbl`-Dateien

- **Anlass:** Die Zuordnung einer Haltestelle oder Einrichtung zur dzielnica beruht über die Zelle auf den OSM-Grenzen.
- **Vorschlag (vorsichtigere Variante, umgesetzt):** `haltestellen.js` und `einrichtungen.js` (ohne `_odbl`) tragen kein
  `st`; die Seite holt es über `zellen_odbl.js`. Werte je dzielnica stehen in `planer_odbl.js` (Luftlinie) und
  `planer_fuss_odbl.js` (Fußweg). `pruefen/D6_versorgung.py` prüft das statt der alten Sperre („KR3-Folgefrage
  offen“).
- **Verworfen:** `st` in `haltestellen.js` setzen (dann müsste die Datei `_odbl` heißen und die ganze Haltestellenliste
  stünde unter Share-Alike).
- **Grenze:** `erreichbar.js` und `klimat.js` bleiben ohne `_odbl`. Begründung: Die 327 Zellen sind genau die Zellen
  mit Mittelpunkt in der BDOT10k-Stadtgrenze (D4-Beleg, Schritt 4), keine Zelle hängt an einer OSM-Grenze; beide
  Dateien enthalten keine Werte je dzielnica. Nachbesserung: jetzt geprüft statt gelesen. `skripte/02_bevoelkerung.py`
  vergleicht die IDs beider Zellmengen (neue Regel im Beleg `belege/D4_bevoelkerung.md`): 327 Zellen über die
  dzielnice, 327 über die Stadtgrenze, 0 nur über die dzielnice. Der Tabellenkommentar von `public.zensus_zelle`
  (`sql/003_zellen.sql`) sagte das Gegenteil („Mittelpunkt in den Grenzen der dzielnice“). Er nennt jetzt die
  Stadtgrenze und die Prüfung. Eingespielt als `admin`, danach `14b_fussweg.sh rechnen` (3.597 Zeilen wie vorher, nur
  der Vermerk anders) und `14c` erneut: beide `_odbl`-Dateien Byte für Byte gleich, `belege/DE_fussweg.md` neu.

## DE4: Fußweg-Ziele in der Datenbank und Export als `_odbl` (neue Skripte)

- **Anlass:** `skripte/14b_fussweg.py` liest `auswertung.einrichtung`, `gruenflaeche`, `haltestelle`; die Kraków-Skripte
  der Versorgung schreiben nur Dateien, und für `erreichbar_fuss_odbl.js`/`planer_fuss_odbl.js` gab es kein Kraków-Skript.
- **Umgesetzt:** `skripte/14a_ziele_db_krakow.py` (Ziele aus `einrichtungen.js`, BDOT10k-Parks, Haltestellen der
  Taktklassen I/II; Rolle `kiezatlas_rechnen`), `skripte/14c_fussweg_export_krakow.py` (liest die Fußweg-Zeilen,
  schreibt beide `_odbl`-Dateien und `belege/DE_fussweg_export.md`). Kennzahlen je dzielnica: `anteil_in_radius`
  (szkola 3.000/4.000 m, przedszkole 3.000 m, vorläufig), `oepnv_takt` (500 m), `gruen_in_radius` (Park in 500 m).
- **Eigentum (Vorschlag):** beide Skripte zum Paket Versorgung und Takt; die Tabellenzeilen in `auswertung.einrichtung`,
  `gruenflaeche`, `haltestelle` ebenso.
- **Offen:** Gehgeschwindigkeit, Grün-Radius und Grünarten fehlen in `config/richtwerte.yaml` (Standards des Skripts,
  im Bericht so benannt). Die Arten in `erreichbar_fuss_odbl.js` (11) sind mehr als in `erreichbar.js` (4), weil die
  OSM-Ziele nur im Fußweg vorkommen.

## DE5: Wikidata nicht abrufbar (robots.txt), `denkmale.js` bleibt Beispieldatei

- **Anlass:** Die Entscheidung erlaubt WDQS für wenige Abfragen mit der Kennung des Abrufskripts und unter den
  WDQS-Regeln. `skripte/abruf.py` führt `query.wikidata.org` auf der Sperrliste.
- **Erster Lauf:** kein Abruf, Begründung damals die Projektkennung im User-Agent. Diese Begründung trägt nicht: Dieselbe
  Kennung ging schon an alle anderen Quellen (Abrufprotokoll), und die Abrufregeln verlangen Projekt und Kontakt im
  User-Agent.
- **Nachbesserung, gemessen:** Sperrlisteneintrag für `query.wikidata.org` probeweise entfernt und eine Probeabfrage
  (`BIND(wd:Q31487 …) LIMIT 1`) über `skripte/abruf.py` gestellt. Das Werkzeug holte zuerst `robots.txt`
  (13.11.2026 21:17:22 UTC, 95 B, SHA256 `212a112f9e27af6072758663789987cf84bfde70bd9b87f97ef76f91fd089b0c`, Befund in
  `kiezatlas-daten/krakow/_robots/2026-11-13/query.wikidata.org.*`): `User-agent: *` / `Disallow: /sparql` /
  `Disallow: /bigdata`. Die Abfrage selbst wurde gesperrt (Rückgabe 6), es ging keine SPARQL-Anfrage hinaus.
  Sperrlisteneintrag danach zurückgesetzt, `skripte/abruf.py` unverändert. Eine Freigabe durch die Entscheidung hebt
  robots.txt nicht auf; über andere Dienste oder Spiegel wird nicht ausgewichen.
- **Für André, ein Schritt:** die Abfrage aus `quellen-DZ.md` (Abschnitt „WDQS-Abfrage“) im Browser auf
  query.wikidata.org ausführen, „Download → JSON“ als `eingang/wikidata_zabytki_krakow.json` ablegen, danach
  `python -I skripte/dz_denkmale.py`. Mit Wikidata allein wird `denkmale.js` echt (das Skript setzt `fixture` nur, wenn
  alle drei Register fehlen). Vorher die Kennungen P3424 und Q31487 auf wikidata.org nachsehen (aus Wissen gewählt).
- **Folge:** `denkmale.js` bleibt Beispieldatei, über die im Auftrag genannten Ausnahmen (Luft, Wohnungsmarkt, NSP je
  dzielnica) hinaus. NID-Register und gminna ewidencja liegen ebenfalls nicht im Eingang.
- **Behoben (zweite Nachbesserung, vor dem Eingang):** `stand` von `denkmale.js` war im Skript das BDOT10k-Datum.
  Jetzt liest `skripte/dz_denkmale.py` den Abruftag jeder vorhandenen Registerdatei aus ihrer Zeile in
  `eingang/HERKUNFT.md` (letzte Spalte, TT.MM.JJJJ), schreibt ihn als `quellen.<kurz>.abruf` und setzt `stand` auf den
  jüngsten; ohne Abruftag Abbruch mit Rückgabe 4 (gleiches Muster wie DE6). Auf den heutigen Eingängen byte-gleich;
  der Wikidata-Pfad ist nur mit Testdateien im Scratchpad geprüft (3 Abbrüche, 2 Treffer), nicht mit echtem Eingang.
  Für André heißt das: beim Ablegen von `wikidata_zabytki_krakow.json` die Zeile in `HERKUNFT.md` mit Abrufdatum
  anlegen (steht schon so in `quellen-DZ.md`).

## DE6: Denkmale aus OSM als ungeprüft gekennzeichnet (Vertragsänderung)

- **Umgesetzt:** Stichprobe von 20 OSM-Treffern mit Gebäude (Startwert 20261113) im Beleg; niemand hat sie am Luftbild
  ausgewertet. `denkmale_odbl.js` trägt `sichtpruefung: {geprueft: false, stichprobe: 20, startwert, hinweis}`; neues
  optionales Feld in `daten/schema/denkmale_odbl.json`. Die Seite soll die Punkte bei `geprueft: false` als ungeprüft
  zeigen.
- **Behoben (Nachbesserung):** `stand` in `denkmale_odbl.js` war der BDOT10k-Stand (2026-10-03). Jetzt liest
  `skripte/dz_denkmale.py` den `osmosis_replication_timestamp` aus dem Kopf des Auszugs (`osm_pbf.kopf_lesen`) und
  schreibt dessen UTC-Tag (2026-11-12); fehlt der Zeitstempel, bricht das Skript ab. Sonst ist die Datei unverändert
  (Vergleich der JSON-Inhalte vor/nach: nur `stand` anders).
- **Nachtrag 15.11.2026 (überholt durch die zweite Sichtprüfung):** Die Kennzeichnung „ungeprüft“ gilt nicht mehr.
  Eine zweite Stichprobe (je 20 Punkte aus Wikidata und OSM, Startwert 20261114, `pruefen/DZ_protokoll.md` Nachtrag 3)
  ist am 15.11.2026 am Luftbild ausgewertet (Regel vor dem Rechnen: Nachtrag 4; Eingabe
  `belege/DZ_sichtpruefung.json`). `denkmale.js` und `denkmale_odbl.js` tragen jetzt `sichtpruefung.geprueft: true`
  mit Quoten und Wilson-Intervall (Schema: `daten/schema/denkmale*.json`), die Seiten nennen das Ergebnis der Ebene
  statt „ungeprüft“; `polozenie_sprawdzone` bleibt je Punkt 0. Ohne die Eingabedatei fallen Daten und Texte auf
  `geprueft: false` und den Hinweis „ungeprüft“ zurück (`pruefen/DZ_test_eingang.py`, `pruefen/S4_bloecke.py` Teil 9).

## DE7: 3D-Dateien je dzielnica außerhalb des Repos

- **Anlass:** KR18: Die Gebäudedateien kommen ins Repo, wenn die Grenzen echt sind. Sie sind echt, die Dateien haben
  zusammen rund 32,5 MB (gzip rund 5,7 MB, Zahlen unten), und ihre Aufteilung beruht auf den OSM-Grenzen; der Vertrag `gebaeude.json`
  legt `gebaeude/*.js` ohne `_odbl` fest.
- **Vorsichtigere Variante:** nicht ins Repo, sondern nach `kiezatlas-daten/krakow/abgeleitet/gebaeude/` mit
  `SHA256SUMS` und `HERKUNFT.md`.
- **Nachbesserung (Vertragsänderung wie DE1):** Die Aufteilung beruht auf den OSM-Grenzen, also gilt Variante a.
  `skripte/20_bdot10k.py --geometrie` schreibt mit echten Grenzen `<nr>_odbl.js` mit dem Vermerk „© OpenStreetMap-
  Mitwirkende, Open Database License (ODbL) 1.0“ im Kopf (mit Beispielgrenzen weiter `<nr>.js`). Neuer Vertrag
  `daten/schema/gebaeude_odbl.json` (`x-datei: gebaeude/[0-9][0-9]_odbl.js`, `x-odbl: true`), `gebaeude.json` gilt
  nur noch für `gebaeude/[0-9][0-9].js` (Potsdam, Beispielgrenzen); `pruefen/daten.py` zählt beide Namen. Neu erzeugt
  nach `2026-11-13-odbl/` (32.484.980 B, gzip 5.702.953 B, Inhalt gleich), der erste Ordner `2026-11-13/` ist in seiner
  `HERKUNFT.md` als ersetzt markiert und darf nicht ausgeliefert werden.
- **Übergabe an das Seitenpaket 3D:** `atlas.js` und `karte.js` laden fest `daten/gebaeude/<nr>.js`; die Gegenprobe
  Potsdam braucht diesen Namen weiter. Beim Einbau den Namen aus der Ortskonfiguration lesen (wie `planer.js`, DE1).
- **Für die Integration:** Ablage (Repo oder wie die Grundkarte über das Deploy).

## DE8: Datenbank: DDL und Zeilen der Integration

- `sql/003_zellen.sql`: `public.zensus_zelle` (Eurostat-Gitter, 1 km) mit `COMMENT ON TABLE` (Eurostat, CC BY 4.0;
  Auswahl über die OSM-Grenzen), `GRANT SELECT` an `kiezatlas_rechnen` und `mosidi_lesen`. Eingespielt als `admin`.
- `public.stadtteil` und `public.zensus_zelle` füllt `skripte/05_db_gliederung.py` als `admin`, weil es für beide keine
  Pipeline-Quelle gibt; `public.*` schreibt sonst nur die Pipeline. Eigentum (Vorschlag): Integration.

## Vorschlag für `docs/entscheidungen.md`

- KR13 bis KR24: Stand „bestätigt (13.11.2026 abends)“.
- KR3, Folge: entschieden, Variante a (DE1, DE3); KR13 „Neu prüfen“ erledigt.
- KR17, offener Teil: Regel 4 mit Ausnahme, `zuordnung_geprueft` = `true` (DE2).
- KR18: LoD2-Höhen veröffentlicht, Vermerk wörtlich, Stand 2017, Herkunft je Gebäude im Feld `hq` (Lauf: lod2 74.320,
  geschosse 16.230, ersatz 13).
- KR20: EEA-Daten gelten als CC BY 4.0 mit Nennung „EEA; Daten: GIOŚ“; `powietrze.js` bleibt Beispiel bis zur CSV.
- KR22: Mindestfallzahl 10 bleibt; `mieszkania.js` bleibt Beispiel bis zum RCN-Handdownload.
- KR24: WDQS erlaubt (wenige Abfragen), aber `robots.txt` von query.wikidata.org sperrt `/sparql` (DE5, gemessen);
  Wikidata bleibt Handdownload. Overpass bleibt gesperrt.
- Neu: ein gemeinsamer Ort für die PBF (`kiezatlas-daten/krakow/eingang/`), Kopien nur mit Prüfsumme (so gelaufen:
  `osm/2026-11-12/` gleich `eingang/SHA256SUMS`).

## Vorschlag für `docs/rundgang.md`, Abschnitt „Datenstand je Thema“

| Thema | Datei | Stand | Grund, wenn Beispiel |
|---|---|---|---|
| Gliederung | `stadtteile_odbl.js`, `zellen_odbl.js`, `kennzahlen_odbl.*` | echt | |
| Bevölkerung | `steckbrief.js` (Stadt, delegatury) | echt | je dzielnica `null` mit Grund (Werte nur in den `_odbl`-Dateien); NSP je dzielnica `null`, solange die rejony fehlen |
| Bevölkerung | `steckbrief_dzielnice_odbl.js` | echt | NSP je dzielnica `null` (rejony fehlen) |
| Fußweg | `auswertung.netz_*`, `zelle_erreichbar`, `zelle_gruen` (Datenbank) | echt | |
| Gebäude | `gebaeude_kennzahlen.js`, `gebaeude_dzielnice_odbl.js` | echt | |
| Gebäude, 3D | `gebaeude/<nr>_odbl.js` | echt, außerhalb des Repos | Ablage und Laden in den Seiten offen (DE7) |
| Versorgung | `haltestellen.js`, `einrichtungen.js`, `einrichtungen_odbl.js`, `erreichbar.js`, `erreichbar_fuss_odbl.js`, `planer_odbl.js`, `planer_fuss_odbl.js` | echt | `st` nur in den `_odbl`-Dateien |
| Luft | `powietrze.js` | Beispiel | EEA-Handdownload fehlt; echt nur Grenzwerte und Uchwała |
| Grundkarte | `grundkarte.js` (Kacheln außerhalb des Repos) | echt | |
| Wohnungsmarkt | `mieszkania.js` | Beispiel | RCN-Handdownload fehlt |
| Klima | `klimat.js`, `klimat_zellen.js`, `klimat_stadtteile_odbl.js` | echt | |
| Denkmale | `denkmale_bdot.js`, `denkmale_odbl.js` | echt | bei Abschluss OSM-Lage ungeprüft; seit 15.11.2026 in einer Stichprobe geprüft (`sichtpruefung.geprueft: true`, DE6 Nachtrag) |
| Denkmale | `denkmale.js` | Beispiel (seit 14.11.2026 echt aus Wikidata) | bei Abschluss fehlten Wikidata, NID-Register und gminna ewidencja im Eingang (DE5); seit 14.11.2026 Wikidata von Hand abgerufen, Lage seit 15.11.2026 in einer Stichprobe geprüft; NID und gminna ewidencja fehlen weiter |

Dazu in der Schritttabelle: neue Schritte `skripte/05_db_gliederung.sh` (nach Schritt 5a), `14a_ziele_db_krakow.py` und
`14c_fussweg_export_krakow.py` (um Schritt 6), Prüfungen wie in `belege/DE_echtlauf.md`.

## Nicht in diesem Paket, aber entschieden

- Schrift mit allen polnischen Zeichen (ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ): betrifft Grundkarte und Seiten, hier nicht geändert.
  Auf `Arbeitszweig df` erledigt (`adcb6cf`, Barlow latin + latin-ext aus Fontsource 5.3.0); nachgeprüft mit fontTools: alle
  fünf Schnitte haben alle 18 Zeichen. Wirksam mit dem Merge von `Arbeitszweig df` in die Integration.
- Thema „Sanierungsatlas Wohnungsbestand“: eigenes Paket, hier nichts gerechnet.
