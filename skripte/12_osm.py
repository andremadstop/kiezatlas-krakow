"""OSM-Einrichtungen und Fußwegnetz aus einem von Hand geladenen OSM-Auszug (offline) nach auswertung.*.

Eingang: eine OpenStreetMap-PBF, von Andre von Hand geladen (Geofabrik-Auszug „malopolskie“, Woiwodschaft
Kleinpolen), abgelegt unter $KIEZ_DATEN/osm/<stand>/ (nicht im gemeinsamen eingang/), <stand> = Datenstand der
Datei. Liegt die PBF noch im gemeinsamen Eingang ($KIEZ_DATEN/eingang/), übernimmt `--uebernehmen` sie: Kopie
(nicht verschieben) nach $KIEZ_DATEN/osm/<stand>/, <stand> aus dem Dateikopf (osmosis_replication_timestamp) oder
aus `--stand JJJJ-MM-TT`, die <datei>.md5 daneben mit; danach läuft alles auf der Kopie. Kein Netzabruf: kein Overpass, kein osmnx-Download, kein Abruf bei Geofabrik oder BBBike (beide Rechner
sperrt skripte/abruf.py). Liegt neben der PBF die Prüfsummendatei von Geofabrik (<datei>.md5), wird sie verglichen.

Ausgang (Rolle kiezatlas_rechnen, nur eigene Tabellen laut Eigentümer-Tabelle in docs/rundgang.md):
- auswertung.osm_poi    Ärzte, Apotheken, Supermärkte, Pflege, Spielplätze. Ohne Namen.
- auswertung.netz_knoten, auswertung.netz_kante   Fußwegnetz (jeder OSM-Knoten eines begehbaren Wegs
                        ist ein Netzknoten, jede Kante ein gerades Stück zwischen zwei Knoten, ungerichtet)
- berichte/osm_netz.md  Herkunft der PBF (SHA256), Abdeckung, Netzkennzahlen mit dem Anteil der größten
                        Komponente, Einrichtungen je Art, Abgleich mit einer amtlichen Liste (falls geladen)

Lizenz: alles Abgeleitete steht unter ODbL 1.0, © OpenStreetMap-Mitwirkende. Veröffentlicht wird es nur in
Dateien mit _odbl im Namen, nie in Dateien unter anderer Lizenz.

Ausschnitt: Umring der 18 dzielnice (public.stadtteil, Grenzen aus OSM) plus 2 km (EPSG:<rechen_srid>). Gelesen
wird ein Rechteck darum (plus Rand), behalten werden Kanten und Einrichtungen, die den Puffer berühren. Einen
Landesfilter gibt es nicht: Alles im Puffer zählt, auch in den Nachbargemeinden.

Herkunft (Rohdaten-Hash): Die SHA256 der PBF wird bei jedem Lauf berechnet und muss in HERKUNFT.md neben der
Datei stehen. Fehlt HERKUNFT.md, legt das Skript sie mit der Prüfsumme an; steht dort eine andere Prüfsumme für
dieselbe Datei, bricht es ab. --hash-eintragen trägt eine fehlende Prüfsumme in eine vorhandene HERKUNFT.md nach.

Aufruf über skripte/12_osm.sh (Umgebung und Rolle wie skripte/lauf.sh); der echte Lauf braucht Speicher, also:
    systemd-run --user --scope -p MemoryMax=6G skripte/12_osm.sh laden --pbf $KIEZ_DATEN/osm/<stand>/malopolskie-latest.osm.pbf
    skripte/12_osm.sh laden --pbf … --trockenlauf     (alles in einer Transaktion, am Ende ROLLBACK)
    skripte/12_osm.sh pruefen                          (Abnahme gegen die Datenbank, pruefen/a3_pruefen.py)
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import math
import os
import re
import shutil
import sys
import time
from pathlib import Path

import numpy as np

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # eigener Code; python -I lässt das Skriptverzeichnis weg
import osm_pbf
from ort_konfig import RECHEN_SRID, srs_name  # noqa: E402  Rechen-Koordinatensystem aus config/<ort>.yaml

PUFFER_M = 2000
RAND_GRAD = 0.01            # Leserechteck um den Puffer, damit Wege am Rand ihre Knoten behalten
DUBLETTE_M = 25             # Fläche und Punkt derselben Art näher als das: nur der Punkt bleibt
TREFFER_M = 150             # Abgleich: amtlicher Standort hat OSM-Gegenstück in diesem Abstand
ODBL = "ODbL 1.0, © OpenStreetMap-Mitwirkende (https://opendatacommons.org/licenses/odbl/1-0/)"

# ------------------------------------------------------------------------------- Regeln (rein)

FUSS_JA = {"yes", "designated", "permissive", "official"}
# Nicht begehbar oder kein Weg. Wie das Netz „walk“ von osmnx, aber Radwege (highway=cycleway) nur mit
# ausdrücklicher Fußfreigabe (foot=yes/designated …). Das ist eine Lesart der OSM-Auszeichnung, keine Aussage
# über polnisches Verkehrsrecht: Ob Fußgänger einen Radweg ohne Gehweg daneben benutzen dürfen, ist nicht
# geprüft (offen in docs/entscheidungen/osm-fussweg.md). Die Regel kann das Netz nur verkleinern, nie Wege
# erfinden; Fußwege werden dadurch eher zu lang als zu kurz.
HIGHWAY_AUS = {
    "motorway", "motorway_link", "bus_guideway", "busway", "raceway", "construction", "proposed",
    "planned", "abandoned", "razed", "disused", "no", "platform", "corridor", "escape",
    "emergency_bay", "rest_area", "services",
}


def ist_fussweg(t: dict[str, str]) -> bool:
    """Ist ein OSM-Weg für Fußgänger begehbar?"""
    hw = t.get("highway")
    if not hw or hw in HIGHWAY_AUS:
        return False
    foot = t.get("foot")
    if foot in ("no", "use_sidepath", "private"):
        return False
    erlaubt = foot in FUSS_JA
    if hw == "cycleway" and not erlaubt:
        return False
    if t.get("motorroad") == "yes" and not erlaubt:
        return False
    if t.get("access") in ("no", "private") and not erlaubt:
        return False
    return not (t.get("service") == "private" and not erlaubt)


def poi_art(t: dict[str, str]) -> tuple[str, str | None] | None:
    """(art, unterart) für die Einrichtungen aus OSM, sonst None. Namen werden nie gelesen."""
    a = t.get("amenity")
    hc = t.get("healthcare")
    if a == "doctors" or (a is None and hc == "doctor"):
        sp = t.get("healthcare:speciality")
        return "arzt", (sp[:120] if sp else None)
    if a == "pharmacy" or (a is None and hc == "pharmacy"):
        return "apotheke", None
    shop = t.get("shop")
    if shop in ("supermarket", "convenience"):
        return "supermarkt", shop
    if a == "nursing_home":
        return "pflege", "nursing_home"
    if a == "social_facility":
        sf = t.get("social_facility")
        fuer = t.get("social_facility:for", "")
        if sf in ("nursing_home", "assisted_living") or (sf == "group_home" and "senior" in fuer):
            return "pflege", sf
        return None
    if t.get("leisure") == "playground":
        if t.get("access") in ("private", "no"):
            return None   # Spielplätze auf Kita- oder Hausgrundstücken
        return "spielplatz", None
    return None


def bildung_art(t: dict[str, str]) -> str | None:
    """Nur für den Vollständigkeitsbericht (nicht in osm_poi)."""
    a = t.get("amenity")
    if a == "kindergarten":
        return "kita"
    if a == "school":
        return "schule"
    return None


def ist_flaeche_relation(t: dict[str, str]) -> bool:
    return t.get("type") == "multipolygon" and (poi_art(t) is not None or bildung_art(t) is not None)


def netz_bauen(wege: list[tuple[int, dict, np.ndarray]], erg: osm_pbf.Ergebnis
               ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Kanten (von, nach) und Knoten (id, lon, lat) aus begehbaren Wegen.

    Jede Folge zweier Knoten eines Wegs wird eine ungerichtete Kante. Fehlt einem Knoten die Koordinate
    (außerhalb des Leserechtecks), entfallen die Kanten daran; der Weg zerfällt an der Stelle. Doppelte
    Kanten (zwei Wege über dieselben Knoten) und Schleifen (gleicher Knoten zweimal) entfallen.
    """
    teile_a, teile_b = [], []
    for _wid, _t, refs in wege:
        if refs.size < 2:
            continue
        _lon, _lat, ok = erg.koordinaten(refs)
        beide = ok[:-1] & ok[1:]
        a, b = refs[:-1][beide], refs[1:][beide]
        teile_a.append(a)
        teile_b.append(b)
    if not teile_a:
        leer = np.zeros(0, dtype=np.int64)
        return leer, leer.copy(), leer.copy(), np.zeros(0)
    a = np.concatenate(teile_a)
    b = np.concatenate(teile_b)
    keine_schleife = a != b
    a, b = a[keine_schleife], b[keine_schleife]
    von = np.minimum(a, b)
    nach = np.maximum(a, b)
    paare = np.unique(np.stack([von, nach], axis=1), axis=0)
    knoten = np.unique(paare.ravel())
    lon, lat, ok = erg.koordinaten(knoten)
    assert ok.all()
    return paare[:, 0], paare[:, 1], knoten, np.stack([lon, lat], axis=1)


def flaeche_wkt(lon: np.ndarray, lat: np.ndarray) -> str | None:
    """WKT für einen Weg: Polygon, wenn geschlossen und ≥ 4 Punkte, sonst Linie bzw. Punkt."""
    if lon.size == 0:
        return None
    pts = ", ".join(f"{x:.7f} {y:.7f}" for x, y in zip(lon, lat))
    if lon.size >= 4 and lon[0] == lon[-1] and lat[0] == lat[-1]:
        return f"POLYGON(({pts}))"
    if lon.size >= 2:
        return f"LINESTRING({pts})"
    return f"POINT({lon[0]:.7f} {lat[0]:.7f})"


def objekte_sammeln(erg: osm_pbf.Ergebnis) -> tuple[list[tuple], list[tuple]]:
    """(pois, bildung) als Zeilen (osm_id, art, unterart, wkt) bzw. (osm_id, art, wkt) in EPSG:4326."""
    pois: list[tuple] = []
    bildung: list[tuple] = []
    wege_nach_id = {wid: refs for wid, _t, refs in erg.wege}

    def ablegen(osm_id: str, t: dict, wkt: str | None) -> None:
        if not wkt:
            return
        p = poi_art(t)
        if p:
            pois.append((osm_id, p[0], p[1], wkt))
        b = bildung_art(t)
        if b:
            bildung.append((osm_id, b, wkt))

    for nid, lon, lat, t in erg.getaggte_knoten:
        ablegen(f"n{nid}", t, f"POINT({lon:.7f} {lat:.7f})")
    for wid, t, refs in erg.wege:
        if poi_art(t) is None and bildung_art(t) is None:
            continue
        lon, lat, ok = erg.koordinaten(refs)
        if not ok.any():
            continue
        if ok.all():
            ablegen(f"w{wid}", t, flaeche_wkt(lon, lat))
        else:   # am Rand abgeschnitten: Punktwolke der vorhandenen Knoten
            ablegen(f"w{wid}", t, "MULTIPOINT(" + ", ".join(
                f"({x:.7f} {y:.7f})" for x, y in zip(lon[ok], lat[ok])) + ")")
    for rid, t, mitglieder in erg.relationen:
        if not ist_flaeche_relation(t):
            continue
        punkte = []
        for typ, ref, rolle in mitglieder:
            if typ == "w" and rolle in ("outer", "") and ref in wege_nach_id:
                lon, lat, ok = erg.koordinaten(wege_nach_id[ref])
                punkte.extend(zip(lon[ok], lat[ok]))
        punkte = list(dict.fromkeys(punkte))   # Ringe schließen mit dem Anfangsknoten: doppelt nur einmal
        if punkte:
            ablegen(f"r{rid}", t, "MULTIPOINT(" + ", ".join(f"({x:.7f} {y:.7f})" for x, y in punkte) + ")")
    return pois, bildung


def lies_osm(pfad: Path, rechteck: tuple[float, float, float, float] | None) -> osm_pbf.Ergebnis:
    """Zwei Durchgänge: erst alles Nötige, dann (falls nötig) die Mitgliedswege der Flächenrelationen."""
    def weg_wahl(t: dict) -> bool:
        return ist_fussweg(t) or poi_art(t) is not None or bildung_art(t) is not None

    def knoten_wahl(t: dict) -> bool:
        return poi_art(t) is not None or bildung_art(t) is not None

    erg = osm_pbf.lies(pfad, rechteck=rechteck, knoten_wahl=knoten_wahl, weg_wahl=weg_wahl,
                       relation_wahl=ist_flaeche_relation)
    vorhanden = {wid for wid, _t, _r in erg.wege}
    fehlend = {ref for _rid, _t, m in erg.relationen for typ, ref, _ro in m if typ == "w"} - vorhanden
    if fehlend:
        zweit = osm_pbf.lies(pfad, rechteck=None, knoten_wahl=lambda t: False,
                             weg_wahl=lambda t: False, relation_wahl=lambda t: False,
                             knoten_lesen=False, weg_ids=fehlend)
        # Diese Wege gehören nicht ins Netz: mit Kennzeichen anhängen, netz_bauen filtert per ist_fussweg
        erg.wege.extend((wid, {"_nur_relation": "1"}, refs) for wid, _t, refs in zweit.wege)
    return erg


# ------------------------------------------------------------------------------- Herkunft

class HerkunftFehler(SystemExit):
    """Prüfsumme der PBF passt nicht zur Herkunft: Lauf abbrechen, nichts schreiben."""


def pruefsumme(pfad: Path, verfahren: str = "sha256") -> str:
    h = hashlib.new(verfahren)
    with open(pfad, "rb") as f:
        for stueck in iter(lambda: f.read(1 << 20), b""):
            h.update(stueck)
    return h.hexdigest()


def sha256(pfad: Path) -> str:
    return pruefsumme(pfad, "sha256")


def md5_pruefen(pfad: Path) -> str:
    """Vergleicht mit der Prüfsummendatei des Anbieters (<datei>.md5, Format „hash  name“), falls vorhanden.

    Gibt den Befund als Satz für den Bericht zurück; bei Abweichung Abbruch (HerkunftFehler).
    """
    md5_datei = pfad.with_name(pfad.name + ".md5")
    if not md5_datei.is_file():
        return "keine Prüfsummendatei des Anbieters (<datei>.md5) neben der PBF"
    erwartet = (md5_datei.read_text(encoding="utf-8", errors="replace").split() or [""])[0].lower()
    if not re.fullmatch(r"[0-9a-f]{32}", erwartet):
        raise HerkunftFehler(f"{md5_datei.name}: keine MD5-Prüfsumme lesbar")
    ist = pruefsumme(pfad, "md5")
    if ist != erwartet:
        raise HerkunftFehler(f"MD5 der PBF {ist} weicht von {md5_datei.name} ({erwartet}) ab: Datei beschädigt "
                             "oder zu einer anderen Lieferung gehörig. Abbruch, nichts geschrieben.")
    return f"MD5 gleich der Prüfsummendatei des Anbieters ({md5_datei.name}, {ist})"


def daten_wurzel(pbf_im_eingang: Path) -> Path:
    """$KIEZ_DATEN, sonst der Ordner über eingang/ (die PBF liegt in $KIEZ_DATEN/eingang/)."""
    umgebung = os.environ.get("KIEZ_DATEN")
    return Path(umgebung).resolve() if umgebung else pbf_im_eingang.parent.parent


def aus_eingang_uebernehmen(pbf: Path, daten: Path, stand: str | None = None) -> Path:
    """Kopiert die PBF (und <datei>.md5, falls vorhanden) aus eingang/ nach <daten>/osm/<stand>/.

    <stand> kommt aus dem Dateikopf (osmosis_replication_timestamp, UTC-Datum); nur wenn er fehlt, aus `stand`.
    Der Eingang bleibt unverändert. Liegt am Ziel schon eine Datei gleichen Namens, muss ihre SHA256 gleich sein
    (dann wird nichts kopiert), sonst Abbruch. Gibt den Pfad der Kopie zurück.
    """
    kopf = osm_pbf.kopf_lesen(pbf)
    if kopf and kopf.zeitstempel:
        stand_kopf = dt.datetime.fromtimestamp(kopf.zeitstempel, dt.UTC).date().isoformat()
        if stand and stand != stand_kopf:
            raise SystemExit(f"--stand {stand} widerspricht dem Dateikopf ({stand_kopf}); Abbruch, nichts kopiert.")
        stand = stand_kopf
    elif not stand:
        raise SystemExit(f"{pbf.name}: kein Datenstand im Dateikopf. Bitte --stand JJJJ-MM-TT angeben "
                         "(Datenstand laut Anbieterseite); nichts kopiert.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stand):
        raise SystemExit(f"--stand {stand}: erwartet JJJJ-MM-TT")
    ordner = daten / "osm" / stand
    ziel = ordner / pbf.name
    if ziel.exists():
        if sha256(ziel) != sha256(pbf):
            raise SystemExit(f"{ziel} gibt es schon mit anderem Inhalt; Abbruch, nichts kopiert.")
        print(f"schon übernommen: {ziel} (SHA256 gleich)", file=sys.stderr)
        return ziel
    ordner.mkdir(parents=True, exist_ok=True)
    for quelle in (pbf, pbf.with_name(pbf.name + ".md5")):
        if not quelle.is_file():
            continue
        zwischen = ordner / (quelle.name + ".teil")
        shutil.copy2(quelle, zwischen)
        zwischen.replace(ordner / quelle.name)
    if sha256(ziel) != sha256(pbf):
        raise SystemExit(f"Kopie {ziel} weicht vom Eingang ab; bitte prüfen.")
    print(f"übernommen: {pbf} → {ziel}", file=sys.stderr)
    return ziel


def herkunft_pruefen(pfad: Path, kopf: osm_pbf.Kopf | None, summe: str, *, schreiben: bool = True,
                     eintragen: bool = False) -> str:
    """Prüft die SHA256 der PBF gegen HERKUNFT.md neben der Datei; legt HERKUNFT.md an, wenn sie fehlt.

    - HERKUNFT.md fehlt: anlegen (nur mit schreiben=True), Felder zum Ergänzen markiert.
    - Die Prüfsumme steht darin: in Ordnung.
    - Eine andere SHA256 steht in der Zeile oder dem Abschnitt dieser Datei: Abbruch (HerkunftFehler).
    - Keine SHA256 zu dieser Datei: mit eintragen=True nachtragen, sonst Abbruch mit Anleitung.
    Im Trockenlauf (schreiben=False) wird nur geprüft, nie geschrieben.
    """
    hk = pfad.parent / "HERKUNFT.md"
    if hk.exists():
        text = hk.read_text(encoding="utf-8")
        if summe in text:
            return f"SHA256 steht in {hk.name}"
        andere = abschnitt_summen(text, pfad.name)
        if andere:
            raise HerkunftFehler(
                f"{hk}: für {pfad.name} ist SHA256 {', '.join(andere)} eingetragen, die Datei hat {summe}. "
                "Abbruch: Die PBF ist nicht die beschriebene Lieferung (neue Lieferung in eigenen Ordner "
                "$KIEZ_DATEN/osm/<stand>/ legen).")
        if not schreiben:
            return f"SHA256 fehlt in {hk.name} (Trockenlauf, nicht eingetragen)"
        if not eintragen:
            raise HerkunftFehler(f"{hk}: keine SHA256 für {pfad.name}. Prüfen, ob die Datei die beschriebene "
                                 "Lieferung ist, dann mit --hash-eintragen erneut starten.")
        with hk.open("a", encoding="utf-8") as f:
            f.write(f"\n## {pfad.name}\n- SHA256: {summe}\n- Größe: {pfad.stat().st_size} Byte\n"
                    f"- eingetragen von skripte/12_osm.py (--hash-eintragen) am {dt.date.today().isoformat()}\n")
        print(f"SHA256 in {hk} nachgetragen", file=sys.stderr)
        return f"SHA256 in {hk.name} nachgetragen"
    if not schreiben:
        return "HERKUNFT.md fehlt (Trockenlauf, nicht angelegt)"
    zeit = (dt.datetime.fromtimestamp(kopf.zeitstempel, dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
            if kopf and kopf.zeitstempel else "nicht im Dateikopf")
    hk.write_text(
        f"# Herkunft: {pfad.name}\n\n"
        "- Quelle: OpenStreetMap, Handdownload durch Andre im Browser. Bezugsadresse: **bitte eintragen** "
        "(Geofabrik-Auszug „malopolskie“)\n"
        "- Abrufdatum: **bitte eintragen**\n"
        "- Lizenz: Open Database License 1.0 (ODbL, https://opendatacommons.org/licenses/odbl/1-0/), "
        "© OpenStreetMap-Mitwirkende\n"
        "- robots/Bedingungen: kein Agentenabruf (skripte/abruf.py sperrt download.geofabrik.de und "
        "download.bbbike.org); Handdownload im Browser\n"
        f"- Größe: {pfad.stat().st_size} Byte\n"
        f"- SHA256: {summe}\n"
        f"- Dateikopf: Programm {kopf.programm if kopf else '?'}, Datenstand (Replikation) {zeit}, "
        f"Rechteck {[round(v, 7) for v in (kopf.links, kopf.unten, kopf.rechts, kopf.oben)] if kopf and kopf.links is not None else '?'}\n"
        f"- angelegt von skripte/12_osm.py am {dt.date.today().isoformat()}\n",
        encoding="utf-8")
    print(f"HERKUNFT.md angelegt: {hk} (Bezugsadresse und Abrufdatum ergänzen)", file=sys.stderr)
    return f"{hk.name} mit SHA256 angelegt"


def abschnitt_summen(text: str, name: str) -> list[str]:
    """SHA256-Werte, die in HERKUNFT.md zu dieser Datei gehören (gleiche Zeile oder Abschnitt mit dem Namen)."""
    summen: list[str] = []
    im_abschnitt = False
    for zeile in text.splitlines():
        if zeile.startswith("#"):
            im_abschnitt = name in zeile
        if im_abschnitt or name in zeile:
            summen += re.findall(r"\b[0-9a-f]{64}\b", zeile.lower())
    return sorted(set(summen))


# ------------------------------------------------------------------------------- Datenbank

def verbinden():
    import psycopg
    if os.environ.get("PGUSER") != "kiezatlas_rechnen":
        raise SystemExit("PGUSER muss kiezatlas_rechnen sein (skripte/12_osm.sh setzt das)")
    return psycopg.connect("")


PUFFER_SQL = f"""
CREATE TEMP TABLE a3_puffer ON COMMIT DROP AS
  SELECT ST_Subdivide(ST_Buffer(ST_Transform(ST_Union(geom), {RECHEN_SRID}), {PUFFER_M}), 128) AS geom FROM public.stadtteil;
CREATE INDEX ON a3_puffer USING gist (geom);
CREATE TEMP TABLE a3_stadt ON COMMIT DROP AS
  SELECT ST_Subdivide(ST_Transform(geom, {RECHEN_SRID}), 128) AS geom FROM public.stadtteil;
CREATE INDEX ON a3_stadt USING gist (geom);
"""


def leserechteck(cur) -> tuple[float, float, float, float]:
    cur.execute("SELECT ST_XMin(e), ST_YMin(e), ST_XMax(e), ST_YMax(e) FROM ("
                "SELECT ST_Extent(ST_Transform(geom, 4326)) e FROM a3_puffer) x")
    w, s, o, n = cur.fetchone()
    return w - RAND_GRAD, s - RAND_GRAD, o + RAND_GRAD, n + RAND_GRAD


def schreiben(cur, kanten_von, kanten_nach, knoten, koords, pois, bildung) -> dict:
    cur.execute("CREATE TEMP TABLE a3_k (id bigint, lon float8, lat float8) ON COMMIT DROP")
    with cur.copy("COPY a3_k (id, lon, lat) FROM STDIN") as cp:
        for i, (x, y) in zip(knoten.tolist(), koords.tolist()):
            cp.write_row((i, x, y))
    cur.execute("CREATE TEMP TABLE a3_e (von bigint, nach bigint) ON COMMIT DROP")
    with cur.copy("COPY a3_e (von, nach) FROM STDIN") as cp:
        for a, b in zip(kanten_von.tolist(), kanten_nach.tolist()):
            cp.write_row((a, b))
    cur.execute("CREATE TEMP TABLE a3_p (osm_id text, art text, unterart text, wkt text) ON COMMIT DROP")
    with cur.copy("COPY a3_p (osm_id, art, unterart, wkt) FROM STDIN") as cp:
        for r in pois:
            cp.write_row(r)
    cur.execute("CREATE TEMP TABLE a3_b (osm_id text, art text, wkt text) ON COMMIT DROP")
    with cur.copy("COPY a3_b (osm_id, art, wkt) FROM STDIN") as cp:
        for r in bildung:
            cp.write_row(r)
    cur.execute(f"""
        ALTER TABLE a3_k ADD COLUMN geom geometry(Point, {RECHEN_SRID});
        UPDATE a3_k SET geom = ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), {RECHEN_SRID});
        CREATE UNIQUE INDEX ON a3_k (id);
        CREATE TEMP TABLE a3_kante ON COMMIT DROP AS
          SELECT e.von, e.nach, ST_MakeLine(a.geom, b.geom)::geometry(LineString, {RECHEN_SRID}) AS geom
          FROM a3_e e JOIN a3_k a ON a.id = e.von JOIN a3_k b ON b.id = e.nach;
        CREATE INDEX ON a3_kante USING gist (geom);
        DELETE FROM a3_kante k WHERE NOT EXISTS (SELECT 1 FROM a3_puffer p WHERE ST_Intersects(p.geom, k.geom));
    """)
    cur.execute("TRUNCATE auswertung.netz_kante, auswertung.netz_knoten, auswertung.osm_poi")
    cur.execute("""
        INSERT INTO auswertung.netz_knoten (id, geom)
          SELECT k.id, k.geom FROM a3_k k
          WHERE k.id IN (SELECT von FROM a3_kante UNION SELECT nach FROM a3_kante);
        INSERT INTO auswertung.netz_kante (id, von, nach, laenge_m, geom)
          SELECT row_number() OVER (ORDER BY von, nach), von, nach, round(ST_Length(geom)::numeric, 2), geom
          FROM a3_kante;
    """)
    # Einrichtungen: Fläche -> Punkt auf der Fläche; Punktwolke (Relation, Randstück) -> Schwerpunkt
    cur.execute(f"""
        CREATE TEMP TABLE a3_poi ON COMMIT DROP AS
          SELECT osm_id, art, unterart,
                 ST_Transform(CASE WHEN GeometryType(g) = 'MULTIPOINT' THEN ST_Centroid(g)
                                   ELSE ST_PointOnSurface(ST_MakeValid(g)) END, {RECHEN_SRID}) AS geom
          FROM (SELECT osm_id, art, unterart, ST_SetSRID(ST_GeomFromText(wkt), 4326) g FROM a3_p) x;
        DELETE FROM a3_poi q WHERE NOT EXISTS (SELECT 1 FROM a3_puffer p WHERE ST_Intersects(p.geom, q.geom));
        -- Dublette: dieselbe Einrichtung als Punkt und als Fläche; der Punkt bleibt
        DELETE FROM a3_poi f WHERE left(f.osm_id, 1) IN ('w', 'r') AND EXISTS (
          SELECT 1 FROM a3_poi n WHERE left(n.osm_id, 1) = 'n' AND n.art = f.art
            AND ST_DWithin(n.geom, f.geom, {DUBLETTE_M}));
        INSERT INTO auswertung.osm_poi (osm_id, art, unterart, geom) SELECT osm_id, art, unterart, geom FROM a3_poi;
    """)
    cur.execute(f"""
        CREATE TEMP TABLE a3_bildung ON COMMIT DROP AS
          SELECT osm_id, art, ST_Transform(ST_MakeValid(ST_SetSRID(ST_GeomFromText(wkt), 4326)), {RECHEN_SRID}) AS geom
          FROM a3_b;
    """)
    cur.execute("SELECT art, count(*) FROM auswertung.osm_poi GROUP BY art ORDER BY art")
    je_art = dict(cur.fetchall())
    cur.execute("SELECT (SELECT count(*) FROM auswertung.netz_knoten), (SELECT count(*) FROM auswertung.netz_kante),"
                " (SELECT round(sum(laenge_m) / 1000) FROM auswertung.netz_kante)")
    nk, ne, km = cur.fetchone()
    return {"poi_je_art": je_art, "knoten": nk, "kanten": ne, "netz_km": km}


# Abgleich mit einer amtlichen Liste: je Art (Tabelle, Schlüsselspalte, Bedingung) oder None. Für Kraków ist noch
# keine Liste geladen (Schulregister RSPO nur als Handdownload, Paket Versorgung und Takt); bis dahin steht im
# Bericht „nicht geprüft“. Eingetragen wird hier nur, was als Tabelle in sql/ steht (Vertrag über die Integration).
AMTLICHE_LISTE: dict[str, tuple[str, str, str] | None] = {"kita": None, "schule": None}


def tabelle_da(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (name,))
    return bool(cur.fetchone()[0])


def vollstaendigkeit(cur, liste: dict[str, tuple[str, str, str] | None] | None = None) -> dict:
    """OSM-Kitas und -Schulen gegen eine amtliche Liste im Stadtgebiet (Trefferquote je Richtung).

    Ohne amtliche Liste (Eintrag None oder Tabelle fehlt bzw. leer): nur die Zahl der OSM-Objekte, quote None und
    ein Grund. Nie eine erfundene Vergleichszahl.
    """
    liste = AMTLICHE_LISTE if liste is None else liste
    erg = {}
    for art in ("kita", "schule"):
        cur.execute("SELECT count(*) FROM a3_bildung b WHERE b.art = %s AND EXISTS "
                    "(SELECT 1 FROM a3_stadt s WHERE ST_Intersects(s.geom, b.geom))", (art,))
        o_n = cur.fetchone()[0]
        eintrag = liste.get(art)
        grund = None
        if eintrag is None:
            grund = "keine amtliche Liste geladen (Schulregister RSPO offen)"
        elif not tabelle_da(cur, eintrag[0]):
            grund = f"Tabelle {eintrag[0]} fehlt"
        if grund:
            erg[art] = {"amtlich": None, "amtlich_mit_osm": None, "osm": o_n, "osm_mit_amtlich": None,
                        "quote": None, "grund": grund}
            continue
        tabelle, schluessel, bedingung = eintrag
        cur.execute(f"""
            WITH m AS (
              SELECT t.{schluessel} id, ST_Transform(t.geom, {RECHEN_SRID}) g FROM {tabelle} t
              WHERE ({bedingung})
                AND EXISTS (SELECT 1 FROM a3_stadt s WHERE ST_Intersects(s.geom, ST_Transform(t.geom, {RECHEN_SRID})))),
            o AS (
              SELECT b.osm_id, b.geom g FROM a3_bildung b
              WHERE b.art = %s AND EXISTS (SELECT 1 FROM a3_stadt s WHERE ST_Intersects(s.geom, b.geom)))
            SELECT (SELECT count(*) FROM m),
                   (SELECT count(*) FROM m WHERE EXISTS (SELECT 1 FROM o WHERE ST_DWithin(o.g, m.g, %s))),
                   (SELECT count(*) FROM o WHERE EXISTS (SELECT 1 FROM m WHERE ST_DWithin(o.g, m.g, %s)))
        """, (art, TREFFER_M, TREFFER_M))
        m_n, m_treffer, o_treffer = cur.fetchone()
        erg[art] = {"amtlich": m_n, "amtlich_mit_osm": m_treffer, "osm": o_n, "osm_mit_amtlich": o_treffer,
                    "quote": (round(100 * m_treffer / m_n, 1) if m_n else None),
                    "grund": None if m_n else f"{tabelle} ohne Zeilen im Stadtgebiet"}
    return erg


# ------------------------------------------------------------------------------- Kennzahlen

def kachel_grad(breite: float, km: float = 1.0) -> tuple[float, float]:
    """Kantenlänge einer Kachel von km × km in Grad (Länge, Breite) bei der gegebenen Breite.

    Näherung auf der Kugel mit dem mittleren Erdradius (6371,0088 km, IUGG): 1° Breite = 111,195 km, 1° Länge
    = 111,195 km · cos(Breite). Für die Abdeckungsprüfung genügt das (es geht um leere Kacheln, nicht um Flächen).
    """
    km_je_grad = 6371.0088 * math.pi / 180.0
    return km / (km_je_grad * math.cos(math.radians(breite))), km / km_je_grad


def abdeckung(cur, erg: osm_pbf.Ergebnis, rechteck: tuple[float, float, float, float]) -> dict:
    """Wie gut deckt die Datei den Puffer ab? Rechteckprüfung plus 1-km-Kacheln ohne jeden OSM-Knoten.

    Leere Kacheln gibt es auch auf großen Wasserflächen; viele leere Kacheln an einem Rand deuten auf einen Auszug,
    der dort endet (z. B. ein Woiwodschaftsauszug, der an der Stadtgrenze aufhört).
    """
    w, s, o, n = rechteck
    kachel_lon, kachel_lat = kachel_grad((s + n) / 2)
    ausd = erg.ausdehnung
    rechteck_ok = ausd is not None and (ausd[0] <= w + RAND_GRAD and ausd[1] <= s + RAND_GRAD
                                        and ausd[2] >= o - RAND_GRAD and ausd[3] >= n - RAND_GRAD)
    nx = int(np.ceil((o - w) / kachel_lon))
    ny = int(np.ceil((n - s) / kachel_lat))
    cur.execute(f"""
        SELECT i, j FROM generate_series(0, %(nx)s - 1) i, generate_series(0, %(ny)s - 1) j
        WHERE EXISTS (SELECT 1 FROM a3_puffer p WHERE ST_Intersects(p.geom, ST_Transform(ST_MakeEnvelope(
            %(w)s + i * %(dx)s, %(s)s + j * %(dy)s, %(w)s + (i + 1) * %(dx)s, %(s)s + (j + 1) * %(dy)s, 4326), {RECHEN_SRID})))
    """, {"nx": nx, "ny": ny, "w": w, "s": s, "dx": kachel_lon, "dy": kachel_lat})
    im_puffer = {(i, j) for i, j in cur.fetchall()}
    if erg.knoten_id.size:
        ki = np.floor((erg.knoten_lon - w) / kachel_lon).astype(np.int64)
        kj = np.floor((erg.knoten_lat - s) / kachel_lat).astype(np.int64)
        belegt = set(zip(ki.tolist(), kj.tolist()))
    else:
        belegt = set()
    leer = sorted(im_puffer - belegt)
    return {"rechteck_ok": rechteck_ok, "kacheln": len(im_puffer), "leer": len(leer),
            "kachel_grad": (round(kachel_lon, 5), round(kachel_lat, 5)),
            "leer_beispiele": [(round(w + (i + 0.5) * kachel_lon, 3), round(s + (j + 0.5) * kachel_lat, 3))
                               for i, j in leer[:8]]}


# Zellen für den Abstand Zellmittelpunkt → Netz. Gleiche Tabelle wie in skripte/14b_fussweg.py; welche Zellen
# Kraków bekommt (Gitter oder rejony statystyczne), legt das Paket Gliederung und Bevölkerung fest.
ZELLEN_TABELLE = "public.zensus_zelle"


def komponenten(knoten_ids: np.ndarray, von: np.ndarray, nach: np.ndarray, auswahl: np.ndarray) -> dict:
    """Zusammenhang des Netzes, rein (ohne Datenbank).

    knoten_ids sortiert; auswahl = Indizes der Knoten, die zählen (im Stadtgebiet). Anteil = Knoten der größten
    Komponente (größte unter den ausgewählten Knoten) / ausgewählte Knoten.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    n = knoten_ids.size
    ia = np.searchsorted(knoten_ids, von)
    ib = np.searchsorted(knoten_ids, nach)
    g = coo_matrix((np.ones(ia.size), (ia, ib)), shape=(n, n))
    anz, label = connected_components(g, directed=False)
    if auswahl.size:
        groesse = np.bincount(label[auswahl])
        groesste = int(groesse.max())
        anteil = groesste / auswahl.size
        zweite = int(np.sort(groesse)[-2]) if groesse.size > 1 else 0
    else:
        groesste, anteil, zweite = 0, 0.0, 0
    return {"komponenten": int(anz), "groesste_komponente_im_stadtgebiet": groesste,
            "zweitgroesste_komponente_im_stadtgebiet": zweite, "anteil_groesste_komponente": round(anteil, 4)}


def kennzahlen(cur) -> dict:
    """Netzkennzahlen für die Abnahme (auch von pruefen/a3_pruefen.py genutzt). Braucht a3_stadt.

    Der Anteil der größten Komponente hängt nur am Netz und an den Stadtteilen; der Abstand der Zellmittelpunkte
    zum Netz nur, wenn die Zelltabelle da ist (sonst zellen_grund).
    """
    from scipy.spatial import cKDTree

    cur.execute("SELECT id, ST_X(geom), ST_Y(geom) FROM auswertung.netz_knoten ORDER BY id")
    zeilen = cur.fetchall()
    if not zeilen:
        return {"knoten": 0}
    ids = np.array([z[0] for z in zeilen], dtype=np.int64)
    xy = np.array([(z[1], z[2]) for z in zeilen])
    cur.execute("SELECT von, nach FROM auswertung.netz_kante")
    e = np.array(cur.fetchall(), dtype=np.int64).reshape(-1, 2)
    cur.execute("""SELECT k.id FROM auswertung.netz_knoten k
                   WHERE EXISTS (SELECT 1 FROM a3_stadt s WHERE ST_Intersects(s.geom, k.geom))""")
    in_stadt = np.searchsorted(ids, np.array([r[0] for r in cur.fetchall()], dtype=np.int64))
    kz = {"knoten": int(ids.size), "kanten": int(e.shape[0]), "knoten_im_stadtgebiet": int(in_stadt.size),
          **komponenten(ids, e[:, 0], e[:, 1], in_stadt)}
    if not tabelle_da(cur, ZELLEN_TABELLE):
        kz["zellen_grund"] = f"{ZELLEN_TABELLE} fehlt (Zellen legt das Paket Gliederung und Bevölkerung an)"
        return kz
    cur.execute(f"""SELECT ST_X(g), ST_Y(g) FROM (
                     SELECT ST_Transform(ST_Centroid(z.geom), {RECHEN_SRID}) g FROM {ZELLEN_TABELLE} z WHERE z.ew > 0) x
                   WHERE EXISTS (SELECT 1 FROM a3_stadt s WHERE ST_Intersects(s.geom, x.g))""")
    zellen = np.array(cur.fetchall()).reshape(-1, 2)
    if not zellen.size:
        kz["zellen_grund"] = f"{ZELLEN_TABELLE} ohne bewohnte Zelle im Stadtgebiet"
        return kz
    d, _ = cKDTree(xy).query(zellen)
    kz.update({
        "bewohnte_zellen": int(zellen.shape[0]), "zellen_le_150m": int((d <= 150).sum()),
        "anteil_zellen_le_150m": round(float((d <= 150).mean()), 4),
        "zelle_knoten_median_m": round(float(np.median(d)), 1),
        "zelle_knoten_max_m": round(float(d.max()), 1),
    })
    return kz


def pz(anteil: float) -> str:
    return f"{100 * anteil:.1f} %".replace(".", ",")


def bericht_schreiben(pfad: Path, *, pbf: Path, summe: str, herkunft: str, md5: str, erg: osm_pbf.Ergebnis,
                      stand: str, geschrieben: dict, voll: dict, kz: dict, trocken: bool) -> None:
    def zeile(art: str) -> str:
        v = voll[art]
        if v["quote"] is None:
            return f"| {art} | – | – | nicht geprüft: {v['grund']} | {v['osm']} | – |"
        q = f"{v['quote']:.1f} %".replace(".", ",")
        return (f"| {art} | {v['amtlich']} | {v['amtlich_mit_osm']} | **{q}** | {v['osm']} | "
                f"{v['osm_mit_amtlich']} |")

    ab = kz["abdeckung"]
    deckt = (f"Ausdehnung der Datei umfasst das Leserechteck: {'ja' if ab['rechteck_ok'] else '**nein**'} "
             f"(nur Rechteckprüfung). 1-km-Kacheln im Puffer ohne einen einzigen OSM-Knoten: {ab['leer']} von "
             f"{ab['kacheln']} (Kachel {ab['kachel_grad'][0]}° × {ab['kachel_grad'][1]}°, aus der Breite berechnet; "
             "große Wasserflächen sind leer; viele leere Kacheln an einem Rand heißen: Auszug endet dort)"
             + (f", Mitten z. B. {ab['leer_beispiele']}" if ab["leer"] else "") + ".")
    if "zellen_grund" in kz:
        zellen = f"- Abstand Zellmittelpunkt → Netz: nicht gerechnet, {kz['zellen_grund']}"
    else:
        zellen = (f"- Bewohnte Zellen im Stadtgebiet {kz.get('bewohnte_zellen', 0)}, davon mit Netzknoten in ≤ 150 m "
                  f"{kz.get('zellen_le_150m', 0)} ({pz(kz.get('anteil_zellen_le_150m', 0))}); "
                  f"Abstand Median {kz.get('zelle_knoten_median_m', 0)} m, größter {kz.get('zelle_knoten_max_m', 0)} m")

    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text("\n".join([
        "# OSM-Einrichtungen und Fußwegnetz" + (" (TROCKENLAUF, nichts gespeichert)" if trocken else ""),
        "",
        f"Erzeugt von `skripte/12_osm.py` am {dt.date.today().isoformat()}. Daten: {ODBL}. "
        f"Abstände in {srs_name()}.",
        "",
        "## Herkunft der Rohdaten",
        "",
        f"- PBF: `{pbf.name}`, {pbf.stat().st_size} Byte, Datenstand {stand}",
        f"- SHA256: `{summe}`",
        f"- Herkunft: {herkunft}",
        f"- Prüfsumme des Anbieters: {md5}",
        f"- Gelesen: {erg.knoten_gesamt} Knoten, {erg.wege_gesamt} Wege, {erg.relationen_gesamt} Relationen",
        f"- Abdeckung des Puffers (Stadtgebiet + {PUFFER_M // 1000} km): {deckt}",
        "",
        "## Fußwegnetz (auswertung.netz_knoten, auswertung.netz_kante)",
        "",
        f"- Knoten {kz.get('knoten', 0)}, Kanten {kz.get('kanten', 0)}, Netzlänge rund {geschrieben['netz_km']} km",
        (f"- Zusammenhang: Knoten im Stadtgebiet {kz.get('knoten_im_stadtgebiet', 0)}, davon in der größten "
         f"Komponente {kz.get('groesste_komponente_im_stadtgebiet', 0)}; **Anteil der größten Komponente "
         f"{pz(kz.get('anteil_groesste_komponente', 0))}**; zweitgrößte Komponente "
         f"{kz.get('zweitgroesste_komponente_im_stadtgebiet', 0)} Knoten; Komponenten insgesamt "
         f"{kz.get('komponenten', 0)}"),
        zellen,
        "",
        ("Regeln: begehbar sind `highway`-Wege außer Autobahn, Bau, geplant, Bahnsteig, Rennstrecke; Radwege nur mit "
         "`foot=yes/designated`; `foot=no`, `access=private/no` ohne Fußfreigabe und Kraftfahrstraßen entfallen. "
         "Jeder OSM-Knoten eines solchen Wegs ist Netzknoten; Kanten sind ungerichtet. Die Fußwegrechnung nutzt nur "
         "die größte Komponente (skripte/14b_fussweg.py)."),
        "",
        "## Einrichtungen aus OSM (auswertung.osm_poi, ohne Namen)",
        "",
        "| Art | Anzahl |", "|---|---|",
        *[f"| {a} | {n} |" for a, n in sorted(geschrieben["poi_je_art"].items())],
        "",
        f"## Kitas und Schulen gegen eine amtliche Liste (Treffer: OSM-Objekt höchstens {TREFFER_M} m entfernt)",
        "",
        "| Art | amtliche Standorte | davon mit OSM-Gegenstück | Trefferquote | OSM-Objekte im Stadtgebiet | davon mit amtlichem Gegenstück |",
        "|---|---|---|---|---|---|",
        zeile("kita"), zeile("schule"),
        "",
        ("OSM-Kitas: `amenity=kindergarten`, Schulen: `amenity=school` (Punkte und Flächen). Die Trefferquote misst, "
         "wie vollständig OSM gegenüber der amtlichen Liste ist; sie ist ein Hinweis auf die Güte der OSM-Kategorien "
         "ohne amtliche Liste (Ärzte, Apotheken, Märkte, Pflege, Spielplätze), kein Beleg dafür."),
        "",
    ]), encoding="utf-8")


# ------------------------------------------------------------------------------- Hauptlauf

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pbf", required=True, type=Path)
    ap.add_argument("--trockenlauf", action="store_true", help="alles rechnen, am Ende ROLLBACK")
    ap.add_argument("--hash-eintragen", action="store_true",
                    help="fehlende SHA256 in eine vorhandene HERKUNFT.md nachtragen (nach Sichtprüfung)")
    ap.add_argument("--bericht", type=Path, default=WURZEL / "berichte" / "osm_netz.md")
    ap.add_argument("--uebernehmen", action="store_true",
                    help="PBF aus dem gemeinsamen Eingang nach $KIEZ_DATEN/osm/<stand>/ kopieren und dort rechnen")
    ap.add_argument("--stand", help="Datenstand JJJJ-MM-TT für --uebernehmen, nur wenn der Dateikopf keinen nennt")
    a = ap.parse_args()
    pbf = a.pbf.resolve()
    if not pbf.is_file():
        raise SystemExit(f"PBF fehlt: {pbf} (Handdownload nach $KIEZ_DATEN/eingang/ oder $KIEZ_DATEN/osm/<stand>/)")
    if pbf.parent.name == "eingang" and a.uebernehmen:
        pbf = aus_eingang_uebernehmen(pbf, daten_wurzel(pbf), a.stand)
    elif pbf.parent.name == "eingang" and not a.trockenlauf:
        # Rohdaten nur unter $KIEZ_DATEN/<quelle>/<stand>/ mit eigener HERKUNFT.md; im gemeinsamen Eingang
        # würde HERKUNFT.md einer anderen Lieferung getroffen.
        raise SystemExit(f"{pbf.name} liegt im Eingang. Mit --uebernehmen kopiert das Skript sie nach "
                         "$KIEZ_DATEN/osm/<stand>/ (stand = Datenstand im Dateikopf) und rechnet dort.")
    t0 = time.time()
    summe = sha256(pbf)
    md5 = md5_pruefen(pbf)
    kopf = osm_pbf.kopf_lesen(pbf)
    # Herkunft vor jedem Schreiben in die Datenbank: eine fremde Datei bricht hier ab
    herkunft = herkunft_pruefen(pbf, kopf, summe, schreiben=not a.trockenlauf, eintragen=a.hash_eintragen)
    print(f"SHA256 {summe}; {herkunft}; {md5}", flush=True)
    with verbinden() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.stadtteil")
            if cur.fetchone()[0] == 0:
                raise SystemExit("public.stadtteil ist leer: erst die Stadtteilgrenzen laden (Grenzen der dzielnice "
                                 "aus OSM, Paket Gliederung und Bevölkerung); ohne sie gibt es keinen Puffer")
            cur.execute(PUFFER_SQL)
            rechteck = leserechteck(cur)
            print(f"Leserechteck {tuple(round(v, 4) for v in rechteck)}", flush=True)
            erg = lies_osm(pbf, rechteck)
            print(f"PBF gelesen in {time.time() - t0:.0f} s: {erg.knoten_gesamt} Knoten, {erg.wege_gesamt} Wege, "
                  f"{erg.relationen_gesamt} Relationen; im Rechteck {erg.knoten_id.size} Knoten", flush=True)
            fusswege = [w for w in erg.wege if "_nur_relation" not in w[1] and ist_fussweg(w[1])]
            von, nach, knoten, koords = netz_bauen(fusswege, erg)
            pois, bildung = objekte_sammeln(erg)
            geschrieben = schreiben(cur, von, nach, knoten, koords, pois, bildung)
            voll = vollstaendigkeit(cur)
            kz = kennzahlen(cur)
            kz["abdeckung"] = abdeckung(cur, erg, rechteck)
            stand = (dt.datetime.fromtimestamp(erg.kopf.zeitstempel, dt.UTC).date().isoformat()
                     if erg.kopf and erg.kopf.zeitstempel
                     else dt.date.fromtimestamp(pbf.stat().st_mtime).isoformat() + " (Dateidatum)")
            bericht_schreiben(a.bericht, pbf=pbf, summe=summe, herkunft=herkunft, md5=md5, erg=erg, stand=stand,
                              geschrieben=geschrieben, voll=voll, kz=kz, trocken=a.trockenlauf)
            print(f"Einrichtungen {geschrieben['poi_je_art']}; Netz {geschrieben['knoten']} Knoten, "
                  f"{geschrieben['kanten']} Kanten; größte Komponente {pz(kz.get('anteil_groesste_komponente', 0))} "
                  f"der Knoten im Stadtgebiet; Abgleich Kita {voll['kita']['quote']}, Schule {voll['schule']['quote']}; "
                  f"leere 1-km-Kacheln im Puffer {kz['abdeckung']['leer']} von {kz['abdeckung']['kacheln']}; "
                  f"Bericht {a.bericht}")
        if a.trockenlauf:
            conn.rollback()
            print("Trockenlauf: ROLLBACK, in auswertung ist nichts geändert.")
        else:
            conn.commit()
    print(f"fertig in {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
