// Vorschaubild og.png (1200 × 630) je Sprache aus einer eigenen Aufnahme der Kartenseite mit 3D-Häusern um das
// Kamera-Ziel „Häuser“ der Ortskonfiguration (Kraków: Rynek Główny).
//
// Ablauf: eigener Server auf 127.0.0.1 (nur Dateien dieses Ordners), headless Chromium aus node_modules, die
// Kartenseite der gewählten Sprache mit #3d=1 laden (karta.html bzw. <lang>/karta.html), warten bis die Seite bereit
// ist und Häuser gezeichnet sind. Dann Kopfleiste, Text und Knöpfe ausblenden, Karte bildfüllend, feste Kamera,
// Titelzeile und Quellenvermerk darüberlegen, Bildschirmfoto. Ausgabe: Pfad, MD5 und Größe des Bildes.
//
// Alles Ortsgebundene kommt aus den Dateien, nicht aus diesem Skript:
//   Titel             KIEZ_ORT.name[lang]                       (daten/ort.js)
//   Untertitel        seiten.karta.beschreibung                 (texte/<lang>/seiten.js)
//   Kamera            KIEZ_ORT.karte.haus_ziel, feste Höhe/Neigung/Drehung unten
//   erlaubte Hosts    Herkunft der Kacheln der Grundkarte       (KIEZ_ORT.karte.grundkarte: url, tiles)
//   Browsersprache    pl-PL, en-GB, de-DE
//   Quellenvermerk    wörtlich, was die Seite im „i“ der Karte zeigt
// Ausgabe: og.png für die erste Sprache, <lang>/og.png für die anderen (skripte/deploy_kopie.py nimmt sie mit).
//
// Voraussetzung: eine Grundkarte in der Ortskonfiguration (karte.grundkarte) und Gebäude für die 3D-Häuser. Fehlt
// das, endet das Skript mit Rückgabe 2 und sagt, was fehlt; ein Ersatzbild ohne Karte erzeugt es nicht.
//
// Netz: nur die Hosts der Grundkarte; liegen die Kacheln auf dem eigenen Server, gar keins. Alles andere beantwortet
// der Browser leer (gezählt). Mit --ohne-netz auch die Grundkarte leer (Probelauf ohne jeden Abruf).
//
// Aufruf:  node skripte/28_vorschaubild.mjs --lang pl|en|de [--aus <datei>] [--ohne-netz]
//          node skripte/28_vorschaubild.mjs --alle [--ohne-netz]     (alle Sprachen der Ortskonfiguration)
import { chromium } from "playwright";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const WURZEL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const OHNE_NETZ = process.argv.includes("--ohne-netz");
const LOCALE = { pl: "pl-PL", en: "en-GB", de: "de-DE" };
const BLICK = { zoom: 16.15, pitch: 58, bearing: -24 };   // feste Höhe, Neigung und Drehung; Mitte aus haus_ziel

function lies(datei, global) {
  const s = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(WURZEL, datei), "utf8"), s);
  return s.window[global];
}
const ORT = lies("daten/ort.js", "KIEZ_ORT");
const sprachen = process.argv.includes("--alle") ? ORT.sprachen : [arg("--lang", "")];
const falsch = sprachen.filter((l) => !ORT.sprachen.includes(l) || !LOCALE[l]);
if (!sprachen.length || falsch.length) {
  console.log(`Aufruf: --lang ${ORT.sprachen.join("|")} oder --alle (unbekannt: ${falsch.join(", ") || "keine Sprache"})`); process.exit(2);
}
if (sprachen.length > 1 && arg("--aus")) { console.log("--aus nur mit einer Sprache"); process.exit(2); }

// Voraussetzungen, bevor ein Browser startet
const fehlt = [];
const gk = ORT.karte && ORT.karte.grundkarte;
if (!gk) fehlt.push("karte.grundkarte ist leer (config/krakow.yaml, Abschnitt karte; Paket Grundkarte und Luftbild)");
if (!fs.existsSync(path.join(WURZEL, "daten", "gebaeude")) || !fs.readdirSync(path.join(WURZEL, "daten", "gebaeude")).length) {
  fehlt.push("keine Gebäude unter daten/gebaeude/ für die 3D-Häuser (Paket Gebäude und Kamienice)");
}
if (fehlt.length) {
  console.log("Vorschaubild nicht erzeugt, Voraussetzung fehlt:\n  - " + fehlt.join("\n  - "));
  process.exit(2);
}
const ERLAUBT = [...new Set([gk.url, ...(gk.tiles || [])].filter((u) => /^https:\/\//.test(u || "")).map((u) => new URL(u).origin + "/"))];

const TYP = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2",
  ".json": "application/json", ".pbf": "application/x-protobuf" };
const server = http.createServer((q, a) => {
  const p = path.normalize(path.join(WURZEL, decodeURIComponent(new URL(q.url, "http://x").pathname)));
  if (p !== WURZEL && !p.startsWith(WURZEL + path.sep)) { a.writeHead(403); a.end(); return; }
  fs.readFile(p, (f, d) => { if (f) { a.writeHead(404); a.end(); return; } a.writeHead(200, { "content-type": TYP[path.extname(p)] || "application/octet-stream" }); a.end(d); });
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const BASIS = `http://127.0.0.1:${server.address().port}/`;

const browser = await chromium.launch();
let rc = 0;
try {
  for (const lang of sprachen) {
    const erste = lang === ORT.sprachen[0], ordner = erste ? "" : lang + "/";
    const T = lies(`texte/${lang}/seiten.js`, "KIEZ_TEXTE") || {};
    const titel = ORT.name[lang], unter = T["seiten.karta.beschreibung"];
    if (!titel || !unter) { console.log(`[${lang}] Titel oder seiten.karta.beschreibung fehlt`); rc = 1; continue; }
    const aus = path.resolve(arg("--aus", path.join(WURZEL, ordner, "og.png")));
    const kamera = { center: ORT.karte.haus_ziel, ...BLICK };
    const zaehler = { eigen: 0, grundkarte: 0, leer: 0 };
    const ctx = await browser.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1, reducedMotion: "reduce", locale: LOCALE[lang] });
    const page = await ctx.newPage();
    const fehler = [];
    page.on("pageerror", (e) => fehler.push(e.message));
    await page.route("**/*", (r) => {
      const u = r.request().url();
      if (u.startsWith(BASIS) || /^(data|blob):/.test(u)) { zaehler.eigen++; return r.continue(); }
      if (!OHNE_NETZ && ERLAUBT.some((e) => u.startsWith(e))) { zaehler.grundkarte++; return r.continue(); }
      zaehler.leer++;
      return r.fulfill(/\.pbf(\?|$)/.test(u) ? { status: 200, contentType: "application/x-protobuf", body: Buffer.alloc(0) } : { status: 204, body: "" });
    });
    await page.goto(BASIS + ordner + "karta.html#3d=1", { waitUntil: "load" });
    await page.waitForFunction(() => window.KIEZ_BEREIT === true && window.KIEZ_KARTE, null, { timeout: 90000 });
    await page.waitForFunction(() => window.KIEZ_KARTE.getLayer("geb-3d") && window.KIEZ_KARTE.queryRenderedFeatures({ layers: ["geb-3d"] }).length > 0, null, { timeout: 30000 });
    // Bühne bildfüllend, alles andere aus; Titel und Vermerk als eigene Lage darüber
    await page.addStyleTag({ content: `
      body > *:not(#buehne):not(.og-lage) { display: none !important; }
      #buehne .werkzeug, #buehne .maplibregl-control-container, #buehne .schild { display: none !important; }
      html, body { overflow: hidden !important; height: 100% !important; }
      #buehne { position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important; border: 0 !important; z-index: 50; display: block !important; }
      #buehne #karte { position: absolute !important; inset: 0 !important; }
      .og-lage { position: fixed; inset: 0; z-index: 60; pointer-events: none; font-family: var(--f-text); color: var(--ink); }
      .og-kopf { position: absolute; left: 0; top: 0; padding: 30px 40px 26px 44px; background: rgba(241,242,238,.94); border-right: 1px solid var(--line); border-bottom: 4px solid var(--accent); max-width: 760px; }
      .og-marke { display: flex; align-items: center; gap: 16px; font: 600 64px/1 var(--f-display); letter-spacing: -.02em; margin: 0; }
      .og-marke i { width: 30px; height: 30px; flex: 0 0 auto; outline: 2px solid var(--ink); background: linear-gradient(var(--accent) 0 0) 0 0/50% 50% no-repeat, linear-gradient(var(--ink) 0 0) 100% 100%/50% 50% no-repeat; }
      .og-unter { font: 500 24px/1.25 var(--f-text); color: var(--muted); margin: 12px 0 0 46px; }
      .og-vermerk { position: absolute; right: 0; bottom: 0; padding: 6px 12px; font: 400 14px/1.35 var(--f-text); color: var(--ink); background: rgba(250,251,248,.9); white-space: pre-line; text-align: right; }` });
    await page.evaluate(([t, u]) => {
      const l = document.createElement("div"); l.className = "og-lage";
      l.innerHTML = '<div class="og-kopf"><p class="og-marke"><i></i><span></span></p><p class="og-unter"></p></div><p class="og-vermerk"></p>';
      l.querySelector(".og-marke span").textContent = t; l.querySelector(".og-unter").textContent = u;
      document.body.appendChild(document.getElementById("buehne"));   // Bühne aus dem Raster der Seite lösen
      document.body.appendChild(l);
    }, [titel, unter]);
    await page.evaluate((k) => { const m = window.KIEZ_KARTE; m.resize(); m.jumpTo(k); }, kamera);
    await page.waitForFunction(() => window.KIEZ_KARTE.queryRenderedFeatures({ layers: ["geb-3d"] }).length > 200, null, { timeout: 30000 });
    // Ruhe: keine Bewegung, Stil und alle Kacheln geladen, dann ein „idle“ (höchstens 20 s), Schriften da
    await page.waitForFunction(() => { const m = window.KIEZ_KARTE; return !m.isMoving() && m.loaded() && m.areTilesLoaded(); }, null, { timeout: 60000, polling: 250 });
    await page.evaluate(() => new Promise((r) => { const m = window.KIEZ_KARTE; m.once("idle", r); m.triggerRepaint(); setTimeout(r, 20000); }));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(800);
    const vermerk = await page.evaluate(() => {
      const t = document.querySelector("#karte .maplibregl-ctrl-attrib-inner").textContent.split(" | ").map((x) => x.trim()).filter(Boolean);
      document.querySelector(".og-vermerk").textContent = t.join("\n"); return t;
    });
    if (!vermerk.length) { console.log(`[${lang}] BEFUND: kein Quellenvermerk auf der Seite, kein Bild`); rc = 1; await ctx.close(); continue; }
    await page.waitForTimeout(200);
    const z = await page.evaluate(() => { const m = window.KIEZ_KARTE;
      return { haeuser: m.queryRenderedFeatures({ layers: ["geb-3d"] }).length, zoom: +m.getZoom().toFixed(2), neigung: Math.round(m.getPitch()) }; });
    fs.mkdirSync(path.dirname(aus), { recursive: true });
    await page.screenshot({ path: aus, type: "png" });
    const md5 = crypto.createHash("md5").update(fs.readFileSync(aus)).digest("hex");
    console.log(`[${lang}] ${aus}\n  ${fs.statSync(aus).size} Byte, MD5 ${md5}`);
    console.log("  Vermerk:\n    " + vermerk.join("\n    "));
    console.log(`  Häuser im Bild: ${z.haeuser}, Zoom ${z.zoom}, Neigung ${z.neigung}`);
    console.log(`  Abrufe: ${zaehler.eigen} eigene, ${zaehler.grundkarte} Grundkarte (${ERLAUBT.join(", ") || "eigener Server"}), ${zaehler.leer} leer beantwortet; Seitenfehler ${fehler.length}`);
    if (!z.haeuser || fehler.length) { console.log("  BEFUND: keine Häuser im Bild oder Seitenfehler " + fehler.join(" | ")); rc = 1; }
    await ctx.close();
  }
} finally {
  await browser.close();
  server.close();
}
process.exitCode = rc;
