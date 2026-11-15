"""Deploy-Kopie des Kiezatlas Kraków: alle Seiten in allen Sprachen, Cache-Busting, verkleinertes JavaScript.

Kopiert genau die Dateien, die unter der kanonischen Adresse (basis_url in config/krakow.yaml) liegen sollen, in
einen Ordner unter ../kiezatlas-deploy/krakow/ und
  1. hängt in jeder HTML-Seite (auch in den Sprachordnern en/, de/) an jeden lokalen Verweis auf .js, .css, .svg,
     .png, .jpg, .mp4, .woff2 und an jeden Verweis unter daten/ ein ?v=<mtime der Zieldatei> an; aufgelöst wird
     gegen den Ordner der Seite, also ../daten/ort.js in en/ gegen die Wurzel; ebenso an url(…) in den eigenen
     Stylesheets der Wurzel (Schriften);
  2. setzt in jeder Seite window.KIEZ_V = jüngste mtime unter daten/ und fonts/ (themen.js hängt den Wert an
     nachgeladene Dateien) und schreibt den Stand (Datum und git describe) in <span data-kiez-version>;
  3. schreibt die Verweise der 404-Seiten auf Pfade ab der Domain um (/kiezatlas/krakow/…), weil der Webserver
     die 404-Seite unter jeder fehlerhaften Adresse ausliefert, auch zwei Ordner tief;
  4. verkleinert das eigene JavaScript (Wurzel *.js und texte/**/*.js) mit esbuild (Entwicklungsabhängigkeit aus
     package-lock.json, genaue Version mit Hash). Nicht verkleinert: daten/ (Lizenzvermerke stehen dort in
     Kommentaren), vendor/ (schon verkleinert), fonts/.
  5. legt die Grundkarte bei, sobald eine Seite daten/grundkarte.js lädt: kacheln/ und schrift/ aus dem
     Kachelordner außerhalb des Repos ($KIEZ_DATEN/abgeleitet/grundkarte/<SHA-Anfang>/, wie
     skripte/entwicklung_server.mjs; anderer Ordner mit --grundkarte) nach daten/grundkarte/ der Kopie. Jede .pbf
     wird gegen MANIFEST.sha256 geprüft, MANIFEST.sha256 gegen lauf.json; schrift/OFL.txt muss die Lizenz von
     Noto Sans tragen. Fehlt der Ordner oder weicht eine Datei ab, bricht das Skript ab. Webserver: .pbf als
     application/x-protobuf ausliefern.
  6. legt die Gebäude in 3D bei, sobald eine Seite kartenseite.js lädt (Knopf „3D“, docs/entscheidungen.md KR42):
     die 18 Dateien <nr>_odbl.js aus $KIEZ_DATEN/abgeleitet/gebaeude/<Stand aus config/gebaeude_3d.json>/, ohne
     Manifest dort aus dem jüngsten Ordner *-odbl mit Manifest (wie skripte/entwicklung_server.mjs; anderer Ordner
     mit --gebaeude) unverändert nach daten/gebaeude/ der Kopie.
     Geprüft wird das Manifest des Ordners (MANIFEST.sha256, sonst SHA256SUMS) gegen die hier festgeschriebene
     Prüfsumme, jede Datei gegen das Manifest, genau eine Datei je dzielnica aus der Ortskonfiguration, der
     ODbL-Vermerk im Kopf jeder Datei und keine weiteren Dateien außer HERKUNFT.md (wird nicht ausgeliefert). Fehlt
     der Ordner oder weicht etwas ab, bricht das Skript ab. Erzeugt werden die Dateien reproduzierbar von
     skripte/20_bdot10k.py --geometrie <Ordner>; „--pruefen --geometrie <Ordner>“ vergleicht byte-gleich.
Am Ende schreibt das Skript MD5SUMS über die geschriebenen Dateien: dagegen prüft man nach dem Upload die live
geladenen Dateien. Das Repo bleibt unverändert, file:// im Repo läuft ohne ?v und unverkleinert.

Sicherheitsgrenzen: Das Ziel muss <deploy-wurzel>/kiezatlas-deploy/krakow/<name> sein (Standard-Wurzel: der Ordner
über dem Repo). Ein bestehendes Ziel wird nur ersetzt, wenn es eine frühere Kraków-Kopie ist (MD5SUMS mit den
Sprachseiten). So trifft das Skript nie einen Potsdamer Stand unter ../kiezatlas-deploy/<datum>. Liegen unter
daten/ Beispieldaten (fixture: true), bricht es ab, außer mit --mit-beispieldaten.

Lädt nichts hoch und ruft nichts aus dem Netz ab. Der Upload ist Andres Schritt (docs/auslieferung.md).

Aufruf (Python aus requirements.txt, wegen pyyaml):
  python -I skripte/deploy_kopie.py [--ziel ../kiezatlas-deploy/krakow/<datum>] [--deploy-wurzel ORDNER]
                                    [--mit-beispieldaten] [--unverkleinert] [--liste] [--grundkarte ORDNER]
                                    [--gebaeude ORDNER]
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
import ort_konfig  # noqa: E402  (liest config/krakow.yaml bzw. $KIEZ_CONFIG)

# Dateien neben den Seiten. Nicht dabei: Vorlagen, Prüfskripte, Belege, Berichte, daten/fixtures/, daten/schema/
# (Verträge, nur im Repo), Rohdaten, die Vorlagen der Langtexte unter texte/<lang>/bloecke/.
WURZEL_MUSTER = ["*.js", "*.css", "favicon.svg"]
ORDNER = ["vendor", "fonts", "daten", "texte"]
AUSSER_ORDNER = ("daten/fixtures/", "daten/schema/")
# GSAP (GreenSock Standard License, keine offene Lizenz) lädt keine Krakauer Seite; es bleibt im Repo nur für die
# Gegenprobe Potsdam (NOTICE) und geht nicht auf den Server
AUSSER_DATEIEN = ("vendor/gsap.min.js", "vendor/ScrollTrigger.min.js")
NUR_ENDUNG = {"texte": {".js"}}          # aus texte/ nur die Sprachdateien
OPTIONAL = ["og.png"]                    # Vorschaubild je Sprache (skripte/28_vorschaubild.mjs), sobald es das gibt


def zu_verkleinern(p: Path) -> bool:
    """Eigener Code: JavaScript in der Wurzel und unter texte/."""
    return p.suffix == ".js" and (len(p.parts) == 1 or p.parts[0] == "texte")


ENDUNGEN = (".js", ".css", ".svg", ".png", ".woff2", ".jpg", ".mp4")
# jeder lokale Verweis in src/href/poster (ohne Schema, ohne Anker, ohne Abfrage)
VERWEIS = re.compile(r'((?:src|href|poster)=")([^"#?:]*)(["#?])')
VERSION_MARKE = "<span data-kiez-version>—</span>"


def konfig():
    k = ort_konfig.lade()
    for f in ("sprachen", "seiten", "basis_url"):
        if not k.get(f):
            sys.exit(f"{ort_konfig.pfad()}: Feld {f} fehlt")
    basis = urlparse(k["basis_url"])
    if basis.scheme != "https" or not basis.path.startswith("/") or not basis.path.endswith("/"):
        sys.exit(f"basis_url muss https://…/ mit Pfad und Schrägstrich am Ende sein: {k['basis_url']}")
    return k, basis.path


def seitenliste(k):
    """Seiten aus der Ortskonfiguration: erste Sprache in der Wurzel, die anderen in <lang>/."""
    return [Path(f"{s}.html") if i == 0 else Path(lang) / f"{s}.html"
            for i, lang in enumerate(k["sprachen"]) for s in k["seiten"]]


def dateiliste(k):
    out = seitenliste(k)
    for m in WURZEL_MUSTER:
        out += sorted(p.relative_to(WURZEL) for p in WURZEL.glob(m) if p.is_file())
    for o in ORDNER:
        for p in sorted((WURZEL / o).rglob("*")):
            r = p.relative_to(WURZEL)
            if not p.is_file() or r.as_posix().startswith(AUSSER_ORDNER) or r.as_posix() in AUSSER_DATEIEN:
                continue
            if o in NUR_ENDUNG and p.suffix not in NUR_ENDUNG[o]:
                continue
            out.append(r)
    for i, lang in enumerate(k["sprachen"]):
        for name in OPTIONAL:
            r = Path(name) if i == 0 else Path(lang) / name
            if (WURZEL / r).is_file():
                out.append(r)
    fehlt = [str(p) for p in out if not (WURZEL / p).is_file()]
    if fehlt:
        sys.exit("fehlt: " + ", ".join(fehlt))
    for p in out:   # keine Datei, die per Verknüpfung aus dem Repo hinauszeigt
        echt = (WURZEL / p).resolve()
        if WURZEL not in echt.parents:
            sys.exit(f"{p} zeigt aus dem Repo hinaus ({echt})")
    return list(dict.fromkeys(out))


def beispieldaten(liste):
    """Dateien unter daten/ mit "fixture":true im Kopf (Beispieldaten)."""
    return [str(p) for p in liste if p.parts[0] == "daten" and p.suffix in (".js", ".json")
            and '"fixture":true' in (WURZEL / p).read_text(encoding="utf-8", errors="replace")[:4000]]


GK_ZIEL = "daten/grundkarte"
GK_TEILE = ("kacheln", "schrift")
GK_LIZENZ = "schrift/OFL.txt"   # nicht im MANIFEST (dort nur .pbf), Inhalt wird geprüft


def braucht_grundkarte(k) -> bool:
    """Lädt eine erzeugte Seite daten/grundkarte.js? Dann gehören die Kacheln in die Kopie."""
    return any(re.search(r'src="(?:\.\./)?daten/grundkarte\.js"', (WURZEL / p).read_text(encoding="utf-8"))
               for p in seitenliste(k))


def grundkarte_ordner(angabe: str | None) -> Path:
    """Kachelordner wie skripte/entwicklung_server.mjs: SHA der BDOT10k-Eingabe aus skripte/27_grundkarte.py."""
    if angabe:
        return Path(angabe).resolve()
    daten = Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")
    m = re.search(r'BDOT_SHA256 = "([0-9a-f]{64})"', (WURZEL / "skripte" / "27_grundkarte.py").read_text(encoding="utf-8"))
    if not m:
        sys.exit("skripte/27_grundkarte.py: BDOT_SHA256 nicht gefunden")
    return (daten / "abgeleitet" / "grundkarte" / m.group(1)[:12]).resolve()


def grundkarte_liste(ordner: Path) -> list[str]:
    """Pfade unter kacheln/ und schrift/ (relativ zum Kachelordner), jede Datei geprüft; Abbruch bei Abweichung."""
    man = ordner / "MANIFEST.sha256"
    if not man.is_file():
        sys.exit(f"Grundkarte: kein Kachelordner unter {ordner} (MANIFEST.sha256 fehlt); skripte/27_grundkarte.py "
                 "ausführen oder --grundkarte angeben. Eine Seite lädt daten/grundkarte.js.")
    lauf = json.loads((ordner / "lauf.json").read_text(encoding="utf-8"))
    if hashlib.sha256(man.read_bytes()).hexdigest() != lauf.get("manifest_sha256"):
        sys.exit(f"Grundkarte: {man} passt nicht zu lauf.json (manifest_sha256)")
    soll = {}
    for z in man.read_text(encoding="utf-8").splitlines():
        h, _, pfad = z.partition("  ")
        soll[pfad] = h
    ist = sorted(p.relative_to(ordner).as_posix() for teil in GK_TEILE for p in (ordner / teil).rglob("*") if p.is_file())
    fremd = [p for p in ist if p not in soll and p != GK_LIZENZ]
    fehlt = [p for p in soll if p not in ist]
    falsch = [p for p in ist if p in soll and hashlib.sha256((ordner / p).read_bytes()).hexdigest() != soll[p]]
    for art, l in (("nicht im MANIFEST", fremd), ("fehlt", fehlt), ("SHA256 weicht ab", falsch)):
        if l:
            sys.exit(f"Grundkarte {ordner}: {art}: " + ", ".join(l[:5]) + (" …" if len(l) > 5 else ""))
    ofl = (ordner / GK_LIZENZ).read_text(encoding="utf-8") if (ordner / GK_LIZENZ).is_file() else ""
    if "SIL OPEN FONT LICENSE" not in ofl or "Noto" not in ofl:
        sys.exit(f"Grundkarte: {ordner / GK_LIZENZ} fehlt oder nennt Noto Sans und die SIL OFL nicht")
    for p in ist:   # keine Verknüpfung, die aus dem Kachelordner hinauszeigt
        if ordner not in (ordner / p).resolve().parents:
            sys.exit(f"Grundkarte: {p} zeigt aus {ordner} hinaus")
    return ist


GEB_ZIEL = "daten/gebaeude"
# Stand der 3D-Dateien und Prüfsumme ihres Manifests aus config/gebaeude_3d.json (gemessen am 14.11.2026, eine Stelle
# für Entwicklungsserver, Deploy-Kopie und Prüfungen). Neuer Stand = neuer Ordner und neue Werte dort.
_GEB_3D = json.loads((WURZEL / "config" / "gebaeude_3d.json").read_text(encoding="utf-8"))
GEB_STAND = _GEB_3D["stand"]
GEB_MANIFEST_SHA256 = _GEB_3D["manifest_sha256"]
GEB_MANIFESTE = ("MANIFEST.sha256", "SHA256SUMS")
GEB_NEBEN = {"HERKUNFT.md"}              # liegt im Ordner, wird nicht ausgeliefert
GEB_ODBL = ("OpenStreetMap", "Open Database License")


def braucht_gebaeude(k) -> bool:
    """Lädt eine erzeugte Seite kartenseite.js (3D auf Knopfdruck)? Dann gehören die Gebäudedateien in die Kopie."""
    return any(re.search(r'src="(?:\.\./)?kartenseite\.js"', (WURZEL / p).read_text(encoding="utf-8"))
               for p in seitenliste(k))


def gebaeude_ordner(angabe: str | None) -> Path:
    """--gebaeude, sonst abgeleitet/gebaeude/<GEB_STAND>/; ohne Manifest dort der jüngste Ordner *-odbl mit Manifest
    (wie skripte/entwicklung_server.mjs). Die Prüfsumme des Manifests muss in jedem Fall GEB_MANIFEST_SHA256 sein."""
    if angabe:
        return Path(angabe).resolve()
    daten = Path(os.environ.get("KIEZ_DATEN") or WURZEL.parent / "kiezatlas-daten" / "krakow")
    basis = daten / "abgeleitet" / "gebaeude"
    fest = basis / GEB_STAND

    def mit_manifest(o: Path) -> bool:
        return any((o / n).is_file() for n in GEB_MANIFESTE)
    if mit_manifest(fest) or not basis.is_dir():
        return fest.resolve()
    kand = sorted(o for o in basis.iterdir() if o.is_dir() and o.name.endswith("-odbl") and mit_manifest(o))
    return (kand[-1] if kand else fest).resolve()


def gebaeude_liste(ordner: Path, k) -> list[str]:
    """Dateinamen <nr>_odbl.js, jede gegen das Manifest geprüft; Abbruch bei Abweichung."""
    man = next((ordner / n for n in GEB_MANIFESTE if (ordner / n).is_file()), None)
    if man is None:
        sys.exit(f"Gebäude 3D: kein Manifest ({' oder '.join(GEB_MANIFESTE)}) unter {ordner}; mit "
                 "skripte/20_bdot10k.py --geometrie erzeugen oder --gebaeude angeben. Eine Seite lädt kartenseite.js.")
    ist_sha = hashlib.sha256(man.read_bytes()).hexdigest()
    if ist_sha != GEB_MANIFEST_SHA256:
        sys.exit(f"Gebäude 3D: {man} hat SHA256 {ist_sha}, festgeschrieben ist {GEB_MANIFEST_SHA256} (GEB_MANIFEST_SHA256)")
    soll = {}
    for z in man.read_text(encoding="utf-8").splitlines():
        h, _, name = z.partition("  ")
        soll[name] = h
    nrn = sorted(str(t["nr"]) for t in (k.get("gliederung") or {}).get("teile") or [])
    erwartet = [f"{nr}_odbl.js" for nr in nrn]
    if not nrn or sorted(soll) != erwartet:
        sys.exit(f"Gebäude 3D: Manifest nennt {sorted(soll)[:3]} …, erwartet genau {len(erwartet)} Dateien <nr>_odbl.js")
    vorhanden = sorted(p.name for p in ordner.iterdir())
    fremd = [n for n in vorhanden if n not in soll and n not in GEB_NEBEN and n != man.name]
    if fremd:
        sys.exit(f"Gebäude 3D {ordner}: Dateien ohne Manifest: " + ", ".join(fremd[:5]))
    for name in erwartet:
        p = ordner / name
        if not p.is_file() or p.is_symlink() or ordner not in p.resolve().parents:
            sys.exit(f"Gebäude 3D: {p} fehlt oder ist eine Verknüpfung")
        roh = p.read_bytes()
        if hashlib.sha256(roh).hexdigest() != soll[name]:
            sys.exit(f"Gebäude 3D: {p} SHA256 weicht vom Manifest ab")
        kopf = roh[:3000].decode("utf-8", errors="replace")
        if not all(v in kopf for v in GEB_ODBL):
            sys.exit(f"Gebäude 3D: {p} ohne ODbL-Vermerk im Kopf")
    return erwartet


def stand(liste):
    return max(int((WURZEL / p).stat().st_mtime) for p in liste if p.parts[0] in ("daten", "fonts"))


def version() -> str:
    """Stand für den Seitenfuß, sprachneutral: ISO-Datum und git describe (mit „-dirty“, wenn nicht alles committet)."""
    try:
        v = subprocess.run(["git", "-C", str(WURZEL), "describe", "--tags", "--always", "--dirty"], capture_output=True,
                           text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        v = "unbekannt"
    return f"{date.today().isoformat()} ({v})"


def aufloesen(seite: Path, ref: str) -> str | None:
    """Verweis einer Seite als Pfad relativ zur Wurzel (POSIX, „“ = Wurzel), None, wenn er hinausführt."""
    if ref.startswith("/") or ref == "":
        return None
    r = posixpath.normpath(posixpath.join(seite.parent.as_posix(), ref))
    if r == ".." or r.startswith("../"):
        return None
    return "" if r == "." else r


def html_umschreiben(seite: Path, text: str, stempel: str, ver: str, basis_pfad: str, ist_404: bool) -> str:
    def ersetze(m):
        ref = m.group(2)
        ziel = aufloesen(seite, ref)
        if ziel is None:
            return m.group(0)
        neu = ref
        if ist_404:   # ab der Domain, damit die Seite unter jeder fehlerhaften Adresse vollständig lädt
            neu = basis_pfad + ziel + ("/" if ref.endswith("/") and ziel else "")
        if ziel and (ziel.startswith("daten/") or ref.endswith(ENDUNGEN)) and (WURZEL / ziel).is_file() \
                and m.group(3) == '"':
            neu += f"?v={int((WURZEL / ziel).stat().st_mtime)}"
        return f"{m.group(1)}{neu}{m.group(3)}"
    text = VERWEIS.sub(ersetze, text)
    marke = '<meta charset="utf-8">'
    if marke not in text:
        sys.exit(f"{seite}: ohne <meta charset>, KIEZ_V lässt sich nicht setzen")
    if text.count(VERSION_MARKE) != 1:
        sys.exit(f"{seite}: {VERSION_MARKE} nicht genau einmal gefunden")
    text = text.replace(VERSION_MARKE, f"<span data-kiez-version>{ver}</span>")
    return text.replace(marke, f'{marke}\n<script>window.KIEZ_V="{stempel}"</script>', 1)


CSS_URL = re.compile(r"url\((['\"]?)([^'\")#?:]+)\1\)")


def css_umschreiben(text: str) -> str:
    """?v= an url(…) der eigenen Stylesheets (Schriften unter fonts/), damit auch sie nach einem Wechsel neu laden."""
    def ersetze(m):
        ziel = WURZEL / m.group(2)
        if not ziel.is_file() or WURZEL not in ziel.resolve().parents:
            return m.group(0)
        return f"url({m.group(1)}{m.group(2)}?v={int(ziel.stat().st_mtime)}{m.group(1)})"
    return CSS_URL.sub(ersetze, text)


ESBUILD_JS = r"""
const fs = require("fs"), path = require("path");
const esbuild = require(path.join(process.argv[1], "node_modules", "esbuild"));
const auftrag = JSON.parse(fs.readFileSync(0, "utf8"));
for (const [q, z] of auftrag) {
  // Kein bundle und kein format: Die Skripte teilen sich Namen auf oberster Ebene über mehrere <script>-Tags;
  // ohne format benennt esbuild diese Namen nicht um. Lizenzkommentare (/*! … */, @license) bleiben stehen.
  const r = esbuild.transformSync(fs.readFileSync(q, "utf8"),
    { loader: "js", minify: true, legalComments: "inline", charset: "utf8", sourcefile: path.basename(q) });
  fs.writeFileSync(z, r.code);
}
process.stdout.write(esbuild.version);
"""


def verkleinern(paare) -> str:
    """Verkleinert [(quelle, ziel), …] mit esbuild aus node_modules; gibt die esbuild-Version zurück."""
    if not (WURZEL / "node_modules" / "esbuild").is_dir():
        sys.exit("esbuild fehlt in node_modules: npm ci --offline --ignore-scripts (Versionen aus package-lock.json)")
    r = subprocess.run(["node", "-e", ESBUILD_JS, str(WURZEL)], input=json.dumps([[str(q), str(z)] for q, z in paare]),
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("esbuild: " + r.stderr.strip())
    lock = json.loads((WURZEL / "package-lock.json").read_text(encoding="utf-8"))
    erwartet = lock["packages"]["node_modules/esbuild"]["version"]
    if r.stdout.strip() != erwartet:
        sys.exit(f"esbuild {r.stdout.strip()} in node_modules, package-lock.json verlangt {erwartet}")
    return r.stdout.strip()


def ziel_pruefen(ziel: Path, deploy_wurzel: Path) -> Path:
    erlaubt = (deploy_wurzel / "kiezatlas-deploy" / "krakow").resolve()
    z = ziel.resolve()
    if z.parent != erlaubt:
        sys.exit(f"Ziel muss direkt unter {erlaubt}/ liegen, nicht {z}")
    if z == WURZEL or WURZEL in z.parents or z in WURZEL.parents:
        sys.exit("Ziel liegt im Repo oder enthält es")
    if z.exists():
        if not z.is_dir():
            sys.exit(f"{z} ist kein Ordner")
        # nur eine frühere Kraków-Kopie dieses Skripts ersetzen, nie einen fremden Ordner
        md5 = z / "MD5SUMS"
        if any(z.iterdir()):
            if not md5.is_file():
                sys.exit(f"{z} ist nicht leer und keine frühere Deploy-Kopie (MD5SUMS fehlt); anderes --ziel wählen")
            pfade = {zeile.split("  ", 1)[1] for zeile in md5.read_text(encoding="utf-8").splitlines() if "  " in zeile}
            if "i18n.js" not in pfade or not any("/" in p and p.endswith("index.html") for p in pfade):
                sys.exit(f"{z}/MD5SUMS beschreibt keine Kraków-Kopie (Sprachseiten fehlen); anderes --ziel wählen")
        shutil.rmtree(z)
    return z


def main():
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("--deploy-wurzel", default=str(WURZEL.parent),
                   help="Ordner, der kiezatlas-deploy/ enthält (Standard: der Ordner über dem Repo)")
    a.add_argument("--ziel", help="Standard: <deploy-wurzel>/kiezatlas-deploy/krakow/<heute>")
    a.add_argument("--mit-beispieldaten", action="store_true",
                   help="auch dann kopieren, wenn unter daten/ Beispieldaten (fixture: true) liegen")
    a.add_argument("--unverkleinert", action="store_true", help="JavaScript nicht verkleinern (zum Vergleich)")
    a.add_argument("--liste", action="store_true", help="nur die Dateiliste ausgeben")
    a.add_argument("--grundkarte", help="Kachelordner der Grundkarte (Standard: $KIEZ_DATEN/abgeleitet/grundkarte/<SHA-Anfang>/)")
    a.add_argument("--gebaeude", help=f"Ordner der 3D-Dateien (Standard: $KIEZ_DATEN/abgeleitet/gebaeude/{GEB_STAND}/)")
    o = a.parse_args()
    k, basis_pfad = konfig()
    liste = dateiliste(k)
    if any(p.as_posix().startswith((GK_ZIEL + "/", GEB_ZIEL + "/")) for p in liste):
        sys.exit(f"{GK_ZIEL}/ oder {GEB_ZIEL}/ liegt im Repo; diese Ordner kommen nur von außerhalb (KR21, KR42)")
    gk_ordner = grundkarte_ordner(o.grundkarte) if braucht_grundkarte(k) else None
    gk = grundkarte_liste(gk_ordner) if gk_ordner else []
    geb_ordner = gebaeude_ordner(o.gebaeude) if braucht_gebaeude(k) else None
    geb = gebaeude_liste(geb_ordner, k) if geb_ordner else []
    if o.liste:
        print("\n".join([p.as_posix() for p in liste] + [f"{GK_ZIEL}/{p}" for p in gk] + [f"{GEB_ZIEL}/{p}" for p in geb]))
        return
    deploy_wurzel = Path(o.deploy_wurzel)
    ziel = Path(o.ziel) if o.ziel else deploy_wurzel / "kiezatlas-deploy" / "krakow" / date.today().isoformat()
    beispiel = beispieldaten(liste)
    if beispiel and not o.mit_beispieldaten:
        sys.exit("Beispieldaten unter daten/ (" + ", ".join(beispiel) + "); nur mit --mit-beispieldaten kopieren")
    ziel = ziel_pruefen(ziel, deploy_wurzel)
    seiten = set(seitenliste(k))
    stempel = str(stand(liste))
    ver = version()
    klein = []
    for p in liste:
        q, z = WURZEL / p, ziel / p
        z.parent.mkdir(parents=True, exist_ok=True)
        if p in seiten:
            z.write_text(html_umschreiben(p, q.read_text(encoding="utf-8"), stempel, ver, basis_pfad,
                                          p.name == "404.html"), encoding="utf-8")
        elif zu_verkleinern(p) and not o.unverkleinert:
            klein.append((q, z))
        elif p.suffix == ".css" and len(p.parts) == 1:
            z.write_text(css_umschreiben(q.read_text(encoding="utf-8")), encoding="utf-8")
            os.utime(z, (q.stat().st_atime, q.stat().st_mtime))
        else:
            shutil.copy2(q, z)
    esb = verkleinern(klein) if klein else None
    for q, z in klein:   # mtime der Quelle behalten (wie copy2), damit ?v= und Datei zusammenpassen
        os.utime(z, (q.stat().st_atime, q.stat().st_mtime))
    for p in gk:   # Grundkarte von außerhalb des Repos, unverändert (geprüft in grundkarte_liste)
        z = ziel / GK_ZIEL / p
        z.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(gk_ordner / p, z)
    liste_gk = [Path(GK_ZIEL) / p for p in gk]
    for p in geb:   # Gebäude in 3D von außerhalb des Repos, unverändert (geprüft in gebaeude_liste)
        z = ziel / GEB_ZIEL / p
        z.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(geb_ordner / p, z)
    liste_geb = [Path(GEB_ZIEL) / p for p in geb]
    md5 = [f"{hashlib.md5((ziel / p).read_bytes()).hexdigest()}  {p.as_posix()}" for p in liste + liste_gk + liste_geb]
    (ziel / "MD5SUMS").write_text("\n".join(md5) + "\n", encoding="utf-8")
    gz = lambda b: len(gzip.compress(b, 9, mtime=0))   # noqa: E731
    print(f"{len(liste)} Dateien ({len(seiten)} Seiten in {', '.join(k['sprachen'])}), "
          f"{sum((ziel / p).stat().st_size for p in liste) / 1e6:.1f} MB nach {ziel}")
    print(f"  KIEZ_V={stempel}, Stand {ver}, Verweise der 404-Seiten ab {basis_pfad}")
    # Einziges Inline-Skript der Auslieferung; sein Hash gehört in script-src der Content-Security-Policy
    csp = base64.b64encode(hashlib.sha256(f'window.KIEZ_V="{stempel}"'.encode("utf-8")).digest()).decode("ascii")
    print(f"  Content-Security-Policy, script-src: 'self' 'sha256-{csp}' (gilt nur für diesen Stempel, "
          "docs/auslieferung.md, Abschnitt Sicherheits-Header)")
    if klein:
        print(f"  verkleinert mit esbuild {esb}: {len(klein)} Dateien, "
              f"{sum(q.stat().st_size for q, _ in klein)} → {sum(z.stat().st_size for _, z in klein)} Byte, "
              f"gzip -9 {sum(gz(q.read_bytes()) for q, _ in klein)} → {sum(gz(z.read_bytes()) for _, z in klein)} Byte")
    if gk:
        print(f"  Grundkarte aus {gk_ordner}: {len(gk)} Dateien, "
              f"{sum((ziel / p).stat().st_size for p in liste_gk)} Byte nach {GK_ZIEL}/ (MANIFEST.sha256 geprüft)")
    if geb:
        print(f"  Gebäude 3D aus {geb_ordner}: {len(geb)} Dateien, "
              f"{sum((ziel / p).stat().st_size for p in liste_geb)} Byte nach {GEB_ZIEL}/ (Manifest geprüft)")
    if beispiel:
        print("  ACHTUNG Beispieldaten, nicht hochladen: " + ", ".join(beispiel))
    print("  MD5SUMS geschrieben. Upload und Abnahme: docs/auslieferung.md")
    remote = "<server>:/opt/www/souverain-systems.de" + basis_pfad
    print("Upload (Andre, additiv, nie --delete):")
    print(f"  rsync -az -n --itemize-changes --exclude MD5SUMS {ziel}/ {remote}   # Probelauf")
    print(f"  rsync -az --exclude MD5SUMS {ziel}/ {remote}")


if __name__ == "__main__":
    os.umask(0o022)
    main()
