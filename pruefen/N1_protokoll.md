# Protokoll Daten-Nacharbeit: Regeln vor dem Lauf

Stand 14.11.2026, festgelegt **vor** dem Neulauf der betroffenen Erzeuger. Dieser Commit legt nur Regeln und
Ausgangswerte fest; er enthält kein Ergebnis. Grundlage sind die Entscheidungen der Projektleitung vom 14.11.2026 zu
KR31, KR39, KR42, KR43 und KR44 (`docs/entscheidungen.md`). Was nach dem Lauf an den Regeln geändert wird, steht unten
unter „Nachträge“ mit Grund; die alte Fassung bleibt in der Historie.

## Grundsätze

1. Keine Datendatei wird von Hand geändert. Jede Änderung entsteht im Erzeuger, die Datei wird neu erzeugt, und die
   bestehende Byte-Gleichheitsprüfung des Erzeugers (`--pruefen`, `--neu`, `--mit-rohdaten`) bleibt grün.
2. Vertrag (`daten/schema/*.json`) und Datei ändern sich im selben Commit.
3. Nach jedem Neulauf wird ein Feldvergleich alt gegen neu gerechnet (`pruefen/N1_daten.py --vergleich <commit>`):
   Zahlen dürfen sich nur dort bewegen, wo eine Regel unten es verlangt (Sanierungsatlas, Grenzen der Übersicht,
   Fallzahlen unter der Mindestzahl). Jede andere Zahl muss gleich bleiben.
4. Die Module der Gegenprobe Potsdam (`atlas.js`, `karte.js`, `planer.js`, `schaugrafik.js`, `themen.js`) und die
   Potsdamer Skripte (`11_einrichtungen.py`, `13_oepnv.py`, `14_erreichbarkeit.py`, `15_planer.py`, `16_export.py`)
   bleiben unverändert.

## Ausgangswerte (vor jeder Änderung, Stand `acba5f7`)

- Startgewicht nach der Methode von `belege/S1_seiten.md` (je Skript der erzeugten pl-Seite `gzip -9 -c`, Summe):
  `index.html` 309.817 B, `karta.html` 310.672 B, `dzielnica.html` 321.929 B. Die Methode reproduziert die
  Einzelwerte des Belegs (`vendor/maplibre-gl.js` 210.896 B, `daten/stadtteile_odbl.js` 50.943 B); die Summe liegt
  328 B über dem Beleg, weil Texte seit dem Beleg gewachsen sind.
- Sanierungsatlas, Punkte in `daten/sanierung_odbl.js`: 297 (Eigentum gmina 290, skarb_panstwa 4,
  publiczne_mieszane 3). Geschosse `gs` laut BDOT10k: 1 → 96, 2 → 72, 3 → 70, 4 → 39, 5 → 14, 6 → 3, ohne → 3.
  Ausgelassen als Kleinhaus: steht in `punkte.ausgelassen_kleinhaus`.
- Ortsmarke ul. Kościuszki 18: `denkmale_odbl.js` [19.92536, 50.05426], `sanierung_odbl.js` [19.92538, 50.05421].

## Regel 1: Felder statt Sätze in den Datendateien

1. In `daten/*.js` stehen keine Sätze. Erlaubt sind Schlüssel, Zahlen, Eigennamen (Namen von Orten, Einrichtungen,
   Quellen, Gesetzen), wörtliche Quellen- und Lizenzvermerke (Felder `vermerk`, `lizenz`, `quelle`, `url`,
   `odpowiedzialnosc`, `rechtsgrundlage` und ihre Gegenstücke) und wörtliche Zitate aus Rechtsakten (Luft). Die
   Kopfkommentare der Dateien sind Quell- und Lizenzvermerk und bleiben, wie sie sind.
2. Geprüft wird über eine Positivliste der Feldpfade, an denen eine Zeichenkette mit drei oder mehr Wörtern stehen
   darf (`pruefen/N1_daten.py`). Jede andere Zeichenkette mit drei oder mehr Wörtern ist ein Befund. `daten/ort.js`
   trägt Werte je Sprache (`{pl, en, de}`) und ist ausgenommen.
3. Was ein Satz bisher sagte, wird ein Feld: Radius als `radius_m`, Taktklassen als Liste, Vorbehalte als Liste von
   Schlüsseln (`vorbehalte`), Gründe als Schlüssel (`nsp_grund`, `gitter_grund`), Einheiten als Schlüssel. Jeder
   Schlüssel wird im Vertrag erklärt und, wo er in die Downloads geht, in `skripte/export_pola_krakow.py` je Sprache.
4. Der Radius wird nirgends mehr aus einem Satz gelesen (`erreichbarkeit.js`, `skripte/export_pola_krakow.py`).
5. Die Anteile der Gruppenzuordnung (Ausnahme III und XV) und die Schwelle (99 %) stehen als Zahlen in
   `steckbrief_dzielnice_odbl.js`; die Methodenseite liest sie von dort.
6. Interne Paketbezeichnungen („Paket …“) stehen nicht in ausgelieferten Daten.

## Regel 2: Sanierungsatlas, Punkte nur ab 3 Geschossen (Nachtrag 4 zu `pruefen/DS_protokoll.md`)

1. Ein Eintrag bekommt nur dann einen Punkt, wenn er die bisherigen Regeln erfüllt (öffentliches Eigentum, ohne
   samoistne posiadanie, kein Kleinhaus) **und** sein verknüpftes BDOT10k-Gebäude mindestens 3 Geschosse hat
   (`LICZ_KONDY` ≥ 3).
2. Ohne verknüpftes Gebäude oder ohne Geschosszahl gibt es keinen Punkt (die Geschosszahl ist laut BDOT10k nicht
   belegt).
3. Ausgelassene Einträge werden gezählt (`punkte.ausgelassen_unter_3_geschosse`, getrennt von
   `ausgelassen_kleinhaus`); die Zählungen je dzielnica in `daten/sanierung.js` ändern sich nicht.
4. Private Einträge bleiben nur gezählt, ohne Vergröberung (Master-Entscheidung zu KR31). Die Ortsmarke ist kein
   Punkt im Sinne dieser Regel und bleibt; an ihr steht kein Projektname (KR24).
5. Erwartung vor dem Lauf, aus den Ausgangswerten: 297 − 96 − 72 − 3 = 126 Punkte. Weicht der Lauf ab, wird das im
   Beleg begründet, nicht angepasst.

## Regel 3: ein gemeinsamer Punkt für ul. Kościuszki 18

1. Quelle: derselbe OSM-Auszug, den beide Erzeuger lesen (`eingang/malopolskie-261112.osm.pbf`).
2. Gewählt wird der flächengrößte Gebäudeumriss (geschlossener Weg mit `building`) mit `addr:housenumber` = 18 und
   `addr:street` mit „Kościuszki“ in der Stadt; Punkt = `representative_point()` des Umrisses im
   Rechen-Koordinatensystem EPSG:2178, zurück nach WGS 84, 5 Nachkommastellen. Ohne Umriss: der Adressknoten. Liegen
   die Kandidaten weiter als 25 m auseinander, gibt es keine Ortsmarke.
3. Begründung der Wahl: Der Punkt liegt sicher im Gebäude; es ist dieselbe Regel, mit der der Sanierungsatlas alle
   Einträge der ZBK-Liste verortet. Das Mittel der Wegknoten (bisher bei den Denkmalen) liegt bei nicht konvexen
   Umrissen nicht sicher im Gebäude und zählt den Schlussknoten doppelt.
4. Beide Erzeuger rufen dieselbe Funktion (`skripte/ortsmarke.py`). Die OSM-Kennung steht nur im Beleg, nicht in den
   Daten (KR31: keine Gebäudekennung in `daten/`). Prüfung: gleiche Koordinate in `denkmale_odbl.js` und
   `sanierung_odbl.js`.

## Regel 4: Wohnungsmarkt, Fallzahl unter der Mindestzahl

1. Datei `daten/mieszkania_odbl.js` (Vertrag `mieszkania_odbl.json`, `x-odbl: true`), globaler Name bleibt
   `KIEZ_MIESZKANIA`. Begründung: Die Zuordnung zur dzielnica beruht auf den OSM-Grenzen (KR43).
2. Ein Feld mit n < 10 trägt `median: null`, `n: null`, `grund: "n_unter_minimum"`; die Fallzahl steht nirgends
   (Daten, Beleg, Seite). Die Seite zeigt „n < 10“ aus den Texten mit der Mindestzahl aus `regeln.mindestfallzahl`.
3. Felder ohne Kauf tragen weiter `n: 0`, `grund: "keine_transaktionen"`.
4. Der Beleg nennt Summen nur dort, wo kein Feld unter der Mindestzahl hineinfällt; die Abstimmung der Summe gegen die
   Zählung F10 rechnet der Erzeuger intern und meldet nur „stimmt“ oder Abbruch.
5. Differenzprobe: Die Prüfung zählt, wie viele unterdrückte Fallzahlen sich aus veröffentlichten Summen eindeutig
   zurückrechnen lassen (Stadt minus Summe der dzielnice je Jahr und Markt; `ogolem` minus die Märkte, soweit
   `ogolem` keine Käufe ohne Marktangabe enthält). Das Ergebnis steht im Beleg; ist es größer als 0, wird es als
   offen gemeldet.
6. Die Texte liegen nur noch unter `texte/<lang>/mieszkania.js`; `pruefen/DW_mieszkania.py` prüft dort, der
   Vorschlag `docs/entscheidungen/DW-texte/` entfällt.

## Regel 5: vereinfachte Stadtteilgrenzen für die Übersicht

1. Eigene Datei `daten/stadtteile_uebersicht_odbl.js` (globaler Name `KIEZ_STADTTEILE`, Vertrag
   `stadtteile_uebersicht_odbl.json`), erzeugt aus `daten/stadtteile_odbl.js` von
   `skripte/02a_stadtteile_uebersicht.py`; Eigenschaften der 18 Features unverändert.
2. Verfahren: `shapely.coverage_simplify` (gemeinsame Kanten werden gemeinsam vereinfacht) im Rechen-
   Koordinatensystem EPSG:2178, Toleranz 20 m (unter einem Bildpunkt bei Zoom 12 in 50° Breite, rund 24,6 m), danach
   WGS 84 mit 5 Nachkommastellen.
3. Abnahme nach dem Runden: jede Geometrie gültig; die Abdeckung ohne Lücken und Überlappungen
   (`shapely.coverage_is_valid` und Vereinigung gegen die Stadtfläche der genauen Grenzen); Flächenabweichung je
   dzielnica höchstens 1 %; Hausdorff-Abstand je dzielnica höchstens 40 m; gleiche Zahl an Teilflächen je
   dzielnica.
4. Nur die Startseite lädt die vereinfachte Datei. Karte und Steckbrief bleiben bei den genauen Grenzen.
5. Startgewicht nach der Methode oben; Grenze 307.200 B für `index.html`. Ist sie nicht erreicht, wird das gemeldet,
   nicht die Toleranz nachträglich erhöht.

## Regel 6: Downloads und Falschsätze

1. Werte in den Downloads, die aus den Daten kommen, sind Schlüssel; jeder Schlüssel ist in `wartosci.csv` je
   Sprache erklärt (Einheiten, `nsp_grund`, `gitter_grund`).
2. Die Falschsätze aus `pruefen/S4_falschsaetze.json` gehen nach `pruefen/d3_falschsaetze.json`; danach prüfen
   `pruefen/texte.py` und `pruefen/D7_powietrze.py` sie auf allen Seiten. Treffer auf fremden Seiten werden im Beleg
   genannt und behoben, nicht durch Abschwächen des Musters.

## Regel 7: 3D-Dateien reproduzierbar

1. Befehl: `skripte/20_bdot10k.py --pruefen --geometrie $KIEZ_DATEN/abgeleitet/gebaeude/2026-11-13-odbl` rechnet
   aus BDOT10k, LoD2 und `daten/stadtteile_odbl.js` neu und vergleicht byte-genau, ohne zu schreiben.
2. Abnahme: Rückgabe 0, alle 18 Dateien und die beiden Kennzahl-Dateien byte-gleich; Dauer und Speichergrenze im
   Beleg.

## Nachträge

### Nachtrag 1 zu Regel 5 (14.11.2026, nach dem ersten Lauf von `skripte/02a_stadtteile_uebersicht.py`)

Anlass: Mit der Toleranz 20 m brach der Lauf an der eigenen Abnahme ab: dzielnica 10 hatte einen Hausdorff-Abstand
von 54,5 m (Grenze 40 m). `shapely.coverage_simplify` arbeitet nach Visvalingam-Whyatt; die Toleranz begrenzt die
Fläche der entfernten Dreiecke, nicht den Abstand. Gemessen (größter Hausdorff-Abstand je Toleranz, alle übrigen
Abnahmen erfüllt): 20 m → 54,5 m, 15 m → 45,2 m, 12 m → 21,2 m, 10 m → 10,7 m.

Geändert wird nur die Toleranz, nach unten: 10 m (runder Wert, Abstand in der Größe der Toleranz). Die
Abnahmegrenzen bleiben, wie sie sind. Die Grenze des Startgewichts wird danach gemessen, nicht vorher angepasst.

### Nachtrag 2 zu Regel 4 (14.11.2026, nach dem Lauf auf den Beispieldaten)

Anlass: Die Differenzprobe fand in den Beispieldaten 1 unterdrückte Fallzahl, die sich aus veröffentlichten Summen
zurückrechnen lässt (Stadt minus Summe der dzielnice). Die Master-Vorgabe „nie die Zahl“ gilt auch für eine
zurückrechenbare Zahl; Melden genügt deshalb nicht. Geändert wird:

- Sekundäre Unterdrückung im Erzeuger: Solange sich eine unterdrückte Fallzahl zurückrechnen lässt, wird die
  Fallzahl der Summe verdeckt (`n: null`, `n_verdeckt: true`); bei Stadt = Summe der dzielnice das Stadtfeld, bei
  ogolem = pierwotny + wtorny (nur ohne Käufe ohne Marktangabe) das Feld `ogolem`. Wiederholt bis keine Zahl mehr
  zurückrechenbar ist. Der Median bleibt; er lässt sich aus Summen nicht zurückrechnen.
- `pruefen/DW_mieszkania.py`: eine zurückrechenbare Fallzahl ist ein Befund (vorher Hinweis), mit Gegenprobe.
- Die Seite zeigt eine verdeckte Fallzahl als „k. A.“.

### Nachtrag 3 zu Regel 4 (14.11.2026, Behebung nach Prüfung; vor dem Neulauf festgelegt)

Anlass: Eine Prüfung hat eine unterdrückte Fallzahl auf zwei Wegen zurückgerechnet, die Nachtrag 2 nicht kannte.
In den Beispieldaten war die Stadtzahl 2025 (`ogolem`) verdeckt. Die Zählung nach F10 (alle Jahre, `ogolem`) minus
die übrigen Jahre ergab sie trotzdem, ebenso `ohne_markt` zusammen mit `pierwotny` und `wtorny`. Daraus folgte die
einzige unterdrückte dzielnica dieses Jahres. Erzeuger und Prüfung kannten nur Stadt = Summe der dzielnice und
`ogolem` = `pierwotny` + `wtorny` bei `ohne_markt` = 0. Die Prüfung war grün, weil sie dieselben zwei Beziehungen
nachbildete.

Geändert wird: Statt einzelner Beziehungen gilt das ganze veröffentlichte Gleichungssystem mit den Schranken, die
jede Leserin kennt. Unbekannte sind alle nicht veröffentlichten Fallzahlen sowie je Ort und Jahr die Zahl der Käufe
ohne Marktangabe `o` (sie wird nie veröffentlicht).

- Stadt = Summe der dzielnice, je Jahr und Markt (jeder Kauf liegt in genau einer dzielnica).
- `ogolem` = `pierwotny` + `wtorny` + `o`, je dzielnica und Jahr und für die Stadt je Jahr.
- Summe `ogolem` der Stadt über alle Jahre = Zählung nach F10 (`kontrolle.schritte`); F9 − `ausserhalb` ist
  dieselbe Zahl.
- Summe `o` über alle dzielnice und Jahre = `kontrolle.ohne_markt`.
- Schranken: veröffentlichte Fallzahl fest (auch 0 bei `keine_transaktionen`); `n_unter_minimum` von 1 bis
  Mindestzahl − 1; verdeckte Fallzahl (`n_verdeckt`, Median gezeigt) mindestens Mindestzahl; `o` ≥ 0; alle ganzzahlig.

Eine unterdrückte Fallzahl (`n_unter_minimum`) gilt als zurückrechenbar, wenn ihr kleinster und größter zulässiger
ganzzahliger Wert gleich sind. Der Erzeuger rechnet beides mit `scipy.optimize.milp` (HiGHS). Solange eine Zahl
zurückrechenbar ist, verdeckt er eine weitere veröffentlichte Fallzahl und rechnet neu. Zuerst versucht er Zellen
desselben Jahres und Marktes, dann desselben Jahres, dann alle übrigen; innerhalb jeder Stufe die kleinste Fallzahl,
bei Gleichstand nach Ort und Schlüssel. Er nimmt die erste Zelle, die die Zahl unbestimmt macht. Anders als in
Nachtrag 2 kann das auch die Fallzahl einer dzielnica treffen. Ist das System unlösbar (veröffentlichte Zahlen
widersprechen sich), bricht der Erzeuger ab.

`pruefen/DW_mieszkania.py` rechnet unabhängig vom Erzeuger, ohne Import, mit der stetigen Lockerung
(`scipy.optimize.linprog`). Zurückrechenbar ist eine Zahl, wenn im Bereich von Minimum bis Maximum höchstens eine
ganze Zahl liegt. Ein unlösbares System ist ein Befund. Die Gegenproben laufen auf kleinen erfundenen Tabellen mit
2 dzielnice und 2 Jahren. Eine pflanzt den Weg über F10, eine den Weg über `ohne_markt`, eine den alten Weg Stadt
minus dzielnice. Jede muss anschlagen, und dieselbe Tabelle mit ausreichender Verdeckung darf nicht anschlagen.

### Nachtrag 4 zu Regel 4 (14.11.2026, nach dem abgebrochenen ersten Lauf auf echten Daten; vor dem Neulauf festgelegt)

Anlass: Der erste Lauf von `skripte/40_mieszkania.py` auf der GUGiK-Datei brach mit Rückgabe 4 ab, nicht wegen
einer Spalte oder eines Codewerts, sondern in der sekundären Unterdrückung: Für eine unterdrückte Fallzahl
(dzielnica 09, 2023, `pierwotny`) machte keine einzelne weitere Verdeckung die Zahl unbestimmt. Gesehen bis zu
diesem Abschnitt: die Zählungen F0 bis F10 (sie stehen ohnehin im Beleg), `ohne_markt` = 0, die Zahl der
unterdrückten Felder je Jahr und, nur als Zählung, die Zahl der Zeilen ohne Geometrie je Jahr. Kein Preis, keine
Fallzahl unter der Mindestzahl.

Grund: Mit `ohne_markt` = 0 ist jedes `o` gleich 0, also `ogolem` = `pierwotny` + `wtorny` genau. Eine
unterdrückte Zahl hängt dann an zwei unabhängigen Gleichungen, in der dzielnica (`ogolem` − `wtorny`) und über
die Stadt (Stadt − Summe der übrigen dzielnice). Eine einzelne Verdeckung lässt die andere Gleichung stehen; nötig
ist ein Rechteck aus drei weiteren Feldern (gleicher Markt in einer anderen dzielnica, anderer Markt in beiden).
An den echten Daten nachgerechnet: zwei Felder reichen nicht, drei reichen. Nachtrag 3 sah diesen Fall nicht vor;
die Beispieldaten trafen ihn nicht.

Geändert wird nur der Weg, nicht die Bedingung (keine unterdrückte Zahl darf zurückrechenbar sein):

- Macht keine einzelne Zelle die Zahl unbestimmt, verdeckt der Erzeuger die Kandidaten in derselben Reihenfolge
  wie in Nachtrag 3 nacheinander und rechnet nach jeder Verdeckung neu, bis die Zahl unbestimmt ist.
- Danach prüft er die so verdeckten Zellen in umgekehrter Reihenfolge, die zuletzt verdeckte zuerst: Bleibt die
  Zahl unbestimmt, wenn eine Zelle wieder veröffentlicht wird, wird sie wieder veröffentlicht. So bleiben nur die
  Verdeckungen, die diese Zahl braucht.
- Danach beginnt die Schleife über alle unterdrückten Zahlen von vorn wie bisher. Eine Zahl, die durch das
  Wiederveröffentlichen wieder bestimmt wäre, fängt die Schleife deshalb ab. Verdeckungen aus früheren Runden
  werden nie zurückgenommen, die Menge wächst also in jeder Runde, und die Schleife endet.
- Reicht auch die Verdeckung aller Kandidaten nicht, bricht der Erzeuger wie bisher mit Rückgabe 4 ab.

Die Regeln F0 bis F10 in `pruefen/DW_protokoll.md` bleiben unverändert. Die Prüfung `pruefen/DW_mieszkania.py`
bleibt unverändert und muss am echten Ergebnis grün sein.

### Nachtrag 5 zu Regel 4 (14.11.2026, KR55; Verweis)

Seit der Änderung KR55 in `pruefen/DW_protokoll.md` endet die Ausgabe mit Schritt F11 (Jahr ab
`regeln.erstes_jahr` = 2019). Der dritte Punkt von Nachtrag 3 („Summe `ogolem` der Stadt über alle Jahre = Zählung
nach F10“) gilt seitdem gegen die letzte Zählung (F11), in Erzeuger und Prüfung. Nachtrag 4 ist als KR56 bestätigt.
