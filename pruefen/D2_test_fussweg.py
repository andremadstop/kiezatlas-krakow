"""Tests für den Fußweg je Zelle (skripte/14b_fussweg.py).

Ohne Datenbank: kleine Netze mit bekannten Wegen, ein Zufallsnetz für „Fußweg ≥ Luftlinie“, Richtwerte mit Herkunft,
Bericht ohne Fremdbezüge, Datenverträge der Fußweg-Dateien (x-odbl, _odbl im Namen).
Mit A5B_DB_TEST=1: Datenbank-Tests, aber nur in der Wegwerf-Datenbank kiezatlas_wegwerf mit der Beispielwelt aus
pruefen/D2_beispielwelt.py (pruefen/D2_wegwerf_db.sh). Gegen jede andere Datenbank brechen sie ab. Alles läuft in
einer Transaktion und endet mit ROLLBACK.

Aufruf: skripte/14b_fussweg.sh test
        pruefen/D2_wegwerf_db.sh        (startet die Wegwerf-PostGIS und ruft die Datenbank-Tests auf)
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
sys.path.insert(0, str(WURZEL / "pruefen"))
from ort_konfig import RECHEN_SRID  # noqa: E402  Rechen-Koordinatensystem aus config/<ort>.yaml

fw = importlib.import_module("14b_fussweg")
WEGWERF_DB = "kiezatlas_wegwerf"


def gitter(nx: int, ny: int, abstand: float = 100.0, x0: float = 0.0, y0: float = 0.0):
    """Rechteckgitter: Knoten-IDs ab 1000, Kanten waagerecht und senkrecht mit Länge = abstand."""
    ii, jj = np.meshgrid(np.arange(nx), np.arange(ny), indexing="ij")
    ids = 1000 + (ii * ny + jj).ravel()
    xy = np.column_stack([x0 + ii.ravel() * abstand, y0 + jj.ravel() * abstand])
    von, nach = [], []
    for i in range(nx):
        for j in range(ny):
            k = 1000 + i * ny + j
            if i + 1 < nx:
                von.append(k), nach.append(k + ny)
            if j + 1 < ny:
                von.append(k), nach.append(k + 1)
    von, nach = np.array(von), np.array(nach)
    return ids, xy, von, nach, np.full(len(von), abstand)


# ------------------------------------------------------------------------------- Netz

def test_gitter_weg_ist_manhattan():
    netz = fw.netz_bauen(*gitter(5, 5))
    meter, ziel = fw.naechstes_ziel(netz, np.array([[400.0, 400.0]]), np.array([[0.0, 0.0], [200.0, 300.0]]))
    assert meter.tolist() == pytest.approx([800.0, 300.0])
    assert ziel.tolist() == [0, 0]


def test_anbindungsstrecken_zaehlen_mit():
    netz = fw.netz_bauen(*gitter(3, 1))         # Knoten bei x = 0, 100, 200 auf y = 0
    meter, _ = fw.naechstes_ziel(netz, np.array([[200.0, 40.0]]), np.array([[0.0, -30.0]]))
    assert meter[0] == pytest.approx(30.0 + 200.0 + 40.0)


def test_mehrere_ziele_naechstes_nach_netz_nicht_nach_luftlinie():
    # Zwei getrennte Straßen, verbunden nur am linken Ende (x = 0): ein Ziel liegt in Luftlinie nah, aber
    # auf der anderen Straße; das andere weiter weg auf derselben Straße.
    ids = np.array([1, 2, 3, 11, 12, 13])
    xy = np.array([[0, 0], [500, 0], [1000, 0], [0, 60], [500, 60], [1000, 60]], dtype=float)
    von, nach = np.array([1, 2, 11, 12, 1]), np.array([2, 3, 12, 13, 11])
    netz = fw.netz_bauen(ids, xy, von, nach, np.array([500, 500, 500, 500, 60.0]))
    ziele = np.array([[1000.0, 60.0], [0.0, 0.0]])  # 0: gegenüber (Luftlinie 60 m), 1: am Anfang derselben Straße
    meter, ziel = fw.naechstes_ziel(netz, ziele, np.array([[1000.0, 0.0]]))
    assert ziel[0] == 1
    assert meter[0] == pytest.approx(1000.0)


def test_kleine_komponente_wird_nicht_angebunden():
    ids, xy, von, nach, laenge = gitter(4, 4)
    ids = np.append(ids, [1, 2])
    xy = np.vstack([xy, [[2000.0, 0.0], [2010.0, 0.0]]])
    von, nach, laenge = np.append(von, 1), np.append(nach, 2), np.append(laenge, 10.0)
    netz = fw.netz_bauen(ids, xy, von, nach, laenge)
    assert netz.gross.sum() == 16
    # Start direkt an der Insel: angebunden wird an den Hauptteil (> MAX_ANBINDUNG_M) → kein Wert
    meter, ziel = fw.naechstes_ziel(netz, np.array([[0.0, 0.0]]), np.array([[2005.0, 0.0]]))
    assert math.isnan(meter[0]) and ziel[0] == -1


def test_zu_weit_vom_netz_kein_wert_und_ziel_ausgelassen():
    netz = fw.netz_bauen(*gitter(3, 3))
    fern = [[0.0, 1000.0]]
    meter, _ = fw.naechstes_ziel(netz, np.array([[200.0, 200.0]]), np.array(fern))
    assert math.isnan(meter[0])
    # Ziel zu weit vom Netz: gilt als nicht erreichbar, das nähere erreichbare zählt
    meter, ziel = fw.naechstes_ziel(netz, np.array([[0.0, 900.0], [200.0, 200.0]]), np.array([[0.0, 0.0]]))
    assert ziel[0] == 1 and meter[0] == pytest.approx(400.0)


def test_parallele_kanten_und_zu_kurze_laenge():
    ids = np.array([1, 2])
    xy = np.array([[0, 0], [100, 0]], dtype=float)
    # doppelt: 150 und 120; dazu eine Länge unter dem geraden Abstand (90 → 100)
    netz = fw.netz_bauen(ids, xy, np.array([1, 2]), np.array([2, 1]), np.array([150.0, 120.0]))
    m, _ = fw.naechstes_ziel(netz, np.array([[100.0, 0.0]]), np.array([[0.0, 0.0]]))
    assert m[0] == pytest.approx(120.0)
    netz = fw.netz_bauen(ids, xy, np.array([1]), np.array([2]), np.array([90.0]))
    m, _ = fw.naechstes_ziel(netz, np.array([[100.0, 0.0]]), np.array([[0.0, 0.0]]))
    assert m[0] == pytest.approx(100.0)


def test_unbekannter_knoten_bricht_ab():
    with pytest.raises(ValueError):
        fw.netz_bauen(np.array([1, 2]), np.zeros((2, 2)), np.array([1]), np.array([3]), np.array([1.0]))


def test_zufallsnetz_fussweg_nie_unter_luftlinie():
    rng = np.random.default_rng(42)
    n = 600
    xy = rng.uniform(0, 3000, size=(n, 2))
    from scipy.spatial import cKDTree
    _, nb = cKDTree(xy).query(xy, k=5)
    von = np.repeat(np.arange(n), 4)
    nach = nb[:, 1:].ravel()
    laenge = np.hypot(*(xy[von] - xy[nach]).T) * rng.uniform(0.98, 1.3, size=len(von))  # auch etwas zu kurz
    netz = fw.netz_bauen(np.arange(n) + 10, xy, von + 10, nach + 10, laenge)
    ziele = rng.uniform(0, 3000, size=(25, 2))
    start = rng.uniform(0, 3000, size=(400, 2))
    meter, ziel = fw.naechstes_ziel(netz, ziele, start, max_anbindung=1e9)
    luft = cKDTree(ziele).query(start)[0]
    ok = np.isfinite(meter)
    assert ok.sum() > 300
    assert np.all(fw.auf_zehntel(meter[ok]) >= luft[ok])
    # Gewähltes Ziel: Fußweg dorthin ist der kleinste über alle Ziele (gegen Einzelrechnung)
    for i in np.flatnonzero(ok)[:20]:
        einzeln = [fw.naechstes_ziel(netz, ziele[j:j + 1], start[i:i + 1], max_anbindung=1e9)[0][0]
                   for j in range(len(ziele))]
        assert meter[i] == pytest.approx(np.nanmin(einzeln))
        assert einzeln[ziel[i]] == pytest.approx(meter[i])


def test_im_radius_gegen_einzelrechnung():
    netz = fw.netz_bauen(*gitter(10, 10))
    zugang = np.array([[0, 0], [900, 900], [450, 0], [0, 450], [900, 0]], dtype=float)
    gruppe = np.array([0, 1, 2, 2, 3])          # Fläche 2 hat zwei Zugänge
    start = np.array([[100, 100], [500, 500], [800, 50], [0, 5000]], dtype=float)
    erg = fw.im_radius(netz, zugang, gruppe, start, radius=500.0, chunk=2)
    for i in range(len(start)):
        if i == 3:
            assert erg[i] is None
            continue
        erwartet = set()
        for g in set(gruppe.tolist()):
            m, _ = fw.naechstes_ziel(netz, zugang[gruppe == g], start[i:i + 1])
            if m[0] <= 500.0:
                erwartet.add(g)
        assert erg[i] == erwartet


def test_aufrunden_und_minuten_und_median():
    assert fw.auf_zehntel(np.array([10.01, 10.0, 0.0]))[:].tolist() == [10.1, 10.0, 0.0]
    assert fw.minuten(np.array([80.0]), 4.8)[0] == pytest.approx(1.0)
    fuss = np.array([120.0, 50.0, 300.0, np.nan])
    luft = np.array([100.0, 40.0, 200.0, 100.0])
    assert fw.median_verhaeltnis(fuss, luft) == pytest.approx(1.35)   # 1,2 und 1,5; 40 m zählt nicht


# ------------------------------------------------------------------------------- Konfiguration und Bericht

def test_richtwerte_aus_dem_repo_mit_herkunft():
    """Fehlen die Werte in config/richtwerte.yaml, gilt der Standard des Skripts, und die Herkunft sagt das."""
    rw = fw.richtwerte()
    for wert, standard in (("kmh", fw.KMH_STANDARD), ("gruen_radius", fw.GRUEN_RADIUS_STANDARD)):
        assert rw[f"{wert}_quelle"].startswith("config/richtwerte.yaml") or rw[wert] == standard
    assert rw["gruen_arten"]
    assert all(rw[f"{w}_quelle"] for w in ("kmh", "gruen_radius", "gruen_arten"))


def test_richtwerte_aus_datei(tmp_path):
    p = tmp_path / "rw.yaml"
    p.write_text("geschwindigkeit_fuss_kmh: {wert: 4.5}\ngruen: {radius_m: {wert: 400}}\n"
                 "gruen_definition: {arten: {park: {zaehlt_vorschlag: true}, wald: {zaehlt_vorschlag: false}}}\n",
                 encoding="utf-8")
    rw = fw.richtwerte(p)
    assert rw["kmh"] == pytest.approx(4.5) and rw["gruen_radius"] == 400 and rw["gruen_arten"] == ("park",)
    assert all(rw[f"{w}_quelle"].startswith("config/richtwerte.yaml") for w in ("kmh", "gruen_radius", "gruen_arten"))
    p.write_text("stand: null\n", encoding="utf-8")
    rw = fw.richtwerte(p)
    assert rw["kmh"] == fw.KMH_STANDARD and rw["kmh_quelle"].startswith("Standard des Skripts")


@pytest.mark.parametrize("name", ["public.zensus_zelle", "auswertung.d4_zelle", "pg_temp.zelle_1"])
def test_tabelle_teilen_gut(name):
    assert ".".join(fw.tabelle_teilen(name)) == name


@pytest.mark.parametrize("name", ["zensus_zelle", "a.b.c", 'public."X"', "public.zelle;drop", "Public.Zelle", ""])
def test_tabelle_teilen_schlecht(name):
    with pytest.raises(SystemExit):
        fw.tabelle_teilen(name)


def _kennzahlen() -> dict:
    return {"netz_schema": "auswertung", "sekunden": 1.0, "knoten": 10, "knoten_gross": 9, "kanten": 12,
            "stadtteile": 18, "zellen_tabelle": "public.zensus_zelle", "zellen_vermerk": "Vermerk der Zellen",
            "zellen": 5, "bewohnt": 4, "ew": 100, "ew_null": 1, "zellen_ohne_anbindung": 0,
            "anbindung_p50": 10.0, "anbindung_p95": 20.0,
            "arten": [fw.ArtErgebnis("kita", 3, 1, 3, 5, 5, 2, 0, 1.3, 400.0)],
            "gruen": {"zeilen": 5, "mit_wert": 5, "ohne_gruen": 1, "median_m2": 1000.0},
            "median_gesamt": 1.3, "kmh": 4.8, "kmh_quelle": "Standard des Skripts, fehlt in config/richtwerte.yaml",
            "gruen_radius": 500, "gruen_radius_quelle": "x", "gruen_arten": ("park",), "gruen_arten_quelle": "y"}


def test_bericht_ohne_fremdbezuege_mit_lizenz_und_aussen():
    text = fw.bericht(_kennzahlen(), trockenlauf=True)
    for verboten in ("Potsdam", "Berlin", "Brandenburg", "VBB", "DHID", "Zensus 2022", "E7", "A5", "A6", "A3"):
        assert verboten not in text, verboten
    assert "ODbL 1.0" in text and "Vermerk der Zellen" in text
    assert "davon außerhalb der Stadtgrenze" in text and "| kita | 3 | 1 |" in text
    assert "Standard des Skripts" in text


def test_kein_landesfilter_und_keine_abrufe_im_code():
    text = (WURZEL / "skripte" / "14b_fussweg.py").read_text(encoding="utf-8").lower()
    for verboten in ("vbb", "berlin", "brandenburg", "dhid", "gtfs_pfad", "halte_land", "land_berlin"):
        assert verboten not in text, verboten
    ohne_lizenz_urls = text.replace("https://opendatacommons.org", "").replace("https://creativecommons.org", "")
    ohne_lizenz_urls = ohne_lizenz_urls.replace("https://gtfs.ztp.krakow.pl/", "")
    for verboten in ("overpass", "osmnx", "requests", "urllib", "http://", "https://", "nominatim", "wikidata"):
        assert verboten not in ohne_lizenz_urls, verboten


def test_vertraege_der_fussweg_dateien_sind_odbl():
    """Jede Datei mit Fußweg-Werten: Vertrag mit x-odbl true und x-datei *_odbl.js; umgekehrt kein Fußweg ohne _odbl."""
    fuss = []
    for p in sorted((WURZEL / "daten" / "schema").glob("*.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        methode = ((s.get("properties") or {}).get("methode") or {}).get("const")
        if methode == "fussweg" or "fuss" in str(s.get("x-datei", "")) or "fussweg" in str(s.get("title", "")):
            fuss.append(p.name)
            assert s.get("x-odbl") is True, p.name
            assert str(s.get("x-datei", "")).endswith("_odbl.js"), p.name
    assert {"erreichbar_fuss_odbl.json", "planer_fuss_odbl.json"} <= set(fuss)


# ------------------------------------------------------------------------------- Datenbank (nur Wegwerf-PostGIS)

DB = os.environ.get("A5B_DB_TEST") == "1"


@pytest.fixture
def cur():
    """Cursor in der Wegwerf-Datenbank; jede andere Datenbank bricht ab. Am Ende ROLLBACK."""
    with fw.verbinden() as conn, conn.cursor() as c:
        c.execute("SELECT current_database()")
        name = c.fetchone()[0]
        if name != WEGWERF_DB or os.environ.get("PGPORT") == "55462":
            pytest.fail(f"Datenbank-Tests nur in {WEGWERF_DB} (Wegwerf-PostGIS), nicht in {name} "
                        f"auf Port {os.environ.get('PGPORT')}")
        yield c
        conn.rollback()


@pytest.mark.skipif(not DB, reason="nur mit A5B_DB_TEST=1 (pruefen/D2_wegwerf_db.sh)")
def test_zelltabelle_fehlt_bricht_ab(cur):
    with pytest.raises(SystemExit, match="to_regclass"):
        fw.zellen_vermerk(cur, "public.gibt_es_nicht")


@pytest.mark.skipif(not DB, reason="nur mit A5B_DB_TEST=1 (pruefen/D2_wegwerf_db.sh)")
def test_zelltabelle_ohne_kommentar_oder_spalten_bricht_ab(cur):
    cur.execute(f"CREATE TEMP TABLE zelle_ohne (gitter_id text, ew int, geom geometry(Point, {RECHEN_SRID}))")
    with pytest.raises(SystemExit, match="Tabellenkommentar"):
        fw.zellen_vermerk(cur, "pg_temp.zelle_ohne")
    cur.execute("CREATE TEMP TABLE zelle_spalte (gitter_id text, geom geometry)")
    cur.execute("COMMENT ON TABLE pg_temp.zelle_spalte IS 'Vermerk'")
    with pytest.raises(SystemExit, match="ew"):
        fw.zellen_vermerk(cur, "pg_temp.zelle_spalte")


@pytest.mark.skipif(not DB, reason="nur mit A5B_DB_TEST=1 (pruefen/D2_wegwerf_db.sh)")
def test_zellen_nach_mittelpunkt_in_der_stadt(cur):
    fw.stadt_anlegen(cur)
    ids, xy, ew, ew_null = fw.zellen_mit_null(cur)
    cur.execute("SELECT count(*) FROM public.zensus_zelle")
    alle = cur.fetchone()[0]
    assert 0 < len(ids) < alle                      # Randzellen der Beispielwelt fallen heraus
    assert len(set(ids)) == len(ids) and ew_null > 0 and (ew == 0).any()
    cur.execute("SELECT count(*) FROM fw_stadt s, unnest(%s::float8[], %s::float8[]) p(x, y) "
                f"WHERE NOT ST_Intersects(s.g, ST_SetSRID(ST_MakePoint(p.x, p.y), {RECHEN_SRID}))",
                (xy[:, 0].tolist(), xy[:, 1].tolist()))
    assert cur.fetchone()[0] == 0


@pytest.mark.skipif(not DB, reason="nur mit A5B_DB_TEST=1 (pruefen/D2_wegwerf_db.sh)")
def test_zellen_laden_fuer_fremde_aufrufer_ohne_fw_stadt(cur):
    """Schnittstelle von skripte/15_planer.py: zellen_laden(cur) ohne stadt_anlegen(), 3 Werte, gleiche Zellen."""
    cur.execute("SELECT to_regclass('pg_temp.fw_stadt')")
    assert cur.fetchone()[0] is None
    ids, xy, ew = fw.zellen_laden(cur)
    fw.stadt_anlegen(cur)
    ids2, xy2, ew2, _ = fw.zellen_mit_null(cur)
    assert ids and ids == ids2 and np.allclose(xy, xy2) and (ew == ew2).all()


@pytest.mark.skipif(not DB, reason="nur mit A5B_DB_TEST=1 (pruefen/D2_wegwerf_db.sh)")
def test_planer_fussweg_zu_mit_echtem_modul(cur):
    """15_planer.fussweg_zu lädt 14b_fussweg.py als Modul (kein Platzhalter wie in A6_test_pfade.py)."""
    spec = importlib.util.spec_from_file_location("d2_planer_probe", WURZEL / "skripte" / "15_planer.py")
    planer = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = planer
    try:
        spec.loader.exec_module(planer)
        werte = planer.fussweg_zu(cur, "art = %s", ("kita",), "kita")
    finally:
        sys.modules.pop(spec.name, None)
        sys.modules.pop("a5b_fussweg", None)
    ids, _, _ = fw.zellen_laden(cur)
    assert set(werte) == set(ids) and len(werte) == len(ids)
    endlich = [m for m in werte.values() if m is not None]
    assert endlich and all(m >= 0 for m in endlich)


@pytest.mark.skipif(not DB, reason="nur mit A5B_DB_TEST=1 (pruefen/D2_wegwerf_db.sh)")
def test_ziele_ausserhalb_zaehlen_mit(cur):
    """OSM-Ziele aus einer TEMP-osm_poi: eines in der Stadt, eines außerhalb; beide bleiben, außerhalb ist gezählt."""
    fw.stadt_anlegen(cur)
    cur.execute(f"CREATE TEMP TABLE osm_poi (osm_id text, art text, unterart text, geom geometry(Point, {RECHEN_SRID}))")
    for oid, lon, lat in (("n1", 19.93, 50.06), ("n2", 20.03, 50.06)):
        cur.execute("INSERT INTO pg_temp.osm_poi VALUES (%s, 'testart', NULL, "
                    f"ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), {RECHEN_SRID}))", (oid, lon, lat))
    zahl = fw.ziele_anlegen(cur, ("park",), poi_schema="pg_temp")
    assert zahl["testart"] == (2, 1)
    cur.execute("SELECT ziel_id, aussen FROM fw_ziel WHERE art = 'testart' ORDER BY 1")
    assert cur.fetchall() == [("n1", False), ("n2", True)]
    cur.execute("SELECT DISTINCT lizenz FROM fw_ziel WHERE herkunft = 'ztp'")
    assert [r[0] for r in cur.fetchall()] == [fw.ZTP]


@pytest.mark.skipif(not DB, reason="nur mit A5B_DB_TEST=1 (pruefen/D2_wegwerf_db.sh)")
def test_probelauf_beispielwelt_rollback(cur):
    abnahme = importlib.import_module("D2_fussweg_pruefen")
    cur.execute("SELECT count(*), sum(meter) FROM auswertung.zelle_erreichbar WHERE methode <> 'fussweg'")
    vorher_fremd = cur.fetchone()
    k = fw.rechnen(cur)
    assert k["zellen"] > 0 and k["bewohnt"] > 0 and k["stadtteile"] == 2
    assert all(a.verstoesse == 0 for a in k["arten"])
    assert any(a.ziele_aussen > 0 for a in k["arten"])
    assert k["knoten_gross"] == k["knoten"] - 2        # Insel aus zwei Knoten bleibt außen vor
    assert 1.1 < k["median_gesamt"] < 1.6              # Manhattan-Gitter: im Mittel 4/π ≈ 1,27
    assert "ODbL" in fw.bericht(k, trockenlauf=True)
    cur.execute("SELECT count(*), sum(meter) FROM auswertung.zelle_erreichbar WHERE methode <> 'fussweg'")
    assert cur.fetchone() == vorher_fremd              # Luftlinie-Zeilen unberührt
    erg = abnahme.pruefen(cur)
    for kr, ok, beleg in erg:
        assert ok, f"{kr}: {beleg}"
