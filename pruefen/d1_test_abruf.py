"""Prüfungen zu skripte/abruf.py (Sperrliste, Kartenbilder, robots.txt, Protokoll), ohne Netz.

Ein lokaler HTTPS-Server mit selbst ausgestelltem Zertifikat (openssl) spielt die Gegenseite; abruf.TLS wird
dafür auf dieses Zertifikat umgestellt. Kein Abruf verlässt den Rechner.

    uv run -q --offline --python 3.13 --no-project --with-requirements requirements-pruefen.txt \
        python -m pytest -q pruefen/d1_test_abruf.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import ssl
import subprocess
import threading
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("abruf", WURZEL / "skripte" / "abruf.py")
abruf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(abruf)


# ----------------------------------------------------------------------------------------- ohne Netz

@pytest.mark.parametrize("url", [
    "https://zabytek.pl/x", "https://www.zabytek.pl/x", "https://download.geofabrik.de/europe/poland.pbf",
    "https://msip.um.krakow.pl/Dane/Dzielnice_JSON.zip", "https://geo.stat.gov.pl/atom",
    "https://nominatim.openstreetmap.org/search?q=Krak%C3%B3w", "https://WWW.GOV.PL/robots.txt",
    "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/HighResolution?SERVICE=WMS&REQUEST=GetMap&BBOX=1",
    "https://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/BDOT10k-BDOO?service=WMTS&request=gettile&x=1",
    "https://integracja.gugik.gov.pl/wmts/BDOT10k/default/Kachelsatz/10/512/300.png",
])
def test_gesperrt(url):
    with pytest.raises(abruf.Gesperrt):
        abruf.regeln_pruefen(url)


@pytest.mark.parametrize("url", [
    "https://gtfs.ztp.krakow.pl/GTFS_KRK_A.zip", "https://notzabytek.pl/x", "https://bip.krakow.pl/x",
    "https://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/BDOT10k-BDOO?Service=WMTS&Request=GetCapabilities",
    "https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/PL_PD_3035_GPKG.zip",
])
def test_regeln_lassen_zu(url):
    abruf.regeln_pruefen(url)


@pytest.mark.parametrize("url", ["http://gtfs.ztp.krakow.pl/x", "https://nutzer:geheim@gtfs.ztp.krakow.pl/x",
                                 "https:///x"])
def test_falscher_aufruf(url):
    with pytest.raises(ValueError):
        abruf.regeln_pruefen(url)


def test_max_mb_grenze(tmp_path, monkeypatch):
    monkeypatch.setenv("KIEZ_DATEN", str(tmp_path))
    assert abruf.main(["https://gtfs.ztp.krakow.pl/x", str(tmp_path / "x"), "--abstand", "5",
                       "--max-mb", "1001"]) == 2
    assert not (tmp_path / "abrufprotokoll.tsv").exists()


def test_robots_deny_und_crawl_delay():
    befund = "200 ausgewertet (2026-11-13T00:00:00+00:00, https://beispiel.pl/robots.txt, text/plain, SHA256 x)"
    with pytest.raises(abruf.Gesperrt):
        abruf.robots_auswerten(befund, "User-agent: *\nDeny: /\n", "https://beispiel.pl/a")
    text = "User-agent: *\nDisallow: /geheim\nCrawl-delay: 12\n"
    assert abruf.robots_auswerten(befund, text, "https://beispiel.pl/offen") == 12
    with pytest.raises(abruf.Gesperrt):
        abruf.robots_auswerten(befund, text, "https://beispiel.pl/geheim/x")
    with pytest.raises(abruf.Gesperrt):
        abruf.robots_auswerten("GESPERRT: Status 401  (…, https://beispiel.pl/robots.txt, )", None,
                               "https://beispiel.pl/a")


def test_befund_nur_fuer_robots_txt_und_frisch(tmp_path, monkeypatch):
    monkeypatch.setenv("KIEZ_ROBOTS", str(tmp_path))
    monkeypatch.setenv("KIEZ_ROBOTS_GEMEINSAM", str(tmp_path / "fehlt"))
    heute = datetime(2026, 11, 13, tzinfo=UTC)
    alt = tmp_path / "2026-09-01"
    alt.mkdir()
    (alt / "a.pl.befund").write_text("404 keine robots.txt (…, https://a.pl/robots.txt) -> erlaubt\n")
    assert abruf.befund_suchen("https://a.pl/x", heute) is None          # älter als 30 Tage
    neu = tmp_path / "2026-11-13"
    neu.mkdir()
    (neu / "b.pl.befund").write_text("404 keine robots.txt (…, https://b.pl/imap/robots.txt) -> erlaubt\n")
    assert abruf.befund_suchen("https://b.pl/x", heute) is None          # Unterpfad zählt nicht
    (neu / "a.pl.befund").write_text("404 keine robots.txt (…, https://a.pl/robots.txt) -> erlaubt\n")
    assert abruf.befund_suchen("https://a.pl/x", heute)[0].startswith("404")
    assert abruf.befund_suchen("https://a.pl/x", heute + timedelta(days=31)) is None


# ------------------------------------------------------------------------------- lokaler HTTPS-Server

ANTWORTEN: dict[str, tuple[int, bytes, dict]] = {}
ANFRAGEN: list[tuple[str, str]] = []


class Gegenseite(BaseHTTPRequestHandler):
    def do_GET(self):
        ANFRAGEN.append((self.path, self.headers.get("User-Agent", "")))
        status, koerper, kopf = ANTWORTEN.get(self.path, (404, b"nicht da", {}))
        self.send_response(status)
        for k, v in kopf.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(koerper)))
        self.end_headers()
        try:
            self.wfile.write(koerper)
        except (BrokenPipeError, ConnectionResetError, ssl.SSLError):
            pass  # der Abruf bricht bei „zu groß“ absichtlich ab

    def log_message(self, *a):
        pass


@pytest.fixture
def server(tmp_path, monkeypatch):
    schluessel, zert = tmp_path / "k.pem", tmp_path / "z.pem"
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=localhost",
                    "-addext", "subjectAltName=DNS:localhost", "-keyout", str(schluessel), "-out", str(zert)],
                   check=True, capture_output=True)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Gegenseite)
    kontext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    kontext.load_cert_chain(zert, schluessel)
    srv.socket = kontext.wrap_socket(srv.socket, server_side=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setattr(abruf, "TLS", ssl.create_default_context(cafile=str(zert)))
    monkeypatch.setenv("KIEZ_DATEN", str(tmp_path / "daten"))
    monkeypatch.delenv("KIEZ_ROBOTS", raising=False)                        # Standard: $KIEZ_DATEN/_robots
    monkeypatch.setenv("KIEZ_ROBOTS_GEMEINSAM", str(tmp_path / "gemeinsam"))
    ANTWORTEN.clear()
    ANFRAGEN.clear()
    yield f"https://localhost:{srv.server_address[1]}", tmp_path
    srv.shutdown()


def _protokoll(tmp_path: Path) -> list[list[str]]:
    zeilen = (tmp_path / "daten" / "abrufprotokoll.tsv").read_text(encoding="utf-8").splitlines()
    return [z.split("\t") for z in zeilen[1:]]


def test_robots_erlaubt_und_sperrt(server):
    basis, tmp = server
    ANTWORTEN["/robots.txt"] = (200, b"User-agent: *\nDisallow: /geheim\n", {"Content-Type": "text/plain"})
    ANTWORTEN["/offen.txt"] = (200, b"Daten", {})
    assert abruf.main([f"{basis}/offen.txt", str(tmp / "ziel" / "offen.txt"), "--abstand", "1"]) == 0
    assert (tmp / "ziel" / "offen.txt").read_bytes() == b"Daten"
    assert abruf.main([f"{basis}/geheim/x", str(tmp / "ziel" / "x"), "--abstand", "1"]) == 6
    assert not (tmp / "ziel" / "x").exists()
    # robots.txt nur einmal geholt, der Befund gilt für den zweiten Aufruf; jede Anfrage im Protokoll
    assert [p for p, _ in ANFRAGEN] == ["/robots.txt", "/offen.txt"]
    assert all(ua == abruf.KENNUNG for _, ua in ANFRAGEN)
    zeilen = _protokoll(tmp)
    assert [z[2].rsplit("/", 1)[1] for z in zeilen] == ["robots.txt", "offen.txt"]
    assert zeilen[1][3] == "200" and zeilen[1][5] == hashlib.sha256(b"Daten").hexdigest()
    assert not (tmp / "gemeinsam").exists()                                  # gemeinsame Ablage nur gelesen
    tag = next((tmp / "daten" / "_robots").iterdir())
    befund = (tag / "localhost_{}.befund".format(basis.rsplit(":", 1)[1])).read_text()
    assert befund.startswith("200 ausgewertet") and "/robots.txt," in befund
    assert (tag / "HERKUNFT.md").exists()


def test_robots_fehler_sperrt(server):
    basis, tmp = server
    ANTWORTEN["/robots.txt"] = (500, b"kaputt", {})
    ANTWORTEN["/a"] = (200, b"x", {})
    assert abruf.main([f"{basis}/a", str(tmp / "a"), "--abstand", "1"]) == 6
    assert [p for p, _ in ANFRAGEN] == ["/robots.txt"]
    assert not (tmp / "a").exists()


def test_robots_404_erlaubt_und_groesse(server):
    basis, tmp = server
    ANTWORTEN["/gross"] = (200, b"x" * (2 * 1024 * 1024), {})
    assert abruf.main([f"{basis}/gross", str(tmp / "g"), "--abstand", "1", "--max-mb", "1"]) == 5
    assert not (tmp / "g").exists() and not (tmp / "g.teil").exists()
    assert "zu groß" in _protokoll(tmp)[-1][3]


def test_weiterleitung_nicht_verfolgt(server):
    basis, tmp = server
    ANTWORTEN["/alt"] = (302, b"", {"Location": "https://anderswo.example/neu"})
    assert abruf.main([f"{basis}/alt", str(tmp / "n"), "--abstand", "1", "--gleicher-rechner"]) == 3
    assert [p for p, _ in ANFRAGEN] == ["/robots.txt", "/alt"]


def test_pruefsummen_liste(server):
    basis, tmp = server
    ANTWORTEN["/eins.zip"] = (200, b"eins", {})
    ANTWORTEN["/zwei.zip"] = (200, b"zwei", {})
    liste = tmp / "belege" / "rohdaten_test.sha256"
    daten = tmp / "daten"
    assert abruf.main([f"{basis}/zwei.zip", str(daten / "q" / "zwei.zip"), "--abstand", "1",
                       "--pruefsummen", str(liste)]) == 0
    assert abruf.main([f"{basis}/eins.zip", str(daten / "q" / "eins.zip"), "--abstand", "1",
                       "--pruefsummen", str(liste)]) == 0
    assert liste.read_text().splitlines() == [f"{hashlib.sha256(b'eins').hexdigest()}  q/eins.zip",
                                              f"{hashlib.sha256(b'zwei').hexdigest()}  q/zwei.zip"]
    # gleiche Form wie pruefen.sh (sha256sum -c im Ordner $KIEZ_DATEN)
    subprocess.run(["sha256sum", "-c", "--strict", "--quiet", str(liste)], cwd=daten, check=True)
    # Ziel außerhalb von $KIEZ_DATEN: Aufruffehler, kein Abruf
    assert abruf.main([f"{basis}/eins.zip", str(tmp / "aussen.zip"), "--abstand", "1",
                       "--pruefsummen", str(liste)]) == 2


def test_gemeinsamer_befund_wird_gelesen(tmp_path, monkeypatch):
    monkeypatch.setenv("KIEZ_DATEN", str(tmp_path / "daten"))
    monkeypatch.delenv("KIEZ_ROBOTS", raising=False)
    monkeypatch.setenv("KIEZ_ROBOTS_GEMEINSAM", str(tmp_path / "gemeinsam"))
    tag = tmp_path / "gemeinsam" / "2026-11-13"
    tag.mkdir(parents=True)
    (tag / "c.pl.befund").write_text("404 keine robots.txt (…, https://c.pl/robots.txt) -> erlaubt\n")
    assert abruf.befund_suchen("https://c.pl/x", datetime(2026, 11, 14, tzinfo=UTC))[0].startswith("404")
    assert abruf.robots_ordner() == tmp_path / "daten" / "_robots"
