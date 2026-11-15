#!/bin/sh
# Ein Befehl für den ganzen Kiezatlas Kraków; Beschreibung: ./atlas.sh hilfe (Logik in skripte/atlas.sh).
exec sh "$(dirname "$0")/skripte/atlas.sh" "$@"
