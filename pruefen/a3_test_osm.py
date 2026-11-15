"""Tests für skripte/osm_pbf.py und skripte/12_osm.py mit einer selbst erzeugten Mini-PBF (Beispieldaten).

Aufruf: skripte/12_osm.sh test            (ohne Datenbank)
        A3_DB_TEST=1 skripte/12_osm.sh test   (dazu Trockenlauf gegen die Datenbank, am Ende ROLLBACK)
"""
from __future__ import annotations

import hashlib
import importlib
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
sys.path.insert(0, str(WURZEL / "pruefen"))
import a3_pbf_schreiben as mini
import osm_pbf

osm = importlib.import_module("12_osm")
RECHTECK = (19.8, 49.95, 20.1, 50.15)


@pytest.fixture(scope="module")
def pbf(tmp_path_factory) -> Path:
    return mini.schreiben(tmp_path_factory.mktemp("a3") / "mini.osm.pbf")


@pytest.fixture(scope="module")
def erg(pbf):
    return osm.lies_osm(pbf, RECHTECK)


# ------------------------------------------------------------------------------- Leser

def test_varints_wie_reines_python():
    rng = np.random.default_rng(5)
    werte = list(rng.integers(0, 2**62, 500)) + [0, 1, 127, 128, 300, 2**63 + 5]
    neg = [-1, -300, -(2**31)]   # int32 negativ: 10 Byte Zweierkomplement
    roh = b"".join(mini._varint(int(v)) for v in werte + neg)
    a = osm_pbf.varints(roh)
    assert a.tolist()[: len(werte)] == [int(v) for v in werte]
    assert osm_pbf.als_int64(a)[len(werte):].tolist() == neg
    zz = [0, -1, 1, -2, 2**40, -(2**40)]
    assert osm_pbf.zigzag(osm_pbf.varints(b"".join(mini._varint(mini._zz(v)) for v in zz))).tolist() == zz


def test_kopf_und_zaehler(erg):
    assert erg.kopf.zeitstempel == 1_793_836_800
    assert "DenseNodes" in erg.kopf.pflicht
    assert erg.knoten_gesamt == len(mini.KNOTEN)
    assert erg.wege_gesamt == len(mini.WEGE)
    assert erg.relationen_gesamt == len(mini.RELATIONEN)


def test_koordinaten_exakt(erg):
    ids = np.array(sorted(i for i in mini.KNOTEN if i not in (31, 99)), dtype=np.int64)
    lon, lat, ok = erg.koordinaten(ids)
    assert ok.all()
    soll = np.array([mini.KNOTEN[i][:2] for i in ids])
    assert np.abs(lon - soll[:, 0]).max() < 1e-7 and np.abs(lat - soll[:, 1]).max() < 1e-7
    _lo, _la, ok_aus = erg.koordinaten(np.array([31, 99, 123456]))
    assert not ok_aus.any()                          # außerhalb des Rechtecks bzw. unbekannt


def test_kompression_unbekannt(tmp_path):
    b = mini.feld_bytes(7, b"abc")                   # zstd
    h = mini.feld_bytes(1, b"OSMData") + mini.feld_varint(3, len(b))
    p = tmp_path / "zstd.pbf"
    p.write_bytes(len(h).to_bytes(4, "big") + h + b)
    with pytest.raises(ValueError, match="zstd"):
        list(osm_pbf.bloecke(p))


# ------------------------------------------------------------------------------- Regeln

@pytest.mark.parametrize("tags, soll", [
    ({"highway": "residential"}, True),
    ({"highway": "footway"}, True),
    ({"highway": "steps"}, True),
    ({"highway": "cycleway"}, False),
    ({"highway": "cycleway", "foot": "designated"}, True),
    ({"highway": "motorway"}, False),
    ({"highway": "trunk", "motorroad": "yes"}, False),
    ({"highway": "service", "access": "private"}, False),
    ({"highway": "service", "access": "private", "foot": "yes"}, True),
    ({"highway": "primary", "foot": "use_sidepath"}, False),
    ({"highway": "construction"}, False),
    ({"building": "yes"}, False),
])
def test_fussweg(tags, soll):
    assert osm.ist_fussweg(tags) is soll


def test_poi_art_ohne_namen():
    assert osm.poi_art({"amenity": "doctors", "name": "Dr. X", "healthcare:speciality": "paediatrics"}) == \
        ("arzt", "paediatrics")
    assert osm.poi_art({"healthcare": "doctor"}) == ("arzt", None)
    assert osm.poi_art({"amenity": "social_facility", "social_facility": "food_bank"}) is None
    assert osm.poi_art({"leisure": "playground", "access": "private"}) is None
    assert osm.poi_art({"shop": "convenience"}) == ("supermarkt", "convenience")
    assert osm.poi_art({"disused:shop": "supermarket"}) is None


# ------------------------------------------------------------------------------- Netz und Objekte

def test_netz(erg):
    fuss = [w for w in erg.wege if "_nur_relation" not in w[1] and osm.ist_fussweg(w[1])]
    assert {w[0] for w in fuss} == mini.ERWARTET["netz_wege"]
    von, nach, knoten, koords = osm.netz_bauen(fuss, erg)
    assert len(von) == mini.ERWARTET["kanten"]
    assert len(knoten) == mini.ERWARTET["knoten"]
    assert (von < nach).all()
    assert len({(a, b) for a, b in zip(von.tolist(), nach.tolist())}) == len(von)
    assert 31 not in knoten.tolist() and 20 not in knoten.tolist()
    assert koords.shape == (len(knoten), 2)


def test_komponenten(erg):
    """Zusammenhang: Gitter (10 Knoten) und Insel (2 Knoten); Anteil bezogen auf die ausgewählten Knoten."""
    fuss = [w for w in erg.wege if "_nur_relation" not in w[1] and osm.ist_fussweg(w[1])]
    von, nach, knoten, _ = osm.netz_bauen(fuss, erg)
    alle = np.arange(knoten.size)
    kz = osm.komponenten(knoten, von, nach, alle)
    assert kz["komponenten"] == mini.ERWARTET["komponenten"]
    assert kz["groesste_komponente_im_stadtgebiet"] == 10 and kz["zweitgroesste_komponente_im_stadtgebiet"] == 2
    assert kz["anteil_groesste_komponente"] == round(10 / 12, 4)
    ohne_insel = np.flatnonzero(~np.isin(knoten, [70, 71]))
    assert osm.komponenten(knoten, von, nach, ohne_insel)["anteil_groesste_komponente"] == 1.0
    assert osm.komponenten(knoten, von, nach, np.zeros(0, dtype=np.int64))["anteil_groesste_komponente"] == 0.0


def test_kachel_aus_breite():
    """1-km-Kachel: mit pyproj (Ellipsoid WGS 84) nachgemessen, nicht gegen eine eingetippte Zahl."""
    from pyproj import Geod
    g = Geod(ellps="WGS84")
    for breite in (0.0, 50.06, 52.4, 60.0):
        dlon, dlat = osm.kachel_grad(breite)
        _a, _b, ost = g.inv(19.9, breite, 19.9 + dlon, breite)
        _a, _b, nord = g.inv(19.9, breite - dlat / 2, 19.9, breite + dlat / 2)
        assert abs(ost - 1000) < 10 and abs(nord - 1000) < 10, (breite, ost, nord)
    assert osm.kachel_grad(50.06)[0] > osm.kachel_grad(0.0)[0]    # Längengrade werden nach Norden kürzer


def test_objekte(erg):
    pois, bildung = osm.objekte_sammeln(erg)
    assert {p[0]: p[1] for p in pois} == mini.ERWARTET["pois"]
    assert {b[0]: b[1] for b in bildung} == mini.ERWARTET["bildung"]
    for p in pois + bildung:
        assert mini.NAME not in " ".join(str(x) for x in p)   # kein Name
    assert all(len(p) == 4 for p in pois)
    rel = next(p for p in pois if p[0] == "r200")
    assert rel[3].startswith("MULTIPOINT(") and rel[3].count("(") == 1 + 4   # 4 verschiedene Ecken aus 2 Mitgliedswegen


def test_relation_zweiter_durchgang(erg):
    ids = {w[0] for w in erg.wege if "_nur_relation" in w[1]}
    assert ids == {121, 122}


def test_eingang_wird_abgelehnt(pbf, tmp_path):
    eingang = tmp_path / "eingang"
    eingang.mkdir()
    ziel = eingang / "x.osm.pbf"
    ziel.write_bytes(pbf.read_bytes())
    lauf = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / "12_osm.py"), "--pbf", str(ziel)],
                          capture_output=True, text=True, check=False, env={**os.environ, "PGUSER": "niemand"})
    assert lauf.returncode != 0 and "Eingang" in lauf.stderr and "--uebernehmen" in lauf.stderr
    assert not (eingang / "HERKUNFT.md").exists()


def _stand_mini(pbf: Path) -> str:
    import datetime as dt
    return dt.datetime.fromtimestamp(osm_pbf.kopf_lesen(pbf).zeitstempel, dt.UTC).date().isoformat()


def test_uebernehmen_kopiert_aus_eingang(pbf, tmp_path):
    daten = tmp_path / "krakow"
    (daten / "eingang").mkdir(parents=True)
    quelle = daten / "eingang" / "malopolskie-latest.osm.pbf"
    quelle.write_bytes(pbf.read_bytes())
    md5 = hashlib.md5(pbf.read_bytes()).hexdigest()
    (daten / "eingang" / "malopolskie-latest.osm.pbf.md5").write_text(f"{md5}  malopolskie-latest.osm.pbf\n")
    vorher = sorted(p.name for p in (daten / "eingang").iterdir())
    ziel = osm.aus_eingang_uebernehmen(quelle, daten)
    stand = _stand_mini(pbf)
    assert ziel == daten / "osm" / stand / "malopolskie-latest.osm.pbf"
    assert ziel.read_bytes() == pbf.read_bytes()
    assert (ziel.parent / "malopolskie-latest.osm.pbf.md5").is_file()
    assert osm.md5_pruefen(ziel).startswith("MD5 gleich")
    assert not list(ziel.parent.glob("*.teil"))
    assert sorted(p.name for p in (daten / "eingang").iterdir()) == vorher   # Eingang unverändert
    # zweiter Aufruf: gleiche Datei, nichts Neues
    assert osm.aus_eingang_uebernehmen(quelle, daten) == ziel


def test_uebernehmen_bricht_bei_widerspruch_ab(pbf, tmp_path):
    daten = tmp_path / "krakow"
    (daten / "eingang").mkdir(parents=True)
    quelle = daten / "eingang" / "malopolskie-latest.osm.pbf"
    quelle.write_bytes(pbf.read_bytes())
    with pytest.raises(SystemExit, match="widerspricht"):
        osm.aus_eingang_uebernehmen(quelle, daten, "1999-01-01")
    assert not (daten / "osm").exists()
    fremd = daten / "osm" / _stand_mini(pbf) / "malopolskie-latest.osm.pbf"
    fremd.parent.mkdir(parents=True)
    fremd.write_bytes(b"andere Lieferung")
    with pytest.raises(SystemExit, match="anderem Inhalt"):
        osm.aus_eingang_uebernehmen(quelle, daten)
    assert fremd.read_bytes() == b"andere Lieferung"


def test_daten_wurzel(tmp_path, monkeypatch):
    monkeypatch.delenv("KIEZ_DATEN", raising=False)
    assert osm.daten_wurzel(tmp_path / "krakow" / "eingang" / "x.pbf") == tmp_path / "krakow"
    monkeypatch.setenv("KIEZ_DATEN", str(tmp_path / "anders"))
    assert osm.daten_wurzel(tmp_path / "krakow" / "eingang" / "x.pbf") == (tmp_path / "anders").resolve()


# ------------------------------------------------------------------------------- Herkunft (Rohdaten-Hash)

def _kopie(pbf: Path, ordner: Path) -> Path:
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = ordner / "malopolskie-latest.osm.pbf"
    ziel.write_bytes(pbf.read_bytes())
    return ziel


def test_herkunft_wird_angelegt(pbf, tmp_path):
    p = _kopie(pbf, tmp_path / "osm" / "2026-11-13")
    summe = hashlib.sha256(p.read_bytes()).hexdigest()
    assert osm.sha256(p) == summe
    befund = osm.herkunft_pruefen(p, osm_pbf.kopf_lesen(p), summe)
    text = (p.parent / "HERKUNFT.md").read_text(encoding="utf-8")
    assert "angelegt" in befund and summe in text and "ODbL" in text and "Potsdam" not in text
    assert osm.herkunft_pruefen(p, None, summe) == "SHA256 steht in HERKUNFT.md"      # zweiter Lauf: gleich


def test_herkunft_andere_summe_bricht_ab(pbf, tmp_path):
    p = _kopie(pbf, tmp_path / "osm" / "x")
    fremd = "ab" * 32
    (p.parent / "HERKUNFT.md").write_text(f"# Herkunft: {p.name}\n\n- SHA256: {fremd}\n", encoding="utf-8")
    with pytest.raises(osm.HerkunftFehler, match="nicht die beschriebene Lieferung"):
        osm.herkunft_pruefen(p, None, osm.sha256(p))
    with pytest.raises(osm.HerkunftFehler):                       # auch im Trockenlauf
        osm.herkunft_pruefen(p, None, osm.sha256(p), schreiben=False)


def test_herkunft_ohne_summe(pbf, tmp_path):
    p = _kopie(pbf, tmp_path / "osm" / "y")
    hk = p.parent / "HERKUNFT.md"
    hk.write_text("# Herkunft\n\n- Quelle: Geofabrik, Handdownload\n", encoding="utf-8")
    summe = osm.sha256(p)
    assert "Trockenlauf" in osm.herkunft_pruefen(p, None, summe, schreiben=False)
    assert summe not in hk.read_text(encoding="utf-8")            # Trockenlauf schreibt nie
    with pytest.raises(osm.HerkunftFehler, match="--hash-eintragen"):
        osm.herkunft_pruefen(p, None, summe)
    assert "nachgetragen" in osm.herkunft_pruefen(p, None, summe, eintragen=True)
    assert f"## {p.name}\n- SHA256: {summe}" in hk.read_text(encoding="utf-8")


def test_md5_des_anbieters(pbf, tmp_path):
    p = _kopie(pbf, tmp_path / "osm" / "z")
    assert "keine Prüfsummendatei" in osm.md5_pruefen(p)
    md5 = hashlib.md5(p.read_bytes()).hexdigest()
    (p.parent / (p.name + ".md5")).write_text(f"{md5}  {p.name}\n", encoding="utf-8")
    assert md5 in osm.md5_pruefen(p)
    (p.parent / (p.name + ".md5")).write_text(f"{'0' * 32}  {p.name}\n", encoding="utf-8")
    with pytest.raises(osm.HerkunftFehler, match="weicht"):
        osm.md5_pruefen(p)


def test_herkunft_vor_datenbank(pbf, tmp_path):
    """Eine fremde Datei bricht ab, bevor das Skript die Datenbank öffnet (PGUSER falsch: käme sonst als Fehler)."""
    p = _kopie(pbf, tmp_path / "osm" / "w")
    (p.parent / "HERKUNFT.md").write_text(f"## {p.name}\n- SHA256: {'cd' * 32}\n", encoding="utf-8")
    lauf = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / "12_osm.py"), "--pbf", str(p)],
                          capture_output=True, text=True, check=False, env={**os.environ, "PGUSER": "niemand"})
    assert lauf.returncode != 0 and "nicht die beschriebene Lieferung" in lauf.stderr
    assert "PGUSER" not in lauf.stderr


def test_bericht_ohne_amtliche_liste_und_zellen(pbf, tmp_path, erg):
    """Bericht: volle SHA256, Anteil der größten Komponente, „nicht geprüft“ statt erfundener Trefferquote."""
    summe = osm.sha256(pbf)
    voll = {a: {"amtlich": None, "amtlich_mit_osm": None, "osm": 1, "osm_mit_amtlich": None, "quote": None,
                "grund": "keine amtliche Liste geladen (Schulregister RSPO offen)"} for a in ("kita", "schule")}
    kz = {"knoten": 12, "kanten": 14, "knoten_im_stadtgebiet": 12, "komponenten": 2,
          "groesste_komponente_im_stadtgebiet": 10, "zweitgroesste_komponente_im_stadtgebiet": 2,
          "anteil_groesste_komponente": round(10 / 12, 4), "zellen_grund": "public.zensus_zelle fehlt",
          "abdeckung": {"rechteck_ok": True, "kacheln": 4, "leer": 0, "kachel_grad": osm.kachel_grad(50.06),
                        "leer_beispiele": []}}
    b = tmp_path / "osm_netz.md"
    osm.bericht_schreiben(b, pbf=pbf, summe=summe, herkunft="SHA256 steht in HERKUNFT.md", md5="keine",
                          erg=erg, stand="2026-11-04", geschrieben={"poi_je_art": {"arzt": 1}, "netz_km": 1},
                          voll=voll, kz=kz, trocken=False)
    text = b.read_text(encoding="utf-8")
    assert f"SHA256: `{summe}`" in text
    assert "Anteil der größten Komponente 83,3 %" in text
    assert "nicht geprüft: keine amtliche Liste" in text and "**" not in text.split("amtliche Liste (Treffer")[1]
    assert "nicht gerechnet, public.zensus_zelle fehlt" in text
    for wort in ("Potsdam", "MBJS", "Brandenburg", "Berlin", "A3"):
        assert wort not in text


def test_kein_landesfilter_keine_potsdam_reste():
    quelle = (WURZEL / "skripte" / "12_osm.py").read_text(encoding="utf-8")
    for wort in ("mbjs", "Brandenburg", "Berlin", "Potsdam", "BBBike-Auszug"):
        assert wort not in quelle, wort


# ------------------------------------------------------------------------------- Datenbank

@pytest.mark.skipif(os.environ.get("A3_DB_TEST") != "1" or os.environ.get("PGUSER") != "kiezatlas_rechnen",
                    reason="nur mit A3_DB_TEST=1 über skripte/12_osm.sh")
def test_trockenlauf_datenbank(pbf, tmp_path):
    import psycopg
    with psycopg.connect("") as c, c.cursor() as cur:
        cur.execute("SELECT (SELECT count(*) FROM auswertung.osm_poi), (SELECT count(*) FROM auswertung.netz_knoten),"
                    " (SELECT count(*) FROM auswertung.netz_kante)")
        vorher = cur.fetchone()
    bericht = tmp_path / "bericht.md"
    lauf = subprocess.run([sys.executable, "-I", str(WURZEL / "skripte" / "12_osm.py"), "--pbf", str(pbf),
                           "--trockenlauf", "--bericht", str(bericht)], capture_output=True, text=True, check=False)
    assert lauf.returncode == 0, lauf.stderr
    assert "ROLLBACK" in lauf.stdout
    # Einrichtungen nach Dublette: 6, Netz 12 Knoten / 14 Kanten (Knoten 30 liegt im Puffer, Insel 70-71 auch)
    assert "'arzt': 1" in lauf.stdout and "'spielplatz': 1" in lauf.stdout and "'supermarkt': 1" in lauf.stdout
    assert "'pflege': 2" in lauf.stdout and "'apotheke': 1" in lauf.stdout
    assert "Netz 12 Knoten, 14 Kanten" in lauf.stdout
    text = bericht.read_text(encoding="utf-8")
    assert "Trefferquote" in text and "TROCKENLAUF" in text and "Anteil der größten Komponente" in text
    assert osm.sha256(pbf) in text
    assert "nur Rechteckprüfung" in text and "1-km-Kacheln im Puffer" in text
    with psycopg.connect("") as c, c.cursor() as cur:
        cur.execute("SELECT (SELECT count(*) FROM auswertung.osm_poi), (SELECT count(*) FROM auswertung.netz_knoten),"
                    " (SELECT count(*) FROM auswertung.netz_kante)")
        assert cur.fetchone() == vorher                 # nichts gespeichert
