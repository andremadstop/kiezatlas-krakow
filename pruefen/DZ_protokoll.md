# Prüfprotokoll Denkmale und Kamienice (vor dem ersten Lauf festgelegt)

Stand 13.11.2026. Dieses Protokoll steht als eigener Commit **vor** dem ersten Lauf von `skripte/dz_denkmale.py`
auf echten Daten. Was hier steht, gilt für die Abnahme; spätere Änderungen nur mit neuem Commit und Begründung in
`docs/entscheidungen/DZ.md`. Ergebnisse: `belege/DZ_denkmale_lauf.md` (Dateiname am 13.11.2026 berichtigt, siehe `docs/entscheidungen/DZ.md`).

## Gegenstand und Grenze

- Gebiet: Stadt Kraków = BDOT10k-Paket 1261 (Powiat grodzki, TERYT 1261). Die Stadtgrenze und die vier
  Delegaturen (`OT_ADJA_A`, `RODZAJ` = „gmina“ bzw. „dzielnica lub delegatura“) kommen aus demselben Paket.
- Das Thema ist eine **Teilmenge der Denkmale**: nur Objekte, die eine der Quellen als Denkmal führt
  (Rejestr zabytków des NID, Gminna ewidencja zabytków, Wikidata mit Registernummer, OSM `heritage=*`). Es gibt
  **keine Flächenaussage zu Baujahren**: Kein Wert dieses Pakets sagt etwas über das Alter aller Gebäude eines
  Gebiets. Die Datei trägt dazu `teilmenge: true` und `flaechenaussage: false`, der Vertrag erzwingt beides.
- BDOT10k hat **kein** Denkmal-Merkmal an Gebäuden (`OT_BUBD_A`: Felder `FOBUD`, `FSBUD`, `PFBUD`,
  `LICZ_KONDY`, `NAZWA`, kein `zabytek`). Ein Gebäudename „Kamienica …“ ist ein **Namensbezug**, kein
  Denkmalstatus, und wird getrennt gezählt. Die Komplexe `OT_KUZA_A` (kompleks zabytkowo-historyczny) sind
  Flächen mit historischem Bezug laut Topographie, kein Register.

## Begriffe (Arbeitsdefinitionen)

| Begriff | Regel |
|---|---|
| Wohngebäude | `OT_BUBD_A.FOBUD` = „budynki mieszkalne“ |
| Mehrfamilienhaus | Wohngebäude mit `PFBUD` = „budynek wielorodzinny“ |
| Kamienica (Atlas) | Mehrfamilienhaus **mit Denkmalbezug** (Treffer einer Register- oder OSM-Denkmalangabe im Gebäude) |
| Namensbezug | `NAZWA` beginnt (ohne Groß-/Kleinschreibung) mit „kamienica“ |
| Treffer im Gebäude | Punkt liegt im Gebäudeumriss (BDOT10k, Koordinatensystem der Lieferung); sonst nächstes Gebäude bis **10 m**, sonst kein Gebäude |
| Delegatura | Lage des Gebäude-Schwerpunkts bzw. des Punkts im Umriss aus `OT_ADJA_A` |
| Gleiche Registernummer | Vergleich ohne Leerraum und Bindestriche, Großbuchstaben („A 1“ = „A-1“ = „a-1“); nachgetragen am 13.11.2026 vor dem ersten Lauf mit Registerdaten, Anlass: Codepfad-Test `pruefen/DZ_test_eingang.py` |

## Bauzeitklassen statt Einzeljahren

Kein Einzeljahr wird veröffentlicht, auch nicht bei Nicht-Wohngebäuden (vorsichtige Lesart von Punkt 30 der
Checkliste: kein Einzeljahr bei Wohnraum; die Wohnnutzung ist ohne Gebäudetreffer nicht sicher). Klassen:
`vor_1800`, `1800_1866`, `1867_1918`, `1919_1945`, `1946_1989`, `ab_1990`. Lesart der Angaben:

- vierstellige Jahreszahl am Anfang (mit `~` oder „ca.“ davor) → Klasse dieses Jahres;
- Jahrzehnt („1890s“), Spanne („1890..1900“, „1890-1900“) oder Jahrhundert („C19“) → Klasse nur, wenn die ganze
  Spanne in einer Klasse liegt, sonst `null`;
- alles andere → `null`, gezählt als „nicht lesbar“.

## Zählungen je Schritt (Pflicht im Beleg)

1. BDOT10k: Gebäude gesamt, je `KAT_ISTNIE`, Wohngebäude, Mehrfamilienhäuser, Namensbezug; Wohngebäude und
   Mehrfamilienhäuser je Delegatura plus „keiner Delegatura zugeordnet“; Komplexe je `RODZAJ`; Mehrfamilienhäuser
   mit Schwerpunkt in einem Komplex „zespół zabudowy historycznej“.
2. Je Registerquelle (sobald die Datei in `eingang/` liegt): Zeilen gelesen, mit Koordinate, in der Stadt, Treffer
   im Gebäude, davon Mehrfamilienhaus, Bauzeitklasse lesbar / nicht lesbar, doppelt über Registernummer.
3. OSM: Objekte mit `heritage=*` bzw. `start_date`, in der Stadt, Treffer im Gebäude, Klassen.

## Abnahmeregeln (Befund, wenn verletzt)

1. Summen stimmen: Σ je Delegatura + nicht zugeordnet = Stadt; Σ je `KAT_ISTNIE` = gesamt; Σ Komplexe je
   `RODZAJ` = Komplexe gesamt; Σ Bauzeitklassen + `null` = Objekte.
2. Kein Feld mit Gebäudekennung (`LOKALNYID`, `id`, `oid`, `gml_id`), keine Adresse, kein Name an Wohngebäuden,
   kein Einzeljahr in `daten/denkmale*.js`.
3. OSM-Werte nur in `daten/denkmale_odbl.js`; `daten/denkmale.js` und `daten/denkmale_bdot.js` ohne OSM-Spur.
4. Jede Datei, deren Eingang fehlt, ist Beispieldatei (`fixture: true`, erfundene Punkte, im Kopf gekennzeichnet).
5. Reproduzierbar: `skripte/dz_denkmale.py --pruefen` erzeugt aus denselben Eingängen byte-gleich dieselben Dateien.
6. Die Ortsmarke ul. Kościuszki 18 hat nur dann eine Lage, wenn eine Quelle sie trägt (keine Geokodierung über
   gesperrte Dienste, keine Koordinate aus dem Gedächtnis); sonst `null` mit `lage_geprueft: false`.
7. Stichprobe: 20 zufällige Treffer (Startwert 20261113) aus jeder Registerquelle werden mit Lage und Gebäude
   aufgelistet, damit ein Mensch sie gegen das Luftbild prüfen kann; ausgewertet wird sie erst nach dem Lauf.

## Nicht geprüft und offen (vor dem Lauf bekannt)

- Formate von NID-Register und Gminna ewidencja (nicht gesehen); der Leser bricht bei fremden Spalten ab.
- Ob der NID-Export Koordinaten trägt (laut Suchtreffer im OSM-Forum nicht; nicht archiviert).
- Die Wikidata-Eigenschaften der Abfrage (Registernummer, Lage in Kraków) sind aus Wissen gewählt und vor dem
  Handabruf auf wikidata.org nachzusehen.

## Aufrufe

| Prüfung | Aufruf | braucht | Vorschlag für `pruefen.sh` |
|---|---|---|---|
| Datenverträge der drei Dateien | `pruefen/daten.py` (bestehend) | nichts | läuft schon mit |
| Paketregeln oben, ohne Rohdaten | `python -I pruefen/DZ_denkmale.py` | nichts | aufnehmen |
| Reproduzierbarkeit aus Rohdaten | `python -I skripte/dz_denkmale.py --pruefen` | `$KIEZ_DATEN` mit BDOT10k 1261 | aufnehmen, übersprungen ohne Rohdaten |

## Nachträge

### Nachtrag 1 zu Schritt 3 (14.11.2026, nach einer Fachprüfung)

Anlass: Der OSM-Leser las nur Knoten und Wege. Denkmale, die in OpenStreetMap als Relation (Multipolygon) erfasst
sind, fielen weg, gerade große Bauten mit Innenhof. Geändert wird:

- Relationen `type=multipolygon` mit `heritage=*` oder `start_date` werden mitgelesen. Ihre Wege kommen in einem
  zweiten Durchgang. Äußere Ringe minus innere ergeben die Fläche, der Punkt ist `representative_point()` (liegt in
  der Fläche, nicht im Innenhof).
- Ein Weg, der äußeres Mitglied einer gelesenen Relation ist, zählt nicht noch einmal.
- Neue Zählungen im Beleg: `relationen_gelesen`, `relationen_ohne_lage` (kein vollständiger äußerer Ring im
  Leserahmen, also außerhalb der Stadt), `relationen_ohne_flaeche`, `relationen_unvollstaendig`, `aus_relationen`,
  `wege_als_teil_einer_relation`.
- Die Kennzahl „Mehrfamilienhaus mit heritage“ heißt auf den Seiten nicht mehr „Kamienice nach der Festlegung des
  Atlas“, sondern „Mehrfamilienhäuser (BDOT10k) mit Denkmal-Kennzeichnung in OpenStreetMap“, solange das
  NID-Register fehlt. Sie zählt OSM-Kennzeichnungen, keine Denkmale.

### Nachtrag 2 zu Regel 7 (14.11.2026, nach einer Sichtprüfung der Stichprobe)

Anlass: Die OSM-Stichprobe wurde aus allen Gebäudetreffern gezogen, auch aus Objekten, die nur `start_date` tragen.
11 von 20 Punkten hatten die Bauzeitklasse `ab_1990`, waren also neue Bauten statt Denkmale. Geändert wird: Die
Stichprobe kommt nur aus Treffern mit `heritage=*`. Startwert (20261113) und Umfang (20) bleiben. Die neue Liste steht
in `belege/DZ_denkmale_lauf.md`. `sichtpruefung.geprueft` bleibt `false`, bis jemand die neue Liste am Luftbild
geprüft hat.

### Nachtrag 3 zu Regel 7 (14.11.2026, vor dem Einbinden des Registers in die Seiten)

Anlass: `daten/denkmale.js` (Wikidata) kommt auf die Seiten `kamienice` und `karta`. Die bisherige Stichprobe
(Startwert 20261113) zog nur aus Punkten mit Gebäudetreffer und nannte keine Kennung, mit der ein Prüfer das Objekt
in der Quelle wiederfindet. Festgelegt wird eine zweite Runde, bevor die Seiten die Registerpunkte zeigen:

- Startwert **20261114**, Umfang je **20** Punkte aus Wikidata und aus OSM.
- Grundgesamtheit ist genau die Menge, die die Karte zeigt: alle Registerpunkte aus `daten/denkmale.js` (auch ohne
  Gebäudetreffer) und alle OSM-Objekte mit `heritage=*` aus `daten/denkmale_odbl.js` (auch ohne Gebäudetreffer).
  Vor dem Ziehen wird nach Lage und Kennung sortiert, damit derselbe Eingang dieselbe Liste ergibt.
- Geprüft werden nur **Lage** (steht der Punkt auf dem Objekt) und **Ansicht** (zeigt das Luftbild ein Bauwerk oder
  eine Anlage, die zur Angabe passt). Bauzeitklasse und Gebäudezuordnung sind nicht Gegenstand dieser Runde.
- Die Liste steht in `belege/DZ_denkmale_lauf.md` und als `belege/DZ_sichtpruefung_stichprobe.json` (je Punkt nur
  `lon`, `lat`, `quelle`, `id`; `id` ist die Wikidata-Kennung bzw. die OSM-Kennung mit Typ, kein Name, keine Adresse).
  Kennungen stehen nur dort, nie in `daten/denkmale*.js` (Regel 2 bleibt).
- Die erste Runde (Startwert 20261113, Nachtrag 2) bleibt im Beleg stehen.
- `sichtpruefung.geprueft` bleibt in beiden Datendateien `false`, bis ein Mensch die zweite Runde ausgewertet hat;
  `sichtpruefung.startwert` nennt die Runde, die aussteht (20261114).

### Nachtrag 4 zu Regel 7 (15.11.2026, vor dem Auswerten der zweiten Runde)

Anlass: Die zweite Runde (Nachtrag 3) ist geprüft; das Ergebnis liegt als Eingabe in `belege/DZ_sichtpruefung.json`
(je Punkt der Stichprobe `quelle`, `id`, `lage` ja/daneben/nein, `ansicht` ja/nein/unklar; Ortofotomapa Geoportal,
Quelle je Punkt verdeckt). Festgelegt wird die Auswertung, bevor gerechnet wird:

- Eingabe gültig nur, wenn der Startwert 20261114 ist, jede Antwort genau einen Punkt der Stichprobe trifft (gleiche
  `quelle` und `id`), jeder Punkt der Stichprobe genau eine Antwort hat und alle Werte aus den Listen oben stammen;
  sonst bricht `skripte/dz_denkmale.py` ab und schreibt nichts.
- **Lage-Quote = ja / alle Antworten** (ja + daneben + nein). „daneben“ zählt nicht als ja; „nein“ bleibt im Nenner.
- **Ansicht-Quote = ja / entschiedene Antworten** (ja + nein); „unklar“ fällt aus dem Nenner und wird mit seiner Zahl
  genannt.
- Je Quelle (Wikidata n = 20, OSM n = 20) und gesamt (n = 40), jeweils mit 95-%-Intervall nach Wilson (z = 1,959964).
- Gespeichert mit einer Nachkommastelle; auf den Seiten ganzzahlig, gerundet nach `Intl.NumberFormat` (0,5 aufwärts).
- Die Quote ist eine Aussage über die Ebene, gewonnen aus einer Zufallsstichprobe, nicht über den einzelnen Punkt. In
  den Downloads bleibt `polozenie_sprawdzone` je Punkt 0 (kein Punkt außerhalb der Stichprobe ist einzeln geprüft;
  die Kennungen der Stichprobe stehen nur in `belege/`).
- Bauzeitklasse und Zuordnung zum Gebäude waren nicht Gegenstand der Runde und bleiben als ungeprüft bezeichnet.
- In `daten/` steht kein Name des Prüfers, nur die Art der Prüfung (Sichtprüfung am Luftbild), die Grundlage
  (Ortofotomapa) und das Datum. Die Datei `denkmale.js` trägt nur das Ergebnis der Wikidata-Punkte; das
  Gesamtergebnis (es enthält OSM-Punkte) steht in `denkmale_odbl.js` und im Beleg.
- Ohne Eingabedatei bleibt alles wie vor diesem Nachtrag (`sichtpruefung.geprueft: false`, Hinweis „ungeprüft“).
