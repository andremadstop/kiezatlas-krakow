/* Kiezatlas: Wohnungsbestand und Sanierung (modernizacja.html in jeder Sprache).
   Gebäude in der Verwaltung des städtischen ZBK (Liste im BIP, Zählungen in daten/sanierung.js, verortete Einträge
   nur in öffentlichem Eigentum in daten/sanierung_odbl.js), Plattenbau-Kandidaten je Stadtteil als Schätzung aus
   BDOT10k (nur Merkmale, keine Baujahre), Höhen aus LoD2 (Stand 2017), die Ortsmarke ul. Kościuszki 18 und der
   Bezug zu Erreichbarkeit und Grün (daten/planer_fuss_odbl.js, auf Knopfdruck). Kein Denkmalstatus: Die Liste nennt
   keinen, das Register fehlt; die OSM-Denkmale lassen sich nur als ungeprüfte Ebene dazuschalten.
   Zustand im Hash: m (Stadtteilfarbe blok|osiedle|-), dz (OSM-Denkmale), st, 3d, k.
   Braucht vorher kartenseite.js, daten/sanierung.js, daten/sanierung_odbl.js. */
(function () {
"use strict";
var KS = window.KIEZ_KS, T = window.KIEZ_THEMEN, I18N = window.KIEZ_I18N, SL = window.KIEZ_SANIERUNG, SO = window.KIEZ_SANIERUNG_ODBL;
if (!KS || !document.getElementById("karte") || !SL || !SO) return;
var t = I18N.t, el = KS.el, $ = KS.$, esc = KS.esc, zahl = KS.zahl, NB = " ";
var D = KS.WURZEL + "daten/";

var ART = ["M", "MU", "MP", "MUP", "U", "UP", "P"];
var ART_TEXT = { M: "sanierung.art.m", MU: "sanierung.art.mu", MP: "sanierung.art.mp", MUP: "sanierung.art.mup", U: "sanierung.art.u", UP: "sanierung.art.up", P: "sanierung.art.p" };
var ART_FARBE = { M: "#13212a", MU: "#3b7684", MP: "#3b7684", MUP: "#3b7684", U: "#a8b8be", UP: "#a8b8be", P: "#ffffff" };
var EIG = ["gmina", "skarb_panstwa", "publiczne_mieszane", "z_prywatnymi", "prywatne", "brak"];
var EIG_TEXT = { gmina: "sanierung.eig.gmina", skarb_panstwa: "sanierung.eig.skarb_panstwa", publiczne_mieszane: "sanierung.eig.publiczne_mieszane",
  z_prywatnymi: "sanierung.eig.z_prywatnymi", prywatne: "sanierung.eig.prywatne", brak: "sanierung.eig.brak" };
var VK = ["verortet", "beschreibung", "poza_krakowem", "ulica_nie_znaleziona", "numer_nie_znaleziony", "mehrdeutig_ulica", "mehrdeutig_punkt", "abweichung_dzielnica"];
var VK_TEXT = { verortet: "sanierung.vk.verortet", beschreibung: "sanierung.vk.beschreibung", poza_krakowem: "sanierung.vk.poza_krakowem",
  ulica_nie_znaleziona: "sanierung.vk.ulica_nie_znaleziona", numer_nie_znaleziony: "sanierung.vk.numer_nie_znaleziony", mehrdeutig_ulica: "sanierung.vk.mehrdeutig_ulica",
  mehrdeutig_punkt: "sanierung.vk.mehrdeutig_punkt", abweichung_dzielnica: "sanierung.vk.abweichung_dzielnica" };
var HQ_TEXT = { lod2: "planer.ks_hq.lod2", geschosse: "planer.ks_hq.geschosse", ersatz: "planer.ks_hq.ersatz" };
var TYP_TEXT = { blok: "sanierung.typ.blok", osiedle: "sanierung.typ.osiedle" };
var MASS = { blok: "sanierung.mass.blok", osiedle: "sanierung.mass.osiedle" };
var KL = [10, 20, 30, 40];   // Anteil in Prozent je Stadtteil (feste Stufen)
var TD = SO.typologie_dzielnice.je_dzielnica;
function anteil(nr, m) { var d = TD[nr]; return d && d.mfh ? 100 * d[m] / d.mfh : null; }

// Stadtteile mit Anteilen als Eigenschaft (Kopie, KIEZ_STADTTEILE bleibt unverändert)
var TEILE = { type: "FeatureCollection", features: window.KIEZ_STADTTEILE.features.map(function (f) {
  var nr = f.properties.nr; return { type: "Feature", geometry: f.geometry, properties: { nr: nr, blok: anteil(nr, "blok"), osiedle: anteil(nr, "osiedle") } };
}) };

// ---------- Zustand
var H = KS.hashLesen();
var S = { m: H.m === "-" ? "" : (H.m === "osiedle" ? "osiedle" : "blok"), dz: H.dz === "1", st: T.TEIL[H.st] ? H.st : "", d3: H["3d"] === "1" };
var drei = null, bereit = false;
function hash() { KS.hashSchreiben(bereit ? map : null, { m: S.m === "blok" ? "" : (S.m || "-"), dz: S.dz, st: S.st, "3d": drei && drei.an() }); }

function stufe(m) {
  var e = ["step", ["get", m], T.STUFEN[0]]; KL.forEach(function (g, i) { e.push(g, T.STUFEN[i + 1]); });
  return ["case", ["==", ["typeof", ["get", m]], "number"], e, T.GRAU];
}
var OM = SO.ortsmarke;
var map = KS.karte({
  kamera: KS.kameraAusHash(H.k),
  quellen: { anteil: { type: "geojson", data: TEILE, attribution: t("sanierung.bild_bdot") },
    zbk: { type: "geojson", data: SO.punkte, attribution: t("sanierung.bild_zbk") },
    dz: { type: "geojson", data: { type: "FeatureCollection", features: [] } },
    om: { type: "geojson", data: { type: "FeatureCollection", features: OM && OM.geometry ? [{ type: "Feature", geometry: OM.geometry, properties: {} }] : [] } } },
  ebenen: [{ id: "anteil", type: "fill", source: "anteil", paint: { "fill-color": stufe("blok"), "fill-opacity": 0.55 } }],
  oben: [
    { id: "dz", type: "circle", source: "dz", layout: { visibility: "none" }, paint: { "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 2.5, 16, 6], "circle-color": "#efe6f3", "circle-stroke-color": "#6a2c82", "circle-stroke-width": 1 } },
    { id: "zbk-typ", type: "circle", source: "zbk", filter: ["!=", ["get", "typ"], null], paint: { "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 6.5, 16, 12], "circle-color": "rgba(0,0,0,0)", "circle-stroke-color": "#6a2c82", "circle-stroke-width": 2 } },
    { id: "zbk", type: "circle", source: "zbk", paint: {
      "circle-color": ["match", ["get", "art"]].concat([].concat.apply([], ART.map(function (a) { return [a, ART_FARBE[a]]; }))).concat(["#ffffff"]),
      "circle-stroke-color": "#13212a", "circle-stroke-width": 1, "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 3.2, 16, 7.5] } },
    { id: "om-ring", type: "circle", source: "om", paint: { "circle-radius": 14, "circle-color": "rgba(0,0,0,0)", "circle-stroke-color": "#6a2c82", "circle-stroke-width": 2.5 } }
  ]
});
var wahl = KS.stadtteilWahl(map);

// ---------- Werkzeug: Stadtteilfarbe und 3D
var wz = $("werkzeug");
var mf = el("fieldset", "themen"); mf.appendChild(el("legend", "nur-sr", t("sanierung.mass_titel")));
[["blok", t(MASS.blok)], ["osiedle", t(MASS.osiedle)], ["", t("sanierung.mass.keins")]].forEach(function (w) {
  var l = el("label", "chip chip--schalter"), r = document.createElement("input"); r.type = "radio"; r.name = "m"; r.value = w[0]; r.checked = S.m === w[0];
  l.appendChild(r); l.appendChild(el("span", null, w[1])); mf.appendChild(l);
});
mf.addEventListener("change", function (e) { if (e.target.name === "m") { S.m = e.target.value; anwenden(); } });
wz.appendChild(mf);
var k3 = el("button", "chip chip--knopf"); k3.type = "button"; k3.appendChild(el("span", null, t("planer.ks_3d"))); k3.setAttribute("aria-pressed", "false");
wz.appendChild(k3);
var dzKnopf = $("dz-knopf"); dzKnopf.setAttribute("aria-pressed", String(S.dz));
dzKnopf.addEventListener("click", function () { S.dz = !S.dz; dzKnopf.setAttribute("aria-pressed", String(S.dz)); denkmale(); });

function anwenden() {
  if (bereit) {
    map.setLayoutProperty("anteil", "visibility", S.m ? "visible" : "none");
    if (S.m) map.setPaintProperty("anteil", "fill-color", stufe(S.m));
  }
  legende(); hash(); fertig();
}
var laeuft = 0;
function denkmale() {
  if (!bereit) return;
  if (!S.dz) { map.setLayoutProperty("dz", "visibility", "none"); legende(); hash(); fertig(); return; }
  laeuft++;
  T.laden(D + "denkmale_odbl.js", "KIEZ_DENKMALE_ODBL", function (d) {
    laeuft--;
    if (d) { map.getSource("dz").setData({ type: "FeatureCollection", features: d.objekte.features.filter(function (f) { return f.properties.h === true; }) }); map.setLayoutProperty("dz", "visibility", S.dz ? "visible" : "none"); }
    else { S.dz = false; dzKnopf.setAttribute("aria-pressed", "false"); }
    legende(); hash(); fertig();
  });
}

// ---------- Legende
function legende() {
  var L = $("legende"); L.innerHTML = "";
  if (S.m) {
    L.appendChild(el("p", "ks-legende__titel", t(S.m === "blok" ? "sanierung.leg_blok" : "sanierung.leg_osiedle")));
    var st = el("div", "stufen stufen--flach"); st.setAttribute("aria-hidden", "true");
    T.STUFEN.forEach(function (f) { var x = el("span"); x.style.background = f; st.appendChild(x); }); L.appendChild(st);
    var m = el("div", "marken"); m.appendChild(el("span", null, "0"));
    KL.forEach(function (g) { m.appendChild(el("span", null, I18N.fmt.zahl(g))); }); m.appendChild(el("span", null, "%")); L.appendChild(m);
    L.appendChild(el("p", null, t("sanierung.leg_schaetzung")));
  }
  var n = {}; SO.punkte.features.forEach(function (f) { n[f.properties.art] = (n[f.properties.art] || 0) + 1; });
  L.appendChild(el("p", "ks-legende__titel", t("sanierung.leg_zbk", { n: zahl(SO.punkte.features.length) })));
  var ul = el("ul");
  ART.filter(function (a) { return n[a]; }).forEach(function (a) {
    var li = el("li"), z = el("i", "ks-zeichen"); z.style.background = ART_FARBE[a]; z.setAttribute("aria-hidden", "true"); li.appendChild(z);
    li.appendChild(document.createTextNode(t(ART_TEXT[a]) + " (" + zahl(n[a]) + ")")); ul.appendChild(li);
  });
  var lt = el("li"), zt = el("i", "ks-zeichen"); zt.style.borderColor = "#6a2c82"; zt.style.borderWidth = "2px"; zt.style.background = "transparent"; zt.setAttribute("aria-hidden", "true"); lt.appendChild(zt); lt.appendChild(document.createTextNode(t("sanierung.leg_typ"))); ul.appendChild(lt);
  if (OM) { var lo = el("li"), zo = el("i", "ks-zeichen"); zo.style.borderColor = "#6a2c82"; zo.style.borderWidth = "2.5px"; zo.setAttribute("aria-hidden", "true"); lo.appendChild(zo); lo.appendChild(document.createTextNode(t("denkmale.ortsmarke.kosciuszki_18"))); ul.appendChild(lo); }
  if (S.dz && window.KIEZ_DENKMALE_ODBL) { var ld = el("li"), zd = el("i", "ks-zeichen"); zd.style.background = "#efe6f3"; zd.style.borderColor = "#6a2c82"; zd.setAttribute("aria-hidden", "true"); ld.appendChild(zd); ld.appendChild(document.createTextNode(KS.geprueft(window.KIEZ_DENKMALE_ODBL) ? t("sanierung.leg_dz_probe") : t("sanierung.leg_dz"))); ul.appendChild(ld); }
  L.appendChild(ul);
  L.appendChild(el("p", null, t("sanierung.leg_privat")));
  var d3 = drei && drei.legende(); if (d3) L.appendChild(d3);
  KS.legendeZeigen();
}

// ---------- Zahlen im Blatt (alle aus den Datendateien)
function zeile(ul, text, wert, klein) { var li = el("li"); li.appendChild(el("span", null, text)); li.appendChild(el("b", null, wert)); if (klein) li.appendChild(el("small", null, klein)); ul.appendChild(li); }
function proz(v, n) { return v == null ? t("kern.k_a") : I18N.fmt.anteil(v, n == null ? 1 : n); }
function bauen() {
  var L = SL.liste;
  $("liste-kopf").textContent = t("sanierung.liste_kopf", { stand: KS.datum(SL.stand) });
  var u = $("liste"); u.innerHTML = "";
  zeile(u, t("sanierung.z_eintraege"), zahl(L.eintraege), t("sanierung.z_eintraege_klein", { krakow: zahl(L.miejscowosc.krakow), wieliczka: zahl(L.miejscowosc.wieliczka) }));
  ART.forEach(function (a) { if (L.je_art[a]) zeile(u, t(ART_TEXT[a]), zahl(L.je_art[a])); });
  var u2 = $("eigentum"); u2.innerHTML = "";
  EIG.forEach(function (k) { if (L.je_eigentum[k] != null) zeile(u2, t(EIG_TEXT[k]), zahl(L.je_eigentum[k])); });
  zeile(u2, t("sanierung.z_samoistne"), zahl(L.samoistne_posiadanie));
  $("liste-fehlt").textContent = t("sanierung.liste_fehlt");
  $("punkte-regel").textContent = t("sanierung.punkte_regel", { n: zahl(SO.punkte.features.length), klein: zahl(SO.punkte.ausgelassen_kleinhaus), niskie: zahl(SO.punkte.ausgelassen_unter_3_geschosse), gs: zahl(SO.punkte.geschosse_min) });
  // Verortung
  var V = SO.verortung, u3 = $("verortung"); u3.innerHTML = "";
  zeile(u3, t("sanierung.z_quote"), proz(V.quote), t("sanierung.wilson", { von: proz(V.wilson95[0]), bis: proz(V.wilson95[1]), n: zahl(V.in_krakow) }));
  VK.forEach(function (k) { if (V.je_klasse[k] != null) zeile(u3, t(VK_TEXT[k]), zahl(V.je_klasse[k])); });
  var G = SO.gegenprobe_dzielnica;
  zeile(u3, t("sanierung.z_gegenprobe"), proz(G.quote), t("sanierung.wilson", { von: proz(G.wilson95[0]), bis: proz(G.wilson95[1]), n: zahl(G.n) }));
  // Höhen
  var K = SO.verknuepfung, u4 = $("hoehen"); u4.innerHTML = "";
  zeile(u4, t("sanierung.z_umriss"), zahl(K.umriss), t("sanierung.z_von_verortet", { n: zahl(K.verortet) }));
  zeile(u4, t("sanierung.z_punkt"), zahl(K.punkt));
  zeile(u4, t("sanierung.z_ohne"), zahl(K.ohne));
  zeile(u4, t("planer.ks_hq.lod2"), zahl(K.hoehe_lod2));
  zeile(u4, t("planer.ks_hq.geschosse"), zahl(K.hoehe_geschosse));
  // Typologie
  var Y = SL.typologie, kr = Y.kriterien;
  $("typ-regel").textContent = t("sanierung.typ_regel", { geschosse: zahl(kr.geschosse_min), flaeche: zahl(kr.flaeche_min_m2), recht: I18N.fmt.zahl(kr.rechteckigkeit_min, 2) });
  $("typ-osiedle").textContent = t("sanierung.typ_osiedle_regel", { nachbarn: zahl(kr.nachbarn_min), umkreis: zahl(kr.umkreis_m) });
  var u5 = $("typ-zahlen"); u5.innerHTML = "";
  zeile(u5, t("sanierung.z_mfh"), zahl(Y.stadt.mfh));
  zeile(u5, t(TYP_TEXT.blok), zahl(Y.stadt.blok), t("sanierung.z_anteil_mfh", { a: proz(100 * Y.stadt.blok / Y.stadt.mfh) }));
  zeile(u5, t(TYP_TEXT.osiedle), zahl(Y.stadt.osiedle), t("sanierung.z_anteil_mfh", { a: proz(100 * Y.stadt.osiedle / Y.stadt.mfh) }));
  zeile(u5, t("sanierung.z_angebaut"), zahl(Y.stadt.blok_angebaut), t("sanierung.z_angebaut_klein", { m: zahl(Y.angebaut.grenze_min_m), osiedle: zahl(Y.stadt.osiedle_angebaut) }));
  var SP = Y.sichtpruefung;
  if (SP) {
    var so = SP.osiedle, sk = SP.kein_kandidat;
    zeile(u5, t("sanierung.z_sicht"), zahl(so.ja) + " / " + zahl(so.ja + so.nein), t("sanierung.z_sicht_klein", { n: zahl(so.n), datum: I18N.fmt.datum(SP.datum), ja: zahl(so.ja), nein: zahl(so.nein), unklar: zahl(so.unklar), von: zahl(so.wilson95[0]), bis: zahl(so.wilson95[1]), kn: zahl(sk.n), kja: zahl(sk.ja), knein: zahl(sk.nein), kunklar: zahl(sk.unklar) }));
  }
  zeile(u5, t("sanierung.z_typ_zbk"), zahl(K.typ_blok), t("sanierung.z_typ_zbk_klein", { osiedle: zahl(K.typ_osiedle) }));
  var lit = Y.literatur, p = $("literatur"); p.innerHTML = "";
  p.appendChild(document.createTextNode(t("sanierung.literatur", { autoren: lit.autoren, zeitschrift: lit.zeitschrift, band: String(lit.band), jahr: String(lit.jahr), artikel: lit.artikel }) + " "));
  var a = el("a", "link", "doi:" + lit.doi); a.href = "https://doi.org/" + lit.doi; p.appendChild(a);
  // Ortsmarke
  var o = SL.ortsmarke, om = $("ortsmarke"); om.innerHTML = "";
  om.appendChild(el("p", null, t("sanierung.om_text")));
  if (o && o.in_liste) om.appendChild(el("p", null, t("sanierung.om_liste", { art: ART_TEXT[o.art] ? t(ART_TEXT[o.art]) : o.art, eig: EIG_TEXT[o.eigentum] ? t(EIG_TEXT[o.eigentum]) : o.eigentum, st: KS.stadtteilName(o.st) })));
  om.appendChild(el("p", "ks-fuss", t("denkmale.ortsmarke.lage_offen") + " " + t("sanierung.om_quelle")));
  // Quellen: Vermerke wörtlich (Bedingung der Weiterverwendung)
  var q = $("quellen-zbk"); q.innerHTML = "";
  [SL.quellen.zbk.vermerk, SL.quellen.zbk.odpowiedzialnosc, SL.quellen.bdot.vermerk].forEach(function (v) { var li = el("li"); li.lang = "pl"; li.appendChild(KS.vermerkKnoten(v)); q.appendChild(li); });
  tabelleTyp();
}
// Tabelle je Stadtteil: ZBK-Einträge (aus der Liste), Kandidaten; Erreichbarkeit und Grün nach dem Laden
function tabelleTyp() {
  var P = window.KIEZ_PLANER_FUSS, box = $("tab-dzielnice"); box.innerHTML = "";
  function kz(nr, k, a) { if (!P) return null; var R = nr ? P.raeume[nr] : P.gesamt; var w = R && R.werte.filter(function (x) { return x.kennzahl === k && x.art === a; })[0]; return w ? w.wert : null; }
  var tab = el("table", "tabelle"); tab.appendChild(el("caption", "nur-sr", t("sanierung.tab_caption")));
  var kopf = el("tr"), sp = [I18N.sprachwert(window.KIEZ_ORT.gliederung.einheit), t("sanierung.sp_zbk"), t("sanierung.sp_blok"), t("sanierung.sp_osiedle"), t("sanierung.sp_angebaut")];
  if (P) sp.push(t("sanierung.sp_takt"), t("sanierung.sp_gruen"));
  sp.forEach(function (x) { var th = el("th", null, x); th.scope = "col"; kopf.appendChild(th); });
  var th = el("thead"); th.appendChild(kopf); tab.appendChild(th);
  var tb = el("tbody");
  Object.keys(TD).sort().forEach(function (nr) {
    var tr = el("tr", nr === S.st ? "gewaehlt" : null), c = el("th", null, KS.stadtteilName(nr)); c.scope = "row"; tr.appendChild(c);
    var j = SL.liste.je_dzielnica[nr];
    tr.appendChild(el("td", null, zahl(j ? j.n : null)));
    tr.appendChild(el("td", null, zahl(TD[nr].blok) + " (" + proz(anteil(nr, "blok"), 0) + ")"));
    tr.appendChild(el("td", null, zahl(TD[nr].osiedle)));
    tr.appendChild(el("td", null, zahl(TD[nr].blok_angebaut)));
    if (P) { tr.appendChild(el("td", null, proz(kz(nr, "oepnv_takt", "haltestelle_takt"), 0))); tr.appendChild(el("td", null, proz(kz(nr, "gruen_in_radius", "park"), 0))); }
    tb.appendChild(tr);
  });
  tab.appendChild(tb);
  var tf = el("tfoot"), tr = el("tr"), c = el("th", null, I18N.ort("ganze_stadt")); c.scope = "row"; tr.appendChild(c);
  var poza = SL.liste.je_dzielnica.poza;
  tr.appendChild(el("td", null, zahl(SL.liste.eintraege)));
  tr.appendChild(el("td", null, zahl(SL.typologie.stadt.blok)));
  tr.appendChild(el("td", null, zahl(SL.typologie.stadt.osiedle)));
  tr.appendChild(el("td", null, zahl(SL.typologie.stadt.blok_angebaut)));
  if (P) { tr.appendChild(el("td", null, proz(kz("", "oepnv_takt", "haltestelle_takt"), 0))); tr.appendChild(el("td", null, proz(kz("", "gruen_in_radius", "park"), 0))); }
  tf.appendChild(tr); tab.appendChild(tf);
  var r = el("div", "ks-tabelle"); r.tabIndex = 0; r.setAttribute("role", "region"); r.setAttribute("aria-label", t("sanierung.tab_caption")); r.appendChild(tab); box.appendChild(r);
  box.appendChild(el("p", "ks-fuss", t("sanierung.tab_hinweis", { poza: zahl(poza ? poza.n : 0) }) + (P ? " " + t("sanierung.tab_hinweis_fuss") : "")));
}
$("bezug-laden").addEventListener("click", function () {
  var b = this; b.disabled = true; laeuft++;
  T.laden(D + "planer_fuss_odbl.js", "KIEZ_PLANER_FUSS", function (d) { laeuft--; b.hidden = !!d; b.disabled = false; tabelleTyp(); fertig(); });
});
var stSel = $("st-wahl");
KS.stadtteilAuswahl(stSel, t("sanierung.st_keine")); stSel.value = S.st;
stSel.addEventListener("change", function () { stWaehlen(stSel.value, true); });
function stWaehlen(nr, zoom) {
  S.st = T.TEIL[nr] ? nr : ""; stSel.value = S.st; if (bereit) wahl(S.st);
  if (zoom && bereit && S.st) map.fitBounds(T.umriss(T.TEIL[S.st]), { padding: 30, maxZoom: 14, animate: !matchMedia("(prefers-reduced-motion: reduce)").matches });
  stInfo(); tabelleTyp(); hash();
}
function stInfo() {
  var box = $("st-inhalt"); box.innerHTML = "";
  if (!S.st) { box.appendChild(el("p", "ks-fuss", t("sanierung.st_hinweis"))); return; }
  var j = SL.liste.je_dzielnica[S.st] || { n: 0, art: {}, eigentum: {} }, d = TD[S.st] || {};
  var ul = el("ul", "ks-zahlen");
  zeile(ul, t("sanierung.z_eintraege"), zahl(j.n), t("sanierung.st_eig", { gmina: zahl(j.eigentum.gmina || 0), privat: zahl((j.eigentum.z_prywatnymi || 0) + (j.eigentum.prywatne || 0)) }));
  zeile(ul, t("sanierung.st_punkte"), zahl(SO.punkte.features.filter(function (f) { return f.properties.st === S.st; }).length));
  zeile(ul, t("sanierung.z_mfh"), zahl(d.mfh));
  zeile(ul, t(TYP_TEXT.blok), zahl(d.blok), t("sanierung.z_anteil_mfh", { a: proz(anteil(S.st, "blok")) }));
  zeile(ul, t(TYP_TEXT.osiedle), zahl(d.osiedle), t("sanierung.z_anteil_mfh", { a: proz(anteil(S.st, "osiedle")) }));
  box.appendChild(ul);
  box.appendChild(el("p", "ks-fuss", t("sanierung.st_schaetzung")));
}
$("om-zeigen").addEventListener("click", function () {
  if (!OM || !OM.geometry || !bereit) return;
  var z = { center: OM.geometry.coordinates, zoom: Math.max(map.getZoom(), 16) };
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) map.jumpTo(z); else map.easeTo(Object.assign(z, { duration: 900 }));
});

// ---------- Klicks
map.on("click", function (e) {
  var f = map.queryRenderedFeatures([[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]], { layers: ["om-ring", "zbk", "dz"].filter(function (l) { return map.getLayoutProperty(l, "visibility") !== "none"; }) });
  var h = "";
  if (f.length && f[0].layer.id === "om-ring") {
    h = "<b>" + esc(t("denkmale.ortsmarke.kosciuszki_18")) + "</b><div class='pop-q'>" + esc(t("sanierung.om_text")) + "</div><div class='pop-q'>" + esc(t("denkmale.ortsmarke.lage_offen")) + "</div>";
  } else if (f.length && f[0].layer.id === "zbk") {
    var p = f[0].properties, hv = p.h == null || p.h === "null" ? null : Number(p.h);
    h = "<b>" + esc(t("sanierung.pop_titel")) + "</b><table class='pop-tab'>" +
      "<tr><td>" + esc(t("sanierung.pop_art")) + "</td><td>" + esc(ART_TEXT[p.art] ? t(ART_TEXT[p.art]) : p.art) + "</td></tr>" +
      "<tr><td>" + esc(t("sanierung.pop_eig")) + "</td><td>" + esc(EIG_TEXT[p.eig] ? t(EIG_TEXT[p.eig]) : p.eig) + "</td></tr>" +
      (p.fn && p.fn !== "null" ? "<tr><td>" + esc(t("sanierung.pop_fn")) + "</td><td lang='pl'>" + esc(p.fn) + "</td></tr>" : "") +
      (p.gs != null && p.gs !== "null" ? "<tr><td>" + esc(t("planer.ks_geschosse")) + "</td><td>" + esc(zahl(Number(p.gs))) + "</td></tr>" : "") +
      "<tr><td>" + esc(t("planer.ks_hoehe")) + "</td><td>" + (hv == null ? esc(t("kern.k_a")) : esc(I18N.fmt.zahl(hv, 1)) + NB + "m") + "</td></tr></table>" +
      (HQ_TEXT[p.hq] ? "<div class='pop-q'>" + esc(t(HQ_TEXT[p.hq])) + "</div>" : "") +
      (TYP_TEXT[p.typ] ? "<div class='pop-q'>" + esc(t(TYP_TEXT[p.typ])) + "; " + esc(t("sanierung.schaetzung")) + "</div>" : "") +
      "<div class='pop-q'>" + esc(t("sanierung.pop_quelle", { stand: KS.datum(SL.stand) })) + "</div>";
  } else if (f.length) {
    var DO = window.KIEZ_DENKMALE_ODBL, dzOk = KS.geprueft(DO);
    h = "<b>" + esc(dzOk ? t("sanierung.leg_dz_probe") : t("sanierung.leg_dz")) + "</b><div class='pop-q'>" + esc(dzOk ? t("sanierung.pop_dz_probe", { punkt: KS.sichtPunkt(DO.sichtpruefung.ergebnis) }) : t("sanierung.pop_dz")) + "</div>";
  } else {
    if (drei && drei.an() && map.getLayer("geb3d") && map.queryRenderedFeatures(e.point, { layers: ["geb3d"] }).length) return;
    var r = map.queryRenderedFeatures(e.point, { layers: ["teile-flaeche"] });
    if (r.length) stWaehlen(r[0].properties.nr === S.st ? "" : r[0].properties.nr, false);
  }
  if (h) new maplibregl.Popup({ maxWidth: "300px" }).setLngLat(e.lngLat).setHTML(h).addTo(map);
});
map.on("moveend", hash);

function fertig() { if (bereit && laeuft === 0) KS.bereitNach(map, function () { return laeuft + (drei ? drei.laufend() : 0); }); }
bauen(); stInfo(); legende();
map.on("load", function () {
  bereit = true;
  drei = KS.drei(map, { knopf: k3, legende: legende, geaendert: hash, bereit: fertig, meldung: function () { legende(); },
    ziel: function () { return OM && OM.geometry ? OM.geometry.coordinates : window.KIEZ_ORT.karte.haus_ziel; },
    klickVorrang: function (e) { return map.queryRenderedFeatures([[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]], { layers: ["zbk", "om-ring"] }).length > 0; } });
  wahl(S.st); anwenden(); denkmale();
  if (S.d3) drei.setzen(true, false);
});
})();
