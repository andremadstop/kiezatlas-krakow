# Quellen Paket Schrift und Grundkarten-Anbindung (DF)

Stand 13.11.2026. Vorlage für `QUELLEN.md` (Übernahme durch die Belegschicht). Weg: A = Abruf über
`skripte/abruf.py`, H = Handdownload, L = lokal installiert. Wörtliche Vermerke in Originalsprache.
Zählungen und Größen: `belege/DF_schriften_grundkarte.md`.

## Quellen

| Quelle | Nutzer | Adresse | Lizenz | Vermerk (Original) | Weg | Stand |
|---|---|---|---|---|---|---|
| Barlow (The Barlow Project Authors), npm-Paket `@fontsource/barlow` 5.3.0 (Fontsource) | `fonts/barlow-400-normal.woff2`, `-500-`, `-600-`; `fonts/einbettung.js` (Schaugrafik) | https://registry.npmjs.org/@fontsource/barlow/-/barlow-5.3.0.tgz | SIL Open Font License 1.1 (`license: OFL-1.1` in den Paketangaben, `package/LICENSE`) | „Copyright 2017 The Barlow Project Authors (https://github.com/jpt/barlow)“ (`package/LICENSE`, erste Zeile) | A | Abruf 13.11.2026, SHA256 `8ad808291f807367d10eadf915791608bd04cc393882e7e86e290daeeadd843c`, npm-Integrität `sha512-tGR0y6QObRtKv71MOth44222+mdNFM/ZWFWDV1VLzNbG4oK9PNRlyJzmkck4vHAi9ibHBXgt4SlY51amFP55CA==` (geprüft) |
| Barlow Semi Condensed (The Barlow Project Authors), npm-Paket `@fontsource/barlow-semi-condensed` 5.3.0 | `fonts/barlow-semi-condensed-500-normal.woff2`, `-600-`; `fonts/einbettung.js` | https://registry.npmjs.org/@fontsource/barlow-semi-condensed/-/barlow-semi-condensed-5.3.0.tgz | SIL Open Font License 1.1 | wie oben | A | Abruf 13.11.2026, SHA256 `94991ed2fc3fe0e11d8af5129932bdd94d29b6a7355859ebfba9a19d6610cc77`, npm-Integrität `sha512-EdpQ1GlLMofGqDsQhEw+g6DonNKmzt21p8y/oNbTl4BFzEkqYkFyE2fj25YGxmZBL/LZZGAxe74FlvEWcgc31w==` (geprüft) |
| Paketangaben der npm-Registry zu beiden Paketen (Version, Lizenz, Integrität) | Prüfung in `skripte/schriften.py` | https://registry.npmjs.org/@fontsource%2fbarlow/latest, https://registry.npmjs.org/@fontsource%2fbarlow-semi-condensed/latest | nicht ausgeliefert | – | A | Abruf 13.11.2026, SHA256 in `belege/rohdaten-DF-schriften.sha256` |

Ablage: `kiezatlas-daten/krakow/schriften/2026-11-13/` mit `HERKUNFT.md`. robots.txt von `registry.npmjs.org`
am 13.11.2026 vom Abrufwerkzeug ausgewertet (Befund unter `kiezatlas-daten/krakow/_robots/2026-11-13/`).

Die Kartenschrift Noto Sans und die Kacheln aus BDOT10k stehen in `quellen-D8.md`; dieses Paket bindet sie nur an
die Seiten an und übernimmt die Bildzeile aus `daten/grundkarte.js` wörtlich in `config/krakow.yaml`
(`karte.grundkarte.attribution`).

## Ausgaben und ihre Lizenz

| Ausgabe | Lizenz | Vermerk |
|---|---|---|
| `fonts/*.woff2`, `fonts/einbettung.js` | SIL Open Font License 1.1 (`fonts/OFL.txt`) | Copyright 2017 The Barlow Project Authors; geändert: Teilmengen latin und latin-ext zusammengefügt |
| Grundkarte auf den Seiten (Quelle `bm`, Bildzeile aus `daten/grundkarte.js`) | wie `quellen-D8.md` | „Podkład: BDOT10k, Główny Urząd Geodezji i Kartografii (stan plików 2026-10-03), opracowanie własne“ |
