# shadcn-svelte: erst nachsehen, dann bauen

Der grösste einzelne Qualitätshebel ist **nicht** besseres Design-Gefühl, sondern die Registry
überhaupt zu benutzen. Gemessen in diesem Repo am 13.8.26:

| | |
|---|---|
| Komponenten in der Registry | **56** |
| davon installiert | **9** |
| **ungenutzt** | **47** |
| Blocks verfügbar | **147** |
| davon genutzt | **0** |

Installiert sind: `badge`, `button`, `card`, `input`, `label`, `select` (als eigene
`native-select.svelte`), `sidebar`, `site-header` (Eigenbau, kein Registry-Eintrag), `textarea`.

Das ist eine bewusste Boilerplate-Entscheidung — nicht jedes Projekt braucht 56 Komponenten. Aber
es heisst auch: **fast alles, was über ein Formular hinausgeht, fehlt noch.** Wer nur `button`,
`input` und `card` hat, baut zwangsläufig flache Knopfwände. Nicht installiert und deshalb typisch
nachgebaut: `dropdown-menu`, `popover`, `command`, `dialog`, `sheet`, `table`/`data-table`, `tabs`,
`tooltip`, `skeleton`, `empty`, `switch`, `checkbox`, `toggle-group`, `sonner`.

## Regel 1: Nachsehen ist Pflicht, nicht Kür

**Bevor du irgendeine UI-Struktur selbst baust**, prüf, ob es sie gibt:

```bash
# Alle Komponenten
curl -s https://shadcn-svelte.com/registry/index.json \
  | python3 -c "import json,sys; [print(i['name']) for i in json.load(sys.stdin) if i['type']=='registry:ui']"

# Alle Blocks (fertige Layouts)
curl -s https://shadcn-svelte.com/registry/index.json \
  | python3 -c "import json,sys; [print(i['name']) for i in json.load(sys.stdin) if i['type']=='registry:block']"

# Was ist schon da?
ls frontend/src/lib/components/ui/
```

Installieren:

```bash
cd frontend && npx shadcn-svelte@latest add <name>
```

**Kein MCP verwenden.** Der offizielle shadcn-MCP ist mit shadcn-svelte inkompatibel — die Svelte-Registry
liefert `files` ohne `path`, das React-Schema verlangt es (`PARSE_ERROR`, getestet 13.8.26). Der
`shadcn-svelte`-CLI hat kein `mcp`-Kommando. Der CLI plus `curl` reichen vollständig.

## Regel 2: Nie nachbauen, was es gibt

Zwei der installierten Komponenten sind Eigenbauten:

| Eigenbau | offiziell | Bemerkung |
|---|---|---|
| `select` (`native-select.svelte`) | `select` | bewusst nativ gehalten; für Suchen/Gruppen das offizielle holen |
| `site-header` | — | echter Eigenbau, in Ordnung (hat einen Django-Zwilling, siehe CLAUDE.md) |

Nicht blind ersetzen — bestehende Eigenbauten laufen. Aber **nichts Neues** in dieser Art bauen, und beim
Anfassen einer Stelle auf das Offizielle wechseln, wenn es ohne Bruch geht.

## Regel 3: Bei neuen Flächen mit einem Block anfangen

Ein Block ist ein fertiges Layout — mit Hierarchie, Responsive-Verhalten und Zuständen, die jemand
durchdacht hat. Das ist der Unterschied zwischen „aus Primitiven zusammengesetzt" und „gestaltet".

Nützliche Blocks (geprüft):

- **`dashboard-01`** — vollständiges Dashboard: 15 Dateien, zieht 18 Komponenten (`sidebar`, `chart`,
  `data-table`, `tabs`, `dropdown-menu`, `badge`, `avatar` …)
- **`sidebar-01` … `sidebar-16`** — 16 Navigationsvarianten. `sidebar-07` (collapsible + Breadcrumb +
  Nutzermenü) ist der übliche Startpunkt für App-Shells
- **`login-01` … `-05`**, **`signup-01` … `-05`**, **`otp-01` … `-05`** — Auth-Flächen
- **`chart-*`** — rund 60 fertige Diagramme (Area, Bar, Line, Pie, Radar, Radial)

```bash
npx shadcn-svelte@latest add dashboard-01
```

Danach gehört der Code euch: anpassen, entfernen, ans eigene System angleichen. **Wichtig:** Blocks
kommen im shadcn-Default-Look (runde Ecken, weiche Schatten). Nach dem Einfügen an das System des
Projekts angleichen (`frontend/src/app.css`) — im Boilerplate heisst das `--radius: 0`, harte Kanten,
Papier/Tinte, mono-Labels. Die Struktur übernehmen, die Optik anpassen.

## Regel 4: Die richtige Komponente für den Zweck

Häufige Fehlgriffe und was stattdessen gehört:

| Statt | Nimm | Warum |
|---|---|---|
| Buttons als Filter-Umschalter | `toggle-group` | ein Toggle, der wie eine Aktion aussieht, lügt |
| mehrere Filterzeilen untereinander | `dropdown-menu` / `popover` | Beiwerk gehört zusammengefaltet |
| eigene Suchliste | `command` | Palette mit Tastatur, kennt jeder |
| `<table>` von Hand | `data-table` | Sortierung, Auswahl, Spalten inklusive |
| Formular aus `input` + `label` | `form` + `field` | Validierung und Fehlerdarstellung inklusive |
| `Lädt…` als Text | `skeleton` / `spinner` | Platzhalter in Form des Inhalts |
| „keine Daten" | `empty` | Zustand mit Handlungsaufforderung |
| eigene Modale | `dialog` / `sheet` / `drawer` | Fokusfalle und Escape sind gelöst |
| Tooltip-Eigenbau | `tooltip` / `hover-card` | Positionierung und Touch sind gelöst |
| eigene Toasts | `sonner` | Stapelung, Timing, a11y sind gelöst |

## Regel 5: Barrierefreiheit kommt gratis — wirf sie nicht weg

Die Komponenten bauen auf `bits-ui`. Tastaturbedienung, Fokusfallen, ARIA-Rollen und Screenreader-
Ankündigungen sind darin gelöst. Ein `<div onclick>` statt `button` wirft genau das weg, und niemand
merkt es beim Ansehen — nur beim Benutzen.

## Bestehende Flächen sanieren

Nicht alles auf einmal. Reihenfolge nach Wirkung:

1. **Inventur** — welche Komponenten fehlen für diese Fläche? (Liste oben)
2. **Installieren** — was fehlt, mit `add` holen
3. **Struktur ersetzen** — das grösste Problem zuerst (meist: Control-Stapel → `dropdown-menu`)
4. **Hierarchie** — Regeln aus `SKILL.md` anwenden
5. **Zustände** — leer/lädt/Fehler/übervoll prüfen
6. **Ansehen** — Screenshot, Vergleich, Nachbessern (`references/visuelle-pruefung.md`)

Schritt 3 vor Schritt 4: Hierarchie in eine falsche Struktur zu bauen ist verlorene Arbeit.
