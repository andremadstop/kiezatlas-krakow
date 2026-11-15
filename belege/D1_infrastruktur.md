# Infrastruktur: Datenbank, Rollen, Pipeline-Stand, Abrufwerkzeug (13.11.2026)

Belegt die Abnahme des Pakets Infrastruktur: Die Datenbank ist nur auf 127.0.0.1 erreichbar, die Rollen haben
die geringsten Rechte (gegen die laufende Datenbank geprüft, nicht nur aus `sql/` gelesen), `skripte/lauf.sh`
schreibt den Stand der Pipeline mit. Keine Passwörter in dieser Datei; sie stehen nur in `../kiezatlas-krakow/.env`
(chmod 600, nicht im Repo).

## Umgebung

| Teil | Stand |
|---|---|
| PostGIS | `postgis/postgis:16-3.6@sha256:d07ce3f06f657b6516c7511412232e97174d7e9dcf4c9fe520109b682b44a201` (wie Potsdam), PostgreSQL 16.15 |
| Compose-Projekt | `kiezatlas-krakow`, Container `kiezatlas-krakow-db-1`, Volume `kiezatlas-krakow_pgdata`, angelegt 13.11.2026 12:53 UTC |
| Port | `127.0.0.1:55462` (Potsdam belegt `127.0.0.1:55461`) |
| Geodaten-Import-Pipeline | Tag `<Tag>` = `12bae5bc96cf34355c8c5a723eb444e66f776f2d`, Checkout ohne Änderungen; `requirements.txt` sha256 `430bed172559d1b6bdea438b8a80941385eb5b8375b47571a42d63ab1576a74f` |
| uv | 0.11.3, immer `--offline` |

## 1. Datenbank nur auf 127.0.0.1

Gestartet im Haupt-Checkout mit `docker compose up -d --wait db` (die `.env` liegt dort). Beim ersten Start spielte
`docker-entrypoint-initdb.d` `001_kiezatlas.sql` und `002_ausbau.sql` ein.

```
$ ss -ltnH | grep 5546
LISTEN 0      4096                        127.0.0.1:55461 0.0.0.0:*
LISTEN 0      4096                        127.0.0.1:55462 0.0.0.0:*
$ docker port kiezatlas-krakow-db-1
5432/tcp -> 127.0.0.1:55462
$ docker inspect -f '{{json .HostConfig.PortBindings}} {{json .HostConfig.SecurityOpt}}' kiezatlas-krakow-db-1
{"5432/tcp":[{"HostIp":"127.0.0.1","HostPort":"55462"}]} ["no-new-privileges:true"]
```

Kein Listener auf `0.0.0.0` oder `[::]`. Restrisiko (wie in Potsdam): Über die Bridge-Adresse des Containers ist
5432 vom eigenen Rechner und aus Containern im selben Compose-Netz erreichbar, nicht aus dem LAN.

## 2. Reihenfolge in `lauf.sh einrichten`

Auf dem frischen Volume, in der bisherigen Reihenfolge (erst `skripte/ausbau_einrichten.py` mit `sql/002`, dann
`pipeline.einrichten --haerten`):

```
$ … has_schema_privilege('mosidi_lesen','auswertung','USAGE'), has_table_privilege('mosidi_lesen','auswertung.einrichtung','SELECT')
False	False
```

Ursache: `sql/002` vergibt die Leserechte an `mosidi_lesen` nur `IF EXISTS`, die Rolle legt aber erst
`pipeline.einrichten` an. Damit wäre `lauf.sh auswerten` (läuft als `mosidi_lesen`) auf `auswertung` blind gewesen.
`lauf.sh einrichten` ruft deshalb jetzt erst `pipeline.einrichten`, dann `ausbau_einrichten.py` auf. Danach:

```
$ sh skripte/lauf.sh einrichten
…
REVOKE ALL ON DATABASE "kiezatlas" FROM PUBLIC
REVOKE CREATE ON SCHEMA public FROM PUBLIC
pipeline_meta und Rollen pipeline_import, mosidi_lesen eingerichtet.
sql/002_ausbau.sql eingespielt, 8 Tabellen in auswertung, Rolle kiezatlas_rechnen mit Anmeldung.
$ … (dieselbe Abfrage)
True	True
```

## 3. Rollen nach geringsten Rechten

`sh skripte/lauf.sh rechte` (`pruefen/D1_rechte.py`, ändert nichts; Schreibproben laufen in zurückgerollten
Transaktionen, als „abgewiesen“ zählt nur eine Rechteverweigerung). Stand `6d88eca`, 13.11.2026 13:01 UTC:

```
Pipeline: <Tag> (12bae5bc96cf34355c8c5a723eb444e66f776f2d)
OK      Container veröffentlicht nur auf 127.0.0.1 (gefunden: 127.0.0.1, Port 55462)
        Datenbank kiezatlas, Port im Container 5432, PostgreSQL 16.15 (Debian 16.15-1.pgdg13+2) on x86_64-pc-linux-gnu
OK      password_encryption = scram-sha-256
OK      pipeline_import: Anmeldung mit SCRAM-Passwort
OK      pipeline_import: keine Sonderrechte (SUPERUSER, CREATEROLE, CREATEDB, BYPASSRLS, REPLICATION)
OK      pipeline_import: in keiner anderen Rolle
OK      pipeline_import: besitzt keine Datenbank, kein Schema, keine Tabelle, keine Funktion
OK      pipeline_import: kein CREATE auf der Datenbank
OK      pipeline_import: kein CREATE auf Schema public
OK      pipeline_import: kein CREATE auf Schema auswertung
OK      pipeline_import: kein CREATE auf Schema pipeline_meta
OK      mosidi_lesen: Anmeldung mit SCRAM-Passwort
OK      mosidi_lesen: keine Sonderrechte (SUPERUSER, CREATEROLE, CREATEDB, BYPASSRLS, REPLICATION)
OK      mosidi_lesen: in keiner anderen Rolle
OK      mosidi_lesen: besitzt keine Datenbank, kein Schema, keine Tabelle, keine Funktion
OK      mosidi_lesen: kein CREATE auf der Datenbank
OK      mosidi_lesen: kein CREATE auf Schema public
OK      mosidi_lesen: kein CREATE auf Schema auswertung
OK      mosidi_lesen: kein CREATE auf Schema pipeline_meta
OK      kiezatlas_rechnen: Anmeldung mit SCRAM-Passwort
OK      kiezatlas_rechnen: keine Sonderrechte (SUPERUSER, CREATEROLE, CREATEDB, BYPASSRLS, REPLICATION)
OK      kiezatlas_rechnen: in keiner anderen Rolle
OK      kiezatlas_rechnen: besitzt keine Datenbank, kein Schema, keine Tabelle, keine Funktion
OK      kiezatlas_rechnen: kein CREATE auf der Datenbank
OK      kiezatlas_rechnen: kein CREATE auf Schema public
OK      kiezatlas_rechnen: kein CREATE auf Schema auswertung
OK      kiezatlas_rechnen: kein CREATE auf Schema pipeline_meta
OK      PUBLIC: keine Rechte auf der Datenbank
OK      PUBLIC: kein CREATE auf Schema public
OK      PUBLIC: kein CREATE auf Schema auswertung
OK      18 Tabellen und Sichten in public, auswertung, pipeline_meta geprüft
OK      pipeline_import: schreibt nicht in auswertung, kein TRUNCATE, REFERENCES, TRIGGER
OK      mosidi_lesen: schreibt nirgends
OK      kiezatlas_rechnen: schreibt nur Zeilen in auswertung (INSERT, UPDATE, DELETE, TRUNCATE)
        pipeline_import schreibt in public (Ziele aus config/krakow.yaml und table_metadata): nichts
OK      mosidi_lesen: keine TEMP-Tabellen
OK      mosidi_lesen: SELECT auf auswertung.einrichtung geht
OK      mosidi_lesen: CREATE TABLE in public wird abgewiesen (permission denied for schema public)
OK      mosidi_lesen: CREATE TEMP TABLE wird abgewiesen (permission denied to create temporary tables in database "kiezatlas")
OK      mosidi_lesen: INSERT in auswertung.einrichtung wird abgewiesen (permission denied for table einrichtung)
OK      mosidi_lesen: INSERT in public.stadtteil wird abgewiesen (permission denied for table stadtteil)
OK      kiezatlas_rechnen: SELECT auf public.stadtteil geht
OK      kiezatlas_rechnen: CREATE TEMP TABLE (Zwischenergebnisse) geht
OK      kiezatlas_rechnen: CREATE TABLE in auswertung wird abgewiesen (permission denied for schema auswertung)
OK      kiezatlas_rechnen: CREATE TABLE in public wird abgewiesen (permission denied for schema public)
OK      kiezatlas_rechnen: INSERT in public.stadtteil wird abgewiesen (permission denied for table stadtteil)
OK      kiezatlas_rechnen: DROP TABLE auswertung.einrichtung wird abgewiesen (must be owner of table einrichtung)
OK      kiezatlas_rechnen: ALTER TABLE auswertung.einrichtung wird abgewiesen (must be owner of table einrichtung)
OK      pipeline_import: CREATE TABLE in public wird abgewiesen (permission denied for schema public)
OK      pipeline_import: INSERT in auswertung.einrichtung wird abgewiesen (permission denied for schema auswertung)
OK      pipeline_import: TRUNCATE public.stadtteil wird abgewiesen (permission denied for table stadtteil)
49 Prüfungen, 0 Fehler
```

`pipeline_import` hat noch kein Schreibrecht in `public`, weil `config/krakow.yaml` noch keine Quellen nennt; die
Rechte je Spalte vergibt `pipeline.einrichten`, sobald die Integration Quellen einträgt. Danach `einrichten` und
`rechte` erneut laufen lassen.

Gegenprobe der Prüfung selbst: Mit absichtlich vergebenem `GRANT INSERT ON auswertung.einrichtung TO mosidi_lesen`
meldete sie zwei Fehler („schreibt nirgends; Verstöße: auswertung.einrichtung (INSERT)“ und „INSERT … wird
abgewiesen (Recht vorhanden: scheiterte erst an „null value in column "id" …“)“); nach dem `REVOKE` wieder 0.

## 4. Pipeline-Stand festgeschrieben und mitgeschrieben

`skripte/lauf.sh` vergleicht vor `laden`, `auswerten`, `einrichten` und `rechte` den Checkout der Pipeline mit
`PIPELINE_SOLL` und schreibt je Schritt `berichte/umgebung/<Zeit UTC>_<schritt>.txt` (außerhalb des Musters
`berichte/2*.json`, mit dem die Pipeline ihre Vorgängerberichte sucht). Beispiel:

```
schritt: rechte
argumente: 
start_utc: 20261113T130155Z
ende_utc: 20261113T130156Z
rueckgabe: 0
pipeline_describe: <Tag>
pipeline_commit: 12bae5bc96cf34355c8c5a723eb444e66f776f2d
pipeline_soll: 12bae5bc96cf34355c8c5a723eb444e66f776f2d
pipeline_abweichung: nein
pipeline_requirements_sha256: 430bed172559d1b6bdea438b8a80941385eb5b8375b47571a42d63ab1576a74f
repo_describe: 6d88eca
repo_commit: 6d88eca1ff3e3de725ac1a34ca08f31cb2aa3c3e
requirements_sha256: 311654dd836577711a5689bab91bc07c3a9681a0273f2d89beca2087cb4a3fa7
uv: uv 0.11.3 (x86_64-unknown-linux-gnu)
datenbank: 127.0.0.1:55462/kiezatlas
```

Bei `laden` kommt die Zeile `pipeline_bericht:` dazu (Laufbericht der Pipeline aus diesem Aufruf). Abweichung wird
abgewiesen (Pipeline-Verzeichnis testweise auf ein anderes Repo gesetzt); `PIPELINE_ABWEICHUNG=1` gilt nur beim
Aufruf, aus der `.env` wird es nicht beachtet (geprüft mit einer Umgebungsdatei, die es setzt: Abbruch wie oben):

```
$ PIPELINE_DIR=../kiezatlas-potsdam sh skripte/lauf.sh rechte
Pipeline: stand-2026-11-08b (7b6eb08d9790d9235fa524f3925d1bbac20593c9)
Pipeline weicht vom festgeschriebenen Stand ab (Commit 7b6eb08d9790d9235fa524f3925d1bbac20593c9 statt 12bae5bc96cf34355c8c5a723eb444e66f776f2d). Abbruch; zum Prüfen PIPELINE_ABWEICHUNG=1 setzen.
```

`uv run` für die Pipeline lief bisher ohne `--offline` und hätte Pakete aus dem Netz nachladen dürfen; jetzt
überall `--offline`.

## 5. requirements mit Prüfsummen

- `requirements.txt` und `requirements-pruefen.txt` neu erzeugt mit dem Befehl aus dem Kopf der `.in`-Datei
  (`uv pip compile --offline --generate-hashes --python-version 3.13 …`): byte-gleich mit dem Stand aus dem Gerüst.
- **Grenze:** `uv run --with-requirements` prüft die Prüfsummen nicht, wenn die Umgebung schon im Zwischenspeicher
  liegt. Probe: Kopie von `requirements-pruefen.txt` mit verfälschten Prüfsummen für `iniconfig`, danach
  `uv run -q --offline --python 3.13 --no-project --with-requirements <kopie> python -c 1` → Rückgabe 0. Eine
  Installation mit Prüfung (`uv pip sync --require-hashes`) braucht die Wheels; die liegen offline nicht vor
  (`Network connectivity is disabled … scipy-1.18.1-…whl`). Die Prüfsummen legen die Versionen also fest, schützen
  im jetzigen Ablauf aber nicht gegen einen veränderten Zwischenspeicher. Vorschlag: `docs/entscheidungen/D1.md`.

## 6. Abrufwerkzeug `skripte/abruf.py`

27 Prüfungen ohne Netz (`pruefen/d1_test_abruf.py`, lokaler HTTPS-Server mit selbst ausgestelltem Zertifikat):

```
$ uv run -q --offline --python 3.13 --no-project --with-requirements requirements-pruefen.txt python -m pytest -q pruefen/d1_test_abruf.py
..........................                                               [100%]
27 passed
```

Abgedeckt: Sperrliste (Rechner und Unterrechner, Teilwörter), GUGiK-Kartenbilder (GetTile, GetMap, Kachelpfade)
gesperrt und Capabilities erlaubt, nur https und ohne Anmeldedaten, Obergrenze 1000 MB, robots.txt (Disallow,
„Deny“, Crawl-delay, Fehlerstatus sperrt, 404 erlaubt), Befunde nur für genau `/robots.txt` und höchstens 30 Tage
alt, robots.txt nur einmal je Rechner und Tag, jede Anfrage im Protokoll mit Kennung `kiezatlas-krakow`,
Weiterleitung auf fremden Rechner nicht verfolgt, Abbruch bei Übergröße ohne Restdatei, Prüfsummenliste im Format
von `sha256sum -c`.

Neue Befunde legt das Werkzeug unter `kiezatlas-daten/krakow/_robots/<datum>/` ab. Die Befunde der Machbarkeitsprobe
(`kiezatlas-daten/_robots/2026-11-13/`) liest es nur und nutzt sie, wenn sie für `https://<rechner>/robots.txt`
erhoben wurden. Für `mapy.geoportal.gov.pl` (nur `/imap/robots.txt`),
`bdl.stat.gov.pl` und `usluga.zabytek.gov.pl` (Ersatzseiten) holt das Werkzeug beim ersten Abruf die robots.txt neu.
Kein Netzabruf in diesem Paket.
