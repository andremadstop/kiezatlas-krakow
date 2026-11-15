# Beleg: Langtexte der Methoden- und Datenseiten

Quelltexte `texte/<lang>/bloecke/quelle/*.html` (Polnisch zuerst geschrieben, Englisch und Deutsch daraus), erzeugt zu
`texte/<lang>/bloecke/*.html` von `skripte/16_bloecke_krakow.py`; die Seiten setzt `skripte/30_seiten.py` zusammen.
Regeln vorab: `pruefen/S4_protokoll.md` (Commit `b20d6ba`). Prüfung: `pruefen/S4_bloecke.py`.

## Blöcke

Zahl der Datenfelder (`data-feld`, je Platzhalter eins) abgelesen aus den erzeugten Blöcken; in allen drei Sprachen
dieselben Felder (geprüft).

| Block | Seite | Datenfelder je Sprache | Inhalt |
|---|---|---:|---|
| `metoda` | `metoda.html` (neu) | 24 | Grundsätze, Methode je Thema (Gliederung und Bevölkerung, Gebäude und 3D, Erreichbarkeit, Klima, Luft, Wohnungsmarkt, Pünktlichkeit, Denkmale und ZBK, Grundkarte), Grenzen, Nicht geprüft, KI-Offenlegung |
| `dane` | `dane.html` (neu) | 19 | Downloads mit Hinweis Dezimalkomma, Bedeutung der Felder (`pola.csv`, `wartosci.csv`), Lizenzen, Datenquellen mit wörtlichen Vermerken, Zitierhinweis, Meldeweg |
| `kamienice_metoda` | `kamienice-metoda.html` | 51 | Gebäude aus BDOT10k, Begriff Kamienica, Denkmale aus Register und OSM, Sanierungsatlas (ZBK-Liste, Datenschutz, Verortung mit Wilson-Intervall), Typologie als Schätzung |
| `kamienice_dane` | `kamienice-dane.html` | 7 | Datendateien des Themas, Downloads, Vermerke |
| `planer_metoda` | `planer-metoda.html` | 40 | Zellen und Einwohner, Einrichtungen (Zählungen aus den Daten), Luftlinie und Fußweg, Schulwege nach Prawo oświatowe (Wortlaut aus `config/richtwerte.yaml`), Taktklassen, Grün, Grenzen |
| `planer_dane` | `planer-dane.html` | 4 | Datendateien des Planers, Downloads, Vermerke |

Umfang ohne Markup und mit jedem Platzhalter als ein Wort: Polnisch 3050, Englisch 3550, Deutsch 3152 Wörter
(`wc -w`, erster Lauf). Nachbesserung 14.11.2026, gezählt als `sed -e 's/<[^>]*>/ /g' texte/<lang>/bloecke/quelle/*.html
| wc -w` (Platzhalter als Text): vorher (Commit `9558378`) pl 3124, en 3621, de 3226; nachher pl 3196, en 3705,
de 3295 (Abschnitt Pünktlichkeit, Zeile zu `pola.csv`/`wartosci.csv`).

## Wie Zahlen in den Text kommen

- Jede Zahl ist ein Platzhalter `[[datei:pfad|format]]` auf eine Datei unter `daten/` oder auf `config/richtwerte.yaml`
  (Richtwerte mit Fundstelle und eigene Festlegungen wie der Radius von 500 m für Haltestellen). Listen werden über
  Filter angesprochen, die genau ein Element treffen müssen (z. B. die Kennzahl mit Art `szkola` und Richtwert
  3000 m), nicht über die Stelle in der Liste; Zählungen über Filter mit dem Format `anzahl`.
- Formatiert wird mit `i18n.js` selbst (Node.js, `Intl.NumberFormat` der Sprache), wie auf den Seiten.
- Aus Beispieldateien darf nur Text kommen oder eine Zahl aus den Teilen, die dort echt sind (`powietrze.js`:
  Grenzwerte und Beschluss; `mieszkania.js`: Regeln mit der Mindestfallzahl); sonst bricht der Generator ab.
- Im Polnischen stehen Zählungen nach einem Doppelpunkt oder als „Bezeichnung: Zahl“, damit sich die Pluralform nicht
  mit den Daten ändern muss.

## Prüfungen

- `python -I pruefen/S4_bloecke.py`: 0 Befunde (111 Einzelprüfungen): Blöcke aktuell, gleiche Datenfelder in pl, en,
  de; keine Ziffer außerhalb der Datenfelder außer den begründeten Kennungen der Liste `ERLAUBT`; keine Treffer der
  Falschsatz-Listen `pruefen/d3_falschsaetze.json` und `pruefen/S4_falschsaetze.json`; in pl und en keine Wörter der
  deutschen Wortliste; keine Plankennungen und keine Pfade zu einzelnen Belegen; nur bekannte Platzhalter; Verweise
  auf vorhandene Downloads und Seiten.
- `python -I pruefen/texte.py` und `pruefen/geruest.py` nach `skripte/30_seiten.py`: 0 Befunde.
- `./pruefen.sh` mit Browser auf Commit `9d4bebf`: 45 Prüfungen, 38 grün, 0 Befund, 7 übersprungen; darin
  `pruefen/seiten.mjs` grün für die vier bestehenden Methoden- und Datenseiten in allen Sprachen.
- Probe der neuen Seiten `metoda` und `dane`: Wegwerf-Arbeitskopie von Commit `dcbb4d1` mit
  `docs/entscheidungen/S4/neue-seiten.patch` und den Blöcken von `9d4bebf`, danach `skripte/31_ort.py`,
  `skripte/30_seiten.py` (51 Seiten, 17 × 3 Sprachen), `pruefen/texte.py`, `pruefen/hreflang.py`, `pruefen/geruest.py`,
  `skripte/31_ort.py --pruefen`: je 0 Befunde; `node pruefen/seiten.mjs`: 508 ok, 0 FEHLT, Ergebnis „grün“
  (Grundkarte dort übersprungen, weil die Kopie keinen Kachelordner neben sich hat). Ein früherer Lauf ohne die
  Listenklasse `quellen` fand bei 360 px seitlichen Überstand auf den Datenseiten (11, 36 und 214 px); behoben in
  `9d4bebf`.

- Nachbesserung 14.11.2026: Seiten `metoda` und `dane` im Zweig angelegt (`docs/entscheidungen/S4.md`, S4-3).
  `./pruefen.sh` mit Browser auf Commit `fae0ace`: 45 Prüfungen, 38 grün, 0 mit Befund, 7 übersprungen; darin
  `pruefen/seiten.mjs` grün für alle 51 Seiten. Eigener Playwright-Lauf über `metoda` und `dane` in pl, en, de bei
  1280 und 390 px: 0 Konsolenfehler, 0 Fehlabrufe, 0 px seitlicher Überstand, axe (wcag2a, wcag2aa) ohne Verstoß, alle
  internen Links erreichbar (4 bzw. 12 je Seite), Tastaturfokus sichtbar (2 px solid); in pl und en kein deutsches Wort
  außer der Rechtsform „UG (haftungsbeschränkt)“ im Firmennamen der Zitierzeile.

- Zweite Nachbesserung 14.11.2026: Jeder der sechs Blöcke löst mindestens einen Platzhalter aus einer `_odbl`-Datei
  auf und endet jetzt in jeder Sprache mit dem ODbL-Vermerk (`kern.odbl`, Link auf openstreetmap.org/copyright).
  Gezählt in den erzeugten Seiten (`grep -c "openstreetmap.org/copyright"`): `metoda`, `planer-metoda`,
  `kamienice-metoda` je 1 Treffer in pl, en, de (vorher 0); `dane` 3, `planer-dane` 2, `kamienice-dane` 2 (Vermerk am
  Block plus Vermerke im Text). Die 3D-Ansicht der Gebäude steht in `metoda` und `kamienice-metoda` im Futur („noch
  nicht veröffentlicht“), ein neuer Falschsatz fängt die alten Sätze ab. `python -I pruefen/S4_bloecke.py`: 148 ok,
  0 Befunde, davon 36 zur neuen Regel 8 (18 Blöcke, 18 Seiten). `./pruefen.sh` mit Browser auf Commit `2f311f0`:
  46 Prüfungen, 39 grün, 0 mit Befund, 7 übersprungen; die Prüfungen des Pakets (`16_export_krakow.py --pruefen`:
  42 Dateien, 0 Abweichungen; `S4_export.py`: 4646 ok, 0 Befunde; `16_bloecke_krakow.py --pruefen`; `S4_bloecke.py`)
  ruft `pruefen.sh` noch nicht auf (Vorschlag S4-4), sie liefen einzeln im uv-Umfeld von `pruefen.sh` auf Commit
  `cf537d5` grün, ebenso `30_seiten.py --pruefen`.

## Grenzen

- Die Seiten `metoda` und `dane` stehen in der Themenliste der Startseite, nicht in Navigation oder Seitenfuß
  (Entscheidung der Integration).
- Zur Ausnahme III/XV bei der Zuordnung zu den delegatury nennt die Methodenseite die Zahlen 98,53 % und 98,64 % nicht:
  Sie stehen in den Datendateien nur im deutschen Satz `hinweis` von `steckbrief_dzielnice_odbl.js`, nicht als Feld.
  Ein Feld dafür ist Sache des Datenpakets Gliederung.
- Polnisch und Englisch sind nicht von Muttersprachlern gelesen.
- Lizenzvermerke in der Originalsprache stehen wörtlich aus den Daten; der OSM-Vermerk ist in pl und en als
  „© OpenStreetMap contributors“ geschrieben, weil die Datendateien ihn nur deutsch tragen
  („© OpenStreetMap-Mitwirkende“).
