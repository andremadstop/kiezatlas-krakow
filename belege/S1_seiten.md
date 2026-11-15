# Seiten Erzählung, Karte, Steckbrief, Vergleich: Abnahme

Stand 14.11.2026, Zweig `Arbeitszweig s1`, Seiten und Module bei Commit `4dc995a`. Zählungen aus den Läufen unten; nichts von Hand gezählt.

## Läufe

| Prüfung | Ergebnis |
|---|---|
| `node pruefen/S1_seiten.mjs` (vier Seiten × pl/en/de: acht Fragen, alle Ebenen, 18 Steckbriefe, Vergleich, Quellen, 360 px) | 189 ok, 0 Befund(e), grün |
| `node pruefen/seiten.mjs` (alle 15 Seiten × 3 Sprachen, file:// und HTTP, axe, 360 px, Beispieldaten-Hinweis) | 450 × ok, 0 × FEHLT |
| `node pruefen/DF_grundkarte.mjs` (Grundkarte auf index, karta, dzielnica je Sprache, 1280 und 390 px) | grün; 9 Kartenseiten (index, karta, dzielnica je Sprache) |
| `./pruefen.sh --voll --gegenprobe` vor der letzten Änderung | alles grün außer Gegenprobe Potsdam (Namensraum `karte` fehlte in index/karta, behoben in `4dc995a`) |
| `pruefen/gegenprobe_potsdam.sh` nach der Behebung | 0 Abweichungen |
| `python -I skripte/41_porownanie.py --pruefen` | byte-gleich nachgerechnet |

## Kennzeilen aus `pruefen/S1_seiten.mjs`

```
ok    pl/index: 5 Kopfzahlen, jede mit Quelle (800 653 | 326,9 | 18 | 90 563 | 508)
ok    pl/index: Register mit 18 Zeilen und Zeile der Stadt, sortierbar, Quelle in der Unterschrift
ok    pl/index bei 360 px: kein waagerechtes Scrollen (0 px)
ok    pl/karta: 11 Zellebenen zur Wahl (ew, u15, 65p, fuss:haltestelle_takt, fuss:szkola, fuss:przedszkole, fuss:park, fuss:supermarkt, fuss:apotheke, klima:bebauung_verkehr, klima:gruen_wald)
ok    pl/karta: nach dem Einschalten der Luft Hinweis Beispieldaten oben und Marke in der Legende
ok    pl/karta: Klick in die Karte öffnet ein Popup mit Quelle („Stacja FIKCJA-M2 dane przykładowePM10, średnia roczna przed zakazem44,9 µg/m³PM1…“)
ok    pl/karta mit Ebenen bei 360 px: kein waagerechtes Scrollen (0 px)
ok    pl/dzielnica: Steckbrief für alle 18 dzielnice
ok    pl/dzielnica #st=09 bei 360 px: kein waagerechtes Scrollen (0 px)
ok    pl/porownanie: sechs Kennzahlen mit Zahl in beiden Spalten und Unterschied
ok    pl/porownanie bei 360 px: kein waagerechtes Scrollen (0 px)
ok    en/index: 5 Kopfzahlen, jede mit Quelle (800,653 | 326.9 | 18 | 90,563 | 508)
ok    en/index: Register mit 18 Zeilen und Zeile der Stadt, sortierbar, Quelle in der Unterschrift
ok    en/index bei 360 px: kein waagerechtes Scrollen (0 px)
ok    en/karta: 11 Zellebenen zur Wahl (ew, u15, 65p, fuss:haltestelle_takt, fuss:szkola, fuss:przedszkole, fuss:park, fuss:supermarkt, fuss:apotheke, klima:bebauung_verkehr, klima:gruen_wald)
ok    en/karta: nach dem Einschalten der Luft Hinweis Beispieldaten oben und Marke in der Legende
ok    en/karta: Klick in die Karte öffnet ein Popup mit Quelle („Stacja FIKCJA-M2 example dataPM10, annual mean before the ban44.9 µg/m³PM10, ann…“)
ok    en/karta mit Ebenen bei 360 px: kein waagerechtes Scrollen (0 px)
ok    en/dzielnica: Steckbrief für alle 18 dzielnice
ok    en/dzielnica #st=09 bei 360 px: kein waagerechtes Scrollen (0 px)
ok    en/porownanie: sechs Kennzahlen mit Zahl in beiden Spalten und Unterschied
ok    en/porownanie bei 360 px: kein waagerechtes Scrollen (0 px)
ok    de/index: 5 Kopfzahlen, jede mit Quelle (800.653 | 326,9 | 18 | 90.563 | 508)
ok    de/index: Register mit 18 Zeilen und Zeile der Stadt, sortierbar, Quelle in der Unterschrift
ok    de/index bei 360 px: kein waagerechtes Scrollen (0 px)
ok    de/karta: 11 Zellebenen zur Wahl (ew, u15, 65p, fuss:haltestelle_takt, fuss:szkola, fuss:przedszkole, fuss:park, fuss:supermarkt, fuss:apotheke, klima:bebauung_verkehr, klima:gruen_wald)
ok    de/karta: nach dem Einschalten der Luft Hinweis Beispieldaten oben und Marke in der Legende
ok    de/karta: Klick in die Karte öffnet ein Popup mit Quelle („Stacja FIKCJA-M2 BeispieldatenPM10, Jahresmittel vor dem Verbot44,9 µg/m³PM10, J…“)
ok    de/karta mit Ebenen bei 360 px: kein waagerechtes Scrollen (0 px)
ok    de/dzielnica: Steckbrief für alle 18 dzielnice
ok    de/dzielnica #st=09 bei 360 px: kein waagerechtes Scrollen (0 px)
ok    de/porownanie: sechs Kennzahlen mit Zahl in beiden Spalten und Unterschied
ok    de/porownanie bei 360 px: kein waagerechtes Scrollen (0 px)
```

## Startgewicht (JavaScript beim Laden, gzip -9, Skriptliste der erzeugten pl-Seite)

- `index.html`: 309489 B gz
- `karta.html`: 310350 B gz
- `dzielnica.html`: 321601 B gz
- `porownanie.html`: 17616 B gz
- davon `vendor/maplibre-gl.js`: 210896 B gz, `daten/stadtteile_odbl.js`: 50943 B gz
- index lädt erst zur ersten Frage nach: `daten/zellen_odbl.js` 11006 B gz, `daten/erreichbar_fuss_odbl.js` 7594 B gz
- Grenze der Bauvorlage für die Startseite: 300 KB gz (307200 B); `index.html` liegt darüber (offen, `docs/entscheidungen/S1.md` Nr. 5).

## Grenzen

- Handy echt (iPhone) nicht geprüft; nur Chromium mit 360 und 390 px.
- Druckansicht des Steckbriefs nur auf Vorhandensein der Regeln geprüft, kein Druckbild verglichen.
- Luft auf der Karte sind Beispieldaten (`powietrze.js`, `fixture: true`), gekennzeichnet.
