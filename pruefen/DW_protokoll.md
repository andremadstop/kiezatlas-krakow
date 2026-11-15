# Vorab-Festlegung Paket Wohnungsmarkt (DW): Mediane Preis je m² aus dem Rejestr cen nieruchomości

Stand 13.11.2026, festgelegt **vor dem ersten Lauf auf echten Daten** (Belegstandard, Punkt 18). Dieser Commit
enthält nur die Regeln; Skript, Datenvertrag und Prüfung folgen in eigenen Commits. Eine spätere Änderung an
diesen Regeln steht als eigener Abschnitt „Änderung <Datum>“ unten, mit Grund, und nie im selben Commit wie
neue Ergebnisse.

## Frage

Wie hoch ist der mittlere Kaufpreis je Quadratmeter Wohnfläche für Wohnungen (lokale mieszkalne) je dzielnica
und Kalenderjahr, getrennt nach Erst- und Weiterverkauf (rynek pierwotny / wtórny)?

Kennzahl: **Median** der Einzelwerte „Preis je m²“ (zł/m², brutto wie im Register), auf ganze Złoty gerundet,
mit der Zahl der Fälle **n**. Kein Mittelwert, keine Extremwerte, keine Perzentile.

## Eingabe

- Handdownload GeoPackage des GUGiK für Powiat 1261 (Kraków) aus dem Kartenmodul „Pobierz dane“ (Gruppe
  „Dane do pobrania“ > „Dane powiatowe“ > „Rejestr Cen Nieruchomości“), abgelegt unter
  `$KIEZ_DATEN/eingang/rcn/`. Dateiname und erwartetes Format: `quellen-DW.md`.
- Stadtteilgrenzen: `daten/stadtteile_odbl.js` (Eigentum Paket Gliederung und Bevölkerung), WGS 84.
- Ohne Eingabedatei läuft das Skript nur mit `--beispiel` auf einer erzeugten Beispieldatei im selben Format;
  die Ausgabe trägt dann `fixture: true`.

## Spalten (Annahme, an echten Daten nicht geprüft)

Die Spaltennamen der GUGiK-Datei sind nicht bekannt. Das Skript sucht je Bedeutung eine Spalte aus einer festen
Liste von Namen (Attributnamen des RCN-Modells nach dem Rozporządzenie w sprawie ewidencji gruntów i budynków
vom 27.07.2021 in camelCase oder snake_case; Wissen, nicht geprüft) und **bricht ab**, wenn eine Pflichtspalte
fehlt, mit der Liste der vorhandenen Spalten. Ebenso bricht es ab, wenn in einer Codeliste ein unbekannter Wert
vorkommt. Eine Erweiterung der Namensliste oder der Werte ist eine Änderung dieses Protokolls.

## Filter (in dieser Reihenfolge, je Schritt gezählt)

| Nr | Schritt | Regel |
|---|---|---|
| F0 | Zeilen der Lokal-Ebene | alle Zeilen der Tabelle mit Lokalen (Spalten für Funktion und Nutzfläche des Lokals vorhanden) |
| F1 | Dubletten | gleiche Transaktion und gleiche Lokalkennung nur einmal |
| F2 | Wohnung | Funktion des Lokals = Wohnung (lokal mieszkalny) |
| F3 | freier Markt | Art der Transaktion = freier Markt (wolny rynek); ausgeschlossen sind u. a. Verkäufe der Gemeinde ohne Ausschreibung (oft mit Nachlass an Mieter) und Ausschreibungen |
| F4 | volles Recht | Anteil am Recht = 1/1 (fehlt die Angabe, gilt die Zeile als ausgeschlossen) |
| F5 | eine Wohnung je Transaktion | in der Transaktion genau ein Lokal (sonst ist der Preis je Wohnung nicht trennbar) |
| F6 | Preis | Preis des Lokals brutto > 0; fehlt er, dann Preis der Transaktion brutto, aber nur, wenn in der Datei kein anderes Objekt (Parzelle, Gebäude) zu derselben Transaktion gehört; beide Wege werden getrennt gezählt |
| F7 | Fläche | Nutzfläche des Lokals > 0 |
| F8 | Plausibilität | 8 m² ≤ Nutzfläche ≤ 400 m² und 1.000 zł/m² ≤ Preis je m² ≤ 100.000 zł/m² (weite Grenzen gegen Tippfehler, keine Anpassung nach Sicht der Daten) |
| F9 | Datum | Datum des Dokuments (data sporządzenia dokumentu) vorhanden; Jahr = Kalenderjahr dieses Datums |
| F10 | Lage | Geometrie vorhanden, Bezugssystem aus der Datei bekannt; Punkt auf der Fläche des Objekts liegt in genau einer dzielnica; sonst als „außerhalb“ gezählt |

Preis je m² = Preis (F6) ÷ Nutzfläche des Lokals (ohne Nebenräume).

## Ausgabe und Datenschutz

- Je dzielnica, Jahr und Markt (`ogolem` = beide, `pierwotny`, `wtorny`): Median und n. Gleiches für die ganze
  Stadt aus allen Zeilen, die einer dzielnica zugeordnet sind.
- **Mindestfallzahl 10:** Ist n < 10, bleibt der Median `null` mit Grund `n_unter_minimum`; ist n = 0, mit Grund
  `keine_transaktionen`. n selbst wird veröffentlicht (eine Fallzahl verrät keinen Kaufpreis).
- Kein Minimum, Maximum oder Perzentil: jeder Extremwert ist ein einzelner, über das Grundbuch auffindbarer Kauf.
- Keine Zeile je Transaktion in `daten/`, `belege/` oder im Repo; die Rohdatei bleibt unter `$KIEZ_DATEN/eingang/`.
  Keine Adresse, keine Parzellen-, Gebäude- oder Lokalkennung, keine Dokumentnummer in einer Ausgabe.
- Das laufende Jahr gilt als unvollständig, wenn das jüngste Dokumentdatum der Datei vor dem 31.12. liegt; die
  Ausgabe nennt dieses Jahr und das Datum (`jahr_teilweise`, `datenstand`).

## Prüfung

`pruefen/DW_mieszkania.py` prüft die Ausgabe gegen diese Regeln (kein Median bei n < 10, jeder `null` mit Grund,
keine verbotenen Felder, Zählungen der Schritte fallen monoton, Summe der n gleich der letzten Zählung) und führt
eine Gegenprobe mit absichtlich falschen Daten aus, die die Prüfung erkennen muss.

## Grenzen (vorab benannt)

- Das Register erfasst Kaufverträge, nicht Angebotspreise und nicht Mieten; Verdrängung lässt sich daraus nur
  mittelbar lesen.
- Ob das GUGiK-Paket für Kraków vollständig ist (alle Jahre, alle Verträge, Geometrie), ist nicht geprüft.
- Die Zuordnung zur dzielnica hängt an den Grenzen aus `daten/stadtteile_odbl.js`.
- Brutto heißt: im Erstverkauf mit Umsatzsteuer, im Weiterverkauf meist ohne; die Trennung nach Markt fängt das
  auf, die Spalte `ogolem` mischt beides.

## Ergänzung 13.11.2026, vor dem ersten Lauf (auch vor dem ersten Lauf auf Beispieldaten)

Beim Schreiben des Skripts fiel eine Lücke auf, die das Protokoll oben offen ließ:

- **Markt fehlt:** Ist die Art des Marktes leer, zählt die Zeile nur in `ogolem`, nicht in `pierwotny` oder
  `wtorny`. Ein nicht leerer, unbekannter Wert führt wie bei den anderen Codelisten zum Abbruch. Die Zahl solcher
  Zeilen steht in der Ausgabe (`kontrolle.ohne_markt`). Darum ist `n(ogolem)` mindestens `n(pierwotny) + n(wtorny)`
  und nicht immer gleich.
- **Stadtwert:** Der Wert für die ganze Stadt kommt aus denselben Zeilen wie die Stadtteile (nach F10), damit
  Stadt und Stadtteile dieselbe Grundlage haben.
- **Rundung:** Median auf ganze Złoty, halbe aufwärts (bei gerader Fallzahl ist der Median das Mittel der beiden
  mittleren Werte).

## Änderung 14.11.2026, vor dem ersten Lauf auf echten Daten

Gesehen bis zu diesem Abschnitt: Tabellen- und Spaltennamen der GUGiK-Datei (`--spalten`), Häufigkeiten der
Codelisten (Funktion, Art der Transaktion, Markt, Anteil, Art und Recht der Immobilie) und die Zahl der Zeilen je
Dokumentjahr samt Zahl leerer Felder. Kein Preis, keine Fläche, keine Adresse, keine Partei, keine Dokumentnummer.

- **Spaltennamen** (die Annahme oben traf nicht; die Datei nutzt snake_case mit Präfix): Tabelle
  `transakcje_lokale`; `tran_oznaczenie_trans` (Transaktion), `lok_id_lokalu`, `tran_rodzaj_trans`,
  `tran_rodzaj_rynku`, `nier_udzial`, `dok_data`, `lok_funkcja`, `lok_pow_uzyt`, `lok_cena_brutto`,
  `tran_cena_brutto`. Die Tabellen `transakcje_dzialki` und `transakcje_budynki` tragen dieselbe Spalte
  `tran_oznaczenie_trans` und zählen für F6 als „andere Objekte“. Bezugssystem EPSG:2180 aus der Datei.
- **Codewerte ergänzt**, alle als „andere“ (fallen in F2 bzw. F3 heraus, keine Änderung der Regel):
  Funktion `handlowoUslugowa`, `biurowa`, `produkcyjna`; Art der Transaktion `sprzedazZBonifikata`,
  `sprzedazWPostepowaniuEgzekucyjnym`, `sprzedazNaCelPubliczny`. Bekannt waren schon `mieszkalna`, `garaz`, `inna`,
  `wolnyRynek`, `sprzedazBezprzetargowa`, `sprzedazPrzetargowa`, `rynekPierwotny`, `rynekWtorny`.
- **Folge einer bestehenden Regel, vorab benannt:** Bis 2015 fehlen in der Datei fast überall Anteil und
  Lokalkennung (2006–2015: über 99 % leer; 2016: 729 von 21.338; ab 2017: höchstens 20 je Jahr). F4 schließt
  Zeilen ohne Anteil aus. Die Regel bleibt; die Zeitreihe ist damit faktisch erst ab 2016/2017 belastbar, das steht
  unter Grenzen und auf der Seite. Einzelne Dokumentdaten vor 2005 (7 Zeilen, z. B. 1900) bleiben drin und fallen
  durch die Mindestfallzahl.
- **Datenschutz unverändert:** Das Skript liest `tran_sprzedajacy`, `tran_kupujacy`, `lok_adres`, `dok_oznaczenie`
  und `dok_tworca` nicht (sie stehen in keiner Bedeutung der Liste).

## Hinweis 14.11.2026, nach dem abgebrochenen ersten Lauf auf echten Daten

Der erste Lauf brach mit Rückgabe 4 in der sekundären Unterdrückung ab, nicht an Spalten oder Codewerten. Die
Behebung steht als Nachtrag 4 zu Regel 4 in `pruefen/N1_protokoll.md`; die Regeln F0 bis F10 und die Spalten- und
Codelisten dieses Protokolls bleiben unverändert. Dabei gesehen (nur Zählungen): Alle Zeilen, die F10 ausschließt,
haben keine Geometrie; keine liegt außerhalb der dzielnice. Sie häufen sich in den Jahren 2016 bis 2020. Werte je
dzielnica sind damit erst ab 2021 belastbar, 2020 nur zum Teil; das steht zusätzlich zur Grenze bis 2015 (fehlender
Anteil) im Beleg und auf der Seite.

## Hinweis 14.11.2026, Datenstand nach der Prüfung des ersten Ergebnisses

Keine Regeländerung. Der Abschnitt „Ausgabe und Datenschutz“ nennt als Datenstand das jüngste Dokumentdatum
**der Datei**. Das Skript nahm bis hierher das jüngste Datum unter den ausgewerteten Käufen (nach F10) und wich
damit vom Protokoll ab. Es folgt jetzt dem Protokoll: jüngstes Dokumentdatum über alle Tabellen der Datei, vor
den Filtern. Medianwerte und Fallzahlen ändern sich dadurch nicht, nur `datenstand`. Der Beleg nennt zusätzlich,
dass das Geoportal ein älteres Aktualisierungsdatum angibt, als die Dokumente der Datei reichen.

## Hinweis 14.11.2026, Grenze der Zeitreihe nach dem Ergebnis

Keine Regeländerung. Die „Folge einer bestehenden Regel“ in der Änderung vom 14.11.2026 („Zeitreihe faktisch
erst ab 2016/2017 belastbar“) war vor dem Lauf allein aus F4 abgeleitet. Nach F10 trägt sie nicht: Bis 2018
erreicht kein Jahr die Mindestfallzahl für die Stadt, und 2019 und 2020 beruhen nur auf einem kleinen bzw.
einem Teil der Käufe mit Datum (Anteile je Jahr im Beleg, aus den Zählungen gerechnet). Seite, Beleg und Doku
nennen deshalb als Grenze: Werte der ganzen Stadt erst ab 2021 weitgehend vollständig. Der Satz in der Änderung
bleibt als Stand vor dem Lauf stehen.

## Änderung 14.11.2026 (KR55): Veröffentlichung erst ab 2019, Verschärfung des Datenschutzes nach Sicht der Daten

Anlass: Eine unabhängige Prüfung des Ergebnisses hat je unterdrückter Fallzahl (`n_unter_minimum`) den kleinsten
und größten ganzzahligen Wert im ganzen veröffentlichten Gleichungssystem gerechnet (`pruefen/N1_protokoll.md`,
Regel 4, Nachträge 3 und 4). Keine Zahl ist eindeutig, aber bei 42 der 74 unterdrückten Felder bleiben nur zwei
mögliche Werte, meist 1 oder 2. Betroffen sind ausschließlich die Jahre 1900, 1901, 2006, 2007, 2009, 2012, 2016
und 2018: Dort ist der jeweils andere Markt mit n = 0 veröffentlicht und `ohne_markt` = 0, so dass die Stadt- und
die Stadtteilzahl nur noch zwischen zwei Werten schwanken. Eine Spanne von zwei Werten schützt einen Einzelkauf
kaum. Diese Jahre zeigt die Seite ohnehin nicht (keine Stadtzahl ab der Mindestfallzahl).

Gesehen bis zu diesem Abschnitt: nur die veröffentlichte Datei `daten/mieszkania_odbl.js` und die Zählung der
Spannen; keine Rohdaten, keine Fallzahl unter der Mindestzahl. Dies ist eine Verschärfung nach Sicht der Daten,
keine Lockerung; die Regeln F0 bis F10 bleiben.

Geändert wird:

- **F11, Jahr ab 2019:** Nach F10 bleiben nur Käufe mit Dokumentjahr ab 2019 (`erstes_jahr` = 2019, Konstante im
  Erzeuger, veröffentlicht unter `regeln.erstes_jahr`). Die Jahre davor stehen nicht in `daten/mieszkania_odbl.js`,
  weder für die Stadt noch je dzielnica. Der Beleg nennt nur die Zahl der so entfallenen Käufe („vor 2019 nicht
  veröffentlicht“), keine Aufteilung nach Jahr, dzielnica oder Markt.
- `kontrolle.ausserhalb` bleibt F9 − F10. `kontrolle.ohne_markt` zählt nach F11.
- In der sekundären Unterdrückung und in der Differenzprobe gilt die Summe über die Jahre jetzt gegen die letzte
  Zählung (F11) statt F10 (`pruefen/N1_protokoll.md`, Nachtrag 3, dritter Punkt).
- Der Erzeuger schreibt zusätzlich in den Beleg, wie viele unterdrückte Fallzahlen danach noch eine Spanne von
  höchstens zwei ganzzahligen Werten haben. Eine unabhängige Rechnung außerhalb des Erzeugers rechnet dieselbe Zahl
  nach. Ist sie größer als 0, wird sie im Beleg benannt und gemeldet; die Regeln werden deshalb nicht weiter
  geändert, ohne neue Entscheidung.

Grund für 2019 und nicht 2021: Ab 2019 hat die Stadt in jedem Jahr eine veröffentlichte Fallzahl ab der
Mindestzahl. Dass 2019 und 2020 nur einen Teil der Käufe abbilden (fehlende Lage), bleibt eine benannte Grenze
(Hinweis 14.11.2026 oben), keine Unterdrückung.
