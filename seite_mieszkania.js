/* Kiezatlas: Seite Wohnungsmarkt (mieszkania). Daten: daten/mieszkania_odbl.js (Median des Preises je m² Wohnfläche je
   dzielnica, Jahr und Markt aus dem Rejestr cen nieruchomości, nur ab der Mindestfallzahl; keine Einzelkäufe, keine
   Extremwerte). Die Zuordnung zur dzielnica beruht auf den OSM-Grenzen; der ODbL-Vermerk steht deshalb in den
   Quellen der Seite. Solange die Datei Beispieldaten trägt, steht oben die fehlende Quelle. Fallzahlen unter der
   Mindestzahl stehen nicht in der Datei; die Seite zeigt dort „n < Mindestzahl“. Interne Felder der Datei
   (kontrolle, regeln.kennzahl) werden nicht angezeigt, sie sind für die Prüfung gedacht. */
(function () {
"use strict";
var I18N = window.KIEZ_I18N, TS = window.KIEZ_TS, el = TS.el, M = window.KIEZ_MIESZKANIA;
if (!I18N || !TS || !M) return;
function $(id) { return document.getElementById(id); }
var BEISPIEL = M.fixture === true, MIN = TS.zahl(M.regeln.mindestfallzahl);
var RYNEK = { ogolem: I18N.t("mieszkania.rynek.ogolem"), pierwotny: I18N.t("mieszkania.rynek.pierwotny"), wtorny: I18N.t("mieszkania.rynek.wtorny") };
var GRUND = {
  n_unter_minimum: function () { return I18N.t("mieszkania.grund.n_unter_minimum", { min: MIN }); },
  keine_transaktionen: function () { return I18N.t("mieszkania.grund.keine_transaktionen"); }
};
var EINHEIT = I18N.t("mieszkania.einheit");
function preis(v) { return v == null ? I18N.t("kern.k_a") : TS.zahl(v) + " " + EINHEIT; }
function anzahl(v) {
  if (v.grund === "n_unter_minimum") return I18N.t("mieszkania.n_unter_min", { min: MIN });
  return v.n == null ? I18N.t("kern.k_a") : I18N.t("mieszkania.n_transakcji", { n: v.n });
}
// Fallzahl in Tabellen: unter der Mindestzahl nie die Zahl, sondern „n < Mindestzahl“
function fallzahl(v) {
  if (v.grund === "n_unter_minimum") return I18N.t("mieszkania.n_unter_min", { min: MIN });
  return v.n == null ? I18N.t("kern.k_a") : TS.zahl(v.n);
}
var TEILW = M.eingabe && M.eingabe.jahr_teilweise, STAND = M.eingabe && M.eingabe.datenstand;
// Start mit dem jüngsten vollständigen Jahr (das laufende Jahr ist unvollständig und bleibt wählbar). Die Datei
// enthält nur Jahre ab regeln.erstes_jahr (pruefen/DW_protokoll.md); alle werden gezeigt, ein Jahr ohne Median zeigt den Grund
var JAHRE = M.jahre, VOLL = JAHRE.filter(function (j) { return j !== TEILW; }), JAHR = VOLL.length ? VOLL[VOLL.length - 1] : JAHRE[JAHRE.length - 1], MARKT = M.maerkte[0];
function jahrText(j) { return String(j) + (j === TEILW ? " (" + I18N.t("mieszkania.jahr_teilweise", { datum: TS.datum(STAND) }) + ")" : ""); }

// ---------- Beispieldaten: fehlende Quelle sichtbar
if (BEISPIEL) {
  TS.beispiel($("m-beispiel"), { titel: I18N.t("mieszkania.beispiel.titel"), marke: I18N.t("mieszkania.beispiel.marke"),
    saetze: [I18N.t("mieszkania.beispieldaten"), I18N.t("mieszkania.beispiel.brak"), I18N.t("mieszkania.beispiel.prawdziwe", { min: MIN })] });
}
$("m-datenschutz").textContent = I18N.t("mieszkania.hinweis_datenschutz", { min: MIN });

// ---------- Auswahl Jahr und Markt; Stadtwert und Tabelle der dzielnice
function zeichnen() {
  var s = (M.stadt[JAHR] || {})[MARKT] || {};
  var ul = TS.leeren($("m-stadt"));
  ul.appendChild(el("li", {}, [el("b", { text: preis(s.median) }), el("span", { text: I18N.t("mieszkania.legende_titel") + ", " + RYNEK[MARKT] + ", " + jahrText(JAHR) })]));
  ul.appendChild(el("li", {}, [el("b", { text: anzahl(s) }), el("span", { text: I18N.t("mieszkania.tab.n_opis") })]));
  var mx = 0;
  TS.teile().forEach(function (t) { var v = ((M.stadtteile[t.nr] || {})[JAHR] || {})[MARKT]; if (v && v.median > mx) mx = v.median; });
  var zeilen = TS.teile().map(function (t) {
    var v = ((M.stadtteile[t.nr] || {})[JAHR] || {})[MARKT] || {};
    var med = v.median != null ? TS.balken(preis(v.median), mx ? v.median / mx : 0)
      : el("span", { class: "ts-leer", text: GRUND[v.grund] ? GRUND[v.grund]() : I18N.t("kern.k_a") });
    return { zellen: [TS.teilName(t.nr), med, fallzahl(v)] };
  });
  zeilen.push({ klasse: "ts-summe", zellen: [I18N.ort("ganze_stadt"), preis(s.median), fallzahl(s)] });
  TS.leeren($("m-dzielnice")).appendChild(TS.tabelle({
    titel: I18N.t("mieszkania.tab.titel", { rynek: RYNEK[MARKT], rok: jahrText(JAHR) }),
    spalten: [{ text: I18N.t("mieszkania.tab.dzielnica") }, { text: I18N.t("mieszkania.tab.mediana"), zahl: true }, { text: I18N.t("mieszkania.tab.n"), zahl: true }],
    zeilen: zeilen
  }));
}
TS.knoepfe($("m-rok"), I18N.t("mieszkania.wybor.rok"), JAHRE.map(function (j) { return { wert: j, text: String(j) }; }), JAHR,
  function (w) { JAHR = w; zeichnen(); });
TS.knoepfe($("m-rynek"), I18N.t("mieszkania.wybor.rynek"), M.maerkte.map(function (m) { return { wert: m, text: RYNEK[m] }; }), MARKT,
  function (w) { MARKT = w; zeichnen(); });
zeichnen();

// ---------- Stadt über die Jahre: Linien je Markt und dieselben Werte als Tabelle
TS.linien({
  rahmen: $("m-wykres"), jahre: JAHRE,
  reihen: M.maerkte.map(function (m) {
    var w = {}; JAHRE.forEach(function (j) { var v = (M.stadt[j] || {})[m]; if (v) w[j] = { w: v.median, offen: j === TEILW }; });
    return { name: RYNEK[m], werte: w, klasse: "ts-m-" + m, hervor: m === "ogolem" };
  }),
  beschreibung: I18N.t("mieszkania.wykres.opis", { od: JAHRE[0], do: JAHRE[JAHRE.length - 1] }),
  format: function (v) { return TS.zahl(v); }
});
$("m-wykres").querySelector("figcaption").textContent = I18N.t("mieszkania.legende_titel") + " (" + EINHEIT + "). "
  + (BEISPIEL ? I18N.t("mieszkania.beispiel.podpis") : I18N.t("mieszkania.zrodlo_kurz"));
$("m-legende").appendChild(TS.legende(M.maerkte.map(function (m) { return { text: RYNEK[m], klasse: "ts-m-" + m }; })
  .concat(TEILW ? [{ text: I18N.t("mieszkania.jahr_teilweise", { datum: TS.datum(STAND) }), klasse: "ts-offen" }] : [])));
$("m-jahre").appendChild(TS.tabelle({
  titel: I18N.t("mieszkania.h.przebieg"),
  spalten: [{ text: I18N.t("mieszkania.tab.rok") }].concat([].concat.apply([], M.maerkte.map(function (m) {
    return [{ text: RYNEK[m] + ": " + I18N.t("mieszkania.tab.mediana"), zahl: true }, { text: RYNEK[m] + ": " + I18N.t("mieszkania.tab.n"), zahl: true }];
  }))),
  zeilen: JAHRE.map(function (j) {
    return { zellen: [jahrText(j)].concat([].concat.apply([], M.maerkte.map(function (m) {
      var v = (M.stadt[j] || {})[m] || {}; return [preis(v.median), fallzahl(v)];
    }))) };
  })
}));

// ---------- Grenzen mit Werten aus den Daten
var gr = $("m-grenzen");
[I18N.t("mieszkania.g.prawo", { min: MIN }),
 I18N.t("mieszkania.g.od_roku", { od: M.regeln.erstes_jahr }),
 BEISPIEL ? null : I18N.t("mieszkania.g.zeitreihe"),
 BEISPIEL ? null : I18N.t("mieszkania.g.lage"),
 TEILW ? I18N.t("mieszkania.g.rok_niepelny", { rok: TEILW, datum: TS.datum(STAND) }) : null
].forEach(function (s) { if (s) gr.appendChild(el("li", { text: s })); });

// ---------- Quellen (Vermerk wörtlich, Polnisch)
var Q = M.quelle;
TS.quellen($("m-quellen"), [
  { titel: I18N.t("mieszkania.zrodlo.rcn"), hinweis: BEISPIEL ? I18N.t("mieszkania.zrodlo.docelowe") : null, zeilen: [
    I18N.t("mieszkania.begriff_rcn"),
    { vor: I18N.t("mieszkania.zrodlo.vermerk"), text: Q.vermerk, lang: "pl" },
    { vor: I18N.t("mieszkania.zrodlo.podstawa"), text: Q.rechtsgrundlage, lang: "pl" },
    { link: Q.url, text: I18N.t("mieszkania.zrodlo.strona") },
    BEISPIEL ? null : I18N.t("mieszkania.zrodlo.stan", { datum: TS.datum(STAND) })
  ] },
  { titel: I18N.t("mieszkania.zrodlo.granice"), zeilen: [I18N.t("kern.odbl").replace(/:\s*$/, ""),
    { link: "https://www.openstreetmap.org/copyright", text: "openstreetmap.org/copyright" }] }
]);
if (window.KIEZ_BEISPIEL_PRUEFEN) window.KIEZ_BEISPIEL_PRUEFEN();
})();
