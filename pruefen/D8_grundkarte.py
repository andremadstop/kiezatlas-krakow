"""Prüfung Grundkarte: eigene Vektorkacheln, Kartenschrift und daten/grundkarte.js (Regeln G1 bis G12 aus
pruefen/D8_protokoll.md).

Eigener Dekoder (unabhängig vom Kodierer in skripte/27_grundkarte.py), kein Netz, keine Datenbank. Prüft:
  G1  MANIFEST.sha256 stimmt mit jeder Datei; Eingabe-SHA256 in lauf.json = BDOT_SHA256 im Skript
  G3  jede Kachel: dekodierbar, Version 2, Ausdehnung 4096, nur MoveTo/LineTo/ClosePath mit passenden Längen,
      erster Ring jedes Polygons positiv (Y nach unten), kein Ring mit Fläche 0
  G4  jede Kachel im Rahmen (config/krakow.yaml, karte.rahmen) vorhanden, keine außerhalb
  G5  keine Kachel über 500 KB
  G6  nur erlaubte Schichten und Attribute (k, nazwa, most)
  G7  mindestens ein Straßenname mit polnischem Sonderzeichen
  G8  jede Schrift hat alle 18 polnischen Sonderzeichen als eigene, untereinander verschiedene Glyphen
  G9  jedes Zeichen aus den Namen der Kacheln steht in der Schrift der Ebene, die den Namen zeigt
      dazu schrift/OFL.txt (Copyright Noto Sans, Wortlaut OFL 1.1)
  G11 daten/grundkarte.js ohne OpenStreetMap/ODbL, mit Quellenangabe (Schema prüft pruefen/daten.py)
  G12 jede Stilebene verweist auf eine vorhandene Quellschicht und einen vorhandenen Schriftstapel

Kachelordner: --ziel DIR, sonst daten/grundkarte/ im Repo, sonst $KIEZ_DATEN/abgeleitet/grundkarte/<SHA-Anfang>/.
Fehlt er, wird nur daten/grundkarte.js geprüft und der Rest als übersprungen gemeldet (Rückgabe 0).

Aufruf: python -I pruefen/D8_grundkarte.py [--ziel DIR]   Rückgabe 0 = grün, 1 = Befund.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
import ort_konfig  # noqa: E402

KIEZ_DATEN = Path(os.environ.get("KIEZ_DATEN") or (WURZEL.parent / "kiezatlas-daten" / "krakow"))
SKRIPT = WURZEL / "skripte" / "27_grundkarte.py"
JS = WURZEL / "daten" / "grundkarte.js"
SCHICHTEN = {"teren", "zielen", "woda", "cieki", "tory", "sciezki", "drogi", "miejsca"}
ATTRIBUTE = {"k", "nazwa", "most"}
POLNISCH = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
MAX_KACHEL = 500 * 1024
befunde: list[str] = []


def pruef(ok: bool, text: str) -> bool:
    print(("  ok    " if ok else "  FEHLT ") + text)
    if not ok:
        befunde.append(text)
    return ok


# ---------------------------------------------------------------- Protobuf lesen
def lies_varint(b: bytes, i: int) -> tuple[int, int]:
    n = s = 0
    while True:
        c = b[i]
        i += 1
        n |= (c & 0x7F) << s
        s += 7
        if not c & 0x80:
            return n, i


def felder(b: bytes):
    """(Feldnummer, Typ, Wert) je Feld; Wert = int (Typ 0) oder bytes (Typ 2)."""
    i = 0
    while i < len(b):
        schl, i = lies_varint(b, i)
        nr, typ = schl >> 3, schl & 7
        if typ == 0:
            v, i = lies_varint(b, i)
        elif typ == 2:
            n, i = lies_varint(b, i)
            v = b[i:i + n]
            if len(v) != n:
                raise ValueError("abgeschnittenes Feld")
            i += n
        elif typ == 5:
            v, i = b[i:i + 4], i + 4
        elif typ == 1:
            v, i = b[i:i + 8], i + 8
        else:
            raise ValueError(f"Drahttyp {typ}")
        yield nr, typ, v


def gepackt(b: bytes) -> list[int]:
    out, i = [], 0
    while i < len(b):
        v, i = lies_varint(b, i)
        out.append(v)
    return out


def unzz(n: int) -> int:
    return (n >> 1) ^ -(n & 1)


def geometrie(befehle: list[int], typ: int) -> list[list[tuple[int, int]]]:
    """Befehlsfolge zu Ringen/Linien/Punktgruppen; wirft ValueError bei ungültiger Folge."""
    teile, akt, x, y, i = [], [], 0, 0, 0
    while i < len(befehle):
        cmd, n = befehle[i] & 7, befehle[i] >> 3
        i += 1
        if cmd == 1:
            if typ != 1 and n != 1:
                raise ValueError("MoveTo mit mehr als einem Punkt in Linie/Fläche")
            if akt:
                teile.append(akt)
            akt = []
        elif cmd == 2:
            if not akt:
                raise ValueError("LineTo ohne MoveTo")
        elif cmd == 7:
            if typ != 3 or n != 1:
                raise ValueError("ClosePath außerhalb einer Fläche")
            teile.append(akt)
            akt = []
            continue
        else:
            raise ValueError(f"Befehl {cmd}")
        if i + 2 * n > len(befehle):
            raise ValueError("zu wenige Parameter")
        for _ in range(n):
            x += unzz(befehle[i])
            y += unzz(befehle[i + 1])
            i += 2
            akt.append((x, y))
    if akt:
        teile.append(akt)
    return teile


def flaeche(r) -> int:
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r)))


def kachel_lesen(b: bytes) -> dict:
    """Rückgabe {Schicht: [(typ, attribute)]}; wirft ValueError bei Regelverstoß gegen G3."""
    schichten = {}
    for nr, _, lb in felder(b):
        if nr != 3:
            raise ValueError(f"Feld {nr} in Tile")
        name, version, extent, schl, werte, feats = None, None, None, [], [], []
        for fnr, _, v in felder(lb):
            if fnr == 1:
                name = v.decode("utf-8")
            elif fnr == 15:
                version = v
            elif fnr == 5:
                extent = v
            elif fnr == 3:
                schl.append(v.decode("utf-8"))
            elif fnr == 4:
                wert = None
                for vnr, _, vv in felder(v):
                    wert = vv.decode("utf-8") if vnr == 1 else bool(vv) if vnr == 7 else vv
                werte.append(wert)
            elif fnr == 2:
                feats.append(v)
        if version != 2 or extent != 4096:
            raise ValueError(f"Schicht {name}: Version {version}, Ausdehnung {extent}")
        liste = []
        for f in feats:
            tags, typ, geo = [], 0, []
            for gnr, _, v in felder(f):
                if gnr == 2:
                    tags = gepackt(v)
                elif gnr == 3:
                    typ = v
                elif gnr == 4:
                    geo = gepackt(v)
            if typ not in (1, 2, 3) or len(tags) % 2:
                raise ValueError(f"Schicht {name}: Typ {typ}, Tags ungerade")
            teile = geometrie(geo, typ)
            if typ == 3:
                if not teile or flaeche(teile[0]) <= 0:
                    raise ValueError(f"Schicht {name}: erster Ring nicht positiv")
                if any(len(r) < 3 or flaeche(r) == 0 for r in teile):
                    raise ValueError(f"Schicht {name}: Ring mit Fläche 0")
            if typ == 2 and any(len(t) < 2 for t in teile):
                raise ValueError(f"Schicht {name}: Linie mit weniger als 2 Punkten")
            attr = {schl[tags[j]]: werte[tags[j + 1]] for j in range(0, len(tags), 2)}
            liste.append((typ, attr))
        schichten[name] = liste
    return schichten


def glyphen_lesen(b: bytes) -> dict[int, bytes]:
    out = {}
    for nr, _, stack in felder(b):
        if nr != 1:
            continue
        for snr, _, g in felder(stack):
            if snr != 3:
                continue
            gid, bitmap = None, b""
            for gnr, _, v in felder(g):
                if gnr == 1:
                    gid = v
                elif gnr == 2:
                    bitmap = v
            out[gid] = bitmap
    return out


# ---------------------------------------------------------------- Kachelordner
def kacheln_im_rahmen(rahmen, z):
    def kachel(lon, lat):
        n = 2 ** z
        x = int((lon + 180) / 360 * n)
        y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
        return min(max(x, 0), n - 1), min(max(y, 0), n - 1)
    x0, y0 = kachel(rahmen[0], rahmen[3])
    x1, y1 = kachel(rahmen[2], rahmen[1])
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def ordner_finden(arg: Path | None) -> Path | None:
    soll = re.search(r'BDOT_SHA256 = "([0-9a-f]{64})"', SKRIPT.read_text(encoding="utf-8")).group(1)
    for p in ([arg] if arg else [WURZEL / "daten" / "grundkarte", KIEZ_DATEN / "abgeleitet" / "grundkarte" / soll[:12]]):
        if p and (p / "MANIFEST.sha256").exists():
            return p
    return None


def js_lesen() -> dict:
    text = JS.read_text(encoding="utf-8")
    m = re.search(r"window\.KIEZ_GRUNDKARTE\s*=\s*", text)
    return text, json.loads(text[m.end():].rstrip().rstrip(";"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ziel", type=Path)
    arg = ap.parse_args()
    soll_sha = re.search(r'BDOT_SHA256 = "([0-9a-f]{64})"', SKRIPT.read_text(encoding="utf-8")).group(1)

    print("G11 daten/grundkarte.js")
    if not JS.exists():
        pruef(False, "daten/grundkarte.js fehlt")
        return 1
    text, gk = js_lesen()
    pruef(not re.search(r"OpenStreetMap|\bODbL\b", text), "kein OpenStreetMap/ODbL (Dateigrenze, pruefen/daten.py Punkt 4)")
    pruef("BDOT10k" in gk["vermerk"] and "Główny Urząd Geodezji i Kartografii" in gk["vermerk"],
          "Vermerk nennt BDOT10k und den Główny Urząd Geodezji i Kartografii (art. 40c ust. 3)")
    pruef(gk["quelle"]["attribution"] == gk["vermerk"], "Bildzeile der Quelle = Vermerk")
    pruef(all(not t.startswith(("http:", "https:", "/")) for t in gk["quelle"]["tiles"] + [gk["glyphs"]]),
          "Kacheln und Schrift relativ zur Atlas-Wurzel (selbst gehostet, kein fremder Rechner)")

    ziel = ordner_finden(arg.ziel)
    if ziel is None:
        print("  übersprungen: kein Kachelordner mit MANIFEST.sha256 (erst skripte/27_grundkarte.py laufen lassen)")
        print(f"\nGrundkarte: {len(befunde)} Befund(e), Kacheln übersprungen")
        return 1 if befunde else 0
    print(f"Kachelordner {ziel}")

    print("G1 Manifest und Eingabe")
    zeilen = [z.split("  ", 1) for z in (ziel / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines()]
    falsch = [p for h, p in zeilen
              if not (ziel / p).is_file() or hashlib.sha256((ziel / p).read_bytes()).hexdigest() != h]
    alle = sorted(p.relative_to(ziel).as_posix() for p in ziel.rglob("*.pbf"))
    pruef(not falsch and alle == sorted(p for _, p in zeilen),
          f"{len(zeilen)} Dateien im Manifest, Prüfsummen stimmen, keine Datei außerhalb" + (f" (falsch: {falsch[:3]})" if falsch else ""))
    lauf = json.loads((ziel / "lauf.json").read_text(encoding="utf-8"))
    pruef(lauf["eingabe"]["sha256"] == soll_sha, f"Eingabe BDOT10k 1261 mit SHA256 {soll_sha[:16]}…")

    print("G3–G7 Kacheln")
    rahmen = ort_konfig.lade()["karte"]["rahmen"]
    zmin, zmax = gk["quelle"]["minzoom"], gk["quelle"]["maxzoom"]
    namen_zeichen: dict[str, set[str]] = {}
    polnisch_name = None
    fehler_g3, gross, schichten_ist, attr_fremd, anzahl = [], [], set(), set(), 0
    for z in range(zmin, zmax + 1):
        soll = kacheln_im_rahmen(rahmen, z)
        ist = {(int(p.parent.name), int(p.stem)) for p in (ziel / "kacheln" / str(z)).glob("*/*.pbf")}
        pruef(ist == soll, f"z{z}: {len(ist)} Kacheln, Rahmen verlangt {len(soll)}"
              + (f" (fehlen {len(soll - ist)}, zu viel {len(ist - soll)})" if ist != soll else ""))
        for x, y in sorted(ist):
            p = ziel / "kacheln" / str(z) / str(x) / f"{y}.pbf"
            b = p.read_bytes()
            anzahl += 1
            if len(b) > MAX_KACHEL:
                gross.append(f"{z}/{x}/{y} {len(b)} B")
            try:
                sch = kachel_lesen(b)
            except (ValueError, IndexError, UnicodeDecodeError) as e:
                fehler_g3.append(f"{z}/{x}/{y}: {e}")
                continue
            for name, feats in sch.items():
                schichten_ist.add(name)
                for _, a in feats:
                    attr_fremd |= set(a) - ATTRIBUTE
                    n = a.get("nazwa")
                    if isinstance(n, str):
                        namen_zeichen.setdefault(name, set()).update(n)
                        if name == "drogi" and polnisch_name is None and set(n) & set(POLNISCH):
                            polnisch_name = n
    pruef(not fehler_g3, f"G3 {anzahl} Kacheln dekodiert, gültiges MVT 2.1" + (f": {fehler_g3[:3]}" if fehler_g3 else ""))
    pruef(not gross, "G5 keine Kachel über 500 KB" + (f": {gross[:3]}" if gross else ""))
    pruef(schichten_ist <= SCHICHTEN, f"G6 Schichten {sorted(schichten_ist)} nur aus der Liste")
    pruef(not attr_fremd, "G6 nur Attribute k, nazwa, most" + (f" (fremd: {sorted(attr_fremd)})" if attr_fremd else ""))
    pruef(polnisch_name is not None, f"G7 Straßenname mit polnischem Sonderzeichen in den Kacheln: „{polnisch_name}“")

    print("G8–G9 Kartenschrift")
    stapel_ebenen = {}
    for e in gk["oben"]:
        for f in e.get("layout", {}).get("text-font", []):
            stapel_ebenen.setdefault(f, set()).add(e["source-layer"])
    for stapel, ebenen in sorted(stapel_ebenen.items()):
        glyphen = {}
        for p in sorted((ziel / "schrift" / stapel).glob("*.pbf")):
            glyphen.update(glyphen_lesen(p.read_bytes()))
        bitmaps = [glyphen.get(ord(c)) for c in POLNISCH]
        pruef(all(bitmaps) and len(set(bitmaps)) == len(POLNISCH),
              f"G8 {stapel}: {len(glyphen)} Glyphen, alle 18 polnischen Sonderzeichen eigene Glyphen")
        brauche = set().union(*(namen_zeichen.get(s, set()) for s in ebenen))
        fehlt = sorted(c for c in brauche if ord(c) not in glyphen)
        pruef(not fehlt, f"G9 {stapel}: {len(brauche)} Zeichen aus den Namen von {sorted(ebenen)} vorhanden"
              + (f" (fehlen: {''.join(fehlt)})" if fehlt else ""))

    ofl = ziel / "schrift" / "OFL.txt"
    ofl_text = ofl.read_text(encoding="utf-8") if ofl.exists() else ""
    pruef("SIL OPEN FONT LICENSE Version 1.1" in ofl_text and "The Noto Project Authors" in ofl_text,
          "schrift/OFL.txt mit Copyright von Noto Sans und Wortlaut der OFL 1.1 (Lizenz geht mit den Glyphen)")

    print("G12 Stil")
    for e in gk["unten"] + gk["oben"]:
        pruef(e["source"] == "bm" and e["source-layer"] in SCHICHTEN and e["id"].startswith("bm-"),
              f"{e['id']}: Quellschicht {e['source-layer']}")
    for stapel in stapel_ebenen:
        pruef((ziel / "schrift" / stapel).is_dir(), f"Schriftstapel {stapel} vorhanden")

    print(f"\nGrundkarte: {len(befunde)} Befund(e)")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
