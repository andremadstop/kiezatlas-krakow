#!/bin/sh
# Ablauf des Kiezatlas Kraków in einzelnen Schritten. Nichts läuft „alles auf einmal“: Mehrere Worktrees
# teilen sich eine Datenbank, und ein Pipeline-Lauf ohne --nur lädt jede fällige Quelle.
#
#   skripte/lauf.sh vorbereiten           lokale Rohdaten aufbereiten (kein Netz), schreibt vorbereitet/
#   skripte/lauf.sh laden --nur QUELLE    eine Quelle aus config/krakow.yaml (oder $KIEZ_CONFIG) laden (Pflicht: --nur)
#   skripte/lauf.sh auswerten             Auswertung mit der Leserolle, schreibt daten/
#   skripte/lauf.sh einrichten            nur Integration: Rollen und Rechte setzen (pipeline.einrichten
#                                         --haerten), danach sql/002 einspielen. Nicht aus einem Paket
#                                         starten: ein zweiter Lauf mit anderer YAML kann Rechte anderer
#                                         Pakete entziehen.
#   skripte/lauf.sh rechte                Rollen und Rechte der laufenden Datenbank prüfen
#                                         (pruefen/D1_rechte.py, ändert nichts), Ergebnis auf stdout
#
# Jeder Schritt schreibt einen Umgebungsbericht nach berichte/umgebung/<Zeit UTC>_<schritt>.txt: Stand der
# Pipeline (git describe, Commit, Prüfsumme ihrer requirements.txt), Stand dieses Repos, Prüfsumme der
# requirements.txt, Rückgabewert. Die Laufberichte der Pipeline (berichte/2*.json) bleiben unberührt; der
# Unterordner liegt außerhalb ihres Suchmusters.
#
# Pipeline-Stand: festgeschrieben auf PIPELINE_SOLL (unten). Weicht der Checkout ab oder hat er lokale
# Änderungen, brechen laden, auswerten, einrichten und rechte ab (Rückgabe 3), außer mit
# PIPELINE_ABWEICHUNG=1 beim Aufruf (nicht aus der .env); dann steht die Abweichung im Umgebungsbericht.
#
# Umgebung:
#   KIEZ_DATEN   Rohdaten außerhalb der Repos (Standard ../kiezatlas-daten/krakow, HERKUNFT.md je Ordner)
#   KIEZ_ENV     Datei mit POSTGRES_PASSWORD, IMPORT_PASSWORD, LESE_PASSWORD, RECHNEN_PASSWORD
#                (chmod 600, Vorlage .env.beispiel). Standard ./.env, in Worktrees ../kiezatlas-krakow/.env.
#   PIPELINE_DIR Repository der Geodaten-Import-Pipeline (Standard ../geodaten-import-pipeline)
# Braucht: Docker, uv, daneben das Repository geodaten-import-pipeline. Python-Pakete für vorbereiten aus
# requirements.txt, für laden, auswerten, einrichten und rechte aus der requirements.txt der Pipeline; beide
# mit exakten Versionen und Prüfsummen, uv immer mit --offline (kein Netz außer über skripte/abruf.py).
set -eu
cd "$(dirname "$0")/.."
# nur aus dem Aufruf, bevor die .env gelesen wird: eine dauerhafte Freigabe in der .env hebelte die Festschreibung aus
ABWEICHUNG_ERLAUBT="${PIPELINE_ABWEICHUNG:-}"
PIPELINE="${PIPELINE_DIR:-../geodaten-import-pipeline}"
# Tag <Tag> der Geodaten-Import-Pipeline. Ändern nur mit Entscheidung (docs/entscheidungen.md)
# und neuer Gegenprobe der Rechte (belege/D1_infrastruktur.md).
PIPELINE_SOLL=12bae5bc96cf34355c8c5a723eb444e66f776f2d
PY="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt python"
KIEZ_DATEN="${KIEZ_DATEN:-$(cd .. && pwd)/kiezatlas-daten/krakow}"
if [ -z "${KIEZ_ENV:-}" ]; then
  if [ -f ./.env ]; then KIEZ_ENV=./.env; else KIEZ_ENV=../kiezatlas-krakow/.env; fi
fi
case "$KIEZ_ENV" in */*) ;; *) KIEZ_ENV="./$KIEZ_ENV" ;; esac   # „.“ sucht sonst im PATH
[ -f "$KIEZ_ENV" ] || { echo "Umgebungsdatei $KIEZ_ENV fehlt (Vorlage .env.beispiel, chmod 600)" >&2; exit 2; }
set -a; . "$KIEZ_ENV"; set +a
export KIEZ_DATEN PGHOST=127.0.0.1 PGPORT="${PG_PORT:-55462}" PGDATABASE=kiezatlas PYTHONPATH="$PIPELINE"
export PIPELINE_KENNUNG="kiezatlas-krakow (+https://souverain-systems.de/kiezatlas/krakow/)"
UV="uv run -q --offline --no-project --with-requirements $PIPELINE/requirements.txt"

sha() { if [ -f "$1" ]; then sha256sum "$1" | cut -d' ' -f1; else echo fehlt; fi; }

# Stand der Pipeline ermitteln und gegen PIPELINE_SOLL prüfen. Setzt P_COMMIT, P_DESCRIBE, P_ABWEICHUNG.
pipeline_pruefen() {
  P_COMMIT=$(git -C "$PIPELINE" rev-parse HEAD 2>/dev/null || echo unbekannt)
  P_DESCRIBE=$(git -C "$PIPELINE" describe --tags --always --dirty 2>/dev/null || echo unbekannt)
  P_AENDERUNGEN=$(git -C "$PIPELINE" status --porcelain --untracked-files=no 2>/dev/null || echo unlesbar)
  P_ABWEICHUNG=nein
  if [ "$P_COMMIT" != "$PIPELINE_SOLL" ]; then P_ABWEICHUNG="Commit $P_COMMIT statt $PIPELINE_SOLL"; fi
  if [ -n "$P_AENDERUNGEN" ]; then
    if [ "$P_ABWEICHUNG" = nein ]; then P_ABWEICHUNG="lokale Änderungen im Checkout"
    else P_ABWEICHUNG="$P_ABWEICHUNG; lokale Änderungen im Checkout"; fi
  fi
  echo "Pipeline: $P_DESCRIBE ($P_COMMIT)" >&2
  if [ "$P_ABWEICHUNG" != nein ]; then
    if [ "$ABWEICHUNG_ERLAUBT" = 1 ]; then
      echo "Warnung: Pipeline weicht vom festgeschriebenen Stand ab ($P_ABWEICHUNG), zugelassen mit PIPELINE_ABWEICHUNG=1" >&2
    else
      echo "Pipeline weicht vom festgeschriebenen Stand ab ($P_ABWEICHUNG). Abbruch; zum Prüfen PIPELINE_ABWEICHUNG=1 setzen." >&2
      exit 3
    fi
  fi
}

# Umgebungsbericht schreiben: $1 Schritt, $2 Rückgabewert, $3 Startzeit, $4 Argumente
umgebung_schreiben() {
  mkdir -p berichte/umgebung
  datei="berichte/umgebung/${3}_$1.txt"
  {
    echo "schritt: $1"
    echo "argumente: $4"
    echo "start_utc: $3"
    echo "ende_utc: $(date -u +%Y%m%dT%H%M%SZ)"
    echo "rueckgabe: $2"
    echo "pipeline_describe: ${P_DESCRIBE:-nicht geprüft}"
    echo "pipeline_commit: ${P_COMMIT:-nicht geprüft}"
    echo "pipeline_soll: $PIPELINE_SOLL"
    echo "pipeline_abweichung: ${P_ABWEICHUNG:-nicht geprüft}"
    echo "pipeline_requirements_sha256: $(sha "$PIPELINE/requirements.txt")"
    echo "repo_describe: $(git describe --tags --always --dirty 2>/dev/null || echo unbekannt)"
    echo "repo_commit: $(git rev-parse HEAD 2>/dev/null || echo unbekannt)"
    echo "requirements_sha256: $(sha requirements.txt)"
    echo "uv: $(uv --version 2>/dev/null || echo unbekannt)"
    echo "datenbank: 127.0.0.1:$PGPORT/$PGDATABASE"
    if [ "$1" = laden ]; then
      # Laufbericht der Pipeline aus diesem Aufruf: jüngster berichte/2*.json mit Kennung ab der Startzeit
      bericht=$(ls berichte/2*.json 2>/dev/null | sort | tail -n 1)
      stamm=$(basename "${bericht:-0}" .json)
      if [ -n "$bericht" ] && [ "$(printf '%s\n%s\n' "$3" "$stamm" | sort | tail -n 1)" = "$stamm" ]; then
        echo "pipeline_bericht: $bericht"
      else
        echo "pipeline_bericht: keiner aus diesem Aufruf"
      fi
    fi
  } > "$datei"
  echo "Umgebungsbericht: $datei" >&2
}

schritt="${1:-}"
[ $# -gt 0 ] && shift
start=$(date -u +%Y%m%dT%H%M%SZ)
args="$*"
case "$schritt" in
  vorbereiten)
    set +e; $PY -I skripte/01_vorbereiten.py "$@"; rc=$?; set -e ;;
  laden)
    case " $* " in
      *" --nur "*) ;;
      *) echo "laden nur mit --nur QUELLE (Ladebetrieb, docs/rundgang.md, „Bau“)" >&2; exit 2 ;;
    esac
    pipeline_pruefen
    set +e
    PGUSER=pipeline_import PGPASSWORD="$IMPORT_PASSWORD" $UV python -m pipeline.laden --config "${KIEZ_CONFIG:-config/krakow.yaml}" "$@"
    rc=$?; set -e ;;
  auswerten)
    pipeline_pruefen
    set +e; PGUSER=mosidi_lesen PGPASSWORD="$LESE_PASSWORD" $UV python skripte/02_auswerten.py; rc=$?; set -e ;;
  einrichten)
    # Den Container startet man im Haupt-Checkout (docker compose up -d --wait db). Der Projektname steht in
    # docker-compose.yml fest, ein Start aus einem Worktree träfe also denselben Container, bände aber
    # ./sql aus dem Worktree ein; verschwindet der Worktree, fehlt die Quelle beim nächsten Neuanlegen.
    docker inspect -f '{{.State.Health.Status}}' kiezatlas-krakow-db-1 2>/dev/null | grep -qx healthy \
      || { echo "Container kiezatlas-krakow-db-1 läuft nicht (im Haupt-Checkout: docker compose up -d --wait db)" >&2; exit 1; }
    pipeline_pruefen
    # Reihenfolge: erst die Rollen der Pipeline (pipeline_import, mosidi_lesen), dann sql/002. Umgekehrt fehlte
    # mosidi_lesen auf einem frischen Volume das Leserecht auf auswertung, weil sql/002 es nur vergibt, wenn
    # die Rolle schon existiert (belege/D1_infrastruktur.md).
    set +e
    PGUSER=admin PGPASSWORD="$POSTGRES_PASSWORD" $UV python -m pipeline.einrichten --config "${KIEZ_CONFIG:-config/krakow.yaml}" --haerten \
      && PGUSER=admin PGPASSWORD="$POSTGRES_PASSWORD" $UV python skripte/ausbau_einrichten.py
    rc=$?; set -e ;;
  rechte)
    pipeline_pruefen
    set +e; $UV python pruefen/D1_rechte.py "$@"; rc=$?; set -e ;;
  *)
    echo "Aufruf: skripte/lauf.sh vorbereiten | laden --nur QUELLE | auswerten | einrichten | rechte" >&2
    exit 2 ;;
esac
umgebung_schreiben "$schritt" "$rc" "$start" "$args"
exit "$rc"
