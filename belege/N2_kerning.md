# Kerning der polnischen Sonderzeichen (KR30)

Erzeugt am 14.11.2026 im Paket Oberfläche und Auslieferung (Zweig `Arbeitszweig n2`); Begründung in `docs/entscheidungen/N2.md`, Abschnitt 3.
Aufrufe ohne Netz, aus der Wurzel des Repos:

```sh
uv run --offline --python 3.13 --no-project --with-requirements requirements.txt \
    --with-requirements requirements-schriften.txt python -I skripte/schriften.py            # erzeugen
…  python -I skripte/schriften.py --pruefen   # byte-gleich nachrechnen
…  python -I pruefen/DF_kerning.py            # Messung
node pruefen/N2_auslieferung.mjs --nur kerning   # Textsatz im Browser
```

## 1. Dateien

| Datei | vorher (Byte, `acba5f7`) | nachher (Byte) | SHA256 nachher |
|---|---|---|---|
| `fonts/barlow-400-normal.woff2` | 28300 | 29208 | `279866f80929849aba518a4b6694ac0125968a896cac20f26eabac9627d02f65` |
| `fonts/barlow-500-normal.woff2` | 28160 | 29088 | `597bacf7ad93fdd8c77e25ef14cc784545c89abc233778ef334a627d26e2046f` |
| `fonts/barlow-600-normal.woff2` | 28956 | 29988 | `2446f5aaa0626c353041cf9d2815f1f415bcf8e858f35a9862bf3670d8ac4998` |
| `fonts/barlow-semi-condensed-500-normal.woff2` | 28508 | 29592 | `3946c9cf42abef88d2723389ee7dd74c54a359fc65ef3cabe4f8c60e457909ab` |
| `fonts/barlow-semi-condensed-600-normal.woff2` | 29156 | 30224 | `e6a9bea83992a39295d1d7cc9b3e171a6594c67e03778e681d5be901cbbc234f` |
| `fonts/einbettung.js` | 115554 | 119562 | `75d433bcb25019b9fec214794fd1825191cb81245d4e8dc8d888410aa8a0e76a` |

Byte-gleich nachgerechnet (`skripte/schriften.py --pruefen`):

```
ok  fonts/barlow-400-normal.woff2 (29208 B, sha256 279866f80929849aba518a4b6694ac0125968a896cac20f26eabac9627d02f65)
ok  fonts/barlow-500-normal.woff2 (29088 B, sha256 597bacf7ad93fdd8c77e25ef14cc784545c89abc233778ef334a627d26e2046f)
ok  fonts/barlow-600-normal.woff2 (29988 B, sha256 2446f5aaa0626c353041cf9d2815f1f415bcf8e858f35a9862bf3670d8ac4998)
ok  fonts/barlow-semi-condensed-500-normal.woff2 (29592 B, sha256 3946c9cf42abef88d2723389ee7dd74c54a359fc65ef3cabe4f8c60e457909ab)
ok  fonts/barlow-semi-condensed-600-normal.woff2 (30224 B, sha256 e6a9bea83992a39295d1d7cc9b3e171a6594c67e03778e681d5be901cbbc234f)
ok  fonts/einbettung.js (119562 B, sha256 75d433bcb25019b9fec214794fd1825191cb81245d4e8dc8d888410aa8a0e76a)
```

## 2. Messung mit `pruefen/DF_kerning.py`

Vorher (Schriften aus `acba5f7`):

```
Kerning der polnischen Sonderzeichen, 5 Schriften unter fonts/
barlow-400-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 0; Grundpaar mit Wert, polnisches Paar ohne: 276, davon |Wert| ≥ 20: 73
    größte: WĄ (wie WA: -93), VĄ (wie VA: -93), ŁT (wie LT: -91), YĄ (wie YA: -81), ĄY (wie AY: -72), Tę (wie Te: -70), Tć (wie Tc: -70), ĄT (wie AT: -65)
barlow-500-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 0; Grundpaar mit Wert, polnisches Paar ohne: 276, davon |Wert| ≥ 20: 81
    größte: YĄ (wie YA: -96), WĄ (wie WA: -96), VĄ (wie VA: -96), ŁT (wie LT: -88), ĄY (wie AY: -77), Tę (wie Te: -75), Tć (wie Tc: -75), ĄT (wie AT: -72)
barlow-600-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 0; Grundpaar mit Wert, polnisches Paar ohne: 277, davon |Wert| ≥ 20: 103
    größte: YĄ (wie YA: -109), WĄ (wie WA: -98), VĄ (wie VA: -98), ŁT (wie LT: -86), ĄY (wie AY: -82), Tę (wie Te: -79), Tć (wie Tc: -79), ĄT (wie AT: -78)
barlow-semi-condensed-500-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 0; Grundpaar mit Wert, polnisches Paar ohne: 332, davon |Wert| ≥ 20: 61
    größte: ŁT (wie LT: -79), WĄ (wie WA: -78), VĄ (wie VA: -78), YĄ (wie YA: -77), ĄT (wie AT: -66), Tę (wie Te: -66), Tć (wie Tc: -66), ĄY (wie AY: -60)
barlow-semi-condensed-600-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 0; Grundpaar mit Wert, polnisches Paar ohne: 328, davon |Wert| ≥ 20: 75
    größte: YĄ (wie YA: -86), WĄ (wie WA: -82), VĄ (wie VA: -82), ŁT (wie LT: -80), Tę (wie Te: -71), Tć (wie Tc: -71), ĄT (wie AT: -69), ĄY (wie AY: -65)
```

Nachher:

```
Kerning der polnischen Sonderzeichen, 5 Schriften unter fonts/
barlow-400-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 276; Grundpaar mit Wert, polnisches Paar ohne: 0, davon |Wert| ≥ 20: 0
    größte: 
barlow-500-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 276; Grundpaar mit Wert, polnisches Paar ohne: 0, davon |Wert| ≥ 20: 0
    größte: 
barlow-600-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 277; Grundpaar mit Wert, polnisches Paar ohne: 0, davon |Wert| ≥ 20: 0
    größte: 
barlow-semi-condensed-500-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 332; Grundpaar mit Wert, polnisches Paar ohne: 0, davon |Wert| ≥ 20: 0
    größte: 
barlow-semi-condensed-600-normal.woff2: 1000 Einheiten je Geviert, 1664 Paare gemessen; über die Teilmengen mit Wert: 328; Grundpaar mit Wert, polnisches Paar ohne: 0, davon |Wert| ≥ 20: 0
    größte: 
```

Lesart: „Grundpaar mit Wert, polnisches Paar ohne“ ist in allen fünf Schriften 0, die Lücke ist geschlossen. Die Zeile
„über die Teilmengen mit Wert“ zählt jetzt genau die übertragenen Paare unter den gemessenen (vorher 0, wie der Kopf
der Messung es für den alten Stand erwartet). Die Messung prüft nur, dass ein Wert da ist; dass er gleich dem des
Grundpaars ist, prüft `skripte/schriften.py` beim Erzeugen für jedes übertragene Paar und der Browser in Abschnitt 3.

## 3. Textsatz im Browser

`node pruefen/N2_auslieferung.mjs --nur kerning` (Chromium aus Playwright, Schriften über `atlas.css`, 1000 px, `lang="pl"`):

```

4. Kerning der polnischen Sonderzeichen im Browser
  ok    Barlow 400: 20 Paare kernen wie ihr Grundpaar (Schrift geladen: true); Beispiel ŁT -91.0 px = LT -91.0 px bei 1000 px; Grundpaar ohne Kerning (nur Hinweis): Tz Tz ZY
  ok    Barlow 500: 20 Paare kernen wie ihr Grundpaar (Schrift geladen: true); Beispiel ŁT -88.0 px = LT -88.0 px bei 1000 px; Grundpaar ohne Kerning (nur Hinweis): Tz Tz ZY
  ok    Barlow 600: 20 Paare kernen wie ihr Grundpaar (Schrift geladen: true); Beispiel ŁT -86.0 px = LT -86.0 px bei 1000 px; Grundpaar ohne Kerning (nur Hinweis): Tz Tz ZY
  ok    Barlow Semi Condensed 500: 20 Paare kernen wie ihr Grundpaar (Schrift geladen: true); Beispiel ŁT -79.0 px = LT -79.0 px bei 1000 px; Grundpaar ohne Kerning (nur Hinweis): ZY
  ok    Barlow Semi Condensed 600: 20 Paare kernen wie ihr Grundpaar (Schrift geladen: true); Beispiel ŁT -80.0 px = LT -80.0 px bei 1000 px; Grundpaar ohne Kerning (nur Hinweis): ZY
  ok    Kerning-Messung index.html: keine Konsolenfehler, Fehlabrufe oder Fremdabrufe

0 Befunde, 0 übersprungen
```

Gegenprobe mit den Schriften aus `acba5f7` (vorübergehend zurückgelegt, danach wieder erzeugt): dieselbe Prüfung meldet
5 Befunde, einen je Schnitt.
