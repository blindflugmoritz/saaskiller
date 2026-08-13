# Diesen Skill beim Fork kalibrieren

Dieser Skill lebt im Boilerplate und wird bei jedem `setup.sh`-Fork mitkopiert. Die Regeln
(Hierarchie, Abstandsrhythmus, Zustände, Registry-Disziplin, Screenshot-Schleife) gelten unverändert
— **die Zahlen und die Antipattern-Liste nicht.** Beides ist gemessen, nicht vermutet, und gilt für
das Boilerplate. **Ein Skill mit falschen Zahlen ist schlimmer als keiner** — er behauptet Autorität,
die er nicht hat.

## Dateien

| Datei | Inhalt | beim Fork anpassen? |
|---|---|---|
| `SKILL.md` | Hierarchie, Abstand, Zustände, Sprache, Checkliste | **ja** — Zahlen + Antipatterns |
| `references/shadcn-registry.md` | Registry-Inventur, Blocks, Komponentenwahl | **ja** — nur die Zahlen |
| `references/visuelle-pruefung.md` | Screenshot-Schleife mit `playwright-cli` | fast nicht — nur Port/Routen |
| `references/neue-flaechen.md` | Greenfield-Design, AI-Defaults, Skalen | nein — projektunabhängig |
| `PORTIEREN.md` | diese Datei | — |

Kein Setup nötig. Skills unter `.claude/skills/<name>/SKILL.md` werden automatisch geladen; die
`references/` liest der Agent bei Bedarf nach.

## 1. Die Messungen neu erheben

```bash
cd <projekt>/frontend

# Typografie-Verteilung — zeigt fehlende Hierarchie
grep -rhoE 'text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|\[[0-9]+px\])' src | sort | uniq -c | sort -rn

# Ad-hoc-Pixelwerte — zeigt umgangene Skala
grep -rhoE 'text-\[[0-9]+px\]' src | sort | uniq -c | sort -rn

# Abstands-Rhythmus — zeigt fehlende Ordnung
grep -rhoE 'space-y-[0-9.]+' src | sort | uniq -c | sort -rn

# Registry-Ausnutzung
curl -s https://shadcn-svelte.com/registry/index.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len([i for i in d if i['type']=='registry:ui']),'Komponenten,',len([i for i in d if i['type']=='registry:block']),'Blocks')"
ls src/lib/components/ui/ | wc -l
```

Ergebnisse eintragen in: `SKILL.md` (Einleitung, Punkt 0 der Reihenfolge, Abschnitt „Abstand") und
`shadcn-registry.md` (Tabelle oben + Liste der installierten Komponenten).

**Bei React-shadcn** stattdessen `https://ui.shadcn.com/r/index.json` — dort funktioniert auch der
offizielle MCP (`pnpm dlx shadcn@latest mcp init --client claude`), der mit **Svelte** nicht geht.

**Stand der aktuellen Zahlen im Boilerplate: 13.8.26.** Wenn das lange her ist, auch hier neu messen.

## 2. Die Antipattern-Liste neu füllen

Der Abschnitt „Antipatterns — im Fork zu ersetzen" in `SKILL.md` ist der wertvollste Teil und
**komplett projektspezifisch**. Er stammt aus mozcrm2 und ist im Boilerplate als „noch nicht gemessen"
markiert. Diese Markierung bleibt so lange stehen, bis jemand sie ersetzt.

Vorgehen: zwei, drei echte Seiten des Projekts ansehen (Screenshot, nicht nur Code) und aufschreiben,
was dort real schiefgeht. Keine Vermutungen, keine Lehrbuch-Fehler — nur was im Code steht. Danach den
Warnkasten entfernen.

## 3. Das Design-System eintragen

`SKILL.md` verweist auf `frontend/src/app.css` als Ort des Systems. Im Boilerplate steht dort das
Swiss/Poster-System (`--radius: 0`, Papier/Tinte, Rot/Blau/Gelb, light-only). Ändert ein Fork das
System, gehören Tokens, Farbrollen und Theme-Situation in `SKILL.md` (Abschnitte „Farbe" und
„Qualitätsboden") und in `visuelle-pruefung.md` (Pflichtansichten) nachgezogen.

## 4. Sprache

Der Skill ist deutsch geschrieben, das Boilerplate-Interface englisch. Bei einem Projekt mit anderer
Interface-Sprache den Abschnitt „Sprache im Interface" anpassen — und wenn Paraglide aktiv ist, den
Hinweis auf `m.*()` behalten.

## 5. Ports und Kommandos

`visuelle-pruefung.md` nennt `make ports`, `make dev-be`/`make dev-fe` und die Defaults 8002/5175.
Weicht ein Fork davon ab (eigene Skripte, Docker, anderer Devserver), dort anpassen.

## Reihenfolge

1. Messungen laufen lassen (Block oben), Zahlen eintragen
2. Zwei, drei echte Seiten ansehen → Antipattern-Liste neu schreiben, Warnkasten entfernen
3. Design-System-Verweise prüfen
4. Ports/Kommandos prüfen
5. Prüfen: `npx -y @playwright/cli@latest open http://localhost:<port>` und ein Screenshot
6. Testen: „bau mir Seite X" — lädt der Skill, und stimmen die Aussagen?

## Prüfen, ob er wirkt

Der Skill ist nur Text im Kontext; er garantiert nichts. Der ehrliche Test ist nicht „wurde er
geladen", sondern: **eine Fläche bauen lassen, ansehen, und mit dem Ergebnis von vorher vergleichen.**
Wenn kein Unterschied sichtbar ist, sind die Regeln zu allgemein — dann fehlen projektspezifische
Antipatterns (Punkt 2).
