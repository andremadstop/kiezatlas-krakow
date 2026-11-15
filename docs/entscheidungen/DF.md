# Entscheidungsvorschläge des Pakets Schrift und Grundkarten-Anbindung (DF, 13.11.2026)

Belege: `belege/DF_schriften_grundkarte.md`, Quellen: `quellen-DF.md`. Alle Punkte sind Vorschläge ohne KR-Nummer;
die Nummer vergibt die Belegschicht. Grundlage: Auftrag der Projektleitung vom 13.11.2026 abends („Die Schrift muss
alle polnischen Zeichen haben“; Grundkarte für alle Atlas-Seiten).

## Dateien des Pakets (Eigentum)

| Datei | Eigentümer bisher | Stand |
|---|---|---|
| `fonts/*.woff2`, `fonts/einbettung.js` | nicht angegeben (Gerüst) | ersetzt, erzeugt von `skripte/schriften.py`; Vorschlag: Eigentümer dieses Paket, danach Integration |
| `skripte/schriften.py`, `pruefen/DF_schriften.py` | neu | Vorschlag: dieses Paket, Prüfung danach Belegschicht |
| `skripte/entwicklung_server.mjs`, `pruefen/DF_grundkarte.mjs` | neu | Vorschlag: dieses Paket, danach Belegschicht |
| `belege/DF_*`, `belege/rohdaten-DF-schriften.sha256`, `quellen-DF.md` | neu | Übernahme durch die Belegschicht |
| `themen.js` | Integration (Vertrag) | geändert im Auftrag der Projektleitung: Auflösung relativer Pfade, Quellen null; Bestätigung als Vertragsänderung nötig |
| `config/krakow.yaml` Abschnitt `karte` | Paket Grundkarte | `grundkarte` gesetzt, Kommentar zu `luftbild` (Auftrag der Projektleitung) |
| `daten/ort.js` | Integration (erzeugt) | neu erzeugt mit `skripte/31_ort.py`, keine Handänderung |
| `NOTICE` | Belegschicht | im Auftrag geändert, nur die Zeilen zu den Schriften (Barlow neu gefasst, Noto Sans ergänzt) |
| `kartenfeld.js`, `kartenfeld.css` | neu | einfache Karte für Textseiten (Grundkarte + Stadtteile); Vorschlag: dieses Paket, danach Seitenpakete |
| `vorlagen/karta.html`, `karta.html`, `en/karta.html`, `de/karta.html` | Seitenpaket | Kartenfläche und Ladeliste ergänzt (Nachbesserung: eine echte Seite muss die Grundkarte zeigen); Seiten mit `30_seiten.py` erzeugt |
| `skripte/30_seiten.py` | Integration | optionale Kopfzeilen `css:` und `skripte:` in den Vorlagen (Module nach `rahmen.js`); ohne die Zeilen unverändert |
| `skripte/deploy_kopie.py` | Paket Deploy | Grundkarte in die Kopie (Abschnitt Bereitstellung) |
| `pruefen.sh` | Belegschicht | Schritte `DF_schriften.py`, `schriften.py --pruefen`, `DF_grundkarte.mjs` |
| `pruefen/seiten.mjs` | Belegschicht | unter HTTP `daten/grundkarte/` aus dem Kachelordner (wie `entwicklung_server.mjs`); ohne Kachelordner fehlende Kacheln als übersprungen gemeldet, nicht als Befund; sonst unverändert |
| `requirements-schriften.in`, `requirements-schriften.txt` | neu | fontTools und brotli mit Hashes; Vorschlag: Paket Infrastruktur |
| `pruefen/DF_kerning.py` | neu | Messung, keine Prüfung; Vorschlag: dieses Paket, danach Belegschicht |

Die Änderungen an fremden Dateien (Vorlage und Seiten `karta`, `30_seiten.py`, `deploy_kopie.py`, `pruefen.sh`)
kamen mit der Nachbesserung nach der Abnahmeprüfung: Ohne sie zeigte keine echte Seite die Grundkarte, und ein
Deploy hätte jede Kachel mit 404 beantwortet. Bestätigung durch die jeweiligen Eigentümer nötig.

Nicht angefasst: `atlas.css`, `schaugrafik.js`, `skripte/16_export.py` (Seitenpakete; dank gleicher Dateinamen nicht
nötig), die übrigen Vorlagen, `requirements.txt`, `docs/entscheidungen.md`, `QUELLEN.md`, `DESIGN.md`.

## Schriften: Barlow bleibt, latin und latin-ext je Schnitt zusammengefügt

- **Anlass:** Die Dateien unter `fonts/` waren die Teilmenge `latin` von Fontsource; 16 der 18 polnischen
  Sonderzeichen fehlten (Beleg Abschnitt 1). Der Browser setzte sie aus einer Systemschrift, die Schaugrafik ebenso.
- **Entscheidung (Vorschlag):** Barlow und Barlow Semi Condensed aus den npm-Paketen `@fontsource/barlow` und
  `@fontsource/barlow-semi-condensed` 5.3.0 (OFL 1.1), abgerufen über `skripte/abruf.py`, geprüft gegen SHA256 und
  die sha512-Integrität der Registry. Je Schnitt werden `latin` und `latin-ext` mit `fontTools.merge` zu einer Datei
  unter dem bisherigen Namen zusammengefügt (`skripte/schriften.py`, byte-reproduzierbar, `--pruefen`).
- **Begründung:** Gleiche Dateinamen und eine Datei je Schnitt: `atlas.css`, `schaugrafik.js` (bettet genau drei
  Schlüssel ein) und `skripte/16_export.py` bleiben unverändert und gehören anderen Paketen. Polnische Seiten
  brauchen latin-ext immer, ein getrenntes Nachladen per `unicode-range` spart dort nichts. Die Glyphen sind die der
  Autoren; nur die Teilmengen werden vereint (OFL erlaubt Änderungen, `fonts/OFL.txt` nennt keinen Reserved Font
  Name). DESIGN.md (Barlow) bleibt gültig.
- **Verworfen:** (a) unveränderte Fontsource-Dateien mit zweitem `@font-face` und `unicode-range` – bytegleich mit
  dem Paket, aber Änderungen in `atlas.css`, `schaugrafik.js` und `16_export.py` (fremdes Eigentum) und zwei Abrufe
  je Schnitt; (b) Noto Sans für die Oberfläche (wäre ein Bruch mit DESIGN.md); (c) Barlow-TTF aus dem
  Google-Fonts-Repository auf GitHub (GitHub ist in `skripte/abruf.py` gesperrt); (d) `npm install` (Netz außerhalb
  des Abrufwerkzeugs).
- **Grenze (gemessen, `pruefen/DF_kerning.py`, Beleg Abschnitt 1):** Kerning über die Teilmengen hinweg fehlt. Von
  1.664 Paaren je Schnitt (16 Zeichen aus Latin Extended-A × a–z, A–Z, beide Reihenfolgen) hat keines einen Wert;
  bei 276 bis 332 Paaren je Schnitt kernt der Grundbuchstabe, bei 61 bis 103 davon um mindestens 20 Einheiten
  (größte: „YĄ“, „WĄ“, „VĄ“, „ŁT“ bis 109 Einheiten, „Tę“, „Tć“ bis 79). Im Fließtext kaum sichtbar, in großen
  Versal-Überschriften (etwa „WĄWÓZ“) schon. Variante (a) behebt das nicht: Über zwei Schriftdateien hinweg kernt
  kein Browser.
- **Offen (Vorschlag, nicht umgesetzt):** (1) Barlow vollständig aus der Quelle der Autoren (GitHub, heute in
  `skripte/abruf.py` gesperrt; Freigabe durch die Projektleitung) statt der Fontsource-Teilmengen; oder (2) in
  `skripte/schriften.py` die Kerning-Klassen der Grundbuchstaben auf die polnischen Zeichen übertragen
  (abgeleitet, nicht gezeichnet; OFL erlaubt es, wäre aber eine typografische Entscheidung). Bis dahin bleibt der
  Verlust als Grenze stehen.
- **Neu prüfen, wenn:** Fontsource eine Datei mit beiden Teilmengen anbietet oder GitHub als Quelle freigegeben ist.

## fontTools und brotli als Werkzeug (Vorschlag an das Paket Infrastruktur)

- **Anlass:** Erzeugung und Glyphenprüfung brauchen fontTools (Zusammenfügen, cmap) und brotli (WOFF2). Beide
  stehen nicht in `requirements.txt`; im lokalen uv-Zwischenspeicher liegen `fonttools 4.68.0` und `brotli`, daher
  laufen beide Skripte mit `uv run --offline … --with fonttools==4.68.0 --with brotli` ohne Netz.
- **Entscheidung (Vorschlag, umgesetzt):** `fonttools==4.68.0` und `brotli==1.2.1` mit Hashes in der eigenen Datei
  `requirements-schriften.txt` (aus `requirements-schriften.in`, offline aus dem Zwischenspeicher erzeugt),
  Eigentümer Paket Infrastruktur. `requirements.txt` bleibt unverändert; `pruefen.sh` nimmt die Datei für die
  beiden Schriftschritte dazu.
- **Verworfen:** ohne fontTools nur mit Pillow/FreeType prüfen (Pillow zeigt Ersatzzeichen, nicht die cmap; die
  Prüfung soll die Zeichentabelle lesen, wie im Auftrag verlangt).

## `themen.js`: relative Pfade der Grundkarte auflösen, Quellen null weglassen (Vertragsänderung)

- **Anlass:** Offen aus KR21: Ohne Auflösung relativer URLs zeigt keine Atlas-Seite die eigene Grundkarte (MapLibre
  4.7.1 lädt Kacheln im Worker und kann relative URLs nicht auflösen). Außerdem setzen `atlas.js`, `karte.js` und
  `jahre.js` `dop: KIEZ_ORT.karte.luftbild` in die Quellen; mit `luftbild: null` lehnt MapLibre den Stil ab.
- **Entscheidung (Vorschlag):** In `themen.js`:
  1. Die Atlas-Wurzel ist der Ordner über `daten/` des tatsächlich geladenen `<script src=…daten/grundkarte.js>`.
     Gesucht wird über `document.scripts` nach dem Pfad ohne Abfrageteil, damit ein `?v=` aus dem Deploy nicht
     stört (der Vorschlag in `docs/entscheidungen/D8.md` mit `script[src$="daten/grundkarte.js"]` hätte mit `?v=`
     nicht mehr gegriffen, also nur auf dem Server versagt).
  2. Relative Kachel- und Schriftpfade werden darauf bezogen absolut; absolute URLs (Potsdam, basemap.de) bleiben.
  3. Unter file:// (oder ohne gefundenes Skript) entfällt eine Grundkarte mit relativen Pfaden: Die Ebene
     `basemap` bleibt als unsichtbarer Platzhalter, nichts wird geladen, kein Fehler. Die übrige Karte bleibt; der
     Stil hat dann keine Schrift (glyphs), Beschriftungsebenen mit `text-field` gehen unter file:// nicht.
  4. Eine Quelle `null` wird entfernt, ihre Ebenen werden zu unsichtbaren Platzhaltern gleichen Namens (Typ
     `background`), damit `setLayoutProperty("dop", …)` in den Modulen keinen Fehler auslöst.
- **Begründung:** Daten bleiben sprachneutral und ohne Rechnernamen; die Potsdamer Gegenprobe ändert sich nicht
  (absolute URLs, Luftbild vorhanden). Ohne Punkt 4 hätte jede Kraków-Seite mit Karte einen Stilfehler.
- **Belegt:** `pruefen/DF_grundkarte.mjs` Teile 1 und 2 (Beleg Abschnitt 2); Gegenprobe Potsdam (Beleg Abschnitt 4).
- **Verworfen:** `location.href` als Basis (falsch in `en/`, `de/`); Auflösung in `daten/grundkarte.js` (Code in
  Daten); `luftbild` mit einer leeren Rasterquelle füllen (MapLibre verlangt Kacheln); die Ebene `dop` ganz
  entfernen (dann Fehler bei jedem Schalten).
- **Nachbesserung Luftbild-Schalter:** `grundLuft(map, true)` blendete die Flächen und Linien der Grundkarte aus,
  ohne dass ein Luftbild darunter lag (leere Karte mit Beschriftungen). Jetzt tut `grundLuft` nichts, solange
  `karte.luftbild` null ist; `KIEZ_THEMEN.LUFTBILD` (false) erlaubt den Modulen, den Schalter auszublenden.
  `pruefen/DF_grundkarte.mjs` Teil 4 prüft, dass nach dem Schalten alle Flächen- und Linienebenen sichtbar bleiben.
- **Offen für die Seitenpakete:** Den Schalter in `karte.js`, `atlas.js`, `jahre.js` mit `KIEZ_THEMEN.LUFTBILD`
  ausblenden.
- **Neu prüfen, wenn:** MapLibre relative URLs selbst auflöst oder es ein Luftbild gibt.
- **Bestätigung durch die Integration nötig** (Vertragsänderung `themen.js`).

## `karte.grundkarte` in `config/krakow.yaml`

- **Entscheidung (Vorschlag, umgesetzt):** wie in `docs/entscheidungen/D8.md` vorgeschlagen: Vektorquelle mit
  `tiles: ["daten/grundkarte/kacheln/{z}/{x}/{y}.pbf"]`, z9 bis z14, Bildzeile wörtlich wie in
  `daten/grundkarte.js`. `luftbild` bleibt `null`. `daten/ort.js` neu erzeugt (`31_ort.py --pruefen` ok).
- **Begründung:** `themen.js` ersetzt diese Quelle durch `daten/grundkarte.js`; die Angabe beschreibt dieselben
  Kacheln, damit die Bildzeile auch ohne Ersatz stimmt.
- **Auflage für die Seitenpakete:** Jede Seite mit Karte lädt `daten/grundkarte.js` vor `themen.js`; sonst steht eine
  Rasterebene auf einer Vektorquelle (Stilfehler). `pruefen/DF_grundkarte.mjs` Teil 4 prüft das.

## Bereitstellung der Kacheln für Entwicklung und Deploy

- **Anlass:** Kacheln und Kartenschrift liegen außerhalb des Repos (KR21), 397 ausgelieferte Dateien, 6.959.078 B
  (gzip -9 der `.pbf` zusammen 4.953.950 B; Beleg Abschnitt 2).
- **Entscheidung (Vorschlag):**
  - **Entwicklung:** `node skripte/entwicklung_server.mjs [--port 8080]` liefert die Atlas-Wurzel auf 127.0.0.1
    und hängt unter `daten/grundkarte/` den Kachelordner `$KIEZ_DATEN/abgeleitet/grundkarte/<SHA-Anfang>/` ein
    (SHA aus `skripte/27_grundkarte.py`, wie die Sichtprobe). Kein Symlink und kein Eintrag in `.gitignore` nötig.
  - **Deploy (umgesetzt in `skripte/deploy_kopie.py`, Bestätigung durch das Paket Deploy nötig):** Sobald eine
    Seite `daten/grundkarte.js` lädt, kopiert das Skript `kacheln/` und `schrift/` (mit `schrift/OFL.txt`) aus
    demselben Ordner (oder `--grundkarte ORDNER`) nach `daten/grundkarte/` der Auslieferung, prüft jede Datei gegen
    `MANIFEST.sha256` und `MANIFEST.sha256` gegen `lauf.json`, und bricht ab, wenn der Ordner fehlt. Die Dateien
    stehen in `MD5SUMS`. Probelauf am 13.11.2026 (Beleg Abschnitt 2): 397 Dateien Grundkarte (387 Kacheln,
    6.002.076 B; 10 Schriftdateien, 957.002 B), Kopie insgesamt 509 Dateien, 9.854.992 B; ohne Kachelordner
    Abbruch vor dem Kopieren. Webserver: `.pbf` mit `Content-Type: application/x-protobuf`, gzip erlaubt.
- **Verworfen:** Kacheln ins Repo (KR21); Symlink `daten/grundkarte` im Repo (zeigt auf jedem anderen Rechner ins
  Leere und gerät leicht in den Deploy-Abzug).
- **Neu prüfen, wenn:** das Deploy ohne Zugriff auf `kiezatlas-daten` laufen muss.

## Startgewicht des Planers

- Gemessen (Beleg Abschnitt 3): `planer.html` heute 13.117 B gz (ohne Karte); mit Karte gerechnet 248.703 B gz,
  davon Grundkarte `daten/grundkarte.js` 1.407 B gz (Potsdam brauchte für `daten/grundkarte.js` laut
  Kommentar in seiner Planerprüfung rund 16 KB gz). Der gemeinsame Code `kopf.js` + `themen.js` + `planer.js`
  wiegt laut Gegenprobe 23.213 B gz gegen 23.886 B in Potsdam; Bedingung 3 der Ausnahme für das Startgewicht hält mit
  673 B Abstand. Das Startgewicht der Gegenprobe steigt von 327 auf 328 KB gz (Mehrlast aus `themen.js`); die
  Auflage, live unter 320 KB gz zu bleiben, trägt weiter das Paket Deploy.
- **Hinweis:** Die Grenze für den Krakauer Planer legt das Seitenpaket fest (Entscheidung zum Startgewicht).

## Hinweise an die Belegschicht

- `pruefen.sh`: Schritte „Schriften (`pruefen/DF_schriften.py`, `skripte/schriften.py --pruefen`)“ mit
  `requirements-schriften.txt` und „Grundkarte auf den Kartenseiten (`node pruefen/DF_grundkarte.mjs`)“ sind
  eingetragen (ohne Kachelordner meldet die Grundkarten-Prüfung die Kachelteile als übersprungen, Rückgabe 0).
  Bitte bestätigen.
- `DESIGN.md`, Abschnitt Datenschutz und Veröffentlichung, nennt noch „fremd sind nur Kartenkacheln und Kartenschrift
  (basemap.de) und Luftbild (LGB)“; für Kraków sind Kacheln und Kartenschrift selbst gehostet, ein Luftbild gibt es
  nicht.
- `NOTICE` ist in den Schriftzeilen geändert (siehe oben); `QUELLEN.md` und `daten/LIZENZ.md` aus `quellen-DF.md`.
- `docs/rundgang.md`, Abschnitt „Übergabe an die Pakete“: Der Satz, dass die Kraków-Seiten die Kartenmodule bis zur
  Grundkarte nicht laden, ist zu ersetzen durch: Die Seite `karta` (pl, en, de) zeigt die Grundkarte über
  `kartenfeld.js`; die übrigen Seiten haben keine Kartenfläche, das Einbinden von `karte.js`/`planer.js` bleibt
  bei den Seitenpaketen; die Voraussetzung `karte.grundkarte` ist erfüllt, `karte.luftbild` bleibt
  `null` und wird von `themen.js` abgefangen.
