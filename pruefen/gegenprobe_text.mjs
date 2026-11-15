// Textabzug für die Gegenprobe Potsdam (pruefen/gegenprobe_potsdam.sh): jede Seite *.html der Wurzel per file://
// laden, warten bis sie fertig ist, und den sichtbaren Text (document.body.innerText) samt Titel ausgeben.
// Zwei Wurzeln mit gleichem Abzug zeigen denselben Text. Kein Netz: Fremdabrufe beantwortet der Browser selbst
// mit einer leeren Antwort (wie pruefen/seiten.mjs in Potsdam).
//
// Aufruf: node pruefen/gegenprobe_text.mjs --wurzel <ordner>   Ausgabe auf stdout, Rückgabe 1 bei Ladefehler.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const WURZEL = path.resolve(arg("--wurzel", "."));
const LEERBILD = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=", "base64");
const fremd = (u) => /\.pbf(\?|$)/.test(u) ? { status: 200, contentType: "application/x-protobuf", body: Buffer.alloc(0) } : { status: 200, contentType: "image/png", body: LEERBILD };

const seiten = fs.readdirSync(WURZEL).filter((f) => f.endsWith(".html")).sort();
const browser = await chromium.launch();
let fehler = 0;
for (const s of seiten) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce", locale: "de-DE", timezoneId: "Europe/Berlin" });
  const page = await ctx.newPage();
  const konsole = [];
  page.on("pageerror", (e) => konsole.push("Seitenfehler: " + e.message));
  await page.route("**/*", (r) => r.request().url().startsWith("file://") ? r.continue() : r.fulfill(fremd(r.request().url())));
  try {
    await page.goto(pathToFileURL(path.join(WURZEL, s)).href, { waitUntil: "load", timeout: 60000 });
    await page.waitForFunction(() => window.KIEZ_BEREIT !== false, null, { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(2500);
    const text = await page.evaluate(() => document.title + "\n" + document.body.innerText);
    console.log("== " + s);
    console.log(text.replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim());
    for (const k of konsole) console.log("!! " + k);
  } catch (e) {
    console.log("== " + s + "\n!! nicht geladen: " + e.message.split("\n")[0]);
    fehler++;
  }
  await ctx.close();
}
await browser.close();
process.exit(fehler ? 1 : 0);
