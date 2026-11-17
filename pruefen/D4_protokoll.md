# Prüfprotokoll Gliederung und Bevölkerung (vor dem ersten Lauf festgelegt)

Stand 13.11.2026. Diese Regeln stehen in einem eigenen Commit **vor** dem ersten Lauf von
`skripte/01_gliederung.py` und `skripte/02_bevoelkerung.py` auf echten Daten. Spätere Änderungen nur als neuer
Abschnitt „Änderung“ mit Datum und Grund, nie durch Umschreiben dieses Texts.

**Offengelegt:** Zwei Ergebnisse waren beim Festlegen schon bekannt, weil die Machbarkeitsprobe vom 13.11.2026 sie mit
den städtischen MSIP-Grenzen (nur Prüfdatum, Lizenz-STOPP) gerechnet hat: Summe des Eurostat-Gitters über die Zellen mit
Mittelpunkt in der Stadt 793.392 gegen 800.653 im NSP 2021 (−0,91 %), und die Zellsummen je dzielnica, aus denen sich je
historischem Stadtbezirk (delegatura) Abweichungen bis rund −2,7 % (Nowa Huta) gegen die NSP-Tabelle ergeben. Die
Toleranzen unten sind also nicht blind gewählt; sie sollen grobe Fehler (falsche Zuordnung, falsche Spalte, falsches
Koordinatensystem) fangen, nicht die Methode bestätigen.

## Raumbezug

1. **Stadtgrenze und delegatury:** BDOT10k Powiat 1261, Schicht `OT_ADJA_A`; Stadt = `RODZAJ` „gmina“ mit
   `IDTERYTJED` 1261011, delegatury = `RODZAJ` „dzielnica lub delegatura“ (vier Einträge, `IDTERYTJED` 1261029,
   1261039, 1261049, 1261059 wie die Symbole der NSP-Tabelle). Fehlt einer, bricht das Skript ab.
2. **Stadtteile (dzielnice):** OpenStreetMap (ODbL) aus `$KIEZ_DATEN/eingang/`, genau 18 Flächen, jede eindeutig einer
   Nummer I bis XVIII aus `config/krakow.yaml` zugeordnet (über `ref`, die römische Ziffer im Namen oder den Namen).
   Weniger oder mehr Treffer: Abbruch, die Beispieldaten bleiben stehen.
3. **Vereinigung der dzielnice gegen die Stadt:** Flächenabweichung höchstens 1 %, symmetrische Differenz höchstens 2 %
   der Stadtfläche. Sonst Befund.
4. **Zuordnung dzielnica → historischer Stadtbezirk** (`gruppe` in der Ortskonfiguration): Jede dzielnica liegt zu
   mindestens 99 % ihrer Fläche in der delegatura ihrer Gruppe. Sonst Befund; `zuordnung_geprueft` bleibt dann `false`.
5. **MSIP nur intern:** Die städtischen Grenzen dienen höchstens als Geometrie-Gegenprobe (Schnitt durch Vereinigung je
   dzielnica). Ergebnis und Zwischendateien bleiben außerhalb des Repos; ausgeliefert wird nichts daraus. Ein Wert unter
   0,98 ist ein Hinweis, kein Befund, weil die MSIP-Fassung den Stand 01.04.2014 trägt.

## Bevölkerung aus dem Gitter (Eurostat 2021, 1 km)

6. **Zuordnung Zelle → Raum:** Mittelpunktregel (die Zelle zählt ganz zu der Fläche, die ihren Mittelpunkt enthält). Zum
   Vergleich und als Maß der Unschärfe die Flächenanteilsregel (Einwohner gleichmäßig über die Zelle verteilt, Anteil =
   Schnittfläche). Ausgeliefert wird die Mittelpunktregel, die Spanne beider steht im Beleg.
7. **Gegenprobe Stadt:** Summe der Zellen mit Mittelpunkt in der Stadt gegen 800.653 (NSP 2021, Zeile „miasto na prawach
   powiatu“, Symbol 1261). Toleranz ±2 %. Darüber Befund.
8. **Gegenprobe delegatury:** Summe je delegatura (Mittelpunktregel) gegen die NSP-Zeile der delegatura. Toleranz ±5 %
   je delegatura. Darüber Befund.
9. **In sich:** je Zelle `Y_LT15 + Y15-64 + Y_GE65 = T`; Abweichungen werden gezählt und genannt, nicht korrigiert.
   Statusfelder (`T_OBS_STATUS`, `T_SPECIAL_VALUE`, Anteile konventionell verortet, nicht gezählt) werden je Wert gezählt.

## Bevölkerung aus dem NSP 2021 je rejon statystyczny (GUS)

10. **Exakte Summen (Toleranz 0):** Σ rejony = Σ obwody = Stadt; Σ rejony je delegatura = Zeile der delegatura;
    Σ delegatury = Stadt; männlich + weiblich = ogółem; Σ der neun 10-Jahres-Gruppen = ogółem; Σ der drei ökonomischen
    Gruppen = ogółem. Je verletzter Gleichung ein Befund.
11. **Rejon → dzielnica** (erst mit der Geometrie der rejony aus dem Handdownload): Zuordnung über einen inneren Punkt
    des rejon (`point_on_surface`). Rejony, deren Fläche zu mehr als 5 % in einer anderen dzielnica liegt, werden
    gezählt und im Beleg genannt (Nummer, keine Werte). Σ rejony je dzielnica über alle dzielnice = Stadt exakt; jeder
    rejon der Tabelle hat genau eine Geometrie und umgekehrt, sonst Befund.

## Datenschutz und Darstellung

12. **Kein Einzelwert unter der dzielnica-Ebene aus dem NSP:** Werte je rejon oder obwód werden nie ausgeliefert, nur
    Summen je dzielnica, delegatura und Stadt.
13. **Mindestfallzahl:** Anteile (Alter) je Gitterzelle nur bei mindestens 100 Personen in der Zelle, sonst `null` (Regel
    des Kiezatlas Potsdam, als strengere Eigenregel, solange die GUS-Geheimhaltungsregel nicht geprüft ist). Für
    Summen je Raum gilt dieselbe Grenze.
14. **Keine eigene Rundung der Zählwerte:** Beide Quellen veröffentlichen ungerundete Zahlen; Anteile mit einer
    Nachkommastelle, Dichte als ganze Zahl Personen je km², Flächen mit zwei Nachkommastellen in km².
15. **Beispieldaten bleiben sichtbar:** Solange eine der Eingaben fehlt, tragen die betroffenen Dateien `fixture: true`;
    Felder, die vom fehlenden Eingang abhängen, sind `null` mit Grund, nie geschätzt.

## Änderung 13.11.2026 (nach dem ersten Lauf mit OSM-Grenzen)

Offengelegt: Alle Punkte dieses Abschnitts sind nach dem ersten Lauf mit den OSM-Grenzen festgelegt worden; die
Ergebnisse von Regel 3 bis 5 waren dabei bekannt.

- **Skript:** Gliederung und Bevölkerung rechnet ein Skript, `skripte/02_bevoelkerung.py`; `skripte/01_gliederung.py`
  gibt es nicht.
- **Regel 2, Lesart der OSM-Daten:** Im Auszug Małopolska (Stand 12.11.2026) tragen die 18 dzielnice `admin_level` 9,
  `name` ohne Ziffer und die Ziffer in `official_name` („dzielnica X Swoszowice“, „Dzielnica XIV Czyżyny“);
  historische Viertel mit denselben Namen tragen `admin_level` 11. Die Zuordnung liest die Ziffer aus `ref`,
  `official_name` oder `name`, übergeht Flächen mit einem anderen `admin_level` als 9 und verlangt, dass der Name ohne
  „dzielnica <Ziffer>“ genau dem Namen der Ortskonfiguration entspricht. Die Regel selbst (genau 18, eindeutig, sonst
  Abbruch) bleibt.
- **Regel 4, Folge:** Ein Befund nach Regel 4 sperrt die Ausgaben nicht; die Folge ist die im Text genannte
  (`zuordnung_geprueft` bleibt `false`). Die Schwelle 99 % bleibt. Begründung und Zahlen: `docs/entscheidungen/D4.md`.
- **Regel 15, Lizenzfolge (KR3):** Solange offen ist, ob aus den OSM-Grenzen abgeleitete Werte unter die ODbL fallen,
  stehen Werte je dzielnica nur in `daten/steckbrief_dzielnice_odbl.js`; `steckbrief.js` trägt für die dzielnice
  `null` mit Grund, `stadtteile_odbl.js`, `zellen.js` und `kennzahlen.*` bleiben Beispieldaten.

## Nachtrag vom 13.11.2026 (nach Entscheidungen, vor dem Echtlauf der Seitendaten)

Festgelegt, bevor `stadtteile_odbl.js`, `zellen_odbl.js` und `kennzahlen_odbl.*` echt geschrieben wurden. Die Regeln oben
bleiben stehen; diese Punkte ändern ihre Folgen.

- **Regel 4, dokumentierte Ausnahme:** III Prądnik Czerwony und XV Mistrzejowice gelten mit 98,53 % bzw. 98,64 % ihrer
  Fläche als ihrer delegatura zugeordnet. Der Rest ist ein Grenzsplitter zwischen den delegatury der BDOT10k und den
  dzielnice (Gegenprobe mit den städtischen Grenzen nach Regel 5, nur intern). Die Schwelle 99 % bleibt. Die Ausnahme
  gilt nur für genau diese beiden Anteile auf zwei Nachkommastellen (`AUSNAHMEN_REGEL4` in
  `skripte/raum_bevoelkerung.py`); ändert sich ein Anteil mit neuen Grenzen, ist es wieder ein Befund. Damit ist
  `zuordnung_geprueft` = `true` (`config/krakow.yaml`, Vermerk mit den Zahlen dort und in
  `daten/steckbrief_dzielnice_odbl.js`, Feld `hinweis`).
- **Regel 15, Lizenzfolge entschieden (Variante a):** Werte, die auf den OSM-Grenzen beruhen, werden als `_odbl`-Dateien
  unter der ODbL 1.0 mit dem Vermerk „© OpenStreetMap-Mitwirkende, ODbL“ ausgeliefert. Die Seitendateien heißen
  deshalb `daten/zellen_odbl.js`, `daten/kennzahlen_odbl.js` und `daten/kennzahlen_odbl.json` (Verträge
  `daten/schema/zellen_odbl.json`, `kennzahlen_odbl.json` mit `x-odbl`); `zellen.js` und `kennzahlen.*` gibt es nicht
  mehr. `steckbrief.js` (ohne `_odbl`) trägt für die dzielnice weiter `null` mit Grund; die Werte je dzielnica stehen in
  `steckbrief_dzielnice_odbl.js` und `kennzahlen_odbl.*`. `SEITENDATEN_AUS_OSM = True`.
- **Prüfung:** `pruefen/D4_bevoelkerung.py`, Teil C, prüft beides: ohne Grenzen alle vier Seitendateien Beispieldaten,
  mit Grenzen alle vier echt und die drei `_odbl`-Skripte mit ODbL-Vermerk im Kopf; die alten Namen gibt es nicht.

## Änderung 17.11.2026 (Geometrie der rejony, vor dem ersten Lauf mit ihr)

Festgelegt, bevor `skripte/02_bevoelkerung.py` die Geometrie der rejony zum ersten Mal gelesen hat. Die Regeln 10 bis 15
bleiben stehen; diese Punkte legen Quelle, Lesart und den Umgang mit einer Abweichung fest.

**Offengelegt:** Beim Festlegen waren bekannt (Zählung ohne Rechnung je dzielnica): In der GUS-Datei tragen 749
Einheiten in Kraków eine sechsstellige Kennung mit `lowers` (rejony) und 4.614 eine siebenstellige mit `uppers`
(obwody). 748 der 749 rejony stehen in der NSP-Tabelle, jeweils mit derselben delegatura wie `LocationString`; der
rejon 390570 (Krowodrza, laut `areaValue` 0,22 km², ein obwód) hat keine Zeile. Die Tabelle hat 4.592 obwody, also 22
weniger als die Geometrie. Die Summe von `areaValue` über die 749 rejony ist 326,43 km².

- **Quelle:** GUS, Bazy Rejonów Statystycznych i Obwodów Spisowych 2021 (BREC), INSPIRE-Thema Statistical Units,
  Woiwodschaft 12, Handdownload `eingang/gus_brec/AreaStatisticalUnit_12.zip` (Herkunft und Prüfsumme in
  `eingang/gus_brec/HERKUNFT.md`). Der Leser liest diese Datei unverändert; es gibt keine abgeleitete Zwischendatei.
- **Lesart:** Kraków = `gml:LocationString` gleich 1261029, 1261039, 1261049 oder 1261059. rejon = `thematicId`
  mit genau sechs Ziffern, die Kennung wird exakt verglichen (kein Abschneiden; ein siebenstelliger obwód darf nie
  als rejon gelesen werden). Geometrie aus `gml:MultiSurface` mit allen `Polygon`en samt Löchern, EPSG:4258 mit
  Breite vor Länge, umgerechnet nach EPSG:4326.
- **Plausibilität (Befund, wenn verletzt):** Mittelpunkt jedes rejon im Rahmen 19,7–20,3 °O und 49,9–50,2 °N; Σ
  Fläche der rejony gegen die Stadtfläche aus BDOT10k höchstens 1 % Abweichung; jede Kennung genau einmal.
- **Regel 11, Rückrichtung:** Ein rejon der Geometrie ohne Zeile in der Tabelle ist kein Befund, wenn er höchstens
  2 von 1000 rejony betrifft (heute 1 von 749); er bekommt keine Werte, wird mit Nummer und delegatura im Beleg
  genannt und zählt nicht zur Zuordnung. Mehr solche rejony, oder einer, dessen `LocationString` nicht zur
  delegatura passt, ist ein Befund. Dass ein fehlender rejon unbewohnt ist, wird nicht behauptet (nicht geprüft).
- **Regel 12 bleibt:** Die Geometrie der rejony dient nur der Summe je dzielnica; weder Geometrie noch Werte je rejon
  werden ausgeliefert. Eine Darstellung je rejon wäre eine Änderung dieser Regel und ist hier nicht vorgesehen.

## Änderung 17.11.2026, nachmittags (Karte je rejon, Entscheidung Andre)

Festgelegt, bevor eine Datei mit Werten je rejon geschrieben wurde. Anlass: Hinweis aus der Hochschule (Mail vom
16.11.2026), die NSP-Tabellen über die Kennung an die Grenzen der rejony zu hängen, um feiner als das 1-km-Gitter zu
werden. Andre hat am 17.11.2026 entschieden, die Karte je rejon zu bauen.

**Offengelegt:** Bekannt waren beim Festlegen die Zählungen aus dem Abschnitt davor (749 rejony in der Geometrie, 748 in
der Tabelle) und aus dem Beleg D4: kleinster rejon 9 Personen, größter rejon und Zahl der rejony unter 100 Personen
stehen in `belege/D4_bevoelkerung.md`, Schritt 3.

- **Regel 12 neu:** Werte je obwód werden nie ausgeliefert. Je rejon statystyczny werden ausgeliefert: Einwohner
  (NSP 2021, wie vom GUS selbst je rejon veröffentlicht), Fläche, Dichte und die Anteile unter 20, ab 60 und im
  nacherwerbsfähigen Alter. Keine weiteren Merkmale je rejon (keine Geschlechter, keine einzelnen Altersgruppen).
  Begründung: Der GUS veröffentlicht diese Zahlen je rejon offen; die Karte zeigt nichts, was nicht schon amtlich
  öffentlich ist, und bleibt bei den Anteilen strenger als die Quelle.
- **Regel 13 je rejon:** Anteile nur ab 100 Personen im rejon, sonst `null` (auf der Karte grau, „zu wenige
  Personen“). Die Einwohnerzahl selbst steht immer, auch unter 100.
- **Rejon ohne Tabellenzeile** (heute 390570): mit Geometrie, Einwohner `null`, Kennzeichen `ohne_zeile`.
- **Kontrollen (Befund, wenn verletzt):** Σ Einwohner über die rejony der Datei = Stadt (NSP) exakt; jede Kennung
  der Tabelle genau einmal; kein Anteil bei weniger als 100 Personen; Differenzprobe je unterdrücktem rejon und
  Anteil: Aus dem Zähler der dzielnica (Summe in `steckbrief_dzielnice_odbl.js`) minus den Zählern der übrigen
  rejony derselben dzielnica, die sich aus Anteil (auf 0,1 gerundet) und Einwohnern nur als Spanne ergeben, folgt eine
  Spanne für den unterdrückten Zähler. Ist diese Spanne enger als 0 bis Einwohner des rejon, ist das ein Befund.
- **Lizenz:** Die Datei hängt nicht an OSM (Grenzen GUS BREC, Werte GUS NSP) und trägt kein `_odbl`; Vermerke beider
  GUS-Quellen im Kopf.

## Änderung 17.11.2026, nach dem ersten Lauf der Karte je rejon

**Offengelegt:** Festgelegt nach dem ersten Lauf. Die Differenzprobe aus dem Abschnitt davor schlug an: Mit Anteilen auf
eine Nachkommastelle ließen sich 15 unterdrückte Zähler der vier rejony unter 100 Personen über die Summe je dzielnica
eingrenzen, einer genau (bei rund 1.000 Personen entspricht 0,1 % etwa einer Person). Es wurde nichts ausgeliefert.

- **Anteile je rejon in ganzen Prozent** (kaufmännisch gerundet), nicht auf 0,1. Die Differenzprobe rechnet
  entsprechend mit ±0,5 Prozentpunkten. Die Regel selbst (Befund, wenn eine Spanne enger ist als 0 bis Einwohner)
  bleibt unverändert.

## Nachtrag 17.11.2026, nach dem Review der Karte je rejon

- **Geltung:** Die Fassung „Regel 12 neu“ (Abschnitt „Karte je rejon“) ersetzt Regel 12 oben und den Punkt „Regel 12
  bleibt“ im Abschnitt „Geometrie der rejony“; beide Texte bleiben als Verlauf stehen.
- **Differenzprobe strenger:** zusätzlich gegen die Stadt und gegen die Kreuzmengen aus Gruppe der dzielnica und
  delegatura (Differenzen zwischen den Summen je dzielnica und je delegatura beziehen sich auf diese Mengen). Die
  Spanne wird ganzzahlig und rechts offen gerechnet (q = ganze Prozent ⇔ (2q−1)·n ≤ 200·Zähler < (2q+1)·n). Der
  Review fand keinen rückrechenbaren Wert; die Erweiterung schließt die Lücke für künftige Daten.
- **Dichte je rejon** aus der ungerundeten Fläche; Fläche in der Datei auf 0,001 km².
