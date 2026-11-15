# Entscheidungsvorschläge des Pakets Wohnungsmarkt (DW), 13.11.2026

Belege: `belege/DW_mieszkania.md` (Zählungen), `pruefen/DW_protokoll.md` (Regeln vor dem ersten Lauf),
`quellen-DW.md` (Quelle, Rechtsgrundlage, Fundstellen). Stand: **nur Beispieldaten**, Handdownload ausstehend.

## Eigentum (Vorschlag für die Eigentümer-Tabelle in `docs/rundgang.md`)

| Datei | Eigentümer |
|---|---|
| `skripte/40_mieszkania.py` | DW |
| `daten/mieszkania.js`, `daten/schema/mieszkania.json` | DW |
| `pruefen/DW_mieszkania.py`, `pruefen/DW_protokoll.md` | DW |
| `belege/DW_mieszkania.md`, `belege/rohdaten_DW.sha256` | DW |
| `quellen-DW.md`, `docs/entscheidungen/DW.md` | DW (bis zur Übernahme durch die Belegschicht) |
| `docs/entscheidungen/DW-texte/<lang>/mieszkania.js` | DW; Ziel `texte/<lang>/mieszkania.js` (Namensraum laut `daten/schema/texte.md` schon dem Themenpaket zugeordnet) |

## RCN ohne Lizenz-STOPP

- **Anlass:** Der Auftrag verlangt STOPP bei unklarer Lizenz.
- **Vorschlag:** kein STOPP. Für Daten des RCN wird nach art. 40c ust. 5 PGiK keine Lizenz erteilt (kostenfrei
  nach art. 40a ust. 2 pkt 1 lit. k); Pflicht ist nur die Quellenangabe (art. 40c ust. 3), gleichlautend der
  Regulamin von geoportal.gov.pl § 3. Wortlaut in `quellen-DW.md`.
- **Begründung:** Gesetz und Portalbedingungen widersprechen sich nicht; beide verlangen nur die Quelle.
- **Verworfen:** STOPP wie bei MSIP (dort fehlt jede Freigabe; hier regelt das Gesetz die Nutzung).
- **Neu prüfen wenn:** das GeoPackage selbst oder seine Metadaten eine eigene Lizenz- oder Nutzungsangabe
  tragen (beim ersten echten Lauf ansehen), oder art. 40a/40c geändert wird.

## Nur Handdownload, kein WFS

- **Anlass:** `robots.txt` von `mapy.geoportal.gov.pl` antwortet mit 302; `abruf.py` sperrt.
- **Vorschlag:** Transaktionsdaten nur aus dem GeoPackage, das Andre aus dem Kartenmodul lädt. Bis dahin
  `--beispiel` mit `fixture: true`.
- **Verworfen:** WFS über einen anderen Pfad oder mit eigener Auslegung des 302 (Umweg um die Sperre); GML von
  dane.gov.pl (Sperrliste).
- **Neu prüfen wenn:** jemand den robots-Befund von `mapy.geoportal.gov.pl` von Hand entscheidet.

## Mindestfallzahl 10, keine Extremwerte

- **Anlass:** Einzelkäufe sind über Grundbuch und Adresse einer Person zuordenbar.
- **Vorschlag:** Median erst ab 10 Käufen je dzielnica, Jahr und Markt, sonst `null` mit Grund; Fallzahl n wird
  veröffentlicht; kein Minimum, Maximum, Perzentil, Mittelwert; keine Zeile je Kauf im Repo.
- **Begründung:** Mindestfallzahl wie im Auftrag; Extremwerte sind immer ein einzelner Kauf.
- **Verworfen:** Mittelwert (empfindlich gegen Ausreißer und Tippfehler); feinere Raumeinheit als dzielnica
  (zu kleine Fallzahlen, Rückschluss auf Gebäude).
- **Neu prüfen wenn:** eine Rechtsprüfung (nicht erfolgt) eine andere Grenze verlangt.

## Textvorschlag außerhalb von `texte/`

- **Anlass:** `pruefen/texte.py` meldet jeden Schlüssel ohne Verwendung in `vorlagen/` als Befund; die
  Themenseite kommt erst in Phase Seitenbau. Mit den Texten unter `texte/` wäre `pruefen.sh` rot.
- **Vorschlag:** Texte bis Phase Seitenbau unter `docs/entscheidungen/DW-texte/<lang>/mieszkania.js`; dieselben Regeln
  (ohne Verwendung) prüft `pruefen/DW_mieszkania.py`. Phase Seitenbau verschiebt die drei Dateien nach `texte/<lang>/`.
- **Verworfen:** Texte unter `texte/` mit rotem `pruefen.sh`; Ausnahme in `pruefen/texte.py` (gemeinsame Datei,
  nicht Eigentum des Pakets); Platzhalter in `vorlagen/mieszkania.html` (Seitenbau ist Phase Seitenbau).

## Für die Integration offen

- Aufnahme von `pruefen/DW_mieszkania.py` in `pruefen.sh` (gemeinsame Datei). Vorschlag: eine Zeile
  `pruef "Wohnungsmarkt: Vertrag, Mindestfallzahl, Reproduktion (pruefen/DW_mieszkania.py)" py pruefen/DW_mieszkania.py`.
- Lizenzfolge der Kennzahlen, deren Raumbezug aus ODbL-Grenzen kommt (KR3), wie bei den anderen Themen.
- `belege/README.md`, `QUELLEN.md`, `docs/rundgang.md`: Einträge aus diesem Paket übernehmen.
