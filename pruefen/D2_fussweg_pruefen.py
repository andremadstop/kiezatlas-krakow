"""Abnahme Fußweg je Zelle gegen die Datenbank. Nur lesen, am Ende ROLLBACK (TEMP-Tabellen).

Kriterien (festgelegt in pruefen/D2_protokoll.md):
  K1  Für jede Zelle (Mittelpunkt in public.stadtteil, darin alle bewohnten) und jede gerechnete Art gibt es genau
      eine Fußweg-Zeile; bewohnte Zellen ohne Wert werden gezählt und genannt
  K2  Für jede Zelle gilt Fußweg ≥ Luftlinie (0 Verstöße). Die Luftlinie wird hier unabhängig vom Rechenskript
      ermittelt: Minimum von ST_Distance über alle Ziele der Art, ohne Index und ohne KNN.
      Liegen schon Luftlinie-Zeilen vor (Paket Versorgung), werden sie zusätzlich verglichen (Hinweis, kein
      Kriterium, weil dort eine andere Zielmenge gewählt sein kann).
  K3  Median Fußweg/Luftlinie zwischen 1,1 und 1,6 (über Zellen mit Luftlinie ≥ 100 m), sonst Ursache im Bericht
  K4  methode ist bei jeder Zeile gesetzt; jede Fußweg-Zeile (zelle_erreichbar und zelle_gruen) trägt ODbL und den
      Lizenzvermerk der Zellen (Tabellenkommentar der Zelltabelle)
  K5  Jedes Ziel einer Fußweg-Zeile steht im Zielbestand (kein Ziel aus einer fremden Quelle). Hinweis: je Art die
      Zahl der Ziele außerhalb der Stadtgrenze und der Zellen, deren nächstes Ziel dort liegt (zählen mit, kein Filter)

Aufruf: skripte/14b_fussweg.sh pruefen [--zellen schema.tabelle]      Ausgang 0 = alle Kriterien erfüllt
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "skripte"))
fw = importlib.import_module("14b_fussweg")


def vorbereiten(cur, zellen_tabelle: str) -> tuple[list[str], set[str], dict, str]:
    """TEMP-Tabellen fw_stadt, fw_zelle und fw_ziel wie im Rechenskript.

    Gibt Zell-IDs, bewohnte Zell-IDs, Ziele je Art (gesamt, außerhalb) und den Lizenzvermerk der Zellen zurück."""
    rw = fw.richtwerte()
    vermerk = fw.zellen_vermerk(cur, zellen_tabelle)
    fw.stadt_anlegen(cur)
    ids, xy, ew, _ = fw.zellen_mit_null(cur, zellen_tabelle)
    fw.zellen_temp(cur, ids, xy)
    ziele = fw.ziele_anlegen(cur, rw["gruen_arten"])
    return ids, {i for i, e in zip(ids, ew.tolist()) if e > 0}, ziele, vermerk


def pruefen(cur, zellen_tabelle: str = fw.ZELLEN_TABELLE) -> list[tuple[str, bool, str]]:
    ids, bewohnt, ziele, vermerk = vorbereiten(cur, zellen_tabelle)
    n = len(ids)
    erg: list[tuple[str, bool, str]] = []

    # K1
    cur.execute("""SELECT e.art, count(*), count(DISTINCT e.gitter_id), count(*) FILTER (WHERE c.gitter_id IS NULL),
                          count(e.meter)
                   FROM auswertung.zelle_erreichbar e LEFT JOIN fw_zelle c USING (gitter_id)
                   WHERE e.methode = 'fussweg' GROUP BY e.art ORDER BY e.art""")
    je_art = cur.fetchall()
    fehl = [f"{a}: {z} Zeilen, {d} Zellen, {fremd} fremd" for a, z, d, fremd, _ in je_art
            if z != n or d != n or fremd]
    cur.execute("SELECT art, gitter_id FROM auswertung.zelle_erreichbar WHERE methode = 'fussweg' AND meter IS NULL")
    ohne: dict[str, int] = {}
    for a, g in cur.fetchall():
        if g in bewohnt:
            ohne[a] = ohne.get(a, 0) + 1
    ok1 = bool(je_art) and not fehl and len(bewohnt) > 0
    erg.append(("K1 je Zelle und Art eine Fußweg-Zeile", ok1,
                f"{len(je_art)} Arten × {n} Zellen (davon {len(bewohnt)} bewohnt); "
                + ("; ".join(fehl) if fehl else "vollständig")
                + "; bewohnte Zellen ohne Wert: " + (", ".join(f"{a} {c}" for a, c in sorted(ohne.items()))
                                                    if ohne else "0")))

    # K2: Luftlinie unabhängig (Minimum ohne Index), Vergleich mit dem gespeicherten Fußweg
    cur.execute("""
      CREATE TEMP TABLE fw_luft ON COMMIT DROP AS
        SELECT e.gitter_id, e.art, e.meter::float8 AS fuss, min(ST_Distance(c.g, z.geom)) AS luft
        FROM auswertung.zelle_erreichbar e
        JOIN fw_zelle c USING (gitter_id)
        JOIN fw_ziel z ON z.art = e.art
        WHERE e.methode = 'fussweg' AND e.meter IS NOT NULL
        GROUP BY e.gitter_id, e.art, e.meter""")
    cur.execute("SELECT count(*), count(*) FILTER (WHERE fuss < luft) FROM fw_luft")
    verglichen, verstoesse = cur.fetchone()
    cur.execute("SELECT art, gitter_id, fuss, luft FROM fw_luft WHERE fuss < luft ORDER BY luft - fuss DESC LIMIT 5")
    bsp = cur.fetchall()
    erg.append(("K2 Fußweg ≥ Luftlinie (0 Verstöße)", verglichen > 0 and verstoesse == 0,
                f"{verglichen} Zellwerte verglichen, {verstoesse} Verstöße" + (f", z. B. {bsp}" if bsp else "")))

    cur.execute("""SELECT count(*), count(*) FILTER (WHERE f.meter < l.meter)
                   FROM auswertung.zelle_erreichbar f JOIN auswertung.zelle_erreichbar l
                     ON l.gitter_id = f.gitter_id AND l.art = f.art AND l.methode = 'luftlinie'
                   WHERE f.methode = 'fussweg' AND f.meter IS NOT NULL AND l.meter IS NOT NULL""")
    luft_n, luft_v = cur.fetchone()

    # K3
    cur.execute(f"""SELECT art, percentile_cont(0.5) WITHIN GROUP (ORDER BY fuss / luft), count(*)
                    FROM fw_luft WHERE luft >= {fw.MIN_LUFTLINIE_VERHAELTNIS_M} GROUP BY ROLLUP (art) ORDER BY art""")
    med = cur.fetchall()
    gesamt = next((m for a, m, _ in med if a is None), None)
    ok3 = gesamt is not None and 1.1 <= gesamt <= 1.6
    beleg3 = ("keine Werte" if gesamt is None else
              f"gesamt {gesamt:.3f}; je Art: " + ", ".join(f"{a} {m:.2f} (n={c})" for a, m, c in med if a))
    erg.append(("K3 Median Fußweg/Luftlinie zwischen 1,1 und 1,6", ok3, beleg3))

    # K4: strpos statt LIKE, damit % und _ im Vermerk nicht als Muster gelten
    zellteil = f"Zellen: {vermerk}"
    cur.execute("""SELECT count(*), count(*) FILTER (WHERE methode IS NULL OR methode = ''),
                          count(*) FILTER (WHERE methode = 'fussweg' AND quelle_lizenz NOT ILIKE '%%ODbL%%'),
                          count(*) FILTER (WHERE methode = 'fussweg' AND strpos(quelle_lizenz, %s) = 0)
                   FROM auswertung.zelle_erreichbar""", (zellteil,))
    z_all, z_ohne, z_odbl, z_zell = cur.fetchone()
    cur.execute("""SELECT count(*) FILTER (WHERE methode = 'fussweg'),
                          count(*) FILTER (WHERE methode = 'fussweg' AND quelle_lizenz NOT ILIKE '%%ODbL%%'),
                          count(*) FILTER (WHERE methode = 'fussweg' AND strpos(quelle_lizenz, %s) = 0)
                   FROM auswertung.zelle_gruen""", (zellteil,))
    g_fuss, g_odbl, g_zell = cur.fetchone()
    cur.execute("SELECT obj_description('auswertung.zelle_erreichbar'::regclass) ILIKE '%ODbL%'")
    kommentar = cur.fetchone()[0]
    erg.append(("K4 methode gesetzt, Fußweg-Zeilen tragen ODbL und den Zellvermerk",
                z_ohne == 0 and z_odbl == 0 and z_zell == 0 and g_odbl == 0 and g_zell == 0 and bool(kommentar),
                (f"zelle_erreichbar {z_all} Zeilen, ohne methode {z_ohne}, Fußweg ohne ODbL {z_odbl}, ohne Zellvermerk "
                 f"{z_zell}; zelle_gruen Fußweg {g_fuss} Zeilen, ohne ODbL {g_odbl}, ohne Zellvermerk {g_zell}; "
                 f"Tabellenkommentar nennt ODbL: {kommentar}")))

    # K5
    cur.execute("""SELECT count(*), count(*) FILTER (WHERE z.ziel_id IS NULL)
                   FROM auswertung.zelle_erreichbar e
                   LEFT JOIN fw_ziel z ON z.art = e.art AND z.ziel_id = e.ziel_id
                   WHERE e.methode = 'fussweg' AND e.ziel_id IS NOT NULL""")
    mit_ziel, fremd = cur.fetchone()
    erg.append(("K5 jedes Ziel einer Fußweg-Zeile steht im Zielbestand", mit_ziel > 0 and fremd == 0,
                f"{mit_ziel} Zeilen mit Ziel, davon nicht im Zielbestand: {fremd}"))

    cur.execute("""SELECT e.art, count(*) FROM auswertung.zelle_erreichbar e
                   JOIN fw_ziel z ON z.art = e.art AND z.ziel_id = e.ziel_id AND z.aussen
                   WHERE e.methode = 'fussweg' GROUP BY e.art ORDER BY e.art""")
    naechst = dict(cur.fetchall())
    erg.append(("Hinweis: Ziele außerhalb der Stadtgrenze (zählen mit)", True,
                "; ".join(f"{a} {au} von {g} Zielen außerhalb, nächstes Ziel außerhalb für {naechst.get(a, 0)} Zellen"
                          for a, (g, au) in sorted(ziele.items())) or "keine Ziele"))
    erg.append(("Hinweis: Vergleich mit Luftlinie-Zeilen", True,
                f"{luft_n} Paare, davon Fußweg < Luftlinie: {luft_v}" if luft_n else "noch keine Luftlinie-Zeilen"))
    return erg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--zellen", default=fw.ZELLEN_TABELLE, help="Zelltabelle schema.tabelle wie beim Rechnen")
    a = ap.parse_args()
    with fw.verbinden() as conn, conn.cursor() as cur:
        erg = pruefen(cur, a.zellen)
        conn.rollback()
    for k, ok, beleg in erg:
        print(f"[{'ok' if ok else 'FEHLT'}] {k}: {beleg}")
    return 0 if all(ok for _, ok, _ in erg) else 1


if __name__ == "__main__":
    sys.exit(main())
