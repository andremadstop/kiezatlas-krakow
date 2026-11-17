"""Bedeutung der Felder und Werte in den Downloads des Kiezatlas Kraków, je Sprache (pl, en, de).

Genutzt von skripte/16_export_krakow.py (Liesmich, pola.csv, wartosci.csv, Tabellen pola und wartosci in beiden
GeoPackages) und von pruefen/S4_export.py (jede Spalte jeder Ebene und jeder Wert der Kategorienfelder hat eine
Erklärung in allen drei Sprachen).

Grundlage der Erklärungen sind die Verträge unter daten/schema/*.json und die erzeugenden Skripte (in Klammern je
Gruppe). Zahlen in den Erklärungen (Schwellen, Radien, Klassengrenzen) kommen aus den Datendateien, nicht aus diesem
Text; sie werden über `kontext()` eingesetzt. Feldnamen bleiben, wie sie in den Datendateien stehen (gleiche Werte in
Seiten und Downloads).
"""
from __future__ import annotations

import re

import ort_konfig

P = tuple  # (pl, en, de)


def _zahl(x, lang: str) -> str:
    s = f"{x:g}" if isinstance(x, float) else str(x)
    return s.replace(".", ",") if lang in ("pl", "de") else s


def kontext(D) -> dict:
    """Zahlen und Namen aus den Datendateien, die in den Erklärungen stehen."""
    sa = D["sanierung"]["typologie"]["kriterien"]
    hs = D["haltestellen"]
    gr = hs["klassen"]["grenzen"]
    radien = {}
    for datei in ("planer_odbl", "planer_fuss_odbl"):
        for r in D[datei]["raeume"].values():
            for w in r["werte"]:
                if w.get("radius_m") is not None and w["kennzahl"] in ("oepnv_takt", "gruen_in_radius"):
                    radien.setdefault((w["kennzahl"], w["methode"]), set()).add(int(w["radius_m"]))
    for k, v in radien.items():
        if len(v) != 1:
            raise SystemExit(f"Radius {k} nicht eindeutig: {sorted(v)}")
    return {
        "gruppen": {nr: g["name"] for nr, g in D["steckbrief"]["gruppen"].items()},
        "typ": sa,
        "fenster": hs["fenster"],
        "grenzen": gr,
        "radien": {k: v.pop() for k, v in radien.items()},
        "geb_min": D["gebaeude_kennzahlen"]["methode"]["mindestfallzahl"],
        "klimat_min_ha": D["klimat_zellen"]["mindestflaeche_ha"],
        "geschoss_m": D["gebaeude_kennzahlen"]["methode"]["geschoss_hoehe_m"],
        "srid": ort_konfig.RECHEN_SRID,
    }


# ------------------------------------------------------------------------------------------------- Bausteine
KST = {  # Kod KŚT (Tabela 26 Rozporządzenia BDOT10k); Wortlaut aus den Texten des Pakets Gebäude (gebaeude.kst.*)
    "101": ("budynki przemysłowe", "industrial buildings", "Industriegebäude"),
    "102": ("budynki transportu i łączności", "transport and communication buildings", "Verkehrs- und Fernmeldegebäude"),
    "103": ("budynki handlowo-usługowe", "retail and service buildings", "Handels- und Dienstleistungsgebäude"),
    "104": ("zbiorniki, silosy i budynki magazynowe", "tanks, silos and warehouses", "Behälter, Silos und Lagergebäude"),
    "105": ("budynki biurowe", "office buildings", "Bürogebäude"),
    "106": ("budynki szpitali i inne budynki opieki zdrowotnej", "hospitals and other healthcare buildings",
            "Krankenhäuser und andere Gesundheitsbauten"),
    "107": ("budynki oświaty, nauki i kultury oraz budynki sportowe", "education, science, culture and sports buildings",
            "Bildungs-, Wissenschafts-, Kultur- und Sportgebäude"),
    "108": ("budynki produkcyjne, usługowe i gospodarcze dla rolnictwa", "agricultural buildings (production, service, utility)",
            "landwirtschaftliche Betriebs- und Wirtschaftsgebäude"),
    "109": ("pozostałe budynki niemieszkalne", "other non-residential buildings", "sonstige Nichtwohngebäude"),
    "110": ("budynki mieszkalne", "residential buildings", "Wohngebäude"),
}
ZUSTAND = {  # KAT_ISTNIE (kategoria istnienia), skripte/20_bdot10k.py
    "eksploatowany": ("eksploatowany", "in use (eksploatowany)", "in Nutzung (eksploatowany)"),
    "w_budowie": ("w budowie", "under construction (w budowie)", "im Bau (w budowie)"),
    "nieczynny": ("nieczynny", "disused (nieczynny)", "außer Betrieb (nieczynny)"),
    "zniszczony": ("zniszczony", "destroyed (zniszczony)", "zerstört (zniszczony)"),
    "leer": ("brak wartości", "no value", "ohne Angabe"),
}
GESCHOSSE = {  # Klassen von LICZ_KONDY, skripte/20_bdot10k.py GESCHOSS_KLASSEN
    "1": ("1 kondygnacja", "1 storey", "1 Geschoss"),
    "2": ("2 kondygnacje", "2 storeys", "2 Geschosse"),
    "3_4": ("3–4 kondygnacje", "3–4 storeys", "3–4 Geschosse"),
    "5_10": ("5–10 kondygnacji", "5–10 storeys", "5–10 Geschosse"),
    "11p": ("11 i więcej kondygnacji", "11 or more storeys", "11 und mehr Geschosse"),
    "unbekannt": ("liczba kondygnacji nieznana", "number of storeys unknown", "Geschosszahl unbekannt"),
}
KLASSE = {  # Bodenbedeckung, skripte/35_klimat.py SCHICHT_KLASSE (BDOT10k-Schichten in Klammern)
    "bebauung": ("zabudowa (PTZB)", "built-up land (PTZB)", "Bebauung (PTZB)"),
    "verkehr": ("tereny komunikacyjne i place (PTKM, PTPL)", "transport land and squares (PTKM, PTPL)",
                "Verkehrsflächen und Plätze (PTKM, PTPL)"),
    "gruen": ("zieleń (PTRK, PTUT, roślinność trawiasta z PTTR)", "green space (PTRK, PTUT, grassland from PTTR)",
              "Grün (PTRK, PTUT, Grasland aus PTTR)"),
    "wald": ("lasy i zadrzewienia (PTLZ)", "woodland (PTLZ)", "Wald und Gehölze (PTLZ)"),
    "wasser": ("wody (PTWP)", "water (PTWP)", "Wasser (PTWP)"),
    "acker": ("grunty orne (uprawy z PTTR)", "arable land (crops from PTTR)", "Acker (Anbau aus PTTR)"),
    "sonstige": ("pozostałe (PTGN, PTSO, PTWZ, PTNZ)", "other (PTGN, PTSO, PTWZ, PTNZ)", "Sonstiges (PTGN, PTSO, PTWZ, PTNZ)"),
    "bebauung_verkehr": ("zabudowa i tereny komunikacyjne razem", "built-up and transport land together",
                         "Bebauung und Verkehr zusammen"),
    "gruen_wald": ("zieleń i lasy razem", "green space and woodland together", "Grün und Wald zusammen"),
}
ZIEL = {  # Ziele der Entfernungen und Arten der Einrichtungen (skripte/11_einrichtungen_krakow.py, 12_osm.py)
    "haltestelle_takt": ("przystanek klasy częstotliwości kursowania I lub II", "stop of service frequency class I or II",
                         "Haltestelle der Taktklasse I oder II"),
    "park": ("park lub skwer (BDOT10k)", "park or square (BDOT10k)", "Park oder Grünanlage (BDOT10k, park lub skwer)"),
    "przedszkole": ("przedszkole", "kindergarten (przedszkole)", "Kindergarten (przedszkole)"),
    "szkola": ("szkoła dowolnego typu (BDOT10k nie rozróżnia typów)", "school of any type (BDOT10k does not distinguish)",
               "Schule jeder Art (BDOT10k trennt nicht)"),
    "szpital": ("szpital", "hospital (szpital)", "Krankenhaus (szpital)"),
    "zlobek": ("żłobek", "nursery (żłobek)", "Krippe (żłobek)"),
    "apotheke": ("apteka (OSM)", "pharmacy (OSM)", "Apotheke (OSM)"),
    "arzt": ("lekarz lub przychodnia (OSM amenity=doctors)", "doctor or practice (OSM amenity=doctors)",
             "Arzt oder Praxis (OSM amenity=doctors)"),
    "pflege": ("dom opieki (OSM)", "care home (OSM)", "Pflegeheim (OSM)"),
    "spielplatz": ("plac zabaw ogólnodostępny (OSM)", "public playground (OSM)", "öffentlicher Spielplatz (OSM)"),
    "supermarkt": ("supermarket lub sklep spożywczy (OSM)", "supermarket or convenience store (OSM)",
                   "Supermarkt oder Lebensmittelladen (OSM)"),
}
ZBK_ART = {  # Rodzaj budynku in der ZBK-Liste (pruefen/DS_protokoll.md); Buchstaben in der Reihenfolge M, U, P
    "M": ("mieszkalny", "residential (M)", "Wohnen (M)"),
    "U": ("użytkowy", "non-residential use (U)", "Nutzung ohne Wohnen (U)"),
    "P": ("przychodnia", "health clinic (P)", "Ambulanz (P)"),
    "MU": ("mieszkalny i użytkowy", "residential and non-residential (MU)", "Wohnen und Nutzung (MU)"),
    "MP": ("mieszkalny i przychodnia", "residential and clinic (MP)", "Wohnen und Ambulanz (MP)"),
    "UP": ("użytkowy i przychodnia", "non-residential and clinic (UP)", "Nutzung und Ambulanz (UP)"),
    "MUP": ("mieszkalny, użytkowy i przychodnia", "residential, non-residential and clinic (MUP)",
            "Wohnen, Nutzung und Ambulanz (MUP)"),
}
EIGENTUM = {  # skripte/36_sanierung.py eigentum_von
    "gmina": ("Gmina Miejska Kraków", "City of Kraków (Gmina Miejska Kraków)", "Stadt Kraków (Gmina Miejska Kraków)"),
    "skarb_panstwa": ("Skarb Państwa", "State Treasury (Skarb Państwa)", "Staatskasse (Skarb Państwa)"),
    "publiczne_mieszane": ("kilku właścicieli publicznych albo województwo", "several public owners or the voivodeship",
                           "mehrere öffentliche Eigentümer oder die Woiwodschaft"),
    "z_prywatnymi": ("własność publiczna z udziałem osób prywatnych", "public ownership with private co-owners",
                     "öffentlich mit privaten Miteigentümern"),
    "prywatne": ("tylko właściciele prywatni", "private owners only", "nur private Eigentümer"),
    "brak": ("własności nie da się przypisać", "ownership cannot be classified", "Eigentum nicht zuzuordnen"),
}
JA = ("1 = tak, 0 = nie", "1 = yes, 0 = no", "1 = ja, 0 = nein")


def _p(pl: str, en: str, de: str) -> P:
    return (pl, en, de)


def _mit(t: P, vor: P = ("", "", ""), nach: P = ("", "", "")) -> P:
    return tuple(f"{v}{x}{n}" for v, x, n in zip(vor, t, nach))


# ------------------------------------------------------------------------------------------------- Familien
def _nsp(s: str) -> P | None:
    m = re.fullmatch(r"alter_10_a(\d+)_(\d+)", s)
    if m:
        a, b = m.groups()
        return _p(f"NSP 2021: mieszkańcy w wieku {a}–{b} lat", f"NSP 2021: residents aged {a}–{b}",
                  f"NSP 2021: Einwohner von {a} bis {b} Jahren")
    m = re.fullmatch(r"alter_10_a(\d+)p", s)
    if m:
        a = m.group(1)
        return _p(f"NSP 2021: mieszkańcy w wieku {a} lat i więcej", f"NSP 2021: residents aged {a} and over",
                  f"NSP 2021: Einwohner ab {a} Jahren")
    return {
        "einwohner": _p("NSP 2021: liczba mieszkańców", "NSP 2021: residents", "NSP 2021: Einwohner"),
        "maenner": _p("NSP 2021: mężczyźni", "NSP 2021: men", "NSP 2021: Männer"),
        "frauen": _p("NSP 2021: kobiety", "NSP 2021: women", "NSP 2021: Frauen"),
        "oekonomisch_vor": _p("NSP 2021: mieszkańcy w wieku przedprodukcyjnym", "NSP 2021: residents of pre-working age",
                              "NSP 2021: Einwohner im vorerwerbsfähigen Alter"),
        "oekonomisch_erwerb": _p("NSP 2021: mieszkańcy w wieku produkcyjnym", "NSP 2021: residents of working age",
                                 "NSP 2021: Einwohner im erwerbsfähigen Alter"),
        "oekonomisch_nach": _p("NSP 2021: mieszkańcy w wieku poprodukcyjnym", "NSP 2021: residents of post-working age",
                               "NSP 2021: Einwohner im nacherwerbsfähigen Alter"),
        "q_u20": _p("NSP 2021: udział mieszkańców poniżej 20 lat, %", "NSP 2021: share of residents under 20, %",
                    "NSP 2021: Anteil unter 20 Jahren, %"),
        "q_60p": _p("NSP 2021: udział mieszkańców w wieku 60 lat i więcej, %", "NSP 2021: share of residents aged 60 and over, %",
                    "NSP 2021: Anteil ab 60 Jahren, %"),
        "q_nach": _p("NSP 2021: udział mieszkańców w wieku poprodukcyjnym, %", "NSP 2021: share of residents of post-working age, %",
                     "NSP 2021: Anteil im nacherwerbsfähigen Alter, %"),
        "rejony": _p("NSP 2021: liczba rejonów statystycznych", "NSP 2021: number of statistical areas (rejony statystyczne)",
                     "NSP 2021: Zahl der rejony statystyczne"),
    }.get(s)


def _gitter(s: str) -> P | None:
    return {
        "zellen": _p("siatka Eurostatu: liczba komórek 1 km, których środek leży w jednostce",
                     "Eurostat grid: number of 1 km cells whose centre lies in the unit",
                     "Eurostat-Gitter: Zahl der 1-km-Zellen mit Mittelpunkt in der Einheit"),
        "einwohner": _p("siatka Eurostatu: mieszkańcy (suma liczby mieszkańców komórek przypisanych według ich środka)",
                        "Eurostat grid: residents (sum of cells by their centre)",
                        "Eurostat-Gitter: Einwohner (Summe der Zellen nach ihrem Mittelpunkt)"),
        "u15": _p("siatka Eurostatu: mieszkańcy poniżej 15 lat", "Eurostat grid: residents under 15",
                  "Eurostat-Gitter: Einwohner unter 15 Jahren"),
        "a15_64": _p("siatka Eurostatu: mieszkańcy w wieku 15–64 lata", "Eurostat grid: residents aged 15–64",
                     "Eurostat-Gitter: Einwohner von 15 bis 64 Jahren"),
        "a65p": _p("siatka Eurostatu: mieszkańcy w wieku 65 lat i więcej", "Eurostat grid: residents aged 65 and over",
                   "Eurostat-Gitter: Einwohner ab 65 Jahren"),
        "a_ges": _p("siatka Eurostatu: suma trzech grup wieku (może nieznacznie odbiegać od liczby mieszkańców)",
                    "Eurostat grid: sum of the three age groups (may differ slightly from the residents)",
                    "Eurostat-Gitter: Summe der drei Altersgruppen (kann leicht von den Einwohnern abweichen)"),
        "q_u15": _p("siatka Eurostatu: udział mieszkańców poniżej 15 lat w sumie grup wieku, %",
                    "Eurostat grid: share under 15 in the sum of age groups, %",
                    "Eurostat-Gitter: Anteil unter 15 Jahren an der Summe der Altersgruppen, %"),
        "q_65p": _p("siatka Eurostatu: udział mieszkańców w wieku 65 lat i więcej w sumie grup wieku, %",
                    "Eurostat grid: share aged 65 and over in the sum of age groups, %",
                    "Eurostat-Gitter: Anteil ab 65 Jahren an der Summe der Altersgruppen, %"),
        "einwohner_flaechenanteil": _p("siatka Eurostatu: mieszkańcy według udziału powierzchni komórek w jednostce (porównanie)",
                                       "Eurostat grid: residents by the area share of cells in the unit (comparison)",
                                       "Eurostat-Gitter: Einwohner nach Flächenanteil der Zellen (Vergleich)"),
        "abweichung_nsp_proz": _p("różnica liczby mieszkańców z siatki względem NSP 2021, %; puste bez NSP",
                                  "difference of grid residents from NSP 2021, %; empty without NSP",
                                  "Abweichung der Gitter-Einwohner vom NSP 2021, %; leer ohne NSP"),
        "zellen_beruehrt": _p("liczba komórek, które choćby częściowo leżą w jednostce",
                              "number of cells that lie at least partly in the unit",
                              "Zahl der Zellen, die wenigstens teilweise in der Einheit liegen"),
        "spanne_proz": _p("różnica między wynikami przypisania według powierzchni i według środka, % (miara niepewności na granicach, nie błąd)",
                          "difference between the area rule and the centre rule, % (blur at the boundaries, not an error)",
                          "Spanne zwischen Flächenanteil und Mittelpunkt, % (Unschärfe an den Grenzen, kein Fehler)"),
    }.get(s)


def _geb(s: str, k: dict) -> P | None:
    m = re.fullmatch(r"zustand_(\w+)", s)
    if m and m.group(1) in ZUSTAND:
        return _mit(ZUSTAND[m.group(1)], ("BDOT10k: budynki o kategorii istnienia: ", "BDOT10k: buildings with status: ",
                                          "BDOT10k: Gebäude mit Bestandsstatus: "))
    m = re.fullmatch(r"funktion_(\d{3})", s)
    if m and m.group(1) in KST:
        c = m.group(1)
        return _mit(KST[c], (f"BDOT10k: budynki o kodzie KŚT {c}: ", f"BDOT10k: buildings with KŚT code {c}: ",
                             f"BDOT10k: Gebäude mit KŚT-Code {c}: "))
    m = re.fullmatch(r"geschosse(_wohn)?_(\w+)", s)
    if m and m.group(2) in GESCHOSSE:
        wohn = m.group(1)
        vor = ("BDOT10k: budynki mieszkalne: ", "BDOT10k: residential buildings: ", "BDOT10k: Wohngebäude: ") if wohn \
            else ("BDOT10k: budynki: ", "BDOT10k: buildings: ", "BDOT10k: Gebäude: ")
        return _mit(GESCHOSSE[m.group(2)], vor)
    n = k["geb_min"]
    lage = {
        "geschosse_median": ("mediana", "median", "Median"), "geschosse_mittel": ("średnia", "mean", "Mittel"),
        "geschosse_median_wohn": ("mediana", "median", "Median"), "geschosse_mittel_wohn": ("średnia", "mean", "Mittel"),
    }
    if s in lage:
        l = lage[s]
        w = s.endswith("_wohn")
        return _p(f"BDOT10k: {l[0]} liczby kondygnacji nadziemnych{' budynków mieszkalnych' if w else ''}; puste poniżej {n} budynków o znanej liczbie kondygnacji",
                  f"BDOT10k: {l[1]} number of storeys above ground{' of residential buildings' if w else ''}; empty below {n} buildings with known storeys",
                  f"BDOT10k: {l[2]} der oberirdischen Geschosse{' der Wohngebäude' if w else ''}; leer unter {n} Gebäuden mit bekannter Geschosszahl")
    return {
        "anzahl": _p("BDOT10k: budynki (OT_BUBD_A) z punktem wewnętrznym w jednostce, wszystkie kategorie istnienia",
                     "BDOT10k: buildings (OT_BUBD_A) with their inner point in the unit, all statuses",
                     "BDOT10k: Gebäude (OT_BUBD_A) mit innerem Punkt in der Einheit, jeder Bestandsstatus"),
        "funktion_unbekannt": _p("BDOT10k: budynki bez kodu KŚT", "BDOT10k: buildings without a KŚT code",
                                 "BDOT10k: Gebäude ohne KŚT-Code"),
        "wohngebaeude": _p("BDOT10k: budynki mieszkalne (KŚT 110)", "BDOT10k: residential buildings (KŚT 110)",
                           "BDOT10k: Wohngebäude (KŚT 110)"),
        "wohn_art_ein": _p("BDOT10k: budynki mieszkalne jednorodzinne (PFBUD)", "BDOT10k: single-family residential buildings (PFBUD)",
                           "BDOT10k: Einfamilienhäuser (PFBUD)"),
        "wohn_art_mehr": _p("BDOT10k: budynki mieszkalne wielorodzinne (PFBUD)", "BDOT10k: multi-family residential buildings (PFBUD)",
                            "BDOT10k: Mehrfamilienhäuser (PFBUD)"),
        "wohn_art_sonst": _p("BDOT10k: pozostałe budynki mieszkalne (PFBUD)", "BDOT10k: other residential buildings (PFBUD)",
                             "BDOT10k: sonstige Wohngebäude (PFBUD)"),
        "grundflaeche_m2": _p("BDOT10k: suma powierzchni obrysów budynków bez zniszczonych, m²",
                              "BDOT10k: total building footprint without destroyed buildings, m²",
                              "BDOT10k: Summe der Grundflächen ohne zerstörte Gebäude, m²"),
        "grundflaeche_wohn_m2": _p("BDOT10k: suma powierzchni obrysów budynków mieszkalnych, m²",
                                   "BDOT10k: total footprint of residential buildings, m²",
                                   "BDOT10k: Summe der Grundflächen der Wohngebäude, m²"),
        "flaeche_m2": _p("powierzchnia jednostki, m²", "area of the unit, m²", "Fläche der Einheit, m²"),
        "bebauungsdichte_wert": _p("wskaźnik zabudowy (udział powierzchni zabudowy w powierzchni jednostki): 100 × zaehler / nenner, %", "building coverage: 100 × zaehler / nenner, %",
                                   "Bebauungsdichte: 100 × zaehler / nenner, %"),
        "bebauungsdichte_zaehler": _p("licznik: powierzchnia obrysów budynków, m²", "numerator: building footprint, m²",
                                      "Zähler: Grundfläche der Gebäude, m²"),
        "bebauungsdichte_nenner": _p("mianownik: powierzchnia jednostki, m²", "denominator: area of the unit, m²",
                                     "Nenner: Fläche der Einheit, m²"),
        "bebauungsdichte_anzeige": _p("sposób prezentacji wartości", "how the value is shown", "Darstellung des Werts"),
        "geschossflaeche_naeherung_wert": _p("przybliżona intensywność zabudowy: Σ(powierzchnia obrysu × liczba kondygnacji) / powierzchnia jednostki; orientacyjnie, nie wartość urzędowa",
                                             "approximate floor area ratio: Σ(footprint × storeys) / area of the unit; for orientation, not an official value",
                                             "Näherung der Geschossflächenzahl: Σ(Grundfläche × Geschosse) / Fläche; Orientierung, keine amtliche GFZ"),
        "geschossflaeche_naeherung_zaehler": _p("licznik: Σ(powierzchnia obrysu × liczba kondygnacji), m²", "numerator: Σ(footprint × storeys), m²",
                                                "Zähler: Σ(Grundfläche × Geschosse), m²"),
        "geschossflaeche_naeherung_nenner": _p("mianownik: powierzchnia jednostki, m²", "denominator: area of the unit, m²",
                                               "Nenner: Fläche der Einheit, m²"),
        "geschossflaeche_naeherung_abzeichen": _p("oznaczenie wartości", "label of the value", "Kennzeichnung des Werts"),
    }.get(s)


def _klimat(s: str, k: dict) -> P | None:
    m = re.fullmatch(r"ha_(\w+)", s)
    if m and m.group(1) in KLASSE:
        return _mit(KLASSE[m.group(1)], ("BDOT10k: powierzchnia klasy pokrycia terenu: ", "BDOT10k: area of land cover class: ",
                                         "BDOT10k: Fläche der Bodenbedeckungsklasse: "), (", ha", ", ha", ", ha"))
    m = re.fullmatch(r"anteil_(\w+)", s)
    if m and m.group(1) in KLASSE:
        return _mit(KLASSE[m.group(1)], ("BDOT10k: udział w sumie klas pokrycia terenu: ", "BDOT10k: share of the land cover total: ",
                                         "BDOT10k: Anteil an der Summe der Bodenbedeckung: "), (", %", ", %", ", %"))
    h = _zahl(k["klimat_min_ha"], "pl"), _zahl(k["klimat_min_ha"], "en"), _zahl(k["klimat_min_ha"], "de")
    return {
        "flaeche_ha": _p("powierzchnia jednostki w granicach miasta, ha", "area of the unit within the city, ha",
                         "Fläche der Einheit in der Stadtgrenze, ha"),
        "flaeche_stadt_ha": _p("powierzchnia komórki w granicach miasta, ha", "area of the cell within the city, ha",
                               "Fläche der Zelle in der Stadtgrenze, ha"),
        "anteil_stadt": _p("udział komórki leżący w granicach miasta, %", "share of the cell within the city, %",
                           "Anteil der Zelle in der Stadtgrenze, %"),
        "abdeckung": _p("udział powierzchni jednostki objęty klasami pokrycia terenu BDOT10k, %",
                        "share of the unit covered by BDOT10k land cover classes, %",
                        "Anteil der Einheit, den die Bodenbedeckungsklassen der BDOT10k abdecken, %"),
        "anteil": _p("pole techniczne, zawsze puste; udziały są w kolumnach anteil_*", "technical field, always empty; shares are in the anteil_* columns",
                     "technisches Feld, immer leer; die Anteile stehen in den Spalten anteil_*"),
        "anteil_grund": _p(f"powód pustych udziałów (powierzchnia w mieście poniżej {h[0]} ha)",
                           f"reason for empty shares (area within the city below {h[1]} ha)",
                           f"Grund für leere Anteile (Fläche in der Stadt unter {h[2]} ha)"),
        "einwohner": _p("mieszkańcy z siatki Eurostatu, podstawa dla zieleni na mieszkańca",
                        "residents from the Eurostat grid, basis for green space per resident",
                        "Einwohner aus dem Eurostat-Gitter, Bezug für Grün je Einwohner"),
        "gruen_je_ew": _p("zieleń i lasy na mieszkańca, m²", "green space and woodland per resident, m²",
                          "Grün und Wald je Einwohner, m²"),
    }.get(s)


def _typ(s: str, k: dict) -> P | None:
    t = k["typ"]
    gs, fl, r, u, n = t["geschosse_min"], t["flaeche_min_m2"], t["rechteckigkeit_min"], t["umkreis_m"], t["nachbarn_min"]
    return {
        "mfh": _p("budynki wielorodzinne eksploatowane (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny)",
                  "multi-family buildings in use (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny)",
                  "Mehrfamilienhäuser in Nutzung (BDOT10k: KAT_ISTNIE = eksploatowany, PFBUD = budynek wielorodzinny)"),
        "blok": _p(f"szacunek: w tym kandydaci na bloki (liczba kondygnacji co najmniej {gs}, powierzchnia obrysu co najmniej {fl} m², prostokątność co najmniej {_zahl(r, 'pl')}); łącznie z kategorią osiedle",
                   f"estimate: block candidates among them (at least {gs} storeys, footprint at least {fl} m², rectangularity at least {_zahl(r, 'en')}); includes osiedle",
                   f"Schätzung: Block-Kandidaten darunter (mindestens {gs} Geschosse, Grundfläche mindestens {fl} m², Rechteckigkeit mindestens {_zahl(r, 'de')}); einschließlich osiedle"),
        "osiedle": _p(f"szacunek: kandydaci na blok na osiedlu blokowym (liczba innych kandydatów w promieniu {u} m co najmniej {n})",
                      f"estimate: block candidates in a large housing estate (at least {n} other candidates within {u} m)",
                      f"Schätzung: Block-Kandidaten in einer Großsiedlung (mindestens {n} weitere Kandidaten im Umkreis von {u} m)"),
        "blok_angebaut": _p("wskazówka, nie reguła: kandydaci na blok ze wspólną granicą o długości co najmniej 3 m z innym budynkiem BDOT10k (zabudowa pierzejowa, typowa dla kamienic)",
                            "indicator, not a rule: block candidates sharing at least 3 m of boundary with another BDOT10k building (perimeter block, typical of kamienice)",
                            "Hinweis, keine Regel: Block-Kandidaten mit mindestens 3 m gemeinsamer Grenze zu einem anderen BDOT10k-Gebäude (Blockrand, typisch für kamienice)"),
        "osiedle_angebaut": _p("jak blok_angebaut, tylko kandydaci na osiedlu blokowym",
                               "as blok_angebaut, only candidates in a large housing estate",
                               "wie blok_angebaut, nur Kandidaten in einer Großsiedlung"),
    }.get(s)


def _bdot_denkmal(s: str) -> P | None:
    return {
        "wohngebaeude": _p("BDOT10k: budynki mieszkalne (FOBUD)", "BDOT10k: residential buildings (FOBUD)", "BDOT10k: Wohngebäude (FOBUD)"),
        "mehrfamilienhaeuser": _p("BDOT10k: budynki wielorodzinne (PFBUD)", "BDOT10k: multi-family buildings (PFBUD)",
                                  "BDOT10k: Mehrfamilienhäuser (PFBUD)"),
        "namensbezug": _p("BDOT10k: budynki o nazwie „Kamienica …”", "BDOT10k: buildings named “Kamienica …”",
                          "BDOT10k: Gebäude mit dem Namen „Kamienica …“"),
    }.get(s)


# ------------------------------------------------------------------------------------------------- Einzelfelder
def _einzeln(w: str, f: str, k: dict) -> P | None:
    gruppen = k["gruppen"]
    gtext = ", ".join(f"{i} = {n}" for i, n in sorted(gruppen.items()))
    zelle = _p("kod komórki siatki Eurostatu 1 km (EPSG:3035, narożnik południowo-zachodni)",
               "code of the 1 km Eurostat grid cell (EPSG:3035, south-west corner)",
               "Kennung der 1-km-Zelle im Eurostat-Gitter (EPSG:3035, Südwestecke)")
    dz = _p("numer dzielnicy (01–18)", "district number (01–18)", "Nummer der dzielnica (01–18)")
    delg = _p("delegatura (nazwa z BDOT10k); puste = bez przypisania", "delegatura (name from BDOT10k); empty = not assigned",
              "delegatura (Name aus BDOT10k); leer = nicht zugeordnet")
    fe = k["fenster"]
    sr = k["srid"]
    tabela = {
        ("*", "teryt"): _p("identyfikator TERYT", "TERYT code", "TERYT-Kennung"),
        ("*", "nazwa"): _p("nazwa (polska nazwa własna)", "name (Polish proper name)", "Name (polnischer Eigenname)"),
        ("delegatury", "gruppe"): _p(f"numer delegatury w atlasie: {gtext}", f"number of the delegatura in the atlas: {gtext}",
                                     f"Nummer der delegatura im Atlas: {gtext}"),
        ("dzielnice", "gruppe"): _p(f"delegatura, do której należy dzielnica: {gtext}", f"delegatura the district belongs to: {gtext}",
                                    f"delegatura, zu der die dzielnica gehört: {gtext}"),
        ("*", "flaeche_km2"): _p("powierzchnia, km²", "area, km²", "Fläche, km²"),
        ("*", "flaeche_quelle"): _p("źródło powierzchni", "source of the area", "Quelle der Fläche"),
        ("*", "nsp_weg"): _p("skąd pochodzą wartości NSP 2021", "where the NSP 2021 values come from", "Herkunft der Werte aus dem NSP 2021"),
        ("*", "nsp"): _p("NSP 2021 dla dzielnicy: puste (zob. nsp_grund)", "NSP 2021 for the district: empty (see nsp_grund)",
                         "NSP 2021 je dzielnica: leer (siehe nsp_grund)"),
        ("*", "nsp_grund"): _p("powód braku wartości NSP 2021", "reason why NSP 2021 values are missing", "Grund für fehlende Werte aus dem NSP 2021"),
        ("*", "dichte_nsp"): _p("gęstość zaludnienia według NSP 2021, mieszkańcy na km²", "population density from NSP 2021, residents per km²",
                                "Einwohnerdichte nach NSP 2021, Einwohner je km²"),
        ("*", "dichte_gitter"): _p("gęstość zaludnienia według siatki Eurostatu, mieszkańcy na km²",
                                   "population density from the Eurostat grid, residents per km²",
                                   "Einwohnerdichte nach Eurostat-Gitter, Einwohner je km²"),
        ("dzielnice", "nr"): dz,
        ("dzielnice", "rzymska"): _p("numer dzielnicy cyframi rzymskimi", "district number in Roman numerals", "Nummer der dzielnica in römischen Ziffern"),
        ("dzielnice", "osm_id"): _p("relacja granicy w OpenStreetMap", "boundary relation in OpenStreetMap", "Grenzrelation in OpenStreetMap"),
        ("siatka_1km", "id"): zelle, ("siatka_1km_odbl", "id"): zelle, ("siatka_1km_pokrycie", "id"): zelle,
        ("rejony_statystyczne", "rejon"): _p("identyfikator rejonu statystycznego GUS (6 cyfr)", "GUS statistical area identifier (6 digits)",
                                             "Kennung des statistischen Bezirks des GUS (6 Ziffern)"),
        ("rejony_statystyczne", "delegatura_teryt"): _p("kod TERYT delegatury według GUS", "TERYT code of the delegatura according to GUS",
                                                        "TERYT-Kennung der delegatura laut GUS"),
        ("rejony_statystyczne", "nsp_einwohner"): _p("NSP 2021: liczba mieszkańców rejonu; puste = brak wiersza w tabeli spisu",
                                                     "NSP 2021: residents of the area; empty = no row in the census table",
                                                     "NSP 2021: Einwohner des Bezirks; leer = keine Zeile in der Zensustabelle"),
        ("rejony_statystyczne", "nsp_q_u20"): _p("NSP 2021: udział osób poniżej 20 lat, pełne %; puste poniżej 100 osób",
                                                 "NSP 2021: share under 20, whole %; empty below 100 people",
                                                 "NSP 2021: Anteil unter 20 Jahren, ganze %; leer unter 100 Personen"),
        ("rejony_statystyczne", "nsp_q_60p"): _p("NSP 2021: udział osób w wieku 60 lat i więcej, pełne %; puste poniżej 100 osób",
                                                 "NSP 2021: share aged 60 and over, whole %; empty below 100 people",
                                                 "NSP 2021: Anteil ab 60 Jahren, ganze %; leer unter 100 Personen"),
        ("rejony_statystyczne", "nsp_q_nach"): _p("NSP 2021: udział osób w wieku poprodukcyjnym, pełne %; puste poniżej 100 osób",
                                                  "NSP 2021: share of post-working age, whole %; empty below 100 people",
                                                  "NSP 2021: Anteil im nacherwerbsfähigen Alter, ganze %; leer unter 100 Personen"),
        ("rejony_statystyczne", "ohne_zeile"): _p("1 = rejon bez wiersza w tabeli spisu (bez wartości)", "1 = area without a row in the census table (no values)",
                                                  "1 = Bezirk ohne Zeile in der Zensustabelle (ohne Werte)"),
        ("*", "ew"): _p("mieszkańcy (siatka Eurostatu 2021)", "residents (Eurostat grid 2021)", "Einwohner (Eurostat-Gitter 2021)"),
        ("*", "a_ges"): _p("suma trzech grup wieku w komórce", "sum of the three age groups in the cell", "Summe der drei Altersgruppen der Zelle"),
        ("*", "q_u15"): _p("udział mieszkańców poniżej 15 lat, %", "share of residents under 15, %", "Anteil unter 15 Jahren, %"),
        ("*", "q_65p"): _p("udział mieszkańców w wieku 65 lat i więcej, %", "share of residents aged 65 and over, %", "Anteil ab 65 Jahren, %"),
        ("siatka_1km_odbl", "st"): _p("dzielnica według środka komórki (granice z OSM)", "district by the cell centre (OSM boundaries)",
                                      "dzielnica nach dem Mittelpunkt der Zelle (OSM-Grenzen)"),
        ("placowki_bdot", "id"): _p("identyfikator obiektu w BDOT10k (LOKALNYID)", "object identifier in BDOT10k (LOKALNYID)",
                                    "Objektkennung in BDOT10k (LOKALNYID)"),
        ("*", "art"): _p("rodzaj placówki", "type of facility", "Art der Einrichtung"),
        ("placowki_bdot", "unterart"): _p("podtyp: puste (BDOT10k go nie podaje)", "subtype: empty (not in BDOT10k)", "Unterart: leer (nicht in BDOT10k)"),
        ("placowki_osm", "unterart"): _p("specjalność lekarza z tagu OSM healthcare:speciality (wartości OSM, po angielsku); puste = brak tagu",
                                         "doctor's speciality from the OSM tag healthcare:speciality (OSM values); empty = no tag",
                                         "Fachrichtung aus dem OSM-Tag healthcare:speciality (OSM-Werte, englisch); leer = ohne Tag"),
        ("*", "q"): _p("źródło (klucz w tabeli licencje)", "source (key in the licencje table)", "Quelle (Schlüssel in der Tabelle licencje)"),
        ("placowki_bdot", "name"): _p("nazwa placówki z BDOT10k (nazwa urzędowa, nie osoba)", "facility name from BDOT10k (official, not a person)",
                                      "Name der Einrichtung aus BDOT10k (amtlich, kein Personenname)"),
        ("placowki_bdot", "plaetze"): _p("liczba miejsc: puste (BDOT10k nie podaje)", "places: empty (not in BDOT10k)", "Plätze: leer (nicht in BDOT10k)"),
        ("placowki_bdot", "schueler"): _p("liczba uczniów: puste (BDOT10k nie podaje)", "pupils: empty (not in BDOT10k)", "Schüler: leer (nicht in BDOT10k)"),
        ("placowki_bdot", "schueler_stand"): _p("stan liczby uczniów: puste", "date of the pupil count: empty", "Stand der Schülerzahl: leer"),
        ("placowki_bdot", "status"): _p("zakres informacji o placówce", "what is known about the facility", "Umfang der Angaben zur Einrichtung"),
        ("*", "in_stadt"): _mit(JA, ("w granicach Krakowa (BDOT10k); ", "within Kraków (BDOT10k); ", "in der Gemeinde Kraków (BDOT10k); ")),
        ("przystanki", "id"): _p("rdzeń kodu przystanku ZTP (stop_code przed myślnikiem)", "stem of the ZTP stop code (stop_code before the hyphen)",
                                 "Stamm des Haltestellen-Codes der ZTP (stop_code vor dem Bindestrich)"),
        ("przystanki", "name"): _p("nazwa przystanku (stop_name)", "stop name (stop_name)", "Name der Haltestelle (stop_name)"),
        ("przystanki", "verkehrsmittel"): _p("środki transportu z odjazdami w dniu liczenia", "modes with departures on the counting day",
                                             "Verkehrsmittel mit Abfahrten am Zähltag"),
        ("przystanki", "fahrten_hvz_je_richtung"): _p(f"odjazdy na godzinę w oknie {fe[0]}–{fe[1]}, kierunek z większą liczbą odjazdów",
                                                      f"departures per hour in the window {fe[0]}–{fe[1]}, busier direction",
                                                      f"Abfahrten je Stunde im Fenster {fe[0]}–{fe[1]}, stärkere Richtung"),
        ("przystanki", "taktklasse"): _p("klasa częstotliwości kursowania (własna klasyfikacja, nie norma)",
                                         "service frequency class (own classification, not a standard)",
                                         "Taktklasse (eigene Klassifikation, keine Norm)"),
        ("bdot_kompleksy", "r"): _p("rodzaj kompleksu (BDOT10k RODZAJ)", "type of complex (BDOT10k RODZAJ)", "Art des Komplexes (BDOT10k RODZAJ)"),
        ("bdot_kompleksy", "n"): _p("nazwa kompleksu (BDOT10k NAZWA)", "name of the complex (BDOT10k NAZWA)", "Name des Komplexes (BDOT10k NAZWA)"),
        ("*", "del"): delg,
        ("*", "w"): _mit(JA, ("budynek mieszkalny (FOBUD); puste = brak budynku; ", "residential building (FOBUD); empty = no building; ",
                              "Wohngebäude (FOBUD); leer = kein Gebäude; ")),
        ("*", "mfh"): _mit(JA, ("budynek wielorodzinny (PFBUD); puste = brak budynku; ", "multi-family building (PFBUD); empty = no building; ",
                                "Mehrfamilienhaus (PFBUD); leer = kein Gebäude; ")),
        ("*", "gs"): _p("liczba kondygnacji nadziemnych (BDOT10k LICZ_KONDY)", "storeys above ground (BDOT10k LICZ_KONDY)",
                        "oberirdische Geschosse (BDOT10k LICZ_KONDY)"),
        ("zbk_wykaz_dzielnice", "dzielnica_z_wykazu"): _p("dzielnica według wykazu ZBK (numer 01–18; poza = poza Krakowem)",
                                                          "district as listed by ZBK (number 01–18; poza = outside Kraków)",
                                                          "dzielnica laut ZBK-Liste (Nummer 01–18; poza = außerhalb Krakóws)"),
        ("zbk_wykaz_dzielnice", "n"): _p("liczba pozycji w wykazie (pozycja to nie zawsze budynek)", "number of list entries (an entry is not always a building)",
                                         "Zahl der Einträge (ein Eintrag ist nicht immer ein Gebäude)"),
        ("dostepnosc", "st"): _p("dzielnica (01–18); puste = całe miasto", "district (01–18); empty = whole city", "dzielnica (01–18); leer = ganze Stadt"),
        ("dostepnosc", "nazwa"): _p("nazwa dzielnicy albo miasta", "name of the district or city", "Name der dzielnica oder der Stadt"),
        ("dostepnosc", "ew"): _p("liczba mieszkańców obszaru (siatka Eurostatu, wartość zaokrąglona)", "residents of the area (Eurostat grid, rounded)",
                                 "Einwohner des Gebiets (Eurostat-Gitter, gerundet)"),
        ("dostepnosc", "kennzahl"): _p("wskaźnik", "indicator", "Kennzahl"),
        ("dostepnosc", "art"): _p("rodzaj celu", "type of destination", "Art des Ziels"),
        ("dostepnosc", "methode"): _p("sposób pomiaru odległości", "how distance is measured", "Art der Entfernungsmessung"),
        ("dostepnosc", "einheit"): _p("jednostka wartości", "unit of the value", "Einheit des Werts"),
        ("dostepnosc", "status"): _p("status wartości", "status of the value", "Status des Werts"),
        ("dostepnosc", "vorlaeufig"): _p("1 = wartość wstępna (szkoły bez obwodów szkolnych); puste = nie dotyczy",
                                         "1 = provisional (schools without catchment areas); empty = not applicable",
                                         "1 = vorläufig (Schulen ohne Schulbezirke); leer = trifft nicht zu"),
        ("dostepnosc", "richtwert_wert"): _p("promień ze standardu urzędowego, z którym porównano", "radius from the official standard used for comparison",
                                             "Radius aus der amtlichen Vorgabe, mit der verglichen wird"),
        ("dostepnosc", "richtwert_einheit"): _p("jednostka promienia", "unit of the radius", "Einheit des Radius"),
        ("dostepnosc", "radius_m"): _p("promień w metrach, w którym liczono (przy udziale w promieniu, przystankach i parkach); puste = nie dotyczy",
                                       "radius in metres used for the count (share within radius, stops, parks); empty = not applicable",
                                       "Radius in Metern, in dem gezählt wurde (Anteil im Radius, Haltestellen, Parks); leer = trifft nicht zu"),
        ("dostepnosc", "richtwert_q"): _p("źródło standardu (klucz w tabeli licencje)", "source of the standard (key in the licencje table)",
                                          "Quelle der Vorgabe (Schlüssel in der Tabelle licencje)"),
        ("dostepnosc", "richtwert_seite"): _p("miejsce w akcie prawnym (artykuł, strona)", "location in the legal act (article, page)",
                                              "Fundstelle im Gesetz (Artikel, Seite)"),
        ("dostepnosc", "wert"): _p("wartość wskaźnika; puste poniżej progu tajemnicy statystycznej", "value of the indicator; empty below the confidentiality threshold",
                                   "Wert der Kennzahl; leer unter der Geheimhaltungsschwelle"),
        ("dostepnosc", "zaehler"): _p("licznik wskaźnika (np. mieszkańcy w promieniu, powierzchnia parków)",
                                      "numerator of the indicator (e.g. residents within the radius, park area)",
                                      "Zähler der Kennzahl (z. B. Einwohner im Radius, Parkfläche)"),
        ("dostepnosc", "nenner"): _p("mianownik wskaźnika (np. mieszkańcy, liczba placówek)", "denominator of the indicator (e.g. residents, number of facilities)",
                                     "Nenner der Kennzahl (z. B. Einwohner, Zahl der Einrichtungen)"),
        ("*", "stand"): _p("stan danych (data)", "data as of (date)", "Datenstand (Datum)"),
        ("placowki_osm", "id"): _p("identyfikator obiektu OSM (n = węzeł, w = linia lub obszar)", "OSM object identifier (n = node, w = way)",
                                   "OSM-Kennung (n = Knoten, w = Weg oder Fläche)"),
        ("rejestr_zabytkow", "q"): _p("źródło punktu (wd = Wikidane, nid = rejestr NID, gez = gminna ewidencja zabytków; kilka po przecinku)",
                                      "source of the point (wd = Wikidata, nid = NID register, gez = gminna ewidencja zabytków; several separated by commas)",
                                      "Quelle des Punkts (wd = Wikidata, nid = NID-Register, gez = gminna ewidencja zabytków; mehrere durch Komma)"),
        ("rejestr_zabytkow", "ep"): _p("okres budowy z daty powstania w Wikidanych (klasa, nigdy pojedynczy rok); puste = brak lub niejednoznaczne",
                                       "construction period from the inception date in Wikidata (class, never a single year); empty = none or ambiguous",
                                       "Bauzeitklasse aus dem Entstehungsdatum in Wikidata (nie ein Einzeljahr); leer = keines oder mehrdeutig"),
        ("rejestr_zabytkow", "polozenie_sprawdzone"): _mit(JA, ("położenie tego punktu sprawdzone osobno na ortofotomapie (wszędzie 0: sprawdzono co najwyżej losową próbę warstwy, wynik w CZYTAJ.md); ",
                                                                "location of this point checked individually on aerial imagery (0 everywhere: at most a random sample of the layer was checked, result in README.md); ",
                                                                "Lage dieses Punkts einzeln am Luftbild geprüft (überall 0: geprüft ist höchstens eine Zufallsstichprobe der Ebene, Ergebnis in LIESMICH.md); ")),
        ("osm_heritage_start_date", "h"): _mit(JA, ("obiekt ma tag heritage; ", "object has a heritage tag; ", "Objekt trägt heritage; ")),
        ("osm_heritage_start_date", "ep"): _p("okres budowy z tagu start_date (klasa, nigdy pojedynczy rok); puste = brak lub niejednoznaczne",
                                              "construction period from the start_date tag (class, never a single year); empty = none or ambiguous",
                                              "Bauzeitklasse aus start_date (nie ein Einzeljahr); leer = keine oder mehrdeutig"),
        ("osm_heritage_start_date", "polozenie_sprawdzone"): _mit(JA, ("położenie tego punktu sprawdzone osobno na ortofotomapie (wszędzie 0: sprawdzono co najwyżej losową próbę warstwy, wynik w CZYTAJ.md); ",
                                                                "location of this point checked individually on aerial imagery (0 everywhere: at most a random sample of the layer was checked, result in README.md); ",
                                                                "Lage dieses Punkts einzeln am Luftbild geprüft (überall 0: geprüft ist höchstens eine Zufallsstichprobe der Ebene, Ergebnis in LIESMICH.md); ")),
        ("zbk_budynki", "art"): _p("rodzaj budynku według wykazu ZBK", "building type in the ZBK list", "Art des Gebäudes laut ZBK-Liste"),
        ("zbk_budynki", "eig"): _p("własność według wykazu ZBK (punkty tylko bez udziału osób prywatnych)",
                                   "ownership in the ZBK list (points only without private owners)",
                                   "Eigentum laut ZBK-Liste (Punkte nur ohne private Eigentümer)"),
        ("zbk_budynki", "st"): _p("dzielnica według wykazu ZBK", "district as listed by ZBK", "dzielnica laut ZBK-Liste"),
        ("zbk_budynki", "fn"): _p("przeważająca funkcja przypisanego budynku BDOT10k (PFBUD); puste = brak", "main use of the linked BDOT10k building (PFBUD); empty = none",
                                  "überwiegende Funktion des verknüpften BDOT10k-Gebäudes (PFBUD); leer = keine"),
        ("zbk_budynki", "h"): _p("wysokość budynku, m (zob. hq)", "building height, m (see hq)", "Gebäudehöhe, m (siehe hq)"),
        ("zbk_budynki", "hq"): _p("pochodzenie wysokości", "origin of the height", "Herkunft der Höhe"),
        ("zbk_budynki", "typ"): _p("typologia (szacunek); puste = brak kandydata", "typology (estimate); empty = no candidate",
                                   "Typologie (Schätzung); leer = kein Kandidat"),
        ("zbk_typologia_dzielnice", "st"): dz,
        ("zbk_typologia_dzielnice", "szacunek"): _mit(JA, ("wartości są szacunkiem; ", "values are an estimate; ", "Werte sind eine Schätzung; ")),
        ("*", "x"): _p(f"współrzędna x (wschód) w EPSG:{sr}, m", f"x coordinate (east) in EPSG:{sr}, m", f"x-Koordinate (Ost) in EPSG:{sr}, m"),
        ("*", "y"): _p(f"współrzędna y (północ) w EPSG:{sr}, m", f"y coordinate (north) in EPSG:{sr}, m", f"y-Koordinate (Nord) in EPSG:{sr}, m"),
        ("*", "wkt"): _p(f"geometria jako WKT w EPSG:{sr}", f"geometry as WKT in EPSG:{sr}", f"Geometrie als WKT in EPSG:{sr}"),
        ("licencje", "plik"): _p("plik GeoPackage", "GeoPackage file", "GeoPackage-Datei"),
        ("licencje", "warstwa"): _p("warstwa", "layer", "Ebene"),
        ("licencje", "licencja_pliku"): _p("licencja warstwy w tym pliku", "licence of the layer in this file", "Lizenz der Ebene in dieser Datei"),
        ("licencje", "licencja_zrodla"): _p("licencja źródła", "licence of the source", "Lizenz der Quelle"),
        ("licencje", "zrodlo"): _p("źródło", "source", "Quelle"),
        ("licencje", "nota"): _p("nota o źródle do podania (dosłownie)", "source notice to give (verbatim)", "anzugebender Quellenvermerk (wörtlich)"),
    }
    if (w, f) in tabela:
        return tabela[(w, f)]
    if f.startswith("luftlinie_m_") and f[12:] in ZIEL:
        return _mit(ZIEL[f[12:]], ("odległość w linii prostej od środka komórki do najbliższego celu: ",
                                   "straight-line distance from the cell centre to the nearest: ",
                                   "Luftlinie vom Mittelpunkt der Zelle zum nächsten Ziel: "), (", m", ", m", ", m"))
    if f.startswith("fussweg_m_") and f[10:] in ZIEL:
        return _mit(ZIEL[f[10:]], ("dojście piesze siecią dróg OSM od środka komórki do najbliższego celu: ",
                                   "walking route along the OSM network from the cell centre to the nearest: ",
                                   "Fußweg über das OSM-Wegenetz vom Mittelpunkt der Zelle zum nächsten Ziel: "), (", m", ", m", ", m"))
    m = re.fullmatch(r"art_(\w+)", f)
    if w == "zbk_wykaz_dzielnice" and m and m.group(1) in ZBK_ART:
        return _mit(ZBK_ART[m.group(1)], ("pozycje wykazu o rodzaju: ", "list entries of type: ", "Einträge der Art: "))
    m = re.fullmatch(r"eigentum_(\w+)", f)
    if w == "zbk_wykaz_dzielnice" and m and m.group(1) in EIGENTUM:
        return _mit(EIGENTUM[m.group(1)], ("pozycje wykazu, własność: ", "list entries, ownership: ", "Einträge, Eigentum: "))
    if w == "zbk_typologia_dzielnice":
        return _typ(f, k)
    return None


def opis(warstwa: str, pole: str, k: dict) -> P | None:
    """Erklärung (pl, en, de) eines Feldes einer Ebene oder None."""
    if (e := _einzeln(warstwa, pole, k)) is not None:
        return e
    if (e := _einzeln("*", pole, k)) is not None:
        return e
    for vor, fn in (("nsp_", _nsp), ("gitter_", _gitter), ("bdot_", _bdot_denkmal)):
        if pole.startswith(vor) and (e := fn(pole[len(vor):])) is not None:
            return e
    if pole.startswith("geb_") and (e := _geb(pole[4:], k)) is not None:
        return e
    if pole.startswith("klimat_") and (e := _klimat(pole[7:], k)) is not None:
        return e
    if warstwa == "siatka_1km_pokrycie" and (e := _klimat(pole, k)) is not None:
        return e
    if pole.startswith("typ_") and (e := _typ(pole[4:], k)) is not None:
        return e
    return None


# ------------------------------------------------------------------------------------------------- Werte
def wartosci(k: dict) -> dict[str, dict[str, P]]:
    """Feld → Wert → Erklärung (pl, en, de). Gilt in jeder Ebene, die das Feld trägt (Ausnahme art, siehe unten)."""
    gr = k["grenzen"]
    ra = k["radien"]
    stufen = sorted(gr.items(), key=lambda kv: -kv[1])
    takt = {kl: _p(f"odjazdy na godzinę w kierunku: co najmniej {_zahl(v, 'pl')}", f"departures per hour and direction: at least {_zahl(v, 'en')}",
                   f"Abfahrten je Stunde und Richtung: mindestens {_zahl(v, 'de')}") for kl, v in stufen}
    unten = stufen[-1][1]
    takt["unter III"] = _p(f"odjazdy na godzinę w kierunku: mniej niż {_zahl(unten, 'pl')}", f"departures per hour and direction: fewer than {_zahl(unten, 'en')}",
                           f"Abfahrten je Stunde und Richtung: weniger als {_zahl(unten, 'de')}")
    ro = ra.get(("oepnv_takt", "fussweg")) or ra.get(("oepnv_takt", "luftlinie"))
    rg = ra.get(("gruen_in_radius", "fussweg"))
    ep = {
        "vor_1800": ("przed 1800", "before 1800", "vor 1800"),
        "1800_1866": ("1800–1866", "1800–1866", "1800–1866"),
        "1867_1918": ("1867–1918", "1867–1918", "1867–1918"),
        "1919_1945": ("1919–1945", "1919–1945", "1919–1945"),
        "1946_1989": ("1946–1989", "1946–1989", "1946–1989"),
        "ab_1990": ("od 1990", "from 1990", "ab 1990"),
    }
    return {
        "art": {**ZIEL},
        "art@zbk_budynki": {**ZBK_ART},
        "eig": {kk: v for kk, v in EIGENTUM.items() if kk in ("gmina", "skarb_panstwa", "publiczne_mieszane")},
        "r": {
            "muzeum": _p("zespół muzealny", "museum complex (zespół muzealny)", "Museumskomplex (zespół muzealny)"),
            "pamiec": _p("miejsce pamięci narodowej", "national memorial site (miejsce pamięci narodowej)", "nationale Gedenkstätte (miejsce pamięci narodowej)"),
            "twierdza": _p("twierdza lub forteca", "fortress (twierdza lub forteca)", "Festung (twierdza lub forteca)"),
            "zabudowa": _p("zespół zabudowy historycznej", "historic building ensemble (zespół zabudowy historycznej)",
                           "historisches Bauensemble (zespół zabudowy historycznej)"),
        },
        "verkehrsmittel": {
            "bus": _p("autobus", "bus", "Bus"), "tram": _p("tramwaj", "tram", "Straßenbahn"),
            "bus+tram": _p("autobus i tramwaj", "bus and tram", "Bus und Straßenbahn"),
        },
        "taktklasse": takt,
        "status": {
            "lage_ohne_kapazitaet": _p("tylko położenie, bez liczby miejsc i uczniów", "location only, no places or pupils",
                                       "nur Lage, ohne Plätze und Schüler"),
            "orientierung": _p("wartość orientacyjna, nie urzędowa", "guide value, not official", "Orientierung, kein amtlicher Wert"),
        },
        "kennzahl": {
            "anteil_in_radius": _p("udział mieszkańców z placówką w promieniu ze standardu urzędowego (richtwert_wert), %",
                                   "share of residents with a facility within the radius of the official standard (richtwert_wert), %",
                                   "Anteil der Einwohner mit Einrichtung im Radius der amtlichen Vorgabe (richtwert_wert), %"),
            "ew_je_einrichtung": _p("mieszkańcy na jedną placówkę", "residents per facility", "Einwohner je Einrichtung"),
            "oepnv_takt": _p(f"udział mieszkańców z przystankiem klasy I lub II w odległości {ro} m, %",
                             f"share of residents with a class I or II stop within {ro} m, %",
                             f"Anteil der Einwohner mit Haltestelle der Taktklasse I oder II in {ro} m, %"),
            "gruen_m2_je_ew": _p("powierzchnia parków i skwerów (BDOT10k) na mieszkańca, m²", "park and square area (BDOT10k) per resident, m²",
                                 "Park- und Grünanlagenfläche (BDOT10k) je Einwohner, m²"),
            "gruen_in_radius": _p(f"udział mieszkańców z parkiem lub skwerem w odległości {rg} m dojścia pieszego, %",
                                  f"share of residents with a park or square within {rg} m walking, %",
                                  f"Anteil der Einwohner mit Park oder Grünanlage in {rg} m Fußweg, %"),
        },
        "methode": {
            "luftlinie": _p("odległość w linii prostej od środka komórki 1 km", "straight-line distance from the centre of the 1 km cell",
                            "Luftlinie vom Mittelpunkt der 1-km-Zelle"),
            "fussweg": _p("dojście piesze siecią dróg OSM od środka komórki 1 km", "walking route along the OSM network from the centre of the 1 km cell",
                          "Fußweg über das OSM-Wegenetz vom Mittelpunkt der 1-km-Zelle"),
        },
        "einheit": {
            "%": _p("procent", "per cent", "Prozent"),
            "ew_je_einrichtung": _p("mieszkańcy na placówkę", "residents per facility", "Einwohner je Einrichtung"),
            "m2_je_ew": _p("m² na mieszkańca", "m² per resident", "m² je Einwohner"),
        },
        "q": {
            "bdot10k": _p("BDOT10k (GUGiK)", "BDOT10k (GUGiK)", "BDOT10k (GUGiK)"),
            "ztp": _p("GTFS ZTP Kraków", "GTFS of ZTP Kraków", "GTFS der ZTP Kraków"),
            "osm": _p("OpenStreetMap", "OpenStreetMap", "OpenStreetMap"),
            "wd": _p("Wikidane (CC0 1.0)", "Wikidata (CC0 1.0)", "Wikidata (CC0 1.0)"),
        },
        "richtwert_einheit": {"m": _p("metry", "metres", "Meter")},
        "richtwert_q": {"prawo_oswiatowe": _p("ustawa Prawo oświatowe", "Education Law (Prawo oświatowe)", "Schulgesetz (Prawo oświatowe)")},
        "anteil_grund": {"bezugsflaeche_zu_klein": _p("powierzchnia odniesienia za mała", "reference area too small", "Bezugsfläche zu klein")},
        "flaeche_quelle": {"bdot10k": _p("granica z BDOT10k (PRG)", "boundary from BDOT10k (PRG)", "Grenze aus BDOT10k (PRG)")},
        "nsp_weg": {
            "tabelle": _p("tabela GUS dla całej jednostki", "GUS table for the whole unit", "GUS-Tabelle für die ganze Einheit"),
            "rejony": _p("suma rejonów statystycznych", "sum of statistical areas", "Summe der rejony statystyczne"),
        },
        "nsp_grund": {
            "rejony_geometrie_fehlt":
                _p("brak granic rejonów statystycznych: ręczne pobranie GUS „Jednostki statystyczne 2021” jeszcze nie nastąpiło",
                   "boundaries of the statistical areas are missing: the manual download of GUS “Jednostki statystyczne 2021” is still pending",
                   "Geometrie der rejony statystyczne fehlt: Handdownload GUS „Jednostki statystyczne 2021“ steht aus"),
        },
        "geb_bebauungsdichte_anzeige": {"anteil": _p("pokazywane jako udział w %", "shown as a share in %", "als Anteil in % gezeigt")},
        "geb_geschossflaeche_naeherung_abzeichen": {"orientacyjnie": _p("orientacyjnie", "for orientation", "Orientierung")},
        "ep": {kk: _p(*v) for kk, v in ep.items()},
        "hq": {
            "lod2": _p("model 3D LoD2 (GUGiK, stan 2017)", "LoD2 3D model (GUGiK, as of 2017)", "LoD2-Modell (GUGiK, Stand 2017)"),
            "geschosse": _p(f"kondygnacje × {k['geschoss_m']} m (szacunek)", f"storeys × {k['geschoss_m']} m (estimate)",
                            f"Geschosse × {k['geschoss_m']} m (Schätzung)"),
        },
        "typ": {
            "blok": _p("kandydat na blok (szacunek)", "block candidate (estimate)", "Block-Kandidat (Schätzung)"),
            "osiedle": _p("kandydat na blok na osiedlu blokowym (szacunek)", "block candidate in a large housing estate (estimate)",
                          "Block-Kandidat in einer Großsiedlung (Schätzung)"),
        },
        "dzielnica_z_wykazu": {"poza": _p("poza Krakowem", "outside Kraków", "außerhalb Krakóws")},
    }


# Kategorienfelder: jeder vorkommende Wert braucht eine Erklärung (Prüfung in pruefen/S4_export.py)
KATEGORIEN = ["art", "eig", "r", "verkehrsmittel", "taktklasse", "status", "kennzahl", "methode", "einheit", "q",
              "richtwert_einheit", "richtwert_q", "anteil_grund", "flaeche_quelle", "nsp_weg", "nsp_grund",
              "geb_bebauungsdichte_anzeige", "geb_geschossflaeche_naeherung_abzeichen", "ep", "hq", "typ"]


def wert_opis(W: dict, warstwa: str, pole: str, wert) -> P | None:
    """Erklärung eines Werts; dzielnica_z_wykazu nur für poza (Nummern sind selbsterklärend)."""
    if pole == "art" and warstwa == "zbk_budynki":
        return W["art@zbk_budynki"].get(wert)
    return W.get(pole, {}).get(wert)
