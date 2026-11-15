# Vorschläge des Pakets Denkmale und Kamienice

Stand 13.11.2026, Zweig `Arbeitszweig dz`. Regeln des Pakets: `pruefen/DZ_protokoll.md`. Quellen und Lizenzen:
`quellen-DZ.md`. Lauf und Zählungen: `belege/DZ_denkmale_lauf.md`. Vorschläge ohne KR-Nummer; die Nummer vergibt
die Belegschicht.

## 1. Eigentum an den neuen Dateien

- **Anlass:** Die Eigentümer-Tabelle in `docs/rundgang.md` kennt das Paket noch nicht.
- **Vorschlag:** neue Zeile „Paket Denkmale und Kamienice“ mit
  - `skripte/dz_denkmale.py`
  - `daten/denkmale.js`, `daten/denkmale_bdot.js`, `daten/denkmale_odbl.js` und die Verträge
    `daten/schema/denkmale.json`, `daten/schema/denkmale_bdot.json`, `daten/schema/denkmale_odbl.json`
  - `pruefen/DZ_denkmale.py`, `pruefen/DZ_test_eingang.py`, `pruefen/DZ_protokoll.md`
  - `belege/DZ_denkmale_lauf.md` (erzeugt, nicht von Hand ändern), `belege/rohdaten-dz-2026-11-13.sha256` (1 Datei)
  - `quellen-DZ.md`, `docs/entscheidungen/DZ.md`, `docs/entscheidungen/DZ-texte/<lang>/denkmale.js` (Vorschlag, siehe 2)
- Gemeinsame Dateien hat das Paket nicht geändert.

## 2. Neuer Namensraum `denkmale.*` (Vertragsänderung, nicht im Paket gemacht)

- **Anlass:** Begriffe und Legenden des Themas brauchen Texte in pl/en/de. `daten/schema/texte.md` lässt neue
  Namensräume nur über die Integration zu, und `pruefen/texte.py` meldet Schlüssel, die keine Seite verwendet
  (Regel 6). Eine Datei `texte/<lang>/denkmale.js` würde `pruefen.sh` darum rot machen, solange es keine Seite gibt.
- **Vorschlag:** Die Integration nimmt `denkmale.*` mit Eigentümer „Paket Denkmale und Kamienice“ in die Tabelle
  „Namensräume und Eigentum“ auf. Die fertigen Dateien liegen unter `docs/entscheidungen/DZ-texte/<lang>/denkmale.js`
  (31 Schlüssel je Sprache, gleiche Schlüssel und Platzhalter in allen drei Sprachen, Pluralformen nach Sprache).
  Verschoben nach `texte/<lang>/` werden sie in Phase Seitenbau zusammen mit der Seite, die sie verwendet.
- **Verworfen:** die Begriffe in `kamienice.*` einzutragen. Den Namensraum besitzt das Paket Seiten Kamienice und
  Planer, und die Begriffe gelten auch auf Karte und Steckbrief.

## 3. Wikidata und Overpass bleiben Handdownload, solange `skripte/abruf.py` sie sperrt

- **Anlass:** Der Auftrag des Pakets nennt WDQS (mit der Kennung des Abrufskripts) und kleine Overpass-Abfragen als
  zulässig. `skripte/abruf.py`, der einzige Netzweg, sperrt aber `query.wikidata.org`, `www.wikidata.org` und
  `overpass-api.de` ausdrücklich (Sperrliste `GESPERRT`, Gründe: „Wikidata nur als Handdownload
  (Machbarkeitsprobe 13.11.2026, offene Handdownloads Nr. 6)“ und der OSM-Grund). Die Datei gehört nicht dem Paket.
- **Vorschlag:** Bis die Integration die Sperre aufhebt, liest das Skript Wikidata und OSM nur aus `eingang/`
  (Dateinamen, Formate und die WDQS-Abfrage stehen in `quellen-DZ.md`). Hebt sie sie auf, braucht es nur einen
  Abruf je Quelle, der die Datei unter demselben Namen in `eingang/` ablegt. `dz_denkmale.py` bleibt dabei ohne Netz.
- **Begründung:** vorsichtigere Lesart. Die Sperrliste ist eine bewusste Entscheidung aus der Machbarkeitsprobe, und
  eine Ausnahme im Paket würde den einzigen Netzweg umgehen.
- **Neu prüfen, wenn:** die Integration `abruf.py` ändert.

## 4. Begriffe (Arbeitsdefinitionen aus dem Prüfprotokoll)

- **Kamienica im Atlas** = Mehrfamilienhaus laut BDOT10k (`FOBUD` „budynki mieszkalne“, `PFBUD` „budynek
  wielorodzinny“) mit Denkmalbezug, also einem Treffer aus Register oder OSM-Denkmalangabe im Umriss oder bis 10 m.
  Ein Gebäudename „Kamienica …“ in BDOT10k zählt getrennt als **Namensbezug**, nicht als Denkmal.
- **Nur Bauzeitklassen**, nie Einzeljahre, auch bei Nicht-Wohngebäuden. Das ist die vorsichtigere Lesart von
  Punkt 30 der Checkliste.
- **Teilmenge, keine Flächenaussage:** `teilmenge: true` und `flaechenaussage: false` stehen in allen drei Dateien,
  die Verträge erzwingen beide Werte.
- **Verworfen:** BDOT10k-Komplexe `OT_KUZA_A` als Denkmalflächen zu zählen. Das sind Flächen der Topographie,
  kein Register.

## 5. Ortsmarke ul. Kościuszki 18 und der Bezug zu FuturHist

- **Anlass:** Das Paket soll den Ausgangsfall der FuturHist-Demo als Ortsmarke mit Quelle zeigen.
- **Vorschlag:** Die Ortsmarke bekommt eine Lage nur aus einer Quelle, die die Adresse trägt (heute nur OSM
  `addr:street`/`addr:housenumber` im Handdownload), immer mit `lage_geprueft: false`. Ohne Quelle bleibt sie
  `geometry: null`. Keine Geokodierung, keine Koordinate aus dem Gedächtnis. Der Text heißt nur „ul. Kościuszki 18“.
- **Begründung:** Für den Bezug zu FuturHist gibt es im Repo keine öffentliche, zitierfähige Quelle; er steht nur
  in der internen Bauvorlage. Der Name FuturHist erscheint deshalb nicht in Daten und Texten, bis eine Quelle
  vorliegt (als offen gemeldet). Laut Bauvorlage ist auch die Lage in der Dzielnica VII Zwierzyniec ungeprüft.

## 6. Berichtigung im Prüfprotokoll

- `pruefen/DZ_protokoll.md` nannte als Ergebnisdatei `belege/DZ_denkmale.md`. Das Skript schreibt aber
  `belege/DZ_denkmale_lauf.md`. Am 13.11.2026 wurde nur der Dateiname berichtigt, an den Regeln ändert sich nichts.

## 7. Aufnahme in `pruefen.sh` (Belegschicht)

| Prüfung | Aufruf | braucht |
|---|---|---|
| Paketregeln ohne Rohdaten | `python -I pruefen/DZ_denkmale.py` | nichts |
| Codepfade der Handdownload-Leser (erfundene Eingänge) | `python -I pruefen/DZ_test_eingang.py` | nichts |
| Reproduzierbarkeit aus Rohdaten (rund 7 s) | `python -I skripte/dz_denkmale.py --pruefen` | `$KIEZ_DATEN` mit BDOT10k 1261; ohne Rohdaten übersprungen |

Die Prüfsummen `belege/rohdaten-dz-2026-11-13.sha256` prüft `pruefen.sh` schon.

## 8. Befund zur Zahl „Mehrfamilienhäuser in historischem Bauensemble = 0“

- Die Null ist kein Rechenfehler. Die 17 Flächen „zespół zabudowy historycznej“ in `OT_KUZA_A` sind Palast-, Park-
  und Gutsanlagen (u. a. Wawel, Błonia, Park Jordana, Pałac Decjusza), keine Stadtquartiere. Die Gebäude mit
  Schwerpunkt darin sind vor allem Museen und Nebengebäude. Das ergab eine Diagnose am 13.11.2026, die nicht als
  Skript im Repo liegt; die Zählung selbst steht im Beleg.
- Nebenbefund: `PFBUD` kennt den Wert „zabytek niepełniący żadnej funkcji użytkowej“ (Denkmal ohne Nutzung). Das
  ist kein allgemeines Denkmal-Merkmal und wird nicht verwendet. Wie oft der Wert vorkommt, ist nicht gezählt.

Nachtrag 14.11.2026 (Paket Oberfläche und Auslieferung): Die Textdateien liegen seit dem Seitenpaket `Arbeitszweig s2` unter
`texte/<lang>/denkmale.js` (mit `git mv` verschoben, KR14, KR41); der Ordner `docs/entscheidungen/DZ-texte/` ist
nicht mehr in Git.

## 9. Register auf die Seiten, zweite Stichprobe (Vorschlag, 14.11.2026)

- **Anlass:** `daten/denkmale.js` ist seit dem 14.11.2026 echt (nur Wikidata), wurde aber von keiner Seite geladen.
- **Vorschlag:** Die Seite `kamienice` zeigt die Registerpunkte je Delegatura neben der OSM-Kennzeichnung, die
  freie Karte hat zwei getrennte Ebenen (Register aus Wikidata, CC0; OSM-Kennzeichnung, ODbL), die Downloads eine
  Ebene der Registerpunkte im GeoPackage ohne OSM-Anteil. Vorher legt Nachtrag 3 im Prüfprotokoll eine zweite
  Stichprobe fest (Startwert 20261114, 20 + 20 Punkte aus genau der gezeigten Menge, nur Lage und Ansicht).
- **Name der Kennzahl:** Ein Punkt ist nicht ein Denkmal und nicht ein Registereintrag, sondern eine Gruppe von
  Wikidata-Objekten mit derselben polnischen Registernummer (P3424), mit Koordinate in der Stadt; die Gruppe liegt an
  der Koordinate ihres ersten Objekts (nach Kennung). Beispiel: 56 Objekte mit der Nummer A-893 sind ein Punkt.
  Die Seiten sagen deshalb „Registerpunkte (Wikidata-Objekte mit Registernummer, gleiche Nummer als ein Punkt)“ und
  zählen auch die Bauzeitklassen an den Punkten, nicht am Zähler `zaehlung.wd.bauzeit_lesbar` (der zählt nur das
  erste Objekt einer Gruppe: 873 gegen 972 Punkte mit Klasse).
- **Ersetzt:** den Teil von KR43, nach dem `daten/denkmale.js` auf `kamienice` nicht geladen wird (damals
  Beispieldaten). Die KR-Nummer für diesen Vorschlag vergibt die Belegschicht.
- **Datenvertrag:** `daten/schema/denkmale.json` bekommt `quellen.wd.vermerk` (wörtlich „Wikidata, CC0 1.0“, für
  Karte, Seite und Downloads) und `sichtpruefung` wie in `denkmale_odbl.json`.
- **Verworfen:** die Registerpunkte in die bestehende Ebene `zabytki` zu mischen. Lizenz, Herkunft und Prüfstand
  sind verschieden; gemischt könnte niemand sagen, woher ein Punkt stammt.
