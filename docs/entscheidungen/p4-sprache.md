# Behebung der Sprachfunde vom 14.11.2026 (Bereich „sprache“)

Stand 14.11.2026, Zweig `Arbeitszweig p4-sprache` (von `main` `327505f`). Zwei Durchsichten haben die polnischen Texte
geprüft: eine fachliche (Planungsrecht, Statistik, Quellen; im Folgenden „F“) und eine sprachliche (Stil,
Grammatik, Einheitlichkeit; „S“). Jeder Fund ist vor der Änderung im Repo nachgeprüft worden. Wo beide Durchsichten
dieselbe Stelle betreffen, steht der Fund einmal mit beiden Nummern. Wo sie sich widersprechen, ist mit einer
Primärquelle entschieden; die Quelle steht beim Fund.

Keiner der Texte ist muttersprachlich gegengelesen. Der Hinweis darauf bleibt auf der Seite Metodologia stehen
(jetzt „nie zostały jeszcze przeczytane przez rodzimych użytkowników języka“), das Glossar behält den Status
„Vorschlag“ für alle Einträge. Nummern und Status in `docs/entscheidungen.md` setzt die Belegschicht; dieses Dokument
schlägt keine neue Entscheidungsnummer vor.

## 1. Entscheidungen bei Widersprüchen

| Frage | F schlägt vor | S schlägt vor | Entscheidung und Beleg |
|---|---|---|---|
| Namensnennung OpenStreetMap | „© współtwórcy OpenStreetMap“ | „© autorzy OpenStreetMap“ | **autorzy.** openstreetmap.org/copyright/pl: „np. w postaci „© autorzy OpenStreetMap””; polnische OSM-Oberfläche `config/locales/pl.yml`, Schlüssel `openstreetmap_contributors: autorzy OpenStreetMap` (beide nachgesehen am 14.11.2026) |
| Prozentzeichen | mit Leerzeichen, `fmt.anteil` nachbearbeiten | ohne Leerzeichen wie `Intl` | **ohne Leerzeichen.** `Intl.NumberFormat("pl-PL", {style: "percent"})` gibt „1%“ (CLDR), `de-DE` „1 %“. `i18n.js` ist ein eingefrorener Vertrag („Zahlen nach Landesbrauch, nie selbst formatieren“), die Langtexte formatieren über dieselbe Funktion. Die Glossarregel „mit Leerzeichen“ stammte aus „Wissen“ und widersprach der eigenen Formatierung; sie ist angepasst. `atlas.js` und `schaugrafik.js` (Potsdamer Stand) hängen zwar NB + „%“ an, werden aber von keiner Krakauer Seite geladen |
| BDOT10k-Status | „eksploatowany“ | „w użytkowaniu“ | **eksploatowany.** Das ist der Wert des Merkmals `KAT_ISTNIE`, auf den `36_sanierung.py` filtert (`a["KAT_ISTNIE"] == "eksploatowany"`) |
| Komplexe der BDOT10k | (nicht genannt) | „zespoły“ überall | **kompleksy.** Ebene `bdot_kompleksy` im Download, Feldbeschreibungen „rodzaj kompleksu“, EN „complexes“, DE „Komplexe“; „zespół zabudowy historycznej“ bleibt als Art |
| Stichtag der NSP 2021 | „moment krytyczny spisu“ | „moment krytyczny spisu“ | **„stan na …“.** Das Gesetz (Ustawa z dnia 9 sierpnia 2019 r. o narodowym spisie powszechnym ludności i mieszkań w 2021 r., art. 1 ust. 2, Text über api.sejm.gov.pl DU/2019/1775) sagt „według stanu na dzień 31 marca 2021 r., godz. 24.00“. „moment krytyczny“ steht dort nicht; als GUS-Methodenbegriff im Glossar vermerkt |
| Gitterzahl in der Startseitenfrage | „Według siatki … mieszka {gitter} mieszkańców“ | „daje {gitter} mieszkańców“ | **„liczba mieszkańców … wynosi {gitter}“**: stimmt für jede Zahl, ohne Wiederholung von mieszka/mieszkańców |

## 2. Funde und Ergebnis

| Nr | Fund | Nachprüfung | Ergebnis |
|---|---|---|---|
| F1 = S1 | „intensywność zabudowy“ für den Anteil der Gebäudegrundfläche (blockierend) | bestätigt: `erzaehlung.dz_bebauung` und `register_quelle`; der Download nutzt „intensywność“ richtig für die GFZ-Näherung (`geb_geschossflaeche_naeherung_wert`) und „wskaźnik zabudowy“ für den Anteil | behoben `6bfde9f`: „udział powierzchni zabudowy budynkami“, Quellenzeile „Budynki i udział powierzchni zabudowy“; Glossar trennt Bebauungsanteil und GFZ-Näherung. EN „building coverage“ war richtig; DE „Bebauungsdichte“ ist unscharf, aber kein falscher Fachbegriff, unverändert |
| F2 | Download-Ebene „dawne dzielnice historyczne“, EN „historic districts“ | bestätigt (`16_export_krakow.py:344`, gegen Glossar) | behoben `ce0f56b`: „Cztery delegatury (dawne dzielnice)“, „Four delegatury (historic boroughs)“; CZYTAJ und Pakete neu erzeugt |
| F3 = S13 | Prozentzeichen uneinheitlich | bestätigt: `fmt.anteil` ohne, NB + „%“ in `erzaehlung.js`, `dzielnica.js`, `karta.js`, `vergleich.js`, `erreichbarkeit.js` mit Leerzeichen; Vorlagen mit „ %“ | behoben `f8cea50` nach Abschnitt 1: Seitenmodule nehmen das Zeichen aus `fmt.anteil` (pl, en ohne, de mit geschütztem Leerzeichen, de unverändert), Vorlagen in pl und en ohne Leerzeichen (en hatte denselben Fehler); Glossarregel angepasst. Die Vorlagen „{proc}%“ usw. in `powietrze.js` waren damit schon richtig |
| F4 = S12 | „przedział Wilsona“ ohne „ufności“; Spannen verschieden geschrieben | bestätigt | behoben `c47b4bb`: „95-procentowy przedział ufności (metoda Wilsona)“, im Methodentext „95-procentowy przedział ufności Wilsona: a–b“ statt „95 %: a do b“; `c89bbe1` lässt den polnischen Namen in der Prüfung der Langtexte zu (die Ziffer 95 galt sonst als Zahl von Hand) |
| F5 = S14 | „bloki z prefabrykatów“ neben „bloki z wielkiej płyty“ | bestätigt (`seiten.modernizacja.beschreibung`) | behoben `c47b4bb`; Glossar: blok z wielkiej płyty. Ob „kandydaci na bloki“ besser „budynki typowane jako bloki“ heißt (S14, unsicher), steht unter „Zur Prüfung zuerst“ |
| F6 = S11 | „osiedle“ für ein einzelnes Gebäude; „w osiedlach bloków“ | bestätigt (Regeltext, Methode, Tabellen) | behoben `c47b4bb`: „Blok na osiedlu blokowym: kandydat, wokół którego …“, durchgehend „na osiedlach blokowych“, auch in den Feldbeschreibungen des Downloads („na osiedlu blokowym“ statt „w wielkim osiedlu“) |
| F7 = S2 | „daje 793 392 osób“ | bestätigt (Zahlwortrektion, Platzhalter) | behoben `0ad0ebe` nach Abschnitt 1 |
| F8 | Rechtsquelle der Grenzwerte ohne Datum, nicht nach Zitierstandard | bestätigt; ELI-Metadaten (api.sejm.gov.pl, 14.11.2026): DU/2021/845 ist das Obwieszczenie mit dem tekst jednolity des Rozporządzenie vom 24.08.2012 (DU/2012/1031) | behoben `46fe77a`: „Rozporządzenie Ministra Środowiska z dnia 24 sierpnia 2012 r. … (t.j. Dz. U. z 2021 r. poz. 845), załącznik nr 1“ in pl, en und de (polnischer Titel wörtlich). **Verworfen** für die Kurzform je Zeile in `daten/powietrze.js` („Dz.U. 2021 poz. 845, …, lp. 7“): der Vertrag `daten/schema/powietrze.json` legt dieses Muster fest (Probelauf: `D7_powietrze.py` meldet es), und es ist die `displayAddress` der ELI-Daten. Ebenso Prawo geodezyjne (DU/2026/1389, laut ELI tekst jednolity) und Prawo oświatowe (DU/2026/820, tekst jednolity) in Vermerken der Datenpakete: siehe Abschnitt 3 |
| F9 = S19 | „15–64 lat“ | bestätigt; die übrigen Altersspannen des Downloads enden auf 9 („lat“ richtig) | behoben `0ad0ebe` in `erzaehlung.*` und `gitter_a15_64` |
| F10 = S23 (Teil) | „w użytkowaniu“ neben „w eksploatacji“ | bestätigt | behoben `c47b4bb` nach Abschnitt 1, auch in der Feldbeschreibung `typ_mfh`; Startseite nennt die Grundgesamtheit („eksploatowanych budynków wielorodzinnych“, `0ad0ebe`) |
| F11 = S17 | OSM-Namensnennung in drei Formen | bestätigt | behoben `c7c337d` nach Abschnitt 1: Kartenbildzeile (`config/krakow.yaml`, `daten/ort.js`), doppelte Vermerke in den Bildzeilen gekürzt („Zabytki: OpenStreetMap“). Die Downloads und Lizenzdateien zitieren das englische Original wörtlich und bleiben (Glossarregel Lizenzvermerke). **Offen:** `VERMERK_OSM_SPRACHEN` in `skripte/36_sanierung.py` (in `daten/sanierung_odbl.js`), Abschnitt 3 |
| F12 = S6 | „dzień odniesienia“, „data referencyjna“; „niesprawdzony“ | bestätigt für die NSP-Texte; „data referencyjna“ in `karte.*` und `planer.ew_quelle` gehört zum deutschen Zensus 2022 (Potsdamer Schlüssel) und bleibt | behoben `9b2f68b` nach Abschnitt 1 („Spis według stanu na …“, „stan na …“, „Daty spisów (stan na)“ im Vergleich). Der Vermerk „data w źródle jeszcze niesprawdzona“ bleibt, solange `daten/steckbrief.js` `stichtag_geprueft: false` trägt; **offen** (Abschnitt 3) |
| F13 = S18 | „kwadrat“ statt „komórka siatki“; „Zieleń i las“ | bestätigt | behoben `fb7c986`, mit Genus („Wybrana komórka …, jej powierzchni“) |
| F14 = S20 | „dopuszczalnie {razy} razy“; „Od {data} w Krakowie“; „okna“ | bestätigt | behoben `46fe77a`: „dopuszczalna częstość przekraczania: … razy w roku kalendarzowym“, „Od 1 września 2019 r.“, „okresu porównawczego“ |
| F15 = S3 | „sprzed i po wejściu“ | bestätigt | behoben `0ad0ebe`: „z lat przed wejściem w życie … i po nim“ |
| F16 (+ S25 Teil) | „native speakerów“, „z liczeniami“ | bestätigt | behoben `742a7b9`: „rodzimych użytkowników języka“, „z obliczeniami“; der Hinweis selbst bleibt |
| F17 | „uszczelnienie gruntu“ oder „zasklepianie gleby“ | als Prüfpunkt bestätigt, ohne Fundstelle für die Krakauer Lehre | **ohne Textänderung**: im Glossar unter „Zur Prüfung zuerst“ (`fb7c986`) |
| F18 = S24 (Teil) | deutsches schließendes Anführungszeichen | bestätigt: `docs/uruchomienie.md` (7×), NSP-Titel aus `02_bevoelkerung.py` | behoben `ce0f56b` (Anleitung) und `886f90c` (Skript geändert, `02_bevoelkerung.py` neu gerechnet: nur das Zeichen ändert sich in `steckbrief.js`, `kennzahlen_odbl.*`; `belege/D4_bevoelkerung.md` byte-gleich; Vergleich und Übersichtsgrenzen mit `--pruefen` byte-gleich) |
| F19 = S10 | „Wikidata“/„Wikidane“; Kamienice zeigt „Wikidata – brak“, obwohl die Grenzen „dostępne“ sagen | bestätigt; der Widerspruch steckte im Code (`kamienice.js` setzte für nid, gez und wd fest „fehlt“) und betraf pl, en, de | behoben `16f3a9f`: neuer Schlüssel `kamienice.q_ungenutzt` („pobrane, jeszcze niewykorzystane“, en, de) für Wikidata; „Wikidane (Wikidata)“ als Quellenname, im Fließtext „Wikidane“; Glossar |
| F20 | offene Klammer „plik (PL_PD_3035_GPKG.zip“ | bestätigt; Ursache: Muster `(\S+\.zip)` in `16_export_krakow.py` nahm die Klammer der Quelle mit, in allen drei Sprachen | behoben `ce0f56b` |
| F21 | ISO-Daten im polnischen Fließtext (Grundkarte, ZBK) | bestätigt | **offen**, Abschnitt 3: beide Texte stehen in Datendateien, deren Erzeuger außerhalb des Repos schreiben |
| S4 | „stoi źródło“, „leży skrypt“, „liczy z“, „leżą obok stron“ | bestätigt | behoben `742a7b9` |
| S5 | „Błąd idzie raczej w górę“, „Terminy obu źródeł“ | bestätigt | behoben `fb7c986`: „Wartość jest raczej zawyżona“, „Daty stanu obu źródeł są różne“ |
| S7 | „w silniejszym kierunku“ | bestätigt (Texte und Feldbeschreibung `fahrten_hvz_je_richtung`) | behoben `742a7b9`: „w kierunku z większą liczbą odjazdów“; Glossar |
| S8 | „Przystanek … ma 78% mieszkańców“, „w promieniu“ für Fußwege | bestätigt; dasselbe „w promieniu“ stand bei Schule und Kindergarten | behoben `742a7b9`: „Udział mieszkańców, którzy mają przystanek … w odległości do … m: … dojściem pieszym, … w linii prostej“, Park ebenso, Schule und Kindergarten „w odległości do“ |
| S9 | zwei Zahlen Mehrfamilienhäuser; „wpisy 508, z tego“ | bestätigt | behoben `0ad0ebe`: „liczba wpisów: …, w tym w Krakowie: …“, „eksploatowanych budynków wielorodzinnych“ |
| S15 | „wybrana część“ | bestätigt | behoben `16f3a9f`: Abzeichen „zbiór niepełny“, Beschreibung „Wybór kamienic i zabytków w dzielnicach: …“ |
| S16 | „trafienie“ | bestätigt | behoben `16f3a9f`: „wpis w rejestrze zabytków przypisany do budynku“, „Obiekty przypisane do budynku BDOT10k“ |
| S21 | „planer“ im sichtbaren Text, „liczy na komórkach“, „status orientacyjnie“ | bestätigt | behoben `742a7b9`: „metodologia dostępności“, „Pliki danych tematu Dostępność“, „Obliczenia dostępności opierają się na …“, „są orientacyjne“ |
| S22 | Frage zum Park, Statuszeile „Cel: bez odległości“, „zawsze dłuższe“, Frage nach älteren Menschen | bestätigt | behoben `742a7b9`: „Gdzie jest daleko do parku?“, eigener Schlüssel `planer.e.status_kein_ziel` (pl, en, de; `planer.e.kein_ziel` bleibt Auswahlwert), „dłuższe od odległości w linii prostej lub jej równe“, „Gdzie udział starszych osób jest największy?“ |
| S23 (Rest) | „mieszana publiczna“; „Kompleksy“/„Zespoły“ | bestätigt | behoben `16f3a9f`: „mieszana, wyłącznie publiczna“ überall; kompleksy nach Abschnitt 1 |
| S24 (Rest) | doppelter Punkt nach dem Eurostat-Zitat; Bindestrich als Minus | bestätigt; der doppelte Punkt stand auch in en und de | behoben `ce0f56b` (Punkt, alle drei Sprachen) und `f8cea50` (Minus „−“ in `a_einwohner`, `sb_ew_spanne`, `vg_pp`) |
| S25 (Rest) | „b.d.“, „ORIENTACYJNIE/WSTĘPNE“, Spaltenköpfe klein, „Kraków-Krowodrza“ neben „Krowodrza“ | „b.d.“, Abzeichen und Spaltenköpfe in Klima und Erreichbarkeit bestätigt; in Kamienice und Modernisierung sind alle Spaltenköpfe klein, dort einheitlich | behoben `20c7bd7`: „brak danych“, „wstępnie“, erster Spaltenkopf groß (Klima, Erreichbarkeit; en ebenso). **Verworfen** für die Namen der delegatury: die Tabellen geben die amtlichen Namen aus den Daten (TERYT/BDOT10k „Kraków-Krowodrza“), die Legende die Kurzform; beides ist richtig |

Zusätzlich gefunden und behoben (`0ad0ebe`): `planer.e.zn.ew_je` „{nenner} obiektów“ hatte dieselbe Zahlwortrektion
wie F7; jetzt „mieszkańcy: …, obiekty w BDOT10k: …“.

## 3. Offen

| Punkt | Grund | Was zu tun ist |
|---|---|---|
| OSM-Vermerk „© współtwórcy“ in `daten/sanierung_odbl.js` | Erzeuger `skripte/36_sanierung.py` schreibt bei jedem Lauf nach `$KIEZ_DATEN/abgeleitet/sanierung/` (außerhalb des erlaubten Schreibbereichs dieser Behebung) | `VERMERK_OSM_SPRACHEN["pl"]` auf „© autorzy OpenStreetMap …“ ändern und mit dem nächsten Lauf neu erzeugen |
| ISO-Daten „stan plików 2026-10-03“ (Grundkarte), „z dnia 2025-12-18“ (ZBK-Vermerk) | Erzeuger `27_grundkarte.py` (Kacheln unter `abgeleitet/`) und `36_sanierung.py`; den wörtlichen BIP-Titel „na dzień 2025-12-01“ ohnehin lassen | Datum im Text mit `fmt.datum` ausgeben oder in den Skripten als „3.10.2026“, „18.12.2025 r.“ schreiben, beim nächsten Lauf |
| `stichtag_geprueft` der NSP 2021 | Datenänderung im Paket Gliederung und Bevölkerung; Fundstelle liegt jetzt vor (Ustawa o NSP 2021, art. 1 ust. 2, DU/2019/1775) | Flag setzen, dann „data w źródle jeszcze niesprawdzona“ und den Satz in „Czego nie sprawdzono“ streichen |
| Zitierform „Dz.U. 2026 poz. 1389“, „Dz.U. 2026 poz. 820“ in Vermerken (`20_bdot10k.py`, `40_mieszkania.py`, `config/richtwerte.yaml`, `planer_odbl.js`) | Vermerke der Datenpakete, Neuberechnung aus Rohdaten; Kurzform ist die ELI-`displayAddress` | mit dem nächsten Datenlauf „t.j. Dz. U. z 2026 r. poz. …“ |
| Lektorat | kein muttersprachliches Gegenlesen | Glossar „Zur Prüfung zuerst“ (neu: Plattenbau-Kandidat, Versiegelung) |

## 4. Eigentum

Geändert im Auftrag der Behebung, Eigentümer laut `docs/rundgang.md`: Texte `texte/pl/*` und die genannten
Schlüssel in en und de (Seitenpakete), Seitenmodule `erzaehlung.js`, `dzielnica.js`, `karta.js`, `vergleich.js`,
`erreichbarkeit.js`, `kamienice.js` (Seitenpakete), `texte/<lang>/bloecke/quelle/` und `skripte/16_export_krakow.py`,
`export_pola_krakow.py` (Paket Methode, Daten, Downloads), `pruefen/S4_bloecke.py` (eine zugelassene Wendung),
`skripte/02_bevoelkerung.py` mit `daten/steckbrief.js`, `kennzahlen_odbl.*` (Paket Gliederung und Bevölkerung, nur
das Anführungszeichen), `config/krakow.yaml` mit `daten/ort.js` (Integration, nur die polnische Bildzeile),
`docs/glossar-pl.md` (Paket Oberflächen-Texte), `docs/uruchomienie.md` (Belegschicht). Nicht angefasst: `i18n.js`
(Vertrag), `atlas.js`, `schaugrafik.js` (Potsdamer Stand), `daten/schema/*`. Erzeugte Dateien nur über die Skripte.

## 5. Prüfung

- `./pruefen.sh` mit Browser am Stand `20c7bd7`: 60 Prüfungen, 52 grün, 1 Befund, 7 übersprungen. Der Befund war
  `35_klimat.py --pruefen`: `belege/dk_klimat.md` trägt die Prüfsumme der Eingabe `kennzahlen_odbl.json`, die sich durch
  das Anführungszeichen (F18) geändert hat; neu gerechnet in `6ab5cbe` (nur die Prüfsumme). Alle sechs Browserprüfungen grün.
- Danach `./pruefen.sh --ohne-browser` am Stand `6ab5cbe` mit diesem Dokument: 60 Prüfungen, 47 grün, 0 Befunde, 13 übersprungen
  (Browser per Schalter, Gegenprobe und Neuberechnung aus den Rohdaten nur mit eigenem Schalter). Die Browserprüfungen
  liefen am Stand davor; seitdem hat sich nur `belege/dk_klimat.md` geändert, das keine Seite lädt.
- Nicht gelaufen: `--voll`, `--gegenprobe`. Die Gegenprobe liest nur `texte/de/*` und gemeinsame Skripte; in de ist die
  Ausgabe der geänderten Seitenmodule gleich geblieben (Prozentzeichen wie bisher mit geschütztem Leerzeichen).
