"""Einzelabruf einer Datei mit Sperrliste, robots.txt, Mindestabstand je Rechner und Abrufprotokoll.

Einziger Netzweg des Kiezatlas Kraków. Jede Anfrage zählt als Abruf, auch robots.txt oder eine
Weiterleitung. Das Werkzeug liest deshalb vor jeder Anfrage das gemeinsame Protokoll
$KIEZ_DATEN/abrufprotokoll.tsv, wartet, bis der Abstand zur letzten Anfrage an denselben Rechner erreicht
ist, und trägt die neue Anfrage ein (Zeit UTC, Rechner, URL, Status, Bytes, SHA256, Ziel). Weiterleitungen
werden nicht verfolgt, außer mit --gleicher-rechner auf denselben Rechner (dann mit erneutem Abstand und
erneuter Prüfung).

Vor dem ersten Abruf bei einem Rechner gilt (in dieser Reihenfolge):
  1. nur https, keine Anmeldedaten in der URL, höchstens 1000 MB
  2. Sperrliste GESPERRT (Rechner und seine Unterrechner) und Teilwörter TEILWORT_GESPERRT, jeweils mit Grund
  3. Kartenbilder der GUGiK-Dienste (GetTile, GetMap, Kachelpfade) nie: deren Bedingungen verbieten das
     automatische Sammeln von Bildern („harvesting“); Capabilities-Dokumente bleiben abrufbar
  4. robots.txt: Befund <JJJJ-MM-TT>/<rechner>.befund aus $KIEZ_ROBOTS (eigene Ablage) oder, nur gelesen, aus
     $KIEZ_ROBOTS_GEMEINSAM (Befunde der Machbarkeitsprobe), höchstens ROBOTS_GUELTIG_TAGE alt und für
     https://<rechner>/robots.txt erhoben. Fehlt er, holt das Werkzeug robots.txt selbst (zählt als Abruf) und
     legt Befund, Text und HERKUNFT.md in $KIEZ_ROBOTS ab, im Format der Machbarkeitsprobe vom 13.11.2026:
       200 mit Text      -> auswerten (Disallow, auch „Deny“, und Crawl-delay)
       200 mit HTML      -> keine Regeln, erlaubt
       404, 410          -> keine robots.txt, erlaubt
       alles andere (3xx auf fremden Rechner, 401, 403, 5xx, Netzfehler) -> GESPERRT, bis von Hand entschieden
     Ein Crawl-delay über --abstand verlängert den Abstand.

Aufruf (Python aus der Projektumgebung, ohne Fremdpakete):
    python -I skripte/abruf.py --abstand 30 URL ZIELDATEI [--max-mb 100] [--gleicher-rechner]
        [--pruefsummen belege/rohdaten_<paket>.sha256]
Rückgabe: 0 gespeichert, 3 Weiterleitung nicht verfolgt, 4 HTTP- oder Netzfehler, 5 zu groß,
6 gesperrt (Sperrliste, Kartenbild, robots.txt), 2 falscher Aufruf.
Gleichzeitige Aufrufe warten aufeinander (Sperre auf abrufprotokoll.lock), damit der Abstand auch bei langen
Downloads hält; jeder Versuch steht im Protokoll, auch ein abgebrochener.

Umgebung: KIEZ_DATEN (Standard ../kiezatlas-daten/krakow), KIEZ_ROBOTS (Standard $KIEZ_DATEN/_robots),
KIEZ_ROBOTS_GEMEINSAM (Standard ../kiezatlas-daten/_robots, nur gelesen). Das Protokoll der Machbarkeitsprobe
(kiezatlas-daten/abrufprotokoll_krakow.tsv, anderes Format) liest das Werkzeug nicht; es ist abgeschlossen.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urljoin, urlsplit

KENNUNG = "kiezatlas-krakow (+https://souverain-systems.de/kiezatlas/krakow/)"
ROBOTER_NAME = "kiezatlas-krakow"          # Name, unter dem robots.txt-Regeln gelten
MAX_MB_GRENZE = 1000                       # große Downloads (> 1 GB) nur von Hand
ROBOTS_GUELTIG_TAGE = 30
TLS = ssl.create_default_context()         # Prüfungen ersetzen den Kontext für einen lokalen Testserver

_OSM = "OSM nur aus dem Handdownload (Machbarkeitsprobe 13.11.2026, offene Handdownloads Nr. 5)"
_WD = "Wikidata nur als Handdownload (Machbarkeitsprobe 13.11.2026, offene Handdownloads Nr. 6)"
_MSIP = ("Lizenz widersprüchlich (Regulamin MSIP 2016: nur nicht kommerziell, Weitergabeverbot); STOPP bis zur "
         "schriftlichen Antwort von msip@um.krakow.pl (docs/entscheidungen.md, KR3)")
_ROBOTS = "robots.txt nicht auswertbar, Befund 13.11.2026 (kiezatlas-daten/_robots/2026-11-13/): "
# Rechner -> Grund. Gesperrt sind der Rechner selbst und alle Unterrechner (*.rechner).
GESPERRT = {
    "download.geofabrik.de": _OSM,
    "download.bbbike.org": _OSM,
    "overpass-api.de": _OSM,
    "query.wikidata.org": _WD,
    "www.wikidata.org": _WD,
    "api.github.com": "kein Code und keine Daten von GitHub zur Laufzeit (Kiezatlas Potsdam, Abrufregeln)",
    "raw.githubusercontent.com": "kein Code und keine Daten von GitHub zur Laufzeit (Kiezatlas Potsdam, Abrufregeln)",
    "zabytek.pl": "robots.txt „Deny: /“, Befund 13.11.2026",
    "www.gov.pl": _ROBOTS + "301 auf robots.txt",
    "api.gios.gov.pl": _ROBOTS + "302 auf robots.txt; Paket Luft klärt den Weg von Hand",
    "msip3.um.krakow.pl": _ROBOTS + "500 auf robots.txt; außerdem " + _MSIP,
    "dane.gov.pl": _ROBOTS + "Zeitüberschreitung",
    "api.dane.gov.pl": _ROBOTS + "Zeitüberschreitung",
    "geo.stat.gov.pl": _ROBOTS + "401; Nutzungsbedingungen des Geostatistikportals verbieten Skripte",
    "portal.geo.stat.gov.pl": "Nutzungsbedingungen des Geostatistikportals verbieten Skripte (13.11.2026)",
    "msip.krakow.pl": _MSIP,
    "msip.um.krakow.pl": _MSIP,
    "msip2.um.krakow.pl": _MSIP,
    "msip-isdp.um.krakow.pl": _MSIP,
}
# Teilwörter im Rechnernamen (Dienste mit vielen Spiegeln)
TEILWORT_GESPERRT = {
    "nominatim": "keine Geokodierung über Nominatim-Dienste (Kiezatlas Potsdam, Abrufregeln)",
    "taginfo": "keine Abfragen an taginfo (Kiezatlas Potsdam, Abrufregeln)",
}
# GUGiK: „Wykorzystanie usługi nie podlega żadnym ograniczeniom z wyłączeniem automatycznego pobierania i
# kolekcjonowania obrazów … (tzw. harvesting)“ (Capabilities, kiezatlas-daten/krakow/2026-11-13/09_grundkarte/)
KARTENBILD_RECHNER = ("geoportal.gov.pl", "gugik.gov.pl")
KARTENBILD_ANFRAGEN = {"gettile", "getmap"}
KARTENBILD_ENDUNGEN = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".pbf", ".mvt")


class Gesperrt(Exception):
    """Abruf unzulässig (Sperrliste, Kartenbild, robots.txt); Rückgabe 6."""


def daten_ordner() -> Path:
    return Path(os.environ.get("KIEZ_DATEN") or Path(__file__).resolve().parents[2] / "kiezatlas-daten" / "krakow")


def robots_ordner() -> Path:
    """Ablage neuer robots-Befunde (unter $KIEZ_DATEN, damit nichts außerhalb des Kraków-Ordners entsteht)."""
    return Path(os.environ.get("KIEZ_ROBOTS") or daten_ordner() / "_robots")


def robots_ordner_gemeinsam() -> Path:
    """Gemeinsame Befunde der Kiezatlas-Proben (nur gelesen, z. B. die Machbarkeitsprobe vom 13.11.2026)."""
    return Path(os.environ.get("KIEZ_ROBOTS_GEMEINSAM") or daten_ordner().parent / "_robots")


def _passt(rechner: str, eintrag: str) -> bool:
    return rechner == eintrag or rechner.endswith("." + eintrag)


def regeln_pruefen(url: str) -> None:
    """Prüfungen 1–3 ohne Netz; wirft Gesperrt oder ValueError (falscher Aufruf)."""
    teile = urlsplit(url)
    rechner = (teile.hostname or "").lower().rstrip(".")
    if teile.scheme != "https":
        raise ValueError(f"nur https: {url}")
    if teile.username is not None or teile.password is not None:
        raise ValueError("keine Anmeldedaten in der URL (Abrufe nur ohne Anmeldung)")
    if not rechner:
        raise ValueError(f"kein Rechner in {url}")
    for eintrag, grund in GESPERRT.items():
        if _passt(rechner, eintrag):
            raise Gesperrt(f"Rechner {rechner} ist für automatische Abrufe gesperrt: {grund}")
    for wort, grund in TEILWORT_GESPERRT.items():
        if wort in rechner:
            raise Gesperrt(f"Rechner {rechner} ist für automatische Abrufe gesperrt: {grund}")
    if any(_passt(rechner, r) for r in KARTENBILD_RECHNER):
        anfrage = {k.lower(): v.lower() for k, v in parse_qsl(teile.query, keep_blank_values=True)}
        if anfrage.get("request") in KARTENBILD_ANFRAGEN or teile.path.lower().endswith(KARTENBILD_ENDUNGEN):
            raise Gesperrt(f"Kartenbilder von {rechner} nie automatisch abrufen (GUGiK verbietet harvesting); "
                           "Capabilities sind erlaubt")


def _robots_schluessel(url: str) -> tuple[str, str]:
    """(Dateiname des Befunds, URL der robots.txt) für den Rechner der URL, Port nur wenn nicht 443."""
    teile = urlsplit(url)
    rechner = (teile.hostname or "").lower()
    name = rechner if teile.port in (None, 443) else f"{rechner}_{teile.port}"
    netz = rechner if teile.port in (None, 443) else f"{rechner}:{teile.port}"
    return name, f"https://{netz}/robots.txt"


def befund_suchen(url: str, heute: datetime | None = None) -> tuple[str, str | None] | None:
    """Jüngster gültiger Befund (Text, robots.txt-Inhalt oder None) für den Rechner der URL, sonst None.

    Gültig ist ein Befund, der höchstens ROBOTS_GUELTIG_TAGE alt ist und für genau https://<rechner>/robots.txt
    erhoben wurde (Befunde für Unterpfade oder Ersatzseiten zählen nicht)."""
    name, robots_url = _robots_schluessel(url)
    heute = heute or datetime.now(UTC)
    tage = []
    for ordner in (robots_ordner(), robots_ordner_gemeinsam()):
        if ordner.is_dir():
            tage += [p for p in ordner.iterdir() if p.is_dir()]
    # jüngster Tag zuerst; bei gleichem Tag gewinnt die eigene Ablage (steht vorn, sort ist stabil)
    for tag in sorted(tage, key=lambda p: p.name, reverse=True):
        try:
            datum = datetime.strptime(tag.name, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            continue
        if heute - datum > timedelta(days=ROBOTS_GUELTIG_TAGE):
            break
        befund_datei = tag / f"{name}.befund"
        if not befund_datei.exists():
            continue
        befund = befund_datei.read_text(encoding="utf-8").strip()
        if f"{robots_url})" not in befund and f"{robots_url}," not in befund:
            continue
        text_datei = tag / f"{name}.txt"
        return befund, (text_datei.read_text(encoding="utf-8") if text_datei.exists() else None)
    return None


def robots_auswerten(befund: str, text: str | None, url: str) -> float:
    """Wirft Gesperrt, wenn robots.txt den Abruf nicht zulässt; gibt das Crawl-delay zurück (0 ohne)."""
    if befund.startswith("GESPERRT"):
        raise Gesperrt(f"robots.txt nicht auswertbar, Abruf unterlassen: {befund}")
    if not befund.startswith("200 ausgewertet"):
        return 0.0
    if text is None:
        raise Gesperrt(f"Befund ohne abgelegte robots.txt: {befund}")
    # „Deny“ kennt robotparser nicht; einige Rechner (zabytek.pl) schreiben es statt Disallow
    zeilen = ["Disallow:" + z.split(":", 1)[1] if z.strip().lower().startswith("deny:") else z
              for z in text.splitlines()]
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(zeilen)
    if not rp.can_fetch(ROBOTER_NAME, url):
        raise Gesperrt(f"robots.txt sperrt {url}")
    return float(rp.crawl_delay(ROBOTER_NAME) or 0)


class OhneWeiterleitung(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **kw):
        return None


def letzte_anfrage(protokoll: Path, rechner: str) -> float | None:
    if not protokoll.exists():
        return None
    zuletzt = None
    for zeile in protokoll.read_text(encoding="utf-8").splitlines()[1:]:
        teile = zeile.split("\t")
        if len(teile) > 1 and teile[1] == rechner:
            zuletzt = datetime.fromisoformat(teile[0]).timestamp()
    return zuletzt


def eintragen(protokoll: Path, zeit: datetime, rechner: str, url: str, status, n: int, sha: str,
              ziel: str) -> None:
    neu = not protokoll.exists()
    with protokoll.open("a", encoding="utf-8") as f:
        if neu:
            f.write("zeit_utc\trechner\turl\tstatus\tbytes\tsha256\tziel\n")
        f.write(f"{zeit.isoformat(timespec='seconds')}\t{rechner}\t{url}\t{status}\t{n}\t{sha}\t{ziel}\n")


def _warten(protokoll: Path, rechner: str, abstand: float) -> None:
    zuletzt = letzte_anfrage(protokoll, rechner)
    if zuletzt is not None:
        warten = zuletzt + abstand - time.time()
        if warten > 0:
            print(f"warte {warten:.0f} s (Abstand {abstand:g} s zu {rechner})", file=sys.stderr)
            time.sleep(warten)


def _oeffnen(url: str):
    oeffner = urllib.request.build_opener(OhneWeiterleitung, urllib.request.HTTPSHandler(context=TLS))
    return oeffner.open(urllib.request.Request(url, headers={"User-Agent": KENNUNG}), timeout=120)


def robots_holen(url: str, abstand: float, protokoll: Path) -> tuple[str, str | None]:
    """robots.txt des Rechners abrufen (zählt als Abruf), Befund ablegen; gibt (Befund, Text) zurück."""
    name, robots_url = _robots_schluessel(url)
    rechner = urlsplit(url).hostname or ""
    _warten(protokoll, rechner, abstand)
    zeit = datetime.now(UTC)
    status, koerper, art, fehler, weiter = "Fehler", b"", "", "", ""
    try:
        with _oeffnen(robots_url) as r:
            status, art = r.status, r.headers.get("Content-Type", "")
            koerper = r.read(5 * 1024 * 1024 + 1)
    except urllib.error.HTTPError as e:
        status, art = e.code, e.headers.get("Content-Type", "")
        weiter = urljoin(robots_url, e.headers.get("Location", "")) if 300 <= e.code < 400 else ""
    except OSError as e:
        fehler = f"{type(e).__name__}: {e}"
    sha = hashlib.sha256(koerper).hexdigest()
    ziel_ordner = robots_ordner() / zeit.strftime("%Y-%m-%d")
    ziel_ordner.mkdir(parents=True, exist_ok=True)
    text = koerper.decode("utf-8", "replace")
    stempel = zeit.isoformat()
    if status == 200 and len(koerper) > 5 * 1024 * 1024:
        befund = f"GESPERRT: Status 200, robots.txt größer als 5 MB ({stempel}, {robots_url}, {art})"
    elif status == 200 and not text.lstrip().lower().startswith(("<!doctype", "<html")):
        (ziel_ordner / f"{name}.txt").write_text(text, encoding="utf-8")
        befund = f"200 ausgewertet ({stempel}, {robots_url}, {art}, SHA256 {sha})"
    elif status == 200:
        befund = f"200 mit HTML statt robots.txt ({stempel}, {robots_url}) -> keine Regeln, erlaubt"
    elif status in (404, 410):
        befund = f"{status} keine robots.txt ({stempel}, {robots_url}) -> erlaubt"
    else:
        befund = (f"GESPERRT: Status {status} {fehler}{('-> ' + weiter) if weiter else ''} "
                  f"({stempel}, {robots_url}, {art})")
    eintragen(protokoll, zeit, rechner, robots_url, status if not fehler else f"Fehler {fehler.split(':')[0]}",
              len(koerper), sha if koerper else "", str(ziel_ordner / f"{name}.befund"))
    (ziel_ordner / f"{name}.befund").write_text(befund + "\n", encoding="utf-8")
    with (ziel_ordner / "HERKUNFT.md").open("a", encoding="utf-8") as f:
        f.write(f"- {name}: {befund} (skripte/abruf.py, Kiezatlas Kraków)\n")
    print(f"robots.txt {rechner}: {befund}", file=sys.stderr)
    return befund, (text if befund.startswith("200 ausgewertet") else None)


def zulassen(url: str, abstand: float, protokoll: Path) -> float:
    """Alle Prüfungen vor einem Abruf; gibt den wirksamen Abstand zurück, wirft Gesperrt oder ValueError."""
    regeln_pruefen(url)
    gefunden = befund_suchen(url)
    befund, text = gefunden if gefunden else robots_holen(url, abstand, protokoll)
    return max(abstand, robots_auswerten(befund, text, url))


def holen(url: str, ziel: Path, abstand: float, max_mb: float, protokoll: Path) -> tuple[int, str | None]:
    rechner = urlsplit(url).hostname or ""
    abstand = zulassen(url, abstand, protokoll)
    _warten(protokoll, rechner, abstand)
    zeit = datetime.now(UTC)
    teil = ziel.with_name(ziel.name + ".teil")
    h, n = hashlib.sha256(), 0
    try:
        with _oeffnen(url) as r:
            laenge = int(r.headers.get("Content-Length") or 0)
            if laenge > max_mb * 1024 * 1024:
                eintragen(protokoll, zeit, rechner, url, f"{r.status} zu groß ({laenge})", 0, "", "")
                return 5, None
            ziel.parent.mkdir(parents=True, exist_ok=True)
            with teil.open("wb") as f:
                while stueck := r.read(1 << 16):
                    n += len(stueck)
                    if n > max_mb * 1024 * 1024:
                        f.close()
                        teil.unlink()
                        eintragen(protokoll, zeit, rechner, url, f"{r.status} abgebrochen > {max_mb} MB", n, "", "")
                        return 5, None
                    h.update(stueck)
                    f.write(stueck)
            status = r.status
    except urllib.error.HTTPError as e:
        if teil.exists():
            teil.unlink()
        if 300 <= e.code < 400:
            ort = urljoin(url, e.headers.get("Location", ""))
            eintragen(protokoll, zeit, rechner, url, f"{e.code} -> {ort}", 0, "", "")
            return 3, ort
        eintragen(protokoll, zeit, rechner, url, e.code, 0, "", "")
        return 4, None
    except (OSError, KeyboardInterrupt) as e:  # URLError, Zeitüberschreitung, TLS, Abbruch: zählt als Abruf
        if teil.exists():
            teil.unlink()
        eintragen(protokoll, zeit, rechner, url, f"Fehler {type(e).__name__}", n, "", "")
        if isinstance(e, KeyboardInterrupt):
            raise
        print(f"Fehler: {e}", file=sys.stderr)
        return 4, None
    teil.replace(ziel)
    eintragen(protokoll, zeit, rechner, url, status, n, h.hexdigest(), str(ziel))
    print(f"{status} {n} Bytes sha256={h.hexdigest()} -> {ziel}")
    return 0, None


def pruefsumme_eintragen(liste: Path, ziel: Path, sha: str) -> None:
    """Zeile „<sha256>  <Pfad relativ zu $KIEZ_DATEN>“ in liste setzen (sha256sum -c, wie pruefen.sh sie prüft).

    Eine ältere Zeile für denselben Pfad wird ersetzt; die Liste bleibt nach Pfad sortiert."""
    rel = ziel.resolve().relative_to(daten_ordner().resolve()).as_posix()
    zeilen = {}
    if liste.exists():
        for z in liste.read_text(encoding="utf-8").splitlines():
            if z.strip():
                zeilen[z.split("  ", 1)[1]] = z
    zeilen[rel] = f"{sha}  {rel}"
    liste.parent.mkdir(parents=True, exist_ok=True)
    liste.write_text("".join(zeilen[k] + "\n" for k in sorted(zeilen)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("url")
    ap.add_argument("ziel", type=Path)
    ap.add_argument("--abstand", type=float, required=True, help="Mindestabstand in s je Rechner")
    ap.add_argument("--max-mb", type=float, default=100, help=f"Obergrenze, höchstens {MAX_MB_GRENZE}")
    ap.add_argument("--gleicher-rechner", action="store_true",
                    help="Weiterleitung verfolgen, wenn sie auf denselben Rechner zeigt")
    ap.add_argument("--pruefsummen", type=Path,
                    help="Liste belege/rohdaten_<paket>.sha256, in die die Prüfsumme der Datei eingetragen wird "
                         "(Ziel muss unter $KIEZ_DATEN liegen)")
    a = ap.parse_args(argv)
    if not 0 < a.max_mb <= MAX_MB_GRENZE:
        print(f"--max-mb muss zwischen 0 und {MAX_MB_GRENZE} liegen (größere Downloads nur von Hand)",
              file=sys.stderr)
        return 2
    if a.abstand < 1:
        print("--abstand mindestens 1 s", file=sys.stderr)
        return 2
    if a.pruefsummen and not a.ziel.resolve().is_relative_to(daten_ordner().resolve()):
        print(f"--pruefsummen: {a.ziel} liegt nicht unter $KIEZ_DATEN ({daten_ordner()})", file=sys.stderr)
        return 2
    protokoll = daten_ordner() / "abrufprotokoll.tsv"
    protokoll.parent.mkdir(parents=True, exist_ok=True)
    url = a.url
    try:
        with (protokoll.parent / "abrufprotokoll.lock").open("w") as sperre:
            fcntl.flock(sperre, fcntl.LOCK_EX)
            for _ in range(3):
                code, ort = holen(url, a.ziel, a.abstand, a.max_mb, protokoll)
                if code == 0 and a.pruefsummen:
                    with a.ziel.open("rb") as f:
                        sha = hashlib.file_digest(f, "sha256").hexdigest()
                    pruefsumme_eintragen(a.pruefsummen, a.ziel, sha)
                    print(f"Prüfsumme eingetragen in {a.pruefsummen}", file=sys.stderr)
                if code != 3:
                    return code
                print(f"Weiterleitung auf {ort}", file=sys.stderr)
                if not (a.gleicher_rechner and urlsplit(ort).hostname == urlsplit(url).hostname):
                    return 3
                url = ort
    except Gesperrt as e:
        print(f"gesperrt: {e}", file=sys.stderr)
        return 6
    except ValueError as e:
        print(f"Aufruf: {e}", file=sys.stderr)
        return 2
    return 3


if __name__ == "__main__":
    sys.exit(main())
