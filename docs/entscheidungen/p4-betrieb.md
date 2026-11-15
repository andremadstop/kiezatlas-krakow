# Behebung Phase Nacharbeit, Bereich „betrieb“ (14.11.2026)

Stand 14.11.2026, Zweig `Arbeitszweig p4-betrieb` (von `main` `327505f`). Jeder Fund ist zuerst nachgeprüft worden; echte
Funde sind je Fund oder Gruppe in einem eigenen Commit behoben. Dieses Dokument schlägt keine neue KR-Nummer vor;
Nummern und Status in `docs/entscheidungen.md` setzt die Integration.

## 1. Funde und Ergebnis

| Nr | Fund (Quelle, Schwere) | Nachprüfung | Ergebnis |
|---|---|---|---|
| 1 | `02a_stadtteile_uebersicht.py` fehlt in der Kette (betreiber, blockierend) | bestätigt: kein Schritt in `skripte/kette.py`; Protokoll des Funds `…/20261114T205059Z.log` zeigt „FEHLT daten/stadtteile_uebersicht_odbl.js“ | behoben `fdb5f15`: Schritt `uebersicht` direkt nach `bevoelkerung`; `./atlas.sh liste` zeigt 25 Schritte, Anleitungen angepasst; Lauf auf dem eigenen Rechner byte-gleich |
| 2 | Kartenschrift an das Arch-Paket gebunden (betreiber, blockierend) | bestätigt: Pfad `/usr/share/fonts/noto` fest in `27_grundkarte.py`, `kette.py`, `schnappschuss.py` | behoben `effda52`: die drei TTF byte-gleich (SHA256 wie `SCHRIFTEN`) unter `schriften/noto/` mit `OFL.txt` (Copyright-Zeile aus der Schrift); Standard von `27_grundkarte.py`, `kette.py` und Quelle des Schnappschusses. Nicht in der Auslieferung (`deploy_kopie.py` nimmt `schriften/` nicht). `oeffentlich_pruefen.py` hat eine Lizenzregel, NOTICE und QUELLEN.md nennen die Dateien. Nachweis: `27_grundkarte.py --pruefen` byte-gleich (396 Dateien), `./atlas.sh trocken --ohne-datenbank` grün, `./atlas.sh oeffentlich` grün |
| 3 | Reproduzierbarkeit nur auf unserem Rechner belegt (betreiber, wichtig) | bestätigt aus dem Klon des Funds: `git diff` zeigt Prądnik Czerwony 643,6 → 643,7 ha in `belege/dk_klimat.md`, Koordinaten in der 5. Nachkommastelle | **teilweise behoben** `5de7a20`: Aussage in beiden Anleitungen auf den Rechner der Herausgeberin eingeschränkt, Abweichung mit Beispiel beschrieben, Hinweis im „Erwarteten Ende“. **Offen:** Referenz-Image (Dockerfile mit festgeschriebener Basis), in dem die Reproduzierbarkeit belegt ist; Ursache nicht eingegrenzt (Vermutung: andere Mathematikbibliothek des Systems). Die Rundung der Koordinaten bleibt unverändert: Doppelrundung verschiebt nur die Kippstelle und hätte alle Grenzdateien, Belege und Downloads auf dem eigenen Rechner umgewälzt |
| 4 | `playwright install` ohne Systembibliotheken (betreiber, wichtig) | bestätigt aus dem Protokoll (`libglib-2.0.so.0`) | behoben `5de7a20`: `npx playwright install --with-deps chromium` (braucht root), Fehlerzeile in Abschnitt 7 beider Anleitungen |
| 5 | `KIEZ_DATEN` in den Anleitungen nie gesetzt (betreiber, wichtig) | bestätigt (`grep` ohne Treffer) | behoben `5de7a20`: `export KIEZ_DATEN=…; mkdir -p` in Abschnitt 2, Satz „alle folgenden Befehle setzen das voraus“ |
| 6 | Drei Adressen fehlen (betreiber, wichtig) | bestätigt | **teilweise behoben** `5de7a20`: Kasten oben in beiden Anleitungen („ohne Rückfrage heute nicht vollständig betreibbar“, Rückfrage über `meldeweg`), Übergabehürde in `przekazanie.md` um Repository und Schnappschuss erweitert. **Offen, Entscheidung beim Herausgeber:** Repository (bereinigter Export) und Pipeline im festgeschriebenen Commit veröffentlichen, Schnappschuss als Zenodo-Datensatz mit DOI; nichts davon war in diesem Auftrag erlaubt |
| 7 | EEA-Hinweis im Trockenlauf falsch (betreiber, wichtig) | bestätigt: Wahl-Muster `eingang/eea/*.csv`, im Eingang liegt `*.geojson.zip` | behoben `aae21d8`: Wahl-Muster mit Alternativen (`a \| b`), Tabellenzeile in beiden Anleitungen; Trockenlauf ohne EEA-Hinweis, mit leerem Rohdatenordner weiter mit Hinweis |
| 8 | Methodenseite verspricht Selbstprüfung ohne Repository-Adresse (jury, wichtig) | bestätigt (`metoda.html` ohne Link; `dane.html` ebenso) | behoben `a684462`: in allen drei Sprachen „Repository noch nicht öffentlich, bis dahin Code und Belege auf Anfrage“ mit Meldeadresse; `CITATION.cff` ebenso; der Verweis auf `docs/entscheidungen.md` sagt, dass sie deutsch ist. **Offen:** mehrsprachige öffentliche Entscheidungsliste (eigene Übersetzungsaufgabe, 56 Einträge) und der echte Link nach der Veröffentlichung |
| 9 | Layoutsprünge beim Laden (jury, wichtig) | bestätigt mit den Skripten der Jury (eigene Kopie, eigener Port): Werte wie im Fund. Ursachen: Behälter, die das Seitenskript nach dem ersten Zeichnen füllt (Themenseiten, Stadtzahlen der Startseite); auf metoda der Umbruch der h1 (zwei Zeilen in der Ersatzschrift, eine in Barlow Semi Condensed), nicht nur die Kopfnavigation | behoben `d7f51c6`, `9ec7198`: `min-height` für die leeren Behälter bis etwa zum Ende des ersten Bildschirms (gemessene Endhöhe, gilt nur solange leer); schmale Systemschriften als Ersatz in `--f-display`, damit die h1 vor dem Laden von Barlow nicht zweizeilig umbricht. Ein erster Versuch mit `font-display:optional` und Vorladen ist zurückgenommen (Abschnitt 2). Messung in Abschnitt 2 |
| 10 | og:image und twitter:card fehlen (jury, klein) | bestätigt (kein `og.png`) | **verworfen für jetzt:** `skripte/28_vorschaubild.mjs` setzt die Potsdamer Lage voraus (3D-Dateien unter `daten/gebaeude/` im Repo) und bricht mit „keine Gebäude unter daten/gebaeude/“ ab; die Anpassung an Gebäude außerhalb des Repos über den Entwicklungsserver ist eine eigene Aufgabe. Ein Vorschaubild nützt erst mit der Veröffentlichung (absolute Adresse aus `basis_url`) |
| 11 | Deutscher Tausendertrenner in `uruchomienie.md` (polnisch-fach, klein) | bestätigt (Zeilen 53, 54, 161, §6, §8) | behoben `5de7a20`: „403 179 520 B“, „950 576 003 B“, „1039 s (ok. 17 min)“; §8 verweist auf §6 |
| 12 | Plankennungen in `uruchomienie.md` (polnisch-fach, klein) | bestätigt | behoben `5de7a20` (zusammen mit Nr. 17) |
| 13 | Potsdamer Restschlüssel in `texte/pl` (polnisch-fach, klein) | bestätigt; die Gegenprobe Potsdam läuft nur deutsch, die Schlüssel stehen in pl für gleiche Schlüssel in allen Sprachen | behoben `c82097e`: Kopfkommentar in `texte/pl/planer.js` und `karte.js` nennt die Schlüssel; „Gimnazjum (Gymnasium)“ → „Gymnasium (niemieckie liceum ogólnokształcące)“ mit neuer pl-Falschsatz-Regel `gimnazj`; Zensus-Regel fängt „15 maja 2022 / 15.05.2022“, `karte.stichtag_zensus` als begründeter Fundort. Auslagern in eine eigene Datei verworfen: `pruefen/texte.py` verlangt dieselben Dateien und Schlüssel in allen Sprachen |
| 14 | „In short“ beginnt mit der Vollvariante (betreiber, klein) | bestätigt | behoben `5de7a20`: zuerst `--ohne-datenbank`, danach die Vollvariante mit Hinweis auf Abschnitt 3 |
| 15 | Installationsweg für uv und Node fehlt (betreiber, klein) | bestätigt (`pruefen.yml`: `pipx install uv==0.11.3`, `UV_PYTHON_PREFERENCE: only-managed`) | behoben `5de7a20`: `pipx install uv==0.11.3`, `UV_PYTHON_PREFERENCE=only-managed`, `uv python install 3.13.12`, Node 22 mit Prüfbefehl; Hinweis auf Python- und Poppler-Version in den Belegen. Keine Installer-Adresse von uv eingetragen (nicht nachgeschlagen) |
| 16 | `.env.beispiel` und `docker-compose.yml` sprechen von Haupt-Checkout und Worktree (betreiber, klein) | bestätigt | behoben `3d355fc`: „Wurzelordner dieses Repositorys“; Worktree- und Potsdam-Hinweise in `docs/rundgang.md`, „Datenbank und mehrere Arbeitskopien“; Halt-Meldung in `kette.py` ebenso |
| 17 | `(KR25)`, `(STOP licencyjny, KR3)` in beiden Anleitungen (betreiber, klein) | bestätigt (vier Fundstellen) | behoben `5de7a20`: Kennung gestrichen bzw. „licencja nie pozwala na dalsze udostępnianie“ / „no licence for redistribution“; `przekazanie.md` `(KR31)` ebenso. `KR34` und `KR1 i dalej` in `przekazanie.md` bleiben, weil sie ausdrücklich in `docs/entscheidungen.md` verweisen |
| 18 | Zeittabelle ohne `./pruefen.sh` und `./atlas.sh alles` (betreiber, klein) | Kettenlauf aus dem Protokoll des Funds nachgerechnet: Summe der Schrittzeiten bis `pruefen` 1123 s; die 913 s für `./pruefen.sh` stehen in einem Protokoll im Container, das hier nicht vorliegt | behoben `5de7a20` und `1400521`: Zeile „`./atlas.sh alles --ohne-datenbank` bis `pruefen`“ mit 1123 s (Debian-Container); `./pruefen.sh` mit Browser auf dem eigenen Rechner gemessen (939 s, 15.11.2026) statt der nicht nachprüfbaren 913 s |

## 2. Messung der Layoutsprünge

Skripte: `/tmp/kz_betrieb/cls.mjs` (Kopie von `/tmp/kz_jury/cls.mjs` und `cls2.mjs`, eigener Port mit
`skripte/entwicklung_server.mjs`), Summe aller `layout-shift`-Einträge ohne Eingabe; Desktop 1440 × 900, Handy
390 × 844 mit vierfacher CPU-Drosselung, 150 ms Latenz, 200 kB/s.

| Seite | Ansicht | vorher | nachher |
|---|---|---|---|
| mieszkania | Desktop | 0,517 | 0,000 |
| powietrze | Desktop | 0,356 | 0,000 |
| klimat | Desktop | 0,067 | 0,000 |
| index | Desktop | 0,107 | 0,007 |
| metoda | Desktop | 0,018 | 0,013 |
| index | Handy, gedrosselt | 0,211 | 0,017 |
| metoda | Handy, gedrosselt | 0,323 | 0,110 |
| klimat | Handy, gedrosselt | 0,217 | 0,077 |
| mieszkania | Handy, gedrosselt | 0,060 | 0,060 |
| powietrze | Handy, gedrosselt | 0,033 | 0,033 |
| dane | Handy, gedrosselt | 0,036 | 0,036 |

Rest auf dem Handy: das Umbrechen von Fließtext und Kopfnavigation, wenn Barlow die Ersatzschrift ablöst (metoda
0,093 aus einer Liste, je Seite rund 0,017 aus der Kopfnavigation). metoda liegt mit 0,110 knapp über 0,1.

Verworfene Wege, mit Grund:
- `font-display:optional` mit `<link rel="preload" … crossorigin>` (Zwischenstand `d7f51c6`, CLS überall nahe 0):
  das Vorladen scheitert unter `file://` an CORS (`pruefen/seiten.mjs`: Konsolenfehler auf allen Seiten), und ohne
  rechtzeitige Schrift bleibt die Ersatzschrift stehen; die Beschriftungen der Liniengrafiken auf powietrze und
  mieszkania überlappen dann (`pruefen/S3_themenseiten.mjs` unter `file://`). Zurückgenommen in `9ec7198`.
- Ersatzschriften mit `size-adjust` (Arial/Liberation Sans auf Barlow-Breite, 96,4 % und 90,9 %; Narrow 93,1 %):
  metoda auf dem Handy stieg wieder auf 0,335. Nicht übernommen.
- `Arial`/`Liberation Sans` vor `system-ui` im Fließtext: metoda 0,002, aber mieszkania 0,060 → 0,152. Nicht übernommen.

Nachgefüllte Behälter auf anderen Seiten (Desktop ohne Drosselung, Zwischenstand): dzielnica 0,082, modernizacja
0,051, planer 0,041; unter 0,1 und nicht Teil des Funds, nicht geändert.

## 3. Eigentum

Geändert im Auftrag der Behebung: `skripte/kette.py`, `skripte/27_grundkarte.py`, `skripte/schnappschuss.py`,
`skripte/oeffentlich_pruefen.py`, `schriften/noto/` (neu), `NOTICE`, `QUELLEN.md`, `.env.beispiel`,
`docker-compose.yml` (nur Kopfkommentar), `docs/rundgang.md` (neuer Abschnitt), `docs/running.md`,
`docs/uruchomienie.md`, `docs/przekazanie.md`, `texte/pl/planer.js`, `texte/pl/karte.js`,
`pruefen/d3_falschsaetze.json`, `texte/<lang>/bloecke/quelle/metoda.html` und `dane.html` (daraus erzeugt die Blöcke
und Seiten), `atlas.css`, `themenseite.css`, `stadtatlas.css`, `vorlagen/_rahmen.html` (daraus alle Seiten).

## 4. Prüfung

`./pruefen.sh` mit Browser im Worktree auf Stand `1400521`, 15.11.2026: Rückgabe 0, 939 s,
„Zählung: 60 Prüfungen, 53 grün, 0 mit Befund, 7 übersprungen“. Übersprungen: Vertrag Bauzeiten-Methode,
`planungsraeume.js`, GIS-Export ohne Datenbank, Codepfade Planer/Export, Landesfilter (alle für Kraków entfallen),
die Neuberechnung aus den Rohdaten (nur mit `--voll`) und die Gegenprobe Potsdam (nur mit `--gegenprobe`). Die Zählung
64/59/0/5 von `main` stammt aus `./pruefen.sh --voll --gegenprobe` (`belege/pruefstand-20261114-ede93e5/pruefen.log`); `--voll` und `--gegenprobe` sind in diesem Auftrag
nicht erneut gelaufen. Protokoll: `/tmp/kz_betrieb/lauf3/pruefen.log`.

## 5. Offen für die Integration

- Referenz-Image mit festgeschriebener Basis, darin die Reproduzierbarkeit belegen (Nr. 3).
- Öffentliches Repository, Pipeline im festgeschriebenen Commit, Schnappschuss mit DOI; danach echte Links auf
  metoda/dane und in beiden Anleitungen (Nr. 6, Nr. 8).
- Mehrsprachige öffentliche Entscheidungsliste (Nr. 8).
- Vorschaubild og:image/twitter:card nach Anpassung von `skripte/28_vorschaubild.mjs` (Nr. 10).
- metoda auf dem Handy CLS 0,110, knapp über 0,1 (Nr. 9, Abschnitt 2).

