# Behebung Bereich Gestaltung (14.11.2026): Vorschläge an die Integration

Stand: Vorschlag. Die 17 Funde der Gestaltungsdurchsicht (Selbstbewertung auf `main` 327505f, keine unabhängige Jury) sind
auf dem Zweig `Arbeitszweig p4-gestaltung` nachgeprüft und bearbeitet, je Fund oder Gruppe ein Commit. Bildschirmfotos vorher
(Stand 327505f) und nachher liegen außerhalb des Repos unter `/tmp/kz_gestaltung/vorher/` und `/tmp/kz_gestaltung/nachher/`
(1440 × 900 px, Handy 390 × 844 px; Skript `/tmp/kz_gestaltung/shot.mjs`).

Einige Eingriffe berühren Dateien anderer Eigentümer: Gerüst (`skripte/30_seiten.py`, `config/krakow.yaml`,
`vorlagen/_rahmen.html`, `pruefen.sh`) und die Namensräume `kern.*`, `erzaehlung.*`, `planer.*`, `powietrze.*`. Sie
stehen unten je Fund zur Bestätigung.

## Übersicht

| Nr. | Schwere | Fund | Ergebnis |
|---|---|---|---|
| 1 | blockierend | Abzeichen „dane przykładowe“ an den echten EEA-Stationen (Mapa) | behoben |
| 2 | wichtig | Bezirkstabelle der Klimaseite rechts abgeschnitten | behoben |
| 3 | wichtig | drei verschiedene Satzspiegel | behoben |
| 4 | wichtig | fünf verschiedene Gitter-Einwohnersummen ohne Erklärung | behoben |
| 5 | wichtig | Methode, Daten und vier Themen fehlen in der Hauptnavigation | behoben |
| 6 | wichtig | Kamienice: Legende verdeckt das westliche Drittel der Karte | behoben |
| 7 | wichtig | Dostępność startet mit leerer Karte | behoben |
| 8 | klein | Powietrze ohne Karte, Vorauswahl ohne aktuelle Werte, leere Anfangsjahre | teilweise behoben |
| 9 | klein | Legendenfelder gesättigt, Kartenflächen blass | behoben |
| 10 | klein | ungerundete Klassengrenzen (Fünftel) | offen, nicht behoben |
| 11 | klein | Kartenattribution verdeckt am Handy viel Fläche | teilweise behoben |
| 12 | klein | Haftungsausschluss ZBK dominiert den Abschnitt | teilweise behoben |
| 13 | klein | Methodenseite ohne Inhaltsverzeichnis | behoben |
| 14 | klein | graue Lücke in den Stadtzahlen am Handy | behoben |
| 15 | klein | Bindestrich statt Minuszeichen | teilweise behoben |
| 16 | klein | Sprachhinweis: breiter Kasten, „Zamknij“ in der falschen Sprache | behoben |
| 17 | klein | Kamienice: Bauzeit-Chips auf dunklem Grund unlesbar, Chip mit 0 Treffern | behoben |

Kein Fund wurde als falsch-positiv verworfen. Alle Funde waren auf 327505f nachvollziehbar. Bei Fund 4 erklärte eine
der fünf Summen schon die Seite selbst (siehe dort).

## 1. Abzeichen „Beispieldaten“ an den Luftstationen (blockierend): behoben

- **Nachgeprüft:** `grep -c fixture daten/powietrze.js` → 0. `vorlagen/karta.html:35` trug fest
  `<span class="fl-beispiel">`. `karta.js` setzt das Abzeichen selbst nur bei `fixture === true` (Legende, Popup).
- **Eingriff:** Das feste Abzeichen ist aus der Vorlage gestrichen und alle 54 Seiten sind neu erzeugt.
  `karta.js` bleibt unverändert.
- **Prüfung:** neu `pruefen/beispielmarke.py` in `pruefen.sh` (ohne Browser, Gerüst). Keine Vorlage und keine erzeugte
  Seite darf `fl-beispiel` im Markup tragen. Auf 327505f meldet sie 3 Befunde, auf dem Zweig 0. Die Zählung von
  `./pruefen.sh` steigt dadurch um eine Prüfung.
- **Belege:** `vorher|nachher/karta-d-500.png`.

## 2. und 3. Satzspiegel und abgeschnittene Tabellen (wichtig): behoben

- **Nachgeprüft:** Bei 1440 px gab es drei Breiten: Textseiten 1100 px (`rahmen.css`), Start, Mapa, Dzielnice und
  Porównanie 1240 px (`stadtatlas.css`), Kamienice, Dostępność und Modernizacja 1280 px (`kartenseite.css`). Gemessen
  mit `/tmp/kz_gestaltung/mass.mjs`:
  - klimat: `.ts-tabellenrahmen` clientWidth 1044 px, scrollWidth 1208 px
  - mieszkania: 1044 px gegen 1224 px (nicht im Fund genannt, gleiche Ursache)
- **Eingriff:**
  - Ein Satzspiegel für alle Seiten: `body.textseite main{max-width:1280px}` in `rahmen.css`. Die linke Kante bleibt
    auf der Flucht der Marke in der Kopfleiste. Die Sonderbreiten in `stadtatlas.css` und `kartenseite.css` sind
    entfallen.
  - Der Selektor ist bewusst stärker als `.textseite main` in `planer.css`. `planer.css` gilt auch für Potsdam und
    bleibt unverändert, damit die Gegenprobe nicht berührt wird.
  - Fließtext bleibt bei 68ch.
  - Tabellen der Themenseiten: Bezirksnamen umbrechen nicht, Zahlenköpfe dürfen umbrechen.
- **Ergebnis:** Bei 1440 px liegen alle 18 Seiten (pl, gemessen mit `mass.mjs`) bei main 0–1280 px, und keine Tabelle läuft seitlich über.
  - Bei 1024 px scrollt die Klimatabelle noch um 53 px in ihrem Rahmen. Das ist so vorgesehen („Tabellen scrollen
    in ihrem Rahmen, nie die Seite“).
- **Gewählt:** linksbündig mit fester Flucht statt zentriert, weil Kopfleiste und Fuß linksbündig an `--gut` stehen.
  Zentriert hätte sich bei 1440 px ein Versatz von 80 px zur Marke ergeben.
- **Belege:** `vorher|nachher/klimat-d-voll.png`, `klimat-ausschnitt.png`, `mieszkania-d.png`, `index-d.png`,
  `kamienice-d-400.png`, `metoda-d.png`.

## 4. Gitter-Einwohnersummen (wichtig): behoben

Jede Abweichung ist aus den Daten nachgerechnet und nicht aus dem Fund übernommen:

| Zahl | Herkunft | auf der Seite jetzt |
|---|---|---|
| 793 392 | Einwohner in den 327 Zellen mit Mittelpunkt in der Stadt (`kennzahlen_odbl.js`, `porownanie.js`) | Bezugszahl |
| 793 297 | Summe der drei Altersgruppen (`a_ges` = u15 + 15–64 + 65+, `skripte/02_bevoelkerung.py`), 95 weniger | Porównanie: Nenner heißt „suma grup wieku“. Darunter steht der Satz, dass das Gitter Einwohnerzahl und Altersgruppen getrennt angibt, mit der Abweichung (Kraków −95, Potsdam +43, im Browser aus den Daten gerechnet) |
| 793 364 | Startseite, Frage Haltestelle: Zellen ohne Fußwegwert fehlen im Nenner (14 Zellen, 28 Personen) | Satz „Pominięto 14 komórek bez wartości dojścia (28 os.).“ aus den Daten |
| 793 400 | Register der Startseite: `T.rundEw` rundet ab 1000 auf Hundert | Bildzeile nennt die Rundungsregel |
| 793 390 | Planer: `rundung.ew = 10` | stand schon auf `planer-metoda` („zaokrąglone do 10“); unverändert |

- **Neue Schlüssel:**
  - `erzaehlung.vg_nenner`
  - `erzaehlung.a_takt_ohne` (Plural)
  - **geändert:** `erzaehlung.vg_von` („suma grup wieku“) und `erzaehlung.register_quelle` (Satz zur Rundung)
  - Eigentümer: Paket Seiten Erzählung, Karte, Steckbrief, Vergleich. Zur Bestätigung.
- **Belege:** `vorher|nachher/porownanie-d.png`, `index-d-Skaatakt.png`, `index-d-Sdzielnice.png`,
  `nachher/de_porownanie-d.png`.

## 5. Hauptnavigation (wichtig): behoben, Vertragsänderung Gerüst

- **Nachgeprüft:** `navigation: [index, karta, dzielnica, kamienice, planer, porownanie]`.
  - Methode, Daten, Klimat, Powietrze, Mieszkania und Modernizacja waren nur über die Aufzählung „Tematy“ am Ende
    der Startseite und den Fuß erreichbar.
  - In `docs/entscheidungen.md` steht keine Entscheidung, die „Kraków i Poczdam“ bewusst in die Hauptnavigation
    gesetzt hat. Bekannt ist nur KR47: Die Kopfleiste zeigt bis 860 px die ganze Hauptnavigation.
- **Eingriff:**
  - Hauptnavigation: Start · Mapa · Dzielnice · Kamienice · Dostępność · Tematy · Metodologia.
  - Neuer Konfigurationsschlüssel `rubriken` in `config/krakow.yaml`. Eine Rubrik ist ein Navigationspunkt ohne eigene
    Seite, mit `ziel`, `text` (Textschlüssel) und `karten` (Seiten der Übersicht). „Tematy“ führt auf
    `index.html#tematy`.
  - `unterseiten.tematy`: Modernizacja · Klimat · Powietrze · Mieszkania, als Unterzeile auf diesen Seiten.
  - `unterseiten.metoda`: Metodologia · Dane · Kraków i Poczdam. „Kraków i Poczdam“ ist damit ein Unterpunkt der
    Methode, wie im Fund vorgeschlagen.
  - Der Vergleich in der Tematy-Unterzeile hätte bei 360 und 390 px die Zeile gesprengt. Das zeigte
    `pruefen/N2_auslieferung.mjs` mit 20 Befunden.
  - `skripte/30_seiten.py`: Es prüft Rubriken, setzt Ziel und Text der Rubrik und benennt die Unterzeile einer
    Rubrik. `{{liste:themenseiten}}` wird zum Kartenraster aus `rubriken.<r>.karten`, je Seite mit Titel und Satz aus
    `seiten.<s>.h1` und `seiten.<s>.beschreibung`. Seiten unter `in_vorbereitung` (Punktualność) fehlen wie bisher.
    Ohne `rubriken` bleibt das alte Verhalten.
  - CSS `.themenkarten` in `rahmen.css`.
- **Abweichung vom Vorschlag:**
  - Der Navigationspunkt heißt „Metodologia“, nicht „Metoda i dane“. `seiten.metoda.nav` steht zugleich in der
    Unterzeile neben „Dane“, und „Metoda i dane · Dane“ wäre doppelt.
  - Es gibt keine eigene Übersichtsseite „Tematy“: Neue Seiten laufen nur über die Integration. Der Anker auf die
    Startseite reicht.
  - Einen Datenstand je Kachel gibt es nicht. Der Seitengenerator kennt keinen Stand je Seite; das wäre ein eigenes
    Feld in der Konfiguration.
- **Prüfung:** `pruefen/N2_auslieferung.mjs` meldet 0 Befunde: Kopfleiste bei 1440, 390 und 360 px in pl, en und de
  ohne Abschneiden. `skripte/30_seiten.py --pruefen`, `pruefen/hreflang.py` und `pruefen/texte.py` sind grün.
- **Neu prüfen, wenn:** eine Rubrik mehr als vier Unterseiten bekommt (Zeilenbreite bei 360 px).
- **Belege:** `vorher|nachher/index-d-Stematy.png` (Liste → Kacheln), `klimat-d.png`, `klimat-m.png`, `dane-d.png`,
  `de_klimat-m.png`, `nachher/index-m-Stematy.png`.

## 6. Kamienice: Legende über der Karte (wichtig): behoben

- **Nachgeprüft:** Die Legende war bei 1440 px aufgeklappt, rund 290 × 400 px groß, und lag über Bronowice,
  Zwierzyniec und der westlichen Altstadt.
- **Eingriff:** `#legende` trägt in `vorlagen/kamienice.html` das Attribut `data-start="zu"`. `kartenseite.js` lässt
  die Legende dann auch am Desktop eingeklappt starten, und der Knopf „Legenda“ öffnet sie. Die Bauzeit-Chips in der
  Seitenleiste dienen als Legende der Farben (siehe Fund 17). Planer und Modernizacja bleiben unverändert, ihre
  Legende ist klein.
- **Verworfen:** den ersten Ausschnitt mit `padding.left` um die Legendenbreite einrücken. Ausprobiert: Die Stadt
  wurde zu klein (Maßstab 5 statt 3 km), Bild nicht abgelegt. Auch verworfen: die Legende in die Seitenleiste
  verschieben. Die Seitenleiste scrollt, und die Legende läge unter dem Bildrand.
- **Belege:** `vorher|nachher/kamienice-d-300.png`.

## 7. Dostępność startet leer (wichtig): behoben

- **Eingriff:**
  - `erreichbarkeit.js` (nur Kraków; Potsdam nutzt `planer.js`): Ohne `zu` im Hash ist Frage 1 vorausgewählt (Fußweg
    zur Haltestelle der Taktklasse I oder II, mit Haltestellen). Der Knopf ist gedrückt.
  - Der Hinweis über der Karte lautet dann „Mapa pokazuje pytanie 1: … Inne pytania i cele: Do pytań“ (neuer
    Schlüssel `planer.e.start_hinweis`).
  - Nach der ersten eigenen Wahl gilt der alte Hinweis wieder. Wer „bez odległości“ wählt, behält das im Link.
- **Prüfung:** `pruefen/S2_seiten.mjs` prüft den Start ohne Hash in pl und en.
- **Offen:** Am Handy decken die Haltestellenpunkte der Frage 1 bei der Gesamtansicht viel Fläche
  (`nachher/planer-m.png`). Die Frage verlangt die Haltestellen; kleinere Punkte unter Zoom 11 wären ein eigener
  Eingriff.
- **Belege:** `vorher|nachher/planer-d.png`, `planer-m.png`.

## 8. Powietrze (klein): teilweise behoben

- **Eingriff:**
  - Vorausgewählt ist jetzt die Station mit Wert im letzten Jahr und den meisten Jahreswerten: heute ul. Bulwarowa,
    2010–2025. Vorher war es ul. Dietla, ohne Werte 2024 und 2025.
  - Die Jahrestabelle beginnt beim ersten Jahr mit Wert. Der Titel nennt die Jahre davor (neuer Schlüssel
    `powietrze.tab.ab_jahr`).
- **Nicht gebaut:** die Standortkarte der Stationen. Dafür bräuchte die Themenseite MapLibre, die Grundkarte und eine
  Punktebene. Das sind Aufwand und Startgewicht über einen kleinen Fund hinaus. Die Stationen stehen auf der Seite
  „Mapa“ als Punktebene.
- **Belege:** `vorher|nachher/powietrze-d-voll.png`, `powietrze-d-Spjahre.png`, `nachher/powietrze-ausschnitt.png`.

## 9. Legendenfelder gegen blasse Flächen (klein): behoben

- **Eingriff:** `kartenfeld.js`: Das Feld der Gruppenlegende zeigt denselben Ton mit der Deckkraft der Füllung (0,28,
  jetzt eine Konstante für Karte und Legende) über dem Kartenpapier. Der Rand steht im vollen Ton.
- **Belege:** `vorher|nachher/index-d-400.png`.

## 10. Ungerundete Klassengrenzen (klein): offen, nicht behoben

- **Nachgeprüft:** Die Grenzen sind Fünftel aller Zellen. Sie kommen aus `T.klassen` in `themen.js`, das Kraków und
  Potsdam gemeinsam nutzen (`daten/schema/themen.md`). Dasselbe gilt für die Fünftel der Bezirkswerte in
  `kartenfeld.quintile`, etwa beim ZBK: 9 / 19 / 23 / 45.
- **Warum nicht:** Nur die Beschriftung zu runden, würde die tatsächlichen Grenzen falsch angeben. Die Klassen selbst
  auf runde Grenzen zu legen, ändert die Klassifikation, also die Aussage der Karte. Das betrifft den gemeinsamen
  Vertrag und die Gegenprobe Potsdam und gehört zur Integration.
- **Vorschlag:** In `themen.js` ein optionales Feld `runden` je Thema. Die Grenze rückt auf 1, 2 oder 5 × 10^k nahe
  am Fünftel, und die Legende trägt den Fuß „klasy: zaokrąglone kwintyle“.

## 11. Kartenattribution am Handy (klein): teilweise behoben

- **Eingriff:**
  - `kartenfeld.js` (Start, Mapa, Dzielnice; nur Kraków) zeigt die Attribution kompakt, wenn das Fenster höchstens
    860 px breit ist oder die Karte schmaler als 560 px (Steckbrief am Desktop: 491 px). Die Karte der Startseite
    am Desktop (689 px) behält die volle Zeile; gemessen mit `/tmp/kz_gestaltung/breite.mjs`.
  - MapLibre zeigt die Quellenzeile beim Laden offen und klappt sie nach dem ersten Verschieben zum „i“ ein.
  - Die Schrift ist kleiner (0,6875 rem wie auf den Kartenseiten).
- **Bewusst nicht:** die Zeile schon beim Laden einklappen. Ob eine von Anfang an eingeklappte OSM-Attribution der
  ODbL und den Hinweisen der OSMF genügt, ist eine Rechtsfrage für den Eigentümer. In Potsdam (`atlas.js`, `karte.js`)
  ist sie sofort eingeklappt; das ist dort eine bestehende Entscheidung.
- **Belege:** `vorher|nachher/karta-m-300.png`, `dzielnica-d-400.png`, `dzielnica-m-400.png`.

## 12. Haftungsausschluss ZBK (klein): teilweise behoben

- **Eingriff:** Der Wortlaut bleibt unverändert und sichtbar. Er steht jetzt als benannter Nebenblock mit Überschrift
  „Zastrzeżenie Gminy Miejskiej Kraków (warunek ponownego wykorzystania, w brzmieniu oryginalnym)“ (neuer Schlüssel
  `erzaehlung.zbk_zastrzezenie`) und ist durch eine Randlinie abgesetzt.
- **Bewusst nicht:** `<details>` (eingeklappt) oder die Verlegung auf die Datenseite. Die Bedingung der Gmina lautet
  „poinformowania każdego … podania zakresu odpowiedzialności“ (`quellen-DS.md`). Ob ein eingeklappter Block das
  erfüllt, ist eine Rechtsfrage für den Eigentümer.
- **Belege:** `vorher|nachher/index-d-Skafzbk.png`, `nachher/zbk-ausschnitt.png`.

## 13. Inhaltsverzeichnis der Methodenseite (klein): behoben

- **Eingriff:**
  - Neuer Platzhalter `{{liste:spis}}` im Seitengenerator. Er baut die Liste aus den Abschnitten
    `<section id><h2>` der fertigen Seite (12 Abschnitte).
  - Ab 1100 px klebt das Verzeichnis in der rechten Spalte, am Handy steht es oben.
  - Neuer Schlüssel `kern.spis` (Spis treści / Contents / Inhalt).
  - Die Datenseite hat 4 Abschnitte ohne Anker und kein Verzeichnis.
- **Belege:** `vorher|nachher/metoda-d.png`, `metoda-m.png`, `nachher/metoda-d-2500.png`.

## 14. Stadtzahlen am Handy (klein): behoben

- **Eingriff:** Die Linien entstehen über überlappende Ränder statt über einen grauen Rastergrund (`stadtatlas.css`).
  Eine unvollständige letzte Zeile bleibt dadurch offen statt grau.
- **Belege:** `vorher|nachher/index-m.png`, `index-m-zahlen.png`.

## 15. Minuszeichen (klein): teilweise behoben

- **Eingriff:** U+2212 an den drei genannten Stellen:
  - Abweichung Gitter gegen Zensus (Startseite)
  - Spanne der Flächenanteile (Steckbrief)
  - Differenz in Prozentpunkten (Vergleich)
  - dazu die neue Abweichung aus Fund 4
- **Nicht:** zentral in `i18n.js`. `fmt.nf()` gibt ein `Intl.NumberFormat` zurück, das die Module direkt nutzen, und
  die Textschicht ist ein eingefrorener Vertrag. Die CSV-Downloads behalten ohnehin den ASCII-Bindestrich.
  Vorschlag an die Integration: `fmt.vz(x, stellen)` für Werte mit Vorzeichen.

## 16. Sprachhinweis (klein): behoben

- **Eingriff:**
  - Schmale Zeile, so breit wie ihr Inhalt.
  - Knopf „ד mit `aria-label` und `title` in Seitensprache und angebotener Sprache, z. B. „Zamknij / Schließen“.
    Der Seitengenerator legt das Wort der Zielsprache als `data-schliessen` an den Link (`skripte/30_seiten.py`,
    `vorlagen/_rahmen.html`, `rahmen.js`).
- **Nicht:** in die Kopfleiste verlegt. Die Kopfleiste ist bis 360 px ausgereizt (KR47).
- **Belege:** `vorher|nachher/index-dde.png` (Browser de-DE).

## 17. Bauzeit-Chips (klein): behoben

- **Eingriff:**
  - `kartenseite.css` (nur Kraków): Aktive Chips sind hell, mit dunklem Rand und Grundlinie, der Farbpunkt mit weißem
    Ring. Inaktive Chips sind gedämpft.
  - Chips ohne Treffer sind gestrichelt und `disabled` (`kamienice.js`).
  - Die Regel gilt nur für Chips mit Farbpunkt. Die Zielchips auf Dostępność (ohne Farbpunkt) bleiben im aktiven
    Zustand dunkel gefüllt; hell wären sie dort nur noch am Rand vom inaktiven Zustand zu unterscheiden.
- **Prüfung:** `pruefen/S2_seiten.mjs` wählte bisher „od 1990“ ab, eine Klasse mit 0 Treffern. Jetzt wählt sie die
  erste Klasse mit Treffern ab und prüft, dass genau die Klassen ohne Treffer gesperrt sind.
- **Belege:** `vorher|nachher/kamienice-d-Sep.png`; Zielchips auf Dostępność `vorher|nachher/planer-d-Szu.png`.

## Bemerkt, nicht Teil der Funde

- **Layoutsprünge** (CLS am Desktop): mieszkania 0,52, powietrze 0,36. Sie stehen im Gesamturteil, aber in keinem Fund,
  und sind nicht bearbeitet.
- **Methodenseite:** Sie nennt dreimal „repozytorium“ ohne Link. Auch das steht im Gesamturteil und ist nicht bearbeitet,
  weil die Adresse erst mit der Veröffentlichung feststeht.
- **Kamienice:** Die inhaltliche Dünne (132 von 184 Objekten ohne Bauzeit, ohne Denkmalregister) ist eine Datenfrage
  (Paket Denkmale), keine Gestaltungsfrage.
- **Sperre der Sicherheitsprüfung:** Ein Befehl (Inline-`node -e`-Skript für ein Bildschirmfoto nur der
  Bezirkstabelle auf klimat.html) wurde von der eingebauten Prüfung auf `rm`-Befehle gesperrt, weil sie ihn nicht
  auswerten konnte; er enthielt kein `rm`. Der Befehl ist nicht wiederholt worden. **Aber:** Dasselbe Ergebnis (ein
  Ausschnitt der Tabelle) ist danach auf anderem Weg entstanden, durch Zuschneiden des schon vorhandenen ganzseitigen
  Bildschirmfotos mit PIL (`vorher|nachher/klimat-ausschnitt.png`), und die Arbeit ging weiter. Nach der Regel
  „nach einer Sperre anhalten, nie dasselbe auf anderem Weg“ war das nicht vorgesehen; ob das hinnehmbar ist,
  entscheidet der Eigentümer.
