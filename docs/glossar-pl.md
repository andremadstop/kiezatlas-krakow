# Glossar Fachbegriffe Polnisch, Englisch, Deutsch

Stand: 15.11.2026 (Gegenlesen durch drei Sprachmodelle, `docs/entscheidungen/p4b-polnisch.md`; davor 13.11.2026). **Status aller Einträge: Vorschlag.** Vor der Veröffentlichung prüft eine polnische
Fachmuttersprachlerin oder ein Fachmuttersprachler die Begriffe, am besten der Lehrstuhl selbst. Besonders offen
sind „Beleg“, „Taktklasse“ und „Gitterzelle“ (Abschnitt „Zur Prüfung zuerst“).

Regeln für die Oberfläche (gelten für `texte/<lang>/*.js` und die Langtexte):

- Eigennamen bleiben polnisch, auch in EN und DE: Namen der dzielnice („Dzielnica I Stare Miasto“), Behörden (GUS,
  GUGiK, GIOŚ, ZTP, NID), Datensätze (BDOT10k, NSP 2021, Rejestr cen nieruchomości).
- Lizenzvermerke bleiben wörtlich in der Originalsprache und werden höchstens erläutert, nie übersetzt.
- Ein Begriff, eine Übersetzung: Steht ein Begriff hier, nutzt jede Textdatei genau diese Form. Abweichungen gehen
  über dieses Glossar, nicht still in einer einzelnen Datei.
- Zahlen, Prozente und Daten formatiert immer `KIEZ_I18N.fmt`, nie der Text (pl-PL: Dezimalkomma, geschütztes
  Leerzeichen als Tausendertrenner ab fünf Stellen, Prozentzeichen ohne Leerzeichen: „24,2%”, wie `Intl` für pl-PL nach
  CLDR; geändert am 14.11.2026, vorher „mit Leerzeichen“, was der eigenen Formatierung widersprach). Wo ein Skript das
  Prozentzeichen selbst anhängt, nimmt es die Form von `fmt.anteil` (pl und en ohne, de mit geschütztem Leerzeichen).
  Negative Werte mit echtem Minuszeichen „−“ (U+2212), nicht mit dem Bindestrich.
- Anrede im Polnischen: unpersönlich oder Plural („Sprawdź“, „Wybierz“; Fragen ohne Geschlechtsform wie „Widzisz
  błąd?“ statt „Znalazłeś błąd?“).
- Herkunft: „Bauvorlage“ = Recherche zur Bauvorlage mit Fundstelle dort (Abschnitt 3); „Wissen“ = aus allgemeiner
  Sprachkenntnis, ohne eigene Fundstelle, darum ausdrücklich prüfen.

## Raum und Gliederung

| Deutsch | Polnisch | Englisch | Herkunft, Anmerkung |
|---|---|---|---|
| Stadtteil (amtlich, 18 in Kraków) | dzielnica, Plural dzielnice; mit Nummer „Dzielnica I Stare Miasto“ | district | Bauvorlage (Radio Kraków). Im Satz Lokativ „w Dzielnicy …“ aus der Ortskonfiguration, nicht im Text beugen |
| Bezirksrat | Rada Dzielnicy | district council | Bauvorlage |
| ehemaliger Stadtbezirk, heute Verwaltungseinheit (4 in Kraków: Śródmieście, Krowodrza, Podgórze, Nowa Huta) | delegatura (dawna dzielnica), Plural delegatury (dawne dzielnice) | historic borough (delegatura) | Vorschlag 14.11.2026, Wissen; zur Prüfung zuerst. Nicht „dzielnica historyczna“: in der Denkmalpflege heißt das ein historisches Viertel (z. B. der geschützte Stadtgrundriss von Nowa Huta) |
| Stadtteilgrenzen | granice dzielnic | district boundaries | Wissen; Grundlage OpenStreetMap (ODbL), Quellenangabe wörtlich |
| statistischer Bezirk (GUS) | rejon statystyczny, Plural rejony statystyczne | statistical area | Wissen; Eigenname der GUS-Gliederung, in EN/DE zusätzlich polnisch nennen |
| kleinere Planungseinheit | jednostka urbanistyczna / osiedle | planning unit / neighbourhood | Bauvorlage („aus Wissen“) |
| Gitterzelle | oczko siatki / komórka siatki; amtlich „siatka kilometrowa (grid)“ | grid cell | Bauvorlage (GUS NSP 2021); zur Prüfung zuerst. Auf den Seiten durchgehend „komórka siatki“, nicht „kwadrat“ |
| Gitter, 1 km | siatka 1 km | 1 km grid | Wissen |
| ganze Stadt | całe miasto | whole city | Wissen |
| Stadt und Umland | miasto i strefa podmiejska | city and surroundings | Wissen |

## Bevölkerung und Kennzahlen

| Deutsch | Polnisch | Englisch | Herkunft, Anmerkung |
|---|---|---|---|
| Einwohnerinnen und Einwohner | mieszkańcy | residents | Wissen |
| Einwohnerdichte | gęstość zaludnienia | population density | Wissen |
| Volkszählung 2021 | Narodowy Spis Powszechny Ludności i Mieszkań 2021 (NSP 2021) | National Census 2021 | Eigenname, bleibt polnisch |
| Anteil | udział | share | Wissen |
| Stichtag der Volkszählung | stan na {datum} (Ustawa o NSP 2021, art. 1 ust. 2: „według stanu na dzień 31 marca 2021 r., godz. 24.00“); GUS-Methodik: moment krytyczny spisu | reference date | Vorschlag 14.11.2026; Wortlaut des Gesetzes am 14.11.2026 über api.sejm.gov.pl (DU/2019/1775) nachgelesen. Nicht „dzień odniesienia“ oder „data referencyjna“ für die NSP; „data referencyjna“ bleibt nur in den Potsdamer Texten zum Zensus 2022 |
| Kennzahl | wskaźnik | indicator | Wissen |
| Median der Geschosszahl | mediana liczby kondygnacji | median number of storeys | Vorschlag 15.11.2026; nicht „mediana kondygnacji“ |
| Quintile (Klassen der Karte) | przedziały kwintylowe (po jednej piątej komórek) | quintiles | Vorschlag 15.11.2026; nicht „piąte części“ |
| keine Angabe | brak danych | no data | Wissen; ersetzt das deutsche „k. A.“ |
| unscharf (zu kleine Grundgesamtheit, grau) | niepewne (zbyt mała liczba) | uncertain (too few) | Wissen; die Grau-Erklärung nennt die Schwelle als Zahl. Nie „nieostre“ (Lehnübersetzung, 15.11.2026 auf allen Seiten ersetzt) |
| Unschärfe an den Grenzen (Flächen- gegen Mittelpunktregel) | niepewność przypisania na granicach | uncertainty at the boundaries | Vorschlag 15.11.2026; nicht „nieostrość“ |
| durch Geheimhaltung verändert (Eurostat-Gitter) | zniekształcone wskutek zastosowania ochrony tajemnicy statystycznej | perturbed by statistical confidentiality | Vorschlag 15.11.2026; die Werte sind verändert, nicht nur unsicher |
| Geheimhaltung | tajemnica statystyczna | statistical confidentiality | Wissen |
| rund (gerundete Zahl) | około | about | Wissen |

## Gebäude, Denkmale, Wohnen

| Deutsch | Polnisch | Englisch | Herkunft, Anmerkung |
|---|---|---|---|
| Bauzeit / Baujahr | okres budowy budynku, wiek zabudowy / rok budowy | construction period / year of construction | Bauvorlage („aus Wissen“). Für Kraków nur bei Denkmalen; keine Flächenaussage zu Baujahren |
| Bürger- bzw. Mietshaus (kamienica) | kamienica, Plural kamienice | tenement house (kamienica) | Bauvorlage; in EN/DE beim ersten Vorkommen mit polnischem Wort. Ohne Epoche: in Kraków reichen kamienice vom Mittelalter (Rynek, Kazimierz) bis ins 20. Jahrhundert; „Gründerzeit-Mietshaus“ verworfen am 14.11.2026 |
| Denkmal (eingetragen) | zabytek (wpisany do rejestru zabytków) | listed monument | Wissen |
| Denkmalregister | rejestr zabytków | register of monuments | Wissen; Herausgeber NID |
| OSM-Schlüssel heritage | znacznik <code>heritage</code> (OpenStreetMap) | heritage tag | Vorschlag 15.11.2026; nicht „znacznik dziedzictwa“; „oznaczenie zabytku“ nur für Register und OSM zusammen; „znacznik“ statt „tag“ |
| Wikidata | Wikidane (beim ersten Vorkommen „Wikidane (Wikidata)“) | Wikidata | Polnische Eigenbezeichnung des Dienstes; im polnischen Fließtext durchgehend „Wikidane“ |
| Komplex (BDOT10k, z. B. historisches Bauensemble, Festung) | kompleks, Plural kompleksy (BDOT10k); Art: zespół zabudowy historycznej, twierdza lub forteca … | complex | Klassenname wie im Download (Ebene bdot_kompleksy); „zespół“ nur als Teil der Art „zespół zabudowy historycznej“ |
| kommunales Denkmalverzeichnis | gminna ewidencja zabytków | municipal heritage record | Themenentscheidung vom 13.11.2026, Eigenname |
| Geschosse | kondygnacje | storeys | Wissen |
| Grundfläche eines Gebäudes (in m²) | powierzchnia obrysu; Formel „powierzchnia obrysu × liczba kondygnacji“ | footprint area | Vorschlag 15.11.2026; „obrys“ allein ist der Umriss, keine Fläche |
| Bebauungsanteil (Anteil der Gebäudegrundfläche an der Fläche einer Einheit) | udział powierzchni zabudowy (budynkami); in Feldbeschreibungen der Downloads „wskaźnik zabudowy (udział powierzchni zabudowy …)“ | building coverage | Vorschlag 14.11.2026, Wissen. Nicht „intensywność zabudowy“: das ist im Planungsrecht (ustawa o planowaniu i zagospodarowaniu przestrzennym, Festsetzungen im MPZP) die Geschossflächenzahl |
| Geschossflächenzahl, Näherung (Σ Grundfläche × Geschosse / Fläche) | przybliżona intensywność zabudowy | approximate floor area ratio | Wissen; nur für diese Näherung, nie für den Bebauungsanteil |
| Gebäudefunktion | funkcja budynku | building use | Wissen; Merkmal in BDOT10k |
| Kaufpreise (Register) | ceny transakcyjne (Rejestr cen nieruchomości) | transaction prices | Wissen; nur aggregiert veröffentlichen |
| Plattenbau | blok z wielkiej płyty, Plural bloki z wielkiej płyty | large-panel block | Vorschlag 14.11.2026, Wissen. Nicht „blok z prefabrykatów“. Ob „kandydaci na bloki“ (Personalform für Gebäude) besser „budynki typowane jako bloki“ heißt, ist offen (Zur Prüfung zuerst) |
| Plattenbausiedlung; Block in einer solchen | osiedle z wielkiej płyty / osiedle blokowe; „blok na osiedlu blokowym“, „na osiedlach blokowych“ | (large-panel) housing estate | Vorschlag 14.11.2026, Wissen. osiedle ist der Siedlungsverband, nie das einzelne Gebäude; Präposition „na osiedlu“, nicht „w osiedlu“ |
| in Nutzung (Gebäudestatus BDOT10k) | eksploatowany (kategoria istnienia w BDOT10k) | in use (eksploatowany) | Wert des Merkmals KAT_ISTNIE; nicht „w użytkowaniu“ oder „w eksploatacji“ |
| Kurzzeitvermietung | najem krótkoterminowy | short-term rental | Wissen; neutral, ohne Wertung |
| Gebäudeliste des ZBK | wykaz ZBK (amtlich „Wykaz budynków i obiektów w zarządzie ZBK“) | ZBK list | Vorschlag 15.11.2026; nicht „lista ZBK“ |
| Weiterverwendung (Informationen des öffentlichen Sektors) | ponowne wykorzystywanie | re-use | Begriff der ustawa o otwartych danych i ponownym wykorzystywaniu informacji sektora publicznego; nicht „wykorzystanie“ |

## Versorgung, Erreichbarkeit, Nahverkehr

| Deutsch | Polnisch | Englisch | Herkunft, Anmerkung |
|---|---|---|---|
| Erreichbarkeit | dostępność (przestrzenna, komunikacyjna, piesza) | accessibility | Bauvorlage (Guzik, PK; GUS) |
| zu Fuß erreichbar | w zasięgu dojścia pieszego | within walking distance | Wissen |
| Fußweg (über das Wegenetz) | dojście piesze (siecią dróg) | walking route (along the network) | Wissen; nie mit Luftlinie verwechseln. „droga piesza“ bleibt als Name der Messart neben „linia prosta“ (Schalter, Spalten); im Fließtext „dojście piesze“ |
| Luftlinie | odległość w linii prostej | straight-line distance | Wissen |
| Haltestelle | przystanek | stop | Wissen |
| Taktklasse | Vorschlag: klasa częstotliwości kursowania | service frequency class | Bauvorlage („aus Wissen“); zur Prüfung zuerst |
| Takt (Abfahrten je Stunde) | częstotliwość kursowania (odjazdy na godzinę) | frequency (departures per hour) | Wissen |
| Haltestelle der Klasse I oder II | przystanek klasy I lub II (co najmniej dwa odjazdy na godzinę) | class I or II stop (at least two departures per hour) | Vorschlag 14.11.2026; zur Prüfung zuerst. Nicht „przystanek z częstymi odjazdami / z częstym kursowaniem“ („frequent“, „dichter Takt“): Klasse II beginnt bei zwei Abfahrten je Stunde (Halbstundentakt), das gilt in der Verkehrsplanung nicht als häufig |
| stärkere Richtung (Richtung mit mehr Abfahrten) | kierunek z większą liczbą odjazdów | direction with more departures | Vorschlag 14.11.2026, Wissen; nicht „silniejszy kierunek“ (Lehnübersetzung). Abstand über das Wegenetz: „w odległości do … m dojściem pieszym“, nicht „w promieniu“ (das ist Luftlinie) |
| Pünktlichkeit | punktualność | punctuality | Wissen |
| Einrichtung (Schule, Kita, Arzt …) | placówka | facility | Wissen |
| Versorgung (Planer: Werte, Tabelle, Datei) | dostępność usług | service provision | Vorschlag 15.11.2026 (drei Sprachmodelle: „zaopatrzenie“ meint Waren und Medien). Verträgt sich mit „dostępność“ (Erreichbarkeit) und dem Seitennamen „Dostępność“: die Versorgungswerte sind die Erreichbarkeit der Dienste. Gruppe „Versorgung und Gesundheit“ (Ärzte, Apotheken): „Usługi i zdrowie“. Potsdamer Restschlüssel der Gegenprobe bleiben unverändert |
| Schulregister | Rejestr Szkół i Placówek Oświatowych (RSPO) | school register (RSPO) | amtlicher Name (KSDO); nicht „rejestr szkół i przedszkoli“ |
| in die Entfernung einbezogen | uwzględniane przy obliczaniu odległości | included in the distance calculation | Vorschlag 15.11.2026; nicht „liczy się do odległości“ (auch sonst „liczyć się“ nicht für „zählen zu“) |
| Kita | przedszkole; Krippe: żłobek | kindergarten; nursery | Wissen |
| Richtwert (amtlich) | standard urzędowy | official standard | Bauvorlage (Paket Versorgung); nur mit amtlicher Fundstelle |
| Richtwert (Orientierung, nicht amtlich) | wartość orientacyjna | guide value | Wissen; als Status nie das Substantiv „orientacja“ |
| Richtwert aus einem Dokument (Planer) | wartość odniesienia | reference value | Vorschlag 15.11.2026, wie `planer.e.richtwert`; nicht „wartość normatywna“ |

## Klima und Luft

| Deutsch | Polnisch | Englisch | Herkunft, Anmerkung |
|---|---|---|---|
| Hitzeinsel | miejska wyspa ciepła | urban heat island | Bauvorlage (Akademia Bialska) |
| Versiegelung | uszczelnienie gruntu / powierzchnia nieprzepuszczalna | soil sealing / impervious surface | Wissen; zur Prüfung zuerst: die polnischen EU-Dokumente zu „soil sealing“ sagen meist „zasklepianie gleby“ |
| Bebauung und Verkehrsflächen (BDOT10k) | zabudowa i tereny komunikacyjne | built-up and transport areas | Vorschlag 15.11.2026; nicht „zabudowa i komunikacja“ |
| Grünfläche | teren zieleni | green space | Wissen |
| Grün und Wald (Flächenanteil, Grün je Einwohner) | zieleń i lasy | green space and woodland | Wissen; Plural „lasy“ auf allen Seiten |
| Oberflächentemperatur | temperatura powierzchni | land surface temperature | Wissen |
| Luftqualität, Messstation | jakość powietrza, stacja pomiarowa | air quality, monitoring station | Wissen; Herausgeber GIOŚ |
| Feinstaub | pył zawieszony (PM10, PM2,5) | particulate matter | Wissen; Dezimalkomma im Polnischen |
| Kohleverbot (2019) | zakaz palenia węglem i drewnem („uchwała antysmogowa“) | ban on burning coal and wood | Wissen; Quelle im Text nennen |

## Belege und Methode

| Deutsch | Polnisch | Englisch | Herkunft, Anmerkung |
|---|---|---|---|
| Beleg | potwierdzenie / zapis weryfikacji; Fußnote: przypis | evidence / verification record | Bauvorlage („aus Wissen“); zur Prüfung zuerst |
| Quelle | źródło | source | Wissen |
| Datenquellen | źródła danych | data sources | Bauvorlage |
| Methode | metodologia | methodology | Bauvorlage |
| Konfidenzintervall (Wilson) | 95-procentowy przedział ufności (metoda Wilsona) | 95% confidence interval (Wilson) | Wissen; „przedział Wilsona“ allein ist unvollständig |
| Grenzen (der Aussage) | ograniczenia | limitations | Bauvorlage |
| Stand (Datum der Daten) | stan na | as of | Wissen; im Satz „stan na {datum}“ |
| Stichprobe | próba (losowa) | (random) sample | Vorschlag 15.11.2026; nicht „próbka“ (Materialprobe) |
| Beispieldaten | dane przykładowe | sample data | Wissen; bis zu den echten Daten auf jeder betroffenen Seite |
| Namensnennung OpenStreetMap | © autorzy OpenStreetMap (ODbL) | © OpenStreetMap contributors | Wortlaut der polnischen Seite openstreetmap.org/copyright/pl und der polnischen OSM-Oberfläche (nachgesehen 14.11.2026); nicht „współtwórcy“. In Downloads und Lizenzdateien bleibt das englische Original, wo es als Originalwortlaut zitiert wird |
| Lizenz | licencja | licence (britisch) | Wissen; EN durchgehend britische Schreibung (en-GB) |
| Download | pliki do pobrania | downloads | Wissen |
| Stadtumbau | rewitalizacja (Gminny Program Rewitalizacji) | regeneration | Bauvorlage (krakow.pl GPR) |

## Bedienung

| Deutsch | Polnisch | Englisch | Herkunft, Anmerkung |
|---|---|---|---|
| Karte | mapa | map | Wissen |
| Legende | legenda | legend | Wissen |
| Ebene | warstwa | layer | Wissen |
| Seite Karte (Verweis aus dem Text) | strona „Mapa” | the “Map” page | Vorschlag 15.11.2026, Name wie in der Navigation; nicht „wolna mapa“ |
| Luftbild | ortofotomapa | aerial image | Wissen |
| Thema | temat | topic | Wissen |
| auswählen | wybierz | select | Wissen |
| Vergleich | porównanie | comparison | Wissen |
| Steckbrief | profil (dzielnicy) | profile | Wissen; entspricht dem Seitennamen „Dzielnica w liczbach“ |
| Startseite | strona główna | home | Wissen; so in `kern.zur_startseite` |
| Impressum | nota prawna | legal notice | Wissen; Linktext und Titel der polnischen Fassung `/pl/nota-prawna/` |
| Datenschutz | ochrona danych osobowych | privacy policy | Wissen; die Seite selbst heißt „Polityka prywatności“ (`/pl/polityka-prywatnosci/`, so auch der Linktext) |

## Zur Prüfung zuerst

| Begriff | Frage an die Prüfenden |
|---|---|
| Beleg → potwierdzenie / zapis weryfikacji | Welcher Begriff ist in polnischen Methodenberichten für den Nachweis je Zahl üblich? |
| Taktklasse → klasa częstotliwości kursowania | Gibt es in der polnischen Verkehrsplanung einen festen Begriff (z. B. in einem „plan transportowy“)? |
| Haltestelle Klasse I oder II → przystanek klasy I lub II (co najmniej dwa odjazdy na godzinę) | Ist die neutrale Benennung verständlich? Ab wie vielen Abfahrten je Stunde spricht die Krakauer Verkehrsplanung von „częste kursowanie“ (hier bewusst nicht verwendet)? |
| Gruppe der dzielnice → delegatura (dawna dzielnica) | Ist „delegatura“ für Leser außerhalb der Verwaltung verständlich, oder ist „dawna dzielnica (1973–1990)“ besser? Gibt es eine übliche Bezeichnung in Lehre und Planung? |
| Plattenbau-Kandidat → kandydat na blok z wielkiej płyty | Ist „kandydaci na bloki“ für Gebäude üblich, oder besser „budynki typowane jako bloki“? |
| Gitterzelle → oczko siatki / komórka siatki | Welche Form verwendet GUS in Veröffentlichungen zum Gitter, welche die Hochschullehre? |
| Versiegelung → uszczelnienie gruntu | Ist in der Krakauer Lehre „uszczelnienie gruntu“ üblich oder „zasklepianie gleby“ (polnische Fassung der EU-Leitlinien zu soil sealing)? |
| unscharf → niepewne | Passt „niepewne“ für Werte mit zu kleiner Grundgesamtheit, oder ist „niewiarygodne statystycznie“ üblicher? |
| rejon statystyczny → statistical area | Englische Entsprechung der GUS-Gliederung in GUS-Veröffentlichungen? |
