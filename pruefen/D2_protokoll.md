# Prüfprotokoll Fußweg je Zelle (vor dem Lauf festgelegt)

Stand 13.11.2026, festgelegt vor dem ersten Lauf mit Beispieldaten und vor jedem Lauf mit echten Daten. Geprüft wird
`skripte/14b_fussweg.py` mit `pruefen/D2_fussweg_pruefen.py` (`skripte/14b_fussweg.sh pruefen`). Ändert sich eine
Regel, dann nur in einem eigenen Commit vor dem nächsten Lauf, mit Grund.

## Eingang des Laufs

- Netz: `auswertung.netz_knoten`, `auswertung.netz_kante` aus `skripte/12_osm.py` (ODbL 1.0, OSM-Auszug Małopolska).
- Zellen: Tabelle `--zellen` (Standard `public.zensus_zelle`) mit `gitter_id`, `ew`, `geom` und Lizenzvermerk als
  Tabellenkommentar. Fehlt die Tabelle oder der Kommentar, rechnet das Skript nicht.
- Stadt: Vereinigung von `public.stadtteil`. Zellen zählen, wenn ihr Mittelpunkt (ST_Centroid in der Rechen-SRID)
  darin liegt oder auf der Grenze.
- Ziele: alle Zeilen aus `auswertung.einrichtung`, `gruenflaeche` (Grünarten laut Richtwerten), `osm_poi`,
  `haltestelle`, ohne Landes- oder Gemeindefilter.

## Kriterien (alle müssen erfüllt sein)

| Nr | Kriterium | Grenze |
|---|---|---|
| K1 | je Zelle und gerechneter Art genau eine Fußweg-Zeile, keine Zeile für eine fremde Zelle | 0 Abweichungen; bewohnte Zellen ohne Wert werden gezählt und genannt, sind aber kein Abbruch |
| K2 | Fußweg ≥ Luftlinie, Luftlinie unabhängig gerechnet (Minimum von ST_Distance über alle Ziele der Art, ohne Index) | 0 Verstöße |
| K3 | Median Fußweg/Luftlinie über alle Arten, nur Zellen mit Luftlinie ≥ 100 m | 1,1 bis 1,6; außerhalb ist ein Befund, dessen Ursache im Bericht steht, bevor etwas veröffentlicht wird |
| K4 | `methode` überall gesetzt; jede Fußweg-Zeile in `zelle_erreichbar` und `zelle_gruen` nennt ODbL und den Lizenzvermerk der Zellen; Tabellenkommentar von `zelle_erreichbar` nennt ODbL | 0 Abweichungen |
| K5 | jedes `ziel_id` einer Fußweg-Zeile steht im Zielbestand des Laufs | 0 fremde Ziele |

## Hinweise (kein Kriterium, stehen im Bericht)

- je Art: Ziele außerhalb der Stadtgrenze und Zellen, deren nächstes Ziel dort liegt;
- Vergleich mit vorhandenen Luftlinie-Zeilen des Pakets Versorgung (andere Zielmenge möglich);
- Anteil der größten Netzkomponente, Anbindung Zellmittelpunkt → Netz (Median, 95 %), Zellen über 300 m Anbindung.

## Was der Lauf mit Beispieldaten belegt und was nicht

Der Lauf in der Wegwerf-PostGIS (`pruefen/D2_wegwerf_db.sh`) belegt, dass Rechnung und Abnahme durchlaufen und die
Kriterien greifen. Er belegt keine Zahl über Kraków: Netz, Zellen und Ziele sind erfunden (`fixture: true`).
