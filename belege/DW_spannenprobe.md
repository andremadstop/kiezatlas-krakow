# Beleg Wohnungsmarkt: unabhängige Spannenprobe (KR55), 14.11.2026

Frage: Wie viele unterdrückte Fallzahlen (`grund: n_unter_minimum`) in `daten/mieszkania_odbl.js` haben im ganzen
veröffentlichten Gleichungssystem höchstens zwei mögliche ganzzahlige Werte? Regel: `pruefen/DW_protokoll.md`,
Änderung KR55. Der Erzeuger rechnet dieselbe Zahl selbst (`belege/DW_mieszkania.md`, „Spannenprobe“); diese
Rechnung ist davon unabhängig: eigener Aufbau des Systems aus der veröffentlichten Datei, nichts aus
`skripte/40_mieszkania.py` importiert, gerechnet außerhalb des Repos (Skript unten wörtlich).

## Ergebnis

| Stand der Datei | primär unterdrückt | Spanne 1 Wert | Spanne 2 Werte | Spanne ≥ 3 Werte | betroffene Jahre |
|---|---|---|---|---|---|
| vor KR55 (Commit `138c319`, Summe über die Jahre gegen F10) | 74 | 0 | 42 | 32 | 1900, 1901, 2006, 2007, 2009, 2012, 2016, 2018 |
| nach KR55 (Commit `1cd6fe5`, Summe gegen F11) | 32 | 0 | 0 | 32 | – |

**Nach KR55 hat keine unterdrückte Fallzahl eine Spanne von höchstens zwei Werten (0 von 32).** Die Zahl stimmt mit
der des Erzeugers überein. Werte je Feld nennt weder die Rechnung noch dieser Beleg.

## Verfahren

Unbekannte: jede nicht veröffentlichte Fallzahl je Ort (Stadt, dzielnica), Jahr und Markt, dazu je Ort und Jahr die
nie veröffentlichte Zahl ohne Marktangabe (`rest`). Gleichungen: Stadt = Summe der dzielnice je Jahr und Markt
(auch `rest`); `ogolem` = `pierwotny` + `wtorny` + `rest` je Ort und Jahr; Summe `ogolem` der Stadt über die Jahre
= letzte Zählung (F11, vor KR55 F10); Summe `rest` = `kontrolle.ohne_markt`. Schranken: veröffentlichte Zahl fest,
unterdrückt 1 bis Mindestzahl − 1, verdeckt mindestens Mindestzahl, `rest` ≥ 0, alle ganzzahlig. Je unterdrücktem
Feld Minimum und Maximum mit `scipy.optimize.milp` (HiGHS); Zahl der Werte = Maximum − Minimum + 1.

Aufruf: `uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt python -I spanne.py daten/mieszkania_odbl.js`

```python
import json, re, sys
from collections import Counter
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

pfad = sys.argv[1]
t = open(pfad, encoding="utf-8").read()
m = re.search(r"window\.\w+\s*=\s*", t)
o = json.loads(t[m.end():].rstrip().rstrip(";"))
mind = o["regeln"]["mindestfallzahl"]
jahre = [str(j) for j in o["jahre"]]
dz = sorted(o["stadtteile"])
orte = ["stadt", *dz]
M = ("ogolem", "pierwotny", "wtorny", "rest")
idx = {}
for ort in orte:
    for j in jahre:
        for mk in M:
            idx[(ort, j, mk)] = len(idx)
A, b = [], []

def gl(terme, w):
    z = np.zeros(len(idx))
    for k, c in terme:
        z[idx[k]] += c
    A.append(z)
    b.append(w)

for j in jahre:
    for mk in M:
        gl([(("stadt", j, mk), 1)] + [((d, j, mk), -1) for d in dz], 0)
    for ort in orte:
        gl([((ort, j, "ogolem"), 1), ((ort, j, "pierwotny"), -1), ((ort, j, "wtorny"), -1), ((ort, j, "rest"), -1)], 0)
schritte = {s["nr"]: s["n"] for s in o["kontrolle"]["schritte"]}
letzte = "F11" if "F11" in schritte else "F10"
gl([(("stadt", j, "ogolem"), 1) for j in jahre], schritte[letzte])
gl([((d, j, "rest"), 1) for d in dz for j in jahre], o["kontrolle"]["ohne_markt"])
lo = np.zeros(len(idx))
hi = np.full(len(idx), np.inf)
ziele = []
for (ort, j, mk), i in idx.items():
    if mk == "rest":
        continue
    w = (o["stadt"] if ort == "stadt" else o["stadtteile"][ort])[j][mk]
    if w.get("n") is not None:
        lo[i] = hi[i] = w["n"]
    elif w.get("grund") == "n_unter_minimum":
        lo[i], hi[i] = 1, mind - 1
        ziele.append((ort, j, mk))
    else:
        lo[i] = mind
A = np.array(A)
b = np.array(b, dtype=float)
breite = Counter()
jahre_eng = Counter()
for k in ziele:
    erg = []
    for v in (1, -1):
        c = np.zeros(len(idx))
        c[idx[k]] = v
        r = milp(c, constraints=LinearConstraint(A, b, b), bounds=Bounds(lo, hi), integrality=np.ones(len(idx)))
        assert r.status == 0, r.message
        erg.append(round(v * r.fun))
    n_werte = erg[1] - erg[0] + 1
    breite[min(n_werte, 3)] += 1
    if n_werte <= 2:
        jahre_eng[k[1]] += 1
print(f"Datei: {pfad}; Summe über die Jahre gegen {letzte}")
print(f"primär unterdrückte Zellen: {len(ziele)}")
print(f"  mit 1 möglichen Wert: {breite[1]}; mit 2: {breite[2]}; mit 3 oder mehr: {breite[3]}")
print(f"  Spanne höchstens 2 Werte: {breite[1] + breite[2]}; betroffene Jahre: {sorted(jahre_eng)}")
```

Ausgabe nach KR55 (wörtlich):

```
Datei: daten/mieszkania_odbl.js; Summe über die Jahre gegen F11
primär unterdrückte Zellen: 32
  mit 1 möglichen Wert: 0; mit 2: 0; mit 3 oder mehr: 32
  Spanne höchstens 2 Werte: 0; betroffene Jahre: []
```
