# Auslieferung: vom Repo nach souverain-systems.de/kiezatlas/krakow/

Stand 15.11.2026 (Version 1.0.0). Ziel ist `https://souverain-systems.de/kiezatlas/krakow/` auf dem Webserver der
Herausgeberin, Ordner
`/opt/www/souverain-systems.de/kiezatlas/krakow/`. Polnisch liegt in der Wurzel, Englisch und Deutsch in `en/` und
`de/` (`config/krakow.yaml`: `sprachen`, `basis_url`). Die Deploy-Kopie, ihre Prüfung und dieser Text gehören zum
Paket Deploy. Hochladen, nginx und die Rechtstexte sind Andres Schritte.

## Kurz

```sh
npm ci --offline --ignore-scripts          # einmal je Checkout: esbuild 0.25.12 und die Prüfwerkzeuge aus package-lock.json
PY="uv run -q --offline --python 3.13 --no-project --with-requirements requirements.txt python -I"
$PY skripte/deploy_kopie.py                # → ../kiezatlas-deploy/krakow/<heute>/
node skripte/deploy_pruefen.mjs --kopie ../kiezatlas-deploy/krakow/<heute>
```

Ab Version 1.0.0 entsteht die Deploy-Kopie aus dem veröffentlichten Stand (dem öffentlichen Repository), nicht aus
einem Arbeitsstand: Der Seitenfuß nennt `git describe`, und dieser Stand muss öffentlich nachlesbar sein. Bei der
ersten Veröffentlichung ist das der Commit nach dem Tag, der die DOI einträgt (Fuß etwa `v1.0.0-1-g…`); eine Kopie
vom Tag selbst verlinkt schon das Repository (Adresse seit 15.11.2026 gesetzt, KR69), hat aber keine DOI.
`deploy_kopie.py` braucht esbuild 0.25.12 in `node_modules`
(`npm ci --offline --ignore-scripts` legt es aus dem npm-Zwischenspeicher an); ohne bricht es mit „esbuild fehlt“ ab.

### Stand 15.11.2026

Probe einer Deploy-Kopie aus dem bereinigten Export beim Tag `v1.0.0` (Zwischenstand vor der Abnahme, nicht zum
Hochladen): 204 Dateien der Seiten (54 Seiten in pl, en, de),
dazu 397 Kacheln der Grundkarte und 18 Gebäudedateien für 3D, zusammen 47 MB; Stand im Fuß `2026-11-15 (v1.0.0)`.
`deploy_pruefen.mjs`: Kopie, Prüfsummen, Verkleinerung, alle Seiten im Browser und die Fehladressen ohne Befund;
**6 Befunde beim Startgewicht:**

- Planer je Sprache 324,5 bis 325,2 KB gz live (Grenze 320 KB). Die Auflage aus KR10 (live unter 320 KB) ist damit
  nicht erfüllt.
- Startseite je Sprache rund 504 KB gz, gemessen über alles, was sie lädt; das JavaScript allein liegt bei 274 KB gz.
  KR39 legt die Grenze als JavaScript-Startgewicht fest, die Prüfung misst aber noch das Gesamtgewicht; nach KR39 ist
  die Startseite unter der Grenze, die Prüfung meldet trotzdem einen Befund.

Hochgeladen wird erst, wenn diese Befunde behoben sind oder Andre die Abweichung ausdrücklich hinnimmt
(Entscheidung dokumentieren).

Vorher muss `./pruefen.sh` grün sein. Hochgeladen wird nur eine Kopie, deren `deploy_pruefen.mjs` grün ist.

## Was `skripte/deploy_kopie.py` tut

- **Dateien:** alle Seiten aus `seiten` × `sprachen`, das JavaScript und die Stylesheets der Wurzel,
  `favicon.svg`, `vendor/` ohne GSAP (`gsap.min.js`, `ScrollTrigger.min.js`, nur für die Gegenprobe Potsdam), `fonts/`, `daten/` ohne `daten/schema/` und `daten/fixtures/`, die Sprachdateien
  `texte/<lang>/*.js` und, sobald es sie gibt, `og.png` je Sprache. Nicht dabei: Vorlagen, Prüfskripte, Belege,
  Rohdaten, Dokumentation. `--liste` zeigt die Liste.
- **Cache-Busting:** An jeden lokalen Verweis auf eine Datei (`.js`, `.css`, `.svg`, `.png`, `.jpg`, `.mp4`,
  `.woff2`, alles unter `daten/`) hängt das Skript `?v=<mtime>` an. Aufgelöst wird gegen den Ordner der Seite,
  `../daten/ort.js` in `en/planer.html` also gegen die Wurzel. Dasselbe gilt für `url(…)` in den Stylesheets der
  Wurzel (Schriften). Jede Seite bekommt `window.KIEZ_V`, die jüngste mtime unter `daten/` und `fonts/`. Damit
  hängt `themen.js` den Stand auch an nachgeladene Dateien.
- **Stand im Seitenfuß:** `<span data-kiez-version>` bekommt das Datum und `git describe`, sprachneutral, etwa
  `2026-11-13 (stand-2026-11-20)`. Steht dort `-dirty`, war beim Kopieren nicht alles committet. So eine Kopie
  wird nicht hochgeladen.
- **404-Seiten:** nginx liefert die 404-Seite unter jeder fehlerhaften Adresse aus, auch unter
  `/kiezatlas/krakow/a/b/c`. Relative Verweise liefen dort ins Leere. Darum schreibt das Skript in `404.html`,
  `en/404.html` und `de/404.html` alle lokalen Verweise auf Pfade ab der Domain um (`/kiezatlas/krakow/…`). Der
  Pfad kommt aus `basis_url`. Die Vorlage bleibt relativ, damit die Seite im Repo per file:// läuft.
- **Verkleinern:** Das eigene JavaScript (`*.js` der Wurzel, `texte/**/*.js`) läuft durch esbuild 0.25.12, eine
  Entwicklungsabhängigkeit mit genauer Version und Hash in `package-lock.json`. Das Skript bricht ab, wenn in
  `node_modules` eine andere Version liegt. Ohne Bündeln und ohne Modulformat behalten die Skripte ihre gemeinsamen
  Namen auf oberster Ebene. Lizenzkommentare (`/*! … */`, `@license`) bleiben stehen. Nicht verkleinert werden
  `daten/` (dort stehen ODbL- und Quellenvermerke in gewöhnlichen Kommentaren), `vendor/` (schon verkleinert) und
  `fonts/`. Wer den Code lesen will, liest ihn im Repo beim Stand aus dem Seitenfuß. Die Prüfung belegt, dass jede
  verkleinerte Datei genau esbuild(Quelle) ist. `--unverkleinert` lässt den Schritt zum Vergleich aus.
- **MD5SUMS:** Prüfsummen über die geschriebenen, also verkleinerten und umgeschriebenen Dateien. Sie werden nicht
  hochgeladen, dienen aber der Abnahme.

### Sicherheitsgrenzen

- Das Ziel muss direkt unter `<deploy-wurzel>/kiezatlas-deploy/krakow/` liegen. Die Standard-Wurzel ist der Ordner
  über dem Repo, der Standardname das heutige Datum. Alles andere lehnt das Skript ab, auch
  `../kiezatlas-deploy/<datum>`, wo die Potsdamer Stände liegen, und Pfade, die per `..` oder Verknüpfung dorthin
  zeigen. Geprüft am 13.11.2026 mit acht Fehlzielen, alle mit Rückgabe 1 abgelehnt, nichts gelöscht
  (`belege/D13_messung.md` nennt den Stand).
- Ein bestehendes Ziel wird nur ersetzt, wenn es leer ist oder eine frühere Kraków-Kopie. Erkennbar ist die an
  einer `MD5SUMS` mit `i18n.js` und Sprachseiten. Einen fremden Ordner oder eine Potsdamer Kopie (`MD5SUMS` ohne
  Sprachseiten) rührt das Skript nicht an.
- Liegen unter `daten/` Beispieldaten (`"fixture":true`), bricht das Skript ab. Nur mit `--mit-beispieldaten`
  kopiert es trotzdem und meldet dann „nicht hochladen“. So eine Kopie ist für Probeläufe da, nicht für den Upload.
- Keine Datei der Kopie darf per Verknüpfung aus dem Repo hinauszeigen. Das Skript lädt nichts hoch und ruft
  nichts aus dem Netz ab.

## Was `skripte/deploy_pruefen.mjs --kopie` prüft

Läuft ohne Netz, rund zwei Minuten.

- Die Kopie liegt unter `kiezatlas-deploy/krakow/` und enthält keine Verknüpfungen. `MD5SUMS` deckt jede Datei
  ab und stimmt. Alle Pfade sind relativ und ohne `..`.
- Jede verkleinerte Datei ist genau esbuild(Quelle im Repo).
- Alle Seiten aller Sprachen sind da. Jede Seite hat `KIEZ_V` (überall derselbe Wert), den Stand im Fuß und `?v=`
  an jedem lokalen Verweis auf eine Datei. Kein Verweis läuft ins Leere. Die 404-Seiten verweisen nur ab der
  Domain.
- Im Browser über einen eigenen Server auf 127.0.0.1, der die Kopie unter `/kiezatlas/krakow/` ausliefert und
  fehlende Adressen wie der nginx-Vorschlag unten mit der 404-Seite der Sprache und Status 404 beantwortet:
  - Jede Seite lädt ohne Seitenfehler und ohne Konsolenfehler, jede eigene Datei mit Status 200 und `?v=`.
  - Fehladressen ein und drei Ordner tief zeigen in jeder Sprache die passende 404-Seite mit `lang` und beiden
    Stylesheets.
- **Startgewicht** je Seite: das JavaScript bis zur Ruhe, als gzip -9 (wie die Potsdamer Prüfung), wie nginx mit
  Stufe 9 und wie heute mit Stufe 6 ausliefert. Grenzen: Planer unter 320 KB (KR10), Startseite unter 300 KB je
  Sprache, gerechnet über alles, was sie lädt (Bauvorlage). Messung und Bewertung: `belege/D13_messung.md`.

`--gewicht <wurzel> --seite <seite> [--verkleinert]` misst nur das Startgewicht einer beliebigen Wurzel. Damit
ist der Stellvertreter-Planer in `belege/D13_messung.md` gemessen.

## Upload (Andre)

Additiv, **nie mit `--delete`**. Erst der Probelauf:

```sh
rsync -az -n --itemize-changes --exclude MD5SUMS ../kiezatlas-deploy/krakow/<datum>/ <server>:/opt/www/souverain-systems.de/kiezatlas/krakow/
rsync -az --exclude MD5SUMS ../kiezatlas-deploy/krakow/<datum>/ <server>:/opt/www/souverain-systems.de/kiezatlas/krakow/
```

**Wichtig für Potsdam:** `krakow/` liegt im Potsdamer Ordner `/opt/www/souverain-systems.de/kiezatlas/`. Ein
Potsdamer rsync mit `--delete` löschte Kraków. Der Potsdamer Upload darf darum nie mit `--delete` laufen. Dieser
Hinweis gehört auch in den Rundgang von `kiezatlas-potsdam`; das Kraków-Repo ändert dort nichts.

## nginx (Vorschlag für Andre)

In `souverain-nginx.conf` den bestehenden Block `location /kiezatlas/` um einen verschachtelten Block für Kraków
ergänzen. Verschachtelt, damit die gzip-Zeilen erben. Ein eigener Block auf oberster Ebene wäre längster
Präfix-Treffer und liefe ohne gzip.

```nginx
    location /kiezatlas/ {
        gzip on;
        gzip_comp_level 6;
        gzip_min_length 1024;
        gzip_vary on;
        gzip_proxied any;
        gzip_types text/css application/javascript application/json application/geo+json text/csv text/plain image/svg+xml;
        try_files $uri $uri/ $uri/index.html =404;

        # Kiezatlas Kraków: Stufe 9 hält den Planer unter 320 KB gz (Messung belege/D13_messung.md im Kraków-Repo),
        # 404 je Sprache (die Seiten verweisen ab der Domain und laden unter jeder Adresse vollständig)
        # error_page erbt nur, wenn ein Block selbst keins setzt; darum stehen 403 und 50x der Website hier erneut
        location /kiezatlas/krakow/ {
            gzip_comp_level 9;
            error_page 404 /kiezatlas/krakow/404.html;
            error_page 403 /403/index.html;
            error_page 500 502 503 504 /50x.html;
            try_files $uri $uri/ $uri/index.html =404;

            location /kiezatlas/krakow/en/ {
                error_page 404 /kiezatlas/krakow/en/404.html;
                error_page 403 /403/index.html;
                error_page 500 502 503 504 /50x.html;
                try_files $uri $uri/ $uri/index.html =404;
            }
            location /kiezatlas/krakow/de/ {
                error_page 404 /kiezatlas/krakow/de/404.html;
                error_page 403 /403/index.html;
                error_page 500 502 503 504 /50x.html;
                try_files $uri $uri/ $uri/index.html =404;
            }
        }
    }
```

Danach `nginx -t` und neu laden. Bei der Gelegenheit, Pre-existing aus Potsdam: Unter `/kiezatlas/` fehlt ein
eigenes `error_page`. Fehladressen bekommen dort die 404-Seite der Website, nicht die des Atlas.

## Sicherheits-Header (Vorschlag)

Die Seiten laden alles vom eigenen Server (MapLibre GL JS und Schriften aus `vendor/` und `fonts/`, keine fremden
Dienste). Eine Content-Security-Policy ist darum eng möglich. Sie gehört in den Block `location /kiezatlas/krakow/`
(nginx erbt `add_header` nur, wenn ein Block selbst keines setzt; die verschachtelten Blöcke `en/` und `de/` setzen
keines):

```nginx
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'sha256-…'; worker-src 'self' blob:; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none'" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

- `script-src`: Das einzige Inline-Skript ist die Zeile `window.KIEZ_V="…"`, die `skripte/deploy_kopie.py` in jede
  Seite setzt. Ihr Hash hängt vom Stempel ab und ändert sich mit jeder Deploy-Kopie; `deploy_kopie.py` gibt die fertige
  Angabe `'self' 'sha256-…'` aus. Bei jedem Upload ist sie im Header zu erneuern, sonst laden die Seiten ohne
  Versionsstempel (nachgeladene Dateien dann ohne `?v=`, also ohne Cache-Busting).
- `worker-src blob:`: MapLibre startet seinen Worker aus einer `blob:`-Adresse; ohne die Angabe bleibt die Karte leer.
- `style-src 'unsafe-inline'`: Popups und Legenden setzen Farben per `style`-Attribut.
- Geprüft am 14.11.2026 mit Playwright über `skripte/entwicklung_server.mjs` (Header per Abfangen gesetzt, ohne das
  Inline-Skript): 15 Seiten in pl, en und de, darunter alle Kartenseiten und `karta.html?3d=1`, ohne
  CSP-Verletzung, Karte gezeichnet. Gegenprobe: ohne `worker-src blob:` meldet der Browser die Verletzung. Dazu eine
  Deploy-Kopie (`deploy_kopie.py --unverkleinert`, lokal, nicht hochgeladen) mit dem ausgegebenen Hash: 11 Seiten
  ohne Verletzung, `window.KIEZ_V` gesetzt; mit falschem Hash blockiert der Browser das Inline-Skript. Nicht geprüft
  ist die verkleinerte Fassung (esbuild); der Hash betrifft nur die Inline-Zeile.

## Abnahme nach dem Upload

Die Abnahme macht Andre oder das Paket Auslieferung. Nur lesende Abrufe der eigenen Seiten:

```sh
# 1. live-MD5 = MD5SUMS (ohne Accept-Encoding, also die Datei selbst)
cd ../kiezatlas-deploy/krakow/<datum>
while read -r h p; do
  l=$(curl -fsS "https://souverain-systems.de/kiezatlas/krakow/$p" | md5sum | cut -d' ' -f1)
  [ "$l" = "$h" ] || echo "ABWEICHUNG $p"
done < MD5SUMS

# 2. 404 je Sprache mit Status 404
for u in gibt-es-nicht a/b/c en/gibt-es-nicht de/x/y; do
  curl -s -o /dev/null -w "%{http_code} $u\n" "https://souverain-systems.de/kiezatlas/krakow/$u"
done

# 3. Startgewicht live: gepackte Größe jeder JavaScript-Datei, die planer.html beim Start lädt
#    (Liste aus deploy_pruefen.mjs, Zeile „planer.html“), Summe unter 327680 Byte
for f in daten/ort.js i18n.js texte/pl/kern.js texte/pl/seiten.js kopf.js rahmen.js; do
  curl -s -H 'Accept-Encoding: gzip' -o /dev/null -w "%{size_download} $f\n" "https://souverain-systems.de/kiezatlas/krakow/$f"
done | awk '{s+=$1; print} END {print s, "Byte gesamt"}'
```

Ob die hreflang-Verweise live in beide Richtungen stimmen, prüft das Paket Auslieferung.

## Nach der Veröffentlichung des Repositorys

Die Adresse steht seit 15.11.2026 in `config/krakow.yaml` (`repository`, KR69). Ist der Schlüssel leer (etwa in
einem Fork vor dessen Veröffentlichung), sagen Methoden- und Datenseite in allen drei Sprachen, das Repository sei
noch nicht öffentlich, und nennen die Meldeadresse. Ist es öffentlich, die Adresse eintragen und die Seiten neu
erzeugen; dann verlinken beide Seiten „Repository“, und der Satz „auf Anfrage“ entfällt:

```sh
# in config/krakow.yaml:  repository: "https://…"   (nur https)
$PY skripte/31_ort.py && $PY skripte/16_bloecke_krakow.py && $PY skripte/30_seiten.py   # ort.js trägt die Prüfsumme der Konfiguration
./pruefen.sh                               # danach neue Deploy-Kopie wie oben
```

`pruefen/S4_bloecke.py` (Teil 9) prüft, dass die eingetragene Adresse auf der Methoden- und der Datenseite steht.

## Vorschaubild

`node skripte/28_vorschaubild.mjs --lang pl|en|de` bzw. `--alle` nimmt die Kartenseite der Sprache mit 3D-Häusern
um `karte.haus_ziel` auf. Titel, Untertitel, Kamera und erlaubte Hosts kommen aus `daten/ort.js` und
`texte/<lang>/seiten.js`. Das Bild landet als `og.png` bzw. `<lang>/og.png` und kommt so in die Deploy-Kopie.
Heute endet das Skript mit Rückgabe 2: Grundkarte und Gebäude fehlen noch. Ein Ersatzbild ohne Karte erzeugt es
nicht. Die Kartenaufnahme selbst ist erst prüfbar, wenn die Kartenseite Grundkarte und Häuser hat. Das
`og:image` steht noch nicht im Seitenrahmen (Vorschlag: `docs/entscheidungen/D13.md`).

## Recht (Andre)

Impressum und Datenschutz verlinken je Sprache auf die passende Fassung der UG-Website (Seitenfuß,
`vorlagen/_rahmen.html` über `{{ort:impressum}}` und `{{ort:datenschutz}}`; Adressen in `config/krakow.yaml`,
Schlüssel `impressum` und `datenschutz`):

| Sprache | Impressum | Datenschutz |
|---|---|---|
| pl | `https://souverain-systems.de/pl/nota-prawna/` | `https://souverain-systems.de/pl/polityka-prywatnosci/` |
| en | `https://souverain-systems.de/en/imprint/` | `https://souverain-systems.de/en/privacy/` |
| de | `https://souverain-systems.de/impressum/` | `https://souverain-systems.de/datenschutz/` |

Die polnischen und englischen Fassungen sind Übersetzungen; verbindlich ist die deutsche (Hinweis oben auf jeder
Fassung). Die Datenschutzerklärung beschreibt den Kiezatlas (statische Seiten, Grundkarte, Schrift, Skripte und
Downloads vom eigenen Server, kein Luftbild, keine Fremdabrufe; Sprachhinweis im localStorage; Besucherstatistik mit
gekürzten IP-Adressen). Quelle der Rechtstexte: Repository `andrestiebitz-site`, Worktree `ug-neu`
(`sites/portfolio/src/pages/{impressum,datenschutz}.astro`, `en/`, `pl/`).

**Reihenfolge:** Die polnischen Seiten gibt es erst, wenn die UG-Website mit ihnen veröffentlicht ist. Deshalb zuerst
die Website hochladen und prüfen (`curl -sI https://souverain-systems.de/pl/nota-prawna/` und
`…/pl/polityka-prywatnosci/` je `200`), danach die Kiezatlas-Kopie. Neue Kartendienste (Grundkarte, Luftbild),
eingebettete Filme oder andere neue Abrufe müssen vor dem Upload in die Datenschutzerklärung, in allen drei Fassungen.
