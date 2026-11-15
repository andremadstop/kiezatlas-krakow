#!/bin/sh
# Grenzen der dzielnice und Zellen in die Datenbank (Integration, Rolle admin). Nur offline.
#
#   skripte/05_db_gliederung.sh ddl       sql/003_zellen.sql einspielen (IF NOT EXISTS, beliebig oft)
#   skripte/05_db_gliederung.sh laden     public.stadtteil und public.zensus_zelle neu füllen, Beleg schreiben
#   skripte/05_db_gliederung.sh pruefen   nur abgleichen (Rechnung, daten/zellen_odbl.js, Auswahl der Fußweg-Rechnung)
#
# KIEZ_ENV: Datei mit POSTGRES_PASSWORD (chmod 600), Standard ./.env, in Worktrees ../kiezatlas-krakow/.env.
set -eu
cd "$(dirname "$0")/.."
KIEZ_DATEN="${KIEZ_DATEN:-$(cd .. && pwd)/kiezatlas-daten/krakow}"
if [ -z "${KIEZ_ENV:-}" ]; then
  if [ -f ./.env ]; then KIEZ_ENV=./.env; else KIEZ_ENV=../kiezatlas-krakow/.env; fi
fi
case "$KIEZ_ENV" in */*) ;; *) KIEZ_ENV="./$KIEZ_ENV" ;; esac
UV="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt"
set -a; . "$KIEZ_ENV"; set +a
export KIEZ_DATEN PGHOST=127.0.0.1 PGPORT="${PG_PORT:-55462}" PGDATABASE="${PG_DATABASE:-kiezatlas}"
export PGUSER=admin PGPASSWORD="$POSTGRES_PASSWORD"
unset POSTGRES_PASSWORD IMPORT_PASSWORD LESE_PASSWORD RECHNEN_PASSWORD
case "${1:-}" in
  ddl)     $UV python -I -c 'import psycopg,sys; c=psycopg.connect(autocommit=True); c.execute(open("sql/003_zellen.sql",encoding="utf-8").read()); print("sql/003_zellen.sql eingespielt")' ;;
  laden)   $UV python -I skripte/05_db_gliederung.py ;;
  pruefen) $UV python -I skripte/05_db_gliederung.py --pruefen ;;
  *) echo "Aufruf: skripte/05_db_gliederung.sh ddl | laden | pruefen" >&2; exit 2 ;;
esac
