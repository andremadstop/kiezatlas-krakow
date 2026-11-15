#!/bin/sh
# Gegenprobe Potsdam: Der umgebaute Code (Textschicht, Ortskonfiguration, Zahlenformate, Rechen-SRID als Parameter,
# neutrale Feldnamen) muss mit den Potsdamer Daten und Seiten genau das zeigen, was der Potsdamer Stand zeigt.
#
# Ablauf (nur lesend gegenüber kiezatlas-potsdam, nichts davon landet im Kraków-Repo):
#   1. Zwei Prüfwurzeln in einem Wegwerf-Ordner, beide aus `git archive HEAD` von kiezatlas-potsdam:
#        basis/     unverändert (Vergleichsstand)
#        umgebaut/  dieselben Seiten und Daten, aber JavaScript, Stylesheets, skripte/ und pruefen/*.py aus diesem Repo
#   2. Mechanische Anpassung von umgebaut/, beides hier dokumentiert und sonst nichts:
#        a) Ortskonfiguration: daten/ort.js aus pruefen/gegenprobe_potsdam/ort.yaml (skripte/31_ort.py) und
#           texte/de/*.js aus diesem Repo; in jede Seite vor dem ersten <script defer src=…> eingefügt:
#           <script defer src="daten/ort.js"></script><script defer src="i18n.js"></script> und je Namensraum
#           <script defer src="texte/de/<ns>.js"></script>, und zwar genau die Namensräume, die die entsprechende
#           Kraków-Vorlage in ihrer Kopfzeile „texte:“ lädt (SEITEN unten: index → index, karte → karta,
#           planer → planer, planer-methode → planer-metoda, planer-daten → planer-dane, 404 → 404). Die Bauzeiten-
#           Seiten (jahre*) haben in Kraków keine Entsprechung (entfallen); sie bekommen nur kern, den themen.js braucht.
#        b) Feldnamen der Daten: in_potsdam → in_stadt (Vertrag daten/schema/einrichtungen.json, kennzahlen.json),
#           in daten/**/*.js und daten/**/*.json, in den CSV-Köpfen unter daten/export/ und als Spaltenname in den
#           GeoPackages unter daten/export/ (sqlite3 ALTER TABLE … RENAME COLUMN).
#   3. In beiden Wurzeln dieselben Prüfungen: die unveränderten Potsdamer Browserprüfungen pruefen/seiten.mjs,
#      pruefen/A7_planer.mjs, pruefen/B5_jahre.mjs, die Codepfad-Prüfungen pruefen/A6_test_pfade.py und
#      pruefen/A8_test_pfade.py sowie ein Textabzug aller Seiten (pruefen/gegenprobe_text.mjs: sichtbarer Text nach
#      dem Laden, file://). Grün heißt: gleiche Rückgabe, gleiche Zahl an „ok“, gleiche „FEHLT“-Zeilen, gleicher Text.
#      Einzige zugelassene Abweichung: Ausnahme KR10 beim Startgewicht des Planers (Bedingungen bei ausnahme_gewicht).
#
# Aufruf:  pruefen/gegenprobe_potsdam.sh [--ohne-browser]
#   KIEZ_POTSDAM   Pfad zu kiezatlas-potsdam (Standard ../kiezatlas-potsdam)
#   GEGENPROBE_BEHALTEN=1  Wegwerf-Ordner nicht löschen (zum Nachsehen)
# Rückgabe 0 = ohne Abweichung, 1 = Abweichung, 2 = Potsdam-Repo fehlt (pruefen.sh zählt das als übersprungen).
# Kein Netz (Fremdabrufe beantworten die Prüfungen selbst), keine Datenbank. Dauer: rund zehn Minuten mit Browser.
set -u
HIER="$(cd "$(dirname "$0")/.." && pwd)"
POTSDAM="${KIEZ_POTSDAM:-$(cd "$HIER/.." && pwd)/kiezatlas-potsdam}"
BROWSER=1
[ "${1:-}" = "--ohne-browser" ] && BROWSER=0
if [ ! -f "$POTSDAM/pruefen/seiten.mjs" ] || ! git -C "$POTSDAM" rev-parse HEAD >/dev/null 2>&1; then
  echo "kiezatlas-potsdam nicht gefunden unter $POTSDAM (KIEZ_POTSDAM setzen)"; exit 2
fi
UV="uv run -q --offline --python 3.13 --no-project --with-requirements $HIER/requirements.txt"
W="$(mktemp -d "${TMPDIR:-/tmp}/kiezatlas-gegenprobe.XXXXXX")"
[ "${GEGENPROBE_BEHALTEN:-0}" = "1" ] || trap 'rm -rf "$W"' EXIT INT TERM
echo "Gegenprobe Potsdam: $(git -C "$POTSDAM" describe --always --dirty) gegen $(git -C "$HIER" describe --always --dirty)"
echo "Wegwerf-Ordner: $W"

for r in basis umgebaut; do
  mkdir -p "$W/$r" && git -C "$POTSDAM" archive HEAD | tar -x -C "$W/$r" || exit 1
done
ln -s "$POTSDAM/node_modules" "$W/basis/node_modules"
ln -s "$HIER/node_modules" "$W/umgebaut/node_modules"

# --- umgebaut: Code aus diesem Repo
U="$W/umgebaut"
cp "$HIER"/*.js "$HIER"/*.css "$U/" || exit 1
rm -rf "$U/skripte" && cp -r "$HIER/skripte" "$U/skripte"
cp "$HIER"/pruefen/*.py "$U/pruefen/"
mkdir -p "$U/pruefen/gegenprobe_potsdam" "$U/texte/de"
cp "$HIER/pruefen/gegenprobe_potsdam/ort.yaml" "$U/pruefen/gegenprobe_potsdam/ort.yaml"
cp "$HIER"/texte/de/*.js "$U/texte/de/"
export KIEZ_CONFIG="$U/pruefen/gegenprobe_potsdam/ort.yaml"   # Potsdamer Ort; richtwerte → $U/config/richtwerte.yaml (Potsdam)
$UV python -I "$U/skripte/31_ort.py" --aus "$U/daten/ort.js" || exit 1
$UV python -I - "$U" "$HIER" "$W" <<'PY' || exit 1
import re, sqlite3, sys
from pathlib import Path
u, hier, w = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
SEITEN = {"index": "index", "karte": "karta", "planer": "planer", "planer-methode": "planer-metoda",
          "planer-daten": "planer-dane", "404": "404"}
def schicht(seite):
    v = SEITEN.get(seite)
    if v is None:
        ns = ["kern"]
    else:
        kopf = (hier / "vorlagen" / f"{v}.html").read_text(encoding="utf-8").split("-->", 1)[0]
        ns = re.search(r"^texte:\s*(.*)$", kopf, re.M).group(1).split()
    return ["daten/ort.js", "i18n.js"] + [f"texte/de/{n}.js" for n in ns]
n_seiten = 0
for p in sorted(u.glob("*.html")):
    t = p.read_text(encoding="utf-8")
    m = re.search(r'<script defer src="', t)
    if m:
        ein = "".join(f'<script defer src="{s}"></script>' for s in schicht(p.stem))
        p.write_text(t[:m.start()] + ein + t[m.start():], encoding="utf-8"); n_seiten += 1
(w / "schicht_planer.txt").write_text("\n".join(schicht("planer")) + "\n", encoding="utf-8")
print("Textschicht je Seite: " + "; ".join(f"{s}: {' '.join(x.split('/')[-1] for x in schicht(s)[2:])}" for s in [*SEITEN, "jahre"]))
n_daten = 0
for p in sorted([*(u / "daten").rglob("*.js"), *(u / "daten").rglob("*.json"), *(u / "daten" / "export").rglob("*.csv")]):
    t = p.read_text(encoding="utf-8")
    if "in_potsdam" in t:
        p.write_text(t.replace("in_potsdam", "in_stadt"), encoding="utf-8"); n_daten += 1
n_spalten = 0
for p in sorted((u / "daten" / "export").glob("*.gpkg")):
    db = sqlite3.connect(p)
    for (tab,) in db.execute("SELECT table_name FROM gpkg_contents").fetchall():
        if any(c[1] == "in_potsdam" for c in db.execute(f'PRAGMA table_info("{tab}")')):
            db.execute(f'ALTER TABLE "{tab}" RENAME COLUMN in_potsdam TO in_stadt'); n_spalten += 1
    db.commit(); db.close()
print(f"Anpassung: Skriptzeile in {n_seiten} Seiten, in_potsdam → in_stadt in {n_daten} Dateien und {n_spalten} GeoPackage-Tabellen")
PY

abw=0
# Ausnahme KR10 (docs/entscheidungen.md): Potsdams Grenze von 320 KB gz für das Startgewicht des Planers ist ein
# Leistungsbudget der Potsdamer Auslieferung mit wenigen hundert Byte Luft. Die Textschicht (daten/ort.js, i18n.js und
# die Textdateien laut Kopfzeile der Kraków-Vorlage planer, Liste in schicht_planer.txt) wird für Potsdam nie ausgeliefert. Die Abweichung zählt nur dann nicht,
# wenn alles Folgende aus den Dateien und Logs nachgerechnet stimmt (gzip -9 wie A7_planer.mjs, keine gerundeten Werte):
#   1. Abweichend sind nur Prüfungen „Startgewicht … mit echten Daten“: Rückgabe Potsdam 0, umgebaut 1, jede
#      zusätzliche FEHLT-Zeile ist eine solche, alle übrigen ok- und FEHLT-Zeilen sind gleich.
#   2. planer.html lädt im umgebauten Stand genau die Dateien der Textschicht zusätzlich (Skriptzeilen), und die
#      Fixture-Läufe laden dieselben Dateien wie Potsdam plus genau diese (Liste „geladen:“).
#   3. Der gemeinsame Code, den planer.html lädt (kopf.js, themen.js, planer.js), ist zusammen nicht schwerer als in
#      Potsdam. Damit ist der Mehrbetrag höchstens das Gewicht der Textschicht; beide Werte werden ausgegeben.
ausnahme_gewicht() {  # Log basis, Log umgebaut, rc basis, rc umgebaut
  $UV python -I - "$W" "$1" "$2" "$3" "$4" <<'PY'
import gzip, re, sys
from pathlib import Path
w, lb, lu = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
rb, ru = sys.argv[4], sys.argv[5]
b, u = lb.read_text(encoding="utf-8").splitlines(), lu.read_text(encoding="utf-8").splitlines()
SCHICHT = (w / "schicht_planer.txt").read_text(encoding="utf-8").split()
GEWICHT = re.compile(r"^\s*FEHLT\s+Startgewicht [\d.,]+ KB gz JS mit echten Daten \(Grenze [\d.,]+\)\s*$")
norm = lambda z: re.sub(r"[0-9][0-9.,]*", "", z)
grund = []
if (rb, ru) != ("0", "1"):
    grund.append(f"Rückgabe {rb}/{ru} statt 0/1")
ok_b = sum(1 for z in b if re.match(r"^\s*ok", z))
ok_u = sum(1 for z in u if re.match(r"^\s*ok", z))
fehlt_b = sorted(norm(z) for z in b if "FEHLT" in z)
fehlt_u = [z for z in u if "FEHLT" in z]
gewicht = [z for z in fehlt_u if GEWICHT.match(z)]
rest_u = sorted(norm(z) for z in fehlt_u if not GEWICHT.match(z))
if not gewicht or rest_u != fehlt_b or ok_u + len(gewicht) != ok_b:
    grund.append(f"abweichend ist nicht nur das Startgewicht mit echten Daten ({len(gewicht)} Gewichtszeilen, ok {ok_b}/{ok_u})")
def skripte(r):
    return re.findall(r'<script[^>]*\bsrc="([^"]+)"', (w / r / "planer.html").read_text(encoding="utf-8"))
sb, su = skripte("basis"), skripte("umgebaut")
if [s for s in su if s not in sb] != SCHICHT or [s for s in su if s in sb] != sb:
    grund.append(f"Skriptzeilen in planer.html: zusätzlich {[s for s in su if s not in sb]}")
def geladen(zeilen):
    return [sorted(x.split("/")[-1] for x in z.split("geladen: ", 1)[1].split(", ")) for z in zeilen if "geladen: " in z]
gb, gu = geladen(b), geladen(u)
extra = [s.split("/")[-1] for s in SCHICHT]
if not gb or len(gb) != len(gu) or any(y != sorted(x + extra) for x, y in zip(gb, gu)):
    grund.append("die Fixture-Läufe laden nicht genau Potsdams Dateien plus die Textschicht")
gz = lambda p: len(gzip.compress(p.read_bytes(), compresslevel=9))
code = [s for s in sb if "/" not in s]
code_b = sum(gz(w / "basis" / s) for s in code)
code_u = sum(gz(w / "umgebaut" / s) for s in code)
schicht = sum(gz(w / "umgebaut" / s) for s in SCHICHT)
if code_u > code_b:
    grund.append(f"gemeinsamer Code mit {code_u} B gz schwerer als Potsdam ({code_b} B gz)")
if grund:
    print("  (Ausnahme KR10 greift nicht: " + "; ".join(grund) + ")")
    sys.exit(1)
werte = ", ".join(re.search(r"Startgewicht ([\d.,]+) KB", z).group(1) for z in gewicht)
print(f"  ok    A7_planer: Ausnahme KR10 (Startgewicht), Rückgabe {ru}, {ok_u} × ok; gleich wie Potsdam bis auf "
      f"{len(gewicht)} × „Startgewicht mit echten Daten“ ({werte} KB gz, Grenze Potsdam 320). Gemeinsamer Code "
      f"({', '.join(code)}) {code_u} B gz gegen Potsdam {code_b} B gz ({code_u - code_b:+d} B), "
      f"Textschicht ({', '.join(SCHICHT)}) {schicht} B gz zusätzlich")
PY
}
vergleich() {  # name, Log basis, Log umgebaut, rc basis, rc umgebaut
  ob=$(grep -c '^ *ok' "$2"); ou=$(grep -c '^ *ok' "$3")
  fb=$(grep 'FEHLT' "$2" | sed 's/[0-9][0-9.,]*//g' | sort); fu=$(grep 'FEHLT' "$3" | sed 's/[0-9][0-9.,]*//g' | sort)
  if [ "$4" = "$5" ] && [ "$ob" = "$ou" ] && [ "$fb" = "$fu" ]; then
    echo "  ok    $1: Rückgabe $5, $ou × ok, $(grep -c FEHLT "$3") × FEHLT, wie Potsdam"
  elif [ "$1" = A7_planer ] && ausnahme_gewicht "$2" "$3" "$4" "$5"; then
    :   # Ausnahme KR10 greift, die Meldung schreibt ausnahme_gewicht
  else
    echo "  FEHLT $1: Potsdam Rückgabe $4 / $ob × ok, umgebaut Rückgabe $5 / $ou × ok"
    diff "$2" "$3" | grep '^[<>].*\(FEHLT\|ok\)' | head -20 | sed 's/^/        /'
    abw=$((abw + 1))
  fi
}
lauf() {  # name, befehl … (in beiden Wurzeln)
  name="$1"; shift
  for r in basis umgebaut; do
    (cd "$W/$r" && KIEZ_CONFIG="$([ "$r" = umgebaut ] && echo "$KIEZ_CONFIG")" "$@" > "$W/$r.$name.log" 2>&1); echo $? > "$W/$r.$name.rc"
  done
  vergleich "$name" "$W/basis.$name.log" "$W/umgebaut.$name.log" "$(cat "$W/basis.$name.rc")" "$(cat "$W/umgebaut.$name.rc")"
}

echo "Vergleich Potsdam (basis) gegen umgebauten Code"
lauf A6_test_pfade $UV python -I pruefen/A6_test_pfade.py
lauf A8_test_pfade $UV python -I pruefen/A8_test_pfade.py
if [ "$BROWSER" -eq 1 ]; then
  for m in seiten A7_planer B5_jahre; do lauf "$m" node "pruefen/$m.mjs"; done
  for r in basis umgebaut; do
    node "$HIER/pruefen/gegenprobe_text.mjs" --wurzel "$W/$r" > "$W/$r.text.log" 2>&1 || { echo "  FEHLT Textabzug $r: $(tail -1 "$W/$r.text.log")"; abw=$((abw + 1)); }
  done
  if cmp -s "$W/basis.text.log" "$W/umgebaut.text.log"; then
    echo "  ok    Textabzug: $(grep -c '^== ' "$W/umgebaut.text.log") Seiten, sichtbarer Text gleich ($(wc -c < "$W/umgebaut.text.log") Byte)"
  else
    echo "  FEHLT Textabzug weicht ab:"; diff "$W/basis.text.log" "$W/umgebaut.text.log" | head -20 | sed 's/^/        /'; abw=$((abw + 1))
  fi
else
  echo "  übersprungen: Browserprüfungen und Textabzug (--ohne-browser)"
fi
echo
if [ "$abw" -eq 0 ]; then echo "0 Abweichungen"; exit 0; fi
echo "$abw Abweichung(en); Logs unter $W (mit GEGENPROBE_BEHALTEN=1 aufheben)"; exit 1
