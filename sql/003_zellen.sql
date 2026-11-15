-- Kiezatlas Kraków: Zelltabelle des Bevölkerungsgitters (Eurostat, Census 2021 population grid, 1 km).
-- Integration (Echtlauf der Daten, 13.11.2026). DDL nur hier; die Zeilen schreibt skripte/05_db_gliederung.py
-- als admin aus derselben Rechnung wie daten/zellen_odbl.js (skripte/02_bevoelkerung.py, gleiche Zellen, gleiche ew).
--
-- Leser: skripte/14b_fussweg.py (ZELLEN_TABELLE = public.zensus_zelle, Spalten gitter_id, ew, geom) liest den
-- Lizenzvermerk aus dem Tabellenkommentar und bricht ohne ihn ab (docs/entscheidungen.md, KR16).
-- Die Datei läuft beliebig oft (IF NOT EXISTS); Einspielen als admin, z. B.
--   docker exec -i kiezatlas-krakow-db-1 psql -U admin -d kiezatlas -v ON_ERROR_STOP=1 < sql/003_zellen.sql
-- Bezugssystem: public.* in EPSG:4326 (Vorgabe der Geodaten-Import-Pipeline); die Quadrate sind aus EPSG:3035
-- umgerechnet (vier Ecken), gerechnet wird mit dem Mittelpunkt in EPSG:2178 (rechen_srid).

CREATE TABLE IF NOT EXISTS public.zensus_zelle (
    gitter_id  varchar(40) PRIMARY KEY CHECK (gitter_id ~ '^CRS3035RES1000mN[0-9]+E[0-9]+$'),
    ew         integer CHECK (ew IS NULL OR ew >= 0),
    geom       geometry(Polygon, 4326) NOT NULL
);
COMMENT ON TABLE public.zensus_zelle IS 'Eurostat, Census 2021 population grid, 1 km (CC BY 4.0, https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution). Auswahl der Zellen: Mittelpunkt in der Stadtgrenze (BDOT10k/PRG, gmina 1261011); dieselben IDs wie über die Grenzen der dzielnice (geprüft in skripte/02_bevoelkerung.py). Zuordnung zur dzielnica (© OpenStreetMap-Mitwirkende, ODbL 1.0) nur in *_odbl-Dateien.';
CREATE INDEX IF NOT EXISTS zensus_zelle_geom_idx ON public.zensus_zelle USING gist (geom);

GRANT SELECT ON public.zensus_zelle TO kiezatlas_rechnen;
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'mosidi_lesen') THEN
        GRANT SELECT ON public.zensus_zelle TO mosidi_lesen;
    END IF;
END $$;
