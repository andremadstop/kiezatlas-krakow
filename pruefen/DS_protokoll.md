# Prüfprotokoll Sanierungsatlas Wohnungsbestand (vor dem ersten Lauf festgelegt)

Stand 13.11.2026. Dieses Protokoll steht als eigener Commit **vor** dem ersten Lauf von `skripte/36_sanierung.py`
auf echten Daten (Verortung, Verknüpfung, Typologie). Was hier steht, gilt für die Abnahme; spätere Änderungen nur
mit neuem Commit und Begründung in `docs/entscheidungen/DS.md`. Ergebnisse: `belege/DS_sanierung_lauf.md`.

Vor diesem Commit gelesen (nicht gerechnet): die Spalten und Rohwerte der ZBK-Liste (Probe-Auszug mit
`pdftotext -bbox`), die Schreibweise der OSM-Adressen in Kraków (`addr:street`, `addr:place`) und die Felder von
BDOT10k `OT_BUBD_A`. Daraus stammen die Regeln unten; kein Ergebnis einer Verortung oder Typologie lag vor.

## Gegenstand und Grenze

- **Liste:** „Wykaz budynków i obiektów w zarządzie ZBK na dzień 2025-12-01“, Załącznik nr 635620 (PDF, 26 Seiten,
  aus Excel erzeugt, eingestellt 18.12.2025), Dokument „Nieruchomości pozostające w zarządzie ZBK“ im BIP des
  Zarząd Budynków Komunalnych w Krakowie (`https://www.bip.krakow.pl/?bip_id=32&mmi=10127`), abgerufen 13.11.2026.
  Das ist die einzige Fassung, die das BIP am Abruftag anbietet (Dziennik zmian: letzte Änderung 16.03.2026).
- **Spalten der Liste:** L.p., ADRES (Straßenname, Vorsatz ul./os./al./pl., Hausnummer), Miejscowość, Rodzaj
  budynku (M mieszkalny, U użytkowy, M/U mieszane, P przychodnie), Własność, samoistne posiadanie, Dzielnica.
  **Nicht enthalten** sind ein Verwalter je Eintrag (Verwalter ist laut Titel der ganzen Liste der ZBK) und eine
  Nummer im Denkmalregister. Beides wird nicht aus anderen Quellen nachgetragen.
- **Ein Eintrag ist kein Gebäude:** Die Liste führt teils mehrere Einträge je Adresse (Vorderhaus und Oficyna als
  „bud. I“, „bud. II“), teils Garagen, Schutzräume und Teile von Grundstücken. Gezählt wird in Einträgen; die
  Zahl der Adressen und der verknüpften BDOT10k-Gebäude steht getrennt im Beleg.
- **Typologie:** eine **Schätzung** von Kandidaten für Plattenbau- und Großsiedlungsbestand aus BDOT10k-Merkmalen,
  ohne Baujahr. Sie ist keine Erhebung der Bauweise. Die Datei trägt `schaetzung: true`, der Vertrag erzwingt das.

## Lesen der PDF-Tabelle

1. Werkzeug: `pdftotext -bbox` (Poppler; Version im Beleg). Wörter mit Rahmen je Seite.
2. Spalten nach x-Bereichen in pt, aus den Kopfwörtern der Seite 1 abgeleitet: L.p. < 36, Name 36–205, Vorsatz
   205–234, Hausnummer 234–316, Miejscowość 316–361, Rodzaj 361–403, Własność 403–488, samoistne posiadanie
   488–528, Dzielnica ≥ 528. Auf jeder Seite müssen die Kopfwörter „L.p.“, „ADRES“, „Miejscowość“, „Rodzaj“,
   „Własność“, „Dzielnica“ höchstens 2 pt von der Lage auf Seite 1 abweichen, sonst Abbruch.
3. Zeilen: Jede Zelle ist in ihrer Tabellenzeile senkrecht mittig gesetzt, wie die L.p. Je Spalte werden die
   Textzeilen in zusammenhängende Gruppen geteilt (Abstand zwischen zwei Textzeilen einer Gruppe höchstens 4 pt)
   und jede Gruppe genau einer L.p. zugeordnet, sodass die Summe der Abstände Gruppenmitte – Mitte der L.p.
   klein ist (dynamische Programmierung; eine L.p. ohne Gruppe kostet 3 pt). Eine Gruppe, deren Mitte mehr als
   6 pt von der Mitte ihrer L.p. liegt, ist ein Befund.
4. Własność und samoistne posiadanie werden zu einem Text zusammengelegt (die Liste setzt „GMK/samoistne
   posiadanie“ teils in die eine, teils in die andere Spalte).
5. **Pflichtprüfungen:** L.p. lückenlos 1 … N ohne Doppel; N je Seite gleich der Zahl der Zeilen, die in
   `pdftotext -layout` mit einer Zahl beginnen und eine Miejscowość tragen (zweiter Leseweg); jede Dzielnica ist
   eine der 18 oder „poza Krakowem“; jeder Eintrag hat Name, Rodzaj und Własność. Rohwerte von Rodzaj,
   Miejscowość, Vorsatz und Dzielnica werden vor dem Vereinheitlichen gezählt.

## Vereinheitlichen

| Feld | Regel |
|---|---|
| Art | Buchstaben M, U, P aus dem Code am Anfang (bis zum ersten Leerzeichen oder „-“ mit Text danach); Schlüssel in der Reihenfolge M, U, P (`M`, `U`, `P`, `MU`, `MP`, `UP`, `MUP`). „U/M“ = „M/U“. Zusätze wie „- w ZBK lokale mieszkalne“ werden gezählt, nicht veröffentlicht. |
| Eigentum | Merkmale im Text: Gemeinde (`Gm. Kr.`, `Gm.Kr`, `GMK`, „Miasto Kraków“), Staat (`SP`), Woiwodschaft („Województwo“), Privatpersonen (`PR`), samoistne posiadanie („samoistne“, „samoi“). Klasse: mit `PR` und öffentlichem Anteil `z_prywatnymi`, nur `PR` `prywatne`, mehrere öffentliche ohne `PR` `publiczne_mieszane`, sonst `gmina` bzw. `skarb_panstwa`, ohne Merkmal `brak`. Brüche und Wortlaut bleiben außerhalb des Repos. |
| Dzielnica | römische Zahl I–XVIII aus dem Text vor „ - “; „poza Krakowem …“ → `poza` |
| Hausnummer | siehe Verortung |

## Verortung (nur Einträge mit Dzielnica I–XVIII)

- **Adressquelle:** OSM-Auszug Małopolska aus `eingang/` (ODbL). BDOT10k 1261 hat **keine** Adresspunkte
  (`OT_BUBD_A` ohne Straße und Hausnummer, kein Adress-Layer im Paket). Die amtlichen PRG-Adresspunkte sind ein
  offener Handdownload. Alles, was von der Verortung abhängt, steht nur in `daten/sanierung_odbl.js`.
- **OSM-Adressen:** Knoten und geschlossene Wege mit `addr:housenumber`, deren Punkt (Knoten bzw. innerer Punkt
  des Umrings) in der Stadtgrenze aus BDOT10k (`OT_ADJA_A`, Gemeinde) liegt. Straße = `addr:street`, sonst
  `addr:place`. Relationen werden nicht gelesen (gezählt).
- **Vergleich der Namen:** klein geschrieben, Punkte entfernt, Leerraum vereinheitlicht. Aus dem ZBK-Namen
  entfallen Angaben in Klammern und in Anführungszeichen; bei „/“ (Eckadresse) gilt der Teil davor, ohne eine
  Hausnummer am Ende. Vorsatz `os.` verlangt einen OSM-Namen mit „osiedle “ davor, `pl.` „plac “, `al.`
  „aleja “ oder keinen Vorsatz, `ul.` keinen der drei. Nach Abzug des Vorsatzes muss der OSM-Name gleich dem
  ZBK-Namen sein oder auf „ “ + ZBK-Namen enden (OSM schreibt Vornamen aus: „Tadeusza Kościuszki“).
- **Hausnummer:** Leerraum zwischen Zahl und Buchstabe entfällt, Vergleich ohne Groß-/Kleinschreibung. Klassen:
  `standard` (Zahl mit höchstens einem Buchstaben), `zusatz` (eine solche Nummer am Anfang, danach Klammer oder
  Text: es gilt die Nummer), `bereich` („2-2B“, „185-187“, „69B/69C“, „68/68A“, „29 / 1“: es gilt die erste
  Nummer, die in OSM vorkommt, in der Reihenfolge des Textes), `beschreibung` (beginnt mit „obok“, „za“, „dz.“,
  „budynek“, „garaż“ oder enthält keine Nummer am Anfang: **nicht verortbar nach Regel**).
- **Eindeutigkeit:** Haben mehrere verschiedene OSM-Straßen die Nummer, ist der Eintrag `mehrdeutig_ulica` und
  bleibt unverortet. Liegen die OSM-Objekte zu Straße und Nummer mehr als 50 m auseinander, ist er
  `mehrdeutig_punkt`. Sonst gilt das Gebäude (geschlossener Weg mit `building=*`, bei mehreren das größte),
  sonst der Knoten.
- **Ergebnisklassen (Zählung je Art im Beleg):** `verortet`, `beschreibung`, `poza_krakowem`,
  `ulica_nie_znaleziona`, `numer_nie_znaleziony`, `mehrdeutig_ulica`, `mehrdeutig_punkt`. Nicht verortete Einträge
  stehen im Beleg mit L.p., Art, Dzielnica und Klasse, ohne Adresse.
- **Gegenprobe ohne Zirkel:** Die Dzielnica der Liste wird mit der OSM-dzielnica am verorteten Punkt verglichen
  (Grenzen aus `skripte/raum_bevoelkerung.py`, nur gelesen). Übereinstimmung als Quote mit Wilson-95-%-Intervall
  und n; jede Abweichung mit L.p. im Beleg.

## Verknüpfung mit BDOT10k, LoD2 und Denkmalstatus

- **Gebäude:** War der OSM-Treffer ein Gebäudeumriss, gilt das BDOT10k-Gebäude mit der größten Schnittfläche, wenn
  sie mindestens 50 % der kleineren der beiden Flächen ausmacht. Sonst (und bei Knoten): BDOT10k-Gebäude, das den
  Punkt enthält, sonst das nächste bis 10 m, sonst keines.
- **Merkmale aus BDOT10k:** Geschosse (`LICZ_KONDY`), Funktion (`FSBUD`, als Schlüssel), `KAT_ISTNIE`. Die
  Kennung `LOKALNYID` dient nur der Verknüpfung und wird nie veröffentlicht.
- **Höhe:** LoD2 (Stand 2017, `buildingId` = `LOKALNYID`, Höhe = höchster minus tiefster z-Wert, wie
  `skripte/20_lod.py`) mit Herkunft `lod2`; sonst Geschosse × 3 m mit Herkunft `geschosse` (Konvention aus dem
  Gebäudepaket, als geschätzt beschriftet); sonst `null`. Veröffentlicht mit dem wörtlichen Vermerk des Geoportals.
- **Denkmalstatus:** OSM `heritage=*` am Treffer oder an einem OSM-Objekt, dessen Punkt im verknüpften
  BDOT10k-Gebäude liegt. `false` heißt „keine Angabe in OSM“, nicht „kein Denkmal“. Registerdaten (NID, gminna
  ewidencja) fehlen im Eingang; die Liste selbst nennt keinen Denkmalstatus.

## Typologie (Schätzung)

- **Grundgesamtheit:** BDOT10k-Gebäude der Stadt mit `KAT_ISTNIE` = „eksploatowany“ und `PFBUD` = „budynek
  wielorodzinny“.
- **Kandidat Block (`blok`):** mindestens 4 Geschosse, Grundfläche mindestens 250 m², Rechteckigkeit (Fläche
  geteilt durch die Fläche des kleinsten umschließenden gedrehten Rechtecks) mindestens 0,85.
- **Kandidat Großsiedlung (`osiedle`):** Kandidat Block, in dessen Umkreis von 150 m (Schwerpunkt zu Schwerpunkt)
  mindestens 9 weitere Kandidaten Block liegen.
- **Bekannte Grenze:** Ohne Baujahr fallen auch rechteckige Wohnblöcke nach 1990 unter die Kandidaten; die Zahl ist
  eine Obergrenze für die Merkmalskombination, keine Zahl der Plattenbauten. Keine Zahl aus der Literatur wird als
  eigene ausgegeben. Bezug nur bibliographisch: Barnaś, Jeleński, Nowak-Ocłoń, Racoń-Leja u. a., Energy 263
  (2023) 125774, DOI 10.1016/j.energy.2022.125774.
- **Stichprobe:** 30 Kandidaten Großsiedlung und 10 Mehrfamilienhäuser mit mindestens 4 Geschossen, die kein
  Kandidat sind, zufällig mit Startwert 20261113, als Punkte im Beleg. Die Sichtprüfung am Luftbild ist **offen**
  (kein automatischer Abruf von Kartenbildern: die GUGiK verbieten „harvesting“); bis dahin keine Trefferquote.
- **Räume:** Stadt und Delegaturen (BDOT10k) in `daten/sanierung.js`; dzielnice (OSM-Grenzen) nur in
  `daten/sanierung_odbl.js`.

## Ortsmarke

ul. Kościuszki 18 (Demonstrator des Projekts FuturHist, Quelle `https://futurhist.eu/demonstrators/krakow/`,
abgerufen 13.11.2026): Lage nur aus der Verortung nach den Regeln oben, immer `lage_geprueft: false`. Aus der
FuturHist-Seite wird nur die Adresse und die Angabe zum ZBK-Bestand („over 500 buildings“, „over 130 buildings …
under conservation protection“) als fremde Vergleichsangabe zitiert, nie als eigene Zahl.

## Abnahmeregeln (Befund, wenn verletzt)

1. Summen: Σ Einträge je Art = Σ je Eigentum = Σ je Dzielnica = N; Σ Ergebnisklassen der Verortung = N;
   Σ Typologie je Delegatura + nicht zugeordnet = Stadt.
2. Keine Adresse (Straße, Hausnummer), keine L.p., keine Gebäudekennung (`LOKALNYID`, `id`, `oid`, `gml_id`),
   keine Namen von Personen in `daten/sanierung*.js`.
3. Punkte nur für Einträge der Klassen `gmina`, `skarb_panstwa`, `publiczne_mieszane`; Einträge mit Anteil von
   Privatpersonen oder samoistne posiadanie nur gezählt.
4. OSM-abhängige Werte nur in `daten/sanierung_odbl.js`; `daten/sanierung.js` ohne OSM-Spur.
5. Typologie mit `schaetzung: true`; keine Baujahre, keine Energiewerte.
6. Reproduzierbar: `skripte/36_sanierung.py --pruefen` erzeugt aus denselben Eingängen byte-gleich dieselben
   Dateien; `pruefen/DS_sanierung.py` prüft Regeln 1–5 ohne Netz und ohne Datenbank.

## Nachtrag 1 (13.11.2026, nach dem ersten Lauf, vor der Abnahme)

Anlass: Der erste Lauf verortete 394 von 500 Einträgen in Kraków; 46 blieben `ulica_nie_znaleziona`, darunter
Namen in der Form „Nachname Vorname“ („Dietla Józefa“; OSM: „Józefa Dietla“), „Św.“ statt „Świętego“ und
„… Plac“ am Ende des Namens. Geändert wird nur der Namensvergleich, nicht die Gegenprobe:

- Ein ZBK-Name aus genau zwei Wörtern passt auch in umgekehrter Reihenfolge.
- Das Wort „św“ passt auf „świętego“, „świętej“ und „świętych“.
- Endet der ZBK-Name auf „plac“, gilt der Vorsatz `pl.` und das Wort entfällt.
- „Verschiedene OSM-Straßen“ (Regel Eindeutigkeit) heißt: verschiedener Name nach Abzug des Vorsatzes
  („Aleja 29 Listopada“ und „29 Listopada“ sind dieselbe Straße). So hat schon der erste Lauf gerechnet.

Die Ergebnisse des ersten Laufs stehen zum Vergleich im Beleg (Abschnitt „Nachtrag 1“). Die Gegenprobe Dzielnica
der Liste gegen OSM-dzielnica bleibt der Maßstab dafür, ob die zusätzlichen Treffer stimmen.

## Nachtrag 2 (13.11.2026, nach dem zweiten Lauf, vor der Abnahme)

Anlass: Die Gegenprobe des zweiten Laufs fand 8 verortete Einträge, deren Punkt nicht in der dzielnica der Liste
liegt. Gemessen (Abstand des Punkts zum OSM-Polygon der dzielnica laut Liste, Rechen-Koordinatensystem): 76 m bis
3,2 km; ein Paar grenzt nicht aneinander. Das sind nicht nur Grenzlagen. Ob die Liste oder die Verortung irrt, lässt
sich aus den offenen Daten nicht entscheiden. Vorsichtige Regel:

- Ein Treffer, dessen OSM-dzielnica nicht die dzielnica der Liste ist (auch: Punkt in keiner OSM-dzielnica), wird
  Ergebnisklasse `abweichung_dzielnica`: kein Punkt, keine Verknüpfung mit BDOT10k, keine Höhe. Er zählt nicht als
  verortet.
- Die Gegenprobe wird über **alle** Treffer vor diesem Filter berichtet (n = verortet + abweichung_dzielnica).
- Der Abstand jedes abweichenden Treffers zum Polygon der Liste steht als Information im Beleg, mit L.p.
- Der Vergleich mit dem Lauf ohne Nachtrag 1 wird im selben Lauf gerechnet (Namensregeln aus), nicht von Hand
  eingetragen.
- Quoten und Wilson-Grenzen: bei n < 100 ohne Nachkommastelle, sonst eine (Checkliste Punkt 19). Im Beleg gilt das
  Dezimalkomma.

Berichtigung zu Nachtrag 2 (13.11.2026): Der kleinste Abstand steht im Beleg mit 75 m; die 76 m oben stammen aus der
Messung vor dem Nachtrag mit anderem Rundungsweg. Maßgeblich ist der Beleg.

## Nachtrag 3 (13.11.2026, nach der Gegenprüfung, vor der Abnahme)

Anlass: Die Gegenprüfung fand Punkte an Einfamilienhäusern mit Wohnnutzung im Eigentum der Gemeinde, einen
für die verortete Datei unvollständigen Hinweis auf die Verarbeitung, ein irreführendes Feld zum Denkmalstatus und
eine zu starke Aussage zur Typologie. Geändert wird:

- Regel 3 wird enger: Ein Eintrag, dessen verknüpftes BDOT10k-Gebäude die Funktion „budynek jednorodzinny“ hat
  (gleich welche Art; die Lieferung 1261 kennt keine eigene Klasse für Häuser mit zwei Wohnungen), und ein Eintrag
  mit Wohnnutzung (Art enthält M) ohne Gebäude bekannter Funktion bekommen keinen Punkt. Sie werden nur gezählt
  (`punkte.ausgelassen_kleinhaus`).
- Hinweis auf die Verarbeitung je Datei: Die Zählungen sagen „plik nie zawiera adresów“, die verortete Datei nennt
  Geokodierung (OpenStreetMap) und Verknüpfung mit BDOT10k und LoD2. Gleich sein müssen nur Quelle und
  Haftungsklausel.
- Das Feld zur Denkmalangabe in OSM entfällt in den Daten, bis das Denkmalregister vorliegt; die Zahl steht weiter
  im Beleg.
- Typologie: Die Zahl ist keine Obergrenze. Bauten nach 1990 fallen mit hinein, Plattenbauten mit unregelmäßigem
  Grundriss, aus mehreren Teilen oder mit wenigen Nachbarn im Umkreis fallen heraus. Sie ist eine Zählung der
  Merkmalskombination, weder Ober- noch Untergrenze, ungeprüft.
- Der Schlüssel des Vergleichslaufs heißt neutral `ohne_namensregeln`.

## Nachtrag 4 (14.11.2026, Master-Entscheidung zu KR31, vor dem Lauf festgelegt in `pruefen/N1_protokoll.md`, Regel 2, Commit 4b58965)

Anlass: Die Projektleitung hat KR31 am 14.11.2026 bestätigt mit der Auflage, Punkte auch bei öffentlichem Eigentum
nur an Gebäuden mit mindestens 3 Geschossen laut BDOT10k zu zeigen; private Einträge bleiben nur gezählt, ohne
Vergröberung. Geändert wird:

- Regel 3 wird enger: Ein Eintrag bekommt nur dann einen Punkt, wenn sein verknüpftes BDOT10k-Gebäude
  `LICZ_KONDY` ≥ 3 hat. Ohne verknüpftes Gebäude oder ohne Geschosszahl gibt es keinen Punkt.
- Ausgelassene Einträge werden gezählt (`punkte.ausgelassen_unter_3_geschosse`, neben `ausgelassen_kleinhaus`);
  die Schwelle steht in `punkte.geschosse_min`.
- Die Ortsmarke ul. Kościuszki 18 ist kein Punkt im Sinne dieser Regel; ihre Koordinate kommt seit dem 14.11.2026
  aus `skripte/ortsmarke.py` und ist in `daten/denkmale_odbl.js` dieselbe.

## Nachtrag 5 (14.11.2026, nach einer Fachprüfung, vor dem Lauf)

Anlass: Die Typologie zählt in dzielnica I Stare Miasto 238 Kandidaten, davon 65 in Großsiedlungen. Im Stadtkern
(Altstadt, Kazimierz, Kleparz, Wesoła) gibt es praktisch keine Siedlungen aus Großtafeln. Die Regel trifft dicht
stehende Mietshäuser (kamienice) der Blockrandbebauung ebenso wie die Ziegelbauten des Sozialistischen Realismus in
Nowa Huta. Der Grenztext nannte nur neuere Wohnblöcke als Fehlerquelle.

Geändert wird, ohne die Regel zu ändern (die Stichprobe vom 14.11. bezieht sich auf die bestehende Regel):

- Neue Messung „angebaut“ je Kandidat: Länge des Umrisses, die innerhalb von 0,5 m an ein anderes Gebäude der
  BDOT10k grenzt; ab 3 m gilt der Kandidat als angebaut. Gezählt als `blok_angebaut` und `osiedle_angebaut` für die
  Stadt, je Delegatur und je dzielnica. Die Seite zeigt die Zahl je dzielnica in einer eigenen Spalte.
- Der Grenztext nennt kamienice der Blockrandbebauung (Stadtkern) und die Ziegelbauten in Nowa Huta ausdrücklich.
- Ausschließen ist eine eigene Entscheidung: Erst eine Stichprobe nach dzielnica geschichtet zeigt, ob „angebaut“
  echte Blöcke mit abtrennt (Blöcke aus mehreren aneinandergebauten Teilen).

## Nachtrag 6 (14.11.2026, Sichtprüfung der Typologie-Stichprobe eingetragen)

Die Stichprobe (Startwert 20261113; 30 Kandidaten in Großsiedlungen, 10 Kontrollen ohne Kandidatenstatus mit
mindestens 4 Geschossen) wurde am 14.11.2026 am Luftbild geprüft (Andre, Ortofotomapa Geoportal, Gruppen verdeckt).
Das Ergebnis steht als Eingabe in `belege/DS_sichtpruefung.json` (nur Zählungen; Einzelergebnisse je Punkt sind nicht
abgelegt). `skripte/36_sanierung.py` prüft die Zählungen gegen die gezogene Stichprobe, rechnet Quote und
Wilson-Intervall über die entschiedenen Punkte (ja + nein) und schreibt sie nach `daten/sanierung.js`
(`typologie.sichtpruefung`) und in den Beleg. Bewertet wurde, ob ein Wohnblock zu sehen ist, nicht die Bauweise; die
Texte sprechen deshalb von Kandidaten nach Geometrie. Eine strengere Geschoss-Untergrenze wird nur im Beleg an
derselben Stichprobe als Spanne gerechnet; die Regel bleibt.
