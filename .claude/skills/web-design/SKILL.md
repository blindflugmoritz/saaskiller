---
name: web-design
description: Design rules for building AND for fixing web UI in this repo (SvelteKit + Tailwind 4 + shadcn-svelte). Read BEFORE writing markup or CSS for a page, view, widget, list, form, table, dialog or dashboard — not after. Covers which shadcn-svelte components/blocks to install instead of hand-building, visual hierarchy, spacing rhythm, states, and the screenshot review loop. Triggers: new route/+page.svelte, new component under lib/components, "baue eine Seite/Ansicht/Maske", "mach das UI", "sieht schlecht/hässlich aus", "überarbeite/optimiere die Ansicht", "mach das schöner", UI-Refactor, any layout/spacing/typography/colour decision.
---

# Web-Design in SaasKiller

SaasKiller ist das Boilerplate, aus dem Forks entstehen. Dieser Skill gilt hier **und wird
mitgeforkt** — deshalb ist er bewusst generisch gehalten, aber auf **gemessene Zahlen dieses
Repos** gestützt. Beim Fork müssen die Zahlen neu erhoben werden, siehe `PORTIEREN.md`.

Das Design-System des Projekts steht in `frontend/src/app.css`. Deine Aufgabe ist fast nie, ein
neues zu erfinden — sondern das vorhandene *diszipliniert anzuwenden*. Oberflächen werden nicht
hässlich, weil sie zu zahm sind. Sie werden hässlich, weil **alles gleich wichtig aussieht**.

Gemessen im Boilerplate (Stand 13.8.26): 64 von 119 Text-Klassen sind `text-sm` oder `text-xs`.
Die Mitte (`text-lg`/`text-xl`) kommt zusammen nur 14-mal vor, während `text-2xl` und grösser
30-mal auftauchen — der Sprung von klein auf gross passiert also fast ohne Zwischenstufe. Der
vertikale Rhythmus kennt bereits **acht** verschiedene Abstände (`space-y-1.5` bis `space-y-12`),
und zwei Stellen umgehen die Skala mit `text-[11px]`. Eine Fläche, auf der alles `text-sm` ist,
hat keine Hierarchie — sie hat eine Textur.

## Die Reihenfolge (nicht verhandelbar)

Erst Material, dann Struktur, dann Ton. Wer mit Farben und Rahmen anfängt, dekoriert ein Problem,
statt es zu lösen.

0. **Was gibt die Registry her?** → `references/shadcn-registry.md`. **Immer zuerst.** 47 von 56
   Komponenten sind hier ungenutzt, 147 Blocks nie angefasst — flache Knopfwände kommen genau
   daher. Nie selbst bauen, was es fertig gibt.
1. **Was ist die eine Aufgabe dieser Fläche?** In einem Satz. Eine Seite, die drei Dinge gleich gut
   können will, kann keines gut. Schreib den Satz in einen Kommentar über das Markup.
2. **Was ist das eine wichtigste Element?** Genau eins. Das bekommt Größe, Gewicht und Ruhe drumherum.
3. **Was ist Beiwerk?** Alles andere. Beiwerk wird *leiser* gemacht (`text-muted-foreground`, kleiner),
   nicht mit Rahmen und Badges lauter.
4. **Was kann weg?** Chanel-Regel: vor dem Rausgehen ein Accessoire ablegen. Der häufigste Fehler
   sind Controls, die niemand vermisst hätte.
5. **Erst jetzt** Farbe, Rahmen, Icons.
6. **Ansehen** → `references/visuelle-pruefung.md`. Screenshot, kritisieren, nachbessern. Ohne diesen
   Schritt ist eine Fläche nicht geprüft, sondern nur kompiliert.

## Hierarchie: das eigentliche Werkzeug

Hierarchie entsteht aus **Größe, Gewicht, Farbe und Abstand** — in dieser Reihenfolge. Nicht aus Rahmen,
nicht aus Badges, nicht aus Emoji.

**Drei Ebenen, mehr nicht:**

| Ebene | Rolle | Mittel |
|---|---|---|
| Primär | worum es geht | groß + `font-semibold` + volle Tinte |
| Sekundär | Kontext dazu | `text-sm`, volle Tinte oder leicht gedämpft |
| Tertiär | Metadaten, Labels, Zähler | `text-xs`, `text-muted-foreground`, ggf. mono |

Wenn du eine vierte Ebene brauchst, ist die Fläche zu voll. Teile sie, statt eine Zwischengröße zu erfinden.

**Der Trick, der am häufigsten verpasst wird:** Rang wird meistens durch *Wegnehmen* erzeugt. Statt das
Wichtige größer zu machen, mach das Unwichtige leiser. Eine Zeile aus Name + Firma + Ort liest sich
richtig, wenn nur der Name volle Tinte hat — nicht wenn der Name fett *und* gerahmt *und* farbig ist.

**Label-Wert-Paare zusammenziehen.** `Ort: Zürich` ist zwei Elemente, die um Aufmerksamkeit konkurrieren.
`Zürich` mit dem Label als kleinem, gedämpftem Eyebrow darüber ist eines. Wenn der Wert selbsterklärend
ist (eine Adresse, ein Datum), lass das Label ganz weg.

## Typografie: benutz die Skala

**Erlaubt sind die Tailwind-Stufen.** `text-[11px]` ist ein Symptom, kein Feature: es heißt, dass zwischen
`xs` (12px) und `sm` (14px) etwas fehlte — meistens fehlte aber nur der Mut, `text-sm` zu nehmen und
stattdessen die *Farbe* zu dämpfen.

- Fließtext und Listeninhalte: `text-sm` (Default) oder `text-base`
- Metadaten, Eyebrows, Zähler: `text-xs`
- Seitentitel: `text-3xl sm:text-4xl` mit `.title`
- Abschnittstitel: `text-lg` oder `text-xl` — **diese Mitte ist fast ungenutzt, benutz sie**

Ausnahme für neue Ad-hoc-Werte: nur bei bewusst gesetzten Display-Zahlen (die `text-7xl`-Momente).
Dort ist der Sprung die Aussage. Überall sonst: Skala.

**Zeilenlänge 45–75 Zeichen.** Fließtext ohne `max-w-prose` (oder `max-w-2xl`) ist auf einem 27"-Monitor
unlesbar. Betrifft jede Erklärung, jeden Hilfetext, jede leere-Zustand-Beschreibung.

**Zwei bis drei Gewichte, nicht mehr.** `font-normal`, `font-semibold`, und mono für Daten/Labels.
`font-bold` überall ist dasselbe wie nirgends.

## Abstand: ein Rhythmus, nicht acht

Der vertikale Rhythmus einer Seite darf **drei Werte** kennen, nicht acht:

- **`space-y-8`** zwischen Abschnitten (großer Sprung — sagt: neues Thema)
- **`space-y-4`** zwischen Blöcken innerhalb eines Abschnitts
- **`space-y-1`** innerhalb einer Einheit (Titel + Untertitel gehören zusammen)

`space-y-1.5`, `space-y-2`, `space-y-3`, `space-y-6` bitte nicht neu einführen — der Unterschied ist
nicht wahrnehmbar, aber die Inkonsistenz ist es. Bestehende Vorkommen beim Anfassen einer Datei mit
angleichen, nicht in einem separaten Refactor. (`space-y-10`/`-12` kommen in den Marketing-Sektionen
der Startseite vor; dort ist der grosse Sprung Absicht — in App-Flächen nicht.)

**Gruppierung schlägt Trennung.** Abstand ist das primäre Mittel, um zu zeigen was zusammengehört. Ein
`<hr>` oder ein Rahmen ist erst nötig, wenn Abstand nicht reicht — und das ist selten. Wenn zwischen
zwei Blöcken derselbe Abstand steht wie innerhalb eines Blocks, ist die Struktur unlesbar, egal wie
viele Linien du ziehst.

**Großzügig anfangen, dann wegnehmen.** Nie umgekehrt. Zu enge Layouts wirken billig; das ist der
schnellste sichtbare Qualitätsgewinn überhaupt.

## Antipatterns — im Fork zu ersetzen

> **Achtung:** Dieser Abschnitt stammt aus mozcrm2 (dem ersten Fork) und ist dort gemessen, nicht
> hier. Im Boilerplate gibt es kaum echte Produktseiten, also gibt es auch kaum echte Antipatterns.
> **Beim Fork ersetzen:** zwei, drei echte Seiten des Projekts ansehen und aufschreiben, was dort
> real schiefgeht — keine Vermutungen, keine Lehrbuch-Fehler. Bis dahin gelten die folgenden als
> plausible Warnungen, nicht als Befund über dieses Repo.

**Der Control-Stapel.** Mehrere Zeilen Filter untereinander (Sortierung, Toggles, Tags, aktive Filter),
alle Buttons in `size="sm"`, alle gleich gewichtet. Der Nutzer sieht eine Wand aus Knöpfen und findet
den Inhalt nicht. → Primäraktion sichtbar abheben, sekundäre Filter in ein `dropdown-menu`/`popover`
falten, und den Inhalt oben halten. Filter sind Beiwerk, keine Überschrift. Das ist meist kein Design-,
sondern ein Materialproblem: `dropdown-menu`, `popover` und `command` sind schlicht nicht installiert.

**Buttons als Filter-Umschalter.** `<Button variant="outline">` für Tag-Filter ist semantisch und
visuell falsch → `toggle-group`. Ein Umschalter, der aussieht wie eine Aktion, lügt über das, was er tut.

**Emoji als Icon-Ersatz.** `📦 Archiv`, `★ Favoriten`, `✕ Filter zurücksetzen`. Emoji rendern je nach
Plattform anders, brechen die Grundlinie und passen nicht zu einem Swiss-System. → `button` mit
`size="icon"` und echte Icons, oder schlicht Text ohne Zeichen davor.

**Alles ist `text-sm`.** Siehe oben. Der häufigste Einzelfehler — und der einzige aus dieser Liste,
der im Boilerplate messbar vorkommt.

**Zähler und Status als Extra-Element.** `{count} Treffer` in eigener Zeile mit eigenem Button daneben
ist ein Block für eine Zahl. → An den Titel anlagern oder in die bestehende Zeile integrieren.

## Eine bestehende Fläche sanieren

Wenn etwas schon existiert und schlecht aussieht, gilt dieselbe Reihenfolge — aber diszipliniert, sonst
wird ein Umbau daraus, der nie fertig wird.

1. **Ansehen.** Screenshot des Ist-Zustands, mobil und Desktop
   (`references/visuelle-pruefung.md`). Ohne Bild diagnostizierst du blind.
   Wenn der Nutzer sagt „sieht schlecht aus": `show --annotate` und ihn zeigen lassen, wo.
2. **Benennen.** Was genau ist kaputt? Meist eines von dreien: kein Rang (alles gleich groß), keine
   Gruppierung (Abstände überall gleich), oder Controls, die den Inhalt verdrängen.
3. **Material prüfen.** Fehlt eine Komponente, die das Problem strukturell löst? Ein Control-Stapel
   ist kein Design-Fehler, sondern ein fehlendes `dropdown-menu`.
4. **Struktur vor Kosmetik.** Erst die falsche Struktur ersetzen, dann Hierarchie und Abstand. Wer
   Hierarchie in eine falsche Struktur baut, macht die Arbeit zweimal.
5. **Wieder ansehen.** Vorher/Nachher vergleichen. Wenn du den Unterschied nicht benennen kannst, hat
   sich nichts verbessert.

**Nicht alles auf einmal.** Eine Fläche pro Durchgang, fertig machen, ansehen. Ein Repo-weiter
Design-Refactor in einem Zug ist nicht überprüfbar und wird nicht besser, sondern nur anders.

**Bestehende Abweichungen** (`text-[11px]`, `space-y-3`) beim Anfassen einer Datei mitziehen — aber kein
eigener Refactor nur dafür. Der Nutzen steht nicht im Verhältnis zum Risiko.

## Zustände sind Teil des Designs, nicht ein Nachtrag

Jede Fläche, die Daten lädt, braucht **vier** Zustände — und zwar bevor du „fertig" sagst:

1. **Leer** — eine Einladung zum Handeln, kein „Keine Daten". Sag, was hier stünde und wie es dahin
   kommt. Die offizielle Komponente heisst `empty`.
2. **Lädt** — `skeleton` in der Form des kommenden Inhalts. Nicht `Lädt…` als mono-Text; das ist ein
   Platzhalter für einen Platzhalter.
3. **Fehler** — was passiert ist und was jetzt zu tun ist. Fehler entschuldigen sich nicht und bleiben
   nie vage.
4. **Gefüllt, aber extrem** — 1 Eintrag und 5000 Einträge. Sehr lange Namen. Fehlende Felder. Wenn ein
   Layout bei einem 60-Zeichen-Namen bricht, ist es nicht fertig.

## Sprache im Interface

Die Sprache des Projekts konsequent durchhalten (Boilerplate: englisch; Forks oft deutsch — und wenn
Paraglide aktiv ist, geht jeder Text durch `m.*()`). Text ist Designmaterial, keine Dekoration.

- **Aus Nutzersicht benennen**, nicht aus Systemsicht. „Erinnerungen", nicht „Reminder-Objekte".
- **Aktiv und konkret.** Ein Knopf sagt, was passiert: „Person anlegen", nicht „Absenden".
- **Ein Wort, ein Ding, überall.** Der Knopf „Speichern" erzeugt die Meldung „Gespeichert". Wenn die
  Liste „Menschen" heißt, heißt sie nicht anderswo „Kontakte".
- **Spezifisch schlägt clever.** Immer.

## Qualitätsboden (ohne Ankündigung erfüllen)

- Responsive bis zum Telefon. Diese Frontends werden real auf dem iPhone benutzt.
- Sichtbarer Tastaturfokus — `--ring` ist definiert, nicht wegstylen.
- Kontrast: `text-muted-foreground` ist für Metadaten gedacht, nicht für Fließtext.
- Klickflächen ≥ 44px auf Touch.
- Themes geprüft: SaasKiller ist per Default **light-only**; wer in einem Fork Dark Mode ergänzt,
  prüft beide. Hart codierte Farbwerte brechen das in jedem Fall.
- `prefers-reduced-motion` respektieren, falls Animation im Spiel ist.

## Farbe

Die Palette ist fertig und **abschließend**: Papier/Tinte plus die Akzente aus `app.css`. Nimm die
Tokens (`bg-primary`, `text-muted-foreground`, `bg-red`/`bg-blue`/`bg-yellow`), **nie** eigene
Hex-Werte und keine neuen Farben.

Farbe trägt Bedeutung, nicht Dekoration: Rot ist destruktiv, Blau ist Fokus/Link. Ein gelber Kasten,
weil die Fläche „etwas leer wirkt", ist genau der Fehler, den dieses System vermeiden soll.

**Grauwert-Test:** Wenn die Fläche in reinem Graustufen-Zustand keine erkennbare Hierarchie hat, ist sie
nicht fertig — dann trägt Farbe eine Last, die Größe und Abstand tragen müssten.

## Wenn du wirklich etwas Neues gestaltest

Nur wenn es *keine* bestehende Fläche gibt, an die anzuschließen wäre (also selten). Dann gilt zusätzlich
`references/neue-flaechen.md`: kurzer Plan (Farbe/Typo/Layout/Signature) **vor** dem Code, gegen die
bekannten AI-Defaults geprüft.

## Bevor du fertig sagst

Geh das durch — nicht überfliegen:

- [ ] Registry geprüft; nichts selbst gebaut, was es fertig gibt
- [ ] Die eine Aufgabe der Fläche ist benennbar
- [ ] Genau ein Element ist offensichtlich das wichtigste
- [ ] Drei Hierarchie-Ebenen, nicht vier
- [ ] Keine neuen `text-[Npx]`-Werte
- [ ] Rhythmus aus `space-y-8/4/1`
- [ ] Fließtext hat eine Zeilenlängenbegrenzung
- [ ] Alle vier Zustände existieren (leer, lädt, Fehler, extrem gefüllt)
- [ ] Keine Emoji als Icons
- [ ] Keine hart codierten Farben
- [ ] Etwas wurde weggelassen
- [ ] **Angeschaut** — Screenshot mobil *und* Desktop, nicht nur kompiliert

Der letzte Punkt ist kein Formalismus. Ohne Bild weißt du nicht, ob es funktioniert — du weißt nur,
dass es baut.

## Die drei Referenzen

- `references/shadcn-registry.md` — was es fertig gibt, und warum Selbstbauen die Ursache des Problems
  ist. **Zuerst lesen.**
- `references/visuelle-pruefung.md` — Screenshot-Schleife mit `playwright-cli`, und wie man beim Nutzer
  echtes Design-Urteil einholt (`show --annotate`).
- `references/neue-flaechen.md` — nur für echtes Neu-Gestalten ohne bestehendes Vorbild. Selten.

Ausserdem: `PORTIEREN.md` — wie dieser Skill beim Fork kalibriert wird (Zahlen neu messen,
Antipatterns neu füllen).
