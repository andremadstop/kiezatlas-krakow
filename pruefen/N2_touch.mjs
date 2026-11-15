// Prüfung Kopfleiste auf einem Touch-Handy (Playwright-Gerät „iPhone 13“, 390 px, pointer:coarse): index, planer, karta
// in pl, en, de. Je Seite: Medienabfrage pointer:coarse greift, kein Navigationslink abgeschnitten, kein Überstand,
// Karte bzw. Werkzeugleiste unter der Kopfleiste, kein Luftbild-Schalter, keine Konsolenfehler.
// Aufruf: node pruefen/N2_touch.mjs [BILD.png]   (Bildschirmfoto von planer.html auf Polnisch, wenn angegeben)
import { chromium, devices } from "playwright";
import { starten } from "../skripte/entwicklung_server.mjs";
const { server, url } = await starten({});
const b = await chromium.launch(); let bef = 0;
for (const pre of ["", "en/", "de/"]) for (const s of ["index", "planer", "karta"]) {
  const ctx = await b.newContext({ ...devices["iPhone 13"] }); const p = await ctx.newPage();
  const fehler = []; p.on("pageerror", (e) => fehler.push(String(e))); p.on("console", (m) => { if (m.type() === "error") fehler.push(m.text()); });
  await p.goto(url + pre + s + ".html"); await p.waitForTimeout(2500);
  const r = await p.evaluate(() => {
    const vw = document.documentElement.clientWidth, k = document.querySelector(".kopfleiste").getBoundingClientRect();
    const raus = [...document.querySelectorAll(".kopfleiste nav a")].filter((e) => { const r = e.getBoundingClientRect(), n = e.closest("nav").getBoundingClientRect(); return !(r.left >= Math.max(0, n.left) - .5 && r.right <= Math.min(vw, n.right) + .5 && r.top >= k.top - .5 && r.bottom <= k.bottom + .5); }).map((e) => e.textContent.trim());
    const w = document.querySelector("#werkzeug, .werkzeug, .ka-buehne__karte, .maplibregl-map"); const wr = w ? w.getBoundingClientRect() : null;
    const luft = [...document.querySelectorAll("button, label")].filter((e) => e.offsetParent && /luftbild|ortofoto|aerial/i.test(e.textContent)).length;
    return { coarse: matchMedia("(pointer:coarse)").matches, vw, kopf: Math.round(k.height), raus, ueber: document.documentElement.scrollWidth - vw, karteOben: wr ? Math.round(wr.top + scrollY) : null, luft };
  });
  const ok = r.coarse && !r.raus.length && r.ueber <= 0 && !fehler.length && !r.luft && (r.karteOben === null || r.karteOben >= r.kopf);
  if (!ok) bef++;
  console.log(`${ok ? "  ok   " : "  FEHLT"} iPhone 13 (Touch) ${pre}${s}.html: pointer:coarse ${r.coarse}, Breite ${r.vw}, Kopfleiste ${r.kopf} px, abgeschnitten ${r.raus.length}, Überstand ${r.ueber}, Karte/Werkzeug ab ${r.karteOben} px, Luftbild-Schalter ${r.luft}, Fehler ${fehler.length}`);
  if (pre === "" && s === "planer" && process.argv[2]) await p.screenshot({ path: process.argv[2] });
  await ctx.close();
}
await b.close(); server.close(); console.log(`${bef} Befund(e)`); process.exit(bef ? 1 : 0);
