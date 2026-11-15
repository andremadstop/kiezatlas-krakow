# Filme: Kiezatlas Kraków in drei kurzen Filmen (polnisch)

Erzeugt von `skripte/filme.mjs` (nicht von Hand ändern) auf Commit `e366af1`
(sauberer Arbeitsstand).

**PL** Trzy krótkie filmy bez dźwięku, nagrane z prawdziwych stron atlasu, z napisami po polsku. Tekst nie był
sprawdzony przez rodzimego użytkownika języka.

**DE** Drei kurze Filme ohne Ton, aufgenommen aus den echten Seiten des Atlas, mit eingeblendeten polnischen
Untertiteln und Texttafeln. Tekst nie był sprawdzony przez rodzimego użytkownika języka: Die polnischen Texte hat
keine Muttersprachlerin und kein Muttersprachler geprüft; Begriffe nach `docs/glossar-pl.md` (Status Vorschlag).
Untertitel als WebVTT: Polnisch wie eingeblendet, dazu Englisch und Deutsch mit denselben Zeiten. Eigennamen
bleiben polnisch.

Befehl (aus dem Wurzelordner, braucht den Kachelordner der Grundkarte wie `skripte/entwicklung_server.mjs`,
Playwright mit Chromium und ffmpeg mit libx264 und libvpx-vp9):

```sh
node skripte/filme.mjs --ziel belege/filme [--nur 1,2,3] [--standbilder ORDNER]
```

So entsteht ein Film: headless Chromium öffnet die Seiten über den Entwicklungsserver (nur 127.0.0.1, fremde Abrufe
werden abgefangen), Ansicht 1280 × 720 px, Pixelverhältnis 1, Sprache pl-PL. Bilder kommen aus dem Bildschirm-Streaming
des Browsers (JPEG) und gehen als Folge mit 25 Bildern je Sekunde an ffmpeg: MP4 (H.264, CRF 28, yuv420p,
faststart) und WebM (VP9, CRF 38) aus derselben Bildfolge, ohne Tonspur. Seitenwechsel und Ladezeiten sind
herausgeschnitten. Untertitel und Tafeln sind Einblendungen in der Seite (Barlow, Farben aus `DESIGN.md`, kein
Orange). Zahlen in den Untertiteln kommen beim Lauf aus den Datendateien (`KIEZ_POWIETRZE.okna`,
`KIEZ_MIESZKANIA.regeln.mindestfallzahl`), nicht aus dem Skript.

Wiederholbar, nicht bitgleich: dasselbe Drehbuch, feste Wartezeiten, `Math.random` mit festem Startwert. Ladezeiten
und Bildtakt des Browsers schwanken, darum weichen einzelne Bilder und damit die Prüfsummen zwischen zwei Läufen ab;
die SHA256 unten gelten für genau diese Dateien. Das Skript prüft jeden neu aufgenommenen Film mit ffprobe (Dauer
50 bis 75 s, je Datei höchstens 5,00 MB, 1280 × 720, ein Strom ohne Ton) und meldet Konsolenfehler.

Was die Filme nicht zeigen: keine Personen, keine einzelnen Transaktionen aus dem Rejestr cen nieruchomości, keine
Einzelgebäude aus dem Wykaz ZBK (die Ebene mit den Gebäudepunkten bleibt aus, die Karte wird nicht angeklickt, der
Zeiger steht außerhalb der Karte). Der Vergleich in Film 1 ist die Seite `porownanie.html` („Kraków i Poczdam“),
die die Seite selbst Porównanie nennt; der Rang einer dzielnica unter allen dzielnice steht im Steckbrief davor.
Film 3 zeigt die Luftwerte vor und nach der uchwała antysmogowa ausdrücklich nur als zeitlichen Vergleich, nicht als
Ursache.

Lizenz: CC BY 4.0 wie die Bildschirmfotos unter `belege/`, Namensnennung „Kiezatlas Kraków, CC BY 4.0“. Die Filme
zeigen eigene Seiten mit Daten aus den genannten Quellen (OpenStreetMap: das Bild ist ein „Produced Work“ im Sinn der
ODbL 1.0); die Quellentafel am Ende jedes Films nennt sie mit Namensnennung, die vollständigen Vermerke stehen auf der
Seite `dane.html`.

## Film 1: Atlas w minutę

The atlas in a minute / Der Atlas in einer Minute

| Datei | Format | Größe | SHA256 |
|---|---|---|---|
| `film1-atlas-w-minute.mp4` | h264, 1280 × 720, 69,3 s | 3,58 MB | `172c2943f313ba874d1bacbc49e5dae0e2b035b35713e77d1a163e9b06d238ce` |
| `film1-atlas-w-minute.webm` | vp9, 1280 × 720, 69,3 s | 2,50 MB | `9f2fa1c0f884e5fec056a66bdbd70b2830381a06ff50131d69e54138c4e8ae42` |
| `film1-atlas-w-minute.pl.vtt` | WebVTT | 1,6 kB | `f43b757f1fdff1b24e51f88f1a30f3fdec839956744825226914970a93509fd6` |
| `film1-atlas-w-minute.en.vtt` | WebVTT | 1,5 kB | `999ce423cb1bb9a60223e976a644e61ba0b59781c7e743306ef022472fa0e7c3` |
| `film1-atlas-w-minute.de.vtt` | WebVTT | 1,6 kB | `df261e2e39928cef6900c8720c8b459487a668d9f78cde251143993f11136d58` |

Drehbuch (Zeiten aus `film1-atlas-w-minute.pl.vtt`, Minuten:Sekunden):

| # | Zeit | Seite | Bild | Untertitel (pl) |
|---|---|---|---|---|
| 1 | 00:00–00:04 | `index.html` | Titeltafel | Atlas w minutę. Atlas dzielnic Krakowa z otwartych danych publicznych |
| 2 | 00:04–00:09 | `index.html` | Startseite, Kopf mit den Stadtzahlen | Strona główna: najważniejsze liczby miasta, przy każdej źródło. |
| 3 | 00:09–00:14 | `index.html` | langsam zur ersten Frage scrollen | Pytania prowadzą przez miasto, a mapa pokazuje odpowiedź. |
| 4 | 00:14–00:19 | `index.html` | weiter zur Frage nach der Dichte | Z każdym pytaniem zmieniają się kolory mapy. |
| 5 | 00:19–00:24 | `karta.html` | Karte mit den delegatury | Mapa: wszystkie tematy atlasu na jednej mapie. |
| 6 | 00:24–00:29 | `karta.html` | Gitterebene „Mieszkańcy w komórce siatki“ wählen | Warstwa siatki 1 km: mieszkańcy w komórce siatki. |
| 7 | 00:29–00:33 | `karta.html` | Gitter aus, Farben der dzielnice: Bebauungsanteil | Kolory dzielnic: udział powierzchni zabudowy budynkami. |
| 8 | 00:33–00:38 | `karta.html` | Punkte: Haltestellen nach Taktklasse | Punkty: przystanki według klasy częstotliwości kursowania. |
| 9 | 00:39–00:43 | `dzielnica.html` | Steckbrief, dzielnica XIII Podgórze wählen | Profil dzielnicy: wskaźniki, miejsce wśród dzielnic i źródło. |
| 10 | 00:43–00:48 | `dzielnica.html` | zu den Kennzahlen scrollen | Brak wartości oznacza brak danych, nie zero. |
| 11 | 00:49–00:54 | `porownanie.html` | Vergleich Kraków und Potsdam | Porównanie: Kraków i Poczdam, ta sama siatka i ta sama metoda. |
| 12 | 00:54–00:58 | `porownanie.html` | zur Tabelle scrollen | Porównujemy tylko wskaźniki o tej samej definicji. |
| 13 | 00:58–01:03 | `porownanie.html` | zu „Czego nie porównujemy“ scrollen | Resztę wymieniamy osobno: czego nie porównujemy i dlaczego. |
| 14 | 01:03–01:08 | `porownanie.html` | Quellentafel | Źródła: GUS, Narodowy Spis Powszechny 2021; Eurostat, Census 2021 population grid (CC BY 4.0); BDOT10k, Główny Urząd Geodezji i Kartografii; Rozkład jazdy: ZTP Kraków, GTFS (CC BY 4.0); Granice dzielnic: © autorzy OpenStreetMap (ODbL). Pełne noty o źródłach i licencje: strona „Dane”. |

## Film 2: Kamienice i zabytki

Tenement houses and monuments / Kamienice und Denkmale

| Datei | Format | Größe | SHA256 |
|---|---|---|---|
| `film2-kamienice-i-zabytki.mp4` | h264, 1280 × 720, 65,1 s | 2,97 MB | `c234e897e9c0b4f389e38203fc75a1db267fa4d43382b02ccb2e9d1bf9a9d5db` |
| `film2-kamienice-i-zabytki.webm` | vp9, 1280 × 720, 65,1 s | 2,39 MB | `f0925de0527368fc21a1af3e65753ddd8ffbc2a32f89e3aa8a9d781e9ae78257` |
| `film2-kamienice-i-zabytki.pl.vtt` | WebVTT | 1,6 kB | `2d6a61dccf19bd3f7a5507db37902dddfba3cf4763e9beef16ac94fdd65e6fc5` |
| `film2-kamienice-i-zabytki.en.vtt` | WebVTT | 1,6 kB | `91503d73e39c6b63ca8705142704b0fa64019225f2d348e14f3e42a5764da45a` |
| `film2-kamienice-i-zabytki.de.vtt` | WebVTT | 1,7 kB | `24a2860dde1b3993b78d220c862312127fb2a5f936d27b0859d0694e0f432599` |

Drehbuch (Zeiten aus `film2-kamienice-i-zabytki.pl.vtt`, Minuten:Sekunden):

| # | Zeit | Seite | Bild | Untertitel (pl) |
|---|---|---|---|---|
| 1 | 00:00–00:04 | `kamienice.html` | Titeltafel | Kamienice i zabytki. Co źródła wymieniają jako zabytek i jak to sprawdzono |
| 2 | 00:04–00:09 | `kamienice.html` | Seite Kamienice, Karte mit allen Punkten | Mapa pokazuje tylko obiekty, które źródło wymienia jako zabytek. |
| 3 | 00:09–00:14 | `kamienice.html` | Marken über der Karte hervorheben | Oznaczenia nad mapą mówią wprost: zbiór niepełny, rejestr tylko z Wikidanych. |
| 4 | 00:14–00:19 | `kamienice.html` | zur Karte scrollen, „Tylko kamienice (OSM)“ drücken | Kamienica w atlasie: budynek wielorodzinny, który źródło wymienia jako zabytek. |
| 5 | 00:19–00:24 | `kamienice.html` | wieder alle Denkmale; Bauzeit-Chip „okres budowy nieznany“ aus | Podajemy tylko okres budowy, nigdy dokładny rok. |
| 6 | 00:24–00:29 | `kamienice.html` | Seitenleiste neben der Karte bis „Źródła i stan“ rollen, Zeile Wikidane mit dem Ergebnis der Sichtprüfung hervorheben | Położenie punktów sprawdzono na ortofotomapie, na losowej próbie. |
| 7 | 00:29–00:34 | `kamienice.html` | stehen lassen | Wynik podano przy źródle: na obiekcie, tuż obok, poza obiektem, z przedziałem ufności. |
| 8 | 00:34–00:39 | `kamienice.html` | Seitenleiste bis „Rejestr zabytków, część z Wikidanych“ rollen | Rejestr zabytków: na razie tylko część z Wikidanych, bez rejestru NID. |
| 9 | 00:39–00:44 | `kamienice.html` | unter der Karte zu „Ograniczenia“ scrollen, Satz hervorheben | Brak punktu nie znaczy, że budynek nie jest zabytkiem. |
| 10 | 00:44–00:49 | `karta.html` | Karte: Registerpunkte aus Wikidata einschalten | Na mapie atlasu: punkty rejestru z Wikidanych jako osobna warstwa. |
| 11 | 00:49–00:54 | `karta.html` | OSM-Kennzeichnung dazu | Obok: oznaczenie zabytku w OpenStreetMap. Dwa źródła, dwie warstwy. |
| 12 | 00:54–00:59 | `karta.html` | dzielnica I Stare Miasto wählen (Karte fliegt hin) | Bliżej: Stare Miasto. |
| 13 | 00:59–01:04 | `karta.html` | Quellentafel | Źródła: Rejestr zabytków: Wikidane (Wikidata, CC0); Oznaczenie zabytku: © autorzy OpenStreetMap (ODbL); Budynki i kompleksy: BDOT10k, Główny Urząd Geodezji i Kartografii; Granice dzielnic: © autorzy OpenStreetMap (ODbL). Pełne noty o źródłach i licencje: strona „Dane”. |

## Film 3: Dane, nie opinie

Data, not opinions / Daten, keine Meinungen

| Datei | Format | Größe | SHA256 |
|---|---|---|---|
| `film3-dane-nie-opinie.mp4` | h264, 1280 × 720, 68,7 s | 4,28 MB | `5dd6bd38513379a22a96ed8449f949e35d5ff5714aa05e916a8cdf8ecfb8d200` |
| `film3-dane-nie-opinie.webm` | vp9, 1280 × 720, 68,7 s | 3,10 MB | `930d21a3054c760103e206a1b932da4f5c7daddd1c874aca143b2cbde1281a04` |
| `film3-dane-nie-opinie.pl.vtt` | WebVTT | 1,8 kB | `f2107f020043a4bd628b667fb4b8f26203a233720b6af4bcb48c760a09c1c2e6` |
| `film3-dane-nie-opinie.en.vtt` | WebVTT | 1,8 kB | `09c978880c8b69ce846306f606048167ace37080011d8119a47570b9aa6b4e8d` |
| `film3-dane-nie-opinie.de.vtt` | WebVTT | 1,8 kB | `0953703f64682d0400ce4096dfa867a34909257669eb7da83cdafd9c2b2dc1f5` |

Drehbuch (Zeiten aus `film3-dane-nie-opinie.pl.vtt`, Minuten:Sekunden):

| # | Zeit | Seite | Bild | Untertitel (pl) |
|---|---|---|---|---|
| 1 | 00:00–00:04 | `powietrze.html` | Titeltafel | Dane, nie opinie. Powietrze, ceny mieszkań, metodologia: co mówią liczby, a czego nie |
| 2 | 00:04–00:09 | `powietrze.html` | Seite Jakość powietrza | Jakość powietrza: wartości roczne stacji pomiarowych, obliczone przez EEA. |
| 3 | 00:09–00:13 | `powietrze.html` | zum Diagramm scrollen | Na wykresie: każda stacja i poziom dopuszczalny. |
| 4 | 00:13–00:18 | `powietrze.html` | stehen lassen (Zeiträume vorher und nachher sind markiert) | Przed: średnia 2016–2018. Po: średnia 2020–2022. Rok 2019 pominięty. |
| 5 | 00:18–00:23 | `powietrze.html` | zur Tabelle vorher/nachher scrollen | To porównanie w czasie, nie dowód przyczyny. |
| 6 | 00:23–00:28 | `powietrze.html` | stehen lassen | Nie uwzględniono wpływu pogody, roku pandemii ani innych działań. |
| 7 | 00:28–00:33 | `mieszkania.html` | Seite Rynek mieszkaniowy | Rynek mieszkaniowy: ceny transakcyjne z rejestru, nie ceny ofertowe. |
| 8 | 00:33–00:38 | `mieszkania.html` | zu den Medianen je dzielnica scrollen | Tylko mediany z co najmniej 10 transakcji, bez pojedynczych cen i adresów. |
| 9 | 00:38–00:43 | `mieszkania.html` | Markt „rynek wtórny“ wählen | Mediany dzielnic dotyczą różnych mieszkań; to nie porównanie takich samych mieszkań. |
| 10 | 00:43–00:48 | `mieszkania.html` | zu „Ograniczenia“ scrollen | Ograniczenia podano na tej samej stronie co liczby. |
| 11 | 00:48–00:53 | `metoda.html` | Metodologia, zu „Ograniczenia“ scrollen | Metodologia: zasady, ograniczenia i to, czego nie sprawdzono. |
| 12 | 00:54–00:58 | `dane.html` | Seite Dane, Downloads | Pliki do pobrania: GeoPackage, CSV i projekt QGIS. |
| 13 | 00:58–01:03 | `dane.html` | zu „Licencje“ scrollen | Licencje i noty o źródłach dosłownie, w języku oryginału. |
| 14 | 01:03–01:08 | `dane.html` | Quellentafel | Źródła: Powietrze: EEA; dane: GIOŚ (CC BY 4.0); Ceny mieszkań: Rejestr cen nieruchomości, Prezydent Miasta Krakowa (powiat 1261); dane udostępnione przez Główny Urząd Geodezji i Kartografii w serwisie www.geoportal.gov.pl; opracowanie własne (mediany, bez danych jednostkowych); Granice dzielnic: © autorzy OpenStreetMap (ODbL). Pełne noty o źródłach i licencje: strona „Dane”. |
