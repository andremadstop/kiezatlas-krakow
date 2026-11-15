/* Kiezatlas: Kamienice und Denkmale als Teilmenge (kamienice.html in jeder Sprache).
   Zeigt nur, was die Quellen tragen: Objekte mit Denkmalangabe aus OpenStreetMap (Lage ungeprüft), auf Wunsch
   Objekte mit Baudatum in OSM ohne Denkmalangabe (keine Denkmale), Komplexe aus BDOT10k (kein Register), Kamienice
   nach der Festlegung des Atlas (Mehrfamilienhaus laut BDOT10k mit Denkmalangabe) und die Ortsmarke ul. Kościuszki 18.
   Nur Bauzeitklassen, nie Einzeljahre; keine Aussage über die Bauzeit aller Gebäude. Aus dem Register liegt nur
   Wikidata vor (daten/denkmale.js): Zahlen je Delegatura im Blatt; die Punkte zeigt die freie Karte (Ebene rejestr),
   diese Karte bleibt bei der OSM-Kennzeichnung. Das Denkmalregister (NID) und die gminna ewidencja fehlen noch.
   Zustand im Hash: ep (Bauzeitklassen), nur (kamienice), alle (auch Objekte ohne Denkmalangabe), kx (Komplexe),
   3d, k. Braucht vorher kartenseite.js, daten/denkmale_bdot.js, daten/denkmale_odbl.js; daten/denkmale.js wenn da. */
(function () {
"use strict";
var KS = window.KIEZ_KS, T = window.KIEZ_THEMEN, I18N = window.KIEZ_I18N, B = window.KIEZ_DENKMALE_BDOT, O = window.KIEZ_DENKMALE_ODBL;
var R = window.KIEZ_DENKMALE && window.KIEZ_DENKMALE.fixture !== true ? window.KIEZ_DENKMALE : null;   // Register, nie Beispieldaten
if (!KS || !document.getElementById("karte") || !B || !O) return;
var t = I18N.t, el = KS.el, $ = KS.$, esc = KS.esc, zahl = KS.zahl;

var KLASSEN = ["vor_1800", "1800_1866", "1867_1918", "1919_1945", "1946_1989", "ab_1990", "null"];
var KL_TEXT = { vor_1800: "denkmale.klasse.vor_1800", "1800_1866": "denkmale.klasse.1800_1866", "1867_1918": "denkmale.klasse.1867_1918",
  "1919_1945": "denkmale.klasse.1919_1945", "1946_1989": "denkmale.klasse.1946_1989", ab_1990: "denkmale.klasse.ab_1990", "null": "denkmale.klasse.null" };
var KL_FARBE = { vor_1800: "#1c4a5b", "1800_1866": "#3b7684", "1867_1918": "#6a2c82", "1919_1945": "#9a6fae", "1946_1989": "#a8c7c2", ab_1990: "#dce6e2", "null": "#ffffff" };
var KX_TEXT = { zabudowa: "denkmale.komplex.zabudowa", twierdza: "denkmale.komplex.twierdza", muzeum: "denkmale.komplex.muzeum", pamiec: "denkmale.komplex.pamiec" };
var KX_FARBE = { zabudowa: "#6a2c82", twierdza: "#4f5d64", muzeum: "#3b7684", pamiec: "#13212a" };
var QUELLE = { nid: "denkmale.quelle.nid", gez: "denkmale.quelle.gez", wd: "denkmale.quelle.wd", osm: "denkmale.quelle.osm" };
function kl(ep) { return ep == null ? "null" : ep; }
// Registerpunkte aus Wikidata: dieselbe Auswahl wie die Ebene rejestr der freien Karte (karta.js)
var REG = R ? R.objekte.features.filter(function (f) { return f.properties.q.indexOf("wd") > -1; }) : [];

// Objekte mit Klasse als Text-Schlüssel für MapLibre (null → "null")
var OBJ = { type: "FeatureCollection", features: O.objekte.features.map(function (f) {
  var p = f.properties; return { type: "Feature", geometry: f.geometry, properties: { h: p.h, k: kl(p.ep), w: p.w, mfh: p.mfh, del: p.del, kam: p.h === true && p.mfh === true } };
}) };
var OM = (O.ortsmarken || [])[0];

// ---------- Zustand
var H = KS.hashLesen();
var S = { ep: H.ep ? H.ep.split(",").filter(function (k) { return KLASSEN.indexOf(k) > -1; }) : KLASSEN.slice(), nur: H.nur === "1", alle: H.alle === "1", kx: H.kx !== "0", d3: H["3d"] === "1" };
var drei = null, bereit = false;
function hash() { KS.hashSchreiben(bereit ? map : null, { ep: S.ep.length === KLASSEN.length ? "" : S.ep.join(",") || "-", nur: S.nur, alle: S.alle, kx: S.kx ? "" : "0", "3d": drei && drei.an() }); }

// ---------- Karte
var map = KS.karte({
  kamera: KS.kameraAusHash(H.k),
  quellen: { kx: { type: "geojson", data: B.komplexe, attribution: t("kamienice.bild_bdot") }, obj: { type: "geojson", data: OBJ, attribution: t("kamienice.bild_osm") },
    om: { type: "geojson", data: OM ? { type: "FeatureCollection", features: [{ type: "Feature", geometry: OM.geometry, properties: {} }] } : { type: "FeatureCollection", features: [] } } },
  ebenen: [
    { id: "kx-flaeche", type: "fill", source: "kx", paint: { "fill-color": ["match", ["get", "r"], "zabudowa", KX_FARBE.zabudowa, "twierdza", KX_FARBE.twierdza, "muzeum", KX_FARBE.muzeum, KX_FARBE.pamiec], "fill-opacity": 0.18 } },
    { id: "kx-linie", type: "line", source: "kx", paint: { "line-color": ["match", ["get", "r"], "zabudowa", KX_FARBE.zabudowa, "twierdza", KX_FARBE.twierdza, "muzeum", KX_FARBE.muzeum, KX_FARBE.pamiec], "line-width": 1.2, "line-dasharray": [2, 1] } }
  ],
  oben: [
    { id: "obj", type: "circle", source: "obj", paint: {
      "circle-color": ["match", ["get", "k"]].concat([].concat.apply([], KLASSEN.map(function (k) { return [k, KL_FARBE[k]]; }))).concat(["#ffffff"]),
      "circle-stroke-color": ["case", ["get", "h"], "#13212a", "#808d92"], "circle-stroke-width": ["case", ["get", "kam"], 3, 1],
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, ["case", ["get", "kam"], 5, ["get", "h"], 3.4, 2.4], 16, ["case", ["get", "kam"], 10, ["get", "h"], 7, 5]] } },
    { id: "om-ring", type: "circle", source: "om", paint: { "circle-radius": 13, "circle-color": "rgba(0,0,0,0)", "circle-stroke-color": "#6a2c82", "circle-stroke-width": 2.5 } },
    { id: "om-punkt", type: "circle", source: "om", paint: { "circle-radius": 4, "circle-color": "#6a2c82" } }
  ]
});

// ---------- Werkzeug: 3D
var k3 = el("button", "chip chip--knopf"); k3.type = "button"; k3.appendChild(el("span", null, t("planer.ks_3d"))); k3.setAttribute("aria-pressed", "false");
$("werkzeug").appendChild(k3);

// ---------- Filter im Blatt
var epBox = $("ep");
function epBauen() {
  epBox.innerHTML = ""; epBox.appendChild(el("legend", null, t("kamienice.bauzeit_titel")));
  var n = zaehlen();
  KLASSEN.forEach(function (k) {
    var l = el("label", "chip chip--ein"), r = document.createElement("input"); r.type = "checkbox"; r.value = k; r.checked = S.ep.indexOf(k) > -1;
    r.disabled = !(n[k] > 0);   // ohne Treffer nicht anbieten
    var z = el("i", "ks-zeichen"); z.style.background = KL_FARBE[k]; z.setAttribute("aria-hidden", "true");
    l.appendChild(r); l.appendChild(z); l.appendChild(el("span", null, t(KL_TEXT[k]) + " (" + zahl(n[k] || 0) + ")")); epBox.appendChild(l);
  });
  epBox.appendChild(el("p", "ks-fuss", t("denkmale.klasse.hinweis")));
}
epBox.addEventListener("change", function (e) {
  if (e.target.type !== "checkbox") return;
  var i = S.ep.indexOf(e.target.value); if (e.target.checked && i < 0) S.ep.push(e.target.value); else if (!e.target.checked && i > -1) S.ep.splice(i, 1);
  anwenden();
});
function schalter(id, feld) {
  var b = $(id); b.setAttribute("aria-pressed", String(S[feld]));
  b.addEventListener("click", function () { S[feld] = !S[feld]; b.setAttribute("aria-pressed", String(S[feld])); epBauen(); anwenden(); });
}
schalter("nur-kamienice", "nur"); schalter("alle-objekte", "alle"); schalter("komplexe", "kx");

// Zählung je Klasse in der aktuellen Auswahl (mit Denkmalangabe, bei „alle“ auch ohne, bei „nur“ nur Kamienice)
function imFilter(p) { return S.nur ? p.kam : (S.alle || p.h === true); }
function zaehlen() { var n = {}; OBJ.features.forEach(function (f) { if (imFilter(f.properties)) n[f.properties.k] = (n[f.properties.k] || 0) + 1; }); return n; }
function anwenden() {
  if (bereit) {
    var f = ["all", ["in", ["get", "k"], ["literal", S.ep]]];
    if (S.nur) f.push(["==", ["get", "kam"], true]); else if (!S.alle) f.push(["==", ["get", "h"], true]);
    map.setFilter("obj", f);
    ["kx-flaeche", "kx-linie"].forEach(function (id) { map.setLayoutProperty(id, "visibility", S.kx ? "visible" : "none"); });
  }
  legende(); hash(); fertig();
}

// ---------- Legende
function legende() {
  var L = $("legende"); L.innerHTML = "";
  L.appendChild(el("p", "ks-legende__titel", S.nur ? t("kamienice.leg_kamienice") : S.alle ? t("kamienice.leg_alle") : t("kamienice.leg_h")));
  var ul = el("ul");
  KLASSEN.filter(function (k) { return S.ep.indexOf(k) > -1; }).forEach(function (k) {
    var li = el("li"), z = el("i", "ks-zeichen"); z.style.background = KL_FARBE[k]; z.setAttribute("aria-hidden", "true"); li.appendChild(z); li.appendChild(document.createTextNode(t(KL_TEXT[k]))); ul.appendChild(li);
  });
  L.appendChild(ul);
  var u2 = el("ul");
  var li = el("li"), z = el("i", "ks-zeichen"); z.style.borderWidth = "3px"; z.setAttribute("aria-hidden", "true"); li.appendChild(z); li.appendChild(document.createTextNode(t("kamienice.leg_kam"))); u2.appendChild(li);
  if (S.alle) { var l2 = el("li"), z2 = el("i", "ks-zeichen"); z2.style.borderColor = "#808d92"; z2.setAttribute("aria-hidden", "true"); l2.appendChild(z2); l2.appendChild(document.createTextNode(t("kamienice.leg_ohne_h"))); u2.appendChild(l2); }
  if (S.kx) Object.keys(KX_TEXT).forEach(function (k) { var l3 = el("li"), z3 = el("i", "ks-zeichen ks-zeichen--flaeche"); z3.style.borderColor = KX_FARBE[k]; z3.style.borderStyle = "dashed"; z3.setAttribute("aria-hidden", "true"); l3.appendChild(z3); l3.appendChild(document.createTextNode(t(KX_TEXT[k]))); u2.appendChild(l3); });
  if (OM) { var l4 = el("li"), z4 = el("i", "ks-zeichen"); z4.style.borderColor = "#6a2c82"; z4.style.borderWidth = "2.5px"; z4.setAttribute("aria-hidden", "true"); l4.appendChild(z4); l4.appendChild(document.createTextNode(t("denkmale.ortsmarke.kosciuszki_18"))); u2.appendChild(l4); }
  L.appendChild(u2);
  var n = zaehlen(), summe = S.ep.reduce(function (a, k) { return a + (n[k] || 0); }, 0);
  L.appendChild(el("p", null, S.nur ? t("denkmale.budynki", { n: summe }) : S.alle ? t("kamienice.obiekty", { n: summe }) : t("denkmale.zabytki", { n: summe })));
  L.appendChild(el("p", null, KS.geprueft(O) ? KS.sichtPunkt(O.sichtpruefung.ergebnis) + " " + t("denkmale.sicht.budynek") : t("kamienice.leg_ungeprueft")));
  var d3 = drei && drei.legende(); if (d3) L.appendChild(d3);
  KS.legendeZeigen();
}

// ---------- Zahlen im Blatt (alle aus den Datendateien)
function zeile(ul, text, wert, klein) { var li = el("li"); li.appendChild(el("span", null, text)); li.appendChild(el("b", null, wert)); if (klein) li.appendChild(el("small", null, klein)); ul.appendChild(li); }
function zahlenBauen() {
  var zO = O.zaehlung, zB = B.zaehlung;
  var u1 = $("zahlen-osm"); u1.innerHTML = "";
  zeile(u1, t("kamienice.z_objekte"), zahl(zO.objekte), t("kamienice.z_objekte_klein", { aussen: zahl(zO.ausserhalb_stadt) }));
  zeile(u1, t("kamienice.z_heritage"), zahl(zO.mit_heritage));
  zeile(u1, t("kamienice.z_start"), zahl(zO.mit_start_date), t("kamienice.z_start_klein", { lesbar: zahl(zO.bauzeit_lesbar), unlesbar: zahl(zO.bauzeit_nicht_lesbar) }));
  zeile(u1, t("kamienice.z_treffer"), zahl(zO.treffer_gebaeude), t("kamienice.z_mfh", { n: zahl(zO.davon_mfh) }));
  var kam = Object.keys(O.kamienice || {}).reduce(function (a, k) { return a + O.kamienice[k]; }, 0);
  zeile(u1, t("kamienice.z_kamienice"), zahl(kam), t("denkmale.kamienica_definition"));
  var u3 = $("zahlen-register"); u3.innerHTML = "";
  if (R && R.zaehlung.wd) {
    var zR = R.zaehlung.wd;
    zeile(u3, t("kamienice.z_reg_punkte"), zahl(REG.length), t("kamienice.z_reg_punkte_klein", { zeilen: zahl(zR.zeilen), doppelt: zahl(zR.doppelt_ueber_nummer), ohne: zahl(zR.ohne_lage), aussen: zahl(zR.ausserhalb_stadt) }));
    zeile(u3, t("kamienice.z_treffer"), zahl(zR.treffer_gebaeude), t("kamienice.z_mfh", { n: zahl(zR.davon_mfh) }));
    var mitEp = REG.filter(function (f) { return f.properties.ep != null; }).length;   // aus den Punkten, wie Karte und Download
    zeile(u3, t("kamienice.z_reg_bauzeit"), zahl(mitEp), t("kamienice.z_reg_bauzeit_klein", { n: zahl(REG.length - mitEp) }));
  } else zeile(u3, t("denkmale.quelle.wd"), t("kamienice.q_fehlt"));
  var u2 = $("zahlen-bdot"); u2.innerHTML = "";
  zeile(u2, t("kamienice.z_gebaeude"), zahl(zB.gebaeude));
  zeile(u2, t("denkmale.wohngebaeude"), zahl(zB.wohngebaeude));
  zeile(u2, t("denkmale.mehrfamilienhaus"), zahl(zB.mehrfamilienhaeuser));
  zeile(u2, t("denkmale.namensbezug"), zahl(zB.namensbezug), t("denkmale.namensbezug.hinweis"));
  Object.keys(KX_TEXT).forEach(function (k) { zeile(u2, t(KX_TEXT[k]), zahl((zB.komplexe || {})[k] || 0)); });
  $("komplex-hinweis").textContent = t("denkmale.komplex.hinweis");
  // Tabelle je Delegatur: BDOT10k-Zählungen und OSM-Objekte mit Denkmalangabe
  var tab = el("table", "tabelle"); tab.appendChild(el("caption", "nur-sr", t("kamienice.tab_caption")));
  var kopf = el("tr"); [t("denkmale.delegatura"), t("kamienice.sp_mfh"), t("kamienice.sp_namen"), t("kamienice.sp_reg"), t("kamienice.sp_reg_mfh"), t("kamienice.sp_h"), t("kamienice.sp_kam")].forEach(function (x) { var th = el("th", null, x); th.scope = "col"; kopf.appendChild(th); });
  var th = el("thead"); th.appendChild(kopf); tab.appendChild(th);
  var hDel = {}; OBJ.features.forEach(function (f) { if (f.properties.h === true) hDel[f.properties.del] = (hDel[f.properties.del] || 0) + 1; });
  var rDel = {}, rMfh = {}; REG.forEach(function (f) { var d = f.properties.del || "-"; rDel[d] = (rDel[d] || 0) + 1; if (f.properties.mfh === true) rMfh[d] = (rMfh[d] || 0) + 1; });
  var tb = el("tbody");
  function reihe(name, d, r, rm, h, k) { var tr = el("tr"), c = el("th", null, name); c.scope = "row"; tr.appendChild(c); [d.mehrfamilienhaeuser, d.namensbezug, r, rm, h, k].forEach(function (v) { tr.appendChild(el("td", null, v == null ? "–" : zahl(v))); }); tb.appendChild(tr); }
  Object.keys(B.delegaturen).sort().forEach(function (k) { reihe(k, B.delegaturen[k], R ? rDel[k] || 0 : null, R ? rMfh[k] || 0 : null, hDel[k] || 0, (O.kamienice || {})[k] || 0); });
  reihe(t("denkmale.nicht_zugeordnet"), B.nicht_zugeordnet, R ? rDel["-"] || 0 : null, R ? rMfh["-"] || 0 : null, 0, 0);
  tab.appendChild(tb);
  var r = $("tab-delegatur"); r.innerHTML = ""; r.appendChild(tab);
  // Quellen und Stand
  var q = $("quellen-stand"); q.innerHTML = "";
  zeile(q, t("kamienice.q_bdot"), KS.datum(B.stand));
  var spO = O.sichtpruefung, spR = R && R.sichtpruefung;
  zeile(q, t(QUELLE.osm), KS.datum(O.stand), KS.geprueft(O) ? KS.sichtLage(spO, spO.ergebnis) + " " + KS.sichtAnsicht(spO.ergebnis)
    : t("kamienice.q_osm_klein", { n: zahl(spO ? spO.stichprobe : null) }));
  if (R) zeile(q, t(QUELLE.wd), KS.datum(R.stand), KS.geprueft(R) ? t("kamienice.q_wd_teil") + " " + KS.sichtLage(spR, spR.ergebnis) + " " + KS.sichtAnsicht(spR.ergebnis)
    : t("kamienice.q_wd_klein", { n: zahl(spR ? spR.stichprobe : null) }));
  else zeile(q, t(QUELLE.wd), t("kamienice.q_fehlt"));
  ["nid", "gez"].forEach(function (k) { zeile(q, t(QUELLE[k]), t("kamienice.q_fehlt")); });
  // Ortsmarke
  var om = $("ortsmarke");
  if (OM) { om.appendChild(el("p", null, t("kamienice.om_text"))); om.appendChild(el("p", "ks-fuss", t("denkmale.ortsmarke.lage_offen") + " " + t("kamienice.om_quelle"))); }
  $("om-zeigen").hidden = !OM;
}
$("om-zeigen").addEventListener("click", function () {
  if (!OM || !bereit) return;
  var z = { center: OM.geometry.coordinates, zoom: Math.max(map.getZoom(), 16) };
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) map.jumpTo(z); else map.easeTo(Object.assign(z, { duration: 900 }));
});

// ---------- Klicks
map.on("click", function (e) {
  var f = map.queryRenderedFeatures([[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]], { layers: ["om-punkt", "om-ring", "obj"] });
  var h = "";
  if (f.length && f[0].layer.id.indexOf("om") === 0) {
    h = "<b>" + esc(t("denkmale.ortsmarke.kosciuszki_18")) + "</b><div class='pop-q'>" + esc(t("kamienice.om_text")) + "</div><div class='pop-q'>" + esc(t("denkmale.ortsmarke.lage_offen")) + "</div>";
  } else if (f.length) {
    var p = f[0].properties;
    h = "<b>" + esc(p.kam === true || p.kam === "true" ? t("kamienice.pop_kamienica") : (p.h === true || p.h === "true") ? t("kamienice.pop_h") : t("kamienice.pop_ohne_h")) + "</b><table class='pop-tab'>" +
      "<tr><td>" + esc(t("kamienice.pop_bauzeit")) + "</td><td>" + esc(t(KL_TEXT[p.k] || KL_TEXT["null"])) + "</td></tr>" +
      "<tr><td>" + esc(t("denkmale.delegatura")) + "</td><td>" + esc(p.del) + "</td></tr></table>" +
      (p.mfh === true || p.mfh === "true" ? "<div class='pop-q'>" + esc(t("denkmale.mehrfamilienhaus")) + " (BDOT10k)</div>" : "") +
      "<div class='pop-q'>" + esc(KS.geprueft(O) ? t("kamienice.pop_vermerk") + " " + KS.sichtPunkt(O.sichtpruefung.ergebnis) : t("kamienice.pop_quelle")) + "</div>";
  } else {
    if (drei && drei.an() && map.getLayer("geb3d") && map.queryRenderedFeatures(e.point, { layers: ["geb3d"] }).length) return;   // Gebäude-Popup aus kartenseite.js
    var k = map.queryRenderedFeatures(e.point, { layers: ["kx-flaeche"] }).filter(function () { return S.kx; });
    if (k.length) { var q = k[0].properties; h = "<b>" + esc(q.n || t(KX_TEXT[q.r] || "denkmale.komplex.zabudowa")) + "</b><div class='pop-q'>" + esc(t(KX_TEXT[q.r] || "denkmale.komplex.zabudowa")) + "</div><div class='pop-q'>" + esc(t("denkmale.komplex.hinweis")) + "</div>"; }
  }
  if (h) new maplibregl.Popup({ maxWidth: "290px" }).setLngLat(e.lngLat).setHTML(h).addTo(map);
});
map.on("moveend", hash);

function fertig() { if (bereit) KS.bereitNach(map, function () { return drei ? drei.laufend() : 0; }); }
// Abzeichen und Grenze zur Lage: Ergebnis der Sichtprüfung am Luftbild, solange keine vorliegt der Hinweis „ungeprüft“
function sichtHinweis() {
  var ok = KS.geprueft(O) && (!R || KS.geprueft(R)), g = O.sichtpruefung && O.sichtpruefung.gesamt;
  var abz = $("abz-lage"); abz.textContent = ok ? t("denkmale.sicht.abz") : t("kamienice.abz_ungeprueft"); abz.hidden = false;
  $("grenze-lage").textContent = ok && g ? t("denkmale.sicht.gesamt") + " " + KS.sichtLage(O.sichtpruefung, g) + " " + t("denkmale.sicht.budynek")
    : t("kamienice.leg_ungeprueft");
}
zahlenBauen(); epBauen(); legende(); sichtHinweis();
map.on("load", function () {
  bereit = true;
  drei = KS.drei(map, { knopf: k3, legende: legende, geaendert: hash, bereit: fertig, meldung: function () { legende(); }, ziel: function () { return OM ? OM.geometry.coordinates : window.KIEZ_ORT.karte.haus_ziel; },
    klickVorrang: function (e) { return map.queryRenderedFeatures([[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]], { layers: ["obj", "om-punkt", "om-ring"] }).length > 0; } });
  anwenden();
  if (S.d3) drei.setzen(true, false);
});
})();
