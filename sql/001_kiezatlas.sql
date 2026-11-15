-- Kiezatlas Kraków: Zieltabellen der Geodaten-Import-Pipeline (public.*). Die Pipeline schreibt hinein,
-- die Auswertung liest daraus. Alles in EPSG:4326 (Vorgabe der Pipeline, ziel.ZIEL_SRID).
--
-- Stand: Gerüst. Hier steht nur, was nach der Machbarkeitsprobe feststeht. Die Tabellen der übrigen
-- Quellen (Bevölkerungsgitter 2021, NSP 2021 je rejon statystyczny, BDOT10k-Gebäude, LoD1/LoD2, Denkmale,
-- GTFS) legt die Integration an, sobald das jeweilige Paket die Spalten aus dem Handdownload belegt hat.
-- DDL schreibt nur die Integration (docs/rundgang.md, „Bau“); Pakete schreiben nur Zeilen.
-- Wird von docker-entrypoint-initdb.d nur beim ersten Start eines leeren Volumes ausgeführt.
CREATE EXTENSION IF NOT EXISTS postgis;

-- 18 dzielnice. Arbeitsgrundlage sind die Grenzen aus OpenStreetMap (ODbL 1.0, © OpenStreetMap-Mitwirkende),
-- weil die Lizenz des städtischen Datensatzes (MSIP) ungeklärt ist (docs/entscheidungen.md, KR3).
-- nr = „01“ … „18“, roemisch = amtliche Zählung I … XVIII (KR2).
CREATE TABLE stadtteil (
    nr        varchar(4) PRIMARY KEY CHECK (nr ~ '^[0-9]{2}$'),
    roemisch  varchar(6) NOT NULL,
    name      varchar(80) NOT NULL,
    geom      geometry(MultiPolygon, 4326) NOT NULL
);
COMMENT ON TABLE stadtteil IS 'ODbL 1.0, © OpenStreetMap-Mitwirkende (Grenzen der dzielnice). Ableitungen mit Geometrie nur in *_odbl-Dateien.';

CREATE INDEX ON stadtteil USING gist (geom);
