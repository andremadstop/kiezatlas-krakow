# Run it yourself

Guide for a team that wants to run and develop Kiezatlas Kraków on its own server, from an empty machine to the
finished pages. Polish version (leading): [`uruchomienie.md`](uruchomienie.md). New city: [`new-city.md`](new-city.md).
Taking over the project: [`przekazanie.md`](przekazanie.md).

As of 14 November 2026. All times and sizes below were measured (source in each table); anything not measured says
“not measured”. Commands and file names are as in the repository; script messages are in German because that is the
language the code was written in.

> **Only the raw-data snapshot is still missing (as of 15 November 2026).** The repositories are public
> (Apache-2.0): this repository <https://github.com/andremadstop/kiezatlas-krakow> (`git clone` in section 2), the Geodaten-Import-Pipeline <https://github.com/andremadstop/geodaten-import-pipeline>
> (database steps, section 3) and Kiezatlas Potsdam <https://github.com/andremadstop/kiezatlas-potsdam> (optional, comparison only). The raw-data snapshot
> (way C) has no Zenodo record and no DOI yet; until then, ask the publisher for it at the address in
> `config/krakow.yaml`, key `meldeweg`. Without the snapshot, fetch the sources by ways A and B.

## In short

```sh
./atlas.sh trocken --ohne-datenbank   # checks tools and every input file of the steps without database; writes nothing
./atlas.sh alles --ohne-datenbank     # without database: compute, downloads, pages and all checks (./pruefen.sh)
./atlas.sh liste                      # the 25 steps
# with the database (set up section 3 first: .env, Docker, Geodaten-Import-Pipeline):
./atlas.sh trocken                    # also checks the database
./atlas.sh alles                      # whole chain including the database steps
```

Without `--ohne-datenbank` both commands stop at once when `.env`, Docker or the database are missing
(`Umgebungsdatei … fehlt`, `docker nicht gefunden`); the results of the database steps under `daten/` stay as they
are in the repository.

`./atlas.sh trocken` exits 0 when every required input is present and 2 with a list when something is missing. A
missing manual download that a step can cope with (air quality, housing market, monument registers, statistical
areas) is only a notice: the affected file stays sample data (`fixture: true`) and the pages say so.
`./atlas.sh alles` stops at the first failing step and tells you where to resume (`./atlas.sh alles --ab <step>`).
Every run is logged to `berichte/kette/<UTC time>.log`.

## 1. Requirements

| Tool | Version (tested) | Used for |
|---|---|---|
| Linux x86_64, `sh`, `git`, `tar`, `sha256sum` | – | everything |
| system Python 3.11 or newer | – | the chain itself, `skripte/kette.py` and `skripte/schnappschuss.py` (standard library only) |
| uv | 0.11.3 | Python 3.13 and the packages in `requirements*.txt` (hash-pinned); always `--offline` inside the chain |
| Node.js | 22 (last v22.23.4) | browser checks, `node --check` |
| npm, packages from `package-lock.json` | Playwright 1.64.1, axe-core 4.14.0 | browser checks (Chromium) |
| Docker with `docker compose` | – | PostGIS `postgis/postgis:16-3.6` (digest in `docker-compose.yml`), only for computing |
| Poppler `pdftotext` | 26.10.0 | ZBK building list (renovation atlas) |
| Noto Sans font (Regular, Medium, Italic) | in the repository under `schriften/noto/` (SIL OFL 1.1, licence next to the files; byte-identical to the Arch package `noto-fonts 1:2026.10.01-1`), nothing to install | labels on the base map; `skripte/27_grundkarte.py` checks the SHA256 of each file |
| Geodaten-Import-Pipeline repository (<https://github.com/andremadstop/geodaten-import-pipeline>) | commit `12bae5bc96cf34355c8c5a723eb444e66f776f2d` (Apache-2.0) | the database steps of `skripte/lauf.sh` (`einrichten`: roles and grants; also `laden`, `auswerten`, `rechte`) |
| Kiezatlas Potsdam repository (<https://github.com/andremadstop/kiezatlas-potsdam>, optional) | – (Apache-2.0) | only the Kraków–Potsdam comparison (`skripte/41_porownanie.py`) and the Potsdam cross-check (which also needs GSAP 3.15.1 in `vendor/`, not included in the repository; see `NOTICE`) |

**Where to get the two other repositories:** both are public on GitHub under Apache-2.0 (checked 15 November
2026). Geodaten-Import-Pipeline: <https://github.com/andremadstop/geodaten-import-pipeline>, at commit `12bae5bc96cf34355c8c5a723eb444e66f776f2d` (this state also has the
DOI [10.5281/zenodo.24073612](https://doi.org/10.5281/zenodo.24073612)); next to this repository as
`../geodaten-import-pipeline` (other path: variable `PIPELINE_DIR`), commands in section 3. At any other commit
`skripte/lauf.sh` stops. Kiezatlas Potsdam: <https://github.com/andremadstop/kiezatlas-potsdam>, next to it as `../kiezatlas-potsdam` (other path:
`KIEZ_POTSDAM`). Without the pipeline the database cannot be set up; the files that need it (walking routes,
`erreichbar_fuss_odbl.js`, `planer_fuss_odbl.js`) then stay as they are in the repository.

### Disk space (measured 14 November 2026)

| What | Size | Measured with |
|---|---|---|
| Repository (files in git) | 26.5 MB | `git ls-files` and `du -cb` |
| Raw data `$KIEZ_DATEN` after all runs | 672 MB, of which 70 MB derived data (`abgeleitet/`) and 194 MB a second copy of the OSM extract (`osm/`) | `du -sh` |
| Raw-data snapshot (tar archive) | about 404 MB (content 404,127,036 B, dry run 15 Nov 2026) | `skripte/schnappschuss.py`, below |
| Docker image PostGIS | 950,576,003 B | `docker image inspect` |
| Database volume after a full run | 469.1 MB | `docker system df -v` |
| `node_modules` | 81 MB | `du -shL` |
| Chromium for Playwright (browser, headless shell, ffmpeg) | 681 MB | `du -shc` in `~/.cache/ms-playwright` |
| uv cache | not measured separately | |

Sum of the table (without the uv cache): about 3.3 GB. Memory: the heaviest measured step (renovation atlas) used
938 MB (time table below); limit long runs, e.g.
`KETTE_PRAEFIX="systemd-run --user --scope -p MemoryMax=8G" ./atlas.sh alles`.

## 2. Code and environment

```sh
# tools (as in .github/workflows/pruefen.yml): uv 0.11.3, Python managed by uv, Node.js 22
pipx install uv==0.11.3
export UV_PYTHON_PREFERENCE=only-managed     # uv’s own Python, never a system Python
uv python install 3.13.12                    # the version in the evidence files of 14 Nov 2026
node --version                               # v22.x (from your distribution or nodejs.org)
git clone https://github.com/andremadstop/kiezatlas-krakow kiezatlas-krakow
cd kiezatlas-krakow
export KIEZ_DATEN="$(cd .. && pwd)/kiezatlas-daten/krakow"; mkdir -p "$KIEZ_DATEN"
# once, with network: the packages into the uv cache
uv run --python 3.13 --no-project --with-requirements requirements.txt python -c pass
uv run --python 3.13 --no-project --with-requirements requirements.txt --with-requirements requirements-pruefen.txt python -c pass
uv run --python 3.13 --no-project --with-requirements requirements.txt --with-requirements requirements-schriften.txt python -c pass
npm ci                                         # packages from package-lock.json
npx playwright install --with-deps chromium    # browser checks; also installs system libraries (needs sudo/root)
```

**All following commands assume `KIEZ_DATEN` and `UV_PYTHON_PREFERENCE` are set** (best in your shell profile). The
scripts fall back to `../kiezatlas-daten/krakow` on their own, but the shell commands in section 4 use
`"$KIEZ_DATEN/…"` directly; with the variable empty they would write to `/2026-11-13/…`. Without
`UV_PYTHON_PREFERENCE=only-managed` uv may pick any system Python 3.13 with another patch version, and that version
then appears in the evidence files (e.g. `belege/DS_sanierung_lauf.md`); the same holds for the Poppler version of
your distribution (tested: 26.10.0). Without root, `npx playwright install chromium` alone fetches only the browser;
the system libraries it needs (e.g. `libglib-2.0.so.0`) must then come from the administrator. After that the chain
needs no network.

## 3. Database (only for computing)

The pages are static; PostGIS is needed only by the steps marked `[Datenbank]` (boundaries and cells, OSM walking
network, walking distances).

```sh
cp .env.beispiel .env && chmod 600 .env    # a long random password per role, e.g.:
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
docker compose up -d --wait db             # 127.0.0.1 only, port 55462
git clone https://github.com/andremadstop/geodaten-import-pipeline ../geodaten-import-pipeline
git -C ../geodaten-import-pipeline checkout 12bae5bc96cf34355c8c5a723eb444e66f776f2d   # pinned commit
skripte/lauf.sh einrichten                 # roles and grants; needs ../geodaten-import-pipeline at the pinned commit
skripte/lauf.sh rechte                     # checks the grants, changes nothing
```

Without a database: `./atlas.sh alles --ohne-datenbank` computes everything else; the walking-distance files under
`daten/` stay as they are in the repository.

## 4. Sources: three ways

Each source has its licence, verbatim notice and way in [`QUELLEN.md`](../QUELLEN.md). Files live under `$KIEZ_DATEN`
at the paths the scripts expect (the paths depend on the city, see [`new-city.md`](new-city.md)).

### Way A: automatic, through `skripte/abruf.py`

The project's only network path: block list, robots.txt, minimum interval per host and a log in
`$KIEZ_DATEN/abrufprotokoll.tsv`. BDOT10k, Eurostat grids, NSP 2021, GTFS, ZBK list, two BIP pages, Fontsource
packages and their registry entries (same commands as in [`uruchomienie.md`](uruchomienie.md), section 4, way A):

```sh
P="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt python -I"
# Dated folders the chain reads today (places in the code: rundgang.md, “Neuer Datenstand”).
# New state: set the download date, e.g. STAND=$(date +%F), and switch those places.
STAND=2026-11-13
STAND_VERGLEICH=2026-11-14
$P skripte/abruf.py --abstand 30 https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/12/1261_SHP.zip "$KIEZ_DATEN/$STAND/03_gebaeude/1261_SHP.zip"
$P skripte/abruf.py --abstand 30 https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/PL_PD_3035_GPKG.zip "$KIEZ_DATEN/$STAND/02_zensus/PL_PD_3035_GPKG.zip"
$P skripte/abruf.py --abstand 30 https://stat.gov.pl/download/gfx/portalinformacyjny/pl/defaultaktualnosci/6536/12/1/1/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx "$KIEZ_DATEN/$STAND/02_zensus/ludnosc_w_rejonach_statystycznych_i_obwodach_spisowych_nsp_2021.xlsx"
for f in A T M; do $P skripte/abruf.py --abstand 30 https://gtfs.ztp.krakow.pl/GTFS_KRK_$f.zip "$KIEZ_DATEN/$STAND/06_oepnv/GTFS_KRK_$f.zip"; done
$P skripte/abruf.py --abstand 30 "https://www.bip.krakow.pl/plik.php?zid=635620&wer=1&new=t&mode=shw" "$KIEZ_DATEN/zbk/$STAND/zbk_wykaz_2025-12.pdf"
$P skripte/abruf.py --abstand 30 "https://www.bip.krakow.pl/?dok_id=48482" "$KIEZ_DATEN/zbk/$STAND/bip_dok48482_ponowne.html"
$P skripte/abruf.py --abstand 30 "https://www.bip.krakow.pl/?dok_id=242410" "$KIEZ_DATEN/$STAND/10_statistik/bip_dok242410_mieszkancy_dzielnice_2025.html"
$P skripte/abruf.py --abstand 30 https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/DE_PD_3035_GPKG.zip "$KIEZ_DATEN/$STAND_VERGLEICH/41_vergleich/DE_PD_3035_GPKG.zip"
$P skripte/abruf.py --abstand 30 https://registry.npmjs.org/@fontsource/barlow/-/barlow-5.3.0.tgz "$KIEZ_DATEN/schriften/$STAND/barlow-5.3.0.tgz"
$P skripte/abruf.py --abstand 30 https://registry.npmjs.org/@fontsource/barlow-semi-condensed/-/barlow-semi-condensed-5.3.0.tgz "$KIEZ_DATEN/schriften/$STAND/barlow-semi-condensed-5.3.0.tgz"
$P skripte/abruf.py --abstand 30 https://registry.npmjs.org/@fontsource%2fbarlow/5.3.0 "$KIEZ_DATEN/schriften/$STAND/npm-barlow-latest.json"
$P skripte/abruf.py --abstand 30 https://registry.npmjs.org/@fontsource%2fbarlow-semi-condensed/5.3.0 "$KIEZ_DATEN/schriften/$STAND/npm-barlow-semi-condensed-latest.json"
```

The addresses always return the newest state of a source. When a source has changed (BDOT10k, GTFS every week), the
checksums in `belege/rohdaten*.sha256` no longer match and `skripte/27_grundkarte.py` aborts (it pins the SHA256 of
BDOT10k). Then follow “Neuer Datenstand” in [`rundgang.md`](rundgang.md) (new dated folder, new checksum list, new
run). To reproduce the state of 14 November 2026 exactly, use way C. The font registry entries in the chain are the
`…/latest` files of 13 November 2026 (version 5.3.0 at the time); the versioned address `…/5.3.0` returns the same
bytes (checked on 14 November 2026 through `skripte/abruf.py`, `belege/fix-offen_npm_versioniert.log`: SHA256 `534c5006…` and `96a07a94…`, as in
`belege/rohdaten-DF-schriften.sha256`), so saving it as `*-latest.json` passes the checksum check. The BIP page
`bip_dok242410_…` (no licence statement, not in the snapshot) is only a cross-check of the city area; without it
`skripte/35_klimat.py` computes the same data and notes in its evidence file that the cross-check was skipped.

### Way B: by hand into `eingang/`, with `HERKUNFT.md`

Sources that may not or cannot be downloaded automatically are saved from a browser into `$KIEZ_DATEN/eingang/`.
Each file gets a line in `$KIEZ_DATEN/eingang/HERKUNFT.md` (file, address, licence with where it is stated, download
date `DD.MM.YYYY` in the last column) and a checksum in `eingang/SHA256SUMS` (`sha256sum FILE >> SHA256SUMS`).

| File in `eingang/` | Source | Without it |
|---|---|---|
| `*.osm.pbf` | OpenStreetMap extract for Małopolska (Geofabrik `malopolskie`), ODbL 1.0 | no district boundaries; stop (steps `osm`, `sanierung`) |
| `lod2_1261_gml.zip` | GUGiK, Modele 3D budynków LoD2, powiat 1261 | stop in `sanierung`; in `gebaeude` heights only from the storey count |
| `eea/*.geojson.zip` (as downloaded on 14 Nov 2026; `*.geojson` or `*.csv` also work) | EEA “Air quality annual statistics” (instructions in `quellen-D7.md`) | `powietrze.js` stays sample data |
| `rcn/*.gpkg` | Rejestr cen nieruchomości, powiat 1261 (instructions in `quellen-DW.md`) | step `wohnungsmarkt` skipped, `mieszkania_odbl.js` stays sample data |
| `wikidata_zabytki_krakow.json`, `nid_rejestr_zabytkow.csv`, `gez_krakow.csv` | Wikidata, NID register, gminna ewidencja zabytków (query and format in `quellen-DZ.md`) | `denkmale.js` stays sample data |
| `rejony_statystyczne.*` | GUS statistical-area geometry (no 2021 edition found) | NSP values per district stay `null` |

The `osm` step (with `--uebernehmen`) copies the OSM extract to `$KIEZ_DATEN/osm/<state>/` with its checksum.

### Way C: raw-data snapshot

`skripte/schnappschuss.py` packs only the raw data that may be redistributed (BDOT10k, LoD2, OSM, Eurostat grids,
NSP 2021, GTFS, EEA air quality extract, Wikidata query result, Barlow font packages, Noto Sans map font), with `SCHNAPPSCHUSS/SHA256SUMS`, `LIZENZEN.md` (source,
licence, verbatim notice) and `AUSGESCHLOSSEN.md` (every left-out file with reason and checksum). The archive is
byte-for-byte reproducible.

```sh
./atlas.sh schnappschuss --ziel /path/outside/the/repository     # writes the archive (content 15 Nov 2026: 404,127,036 B)
python3 -I skripte/schnappschuss.py --pruefen ARCHIVE.tar          # checks the archive against its SHA256SUMS
mkdir -p "$KIEZ_DATEN" && tar -xf ARCHIVE.tar -C "$KIEZ_DATEN"     # unpack into an empty folder
```

Left out (reason in `AUSGESCHLOSSEN.md`): the RCN transaction file (single transactions with place, date and price;
fetch it by hand as in `quellen-DW.md`), the ZBK list (personal data in the PDF metadata and private ownership
shares), the BIP page with the city area (no licence), the npm registry entries (maintainers’ e-mail addresses),
web pages and legal texts kept as evidence, MSIP boundaries (no licence for redistribution). The chain needs five of them: fetch
the ZBK list, the BIP page with the reuse rules, the BIP page with the city area and both npm entries by way A after
unpacking; `./atlas.sh trocken` lists them. Checked on
14 November 2026 against the unpacked snapshot plus these five files: `./atlas.sh trocken --ohne-datenbank` green;
`02_bevoelkerung.py`, `20_bdot10k.py`, `dz_denkmale.py`, `13_oepnv_krakow.py`, `15_planer_krakow.py`,
`35_klimat.py`, `36_sanierung.py`, `41_porownanie.py` and `skripte/schriften.py` with `--pruefen` reproduce the
repository files; `27_grundkarte.py` with the snapshot font (`--schrift-ordner`) gives the same `MANIFEST.sha256`.
The EEA extract and the Wikidata result are in the snapshot since 15 November 2026; `32_powietrze.py` and
`dz_denkmale.py` have not yet been run against an unpacked snapshot that contains them.

**Reproducibility is proven only on the publisher’s machine.** In a fresh Debian container (14 November 2026, same
hash-pinned wheels, Python 3.13.12 managed by uv) `02_bevoelkerung.py --pruefen` reported `daten/stadtteile_odbl.js`
as different: boundary coordinates differed in the 5th decimal place (e.g. 19.98267 → 19.98268), and with them the
files derived from the boundaries (e.g. Prądnik Czerwony 643.6 → 643.7 ha in `belege/dk_klimat.md`, the climate,
building and housing files per district, the downloads). The 3D files and their manifest were byte-identical. The
cause has not been narrowed down (suspected, not tested: a different system maths library). In another environment
expect such differences in the last decimal place; a reference image (Dockerfile with a pinned base) in which
reproducibility is proven is still open.

## 5. Running the chain

```sh
./atlas.sh trocken
./atlas.sh alles                 # browser checks at the end
./atlas.sh alles --ohne-browser  # checks without a browser
```

The order is the one in [`rundgang.md`](rundgang.md) (“Schritte”): data packages, then comparison, downloads, long
texts and finally the pages (`skripte/30_seiten.py`); otherwise downloads and texts silently go stale. 3D building
files go to a new dated folder `$KIEZ_DATEN/abgeleitet/gebaeude/<date>-odbl/`, base-map tiles to
`$KIEZ_DATEN/abgeleitet/grundkarte/<start of the BDOT10k SHA256>/`.

The step writes the manifest `MANIFEST.sha256` next to the files (the folder of 13 November 2026 carries the same list as `SHA256SUMS`). The development server and `skripte/deploy_kopie.py`
take the folder named in `config/gebaeude_3d.json` (currently `2026-11-13-odbl/`); if it has no manifest, they take
the newest `*-odbl/` folder with one. Another folder: `--gebaeude <folder>` for both, e.g.
`node skripte/entwicklung_server.mjs --gebaeude "$KIEZ_DATEN/abgeleitet/gebaeude/<date>-odbl"`. The deploy copy
accepts only a manifest with the checksum in `config/gebaeude_3d.json`; a byte-identical rerun gives exactly that.
Check without writing: `python -I skripte/20_bdot10k.py --pruefen --geometrie <folder>`.

Local preview with base map: `node skripte/entwicklung_server.mjs --port 8080` (127.0.0.1 only). Any static web server
can publish the pages; they call no third-party services at run time. What has to be copied next to the pages (map
tiles, 3D files) is described in `skripte/deploy_kopie.py` and `docs/auslieferung.md` (written for the publisher’s
current server; replace the target with your own).

**Expected end after way C:** `./atlas.sh alles` stops in its last step with

```
HALT: Schritt pruefen mit Rückgabe 1 nach … s; volle Ausgabe im Protokoll berichte/kette/. Weiter nach der Behebung mit: ./atlas.sh alles --ab pruefen
```

and exit code 3. All steps before it have run and the pages are written. The cause is the checksum lists in
`belege/rohdaten*.sha256` that name raw files the snapshot leaves out (`AUSGESCHLOSSEN.md` in the archive); in a run
of 14 November 2026 these were six lists (D5, D6, D7, DE, DS, DW). Check in the log under `berichte/kette/` that the
findings are only those lists; any other finding has to be fixed first. Exception outside the publisher’s machine:
checks that recompute the boundaries or files derived from them (e.g. `02_bevoelkerung.py --pruefen`) may report
differences in the 5th decimal place of coordinates (section 4, way C); `git diff` shows whether only such last
digits moved. The files missing from the snapshot come by way A or B; after that run `./atlas.sh alles --ab pruefen`
(that this then ends green has not been tested).

Security headers (suggestion): the pages load everything from your own server, so a narrow Content-Security-Policy
works, for example in nginx:

```nginx
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'sha256-…'; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none'" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

The only inline script is the line `window.KIEZ_V="…"` inserted by `skripte/deploy_kopie.py`; its hash
(`'sha256-…'`) changes with every copy and `deploy_kopie.py` prints it, so renew it with every upload. MapLibre needs
`worker-src blob:`, map pop-ups set colours through a `style` attribute. Reasons and what was tested:
`docs/auslieferung.md`, section “Sicherheits-Header”.

## 6. Time (measured)

Measuring machine: x86_64, 8 cores / 16 threads, 62 GB RAM. Each computing step was timed in its `--pruefen` mode
(computes everything, compares byte for byte, writes nothing) on 14 November 2026; RAM = peak resident memory.

| Step | Time | RAM | Source |
|---|---|---|---|
| `bevoelkerung` (`02_bevoelkerung.py`) | 88.3 s | 473 MB | measured 14 Nov 2026 |
| `gebaeude` (`20_bdot10k.py`) | 46.8 s | 689 MB | measured 14 Nov 2026 |
| `grundkarte` (`27_grundkarte.py`) | 23.6 s | 490 MB | measured 14 Nov 2026; first run 24.0 s (`belege/D8_grundkarte.md`) |
| `klima` (`35_klimat.py`) | 9.7 s | 166 MB | measured 14 Nov 2026 |
| `sanierung` (`36_sanierung.py`) | 194.2 s | 938 MB | measured 14 Nov 2026 |
| `denkmale` (`dz_denkmale.py`) | 46.4 s | 573 MB | measured 14 Nov 2026 |
| `oepnv` (`13_oepnv_krakow.py`) | 12.4 s | 180 MB | measured 14 Nov 2026 |
| `planer` (`15_planer_krakow.py`) | 0.5 s | 105 MB | measured 14 Nov 2026 |
| `fussweg` (`14b_fussweg.sh rechnen`) | 14.8 s | not measured | run report of 13 Nov 2026 (`belege/DE_fussweg.md`) |
| `osm`, `db_gliederung`, `einrichtungen`, `ziele_db`, `fussweg_export` | not measured | not measured | |
| `./pruefen.sh --voll` with browser | sum of step times 1,039 s (about 17 min) | – | `belege/pruefstand-20261114-5f5bf50/pruefen.log` |
| `./atlas.sh alles --ohne-datenbank` up to the step `pruefen` | sum of step times 1,123 s (about 19 min) | – | fresh Debian container, 16 threads, 14 Nov 2026 (`bevoelkerung` 243 s, `sanierung` 298 s, `denkmale` 160 s); `pruefen` itself not counted (browser libraries were missing) |
| `./pruefen.sh` with browser (without `--voll`) | 939 s (about 16 min) | – | publisher’s machine, 16 threads, 15 Nov 2026; count 60 checks, 53 green, 0 findings, 7 skipped |
| `./atlas.sh trocken` | 0.3 s | – | measured 14 Nov 2026 |
| snapshot (`schnappschuss.py`, 403 MB) | 3.5 s | – | measured 14 Nov 2026 |

## 7. Errors and fixes

The messages are verbatim (system tools with `LC_ALL=C.UTF-8`); the full table with all messages is in
[`uruchomienie.md`](uruchomienie.md), section 7.

| Message | Cause | Fix |
|---|---|---|
| `error: No interpreter found for Python 3.13 …` / `… but uv is set to offline mode` | empty uv cache | section 2 (once, with network) |
| `× No solution found when resolving --with dependencies:` … `Because certifi was not found in the cache` | packages from `requirements.txt` not cached | section 2 |
| `Umgebungsdatei … fehlt (Vorlage .env.beispiel, chmod 600)` | no `.env` | section 3 |
| `Container kiezatlas-krakow-db-1 läuft nicht oder ist nicht gesund …` | database not running | `docker compose up -d --wait db`, then once `skripte/lauf.sh einrichten` |
| `Pipeline weicht vom festgeschriebenen Stand ab (…). Abbruch; …` | pipeline repository at another commit | check out commit `12bae5bc96cf34355c8c5a723eb444e66f776f2d` |
| `…/1261_SHP.zip: SHA256 … statt 68b6ff47… (Regel G1) …` | newer BDOT10k | way C, or “Neuer Datenstand” |
| `…: SHA256 …, erwartet … (andere Schriftdatei)` | `--schrift-ordner` points to another Noto Sans version | leave out `--schrift-ordner`: the default is `schriften/noto/` in the repository (the chain uses it automatically) |
| `FileNotFoundError: … bip_dok242410_mieszkancy_dzielnice_2025.html` | BIP page not in the snapshot | fetch by way A |
| `sha256sum: zbk/2026-11-13/bip_32.html: No such file or directory` / `FAILED open or read` | checksum lists in `belege/` also name evidence files outside the snapshot | expected after way C; list in `SCHNAPPSCHUSS/AUSGESCHLOSSEN.md` |
| `chrome-headless-shell: error while loading shared libraries: libglib-2.0.so.0: cannot open shared object file` | Chromium installed without its system libraries | `npx playwright install-deps chromium` as root (or `--with-deps` in section 2) |
| `HALT: Schritt <step> mit Rückgabe <n> …` | a step failed | log in `berichte/kette/`, then `./atlas.sh alles --ab <step>` |

## 8. Checks

`./pruefen.sh` runs every check without network and database (time in section 6);
`./pruefen.sh --voll` also recomputes the data packages from the raw data. Without raw data (empty `$KIEZ_DATEN`)
`./pruefen.sh` reports the checksum lists as findings (after way C only the lists of the excluded files, see section 5). Air and housing market (`pruefen/D7_powietrze.py`, `pruefen/DW_mieszkania.py`) then check only the files in the
repository (`--ohne-lauf`); their recomputation from the raw data counts as skipped, not as a finding. For that case `.github/workflows/pruefen.yml` runs the checks
that need no raw data, no database and no browser. Before publishing: `./atlas.sh oeffentlich` (personal paths,
e-mail addresses, host names, secrets, large files, licences) and `./atlas.sh oeffentlich --historie` (whole git
history).
