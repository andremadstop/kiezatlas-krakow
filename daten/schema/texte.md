# Vertrag: Textschicht (`i18n.js`, `texte/<lang>/*.js`)

Eingefroren mit dem Gerüst. Änderungen nur als Vertragsänderung über die Integration, nie in einem Paket.

## Sprachen und Ablage

- Sprachen: `pl` (Standard, Wurzelordner), `en` (Ordner `en/`), `de` (Ordner `de/`). Die Liste steht in
  `config/krakow.yaml` (`sprachen`); die erste ist die Standardsprache.
- Die Seitensprache steht in `<html lang>`. `i18n.js` liest sie; fehlt sie oder ist sie unbekannt, gilt `pl`.
- Kurze Texte liegen in `texte/<lang>/<namensraum>.js`, lange Texte (Methode, Daten, Erzählung) als fertiges
  HTML in `texte/<lang>/bloecke/<seite>.html` und werden vom Seitengenerator `skripte/30_seiten.py` eingesetzt.
- Daten (`daten/*.js`) sind sprachneutral: Sie tragen Schlüssel und Zahlen, keine Sätze.

## Ladereihenfolge auf jeder Seite

```html
<script src="daten/ort.js"></script>          <!-- window.KIEZ_ORT, erzeugt von skripte/31_ort.py -->
<script src="i18n.js"></script>               <!-- window.KIEZ_I18N, window.KIEZ_LANG -->
<script src="texte/pl/kern.js"></script>      <!-- je Namensraum eine Datei, Sprache der Seite -->
<script src="kopf.js"></script>               <!-- danach die Seitenmodule (themen.js, atlas.js …) -->
```

In den Sprachordnern stehen dieselben Verweise mit `../` davor; das setzt der Seitengenerator.

## Wie eine Textdatei sich einträgt

```js
/* texte/pl/planer.js: Namensraum planer.* */
(function (T) {
  T["planer.titel"] = "Planer";
  T["planer.einrichtungen"] = { one: "{n} placówka", few: "{n} placówki", many: "{n} placówek", other: "{n} placówki" };
})(window.KIEZ_TEXTE = window.KIEZ_TEXTE || {});
```

- Jede Datei hängt **nur Schlüssel ihres eigenen Namensraums** an: `texte/<lang>/<ns>.js` enthält nur
  `"<ns>.…"`. `pruefen/texte.py` prüft das; so fassen parallele Pakete nie dieselbe Datei an.
- Schlüssel: `<namensraum>.<name>`, Name aus Kleinbuchstaben, Ziffern und `_`, Punkt für Unterteilung.
- Werte: Zeichenkette mit benannten Platzhaltern `{name}`, oder Pluralobjekt mit den Formen von
  `Intl.PluralRules` der Sprache (`pl`: `one`, `few`, `many`, `other`; `en`/`de`: `one`, `other`). Im
  Pluraltext steht die Zahl als `{n}`; `t()` formatiert sie nach Landesbrauch.
- Ausnahme Objektwert ohne Plural: `kern.karte_locale` (Bedientexte für MapLibre, Schlüssel wie in MapLibre).

## Namensräume und Eigentum

| Namensraum | Datei | Eigentümer |
|---|---|---|
| `kern.*` | `texte/<lang>/kern.js` | Gerüst legt an, danach Paket Oberflächen-Texte |
| `seiten.*` | `texte/<lang>/seiten.js` | Gerüst (Titel, Beschreibungen, Navigation der Seiten; vom Seitengenerator gelesen) |
| `karte.*` | `texte/<lang>/karte.js` | Paket Oberflächen-Texte |
| `erzaehlung.*` | `texte/<lang>/erzaehlung.js` | Paket Seiten Erzählung, Karte, Steckbrief, Vergleich |
| `kamienice.*` | `texte/<lang>/kamienice.js` | Paket Seiten Planer, Denkmale und Sanierungsatlas (seit 14.11.2026, KR41) |
| `planer.*` | `texte/<lang>/planer.js` | Paket Seiten Planer, Denkmale und Sanierungsatlas; die Potsdamer Schlüssel bleiben für die Gegenprobe (KR36) |
| `klimat.*`, `powietrze.*`, `mieszkania.*` | je eigene Datei | Paket Themenseiten Luft, Wohnungsmarkt, Klima (seit 14.11.2026 unter `texte/`, KR14, KR43) |
| `punktualnosc.*` | eigene Datei | Paket der Themenseite Pünktlichkeit (noch keine Datei) |
| `sanierung.*` | `texte/<lang>/sanierung.js` | Paket Seiten Planer, Denkmale und Sanierungsatlas (Seite `modernizacja`; von der Integration übernommen am 14.11.2026, KR41) |
| `bevoelkerung.*` | `texte/<lang>/bevoelkerung.js` | Paket Gliederung und Bevölkerung (bis Phase Seitenbau als Vorschlag unter `docs/entscheidungen/D4/texte/`, KR14) |
| `gebaeude.*` | `texte/<lang>/gebaeude.js` | Paket Gebäude und 3D (bis Phase Seitenbau unter `docs/entscheidungen/D5/texte/`, KR14) |
| `denkmale.*` | `texte/<lang>/denkmale.js` | Paket Seiten Planer, Denkmale und Sanierungsatlas (seit 14.11.2026 unter `texte/`, mit der Seite `kamienice` verschoben, KR14, KR41) |
| `fussweg.*` | `texte/<lang>/fussweg.js` | Paket OSM und Fußwegnetz (noch keine Datei, KR14) |

Neue Namensräume nur über die Integration (Eigentümer-Tabelle in `docs/rundgang.md`, Abschnitt „Bau“).

## Schnittstelle `window.KIEZ_I18N`

| Aufruf | Ergebnis |
|---|---|
| `t(schluessel, werte)` | Text mit eingesetzten Platzhaltern. Fehlt der Schlüssel, kommt der Schlüssel selbst zurück (sichtbar, `pruefen/seiten.mjs` findet ihn). Pluraltext: Zahl in `werte.n`. |
| `fmt.nf(optionen)` | `Intl.NumberFormat` der Seitensprache, zwischengespeichert |
| `fmt.zahl(x, stellen)` | Zahl, mit festen Nachkommastellen, wenn `stellen` angegeben ist |
| `fmt.anteil(x, stellen)` | Prozentwert (`x` = 0 … 100) nach Landesbrauch, Standard eine Nachkommastelle |
| `fmt.datum(d, optionen)` | Datum (`toLocaleDateString` der Seitensprache) |
| `fmt.zeit(d, optionen)` | Datum und Uhrzeit (`toLocaleString` der Seitensprache) |
| `plural(n)` | Pluralform (`one`, `few`, `many`, `other`) |
| `karteLocale()` | Bedientexte für MapLibre (`kern.karte_locale`) |
| `lang`, `locale` | `pl` / `pl-PL`, `en` / `en-GB`, `de` / `de-DE` |
| `sprachwert(v)` | Wert aus `daten/ort.js` in der Seitensprache: Objekt `{pl, en, de}` → `v[lang]` (fehlt die Sprache: Standardsprache des Orts), Zeichenkette unverändert |
| `ort(feld)` | `sprachwert(KIEZ_ORT[feld])`, z. B. `ort("stadt")` → „Kraków“ / „Krakau“ |

`i18n.js` arbeitet ohne `fetch` und ohne Build zur Laufzeit und läuft auch per `file://`. `window.KIEZ_LANG` trägt
dieselbe Sprache wie `lang`. Zahlen und Daten nie selbst formatieren, immer über `fmt`. Achtung: `pl-PL` gruppiert vierstellige Zahlen
nicht und trennt Tausender mit geschütztem Leerzeichen; Prüfungen dürfen nicht auf ein Tausenderzeichen setzen.

## Was nicht übersetzt wird

Lizenzvermerke bleiben wörtlich in der Originalsprache (meist polnisch) und werden höchstens erläutert.
Eigennamen (Namen der dzielnice, Quellen, Behörden) bleiben polnisch.
