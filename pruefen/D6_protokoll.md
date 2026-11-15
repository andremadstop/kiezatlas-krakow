# Protokoll Versorgung und Takt: Regeln vor dem ersten Lauf

Stand 13.11.2026, festgelegt **vor** dem ersten Lauf der Skripte `skripte/11_einrichtungen_krakow.py`,
`13_oepnv_krakow.py`, `14_erreichbarkeit_krakow.py` und `15_planer_krakow.py`. Dieser Commit legt nur die Regeln
fest; er enthält kein Ergebnis. Was danach an den Regeln geändert wird, steht unten unter „Änderungen nach dem
ersten Lauf“ mit Grund und Commit, die alte Fassung bleibt in der Historie.

Bekannt vor diesem Protokoll war nur der Aufbau der Eingaben, keine Auswertung: Feldnamen und Zeilenzahlen der drei
GTFS-Dateien (alle `location_type` 0, kein `parent_station`, `direction_id` überall gefüllt, Haltestellen-Codes
der Form `NNN-PP`, alle Wochentage in `calendar.txt` 0, Dienste nur über `calendar_dates.txt`), die Fahrtenzahlen
je Feed am 18.11.2026 aus der Machbarkeitsprobe und die Werte der Felder `RODZAJ` in den BDOT10k-Ebenen
`OT_KUOS_A`, `OT_KUOZ_A`, `OT_KUSK_A`, `OT_ADJA_A`.

## Eingaben

| Eingabe | Pfad unter `$KIEZ_DATEN` | Lizenz |
|---|---|---|
| GTFS ZTP Kraków, Bus (A), Tram (T), Mobilis (M) | `2026-11-13/06_oepnv/GTFS_KRK_{A,T,M}.zip` | CC BY 4.0 |
| BDOT10k Powiat 1261 | `2026-11-13/03_gebaeude/1261_SHP.zip` | frei, Quellenangabe (art. 40a ust. 2 pkt 1 lit. h, art. 40c ust. 3 und 5 Prawo geodezyjne i kartograficzne) |
| Prawo oświatowe, tekst jednolity Dz.U. 2026 poz. 820 | `d6_recht/2026-11-13/prawo_oswiatowe_DU_2026_820.pdf` | amtlicher Text |
| Zellen, Stadtteile, Einwohner | `daten/zellen.js`, `daten/stadtteile_odbl.js` im Repo | bis zum Paket Gliederung und Bevölkerung Beispieldaten |

Prüfsummen der Rohdaten in `belege/rohdaten-D6-2026-11-13.sha256`, selbst berechnet.

## ÖPNV-Haltestellen und Taktklasse (`13_oepnv_krakow.py`)

1. **Haltestelle** = Stamm des `stop_code` vor dem Bindestrich (`100-03` → `100`), über alle drei Feeds. Die Kennungen
   (`stop_id`, `trip_id`, `service_id`) werden je Feed mit dem Feed-Kürzel versehen, bevor sie zusammenkommen.
   Befund, wenn ein Stamm in den Feeds verschiedene `stop_name` trägt. Berichtet wird, wie viele Stämme in mehr als
   einem Feed vorkommen und wie viele Steige mehr als 300 m vom Mittelpunkt ihres Stamms liegen.
2. **Lage** = Mittel der Steige des Stamms (WGS 84, 5 Nachkommastellen).
3. **Stichtag** Mittwoch, 18.11.2026 (Schulwoche; kein Feiertag). Gegenprobe Freitag, 13.11.2026 (der einzige
   Werktag, der in allen drei Feeds und im `feed_version`-Zeitraum des Bus-Feeds liegt). Abbruchregel: Die Zahl der
   Fahrten am 18.11. je Feed muss den unabhängig gezählten Werten der Machbarkeitsprobe gleichen
   (`2026-11-13/_auswertung/gtfs_stichtage.txt`: A 10.280, T 3.710, M 2.590), sonst Befund und kein Ergebnis.
4. **Fenster** 06:00 bis 09:00 Uhr. Gezählt werden Abfahrten (ohne `pickup_type` 1, ohne letzten Halt der Fahrt),
   alle Linien zusammen, je `direction_id`; es zählt die stärkere Richtung; Wert = Abfahrten je Stunde (Mittel über
   drei Stunden). Fahrten des Vortags mit Zeiten ab 24:00 zählen mit ihrer Uhrzeit.
5. **Taktklasse** nach den Untergrenzen I ≥ 6, II ≥ 2, III ≥ 1 Abfahrten je Stunde und Richtung, sonst „unter III“.
   Die Grenzen sind das Muster des Kiezatlas Potsdam (dort aus dem Potsdamer Nahverkehrsplan); für Kraków ist das
   eine **eigene Klassifikation ohne polnische Fundstelle**: Status „orientierung“, kein Richtwert, kein Abzeichen
   „standard urzędowy“.
6. **Verkehrsmittel**: `route_type` 0 und 900–999 = tram, 3 und 700–799 = bus; anderes wird als „sonstige“ gezählt und
   berichtet. Nur Haltestellen mit mindestens einer Abfahrt am Stichtag.
7. **Lage zur Stadt**: `in_stadt` = Punkt in der Gemeinde Kraków aus BDOT10k `OT_ADJA_A` (`RODZAJ` „gmina“,
   `IDTERYTJED` 1261011). Haltestellen bis 1.000 m außerhalb bleiben mit `in_stadt: false`, weiter entfernte fallen
   weg (Zahl im Beleg). Zuordnung zu einer dzielnica nur, wenn `daten/stadtteile_odbl.js` echte Grenzen trägt
   (kein `fixture`); sonst `st: null`.

## Einrichtungen (`11_einrichtungen_krakow.py`)

8. BDOT10k-Komplexe, Lage = Punkt in der Fläche (`point_on_surface`), umgerechnet aus dem Koordinatensystem der
   `.prj`-Datei nach WGS 84:

   | Ebene | `RODZAJ` | `art` |
   |---|---|---|
   | `OT_KUOS_A` | szkoła lub zespół szkół | `szkola` |
   | `OT_KUOS_A` | przedszkole | `przedszkole` |
   | `OT_KUOZ_A` | żłobek | `zlobek` |
   | `OT_KUOZ_A` | zespół szpitalny lub sanatoryjny | `szpital` |
   | `OT_KUSK_A` | park lub skwer | `park` (mit Fläche in m² im Rechen-Koordinatensystem) |

   Alle anderen Werte (u. a. szkoła wyższa, ośrodek naukowo-badawczy, zakład opieki socjalnej lub dom dziecka,
   kompleks sportowo-rekreacyjny, ogród botaniczny, ogród zoologiczny) werden gezählt und nicht übernommen. Ein
   Komplex mit `KAT_ISTNIE` außer leer oder „eksploatowany“ fällt weg (Zahl im Beleg).
9. Namen nur aus `NAZWA` (Name der Einrichtung), keine Adresse, keine weiteren Felder. `status` immer
   „lage_ohne_kapazitaet“ (BDOT10k nennt keine Plätze und keine Schülerzahlen).
10. RSPO (Schulregister) nur aus einem Handdownload unter `$KIEZ_DATEN/eingang/`; ohne Datei kein RSPO-Teil.
    OSM-Einrichtungen nur aus `auswertung.osm_poi` (Paket OSM und Fußwegnetz); solange die Tabelle leer ist, ist
    `daten/einrichtungen_odbl.js` eine Beispieldatei mit `fixture: true`.

## Erreichbarkeit und Planer (`14_erreichbarkeit_krakow.py`, `15_planer_krakow.py`)

11. Methode Luftlinie (Zellmittelpunkt bzw. Einwohner der Zelle am Zellmittelpunkt zur nächsten Einrichtung) im
    Rechen-Koordinatensystem, auf 10 m gerundet. Unbewohnte Zellen (`ew` 0 oder fehlt) = `null`. Fußweg erst mit
    dem Netz des Pakets OSM und Fußwegnetz, in einer `*_odbl`-Datei.
12. Eine Ausgabe, die `daten/zellen.js` oder `daten/stadtteile_odbl.js` als Beispieldatei liest, ist selbst eine
    Beispieldatei (`fixture: true`), auch wenn Einrichtungen und Haltestellen echt sind; der Hinweis sagt das.
13. Kennzahlen je dzielnica, je Quote mit Zähler und Nenner:
    - `anteil_in_radius` für `szkola` mit 3.000 m und 4.000 m und für `przedszkole` mit 3.000 m. Fundstellen:
      art. 39 ust. 2 (Weg zur Grundschule höchstens 3 km für Klassen I–IV, 4 km für Klassen V–VIII) und
      art. 32 ust. 3 (Weg zum Kindergarten höchstens 3 km) Prawo oświatowe. Status „orientierung“ und `vorlaeufig`,
      weil das Gesetz den **Weg** zur Schule des eigenen Schulbezirks meint, hier aber die Luftlinie zur nächsten
      Schule jeder Art gemessen wird (BDOT10k trennt Grund- und weiterführende Schulen nicht).
    - `ew_je_einrichtung` für `szkola`, `przedszkole`, `zlobek`; ohne Richtwert.
    - `oepnv_takt`: Anteil der Einwohner mit einer Haltestelle der Taktklasse I oder II im Umkreis von 500 m
      Luftlinie. 500 m ist eine eigene Festlegung; ohne Richtwert.
    - `gruen_m2_je_ew`: Parkfläche (BDOT10k, `park`) in der dzielnica je Einwohner; ohne Richtwert.
14. Geheimhaltung: In Raumeinheiten unter `geheimhaltung.min_ew_raumeinheit` Einwohnern ist jeder Wert `null` mit
    Grund; Einwohner gerundet nach `geheimhaltung.rundung_ew`, Anteile ganzzahlig. Kein `0`, wo ein Wert fehlt.
15. Wilson-Intervalle entfallen: Die Quoten sind Vollerhebungen über Zellen, keine Stichproben. Die Unsicherheit
    (1-km-Zellen, Luftlinie, Stichtag) steht als Text an jedem Wert.

## Abnahme

- `pruefen/D6_versorgung.py` grün: Verträge, Taktklasse aus Abfahrten nach Regel 5 nachgerechnet, Zählungen der
  Belege gleich den Dateien, keine Plankennungen und keine OSM-Spur außerhalb von `*_odbl`, jede Beispieldatei mit
  `fixture: true`, jedes Skript mit `--pruefen` byte-gleich.
- `./pruefen.sh` im Worktree grün.

## Änderungen nach dem ersten Lauf

1. **Regel 7, Zuordnung zur dzielnica** (13.11.2026, Commit `e15a871`, nach dem ersten Lauf von
   `13_oepnv_krakow.py`; Ergebnis unverändert, weil weiter `st: null`): Die Haltestelle bekommt das Feld `st` der Zelle aus `daten/zellen.js`, in
   der sie liegt, nicht mehr den Stadtteil aus `daten/stadtteile_odbl.js`. Grund: Echte Stadtteilgrenzen stehen dort
   unter ODbL; eine Zuordnung daraus darf nicht in `daten/haltestellen.js` (ohne `_odbl`) einfließen. Dieselbe
   Zuordnung über die Zelle nutzt `15_planer_krakow.py` für Einrichtungen und Parks (Regel 13). Folge: An Grenzen
   einer dzielnica, die eine Zelle schneidet, folgt die Zuordnung der Zelle, nicht der Grenze.
   *Berichtigung (13.11.2026, Nachprüfung, Commit `b37b7cd`):* Die Begründung „darf nicht einfließen“ ist damit nicht erledigt. Das
   Feld `st` der Zelle stammt selbst aus einer Grenze der dzielnice, und die einzige freigegebene Quelle dafür ist
   OSM (KR3). Ob davon abgeleitete Werte unter die ODbL fallen, ist offen (KR3, Paket Gliederung). Bis dahin trägt
   `haltestellen.js` nur `st: null` und `planer.js` `fixture: true`; siehe `docs/entscheidungen/D6.md`.
2. **Regel 10, OSM** (Schalter eingeführt mit dem ersten Lauf von `11_einrichtungen_krakow.py` in Commit `5f7c450`,
   hier nachgetragen in `e15a871`, also nach dem ersten Lauf): `auswertung.osm_poi` wird nur
   mit dem Schalter `--osm-db` gelesen (Leserolle `mosidi_lesen`); am 13.11.2026 mit dem Schalter geprüft: 0 Zeilen,
   also Beispieldatei. Overpass ist kein Ausweg: `skripte/abruf.py` sperrt `overpass-api.de` („OSM nur aus dem
   Handdownload“).
3. **Abnahme, Taktklasse nachgerechnet** (Commit `e15a871`, vor dem ersten Lauf von `pruefen/D6_versorgung.py`): Die Prüfung rechnet
   Abfahrten und Taktklasse mit eigenem Code aus den GTFS-Zips nach (ohne `13_oepnv_krakow.py` zu importieren), für
   eine feste Stichprobe von Haltestellen; fehlen die Zips unter `$KIEZ_DATEN`, wird dieser Teil mit Grund
   übersprungen.
4. **Regel 8, Parkfläche** (Commit `1b7a6ce`, nach dem ersten Lauf von `11_einrichtungen_krakow.py`): `park` trägt in
   `daten/einrichtungen.js` keine Fläche, weil der Vertrag `einrichtungen.json` dafür kein Feld hat
   (`additionalProperties: false`). `15_planer_krakow.py` liest die Parkflächen stattdessen direkt aus BDOT10k
   (`OT_KUSK_A`, „park lub skwer“, gleiche `KAT_ISTNIE`-Regel) und verschneidet sie mit den Zellen.
5. **Abnahme, Fundstellen nachgelesen** (13.11.2026 17:35, Commit `4fda5ff`, Nachbesserung nach der Nachprüfung, nach dem ersten Lauf
   von `15_planer_krakow.py`): Die Seitenzahlen in `config/richtwerte.yaml` waren falsch (art. 39 ust. 2 auf s. 40
   statt 41, art. 32 ust. 3 auf s. 36 statt 37; Wortlaut richtig). Korrigiert, `daten/planer.js` und
   `belege/D6_planer.md` mit `15_planer_krakow.py` neu erzeugt (nur die Fundstellen ändern sich, keine Zahl;
   Beleg: `git diff --word-diff=porcelain 30d4bfa 4fda5ff -- daten/planer.js belege/D6_planer.md` zeigt nur
   `41`→`40` (38 + 2 Stellen) und `37`→`36` (19 + 1 Stellen)). Neuer
   Prüfschritt 7 in `pruefen/D6_versorgung.py`: Prüfsumme des Abzugs gleich dem Beleg, auf der genannten Seite stehen
   Seitenkopf, „Art. N.“, Absatz M vor dem Wortlaut und der ganze Wortlaut; Schritt 6 verlangt zusätzlich, dass jede
   Fundstelle in `planer.js` so in der config steht. Gegenprobe: Mit den alten Seiten 41/37 meldet Schritt 7 beide
   Fundstellen als Befund, Schritt 6 die Abweichung zu `planer.js`.
6. **Verträge `erreichbar.json`, `erreichbar_fuss_odbl.json`** (13.11.2026 17:37, Commit `e61eb2e`, Nachbesserung): Die direkte Änderung
   des Musters auf `^CRS3035RES(100|1000)m` aus Commit `928f0d5` ist zurückgenommen (Dateien gehören der
   Integration); sie steht nur noch als Vorschlag in `docs/entscheidungen/D6.md`. Folge: `pruefen/daten.py` meldet für
   `daten/erreichbar.js` einen Befund, bis die Integration entscheidet. Die Abnahme „`./pruefen.sh` grün“ hängt
   damit an dieser Entscheidung.
