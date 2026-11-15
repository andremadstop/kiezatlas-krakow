# Beleg Datenbank: Grenzen der dzielnice und Zellen (erzeugt)

Erzeugt von `skripte/05_db_gliederung.py laden` (nicht von Hand ändern); `pruefen` gleicht ohne Schreiben ab.
Grenzen: `eingang/malopolskie-261112.osm.pbf`, Datenstand laut Dateikopf 2026-11-12T21:23:05Z (ungeglättet; die Kartengeometrie in `daten/stadtteile_odbl.js` ist auf 3 m vereinfacht).

| Tabelle | Zeilen vorher | Zeilen nachher |
|---|---|---|
| `public.stadtteil` | 0 | 18 |
| `public.zensus_zelle` | 0 | 327 |

Einwohner in den Zellen (Summe `ew`): 793.392

| Abgleich | erfüllt | Angabe |
|---|---|---|
| public.stadtteil: 18 Zeilen mit nr, roemisch, name aus config/krakow.yaml, Geometrie gültig | ja | 18 Zeilen |
| public.zensus_zelle = Rechnung (gitter_id und ew) | ja | 327 Zeilen in der Datenbank, 327 gerechnet |
| public.zensus_zelle = daten/zellen_odbl.js (gitter_id und ew, gleiche Reihenfolge) | ja | 327 Zellen in der Datei |
| Auswahl der Fußweg-Rechnung (Mittelpunkt in EPSG:2178) = alle Zellen der Tabelle | ja | 327 Zellen |
| Tabellenkommentar von public.zensus_zelle nennt Eurostat und CC BY 4.0 | ja | 294 Zeichen |
