// Prüfung der Themenseiten Luft (powietrze), Wohnungsmarkt (mieszkania) und Klima (klimat), je Sprache pl/en/de,
// per HTTP (skripte/entwicklung_server.mjs, mit Grundkarte) und per file://, in den Breiten 360, 390 und 1280 px.
//
// Je Seite, Sprache, Weg und Breite:
//   - keine Konsolenfehler, keine Seitenfehler, keine fehlgeschlagene Anfrage (unter file:// zählen Kacheln nicht)
//   - kein seitlicher Überstand (scrollWidth − clientWidth = 0)
//   - in jeder Liniengrafik keine zwei Beschriftungen übereinander und keine angeschnitten (jeder Text ganz in der
//     Zeichenfläche); auf der Seite Luft nach jedem Kennwert-Knopf erneut, weil Grenzwerte mit dem Kennwert wechseln
//   - Beispieldaten unübersehbar: lädt die Seite eine Datei mit fixture: true, sind der Kasten der Seite (mit
//     fehlender Quelle, mindestens drei Sätze) und der Hinweis des Rahmens sichtbar und jede Abbildung trägt die
//     Marke; sonst sind beide verborgen und keine Marke ist zu sehen
//   - Grenzen sichtbar (mindestens vier Punkte) und Quellen sichtbar (mindestens zwei Einträge, Quellenvermerk der
//     Daten wörtlich enthalten)
//   - kein sichtbarer Platzhalter ({…}, {{…}}) und kein sichtbarer Textschlüssel (powietrze.…, mieszkania.…, klimat.…)
//   - keine Kausalwendung zum Verbot fester Brennstoffe (Liste wie pruefen/D7_powietrze.py)
//   - eine Zahl der Daten steht formatiert auf der Seite (Gegenprobe Daten → Seite)
//   - auf Touch-Breiten jeder Auswahlknopf mindestens 44 × 44 px
//   - axe-core ohne Verstoß (nur HTTP, 1280 und 390 px)
//
// Aufruf:  node pruefen/S3_themenseiten.mjs [--json <datei>]   Rückgabe 0 = grün, 1 = Befund.
// Braucht: node_modules mit playwright und axe-core, Chromium unter ~/.cache/ms-playwright. Kein Netz.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath, pathToFileURL } from "node:url";
import { starten } from "../skripte/entwicklung_server.mjs";

const HIER = path.dirname(fileURLToPath(import.meta.url)), WURZEL = path.resolve(HIER, "..");
const AXE = fs.readFileSync(path.join(WURZEL, "node_modules", "axe-core", "axe.min.js"), "utf8");
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const SEITEN = ["powietrze", "mieszkania", "klimat"], SPRACHEN = ["pl", "en", "de"], BREITEN = [360, 390, 1280];
const KAUSAL = {
  pl: /dzięki zakaz|z powodu zakaz|zakaz\w* spowodował|w wyniku zakaz|zakaz\w* sprawił/i,
  en: /because of the ban|thanks to the ban|due to the ban|the ban caused|as a result of the ban|the ban (led|has led) to/i,
  de: /wegen des Verbots|dank des Verbots|durch das Verbot|das Verbot bewirkte|infolge des Verbots|das Verbot führte/i,
};

// Daten wie die Seite sie lädt
function laden(datei) {
  const box = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(WURZEL, "daten", datei), "utf8"), box);
  return Object.values(box.window)[0];
}
const P = laden("powietrze.js"), M = laden("mieszkania_odbl.js"), K = laden("klimat.js");
const NF = (l, o) => new Intl.NumberFormat({ pl: "pl-PL", en: "en-GB", de: "de-DE" }[l], o);
const mJahr = M.jahre.filter((j) => j !== M.eingabe.jahr_teilweise).at(-1);
const ERWARTET = {   // Vermerk wörtlich, eine Zahl der Daten in der Formatierung der Sprache, Beispieldaten ja/nein
  powietrze: { vermerk: P.quelle.vermerk, beispiel: P.fixture === true,
    zahl: (l) => NF(l, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(P.stacje.find((s) => s.przed_po.pm10_srednia && s.przed_po.pm10_srednia.przed != null).przed_po.pm10_srednia.przed) },
  mieszkania: { vermerk: M.quelle.vermerk, beispiel: M.fixture === true, zahl: (l) => NF(l).format(M.stadt[mJahr].ogolem.median) },
  klimat: { vermerk: K.quelle.vermerk, beispiel: K.fixture === true,
    zahl: (l) => NF(l, { style: "percent", minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(K.stadt.anteil.bebauung_verkehr / 100) },
};

// Beschriftungen der Liniengrafiken: Paare, die sich überdecken, und Texte, die über den Rand der Zeichenfläche ragen
function texteLage() {
  const raus = [];
  document.querySelectorAll("svg.ts-linien").forEach((svg) => {
    const f = svg.getBoundingClientRect(), z = (svg.closest(".ts-zeichnung") || svg).getBoundingClientRect();
    const rand = { l: Math.max(f.left, z.left), r: Math.min(f.right, z.right), o: Math.max(f.top, z.top), u: Math.min(f.bottom, z.bottom) };
    const t = [...svg.querySelectorAll("text")].map((e) => ({ s: e.textContent, r: e.getBoundingClientRect() })).filter((x) => x.r.width > 0);
    t.forEach((a) => { if (a.r.left < rand.l - 0.5 || a.r.right > rand.r + 0.5 || a.r.top < rand.o - 0.5 || a.r.bottom > rand.u + 0.5) raus.push("angeschnitten „" + a.s + "“"); });
    for (let i = 0; i < t.length; i++) for (let j = i + 1; j < t.length; j++) {
      const a = t[i].r, b = t[j].r;
      if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 0.5 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 0.5) raus.push("„" + t[i].s + "“ über „" + t[j].s + "“");
    }
  });
  return raus;
}

const befunde = [], zeilen = [];
let laeufe = 0;
function pruef(ok, text) { if (!ok) befunde.push(text); return ok; }

const { server, url: BASIS } = await starten({ port: 0 });
const browser = await chromium.launch();
try {
  for (const seite of SEITEN) for (const l of SPRACHEN) for (const weg of ["http", "file"]) for (const b of BREITEN) {
    const rel = (l === "pl" ? "" : l + "/") + seite + ".html";
    const ziel = weg === "http" ? BASIS + rel : pathToFileURL(path.join(WURZEL, rel)).href;
    const ctx = await browser.newContext({ viewport: { width: b, height: 860 }, isMobile: b < 500, hasTouch: b < 500 });
    const p = await ctx.newPage(), fehler = [];
    p.on("console", (m) => { if (m.type() === "error") fehler.push("console: " + m.text()); });
    p.on("pageerror", (e) => fehler.push("pageerror: " + e.message));
    p.on("requestfailed", (r) => { if (!(weg === "file" && /grundkarte\//.test(r.url()))) fehler.push("failed: " + r.url()); });
    await p.route(/^https?:\/\/(?!127\.0\.0\.1)/, (r) => { fehler.push("fremd: " + r.request().url()); r.abort(); });
    await p.goto(ziel, { waitUntil: "load" });
    await p.waitForTimeout(seite === "klimat" ? 1200 : 400);
    const m = await p.evaluate(() => {
      const sicht = (e) => !!e && !e.hidden && e.getClientRects().length > 0 && getComputedStyle(e).display !== "none";
      const kasten = document.querySelector(".ts-beispiel"), rahmen = document.getElementById("beispieldaten");
      const zonen = [...document.querySelectorAll(".ts-abbildung,.ts-beispielzone")];
      const marken = zonen.map((z) => getComputedStyle(z, "::before").content).filter((c) => c && c !== "none" && c !== '""' && c !== "normal");
      const knoepfe = [...document.querySelectorAll(".ts-knopf")].map((k) => k.getBoundingClientRect()).filter((r) => r.width > 0);
      return {
        ueberstand: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        kasten: sicht(kasten), kastenSaetze: kasten ? kasten.querySelectorAll("p").length : 0, rahmen: sicht(rahmen),
        zonen: zonen.length, marken: marken.length,
        grenzen: document.querySelectorAll(".ts-grenzen li").length,
        quellen: document.querySelectorAll(".ts-quellen dt").length,
        quellenText: (document.querySelector(".ts-quellen") || {}).textContent || "",
        text: document.querySelector("main").innerText,
        klein: knoepfe.filter((r) => r.width < 44 || r.height < 44).length, knoepfe: knoepfe.length,
      };
    });
    // Beschriftungen: Ausgangszustand, dann jeder Kennwert-Knopf der Grafik (Seite Luft)
    const lage = [], wahl = await p.$$("#p-wahl .ts-knopf");
    lage.push(...(await p.evaluate(texteLage)).map((x) => "Start: " + x));
    for (const k of wahl) {
      await k.click();
      await p.waitForTimeout(60);
      const name = (await k.textContent()).trim();
      lage.push(...(await p.evaluate(texteLage)).map((x) => name + ": " + x));
    }
    if (wahl.length) { await wahl[0].click(); await p.waitForTimeout(60); }
    const e = ERWARTET[seite], wo = `${rel} ${weg} ${b}px`;
    laeufe++;
    const ok = [
      pruef(!fehler.length, `${wo}: ${fehler.length} Fehler (${fehler.slice(0, 2).join("; ")})`),
      pruef(m.ueberstand === 0, `${wo}: seitlicher Überstand ${m.ueberstand} px`),
      pruef(!lage.length, `${wo}: Beschriftung der Grafik (${lage.length}): ${[...new Set(lage)].slice(0, 3).join("; ")}`),
      e.beispiel
        ? pruef(m.kasten && m.kastenSaetze >= 4 && m.rahmen && m.zonen > 0 && m.marken === m.zonen,
            `${wo}: Beispielkennzeichnung unvollständig (Kasten ${m.kasten}, Sätze ${m.kastenSaetze}, Rahmen ${m.rahmen}, Marken ${m.marken}/${m.zonen})`)
        : pruef(!m.kasten && !m.rahmen && m.marken === 0, `${wo}: Beispielkennzeichnung ohne Beispieldaten`),
      pruef(m.grenzen >= 4, `${wo}: nur ${m.grenzen} Grenzen`),
      pruef(m.quellen >= 2 && m.quellenText.includes(e.vermerk), `${wo}: Quellen unvollständig (${m.quellen} Einträge, Vermerk ${m.quellenText.includes(e.vermerk)})`),
      pruef(!/\{\{|\{[a-z_]+\}/.test(m.text) && !/\b(powietrze|mieszkania|klimat)\.[a-z_]+\b/.test(m.text), `${wo}: sichtbarer Platzhalter oder Schlüssel`),
      pruef(!KAUSAL[l].test(m.text), `${wo}: Kausalwendung`),
      pruef(m.text.includes(e.zahl(l)), `${wo}: Zahl aus den Daten (${e.zahl(l)}) nicht auf der Seite`),
      pruef(b >= 500 || m.klein === 0, `${wo}: ${m.klein} von ${m.knoepfe} Auswahlknöpfen unter 44 px`),
    ];
    let axe = "–";
    if (weg === "http" && b !== 360) {
      await p.addScriptTag({ content: AXE });
      const v = await p.evaluate(async () => (await window.axe.run(document, { resultTypes: ["violations"] })).violations.map((x) => x.id + " (" + x.nodes.length + ")"));
      ok.push(pruef(!v.length, `${wo}: axe ${v.join(", ")}`));
      axe = v.length ? v.join(", ") : "0";
    }
    zeilen.push({ seite: rel, weg, breite: b, ok: ok.every(Boolean), ueberstand: m.ueberstand, beschriftung: lage.length, beispiel: e.beispiel, marken: `${m.marken}/${m.zonen}`,
      grenzen: m.grenzen, quellen: m.quellen, fehler: fehler.length, axe });
    console.log(`${ok.every(Boolean) ? "  ok   " : "  FEHLT"} ${wo}: Überstand ${m.ueberstand}, Beschriftung ${lage.length ? lage.length + " Befund(e)" : "frei"}, Beispiel ${e.beispiel ? "ja" : "nein"} (Marken ${m.marken}/${m.zonen}), Grenzen ${m.grenzen}, Quellen ${m.quellen}, axe ${axe}`);
    await ctx.close();
  }
} finally {
  await browser.close();
  server.close();
}
if (arg("--json")) fs.writeFileSync(arg("--json"), JSON.stringify({ laeufe, befunde, zeilen }, null, 1));
console.log(`\n${laeufe} Läufe, ${befunde.length} Befund(e)`);
befunde.forEach((x) => console.log("  " + x));
process.exit(befunde.length ? 1 : 0);
