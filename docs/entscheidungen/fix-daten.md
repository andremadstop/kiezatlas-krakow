# Behebung Bereich Daten (14.11.2026)

Stand 14.11.2026, vom Integrationsstand `dd7d2e5` aus. Acht Funde aus der Prüfung vom 14.11.2026 zum Bereich Daten,
jeder zuerst nachgeprüft, dann behoben, je Fund ein Commit. Keine neue KR-Nummer; Übernahme nach
`docs/entscheidungen.md` macht die Belegschicht.

## 1. Eigentum

Die Dateien gehören anderen Paketen und wurden im Auftrag der Behebung geändert:

| Datei | Eigentümer laut `docs/rundgang.md` | Änderung (Fund) |
|---|---|---|
| `skripte/40_mieszkania.py`, `pruefen/DW_mieszkania.py`, `daten/mieszkania_odbl.js`, `belege/DW_mieszkania.md` | Wohnungsmarkt | Rückrechnung über F10 und `ohne_markt` (2.1) |
| `pruefen/N1_protokoll.md` | Daten-Nacharbeit | Nachtrag 3 zu Regel 4 (2.1) |
| `skripte/entwicklung_server.mjs`, `pruefen/N2_auslieferung.mjs` | Schrift und Grundkarte, Oberfläche und Auslieferung | Freigabeliste und Host-Kopf (2.2), Stand der 3D-Dateien (2.6) |
| `skripte/deploy_kopie.py`, `skripte/20_bdot10k.py`, `pruefen.sh`, `pruefen/S2_seiten.mjs`, `docs/uruchomienie.md`, `docs/running.md`, `docs/rundgang.md` | Deploy, Gebäude, Belegschicht, Seitenpaket S2 | 3D-Dateien (2.6) |
| `skripte/36_sanierung.py`, `daten/sanierung*.js`, `daten/schema/sanierung*.json`, `belege/DS_sanierung_lauf.md`, `pruefen/DS_protokoll.md`, `QUELLEN.md`, `quellen-DS.md`, `texte/<lang>/sanierung.js`, `sanierungsatlas.js` | Sanierungsatlas, Seitenpaket S2 | Ortsmarke (2.3), Typologie (2.4, 2.8) |
| `skripte/oeffentlich_pruefen.py` | Integration | Projektname in auslieferbaren Dateien (2.3) |
| `skripte/dz_denkmale.py`, `daten/denkmale_odbl.js`, `belege/DZ_denkmale_lauf.md`, `pruefen/DZ_protokoll.md`, `texte/<lang>/kamienice.js` | Denkmale | Relationen (2.5), Stichprobe (2.7) |
| `daten/pobierz/`, `texte/<lang>/bloecke/`, `belege/S2_seiten_zaehlungen.md`, erzeugte Seiten | Erzeuger | neu erzeugt |

Neu: `config/gebaeude_3d.json` (Stand und Prüfsumme der 3D-Dateien), `belege/DS_sichtpruefung.json` (Ergebnis der
Sichtprüfung als Eingabe), dieses Dokument.

Rohdaten unter `kiezatlas-daten/` blieben unberührt. `36_sanierung.py` schreibt `abgeleitet/sanierung/zbk_tabelle.tsv`;
die Läufe liefen deshalb gegen ein Ersatzverzeichnis, das die Rohdaten verlinkt und `abgeleitet/sanierung/` in einem
Zwischenordner hält. Die Tabelle kam byte-gleich heraus. Die 3D-Dateien wurden in einen Zwischenordner neu erzeugt.

## 2. Funde

### 2.1 Wohnungsmarkt: unterdrückte Fallzahl über F10 zurückrechenbar (bestätigt, behoben)

- **Nachgeprüft:** Am Integrationsstand ergibt F10 3442 minus die Stadtzahlen der übrigen Jahre (2856) die verdeckte
  Stadtzahl 2025 (586), daraus dzielnica 18, 2025, `ogolem` = 7. Die neue Prüfung findet in der alten Datei genau
  diese 1 Zahl.
- **Behoben:** `pruefen/N1_protokoll.md`, Nachtrag 3: Das ganze veröffentlichte Gleichungssystem mit Schranken gilt.
  Der Erzeuger rechnet je unterdrückter Zahl Minimum und Maximum ganzzahlig (`scipy.optimize.milp`) und verdeckt, bis
  keine festliegt. Die Prüfung rechnet unabhängig mit `linprog`, Gegenproben auf erfundenen Tabellen je Weg (Stadt
  minus dzielnica, F10, `ohne_markt`). Ergebnis in den Beispieldaten: verdeckt ist jetzt dzielnica 14, 2025,
  `ogolem` statt der Stadtzahl 2025.
- **Offen:** Die absoluten Zählungen in `kontrolle` bleiben veröffentlicht. Bei echten RCN-Daten entscheidet der
  Erzeuger neu; die Zahl der verdeckten Felder kann steigen.

### 2.2 Entwicklungsserver liefert die ganze Repo-Wurzel aus (bestätigt, behoben)

- **Nachgeprüft:** `/.env.beispiel`, `/.git/config`, `/node_modules/.package-lock.json`, `/package.json` gaben 200;
  ein fremder Host-Kopf wurde angenommen.
- **Behoben:** Freigabeliste wie `skripte/deploy_kopie.py`, Pfadteile mit Punkt am Anfang 404, Host-Kopf nur
  `127.0.0.1:<port>` oder `localhost:<port>`, sonst 403. Prüfung in `pruefen/N2_auslieferung.mjs` (Teil 0, ohne
  Browser, nur Statuscodes); gegen den alten Server schlägt sie an.
- **Offen:** Die Prüfserver in `pruefen/seiten.mjs` und `pruefen/S2_seiten.mjs` liefern während des Prüflaufs weiter
  die Wurzel aus (nur 127.0.0.1, nur solange die Prüfung läuft).

### 2.3 Projektname an der Ortsmarke (bestätigt, behoben)

- **Nachgeprüft:** `daten/sanierung.js`, `ortsmarke.quelle` trug die URL des Ausgangsprojekts.
- **Behoben:** Feld entfällt (Erzeuger und Vertrag); QUELLEN.md und `quellen-DS.md` führen die Seite nur noch als
  Vergleichsangabe im Beleg. `skripte/oeffentlich_pruefen.py` meldet den Namen in auslieferbaren Dateien.

### 2.4 Typologie zählt kamienice im Stadtkern mit (bestätigt, gemessen, ausgewiesen)

- **Nachgeprüft:** dzielnica I: 238 Kandidaten, 65 in Großsiedlungen (wie gemeldet).
- **Gemessen:** neue Kennzahl „angebaut“ (gemeinsame Grenze ≥ 3 m mit einem anderen BDOT10k-Gebäude). In dzielnica I
  sind 223 von 238 Kandidaten angebaut und alle 65 Großsiedlungs-Kandidaten; in den Plattenbau-Stadtteilen XIV bis
  XVII fast keine (Zahlen je dzielnica im Beleg `belege/DS_sanierung_lauf.md`).
- **Behoben:** eigene Spalte auf der Seite, Grenztext nennt kamienice der Blockrandbebauung und die Ziegelbauten in
  Nowa Huta (`pruefen/DS_protokoll.md`, Nachtrag 5). Die Regel bleibt.
- **Vorschlag, offen:** „angebaut“ als Ausschlussregel erst nach einer nach dzielnica geschichteten Stichprobe; sie
  könnte Blöcke aus mehreren aneinandergebauten Teilen mit abtrennen.

### 2.5 Kamienice: OSM-Relationen fehlten (bestätigt, behoben)

- **Nachgeprüft:** `relation_wahl=lambda t: False` in `skripte/dz_denkmale.py`.
- **Behoben:** Multipolygone mit `heritage` oder `start_date` werden gelesen (Nachtrag 1 im DZ-Protokoll). heritage
  167 → 184, Mehrfamilienhäuser mit heritage 8 → 9. Von den 184 heritage-Objekten treffen 143 ein BDOT10k-Gebäude,
  29 ein Wohngebäude, 9 ein Mehrfamilienhaus. Die Kennzahl heißt jetzt „Mehrfamilienhäuser (BDOT10k) mit
  Denkmal-Kennzeichnung in OpenStreetMap“.
- **Offen:** Eine belastbare Zahl der kamienice braucht das NID-Register (Handdownload).

### 2.6 3D-Dateien eines neuen Laufs wurden nicht ausgeliefert (bestätigt, behoben)

- **Nachgeprüft:** Server und Deploy lasen fest `2026-11-13-odbl/`, `20_bdot10k.py --geometrie` schrieb kein Manifest.
- **Behoben:** `20_bdot10k.py --geometrie` schreibt `SHA256SUMS` (gegen den Bestand byte-gleich, SHA256 des Manifests
  wie festgeschrieben). Stand und Prüfsumme in `config/gebaeude_3d.json`; ohne Manifest im Stand-Ordner gilt der
  jüngste `*-odbl/` mit Manifest. Gegenprobe: frischer Lauf in einem Ersatzverzeichnis, Server liefert 18 Dateien,
  die Deploy-Kopie nimmt den Ordner an. `--gebaeude` steht in beiden Anleitungen.

### 2.7 Denkmal-Stichprobe aus Treffern ohne heritage (bestätigt, behoben)

- **Behoben:** Stichprobe nur aus Gebäudetreffern mit `heritage`, Startwert und Umfang gleich (Nachtrag 2 im
  DZ-Protokoll). In der neuen Liste keine Klasse `ab_1990` mehr. `sichtpruefung.geprueft` bleibt `false`.

### 2.8 Sichtprüfung der Typologie eingetragen (behoben)

- Eingabe `belege/DS_sichtpruefung.json` (Zählungen, Prüfer, Datum), vom Erzeuger gegen die Stichprobe geprüft;
  Quote und Wilson-Intervall rechnet der Erzeuger. Die Seite zeigt das Ergebnis; Texte sagen „nach Geometrie“ statt
  Bauweise.
- **Offen:** Die Einzelergebnisse je Punkt liegen nicht vor. Die Wirkung einer strengeren Geschoss-Untergrenze ist
  deshalb nur als Spanne belegt; die Regel bleibt.
