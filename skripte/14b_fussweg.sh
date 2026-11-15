#!/bin/sh
# Fußweg je Zelle über das OSM-Wegenetz (ODbL). Umgebung wie skripte/12_osm.sh: Rolle kiezatlas_rechnen, nur
# offline (uv --offline: Pakete aus dem lokalen Zwischenspeicher, kein Paketindex).
#
#   skripte/14b_fussweg.sh rechnen [--trockenlauf] [--zellen s.t]  Fußweg je Zelle und Art nach
#                                          auswertung.zelle_erreichbar und zelle_gruen (nur methode = fussweg),
#                                          Bericht berichte/fussweg.md
#   skripte/14b_fussweg.sh pruefen [--zellen s.t]   Abnahme gegen die Datenbank (pruefen/D2_fussweg_pruefen.py)
#   skripte/14b_fussweg.sh test            Tests ohne Datenbank (pruefen/D2_test_fussweg.py)
#   A5B_DB_TEST=1 skripte/14b_fussweg.sh test   dazu die Datenbank-Tests; laufen nur gegen die Wegwerf-Datenbank
#                                          kiezatlas_wegwerf (pruefen/D2_wegwerf_db.sh), nie gegen die gemeinsame
#
# KIEZ_ENV: Datei mit RECHNEN_PASSWORD (chmod 600), Standard ./.env, in Worktrees ../kiezatlas-krakow/.env.
# Optional darin PG_PORT (Standard 55462) und PG_DATABASE (Standard kiezatlas).
set -eu
cd "$(dirname "$0")/.."
KIEZ_DATEN="${KIEZ_DATEN:-$(cd .. && pwd)/kiezatlas-daten/krakow}"
if [ -z "${KIEZ_ENV:-}" ]; then
  if [ -f ./.env ]; then KIEZ_ENV=./.env; else KIEZ_ENV=../kiezatlas-krakow/.env; fi
fi
case "$KIEZ_ENV" in */*) ;; *) KIEZ_ENV="./$KIEZ_ENV" ;; esac
# Pakete mit exakten Versionen und Prüfsummen aus requirements.txt, pytest aus requirements-pruefen.txt.
UV="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt"

lade_umgebung() {
  set -a; . "$KIEZ_ENV"; set +a
  export KIEZ_DATEN PGHOST=127.0.0.1 PGPORT="${PG_PORT:-55462}" PGDATABASE="${PG_DATABASE:-kiezatlas}"
  export PGUSER=kiezatlas_rechnen PGPASSWORD="$RECHNEN_PASSWORD"
  unset POSTGRES_PASSWORD IMPORT_PASSWORD LESE_PASSWORD
}

schritt="${1:-}"
[ $# -gt 0 ] && shift
case "$schritt" in
  rechnen) lade_umgebung; $UV python -I skripte/14b_fussweg.py "$@" ;;
  pruefen) lade_umgebung; $UV python -I pruefen/D2_fussweg_pruefen.py "$@" ;;
  test)
    if [ "${A5B_DB_TEST:-0}" = 1 ]; then lade_umgebung; fi
    $UV --with-requirements requirements-pruefen.txt python -I -m pytest -q -p no:cacheprovider pruefen/D2_test_fussweg.py "$@" ;;
  *) echo "Aufruf: skripte/14b_fussweg.sh rechnen [--trockenlauf] [--zellen schema.tabelle] | pruefen | test" >&2; exit 2 ;;
esac
