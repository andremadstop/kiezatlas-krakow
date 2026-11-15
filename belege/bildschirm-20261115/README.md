# Bildschirmfotos aller Seiten (pl)

Erzeugt von `skripte/bildschirmfotos.mjs` (nicht von Hand ändern) auf Commit `6b8df6d`
(sauberer Arbeitsstand). Headless Chromium über Playwright, reduzierte Bewegung,
ganze Seite, Pixelverhältnis 1. Ansichten: Desktop 1440 × 900 px, Handy 390 × 844 px (mobil, Touch). Die Seiten
kommen über `skripte/entwicklung_server.mjs` mit der Grundkarte aus dem Kachelordner; bei Kartenseiten wartet der
Lauf, bis die Karte geladen ist und alle Kacheln da sind. Seitenliste: `seiten` in `config/krakow.yaml`
(18 Seiten). Spalten mit zwei Werten: Desktop / Handy.

„Hinweis Beispieldaten“ heißt: der Hinweis des Seitenrahmens (`#beispieldaten`) war beim Foto sichtbar. Ob eine
Seite Beispieldaten zeigt, steht in `docs/rundgang.md`, „Datenstand je Thema“.

| Seite | Desktop | Handy | Karte | Hinweis Beispieldaten | Konsolenfehler |
|---|---|---|---|---|---|
| `index` | `index-1440.png` | `index-390.png` | geladen / geladen | nein / nein | 0 / 0 |
| `karta` | `karta-1440.png` | `karta-390.png` | geladen / geladen | nein / nein | 0 / 0 |
| `dzielnica` | `dzielnica-1440.png` | `dzielnica-390.png` | geladen / geladen | nein / nein | 0 / 0 |
| `porownanie` | `porownanie-1440.png` | `porownanie-390.png` | keine / keine | nein / nein | 0 / 0 |
| `kamienice` | `kamienice-1440.png` | `kamienice-390.png` | geladen / geladen | nein / nein | 0 / 0 |
| `kamienice-metoda` | `kamienice-metoda-1440.png` | `kamienice-metoda-390.png` | keine / keine | nein / nein | 0 / 0 |
| `kamienice-dane` | `kamienice-dane-1440.png` | `kamienice-dane-390.png` | keine / keine | nein / nein | 0 / 0 |
| `planer` | `planer-1440.png` | `planer-390.png` | geladen / geladen | nein / nein | 0 / 0 |
| `planer-metoda` | `planer-metoda-1440.png` | `planer-metoda-390.png` | keine / keine | nein / nein | 0 / 0 |
| `planer-dane` | `planer-dane-1440.png` | `planer-dane-390.png` | keine / keine | nein / nein | 0 / 0 |
| `modernizacja` | `modernizacja-1440.png` | `modernizacja-390.png` | geladen / geladen | nein / nein | 0 / 0 |
| `klimat` | `klimat-1440.png` | `klimat-390.png` | geladen / geladen | nein / nein | 0 / 0 |
| `powietrze` | `powietrze-1440.png` | `powietrze-390.png` | keine / keine | nein / nein | 0 / 0 |
| `mieszkania` | `mieszkania-1440.png` | `mieszkania-390.png` | keine / keine | nein / nein | 0 / 0 |
| `punktualnosc` | `punktualnosc-1440.png` | `punktualnosc-390.png` | keine / keine | nein / nein | 0 / 0 |
| `metoda` | `metoda-1440.png` | `metoda-390.png` | keine / keine | nein / nein | 0 / 0 |
| `dane` | `dane-1440.png` | `dane-390.png` | keine / keine | nein / nein | 0 / 0 |
| `404` | `404-1440.png` | `404-390.png` | keine / keine | nein / nein | 0 / 0 |

Grenzen: Nur Polnisch; Englisch und Deutsch prüfen `pruefen/seiten.mjs` und die Paketprüfungen im Browser, ohne Foto.
Die Fotos zeigen den Zustand nach dem Laden ohne Bedienung (keine geöffneten Fragen, keine 3D-Gebäude). Die Seite
`404` ist direkt aufgerufen.
