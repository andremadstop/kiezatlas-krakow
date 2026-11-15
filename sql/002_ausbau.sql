-- Kiezatlas Kraków: Schema auswertung, Zieltabellen der Rechenschritte, Rollenrechte.
-- Gerüst aus dem Kiezatlas Potsdam: Struktur und Lizenz-CHECKs übernommen (Fußweg ⇒ ODbL), Potsdamer
-- Quelltabellen (Zensus 2022, MBJS, ALKIS) und die Tabellen der Bauzeiten-Kaskade entfernt (die Kaskade
-- entfällt mangels offener Baujahre, docs/entscheidungen.md, KR4).
--
-- DDL schreibt nur die Integration; alle Pakete schreiben Zeilen in ihre eigenen Tabellen (Eigentümer je
-- Tabelle im COMMENT und in docs/rundgang.md, „Bau“). Neue Tabellen als Vertragsänderung über die Integration.
--
-- Einspielen als admin (auch bei bestehendem Volume, docker-entrypoint-initdb.d greift dann nicht):
--   skripte/ausbau_einrichten.py   (spielt diese Datei ein und setzt das Passwort der Rolle
--                                   kiezatlas_rechnen aus RECHNEN_PASSWORD als SCRAM-Hash)
-- Die Datei läuft beliebig oft (IF NOT EXISTS); sie ändert keine bestehende Tabelle aus 001.
--
-- Bezugssysteme: public.* in EPSG:4326 (Vorgabe der Geodaten-Import-Pipeline, ziel.ZIEL_SRID),
-- auswertung.* in EPSG:2178 = rechen_srid aus config/krakow.yaml (metrisch, für Abstände und Flächen).
-- pruefen/geruest.py prüft, dass jede metrische SRID hier gleich rechen_srid ist.
--
-- Rollen:
--   pipeline_import  schreibt public-Ziele aus config/krakow.yaml (Rechte vergibt pipeline.einrichten)
--   mosidi_lesen     liest public und auswertung, schreibt nichts
--   kiezatlas_rechnen  liest public, schreibt Zeilen in auswertung (kein CREATE, ALTER, DROP:
--                      Zwischenergebnisse in TEMP-Tabellen). Passwort: RECHNEN_PASSWORD in .env.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA IF NOT EXISTS auswertung AUTHORIZATION admin;
COMMENT ON SCHEMA auswertung IS 'Abgeleitete Zwischenergebnisse des Kiezatlas-Ausbaus DDL nur aus sql/002_ausbau.sql (Integration).';

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'kiezatlas_rechnen') THEN
        CREATE ROLE kiezatlas_rechnen NOLOGIN;
    END IF;
END $$;

-- ================================================================================= auswertung

-- Einrichtungen (amtliche Listen, sonst BDOT10k/OSM nur als Lage). Eigentümer: Paket Versorgung und Takt (D6).
-- art: Liste der Arten (żłobek, przedszkole, Schulformen …) legt D6 in config/richtwerte.yaml fest.
-- status: 'kapazitaet' (Plätze bzw. Schüler bekannt) oder 'lage_ohne_kapazitaet'
CREATE TABLE IF NOT EXISTS auswertung.einrichtung (
    id              text PRIMARY KEY,
    art             text NOT NULL,
    unterart        text,
    name            text,
    plaetze         integer,
    schueler        integer,
    schueler_stand  text,
    altersstruktur  text,
    status          text NOT NULL DEFAULT 'kapazitaet' CHECK (status IN ('kapazitaet', 'lage_ohne_kapazitaet')),
    quelle          text NOT NULL,
    lizenz          text NOT NULL,
    stand           date,
    in_stadt      boolean NOT NULL,
    geom            geometry(Point, 2178) NOT NULL
);
COMMENT ON TABLE auswertung.einrichtung IS 'D6 (skripte/11_einrichtungen.py). Keine Telefon-, Fax- oder E-Mail-Spalte. Lizenz je Zeile (Spalte lizenz).';

-- Grünflächen, D6 (Definition in config/richtwerte.yaml, Abschnitt gruen_definition)
CREATE TABLE IF NOT EXISTS auswertung.gruenflaeche (
    id          text PRIMARY KEY,
    art         text NOT NULL,
    bez         text,
    flaeche_m2  numeric(14,1) NOT NULL,
    quelle      text NOT NULL,
    lizenz      text NOT NULL,
    geom        geometry(MultiPolygon, 2178) NOT NULL
);
COMMENT ON TABLE auswertung.gruenflaeche IS 'D6 (skripte/11_einrichtungen.py). Lizenz je Zeile (Spalte lizenz), Daten verändert (eigene Berechnung).';

-- OSM-Einrichtungen (D2), ohne Namen (Ärzte, Apotheken, Märkte, Pflege, Spielplätze)
CREATE TABLE IF NOT EXISTS auswertung.osm_poi (
    osm_id    text PRIMARY KEY,
    art       text NOT NULL,
    unterart  text,
    geom      geometry(Point, 2178) NOT NULL
);
COMMENT ON TABLE auswertung.osm_poi IS 'ODbL 1.0, © OpenStreetMap-Mitwirkende. D2 (skripte/12_osm.py). Keine Spalte name. Ableitungen nur in *_odbl-Dateien.';

-- Fußwegnetz aus dem OSM-Auszug, offline (D2)
CREATE TABLE IF NOT EXISTS auswertung.netz_knoten (
    id    bigint PRIMARY KEY,
    geom  geometry(Point, 2178) NOT NULL
);
COMMENT ON TABLE auswertung.netz_knoten IS 'ODbL 1.0, © OpenStreetMap-Mitwirkende. D2 (skripte/12_osm.py).';
CREATE TABLE IF NOT EXISTS auswertung.netz_kante (
    id        bigint PRIMARY KEY,
    von       bigint NOT NULL,
    nach      bigint NOT NULL,
    laenge_m  numeric(10,2) NOT NULL,
    geom      geometry(LineString, 2178)
);
COMMENT ON TABLE auswertung.netz_kante IS 'ODbL 1.0, © OpenStreetMap-Mitwirkende. D2 (skripte/12_osm.py).';

-- Haltestellen mit Taktklasse (Klassengrenzen wie Potsdam, config/richtwerte.yaml; D6)
CREATE TABLE IF NOT EXISTS auswertung.haltestelle (
    stop_id                  text PRIMARY KEY,
    name                     text,
    verkehrsmittel           text,
    fahrten_hvz_je_richtung  numeric(6,1),
    klasse                   text CHECK (klasse IN ('I', 'II', 'III', 'unter III')),
    in_stadt               boolean,
    geom                     geometry(Point, 2178) NOT NULL
);
COMMENT ON TABLE auswertung.haltestelle IS 'D6 (skripte/13_oepnv.py). GTFS der ZTP Kraków, Lizenz laut QUELLEN.md, Daten verändert (eigene Berechnung).';

-- D6: Entfernung je Zelle zur nächsten Einrichtung je Art. Zeilen mit methode = fussweg: ODbL.
CREATE TABLE IF NOT EXISTS auswertung.zelle_erreichbar (
    gitter_id      varchar(40) NOT NULL,
    art            text NOT NULL,
    methode        text NOT NULL CHECK (methode IN ('luftlinie', 'fussweg')),
    meter          numeric(10,1),
    minuten        numeric(6,1),
    ziel_id        text,
    quelle_lizenz  text NOT NULL,
    PRIMARY KEY (gitter_id, art, methode),
    CHECK (methode <> 'fussweg' OR quelle_lizenz ILIKE '%ODbL%')
);
COMMENT ON TABLE auswertung.zelle_erreichbar IS 'D6 (skripte/14_erreichbarkeit.py). Luftlinie: Lizenz je Quelle. Fußweg: ODbL 1.0 (OSM-Netz).';

-- D6: Grün je Zelle (eigene Tabelle statt Spalte in zelle_erreichbar)
CREATE TABLE IF NOT EXISTS auswertung.zelle_gruen (
    gitter_id      varchar(40) NOT NULL,
    methode        text NOT NULL CHECK (methode IN ('luftlinie', 'fussweg')),
    radius_m       integer NOT NULL,
    m2_gruen       numeric(14,1),
    m2_je_ew       numeric(10,2),
    quelle_lizenz  text NOT NULL,
    PRIMARY KEY (gitter_id, methode, radius_m),
    CHECK (methode <> 'fussweg' OR quelle_lizenz ILIKE '%ODbL%')
);
COMMENT ON TABLE auswertung.zelle_gruen IS 'D6 (skripte/14_erreichbarkeit.py). Grünfläche im Umkreis je Zelle (Definition: config/richtwerte.yaml). Luftlinie: Lizenz je Quelle. Fußweg: ODbL 1.0 (OSM-Netz).';

-- ===================================================================================== Rechte
-- Nach pipeline.einrichten --haerten hat PUBLIC kein CONNECT mehr: jede Rolle braucht es ausdrücklich.
DO $$ BEGIN
    EXECUTE format('GRANT CONNECT, TEMPORARY ON DATABASE %I TO kiezatlas_rechnen', current_database());
END $$;
REVOKE CREATE ON SCHEMA auswertung FROM PUBLIC;
GRANT USAGE ON SCHEMA public, auswertung TO kiezatlas_rechnen;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO kiezatlas_rechnen;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA auswertung TO kiezatlas_rechnen;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA auswertung TO kiezatlas_rechnen;

DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'mosidi_lesen') THEN
        GRANT USAGE ON SCHEMA auswertung TO mosidi_lesen;
        GRANT SELECT ON ALL TABLES IN SCHEMA auswertung TO mosidi_lesen;
    END IF;
END $$;
