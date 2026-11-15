// Sichtprobe Grundkarte (Regel G13 in pruefen/D8_protokoll.md): MapLibre 4.7.1 aus vendor/, nur 127.0.0.1.
//
// Startet einen eigenen HTTP-Server auf 127.0.0.1 (freier Port), der die Atlas-Wurzel ausliefert und unter
// daten/grundkarte/ den Kachelordner von skripte/27_grundkarte.py einhängt (so liegt er später auch auf dem Server).
// Die Vorschauseite baut den Stil wie themen.js: Quelle bm = KIEZ_GRUNDKARTE.quelle, glyphs, unten, oben, dazu nur
// ein Papier-Hintergrund. Kachel- und Schrift-URL bleiben relativ wie in daten/grundkarte.js.
// Jeder Abruf außerhalb 127.0.0.1 wird abgebrochen und als Befund gezählt; Konsolenfehler und fehlgeschlagene
// Abrufe ebenso. Bildschirmfotos (Chromium, Playwright) nach --bilder DIR (Standard belege/D8_vorschau/).
//
// Aufruf: node skripte/27_grundkarte_vorschau.mjs [--ziel KACHELORDNER] [--bilder DIR]
// Rückgabe 0 = Karte gezeichnet, keine Fehler; 1 = Befund.
import { chromium } from "playwright";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const WURZEL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const KIEZ_DATEN = process.env.KIEZ_DATEN || path.join(WURZEL, "..", "kiezatlas-daten", "krakow");
const sha = /BDOT_SHA256 = "([0-9a-f]{64})"/.exec(fs.readFileSync(path.join(WURZEL, "skripte", "27_grundkarte.py"), "utf8"))[1];
const ZIEL = path.resolve(arg("--ziel", path.join(KIEZ_DATEN, "abgeleitet", "grundkarte", sha.slice(0, 12))));
const BILDER = path.resolve(arg("--bilder", path.join(WURZEL, "belege", "D8_vorschau")));
if (!fs.existsSync(path.join(ZIEL, "MANIFEST.sha256"))) { console.error(`kein Kachelordner: ${ZIEL}`); process.exit(1); }

// MapLibre lädt Kacheln im Worker und kann relative URLs nicht auflösen („Failed to parse URL“). Die Seite macht
// sie darum absolut, bezogen auf den Ort von daten/grundkarte.js (eine Ebene darüber = Atlas-Wurzel, gleich ob die
// Seite in der Wurzel oder in en/, de/ liegt). Dieselben Zeilen schlägt docs/entscheidungen/D8.md für themen.js vor.
const SEITE = (vor, lang) => `<!doctype html><html lang="${lang}"><head><meta charset="utf-8">
<link rel="stylesheet" href="${vor}vendor/maplibre-gl.css">
<style>html,body,#k{margin:0;height:100%}</style></head><body><div id="k"></div>
<script src="${vor}vendor/maplibre-gl.js"></script><script src="${vor}daten/grundkarte.js"></script>
<script>
var GK = window.KIEZ_GRUNDKARTE;
var GK_WURZEL = new URL("../", document.querySelector('script[src$="daten/grundkarte.js"]').src).href;
function gkAbsolut(u) { return /^[a-z][a-z0-9+.-]*:/i.test(u) ? u : GK_WURZEL + u; }
var quelle = Object.assign({}, GK.quelle, { tiles: GK.quelle.tiles.map(gkAbsolut) });
var stil = { version: 8, glyphs: gkAbsolut(GK.glyphs), sources: { bm: quelle },
  layers: [{ id: "papier", type: "background", paint: { "background-color": "#f1f2ee" } }].concat(GK.unten, GK.oben) };
window.fehler = [];
window.karte = new maplibregl.Map({ container: "k", style: stil, center: [19.94, 50.06], zoom: 11,
  attributionControl: { compact: false }, fadeDuration: 0 });
window.karte.on("error", function (e) { window.fehler.push(String(e && e.error && e.error.message || e)); });
</script></body></html>`;

const TYPEN = { ".js": "text/javascript", ".css": "text/css", ".pbf": "application/x-protobuf", ".html": "text/html" };
const server = http.createServer((q, a) => {
  const url = decodeURIComponent(new URL(q.url, "http://x").pathname);
  if (url === "/vorschau.html" || url === "/en/vorschau.html") {
    a.writeHead(200, { "content-type": "text/html" });
    a.end(url === "/vorschau.html" ? SEITE("", "pl") : SEITE("../", "en"));
    return;
  }
  const rel = url.replace(/^\/+/, "");
  const datei = rel.startsWith("daten/grundkarte/") ? path.join(ZIEL, rel.slice("daten/grundkarte/".length)) : path.join(WURZEL, rel);
  const basis = rel.startsWith("daten/grundkarte/") ? ZIEL : WURZEL;
  if (!path.resolve(datei).startsWith(basis + path.sep) || !fs.existsSync(datei) || !fs.statSync(datei).isFile()) {
    a.writeHead(404); a.end(); return;
  }
  a.writeHead(200, { "content-type": TYPEN[path.extname(datei)] || "application/octet-stream" });
  a.end(fs.readFileSync(datei));
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const HTTP = `http://127.0.0.1:${server.address().port}/`;

const befunde = [], fremd = [], kaputt = [], konsole = [];
const pruef = (ok, text) => { console.log((ok ? "  ok    " : "  FEHLT ") + text); if (!ok) befunde.push(text); };
const browser = await chromium.launch();
const seite = await browser.newPage({ viewport: { width: 1000, height: 700 } });
await seite.route("**/*", (r) => {
  const u = new URL(r.request().url());
  if (u.hostname !== "127.0.0.1") { fremd.push(u.href); return r.abort(); }
  return r.continue();
});
seite.on("console", (m) => { if (m.type() === "error") konsole.push(m.text()); });
seite.on("response", (r) => { if (r.status() >= 400) kaputt.push(`${r.status()} ${r.url().replace(HTTP, "")}`); });
fs.mkdirSync(BILDER, { recursive: true });
const ansichten = [   // Seite, Name, Mitte, Zoom; en/ prüft die Auflösung der Pfade aus einem Sprachordner
  ["vorschau.html", "stadt_z11", [19.94, 50.06], 11],
  ["vorschau.html", "altstadt_z14", [19.9373, 50.0617], 14],
  ["vorschau.html", "kazimierz_z16", [19.9445, 50.0515], 16],
  ["en/vorschau.html", "en_altstadt_z14", [19.9373, 50.0617], 14],
];
let geladen = null;
for (const [url, name, mitte, zoom] of ansichten) {
  if (geladen !== url) { await seite.goto(HTTP + url); geladen = url; }
  await seite.evaluate(([m, z]) => window.karte.jumpTo({ center: m, zoom: z }), [mitte, zoom]);
  try {
    await seite.waitForFunction(() => window.karte.loaded() && window.karte.areTilesLoaded(), null, { timeout: 30000 });
  } catch (e) {
    pruef(false, `${name}: Karte nach 30 s nicht geladen; MapLibre: ${(await seite.evaluate(() => window.fehler)).slice(0, 3).join(" | ")}; Konsole: ${konsole.slice(0, 3).join(" | ")}; Abrufe: ${kaputt.slice(0, 3).join(" | ")}`);
    continue;
  }
  await seite.waitForTimeout(300);
  const zahl = await seite.evaluate(() => {
    const f = window.karte.queryRenderedFeatures();
    const n = {};
    f.forEach((x) => { n[x.sourceLayer] = (n[x.sourceLayer] || 0) + 1; });
    const namen = f.filter((x) => x.layer.type === "symbol").map((x) => x.properties.nazwa).filter(Boolean);
    return { n, namen: [...new Set(namen)].sort() };
  });
  if (!name.startsWith("en_")) await seite.screenshot({ path: path.join(BILDER, `${name}.png`) });   // en/ zeichnet dasselbe
  const pl = zahl.namen.filter((s) => /[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]/.test(s));
  pruef(Object.keys(zahl.n).length > 0, `${name}: gezeichnete Objekte je Schicht ${JSON.stringify(zahl.n)}`);
  console.log(`        Beschriftungen ${zahl.namen.length}, davon mit polnischem Sonderzeichen ${pl.length}` +
    (pl.length ? ` (z. B. „${pl.slice(0, 3).join("“, „")}“)` : ""));
  if (zoom >= 14) pruef(pl.length > 0, `${name}: mindestens eine Beschriftung mit polnischem Sonderzeichen gezeichnet`);
}
const attribution = await seite.evaluate(() => document.querySelector(".maplibregl-ctrl-attrib-inner")?.textContent || "");
pruef(/BDOT10k/.test(attribution) && /Główny Urząd Geodezji i Kartografii/.test(attribution), `Bildzeile auf der Karte: „${attribution}“`);
const mlFehler = await seite.evaluate(() => window.fehler);
pruef(!mlFehler.length, `keine MapLibre-Fehler${mlFehler.length ? ": " + mlFehler.slice(0, 3).join(" | ") : ""}`);
pruef(!konsole.length, `keine Konsolenfehler${konsole.length ? ": " + konsole.slice(0, 3).join(" | ") : ""}`);
pruef(!kaputt.length, `keine fehlgeschlagenen Abrufe${kaputt.length ? ": " + kaputt.slice(0, 3).join(" | ") : ""}`);
pruef(!fremd.length, `kein Abruf außerhalb 127.0.0.1${fremd.length ? ": " + fremd.slice(0, 3).join(" | ") : ""}`);
await browser.close();
server.close();
console.log(`\nVorschau: ${befunde.length} Befund(e), Bilder unter ${path.relative(WURZEL, BILDER) || BILDER}`);
process.exit(befunde.length ? 1 : 0);
