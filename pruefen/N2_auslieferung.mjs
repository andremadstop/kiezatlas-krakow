// Prüfung Auslieferung (Browser): Gebäude in 3D über den Entwicklungsserver und über eine Deploy-Kopie, Kopfleiste
// in allen Breiten. Ohne Netz; fremde Abrufe werden abgefangen und zählen als Befund.
//
//   1. 3D über skripte/entwicklung_server.mjs (daten/gebaeude/ aus $KIEZ_DATEN/abgeleitet/gebaeude/<Stand>/):
//      Seiten mit Knopf „3D“ (planer, kamienice, modernizacja) in pl, en, de bei 1440 und 390 px: vor dem Knopf keine
//      Gebäudedatei angefragt; nach dem Knopf Zoom ≥ 14,5, Gebäude geladen und gezeichnet; keine Konsolenfehler,
//      keine Fehlabrufe.
//   2. Dasselbe in einer Deploy-Kopie (skripte/deploy_kopie.py, verkleinertes JavaScript mit ?v=), wenn --deploy
//      ORDNER angegeben ist, bei 1440 px; dazu je Sprache die Startseite mit Grundkarte (Kacheln aus der Kopie).
//   3. Kopfleiste: alle 18 Seiten in pl, en, de bei 1440, 390 und 360 px: jeder Link der Haupt-, Unter- und
//      Sprachnavigation liegt ganz im Bild und in der Kopfleiste, kein seitlicher Überstand der Seite; kein
//      sichtbarer Luftbild-Schalter (Kraków hat kein Luftbild).
//   4. Kerning der polnischen Sonderzeichen im Textsatz des Browsers (skripte/schriften.py überträgt die Werte der
//      Grundbuchstaben): je Schrift und Schnitt aus basis.css ist der Kerning-Betrag eines Paars mit Sonderzeichen
//      (Breite des Paars minus Breite der Einzelzeichen, 1000 px Schriftgrad, lang="pl") gleich dem des Grundpaars,
//      und das Grundpaar kernt (Betrag ungleich 0).
//
//   0. Entwicklungsserver ohne Browser: .env, .git/, node_modules/, Skripte, Belege, Verträge und Pfade mit einem
//      Teil, der mit einem Punkt beginnt, geben 404; Seiten, Skripte, Daten und Texte 200; ein fremder Host-Kopf
//      gibt 403 (DNS-Rebinding). Ausgegeben werden nur Statuscodes.
//
// Aufruf: node pruefen/N2_auslieferung.mjs [--deploy <Deploy-Kopie>] [--nur server|3d|kopf|kerning]
// Rückgabe 0 = grün, 1 = Befund.
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { starten, gebaeudeordner } from "../skripte/entwicklung_server.mjs";

const WURZEL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const DEPLOY = arg("--deploy", null), NUR = arg("--nur", null);
const SPRACHEN = [["pl", ""], ["en", "en/"], ["de", "de/"]];
const SEITEN_3D = ["planer", "kamienice", "modernizacja"];
const ORT = JSON.parse(/window\.KIEZ_ORT=(\{.*\});/.exec(fs.readFileSync(path.join(WURZEL, "daten", "ort.js"), "utf8"))[1]);
const TYP = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml",
  ".png": "image/png", ".woff2": "font/woff2", ".json": "application/json", ".pbf": "application/x-protobuf" };

const befunde = [];
let uebersprungen = 0;
function pruef(ok, text) { console.log((ok ? "  ok    " : "  FEHLT ") + text); if (!ok) befunde.push(text); return ok; }
function ueber(text) { console.log("  übersprungen  " + text); uebersprungen++; }

// statischer Server für die Deploy-Kopie: nur Dateien darunter, Abfrage (?v=) wird ignoriert wie vom Webserver
function deployServer(wurzel) {
  const s = http.createServer((q, a) => {
    let rel = decodeURIComponent(new URL(q.url, "http://x").pathname);
    if (rel.endsWith("/")) rel += "index.html";
    const p = path.normalize(path.join(wurzel, rel));
    if (!p.startsWith(wurzel + path.sep)) { a.writeHead(403); a.end(); return; }
    fs.readFile(p, (f, b) => { if (f) { a.writeHead(404); a.end(); return; } a.writeHead(200, { "content-type": TYP[path.extname(p)] || "application/octet-stream" }); a.end(b); });
  });
  return new Promise((r) => s.listen(0, "127.0.0.1", () => r({ server: s, url: `http://127.0.0.1:${s.address().port}/` })));
}

const browser = await chromium.launch();

async function oeffnen(basis, rel, breite, mitKarte = true) {
  const ctx = await browser.newContext({ viewport: { width: breite, height: breite < 600 ? 844 : 900 }, reducedMotion: "reduce", locale: "pl-PL" });
  const page = await ctx.newPage();
  const fehler = [], fremd = [], abrufe = [];
  page.on("console", (m) => { if (m.type() === "error") fehler.push("Konsole: " + m.text()); });
  page.on("pageerror", (e) => fehler.push("Seitenfehler: " + e.message));
  page.on("requestfailed", (r) => fehler.push("nicht geladen: " + r.url().replace(basis, "")));
  page.on("response", (r) => { if (r.status() >= 400) fehler.push(`HTTP ${r.status()}: ${r.url().replace(basis, "")}`); });
  page.on("request", (r) => abrufe.push(r.url().replace(basis, "")));
  await page.route("**/*", (r) => { const u = r.request().url(); if (u.startsWith(basis) || u.startsWith("data:") || u.startsWith("blob:")) return r.continue(); fremd.push(u); return r.fulfill({ status: 204, body: "" }); });
  await page.goto(basis + rel, { waitUntil: "load" });
  if (mitKarte) {
    await page.waitForFunction(() => window.KIEZ_KARTE && window.KIEZ_KARTE.loaded(), null, { timeout: 30000 }).catch(() => {});
    await page.waitForFunction(() => window.KIEZ_BEREIT === true, null, { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(300);
  }
  return { ctx, page, fehler, fremd, abrufe };
}
function sauber(s, was) {
  pruef(!s.fehler.length && !s.fremd.length, `${was}: keine Konsolenfehler, Fehlabrufe oder Fremdabrufe${s.fehler.length ? ": " + s.fehler.slice(0, 3).join("; ") : ""}${s.fremd.length ? " fremd: " + s.fremd.slice(0, 2).join(" ") : ""}`);
}

async function dreiD(basis, wo, rel, breite) {
  const was = `${wo} ${rel} ${breite} px`;
  const s = await oeffnen(basis, rel, breite);
  const { page } = s;
  pruef(!s.abrufe.some((u) => u.includes("daten/gebaeude/")), `${was}: vor dem Knopf keine Gebäudedatei angefragt`);
  await page.evaluate((z) => window.KIEZ_KARTE.jumpTo({ center: z, zoom: 12 }), ORT.karte.haus_ziel);
  await page.waitForTimeout(300);
  const knopf = await page.evaluateHandle(() => [...document.querySelectorAll("button")].find((b) => b.textContent.trim() === window.KIEZ_I18N.t("planer.ks_3d")));
  if (!pruef(!!(await knopf.evaluate((b) => !!b)), `${was}: Knopf „${await page.evaluate(() => window.KIEZ_I18N.t("planer.ks_3d"))}“ vorhanden`)) { await s.ctx.close(); return; }
  await knopf.asElement().click();
  await page.waitForFunction(() => { const m = window.KIEZ_KARTE, q = m.getSource("geb3d"); return m.getZoom() >= 14.5 && q && q._data && q._data.features && q._data.features.length > 0; }, null, { timeout: 60000 }).catch(() => {});
  await page.waitForFunction(() => !window.KIEZ_KARTE.isMoving(), null, { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(800);
  const r = await page.evaluate(() => {
    const m = window.KIEZ_KARTE, q = m.getSource("geb3d");
    return { zoom: m.getZoom(), geladen: q && q._data && q._data.features ? q._data.features.length : 0,
      gezeichnet: m.getLayer("geb3d") ? m.queryRenderedFeatures({ layers: ["geb3d"] }).length : 0 };
  });
  const dateien = [...new Set(s.abrufe.filter((u) => u.includes("daten/gebaeude/")).map((u) => u.split("?")[0].split("/").pop()))];
  pruef(r.zoom >= 14.5 && r.geladen > 0 && r.gezeichnet > 0 && dateien.length > 0 && dateien.length <= 3,
    `${was}: nach dem Knopf Zoom ${r.zoom.toFixed(2)}, ${r.geladen} Gebäude geladen, ${r.gezeichnet} gezeichnet, Dateien ${dateien.join(" ")}`);
  sauber(s, was);
  await s.ctx.close();
}

async function kopf(basis, rel, breite) {
  const was = `Kopfleiste ${rel} ${breite} px`;
  const s = await oeffnen(basis, rel, breite, false);
  await s.page.waitForTimeout(150);
  const r = await s.page.evaluate(() => {
    const vw = document.documentElement.clientWidth, k = document.querySelector(".kopfleiste").getBoundingClientRect();
    const links = [...document.querySelectorAll(".kopfleiste nav a")];
    const raus = links.filter((e) => {
      const r = e.getBoundingClientRect(), n = e.closest("nav").getBoundingClientRect();
      return !(r.width > 0 && r.left >= Math.max(0, n.left) - 0.5 && r.right <= Math.min(vw, n.right) + 0.5 && r.top >= k.top - 0.5 && r.bottom <= k.bottom + 0.5);
    }).map((e) => e.textContent.trim());
    // kein Luftbild-Schalter (Kraków hat kein Luftbild, KIEZ_THEMEN.LUFTBILD ist false)
    const luft = [...document.querySelectorAll("button, label, [role=switch], input")].filter((e) => e.offsetParent && /luftbild|ortofoto|aerial|orthophoto/i.test(e.textContent + " " + (e.getAttribute("aria-label") || "") + " " + (e.title || ""))).length;
    return { n: links.length, raus, ueber: document.documentElement.scrollWidth - vw, luft, LB: window.KIEZ_THEMEN ? window.KIEZ_THEMEN.LUFTBILD : null };
  });
  pruef(r.n > 0 && !r.raus.length && r.ueber <= 0 && !r.luft && r.LB !== true, `${was}: ${r.n} Links ganz sichtbar${r.raus.length ? ", abgeschnitten: " + r.raus.join(", ") : ""}, Überstand ${r.ueber} px, Luftbild-Schalter ${r.luft} (LUFTBILD ${r.LB})`);
  sauber(s, was);
  await s.ctx.close();
}

const dev = await starten({});
console.log(`Entwicklungsserver: ${dev.gebaeude_dateien} 3D-Dateien im Manifest von abgeleitet/gebaeude/${path.basename(gebaeudeordner())}`);

// Freigabeliste und Host-Kopf des Entwicklungsservers (ohne Browser; ausgegeben werden nur Statuscodes, nie Inhalte)
function status(pfad, host) {
  const u = new URL(dev.url);
  return new Promise((r) => {
    const q = http.request({ host: "127.0.0.1", port: u.port, path: pfad, method: "HEAD", headers: { host: host || u.host } }, (a) => { a.resume(); r(a.statusCode); });
    q.on("error", () => r(0));
    q.end();
  });
}
if (!NUR || NUR === "server") {
  console.log("\n0. Entwicklungsserver: nur ausgelieferte Dateien, nur eigener Host");
  const zu = ["/.env", "/.env.beispiel", "/.git/config", "/.git/HEAD", "/node_modules/.package-lock.json", "/package.json",
    "/docs/entscheidungen.md", "/skripte/abruf.py", "/pruefen.sh", "/config/krakow.yaml", "/daten/schema/mieszkania_odbl.json",
    "/daten/fixtures/", "/texte/pl/bloecke/", "/%2e%2e/%2e%2e/etc/passwd", "/daten/grundkarte/MANIFEST.sha256", "/belege/README.md"];
  const offen = ["/index.html", "/en/karta.html", "/atlas.js", "/daten/ort.js", "/texte/pl/kern.js", "/favicon.svg"];
  const z = await Promise.all(zu.map((p) => status(p))), o = await Promise.all(offen.map((p) => status(p)));
  pruef(z.every((c) => c === 404), `Server: nicht ausgelieferte Pfade geben 404 (${zu.map((p, i) => p + " " + z[i]).filter((_, i) => z[i] !== 404).join(", ") || "alle " + zu.length})`);
  pruef(o.every((c) => c === 200), `Server: Seiten, Skripte, Daten, Texte geben 200 (${offen.map((p, i) => p + " " + o[i]).join(", ")})`);
  const fremd = await status("/index.html", `rebind.example:${new URL(dev.url).port}`), lh = await status("/index.html", `localhost:${new URL(dev.url).port}`);
  pruef(fremd === 403 && lh === 200, `Server: fremder Host-Kopf 403 (ist ${fremd}), localhost 200 (ist ${lh})`);
}

if (!NUR || NUR === "3d") {
  console.log("\n1. 3D über den Entwicklungsserver");
  if (!dev.gebaeude_dateien && !dev.gebaeude_abweichend) ueber("3D: kein Gebäudeordner mit Manifest");
  else pruef(!dev.gebaeude_abweichend, `Entwicklungsserver: alle 3D-Dateien passen zum Manifest (SHA256), ${dev.gebaeude_abweichend} abweichend`);
  if (dev.gebaeude_dateien) for (const [, pre] of SPRACHEN) for (const seite of SEITEN_3D) for (const b of [1440, 390]) await dreiD(dev.url, "Entwicklung", `${pre}${seite}.html`, b);

  console.log("\n2. Deploy-Kopie");
  if (!DEPLOY) ueber("Deploy-Kopie: --deploy nicht angegeben");
  else {
    const wurzel = path.resolve(DEPLOY);
    const dep = await deployServer(wurzel);
    const ks = fs.readFileSync(path.join(wurzel, "kartenseite.js"), "utf8");
    pruef(!ks.includes("\n  ") && ks.length < fs.readFileSync(path.join(WURZEL, "kartenseite.js"), "utf8").length, "Deploy-Kopie: kartenseite.js verkleinert");
    pruef(fs.readdirSync(path.join(wurzel, "daten", "gebaeude")).length === ORT.gliederung.teile.length, `Deploy-Kopie: ${ORT.gliederung.teile.length} Dateien unter daten/gebaeude/`);
    for (const [, pre] of SPRACHEN) {
      for (const seite of SEITEN_3D) await dreiD(dep.url, "Deploy", `${pre}${seite}.html`, 1440);
      const s = await oeffnen(dep.url, `${pre}index.html`, 1440);
      const kacheln = s.abrufe.filter((u) => u.includes("daten/grundkarte/kacheln/")).length;
      pruef(kacheln > 0, `Deploy ${pre}index.html: Grundkarte aus der Kopie (${kacheln} Kacheln abgerufen)`);
      sauber(s, `Deploy ${pre}index.html`);
      await s.ctx.close();
    }
    dep.server.close();
  }
}

if (!NUR || NUR === "kopf") {
  console.log("\n3. Kopfleiste");
  for (const [, pre] of SPRACHEN) for (const seite of ORT.seiten) for (const b of [1440, 390, 360]) await kopf(dev.url, `${pre}${seite}.html`, b);
}

if (!NUR || NUR === "kerning") {
  console.log("\n4. Kerning der polnischen Sonderzeichen im Browser");
  const PAARE = [["ŁT", "LT"], ["WĄ", "WA"], ["VĄ", "VA"], ["YĄ", "YA"], ["ĄY", "AY"], ["ĄT", "AT"], ["Tę", "Te"], ["Tć", "Tc"],
    ["Tą", "Ta"], ["Tś", "Ts"], ["Tź", "Tz"], ["Tż", "Tz"], ["Tń", "Tn"], ["Fą", "Fa"], ["ŁY", "LY"], ["ŁV", "LV"], ["ŁW", "LW"],
    ["WĄWÓZ".slice(0, 2), "WA"], ["Ł’", "L’"], ["ŻY", "ZY"]];
  const SCHNITTE = [["Barlow", 400], ["Barlow", 500], ["Barlow", 600], ["Barlow Semi Condensed", 500], ["Barlow Semi Condensed", 600]];
  const s = await oeffnen(dev.url, "index.html", 1440, false);
  for (const [fam, gew] of SCHNITTE) {
    const r = await s.page.evaluate(async ({ fam, gew, PAARE }) => {
      await document.fonts.load(`${gew} 100px "${fam}"`, "ŁĄąęŻ");
      const sp = document.createElement("span");
      sp.lang = "pl"; sp.style.cssText = `position:absolute;left:0;top:0;white-space:pre;font:${gew} 1000px "${fam}";font-kerning:normal;font-feature-settings:normal;letter-spacing:0`;
      document.body.appendChild(sp);
      const b = (x) => { sp.textContent = x; return sp.getBoundingClientRect().width; };
      const kern = (p) => b(p) - b(p[0]) - b(p[1]);
      const aus = PAARE.map(([pl, g]) => ({ pl, g, kpl: kern(pl), kg: kern(g) }));
      sp.remove();
      return { geladen: document.fonts.check(`${gew} 100px "${fam}"`, "Ł"), aus };
    }, { fam, gew, PAARE });
    const falsch = r.aus.filter((x) => Math.abs(x.kpl - x.kg) > 0.5);
    const ohne = r.aus.filter((x) => Math.abs(x.kg) < 0.5);
    pruef(r.geladen && !falsch.length, `${fam} ${gew}: ${r.aus.length} Paare kernen wie ihr Grundpaar (Schrift geladen: ${r.geladen})` +
      (falsch.length ? ", abweichend: " + falsch.map((x) => `${x.pl} ${x.kpl.toFixed(1)} statt ${x.kg.toFixed(1)}`).join(", ") : "") +
      `; Beispiel ŁT ${r.aus[0].kpl.toFixed(1)} px = LT ${r.aus[0].kg.toFixed(1)} px bei 1000 px` +
      (ohne.length ? `; Grundpaar ohne Kerning (nur Hinweis): ${ohne.map((x) => x.g).join(" ")}` : ""));
  }
  sauber(s, "Kerning-Messung index.html");
  await s.ctx.close();
}

await browser.close();
dev.server.close();
console.log(`\n${befunde.length ? befunde.length + " Befund(e)" : "0 Befunde"}, ${uebersprungen} übersprungen`);
process.exit(befunde.length ? 1 : 0);
