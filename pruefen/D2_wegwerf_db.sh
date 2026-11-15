#!/bin/sh
# Ende-zu-Ende-Probe des Fußwegs in einer Wegwerf-PostGIS mit Beispieldaten (fixture: true).
#
#   pruefen/D2_wegwerf_db.sh [--beleg DATEI]      Standard: belege/D2_fussweg.md
#
# Ablauf: eigener Container aus demselben Image wie docker-compose.yml (Digest), nur auf 127.0.0.1, freier Port,
# Datenbank kiezatlas_wegwerf auf tmpfs (nichts bleibt auf der Platte), sql/ als Init-Skripte (nur lesend
# eingebunden). Dann: Rolle kiezatlas_rechnen mit Zufallspasswort, Beispielwelt (pruefen/D2_beispielwelt.py),
# skripte/14b_fussweg.sh rechnen, pruefen und test mit A5B_DB_TEST=1. Am Ende wird der Container gestoppt
# (--rm entfernt ihn); Passwörter liegen nur in einem Wegwerf-Ordner mit Rechten 700/600.
# Die gemeinsame Datenbank (kiezatlas-krakow-db-1, Port 55462) wird nie angesprochen: Port und Datenbankname
# sind andere, und Beispielwelt und Datenbank-Tests brechen in jeder anderen Datenbank als kiezatlas_wegwerf ab.
set -eu
cd "$(dirname "$0")/.."
unset PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE PGSERVICE A5B_DB_TEST KIEZ_ENV 2>/dev/null || true
BELEG=belege/D2_fussweg.md
while [ $# -gt 0 ]; do
  case "$1" in
    --beleg) BELEG="$2"; shift 2 ;;
    *) echo "unbekannter Schalter: $1" >&2; exit 2 ;;
  esac
done
UV="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt"
BILD=$(sed -n 's/^ *image: *//p' docker-compose.yml | head -n 1)
[ -n "$BILD" ] || { echo "kein image in docker-compose.yml" >&2; exit 1; }
DB=kiezatlas_wegwerf
PORT=$($UV python -I -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
[ "$PORT" != 55462 ] || { echo "Port 55462 ist der gemeinsamen Datenbank vorbehalten" >&2; exit 1; }
NAME="kiezatlas-d2-wegwerf-$$"
WEG=$(mktemp -d)
chmod 700 "$WEG"
aufraeumen() { docker stop "$NAME" >/dev/null 2>&1 || true; rm -rf "$WEG"; }
trap aufraeumen EXIT INT TERM
zufall() { od -An -N24 -tx1 /dev/urandom | tr -d ' \n'; }
ADMIN_PW=$(zufall); RECHNEN_PW=$(zufall)
umask 077
printf 'POSTGRES_DB=%s\nPOSTGRES_USER=admin\nPOSTGRES_PASSWORD=%s\n' "$DB" "$ADMIN_PW" > "$WEG/container.env"
printf 'RECHNEN_PASSWORD=%s\nPG_PORT=%s\nPG_DATABASE=%s\n' "$RECHNEN_PW" "$PORT" "$DB" > "$WEG/rechnen.env"
umask 022

echo "Wegwerf-PostGIS $NAME, $BILD, 127.0.0.1:$PORT, Datenbank $DB"
docker run -d --rm --name "$NAME" --env-file "$WEG/container.env" --tmpfs /var/lib/postgresql/data:rw \
  -p "127.0.0.1:$PORT:5432" -v "$(pwd)/sql:/docker-entrypoint-initdb.d:ro" "$BILD" >/dev/null
admin_sql() { PGPASSWORD="$ADMIN_PW" psql -X -q -h 127.0.0.1 -p "$PORT" -U admin -d "$DB" -v ON_ERROR_STOP=1 "$@"; }
i=0
until [ "$(admin_sql -Atc "SELECT to_regclass('auswertung.zelle_gruen') IS NOT NULL" 2>/dev/null)" = t ]; do
  i=$((i + 1)); [ $i -le 120 ] || { echo "Wegwerf-PostGIS nicht bereit nach 120 s" >&2; docker logs "$NAME" | tail -20; exit 1; }
  sleep 1
done
# Variable über stdin (psql setzt :'pw' in -c nicht ein), so steht das Passwort in keiner Befehlszeile
echo "ALTER ROLE kiezatlas_rechnen LOGIN PASSWORD :'pw';" | admin_sql -v pw="$RECHNEN_PW"

echo "== Beispielwelt"
PGHOST=127.0.0.1 PGPORT="$PORT" PGDATABASE="$DB" PGUSER=admin PGPASSWORD="$ADMIN_PW" \
  $UV python -I pruefen/D2_beispielwelt.py | tee "$WEG/welt.txt"
echo "== Rechnen"
KIEZ_ENV="$WEG/rechnen.env" skripte/14b_fussweg.sh rechnen --bericht "$WEG/bericht.md" > "$WEG/rechnen.txt"
cat "$WEG/bericht.md"
echo "== Abnahme"
rc_pruefen=0
KIEZ_ENV="$WEG/rechnen.env" skripte/14b_fussweg.sh pruefen > "$WEG/pruefen.txt" || rc_pruefen=$?
cat "$WEG/pruefen.txt"
echo "== Tests mit Datenbank"
rc_test=0
A5B_DB_TEST=1 KIEZ_ENV="$WEG/rechnen.env" skripte/14b_fussweg.sh test -rs > "$WEG/test.txt" 2>&1 || rc_test=$?
tail -n 5 "$WEG/test.txt"

commit=$(git rev-parse HEAD)
offen=$(git status --porcelain -- skripte pruefen sql config | wc -l)
{
  echo "# Beleg Fußweg je Zelle: Probe mit Beispieldaten"
  echo
  echo "**Beispieldaten (fixture: true).** Netz, Zellen und Ziele sind erfunden (\`pruefen/D2_beispielwelt.py\`, fester"
  echo "Zufallsstartwert). Keine Zahl hier beschreibt Kraków. Belegt ist nur, dass Rechnung und Abnahme durchlaufen"
  echo "und die Kriterien aus \`pruefen/D2_protokoll.md\` greifen."
  echo
  echo "- Lauf: $(date '+%d.%m.%Y %H:%M:%S %Z'), Commit \`$commit\`, offene Änderungen in skripte/, pruefen/, sql/, config/: $offen"
  echo "- Aufruf: \`pruefen/D2_wegwerf_db.sh\` (Wegwerf-PostGIS \`$BILD\`, 127.0.0.1, Datenbank \`$DB\` auf tmpfs)"
  echo "- Werkzeuge: $(uv --version), Python $($UV python -c 'import sys; print(sys.version.split()[0])')"
  echo
  echo "## Schritt 1: Beispielwelt (Zeilen je Tabelle nach dem Anlegen)"
  echo
  echo "| Tabelle | Zeilen |"
  echo "|---|---:|"
  sed -n 's/^zaehlung \([^ ]*\) \(.*\)$/| `\1` | \2 |/p' "$WEG/welt.txt"
  echo
  echo "## Schritt 2: Rechnung (Bericht von \`skripte/14b_fussweg.py\`, Überschriften eine Ebene tiefer)"
  echo
  sed -e '1d' -e 's/^## /### /' "$WEG/bericht.md"
  echo
  echo "## Schritt 3: Abnahme (\`skripte/14b_fussweg.sh pruefen\`, Rückgabe $rc_pruefen)"
  echo
  echo '```'
  cat "$WEG/pruefen.txt"
  echo '```'
  echo
  echo "## Schritt 4: Tests mit Datenbank (\`A5B_DB_TEST=1 skripte/14b_fussweg.sh test\`, Rückgabe $rc_test)"
  echo
  echo '```'
  tail -n 3 "$WEG/test.txt"
  echo '```'
} > "$BELEG"
echo "Beleg: $BELEG (Abnahme $rc_pruefen, Tests $rc_test)"
[ "$rc_pruefen" -eq 0 ] && [ "$rc_test" -eq 0 ]
