# Prüfprotokoll Infrastruktur

Was das Paket Infrastruktur prüft, wie man es wiederholt und wohin es gehört. Ergebnisse: `belege/D1_infrastruktur.md`.

| Prüfung | Aufruf | braucht | Vorschlag für `pruefen.sh` |
|---|---|---|---|
| Abrufwerkzeug: Sperrliste, Kartenbilder, robots.txt, Protokoll, Prüfsummenliste (26 Fälle, lokaler HTTPS-Server) | `uv run -q --offline --python 3.13 --no-project --with-requirements requirements-pruefen.txt python -m pytest -q pruefen/d1_test_abruf.py` | openssl, kein Netz, keine Datenbank | aufnehmen (rund 6 s) |
| Netz, Rollen und Rechte der laufenden Datenbank (49 Fälle, ändert nichts) | `sh skripte/lauf.sh rechte` | laufender Container, `.env` | nicht aufnehmen (`pruefen.sh` liest keine `.env`); in `docs/rundgang.md` nach jedem `lauf.sh einrichten` |
| Pipeline-Stand | jeder Schritt von `skripte/lauf.sh` außer `vorbereiten` | Checkout `../geodaten-import-pipeline` | läuft von selbst; Umgebungsbericht unter `berichte/umgebung/` |
| requirements reproduzierbar | Befehl im Kopf von `requirements.in` bzw. `requirements-pruefen.in`, danach `git diff --exit-code requirements*.txt` | uv-Zwischenspeicher | optional aufnehmen |

Vor jedem Commit dieses Pakets: `sh -n skripte/lauf.sh`, `ruff check --line-length 120` auf `skripte/abruf.py`,
`pruefen/D1_rechte.py`, `pruefen/d1_test_abruf.py`, `docker compose --env-file ../kiezatlas-krakow/.env config -q`,
`./pruefen.sh --ohne-browser`. `shellcheck` ist auf dem Rechner nicht installiert.
