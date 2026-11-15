"""Fußweg je Zelle zur nächsten Einrichtung je Art, über das OSM-Wegenetz (ODbL).

Eingang (nur lesen):
- auswertung.netz_knoten, auswertung.netz_kante   Fußwegnetz aus skripte/12_osm.py (ODbL 1.0,
                                           © OpenStreetMap-Mitwirkende)
- auswertung.einrichtung, auswertung.gruenflaeche (skripte/11_einrichtungen.py), auswertung.osm_poi
  (skripte/12_osm.py), auswertung.haltestelle (skripte/13_oepnv.py)
- Zellen aus ZELLEN_TABELLE (Standard public.zensus_zelle, sonst --zellen; Spalten gitter_id, ew, geom), alle
  Zellen mit Mittelpunkt in einem der dzielnice (public.stadtteil), darunter die bewohnten (ew > 0). Fehlt die
  Tabelle (to_regclass) oder ihr Tabellenkommentar mit dem Lizenzvermerk, bricht das Skript ab. Welche Zellen
  Kraków bekommt und unter welcher Lizenz, legt das Paket Gliederung und Bevölkerung fest.
- config/richtwerte.yaml   geschwindigkeit_fuss_kmh, gruen.radius_m, gruen_definition.arten (fehlt ein Wert, gilt
  der Standard des Skripts, und der Bericht nennt ihn als solchen)

Ausgang (Rolle kiezatlas_rechnen, nur Zeilen mit methode = 'fussweg'; die Luftlinie-Zeilen bleiben):
- auswertung.zelle_erreichbar   je Zelle und Art: Meter, Minuten, nächstes Ziel
- auswertung.zelle_gruen        je Zelle: Grünfläche, deren Rand in 500 m Fußweg erreichbar ist
- berichte/fussweg.md           Kennzahlen, Prüfung Fußweg ≥ Luftlinie, Median Fußweg/Luftlinie

Rechnung (Python offline, kein pgRouting, kein Netzabruf):
- Ungerichteter Graph aus netz_kante; Kantengewicht = max(laenge_m, gerader Abstand der Endknoten), damit
  Rundungen in laenge_m den Fußweg nie unter die Luftlinie drücken.
- Nur die größte zusammenhängende Komponente zählt. Zellmittelpunkt und Ziel werden je an den nächsten Knoten
  dieser Komponente gebunden (cKDTree); beide Anbindungsstrecken zählen mit. Über MAX_ANBINDUNG_M: kein Wert.
- Je Art eine Dijkstra-Suche mit allen Zielen als Quellen (scipy.sparse.csgraph, min_only). Jedes Ziel hängt als
  eigener Knoten mit seiner Anbindungsstrecke am Netz, so ist der Weg Zelle → Knoten → … → Knoten → Ziel ein
  Streckenzug und damit nie kürzer als die Luftlinie (Dreiecksungleichung).
- Flächen (Grün) werden über Punkte auf ihrem Rand erreicht (ST_Segmentize, Abstand ZUGANG_ABSTAND_M).
- Minuten = Meter / (geschwindigkeit_fuss_kmh · 1000 / 60).

Ziele außerhalb der Stadtgrenze: Alle Ziele zählen, auch in den Nachbargemeinden; einen Landes- oder
Gemeindefilter gibt es nicht. Das OSM-Netz reicht 2 km über die Stadtgrenze (skripte/12_osm.py), weiter entfernte
Ziele kommen über die Anbindungsgrenze nicht in Frage. Stadtgrenze = Vereinigung von public.stadtteil. Der Bericht
nennt je Art, wie viele Ziele außerhalb liegen und für wie viele Zellen das nächste Ziel außerhalb liegt.
Ob amtliche Listen nur das Stadtgebiet abdecken (dann fehlten Ziele jenseits der Grenze), steht im Bericht des
Pakets, das sie lädt.

Lizenz: Jede Fußweg-Zeile ist aus dem OSM-Netz abgeleitet und steht unter ODbL 1.0 (CHECK in sql/002_ausbau.sql).
Veröffentlicht wird sie nur in Dateien mit _odbl im Namen (daten/erreichbar_fuss_odbl.js,
daten/planer_fuss_odbl.js; Verträge daten/schema/*_fuss_odbl.json mit x-odbl), nie in anderen Dateien.

Aufruf über skripte/14b_fussweg.sh (Umgebung und Rolle wie skripte/12_osm.sh):
    skripte/14b_fussweg.sh rechnen [--trockenlauf] [--zellen schema.tabelle]
    skripte/14b_fussweg.sh pruefen [--zellen schema.tabelle]
    skripte/14b_fussweg.sh test
    pruefen/D2_wegwerf_db.sh          Ende-zu-Ende-Probe mit Beispieldaten in einer Wegwerf-PostGIS
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree
sys.path.insert(0, str(Path(__file__).resolve().parent))   # eigener Code; python -I lässt das Skriptverzeichnis weg
from ort_konfig import RECHEN_SRID, RICHTWERTE  # noqa: E402  Rechen-Koordinatensystem aus config/<ort>.yaml

WURZEL = Path(__file__).resolve().parent.parent

MAX_ANBINDUNG_M = 300.0     # Zelle bzw. Ziel weiter vom nächsten Netzknoten: kein Fußwegwert
ZUGANG_ABSTAND_M = 20.0     # Randpunkte von Grünflächen in diesem Abstand
MIN_LUFTLINIE_VERHAELTNIS_M = 100.0   # Median Fußweg/Luftlinie nur über Zellen mit größerer Luftlinie
CHUNK_RADIUS = 16           # Zellen je Dijkstra-Lauf für den Radius (Speicher: CHUNK · Knoten · 8 Byte)
# Standardwerte, solange config/richtwerte.yaml (Paket Versorgung und Takt) sie nicht nennt; der Bericht sagt, woher
# der benutzte Wert kommt. Die Grünarten sind Kategorien von auswertung.gruenflaeche; welche für Kraków als Grün
# zählen, legt config/richtwerte.yaml fest (offen, docs/entscheidungen/D2.md).
KMH_STANDARD = 4.8
GRUEN_RADIUS_STANDARD = 500
GRUEN_ARTEN_STANDARD = ("gruenanlage", "park")

ODBL = "ODbL 1.0, © OpenStreetMap-Mitwirkende (https://opendatacommons.org/licenses/odbl/1-0/)"
NETZ_VERMERK = f"Fußweg über das OSM-Wegenetz: {ODBL}"
# Haltestellen: GTFS der ZTP Kraków, Lizenz laut https://gtfs.ztp.krakow.pl/ („Licencja: Creative Commons (CC BY
# 4.0)“, Befund vom 13.11.2026 in der Machbarkeitsprobe, quellen-D2.md)
ZTP = ("ZTP Kraków (Zarząd Transportu Publicznego), GTFS, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), "
       "Daten verändert (eigene Berechnung)")
# Zellen: Tabelle mit gitter_id, ew, geom (Punkt oder Fläche, gerechnet wird mit dem Mittelpunkt). Der Lizenzvermerk
# steht im Tabellenkommentar (COMMENT ON TABLE), den die Integration mit der Tabelle anlegt; ohne ihn bricht das
# Skript ab. Andere Tabelle: --zellen schema.tabelle.
ZELLEN_TABELLE = "public.zensus_zelle"
BEZEICHNER = re.compile(r"[a-z_][a-z0-9_]*")


# ------------------------------------------------------------------------------- Netz (rein)

@dataclass
class Netz:
    """Ungerichtetes Wegenetz. Indizes 0..n-1, xy in EPSG:<rechen_srid>."""
    xy: np.ndarray                  # (n, 2)
    zeile: np.ndarray               # Kanten beider Richtungen, für den erweiterten Graphen
    spalte: np.ndarray
    gewicht: np.ndarray
    gross: np.ndarray               # bool (n,): Knoten der größten Komponente
    baum: cKDTree = field(repr=False)
    gross_idx: np.ndarray = field(repr=False)   # Index im Netz für jeden Punkt des Baums

    @property
    def n(self) -> int:
        return len(self.xy)


def netz_bauen(knoten_id: np.ndarray, xy: np.ndarray, von: np.ndarray, nach: np.ndarray,
               laenge: np.ndarray) -> Netz:
    """Netz aus Knoten (id, x, y) und Kanten (von, nach, laenge_m) wie in auswertung.netz_*."""
    knoten_id = np.asarray(knoten_id, dtype=np.int64)
    xy = np.asarray(xy, dtype=np.float64).reshape(-1, 2)
    ordnung = np.argsort(knoten_id, kind="stable")
    ids = knoten_id[ordnung]
    if len(ids) and np.any(ids[1:] == ids[:-1]):
        raise ValueError("Knoten-IDs nicht eindeutig")

    def index(werte: np.ndarray) -> np.ndarray:
        werte = np.asarray(werte, dtype=np.int64)
        pos = np.searchsorted(ids, werte)
        pos = np.clip(pos, 0, max(len(ids) - 1, 0))
        if len(werte) and (len(ids) == 0 or np.any(ids[pos] != werte)):
            raise ValueError("Kante verweist auf unbekannten Knoten")
        return ordnung[pos]

    a, b = index(von), index(nach)
    gerade = np.hypot(*(xy[a] - xy[b]).T) if len(a) else np.zeros(0)
    w = np.maximum(np.asarray(laenge, dtype=np.float64), gerade)
    w = np.maximum(w, 1e-3)              # explizite Nullen wären in scipy keine Kante
    behalten = a != b                    # Schleifen tragen nichts bei
    a, b, w = a[behalten], b[behalten], w[behalten]
    # Parallele Kanten: nur die kürzeste (coo → csr würde sie addieren)
    u, v = np.minimum(a, b), np.maximum(a, b)
    o = np.lexsort((w, v, u))
    u, v, w = u[o], v[o], w[o]
    erst = np.ones(len(u), dtype=bool)
    erst[1:] = (u[1:] != u[:-1]) | (v[1:] != v[:-1])
    u, v, w = u[erst], v[erst], w[erst]
    zeile = np.concatenate([u, v])
    spalte = np.concatenate([v, u])
    gewicht = np.concatenate([w, w])
    n = len(xy)
    g = csr_matrix((gewicht, (zeile, spalte)), shape=(n, n))
    if n:
        _, label = connected_components(g, directed=False)
        groesste = np.bincount(label).argmax()
        gross = label == groesste
    else:
        gross = np.zeros(0, dtype=bool)
    gross_idx = np.flatnonzero(gross)
    baum = cKDTree(xy[gross_idx]) if len(gross_idx) else None
    return Netz(xy=xy, zeile=zeile, spalte=spalte, gewicht=gewicht, gross=gross, baum=baum, gross_idx=gross_idx)


def anbinden(netz: Netz, punkte: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Nächster Knoten der größten Komponente und Abstand dorthin, je Punkt."""
    punkte = np.asarray(punkte, dtype=np.float64).reshape(-1, 2)
    if netz.baum is None or len(punkte) == 0:
        return np.zeros(len(punkte), dtype=np.int64), np.full(len(punkte), np.inf)
    d, i = netz.baum.query(punkte)
    return netz.gross_idx[i].astype(np.int64), d


def _erweitert(netz: Netz, ziel_knoten: np.ndarray, ziel_abstand: np.ndarray) -> csr_matrix:
    """Netz plus ein Knoten je Ziel (Index n + j), verbunden mit seinem Netzknoten über die Anbindungsstrecke."""
    t = len(ziel_knoten)
    virt = netz.n + np.arange(t)
    w = np.maximum(ziel_abstand, 1e-3)
    zeile = np.concatenate([netz.zeile, virt, ziel_knoten])
    spalte = np.concatenate([netz.spalte, ziel_knoten, virt])
    gewicht = np.concatenate([netz.gewicht, w, w])
    m = netz.n + t
    return coo_matrix((gewicht, (zeile, spalte)), shape=(m, m)).tocsr()


def naechstes_ziel(netz: Netz, ziel_xy: np.ndarray, start_xy: np.ndarray,
                   max_anbindung: float = MAX_ANBINDUNG_M) -> tuple[np.ndarray, np.ndarray]:
    """Fußweg (m) jeder Startposition zum nächsten Ziel und Index dieses Ziels (−1 = kein Wert)."""
    start_k, start_d = anbinden(netz, start_xy)
    ziel_k, ziel_d = anbinden(netz, ziel_xy)
    meter = np.full(len(start_k), np.nan)
    ziel = np.full(len(start_k), -1, dtype=np.int64)
    ok_ziel = np.flatnonzero(ziel_d <= max_anbindung)
    if len(ok_ziel) == 0 or len(start_k) == 0:
        return meter, ziel
    g = _erweitert(netz, ziel_k[ok_ziel], ziel_d[ok_ziel])
    quellen = netz.n + np.arange(len(ok_ziel))
    dist, _, herkunft = dijkstra(g, directed=True, indices=quellen, min_only=True, return_predecessors=True)
    ok_start = start_d <= max_anbindung
    d_knoten = dist[start_k]
    gueltig = ok_start & np.isfinite(d_knoten)
    j = herkunft[start_k[gueltig]] - netz.n
    # Anbindung 0 m wurde für scipy als 1 mm eingetragen (_erweitert); diesen Zuschlag wieder abziehen
    zuschlag = np.maximum(ziel_d[ok_ziel][j], 1e-3) - ziel_d[ok_ziel][j]
    meter[gueltig] = start_d[gueltig] + d_knoten[gueltig] - zuschlag
    ziel[gueltig] = ok_ziel[j]
    return meter, ziel


def im_radius(netz: Netz, zugang_xy: np.ndarray, zugang_gruppe: np.ndarray, start_xy: np.ndarray,
              radius: float, max_anbindung: float = MAX_ANBINDUNG_M,
              chunk: int = CHUNK_RADIUS) -> list[set[int] | None]:
    """Je Start die Gruppen (z. B. Flächen), von denen ein Zugangspunkt in ≤ radius Fußweg liegt; None = kein Wert."""
    start_k, start_d = anbinden(netz, start_xy)
    zug_k, zug_d = anbinden(netz, zugang_xy)
    ok = np.flatnonzero(zug_d <= max_anbindung)
    zugang_gruppe = np.asarray(zugang_gruppe)[ok]
    g = _erweitert(netz, zug_k[ok], zug_d[ok])
    erg: list[set[int] | None] = [None] * len(start_k)
    rechnen = np.flatnonzero(start_d <= max_anbindung)
    for s in range(0, len(rechnen), chunk):
        teil = rechnen[s:s + chunk]
        # Begrenzung auf den Radius minus Anbindung je Zelle: limit gilt für den ganzen Lauf, also das Maximum
        rest = radius - start_d[teil]
        dist = dijkstra(g, directed=True, indices=start_k[teil], limit=float(max(rest.max(), 0.0)))
        dist = np.atleast_2d(dist)[:, netz.n:]
        for zeile_i, i in enumerate(teil):
            treffer = np.flatnonzero(dist[zeile_i] <= rest[zeile_i])
            erg[i] = {int(x) for x in np.unique(zugang_gruppe[treffer])}
    return erg


def minuten(meter: np.ndarray, kmh: float) -> np.ndarray:
    return np.asarray(meter, dtype=np.float64) / (kmh * 1000.0 / 60.0)


def auf_zehntel(meter: np.ndarray) -> np.ndarray:
    """Aufrunden auf 0,1 m (numeric(10,1)), damit gespeicherter Fußweg nie unter der exakten Luftlinie liegt."""
    return np.ceil(np.asarray(meter, dtype=np.float64) * 10.0 - 1e-9) / 10.0


def median_verhaeltnis(fuss: np.ndarray, luft: np.ndarray, ab_m: float = MIN_LUFTLINIE_VERHAELTNIS_M) -> float | None:
    fuss, luft = np.asarray(fuss, dtype=float), np.asarray(luft, dtype=float)
    m = np.isfinite(fuss) & np.isfinite(luft) & (luft >= ab_m)
    return float(np.median(fuss[m] / luft[m])) if m.any() else None


# ------------------------------------------------------------------------------- Konfiguration

def richtwerte(pfad: Path = RICHTWERTE) -> dict:
    """Gehgeschwindigkeit, Grün-Radius und Grünarten aus config/richtwerte.yaml, je mit Herkunft.

    Fehlt ein Wert in der Datei, gilt der Standard des Skripts, und die Herkunft sagt das (Bericht)."""
    import yaml
    with open(pfad, encoding="utf-8") as f:
        rw = yaml.safe_load(f) or {}
    kmh_roh = rw.get("geschwindigkeit_fuss_kmh")
    if isinstance(kmh_roh, dict):
        kmh_roh = kmh_roh.get("wert")
    radius_roh = ((rw.get("gruen") or {}).get("radius_m") or {}).get("wert")
    arten = (rw.get("gruen_definition") or {}).get("arten")
    if isinstance(arten, dict):
        gruen = tuple(a for a, v in arten.items() if isinstance(v, dict) and v.get("zaehlt_vorschlag") is True)
    else:
        gruen = ()
    standard = "Standard des Skripts, fehlt in config/richtwerte.yaml"
    return {"kmh": float(kmh_roh or KMH_STANDARD),
            "kmh_quelle": "config/richtwerte.yaml (geschwindigkeit_fuss_kmh)" if kmh_roh else standard,
            "gruen_radius": int(radius_roh or GRUEN_RADIUS_STANDARD),
            "gruen_radius_quelle": "config/richtwerte.yaml (gruen.radius_m)" if radius_roh else standard,
            "gruen_arten": gruen or GRUEN_ARTEN_STANDARD,
            "gruen_arten_quelle": "config/richtwerte.yaml (gruen_definition.arten, zaehlt_vorschlag: true)" if gruen
            else standard}


def tabelle_teilen(name: str) -> tuple[str, str]:
    """„schema.tabelle“ in seine Teile; nur einfache Bezeichner (kein Anführungszeichen, kein Punkt im Namen)."""
    teile = name.split(".")
    if len(teile) != 2 or not all(BEZEICHNER.fullmatch(t) for t in teile):
        raise SystemExit(f"Zelltabelle {name!r}: erwartet schema.tabelle aus Kleinbuchstaben, Ziffern und _")
    return teile[0], teile[1]


# ------------------------------------------------------------------------------- Datenbank

def verbinden():
    import psycopg
    if os.environ.get("PGUSER") != "kiezatlas_rechnen":
        raise SystemExit("PGUSER muss kiezatlas_rechnen sein (skripte/14b_fussweg.sh setzt das)")
    return psycopg.connect("")


def stadt_anlegen(cur) -> int:
    """TEMP-Tabelle fw_stadt (eine Zeile: Vereinigung aller dzielnice in EPSG:<rechen_srid>). Gibt ihre Zahl zurück."""
    cur.execute("SELECT count(*) FROM public.stadtteil")
    n = cur.fetchone()[0]
    if n == 0:
        raise SystemExit("public.stadtteil ist leer: erst die Grenzen der dzielnice laden (Paket Gliederung und "
                         "Bevölkerung); ohne sie gibt es weder Zellauswahl noch Stadtgrenze")
    cur.execute("DROP TABLE IF EXISTS pg_temp.fw_stadt")    # nur die eigene TEMP-Tabelle (zweiter Aufruf)
    cur.execute(f"""CREATE TEMP TABLE fw_stadt ON COMMIT DROP AS
                    SELECT ST_Union(ST_MakeValid(ST_Transform(geom, {RECHEN_SRID}))) AS g FROM public.stadtteil""")
    return int(n)


def zellen_vermerk(cur, tabelle: str = ZELLEN_TABELLE) -> str:
    """Prüft, dass die Zelltabelle mit gitter_id, ew, geom da ist, und gibt ihren Lizenzvermerk (Tabellenkommentar)."""
    schema, name = tabelle_teilen(tabelle)
    cur.execute("SELECT to_regclass(%s)::oid", (f"{schema}.{name}",))
    oid = cur.fetchone()[0]
    if oid is None:
        raise SystemExit(f"Zelltabelle {tabelle} gibt es nicht (to_regclass ist NULL). Sie kommt mit dem Paket "
                         "Gliederung und Bevölkerung über die Integration (sql/); andere Tabelle mit --zellen.")
    cur.execute("""SELECT attname FROM pg_attribute WHERE attrelid = %s AND attnum > 0 AND NOT attisdropped""", (oid,))
    spalten = {r[0] for r in cur.fetchall()}
    fehlt = sorted({"gitter_id", "ew", "geom"} - spalten)
    if fehlt:
        raise SystemExit(f"Zelltabelle {tabelle}: Spalten fehlen: {', '.join(fehlt)} (erwartet gitter_id, ew, geom)")
    cur.execute("SELECT obj_description(%s, 'pg_class')", (oid,))
    vermerk = (cur.fetchone()[0] or "").strip()
    if not vermerk:
        raise SystemExit(f"Zelltabelle {tabelle} hat keinen Tabellenkommentar mit Lizenzvermerk (COMMENT ON TABLE). "
                         "Ohne Vermerk wird nichts gerechnet: Jede Fußweg-Zeile muss die Lizenz der Zellen nennen.")
    return vermerk


def zellen_mit_null(cur, tabelle: str = ZELLEN_TABELLE) -> tuple[list[str], np.ndarray, np.ndarray, int]:
    """Zellen, deren Mittelpunkt in der Stadt liegt: IDs, Mittelpunkt, ew (NULL → 0), Zahl der NULL-ew.

    Der Mittelpunkt ist ST_Centroid in EPSG:<rechen_srid> (Punkt oder Fläche). Grenzfälle auf der Linie zählen dazu
    (ST_Intersects), jede Zelle genau einmal, weil gegen die Vereinigung geprüft wird. Die Stadt ist die TEMP-Tabelle
    fw_stadt, wenn stadt_anlegen() sie in dieser Sitzung angelegt hat, sonst dieselbe Vereinigung direkt aus
    public.stadtteil (fremde Aufrufer wie skripte/15_planer.py legen fw_stadt nicht an)."""
    from psycopg import sql
    schema, name = tabelle_teilen(tabelle)
    cur.execute("SELECT to_regclass('pg_temp.fw_stadt') IS NOT NULL")
    stadt = (sql.SQL("fw_stadt") if cur.fetchone()[0] else
             sql.SQL("(SELECT ST_Union(ST_MakeValid(ST_Transform(geom, {srid}))) AS g FROM public.stadtteil)").format(
                 srid=sql.Literal(RECHEN_SRID)))
    cur.execute(sql.SQL("""
        SELECT z.gitter_id::text, ST_X(c), ST_Y(c), z.ew
        FROM {}.{} z, LATERAL ST_Centroid(ST_Transform(z.geom, {srid})) c, {stadt} s
        WHERE ST_Intersects(s.g, c)
        ORDER BY z.gitter_id""").format(sql.Identifier(schema), sql.Identifier(name), srid=sql.Literal(RECHEN_SRID),
                                        stadt=stadt))
    rows = cur.fetchall()
    ids = [r[0] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"Zelltabelle {tabelle}: gitter_id nicht eindeutig")
    xy = np.array([(r[1], r[2]) for r in rows], dtype=np.float64).reshape(-1, 2)
    ew = np.array([r[3] or 0 for r in rows], dtype=np.int64)
    return ids, xy, ew, sum(1 for r in rows if r[3] is None)


def zellen_laden(cur, tabelle: str = ZELLEN_TABELLE) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Schnittstelle für fremde Aufrufer (skripte/15_planer.py, fussweg_zu): (ids, xy, ew) wie bisher, 3 Werte.

    Gleiche Zellauswahl wie die Fußweg-Rechnung (zellen_mit_null); braucht kein stadt_anlegen() vorher."""
    ids, xy, ew, _ = zellen_mit_null(cur, tabelle)
    return ids, xy, ew


def netz_laden(cur, schema: str = "auswertung") -> Netz:
    from psycopg import sql
    cur.execute(sql.SQL("SELECT id, ST_X(geom), ST_Y(geom) FROM {}.netz_knoten").format(sql.Identifier(schema)))
    k = np.array(cur.fetchall(), dtype=np.float64).reshape(-1, 3)
    cur.execute(sql.SQL("SELECT von, nach, laenge_m::float8 FROM {}.netz_kante").format(sql.Identifier(schema)))
    e = np.array(cur.fetchall(), dtype=np.float64).reshape(-1, 3)
    # IDs exakt als int64 (float64 trägt OSM-IDs bis 2^53 verlustfrei)
    return netz_bauen(k[:, 0].astype(np.int64), k[:, 1:], e[:, 0].astype(np.int64), e[:, 1].astype(np.int64), e[:, 2])


def ziele_anlegen(cur, gruen_arten: tuple[str, ...], poi_schema: str = "auswertung") -> dict[str, tuple[int, int]]:
    """TEMP-Tabelle fw_ziel (art, ziel_id, lizenz, geom <rechen_srid>, herkunft, aussen) mit allen Zielen.

    Kein Landes- oder Gemeindefilter: Ziele außerhalb der Stadtgrenze zählen mit (siehe Kopf). aussen = Punkt auf der
    Fläche bzw. der Punkt selbst liegt nicht in fw_stadt. Gibt je Art (Ziele, davon außerhalb) zurück.
    poi_schema: nur für Tests (pg_temp)."""
    from psycopg import sql
    cur.execute("DROP TABLE IF EXISTS pg_temp.fw_ziel")    # nur die eigene TEMP-Tabelle (zweiter Aufruf)
    cur.execute(sql.SQL("""
      CREATE TEMP TABLE fw_ziel ON COMMIT DROP AS
        SELECT art, id AS ziel_id, lizenz, geom::geometry(Geometry, {srid}) AS geom, 'amtlich'::text AS herkunft
          FROM auswertung.einrichtung
        UNION ALL
        SELECT 'gruen', id, lizenz, geom, 'amtlich' FROM auswertung.gruenflaeche WHERE art = ANY(%s)
        UNION ALL
        SELECT art, osm_id, %s, geom, 'osm' FROM {schema}.osm_poi
        UNION ALL
        SELECT 'haltestelle', stop_id, %s, geom, 'ztp' FROM auswertung.haltestelle""").format(
                srid=sql.Literal(RECHEN_SRID), schema=sql.Identifier(poi_schema)), (list(gruen_arten), ODBL, ZTP))
    # nur die eigene TEMP-Tabelle fw_ziel
    cur.execute("ALTER TABLE pg_temp.fw_ziel ADD COLUMN aussen boolean")
    cur.execute("UPDATE pg_temp.fw_ziel z SET aussen = NOT ST_Intersects(s.g, ST_PointOnSurface(z.geom)) "
                "FROM fw_stadt s")
    cur.execute("CREATE INDEX ON fw_ziel USING gist (geom)")
    cur.execute("CREATE INDEX ON fw_ziel (art)")
    cur.execute("ANALYZE fw_ziel")
    cur.execute("SELECT art, count(*), count(*) FILTER (WHERE aussen) FROM fw_ziel GROUP BY art ORDER BY art")
    return {a: (int(n), int(au)) for a, n, au in cur.fetchall()}


def zugaenge_laden(cur, art: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Zugangspunkte je Ziel einer Art: Punkt selbst bzw. Randpunkte der Fläche. (ziel_ids, xy, ziel_nr je Punkt)"""
    cur.execute("SELECT ziel_id FROM fw_ziel WHERE art = %s ORDER BY ziel_id", (art,))
    ids = [r[0] for r in cur.fetchall()]
    cur.execute(f"""
      WITH z AS (SELECT row_number() OVER (ORDER BY ziel_id) - 1 AS nr, geom FROM fw_ziel WHERE art = %s)
      SELECT nr, ST_X(geom), ST_Y(geom) FROM z WHERE GeometryType(geom) = 'POINT'
      UNION ALL
      SELECT nr, ST_X((d).geom), ST_Y((d).geom)
        FROM (SELECT nr, ST_DumpPoints(ST_Segmentize(ST_Boundary(geom), {ZUGANG_ABSTAND_M})) d
              FROM z WHERE GeometryType(geom) <> 'POINT') x""", (art,))
    rows = np.array(cur.fetchall(), dtype=np.float64).reshape(-1, 3)
    return ids, rows[:, 1:], rows[:, 0].astype(np.int64)


def luftlinie(cur, art: str, zellen_ids: list[str]) -> np.ndarray:
    """Exakter Abstand jeder Zelle zum nächsten Ziel der Art (PostGIS, KNN mit Neuprüfung). nan = kein Ziel."""
    cur.execute("""
      SELECT c.gitter_id,
             (SELECT ST_Distance(c.g, z.geom) FROM fw_ziel z WHERE z.art = %s ORDER BY z.geom <-> c.g LIMIT 1)
      FROM fw_zelle c""", (art,))
    d = dict(cur.fetchall())
    return np.array([np.nan if d.get(i) is None else float(d[i]) for i in zellen_ids], dtype=np.float64)


def zellen_temp(cur, ids: list[str], xy: np.ndarray) -> None:
    cur.execute("DROP TABLE IF EXISTS pg_temp.fw_zelle")   # nur die eigene TEMP-Tabelle (zweiter Aufruf)
    cur.execute(f"CREATE TEMP TABLE fw_zelle (gitter_id varchar(40) PRIMARY KEY, g geometry(Point, {RECHEN_SRID})) "
                "ON COMMIT DROP")
    with cur.copy("COPY fw_zelle (gitter_id, g) FROM STDIN") as cp:
        for i, (x, y) in zip(ids, xy.tolist()):
            cp.write_row((i, f"SRID={RECHEN_SRID};POINT({x!r} {y!r})"))


def lizenz_je_art(cur, art: str, zellen: str) -> str:
    cur.execute("SELECT DISTINCT lizenz FROM fw_ziel WHERE art = %s ORDER BY 1", (art,))
    ziele = [r[0] for r in cur.fetchall()]
    return f"{NETZ_VERMERK}; Ziele: " + " | ".join(ziele) + f"; Zellen: {zellen}"


@dataclass
class ArtErgebnis:
    art: str
    ziele: int
    ziele_aussen: int
    zugaenge: int
    zeilen: int
    mit_wert: int
    naechstes_aussen: int
    verstoesse: int
    median: float | None
    p90_meter: float | None


def rechnen(cur, *, netz_schema: str = "auswertung", rw: dict | None = None,
            arten: list[str] | None = None, zellen_tabelle: str = ZELLEN_TABELLE) -> dict:
    """Ganze Rechnung in der offenen Transaktion. Schreibt nur methode = 'fussweg'. Gibt Kennzahlen zurück."""
    rw = rw or richtwerte()
    t0 = time.monotonic()
    netz = netz_laden(cur, netz_schema)
    if netz.n == 0:
        raise SystemExit(f"{netz_schema}.netz_knoten ist leer: erst skripte/12_osm.sh laden mit dem OSM-Auszug")
    z_vermerk = zellen_vermerk(cur, zellen_tabelle)
    n_stadtteile = stadt_anlegen(cur)
    ids, xy, ew, ew_null = zellen_mit_null(cur, zellen_tabelle)
    if not ids:
        raise SystemExit(f"Keine Zelle aus {zellen_tabelle} hat ihren Mittelpunkt in public.stadtteil")
    zellen_temp(cur, ids, xy)
    ziel_zahl = ziele_anlegen(cur, rw["gruen_arten"])
    if arten is None:
        arten = sorted(ziel_zahl)
    _, start_d = anbinden(netz, xy)

    cur.execute("DELETE FROM auswertung.zelle_erreichbar WHERE methode = 'fussweg'")
    cur.execute("DELETE FROM auswertung.zelle_gruen WHERE methode = 'fussweg'")
    je_art: list[ArtErgebnis] = []
    verhaeltnisse = []
    for art in arten:
        ziel_ids, zug_xy, zug_nr = zugaenge_laden(cur, art)
        if not ziel_ids:
            continue
        cur.execute("SELECT ziel_id FROM fw_ziel WHERE art = %s AND aussen", (art,))
        aussen_ids = {r[0] for r in cur.fetchall()}
        meter_roh, zug = naechstes_ziel(netz, zug_xy, xy)
        meter = auf_zehntel(meter_roh)
        luft = luftlinie(cur, art, ids)
        vergleich = np.isfinite(meter) & np.isfinite(luft)
        verstoesse = int(np.sum(meter[vergleich] < luft[vergleich]))
        if verstoesse:
            raise RuntimeError(f"{art}: {verstoesse} Zellen mit Fußweg < Luftlinie, Rechnung abgebrochen")
        med = median_verhaeltnis(meter, luft)
        m = vergleich & (luft >= MIN_LUFTLINIE_VERHAELTNIS_M)
        verhaeltnisse.append(meter[m] / luft[m])
        lz = lizenz_je_art(cur, art, z_vermerk)
        mins = np.round(minuten(meter, rw["kmh"]), 1)
        n_aussen = 0
        with cur.copy("COPY auswertung.zelle_erreichbar (gitter_id, art, methode, meter, minuten, ziel_id, "
                      "quelle_lizenz) FROM STDIN") as cp:
            for i, gid in enumerate(ids):
                if np.isfinite(meter[i]):
                    zid = ziel_ids[zug_nr[zug[i]]]
                    n_aussen += zid in aussen_ids
                    cp.write_row((gid, art, "fussweg", float(meter[i]), float(mins[i]), zid, lz))
                else:
                    cp.write_row((gid, art, "fussweg", None, None, None, lz))
        fin = meter[np.isfinite(meter)]
        je_art.append(ArtErgebnis(art=art, ziele=len(ziel_ids), ziele_aussen=ziel_zahl[art][1], zugaenge=len(zug_xy),
                                  zeilen=len(ids), mit_wert=int(np.isfinite(meter).sum()), naechstes_aussen=n_aussen,
                                  verstoesse=verstoesse, median=med,
                                  p90_meter=float(np.percentile(fin, 90)) if len(fin) else None))

    gruen = None
    if "gruen" in arten and "gruen" in ziel_zahl:
        ziel_ids, zug_xy, zug_nr = zugaenge_laden(cur, "gruen")
        cur.execute("SELECT ziel_id, flaeche_m2::float8 FROM fw_ziel z JOIN auswertung.gruenflaeche g "
                    "ON g.id = z.ziel_id WHERE z.art = 'gruen'")
        flaeche = dict(cur.fetchall())
        fl = np.array([flaeche[z] for z in ziel_ids], dtype=np.float64)
        erreichbar = im_radius(netz, zug_xy, zug_nr, xy, rw["gruen_radius"])
        cur.execute("SELECT DISTINCT lizenz FROM auswertung.gruenflaeche WHERE art = ANY(%s) ORDER BY 1",
                    (list(rw["gruen_arten"]),))
        lz = f"{NETZ_VERMERK}; Flächen: " + " | ".join(r[0] for r in cur.fetchall()) + f"; Zellen: {z_vermerk}"
        werte = []
        with cur.copy("COPY auswertung.zelle_gruen (gitter_id, methode, radius_m, m2_gruen, m2_je_ew, quelle_lizenz) "
                      "FROM STDIN") as cp:
            for gid, s in zip(ids, erreichbar):
                m2 = None if s is None else round(float(fl[list(s)].sum()) if s else 0.0, 1)
                if m2 is not None:
                    werte.append(m2)
                cp.write_row((gid, "fussweg", rw["gruen_radius"], m2, None, lz))
        gruen = {"zeilen": len(ids), "mit_wert": len(werte), "ohne_gruen": sum(1 for w in werte if w == 0),
                 "median_m2": float(np.median(werte)) if werte else None}

    alle = np.concatenate(verhaeltnisse) if verhaeltnisse else np.zeros(0)
    return {
        "knoten": netz.n, "knoten_gross": int(netz.gross.sum()), "kanten": len(netz.zeile) // 2,
        "stadtteile": n_stadtteile, "zellen_tabelle": zellen_tabelle, "zellen_vermerk": z_vermerk,
        "zellen": len(ids), "bewohnt": int((ew > 0).sum()), "ew": int(ew.sum()), "ew_null": ew_null,
        "zellen_ohne_anbindung": int(np.sum(start_d > MAX_ANBINDUNG_M)),
        "anbindung_p50": float(np.median(start_d)) if len(start_d) else None,
        "anbindung_p95": float(np.percentile(start_d, 95)) if len(start_d) else None,
        "arten": je_art, "gruen": gruen,
        "median_gesamt": float(np.median(alle)) if len(alle) else None,
        "kmh": rw["kmh"], "kmh_quelle": rw["kmh_quelle"],
        "gruen_radius": rw["gruen_radius"], "gruen_radius_quelle": rw["gruen_radius_quelle"],
        "gruen_arten": rw["gruen_arten"], "gruen_arten_quelle": rw["gruen_arten_quelle"],
        "netz_schema": netz_schema, "sekunden": round(time.monotonic() - t0, 1),
    }


# ------------------------------------------------------------------------------- Bericht

def zahl(x: float | None, nach: int = 0) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    s = f"{x:,.{nach}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def bericht(k: dict, *, trockenlauf: bool) -> str:
    z = [
        "# Fußweg je Zelle",
        "",
        f"Lauf {dt.datetime.now().strftime('%d.%m.%Y %H:%M')}"
        + (" (Trockenlauf, am Ende ROLLBACK)" if trockenlauf else "")
        + f", Netz aus `{k['netz_schema']}.netz_*`, {zahl(k['sekunden'], 1)} s.",
        "",
        f"Lizenz: Alle Werte sind aus dem OSM-Wegenetz abgeleitet, {ODBL}. Veröffentlichung nur in `*_odbl`-Dateien.",
        "",
        "## Netz und Zellen",
        "",
        (f"- Knoten {zahl(k['knoten'])}, davon in der größten Komponente {zahl(k['knoten_gross'])} "
         f"({zahl(100 * k['knoten_gross'] / max(k['knoten'], 1), 1)} %); Kanten {zahl(k['kanten'])}"),
        (f"- Zellen aus `{k['zellen_tabelle']}` mit Mittelpunkt in einem der {zahl(k['stadtteile'])} Stadtteile "
         f"(`public.stadtteil`): {zahl(k['zellen'])}, davon bewohnt (ew > 0) {zahl(k['bewohnt'])} mit zusammen "
         f"{zahl(k['ew'])} Einwohnern; ew leer (als 0 gezählt): {zahl(k['ew_null'])}"),
        f"- Lizenzvermerk der Zellen (Tabellenkommentar): {k['zellen_vermerk']}",
        (f"- Anbindung Zellmittelpunkt → Netzknoten: Median {zahl(k['anbindung_p50'], 1)} m, "
         f"95 % ≤ {zahl(k['anbindung_p95'], 1)} m; über {zahl(MAX_ANBINDUNG_M)} m (kein Wert): "
         f"{zahl(k['zellen_ohne_anbindung'])} Zellen"),
        f"- Gehgeschwindigkeit {zahl(k['kmh'], 1)} km/h ({k['kmh_quelle']})",
        "",
        "## Je Art",
        "",
        ("| Art | Ziele | davon außerhalb der Stadtgrenze | Zugangspunkte | Zellen mit Wert | nächstes Ziel außerhalb "
         "| Fußweg < Luftlinie | Median Fußweg/Luftlinie | 90 % ≤ m |"),
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for a in k["arten"]:
        z.append(f"| {a.art} | {zahl(a.ziele)} | {zahl(a.ziele_aussen)} | {zahl(a.zugaenge)} | "
                 f"{zahl(a.mit_wert)} von {zahl(a.zeilen)} | {zahl(a.naechstes_aussen)} | {a.verstoesse} | "
                 f"{zahl(a.median, 2)} | {zahl(a.p90_meter)} |")
    med = k["median_gesamt"]
    z += ["",
          f"Median Fußweg/Luftlinie über alle Arten (Luftlinie ≥ {zahl(MIN_LUFTLINIE_VERHAELTNIS_M)} m): "
          f"**{zahl(med, 2)}**"
          + ("" if med is None or 1.1 <= med <= 1.6 else " (außerhalb 1,1 bis 1,6: Ursache prüfen)"),
          ""]
    if k["gruen"]:
        g = k["gruen"]
        z += ["## Grün im Fußweg-Umkreis",
              "",
              f"- Flächen: {', '.join(k['gruen_arten'])} ({k['gruen_arten_quelle']})",
              f"- Radius {zahl(k['gruen_radius'])} m ({k['gruen_radius_quelle']})",
              f"- Zugang über Randpunkte im Abstand von {zahl(ZUGANG_ABSTAND_M)} m",
              (f"- Zellen mit Wert {zahl(g['mit_wert'])} von {zahl(g['zeilen'])}; ohne erreichbare Fläche "
               f"in {zahl(k['gruen_radius'])} m: {zahl(g['ohne_gruen'])}; Median {zahl(g['median_m2'])} m²"),
              ("- `m2_je_ew` bleibt leer: Fläche je Einwohner teilt jede Fläche auf alle Einwohner ihres "
               "Einzugsbereichs auf; das rechnet das Paket Versorgung je Raumeinheit, nicht je Zelle."),
              ""]
    z += ["## Methode",
          "",
          "- Graph aus `netz_kante`, ungerichtet; Gewicht = max(`laenge_m`, gerader Abstand der Endknoten).",
          ("- Nur die größte zusammenhängende Komponente. Zelle und Ziel hängen je am nächsten Knoten, beide "
           "Anbindungsstrecken zählen mit. Damit ist jeder Fußweg ein Streckenzug von der Zelle zum Ziel und nie "
           "kürzer als die Luftlinie."),
          ("- Je Art eine Dijkstra-Suche mit allen Zielen als Quellen (scipy). Ziele außerhalb der Stadtgrenze "
           "(Vereinigung von `public.stadtteil`) zählen mit, ohne Landes- oder Gemeindefilter; das Netz reicht 2 km "
           "über die Stadtgrenze (`skripte/12_osm.py`)."),
          "- Meter auf 0,1 m aufgerundet, Minuten = Meter / (km/h · 1000 / 60).",
          "",
          "## Grenzen",
          "",
          ("- Amtliche Ziellisten (Einrichtungen, Grün, Haltestellen) decken womöglich nur das Stadtgebiet ab; dann "
           "fehlen Ziele jenseits der Grenze, und Randzellen bekommen zu lange Wege. Das prüft das Paket, das die "
           "Liste lädt (nicht hier geprüft)."),
          "- Nicht geprüft: Begehbarkeit einzelner Wege (Zugangsbeschränkungen, Treppen, Barrierefreiheit).",
          ""]
    return "\n".join(z)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trockenlauf", action="store_true", help="alles rechnen, am Ende ROLLBACK")
    ap.add_argument("--bericht", type=Path, default=WURZEL / "berichte" / "fussweg.md")
    ap.add_argument("--zellen", default=ZELLEN_TABELLE,
                    help=f"Zelltabelle schema.tabelle mit gitter_id, ew, geom und Lizenz im Kommentar "
                         f"(Standard {ZELLEN_TABELLE})")
    args = ap.parse_args()
    with verbinden() as conn, conn.cursor() as cur:
        k = rechnen(cur, zellen_tabelle=args.zellen)
        text = bericht(k, trockenlauf=args.trockenlauf)
        if args.trockenlauf:
            conn.rollback()
        else:
            conn.commit()
    args.bericht.parent.mkdir(parents=True, exist_ok=True)
    args.bericht.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
