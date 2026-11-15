# Paket Luft (D7): Abrufe, Lizenz- und Rechtsfundstellen, Grenzen

Stand 13.11.2026. Belegt, was das Paket aus dem Netz geholt hat, mit welchem Wortlaut Lizenz, Grenzwerte und Stichtag
begründet sind, und was nicht geprüft ist. Die Zählung des Datenlaufs steht getrennt in `belege/D7_luft_lauf.md`
(erzeugt von `skripte/32_powietrze.py`). Quellenliste und Handdownloads: `quellen-D7.md`.

## 1. Abrufe

Alle über `skripte/abruf.py` (Kennung `kiezatlas-krakow`), jede Anfrage im gemeinsamen Protokoll
`kiezatlas-daten/krakow/abrufprotokoll.tsv`. Zählung aus diesem Protokoll (Zeilen dieser Rechner zwischen
14:10 und 14:21 UTC am 13.11.2026):

| Rechner | Anfragen | davon robots.txt | gespeichert (200) | Ergebnis |
|---|---|---|---|---|
| powietrze.gios.gov.pl | 1 | 1 | 0 | DNS ohne Antwort, gesperrt nach Regel |
| www.eea.europa.eu | 2 | 1 | 2 | robots.txt, Copyright notice |
| sdi.eea.europa.eu | 4 | 1 | 4 | robots.txt, zwei Metadatensätze, eine CSW-Suche |
| discomap.eea.europa.eu | 7 | 1 | 3 | 2 Weiterleitungen (301, nicht verfolgt), Betrachter, `connector.js`, Feldliste `init`, ArcGIS-Pfad 404 |
| discodata.eea.europa.eu | 4 | 1 | 2 | eine Anfrage 403; zwei Antworten 200 mit Fehlermeldung statt Daten |
| air.discomap.eea.europa.eu | 1 | 1 | 0 | robots.txt 302, gesperrt |
| aqportal.discomap.eea.europa.eu | 1 | 1 | 0 | robots.txt 301, gesperrt |
| edziennik.malopolska.uw.gov.pl | 1 | 1 | 0 | TLS-Fehler, gesperrt |
| sprawyspoleczne.krakow.pl | 2 | 1 | 2 | robots.txt, Uchwała (PDF) |
| eur-lex.europa.eu | 1 | 1 | 0 | robots.txt 202, gesperrt |
| api.sejm.gov.pl (nur Paket Luft) | 2 | 0 | 2 | ELI-Metadaten DU/2012/1031, Tekst jednolity DU/2021/845 (PDF) |
| **Summe** | **26** | **10** | **15** | |

robots.txt von api.sejm.gov.pl stammt aus einem früheren Abruf eines anderen Pakets und ist hier nicht mitgezählt.
Prüfsummen der zehn Dateien, auf die sich Daten und Texte stützen: `belege/rohdaten_D7.sha256` (von `pruefen.sh`
gegen die Ablage geprüft). Die zwei Fehlermeldungen von discodata (`eea/2026-11-13/test/`) und die CSW-Suche
sind Fundweg, keine Grundlage, und stehen nicht in der Liste. **Messwerte wurden keine abgerufen.**

## 2. Wörtliche Fundstellen

### 2.1 Lizenz der EEA-Jahresstatistik

`eea/2026-11-13/sdi_6e191a3b_statistik.xml` (Metadatensatz 6e191a3b-258d-491e-b636-6cbb15cf473b, „Air quality annual
statistics calculated by the EEA“), Feld der Nutzungsbedingungen:

> License CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Copyright holder: European Commission.

`eea/2026-11-13/eea_legal_notice.html` (https://www.eea.europa.eu/en/legal-notice), Abschnitt „Copyright notice“:

> Information, documents and material available on this website and for which the EEA holds the rights of use are
> public and may be re-used without prior permission, free of charge, for commercial or non-commercial purposes,
> provided that the EEA is always acknowledged as the original source of the material and that the original meaning
> or message of the content is not distorted. […] The re-use of certain data may be subject to different conditions,
> and if so the item concerned is accompanied by a copyright mark or other mention of the specific conditions
> relating to it.

und „Third party content“:

> The above-mentioned permissions do not apply to content supplied by third parties.

**Einordnung:** Der Datensatz trägt eine eigene, ausdrückliche Lizenzzeile (CC BY 4.0). Nach dem Satz „accompanied
by … other mention of the specific conditions“ geht diese der allgemeinen Seite vor. Die Jahreskennwerte sind von
der EEA berechnet; die zugrunde liegenden Messungen stammen von der GIOŚ. Ob die Klausel „Third party content“ die
berechneten Kennwerte erfasst, ist **nicht geprüft**; gelesen als nein, weil der Datensatz selbst die Lizenz nennt.
Folge: Vermerk „EEA (Daten GIOŚ), CC BY 4.0“ in Datei und Seite, Abzeichen „orientacyjnie“.

### 2.2 Grenzwerte

`rozporzadzenie_poziomy/2026-11-13/DU_2021_845.pdf`, Załącznik nr 1, Tabelle „Poziomy dopuszczalne niektórych
substancji w powietrzu …“, abgelesen (Spalten: Okres uśredniania, Poziom dopuszczalny w µg/m3, Dopuszczalna częstość
przekraczania, Termin osiągnięcia):

| Lp. | Substanz | Zeile im PDF (Textauszug) |
|---|---|---|
| 2 | dwutlenek azotu | „jedna godzina 200c) 18 razy … 2010“; „rok kalendarzowy 40c) … 2010“ |
| 6 | pył zawieszony PM2,5 | „rok kalendarzowy 25c), j) … 2015“; „20c), k) … 2020“ |
| 7 | pył zawieszony PM10 | „24 godziny 50 35 razy … 2005“; „rok kalendarzowy 40c) … 2005“ |

Fußnoten: „j) Poziom dopuszczalny dla pyłu zawieszonego PM2,5 do osiągnięcia do dnia 1 stycznia 2015 r. (faza I).“
und „k) Poziom dopuszczalny dla pyłu zawieszonego PM2,5 do osiągnięcia do dnia 1 stycznia 2020 r. (faza II).“
Status: `eli_DU_2012_1031.json`, „inForce“: „IN_FORCE“, „status“: „akt posiada tekst jednolity“, Verweis auf
DU/2021/845. Dieselben Werte stehen ein zweites Mal von Hand in `pruefen/D7_powietrze.py` und werden gegen die Datei
geprüft.

### 2.3 Stichtag (Kohleverbot)

`uchwala_antysmogowa/2026-11-13/sprawyspoleczne_zalacznik_424838.pdf`, Kopf: „Dziennik Urzędowy Województwa
Małopolskiego, Kraków, dnia 1 lutego 2016 r., Poz. 812“, „Uchwała Nr XVIII/243/16 Sejmiku Województwa Małopolskiego
z dnia 15 stycznia 2016 roku w sprawie wprowadzenia na obszarze Gminy Miejskiej Kraków ograniczeń w zakresie
eksploatacji instalacji, w których następuje spalanie paliw“.

> § 4. W instalacjach wskazanych w § 2 dopuszcza się wyłącznie stosowanie następujących rodzajów paliw:
> 1) gazu ziemnego wysokometanowego lub zaazotowanego (w tym skroplonego gazu ziemnego), propan-butanu, biogazu
> rolniczego lub innego rodzaju gazu palnego, 2) lekkiego oleju opałowego […]

> § 6. […] 2. Uchwała wchodzi w życie z dniem 1 września 2019 r.

Die Machbarkeitsprobe hatte die Nummer XVIII/243/16 als „aus Wissen, nicht geprüft“ geführt; sie ist hiermit am
Primärtext belegt.

## 3. Grenzen (nicht geprüft)

- **Keine echten Messwerte.** `daten/powietrze.js` trägt Beispieldaten (`fixture: true`, Kennungen `FIKCJA-…`), bis
  der EEA-Export abgelegt ist. Die Kopfzeile des Exports ist nicht gesehen; das Skript bricht bei fehlenden Spalten ab.
- Ob `City` = „Kraków“ in den EEA-Daten genau der Gemeindegrenze entspricht (Zuordnung nach Urban Audit).
- Ob die EEA-Jahreswerte mit der amtlichen Jahresbewertung der GIOŚ (ocena roczna) übereinstimmen; dafür ist die
  GIOŚ-Gegenprobe vorgesehen. Lizenz der GIOŚ-Daten nicht gelesen (Rechner nicht erreichbar).
- Änderungen der Uchwała nach 2016 und der Verordnung nach dem 13.11.2026; die Uchwała ist ein Abzug von
  sprawyspoleczne.krakow.pl, nicht aus dem Dziennik selbst (der war nicht erreichbar).
- Urheberrechtsfreiheit der Rechtsakte (art. 4 ustawy o prawie autorskim): aus Wissen, Wortlaut nicht geprüft.
- Ursachen von Veränderungen: keine Aussage. Vorher/Nachher ist ein Vergleich zweier Zeitfenster um einen belegten
  Stichtag; Wetter, Pandemiejahr 2020 und weitere Maßnahmen sind nicht geprüft und nicht herausgerechnet.
