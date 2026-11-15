// Seitenprüfung Kraków: alle erzeugten Seiten (skripte/30_seiten.py) in allen Sprachen, per file:// und per HTTP.
//
// Je Seite und Sprache:
//   - lädt ohne Konsolen- oder Seitenfehler und ohne fehlende Datei; Fremdabrufe gibt es keine (jeder würde gezählt)
//   - kein sichtbarer Platzhalter ({{…}}) und kein sichtbarer Textschlüssel (kern.…, seiten.… …)
//   - <html lang> passt zum Ordner, og:locale passt, keine deutschen Reste in pl/en (Wortliste)
//   - hreflang-Block vollständig (pl, en, de, x-default) und reziprok, canonical = eigene Fassung
//   - Hinweis „Beispieldaten“ sichtbar genau dann, wenn die Seite Beispieldaten lädt
//   - axe-core ohne Verstoß, bei 360 px Breite kein seitlicher Überstand
// Dazu: Sprachschalter nimmt den Hash mit (file:// und HTTP), i18n.js liefert Plural und Zahlformate der Sprache.
//
// Grundkarte: Unter HTTP wird daten/grundkarte/ wie in skripte/entwicklung_server.mjs aus dem Kachelordner außerhalb
// des Repos geliefert, wenn die Wurzel keinen eigenen Ordner daten/grundkarte/ hat (Deploy-Kopie: hat ihn). Fehlt
// auch der Kachelordner, zählen Fehlabrufe unter daten/grundkarte/ nicht und werden als übersprungen gemeldet.
//
// Aufruf:  node pruefen/seiten.mjs [--wurzel <ordner>] [--json <datei>]
// Braucht: node_modules mit playwright und axe-core, Chromium unter ~/.cache/ms-playwright. Rückgabe 0 = grün.
import { chromium } from "playwright";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath, pathToFileURL } from "node:url";
import { kachelordner } from "../skripte/entwicklung_server.mjs";

const HIER = path.dirname(fileURLToPath(import.meta.url));
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const WURZEL = path.resolve(arg("--wurzel", path.join(HIER, "..")));
const AXE = fs.readFileSync(path.join(HIER, "..", "node_modules", "axe-core", "axe.min.js"), "utf8");
const TYP = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml",
  ".png": "image/png", ".woff2": "font/woff2", ".json": "application/json", ".pbf": "application/x-protobuf" };

// Ortskonfiguration aus daten/ort.js (dieselbe Datei, die die Seiten laden)
const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(WURZEL, "daten", "ort.js"), "utf8"), sandbox);
const ORT = sandbox.window.KIEZ_ORT;
const SPRACHEN = ORT.sprachen, STANDARD = ORT.standardsprache;
const ordner = (l) => (l === STANDARD ? "" : l + "/");
const OG = { pl: "pl_PL", en: "en_GB", de: "de_DE" };
const LOCALE = { pl: "pl-PL", en: "en-GB", de: "de-DE" };
// Seiten, die Beispieldaten laden dürfen: das sagt der Vorlagenkopf (daten: …)
const DATEN = Object.fromEntries(ORT.seiten.map((s) => {
  const kopf = fs.readFileSync(path.join(WURZEL, "vorlagen", s + ".html"), "utf8").match(/<!--seite\n([\s\S]*?)\n-->/)[1];
  return [s, ((kopf.match(/^daten:(.*)$/m) || [])[1] || "").trim().split(/\s+/).filter(Boolean)];
}));
const istBeispiel = (datei) => /"fixture":true/.test(fs.readFileSync(path.join(WURZEL, datei), "utf8").slice(0, 4000));
// deutsche Wörter, die in pl/en nicht vorkommen dürfen (ganze Wörter, Groß-/Kleinschreibung egal)
const DEUTSCH = /\b(und|nicht|oder|Stadtteile?|Einwohner|Karte|Daten|Quelle|Stand der|zeigen|Gebäude|für|über|Seite)\b/i;
const SCHLUESSEL = /\b(kern|seiten|karte|erzaehlung|kamienice|planer|klimat|powietrze|mieszkania|punktualnosc|denkmale|sanierung|gebaeude|bevoelkerung|fussweg)\.(?!(?:js|json|csv|gpkg|html|md)\b)[a-z0-9_]+(\.[a-z0-9_]+)*\b/;

// Pflichtangaben aus den Bedingungen der Gmina Miejska Kraków (quellen-DS.md, Bedingung II), wörtliche Stücke
const ZBK_KLAUSEL = ["data wytworzenia", "data pozyskania", "Informacja przetworzona", "nie ponosi odpowiedzialności"];
const befunde = [];
const bericht = { stand: new Date().toISOString(), wurzel: WURZEL, seiten: [] };
function pruef(ok, text) { console.log((ok ? "  ok   " : "  FEHLT ") + text); if (!ok) befunde.push(text); return ok; }

const EIGENE_GK = fs.existsSync(path.join(WURZEL, "daten", "grundkarte"));
const KACHELN = EIGENE_GK ? null : kachelordner();
const MIT_KACHELN = EIGENE_GK || fs.existsSync(path.join(KACHELN, "MANIFEST.sha256"));
const IST_GK = (u) => /\/daten\/grundkarte\//.test(u);
let gkUebersprungen = 0;
const server = http.createServer((q, a) => {
  const rel = decodeURIComponent(new URL(q.url, "http://x").pathname);
  const gk = !EIGENE_GK && rel.startsWith("/daten/grundkarte/");
  const basis = gk ? KACHELN : WURZEL;
  const p = path.normalize(path.join(basis, gk ? rel.slice("/daten/grundkarte/".length) : rel));
  if (p !== basis && !p.startsWith(basis + path.sep)) { a.writeHead(403); a.end(); return; }
  fs.readFile(p, (f, b) => { if (f) { a.writeHead(404); a.end(); return; } a.writeHead(200, { "content-type": TYP[path.extname(p)] || "application/octet-stream" }); a.end(b); });
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const HTTP = `http://127.0.0.1:${server.address().port}/`, FILE = pathToFileURL(WURZEL + path.sep).href;
const eigen = (u) => u.startsWith("file://") || u.startsWith(HTTP) || u.startsWith("data:") || u.startsWith("about:");
const browser = await chromium.launch();

async function oeffnen(url, o = {}) {
  const ctx = await browser.newContext({ viewport: { width: o.breite || 1280, height: 800 }, reducedMotion: "reduce", locale: o.locale || "pl-PL" });
  const page = await ctx.newPage();
  const fehler = [], fremd = [];
  page.on("console", (m) => { if (m.type() === "error") fehler.push("Konsole: " + m.text()); });
  page.on("pageerror", (e) => fehler.push("Seitenfehler: " + e.message));
  const gkLuecke = (u) => { if (!MIT_KACHELN && IST_GK(u)) { gkUebersprungen++; return true; } return false; };
  page.on("requestfailed", (r) => { if (!gkLuecke(r.url())) fehler.push("nicht geladen: " + r.url()); });
  page.on("response", (r) => { if (r.status() >= 400 && !gkLuecke(r.url())) fehler.push(`HTTP ${r.status()}: ${r.url()}`); });
  await page.route("**/*", (r) => { const u = r.request().url(); if (eigen(u)) return r.continue(); fremd.push(u); return r.fulfill({ status: 204, body: "" }); });
  await page.goto(url, { waitUntil: "load" });
  await page.waitForTimeout(150);
  return { ctx, page, fehler, fremd };
}

// ---------- Je Seite und Sprache
for (const lang of SPRACHEN) {
  console.log(`\n[${lang}] ${ORT.seiten.length} Seiten`);
  for (const s of ORT.seiten) {
    const rel = ordner(lang) + s + ".html";
    for (const [art, basis] of [["file", FILE], ["http", HTTP]]) {
      const { ctx, page, fehler, fremd } = await oeffnen(basis + rel);
      const info = await page.evaluate(() => ({
        lang: document.documentElement.lang, text: document.body.innerText, html: document.documentElement.outerHTML,
        og: (document.querySelector('meta[property="og:locale"]') || {}).content,
        alt: [...document.querySelectorAll('link[rel="alternate"][hreflang]')].map((l) => [l.hreflang, l.href]),
        canon: (document.querySelector('link[rel="canonical"]') || {}).href || null,
        noindex: !!document.querySelector('meta[name="robots"][content*="noindex"]'),
        beispiel: (() => { const b = document.getElementById("beispieldaten"); return !!b && !b.hidden && b.offsetHeight > 0; })(),
        bereit: !!(window.KIEZ_ORT && window.KIEZ_I18N && window.KIEZ_TEXTE && window.KIEZ_TEXTE["kern.sprung"]),
      }));
      const kurz = `${rel} (${art})`;
      pruef(!fehler.length && !fremd.length && info.bereit, `${kurz}: lädt ohne Fehler${fehler.length ? ": " + fehler.slice(0, 3).join("; ") : ""}${fremd.length ? ", Fremdabrufe: " + fremd.slice(0, 3).join(" ") : ""}${info.bereit ? "" : ", Textschicht nicht geladen"}`);
      if (art === "http") { await ctx.close(); continue; }   // Inhaltsprüfungen einmal, per file://
      const sichtbarSchl = info.text.match(SCHLUESSEL);
      pruef(!info.text.includes("{{") && !sichtbarSchl, `${kurz}: kein Platzhalter und kein Textschlüssel sichtbar${sichtbarSchl ? ": " + sichtbarSchl[0] : ""}`);
      pruef(info.lang === lang && info.og === OG[lang], `${kurz}: lang="${info.lang}", og:locale ${info.og}`);
      if (lang !== "de") {
        const d = info.text.replace(/Stiebitz Souverain Systems UG \(haftungsbeschränkt\)/g, "").replace(/Impressum|Datenschutz/g, "")
          .split(/\n/).filter((z) => !/Auch auf Deutsch/.test(z)).join("\n").match(DEUTSCH);
        pruef(!d, `${kurz}: keine deutschen Reste${d ? ": „" + d[0] + "“" : ""}`);
      }
      if (info.noindex) {
        pruef(!info.alt.length && !info.canon, `${kurz}: noindex ohne hreflang und canonical`);
      } else {
        const erwartet = Object.fromEntries(SPRACHEN.map((l) => [l, ORT.basis_url + ordner(l) + (s === "index" ? "" : s + ".html")]));
        erwartet["x-default"] = erwartet[STANDARD];
        const ist = Object.fromEntries(info.alt);
        const vollst = Object.keys(erwartet).every((k) => ist[k] === erwartet[k]) && info.alt.length === Object.keys(erwartet).length;
        pruef(vollst && info.canon === erwartet[lang], `${kurz}: hreflang (${info.alt.map((a) => a[0]).join(", ")}) und canonical vollständig`);
        // reziprok: jede genannte Fassung nennt dieselbe Gruppe
        const fehlend = [];
        for (const l of SPRACHEN) {
          const datei = path.join(WURZEL, ordner(l), s + ".html");
          const t = fs.existsSync(datei) ? fs.readFileSync(datei, "utf8") : "";
          for (const k of Object.keys(erwartet)) if (!t.includes(`hreflang="${k}" href="${erwartet[k]}"`)) fehlend.push(`${l}→${k}`);
        }
        pruef(!fehlend.length, `${kurz}: hreflang reziprok${fehlend.length ? ", fehlt: " + fehlend.join(" ") : ""}`);
      }
      const sollBeispiel = DATEN[s].some(istBeispiel);
      pruef(info.beispiel === sollBeispiel, `${kurz}: Hinweis Beispieldaten ${sollBeispiel ? "sichtbar" : "verborgen"} (${DATEN[s].join(" ") || "keine Daten"})`);
      // Bedingungen der Gmina Miejska Kraków (Weiterverwendung der ZBK-Liste): Quelle mit Zeiten, Verarbeitung und
      // Zakres odpowiedzialności wörtlich auf jeder Seite, die ZBK-Werte zeigt
      if (/src="[^"]*daten\/sanierung(_odbl)?\.js"/.test(info.html)) pruef(ZBK_KLAUSEL.every((x) => info.text.includes(x)),
        `${kurz}: ZBK-Werte mit Quelle, Zeiten, Verarbeitung und Haftungsklausel (${ZBK_KLAUSEL.filter((x) => !info.text.includes(x)).join(", ") || "vollständig"})`);
      await page.addScriptTag({ content: AXE });
      const axe = await page.evaluate(async () => (await window.axe.run(document, { resultTypes: ["violations"] })).violations.map((v) => `${v.id} (${v.nodes.length})`));
      pruef(!axe.length, `${kurz}: axe ohne Verstoß${axe.length ? ": " + axe.join(", ") : ""}`);
      await ctx.close();
      const schmal = await oeffnen(basis + rel, { breite: 360 });
      const ueber = await schmal.page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      pruef(ueber <= 0, `${kurz}: 360 px ohne seitlichen Überstand (${ueber} px)`);
      await schmal.ctx.close();
      bericht.seiten.push({ seite: rel, beispiel: info.beispiel });
    }
  }
}

// ---------- Karte: ZBK als Färbung und als Punkte mit Haftungsklausel in der Legende
console.log("\nKarte mit ZBK");
for (const lang of SPRACHEN) {
  for (const h of ["dz=zbk", "pkt=zbk"]) {
    const { ctx, page } = await oeffnen(HTTP + ordner(lang) + "karta.html#" + h);
    await page.waitForFunction((x) => x.every((s) => document.body.innerText.includes(s)), ZBK_KLAUSEL, { timeout: 15000 }).catch(() => {});
    const text = await page.evaluate(() => document.body.innerText);
    pruef(ZBK_KLAUSEL.every((x) => text.includes(x)), `${lang} karta.html#${h}: Legende mit Quelle, Zeiten, Verarbeitung und Haftungsklausel (${ZBK_KLAUSEL.filter((x) => !text.includes(x)).join(", ") || "vollständig"})`);
    await ctx.close();
  }
}

// ---------- Sprachschalter behält den Hash
console.log("\nSprachschalter");
for (const [art, basis] of [["file", FILE], ["http", HTTP]]) {
  for (const [von, nach] of [["en", "de"], [STANDARD, "en"], ["de", STANDARD]]) {
    const { ctx, page } = await oeffnen(basis + ordner(von) + "karta.html#thema=ew&st=07");
    await page.evaluate(() => { location.hash = "thema=ew&st=07&k=12/50.06/19.94/0/0"; });
    await Promise.all([page.waitForURL((u) => u.pathname.includes(nach === STANDARD ? "/karta.html" : `/${nach}/karta.html`) && !u.pathname.includes(`/${von}/`) || false), page.click(`.sprachen a[data-sprache="${nach}"]`)]);
    const u = new URL(page.url());
    pruef(u.hash === "#thema=ew&st=07&k=12/50.06/19.94/0/0" && (await page.evaluate(() => document.documentElement.lang)) === nach,
      `${art}: ${von} → ${nach}: ${u.pathname.split("/").slice(-2).join("/")}${u.hash}`);
    await ctx.close();
  }
}

// ---------- Sprachhinweis: einmal, nur bei abweichender Browsersprache, ohne Umleitung
console.log("\nSprachhinweis");
{
  const a = await oeffnen(FILE + "index.html", { locale: "de-DE" });
  const sicht = await a.page.evaluate(() => { const h = document.getElementById("sprachhinweis"); return !h.hidden && [...h.querySelectorAll("a")].filter((x) => !x.hidden).map((x) => x.lang); });
  pruef(JSON.stringify(sicht) === '["de"]' && a.page.url().endsWith("/index.html"), `Browser de, Seite pl: Hinweis nur auf Deutsch (${JSON.stringify(sicht)}), keine Umleitung`);
  await a.ctx.close();
  const b = await oeffnen(FILE + "index.html", { locale: "pl-PL" });
  pruef(await b.page.evaluate(() => document.getElementById("sprachhinweis").hidden), "Browser pl, Seite pl: kein Hinweis");
  await b.ctx.close();
}

// ---------- i18n.js: Plural, Zahlen, Datum, fehlender Schlüssel
console.log("\ni18n.js");
for (const lang of SPRACHEN) {
  const { ctx, page } = await oeffnen(FILE + ordner(lang) + "index.html");
  const r = await page.evaluate(() => {
    const I = window.KIEZ_I18N;
    return { lang: I.lang, p: [1, 2, 5, 12, 22, 25].map((n) => I.t("kern.dzielnice", { n })), z: [I.fmt.zahl(1234), I.fmt.zahl(12345), I.fmt.zahl(2.5, 1)],
      a: I.fmt.anteil(12.5), d: I.fmt.datum("2021-03-31"), fehlt: I.t("kern.gibt_es_nicht"), stadt: I.ort("stadt"), name: I.ort("name") };
  });
  const L = LOCALE[lang], nf = new Intl.NumberFormat(L), pr = new Intl.PluralRules(L);
  const T = (await page.evaluate(() => window.KIEZ_TEXTE["kern.dzielnice"]));
  const pErw = [1, 2, 5, 12, 22, 25].map((n) => (T[pr.select(n)] || T.other).replace("{n}", nf.format(n)));
  pruef(JSON.stringify(r.p) === JSON.stringify(pErw), `${lang}: Plural ${r.p.join(" | ")}`);
  const zErw = [nf.format(1234), nf.format(12345), new Intl.NumberFormat(L, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(2.5)];
  pruef(JSON.stringify(r.z) === JSON.stringify(zErw) && r.a === new Intl.NumberFormat(L, { style: "percent", minimumFractionDigits: 1 }).format(0.125)
    && r.d === new Date("2021-03-31").toLocaleDateString(L), `${lang}: Zahlen ${r.z.join(" | ")}, Anteil ${r.a}, Datum ${r.d}`);
  if (lang === "pl") pruef(r.p.join("|") === "1 dzielnica|2 dzielnice|5 dzielnic|12 dzielnic|22 dzielnice|25 dzielnic" && r.z[0] === "1234",
    `pl: Formen one/few/many richtig, vierstellige Zahl ungruppiert (${r.z[0]})`);
  pruef(r.fehlt === "kern.gibt_es_nicht" && r.lang === lang && r.stadt === ORT.stadt[lang] && r.name === ORT.name[lang],
    `${lang}: fehlender Schlüssel bleibt sichtbar, Ortswerte in der Seitensprache (${r.stadt})`);
  await ctx.close();
}

await browser.close(); server.close();
const j = arg("--json"); if (j) fs.writeFileSync(j, JSON.stringify({ ...bericht, befunde }, null, 1));
console.log(`\nGrundkarte: ${EIGENE_GK ? "aus der Wurzel" : MIT_KACHELN ? "aus " + KACHELN : "übersprungen, kein Kachelordner unter " + KACHELN + " (" + gkUebersprungen + " Abrufe nicht gezählt)"}`);
console.log(befunde.length ? `\n${befunde.length} Befund(e)` : "\ngrün");
process.exit(befunde.length ? 1 : 0);
