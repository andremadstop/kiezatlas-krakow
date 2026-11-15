/* Kiezatlas: Seite Luft (powietrze). Daten: daten/powietrze.js (Jahreskennwerte der Messstationen nach der
   EEA-Jahresstatistik, Grenzwerte, Wortlaut der Uchwała zum Verbot fester Brennstoffe). Vorher/Nachher ist ein
   Vergleich zweier Zeitfenster um einen belegten Stichtag, keine Ursache. Solange die Datei Beispieldaten
   trägt (fixture), steht oben die fehlende Quelle, und jede Abbildung ist als Beispiel markiert; eine Karte der
   Stationen gibt es dann bewusst nicht (erfundene Orte auf echter Karte sähen echt aus). */
(function () {
"use strict";
var I18N = window.KIEZ_I18N, TS = window.KIEZ_TS, el = TS.el, P = window.KIEZ_POWIETRZE;
if (!I18N || !TS || !P) return;
function $(id) { return document.getElementById(id); }
var BEISPIEL = P.fixture === true, R = P.reguly || {};

// Begriffe aus den Daten über feste Tabellen (jeder Schlüssel steht wörtlich hier)
function prog(k) { var g = (P.grenzwerte[k] || [])[0]; return g ? TS.zahl(g.wartosc) : I18N.t("kern.k_a"); }
var KENNWERT = {
  pm10_srednia: I18N.t("powietrze.kennwert.pm10_srednia"),
  pm10_dni: I18N.t("powietrze.kennwert.pm10_dni", { prog: prog("pm10_dni") }),
  pm25_srednia: I18N.t("powietrze.kennwert.pm25_srednia"),
  no2_srednia: I18N.t("powietrze.kennwert.no2_srednia"),
  no2_godziny: I18N.t("powietrze.kennwert.no2_godziny", { prog: prog("no2_godziny") })
};
var ROLA = { miasto: I18N.t("powietrze.rola.miasto"), okolica: I18N.t("powietrze.rola.okolica", { km: TS.zahl(R.okolica_km) }) };
var TYP = { traffic: I18N.t("powietrze.typ.traffic"), background: I18N.t("powietrze.typ.background"), industrial: I18N.t("powietrze.typ.industrial") };
var OBSZAR = { urban: I18N.t("powietrze.obszar.urban"), suburban: I18N.t("powietrze.obszar.suburban"), rural: I18N.t("powietrze.obszar.rural") };
var OKRES = { "rok kalendarzowy": I18N.t("powietrze.okres.rok"), "24 godziny": I18N.t("powietrze.okres.doba"), "jedna godzina": I18N.t("powietrze.okres.godzina") };
var BEZ = { brak_dobowego_poziomu_dopuszczalnego: I18N.t("powietrze.pm25_bez_dni") };
function los(tab, v) { return v == null ? I18N.t("kern.k_a") : (tab[String(v).toLowerCase()] || v); }
// Wert mit Einheit: Konzentration in µg/m³, Häufigkeiten als Tage bzw. Stunden (Plural der Sprache)
function wert(k, w) {
  if (w == null) return I18N.t("kern.k_a");
  var e = (P.kennwerte[k] || {}).jednostka;
  if (e === "dni") return I18N.t("powietrze.jednostka.dni", { n: w });
  if (e === "godziny") return I18N.t("powietrze.jednostka.godziny", { n: w });
  return TS.zahl(w, 1) + " " + I18N.t("powietrze.jednostka.ugm3");
}
var LATA = P.lata, OK = P.okna, PELNE = TS.zahl(R.pokrycie_pelne), MIN = TS.zahl(R.pokrycie_min);
// Umland: fehlt im Export (Filter nach Stadt), sagt das die Seite unter den Grenzen statt einer leeren Legende
var UMLAND = P.stacje.some(function (s) { return s.rola === "okolica"; });
var stacje = P.stacje.slice().sort(function (a, b) { return (a.rola === b.rola ? 0 : a.rola === "miasto" ? -1 : 1) || a.odleglosc_km - b.odleglosc_km; });

// ---------- Beispieldaten: fehlende Quelle sichtbar
if (BEISPIEL) {
  TS.beispiel($("p-beispiel"), { titel: I18N.t("powietrze.beispiel.titel"), marke: I18N.t("powietrze.beispiel.marke"),
    saetze: [I18N.t("powietrze.beispieldaten"), I18N.t("powietrze.beispiel.brak"), I18N.t("powietrze.beispiel.prawdziwe")] });
}

// ---------- Uchwała: Stichtag und Wortlaut (echt, auch bei Beispieldaten)
var KX = P.kontekst;
$("p-stichtag").textContent = I18N.t("powietrze.stichtag", { data: TS.datum(KX.wejscie_w_zycie) });
var zitat = $("p-zitat");
zitat.appendChild(el("p", { lang: "pl", text: KX.cytat_paliwa }));
zitat.appendChild(el("p", { lang: "pl", text: KX.cytat_wejscie }));
zitat.appendChild(el("footer", {}, [el("span", { lang: "pl", text: KX.akt + "; " + KX.publikacja })]));
if (KX.zmiany_pozniejsze === "nie sprawdzono") $("p-zmiany").textContent = I18N.t("powietrze.zmiany_niesprawdzone");

// ---------- Jahreswerte: Auswahl Kennwert und hervorgehobene Station
var K = Object.keys(KENNWERT).filter(function (k) { return P.kennwerte[k]; })[0], HERVOR = stacje.length ? stacje[0].kod : null;
// Vorauswahl: unter den Stationen mit Wert im letzten Jahr die mit den meisten Jahreswerten (bei Gleichstand die
// erste der Liste: Stadt, nach Entfernung), damit die Seite mit einer langen, aktuellen Reihe öffnet
var LETZT = LATA[LATA.length - 1];
function jahreMitWert(s) { var r = s.serie[K] || {}; return Object.keys(r).filter(function (j) { return r[j] && r[j].w != null; }).length; }
var mitWert = stacje.filter(function (s) { var p = (s.serie[K] || {})[LETZT]; return p && p.w != null; })
  .reduce(function (best, s) { return !best || jahreMitWert(s) > jahreMitWert(best) ? s : best; }, null);
if (mitWert) HERVOR = mitWert.kod;
var sel = $("p-stacja");
stacje.forEach(function (s) { sel.appendChild(el("option", { value: s.kod, text: s.nazwa + " (" + ROLA[s.rola] + ")" })); });
if (HERVOR) sel.value = HERVOR;
sel.addEventListener("change", function () { HERVOR = sel.value; zeichnen(); });

var neu;
function zeichnen() {
  var g = P.grenzwerte[K] || [], art = (P.kennwerte[K] || {}).jednostka;
  // Häufigkeits-Kennwerte: die Linie liegt bei der zulässigen Zahl der Tage/Stunden, nicht beim Schwellenwert
  var grenzen = g.map(function (x) {
    var y = art === "µg/m³" ? x.wartosc : x.dopuszczalna_czestosc;
    return { y: y, ab: x.od_roku, text: I18N.t("powietrze.wykres.poziom") + (x.faza ? " (" + I18N.t("powietrze.grenzwert.faza", { faza: x.faza, rok: x.od_roku }) + ")" : "") };
  }).filter(function (x) { return x.y != null; });
  var reihen = stacje.map(function (s) {
    var werte = {};
    Object.keys(s.serie[K] || {}).forEach(function (j) { var p = s.serie[K][j]; werte[j] = { w: p.w, offen: p.niepelne === true }; });
    return { name: s.nazwa, werte: werte, hervor: s.kod === HERVOR, klasse: s.kod === HERVOR ? "ts-hervor" : s.rola === "miasto" ? "ts-stadt" : "" };
  });
  reihen.sort(function (a, b) { return (a.hervor ? 1 : 0) - (b.hervor ? 1 : 0); });   // hervorgehobene zuletzt (oben)
  var fig = $("p-wykres");
  var opt = { rahmen: fig, jahre: LATA, reihen: reihen, grenzen: grenzen, band: { jahr: OK.przejscie },
    fenster: [{ von: OK.przed[0], bis: OK.przed[1], text: I18N.t("powietrze.okno.przed", { od: OK.przed[0], do: OK.przed[1] }) },
              { von: OK.po[0], bis: OK.po[1], text: I18N.t("powietrze.okno.po", { od: OK.po[0], do: OK.po[1] }) }],
    beschreibung: I18N.t("powietrze.wykres.opis", { kennwert: KENNWERT[K], od: LATA[0], do: LATA[LATA.length - 1] }),
    format: function (v) { return TS.zahl(v); } };
  neu = TS.linien(opt);
  fig.querySelector("figcaption").textContent = KENNWERT[K] + ". " + (BEISPIEL ? I18N.t("powietrze.beispiel.podpis") : I18N.t("powietrze.zrodlo_kurz"));
  var leg = TS.leeren($("p-legende"));
  leg.appendChild(TS.legende([
    { text: (stacje.filter(function (s) { return s.kod === HERVOR; })[0] || {}).nazwa || "", klasse: "ts-hervor" },
    { text: I18N.t("powietrze.wykres.miasto"), klasse: "ts-stadt" },
    UMLAND ? { text: I18N.t("powietrze.wykres.okolica"), klasse: "" } : null,
    { text: I18N.t("powietrze.wykres.poziom"), klasse: "ts-grenze" },
    { text: I18N.t("powietrze.wykres.okna"), klasse: "ts-fenster" },
    { text: I18N.t("powietrze.okno.przejscie", { rok: OK.przejscie }), klasse: "ts-band" },
    { text: I18N.t("powietrze.wykres.niepelne", { pelne: PELNE }), klasse: "ts-offen" }
  ].filter(Boolean)));
  var bez = Object.keys(P.bez_wartosci || {}).filter(function (k) { return k.indexOf(K.split("_")[0]) === 0; })
    .map(function (k) { return BEZ[P.bez_wartosci[k]]; }).filter(Boolean);
  $("p-bez").textContent = bez.join(" ");
  // Tabelle der hervorgehobenen Station: dieselben Werte wie die Linie, mit Deckung
  var s = stacje.filter(function (x) { return x.kod === HERVOR; })[0];
  var t = TS.leeren($("p-jahre"));
  // Zeilen ab dem ersten Jahr mit Wert; die Jahre davor nennt der Titel statt leerer Zeilen
  var ab = s ? LATA.filter(function (j) { var p = (s.serie[K] || {})[j]; return p && p.w != null; })[0] : null;
  var jahre = ab != null ? LATA.filter(function (j) { return j >= ab; }) : LATA;
  if (s) t.appendChild(TS.tabelle({
    titel: I18N.t("powietrze.tab.jahre", { stacja: s.nazwa, kennwert: KENNWERT[K] }) + (ab != null && ab > LATA[0] ? " " + I18N.t("powietrze.tab.ab_jahr", { rok: ab, od: LATA[0], bis: ab - 1 }) : ""),
    spalten: [{ text: I18N.t("powietrze.tab.rok") }, { text: I18N.t("powietrze.tab.wartosc"), zahl: true }, { text: I18N.t("powietrze.tab.pokrycie"), zahl: true }],
    zeilen: jahre.map(function (j) {
      var p = (s.serie[K] || {})[j];
      return { zellen: [String(j), p ? wert(K, p.w) : I18N.t("kern.k_a"),
        p && p.pokrycie != null ? I18N.t("powietrze.pokrycie", { proc: TS.zahl(p.pokrycie) }) + (p.niepelne ? " (" + I18N.t("powietrze.tab.niepelne") + ")" : "") : I18N.t("kern.k_a")] };
    })
  }));
  przedPo();
}
TS.knoepfe($("p-wahl"), I18N.t("powietrze.wybor.kennwert"),
  Object.keys(KENNWERT).filter(function (k) { return P.kennwerte[k]; }).map(function (k) { return { wert: k, text: KENNWERT[k] }; }),
  K, function (w) { K = w; zeichnen(); });

// ---------- Vorher/Nachher je Station (Mittel der Fenster, kein Unterschied ausgerechnet: keine Wirkungsaussage)
function przedPo() {
  var box = TS.leeren($("p-przedpo"));
  box.appendChild(TS.tabelle({
    titel: KENNWERT[K],
    spalten: [{ text: I18N.t("powietrze.tab.stacja") }, { text: I18N.t("powietrze.tab.rola") }, { text: I18N.t("powietrze.tab.typ") },
      { text: I18N.t("powietrze.tab.odleglosc"), zahl: true },
      { text: I18N.t("powietrze.okno.przed", { od: OK.przed[0], do: OK.przed[1] }), zahl: true },
      { text: I18N.t("powietrze.okno.po", { od: OK.po[0], do: OK.po[1] }), zahl: true }],
    zeilen: stacje.map(function (s) {
      var v = s.przed_po[K] || {}, brak = v.powod === "brak_pelnego_okna" ? I18N.t("powietrze.brak_pelnego_okna") : I18N.t("kern.k_a");
      return { klasse: s.kod === HERVOR ? "ts-gewaehlt" : null, zellen: [s.nazwa, ROLA[s.rola],
        los(TYP, s.typ) + ", " + los(OBSZAR, s.obszar),
        I18N.t("powietrze.odleglosc", { km: TS.zahl(s.odleglosc_km, 1) }),
        v.przed == null ? el("span", { class: "ts-leer", text: brak }) : wert(K, v.przed),
        v.po == null ? el("span", { class: "ts-leer", text: brak }) : wert(K, v.po)] };
    })
  }));
}
zeichnen();

// ---------- Grenzwerte (Verordnung, echt)
$("p-normy").appendChild(TS.tabelle({
  titel: I18N.t("powietrze.grenzwert.zrodlo"),
  spalten: [{ text: I18N.t("powietrze.tab.wskaznik") }, { text: I18N.t("powietrze.tab.poziom") }, { text: I18N.t("powietrze.tab.podstawa") }],
  zeilen: [].concat.apply([], Object.keys(KENNWERT).map(function (k) {
    return (P.grenzwerte[k] || []).map(function (g) {
      var txt = g.dopuszczalna_czestosc != null
        ? I18N.t("powietrze.grenzwert.czestosc", { wartosc: TS.zahl(g.wartosc), okres: OKRES[g.okres] || g.okres, razy: TS.zahl(g.dopuszczalna_czestosc) })
        : I18N.t("powietrze.grenzwert.srednia", { wartosc: TS.zahl(g.wartosc), rok: g.od_roku }) + (g.faza ? "; " + I18N.t("powietrze.grenzwert.faza", { faza: g.faza, rok: g.od_roku }) : "");
      return { zellen: [KENNWERT[k], txt, el("span", { lang: "pl", text: g.fundstelle })] };
    });
  }))
}));

// ---------- Grenzen mit Werten aus den Daten
var gr = $("p-grenzen");
[
  I18N.t("powietrze.niepelne", { min: MIN, pelne: PELNE }),
  I18N.t("powietrze.g.pominiete", { min: MIN }),
  I18N.t(UMLAND ? "powietrze.g.okolica" : "powietrze.g.okolica_brak", { km: TS.zahl(R.okolica_km) })
].forEach(function (s) { gr.appendChild(el("li", { text: s })); });

// ---------- Quellen
var Q = P.quelle;
TS.quellen($("p-quellen"), [
  { titel: I18N.t("powietrze.zrodlo.pomiary"), hinweis: BEISPIEL ? I18N.t("powietrze.zrodlo.docelowe") : null, zeilen: [
    { text: Q.nazwa, lang: "en" },
    { text: Q.pochodzenie, lang: "pl" },
    I18N.t("powietrze.zrodlo.uznanie"),
    { vor: I18N.t("powietrze.zrodlo.licencja"), text: Q.vermerk, lang: "en" },
    { link: Q.metadane, text: I18N.t("powietrze.zrodlo.metadane") },
    BEISPIEL ? null : I18N.t("powietrze.zrodlo.lata", { od: LATA[0], do: LATA[LATA.length - 1] })
  ] },
  { titel: I18N.t("powietrze.zrodlo.normy"), zeilen: [{ text: I18N.t("powietrze.grenzwert.zrodlo"), lang: "pl" }] },
  { titel: I18N.t("powietrze.zrodlo.uchwala"), zeilen: [
    { text: KX.akt, lang: "pl" }, { text: KX.publikacja, lang: "pl" }, { link: KX.url, text: I18N.t("powietrze.zrodlo.tekst") }
  ] }
]);
if (window.KIEZ_BEISPIEL_PRUEFEN) window.KIEZ_BEISPIEL_PRUEFEN();
})();
