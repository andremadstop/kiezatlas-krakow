# Gegenlesen der polnischen Texte durch drei Sprachmodelle

Stand 15.11.2026, Zweig `Arbeitszweig p4b-polnisch` (von `Arbeitszweig p4b-integration` `e6e3358`). Drei Sprachmodelle haben die
polnischen Texte unabhängig voneinander gegengelesen: Gemini (G, 52 Vorschläge), Claude Sonnet (S, 57) und Codex (C,
134), zusammen 243. Auftrag und Korpus: alle Kurztexte `texte/pl/*.js`, die Langtexte `texte/pl/bloecke/quelle/*.html`,
`daten/pobierz/CZYTAJ.md`, `docs/uruchomienie.md`, die polnischen Filmuntertitel und der polnische Teil des
Mailentwurfs an Prof. Racoń-Leja. Vorgabe an die Leser: Sinn, Zahlen, Schlüssel, Platzhalter, HTML, Adressen und
Dateinamen nicht ändern, nur was wirklich stört.

Das ersetzt kein muttersprachliches Lektorat. Der Hinweis darauf bleibt auf der Seite Metodologia und in den Filmen
stehen; das Glossar behält für alle Einträge den Status „Vorschlag“. Dieses Dokument schlägt keine neue
Entscheidungsnummer vor; die Begriffe stehen in `docs/glossar-pl.md` (KR60 gilt weiter).

## Regeln des Abgleichs

- Vorschläge, die dieselbe Textstelle betreffen, sind zu einer Stelle zusammengefasst (Spalte „Leser“: Nummer = Zeile
  in der jeweiligen jsonl-Datei, ab 0). Gleiche Sache an mehreren Orten steht einmal, die Edits nennen alle Orte.
- Von zwei oder drei Lesern angestrichen: übernommen, außer der Vorschlag ändert Sinn, Zahl, Platzhalter, Schlüssel,
  HTML oder Adresse oder widerspricht Glossar und KR60. Bei verschiedenen Fassungen ist die bessere gewählt; der Grund
  steht in der Zeile.
- Von einem Leser: übernommen nur bei klarem Fehler (Grammatik, Rektion, Kongruenz, amtlicher Name, Zeichensetzung,
  eindeutige Lehnübersetzung) oder wenn der Vorschlag das Glossar durchsetzt; reine Stilfragen verworfen.
- Einheitlichkeit: jeder übernommene Begriff ist in allen polnischen Quellen gesucht und überall gleich gesetzt; neue
  oder vereinheitlichte Begriffe stehen im Glossar (Einträge vom 15.11.2026).
- Nicht geändert: Schlüssel, die nur die Gegenprobe Potsdam braucht (Kopf von `texte/pl/planer.js`); sie erscheinen
  nie auf Krakauer Seiten.

## Was sich daraus ergab

- **Versorgung im Planer:** „zaopatrzenie“ (Waren, Medien) heißt jetzt überall „dostępność usług“, die Gruppe der
  Ärzte und Apotheken „Usługi i zdrowie“ (12 Schlüssel; Glossar).
- **amtliche Namen:** „Rejestr Szkół i Placówek Oświatowych (RSPO)“ an allen vier Stellen; „do miasta Krakowa“.
- **Glossar durchgesetzt:** „niepewne“ statt „nieostre“, „wartość orientacyjna“ statt „orientacja“, „próba“ statt
  „próbka“, „zapis weryfikacji“, „wykaz ZBK“, „zabudowa i tereny komunikacyjne“, „znacznik `heritage`“ statt
  „znacznik dziedzictwa“, „strona „Mapa”“ statt „wolna mapa“.
- **Rechtschreibung 2026:** „nie“ mit Adjektivpartizip zusammen (nieuwzględniony, nieoceniona, niewliczony).
- **Sachfehler nebenbei (S49):** `dane.html` behauptete in allen drei Sprachen, das Denkmalregister habe noch keine
  eigene Ebene; CZYTAJ und README führen `rejestr_zabytkow`. In pl, en und de berichtigt.
- **verworfen mit Sinnbezug:** G24/S52 (gemeint sind Fallzahlen, nicht Transaktionen), G2 („środek ciężkości“ für den
  Zellmittelpunkt), G46 (gegen KR60), G43 und G51 (Sinn), G26/G29 (falsche Form bei {n} = 1).

## Filme und Mail

- **Filme:** Kein übernommener Vorschlag ändert einen Untertitel. Die Untertitel-Vorschläge (G47, G48, S44, C78, C81)
  und die zugehörigen Seitentexte (G0, C77, C79, C80) sind als Paar verworfen, damit Seite und Film gleich bleiben.
  Die Filme sind deshalb nicht neu aufgenommen. Offen: die Filme zeigen Seiten vom Stand `e366af1`; Seitentext, der
  sich jetzt geändert hat und im Bild zu sehen ist (z. B. „rok przejściowy … (nieuwzględniony)“ auf `powietrze`),
  steht dort noch in der alten Form.
- **Mail** (`UG-Souverain/Wissen/produkt/kiezatlas/mail-racon-leja-entwurf-20261115.md`, Kopie vorher unter
  `~/.cache/kz_tmp/polnisch/mail-vorher.md`): zwei Stellen geändert (S48/C130, S47/C131), vier verworfen.

## Alle Stellen

| Nr | Leser | Datei · Stelle | alt | neu | Entscheidung | Grund |
|---|---|---|---|---|---|---|
| 1 | G30 S4 C0 | `planer.js` · planer.e.leg_unvollstaendig | rejestru szkół i przedszkoli (RSPO) | Rejestru Szkół i Placówek Oświatowych (RSPO) | übernommen | amtlicher Name des Registers (KSDO); drei Leser |
| 2 | C1 | `planer.js` · planer.e.grenze.bdot | rejestru szkół i przedszkoli (RSPO) | Rejestru Szkół i Placówek Oświatowych (RSPO) | übernommen | amtlicher Name; Einheitlichkeit mit leg_unvollstaendig |
| 3 | G39 S5 C2 | `quelle/planer_metoda.html` · p-placowki | Rejestr szkół RSPO | Rejestr Szkół i Placówek Oświatowych (RSPO) | übernommen | amtlicher Name; drei Leser |
| 4 | – | `quelle/metoda.html` · m-ograniczenia (Szkoły) | rejestru RSPO | Rejestru Szkół i Placówek Oświatowych (RSPO) | übernommen | nicht angestrichen; Einheitlichkeit mit den drei RSPO-Stellen |
| 5 | G23 | `mieszkania.js` · mieszkania.begriff_rcn | Rejestr cen nieruchomości | Rejestr Cen Nieruchomości | verworfen | widerspricht dem Glossar (Eigenname wie im Prawo geodezyjne i kartograficzne, kleingeschrieben) |
| 6 | G46 | `erzaehlung.js` · erzaehlung.dz_bebauung (auch Film 1) | powierzchni zabudowy budynkami | powierzchni zabudowanej | verworfen | widerspricht KR60 (udział powierzchni zabudowy (budynkami)) |
| 7 | G2 | `quelle/metoda.html` · m-ograniczenia (Ludność) | według środka | według środka ciężkości | verworfen | Sinn: gemeint ist der Mittelpunkt der Gitterzelle, nicht der Schwerpunkt; metoda.html grenzt „środek ciężkości“ ausdrücklich ab |
| 8 | C71 C73 | `powietrze.js` · powietrze.tab.odleglosc, powietrze.g.okolica_brak | od środka stacji miejskich | od punktu o średnich współrzędnych stacji miejskich | verworfen | „środek“ ist in powietrze.g.okolica als Mittel der Koordinaten erklärt; kein klarer Fehler, ein Leser |
| 9 | C72 | `powietrze.js` · powietrze.g.okolica | od środka stacji miejskich (średniej ich współrzędnych) | od punktu wyznaczonego przez średnie współrzędne stacji miejskich | verworfen | wie C71; die Klammer erklärt den Begriff schon |
| 10 | G20 | `kern.js` · kern.hq_ersatz | katastrze | katastrze/ewidencji | verworfen | kein Fehler: „kataster nieruchomości“ ist der gesetzliche Name der ewidencja gruntów i budynków; Schrägstrich-Form schlechter |
| 11 | S13 C28 | `karte.js` · karte.grau_personen | wartość zbyt nieostra | wartość zbyt niepewna | übernommen | Glossar: unscharf = niepewne; zwei Leser |
| 12 | S14 C29 | `karte.js` · karte.grau_wohnungen | wartość zbyt nieostra | wartość zbyt niepewna | übernommen | Glossar; zwei Leser |
| 13 | S16 C30 | `karte.js` · karte.grafik.unscharf_personen | nieostre, poniżej 10 osób | niepewne, poniżej 10 osób | übernommen | Glossar; zwei Leser |
| 14 | C31 | `karte.js` · karte.grafik.unscharf_wohnungen | nieostre, poniżej 10 mieszkań | niepewne, poniżej 10 mieszkań | übernommen | Glossar; Einheitlichkeit |
| 15 | S15 C27 | `karte.js` · karte.pop_geheim | Małe wartości są nieostre z powodu tajemnicy statystycznej | Małe wartości są zniekształcone wskutek zastosowania ochrony tajemnicy statystycznej | übernommen | zwei Leser; Variante C, weil die Geheimhaltung die Werte verändert (darum Anteile über 100 %), nicht nur unsicher macht |
| 16 | C98 | `quelle/metoda.html` · m-podzial | rozpiętość obu reguł pokazuje nieostrość na granicach | różnica między wynikami obu metod pokazuje niepewność przypisania na granicach | übernommen | „rozpiętość reguł“ ist schief (verglichen werden Ergebnisse); „nieostrość“ nach Glossar „niepewność“; gleich mit C115 |
| 17 | C115 | `skripte/export_pola_krakow.py` · pola gitter_spanne_proz | różnica między regułą powierzchni a regułą środka (miara nieostrości …) | różnica między wynikami przypisania według powierzchni i według środka (miara niepewności …) | übernommen | Prozent ist der Unterschied der Ergebnisse, nicht der Regeln; „nieostrości“ nach Glossar mitgezogen |
| 18 | G18 S12 C59 | `karte.js` · karte.kind_auch | Ma też udziałowo najwięcej | Ma też największy udział | übernommen | „udziałowo“ ist kein übliches Wort; drei Leser, Variante G/S (zwei gleich) |
| 19 | G19 S11 C60 | `karte.js` · karte.kind_vorn | Udziałowo prowadzi dzielnica | Pod względem udziału prowadzi dzielnica | übernommen | drei Leser; Variante G/S (zwei gleich), C stellt den Satz ganz um |
| 20 | G16 S0 C62 | `karte.js` · karte.gz_cap (Satz 2) | z {stichproben} punktów próbnych; tabelę PostGIS liczy dokładnie | na podstawie {stichproben} punktów próbnych; wartości w tabeli są obliczane dokładnie w PostGIS | übernommen | drei Leser: „tabelę … liczy“ ohne klares Subjekt; Variante C behält den Bezug auf die Tabelle, G lässt ihn fallen, S bleibt ohne Subjekt |
| 21 | C61 | `karte.js` · karte.gz_cap (Satz 1) | której powierzchnia dotyka dwóch dzielnic | która leży częściowo w każdej z dwóch dzielnic | verworfen | ein Leser; verständlich, Stilfrage |
| 22 | G17 C63 | `karte.js` · karte.gz_mitte | liczą się tam, żaden w dzielnicy {b} | są przypisani do tej dzielnicy, a żaden do dzielnicy {b} | übernommen | zwei Leser („liczą się“ = zählen, Lehnbedeutung); Variante C, weil G den zweiten Satzteil unverändert lässt |
| 23 | S17 | `karte.js` · karte.gz_flaeche | liczy się wtedy dla jednej, a {xb} dla drugiej | … dla jednej dzielnicy, a … | verworfen | ein Leser; elliptisch, aber verständlich |
| 24 | S18 C64 | `karte.js` · karte.grenz_lead | czyli osoby: {personen} | czyli liczba osób: {personen} | übernommen | zwei Leser; Variante C (Zahl, nicht Personen) |
| 25 | S9 C26 | `karte.js` · karte.stufen_fuenftel | Przedziały: piąte części wszystkich komórek. | Przedziały kwintylowe: po jednej piątej wszystkich komórek. | übernommen | zwei Leser; Variante C nennt den Fachbegriff und sagt zugleich, was er heißt |
| 26 | C3 | `karte.js` · karte.vert_anteile | Udziały w ogółem. | Udziały w ogólnej liczbie. | übernommen | Grammatik: „ogółem“ ist Adverb, nach „w“ unmöglich |
| 27 | G15 S56 | `karte.js` · karte.davon_vor1949 | w tym sprzed 1949 | w tym sprzed 1949 r. | übernommen | zwei Leser; Jahreszahl mit „r.“ |
| 28 | S10 | `karte.js` · karte.grafik.format_halb | Pół strony poziomo | Połowa strony poziomo | verworfen | „pół strony“ ist korrekt |
| 29 | S42 C133 | `karte.js` · karte.grafik.png_laeuft | Trwa tworzenie PNG … | Trwa tworzenie PNG… | übernommen | zwei Leser; Auslassungspunkte für einen laufenden Vorgang ohne Leerzeichen |
| 30 | S41 C132 | `erzaehlung.js` · erzaehlung.laedt | Wczytywanie danych … | Wczytywanie danych… | übernommen | zwei Leser; wie oben |
| 31 | S43 | `quelle/kamienice_dane.html` · denkmale_bdot.js (auch denkmale.namensbezug) | „Kamienica …” | „Kamienica…” | verworfen | Auslassungspunkte stehen hier für ein ausgelassenes Wort (Kamienica + Name), dann mit Leerzeichen |
| 32 | C4 | `erzaehlung.js` · erzaehlung.sb_geschosse | Mediana kondygnacji | Mediana liczby kondygnacji | übernommen | Median der Geschosszahl, nicht der Geschosse |
| 33 | C5 | `erzaehlung.js` · erzaehlung.a_gebaeude | Mediana kondygnacji budynku mieszkalnego | Mediana liczby kondygnacji budynków mieszkalnych | übernommen | wie C4; Median über alle Wohngebäude |
| 34 | G3 | `erzaehlung.js` · erzaehlung.sb_rang | miejsce {r} z {n} | miejsce {r}. na {n} | verworfen | „miejsce 3 z 18“ ist üblich und korrekt |
| 35 | G1 | `denkmale.js` · denkmale.sicht.ansicht | w {ja} z {ent} | w {ja} na {ent} | verworfen | „w 33 z 40 przypadków“ ist korrekt |
| 36 | G4 | `erzaehlung.js` · erzaehlung.sb_nsp_fehlt | dla pojedynczej dzielnicy | dla poszczególnych dzielnic | verworfen | kein Fehler |
| 37 | G5 S53 | `erzaehlung.js` · erzaehlung.a_takt | z których środka do przystanku … jest najwyżej {m} pieszo | od których środka do przystanku … jest pieszo najwyżej {m} | übernommen | zwei Leser; Variante S: „odległość od środka“, „pieszo“ vor die Zahl; G „ze środka których“ ist schlechter |
| 38 | G6 | `erzaehlung.js` · erzaehlung.zbk_zastrzezenie | warunek ponownego wykorzystania | warunek ponownego wykorzystywania | übernommen, angepasst | gesetzlicher Begriff „ponowne wykorzystywanie“ (ustawa o otwartych danych); so schon in sanierung.quellen_wortlaut; Singular bleibt (ein Vorbehalt) |
| 39 | G7 C33 | `erzaehlung.js` · erzaehlung.leg_von_bis | {von} do poniżej {bis} | od {von} do poniżej {bis} | übernommen | zwei Leser; „od … do“ |
| 40 | C32 | `erzaehlung.js` · erzaehlung.leg_grau_gitter | szare: bez udziału, | szare: bez podanej wartości udziału, | übernommen | „bez udziału“ heißt idiomatisch „ohne Beteiligung“ bzw. liest sich als Anteil 0 |
| 41 | G8 | `erzaehlung.js` · erzaehlung.dz_versiegelung | udział zabudowy i komunikacji w powierzchni | udział zabudowy i terenów komunikacyjnych w powierzchni | übernommen, angepasst | Einheitlichkeit: „tereny komunikacyjne“ wie klimat.abgeleitet und metoda; G-Vorschlag „powierzchni zabudowanej“ verworfen (KR60) |
| 42 | S45 | `klimat.js` · klimat.tab.uszczelnienie | Zabudowa i komunikacja | Zabudowa i tereny komunikacyjne | übernommen | Einheitlichkeit; mitgezogen: klimat.mapa.kwadrat, erzaehlung.klima_bebauung_verkehr, metoda.html (m-klimat) |
| 43 | G21 | `klimat.js` · klimat.abgeleitet.bebauung_verkehr | przybliżenie uszczelnienia | przybliżenie uszczelnienia gruntu | übernommen, angepasst | Glossar „uszczelnienie gruntu“, wie in metoda.html; „stopnia“ nicht nötig |
| 44 | G22 | `klimat.js` · klimat.hinweis.versiegelung | powierzchni uszczelnionych | powierzchni uszczelnionej | verworfen | Stilfrage |
| 45 | G9 | `erzaehlung.js` · erzaehlung.vg_15_64 | 15–64 lata | 15–64 lat | verworfen | GUS schreibt „w wieku 15–64 lata“ (Kongruenz mit der letzten Zahl) |
| 46 | G10 | `erzaehlung.js` · erzaehlung.vg_nenner | liczone są od sumy | obliczono w stosunku do sumy | verworfen | Stilfrage |
| 47 | G11 | `erzaehlung.js` · erzaehlung.vg_methode | spisów | spisów powszechnych | verworfen | Stilfrage |
| 48 | G12 | `erzaehlung.js` · erzaehlung.a_takt_ohne | bez wartości dojścia | dla której brak wartości dojścia | verworfen | Stilfrage; hätte zudem alle vier Pluralformen geändert |
| 49 | G0 | `denkmale.js` · denkmale.teilmenge | które źródło wymienia jako zabytek | które źródło wskazuje jako zabytek | verworfen | Stilfrage; zusammen mit G47 (Filmtitel) verworfen, damit Seite und Film gleich bleiben |
| 50 | G47 | `belege/filme/film2 (skripte/filme.mjs)` · Titeltafel Film 2 | wymieniają jako zabytek | klasyfikują jako zabytek | verworfen | wie G0 |
| 51 | C65 | `denkmale.js` · denkmale.teilmenge | budynki danego wieku | budynki z danego okresu | übernommen | „wiek“ ist doppeldeutig (Alter/Jahrhundert) |
| 52 | C66 | `denkmale.js` · denkmale.sicht.punkt | na próbie warstwy | na próbie obiektów z warstwy | verworfen | „próba warstwy“ ist korrekt |
| 53 | G13 S38 | `kamienice.js` · kamienice.om_text | atlas nie umie jeszcze | atlas nie potrafi jeszcze | übernommen | zwei Leser („umieć“ für Fähigkeiten von Personen); Variante S, kürzer |
| 54 | G14 | `kamienice.js` · kamienice.grenze.kamienica | do 10 m od niego | w promieniu do 10 m od niego | verworfen | Stilfrage; „Radius“ um einen Umriss passt nicht |
| 55 | S30 | `kamienice.js` · kamienice.q_osm_klein, q_wd_klein; kamienice_metoda | próbka do kontroli | próba do kontroli | übernommen | Statistik: „próba“ (Stichprobe), „próbka“ ist ein Materialprobe; alle drei Stellen |
| 56 | C19 C20 | `kamienice.js` · kamienice.q_osm_klein, q_wd_klein | jeszcze nie oceniona | jeszcze nieoceniona | übernommen | Zusammenschreibung von „nie“ mit Adjektivpartizip (Regel der Rada Języka Polskiego, gültig seit 1.1.2026) |
| 57 | C21 | `quelle/kamienice_metoda.html` · k-zabytki (OSM) | ale nie oceniona | ale nieoceniona | übernommen | wie C19 |
| 58 | G31 C18 | `powietrze.js` · powietrze.okno.przejscie | nie uwzględniony | nieuwzględniony | übernommen | zwei Leser; wie C19 |
| 59 | C22 | `docs/uruchomienie.md` · Tabelle Zeiten, Schritt pruefen | nie wliczony | niewliczony | übernommen | wie C19 |
| 60 | S20 S21 S19 C23 C24 C25 | `kamienice.js` · kamienice.grenze.register, kamienice.reg_hinweis, kamienice_metoda k-zabytki | na wolnej mapie / wolna mapa | na stronie „Mapa” / strona „Mapa” | übernommen | zwei Leser je Stelle („freie Karte“ ist Lehnübersetzung); Variante S nennt die Seite wie in der Navigation (seiten.karta.nav) und ist von „Mapa na tej stronie“ unterscheidbar; C „mapa atlasu“ wäre mit der Karte auf derselben Seite verwechselbar |
| 61 | S39 | `kamienice.js` · kamienice.grenze.register | bo nie zostały pobrane ręcznie | bo nie zostały jeszcze ręcznie pobrane | verworfen | Stilfrage; „jeszcze“ steht schon im Satz |
| 62 | S51 | `kamienice.js` · kamienice.grenze.delegatur | Zliczenia z BDOT10k | Zestawienia z BDOT10k | verworfen | „zliczenia“ ist korrekt |
| 63 | C68 | `kamienice.js` · kamienice.z_reg_bauzeit | z okresem budowy z daty powstania | z okresem budowy ustalonym na podstawie daty powstania | übernommen | „z … z“ ohne Bezug ist unverständlich |
| 64 | C67 | `kamienice.js` · kamienice.grenze.wd | Liczba podaje więc punkty, a nie zabytki ani budynki. | Podana liczba dotyczy więc punktów, a nie zabytków ani budynków. | übernommen | eine Zahl „gibt“ keine Punkte an; Sinnfehler |
| 65 | S26 C93 | `quelle/dane.html` · d-pobierz | obiektami OSM ze znacznikiem dziedzictwa | obiektami OSM ze znacznikiem <code>heritage</code> | übernommen | zwei Leser; Variante S: der Schlüssel heißt heritage, so schon in kamienice_metoda und README; C „oznaczenie zabytku“ meint OSM und Register zusammen |
| 66 | S27 C94 | `quelle/metoda.html` · m-ograniczenia (OSM), beide Varianten | ze znacznikiem dziedzictwa | ze znacznikiem <code>heritage</code> | übernommen | wie oben |
| 67 | C92 | `quelle/kamienice_metoda.html` · k-kamienica | ze znacznikiem dziedzictwa | ze znacznikiem <code>heritage</code> | übernommen, angepasst | ein Leser, aber Einheitlichkeit mit S26/S27 |
| 68 | C95 | `quelle/kamienice_metoda.html` · k-kamienica | liczy się osobno jako związek przez nazwę | jest liczony osobno ze względu na nazwę | übernommen | „związek przez nazwę“ ist Lehnübersetzung („Bezug über den Namen“) |
| 69 | C96 | `quelle/kamienice_metoda.html` · k-zabytki | jeden punkt we współrzędnych pierwszego obiektu | jeden punkt o współrzędnych pierwszego obiektu | übernommen | Präposition |
| 70 | S7 C97 | `quelle/kamienice_metoda.html` · k-zabytki | Zostaje punktów w mieście: | Liczba pozostałych punktów w mieście: | übernommen | zwei Leser; Variante C passt zur Zahl nach dem Doppelpunkt |
| 71 | G36 | `quelle/kamienice_metoda.html` · k-budynki | z [[…]] rekordów | spośród [[…]] rekordów | verworfen | Stilfrage |
| 72 | C6 C7 | `quelle/kamienice_metoda.html` · k-budynki; pola geschossflaeche_naeherung_* | obrys × kondygnacje | powierzchnia obrysu × liczba kondygnacji | übernommen | multipliziert werden Fläche und Zahl; alle Stellen |
| 73 | C8 C9 | `quelle/kamienice_metoda.html` · k-typologia; pola blok | obrys co najmniej … m² | powierzchnia obrysu co najmniej … m² | übernommen | eine Fläche in m², kein Umriss |
| 74 | S29 | `quelle/kamienice_metoda.html` · k-zbk | z udziałem prywatnym | z udziałem osób prywatnych | übernommen | Einheitlichkeit mit sanierung.grenze.privat |
| 75 | C91 | `quelle/kamienice_dane.html` · gebaeude_kennzahlen.js | i pochodzeniem wysokości | oraz informacje o źródłach danych o wysokości | übernommen | Instrumental ohne regierendes Wort |
| 76 | C99 | `quelle/metoda.html` · m-podzial (delegatury) | sprawdzono na powierzchni | sprawdzono na podstawie udziałów powierzchni | übernommen | „an der Fläche geprüft“, Lehnübersetzung ohne Sinn |
| 77 | C100 | `quelle/metoda.html` · m-podzial | nieznacznie nie osiągają progu | są nieznacznie poniżej progu | verworfen | korrekt |
| 78 | C101 | `quelle/metoda.html` · m-powietrze | cytat uchwały antysmogowej | cytat z uchwały antysmogowej | übernommen | Rektion: cytat z |
| 79 | C74 C75 C76 | `powietrze.js` · powietrze.g.miasto, g.okolica_brak; metoda m-powietrze | do miasta Kraków | do miasta Krakowa | übernommen | Apposition mit „miasto“ wird gebeugt (PWN); amtliche Namen wie „Gmina Miejska Kraków“ bleiben |
| 80 | S8 C102 | `quelle/metoda.html` · m-ograniczenia (Typologia) | potwierdza blok mieszkalny u | potwierdza blok mieszkalny w | übernommen | zwei Leser; Variante S (nur die Präposition); C formt den Satz um |
| 81 | S36 | `quelle/metoda.html` · m-niesprawdzone | granicy ochrony danych | progu ochrony danych | übernommen | Einheitlichkeit mit mieszkania.js („próg“); „granica“ ist doppeldeutig |
| 82 | G38 | `quelle/metoda.html` · m-klimat | ogródki działkowe tak | natomiast ogródki działkowe tak | verworfen | Stilfrage |
| 83 | S49 | `quelle/dane.html` · d-pobierz (auch en, de) | Powietrze, ceny mieszkań i rejestr zabytków nie mają jeszcze własnej warstwy | Powietrze i ceny mieszkań nie mają jeszcze własnej warstwy | berichtigt (Sachfehler) | Sachfehler, keine Sprachfrage: CZYTAJ.md und README führen die Ebene rejestr_zabytkow; in en und de gleich berichtigt |
| 84 | S40 | `quelle/dane.html` · d-licencje | Kto je zmienia i udostępnia, udostępnia na tej samej licencji. | … robi to … | verworfen | bewusste Wiederholung (Lizenzbedingung) |
| 85 | G27 S25 C34 | `planer.js` · planer.frage.raum | Jak zaopatrzona jest jednostka ({einheit})? | Jaka jest dostępność usług w jednostce ({einheit})? | übernommen | drei Leser („zaopatrzenie“ = Waren, Medien); Variante C, weil sie den Begriff liefert, der überall gilt (Glossar neu: Versorgung = dostępność usług) |
| 86 | C35 | `planer.js` · planer.versorgung | Zaopatrzenie | Dostępność usług | übernommen | Einheitlichkeit mit frage.raum |
| 87 | C42 | `planer.js` · planer.vs_aria | Zaopatrzenie: {name} | Dostępność usług: {name} | übernommen | Einheitlichkeit |
| 88 | C10 | `planer.js` · planer.datei_ebene | Plik zaopatrzenia liczy na {ebene}. | Plik zawiera dane o dostępności usług na {ebene}. | übernommen | eine Datei „rechnet“ nicht; Einheitlichkeit ({ebene} = „poziomie dzielnic“) |
| 89 | C36 G25 | `planer.js` · planer.druck | z tabelą zaopatrzenia. Karta liczy odległość | z tabelą dostępności usług. Karta podaje odległość | übernommen | Einheitlichkeit (C); „Karta liczy“ Lehnübersetzung „rechnet“ (G); verschiedene Teile desselben Satzes |
| 90 | C37 | `planer.js` · planer.fehler_datei | pliku zaopatrzenia | pliku z danymi o dostępności usług | übernommen | Einheitlichkeit |
| 91 | C38 | `planer.js` · planer.keine_werte | wartości zaopatrzenia | wskaźników dostępności usług | übernommen | Einheitlichkeit |
| 92 | C39 | `planer.js` · planer.nur_lage | bez oceny zaopatrzenia | bez oceny dostępności usług | übernommen | Einheitlichkeit |
| 93 | C40 | `planer.js` · planer.pop_keine_aussage | bez oceny zaopatrzenia | bez oceny dostępności usług | übernommen | Einheitlichkeit |
| 94 | C41 | `planer.js` · planer.vg_hinweise | tabeli zaopatrzenia | tabeli dostępności usług | übernommen | Einheitlichkeit |
| 95 | C43 | `planer.js` · planer.werte_je | Wartości zaopatrzenia są dostępne na poziomie | Wskaźniki dostępności usług są podane na poziomie | übernommen, angepasst | Einheitlichkeit; „są dostępne“ zu „są podane“, sonst „dostępności … dostępne“ |
| 96 | S24 C44 | `planer.js` · planer.gruppe.versorgung | Zaopatrzenie i zdrowie | Usługi i zdrowie | übernommen | zwei Leser; Variante S, denn in Kraków enthält die Gruppe Ärzte und Apotheken, „Handel“ (C) träfe nicht |
| 97 | C47 C48 C49 | `planer.js` · planer.gruppe.versorgung_hinweis | bez oceny zaopatrzenia; lekarzy planuje …; nie podaje pojemności | … | verworfen | Schlüssel nur für die Gegenprobe Potsdam (Kopf von planer.js, d3_falschsaetze „ausser“), nie auf Krakauer Seiten |
| 98 | C45 | `planer.js` · planer.gruppe.gemeinbedarf_hinweis | lokalizacja bez pojemności | lokalizacja bez danych o liczbie miejsc | verworfen | nur Gegenprobe Potsdam |
| 99 | C55 | `planer.js` · planer.gruppe.bildung_hinweis | uwzględnia się je przy odległościach | … przy obliczaniu odległości | verworfen | nur Gegenprobe Potsdam |
| 100 | C50 | `planer.js` · planer.art.sek1_name | Szkoła z poziomem średnim I stopnia | Szkoła prowadząca kształcenie średnie I stopnia | verworfen | Art sek1 gibt es nur in Potsdam (daten/einrichtungen*.js für Kraków ohne sek1) |
| 101 | C46 | `planer.js` · planer.pop_nur_lage | Tylko lokalizacja, bez pojemności | … bez danych o liczbie miejsc | verworfen | gilt für Ärzte und Apotheken, „liczba miejsc“ passt dort nicht; ein Leser |
| 102 | G28 S3 C11 | `planer.js` · planer.kz.plaetze_bedarf | Miejsca na miejsce zapotrzebowania | Liczba miejsc przypadających na jedno potrzebne miejsce | übernommen | drei Leser; Variante C: genau das Verhältnis; G behält die Lehnübersetzung „miejsce zapotrzebowania“, S verwischt das Verhältnis |
| 103 | G26 S1 | `planer.js` · planer.fehlen | Rachunkowo brakuje miejsc | Według obliczeń brakuje miejsc | übernommen | zwei Leser; Variante S; G („brakuje {n} miejsc“) verworfen: falsche Form bei {n} = 1 (miejsca) |
| 104 | G29 S2 C52 | `planer.js` · planer.mehr | Rachunkowo miejsc jest więcej niż zapotrzebowanie: {n}. | Według obliczeń miejsc jest więcej niż wynosi zapotrzebowanie: {n}. | übernommen | drei Leser; Variante S, gleich gebaut wie planer.fehlen; G mit derselben Liczebnik-Falle wie G26 |
| 105 | S22 | `planer.js` · planer.richtwert | Wartość normatywna: | Wartość odniesienia: | übernommen | Einheitlichkeit mit planer.e.richtwert und seiten.planer |
| 106 | S23 | `planer.js` · planer.status.orientierung | bez wartości normatywnej | bez wartości odniesienia | übernommen | wie S22 |
| 107 | C53 | `planer.js` · planer.strittig | nie liczy się do odległości | nie jest uwzględniana przy obliczaniu odległości | übernommen | Lehnübersetzung „zählt nicht zur Entfernung“ |
| 108 | C54 | `planer.js` · planer.pop_aussen | uwzględniane przy odległościach | uwzględniane przy obliczaniu odległości | übernommen | Einheitlichkeit mit C53/C106 |
| 109 | C106 | `quelle/planer_metoda.html` · p-placowki (Lekarze) | liczą się do odległości | są uwzględniane przy obliczaniu odległości | übernommen | wie C53 |
| 110 | C58 | `planer.js` · planer.e.grenze.zelle | Wszyscy mieszkańcy komórki liczą się tak | Wszystkich mieszkańców komórki uwzględnia się tak | übernommen | wie C53 („liczą się“ = haben Gewicht) |
| 111 | C51 | `planer.js` · planer.vg_ohne_zn | mediana po komórkach | mediana wartości dla komórek | übernommen | Lehnübersetzung „Median über Zellen“ |
| 112 | C56 | `planer.js` · planer.e.frage.luft_text | To samo pytanie o przystanek, mierzone w linii prostej. | …, ale odległość mierzona w linii prostej. | übernommen | gemessen wird die Entfernung, nicht die Frage |
| 113 | C57 | `planer.js` · planer.e.frage.luft_text | droga piesza jest zawsze dłuższa lub równa | … co najmniej tak długa jak odległość w linii prostej | übernommen | Vergleich ohne zweites Glied |
| 114 | S50 | `planer.js` · planer.e.frage.takt_text | Droga piesza z każdej komórki | Dojście piesze z każdej komórki | übernommen | Glossar „dojście piesze“ im Fließtext, wie planer.e.frage.takt; „droga piesza“ bleibt als Name der Messart (neben „linia prosta“) |
| 115 | C12 | `planer.js` · planer.e.leg_ohne_punkte | Tego celu nie pokazujemy jako punkty | Obiektów tego rodzaju nie pokazujemy jako punktów | übernommen | Kongruenz Einzahl/Mehrzahl |
| 116 | C13 | `planer.js` · planer.e.st_kopf | Mieszkańcy: {ew} (zaokrąglone do {rundung}). | Liczba mieszkańców: {ew} (zaokrąglona do {rundung}). | übernommen | Kongruenz: gerundet ist die Zahl |
| 117 | C14 | `planer.js` · planer.e.zn.anteil | (zaokrąglone do {rundung}) | (liczby zaokrąglone do {rundung}) | übernommen | Kongruenz mit „mieszkańców“ |
| 118 | C103 | `quelle/planer_metoda.html` · p-jednostki | rozłożeni nierówno | rozmieszczeni nierównomiernie | verworfen | korrekt, Stilfrage |
| 119 | C104 | `quelle/planer_metoda.html` · p-placowki | kompleksy z własną powierzchnią (tu punkt wewnątrz powierzchni) | kompleksy zajmujące własny teren (tu reprezentowane przez punkt wewnątrz tego terenu) | übernommen | Einheitlichkeit mit planer.e.grenze.bdot („obiekty z własnym terenem“) |
| 120 | C105 | `quelle/planer_metoda.html` · p-placowki | nie podaje miejsc ani liczby uczniów | nie podaje liczby miejsc ani liczby uczniów | übernommen | Parallelität, gemeint ist die Zahl |
| 121 | C107 | `quelle/planer_metoda.html` · p-szkoly | to <em>orientacja</em> | to <em>wartość orientacyjna</em> | übernommen | Glossar „wartość orientacyjna“ |
| 122 | C108 | `quelle/planer_metoda.html` · p-zielen | odległość graniczna to standard skryptu obliczeń | odległość graniczna jest ustalona w skrypcie obliczeniowym | übernommen | „standard“ ist im Glossar dem amtlichen Richtwert vorbehalten (standard urzędowy) |
| 123 | C109 | `quelle/planer_metoda.html` · p-granice | Komórka 1 km z mieszkańcami w środku zawyża … | Umieszczenie wszystkich mieszkańców w środku komórki 1 km zawyża … | verworfen | verständlich, Stilfrage |
| 124 | C110 | `quelle/planer_metoda.html` · p-granice | Sieć dróg pieszych i lekarze z OpenStreetMap są tak kompletne | Dane o sieci dróg pieszych i lekarzach … są tak kompletne | übernommen | Kongruenz: gemischtes Subjekt mit Personen verlangt „kompletni“; mit „Dane“ korrekt |
| 125 | G32 C70 | `powietrze.js` · powietrze.bez_przyczyny | tego nie sprawdzono ani nie odliczono | tego nie sprawdzono ani nie uwzględniono w obliczeniach | übernommen | zwei Leser („odliczyć“ = abziehen, Lehnübersetzung von „herausrechnen“); Variante G, kürzer bei gleichem Sinn |
| 126 | C69 | `powietrze.js` · powietrze.brak_pelnego_okna | jest ważna wartość | dostępna jest wartość spełniająca kryteria jakości | verworfen | „ważna wartość“ ist verständlich; Ersatz zu lang |
| 127 | C77 C78 | `powietrze.js` · powietrze.h.przebieg; Film 3 | Wartości roczne stacji pomiarowych | Wartości roczne ze stacji pomiarowych | verworfen | Genitiv ist korrekt; Seite und Film bleiben gleich |
| 128 | C79 C80 C81 | `powietrze.js` · powietrze.okno.przed/po; Film 3 | średnia {od}–{do} | średnia z lat {od}–{do} | verworfen | knappe Beschriftung ist korrekt; Seite und Film bleiben gleich |
| 129 | G48 | `belege/filme/film3 (skripte/filme.mjs)` · Untertitel Film 3 | Rok 2019 pominięty. | Rok 2019 został pominięty. | verworfen | elliptischer Untertitel ist korrekt |
| 130 | S44 | `belege/filme/film1 (skripte/filme.mjs)` · Quellentafel Film 1 | ; Rozkład jazdy: ZTP Kraków | ; rozkład jazdy: ZTP Kraków | verworfen | eigene Zeile der Quellentafel im Film; das Semikolon setzt nur die Untertiteldatei zwischen die Zeilen |
| 131 | G24 S52 | `mieszkania.js` · mieszkania.g.od_roku | pojedyncze liczby transakcji | pojedyncze transakcje | verworfen | ändert den Sinn: gemeint sind Fallzahlen (de „einzelne Fallzahlen“, en „single case counts“), nicht einzelne Käufe |
| 132 | S37 | `sanierung.js` · sanierung.lede | Budynki w zarządzie Zarządu Budynków Komunalnych | Budynki zarządzane przez Zarząd … | verworfen | folgt dem amtlichen Titel „Wykaz budynków i obiektów w zarządzie ZBK“ |
| 133 | G37 | `sanierung.js` · sanierung.grenze.typologie | Nie rozpoznaje technologii budowy | Nie uwzględnia technologii budowy | verworfen | ändert den Sinn (erkennen ≠ berücksichtigen) |
| 134 | G35 | `sanierung.js` · sanierung.grenze.privat | Punkty tylko dla budynków | Punkty oznaczają tylko budynki | verworfen | Stilfrage |
| 135 | C82 C83 C84 | `sanierung.js` · sanierung.leg_zbk, punkte_regel, grenze.privat | we własności publicznej | stanowiące własność publiczną | verworfen | „we własności“ ist im Rechtspolnisch üblich („pozostające we własności“) |
| 136 | C85 | `sanierung.js` · sanierung.typ_grenze | Liczba obejmuje tylko kombinację cech | Liczba obejmuje tylko budynki o określonej kombinacji cech | übernommen | gezählt werden Gebäude, nicht Merkmalskombinationen |
| 137 | S55 C86 | `sanierung.js` · sanierung.typ_grenze | ceglane budynki socrealizmu | ceglane budynki socrealistyczne | übernommen | zwei Leser; Variante C (Adjektiv) |
| 138 | G33 C87 | `sanierung.js` · sanierung.z_angebaut_klein | na co najmniej {m} m | na długości co najmniej {m} m | übernommen | zwei Leser; Variante G (ohne neues geschütztes Leerzeichen, wie der Rest der Datei) |
| 139 | C117 | `skripte/export_pola_krakow.py` · pola blok_angebaut | ze wspólną granicą co najmniej 3 m | ze wspólną granicą o długości co najmniej 3 m | übernommen, angepasst | Maßangabe ohne Größe; wie G33, normales Leerzeichen |
| 140 | C88 | `sanierung.js` · sanierung.grenze.liste | Odczyt tabeli z PDF sprawdzono zgodnością sum | Poprawność odczytu tabeli z PDF sprawdzono, porównując sumy | übernommen | „sprawdzono zgodnością“ ist ungrammatisch |
| 141 | C89 C90 | `sanierung.js` · sanierung.z_umriss, z_punkt | ustalony przez | ustalony na podstawie | übernommen | Lehnübersetzung („über den Umriss“) |
| 142 | G34 | `sanierung.js` · sanierung.vk.abweichung_dzielnica | punkt poza dzielnicą z wykazu | punkt leży poza … | verworfen | Stilfrage |
| 143 | C111 | `skripte/16_export_krakow.py` · CZYTAJ siatka_1km | udziały wieku | udziały grup wieku | übernommen | Einheitlichkeit mit metoda.html („Udziały grup wieku“) |
| 144 | C112 | `skripte/16_export_krakow.py` · CZYTAJ siatka_1km | w granicy miasta | w granicach miasta | übernommen | „w granicach“ = innerhalb |
| 145 | S28 | `skripte/16_export_krakow.py` · CZYTAJ Ograniczenia | z tagiem `start_date` | ze znacznikiem `start_date` | übernommen | Einheitlichkeit („znacznik“ auf den Seiten) |
| 146 | C121 | `skripte/16_export_krakow.py` · CZYTAJ Ograniczenia (ludność) | wartości dla dzielnic sumują komórki według ich środka | wartości dla dzielnic powstają przez sumowanie danych z komórek przypisanych według ich środka | übernommen | Werte summieren nicht |
| 147 | C122 | `skripte/16_export_krakow.py` · CZYTAJ Ograniczenia (odległości) | to orientacja, nie wartość urzędowa | to wartości orientacyjne, nie urzędowe | übernommen | Glossar „wartość orientacyjna“ |
| 148 | C113 | `skripte/export_pola_krakow.py` · pola gitter_einwohner | mieszkańcy (suma komórek według ich środka) | mieszkańcy (suma liczby mieszkańców komórek przypisanych według ich środka) | übernommen | summiert werden Einwohnerzahlen, nicht Zellen; gleich mit C121 |
| 149 | C114 | `skripte/export_pola_krakow.py` · pola gitter_abweichung_nsp_proz | różnica mieszkańców z siatki | różnica liczby mieszkańców z siatki | übernommen | Unterschied der Zahl |
| 150 | S6 C116 | `skripte/export_pola_krakow.py` · pola blok (typ_blok, blok) | kandydaci na blok wśród nich (…); łącznie z osiedle | w tym kandydaci na bloki (…); łącznie z kategorią osiedle | übernommen, angepasst | zwei Leser: „łącznie z osiedle“ ohne Kasus; Anfang nach S („w tym“), Ende nach C (Bezug auf die Kategorie osiedle bleibt, S „na osiedlach“ verlöre ihn) |
| 151 | C118 | `skripte/export_pola_krakow.py` · pola anteil_stadt | udział komórki leżący w granicach miasta | część powierzchni komórki znajdująca się w granicach miasta | verworfen | verständlich, Stilfrage |
| 152 | C119 | `skripte/export_pola_krakow.py` · pola przystanki.verkehrsmittel | środki transportu z odjazdami w dniu liczenia | środki transportu kursujące w analizowanym dniu | verworfen | Stilfrage |
| 153 | C120 | `skripte/export_pola_krakow.py` · pola zbk_budynki.fn | połączonego budynku BDOT10k | przypisanego budynku BDOT10k | übernommen | „połączony“ = baulich verbunden; gemeint ist die Zuordnung |
| 154 | C15 | `skripte/export_pola_krakow.py` · pola dostepnosc.ew | mieszkańcy obszaru (siatka Eurostatu, zaokrąglone) | liczba mieszkańców obszaru (siatka Eurostatu, wartość zaokrąglona) | übernommen | Kongruenz |
| 155 | G40 S31 C123 | `docs/uruchomienie.md` · Warnkasten, Überschrift | Bez pytania wydawcy dziś jeszcze nie do uruchomienia w całości | Pełne uruchomienie wymaga jeszcze kontaktu z wydawcą | übernommen | drei Leser; Variante C, kürzester korrekter Satz |
| 156 | G41 | `docs/uruchomienie.md` · Warnkasten | repozytorium Geodaten-Import-Pipeline | adresu repozytorium … | verworfen | Aufzählung nach „adresu“ ist korrekt elliptisch |
| 157 | C124 | `docs/uruchomienie.md` · Warnkasten | Adresu nie ma też repozytorium Kiezatlas Potsdam | Brakuje też adresu repozytorium Kiezatlas Potsdam | verworfen | korrekt, Stilfrage |
| 158 | G42 | `docs/uruchomienie.md` · Warnkasten | trzeba zapytać wydawcę | należy o nie zapytać wydawcę | verworfen | Stilfrage |
| 159 | C17 | `docs/uruchomienie.md` · Einleitung | czego nie zmierzono, jest oznaczone | to, czego nie zmierzono, jest oznaczone | übernommen | Korrelat fehlt |
| 160 | G43 | `docs/uruchomienie.md` · Wymagania | zostaje danymi przykładowymi | zostaje zastąpiony danymi przykładowymi | verworfen | ändert den Sinn (die Datei bleibt Beispieldatei, sie wird nicht ersetzt) |
| 161 | G44 | `docs/uruchomienie.md` · Wymagania, Tabelle Werkzeuge | lista budynków ZBK | wykaz budynków ZBK | übernommen | Einheitlichkeit („wykaz ZBK“ auf allen Seiten); mitgezogen: „lista ZBK“ im Abschnitt Droga C |
| 162 | C125 | `docs/uruchomienie.md` · Skąd wziąć dwa pozostałe repozytoria | To otwarta przeszkoda w przekazaniu | To nierozwiązany problem utrudniający przekazanie | übernommen | Lehnübersetzung („offenes Hindernis“) |
| 163 | G45 | `docs/uruchomienie.md` · Droga A, Hinweis | przerywa (zapisana suma SHA256 BDOT10k) | przerywa działanie (…) | übernommen | „przerywać“ verlangt ein Objekt |
| 164 | C126 | `docs/uruchomienie.md` · Droga A | Aby dokładnie odtworzyć stan z 14.11.2026, służy droga C. | Do dokładnego odtworzenia stanu z 14.11.2026 służy droga C. | übernommen | „aby“ ohne passendes Subjekt |
| 165 | S35 | `docs/uruchomienie.md` · Droga A | w dokumencie dowodowym | w zapisie weryfikacji | übernommen | Glossar Beleg = zapis weryfikacji |
| 166 | S32 S33 | `docs/uruchomienie.md` · Droga B, Tabelle Handdownloads | przerwa | przebieg zostaje przerwany / krok … zostaje przerwany | übernommen | „przerwa“ = Pause, gemeint ist der Abbruch |
| 167 | S34 | `docs/uruchomienie.md` · W skrócie | cały łańcuch | cały potok przetwarzania | verworfen | „łańcuch“ steht im ganzen Dokument für die Kette; Stilfrage |
| 168 | C127 | `docs/uruchomienie.md` · Droga C | siatki Eurostat | siatki Eurostatu | übernommen | Genitiv, wie überall sonst |
| 169 | C128 | `docs/uruchomienie.md` · Droga C | wynik zapytania Wikidanych | wynik zapytania do Wikidanych | übernommen | Rektion |
| 170 | S54 | `docs/uruchomienie.md` · Droga C | Archiwum jest powtarzalne bajt w bajt | Archiwum daje się odtworzyć bajt w bajt | verworfen | „powtarzalny“ ist im Sinn von reproduzierbar üblich |
| 171 | C16 | `docs/uruchomienie.md` · Droga C | Pięć z nich łańcuch potrzebuje | Pięciu z nich łańcuch potrzebuje | übernommen | „potrzebować“ + Genitiv |
| 172 | C129 | `docs/uruchomienie.md` · Oczekiwany koniec po drodze C | każde inne trzeba najpierw usunąć | przyczynę każdego innego zgłoszenia trzeba najpierw usunąć | übernommen | Sinn: zu beheben ist die Ursache, nicht die Meldung |
| 173 | S48 C130 | `MAIL` · Polski, Absatz Ziel | Ma służyć jako otwarty przepis | Ma służyć jako otwarty wzór do powtórzenia | übernommen | zwei Leser („przepis“ = Kochrezept oder Vorschrift); Variante S trifft die Idee des Nachbauens, C „instrukcja“ ist enger |
| 174 | S47 C131 | `MAIL` · Polski, Fragen | przy których Pani doświadczenie bardzo by pomogło | w których wyjaśnieniu Pani doświadczenie bardzo by pomogło | übernommen | zwei Leser („przy których“ falsche Präposition); Variante C behält „bardzo“ |
| 175 | G49 | `MAIL` · Polski | Zostały mi dwa pytania | Pozostały mi dwa pytania | verworfen | Stilfrage |
| 176 | G50 | `MAIL` · Polski | kogo o to zapytać, | do kogo mógłbym się z tym zwrócić, | verworfen | Stilfrage |
| 177 | G51 | `MAIL` · Polski | zauważą, gdzie coś brzmi nienaturalnie, | zauważą, że coś … | verworfen | ändert den Sinn (wo ≠ dass) |
| 178 | S46 | `MAIL` · Vor dem Senden prüfen (deutsch) | bez udziału mojej firmy.“ | bez udziału mojej firmy.” | verworfen | die Anführungszeichen gehören zum deutschen Prüfhinweis, der den polnischen Satz zitiert, nicht zum polnischen Text |

## Zählung

178 Stellen aus 243 Vorschlägen; eine davon (Nr. 4, RSPO in `metoda.html`) hat kein Leser angestrichen, sie folgt
aus der Einheitlichkeit.

| Konsens | Stellen | übernommen | davon angepasst | verworfen | Sachfehler berichtigt |
|---|---|---|---|---|---|
| alle drei Leser | 9 | 9 | 0 | 0 | 0 |
| zwei Leser | 29 | 28 | 1 | 1 | 0 |
| ein Leser | 139 | 81 | 6 | 57 | 1 |
| kein Leser (Einheitlichkeit) | 1 | 1 | 0 | 0 | 0 |
| **gesamt** | **178** | **119** | **7** | **58** | **1** |

Nach Vorschlägen: 176 der 243 Vorschläge gehören zu Stellen, die geändert sind (bei mehreren Fassungen ist eine
gewählt), 67 zu verworfenen Stellen. Je Leser angestrichene Stellen, die ein anderer Leser auch hatte (nach dem
Zusammenfassen, dreifache mitgezählt): G∩S 14, G∩C 15, S∩C 27, alle drei 9. Die Vorabzählung vor dem Abgleich (alle
drei 7, G∩C 14, S∩C 36, G∩S 11) verglich einzelne Vorschläge; hier zählen Textstellen: mehrere Vorschläge zu einer
Stelle (z. B. „wolna mapa“ an drei Orten, „nieostre“, „zaopatrzenie“) zählen einmal, verschiedene Satzteile in einem
Schlüssel (z. B. `karte.gz_cap`) getrennt.
