/* Kiezatlas: Startseite als Erzählung über Kraków (index.html). Kopfzahlen, Fragen mit Kameraziel auf der Karte,
   Register der Stadtteile. Jede Frage stellt die Karte ein (Färbung, Ebene, Ausschnitt), sobald sie in der Mitte
   des Fensters steht; die Antwortsätze sind Vorlagen aus den Texten, die Zahlen kommen live aus daten/*.js.
   Gitter (zellen_odbl.js) und Fußwege (erreichbar_fuss_odbl.js) werden erst zur ersten Frage, die sie braucht,
   nachgeladen (Startgewicht). Hier steht keine Ergebniszahl von Hand; Schwellen sind Methode und stehen im Text. */
(function () {
"use strict";
var KF = window.KIEZ_KARTENFELD, T = window.KIEZ_THEMEN, I18N = window.KIEZ_I18N, ORT = window.KIEZ_ORT;
if (!KF || !T || !document.getElementById("karte")) return;
var tt = I18N.t, fmt = T.fmt, fmt1 = T.fmt1, el = KF.el, NB = " ";
// Prozentzeichen nach Landesbrauch wie fmt.anteil (pl, en ohne Leerzeichen, de mit geschütztem)
var PZ = I18N.fmt.anteil(1, 0).replace(/^[0-9]+/, "");
var SB = window.KIEZ_STECKBRIEF, SD = window.KIEZ_STECKBRIEF_DZIELNICE, GK = window.KIEZ_GEB_KENNZAHLEN, GD = window.KIEZ_GEB_DZIELNICE;
var SA = window.KIEZ_SANIERUNG;
var TEILE = ORT.gliederung.teile, NRS = TEILE.map(function (t) { return t.nr; });
var FUSS_SCHWELLE = 500;   // Meter Fußweg zur Haltestelle (Methode, im Antworttext genannt)
function teil(nr) { return TEILE.filter(function (t) { return t.nr === nr; })[0]; }
function anzeige(nr) { var t = teil(nr); return t ? I18N.sprachwert(t.anzeige) : nr; }
function fuelle(id, html) { var n = document.getElementById(id); if (n) n.textContent = html; }
// Antwortsatz: Vorlage mit {platzhaltern}, Werte fett (als Text, nie als HTML)
// Vorzeichen: typografisches Minus (U+2212) statt Bindestrich, wie es Intl für pl/en/de liefert
function minus(s) { return String(s).replace(/^-/, "\u2212"); }
function satz(id, schluessel, werte) {
  var n = document.getElementById(id); if (!n) return;
  n.textContent = "";
  var vorlage = tt(schluessel), re = /\{(\w+)\}/g, i = 0, m;
  while ((m = re.exec(vorlage))) {
    n.appendChild(document.createTextNode(vorlage.slice(i, m.index)));
    n.appendChild(el("b", null, werte[m[1]] == null ? tt("kern.k_a") : String(werte[m[1]])));
    i = re.lastIndex;
  }
  n.appendChild(document.createTextNode(vorlage.slice(i)));
}
function maxNr(f) { var best = null; NRS.forEach(function (nr) { var v = f(nr); if (v != null && (best == null || v > f(best))) best = nr; }); return best; }
function minNr(f) { var best = null; NRS.forEach(function (nr) { var v = f(nr); if (v != null && (best == null || v < f(best))) best = nr; }); return best; }
function sd(nr) { return SD && SD.stadtteile[nr] && SD.stadtteile[nr].gitter && SD.stadtteile[nr].gitter.a_ges >= SD.methode.mindestfallzahl ? SD.stadtteile[nr] : null; }

// ---------- Kopfzahlen
(function () {
  var box = document.getElementById("ka-stadtzahlen"); if (!box) return;
  function zahl(titel, wert, einheit, quelle) {
    var d = el("div"), dt = el("dt", null, titel), dd = el("dd", null, wert);
    if (einheit) dd.appendChild(el("small", null, einheit));
    dd.appendChild(el("span", "ka-quelle", quelle));
    d.appendChild(dt); d.appendChild(dd); box.appendChild(d);
  }
  if (SB) zahl(tt("erzaehlung.kz_einwohner"), fmt.format(SB.stadt.nsp.einwohner), "", tt("erzaehlung.quelle_nsp_kurz"));
  if (SB) zahl(tt("erzaehlung.kz_flaeche"), fmt1.format(SB.stadt.flaeche_km2), "km²", tt("erzaehlung.quelle_prg_kurz"));
  zahl(tt("erzaehlung.kz_teile"), fmt.format(TEILE.length), "", I18N.sprachwert(ORT.karte.teile_bildzeile));
  if (GK) zahl(tt("erzaehlung.kz_gebaeude"), fmt.format(GK.stadt.anzahl), "", tt("erzaehlung.quelle_bdot_kurz"));
  if (SA) zahl(tt("erzaehlung.kz_zbk"), fmt.format(SA.liste.eintraege), "", tt("erzaehlung.quelle_zbk_kurz", { datum: I18N.fmt.datum(SA.stand) }));
})();

// ---------- Antworten (live aus den Daten)
var Q = {};   // je Frage: Kameraziel und Ansicht
(function () {
  // 1 Gliederung
  var gruppen = ORT.gliederung.gruppen.map(function (g) { return g.name; });
  satz("ka-a-teile", "erzaehlung.a_teile", { n: fmt.format(TEILE.length), g: fmt.format(gruppen.length), namen: gruppen.join(", "), flaeche: SB ? fmt1.format(SB.stadt.flaeche_km2) + NB + "km²" : null });
  Q.teile = { ziel: null, ansicht: "gruppen" };
  // 2 Einwohner
  if (SB) satz("ka-a-einwohner", "erzaehlung.a_einwohner", { nsp: fmt.format(SB.stadt.nsp.einwohner), datum: I18N.fmt.datum(SB.quellen.nsp2021.stichtag),
    gitter: fmt.format(SB.stadt.gitter.einwohner), abw: minus(fmt1.format(SB.stadt.gitter.abweichung_nsp_proz)), zellen: fmt.format(SB.stadt.gitter.zellen) });
  Q.einwohner = { ziel: null, ansicht: "gitter:ew" };
  // 3 Dichte
  var dicht = maxNr(function (nr) { var s = sd(nr); return s ? s.dichte_gitter : null; });
  var duenn = minNr(function (nr) { var s = sd(nr); return s ? s.dichte_gitter : null; });
  if (dicht) satz("ka-a-dichte", "erzaehlung.a_dichte", { teil: anzeige(dicht), wert: fmt.format(SD.stadtteile[dicht].dichte_gitter), duenn: anzeige(duenn),
    wert2: fmt.format(SD.stadtteile[duenn].dichte_gitter), stadt: fmt.format(SB.stadt.dichte_gitter) });
  Q.dichte = { ziel: dicht, ansicht: "gitter:ew" };
  // 4 Ältere
  var alt = maxNr(function (nr) { var s = sd(nr); return s ? s.gitter.q_65p : null; });
  var jung = minNr(function (nr) { var s = sd(nr); return s ? s.gitter.q_65p : null; });
  if (alt) satz("ka-a-alter", "erzaehlung.a_alter", { teil: anzeige(alt), wert: fmt1.format(SD.stadtteile[alt].gitter.q_65p) + PZ, jung: anzeige(jung),
    wert2: fmt1.format(SD.stadtteile[jung].gitter.q_65p) + PZ, stadt: fmt1.format(SB.stadt.gitter.q_65p) + PZ });
  Q.alter = { ziel: alt, ansicht: "gitter:65p" };
  // 5 Gebäude
  var dichtGeb = GD ? maxNr(function (nr) { var g = GD.stadtteile[nr]; return g && g.bebauungsdichte ? g.bebauungsdichte.wert : null; }) : null;
  if (GK) satz("ka-a-gebaeude", "erzaehlung.a_gebaeude", { n: fmt.format(GK.stadt.anzahl), wohn: fmt.format(GK.stadt.wohngebaeude), mehr: fmt.format(GK.stadt.wohn_art.mehr),
    median: fmt1.format(GK.stadt.geschosse_median_wohn), teil: dichtGeb ? anzeige(dichtGeb) : null,
    wert: dichtGeb ? fmt1.format(GD.stadtteile[dichtGeb].bebauungsdichte.wert) + PZ : null, stadt: fmt1.format(GK.stadt.bebauungsdichte.wert) + PZ });
  Q.gebaeude = { ziel: dichtGeb, ansicht: "teile:bebauung" };
  // 6 Erreichbarkeit: wird mit den Fußwegen nachgeladen
  Q.takt = { ziel: null, ansicht: "fuss:haltestelle_takt" };
  // 7 Luft: Ausblick ohne Zahl (die Werte stehen auf der Seite Luft, mit Abzeichen „orientacyjnie“)
  Q.luft = { ziel: null, ansicht: "gruppen" };
  // 8 Sanierung
  var zbkMax = SA ? maxNr(function (nr) { var e = SA.liste.je_dzielnica[nr]; return e ? e.n : null; }) : null;
  if (SA) satz("ka-a-zbk", "erzaehlung.a_zbk", { n: fmt.format(SA.liste.eintraege), datum: I18N.fmt.datum(SA.stand), krakow: fmt.format(SA.liste.miejscowosc.krakow),
    teil: zbkMax ? anzeige(zbkMax) : null, wert: zbkMax ? fmt.format(SA.liste.je_dzielnica[zbkMax].n) : null,
    blok: fmt.format(SA.typologie.stadt.blok), mfh: fmt.format(SA.typologie.stadt.mfh), kmin: fmt.format(SA.typologie.kriterien.geschosse_min) });
  // Grenzen der Liste: Einträge ohne Wohnnutzung (Art ohne M) und ohne alleiniges Eigentum der Gemeinde, aus den Zählungen der Liste
  if (SA) {
    var ohneWohnen = 0, nichtGmina = 0;
    Object.keys(SA.liste.je_art).forEach(function (a) { if (a.indexOf("M") < 0) ohneWohnen += SA.liste.je_art[a]; });
    Object.keys(SA.liste.je_eigentum).forEach(function (e) { if (e !== "gmina") nichtGmina += SA.liste.je_eigentum[e]; });
    satz("ka-a-zbk-grenzen", "erzaehlung.a_zbk_grenzen", { ohne_wohnen: fmt.format(ohneWohnen), nicht_gmina: fmt.format(nichtGmina) });
  }
  // Bedingungen der Gmina Miejska Kraków zur Weiterverwendung: Quelle mit Erstellungs- und Abrufzeit, Hinweis auf die
  // Verarbeitung und Zakres odpowiedzialności wörtlich; gilt für alle ZBK-Werte der Seite (Kachel, Antwort, Register)
  var fZbk = document.getElementById("ka-f-zbk");
  if (SA && fZbk && SA.quellen.zbk.vermerk) { var q = el("p", "ka-quelle", SA.quellen.zbk.vermerk); q.lang = "pl"; fZbk.appendChild(q); }
  // Haftungsklausel wörtlich und sichtbar (Bedingung der Weiterverwendung), als benannter, abgesetzter Block
  if (SA && fZbk && SA.quellen.zbk.odpowiedzialnosc) {
    var zs = el("div", "ka-zastrzezenie"); zs.appendChild(el("p", "ka-zastrzezenie__titel", tt("erzaehlung.zbk_zastrzezenie")));
    var zq = el("p", "ka-quelle", SA.quellen.zbk.odpowiedzialnosc); zq.lang = "pl"; zs.appendChild(zq); fZbk.appendChild(zs);
  }
  Q.zbk = { ziel: zbkMax, ansicht: "teile:zbk" };
})();

// ---------- Karte und Ansichten
var map = KF.bauen(document.getElementById("karte"));
var leg = document.getElementById("ka-buehne-legende");
var ZK = null;   // Klassen der Gitterthemen, sobald das Gitter da ist
function gitter(fertig) {
  if (window.KIEZ_ZELLEN && ZK) { fertig(); return; }
  KF.laden("daten/zellen_odbl.js", "KIEZ_ZELLEN", function (Z) {
    if (!Z) return;
    ZK = {}; T.THEMEN.slice(1).forEach(function (th) { ZK[th.id] = T.klassen(th, Z.features); });
    KF.zellenSetzen(map); fertig();
  });
}
// Fußweg zur Haltestelle: Werte in Zellreihenfolge, nur wenn Anzahl, erste und letzte Zelle zu zellen_odbl.js passen
function fusswerte(art, fertig) {
  gitter(function () {
    KF.laden("daten/erreichbar_fuss_odbl.js", "KIEZ_ERREICHBAR_FUSS", function (d) {
      var Z = window.KIEZ_ZELLEN, f = Z.features;
      var ok = d && d.anzahl === f.length && d.erste_id === f[0].properties.id && d.letzte_id === f[f.length - 1].properties.id && d.werte[art] && d.werte[art].length === f.length;
      fertig(ok ? d.werte[art] : null);
    });
  });
}
function taktAntwort() {
  fusswerte("haltestelle_takt", function (w) {
    if (!w) return;
    var f = window.KIEZ_ZELLEN.features, nah = 0, alle = 0, ohne = 0, ohneEw = 0;
    f.forEach(function (z, i) { if (w[i] == null) { ohne++; ohneEw += z.properties.ew; return; } alle += z.properties.ew; if (w[i] <= FUSS_SCHWELLE) nah += z.properties.ew; });
    satz("ka-a-takt", "erzaehlung.a_takt", { m: fmt.format(FUSS_SCHWELLE) + NB + "m", anteil: alle ? fmt1.format(100 * nah / alle) + PZ : null, nah: fmt.format(nah), alle: fmt.format(alle) });
    // Nenner offenlegen: Zellen ohne Fußwegwert fehlen in „alle“, darum weicht die Summe von der Einwohnerzahl des Gitters ab
    var a = document.getElementById("ka-a-takt");
    if (a && ohne) a.appendChild(document.createTextNode(" " + tt("erzaehlung.a_takt_ohne", { n: ohne, ew: fmt.format(ohneEw) })));
  });
}
var aktiv = null;
function ansicht(name) {
  var a = Q[name]; if (!a || !map.loaded()) return;
  aktiv = name;
  var art = a.ansicht.split(":")[0], id = a.ansicht.split(":")[1];
  KF.auswahl(map, a.ziel || "");
  KF.zeige(map, a.ziel ? KF.teilRahmen(a.ziel) : T.GANZ, 28);
  if (art === "gruppen") { KF.zellThema(map, null); KF.teilWerte(map, null); KF.legendeGruppen(leg); return; }
  if (art === "gitter") {
    gitter(function () {
      if (aktiv !== name) return;
      var th = T.THEMA[T.HASH[id] || id];
      KF.teilWerte(map, null); map.setPaintProperty("teile-flaeche", "fill-opacity", 0.06);
      map.setPaintProperty("zellen-flaeche", "fill-color", T.farbe(th, ZK[th.id])); map.setLayoutProperty("zellen-flaeche", "visibility", "visible");
      KF.legende(leg, th.name, ZK[th.id].grenzen, { einheit: th.einheit === "%" ? PZ : "", grau: th.nenner ? tt("erzaehlung.leg_grau_gitter", { n: fmt.format(th.mindest || 10) }) : null });
    });
    return;
  }
  if (art === "fuss") {
    fusswerte(id, function (w) {
      if (aktiv !== name || !w) return;
      var g = [FUSS_SCHWELLE, 1000, 1500, 2500];
      KF.teilWerte(map, null); map.setPaintProperty("teile-flaeche", "fill-opacity", 0.06);
      KF.zellWerte(map, w, g);
      KF.legende(leg, tt("erzaehlung.leg_fuss", { ziel: tt("erzaehlung.ziel_haltestelle_takt") }), g, { einheit: NB + "m", grau: tt("erzaehlung.leg_grau_fuss") });
    });
    return;
  }
  if (art === "teile") {
    KF.zellThema(map, null);
    var w = {}, einheit = "", titel = "", f1 = function (x) { return fmt.format(x); };
    if (id === "bebauung") { NRS.forEach(function (nr) { var g = GD.stadtteile[nr]; w[nr] = g && g.bebauungsdichte ? g.bebauungsdichte.wert : null; }); einheit = PZ; titel = tt("erzaehlung.dz_bebauung"); f1 = function (x) { return fmt1.format(x); }; }
    if (id === "zbk") { NRS.forEach(function (nr) { var e = SA.liste.je_dzielnica[nr]; w[nr] = e ? e.n : null; }); titel = tt("erzaehlung.dz_zbk"); }
    var g2 = KF.quintile(NRS.map(function (nr) { return w[nr]; }));
    KF.teilWerte(map, w, g2);
    KF.legende(leg, titel, g2, { einheit: einheit, format: f1 });
  }
}
// Frage in der Fenstermitte stellt die Karte ein
var fragen = [].slice.call(document.querySelectorAll(".ka-frage[data-ansicht]"));
function start() {
  ansicht("teile");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        fragen.forEach(function (f) { f.classList.toggle("ist-aktiv", f === e.target); });
        ansicht(e.target.getAttribute("data-ansicht"));
      });
    }, { rootMargin: "-45% 0px -45% 0px" });
    fragen.forEach(function (f) { io.observe(f); });
  }
}
if (map.loaded()) start(); else map.once("load", start);
// Die Antwort zur Erreichbarkeit braucht die Fußwege: erst laden, wenn die Frage näher kommt (oder sofort ohne Beobachter)
(function () {
  var f = document.getElementById("ka-f-takt"); if (!f) return;
  if (!("IntersectionObserver" in window)) { taktAntwort(); return; }
  var io = new IntersectionObserver(function (es) { if (es.some(function (e) { return e.isIntersecting; })) { io.disconnect(); taktAntwort(); } }, { rootMargin: "100% 0px 100% 0px" });
  io.observe(f);
})();
// Knöpfe „auf der Karte zeigen“ (Tastatur, ohne Scrollen)
document.querySelectorAll("[data-zeige]").forEach(function (b) { b.addEventListener("click", function () { ansicht(b.getAttribute("data-zeige")); }); });

// ---------- Register der Stadtteile: sortierbare Tabelle
(function () {
  var tab = document.getElementById("ka-register"); if (!tab || !SD) return;
  var SPALTEN = [
    { id: "ew", w: function (nr) { var s = sd(nr); return s ? s.gitter.einwohner : null; }, z: function (v) { return T.rundEw(v); }, stadt: function () { return T.rundEw(SB.stadt.gitter.einwohner); } },
    { id: "dichte", w: function (nr) { var s = sd(nr); return s ? s.dichte_gitter : null; }, z: function (v) { return fmt.format(v); }, stadt: function () { return fmt.format(SB.stadt.dichte_gitter); } },
    { id: "65p", w: function (nr) { var s = sd(nr); return s ? s.gitter.q_65p : null; }, z: function (v) { return fmt1.format(v); }, stadt: function () { return fmt1.format(SB.stadt.gitter.q_65p); } },
    { id: "geb", w: function (nr) { var g = GD && GD.stadtteile[nr]; return g ? g.anzahl : null; }, z: function (v) { return fmt.format(v); }, stadt: function () { return fmt.format(GK.stadt.anzahl); } },
    { id: "bebauung", w: function (nr) { var g = GD && GD.stadtteile[nr]; return g && g.bebauungsdichte ? g.bebauungsdichte.wert : null; }, z: function (v) { return fmt1.format(v); }, stadt: function () { return fmt1.format(GK.stadt.bebauungsdichte.wert); } },
    { id: "zbk", w: function (nr) { var e = SA && SA.liste.je_dzielnica[nr]; return e ? e.n : null; }, z: function (v) { return fmt.format(v); }, stadt: function () { return fmt.format(SA.liste.miejscowosc.krakow); } }
  ];
  var sortierung = { id: "nr", ab: false };
  var tbody = tab.querySelector("tbody"), tfoot = tab.querySelector("tfoot");
  function zeichnen() {
    var nrs = NRS.slice();
    if (sortierung.id !== "nr") {
      var s = SPALTEN.filter(function (x) { return x.id === sortierung.id; })[0];
      nrs.sort(function (a, b) { var x = s.w(a), y = s.w(b); if (x == null) return 1; if (y == null) return -1; return sortierung.ab ? y - x : x - y; });
    }
    tbody.textContent = "";
    var maxe = {}; SPALTEN.forEach(function (s) { maxe[s.id] = Math.max.apply(null, NRS.map(function (nr) { return s.w(nr) || 0; })); });
    nrs.forEach(function (nr) {
      var tr = el("tr"), th = el("th"); th.setAttribute("scope", "row");
      var a = el("a", "link", anzeige(nr)); a.href = "dzielnica.html#st=" + nr; th.appendChild(a); tr.appendChild(th);
      SPALTEN.forEach(function (s) {
        var v = s.w(nr), td = el("td", null, v == null ? tt("kern.k_a") : s.z(v));
        if (v != null && maxe[s.id] > 0) { var b = el("span", "ka-balken"); b.style.width = (100 * v / maxe[s.id]).toFixed(1) + "%"; td.appendChild(b); }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    tab.querySelectorAll("thead button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-sort") === sortierung.id)); });
  }
  var st = el("tr", "ka-stadt"), sth = el("th", null, I18N.ort("stadt")); sth.setAttribute("scope", "row"); st.appendChild(sth);
  SPALTEN.forEach(function (s) { st.appendChild(el("td", null, s.stadt())); });
  tfoot.appendChild(st);
  tab.querySelectorAll("thead button").forEach(function (b) {
    b.addEventListener("click", function () {
      var id = b.getAttribute("data-sort");
      sortierung = { id: id, ab: id === sortierung.id ? !sortierung.ab : id !== "nr" };
      zeichnen();
    });
  });
  zeichnen();
})();
})();
