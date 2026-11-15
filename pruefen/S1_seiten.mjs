// Prüfung der Seiten Erzählung (index), Karte (karta), Steckbrief (dzielnica) und Vergleich (porownanie) im Browser,
// in pl, en und de, über HTTP (skripte/entwicklung_server.mjs, Kacheln der Grundkarte eingehängt), nur 127.0.0.1.
//
// Je Sprache:
//   index      alle Fragen nacheinander in die Fenstermitte: Antwortsatz gefüllt (keine „b.d.“, kein Platzhalter),
//              Karte stellt die Ansicht ein (Legende gefüllt), Kopfzahlen und Fragen mit Zahl tragen eine Quelle,
//              Register mit 18 Zeilen und Zeile der Stadt, Sortieren ändert die Reihenfolge
//   karta      jede Zellebene, jede Färbung der Stadtteile, jede Punktebene: Legende mit Quelle, kein Fehler;
//              nach dem Einschalten der Luft Hinweis oben und Marke in der Legende genau dann, wenn powietrze.js
//              fixture: true trägt;
//              Hash nach einem Sprachwechsel unverändert (Zustand teilbar)
//   dzielnica  #st=01 … 18: Name mit römischer Ziffer, vier Gruppen, jede Kennzahl mit Quelle, Rang „von 18“,
//              kein NaN/undefined/Textschlüssel; hashchange wechselt den Stadtteil
//   porownanie sechs Zeilen mit Zahl in beiden Spalten, Quelle in der Tabellenunterschrift, Liste „nicht verglichen“
// Dazu je Seite und Zustand: keine Konsolen- oder Seitenfehler, keine fehlgeschlagenen Abrufe, kein Abruf außerhalb
// 127.0.0.1, bei 360 px Breite kein waagerechtes Scrollen.
//
// Aufruf: node pruefen/S1_seiten.mjs [--ziel KACHELORDNER]   Rückgabe 0 = grün, 1 = Befund.
import { chromium } from "playwright";
import { starten } from "../skripte/entwicklung_server.mjs";

const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const SPRACHEN = [["pl", ""], ["en", "en/"], ["de", "de/"]];
const SCHLUESSEL = /\b(kern|seiten|karte|erzaehlung)\.[a-z0-9_]+/;
const KAPUTT = /NaN|undefined|\{\{|\[object/;
const befunde = [];
let oks = 0;
const pruef = (ok, text) => { console.log((ok ? "  ok    " : "  BEFUND ") + text); if (ok) oks++; else befunde.push(text); return ok; };

const { server, url: HTTP } = await starten({ ziel: arg("--ziel") });
const browser = await chromium.launch();

async function seite(pfad, breite = 1280) {
  const ctx = await browser.newContext({ viewport: { width: breite, height: 860 }, reducedMotion: "reduce", locale: "pl-PL" });
  const page = await ctx.newPage();
  const fehler = [];
  // Warnungen von MapLibre zu Ausdrücken („found null“) zählen mit: dann fällt eine Stufenregel auf die Standardfarbe Schwarz
  page.on("console", (m) => { if (m.type() === "error" || (m.type() === "warning" && /found null|Expected value to be of type/.test(m.text()))) fehler.push("Konsole: " + m.text()); });
  page.on("pageerror", (e) => fehler.push("Seitenfehler: " + e.message));
  page.on("requestfailed", (r) => fehler.push("nicht geladen: " + r.url()));
  page.on("response", (r) => { if (r.status() >= 400) fehler.push(`HTTP ${r.status()}: ${r.url()}`); });
  await page.route("**/*", (r) => (r.request().url().startsWith(HTTP) ? r.continue() : (fehler.push("Fremdabruf: " + r.request().url()), r.fulfill({ status: 204, body: "" }))));
  await page.goto(HTTP + pfad, { waitUntil: "load" });
  await page.waitForFunction(() => window.KIEZ_KARTE ? window.KIEZ_KARTE.loaded() : true, null, { timeout: 30000 }).catch(() => fehler.push("Karte nach 30 s nicht geladen"));
  await page.waitForTimeout(400);
  return { ctx, page, fehler };
}
const ueber = (page) => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
const text = (page) => page.evaluate(() => document.body.innerText);
async function sauber(s, was) {
  const t = await text(s.page), k = t.match(SCHLUESSEL), x = t.match(KAPUTT);
  pruef(!s.fehler.length && !k && !x, `${was}: ohne Fehler, ohne Textschlüssel, ohne NaN/undefined${s.fehler.length ? ": " + s.fehler.slice(0, 3).join("; ") : ""}${k ? ", Schlüssel " + k[0] : ""}${x ? ", „" + x[0] + "“" : ""}`);
}
async function schmal(pfad, was, aktion) {
  const s = await seite(pfad, 360);
  if (aktion) { await s.page.evaluate(aktion); await s.page.waitForTimeout(1500); }
  const u = await ueber(s.page);
  pruef(u <= 0 && !s.fehler.length, `${was} bei 360 px: kein waagerechtes Scrollen (${u} px)${s.fehler.length ? ", Fehler: " + s.fehler.slice(0, 2).join("; ") : ""}`);
  await s.ctx.close();
}

for (const [lang, o] of SPRACHEN) {
  console.log(`\n[${lang}] index`);
  {
    const s = await seite(o + "index.html");
    const kopf = await s.page.evaluate(() => [...document.querySelectorAll("#ka-stadtzahlen > div")].map((d) => ({ zahl: d.querySelector("dd").firstChild.textContent, quelle: (d.querySelector(".ka-quelle") || {}).textContent || "" })));
    pruef(kopf.length === 5 && kopf.every((k) => /\d/.test(k.zahl) && k.quelle.length > 3), `${lang}/index: 5 Kopfzahlen, jede mit Quelle (${kopf.map((k) => k.zahl).join(" | ")})`);
    const fragen = await s.page.evaluate(() => [...document.querySelectorAll(".ka-frage[data-ansicht]")].map((f) => f.id));
    for (const id of fragen) {
      await s.page.evaluate((id) => { const f = document.getElementById(id); scrollTo(0, f.getBoundingClientRect().top + scrollY - innerHeight / 2 + 40); }, id);
      await s.page.waitForTimeout(1800);
      const r = await s.page.evaluate((id) => {
        const f = document.getElementById(id), a = f.querySelector(".ka-antwort");
        const zahl = /\d/.test(a.textContent);
        return { aktiv: f.classList.contains("ist-aktiv"), antwort: a.textContent.trim(), zahl, quelle: !!f.querySelector(".ka-quelle") && f.querySelector(".ka-quelle").textContent.length > 10,
          legende: document.getElementById("ka-buehne-legende").textContent.trim().slice(0, 60), bd: a.textContent.includes(window.KIEZ_I18N.t("kern.k_a")) };
      }, id);
      const luft = id === "ka-f-luft";
      pruef(r.aktiv && r.antwort.length > 20 && !r.bd && r.legende.length > 0 && (luft ? !r.zahl : r.zahl && r.quelle),
        `${lang}/index ${id}: Ansicht gesetzt (Legende „${r.legende}“), Antwort ${luft ? "ohne Zahl (Ausblick auf die Seite Luft)" : "mit Zahl und Quelle"}: „${r.antwort.slice(0, 90)}…“`);
    }
    const reg = await s.page.evaluate(() => {
      const zeilen = () => [...document.querySelectorAll("#ka-register tbody tr")].map((tr) => tr.querySelector("th").textContent);
      const vor = zeilen(); document.querySelector('#ka-register button[data-sort="ew"]').click(); const nach = zeilen();
      return { n: vor.length, stadt: !!document.querySelector("#ka-register tfoot tr"), sortiert: vor.join() !== nach.join(), caption: document.querySelector("#ka-register caption").textContent.length };
    });
    pruef(reg.n === 18 && reg.stadt && reg.sortiert && reg.caption > 20, `${lang}/index: Register mit ${reg.n} Zeilen und Zeile der Stadt, sortierbar, Quelle in der Unterschrift`);
    const bsp = await s.page.evaluate(() => !document.getElementById("beispieldaten").hidden);
    pruef(!bsp, `${lang}/index: kein Hinweis Beispieldaten (lädt keine Beispieldatei)`);
    await sauber(s, `${lang}/index nach allen Fragen`);
    await s.ctx.close();
    await schmal(o + "index.html", `${lang}/index`, "scrollTo(0, document.getElementById('ka-register').offsetTop)");
  }

  console.log(`\n[${lang}] karta`);
  {
    const s = await seite(o + "karta.html");
    const zell = await s.page.evaluate(() => [...document.querySelectorAll("#ka-zelle option")].map((x) => x.value).filter(Boolean));
    pruef(zell.length >= 11, `${lang}/karta: ${zell.length} Zellebenen zur Wahl (${zell.join(", ")})`);
    for (const v of zell) {
      await s.page.selectOption("#ka-zelle", v); await s.page.waitForTimeout(900);
      const l = await s.page.evaluate(() => { const b = document.getElementById("ka-leg-zelle"); return { sicht: !b.hidden, stufen: b.querySelectorAll(".fl-stufen li").length, quelle: (b.querySelector(".fl-quelle") || {}).textContent || "" }; });
      pruef(l.sicht && l.stufen >= 3 && l.quelle.length > 10, `${lang}/karta Zellebene ${v}: Legende mit ${l.stufen} Stufen und Quelle`);
    }
    await s.page.selectOption("#ka-zelle", "");
    for (const v of ["bebauung", "versiegelung", "zbk", "gruppen"]) {
      await s.page.check(`input[name="dz"][value="${v}"]`); await s.page.waitForTimeout(900);
      const l = await s.page.evaluate(() => { const b = document.getElementById("ka-leg-teile"); return { stufen: b.querySelectorAll(".fl-stufen li").length, quelle: (b.querySelector(".fl-quelle") || {}).textContent || "" }; });
      pruef(l.stufen >= 3 && l.quelle.length > 10, `${lang}/karta Stadtteile „${v}“: Legende mit ${l.stufen} Einträgen und Quelle`);
    }
    for (const v of ["haltestellen", "einrichtungen", "zbk", "rejestr", "zabytki"]) {
      await s.page.check(`input[name="pkt"][value="${v}"]`); await s.page.waitForTimeout(1200);
    }
    const p = await s.page.evaluate(() => ({ n: document.querySelectorAll("#ka-leg-punkte .fl-punkt").length, q: document.querySelectorAll("#ka-leg-punkte .fl-quelle:not(.fl-klausel)").length, kl: document.querySelectorAll("#ka-leg-punkte .fl-klausel").length, bsp: !document.getElementById("beispieldaten").hidden }));
    pruef(p.n === 5 && p.q === 5 && p.kl === 1 && !p.bsp, `${lang}/karta: fünf Punktebenen mit Quelle (ZBK mit Haftungsklausel), ohne Hinweis Beispieldaten`);
    // Ebene zabytki zeigt dieselbe Menge wie kamienice und modernizacja: nur Objekte mit Denkmalangabe (h === true)
    const zb = await s.page.evaluate(() => {
      const d = window.KIEZ_DENKMALE_ODBL, q = window.KIEZ_KARTE.getSource("pkt-zabytki"), fc = q ? q.serialize().data : null;
      const ist = fc && fc.features ? fc.features : [];
      return { soll: d.objekte.features.filter((f) => f.properties.h === true).length, ist: ist.length,
        nurH: ist.length > 0 && ist.every((f) => f.properties.h === true), leg: document.getElementById("ka-leg-punkte").textContent };
    });
    pruef(zb.ist === zb.soll && zb.nurH && zb.leg.includes(new Intl.NumberFormat(lang).format(zb.soll)),
      `${lang}/karta: Ebene zabytki mit ${zb.ist} Objekten, alle mit Denkmalangabe (soll ${zb.soll}), Legende nennt die Zahl`);
    // Ebene rejestr: Registerpunkte aus Wikidata, dieselbe Menge wie die Zahl auf kamienice (zaehlung.wd.in_stadt und
    // Summe der Tabelle je Delegatura, pruefen/S2_seiten.mjs); Quelle je Ebene mit Lizenz (CC0 bzw. ODbL)
    const rg = await s.page.evaluate(() => {
      const d = window.KIEZ_DENKMALE, q = window.KIEZ_KARTE.getSource("pkt-rejestr"), fc = q ? q.serialize().data : null;
      const ist = fc && fc.features ? fc.features : [], qu = [...document.querySelectorAll("#ka-leg-punkte .fl-quelle")].map((x) => x.textContent);
      return { fixture: d.fixture === true, soll: d.objekte.features.filter((f) => f.properties.q.includes("wd")).length, zahl: d.zaehlung.wd.in_stadt,
        ist: ist.length, nurWd: ist.every((f) => f.properties.q.includes("wd")), leg: document.getElementById("ka-leg-punkte").textContent,
        cc0: qu.some((x) => /Wikidata, CC0 1\.0/.test(x)), odbl: qu.some((x) => /ODbL/.test(x) && /OpenStreetMap/.test(x)),
        unten: (() => { const ids = window.KIEZ_KARTE.getStyle().layers.map((l) => l.id); return ids.indexOf("pkt-rejestr") > -1 && ids.indexOf("pkt-rejestr") < ids.indexOf("pkt-zabytki"); })() };
    });
    pruef(!rg.fixture && rg.ist === rg.soll && rg.ist === rg.zahl && rg.nurWd && rg.leg.includes(new Intl.NumberFormat(lang).format(rg.soll)),
      `${lang}/karta: Ebene rejestr mit ${rg.ist} Registerpunkten aus Wikidata (soll ${rg.soll}, zaehlung.wd.in_stadt ${rg.zahl}), Legende nennt die Zahl`);
    pruef(rg.cc0 && rg.odbl, `${lang}/karta: Register und OSM-Kennzeichnung je mit eigener Quelle (Wikidata, CC0 1.0; OpenStreetMap, ODbL)`);
    pruef(rg.unten, `${lang}/karta: Registerpunkte unter der OSM-Kennzeichnung (verdecken sie nicht)`);
    // Lage der Denkmalpunkte: bei sichtpruefung.geprueft true die Quote aus den Daten, sonst der Hinweis „ungeprüft“
    const sicht = await s.page.evaluate(() => {
      const leg = document.getElementById("ka-leg-punkte").textContent, T = window.KIEZ_TEXTE, F = window.KIEZ_I18N.fmt;
      return ["rejestr", "zabytki"].map((id) => {
        const d = id === "rejestr" ? window.KIEZ_DENKMALE : window.KIEZ_DENKMALE_ODBL, sp = d.sichtpruefung || {}, ok = sp.geprueft === true;
        const q = ok ? F.anteil(sp.ergebnis.lage.quote, 0) : null;
        return { id, ok, q, n: ok ? sp.ergebnis.n : null, hatQuote: ok && leg.includes(q) && leg.includes(F.zahl(sp.ergebnis.lage.daneben)),
          hatHinweis: leg.includes(T["erzaehlung." + id + "_ungeprueft"]) };
      });
    });
    for (const x of sicht) pruef(x.ok ? x.hatQuote && !x.hatHinweis : x.hatHinweis,
      `${lang}/karta: Ebene ${x.id}, Lage ${x.ok ? `in Stichprobe geprüft: Legende nennt ${x.q} (n = ${x.n}), kein Hinweis „ungeprüft“` : "ungeprüft: Hinweis in der Legende"}`);
    await s.page.check('input[name="pkt"][value="powietrze"]'); await s.page.waitForTimeout(1200);
    const l = await s.page.evaluate(() => ({ bsp: !document.getElementById("beispieldaten").hidden && document.getElementById("beispieldaten").offsetHeight > 0,
      marke: [...document.querySelectorAll("#ka-leg-punkte .fl-punkt")].some((x) => x.querySelector(".fl-beispiel")), hash: location.hash,
      fixture: !!(window.KIEZ_POWIETRZE && window.KIEZ_POWIETRZE.fixture === true), geladen: !!window.KIEZ_POWIETRZE }));
    // Hinweis Beispieldaten und Marke genau dann, wenn die nachgeladene Luftdatei fixture: true trägt
    pruef(l.geladen && l.bsp === l.fixture && l.marke === l.fixture,
      `${lang}/karta: nach dem Einschalten der Luft Hinweis Beispieldaten oben und Marke in der Legende ${l.fixture ? "sichtbar (fixture)" : "nicht sichtbar (echte Daten)"}`);
    // Klick in die Kartenmitte (Stadtteil oder Punkt): Popup mit Quelle
    const pop = await s.page.evaluate(() => new Promise((ok) => {
      const m = window.KIEZ_KARTE, c = m.getCanvas().getBoundingClientRect();
      m.fire("click", { point: { x: c.width / 2, y: c.height / 2 }, lngLat: m.getCenter(), originalEvent: {} });
      setTimeout(() => { const p = document.querySelector(".maplibregl-popup"); ok(p ? { q: !!p.querySelector(".ka-pop-q"), t: p.textContent.slice(0, 80) } : null); }, 600);
    }));
    pruef(!!pop && pop.q, `${lang}/karta: Klick in die Karte öffnet ein Popup mit Quelle${pop ? " („" + pop.t + "…“)" : ""}`);
    await sauber(s, `${lang}/karta nach allen Ebenen`);
    await s.ctx.close();
    // Hash: Zustand aus dem Link, unverändert nach dem Laden
    const h = "#thema=65p&st=18&dz=gruppen&pkt=haltestellen&k=12.0/50.0700/20.0300/0/0";
    const s2 = await seite(o + "karta.html" + h);
    const z = await s2.page.evaluate(() => ({ hash: location.hash, zelle: document.getElementById("ka-zelle").value, teil: document.getElementById("ka-teil").value }));
    pruef(z.hash === h && z.zelle === "65p" && z.teil === "18", `${lang}/karta: Zustand aus dem Hash (Ebene ${z.zelle}, Stadtteil ${z.teil}), Hash beim Laden unverändert`);
    await sauber(s2, `${lang}/karta mit Hash`);
    await s2.ctx.close();
    await schmal(o + "karta.html#thema=fuss:szkola&pkt=zbk", `${lang}/karta mit Ebenen`);
  }

  console.log(`\n[${lang}] dzielnica`);
  {
    const s = await seite(o + "dzielnica.html");
    const alle = [];
    for (let i = 1; i <= 18; i++) {
      const nr = String(i).padStart(2, "0");
      await s.page.evaluate((nr) => { location.hash = "st=" + nr; }, nr);
      await s.page.waitForTimeout(350);
      const r = await s.page.evaluate(() => {
        const karten = [...document.querySelectorAll("#ka-sb-werte .ka-wert")];
        return { ziffer: document.getElementById("ka-sb-ziffer").textContent, name: document.getElementById("ka-sb-name").textContent, wahl: document.getElementById("ka-teil").value,
          gruppen: document.querySelectorAll("#ka-sb-werte .ka-gruppe-titel").length, karten: karten.length,
          mitQuelle: karten.filter((k) => (k.querySelector(".ka-quelle") || {}).textContent?.length > 10).length,
          mitRang: karten.filter((k) => k.querySelector(".ka-rang")).length, nsp: document.querySelectorAll("#ka-sb-nsp .ka-wert").length,
          text: document.getElementById("ka-sb-werte").innerText + document.getElementById("ka-sb-nsp").innerText };
      });
      const ort = await s.page.evaluate((nr) => window.KIEZ_ORT.gliederung.teile.find((t) => t.nr === nr), nr);
      const ok = r.ziffer === ort.roemisch && r.name === ort.name && r.wahl === nr && r.gruppen === 4 && r.karten >= 12 && r.mitQuelle === r.karten && r.mitRang >= 10 && r.nsp === 4 && !KAPUTT.test(r.text) && !SCHLUESSEL.test(r.text);
      alle.push(ok);
      pruef(ok, `${lang}/dzielnica #st=${nr}: ${r.ziffer} ${r.name}, ${r.karten} Kennzahlen (mit Quelle ${r.mitQuelle}, mit Rang ${r.mitRang}), Delegatur-Werte ${r.nsp}`);
    }
    pruef(alle.filter(Boolean).length === 18, `${lang}/dzielnica: Steckbrief für alle 18 dzielnice`);
    const druck = await s.page.evaluate(() => [...document.styleSheets].some((sh) => { try { return [...sh.cssRules].some((r) => r.media && /print/.test(r.media.mediaText)); } catch { return false; } }));
    pruef(druck && await s.page.evaluate(() => !!document.getElementById("ka-drucken")), `${lang}/dzielnica: Druckknopf und Druckregeln (@media print) vorhanden`);
    await sauber(s, `${lang}/dzielnica nach 18 Wechseln`);
    await s.ctx.close();
    await schmal(o + "dzielnica.html#st=09", `${lang}/dzielnica #st=09`);
  }

  console.log(`\n[${lang}] porownanie`);
  {
    const s = await seite(o + "porownanie.html");
    const r = await s.page.evaluate(() => ({ zeilen: [...document.querySelectorAll("#ka-vergleich tbody tr")].map((tr) => [...tr.querySelectorAll("td")].map((td) => td.textContent)),
      caption: document.getElementById("ka-vg-quelle").textContent, nicht: document.querySelectorAll(".ka-weggelassen li").length, balken: document.querySelectorAll(".ka-vg-balken").length }));
    pruef(r.zeilen.length === 6 && r.zeilen.every((z) => /\d/.test(z[0]) && /\d/.test(z[1]) && /\d/.test(z[2])), `${lang}/porownanie: sechs Kennzahlen mit Zahl in beiden Spalten und Unterschied`);
    pruef(/Eurostat/.test(r.caption) && /CC BY 4\.0/.test(r.caption), `${lang}/porownanie: Quelle in der Tabellenunterschrift („${r.caption.slice(0, 70)}…“)`);
    pruef(r.nicht >= 5 && r.balken === 2, `${lang}/porownanie: ${r.nicht} nicht verglichene Kennzahlen mit Grund, Altersbalken für beide Städte`);
    await sauber(s, `${lang}/porownanie`);
    await s.ctx.close();
    await schmal(o + "porownanie.html", `${lang}/porownanie`);
  }
}

await browser.close();
server.close();
console.log(`\n${oks} ok, ${befunde.length} Befund(e)`);
console.log(befunde.length ? "Befund" : "grün");
process.exit(befunde.length ? 1 : 0);
