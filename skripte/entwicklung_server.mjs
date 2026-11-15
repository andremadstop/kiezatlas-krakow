// Entwicklungsserver: liefert die Atlas-Wurzel auf 127.0.0.1 aus und hängt zwei Ordner außerhalb des Repos ein:
//   daten/grundkarte/  Kachelordner der Grundkarte (Kacheln und Kartenschrift, erzeugt von skripte/27_grundkarte.py
//                      unter $KIEZ_DATEN/abgeleitet/grundkarte/<SHA-Anfang>/);
//   daten/gebaeude/    Gebäude in 3D je dzielnica (<nr>_odbl.js, erzeugt von skripte/20_bdot10k.py --geometrie unter
//                      $KIEZ_DATEN/abgeleitet/gebaeude/<Stand aus config/gebaeude_3d.json>/, ohne Manifest dort der
//                      jüngste Ordner *-odbl mit Manifest); ausgeliefert werden nur die Dateien, die im Manifest des
//                      Ordners stehen (MANIFEST.sha256, sonst SHA256SUMS) und deren SHA256 beim Start zum Manifest
//                      passt, nicht HERKUNFT.md. Abweichende Dateien meldet der Server und liefert sie nicht aus (404),
//                      wie skripte/deploy_kopie.py sie nicht kopiert.
// Auf dem Server liegen dieselben Ordner unter daten/grundkarte/ und daten/gebaeude/ der Auslieferung
// (skripte/deploy_kopie.py); die Seiten merken keinen Unterschied.
//
// Aufruf: node skripte/entwicklung_server.mjs [--port 8080] [--ziel KACHELORDNER] [--gebaeude GEBAEUDEORDNER]
// Dann z. B. http://127.0.0.1:8080/karta.html öffnen. Nur 127.0.0.1, nur lesend. Unter file:// zeigen die Seiten
// keine eigene Grundkarte (MapLibre lädt dort keine Kacheln) und keine 3D-Häuser; dafür ist dieser Server da.
//
// Ausgeliefert wird nur, was auch die Deploy-Kopie ausliefert (Freigabeliste wie skripte/deploy_kopie.py): Seiten
// *.html in der Wurzel und in den Sprachordnern aus config/krakow.yaml (sprachen), *.js, *.css, favicon.svg und
// og.png in der Wurzel, vendor/, fonts/, daten/ ohne daten/fixtures/ und daten/schema/, texte/<lang>/*.js, dazu die
// beiden eingehängten Ordner (Grundkarte nur kacheln/ und schrift/, Gebäude nur die Dateien aus dem Manifest). Alles andere, besonders .env, .git/, node_modules/, Skripte, Belege und jeder Pfad
// mit einem Teil, der mit einem Punkt beginnt, gibt 404. Anfragen mit einem anderen Host-Kopf als
// 127.0.0.1:<port> oder localhost:<port> geben 403 (Schutz gegen DNS-Rebinding: eine fremde Seite, deren Name
// auf 127.0.0.1 zeigt, schickt ihren eigenen Namen im Host-Kopf).
import http from "node:http";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const WURZEL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const TYPEN = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png",
  ".woff2": "font/woff2", ".pbf": "application/x-protobuf", ".txt": "text/plain; charset=utf-8",
};

// Kachelordner wie skripte/27_grundkarte_vorschau.mjs: SHA der BDOT10k-Eingabe aus skripte/27_grundkarte.py
export function kachelordner(ziel) {
  if (ziel) return path.resolve(ziel);
  const daten = process.env.KIEZ_DATEN || path.join(WURZEL, "..", "kiezatlas-daten", "krakow");
  const sha = /BDOT_SHA256 = "([0-9a-f]{64})"/.exec(fs.readFileSync(path.join(WURZEL, "skripte", "27_grundkarte.py"), "utf8"))[1];
  return path.join(daten, "abgeleitet", "grundkarte", sha.slice(0, 12));
}

// Stand der 3D-Dateien (Ordnername unter abgeleitet/gebaeude/) aus config/gebaeude_3d.json, wie skripte/deploy_kopie.py
export const GEBAEUDE_STAND = JSON.parse(fs.readFileSync(path.join(WURZEL, "config", "gebaeude_3d.json"), "utf8")).stand;
const GEB_MANIFESTE = ["MANIFEST.sha256", "SHA256SUMS"];

// Gebäudeordner: --gebaeude, sonst abgeleitet/gebaeude/<GEBAEUDE_STAND>/; fehlt dort ein Manifest, der jüngste Ordner
// *-odbl mit Manifest (ein neuer Lauf von skripte/kette.py schreibt nach <heute>-odbl/)
export function gebaeudeordner(ziel) {
  if (ziel) return path.resolve(ziel);
  const daten = process.env.KIEZ_DATEN || path.join(WURZEL, "..", "kiezatlas-daten", "krakow");
  const basis = path.join(daten, "abgeleitet", "gebaeude"), fest = path.join(basis, GEBAEUDE_STAND);
  const mitManifest = (o) => GEB_MANIFESTE.some((n) => fs.existsSync(path.join(o, n)));
  if (mitManifest(fest) || !fs.existsSync(basis)) return fest;
  const kand = fs.readdirSync(basis).filter((n) => /-odbl$/.test(n) && mitManifest(path.join(basis, n))).sort();
  return kand.length ? path.join(basis, kand[kand.length - 1]) : fest;
}

// Dateinamen aus dem Manifest des Gebäudeordners (Zeilen „<sha256>  <name>“), nur Dateien, deren SHA256 zum Manifest
// passt; leer, wenn es keines gibt. Abweichende oder fehlende Dateien stehen in .abweichend (Liste der Namen).
export function gebaeudeliste(ordner) {
  for (const name of GEB_MANIFESTE) {
    const p = path.join(ordner, name);
    if (fs.existsSync(p)) {
      const gut = new Set(), abweichend = [];
      for (const z of fs.readFileSync(p, "utf8").split("\n")) {
        const [sha, n] = z.split("  ");
        if (!n || !/^[0-9]{2}_odbl\.js$/.test(n)) continue;
        const d = path.join(ordner, n);
        const ist = fs.existsSync(d) ? crypto.createHash("sha256").update(fs.readFileSync(d)).digest("hex") : null;
        if (ist === sha) gut.add(n); else abweichend.push(n);
      }
      gut.abweichend = abweichend;
      return gut;
    }
  }
  const leer = new Set();
  leer.abweichend = [];
  return leer;
}

// Sprachordner aus der Ortskonfiguration (Zeile „sprachen: [pl, en, de]“; die erste Sprache liegt in der Wurzel)
export function sprachordner() {
  const k = process.env.KIEZ_CONFIG || path.join(WURZEL, "config", "krakow.yaml");
  const m = /^sprachen:\s*\[([^\]]*)\]/m.exec(fs.readFileSync(k, "utf8"));
  return new Set(m ? m[1].split(",").map((x) => x.trim()).filter(Boolean).slice(1) : []);
}

// Darf ein Pfad unter der Wurzel ausgeliefert werden? (rel ohne führenden Schrägstrich, POSIX)
export function freigegeben(rel, sprachen = sprachordner()) {
  const t = rel.split("/");
  if (t.some((x) => x === "" || x.startsWith("."))) return false;
  const name = t[t.length - 1];
  if (t.length === 1) return /\.(html|js|css)$/.test(name) || name === "favicon.svg" || name === "og.png";
  if (t.length === 2 && sprachen.has(t[0])) return name.endsWith(".html") || name === "og.png";
  if (t[0] === "vendor" || t[0] === "fonts") return true;
  if (t[0] === "daten") return t[1] !== "fixtures" && t[1] !== "schema";
  if (t[0] === "texte") return t.length === 3 && name.endsWith(".js");
  return false;
}

// zusatz: { "/pfad.html": () => "<html>…" } für Prüfseiten, die nicht im Repo liegen
export function starten({ port = 0, ziel, gebaeude, zusatz = {} } = {}) {
  const KACHELN = kachelordner(ziel);
  const GEB = gebaeudeordner(gebaeude), GEB_LISTE = gebaeudeliste(GEB);
  const SPRACHEN = sprachordner();
  let hosts = new Set();
  if (GEB_LISTE.abweichend.length) console.error(`Gebäude 3D: SHA256 weicht vom Manifest ab oder Datei fehlt, nicht ausgeliefert: ${GEB_LISTE.abweichend.join(", ")}`);
  const server = http.createServer((q, a) => {
    if (!hosts.has(String(q.headers.host || "").toLowerCase())) { a.writeHead(403); a.end(); return; }
    let url;
    try { url = decodeURIComponent(new URL(q.url, "http://x").pathname); } catch { a.writeHead(400); a.end(); return; }
    if (q.method !== "GET" && q.method !== "HEAD") { a.writeHead(405); a.end(); return; }
    if (zusatz[url]) { a.writeHead(200, { "content-type": TYPEN[".html"] }); a.end(zusatz[url]()); return; }
    if (url.endsWith("/")) url += "index.html";
    const rel = url.replace(/^\/+/, "");
    const gk = rel.startsWith("daten/grundkarte/"), geb = rel.startsWith("daten/gebaeude/");
    const basis = gk ? KACHELN : geb ? GEB : WURZEL;
    const datei = path.resolve(basis, gk ? rel.slice("daten/grundkarte/".length) : geb ? rel.slice("daten/gebaeude/".length) : rel);
    if ((geb && !GEB_LISTE.has(path.relative(GEB, datei))) || (!gk && !geb && !freigegeben(rel, SPRACHEN)) ||
        (gk && !/^daten\/grundkarte\/(kacheln|schrift)\//.test(rel)) ||
        rel.split("/").some((x) => x.startsWith(".")) ||
        !datei.startsWith(basis + path.sep) || !fs.existsSync(datei) || !fs.statSync(datei).isFile()) {
      a.writeHead(404); a.end(); return;
    }
    a.writeHead(200, { "content-type": TYPEN[path.extname(datei)] || "application/octet-stream" });
    a.end(q.method === "HEAD" ? undefined : fs.readFileSync(datei));
  });
  return new Promise((r) => server.listen(port, "127.0.0.1", () => {
    const p = server.address().port;
    hosts = new Set([`127.0.0.1:${p}`, `localhost:${p}`]);
    r({ server, url: `http://127.0.0.1:${p}/`, kacheln: KACHELN, gebaeude: GEB, gebaeude_dateien: GEB_LISTE.size, gebaeude_abweichend: GEB_LISTE.abweichend.length });
  }));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
  const { url, kacheln, gebaeude, gebaeude_dateien } = await starten({ port: Number(arg("--port", 8080)), ziel: arg("--ziel"), gebaeude: arg("--gebaeude") });
  if (!fs.existsSync(path.join(kacheln, "MANIFEST.sha256"))) console.error(`Hinweis: kein Kachelordner unter ${kacheln}; die Seiten zeigen dann keine Grundkarte`);
  if (!gebaeude_dateien) console.error(`Hinweis: keine 3D-Dateien mit Manifest unter ${gebaeude}; der Knopf „3D“ meldet dann fehlende Dateien`);
  console.log(`Atlas unter ${url} (Grundkarte aus ${kacheln}, ${gebaeude_dateien} 3D-Dateien aus ${gebaeude}); Ende mit Strg+C`);
}
