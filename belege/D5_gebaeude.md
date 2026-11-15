# Beleg Gebäude und 3D (Paket Gebäude und 3D), Stand 13.11.2026

Zusammenfassung und Einordnung. Die Zählungen je Schritt schreibt das Skript selbst nach
`belege/D5_gebaeude_lauf.md` (nicht von Hand ändern); die Zahlen hier sind von dort übernommen. Regeln und
Abnahmekriterien standen vor dem ersten Lauf fest: `pruefen/D5_protokoll.md` (Commit 5313efe).

## Datenstand

| Teil | Stand | Grund |
|---|---|---|
| Stadt und 4 Delegaturen (`daten/gebaeude_kennzahlen.js`) | **echt** | BDOT10k 1261, frei nach art. 40a ust. 2 pkt 1 lit. h (`quellen-D5.md`) |
| 18 dzielnice (`daten/gebaeude_dzielnice_odbl.js`) | **Beispieldaten** (`fixture: true`, Hinweis in der Datei) | echte Gebäude, aber die Grenzen in `daten/stadtteile_odbl.js` sind noch Rechtecke des Gerüsts; keine Aussage über die dzielnice |
| Höhe für 3D (`h`, `hq`) | **orientierend** (`hq = geschosse` bzw. `ersatz`) | LoD1/LoD2 per Handdownload ausstehend; Höhe = Geschosse × 3 m, nicht gemessen |

## Eingaben

| Datei unter `$KIEZ_DATEN` | SHA256 |
|---|---|
| `2026-11-13/03_gebaeude/1261_SHP.zip` | `68b6ff47ed37184960a3abffecc34b6341d5433bb589b74dea062a4a19e2701d` |
| `2026-11-13/_auswertung/bdot10k_bubd_1261.txt` (unabhängige Zählung der Machbarkeitsprobe, Gegenprobe V1) | `963e9d59f75759b5515aaf2c422dcc77e947cdeb075612afae3446379290babd` |
| `bdot10k_rozporzadzenie/2026-11-13/D20211412.pdf` (Begriffe) | `cfaa96b5d39b5c646467210a77c3f7bb50af5c0edd2e58c40f51bc6de00d12a4` |

Vollständige Liste mit Gesetzestext und Geoportal-Seiten: `belege/rohdaten-D5-2026-11-13.sha256` (7 Dateien,
`./pruefen.sh` rechnet sie nach).

## Nachrechnen

```sh
UV="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt"
$UV python -I skripte/20_bdot10k.py             # schreibt die zwei Datendateien und den Lauf-Beleg
$UV python -I skripte/20_bdot10k.py --pruefen   # neu rechnen, byte-gleich vergleichen (V6)
$UV python -I pruefen/D5_gebaeude.py            # Abnahme V1 bis V8, Leser-Tests, Textvorschlag
```

Lauf am 13.11.2026: `--pruefen` meldet „byte-gleich: gebaeude_kennzahlen.js, gebaeude_dzielnice_odbl.js,
D5_gebaeude_lauf.md“, rund 5 s; `pruefen/D5_gebaeude.py` „0 Befunde“.

## Zählungen (aus `belege/D5_gebaeude_lauf.md`)

| Schritt | Zahl |
|---|---|
| Datensätze `OT_BUBD_A` | 90563 |
| als gelöscht markiert / ohne Geometrie / ungültig / ohne Fläche | 0 / 0 / 0 / 0 |
| mit Vermerk „Duplikaty …“ in `UWAGI` (nicht entfernt) | 466 |
| innerer Punkt in der Gemeinde Kraków / außerhalb | 90563 / 0 |
| in genau einer Delegatur | 90563 |
| in einer dzielnica (Beispielrechtecke) | 90563, davon in 16 der 18 Rechtecke mindestens ein Gebäude |
| Höhe aus LoD1 / LoD2 / Geschossen / Ersatz 3 m | 0 / 0 / 90366 / 197 |

Stadt: 90563 Gebäude, davon 61199 Wohngebäude (KŚT 110; Einfamilien 46817, Mehrfamilien 13739, sonst 643).
Geschosszahl bekannt bei 90366, Median 2, Mittel 2,2. Grundfläche 23078948 m² auf 326859586 m² Gemeindefläche,
Bebauungsdichte 7,1 %.

Delegaturen (aus `daten/gebaeude_kennzahlen.js`):

| Delegatur | Gebäude | Wohngebäude | Bebauungsdichte |
|---|---|---|---|
| Kraków-Krowodrza | 21559 | 15568 | 7,2 % |
| Kraków-Nowa Huta | 17831 | 9691 | 5,2 % |
| Kraków-Podgórze | 40988 | 29518 | 6,9 % |
| Kraków-Śródmieście | 10185 | 6422 | 19,5 % |

Σ Gebäude 90563 = Stadt, Σ Wohngebäude 61199 = Stadt (geprüft in `pruefen/D5_gebaeude.py`, Teil C).

## Abnahme gegen das Protokoll

| Nr | Ergebnis |
|---|---|
| V1 | grün: Datensätze, `FOBUD`, `KAT_ISTNIE`, `ZRO_DANYCH` und die 12 häufigsten Werte `LICZ_KONDY` gleich der Machbarkeitsprobe (anderes Werkzeug) |
| V2 | grün: 90563 + 0 = 90563; Σ Delegaturen = Stadt für jede Zählgröße |
| V3 | grün: Deckung 1,0, größte Überlappung 0,0 m² |
| V4 | grün: 0 ungültige, 0 ohne Fläche (gezählt, nichts still ausgelassen) |
| V5 | grün: keine Kennung, kein Name, keine Zusatzinformation in den Ausgaben; je Gebäude nur `f`, `gs`, `h`, `hq` |
| V6 | grün: zweiter Lauf byte-gleich |
| V7 | nicht anwendbar: keine LoD-Datei; der Leser ist mit einer Beispiel-GML im Prüfskript getestet (5 Gebäude, davon 1 ohne Kennung, 1 mit 0 m, 1 doppelt) |
| V8 | grün: `fixture` der dzielnice-Datei = `fixture` der Stadtteilgrenzen (beide `true`) |

## Warum keine Konfidenzintervalle

BDOT10k ist ein Register mit Vollerfassung, keine Stichprobe. Die Unsicherheit liegt in der Erfassung (Aktualität,
Quelle der Geometrie: 82859 aus EGiB, 4480 aus Orthofoto, 2450 „inne“, 550 BDOT500, 224 mapa zasadnicza), nicht im
Zufall. Ein Wilson-Intervall würde eine Genauigkeit vortäuschen, die es nicht misst. Stattdessen stehen Zähler und
Nenner in jeder Quote, und Median/Mittel der Geschosse erst ab 30 Gebäuden mit bekannter Zahl.

## Personenbezug

Die Ausgaben enthalten nur Zählungen je Gebiet (kleinstes nicht leeres Beispielgebiet 977 Gebäude; für die echten
dzielnice nicht geprüft) und, mit `--geometrie`, Grundrisse mit Funktion, Geschosszahl und Höhe. Keine Kennung
(`LOKALNYID`), keine Namen, keine Zusatzinformationen, keine Adressen. Ein Grundriss mit Funktion ist eine
Sachangabe über ein Bauwerk, wie auf jeder topographischen Karte 1:10 000; Eigentümer oder Bewohner lassen sich
daraus nicht ablesen. Wohnungsmarktdaten nutzt das Paket nicht.

## Grenzen

- **dzielnice:** Beispielrechtecke, die Zahlen je dzielnica sind ohne Aussage, bis das Paket Gliederung echte
  Grenzen liefert; dann einfach neu laufen lassen.
- **Höhe:** Geschosse × 3 m ist eine Konvention aus Potsdam, keine Messung; Hallen, Kirchen und Türme werden damit
  unterschätzt. LoD1 2024 (`measuredHeight`) und LoD2 2017: Leser gebaut, mit echten Dateien **nicht geprüft**
  (Feldnamen nur aus der Geoportal-Beschreibung und einer selbst geschriebenen Beispiel-GML). Wie viele
  BDOT10k-Gebäude über `buildingId` = `LOKALNYID` verknüpft werden, ist offen (V7).
- **Geschossflächen-Näherung:** Geschosse ≠ Geschossfläche; Abzeichen „orientacyjnie“.
- **Duplikate:** 466 Gebäude tragen den Vermerk „Duplikaty …“; sie bleiben gezählt, weil die Quelle sie als eigene
  Objekte führt. Wie viele davon echte Doppelungen sind, ist nicht geprüft; obere Schranke für den Fehler der
  Stadt-Zählung: 466 von 90563.
- **Geschosszahl:** bei 197 Gebäuden leer. `LICZ_KONDY` zählt nur oberirdische Geschosse; für Sakral-,
  Produktions- und Lagerbauten wird sie laut Regel nicht erfasst (Rozporządzenie Dz.U. 2021 poz. 1412, Tabela 25
  Lp. 6, S. 42: „1) liczba nadziemnych kondygnacji budynku 2) dla budynków sakralnych, produkcyjnych i magazynów
  atrybutu „liczba kondygnacji” nie pozyskuje się“). Dass trotzdem nur 197 leer sind, heißt: Die Quelle füllt das
  Feld auch dort oft; mit welchem Wert und nach welcher Regel, ist nicht geprüft.
- **Grundfläche:** Die Geometrie ist der Umriss der Grundfläche, bei auskragenden Obergeschossen aber die größte
  Ausdehnung (ebd. Lp. 8: „zarys podstawy budynku, a w przypadku budynków, których podstawy zajmują mniejszą
  powierzchnię niż poziomy przekrój wyższych kondygnacji – maksymalny zasięg budynku“). Die Bebauungsdichte ist
  deshalb eher etwas zu hoch als zu niedrig; wie viel, ist nicht geprüft.
- **Aktualität:** jüngste `WERSJA` 2026-05-18; wie alt die einzelnen Objekte sind, ist nicht ausgewertet.
- **Baujahr:** nicht enthalten und nicht frei (art. 40a ust. 2 pkt 1 lit. j), Kaskade gestrichen (KR4).
- **Gebäudedateien je dzielnica** (`--geometrie`): 32819717 Bytes, gzip 5609662 Bytes für alle 16 nicht leeren
  Beispielgebiete (Prüfskript, Teil E); nicht eingecheckt (Vorschlag in `docs/entscheidungen/D5.md`).
