# Prüfprotokoll Klima: Versiegelung und Grün (vor dem ersten Lauf festgelegt)

Stand 13.11.2026. Dieses Protokoll steht als eigener Commit vor dem ersten Lauf des Generators
`skripte/35_klimat.py`. Spätere Änderungen an Zuordnung, Schwellen oder Regeln bekommen einen eigenen Commit mit
Grund; die alte Fassung bleibt in der Historie. Ergebnisse und Zählungen: `belege/dk_klimat.md`.

## Frage

Welcher Anteil der Fläche ist je Einheit (Stadt, die vier Delegaturen der Verwaltung, dzielnice, 1-km-Zellen)
bebaut, Verkehrsfläche, Grün, Wald und Gehölz, Wasser, Acker oder sonstige Fläche, und wie viel Grün kommt auf
eine Einwohnerin oder einen Einwohner?

## Daten

- **BDOT10k, Paket Powiat 1261** (`$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip`), Schichten der
  Bodenbedeckung `OT_PT??_A` und die Verwaltungseinheiten `OT_ADJA_A`. Koordinatensystem der Datei aus der
  `.prj`, gerechnet wird im Rechen-Koordinatensystem der Ortskonfiguration (`rechen_srid`, KR1).
- **Stadtgrenze:** `OT_ADJA_A` mit `RODZAJ = gmina` und `IDTERYTJED = 1261011` (Gemeinde Kraków).
- **Delegaturen:** `OT_ADJA_A` mit `RODZAJ = dzielnica lub delegatura` (vier Einheiten), Schlüssel
  `IDTERYTJED`. Eine Zuordnung der 18 dzielnice zu den Delegaturen wird nicht behauptet.
- **dzielnice:** Geometrie aus `daten/stadtteile_odbl.js` (Paket Gliederung und Bevölkerung). Solange diese Datei
  `fixture: true` trägt, ist die Ausgabe je dzielnica ebenfalls Beispieldaten.
- **Einwohner:** `daten/kennzahlen.json` (Kachel `einwohner` je Stadtteil und Stadt), Paket Gliederung und
  Bevölkerung. Solange `fixture: true`, gibt es kein Grün je Einwohner (Wert `null` mit Grund) in echten Dateien.
- **1-km-Zellen:** INSPIRE-Gitter in EPSG:3035, Kennung `CRS3035RES1000mN<Nord>E<Ost>` (linke untere Ecke in
  Metern), selbst erzeugt, keine Fremddatei.

## Zuordnung Schicht → Klasse (vollständig)

| Klasse | Schicht (BDOT10k) | Bedingung |
|---|---|---|
| `bebauung` | `PTZB` (zabudowa) | alle Werte von `RODZAJ` |
| `verkehr` | `PTKM` (teren pod drogami kołowymi, szynowymi i lotniskowymi), `PTPL` (plac) | alle |
| `gruen` | `PTTR` (roślinność trawiasta i uprawa rolna) | nur `RODZAJ = roślinność trawiasta` |
| `gruen` | `PTRK` (roślinność krzewiasta), `PTUT` (uprawa trwała: sad, ogródki działkowe, szkółka roślin, plantacja) | alle |
| `wald` | `PTLZ` (las, zadrzewienie, zagajnik) | alle |
| `wasser` | `PTWP` (woda powierzchniowa) | alle |
| `acker` | `PTTR` | nur `RODZAJ = uprawa na gruntach ornych` |
| `sonstige` | `PTGN` (grunt nieużytkowy), `PTSO` (składowisko odpadów), `PTWZ` (wyrobisko i zwałowisko), `PTNZ` (pozostały teren niezabudowany) | alle |

Jede andere Schicht `OT_PT??_A` im Paket oder ein unbekannter `RODZAJ` bei `PTTR` bricht den Lauf ab
(nichts wird still einer Klasse zugeschlagen). Die Fläche je Schicht und je `RODZAJ` steht im Beleg, damit
andere Zuordnungen nachrechenbar sind.

Abgeleitet:

- `bebauung_verkehr` = `bebauung` + `verkehr`. **Näherung, keine gemessene Versiegelung:** `PTZB` umfasst auch
  Höfe und Gärten innerhalb bebauter Flächen, `PTPL` auch unbefestigte Plätze. Abzeichen immer „orientacyjnie /
  Orientierung“, nie „standard urzędowy“.
- `gruen_wald` = `gruen` + `wald`, Grundlage für Grün je Einwohner. Acker zählt nicht als Grün (nicht
  allgemein zugänglich, jahreszeitlich ohne Bewuchs).

## Regeln

1. **Lesen:** Je Schicht muss die Zahl der Datensätze in `.dbf` und `.shp` gleich sein, sonst Abbruch. Als
   gelöscht markierte DBF-Sätze (erstes Byte `*`) werden gezählt und nicht verwendet. Nur Formtyp Polygon (5);
   ein anderer Formtyp bricht ab. Nur Sätze mit `TERYT = 1261`; andere werden gezählt.
2. **Geometrie:** Ringe nach Umlaufsinn zu Außenringen und Löchern zusammengesetzt (Shapefile: Außenring im
   Uhrzeigersinn). Ungültige Geometrien werden mit `make_valid` repariert; Zahl und Flächenänderung stehen im
   Beleg.
3. **Abdeckung:** Innerhalb der Stadtgrenze werden Summe der Klassenflächen (S), Fläche ihrer Vereinigung (U) und
   Stadtfläche (A) bestimmt. Überlappung = S − U, Lücke = A − U. **Schwelle: beide höchstens 0,5 % von A.** Wird
   eine überschritten, ist das ein Befund: Die Ausgaben werden geschrieben, tragen aber `befund` und dürfen nicht
   veröffentlicht werden, bis die Ursache im Beleg geklärt ist.
4. **Nenner der Anteile:** Summe der Klassenflächen innerhalb der Einheit; die Anteile einer Einheit ergeben
   damit 100 %. Daneben steht je Einheit die Fläche innerhalb der Stadt und die Abdeckung (Klassenflächen durch
   Einheitsfläche).
5. **Summen:** Σ der vier Delegaturen = Stadt (Fläche und jede Klassenfläche, Abweichung höchstens 0,1 %).
   Σ der Zellteile innerhalb der Stadt = Stadtfläche (höchstens 0,01 %), Σ der Klassenflächen über die Zellen
   = Klassenflächen der Stadt (höchstens 0,1 %). Mit echten dzielnice: Σ dzielnice = Stadt (höchstens 0,5 %); mit
   Beispieldaten nur berichtet.
6. **Gegenprobe Stadtfläche:** Stadtfläche aus `OT_ADJA_A` gegen die Fläche im BIP der Stadt („RAZEM 32683,90“ ha,
   Quelle dort: Wydział Geodezji Urzędu Miasta Krakowa; Datei `$KIEZ_DATEN/2026-11-13/10_statistik/
   bip_dok242410_mieszkancy_dzielnice_2025.html`). **Schwelle 0,5 %.** Die BIP-Zahl dient nur der Prüfung und wird
   nicht veröffentlicht (Lizenz der BIP-Tabellen offen). Mit echten dzielnice zusätzlich je dzielnica gegen die
   BIP-Fläche, nur berichtet.
7. **Zellen:** Jede 1-km-Zelle, die die Stadtgrenze mit positiver Fläche schneidet. Je Zelle Fläche innerhalb der
   Stadt. Liegt weniger als **10 ha** der Zelle in der Stadt, sind die Anteile `null` (zu kleine Bezugsfläche);
   die Flächen stehen trotzdem in der Summe.
   **dzielnice (Ergänzung vom 13.11.2026, vor dem Lauf mit dieser Fassung):** Liegt von einer dzielnica weniger
   als 10 ha in der Stadt, gilt je nach Herkunft der Grenzen: (a) Grenzen mit `fixture: true`: Anteile `null` mit
   Grund `anteil_grund = bezugsflaeche_zu_klein`; (b) echte Grenzen: **Befund** (die kleinste dzielnica im
   BIP-Abzug von Regel 6 hat 369,90 ha, Zeile XVI; unter 10 ha deutet auf eine kaputte oder verschobene Geometrie,
   nicht auf eine kleine Einheit). Anlass: Die Beispielgrenzen von dzielnica 17 und 18 liegen außerhalb der Stadt
   (0,0 ha); die Anteile hätten einen leeren Nenner gehabt, und `pruefen/dk_klimat.py` meldete „Anteile ohne
   Fläche“. Die Fassung vor dieser Ergänzung liegt in der Historie.
8. **Grün je Einwohner:** `gruen_wald` in m² geteilt durch Einwohner, ganze m². Nur wenn die Einwohnerdatei kein
   `fixture: true` trägt **und** die Einheit mindestens **1.000** Einwohner hat; sonst `null` mit Grund. Nicht je
   Zelle (1-km-Zellen mischen Wald und Wohnen, Werte wären ohne Aussage).
   **Ergänzung vom 13.11.2026 (vor dem Lauf mit dieser Fassung):** In `klimat_stadtteile_odbl.js`, die mit
   Beispieleinwohnern ohnehin `fixture: true` trägt, wird Grün je Einwohner **mit den Beispieleinwohnern gerechnet**
   (Formel und Mindestzahl wie oben), und `einwohner` steht als Zahl in der Datei. Anlass: Der Auftrag verlangt Grün
   je Einwohner „mit D4-Bevölkerung, bis dahin Beispieldaten“; außerdem läuft so der Rechenweg samt Prüfung schon vor
   der Lieferung von D4. In `klimat.js` (echte Datei) bleibt der Stadtwert `null` mit `einwohner_beispieldaten`.
   Hat eine Einheit keine Anteile (Regel 7, unter 10 ha in der Stadt), ist auch Grün je Einwohner `null` mit Grund
   `bezugsflaeche_zu_klein`.
9. **Beispieldaten:** Eine Ausgabedatei trägt `fixture: true` genau dann, wenn eine ihrer Eingaben es trägt.
   `klimat.js` und `klimat_zellen.js` hängen für Flächen nur vom BDOT10k ab; `klimat.js` liest zusätzlich die
   Einwohnerzahl der Stadt für Grün je Einwohner und setzt den Wert nach Regel 8 auf `null`, solange diese
   Beispieldaten sind (die Datei bleibt dadurch echt). `klimat_stadtteile_odbl.js` hängt von
   `stadtteile_odbl.js` und `kennzahlen.json` ab.
   Gründe für `null` stehen in den Daten als Schlüssel (`einwohner_beispieldaten`, `unter_mindestzahl`,
   `bezugsflaeche_zu_klein`), die Sätze dazu in `texte/<lang>/klimat.js`.
10. **Lizenzgrenze:** Werte je dzielnica beruhen auf Grenzen aus OpenStreetMap und stehen deshalb nur in
    `klimat_stadtteile_odbl.js` (vorsichtige Lesart, bis geklärt ist, ob abgeleitete Kennzahlen unter die ODbL
    fallen). Stadt, Delegaturen und Zellen enthalten keine OSM-Anteile.
11. **Runden:** Anteile auf 0,1 Prozentpunkt, Flächen auf 0,1 ha. Die Summenprüfungen laufen auf ungerundeten
    Werten; die gerundeten Anteile einer Einheit dürfen um höchstens 0,5 Punkte von 100 abweichen.
12. **Reproduzierbar:** `skripte/35_klimat.py --pruefen` erzeugt alles neu und vergleicht byteweise mit den
    Dateien unter `daten/`; `pruefen/dk_klimat.py` prüft die veröffentlichten Dateien ohne Rohdaten.
13. **Datenschutz:** nur Flächen und Anteile, keine Objektkennungen, keine Adressen.

## Nicht Gegenstand

- Gemessene Versiegelung (z. B. Copernicus Imperviousness), Baumkronen, Oberflächentemperatur: nicht in diesem
  Lauf, siehe `quellen-dk.md` (Grenzen).
- Geländemodell und Orthofoto: für Flächenanteile nicht nötig.
