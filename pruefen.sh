#!/bin/sh
# Alle Prüfungen des Kiezatlas, die ohne Netz und ohne Datenbank laufen, nacheinander.
# Anders als ein Abbruch beim ersten Fehler laufen hier immer alle Prüfungen; am Ende steht die Zählung.
# Rückgabe 0 = alles grün, 1 = mindestens ein Befund. Übersprungene Prüfungen (fehlende Rohdaten,
# --ohne-browser) zählen nicht als Befund, stehen aber in der Zählung.
#
#   ./pruefen.sh                 alles, auch die Browser-Prüfungen (Playwright, rund sechzehn Minuten)
#   ./pruefen.sh --ohne-browser  ohne pruefen/*.mjs
#   ./pruefen.sh --voll          zusätzlich die langen Paketprüfungen, die aus den Rohdaten byte-gleich neu rechnen
#                                (Gliederung, Gebäude, Denkmale, Sanierungsatlas, 3D-Dateien außerhalb des Repos;
#                                braucht $KIEZ_DATEN)
#   ./pruefen.sh --gegenprobe    zusätzlich die Gegenprobe Potsdam (pruefen/gegenprobe_potsdam.sh, rund zehn Minuten,
#                                braucht ../kiezatlas-potsdam); ohne den Schalter steht sie als übersprungen in der Zählung
#
# Braucht: uv (Pakete nur aus dem lokalen Zwischenspeicher, --offline, Versionen aus requirements.txt und für die
# Schriften requirements-schriften.txt),
# node mit den Paketen aus package.json (node_modules), für die Rohdaten-Prüfsummen $KIEZ_DATEN.
# Liest keine .env und keine Datenbank: PG*-Variablen werden vorher entfernt. Was die Datenbank braucht
# (Abnahmen der Datenpakete), steht in docs/rundgang.md und läuft nicht hier.
set -u
cd "$(dirname "$0")"
unset PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE PGSERVICE A3_DB_TEST A5B_DB_TEST 2>/dev/null || true
KIEZ_DATEN="${KIEZ_DATEN:-$(cd .. && pwd)/kiezatlas-daten/krakow}"
export KIEZ_DATEN
UV="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt"
BROWSER=1; GEGENPROBE=0; VOLL=0
for a in "$@"; do
  case "$a" in
    --ohne-browser) BROWSER=0 ;;
    --gegenprobe) GEGENPROBE=1 ;;
    --voll) VOLL=1 ;;
    *) echo "unbekannter Schalter: $a"; exit 2 ;;
  esac
done

gruen=0; befund=0; ueber=0; liste=""
py() { $UV python -I "$@"; }
pys() { $UV --with-requirements requirements-schriften.txt python -I "$@"; }
pyt() { $UV --with-requirements requirements-pruefen.txt python -I "$@"; }
pruef() {
  name="$1"; shift
  echo; echo "== $name"
  start=$(date +%s)
  "$@"; rc=$?
  dauer=$(( $(date +%s) - start ))
  if [ "$rc" -eq 0 ]; then gruen=$((gruen + 1)); st="grün"; else befund=$((befund + 1)); st="BEFUND (Rückgabe $rc)"; fi
  echo "-- $name: $st, ${dauer} s"
  liste="$liste
  $st  $name"
}
ueberspringe() {
  echo; echo "== $1"; echo "-- übersprungen: $2"
  ueber=$((ueber + 1))
  liste="$liste
  übersprungen  $1 ($2)"
}

js_syntax() {
  n=0; f=0
  for d in *.js texte/*/*.js daten/ort.js pruefen/*.mjs; do
    n=$((n + 1)); node --check "$d" || { echo "  Syntaxfehler: $d"; f=$((f + 1)); }
  done
  echo "  $n Dateien, $f mit Fehler"; [ "$f" -eq 0 ]
}
sh_syntax() {
  n=0; f=0
  for d in pruefen.sh skripte/*.sh pruefen/*.sh; do
    n=$((n + 1)); sh -n "$d" || { echo "  Syntaxfehler: $d"; f=$((f + 1)); }
  done
  echo "  $n Dateien, $f mit Fehler"; [ "$f" -eq 0 ]
}
py_syntax() {
  py -c 'import ast, sys
f = 0
for d in sys.argv[1:]:
    try:
        ast.parse(open(d, encoding="utf-8").read(), d)
    except SyntaxError as e:
        print("  Syntaxfehler:", e); f += 1
print(f"  {len(sys.argv) - 1} Dateien, {f} mit Fehler"); sys.exit(1 if f else 0)' skripte/*.py pruefen/*.py
}

hash_pruefen() { (cd "$KIEZ_DATEN" && sha256sum -c --strict --quiet "$1") && echo "  $(wc -l < "$1") Dateien stimmen"; }

echo "Kiezatlas Kraków, Prüflauf $(date '+%d.%m.%Y %H:%M:%S %Z')"
echo "Commit: $(git rev-parse HEAD 2>/dev/null || echo unbekannt)"
offen=$(git status --porcelain 2>/dev/null)
if [ -z "$offen" ]; then echo "Arbeitsstand: sauber (keine offenen Änderungen)"; else echo "Arbeitsstand: offene Änderungen"; echo "$offen" | sed 's/^/  /'; fi
echo "Werkzeuge: $(uv --version), node $(node --version), Python $($UV python -c 'import sys; print(sys.version.split()[0])')"

pruef "Syntax JavaScript (node --check)" js_syntax
pruef "Syntax Shell (sh -n)" sh_syntax
pruef "Syntax Python (ast)" py_syntax
pruef "Gerüst: Ortskonfiguration, Rechen-SRID, keine Plankennungen (pruefen/geruest.py)" py pruefen/geruest.py
pruef "ort.js aktuell (skripte/31_ort.py --pruefen)" py skripte/31_ort.py --pruefen
pruef "Seiten aktuell, pl/en/de (skripte/30_seiten.py --pruefen)" py skripte/30_seiten.py --pruefen
pruef "Textschicht pl/en/de (pruefen/texte.py)" py pruefen/texte.py
pruef "Abzeichen Beispieldaten nur aus den Daten, nie fest im Seiten-HTML (pruefen/beispielmarke.py)" py pruefen/beispielmarke.py
pruef "Sprachverweise ohne Browser: hreflang, canonical, Sprachschalter (pruefen/hreflang.py)" py pruefen/hreflang.py
pruef "Datenverträge und Summen (pruefen/daten.py)" py pruefen/daten.py
pruef "Belegschicht in sich stimmig: belege/, README-Kasten, Entscheidungen, Meldeweg, Checkliste (pruefen/belege.py)" py pruefen/belege.py
pruef "Schriften: polnische Sonderzeichen in jeder Schrift (pruefen/DF_schriften.py)" pys pruefen/DF_schriften.py
pruef "Schriften: Kerning der polnischen Sonderzeichen aus den Grundbuchstaben, Lücke geschlossen (pruefen/DF_kerning.py)" pys pruefen/DF_kerning.py
if [ -d "$KIEZ_DATEN/schriften" ]; then
  pruef "Schriften aus den Fontsource-Paketen reproduzierbar (skripte/schriften.py --pruefen)" pys skripte/schriften.py --pruefen
else
  ueberspringe "Schriften aus den Fontsource-Paketen reproduzierbar (skripte/schriften.py --pruefen)" "keine Pakete unter \$KIEZ_DATEN/schriften"
fi
# Jede Datei, die noch Beispieldaten trägt, muss ihr Erzeuger byte-gleich neu erzeugen; unbekannter Erzeuger = Befund
beispiel_reproduzierbar() {
  n=0; f=0; erz=""
  for d in daten/*.js; do
    grep -q '"fixture":true' "$d" || continue
    n=$((n + 1))
    case "$(basename "$d")" in
      stadtteile_odbl.js|zellen_odbl.js|kennzahlen_odbl.js) e=pruefen/fixtures_krakow.py ;;
      denkmale.js|denkmale_odbl.js|denkmale_bdot.js) e=skripte/dz_denkmale.py ;;
      powietrze.js) e=skripte/32_powietrze.py ;;
      mieszkania_odbl.js) e=skripte/40_mieszkania.py ;;
      *) echo "  FEHLT $d: Beispieldaten ohne bekannten Erzeuger"; f=$((f + 1)); continue ;;
    esac
    case " $erz " in *" $e "*) continue ;; esac
    erz="$erz $e"
    aus=$(py "$e" --pruefen 2>&1); rc_e=$?
    echo "$aus" | sed 's/^/  /'
    [ "$rc_e" -eq 0 ] || { echo "  FEHLT $e --pruefen (für $d), Rückgabe $rc_e"; f=$((f + 1)); }
  done
  echo "  $n Dateien mit Beispieldaten, Erzeuger:${erz:- keine}; $f mit Befund"; [ "$f" -eq 0 ]
}
pruef "Beispieldaten reproduzierbar (Erzeuger je Datei mit fixture: true, --pruefen)" beispiel_reproduzierbar
ueberspringe "Vertrag Bauzeiten-Methode (pruefen/B5_methode.py, skripte/26_jahre_methode.py --pruefen)" "Bauzeiten-Kaskade für Kraków gestrichen (docs/entscheidungen.md, KR4); läuft in der Gegenprobe Potsdam mit"
if [ -f daten/planungsraeume.js ] && [ -f "$KIEZ_DATEN/eingang/planungsraeume.geojson" ]; then
  pruef "planungsraeume.js aktuell (skripte/17_planungsraeume_js.py --pruefen)" py skripte/17_planungsraeume_js.py --pruefen
else
  ueberspringe "planungsraeume.js aktuell (skripte/17_planungsraeume_js.py --pruefen)" "noch keine Raumebene unter den dzielnice"
fi
if [ -d daten/export ]; then
  pruef "GIS-Export ohne Datenbank (pruefen/A8_export.py --odbl-erwartet)" py pruefen/A8_export.py --odbl-erwartet
else
  ueberspringe "GIS-Export ohne Datenbank (pruefen/A8_export.py --odbl-erwartet)" "noch kein Export unter daten/export/"
fi
ueberspringe "Codepfade Planer und Export (pruefen/A6_test_pfade.py, pruefen/A8_test_pfade.py)" "brauchen Richtwerte und Exporte eines Orts; laufen in der Gegenprobe Potsdam"
pruef "OSM-Leser und Netz, ohne Datenbank (skripte/12_osm.sh test)" skripte/12_osm.sh test
pruef "Fußweg, ohne Datenbank (skripte/14b_fussweg.sh test)" skripte/14b_fussweg.sh test
ueberspringe "Landesfilter (skripte/14b_fussweg.sh kreuzprobe)" "Landesfilter über VBB-DHID entfällt für Kraków (Bauvorlage, 14b)"
# Prüfungen der Datenpakete (ohne Netz und ohne Datenbank; Regeln je Paket in pruefen/<paket>_protokoll.md)
BDOT="$KIEZ_DATEN/2026-11-13/03_gebaeude/1261_SHP.zip"
pruef "Abrufwerkzeug: Sperrliste, robots.txt, Protokoll (pytest pruefen/d1_test_abruf.py)" pyt -m pytest -q pruefen/d1_test_abruf.py
pruef "Gliederung und Bevölkerung, Ausgaben (pruefen/D4_bevoelkerung.py --ohne-rohdaten)" py pruefen/D4_bevoelkerung.py --ohne-rohdaten
pruef "Gebäude und 3D, Ausgaben (pruefen/D5_gebaeude.py --ohne-rohdaten)" py pruefen/D5_gebaeude.py --ohne-rohdaten
pruef "Versorgung und Takt (pruefen/D6_versorgung.py; Skripte mit Datenbank übersprungen)" py pruefen/D6_versorgung.py
# Luft und Wohnungsmarkt rechnen seit den Handdownloads nur aus den Rohdaten neu (eingang/eea, eingang/rcn). Fehlen
# sie, prüft die CI-Fassung (--ohne-lauf) die Dateien im Repo, und die Neurechnung zählt als übersprungen.
eea_da() { for f in "$KIEZ_DATEN"/eingang/eea/*.csv "$KIEZ_DATEN"/eingang/eea/*.geojson "$KIEZ_DATEN"/eingang/eea/*.geojson.zip; do [ -f "$f" ] && return 0; done; return 1; }
rcn_da() { for f in "$KIEZ_DATEN"/eingang/rcn/*.gpkg; do [ -f "$f" ] && return 0; done; return 1; }
if eea_da; then
  pruef "Luft (pruefen/D7_powietrze.py)" py pruefen/D7_powietrze.py
else
  pruef "Luft, Dateien im Repo (pruefen/D7_powietrze.py --ohne-lauf)" py pruefen/D7_powietrze.py --ohne-lauf
  ueberspringe "Luft aus den Rohdaten neu (skripte/32_powietrze.py --pruefen)" "kein EEA-Auszug unter \$KIEZ_DATEN/eingang/eea"
fi
pruef "Grundkarte, eigener Dekoder (pruefen/D8_grundkarte.py; ohne Kachelordner übersprungen)" py pruefen/D8_grundkarte.py
pruef "Klima, Ausgaben (pruefen/dk_klimat.py)" py pruefen/dk_klimat.py
if [ -f "$BDOT" ]; then
  pruef "Klima aus den Rohdaten byte-gleich (skripte/35_klimat.py --pruefen)" py skripte/35_klimat.py --pruefen
else
  ueberspringe "Klima aus den Rohdaten byte-gleich (skripte/35_klimat.py --pruefen)" "BDOT10k 1261 fehlt unter \$KIEZ_DATEN"
fi
if rcn_da; then
  pruef "Wohnungsmarkt (pruefen/DW_mieszkania.py)" py pruefen/DW_mieszkania.py
else
  pruef "Wohnungsmarkt, Dateien im Repo (pruefen/DW_mieszkania.py --ohne-lauf)" py pruefen/DW_mieszkania.py --ohne-lauf
  ueberspringe "Wohnungsmarkt aus den Rohdaten neu (skripte/40_mieszkania.py --pruefen)" "kein GeoPackage unter \$KIEZ_DATEN/eingang/rcn"
fi
pruef "Denkmale und Kamienice, Ausgaben (pruefen/DZ_denkmale.py)" py pruefen/DZ_denkmale.py
dz_eingang() { py pruefen/DZ_test_eingang.py; rc=$?; [ "$rc" -eq 77 ] && { echo "  BDOT10k fehlt, Codepfade nicht geprüft"; return 0; }; return "$rc"; }
if [ -f "$BDOT" ]; then
  pruef "Denkmale: Leser der Handdownloads mit erfundenen Eingängen (pruefen/DZ_test_eingang.py)" dz_eingang
else
  ueberspringe "Denkmale: Leser der Handdownloads mit erfundenen Eingängen (pruefen/DZ_test_eingang.py)" "BDOT10k 1261 fehlt unter \$KIEZ_DATEN"
fi
pruef "Sanierungsatlas, Ausgaben und Beleg (pruefen/DS_sanierung.py)" py pruefen/DS_sanierung.py
pruef "Daten-Nacharbeit: keine Sätze in Datenpaketen, Ortsmarke, radius_m, JavaScript-Startgewicht (pruefen/N1_daten.py)" py pruefen/N1_daten.py
pruef "Übersichtsgrenzen der Startseite byte-gleich (skripte/02a_stadtteile_uebersicht.py --pruefen)" py skripte/02a_stadtteile_uebersicht.py --pruefen
pruef "Vor Veröffentlichung: Pfade, Adressen, Rechnernamen, Geheimnisse, Plankennungen, Lizenzregeln (skripte/oeffentlich_pruefen.py)" py skripte/oeffentlich_pruefen.py
# Prüfungen der Seitenpakete (ohne Browser): Vergleich, Zählungen der Kartenseiten, Downloads, Langtexte
if [ -f "$KIEZ_DATEN/2026-11-14/41_vergleich/DE_PD_3035_GPKG.zip" ] && [ -d ../kiezatlas-potsdam/.git ]; then
  pruef "Vergleich Kraków–Potsdam byte-gleich neu gerechnet (skripte/41_porownanie.py --pruefen)" py skripte/41_porownanie.py --pruefen
else
  ueberspringe "Vergleich Kraków–Potsdam byte-gleich neu gerechnet (skripte/41_porownanie.py --pruefen)" "Eurostat-Gitter DE unter \$KIEZ_DATEN/2026-11-14/41_vergleich/ oder ../kiezatlas-potsdam fehlt"
fi
pruef "Kartenseiten: Zählungen gegen den Beleg (pruefen/S2_zaehlungen.py --pruefen)" py pruefen/S2_zaehlungen.py --pruefen
pruef "Downloads aus den Datendateien byte-gleich (skripte/16_export_krakow.py --pruefen)" py skripte/16_export_krakow.py --pruefen
pruef "Downloads: Ebenen, Felder, Lizenzen (pruefen/S4_export.py)" py pruefen/S4_export.py
pruef "Langtexte aus Quelltexten und Daten byte-gleich (skripte/16_bloecke_krakow.py --pruefen)" py skripte/16_bloecke_krakow.py --pruefen
pruef "Langtexte: Platzhalter, Falschsätze, ODbL-Vermerk (pruefen/S4_bloecke.py)" py pruefen/S4_bloecke.py
VOLL_LISTE="Gliederung (pruefen/D4_bevoelkerung.py), Gebäude (pruefen/D5_gebaeude.py), Denkmale (pruefen/DZ_denkmale.py --mit-rohdaten), Sanierungsatlas (pruefen/DS_sanierung.py --neu), 3D-Dateien (skripte/20_bdot10k.py --pruefen --geometrie)"
# 3D-Ordner wie Entwicklungsserver und Deploy-Kopie: Stand aus config/gebaeude_3d.json, sonst jüngster *-odbl mit Manifest
GEB3D=$(node -e 'import("./skripte/entwicklung_server.mjs").then((m) => console.log(m.gebaeudeordner()))' 2>/dev/null)
[ -n "$GEB3D" ] || GEB3D="$KIEZ_DATEN/abgeleitet/gebaeude/2026-11-13-odbl"
if [ "$VOLL" -eq 1 ] && [ -f "$BDOT" ]; then
  pruef "aus den Rohdaten neu: Gliederung und Bevölkerung (pruefen/D4_bevoelkerung.py)" py pruefen/D4_bevoelkerung.py
  pruef "aus den Rohdaten neu: Gebäude und 3D (pruefen/D5_gebaeude.py)" py pruefen/D5_gebaeude.py
  pruef "aus den Rohdaten neu: Denkmale (pruefen/DZ_denkmale.py --mit-rohdaten)" py pruefen/DZ_denkmale.py --mit-rohdaten
  pruef "aus den Rohdaten neu: Sanierungsatlas (pruefen/DS_sanierung.py --neu)" py pruefen/DS_sanierung.py --neu
  if [ -d "$GEB3D" ]; then
    pruef "aus den Rohdaten neu: 3D-Dateien und Manifest byte-gleich (skripte/20_bdot10k.py --pruefen --geometrie \$KIEZ_DATEN/abgeleitet/gebaeude/$(basename "$GEB3D"))" py skripte/20_bdot10k.py --pruefen --geometrie "$GEB3D"
  else
    ueberspringe "aus den Rohdaten neu: 3D-Dateien (skripte/20_bdot10k.py --pruefen --geometrie)" "kein Ordner abgeleitet/gebaeude/*-odbl mit Manifest unter \$KIEZ_DATEN"
  fi
elif [ "$VOLL" -eq 1 ]; then
  ueberspringe "aus den Rohdaten neu: $VOLL_LISTE" "BDOT10k 1261 fehlt unter \$KIEZ_DATEN"
else
  ueberspringe "aus den Rohdaten neu: $VOLL_LISTE" "eigener Lauf mit --voll"
fi
n_listen=0
for hl in belege/rohdaten*.sha256; do
  [ -f "$hl" ] || continue
  n_listen=$((n_listen + 1)); pruef "Prüfsummen ($hl gegen \$KIEZ_DATEN)" hash_pruefen "$(pwd)/$hl"
done
[ "$n_listen" -eq 0 ] && ueberspringe "Prüfsummen der Rohdaten (belege/rohdaten*.sha256)" "noch keine Rohdaten abgerufen"
if [ "$BROWSER" -eq 1 ]; then
  pruef "Browser: pruefen/seiten.mjs (alle Seiten in pl, en, de)" node pruefen/seiten.mjs
  pruef "Browser: Grundkarte auf den Kartenseiten, Schriften (pruefen/DF_grundkarte.mjs)" node pruefen/DF_grundkarte.mjs
  pruef "Browser: Startseite, Karte, Steckbrief, Vergleich (pruefen/S1_seiten.mjs)" node pruefen/S1_seiten.mjs
  pruef "Browser: Erreichbarkeit, Kamienice, Wohnungsbestand, 3D (pruefen/S2_seiten.mjs)" node pruefen/S2_seiten.mjs
  pruef "Browser: Themenseiten Luft, Wohnungsmarkt, Klima (pruefen/S3_themenseiten.mjs)" node pruefen/S3_themenseiten.mjs
  pruef "Browser: Entwicklungsserver (Freigabeliste, Host-Kopf), 3D darüber, Kopfleiste bis 360 px, Kerning (pruefen/N2_auslieferung.mjs; Deploy-Teil nur mit --deploy)" node pruefen/N2_auslieferung.mjs
else
  ueberspringe "Browser: pruefen/seiten.mjs" "--ohne-browser"
  ueberspringe "Browser: pruefen/DF_grundkarte.mjs" "--ohne-browser"
  ueberspringe "Browser: pruefen/S1_seiten.mjs" "--ohne-browser"
  ueberspringe "Browser: pruefen/S2_seiten.mjs" "--ohne-browser"
  ueberspringe "Browser: pruefen/S3_themenseiten.mjs" "--ohne-browser"
  ueberspringe "Browser: pruefen/N2_auslieferung.mjs" "--ohne-browser"
fi
if [ "$GEGENPROBE" -eq 1 ]; then
  if [ "$BROWSER" -eq 1 ]; then pruef "Gegenprobe Potsdam (pruefen/gegenprobe_potsdam.sh)" pruefen/gegenprobe_potsdam.sh
  else pruef "Gegenprobe Potsdam ohne Browser (pruefen/gegenprobe_potsdam.sh --ohne-browser)" pruefen/gegenprobe_potsdam.sh --ohne-browser; fi
else
  ueberspringe "Gegenprobe Potsdam (pruefen/gegenprobe_potsdam.sh)" "eigener Lauf mit --gegenprobe"
fi

summe=$((gruen + befund + ueber))
echo
echo "== Zählung: $summe Prüfungen, $gruen grün, $befund mit Befund, $ueber übersprungen$liste"
[ "$befund" -eq 0 ]
