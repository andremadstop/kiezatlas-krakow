# Abnahme vor der Veröffentlichung 1.0.0 (15.11.2026): Funde und ihr Verbleib

Stand 15.11.2026, Zweig `Arbeitszweig p4b-integration` (von `main` `8cac472`). Drei Zweige haben die Veröffentlichung
vorbereitet: Nacharbeit zur Sichtprüfung (`Arbeitszweig p4b-rest`), drei kurze Filme (`Arbeitszweig p4b-filme`) und Veröffentlichung
mit bereinigtem Export, Version 1.0.0 und Schrittliste (`Arbeitszweig p4b-veroeffentlichung`). Eine Abnahme hat alle drei
lesend geprüft, den vorbereiteten Export in einem frischen Klon nachgeprüft und die Filme in Standbildern angesehen.
Ihr Urteil: bedingt abnahmefähig. Nacharbeit sauber, Filme fachlich korrekt, aber der Export war nicht der
Release-Stand, die Filmlizenz sperrte den Export, und die Schrittliste hatte Reihenfolgefehler.

Die Integration hat die drei Zweige zusammengeführt und jeden Fund am Integrationsstand behoben oder begründet
geschlossen. Status: **behoben** (Commit), **teilweise** (was fehlt, steht dabei), **offen** (wer entscheidet),
**verworfen** (Grund).

## Zusammenführung

| Merge | Konflikt | Lösung |
|---|---|---|
| `Arbeitszweig p4b-rest` (`791b2f1`) | keiner | – |
| `Arbeitszweig p4b-filme` (`40f3a14`) | `CHANGELOG.md` | beide Abschnitte behalten |
| `Arbeitszweig p4b-veroeffentlichung` (`fa4e4e2`) | `CHANGELOG.md`, `skripte/oeffentlich_ausnahmen.tsv`, `skripte/oeffentlich_pruefen.py` | Abschnitt 1.0.0 oben, die Abschnitte der beiden anderen Zweige darunter (sie gehören zu 1.0.0); `.vtt` und `.gitattributes` beide in die Textlisten; Lizenzzeile der Bildschirmfotos aus der Veröffentlichung, die beiden Filmzeilen aus den Filmen (danach eigener Commit, Fund 2) |

## Funde der Abnahme

| Nr. | Schwere | Zweig | Fund | Verbleib |
|---|---|---|---|---|
| 1 | blockierend | Veröffentlichung | Der vorbereitete Export (`f37ad25`) stammte nur aus dem Zweig Veröffentlichung, ohne die Fixes der Nacharbeit und ohne die Filme; beim Zusammenführen gab es Konflikte. | **behoben:** alle drei Zweige zusammengeführt (oben), Prüfstand am Integrationsstand (README-Kasten), danach neuer Export aus diesem Stand. Der alte Export unter `/tmp/kz_export/kiezatlas-krakow/` ist überholt und wird nicht gepusht. |
| 2 | blockierend | Filme | Nach dem Merge war `oeffentlich_pruefen.py --veroeffentlichung` rot (6 Videodateien ohne Lizenzregel); der Export setzt einen grünen Lauf voraus. | **behoben** `9b10495`: CC BY 4.0 wie die Bildschirmfotos (KR63), Lizenzregel `ausnahme`, Zeile in `belege/README.md`, `belege/filme/README.md` und im Generator `skripte/filme.mjs`. **Offen (Andre):** Lizenz bestätigen, sonst die Filme vor dem Export herausnehmen. |
| 3 | wichtig | Veröffentlichung | Schrittliste: Schritt 0 schrieb nach `…-2`, die Schritte 1, 4, 6, 7 arbeiteten im alten Ordner; wörtlich ausgeführt wäre der alte Export gepusht worden. | **behoben** `90ff279`: `EXPORT` einmal in Schritt 0 setzen, alle Schritte mit `"$EXPORT"`, vor dem Push Abgleich des Hashes. |
| 4 | wichtig | Veröffentlichung | Schritt 8 hätte die vor Schritt 7 gebaute Deploy-Kopie mit festem CSP-Hash hochgeladen; dort steht noch „Repository noch nicht öffentlich“, keine DOI. | **behoben** `90ff279`: Neubau zwingend nach Schritt 7 in `"$DEPLOY"`, rsync, CSP und MD5-Abgleich auf diesen Ordner, Hash aus der Ausgabe von `deploy_kopie.py`, grep auf „nicht öffentlich“; `docs/auslieferung.md` entsprechend. Die alte Probe-Kopie unter `/tmp/kz_deploy/…/2026-11-15/` ist nicht zum Hochladen. |
| 5 | wichtig | Veröffentlichung | Schritt 7 verlangte eine Handänderung an `metoda.html`, die den Schalter `repository` aus der Nacharbeit bricht; `skripte/31_ort.py` fehlte. | **behoben** `90ff279`: Zeile auf `config/krakow.yaml` `repository:` umgeschrieben, `ort` zuerst (Prüfsumme in `daten/ort.js`), Liste der Stellen, die der Schalter nicht erfasst (dane, `CITATION.cff`, Kästen in running/uruchomienie, przekazanie), grep auf übrige „noch nicht öffentlich“ (KR66). |
| 6 | wichtig | Veröffentlichung | `NOTICE` nannte Luft, Wohnungsmarkt und Denkmale noch Beispieldaten; EEA, RCN und Wikidata fehlten. | **behoben** `fdb46c1`. |
| 7 | wichtig | Veröffentlichung | Der Volllauf im Zweig Veröffentlichung ist nie fertig geworden (Log bricht bei D4 ab). | **behoben:** `./pruefen.sh --voll --gegenprobe` am Integrationsstand, Protokoll unter `belege/pruefstand-…/` (README-Kasten). |
| 8 | wichtig | Veröffentlichung | Frischer Klon ohne Rohdaten: `./pruefen.sh` meldete Luft und Wohnungsmarkt als Befund, ohne Erklärung. | **behoben** `26288ae`: ohne Eingang `--ohne-lauf` wie die CI, Neurechnung übersprungen (KR68); Probe mit leerem `KIEZ_DATEN`: nur noch die zehn dokumentierten Prüfsummenlisten. `docs/running.md` und `uruchomienie.md` §8 ergänzt. |
| 9 | wichtig | Filme | Orange in Film 2: OSM-Kennzeichnung `#b07a1f` auf der Karte. | **behoben** `c9c1de1` (Karte, KR64) und `2670e92` (Filme neu aufgenommen); Standbild „Bliżej: Stare Miasto“ ohne Orange. Bildschirmfotos: kein Foto zeigt die Ebene (Karte startet ohne Punktebenen), deshalb nicht neu. |
| 10 | klein | Filme | RCN-Nennung auf der Quellentafel von Film 3 verkürzt. | **behoben** `e366af1`, `2670e92`: wörtlich wie `daten/mieszkania_odbl.js`. |
| 11 | klein | Filme | Polnische Lehnübertragungen; Titel „Atlas w minutę“ bei 69 s; Untertitel verdecken Tabellenwerte. | **teilweise** `e366af1`, `2670e92`: die drei Sätze wie vorgeschlagen ersetzt. **Verworfen:** Titel, „w minutę“ ist eine Redewendung, 69 s liegen nah genug; das Lektorat kann ihn ändern. **Offen:** Untertitel über Tabellenwerten (mieszkania), zusammen mit dem muttersprachlichen Lektorat in einer Neuaufnahme. |
| 12 | klein | Veröffentlichung | Ordner des Arbeitsrechners in Tilde-Form im Export, vom Muster nicht erkannt. | **behoben** `e81dfcb`: Stellen ersetzt, Muster erweitert. |
| 13 | klein | Veröffentlichung | Schrittliste: Entscheidung 2 verwies auf Schritt 7 statt 8; `gh auth setup-git` fehlte; `npm ci` im Export mit `node_modules`-Verweis. | **behoben** `90ff279`. |
| 14 | klein | Veröffentlichung | Mailentwurf behauptete standardmäßig „recompute it“ / „przeliczyć“, obwohl die Pipeline nicht öffentlich ist. | **behoben** im Entwurf (interner Vault der UG, außerhalb des Repos): der vorsichtige Satz ist Standard, „recompute“ erst nach Veröffentlichung der Pipeline. **Verworfen:** die EN-Fassung kürzen (optional, Länge vertretbar). |
| 15 | klein | Nacharbeit | Review-Funde behoben, Prüfstand echt grün; offen nur KR33 („ungeprüft“) und Widersprüche nach dem Setzen von `repository` (dane, CITATION-Satz, running/uruchomienie, przekazanie). | **behoben** `e55f7ef` (KR33 Nachtrag); die Widersprüche löst Schritt 7 der Schrittliste beim Veröffentlichen (Fund 5), vorher sind die Sätze richtig. |

## Was aus den Berichten der Zweige offen war

| Punkt | Verbleib |
|---|---|
| CHANGELOG 1.0.0 ohne Schnappschuss-Änderungen (EEA, Wikidata, RCN ausgeschlossen, Größe, Deploy-Kopie aus dem veröffentlichten Stand) | **behoben** (Abschnitt „Abnahme vor der Veröffentlichung“) |
| Schnappschuss-Lizenz als Nachtrag zu KR49 | **behoben** als Vorschlag KR65; **offen (Andre):** vor dem Upload bestätigen |
| Entscheidungen der Filme nur im README (CDP-Streaming, 5 MB, „Vergleich“) | **behoben** KR63 |
| Unabhängiges Review des Bedingungsparsers in `skripte/16_bloecke_krakow.py` und von `pruefen/S4_bloecke.py` Teil 9 | **teilweise:** die Abnahme hat den Parser gelesen, ohne Fund; ein Review mit frischem Kontext lief nicht |
| Schnellprüfungen sollen nach Änderungen an `config/krakow.yaml` auch `skripte/31_ort.py --pruefen` enthalten | **behoben** für diesen Stand (lief mit); Schritt 7 der Schrittliste nennt es |
| Startgewicht: Planer 325 KB gz über der Grenze aus KR10; Startseite misst die Prüfung gesamt statt JavaScript (KR39) | **offen (Andre):** beheben oder Abweichung hinnehmen, vor dem Website-Upload |
| GSAP in `vendor/` (GreenSock „No Charge“ License) im öffentlichen Repo | **offen (Andre)** |
| Zenodo-Lizenzkennung `Apache-2.0` in `.zenodo.json` (Vokabular vermutlich klein geschrieben) | **offen:** nach dem Release in Zenodo ansehen |
| Geodaten-Import-Pipeline nicht öffentlich; Datenbankschritte nicht nachrechenbar | **offen** (Andre), in `docs/przekazanie.md` benannt |
| Polnische und englische Texte, Untertitel der Filme nicht muttersprachlich geprüft | **offen** (Lektorat) |
| Filme nirgends eingebunden; Erstnennung nach Glossar in den Untertiteln; Bildtakt rund 13 bis 14 Bilder je Sekunde | **offen**, nicht beauftragt; mit dem Lektorat zusammen |
