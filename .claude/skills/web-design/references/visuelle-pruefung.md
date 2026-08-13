# Ansehen, nicht nur kompilieren

Der Grund, warum generierte Oberflächen schlecht aussehen und trotzdem „fertig" gemeldet werden: Der
Agent schreibt Markup und **sieht das Ergebnis nie**. Gebrochene Proportionen, ein Layout das bei langen
Namen zerfällt, unlesbarer Kontrast bei gedämpftem Text — im Code unsichtbar, im Bild sofort offensichtlich.

Anthropic dazu: *a picture is worth 1000 tokens*.

## Werkzeug: playwright-cli (nicht das MCP)

Microsoft hat 2026 `@playwright/cli` veröffentlicht und empfiehlt es **ausdrücklich statt des MCP** für
Coding-Agents. Gemessen: ~27.000 statt ~114.000 Token für dieselbe Aufgabe, weil das MCP komplette
Accessibility-Trees in den Kontext streamt.

Playwright ist in diesem Repo bereits vorhanden (`@playwright/test`, `frontend/tests/e2e/`). Der CLI
kommt zusätzlich, per `npx` ohne Installation.

**Der Port ist nicht fix.** SaasKiller-Projekte holen ihre Ports aus der Registry `~/coding/ports.txt`
(via `portman.sh`); der Default ist `5175` für Vite und `8002` für Django. Vor dem ersten Screenshot:

```bash
make ports              # zeigt den tatsächlichen Vite-/Django-Port dieses Projekts
```

```bash
# Server müssen laufen: make dev-be  +  make dev-fe
npx -y @playwright/cli@latest open http://localhost:5175/dashboard
npx -y @playwright/cli@latest screenshot --filename=/tmp/vorher.png
```

Für Flächen hinter dem Login: der E2E-Helfer `loginAsTestUser()` (siehe CLAUDE.md) injiziert ein JWT
direkt in `localStorage` — schneller und deterministischer als der Magic-Link-Flow. Für einen reinen
Screenshot reicht oft eine öffentliche Route (`/`, `/auth/login`).

Dann das Bild mit dem Read-Tool ansehen. **Das ist der Punkt** — nicht der Screenshot, sondern das
Anschauen.

Nützliche Befehle:

```bash
npx -y @playwright/cli@latest goto <url>
npx -y @playwright/cli@latest resize 390 844        # iPhone — wird real benutzt
npx -y @playwright/cli@latest resize 1440 900       # Desktop
npx -y @playwright/cli@latest screenshot --full-page --filename=/tmp/x.png
npx -y @playwright/cli@latest click e15             # refs kommen aus `snapshot`
npx -y @playwright/cli@latest snapshot              # Struktur statt Bild, spart Token
npx -y @playwright/cli@latest close
```

`snapshot` ist token-günstiger als ein Bild und reicht für Struktur- und Text-Fragen. Für **Design**
brauchst du das Bild — Abstand, Gewicht und Rhythmus stehen nicht im Accessibility-Baum.

## Die Schleife

Nach jeder echten UI-Änderung, mindestens einmal, besser zweimal:

1. **Aufnehmen** — Screenshot der geänderten Fläche
2. **Ansehen** — Bild mit Read öffnen
3. **Benennen** — konkrete Unterschiede zur Absicht aufschreiben, in diesen Kategorien:
   - Grössenhierarchie: ist erkennbar, was das Wichtigste ist?
   - Rhythmus: sind die Abstände gleichmässig, gruppieren sie richtig?
   - Dichte: atmet es, oder klebt alles?
   - Kontrast: ist Nebensächliches wirklich leiser?
4. **Korrigieren** — die benannten Punkte, nicht alles
5. **Wiederholen** — einmal

Vage Selbstkritik („sieht gut aus") ist wertlos. Nützlich ist: *„Die drei Filterzeilen haben denselben
Abstand wie die Listeneinträge, dadurch wirkt der Kopf wie Teil der Liste."*

## Pflichtansichten

Eine Fläche ist nicht geprüft, solange nicht angesehen wurde:

- **Mobil (390px)** — diese Frontends werden real auf dem Telefon benutzt
- **Desktop (1440px)**
- **Themes** — SaasKiller ist per Default light-only. Ergänzt ein Fork Dark Mode, gehört er in
  `app.css` und in diese Liste; ein hart codierter Farbwert bricht dann eines der beiden
- **Leer und übervoll** — 0 Einträge und viele; sehr lange Namen

## Urteil beim Nutzer einholen

Für echtes Design-Feedback statt Selbsteinschätzung:

```bash
npx -y @playwright/cli@latest show --annotate
```

Der Nutzer zeichnet Kästen auf die laufende Seite und schreibt Kommentare dazu; zurück kommen
annotierter Screenshot, Snapshot der markierten Stelle und die Notizen. Genau dann einsetzen, wenn
„das sieht schlecht aus" im Raum steht — es macht aus einem Gefühl eine bearbeitbare Liste.

## Einschränkungen, ehrlich

- `@playwright/cli` steht bei **0.1.x** — jung, kann sich ändern.
- Microsofts eigener Skill sagt zum Screenshot: *„rarely used, as snapshot is more common"*. Das Werkzeug
  ist auf Testautomatisierung optimiert; für Design nutzt ihr es gegen den Strich. Funktioniert, ist aber
  kein ausgereifter Design-Workflow.
- Ein Screenshot beweist nicht, dass etwas *gut* ist — nur, dass es nicht offensichtlich kaputt ist.
  Er ersetzt kein Urteil, er ermöglicht eines.

## Nicht überziehen

Screenshots kosten Kontext. Nicht nach jeder Zeile. Sinnvoll ist:

- nach einer fertigen Fläche oder einem grösseren Umbau — **ja**
- bei jedem kleinen Textwechsel — nein
- wenn der Nutzer sagt, etwas sehe schlecht aus — **immer**, plus `show --annotate`
