// Bildschirmfotos aller Seiten einer Sprache (Standard pl) für die Belege: Desktop 1440 px und Handy 390 px,
// headless Chromium, reduzierte Bewegung, ganze Seite. Die Seiten kommen über den Entwicklungsserver
// (skripte/entwicklung_server.mjs, nur 127.0.0.1) mit der Grundkarte aus dem Kachelordner; die Seitenliste aus
// config/krakow.yaml (seiten). Kartenseiten: gewartet wird, bis die Karte geladen ist und alle Kacheln da sind.
// Schreibt <ziel>/<seite>-1440.png, <ziel>/<seite>-390.png und <ziel>/README.md (Übersicht mit Commit, Ansichten,
// Hinweis Beispieldaten und Konsolenmeldungen je Seite). Kein Netz außer 127.0.0.1.
//
//   node skripte/bildschirmfotos.mjs --ziel belege/bildschirm-20261113 [--lang pl]
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { starten } from "./entwicklung_server.mjs";

const WURZEL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const ZIEL = path.resolve(WURZEL, arg("--ziel", "belege/bildschirm"));
const LANG = arg("--lang", "pl");
const ANSICHTEN = [
  { name: "1440", width: 1440, height: 900, mobil: false },
  { name: "390", width: 390, height: 844, mobil: true },
];

// Seitenliste aus der Ortskonfiguration (Zeile „seiten: [ … ]“, über mehrere Zeilen)
const yaml = fs.readFileSync(path.join(WURZEL, "config", "krakow.yaml"), "utf-8");
const m = /^seiten:\s*\[([^\]]*)\]/m.exec(yaml);
if (!m) { console.error("seiten in config/krakow.yaml nicht gefunden"); process.exit(1); }
const SEITEN = m[1].split(",").map((s) => s.trim().replace(/^"|"$/g, "")).filter(Boolean);

const git = (...a) => execFileSync("git", ["-C", WURZEL, ...a], { encoding: "utf-8" }).trim();
const commit = git("rev-parse", "HEAD");
const sauber = git("status", "--porcelain") === "";

fs.mkdirSync(ZIEL, { recursive: true });
const { server, url: BASIS } = await starten({ port: 0 });
const browser = await chromium.launch();
const zeilen = [];
let fehlerGesamt = 0;
try {
  for (const seite of SEITEN) {
    const zeile = { seite, dateien: [], beispiel: [], konsole: [], karte: [] };
    for (const a of ANSICHTEN) {
      const ctx = await browser.newContext({ viewport: { width: a.width, height: a.height }, isMobile: a.mobil,
        hasTouch: a.mobil, deviceScaleFactor: 1, reducedMotion: "reduce", locale: "pl-PL" });
      const page = await ctx.newPage();
      const meldungen = [];
      page.on("console", (c) => { if (c.type() === "error") meldungen.push(c.text()); });
      page.on("pageerror", (e) => meldungen.push(String(e)));
      const pfad = (LANG === "pl" ? "" : LANG + "/") + seite + ".html";
      await page.goto(BASIS + pfad, { waitUntil: "load" });
      let karte = "keine";
      if (await page.evaluate(() => !!document.getElementById("karte") || !!window.maplibregl)) {
        try {
          await page.waitForFunction(() => window.KIEZ_KARTE && window.KIEZ_KARTE.loaded() && window.KIEZ_KARTE.areTilesLoaded(),
            null, { timeout: 30000 });
          karte = "geladen";
        } catch { karte = "nicht geladen (30 s)"; }
      }
      await page.waitForTimeout(500);
      const beispiel = await page.evaluate(() => {
        const b = document.getElementById("beispieldaten");
        return !!(b && !b.hidden && b.offsetParent !== null);
      });
      const datei = `${seite}-${a.name}.png`;
      await page.screenshot({ path: path.join(ZIEL, datei), fullPage: true });
      zeile.dateien.push(datei); zeile.beispiel.push(beispiel); zeile.konsole.push(meldungen.length); zeile.karte.push(karte);
      fehlerGesamt += meldungen.length;
      for (const t of meldungen) console.log(`  Konsole ${seite} ${a.name}: ${t}`);
      console.log(`ok    ${seite} ${a.name} px: ${datei} (Karte ${karte}, Hinweis Beispieldaten ${beispiel ? "ja" : "nein"}, ${meldungen.length} Konsolenfehler)`);
      await ctx.close();
    }
    zeilen.push(zeile);
  }
} finally {
  await browser.close();
  server.close();
}

const ja = (v) => (v ? "ja" : "nein");
const tab = zeilen.map((z) => `| \`${z.seite}\` | \`${z.dateien[0]}\` | \`${z.dateien[1]}\` | ${z.karte[0]} / ${z.karte[1]} | ${ja(z.beispiel[0])} / ${ja(z.beispiel[1])} | ${z.konsole[0]} / ${z.konsole[1]} |`).join("\n");
const readme = `# Bildschirmfotos aller Seiten (${LANG})

Erzeugt von \`skripte/bildschirmfotos.mjs\` (nicht von Hand ändern) auf Commit \`${commit.slice(0, 7)}\`
(${sauber ? "sauberer Arbeitsstand" : "mit offenen Änderungen"}). Headless Chromium über Playwright, reduzierte Bewegung,
ganze Seite, Pixelverhältnis 1. Ansichten: Desktop 1440 × 900 px, Handy 390 × 844 px (mobil, Touch). Die Seiten
kommen über \`skripte/entwicklung_server.mjs\` mit der Grundkarte aus dem Kachelordner; bei Kartenseiten wartet der
Lauf, bis die Karte geladen ist und alle Kacheln da sind. Seitenliste: \`seiten\` in \`config/krakow.yaml\`
(${SEITEN.length} Seiten). Spalten mit zwei Werten: Desktop / Handy.

„Hinweis Beispieldaten“ heißt: der Hinweis des Seitenrahmens (\`#beispieldaten\`) war beim Foto sichtbar. Ob eine
Seite Beispieldaten zeigt, steht in \`docs/rundgang.md\`, „Datenstand je Thema“.

| Seite | Desktop | Handy | Karte | Hinweis Beispieldaten | Konsolenfehler |
|---|---|---|---|---|---|
${tab}

Grenzen: Nur Polnisch; Englisch und Deutsch prüfen \`pruefen/seiten.mjs\` und die Paketprüfungen im Browser, ohne Foto.
Die Fotos zeigen den Zustand nach dem Laden ohne Bedienung (keine geöffneten Fragen, keine 3D-Gebäude). Die Seite
\`404\` ist direkt aufgerufen.
`;
fs.writeFileSync(path.join(ZIEL, "README.md"), readme);
console.log(`${zeilen.length} Seiten × ${ANSICHTEN.length} Ansichten, ${fehlerGesamt} Konsolenfehler; Übersicht ${path.relative(WURZEL, path.join(ZIEL, "README.md"))}`);
