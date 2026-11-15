"""Langtexte der Methoden- und Datenseiten: setzt jede Zahl aus den Datendateien in die Quelltexte ein.

Quelle:  texte/<lang>/bloecke/quelle/<block>.html   Langtext mit Platzhaltern
Ziel:    texte/<lang>/bloecke/<block>.html          fertiger Block, den skripte/30_seiten.py in die Seite setzt

Platzhalter  [[datei:pfad|format]]
  datei    Datendatei unter daten/ ohne .js (z. B. steckbrief, planer_fuss_odbl), richtwerte (config/richtwerte.yaml:
           Richtwerte mit Fundstelle und eigene Festlegungen der Rechnung, etwa der Radius für Haltestellen) oder konfig
           (config/krakow.yaml, etwa die Adresse des Repositorys)
  pfad     Schlüssel mit Punkt getrennt; Listen über die Stelle (features.0) oder über einen Filter, der genau ein
           Element treffen muss: werte[kennzahl=anteil_in_radius,art=szkola,richtwert.wert=3000]
  format   zahl (Standard, wie KIEZ_I18N.fmt.zahl), zahl0, zahl1, zahl2 (feste Nachkommastellen), anteil, anteil0
           anteil1, anteil2 (Prozent wie fmt.anteil, Wert 0 … 100), datum (Tag, Monat ausgeschrieben, Jahr), text (Zeichenkette wörtlich),
           anzahl (Länge einer Liste oder eines Objekts; mit Filter: Zahl der Treffer), adresse (https-Adresse,
           maskiert und ohne Spanne, für href="…")
Bedingung    [[wenn datei:pfad]] … [[sonst]] … [[ende]]   (sonst-Teil optional, nicht geschachtelt)
           Der erste Teil gilt, wenn der Pfad auflösbar ist und sein Wert weder null, false noch leer ist, sonst der
           zweite. So fällt ein Text auf den Hinweis „ungeprüft“ zurück, solange eine Sichtprüfung fehlt (etwa ohne
           belege/DZ_sichtpruefung.json), und ein Verweis erscheint erst, wenn die Adresse in der Konfiguration steht.
Aus jedem Platzhalter wird <span data-feld="datei:pfad">Wert</span>; Texte (format text) bekommen dazu lang="pl", wenn
die Zeichenkette polnisch ist und die Seite nicht (Vermerke bleiben in der Originalsprache). Zahlen formatiert
Node.js mit i18n.js selbst (Intl der Seitensprache), damit die Langtexte dieselbe Schreibweise haben wie die Seiten.
Lizenzvermerk ODbL: Löst ein Block mindestens einen Platzhalter aus einer _odbl-Datei auf (Werte auf den OSM-Grenzen,
Lizenzfolge Variante a), endet er mit dem Vermerk kern.odbl der Sprache und dem Link auf openstreetmap.org/copyright.
So steht der Vermerk auf jeder Seite, die solche Werte zeigt, auch wenn sie die _odbl-Datei nicht als Skript lädt.

Kein Netz, keine Datenbank. Python aus requirements.txt (pyyaml), Node.js für die Zahlenformate. Dateien mit fixture: true dürfen nur mit dem Format text oder als Stand genannt werden;
eine Zahl aus einer Beispieldatei bricht ab.

Aufruf:
  python -I skripte/16_bloecke_krakow.py            alle Blöcke schreiben
  python -I skripte/16_bloecke_krakow.py --pruefen  erzeugen und mit den eingecheckten Blöcken vergleichen (Rückgabe 1
                                                    bei Abweichung oder fehlendem Block)
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
import textschicht  # noqa: E402

DATEN = WURZEL / "daten"
TEXTE = WURZEL / "texte"
SPRACHEN = ("pl", "en", "de")
PLATZ = re.compile(r"\[\[([a-z0-9_]+):((?:[^|\[\]]|\[[^\[\]]*\])+)(?:\|([a-z0-9]+))?\]\]")
FORMATE = {"zahl", "zahl0", "zahl1", "zahl2", "anteil", "anteil0", "anteil1", "anteil2", "datum", "text", "anzahl",
           "adresse"}
WENN = re.compile(r"\[\[wenn ([a-z0-9_]+):([^\]\s]+)\]\](.*?)(?:\[\[sonst\]\](.*?))?\[\[ende\]\]", re.S)
# In Beispieldateien sind nur diese Teile echt (docs/rundgang.md, „Datenstand je Thema“; Mindestfallzahl laut Entscheidung
# zum Wohnungsmarkt); nur aus ihnen darf eine Zahl stammen.
FIXTURE_ECHT = {"mieszkania_odbl": ("regeln",), "powietrze": ("grenzwerte", "kontekst")}
POLNISCH = re.compile(r"[ąćęłńśźżĄĆĘŁŃŚŹŻ]")
ODBL_LINK = "https://www.openstreetmap.org/copyright"


def odbl_vermerk(lang: str) -> str:
    """Vermerk für Blöcke mit Werten aus _odbl-Dateien; Wortlaut wie im Seitenfuß (kern.odbl)."""
    t = textschicht.flach(lang).get("kern.odbl")
    if not isinstance(t, str):
        raise Fehler(f"kern.odbl fehlt in texte/{lang}/kern.js")
    return (f'<p class="odbl-vermerk"><small>{html.escape(t, quote=False)} <a class="link" href="{ODBL_LINK}">'
            f'openstreetmap.org/copyright</a>.</small></p>')

NODE = r"""
const fs = require("fs"), vm = require("vm");
const auftrag = JSON.parse(fs.readFileSync(0, "utf8"));
const quelle = fs.readFileSync(auftrag.i18n, "utf8");
const fmt = {};
for (const lang of ["pl", "en", "de"]) {
  const w = { document: { documentElement: { getAttribute: () => lang } } };
  w.window = w; vm.createContext(w); vm.runInContext(quelle, w);
  fmt[lang] = w.KIEZ_I18N.fmt;
}
const aus = auftrag.werte.map(([lang, art, x]) => {
  const f = fmt[lang];
  if (art === "zahl") return f.zahl(x);
  if (art.startsWith("zahl")) return f.zahl(x, Number(art.slice(4)));
  if (art === "anteil") return f.anteil(x);
  if (art.startsWith("anteil")) return f.anteil(x, Number(art.slice(6)));
  if (art === "datum") return f.datum(x + "T12:00:00Z", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
  throw new Error("Format " + art);
});
process.stdout.write(JSON.stringify(aus));
"""


class Fehler(Exception):
    pass


def daten(name: str, cache: dict) -> dict:
    yaml_datei = {"richtwerte": "richtwerte.yaml", "konfig": "krakow.yaml"}   # Richtwerte; Ortskonfiguration
    if name not in cache and name in yaml_datei:
        import yaml
        roh = yaml.safe_load((WURZEL / "config" / yaml_datei[name]).read_text(encoding="utf-8"))
        cache[name] = json.loads(json.dumps(roh, default=str))
    if name not in cache:
        p = DATEN / f"{name}.js"
        if not p.exists():
            raise Fehler(f"daten/{name}.js gibt es nicht")
        t = p.read_text(encoding="utf-8")
        m = re.search(r"window\.[A-Za-z0-9_]+\s*=\s*", t)
        cache[name] = json.loads(t[m.end():].rstrip().rstrip(";"))
    return cache[name]


def schritte(pfad: str) -> list[str]:
    """Pfad in Schritte zerlegen; Punkte innerhalb eckiger Klammern gehören zum Filter."""
    aus, tief, akt = [], 0, ""
    for ch in pfad:
        if ch == "." and tief == 0:
            aus.append(akt)
            akt = ""
            continue
        tief += ch == "["
        tief -= ch == "]"
        akt += ch
    aus.append(akt)
    return aus


def holen(o, weg: str):
    for k in weg.split("."):
        o = o[k] if isinstance(o, dict) else o[int(k)]
    return o


def passt(e, bedingungen: list[tuple[str, str]]) -> bool:
    for k, v in bedingungen:
        try:
            w = holen(e, k)
        except (KeyError, IndexError, ValueError, TypeError):
            return False
        s = json.dumps(w) if isinstance(w, bool) or w is None else str(w)
        if s != v:
            return False
    return True


def aufloesen(obj, pfad: str, anzahl: bool):
    o = obj
    teile = schritte(pfad)
    for i, s in enumerate(teile):
        m = re.fullmatch(r"([^\[]*)(?:\[(.*)\])?", s)
        k, filt = m.group(1), m.group(2)
        if k:
            if isinstance(o, dict):
                if k not in o:
                    raise Fehler(f"Schlüssel {k} fehlt")
                o = o[k]
            elif isinstance(o, list) and re.fullmatch(r"\d+", k):
                o = o[int(k)]
            else:
                raise Fehler(f"{k}: weder Schlüssel noch Stelle")
        if filt is not None:
            bed = [tuple(b.split("=", 1)) for b in filt.split(",")]
            werte = list(o.values()) if isinstance(o, dict) else o
            treffer = [e for e in werte if passt(e, bed)]
            if anzahl and i == len(teile) - 1:
                return len(treffer)
            if len(treffer) != 1:
                raise Fehler(f"Filter [{filt}] trifft {len(treffer)} statt genau 1")
            o = treffer[0]
    if anzahl:
        if not isinstance(o, (list, dict)):
            raise Fehler("anzahl braucht eine Liste oder ein Objekt")
        return len(o)
    return o


def bloecke() -> list[tuple[str, str]]:
    namen = sorted({p.stem for l in SPRACHEN for p in (TEXTE / l / "bloecke" / "quelle").glob("*.html")})
    for n in namen:
        for l in SPRACHEN:
            if not (TEXTE / l / "bloecke" / "quelle" / f"{n}.html").exists():
                raise Fehler(f"texte/{l}/bloecke/quelle/{n}.html fehlt (jeder Block in allen Sprachen)")
    return [(l, n) for n in namen for l in SPRACHEN]


def bedingungen(quelle: str, cache: dict, ort: str) -> str:
    """[[wenn datei:pfad]] … [[sonst]] … [[ende]] auflösen, bevor die Platzhalter drankommen."""
    def eins(m: re.Match) -> str:
        try:
            w = aufloesen(daten(m.group(1), cache), m.group(2), False)
        except (KeyError, IndexError, ValueError, TypeError):
            w = None
        except Fehler as x:
            if "gibt es nicht" in str(x):
                raise Fehler(f"{ort}: [[wenn {m.group(1)}:{m.group(2)}]]: {x}") from None
            w = None
        return m.group(3) if w not in (None, False, "", [], {}) else (m.group(4) or "")
    aus = WENN.sub(eins, quelle)
    if re.search(r"\[\[(wenn |sonst\]\]|ende\]\])", aus):
        raise Fehler(f"{ort}: Bedingung nicht lesbar ([[wenn …]] … [[sonst]] … [[ende]], nicht geschachtelt)")
    return aus


def erzeugen(vorgabe: dict | None = None) -> dict[Path, str]:
    """vorgabe: Inhalte von Datendateien statt der Dateien (Name ohne .js → Inhalt), für Prüfungen ohne Schreiben."""
    cache: dict = json.loads(json.dumps(vorgabe)) if vorgabe else {}
    auftraege: list = []          # (lang, format, wert) für Node
    stuecke: dict[Path, list] = {}
    for lang, name in bloecke():
        quelle = (TEXTE / lang / "bloecke" / "quelle" / f"{name}.html").read_text(encoding="utf-8")
        quelle = bedingungen(quelle, cache, f"texte/{lang}/bloecke/quelle/{name}.html")
        teile: list = []
        pos = 0
        odbl = False
        for m in PLATZ.finditer(quelle):
            datei, pfad, art = m.group(1), m.group(2), m.group(3) or "zahl"
            odbl = odbl or datei.endswith("_odbl")
            ort = f"texte/{lang}/bloecke/quelle/{name}.html: [[{datei}:{pfad}|{art}]]"
            if art not in FORMATE:
                raise Fehler(f"{ort}: unbekanntes Format")
            d = daten(datei, cache)
            try:
                w = aufloesen(d, pfad, art == "anzahl")
            except (Fehler, KeyError, IndexError, ValueError, TypeError) as x:
                raise Fehler(f"{ort}: {x}") from None
            if d.get("fixture") is True and art not in ("text", "datum") \
                    and not pfad.startswith(FIXTURE_ECHT.get(datei, ("\0",))):
                raise Fehler(f"{ort}: Zahl aus einer Beispieldatei (echt sind dort nur {FIXTURE_ECHT.get(datei, ())})")
            teile.append(quelle[pos:m.start()])
            feld = html.escape(f"{datei}:{pfad}", quote=True)
            if art == "adresse":
                if not (isinstance(w, str) and re.fullmatch(r"https://[^\s\"<>]+", w)):
                    raise Fehler(f"{ort}: Format adresse braucht eine https-Adresse, nicht {w!r}")
                teile.append(html.escape(w, quote=True))
            elif art == "text":
                if not isinstance(w, str):
                    raise Fehler(f"{ort}: Format text braucht eine Zeichenkette, nicht {type(w).__name__}")
                spr = ' lang="pl"' if lang != "pl" and POLNISCH.search(w) else ""
                teile.append(f'<span data-feld="{feld}"{spr}>{html.escape(w, quote=False)}</span>')
            else:
                if art == "datum":
                    if not (isinstance(w, str) and re.match(r"\d{4}-\d{2}-\d{2}", w)):
                        raise Fehler(f"{ort}: kein Datum ({w!r})")
                    w = w[:10]
                elif isinstance(w, bool) or not isinstance(w, (int, float)):
                    raise Fehler(f"{ort}: keine Zahl ({w!r})")
                teile.append((len(auftraege), feld))
                auftraege.append([lang, "zahl" if art == "anzahl" else art, w])
            pos = m.end()
        teile.append(quelle[pos:].rstrip())
        if odbl:
            teile.append("\n\n" + odbl_vermerk(lang))
        rest = re.search(r"\[\[[^\]]*\]\]", quelle[pos:])
        if rest or any(isinstance(t, str) and "[[" in t for t in teile):
            raise Fehler(f"texte/{lang}/bloecke/quelle/{name}.html: Platzhalter nicht lesbar")
        stuecke[TEXTE / lang / "bloecke" / f"{name}.html"] = teile
    r = subprocess.run(["node", "-e", NODE], input=json.dumps({"i18n": str(WURZEL / "i18n.js"), "werte": auftraege}),
                       capture_output=True, text=True, check=False)
    if r.returncode:
        raise Fehler(f"Node: {r.stderr.strip()}")
    formatiert = json.loads(r.stdout)
    aus = {}
    for p, teile in stuecke.items():
        s = "".join(t if isinstance(t, str) else f'<span data-feld="{t[1]}">{html.escape(formatiert[t[0]])}</span>'
                    for t in teile)
        kopf = ("<!-- erzeugt von skripte/16_bloecke_krakow.py aus quelle/" + p.name
                + "; nicht von Hand ändern, Zahlen kommen aus daten/ -->\n")
        aus[p] = kopf + s.strip() + "\n"
    return aus


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("--pruefen", action="store_true")
    o = a.parse_args()
    try:
        neu = erzeugen()
    except Fehler as x:
        print(f"  FEHLT Langtexte: {x}")
        return 1
    if not o.pruefen:
        for p, t in neu.items():
            p.write_text(t, encoding="utf-8")
        print(f"{len(neu)} Blöcke geschrieben")
        return 0
    ab = [p for p, t in neu.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
    for p in ab:
        print(f"  FEHLT {p.relative_to(WURZEL)} ist nicht aktuell (python -I skripte/16_bloecke_krakow.py)")
    if not ab:
        print(f"  ok    {len(neu)} Blöcke entsprechen ihren Quelltexten und den Datendateien")
    return 1 if ab else 0


if __name__ == "__main__":
    sys.exit(main())
