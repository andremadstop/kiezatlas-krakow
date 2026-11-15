# OSM-Einrichtungen und Fußwegnetz

Erzeugt von `skripte/12_osm.py` am 2026-11-13. Daten: ODbL 1.0, © OpenStreetMap-Mitwirkende (https://opendatacommons.org/licenses/odbl/1-0/). Abstände in ETRS89 / Poland CS2000 zone 7 (EPSG:2178).

## Herkunft der Rohdaten

- PBF: `malopolskie-261112.osm.pbf`, 203717015 Byte, Datenstand 2026-11-12
- SHA256: `525d0d227cb9c876c4df02278e7fac870f0825ab0ae2c7228af6dc5c9e0f5a7e`
- Herkunft: HERKUNFT.md mit SHA256 angelegt
- Prüfsumme des Anbieters: keine Prüfsummendatei des Anbieters (<datei>.md5) neben der PBF
- Gelesen: 24249782 Knoten, 3159697 Wege, 31044 Relationen
- Abdeckung des Puffers (Stadtgebiet + 2 km): Ausdehnung der Datei umfasst das Leserechteck: ja (nur Rechteckprüfung). 1-km-Kacheln im Puffer ohne einen einzigen OSM-Knoten: 0 von 593 (Kachel 0.014° × 0.00899°, aus der Breite berechnet; große Wasserflächen sind leer; viele leere Kacheln an einem Rand heißen: Auszug endet dort).

## Fußwegnetz (auswertung.netz_knoten, auswertung.netz_kante)

- Knoten 626425, Kanten 691029, Netzlänge rund 9863 km
- Zusammenhang: Knoten im Stadtgebiet 502487, davon in der größten Komponente 493202; **Anteil der größten Komponente 98,2 %**; zweitgrößte Komponente 177 Knoten; Komponenten insgesamt 1845
- Bewohnte Zellen im Stadtgebiet 314, davon mit Netzknoten in ≤ 150 m 302 (96,2 %); Abstand Median 27.9 m, größter 298.0 m

Regeln: begehbar sind `highway`-Wege außer Autobahn, Bau, geplant, Bahnsteig, Rennstrecke; Radwege nur mit `foot=yes/designated`; `foot=no`, `access=private/no` ohne Fußfreigabe und Kraftfahrstraßen entfallen. Jeder OSM-Knoten eines solchen Wegs ist Netzknoten; Kanten sind ungerichtet. Die Fußwegrechnung nutzt nur die größte Komponente (skripte/14b_fussweg.py).

## Einrichtungen aus OSM (auswertung.osm_poi, ohne Namen)

| Art | Anzahl |
|---|---|
| apotheke | 321 |
| arzt | 283 |
| pflege | 20 |
| spielplatz | 1107 |
| supermarkt | 1270 |

## Kitas und Schulen gegen eine amtliche Liste (Treffer: OSM-Objekt höchstens 150 m entfernt)

| Art | amtliche Standorte | davon mit OSM-Gegenstück | Trefferquote | OSM-Objekte im Stadtgebiet | davon mit amtlichem Gegenstück |
|---|---|---|---|---|---|
| kita | – | – | nicht geprüft: keine amtliche Liste geladen (Schulregister RSPO offen) | 390 | – |
| schule | – | – | nicht geprüft: keine amtliche Liste geladen (Schulregister RSPO offen) | 328 | – |

OSM-Kitas: `amenity=kindergarten`, Schulen: `amenity=school` (Punkte und Flächen). Die Trefferquote misst, wie vollständig OSM gegenüber der amtlichen Liste ist; sie ist ein Hinweis auf die Güte der OSM-Kategorien ohne amtliche Liste (Ärzte, Apotheken, Märkte, Pflege, Spielplätze), kein Beleg dafür.
