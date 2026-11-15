# Beleg Themenseiten Luft, Wohnungsmarkt, Klima: Zählungen und Prüfläufe

Stand 14.11.2026, Zweig `Arbeitszweig s3`, Prüflauf auf Commit `be1fae1`. Die Seiten bauen nur auf vorhandenen Datendateien
auf; neue Zahlen entstehen nicht. Jede auf den Seiten gezeigte Zahl kommt zur Laufzeit aus `daten/*.js` und wird über
`i18n.js` formatiert; die Vorlagen (`vorlagen/powietrze.html`, `mieszkania.html`, `klimat.html`) enthalten keine Zahl.

## Datenstand je Seite (abgelesen am Feld `fixture` der geladenen Dateien)

| Seite | lädt | Stand | auf der Seite |
|---|---|---|---|
| `powietrze` | `daten/powietrze.js` | Beispiel (`fixture: true`, Kennungen `FIKCJA-…`) | Kasten „Dane przykładowe“ mit fehlender Quelle (EEA-Jahresstatistik, Handdownload), Hinweis des Rahmens, Marke auf 3 von 3 Abbildungen/Tabellen; echt und als echt benannt: Grenzwerte (Dz.U. 2021 poz. 845) und Wortlaut der Uchwała XVIII/243/16. Keine Stationskarte, solange Beispiel. |
| `mieszkania` | `daten/mieszkania.js` | Beispiel (`fixture: true`) | Kasten mit fehlender Quelle (RCN-GeoPackage, Handdownload), Hinweis des Rahmens, Marke auf 3 von 3 Zonen; echt: Stadtteilnamen (Ortskonfiguration), Mindestfallzahl aus `regeln.mindestfallzahl`. |
| `klimat` | `daten/stadtteile_odbl.js`, `klimat.js`, `klimat_zellen.js`, `klimat_stadtteile_odbl.js` | echt | keine Beispielkennzeichnung (0 Marken); ODbL-Vermerk im Fuß, weil eine `_odbl`-Datei geladen wird. |

## Texte

| Namensraum | Schlüssel je Sprache (pl = en = de) | Herkunft |
|---|---|---|
| `powietrze.*` | 82 | Vorschlag des Datenpakets Luft (`git mv` aus `docs/entscheidungen/D7_texte/`), erweitert um die Seite |
| `mieszkania.*` | 45 | Vorschlag des Datenpakets Wohnungsmarkt (Kopie aus `docs/entscheidungen/DW-texte/`, dort unverändert), erweitert |
| `klimat.*` | 54 | Vorschlag des Datenpakets Klima (`git mv` aus `docs/entscheidungen/dk/texte/`), erweitert; unbenutzte Schlüssel `klimat.anteil`, `klimat.gruen_je_ew`, `klimat.ebene.zelle` entfernt |

Ziffern in den Texten (gezählt mit `grep` über alle neun Dateien, ohne Schlüsselnamen): nur Kennungen und Namen
(`BDOT10k`, `PM10`, `PM2,5`, `XVIII/243/16`, `Dz.U. 2021 poz. 845, załącznik nr 1`, `CC BY 4.0`) und das Pandemiejahr
`2020` im Satz zu anderen Einflüssen, den `pruefen/D7_powietrze.py` verlangt (Protokoll des Datenpakets Luft).
Schwellen, Deckung, Mindestfallzahl, Gitterweite, Jahre, Fenster und Stichtage sind Platzhalter aus den Daten.
Geändert gegenüber den Vorschlägen: `powietrze.kennwert.pm10_dni`/`no2_godziny` (Schwelle `{prog}`),
`powietrze.niepelne` (`{min}`, `{pelne}`), `powietrze.stichtag` (`{data}`), `mieszkania.begriff_rcn` (ohne Datum).

## Prüfläufe

| Prüfung | Ergebnis |
|---|---|
| `skripte/30_seiten.py --pruefen` | 45 Seiten aktuell (15 × 3) |
| `pruefen/texte.py` | 0 Befunde (alle Schlüssel verwendet, gleiche Schlüssel und Platzhalter, keine deutschen Reste in pl/en, Falschsatz-Listen) |
| `pruefen/D7_powietrze.py`, `--selbsttest` | 0 Befunde (prüft seit diesem Zweig `texte/<lang>/powietrze.js`, auch die Kausalwendungen); Selbsttest 9 von 9 Verfälschungen erkannt |
| `pruefen/DW_mieszkania.py` | 0 Befunde (prüft weiter den Vorschlagsordner) |
| `pruefen/dk_klimat.py` | 0 Befunde |
| `pruefen/S3_themenseiten.mjs` | 54 Läufe (3 Seiten × 3 Sprachen × HTTP/file × 360/390/1280 px), 0 Befunde; je Lauf Überstand 0 px, keine Konsolen-/Seitenfehler, keine Fremdabrufe, Beispielkennzeichnung genau bei Beispieldaten, Grenzen sichtbar (Luft 7, Wohnungsmarkt 7, Klima 10 Punkte), Quellen sichtbar mit wörtlichem Vermerk der Daten (Luft 3, Wohnungsmarkt 2, Klima 3 Einträge), keine sichtbaren Schlüssel oder Platzhalter, keine Kausalwendung, je eine Zahl der Daten formatiert auf der Seite gefunden, Auswahlknöpfe auf Touch ≥ 44 px; axe-core 18 Läufe (HTTP, 390 und 1280 px) ohne Verstoß |
| `./pruefen.sh` (mit Browser) | siehe Abschnitt „Gesamtlauf“ |

## Nachbesserung nach dem Review (14.11.2026)

| Fund | Behebung | Beleg |
|---|---|---|
| Fensterbeschriftungen der Liniengrafik (Luft) bei 360/390 px übereinander, pl/en/de | `pruefen/S3_themenseiten.mjs` prüft jetzt in jeder Liniengrafik alle Textpaare auf Überdeckung und jeden Text auf Anschnitt, auf der Seite Luft auch nach jedem der 5 Kennwert-Knöpfe. Vor der Behebung (Commit `92ffe44`): 12 Befunde, genau Luft × pl/en/de × HTTP/file × 360/390 px. `themenseite.js` misst die Beschriftungen, hält sie an den Rändern und setzt bei Überdeckung die spätere eine Zeile höher (`a813cd5`) | Lauf auf `f91fa37`: 54 Läufe, 0 Befunde, 0 Beschriftungsbefunde, axe 18 Läufe ohne Verstoß; Bildschirmfotos pl 360, de 390, en 1280 px angesehen |
| Überschrift/Beschreibung Klima versprechen Hitze und gemessene Versiegelung; Beschreibung Luft „amtliche Messstationen“ neben „orientacyjnie“ | Datei des Gerüsts, als einzelner Commit `f91fa37` (nur drei Schlüssel je Sprache, Seiten neu erzeugt: je Sprache `index`, `klimat`, `powietrze`) zur Bestätigung durch die Integration | `30_seiten.py --pruefen` 45 Seiten aktuell, `pruefen/seiten.mjs` grün, `texte.py` 0 Befunde |
| „Stan —“ im Fuß | kein Mangel der Themenseiten: das Feld ist `<span data-kiez-version>`, der Auslieferungsstand, den `skripte/deploy_kopie.py` beim Deploy auf allen Seiten setzt (auch `index`); der Datenstand steht bei Klima in Grenzen und Quellen (`klimat.g.daty`, `klimat.zrodlo.stan`), bei Beispieldaten absichtlich nicht | `skripte/deploy_kopie.py` Zeile 71 und 218 |
| Zellenkarte Klima nicht per Tastatur | als Grenze geführt (unten) | – |
| Fallzahl n < 10 sichtbar (Wohnungsmarkt) | zur Bestätigung bei der Mindestfallzahlregel offen (`docs/entscheidungen/S3.md`, Vorschlag G) | – |

Weitere Läufe auf `f91fa37`: `texte.py`, `D7_powietrze.py`, `DW_mieszkania.py`, `dk_klimat.py`, `geruest.py`,
`hreflang.py` je 0 Befunde, `daten.py` 0 Abweichungen, `belege.py` 0 Befunde (3 Hinweise zum Einsammeln).

## Gesamtlauf

`./pruefen.sh` mit Browser auf Commit `6c28847` (sauberer Arbeitsstand): 45 Prüfungen, 38 grün, 0 mit Befund,
7 übersprungen (Gründe im Protokoll, keiner betrifft diese Seiten), darunter `pruefen/seiten.mjs` (alle Seiten in
pl, en, de, axe, 360 px) und `pruefen/texte.py`. Protokoll: [`belege/S3_pruefen-6c28847.log`](S3_pruefen-6c28847.log).
Der Lauf davor (Commit `442276b`) hatte einen Befund in `pruefen/geruest.py`: Entscheidungskennungen (KR20, KR22,
KR23) in Kommentaren von `seite_*.js`; behoben in `6c28847`. `pruefen/S3_themenseiten.mjs` ist noch kein Schritt
von `pruefen.sh` (Vorschlag an die Belegschicht).

Nach der Nachbesserung: `./pruefen.sh` mit Browser auf Commit `45dd18f` (sauberer Arbeitsstand, unter
`systemd-run --user --scope -p MemoryMax=8G`): 45 Prüfungen, 38 grün, 0 mit Befund, 7 übersprungen. Protokoll:
[`belege/S3_pruefen-45dd18f.log`](S3_pruefen-45dd18f.log). `pruefen/S3_themenseiten.mjs` separat auf `f91fa37`
(seither nur Beleg-Dateien geändert): 54 Läufe, 0 Befunde.

## Grenzen

- Die Kartenfläche der Seite Klima zeigt im kopflosen Prüfbrowser nur einen Ausschnitt (gleiches Bild auf der
  bestehenden Seite `karta`); am echten Gerät nicht angesehen. Bedienung am Handy nimmt Andre ab.
- Ein Quadrat der Zellenkarte (Klima) lässt sich nur mit Maus oder Touch wählen, nicht per Tastatur; die Werte der
  dzielnice und delegatury stehen als Tabelle bereit, die der einzelnen Quadrate nicht. Nach „Maß halten“ bei
  WCAG 2.1 AA vertretbar, Tastaturbedienung der Zellen erst mit Bedarf.
- Die Prüfung der Beschriftungen deckt die Grenzwert-Beschriftungen nur für die heutigen Daten ab; mit echten
  EEA-Werten erneut laufen lassen.
- Polnische und englische Texte nicht von Muttersprachlern gegengelesen (Glossar Status „Vorschlag“).
- Der Langtext je Seite (`{{block:…}}`) gehört dem Paket Langtexte; bis dahin steht dort der Satz „w przygotowaniu“.
