#!/bin/sh
# Ein Befehl für den ganzen Kiezatlas Kraków. Aufruf über ./atlas.sh im Wurzelordner (reicht hierher weiter).
#
#   ./atlas.sh trocken [--ohne-datenbank] [--ab SCHRITT] [--nur SCHRITT]   Plan und Eingänge prüfen, nichts schreiben
#   ./atlas.sh alles   [--ohne-datenbank] [--ab SCHRITT] [--nur SCHRITT] [--ohne-browser]
#                                              Kette rechnen, Seiten erzeugen, ./pruefen.sh; Halt beim ersten Fehler
#   ./atlas.sh liste                           Schritte der Kette
#   ./atlas.sh pruefen [Schalter von pruefen.sh]   nur die Prüfungen
#   ./atlas.sh schnappschuss --ziel DIR        weiterverbreitbare Rohdaten als Archiv (skripte/schnappschuss.py)
#   ./atlas.sh oeffentlich [--historie]        Prüfung vor einer Veröffentlichung (skripte/oeffentlich_pruefen.py)
#
# Die Logik steht in skripte/kette.py (nur Python-Standardbibliothek, ab Python 3.11); Anleitung:
# docs/uruchomienie.md (polnisch), docs/running.md (englisch).
set -eu
cd "$(dirname "$0")/.."
PY=""
for p in python3.13 python3.12 python3.11 python3; do
  if command -v "$p" >/dev/null 2>&1 && "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    PY="$p"; break
  fi
done
[ -n "$PY" ] || { echo "Python ab 3.11 nicht gefunden (für die Kette selbst; die Schritte nutzen Python 3.13 über uv)" >&2; exit 2; }
befehl="${1:-hilfe}"
[ $# -gt 0 ] && shift
case "$befehl" in
  trocken|alles|liste) exec "$PY" -I skripte/kette.py "$befehl" "$@" ;;
  pruefen)             exec sh ./pruefen.sh "$@" ;;
  schnappschuss)       exec "$PY" -I skripte/schnappschuss.py "$@" ;;
  oeffentlich)         exec "$PY" -I skripte/oeffentlich_pruefen.py "$@" ;;
  hilfe|-h|--help)     sed -n '2,13p' skripte/atlas.sh | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "unbekannter Befehl: $befehl (./atlas.sh hilfe)" >&2; exit 4 ;;
esac
