# Prüfprotokoll Grundkarte (vor dem ersten Lauf festgelegt)

Stand 13.11.2026, festgelegt **bevor** `skripte/27_grundkarte.py` zum ersten Mal Kacheln schreibt. Was danach
geändert wird, steht mit Grund und Commit unten unter „Änderungen nach dem Lauf“. Ergebnisse:
`belege/D8_grundkarte.md`.

## Gegenstand

Eigene Vektorkacheln (Mapbox Vector Tile 2.1, Web-Mercator EPSG:3857, Ordner `{z}/{x}/{y}.pbf`) und eigene
Kartenschrift (SDF-Glyphen im MapLibre-Format) für die Grundkarte des Atlas. Quelle der Geometrie nur BDOT10k,
Paket Powiat 1261 (Miasto Kraków), GUGiK. Kein OpenStreetMap (Dateigrenze ODbL, `pruefen/daten.py` Punkt 4),
kein Abruf von GUGiK-Kartendiensten (WMTS/WMS: „harvesting“ verboten).

## Regeln, die der Lauf erfüllen muss

| Nr | Regel | geprüft von |
|---|---|---|
| G1 | Eingabe ist genau die Datei mit der in `skripte/27_grundkarte.py` hinterlegten SHA256 (Abweichung = Abbruch, kein Weiterrechnen mit anderem Stand) | Skript (Abbruch), `pruefen/D8_grundkarte.py` (Manifest) |
| G2 | Koordinatensystem der Quelle wird aus der `.prj` jeder Schicht gelesen, nicht fest eingetragen; alle Schichten haben dasselbe | Skript (Abbruch) |
| G3 | Jede Kachel ist gültiges MVT: dekodierbar, Version 2, Ausdehnung 4096, nur Befehle MoveTo/LineTo/ClosePath, Polygon-Außenringe mit positiver Fläche (Y nach unten), Innenringe negativ | `pruefen/D8_grundkarte.py` (eigener Dekoder, jede Kachel) |
| G4 | Kachelsatz deckt `karte.rahmen` aus `config/krakow.yaml` in allen Zoomstufen lückenlos ab (jede Kachel im Rahmen vorhanden, auch leere) | `pruefen/D8_grundkarte.py` |
| G5 | Keine Kachel größer als 500 KB (Richtwert für die Ladezeit am Handy, Herkunft der Zahl nicht geprüft) | `pruefen/D8_grundkarte.py` |
| G6 | Nur Schichten und Attribute laut Liste im Skript; kein Gebäude, keine Adresse, keine Kennung (`LOKALNYID`, `IDULIC` …), keine Personendaten | `pruefen/D8_grundkarte.py` (Attributschlüssel je Schicht) |
| G7 | Polnische Namen unverändert aus der Quelle (UTF-8, Diakritika); Stichprobe: mindestens ein Straßenname mit ń, ł, ó, ś, ż oder ą in den Kacheln | `pruefen/D8_grundkarte.py` |
| G8 | Kartenschrift enthält alle 18 polnischen Sonderzeichen (ą ć ę ł ń ó ś ź ż und groß) als eigene Glyphe, nicht als Ersatzzeichen | `pruefen/D8_grundkarte.py` (Glyphen-PBF dekodiert, Bitmap ≠ Ersatzzeichen) |
| G9 | Jedes Zeichen, das in einem Namen der Kacheln vorkommt, steht in der Kartenschrift | `pruefen/D8_grundkarte.py` |
| G10 | Zwei Läufe mit derselben Eingabe ergeben byte-gleiche Kacheln und Glyphen (Manifest-SHA256 gleich) | Skript `--pruefen` gegen das Manifest |
| G11 | `daten/grundkarte.js` erfüllt `daten/schema/grundkarte.json`, enthält weder „OpenStreetMap“ noch „ODbL“ und nennt die Quelle (GUGiK, BDOT10k) | `pruefen/daten.py`, `pruefen/D8_grundkarte.py` |
| G12 | Jede Ebene im Stil verweist nur auf vorhandene Quellschichten und Schriftstapel | `pruefen/D8_grundkarte.py` |
| G13 | Sichtprobe im Browser (MapLibre 4.7.1 aus `vendor/`, nur 127.0.0.1): Karte zeichnet, polnische Beschriftung lesbar, keine Konsolenfehler, kein Abruf außerhalb 127.0.0.1 | `skripte/27_grundkarte_vorschau.mjs` (Bildschirmfoto im Beleg) |

Zählungen, die der Beleg nennen muss (nur gemessen, keine Schätzung): gelesene Objekte je BDOT10k-Schicht,
übernommene Objekte je Kartenschicht nach Filter, Objekte je Zoomstufe, Zahl der Kacheln je Zoomstufe (davon leer),
Bytes je Zoomstufe und gesamt, größte Kachel, Zahl der Glyphen je Schriftstapel und Bereich, Laufzeit.

## Ausdrücklich nicht geprüft

- Lagegenauigkeit der BDOT10k-Geometrie (übernommen, wie geliefert; Maßstab 1:10 000).
- Vollständigkeit der Straßennamen in BDOT10k gegen das amtliche Straßenregister (TERYT ULIC).
- Darstellung in anderen Browsern als Chromium (Playwright).
- Alles außerhalb von Powiat 1261: Der Rahmen der Karte reicht über die Stadtgrenze hinaus, dort bleibt die
  Grundkarte leer.

## Änderungen nach dem Lauf

Erster voller Lauf mit dem Skriptstand `bce3bb3`, Ergebnis committet in `5d44ce9`. Ein früherer, abgebrochener Lauf
(Nutzungslimit) hatte `daten/grundkarte.js` schon einmal geschrieben; seine Kacheln lagen nicht mehr vor, er geht in
keinen Beleg ein. Danach geändert (keine Regel G1 bis G13 gelockert):

| Commit | Änderung | Grund | Wirkung auf die Kacheln |
|---|---|---|---|
| `607bf62` | Linienbreiten im Stil: `["zoom"]` nur im obersten `interpolate`, `match` je Stufe | Sichtprobe G13: MapLibre lehnt den Stil ab („Only one zoom-based "step" or "interpolate" subexpression may be used in an expression“), Karte bleibt leer | keine (nur `daten/grundkarte.js`) |
| `607bf62` | Straßennamen: Merkmal (al., pl., rondo …) nicht davorsetzen, wenn es ausgeschrieben schon im Namen steht | Sichtprobe zeigte „al. Aleja Adama Mickiewicza“; betrifft 876 Straßenabschnitte (Beleg Abschnitt 3) | Namen in z13 und z14 kürzer, Manifest neu |
| `607bf62` | Vorschau macht Kachel- und Schrift-URL absolut, bezogen auf den Ort von `daten/grundkarte.js` | MapLibre 4.7.1 löst relative URLs im Worker nicht auf („Failed to parse URL“); Vorschlag für `themen.js` in `docs/entscheidungen/D8.md` | keine. **G13 gilt damit für die Vorschau, nicht für die Atlas-Seiten**, solange `themen.js` die Auflösung nicht übernimmt |
| `607bf62` | `pruefen/D8_grundkarte.py`: fehlende Datei im Manifest ist ein Befund statt Absturz | Gegenprobe mit absichtlich beschädigtem Kachelordner brach mit FileNotFoundError ab | keine |
| `3753299` | `schrift/OFL.txt` (Copyright aus der Schriftdatei, Wortlaut OFL 1.1) wird mitgeschrieben und geprüft | Glyphen sind aus Noto Sans abgeleitet, die OFL verlangt Lizenz und Copyright bei der Weitergabe | neue Textdatei neben den Glyphen, Manifest (nur `.pbf`) unverändert |
