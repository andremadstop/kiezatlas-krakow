# Behebung der offenen Funde vom 14.11.2026 (Bereich „offen“)

Stand 14.11.2026, Zweig `Arbeitszweig fix-offen` (von `Arbeitszweig integration` `dd7d2e5`). Jeder Fund ist zuerst nachgeprüft
worden; echte Funde sind je in einem eigenen Commit behoben. Nummern und Status in `docs/entscheidungen.md` setzt die
Belegschicht; dieses Dokument schlägt keine neue KR-Nummer vor.

## 1. Funde und Ergebnis

| Nr | Fund (Quelle) | Nachprüfung | Ergebnis |
|---|---|---|---|
| 1 | Name der Startgewicht-Prüfung (korrektheit) | bestätigt: `N1_daten.py` zählt nur `<script src>`; mit HTML und Stylesheets 313.351 B gz | behoben `945d518`: Prüfzeile „JavaScript-Startgewicht“, Gewicht mit HTML und CSS zur Information; README nennt keine Startseiten-Grenze |
| 2 | 3D ohne `MANIFEST.sha256`, Entwicklungsserver prüft keine SHA256 (korrektheit) | bestätigt | behoben `6b4e819`: Server prüft SHA256 beim Start, `20_bdot10k.py --geometrie` schreibt künftig `MANIFEST.sha256`, `--pruefen` vergleicht `SHA256SUMS` byte-gleich (Lauf: byte-gleich, rc=0); Name im alten Ordner in KR42 begründet |
| 3 | keine Sicherheits-Header (sicherheit) | bestätigt (0 von 54 Seiten, keine Header in den Anleitungen) | behoben `5ddc4b2`, `844f970`: Header-Block in `docs/auslieferung.md`, `running.md`, `uruchomienie.md`; `deploy_kopie.py` gibt den Hash des Inline-Skripts aus. Browserprobe siehe Abschnitt 3 |
| 4 | Bestandsaufnahme Geheimnisse und Reste (sicherheit) | bestätigt als Bestandsaufnahme ohne neuen Befund | **ohne Änderung geschlossen.** Vor einer Veröffentlichung nur der bereinigte Export (`docs/entscheidungen/O.md`, KR50), nie der Rohstand der Historie |
| 5 | ZBK-Werte ohne Haftungsklausel (lizenz) | bestätigt für Startseite, Steckbrief, Karte | behoben `7a9fb17`, `b3c83c6`: Vermerk und Klausel auf allen drei; `pruefen/seiten.mjs` prüft jede Seite mit `sanierung*.js` und `karta.html#dz=zbk`, `#pkt=zbk`. Langtexte (`dane`, `kamienice_dane`) und `daten/pobierz/licencje.csv` tragen Vermerk und Klausel schon |
| 6 | NOTICE ohne Kerning-Änderung (lizenz) | bestätigt | behoben `adcbcc7` |
| 7 | GSAP wird ausgeliefert (lizenz) | bestätigt (`ORDNER` mit `vendor`) | behoben `fcc610e`: `AUSSER_DATEIEN`; Deploy-Kopie vom 14.11.2026 enthält unter `vendor/` nur MapLibre und Begleittexte |
| 8 | Inhaltsangabe zu einem nicht gelesenen Artikel (professorin) | bestätigt | behoben `4c8e27e`: nur bibliographisch; kein Abruf (Verlagstext, Lizenz ungeklärt) |
| 9 | kamienica als „Gründerzeit-Mietshaus“ (professorin) | bestätigt; kein Text nutzte die Form | behoben `6cc7809` |
| 10 | modernizacja ohne Modernisierungsinhalte (professorin) | bestätigt als Lücke | behoben `537c124`: Vorspann nennt den Umfang; GPR-Gebiete und Oberflächentemperatur als offene Quellen in `docs/entscheidungen.md` („Nicht geprüft“) |
| 11 | Jährliches Aktualisieren nicht ausführbar (betreiber) | bestätigt (`quellen: {}`) | teilweise behoben `2c107eb`, `16e069d`: Rundgang listet je Quelle die festgeschriebenen Orte, Weg A mit `$STAND`. **Offen:** zentrale Führung in `config/krakow.yaml` (`quellen`) |
| 12 | HALT nach Weg C nicht angekündigt, DF_grundkarte unzuverlässig (betreiber) | bestätigt aus dem Protokoll des Funds; ERR_ABORTED bei Kacheln ist ein Abbruch durch MapLibre | behoben `cfe3450` (Anleitungen), `b915bda` (Prüfung zählt abgebrochene Kachelabrufe nur) |
| 13 | Bezugsadresse der Pipeline fehlt (betreiber) | bestätigt | als offene Übergabehürde benannt `b27d3d0`; **Entscheidung beim Herausgeber**, ob und wo das Repository öffentlich wird |
| 14 | npm-Angaben, BIP-Seite als Pflichteingang (betreiber) | npm: über `skripte/abruf.py` abgerufen, byte-gleich (`belege/fix-offen_npm_versioniert.log`); BIP: bestätigt | behoben `51644b3`, `fe3754e`: Anleitungen; `35_klimat.py` und `kette.py` ohne BIP-Seite nur ohne Gegenprobe (Datendateien byte-gleich mit und ohne) |
| 15 | Handdownloads an eine Person gerichtet (betreiber) | bestätigt | behoben `8dff134`. **Offen:** Dateinamen `quellen-<Paket>.md` umbenennen |
| 16 | Ungenauigkeiten der Übernahme-Anleitungen (betreiber) | (1)–(4) bestätigt | behoben `6b3b7de` (Weg A in `running.md`), `643af1e` (`package.json`, 54 + 54), `1f8d4cf` (README-Zeiten mit Verweis auf `running.md` Abschnitt 6) |

## 2. Eigentum

Geändert im Auftrag der Behebung, Eigentümer laut `docs/rundgang.md`:

| Datei | Eigentümer | Fund |
|---|---|---|
| `pruefen/N1_daten.py`, `pruefen.sh` (Bezeichnung) | Nacharbeit N1, Belegschicht | 1 |
| `skripte/entwicklung_server.mjs`, `pruefen/N2_auslieferung.mjs` | Schrift und Grundkarte, Nacharbeit N2 | 2 |
| `skripte/20_bdot10k.py` | Gebäude und Kamienice | 2 |
| `skripte/deploy_kopie.py`, `docs/auslieferung.md` | Deploy | 3, 7 |
| `karta.js`, `dzielnica.js`, `erzaehlung.js`, `pruefen/seiten.mjs` | Seitenpakete S1, S2; Belegschicht | 5 |
| `NOTICE`, `vendor/README.txt` | Integration | 6, 7 |
| `texte/<lang>/bloecke/quelle/kamienice_metoda.html`, `pruefen/S4_bloecke.py` | Seitenpaket S4 | 8 |
| `texte/<lang>/sanierung.js` | Sanierungsatlas (Seiten) | 10 |
| `skripte/35_klimat.py`, `skripte/kette.py` | Klima, Integration | 14 |
| `pruefen/DF_grundkarte.mjs` | Belegschicht | 12 |
| `docs/*.md`, `quellen-*.md`, `DESIGN.md`, `package*.json`, `README.md` | Belegschicht, Integration | 9–16 |
| erzeugte Seiten und Langtexte | `skripte/30_seiten.py`, `skripte/16_bloecke_krakow.py` | 8, 10 |

## 3. Belege der Behebung

- 3D-Manifest: `20_bdot10k.py --pruefen --geometrie $KIEZ_DATEN/abgeleitet/gebaeude/2026-11-13-odbl` am 14.11.2026:
  „byte-gleich: … 18_odbl.js, SHA256SUMS“, rc=0.
- Sicherheits-Header: Playwright mit dem vorgeschlagenen Header, einmal über `skripte/entwicklung_server.mjs` (15
  Seiten, ohne Inline-Skript) und einmal über eine Deploy-Kopie (`deploy_kopie.py --unverkleinert`, 11 Seiten, mit
  dem ausgegebenen Hash): keine Verletzung, `window.KIEZ_V` gesetzt, Karte gezeichnet. Gegenproben: ohne `worker-src
  blob:` und mit falschem Hash meldet der Browser die Verletzung. Die verkleinerte Fassung (esbuild) ist nicht
  geprüft; der Hash hängt nur an der Inline-Zeile, nicht am verkleinerten Code.
- npm-Angaben: `belege/fix-offen_npm_versioniert.log`. Der Abruf lief mit einem eigenen `KIEZ_DATEN` außerhalb von
  `kiezatlas-daten/` (dort nur lesen); er steht darum nicht im gemeinsamen Abrufprotokoll.
- In `docs/entscheidungen/O.md` („Funde für andere Eigentümer“) sind damit erledigt: `35_klimat.py` bricht ohne
  BIP-Seite ab; npm-Angaben unter `*-latest.json`; GSAP unter `vendor/` (nicht mehr ausgeliefert). O.md selbst
  bleibt unverändert.

## 4. Offen

- Zentrale Pfade und Stände in `config/krakow.yaml` (`quellen`) statt fest im Code (Fund 11).
- Dateinamen `quellen-<Paket>.md` tragen interne Paketkennungen; Umbenennen berührt Verweise in Anleitungen und
  Prüfungen (Fund 15).
- Bezugsadresse der Geodaten-Import-Pipeline und des Potsdamer Repos, öffentlich oder nicht (Fund 13).
- Verbliebene Personennamen in Betreiber-Texten: `docs/rundgang.md` (Rechtspunkt mit Vornamen), Text, den
  `skripte/12_osm.py` in `HERKUNFT.md` schreibt, und `skripte/36_sanierung.py` (Beleg `DS_sanierung_lauf.md`, müsste
  neu erzeugt werden); Kommentare mit Vornamen in Potsdamer Modulen (`atlas.js`, `karte.js`, `jahre.js`, CSS).
- Ob `./atlas.sh alles --ab pruefen` nach Weg C mit den Dateien aus Weg A grün endet, ist nicht geprüft.
