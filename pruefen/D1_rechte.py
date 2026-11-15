"""Prüft Netz, Rollen und Rechte der laufenden Datenbank des Kiezatlas Kraków (geringste Rechte).

Ändert nichts: Alle Schreibproben laufen in Transaktionen, die zurückgerollt werden, und sollen am
Rechtesystem scheitern, bevor eine Zeile entsteht.

Aufruf über skripte/lauf.sh rechte (Umgebung aus .env: POSTGRES_PASSWORD, IMPORT_PASSWORD,
LESE_PASSWORD, RECHNEN_PASSWORD; PGHOST, PGPORT, PGDATABASE). Rückgabe 0, wenn alles stimmt, sonst 1.

Soll (sql/002_ausbau.sql, pipeline.einrichten der Geodaten-Import-Pipeline, docs/rundgang.md „Bau“):
  - Container nur auf 127.0.0.1 veröffentlicht
  - pipeline_import, mosidi_lesen, kiezatlas_rechnen: Anmeldung mit SCRAM-Passwort, keine Sonderrechte
    (SUPERUSER, CREATEROLE, CREATEDB, BYPASSRLS, REPLICATION), in keiner anderen Rolle, besitzen nichts
  - PUBLIC: kein CONNECT, TEMPORARY, CREATE auf der Datenbank, kein CREATE auf public und auswertung
  - keine der drei Rollen darf Schemas oder Tabellen anlegen (CREATE auf Datenbank oder Schema)
  - mosidi_lesen liest nur (kein Schreibrecht, auch nicht spaltenweise, keine TEMP-Tabellen)
  - kiezatlas_rechnen liest public, schreibt Zeilen nur in auswertung
  - pipeline_import schreibt nicht in auswertung, nie TRUNCATE
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import psycopg

ROLLEN = {"pipeline_import": "IMPORT_PASSWORD", "mosidi_lesen": "LESE_PASSWORD",
          "kiezatlas_rechnen": "RECHNEN_PASSWORD"}
SCHEMAS = ("public", "auswertung", "pipeline_meta")
SCHREIBEN = ("INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER")
CONTAINER = "kiezatlas-krakow-db-1"

ergebnisse: list[tuple[bool, str]] = []


def melde(ok: bool, text: str) -> None:
    ergebnisse.append((ok, text))
    print(("OK      " if ok else "FEHLER  ") + text)


def netz() -> None:
    try:
        aus = subprocess.run(["docker", "inspect", "-f", "{{json .HostConfig.PortBindings}}", CONTAINER],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        melde(False, f"docker inspect {CONTAINER} nicht möglich ({e})")
        return
    bindungen = [b for liste in (json.loads(aus) or {}).values() for b in (liste or [])]
    adressen = sorted({b.get("HostIp") or "0.0.0.0" for b in bindungen})
    melde(bool(bindungen) and adressen == ["127.0.0.1"],
          f"Container veröffentlicht nur auf 127.0.0.1 (gefunden: {', '.join(adressen) or 'nichts'}, "
          f"Port {', '.join(sorted({b.get('HostPort', '') for b in bindungen}))})")


def katalog(cur) -> None:
    cur.execute("SHOW password_encryption")
    melde(cur.fetchone()[0] == "scram-sha-256", "password_encryption = scram-sha-256")
    for rolle in ROLLEN:
        cur.execute("""SELECT rolcanlogin, rolsuper, rolcreaterole, rolcreatedb, rolbypassrls, rolreplication,
                              coalesce(rolpassword LIKE 'SCRAM-SHA-256$%%', false)
                       FROM pg_authid WHERE rolname = %s""", (rolle,))
        z = cur.fetchone()
        if z is None:
            melde(False, f"Rolle {rolle} fehlt (skripte/lauf.sh einrichten)")
            continue
        login, *sonder, scram = z
        melde(login and scram, f"{rolle}: Anmeldung mit SCRAM-Passwort")
        melde(not any(sonder), f"{rolle}: keine Sonderrechte (SUPERUSER, CREATEROLE, CREATEDB, BYPASSRLS, "
                               f"REPLICATION)")
        cur.execute("""SELECT string_agg(g.rolname, ', ') FROM pg_auth_members m
                       JOIN pg_roles g ON g.oid = m.roleid JOIN pg_roles r ON r.oid = m.member
                       WHERE r.rolname = %s""", (rolle,))
        mitglied = cur.fetchone()[0]
        melde(mitglied is None, f"{rolle}: in keiner anderen Rolle" + (f" (gefunden: {mitglied})" if mitglied else ""))
        cur.execute("""SELECT (SELECT count(*) FROM pg_class WHERE relowner = r.oid)
                            + (SELECT count(*) FROM pg_namespace WHERE nspowner = r.oid)
                            + (SELECT count(*) FROM pg_proc WHERE proowner = r.oid)
                            + (SELECT count(*) FROM pg_database WHERE datdba = r.oid)
                       FROM pg_roles r WHERE r.rolname = %s""", (rolle,))
        melde(cur.fetchone()[0] == 0, f"{rolle}: besitzt keine Datenbank, kein Schema, keine Tabelle, keine Funktion")
        cur.execute("SELECT has_database_privilege(%s, current_database(), 'CREATE')", (rolle,))
        melde(not cur.fetchone()[0], f"{rolle}: kein CREATE auf der Datenbank")
        for schema in SCHEMAS:
            cur.execute("SELECT has_schema_privilege(%s, %s, 'CREATE')", (rolle, schema))
            melde(not cur.fetchone()[0], f"{rolle}: kein CREATE auf Schema {schema}")

    cur.execute("""SELECT coalesce(string_agg(a.privilege_type, ', '), '')
                   FROM pg_database d, aclexplode(coalesce(d.datacl, acldefault('d', d.datdba))) a
                   WHERE d.datname = current_database() AND a.grantee = 0""")
    public_db = cur.fetchone()[0]
    melde(public_db == "", "PUBLIC: keine Rechte auf der Datenbank" + (f" (gefunden: {public_db})" if public_db else ""))
    for schema in ("public", "auswertung"):
        cur.execute("""SELECT coalesce(string_agg(a.privilege_type, ', '), '')
                       FROM pg_namespace n, aclexplode(coalesce(n.nspacl, acldefault('n', n.nspowner))) a
                       WHERE n.nspname = %s AND a.grantee = 0 AND a.privilege_type = 'CREATE'""", (schema,))
        melde(cur.fetchone()[0] == "", f"PUBLIC: kein CREATE auf Schema {schema}")

    # Rechte je Tabelle (auch Sichten) und Rolle; spaltenweise Rechte zählen mit
    cur.execute("""SELECT n.nspname, c.relname, c.oid FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                   WHERE n.nspname = ANY(%s) AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
                   ORDER BY 1, 2""", (list(SCHEMAS),))
    tabellen = cur.fetchall()
    melde(bool(tabellen), f"{len(tabellen)} Tabellen und Sichten in {', '.join(SCHEMAS)} geprüft")
    verstoesse: dict[str, list[str]] = {r: [] for r in ROLLEN}
    import_public: list[str] = []
    for schema, tabelle, oid in tabellen:
        for rolle in ROLLEN:
            rechte = []
            for recht in SCHREIBEN:
                if recht in ("INSERT", "UPDATE", "REFERENCES"):
                    cur.execute("SELECT has_any_column_privilege(%s, %s, %s)", (rolle, oid, recht))
                else:
                    cur.execute("SELECT has_table_privilege(%s, %s, %s)", (rolle, oid, recht))
                if cur.fetchone()[0]:
                    rechte.append(recht)
            if not rechte:
                continue
            name = f"{schema}.{tabelle} ({', '.join(rechte)})"
            if rolle == "mosidi_lesen":
                verstoesse[rolle].append(name)
            elif rolle == "kiezatlas_rechnen":
                if schema != "auswertung" or set(rechte) - {"INSERT", "UPDATE", "DELETE", "TRUNCATE"}:
                    verstoesse[rolle].append(name)
            else:  # pipeline_import: Schreibrechte vergibt pipeline.einrichten je Ziel der Konfiguration
                if schema == "auswertung" or set(rechte) & {"TRUNCATE", "REFERENCES", "TRIGGER"}:
                    verstoesse[rolle].append(name)
                elif schema == "public":
                    import_public.append(name)
    soll = {"mosidi_lesen": "schreibt nirgends",
            "kiezatlas_rechnen": "schreibt nur Zeilen in auswertung (INSERT, UPDATE, DELETE, TRUNCATE)",
            "pipeline_import": "schreibt nicht in auswertung, kein TRUNCATE, REFERENCES, TRIGGER"}
    for rolle, liste in verstoesse.items():
        melde(not liste, f"{rolle}: {soll[rolle]}" + (f"; Verstöße: {'; '.join(liste)}" if liste else ""))
    print("        pipeline_import schreibt in public (Ziele aus config/krakow.yaml und table_metadata): "
          + ("; ".join(import_public) if import_public else "nichts"))
    cur.execute("SELECT has_database_privilege('mosidi_lesen', current_database(), 'TEMPORARY')")
    melde(not cur.fetchone()[0], "mosidi_lesen: keine TEMP-Tabellen")


def probe(rolle: str, text: str, befehl: str, soll_scheitern: bool) -> None:
    """Befehl als Rolle in einer Transaktion ausführen, danach immer zurückrollen."""
    passwort = os.environ.get(ROLLEN[rolle])
    if not passwort:
        melde(False, f"{rolle}: {ROLLEN[rolle]} fehlt, Probe „{text}“ nicht möglich")
        return
    try:
        with psycopg.connect("", user=rolle, password=passwort, autocommit=False) as conn:
            # Nur eine Rechteverweigerung zählt als „abgewiesen“. Scheitert der Befehl später (etwa an
            # NOT NULL), hat die Rolle das Recht: Das ist bei soll_scheitern ein Fehler.
            fehler, anderer = None, None
            try:
                conn.execute(befehl)
            except psycopg.errors.InsufficientPrivilege as e:
                fehler = e.diag.message_primary
            except psycopg.Error as e:
                anderer = e.diag.message_primary or type(e).__name__
            finally:
                conn.rollback()
    except psycopg.OperationalError as e:
        melde(False, f"{rolle}: Anmeldung gescheitert ({str(e).strip().splitlines()[-1]})")
        return
    if soll_scheitern:
        if fehler:
            melde(True, f"{rolle}: {text} wird abgewiesen ({fehler})")
        else:
            melde(False, f"{rolle}: {text} wird abgewiesen (Recht vorhanden: "
                         + (f"scheiterte erst an „{anderer}“)" if anderer else "lief durch)"))
    else:
        melde(fehler is None and anderer is None, f"{rolle}: {text} geht"
              + (f" (abgewiesen: {fehler or anderer})" if fehler or anderer else ""))


def proben() -> None:
    probe("mosidi_lesen", "SELECT auf auswertung.einrichtung", "SELECT count(*) FROM auswertung.einrichtung", False)
    probe("mosidi_lesen", "CREATE TABLE in public", "CREATE TABLE public.d1_probe (x int)", True)
    probe("mosidi_lesen", "CREATE TEMP TABLE", "CREATE TEMP TABLE d1_probe (x int)", True)
    probe("mosidi_lesen", "INSERT in auswertung.einrichtung", "INSERT INTO auswertung.einrichtung DEFAULT VALUES", True)
    probe("mosidi_lesen", "INSERT in public.stadtteil", "INSERT INTO public.stadtteil DEFAULT VALUES", True)
    probe("kiezatlas_rechnen", "SELECT auf public.stadtteil", "SELECT count(*) FROM public.stadtteil", False)
    probe("kiezatlas_rechnen", "CREATE TEMP TABLE (Zwischenergebnisse)", "CREATE TEMP TABLE d1_probe (x int)", False)
    probe("kiezatlas_rechnen", "CREATE TABLE in auswertung", "CREATE TABLE auswertung.d1_probe (x int)", True)
    probe("kiezatlas_rechnen", "CREATE TABLE in public", "CREATE TABLE public.d1_probe (x int)", True)
    probe("kiezatlas_rechnen", "INSERT in public.stadtteil", "INSERT INTO public.stadtteil DEFAULT VALUES", True)
    probe("kiezatlas_rechnen", "DROP TABLE auswertung.einrichtung", "DROP TABLE auswertung.einrichtung", True)
    probe("kiezatlas_rechnen", "ALTER TABLE auswertung.einrichtung",
          "ALTER TABLE auswertung.einrichtung ADD COLUMN d1_probe int", True)
    probe("pipeline_import", "CREATE TABLE in public", "CREATE TABLE public.d1_probe (x int)", True)
    probe("pipeline_import", "INSERT in auswertung.einrichtung", "INSERT INTO auswertung.einrichtung DEFAULT VALUES", True)
    probe("pipeline_import", "TRUNCATE public.stadtteil", "TRUNCATE public.stadtteil", True)


def main() -> int:
    netz()
    passwort = os.environ.get("POSTGRES_PASSWORD")
    if not passwort:
        melde(False, "POSTGRES_PASSWORD fehlt (.env), Katalog nicht lesbar")
    else:
        with psycopg.connect("", user="admin", password=passwort) as conn, conn.cursor() as cur:
            cur.execute("SELECT current_database(), inet_server_port(), version()")
            db, port, version = cur.fetchone()
            print(f"        Datenbank {db}, Port im Container {port}, {version.split(',')[0]}")
            katalog(cur)
    proben()
    fehler = sum(not ok for ok, _ in ergebnisse)
    print(f"{len(ergebnisse)} Prüfungen, {fehler} Fehler")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
