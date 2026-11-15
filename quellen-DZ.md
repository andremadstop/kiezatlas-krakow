# Quellen des Pakets Denkmale und Kamienice (Lieferung an die Belegschicht)

Stand 13.11.2026. Skript: `skripte/dz_denkmale.py`. Regeln: `pruefen/DZ_protokoll.md`. Weg: A = automatischer
Abruf über `skripte/abruf.py`, H = Handdownload durch den Betreiber nach `$KIEZ_DATEN/eingang/`, L = schon geladen (Machbarkeitsprobe).

## Quellen

| Quelle | Nutzer (Ausgabe) | URL | Lizenz | wörtlicher Vermerk, Fundstelle | Weg | Stand |
|---|---|---|---|---|---|---|
| BDOT10k, Paket 1261 (GUGiK): Gebäude `OT_BUBD_A`, Komplexe `OT_KUZA_A`, Stadt und Delegaturen `OT_ADJA_A` | `daten/denkmale_bdot.js`; Gebäudebezug in `daten/denkmale.js` und `daten/denkmale_odbl.js` | https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip | gebührenfrei, keine Lizenz, Quellenangabe Pflicht | Prawo geodezyjne i kartograficzne, Dz.U. 2026 poz. 1389, art. 40c ust. 3: „Podmioty, które wykorzystują materiały zasobu, zamieszczają w publikowanych opracowaniach informacje o źródle pochodzenia użytego materiału.“; art. 40c ust. 5: „Licencji nie wydaje się … w przypadku udostępnienia materiałów zasobu, o których mowa w art. 40a ust. 2 pkt 1 i 3.“ (`2026-11-13/03_gebaeude/pgik_DU_2026_1389.pdf`, SHA256 `f7b4ac608d0737a50bf59729d04ea7100f9e64728affcf3fd7582cbfcfaa0c24`). Geoportal: „Baza BDOT10k jest dostępna bezpłatnie i możliwa do dowolnego wykorzystania.“ (`2026-11-13/03_gebaeude/geoportal_bdot10k.html`, SHA256 `58fe5cf154ec9006845bce4d4227513f630022b439643e5113efe114496840e4`) | L (Abruf 13.11.2026, `2026-11-13/03_gebaeude/HERKUNFT.md`) | Dateien vom 03.10.2026 |
| Wikidata, Objekte mit polnischer Denkmal-Registernummer in Kraków | `daten/denkmale.js` | https://query.wikidata.org/ (Abfrage unten) | CC0 1.0 für strukturierte Daten | wörtlich in `eingang/wikidata_licensing_20261114.txt` (https://www.wikidata.org/wiki/Wikidata:Licensing, Handabruf 14.11.2026); Vermerk im Atlas „Wikidata, CC0 1.0“ (`quellen.wd.vermerk`) | H (`query.wikidata.org` und `www.wikidata.org` sind in `skripte/abruf.py` gesperrt) | Abruf 14.11.2026 |
| Rejestr zabytków, Narodowy Instytut Dziedzictwa (dane.gov.pl, Datensatz 1130) | `daten/denkmale.js` | https://dane.gov.pl/pl/dataset/1130 (Adresse aus der Machbarkeitsprobe, Seite nicht abgerufen) | **nicht geprüft** (dane.gov.pl lieferte bei der Probe eine Zeitüberschreitung) | steht aus: Lizenzangabe der Datensatzseite beim Handabruf als HTML ablegen | H | – |
| Gminna ewidencja zabytków Krakowa (Zarządzenie Prezydenta Miasta Krakowa Nr 2184/2013 mit Änderungen) | `daten/denkmale.js` | nicht angegeben (Fundstelle im BIP nicht gesucht) | **nicht geprüft**; amtliche Anlagen einer Verordnung sind nach art. 4 pr. aut. vermutlich frei (Wissen, nicht geprüft) | steht aus | H | – |
| OpenStreetMap, Objekte mit `heritage=*` oder `start_date`, Ortsmarke über `addr:*` | `daten/denkmale_odbl.js` | Auszug Małopolska (Geofabrik oder BBBike) | ODbL 1.0 | „OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF).“ (`2026-11-13/08_fussweg/osm_copyright.html`, SHA256 `226baa199d8471191c56cdbe340ec39ea5b9f4500be61b3e69fdaa387f4bcd07`) | H (Overpass und Geofabrik in `skripte/abruf.py` gesperrt) | – |
| zabytek.pl (NID) | keine | https://zabytek.pl/ | – | robots.txt „Deny: /“ (`2026-11-13/04_bauzeit/_zabytek_robots_probe.txt`); nicht verwendet | – | – |

Pfade relativ zu `$KIEZ_DATEN` (Standard `../kiezatlas-daten/krakow`). Prüfsumme des BDOT10k-Pakets:
`belege/rohdaten-dz-2026-11-13.sha256`.

## Ausgaben und ihre Lizenz

| Datei | Inhalt | Lizenz |
|---|---|---|
| `daten/denkmale_bdot.js` | echte Daten: Zählungen der Gebäude, 59 Komplexe, 28 Gebäude mit Namen „Kamienica“ | Quellenangabe nach art. 40c ust. 3 (Feld `quelle.vermerk`, eigene Formulierung des Vermerks) |
| `daten/denkmale.js` | echt seit 14.11.2026, bisher nur aus Wikidata (`eingang/wikidata_zabytki_krakow.json`); NID-Register und gminna ewidencja fehlen; Lage am Luftbild in einer Zufallsstichprobe geprüft (15.11.2026, `sichtpruefung` in der Datei, Ergebnis in `belege/DZ_denkmale_lauf.md`), nicht je Punkt; geladen von `kamienice` und `karta`, Download-Ebene `rejestr_zabytkow` | Wikidata CC0 1.0 (wörtlich in `eingang/wikidata_licensing_20261114.txt`); übrige Register noch nicht geprüft (siehe oben) |
| `daten/denkmale_odbl.js` | echt: OSM-Objekte mit `heritage` oder `start_date`; Lage der Objekte mit `heritage` am Luftbild in einer Zufallsstichprobe geprüft (15.11.2026, `sichtpruefung` mit Ergebnis der OSM-Punkte und beider Ebenen zusammen), nicht je Punkt | echt: ODbL 1.0, © OpenStreetMap-Mitwirkende |

## Handdownloads für den Betreiber: Dateinamen und erwartetes Format

Ablage: `$KIEZ_DATEN/eingang/`, je Datei eine Zeile in `eingang/HERKUNFT.md` (URL,
Datum, Lizenzseite als HTML daneben). Die Zeile beginnt mit `| <Dateiname>`, die letzte Spalte nennt den Abruftag als
TT.MM.JJJJ; daraus setzt das Skript `stand` von `daten/denkmale.js` (jüngster Abruftag der vorhandenen Register) und
bricht ohne ihn mit Rückgabe 4 ab. Danach `python -I skripte/dz_denkmale.py` und Prüfsummen in eine neue Liste
`belege/rohdaten-dz-eingang-<datum>.sha256` (der Lauf schreibt die SHA256 der Eingänge schon in
`belege/DZ_denkmale_lauf.md`).

| Datei | Herkunft | erwartetes Format | was der Leser tut, wenn es nicht passt |
|---|---|---|---|
| `wikidata_zabytki_krakow.json` | WDQS-Oberfläche, Abfrage unten, „Download → JSON“ | SPARQL-JSON (`head.vars`, `results.bindings`), Variablen mindestens `item`, `nr`; dazu `coord` als `Point(Länge Breite)` und `inception` als Zeitwert | Abbruch mit Rückgabe 3, wenn `item` oder `nr` fehlt |
| `nid_rejestr_zabytkow.csv` | dane.gov.pl, Datensatz 1130, CSV-Export | **nicht geprüft**. Erwartet: Kopfzeile, Trenner `;`, `,` oder Tab, UTF-8; eine Spalte mit Registernummer (Name enthält „rejestr“, „nr_rej“ oder „numer“); Koordinaten, falls vorhanden, in Spalten mit „szerokość“/„lat“ und „długość“/„lon“; Datierung, falls vorhanden, in einer Spalte mit „datowanie“ | Abbruch mit Rückgabe 3 ohne Spalte für die Registernummer; ohne Koordinaten nur Zählung und Verknüpfung mit Wikidata über die Nummer |
| `gez_krakow.csv` | Gminna ewidencja zabytków als Tabelle | **nicht geprüft**, Muster wie oben; Registernummer nicht nötig | ohne Koordinaten nur Zählung. Liegt die Ewidencja nur als PDF vor, nicht abtippen: als offen melden |
| `*.osm.pbf` (die erste nach Namen) | Geofabrik `malopolskie-latest.osm.pbf` oder BBBike-Auszug Kraków, wie Potsdam | PBF mit zlib-Blöcken (Leser `skripte/osm_pbf.py` des Pakets OSM und Fußwegnetz) | lzma, lz4, zstd lehnt der Leser ab |

### WDQS-Abfrage (von Hand auf https://query.wikidata.org/ ausführen)

Die Kennungen sind aus Wissen gewählt und vor dem Abruf auf wikidata.org nachzusehen: `P3424` (Registernummer im
polnischen Denkmalregister), `P131` (liegt in der Verwaltungseinheit), `Q31487` (Kraków), `P625` (Koordinaten),
`P571` (Entstehung).

```sparql
SELECT ?item ?nr ?coord ?inception WHERE {
  ?item wdt:P3424 ?nr ;
        wdt:P131* wd:Q31487 .
  OPTIONAL { ?item wdt:P625 ?coord }
  OPTIONAL { ?item wdt:P571 ?inception }
}
```

Bricht die Abfrage wegen `P131*` mit Zeitüberschreitung ab, ist das zu melden; nicht über andere Dienste oder
Spiegel ausweichen.
