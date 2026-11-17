# Änderungen

Je veröffentlichtem Stand ein Abschnitt und ein Git-Tag, ab 1.0.0 `v<Version>` (Zenodo übernimmt die Version aus dem Tag; vorher `stand-JJJJ-MM-TT`). Unveröffentlichtes steht oben.

## Unveröffentlicht

(nichts)

## 1.1.0 (17.11.2026)

### Volkszählung je statistischem Bezirk (17.11.2026)

- Grenzen der rejony statystyczne aus dem GUS-Datensatz „Jednostki statystyczne 2021“ (BREC, INSPIRE), gelesen direkt
  aus der Datei des Downloaddienstes (`skripte/raum_bevoelkerung.py`, `rejony_aus_brec`). 748 von 749 rejony haben
  eine Zeile in der NSP-Tabelle; der eine ohne Zeile bekommt keine Werte. Regeln vor dem ersten Lauf in
  `pruefen/D4_protokoll.md` (Änderungen vom 17.11.2026), Beleg `belege/D4_bevoelkerung.md`.
- NSP 2021 je dzielnica als Summe der rejony (Zuordnung über einen inneren Punkt); Σ über alle dzielnice = Stadt
  (800.653). Steckbrief der dzielnica zeigt die Werte des Stadtteils und darunter die der delegatura.
- Neue Kartenebene „Volkszählung 2021 je statistischem Bezirk“ (`daten/rejony.js`): Einwohner je km² und drei
  Altersanteile je rejon, Anteile in ganzen Prozent und erst ab 100 Personen. Die Differenzprobe (Rückrechnung
  unterdrückter Werte über die Summen je dzielnica, delegatura, Stadt und ihre Kreuzmengen) ist Teil der Rechnung;
  sie schlug mit Anteilen auf eine Nachkommastelle an, deshalb ganze Prozent.
- Downloads: Ebene `rejony_statystyczne` im GeoPackage ohne OSM-Anteil und als CSV; NSP-Spalten je dzielnica in der
  ODbL-Ebene `dzielnice`.
- Methoden- und Datenseite (pl, en, de) beschreiben Verfahren und Quelle.

### Gemeinsamer Kern mit anderen Städten (16.11.2026)

- Laufzeit-Module, Seitenrahmen und Seitengenerator kommen als Kopie zu festem Commit aus dem gemeinsamen
  Kiezatlas-Kern (`MASCHINE.txt`, `MASCHINE.lock`, `skripte/maschine.py`; KR70). In diesem Repository werden diese
  Dateien nicht von Hand geändert; `pruefen.sh` prüft ihre Prüfsummen.
- Grundgestaltung (`basis.css`) getrennt von den Seitenstilen (`atlas.css`); ausgelieferte Seiten unverändert im
  Aussehen.

### DOI eingetragen (15.11.2026)

- DOI eingetragen (Zenodo): Konzept-DOI 10.5281/zenodo.24254005 (alle Versionen), Versions-DOI
  10.5281/zenodo.24254006 (1.0.0).
  `CITATION.cff` (`doi`, `identifiers`), README, `docs/przekazanie.md`; in `config/krakow.yaml` neuer Schlüssel `doi`
  (die Datenseite in pl, en, de nennt und verlinkt die DOI daraus, ohne ihn gilt der alte Satz) und die DOI in der
  `zitierzeile` (Grafiken und Druck über `daten/ort.js`; die Downloads sind unverändert). Der Rohdaten-Schnappschuss
  hat noch keinen Zenodo-Eintrag; `.zenodo.json` bekommt die Verknüpfung mit ihm.

## 1.0.0 (15.11.2026)

Erste öffentliche Fassung: bereinigter Export ohne Arbeitshistorie (KR50; Lesehilfe und Ersetzungen in `docs/export.md` des Exports). Alle 18 Seiten mit echten Daten, Prüfstand `d5f70c0` grün (65 Prüfungen, 60 grün, 0 mit Befund, 5 übersprungen mit Grund; `belege/pruefstand-20261115-d5f70c0/pruefen.log`). `CITATION.cff` und `.zenodo.json` mit Version 1.0.0; DOI noch nicht vergeben. Bildschirmfotos unter `belege/` stehen unter CC BY 4.0 mit den Vermerken BDOT10k und OpenStreetMap (`belege/README.md`). Die Prüfungen der CI laufen ohne Rohdaten; `pruefen/D7_powietrze.py` hat dafür wie `pruefen/DW_mieszkania.py` den Schalter `--ohne-lauf`.

### Adressen der Repositorys (15.11.2026)

- `config/krakow.yaml`: `repository` gesetzt; Methoden- und Datenseite verlinken das Repository, der Satz „noch nicht
  öffentlich, auf Anfrage“ entfällt (KR69). Die Datenseite folgt jetzt demselben Schalter.
- Anleitungen und Übergabe: Geodaten-Import-Pipeline und Kiezatlas Potsdam sind öffentlich (Apache-2.0), mit
  Adresse, festgeschriebenem Commit und DOI der Pipeline; offen bleibt nur der Rohdaten-Schnappschuss.
- `CITATION.cff`: `repository-code` und Eintrag der Pipeline unter `references`; `.zenodo.json`: `related_identifiers`.

### Polnische Texte gegengelesen (15.11.2026)

- Drei Sprachmodelle (Gemini, Claude Sonnet, Codex) haben die polnischen Texte unabhängig gegengelesen; 243 Vorschläge
  zu 178 Stellen, 119 übernommen, 58 verworfen, Grund je Stelle in `docs/entscheidungen/p4b-polnisch.md`. Ein
  muttersprachliches Lektorat ersetzt das nicht; der Hinweis auf den Seiten bleibt.
- Planer: „dostępność usług“ statt „zaopatrzenie“, Gruppe „Usługi i zdrowie“; RSPO mit amtlichem Namen „Rejestr
  Szkół i Placówek Oświatowych“; „niepewne“ statt „nieostre“; Verweis auf die Karte als strona „Mapa”; „nie“ mit
  Partizip zusammengeschrieben; Glossar um die vereinheitlichten Begriffe ergänzt.
- `dane.html` (pl, en, de): das Denkmalregister hat eine eigene Ebene (`rejestr_zabytkow`); der Satz sagte das Gegenteil.
- Downloads neu erzeugt (Feldbeschreibungen in `pola.csv`, GeoPackages, CZYTAJ). Filme unverändert, kein Untertitel
  betroffen. Prüfstand `7ef6874` grün (65 Prüfungen, 60 grün, 0 mit Befund, 5 übersprungen;
  `belege/pruefstand-20261115-7ef6874/pruefen.log`).

### Abnahme vor der Veröffentlichung (15.11.2026)

Die Zweige mit der Nacharbeit, den Filmen und der Veröffentlichung sind zusammengeführt (Konflikte in `CHANGELOG.md`,
`skripte/oeffentlich_ausnahmen.tsv` und `skripte/oeffentlich_pruefen.py` inhaltlich gelöst); Verbleib jedes
Abnahme-Funds in `docs/entscheidungen/review-p4b.md`, neue Entscheidungen als Vorschlag KR63 bis KR68.

- Filme: Lizenz CC BY 4.0 wie die Bildschirmfotos (KR63); neu aufgenommen mit der OSM-Kennzeichnung ohne Ocker
  (KR64), polnischen Untertiteln ohne Lehnübertragungen und der wörtlichen RCN-Nennung auf der Quellentafel.
- Karte: OSM-Kennzeichnung der Denkmale hell mit violettem Rand wie auf `modernizacja`, kein Orange mehr.
- `./pruefen.sh` ohne Rohdaten: Luft und Wohnungsmarkt prüfen die Dateien im Repository, die Neurechnung zählt als
  übersprungen (KR68); `docs/running.md` und `docs/uruchomienie.md` §8.
- `NOTICE`: Luft, Wohnungsmarkt und Denkmalregister sind echte Daten; EEA (CC BY 4.0), RCN (Quellenangabe) und
  Wikidata (CC0) mit Nennung.
- Keine Ordner des Arbeitsrechners mehr in Tilde-Form (`quellen-DZ.md`, `pruefen/a3_gegenprobe_gdal.py`);
  `skripte/oeffentlich_pruefen.py` erkennt sie.
- Rohdaten-Schnappschuss (`skripte/schnappschuss.py`): EEA-Auszug (CC BY 4.0) und Wikidata-Ergebnis (CC0) aufgenommen,
  RCN-Einzeltransaktionen mit Grund ausgeschlossen (KR65); Inhalt laut Trockenlauf 404.127.036 B, Größe in
  `docs/running.md` und `docs/uruchomienie.md`.
- Auslieferung: die Deploy-Kopie entsteht aus dem veröffentlichten Stand, nach dem Eintragen von DOI und
  Repository-Adresse (`docs/auslieferung.md`).
- KR33 mit Nachtrag zur zweiten Sichtprüfung; Liste „Nicht geprüft“ nachgezogen.

### Nacharbeit zur Sichtprüfung, Typologie, Repository-Link (15.11.2026)

- Gegenprobe des Merges: `skripte/dz_denkmale.py` meldet kaputte Eingaben der Sichtprüfung (kein JSON, falsche Form,
  ungültiges Datum) mit Rückgabe 5 statt eines Tracebacks; der Beleg lässt sich auch schreiben, wenn keine Ansicht
  entschieden ist (Intervall „–“). Echte Daten byte-gleich.
- `skripte/16_bloecke_krakow.py`: Bedingung `[[wenn …]] … [[sonst]] … [[ende]]`. Ohne `belege/DZ_sichtpruefung.json`
  fallen die Langtexte auf die Sätze „ungeprüft“ zurück, statt abzubrechen (`pruefen/S4_bloecke.py`, Teil 9).
- Methode (Seite und Unterseite Kamienice): die Typologie-Stichprobe ist nicht mehr „noch nicht ausgewertet“, sondern
  nennt das Ergebnis vom 14.11.2026 aus `daten/sanierung.js`.
- `config/krakow.yaml`: `repository` (leer). Mit Adresse verlinkt die Methodenseite das Repository
  (`docs/auslieferung.md`, „Nach der Veröffentlichung des Repositorys“).
- Doku: DE6 (Nachtrag), `quellen-DZ.md`; Bildschirmfotos `belege/bildschirm-20261115/` neu.

### Drei kurze Filme auf Polnisch (15.11.2026)

- `skripte/filme.mjs` nimmt drei Filme aus den echten Seiten auf (headless Chromium über den Entwicklungsserver,
  1280 × 720, ohne Ton): „Atlas w minutę“ (Start, Karta mit Ebenen, Profil einer dzielnica, Kraków i Poczdam),
  „Kamienice i zabytki“ (Kamienice, Sichtprüfung als Beleg, Karta mit Register und OSM-Kennzeichnung), „Dane, nie
  opinie“ (Luft vorher/nachher nur zeitlich, Wohnungsmarkt mit Mindestfallzahl, Methode, Daten und Lizenzen).
- Untertitel und Texttafeln als Einblendung in der Seite (Barlow, Farben aus `DESIGN.md`), WebVTT pl/en/de; Zahlen
  in Untertiteln aus den Datendateien. MP4 (H.264, CRF 28) und WebM (VP9) unter `belege/filme/`, je Datei unter 5 MB;
  Drehbuch, Dauer, Größe und SHA256 in `belege/filme/README.md`. Polnische Texte nicht muttersprachlich geprüft.
- `skripte/oeffentlich_pruefen.py` zählt `.vtt` als Text; die Filme haben eine Lizenzregel wie die Bildschirmfotos
  (vor der Veröffentlichung festlegen).

### Denkmale: zweite Sichtprüfung ausgewertet (15.11.2026)

- Eingabe `belege/DZ_sichtpruefung.json` (40 Punkte der Stichprobe mit Startwert 20261114, Ortofotomapa Geoportal,
  Quelle je Punkt verdeckt). Regel vor dem Rechnen in `pruefen/DZ_protokoll.md`, Nachtrag 4: Lage-Quote = ja / alle
  („daneben“ zählt nicht als ja), Ansicht-Quote = ja / entschiedene, Wilson 95 %.
- Ergebnis: Lage auf dem Objekt Wikidata 17 von 20 (85 %, Wilson 64–95 %), OSM 16 von 20 (80 %, 58–92 %), gesamt
  33 von 40 (82,5 %, 68–91 %); Ansicht passt in 18 von 18, 17 von 17 bzw. 35 von 35 entschiedenen Fällen.
- `skripte/dz_denkmale.py` liest und prüft die Eingabe (Rückgabe 5, wenn sie nicht zur Stichprobe passt) und setzt
  `sichtpruefung.geprueft: true` mit Datum, Art der Prüfung (kein Name) und Quoten; Wikidata in `denkmale.js`, OSM und
  gesamt in `denkmale_odbl.js`. Ohne Eingabe bleibt alles wie bisher (geprüft: byte-gleich). Verträge
  `denkmale.json` und `denkmale_odbl.json` mit zwei Varianten (geprüft / ungeprüft).
- Seiten: Hinweis „Lage ungeprüft“ auf `kamienice`, `karta` und `modernizacja` durch die Quote aus den Daten ersetzt
  (Abzeichen, Legende, Quellen, Grenzen, Popups; Methode und Daten); bei `geprueft: false` bleibt der Hinweis. Die
  Zuordnung zum Gebäude heißt weiter ungeprüft. Prüfungen `pruefen/DZ_denkmale.py`, `S1_seiten.mjs`, `S2_seiten.mjs`
  verlangen je nach `geprueft` die Angabe oder den Hinweis.
- Downloads: Titel der Ebenen `rejestr_zabytkow` und `osm_heritage_start_date` und Abschnitt „Grenzen“ im Liesmich
  nennen das Ergebnis; `polozenie_sprawdzone` bleibt je Punkt 0 (geprüft ist die Ebene in einer Stichprobe, nicht
  der Punkt), Feldbeschreibung entsprechend.

### Behebung der Sichtung vor der Veröffentlichung (15.11.2026)

Zusammengeführt aus vier Zweigen (Denkmale, Gestaltung, Sprache, Betrieb); Verbleib jedes Sichtungsfunds in
`docs/entscheidungen/review-p4a.md`, Entscheidungen als Vorschlag KR57 bis KR62.

- Gestaltung: feste Marke „Beispieldaten“ an den echten EEA-Stationen entfernt, neue Prüfung
  `pruefen/beispielmarke.py`; ein Satzspiegel (1280 px) für alle Seiten; Kopfleiste mit den Rubriken „Tematy“ und
  „Metodologia“, Themen der Startseite als Kacheln; Inhaltsverzeichnis der Methodenseite; jeder abweichende Nenner der
  Gitter-Einwohnersummen erklärt; Kamienice-Legende startet eingeklappt, Bauzeit-Chips lesbar; Dostępność startet mit
  Frage 1; Powietrze wählt eine Station mit langer aktueller Reihe vor; ZBK-Haftungsausschluss als benannter Block.
- Sprache (pl): „udział powierzchni zabudowy“ statt „intensywność zabudowy“ (GFZ); Prozentzeichen nach Landesbrauch,
  echtes Minuszeichen; „© autorzy OpenStreetMap“; wielka płyta, osiedle blokowe, eksploatowany, kompleksy,
  95-procentowy przedział ufności; Stichtag der NSP 2021 als „stan na“; Rechtsquelle der Luft-Grenzwerte mit Datum und
  tekst jednolity; Germanismen und Lehnübersetzungen ersetzt.
- Betrieb: Schritt `02a` in der Kette, Kartenschrift Noto Sans im Repository (`schriften/noto/`, OFL), EEA-Eingang
  als GeoJSON(-ZIP) oder CSV; Anleitungen für eine Hochschule ohne Rückfrage (KIEZ_DATEN, Installationswege,
  Systembibliotheken für Playwright, Grenzen der Reproduzierbarkeit); Methode und Daten sagen, dass das Repository noch
  nicht öffentlich ist; Layoutsprünge beim Laden unter 0,1.
- Integration: Konflikte inhaltlich gelöst (je Merge-Commit begründet), erzeugte Dateien neu erzeugt; Schlüssel
  `kamienice.q_ungenutzt` entfällt (das Register wird jetzt geladen); Übergabe und Checkliste nennen EEA und RCN als
  heruntergeladen (Altfehler). Bildschirmfotos neu (`belege/bildschirm-20261115/`).

### Denkmalregister aus Wikidata auf den Seiten (14.11.2026, nachts)

- Kamienice: Zahlen aus `denkmale.js` je Delegatura neben der OSM-Kennzeichnung (1.214 Registerpunkte in der
  Stadt, davon 571 in einem Mehrfamilienhaus laut BDOT10k). Die Kennzahl heißt „Registerpunkte (Wikidata-Objekte mit
  Registernummer, gleiche Nummer als ein Punkt)“: 1.909 Objekte ergeben 1.214 Punkte (A-893 hat 56 Objekte).
  Grenzen, Quellen, Abzeichen, Seitenbeschreibung, Methode und Daten in pl/en/de nachgezogen.
- Karte: neue Punktebene „Denkmalregister aus Wikidata“ (`pkt=rejestr`, Vermerk „Wikidata, CC0 1.0“), getrennt von
  der OSM-Kennzeichnung (`pkt=zabytki`, ODbL; alte Links zeigen weiter OSM). Je Ebene Zahl, Quelle und Hinweis
  „Lage ungeprüft“. Tabelle auf `kamienice`, Ebene der Karte und `zaehlung.wd.in_stadt` sind dieselbe Menge
  (geprüft in `pruefen/S1_seiten.mjs` und `pruefen/S2_seiten.mjs`).
- Downloads: Ebene `rejestr_zabytkow` im GeoPackage ohne OSM-Anteil, mit CC0-Vermerk in `licencje`.
- Zweite Stichprobe zur Sichtprüfung (Startwert 20261114, je 20 Punkte aus Wikidata und OSM aus der Menge der Karte,
  nur Lage und Ansicht): `belege/DZ_sichtpruefung_stichprobe.json` und `belege/DZ_denkmale_lauf.md`, Regel in
  `pruefen/DZ_protokoll.md` (Nachtrag 3). Nicht ausgewertet; `sichtpruefung.geprueft` bleibt `false`.
- Datenvertrag `denkmale.json`: `quellen.wd.vermerk`, `sichtpruefung`.
- Altfehler: Auf der Karte stand neben „Messstationen Luftqualität“ fest die Marke „Beispieldaten“, obwohl
  `powietrze.js` echt ist.

### Wohnungsmarkt ab 2019, Kamienice-Texte (14.11.2026, nachts)

- Wohnungsmarkt (KR55): Eine unabhängige Prüfung fand 42 von 74 unterdrückten Fallzahlen mit nur zwei möglichen
  Werten, alle in den Jahren 1900 bis 2018. Neuer Schritt F11: veröffentlicht werden nur Jahre ab 2019
  (`regeln.erstes_jahr`), 14 Käufe davor entfallen. Primär unterdrückt jetzt 32 Felder, Spannenprobe 0 von 32
  (Erzeuger und unabhängige Rechnung, `belege/DW_spannenprobe.md`); 371 Mediane je dzielnica und 24 der Stadt sowie
  27 verdeckte Fallzahlen unverändert. Die Seite sagt „Daten ab 2019“; der Satz zu ausgeblendeten Jahren entfällt.
  Jahresgrenzen im Beleg kommen aus den Zählungen; was fest im Text steht, nennt `docs/rundgang.md`.
- KR56: Nachtrag 4 zu Regel 4 (Verdeckung mehrerer Felder) bestätigt; Durchsicht der Funktion ohne Befund.
- Kamienice: Texte nannten `denkmale.js` „Beispieldaten“; jetzt „Registerdaten aus Wikidata liegen vor (Stand
  14.11.2026), auf dieser Seite noch nicht eingebunden“ (pl/en/de).
- Bildschirmfotos aller Seiten neu (`belege/bildschirm-20261114/`).

### Nachprüfung der echten Daten (14.11.2026, spät)

- Wohnungsmarkt: Datenstand ist das jüngste Dokumentdatum der Datei (29.09.2026), wie im Protokoll; vorher das
  jüngste der ausgewerteten Käufe (25.09.2026). Der Beleg nennt den Widerspruch zum Geoportal-Datum 21.09.2026.
- Wohnungsmarkt: Die Grenze „belastbar ab 2016/2017“ stimmte nicht mit der gezeigten Reihe überein (sie beginnt
  2019). Neu: Werte der ganzen Stadt erst ab 2021 weitgehend vollständig; 2019 und 2020 beruhen nur auf einem
  Teil der Käufe (Anteile je Jahr im Beleg).
- Luft: Kopf von `daten/powietrze.js` sagt „in Kraków“, wenn keine Umland-Station enthalten ist; die Spalte
  „Abstand“ und die Umland-Sätze nennen den Mittelpunkt der Stadtstationen statt „Zentrum“ (Altfehler).
- Startseite: Satz zur Luftseite in PL und EN im Präsens.
- Doku: Rundgang (Handdownloads Luft und Wohnungsmarkt, Zählung der Wikidata-Objekte), `quellen-DW.md`
  (Ausgabedatei `mieszkania_odbl.js`, Datenstand).
- Prüfstand `belege/pruefstand-20261114-d18c434/pruefen.log` grün (mit Gegenprobe Potsdam).

### Echte Daten für Luft, Wohnungsmarkt und Denkmalregister (14.11.2026, abends)

- Luft: EEA-Statistik als GeoJSON-Handdownload (Filter `City = Kraków`), 10 Stationen, 337 Jahreswerte 2010–2025.
  Das Umland fehlt im Export; Seite und Methode sagen das, die Legende zeigt dann keinen Umland-Eintrag. Vertrag
  kennt `zaehlung.ausreisser_nicht_geliefert`; die Prüfung des Vorher/Nachher-Mittels hat eine begründete Toleranz
  von 0,1 (Mittel aus ungerundeten Werten, Prüfung aus gerundeten).
- Wohnungsmarkt: RCN Powiat 1261 gerechnet. Nach F10 45.701 Käufe, 371 Mediane je dzielnica, Jahr und Markt,
  27 sekundär verdeckte Fallzahlen. Der erste Lauf brach in der sekundären Unterdrückung ab (keine einzelne
  Verdeckung reichte); Nachtrag 4 zu Regel 4 in `pruefen/N1_protokoll.md` regelt die Verdeckung mehrerer Felder,
  vor dem Neulauf festgelegt. Grenzen auf der Seite und im Beleg: belastbar erst ab 2016/2017 (Anteil fehlt bis
  2015), je dzielnica erst ab 2021 (Lage fehlt 2016–2020). Jahre ohne Median der Stadt (z. B. 1900) fehlen in
  Auswahl und Grafik und stehen mit Jahreszahl unter den Grenzen.
- Denkmalregister: `denkmale.js` aus Wikidata (CC0), weiter von keiner Seite geladen.
- Downloads: Liesmich ohne Beispieldateien; Luft, Wohnungsmarkt und Denkmalregister als „noch ohne eigene Ebene“
  genannt. Texte auf Startseite, Methode, Daten und Sanierungsatlas ohne „Beispieldaten“ für Luft und Wohnungsmarkt.
- Prüfungen für Beispiel und echt: Hinweis „Beispieldaten“ auf der Karte genau dann, wenn `fixture: true`;
  Stationsnamen sind Eigennamen; Selbsttests von Luft und Wohnungsmarkt laufen auf beiden Ständen.

### Behebung der Funde vom 14.11.2026

- Drei Behebungen übernommen (Bereiche Daten, Oberfläche, offen; `docs/entscheidungen/fix-*.md`), Vorschläge als
  KR52 bis KR54 (Bestätigung offen):
  - Wohnungsmarkt: keine unterdrückte Fallzahl mehr über F10 oder `ohne_markt` zurückrechenbar (ganzes
    Gleichungssystem mit Schranken, unabhängig nachgerechnet).
  - Entwicklungsserver liefert nur die Freigabeliste der Deploy-Kopie aus, prüft den Host-Kopf und die SHA256 der
    3D-Dateien beim Start; neue 3D-Läufe schreiben `MANIFEST.sha256`, Stand und Prüfsumme in
    `config/gebaeude_3d.json`.
  - Denkmale mit OSM-Relationen; Stichprobe nur aus Treffern mit `heritage`; Kartenebene `zabytki` nur mit
    Denkmalangabe.
  - Sanierungsatlas: kein Projektname an der Ortsmarke, angebaute Kandidaten gesondert, Sichtprüfung der Stichprobe
    eingetragen; ZBK-Werte überall mit Vermerk und Haftungsklausel der Gmina Miejska Kraków; Vorspann von
    `modernizacja` sagt, dass die Seite Bestand und Typologie zeigt, nicht Sanierungsbedarf.
  - Oberfläche: Zellen ohne Wert grau statt schwarz (Schwelle aus der Ortskonfiguration), kein Satz „w
    przygotowaniu“ mehr auf Seiten mit Daten, Vergleichstabelle bei 360/390 px, Legende der Zellfarben im Steckbrief,
    polnische Begriffe „delegatura (dawna dzielnica)“ und „przystanek klasy I lub II“ zur Prüfung im Glossar.
  - Betrieb: Sicherheits-Header als Vorschlag in den Anleitungen, GSAP nicht mehr ausgeliefert, NOTICE zu Barlow,
    versionsgenaue npm-Angaben belegt, Anleitungen an die Rolle Betreiber gerichtet.
- Integration: Lizenzregel der Prüfung vor Veröffentlichung nur über genaue Namen; `pruefen/DF_kerning.py` ist eine
  Prüfung in `pruefen.sh` (Rückgabe 1 bei einem verlorenen Paar). JavaScript-Startgewicht der Startseite
  287.089 B gz; mit HTML und CSS 314.482 B gz (ohne Schriften und Kacheln), die Grenze von 300 KB gilt damit nur für
  JavaScript (KR39, offen).
- Kleine, nicht behobene Funde der Durchsicht: `docs/entscheidungen/review-20261114.md`.

### Nacharbeit nach den Entscheidungen vom 14.11.2026

- Entscheidungen KR28 bis KR44 bestätigt, bei KR30, KR31, KR39, KR40, KR42 und KR43 mit Auflagen; die Auflagen sind
  umgesetzt (Pakete Daten-Nacharbeit, Oberfläche und Auslieferung):
  - Datenpakete liefern Felder (`radius_m`, `vorbehalte`, `zuordnung` mit den Anteilen III und XV u. a.) statt
    deutscher Sätze; `mieszkania.js` heißt `mieszkania_odbl.js`, Fallzahl unter 10 nur als „n < 10“, dazu sekundäre
    Unterdrückung der Summe; eine gemeinsame Ortsmarke ul. Kościuszki 18 in `denkmale_odbl.js` und
    `sanierung_odbl.js` (KR46).
  - Sanierungsatlas: private Einträge nur gezählt, Punkte nur an öffentlichen Gebäuden ab 3 Geschossen laut BDOT10k.
  - Startseite mit vereinfachten Stadtteilgrenzen (`daten/stadtteile_uebersicht_odbl.js`, 10 m, Abdeckung gültig):
    JavaScript der Startseite 286.168 B gz statt über 300 KB.
  - Kerning der polnischen Sonderzeichen aus den Grundbuchstaben übertragen (`skripte/schriften.py`, byte-gleich);
    `pruefen/DF_kerning.py` misst in allen fünf Schriften 0 Paare ohne Wert.
  - Gebäude in 3D über Entwicklungsserver und Deploy-Kopie aus `abgeleitet/gebaeude/2026-11-13-odbl/`, gegen das
    Manifest geprüft und aus den Rohdaten byte-gleich nachgerechnet.
  - Zweite Fassung des Beispieldaten-Hinweises für nachgeladene Beispieldaten; `Map.Title` je Sprache;
    Bildzeile der Stadtteilgrenzen je Sprache; Kopfleiste bis 360 px ohne abgeschnittene Links.
- Offene Wissenschaft: Anleitungen zum Selbstbetrieb und zu einer neuen Stadt (pl, en), Übergabe
  (`docs/przekazanie.md`), ein Befehl für die Kette (`./atlas.sh`), Rohdaten-Schnappschuss (nur lokal), Prüfung vor
  Veröffentlichung (`skripte/oeffentlich_pruefen.py`), CI-Vorlage, `.zenodo.json`, `NOTICE` neu gefasst.
- Vorschläge der drei Pakete als KR45 bis KR51 (Bestätigung offen); neue Prüfungen in `pruefen.sh`
  (`pruefen/N1_daten.py`, Übersichtsgrenzen, Prüfung vor Veröffentlichung, `pruefen/N2_auslieferung.mjs`, 3D mit
  `--voll`).

### Seiten mit echten Daten (14.11.2026)

- Vier Seitenpakete übernommen: Startseite als Erzählung, freie Karte mit allen Ebenen, Steckbrief je dzielnica,
  Vergleich Kraków–Potsdam aus dem Eurostat-Gitter (`daten/porownanie.js`); Erreichbarkeit, Kamienice und neue Seite
  `modernizacja` (Sanierungsatlas Wohnungsbestand) mit 3D-Gebäuden auf Wunsch; Themenseiten Luft, Wohnungsmarkt und
  Klima; neue Seiten `metoda` und `dane`, Downloads unter `daten/pobierz/` (GeoPackage, CSV, QGIS-Projekt,
  Liesmich pl/en/de). 18 Seiten je Sprache.
- Seitenmodul der freien Karte `karta.js` (im Paket `kartenseite.js`, Namensgleichheit mit dem Unterbau der
  Kartenseiten); Seite `klimat` lädt den Namensraum `erzaehlung` für `kartenfeld.js` und baut ihre Karte über
  `KIEZ_KARTENFELD.bauen` (seit `kartenfeld.js` eine Bibliothek ist, blieb die Karte sonst leer); Seitenfuß nennt den
  ODbL-Vermerk auch bei Werten aus `_odbl`-Dateien in Langtexten.
- Vorschläge der Seitenpakete als KR36 bis KR44 (Bestätigung offen); Paketprüfungen in `pruefen.sh`; Quellen des
  Vergleichs in `QUELLEN.md`; Bildschirmfotos aller Seiten (pl, 1440 und 390 px) unter `belege/bildschirm-20261113/`.

### Echtlauf, Sanierungsatlas, Schrift und Grundkarte (13.11.2026 abends)

- Entscheidungen der Projektleitung: KR13 bis KR24 bestätigt; Lizenzfolge der OSM-Grenzen Variante a (Werte je
  dzielnica als `_odbl`-Dateien), Gruppenzuordnung III und XV mit Ausnahme, LoD2-Höhen veröffentlicht, EEA als
  CC BY 4.0, WDQS erlaubt (aber durch robots.txt gesperrt); neu KR25 bis KR27.
- Alle Themen mit den vorhandenen echten Daten gerechnet; umbenannt `zellen.js` → `zellen_odbl.js`,
  `kennzahlen.*` → `kennzahlen_odbl.*`, `planer.js` → `planer_odbl.js`. Beispieldaten bleiben nur Luft,
  Wohnungsmarkt und Denkmalregister (Handdownloads fehlen).
- Neues Thema Sanierungsatlas Wohnungsbestand (`daten/sanierung.js`, `sanierung_odbl.js`).
- Schriften mit allen polnischen Sonderzeichen; Grundkarte auf der Seite `karta` in allen drei Sprachen.
- Vorschläge der Pakete als KR28 bis KR35 übernommen (Bestätigung offen); Quellen aller Pakete in `QUELLEN.md`,
  Lizenzen je Datei in `daten/LIZENZ.md`, alle Belege in `belege/README.md`; Paketprüfungen in `pruefen.sh`
  (`--voll` für die Neurechnung aus den Rohdaten).

### Belegschicht (13.11.2026)

- `docs/checkliste.md`: Stand gegen den Belegstandard Punkt für Punkt (36 Punkte, zehn Audit-Lehren, fünf
  Zusatzauflagen), jede Zeile mit Status und Beleg.
- `pruefen/belege.py` in `pruefen.sh`: Belege, README-Kasten, Entscheidungen, Meldeweg und Checkliste in sich
  stimmig; nicht übernommene Lieferungen der Pakete als Hinweis.
- `pruefen/hreflang.py` in `pruefen.sh`: hreflang, canonical und Sprachschalter auch ohne Browser.
- Entscheidung KR11 (Themen nach Datenlage), Kürzeltabelle, polnische Fassung von „Nicht belegt“ und „Nicht
  geprüft“, Abschnitte „Neuer Datenstand“ und „Einsammeln“ im Rundgang, gesperrte Wege in `QUELLEN.md`.
- KR10 und das Ergebnis der Gegenprobe auf den maßgeblichen Lauf gegen `291befb` gebracht.

### Gerüst (13.11.2026)

- Code aus dem Kiezatlas Potsdam übernommen (Stand `7b6eb08`), ohne dessen Historie und Daten.
- Ortskonfiguration `config/krakow.yaml` → `daten/ort.js` (`skripte/31_ort.py`); Rechen-Koordinatensystem als
  Parameter `rechen_srid` (EPSG:2178).
- Textschicht `i18n.js` mit `t()`, Plural und Zahlformaten; Texte in `texte/pl|en|de/`.
- Seitengenerator `skripte/30_seiten.py`: 15 Seiten in Polnisch, Englisch und Deutsch mit hreflang und Sprachschalter.
- Beispieldaten für 18 dzielnice (`fixture: true`, auf den Seiten gekennzeichnet).
- Prüfkette `pruefen.sh` mit Seiten-, Text- und Datenprüfung; Gegenprobe gegen den Potsdamer Stand.
- Dokumentationsschicht leer angelegt.
