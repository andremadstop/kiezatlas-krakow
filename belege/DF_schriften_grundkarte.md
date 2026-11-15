# Beleg Schrift und Grundkarten-Anbindung (13.11.2026)

Erzeugt von: `skripte/schriften.py` (Schriften), `pruefen/DF_schriften.py` (Glyphen, fontTools),
`pruefen/DF_grundkarte.mjs` (Browser). Alle Zahlen unten sind Ausgaben dieser Läufe oder mit dem genannten Befehl
nachgezählt, Stand Zweig `Arbeitszweig df`.

## 1. Schriften

### Vorher

Die fünf Dateien unter `fonts/` waren byte-gleich mit den Teilmengen `latin` von Fontsource 5.3.0 (Vergleich
SHA256 je Datei gegen `package/files/<paket>-latin-<schnitt>.woff2` aus den Paketen). Abdeckung der 18 polnischen
Sonderzeichen `ąćęłńóśźżĄĆĘŁŃÓŚŹŻ` je Datei laut cmap (fontTools 4.68.0):

| Datei | vorhanden | fehlend |
|---|---|---|
| `barlow-400-normal.woff2` | 2 | ąćęłńśźżĄĆĘŁŃŚŹŻ |
| `barlow-500-normal.woff2` | 2 | ąćęłńśźżĄĆĘŁŃŚŹŻ |
| `barlow-600-normal.woff2` | 2 | ąćęłńśźżĄĆĘŁŃŚŹŻ |
| `barlow-semi-condensed-500-normal.woff2` | 2 | ąćęłńśźżĄĆĘŁŃŚŹŻ |
| `barlow-semi-condensed-600-normal.woff2` | 2 | ąćęłńśźżĄĆĘŁŃŚŹŻ |

### Nachher

Je Schnitt latin + latin-ext aus demselben Paket mit `fontTools.merge` zusammengefügt. `fpgm`, `prep`, `cvt ` und
`gasp` sind in beiden Teilmengen gleich, für alle fünf Schnitte; `skripte/schriften.py` bricht sonst ab. Glyphen: latin 272 + latin-ext 234 = 506 nach dem
Zusammenfügen (Barlow 400).

| Datei | Byte vorher | Byte nachher | SHA256 nachher | polnische Zeichen |
|---|---|---|---|---|
| `barlow-400-normal.woff2` | 22.196 | 28.300 | `0279f5a9968d0ebba6cc7fe17076fb200d04362c93ce1f4481527f3c1d31802d` | 18 von 18 |
| `barlow-500-normal.woff2` | 22.008 | 28.160 | `5e171be17d211b033f970e6054422c3d98cc440c490927bf48fed59afc877de5` | 18 von 18 |
| `barlow-600-normal.woff2` | 22.772 | 28.956 | `8cc6b1bbe251933ebe249a852bbf075e09251a67202d592052c79aa5df9bea59` | 18 von 18 |
| `barlow-semi-condensed-500-normal.woff2` | 22.428 | 28.508 | `461811ce1a0289aaff99b2cd5872dbf3a58486f0fb805b7bd866664f06d93f9e` | 18 von 18 |
| `barlow-semi-condensed-600-normal.woff2` | 22.984 | 29.156 | `476cddbbf16e102c16f2fd4f800f6a53db716149f0f66830c85c74e109f85b1f` | 18 von 18 |
| `einbettung.js` (Schaugrafik, drei Schnitte als Data-URI) | 90.917 | 115.554 | `29f4ab2b229402ae268e09d55d587a3c027ac0d46d6e3b6339b8a76920c269f0` | je 18 von 18 |

Zusammen 112.388 B vorher, 143.080 B nachher (+30.692 B, WOFF2 ist schon komprimiert). Eine Seite lädt nur die
Schnitte, die sie verwendet.

Reproduzierbar: `skripte/schriften.py --pruefen` meldet alle sechs Dateien byte-gleich. Dafür übernimmt das Skript
`head.created` und `head.modified` aus der latin-Datei; ohne das setzt `fontTools.merge` beide auf die Laufzeit
(gemessen: drei Läufe, drei verschiedene SHA256).

### Prüfungen

- `pruefen/DF_schriften.py` (fontTools): 5 eingebundene Dateien (aus `atlas.css` und `skripte/16_export.py`,
  kein `unicode-range`), je 18 von 18 Zeichen mit cmap-Eintrag und Umriss; 3 eingebettete Schriften je 18 von 18 und
  byte-gleich mit den Dateien; OFL und Copyright vorhanden; Gegenprobe der Prüfung: eine Kopie ohne Latin
  Extended-A wird mit 16 fehlenden Zeichen erkannt. Ergebnis grün.
- `pruefen/DF_grundkarte.mjs`, Teil 3 (Chromium): Breite von „ąćęłńóśźżĄĆĘŁŃÓŚŹŻ“ in 40 px mit Ersatz monospace
  und mit Ersatz serif gleich, also kein Zeichen aus einer Ersatzschrift:

| Schrift | mit monospace | mit serif | nur monospace |
|---|---|---|---|
| Barlow 400 | 389,00 px | 389,00 px | 432,00 px |
| Barlow 500 | 395,00 px | 395,00 px | 432,00 px |
| Barlow 600 | 398,00 px | 398,00 px | 432,00 px |
| Barlow Semi Condensed 500 | 345,00 px | 345,00 px | 432,00 px |
| Barlow Semi Condensed 600 | 352,00 px | 352,00 px | 432,00 px |

  Gegenprobe derselben Messung mit der alten Datei `barlow-400-normal.woff2`: 414,00 px gegen 388,56 px, also
  ungleich (die Messung erkennt die Lücke).

### Kerning über die Teilmengen (Messung)

`pruefen/DF_kerning.py` (fontTools, Feature `kern`, PairPos Format 1 und 2), Lauf vom 13.11.2026. Gemessen je
Schnitt 1.664 Paare: jedes der 16 Zeichen aus Latin Extended-A mit a–z, A–Z in beiden Reihenfolgen. Verglichen wird
mit dem Paar der Grundbuchstaben (Ł→L, ż→z …); 1000 Einheiten je Geviert.

| Schrift | Paare mit Wert | Grundpaar mit Wert, polnisches Paar ohne | davon ≥ 20 Einheiten | größte Lücken (Einheiten) |
|---|---|---|---|---|
| Barlow 400 | 0 | 276 | 73 | WĄ, VĄ −93; ŁT −91; YĄ −81 |
| Barlow 500 | 0 | 276 | 81 | YĄ, WĄ, VĄ −96; ŁT −88 |
| Barlow 600 | 0 | 277 | 103 | YĄ −109; WĄ, VĄ −98; ŁT −86 |
| Barlow Semi Condensed 500 | 0 | 332 | 61 | ŁT −79; WĄ, VĄ −78; YĄ −77 |
| Barlow Semi Condensed 600 | 0 | 328 | 75 | YĄ −86; WĄ, VĄ −82; ŁT −80 |

Lesart: Keines der gemessenen Paare über die Teilmengen hat einen Kerning-Wert (die Grenze ist wie beschrieben).
Ob Barlow die polnischen Zeichen wie ihre Grundbuchstaben kernen würde, belegt die Messung nicht; die Werte des
Grundpaars sind eine Schätzung, wie groß die Lücke ist. Bei 32 px entsprechen 100 Einheiten 3,2 px. Betroffen sind
vor allem Versalpaare (YĄ, WĄ, ŁT) und T vor ę/ć.

## 2. Grundkarte auf den Seiten

Kachelordner (außerhalb des Repos, erzeugt vom Paket Grundkarte):
`kiezatlas-daten/krakow/abgeleitet/grundkarte/68b6ff47ed37/`

| Teil | Dateien | Byte | Byte gzip -9 (nur .pbf) |
|---|---|---|---|
| `kacheln/` (z9 bis z14) | 387 | 6.002.076 | 4.622.395 |
| `schrift/` (Noto Sans Regular, Medium, Italic, je 3 Bereiche, dazu `OFL.txt`) | 10 | 957.002 | 331.555 |
| ganzer Ordner mit `MANIFEST.sha256` und `lauf.json` | 399 | 6.998.577 | |

Gezählt mit `du -sb`, `find -type f | wc -l` und Python `gzip.compress(…, 9)` je Datei. Ausgeliefert werden
`kacheln/` und `schrift/` (397 Dateien, 6.959.078 B).

`pruefen/DF_grundkarte.mjs`, Lauf vom 13.11.2026, alle Teile grün:

- Teil 1, Prüfseite über HTTP in Wurzel, `en/` und `de/` (Rynek Główny, z14, 1000 × 700 px): je 8 Schichten der
  Grundkarte gezeichnet (miejsca 11, drogi 1.310, tory 163, sciezki 1.051, cieki 3, woda 6, zielen 17, teren 41
  Objekte), 88 Beschriftungen, davon 38 mit polnischem Sonderzeichen (z. B. „Nowa Wieś“, „Wesoła“); Kachel-URL
  absolut `…/daten/grundkarte/kacheln/{z}/{x}/{y}.pbf`, obwohl `daten/grundkarte.js` mit `?v=` geladen wurde;
  6 Kacheln und 6 Schriftbereiche geladen; Quelle `dop` (Luftbild null) entfernt, Schalter ohne Fehler; Bildzeile
  „Podkład: BDOT10k, Główny Urząd Geodezji i Kartografii (stan plików 2026-10-03), opracowanie własne“ im
  Bildzeilenfeld der Karte; keine Konsolenfehler, keine fehlgeschlagenen Abrufe, kein Abruf außerhalb 127.0.0.1.
- Teil 2, dieselbe Seite per file://: keine Quelle `bm`, Stadtteile gezeichnet (8 Objekte), keine Fehler.
- Teil 4 (Lauf nach der Nachbesserung): 45 von 45 erzeugten Seiten über HTTP ohne Konsolenfehler und Fehlabruf;
  3 Seiten laden `themen.js`, nämlich `karta.html`, `en/karta.html`, `de/karta.html` (über `kartenfeld.js`), jede
  lädt `daten/grundkarte.js` davor. Je Seite bei 1280 und 390 px: Karte mit eigener Grundkarte gezeichnet (610 bzw.
  319 Objekte, Quellen `teile`, `bm`), Bildzeilen sichtbar in der Karte „© OpenStreetMap (ODbL) | Podkład: BDOT10k,
  Główny Urząd Geodezji i Kartografii (stan plików 2026-10-03), opracowanie własne“, kein horizontaler Überlauf;
  nach dem Sprung zum Rynek Główny (z15) 46 bzw. 20 Beschriftungen, davon 16 bzw. 8 mit polnischem Sonderzeichen
  („Nowy Świat“, „Piotra Michałowskiego“, „św. Gertrudy“), 6 Schriftbereiche geladen; nach dem Luftbild-Schalter
  8 von 8 Flächen- und Linienebenen weiter sichtbar; keine Konsolenfehler, keine Fehlabrufe, nichts außerhalb
  127.0.0.1. Die übrigen 42 Seiten haben keine Kartenfläche (keine `#karte`, kein Kartenmodul).

Voller Prüflauf `./pruefen.sh` (mit Browser) auf `6b7792d`: 30 Prüfungen, 24 grün, 0 mit Befund, 6 übersprungen.
Der erste volle Lauf nach dem Einbinden der Karte fand 4 Befunde in `pruefen/seiten.mjs`: 404 auf Kacheln (deren
eigener Server kannte den Kachelordner nicht) und in `en/karta.html` axe `landmark-unique` (die Kartenfläche trug
die Region „Map“ wie die MapLibre-Fläche). Behoben in `45cb895` und `6b7792d`. Ohne Kachelordner (`KIEZ_DATEN` auf
einen leeren Ordner) laufen `seiten.mjs` und `DF_grundkarte.mjs` grün und melden die Kachelteile als übersprungen.

### Deploy-Kopie (Probelauf)

`skripte/deploy_kopie.py --mit-beispieldaten --unverkleinert` in einen Wegwerf-Ordner (Stand `97f3aa5`;
`--unverkleinert`, weil esbuild in diesem Arbeitsbaum nicht installiert ist): 111 Dateien Atlas plus 397 Dateien
Grundkarte (387 Kacheln, 6.002.076 B; 10 Schriftdateien, 957.002 B), zusammen 509 Dateien mit `MD5SUMS`,
9.854.992 B; `md5sum -c MD5SUMS` ohne Abweichung (508 Zeilen, davon 397 unter `daten/grundkarte/`);
`kartenfeld.js` und `kartenfeld.css` in der Kopie. Die Kopie über einen statischen Server auf 127.0.0.1
(`python3 -m http.server`) ausgeliefert: `karta.html`, `en/karta.html`, `de/karta.html` je 610 Objekte der
Grundkarte, 4 Kachelabrufe mit Status 200, Kachel-URL `…/daten/grundkarte/kacheln/{z}/{x}/{y}.pbf`, 0 Fehler,
0 Abrufe nach außen. Gegenprobe: mit `--grundkarte` auf einen fehlenden Ordner bricht das Skript vor dem Kopieren
ab („kein Kachelordner … MANIFEST.sha256 fehlt“), es entsteht kein Ziel.

## 3. Startgewicht des Planers

JavaScript beim Start, gzip -9 (zlib in Node, wie die Planerprüfung):

- `planer.html` wie erzeugt: 13.117 B gz, 7 Dateien (`daten/ort.js`, `i18n.js`, `texte/pl/kern.js`,
  `texte/pl/seiten.js`, `kopf.js`, `texte/pl/planer.js`, `rahmen.js`). Die Seite hat noch keine Karte.
- `planer.html` mit Karte, gerechnet aus der Ladeliste der Potsdamer `planer.html` auf die Krakauer Dateien
  übertragen: 248.818 B gz (243,0 KB; Lauf nach der Nachbesserung, `themen.js` mit Luftbild-Abfang), davon
  `vendor/maplibre-gl.js` 211.733, `planer.js` 16.251, `themen.js` 5.239,
  `texte/pl/planer.js` 3.938, `daten/ort.js` 2.539, `kopf.js` 1.901, `daten/grundkarte.js` 1.407, `rahmen.js` 1.342,
  `texte/pl/seiten.js` 1.242, `texte/pl/kern.js` 1.184, `daten/stadtteile_odbl.js` 1.071 (Beispieldaten),
  `i18n.js` 971. Ohne `daten/planungsraeume.js` (gibt es in Kraków nicht) und ohne Daten, die der Planer erst bei
  Bedarf lädt. Die Bauvorlage nennt für die Startseite 300 KB gz; eine Grenze für den Krakauer Planer legt das Paket
  der Seiten fest.
- Bedingung 3 der Ausnahme für das Startgewicht in der Gegenprobe (gemeinsamer Code nicht schwerer als in
  Potsdam): maßgeblich ist die Messung der Gegenprobe, 23.213 B gz gegen Potsdam 23.886 B gz, 673 B Abstand
  (Abschnitt 4). Eigene Nebenmessung mit dem Befehl `gzip -9` (andere Implementierung, darum leicht andere Werte):
  Potsdam `kopf.js` 1.886 + `themen.js` 4.475 + `planer.js` 17.492 = 23.853 B; dieser Zweig 1.909 + 5.119 + 16.149 =
  23.177 B (vor diesem Paket 22.385 B; `themen.js` +792 B).

## 4. Gegenprobe Potsdam

Lauf von `pruefen/gegenprobe_potsdam.sh` auf diesem Zweig, Commit `38bf1a4` (letzte Änderung an `themen.js`),
Protokoll `belege/DF_gegenprobe_potsdam-38bf1a4.log`: Rückgabe 0, „0 Abweichungen“. A6, A8, `seiten`, B5 und der
Textabzug (9 Seiten, 89.664 Byte) wie Potsdam; `A7_planer` mit der zugelassenen Ausnahme für das Startgewicht:
328 KB gz (vorher 327 KB gz im Lauf `13d7eba`, Mehrlast aus `themen.js`), gemeinsamer Code 23.213 B gz gegen
Potsdam 23.886 B gz (−673 B, Messung der Gegenprobe; der erste Lauf auf `eee6b25`, `belege/DF_gegenprobe_potsdam-eee6b25.log`, ergab 23.145 B, ebenfalls
0 Abweichungen), Textschicht 8.191 B gz zusätzlich wie zuvor.

Nach der Nachbesserung (`30_seiten.py`, Luftbild-Abfang in `themen.js`, `deploy_kopie.py`) erneut auf `97f3aa5`,
Protokoll `belege/DF_gegenprobe_potsdam-97f3aa5.log`: „0 Abweichungen“, alle Rückgaben gesetzt (A6 0, A8 1 wie
Potsdam, `seiten` 0 mit 120 × ok, `A7_planer` 1 mit 119 × ok und der Ausnahme für das Startgewicht 328 KB gz,
B5 0 mit 251 × ok, Textabzug 89.664 Byte gleich). Gemeinsamer Code 23.327 B gz gegen Potsdam 23.886 B gz (−559 B;
Mehrlast des Luftbild-Abfangs +114 B gegenüber `38bf1a4`). Ein früherer Lauf auf `d5c699d` wurde abgebrochen und
nicht als Beleg aufgenommen; dabei fiel auf, dass `gegenprobe_potsdam.sh` bei fehlenden Ergebnisdateien einzelne
Zeilen mit leerer Rückgabe als „ok … wie Potsdam“ meldet (die Gesamtzählung meldete trotzdem Abweichungen).

Nach der Änderung an `pruefen/seiten.mjs` und der Seite `karta` erneut auf `6b7792d`, Protokoll
`belege/DF_gegenprobe_potsdam-6b7792d.log`: „0 Abweichungen“, Rückgaben und Zählungen wie auf `97f3aa5`.

## Grenzen

- Eine Karte haben 3 von 45 Seiten: `karta` in pl, en und de (einfache Karte aus `kartenfeld.js`: Grundkarte und
  Stadtteile). `index`, `planer`, `kamienice`, `dzielnica` und die übrigen Seiten haben keine Kartenfläche; das
  Einbinden von `karte.js`, `planer.js` oder `atlas.js` in diese Seiten gehört den Seitenpaketen. Jede neue
  Kartenseite muss `daten/grundkarte.js` vor `themen.js` laden; `pruefen/DF_grundkarte.mjs` Teil 4 prüft das und
  zeichnet jede Seite mit `themen.js` als Kartenseite bei 1280 und 390 px.
- Unter file:// zeigen die Seiten keine eigene Grundkarte (MapLibre lädt dort keine Kacheln), nur die übrigen
  Ebenen. Für die Entwicklung: `node skripte/entwicklung_server.mjs`.
- Kerning zwischen Zeichen aus verschiedenen Teilmengen fehlt nach dem Zusammenfügen; gemessen in Abschnitt 1
  (bis 109 Einheiten bei Versalpaaren wie „YĄ“, „ŁT“). Eine Sichtprobe am Bildschirm steht aus.
- Die Glyphenprüfung im Browser lief nur in Chromium (Playwright), nicht in Firefox oder Safari.
