# Quellen des Pakets Sanierungsatlas Wohnungsbestand (Lieferung an die Belegschicht)

Stand 13.11.2026, Zweig `Arbeitszweig ds`. Skript: `skripte/36_sanierung.py`. Regeln: `pruefen/DS_protokoll.md`. Lauf:
`belege/DS_sanierung_lauf.md`. Weg: A = automatischer Abruf über `skripte/abruf.py`, H = Handdownload durch den Betreiber
nach `$KIEZ_DATEN/eingang/`, L = schon geladen. Pfade relativ zu `$KIEZ_DATEN` (Standard `../kiezatlas-daten/krakow`).
Prüfsummen der Abrufe dieses Pakets: `belege/rohdaten-DS-2026-11-13.sha256`.

## Quellen

| Quelle | Nutzer (Ausgabe) | URL | Lizenz | wörtlicher Vermerk, Fundstelle | Weg | Stand |
|---|---|---|---|---|---|---|
| Zarząd Budynków Komunalnych w Krakowie, „Wykaz budynków i obiektów w zarządzie ZBK na dzień 2025-12-01“ (PDF, 26 Seiten, Załącznik nr 635620, Fassung 1 vom 18.12.2025) | `daten/sanierung.js`, `daten/sanierung_odbl.js` | Dokument https://www.bip.krakow.pl/?bip_id=32&mmi=10127, Datei https://www.bip.krakow.pl/plik.php?zid=635620&wer=1&new=t&mode=shw | informacja sektora publicznego im BIP der Gmina Miejska Kraków; Weiterverwendung **für jeden Zweck** unter drei Pflichten (Quelle mit Erstellungs- und Abrufzeit, Hinweis auf Verarbeitung, Haftungsklausel wörtlich); keine eigenen Regeln des ZBK | siehe Abschnitt „Weiterverwendung, wörtlich“ (`zbk/2026-11-13/bip_dok48482_ponowne.html`, SHA256 `29cf66e42695f1dc119e0aba7fdb25204ae7f007f49ceb961c08767aad3e2391`) | A (13.11.2026, `zbk/2026-11-13/HERKUNFT.md`) | Stichtag der Liste 01.12.2025 |
| BDOT10k, Paket 1261 (GUGiK): `OT_BUBD_A`, `OT_ADJA_A` | Verknüpfung und Typologie in beiden Dateien | https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip | gebührenfrei, keine Lizenz, Quellenangabe Pflicht | Prawo geodezyjne i kartograficzne, Dz.U. 2026 poz. 1389, art. 40c ust. 3: „Podmioty, które wykorzystują materiały zasobu, zamieszczają w publikowanych opracowaniach informacje o źródle pochodzenia użytego materiału.“ (`2026-11-13/03_gebaeude/pgik_DU_2026_1389.pdf`); Fundstellen wie `quellen-DZ.md` | L | Dateien vom 03.10.2026 |
| Modele 3D budynków LoD2, Powiat 1261 (GUGiK), Stand 2017 | Höhe `h` mit Herkunft `hq = lod2` in `daten/sanierung_odbl.js` | https://opendata.geoportal.gov.pl/InneDane/Budynki3D/LOD2/1261_gml.zip | frei, Quellenangabe nach art. 40c ust. 3 | „Modele 3D budynków są dostępne bezpłatnie i możliwe do dowolnego wykorzystania.“ (https://www.geoportal.gov.pl/pl/dane/inne-dane/modele-3d-budynkow/, `eingang/HERKUNFT.md`); Lesart vom Master am 13.11.2026 als ausreichend bestätigt | H (`eingang/lod2_1261_gml.zip`, SHA256 `de14ed1860865d58b5b4c57b256e1a0da7218680effe19be66a885c290091356`) | 2017 (Last-Modified 01.03.2019) |
| OpenStreetMap, Auszug Małopolska: `addr:*`, `building`, `heritage`; Grenzen der dzielnice (admin_level 9, Leser des Pakets Gliederung und Bevölkerung) | nur `daten/sanierung_odbl.js` | https://download.geofabrik.de/europe/poland/malopolskie.html | ODbL 1.0 | „OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF).“ (`2026-11-13/08_fussweg/osm_copyright.html`) | H (`eingang/malopolskie-261112.osm.pbf`, SHA256 `525d0d227cb9c876c4df02278e7fac870f0825ab0ae2c7228af6dc5c9e0f5a7e`) | 12.11.2026 |
| FuturHist, Demonstrator Kraków | Vergleichsangabe zum ZBK-Bestand im Beleg; nicht in den Daten und nicht an der Ortsmarke (KR24; das Feld `ortsmarke.quelle` ist entfallen) | https://futurhist.eu/demonstrators/krakow/ | nur Tatsachenangaben zitiert (Adresse, „over 500 buildings“, „Over 130 buildings managed by ZBK are under conservation protection“), keine Bilder, kein Text übernommen | Adresse auf der Seite: „18 Kościuszki Street 30-105 Kraków, Poland“ (`futurhist/2026-11-13/demonstrators_krakow.html`, SHA256 `fee9713c5aa6e0bfca315adf5e67ce2d69a2ecdb1a469da38aa0a3d4d2e27c0d`) | A | Abruf 13.11.2026 |
| Barnaś, Jeleński, Nowak-Ocłoń, Racoń-Leja u. a., Energy 263 (2023) 125774 | nur bibliographisch (`typologie.literatur`) | https://doi.org/10.1016/j.energy.2022.125774 | – | nicht abgerufen; keine Zahl und keine Daten daraus verwendet | – | – |

## Weiterverwendung, wörtlich

Fundstelle: „Zasady udostępniania informacji publicznych będących w posiadaniu Gminy Miejskiej Kraków w celu ich
ponownego wykorzystywania“, https://www.bip.krakow.pl/?dok_id=48482 (abgerufen 13.11.2026). Das BIP des ZBK verweist
unter „Ponowne wykorzystywanie informacji sektora publicznego“ (https://www.bip.krakow.pl/?bip_id=32&mmi=16801) mit
HTTP 302 genau auf diese Seite (Zeile im Abrufprotokoll `$KIEZ_DATEN/abrufprotokoll.tsv`, 13.11.2026 17:29:29 UTC).
Der ZBK steht nicht in der Liste der Einheiten mit eigenen Regeln (dort nur MOCAK, Muzeum Historii Fotografii,
Biblioteka Kraków, Bunkier Sztuki) und gehört nicht zu den ausgenommenen Kultur- und Bildungseinrichtungen.

> I. Ponownemu wykorzystywaniu podlega informacja sektora publicznego: udostępniona w systemie teleinformatycznym
> Gminy Miejskiej Kraków, w szczególności na stronie Biuletynu Informacji Publicznej Miasta Krakowa
> (www.bip.krakow.pl) lub zamieszczona w miejskich serwisach internetowych; […]
>
> II. […] Jeśli dla danej informacji sektora publicznego, udostępnionej w powyższy sposób, nie zostały określone
> inne warunki ponownego wykorzystywania, osoby fizyczne, osoby prawne i jednostki organizacyjne nieposiadające
> osobowości prawnej wykorzystujące ponownie te informacje, są każdorazowo zobowiązane do: poinformowania każdego o
> źródle (np.: adresie www BIP podmiotu, adresie www innego źródła udostępniającego informację, wskazaniu nośnika lub
> źródła emisji), czasie wytworzenia i pozyskania informacji sektora publicznego od Gminy Miejskiej Kraków;
> informowania o przetworzeniu informacji ponownie wykorzystywanej; podania zakresu odpowiedzialności Gminy Miejskiej
> Kraków za udostępniane lub przekazywane informacje o treści: „Gmina Miejska Kraków nie ponosi odpowiedzialności za:
> […]”
>
> III. […] Gmina Miejska Kraków zapewnia możliwość dowolnego wykorzystywania utworu lub przedmiotu praw pokrewnych
> […] lub bazy danych, do celów komercyjnych i niekomercyjnych, tworzenia i rozpowszechniania kopii utworu lub bazy
> danych, w całości lub we fragmentach, oraz wprowadzania zmian i rozpowszechniania utworów zależnych, pod
> warunkiem, że nie narusza to ww. ustawy lub ustawy z dnia 27 lipca 2001 r. o ochronie baz danych […], z
> zastrzeżeniem praw przysługujących podmiotom trzecim.

Umsetzung der drei Pflichten in beiden Dateien: `quellen.zbk.vermerk` (Quelle mit BIP-Adresse, data wytworzenia
2025-12-18, data pozyskania 2026-11-13, „Informacja przetworzona: …“) und `quellen.zbk.odpowiedzialnosc` (die
Haftungsklausel, vom Skript wörtlich aus der abgelegten Seite gelesen; `pruefen/DS_sanierung.py` prüft, dass sie in
beiden Dateien gleich ist). Der Hinweis auf die Verarbeitung ist je Datei verschieden: Die Zählungen nennen „plik nie
zawiera adresów“, die verortete Datei nennt „geokodowanie adresów (OpenStreetMap), powiązanie z budynkami BDOT10k i
modelami LoD2“; die Quellenangabe davor ist gleich und wird geprüft. „Data wytworzenia“ ist das Erstellungsdatum der PDF-Datei (Metadaten `CreationDate` 18.12.2025, gleich dem
Datum, an dem der Anhang eingestellt wurde); die Liste selbst nennt den Stichtag 01.12.2025. Die Metka der
BIP-Seite („Data wytworzenia: 2018-02-06“, „Data aktualizacji: 2026-03-16“) betrifft das übergeordnete Dokument,
nicht die Liste. Rechte Dritter: keine erkennbar; personenbezogene Angaben (Bruchteile von Privatpersonen,
Namen in Metka und PDF-Metadaten) werden nicht weitergegeben (siehe `pruefen/DS_protokoll.md`, Regel 2 und 3).

## Ausgaben und ihre Lizenz

| Datei | Inhalt | Lizenz |
|---|---|---|
| `daten/sanierung.js` | echte Daten: Einträge der ZBK-Liste je Art, Eigentumsklasse und dzielnica laut Liste; Typologie-Schätzung aus BDOT10k je Delegatur; Ortsmarke ohne Lage | Weiterverwendung nach den Regeln der Gmina Miejska Kraków (Vermerk und Haftungsklausel im Feld `quellen.zbk`); BDOT10k Quellenangabe nach art. 40c ust. 3 |
| `daten/sanierung_odbl.js` | echte Daten: Verortung, Gegenprobe der dzielnica, Verknüpfung mit BDOT10k und LoD2, Punkte nur für öffentliches Eigentum (ohne Einfamilienhäuser laut BDOT10k), Typologie je dzielnica, Ortsmarke mit Lage (Zahlen: `belege/DS_sanierung_lauf.md`) | ODbL 1.0, © OpenStreetMap-Mitwirkende; dazu die Vermerke von ZBK, BDOT10k und LoD2 im Feld `quellen` |
| `$KIEZ_DATEN/abgeleitet/sanierung/zbk_tabelle.tsv` | gelesene Tabelle mit Rohtext (Adressen, Wortlaut der Eigentumsspalte) | nur intern, nicht im Repo, nicht ausliefern |

## Offene Handdownloads und Klärungen

| Was | Warum | Ablage |
|---|---|---|
| PRG-Adresspunkte (GUGiK) für Powiat 1261 | amtliche Adressen ohne ODbL; damit könnte die Verortung aus `_odbl` heraus. BDOT10k hat keine Adressen. Nicht abgerufen (Größe und Bezugsweg nicht geprüft) | `eingang/` mit Lizenzseite als HTML |
| Rejestr zabytków (NID), Gminna ewidencja zabytków | Denkmalstatus der ZBK-Gebäude; die Liste nennt ihn nicht, OSM `heritage` trifft fast keinen verorteten Eintrag (Zahl im Beleg, Schritt 4) | wie `quellen-DZ.md` |
| neuere Fassung der ZBK-Liste | Die Themenentscheidung nennt eine Fassung vom 01.05.2026 mit Verwalter und Registernummer auf plikimpi.krakow.pl; das BIP bot am 13.11.2026 nur die Fassung zum 01.12.2025 ohne diese Spalten an (Dziennik zmian zuletzt 16.03.2026). Fundstelle der genannten Fassung nicht gefunden | `zbk/<stand>/` mit neuer Prüfsummenliste |
| Sichtprüfung der Typologie-Stichprobe | Punkte im Beleg (Schritt 5); Kartenbilder der GUGiK dürfen nicht automatisch abgerufen werden | Ergebnis als Nachtrag in `belege/` |
