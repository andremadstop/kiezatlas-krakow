// Prüfung Grundkarte auf den Seiten und Schriften im Browser (Chromium, Playwright), nur 127.0.0.1.
//
// 1. Kartenprobe je Sprache (Wurzel, en/, de/) über HTTP (skripte/entwicklung_server.mjs, Kacheln unter
//    daten/grundkarte/ eingehängt): eine Prüfseite lädt dieselben Dateien wie eine Kartenseite (daten/ort.js,
//    i18n.js, Texte, Stadtteile, vendor/maplibre-gl.js, daten/grundkarte.js mit ?v= wie nach dem Deploy,
//    themen.js) und baut den Stil genau wie karte.js (Quellen basemap = KIEZ_ORT.karte.grundkarte,
//    dop = KIEZ_ORT.karte.luftbild, über KIEZ_THEMEN.grundkarte). Geprüft: Schichten der Grundkarte gezeichnet,
//    Beschriftungen mit polnischen Sonderzeichen, Bildzeile mit BDOT10k und GUGiK, Luftbild-Schalter ohne Fehler,
//    keine Konsolenfehler, keine fehlgeschlagenen Abrufe (außer von MapLibre abgebrochenen Kachelabrufen,
//    net::ERR_ABORTED bei kacheln/*.pbf, nur gezählt), kein Abruf außerhalb 127.0.0.1.
// 2. Dieselbe Prüfseite per file://: keine eigene Grundkarte (MapLibre lädt dort keine Kacheln), aber auch kein
//    Fehler; die übrige Karte wird gezeichnet.
// 3. Schriften im Browser: Für jede Schrift aus atlas.css wird „ąćęłńóśźżĄĆĘŁŃÓŚŹŻ“ einmal mit Ersatz monospace
//    und einmal mit Ersatz serif gemessen. Gleiche Breite heißt: kein Zeichen fiel auf die Ersatzschrift zurück.
// 4. Alle erzeugten Seiten (pl, en, de) über HTTP ohne Konsolenfehler; lädt eine Seite themen.js, muss sie
//    vorher daten/grundkarte.js laden (sonst zeigt sie eine Rasterebene auf einer Vektorquelle).
//    Jede Seite, die themen.js lädt, wird danach bei 1280 und 390 px Breite als Kartenseite geprüft: Karte gezeichnet
//    (.maplibregl-map, Objekte der Grundkarte), Bildzeilen BDOT10k/GUGiK und OpenStreetMap sichtbar, kein
//    horizontaler Überlauf; nach einem Sprung zum Rynek Główny (z15) Beschriftungen mit polnischen Sonderzeichen und
//    geladene Schriftbereiche; ohne Luftbild lässt der Luftbild-Schalter (KIEZ_THEMEN.grundLuft) die Grundkarte stehen.
//    Mindestens eine Seite muss eine Karte haben.
// 5. Startgewicht des Planers (JavaScript, gzip -9 wie die Planerprüfung): planer.html wie ausgeliefert und
//    rechnerisch mit Karte (Ladeliste der Potsdamer planer.html auf die Krakauer Dateien übertragen).
//
// Aufruf: node pruefen/DF_grundkarte.mjs [--ziel KACHELORDNER] [--bilder DIR]
// Ohne Kachelordner: Teile 1 und 2 übersprungen (Rückgabe 0, gemeldet), 3 bis 5 laufen.
// Rückgabe 0 = grün, 1 = Befund.
import { chromium } from "playwright";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import zlib from "node:zlib";
import { pathToFileURL } from "node:url";
import { starten, WURZEL } from "../skripte/entwicklung_server.mjs";

const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const BILDER = arg("--bilder") ? path.resolve(arg("--bilder")) : null;
const POLNISCH = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ";
const SPRACHEN = [["pl", ""], ["en", "en/"], ["de", "de/"]];
const befunde = [];
const pruef = (ok, text) => { console.log((ok ? "  ok    " : "  BEFUND ") + text); if (!ok) befunde.push(text); };

// Prüfseite; vor = Pfad zur Atlas-Wurzel ("", "../" oder eine file://-URL mit / am Ende)
const PROBE = (vor, lang) => `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>Probe</title>
<link rel="stylesheet" href="${vor}vendor/maplibre-gl.css"><link rel="stylesheet" href="${vor}atlas.css">
<style>html,body{margin:0;height:100%}#karte{position:absolute;inset:0}</style></head><body><div id="karte"></div>
<script src="${vor}daten/ort.js"></script><script src="${vor}i18n.js"></script>
<script src="${vor}texte/${lang}/kern.js"></script><script src="${vor}daten/kennzahlen_odbl.js"></script>
<script src="${vor}daten/stadtteile_odbl.js"></script><script src="${vor}vendor/maplibre-gl.js"></script>
<script src="${vor}daten/grundkarte.js?v=20261113"></script><script src="${vor}themen.js"></script>
<script>
window.fehler = [];
var T = window.KIEZ_THEMEN, ST = window.KIEZ_STADTTEILE;
window.stil = T.grundkarte({ version: 8, sources: {
    basemap: window.KIEZ_ORT.karte.grundkarte,
    dop: window.KIEZ_ORT.karte.luftbild,
    teile: { type: "geojson", data: ST, promoteId: "nr", attribution: KIEZ_I18N.sprachwert(window.KIEZ_ORT.karte.teile_attribution) } },
  layers: [
    { id: "papier", type: "background", paint: { "background-color": "#e6e9e4" } },
    { id: "basemap", type: "raster", source: "basemap", paint: { "raster-opacity": 0.6, "raster-saturation": -1 } },
    { id: "dop", type: "raster", source: "dop", layout: { visibility: "none" } },
    { id: "teile-linie", type: "line", source: "teile", paint: { "line-color": "#6a2c82", "line-width": 1.2 } }
  ] });
window.KIEZ_KARTE = new maplibregl.Map({ container: "karte", style: window.stil, center: [19.9373, 50.0617], zoom: 14,
  attributionControl: false, fadeDuration: 0, locale: KIEZ_I18N.karteLocale() });
KIEZ_KARTE.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");
KIEZ_KARTE.on("error", function (e) { window.fehler.push(String(e && e.error && e.error.message || e)); });
</script></body></html>`;

function gz(datei) { try { return zlib.gzipSync(fs.readFileSync(datei), { level: 9 }).length; } catch { return null; } }

const { server, url: HTTP, kacheln } = await starten({
  ziel: arg("--ziel"),
  zusatz: Object.fromEntries(SPRACHEN.map(([l, o]) => [`/${o}__probe.html`, () => PROBE(o ? "../" : "", l)])),
});
const mitKacheln = fs.existsSync(path.join(kacheln, "MANIFEST.sha256"));
const browser = await chromium.launch();

async function neueSeite() {
  const page = await browser.newPage({ viewport: { width: 1000, height: 700 } });
  const s = { page, fremd: [], kaputt: [], konsole: [], geladen: [] };
  await page.route("**/*", (r) => {
    const u = new URL(r.request().url());
    if (u.protocol === "file:" || u.protocol === "data:" || u.protocol === "blob:" || u.hostname === "127.0.0.1") return r.continue();
    s.fremd.push(u.href); return r.abort();
  });
  page.on("console", (m) => { if (m.type() === "error") s.konsole.push(m.text()); });
  page.on("pageerror", (e) => s.konsole.push(String(e)));
  // Ohne Kachelordner fehlen die Kacheln absichtlich (Teile 1, 2 und die Kartenseiten sind dann übersprungen)
  const luecke = (u) => !mitKacheln && /\/daten\/grundkarte\//.test(u);
  // MapLibre bricht Kachelabrufe ab, die beim Zoomen oder Seitenwechsel nicht mehr gebraucht werden (net::ERR_ABORTED);
  // das ist kein Fehler der Grundkarte. Gezählt wird es nur, andere Fehler bei Kacheln bleiben Befund.
  const abgebrochen = (r) => r.failure()?.errorText === "net::ERR_ABORTED" && /\/daten\/grundkarte\/kacheln\/.+\.pbf$/.test(new URL(r.url()).pathname);
  page.on("requestfailed", (r) => {
    if (luecke(r.url())) return;
    if (abgebrochen(r)) { s.abgebrochen = (s.abgebrochen || 0) + 1; return; }
    s.kaputt.push(`${r.failure()?.errorText} ${r.url()}`);
  });
  page.on("response", (r) => { s.geladen.push(r.url()); if (r.status() >= 400 && !luecke(r.url())) s.kaputt.push(`${r.status()} ${r.url()}`); });
  return s;
}
const sauber = (s, wo) => {
  pruef(!s.konsole.length, `${wo}: keine Konsolenfehler${s.konsole.length ? ": " + s.konsole.slice(0, 3).join(" | ") : ""}`);
  pruef(!s.kaputt.length, `${wo}: keine fehlgeschlagenen Abrufe${s.kaputt.length ? ": " + s.kaputt.slice(0, 3).join(" | ") : ""}${s.abgebrochen ? ` (${s.abgebrochen} Kachelabrufe von MapLibre abgebrochen, kein Befund)` : ""}`);
  pruef(!s.fremd.length, `${wo}: kein Abruf außerhalb 127.0.0.1${s.fremd.length ? ": " + s.fremd.slice(0, 3).join(" | ") : ""}`);
};
const warteKarte = (page) => page.waitForFunction(() => window.KIEZ_KARTE && window.KIEZ_KARTE.loaded() && window.KIEZ_KARTE.areTilesLoaded(), null, { timeout: 30000 });

console.log("1. Grundkarte über HTTP je Sprache" + (mitKacheln ? ` (Kacheln aus ${kacheln})` : ""));
if (!mitKacheln) console.log(`  übersprungen: kein Kachelordner mit MANIFEST.sha256 unter ${kacheln} (erst skripte/27_grundkarte.py)`);
else for (const [lang, ord] of SPRACHEN) {
  const s = await neueSeite(), wo = `${ord}__probe.html`;
  await s.page.goto(HTTP + wo);
  try { await warteKarte(s.page); } catch { pruef(false, `${wo}: Karte nach 30 s nicht geladen; ${(await s.page.evaluate(() => window.fehler)).slice(0, 2).join(" | ")}`); }
  await s.page.waitForTimeout(300);
  const r = await s.page.evaluate(() => {
    const m = window.KIEZ_KARTE, n = {};
    const f = m.queryRenderedFeatures();
    f.forEach((x) => { if (x.source === "bm") n[x.sourceLayer] = (n[x.sourceLayer] || 0) + 1; });
    const namen = [...new Set(f.filter((x) => x.source === "bm" && x.layer.type === "symbol").map((x) => x.properties.nazwa).filter(Boolean))];
    let schalter = null;
    try { m.setLayoutProperty("dop", "visibility", "visible"); m.setLayoutProperty("dop", "visibility", "none"); schalter = "ok"; } catch (e) { schalter = String(e); }
    const st = m.getStyle();
    return { n, namen, schalter, quellen: Object.keys(st.sources), kachel: st.sources.bm && st.sources.bm.tiles[0], glyphs: st.glyphs,
      attribution: (document.querySelector(".maplibregl-ctrl-attrib-inner") || {}).textContent || "", fehler: window.fehler };
  });
  pruef(Object.keys(r.n).length >= 3, `${wo}: Schichten der Grundkarte gezeichnet ${JSON.stringify(r.n)}`);
  const pl = r.namen.filter((x) => /[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]/.test(x));
  pruef(pl.length > 0, `${wo}: ${r.namen.length} Beschriftungen, davon ${pl.length} mit polnischem Sonderzeichen (z. B. „${pl.slice(0, 2).join("“, „")}“)`);
  const wurzel = HTTP;
  pruef(r.kachel === `${wurzel}daten/grundkarte/kacheln/{z}/{x}/{y}.pbf` && r.glyphs === `${wurzel}daten/grundkarte/schrift/{fontstack}/{range}.pbf`,
    `${wo}: Pfade absolut zur Atlas-Wurzel aufgelöst (${(r.kachel || "").replace(HTTP, "/")}, trotz ?v= an daten/grundkarte.js)`);
  pruef(!r.quellen.includes("dop") && !r.quellen.includes("basemap") && r.schalter === "ok",
    `${wo}: Luftbild null ohne Quelle, Schalter "dop" ohne Fehler (${r.schalter}); Quellen ${r.quellen.join(", ")}`);
  pruef(/BDOT10k/.test(r.attribution) && /Główny Urząd Geodezji i Kartografii/.test(r.attribution),
    `${wo}: Bildzeile auf der Karte „${r.attribution.trim().slice(0, 140)}…“`);
  pruef(!r.fehler.length, `${wo}: keine MapLibre-Fehler${r.fehler.length ? ": " + r.fehler.slice(0, 2).join(" | ") : ""}`);
  const kachelAbrufe = s.geladen.filter((u) => /\/daten\/grundkarte\/kacheln\/\d+\/\d+\/\d+\.pbf$/.test(u)).length;
  const schriftAbrufe = s.geladen.filter((u) => /\/daten\/grundkarte\/schrift\//.test(u)).length;
  pruef(kachelAbrufe > 0 && schriftAbrufe > 0, `${wo}: ${kachelAbrufe} Kacheln und ${schriftAbrufe} Schriftbereiche geladen`);
  sauber(s, wo);
  if (BILDER && lang === "pl") { fs.mkdirSync(BILDER, { recursive: true }); await s.page.screenshot({ path: path.join(BILDER, "rynek_z14.png") }); }
  await s.page.close();
}

console.log("2. Dieselbe Prüfseite per file://");
{
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "df-probe-"));
  const datei = path.join(tmp, "probe.html");
  fs.writeFileSync(datei, PROBE(pathToFileURL(WURZEL).href + "/", "pl"));
  const s = await neueSeite();
  await s.page.goto(pathToFileURL(datei).href);
  try { await warteKarte(s.page); } catch { pruef(false, "file://: Karte nach 30 s nicht geladen"); }
  const r = await s.page.evaluate(() => ({ gk: window.KIEZ_THEMEN.GRUNDKARTE, quellen: Object.keys(window.KIEZ_KARTE.getStyle().sources),
    teile: window.KIEZ_KARTE.queryRenderedFeatures({ layers: ["teile-linie"] }).length, fehler: window.fehler }));
  pruef(r.gk && !r.quellen.includes("bm") && r.teile > 0, `file://: ohne eigene Grundkarte (Quellen ${r.quellen.join(", ")}), Stadtteile gezeichnet (${r.teile})`);
  pruef(!r.fehler.length, `file://: keine MapLibre-Fehler${r.fehler.length ? ": " + r.fehler.slice(0, 2).join(" | ") : ""}`);
  sauber(s, "file://");
  await s.page.close();
  fs.rmSync(tmp, { recursive: true });
}

console.log("3. Schriften im Browser: polnische Sonderzeichen ohne Ersatzschrift");
{
  const s = await neueSeite();
  await s.page.goto(HTTP + "index.html");
  const faces = [...fs.readFileSync(path.join(WURZEL, "atlas.css"), "utf8").matchAll(/@font-face\{font-family:"([^"]+)";src:url\(([^)]+)\)[^}]*font-weight:(\d+)/g)].map((m) => [m[1], m[3], m[2]]);
  const r = await s.page.evaluate(async ([faces, text]) => {
    const aus = [];
    for (const [fam, w] of faces) {
      await document.fonts.load(`${w} 40px "${fam}"`, text);
      const c = document.createElement("canvas").getContext("2d");
      c.font = `${w} 40px "${fam}", monospace`; const a = c.measureText(text).width;
      c.font = `${w} 40px "${fam}", serif`; const b = c.measureText(text).width;
      c.font = `${w} 40px monospace`; const m = c.measureText(text).width;
      aus.push({ fam, w, a, b, m, geladen: document.fonts.check(`${w} 40px "${fam}"`, text) });
    }
    return aus;
  }, [faces, POLNISCH]);
  pruef(r.length === 5, `${r.length} Schriften aus atlas.css gemessen`);
  for (const x of r) pruef(x.geladen && Math.abs(x.a - x.b) < 0.01 && Math.abs(x.a - x.m) > 1,
    `${x.fam} ${x.w}: Breite mit Ersatz monospace ${x.a.toFixed(2)} px = mit Ersatz serif ${x.b.toFixed(2)} px (nur monospace: ${x.m.toFixed(2)} px)`);
  sauber(s, "index.html (Schriften)");
  await s.page.close();
}

console.log("4. Alle erzeugten Seiten über HTTP");
{
  const seiten = SPRACHEN.flatMap(([, o]) => fs.readdirSync(path.join(WURZEL, o || ".")).filter((f) => f.endsWith(".html")).map((f) => o + f));
  let ohneFehler = 0, mitKarte = 0;
  const kartenseiten = [];
  for (const wo of seiten) {
    const s = await neueSeite();
    await s.page.goto(HTTP + wo, { waitUntil: "load" });
    await s.page.waitForTimeout(150);
    const reihe = await s.page.evaluate(() => [...document.scripts].map((x) => (x.getAttribute("src") || "").split("?")[0]));
    const t = reihe.findIndex((x) => /(^|\/)themen\.js$/.test(x)), g = reihe.findIndex((x) => /(^|\/)daten\/grundkarte\.js$/.test(x));
    if (t >= 0) { mitKarte++; kartenseiten.push(wo); pruef(g >= 0 && g < t, `${wo}: lädt daten/grundkarte.js vor themen.js`); }
    const fehler = s.konsole.length + s.kaputt.length + s.fremd.length;
    if (fehler && wo !== "404.html" && !wo.endsWith("/404.html")) sauber(s, wo); else ohneFehler++;
    await s.page.close();
  }
  pruef(ohneFehler === seiten.length, `${ohneFehler} von ${seiten.length} Seiten ohne Konsolenfehler und Fehlabruf (404.html darf sich selbst melden)`);
  console.log(`        Seiten, die themen.js laden (also eine Karte haben): ${mitKarte} (${kartenseiten.join(", ")})`);
  pruef(mitKarte > 0, `${mitKarte} erzeugte Seiten laden eine Karte`);
  if (!mitKacheln) console.log("  Kartenseiten übersprungen: kein Kachelordner");
  else for (const wo of kartenseiten) for (const breite of [1280, 390]) {
    const s = await neueSeite(), was = `${wo} (${breite} px)`;
    await s.page.setViewportSize({ width: breite, height: 900 });
    await s.page.goto(HTTP + wo, { waitUntil: "load" });
    try { await warteKarte(s.page); } catch { pruef(false, `${was}: Karte nach 30 s nicht geladen`); await s.page.close(); continue; }
    await s.page.waitForTimeout(300);
    const r = await s.page.evaluate(() => {
      const m = window.KIEZ_KARTE, st = m.getStyle(), gk = st.layers.filter((l) => l.source === "bm").map((l) => l.id);
      const a = document.querySelector(".maplibregl-ctrl-attrib"), ar = a ? a.getBoundingClientRect() : null;
      const kr = m.getContainer().getBoundingClientRect();
      return { karte: !!document.querySelector(".maplibregl-map"), quellen: Object.keys(st.sources), n: m.queryRenderedFeatures({ layers: gk }).length,
        bild: a ? a.textContent.replace(/\s+/g, " ").trim() : "", bildDrin: !!ar && ar.width > 0 && ar.height > 0 && ar.left >= kr.left - 1 && ar.right <= kr.right + 1 && ar.bottom <= kr.bottom + 1,
        ueber: document.documentElement.scrollWidth > window.innerWidth };
    });
    pruef(r.karte && r.quellen.includes("bm") && r.n > 0, `${was}: Karte mit eigener Grundkarte gezeichnet (${r.n} Objekte, Quellen ${r.quellen.join(", ")})`);
    pruef(/BDOT10k/.test(r.bild) && /Główny Urząd Geodezji i Kartografii/.test(r.bild) && /OpenStreetMap/.test(r.bild) && r.bildDrin,
      `${was}: Bildzeilen sichtbar in der Karte „${r.bild.slice(0, 160)}“`);
    pruef(!r.ueber, `${was}: kein horizontaler Überlauf`);
    // Auf „idle“ nach dem Sprung warten: loaded() ist direkt nach jumpTo oft noch true, bevor die neuen Kacheln und
    // Beschriftungen gesetzt sind (mit den echten Stadtteilgrenzen dauert das länger als mit Beispieldaten)
    const still = await s.page.evaluate(() => new Promise((ok) => {
      const m = window.KIEZ_KARTE, t = setTimeout(() => ok(false), 30000);
      m.once("idle", () => { clearTimeout(t); ok(true); });
      m.jumpTo({ center: [19.9373, 50.0617], zoom: 15 });
    }));
    if (!still) pruef(false, `${was}: Rynek z15 nach 30 s nicht geladen`);
    try { await warteKarte(s.page); } catch { pruef(false, `${was}: Rynek z15 nach 30 s nicht geladen`); }
    await s.page.waitForTimeout(300);
    const z = await s.page.evaluate(() => {
      const m = window.KIEZ_KARTE, T = window.KIEZ_THEMEN, gk = m.getStyle().layers.filter((l) => l.source === "bm");
      const namen = [...new Set(m.queryRenderedFeatures({ layers: gk.filter((l) => l.type === "symbol").map((l) => l.id) }).map((x) => x.properties.nazwa).filter(Boolean))];
      T.grundLuft(m, true);
      const sichtbar = gk.filter((l) => l.type !== "symbol" && m.getLayoutProperty(l.id, "visibility") !== "none").length;
      T.grundLuft(m, false);
      return { namen, luft: T.LUFTBILD, sichtbar, flaechen: gk.filter((l) => l.type !== "symbol").length };
    });
    const pl = z.namen.filter((x) => /[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]/.test(x));
    const schrift = s.geladen.filter((u) => /\/daten\/grundkarte\/schrift\//.test(u)).length;
    pruef(pl.length > 0 && schrift > 0, `${was}: Rynek z15 mit ${z.namen.length} Beschriftungen, davon ${pl.length} mit polnischem Sonderzeichen (z. B. „${pl.slice(0, 2).join("“, „")}“), ${schrift} Schriftbereiche geladen`);
    if (!z.luft) pruef(z.sichtbar === z.flaechen, `${was}: ohne Luftbild lässt der Luftbild-Schalter die Grundkarte stehen (${z.sichtbar} von ${z.flaechen} Flächen- und Linienebenen sichtbar)`);
    sauber(s, was);
    if (BILDER) { fs.mkdirSync(BILDER, { recursive: true }); await s.page.screenshot({ path: path.join(BILDER, `${wo.replace("/", "_").replace(".html", "")}_${breite}.png`) }); }
    await s.page.close();
  }
}

console.log("5. Startgewicht des Planers (JavaScript, gzip -9)");
{
  const s = await neueSeite();
  await s.page.goto(HTTP + "planer.html", { waitUntil: "load" });
  await s.page.waitForTimeout(300);
  const js = [...new Set(s.geladen.filter((u) => new URL(u).pathname.endsWith(".js")).map((u) => new URL(u).pathname.slice(1)))];
  const summe = js.reduce((a, f) => a + (gz(path.join(WURZEL, f)) || 0), 0);
  console.log(`        planer.html heute: ${summe} B gz (${js.length} Dateien: ${js.join(", ")})`);
  pruef(summe > 0, "Startgewicht von planer.html gemessen");
  await s.page.close();
  // Mit Karte: Ladeliste der Potsdamer planer.html (kopf.js, daten/stadtteile.js, daten/planungsraeume.js,
  // vendor/maplibre-gl.js, daten/grundkarte.js, themen.js, planer.js) auf Kraków übertragen, dazu die Textschicht.
  // daten/planungsraeume.js gibt es in Kraków nicht; die Zellen lädt der Planer erst bei Bedarf.
  const mitKarte = ["daten/ort.js", "i18n.js", "texte/pl/kern.js", "texte/pl/seiten.js", "texte/pl/planer.js", "kopf.js", "rahmen.js",
    "daten/stadtteile_odbl.js", "vendor/maplibre-gl.js", "daten/grundkarte.js", "themen.js", "planer.js"];
  const teile = mitKarte.map((f) => [f, gz(path.join(WURZEL, f))]);
  const fehlt = teile.filter(([, b]) => b == null).map(([f]) => f);
  const summe2 = teile.reduce((a, [, b]) => a + (b || 0), 0);
  console.log(`        planer.html mit Karte (gerechnet): ${summe2} B gz = ${(summe2 / 1024).toFixed(1)} KB; je Datei ${teile.map(([f, b]) => `${f} ${b}`).join(", ")}`);
  pruef(!fehlt.length, `alle Dateien der Ladeliste vorhanden${fehlt.length ? " (fehlen: " + fehlt.join(", ") + ")" : ""}`);
  console.log(`        davon Grundkarte daten/grundkarte.js: ${gz(path.join(WURZEL, "daten/grundkarte.js"))} B gz`);
}

await browser.close();
server.close();
console.log(`\n${befunde.length ? befunde.length + " Befund(e)" : "grün"}`);
process.exit(befunde.length ? 1 : 0);
