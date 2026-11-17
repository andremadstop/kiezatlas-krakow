# Entscheidungen

Festgelegte Regeln des Kiezatlas Kraków mit Anlass, Entscheidung, Begründung, Verworfenem und dem, wann neu zu prüfen
ist. Nummern mit dem Präfix **KR**, damit sie weder mit dem Kiezatlas Potsdam (A1 bis A20) noch mit dem
Entscheidungsprotokoll der Geodaten-Import-Pipeline (E1 bis E48) verwechselt werden. Grundlage sind die Bauvorlage
und die Entscheidung nach der Machbarkeitsprobe vom 13.11.2026; beide liegen im internen Vault der UG und sind nicht
öffentlich. Was dort steht und hier gebraucht wird, steht unten ausgeschrieben.

Entschieden hat André Stiebitz, für die Themenauswahl nach der Machbarkeitsprobe ausdrücklich an Claude delegiert;
Vorschläge, Prüfungen und Umsetzung kamen von KI-Agenten (Claude). Pakete liefern Vorschläge als
`docs/entscheidungen/<paket>.md`; übernommen werden sie hier von der Belegschicht. Die Projektleitung hat am
13.11.2026 abends die Vorschläge KR13 bis KR24 bestätigt und die offenen Fragen zu KR3, KR17, KR18, KR20, KR22 und
KR24 entschieden; was sie entschieden hat, steht im jeweiligen Eintrag unter „Stand“. Vorschläge der Pakete, die sie
nicht ausdrücklich entschieden hat, stehen als „Vorschlag, von der Integration übernommen, Bestätigung offen“. Am
14.11.2026 hat die Projektleitung KR28 bis KR44 bestätigt, bei KR30, KR31, KR39, KR40, KR42 und KR43 mit Auflagen;
diese Einträge stehen als „bestätigt (14.11.)“, die Auflagen im jeweiligen „Stand“. KR45 bis KR51 stammen aus den
Paketen der Nacharbeit vom 14.11.2026 (Daten-Nacharbeit, Oberfläche und Auslieferung, Offene Wissenschaft). KR52 bis KR54 stammen aus der Behebung der Funde vom 14.11.2026 (Bereiche Daten, Oberfläche, offen;
`docs/entscheidungen/fix-daten.md`, `fix-oberflaeche.md`, `fix-offen.md`); KR45 bis KR54 hat die Projektleitung am 14.11.2026 nach der Behebung bestätigt, KR39 mit Entscheidung zur offenen Frage; was die Behebung an
bestehenden Einträgen ändert, steht dort jeweils als „Behebung 14.11.2026“. Die kleinen, nicht behobenen Funde der
Durchsicht stehen in `docs/entscheidungen/review-20261114.md`. KR55 und KR56 hat die Projektleitung am 14.11.2026
nach der Prüfung des ersten echten Wohnungsmarkt-Ergebnisses entschieden bzw. bestätigt. KR57 bis KR62 stammen aus
der Behebung der Sichtung vom 14./15.11.2026 (Bereiche Denkmale, Gestaltung, Sprache, Betrieb;
`docs/entscheidungen/DZ.md` §9, `p4-gestaltung.md`, `p4-sprache.md`, `p4-betrieb.md`) und stehen als Vorschlag der
Integration; Verbleib aller Sichtungsfunde in `docs/entscheidungen/review-p4a.md`. KR63 bis KR68 stammen aus der
Vorbereitung der Veröffentlichung 1.0.0 vom 15.11.2026 (Nacharbeit zur Sichtprüfung, Filme, Veröffentlichung) und
ihrer Abnahme; sie stehen als Vorschlag der Integration, Verbleib aller Abnahme-Funde in
`docs/entscheidungen/review-p4b.md`.

## Übersicht

| Nr. | Entscheidung | Stand |
|---|---|---|
| KR1 | Rechen-Koordinatensystem EPSG:2178 (PL-2000 Zone 7) als Parameter `rechen_srid` | 13.11.2026 |
| KR2 | Stadtteilnummer `nr` „01“ bis „18“, angezeigt die römische Zählung | 13.11.2026; Gruppenzuordnung geprüft (KR17) |
| KR3 | Stadtteilgrenzen aus OpenStreetMap, daher `stadtteile_odbl.js`; abgeleitete Werte als `_odbl`-Dateien (Folgefrage: Variante a) | 13.11.2026, Folgefrage bestätigt am Abend; neu prüfen nach Antwort der Stadt |
| KR4 | Keine Bauzeiten-Kaskade und keine Heizungsseite | 13.11.2026 |
| KR5 | Polnisch im Wurzelordner, Englisch und Deutsch in `en/` und `de/`, keine automatische Umleitung | 13.11.2026 |
| KR6 | Beispieldaten liegen bis zu den echten Daten direkt unter `daten/`, sichtbar gekennzeichnet | 13.11.2026 |
| KR7 | Neutrale Feldnamen: `in_stadt` statt `in_potsdam`; `lhp` wird nicht umbenannt, weil die Bauzeiten-Kaskade entfällt | 13.11.2026 |
| KR8 | Themen der Zellkarte vorläufig nach dem Eurostat-Gitter 2021 (1 km) | 13.11.2026, vorläufig |
| KR9 | Gegenprobe Potsdam als eigener Lauf neben `pruefen.sh` | 13.11.2026 |
| KR10 | Startgewicht des Planers: Potsdams Grenze gilt in der Gegenprobe ohne die Textschicht, Kraków bekommt eigene Grenzen | 13.11.2026, bestätigt (Gegenprobe `belege/gegenprobe_potsdam-20261113-291befb.log`, 0 Abweichungen) |
| KR11 | Themen nach Datenlage: neue Krakauer Themen nur nach Lizenz- und robots-Prüfung im eigenen Paket | 13.11.2026 |
| KR12 | Vertragsänderung für die Oberflächen-Texte (`t()` in den Modulen, Ortsvertrag je Sprache) | 13.11.2026, bestätigt (Gegenprobe 0 Abweichungen außer KR10) |
| KR13 | Werte aus OSM-Grenzen nur in `_odbl`-Dateien; seit der Folgefrage zu KR3 (Variante a) auch Zellen, Kennzahlen und Planer | 13.11.2026, bestätigt (abends) |
| KR14 | Texte neuer Themen bis zur Seite unter `docs/entscheidungen/`, nicht unter `texte/` | 13.11.2026, bestätigt (abends) |
| KR15 | Neue Datenverträge der Themen; 1-km-Zellen in `erreichbar*`, `lod1`/`lod2` in `gebaeude.json`, eigene Kacheln in `grundkarte.json` | 13.11.2026, bestätigt (abends) |
| KR16 | Fußweg je Zelle ohne Landesfilter, Zelltabelle als Parameter mit Lizenz aus dem Tabellenkommentar | 13.11.2026, bestätigt (abends) |
| KR17 | Bevölkerung aus Eurostat-Gitter und NSP 2021, Mindestfallzahl 100, MSIP nur intern; III und XV mit dokumentierter Ausnahme zugeordnet | 13.11.2026, bestätigt (abends) |
| KR18 | Gebäude aus BDOT10k über den inneren Punkt; LoD2-Höhen (Stand 2017) veröffentlicht, Lesart der Geoportal-Erklärung bestätigt | 13.11.2026, bestätigt (abends) |
| KR19 | Haltestellen-Datei, Taktklassen 6/2/1 als Orientierung, `st` über die Zelle | 13.11.2026, bestätigt (abends) |
| KR20 | Luft aus der EEA-Jahresstatistik per Handdownload, Abzeichen „orientacyjnie“; EEA-Daten als CC BY 4.0 mit „EEA; Daten: GIOŚ“ | 13.11.2026, bestätigt (abends) |
| KR21 | Grundkarte aus eigenen Vektorkacheln, nur BDOT10k, Noto Sans | 13.11.2026, bestätigt (abends) |
| KR22 | Wohnungsmarkt nur aggregiert, Median ab 10 Käufen, nur Handdownload | 13.11.2026, bestätigt (abends); RCN fehlt noch |
| KR23 | Klima: Bebauung und Verkehr als Näherung für Versiegelung, Acker kein Grün, Hitze nur als Grenze | 13.11.2026, bestätigt (abends) |
| KR24 | Denkmale als Teilmenge, nur Bauzeitklassen; WDQS erlaubt, aber durch robots.txt gesperrt, daher Wikidata aus dem Eingang | 13.11.2026, bestätigt (abends) |
| KR25 | Ein gemeinsamer Ort für den OSM-Auszug: `kiezatlas-daten/krakow/eingang/`, Kopien nur mit Prüfsumme | 13.11.2026, bestätigt (abends) |
| KR26 | Schriften der Seiten mit allen polnischen Sonderzeichen | 13.11.2026, bestätigt (abends) |
| KR27 | Neues Thema „Sanierungsatlas Wohnungsbestand“ | 13.11.2026, bestätigt (abends) |
| KR28 | Echtlauf mit OSM-Grenzen: neue `_odbl`-Namen, `st` nur in `_odbl`-Dateien, 3D-Dateien außerhalb des Repos | 13.11.2026, bestätigt (14.11.); Auslieferung der 3D-Dateien nach KR42 |
| KR29 | Fußweg-Ziele und Gliederung in der Datenbank, `sql/003_zellen.sql` | 13.11.2026, bestätigt (14.11.), mit der nachträglichen Ausnahme für `public.stadtteil` und `public.zensus_zelle` |
| KR30 | Schriften: Barlow mit `latin` und `latin-ext` je Schnitt zusammengefügt | 13.11.2026, bestätigt (14.11.) mit Auflage Kerning |
| KR31 | Sanierungsatlas: ZBK-Liste weiterverwendbar, Punkte nur für öffentliches Eigentum, Verortung über OSM, Typologie als Schätzung | 13.11.2026, bestätigt (14.11.) mit Auflagen: private Einträge nur gezählt, Punkte ab 3 Geschossen |
| KR32 | Grundkarte auf den Seiten: relative Pfade in `themen.js`, fehlende Quellen als Platzhalter, Kacheln über Entwicklungsserver und Deploy | 13.11.2026, bestätigt (14.11.), mit der Kachelkopie in `skripte/deploy_kopie.py` |
| KR33 | Denkmale aus OSM als ungeprüft gekennzeichnet, `stand` aus Abruftag bzw. Kopf des Auszugs | 13.11.2026, bestätigt (14.11.); Nachtrag 15.11.: Lage in einer Stichprobe geprüft, „ungeprüft“ nur noch ohne Sichtprüfung |
| KR34 | Infrastruktur: Pipeline-Stand fest, robots.txt vor jedem Rechner, Prüfsummen der Pakete wirken offline nicht | 13.11.2026, bestätigt (14.11.); `berichte/umgebung/` bleibt unversioniert |
| KR35 | Deploy: verkleinerte Auslieferung mit esbuild, Eigentum `package.json` | 13.11.2026, bestätigt (14.11.) |
| KR36 | Krakauer Seiten mit eigenen Modulen, Potsdamer Module unverändert; Seitenmodul der Karte `karta.js` | 14.11.2026, bestätigt (14.11.) |
| KR37 | Vergleich Kraków–Potsdam nur aus dem Eurostat-Gitter 2021 (1 km) | 14.11.2026, bestätigt (14.11.) |
| KR38 | Zahlen in Texten nur als Methode und Eigenname | 14.11.2026, bestätigt (14.11.) |
| KR39 | Startgewicht: 300 KB gz für die Startseite (heute darüber), Textschicht in der Gegenprobe hingenommen | 14.11.2026, bestätigt (14.11.) mit Auflage: vereinfachte Grenzen für die Übersicht; Grenze gilt als JavaScript-Startgewicht |
| KR40 | Beispieldaten auf den Seiten: Kasten, Marke an Abbildung und Tabelle, keine Stationskarte | 14.11.2026, bestätigt (14.11.) mit Auflage: zweite Fassung des Rahmenhinweises |
| KR41 | Seite `modernizacja` und Namensraum `sanierung.*` | 14.11.2026, bestätigt (14.11.); Glossarbegriffe als Vorschlag in `docs/glossar-pl.md` |
| KR42 | Gebäude in 3D nur auf Wunsch, Auslieferung über den Server | 14.11.2026, bestätigt (14.11.) mit Vorschlag: Auslieferung wie die Grundkarte, reproduzierbar |
| KR43 | Inhalt der Karten- und Themenseiten | 14.11.2026, bestätigt (14.11.) mit Auflagen (n < 10, eine Ortsmarke, Felder statt Sätze) |
| KR44 | Methode, Daten, Downloads und Zitierhinweis; Seiten `metoda` und `dane` | 14.11.2026, bestätigt (14.11.) |
| KR45 | Falschsätze mit begründeten Fundorten (`ausser` mit Grund) | 14.11.2026, bestätigt (14.11.) |
| KR46 | Gemeinsame Ortsmarke ul. Kościuszki 18 aus dem größten OSM-Gebäudeumriss (`representative_point`) | 14.11.2026, bestätigt (14.11.) (Umsetzung der Auflage zu KR43) |
| KR47 | Kopfleiste bis 860 px mit ganzer Hauptnavigation; Bildzeile der Stadtteilgrenzen als Sprachwert | 14.11.2026, bestätigt (14.11.); Vertragsänderung `ort.json` von der Integration übernommen |
| KR48 | Ein Befehl für die ganze Kette (`./atlas.sh`, `skripte/kette.py`) | 14.11.2026, bestätigt (14.11.) |
| KR49 | Rohdaten-Schnappschuss nur aus ausdrücklich erlaubten Quellen | 14.11.2026, bestätigt (14.11.); Upload offen (Andre) |
| KR50 | Prüfung vor Veröffentlichung in `pruefen.sh`; öffentlich nur ein frischer, bereinigter Export ohne Arbeitshistorie | 14.11.2026, bestätigt (14.11.); Veröffentlichung offen (Andre) |
| KR51 | CI ohne Rohdaten, Datenbank und Browser; `.zenodo.json` als `software` neben `CITATION.cff` als `dataset` | 14.11.2026, bestätigt (14.11.); CI nie auf GitHub gelaufen |
| KR52 | Schwelle der Gitteranteile aus der Ortskonfiguration (`themen[].mindestfallzahl`), fehlender Wert grau | 14.11.2026, bestätigt (14.11.); Vertragsänderung `ort.json` von der Integration übernommen |
| KR53 | Fehlender Langtext-Block erzeugt nichts; Seiten in Vorbereitung über `in_vorbereitung` | 14.11.2026, bestätigt (14.11.) |
| KR54 | Polnische Begriffe „delegatura (dawna dzielnica)“ und „przystanek klasy I lub II“ | 14.11.2026, bestätigt (14.11.); Glossar zur Prüfung durch den Lehrstuhl |
| KR55 | Wohnungsmarkt veröffentlicht nur Jahre ab 2019 (Schritt F11, `regeln.erstes_jahr`) | 14.11.2026, entschieden (Master); Spannenprobe 0 von 32 |
| KR56 | Sekundäre Unterdrückung mit mehreren Feldern (Nachtrag 4 zu Regel 4) | 14.11.2026, bestätigt (Master) |
| KR57 | Denkmalregister aus Wikidata auf `kamienice`, eigene Kartenebene `rejestr` (CC0) getrennt von OSM, Kennzahl „Registerpunkte“; ersetzt Teil von KR43 | 15.11.2026, bestätigt (15.11., Master) |
| KR58 | Rubriken „Tematy“ und „Metodologia“ in der Kopfleiste, ein Satzspiegel 1280 px, Inhaltsverzeichnis, keine feste Beispielmarke | 15.11.2026, bestätigt (15.11., Master) |
| KR59 | Prozentzeichen aus `fmt.anteil`, Minus U+2212 an Werten mit Vorzeichen | 15.11.2026, bestätigt (15.11., Master) |
| KR60 | Polnische Fachbegriffe der Sprachbehebung (udział powierzchni zabudowy, autorzy OSM, eksploatowany, kompleksy, stan na, przedział ufności) | 15.11.2026, bestätigt (15.11., Master) |
| KR61 | Betrieb ohne unsere Rechner: Schrift im Repository, Schritt `02a` in der Kette, Grenzen der Reproduzierbarkeit und des Repository-Zugangs offen benannt | 15.11.2026, bestätigt (15.11., Master) |
| KR62 | Änderungen an gemeinsamen Dateien des Potsdamer Stands (`atlas.css`, `skripte/30_seiten.py`) über die Integration | 15.11.2026, bestätigt (15.11., Master) |
| KR63 | Drei Belegfilme auf Polnisch unter `belege/filme/`, Lizenz CC BY 4.0 wie die Bildschirmfotos | 15.11.2026, bestätigt (Andre, CC BY 4.0) |
| KR64 | OSM-Kennzeichnung der Denkmale auf der Karte hell mit violettem Rand statt Ocker | 15.11.2026, Vorschlag |
| KR65 | Schnappschuss mit EEA-Auszug (CC BY 4.0) und Wikidata-Ergebnis (CC0), RCN-Transaktionen ausgeschlossen (Nachtrag zu KR49) | 15.11.2026, Vorschlag; vor dem Upload von Andre zu bestätigen |
| KR66 | Repository-Adresse als Schalter `repository` in `config/krakow.yaml`; Bedingungen in Langtexten, Rückfall auf „ungeprüft“ | 15.11.2026, Vorschlag |
| KR67 | Version 1.0.0 als bereinigter Export: ein Commit, Rollenadresse, Werkzeug der Herausgeberin nicht im Export | 15.11.2026, Vorschlag; Veröffentlichung bei Andre |
| KR68 | `./pruefen.sh` ohne Rohdaten: Luft und Wohnungsmarkt prüfen die Dateien, Neurechnung übersprungen | 15.11.2026, Vorschlag |
| KR69 | Repositorys öffentlich (Atlas, Pipeline mit Commit und DOI, Potsdam); `repository` gesetzt, offen nur der Schnappschuss | 15.11.2026, geprüft |
| KR70 | Gemeinsame Kiezatlas-Maschine in eigenem Repository (`kiezatlas`); Kraków enthält eine Kopie zu festem Commit (`MASCHINE.txt`, `MASCHINE.lock`, `skripte/maschine.py`, Prüfschritt in `pruefen.sh`). Maschinendateien werden hier nicht von Hand geändert. Erste Fassung byte-gleich mit dem Stand e7c85ca, ausgelieferte Seiten unverändert | 16.11.2026, Andre (ein Code für alle Städte, eigenes Repository) |

## KR1: Rechen-Koordinatensystem EPSG:2178

- **Anlass:** Potsdam rechnete fest in EPSG:25833 (ETRS89 / UTM 33N); die Zahl stand in elf Skripten.
- **Entscheidung:** Abstände und Flächen werden in EPSG:2178 (ETRS89 / Poland CS2000 zone 7) gerechnet. Der Wert
  steht nur in `config/krakow.yaml` (`rechen_srid`); Skripte lesen ihn über `skripte/ort_konfig.py`, die DDL in
  `sql/` muss ihn gleich führen (`pruefen/geruest.py`).
- **Begründung:** Kraków liegt bei rund 19,9° O und damit in der Zone 7 des polnischen Systems 2000
  (Mittelmeridian 21° O); es ist das amtliche System für großmaßstäbige Karten in Polen.
- **Verworfen:** EPSG:2180 (PL-1992, landesweit, größere Längenverzerrung im Kleinen), EPSG:25834 (UTM 34N, das
  genaue Gegenstück zu Potsdam, aber nicht das Bezugssystem polnischer Quellen).
- **Neu prüfen, wenn:** eine Quelle mit hoher Lagegenauigkeit nur in einem anderen System vorliegt.

## KR2: Stadtteilnummer und Anzeige

- **Anlass:** Die 18 dzielnice werden amtlich römisch gezählt (I Stare Miasto … XVIII Nowa Huta); Potsdam nutzte
  zweistellige Nummern, deren erste Ziffer den Bezirk angab.
- **Entscheidung:** Interner Schlüssel `nr` = „01“ … „18“ (Sortierung als Text = als Zahl), angezeigt die römische
  Ziffer und der Name (`gliederung.anzeige_muster`). Die Gruppe (dzielnica historyczna) steht als eigenes Feld
  (`bezirk` = Gruppen-id) und bestimmt den Farbton. Im Hash steht `st=<nr>`.
- **Begründung:** Gleiche Datenform wie in Potsdam, damit der übernommene Code ohne Sonderfall läuft.
- **Verworfen:** nicht angegeben (keine Alternative festgehalten).
- **Neu prüfen, wenn:** die Zuordnung der dzielnice zu den vier historischen Stadtbezirken amtlich geprüft ist.
  Gegen die delegatury der BDOT10k ist sie seit dem 13.11.2026 geprüft (`zuordnung_geprueft: true`, KR17); eine
  amtliche Liste der Stadt dazu ist nicht gelesen.

## KR3: Stadtteilgrenzen aus OpenStreetMap

- **Anlass:** Die Grenzen der dzielnice im städtischen Portal MSIP sind im BIP als offene Daten beschrieben, die
  Nutzungsbedingungen des Portals von 2016 erlauben aber nur nichtkommerzielle Nutzung ohne Weitergabe.
- **Entscheidung:** Arbeitsgrundlage sind die Grenzen aus OpenStreetMap (ODbL 1.0). Deshalb heißt die Datei
  `daten/stadtteile_odbl.js` (Vertrag `daten/schema/stadtteile_odbl.json` mit `x-odbl`), der Kopf trägt den
  ODbL-Vermerk. Die MSIP-Grenzen dienen nur intern als Gegenprobe der Geometrie. Eine Anfrage an die Stadt zur
  Lizenz ist vorbereitet.
- **Begründung:** Die Lizenz der OSM-Grenzen ist eindeutig (ODbL 1.0); bei den MSIP-Grenzen widersprechen sich
  Beschreibung und Nutzungsbedingungen, und bei einem Widerspruch gilt die engere Lesart (KR11).
- **Verworfen:** die MSIP-Grenzen ohne schriftliche Lizenzklärung zu veröffentlichen.
- **Folge, bestätigt durch die Projektleitung am 13.11.2026 abends:** Variante (a). Werte, die auf den OSM-Grenzen beruhen (Zuordnung der Zellen, Kennzahlen je
  dzielnica, Stadtteile, Dateien je dzielnica), werden als `_odbl`-Dateien unter der ODbL mit dem Vermerk
  „© OpenStreetMap-Mitwirkende, ODbL“ ausgeliefert; `SEITENDATEN_AUS_OSM = True` in `skripte/02_bevoelkerung.py`.
  Prüfungen, die dadurch absichtlich rot würden, werden auf den neuen Stand gebracht, nicht abgeschaltet. Umsetzung
  im Einzelnen: KR13.
- **Neu prüfen, wenn:** die Stadt die Lizenz schriftlich klärt.

## KR4: Keine Bauzeiten-Kaskade und keine Heizungsseite

- **Anlass:** Machbarkeitsprobe vom 13.11.2026: Das Bevölkerungsgitter trägt kein Baujahr, das Baujahr im
  Gebäudekataster ist kostenpflichtig; das Heizungsregister (CEEB) ist nicht offen.
- **Entscheidung:** Die Seiten zu Bauzeiten im Potsdamer Format und zur Heizungsart entfallen. An ihre Stelle treten
  Kamienice und Denkmale (ehrlich als Denkmal-Teilmenge, ohne Flächenaussage zu Baujahren) und die Seite Luft
  (amtliche Messstationen). Beides steht im Atlas offen im Abschnitt „Grenzen“. Die Potsdamer Skripte 21 bis 26 und
  `jahre.js` bleiben im Repo, weil die Gegenprobe Potsdam sie braucht; `pruefen.sh` überspringt ihre Prüfungen mit
  diesem Grund.
- **Begründung:** Ohne offene Daten trüge die Seite keine belegten Zahlen (KR11).
- **Verworfen:** keine Alternative erwogen; eine offene Quelle für Baujahre oder Heizungsart hat die
  Machbarkeitsprobe nicht gefunden.
- **Neu prüfen, wenn:** eine offene Quelle für Baujahre oder Heizungsart kleinräumig erscheint.

## KR5: Sprachen und Ordner

- **Anlass:** Der Atlas erscheint mit polnischer Oberfläche und englischer und deutscher Fassung; jede Fassung braucht
  eine eigene Adresse.
- **Entscheidung:** Polnisch ist Standardsprache und liegt im Wurzelordner, Englisch und Deutsch in `en/` und `de/`
  mit denselben Dateinamen. Der Sprachschalter tauscht den Ordner und nimmt den Hash mit. Keine Umleitung nach der
  Browsersprache; stattdessen ein einmaliger Hinweis („Also available in English“), gemerkt im Browser.
- **Begründung:** Eine automatische Umleitung bricht file://, Suchmaschinen und geteilte Links.
- **Verworfen:** Sprache als Hash- oder Suchparameter (eine URL je Inhalt und Sprache ist für hreflang nötig).
- **Neu prüfen, wenn:** nicht angegeben.

## KR6: Beispieldaten unter `daten/`

- **Anlass:** Vor den Datenpaketen gibt es keine echten Daten; die Seiten sollen trotzdem vollständig laufen.
- **Entscheidung:** `pruefen/fixtures_krakow.py` schreibt Beispieldaten (Rechtecke statt Grenzen, 1-km-Gitter,
  Werte aus einem festen Zufallsgenerator) direkt nach `daten/`, jede Datei mit `fixture: true`. Jede Seite, die
  eine solche Datei lädt, zeigt den Hinweis „Beispieldaten“ (`rahmen.js`). Die Datenpakete ersetzen die Dateien;
  `pruefen/daten.py --veroeffentlichung` macht jede verbliebene Beispieldatei zum Befund.
- **Begründung:** Die Seiten laden ihre Daten von festen Pfaden. Liegen die Beispieldaten dort, tauschen die
  Datenpakete nur Dateien aus; die Kennzeichnung bleibt über `fixture: true` und die Prüfung erzwungen.
- **Verworfen:** Beispieldaten nur unter `daten/fixtures/` wie in Potsdam (die Seiten müssten dann je Paket auf
  echte Pfade umgestellt werden).
- **Neu prüfen, wenn:** das letzte Datenpaket seine Dateien ersetzt hat; vor dem ersten veröffentlichten Stand muss
  `pruefen/daten.py --veroeffentlichung` grün sein.

## KR7: Neutrale Feldnamen

- **Anlass:** Die Bauvorlage verlangte, potsdamgebundene Feldnamen (`in_potsdam`, `lhp`) neutral umzubenennen.
- **Entscheidung:** Das Feld `in_potsdam` heißt in Vertrag, SQL, Skripten und Prüfungen `in_stadt` (ebenso
  `kontrolle.gebaeude_in_stadt`). Das Feld `lhp` (Vergleich mit der Gebäudestatistik der Landeshauptstadt Potsdam)
  wird nicht in `vergleich_stadt` umbenannt.
- **Begründung:** `lhp` gehört nur zur Bauzeiten-Kaskade, und die entfällt für Kraków (KR4, Entscheidung nach der
  Machbarkeitsprobe vom 13.11.2026). Ein umbenanntes Feld hätte in Kraków keine Daten und keinen Leser. Im Code steht
  `lhp` nur noch als Potsdamer Bestand, damit die Gegenprobe Potsdam (KR9) aussagekräftig bleibt: Die unveränderte
  Potsdamer Prüfung `B5_jahre.mjs` liest `KIEZ_JAHRE_METHODE.lhp` und `lhp_2025` und prüft die Tabelle `#j-m-lhp`.
- **Verworfen:** Umbenennen nach der Bauvorlage (Abschnitt 1 und Inhalt des Gerüsts). Dann wäre `M.lhp` in der
  Gegenprobe undefiniert und B5 schlüge fehl; ohne Umbenennung der Daten zeigte der umgebaute Code dort keine
  Vergleichstabelle. Die Bauvorlage ging noch von einer Kaskade für Kraków aus.
- **Betroffen:** `jahre.js`, `jahre.css`, `daten/schema/jahre_methode.json` (Vertrag, bleibt unverändert),
  `skripte/24_*`, `skripte/26_*`, `pruefen/B5_schema/`.
- **Folge:** Den Codepfad mit `lhp` entfernt der Eigentümer von `jahre.js` (Paket Seiten Kamienice und Planer), wenn
  er die Kamienice-Seite ohne Kaskade baut; dann fällt das Feld ganz weg und die Gegenprobe prüft B5 gegen den
  Potsdamer `jahre.js`.
- **Neu prüfen, wenn:** eine offene Quelle für Baujahre kleinräumig erscheint und die Kaskade für Kraków doch kommt
  (dann mit neutralem Namen `vergleich_stadt` als Vertragsänderung).

## KR8: Themen der Zellkarte vorläufig

- **Anlass:** Die Potsdamer Themen der Zellkarte stammen aus dem deutschen Zensus 2022 und gibt es für Kraków nicht.
- **Entscheidung:** Themen stehen in der Ortskonfiguration (`themen`), nicht mehr in `themen.js`. Für Kraków
  vorläufig: Einwohner je Zelle, Anteil unter 15 Jahren, Anteil 65 Jahre und älter, nach den Merkmalen des
  Eurostat-Gitters 2021 (1 km, CC BY 4.0).
- **Begründung:** Das Eurostat-Gitter 2021 ist nach der Machbarkeitsprobe die offene Quelle mit Merkmalen je Zelle
  (KR11).
- **Verworfen:** nicht angegeben (keine Alternative festgehalten).
- **Neu prüfen, wenn:** das Paket Gliederung und Bevölkerung die Merkmale aus dem Handdownload belegt hat
  (Vertragsänderung über die Integration).

## KR9: Gegenprobe Potsdam als eigener Lauf

- **Anlass:** Der Umbau (Textschicht, Ortskonfiguration, Zahlenformate, Rechen-SRID, Feldnamen) darf an Potsdam
  nichts ändern. Die Probe braucht `../kiezatlas-potsdam` und rund zehn Minuten.
- **Entscheidung:** `pruefen/gegenprobe_potsdam.sh` vergleicht den unveränderten Potsdamer Stand mit dem umgebauten
  Code auf denselben Potsdamer Seiten und Daten (Browserprüfungen, Codepfade, Textabzug). In `pruefen.sh` läuft sie
  nur mit `--gegenprobe`. Ergebnis und bekannte Abweichungen stehen in `docs/rundgang.md`, Abschnitt „Bau“.
- **Begründung:** Zehn Minuten Laufzeit und das Nachbar-Repo würden jeden Lauf von `pruefen.sh` verlängern und an
  Dateien außerhalb dieses Repos binden.
- **Verworfen:** die Gegenprobe in jedem Lauf von `pruefen.sh` (aus diesem Grund).
- **Neu prüfen, wenn:** nicht angegeben.

## KR10: Startgewicht des Planers in der Gegenprobe

- **Anlass:** In der Gegenprobe (KR9) kippen in `A7_planer.mjs` nur die beiden Prüfungen „Startgewicht … mit echten
  Daten“ (file:// und HTTP). Potsdam lädt dort 320 KB gz JavaScript bei einer Grenze von 320 KB, also mit weniger als
  0,5 KB Luft. Der umgebaute Code lädt zusätzlich die Textschicht `daten/ort.js`, `i18n.js` und `texte/de/kern.js`,
  zusammen rund 3 KB gz.
- **Entscheidung:** Die Grenze von 320 KB ist ein Leistungsbudget der Potsdamer Auslieferung. Der umgebaute Code
  wird für Potsdam nie ausgeliefert. Die Gegenprobe lässt deshalb genau diese Abweichung zu, aber nur, wenn alles
  Folgende aus den Dateien nachgerechnet stimmt (gzip -9 wie `A7_planer.mjs`, keine gerundeten Werte):
  1. Abweichend sind nur Prüfungen „Startgewicht … mit echten Daten“; alle übrigen ok- und FEHLT-Zeilen sind gleich.
  2. `planer.html` lädt genau die drei Dateien der Textschicht zusätzlich, und die Fixture-Läufe laden Potsdams
     Dateien plus genau diese drei.
  3. Der gemeinsame Code, den `planer.html` lädt (`kopf.js`, `themen.js`, `planer.js`), ist zusammen nicht schwerer
     als in Potsdam.

  Die Gegenprobe gibt beide Werte in Byte aus und meldet die Zeile als „Ausnahme KR10“, nicht als schlichtes ok.
  Kraków bekommt eigene Grenzen (Bauvorlage: Startseite je Sprache unter 300 KB gz), die das Paket Seiten Kamienice
  und Planer mit den Krakauer Daten festlegt.
- **Begründung:** wie im ersten Absatz der Entscheidung: Die Grenze ist ein Budget der Potsdamer Auslieferung, und
  der umgebaute Code wird für Potsdam nie ausgeliefert; die drei Bedingungen stellen sicher, dass die Mehrlast nur
  aus der Textschicht kommt.
- **Verworfen:** Kommentare in `planer.js`, `themen.js` und `kopf.js` streichen (spart rund 3 KB gz, aber nur knapp
  genug, und es löscht die Methodenbeschreibung im Code, um eine Messung zu bestehen); `KIEZ_ORT` in die Seiten
  schreiben oder Dateien zusammenlegen (umginge nur die Messung). Eine verkleinerte Kopie beim Deploy ist als
  **Ersatz für die Ausnahme** verworfen, weil die Gegenprobe die Quelldateien misst; als Auflage für die Auslieferung
  gilt sie dagegen (unten).
- **Bestätigt am 13.11.2026** durch die Integration: Ein eigener Lauf der Gegenprobe gegen `291befb` ergab
  0 Abweichungen; die Ausnahme greift nur bei den zwei Startgewicht-Zeilen (323 KB gz; gemeinsamer Code 437 B gz
  leichter als in Potsdam, Textschicht 3.368 B gz zusätzlich). Beleg: `belege/gegenprobe_potsdam-20261113-291befb.log`.
- **Auflage:** Die Auslieferung verkleinert JavaScript, sodass das Startgewicht des Planers live unter 320 KB gz
  bleibt, und belegt das mit einer Messung (Paket Deploy). Die Bauvorlage verlangte für den Regressionsfall „ohne
  Abweichung“; die Abweichung von dieser Vorgabe ist damit entschieden, nicht mehr offen.
- **Neu prüfen, wenn:** die Textschicht wächst (Bedingung 3 fängt nur den gemeinsamen Code) oder Potsdam seine
  Grenze ändert.

## KR11: Themen nach Datenlage

- **Anlass:** Die Machbarkeitsprobe vom 13.11.2026 hat je geplanter Seite geprüft, ob offene Daten sie tragen.
  Zwei Seiten entfallen (KR4); dafür gibt es in Kraków Daten, die Potsdam nicht hatte.
- **Entscheidung:** Seiten und Datengrundlage nach dieser Probe:

  | Seite | Daten | Bedingung |
  |---|---|---|
  | Startseite, Stadtteile in Zahlen | Eurostat-Gitter 2021 (1 km, CC BY 4.0), NSP 2021 je rejon statystyczny (GUS, mit Quellenangabe) | Werte je dzielnica aus den rejony, sobald deren Geometrie per Handdownload vorliegt; das 1-km-Gitter nur als Übersicht und so benannt |
  | Stadtteilgrenzen | OpenStreetMap (ODbL) | KR3 |
  | Gebäude und 3D | BDOT10k (Funktion, Geschosse), LoD1 2024 und LoD2 2017 (Handdownload) | ersetzt Potsdams Gebäudeebene |
  | Kamienice und Denkmale | Denkmalregister des NID, gminna ewidencja zabytków, Wikidata, OSM `start_date` | als Teilmenge der Denkmale benannt, keine Flächenaussage zu Baujahren (KR4) |
  | Erreichbarkeit, Planer | GTFS der ZTP (CC BY 4.0), OSM-Fußwegnetz, Einrichtungen aus BDOT10k und OSM | Taktklassen wie in Potsdam |
  | Pünktlichkeit (neu) | GTFS-RT der ZTP | Lizenz und Dauer des Mitschnitts im Paket prüfen, ohne Klärung entfällt die Seite |
  | Wohnungsmarkt (neu) | Rejestr cen nieruchomości (kostenfrei seit 13.02.2026) | Lizenz und Datenschutz (Einzelkäufe) im Paket prüfen, nur zusammengefasst veröffentlichen |
  | Klima: Versiegelung, Grün, Hitze (neu) | BDOT10k-Flächen, Geländemodell, Orthofoto | Hitze nur mit offener Quelle für Oberflächentemperatur (etwa Landsat oder Copernicus) |
  | Luft (neu, statt Heizung) | Messstationen des GIOŚ | Lizenz im Paket prüfen; Kohleverbot 2019 nur mit Quelle |
  | Grundkarte | eigene Vektorkacheln aus BDOT10k und OSM, selbst gehostet | der WMTS des GUGiK liefert nur EPSG:2180 und verbietet das Abgreifen ganzer Kachelsätze |
  | Vergleich Kraków–Potsdam | nur Kennzahlen mit gleicher Definition | sonst weglassen |

  Jedes neue Thema prüft im eigenen Paket zuerst Lizenz und robots.txt. Widersprechen sich die Angaben, hält das
  Paket an und meldet es, statt die günstigere Lesart zu wählen.
- **Begründung:** Eine Seite, deren Daten nicht offen sind, würde entweder Zahlen ohne Beleg zeigen oder Daten
  weitergeben, die nicht weitergegeben werden dürfen.
- **Verworfen:** die Bauvorlage mit Bauzeiten-Kaskade und Heizungsseite (KR4); die Grenzen aus dem städtischen
  Portal ohne Lizenzklärung (KR3).
- **Neu prüfen, wenn:** ein Paket bei Lizenz oder robots.txt einen Widerspruch findet (dann entfällt die Seite oder
  bekommt einen Ersatz über die Integration) oder eine neue offene Quelle erscheint.

## KR12: Vertragsänderung für die Oberflächen-Texte

Stand: bestätigt durch die Projektleitung am 13.11.2026. Herkunft und Umsetzung im Einzelnen:
`docs/entscheidungen/d3.md` (dort als „KR11“ vorgeschlagen, umnummeriert, weil KR11 schon vergeben war).

- **Anlass:** Im übernommenen JavaScript standen rund 400 deutsche Textstellen, und zwar in Modulen, die
  eingefrorene Verträge sind oder den Seitenpaketen gehören (`atlas.js`, `karte.js`, `schaugrafik.js`, `planer.js`,
  `kopf.js`, `themen.js`).
- **Entscheidung:** Einmalig ersetzt das Paket Oberflächen-Texte die deutschen Textstellen mechanisch durch `t()`. Die
  deutschen Werte bleiben wörtlich, die Logik bleibt unverändert. Dazu kommen neue Textdateien
  `texte/<lang>/karte.js` und `planer.js`, eine erweiterte `pruefen/texte.py` und der Ortsvertrag `stadt_amtlich`
  und `stadt_art` je Sprache. Potsdamer Quellenvermerke bleiben wörtlich und stehen auf einer begründeten
  Ausnahmeliste. Die Gegenprobe Potsdam spielt die Textdateien je Seite ein.
- **Begründung:** Sonst müsste jedes Seitenpaket dieselbe mechanische Arbeit an fremden Stellen wiederholen. Die
  Gegenprobe belegt, dass Potsdam auf Deutsch gleich bleibt: 0 Abweichungen außer KR10, Startgewicht 327 KB gz.
- **Verworfen:** Texte nur als Schlüssel liefern und das Umverdrahten den Seitenpaketen überlassen; Ausnahmen als
  Kommentare in den Modulen, weil das das Startgewicht erhöht (KR10).
- **Neu prüfen, wenn:** die Datenpakete die Potsdamer Quellenvermerke ersetzen (dann wird die Ausnahmeliste leer)
  oder ein Seitenpaket die Satzbauten in `atlas.js`, `karte.js` oder `planer.js` ändert.

## KR13: Werte aus OSM-Grenzen nur in `_odbl`-Dateien, bis die Folgefrage zu KR3 entschieden ist

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends; die Folgefrage zu KR3 ist entschieden (Variante a, unten „Nach der Entscheidung“). Herkunft:
`docs/entscheidungen/D4.md`, `D5.md`, `D6.md`, `dk.md`, `DW.md`.

- **Anlass:** KR3 lässt offen, ob Kennzahlen, die aus den OSM-Grenzen der dzielnice abgeleitet sind (Fläche,
  Einwohner, Dichte, Anteile, Zuordnung `st`), selbst unter die ODbL fallen. Die Pakete der Phase Datenpakete haben dafür echte
  Werte gerechnet.
- **Entscheidung:** Es gilt die strengste Lesart. Alles, was an den OSM-Grenzen hängt, steht nur in Dateien mit
  `_odbl` im Namen, mit `x-odbl` im Vertrag und dem ODbL-Vermerk im Kopf: `steckbrief_dzielnice_odbl.js`,
  `gebaeude_dzielnice_odbl.js`, `klimat_stadtteile_odbl.js`, `denkmale_odbl.js`. Dateien ohne `_odbl` tragen für die
  dzielnice `null` mit Grund. `zellen.js`, `kennzahlen.*` und `stadtteile_odbl.js` bleiben Beispieldaten, bis die
  Folgefrage entschieden ist (`SEITENDATEN_AUS_OSM = False` in `skripte/02_bevoelkerung.py`). `planer.js` und das Feld
  `st` in `haltestellen.js` dürfen erst danach echte Werte je dzielnica tragen; `pruefen/D6_versorgung.py` wird
  absichtlich rot, wenn das vorher geschieht.
- **Begründung:** Eine rechtliche Klärung ist in den Paketen nicht möglich. Die Trennung hält die Dateien aus BDOT10k,
  GTFS und Eurostat frei von der Share-Alike-Pflicht.
- **Verworfen:** echte Werte in `kennzahlen.js` ohne Entscheidung (widerspricht KR3); die dzielnice ganz weglassen
  (die Werte sind gerechnet und belegt, offen ist nur ihre Lizenzfolge); MSIP-Grenzen (Lizenz-STOPP, KR3).
- **Nach der Entscheidung (Variante a, 13.11.2026 abends):** Die Seitendateien werden `_odbl`-Dateien mit
  Vertragsänderung: `zellen.js` → `zellen_odbl.js`, `kennzahlen.*` → `kennzahlen_odbl.*`, `planer.js` →
  `planer_odbl.js`, die 3D-Dateien je dzielnica `gebaeude/<nr>_odbl.js`; `SEITENDATEN_AUS_OSM = True`.
  `pruefen/D6_versorgung.py` prüft jetzt, dass `st` nur in `_odbl`-Dateien steht, statt eine echte Zuordnung zu
  verbieten. Umgesetzt im Echtlauf der Daten, Einzelheiten in KR28.
- **Neu prüfen, wenn:** amtliche Grenzen mit klarer Lizenz vorliegen (dann zurück zu Namen ohne `_odbl`).

## KR14: Texte neuer Themen bis zur Seite außerhalb von `texte/`

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends. Herkunft: `docs/entscheidungen/D4.md`, `D5.md`, `D7.md`, `DW.md`,
`dk.md`, `DZ.md`.
Umsetzung 14.11.2026: `powietrze`, `klimat` und `denkmale` liegen mit ihren Seiten unter `texte/<lang>/` (`git mv`),
`mieszkania` als Kopie, weil `pruefen/DW_mieszkania.py` den Vorschlag `DW-texte/` noch fest liest (offen, KR43);
`bevoelkerung`, `gebaeude` und `fussweg` haben noch keine Seite.

- **Anlass:** `pruefen/texte.py` meldet jeden Schlüssel, den noch keine Seite benutzt. Die Themenseiten entstehen erst
  in Phase Seitenbau; Textdateien unter `texte/<lang>/` würden `pruefen.sh` rot machen.
- **Entscheidung:** Die fertigen Textdateien der Themen liegen bis Phase Seitenbau unter `docs/entscheidungen/`:
  `D4/texte/<lang>/bevoelkerung.js`, `D5/texte/<lang>/gebaeude.js`, `D7_texte/<lang>/powietrze.js`,
  `DW-texte/<lang>/mieszkania.js`, `dk/texte/<lang>/klimat.js` und `DZ-texte/<lang>/denkmale.js`. Die Paketprüfungen
  prüfen sie dort (Format, gleiche Schlüssel, Platzhalter, Plural). Phase Seitenbau verschiebt sie mit `git mv` nach
  `texte/<lang>/`, zusammen mit der Seite, die sie benutzt. Die Namensräume `bevoelkerung`, `gebaeude`, `denkmale`
  und `fussweg` stehen seit diesem Eintrag in `daten/schema/texte.md`.
- **Begründung:** `pruefen.sh` bleibt grün, und die Texte sind trotzdem geprüft und übernahmefertig.
- **Verworfen:** Schlüssel in Kommentaren der Vorlagen erwähnen, nur damit die Prüfung sie findet (das täuscht die
  Prüfung); eine Ausnahme in `pruefen/texte.py`.
- **Neu prüfen, wenn:** Phase Seitenbau die Seiten baut oder die Belegschicht eine allgemeine Regel für Texte vor ihrer Seite
  festlegt.

## KR15: Neue Datenverträge und Vertragsänderungen der Phase Datenpakete

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends. Herkunft: die Paketvorschläge unter `docs/entscheidungen/`.

- **Anlass:** Die Themenpakete brauchen neue Datendateien. Laut `docs/rundgang.md` gibt es neue Dateien unter
  `daten/` nur mit einem neuen Vertrag über die Integration, und drei bestehende Verträge passten nicht zu Kraków.
- **Entscheidung:** Übernommen als Verträge der Integration: `steckbrief.json`, `steckbrief_dzielnice_odbl.json`
  (Gliederung und Bevölkerung), `gebaeude_kennzahlen.json`, `gebaeude_dzielnice_odbl.json` (Gebäude und 3D),
  `haltestellen.json` (Versorgung und Takt), `powietrze.json` (Luft), `mieszkania.json` (Wohnungsmarkt),
  `klimat.json`, `klimat_zellen.json`, `klimat_stadtteile_odbl.json` (Klima), `denkmale.json`, `denkmale_bdot.json`,
  `denkmale_odbl.json` (Denkmale). Geändert: `erreichbar.json` und `erreichbar_fuss_odbl.json` lassen
  `^CRS3035RES(100|1000)m` zu, wie `zellen.json`; `gebaeude.json` kennt die Höhenherkunft `lod1` und `lod2`;
  `grundkarte.json` beschreibt die eigenen Kacheln mit Pfaden relativ zur Atlas-Wurzel und dem BDOT10k-Vermerk statt
  basemap.de (KR21).
- **Begründung:** Ohne Vertrag prüft `pruefen/daten.py` eine Datei nicht. Die geänderten Muster sind Obermengen der
  alten, Potsdam bleibt gültig. Die Gegenprobe kopiert `daten/schema/` nicht, Potsdam behält dort seinen
  basemap.de-Vertrag.
- **Verworfen:** eigene Kraków-Schemas neben den alten (zwei Verträge für dieselbe Datei); `erreichbar.js` bis zur
  Entscheidung weglassen; LoD-Höhen als `kataster` beschriften (falsche Herkunft).
- **Neu prüfen, wenn:** Phase Seitenbau andere Zuschnitte braucht oder ein Ort ein anderes Gitter nutzt. Offen bleibt das
  Feld `x-eigentuemer` in `einrichtungen*`, `erreichbar*` und `planer*`, das noch „A6“ (Potsdam) nennt.

## KR16: Fußweg je Zelle ohne Landesfilter, Zellen und Lizenz aus der Datenbank

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends. Herkunft: `docs/entscheidungen/D2.md`.

- **Anlass:** Der Potsdamer Code filterte Ziele über den VBB-Landesfilter, las `public.zensus_zelle` mit einem fest
  eingetippten Zensus-Vermerk und rechnete seine Probe in der gemeinsamen Datenbank.
- **Entscheidung:** Es gibt keinen Landesfilter. Ziele in Nachbargemeinden zählen mit; ob ein Ziel außerhalb liegt,
  wird räumlich bestimmt und je Art gezählt. Die Zelltabelle ist ein Parameter (`--zellen`); den Lizenzvermerk liest
  das Skript aus `COMMENT ON TABLE`, und ohne Tabelle oder Vermerk bricht es ab. Gezählt wird eine Zelle, wenn ihr
  Mittelpunkt in der Rechen-SRID die Vereinigung der dzielnice berührt. Datenbank-Tests laufen nur in einer
  Wegwerf-PostGIS (`pruefen/D2_wegwerf_db.sh`, nicht in `pruefen.sh`). Den OSM-Auszug übernimmt
  `skripte/12_osm.sh laden --uebernehmen` per Kopie aus `eingang/` nach `osm/<stand>/`. Solange
  `config/richtwerte.yaml` keine Gehgeschwindigkeit, keinen Grün-Radius und keine Grünarten nennt, gelten sichtbar
  markierte Standards des Skripts.
- **Begründung:** Im Umland Krakóws gibt es keine Landesgrenze; ein Weg zur Apotheke in Zabierzów ist ein echter Weg.
  Ein eingetippter Vermerk wäre beim ersten Quellwechsel falsch. Ein Schreibzugriff auf fremde Zeilen bleibt einer,
  auch wenn er zurückgerollt wird.
- **Verworfen:** Filter auf die Gemeinde (Randzellen bekämen zu lange Wege); Vermerk als Konstante; Zuordnung je
  Stadtteil mit JOIN (doppelte Zellen auf Grenzen); Tests gegen die gemeinsame Datenbank mit ROLLBACK.
- **Neu prüfen, wenn:** ein Thema nur städtische Angebote meint, die Zelltabelle in `sql/` anders heißt oder echte
  Daten in der gemeinsamen Datenbank liegen (dann zusätzlich `14b_fussweg.sh pruefen` dort, nur lesend).

## KR17: Bevölkerung aus dem Eurostat-Gitter und dem NSP, Mindestfallzahl 100

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends, einschließlich der Gruppenzuordnung (Regel 4, unten). Herkunft: `docs/entscheidungen/D4.md`.

- **Anlass:** Für Stadt, delegatury und dzielnice werden Einwohner, Dichte und Altersanteile gebraucht. Die Geometrie
  der rejony statystyczne fehlt, und die MSIP-Grenzen stehen unter Lizenz-STOPP (KR3).
- **Entscheidung:** Stadt und delegatury aus dem NSP 2021 und dem Eurostat-Gitter 2021 (1 km), dzielnice aus dem
  Gitter in den OSM-Grenzen (KR13). NSP-Werte je dzielnica bleiben `null` mit Grund, bis die rejony vorliegen.
  Altersanteile je Raum und je Zelle gibt es erst ab 100 Personen, sonst `null`; Werte je rejon oder obwód werden nie
  ausgeliefert. MSIP dient nur als Prüfwerkzeug außerhalb des Repos (`--intern-msip`, `--msip-gegenprobe`). Die
  Sperre von Overpass in `skripte/abruf.py` bleibt.
- **Begründung:** Das Eurostat-Gitter liefert dieselben Zählungen wie das GUS-1-km-Gitter, bei klarerer Lizenz.
  Overpass ist seit dem OSM-Handdownload nicht mehr nötig.
- **Verworfen:** andere Overpass-Rechner (gleiche Sperrabsicht, nur ein anderer Weg); MSIP-Ergebnisse im Repo.
- **Neu prüfen, wenn:** die rejony-Geometrie mit geprüfter Lizenz vorliegt oder die Geheimhaltungsregel des GUS
  geprüft ist.
- **Regel 4, Gruppenzuordnung (entschieden am 13.11.2026 abends):** III Prądnik Czerwony und XV Mistrzejowice
  gelten mit 98,53 % bzw. 98,64 % Flächenanteil in der delegatura ihrer Gruppe als zugeordnet. Der Rest ist ein
  Grenzsplitter zwischen den delegatury der BDOT10k und den dzielnice; die Gegenprobe mit den städtischen Grenzen
  (MSIP, nur intern) bestätigt das. `zuordnung_geprueft` = `true` mit Vermerk und Zahlen in `config/krakow.yaml`;
  die Schwelle 99 % bleibt, die Ausnahme gilt nur für genau diese zwei Anteile (`AUSNAHMEN_REGEL4` in
  `skripte/raum_bevoelkerung.py`). Zahlen: `belege/D4_bevoelkerung.md`, Regel 4.

## KR18: Gebäude aus BDOT10k, Höhe aus LoD erst nach bestätigter Lesart

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends, einschließlich der Lesart der LoD-Freigabe (unten). Herkunft: `docs/entscheidungen/D5.md`.

- **Anlass:** Potsdams Gebäudeebene kam aus ALKIS mit Kataster-Höhen. In Kraków gibt es BDOT10k (Funktion,
  Geschosse) und die GUGiK-Modelle LoD1 2024 und LoD2 2017, deren Rechtsgrundlage nur die Geoportal-Seite nennt.
- **Entscheidung:** Jedes Gebäude wird über den inneren Punkt des Grundrisses (`point_on_surface`) genau einer Einheit
  zugeordnet. Duplikat-Vermerke werden gezählt, nicht entfernt. Ohne LoD gilt die Höhe Geschosse × 3 m, sonst 3 m,
  als „geschätzt“ beschriftet. Höhen aus LoD werden erst veröffentlicht, wenn die Lesart bestätigt ist, dass die
  Erklärung des Herausgebers auf der Geoportal-Seite genügt; Quellenangabe nach art. 40c ust. 3. Die Gebäudedateien
  je dzielnica kommen erst ins Repo, wenn die Grenzen echt sind (mit Beispielgrenzen 32,8 MB).
- **Begründung:** Eine anteilige Zuordnung würde Gebäude zerteilen. Welche Fassung eines Duplikats richtig ist, lässt
  sich aus den offenen Daten nicht entscheiden. Bei den LoD-Modellen widersprechen sich die Texte nicht, es fehlt
  aber ein Beleg.
- **Verworfen:** Schwerpunkt statt innerem Punkt (kann außerhalb liegen); ein Krakauer Geschossmaß (kein Beleg);
  STOPP für LoD (der Herausgeber erklärt die freie Nutzung selbst); eine Datei für die ganze Stadt.
- **Lesart entschieden (13.11.2026 abends):** Die Erklärung des Geoportals „Modele 3D budynków są dostępne
  bezpłatnie i możliwe do dowolnego wykorzystania.“ reicht als Grundlage. Die LoD2-Höhen (`lod2_1261_gml.zip` aus
  dem Eingang) werden veröffentlicht, mit diesem Satz wörtlich im Vermerk und dem Stand 2017; die Herkunft der Höhe
  steht je Gebäude im Feld `hq` (`lod2`, `geschosse`, `ersatz`). Die Gebäudedateien je dzielnica beruhen auf den
  OSM-Grenzen und heißen deshalb `gebaeude/<nr>_odbl.js` (KR3, Variante a); sie liegen außerhalb des Repos (KR28).
- **Neu prüfen, wenn:** GUGiK sich anders äußert, LoD1 vorliegt (dann die 3-m-Konvention am Median
  `measuredHeight / LICZ_KONDY` messen) oder amtliche Grenzen der dzielnice mit klarer Lizenz vorliegen.

## KR19: Versorgung und Takt: Haltestellen-Datei und Taktklassen als Orientierung

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends. Herkunft: `docs/entscheidungen/D6.md`.

- **Anlass:** Die Themenentscheidung nach der Machbarkeitsprobe verlangt Taktklassen wie in Potsdam. Deren Grenzen stammen aus dem Potsdamer
  Nahverkehrsplan, nicht aus einer polnischen Quelle.
- **Entscheidung:** Es gibt eine neue Datei `daten/haltestellen.js` (`KIEZ_HALTESTELLEN`, GTFS der ZTP, CC BY 4.0)
  mit Taktklasse und `klassen.status`. Die Grenzen sind 6, 2 und 1 Abfahrten je Stunde und Richtung, werktags
  06–09 Uhr, Stichtag Mittwoch 18.11.2026; der Status ist „orientierung“, ohne Abzeichen „standard urzędowy“.
  Haltestellen, Einrichtungen und Parks bekommen `st` über die Zelle aus `daten/zellen.js` (vorbehaltlich KR13). Die
  Kraków-Skripte heißen `*_krakow.py`; die Potsdamer Fassungen bleiben für die Gegenprobe unverändert.
- **Begründung:** Eine Datei dient Karte und Planer zugleich, und der Status steht an den Daten. Die Einteilung bleibt
  mit Potsdam vergleichbar und ist ehrlich gekennzeichnet.
- **Verworfen:** Haltestellen als `art` in `einrichtungen.js` (der Vertrag hat keine Felder dafür); eigene Krakauer
  Grenzen aus der Verteilung der Abfahrten (wären ausgedacht).
- **Neu prüfen, wenn:** der Krakauer Plan transportowy gelesen ist oder die Folgefrage zu KR3 entschieden ist.

## KR20: Luft aus der EEA-Jahresstatistik per Handdownload, Abzeichen „orientacyjnie“

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends, einschließlich der Lizenz-Lesart (unten). Herkunft: `docs/entscheidungen/D7.md`.

- **Anlass:** Die GIOŚ-Rechner sind nach der robots-Regel gesperrt oder waren nicht erreichbar; die Lizenz der
  GIOŚ-Daten ist damit nicht lesbar. Die EEA veröffentlicht dieselben Messungen mit eigener Lizenzzeile CC BY 4.0.
- **Entscheidung:** Hauptquelle ist die EEA-Tabelle „Annual AQ statistics“ als CSV-Handdownload nach
  `eingang/eea/`. Das GIOŚ-Archiv dient nur als interne Gegenprobe, bis seine Lizenz wörtlich belegt ist. Das
  Abzeichen auf der Seite ist „orientacyjnie“, weil die Jahreskennwerte von der EEA stammen und keine amtliche
  Bewertung der GIOŚ sind. Bis zum Handdownload stehen Beispieldaten (`fixture: true`) im Repo; echt sind nur die
  Grenzwerte (Dz.U. 2021 poz. 845) und das Zitat der Uchwała XVIII/243/16.
- **Begründung:** Das ist die einzige Quelle mit belegter Lizenz und Jahresreihen ab 2010.
- **Verworfen:** die GIOŚ-API (gesperrt); Discodata und die ArcGIS-Dienste der EEA (unbekannte Tabelle oder
  robots-Sperre); ein automatischer POST an den Betrachter (`abruf.py` kann nur GET, und der einzige Netzweg wird
  nicht erweitert).
- **Lizenz-Lesart entschieden (13.11.2026 abends):** Die EEA-Luftdaten gelten als CC BY 4.0 mit der Nennung
  „EEA; Daten: GIOŚ“. Bis die EEA-CSV per Handdownload vorliegt, bleibt `daten/powietrze.js` Beispieldatei.
- **Neu prüfen, wenn:** die GIOŚ-Nutzungsbedingungen wörtlich vorliegen oder die EEA die Lizenzzeile des Datensatzes
  ändert.

## KR21: Grundkarte aus eigenen Vektorkacheln, nur BDOT10k

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends. Herkunft: `docs/entscheidungen/D8.md`.

- **Anlass:** Für Kraków gibt es kein basemap.de. Der WMTS des GUGiK liefert nur EPSG:2180, und das Abgreifen ganzer
  Kachelsätze ist verboten (KR11).
- **Entscheidung:** Nur BDOT10k 1261, ohne OSM. Ein eigener Kodierer in Python (`skripte/27_grundkarte.py`, nur Pakete
  aus `requirements.txt`) schreibt einen Kachelordner `{z}/{x}/{y}.pbf` für z9 bis z14, darüber wird hochgezoomt. Die
  Kartenschrift ist Noto Sans (OFL 1.1), weil Barlow 16 der 18 polnischen Sonderzeichen fehlen. Kacheln und Schrift
  liegen außerhalb des Repos unter `kiezatlas-daten/krakow/abgeleitet/grundkarte/<SHA-Anfang>/`; das Deploy kopiert
  sie nach `daten/grundkarte/`. `daten/grundkarte.js` nennt die Pfade relativ zur Atlas-Wurzel (Vertrag KR15).
- **Begründung:** BDOT10k braucht keine Lizenz, nur eine Quellenangabe. OSM in den Kacheln würde jede Seite mit Karte
  zur ODbL-Datei machen. Tippecanoe, planetiler und GDAL sind nicht installiert und nicht mit Hash beziehbar. Der
  Ordner geht mit jedem statischen Server.
- **Verworfen:** OSM als Haupt- oder Zusatzquelle; PMTiles oder MBTiles; Kacheln im Repo (7 MB Binärdaten je
  BDOT-Stand); Barlow als Kartenschrift.
- **Neu prüfen, wenn:** die Karte über Powiat 1261 hinaus gefüllt werden soll (zuerst BDOT10k 1206 und 1219), GDAL
  oder tippecanoe mit fester Version bereitstehen oder die Seitenpakete die Karte einbinden. Offen bleiben die
  Auflösung relativer URLs in `themen.js` (ohne sie zeigt keine Atlas-Seite die Grundkarte) und der Eintrag
  `karte.grundkarte` in `config/krakow.yaml`; beides gehört zu Phase Seitenbau.

## KR22: Wohnungsmarkt nur aggregiert, Mindestfallzahl 10, nur Handdownload

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends: Die Mindestfallzahl 10 bleibt; der RCN-Handdownload fehlt noch, `daten/mieszkania.js` bleibt bis dahin
Beispieldatei. Herkunft: `docs/entscheidungen/DW.md`.

- **Anlass:** Der Rejestr cen nieruchomości (RCN) ist seit dem 13.02.2026 kostenfrei. Einzelkäufe lassen sich aber
  über Grundbuch und Adresse einer Person zuordnen. Der WFS ist nach der robots-Regel gesperrt.
- **Entscheidung:** Es gibt keinen Lizenz-STOPP: Nach art. 40c ust. 5 PGiK wird keine Lizenz erteilt, Pflicht ist nur
  die Quellenangabe (art. 40c ust. 3, gleichlautend Regulamin geoportal.gov.pl § 3). Transaktionen kommen nur aus dem
  GeoPackage-Handdownload nach `eingang/rcn/`. Veröffentlicht wird der Median ab 10 Käufen je dzielnica, Jahr und
  Markt, mit Fallzahl n. Es gibt kein Minimum, kein Maximum, kein Perzentil, keinen Mittelwert und keine Zeile je
  Kauf im Repo.
- **Begründung:** Gesetz und Portalbedingungen widersprechen sich nicht. Extremwerte sind immer ein einzelner Kauf.
- **Verworfen:** der WFS über einen anderen Pfad (Umweg um die Sperre); Mittelwert (empfindlich gegen Ausreißer); eine
  feinere Raumeinheit als die dzielnica.
- **Neu prüfen, wenn:** das GeoPackage eigene Lizenzangaben trägt, art. 40a/40c geändert wird oder eine Rechtsprüfung
  eine andere Grenze verlangt. Die Einstufung als personenbezogen und die Grenze 10 sind rechtlich nicht geprüft.

## KR23: Klima: Bebauung und Verkehr als Näherung für Versiegelung, Acker ist kein Grün

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends. Herkunft: `docs/entscheidungen/dk.md`.

- **Anlass:** Eine gemessene Versiegelung liegt für Kraków nicht frei und geprüft vor, die BDOT10k-Bodenbedeckung
  schon.
- **Entscheidung:** `bebauung_verkehr` = `PTZB` + `PTKM` + `PTPL` als Anteil der Klassenflächen, immer mit Abzeichen
  „orientacyjnie“ und nie als Messung bezeichnet. Acker (`PTTR`, uprawa na gruntach ornych) ist eine eigene Klasse
  und zählt nicht als Grün; Kleingärten zählen. Grün je Einwohner = Grün + Wald, nur ab 1 000 Einwohnern und nicht je
  Zelle. Werte je dzielnica stehen nur in `klimat_stadtteile_odbl.js` (KR13). Hitze ist nur als Grenze benannt. Mit
  echten Grenzen ist jede dzielnica unter 10 ha in der Stadt ein Befund.
- **Begründung:** Die Richtung des Fehlers ist bekannt (eher zu hoch), seine Größe nicht gemessen; der Beleg nennt den
  bewachsenen Teil von `PTZB`. Acker ist nicht allgemein zugänglich.
- **Verworfen:** Copernicus Imperviousness (Lizenz und Bezugsweg nicht geprüft); Bebauung ohne Verkehr (systematisch
  zu niedrig); Grün je Einwohner je Zelle.
- **Neu prüfen, wenn:** eine gemessene Versiegelung oder eine Oberflächentemperatur mit wörtlich belegter offener
  Lizenz vorliegt.

## KR24: Denkmale als Teilmenge, nur Bauzeitklassen, Wikidata und OSM nur aus dem Eingang

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends, mit geänderter Sperrliste (unten). Herkunft: `docs/entscheidungen/DZ.md`.

- **Anlass:** Kamienice und Denkmale sollen ohne Bauzeiten-Kaskade (KR4) auskommen. Der Paketauftrag nannte WDQS und
  Overpass als zulässig, `skripte/abruf.py` sperrt beide.
- **Entscheidung:** „Kamienica“ heißt im Atlas: ein Mehrfamilienhaus laut BDOT10k mit Denkmalbezug (ein Treffer aus
  dem Register oder einer OSM-Denkmalangabe im Umriss oder bis 10 m). Ein Gebäudename „Kamienica …“ zählt getrennt als
  Namensbezug. Es gibt nur Bauzeitklassen, nie Einzeljahre. `teilmenge: true` und `flaechenaussage: false` erzwingen
  die Verträge. Wikidata und OSM liest das Skript nur aus `eingang/`; die Sperrliste bleibt. Die Ortsmarke
  ul. Kościuszki 18 bekommt eine Lage nur aus einer Quelle, die die Adresse trägt, immer mit
  `lage_geprueft: false`. Der Name des Ausgangsprojekts erscheint nicht, solange es keine öffentliche Quelle gibt.
- **Begründung:** Die Sperrliste ist eine bewusste Entscheidung aus der Machbarkeitsprobe, und eine Ausnahme im Paket
  würde den einzigen Netzweg umgehen. Einzeljahre wären eine Scheingenauigkeit.
- **Verworfen:** BDOT10k-Komplexe `OT_KUZA_A` als Denkmalflächen zählen (Topographie, kein Register); die Begriffe im
  Namensraum `kamienice.*`; Geokodierung oder Koordinaten aus dem Gedächtnis.
- **Sperrliste, entschieden am 13.11.2026 abends:** WDQS (query.wikidata.org) ist erlaubt für höchstens wenige
  Abfragen mit der Kennung des Abrufskripts (Wikidata CC0, Nutzungsregeln des WDQS beachten). Overpass bleibt
  gesperrt; OSM kommt aus dem Handdownload. Gemessen am selben Abend: Die `robots.txt` von query.wikidata.org sperrt
  `/sparql` und `/bigdata` für alle Programme (Probe über `skripte/abruf.py`, Befund unter
  `kiezatlas-daten/krakow/_robots/2026-11-13/`; es ging keine SPARQL-Anfrage hinaus). Die Freigabe der Projektleitung
  hebt robots.txt nicht auf; `skripte/abruf.py` bleibt unverändert, Wikidata bleibt ein Handdownload (Abfrage in
  `quellen-DZ.md`).
- **Neu prüfen, wenn:** Lizenzen und Fundstellen für das NID-Register und die gminna ewidencja vorliegen, die
  `robots.txt` des WDQS die Abfrage erlaubt oder die Integration `abruf.py` ändert.

## KR25: Ein gemeinsamer Ort für den OSM-Auszug

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends.

- **Anlass:** Mehrere Pakete lesen denselben OSM-Auszug (Małopolska, Handdownload). Getrennte Kopien in Paketordnern
  können auseinanderlaufen, ohne dass es jemand merkt.
- **Entscheidung:** Quelle ist `kiezatlas-daten/krakow/eingang/` (heute `malopolskie-261112.osm.pbf`, Prüfsumme in
  `eingang/SHA256SUMS`). Kopien, etwa nach `osm/<stand>/` durch `skripte/12_osm.sh laden --uebernehmen`, gibt es nur
  mit Prüfsumme, die gegen den Eingang stimmt.
- **Begründung:** Ein Ort und eine Prüfsumme genügen, um jeden Lauf auf denselben Auszug zurückzuführen.
- **Verworfen:** Kopien je Paket ohne Prüfsumme; ein neuer Abruf über Overpass (gesperrt, KR17, KR24).
- **Neu prüfen, wenn:** ein neuer Auszug abgelegt wird (dann neuer Stand nach `docs/rundgang.md`, „Neuer
  Datenstand“).

## KR26: Schriften der Seiten mit allen polnischen Sonderzeichen

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends (Vorgabe); die Umsetzung ist ein Vorschlag des Pakets Schrift und Grundkarte, von der Integration
übernommen (KR30).

- **Anlass:** Die Schriftdateien unter `fonts/` waren die Fontsource-Teilmenge `latin`; 16 der 18 polnischen
  Sonderzeichen fehlten, der Browser setzte sie aus einer Ersatzschrift.
- **Entscheidung:** Jede Schrift des Atlas muss alle polnischen Sonderzeichen haben: ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś
  Ź Ż. Geprüft wird das an der Zeichentabelle jeder Schriftdatei (`pruefen/DF_schriften.py` in `pruefen.sh`).
- **Begründung:** Polnisch ist die Standardsprache des Atlas; Ersatzglyphen aus einer anderen Schrift sehen fremd aus
  und verschieben Laufweiten.
- **Verworfen:** nicht angegeben (Vorgabe der Projektleitung ohne festgehaltene Alternative).
- **Neu prüfen, wenn:** eine weitere Sprache mit anderen Sonderzeichen dazukommt.

## KR27: Neues Thema „Sanierungsatlas Wohnungsbestand“

Stand: bestätigt durch die Projektleitung am 13.11.2026 abends (Thema); Umsetzung und Datenschutzgrenze sind Vorschläge des Pakets, von der Integration übernommen
(KR31).

- **Anlass:** Gesucht waren Daten, an denen Forschende zur Sanierung des Wohnungsbestands ihr eigenes Feld erkennen.
  Gefunden wurde die Gebäudeliste des ZBK („Wykaz budynków i obiektów w zarządzie ZBK“, BIP Kraków) und eine
  Typologie-Schätzung für Plattenbauten aus BDOT10k.
- **Entscheidung:** Eigene Themenseite mit Datennachlauf: ZBK-Leser, Verortung über Adressen, Typologie-Kandidaten
  aus BDOT10k. Grenzen offen: keine Baujahre, keine Energiewerte, die Typologie ist eine Schätzung.
- **Begründung:** Die Liste ist der kommunale Bestand, auf den Sanierungsprogramme zielen; sie ist öffentlich.
- **Verworfen:** Energiewerte oder Baujahre aus nicht offenen Registern (CEEB, EGiB; KR4).
- **Neu prüfen, wenn:** Baujahre oder Energiekennwerte mit klarer Lizenz vorliegen.

## KR28: Echtlauf mit OSM-Grenzen: `_odbl`-Namen, `st` nur in `_odbl`-Dateien, 3D außerhalb des Repos

Stand: bestätigt (14.11.); Ablage der 3D-Dateien außerhalb des Repos, Auslieferung über Entwicklungsserver und Deploy nach KR42. Herkunft:
`docs/entscheidungen/DE.md` (DE1, DE3, DE7).

- **Anlass:** Nach Variante (a) werden Werte, die auf den OSM-Grenzen beruhen, als `_odbl`-Dateien ausgeliefert, und
  `pruefen/daten.py` erlaubt den ODbL-Vermerk nur in Dateien mit `_odbl` im Namen.
- **Entscheidung:** Umbenannt mit Vertragsänderung: `zellen.js` → `zellen_odbl.js`, `kennzahlen.js/.json` →
  `kennzahlen_odbl.js/.json`, `planer.js` → `planer_odbl.js` (Verträge mit `x-odbl: true`); die globalen Namen
  bleiben (`KIEZ_ZELLEN`, `KIEZ_KENNZAHLEN`, `KIEZ_PLANER`). `haltestellen.js` und `einrichtungen.js` tragen kein
  `st`; die Seite holt es über `zellen_odbl.js`. `erreichbar.js` und `klimat.js` bleiben ohne `_odbl`, weil die 327
  Zellen geprüft genau die Zellen mit Mittelpunkt in der BDOT10k-Stadtgrenze sind (327/327, `belege/D4_bevoelkerung.md`).
  Die Gebäudedateien für 3D heißen mit echten Grenzen `gebaeude/<nr>_odbl.js` (Vertrag `gebaeude_odbl.json`) und
  liegen außerhalb des Repos unter `kiezatlas-daten/krakow/abgeleitet/gebaeude/2026-11-13-odbl/` (zusammen
  32.484.980 B, gzip 5.702.953 B; der ältere Ordner `2026-11-13/` ist als ersetzt markiert).
- **Begründung:** Die Dateigrenze der ODbL bleibt technisch geprüft; Dateien aus BDOT10k, GTFS und Eurostat bleiben
  frei von der Share-Alike-Pflicht. Die 3D-Dateien würden das Repo um mehr als 30 MB vergrößern.
- **Verworfen:** Namen behalten und die Prüfung lockern; `st` in `haltestellen.js` (die ganze Haltestellenliste stünde
  unter Share-Alike); die 3D-Dateien ins Repo.
- **Offen:** Ablage und Auslieferung der 3D-Dateien (Repo oder wie die Grundkarte über das Deploy). Die Module
  `planer.js`, `atlas.js` und `karte.js` laden noch die alten Namen (`daten/zellen.js`, `daten/gebaeude/<nr>.js`), die
  die Gegenprobe Potsdam braucht; beim Einbau in die Krakauer Seiten den Namen aus der Ortskonfiguration lesen.
  `skripte/16_export.py` liest weiter `zellen.js`.
- **Neu prüfen, wenn:** amtliche Grenzen mit klarer Lizenz vorliegen (dann zurück zu Namen ohne `_odbl`).

## KR29: Fußweg-Ziele und Gliederung in der Datenbank, `sql/003_zellen.sql`

Stand: bestätigt (14.11.), einschließlich der nachträglichen Ausnahme für `public.stadtteil` und `public.zensus_zelle`. Herkunft: `docs/entscheidungen/DE.md` (DE4, DE8).

- **Anlass:** `skripte/14b_fussweg.py` liest Ziele aus `auswertung.einrichtung`, `gruenflaeche` und `haltestelle`; die
  Krakauer Skripte der Versorgung schrieben nur Dateien, und für die beiden Fußweg-Dateien gab es kein Krakauer
  Skript. Für `public.stadtteil` und `public.zensus_zelle` gibt es keine Quelle der Pipeline.
- **Entscheidung:** `skripte/14a_ziele_db_krakow.py` schreibt die Ziele (Rolle `kiezatlas_rechnen`),
  `skripte/14c_fussweg_export_krakow.py` schreibt `erreichbar_fuss_odbl.js` und `planer_fuss_odbl.js`;
  beide gehören zum Paket Versorgung und Takt. `sql/003_zellen.sql` legt `public.zensus_zelle` mit
  `COMMENT ON TABLE` an; `skripte/05_db_gliederung.py` füllt `public.stadtteil` und `public.zensus_zelle` als `admin`.
  Beide gehören der Integration. Solange `config/richtwerte.yaml` keine Gehgeschwindigkeit, keinen Grün-Radius und
  keine Grünarten nennt, gelten sichtbar markierte Standards des Skripts.
- **Begründung:** So rechnet der Fußweg auf denselben Zielen wie die Luftlinie, und der Lizenzvermerk der Zellen
  kommt aus der Tabelle selbst (KR16).
- **Verworfen:** Ziele erneut aus OSM in der Datenbank zusammenstellen, getrennt von `einrichtungen.js`.
- **Offen:** Das Paket hat `sql/003_zellen.sql` selbst als `admin` in die gemeinsame Datenbank eingespielt und
  `public.*` beschrieben; nach den Bauregeln schreibt DDL nur die Integration und `public.*` nur die Pipeline. Die
  Integration übernimmt die Datei nachträglich; die Ausnahme für `public.stadtteil` und `public.zensus_zelle` hat die
  Projektleitung am 14.11.2026 nachträglich bestätigt.
- **Neu prüfen, wenn:** die Pipeline eine Quelle für Grenzen oder Gitter bekommt oder `config/richtwerte.yaml` die
  Fußweg-Werte nennt.

## KR30: Schriften: Barlow mit `latin` und `latin-ext` je Schnitt zusammengefügt

Stand: bestätigt (14.11.) mit Auflage: Die Kerning-Paare der polnischen Zeichen werden aus den Grundbuchstaben übertragen (Ą←A, Ć←C, Ę←E, Ł←L, Ń←N, Ó←O, Ś←S, Ź/Ż←Z, klein ebenso), per fontTools in `skripte/schriften.py`, byte-reproduzierbar; `pruefen/DF_kerning.py` muss die Lücke als geschlossen messen. GitHub bleibt gesperrt. Herkunft: `docs/entscheidungen/DF.md`. Erfüllt die Vorgabe KR26.

- **Anlass:** Den Schriften unter `fonts/` fehlten 16 der 18 polnischen Sonderzeichen (KR26).
- **Entscheidung:** Barlow und Barlow Semi Condensed aus den npm-Paketen `@fontsource/barlow` und
  `@fontsource/barlow-semi-condensed` 5.3.0 (OFL 1.1), abgerufen über `skripte/abruf.py` und gegen SHA256 und die
  Integrität der Registry geprüft. Je Schnitt fügt `skripte/schriften.py` die Teilmengen `latin` und `latin-ext` mit
  `fontTools.merge` unter dem bisherigen Dateinamen zusammen (byte-reproduzierbar, `--pruefen`). fontTools und brotli
  stehen mit Hashes in `requirements-schriften.txt`.
- **Begründung:** Gleiche Dateinamen und eine Datei je Schnitt; `atlas.css`, `schaugrafik.js` und
  `skripte/16_export.py` bleiben unverändert. Die Glyphen sind die der Autoren, nur die Teilmengen sind vereint.
- **Verworfen:** zweites `@font-face` mit `unicode-range` (Änderungen in fremden Dateien, zwei Abrufe je Schnitt);
  Noto Sans für die Oberfläche (Bruch mit `DESIGN.md`); Barlow aus GitHub (dort gesperrt); `npm install` (Netz
  außerhalb des Abrufwerkzeugs).
- **Offen:** Kerning über die Teilmengen hinweg fehlt (gemessen mit `pruefen/DF_kerning.py`: von 1.664 Paaren je
  Schnitt hat keines einen Wert, bei 61 bis 103 Paaren kernt der Grundbuchstabe um mindestens 20 Einheiten); sichtbar
  in großen Versalien wie „WĄWÓZ“. Ausweg wäre Barlow vollständig aus der Quelle der Autoren (GitHub freigeben) oder
  übertragene Kerning-Klassen (typografische Entscheidung).
- **Integration 14.11.2026:** `pruefen/DF_kerning.py` ist eine Prüfung (Rückgabe 1, sobald ein polnisches Paar ohne
  den Wert seines Grundpaars bleibt) und läuft in `pruefen.sh` ohne Browser; am Stand 0 verlorene Paare in allen
  fünf Schriften (`docs/entscheidungen/review-20261114.md`, Nr. 2). Datei des Pakets Schrift und Grundkarte, von der
  Integration geändert.
- **Neu prüfen, wenn:** Fontsource eine Datei mit beiden Teilmengen anbietet oder GitHub als Quelle freigegeben ist.

## KR31: Sanierungsatlas: Weiterverwendung, Datenschutz, Verortung und Typologie

Stand: bestätigt (14.11.) mit Auflagen: Private Einträge werden nur gezählt, ohne Vergröberung. Punkte gibt es auch bei öffentlichem Eigentum nur an Gebäuden mit mindestens 3 Geschossen laut BDOT10k, kleinere werden nur gezählt. KR24 bleibt: kein Projektname an der Ortsmarke. Herkunft: `docs/entscheidungen/DS.md`; Regeln vorab in `pruefen/DS_protokoll.md` (mit Nachträgen 1 bis
3); Zählungen in `belege/DS_sanierung_lauf.md`. Das Thema selbst ist bestätigt (KR27).

- **Anlass:** Die ZBK-Liste ist eine Adressliste mit Eigentumsangaben, auch von Privatpersonen; BDOT10k 1261 hat keine
  Adressen.
- **Entscheidung:** Die Liste wird nach den Regeln der Gmina Miejska Kraków zur Weiterverwendung genutzt (für jeden
  Zweck, mit Quelle, Erstellungs- und Abrufzeit, Hinweis auf Verarbeitung und Haftungsklausel; wörtlich in
  `quellen-DS.md`). In `daten/` stehen keine Adresse, keine laufende Nummer und keine Gebäudekennung. Punkte gibt es
  nur für Einträge in öffentlichem Eigentum (Gemeinde, Staat, gemischt öffentlich) ohne samoistne posiadanie, nicht an
  Einfamilienhäusern laut BDOT10k und nicht für Wohnnutzung ohne Gebäude bekannter Funktion; alles andere nur als
  Zählung je dzielnica. Verortet wird über OSM-Adressen, deshalb steht alles Verortete nur in
  `daten/sanierung_odbl.js`; `daten/sanierung.js` enthält nur Zählungen aus der Liste und die Typologie aus BDOT10k je
  delegatura. Die Typologie (Mehrfamilienhaus, mindestens 4 Geschosse, mindestens 250 m², Rechteckigkeit ≥ 0,85;
  Großsiedlung mit mindestens 9 solchen Blöcken im Umkreis von 150 m) ist eine Schätzung; die Verträge erzwingen
  `schaetzung: true` und `baujahr: false`.
- **Begründung:** Ein Punkt an einem Haus mit privatem Anteil verbindet eine Adresse mit dem Eigentum einer Person; ein
  Punkt an einem Einfamilienhaus der Gemeinde sagt etwas über einen bestimmten Haushalt. Die Liste steht zwar im BIP,
  aber nicht in einem Kartenzusammenhang.
- **Verworfen:** alle Punkte (Personenbezug); gar keine Punkte (die Karte des Bestands ist der Kern des Themas);
  OSM-Merkmale in der Typologie (machten die Datei ohne Nutzen zur ODbL-Datei).
- **Offen:** ob private Einträge vergröbert gezeigt werden dürfen und ob kleine Mehrfamilienhäuser dieselbe Regel
  brauchen; die Sichtprüfung der Typologie-Stichprobe; PRG-Adresspunkte als Weg aus der ODbL; die Fassung der Liste vom
  01.05.2026 mit Verwalter und Registernummer (im BIP nicht gefunden); der Denkmalstatus (braucht das NID-Register).
  Der Vorschlag, den Projektnamen der Ortsmarke ul. Kościuszki 18 zu nennen, weil die Projektseite das Gebäude
  öffentlich als Demonstrator führt, ändert KR24 und ist **nicht übernommen**; bis zur Bestätigung gilt KR24.
- **Behebung 14.11.2026** (`docs/entscheidungen/fix-daten.md` 2.3, 2.4, 2.8): Die Ortsmarke trägt kein Feld
  `quelle` mehr (KR24, `skripte/oeffentlich_pruefen.py` meldet den Projektnamen in auslieferbaren Dateien). Die
  Typologie weist angebaute Kandidaten (gemeinsame Grenze ≥ 3 m mit einem anderen BDOT10k-Gebäude) gesondert aus;
  die Regel selbst bleibt (Nachtrag 5 in `pruefen/DS_protokoll.md`). Die Sichtprüfung der Stichprobe ist als
  Eingabe `belege/DS_sichtpruefung.json` eingetragen; Quote und Wilson-Intervall rechnet der Erzeuger. Vorschlag,
  offen: „angebaut“ als Ausschlussregel erst nach einer nach dzielnica geschichteten Stichprobe.
- **Neu prüfen, wenn:** eine Rechtsprüfung die Datenschutzgrenze anders zieht, Baujahre mit klarer Lizenz vorliegen
  oder die Stichprobe geprüft ist.

## KR32: Grundkarte auf den Seiten

Stand: bestätigt (14.11.), einschließlich der Kopie der Kacheln in `skripte/deploy_kopie.py`.
Herkunft: `docs/entscheidungen/DF.md`. Erledigt damit die offenen Punkte aus KR21.

- **Anlass:** MapLibre 4.7.1 lädt Kacheln im Worker und kann relative URLs nicht auflösen; ohne Auflösung zeigte keine
  Seite die eigene Grundkarte. Mit `karte.luftbild: null` lehnte MapLibre den Stil ab.
- **Entscheidung:** `themen.js` bezieht relative Kachel- und Schriftpfade auf den Ordner über `daten/` des tatsächlich
  geladenen `daten/grundkarte.js` (auch mit `?v=`); absolute URLs bleiben. Unter file:// entfällt eine Grundkarte mit
  relativen Pfaden still. Eine Quelle `null` wird entfernt, ihre Ebenen werden unsichtbare Platzhalter; der
  Luftbild-Schalter tut ohne Luftbild nichts (`KIEZ_THEMEN.LUFTBILD`). `config/krakow.yaml` nennt `karte.grundkarte`.
  Jede Seite mit Karte lädt `daten/grundkarte.js` vor `themen.js`. Kacheln und Kartenschrift liefert in der
  Entwicklung `skripte/entwicklung_server.mjs`, im Deploy kopiert `skripte/deploy_kopie.py` sie nach
  `daten/grundkarte/` und prüft sie gegen `MANIFEST.sha256`. Die Seite `karta` zeigt die Karte über `kartenfeld.js`.
  `skripte/30_seiten.py` kennt dafür die optionalen Kopfzeilen `css:` und `skripte:`.
- **Begründung:** Daten bleiben sprachneutral und ohne Rechnernamen; die Gegenprobe Potsdam ändert sich nicht.
- **Verworfen:** `location.href` als Basis (falsch in `en/` und `de/`); Auflösung in `daten/grundkarte.js` (Code in
  Daten); ein Symlink `daten/grundkarte` im Repo.
- **Offen:** Den Luftbild-Schalter in `karte.js`, `atlas.js` und `jahre.js` mit `KIEZ_THEMEN.LUFTBILD` ausblenden
  (Seitenpakete). Das Startgewicht des Planers mit Karte liegt mit den echten Stadtteilgrenzen gerechnet bei
  298.879 B gz (Grenze der Startseite 300 KB gz; Messung von `pruefen/DF_grundkarte.mjs`).
- **Neu prüfen, wenn:** MapLibre relative URLs selbst auflöst, es ein Luftbild gibt oder das Deploy ohne Zugriff auf
  `kiezatlas-daten` laufen muss.

## KR33: Denkmale aus OSM als ungeprüft gekennzeichnet, Stand aus der Quelle

Stand: bestätigt (14.11.). Herkunft: `docs/entscheidungen/DE.md` (DE5, DE6).

- **Anlass:** Niemand hat die Lage der OSM-Denkmale am Luftbild geprüft; `stand` der Denkmaldateien war das
  BDOT10k-Datum, nicht der Stand der Denkmalquelle.
- **Entscheidung:** `denkmale_odbl.js` trägt `sichtpruefung: {geprueft: false, stichprobe: 20, startwert, hinweis}`
  (neues optionales Feld im Vertrag `denkmale_odbl.json`); die Seite zeigt die Punkte dann als ungeprüft. Der `stand`
  von `denkmale_odbl.js` ist der UTC-Tag des `osmosis_replication_timestamp` im Kopf des Auszugs, der von
  `denkmale.js` der jüngste Abruftag der Registerdateien aus `eingang/HERKUNFT.md`; fehlt die Angabe, bricht
  `skripte/dz_denkmale.py` ab.
- **Begründung:** Ein Stand muss der Stand der Quelle sein, sonst ist er eine falsche Angabe.
- **Verworfen:** Dateizeit oder BDOT10k-Datum als Ersatz.
- **Behebung 14.11.2026** (`docs/entscheidungen/fix-daten.md` 2.5, 2.7): OSM-Relationen (Multipolygone) mit
  `heritage` oder `start_date` werden mitgelesen (heritage 167 → 184, Beleg `belege/DZ_denkmale_lauf.md`); die
  Kennzahl heißt „Mehrfamilienhäuser (BDOT10k) mit Denkmal-Kennzeichnung in OpenStreetMap“. Die Stichprobe zur
  Sichtprüfung zieht nur noch aus Gebäudetreffern mit `heritage` (Nachträge 1 und 2 in `pruefen/DZ_protokoll.md`);
  `sichtpruefung.geprueft` bleibt `false`. Die Kartenebene `zabytki` zeigt nur Objekte mit Denkmalangabe
  (`h === true`), wie kamienice und modernizacja (`docs/entscheidungen/fix-oberflaeche.md`, geprüft in
  `pruefen/S1_seiten.mjs`).
- **Nachtrag 15.11.2026 (zweite Sichtprüfung):** Die Kennzeichnung „ungeprüft“ gilt nur noch, wenn
  `sichtpruefung.geprueft` `false` ist. Die zweite Stichprobe (je 20 Punkte aus Wikidata und OSM, Startwert 20261114)
  ist am 15.11.2026 am Luftbild ausgewertet (`belege/DZ_sichtpruefung.json`, Regel in `pruefen/DZ_protokoll.md`
  Nachtrag 4): Lage auf dem Objekt OSM 16 von 20, Wikidata 17 von 20, mit Wilson-Intervall. `denkmale.js` und
  `denkmale_odbl.js` tragen `geprueft: true` mit den Quoten, die Seiten nennen das Ergebnis der Ebene. Geprüft ist die
  Ebene in einer Stichprobe, nicht der einzelne Punkt (`polozenie_sprawdzone` bleibt 0); die Zuordnung zum Gebäude
  heißt weiter ungeprüft. Ohne die Eingabedatei fallen Daten und Langtexte auf `geprueft: false` und den Hinweis
  „ungeprüft“ zurück (`pruefen/DZ_test_eingang.py`, `pruefen/S4_bloecke.py` Teil 9; DE6 Nachtrag).
- **Neu prüfen, wenn:** die Stichprobe am Luftbild ausgewertet ist (erledigt 15.11.2026, Nachtrag oben); erneut, wenn
  ein neuer OSM-Auszug oder neue Registerdateien die Menge der Punkte ändern.

## KR34: Infrastruktur: Pipeline-Stand, robots.txt, Prüfsummen der Pakete

Stand: bestätigt (14.11.); `berichte/umgebung/` bleibt unversioniert. Herkunft: `docs/entscheidungen/D1.md`; Beleg `belege/D1_infrastruktur.md`.

- **Anlass:** Im Potsdamer Audit war offen, welcher Stand der Geodaten-Import-Pipeline einen Beleg erzeugt hat, und
  robots.txt prüfte niemand automatisch.
- **Entscheidung:** `skripte/lauf.sh` schreibt den Stand der Pipeline fest (`PIPELINE_SOLL`) und bricht bei anderem
  Commit oder lokalen Änderungen ab, außer mit `PIPELINE_ABWEICHUNG=1` beim Aufruf. `lauf.sh einrichten` ruft erst
  `pipeline.einrichten --haerten`, dann `sql/002`. `skripte/abruf.py` nutzt einen robots-Befund höchstens 30 Tage
  und holt sonst robots.txt selbst; Fehlerstatus sperrt, 404 erlaubt.
- **Begründung:** Abbruch statt Warnung, weil ein Lauf mit anderem Stand sonst unbemerkt in Belege gerät.
- **Verworfen:** die Pipeline als Git-Submodul; eine Freigabeliste je Rechner.
- **Offen:** `uv run --with-requirements` prüft die Hashes beim Start aus dem Zwischenspeicher nicht (gemessen); bis
  eine Projektumgebung mit `--require-hashes` angelegt ist (braucht einmal Netz), legen die Hashes nur die Versionen
  fest. `berichte/umgebung/` bleibt unversioniert (in `.gitignore` über `berichte/`; entschieden am 14.11.2026).
- **Neu prüfen, wenn:** die Pipeline einen neuen Tag bekommt oder msip@um.krakow.pl die Lizenz klärt.

## KR35: Deploy: verkleinerte Auslieferung mit esbuild

Stand: bestätigt (14.11.). Herkunft: `docs/entscheidungen/D13.md`; Beleg `belege/D13_messung.md`.

- **Anlass:** Die Auflage aus KR10 verlangt, dass die Auslieferung JavaScript verkleinert und das Startgewicht des
  Planers live unter 320 KB gz bleibt.
- **Entscheidung:** `skripte/deploy_kopie.py` verkleinert das eigene JavaScript (Wurzel und `texte/`) mit esbuild
  0.25.12 ohne Bündeln; `daten/`, `vendor/` und `fonts/` bleiben unverändert. Für den Server
  `gzip_comp_level 9` (nginx, Andre). `package.json` und `package-lock.json` gehören der Integration.
- **Begründung:** Gemessen am umgebauten Planer mit Potsdamer Daten: unverkleinert 323,1 KB gz -9, verkleinert
  316,3 KB.
- **Verworfen:** `daten/` verkleinern (entfernt ODbL- und Quellenvermerke in Kommentaren); vorkomprimierte `.gz`;
  terser.
- **Offen:** `og:image` im Seitenrahmen, sobald ein Vorschaubild existiert; ein Schalter `--deploy` in `pruefen.sh`
  für die Deploy-Probe.
- **Neu prüfen, wenn:** der Krakauer Planer echte Daten lädt (eigene Grenze) oder Andre die nginx-Stufe nicht ändert.

## KR36: Krakauer Seiten mit eigenen Modulen, Potsdamer Module unverändert

Stand: bestätigt (14.11.). Herkunft: `docs/entscheidungen/S1.md` Nr. 1 und 2, `docs/entscheidungen/S2.md` Nr. 1, `docs/entscheidungen/S3.md` Vorschlag A, `docs/entscheidungen/S4.md` S4-1.

- **Anlass:** Die Gegenprobe Potsdam (KR9) kopiert `atlas.js`, `karte.js`, `schaugrafik.js`, `planer.js`, `jahre.js`,
  ihre Stylesheets und `skripte/16_export.py` in die Potsdamer Seiten; `pruefen/texte.py` führt für die Potsdamer
  Lizenzvermerke in diesen Dateien Ausnahmen. Die Seitenpakete der Phase Seitenbau brauchten Kraków-eigene Seiten.
- **Entscheidung:** Die Krakauer Seiten laden eigene Module: `erzaehlung.js` (index), `karta.js` (karta),
  `dzielnica.js`, `vergleich.js` (porownanie), `stadtatlas.css`; `kartenseite.js` und `kartenseite.css` als
  Unterbau der Kartenseiten im Textrahmen (`window.KIEZ_KS`) mit `erreichbarkeit.js` (planer), `kamienice.js`,
  `sanierungsatlas.js` (modernizacja); `themenseite.js`, `themenseite.css` mit `seite_powietrze.js`,
  `seite_mieszkania.js`, `seite_klimat.js`; `skripte/16_export_krakow.py`, `export_pola_krakow.py`,
  `16_bloecke_krakow.py` neben dem Potsdamer Export. `kartenfeld.js` ist seit `Arbeitszweig s1` eine Bibliothek
  (`window.KIEZ_KARTENFELD`) und setzt weiter `window.KIEZ_KARTE`. Die Potsdamer Dateien bleiben byte-gleich. Das
  Seitenmodul der freien Karte hieß im Paket `kartenseite.js`; die Integration hat es in `karta.js` umbenannt, weil
  `Arbeitszweig s2` denselben Namen für den Unterbau nutzt und sich über ihn findet. Eigentum: Eigentümer-Tabelle in
  `docs/rundgang.md`.
- **Begründung:** Die Gegenprobe und die Ausnahmen der Textprüfung bleiben gültig; jedes Paket ändert nur eigene
  Dateien.
- **Verworfen:** `atlas.js`, `karte.js` und `planer.js` für Kraków umschreiben (bricht die Gegenprobe); den Unterbau
  von `Arbeitszweig s2` umbenennen (er sucht seinen eigenen Pfad über den Dateinamen, drei Vorlagen laden ihn).
- **Neu prüfen, wenn:** die Gegenprobe Potsdam entfällt; dann können die Potsdamer Module samt Ausnahmen in
  `pruefen/texte.py` entfallen.

## KR37: Vergleich Kraków–Potsdam nur aus dem Eurostat-Gitter

Stand: bestätigt (14.11.). Herkunft: `docs/entscheidungen/S1.md` Nr. 3; Belege `belege/S1_porownanie.md`, `belege/rohdaten-S1-2026-11-14.sha256`.

- **Anlass:** KR11 erlaubt den Vergleich nur mit Kennzahlen gleicher Definition. Der Potsdamer Atlas rechnet mit dem
  Zensus-100-m-Gitter (unter 18 Jahre, dl-de/by-2-0 mit deutschem Pflichtvermerk), Kraków mit dem 1-km-Gitter
  von Eurostat (unter 15 Jahre).
- **Entscheidung:** Beide Städte aus dem Eurostat Census 2021 population grid (1 km, CC BY 4.0) mit denselben
  Merkmalen und derselben Mittelpunktregel; Potsdam neu gerechnet aus `DE_PD_3035_GPKG.zip` (Abruf über
  `skripte/abruf.py`, Prüfsumme in `belege/rohdaten-S1-2026-11-14.sha256`), Stadtgrenze aus den Potsdamer
  Stadtteilen (dl-de/zero-2-0). `skripte/41_porownanie.py` schreibt `daten/porownanie.js` (`KIEZ_POROWNANIE`,
  Vertrag `daten/schema/porownanie.json`); `--pruefen` rechnet byte-gleich nach und steht in `pruefen.sh`.
- **Begründung:** gleicher Datensatz, gleiche Zellgröße, gleiche Regel; die Nennung „Eurostat“ geht in allen drei
  Sprachen.
- **Verworfen:** die Potsdamer Atlaswerte übernehmen (andere Zellgröße und Altersgrenze, deutscher Pflichtvermerk);
  Vergleiche einzelner Stadtteile (1-km-Zellen zu grob); Gebäude, Bauzeit, Heizung, Taktklassen (andere Quellen
  oder in Kraków gestrichen). Die Seite nennt die weggelassenen Vergleiche mit Grund.
- **Offen:** Die Stichtage beider Gitter sind an der Primärquelle nicht geprüft (`stichtag_geprueft: false`).
- **Neu prüfen, wenn:** Eurostat ein neues Gitter veröffentlicht oder die Stichtage belegt sind.

## KR38: Zahlen in Texten nur als Methode und Eigenname

Stand: bestätigt (14.11.). Herkunft: `docs/entscheidungen/S1.md` Nr. 4, `docs/entscheidungen/S2.md` Nr. 6 (feste Werte), `docs/entscheidungen/S3.md` Vorschlag C.

- **Anlass:** Keine handgetippte Ergebniszahl auf Seite oder Methodentext (Checkliste Punkt 23), auch nicht in
  übersetzten Texten; die Textvorschläge der Datenpakete trugen feste Schwellen und Daten.
- **Entscheidung:** Ergebniszahlen stehen nie in `texte/` oder `vorlagen/`; Antwortsätze sind Vorlagen mit
  Platzhaltern aus den Daten (auch Grenzwerte, Deckungsregeln und Stichtag der Uchwała aus `powietrze.js`). In
  Texten und Code stehen nur Methodenwerte (Klassengrenzen, Entfernungsstufen 300/500/1.000/2.000 m, Anteilsstufen
  10/20/30/40 %, Zellgröße 1 km, Geschosshöhe 3 m, Zoomstufe 14,5 für 3D, Abstand 10 m der Kamienica-Festlegung)
  und Eigennamen mit Jahr. Ausnahme: das Pandemiejahr 2020 im Satz zu anderen Einflüssen auf die Luft, weil
  `pruefen/D7_powietrze.py` es verlangt.
- **Begründung:** Ändert sich ein Datenstand, folgen die Sätze von selbst; die Methodenwerte sind Teil der Methode.
- **Verworfen:** auch Zellgröße und Geschosshöhe als Platzhalter (möglich, aber ohne Gewinn, solange die Methode
  sie festlegt).
- **Neu prüfen, wenn:** das Paket Luft das Pandemiejahr als Feld liefert oder die Methode einen dieser Werte ändert.

## KR39: Startgewicht der Seiten und der Gegenprobe

Stand: bestätigt (14.11.) mit Auflage: Die Startseite kommt unter 300 KB gz über vereinfachte Stadtteilgrenzen für die Übersicht (eigene Datei, Vereinfachung dokumentiert, topologisch sauber); die genauen Grenzen laden nur Steckbrief und Karte bei Bedarf. Herkunft: `docs/entscheidungen/S1.md` Nr. 5, `docs/entscheidungen/S2.md` Nr. 3; Beleg `belege/S1_seiten.md`.

- **Anlass:** Die Bauvorlage setzt 300 KB gz für die Startseite. Gemessen (`belege/S1_seiten.md`, pl, `gzip -9`):
  `index.html` 309.489 B, `karta.html` 310.350 B, `dzielnica.html` 321.601 B; davon MapLibre 210.896 B und die
  Stadtteilgrenzen 50.943 B. In der Gegenprobe Potsdam bringt die Textschicht der Krakauer Vorlage
  (`texte/de/planer.js`) seit `Arbeitszweig s2` neue Schlüssel mit.
- **Entscheidung:** Grenze 300 KB gz für die Startseite bleibt; die Startseite liegt heute darüber, das steht als
  offener Punkt. Karte und Steckbrief laden das Gitter sofort und werden an derselben Grenze nicht gemessen, bis
  vereinfachte Grenzen für die Übersicht vorliegen. In der Gegenprobe wird das Startgewicht mit Textschicht
  hingenommen (die Textschicht wird für Potsdam nie ausgeliefert); maßgeblich bleibt der gemeinsame Code
  (`docs/rundgang.md`, „Ergebnis der Gegenprobe“).
- **Begründung:** MapLibre allein belegt zwei Drittel der Grenze; der nächste Hebel sind vereinfachte Grenzen (Paket
  Gliederung und Bevölkerung) und die Verkleinerung der Auslieferung (KR35).
- **Verworfen:** die Grenze auf 320 KB gz heben; die Gegenprobe mit einer festen Namensraumliste laden (möglich,
  ändert aber die Gegenprobe ohne Not).
- **Umsetzung und Messung (Integration 14.11.2026):** Die Startseite lädt `stadtteile_uebersicht_odbl.js` statt der
  genauen Grenzen (`belege/N1_stadtteile_uebersicht.md`). `pruefen/N1_daten.py` misst nur JavaScript (`gzip -9` je
  Skript der erzeugten pl-Seite): `index.html` 287.089 B gz, unter der Grenze von 307.200 B; mit HTML und Stylesheets
  314.482 B gz, ohne Schriften und Kacheln. Die Auflage „Startseite unter 300 KB gz“ ist damit nur für das
  JavaScript erfüllt; mit Schriften (fünf Barlow-Schnitte auf jeder Seite) und den ersten Kacheln liegt die
  Startseite deutlich darüber (`docs/entscheidungen/review-20261114.md`). Offen zur Entscheidung: Grenze
  ausdrücklich als JavaScript-Startgewicht festhalten oder das Gesamtgewicht bis zur Ruhe messen und begrenzen.
- **Entscheidung der Projektleitung (14.11.2026, nach der Behebung):** Die Grenze 300 KB gz gilt als
  **JavaScript-Startgewicht** der Startseite (`pruefen/N1_daten.py`). Das Gesamtgewicht mit HTML, Stylesheets,
  Schriften und ersten Kacheln wird gemessen und angegeben, aber nicht begrenzt. Begründung: Schriften und Kacheln
  werden zwischengespeichert und von allen Seiten geteilt; eine Gesamtgrenze würde die Schriftwahl (KR30) gegen die
  Ladezeit ausspielen, ohne dass ein Nutzer das spürt. Neu prüfen beim Handy-Test am echten Gerät.
- **Neu prüfen, wenn:** vereinfachte Grenzen vorliegen oder die verkleinerte Auslieferung gemessen ist.

## KR40: Beispieldaten auf den Seiten

Stand: bestätigt (14.11.) mit Auflage: zweite Fassung des Rahmenhinweises für Seiten, die Beispieldaten nur nachladen. Herkunft: `docs/entscheidungen/S1.md` Nr. 6, `docs/entscheidungen/S3.md` Vorschlag D.

- **Anlass:** Luft und Wohnungsmarkt sind Beispieldaten (KR20, KR22). Der Hinweis des Rahmens (`kern.beispieldaten`)
  sagt, die ganze Seite zeige erfundene Werte; auf der Karte sind aber alle Ebenen außer der Luft echt.
- **Entscheidung:** Auf den Themenseiten zusätzlich zum Hinweis des Rahmens ein Kasten mit der fehlenden Quelle und
  dem, was schon echt ist, und eine Marke „PRZYKŁAD / SAMPLE / BEISPIEL“ auf jeder Abbildung und Tabelle mit
  Beispielwerten; die fehlende Quelle heißt „Źródło docelowe“. Bei Beispieldaten der Luft keine Stationskarte. Auf
  der Karte kennzeichnen Auswahl, Legende und Popup die Ebene; der Hinweis oben erscheint erst, wenn die Datei geladen
  ist. Geprüft von `pruefen/S3_themenseiten.mjs` und `pruefen/S1_seiten.mjs`.
- **Begründung:** Erfundene Orte auf echter Grundkarte sähen echt aus; Kennzeichnung an der Stelle, an der der Wert
  steht.
- **Verworfen:** eine eigene Seite für Beispieldaten; die Luft-Ebene auf der Karte weglassen.
- **Offen:** eine zweite Fassung des Rahmenhinweises für Seiten, die Beispieldaten nur nachladen (Paket
  Oberflächen-Texte).
- **Neu prüfen, wenn:** die EEA-CSV und der RCN-Handdownload vorliegen.

## KR41: Seite `modernizacja` und Namensraum `sanierung.*`

Stand: bestätigt (14.11.); Vertragsänderung übernommen am 14.11.2026 (Commit `2c96a56` aus `Arbeitszweig s2`); die Glossarbegriffe stehen als Vorschlag in `docs/glossar-pl.md`. Herkunft: `docs/entscheidungen/S2.md` Nr. 2 und 8; Umsetzung von KR27.

- **Anlass:** KR27 verlangt eine Themenseite „Sanierungsatlas Wohnungsbestand“; neue Seiten und Namensräume sind
  Vertrag der Integration.
- **Entscheidung:** Seite `modernizacja` in `config/krakow.yaml` (`seiten`, nicht in der Kopfnavigation, erreichbar
  über die Themenliste der Startseite), `seiten.modernizacja.*` in `texte/<lang>/seiten.js`, Namensraum `sanierung.*`
  in `daten/schema/texte.md`. Die Beschreibung der Seite `kamienice` nennt die Denkmal-Teilmenge statt des noch
  fehlenden Registers. `texte/<lang>/denkmale.js` liegt mit der Seite `kamienice` unter `texte/` (KR14) und gehört
  dem Seitenpaket. Glossarvorschläge für `docs/glossar-pl.md`: modernizacja (budynków) / retrofit, energetisch
  termomodernizacja, nicht „rewitalizacja“; blok z wielkiej płyty; osiedle bloków; zasób mieszkaniowy.
- **Begründung:** „modernizacja“ trifft die Sanierung einzelner Gebäude; „rewitalizacja“ ist Stadtumbau eines Gebiets.
- **Verworfen:** Unterseite von `kamienice`; `rewitalizacja.html`; Texte im Namensraum `kamienice.*`.
- **Neu prüfen, wenn:** der Lehrstuhl die Glossarbegriffe gegenliest.

## KR42: Gebäude in 3D nur auf Wunsch, Auslieferung über den Server

Stand: bestätigt (14.11.) mit Vorschlag: `skripte/entwicklung_server.mjs` und `skripte/deploy_kopie.py` liefern `daten/gebaeude/` aus `$KIEZ_DATEN/abgeleitet/gebaeude/2026-11-13-odbl/` wie die Grundkarte (mit Manifest); die 3D-Dateien müssen von der Pipeline reproduzierbar sein (Befehl dokumentiert). Herkunft: `docs/entscheidungen/S2.md` Nr. 4.

- **Anlass:** Die 3D-Dateien `gebaeude/<nr>_odbl.js` liegen außerhalb des Repos (KR28).
- **Entscheidung:** Die Kartenseiten laden `daten/gebaeude/<nr>_odbl.js` nur nach dem Knopf „Budynki 3D“ oder mit
  `3d=1` im Link, erst ab Zoom 14,5 und nur für die Stadtteile im Bild (höchstens drei je Bewegung). Fehlt eine Datei,
  sagt die Legende das einmal, ohne erneuten Abruf. Höhenherkunft je Gebäude (LoD2 oder Schätzung aus Geschossen) und
  der wörtliche LoD-Vermerk stehen im Popup. Vorschlag: `skripte/entwicklung_server.mjs` und `skripte/deploy_kopie.py`
  liefern `daten/gebaeude/` aus `$KIEZ_DATEN/abgeleitet/gebaeude/2026-11-13-odbl/` wie die Grundkarte.
- **Begründung:** Die Standardansicht bleibt leicht (keine Gebäudedatei angefragt, geprüft von `pruefen/S2_seiten.mjs`);
  3D ist auf echter Höhe belegt (KR18).
- **Verworfen:** 3D-Dateien ins Repo (Größe); 3D beim Laden.
- **Neu prüfen, wenn:** Deploy und Entwicklungsserver den Ordner einhängen.
- **Abweichung vom Vorschlag, begründet (Nacharbeit 14.11.2026):** Im Ordner `2026-11-13-odbl/` heißt das Manifest
  `SHA256SUMS`, nicht `MANIFEST.sha256`; Format (`sha256sum`) und Inhalt sind die eines Manifests, seine Prüfsumme
  ist in `skripte/deploy_kopie.py` festgeschrieben (`GEB_MANIFEST_SHA256`). Der Ordner bleibt unverändert, weil
  `kiezatlas-daten/` nur gelesen wird und ein neuer Datumsordner mit gleichem Inhalt alle Verweise und die
  festgeschriebene Prüfsumme umstellen müsste, ohne die Daten zu ändern. Ab dem nächsten Stand schreibt
  `skripte/20_bdot10k.py --geometrie` selbst `MANIFEST.sha256` in den neuen Ordner; `--pruefen` vergleicht im alten
  Ordner `SHA256SUMS` byte-gleich mit dem neu gerechneten Manifest. `skripte/deploy_kopie.py` und
  `skripte/entwicklung_server.mjs` lesen `MANIFEST.sha256`, sonst `SHA256SUMS`, und prüfen beide jede Datei gegen
  ihre Prüfsumme; abweichende Dateien liefert der Entwicklungsserver nicht aus (404), `pruefen/N2_auslieferung.mjs`
  meldet sie als Befund.
- **Integration 14.11.2026:** Die Behebungen Daten und offen schlugen zwei Namen für das Manifest neuer Läufe vor
  (`SHA256SUMS` bzw. `MANIFEST.sha256`). Übernommen ist der Wortlaut der Entscheidung vom 14.11.2026: neue Läufe schreiben
  `MANIFEST.sha256` (`docs/entscheidungen/fix-daten.md` 2.6 ist in diesem Punkt überholt). Stand und Prüfsumme des
  Manifests stehen an einer Stelle, `config/gebaeude_3d.json`; ohne Manifest im genannten Ordner gilt der jüngste
  `*-odbl/` mit Manifest, die Deploy-Kopie verlangt auch dann die festgeschriebene Prüfsumme. Der Entwicklungsserver
  liefert nur die Freigabeliste der Deploy-Kopie aus und nimmt nur den Host-Kopf `127.0.0.1:<port>` oder
  `localhost:<port>` an. `skripte/20_bdot10k.py --pruefen --geometrie` ist am Integrationsstand byte-gleich.

## KR43: Inhalt der Karten- und Themenseiten

Stand: bestätigt (14.11.) mit Auflagen: Bei echten RCN-Daten wird eine Fallzahl unter 10 ohne Wert angezeigt („n < 10“), nie die Zahl. Ein gemeinsamer Punkt für ul. Kościuszki 18 aus einer Quelle, in allen Dateien gleich, mit begründeter Wahl. Datenpakete liefern Felder (`radius_m` u. a.) statt deutscher Sätze. `mieszkania.js` heißt jetzt `mieszkania_odbl.js`; `pruefen/DW_mieszkania.py` liest `texte/`, `docs/entscheidungen/DW-texte/` entfällt. Änderung an `texte/<lang>/seiten.js` (Commit `f91fa37` aus `Arbeitszweig s3`) übernommen. Herkunft: `docs/entscheidungen/S2.md` Nr. 5 und 6, `docs/entscheidungen/S3.md` Vorschläge B, E, F, G.

- **Anlass:** Die Seitenpakete haben ohne Rückfrage jeweils die vorsichtigere Variante gewählt; das Review vom
  14.11.2026 fand in den Seitentexten von Klima und Luft Versprechen, die die Seite nicht hält.
- **Entscheidung:**
  - Erreichbarkeit: Fußweg ist Standard, Luftlinie ein Schalter; alle Kennzahlen „orientacyjnie“ (KR19); bei Schule,
    Kindergarten und Krippe nennt die Legende die Lücken der BDOT10k.
  - Kamienice: Standard sind die OSM-Objekte mit Denkmalangabe (ungeprüft, KR33); `daten/denkmale.js` (Beispiel) wird
    nicht geladen, Register, gminna ewidencja und Wikidata stehen als „brak“.
  - Wohnungsbestand: Punkte nur aus `sanierung_odbl.js` (öffentliches Eigentum, KR31), Stadtteilfarbe als Anteil der
    Plattenbau-Kandidaten mit Abzeichen „szacunek“; Literatur nur mit DOI, keine Zahl aus dem Artikel; Quellenvermerk
    und Haftungsklausel des ZBK wörtlich. Ortsmarke ul. Kościuszki 18 je Seite aus der eigenen Datei (zwei OSM-Punkte
    5,7 m auseinander).
  - Luft: Kontext der Uchwała ohne Kausalbehauptung; Vorher/Nachher nur als Mittel zweier Fenster ohne Differenz,
    Übergangsjahr grau; Kausalwendungen geprüft (`pruefen/D7_powietrze.py`, `pruefen/S3_themenseiten.mjs`).
  - Klima und Luft: Überschrift und Beschreibung ohne Hitze und ohne gemessene Versiegelung, Luft als „von der EEA
    berechnete Jahreswerte, orientacyjnie“.
  - Wohnungsmarkt: ODbL-Vermerk in den Quellen der Seite, weil die Mediane je dzielnica auf OSM-Grenzen beruhen.
  - Texte: `powietrze` und `klimat` mit `git mv` nach `texte/`, `mieszkania` als Kopie (der Vorschlag bleibt, weil
    `pruefen/DW_mieszkania.py` ihn fest liest).
- **Begründung:** Die Seiten sagen nicht mehr, als die Daten tragen (KR19, KR23, KR24, KR31).
- **Verworfen:** Stationskarte mit Beispieldaten; die Typologie als Verzeichnis; Projektname an der Ortsmarke.
- **Offen:** Sätze in den Datendateien (`planer*_odbl.js`, `erreichbar*.js`, `einrichtungen*.js`, `haltestellen.js`)
  sind deutsch, die Seiten bauen ihre Sätze aus Schlüsseln; der Radius steht nur im `zaehler_text` (Vorschlag
  `radius_m` an das Paket Versorgung und Takt). `mieszkania.js` in `mieszkania_odbl.js` umbenennen, bevor echte Daten
  kommen. Kleine Fallzahlen unter der Mindestzahl (KR22) sichtbar lassen oder ohne Zahl zeigen: bei echten
  RCN-Daten zu entscheiden. Ein gemeinsamer Punkt für ul. Kościuszki 18. `pruefen/DW_mieszkania.py` auf `texte/`
  ausrichten und den Vorschlag `docs/entscheidungen/DW-texte/` danach entfernen.
- **Behebung 14.11.2026** (`docs/entscheidungen/fix-daten.md` 2.1): Eine unterdrückte Fallzahl darf über das ganze
  veröffentlichte Gleichungssystem nicht festliegen (Stadt minus dzielnica, F10, `ohne_markt`; Nachtrag 3 zu Regel 4
  in `pruefen/N1_protokoll.md`). Der Erzeuger rechnet je unterdrückter Zahl Minimum und Maximum ganzzahlig und
  verdeckt weiter, bis keine festliegt; `pruefen/DW_mieszkania.py` rechnet unabhängig nach. Bei echten RCN-Daten
  kann die Zahl der verdeckten Felder steigen.
- **Neu prüfen, wenn:** echte Luft- oder RCN-Daten vorliegen oder die Datenpakete Felder statt Sätze liefern.

## KR44: Methode, Daten, Downloads und Zitierhinweis

Stand: bestätigt (14.11.); Seiten `metoda` und `dane` und der Fußvermerk-Patch als Vertragsänderung übernommen am 14.11.2026. Herkunft: `docs/entscheidungen/S4.md` S4-2 bis S4-10; Belege `belege/S4_downloads.md`, `belege/S4_langtexte.md`, Regeln vor dem Lauf `pruefen/S4_protokoll.md`.

- **Anlass:** Methode für alle Themen, Grenzen, Quellen, Lizenzen, Downloads und Zitierhinweis hatten keine Seite;
  der Potsdamer Export holte Geometrien aus der Datenbank.
- **Entscheidung:**
  - Downloads unter `daten/pobierz/`, nur aus `daten/*.js`: zwei GeoPackages (ohne ODbL und `_odbl`), CSV mit Punkt
    und mit Dezimalkomma, QGIS-Projekt, `licencje.csv`, `pola.csv`, `wartosci.csv`, CSV-Archiv, Liesmich pl/en/de;
    jede Spalte und jeder Kategorienwert erklärt, sonst bricht der Export ab. Beispieldateien bleiben draußen.
  - Die Ebene `siatka_1km` ohne ODbL übernimmt aus `zellen_odbl.js` nur die Eurostat-Werte und die Luftlinie, ohne
    `st`; Geometrie aus der Zellkennung (Lesart wie `erreichbar.js`).
  - Seiten `metoda` („Metodologia i ograniczenia“) und `dane` („Dane, źródła i licencje“) in allen Sprachen, über die
    Themenliste der Startseite erreichbar. Langtexte aus `texte/<lang>/bloecke/quelle/` mit Platzhaltern aus den
    Daten (`skripte/16_bloecke_krakow.py`); jeder Block mit Werten aus `_odbl`-Dateien endet mit dem ODbL-Vermerk,
    und der Seitenfuß nennt ihn auch dann (Patch `docs/entscheidungen/S4/fussvermerk-odbl.patch` in
    `skripte/30_seiten.py`).
  - Reihenfolge beim Neurechnen: Datenpakete, Export, Langtexte, `skripte/30_seiten.py`. Alle vier Prüfungen stehen in
    `pruefen.sh`.
  - `CITATION.cff` polnisch zuerst, ohne Lizenzfeld auf oberster Ebene (Lizenzen je Quelle in `references` und
    `licencje.csv`), gültig nach CFF 1.2.0.
- **Begründung:** Seiten und Downloads zeigen dieselben Werte; die Prüfkette bleibt ohne Datenbank; ändert ein
  Datenpaket eine Zahl, werden Blöcke und Downloads nicht still alt.
- **Verworfen:** `skripte/16_export.py` umschreiben (Gegenprobe); genaue Geometrie aus der Datenbank; Spalten
  polnisch umbenennen; `license` als Liste.
- **Offen:** Falschsätze aus `pruefen/S4_falschsaetze.json` in `pruefen/d3_falschsaetze.json` übernehmen und
  Anteile der Ausnahme III und XV als Feld (beides erledigt am 14.11.2026 in der Daten-Nacharbeit, KR45 und
  `steckbrief_dzielnice_odbl.json` Feld `zuordnung`); deutsche Vermerke in den Datendateien; Abgleich des EEA-Vermerks beim echten
  Lauf Luft; DOI (Andre); Gegenlesen der Langtexte durch Muttersprachler.
- **Neu prüfen, wenn:** Luft, Wohnungsmarkt oder das Denkmalregister echte Daten bekommen, eine DOI vergeben wird oder
  eine Rechtsprüfung die Lesart der Zellen ohne ODbL anders sieht.

## KR45: Falschsätze mit begründeten Fundorten

Stand: bestätigt (14.11., Master). Herkunft: `docs/entscheidungen/N1.md` Nr. 3.

- **Anlass:** Mit den Mustern aus `pruefen/S4_falschsaetze.json` in der gemeinsamen Liste trafen drei Muster
  (100-m-Gitter, Zensus 2022, ALKIS/dl-de) die Potsdamer Schlüssel der Gegenprobe (KR36) und die Seite `porownanie`,
  die die Potsdamer Quellen als Grund für fehlende Vergleiche nennt (KR37).
- **Entscheidung:** Ein Eintrag in `pruefen/d3_falschsaetze.json` darf ein Feld `ausser` tragen (Fundorte als
  regulärer Ausdruck über Textschlüssel und Seiten, dazu `grund`); `pruefen/texte.py` lässt diese Fundorte aus und
  meldet ein `ausser` ohne Grund als Befund. `pruefen/S4_bloecke.py` beachtet `ausser` nicht.
- **Begründung:** Das Muster bleibt überall sonst streng; jede Ausnahme ist mit Grund lesbar.
- **Verworfen:** Muster abschwächen; die Potsdamer Texte ändern (bräche die Gegenprobe).
- **Neu prüfen, wenn:** die Potsdamer Schlüssel aus `texte/` verschwinden.

## KR46: Gemeinsame Ortsmarke ul. Kościuszki 18

Stand: bestätigt (14.11., Master); setzt die Auflage „ein gemeinsamer Punkt aus einer Quelle, Wahl begründen“ zu KR43 um. Herkunft:
`docs/entscheidungen/N1.md` Nr. 4; Beleg `belege/N1_daten_nacharbeit.md`; Prüfung `pruefen/N1_daten.py`.

- **Anlass:** `denkmale_odbl.js` und `sanierung_odbl.js` setzten die Ortsmarke aus verschiedenen OSM-Objekten
  (5,7 m auseinander).
- **Entscheidung:** Quelle ist der OSM-Auszug in `eingang/`; gewählt ist der flächengrößte Gebäudeumriss mit
  Hausnummer 18 und „Kościuszki“ in der Straße innerhalb der Stadt, Punkt = `representative_point()` in EPSG:2178,
  berechnet in `skripte/ortsmarke.py` und von beiden Erzeugern gerufen. Gilt für die Dateien mit Geometrie;
  `sanierung.js` und `denkmale.js` tragen wegen der ODbL-Dateigrenze keinen Punkt. Kein Projektname an der Marke
  (KR24, KR31).
- **Begründung:** Der Punkt liegt sicher im Gebäude; dieselbe Regel verortet die ZBK-Liste im Sanierungsatlas. Die
  OSM-Kennung steht nur im Beleg.
- **Verworfen:** Mittel der Wegknoten (liegt bei nicht konvexen Umrissen nicht sicher im Gebäude); der Adressknoten
  (andere Postleitzahl, ein Geschäft im Haus).
- **Neu prüfen, wenn:** der OSM-Auszug neu geladen wird oder das Gebäude in OSM anders erfasst ist.

## KR47: Kopfleiste schmal und Bildzeile der Stadtteilgrenzen je Sprache

Stand: bestätigt (14.11., Master); die Vertragsänderung `daten/schema/ort.json` (`karte.teile_attribution` als Sprachwert, eine
Zeichenkette bleibt gültig) hat die Integration am 14.11.2026 übernommen. Herkunft: `docs/entscheidungen/N2.md`
Nr. 4 und 7; Belege `belege/N2_auslieferung-dd7344e.log`, `belege/N2_touch-c19b3e1.log`.

- **Anlass:** Bei 390 px lagen drei bis vier Navigationspunkte und der Sprachschalter außerhalb des Bildes; die
  Bildzeile der Stadtteilgrenzen war einsprachig, die Entscheidung vom 14.11.2026 gibt den Wortlaut je Sprache vor.
- **Entscheidung:** Nur in `rahmen.css` (Krakauer Seiten): bis 860 px oben Marke und Sprachschalter, darunter die
  ganze Hauptnavigation, unter 600 px in zwei Zeilen; Tippziele auf Touch 44 px. Bildzeile wörtlich pl „© współtwórcy
  OpenStreetMap, ODbL“, en „© OpenStreetMap contributors, ODbL“, de „© OpenStreetMap-Mitwirkende, ODbL“, aufgelöst
  über `I18N.sprachwert`.
- **Begründung:** Jede Navigation bleibt sichtbar; die Potsdamer Module bleiben byte-gleich (Gegenprobe).
- **Verworfen:** Menüknopf (Navigation unsichtbar); kleinere Schrift (reicht auf Deutsch nicht).
- **Neu prüfen, wenn:** die Bedienung am echten Handy (auch quer) anderes zeigt, oder der übrige polnische Wortlaut
  „© autorzy OpenStreetMap, ODbL 1.0“ in den Texten vereinheitlicht wird (offen, Paket Oberflächen-Texte).

## KR48: Ein Befehl für die ganze Kette

Stand: bestätigt (14.11., Master). Herkunft: `docs/entscheidungen/O.md` („Ein Befehl für die ganze Kette“).

- **Anlass:** Die Kette bestand aus 24 Einzelaufrufen, deren Reihenfolge nur in `docs/rundgang.md` stand.
- **Entscheidung:** `./atlas.sh trocken | alles | liste` (`skripte/kette.py`, nur Standardbibliothek) ruft die
  Skripte in der Reihenfolge des Rundgangs; vorher Prüfung von Werkzeugen, Datenbank (nur lesend) und Eingängen, Halt
  mit Liste bei fehlendem Pflichteingang, Wiederaufsetzen mit `--ab <schritt>`.
- **Begründung:** Eine Hochschule soll die Kette ohne die Herausgeberin betreiben können.
- **Verworfen:** Makefile; `skripte/lauf.sh` erweitern (bewusst schrittweise, Paket Infrastruktur).
- **Neu prüfen, wenn:** ein Skript neue Eingänge liest; `./atlas.sh alles` über alle Schritte ist nie gelaufen
  (gemeinsame Datenbank im parallelen Bau).

## KR49: Rohdaten-Schnappschuss

Stand: bestätigt (14.11., Master); der Upload als eigener Eintrag ist eine Veröffentlichung und bleibt bei Andre. Herkunft:
`docs/entscheidungen/O.md` („Rohdaten-Schnappschuss“).

- **Anlass:** Ohne die Rohdaten lässt sich keine Zahl nachrechnen; nicht jede Quelle erlaubt die Weitergabe.
- **Entscheidung:** `skripte/schnappschuss.py` packt nur ausdrücklich erlaubte Rohdaten mit Quelle, Lizenz und
  wörtlichem Vermerk je Regel; alles andere steht mit Grund und SHA256 in `AUSGESCHLOSSEN.md`. Archiv byte-gleich
  wiederholbar, vorher Abgleich mit `belege/rohdaten*.sha256`.
- **Begründung:** Nachrechenbarkeit ohne Lizenzrisiko; was keine Regel trifft, bleibt vorsichtshalber draußen (ZBK-Liste,
  npm-Angaben mit Adressen, BIP-Seite, MSIP).
- **Verworfen:** ganzes `$KIEZ_DATEN` weitergeben.
- **Neu prüfen, wenn:** eine Quelle einen neuen Stand hat oder ein Skript neue Eingänge liest.

## KR50: Prüfung vor Veröffentlichung, bereinigter Export

Stand: bestätigt (14.11., Master); die Veröffentlichung selbst bleibt bei Andre. Herkunft: `docs/entscheidungen/O.md` („Prüfung vor
Veröffentlichung“, „Git-Historie“).

- **Anlass:** Das Repo soll an eine Hochschule gehen; es enthält Arbeitsvermerke, Pfade des Arbeitsrechners in
  Prüfprotokollen und eine persönliche Adresse in jedem Commit.
- **Entscheidung:** `skripte/oeffentlich_pruefen.py` läuft in `pruefen.sh` (Befund = Rückgabe 1; bekannte Stellen
  anderer Eigentümer als Hinweis, mit `--veroeffentlichung` als Befund; begründete Ausnahmen in
  `skripte/oeffentlich_ausnahmen.tsv`). Öffentlich wird ein frischer Export aus dem geprüften Stand, nicht die
  Arbeitshistorie. Bildschirmfotos unter `belege/` als CC BY 4.0 mit den Vermerken BDOT10k und OpenStreetMap
  (Vorschlag, Zeile in `belege/README.md` steht aus).
- **Begründung:** Regel „nur bereinigter Export“ der UG; Kennungen in Belegen meinen dann die interne Historie.
- **Verworfen:** Historie mit `git filter-repo` umschreiben; Historie unverändert veröffentlichen.
- **Behebung 14.11.2026** (`docs/entscheidungen/fix-offen.md`): Sicherheits-Header als Vorschlag in
  `docs/auslieferung.md`, `docs/running.md` und `docs/uruchomienie.md` (CSP mit Hash des Inline-Skripts, den
  `skripte/deploy_kopie.py` ausgibt); GSAP wird nicht mehr ausgeliefert; `NOTICE` nennt Barlow als abgeleitete Fassung
  mit übertragenem Kerning; ZBK-Werte tragen auf Startseite, Steckbrief und Karte Vermerk und Haftungsklausel der
  Gmina Miejska Kraków. Die Lizenzregel unter `daten/` prüft `skripte/oeffentlich_pruefen.py` seit der Integration
  nur über genaue Namen oder ausdrückliche Globs. Offen: zentrale Quellenstände in `config/krakow.yaml`, Dateinamen
  `quellen-<Paket>.md`, Bezugsadresse der Geodaten-Import-Pipeline, Personennamen in Betreibertexten.
- **Neu prüfen, wenn:** Andre die Veröffentlichung freigibt (`./atlas.sh oeffentlich --veroeffentlichung` muss dann
  grün sein).

## KR51: CI und Zitierbarkeit

Stand: bestätigt (14.11., Master); die CI ist nie auf GitHub gelaufen (GitHub bleibt gesperrt). Herkunft: `docs/entscheidungen/O.md` („CI“,
„Zitierbarkeit“).

- **Anlass:** Eine übernehmende Hochschule braucht Prüfungen ohne Rohdaten und einen zitierbaren Eintrag.
- **Entscheidung:** `.github/workflows/pruefen.yml` führt nur Prüfungen ohne Rohdaten, Datenbank, Netz und Browser
  aus, dazu Trockenlauf und Prüfung vor Veröffentlichung. `.zenodo.json` beschreibt das Repo als `software`
  (Apache-2.0 nur für Code und eigene Texte); `CITATION.cff` bleibt `dataset` (KR44).
- **Begründung:** Repo ist das Rezept; Daten und Schnappschuss bekommen eigene Einträge.
- **Verworfen:** `pruefen.sh` in der CI unverändert (11 Befunde ohne Rohdaten); vorgeschlagen ist dafür ein Schalter
  `--ohne-rohdaten`.
- **Neu prüfen, wenn:** `pruefen.sh --ohne-rohdaten` kommt, Actions auf Commit-SHA festgeschrieben werden oder eine DOI
  vergeben wird.

## KR52: Schwelle der Gitteranteile aus der Ortskonfiguration

Stand: bestätigt (14.11., Master); Vertragsänderung `daten/schema/ort.json`. Herkunft: `docs/entscheidungen/fix-oberflaeche.md` Nr. 1.

- **Anlass:** `zellen_odbl.js` setzt `q_u15` und `q_65p` unter 100 Personen auf `null` (Mindestfallzahl KR17).
  `themen.js` graute nur unter 10 Personen aus; MapLibre zeichnete `null` in der Stufenregel schwarz (32 Zellen mit
  10 bis 99 Einwohnern).
- **Entscheidung:** `farbe()`, `hoehe()` und `unscharf()` prüfen auch auf einen fehlenden Wert. Neues optionales Feld
  `themen[].mindestfallzahl` in `config/krakow.yaml`, `daten/schema/ort.json` und `skripte/31_ort.py`; fehlt es, gilt
  10 wie in Potsdam. Die Legende nennt die Schwelle (`erzaehlung.leg_grau_gitter`, `{n}`). Die Potsdamer Schlüssel
  `karte.grau_personen` und `karte.grafik.unscharf_personen` bleiben unverändert (KR36).
- **Begründung:** Die Schwelle gehört zur Quelle, nicht zum Code; Schwarz las sich als Wert.
- **Verworfen:** die Schwelle fest auf 100 setzen (änderte die Gegenprobe Potsdam).
- **Neu prüfen, wenn:** ein Thema eine andere Mindestfallzahl braucht.

## KR53: Fehlender Langtext-Block bleibt leer, Seiten in Vorbereitung

Stand: bestätigt (14.11., Master). Herkunft: `docs/entscheidungen/fix-oberflaeche.md` Nr. 2.

- **Anlass:** Fehlte ein Block, setzte `skripte/30_seiten.py` den Satz `kern.in_arbeit` ein; sieben Seiten mit
  geprüften Daten endeten je Sprache mit „Ta część atlasu jest w przygotowaniu“.
- **Entscheidung:** Ein fehlender Block erzeugt nichts. Neuer Schlüssel `in_vorbereitung` in `config/krakow.yaml`
  (heute `[punktualnosc]`): Die Seite bleibt erreichbar, steht aber nicht in `{{liste:themenseiten}}`;
  `vorlagen/punktualnosc.html` ist `noindex` und setzt den Hinweis ausdrücklich.
- **Begründung:** Ein Hinweis „in Vorbereitung“ auf einer Seite mit echten Daten widerspricht dem Belegstandard.
- **Verworfen:** leere Blöcke anlegen (verdeckt, welche Seiten wirklich fehlen).
- **Neu prüfen, wenn:** das Thema Pünktlichkeit Daten liefert; dann `punktualnosc` aus `in_vorbereitung` nehmen.

## KR54: Polnische Begriffe für Gruppen und Taktklassen

Stand: bestätigt (14.11., Master); Begriffe in `docs/glossar-pl.md` unter „Zur Prüfung zuerst“. Herkunft: `docs/entscheidungen/fix-oberflaeche.md` Nr. 3 und 4.

- **Anlass:** Die vier Gruppen hießen teils „dzielnica historyczna“, die Haltestellen der Klassen I und II
  „przystanek z częstymi odjazdami“; beides wertet bzw. ist ungenau.
- **Entscheidung:** „delegatura (dawna dzielnica)“, auch in `gliederung.gruppe` in `config/krakow.yaml`; „przystanek
  klasy I lub II“ bzw. „z co najmniej dwoma odjazdami na godzinę“ (Schwelle aus `config/richtwerte.yaml`,
  `taktklassen.II`). Englisch und Deutsch bleiben.
- **Begründung:** ein Begriff je Sache; die Klasse ist eine Schwelle, kein Urteil.
- **Verworfen:** „dawna dzielnica (1973–1990)“ mit Jahreszahlen (aus Sprachwissen, nicht belegt).
- **Neu prüfen, wenn:** der Lehrstuhl die Glossarbegriffe gegenliest.

## KR55: Wohnungsmarkt nur ab 2019

Stand: entschieden (14.11., Master); Regel `pruefen/DW_protokoll.md`, Änderung KR55; Vertragsänderung
`daten/schema/mieszkania_odbl.json` (`regeln.erstes_jahr`, Schritt `ab_erstem_jahr`). Ergänzt KR22.

- **Anlass:** Eine unabhängige Prüfung des ersten echten Ergebnisses fand, dass bei 42 der 74 primär unterdrückten
  Fallzahlen aus den veröffentlichten Summen nur zwei mögliche Werte übrig blieben, meist 1 oder 2. Betroffen waren
  nur die Jahre 1900, 1901, 2006, 2007, 2009, 2012, 2016 und 2018: Dort ist der andere Markt mit n = 0
  veröffentlicht und `ohne_markt` = 0. Keine Zahl war eindeutig, die Differenzprobe (Regel 4) war deshalb grün.
- **Entscheidung:** Neuer Schritt F11 nach F10: Nur Käufe mit Dokumentjahr ab 2019 gehen in die Ausgabe; frühere
  Jahre stehen nicht in `daten/mieszkania_odbl.js`. Der Beleg nennt nur die Zahl der entfallenen Käufe. Die Summe
  über die Jahre gilt in Unterdrückung und Prüfung gegen F11. Der Erzeuger schreibt die Zahl der unterdrückten
  Felder mit einer Spanne von höchstens zwei Werten in den Beleg; eine unabhängige Rechnung
  (`belege/DW_spannenprobe.md`) kommt auf dieselbe Zahl: 0 von 32. Die Seite sagt „Daten ab {erstes Jahr}“ statt
  ausgeblendete Jahre aufzuzählen.
- **Begründung:** Eine Spanne von zwei Werten schützt einen Einzelkauf kaum. Die betroffenen Jahre zeigte die Seite
  ohnehin nicht (keine Stadtzahl ab der Mindestfallzahl); ab 2019 hat jedes Jahr eine veröffentlichte Stadtzahl.
  Es ist eine Verschärfung nach Sicht der Daten, keine Lockerung.
- **Verworfen:** die Bedingung „eindeutig“ allgemein auf „höchstens zwei Werte“ verschärfen und weiter verdecken
  (verdeckt viele Fallzahlen in Jahren, die niemand sieht); erst ab 2021 veröffentlichen (2019 und 2020 tragen echte
  Werte, ihre Grenze steht auf der Seite).
- **Neu prüfen, wenn:** eine neue RCN-Datei frühere Jahre mit Lage füllt oder die Spannenprobe größer als 0 wird.

## KR56: Sekundäre Unterdrückung mit mehreren Feldern

Stand: bestätigt (14.11., Master); Regel `pruefen/N1_protokoll.md`, Nachtrag 4 zu Regel 4; Umsetzung Commits
`28cd342` und `394a2c3` (`skripte/40_mieszkania.py`, `verdecken` und `_mehrere_verdecken`).

- **Anlass:** Der erste Lauf auf der GUGiK-Datei brach in der sekundären Unterdrückung ab: Mit `ohne_markt` = 0 hängt
  eine unterdrückte Fallzahl an zwei unabhängigen Gleichungen (in der dzielnica `ogolem` − anderer Markt, über die
  Stadt Stadt − übrige dzielnice); keine einzelne weitere Verdeckung machte sie unbestimmt.
- **Entscheidung:** Reicht keine einzelne Zelle, verdeckt der Erzeuger Kandidaten in der Reihenfolge von Nachtrag 3
  nacheinander, bis die Zahl unbestimmt ist, und veröffentlicht sie dann in umgekehrter Reihenfolge wieder, soweit
  die Zahl unbestimmt bleibt. Danach beginnt die Schleife über alle unterdrückten Zahlen von vorn. Die Bedingung
  (keine unterdrückte Zahl eindeutig) bleibt.
- **Begründung:** Durchsicht der Funktion am 14.11.2026, ohne Befund: Eine Verdeckung ersetzt einen festen Wert ≥ 10
  durch die Schranke „mindestens 10“, lockert also nur; Spannen werden nie enger. Jede Runde verdeckt mindestens
  ein Feld (beim Zurücknehmen bleibt mindestens das letzte nötige verdeckt), Verdeckungen früherer Runden werden nie
  zurückgenommen, also endet die Schleife nach höchstens so vielen Runden, wie es veröffentlichte Fallzahlen gibt.
  Das Zurücknehmen prüft nur die gerade behandelte Zahl; die übrigen bleiben geschützt, weil die verdeckte Menge
  danach eine Obermenge der vorigen ist, und die nächste Runde prüft ohnehin alle. Felder mit n = 0 sind keine
  Kandidaten (dort gibt es keinen Median, eine Verdeckung wäre selbst eine Aussage). Ergebnis am echten Lauf:
  27 verdeckte Fallzahlen, Differenzprobe 0.
- **Verworfen:** eine optimale (kleinste) Verdeckung über ein eigenes Optimierungsproblem (aufwendiger, für 27 Felder
  ohne Nutzen); Abbruch und Handentscheidung je Fall.
- **Neu prüfen, wenn:** `ohne_markt` größer als 0 wird oder der Erzeuger erneut mit Rückgabe 4 abbricht.

## KR57: Denkmalregister aus Wikidata auf den Seiten, getrennt von OSM

Stand: bestätigt (15.11.2026, Master). Herkunft:
`docs/entscheidungen/DZ.md` §9, Zweig `Arbeitszweig p4-denkmale`. Ersetzt den Teil von KR43, nach dem `daten/denkmale.js` auf
`kamienice` nicht geladen wird. Vertragsänderung `daten/schema/denkmale.json` (`quellen.wd.vermerk`, `sichtpruefung`)
und Nachtrag 3 in `pruefen/DZ_protokoll.md` zur Bestätigung.

- **Anlass:** `daten/denkmale.js` ist seit dem Handdownload vom 14.11.2026 echt (nur Wikidata), wurde aber von keiner
  Seite geladen. Die Sichtung für die Professorin (Denkmal und Stadtumbau) nannte die Kamienice-Seite „ehrlich, aber
  inhaltlich dünn“: vor allem OSM-Punkte, „bez rejestru zabytków“.
- **Entscheidung:** `kamienice` zeigt die Registerpunkte je Delegatura neben der OSM-Kennzeichnung; die freie Karte hat
  eine eigene Ebene `rejestr` (Wikidata, CC0 1.0), getrennt von `zabytki` (OSM, ODbL), alte Links zeigen weiter OSM;
  die Downloads haben die Ebene `rejestr_zabytkow` im GeoPackage ohne OSM-Anteil. Die Kennzahl heißt
  „Registerpunkte“ (Gruppe von Wikidata-Objekten mit derselben Registernummer, an der Koordinate des ersten Objekts):
  1.909 Objekte ergeben 1.214 Punkte; Bauzeitklassen werden an den Punkten gezählt (972), nicht am Zähler
  `zaehlung.wd.bauzeit_lesbar` (873). Vor dem Einbinden legt Nachtrag 3 eine zweite Stichprobe fest (Startwert
  20261114, je 20 Punkte aus Wikidata und OSM aus genau der gezeigten Menge); sie ist nicht ausgewertet,
  `sichtpruefung.geprueft` bleibt `false`.
- **Begründung:** Für das Fachpublikum ist das Register die wichtigste Quelle der Seite; getrennte Ebenen halten Lizenz,
  Herkunft und Prüfstand je Punkt nachvollziehbar.
- **Verworfen:** Registerpunkte in die Ebene `zabytki` mischen (Herkunft und Lizenz nicht mehr unterscheidbar); die
  Zahl „Registernummern“ nennen (die Gruppierung ist nicht transitiv, siehe `docs/entscheidungen/DZ.md`).
- **Neu prüfen, wenn:** das NID-Register oder die gminna ewidencja per Handdownload vorliegen, oder die Stichprobe am
  Luftbild ausgewertet ist.

## KR58: Rubriken in der Kopfleiste, ein Satzspiegel, Inhaltsverzeichnis

Stand: bestätigt (15.11.2026, Master); Rechtsfragen zu eingeklappter OSM-Attribution und ZBK-Haftungsklausel entschieden: beide bleiben beim Laden sichtbar. Herkunft:
`docs/entscheidungen/p4-gestaltung.md` Nr. 1–5, 13, 16. Vertragsänderung im Gerüst: Schlüssel `rubriken` in
`config/krakow.yaml`, `skripte/30_seiten.py` (`rubriken`, `{{liste:spis}}`, `data-schliessen`),
`vorlagen/_rahmen.html`, neue Prüfung `pruefen/beispielmarke.py` in `pruefen.sh`. Neue oder geänderte Textschlüssel
in fremden Namensräumen: `kern.spis`, `erzaehlung.vg_nenner`, `erzaehlung.a_takt_ohne`,
`erzaehlung.zbk_zastrzezenie`, `erzaehlung.vg_von`, `erzaehlung.register_quelle`, `planer.e.start_hinweis`,
`powietrze.tab.ab_jahr`.

- **Anlass:** Methode, Daten und vier Themen fehlten in der Hauptnavigation; drei Satzspiegel (1100/1240/1280 px);
  ein festes Abzeichen „Beispieldaten“ an den echten EEA-Stationen (Blocker der Sichtung).
- **Entscheidung:** Hauptnavigation Start · Mapa · Dzielnice · Kamienice · Dostępność · Tematy · Metodologia; eine
  Rubrik ist ein Navigationspunkt ohne eigene Seite (Ziel, Text, Kacheln), „Tematy“ führt auf `index.html#tematy`.
  Ein Satzspiegel von 1280 px für alle Seiten, linksbündig auf der Flucht der Marke. `{{liste:spis}}` baut das
  Inhaltsverzeichnis aus den Abschnitten der fertigen Seite. Kein Markup darf `fl-beispiel` fest tragen
  (`pruefen/beispielmarke.py`). Jeder abweichende Nenner der Gitter-Einwohnersummen steht auf der Seite.
- **Begründung:** Eine Professorin sucht Methode und Daten zuerst; feste Abzeichen ohne Datenbezug sind Behauptungen.
- **Verworfen:** eigene Übersichtsseite „Tematy“ (neue Seiten nur über die Integration), Satzspiegel zentriert
  (80 px Versatz zur Marke), Navigationspunkt „Metoda i dane“ (doppelt mit „Dane“).
- **Neu prüfen, wenn:** eine Rubrik mehr als vier Unterseiten bekommt (Zeilenbreite bei 360 px).

## KR59: Prozent- und Minuszeichen nach Landesbrauch

Stand: bestätigt (15.11.2026, Master). Herkunft:
`docs/entscheidungen/p4-sprache.md` F3, S24 und `p4-gestaltung.md` Nr. 15; in der Integration zusammengeführt
(`vergleich.js`, `erzaehlung.js`).

- **Anlass:** Prozentzeichen mal mit, mal ohne Leerzeichen, teils im selben Satz; Bindestrich statt Minus.
- **Entscheidung:** Die Krakauer Seitenmodule nehmen das Prozentzeichen aus `fmt.anteil` (`PZ`: pl und en ohne
  Leerzeichen, de mit geschütztem Leerzeichen, wie `Intl`/CLDR); Vorlagen in pl und en ohne Leerzeichen. Werte mit
  Vorzeichen tragen U+2212 (Startseite, Steckbrief, Vergleich). Die Glossarregel ist angepasst. CSV-Downloads behalten
  den ASCII-Bindestrich.
- **Begründung:** `i18n.js` ist ein eingefrorener Vertrag („Zahlen nach Landesbrauch, nie selbst formatieren“); die
  alte Glossarregel „mit Leerzeichen“ widersprach der eigenen Formatierung.
- **Verworfen:** `fmt.anteil` nachbearbeiten (bricht den Vertrag); ein zentrales `fmt.vz()` in `i18n.js` jetzt
  einzuführen (Vertragsänderung mit Potsdam; bleibt Vorschlag).
- **Neu prüfen, wenn:** `i18n.js` geöffnet wird; dann `fmt.vz(x, stellen)` für alle Werte mit Vorzeichen.

## KR60: Polnische Fachbegriffe der Sprachbehebung

Stand: bestätigt (15.11.2026, Master); Glossar `docs/glossar-pl.md`
bleibt „Vorschlag“. Herkunft: `docs/entscheidungen/p4-sprache.md` Abschnitt 1 und 2. Ergänzt KR54.

- **Anlass:** Zwei Durchsichten der polnischen Texte; blockierend „intensywność zabudowy“ für den Anteil der
  Gebäudegrundfläche (im Planungsrecht die Geschossflächenzahl).
- **Entscheidung:** „udział powierzchni zabudowy“ für den Bebauungsanteil, „intensywność zabudowy“ nur für die
  GFZ-Näherung im Download; „© autorzy OpenStreetMap“ (openstreetmap.org/copyright/pl); „eksploatowany“ (Wert von
  `KAT_ISTNIE`); „kompleksy“ für die Komplexe der BDOT10k; „stan na …“ für den Stichtag der NSP 2021 (Ustawa o NSP
  2021, art. 1 ust. 2, DU/2019/1775); „95-procentowy przedział ufności (metoda Wilsona)“; „wielka płyta“, „osiedle
  blokowe“, „komórka siatki“. Rechtsquelle der Grenzwerte mit Datum und tekst jednolity.
- **Begründung:** Bei Widerspruch zwischen den Durchsichten entscheidet eine Primärquelle (je Fund in
  `p4-sprache.md`).
- **Verworfen:** die Vollform der Rechtsquelle in den Datenzeilen (der Vertrag `powietrze.json` legt die Kurzform
  fest); Kurznamen der delegatury in Tabellen (die amtlichen Namen kommen aus den Daten).
- **Neu prüfen, wenn:** das muttersprachliche Lektorat die Punkte unter „Zur Prüfung zuerst“ beantwortet.

## KR61: Betrieb ohne unsere Rechner: Schrift im Repository, vollständige Kette, ehrliche Grenzen

Stand: bestätigt (15.11.2026, Master). Herkunft:
`docs/entscheidungen/p4-betrieb.md` Nr. 1–18.

- **Anlass:** Ein Neuaufbau nur mit der Anleitung (Container, ohne `.env`) kam an zwei Stellen nicht weiter: Schritt
  `02a` fehlte in der Kette, die Kartenschrift kam aus einem Arch-Paket. Die Methodenseite versprach Selbstprüfung
  ohne Repository-Adresse.
- **Entscheidung:** Die drei Noto-Sans-Dateien liegen byte-gleich unter `schriften/noto/` mit `OFL.txt` (nicht in
  der Auslieferung); `02a_stadtteile_uebersicht.py` ist Schritt der Kette direkt nach der Bevölkerung; der EEA-Eingang
  wird als GeoJSON(-ZIP) oder CSV erkannt. Die Anleitungen setzen `KIEZ_DATEN`, nennen die Installationswege und
  schränken die Byte-Gleichheit auf den Rechner der Herausgeberin ein. Methode und Daten sagen in allen drei
  Sprachen, dass das Repository noch nicht öffentlich ist (Code und Belege auf Anfrage).
- **Begründung:** Eine Hochschule soll das Rezept ohne Rückfrage betreiben können; was noch nicht geht, steht da.
- **Verworfen:** Koordinaten doppelt runden, um die Abweichung in der 5. Nachkommastelle zu verdecken (verschiebt nur
  die Kippstelle); das Vorschaubild (`og:image`) jetzt (nützt erst mit der Veröffentlichung).
- **Neu prüfen, wenn:** das Repository veröffentlicht ist (echte Links) oder ein Referenz-Image die Reproduzierbarkeit
  auf fremden Rechnern belegt.

## KR62: Änderungen an gemeinsamen Dateien des Potsdamer Stands

Stand: bestätigt (15.11.2026, Master). Betrifft KR36 („Potsdamer Module unverändert,
Änderungen nur über die Integration“).

- **Anlass:** Die Behebung „Betrieb“ hat in `atlas.css` die Ersatzschriften von `--f-display` erweitert (schmale
  Systemschriften gegen den Umbruch der h1 vor dem Laden von Barlow); die Gestaltung hat `skripte/30_seiten.py`
  erweitert, das auch die Gegenprobe Potsdam nutzt.
- **Entscheidung:** Beide Änderungen übernimmt die Integration als Eigentümerin. Die erste Schrift der Kette bleibt
  Barlow Semi Condensed, also sehen Seiten in Potsdam nach dem Laden der Schrift gleich aus; `30_seiten.py` verhält sich ohne
  `rubriken` wie bisher. Beleg: Gegenprobe Potsdam im Prüfstand der Integration.
- **Begründung:** Ein eigener Krakauer Zweig von `atlas.css` für eine Zeile wäre teurer als die gemeinsame Änderung.
- **Verworfen:** die Ersatzschriften nur in einer Krakauer CSS-Datei setzen (`--f-display` wird in `atlas.css`
  definiert; eine zweite Definition hinge von der Ladereihenfolge ab).
- **Neu prüfen, wenn:** die Gegenprobe Potsdam eine Abweichung meldet.

## KR63: Belegfilme auf Polnisch, Lizenz wie die Bildschirmfotos

Stand: bestätigt (15.11.2026, Andre: Lizenz CC BY 4.0).11.2026); die Lizenz bestätigt Andre vor der Veröffentlichung. Herkunft:
`belege/filme/README.md` (Zweig Filme), Abnahme-Funde in `docs/entscheidungen/review-p4b.md`.

- **Anlass:** Eine Hochschule soll in wenigen Minuten sehen, was der Atlas zeigt und wie er belegt. Die Filme hatten
  keine Lizenz; `oeffentlich_pruefen.py --veroeffentlichung` war deshalb rot, und der Export wäre gescheitert.
- **Entscheidung:** Drei Filme ohne Ton (je 65 bis 70 s, 1280 × 720, MP4 und WebM je höchstens 5 MB, Untertitel als
  WebVTT pl/en/de), aufgenommen von `skripte/filme.mjs` aus den echten Seiten über den Entwicklungsserver, Bilder aus
  dem Bildschirm-Streaming von Chromium direkt an ffmpeg (kein `recordVideo`, keine Zwischendateien). Zahlen in den
  Untertiteln kommen beim Lauf aus den Datendateien. Lizenz CC BY 4.0 wie die Bildschirmfotos (KR50), mit den
  Vermerken der Quellentafel; die Lizenzzeile erzeugt das Skript selbst im README. Der „Vergleich“ in Film 1 ist
  `porownanie.html`. Keine Personen, keine RCN-Einzelfälle, keine ZBK-Gebäudepunkte im Bild.
- **Begründung:** Die Filme zeigen dieselben eigenen Seiten wie die Bildschirmfotos; eine zweite Lizenz wäre ohne
  Grund. 5 MB statt 8 MB, damit die Größenprüfung ohne Ausnahme grün bleibt.
- **Verworfen:** Filme aus 1.0.0 herauslassen (sie sind fertig und geprüft); Bildschirmaufnahme mit `recordVideo`
  (ruckelt, braucht Zwischendateien); Zahlen im Skript.
- **Neu prüfen, wenn:** das muttersprachliche Lektorat die Untertitel ändert (dann neu aufnehmen) oder eine Seite
  sich sichtbar ändert.

## KR64: OSM-Kennzeichnung der Denkmale ohne Ocker

Stand: Vorschlag der Integration (15.11.2026). Herkunft: Abnahme-Fund „Orange in Film 2“.

- **Anlass:** Die Kartenebene „oznaczenie zabytku w OpenStreetMap“ hatte `#b07a1f`; in der Nahaufnahme von Stare
  Miasto waren das viele ockerfarbene Punkte. `DESIGN.md` schließt Orange aus.
- **Entscheidung:** Füllung `#efe6f3` mit Rand `#6a2c82` in `karta.js`, wie die OSM-Kennzeichnung auf `modernizacja`
  (`sanierungsatlas.js`); die Legende zeigt den Rand mit. Das Register aus Wikidata bleibt voll violett mit dunklem
  Rand, beide Ebenen sind nebeneinander unterscheidbar (Standbild Film 2).
- **Begründung:** Gleiche Bedeutung, gleiches Zeichen auf allen Seiten; Palette aus `DESIGN.md`.
- **Verworfen:** ein Blauton aus der Gitterskala (fällt mit den Haltestellen-Klassen zusammen).
- **Neu prüfen, wenn:** weitere Punktebenen dazukommen.

## KR65: Schnappschuss mit EEA und Wikidata, ohne RCN-Transaktionen (Nachtrag zu KR49)

Stand: Vorschlag der Integration (15.11.2026); vor dem Upload bestätigt Andre die Lizenzen (Auslöser aus KR49).
Herkunft: Zweig Veröffentlichung, `skripte/schnappschuss.py`.

- **Anlass:** Seit den Handdownloads vom 14.11.2026 rechnen Luft, Wohnungsmarkt und Denkmalregister aus Rohdaten,
  die der Schnappschuss noch nicht kannte.
- **Entscheidung:** Aufgenommen werden der EEA-Auszug (CC BY 4.0, Nennung „EEA; Daten: GIOŚ“) und das
  Wikidata-Ergebnis (CC0 1.0). Die RCN-Einzeltransaktionen bleiben draußen und stehen mit Grund in
  `AUSGESCHLOSSEN.md`. Inhalt laut Trockenlauf 404.127.036 B.
- **Begründung:** Beide Lizenzen erlauben die Weitergabe ausdrücklich; Einzeltransaktionen können Personenbezug haben
  (KR22), die Seiten zeigen nur Mediane ab 10 Käufen.
- **Verworfen:** RCN-Datei mit Hinweis weitergeben.
- **Neu prüfen, wenn:** eine Quelle ihre Lizenz ändert oder der Wohnungsmarkt ohne die Rohdatei nachrechenbar sein soll.

## KR66: Repository-Adresse als Schalter, Bedingungen in Langtexten

Stand: Vorschlag der Integration (15.11.2026). Herkunft: Zweig Nacharbeit zur Sichtprüfung.

- **Anlass:** Nach der Veröffentlichung muss die Methodenseite das Repository verlinken; ohne die Datei der
  Sichtprüfung brach die Erzeugung der Langtexte ab, statt auf „ungeprüft“ zurückzufallen.
- **Entscheidung:** `config/krakow.yaml` hat den Schlüssel `repository` (leer, nur `https://`). Ist er gesetzt,
  verlinkt `metoda` das Repository und lässt den Satz „noch nicht öffentlich, auf Anfrage“ weg.
  `skripte/16_bloecke_krakow.py` kennt dafür `[[wenn …]] … [[sonst]] … [[ende]]` (Datei oder Konfigurationsschlüssel);
  ohne `belege/DZ_sichtpruefung.json` stehen die Sätze von vor der Sichtprüfung da. Nach einer Änderung an
  `config/krakow.yaml` zuerst `skripte/31_ort.py` (Prüfsumme in `daten/ort.js`).
- **Begründung:** Eine Angabe an einer Stelle statt Handänderungen in drei Sprachen; der Rückfall hält das Rezept für
  eine neue Stadt ohne Sichtprüfung lauffähig.
- **Verworfen:** die Blöcke beim Veröffentlichen von Hand ändern.
- **Neu prüfen, wenn:** weitere Seiten (`dane`, Anleitungen) die Adresse brauchen; heute erfasst der Schalter nur
  `metoda` (Liste in Schritt 7 der Schrittliste der Herausgeberin).

## KR67: Version 1.0.0 als bereinigter Export

Stand: Vorschlag der Integration (15.11.2026); die Veröffentlichung selbst bleibt bei Andre (KR50). Herkunft: Zweig
Veröffentlichung, Abnahme.

- **Anlass:** KR50 legt fest, dass nur ein bereinigter Export öffentlich wird; offen war, wie er entsteht.
- **Entscheidung:** Ein Werkzeug der Herausgeberin erzeugt aus einem geprüften Stand per `git archive` einen Export mit
  einem einzigen Commit „Kiezatlas Kraków 1.0.0“ und Tag `v1.0.0`; Autor „André Stiebitz“ mit der Rollenadresse.
  Ersetzt werden mechanisch nur die Stellen, die `oeffentlich_pruefen.py` vor einer Veröffentlichung meldet (Pfade,
  Rechnername, Arbeitsvermerke), mit Lesehilfe und Zählung in `docs/export.md` des Exports. Gleicher Baum, Autor und
  Datum ergeben denselben Commit. Werkzeug, Schrittliste und Release-Notizen sind nicht im Export (`export-ignore`).
  `CITATION.cff` und `.zenodo.json` tragen Version 1.0.0 und Datum 15.11.2026.
- **Begründung:** Wiederholbar und prüfbar: Wer nach einer Änderung neu exportiert, sieht am Hash, ob sich am
  veröffentlichten Inhalt etwas geändert hat.
- **Verworfen:** Ersetzungen von Hand im Export; die persönliche Adresse als Autor.
- **Neu prüfen, wenn:** eine zweite Version veröffentlicht wird (dann Folgecommit im öffentlichen Repo statt neuer
  Einzelcommit).

## KR68: Prüfungen ohne Rohdaten

Stand: Vorschlag der Integration (15.11.2026). Herkunft: Abnahme-Fund „frischer Klon ohne Rohdaten rot“.

- **Anlass:** In einem frischen Klon ohne `$KIEZ_DATEN` meldete `./pruefen.sh` Befunde bei Luft und Wohnungsmarkt,
  obwohl der Kopf verspricht, dass fehlende Rohdaten als übersprungen zählen.
- **Entscheidung:** Fehlt der EEA-Auszug unter `eingang/eea/` bzw. das GeoPackage unter `eingang/rcn/`, ruft
  `pruefen.sh` `pruefen/D7_powietrze.py` bzw. `pruefen/DW_mieszkania.py` mit `--ohne-lauf` auf (wie die CI) und
  zählt die Neurechnung als übersprungen. Die Befunde der Prüfsummenlisten bleiben (dokumentiert in
  `docs/running.md` §8 und `docs/uruchomienie.md` §8).
- **Begründung:** Eine Hochschule soll beim ersten Lauf nur Befunde sehen, die erklärt sind.
- **Verworfen:** Prüfsummenlisten ohne Rohdaten überspringen (sie sollen zeigen, dass Rohdaten fehlen).
- **Neu prüfen, wenn:** weitere Prüfungen Rohdaten brauchen.

## KR69: Adressen der Repositorys (15.11.2026)

Stand: Prüfung der Integration (15.11.2026). Herkunft: Zweig Repository-Adressen.

- **Anlass:** Anleitungen und Übergabe sagten, drei Adressen fehlten und es sei ungeprüft, ob die Repositorys
  öffentlich sind; der Mailentwurf an die Hochschule übernahm das.
- **Geprüft (15.11.2026):** `gh repo view` und `git ls-remote` auf die drei Adressen, Zenodo per
  `curl -sIL https://doi.org/10.5281/zenodo.24073612` und `https://zenodo.org/api/records/24073612`:
  - `https://github.com/andremadstop/kiezatlas-krakow`: öffentlich, am 15.11.2026 angelegt, noch leer (Export 1.0.0
    folgt, Schrittliste der Herausgeberin).
  - `https://github.com/andremadstop/geodaten-import-pipeline`: öffentlich, `LICENSE` Apache-2.0, `main` =
    `12bae5bc96cf34355c8c5a723eb444e66f776f2d` = `PIPELINE_SOLL` in `skripte/lauf.sh`; der Tag dieses Stands zeigt
    auf denselben Commit.
  - DOI 10.5281/zenodo.24073612 löst auf `zenodo.org/records/24073612` auf: Titel „Geodaten-Import-Pipeline
    (WFS/CSV → PostgreSQL/PostGIS)“, Lizenz Apache-2.0, Autor André Stiebitz, veröffentlicht 09.11.2026, verwandte
    Kennung „isSupplementTo“ = genau dieser Tag im Pipeline-Repo, also derselbe Commit. Eingetragen ist die
    Versions-DOI (nicht die Konzept-DOI 10.5281/zenodo.24073610), weil nur sie an den festgeschriebenen Stand gebunden ist.
  - `https://github.com/andremadstop/kiezatlas-potsdam`: öffentlich, `LICENSE` Apache-2.0, kein Release, keine DOI.
- **Entscheidung:** `repository` in `config/krakow.yaml` gesetzt (KR66); der Schalter wirkt jetzt auch auf den Absatz
  „Zitieren“ der Datenseite. Anleitungen (`docs/uruchomienie.md`, `docs/running.md`), Übergabe (`docs/przekazanie.md`),
  `CITATION.cff` (`repository-code`, Eintrag `references` der Pipeline mit Commit und DOI) und `.zenodo.json`
  (`related_identifiers`, „requires“) nennen die Adressen. Offen bleibt nur der Rohdaten-Schnappschuss (Schritt 6 der
  Schrittliste); die DOI des Atlas selbst kommt in Schritt 7.
- **Begründung:** Die Sätze waren seit der Veröffentlichung der Repositorys falsch und hätten Lesern einen Weg über die
  Herausgeberin vorgeschrieben, den es nicht braucht.
- **Verworfen:** den internen Tag-Namen der Pipeline oder die Zenodo-Adresse mit Tag nennen (im Export nicht erlaubt,
  Prüfmuster „interner Tag“); Commit und DOI genügen.
- **Neu prüfen, wenn:** `PIPELINE_SOLL` sich ändert (dann neue Pipeline-Version mit eigener DOI eintragen) oder ein
  Repository umzieht.


## KR70: Gemeinsame Kiezatlas-Maschine (16.11.2026)

Stand: 16.11.2026. Entscheidung der Herausgeberin: ein Code für alle Städte, in einem eigenen Repository.

- **Anlass:** Der Code dieses Atlas zeigt nachweislich auch Potsdam (Gegenprobe, 0 Abweichungen). Ohne gemeinsamen Ort
  entstehen Verbesserungen je Stadt doppelt, und die Städte laufen auseinander.
- **Entscheidung:** Der ortsunabhängige Teil liegt im eigenen Repository `kiezatlas` (die Maschine). Kraków enthält
  eine Kopie zu festem Commit: `MASCHINE.txt` nennt die Dateien, `MASCHINE.lock` Commit und SHA256 je Datei,
  `skripte/maschine.py` holt und prüft, `pruefen.sh` prüft die Kopie. Maschinendateien werden hier nicht von Hand
  geändert. Erste Fassung byte-gleich mit e7c85ca (16 Dateien: Laufzeit-Module, Seitenrahmen, Seitengenerator);
  keine ausgelieferte Datei hat sich geändert (Deploy-Liste 619 Dateien, keine davon im Diff).
- **Begründung:** Eine Kopie hält dieses Repository und jedes Archiv (Zenodo) für sich allein vollständig, so wie es
  das offene Rezept verlangt; der feste Commit macht jede Stadt nachrechenbar. Adressen und DOI bleiben unverändert.
- **Verworfen:** Maschine in diesem Repository mit Potsdam als zweiter Konfiguration (ein Repository mit Stadtnamen
  für mehrere Städte); Potsdam zieht die Maschine aus Kraków (Kraków bliebe Sonderfall); Maschine ohne Kopie nur zur
  Laufzeit nachladen (Archiv unvollständig).
- **Neu prüfen, wenn:** eine Stadt eine Maschinendatei ändern muss, die für die anderen nicht passt, oder die Kopie
  so groß wird, dass sie die Prüfungen der Städte verlangsamt.

## Nie sprawdzono / Nicht geprüft sind …

- die polnischen und englischen Oberflächentexte und die Untertitel der Filme durch Muttersprachler (Fachbegriffe
  Status „Vorschlag“);
- die Zuordnung der 18 dzielnice zu den vier historischen Stadtbezirken an einer amtlichen Liste der Stadt (geprüft
  ist sie gegen die delegatury der BDOT10k, KR17);
- jede Zahl auf den Seiten durch eine unabhängige Nachrechnung: die Seiten zeigen seit dem 14.11.2026 die echten
  Daten (seit den Handdownloads vom 14.11.2026 auch Luft, Wohnungsmarkt und Denkmalregister aus Wikidata); geprüft ist, dass Seiten, Langtexte und Downloads
  dieselben Werte wie die Datendateien zeigen, nicht die Rechnung dahinter (Stand je Thema in `docs/rundgang.md`);
- die Lizenzfolge der OSM-Grenzen, die LoD-Freigabe und die EEA-Lizenzzeile durch eine Rechtsprüfung (entschieden
  hat die Projektleitung nach Lesart, KR3, KR18, KR20), die Datenschutzgrenze des Wohnungsmarkts (KR22) und die des
  Sanierungsatlas (KR31);
- der Stichtag des NSP 2021 in den Daten: die Fundstelle liegt seit der Sprachbehebung vor (Ustawa o NSP 2021,
  art. 1 ust. 2, DU/2019/1775: „według stanu na dzień 31 marca 2021 r.“), `daten/steckbrief.js` trägt aber noch
  `stichtag_geprueft: false` (Paket Gliederung und Bevölkerung);
- die Lizenzen der neuen Themen Pünktlichkeit, Wohnungsmarkt, Klima und Luft (KR11, je im eigenen Paket);
- die polnischen Ortsangaben und Fachbegriffe in diesen Dokumenten auf Rechtschreibung durch Muttersprachler;
- die Lage jedes einzelnen Denkmalpunkts am Luftbild (geprüft ist je Ebene eine Zufallsstichprobe von 20 Punkten,
  KR33 Nachtrag) und die Bauweise der Typologie-Kandidaten (die Stichprobe vom 14.11.2026 prüfte nur, ob ein Wohnblock
  zu sehen ist, KR31);
- die Hashes der Python-Pakete beim Start aus dem Zwischenspeicher (KR34).
- offene Quellen für die Seite „modernizacja“, die sie heute nicht zeigt und deren Lizenz nicht geprüft ist: Gebiete
  des Gminny Program Rewitalizacji (Stadt Kraków) und Oberflächentemperatur (Hitzeinseln) aus Landsat- oder
  Copernicus-Produkten; Wärmebedarf und Heizungsart gibt es nicht offen (CEEB, KR4). Vor einer Nutzung Lizenz prüfen
  und über `skripte/abruf.py` abrufen; die Seite sagt im Vorspann, dass sie Bestand und Typologie zeigt, nicht
  Sanierungsbedarf.

**PL (skrót):** Nie sprawdzono dotąd: tekstów polskich i angielskich przez native speakerów, przypisania 18 dzielnic do
czterech delegatur (dawnych dzielnic) w urzędowym wykazie miasta, żadnej liczby na stronach w niezależnym
przeliczeniu, daty spisu NSP 2021 (stan na) w danych atlasu ani licencji nowych tematów w drodze opinii prawnej.

## Kürzel

| Kürzel | Bedeutung |
|---|---|
| KR1 bis KR62 | Entscheidungen des Kiezatlas Kraków (dieses Dokument) |
| A1 bis A20 | Entscheidungen des Kiezatlas Potsdam (dort `docs/entscheidungen.md`); hier nur als Herkunft erwähnt |
| E1 bis E48 | Entscheidungsprotokoll der Geodaten-Import-Pipeline |
| L1 bis L10, Z1 bis Z5 | Lehren aus dem Potsdamer Audit und Zusatzauflagen in `docs/checkliste.md` |
| BDOT10k | Baza Danych Obiektów Topograficznych 1:10 000, topographische Datenbank der Landesvermessung |
| BIP | Biuletyn Informacji Publicznej, amtliches Informationsblatt |
| CEEB | Centralna Ewidencja Emisyjności Budynków, Register der Heizungen und Emissionen von Gebäuden (nicht offen, KR4) |
| EPSG | Register der Koordinatensysteme; EPSG:2178 ist das Rechensystem (KR1) |
| EGiB | Ewidencja Gruntów i Budynków, Liegenschaftskataster |
| GIOŚ | Główny Inspektorat Ochrony Środowiska, Hauptinspektion für Umweltschutz (Luftmessnetz) |
| GTFS, GTFS-RT | Fahrplanformat und seine Echtzeit-Ergänzung |
| GUGiK | Główny Urząd Geodezji i Kartografii, Hauptamt für Geodäsie und Kartographie |
| GUS | Główny Urząd Statystyczny, Statistisches Hauptamt |
| LoD1, LoD2 | Detailstufen von 3D-Gebäudemodellen (Klötzchen bzw. mit Dachform) |
| MSIP | Miejski System Informacji Przestrzennej, Geoportal der Stadt Kraków |
| NID | Narodowy Instytut Dziedzictwa, Nationales Denkmalinstitut |
| NSP 2021 | Narodowy Spis Powszechny Ludności i Mieszkań 2021, Volks- und Wohnungszählung |
| OSM | OpenStreetMap |
| ODbL | Open Database License 1.0 (OpenStreetMap) |
| UG | Stiebitz Souverain Systems UG (haftungsbeschränkt), Herausgeberin |
| ZTP | Zarząd Transportu Publicznego w Krakowie, städtischer Verkehrsträger |

Interne Dokumente der UG (Bauvorlage, Machbarkeitsbericht) werden hier nicht zitiert; was aus ihnen gilt, steht in
den Abschnitten oben ausgeschrieben.
