# Behebung Bereich Oberfläche (14.11.2026): Vorschläge an die Integration

Stand: Vorschlag. Die Funde aus der Durchsicht der Oberfläche sind auf dem Zweig `Arbeitszweig fix-oberflaeche` behoben,
je Fund ein Commit. Einige Eingriffe berühren Dateien anderer Eigentümer (`docs/rundgang.md`, Abschnitt „Bau“).
Sie stehen hier zur Bestätigung.

## 1. Schwelle der Gitteranteile aus der Ortskonfiguration (Gerüst, Vertrag `ort.json`, `themen.md`)

- **Anlass:** `zellen_odbl.js` setzt `q_u15` und `q_65p` unter 100 Personen auf `null` (Mindestfallzahl aus
  `skripte/raum_bevoelkerung.py`). `themen.js` graute nur unter 10 Personen aus. MapLibre zeichnete `null` in der
  Stufenregel schwarz, betroffen waren 32 Zellen mit 10 bis 99 Einwohnern.
- **Eingriff:**
  - `farbe()`, `hoehe()` und `unscharf()` prüfen zusätzlich auf einen fehlenden Wert.
  - Neues optionales Feld `themen[].mindestfallzahl` in `config/krakow.yaml`, `daten/schema/ort.json` und
    `skripte/31_ort.py`. Fehlt es, gilt 10 wie bisher in Potsdam.
  - Die Legende `erzaehlung.leg_grau_gitter` nennt die Schwelle als `{n}`.
- **Unverändert:** Die Potsdamer Schlüssel `karte.grau_personen` und `karte.grafik.unscharf_personen` (nur
  `atlas.js`, `karte.js`, `schaugrafik.js`, KR36). Dort stimmt die Schwelle 10.

## 2. Fehlender Langtext-Block bleibt leer, `in_vorbereitung` (Gerüst, `skripte/30_seiten.py`)

- **Anlass:** Fehlte ein Block, setzte `30_seiten.py` den Satz `kern.in_arbeit` ein. Dadurch endeten sieben Seiten
  je Sprache mit „Ta część atlasu jest w przygotowaniu“.
- **Eingriff:**
  - Ein fehlender Block erzeugt nichts mehr.
  - Neuer Schlüssel `in_vorbereitung` in `config/krakow.yaml` (heute `[punktualnosc]`): Die Seite bleibt
    erreichbar, steht aber nicht in `{{liste:themenseiten}}`.
  - `vorlagen/punktualnosc.html` ist `noindex` und setzt den Hinweis ausdrücklich.
- **Neu prüfen, wenn:** Das Paket Pünktlichkeit vergeben ist und Daten liefert. Dann `punktualnosc` aus
  `in_vorbereitung` nehmen.

## 3. Polnischer Begriff für die vier Gruppen (Glossar, `config/krakow.yaml`)

- Die Gruppe heißt im Polnischen jetzt einheitlich „delegatura (dawna dzielnica)“, nicht „dzielnica historyczna“.
  Der Begriff gilt auch für `gliederung.gruppe` in `config/krakow.yaml`.
- Englisch und Deutsch bleiben unverändert.
- Der Eintrag steht in `docs/glossar-pl.md` als Vorschlag und unter „Zur Prüfung zuerst“. Ob „dawna dzielnica
  (1973–1990)“ besser passt, soll der Lehrstuhl entscheiden. Die Jahreszahlen stammen aus Sprachwissen und sind
  nicht belegt, deshalb stehen sie nicht im Text.

## 4. Takt: neutrale Benennung (Glossar)

- „przystanek z częstymi odjazdami / z częstym kursowaniem“ ist ersetzt durch „przystanek klasy I lub II“ bzw. „z co
  najmniej dwoma odjazdami na godzinę“. Die Schwelle steht in `config/richtwerte.yaml` unter `taktklassen.II`.
- Die Schlüssel `sanierung.bezug_text` und `sanierung.link_takt` gehören dem Paket Seiten Planer, Denkmale und
  Sanierungsatlas. Sie sind zur Einheitlichkeit mit angepasst.
- Der Begriff steht im Glossar zur Prüfung.

## 5. Prüfungen

- `pruefen/S1_seiten.mjs`:
  - Zählt MapLibre-Warnungen „found null / Expected value to be of type“ als Fehler.
  - Prüft, dass die Kartenebene `zabytki` nur Objekte mit `h === true` zeigt und die Legende ihre Zahl nennt.
- `pruefen/d3_falschsaetze.json`: Die 3D-Regel ist umgedreht. Befund ist jetzt ein Text, der 3D als „noch nicht
  veröffentlicht“ oder „folgt“ beschreibt (Stand KR42).
