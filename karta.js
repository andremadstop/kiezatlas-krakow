/* Kiezatlas: freie Karte (karta.html). Alle Ebenen des Atlas zum Wählen, je Ebene Legende und Quelle;
   Klick auf ein Objekt zeigt Wert und Quelle. Ebenen außer Stadtteilen und Gitter werden erst beim Einschalten
   nachgeladen (per <script>, auch über file://). Beispieldaten (Feld fixture) sind in Legende und Popup
   gekennzeichnet; der Hinweis oben auf der Seite erscheint, sobald eine solche Datei geladen ist.
   Hash (teilbar, Schlüssel deutsch): thema (Zellebene), st (Stadtteil-nr), k (Kamera z/Breite/Länge/0/0),
   dz (Färbung der Stadtteile), pkt (Punktebenen, durch Komma getrennt). Der Hash wird nur nach einer Handlung
   geschrieben, nie beim Laden. Keine Ergebniszahl von Hand; Klassengrenzen sind Methode. */
(function () {
"use strict";
var KF = window.KIEZ_KARTENFELD, T = window.KIEZ_THEMEN, I18N = window.KIEZ_I18N, ORT = window.KIEZ_ORT;
var feld = document.getElementById("karte");
if (!KF || !feld || !window.maplibregl) return;
var tt = I18N.t, fmt = T.fmt, fmt1 = T.fmt1, esc = T.esc, el = KF.el, NB = " ";
// Prozentzeichen nach Landesbrauch wie fmt.anteil (pl, en ohne Leerzeichen, de mit geschütztem)
var PZ = I18N.fmt.anteil(1, 0).replace(/^[0-9]+/, "");
var K = window.KIEZ_KENNZAHLEN;
var map = KF.bauen(feld);

// ---------- Zustand aus dem Hash
function hashLesen() {
  var o = {};
  location.hash.replace(/^#/, "").split("&").forEach(function (p) { var i = p.indexOf("="); if (i > 0) o[p.slice(0, i)] = decodeURIComponent(p.slice(i + 1)); });
  return o;
}
var Z0 = hashLesen();
var zustand = { thema: Z0.thema || "", st: T.TEIL[Z0.st] ? Z0.st : "", dz: Z0.dz || "gruppen", pkt: (Z0.pkt || "").split(",").filter(Boolean), k: Z0.k || "" };
function hashSchreiben() {
  var c = map.getCenter(), teile = [];
  if (zustand.thema) teile.push("thema=" + zustand.thema);
  if (zustand.st) teile.push("st=" + zustand.st);
  if (zustand.dz && zustand.dz !== "gruppen") teile.push("dz=" + zustand.dz);
  if (zustand.pkt.length) teile.push("pkt=" + zustand.pkt.join(","));
  teile.push("k=" + map.getZoom().toFixed(1) + "/" + c.lat.toFixed(4) + "/" + c.lng.toFixed(4) + "/0/0");
  history.replaceState(null, "", "#" + teile.join("&"));
}

// ---------- Zellebenen (eine zur Zeit): Gitter-Themen, Fußweg zur nächsten Einrichtung, Flächennutzung
var FUSS = ["haltestelle_takt", "szkola", "przedszkole", "park", "supermarkt", "apotheke"];
var FUSS_TEXT = {
  haltestelle_takt: tt("erzaehlung.ziel_haltestelle_takt"), szkola: tt("erzaehlung.ziel_szkola"), przedszkole: tt("erzaehlung.ziel_przedszkole"),
  park: tt("erzaehlung.ziel_park"), supermarkt: tt("erzaehlung.ziel_supermarkt"), apotheke: tt("erzaehlung.ziel_apotheke")
};
var FUSS_GRENZEN = [500, 1000, 1500, 2500];               // Meter, Methode (Legende nennt sie)
var PROZ_GRENZEN = [20, 40, 60, 80];                      // Prozent, wie die Zellthemen (themen.js)
var KLIMA = { bebauung_verkehr: tt("erzaehlung.klima_bebauung_verkehr"), gruen_wald: tt("erzaehlung.klima_gruen_wald") };
var legZelle = document.getElementById("ka-leg-zelle"), legTeile = document.getElementById("ka-leg-teile"), legPunkte = document.getElementById("ka-leg-punkte");

function themaTeile(t) { var p = t.split(":"); return { art: p.length > 1 ? p[0] : "gitter", id: p.length > 1 ? p[1] : t }; }
function gitterQuelle() { return tt("erzaehlung.quelle_gitter"); }
function zellebene(t) {
  ["zellen-flaeche", "klimat-flaeche"].forEach(function (id) { if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", "none"); });
  legZelle.textContent = ""; legZelle.hidden = true;
  if (!t) return;
  var x = themaTeile(t);
  if (x.art === "gitter") {
    var th = T.THEMA[T.HASH[x.id] || x.id]; if (!th || th.id === "stadtteile") return;
    KF.zellThema(map, th.id);
    var k = T.klassen(th);
    KF.legende(legZelle, th.name, k.grenzen, { einheit: th.einheit === "%" ? PZ : "", grau: th.nenner ? tt("erzaehlung.leg_grau_gitter", { n: fmt.format(th.mindest || 10) }) : null, quelle: gitterQuelle() });
    legZelle.hidden = false;
  } else if (x.art === "fuss") {
    KF.laden("daten/erreichbar_fuss_odbl.js", "KIEZ_ERREICHBAR_FUSS", function (d) {
      var liste = T.ebenen.zellwerte("erreichbar_fuss", x.id);
      if (!liste) return;
      KF.zellWerte(map, liste, FUSS_GRENZEN);
      KF.legende(legZelle, tt("erzaehlung.leg_fuss", { ziel: FUSS_TEXT[x.id] || x.id }), FUSS_GRENZEN, { einheit: NB + "m", grau: tt("erzaehlung.leg_grau_fuss"), quelle: tt("erzaehlung.quelle_fuss") });
      legZelle.hidden = false;
    });
  } else if (x.art === "klima") {
    KF.laden("daten/klimat_zellen.js", "KIEZ_KLIMAT_ZELLEN", function (d) {
      if (!d) return;
      if (!map.getSource("klimat")) {
        // Anteile flach in die Eigenschaften (MapLibre liest keine verschachtelten Objekte in Ausdrücken)
        var fc = { type: "FeatureCollection", features: d.features.map(function (f) {
          var a = f.properties.anteil || {};
          return { type: "Feature", geometry: f.geometry, properties: { id: f.properties.id, bebauung_verkehr: a.bebauung_verkehr == null ? null : a.bebauung_verkehr,
            gruen_wald: a.gruen_wald == null ? null : a.gruen_wald, flaeche: f.properties.flaeche_stadt_ha } };
        }) };
        map.addSource("klimat", { type: "geojson", data: fc, attribution: d.quelle.vermerk });
        map.addLayer({ id: "klimat-flaeche", type: "fill", source: "klimat", paint: { "fill-opacity": 0.72, "fill-outline-color": "rgba(255,255,255,.55)" } }, "teile-flaeche");
      }
      map.setPaintProperty("klimat-flaeche", "fill-color", KF.stufen(["get", x.id], PROZ_GRENZEN));
      map.setLayoutProperty("klimat-flaeche", "visibility", "visible");
      KF.legende(legZelle, KLIMA[x.id], PROZ_GRENZEN, { einheit: PZ, grau: tt("erzaehlung.leg_grau_klima"), quelle: d.quelle.vermerk });
      legZelle.appendChild(el("p", "fl-abzeichen", tt("erzaehlung.abzeichen_orientierung")));
      legZelle.hidden = false;
    });
  }
}
// Fußwege in Zellreihenfolge: Register von themen.js (prüft Anzahl, erste und letzte Zelle gegen zellen_odbl.js)
T.ebenen.registrieren({ id: "erreichbar_fuss", global: "KIEZ_ERREICHBAR_FUSS" });

// ---------- Färbung der Stadtteile
var dzBox = document.getElementById("ka-dz");
function teilfaerbung(art) {
  if (art === "gruppen" || !art) { KF.teilWerte(map, null); KF.legendeGruppen(legTeile); return; }
  if (art === "bebauung") {
    KF.laden("daten/gebaeude_dzielnice_odbl.js", "KIEZ_GEB_DZIELNICE", function (d) {
      if (!d) return;
      var w = {}; Object.keys(d.stadtteile).forEach(function (nr) { var b = d.stadtteile[nr].bebauungsdichte; w[nr] = b ? b.wert : null; });
      var g = KF.quintile(Object.keys(w).map(function (nr) { return w[nr]; }));
      KF.teilWerte(map, w, g);
      KF.legende(legTeile, tt("erzaehlung.dz_bebauung"), g, { einheit: PZ, format: function (x) { return fmt1.format(x); }, quelle: d.quellen.bdot10k.vermerk });
    });
  } else if (art === "zbk") {
    KF.laden("daten/sanierung.js", "KIEZ_SANIERUNG", function (d) {
      if (!d) return;
      var w = {}; Object.keys(T.TEIL).forEach(function (nr) { var e = d.liste.je_dzielnica[nr]; w[nr] = e ? e.n : null; });
      var g = KF.quintile(Object.keys(w).map(function (nr) { return w[nr]; }));
      KF.teilWerte(map, w, g);
      KF.legende(legTeile, tt("erzaehlung.dz_zbk"), g, { quelle: d.quellen.zbk.vermerk });
      legTeile.appendChild(el("p", "fl-hinweis", tt("erzaehlung.zbk_eintraege_hinweis")));
      klausel(legTeile, d.quellen.zbk);
    });
  } else if (art === "versiegelung") {
    KF.laden("daten/klimat_stadtteile_odbl.js", "KIEZ_KLIMAT_STADTTEILE", function (d) {
      if (!d) return;
      var w = {}; Object.keys(d.stadtteile).forEach(function (nr) { var a = d.stadtteile[nr].anteil; w[nr] = a ? a.bebauung_verkehr : null; });
      KF.teilWerte(map, w, PROZ_GRENZEN);
      KF.legende(legTeile, tt("erzaehlung.dz_versiegelung"), PROZ_GRENZEN, { einheit: PZ, quelle: d.quelle.vermerk });
      legTeile.appendChild(el("p", "fl-abzeichen", tt("erzaehlung.abzeichen_orientierung")));
    });
  }
}

// Mit Zellebene bleiben die Stadtteile als Umriss mit leichtem Farbton der Gruppe stehen
function teilDeckkraft() { if (zustand.dz === "gruppen" || !zustand.dz) map.setPaintProperty("teile-flaeche", "fill-opacity", zustand.thema ? 0.08 : 0.28); }

// Bedingungen der Gmina Miejska Kraków zur Weiterverwendung: Zakres odpowiedzialności wörtlich bei jedem ZBK-Wert
function klausel(box, q) {
  if (!q || !q.odpowiedzialnosc) return;
  var p = el("p", "fl-quelle fl-klausel", q.odpowiedzialnosc); p.lang = "pl"; box.appendChild(p);
}

// ---------- Punktebenen (mehrere zugleich)
var PUNKTE = {
  haltestellen: { datei: "daten/haltestellen.js", global: "KIEZ_HALTESTELLEN", farbe: ["match", ["get", "taktklasse"], "I", "#1c4a5b", "II", "#3b7684", "III", "#6fa1a3", "#a8b4b8"],
    fc: function (d) { return d; }, quelle: function (d) { return d.quellen.ztp.vermerk; } },
  einrichtungen: { datei: "daten/einrichtungen.js", global: "KIEZ_EINRICHTUNGEN", farbe: ["match", ["get", "art"], "szkola", "#6a2c82", "przedszkole", "#9b5fb0", "zlobek", "#c49ad3", "szpital", "#13212a", "park", "#4f7d4a", "#888"],
    fc: function (d) { return d; }, quelle: function (d) { return d.quellen.bdot10k.vermerk; } },
  zbk: { datei: "daten/sanierung_odbl.js", global: "KIEZ_SANIERUNG_ODBL", farbe: "#8a3b2e",
    fc: function (d) { return d.punkte; }, quelle: function (d) { return d.quellen.zbk.vermerk; } },
  // Register aus Wikidata (CC0): alle Registerpunkte mit Quelle wd, dieselbe Auswahl wie die Tabelle auf kamienice.js;
  // Beispieldaten (fixture) nie. Getrennt von der OSM-Kennzeichnung (zabytki): andere Lizenz, Herkunft, Prüfstand.
  rejestr: { datei: "daten/denkmale.js", global: "KIEZ_DENKMALE", farbe: "#6a2c82", rand: "#13212a",
    fc: function (d) { return { type: "FeatureCollection", features: d.fixture === true ? [] : d.objekte.features.filter(function (f) { return f.properties.q.indexOf("wd") > -1; }) }; },
    quelle: function (d) { return d.quellen.wd.vermerk || ""; } },
  zabytki: { datei: "daten/denkmale_odbl.js", global: "KIEZ_DENKMALE_ODBL", farbe: "#efe6f3", rand: "#6a2c82",   // wie die OSM-Kennzeichnung im Sanierungsatlas; kein Orange (DESIGN.md)
    // nur Objekte mit Denkmalangabe (heritage, h === true), wie kamienice.js und sanierungsatlas.js; Objekte nur mit start_date fehlen
    fc: function (d) { return { type: "FeatureCollection", features: d.objekte.features.filter(function (f) { return f.properties.h === true; }) }; },
    quelle: function (d) { return d.vermerk; } },
  powietrze: { datei: "daten/powietrze.js", global: "KIEZ_POWIETRZE", farbe: "#c0392b",
    fc: function (d) { return { type: "FeatureCollection", features: d.stacje.map(function (s) {
      return { type: "Feature", geometry: { type: "Point", coordinates: [s.lon, s.lat] }, properties: { kod: s.kod, nazwa: s.nazwa, typ: s.typ, obszar: s.obszar, rola: s.rola,
        pm10_przed: s.przed_po && s.przed_po.pm10_srednia ? s.przed_po.pm10_srednia.przed : null, pm10_po: s.przed_po && s.przed_po.pm10_srednia ? s.przed_po.pm10_srednia.po : null } }; }) }; },
    quelle: function (d) { return d.quelle.vermerk; } }
};
var PUNKT_TEXT = { haltestellen: tt("erzaehlung.pkt_haltestellen"), einrichtungen: tt("erzaehlung.pkt_einrichtungen"), zbk: tt("erzaehlung.pkt_zbk"),
  rejestr: tt("erzaehlung.pkt_rejestr"), zabytki: tt("erzaehlung.pkt_zabytki"), powietrze: tt("erzaehlung.pkt_powietrze") };
var GELADEN = {};
function punktebene(id, an, fertig) {
  var P = PUNKTE[id]; if (!P) return;
  var lid = "pkt-" + id;
  if (!an) { if (map.getLayer(lid)) map.setLayoutProperty(lid, "visibility", "none"); punktLegende(); return; }
  KF.laden(P.datei, P.global, function (d) {
    if (!d) return;
    GELADEN[id] = d;
    if (!map.getSource(lid)) {
      map.addSource(lid, { type: "geojson", data: P.fc(d), attribution: P.quelle(d) });
      map.addLayer({ id: lid, type: "circle", source: lid, paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 2.6, 14, 6], "circle-color": P.farbe,
        "circle-stroke-color": P.rand || "#fff", "circle-stroke-width": P.rand ? 1.5 : 1 } },
        id === "rejestr" && map.getLayer("pkt-zabytki") ? "pkt-zabytki" : undefined);   // Register unter der OSM-Kennzeichnung, sonst verdeckt
    }
    map.setLayoutProperty(lid, "visibility", "visible");
    punktLegende();
    if (fertig) fertig();
  });
}
// Sichtprüfung der Denkmalpunkte am Luftbild (Feld sichtpruefung in daten/denkmale*.js): Zahlen aus den Daten
function geprueft(d) { return !!(d && d.sichtpruefung && d.sichtpruefung.geprueft === true && d.sichtpruefung.ergebnis); }
function proz0(x) { return I18N.fmt.anteil(x, 0); }
function sichtLage(d) {
  var sp = d.sichtpruefung, e = sp.ergebnis, L = e.lage;
  return tt("denkmale.sicht.lage", { n: fmt.format(e.n), datum: I18N.fmt.datum(sp.datum + "T12:00:00", { day: "numeric", month: "long", year: "numeric" }),
    ja: fmt.format(L.ja), daneben: fmt.format(L.daneben), nein: fmt.format(L.nein), q: proz0(L.quote), von: proz0(L.wilson95[0]), bis: proz0(L.wilson95[1]) });
}
function sichtPunkt(d) { return tt("denkmale.sicht.punkt", { q: proz0(d.sichtpruefung.ergebnis.lage.quote) }); }
function punktLegende() {
  legPunkte.textContent = "";
  var an = zustand.pkt.filter(function (id) { return GELADEN[id]; });
  legPunkte.hidden = !an.length;
  an.forEach(function (id) {
    var d = GELADEN[id], p = el("p", "fl-punkt"), sw = el("span", "fl-kreis");
    sw.style.background = typeof PUNKTE[id].farbe === "string" ? PUNKTE[id].farbe : PUNKTE[id].farbe[3];
    if (PUNKTE[id].rand) sw.style.boxShadow = "0 0 0 1.5px " + PUNKTE[id].rand;
    p.appendChild(sw); p.appendChild(document.createTextNode(PUNKT_TEXT[id]));
    if (d.fixture === true) p.appendChild(el("span", "fl-beispiel", tt("erzaehlung.beispiel_marke")));
    legPunkte.appendChild(p);
    if (id === "zabytki") legPunkte.appendChild(el("p", "fl-hinweis", tt("erzaehlung.zabytki_auswahl", {
      n: fmt.format(PUNKTE.zabytki.fc(d).features.length), alle: fmt.format(d.objekte.features.length) })));
    if (id === "zabytki" && d.sichtpruefung) legPunkte.appendChild(el("p", "fl-hinweis", geprueft(d) ? sichtLage(d) + " " + tt("denkmale.sicht.budynek") : tt("erzaehlung.zabytki_ungeprueft")));
    if (id === "rejestr") legPunkte.appendChild(el("p", "fl-hinweis", tt("erzaehlung.rejestr_auswahl", { n: fmt.format(PUNKTE.rejestr.fc(d).features.length) })));
    if (id === "rejestr" && d.sichtpruefung) legPunkte.appendChild(el("p", "fl-hinweis", geprueft(d) ? tt("erzaehlung.rejestr_lage") + " " + sichtLage(d) : tt("erzaehlung.rejestr_ungeprueft")));
    if (id === "haltestellen") legPunkte.appendChild(el("p", "fl-hinweis", tt("erzaehlung.takt_klassen", {
      i: fmt.format(d.klassen.grenzen.I), ii: fmt.format(d.klassen.grenzen.II), iii: fmt.format(d.klassen.grenzen.III) })));
    legPunkte.appendChild(el("p", "fl-quelle", PUNKTE[id].quelle(d)));
    if (id === "zbk") klausel(legPunkte, d.quellen.zbk);
  });
}

// ---------- Popups: Wert und Quelle des angeklickten Objekts
var EIG = { gmina: tt("erzaehlung.eig_gmina"), skarb_panstwa: tt("erzaehlung.eig_skarb_panstwa"), publiczne_mieszane: tt("erzaehlung.eig_publiczne_mieszane") };
var ART_ZBK = { M: tt("erzaehlung.zbk_art_m"), U: tt("erzaehlung.zbk_art_u"), P: tt("erzaehlung.zbk_art_p") };
var ART_EIN = { szkola: tt("erzaehlung.ziel_szkola"), przedszkole: tt("erzaehlung.ziel_przedszkole"), zlobek: tt("erzaehlung.ziel_zlobek"), szpital: tt("erzaehlung.ziel_szpital"), park: tt("erzaehlung.ziel_park") };
var KLASSE_TEXT = { vor_1800: tt("denkmale.klasse.vor_1800"), "1800_1866": tt("denkmale.klasse.1800_1866"), "1867_1918": tt("denkmale.klasse.1867_1918"),
  "1919_1945": tt("denkmale.klasse.1919_1945"), "1946_1989": tt("denkmale.klasse.1946_1989"), ab_1990: tt("denkmale.klasse.ab_1990"), "null": tt("denkmale.klasse.null") };
var HQ = { lod2: tt("erzaehlung.hq_lod2"), geschosse: tt("erzaehlung.hq_geschosse") };
function zeile(k, v) { return "<div class='ka-pop-z'><span>" + esc(k) + "</span><b>" + esc(v) + "</b></div>"; }
function quelle(q) { return "<p class='ka-pop-q'>" + esc(q) + "</p>"; }
function teilName(nr) { var t = ORT.gliederung.teile.filter(function (x) { return x.nr === nr; })[0]; return t ? I18N.sprachwert(t.anzeige) : nr; }
var popup = new maplibregl.Popup({ closeButton: true, maxWidth: "300px" });
map.on("click", function (e) {
  var punktIds = Object.keys(PUNKTE).map(function (id) { return "pkt-" + id; }).filter(function (id) { return map.getLayer(id) && map.getLayoutProperty(id, "visibility") !== "none"; });
  var f = punktIds.length ? map.queryRenderedFeatures(e.point, { layers: punktIds })[0] : null, h = "";
  if (f) {
    var id = f.layer.id.slice(4), p = f.properties, d = GELADEN[id];
    if (id === "haltestellen") h = "<p class='ka-pop-t'>" + esc(p.name) + "</p>" + zeile(tt("erzaehlung.pop_taktklasse"), p.taktklasse)
      + zeile(tt("erzaehlung.pop_fahrten"), p.fahrten_hvz_je_richtung == null ? tt("kern.k_a") : fmt1.format(p.fahrten_hvz_je_richtung)) + quelle(PUNKTE[id].quelle(d));
    else if (id === "einrichtungen") h = "<p class='ka-pop-t'>" + esc(ART_EIN[p.art] || p.art) + "</p>" + (p.name && p.name !== "null" ? "<p>" + esc(p.name) + "</p>" : "")
      + "<p class='ka-pop-h'>" + esc(tt("erzaehlung.pop_ohne_kapazitaet")) + "</p>" + quelle(PUNKTE[id].quelle(d));
    else if (id === "zbk") {
      var arten = String(p.art).split("").map(function (c) { return ART_ZBK[c] || c; }).join(", ");
      h = "<p class='ka-pop-t'>" + esc(tt("erzaehlung.pkt_zbk")) + "</p>" + zeile(tt("erzaehlung.pop_zbk_art"), arten) + zeile(tt("erzaehlung.pop_eigentum"), EIG[p.eig] || p.eig)
        + (p.fn && p.fn !== "null" ? zeile(tt("erzaehlung.pop_funktion"), p.fn) : "")
        + (p.gs && p.gs !== "null" ? zeile(tt("erzaehlung.pop_geschosse"), fmt.format(+p.gs)) : "")
        + (p.h && p.h !== "null" ? zeile(tt("erzaehlung.pop_hoehe"), fmt1.format(+p.h) + NB + "m") + "<p class='ka-pop-h'>" + esc(HQ[p.hq] || tt("kern.k_a")) + "</p>" : "")
        + quelle(PUNKTE[id].quelle(d)) + (p.hq === "lod2" ? quelle(d.quellen.lod2.vermerk) : "");
    } else if (id === "rejestr") h = "<p class='ka-pop-t'>" + esc(tt("erzaehlung.pop_rejestr")) + "</p>"
      + zeile(tt("erzaehlung.pop_bauzeit"), KLASSE_TEXT[p.ep] || KLASSE_TEXT["null"])
      + zeile(tt("denkmale.delegatura"), p.del)
      + "<p class='ka-pop-h'>" + esc(geprueft(d) ? tt("erzaehlung.rejestr_lage") + " " + sichtPunkt(d) : tt("erzaehlung.rejestr_ungeprueft")) + "</p>" + quelle(PUNKTE[id].quelle(d));
    else if (id === "zabytki") h = "<p class='ka-pop-t'>" + esc(tt("erzaehlung.pkt_zabytki")) + "</p>"
      + "<p class='ka-pop-h'>" + esc(geprueft(d) ? sichtPunkt(d) + " " + tt("denkmale.sicht.budynek") : tt("erzaehlung.zabytki_ungeprueft")) + "</p>" + quelle(PUNKTE[id].quelle(d));
    else if (id === "powietrze") h = "<p class='ka-pop-t'>" + esc(p.nazwa) + (d && d.fixture === true ? " <span class='fl-beispiel'>" + esc(tt("erzaehlung.beispiel_marke")) + "</span>" : "") + "</p>"
      + zeile(tt("erzaehlung.pop_pm10_przed"), p.pm10_przed == null || p.pm10_przed === "null" ? tt("kern.k_a") : fmt1.format(+p.pm10_przed) + NB + "µg/m³")
      + zeile(tt("erzaehlung.pop_pm10_po"), p.pm10_po == null || p.pm10_po === "null" ? tt("kern.k_a") : fmt1.format(+p.pm10_po) + NB + "µg/m³") + quelle(PUNKTE[id].quelle(d));
  }
  if (!h && map.getLayer("klimat-flaeche") && map.getLayoutProperty("klimat-flaeche", "visibility") !== "none") {
    var kz = map.queryRenderedFeatures(e.point, { layers: ["klimat-flaeche"] })[0];
    if (kz) {
      var x = themaTeile(zustand.thema).id, v = kz.properties[x];
      h = "<p class='ka-pop-t'>" + esc(KLIMA[x]) + "</p>" + zeile(tt("erzaehlung.pop_anteil"), v == null || v === "null" ? tt("erzaehlung.pop_zu_klein") : fmt1.format(+v) + PZ)
        + zeile(tt("erzaehlung.pop_flaeche_stadt"), fmt1.format(+kz.properties.flaeche) + NB + "ha") + quelle(window.KIEZ_KLIMAT_ZELLEN.quelle.vermerk);
    }
  }
  if (!h && map.getLayoutProperty("zellen-flaeche", "visibility") !== "none") {
    var z = map.queryRenderedFeatures(e.point, { layers: ["zellen-flaeche"] })[0];
    if (z) {
      var tx = themaTeile(zustand.thema), zp = z.properties;
      if (tx.art === "fuss") {
        var w = map.getFeatureState({ source: "zellen", id: zp.id }).w;
        h = "<p class='ka-pop-t'>" + esc(tt("erzaehlung.leg_fuss", { ziel: FUSS_TEXT[tx.id] })) + "</p>"
          + zeile(tt("erzaehlung.pop_fuss_m"), w == null ? tt("kern.k_a") : fmt.format(w) + NB + "m")
          + "<p class='ka-pop-h'>" + esc(tt("erzaehlung.fuss_hinweis")) + "</p>" + quelle(tt("erzaehlung.quelle_fuss"));
      } else {
        var th = T.THEMA[T.HASH[tx.id] || tx.id];
        h = "<p class='ka-pop-t'>" + esc(th.name) + "</p>" + zeile(tt("erzaehlung.pop_ew_zelle"), fmt.format(zp.ew))
          + (th.einheit === "%" ? zeile(th.kurz, zp[th.id] == null ? tt("kern.k_a") : fmt1.format(zp[th.id]) + PZ) : "")
          + (zp.st ? zeile(I18N.sprachwert(ORT.gliederung.einheit), teilName(zp.st)) : "") + quelle(tt("erzaehlung.quelle_gitter"));
      }
    }
  }
  if (!h) {
    var t = map.queryRenderedFeatures(e.point, { layers: ["teile-flaeche"] })[0];
    if (t) { teilWaehlen(t.properties.nr, false); h = teilPopup(t.properties.nr); hashSchreiben(); }
  }
  if (h) popup.setLngLat(e.lngLat).setHTML(h).addTo(map); else popup.remove();
});
function teilPopup(nr) {
  var k = K && K.stadtteile[nr], ew = k ? T.kachel(k, "einwohner") : null;
  return "<p class='ka-pop-t'>" + esc(teilName(nr)) + "</p>"
    + (ew ? zeile(tt("erzaehlung.pop_ew_gitter"), tt("kern.rund", { zahl: T.rundEw(ew.wert) })) : "")
    + (k ? zeile(tt("erzaehlung.pop_flaeche"), fmt1.format(k.flaeche_km2) + NB + "km²") : "")
    + quelle(tt("erzaehlung.quelle_gitter")) + quelle(I18N.sprachwert(ORT.karte.teile_bildzeile))
    + "<p><a class='link' href='dzielnica.html#st=" + esc(nr) + "'>" + esc(tt("erzaehlung.zum_steckbrief")) + "</a></p>";
}
map.on("mousemove", function (e) {
  var ids = ["teile-flaeche"].concat(Object.keys(PUNKTE).map(function (id) { return "pkt-" + id; }).filter(function (id) { return map.getLayer(id); }));
  map.getCanvas().style.cursor = map.queryRenderedFeatures(e.point, { layers: ids }).length ? "pointer" : "";
});

// ---------- Stadtteil wählen (Auswahl, Liste, Hash st)
var wahl = document.getElementById("ka-teil");
ORT.gliederung.teile.forEach(function (t) { var o = el("option", null, I18N.sprachwert(t.anzeige)); o.value = t.nr; wahl.appendChild(o); });
function teilWaehlen(nr, fliegen) {
  zustand.st = T.TEIL[nr] ? nr : "";
  wahl.value = zustand.st;
  KF.auswahl(map, zustand.st);
  if (fliegen) KF.zeige(map, KF.teilRahmen(zustand.st || null), 32);
}
wahl.addEventListener("change", function () { teilWaehlen(wahl.value, true); popup.remove(); hashSchreiben(); });

// ---------- Bedienelemente
var zellWahl = document.getElementById("ka-zelle");
function zellWahlFuellen() {
  T.THEMEN.slice(1).forEach(function (th) { var o = el("option", null, th.name); o.value = th.h; zellWahl.querySelector('optgroup[data-gruppe="gitter"]').appendChild(o); });
  FUSS.forEach(function (id) { var o = el("option", null, FUSS_TEXT[id]); o.value = "fuss:" + id; zellWahl.querySelector('optgroup[data-gruppe="fuss"]').appendChild(o); });
  Object.keys(KLIMA).forEach(function (id) { var o = el("option", null, KLIMA[id]); o.value = "klima:" + id; zellWahl.querySelector('optgroup[data-gruppe="klima"]').appendChild(o); });
}
zellWahlFuellen();
// Zellebene und Färbung der Stadtteile nach Werten schließen sich aus (sonst überdecken sich zwei Farbskalen)
function dzSetzen(art) { zustand.dz = art; var r = dzBox.querySelector('input[name="dz"][value="' + art + '"]'); if (r) r.checked = true; teilfaerbung(art); }
zellWahl.addEventListener("change", function () {
  zustand.thema = zellWahl.value; popup.remove();
  if (zustand.thema && zustand.dz !== "gruppen") dzSetzen("gruppen");
  zellebene(zustand.thema); teilDeckkraft(); hashSchreiben();
});
dzBox.addEventListener("change", function (e) {
  if (e.target.name !== "dz") return;
  zustand.dz = e.target.value;
  if (zustand.dz !== "gruppen" && zustand.thema) { zustand.thema = zellWahl.value = ""; zellebene(""); }
  teilfaerbung(zustand.dz); teilDeckkraft(); hashSchreiben();
});
document.querySelectorAll('input[name="pkt"]').forEach(function (c) {
  c.addEventListener("change", function () {
    zustand.pkt = [].slice.call(document.querySelectorAll('input[name="pkt"]:checked')).map(function (x) { return x.value; });
    punktebene(c.value, c.checked); hashSchreiben();
  });
});
map.on("moveend", function (e) { if (e.originalEvent) hashSchreiben(); });

// ---------- Start: Zustand aus dem Hash anwenden (ohne den Hash zu schreiben)
function anwenden() {
  if (zustand.thema && zellWahl.querySelector('option[value="' + zustand.thema.replace(/"/g, "") + '"]')) zellWahl.value = zustand.thema; else zustand.thema = zellWahl.value = "";
  zellebene(zustand.thema);
  var r = dzBox.querySelector('input[name="dz"][value="' + zustand.dz.replace(/"/g, "") + '"]');
  if (!r) { zustand.dz = "gruppen"; r = dzBox.querySelector('input[name="dz"][value="gruppen"]'); }
  if (zustand.dz !== "gruppen" && zustand.thema) { zustand.dz = "gruppen"; r = dzBox.querySelector('input[name="dz"][value="gruppen"]'); }
  r.checked = true; teilfaerbung(zustand.dz); teilDeckkraft();
  zustand.pkt = zustand.pkt.filter(function (id) { return PUNKTE[id]; });
  zustand.pkt.forEach(function (id) { var c = document.querySelector('input[name="pkt"][value="' + id + '"]'); if (c) { c.checked = true; punktebene(id, true); } });
  var kk = (zustand.k || "").split("/").map(Number);
  if (kk.length >= 3 && kk.slice(0, 3).every(function (x) { return isFinite(x); })) map.jumpTo({ zoom: kk[0], center: [kk[2], kk[1]] });
  if (zustand.st) teilWaehlen(zustand.st, !(kk.length >= 3 && isFinite(kk[0])));
}
if (map.loaded()) anwenden(); else map.once("load", anwenden);
addEventListener("hashchange", function () {
  var o = hashLesen();
  if ((o.thema || "") !== zustand.thema && (!o.thema || zellWahl.querySelector('option[value="' + o.thema.replace(/"/g, "") + '"]'))) {
    zustand.thema = o.thema || ""; zellWahl.value = zustand.thema; zellebene(zustand.thema); teilDeckkraft();
  }
  if ((o.st || "") !== zustand.st && T.TEIL[o.st]) teilWaehlen(o.st, true);
});
})();
