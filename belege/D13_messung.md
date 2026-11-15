# Messung: Startgewicht des Planers mit verkleinerter Auslieferung

Stand 13.11.2026. Beleg für die Auflage aus KR10 (`docs/entscheidungen.md`): Die Auslieferung verkleinert
JavaScript, damit das Startgewicht des Planers live unter 320 KB gz bleibt.

## Was gemessen wurde und warum so

Der Krakauer Planer lädt heute nur den Seitenrahmen. Die Grundkarte fehlt, darum bindet die Seite `planer.js` und
MapLibre noch nicht ein (siehe `docs/rundgang.md`, „Übergabe an die Pakete“). Eine Messung daran wäre trivial grün
und würde nichts zeigen. Gemessen wurde deshalb der Aufbau, an dem KR10 entstanden ist: der Potsdamer Planer mit
echten Potsdamer Daten, einmal unverändert und einmal mit dem umgebauten Code dieses Repos (Textschicht,
Ortskonfiguration). Beide Wurzeln baut `pruefen/gegenprobe_potsdam.sh`. Die dritte Messung ist dieselbe umgebaute
Wurzel, deren eigenes JavaScript so verkleinert ausgeliefert wird, wie `skripte/deploy_kopie.py` es tut.

- Potsdam: `kiezatlas-potsdam` `7b6eb08` (`git archive HEAD`), echte Daten
- umgebauter Code: JavaScript dieses Repos, unverändert seit `f3cbc06`; Messwerkzeug ab `360d2db`
- esbuild 0.25.12 (genau, Hash in `package-lock.json`), Einstellungen: `minify`, `legalComments: inline`, kein
  Bündeln, kein Modulformat. Verkleinert werden nur `*.js` der Wurzel und `texte/**/*.js`, nicht `daten/`,
  `vendor/` und `fonts/`.
- Node 22.23.4, Playwright 1.64.1 (Chromium aus `~/.cache/ms-playwright`), kein Netz: fremde Adressen beantwortet
  der Prüfbrowser leer (4 Abrufe je Lauf, die Grundkarte von basemap.de)

Rechenweg: alle JavaScript-Dateien, die `planer.html` bis zur Ruhe lädt (`load`, `KIEZ_BEREIT`, keine offenen
Abrufe), je Datei einmal.

- **gz9** = gzip -9 je Datei, summiert. So rechnet die Potsdamer Prüfung `A7_planer.mjs`; sie rundet auf KB.
- **live** = gzip Stufe 9 ab 1024 Byte, kleinere Dateien ungepackt. So liefert nginx mit dem Vorschlag in
  `docs/auslieferung.md` aus (`gzip_comp_level 9` für `/kiezatlas/krakow/`).
- **heute** = gzip Stufe 6 ab 1024 Byte, die heutige Einstellung für `/kiezatlas/` (nginx-Konfiguration vom
  07.11.2026).

## Aufruf

```sh
mkdir -p "$S/gp"
GEGENPROBE_BEHALTEN=1 TMPDIR="$S/gp" pruefen/gegenprobe_potsdam.sh --ohne-browser   # baut basis/ und umgebaut/
G="$S/gp/kiezatlas-gegenprobe.<zufall>"
node skripte/deploy_pruefen.mjs --gewicht "$G/basis"    --seite planer.html
node skripte/deploy_pruefen.mjs --gewicht "$G/umgebaut" --seite planer.html
node skripte/deploy_pruefen.mjs --gewicht "$G/umgebaut" --seite planer.html --verkleinert
```

Jeder Lauf ging unter `systemd-run --user --scope -p MemoryMax=6G`. Die Gegenprobe ohne Browser meldete dabei
0 Abweichungen (A6, A8 wie Potsdam).

## Ergebnis

| Wurzel | JS-Dateien | gz9 | live (Stufe 9) | heute (Stufe 6) | ungepackt |
|---|---|---|---|---|---|
| Potsdam unverändert | 8 | 327.942 B (320,3 KB) | 327.942 B | 332.929 B (325,1 KB) | 1.532.553 B |
| umgebaut, unverkleinert | 11 | 330.872 B (323,1 KB) | 330.872 B | 335.855 B (328,0 KB) | 1.537.710 B |
| **umgebaut, verkleinert** | 11 | **323.941 B (316,3 KB)** | **323.941 B (316,3 KB)** | 328.852 B (321,1 KB) | 1.513.084 B |

Grenze: 320 KB = 327.680 B.

Das Messwerkzeug stimmt mit der Potsdamer Prüfung überein: `A7_planer.mjs` meldete für dieselben Wurzeln 320 KB
und 323 KB (`docs/rundgang.md`, „Ergebnis der Gegenprobe“).

Verkleinert lädt der Planer ohne Seitenfehler und ohne Konsolenfehler bis `KIEZ_BEREIT`. Die verkleinerten Skripte
teilen sich also weiter ihre Namen auf oberster Ebene.

Je Datei (umgebaut, verkleinert; Byte ungepackt vorher → nachher, gz9, Stufe 6):

| Datei | vorher | nachher | gz9 | Stufe 6 |
|---|---|---|---|---|
| `daten/ort.js` | 3.633 | 3.633 (nicht verkleinert) | 1.558 | 1.577 |
| `i18n.js` | 2.308 | 1.382 | 710 | 706 |
| `texte/de/kern.js` | 1.713 | 1.496 | 761 | 763 |
| `kopf.js` | 4.140 | 2.141 | 1.018 | 1.011 |
| `themen.js` | 10.464 | 6.051 | 2.769 | 2.791 |
| `planer.js` | 55.032 | 37.961 | 13.132 | 13.192 |
| `daten/planungsraeume.js` | 48.077 | gleich | 11.680 | 12.251 |
| `daten/stadtteile.js` | 196.878 | gleich | 47.752 | 49.133 |
| `daten/grundkarte.js` | 204.735 | gleich | 16.144 | 16.369 |
| `vendor/maplibre-gl.js` | 803.086 | gleich | 211.733 | 213.785 |
| `daten/einrichtungen.js` | 207.644 | gleich | 16.684 | 17.274 |

## Bewertung

- **Erfüllt mit gzip Stufe 9:** Verkleinert sind es 316,3 KB, also 3,7 KB unter der Grenze. Die Mehrlast der
  Textschicht (2,9 KB) ist mehr als ausgeglichen; der umgebaute Planer ist 4,0 KB leichter als Potsdam unverändert.
- **Nicht erfüllt mit der heutigen Stufe 6:** 321,1 KB. Schon Potsdam unverändert liegt dort bei 325,1 KB. Die
  320-KB-Grenze aus `A7_planer.mjs` ist gzip -9 gerechnet und wird heute mit Stufe 6 nicht eingehalten (Potsdam
  unverändert 325,1 KB). Der
  Unterschied kommt fast ganz aus den großen Daten- und Bibliotheksdateien (MapLibre 2,0 KB, Stadtteile 1,3 KB),
  nicht aus dem eigenen Code. Darum schlägt `docs/auslieferung.md` für `/kiezatlas/krakow/` `gzip_comp_level 9`
  vor. Bei Dateien dieser Größe kostet das den Server kaum Rechenzeit, und Potsdam bleibt unberührt.
- **Grenzen der Messung:** Gemessen ist ein Stellvertreter: Potsdamer Daten, deutscher Text. Der Krakauer Planer
  bekommt seine eigene Grenze, sobald er Daten hat (Paket Seiten Kamienice und Planer). Live gemessen ist noch
  nichts, weil es keinen Upload gibt. Die Messung nach dem Upload steht in `docs/auslieferung.md`, Abschnitt
  „Abnahme nach dem Upload“.

## Deploy-Kopie Kraków auf Beispieldaten

`skripte/deploy_kopie.py --mit-beispieldaten` gefolgt von `skripte/deploy_pruefen.mjs --kopie …`, Stand `360d2db`,
grün. 85 Dateien, 45 Seiten (15 je Sprache), 15 Dateien eigenes JavaScript verkleinert (257.741 → 174.719 Byte,
gzip -9 86.547 → 64.552 Byte). Jede verkleinerte Datei ist genau die Ausgabe von esbuild für ihre Quelle.

| Sprache | Planer JS gz9 | Startseite, alles, live |
|---|---|---|
| pl | 6.751 B | 110.765 B (108,2 KB) |
| en | 6.574 B | 110.560 B (108,0 KB) |
| de | 6.586 B | 110.572 B (108,0 KB) |

Grenzen: Planer 320 KB, Startseite 300 KB je Sprache (Bauvorlage). Diese Werte sind klein, weil die Seiten noch
ohne Karte laufen. Sie zeigen nur, dass die Messung über alle drei Sprachen läuft.

## Schutz des Ablageorts

Stand `30e4f9d`, Deploy-Wurzel im Wegwerf-Ordner (`--deploy-wurzel "$S/dw"`), darin zum Schein ein Potsdamer
Stand `kiezatlas-deploy/2026-11-07/`, ein fremder Ordner `krakow/fremd/` und ein Ordner `krakow/potsdamartig/` mit
einer `MD5SUMS` ohne Sprachseiten. `deploy_kopie.py --ziel …` lehnte alle acht Fehlziele mit Rückgabe 1 ab, und
alle drei Ordner blieben unverändert:

| `--ziel` | Meldung |
|---|---|
| `$S/irgendwo` | Ziel muss direkt unter `…/kiezatlas-deploy/krakow/` liegen |
| `…/kiezatlas-deploy/2026-11-07` | dito |
| `…/kiezatlas-deploy/krakow` | dito |
| `…/kiezatlas-deploy/krakow/x/y` | dito |
| `…/kiezatlas-deploy/krakow/../2026-11-07` | dito (aufgelöst) |
| `.` (das Repo) | dito |
| `…/krakow/fremd` | nicht leer und keine frühere Deploy-Kopie (MD5SUMS fehlt) |
| `…/krakow/potsdamartig` | MD5SUMS beschreibt keine Kraków-Kopie |

Ohne `--mit-beispieldaten` brach das Skript auf den Beispieldaten mit Rückgabe 1 ab und nannte die drei Dateien.
Ein zweiter Lauf auf dieselbe Kraków-Kopie ersetzte sie wie vorgesehen.
