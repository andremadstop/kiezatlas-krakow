# Beleg Einrichtungen

Erzeugt von `skripte/11_einrichtungen_krakow.py` (nicht von Hand ändern; `--pruefen` vergleicht byte-genau). Regeln vor dem Lauf: `pruefen/D6_protokoll.md`, Regeln 8–10. Eingaben und Prüfsummen: `belege/rohdaten-D6-2026-11-13.sha256`.

## Schritt 1: BDOT10k-Komplexe

| Ebene | RODZAJ | Sätze | übernommen als | weg (KAT_ISTNIE) |
|---|---|---|---|---|
| `OT_KUOS_A` | szkoła lub zespół szkół | 170 | `szkola` | 0 |
| `OT_KUOS_A` | szkoła wyższa | 39 | nicht übernommen | 0 |
| `OT_KUOS_A` | przedszkole | 35 | `przedszkole` | 0 |
| `OT_KUOS_A` | ośrodek naukowo-badawczy | 17 | nicht übernommen | 0 |
| `OT_KUOZ_A` | zespół szpitalny lub sanatoryjny | 24 | `szpital` | 0 |
| `OT_KUOZ_A` | zakład opieki socjalnej lub dom dziecka | 10 | nicht übernommen | 0 |
| `OT_KUOZ_A` | żłobek | 2 | `zlobek` | 0 |
| `OT_KUSK_A` | park lub skwer | 90 | `park` | 0 |
| `OT_KUSK_A` | kompleks sportowo-rekreacyjny | 47 | nicht übernommen | 0 |
| `OT_KUSK_A` | ogród botaniczny | 1 | nicht übernommen | 0 |
| `OT_KUSK_A` | ogród zoologiczny | 1 | nicht übernommen | 0 |

- übernommen: 321, davon außerhalb der Gemeindegrenze (Punkt in der Fläche): 0
- mit Name (NAZWA): 309

## Schritt 2: RSPO (Schulregister)

- Datei `$KIEZ_DATEN/eingang/rspo_krakow.csv` fehlt (Handdownload ausstehend): kein RSPO-Teil.

## Schritt 3: Ärzte und Apotheken aus OSM (nur `daten/einrichtungen_odbl.js`)

- aus `auswertung.osm_poi`: 604 (apotheke 321, arzt 283)

## Ergebnis `daten/einrichtungen.js`

| art | Einrichtungen |
|---|---|
| `park` | 90 |
| `przedszkole` | 35 |
| `szkola` | 170 |
| `szpital` | 24 |
| `zlobek` | 2 |
| zusammen | 321 |

## Grenzen

- BDOT10k erfasst Komplexe (Flächen mit eigener Abgrenzung), kein Register: Schulen und Kindergärten ohne eigene Fläche fehlen. Vollständigkeit gegen RSPO oder eine städtische Liste: nicht geprüft.
- `szkola` umfasst Grund- und weiterführende Schulen (BDOT10k trennt sie nicht); Schulbezirke (obwody) fehlen.
- Keine Plätze, keine Schülerzahlen, keine Öffnungs- oder Trägerangaben.
- `szpital` umfasst laut BDOT10k-Wert auch Sanatorien; ambulante Ärzte nur über OSM (derzeit Beispieldaten).
- Aktualität: Stand der BDOT10k-Lieferung für Powiat 1261 laut Datei, nicht gegen die Wirklichkeit geprüft.
