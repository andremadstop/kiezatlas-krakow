"""Grenzen der dzielnice und Zellen des Bevölkerungsgitters in die Datenbank (public.stadtteil, public.zensus_zelle).

Integration, Echtlauf der Daten. Kein Netz. Rechnet dieselben Grenzen und Zellen wie skripte/02_bevoelkerung.py
(Bausteine aus skripte/raum_bevoelkerung.py): Grenzen ungeglättet aus dem OSM-Auszug in $KIEZ_DATEN/eingang/,
Zellen mit Mittelpunkt in einer dzielnica (Mittelpunktregel in EPSG:3035), ew = T des Eurostat-Gitters.

Liest:    $KIEZ_DATEN/eingang/*.osm.pbf, 2026-11-13/03_gebaeude/1261_SHP.zip, 2026-11-13/02_zensus/PL_PD_3035_GPKG.zip
          daten/zellen_odbl.js (nur zum Abgleich: gleiche Zellen, gleiche ew)
Schreibt: public.stadtteil (18 Zeilen), public.zensus_zelle (DDL: sql/001_kiezatlas.sql, sql/003_zellen.sql);
          belege/DE_db_gliederung.md (Zählungen vorher/nachher, Abgleich)
Rolle:    admin (PG*-Umgebung aus skripte/05_db_gliederung.sh). public.* schreibt sonst die Pipeline; für diese zwei
          Tabellen gibt es keine Pipeline-Quelle, darum die Integration.

Aufruf:   skripte/05_db_gliederung.sh laden | pruefen
pruefen:  nichts schreiben; Rückgabe 1, wenn die Datenbank nicht zur Rechnung oder zu daten/zellen_odbl.js passt.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import psycopg
from shapely.geometry import MultiPolygon, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import raum_bevoelkerung as rb  # noqa: E402

WURZEL = rb.WURZEL
BELEG = WURZEL / "belege" / "DE_db_gliederung.md"


def js_lesen(pfad: Path) -> dict:
    t = pfad.read_text(encoding="utf-8")
    m = re.search(r"window\.KIEZ_\w+\s*=\s*", t)
    return json.loads(t[m.end():].rstrip().rstrip(";"))


def rechnen(konfig: dict):
    d = rb.daten_ordner()
    gl = rb.gliederung_laden(konfig)
    if not gl.dzielnice:
        raise SystemExit(f"Grenzen der dzielnice fehlen: {gl.dzielnice_grund}")
    zellen, _info = rb.gitter_lesen(d / rb.GITTER_ZIP, rb.rahmen_3035(gl.stadt.geom))
    m_dz, _a = rb.gitter_zuordnen(zellen, {nr: e.geom for nr, e in gl.dzielnice.items()})
    auswahl = sorted((z for z in zellen if z.gid in m_dz), key=lambda z: z.gid)
    return gl, auswahl


def multi(g) -> MultiPolygon:
    g = rb.nur_flaechen(g)
    return g if isinstance(g, MultiPolygon) else MultiPolygon([g])


def zaehlen(cur) -> dict:
    erg = {}
    for t in ("public.stadtteil", "public.zensus_zelle"):
        cur.execute(f"SELECT count(*) FROM {t}")
        erg[t] = cur.fetchone()[0]
    return erg


def abgleich(cur, konfig, auswahl) -> list[tuple[str, bool, str]]:
    erg = []
    teile = {t["nr"]: t for t in konfig["gliederung"]["teile"]}
    cur.execute("SELECT nr, roemisch, name, ST_IsValid(geom) FROM public.stadtteil ORDER BY nr")
    zeilen = cur.fetchall()
    erg.append(("public.stadtteil: 18 Zeilen mit nr, roemisch, name aus config/krakow.yaml, Geometrie gültig",
                len(zeilen) == 18 and all(teile.get(n) and teile[n]["roemisch"] == r and teile[n]["name"] == na and ok
                                          for n, r, na, ok in zeilen), f"{len(zeilen)} Zeilen"))
    cur.execute("SELECT gitter_id, ew FROM public.zensus_zelle ORDER BY gitter_id")
    db = cur.fetchall()
    rechnung = [(z.gid, z.t) for z in auswahl]
    erg.append(("public.zensus_zelle = Rechnung (gitter_id und ew)", db == rechnung,
                f"{len(db)} Zeilen in der Datenbank, {len(rechnung)} gerechnet"))
    zj = js_lesen(WURZEL / "daten" / "zellen_odbl.js")
    datei = [(f["properties"]["id"], f["properties"]["ew"]) for f in zj["features"]]
    erg.append(("public.zensus_zelle = daten/zellen_odbl.js (gitter_id und ew, gleiche Reihenfolge)", db == datei,
                f"{len(datei)} Zellen in der Datei"))
    # dieselbe Auswahl, die skripte/14b_fussweg.py trifft (Mittelpunkt in EPSG:<rechen_srid> in der Vereinigung)
    cur.execute(f"""SELECT z.gitter_id FROM public.zensus_zelle z,
                      (SELECT ST_Union(ST_MakeValid(ST_Transform(geom, {ort_konfig.RECHEN_SRID}))) g FROM public.stadtteil) s
                    WHERE ST_Intersects(s.g, ST_Centroid(ST_Transform(z.geom, {ort_konfig.RECHEN_SRID})))
                    ORDER BY 1""")
    fw = [r[0] for r in cur.fetchall()]
    erg.append(("Auswahl der Fußweg-Rechnung (Mittelpunkt in EPSG:" + str(ort_konfig.RECHEN_SRID)
                + ") = alle Zellen der Tabelle", fw == [g for g, _ in db], f"{len(fw)} Zellen"))
    cur.execute("SELECT obj_description('public.zensus_zelle'::regclass, 'pg_class')")
    k = cur.fetchone()[0] or ""
    erg.append(("Tabellenkommentar von public.zensus_zelle nennt Eurostat und CC BY 4.0", "Eurostat" in k and "CC BY 4.0" in k,
                f"{len(k)} Zeichen"))
    return erg


def main(argv: list[str]) -> int:
    konfig = ort_konfig.lade()
    pruefen = "--pruefen" in argv
    gl, auswahl = rechnen(konfig)
    with psycopg.connect() as con, con.cursor() as cur:
        vorher = zaehlen(cur)
        if not pruefen:
            cur.execute("TRUNCATE public.stadtteil")
            for t in konfig["gliederung"]["teile"]:
                g = multi(gl.dzielnice[t["nr"]].geom)
                cur.execute("INSERT INTO public.stadtteil (nr, roemisch, name, geom) "
                            "VALUES (%s, %s, %s, ST_Multi(ST_GeomFromText(%s, 4326)))",
                            (t["nr"], t["roemisch"], t["name"], g.wkt))
            cur.execute("TRUNCATE public.zensus_zelle")
            with cur.copy("COPY public.zensus_zelle (gitter_id, ew, geom) FROM STDIN") as cp:
                for z in auswahl:
                    q = Polygon(rb.gitter_quadrat_wgs84(z)["coordinates"][0])
                    cp.write_row((z.gid, z.t, f"SRID=4326;{q.wkt}"))
        nachher = zaehlen(cur)
        regeln = abgleich(cur, konfig, auswahl)
        if pruefen:
            con.rollback()
        else:
            con.commit()
    for text, ok, angabe in regeln:
        print(f"  {'ok   ' if ok else 'FEHLT'} {text}: {angabe}")
    if not pruefen:
        L = ["# Beleg Datenbank: Grenzen der dzielnice und Zellen (erzeugt)", "",
             "Erzeugt von `skripte/05_db_gliederung.py laden` (nicht von Hand ändern); `pruefen` gleicht ohne Schreiben ab.",
             f"Grenzen: `{gl.dzielnice_quelle}`, Datenstand laut Dateikopf {gl.zaehlung.get('dzielnice_stand_osm') or 'nicht angegeben'} "
             "(ungeglättet; die Kartengeometrie in `daten/stadtteile_odbl.js` ist auf 3 m vereinfacht).", "",
             "| Tabelle | Zeilen vorher | Zeilen nachher |", "|---|---|---|"]
        for t in vorher:
            L.append(f"| `{t}` | {vorher[t]} | {nachher[t]} |")
        L += ["", f"Einwohner in den Zellen (Summe `ew`): {sum(z.t or 0 for z in auswahl):,}".replace(",", "."), "",
              "| Abgleich | erfüllt | Angabe |", "|---|---|---|"]
        L += [f"| {t} | {'ja' if ok else 'NEIN'} | {a} |" for t, ok, a in regeln]
        BELEG.write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"belege/{BELEG.name}")
    return 0 if all(ok for _t, ok, _a in regeln) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
