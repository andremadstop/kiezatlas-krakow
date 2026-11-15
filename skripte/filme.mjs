// Drei kurze Filme auf Polnisch aus der echten Seite: headless Chromium über den Entwicklungsserver
// (skripte/entwicklung_server.mjs, nur 127.0.0.1), ohne Ton, mit eingeblendeten Untertiteln und Texttafeln.
// Aufgenommen wird über das Bildschirm-Streaming von Chromium (CDP Page.startScreencast, JPEG); die Bilder bleiben im
// Speicher und gehen als gleichmäßige Folge mit 25 Bildern je Sekunde direkt an ffmpeg (MP4 H.264 und WebM VP9 in
// einem Lauf, keine Zwischendateien). Seitenwechsel und Ladezeiten werden herausgeschnitten: aufgenommen wird nur,
// solange eine Szene läuft.
//
// Wiederholbar, nicht bitgleich: feste Ansicht 1280 × 720 px, Pixelverhältnis 1, feste Wartezeiten, Math.random mit
// festem Startwert, Abrufe nur von 127.0.0.1. Ladezeiten und Bildtakt des Browsers schwanken, darum unterscheiden sich
// zwei Läufe in einzelnen Bildern und damit in der Prüfsumme.
//
// Zahlen in den Untertiteln stehen nicht im Skript, sondern kommen beim Lauf aus den Datendateien der Seite
// (window.KIEZ_POWIETRZE.okna, window.KIEZ_MIESZKANIA.regeln.mindestfallzahl). Untertitel je Film als WebVTT auf Polnisch
// (wie eingeblendet), dazu Englisch und Deutsch mit denselben Zeiten. Keine Bedienung auf der Karte (keine Popups
// mit Adressen), keine Ebene mit Einzelgebäuden aus dem Wykaz ZBK, keine Einzelpreise.
//
// Schreibt nach <ziel>/: film<N>-<name>.mp4, .webm, .pl.vtt, .en.vtt, .de.vtt und README.md (Drehbuch, Dauer,
// Größe, SHA256, Befehl; aus den Dateien auf der Platte, auch für Filme, die dieser Lauf nicht neu aufnimmt).
// Prüft jeden neuen Film mit ffprobe: Dauer 50 bis 75 s, MP4 und WebM je höchstens 5 MB. Mit --standbilder ORDNER
// legt es je Untertitel ein Standbild aus der Mitte der Einblendung ab (zum Ansehen, nicht für das Repo).
//
//   node skripte/filme.mjs [--ziel belege/filme] [--nur 1,2,3] [--standbilder ORDNER]
// Rückgabe 0 = alle Vorgaben erfüllt, 1 = Befund.
import { chromium } from "playwright";
import { spawn, execFileSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { starten } from "./entwicklung_server.mjs";

const WURZEL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const ZIEL = path.resolve(WURZEL, arg("--ziel", "belege/filme"));
const NUR = arg("--nur", "1,2,3").split(",").map(Number);
const STANDBILDER = arg("--standbilder", null);
const BREITE = 1280, HOEHE = 720, FPS = 25;
const DAUER_MIN = 50, DAUER_MAX = 75, GROESSE_MAX = 5 * 1024 * 1024;
const SPRACHEN = ["pl", "en", "de"];

// ---------------------------------------------------------------------------------------------------------------
// Drehbuch. Jede Szene: Seite, dann Schritte. Ein Schritt mit Text (pl/en/de) blendet einen Untertitel ein, der bis
// zum nächsten Text oder zum Ende der Szene steht; „tafel“ zeigt eine Texttafel über der Seite. Texte können
// Funktionen der Daten d sein (d wird beim Lauf aus der Seite gelesen). „tun“ beschreibt die Bedienung für das
// Drehbuch im README.

const QUELLEN_TITEL = { pl: "Źródła", en: "Sources", de: "Quellen" };
const NOTEN = { pl: "Pełne noty o źródłach i licencje: strona „Dane”.", en: "Full source notes and licences: the „Dane” page.",
  de: "Vollständige Quellenvermerke und Lizenzen: Seite „Dane“." };

const FILME = [
  {
    nr: 1, name: "atlas-w-minute",
    titel: { pl: "Atlas w minutę", en: "The atlas in a minute", de: "Der Atlas in einer Minute" },
    szenen: [
      { seite: "index", schritte: [
        { tafel: true, ms: 4000, tun: "Titeltafel",
          pl: ["Atlas w minutę", "Atlas dzielnic Krakowa z otwartych danych publicznych"],
          en: ["The atlas in a minute", "An atlas of Kraków's districts from open public data"],
          de: ["Der Atlas in einer Minute", "Ein Atlas der Krakauer Stadtteile aus offenen amtlichen Daten"] },
        { ms: 4800, tun: "Startseite, Kopf mit den Stadtzahlen",
          pl: "Strona główna: najważniejsze liczby miasta, przy każdej źródło.",
          en: "Home page: the city's key figures, each with its source.",
          de: "Startseite: die wichtigsten Zahlen der Stadt, jede mit Quelle." },
        { ms: 5000, tun: "langsam zur ersten Frage scrollen", aktion: { scrolle: "h2", nr: 0, ms: 2200 },
          pl: "Pytania prowadzą przez miasto, a mapa pokazuje odpowiedź.",
          en: "Questions lead through the city; the map shows the answer.",
          de: "Fragen führen durch die Stadt, die Karte zeigt die Antwort." },
        { ms: 5200, tun: "weiter zur Frage nach der Dichte", aktion: { scrolle: "h2", nr: 2, ms: 2400 },
          pl: "Z każdym pytaniem zmieniają się kolory mapy.",
          en: "The map colours change with every question.",
          de: "Mit jeder Frage wechseln die Farben der Karte." },
      ] },
      { seite: "karta", vorher: { scrolle: ".ka-kartenseite", versatz: 72 }, schritte: [
        { ms: 4400, tun: "Karte mit den delegatury",
          pl: "Mapa: wszystkie tematy atlasu na jednej mapie.",
          en: "Map: all topics of the atlas on one map.",
          de: "Karte: alle Themen des Atlas auf einer Karte." },
        { ms: 4800, tun: "Gitterebene „Mieszkańcy w komórce siatki“ wählen", aktion: { waehle: "#ka-zelle", erste: true },
          pl: "Warstwa siatki 1 km: mieszkańcy w komórce siatki.",
          en: "1 km grid layer: residents per grid cell.",
          de: "Gitterebene 1 km: Einwohner je Gitterzelle." },
        { ms: 4800, tun: "Gitter aus, Farben der dzielnice: Bebauungsanteil", aktion: [{ waehle: "#ka-zelle", wert: "" }, { klicke: 'input[name=dz][value=bebauung]' }],
          pl: "Kolory dzielnic: udział powierzchni zabudowy budynkami.",
          en: "District colours: building coverage.",
          de: "Farben der Stadtteile: Bebauungsanteil." },
        { ms: 4800, tun: "Punkte: Haltestellen nach Taktklasse", aktion: { klicke: 'input[name=pkt][value=haltestellen]' },
          pl: "Punkty: przystanki według klasy częstotliwości kursowania.",
          en: "Points: stops by service frequency class.",
          de: "Punkte: Haltestellen nach Taktklasse." },
      ] },
      { seite: "dzielnica", schritte: [
        { ms: 4800, tun: "Steckbrief, dzielnica XIII Podgórze wählen", aktion: { waehle: "#ka-teil", text: "Podgórze", genau: "XIII" },
          pl: "Profil dzielnicy: wskaźniki, miejsce wśród dzielnic i źródło.",
          en: "District profile: indicators, rank among districts and source.",
          de: "Steckbrief: Kennzahlen, Rang unter den Stadtteilen und Quelle." },
        { ms: 5000, tun: "zu den Kennzahlen scrollen", aktion: { scrolle: "h3", nr: 0, ms: 2200, versatz: 90 },
          pl: "Brak wartości oznacza brak danych, nie zero.",
          en: "A missing value means no data, not zero.",
          de: "Fehlt ein Wert, fehlen Daten; er ist nicht null." },
      ] },
      { seite: "porownanie", schritte: [
        { ms: 4800, tun: "Vergleich Kraków und Potsdam",
          pl: "Porównanie: Kraków i Poczdam, ta sama siatka i ta sama metoda.",
          en: "Comparison: Kraków and Potsdam, same grid, same method.",
          de: "Vergleich: Kraków und Potsdam, gleiches Gitter, gleiche Methode." },
        { ms: 4800, tun: "zur Tabelle scrollen", aktion: { scrolle: "h2", nr: 0, ms: 2000, versatz: 90 },
          pl: "Porównujemy tylko wskaźniki o tej samej definicji.",
          en: "Only indicators with the same definition are compared.",
          de: "Verglichen werden nur Kennzahlen mit gleicher Definition." },
        { ms: 5000, tun: "zu „Czego nie porównujemy“ scrollen", aktion: { scrolle: "h2", nr: 2, ms: 2200, versatz: 90 },
          pl: "Resztę wymieniamy osobno: czego nie porównujemy i dlaczego.",
          en: "The rest is listed separately: what is not compared and why.",
          de: "Der Rest steht eigens da: was nicht verglichen wird und warum." },
        { tafel: true, quellen: true, ms: 5000, tun: "Quellentafel",
          pl: [QUELLEN_TITEL.pl, "GUS, Narodowy Spis Powszechny 2021", "Eurostat, Census 2021 population grid (CC BY 4.0)",
            "BDOT10k, Główny Urząd Geodezji i Kartografii", "Rozkład jazdy: ZTP Kraków, GTFS (CC BY 4.0)",
            "Granice dzielnic: © autorzy OpenStreetMap (ODbL)", NOTEN.pl],
          en: [QUELLEN_TITEL.en, "GUS, Narodowy Spis Powszechny 2021", "Eurostat, Census 2021 population grid (CC BY 4.0)",
            "BDOT10k, Główny Urząd Geodezji i Kartografii", "Timetable: ZTP Kraków, GTFS (CC BY 4.0)",
            "District boundaries: © OpenStreetMap contributors (ODbL)", NOTEN.en],
          de: [QUELLEN_TITEL.de, "GUS, Narodowy Spis Powszechny 2021", "Eurostat, Census 2021 population grid (CC BY 4.0)",
            "BDOT10k, Główny Urząd Geodezji i Kartografii", "Fahrplan: ZTP Kraków, GTFS (CC BY 4.0)",
            "Stadtteilgrenzen: © OpenStreetMap-Mitwirkende (ODbL)", NOTEN.de] },
      ] },
    ],
  },
  {
    nr: 2, name: "kamienice-i-zabytki",
    titel: { pl: "Kamienice i zabytki", en: "Tenement houses and monuments", de: "Kamienice und Denkmale" },
    szenen: [
      { seite: "kamienice", schritte: [
        { tafel: true, ms: 4000, tun: "Titeltafel",
          pl: ["Kamienice i zabytki", "Co źródła wymieniają jako zabytek i jak to sprawdzono"],
          en: ["Tenement houses and monuments", "What the sources list as a monument, and how it was checked"],
          de: ["Kamienice und Denkmale", "Was die Quellen als Denkmal nennen und wie es geprüft wurde"] },
        { ms: 4800, tun: "Seite Kamienice, Karte mit allen Punkten",
          pl: "Mapa pokazuje tylko obiekty, które źródło wymienia jako zabytek.",
          en: "The map shows only objects that a source lists as a monument.",
          de: "Die Karte zeigt nur Objekte, die eine Quelle als Denkmal nennt." },
        { ms: 5000, tun: "Marken über der Karte hervorheben", aktion: { hebe: ".ks-abz" },
          pl: "Oznaczenia nad mapą mówią wprost: zbiór niepełny, rejestr tylko z Wikidanych.",
          en: "The labels above the map say it plainly: incomplete set, register only from Wikidata.",
          de: "Die Marken über der Karte sagen es offen: unvollständig, Register nur aus Wikidata." },
        { ms: 5000, tun: "zur Karte scrollen, „Tylko kamienice (OSM)“ drücken", aktion: [{ scrolle: ".kartenfeld, #karte", nr: 0, ms: 1600, versatz: 24 }, { klicke: "#nur-kamienice" }],
          pl: "Kamienica w atlasie: budynek wielorodzinny, który źródło wymienia jako zabytek.",
          en: "Kamienica (tenement house) in the atlas: a multi-family building that a source lists as a monument.",
          de: "Kamienica (Mietshaus) im Atlas: ein Mehrfamilienhaus, das eine Quelle als Denkmal nennt." },
        { ms: 4800, tun: "wieder alle Denkmale; Bauzeit-Chip „okres budowy nieznany“ aus", aktion: [{ klicke: "#nur-kamienice" }, { klicke: '#ep label:has(input[value="null"])' }],
          pl: "Podajemy tylko okres budowy, nigdy dokładny rok.",
          en: "Only the construction period is given, never the exact year.",
          de: "Angegeben wird nur die Bauzeit als Spanne, nie das genaue Jahr." },
        { ms: 5200, tun: "Seitenleiste neben der Karte bis „Źródła i stan“ rollen, Zeile Wikidane mit dem Ergebnis der Sichtprüfung hervorheben",
          aktion: [{ scrolle: "h2", text: "Źródła i stan", ms: 2000 }, { hebe: ".ks-zahlen li", text: "Część rejestru; położenie", dauer: 8000 }],
          pl: "Położenie punktów sprawdzono na ortofotomapie, na losowej próbie.",
          en: "Point locations were checked against the aerial image on a random sample.",
          de: "Die Lage der Punkte wurde am Luftbild in einer Zufallsstichprobe geprüft." },
        { ms: 5200, tun: "stehen lassen",
          pl: "Wynik podano przy źródle: na obiekcie, tuż obok, poza obiektem, z przedziałem ufności.",
          en: "The result sits next to the source: on the object, just beside it, off it, with a confidence interval.",
          de: "Das Ergebnis steht bei der Quelle: auf dem Objekt, knapp daneben, nicht dort, mit Konfidenzintervall." },
        { ms: 5000, tun: "Seitenleiste bis „Rejestr zabytków, część z Wikidanych“ rollen", aktion: { scrolle: "h2", text: "Rejestr zabytków", ms: 2000 },
          pl: "Rejestr zabytków: na razie tylko część z Wikidanych, bez rejestru NID.",
          en: "Register of monuments: for now only the part in Wikidata, without the NID register.",
          de: "Denkmalregister: vorerst nur der Teil aus Wikidata, ohne das NID-Register." },
        { ms: 5000, tun: "unter der Karte zu „Ograniczenia“ scrollen, Satz hervorheben",
          aktion: [{ scrolle: "h2", text: "Ograniczenia", ms: 2000, versatz: 90 }, { hebe: "li", text: "Brak punktu", dauer: 4000 }],
          pl: "Brak punktu nie znaczy, że budynek nie jest zabytkiem.",
          en: "A missing point does not mean that a building is not a monument.",
          de: "Fehlt ein Punkt, heißt das nicht, dass das Haus kein Denkmal ist." },
      ] },
      { seite: "karta", vorher: { scrolle: ".ka-kartenseite", versatz: 72 }, schritte: [
        { ms: 5000, tun: "Karte: Registerpunkte aus Wikidata einschalten", aktion: { klicke: 'input[name=pkt][value=rejestr]' },
          pl: "Na mapie atlasu: punkty rejestru z Wikidanych jako osobna warstwa.",
          en: "On the atlas map: register points from Wikidata as a separate layer.",
          de: "Auf der Atlaskarte: Registerpunkte aus Wikidata als eigene Ebene." },
        { ms: 5000, tun: "OSM-Kennzeichnung dazu", aktion: { klicke: 'input[name=pkt][value=zabytki]' },
          pl: "Obok: oznaczenie zabytku w OpenStreetMap. Dwa źródła, dwie warstwy.",
          en: "Next to it: the heritage tag in OpenStreetMap. Two sources, two layers.",
          de: "Daneben: die Denkmal-Kennzeichnung in OpenStreetMap. Zwei Quellen, zwei Ebenen." },
        { ms: 4800, tun: "dzielnica I Stare Miasto wählen (Karte fliegt hin)", aktion: { waehle: "#ka-teil", text: "Stare Miasto", genau: "Dzielnica I " },
          pl: "Bliżej: Stare Miasto.",
          en: "Closer: Stare Miasto.",
          de: "Näher heran: Stare Miasto." },
        { tafel: true, quellen: true, ms: 5000, tun: "Quellentafel",
          pl: [QUELLEN_TITEL.pl, "Rejestr zabytków: Wikidane (Wikidata, CC0)", "Oznaczenie zabytku: © autorzy OpenStreetMap (ODbL)",
            "Budynki i kompleksy: BDOT10k, Główny Urząd Geodezji i Kartografii", "Granice dzielnic: © autorzy OpenStreetMap (ODbL)", NOTEN.pl],
          en: [QUELLEN_TITEL.en, "Register of monuments: Wikidata (CC0)", "Heritage tag: © OpenStreetMap contributors (ODbL)",
            "Buildings and complexes: BDOT10k, Główny Urząd Geodezji i Kartografii", "District boundaries: © OpenStreetMap contributors (ODbL)", NOTEN.en],
          de: [QUELLEN_TITEL.de, "Denkmalregister: Wikidata (CC0)", "Denkmal-Kennzeichnung: © OpenStreetMap-Mitwirkende (ODbL)",
            "Gebäude und Komplexe: BDOT10k, Główny Urząd Geodezji i Kartografii", "Stadtteilgrenzen: © OpenStreetMap-Mitwirkende (ODbL)", NOTEN.de] },
      ] },
    ],
  },
  {
    nr: 3, name: "dane-nie-opinie",
    titel: { pl: "Dane, nie opinie", en: "Data, not opinions", de: "Daten, keine Meinungen" },
    szenen: [
      { seite: "powietrze", schritte: [
        { tafel: true, ms: 4000, tun: "Titeltafel",
          pl: ["Dane, nie opinie", "Powietrze, ceny mieszkań, metodologia: co mówią liczby, a czego nie"],
          en: ["Data, not opinions", "Air, housing prices, methodology: what the figures say and what they do not"],
          de: ["Daten, keine Meinungen", "Luft, Wohnungspreise, Methode: was die Zahlen sagen und was nicht"] },
        { ms: 4600, tun: "Seite Jakość powietrza",
          pl: "Jakość powietrza: wartości roczne stacji pomiarowych, obliczone przez EEA.",
          en: "Air quality: annual values of the monitoring stations, calculated by the EEA.",
          de: "Luftqualität: Jahreswerte der Messstationen, berechnet von der EEA." },
        { ms: 4600, tun: "zum Diagramm scrollen", aktion: { scrolle: "#p-h-przebieg", ms: 2200, versatz: 70 },
          pl: "Na wykresie: każda stacja i poziom dopuszczalny.",
          en: "The chart: every station and the limit value.",
          de: "Im Diagramm: jede Station und der Grenzwert." },
        { ms: 5200, tun: "stehen lassen (Zeiträume vorher und nachher sind markiert)",
          pl: (d) => `Przed: średnia ${d.okna.przed[0]}–${d.okna.przed[1]}. Po: średnia ${d.okna.po[0]}–${d.okna.po[1]}. Rok ${d.okna.przejscie} pominięty.`,
          en: (d) => `Before: mean ${d.okna.przed[0]}–${d.okna.przed[1]}. After: mean ${d.okna.po[0]}–${d.okna.po[1]}. ${d.okna.przejscie} left out.`,
          de: (d) => `Vorher: Mittel ${d.okna.przed[0]}–${d.okna.przed[1]}. Nachher: Mittel ${d.okna.po[0]}–${d.okna.po[1]}. ${d.okna.przejscie} ausgelassen.` },
        { ms: 4800, tun: "zur Tabelle vorher/nachher scrollen", aktion: { scrolle: "#p-h-przedpo", ms: 2200, versatz: 70 },
          pl: "To porównanie w czasie, nie dowód przyczyny.",
          en: "This is a comparison over time, not proof of cause.",
          de: "Das ist ein zeitlicher Vergleich, kein Beleg für eine Ursache." },
        { ms: 4800, tun: "stehen lassen",
          pl: "Nie uwzględniono wpływu pogody, roku pandemii ani innych działań.",
          en: "Weather, the pandemic year and other measures were not taken out.",
          de: "Wetter, das Pandemiejahr und andere Maßnahmen sind nicht herausgerechnet." },
      ] },
      { seite: "mieszkania", schritte: [
        { ms: 4800, tun: "Seite Rynek mieszkaniowy",
          pl: "Rynek mieszkaniowy: ceny transakcyjne z rejestru, nie ceny ofertowe.",
          en: "Housing market: transaction prices from the register, not asking prices.",
          de: "Wohnungsmarkt: Kaufpreise aus dem Register, keine Angebotspreise." },
        { ms: 5000, tun: "zu den Medianen je dzielnica scrollen", aktion: { scrolle: "#m-h-dzielnice", ms: 2200, versatz: 70 },
          pl: (d) => `Tylko mediany z co najmniej ${d.n} transakcji, bez pojedynczych cen i adresów.`,
          en: (d) => `Only medians from at least ${d.n} transactions, no single prices or addresses.`,
          de: (d) => `Nur Mediane aus mindestens ${d.n} Käufen, keine Einzelpreise und Adressen.` },
        { ms: 5200, tun: "Markt „rynek wtórny“ wählen", aktion: { klicke: ".ts-knopf", text: "rynek wtórny" },
          pl: "Mediany dzielnic dotyczą różnych mieszkań; to nie porównanie takich samych mieszkań.",
          en: "District medians cover different flats; they do not compare like with like.",
          de: "Die Mediane der Stadtteile betreffen verschiedene Wohnungen, kein Vergleich gleicher Wohnungen." },
        { ms: 4600, tun: "zu „Ograniczenia“ scrollen", aktion: { scrolle: "#m-h-granice", ms: 2200, versatz: 70 },
          pl: "Ograniczenia podano na tej samej stronie co liczby.",
          en: "The limitations are on the same page as the figures.",
          de: "Die Grenzen stehen auf derselben Seite wie die Zahlen." },
      ] },
      { seite: "metoda", schritte: [
        { ms: 4800, tun: "Metodologia, zu „Ograniczenia“ scrollen", aktion: { scrolle: "h2", text: "Ograniczenia", ms: 2600, versatz: 90 },
          pl: "Metodologia: zasady, ograniczenia i to, czego nie sprawdzono.",
          en: "Methodology: principles, limitations and what was not checked.",
          de: "Methode: Grundsätze, Grenzen und was nicht geprüft wurde." },
      ] },
      { seite: "dane", schritte: [
        { ms: 4600, tun: "Seite Dane, Downloads", aktion: { scrolle: "h2", text: "Pliki do pobrania", ms: 1600, versatz: 90 },
          pl: "Pliki do pobrania: GeoPackage, CSV i projekt QGIS.",
          en: "Downloads: GeoPackage, CSV and a QGIS project.",
          de: "Downloads: GeoPackage, CSV und ein QGIS-Projekt." },
        { ms: 4600, tun: "zu „Licencje“ scrollen", aktion: { scrolle: "h2", text: "Licencje", ms: 2000, versatz: 90 },
          pl: "Licencje i noty o źródłach dosłownie, w języku oryginału.",
          en: "Licences and source notes verbatim, in the original language.",
          de: "Lizenzen und Quellenvermerke wörtlich, in der Originalsprache." },
        { tafel: true, quellen: true, ms: 5000, tun: "Quellentafel",
          pl: [QUELLEN_TITEL.pl, "Powietrze: EEA; dane: GIOŚ (CC BY 4.0)", "Ceny mieszkań: Rejestr cen nieruchomości, Prezydent Miasta Krakowa (powiat 1261); dane udostępnione przez Główny Urząd Geodezji i Kartografii w serwisie www.geoportal.gov.pl; opracowanie własne (mediany, bez danych jednostkowych)",
            "Granice dzielnic: © autorzy OpenStreetMap (ODbL)", NOTEN.pl],
          en: [QUELLEN_TITEL.en, "Air: EEA; data: GIOŚ (CC BY 4.0)", "Housing prices: Rejestr cen nieruchomości, Prezydent Miasta Krakowa (powiat 1261); dane udostępnione przez Główny Urząd Geodezji i Kartografii w serwisie www.geoportal.gov.pl; opracowanie własne (mediany, bez danych jednostkowych)",
            "District boundaries: © OpenStreetMap contributors (ODbL)", NOTEN.en],
          de: [QUELLEN_TITEL.de, "Luft: EEA; Daten: GIOŚ (CC BY 4.0)", "Wohnungspreise: Rejestr cen nieruchomości, Prezydent Miasta Krakowa (powiat 1261); dane udostępnione przez Główny Urząd Geodezji i Kartografii w serwisie www.geoportal.gov.pl; opracowanie własne (mediany, bez danych jednostkowych)",
            "Stadtteilgrenzen: © OpenStreetMap-Mitwirkende (ODbL)", NOTEN.de] },
      ] },
    ],
  },
];

// ---------------------------------------------------------------------------------------------------------------
// Einblendungen in der Seite (Farben und Schrift wie DESIGN.md: Kartenpapier, Tiefenlinie, Grenzviolett nur als
// Akzent, Barlow / Barlow Semi Condensed; Radius 0; Ease cubic-bezier(.2,.8,.2,1))

const EINBLENDUNG_CSS = `
#film-ut{position:fixed;left:50%;bottom:30px;transform:translateX(-50%);max-width:1000px;z-index:2147483646;
  background:rgba(19,33,42,.94);color:#f1f2ee;font:500 25px/1.32 "Barlow",sans-serif;padding:10px 20px 11px;
  border-left:4px solid #6a2c82;opacity:0;transition:opacity .35s cubic-bezier(.2,.8,.2,1);text-align:left;
  font-variant-numeric:tabular-nums;letter-spacing:.005em;pointer-events:none}
#film-ut.an{opacity:1}
#film-tafel{position:fixed;inset:0;z-index:2147483647;background:#f1f2ee;color:#13212a;display:flex;flex-direction:column;
  justify-content:center;padding:0 96px;opacity:0;transition:opacity .45s cubic-bezier(.2,.8,.2,1);pointer-events:none;
  background-image:linear-gradient(#cdd1cc 1px,transparent 1px),linear-gradient(90deg,#cdd1cc 1px,transparent 1px);
  background-size:80px 80px;background-position:-1px -1px}
#film-tafel.an{opacity:1}
#film-tafel .marke{position:absolute;top:40px;left:96px;font:600 20px/1 "Barlow",sans-serif;display:flex;gap:10px;align-items:center}
#film-tafel .marke i{display:inline-block;width:16px;height:16px;background:linear-gradient(90deg,#13212a 50%,#6a2c82 50%)}
#film-tafel .blatt{background:#f1f2ee;padding:36px 40px 40px;border:1px solid #cdd1cc;max-width:1000px;border-left:6px solid #6a2c82}
#film-tafel h1{font:600 76px/1.02 "Barlow Semi Condensed",sans-serif;margin:0 0 18px;letter-spacing:-.005em}
#film-tafel p{font:400 28px/1.35 "Barlow",sans-serif;color:#4f5d64;margin:0}
#film-tafel.quellen h1{font-size:52px;margin-bottom:22px}
#film-tafel.quellen li{font:400 25px/1.45 "Barlow",sans-serif;color:#13212a;list-style:none;margin:0;padding:0}
#film-tafel.quellen ul{margin:0 0 20px;padding:0}
#film-tafel.quellen p{font-size:22px}
.film-hebe{outline:3px solid #6a2c82 !important;outline-offset:4px !important;transition:outline-color .35s}
`;

function einblendungen(css) {
  if (document.getElementById("film-stil")) return;
  const s = document.createElement("style"); s.id = "film-stil"; s.textContent = css; document.head.appendChild(s);
  const ut = document.createElement("div"); ut.id = "film-ut"; ut.setAttribute("aria-hidden", "true"); document.body.appendChild(ut);
  const t = document.createElement("div"); t.id = "film-tafel"; t.setAttribute("aria-hidden", "true"); document.body.appendChild(t);
}

// fester Startwert für Math.random (mulberry32)
const ZUFALL_FEST = `(() => { let a = 20261115; Math.random = function () { a |= 0; a = a + 0x6D2B79F5 | 0;
  let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; })();`;

// ---------------------------------------------------------------------------------------------------------------
// Aufnahme

const warte = (ms) => new Promise((r) => setTimeout(r, ms));
const git = (...a) => execFileSync("git", ["-C", WURZEL, ...a], { encoding: "utf-8" }).trim();

class Aufnahme {
  constructor(cdp) {
    this.cdp = cdp; this.bilder = []; this.letztes = null; this.laeuft = false; this.film = 0; this.seit = 0;
    cdp.on("Page.screencastFrame", ({ data, sessionId }) => {
      cdp.send("Page.screencastFrameAck", { sessionId }).catch(() => {});
      this.letztes = Buffer.from(data, "base64");
      if (this.laeuft) this.bilder.push({ t: this.zeit(), b: this.letztes });
    });
  }
  async start() { await this.cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, maxWidth: BREITE, maxHeight: HOEHE, everyNthFrame: 1 }); }
  zeit() { return this.film + (this.laeuft ? Date.now() - this.seit : 0); }
  weiter() { // Szene beginnt: letztes Bild (die fertig geladene Seite) zur aktuellen Filmzeit
    this.seit = Date.now(); this.laeuft = true;
    if (this.letztes) this.bilder.push({ t: this.zeit(), b: this.letztes });
  }
  pause() { this.film = this.zeit(); this.laeuft = false; }
  // gleichmäßige Folge: zu jedem Zeitpunkt k/FPS das zuletzt davor gekommene Bild
  *folge() {
    const n = Math.round(this.film / 1000 * FPS);
    let i = 0;
    for (let k = 0; k < n; k++) {
      const t = k * 1000 / FPS;
      while (i + 1 < this.bilder.length && this.bilder[i + 1].t <= t) i++;
      yield this.bilder[i].b;
    }
  }
}

async function bereit(page) {
  await page.evaluate(() => document.fonts.ready);
  const mitKarte = await page.evaluate(() => !!document.getElementById("karte") || !!window.maplibregl);
  if (mitKarte) {
    await page.waitForFunction(() => window.KIEZ_KARTE && window.KIEZ_KARTE.loaded() && window.KIEZ_KARTE.areTilesLoaded(), null, { timeout: 30000 }).catch(() => console.log("  Hinweis: Karte nach 30 s nicht vollständig geladen"));
  }
}

async function kartenRuhe(page, max = 6000) {
  await page.waitForFunction(() => !window.KIEZ_KARTE || (window.KIEZ_KARTE.loaded() && window.KIEZ_KARTE.areTilesLoaded() && !window.KIEZ_KARTE.isMoving()), null, { timeout: max }).catch(() => {});
}

// Ziel eines Schritts finden (CSS-Auswahl, n-tes Element oder mit Text)
async function element(page, a) {
  const loc = page.locator(a.scrolle || a.klicke || a.hebe);
  if (a.text) return loc.filter({ hasText: a.text }).first();
  return loc.nth(a.nr || 0);
}

async function scrolle(page, a) {
  // Liegt das Ziel in einem eigenen Rollbereich (Seitenleiste neben der Karte), rollt dieser Bereich, sonst die Seite
  const el = await element(page, a);
  await el.evaluate((e, [v, ms]) => new Promise((r) => {
    let c = e.parentElement;
    while (c && c !== document.body && !(/(auto|scroll)/.test(getComputedStyle(c).overflowY) && c.scrollHeight > c.clientHeight + 4)) c = c.parentElement;
    const innen = c && c !== document.body ? c : null;
    const von = innen ? innen.scrollTop : window.scrollY;
    const ziel = innen ? Math.max(0, e.getBoundingClientRect().top - innen.getBoundingClientRect().top + innen.scrollTop - 16)
      : Math.max(0, e.getBoundingClientRect().top + window.scrollY - v);
    const t0 = performance.now(), ease = (x) => 1 - Math.pow(1 - x, 4);
    function schritt(t) {
      const x = Math.min(1, (t - t0) / ms), y = von + (ziel - von) * ease(x);
      if (innen) innen.scrollTop = y; else window.scrollTo(0, y);
      if (x < 1) requestAnimationFrame(schritt); else r();
    }
    requestAnimationFrame(schritt);
  }), [a.versatz ?? 80, a.ms ?? 1800]);
}

async function hebe(page, el, ms = 900) {
  await el.evaluate((e) => { const z = e.closest("label") || e; z.classList.add("film-hebe"); }).catch(() => {});
  setTimeout(() => el.evaluate((e) => { const z = e.closest("label") || e; z.classList.remove("film-hebe"); }).catch(() => {}), ms);
}

async function aktion(page, a) {
  if (a.scrolle) return scrolle(page, a);
  if (a.klicke) {
    const el = await element(page, a);
    await el.scrollIntoViewIfNeeded();
    await hebe(page, el);
    await warte(450);
    await el.click();
    await page.mouse.move(4, 4); // Zeiger weg von der Karte: keine Hover-Popups
    return;
  }
  if (a.waehle) {
    const sel = page.locator(a.waehle);
    await hebe(page, sel);
    await warte(450);
    let wert = a.wert;
    if (a.erste) wert = await sel.evaluate((s) => [...s.options].find((o) => o.value)?.value);
    if (a.text) wert = await sel.evaluate((s, [t, g]) => [...s.options].find((o) => o.textContent.includes(t) && o.textContent.includes(g))?.value, [a.text, a.genau || ""]);
    if (wert === undefined) throw new Error(`Auswahl ${a.waehle}: Eintrag nicht gefunden`);
    await sel.selectOption(String(wert));
    await page.mouse.move(4, 4);
    return;
  }
  if (a.hebe) {
    let el = page.locator(a.hebe).filter({ visible: true });
    if (a.text) el = el.filter({ hasText: a.text }).first();
    const n = await el.count();
    for (let i = 0; i < n; i++) await hebe(page, el.nth(i), a.dauer ?? 3200);
  }
}

async function zeigeText(page, text) {
  await page.evaluate((t) => { const u = document.getElementById("film-ut"); if (t) { u.textContent = t; u.classList.add("an"); } else u.classList.remove("an"); }, text);
}

async function zeigeTafel(page, zeilen, quellen) {
  await page.evaluate(([z, q]) => {
    const t = document.getElementById("film-tafel");
    const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
    t.className = q ? "quellen" : "";
    t.innerHTML = `<div class="marke"><i></i>Kiezatlas Kraków</div><div class="blatt"><h1>${esc(z[0])}</h1>` +
      (q ? `<ul>${z.slice(1, -1).map((x) => `<li>${esc(x)}</li>`).join("")}</ul><p>${esc(z[z.length - 1])}</p>` : `<p>${esc(z[1])}</p>`) + `</div>`;
    requestAnimationFrame(() => t.classList.add("an"));
  }, [zeilen, quellen]);
}
async function versteckeTafel(page) { await page.evaluate(() => document.getElementById("film-tafel").classList.remove("an")); }

const text = (wert, d) => (typeof wert === "function" ? wert(d) : wert);

async function film(browser, basis, f) {
  const ctx = await browser.newContext({ viewport: { width: BREITE, height: HOEHE }, deviceScaleFactor: 1, locale: "pl-PL",
    timezoneId: "Europe/Warsaw", extraHTTPHeaders: { "Accept-Language": "pl-PL,pl;q=0.9" }, reducedMotion: "no-preference" });
  await ctx.addInitScript(ZUFALL_FEST);
  const page = await ctx.newPage();
  const meldungen = [];
  page.on("console", (m) => { if (m.type() === "error") meldungen.push(m.text()); });
  page.on("pageerror", (e) => meldungen.push(String(e)));
  await page.route("**/*", (r) => { const u = r.request().url(); if (u.startsWith(basis) || u.startsWith("data:") || u.startsWith("blob:")) return r.continue(); meldungen.push("fremder Abruf abgefangen: " + u); return r.fulfill({ status: 204, body: "" }); });
  const cdp = await ctx.newCDPSession(page);
  const auf = new Aufnahme(cdp);
  await auf.start();
  const cues = []; // { start, ende, pl, en, de, tun, seite }
  let offen = null;
  const schliessen = () => { if (offen) { offen.ende = auf.zeit(); cues.push(offen); offen = null; } };

  for (const sz of f.szenen) {
    await page.goto(basis + sz.seite + ".html", { waitUntil: "load" });
    await page.evaluate(einblendungen, EINBLENDUNG_CSS);
    await bereit(page);
    if (sz.vorher) await page.evaluate(([s, v]) => { const e = document.querySelector(s); if (e) window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - v); }, [sz.vorher.scrolle, sz.vorher.versatz]);
    await page.mouse.move(4, 4);
    await kartenRuhe(page);
    const d = await page.evaluate(() => ({ okna: window.KIEZ_POWIETRZE?.okna, n: window.KIEZ_MIESZKANIA?.regeln?.mindestfallzahl }));
    // erste Tafel einer Szene schon vor dem ersten Bild zeigen (kein Aufblitzen der Seite)
    const erste = sz.schritte[0];
    if (erste.tafel) { await zeigeTafel(page, text(erste.pl, d), erste.quellen); await warte(600); }
    await warte(250);
    auf.weiter();
    for (const s of sz.schritte) {
      schliessen();
      const t0 = auf.zeit();
      const z = Object.fromEntries(SPRACHEN.map((l) => [l, text(s[l], d)]));
      for (const l of SPRACHEN) if (z[l] === undefined || /undefined|NaN/.test(String(z[l]))) throw new Error(`Film ${f.nr}: Text ${l} ohne Daten: ${z[l]}`);
      offen = { start: t0, ...z, tun: s.tun, seite: sz.seite, tafel: !!s.tafel };
      if (s.tafel) {
        await zeigeText(page, null);
        if (s !== erste) await zeigeTafel(page, z.pl, s.quellen);
        await warte(s.ms);
        if (s !== sz.schritte[sz.schritte.length - 1] || sz !== f.szenen[f.szenen.length - 1]) { await versteckeTafel(page); await warte(450); }
      } else {
        await zeigeText(page, z.pl);
        const ak = s.aktion ? (Array.isArray(s.aktion) ? s.aktion : [s.aktion]) : [];
        const t1 = Date.now();
        for (const a of ak) { await warte(500); await aktion(page, a); }
        if (ak.some((a) => a.klicke || a.waehle)) await kartenRuhe(page, Math.max(500, s.ms - (Date.now() - t1) - 300));
        const rest = s.ms - (Date.now() - t1);
        if (rest > 0) await warte(rest);
      }
    }
    schliessen();
    await zeigeText(page, null);
    await warte(380);
    auf.pause();
  }
  await cdp.send("Page.stopScreencast").catch(() => {});
  await ctx.close();
  return { auf, cues, meldungen };
}

// ---------------------------------------------------------------------------------------------------------------
// Ausgabe

const vttZeit = (ms) => {
  const h = Math.floor(ms / 3600000), m = Math.floor(ms / 60000) % 60, s = Math.floor(ms / 1000) % 60, r = Math.round(ms % 1000);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(r).padStart(3, "0")}`;
};
const HINWEIS_VTT = {
  pl: "Napisy do filmu Kiezatlas Kraków (wersja wyświetlana w filmie). Tekst nie był sprawdzony przez rodzimego użytkownika języka.",
  en: "English translation of the Polish subtitles burned into the film.",
  de: "Deutsche Übersetzung der polnischen Untertitel, die im Film eingeblendet sind.",
};

function vtt(cues, lang) {
  const teile = [`WEBVTT\n\nNOTE ${HINWEIS_VTT[lang]}`];
  cues.forEach((c, i) => {
    const t = Array.isArray(c[lang]) ? (c.tafel && c[lang].length > 2 && c[lang][0] === QUELLEN_TITEL[lang] ? `${c[lang][0]}: ${c[lang].slice(1, -1).join("; ")}. ${c[lang][c[lang].length - 1]}` : c[lang].join(". ")) : c[lang];
    teile.push(`${i + 1}\n${vttZeit(c.start)} --> ${vttZeit(c.ende)}\n${t}`);
  });
  return teile.join("\n\n") + "\n";
}

function kodieren(auf, mp4, webm) {
  return new Promise((r, f) => {
    const p = spawn("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
      "-map_metadata", "-1", "-an", "-vf", "scale=in_range=full:out_range=tv,format=yuv420p",
      "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-tune", "stillimage", "-g", String(FPS * 4), "-movflags", "+faststart", mp4,
      "-map_metadata", "-1", "-an", "-vf", "scale=in_range=full:out_range=tv,format=yuv420p",
      "-c:v", "libvpx-vp9", "-crf", "38", "-b:v", "0", "-deadline", "good", "-cpu-used", "2", "-row-mt", "1", "-g", String(FPS * 4), webm],
    { stdio: ["pipe", "inherit", "inherit"] });
    p.on("error", f);
    p.on("close", (c) => (c === 0 ? r() : f(new Error("ffmpeg Rückgabe " + c))));
    (async () => {
      for (const b of auf.folge()) { if (!p.stdin.write(b)) await new Promise((x) => p.stdin.once("drain", x)); }
      p.stdin.end();
    })().catch(f);
  });
}

function ffprobe(datei) {
  const j = JSON.parse(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration,size:stream=codec_name,width,height,r_frame_rate", "-of", "json", datei], { encoding: "utf-8" }));
  const v = j.streams.find((s) => s.width) || {};
  return { dauer: Number(j.format.duration), groesse: Number(j.format.size), codec: v.codec_name, breite: v.width, hoehe: v.height, fps: v.r_frame_rate, stroeme: j.streams.length };
}
const sha256 = (d) => crypto.createHash("sha256").update(fs.readFileSync(d)).digest("hex");
const mb = (b) => (b / 1024 / 1024).toFixed(2).replace(".", ",");
const sek = (s) => s.toFixed(1).replace(".", ",");

function vttLesen(datei) {
  const cues = [];
  for (const block of fs.readFileSync(datei, "utf-8").split(/\n\n+/)) {
    const m = /^(\d+)\n(\S+) --> (\S+)\n([\s\S]*)$/.exec(block.trim());
    if (m) cues.push({ start: m[2], ende: m[3], text: m[4].trim() });
  }
  return cues;
}

const befunde = [];
const pruef = (ok, t) => { console.log((ok ? "  ok    " : "  FEHLT ") + t); if (!ok) befunde.push(t); };

fs.mkdirSync(ZIEL, { recursive: true });
const commit = git("rev-parse", "HEAD"), sauber = git("status", "--porcelain") === "";
const { server, url: BASIS } = await starten({ port: 0 });
const browser = await chromium.launch({ args: ["--hide-scrollbars"] });
const laufInfo = {};
try {
  for (const f of FILME.filter((x) => NUR.includes(x.nr))) {
    const stamm = path.join(ZIEL, `film${f.nr}-${f.name}`);
    console.log(`Film ${f.nr} „${f.titel.pl}“`);
    const { auf, cues, meldungen } = await film(browser, BASIS, f);
    for (const m of meldungen) console.log("  Konsole: " + m);
    pruef(meldungen.length === 0, `Film ${f.nr}: keine Konsolenfehler und keine fremden Abrufe (${meldungen.length})`);
    console.log(`  ${auf.bilder.length} Bilder aufgenommen, ${sek(auf.film / 1000)} s`);
    await kodieren(auf, stamm + ".mp4", stamm + ".webm");
    for (const l of SPRACHEN) fs.writeFileSync(`${stamm}.${l}.vtt`, vtt(cues, l));
    for (const end of ["mp4", "webm"]) {
      const p = ffprobe(`${stamm}.${end}`);
      pruef(p.dauer >= DAUER_MIN && p.dauer <= DAUER_MAX, `film${f.nr}.${end}: Dauer ${sek(p.dauer)} s (${DAUER_MIN} bis ${DAUER_MAX} s)`);
      pruef(p.groesse <= GROESSE_MAX, `film${f.nr}.${end}: ${mb(p.groesse)} MB (höchstens ${mb(GROESSE_MAX)} MB)`);
      pruef(p.breite === BREITE && p.hoehe === HOEHE && p.stroeme === 1, `film${f.nr}.${end}: ${p.codec} ${p.breite} × ${p.hoehe}, ${p.stroeme} Strom (ohne Ton)`);
    }
    const letzte = cues[cues.length - 1].ende / 1000, p = ffprobe(`${stamm}.mp4`);
    pruef(letzte <= p.dauer + 0.05, `film${f.nr}: letzter Untertitel endet bei ${sek(letzte)} s, im Film (${sek(p.dauer)} s)`);
    laufInfo[f.nr] = { cues };
    if (STANDBILDER) {
      fs.mkdirSync(STANDBILDER, { recursive: true });
      cues.forEach((c, i) => {
        const mitte = ((c.start + c.ende) / 2 / 1000).toFixed(2);
        execFileSync("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", "-ss", mitte, "-i", `${stamm}.mp4`, "-frames:v", "1", "-q:v", "3",
          path.join(STANDBILDER, `film${f.nr}-${String(i + 1).padStart(2, "0")}.jpg`)]);
      });
      console.log(`  ${cues.length} Standbilder nach ${STANDBILDER}`);
    }
  }
} finally {
  await browser.close();
  server.close();
}

// README aus den Dateien auf der Platte (auch für Filme, die dieser Lauf nicht neu aufgenommen hat)
const abschnitte = [];
for (const f of FILME) {
  const stamm = `film${f.nr}-${f.name}`;
  if (!fs.existsSync(path.join(ZIEL, stamm + ".mp4"))) { abschnitte.push(`## Film ${f.nr}: ${f.titel.pl}\n\nNoch nicht aufgenommen.\n`); continue; }
  const dateien = ["mp4", "webm", "pl.vtt", "en.vtt", "de.vtt"].map((e) => `${stamm}.${e}`);
  const zeilen = dateien.map((d) => {
    const p = path.join(ZIEL, d), g = fs.statSync(p).size;
    const pr = d.endsWith(".vtt") ? null : ffprobe(p);
    return `| \`${d}\` | ${pr ? `${pr.codec}, ${pr.breite} × ${pr.hoehe}, ${sek(pr.dauer)} s` : "WebVTT"} | ${pr ? mb(g) + " MB" : (g / 1024).toFixed(1).replace(".", ",") + " kB"} | \`${sha256(p)}\` |`;
  });
  const pl = vttLesen(path.join(ZIEL, `${stamm}.pl.vtt`));
  const schritte = f.szenen.flatMap((sz) => sz.schritte.map((s) => ({ seite: sz.seite, tun: s.tun })));
  const buch = pl.map((c, i) => `| ${i + 1} | ${c.start.slice(3, 8)}–${c.ende.slice(3, 8)} | \`${schritte[i]?.seite ?? "?"}.html\` | ${schritte[i]?.tun ?? ""} | ${c.text.replace(/\|/g, "\\|").replace(/\n/g, " ")} |`);
  abschnitte.push(`## Film ${f.nr}: ${f.titel.pl}

${f.titel.en} / ${f.titel.de}

| Datei | Format | Größe | SHA256 |
|---|---|---|---|
${zeilen.join("\n")}

Drehbuch (Zeiten aus \`${stamm}.pl.vtt\`, Minuten:Sekunden):

| # | Zeit | Seite | Bild | Untertitel (pl) |
|---|---|---|---|---|
${buch.join("\n")}
`);
}
const readme = `# Filme: Kiezatlas Kraków in drei kurzen Filmen (polnisch)

Erzeugt von \`skripte/filme.mjs\` (nicht von Hand ändern) auf Commit \`${commit.slice(0, 7)}\`
(${sauber ? "sauberer Arbeitsstand" : "mit offenen Änderungen"}).

**PL** Trzy krótkie filmy bez dźwięku, nagrane z prawdziwych stron atlasu, z napisami po polsku. Tekst nie był
sprawdzony przez rodzimego użytkownika języka.

**DE** Drei kurze Filme ohne Ton, aufgenommen aus den echten Seiten des Atlas, mit eingeblendeten polnischen
Untertiteln und Texttafeln. Tekst nie był sprawdzony przez rodzimego użytkownika języka: Die polnischen Texte hat
keine Muttersprachlerin und kein Muttersprachler geprüft; Begriffe nach \`docs/glossar-pl.md\` (Status Vorschlag).
Untertitel als WebVTT: Polnisch wie eingeblendet, dazu Englisch und Deutsch mit denselben Zeiten. Eigennamen
bleiben polnisch.

Befehl (aus dem Wurzelordner, braucht den Kachelordner der Grundkarte wie \`skripte/entwicklung_server.mjs\`,
Playwright mit Chromium und ffmpeg mit libx264 und libvpx-vp9):

\`\`\`sh
node skripte/filme.mjs --ziel belege/filme [--nur 1,2,3] [--standbilder ORDNER]
\`\`\`

So entsteht ein Film: headless Chromium öffnet die Seiten über den Entwicklungsserver (nur 127.0.0.1, fremde Abrufe
werden abgefangen), Ansicht 1280 × 720 px, Pixelverhältnis 1, Sprache pl-PL. Bilder kommen aus dem Bildschirm-Streaming
des Browsers (JPEG) und gehen als Folge mit ${FPS} Bildern je Sekunde an ffmpeg: MP4 (H.264, CRF 28, yuv420p,
faststart) und WebM (VP9, CRF 38) aus derselben Bildfolge, ohne Tonspur. Seitenwechsel und Ladezeiten sind
herausgeschnitten. Untertitel und Tafeln sind Einblendungen in der Seite (Barlow, Farben aus \`DESIGN.md\`, kein
Orange). Zahlen in den Untertiteln kommen beim Lauf aus den Datendateien (\`KIEZ_POWIETRZE.okna\`,
\`KIEZ_MIESZKANIA.regeln.mindestfallzahl\`), nicht aus dem Skript.

Wiederholbar, nicht bitgleich: dasselbe Drehbuch, feste Wartezeiten, \`Math.random\` mit festem Startwert. Ladezeiten
und Bildtakt des Browsers schwanken, darum weichen einzelne Bilder und damit die Prüfsummen zwischen zwei Läufen ab;
die SHA256 unten gelten für genau diese Dateien. Das Skript prüft jeden neu aufgenommenen Film mit ffprobe (Dauer
${DAUER_MIN} bis ${DAUER_MAX} s, je Datei höchstens ${mb(GROESSE_MAX)} MB, ${BREITE} × ${HOEHE}, ein Strom ohne Ton) und meldet Konsolenfehler.

Was die Filme nicht zeigen: keine Personen, keine einzelnen Transaktionen aus dem Rejestr cen nieruchomości, keine
Einzelgebäude aus dem Wykaz ZBK (die Ebene mit den Gebäudepunkten bleibt aus, die Karte wird nicht angeklickt, der
Zeiger steht außerhalb der Karte). Der Vergleich in Film 1 ist die Seite \`porownanie.html\` („Kraków i Poczdam“),
die die Seite selbst Porównanie nennt; der Rang einer dzielnica unter allen dzielnice steht im Steckbrief davor.
Film 3 zeigt die Luftwerte vor und nach der uchwała antysmogowa ausdrücklich nur als zeitlichen Vergleich, nicht als
Ursache.

Lizenz: CC BY 4.0 wie die Bildschirmfotos unter \`belege/\`, Namensnennung „Kiezatlas Kraków, CC BY 4.0“. Die Filme
zeigen eigene Seiten mit Daten aus den genannten Quellen (OpenStreetMap: das Bild ist ein „Produced Work“ im Sinn der
ODbL 1.0); die Quellentafel am Ende jedes Films nennt sie mit Namensnennung, die vollständigen Vermerke stehen auf der
Seite \`dane.html\`.

${abschnitte.join("\n")}`;
fs.writeFileSync(path.join(ZIEL, "README.md"), readme);
console.log(`README ${path.relative(WURZEL, path.join(ZIEL, "README.md"))}; ${befunde.length ? befunde.length + " Befund(e)" : "alle Vorgaben erfüllt"}`);
process.exit(befunde.length ? 1 : 0);
