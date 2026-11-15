# Vorschläge des Pakets Sanierungsatlas Wohnungsbestand

Stand 13.11.2026, Zweig `Arbeitszweig ds`. Regeln: `pruefen/DS_protokoll.md` (mit Nachträgen 1–3). Quellen und Lizenzen:
`quellen-DS.md`. Lauf und Zählungen: `belege/DS_sanierung_lauf.md`. Vorschläge ohne KR-Nummer; die Nummer vergibt
die Belegschicht. Gemeinsame Dateien hat das Paket nicht geändert. Die Master-Entscheidungen vom 13.11.2026 abends
trägt die Belegschicht in `docs/entscheidungen.md` ein, nicht dieses Paket.

## 1. Eigentum an den neuen Dateien

- **Vorschlag:** neue Zeile „Paket Sanierungsatlas Wohnungsbestand“ in der Eigentümer-Tabelle (`docs/rundgang.md`):
  - `skripte/36_sanierung.py`
  - `daten/sanierung.js`, `daten/sanierung_odbl.js` und die Verträge `daten/schema/sanierung.json`,
    `daten/schema/sanierung_odbl.json` (Vertrag bei der Integration, wie KR15)
  - `pruefen/DS_sanierung.py`, `pruefen/DS_protokoll.md`
  - `belege/DS_sanierung_lauf.md` (erzeugt, nicht von Hand ändern), `belege/rohdaten-DS-2026-11-13.sha256`
  - `quellen-DS.md`, `docs/entscheidungen/DS.md`
- **Neue Datennamen:** `KIEZ_SANIERUNG`, `KIEZ_SANIERUNG_ODBL` (Abschnitt „Schlüssel-Namensräume“).
- **Rundgang:** Schritt „7g Sanierungsatlas“: `skripte/36_sanierung.py`; liest ZBK-PDF und Weiterverwendungsregeln
  aus `zbk/2026-11-13/`, BDOT10k 1261, LoD2 und OSM aus `eingang/`; schreibt die beiden Dateien und den Beleg;
  Prüfung `pruefen/DS_sanierung.py` (schnell, ohne Rohdaten) und `pruefen/DS_sanierung.py --neu` (rund vier
  Minuten, byte-gleich aus den Rohdaten). Werkzeug zusätzlich: Poppler `pdftotext` 26.10.0 (Systempaket, Version im
  Beleg); für den Rundgang unter „Was man braucht“.
- **Datenstand je Thema:** Sanierungsatlas, beide Dateien „echt“.

## 2. Die ZBK-Liste ist weiterverwendbar (kein STOPP)

- **Anlass:** Der Auftrag verlangt die Lizenzprüfung mit wörtlicher Fundstelle oder STOPP.
- **Vorschlag:** Die Liste wird verwendet. Grundlage sind die Regeln der Gmina Miejska Kraków zur Weiterverwendung
  (BIP, `?dok_id=48482`, Abschnitte I bis III, wörtlich in `quellen-DS.md`): Weiterverwendung für jeden Zweck, mit
  Quelle, Zeitpunkt von Erstellung und Abruf, Hinweis auf Verarbeitung und der Haftungsklausel im Wortlaut. Der ZBK
  verweist mit HTTP 302 auf genau diese Regeln und hat keine eigenen.
- **Begründung:** Die Regeln sind eindeutig und widersprechen sich nicht; anders als bei MSIP (KR3) gibt es keine
  zweite, engere Fassung.
- **Neu prüfen, wenn:** der ZBK eigene Regeln veröffentlicht oder die Liste mit einer Lizenzangabe erscheint.

## 3. Datenschutz: Punkte nur für öffentliches Eigentum, keine Adressen

- **Anlass:** Die Liste ist eine Adressliste. Ein Teil der Einträge nennt Bruchteile von Privatpersonen („PR“),
  einige nur Privatpersonen (der ZBK verwaltet auch Eigentum von Personen unbekannten Aufenthalts), einige samoistne
  posiadanie (Zahlen je Klasse: `belege/DS_sanierung_lauf.md`, Schritt 2). Punkt 30 der Checkliste verbietet
  Adressen in den Daten.
- **Vorschlag:** In `daten/` stehen keine Adresse, keine L.p., keine Gebäudekennung. Punkte gibt es nur für Einträge
  der Klassen `gmina`, `skarb_panstwa`, `publiczne_mieszane` ohne samoistne posiadanie; alle anderen nur
  als Zählung je dzielnica. Zusätzlich (Protokoll, Nachtrag 3): kein Punkt an Einfamilienhäusern laut BDOT10k
  (gleich welche Art) und keiner für Wohnnutzung (Art enthält M) ohne Gebäude bekannter Funktion; Zahl
  `punkte.ausgelassen_kleinhaus`, im Beleg Schritt 4. Die BDOT10k-Lieferung 1261 hat keine eigene Klasse für Häuser
  mit zwei Wohnungen; ob solche Häuser unter „budynek jednorodzinny“ oder „budynek wielorodzinny“ stehen, ist nicht
  geprüft. Der Rohtext bleibt unter `$KIEZ_DATEN/abgeleitet/sanierung/`. Im Beleg stehen nicht
  verortete Einträge nur mit L.p., Art und dzielnica.
- **Begründung:** Ein Punkt an einem Mehrfamilienhaus oder einem Nichtwohngebäude der Gemeinde verrät nichts über
  einzelne Personen. Ein Punkt an einem Haus mit privatem Anteil verbindet eine Adresse mit dem Eigentum einer
  Person. Ein Punkt an einem Einfamilienhaus der Gemeinde mit Wohnnutzung sagt über einen bestimmten Haushalt, dass
  er in einer Gemeindewohnung lebt (oft Sozialwohnung). Dass das BIP die Adresse veröffentlicht, stellt sie noch
  nicht in einen neuen Kartenzusammenhang; deshalb die vorsichtigere Variante.
- **Offen (Entscheidung Master/Andre):** ob diese Einträge statt gar nicht vergröbert (etwa auf ein Raster) gezeigt
  werden dürfen, und ob kleine Mehrfamilienhäuser (wenige Wohnungen) dieselbe Regel brauchen. Bis dahin nur gezählt.
- **Verworfen:** alle Punkte (Personenbezug); gar keine Punkte (die Karte des Bestands ist der Kern des Themas);
  Adresse als Beschriftung (Checkliste 30).
- **Neu prüfen, wenn:** eine Rechtsprüfung die Grenze anders zieht.

## 4. Verortung über OSM, deshalb `_odbl`; PRG als Ausweg

- **Anlass:** BDOT10k 1261 hat keine Adressen (Felder von `OT_BUBD_A` im Protokoll). Der Auftrag nennt
  „BDOT10k-/OSM-Adresspunkte“.
- **Vorschlag:** Adressen aus OSM; alles, was davon abhängt (Punkte, Verknüpfung, Höhen je Eintrag,
  Denkmalangabe), steht nur in `daten/sanierung_odbl.js` mit `x-odbl` (KR13, Folgefrage KR3 Variante a).
  `daten/sanierung.js` enthält nur Zählungen aus der Liste selbst und die Typologie aus BDOT10k je Delegatur.
  Die amtlichen PRG-Adresspunkte sind als Handdownload vorgemerkt; mit ihnen könnte die Verortung die ODbL verlassen.
- **Ergebnis:** Zahlen in `belege/DS_sanierung_lauf.md`, Schritt 3. Wohnhäuser (M) lassen sich fast alle verorten,
  Nutzbauten (U) nur gut zur Hälfte, weil die Liste dort oft Grundstücke, Garagen oder Forts statt Adressen nennt.
  Die Gegenprobe der dzielnica fand abweichende Treffer, deren Punkt bis zu Kilometer weit vom Polygon der Liste
  liegt; sie sind nach Nachtrag 2 eine eigene Klasse ohne Punkt und ohne Verknüpfung. Abstände je Treffer mit L.p. im
  Beleg; ob die Liste oder die Verortung irrt, ist nicht geprüft.

## 5. Nachtrag 1 zum Protokoll nach dem ersten Lauf

- **Anlass:** Der erste Lauf fand viele Straßen nicht; darunter Namen in der Form „Nachname Vorname“ („Dietla
  Józefa“).
- **Vorschlag:** Namensvergleich erweitert (zwei Wörter auch umgekehrt, „św“, „… Plac“), als eigener Commit vor dem
  zweiten Lauf. Der Lauf rechnet die Verortung zum Vergleich auch ohne diese Regeln; beide Ergebnisse stehen
  gerechnet im Beleg (Schritt 3, „Vergleichslauf ohne Nachtrag 1“), und `pruefen/DS_sanierung.py` prüft sie gegen
  die Daten.
- **Begründung:** Die Regel betrifft nur die Schreibweise, nicht die Abnahme; die unabhängige Gegenprobe bleibt.
- **Offen:** Eine Änderung der Regeln nach Sicht auf Ergebnisse ist schwächer als eine Vorab-Festlegung. Das steht so
  im Protokoll.

## 6. Typologie nur als Schätzung, nur aus BDOT10k

- **Anlass:** Der Auftrag verlangt Plattenbau- und Großsiedlungs-Kandidaten aus BDOT10k und OSM, ausdrücklich als
  Schätzung, mit offener Methode.
- **Vorschlag:** Kriterien nur aus BDOT10k (Mehrfamilienhaus, mindestens 4 Geschosse, mindestens 250 m²,
  Rechteckigkeit ≥ 0,85; Großsiedlung: mindestens 9 weitere solche Blöcke im Umkreis von 150 m). OSM nur für die
  Zuordnung zu den dzielnice (`_odbl`). Zahlen im Beleg, Schritt 5. Die Verträge erzwingen `schaetzung: true` und `baujahr: false`.
- **Begründung:** OSM-Merkmale (`building:levels`) bringen gegenüber BDOT10k nichts und würden die Datei ohne Not zur
  ODbL-Datei machen. Die Zahl zählt nur die Merkmalskombination, weder Ober- noch Untergrenze, ungeprüft:
  Wohnblöcke nach 1990 fallen mit hinein, Plattenbauten mit unregelmäßigem Grundriss, aus mehreren Teilpolygonen
  oder mit wenigen Nachbarn im Umkreis (lange Scheiben) fallen heraus (Protokoll, Nachtrag 3).
- **Offen:** Sichtprüfung der Stichprobe (Punkte im Beleg, Schritt 5) am Luftbild durch Andre; bis dahin keine
  Trefferquote. Abgleich mit der Literatur (Energy 263, 2023, 125774) nur bibliographisch, keine Zahl daraus.
- **Neu prüfen, wenn:** Baujahre mit klarer Lizenz vorliegen oder die Stichprobe geprüft ist.

## 7. Projektname FuturHist darf erscheinen (Änderung zu KR24)

- **Anlass:** KR24 sagt: „Der Name des Ausgangsprojekts erscheint nicht, solange es keine öffentliche Quelle gibt.“
  Die Seite https://futurhist.eu/demonstrators/krakow/ nennt das Gebäude ul. Kościuszki 18 öffentlich als
  Demonstrator.
- **Vorschlag:** Die Bedingung von KR24 ist erfüllt; die Ortsmarke darf den Projektnamen mit dieser Quelle tragen
  (`ortsmarke.quelle`). Die Lage bleibt `lage_geprueft: false`.
- **Begründung:** Die Quelle ist öffentlich und vom Projekt selbst.
- **Gilt auch für:** das Paket Denkmale und Kamienice, dessen Ortsmarke denselben Ort meint.

## 8. Weitere offene Punkte

- **Verwalter und Registernummer:** Die Liste vom 01.12.2025 hat beide Spalten nicht. Die Fassung vom 01.05.2026,
  die die Themenentscheidung nennt, war im BIP nicht zu finden. Nicht nachgetragen.
- **Denkmalstatus:** Die Liste nennt keinen. OSM `heritage` trifft fast keinen verorteten Eintrag (Zahl im Beleg, Schritt 4),
  darunter nicht
  ul. Kościuszki 18, das laut FuturHist im Register steht. Ein Feld „keine Angabe in OSM“ würde auf einer Seite als
  „kein Denkmal“ gelesen; deshalb steht kein Denkmalfeld in den Daten (Protokoll, Nachtrag 3), die Zahl nur im Beleg.
  Ein brauchbarer Denkmalstatus braucht das NID-Register (Handdownload).
- **WDQS:** Der Master hat WDQS für wenige Abfragen erlaubt; `skripte/abruf.py` (Paket Infrastruktur) sperrt
  `query.wikidata.org` noch. Dieses Paket hat WDQS nicht gebraucht und die Sperre nicht angefasst.
- **Texte:** Ein Namensraum `sanierung.*` für die Seite fehlt noch (Phase Seitenbau, über die Integration). Die Daten tragen
  nur Schlüssel (`art`, `eig`, `hq`, `typ`, Klassen der Verortung).
- **OSM-Nennung je Sprache:** Der vorgegebene Wortlaut „© OpenStreetMap-Mitwirkende“ steht im Kopf und in
  `quellen.osm.vermerk`; für die Seiten liegen pl/en/de in `quellen.osm.vermerk_sprachen`.
- **Schrift:** Die Seite braucht eine Schrift mit allen polnischen Zeichen (Master-Entscheidung); betrifft das
  Seitenpaket, nicht die Daten.
