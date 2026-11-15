"""Downloads des Kiezatlas Kraków: GeoPackage, CSV, QGIS-Projekt und Liesmich je Sprache aus den Datendateien.

Kein Netz, keine Datenbank. Liest nur die veröffentlichten Dateien unter daten/ (dieselben, die die Seiten laden),
formt sie um (Koordinaten ins Rechensystem, verschachtelte Felder zu Spalten) und rechnet keinen Wert neu. Dateien
mit fixture: true (Beispieldaten) bleiben draußen und stehen mit Grund im Liesmich.

Ausgabe (Standard daten/pobierz/; daten/export/ bleibt der Potsdamer Exportprüfung vorbehalten):
  kiezatlas_krakow.gpkg        ohne Anteil aus OpenStreetMap und ohne Zuordnung über die OSM-Grenzen
  kiezatlas_krakow_odbl.gpkg   alles aus den *_odbl-Dateien, Open Database License 1.0
  csv/, csv_odbl/              je Ebene eine CSV: UTF-8 mit BOM, Semikolon, Punkt als Dezimalzeichen
  csv_pl/, csv_odbl_pl/        dieselben CSV mit Dezimalkomma ohne Tausendertrenner (polnisches Excel, LibreOffice)
  kiezatlas_krakow.qgz         QGIS-Projekt mit relativen Pfaden auf beide GeoPackages, Stile nach DESIGN.md
  licencje.csv                 Lizenz und wörtlicher Vermerk je Datei und Ebene (auch als Tabelle in jedem GeoPackage)
  pola.csv, wartosci.csv       Bedeutung jedes Felds und jedes Kategorienwerts auf pl, en, de (auch als Tabellen pola
                               und wartosci in jedem GeoPackage); Texte in skripte/export_pola_krakow.py
  kiezatlas_krakow_csv.zip     alle CSV, licencje.csv und die Liesmich in einem Archiv
  CZYTAJ.md, README.md, LIESMICH.md   Liesmich auf Polnisch, Englisch, Deutsch
Regeln vorab: pruefen/S4_protokoll.md. Prüfung: pruefen/S4_export.py.

Aufruf (Python aus requirements.txt: pyyaml, pyproj, shapely):
  python -I skripte/16_export_krakow.py [--ziel daten/pobierz]
  python -I skripte/16_export_krakow.py --pruefen   erzeugt in einen Wegwerf-Ordner und vergleicht byte-genau mit
                                                    daten/pobierz/; Rückgabe 1 bei Abweichung
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sqlite3
import struct
import sys
import tempfile
import zipfile
from html import escape
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))   # python -I lässt das Skriptverzeichnis weg
import ort_konfig  # noqa: E402
import export_pola_krakow as pola  # noqa: E402

DATEN = WURZEL / "daten"
ZIEL_STANDARD = DATEN / "pobierz"
SRID = ort_konfig.RECHEN_SRID
GPKG_FREI = "kiezatlas_krakow.gpkg"
GPKG_ODBL = "kiezatlas_krakow_odbl.gpkg"
QGZ = "kiezatlas_krakow.qgz"
CSV_ZIP = "kiezatlas_krakow_csv.zip"
ODBL_URL = "https://opendatacommons.org/licenses/odbl/1-0/"
STAND_ZEIT = "T00:00:00.000Z"
INK, MUTED, GRUND, AKZENT = "#13212a", "#4f5d64", "#f1f2ee", "#6a2c82"
STUFEN = ["#dce6e2", "#a8c7c2", "#6fa1a3", "#3b7684", "#1c4a5b"]   # DESIGN.md, Klassenfarben im Gitter


# ------------------------------------------------------------------------------------------------- lesen
def js_lesen(name: str) -> tuple[str, dict]:
    text = (DATEN / f"{name}.js").read_text(encoding="utf-8")
    m = re.search(r"window\.([A-Za-z0-9_]+)\s*=\s*", text)
    if not m:
        raise SystemExit(f"daten/{name}.js: keine Zuweisung window.NAME=")
    kopf = re.sub(r"^\s*/\*\s*|\s*\*/\s*$", "", text[: m.start()].strip())
    return kopf, json.loads(text[m.end():].rstrip().rstrip(";"))


# Themen mit echten Atlas-Dateien, aber noch ohne Ebene im Export; das Liesmich nennt sie (pruefen/S4_export.py
# prüft, dass keine Ebene aus ihnen gelesen wird). Eine neue Ebene aus einer dieser Dateien: hier streichen.
OHNE_EBENE = {
    "powietrze": {"pl": "jakość powietrza", "en": "air quality", "de": "Luft"},
    "mieszkania_odbl": {"pl": "rynek mieszkaniowy", "en": "housing market", "de": "Wohnungsmarkt"},
}


class Daten:
    def __init__(self) -> None:
        self.kopf: dict[str, str] = {}
        self.d: dict[str, dict] = {}
        self.beispiel: list[str] = []
        self.benutzt: set[str] = set()      # über D[name] gelesene Dateien (Quellen einer Ebene)
        for p in sorted(DATEN.glob("*.js")):
            k, v = js_lesen(p.stem)
            self.kopf[p.stem], self.d[p.stem] = k, v
            if isinstance(v, dict) and v.get("fixture") is True:
                self.beispiel.append(p.stem)

    def __getitem__(self, name: str) -> dict:
        if name in self.beispiel:
            raise SystemExit(f"daten/{name}.js ist Beispieldatei (fixture: true) und darf nicht exportiert werden")
        if name in OHNE_EBENE:
            raise SystemExit(f"daten/{name}.js steht in OHNE_EBENE; mit eigener Ebene dort und im Liesmich streichen")
        self.benutzt.add(name)
        return self.d[name]


# ------------------------------------------------------------------------------------------------- Werte
def flach(o, vor: str = "") -> list[tuple[str, object]]:
    """Verschachtelte Objekte zu Spalten (Namen mit _ verbunden), Listen als JSON-Text."""
    aus: list[tuple[str, object]] = []
    for k, v in o.items():
        n = f"{vor}_{k}" if vor else str(k)
        if isinstance(v, dict):
            aus += flach(v, n)
        elif isinstance(v, list):
            aus.append((n, json.dumps(v, ensure_ascii=False, sort_keys=True)))
        else:
            aus.append((n, v))
    return aus


def typ(werte: list) -> str:
    w = [v for v in werte if v is not None]
    if w and all(isinstance(v, bool) for v in w):
        return "BOOLEAN"
    if w and all(isinstance(v, int) and not isinstance(v, bool) for v in w):
        return "INTEGER"
    if w and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in w):
        return "REAL"
    return "TEXT"


def tabelle(zeilen: list[list[tuple[str, object]]]) -> tuple[list[tuple[str, str]], list[list]]:
    """Zeilen aus (Spalte, Wert)-Listen zu festen Spalten (Reihenfolge des ersten Auftretens) und Typen."""
    namen: list[str] = []
    for z in zeilen:
        for n, _ in z:
            if n not in namen:
                namen.append(n)
    dicts = [dict(z) for z in zeilen]
    werte = [[d.get(n) for n in namen] for d in dicts]
    typen = [typ([w[i] for w in werte]) for i in range(len(namen))]
    for i, t in enumerate(typen):   # gemischte ganze und gebrochene Zahlen einheitlich als REAL
        if t == "REAL":
            for w in werte:
                if isinstance(w[i], int) and not isinstance(w[i], bool):
                    w[i] = float(w[i])
    return list(zip(namen, typen)), werte


# ------------------------------------------------------------------------------------------------- Geometrie
class Geo:
    def __init__(self) -> None:
        from pyproj import CRS, Transformer
        import shapely
        from shapely.geometry import shape
        self.shapely, self.shape = shapely, shape
        self.aus_wgs = Transformer.from_crs(4326, SRID, always_xy=True)
        self.aus_3035 = Transformer.from_crs(3035, SRID, always_xy=True)
        self.wkt = {s: CRS.from_epsg(s).to_wkt("WKT1_GDAL") for s in (4326, SRID)}
        import warnings
        with warnings.catch_warnings():   # PROJ-Zeichenkette nur als Beigabe im QGIS-Projekt, maßgeblich ist das WKT
            warnings.simplefilter("ignore", UserWarning)
            self.proj4, self.proj_kurz = ort_konfig.proj4()

    def _runden(self, g):
        return self.shapely.set_precision(g, 0.01, mode="pointwise")

    def aus_geojson(self, gj: dict, multi: bool = False):
        g = self.shape(gj)
        g = self.shapely.transform(g, lambda xy: _tr(self.aus_wgs, xy))
        if multi and g.geom_type == "Polygon":
            g = self.shapely.MultiPolygon([g])
        return self._runden(g)

    def zelle(self, kennung: str):
        m = re.fullmatch(r"CRS3035RES(\d+)mN(\d+)E(\d+)", kennung)
        if not m:
            raise SystemExit(f"unbekannte Zellkennung {kennung}")
        r, n, e = (int(x) for x in m.groups())
        if r != 1000:   # Titel und Liesmich nennen das 1-km-Gitter
            raise SystemExit(f"Zelle {kennung}: Auflösung {r} m, erwartet 1000 m")
        ring = [(e, n), (e + r, n), (e + r, n + r), (e, n + r), (e, n)]
        g = self.shapely.Polygon(ring)
        return self._runden(self.shapely.transform(g, lambda xy: _tr(self.aus_3035, xy)))

    def zeile(self, g) -> tuple[bytes, tuple | None, str]:
        wkb = self.shapely.to_wkb(g, byte_order=1, include_srid=False)
        x1, y1, x2, y2 = g.bounds
        huelle = None if g.geom_type == "Point" else (x1, x2, y1, y2)
        return wkb, huelle, self.shapely.to_wkt(g, rounding_precision=2, trim=True)


def _tr(t, xy):
    import numpy as np
    x, y = t.transform(xy[:, 0], xy[:, 1])
    return np.column_stack([x, y])


# ------------------------------------------------------------------------------------------------- GeoPackage
def gp_blob(wkb: bytes, huelle: tuple | None) -> bytes:
    if huelle is None:
        return b"GP" + bytes([0, 0x01]) + struct.pack("<i", SRID) + wkb
    minx, maxx, miny, maxy = huelle
    return b"GP" + bytes([0, 0x03]) + struct.pack("<i4d", SRID, minx, maxx, miny, maxy) + wkb


class GPKG:
    def __init__(self, pfad: Path, geo: Geo, stand: str) -> None:
        if pfad.exists():
            pfad.unlink()
        self.stand = stand + STAND_ZEIT
        self.c = sqlite3.connect(pfad)
        c = self.c
        c.execute("PRAGMA application_id = 1196444487")
        c.execute("PRAGMA user_version = 10400")
        c.executescript("""
            CREATE TABLE gpkg_spatial_ref_sys (srs_name TEXT NOT NULL, srs_id INTEGER NOT NULL PRIMARY KEY,
              organization TEXT NOT NULL, organization_coordsys_id INTEGER NOT NULL, definition TEXT NOT NULL,
              description TEXT);
            CREATE TABLE gpkg_contents (table_name TEXT NOT NULL PRIMARY KEY, data_type TEXT NOT NULL,
              identifier TEXT UNIQUE, description TEXT DEFAULT '',
              last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              min_x DOUBLE, min_y DOUBLE, max_x DOUBLE, max_y DOUBLE, srs_id INTEGER,
              CONSTRAINT fk_gc_r_srs_id FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id));
            CREATE TABLE gpkg_geometry_columns (table_name TEXT NOT NULL, column_name TEXT NOT NULL,
              geometry_type_name TEXT NOT NULL, srs_id INTEGER NOT NULL, z TINYINT NOT NULL, m TINYINT NOT NULL,
              CONSTRAINT pk_geom_cols PRIMARY KEY (table_name, column_name),
              CONSTRAINT uk_gc_table_name UNIQUE (table_name),
              CONSTRAINT fk_gc_tn FOREIGN KEY (table_name) REFERENCES gpkg_contents(table_name),
              CONSTRAINT fk_gc_srs FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys (srs_id));
        """)
        c.executemany("INSERT INTO gpkg_spatial_ref_sys VALUES (?,?,?,?,?,?)", [
            ("Undefined cartesian SRS", -1, "NONE", -1, "undefined", "undefined cartesian coordinate reference system"),
            ("Undefined geographic SRS", 0, "NONE", 0, "undefined", "undefined geographic coordinate reference system"),
            ("WGS 84 geodetic", 4326, "EPSG", 4326, geo.wkt[4326],
             "longitude/latitude coordinates in decimal degrees on the WGS 84 spheroid"),
            (ort_konfig.SRS_NAMEN[SRID], SRID, "EPSG", SRID, geo.wkt[SRID], ort_konfig.srs_name()),
        ])

    def ebene(self, e: "Ebene") -> None:
        spalten = ", ".join(f'"{n}" {t}' for n, t in e.felder)
        geo = f', "geom" {e.geom}' if e.geom else ""
        self.c.execute(f'CREATE TABLE "{e.name}" (fid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL{geo}, {spalten})')
        hx: list = [None] * 4
        rows = []
        for z, g in zip(e.zeilen, e.geometrie or [None] * len(e.zeilen)):
            if e.geom:
                wkb, huelle, _ = g
                if huelle is None:
                    x, y = struct.unpack("<dd", wkb[5:21])
                    h = (x, x, y, y)
                else:
                    h = huelle
                hx = [h[0] if hx[0] is None else min(hx[0], h[0]), h[1] if hx[1] is None else max(hx[1], h[1]),
                      h[2] if hx[2] is None else min(hx[2], h[2]), h[3] if hx[3] is None else max(hx[3], h[3])]
                rows.append([gp_blob(wkb, huelle), *z])
            else:
                rows.append(list(z))
        namen = (['"geom"'] if e.geom else []) + [f'"{n}"' for n, _ in e.felder]
        self.c.executemany(f'INSERT INTO "{e.name}" ({", ".join(namen)}) VALUES ({", ".join("?" * len(namen))})', rows)
        if e.geom:
            self.c.execute("INSERT INTO gpkg_contents VALUES (?,?,?,?,?,?,?,?,?,?)",
                           (e.name, "features", e.name, e.titel["pl"], self.stand, hx[0], hx[2], hx[1], hx[3], SRID))
            self.c.execute("INSERT INTO gpkg_geometry_columns VALUES (?,?,?,?,0,0)", (e.name, "geom", e.geom, SRID))
        else:
            self.c.execute("INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change) "
                           "VALUES (?,?,?,?,?)", (e.name, "attributes", e.name, e.titel["pl"], self.stand))

    def stile(self, stile: dict[str, str]) -> None:
        self.c.execute("""CREATE TABLE layer_styles (id INTEGER PRIMARY KEY AUTOINCREMENT, f_table_catalog TEXT(256),
            f_table_schema TEXT(256), f_table_name TEXT(256), f_geometry_column TEXT(256), styleName TEXT(30),
            styleQML TEXT, styleSLD TEXT, useAsDefault BOOLEAN, description TEXT, owner TEXT(30), ui TEXT(30),
            update_time DATETIME)""")
        for name, qml in stile.items():
            self.c.execute("INSERT INTO layer_styles (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, "
                           "styleName, styleQML, styleSLD, useAsDefault, description, owner, ui, update_time) "
                           "VALUES ('', '', ?, 'geom', ?, ?, '', 1, ?, '', '', ?)",
                           (name, f"kiezatlas_{name}", qml, "Kiezatlas Kraków", self.stand))
        self.c.execute("INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change) "
                       "VALUES ('layer_styles', 'attributes', 'layer_styles', 'QGIS', ?)", (self.stand,))

    def schliessen(self) -> None:
        self.c.commit()
        self.c.execute("VACUUM")
        self.c.close()


# ------------------------------------------------------------------------------------------------- Ebenen
class Ebene:
    """Eine Ebene: name, Titel je Sprache, Geometrietyp (POINT, POLYGON, MULTIPOLYGON oder None), Spalten, Zeilen,
    Geometrie-Tupel (wkb, hülle, wkt) je Zeile, Herkunft (Datendateien) und Vermerke [(Lizenz, Vermerk wörtlich)]."""

    def __init__(self, name, titel, geom, zeilen_paare, geometrie, herkunft, vermerke, odbl):
        self.name, self.titel, self.geom = name, titel, geom
        self.felder, self.zeilen = tabelle(zeilen_paare)
        self.geometrie = geometrie
        self.herkunft, self.vermerke, self.odbl = herkunft, vermerke, odbl


def q(d: dict, *weg):
    for k in weg:
        d = d[k]
    return d


def vermerke(D: Daten) -> dict[str, tuple[str, str, str]]:
    """Kurzname → (Lizenz, Quelle, Vermerk); Quelle und Vermerk wörtlich aus den Datendateien (Quelle leer, wenn die
    Datei sie nur im Vermerk nennt). Beim ZBK ist die Quelle der Vermerk der Stadt, der Vermerk die Haftungsklausel."""
    sb = D["steckbrief"]["quellen"]
    gk = D["gebaeude_kennzahlen"]["quellen"]
    # Lizenzangabe einheitlich polnisch: für alle GUGiK-Daten die Zeile aus einrichtungen.js, für den GUS die
    # Bedingung aus seinem Vermerk (in steckbrief.js steht die Angabe nur deutsch)
    BDOT = D["einrichtungen"]["quellen"]["bdot10k"]["lizenz"]
    GUS = "kopiowanie dozwolone z podaniem źródła (warunki GUS)"
    # Quelle der Eurostat-Zeile: Name des Datensatzes (wörtlich aus quelle) und Adresse (wörtlich aus url); die
    # Zeile quelle selbst ist deutsch („Polen“, „Datei“). Für OSM: eine Zeile mit dem englischen Vermerk aus
    # sanierung_odbl.js (so stehen die Seiten in pl und en); die Kopfkommentare der _odbl-Dateien sind deutsche
    # Herkunftsangaben mit Skriptpfaden und kein Quellenvermerk (Nachtrag in pruefen/S4_protokoll.md).
    eu = sb["eurostat2021"]
    eu_name = ", ".join(eu["quelle"].split(", ")[:2])
    if eu_name not in eu["quelle"] or not eu_name.startswith("Eurostat"):
        raise SystemExit(f"steckbrief.js eurostat2021.quelle unerwartet: {eu['quelle']}")
    osm_v = D["sanierung_odbl"]["quellen"]["osm"]["vermerk_sprachen"]["en"]
    osm = ("ODbL 1.0", f"OpenStreetMap ({D['einrichtungen_odbl']['quellen']['osm']['url']})", osm_v)
    v = {
        "nsp": (GUS, sb["nsp2021"]["quelle"], sb["nsp2021"]["vermerk"]),
        "eurostat": (eu["lizenz"], f"{eu_name} ({eu['url']})", eu["vermerk"]),
        "bdot_prg": (BDOT, sb["bdot10k"]["quelle"], sb["bdot10k"]["vermerk"]),
        "bdot_geb": (BDOT, gk["bdot10k"]["vermerk"]),
        "delegatury": (BDOT, gk["delegatury"]["vermerk"]),
        "lod2": (BDOT, gk["hoehen"]["vermerk"]),
        "bdot_einr": (BDOT, D["einrichtungen"]["quellen"]["bdot10k"]["vermerk"]),
        "bdot_klimat": (BDOT, D["klimat"]["quelle"]["vermerk"]),
        "bdot_denkmal": (BDOT, D["denkmale_bdot"]["quelle"]["vermerk"]),
        "wd": ("CC0 1.0", D["denkmale"]["quellen"]["wd"]["vermerk"]),
        "bdot_sanierung": (BDOT, D["sanierung"]["quellen"]["bdot"]["vermerk"]),
        "ztp": (D["haltestellen"]["quellen"]["ztp"]["lizenz"], D["haltestellen"]["quellen"]["ztp"]["vermerk"]),
        "prawo_oswiatowe": (D["planer_odbl"]["quellen"]["prawo_oswiatowe"]["lizenz"],
                            D["planer_odbl"]["quellen"]["prawo_oswiatowe"]["vermerk"]),
        "zbk": ("ponowne wykorzystywanie informacji sektora publicznego (Gmina Miejska Kraków)",
                D["sanierung"]["quellen"]["zbk"]["vermerk"], D["sanierung"]["quellen"]["zbk"]["odpowiedzialnosc"]),
        "zbk_odbl": ("ponowne wykorzystywanie informacji sektora publicznego (Gmina Miejska Kraków)",
                     D["sanierung_odbl"]["quellen"]["zbk"]["vermerk"], D["sanierung_odbl"]["quellen"]["zbk"]["odpowiedzialnosc"]),
        "osm": osm,
    }
    return {k: (w[0], "", w[1]) if len(w) == 2 else w for k, w in v.items()}


T = {  # Titel je Ebene: pl, en, de
    "miasto": ("Kraków: liczby dla całego miasta", "Kraków: city-wide figures", "Krakau: Zahlen der ganzen Stadt"),
    "delegatury": ("Cztery delegatury (dawne dzielnice)", "Four delegatury (historic boroughs)",
                   "Vier delegatury (historische Stadtbezirke)"),
    "siatka_1km": ("Siatka 1 km: ludność i odległości w linii prostej", "1 km grid: population and straight-line distances",
              "1-km-Gitter: Einwohner und Luftlinie"),
    "siatka_1km_pokrycie": ("Siatka 1 km: pokrycie terenu", "1 km grid: land cover", "1-km-Gitter: Bodenbedeckung"),
    "placowki_bdot": ("Placówki z BDOT10k", "Facilities from BDOT10k", "Einrichtungen aus BDOT10k"),
    "przystanki": ("Przystanki z klasą częstotliwości", "Stops with frequency class", "Haltestellen mit Taktklasse"),
    "bdot_kompleksy": ("Kompleksy BDOT10k (muzea, forty, zespoły zabudowy)",
                              "BDOT10k complexes (museums, forts, building ensembles)",
                              "BDOT10k-Komplexe (Museen, Forts, Bauensembles)"),
    "bdot_kamienica_nazwa": ("Budynki o nazwie „Kamienica …” w BDOT10k", "Buildings named “Kamienica …” in BDOT10k",
                           "Gebäude mit dem Namen „Kamienica …“ in BDOT10k"),
    "rejestr_zabytkow": ("Punkty rejestru zabytków z Wikidanych: obiekty o tym samym numerze rejestru jako jeden punkt "
                         "(położenie niesprawdzone)",
                         "Heritage register points from Wikidata: objects with the same register number as one point "
                         "(location not verified)",
                         "Registerpunkte aus Wikidata: Objekte mit gleicher Registernummer als ein Punkt "
                         "(Lage ungeprüft)"),
    "zbk_wykaz_dzielnice": ("Wykaz ZBK: liczby według dzielnicy z wykazu", "ZBK list: counts by district as listed",
                        "ZBK-Liste: Zählungen je dzielnica laut Liste"),
    "dzielnice": ("18 dzielnic: granice i wskaźniki", "18 districts: boundaries and indicators",
                  "18 dzielnice: Grenzen und Kennzahlen"),
    "siatka_1km_odbl": ("Siatka 1 km z przypisaniem do dzielnicy i drogą pieszą",
                   "1 km grid with district and walking distance", "1-km-Gitter mit dzielnica und Fußweg"),
    "dostepnosc": ("Dostępność placówek według dzielnicy", "Access to facilities by district",
                   "Versorgung je dzielnica"),
    "placowki_osm": ("Lekarze i apteki z OpenStreetMap", "Doctors and pharmacies from OpenStreetMap",
                         "Ärzte und Apotheken aus OpenStreetMap"),
    "osm_heritage_start_date": ("Obiekty OSM z heritage lub start_date (położenie niesprawdzone)",
                    "OSM objects with heritage or start_date (location not verified)",
                    "OSM-Objekte mit heritage oder start_date (Lage ungeprüft)"),
    "zbk_budynki": ("Budynki ZBK w zasobie publicznym (położenie)", "ZBK buildings in public ownership (location)",
                        "ZBK-Gebäude in öffentlichem Eigentum (Lage)"),
    "zbk_typologia_dzielnice": ("Typologia bloków według dzielnicy (szacunek)", "Block typology by district (estimate)",
                            "Typologie der Blöcke je dzielnica (Schätzung)"),
}


# Titel der Denkmalebenen, wenn die Lage in einer Stichprobe am Luftbild geprüft ist (sichtpruefung.geprueft true)
T_SICHT = {
    "rejestr_zabytkow": ("Punkty rejestru zabytków z Wikidanych: obiekty o tym samym numerze rejestru jako jeden punkt "
                         "(położenie sprawdzone na próbie)",
                         "Heritage register points from Wikidata: objects with the same register number as one point "
                         "(location checked on a sample)",
                         "Registerpunkte aus Wikidata: Objekte mit gleicher Registernummer als ein Punkt "
                         "(Lage in Stichprobe geprüft)"),
    "osm_heritage_start_date": ("Obiekty OSM z heritage lub start_date (położenie obiektów z heritage sprawdzone na próbie)",
                                "OSM objects with heritage or start_date (location of heritage objects checked on a sample)",
                                "OSM-Objekte mit heritage oder start_date (Lage der Objekte mit heritage in Stichprobe geprüft)"),
}


def titel(name: str, sicht: bool = False) -> dict:
    return dict(zip(("pl", "en", "de"), T_SICHT[name] if sicht else T[name]))


def geprueft(d: dict) -> bool:
    sp = d.get("sichtpruefung") or {}
    return sp.get("geprueft") is True and "ergebnis" in sp


def ebenen_bauen(D: Daten, geo: Geo) -> list[Ebene]:
    V = vermerke(D)
    E: list[Ebene] = []

    def v(*k):
        return [V[x] for x in k]

    # --- ohne ODbL
    sb, gk, kl, sa = D["steckbrief"], D["gebaeude_kennzahlen"], D["klimat"], D["sanierung"]
    stadt = sb["stadt"]
    zeile = [("teryt", stadt["teryt"]), ("nazwa", stadt["name"])]
    zeile += flach({k: w for k, w in stadt.items() if k not in ("teryt", "name")})
    zeile += flach({k: w for k, w in gk["stadt"].items() if k != "name"}, "geb")
    zeile += flach({k: w for k, w in kl["stadt"].items() if k != "teryt"}, "klimat")
    zeile += flach(sa["typologie"]["stadt"], "typ")
    E.append(Ebene("miasto", titel("miasto"), None, [zeile], None,
                   ["steckbrief", "gebaeude_kennzahlen", "klimat", "sanierung"],
                   v("nsp", "eurostat", "bdot_prg", "bdot_geb", "lod2", "bdot_klimat", "bdot_sanierung"), False))

    zeilen = []
    for nr, g in sorted(sb["gruppen"].items()):
        t, name = g["teryt"], g["name"]
        z = [("gruppe", nr), ("teryt", t), ("nazwa", name)]
        z += flach({k: w for k, w in g.items() if k not in ("teryt", "name")})
        z += flach({k: w for k, w in gk["delegatury"][t].items() if k != "name"}, "geb")
        z += flach({k: w for k, w in kl["delegaturen"][t].items() if k not in ("name", "gruppe_nach_name")}, "klimat")
        z += flach(sa["typologie"]["delegaturen"][name], "typ")
        z += flach(D["denkmale_bdot"]["delegaturen"][name], "bdot")
        zeilen.append(z)
    E.append(Ebene("delegatury", titel("delegatury"), None, zeilen, None,
                   ["steckbrief", "gebaeude_kennzahlen", "klimat", "sanierung", "denkmale_bdot"],
                   v("nsp", "eurostat", "delegatury", "bdot_geb", "lod2", "bdot_klimat", "bdot_sanierung", "bdot_denkmal"),
                   False))

    # Zellen ohne Zuordnung: Einwohner (Eurostat) und Luftlinie; Geometrie aus der Zellkennung
    zo, er = D["zellen_odbl"]["features"], D["erreichbar"]
    ids = [f["properties"]["id"] for f in zo]
    if (len(ids), ids[0], ids[-1]) != (er["anzahl"], er["erste_id"], er["letzte_id"]):
        raise SystemExit("erreichbar.js passt nicht zur Reihenfolge von zellen_odbl.js")
    zeilen, geom = [], []
    for i, f in enumerate(zo):
        p = f["properties"]
        z = [(k, p[k]) for k in ("id", "ew", "a_ges", "q_u15", "q_65p")]
        z += [(f"luftlinie_m_{a}", er["werte"][a][i]) for a in er["arten"]]
        zeilen.append(z)
        geom.append(geo.zeile(geo.zelle(p["id"])))
    E.append(Ebene("siatka_1km", titel("siatka_1km"), "POLYGON", zeilen, geom, ["zellen_odbl", "erreichbar"],
                   v("eurostat", "bdot_einr", "ztp"), False))

    zeilen, geom = [], []
    for f in D["klimat_zellen"]["features"]:
        zeilen.append(flach(f["properties"]))
        geom.append(geo.zeile(geo.aus_geojson(f["geometry"])))
    E.append(Ebene("siatka_1km_pokrycie", titel("siatka_1km_pokrycie"), "POLYGON", zeilen, geom, ["klimat_zellen"],
                   v("bdot_klimat"), False))

    for name, datei, weg, ver, ohne in (
        ("placowki_bdot", "einrichtungen", ("features",), ("bdot_einr",), ()),
        ("przystanki", "haltestellen", ("features",), ("ztp", "bdot_prg"), ("st",)),
        ("bdot_kompleksy", "denkmale_bdot", ("komplexe", "features"), ("bdot_denkmal",), ()),
        ("bdot_kamienica_nazwa", "denkmale_bdot", ("namensbezug", "features"), ("bdot_denkmal",), ()),
    ):
        feats = q(D[datei], *weg)
        gtyp = {f["geometry"]["type"] for f in feats}
        if len(gtyp) != 1:
            raise SystemExit(f"{datei}: gemischte Geometrietypen {gtyp}")
        gt = {"Point": "POINT", "Polygon": "POLYGON"}[gtyp.pop()]
        zeilen = [flach({k: w for k, w in f["properties"].items() if k not in ohne}) for f in feats]
        geom = [geo.zeile(geo.aus_geojson(f["geometry"])) for f in feats]
        E.append(Ebene(name, titel(name), gt, zeilen, geom, [datei], v(*ver), False))

    # Registerpunkte (bisher nur Wikidata, CC0): Quellen der Punkte als Text (wd, nid, gez). polozenie_sprawdzone je
    # Punkt bleibt 0: geprüft ist höchstens eine Stichprobe der Ebene (Prüfprotokoll Denkmale, Nachtrag 4), deren
    # Ergebnis im Liesmich steht
    R = D["denkmale"]
    feats = R["objekte"]["features"]
    zeilen = [[("q", ",".join(f["properties"]["q"]))] + flach({k: w for k, w in f["properties"].items() if k != "q"})
              + [("polozenie_sprawdzone", False)] for f in feats]
    geom = [geo.zeile(geo.aus_geojson(f["geometry"])) for f in feats]
    E.append(Ebene("rejestr_zabytkow", titel("rejestr_zabytkow", geprueft(R)), "POINT", zeilen, geom, ["denkmale"],
                   v("wd", "bdot_denkmal"), False))

    zeilen = [[("dzielnica_z_wykazu", nr)] + flach(w) for nr, w in sorted(sa["liste"]["je_dzielnica"].items())]
    E.append(Ebene("zbk_wykaz_dzielnice", titel("zbk_wykaz_dzielnice"), None, zeilen, None, ["sanierung"], v("zbk"), False))

    # --- ODbL
    st = D["stadtteile_odbl"]["features"]
    sd, gd, ks = D["steckbrief_dzielnice_odbl"]["stadtteile"], D["gebaeude_dzielnice_odbl"]["stadtteile"], \
        D["klimat_stadtteile_odbl"]["stadtteile"]
    zeilen, geom = [], []
    for f in sorted(st, key=lambda f: f["properties"]["nr"]):
        p = f["properties"]
        nr = p["nr"]
        z = [("nr", nr), ("rzymska", p["roemisch"]), ("nazwa", p["name"]), ("gruppe", p["bezirk"]),
             ("flaeche_km2", p["flaeche_km2"])]
        s = sd[nr]
        z += flach({k: w for k, w in s.items() if k not in ("name", "roemisch", "gruppe", "flaeche_km2")})
        z += flach({k: w for k, w in gd[nr].items() if k != "name"}, "geb")
        z += flach({k: w for k, w in ks[nr].items() if k != "name"}, "klimat")
        zeilen.append(z)
        geom.append(geo.zeile(geo.aus_geojson(f["geometry"], multi=True)))
    E.append(Ebene("dzielnice", titel("dzielnice"), "MULTIPOLYGON", zeilen, geom,
                   ["stadtteile_odbl", "steckbrief_dzielnice_odbl", "gebaeude_dzielnice_odbl", "klimat_stadtteile_odbl"],
                   v("osm", "eurostat", "bdot_geb", "lod2", "bdot_klimat"), True))

    ef = D["erreichbar_fuss_odbl"]
    if (ef["anzahl"], ef["erste_id"], ef["letzte_id"]) != (len(ids), ids[0], ids[-1]):
        raise SystemExit("erreichbar_fuss_odbl.js passt nicht zur Reihenfolge von zellen_odbl.js")
    zeilen, geom = [], []
    for i, f in enumerate(zo):
        p = f["properties"]
        z = [(k, p[k]) for k in ("id", "st", "ew", "a_ges", "q_u15", "q_65p")]
        z += [(f"fussweg_m_{a}", ef["werte"][a][i]) for a in ef["arten"]]
        zeilen.append(z)
        geom.append(geo.zeile(geo.zelle(p["id"])))
    E.append(Ebene("siatka_1km_odbl", titel("siatka_1km_odbl"), "POLYGON", zeilen, geom, ["zellen_odbl", "erreichbar_fuss_odbl"],
                   v("osm", "eurostat", "bdot_einr", "ztp"), True))

    zeilen = []
    for datei in ("planer_odbl", "planer_fuss_odbl"):
        P = D[datei]
        raeume = [(nr, r) for nr, r in sorted(P["raeume"].items())] + [("", P["gesamt"])]
        for nr, r in raeume:
            for w in r["werte"]:
                z = [("st", nr or None), ("nazwa", r["name"]), ("ew", r["ew"])]
                z += [(k, w.get(k)) for k in ("kennzahl", "art", "methode", "einheit", "status", "vorlaeufig", "q")]
                rw = w.get("richtwert") or {}
                z += [("richtwert_wert", rw.get("wert")), ("richtwert_einheit", rw.get("einheit")),
                      ("richtwert_q", rw.get("q")), ("richtwert_seite", rw.get("seite")), ("radius_m", w.get("radius_m"))]
                z += [(k, w.get(k)) for k in ("wert", "zaehler", "nenner", "stand")]
                zeilen.append(z)
    E.append(Ebene("dostepnosc", titel("dostepnosc"), None, zeilen, None, ["planer_odbl", "planer_fuss_odbl"],
                   v("osm", "eurostat", "bdot_einr", "ztp", "prawo_oswiatowe"), True))

    for name, datei, weg, ver in (
        ("placowki_osm", "einrichtungen_odbl", ("features",), ("osm",)),
        ("osm_heritage_start_date", "denkmale_odbl", ("objekte", "features"), ("osm", "bdot_denkmal")),
        ("zbk_budynki", "sanierung_odbl", ("punkte", "features"), ("osm", "zbk_odbl", "bdot_sanierung", "lod2")),
    ):
        feats = q(D[datei], *weg)
        zeilen = [flach(f["properties"]) for f in feats]
        if name == "osm_heritage_start_date":   # je Punkt 0, siehe Registerpunkte
            zeilen = [z + [("polozenie_sprawdzone", False)] for z in zeilen]
        geom = [geo.zeile(geo.aus_geojson(f["geometry"])) for f in feats]
        E.append(Ebene(name, titel(name, name == "osm_heritage_start_date" and geprueft(D[datei])), "POINT", zeilen, geom,
                       [datei], v(*ver), True))

    td = D["sanierung_odbl"]["typologie_dzielnice"]
    zeilen = [[("st", nr), ("szacunek", td["schaetzung"])] + flach(w) for nr, w in sorted(td["je_dzielnica"].items())]
    E.append(Ebene("zbk_typologia_dzielnice", titel("zbk_typologia_dzielnice"), None, zeilen, None, ["sanierung_odbl"],
                   v("osm", "bdot_sanierung"), True))
    return E


# ------------------------------------------------------------------------------------------------- Stile, QGIS
def _farbe(h: str, a: int = 255) -> str:
    h = h.lstrip("#")
    return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a}"


def _opt(d: dict) -> str:
    o = "".join(f'<Option type="QString" name="{escape(k)}" value="{escape(str(v))}"/>' for k, v in d.items())
    p = "".join(f'<prop k="{escape(k)}" v="{escape(str(v))}"/>' for k, v in d.items())
    return f'<Option type="Map">{o}</Option>{p}'


def _marker(name: str, farbe: str, form: str = "circle", groesse: float = 2.0) -> str:
    return (f'<symbol type="marker" name="{name}" alpha="1" clip_to_extent="1" force_rhr="0">'
            '<layer class="SimpleMarker" enabled="1" locked="0" pass="0">'
            + _opt({"name": form, "color": _farbe(farbe), "outline_color": _farbe(GRUND), "outline_style": "solid",
                    "outline_width": "0.25", "outline_width_unit": "MM", "size": groesse, "size_unit": "MM",
                    "angle": "0", "joinstyle": "miter", "scale_method": "diameter"})
            + "</layer></symbol>")


def _flaeche(name: str, farbe: str | None, rand: str | None, breite: float = 0.26) -> str:
    return (f'<symbol type="fill" name="{name}" alpha="1" clip_to_extent="1" force_rhr="0">'
            '<layer class="SimpleFill" enabled="1" locked="0" pass="0">'
            + _opt({"color": _farbe(farbe or GRUND, 255 if farbe else 0), "style": "solid" if farbe else "no",
                    "outline_color": _farbe(rand or GRUND, 255 if rand else 0), "outline_style": "solid" if rand else "no",
                    "outline_width": breite, "outline_width_unit": "MM", "joinstyle": "miter"})
            + "</layer></symbol>")


def _qml(renderer: str, feld: str = "") -> str:
    besch = ""
    if feld:
        besch = ('<labeling type="simple"><settings calloutType="simple">'
                 f'<text-style fieldName="{escape(feld)}" isExpression="1" fontFamily="Noto Sans" fontSize="8" '
                 f'fontSizeUnit="Point" textColor="{_farbe(INK)}" textOpacity="1">'
                 f'<text-buffer bufferDraw="1" bufferSize="0.8" bufferSizeUnits="MM" bufferColor="{_farbe(GRUND)}" '
                 'bufferOpacity="0.85"/></text-style><placement placement="1" centroidInside="1"/>'
                 '<rendering drawLabels="1" obstacle="1"/></settings></labeling>')
    return ("<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n"
            f'<qgis version="3.34.0-Prizren" styleCategories="Symbology|Labeling" labelsEnabled="{1 if feld else 0}">'
            f"{renderer}{besch}<blendMode>0</blendMode><featureBlendMode>0</featureBlendMode>"
            "<layerOpacity>1</layerOpacity></qgis>\n")


def _einzeln(sym: str) -> str:
    return f'<renderer-v2 type="singleSymbol" symbollevels="0" forceraster="0" enableorderby="0"><symbols>{sym}</symbols></renderer-v2>'


def _kategorien(attr: str, kat: list[tuple[str, str, str]]) -> str:
    c = "".join(f'<category value="{escape(v)}" label="{escape(t)}" symbol="{i}" render="true"/>'
                for i, (v, t, _) in enumerate(kat))
    s = "".join(sym.replace('name="X"', f'name="{i}"') for i, (_, _, sym) in enumerate(kat))
    return (f'<renderer-v2 type="categorizedSymbol" attr="{attr}" symbollevels="0" forceraster="0" enableorderby="0">'
            f"<categories>{c}</categories><symbols>{s}</symbols></renderer-v2>")


def _abgestuft(attr: str, grenzen: list[float]) -> str:
    rng = "".join(f'<range lower="{lo}" upper="{hi}" label="{lo:g} – {hi:g}" symbol="{i}" render="true"/>'
                  for i, (lo, hi) in enumerate(zip(grenzen, grenzen[1:])))
    syms = "".join(_flaeche(str(i), STUFEN[i], None) for i in range(len(grenzen) - 1))
    return (f'<renderer-v2 type="graduatedSymbol" attr="{attr}" graduatedMethod="GraduatedColor" symbollevels="0" '
            f'forceraster="0" enableorderby="0"><ranges>{rng}</ranges><symbols>{syms}</symbols></renderer-v2>')


def stile(E: list[Ebene]) -> dict[str, str]:
    def werte(e: Ebene, feld: str) -> list:
        i = [n for n, _ in e.felder].index(feld)
        return sorted({z[i] for z in e.zeilen if z[i] is not None}, key=str)

    reihe = ["#13212a", "#3b7684", "#6a2c82", "#4d7a3c", "#2d5e86", "#7a3b57", "#1c4a5b", "#6d8cb8", "#4f5d64"]
    s: dict[str, str] = {}
    for e in E:
        if e.name == "dzielnice":
            s[e.name] = _qml(_einzeln(_flaeche("0", None, AKZENT, 0.4)), '"rzymska" || \' \' || "nazwa"')
        elif e.name in ("siatka_1km", "zelle_odbl"):
            s[e.name] = _qml(_abgestuft("ew", [0, 100, 1000, 2500, 5000, 1e7]))
        elif e.name == "siatka_1km_pokrycie":
            s[e.name] = _qml(_abgestuft("anteil_bebauung", [0, 20, 40, 60, 80, 100.01]))
        elif e.name == "przystanki":
            kl = [("I", "I", INK, 2.0), ("II", "II", "#3b5560", 1.7), ("III", "III", "#6d7f86", 1.4),
                  ("unter III", "< III", "#a3aeb2", 1.2)]
            s[e.name] = _qml(_kategorien("taktklasse", [(a, t, _marker("X", f, "triangle", g)) for a, t, f, g in kl]))
        elif e.geom == "POINT":
            feld = "art" if "art" in [n for n, _ in e.felder] else None
            if feld:
                s[e.name] = _qml(_kategorien(feld, [(str(a), str(a), _marker("X", reihe[i % len(reihe)]))
                                                     for i, a in enumerate(werte(e, feld))]))
            else:
                s[e.name] = _qml(_einzeln(_marker("0", MUTED, "circle", 1.6)))
        elif e.geom:
            s[e.name] = _qml(_einzeln(_flaeche("0", None, MUTED, 0.3)))
    return s


def _srs_xml(geo: Geo) -> str:
    return ('<spatialrefsys nativeFormat="Wkt">'
            f"<wkt>{escape(geo.wkt[SRID])}</wkt><proj4>{escape(geo.proj4)}</proj4>"
            f"<srid>{SRID}</srid><authid>EPSG:{SRID}</authid><description>{ort_konfig.SRS_NAMEN[SRID]}</description>"
            f"<projectionacronym>{geo.proj_kurz}</projectionacronym><ellipsoidacronym>EPSG:7019</ellipsoidacronym>"
            "<geographicflag>false</geographicflag></spatialrefsys>")


def projekt(E: list[Ebene], st: dict[str, str], geo: Geo, huelle: tuple) -> str:
    baum, schichten = [], []
    an = {"dzielnice", "siatka_1km", "przystanki"}
    for e in sorted((e for e in E if e.geom), key=lambda e: ({"POINT": 0, "MULTIPOLYGON": 1, "POLYGON": 2}[e.geom], e.name)):
        lid = f"kiezatlas_{e.name}"
        datei = GPKG_ODBL if e.odbl else GPKG_FREI
        quelle = f"./{datei}|layername={e.name}"
        baum.append(f'<layer-tree-layer id="{lid}" name="{escape(e.titel["pl"])}" '
                    f'checked="{"Qt::Checked" if e.name in an else "Qt::Unchecked"}" expanded="0" '
                    f'source="{escape(quelle)}" providerKey="ogr"><customproperties/></layer-tree-layer>')
        qml = st[e.name]
        innen = re.sub(r"^.*?<qgis[^>]*>|</qgis>\s*$", "", qml, flags=re.S)
        wkb = {"POINT": "Point", "POLYGON": "Polygon", "MULTIPOLYGON": "MultiPolygon"}[e.geom]
        schichten.append(
            f'<maplayer type="vector" geometry="{"Point" if e.geom == "POINT" else "Polygon"}" wkbType="{wkb}" '
            f'labelsEnabled="{1 if "labelsEnabled=\"1\"" in qml else 0}" hasScaleBasedVisibilityFlag="0" readOnly="0">'
            f"<id>{lid}</id><datasource>{escape(quelle)}</datasource><layername>{escape(e.titel['pl'])}</layername>"
            f'<srs>{_srs_xml(geo)}</srs><provider encoding="UTF-8">ogr</provider>{innen}</maplayer>')
    x1, x2, y1, y2 = huelle
    t = "Kiezatlas Kraków"
    return ("<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n"
            f'<qgis projectname="{t}" version="3.34.0-Prizren"><homePath path=""/><title>{t}</title>'
            f"<projectCrs>{_srs_xml(geo)}</projectCrs>"
            f"<layer-tree-group><customproperties/>{''.join(baum)}</layer-tree-group>"
            '<mapcanvas name="theMapCanvas" annotationsVisible="1"><units>meters</units>'
            f"<extent><xmin>{x1:.0f}</xmin><ymin>{y1:.0f}</ymin><xmax>{x2:.0f}</xmax><ymax>{y2:.0f}</ymax></extent>"
            f"<rotation>0</rotation><destinationsrs>{_srs_xml(geo)}</destinationsrs></mapcanvas>"
            f"<projectlayers>{''.join(schichten)}</projectlayers>"
            '<properties><Paths><Absolute type="bool">false</Absolute></Paths>'
            '<Measure><Ellipsoid type="QString">EPSG:7019</Ellipsoid></Measure></properties></qgis>\n')


def zip_fest(pfad: Path, dateien: dict[str, bytes]) -> None:
    with zipfile.ZipFile(pfad, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, inhalt in sorted(dateien.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, inhalt)


# ------------------------------------------------------------------------------------------------- CSV
def csv_wert(v, komma: bool):
    if v is None:
        return ""
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, float):
        s = repr(v)
        if "e" in s or "E" in s:
            s = format(v, "f")
        return s.replace(".", ",") if komma else s
    return v


def csv_schreiben(pfad: Path, kopf: list[str], zeilen: list[list], komma: bool) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with pfad.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(kopf)
        for z in zeilen:
            w.writerow([csv_wert(v, komma) for v in z])


def ebene_csv(ordner: Path, e: Ebene, komma: bool) -> None:
    kopf = [n for n, _ in e.felder]
    if e.geom == "POINT":
        zeilen = [z + [float(round(struct.unpack("<dd", g[0][5:21])[0], 2)), float(round(struct.unpack("<dd", g[0][5:21])[1], 2))]
                  for z, g in zip(e.zeilen, e.geometrie)]
        csv_schreiben(ordner / f"{e.name}.csv", kopf + ["x", "y"], zeilen, komma)
    elif e.geom:
        csv_schreiben(ordner / f"{e.name}.csv", kopf + ["wkt"], [z + [g[2]] for z, g in zip(e.zeilen, e.geometrie)], komma)
    else:
        csv_schreiben(ordner / f"{e.name}.csv", kopf, e.zeilen, komma)


# ------------------------------------------------------------------------------------------------- Liesmich
def lizenz_zeilen(E: list[Ebene]) -> list[list[str]]:
    z = []
    for e in E:
        datei = GPKG_ODBL if e.odbl else GPKG_FREI
        gesamt = "ODbL 1.0" if e.odbl else "; ".join(dict.fromkeys(l for l, _, _ in e.vermerke))
        for lizenz, quelle, vermerk in dict.fromkeys(e.vermerke):
            z.append([datei, e.name, gesamt, lizenz, quelle, vermerk])
    return z


def pola_zeilen(E: list[Ebene], D: Daten) -> tuple[list[list], list[list]]:
    """Bedeutung je (Ebene, Feld) und je (Feld, Wert) auf pl, en, de; bricht ab, wenn eine Erklärung fehlt."""
    k = pola.kontext(D)
    W = pola.wartosci(k)
    pz, wz, fehlt = [], [], []
    lic = [n for n, _ in LZ_FELDER]
    for e in E + [None]:
        name = e.name if e else "licencje"
        felder = [n for n, _ in e.felder] if e else lic
        extra = (["x", "y"] if e.geom == "POINT" else ["wkt"] if e.geom else []) if e else []
        for f in felder + extra:
            o = pola.opis(name, f, k)
            if o is None:
                fehlt.append(f"{name}.{f}")
                continue
            pz.append([name, f, *o])
        if not e:
            continue
        for i, (f, _) in enumerate(e.felder):
            if f not in pola.KATEGORIEN:
                continue
            for w in sorted({z[i] for z in e.zeilen if z[i] is not None}, key=str):
                o = pola.wert_opis(W, e.name, f, w)
                if o is None:
                    fehlt.append(f"{e.name}.{f}={w}")
                    continue
                wz.append([e.name, f, w, *o])
    if fehlt:
        raise SystemExit("ohne Erklärung in skripte/export_pola_krakow.py: " + ", ".join(fehlt[:20]))
    return pz, wz


LZ_FELDER = [("plik", "TEXT"), ("warstwa", "TEXT"), ("licencja_pliku", "TEXT"), ("licencja_zrodla", "TEXT"),
             ("zrodlo", "TEXT"), ("nota", "TEXT")]
POLA_FELDER = [("warstwa", "TEXT"), ("pole", "TEXT"), ("opis_pl", "TEXT"), ("opis_en", "TEXT"), ("opis_de", "TEXT")]
WART_FELDER = [("warstwa", "TEXT"), ("pole", "TEXT"), ("wartosc", "TEXT"), ("opis_pl", "TEXT"), ("opis_en", "TEXT"),
               ("opis_de", "TEXT")]
POLA_TITEL = {"pola": "Znaczenie pól", "wartosci": "Znaczenie wartości kodowanych"}


LIESMICH = {
    "pl": {
        "datei": "CZYTAJ.md",
        "titel": "Kiezatlas Kraków: dane do pobrania",
        "stand": "Stan danych: wyliczono z plików atlasu (katalog `daten/`), ostatnia data w danych: {stand}. Skrypt: `skripte/16_export_krakow.py`.",
        "pliki": "Pliki",
        "p_frei": "GeoPackage bez danych z OpenStreetMap. Licencje źródeł w tabeli `licencje`.",
        "p_odbl": "GeoPackage z danymi z OpenStreetMap i wszystkim, co przypisano do dzielnic według granic z OSM. Cały plik: Open Database License 1.0, © OpenStreetMap contributors ({url}).",
        "p_csv": "Te same warstwy jako CSV (UTF-8 z BOM, separator średnik, kropka dziesiętna).",
        "p_csv_pl": "To samo z **przecinkiem dziesiętnym** i bez separatora tysięcy: otwiera się poprawnie w polskim Excelu i LibreOffice (liczby jako liczby).",
        "p_qgz": "Projekt QGIS (ścieżki względne, oba pliki GeoPackage obok w tym samym katalogu).",
        "p_lic": "Licencja i dosłowna nota o źródle dla każdej warstwy.",
        "p_zip": "Wszystkie pliki CSV z `licencje.csv`, `pola.csv`, `wartosci.csv` i plikami CZYTAJ, README, LIESMICH w jednym archiwum.",
        "p_pola": "Znaczenie każdego pola (`pola.csv`) i każdej wartości kodowanej (`wartosci.csv`) po polsku, angielsku i niemiecku; także jako tabele `pola` i `wartosci` w obu plikach GeoPackage.",
        "warstwy": "Warstwy",
        "kopf": "| Warstwa | Plik | Geometria | Wiersze | Z plików atlasu |",
        "bez": "bez",
        "uklad": "Układ współrzędnych: {srs}. Współrzędne zaokrąglone do 0,01 m; geometrie nie są upraszczane. Nazwy pól są takie jak w plikach atlasu (częściowo niemieckie skróty); ich znaczenie opisują sekcje poniżej oraz `pola.csv` i `wartosci.csv`. Wartości logiczne w CSV: 1 = tak, 0 = nie; puste pole = brak danych.",
        "pola": "Znaczenie pól",
        "pola_kopf": "| Pole | Znaczenie |",
        "wart": "Wartości kodowane",
        "wart_kopf": "| Pole | Wartość | Znaczenie |",
        "siatka": "Warstwa `siatka_1km` przejmuje z `zellen_odbl` tylko liczbę mieszkańców i udziały grup wieku (Eurostat), bez przypisania do dzielnicy (`st`); geometria komórki powstaje z jej kodu w siatce Eurostatu. Komórki to te, których środek leży w granicach miasta z BDOT10k, dlatego warstwa nie zawiera danych z OpenStreetMap.",
        "brak": "Czego nie ma w eksporcie",
        "brak_t": "Te pliki atlasu zawierają jeszcze dane przykładowe (`fixture: true`), bo brakuje ręcznego pobrania źródła; nie ma ich w eksporcie:",
        "brak_keine": "Żaden plik atlasu nie zawiera już danych przykładowych.",
        "ohne_ebene": "Bez własnej warstwy w eksporcie są jeszcze (dane rzeczywiste, tylko jako pliki atlasu w katalogu `daten/`):",
        "granice": "Ograniczenia",
        "granice_t": [
            "Brak lat budowy i danych o ogrzewaniu: rok budowy w ewidencji jest płatny, rejestr CEEB nie jest otwarty. Okres budowy (`ep`) mają tylko pojedyncze obiekty: ze znacznikiem `start_date` w OSM (warstwa `osm_heritage_start_date`) i z datą powstania w Wikidanych (warstwa `rejestr_zabytkow`), niesprawdzony i nigdy dla obszarów.",
            "Ludność pochodzi z siatki Eurostatu ({siatka_pl}); wartości dla dzielnic powstają przez sumowanie danych z komórek przypisanych według ich środka i są przybliżeniem na granicach.",
            "Typologia bloków (`typ_*`) to szacunek z BDOT10k (kondygnacje, powierzchnia, prostokątność), nie spis budynków z wielkiej płyty.",
            "Odległości to linia prosta albo droga piesza od środka komórki 1 km do najbliższej placówki; to wartości orientacyjne, nie urzędowe.",
        ],
        "lage_offen": "Położenie obiektów OSM z `heritage` lub `start_date` i punktów rejestru nie zostało sprawdzone na ortofotomapie (`polozenie_sprawdzone` = 0).",
        "lage_probe": "Położenie sprawdzono na ortofotomapie tylko na losowej próbie ({datum}): punkty rejestru (Wikidane) {wd_ja} z {wd_n} na obiekcie ({wd_q}, 95-procentowy przedział Wilsona {wd_von}–{wd_bis}), obiekty OSM z `heritage` {osm_ja} z {osm_n} ({osm_q}, {osm_von}–{osm_bis}); „tuż obok” nie liczy się jako „na obiekcie”. To wynik dla warstwy, nie dla punktu: `polozenie_sprawdzone` = 0 przy każdym punkcie. Przypisania do budynku nie sprawdzano.",
        "cytuj": "Jak cytować",
        "cytuj_t": "Kiezatlas Kraków, Stiebitz Souverain Systems UG (haftungsbeschränkt), {url}, stan danych {stand} (dane do pobrania). Szczegóły: `CITATION.cff` w repozytorium. Do każdej warstwy należy podać noty o źródłach z tabeli `licencje`.",
        "kontakt": "Błąd w danych? {mail}",
    },
    "en": {
        "datei": "README.md",
        "titel": "Kiezatlas Kraków: downloads",
        "stand": "Data state: built from the atlas data files (`daten/` folder), latest date in the data: {stand}. Script: `skripte/16_export_krakow.py`.",
        "pliki": "Files",
        "p_frei": "GeoPackage without OpenStreetMap data. Source licences in the table `licencje`.",
        "p_odbl": "GeoPackage with OpenStreetMap data and everything assigned to districts via the OSM boundaries. Whole file: Open Database License 1.0, © OpenStreetMap contributors ({url}).",
        "p_csv": "The same layers as CSV (UTF-8 with BOM, semicolon separator, decimal point).",
        "p_csv_pl": "The same with a **decimal comma** and no thousands separator, for Polish-locale Excel and LibreOffice.",
        "p_qgz": "QGIS project (relative paths; keep both GeoPackage files in the same folder).",
        "p_lic": "Licence and verbatim source notice for every layer.",
        "p_zip": "All CSV files with `licencje.csv`, `pola.csv`, `wartosci.csv` and the read-me files in one archive.",
        "p_pola": "Meaning of every field (`pola.csv`) and every coded value (`wartosci.csv`) in Polish, English and German; also as the tables `pola` and `wartosci` in both GeoPackages.",
        "warstwy": "Layers",
        "kopf": "| Layer | File | Geometry | Rows | From atlas files |",
        "bez": "none",
        "uklad": "Coordinate reference system: {srs}. Coordinates rounded to 0.01 m; geometries are not simplified. Field names are those of the atlas files (partly German abbreviations); their meaning is given in the sections below and in `pola.csv` and `wartosci.csv`. Logical values in the CSV: 1 = yes, 0 = no; an empty field means no data.",
        "pola": "Field meanings",
        "pola_kopf": "| Field | Meaning |",
        "wart": "Coded values",
        "wart_kopf": "| Field | Value | Meaning |",
        "siatka": "The layer `siatka_1km` takes from `zellen_odbl` only population and age shares (Eurostat), without the district assignment (`st`); the cell geometry is built from its Eurostat grid code. The cells are those whose centre lies within the city boundary from BDOT10k, so the layer holds no OpenStreetMap data.",
        "brak": "Not in the export",
        "brak_t": "These atlas files still hold sample data (`fixture: true`) because the manual download of the source is missing; they are not exported:",
        "brak_keine": "No atlas file holds sample data any more.",
        "ohne_ebene": "Not yet a layer of their own in the export (real data, only as atlas files in the `daten/` folder):",
        "granice": "Limits",
        "granice_t": [
            "No construction years and no heating data: the year of construction in the cadastre is paid, the CEEB register is not open. A construction period (`ep`) exists only for single objects: with a `start_date` tag in OSM (layer `osm_heritage_start_date`) and with an inception date in Wikidata (layer `rejestr_zabytkow`), unchecked and never for areas.",
            "Population comes from the Eurostat grid ({siatka_en}); district values add up cells by their centre and are approximate at the boundaries.",
            "The block typology (`typ_*`) is an estimate from BDOT10k (storeys, footprint, rectangularity), not a register of prefabricated buildings.",
            "Distances are straight-line or walking distances from the centre of a 1 km cell to the nearest facility; orientation, not an official value.",
        ],
        "lage_offen": "The location of OSM objects with `heritage` or `start_date` and of the register points has not been checked against aerial imagery (`polozenie_sprawdzone` = 0).",
        "lage_probe": "The location was checked on the orthophoto only for a random sample ({datum}): register points (Wikidata) {wd_ja} of {wd_n} on the object ({wd_q}, 95% Wilson interval {wd_von}–{wd_bis}), OSM objects with `heritage` {osm_ja} of {osm_n} ({osm_q}, {osm_von}–{osm_bis}); “just beside” does not count as “on the object”. This is a result for the layer, not for the point: `polozenie_sprawdzone` = 0 at every point. The assignment to a building has not been checked.",
        "cytuj": "How to cite",
        "cytuj_t": "Kiezatlas Kraków, Stiebitz Souverain Systems UG (haftungsbeschränkt), {url}, data state {stand} (downloads). Details: `CITATION.cff` in the repository. Each layer must carry the source notices listed in the table `licencje`.",
        "kontakt": "Found an error? {mail}",
    },
    "de": {
        "datei": "LIESMICH.md",
        "titel": "Kiezatlas Kraków: Downloads",
        "stand": "Datenstand: erzeugt aus den Datendateien des Atlas (Ordner `daten/`), jüngstes Datum in den Daten: {stand}. Skript: `skripte/16_export_krakow.py`.",
        "pliki": "Dateien",
        "p_frei": "GeoPackage ohne Daten aus OpenStreetMap. Lizenzen der Quellen in der Tabelle `licencje`.",
        "p_odbl": "GeoPackage mit den Daten aus OpenStreetMap und allem, was über die OSM-Grenzen einer dzielnica zugeordnet ist. Ganze Datei: Open Database License 1.0, © OpenStreetMap-Mitwirkende ({url}).",
        "p_csv": "Dieselben Ebenen als CSV (UTF-8 mit BOM, Semikolon, Dezimalpunkt).",
        "p_csv_pl": "Dasselbe mit **Dezimalkomma** und ohne Tausendertrenner, für Excel und LibreOffice mit polnischer (oder deutscher) Ländereinstellung.",
        "p_qgz": "QGIS-Projekt (relative Pfade; beide GeoPackages im selben Ordner lassen).",
        "p_lic": "Lizenz und wörtlicher Quellenvermerk je Ebene.",
        "p_zip": "Alle CSV mit `licencje.csv`, `pola.csv`, `wartosci.csv` und den Liesmich-Dateien in einem Archiv.",
        "p_pola": "Bedeutung jedes Felds (`pola.csv`) und jedes kodierten Werts (`wartosci.csv`) auf Polnisch, Englisch und Deutsch; auch als Tabellen `pola` und `wartosci` in beiden GeoPackages.",
        "warstwy": "Ebenen",
        "kopf": "| Ebene | Datei | Geometrie | Zeilen | Aus den Atlas-Dateien |",
        "bez": "keine",
        "uklad": "Koordinatensystem: {srs}. Koordinaten auf 0,01 m gerundet; Geometrien nicht vereinfacht. Feldnamen wie in den Atlas-Dateien; ihre Bedeutung steht in den Abschnitten unten und in `pola.csv` und `wartosci.csv`. Wahrheitswerte in der CSV: 1 = ja, 0 = nein; leeres Feld = keine Angabe.",
        "pola": "Bedeutung der Felder",
        "pola_kopf": "| Feld | Bedeutung |",
        "wart": "Kodierte Werte",
        "wart_kopf": "| Feld | Wert | Bedeutung |",
        "siatka": "Die Ebene `siatka_1km` übernimmt aus `zellen_odbl` nur Einwohner und Altersanteile (Eurostat), ohne Zuordnung zur dzielnica (`st`); die Geometrie der Zelle entsteht aus ihrer Kennung im Eurostat-Gitter. Es sind die Zellen mit Mittelpunkt in der Stadtgrenze aus BDOT10k, deshalb enthält die Ebene keine Daten aus OpenStreetMap.",
        "brak": "Nicht im Export",
        "brak_t": "Diese Atlas-Dateien enthalten noch Beispieldaten (`fixture: true`), weil der Handdownload der Quelle fehlt; sie sind nicht im Export:",
        "brak_keine": "Keine Atlas-Datei enthält noch Beispieldaten.",
        "ohne_ebene": "Noch ohne eigene Ebene im Export sind (echte Daten, nur als Atlas-Dateien im Ordner `daten/`):",
        "granice": "Grenzen",
        "granice_t": [
            "Keine Baujahre und keine Heizungsdaten: Das Baujahr im Kataster ist kostenpflichtig, das Register CEEB nicht offen. Eine Bauzeitklasse (`ep`) haben nur einzelne Objekte: mit `start_date` in OSM (Ebene `osm_heritage_start_date`) und mit Entstehungsdatum in Wikidata (Ebene `rejestr_zabytkow`), ungeprüft und nie für Flächen.",
            "Die Bevölkerung stammt aus dem Eurostat-Gitter ({siatka_de}); Werte je dzielnica summieren Zellen nach ihrem Mittelpunkt und sind an den Grenzen eine Näherung.",
            "Die Typologie der Blöcke (`typ_*`) ist eine Schätzung aus BDOT10k (Geschosse, Grundfläche, Rechteckigkeit), kein Verzeichnis der Plattenbauten.",
            "Entfernungen sind Luftlinie oder Fußweg vom Mittelpunkt einer 1-km-Zelle zur nächsten Einrichtung; Orientierung, kein amtlicher Wert.",
        ],
        "lage_offen": "Die Lage der OSM-Objekte mit `heritage` oder `start_date` und der Registerpunkte ist nicht am Luftbild geprüft (`polozenie_sprawdzone` = 0).",
        "lage_probe": "Die Lage ist am Luftbild nur in einer Zufallsstichprobe geprüft ({datum}): Registerpunkte (Wikidata) {wd_ja} von {wd_n} auf dem Objekt ({wd_q}, 95-%-Wilson-Intervall {wd_von}–{wd_bis}), OSM-Objekte mit `heritage` {osm_ja} von {osm_n} ({osm_q}, {osm_von}–{osm_bis}); „knapp daneben“ zählt nicht als „auf dem Objekt“. Das ist ein Ergebnis für die Ebene, nicht für den Punkt: `polozenie_sprawdzone` = 0 an jedem Punkt. Die Zuordnung zum Gebäude ist nicht geprüft.",
        "cytuj": "Zitieren",
        "cytuj_t": "Kiezatlas Kraków, Stiebitz Souverain Systems UG (haftungsbeschränkt), {url}, Datenstand {stand} (Downloads). Einzelheiten: `CITATION.cff` im Repository. Zu jeder Ebene gehören die Quellenvermerke aus der Tabelle `licencje`.",
        "kontakt": "Fehler gefunden? {mail}",
    },
}


def lage_satz(L: dict, lang: str, R: dict, O: dict) -> str:
    """Grenze zur Lage der Denkmalpunkte: Ergebnis der Sichtprüfung (Zahlen aus den Daten) oder Hinweis „ungeprüft“."""
    if not (geprueft(R) and geprueft(O)):
        return L["lage_offen"]
    def proz(x: float) -> str:   # ganzzahlig, 0,5 aufwärts wie auf den Seiten (Intl.NumberFormat)
        return str(int(x + 0.5)) + (" %" if lang == "de" else "%")
    w = {"datum": R["sichtpruefung"]["datum"]}
    for q, d in (("wd", R), ("osm", O)):
        e = d["sichtpruefung"]["ergebnis"]
        w.update({f"{q}_ja": e["lage"]["ja"], f"{q}_n": e["n"], f"{q}_q": proz(e["lage"]["quote"]),
                  f"{q}_von": proz(e["lage"]["wilson95"][0]), f"{q}_bis": proz(e["lage"]["wilson95"][1])})
    return L["lage_probe"].format(**w)


def liesmich(lang: str, E: list[Ebene], D: Daten, stand: str, pz: list[list], wz: list[list]) -> str:
    L = LIESMICH[lang]
    k = ort_konfig.lade()
    url = k["basis_url"]
    mail = k.get("meldeweg") or D.d["ort"].get("meldeweg")
    z = [f"# {L['titel']}", "", L["stand"].format(stand=stand), "", f"## {L['pliki']}", ""]
    z += [f"- `{GPKG_FREI}`: {L['p_frei']}", f"- `{GPKG_ODBL}`: {L['p_odbl'].format(url=ODBL_URL)}",
          f"- `csv/`, `csv_odbl/`: {L['p_csv']}", f"- `csv_pl/`, `csv_odbl_pl/`: {L['p_csv_pl']}",
          f"- `{QGZ}`: {L['p_qgz']}", f"- `licencje.csv`: {L['p_lic']}", f"- `pola.csv`, `wartosci.csv`: {L['p_pola']}",
          f"- `{CSV_ZIP}`: {L['p_zip']}", "",
          f"## {L['warstwy']}", "", L["kopf"], "|---|---|---|---:|---|"]
    for e in E:
        z.append(f"| `{e.name}`: {e.titel[lang]} | `{GPKG_ODBL if e.odbl else GPKG_FREI}` | "
                 f"{e.geom.lower() if e.geom else L['bez']} | {len(e.zeilen)} | "
                 + ", ".join(f"`{h}`" for h in e.herkunft) + " |")
    z += ["", L["siatka"], "", L["uklad"].format(srs=ort_konfig.srs_name()), "", f"## {L['brak']}", ""]
    if D.beispiel:
        z += [L["brak_t"], ""] + [f"- `daten/{b}.js`" for b in sorted(D.beispiel)]
    else:
        z.append(L["brak_keine"])
    ohne = [n for n in sorted(OHNE_EBENE) if n in D.d and n not in D.beispiel]
    if ohne:
        z += ["", L["ohne_ebene"], ""] + [f"- {OHNE_EBENE[n][lang]}: `{n}.js`" for n in ohne]
    eu = D["steckbrief"]["quellen"]["eurostat2021"]["quelle"]
    m = re.search(r"([\w.-]+\.zip)", eu)
    name = ", ".join(eu.split(", ")[:2])
    siatka = {"siatka_pl": f"{name}, plik {m.group(1)}", "siatka_en": f"{name}, file {m.group(1)}",
              "siatka_de": f"{name}, Datei {m.group(1)}"}
    z += ["", f"## {L['granice']}", ""] + [f"- {t.format(**siatka)}" for t in L["granice_t"]]
    z.append("- " + lage_satz(L, lang, D["denkmale"], D["denkmale_odbl"]))
    i = {"pl": 2, "en": 3, "de": 4}[lang]
    z += ["", f"## {L['pola']}", ""]
    for name in [e.name for e in E] + ["licencje"]:
        z += [f"### `{name}`", "", L["pola_kopf"], "|---|---|"]
        z += [f"| `{r[1]}` | {r[i]} |" for r in pz if r[0] == name]
        z.append("")
    z += [f"## {L['wart']}", "", L["wart_kopf"], "|---|---|---|"]
    gesehen = set()
    for r in wz:
        if (r[1], r[2], r[i + 1]) in gesehen:
            continue
        gesehen.add((r[1], r[2], r[i + 1]))
        z.append(f"| `{r[1]}` | `{r[2]}` | {r[i + 1]} |")
    z += ["", f"## {L['cytuj']}", "", L["cytuj_t"].format(url=url, stand=stand), "", L["kontakt"].format(mail=mail), ""]
    return "\n".join(z)


# ------------------------------------------------------------------------------------------------- Lauf
def stand_der_daten(D: Daten, E: list[Ebene]) -> str:
    """Jüngstes Datum (JJJJ-MM-TT) in den Stand-Feldern der exportierten Dateien."""
    tage = []
    for name in sorted({h.split(" ")[0] for e in E for h in e.herkunft}):
        for k, v in D.d[name].items():
            if k.startswith("stand") and isinstance(v, str):
                m = re.match(r"\d{4}-\d{2}-\d{2}", v)
                if m:
                    tage.append(m.group(0))
    return max(tage)


def erzeugen(ziel: Path) -> dict:
    D, geo = Daten(), Geo()
    E = ebenen_bauen(D, geo)
    stand = stand_der_daten(D, E)
    if ziel.exists():
        shutil.rmtree(ziel)
    ziel.mkdir(parents=True)
    st = stile(E)
    lz = lizenz_zeilen(E)
    lz_felder = LZ_FELDER
    pz, wz = pola_zeilen(E, D)
    for datei, odbl in ((GPKG_FREI, False), (GPKG_ODBL, True)):
        g = GPKG(ziel / datei, geo, stand)
        for e in E:
            if e.odbl == odbl:
                g.ebene(e)
        lic = Ebene.__new__(Ebene)
        lic.name, lic.titel, lic.geom, lic.geometrie = "licencje", {"pl": "Licencje i noty o źródłach"}, None, None
        lic.felder, lic.zeilen = lz_felder, [r for r in lz if r[0] == datei]
        g.ebene(lic)
        namen = {e.name for e in E if e.odbl == odbl} | {"licencje"}
        for tab, felder, zeilen in (("pola", POLA_FELDER, [r for r in pz if r[0] in namen]),
                                    ("wartosci", WART_FELDER, [r for r in wz if r[0] in namen])):
            t_ = Ebene.__new__(Ebene)
            t_.name, t_.titel, t_.geom, t_.geometrie = tab, {"pl": POLA_TITEL[tab]}, None, None
            t_.felder, t_.zeilen = felder, [[str(x) for x in r] for r in zeilen]
            g.ebene(t_)
        g.stile({e.name: st[e.name] for e in E if e.odbl == odbl and e.geom})
        g.schliessen()
    for e in E:
        for komma in (False, True):
            ebene_csv(ziel / (("csv_odbl" if e.odbl else "csv") + ("_pl" if komma else "")), e, komma)
    csv_schreiben(ziel / "licencje.csv", [n for n, _ in lz_felder], lz, False)
    csv_schreiben(ziel / "pola.csv", [n for n, _ in POLA_FELDER], pz, False)
    csv_schreiben(ziel / "wartosci.csv", [n for n, _ in WART_FELDER], [[str(x) for x in r] for r in wz], False)
    xs = [h for e in E if e.geom for g in e.geometrie for h in ([g[1]] if g[1] else [])]
    huelle = (min(h[0] for h in xs), max(h[1] for h in xs), min(h[2] for h in xs), max(h[3] for h in xs))
    zip_fest(ziel / QGZ, {"kiezatlas_krakow.qgs": projekt(E, st, geo, huelle).encode("utf-8")})
    for lang in ("pl", "en", "de"):
        (ziel / LIESMICH[lang]["datei"]).write_text(liesmich(lang, E, D, stand, pz, wz), encoding="utf-8")
    # alle CSV mit Lizenztabelle und Liesmich in einem Archiv, damit man sie mit einem Klick bekommt
    beilage = [p for p in sorted(ziel.rglob("*")) if p.is_file() and (p.suffix in (".csv", ".md"))]
    zip_fest(ziel / CSV_ZIP, {str(p.relative_to(ziel)): p.read_bytes() for p in beilage})
    return {"stand": stand, "ebenen": [(e.name, e.odbl, e.geom, len(e.zeilen), len(e.felder)) for e in E],
            "beispiel": D.beispiel}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dateien(ordner: Path) -> dict[str, str]:
    return {str(p.relative_to(ordner)): sha(p) for p in sorted(ordner.rglob("*")) if p.is_file()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ziel", type=Path, default=ZIEL_STANDARD)
    ap.add_argument("--pruefen", action="store_true")
    a = ap.parse_args()
    if a.pruefen:
        with tempfile.TemporaryDirectory() as t:
            neu = Path(t) / "pobierz"
            erzeugen(neu)
            alt, frisch = dateien(a.ziel) if a.ziel.exists() else {}, dateien(neu)
        ab = sorted(set(alt) ^ set(frisch)) + sorted(k for k in set(alt) & set(frisch) if alt[k] != frisch[k])
        for k in ab:
            print(f"  ABWEICHUNG {k}")
        print(f"{len(frisch)} Dateien neu erzeugt, {len(ab)} Abweichungen gegen {a.ziel.relative_to(WURZEL) if a.ziel.is_relative_to(WURZEL) else a.ziel}")
        return 1 if ab else 0
    info = erzeugen(a.ziel)
    print(f"Stand {info['stand']}; ohne Beispieldateien: {', '.join(info['beispiel']) or 'keine'}")
    for n, o, g, z, f in info["ebenen"]:
        print(f"  {n:24} {'ODbL' if o else 'frei':4} {g or '-':12} {z:6} Zeilen {f:4} Spalten")
    for k, v in dateien(a.ziel).items():
        print(f"  {v}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
