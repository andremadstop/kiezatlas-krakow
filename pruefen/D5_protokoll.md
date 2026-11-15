# Prüfprotokoll Gebäude und 3D, festgelegt vor dem ersten Lauf (13.11.2026)

Dieses Protokoll legt fest, was gerechnet wird und woran ein Lauf gemessen wird, **bevor** das Skript zum ersten
Mal auf den echten Daten läuft. Es steht als eigener Commit vor dem ersten Lauf und wird nicht nachträglich
geändert; Änderungen kommen als neuer Abschnitt mit Datum und Grund darunter.

Skripte: `skripte/20_bdot10k.py` (Gebäude und Kennzahlen), `skripte/20_lod.py` (Höhen aus den 3D-Modellen).
Prüfung: `pruefen/D5_gebaeude.py`. Beleg: `belege/D5_gebaeude.md`.

## Eingaben

| Eingabe | Pfad unter `$KIEZ_DATEN` | Rolle |
|---|---|---|
| BDOT10k Powiat 1261, SHP | `2026-11-13/03_gebaeude/1261_SHP.zip` (SHA256 `68b6ff47…2701d`, Machbarkeitsprobe) | Gebäude (`OT_BUBD_A`), Gemeinde und Delegaturen (`OT_ADJA_A`) |
| Rozporządzenie BDOT10k (Dz.U. 2021 poz. 1412) | `bdot10k_rozporzadzenie/2026-11-13/D20211412.pdf` | Begriffe (Tabelle 25 und 26), Erfassungsregeln (Rozdział 6) |
| Stadtteilgrenzen (dzielnice) | `daten/stadtteile_odbl.js` (Paket Gliederung) | Zuordnung zu den 18 dzielnice; solange die Datei `fixture: true` trägt, ist auch das Ergebnis je dzielnica Beispieldaten |
| LoD1 2024 / LoD2 (Handdownload) | `eingang/lod1_2024_1261*.zip|.gml`, `eingang/lod2_1261*.zip|.gml` | Höhe je Gebäude; fehlt die Datei, Höhe aus Geschossen |

## Raumeinheiten und Zuordnung

1. **Stadt** = Polygon in `OT_ADJA_A` mit `RODZAJ = "gmina"` und `NAZWA = "Kraków"`.
2. **Delegatury** (4) = Polygone in `OT_ADJA_A` mit `RODZAJ = "dzielnica lub delegatura"` (Quelle PRG, im Paket
   enthalten). Sie sind nicht die 18 dzielnice.
3. **dzielnice** (18) = Polygone aus `daten/stadtteile_odbl.js`.
4. Ein Gebäude gehört zu der Einheit, die seinen **inneren Punkt** (`point_on_surface` des Grundrisses, im
   Koordinatensystem der Quelle aus der `.prj`) enthält. Jedes Gebäude zählt höchstens einmal je Ebene.
5. Flächen (Grundfläche, Fläche der Einheit) werden im Rechen-Koordinatensystem der Ortskonfiguration
   (`rechen_srid`, KR1) gerechnet, nach Transformation aus dem Koordinatensystem der Quelle.

## Kennzahlen (Definitionen, fest)

| Feld | Definition |
|---|---|
| `anzahl` | Datensätze in `OT_BUBD_A`, deren innerer Punkt in der Einheit liegt (alle Kategorien `KAT_ISTNIE`) |
| `zustand.<wert>` | Anzahl je `KAT_ISTNIE` (eksploatowany, w budowie, nieczynny, zniszczony, leer) |
| `funktion.<KST>` | Anzahl je Klasse `KODKST` (101 … 110, Tabelle 26 des Rozporządzenie) |
| `wohngebaeude` | `KODKST = 110` („budynki mieszkalne“) |
| `wohn_art.ein`, `.mehr`, `.sonst` | Wohngebäude mit `PFBUD` (przeważająca funkcja) „budynek jednorodzinny“, „budynek wielorodzinny“, sonst |
| `geschosse.<klasse>` | Klassen von `LICZ_KONDY`: 1, 2, 3–4, 5–10, 11+, unbekannt (leer oder 0) |
| `geschosse_median`, `geschosse_mittel` | über Gebäude mit bekannter Geschosszahl, getrennt für alle und für Wohngebäude; nur bei n ≥ 30, sonst `null` mit Grund |
| `grundflaeche_m2` | Summe der Grundrissflächen der Gebäude mit `KAT_ISTNIE` ≠ „zniszczony“ |
| `flaeche_m2` | Fläche der Einheit |
| `bebauungsdichte` | `grundflaeche_m2 / flaeche_m2` in Prozent, mit Zähler und Nenner |
| `geschossflaeche_naeherung` | Σ (Grundfläche × Geschosse) / Fläche der Einheit, nur Gebäude mit bekannter Geschosszahl; Abzeichen „orientacyjnie“, weil Geschosse ≠ Geschossfläche und Produktions-, Lager- und Sakralbauten ohne Geschosszahl erfasst werden |

Es sind Vollzählungen des Registers, keine Stichproben; Wilson-Intervalle entfallen deshalb (begründet im Beleg).

## Höhe für 3D (Feld `h`, Herkunft `hq`)

1. `lod1`: `measuredHeight` aus LoD1 2024, verknüpft über `buildingId` = `LOKALNYID` des BDOT10k-Gebäudes.
2. `lod2`: Höhe aus LoD2 (Stand 2017), nur wenn LoD1 fehlt; gleiche Verknüpfung.
3. `geschosse`: `LICZ_KONDY` × 3 m (Konvention aus Potsdam, Orientierung, nicht gemessen).
4. `ersatz`: 3 m, wenn nichts davon vorliegt.

Ganze Meter. `lod1`/`lod2` sind im Vertrag `daten/schema/gebaeude.json` noch nicht vorgesehen
(Vorschlag Vertragsänderung in `docs/entscheidungen/D5.md`).

## Prüfungen und Abnahmekriterien (fest vor dem Lauf)

| Nr | Prüfung | grün, wenn |
|---|---|---|
| V1 | Datensätze `OT_BUBD_A` und Verteilung `FOBUD`, `KAT_ISTNIE`, `ZRO_DANYCH` gegen die unabhängige Zählung der Machbarkeitsprobe (`_auswertung/bdot10k_bubd_1261.txt`, anderes Werkzeug) | alle Zahlen gleich |
| V2 | jedes Gebäude genau einer Delegatur oder „außerhalb“ zugeordnet | Σ Delegaturen + außerhalb der Stadt = alle Datensätze; Σ Delegaturen = Stadt, für jede Kennzahl mit Zählcharakter |
| V3 | Delegaturen decken die Stadt | Fläche(Vereinigung) / Fläche(Stadt) zwischen 0,9999 und 1,0001; Überlappung zwischen Delegaturen < 1 m² je Paar |
| V4 | Geometrien | ungültige Grundrisse gezählt und mit `make_valid` gerechnet; Gebäude ohne Fläche gezählt; keine stille Auslassung |
| V5 | Datenschutzgrenze | in den Ausgaben kein `LOKALNYID`, `NAZWA`, `INFO_DODAT`, keine Adressfelder; je Gebäude nur `f`, `gs`, `h`, `hq` |
| V6 | Reproduzierbarkeit | zweiter Lauf erzeugt byte-gleiche Ausgaben (`--pruefen`) |
| V7 | LoD-Verknüpfung (sobald die Datei da ist) | Anteil verknüpfter Gebäude und Anteil `measuredHeight` ≤ 0 oder > 300 m im Beleg; kein Abnahmekriterium, weil kein Vorwissen über den Anteil besteht |
| V8 | Beispieldaten | Ausgaben je dzielnica tragen `fixture: true`, solange `daten/stadtteile_odbl.js` Beispieldaten sind |

Doppelte Gebäude (`UWAGI` „Duplikaty występują …“) werden **nicht** entfernt, sondern gezählt und im Beleg genannt:
Die Quelle führt sie als eigene Objekte, und welche Fassung richtig ist, lässt sich aus den offenen Daten nicht
entscheiden.

## Nicht Teil dieses Pakets

Baujahre und die Bauzeiten-Kaskade (KR4), Gebäudeseiten (spätere Bauphase), Daten aus MSIP (Lizenz-STOPP, KR3).
