/* Kiezatlas: Seite Klima (Bebauung und Grün). Daten: daten/klimat.js (Stadt, delegatury), daten/klimat_zellen.js
   (1-km-Zellen), daten/klimat_stadtteile_odbl.js (dzielnice; Grenzen aus OpenStreetMap, ODbL). Karte über
   kartenfeld.js (window.KIEZ_KARTE): die Zellen kommen als eigene Ebene unter die Stadtteilgrenzen. Abzeichen
   „orientacyjnie“: Bebauung und Verkehr sind eine Näherung für Versiegelung, keine Messung. */
(function () {
"use strict";
var I18N = window.KIEZ_I18N, TS = window.KIEZ_TS, el = TS.el;
var K = window.KIEZ_KLIMAT, Z = window.KIEZ_KLIMAT_ZELLEN, S = window.KIEZ_KLIMAT_STADTTEILE;
if (!I18N || !TS || !K) return;
function $(id) { return document.getElementById(id); }

// Begriffe der Klassen und Gründe: feste Tabellen, damit jeder Schlüssel wörtlich im Code steht
var KLASSE = {
  bebauung: I18N.t("klimat.klasse.bebauung"), verkehr: I18N.t("klimat.klasse.verkehr"), gruen: I18N.t("klimat.klasse.gruen"),
  wald: I18N.t("klimat.klasse.wald"), wasser: I18N.t("klimat.klasse.wasser"), acker: I18N.t("klimat.klasse.acker"),
  sonstige: I18N.t("klimat.klasse.sonstige")
};
var ABGELEITET = { bebauung_verkehr: I18N.t("klimat.abgeleitet.bebauung_verkehr"), gruen_wald: I18N.t("klimat.abgeleitet.gruen_wald") };
var GRUND = {
  einwohner_beispieldaten: function () { return I18N.t("klimat.grund.einwohner_beispieldaten"); },
  unter_mindestzahl: function (d) { return I18N.t("klimat.grund.unter_mindestzahl", { zahl: TS.zahl(d.mindest_einwohner) }); },
  bezugsflaeche_zu_klein: function (d) { return I18N.t("klimat.grund.bezugsflaeche_zu_klein", { ha: TS.zahl(d.mindestflaeche_ha) }); }
};
function grund(code, d) { return GRUND[code] ? GRUND[code](d) : I18N.t("kern.k_a"); }
function leer(text) { return el("span", { class: "ts-leer", text: text }); }

// Weite der Gitterzellen aus der Zellkennung (INSPIRE: …RES1000m…), nicht von Hand
var KM = (function () {
  var f = Z && Z.features && Z.features[0], m = f && /RES(\d+)m/.exec(f.properties.id);
  return m ? Number(m[1]) / 1000 : null;
})();
var KM_TEXT = KM == null ? I18N.t("kern.k_a") : TS.zahl(KM);

// ---------- Stadt: Kennzahlen und Klassen
(function () {
  var s = K.stadt, a = s.anteil;
  var zahlen = [
    [TS.proz(a.bebauung_verkehr), ABGELEITET.bebauung_verkehr],
    [TS.proz(a.gruen_wald), ABGELEITET.gruen_wald],
    [TS.proz(a.acker), KLASSE.acker],
    [s.gruen_je_ew == null ? I18N.t("kern.k_a") : TS.zahl(s.gruen_je_ew) + " m²", I18N.t("klimat.tab.zielen_ew")]
  ];
  var ul = $("k-zahlen");
  zahlen.forEach(function (z) { ul.appendChild(el("li", {}, [el("b", { text: z[0] }), el("span", { text: z[1] })])); });
  $("k-klassen").appendChild(TS.tabelle({
    titel: I18N.t("klimat.h.klasy"),
    spalten: [{ text: I18N.t("klimat.tab.klasa") }, { text: I18N.t("klimat.tab.ha"), zahl: true }, { text: I18N.t("klimat.tab.udzial"), zahl: true }],
    zeilen: K.klassen.map(function (k) {
      return { zellen: [KLASSE[k] || k, TS.zahl(s.ha[k], 1), TS.balken(TS.proz(a[k]), a[k] / 100)] };
    })
  }));
})();

// ---------- dzielnice und delegatury
var SORT = "nr";
function zeileTeil(nr, d) {
  var a = d.anteil, ew = d.einwohner;
  return { klasse: null, zellen: [
    TS.teilName(nr),
    TS.zahl(d.flaeche_ha, 1),
    a ? TS.balken(TS.proz(a.bebauung_verkehr), a.bebauung_verkehr / 100) : leer(grund(d.anteil_grund, S)),
    a ? TS.balken(TS.proz(a.gruen_wald), a.gruen_wald / 100) : leer(grund(d.anteil_grund, S)),
    a ? TS.proz(a.acker) : I18N.t("kern.k_a"),
    ew == null ? I18N.t("kern.k_a") : I18N.t("kern.rund", { zahl: TS.zahl(ew >= 1000 ? Math.round(ew / 100) * 100 : Math.round(ew / 10) * 10) }),
    d.gruen_je_ew == null ? leer(grund(d.gruen_je_ew_grund, S)) : TS.zahl(d.gruen_je_ew)
  ] };
}
function wert(d, sort) {
  if (sort === "bv") return d.anteil ? d.anteil.bebauung_verkehr : -1;
  if (sort === "gw") return d.anteil ? d.anteil.gruen_wald : -1;
  if (sort === "ew") return d.gruen_je_ew == null ? -1 : d.gruen_je_ew;
  return 0;
}
function teileZeichnen() {
  var box = TS.leeren($("k-dzielnice"));
  if (!S) { box.appendChild(el("p", { text: I18N.t("kern.laden_fehler", { datei: "daten/klimat_stadtteile_odbl.js" }) })); return; }
  var nrs = Object.keys(S.stadtteile).sort();
  if (SORT !== "nr") nrs.sort(function (x, y) { return wert(S.stadtteile[y], SORT) - wert(S.stadtteile[x], SORT); });
  var s = K.stadt;
  var zeilen = nrs.map(function (nr) { return zeileTeil(nr, S.stadtteile[nr]); });
  zeilen.push({ klasse: "ts-summe", zellen: [I18N.ort("ganze_stadt") || I18N.t("klimat.ebene.stadt"), TS.zahl(s.flaeche_ha, 1),
    TS.proz(s.anteil.bebauung_verkehr), TS.proz(s.anteil.gruen_wald), TS.proz(s.anteil.acker), "",
    s.gruen_je_ew == null ? I18N.t("kern.k_a") : TS.zahl(s.gruen_je_ew)] });
  box.appendChild(TS.tabelle({
    titel: I18N.t("klimat.h.dzielnice"),
    spalten: [{ text: I18N.t("klimat.ebene.dzielnica") }, { text: I18N.t("klimat.tab.powierzchnia"), zahl: true },
      { text: I18N.t("klimat.tab.uszczelnienie"), zahl: true }, { text: I18N.t("klimat.tab.zielen"), zahl: true },
      { text: KLASSE.acker, zahl: true }, { text: I18N.t("klimat.tab.mieszkancy"), zahl: true },
      { text: I18N.t("klimat.tab.zielen_ew"), zahl: true }],
    zeilen: zeilen
  }));
}
TS.knoepfe($("k-sort"), I18N.t("klimat.sortuj"), [
  { wert: "nr", text: I18N.t("klimat.sort.nr") }, { wert: "bv", text: I18N.t("klimat.tab.uszczelnienie") },
  { wert: "gw", text: I18N.t("klimat.tab.zielen") }, { wert: "ew", text: I18N.t("klimat.tab.zielen_ew") }
], SORT, function (w) { SORT = w; teileZeichnen(); });
teileZeichnen();

$("k-delegatury").appendChild(TS.tabelle({
  titel: I18N.t("klimat.h.delegatury"),
  spalten: [{ text: I18N.t("klimat.ebene.delegatura") }, { text: I18N.t("klimat.tab.powierzchnia"), zahl: true },
    { text: I18N.t("klimat.tab.uszczelnienie"), zahl: true }, { text: I18N.t("klimat.tab.zielen"), zahl: true }, { text: KLASSE.acker, zahl: true }],
  zeilen: Object.keys(K.delegaturen).sort().map(function (id) {
    var d = K.delegaturen[id], a = d.anteil;
    return { zellen: [d.name, TS.zahl(d.flaeche_ha, 1), TS.balken(TS.proz(a.bebauung_verkehr), a.bebauung_verkehr / 100),
      TS.balken(TS.proz(a.gruen_wald), a.gruen_wald / 100), TS.proz(a.acker)] };
  })
}));

// ---------- Karte der Zellen
var STUFEN = ["--k1", "--k2", "--k3", "--k4", "--k5"].map(function (v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); });
var GRAU = "#cdc8be", GRENZEN = [20, 40, 60, 80], WAHL = "bebauung_verkehr";
var zellen = Z ? { type: "FeatureCollection", features: Z.features.map(function (f) {
  var p = f.properties, a = p.anteil;
  return { type: "Feature", geometry: f.geometry, properties: { id: p.id, bebauung_verkehr: a ? a.bebauung_verkehr : null,
    gruen_wald: a ? a.gruen_wald : null, anteil_stadt: p.anteil_stadt, grund: p.anteil_grund || null } };
}) } : null;
function farbe(k) {
  var e = ["step", ["get", k], STUFEN[0]];
  GRENZEN.forEach(function (g, i) { e.push(g, STUFEN[i + 1]); });
  return ["case", ["==", ["typeof", ["get", k]], "number"], e, GRAU];
}
function legendeZeichnen() {
  var ul = TS.leeren($("k-legende")), b = [0].concat(GRENZEN, [100]);
  ul.appendChild(el("li", { class: "ts-legende-titel" }, [el("b", { text: ABGELEITET[WAHL] })]));
  STUFEN.forEach(function (c, i) {
    var m = el("span", { class: "ts-muster ts-flaeche", "aria-hidden": "true" }); m.style.background = c;
    ul.appendChild(el("li", {}, [m, TS.proz(b[i], 0) + "–" + TS.proz(b[i + 1], 0)]));
  });
  ul.appendChild(el("li", {}, [el("span", { class: "ts-muster ts-grau", "aria-hidden": "true" }), grund("bezugsflaeche_zu_klein", Z)]));
}
TS.knoepfe($("k-wahl"), I18N.t("klimat.wybor.wskaznik"), [
  { wert: "bebauung_verkehr", text: ABGELEITET.bebauung_verkehr }, { wert: "gruen_wald", text: ABGELEITET.gruen_wald }
], WAHL, function (w) {
  WAHL = w; legendeZeichnen();
  var m = window.KIEZ_KARTE;
  if (m && m.getLayer("klimat-zellen")) m.setPaintProperty("klimat-zellen", "fill-color", farbe(WAHL));
});
legendeZeichnen();
$("k-mapa-opis").textContent = I18N.t("klimat.mapa.opis", { km: KM_TEXT });

// kartenfeld.js baut die Karte nicht mehr selbst, sondern ist eine Bibliothek (window.KIEZ_KARTENFELD)
var map = window.KIEZ_KARTE;
if (!map && window.KIEZ_KARTENFELD && $("karte") && window.maplibregl) map = window.KIEZ_KARTENFELD.bauen($("karte"));
if (map && zellen) {
  var einbauen = function () {
    if (map.getLayer("klimat-zellen")) return;
    // Rahmengröße erst nach den Stylesheets der Seite endgültig: neu messen und die ganze Stadt zeigen
    map.resize();
    if (window.KIEZ_THEMEN.GANZ) map.fitBounds(window.KIEZ_THEMEN.GANZ, { padding: 16, animate: false });
    map.addSource("klimat-zellen", { type: "geojson", data: zellen, attribution: K.quelle.vermerk });
    var vor = map.getLayer("teile-linie") ? "teile-linie" : undefined;
    map.addLayer({ id: "klimat-zellen", type: "fill", source: "klimat-zellen", paint: { "fill-color": farbe(WAHL), "fill-opacity": 0.78 } }, vor);
    map.addLayer({ id: "klimat-zellen-linie", type: "line", source: "klimat-zellen", paint: { "line-color": "#ffffff", "line-width": 0.5, "line-opacity": 0.6 } }, vor);
    if (map.getLayer("teile-flaeche")) map.setPaintProperty("teile-flaeche", "fill-opacity", 0);
    map.on("click", "klimat-zellen", function (e) {
      var p = e.features && e.features[0] && e.features[0].properties;
      if (!p) return;
      var txt = typeof p.bebauung_verkehr === "number"
        ? I18N.t("klimat.mapa.kwadrat", { bv: TS.proz(p.bebauung_verkehr), gw: TS.proz(p.gruen_wald), stadt: TS.proz(p.anteil_stadt) })
        : grund(p.grund, Z);
      $("k-zelle").textContent = txt;
    });
    map.on("mouseenter", "klimat-zellen", function () { map.getCanvas().style.cursor = "pointer"; });
    map.on("mouseleave", "klimat-zellen", function () { map.getCanvas().style.cursor = ""; });
  };
  if (map.isStyleLoaded()) einbauen(); else map.on("load", einbauen);
}
$("k-zelle").textContent = I18N.t("klimat.mapa.klik");

// ---------- Grenzen mit Werten aus den Daten
var gr = $("k-grenzen");
[
  I18N.t("klimat.g.daty", { data: TS.datum(K.stand_daten) }),
  I18N.t("klimat.g.ludnosc", { km: KM_TEXT }),
  I18N.t("klimat.g.min", { zahl: TS.zahl(K.mindest_einwohner) }),
  Z ? I18N.t("klimat.g.kwadraty", { ha: TS.zahl(Z.mindestflaeche_ha) }) : null
].forEach(function (s) { if (s) gr.appendChild(el("li", { text: s })); });

// ---------- Quellen (Vermerke wörtlich, Polnisch)
TS.quellen($("k-quellen"), [
  { titel: I18N.t("klimat.zrodlo.bdot"), zeilen: [
    { text: K.quelle.quelle, lang: "pl" },
    { vor: I18N.t("klimat.zrodlo.vermerk"), text: K.quelle.vermerk, lang: "pl" },
    I18N.t("klimat.zrodlo.stan", { data: TS.datum(K.stand_daten) }),
    { link: K.quelle.url, text: I18N.t("klimat.zrodlo.plik") }
  ] },
  S && S.quelle_grenzen ? { titel: I18N.t("klimat.zrodlo.granice"), zeilen: [
    { vor: I18N.t("klimat.zrodlo.vermerk"), text: S.quelle_grenzen.vermerk, lang: "pl" }
  ] } : null,
  { titel: I18N.t("klimat.zrodlo.ludnosc"), zeilen: [I18N.t("klimat.zrodlo.ludnosc_tekst", { km: KM_TEXT })] }
].filter(Boolean));
if (window.KIEZ_BEISPIEL_PRUEFEN) window.KIEZ_BEISPIEL_PRUEFEN();
})();
