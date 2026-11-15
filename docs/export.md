# Öffentlicher Export: Lesehilfe und Ersetzungen

Dieses Repository ist ein bereinigter Export des internen Arbeitsstands (Entscheidung KR50 in
`docs/entscheidungen.md`). Die Arbeitshistorie ist nicht enthalten; die öffentliche Historie beginnt mit Version
1.0.0.

## Commit-Kennungen

Belege, Prüfprotokolle, `README.md`, `CHANGELOG.md` und `docs/` nennen Commits der internen Historie (etwa den
Prüfstand `belege/pruefstand-<datum>-<commit>/`). Diese Commits gibt es in diesem Repository nicht. Sie bezeichnen den
Stand, an dem ein Protokoll entstand; der Inhalt der Dateien ist hier derselbe bis auf die Ersetzungen unten. Wer
nachrechnen will, rechnet am Stand dieses Repositorys (`./pruefen.sh`, `docs/running.md`).

## Begriffe des Baus

- **Pakete:** Der Atlas entstand in Arbeitspaketen. Ihre Kürzel stehen in Dateinamen (`belege/D5_*.md`,
  `docs/entscheidungen/D5.md`, `quellen-D5.md`, `pruefen/D5_*.py`): D1 Infrastruktur, D2 OSM und Fußwegnetz,
  d3 Oberflächen-Texte, D4 Gliederung und Bevölkerung, D5 Gebäude und 3D, D6 Versorgung und Takt, D7 Luft,
  D8 Grundkarte, D13 Deploy, DE Echtlauf der Daten, DF Schrift und Grundkarten-Anbindung, dk Klima, DS Sanierungsatlas,
  DW Wohnungsmarkt, DZ Denkmale und Kamienice, S1 bis S4 Seiten, N1 Daten-Nacharbeit, N2 Oberfläche und
  Auslieferung, O Offene Wissenschaft; `fix-*`, `p4-*` und `review-*` sind Behebungen nach Durchsichten. Je Paket ein
  Vorschlag unter `docs/entscheidungen/`; angenommene Vorschläge stehen als KR1 ff. in `docs/entscheidungen.md`.
- **Phase Datenpakete / Phase Seitenbau / Phase Nacharbeit:** Bauabschnitte: erst die Datenpakete (13.11.2026),
  dann die Seiten mit ihren Texten (14.11.2026), danach Behebung der Sichtung.
- **Paket Grundgerüst / Paket Themen:** Bauabschnitte des Kiezatlas Potsdam, aus dem Gerüst, Prüfungen und Verträge
  stammen.
- **Projektleitung:** die Stelle, die Vorschläge der Pakete bestätigt oder verworfen hat (André Stiebitz).
- **Freigabe der Projektleitung:** Entscheidung vor dem Bau des Kraków-Atlas.
- **Arbeitszweig `<name>`:** Git-Zweig der internen Historie, in dem ein Paket gebaut wurde.
- **`<Tag>`:** Name eines internen Tags der Geodaten-Import-Pipeline; maßgeblich ist der daneben stehende Commit
  `12bae5bc96cf34355c8c5a723eb444e66f776f2d` (`skripte/lauf.sh`, `PIPELINE_SOLL`).

## Ersetzungen

Mechanisch ersetzt wurden nur die Stellen, die `skripte/oeffentlich_pruefen.py` vor einer Veröffentlichung meldet
(Ausnahmeliste `skripte/oeffentlich_ausnahmen.tsv`, Art „vor_veroeffentlichung“). Sonst sind die Dateien
unverändert, auch die Prüfprotokolle unter `belege/` (dort ändern die Ersetzungen nur Ordnernamen und Wörter, keine
Zahl und kein Ergebnis).

- Ordner des Arbeitsrechners: Datenordner → `$KIEZ_DATEN`, Repository → `<Arbeitsordner>`, Zwischenordner →
  `<zwischenordner>`, übriges Heimatverzeichnis → `<home>/`.
- Name des eigenen Webservers → `<server>` (`docs/auslieferung.md`, `skripte/deploy_kopie.py` und Zitate in
  Prüfprotokollen).
- Arbeitsvermerke → Begriffe oben.

| Ersetzung | Stellen | Dateien |
|---|---|---|
| Arbeitsvermerk → <Tag> | 50 | 12 |
| Arbeitsvermerk → Arbeitszweig d2 | 10 | 10 |
| Arbeitsvermerk → Arbeitszweig d8 | 1 | 1 |
| Arbeitsvermerk → Arbeitszweig de | 7 | 3 |
| Arbeitsvermerk → Arbeitszweig df | 9 | 5 |
| Arbeitsvermerk → Arbeitszweig ds | 14 | 13 |
| Arbeitsvermerk → Arbeitszweig dz | 1 | 1 |
| Arbeitsvermerk → Arbeitszweig fix | 5 | 3 |
| Arbeitsvermerk → Arbeitszweig integration | 8 | 7 |
| Arbeitsvermerk → Arbeitszweig n1 | 3 | 3 |
| Arbeitsvermerk → Arbeitszweig n2 | 4 | 4 |
| Arbeitsvermerk → Arbeitszweig o | 1 | 1 |
| Arbeitsvermerk → Arbeitszweig p4 | 9 | 5 |
| Arbeitsvermerk → Arbeitszweig p4b | 10 | 3 |
| Arbeitsvermerk → Arbeitszweig s1 | 15 | 14 |
| Arbeitsvermerk → Arbeitszweig s2 | 9 | 6 |
| Arbeitsvermerk → Arbeitszweig s3 | 2 | 2 |
| Arbeitsvermerk → Arbeitszweig s4 | 3 | 2 |
| Arbeitsvermerk → Paket Gebäude und 3D | 11 | 10 |
| Arbeitsvermerk → Paket Grundgerüst | 7 | 6 |
| Arbeitsvermerk → Paket Grundkarte | 10 | 10 |
| Arbeitsvermerk → Paket Themen | 5 | 1 |
| Arbeitsvermerk → Paket Wohnungsmarkt | 11 | 11 |
| Arbeitsvermerk → Phase Datenpakete | 25 | 13 |
| Arbeitsvermerk → Phase Nacharbeit | 1 | 1 |
| Arbeitsvermerk → Phase Seitenbau | 80 | 21 |
| Arbeitsvermerk → Projektleitung | 160 | 19 |
| Ordner → $KIEZ_DATEN | 52 | 13 |
| Ordner → <Arbeitsordner> | 10 | 10 |
| Ordner → <home>/ | 52 | 9 |
| Ordner → <zwischenordner> | 2 | 1 |
| Rechnername im Zitat → <server> | 29 | 9 |
| Webserver → <server> | 3 | 2 |
| nicht exportierte Datei im Prüfprotokoll → <nicht im Export> | 15 | 1 |

Nicht im Export: Werkzeug und Schrittliste der Herausgeberin für diese Veröffentlichung.
