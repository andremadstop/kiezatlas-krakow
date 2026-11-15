/* Kiezatlas: Vergleich Kraków–Potsdam (porownanie.html). Nur Kennzahlen gleicher Definition aus daten/porownanie.js
   (derselbe Datensatz, dieselbe Zellgröße, dieselbe Zuordnungsregel); was nicht vergleichbar ist, nennt die Seite mit
   Grund. Zahlen nur aus den Daten, hier steht keine Ergebniszahl von Hand. */
(function () {
"use strict";
var V = window.KIEZ_POROWNANIE, I18N = window.KIEZ_I18N;
var tab = document.getElementById("ka-vergleich");
if (!V || !I18N || !tab) return;
var tt = I18N.t, fmt = I18N.fmt.nf(), fmt1 = I18N.fmt.nf({ minimumFractionDigits: 1, maximumFractionDigits: 1 });
var fmt2 = I18N.fmt.nf({ minimumFractionDigits: 2, maximumFractionDigits: 2 }), NB = " ";
// Prozentzeichen nach Landesbrauch wie fmt.anteil (pl, en ohne Leerzeichen, de mit geschütztem)
var PZ = I18N.fmt.anteil(1, 0).replace(/^[0-9]+/, "");
var KR = V.staedte.krakow, PD = V.staedte.potsdam;
function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
function proz(v) { return v == null ? tt("kern.k_a") : fmt1.format(v) + PZ; }
// Abweichung mit Vorzeichen, Minus als U+2212
function abw(d) { return (d > 0 ? "+" : d < 0 ? "\u2212" : "") + fmt.format(Math.abs(d)); }
function pp(a, b) { return a == null || b == null ? tt("kern.k_a") : tt("erzaehlung.vg_pp", { wert: (a - b > 0 ? "+" : a - b < 0 ? "\u2212" : "") + fmt1.format(Math.abs(a - b)) }); }
function faktor(a, b) { return a == null || !b ? tt("kern.k_a") : tt("erzaehlung.vg_faktor", { wert: fmt1.format(a / b) }); }

// Stichtage und Methode im Kopf
document.getElementById("ka-vg-methode").textContent = tt("erzaehlung.vg_methode", {
  kr: I18N.fmt.datum(V.quellen.eurostat_pl.stichtag), pd: I18N.fmt.datum(V.quellen.eurostat_de.stichtag) });

var ZEILEN = [
  { titel: tt("erzaehlung.vg_einwohner"), kr: fmt.format(KR.einwohner), pd: fmt.format(PD.einwohner), d: faktor(KR.einwohner, PD.einwohner),
    zusatz: tt("erzaehlung.vg_zellen", { kr: fmt.format(KR.zellen), pd: fmt.format(PD.zellen) }) },
  { titel: tt("erzaehlung.vg_flaeche"), kr: fmt2.format(KR.flaeche_km2) + NB + "km²", pd: fmt2.format(PD.flaeche_km2) + NB + "km²", d: faktor(KR.flaeche_km2, PD.flaeche_km2),
    zusatz: tt("erzaehlung.vg_flaeche_quelle") },
  { titel: tt("erzaehlung.vg_dichte"), kr: KR.dichte == null ? tt("kern.k_a") : fmt.format(KR.dichte), pd: PD.dichte == null ? tt("kern.k_a") : fmt.format(PD.dichte), d: faktor(KR.dichte, PD.dichte) },
  { titel: tt("erzaehlung.sb_u15"), kr: proz(KR.q_u15), pd: proz(PD.q_u15), d: pp(KR.q_u15, PD.q_u15),
    zusatz: tt("erzaehlung.vg_von", { kr: fmt.format(KR.u15) + " / " + fmt.format(KR.a_ges), pd: fmt.format(PD.u15) + " / " + fmt.format(PD.a_ges) }) +
      (KR.a_ges !== KR.einwohner || PD.a_ges !== PD.einwohner ? " " + tt("erzaehlung.vg_nenner", { kr: abw(KR.a_ges - KR.einwohner), pd: abw(PD.a_ges - PD.einwohner) }) : "") },
  { titel: tt("erzaehlung.vg_15_64"), kr: proz(KR.q_15_64), pd: proz(PD.q_15_64), d: pp(KR.q_15_64, PD.q_15_64),
    zusatz: tt("erzaehlung.vg_von", { kr: fmt.format(KR.a15_64) + " / " + fmt.format(KR.a_ges), pd: fmt.format(PD.a15_64) + " / " + fmt.format(PD.a_ges) }) },
  { titel: tt("erzaehlung.sb_65p"), kr: proz(KR.q_65p), pd: proz(PD.q_65p), d: pp(KR.q_65p, PD.q_65p),
    zusatz: tt("erzaehlung.vg_von", { kr: fmt.format(KR.a65p) + " / " + fmt.format(KR.a_ges), pd: fmt.format(PD.a65p) + " / " + fmt.format(PD.a_ges) }) }
];
var tbody = tab.querySelector("tbody");
ZEILEN.forEach(function (z) {
  var tr = el("tr"), th = el("th", null, z.titel); th.setAttribute("scope", "row");
  if (z.zusatz) th.appendChild(el("span", "ka-quelle ka-block", z.zusatz));
  tr.appendChild(th); tr.appendChild(el("td", null, z.kr)); tr.appendChild(el("td", null, z.pd)); tr.appendChild(el("td", null, z.d));
  tbody.appendChild(tr);
});

// Altersaufbau als gestapelte Balken (drei Gruppen, Anteile aus den Daten)
var balken = document.getElementById("ka-vg-alter");
[[tt("erzaehlung.vg_krakow"), KR], [tt("erzaehlung.vg_potsdam"), PD]].forEach(function (p) {
  var zeile = el("div", "ka-vg-zeile"), name = el("span", "ka-vg-name", p[0]), b = el("div", "ka-vg-balken");
  b.setAttribute("role", "img");
  b.setAttribute("aria-label", tt("erzaehlung.vg_alter_aria", { stadt: p[0], u15: proz(p[1].q_u15), m: proz(p[1].q_15_64), a: proz(p[1].q_65p) }));
  // Werte nicht im Balken (schmale Segmente schnitten „14,0 %“ zu „4,0 %“ ab), sondern vollständig darunter
  var werte = el("p", "ka-vg-werte");
  werte.setAttribute("aria-hidden", "true");
  [["q_u15", "ka-vg-u15", "erzaehlung.vg_leg_u15"], ["q_15_64", "ka-vg-m", "erzaehlung.vg_leg_m"], ["q_65p", "ka-vg-a", "erzaehlung.vg_leg_a"]].forEach(function (g) {
    var v = p[1][g[0]], s = el("span", g[1]); s.style.width = (v || 0) + "%"; b.appendChild(s);
    var w = el("span", null, tt(g[2]) + ": "); w.appendChild(el("b", null, proz(v))); werte.appendChild(w);
  });
  zeile.appendChild(name); zeile.appendChild(b); zeile.appendChild(werte); balken.appendChild(zeile);
});
document.getElementById("ka-vg-quelle").textContent = tt("erzaehlung.vg_quelle", { vermerk: V.quellen.eurostat_de.vermerk });
})();
