"""Beispielwelt (fixture: true) für die Ende-zu-Ende-Probe des Fußwegs in einer Wegwerf-PostGIS.

Nur für pruefen/D2_wegwerf_db.sh. Läuft als admin und bricht ab, wenn die Datenbank nicht kiezatlas_wegwerf heißt:
die gemeinsame Datenbank (kiezatlas, Port 55462) wird nie berührt.

Alles ist erfunden und deterministisch (fester Zufallsstartwert), nichts davon ist eine echte Quelle:
- public.stadtteil: zwei Rechtecke „01“, „02“ (Lage um Kraków, damit EPSG:<rechen_srid> passt)
- public.zensus_zelle: 250-m-Gitter über die Stadt plus 500 m Rand, ew erfunden, einige NULL; mit Tabellenkommentar
  (DDL nur hier, in der Wegwerf-Datenbank; die echte Zelltabelle legt die Integration an)
- auswertung.netz_knoten/netz_kante: 50-m-Gitter über die Stadt plus 2 km, dazu eine Insel aus zwei Knoten
- auswertung.einrichtung (kita, schule), gruenflaeche (park, gruenanlage, wald), osm_poi (apotheke, supermarkt),
  haltestelle: je einige Ziele innerhalb und außerhalb der Stadtgrenze
- auswertung.zelle_erreichbar: einige Luftlinie-Zeilen, die die Fußweg-Rechnung nicht anfassen darf

Gibt die Zählungen je Tabelle als Zeilen „zaehlung <tabelle> <n>“ aus (für den Beleg).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import psycopg
from psycopg import sql

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skripte"))
from ort_konfig import RECHEN_SRID  # noqa: E402

DB_NAME = "kiezatlas_wegwerf"
STARTWERT = 20261113
FIXTURE = "Beispieldaten (fixture: true), frei erfunden für die Probe in der Wegwerf-Datenbank, keine Quelle"
# lon/lat der beiden Stadtteile (westlich und östlich 19,95° O)
STADTTEILE = [("01", "I", "Beispiel West", (19.90, 50.04, 19.95, 50.08)),
              ("02", "II", "Beispiel Ost", (19.95, 50.04, 20.00, 50.08))]
ZELLE_M, NETZ_M, NETZ_RAND_M = 250.0, 50.0, 2000.0


def main() -> int:
    rng = np.random.default_rng(STARTWERT)
    with psycopg.connect("") as conn, conn.cursor() as cur:
        cur.execute("SELECT current_database()")
        if cur.fetchone()[0] != DB_NAME:
            raise SystemExit(f"Beispielwelt nur in der Datenbank {DB_NAME} (Wegwerf-PostGIS), Abbruch")
        cur.execute("SELECT count(*) FROM public.stadtteil")
        if cur.fetchone()[0]:
            raise SystemExit("public.stadtteil ist nicht leer: Beispielwelt nur in eine frische Wegwerf-Datenbank")

        for nr, roem, name, (x0, y0, x1, y1) in STADTTEILE:
            cur.execute("INSERT INTO public.stadtteil (nr, roemisch, name, geom) "
                        "VALUES (%s, %s, %s, ST_Multi(ST_MakeEnvelope(%s, %s, %s, %s, 4326)))",
                        (nr, roem, name, x0, y0, x1, y1))
        cur.execute(f"""SELECT ST_XMin(e), ST_YMin(e), ST_XMax(e), ST_YMax(e) FROM
                        (SELECT ST_Extent(ST_Transform(geom, {RECHEN_SRID})) e FROM public.stadtteil) x""")
        sx0, sy0, sx1, sy1 = cur.fetchone()

        # Zellen: Testtabelle mit Kommentar, nur in der Wegwerf-Datenbank. sql/003_zellen.sql legt die echte Tabelle
        # (nur 1-km-Kennungen) schon beim Init an; hier wird sie durch die Testtabelle mit 250-m-Zellen ersetzt.
        cur.execute("DROP TABLE IF EXISTS public.zensus_zelle")
        cur.execute("CREATE TABLE public.zensus_zelle (gitter_id varchar(40) PRIMARY KEY, ew integer, "
                    "geom geometry(Polygon, 4326) NOT NULL)")
        cur.execute(sql.SQL("COMMENT ON TABLE public.zensus_zelle IS {}").format(sql.Literal(FIXTURE)))
        cur.execute("GRANT SELECT ON public.zensus_zelle TO kiezatlas_rechnen")
        cur.execute(f"""
          INSERT INTO public.zensus_zelle (gitter_id, ew, geom)
          SELECT format('fx250_%%s_%%s', g.i, g.j),
                 CASE WHEN (g.i * g.j) %% 17 = 5 THEN NULL
                      WHEN (g.i + g.j) %% 11 = 0 THEN 0
                      ELSE ((g.i * 7 + g.j * 13) %% 23) * 5 + 3 END,
                 ST_Transform(g.geom, 4326)
          FROM ST_SquareGrid(%s, ST_MakeEnvelope(%s, %s, %s, %s, {RECHEN_SRID})) g""",
                    (ZELLE_M, sx0 - 500, sy0 - 500, sx1 + 500, sy1 + 500))

        # Netz: 50-m-Gitter über Stadt plus 2 km, Knoten-IDs ab 1000; Insel aus zwei Knoten weit draußen
        gx0, gy0 = sx0 - NETZ_RAND_M, sy0 - NETZ_RAND_M
        nx = int((sx1 + NETZ_RAND_M - gx0) / NETZ_M) + 1
        ny = int((sy1 + NETZ_RAND_M - gy0) / NETZ_M) + 1
        with cur.copy("COPY auswertung.netz_knoten (id, geom) FROM STDIN") as cp:
            for i in range(nx):
                for j in range(ny):
                    cp.write_row((1000 + i * ny + j, f"SRID={RECHEN_SRID};POINT({gx0 + i * NETZ_M} {gy0 + j * NETZ_M})"))
            for k, dx in ((1, 0.0), (2, 30.0)):
                cp.write_row((k, f"SRID={RECHEN_SRID};POINT({gx0 - 5000 + dx} {gy0 - 5000})"))
        kid = 0
        with cur.copy("COPY auswertung.netz_kante (id, von, nach, laenge_m) FROM STDIN") as cp:
            for i in range(nx):
                for j in range(ny):
                    k = 1000 + i * ny + j
                    if i + 1 < nx:
                        kid += 1
                        cp.write_row((kid, k, k + ny, NETZ_M))
                    if j + 1 < ny:
                        kid += 1
                        cp.write_row((kid, k, k + 1, NETZ_M))
            kid += 1
            cp.write_row((kid, 1, 2, 30.0))

        def punkte(n_innen: int, n_aussen: int) -> list[tuple[float, float, bool]]:
            erg = [(float(rng.uniform(sx0, sx1)), float(rng.uniform(sy0, sy1)), True) for _ in range(n_innen)]
            while len(erg) < n_innen + n_aussen:     # Ring bis 1,5 km außerhalb der Stadt
                x, y = rng.uniform(sx0 - 1500, sx1 + 1500), rng.uniform(sy0 - 1500, sy1 + 1500)
                if not (sx0 <= x <= sx1 and sy0 <= y <= sy1):
                    erg.append((float(x), float(y), False))
            return erg

        def pt(x: float, y: float) -> str:
            return f"SRID={RECHEN_SRID};POINT({x!r} {y!r})"

        for art, n_i, n_a in (("kita", 40, 5), ("schule", 15, 3)):
            for k, (x, y, innen) in enumerate(punkte(n_i, n_a)):
                cur.execute("INSERT INTO auswertung.einrichtung (id, art, quelle, lizenz, in_stadt, geom) "
                            "VALUES (%s, %s, 'Beispieldaten', %s, %s, %s)",
                            (f"fx-{art}-{k:03d}", art, FIXTURE, innen, pt(x, y)))
        for art, n_i, n_a in (("park", 8, 2), ("gruenanlage", 4, 1), ("wald", 2, 0)):
            for k, (x, y, _) in enumerate(punkte(n_i, n_a)):
                s = float(rng.uniform(100, 300))
                cur.execute(f"""INSERT INTO auswertung.gruenflaeche (id, art, flaeche_m2, quelle, lizenz, geom)
                                SELECT %s, %s, round(ST_Area(g)::numeric, 1), 'Beispieldaten', %s, ST_Multi(g)
                                FROM ST_MakeEnvelope(%s, %s, %s, %s, {RECHEN_SRID}) g""",
                            (f"fx-{art}-{k:03d}", art, FIXTURE, x, y, x + s, y + s * 0.7))
        for art, n_i, n_a in (("apotheke", 20, 3), ("supermarkt", 25, 4)):
            for k, (x, y, _) in enumerate(punkte(n_i, n_a)):
                cur.execute("INSERT INTO auswertung.osm_poi (osm_id, art, geom) VALUES (%s, %s, %s)",
                            (f"fx-n{art[:3]}{k:03d}", art, pt(x, y)))
        for k, (x, y, innen) in enumerate(punkte(30, 3)):
            cur.execute("INSERT INTO auswertung.haltestelle (stop_id, name, in_stadt, geom) VALUES (%s, %s, %s, %s)",
                        (f"fx-stop-{k:03d}", f"Beispielhalt {k}", innen, pt(x, y)))
        # Luftlinie-Zeilen, die die Fußweg-Rechnung stehen lassen muss
        cur.execute("""INSERT INTO auswertung.zelle_erreichbar (gitter_id, art, methode, meter, minuten, ziel_id,
                                                               quelle_lizenz)
                       SELECT gitter_id, 'kita', 'luftlinie', 1.0, 0.0, NULL, %s
                       FROM public.zensus_zelle z
                       WHERE EXISTS (SELECT 1 FROM public.stadtteil s WHERE ST_Intersects(s.geom, ST_Centroid(z.geom)))
                       ORDER BY gitter_id LIMIT 10""", (FIXTURE,))
        for t in ("public.stadtteil", "public.zensus_zelle", "auswertung.netz_knoten", "auswertung.netz_kante",
                  "auswertung.einrichtung", "auswertung.gruenflaeche", "auswertung.osm_poi", "auswertung.haltestelle",
                  "auswertung.zelle_erreichbar"):
            cur.execute(f"SELECT count(*) FROM {t}")
            print(f"zaehlung {t} {cur.fetchone()[0]}")
        conn.commit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
