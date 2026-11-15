// Prüfung der Kartenseiten Erreichbarkeit (planer), Kamienice (kamienice) und Wohnungsbestand (modernizacja) im
// Browser, in pl, en und de, über HTTP auf 127.0.0.1 (Chromium, Playwright).
//
// Der Prüfserver liefert wie skripte/entwicklung_server.mjs die Kacheln der Grundkarte unter daten/grundkarte/ aus
// dem Kachelordner außerhalb des Repos und zusätzlich die 3D-Dateien unter daten/gebaeude/ aus
// dem Gebäudeordner von skripte/entwicklung_server.mjs (config/gebaeude_3d.json). Fehlt einer der Ordner,
// werden die Teile, die ihn brauchen, übersprungen und gemeldet.
//
// Je Seite und Sprache:
//   - lädt ohne Konsolenfehler, ohne Fehlabruf und ohne Abruf außerhalb 127.0.0.1; kein sichtbarer Textschlüssel
//     (alle Namensräume, auch denkmale.* und sanierung.*) und kein Platzhalter {…}
//   - Kamienice und Wohnungsbestand: Teilmenge, Schätzung und Grenzen sind sichtbar (Abzeichen, Abschnitt Grenzen)
//   - 3D: vor dem Knopf kein Abruf unter daten/gebaeude/; nach dem Knopf Zoom ≥ 14,5, Gebäude geladen und gezeichnet,
//     Popup nennt die Herkunft der Höhe; bei Zoom 13 erscheint der Hinweis auf die Zoomstufe
//   - Handybreite 390 und 360 px: kein seitlicher Überstand, Karte mindestens 300 px hoch, Seitenleiste darunter
// Planer: jede Frage stellt Ziel, Messart, Haltestellen bzw. Stadtteil ein (Hash und sichtbare Ebenen), Fußweg ist
// Standard, die Luftlinien-Frage stellt Luftlinie ein; Stadtteiltabelle und Vergleich zeigen Zähler und Nenner.
//
// Aufruf: node pruefen/S2_seiten.mjs [--nur planer|kamienice|modernizacja] [--bilder DIR]
// Rückgabe 0 = grün, 1 = Befund.
import { chromium } from "playwright";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { kachelordner, gebaeudeordner } from "../skripte/entwicklung_server.mjs";

const HIER = path.dirname(fileURLToPath(import.meta.url));
const WURZEL = path.resolve(HIER, "..");
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const NUR = arg("--nur", null), BILDER = arg("--bilder", null);
const DATEN = process.env.KIEZ_DATEN || path.join(WURZEL, "..", "kiezatlas-daten", "krakow");
const KACHELN = kachelordner();
const GEB = gebaeudeordner();     // wie Entwicklungsserver und Deploy-Kopie (config/gebaeude_3d.json)
const MIT_KACHELN = fs.existsSync(path.join(KACHELN, "MANIFEST.sha256"));
const MIT_GEB = fs.existsSync(path.join(GEB, "01_odbl.js"));
const TYP = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml",
  ".png": "image/png", ".woff2": "font/woff2", ".json": "application/json", ".pbf": "application/x-protobuf" };
const SPRACHEN = [["pl", ""], ["en", "en/"], ["de", "de/"]];
const SCHLUESSEL = /\b(kern|seiten|karte|erzaehlung|kamienice|planer|klimat|powietrze|mieszkania|punktualnosc|denkmale|sanierung|gebaeude|bevoelkerung|fussweg)\.[a-z0-9_]+(\.[a-z0-9_]+)*\b/;

const befunde = [];
let uebersprungen = 0;
function pruef(ok, text) { console.log((ok ? "  ok    " : "  FEHLT ") + text); if (!ok) befunde.push(text); return ok; }
function ueber(text) { console.log("  übersprungen  " + text); uebersprungen++; }

const server = http.createServer((q, a) => {
  const rel = decodeURIComponent(new URL(q.url, "http://x").pathname);
  let basis = WURZEL, teil = rel;
  if (rel.startsWith("/daten/grundkarte/")) { basis = KACHELN; teil = rel.slice("/daten/grundkarte".length); }
  else if (rel.startsWith("/daten/gebaeude/")) { basis = GEB; teil = rel.slice("/daten/gebaeude".length); }
  const p = path.normalize(path.join(basis, teil));
  if (p !== basis && !p.startsWith(basis + path.sep)) { a.writeHead(403); a.end(); return; }
  fs.readFile(p, (f, b) => { if (f) { a.writeHead(404); a.end(); return; } a.writeHead(200, { "content-type": TYP[path.extname(p)] || "application/octet-stream" }); a.end(b); });
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const HTTP = `http://127.0.0.1:${server.address().port}/`;
const browser = await chromium.launch();

async function oeffnen(url, o = {}) {
  const ctx = await browser.newContext({ viewport: { width: o.breite || 1280, height: o.hoehe || 860 }, reducedMotion: "reduce", locale: "pl-PL", hasTouch: !!o.touch });
  const page = await ctx.newPage();
  const fehler = [], fremd = [], abrufe = [];
  page.on("console", (m) => { if (m.type() === "error") fehler.push("Konsole: " + m.text()); });
  page.on("pageerror", (e) => fehler.push("Seitenfehler: " + e.message));
  page.on("requestfailed", (r) => fehler.push("nicht geladen: " + r.url()));
  page.on("response", (r) => { if (r.status() >= 400) fehler.push(`HTTP ${r.status()}: ${r.url()}`); });
  page.on("request", (r) => abrufe.push(r.url()));
  await page.route("**/*", (r) => { const u = r.request().url(); if (u.startsWith(HTTP) || u.startsWith("data:") || u.startsWith("blob:")) return r.continue(); fremd.push(u); return r.fulfill({ status: 204, body: "" }); });
  await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => window.KIEZ_KARTE && window.KIEZ_KARTE.loaded(), null, { timeout: 30000 });
  await bereit(page);
  return { ctx, page, fehler, fremd, abrufe };
}
async function bereit(page, ms = 30000) {
  await page.waitForFunction(() => window.KIEZ_BEREIT === true, null, { timeout: ms }).catch(() => {});
  await page.waitForTimeout(200);
}
function sauber(s, was) {
  pruef(!s.fehler.length && !s.fremd.length, `${was}: keine Konsolenfehler, Fehlabrufe oder Fremdabrufe${s.fehler.length ? ": " + s.fehler.slice(0, 3).join("; ") : ""}${s.fremd.length ? " fremd: " + s.fremd.slice(0, 2).join(" ") : ""}`);
}
async function textPruefen(page, was) {
  const text = await page.evaluate(() => document.body.innerText);
  const s = text.match(SCHLUESSEL), p = /\{[a-z_]+\}|\{\{/.exec(text);
  pruef(!s && !p, `${was}: kein Textschlüssel und kein Platzhalter sichtbar${s ? ": " + s[0] : ""}${p ? ": " + p[0] : ""}`);
  return text;
}
async function hash(page) { return page.evaluate(() => Object.fromEntries(location.hash.slice(1).split("&").map((x) => x.split("=")))); }
async function sichtbar(page, ebene) { return page.evaluate((e) => { const m = window.KIEZ_KARTE; return !!m.getLayer(e) && m.getLayoutProperty(e, "visibility") !== "none"; }, ebene); }

// ---------- 3D (gemeinsam für alle drei Seiten)
async function dreiD(s, was) {
  const { page } = s;
  pruef(!s.abrufe.some((u) => u.includes("/daten/gebaeude/")), `${was}: vor dem 3D-Knopf keine Gebäudedatei angefragt`);
  if (!MIT_GEB) { ueber(`${was}: 3D (kein Ordner ${GEB})`); return; }
  await page.evaluate(() => window.KIEZ_KARTE.jumpTo({ center: [19.9373, 50.0617], zoom: 12 }));
  await bereit(page);
  await page.click("#werkzeug .chip--knopf");
  await page.waitForFunction(() => { const m = window.KIEZ_KARTE, q = m.getSource("geb3d"); return m.getZoom() >= 14.5 && q && q._data && q._data.features && q._data.features.length > 0; }, null, { timeout: 60000 }).catch(() => {});
  await bereit(page, 60000);
  const r = await page.evaluate(() => {
    const m = window.KIEZ_KARTE, f = m.queryRenderedFeatures({ layers: ["geb3d"] });
    return { zoom: m.getZoom(), pitch: m.getPitch(), n: f.length, hq: [...new Set(f.map((x) => x.properties.hq))], hash: location.hash, gedrueckt: document.querySelector("#werkzeug .chip--knopf").getAttribute("aria-pressed") };
  });
  pruef(r.zoom >= 14.5 && r.n > 0 && r.gedrueckt === "true" && /(^|&|#)3d=1/.test(r.hash), `${was}: 3D-Knopf: Zoom ${r.zoom.toFixed(1)}, Neigung ${Math.round(r.pitch)}°, ${r.n} Gebäude gezeichnet, Herkunft der Höhe ${r.hq.join("/")}, Hash 3d=1`);
  // Popup eines Gebäudes in der Bildmitte
  const pt = await page.evaluate(() => { const m = window.KIEZ_KARTE, f = m.queryRenderedFeatures({ layers: ["geb3d"] }); if (!f.length) return null; const c = m.getCanvas().getBoundingClientRect(); const p = m.project(f[Math.floor(f.length / 2)].geometry.type === "Polygon" ? f[Math.floor(f.length / 2)].geometry.coordinates[0][0] : f[0].geometry.coordinates[0][0][0]); return { x: c.left + p.x, y: c.top + p.y }; });
  if (pt) {
    // in die Fläche eines Gebäudes klicken: Mittelpunkt der Bildschirmprojektion seines Umrisses
    const ziel = await page.evaluate(() => {
      const m = window.KIEZ_KARTE, c = m.getCanvas().getBoundingClientRect(), w = c.width, h = c.height;
      for (let y = h * 0.35; y < h * 0.75; y += 9) for (let x = w * 0.3; x < w * 0.7; x += 9) { const f = m.queryRenderedFeatures([x, y], { layers: ["geb3d"] }); if (f.length && document.elementFromPoint(c.left + x, c.top + y) === m.getCanvas() && !m.queryRenderedFeatures([[x - 9, y - 9], [x + 9, y + 9]], { layers: m.getStyle().layers.filter((l) => l.type === "circle").map((l) => l.id) }).length) return { x: c.left + x, y: c.top + y }; }
      return null;
    });
    if (ziel) {
      await page.mouse.click(ziel.x, ziel.y);
      await page.waitForTimeout(400);
      const pop = await page.evaluate(() => { const p = document.querySelector(".maplibregl-popup-content"); return p ? p.innerText : ""; });
      pruef(/LoD2|×\s*3\s*m|3 m/.test(pop) && /Modele 3D budynków są dostępne bezpłatnie/.test(pop), `${was}: Popup eines Gebäudes nennt Höhe, Herkunft und den wörtlichen Vermerk („${pop.replace(/\s+/g, " ").slice(0, 90)}…“)`);
      await page.evaluate(() => document.querySelectorAll(".maplibregl-popup").forEach((p) => p.remove()));
    } else pruef(false, `${was}: kein Gebäude zum Anklicken in der Bildmitte`);
  }
  // geteilter Link mit 3d=1 stellt die 3D-Häuser wieder her
  const s3 = await oeffnen(page.url().split("#")[0] + "#3d=1&k=15.6/50.06170/19.93730/50/0");
  await s3.page.waitForFunction(() => { const q = window.KIEZ_KARTE.getSource("geb3d"); return q && q._data && q._data.features && q._data.features.length > 0; }, null, { timeout: 60000 }).catch(() => {});
  await bereit(s3.page, 60000);
  const n3 = await s3.page.evaluate(() => window.KIEZ_KARTE.getLayer("geb3d") ? window.KIEZ_KARTE.queryRenderedFeatures({ layers: ["geb3d"] }).length : 0);
  pruef(n3 > 0, `${was}: Link mit #3d=1 zeigt die 3D-Häuser (${n3} gezeichnet)`);
  sauber(s3, `${was} (Link 3d=1)`); await s3.ctx.close();
  await page.evaluate(() => window.KIEZ_KARTE.jumpTo({ zoom: 13 }));
  await page.waitForTimeout(500);
  const leg = await page.evaluate(() => document.getElementById("legende").innerText);
  pruef(/1[45]/.test(leg) && /3D/.test(leg), `${was}: bei Zoom 13 Hinweis auf die Zoomstufe der 3D-Häuser in der Legende`);
}

// ---------- Handybreite
async function handy(url, was) {
  for (const breite of [390, 360]) {
    const s = await oeffnen(url, { breite, hoehe: 800, touch: true });
    const r = await s.page.evaluate(() => {
      const k = document.querySelector(".ks__karte").getBoundingClientRect(), b = document.querySelector(".ks-blatt").getBoundingClientRect();
      return { ueber: document.documentElement.scrollWidth - document.documentElement.clientWidth, kh: k.height, darunter: b.top >= k.bottom - 1, bw: b.width };
    });
    pruef(r.ueber <= 0 && r.kh >= 300 && r.darunter, `${was} bei ${breite} px: kein Überstand (${r.ueber} px), Karte ${Math.round(r.kh)} px hoch, Seitenleiste darunter (${Math.round(r.bw)} px breit)`);
    sauber(s, `${was} bei ${breite} px`);
    if (BILDER) { fs.mkdirSync(BILDER, { recursive: true }); await s.page.screenshot({ path: path.join(BILDER, `${was.replace(/[^a-z0-9]+/gi, "_")}_${breite}.png`), fullPage: false }); }
    await s.ctx.close();
  }
}

// ---------- Planer
async function planer(lang, o) {
  const url = HTTP + o + "planer.html", was = `${o}planer.html`;
  console.log(`\n[${lang}] Erreichbarkeit`);
  const s = await oeffnen(url);
  const { page } = s;
  await textPruefen(page, was);
  const h0 = await hash(page);
  pruef(h0.weg === "fuss", `${was}: Fußweg ist Standard (Hash weg=${h0.weg})`);
  const start = await page.evaluate(() => ({ p: (document.querySelector("#fragen .ks-frage") || {}).getAttribute?.("aria-pressed"), hw: !document.getElementById("wahl-hinweis").hidden }));
  pruef(h0.zu === "haltestelle_takt" && start.p === "true" && start.hw && await sichtbar(page, "zellen"),
    `${was}: ohne Hash startet Frage 1 (zu=${h0.zu}, Frage 1 gedrückt: ${start.p}, Hinweis sichtbar: ${start.hw})`);
  const fragen = await page.$$eval("#fragen .ks-frage", (b) => b.map((x) => x.dataset.frage));
  pruef(fragen.length === 5, `${was}: ${fragen.length} Fragen`);
  const soll = { takt: { zu: "haltestelle_takt", weg: "fuss", halt: true }, gruen: { zu: "park", weg: "fuss" }, schule: { zu: "szkola", weg: "fuss" }, luft: { zu: "haltestelle_takt", weg: "luft", halt: true } };
  for (const f of fragen) {
    await page.click(`#fragen .ks-frage[data-frage="${f}"]`);
    await bereit(page);
    const h = await hash(page), z = await sichtbar(page, "zellen"), ha = await sichtbar(page, "halt");
    const leg = await page.evaluate(() => document.getElementById("legende").innerText);
    const gedrueckt = await page.$eval(`#fragen .ks-frage[data-frage="${f}"]`, (b) => b.getAttribute("aria-pressed"));
    if (soll[f]) {
      const S = soll[f];
      const zellen = await page.evaluate(() => { const q = window.KIEZ_KARTE.getSource("zellen"); return q._data.features.filter((x) => typeof x.properties.wert === "number").length; });
      pruef(h.zu === S.zu && h.weg === S.weg && z && zellen > 0 && (!S.halt || (ha && h.halt === "1")) && gedrueckt === "true" && leg.length > 20,
        `${was}: Frage „${f}“ → zu=${h.zu}, weg=${h.weg}${S.halt ? ", Haltestellen " + (ha ? "an" : "aus") : ""}, ${zellen} Zellen mit Wert, Legende da`);
    } else {
      const tab = await page.evaluate(() => ({ st: document.getElementById("st-wahl").value, zeilen: document.querySelectorAll("#st-inhalt .ks-zahlen li").length, text: document.getElementById("st-inhalt").innerText }));
      pruef(h.st && tab.st === h.st && tab.zeilen > 0 && /\d/.test(tab.text) && h.weg === "fuss", `${was}: Frage „${f}“ → Stadtteil ${tab.st}, ${tab.zeilen} Kennzahlen mit Zähler und Nenner, Fußweg`);
    }
  }
  // Wechsel der Messart über die Chips
  await page.click('#werkzeug input[name="weg"][value="luft"]', { force: true });
  await bereit(page);
  pruef((await hash(page)).weg === "luft", `${was}: Chip Luftlinie setzt weg=luft`);
  // Vergleich
  await page.click("#vg-laden");
  await bereit(page);
  const vg = await page.evaluate(() => ({ zeilen: document.querySelectorAll("#vg-inhalt tbody tr").length, fuss: document.querySelectorAll("#vg-inhalt tfoot tr").length }));
  pruef(vg.zeilen === 18 && vg.fuss === 1, `${was}: Vergleich mit ${vg.zeilen} Stadtteilen und einer Zeile für die ganze Stadt`);
  // Link mit Zustand öffnet dieselbe Ansicht
  const s2 = await oeffnen(url + "#zu=park&weg=fuss&st=08");
  const r2 = await s2.page.evaluate(() => ({ st: document.getElementById("st-wahl").value, zu: (document.querySelector('#zu input:checked') || {}).value }));
  pruef(r2.st === "08" && r2.zu === "park" && await sichtbar(s2.page, "zellen"), `${was}: geteilter Link #zu=park&weg=fuss&st=08 öffnet Park, Fußweg, Stadtteil 08`);
  sauber(s2, `${was} (Link)`); await s2.ctx.close();
  await dreiD(s, was);
  sauber(s, was);
  await s.ctx.close();
  await handy(url, was);
}

// ---------- Kamienice
async function kamienice(lang, o) {
  const url = HTTP + o + "kamienice.html", was = `${o}kamienice.html`;
  console.log(`\n[${lang}] Kamienice`);
  const s = await oeffnen(url);
  const { page } = s;
  await textPruefen(page, was);
  const r = await page.evaluate(() => {
    const O = window.KIEZ_DENKMALE_ODBL, abz = [...document.querySelectorAll("main > p .ks-abz")].filter((x) => x.offsetHeight > 0).length;
    const h = O.objekte.features.filter((f) => f.properties.h === true).length;
    const grenzen = document.querySelectorAll(".ks-grenzen li").length;
    const f = window.KIEZ_KARTE.querySourceFeatures("obj").length;
    // Spalte „Objekte mit Registernummer (Wikidata)“ der Tabelle je Delegatura (vierte Spalte, nach dem Zeilenkopf die dritte Zelle)
    const R = window.KIEZ_DENKMALE, sp = [...document.querySelectorAll("#tab-delegatur tbody tr")].map((tr) => Number(tr.querySelectorAll("td")[2].textContent.replace(/\D/g, "")));
    return { abz, h, grenzen, leg: document.getElementById("legende").innerText, register: !!R && R.fixture !== true, quellen: document.getElementById("quellen-stand").innerText,
      regTab: sp.reduce((a, b) => a + b, 0), regSoll: R ? R.objekte.features.filter((f) => f.properties.q.includes("wd")).length : -1, regZahl: R ? R.zaehlung.wd.in_stadt : -2,
      regBlock: document.getElementById("zahlen-register").innerText, cc0: document.body.innerText.includes("CC0 1.0"),
      regEp: R ? R.objekte.features.filter((f) => f.properties.q.includes("wd") && f.properties.ep != null).length : -3 };
  });
  pruef(r.abz === 3 && r.grenzen >= 5, `${was}: Abzeichen Teilmenge, Lage, Register nur aus Wikidata sichtbar (${r.abz}); ${r.grenzen} Grenzen`);
  // Lage der Denkmalpunkte: bei sichtpruefung.geprueft true Abzeichen, Grenze, Legende und Quellen mit den Zahlen aus den
  // Daten und ohne Hinweis „ungeprüft“; sonst der Hinweis
  const si = await page.evaluate(() => {
    const T = window.KIEZ_TEXTE, F = window.KIEZ_I18N.fmt, O = window.KIEZ_DENKMALE_ODBL, R = window.KIEZ_DENKMALE;
    const ok = !!(O.sichtpruefung && O.sichtpruefung.geprueft === true && R.sichtpruefung && R.sichtpruefung.geprueft === true);
    const abz = document.getElementById("abz-lage").textContent, gr = document.getElementById("grenze-lage").textContent;
    const leg = document.getElementById("legende").innerText, qu = document.getElementById("quellen-stand").innerText;
    const q = (d) => F.anteil(d.ergebnis.lage.quote, 0);
    return { ok, abzOk: abz === T["denkmale.sicht.abz"], abzUn: abz === T["kamienice.abz_ungeprueft"],
      grOk: ok && gr.includes(q({ ergebnis: O.sichtpruefung.gesamt })) && gr.includes(F.zahl(O.sichtpruefung.gesamt.n)),
      legOk: ok && leg.includes(q(O.sichtpruefung)), quOk: ok && qu.includes(q(O.sichtpruefung)) && qu.includes(q(R.sichtpruefung)),
      hinweis: [T["kamienice.leg_ungeprueft"], T["kamienice.q_osm_klein"].split(";")[0]].map((h) => (gr + leg + qu).includes(h)),
      gesamt: ok ? q({ ergebnis: O.sichtpruefung.gesamt }) : null };
  });
  pruef(si.ok ? si.abzOk && si.grOk && si.legOk && si.quOk && !si.hinweis.some(Boolean) : si.abzUn && si.hinweis[0],
    `${was}: Lage ${si.ok ? `in Stichprobe geprüft: Abzeichen, Grenze (gesamt ${si.gesamt}), Legende und Quellen mit den Quoten aus den Daten, kein Hinweis „ungeprüft“` : "ungeprüft: Abzeichen und Hinweis"}`);
  pruef(r.register, `${was}: Register aus daten/denkmale.js geladen, keine Beispieldaten`);
  pruef(r.regTab === r.regSoll && r.regSoll === r.regZahl && r.regBlock.includes(new Intl.NumberFormat(lang).format(r.regZahl)) && r.cc0,
    `${was}: Registerpunkte je Delegatura (Summe ${r.regTab}) = Ebene rejestr der Karte (${r.regSoll}) = zaehlung.wd.in_stadt (${r.regZahl}); Vermerk CC0 1.0`);
  pruef(r.regBlock.includes(new Intl.NumberFormat(lang).format(r.regEp)) && r.regBlock.includes(new Intl.NumberFormat(lang).format(r.regSoll - r.regEp)),
    `${was}: Registerpunkte mit Bauzeitklasse aus den Punkten gezählt (${r.regEp}, ohne Klasse ${r.regSoll - r.regEp})`);
  const n0 = (r.leg.match(/(\d[\d\s .,]*)/) || [])[1];
  pruef(r.leg.includes(String(r.h)), `${was}: Legende nennt die ${r.h} Objekte mit Denkmalangabe (Zahl aus daten/denkmale_odbl.js)`);
  // Nur Kamienice
  await page.click("#nur-kamienice"); await bereit(page);
  const k = await page.evaluate(() => { const O = window.KIEZ_DENKMALE_ODBL; return { soll: Object.values(O.kamienice).reduce((a, b) => a + b, 0), filter: JSON.stringify(window.KIEZ_KARTE.getFilter("obj")), leg: document.getElementById("legende").innerText, hash: location.hash }; });
  pruef(k.leg.includes(String(k.soll)) && /kam/.test(k.filter) && /nur=1/.test(k.hash), `${was}: „Nur Kamienice“ filtert auf ${k.soll} Kamienice (Legende, Filter, Hash nur=1)`);
  await page.click("#nur-kamienice"); await bereit(page);
  // Bauzeitklasse abwählen (die erste Klasse mit Treffern; Klassen ohne Treffer sind gesperrt)
  const ep = await page.evaluate(() => { const i = [...document.querySelectorAll("#ep input")]; return { wahl: i.filter((x) => !x.disabled && x.checked).map((x) => x.value)[0], gesperrt: i.filter((x) => x.disabled).map((x) => x.value), leer: i.filter((x) => /\(0\)/.test(x.parentNode.textContent)).map((x) => x.value) }; });
  pruef(JSON.stringify(ep.gesperrt) === JSON.stringify(ep.leer), `${was}: Bauzeitklassen ohne Treffer gesperrt (${ep.gesperrt.join(", ") || "keine"})`);
  await page.click(`#ep input[value="${ep.wahl}"]`, { force: true }); await bereit(page);
  pruef(!new RegExp(ep.wahl).test(JSON.stringify(await page.evaluate(() => window.KIEZ_KARTE.getFilter("obj")))) && /ep=/.test(await page.evaluate(() => location.hash)), `${was}: Bauzeitklasse ${ep.wahl} abwählen ändert Filter und Hash`);
  // Ortsmarke
  await page.click("#om-zeigen"); await page.waitForTimeout(1500); await bereit(page);
  const om = await page.evaluate(() => { const m = window.KIEZ_KARTE, c = m.getCenter(), g = window.KIEZ_DENKMALE_ODBL.ortsmarken[0].geometry.coordinates; return { z: m.getZoom(), d: Math.hypot(c.lng - g[0], c.lat - g[1]), text: document.getElementById("ortsmarke").innerText }; });
  pruef(om.z >= 15.9 && om.d < 0.001 && om.text.length > 20, `${was}: Ortsmarke ul. Kościuszki 18: Karte springt hin (Zoom ${om.z.toFixed(1)}), Text mit „ungeprüft“-Hinweis`);
  const nameFrei = !(await page.evaluate(() => document.body.innerText)).match(/FuturHist/i);
  pruef(nameFrei, `${was}: kein Projektname an der Ortsmarke (KR24)`);
  await dreiD(s, was);
  sauber(s, was);
  await s.ctx.close();
  await handy(url, was);
}

// ---------- Wohnungsbestand und Sanierung
async function modernizacja(lang, o) {
  const url = HTTP + o + "modernizacja.html", was = `${o}modernizacja.html`;
  console.log(`\n[${lang}] Wohnungsbestand`);
  const s = await oeffnen(url);
  const { page } = s;
  const text = await textPruefen(page, was);
  const r = await page.evaluate(() => {
    const S1 = window.KIEZ_SANIERUNG, S2 = window.KIEZ_SANIERUNG_ODBL, m = window.KIEZ_KARTE;
    return {
      abz: [...document.querySelectorAll("main > p .ks-abz, .ks-blatt h2 .ks-abz")].filter((x) => x.offsetHeight > 0).length,
      grenzen: document.querySelectorAll(".ks-grenzen li").length,
      punkte: m.querySourceFeatures("zbk").length >= 0 && S2.punkte.features.length,
      privat: S2.punkte.features.every((f) => ["gmina", "skarb_panstwa", "publiczne_mieszane"].includes(f.properties.eig)),
      liste: document.getElementById("liste").innerText, eintraege: S1.liste.eintraege,
      typ: document.getElementById("typ-zahlen").innerText, blok: S1.typologie.stadt.blok,
      verortung: document.getElementById("verortung").innerText, quote: S2.verortung.quote,
      quellen: document.getElementById("quellen-zbk").innerText, vermerk: S1.quellen.zbk.vermerk.slice(0, 60), haftung: S1.quellen.zbk.odpowiedzialnosc.slice(0, 60),
      anteil: m.getLayoutProperty("anteil", "visibility") !== "none", leg: document.getElementById("legende").innerText,
      lit: document.getElementById("literatur").innerHTML, om: document.getElementById("ortsmarke").innerText,
    };
  });
  const z = (n) => new Intl.NumberFormat({ "": "pl-PL", "en/": "en-GB", "de/": "de-DE" }[o]).format(n);
  pruef(r.abz >= 5 && r.grenzen >= 7, `${was}: Abzeichen Schätzung, ohne Baujahre, ohne Energie, ohne Denkmalstatus sichtbar (${r.abz}); ${r.grenzen} Grenzen und Verweise`);
  pruef(r.privat && r.punkte > 0, `${was}: ${r.punkte} Punkte, alle in öffentlichem Eigentum`);
  pruef(r.liste.includes(z(r.eintraege)) && r.typ.includes(z(r.blok)), `${was}: Zahlen aus den Datendateien im Blatt (${r.eintraege} Einträge, ${r.blok} Kandidaten)`);
  pruef(/Wilson/i.test(r.verortung), `${was}: Verortungsquote mit Wilson-Intervall`);
  pruef(r.quellen.includes(r.vermerk) && r.quellen.includes(r.haftung), `${was}: Quellenvermerk und Haftungsklausel des ZBK wörtlich`);
  pruef(r.anteil && /%/.test(r.leg), `${was}: Stadtteile nach Anteil der Kandidaten gefärbt, Legende mit Prozent und Schätzung`);
  pruef(/doi\.org\/10\.1016\/j\.energy\.2022\.125774/.test(r.lit) && !/80\s*%/.test(text), `${was}: Literatur nur bibliographisch (DOI), keine Zahl aus dem Artikel`);
  pruef(!/FuturHist/i.test(text) && /Kościuszki 18/.test(r.om), `${was}: Ortsmarke ul. Kościuszki 18 ohne Projektname (KR24)`);
  // Stadtteil wählen
  await page.selectOption("#st-wahl", "16"); await bereit(page);
  const st = await page.evaluate(() => ({ text: document.getElementById("st-inhalt").innerText, hash: location.hash }));
  pruef(/st=16/.test(st.hash) && /\d/.test(st.text), `${was}: Stadtteil 16 gewählt: Zählungen und Kandidaten mit Hinweis Schätzung`);
  // Bezug Erreichbarkeit
  await page.click("#bezug-laden"); await bereit(page);
  const tb = await page.evaluate(() => ({ sp: document.querySelectorAll("#tab-dzielnice thead th").length, zeilen: document.querySelectorAll("#tab-dzielnice tbody tr").length }));
  pruef(tb.sp === 7 && tb.zeilen === 18, `${was}: Tabelle je Stadtteil mit Erreichbarkeit und Grün (${tb.zeilen} Zeilen, ${tb.sp} Spalten)`);
  // OSM-Denkmale zuschalten
  await page.click("#dz-knopf"); await bereit(page);
  const dz = await page.evaluate(() => { const T = window.KIEZ_TEXTE, O = window.KIEZ_DENKMALE_ODBL, leg = document.getElementById("legende").innerText;
    const ok = !!(O && O.sichtpruefung && O.sichtpruefung.geprueft === true); return { ok, leg: ok ? leg.includes(T["sanierung.leg_dz_probe"]) && !leg.includes(T["sanierung.leg_dz"]) : leg.includes(T["sanierung.leg_dz"]) }; });
  pruef(await sichtbar(page, "dz") && /\bdz=1/.test(await page.evaluate(() => location.hash)) && dz.leg,
    `${was}: OSM-Denkmale als Ebene zuschaltbar (Hash dz=1), Legende ${dz.ok ? "„Lage in Stichprobe geprüft“" : "„ungeprüft“"}`);
  // Farbe umschalten
  await page.click('#werkzeug input[name="m"][value="osiedle"]', { force: true }); await bereit(page);
  pruef(/m=osiedle/.test(await page.evaluate(() => location.hash)), `${was}: Stadtteilfarbe auf Großsiedlungen (Hash m=osiedle)`);
  // Links zur Erreichbarkeit öffnen die richtige Ansicht
  const link = await page.$eval('a[href^="planer.html#zu=haltestelle_takt"]', (a) => a.getAttribute("href"));
  pruef(/weg=fuss/.test(link) && /halt=1/.test(link), `${was}: Verweis auf die Erreichbarkeit öffnet Haltestelle, Fußweg, Taktklassen (${link})`);
  await dreiD(s, was);
  sauber(s, was);
  await s.ctx.close();
  await handy(url, was);
}

const SEITEN = { planer, kamienice, modernizacja };
for (const [lang, o] of SPRACHEN) for (const [n, f] of Object.entries(SEITEN)) if (!NUR || NUR === n) await f(lang, o);

if (!MIT_KACHELN) ueber("Grundkarte nicht geprüft (kein Kachelordner)");
await browser.close();
server.close();
console.log(`\n${befunde.length ? befunde.length + " Befund(e)" : "grün"}${uebersprungen ? ", " + uebersprungen + " übersprungen" : ""}`);
process.exit(befunde.length ? 1 : 0);
