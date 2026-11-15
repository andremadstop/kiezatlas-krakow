# Luft: Zählung des letzten Laufs (erzeugt von `skripte/32_powietrze.py`, nicht von Hand ändern)

Eingabe: `eingang/eea/eea_aq_statistik_krakow_20261114.geojson.zip`; Prüfsummen beim Lesen in `daten/powietrze.js` (`quelle.pliki`).

## Zeilen je Schritt

| Schritt | Zeilen |
|---|---|
| Eingabe gesamt | 10133 |
| verworfen: Land nicht Polen | 0 |
| verworfen: anderer Schadstoff oder Kennwert | 9385 |
| verworfen: Jahr außerhalb 2010–2025 | 244 |
| verworfen: Datenfluss nicht validiert (E2a u. a.) | 0 |
| verworfen: Deckung unter 75 % oder leer | 40 |
| verworfen: potentialOutlier (Feld im Export nicht geliefert, Regel greift nicht; Abweichung 2) | 0 |
| verworfen: Wert leer | 0 |
| verworfen: Koordinate leer | 0 |
| verworfen: weiter als 30 km und nicht Kraków | 0 |
| verworfen: Dublette (zweiter Messpunkt) | 127 |
| **verwendet** (Station × Kennwert × Jahr) | 337 |
| Summe verwendet + verworfen | 10133 |

## Ergebnis

- Stationen: 10 in Kraków, 0 im Umland (≤ 30 km vom Mittel der Stadt-Stationen, Länge/Breite 19.98433 / 50.05103).
- Werte mit Deckung 75–85 % (gekennzeichnet `niepelne`): 4.
- Vorher/Nachher (2016–2018 gegen 2020–2022, Übergang 2019): 17 Paare vollständig, 17 ohne volles Fenster (`null`).

## Gegenprobe GIOŚ

- GIOŚ-Gegenprobe: nicht geprüft (keine Datei unter `eingang/gios/`).
