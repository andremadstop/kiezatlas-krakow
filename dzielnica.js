/* Kiezatlas: Steckbrief eines Stadtteils (dzielnica.html, Hash #st=01 … 18). Je Kennzahl Wert, Stadtwert, Rang unter
   allen Stadtteilen und Quelle; fehlende Werte als „brak danych“ mit Grund aus den Texten, nie als 0. Druckbar
   (Druckansicht des Browsers, stadtatlas.css). Alle Zahlen aus daten/*.js; hier steht keine Ergebniszahl von Hand.
   Werte je dzielnica stehen in *_odbl-Dateien (Grenzen aus OpenStreetMap); NSP-Werte gibt es nur je Delegatur. */
(function () {
"use strict";
var KF = window.KIEZ_KARTENFELD, T = window.KIEZ_THEMEN, I18N = window.KIEZ_I18N, ORT = window.KIEZ_ORT;
var box = document.getElementById("ka-steckbrief");
if (!KF || !T || !box) return;
var tt = I18N.t, fmt = T.fmt, fmt1 = T.fmt1, el = KF.el, NB = " ";
// Prozentzeichen nach Landesbrauch wie fmt.anteil (pl, en ohne Leerzeichen, de mit geschütztem)
var PZ = I18N.fmt.anteil(1, 0).replace(/^[0-9]+/, "");
var SB = window.KIEZ_STECKBRIEF, SD = window.KIEZ_STECKBRIEF_DZIELNICE, GK = window.KIEZ_GEB_KENNZAHLEN, GD = window.KIEZ_GEB_DZIELNICE;
var KL = window.KIEZ_KLIMAT, KS = window.KIEZ_KLIMAT_STADTTEILE, SA = window.KIEZ_SANIERUNG;
var TEILE = ORT.gliederung.teile, NRS = TEILE.map(function (t) { return t.nr; });
function teil(nr) { return TEILE.filter(function (t) { return t.nr === nr; })[0]; }
function gruppe(id) { return ORT.gliederung.gruppen.filter(function (g) { return g.id === id; })[0]; }

// ---------- Kennzahlen: je Eintrag Wert je nr, Stadtwert, Format, Quelle
function proz(v) { return v == null ? null : fmt1.format(v); }
var KENN = [
  { gruppe: "bevoelkerung", id: "ew", titel: tt("erzaehlung.sb_ew"), einheit: "",
    wert: function (nr) { var g = SD && SD.stadtteile[nr] && SD.stadtteile[nr].gitter; return g && g.einwohner >= SD.methode.mindestfallzahl ? g.einwohner : null; },
    stadt: function () { return SB.stadt.gitter.einwohner; }, zeigen: function (v) { return tt("kern.rund", { zahl: T.rundEw(v) }); },
    zusatz: function (nr) { var g = SD.stadtteile[nr].gitter; return g && g.einwohner_flaechenanteil != null ? tt("erzaehlung.sb_ew_spanne", { wert: T.rundEw(g.einwohner_flaechenanteil), proz: (g.spanne_proz < 0 ? "\u2212" : "") + fmt1.format(Math.abs(g.spanne_proz)) }) : ""; },
    quelle: function () { return tt("erzaehlung.quelle_gitter"); } },
  { gruppe: "bevoelkerung", id: "dichte", titel: tt("erzaehlung.sb_dichte"), einheit: NB + tt("erzaehlung.einheit_je_km2"),
    wert: function (nr) { var s = SD && SD.stadtteile[nr]; return s && s.gitter && s.gitter.einwohner >= SD.methode.mindestfallzahl ? s.dichte_gitter : null; },
    stadt: function () { return SB.stadt.dichte_gitter; }, zeigen: function (v) { return fmt.format(v); },
    quelle: function () { return tt("erzaehlung.quelle_gitter") + " " + tt("erzaehlung.quelle_flaeche_osm"); } },
  { gruppe: "bevoelkerung", id: "u15", titel: tt("erzaehlung.sb_u15"), einheit: PZ,
    wert: function (nr) { var g = SD && SD.stadtteile[nr] && SD.stadtteile[nr].gitter; return g && g.a_ges >= SD.methode.mindestfallzahl ? g.q_u15 : null; },
    stadt: function () { return SB.stadt.gitter.q_u15; }, zeigen: proz,
    zusatz: function (nr) { var g = SD.stadtteile[nr].gitter; return g ? tt("erzaehlung.sb_von", { zaehler: fmt.format(g.u15), nenner: fmt.format(g.a_ges) }) : ""; },
    quelle: function () { return tt("erzaehlung.quelle_gitter"); } },
  { gruppe: "bevoelkerung", id: "65p", titel: tt("erzaehlung.sb_65p"), einheit: PZ,
    wert: function (nr) { var g = SD && SD.stadtteile[nr] && SD.stadtteile[nr].gitter; return g && g.a_ges >= SD.methode.mindestfallzahl ? g.q_65p : null; },
    stadt: function () { return SB.stadt.gitter.q_65p; }, zeigen: proz,
    zusatz: function (nr) { var g = SD.stadtteile[nr].gitter; return g ? tt("erzaehlung.sb_von", { zaehler: fmt.format(g.a65p), nenner: fmt.format(g.a_ges) }) : ""; },
    quelle: function () { return tt("erzaehlung.quelle_gitter"); } },
  { gruppe: "bevoelkerung", id: "flaeche", titel: tt("erzaehlung.sb_flaeche"), einheit: NB + "km²",
    wert: function (nr) { var s = SD && SD.stadtteile[nr]; return s ? s.flaeche_km2 : null; },
    stadt: function () { return SB.stadt.flaeche_km2; }, zeigen: function (v) { return fmt1.format(v); },
    quelle: function () { return tt("erzaehlung.quelle_flaeche_osm") + " " + tt("erzaehlung.quelle_flaeche_stadt"); } },

  { gruppe: "gebaeude", id: "geb", titel: tt("erzaehlung.sb_geb"), einheit: "",
    wert: function (nr) { var g = GD && GD.stadtteile[nr]; return g ? g.anzahl : null; },
    stadt: function () { return GK.stadt.anzahl; }, zeigen: function (v) { return fmt.format(v); },
    quelle: function () { return GD.quellen.bdot10k.vermerk; } },
  { gruppe: "gebaeude", id: "wohn", titel: tt("erzaehlung.sb_wohn"), einheit: "",
    wert: function (nr) { var g = GD && GD.stadtteile[nr]; return g ? g.wohngebaeude : null; },
    stadt: function () { return GK.stadt.wohngebaeude; }, zeigen: function (v) { return fmt.format(v); },
    zusatz: function (nr) { var g = GD.stadtteile[nr]; return g ? tt("erzaehlung.sb_wohn_mehr", { mehr: fmt.format(g.wohn_art.mehr), ein: fmt.format(g.wohn_art.ein) }) : ""; },
    quelle: function () { return GD.quellen.bdot10k.vermerk; } },
  { gruppe: "gebaeude", id: "geschosse", titel: tt("erzaehlung.sb_geschosse"), einheit: "",
    wert: function (nr) { var g = GD && GD.stadtteile[nr]; return g && g.wohngebaeude >= GD.methode.mindestfallzahl ? g.geschosse_median_wohn : null; },
    stadt: function () { return GK.stadt.geschosse_median_wohn; }, zeigen: function (v) { return fmt1.format(v); },
    quelle: function () { return GD.quellen.bdot10k.vermerk; } },
  { gruppe: "gebaeude", id: "bebauung", titel: tt("erzaehlung.dz_bebauung"), einheit: PZ,
    wert: function (nr) { var g = GD && GD.stadtteile[nr]; return g && g.bebauungsdichte ? g.bebauungsdichte.wert : null; },
    stadt: function () { return GK.stadt.bebauungsdichte.wert; }, zeigen: proz,
    quelle: function () { return GD.quellen.bdot10k.vermerk; } },

  { gruppe: "flaechen", id: "versiegelung", titel: tt("erzaehlung.klima_bebauung_verkehr"), einheit: PZ, abzeichen: true,
    wert: function (nr) { var k = KS && KS.stadtteile[nr]; return k && k.anteil ? k.anteil.bebauung_verkehr : null; },
    stadt: function () { return KL.stadt.anteil.bebauung_verkehr; }, zeigen: proz,
    quelle: function () { return KS.quelle.vermerk; } },
  { gruppe: "flaechen", id: "gruen", titel: tt("erzaehlung.klima_gruen_wald"), einheit: PZ, abzeichen: true,
    wert: function (nr) { var k = KS && KS.stadtteile[nr]; return k && k.anteil ? k.anteil.gruen_wald : null; },
    stadt: function () { return KL.stadt.anteil.gruen_wald; }, zeigen: proz,
    quelle: function () { return KS.quelle.vermerk; } },
  { gruppe: "flaechen", id: "gruen_ew", titel: tt("erzaehlung.sb_gruen_ew"), einheit: NB + "m²", abzeichen: true,
    wert: function (nr) { var k = KS && KS.stadtteile[nr]; return k && k.einwohner >= KS.mindest_einwohner ? k.gruen_je_ew : null; },
    stadt: function () { return KL.stadt.gruen_je_ew; }, zeigen: function (v) { return fmt.format(v); },
    quelle: function () { return KS.quelle.vermerk + " " + tt("erzaehlung.quelle_gitter"); } },

  { gruppe: "zbk", id: "zbk", titel: tt("erzaehlung.dz_zbk"), einheit: "",
    wert: function (nr) { var e = SA && SA.liste.je_dzielnica[nr]; return e ? e.n : null; },
    stadt: function () { return SA.liste.eintraege; }, zeigen: function (v) { return fmt.format(v); },
    zusatz: function (nr) { var e = SA.liste.je_dzielnica[nr]; return e ? tt("erzaehlung.sb_zbk_gmina", { n: fmt.format(e.eigentum.gmina) }) : ""; },
    stadtText: function () { return tt("erzaehlung.sb_zbk_stadt", { n: fmt.format(SA.liste.eintraege), poza: fmt.format(SA.liste.je_dzielnica.poza ? SA.liste.je_dzielnica.poza.n : 0) }); },
    quelle: function () { return SA.quellen.zbk.vermerk; }, klausel: function () { return SA.quellen.zbk.odpowiedzialnosc; } }
];
var GRUPPEN = [
  { id: "bevoelkerung", titel: tt("erzaehlung.sb_gruppe_bevoelkerung") },
  { id: "gebaeude", titel: tt("erzaehlung.sb_gruppe_gebaeude") },
  { id: "flaechen", titel: tt("erzaehlung.sb_gruppe_flaechen") },
  { id: "zbk", titel: tt("erzaehlung.sb_gruppe_zbk") }
];
// Rang unter den Stadtteilen mit Wert (1 = höchster Wert)
function rang(k, nr) {
  var w = k.wert(nr); if (w == null) return null;
  var alle = NRS.map(function (n) { return k.wert(n); }).filter(function (v) { return v != null; });
  return { r: 1 + alle.filter(function (v) { return v > w; }).length, n: alle.length };
}

// ---------- Karte: gewählter Stadtteil, seine Zellen nach Einwohnern
var map = KF.bauen(document.getElementById("karte"), { druck: true });
function karte(nr) {
  if (!map.loaded()) { map.once("load", function () { karte(nr); }); return; }
  KF.auswahl(map, nr);
  map.setPaintProperty("teile-flaeche", "fill-opacity", ["case", ["==", ["get", "nr"], nr], 0.05, 0.35]);
  map.setPaintProperty("teile-flaeche", "fill-color", ["case", ["==", ["get", "nr"], nr], "#ffffff", "#e6e9e4"]);
  if (window.KIEZ_ZELLEN) {
    KF.zellThema(map, "ew"); map.setFilter("zellen-flaeche", ["==", ["get", "st"], nr]);
    // Legende der Zellfarben: dieselben Klassen wie die Färbung (themen.js, Quintile über alle Zellen der Stadt)
    var leg = document.getElementById("ka-sb-legende");
    if (leg) { KF.legende(leg, tt("erzaehlung.pop_ew_gitter"), T.klassen(T.THEMA.ew).grenzen, { quelle: tt("erzaehlung.quelle_gitter") }); leg.hidden = false; }
  }
  KF.zeige(map, KF.teilRahmen(nr), 28);
}

// ---------- Steckbrief zeichnen
var wahl = document.getElementById("ka-teil");
TEILE.forEach(function (t) { var o = el("option", null, I18N.sprachwert(t.anzeige)); o.value = t.nr; wahl.appendChild(o); });
function zeichnen(nr) {
  var t = teil(nr); if (!t) return;
  wahl.value = nr;
  var g = gruppe(t.gruppe);
  document.getElementById("ka-sb-ziffer").textContent = t.roemisch;
  document.getElementById("ka-sb-name").textContent = t.name;
  document.getElementById("ka-sb-gruppe").textContent = tt("erzaehlung.sb_gruppe_von", { einheit: I18N.sprachwert(ORT.gliederung.gruppe), name: g ? g.name : "" });
  var liste = document.getElementById("ka-sb-werte"); liste.textContent = "";
  GRUPPEN.forEach(function (gr) {
    liste.appendChild(el("h3", "ka-gruppe-titel", gr.titel));
    var feld = el("div", "ka-werte");
    KENN.filter(function (k) { return k.gruppe === gr.id; }).forEach(function (k) {
      var w = k.wert(nr), s = k.stadt(), r = rang(k, nr), c = el("div", "ka-wert");
      c.appendChild(el("h4", null, k.titel));
      var z = el("span", "ka-zahl");
      if (w == null) z.textContent = tt("kern.k_a");
      else { z.textContent = k.zeigen(w); if (k.einheit) z.appendChild(el("small", null, k.einheit.trim())); }
      c.appendChild(z);
      if (w != null && k.zusatz) { var zu = k.zusatz(nr); if (zu) c.appendChild(el("p", "ka-vergleich", zu)); }
      if (w == null) c.appendChild(el("p", "ka-vergleich", tt("erzaehlung.sb_kein_wert")));
      c.appendChild(el("p", "ka-vergleich", k.stadtText ? k.stadtText() : tt("erzaehlung.sb_stadt", { stadt: I18N.ort("stadt"), wert: s == null ? tt("kern.k_a") : k.zeigen(s) + k.einheit })));
      if (r) {
        var leiste = el("span", "ka-rang"); leiste.setAttribute("aria-hidden", "true");
        for (var i = 1; i <= r.n; i++) { var b = el("i"); if (i === r.r) b.className = "ist"; leiste.appendChild(b); }
        c.appendChild(leiste);
        c.appendChild(el("p", "ka-vergleich", tt("erzaehlung.sb_rang", { r: fmt.format(r.r), n: fmt.format(r.n) })));
      }
      if (k.abzeichen) c.appendChild(el("p", "fl-abzeichen", tt("erzaehlung.abzeichen_orientierung")));
      c.appendChild(el("p", "ka-quelle", k.quelle()));
      if (k.klausel && k.klausel()) { var kl = el("p", "ka-quelle", k.klausel()); kl.lang = "pl"; c.appendChild(kl); }
      feld.appendChild(c);
    });
    liste.appendChild(feld);
  });
  // NSP 2021: nur je Delegatur (historischer Stadtbezirk); je dzielnica fehlt die Geometrie der rejony statystyczne
  var nsp = document.getElementById("ka-sb-nsp"); nsp.textContent = "";
  var gd = SB && SB.gruppen[t.gruppe];
  nsp.appendChild(el("h3", "ka-gruppe-titel", tt("erzaehlung.sb_gruppe_nsp")));
  nsp.appendChild(el("p", null, tt("erzaehlung.sb_nsp_fehlt")));
  if (gd && gd.nsp) {
    var tab = el("div", "ka-werte");
    [[tt("erzaehlung.sb_nsp_ew"), fmt.format(gd.nsp.einwohner), ""],
     [tt("erzaehlung.sb_nsp_u20"), fmt1.format(gd.nsp.q_u20), PZ],
     [tt("erzaehlung.sb_nsp_60p"), fmt1.format(gd.nsp.q_60p), PZ],
     [tt("erzaehlung.sb_nsp_nach"), fmt1.format(gd.nsp.q_nach), PZ]].forEach(function (z) {
      var c = el("div", "ka-wert"); c.appendChild(el("h4", null, z[0]));
      var n = el("span", "ka-zahl", z[1]); if (z[2]) n.appendChild(el("small", null, z[2].trim())); c.appendChild(n);
      c.appendChild(el("p", "ka-vergleich", tt("erzaehlung.sb_nsp_fuer", { name: gd.name }))); tab.appendChild(c);
    });
    nsp.appendChild(tab);
    nsp.appendChild(el("p", "ka-quelle", SB.quellen.nsp2021.vermerk));
    nsp.appendChild(el("p", "ka-quelle", tt("erzaehlung.sb_nsp_stichtag", { datum: I18N.fmt.datum(SB.quellen.nsp2021.stichtag) })));
  }
  document.title = I18N.sprachwert(t.anzeige) + " · " + I18N.ort("name");
  karte(nr);
}
function ausHash() { var m = /(?:^|[#&])st=([0-9]{2})(?:&|$)/.exec(location.hash); return m && teil(m[1]) ? m[1] : null; }
wahl.addEventListener("change", function () { history.replaceState(null, "", "#st=" + wahl.value); zeichnen(wahl.value); });
addEventListener("hashchange", function () { var nr = ausHash(); if (nr) zeichnen(nr); });
document.getElementById("ka-drucken").addEventListener("click", function () { window.print(); });
zeichnen(ausHash() || NRS[0]);
})();
