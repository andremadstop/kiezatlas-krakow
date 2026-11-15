# Entscheidungsvorschläge des Pakets Offene Wissenschaft (O, 14.11.2026)

Ziel des Pakets: Das Rezept so herrichten, dass eine Hochschule es ohne die Herausgeberin betreiben und
weiterentwickeln kann (Lizenzen, Betriebsanleitung, ein Befehl für die Kette, neue Stadt, Zitierbarkeit,
Rohdaten-Schnappschuss, Übergabe, Prüfung vor Veröffentlichung, CI). Alle Punkte sind Vorschläge ohne KR-Nummer;
die Nummer vergibt die Belegschicht.

## Dateien des Pakets (Eigentum)

Der Auftrag nennt Dateien, die laut `docs/rundgang.md` („Eigentümer je Datei“) der Belegschicht gehören. Sie sind
hier nur in dem Umfang geändert, den der Auftrag ausdrücklich nennt; die Bestätigung durch die Belegschicht steht aus.

| Datei | Eigentümer bisher | Stand |
|---|---|---|
| `docs/entscheidungen/O.md` | neu | dieses Dokument |
| `atlas.sh`, `skripte/atlas.sh`, `skripte/kette.py` | neu | ein Befehl für die Kette; Vorschlag: Eigentümer dieses Paket, danach Integration |
| `skripte/schnappschuss.py` | neu | Rohdaten-Schnappschuss; Vorschlag: dieses Paket, danach Integration |
| `skripte/oeffentlich_pruefen.py`, `skripte/oeffentlich_ausnahmen.tsv` | neu | Prüfung vor Veröffentlichung; Vorschlag: dieses Paket, danach Belegschicht (wie die übrigen Prüfungen) |
| `.github/workflows/pruefen.yml` | neu | CI ohne Rohdaten; Vorschlag: Belegschicht |
| `.zenodo.json` | neu | Vorschlag: Belegschicht (wie `CITATION.cff`) |
| `docs/uruchomienie.md`, `docs/running.md`, `docs/nowe-miasto.md`, `docs/new-city.md`, `docs/przekazanie.md` | neu, fallen unter `docs/*.md` (Belegschicht) | im Auftrag angelegt |
| `NOTICE` | Belegschicht | im Auftrag neu gefasst: Datenabschnitt nach dem Echtlauf (der alte Satz „nur Beispieldaten“ war überholt), GSAP als nicht freier Bestandteil, Werkzeuge außerhalb |
| `README.md` | Belegschicht | im Auftrag nur zwei Abschnitte: „Uruchom u siebie / Run it yourself / Selbst betreiben“ neu, „Lizenz“ als Tabelle Code gegen Daten; README-Kasten unverändert |
| `CITATION.cff` | Belegschicht | unverändert, mit `cffconvert 2.0.0` (lokaler uv-Zwischenspeicher, ohne Netz) gegen CFF 1.2.0 geprüft: „Citation metadata are valid according to schema version 1.2.0.“ |
| `LICENSE` | Gerüst | unverändert; Wortlaut byte-gleich mit der `LICENSE` der Geodaten-Import-Pipeline (`cmp`), SHA256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |

Nicht angefasst: `pruefen.sh`, `docs/entscheidungen.md`, `docs/rundgang.md`, `docs/checkliste.md`, `QUELLEN.md`,
`daten/LIZENZ.md`, `CHANGELOG.md`, `belege/`, alle Skripte und Daten anderer Pakete, `kiezatlas-daten/` (nur gelesen;
der Schnappschuss liegt im Zwischenordner der Sitzung, nicht unter `abgeleitet/`).

## Ein Befehl für die ganze Kette (`./atlas.sh`, `skripte/kette.py`)

- **Anlass:** Die Kette bestand aus 24 Einzelaufrufen, deren Reihenfolge nur in `docs/rundgang.md` stand.
- **Vorschlag:** `./atlas.sh trocken | alles | liste` ruft die vorhandenen Skripte in der Reihenfolge des Rundgangs
  auf (Datenpakete, Vergleich, Export, Langtexte, zuletzt `30_seiten.py`, dann `./pruefen.sh`). Vor dem ersten
  Schritt prüft die Kette Werkzeuge, Datenbank (nur lesend: `.env` vorhanden, Container gesund) und alle Eingänge;
  fehlt ein Pflichteingang, hält sie mit einer Liste an (Rückgabe 2, nichts geschrieben). Fehlt nur ein Handdownload,
  mit dem ein Schritt umgehen kann, ist das ein Hinweis. Halt beim ersten Fehler mit dem Befehl zum Wiederaufsetzen
  (`--ab <schritt>`). Nur Python-Standardbibliothek, damit der Trockenlauf auch vor dem ersten `uv` läuft.
- **Gemessen:** Trockenlauf gegen `$KIEZ_DATEN` grün mit 6 Hinweisen (rejony, EEA, RCN, drei Register), 0,3 s;
  gegen einen leeren Ordner Halt mit 13 Punkten (12 Pflichteingänge, `.env`); `alles --nur ort --nur export --nur
  bloecke --nur seiten` echt ausgeführt, Arbeitsbaum danach unverändert (byte-gleiche Ausgaben).
- **Nicht ausgeführt:** `./atlas.sh alles` über alle Schritte. Es schriebe Dateien anderer Pakete und die gemeinsame
  Datenbank. `skripte/lauf.sh` sagt ausdrücklich „Nichts läuft alles auf einmal“, weil mehrere Worktrees sich eine
  Datenbank teilen; die Kette ist für einen Betreiber mit eigener Datenbank gedacht. Im parallelen Bau also nur
  `--ohne-datenbank` oder `--nur`.
- **Datenbank-Schritte:** `einrichtungen`, `ziele_db` und `fussweg_export` rufen Python direkt auf; die Kette setzt
  ihnen die Datenbankumgebung wie die Shell-Hüllen `12_osm.sh` und `14b_fussweg.sh` (`.env` lesen, Rolle
  `mosidi_lesen` bzw. `kiezatlas_rechnen`, übrige Passwörter entfernt; im Protokoll nur Variablennamen). Geprüft durch
  genau diese Hülle, nur lesend: `11_einrichtungen_krakow.py --osm-db --pruefen` und `14c_fussweg_export_krakow.py
  --pruefen` gegen die gemeinsame Datenbank, beide „aktuell“. `14a` nicht ausgeführt (leert Tabellen). Der
  Trockenlauf prüft zusätzlich, dass die drei Passwörter in der `.env` gesetzt sind (nicht leer), ohne Werte auszugeben.
- **Verworfen:** Makefile (Halt mit Erklärung je fehlender Datei wäre umständlich, `make -n` zeigt keine Eingänge);
  `skripte/lauf.sh` erweitern (Eigentum Infrastruktur, bewusst schrittweise).

## Rohdaten-Schnappschuss (`skripte/schnappschuss.py`)

- **Vorschlag:** Nur ausdrücklich erlaubte Rohdaten, mit Quelle, Lizenz und wörtlichem Vermerk je Regel: BDOT10k und
  LoD2 (art. 40c ust. 5 und 3), OSM-Auszug (ODbL), Eurostat-Gitter PL und DE (CC BY 4.0), NSP-2021-Tabelle
  (Kopieren mit Quellenangabe), GTFS (CC BY 4.0), Fontsource-Pakete (OFL) und die Kartenschrift Noto Sans aus dem
  Systempaket (OFL, nur wenn die SHA256 zu `27_grundkarte.py` passen; `OFL.txt` mit dem Copyright aus der
  name-Tabelle). Alles andere bleibt draußen und steht mit Grund und SHA256 in `AUSGESCHLOSSEN.md`; was keine Regel
  trifft, gilt vorsichtshalber als ausgeschlossen. Archiv unkomprimiert, byte-gleich wiederholbar (zweimal gebaut,
  gleiche SHA256), vorher Abgleich mit `belege/rohdaten*.sha256`.
- **Ergebnis:** 12 Dateien aus `$KIEZ_DATEN`, 3 Schriftdateien, 4 Begleitdateien, 579 ausgeschlossen; 11 der 12
  gegen `belege/` geprüft, 0 Abweichungen; Archiv `kiezatlas-krakow-rohdaten-2026-11-14.tar`, 403.179.520 B,
  SHA256 `286d70b4ca2b5385e2892f65b015102d8841f8d1b626371888f0e463627ea366` (`--pruefen`: 18 Dateien, 0 Abweichungen).
  Nur lokal im Zwischenordner der Sitzung, nicht hochgeladen.
- **Ausgeschlossen mit Absicht (vorsichtigere Variante):** ZBK-Liste (Autorfeld der PDF nennt Bearbeiter, Spalte
  „Własność“ Bruchteile von Privatpersonen; die Weiterverwendung wäre erlaubt), npm-Paketangaben (E-Mail-Adressen
  der Paketbetreuer), BIP-Seite mit der Stadtfläche (keine Lizenzangabe), MSIP (Lizenz-STOPP, KR3), Webseiten und
  Rechtstexte als Belege, `HERKUNFT.md` (Arbeitsvermerke, eine nennt eine Person), abgeleitete Ausgaben.
- **Gegenprobe mit dem ausgepackten Schnappschuss:** zuerst ohne Zusatzdateien: `02_bevoelkerung.py`,
  `20_bdot10k.py`, `dz_denkmale.py`, `13_oepnv_krakow.py`, `15_planer_krakow.py`, `41_porownanie.py` mit `--pruefen`
  byte-gleich; `35_klimat.py` bricht ohne die BIP-Seite zur Stadtfläche ab (`FileNotFoundError`),
  `skripte/schriften.py` ohne die npm-Angaben, `36_sanierung.py` ohne ZBK-Liste und BIP-Seite der
  Weiterverwendungsregeln. Mit diesen fünf Dateien (Weg A nachgestellt durch Kopie): Trockenlauf grün, `35_klimat.py`,
  `36_sanierung.py`, `schriften.py` mit `--pruefen` byte-gleich, `27_grundkarte.py` mit der Schrift aus dem
  Schnappschuss (`--schrift-ordner`) gleiches `MANIFEST.sha256`. Die Kette führt die fünf als Pflichteingang, die
  Anleitung holt sie per `skripte/abruf.py`.
- **Offen für Andre:** Upload als eigener Zenodo-Eintrag (Veröffentlichung).

## Prüfung vor Veröffentlichung (`skripte/oeffentlich_pruefen.py`)

- **Vorschlag:** Arbeitsbaum (eingecheckt und neu, ohne ignorierte Dateien) auf persönliche Pfade, E-Mail-Adressen,
  Rechnernamen, Geheimnis-Muster, Plankennungen im Fließtext, Dateien über 5 MB und Dateien ohne Lizenzregel. Die
  Rechnernamen liest das Skript zur Laufzeit (eigener Name, Host-Einträge in `~/.ssh/config`, Zusatzliste über
  `$OEFFENTLICH_RECHNER`); sie stehen nicht im Skript, weil es selbst veröffentlicht wird. Begründete Ausnahmen und
  bekannte Stellen anderer Eigentümer stehen in `skripte/oeffentlich_ausnahmen.tsv`; mit `--veroeffentlichung` zählen
  die bekannten Stellen als Befund. Dateinamen wie `belege/D4_*.md` und die Nummern KR1 ff. sind keine Treffer.
- **Ergebnis auf dem Paketstand:** 0 Befunde, 129 begründete Ausnahmen, 198 gemeldete Stellen anderer Eigentümer:
  | Stellen | Was | Eigentümer |
  |---|---|---|
  | 19 | Pfade des Arbeitsrechners (`/home/…`, Zwischenordner) in Prüfprotokollen `belege/*.log` | Belegschicht |
  | 3 | Rechnername des Webservers in `docs/auslieferung.md` und `skripte/deploy_kopie.py` | Deploy |
  | 39 | Bildschirmfotos und Vorschaubilder `belege/**/*.png` ohne Lizenzzeile | Belegschicht |
  | 136 | Arbeitsvermerke des Baus (Tor, Phase, Zweig, Leitungssitzung, P-Nummern) in Entscheidungen, Rundgang, Belegen, Schemata, Kommentaren | Belegschicht, Integration, Pakete |
  | 1 | Tag-Name der Pipeline im Kommentar von `skripte/lauf.sh` | Infrastruktur |
- **Vorschlag Lizenz der Bildschirmfotos:** CC BY 4.0 wie die Schaugrafik, mit den Vermerken BDOT10k und
  OpenStreetMap (ODbL, „Produced Work“) als Zeile in `belege/README.md`.
- **Vorschlag:** Schritt in `pruefen.sh` (Belegschicht); in der CI ist er schon enthalten.

## Git-Historie: Befund und Vorschlag

`python3 -I skripte/oeffentlich_pruefen.py --historie` über alle Zweige (14.11.2026, Stand dieses Zweigs): 310
Commits, 1.623 verschiedene Dateiinhalte, jeder Inhalt jeder Fassung gelesen (nicht nur `git log -p`).

- Keine `.env` und keine andere Umgebungsdatei je eingecheckt; keine Datei über 5 MB.
- Geheimnis-Muster: nur der Platzhalter im Negativtest `pruefen/d1_test_abruf.py` (begründete Ausnahme); 0 sonst.
- Persönliche Pfade: 17 Zeilen `/home/<name>/` und 2 Zeilen Zwischenordner, alle in Prüfprotokollen unter `belege/`.
- Rechnername des Webservers: 9 Zeilen in Fassungen von `docs/auslieferung.md` und `skripte/deploy_kopie.py`.
- E-Mail-Adressen: Rollenadresse der UG (445 Zeilen), Behördenadresse der Stadt (8), Urhebervermerk in GSAP (2).
- **Commit-Metadaten:** alle 310 Commits mit Autor und Committer André Stiebitz und einer persönlichen E-Mail-Adresse
  (hier bewusst nicht wiedergegeben; `git log --format='%an <%ae>'` zeigt sie).
- Commit-Texte mit Arbeitsvermerken: 29 mit Zweignamen, 5 mit „Phase“, 1 mit Leitungssitzung, 1 mit internem Tag;
  dazu 529 Zeilen Arbeitsvermerke in alten Dateifassungen.
- Datendateien früherer Fassungen unter `daten/`: keine Fundstelle „msip“ (geprüft mit `git show` je Commit und Datei).

**Vorschlag (nicht ausgeführt): frischer, bereinigter Export statt der Historie.** Erster öffentlicher Commit aus dem
geprüften Stand, Autor mit Rollenadresse oder ohne Adresse, signiert von Andre; die Arbeitshistorie bleibt intern.
Begründung: persönliche Adresse in jedem Commit, Arbeitsvermerke in Commit-Texten, Pfade in alten Protokollen; die
Regel „nur bereinigter Export“ gilt bei der UG ohnehin. Folge: Die in README und Belegen genannten Commits (etwa
`5f5bf50`, `19634c3`) gibt es öffentlich nicht; der Export braucht einen Satz, dass diese Kennungen die interne
Historie meinen und die Prüfprotokolle mit ihren Kennungen unverändert mitgehen. Verworfen: Historie mit
`git filter-repo` umschreiben (alle Kennungen ändern sich trotzdem, Aufwand und Fehlerrisiko höher, Prüfprotokolle
verweisen auf alte Kennungen); Historie unverändert veröffentlichen (persönliche Adresse, Arbeitsvermerke).

## CI (`.github/workflows/pruefen.yml`)

- **Vorschlag:** Nur Prüfungen ohne Rohdaten, Datenbank, Netz (nach dem Füllen des uv-Zwischenspeichers) und Browser;
  dazu der Trockenlauf (erwartet Rückgabe 2) und die Prüfung vor Veröffentlichung.
- **Gemessen:** `./pruefen.sh --ohne-browser` mit leerem `$KIEZ_DATEN`: 55 Prüfungen, 28 grün, 11 Befunde, 16
  übersprungen; die 11 Befunde sind die 10 Prüfsummenlisten und die Beispieldaten der Denkmale (brauchen BDOT10k).
  Darum spiegelt die CI die grünen Schritte einzeln. Alle Schritte der CI lokal nachgestellt (leeres `$KIEZ_DATEN`,
  YAML mit `yaml.safe_load` gelesen): grün.
- **Vorschlag an die Belegschicht:** Schalter `./pruefen.sh --ohne-rohdaten` (Prüfsummenlisten und Neurechnungen aus
  Rohdaten übersprungen statt Befund), dann ruft die CI nur noch `./pruefen.sh --ohne-browser --ohne-rohdaten` auf.
  Für den Weg über den Schnappschuss dazu `sha256sum -c --ignore-missing` mit Abgleich gegen
  `SCHNAPPSCHUSS/AUSGESCHLOSSEN.md`.
- **Offen:** Actions auf Commit-SHA festschreiben (Tags `actions/checkout@v4`, `actions/setup-node@v4`; ohne Netz
  nicht nachgeschlagen); die CI ist nie auf GitHub gelaufen (GitHub bleibt gesperrt).

## Zitierbarkeit (`CITATION.cff`, `.zenodo.json`)

- `CITATION.cff` bleibt `type: dataset` und ohne Lizenzfeld auf oberster Ebene (KR44, bestätigt).
- `.zenodo.json` (neu, ohne DOI): Eintrag `software`, weil die GitHub-Anbindung von Zenodo das Repository je Tag
  archiviert und das Repository das Rezept ist; Ersteller die UG und André Stiebitz (ohne E-Mail, ohne ORCID),
  Lizenz Apache-2.0 mit dem Satz, dass sie nur Code und eigene Texte deckt. Bei Zenodo hat `.zenodo.json` Vorrang
  vor `CITATION.cff` (aus Wissen, nicht geprüft). Der Unterschied dataset/software ist gewollt: Daten und
  Schnappschuss bekommen eigene Einträge vom Typ dataset. Vorschlag an die Belegschicht: `CITATION.cff` auf
  `software` umstellen, falls das Repository allein zitiert werden soll.
- Software Heritage: Hinweis in README und `docs/przekazanie.md` (archiviert öffentliche Repositorys; SWHID nach der
  Archivierung in `CITATION.cff` unter `identifiers`).

## Funde für andere Eigentümer (gemeldet, nicht geändert)

| Fund | Datei | Eigentümer | Vorschlag |
|---|---|---|---|
| bricht ohne die BIP-Seite ab, obwohl sie nur Gegenprobe ist | `skripte/35_klimat.py` | Klima | Gegenprobe überspringen und im Beleg vermerken |
| liest `npm-…-latest.json`; „latest“ wandert mit neuen Fassungen | `skripte/schriften.py` | Schrift und Grundkarte | versionsgenaue Adresse `…/5.3.0` |
| `package.json` trägt Name und Beschreibung des Kiezatlas Potsdam; `node_modules` ist eine Verknüpfung in das Potsdamer Repo | `package.json` | Integration | eigener Name und Beschreibung; `npm ci` funktioniert mit `package-lock.json` |
| Name der UG fest im Zitiersatz der Downloads statt aus `herausgeber` | `skripte/16_export_krakow.py` | Methode, Daten, Downloads | aus `config/krakow.yaml` lesen |
| Kartenschrift auf die SHA256 eines Arch-Pakets festgeschrieben; andere Systeme brechen ab | `skripte/27_grundkarte.py` | Schrift und Grundkarte | Schnappschuss liefert die Dateien (umgesetzt über `--schrift-ordner`); dokumentiert |
| Prüfsummenlisten nennen auch Belegdateien, die nicht weitergegeben werden dürfen | `belege/rohdaten*.sha256`, `pruefen.sh` | Belegschicht | Daten und Belege in getrennten Listen oder `--ignore-missing` mit Ausschlussliste |
| GSAP liegt unter `vendor/`, keine Krakauer Seite lädt es (nur Potsdamer `atlas.js` für die Gegenprobe); Lizenz nicht frei | `vendor/gsap.min.js`, `vendor/ScrollTrigger.min.js` | Integration | für den öffentlichen Export entscheiden: behalten (Gegenprobe) oder entfernen; offen für Andre |
| Geodaten-Import-Pipeline nötig für `lauf.sh einrichten`; ob ihr Repository öffentlich ist, ist nicht geprüft (GitHub gesperrt) | `skripte/lauf.sh` | Infrastruktur | vor der Übergabe klären |
| Die Kette schreibt die 3D-Dateien in einen neuen Ordner `abgeleitet/gebaeude/<heute>-odbl/`; Entwicklungsserver und Deploy-Kopie liefern nach KR42 fest `2026-11-13-odbl/` aus, ein neuer Lauf käme also nicht an | `skripte/entwicklung_server.mjs`, `skripte/deploy_kopie.py` | Schrift und Grundkarte, Deploy | jüngsten `*-odbl`-Ordner mit `MANIFEST.sha256` nehmen oder Ordner als Schalter |
| „auf der Workstation“ in zwei Kopfkommentaren (kein Rechnername, nur Arbeitsvermerk) | `skripte/osm_pbf.py`, `skripte/versorgung_werkzeug.py` | OSM, Versorgung | neutral formulieren |
| Pfade, Rechnername, Bildlizenz, Arbeitsvermerke | siehe Prüfung vor Veröffentlichung | | |

## Nie sprawdzono / Nicht geprüft sind …

- die vollständige Kette `./atlas.sh alles` über alle 24 Schritte (Grund oben);
- die Zeiten der Datenbank-Schritte `osm`, `db_gliederung`, `einrichtungen`, `ziele_db`, `fussweg_export`;
- `.zenodo.json` gegen das Schema von Zenodo (nur Schlüssel und Typen von Hand gegen die bekannte Liste);
- die CI auf GitHub und die Existenz der genannten Action-Tags;
- ob die versionsgenaue Registry-Adresse der Fontsource-Pakete dieselben Angaben liefert wie die abgelegten
  `latest`-Dateien;
- die polnischen Anleitungen durch eine Muttersprachlerin oder einen Muttersprachler (Begriffe nach
  `docs/glossar-pl.md`, Status dort: Vorschlag);
- die Aktualisierungsrhythmen der Quellen, soweit `docs/przekazanie.md` sie nicht aus Dateien belegt.

## Neu prüfen, wenn

eine Quelle einen neuen Stand hat (Schnappschuss neu bauen, Regeln prüfen), ein Skript neue Eingänge liest (Liste in
`skripte/kette.py` und Regeln in `skripte/schnappschuss.py`), die Belegschicht `pruefen.sh --ohne-rohdaten` einführt
(CI vereinfachen) oder Andre die Veröffentlichung freigibt (Export nach dem Vorschlag oben, `./atlas.sh oeffentlich
--veroeffentlichung` muss grün sein).

## Prüfstand des Pakets

`./pruefen.sh` mit Browser auf dem Stand `f094dba` dieses Zweigs (nach allen Dateien des Pakets außer den späteren
Korrekturen an `skripte/kette.py`, `skripte/schnappschuss.py` und Dokumentation): 55 Prüfungen, 48 grün, 0 mit
Befund, 7 übersprungen (Gründe wie im Prüfstand `5f5bf50`; `--voll` und `--gegenprobe` nicht gelaufen). Danach
`./pruefen.sh --ohne-browser` auf dem Endstand (siehe Abschlussmeldung des Pakets).
