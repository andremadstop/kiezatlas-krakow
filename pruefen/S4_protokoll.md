# Protokoll vor dem Lauf: Methode, Daten, Downloads

Festgelegt am 14.11.2026, bevor der Export und die Langtexte erzeugt werden. Spätere Änderungen nur als Nachtrag
unten, mit Datum und Grund; dieser Abschnitt bleibt stehen.

## Gegenstand

1. **Downloads** (`skripte/16_export_krakow.py`): GeoPackage, CSV, QGIS-Projekt und Liesmich je Sprache aus den
   veröffentlichten Datendateien unter `daten/`. Ziel ist `daten/pobierz/`, nicht `daten/export/`: Der Ordner
   `daten/export/` weckt in `pruefen.sh` die Potsdamer Exportprüfung, und `skripte/16_export.py` bleibt
   unverändert, weil die Gegenprobe Potsdam es braucht.
2. **Langtexte** (`skripte/16_bloecke_krakow.py`): Methoden- und Datenseiten in `texte/<lang>/bloecke/*.html`, erzeugt
   aus Quelltexten in `texte/<lang>/bloecke/quelle/*.html` mit Platzhaltern für jede Zahl.
3. **Prüfungen** (`pruefen/S4_export.py`, `pruefen/S4_bloecke.py`).

## Regeln für die Downloads

1. Quelle sind nur die Dateien unter `daten/`; keine Datenbank, kein Netz. Werte werden nicht neu gerechnet, nur
   umgeformt (Koordinaten, Spalten).
2. Dateien mit `fixture: true` (Beispieldaten) kommen nicht in den Export. Jede ausgelassene Datei steht mit Grund im
   Liesmich und im Beleg.
3. Zwei GeoPackages: `kiezatlas_krakow.gpkg` ohne jeden Anteil aus OpenStreetMap und ohne Zuordnung über die
   OSM-Grenzen (kein Feld `st`, keine Fußweg-Werte, keine OSM-Objekte); `kiezatlas_krakow_odbl.gpkg` mit allem, was
   aus `_odbl`-Dateien stammt, unter der ODbL 1.0 mit Vermerk „© OpenStreetMap-Mitwirkende“ bzw. „© OpenStreetMap
   contributors“. Für die CSV gilt dieselbe Trennung (`csv/` und `csv_odbl/`).
4. Die Zellen ohne Zuordnung (`zelle` in der Datei ohne ODbL) tragen nur Werte, die nicht aus OSM stammen: Einwohner
   und Altersanteile (Eurostat) und die Luftlinie (BDOT10k, ZTP). Grundlage ist dieselbe Lesart wie bei
   `daten/erreichbar.js` (`daten/LIZENZ.md`): Die Zellen sind die Zellen mit Mittelpunkt in der Stadtgrenze aus
   BDOT10k. Die Geometrie wird aus der Zellkennung des Eurostat-Gitters (EPSG:3035) gebildet, nicht aus
   `zellen_odbl.js`.
5. Koordinatensystem ist das Rechensystem `rechen_srid` aus `config/krakow.yaml` (EPSG:2178); umgerechnet mit pyproj
   aus WGS 84 (Datendateien) bzw. EPSG:3035 (Zellkennung). Keine Geometrie wird vereinfacht.
6. CSV in zwei Fassungen mit gleichem Inhalt: `csv*/` mit Punkt als Dezimalzeichen und `csv*_pl/` mit Dezimalkomma
   ohne Tausendertrenner (polnisches Excel und LibreOffice), beide UTF-8 mit BOM, Trennzeichen Semikolon. Punkte mit
   `x`/`y` im Rechensystem, Flächen mit WKT.
7. Jede Ebene trägt Lizenz und Vermerk aus den Feldern ihrer Datendatei (`quellen`, `vermerk`, `lizenz`, Kopfkommentar),
   wörtlich, nicht neu getippt. Die Lizenztabelle `licencje` steht in jedem GeoPackage und als `licencje.csv`.
8. Kein Personenbezug: keine Spalte für Adresse, Straße, Hausnummer, Telefon, E-Mail oder Personennamen; kein Wert mit
   Hausnummer oder Postleitzahl; keine Zeile je Kauf, keine Werte unter den Mindestfallzahlen der Quellen
   (die Datendateien halten sie schon ein; der Export übernimmt `null`).
9. Inhalt gleich Quelle: Jede Zahl jeder Ebene muss gleich dem Wert der Datendatei sein; CSV gleich GeoPackage.
10. QGIS-Projekt `kiezatlas_krakow.qgz` mit relativen Pfaden auf beide GeoPackages, Stile nach `DESIGN.md` (kein Orange).
11. Liesmich `CZYTAJ.md` (pl), `README.md` (en), `LIESMICH.md` (de): Ebenen, Felder, Lizenz je Datei, Zitierhinweis,
    Hinweis zum Dezimalkomma, Grenzen. Zahlen darin kommen aus den Daten.
12. Zwei Läufe hintereinander ergeben byte-gleiche Dateien (`--pruefen` vergleicht mit dem eingecheckten Stand).

## Regeln für die Langtexte

1. Polnisch zuerst, Englisch und Deutsch daraus abgeleitet; Fachbegriffe nach `docs/glossar-pl.md`.
2. Jede Zahl im sichtbaren Text ist ein Platzhalter `[[datei:pfad|format]]` und wird im erzeugten Block zu
   `<span data-feld="datei:pfad">Wert</span>`, formatiert wie `i18n.js` (`Intl.NumberFormat` der Sprache). Die
   Prüfung entfernt diese Spannen und meldet jede verbleibende Ziffer, außer einer kurzen, begründeten Liste von
   Kennungen (Namen von Datensätzen und Lizenzen, Rechtsfundstellen, EPSG-Codes, TERYT); die Liste steht in
   `pruefen/S4_bloecke.py`.
3. Lizenzvermerke stehen wörtlich aus den Datendateien (als Platzhalter), in der Originalsprache, nicht übersetzt.
4. Falschsätze: die Listen aus `pruefen/d3_falschsaetze.json` und eine eigene Liste für diese Seiten (Baujahr je
   Gebäude oder Fläche, Heizungsart, 100-m-Gitter, amtliche Bewertung eigener Rechnungen) laufen auf allen Blöcken;
   kein Treffer.
5. Keine internen Plankennungen und keine Pfade zu einzelnen Belegdateien im sichtbaren Text der Seiten; Verweise
   auf das Repository (`README.md`, `belege/README.md`, `docs/rundgang.md`, `docs/entscheidungen.md`) genügen.
6. Beispieldaten werden als solche benannt; Grenzen stehen offen in einem eigenen Abschnitt.

## Nachtrag 14.11.2026 (Nachbesserung nach der Abnahme)

Grund: Die Abnahme fand in den polnischen und englischen Downloads deutsche Reste und keine Erklärung der Felder.

1. **Zu Regel 7 (Vermerke):** Die Kopfkommentare der `_odbl`-Dateien sind deutsche Herkunftsangaben mit Skriptpfaden,
   kein Quellenvermerk. Für alle Anteile aus OpenStreetMap steht deshalb eine Zeile: Lizenz „ODbL 1.0“, Quelle
   „OpenStreetMap (Adresse aus `einrichtungen_odbl.js`)“, Vermerk wörtlich der englische OSM-Vermerk aus
   `sanierung_odbl.js` (`vermerk_sprachen.en`), so wie die Seiten in pl und en ihn zeigen. Die Quelle der Eurostat-Zeile
   ist „Name des Datensatzes (Adresse)“, beides wörtlich aus `steckbrief.js`; die dortige Zeile `quelle` ist deutsch
   („Polen“, „Datei“). Die Prüfung akzeptiert für die Spalte `zrodlo` diese Form „Teiltext (Adresse)“, wenn beide Teile
   wörtlich in den Datendateien stehen. Doppelte Zeilen je Ebene entfallen.
2. **Zu Regel 11 (Liesmich):** Die Bedeutung jedes Felds und jedes Kategorienwerts steht auf pl, en und de im Liesmich,
   in `pola.csv` und `wartosci.csv` und als Tabellen `pola` und `wartosci` in beiden GeoPackages. Texte in
   `skripte/export_pola_krakow.py`, erarbeitet aus `daten/schema/*.json` und den erzeugenden Skripten; Zahlen darin
   (Schwellen, Radien, Klassengrenzen) kommen aus den Datendateien. Fehlt eine Erklärung, bricht der Export ab.
   Feldnamen bleiben wie in den Datendateien (Regel 9).
3. **Grenzen:** Der Satz zu Baujahren nennt die einzige Ausnahme (Bauzeitklasse `ep` bei einzelnen OSM-Objekten mit
   `start_date`, ungeprüft, nie für Flächen).
4. **Neue Prüfungen** in `pruefen/S4_export.py` (Punkte 11 und 12 im Kopf): Erklärungen vollständig, CSV gleich den
   Tabellen, `licencje.csv` inhaltlich gleich den Tabellen, keine deutschen Wörter in pl und en (Feldnamen, Werte in
   Backticks, wörtliche Vermerke und die Rechtsform „UG (haftungsbeschränkt)“ im Firmennamen ausgenommen).
5. **Quellen vollständig (Altfehler aus dem ersten Lauf):** Die neue Prüfung 13 fand drei Ebenen, deren Quelle in
   `licencje` fehlte: `dostepnosc` ohne Eurostat (Einwohner, Zähler, Nenner), `osm_heritage_start_date` ohne BDOT10k
   (Felder `w`, `mfh`, `del`), `przystanki` ohne BDOT10k (Feld `in_stadt`, Stadtgrenze). Die alten Kopfkommentare nannten
   diese Quellen auch nicht; die Lücke bestand seit dem ersten Lauf. Ergänzt; Ausnahmen mit Grund in
   `pruefen/S4_export.py` (`QUELLE_AUSNAHMEN`).
