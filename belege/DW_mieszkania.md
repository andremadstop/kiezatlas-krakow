# Beleg Wohnungsmarkt (Paket Wohnungsmarkt): Zählungen je Schritt

Erzeugt von `skripte/40_mieszkania.py` im selben Lauf wie `daten/mieszkania_odbl.js`; nicht von Hand ändern. Regeln: `pruefen/DW_protokoll.md`. Prüfung: `pruefen/DW_mieszkania.py`.

## Eingabe

- Art: `rcn_gpkg`; Datei: `eingang/rcn/1261_transakcje_ceny.gpkg`; SHA256: `ed4cc8bb321a3ac8fbe7a60dc6b43a51fd86d1fd7400a618442c51ce672d99fc`
- Tabelle der Lokale: `transakcje_lokale`; Spalten: transaktion = `tran_oznaczenie_trans`, lokal_id = `lok_id_lokalu`, art_transaktion = `tran_rodzaj_trans`, markt = `tran_rodzaj_rynku`, anteil = `nier_udzial`, datum = `dok_data`, funktion = `lok_funkcja`, flaeche = `lok_pow_uzyt`, preis_lokal = `lok_cena_brutto`, preis_transaktion = `tran_cena_brutto`
- jüngstes Dokumentdatum der Datei (alle Tabellen, vor den Filtern; `datenstand`): 2026-09-29; unvollständiges Jahr: 2026
- Geoportal nennt beim Handdownload vom 14.11.2026 (`eingang/HERKUNFT.md`) „Data ostatniej aktualizacji 2026-09-21“; die Datei enthält trotzdem Dokumente bis 2026-09-29. Der Unterschied ist nicht geklärt.
- Stadtteilgrenzen: daten/stadtteile_odbl.js (SHA256 561dd8d8923cbb51e4876da74bc14ecd774b6f2e8ca20b78746c5238f47ef89e, 18 dzielnice)
- Stand der Auswertung: 2026-11-14

## Zählung je Schritt

| Nr | Schritt | Zeilen danach |
|---|---|---|
| F0 | Zeilen der Lokal-Ebene | 358344 |
| F1 | ohne Dubletten (Transaktion und Lokal) | 358332 |
| F2 | Funktion Wohnung | 270377 |
| F3 | freier Markt | 258437 |
| F4 | volles Recht (Anteil 1/1) | 166168 |
| F5 | genau eine Wohnung je Transaktion | 154574 |
| F6 | Preis vorhanden | 109461 |
| F7 | Nutzfläche vorhanden | 109452 |
| F8 | Fläche und Preis je m² in den Plausibilitätsgrenzen | 109276 |
| F9 | Datum des Dokuments vorhanden | 109276 |
| F10 | einer dzielnica zugeordnet | 45701 |
| F11 | Dokumentjahr ab 2019 (Jahre davor nicht veröffentlicht, KR55) | 45687 |

- Preis aus dem Lokal: 109290; Preis aus der Transaktion (ein Lokal, kein anderes Objekt): 171
- nach F9 keiner dzielnica zugeordnet: 63575
- vor 2019 nicht veröffentlicht (F11, KR55): 14
- ohne Angabe des Marktes (nur in `ogolem`): 0

## Veröffentlichte Werte

Mindestfallzahl 10. Felder je dzielnica, Jahr und Markt: 432; mit Median 371; leer wegen n < 10: 32; ohne Transaktion: 29.

Abstimmung: Summe n (`ogolem`) über alle dzielnice und Jahre gegen die Zählung nach F11, vor dem Unterdrücken gerechnet: stimmt.

Sekundäre Unterdrückung (Nachträge 2 bis 4), damit sich keine unterdrückte Fallzahl aus veröffentlichten Summen zurückrechnen lässt: verdeckte Fallzahlen 27 (Median bleibt).

Spannenprobe (`pruefen/DW_protokoll.md`, Änderung KR55): unterdrückte Fallzahlen, die im ganzen veröffentlichten System höchstens zwei ganzzahlige Werte haben: 0 von 32.

| Jahr | n Stadt (ogolem) | Median Stadt ogolem (zł/m²) | n pierwotny | n wtórny |
|---|---|---|---|---|
| 2019 | 256 | 7352 | 207 | 49 |
| 2020 | 2525 | 7657 | 1979 | 546 |
| 2021 | 9417 | 8850 | 5879 | 3538 |
| 2022 | 8714 | 10028 | 5220 | 3494 |
| 2023 | 8524 | 11081 | 4598 | 3926 |
| 2024 | 6333 | 13468 | 3314 | 3019 |
| 2025 | 5881 | 14651 | 3134 | 2747 |
| 2026 | 4037 | 14973 | 2265 | 1772 |

## Grenzen

- Kaufverträge, keine Angebote und keine Mieten. Brutto wie im Register (Erstverkauf meist mit Umsatzsteuer).
- Vollständigkeit des Registers für Kraków und Richtigkeit der Geometrie: nicht geprüft.
- **Werte der ganzen Stadt erst ab 2021 weitgehend vollständig** (ab da in jedem Jahr mindestens 90 % der Käufe mit Datum auch mit Lage): Anteil der Käufe mit Lage (nach F10) an den Käufen mit Datum (nach F9) je Jahr mit veröffentlichter Stadtzahl (Anteil abgerundet): 2019: 256 von 13117 (1,9 %); 2020: 2525 von 9617 (26,2 %); 2021: 9417 von 10322 (91,2 %); 2022: 8714 von 8718 (99,9 %); 2023: 8524 von 8524 (100,0 %); 2024: 6333 von 6333 (100,0 %); 2025: 5881 von 5881 (100,0 %); 2026: 4037 von 4037 (100,0 %). **Werte je dzielnica erst ab 2021, davor nur zum Teil:** In den veröffentlichten Jahren 2019 bis 2020 fehlt mehr als der Hälfte der Zeilen nach F9 die Geometrie, F10 schließt sie aus (nach F9 ohne Geometrie 63575 Zeilen über alle Jahre, mit Geometrie außerhalb der dzielnice 0). Bis 2015 fehlt in der Datei außerdem den meisten Zeilen der Anteil am Recht, F4 schließt sie aus. Jahre vor 2019 sind nicht veröffentlicht (F11, KR55).
- Zuordnung zur dzielnica über `daten/stadtteile_odbl.js`; Lizenzfolge für abgeleitete Werte offen (docs/entscheidungen.md, KR3).
- Keine Extremwerte, keine Perzentile, keine Einzelfälle veröffentlicht (Datenschutz).
