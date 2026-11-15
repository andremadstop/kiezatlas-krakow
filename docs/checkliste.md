# Belegstandard: Checkliste

Der Kiezatlas Kraków soll denselben Belegstandard erfüllen wie der Kiezatlas Potsdam. Diese Liste führt die 36 Punkte
des Standards, die zehn Lehren aus dem Potsdamer Audit vom 06.11.2026 und die Zusatzauflagen aus der Kritik am
Potsdamer Bauplan, jeweils mit dem Stand und dem Beleg, der ihn trägt. Die Liste selbst ist ein Arbeitsstand und
kein Prüfergebnis: Belastbar ist nur, was der Beleg zeigt.

Stand: 15.11.2026, nach der Behebung der Sichtung: echte Daten in allen Themen außer Pünktlichkeit (seit den Handdownloads vom 14.11.2026; Denkmalregister nur aus Wikidata). Der jüngste Prüfstand
steht in `belege/README.md`.

**Status:**

- **erfüllt**: Der Beleg würde fehlschlagen oder fehlen, wenn die Aussage falsch wäre (eine Prüfung in `pruefen.sh`
  oder eine vorhandene Datei mit Abschnitt).
- **teilweise**: Der Rahmen steht, Inhalt oder Prüfung fehlen noch. Was fehlt, steht in der Zeile.
- **offen (Paket …)**: Das genannte Paket liefert es; bis dahin gibt es nichts zu belegen.
- **entfällt (KRn)**: Für Kraków entschieden, mit Begründung in `docs/entscheidungen.md`.

`pruefen/belege.py` prüft, dass jede Zeile einen Status und einen Beleg hat und dass die genannten Dateien existieren.

## Einstieg und Nachvollziehbarkeit

| Nr | Punkt | Status | Beleg |
|---|---|---|---|
| 1 | README-Kasten „Do weryfikacji / Zur Prüfung“ mit Datum und Commit, je Kernzahl Angabe, Beleg, Skript | erfüllt: Kasten mit Datum, Prüfstand-Commit und sechs Kernzahlen mit Beleg und Skript (Stand 14.11.2026, `d18c434`) | `README.md` Abschnitt „Do weryfikacji / Zur Prüfung“; `pruefen/belege.py` (Prüfstand im Kasten vorhanden) |
| 2 | Satz „Dotąd niepotwierdzone / Nicht belegt sind bisher“ mit Verweis | erfüllt | `README.md` Abschnitt „Do weryfikacji / Zur Prüfung“ |
| 3 | Meldeweg in README, Seitenfuß und CITATION | erfüllt | `config/krakow.yaml` (`meldeweg`), `vorlagen/_rahmen.html` (Seitenfuß), `CITATION.cff` (`contact`), `README.md`; Gleichheit prüft `pruefen/belege.py` |
| 4 | `docs/rundgang.md` mit Schritttabelle Nr, Skript, liest, schreibt, Prüfung; Fehlendes als „nicht angegeben“ | erfüllt (für das Gerüst; die Datenpakete füllen ihre Zeilen) | `docs/rundgang.md` Abschnitt „Schritte“ |
| 5 | `belege/README.md` je Datei „belegt“ und „erzeugt von“, Fehlendes ausdrücklich | erfüllt | `belege/README.md`; `pruefen/belege.py`: jede in der Tabelle genannte Datei existiert, jedes Prüfprotokoll unter `belege/` steht in der Tabelle, übrige Dateien (Lieferungen der Pakete) erscheinen als Hinweis zum Einsammeln |

## Reproduzierbarkeit

| Nr | Punkt | Status | Beleg |
|---|---|---|---|
| 6 | `requirements.txt` mit Hashes, Werkzeugversionen im Rundgang, Neuerzeugung byte-gleich | teilweise: Hashes, Versionen und byte-gleiche Neuerzeugung von Seiten, `ort.js` und Beispieldaten stehen; Stand der Geodaten-Import-Pipeline erst mit dem ersten Lauf | `requirements.txt`, `requirements-pruefen.txt`, `docs/rundgang.md` Abschnitt „Was man braucht“, `skripte/30_seiten.py --pruefen`, `skripte/31_ort.py --pruefen`, `pruefen/fixtures_krakow.py --pruefen` |
| 7 | Rohdaten unter `$KIEZ_DATEN` mit `HERKUNFT.md` je Ordner, beim Abruf gehasht in `belege/rohdaten*.sha256` | teilweise: Rohdaten der Pakete unter `$KIEZ_DATEN` mit `HERKUNFT.md`, Prüfsummen in neun Listen `belege/rohdaten*.sha256`, in `pruefen.sh` geprüft; Handdownloads für Luft, Wohnungsmarkt, Denkmalregister, LoD1, rejony und RSPO fehlen | `pruefen.sh` (Prüfsummen-Schritt, derzeit „übersprungen“ mit Grund) |
| 8 | Bezugs-Snapshots auch außerhalb der Datenbank | offen (Paket Gebäude und Kamienice) | `docs/rundgang.md` Abschnitt „Neuer Datenstand“ |
| 9 | Stand der Fremd-Pipeline (`git describe --dirty`) in jedem Laufbericht | offen (Paket Infrastruktur, `skripte/lauf.sh`) | `docs/rundgang.md` Abschnitt „Was man braucht“ (Zeile Geodaten-Import-Pipeline: „nicht angegeben“) |
| 10 | Abschnitt „Neuer Datenstand“: neue Fassung unter `<quelle>/<stand>/`, alte Hashes bleiben | erfüllt | `docs/rundgang.md` Abschnitt „Neuer Datenstand“ |

## Prüfkette

| Nr | Punkt | Status | Beleg |
|---|---|---|---|
| 11 | `pruefen.sh` ohne Netz und DB, alle Prüfungen laufen, Zählung, Übersprungenes mit Grund, Kopf mit Commit und Werkzeugversionen | erfüllt | `pruefen.sh`; Kopf und Zählung im jüngsten Prüfstand unter `belege/` |
| 12 | JSON-Schema je veröffentlichter Datei, Datei ohne Schema = Befund, Fixtures gegen dasselbe Schema | erfüllt | `pruefen/daten.py` (Punkte 2 und 3 im Kopf), `daten/schema/` |
| 13 | Summenprüfung Zelle → dzielnica → Stadt gegen `kennzahlen.json` | teilweise: läuft auf Beispieldaten; mit echten Daten im Paket Gliederung und Bevölkerung | `pruefen/daten.py` (Punkt 1 im Kopf) |
| 14 | Generatoren mit `--pruefen`, auch Seitengenerator und `ort.js` | teilweise: Seitengenerator, `ort.js` und Beispieldaten haben es; die Datenskripte bekommen es in ihren Paketen | `skripte/30_seiten.py`, `skripte/31_ort.py`, `pruefen/fixtures_krakow.py` |
| 15 | Browserprüfungen (file:// und HTTP, Konsole, axe, Falschsätze, mehrere Breiten) in allen drei Sprachen | teilweise: file:// und HTTP, Konsole, axe, 1280 und 360 px in pl, en, de laufen für alle 18 Seiten, dazu die Browserprüfungen der Seitenpakete mit 390 px; Falschsatz-Listen gelten noch nicht für alle Seiten (`pruefen/S4_falschsaetze.json` nur auf den Langtexten, KR44); Bildschirmfotos nur auf Polnisch | `pruefen/seiten.mjs`, `pruefen/S1_seiten.mjs`, `pruefen/S2_seiten.mjs`, `pruefen/S3_themenseiten.mjs`, `belege/bildschirm-20261115/README.md`; hreflang zusätzlich ohne Browser in `pruefen/hreflang.py` |
| 16 | Prüfprotokoll je veröffentlichtem Stand unter `belege/pruefstand-<datum>-<commit>/pruefen.log`, grün | teilweise: grüner Prüfstand nach der Nachprüfung der echten Daten `belege/pruefstand-20261114-d18c434/pruefen.log` (mit Gegenprobe, ohne Beispieldaten); ein veröffentlichter Stand fehlt noch (Paket Auslieferung) | `belege/README.md` (Zeilen `pruefstand-…`) |
| 17 | DB-Abnahmen je Paket als eigene Skripte; Rundgang nennt, was nicht in der Kette läuft | teilweise: Der Rundgang nennt es; Skripte kommen mit den Datenpaketen | `docs/rundgang.md` Abschnitt „Prüfungen“ |

## Methodische Strenge

| Nr | Punkt | Status | Beleg |
|---|---|---|---|
| 18 | Validierungsregeln vor dem Lauf als eigener öffentlicher Commit (`pruefen/<paket>_protokoll.md`) | teilweise: Protokolle vor dem Lauf für die Datenpakete und das Paket Methode, Daten, Downloads; die Seitenpakete Erzählung/Karte, Planer/Kamienice/Sanierungsatlas und Themenseiten haben keins vor ihrem ersten Lauf abgelegt | `belege/README.md` Abschnitt „Prüfprotokolle vor dem Lauf“, `pruefen/S4_protokoll.md` |
| 19 | Quoten mit Wilson-95-%-Intervall und n, keine Nachkommastelle bei kleinem n | offen (Paket Versorgung und Takt, Themenpakete) | `docs/rundgang.md` Abschnitt „Bau“ |
| 20 | Abzeichen „standard urzędowy“ nur bei amtlicher Rechenweise, sonst „orientacyjnie“ | offen (Paket Versorgung und Takt, `config/richtwerte.yaml` mit Fundstellen) | `config/richtwerte.yaml` (noch Potsdamer Stand) |
| 21 | Gegenproben gegen unabhängige amtliche Werte in `belege/gegenproben.md` | offen (Paket Gliederung und Bevölkerung: GUS-Gemeindeergebnis) | `belege/README.md` Abschnitt „Erwartet“ |
| 22 | Offenlegen, was KI erhoben oder geprüft hat und wer entschieden hat | teilweise: für Entscheidungen und Code offengelegt; je Datenlauf in den Laufberichten der Pakete | `docs/entscheidungen.md` (Einleitung), `CITATION.cff` (`notes`) |
| 23 | Keine handgetippte Zahl auf Seite, Methodentext oder Film, auch nicht in Übersetzungen | teilweise: Seiten, Langtexte und Downloads holen Zahlen aus `daten/` (KR38); `pruefen/S4_bloecke.py` und `skripte/16_bloecke_krakow.py --pruefen` prüfen die Langtexte gegen die Daten; eine allgemeine Prüfung auf Ziffern in `texte/` fehlt | `pruefen/texte.py` (gleiche Platzhalter in allen Sprachen), `pruefen/S4_bloecke.py`, `docs/entscheidungen.md` KR38 |

## Entscheidungen und Grenzen

| Nr | Punkt | Status | Beleg |
|---|---|---|---|
| 24 | `docs/entscheidungen.md` mit Präfix KR, je Eintrag Anlass, Entscheidung, Begründung, Verworfen, Neu prüfen wenn | erfüllt | `docs/entscheidungen.md`; `pruefen/belege.py`: Übersicht und Abschnitte stimmen überein, jeder Eintrag hat alle fünf Punkte (fehlende Angaben als „nicht angegeben“) |
| 25 | Liste „Nie sprawdzono / Nicht geprüft sind“ | erfüllt | `docs/entscheidungen.md` Abschnitt „Nie sprawdzono / Nicht geprüft sind …“ |
| 26 | Kürzeltabelle; interne Dokumente ausschreiben statt zitieren | erfüllt | `docs/entscheidungen.md` Abschnitt „Kürzel“ |

## Lizenz, Quellen, Datenschutz

| Nr | Punkt | Status | Beleg |
|---|---|---|---|
| 27 | `QUELLEN.md` mit Quelle, Nutzer, URL, Lizenz, Vermerk im Original-Polnisch, Weg, Stand; Tabelle „Ausgaben und ihre Lizenz“ | teilweise: Quellen aller Pakete mit Vermerk im Original, Weg und Stand, Ausgaben-Tabelle und gesperrte Wege stehen; Lizenzen von NID-Register, gminna ewidencja und RSPO nicht geprüft | `QUELLEN.md` |
| 28 | Abrufregeln je Host, verbotene Hosts, ein Abrufwerkzeug mit Protokoll, über 50 MB nur mit Freigabe | teilweise: Regeln und die Befunde der Machbarkeitsprobe zu gesperrten Wegen stehen; Hostliste mit robots-Befund liefert das Paket Infrastruktur | `QUELLEN.md` Abschnitte „Abrufregeln“ und „Gesperrte und nur interne Wege“, `skripte/abruf.py` (noch Potsdamer Stand) |
| 29 | ODbL nur in `*_odbl`-Dateien (technisch), CC BY-SA nur als Prüfspalte, unklare Lizenz nur intern (auch Hashes) | teilweise: ODbL-Grenze technisch geprüft; MSIP-Grenzen bleiben intern (KR3) | `pruefen/daten.py` (Punkt 4 im Kopf), `docs/entscheidungen.md` KR3 |
| 30 | Datenschutzgrenze im Schema und in der Offline-Prüfung: keine Adressen, keine Gebäudekennung, kein Einzeljahr bei Wohnraum | teilweise: Adress- und Kennungsfelder werden geprüft; Einzelkäufe im Wohnungsmarkt und Gebäudeebene kommen mit ihren Paketen | `pruefen/daten.py` (Punkt 5 im Kopf) |
| 31 | `LICENSE` (Apache-2.0), `NOTICE` mit GSAP-Vermerk, `daten/LIZENZ.md`, Grafiken CC BY 4.0 | erfüllt | `LICENSE`, `NOTICE`, `daten/LIZENZ.md`, `QUELLEN.md` Abschnitt „Ausgaben und ihre Lizenz“ |
| 32 | `CITATION.cff` (`type: dataset`), `CHANGELOG.md` mit Tag je Stand, Stand im Seitenfuß | teilweise: alles angelegt; Tags gibt es erst mit dem ersten veröffentlichten Stand (Paket Auslieferung) | `CITATION.cff`, `CHANGELOG.md`, `vorlagen/_rahmen.html` (`data-kiez-version`) |

## Nutzen je Gruppe

| Nr | Punkt | Status | Beleg |
|---|---|---|---|
| 33 | GIS-Export (GPKG, `.qgz`, Lizenz je Ebene) und Office-CSV in polnischer Norm | erfüllt: zwei GeoPackages (ohne ODbL und `_odbl`), QGIS-Projekt, Lizenz je Ebene, CSV mit Punkt und mit Dezimalkomma, Feldbedeutung pl/en/de (KR44) | `pruefen/S4_export.py`, `skripte/16_export_krakow.py` (`--pruefen` in `pruefen.sh`), `belege/S4_downloads.md` |
| 34 | Zähler und Nenner zu jeder Quote, Stadtwert, Vergleich aller Räume | offen (Datenpakete und Seitenpakete) | `docs/rundgang.md` Abschnitt „Bau“ |
| 35 | Antwortsätze mit Stichtag und Grenzen (NSP-Stichtag, Abweichung zum Melderegister, Rundung) | offen (Paket Gliederung und Bevölkerung, Seitenpakete); der NSP-Stichtag ist noch nicht aus der Quelle bestätigt | `docs/entscheidungen.md` Abschnitt „Nie sprawdzono / Nicht geprüft sind …“ |
| 36 | Audit mit Perspektiven, Gegenprüfer am Code, Fundtabelle mit Status, Rohfassung als JSON | offen (Paket Audit, nach allen Seitenpaketen) | `docs/rundgang.md` Abschnitt „Bau“ |

## Lehren aus dem Potsdamer Audit

| Nr | Lehre | Status | Beleg |
|---|---|---|---|
| L1 | Dokumentationsschicht ab Tag 1 | erfüllt | `README.md`, `docs/rundgang.md`, `docs/entscheidungen.md`, `belege/README.md`, angelegt mit dem Gerüst |
| L2 | Texte widersprechen dem Code nicht: Herkunftsfeld je Objekt, Falschsatz-Prüfungen je Sprache, Zahlen nie im HTML | teilweise: Zahlen kommen aus `daten/`, Texte haben je Sprache dieselben Platzhalter; Falschsatz-Listen und Herkunftsfeld fehlen (Paket Oberflächen-Texte, Datenpakete) | `pruefen/texte.py` |
| L3 | Datenschutzgrenze in Vertrag und Prüfung | teilweise (wie Punkt 30) | `pruefen/daten.py`, `daten/schema/` |
| L4 | Abzeichen versprechen nicht mehr als die Rechnung; `null` mit Grund statt falscher Null | offen (Paket Versorgung und Takt) | `docs/rundgang.md` Abschnitt „Bau“ |
| L5 | Beim Abruf hashen, Snapshots außerhalb der DB | offen (wie Punkte 7 und 8) | `pruefen.sh` (Prüfsummen-Schritt) |
| L6 | Umgebung und Fremd-Pipeline festschreiben | teilweise (wie Punkte 6 und 9) | `requirements.txt`, `docs/rundgang.md` Abschnitt „Was man braucht“ |
| L7 | Vorab-Festlegungen öffentlich belegbar, frisches Repo ohne Potsdam-Historie, Protokoll-Commits nie squashen | teilweise: frisches Repo ohne Potsdam-Historie; Protokoll-Commits kommen mit den Datenpaketen | `docs/rundgang.md` (Einleitung), `CHANGELOG.md` Abschnitt „Gerüst“ |
| L8 | Office-Export in der Ländernorm | offen (wie Punkt 33) | `pruefen.sh` (Export-Schritt) |
| L9 | Unsicherheit sichtbar | offen (Datenpakete, Seitenpakete) | `docs/rundgang.md` Abschnitt „Bau“ |
| L10 | Nutzerperspektiven: Grau-Erklärung am Handy, Ortsfindung, einheitliche Kopfzeilen, Fragen öffnen die richtige Ansicht | offen (Seitenpakete, Paket Audit) | `pruefen/seiten.mjs` (360 px ohne seitlichen Überstand) |

## Zusatzauflagen

| Nr | Auflage | Status | Beleg |
|---|---|---|---|
| Z1 | Abnahmen nicht tautologisch: eine Prüfung muss scheitern können, wenn die Aussage falsch ist | teilweise: für die Prüfungen der Belegschicht mit einem Gegenversuch belegt (gezielt verfälschte Seite bzw. Liste ergibt Befund); für die Datenpakete in ihren Protokollen | `pruefen/hreflang.py`, `pruefen/belege.py` |
| Z2 | Bauzeiten-Kaskade mit vorab festgelegter Neubau-Referenz und Holdout je Klasse | entfällt (KR4) | `docs/entscheidungen.md` KR4 |
| Z3 | Startseite unter 300 KB gz je Sprache | teilweise: JavaScript der Startseite (pl) 287.089 B gz unter 307.200 B mit den vereinfachten Übersichtsgrenzen (KR39); mit HTML und CSS 314.482 B gz (über der Grenze, ohne Schriften und Kacheln); „alles, was die Seite lädt“ (mit Kacheln und Schriften) misst nur die Deploy-Kopie, zuletzt vor der Vereinfachung | `pruefen/N1_daten.py` in `pruefen.sh`; `belege/N1_stadtteile_uebersicht.md`; `belege/N2_deploy_probe-dd7344e.log`; `docs/entscheidungen.md` KR39 |
| Z4 | Kein Verweis im README-Kasten auf einen Prüfstand, der nicht grün unter `belege/` liegt | erfüllt | `pruefen/belege.py` (Prüfstand im Kasten liegt unter `belege/` und endet mit „0 mit Befund“) |
| Z5 | Zahlen in `belege/README.md` stimmen mit den Dateien (Potsdam: „80 Dateien“ gegen 78 Hashzeilen) | erfüllt | `pruefen/belege.py` (Zählung eines Prüfstands und Zeilen je `rohdaten*.sha256` gegen die Angabe in `belege/README.md`) |
