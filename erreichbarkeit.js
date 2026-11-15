/* Kiezatlas: Erreichbarkeit und Takt auf einer Kartenseite (planer.html in jeder Sprache).
   Entfernung zu Fuß (Standard) oder in Luftlinie vom Mittelpunkt jeder 1-km-Zelle zur nächsten Einrichtung,
   Haltestellen nach Taktklasse, Kennzahlen je Stadtteil und Vergleich aller Stadtteile. Fragen setzen die Ansicht.
   Sätze kommen aus den Texten (Namensraum planer.e.*), Zahlen, Radien (radius_m) und Quellenvermerke aus den
   Datendateien; die Datendateien tragen keine Sätze.
   Zustand im Hash: zu (Ziel), weg (fuss|luft), st (Stadtteil), halt (Haltestellen), 3d, k (Kamera).
   Braucht vorher kartenseite.js (window.KIEZ_KS). Lädt nach: zellen_odbl.js, erreichbar*.js, einrichtungen*.js,
   haltestellen.js, planer*_odbl.js. */
(function () {
"use strict";
var KS = window.KIEZ_KS, T = window.KIEZ_THEMEN, I18N = window.KIEZ_I18N;
if (!KS || !document.getElementById("karte")) return;
var t = I18N.t, el = KS.el, $ = KS.$, esc = KS.esc, NB = " ";
// Prozentzeichen nach Landesbrauch wie fmt.anteil (pl, en ohne Leerzeichen, de mit geschütztem)
var PZ = I18N.fmt.anteil(1, 0).replace(/^[0-9]+/, "");
var D = KS.WURZEL + "daten/";
var DATEI = {
  zellen: ["zellen_odbl.js", "KIEZ_ZELLEN"], luft: ["erreichbar.js", "KIEZ_ERREICHBAR"], fuss: ["erreichbar_fuss_odbl.js", "KIEZ_ERREICHBAR_FUSS"],
  ein: ["einrichtungen.js", "KIEZ_EINRICHTUNGEN"], ein_odbl: ["einrichtungen_odbl.js", "KIEZ_EINRICHTUNGEN_ODBL"],
  halt: ["haltestellen.js", "KIEZ_HALTESTELLEN"], p_luft: ["planer_odbl.js", "KIEZ_PLANER"], p_fuss: ["planer_fuss_odbl.js", "KIEZ_PLANER_FUSS"]
};
var offen = 0;
function holen(n, fertig) { offen++; T.laden(D + DATEI[n][0], DATEI[n][1], function (d) { offen--; fertig(d); }); }

// Ziele in der Reihenfolge der Chips; punkte: Datei mit den Lagen (OSM-Arten ohne Lage: nur Entfernung)
var ZIELE = ["haltestelle_takt", "park", "szkola", "przedszkole", "zlobek", "szpital", "apotheke", "arzt", "supermarkt", "spielplatz", "pflege"];
var PUNKTE = { szkola: "ein", przedszkole: "ein", zlobek: "ein", szpital: "ein", park: "ein", apotheke: "ein_odbl", arzt: "ein_odbl", haltestelle_takt: "halt" };
var ZIEL_TEXT = { haltestelle_takt: "planer.e.ziel.haltestelle_takt", park: "planer.e.ziel.park", szkola: "planer.e.ziel.szkola",
  przedszkole: "planer.e.ziel.przedszkole", zlobek: "planer.e.ziel.zlobek", szpital: "planer.e.ziel.szpital", apotheke: "planer.e.ziel.apotheke",
  arzt: "planer.e.ziel.arzt", supermarkt: "planer.e.ziel.supermarkt", spielplatz: "planer.e.ziel.spielplatz", pflege: "planer.e.ziel.pflege" };
function zielName(a) { return ZIEL_TEXT[a] ? t(ZIEL_TEXT[a]) : String(a).replace(/_/g, " "); }
var KL = [300, 500, 1000, 2000];
var TAKT = ["I", "II", "III", "unter III"], TAKT_FARBE = { "I": "#13212a", "II": "#4f6b78", "III": "#a8b8be", "unter III": "#ffffff" };
var TAKT_LEG = { "I": "planer.e.takt.i", "II": "planer.e.takt.ii", "III": "planer.e.takt.iii", "unter III": "planer.e.takt.unter_iii" };
var TAKT_KURZ = { "I": "planer.e.takt_kurz.i", "II": "planer.e.takt_kurz.ii", "III": "planer.e.takt_kurz.iii", "unter III": "planer.e.takt_kurz.unter_iii" };
var MITTEL = { bus: "planer.e.mittel.bus", tram: "planer.e.mittel.tram", "bus+tram": "planer.e.mittel.bus_tram" };

// ---------- Zustand
var H = KS.hashLesen();
var S = { zu: ZIELE.indexOf(H.zu) > -1 ? H.zu : "", weg: H.weg === "luft" ? "luft" : "fuss", st: T.TEIL[H.st] ? H.st : "", halt: H.halt === "1", d3: H["3d"] === "1" };
function hash() { KS.hashSchreiben(bereit ? map : null, { zu: S.zu, weg: S.weg, st: S.st, halt: S.halt, "3d": drei && drei.an() }); }

// ---------- Karte
var LEER = { type: "FeatureCollection", features: [] };
var map = KS.karte({
  kamera: KS.kameraAusHash(H.k),
  quellen: { zellen: { type: "geojson", data: LEER }, punkte: { type: "geojson", data: LEER }, halt: { type: "geojson", data: LEER } },
  ebenen: [{ id: "zellen", type: "fill", source: "zellen", layout: { visibility: "none" }, paint: { "fill-color": T.STUFEN[2], "fill-opacity": 0.72, "fill-outline-color": "rgba(255,255,255,0.5)" } }],
  oben: [
    { id: "halt", type: "circle", source: "halt", layout: { visibility: "none" }, paint: {
      "circle-color": ["match", ["get", "taktklasse"], "I", TAKT_FARBE.I, "II", TAKT_FARBE.II, "III", TAKT_FARBE.III, TAKT_FARBE["unter III"]],
      "circle-stroke-color": "#13212a", "circle-stroke-width": 1,
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, ["match", ["get", "taktklasse"], "I", 3.2, "II", 2.8, 2.2], 15, ["match", ["get", "taktklasse"], "I", 7, "II", 6, 5]],
      "circle-opacity": ["case", ["==", ["get", "in_stadt"], false], 0.5, 1] } },
    { id: "punkte", type: "circle", source: "punkte", paint: { "circle-color": "#ffffff", "circle-stroke-color": "#6a2c82", "circle-stroke-width": 2,
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 3, 15, 6.5], "circle-opacity": ["case", ["==", ["get", "in_stadt"], false], 0.5, 1] } }
  ]
});
var wahl = KS.stadtteilWahl(map);
var drei = null, bereit = false;

// ---------- Werkzeugleiste auf der Karte: Messart und 3D
var wz = $("werkzeug");
var weg = el("fieldset", "themen"); weg.appendChild(el("legend", "nur-sr", t("planer.e.messart")));
[["fuss", t("planer.e.fussweg")], ["luft", t("planer.e.luftlinie")]].forEach(function (w) {
  var l = el("label", "chip chip--schalter"), r = document.createElement("input"); r.type = "radio"; r.name = "weg"; r.value = w[0];
  l.appendChild(r); l.appendChild(el("span", null, w[1])); weg.appendChild(l);
});
weg.addEventListener("change", function (e) { if (e.target.name === "weg") { S.weg = e.target.value; frageAus(); anwenden(); } });
wz.appendChild(weg);
var k3 = el("button", "chip chip--knopf"); k3.type = "button"; k3.appendChild(el("span", null, t("planer.ks_3d"))); k3.setAttribute("aria-pressed", "false");
wz.appendChild(k3);

// ---------- Ziel-Chips und Haltestellen-Schalter im Blatt
var zuBox = $("zu"), haltKnopf = $("halt-knopf");
function zuBauen() {
  zuBox.innerHTML = ""; zuBox.appendChild(el("legend", null, t("planer.e.ziel_titel")));
  var E = window[DATEI[S.weg][1]];
  [""].concat(ZIELE).forEach(function (a) {
    var l = el("label", "chip"), r = document.createElement("input"); r.type = "radio"; r.name = "zu"; r.value = a;
    var aus = !!(a && E && E.arten.indexOf(a) < 0);
    r.checked = S.zu === a; r.disabled = aus; if (aus) { l.classList.add("chip--aus"); l.title = t("planer.e.nur_fuss"); }
    l.appendChild(r); l.appendChild(el("span", null, a ? zielName(a) : t("planer.e.kein_ziel"))); zuBox.appendChild(l);
  });
}
zuBox.addEventListener("change", function (e) { if (e.target.name === "zu") { S.zu = e.target.value; frageAus(); anwenden(); } });
haltKnopf.addEventListener("click", function () { S.halt = !S.halt; frageAus(); haltAnwenden(); hash(); });

// ---------- Zellen und Punkte
var ZELLEN = null;
function zellwerte(d, z, a) {
  var f = z.features, l = d.werte && d.werte[a];
  return Array.isArray(l) && d.anzahl === f.length && l.length === f.length && f.length &&
    d.erste_id === f[0].properties.id && d.letzte_id === f[f.length - 1].properties.id ? l : null;
}
function farbe() {
  var e = ["step", ["get", "wert"], T.STUFEN[0]];
  KL.forEach(function (g, i) { e.push(g, T.STUFEN[i + 1]); });
  return ["case", ["==", ["typeof", ["get", "wert"]], "number"], e, T.GRAU];
}
var status = "";
// Sprunglink zu den Fragen ohne Hash-Änderung (der Hash trägt den Zustand der Seite)
(function () {
  var a = document.querySelector("#wahl-hinweis a"); if (!a) return;
  a.addEventListener("click", function (e) {
    var z = document.getElementById("fragen"); if (!z) return;
    e.preventDefault(); z.scrollIntoView({ block: "start" });
    var b = z.querySelector("button, a, input"); if (b) b.focus({ preventScroll: true });
  });
})();
function anwenden() {
  // Hinweis über der Karte, solange kein Ziel gewählt ist (Startzustand: nur Stadtteilgrenzen)
  var hw = document.getElementById("wahl-hinweis");
  if (hw) { hw.hidden = !!S.zu && !startFrage; if (hw.firstChild && hw.firstChild.nodeType === 3) hw.firstChild.nodeValue = (startFrage ? t("planer.e.start_hinweis") : t("planer.e.wahl_hinweis")) + " "; }
  if (!bereit) return;
  zuBauen(); wegSetzen();
  var a = S.zu, w = S.weg;
  if (!a) { map.setLayoutProperty("zellen", "visibility", "none"); map.getSource("punkte").setData(LEER); fertig(); return; }
  holen("zellen", function (z) {
    holen(w, function (d) {
      if (a !== S.zu || w !== S.weg) return;
      if (!z || !d) { status = t("planer.e.fehler_datei"); S.zu = ""; anwenden(); return; }
      if (d.arten.indexOf(a) < 0) { status = t("planer.e.nur_fuss"); S.zu = ""; anwenden(); return; }
      var l = zellwerte(d, z, a);
      if (!l) { status = t("planer.e.fehler_passt"); S.zu = ""; anwenden(); return; }
      ZELLEN = { type: "FeatureCollection", features: z.features.map(function (f, i) { return { type: "Feature", geometry: f.geometry, properties: { id: f.properties.id, ew: f.properties.ew, st: f.properties.st, wert: l[i] } }; }) };
      map.getSource("zellen").setData(ZELLEN);
      map.setPaintProperty("zellen", "fill-color", farbe());
      map.setLayoutProperty("zellen", "visibility", "visible");
      punkte(a); fertig();
    });
  });
  fertig();
}
function punkte(a) {
  var q = PUNKTE[a];
  if (!q || q === "halt") { map.getSource("punkte").setData(LEER); if (q === "halt" && !S.halt) { S.halt = true; haltAnwenden(); } legende(); return; }
  holen(q, function (d) {
    if (a !== S.zu) return;
    map.getSource("punkte").setData(d ? { type: "FeatureCollection", features: d.features.filter(function (f) { return f.properties.art === a; }) } : LEER);
    legende(); fertig();
  });
}
function haltAnwenden() {
  haltKnopf.setAttribute("aria-pressed", String(S.halt));
  if (!bereit) return;
  if (!S.halt) { map.setLayoutProperty("halt", "visibility", "none"); legende(); fertig(); return; }
  holen("halt", function (d) {
    if (!d) { status = t("planer.e.fehler_datei"); S.halt = false; haltAnwenden(); return; }
    map.getSource("halt").setData(d);
    map.setLayoutProperty("halt", "visibility", S.halt ? "visible" : "none");
    legende(); fertig();
  });
}
function wegSetzen() { weg.querySelectorAll("input").forEach(function (r) { r.checked = r.value === S.weg; }); }

// ---------- Legende
function anzahl(q, a) { var d = window[DATEI[q][1]]; return d ? d.features.filter(function (f) { return f.properties.art === a; }).length : null; }
function vermerke(d) {
  return Object.keys(d.quellen || {}).map(function (k) { return k === "osm" ? t("planer.e.osm_vermerk") : d.quellen[k].vermerk; });
}
function legende() {
  var L = $("legende"); L.innerHTML = "";
  var d = window[DATEI[S.weg][1]];
  if (S.zu && d && map.getLayoutProperty("zellen", "visibility") === "visible") {
    L.appendChild(el("p", "ks-legende__titel", t("planer.e.leg_titel", { ziel: zielName(S.zu), weg: S.weg === "fuss" ? t("planer.e.fussweg") : t("planer.e.luftlinie") })));
    var st = el("div", "stufen stufen--flach"); st.setAttribute("aria-hidden", "true");
    T.STUFEN.forEach(function (f) { var x = el("span"); x.style.background = f; st.appendChild(x); }); L.appendChild(st);
    var m = el("div", "marken"); m.appendChild(el("span", null, "0"));
    KL.forEach(function (g) { m.appendChild(el("span", null, I18N.fmt.zahl(g))); }); m.appendChild(el("span", null, t("planer.e.leg_mehr"))); L.appendChild(m);
    var g = el("p"); var gz = el("i", "ks-zeichen ks-zeichen--flaeche"); gz.style.background = T.GRAU; gz.setAttribute("aria-hidden", "true"); g.appendChild(gz); g.appendChild(document.createTextNode(" " + t("planer.e.leg_grau"))); L.appendChild(g);
    L.appendChild(el("p", null, t("planer.e.leg_zelle")));
    var q = PUNKTE[S.zu];
    if (q === "ein" || q === "ein_odbl") {
      var n = anzahl(q, S.zu);
      if (n != null) L.appendChild(el("p", null, t(q === "ein" ? "planer.e.leg_punkte_bdot" : "planer.e.leg_punkte_osm", { n: I18N.fmt.zahl(n) })));
    } else if (!q) L.appendChild(el("p", null, t("planer.e.leg_ohne_punkte")));
    if (S.zu === "przedszkole" || S.zu === "zlobek" || S.zu === "szkola") L.appendChild(el("p", null, t("planer.e.leg_unvollstaendig")));
    var v = el("p"); v.appendChild(KS.vermerkKnoten(vermerke(d).join(" "))); L.appendChild(v);
  }
  var h = window.KIEZ_HALTESTELLEN;
  if (S.halt && h) {
    var box = el("div"); box.appendChild(el("p", "ks-legende__titel", t("planer.e.takt_titel")));
    var ul = el("ul");
    TAKT.forEach(function (k) {
      var li = el("li"), z = el("i", "ks-zeichen"); z.style.background = TAKT_FARBE[k]; z.setAttribute("aria-hidden", "true"); li.appendChild(z);
      var gr = h.klassen.grenzen, txt = t(TAKT_LEG[k], { n: k === "unter III" ? gr.III : gr[k] });
      li.appendChild(document.createTextNode(txt)); ul.appendChild(li);
    });
    box.appendChild(ul);
    box.appendChild(el("p", null, t("planer.e.takt_fenster", { von: h.fenster[0], bis: h.fenster[1], tag: KS.datum(h.stichtag) })));
    var v2 = el("p"); v2.appendChild(KS.vermerkKnoten(vermerke(h).join(" "))); box.appendChild(v2);
    L.appendChild(box);
  }
  var d3 = drei && drei.legende(); if (d3) L.appendChild(d3);
  if (!L.children.length) L.appendChild(el("p", null, t("planer.e.leg_leer")));
  KS.legendeZeigen();
}

// ---------- Kennzahlen je Stadtteil und Vergleich (Texte aus Schlüsseln, nicht aus der Datei)
function radiusAus(w) {
  if (w.richtwert) return I18N.fmt.zahl(w.richtwert.wert) + NB + w.richtwert.einheit;
  return w.radius_m != null ? I18N.fmt.zahl(w.radius_m) + NB + "m" : "";   // Feld radius_m der Datei (eigene Festlegung)
}
function kzTitel(w) {
  var r = radiusAus(w), a = zielName(w.art);
  if (w.kennzahl === "anteil_in_radius" || w.kennzahl === "oepnv_takt" || w.kennzahl === "gruen_in_radius")
    return r ? t("planer.e.kz.anteil", { radius: r, ziel: a }) : t("planer.e.kz.anteil_ohne", { ziel: a });
  if (w.kennzahl === "ew_je_einrichtung") return t("planer.e.kz.ew_je", { ziel: a });
  if (w.kennzahl === "gruen_m2_je_ew") return t("planer.e.kz.gruen_m2");
  return w.kennzahl;
}
function einheit(w) { return w.kennzahl === "gruen_m2_je_ew" ? NB + "m²" : w.einheit === "%" ? PZ : ""; }
function wert(w) { return !w || w.wert == null ? t("planer.e.kein_wert") : I18N.fmt.zahl(w.wert) + einheit(w); }
function zn(w, P) {
  if (!w || w.zaehler == null || w.nenner == null) return "";
  var z = I18N.fmt.zahl(w.zaehler), n = I18N.fmt.zahl(w.nenner);
  if (w.kennzahl === "ew_je_einrichtung") return t("planer.e.zn.ew_je", { zaehler: z, nenner: n });
  if (w.kennzahl === "gruen_m2_je_ew") return t("planer.e.zn.gruen_m2", { zaehler: z, nenner: n });
  return t("planer.e.zn.anteil", { zaehler: z, nenner: n, rundung: I18N.fmt.zahl(P.rundung.ew) });
}
function schl(w) { return [w.kennzahl, w.art, w.richtwert ? w.richtwert.wert : "-"].join("|"); }
function P() { return window[DATEI[S.weg === "fuss" ? "p_fuss" : "p_luft"][1]]; }
function planerHolen(fertig) { holen(S.weg === "fuss" ? "p_fuss" : "p_luft", fertig); }
var stSel = $("st-wahl");
KS.stadtteilAuswahl(stSel, t("planer.e.st_keine")); stSel.value = S.st;
stSel.addEventListener("change", function () { stWaehlen(stSel.value, true); });
function stWaehlen(nr, zoom) {
  S.st = T.TEIL[nr] ? nr : ""; stSel.value = S.st; if (bereit) wahl(S.st);
  if (zoom && bereit && S.st) map.fitBounds(T.umriss(T.TEIL[S.st]), { padding: 30, maxZoom: 14, animate: !matchMedia("(prefers-reduced-motion: reduce)").matches });
  tabelle(); hash();
}
function tabelle() {
  var box = $("st-inhalt"); box.innerHTML = "";
  if (!S.st) { box.appendChild(el("p", "ks-fuss", t("planer.e.st_hinweis"))); return; }
  var p = P();
  if (!p) { box.appendChild(el("p", "ks-fuss", t("planer.e.laedt"))); planerHolen(function (d) { if (!d) box.textContent = t("planer.e.fehler_datei"); else tabelle(); vergleich(); fertig(); }); return; }
  var R = p.raeume[S.st]; if (!R) { box.appendChild(el("p", "ks-fuss", t("planer.e.kein_wert"))); return; }
  box.appendChild(el("p", "ks-fuss", t("planer.e.st_kopf", { ew: I18N.fmt.zahl(R.ew), rundung: I18N.fmt.zahl(p.rundung.ew), weg: S.weg === "fuss" ? t("planer.e.fussweg") : t("planer.e.luftlinie") })));
  var ul = el("ul", "ks-zahlen");
  R.werte.forEach(function (w) {
    var li = el("li"); li.appendChild(el("span", null, kzTitel(w))); li.appendChild(el("b", null, wert(w)));
    var G = p.gesamt && p.gesamt.werte.filter(function (g) { return schl(g) === schl(w); })[0];
    var s = el("small");
    var teile = [zn(w, p)];
    if (G) teile.push(t("planer.e.stadt", { stadt: I18N.ort("ganze_stadt"), wert: wert(G) }));
    s.appendChild(document.createTextNode(teile.filter(Boolean).join(". ") + ". "));
    s.appendChild(el("span", "ks-abz", w.status === "orientierung" ? t("planer.e.orientierung") : t("planer.e.amtlich")));
    if (w.vorlaeufig) s.appendChild(el("span", "ks-abz", t("planer.e.vorlaeufig")));
    if (w.richtwert) {
      var Q = p.quellen[w.richtwert.q] || {};
      s.appendChild(document.createTextNode(t("planer.e.richtwert", { wert: I18N.fmt.zahl(w.richtwert.wert) + NB + w.richtwert.einheit, dokument: Q.vermerk || w.richtwert.q, stelle: w.richtwert.seite || "" })));
    }
    li.appendChild(s); ul.appendChild(li);
  });
  box.appendChild(ul);
  box.appendChild(el("p", "ks-fuss", t("planer.e.norm_hinweis")));
}
var vgSel = $("vg-kennzahl"), vgOffen = false;
$("vg-laden").addEventListener("click", function () { vgOffen = true; this.hidden = true; $("vg-auswahl").hidden = false; vergleich(); });
vgSel.addEventListener("change", vergleich);
function vergleich() {
  if (!vgOffen) return;
  var box = $("vg-inhalt"), p = P(); box.innerHTML = "";
  if (!p) { box.appendChild(el("p", "ks-fuss", t("planer.e.laedt"))); planerHolen(function () { tabelle(); vergleich(); fertig(); }); return; }
  var liste = [], ges = {};
  Object.keys(p.raeume).forEach(function (k) { p.raeume[k].werte.forEach(function (w) { if (!ges[schl(w)]) { ges[schl(w)] = 1; liste.push(w); } }); });
  var alt = vgSel.value, kenn = liste.map(schl).join(",");
  if (vgSel.dataset.liste !== kenn) { vgSel.innerHTML = ""; liste.forEach(function (w) { var o = el("option", null, kzTitel(w)); o.value = schl(w); vgSel.appendChild(o); }); vgSel.dataset.liste = kenn; }
  vgSel.value = ges[alt] ? alt : schl(liste[0]);
  var tab = el("table", "tabelle"), cap = el("caption", "nur-sr", t("planer.e.vg_caption", { kennzahl: vgSel.options[vgSel.selectedIndex].text }));
  tab.appendChild(cap);
  var kopfEinheit = I18N.sprachwert(window.KIEZ_ORT.gliederung.einheit) || "";
  var kopf = el("tr"); [kopfEinheit.charAt(0).toLocaleUpperCase(I18N.locale) + kopfEinheit.slice(1), t("planer.e.sp_wert"), t("planer.e.sp_zaehler"), t("planer.e.sp_nenner")].forEach(function (x) { var th = el("th", null, x); th.scope = "col"; kopf.appendChild(th); });
  var th = el("thead"); th.appendChild(kopf); tab.appendChild(th);
  function reihe(teil, name, w) {
    var tr = el("tr"), c = el("th", null, name); c.scope = "row"; tr.appendChild(c);
    tr.appendChild(el("td", null, wert(w))); tr.appendChild(el("td", null, w && w.zaehler != null ? I18N.fmt.zahl(w.zaehler) : ""));
    tr.appendChild(el("td", null, w && w.nenner != null ? I18N.fmt.zahl(w.nenner) : "")); teil.appendChild(tr);
  }
  var tb = el("tbody");
  Object.keys(p.raeume).sort().forEach(function (nr) { reihe(tb, KS.stadtteilName(nr), p.raeume[nr].werte.filter(function (w) { return schl(w) === vgSel.value; })[0]); });
  tab.appendChild(tb);
  if (p.gesamt) { var tf = el("tfoot"); reihe(tf, I18N.ort("ganze_stadt"), p.gesamt.werte.filter(function (w) { return schl(w) === vgSel.value; })[0]); tab.appendChild(tf); }
  var r = el("div", "ks-tabelle"); r.tabIndex = 0; r.setAttribute("role", "region"); r.setAttribute("aria-label", cap.textContent); r.appendChild(tab); box.appendChild(r);
  box.appendChild(el("p", "ks-fuss", t("planer.e.vg_hinweis")));
}

// ---------- Fragen: jede stellt Ziel, Messart, Haltestellen und ggf. den Stadtteil ein
var FRAGEN = [
  { id: "takt", titel: "planer.e.frage.takt", text: "planer.e.frage.takt_text", zu: "haltestelle_takt", weg: "fuss", halt: true },
  { id: "gruen", titel: "planer.e.frage.gruen", text: "planer.e.frage.gruen_text", zu: "park", weg: "fuss", halt: false },
  { id: "schule", titel: "planer.e.frage.schule", text: "planer.e.frage.schule_text", zu: "szkola", weg: "fuss", halt: false },
  { id: "luft", titel: "planer.e.frage.luft", text: "planer.e.frage.luft_text", zu: "haltestelle_takt", weg: "luft", halt: true },
  { id: "st", titel: "planer.e.frage.st", text: "planer.e.frage.st_text", zu: "", weg: "fuss", halt: false, block: "block-st" }
];
var frageAktiv = -1, startFrage = false;
function frageAus() { frageAktiv = -1; startFrage = false; $("fragen").querySelectorAll(".ks-frage").forEach(function (b) { b.setAttribute("aria-pressed", "false"); }); }
function fragenBauen() {
  var ul = $("fragen");
  FRAGEN.forEach(function (F, i) {
    var li = el("li"), b = el("button", "ks-frage"); b.type = "button"; b.dataset.frage = F.id; b.setAttribute("aria-pressed", "false");
    b.appendChild(el("span", "ks-frage__nr", String(i + 1)));
    var x = el("span", "ks-frage__text"); x.appendChild(el("b", null, t(F.titel))); x.appendChild(el("span", null, t(F.text))); b.appendChild(x);
    b.addEventListener("click", function () {
      S.zu = F.zu; S.weg = F.weg; S.halt = F.halt;
      anwenden(); haltAnwenden();
      if (F.block) {
        var nr = S.st || (window.KIEZ_ORT.gliederung.teile[0] || {}).nr;
        stWaehlen(nr, true);
        var blk = $(F.block); blk.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); stSel.focus({ preventScroll: true });
      }
      frageAus(); frageAktiv = i; b.setAttribute("aria-pressed", "true"); hash();
    });
    li.appendChild(b); ul.appendChild(li);
  });
}

// ---------- Klicks: Haltestelle, Einrichtung, Zelle (keine Kamerabewegung)
function zeile(a, b) { return "<tr><td>" + esc(a) + "</td><td>" + esc(b) + "</td></tr>"; }
map.on("click", function (e) {
  var lay = ["halt", "punkte"].filter(function (l) { return map.getLayoutProperty(l, "visibility") !== "none"; });
  var f = lay.length ? map.queryRenderedFeatures([[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]], { layers: lay }) : [];
  var h;
  if (f.length && f[0].layer.id === "halt") {
    var p = f[0].properties, H2 = window.KIEZ_HALTESTELLEN;
    h = "<b>" + esc(p.name) + "</b><table class='pop-tab'>" + zeile(t("planer.e.pop_klasse"), (TAKT_KURZ[p.taktklasse] ? t(TAKT_KURZ[p.taktklasse]) : String(p.taktklasse))) +
      zeile(t("planer.e.pop_fahrten", { von: H2.fenster[0], bis: H2.fenster[1] }), I18N.fmt.zahl(Number(p.fahrten_hvz_je_richtung), 1)) +
      zeile(t("planer.e.pop_mittel"), (MITTEL[p.verkehrsmittel] ? t(MITTEL[p.verkehrsmittel]) : String(p.verkehrsmittel))) + "</table>" +
      (p.in_stadt === false ? "<div class='pop-q'>" + esc(t("planer.e.pop_aussen")) + "</div>" : "") +
      "<div class='pop-q'>" + esc(t("planer.e.pop_takt_hinweis", { tag: KS.datum(H2.stichtag) })) + "</div>";
  } else if (f.length) {
    var q = f[0].properties, osm = q.q === "osm";
    h = "<b>" + esc(!osm && q.name ? q.name : zielName(q.art)) + "</b><div class='pop-q'>" + esc(t(osm ? "planer.e.pop_osm" : "planer.e.pop_bdot")) + "</div>" +
      (q.in_stadt === false ? "<div class='pop-q'>" + esc(t("planer.e.pop_aussen")) + "</div>" : "");
  } else if (drei && drei.an() && map.getLayer("geb3d") && map.queryRenderedFeatures(e.point, { layers: ["geb3d"] }).length) {
    return;   // Gebäude-Popup aus kartenseite.js
  } else if (map.getLayoutProperty("zellen", "visibility") === "visible") {
    var c = map.queryRenderedFeatures(e.point, { layers: ["zellen"] });
    if (c.length) {
      var z = c[0].properties, w = z.wert === undefined || z.wert === null || z.wert === "null" ? null : Number(z.wert);
      h = "<b>" + esc(t("planer.e.pop_zelle")) + "</b><table class='pop-tab'>" +
        zeile(t("planer.e.pop_naechste", { ziel: zielName(S.zu) }), w == null ? t("planer.e.kein_wert") : I18N.fmt.zahl(w) + NB + "m, " + (S.weg === "fuss" ? t("planer.e.fussweg") : t("planer.e.luftlinie"))) +
        zeile(t("planer.e.pop_ew"), I18N.fmt.zahl(Number(z.ew))) + "</table><div class='pop-q'>" + esc(t("planer.e.pop_zelle_q")) + "</div>";
    }
  }
  if (h) { new maplibregl.Popup({ maxWidth: "290px" }).setLngLat(e.lngLat).setHTML(h).addTo(map); return; }
  var r = map.queryRenderedFeatures(e.point, { layers: ["teile-flaeche"] });
  if (r.length) stWaehlen(r[0].properties.nr === S.st ? "" : r[0].properties.nr, false);
});
map.on("moveend", hash);

// ---------- Aufbau
function fertig() {
  legende();
  $("kartenstatus").textContent = (status ? status + " " : "") + (S.zu ? t("planer.e.status", { ziel: zielName(S.zu), weg: S.weg === "fuss" ? t("planer.e.fussweg") : t("planer.e.luftlinie") })
    : t("planer.e.status_kein_ziel", { weg: S.weg === "fuss" ? t("planer.e.fussweg") : t("planer.e.luftlinie") }));
  status = ""; hash();
  if (bereit && offen === 0) KS.bereitNach(map, function () { return offen + (drei ? drei.laufend() : 0); });
}
fragenBauen();
// Ohne Zustand im Link (kein „zu“ im Hash) zeigt die Seite gleich Frage 1 statt einer leeren Karte; der Hinweis über
// der Karte sagt das und führt zu den übrigen Fragen. Wer ein Ziel abwählt („bez odległości“), behält das im Link.
if (!("zu" in H)) {
  S.zu = FRAGEN[0].zu; S.weg = FRAGEN[0].weg; S.halt = FRAGEN[0].halt;
  frageAktiv = 0; startFrage = true;
  $("fragen").querySelector(".ks-frage").setAttribute("aria-pressed", "true");
}
zuBauen(); wegSetzen(); haltKnopf.setAttribute("aria-pressed", String(S.halt)); tabelle();
map.on("load", function () {
  bereit = true;
  drei = KS.drei(map, { klickVorrang: function (e) { var l = ["halt", "punkte"].filter(function (x) { return map.getLayoutProperty(x, "visibility") !== "none"; }); return l.length > 0 && map.queryRenderedFeatures([[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]], { layers: l }).length > 0; }, knopf: k3, legende: legende, geaendert: hash, bereit: fertig, meldung: function (m) { status = m; fertig(); },
    ziel: function () { return S.st ? T.umriss(T.TEIL[S.st]).reduce(function (a, b) { return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]; }) : window.KIEZ_ORT.karte.haus_ziel; } });
  wahl(S.st); anwenden(); haltAnwenden();
  if (S.d3) drei.setzen(true, false);
});
})();
