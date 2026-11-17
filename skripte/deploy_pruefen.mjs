// Prüfung einer Deploy-Kopie (skripte/deploy_kopie.py) vor dem Upload, ohne Netz.
//
// Zwei Arten:
//   node skripte/deploy_pruefen.mjs --kopie <ordner>
//       Abnahme der Kopie: Pfad unter kiezatlas-deploy/krakow/, keine Verknüpfungen, MD5SUMS vollständig und
//       stimmig; jede Seite in jeder Sprache mit KIEZ_V, Stand und ?v= an jedem lokalen Verweis auf eine Datei, kein
//       Verweis ins Leere. Dann im Browser über einen eigenen Server auf 127.0.0.1, der die Kopie wie live unter dem
//       Pfad aus basis_url (daten/ort.js) ausliefert und für fehlende Adressen die 404-Seite der Sprache mit Status 404
//       schickt (so wie der nginx-Vorschlag in docs/auslieferung.md): jede Seite ohne Seitenfehler und
//       Konsolenfehler, jede eigene Datei mit Status 200 und ?v=, auch tiefe Fehladressen mit vollständig geladener
//       404-Seite. Zum Schluss das Startgewicht je Seite.
//   node skripte/deploy_pruefen.mjs --gewicht <wurzel> --seite planer.html [--seite …] [--verkleinert] [--json datei]
//       nur das Startgewicht beliebiger Seiten einer Wurzel (für die Messung der verkleinerten Auslieferung);
//       --verkleinert liefert das eigene JavaScript (Wurzel *.js, texte/**/*.js) so aus, wie deploy_kopie.py es
//       verkleinert (gleiche esbuild-Einstellungen).
//
// Startgewicht: alle JavaScript-Dateien, die die Seite bis zur Ruhe lädt (load, dann window.KIEZ_BEREIT, falls die
// Seite es setzt, dann keine offenen Abrufe), je Datei einmal. Drei Werte in Byte:
//   gz9   gzip -9 je Datei, Summe (Rechenweg der Potsdamer Prüfung A7_planer.mjs, dort in KB gerundet)
//   live  wie der Webserver mit dem Vorschlag in docs/auslieferung.md ausliefert: gzip Stufe 9 ab 1024 Byte,
//         kleinere Dateien ungepackt (gzip_comp_level 9 im Block /kiezatlas/krakow/, gzip_min_length 1024)
//   heute wie die heutige nginx-Konfiguration von souverain-systems.de (gzip_comp_level 6), nur zur Auskunft
//   roh   ungepackt
// Fremde Adressen beantwortet der Prüfbrowser leer (gezählt). Rückgabe 0 = grün, 1 = Befund.
import { chromium } from "playwright";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import crypto from "node:crypto";
import vm from "node:vm";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const esbuild = createRequire(import.meta.url)(path.join(REPO, "node_modules", "esbuild"));
// dieselben Einstellungen wie ESBUILD_JS in skripte/deploy_kopie.py; die Abnahme einer Kopie prüft, dass jede
// verkleinerte Datei genau esbuild(Quelle) mit diesen Einstellungen ist
const VERKLEINERN = { loader: "js", minify: true, legalComments: "inline", charset: "utf8" };
const eigenerCode = (rel) => rel.endsWith(".js") && (!rel.includes("/") || rel.startsWith("texte/"));

const arg = (n) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : null; };
const alle = (n) => process.argv.flatMap((a, i) => (a === n ? [process.argv[i + 1]] : []));
const GRENZE_PLANER = 320 * 1024;   // Auflage KR10: Startgewicht des Planers unter 320 KB gz
const GRENZE_SEITE = 300 * 1024;    // Bauvorlage: Startseite je Sprache unter 300 KB gz (alles, was sie lädt)
const befunde = [];
function pruef(ok, text) { console.log((ok ? "  ok   " : "  FEHLT ") + text); if (!ok) befunde.push(text); return ok; }

const TYP = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".png": "image/png",
  ".woff2": "font/woff2", ".json": "application/json", ".md": "text/plain; charset=utf-8", ".txt": "text/plain; charset=utf-8" };
const gz9 = (b) => zlib.gzipSync(b, { level: 9 }).length;
const live = (b) => (b.length < 1024 ? b.length : zlib.gzipSync(b, { level: 9 }).length);
const heute = (b) => (b.length < 1024 ? b.length : zlib.gzipSync(b, { level: 6 }).length);

// Server: Wurzel unter einem Pfad; fehlt eine Datei, die 404-Seite der Sprache (erster Ordner nach dem Pfad).
function server(wurzel, praefix, sprachen, klein = false) {
  const s = http.createServer((q, a) => {
    const u = decodeURIComponent(new URL(q.url, "http://x").pathname);
    const schick = (p, status) => fs.readFile(p, (f, d) => {
      if (f) { a.writeHead(500); a.end(); return; }
      if (klein && eigenerCode(path.relative(wurzel, p).split(path.sep).join("/"))) d = Buffer.from(esbuild.transformSync(d.toString("utf8"), VERKLEINERN).code);
      a.writeHead(status, { "content-type": TYP[path.extname(p)] || "application/octet-stream" }); a.end(d);
    });
    if (!u.startsWith(praefix)) { a.writeHead(404); a.end(); return; }
    let rel = u.slice(praefix.length);
    if (rel === "" || rel.endsWith("/")) rel += "index.html";
    const p = path.normalize(path.join(wurzel, rel));
    if (p !== wurzel && !p.startsWith(wurzel + path.sep)) { a.writeHead(403); a.end(); return; }
    if (fs.existsSync(p) && fs.statSync(p).isFile()) return schick(p, 200);
    if (!sprachen) { a.writeHead(404); a.end(); return; }
    const erster = rel.split("/")[0];
    const lang = sprachen.slice(1).includes(erster) ? erster : null;
    schick(path.join(wurzel, lang ? `${lang}/404.html` : "404.html"), 404);
  });
  return new Promise((r) => s.listen(0, "127.0.0.1", () => r(s)));
}

async function oeffnen(browser, basis, url) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" });
  const page = await ctx.newPage();
  const fehler = [], eigen = [], fremd = [];
  page.on("pageerror", (e) => fehler.push("Seitenfehler: " + e.message));
  page.on("console", (m) => { if (m.type() === "error" && !/status of 404/.test(m.text())) fehler.push("Konsole: " + m.text()); });
  page.on("response", (r) => { if (r.url().startsWith(basis)) eigen.push({ url: r.url(), status: r.status() }); });
  await page.route("**/*", (r) => {
    const u = r.request().url();
    if (u.startsWith(basis) || /^(data|blob):/.test(u)) return r.continue();
    fremd.push(u);
    return r.fulfill(/\.pbf(\?|$)/.test(u) ? { status: 200, contentType: "application/x-protobuf", body: Buffer.alloc(0) } : { status: 204, body: "" });
  });
  const antwort = await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => window.KIEZ_BEREIT === undefined || window.KIEZ_BEREIT === true, null, { timeout: 90000 }).catch(() => fehler.push("KIEZ_BEREIT kam nicht"));
  await page.waitForLoadState("networkidle").catch(() => {});
  await page.waitForTimeout(300);
  return { ctx, page, fehler, eigen, fremd, status: antwort.status() };
}

let KLEIN = false;   // --gewicht … --verkleinert: Gewicht der Dateien, wie der Server sie verkleinert ausliefert
const klein = (rel, b) => (KLEIN && eigenerCode(rel) ? Buffer.from(esbuild.transformSync(b.toString("utf8"), VERKLEINERN).code) : b);
function gewicht(wurzel, basis, eigen) {
  const js = [...new Set(eigen.map((e) => e.url.split("?")[0]).filter((u) => u.endsWith(".js")))];
  const w = { dateien: js.length, gz9: 0, live: 0, heute: 0, roh: 0, liste: [], alles_live: 0 };
  for (const u of new Set(eigen.filter((e) => e.status === 200).map((e) => e.url.split("?")[0]))) {
    const rel = decodeURIComponent(u.slice(basis.length)), p = path.join(wurzel, rel);
    if (fs.existsSync(p) && fs.statSync(p).isFile()) w.alles_live += live(klein(rel, fs.readFileSync(p)));
  }
  for (const u of js) {
    const rel = decodeURIComponent(u.slice(basis.length)), p = path.join(wurzel, rel);
    if (!fs.existsSync(p)) continue;
    const b = klein(rel, fs.readFileSync(p));
    w.gz9 += gz9(b); w.live += live(b); w.heute += heute(b); w.roh += b.length; w.liste.push(u.slice(basis.length));
  }
  return w;
}
const kb = (n) => `${n} Byte (${(n / 1024).toFixed(1)} KB)`;

// ---------------------------------------------------------------- nur Gewicht
if (arg("--gewicht")) {
  const wurzel = path.resolve(arg("--gewicht"));
  KLEIN = process.argv.includes("--verkleinert");
  console.log(`Wurzel ${wurzel}${KLEIN ? `, eigenes JavaScript beim Ausliefern verkleinert (esbuild ${esbuild.version})` : ""}`);
  const srv = await server(wurzel, "/", null, KLEIN);
  const basis = `http://127.0.0.1:${srv.address().port}/`;
  const browser = await chromium.launch();
  const ergebnis = [];
  try {
    for (const s of alle("--seite")) {
      const o = await oeffnen(browser, basis, basis + s);
      const w = gewicht(wurzel, basis, o.eigen);
      console.log(`${s}: Status ${o.status}, ${w.dateien} JS-Dateien, gz9 ${kb(w.gz9)}, live ${kb(w.live)}, heute (Stufe 6) ${kb(w.heute)}, roh ${kb(w.roh)}; alle eigenen Dateien live ${kb(w.alles_live)}; ${o.fremd.length} fremde Abrufe leer beantwortet`);
      console.log("  geladen: " + w.liste.join(", "));
      if (o.fehler.length) console.log("  Fehler: " + o.fehler.join(" | "));
      pruef(o.status === 200 && !o.fehler.length, `${s} ohne Seitenfehler und Konsolenfehler`);
      ergebnis.push({ seite: s, ...w, fehler: o.fehler, fremd: o.fremd.length });
      await o.ctx.close();
    }
  } finally { await browser.close(); srv.close(); }
  const aus = arg("--json");
  if (aus) fs.writeFileSync(aus, JSON.stringify({ wurzel, stand: new Date().toISOString(), ergebnis }, null, 1));
  process.exit(befunde.length ? 1 : 0);
}

// ---------------------------------------------------------------- Abnahme einer Kopie
const KOPIE = path.resolve(arg("--kopie") || "");
if (!arg("--kopie") || !fs.existsSync(path.join(KOPIE, "MD5SUMS"))) { console.log("Aufruf: --kopie <ordner mit MD5SUMS> | --gewicht <wurzel> --seite …"); process.exit(2); }
const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(KOPIE, "daten", "ort.js"), "utf8"), sandbox);
const ORT = sandbox.window.KIEZ_ORT;
const PRAEFIX = new URL(ORT.basis_url).pathname;
console.log(`Deploy-Kopie ${KOPIE}\n  Pfad live: ${PRAEFIX}, Sprachen ${ORT.sprachen.join(", ")}`);

console.log("\nOrt und Dateien");
const teile = KOPIE.split(path.sep);
pruef(teile.at(-2) === "krakow" && teile.at(-3) === "kiezatlas-deploy", `Kopie liegt unter kiezatlas-deploy/krakow/ (${teile.slice(-3).join("/")})`);
const dateien = [], links = [];
(function lauf(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isSymbolicLink()) links.push(p); else if (e.isDirectory()) lauf(p); else dateien.push(path.relative(KOPIE, p).split(path.sep).join("/"));
  }
})(KOPIE);
pruef(!links.length, `keine Verknüpfungen in der Kopie (${links.length})`);
const md5 = new Map(fs.readFileSync(path.join(KOPIE, "MD5SUMS"), "utf8").trim().split("\n").map((z) => { const i = z.indexOf("  "); return [z.slice(i + 2), z.slice(0, i)]; }));
const ohneMd5 = dateien.filter((d) => d !== "MD5SUMS" && !md5.has(d)), fehlt = [...md5.keys()].filter((d) => !dateien.includes(d));
const falsch = [...md5].filter(([d, h]) => dateien.includes(d) && crypto.createHash("md5").update(fs.readFileSync(path.join(KOPIE, d))).digest("hex") !== h);
pruef(!ohneMd5.length && !fehlt.length && !falsch.length, `MD5SUMS: ${md5.size} Einträge, ohne Eintrag ${ohneMd5.length}, fehlend ${fehlt.length}, abweichend ${falsch.length} ${[...ohneMd5, ...fehlt, ...falsch.map((f) => f[0])].slice(0, 5).join(" ")}`);
pruef([...md5.keys()].every((d) => !d.startsWith("/") && !d.split("/").includes("..")), "alle Pfade in MD5SUMS relativ und ohne ..");

const verkleinert = [...md5.keys()].filter(eigenerCode), nichtEsbuild = verkleinert.filter((d) => !fs.existsSync(path.join(REPO, d))
  || esbuild.transformSync(fs.readFileSync(path.join(REPO, d), "utf8"), VERKLEINERN).code !== fs.readFileSync(path.join(KOPIE, d), "utf8"));
pruef(verkleinert.length > 0 && !nichtEsbuild.length, `${verkleinert.length} JavaScript-Dateien des eigenen Codes sind genau esbuild ${esbuild.version}(Quelle in ${REPO}) ${nichtEsbuild.slice(0, 3).join(" ")}`);

console.log("\nSeiten (statisch)");
const seiten = ORT.sprachen.flatMap((l, i) => ORT.seiten.map((s) => (i === 0 ? "" : l + "/") + s + ".html"));
const fehltSeite = seiten.filter((s) => !dateien.includes(s));
pruef(!fehltSeite.length, `${seiten.length} Seiten (${ORT.seiten.length} je Sprache) vorhanden ${fehltSeite.join(" ")}`);
const ENDUNG = /\.(js|css|svg|png|woff2|jpg|mp4)$/;
let ohneV = [], insLeere = [], ohneKiezV = [], ohneStand = [], v404 = [];
const stempel = new Set();
for (const s of seiten.filter((x) => dateien.includes(x))) {
  const t = fs.readFileSync(path.join(KOPIE, s), "utf8");
  const m = t.match(/<script>window\.KIEZ_V="(\d+)"<\/script>/);
  if (!m) ohneKiezV.push(s); else stempel.add(m[1]);
  const st = t.match(/<span data-kiez-version>([^<]*)<\/span>/);
  if (!st || !/^\d{4}-\d{2}-\d{2} \(.+\)$/.test(st[1])) ohneStand.push(s);
  const ist404 = s.endsWith("404.html");
  for (const [, ref] of t.matchAll(/(?:src|href|poster)="([^"]*)"/g)) {
    if (/^(#|[a-z]+:)/.test(ref) || ref === "") continue;
    const [p] = ref.split(/[?#]/);
    let rel;
    if (p.startsWith("/")) { if (!p.startsWith(PRAEFIX)) { insLeere.push(`${s}: ${ref}`); continue; } rel = p.slice(PRAEFIX.length); }
    else { if (ist404) v404.push(`${s}: ${ref}`); rel = path.posix.normalize(path.posix.join(path.posix.dirname(s), p)); }
    if (rel === "" || rel.endsWith("/")) rel += "index.html";
    if (rel.startsWith("..") || !dateien.includes(rel)) { insLeere.push(`${s}: ${ref}`); continue; }
    if ((ENDUNG.test(p) || rel.startsWith("daten/")) && !/\?v=\d+$/.test(ref)) ohneV.push(`${s}: ${ref}`);
  }
}
pruef(!ohneKiezV.length && stempel.size === 1, `KIEZ_V in jeder Seite, überall derselbe Wert (${[...stempel].join(", ")}) ${ohneKiezV.slice(0, 3).join(" ")}`);
pruef(!ohneStand.length, `Stand (Datum und Version) im Seitenfuß jeder Seite ${ohneStand.slice(0, 3).join(" ")}`);
pruef(!ohneV.length, `?v= an jedem lokalen Verweis auf eine Datei ${ohneV.slice(0, 3).join(" ")}`);
pruef(!insLeere.length, `kein lokaler Verweis ins Leere ${insLeere.slice(0, 3).join(" ")}`);
pruef(!v404.length, `404-Seiten verweisen nur ab der Domain (${PRAEFIX}…) ${v404.slice(0, 3).join(" ")}`);

console.log("\nIm Browser (Server auf 127.0.0.1, Pfad wie live)");
const srv = await server(KOPIE, PRAEFIX, ORT.sprachen);
const HOST = `http://127.0.0.1:${srv.address().port}`, BASIS = HOST + PRAEFIX;
const browser = await chromium.launch();
const bericht = { kopie: KOPIE, stand: new Date().toISOString(), seiten: [] };
try {
  for (const s of seiten) {
    const o = await oeffnen(browser, HOST + "/", BASIS + s);
    const kaputt = o.eigen.filter((e) => e.status !== 200 && e.url !== BASIS + s);
    const ohne = o.eigen.filter((e) => e.url !== BASIS + s && /\.(js|css|woff2|svg|png)(\?|$)/.test(e.url) && !/\?v=\d+/.test(e.url));
    const kiezV = await o.page.evaluate(() => window.KIEZ_V);
    const w = gewicht(KOPIE, BASIS, o.eigen.filter((e) => e.url.startsWith(BASIS)));
    bericht.seiten.push({ seite: s, status: o.status, ...w, fehler: o.fehler, fremd: o.fremd.length });
    pruef(o.status === 200 && !o.fehler.length && !kaputt.length && !ohne.length && kiezV === [...stempel][0],
      `${s}: ${o.eigen.length} eigene Abrufe, nicht 200: ${kaputt.length}, ohne ?v: ${ohne.length}, KIEZ_V ${kiezV}, Fehler ${o.fehler.length}${o.fehler.length ? " " + o.fehler[0] : ""}; JS gz9 ${w.gz9}, live ${w.live}`);
    await o.ctx.close();
  }
  console.log("\nFehladressen (404-Seite der Sprache, vollständig geladen)");
  const tief = [["gibt-es-nicht.html", ORT.sprachen[0]], ["a/b/c/gibt-es-nicht", ORT.sprachen[0]], ...ORT.sprachen.slice(1).flatMap((l) => [[`${l}/gibt-es-nicht.html`, l], [`${l}/x/y/z`, l]])];
  for (const [u, lang] of tief) {
    const o = await oeffnen(browser, HOST + "/", BASIS + u);
    const z = await o.page.evaluate(() => ({ lang: document.documentElement.lang, seite: document.body.dataset.seite,
      css: [...document.styleSheets].filter((x) => { try { return x.cssRules.length > 0; } catch { return false; } }).length,
      kopf: getComputedStyle(document.querySelector(".kopfleiste")).position }));
    const kaputt = o.eigen.filter((e) => e.status !== 200 && e.url !== BASIS + u);
    pruef(o.status === 404 && z.lang === lang && z.seite === "404" && z.css >= 2 && !kaputt.length && !o.fehler.length,
      `${PRAEFIX}${u}: Status ${o.status}, lang=${z.lang}, Stylesheets ${z.css}, Dateien nicht 200: ${kaputt.length}, Fehler ${o.fehler.length}`);
    await o.ctx.close();
  }
  // Nachgeladene Ebenen (kartenfeld.js lädt per Pfad ab der Wurzel): in jeder Sprache aus dem Wurzelordner daten/,
  // nicht aus <lang>/daten/ (Fehler bis 17.11.2026: ?v= am Verweis auf daten/ort.js verdeckte die Wurzel)
  console.log("\nNachgeladene Ebenen der Karte (je Sprache)");
  const NACH = [["spis:dichte", "daten/rejony.js"], ["klima:gruen_wald", "daten/klimat_zellen.js"], ["fuss:szkola", "daten/erreichbar_fuss_odbl.js"]];
  for (const l of ORT.sprachen) {
    const pre = l === ORT.sprachen[0] ? "" : l + "/";
    if (!seiten.includes(pre + "karta.html")) continue;
    for (const [thema, datei] of NACH) {
      if (!fs.existsSync(path.join(KOPIE, datei))) continue;
      const o = await oeffnen(browser, HOST + "/", BASIS + pre + "karta.html#thema=" + thema);
      await o.page.waitForFunction(() => !document.getElementById("ka-leg-zelle").hidden, null, { timeout: 20000 }).catch(() => {});
      const geladen = o.eigen.filter((e) => e.url.split("?")[0] === BASIS + datei && e.status === 200).length;
      const kaputt = o.eigen.filter((e) => e.status !== 200 && !e.url.startsWith(BASIS + pre + "karta.html"));
      const leg = await o.page.evaluate(() => !document.getElementById("ka-leg-zelle").hidden);
      pruef(geladen === 1 && !kaputt.length && leg && !o.fehler.length,
        `[${l}] karta #thema=${thema}: ${datei} aus der Wurzel geladen ${geladen}×, nicht 200: ${kaputt.length}${kaputt.length ? " " + kaputt[0].url : ""}, Legende ${leg ? "da" : "fehlt"}`);
      await o.ctx.close();
    }
  }
} finally { await browser.close(); srv.close(); }

console.log("\nStartgewicht (JavaScript bis zur Ruhe; gz9 = gzip -9 je Datei, live = Stufe 9 ab 1024 Byte, heute = Stufe 6)");
for (const l of ORT.sprachen) {
  const pre = l === ORT.sprachen[0] ? "" : l + "/";
  const planer = bericht.seiten.find((x) => x.seite === pre + "planer.html"), start = bericht.seiten.find((x) => x.seite === pre + "index.html");
  if (planer) pruef(Math.max(planer.gz9, planer.live) < GRENZE_PLANER, `[${l}] planer.html: gz9 ${kb(planer.gz9)}, live ${kb(planer.live)}, heute ${kb(planer.heute)} (Grenze ${GRENZE_PLANER / 1024} KB); ${planer.liste.join(", ")}`);
  if (start) pruef(start.alles_live < GRENZE_SEITE, `[${l}] index.html: alles, was die Seite lädt, live ${kb(start.alles_live)} (Grenze Startseite ${GRENZE_SEITE / 1024} KB), davon JS gz9 ${kb(start.gz9)}`);
}
const aus = arg("--json");
if (aus) fs.writeFileSync(aus, JSON.stringify(bericht, null, 1));
console.log(befunde.length ? `\n${befunde.length} Befund(e)` : "\ngrün");
process.exit(befunde.length ? 1 : 0);
