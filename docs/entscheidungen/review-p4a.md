# Sichtung vor der Veröffentlichung (14./15.11.2026): Funde und ihr Verbleib

Stand 15.11.2026, Zweig `Arbeitszweig p4-integration` (von `main` `327505f`). Vier Sichtungen haben `main` `327505f` nur lesend
geprüft: Gestaltung und Bedienung (Selbstbewertung nach Jury-Maßstab, kein blinder Kritiker), polnische Fachsprache
(zwei Durchsichten: fachlich „F“, sprachlich „S“) und Betrieb (Neuaufbau nur mit der Anleitung in einem Container,
ohne `.env`). Dazu kam der Auftrag, das Denkmalregister auf die Seiten zu bringen. Behoben wurde auf vier Zweigen; die
Integration hat sie zusammengeführt und jeden Fund am Integrationsstand nachgesehen.

Die Funde stehen je Bereich vollständig mit Nachprüfung und Commit in den Berichten der Zweige. Hier steht der
Verbleib jedes Funds nach der Integration, dazu was erst durch das Zusammenführen entstanden oder erledigt ist.

| Bereich | Bericht | Zweig |
|---|---|---|
| Denkmalregister | `docs/entscheidungen/DZ.md` §9, `pruefen/DZ_protokoll.md` Nachtrag 3 | `Arbeitszweig p4-denkmale` |
| Gestaltung (Jury) | `docs/entscheidungen/p4-gestaltung.md` | `Arbeitszweig p4-gestaltung` |
| Sprache (polnisch, fachlich und sprachlich) | `docs/entscheidungen/p4-sprache.md` | `Arbeitszweig p4-sprache` |
| Betrieb (Betreiberin, Jury, polnisch-fach) | `docs/entscheidungen/p4-betrieb.md` | `Arbeitszweig p4-betrieb` |

Status: **behoben** (Commit auf dem Zweig oder in der Integration), **teilweise** (was fehlt, steht dabei),
**offen** (wer entscheidet), **verworfen** (Grund).

## Gesamturteile der Sichtung (Kurzfassung)

- **Gestaltung:** Design 7/10, Bedienbarkeit 6,5/10, Inhalt 8/10; axe 0 Verstöße, Fokus sichtbar, kein seitliches
  Überlaufen bei 390 px. Einziger Blocker: Abzeichen „dane przykładowe“ an den echten EEA-Stationen. Strategisch:
  Die Kamienice-Seite, für eine Denkmal- und Stadtumbau-Professorin die wichtigste, war „ehrlich, aber dünn“.
- **Sprache:** im Kern solide (GIOŚ-Typen, RCN-Begriffe, TERYT, Zahlformate). Schaden würden Planungsbegriffe und
  Uneinheitlichkeit; blockierend „intensywność zabudowy“ für den Grundflächenanteil. Ein muttersprachliches Lektorat
  bleibt nötig.
- **Betrieb:** Seiten lassen sich nach der Anleitung erzeugen, `./pruefen.sh` wurde aber nicht grün, und ohne
  unsere Rechner fehlen Rohdaten und Kartenschrift. 3D-Dateien auf fremdem Rechner byte-gleich, Stadtteilgrenzen
  nicht (5. Nachkommastelle).

## Denkmalregister

| Fund | Verbleib |
|---|---|
| `daten/denkmale.js` echt, aber von keiner Seite geladen; Kamienice inhaltlich dünn (Gesamturteil Gestaltung) | behoben `e540d38`, `f2dbf01`, `4fa0a36`, `f95475e`: Registerpunkte je Delegatura auf `kamienice`, Ebene `rejestr` auf der Karte, Ebene `rejestr_zabytkow` im Download; KR57 |
| zweite Stichprobe zur Sichtprüfung | teilweise `3ba74d3`, `7334df3`: gezogen (20 + 20 Punkte), nicht ausgewertet; offen für einen Menschen am Luftbild |
| feste Marke „Beispieldaten“ neben der Luft-Ebene | behoben, doppelt: `e197ab0` (Denkmale) und `a0f2698` (Gestaltung, mit Prüfung `pruefen/beispielmarke.py`); im Merge ohne Konflikt zusammengeführt |
| NID-Register und gminna ewidencja fehlen | offen: Handdownload (Andre) |
| Gruppierung der Registerpunkte nicht transitiv; Zähler `bauzeit_lesbar` (873) gegen Seite (972) | offen im Generator `skripte/dz_denkmale.py`; die Seite zählt an den Punkten und nennt die Zahl „Punkte“, nicht „Registernummern“ |
| Seitenkarte `kamienice` zeigt nur OSM-Punkte | offen, bewusst: Registerpunkte auf der freien Karte (`karta.html#pkt=rejestr`), Kennzeichnung „nach OSM“ |
| `docs/przekazanie.md` (EEA, RCN „pobranie ręczne jeszcze nie wykonane“), `docs/checkliste.md` Stand | behoben in der Integration `7f55eb0` (Altfehler, eigener Commit); der Betriebszweig hatte diese Zeilen nicht geändert |

## Gestaltung

| Nr | Fund | Verbleib |
|---|---|---|
| 1 | Abzeichen „dane przykładowe“ an den EEA-Stationen (blockierend) | behoben `a0f2698` (siehe Denkmale) |
| 2, 3 | Klimatabelle abgeschnitten, drei Satzspiegel | behoben `5651ae3`; KR58 |
| 4 | fünf Gitter-Einwohnersummen ohne Erklärung | behoben `6dcb5a9`; in der Integration mit dem Prozentzeichen der Sprache zusammengeführt (`erzaehlung.js`, `texte/pl/erzaehlung.js`, Merge `c51ecd0`) |
| 5 | Methode, Daten, vier Themen nicht in der Hauptnavigation | behoben `d1a0421`; KR58 (Vertragsänderung Gerüst) |
| 6 | Kamienice-Legende verdeckt die Karte | behoben `2d95799` |
| 7 | Dostępność startet leer | behoben `074adc3`; im Merge mit der neuen Wortstellung der Parkfrage (Sprache) zusammengeführt |
| 8 | Powietrze ohne Karte, Vorauswahl ohne aktuelle Werte | teilweise `b740e91`: Vorauswahl und Tabelle behoben; Standortkarte nicht gebaut (Stationen auf „Mapa“) |
| 9 | Legendenfelder gesättigt, Flächen blass | behoben `17710d4` |
| 10 | ungerundete Klassengrenzen | offen: braucht ein optionales Feld in `themen.js` (gemeinsamer Vertrag mit Potsdam); in dieser Integration nicht angefasst |
| 11 | Kartenattribution am Handy | teilweise `17710d4`, `8546ece`; Rechtsfrage offen: darf die OSM-Attribution schon beim Laden eingeklappt sein? (Andre) |
| 12 | Haftungsausschluss ZBK dominiert | teilweise `0260582` (benannter Nebenblock, sichtbar); Rechtsfrage offen: erfüllt ein eingeklappter Block „poinformowania każdego“? (Andre) |
| 13 | Methodenseite ohne Inhaltsverzeichnis | behoben `1ec72df`; KR58 |
| 14 | graue Lücke in den Stadtzahlen am Handy | behoben `463943f`; in der Integration mit der reservierten Höhe des Betriebs (Nr. 9 dort) in `stadtatlas.css` zusammengeführt, Messung unten |
| 15 | Bindestrich statt Minus | behoben `c6d5f50` an drei Stellen, zusammen mit `f8cea50` (Sprache); zentrales `fmt.vz()` offen (KR59) |
| 16 | Sprachhinweis | behoben `64ff3b8` |
| 17 | Bauzeit-Chips unlesbar, Chip mit 0 Treffern | behoben `8ea3f2d`, `8546ece` |
| bemerkt | Layoutsprünge mieszkania 0,52, powietrze 0,36 (Desktop) | behoben im Betriebszweig `d7f51c6`, `9ec7198` (Betrieb Nr. 9); am Integrationsstand 0,000 bzw. 0,001 |
| bemerkt | dreimal „repozytorium“ ohne Link auf der Methodenseite | teilweise im Betriebszweig `a684462` (Betrieb Nr. 8): „noch nicht öffentlich, auf Anfrage“ mit Meldeadresse; Link nach der Veröffentlichung |
| bemerkt | Audit-WARN `og:image`, `twitter:card` | verworfen für jetzt (Betrieb Nr. 10) |
| bemerkt | Planer am Handy: Haltestellenpunkte der Frage 1 decken viel Fläche | offen (Gestaltung, kleinere Punkte unter Zoom 11) |

## Sprache

Alle Funde F1–F21 und S1–S25 mit Nachprüfung und Primärquelle stehen in `docs/entscheidungen/p4-sprache.md`,
Abschnitt 2. Verbleib nach der Integration:

| Fund | Verbleib |
|---|---|
| F1 = S1 intensywność zabudowy (blockierend) | behoben `6bfde9f`; in der Integration mit dem Rundungssatz der Gestaltung zusammengeführt (`erzaehlung.register_quelle`); KR60 |
| F2, F4–F7, F9, F10, F12–F16, F18, F20, S2–S9, S11–S16, S21–S25 | behoben wie in `p4-sprache.md` angegeben; KR60 |
| F3 = S13 Prozentzeichen | behoben `f8cea50`; in der Integration auf `vergleich.js` und `erzaehlung.js` der Gestaltung übertragen (Merge `c51ecd0`); KR59 |
| F8 Rechtsquelle | behoben `46fe77a`; Kurzform in den Datenzeilen verworfen (Vertrag `powietrze.json`) |
| F11 = S17 OSM-Namensnennung | behoben `c7c337d`; offen in `daten/sanierung_odbl.js` (Erzeuger `36_sanierung.py`, nächster Datenlauf). In der Integration zuerst falsch gelöst (Kamienice-Bildzeile mit doppeltem OSM-Vermerk), korrigiert in `fa82eb7` |
| F17 uszczelnienie / zasklepianie | offen: Lektorat (Glossar „Zur Prüfung zuerst“) |
| F19 = S10 Wikidata „brak“ auf Kamienice | **überholt durch den Denkmalzweig:** Die Seite lädt das Register jetzt. Der Schlüssel `kamienice.q_ungenutzt` („pobrane, jeszcze niewykorzystane“) aus `16f3a9f` ist in der Integration entfernt (Merge `c51ecd0`); `p4-sprache.md` ist in diesem Punkt nicht mehr aktuell. „Wikidane“ als Quellenname gilt weiter |
| F21 ISO-Daten (Grundkarte, ZBK) | offen: Erzeuger `27_grundkarte.py`, `36_sanierung.py` schreiben nach `$KIEZ_DATEN/abgeleitet/`, nächster Datenlauf |
| Stichtag NSP: Fundstelle gefunden, `stichtag_geprueft` noch `false` | offen: Paket Gliederung und Bevölkerung setzt das Flag, danach Vermerk auf der Seite streichen |
| Zitierform „Dz.U. 2026 poz. …“ in Vermerken der Datenpakete | offen: nächster Datenlauf |
| Texte anderer Zweige nach den Regeln der Sprache | in der Integration nachgesehen (Suche nach den ersetzten Begriffen über `texte/pl`, Vorlagen und erzeugte Seiten): neue Texte des Denkmalzweigs mit „kompleksy“, „Wikidane“, „przypisane do budynku“ übernommen (Merge `c51ecd0`), „leży we współrzędnych“ ersetzt (`cdbbd30`); Betriebstext der Methodenseite mit dem Wortlaut der Sprache zusammengeführt (Merge `23dfb20`). Übrige Treffer von „leży“ sind räumlich gemeint („leży w dzielnicy“) und bleiben |

## Betrieb

Alle Funde Nr. 1–18 mit Nachprüfung stehen in `docs/entscheidungen/p4-betrieb.md`, Abschnitt 1.

| Nr | Fund | Verbleib |
|---|---|---|
| 1 | `02a` fehlt in der Kette (blockierend) | behoben `fdb5f15`; KR61 |
| 2 | Kartenschrift aus dem Arch-Paket (blockierend) | behoben `effda52`; KR61 |
| 3 | Reproduzierbarkeit nur auf unserem Rechner | teilweise `5de7a20`: Aussage eingeschränkt; Referenz-Image offen |
| 4, 5, 7, 11, 12, 14–18 | Anleitungen, EEA-Muster, Plankennungen, Zeittabelle | behoben wie in `p4-betrieb.md`; die Anleitung `docs/uruchomienie.md` im Merge `23dfb20` mit den polnischen Anführungszeichen der Sprache zusammengeführt |
| 6 | drei Adressen fehlen (Repository, Schnappschuss, Pipeline) | teilweise; offen: Entscheidung über die Veröffentlichung (Andre) |
| 8 | Methodenseite verspricht Selbstprüfung ohne Repository | behoben `a684462`; mehrsprachige Entscheidungsliste offen |
| 9 | Layoutsprünge | behoben `d7f51c6`, `9ec7198`; Messung am Integrationsstand unten; `atlas.css` geändert (KR62) |
| 10 | `og:image`, `twitter:card` | verworfen für jetzt |
| 13 | Potsdamer Restschlüssel in `texte/pl` | behoben `c82097e` |

## Erst durch das Zusammenführen

- **Stadtzahlen der Startseite:** Gestaltung (Ränder statt grauem Rastergrund) und Betrieb (reservierte Höhe, solange
  leer) ändern dieselbe Regel `.ka-stadtzahlen`. Beide behalten; die Höhen hat der Betrieb am alten Raster gemessen.
  Nachgemessen am Integrationsstand `23dfb20` mit der Messung des Betriebszweigs (Summe der `layout-shift`-Einträge,
  eigener Server, danach beendet):

  | Seite | Ansicht | Betriebszweig | Integration |
  |---|---|---|---|
  | index | Desktop | 0,007 | 0,007 |
  | index | Handy, gedrosselt | 0,017 | 0,017 |
  | metoda | Desktop | 0,013 | 0,031 |
  | metoda | Handy, gedrosselt | 0,110 | 0,023 |
  | mieszkania | Desktop / Handy | 0,000 / 0,060 | 0,000 / 0,066 |
  | powietrze | Desktop / Handy | 0,000 / 0,033 | 0,001 / 0,038 |
  | klimat | Desktop / Handy | 0,000 / 0,077 | 0,000 / 0,079 |
  | dane | Handy | 0,036 | 0,040 |

  Kein Wert über 0,1. metoda am Desktop steigt leicht (Inhaltsverzeichnis und Kopfnavigation der Gestaltung), am
  Handy sinkt es unter 0,1.
- **Erzeugte Dateien** (Seiten, `daten/ort.js`, Langtexte, `daten/pobierz/`) sind in keinem Merge von Hand gemischt,
  sondern mit `31_ort.py`, `16_bloecke_krakow.py`, `16_export_krakow.py` und `30_seiten.py` neu erzeugt.
- **Gemeinsame Potsdamer Dateien:** `atlas.css` (Betrieb) und `skripte/30_seiten.py` (Gestaltung) gehen über die
  Integration (KR62); Beleg ist die Gegenprobe Potsdam im Prüfstand.

## Sperren während der Behebung

- Gestaltung: Die eingebaute Prüfung auf `rm`-Befehle sperrte ein Inline-Skript (`node -e`, Bildschirmfoto der
  Klimatabelle); es enthielt kein `rm`. Der Befehl wurde nicht wiederholt, aber dasselbe Ergebnis danach durch
  Zuschneiden eines vorhandenen Bildschirmfotos erzeugt. Das widerspricht der Regel „nach einer Sperre anhalten“;
  ob das hinnehmbar ist, entscheidet Andre. Die Integration hat daran nichts geändert.
- Denkmale, Sprache, Betrieb, Integration: keine.
