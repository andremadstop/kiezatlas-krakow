# Quellen des Pakets Wohnungsmarkt (DW)

Stand 13.11.2026. Zulieferung für `QUELLEN.md` und `daten/LIZENZ.md` (übernimmt die Belegschicht). Regeln der
Auswertung: `pruefen/DW_protokoll.md`; Zählungen: `belege/DW_mieszkania.md`; Entscheidungsvorschläge:
`docs/entscheidungen/DW.md`.

**Stand der Daten: echt seit 14.11.2026** (`eingang/rcn/1261_transakcje_ceny.gpkg`, Zählungen in
`belege/DW_mieszkania.md`; Stadtwerte erst ab 2021 weitgehend vollständig, 2019 rund 2 %, 2020 rund 26 % der Käufe; je dzielnica erst ab 2021). Die Transaktionsdaten kommen nur per Handdownload
(Abschnitt „Erwarteter Handdownload“); der Dienst WFS ist für das Abrufwerkzeug gesperrt (robots.txt, unten).

## Quellen

| Quelle | Nutzer | Adresse | Lizenz / Rechtsgrundlage | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| Rejestr cen nieruchomości (RCN), Powiat 1261 (Kraków, geführt vom Prezydent Miasta Krakowa), bereitgestellt vom GUGiK | `skripte/40_mieszkania.py` → `daten/mieszkania_odbl.js`, `belege/DW_mieszkania.md` | https://www.geoportal.gov.pl/pl/dane/rejestr-cen-nieruchomosci-rcn/ | keine Lizenz: Daten des RCN werden kostenfrei bereitgestellt, und für diese Daten wird keine Lizenz erteilt (art. 40a ust. 2 pkt 1 lit. k, art. 40c ust. 5 Prawo geodezyjne i kartograficzne); Pflicht zur Quellenangabe (art. 40c ust. 3; Regulamin geoportal.gov.pl § 3) | „Źródło: Rejestr cen nieruchomości, Prezydent Miasta Krakowa (powiat 1261); dane udostępnione przez Główny Urząd Geodezji i Kartografii w serwisie www.geoportal.gov.pl; opracowanie własne (mediany, bez danych jednostkowych)“ | H (Handdownload 14.11.2026, `eingang/rcn/1261_transakcje_ceny.gpkg`, Eintrag in `eingang/HERKUNFT.md`) | „Data ostatniej aktualizacji 2026-09-21“; jüngstes Dokumentdatum der Datei 29.09.2026 (`belege/DW_mieszkania.md`) |
| Stadtteilgrenzen | Zuordnung zur dzielnica | `daten/stadtteile_odbl.js` | ODbL 1.0 (Paket Gliederung und Bevölkerung, KR3) | wie dort | A (anderes Paket) | wie dort |

### Fundstellen (wörtlich)

Alle Dateien unter `kiezatlas-daten/krakow/`, Prüfsummen in `belege/rohdaten_DW.sha256` und
`rcn/2026-11-13/HERKUNFT.md`; abgerufen über `skripte/abruf.py` (Protokoll `abrufprotokoll.tsv`).

- **Kostenfrei:** Ustawa Prawo geodezyjne i kartograficzne, tekst jednolity Dz.U. 2026 poz. 1389
  (`2026-11-13/03_gebaeude/pgik_DU_2026_1389.pdf`, SHA256
  `f7b4ac608d0737a50bf59729d04ea7100f9e64728affcf3fd7582cbfcfaa0c24`), art. 40a ust. 2: „Nie pobiera się opłaty za:
  1) udostępnianie zbiorów danych: […] k) rejestru cen nieruchomości;“ mit Fußnote 7: „Dodana przez art. 1 pkt 1
  ustawy z dnia 26 września 2025 r. o zmianie ustawy – Prawo geodezyjne i kartograficzne (Dz. U. poz. 1542), która
  weszła w życie z dniem 13 lutego 2026 r.“
- **Keine Lizenz:** ebenda art. 40c ust. 5: „Licencji nie wydaje się w przypadku udostępnienia materiałów zasobu w
  związku ze zgłoszeniem prac lub jego uzupełnieniem oraz w przypadku udostępnienia materiałów zasobu, o których
  mowa w art. 40a ust. 2 pkt 1 i 3.“ (Zum Vergleich ust. 1: „Uprawnienia podmiotu dotyczące możliwości
  wykorzystywania udostępnionych mu materiałów zasobu określa licencja wydawana przez organ udostępniający te
  materiały.“ Für RCN entfällt diese Lizenz also.)
- **Quellenangabe:** ebenda art. 40c ust. 3: „Podmioty, które wykorzystują materiały zasobu, zamieszczają w
  publikowanych opracowaniach informacje o źródle pochodzenia użytego materiału.“
- **Nutzungsbedingungen des Portals:** Regulamin serwisu www.geoportal.gov.pl (in Kraft seit 8. Juli 2024),
  `rcn/2026-11-13/geoportal_regulamin.html`, SHA256
  `ece96e74ab79a695d3606363b6a1000f21ac815dcb174dbd557360168ab5cbc0`, § 3: „Publikacja materiałów z Serwisu jest
  dozwolona pod warunkiem umieszczenia informacji o źródle pochodzenia.“ Ein Verbot automatischen Sammelns steht
  im Regulamin nicht; es steht in den AccessConstraints der GUGiK-Kartendienste (`QUELLEN.md`, Zeile WMTS) und
  betrifft Kartenbilder und GetFeatureInfo, nicht den Download des GeoPackage.
- **Download als GeoPackage:** Informationsseite `rcn/2026-11-13/geoportal_rcn.html` (SHA256
  `945c10a06696691fb375f41c39ef56196880b3a838811444375ba3c427a0fb19`): „Pliki do pobrania dostępne są w formatach
  GeoParquet (dla danych krajowych i wojewódzkich) oraz GeoPackage (dla danych wojewódzkich i powiatowych).“ Pfad
  im Kartenmodul laut derselben Seite: „Dane do pobrania“ > „Dane powiatowe“ > „Rejestr Cen Nieruchomości“.
- **Veröffentlichte Attribute** (Grundlage der Spaltennamen im Skript und der Datenschutzregeln):
  `rcn/2026-11-13/geoportal_news_rcn_sprawdzisz.html` (Meldung vom 18.02.2026, SHA256
  `e7464199ecfd5988fd2c38ca55d3d732df4646ec7303e3dec91ae7c89044c4e2`), u. a. „oznaczenie transakcji rodzaj
  transakcji rodzaj rynku strona sprzedająca strona kupująca cena transakcji brutto kwota podatku VAT oznaczenie
  dokumentu data sporządzenia dokumentu […] udział w prawie do nieruchomości“ und für Lokale „identyfikator lokalu
  funkcja lokalu liczba izb numer kondygnacji powierzchnia użytkowa lokalu powierzchnia pomieszczeń przynależnych
  cena lokalu brutto kwota podatku VAT dla lokalu dodatkowe informacje adres budynku z lokalem“.

### Nicht genutzte Wege (mit Grund)

| Weg | Grund |
|---|---|
| WFS/WMS `https://mapy.geoportal.gov.pl/wss/service/rcn` | `robots.txt` antwortet mit 302 auf einen anderen Pfad; `skripte/abruf.py` wertet das als GESPERRT, bis von Hand entschieden (Befund `_robots/2026-11-13/mapy.geoportal.gov.pl.befund`). Kein Umweg versucht. |
| KICN (`integracja.gugik.gov.pl`) | nur Kartenbilder und GetFeatureInfo, beides fällt unter das Harvesting-Verbot der GUGiK-Dienste |
| GML der Starosten auf `dane.gov.pl` | Rechner auf der Sperrliste von `skripte/abruf.py` (robots.txt nicht auswertbar) |
| MSIP Kraków „Rejestr cen lokali mieszkalnych“ | Lizenz-STOPP der MSIP-Daten (KR3), Sperrliste |
| Einzelabfrage im Kartenmodul (Klick, GetFeatureInfo) | Einzelabfragen, nicht für eine Auswertung gedacht; automatisiert verboten |

## Datenschutz

Die Rohdatei enthält je Kauf Preis, Datum, Dokumentnummer, Art der Parteien, Lage (Geometrie, Adresse des
Gebäudes) und Kennungen von Parzelle, Gebäude und Lokal. Über Grundbuch und Adresse lässt sich ein Einzelkauf
einer Person zuordnen; die Einzelwerte gelten deshalb als personenbezogen (Annahme, rechtlich nicht geprüft). Darum:

- Rohdatei nur unter `kiezatlas-daten/krakow/eingang/rcn/`, nie im Repo, nicht in der Datenbank.
- Veröffentlicht werden nur Median und Fallzahl je dzielnica, Jahr und Markt; Median erst ab 10 Käufen, sonst
  `null` mit Grund. Keine Extremwerte, keine Perzentile, keine Kennung, keine Adresse, kein Dokument.
- `pruefen/DW_mieszkania.py` prüft das an der Ausgabe und mit verfälschten Kopien.

## Ausgaben und ihre Lizenz

| Ausgabe | Lizenz |
|---|---|
| `daten/mieszkania.js` (Mediane, Fallzahlen) | Quellenangabe nach art. 40c ust. 3 (Vermerk oben, steht im Kopf der Datei und in `quelle.vermerk`). Weil die dzielnica-Zuordnung die ODbL-Grenzen nutzt: Lizenzfolge für abgeleitete Kennzahlen offen wie bei den anderen Themen (KR3); bis dahin Vermerk beider Quellen. |
| `belege/DW_mieszkania.md` | wie oben |

## Erwarteter Handdownload

| Datei | Ablage | Format | Wer liest |
|---|---|---|---|
| GeoPackage des RCN für Powiat 1261 (Kraków) aus dem Kartenmodul „Pobierz dane“ von geoportal.gov.pl (Gruppe „Dane do pobrania“ > „Dane powiatowe“ > „Rejestr Cen Nieruchomości“), Dateiname beliebig, Endung `.gpkg` | `kiezatlas-daten/krakow/eingang/rcn/` (genau eine `.gpkg`-Datei; bei mehreren bricht das Skript ab) | GeoPackage (SQLite) mit einer Tabelle je Objektart; das Skript nimmt die Tabelle, die die Spalten für Funktion und Nutzfläche des Lokals hat. Spaltennamen nicht geprüft: das Skript sucht je Bedeutung aus einer festen Namensliste (`SPALTEN` in `skripte/40_mieszkania.py`, camelCase oder snake_case des RCN-Modells) und bricht mit der Liste der vorhandenen Spalten ab, wenn eine Pflichtspalte fehlt. Bezugssystem aus `gpkg_spatial_ref_sys` (EPSG). Größe nicht geprüft. | `skripte/40_mieszkania.py --spalten` (nur Tabellen und Spalten zeigen), dann `skripte/40_mieszkania.py` |

Nach dem Ablegen: erst `--spalten`, bei Abbruch die Namensliste als „Änderung <Datum>“ in `pruefen/DW_protokoll.md`
erweitern (eigener Commit vor dem Lauf), dann rechnen; die SHA256 der Datei steht danach in `daten/mieszkania.js`
und im Beleg. Ersatzweise ginge der GeoParquet-Auszug der Woiwodschaft; das liest das Skript nicht (nicht gebaut).
