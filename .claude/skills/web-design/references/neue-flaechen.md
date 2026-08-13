# Neue Flächen: wenn es nichts gibt, woran anzuschließen wäre

Gilt **nur**, wenn wirklich kein bestehendes Muster passt — ein neues Produkt, eine eigenständige
Oberfläche, ein Prototyp außerhalb dieses Produkts. Innerhalb eines Projekts mit bestehendem
Design-System ist der Anschluss daran fast immer die richtige Antwort; siehe `SKILL.md`.

## Warum generische UIs entstehen

Ein Sprachmodell sagt das wahrscheinlichste nächste Token voraus. Bei Design heißt das: der Median der
Trainingsdaten. Deshalb konvergiert jedes Modell ohne Vorgaben auf dasselbe — Inter, lila Verlauf auf
Weiß, drei Karten mit abgerundeten Ecken, Hero mit großer Zahl und kleinem Label.

Das lässt sich **nicht durch bessere Adjektive im Prompt** beheben („modern", „elegant", „clean" sind
selbst Teil des Medians). Es lässt sich nur beheben, indem die Entscheidungen, die sonst übersprungen
werden, explizit getroffen werden — vor dem Code.

## Zwei Durchgänge

### Durchgang 1: Plan (vor jeder Zeile Code)

Ein kompaktes Token-System, vier Punkte, schriftlich:

- **Farbe** — 4–6 benannte Hex-Werte. Nicht mehr. Eine dominante Farbe, ein scharfer Akzent.
- **Typografie** — mindestens zwei Rollen: eine charaktervolle Display-Schrift (sparsam eingesetzt),
  eine Body-Schrift, optional eine Utility-Schrift für Daten/Labels.
- **Layout** — ein Satz Prosa plus ASCII-Wireframe. Der Wireframe zwingt zu einer Entscheidung über
  Proportion, bevor CSS sie zufällig trifft.
- **Signature** — das *eine* Element, an das man sich erinnert. Genau eines.

### Durchgang 2: Kritik (immer noch vor dem Code)

Prüf den Plan gegen die bekannten Defaults. Ehrlicher Test: Würdest du bei einem *anderen* Briefing
mit ähnlicher Form beim selben Plan landen? Dann ist es kein Entwurf, sondern ein Reflex — überarbeite
die Stelle und benenne, was du geändert hast und warum.

## Die drei AI-Defaults (Anthropic, offizielle frontend-design Skill)

1. Warmer cremefarbener Grund (~`#F4F1EA`) + kontrastreiche Serif + Terrakotta-Akzent
2. Fast schwarzer Grund + ein greller Akzent in Acid-Green oder Zinnoberrot
3. Broadsheet-Layout mit Haarlinien, `border-radius: 0`, dichte Zeitungsspalten

Alle drei sind für manche Briefings legitim. Das Problem ist, dass sie **unabhängig vom Thema**
auftauchen. Wenn das Briefing eine Richtung vorgibt, folge ihr exakt — die Worte des Briefings gewinnen
immer, auch wenn sie einen dieser Looks verlangen. Wo das Briefing frei lässt, gib die Freiheit nicht
für einen dieser Defaults aus.

## Weitere verbrannte Muster

Diese lesen sich sofort als maschinell erzeugt:

- **Schriften:** Inter, Roboto, Open Sans, Arial als Default-Griff
- **Verlaufstext:** `background: linear-gradient(...)` + `-webkit-text-fill-color: transparent`
  auf Überschriften und Kennzahlen
- **Lila-Blau-Verläufe** (`#667eea` → `#764ba2`), Cyan auf Dunkelblau (`#38BDF8` auf `#0F172A`)
- **Glassmorphism als Dekor** — `backdrop-filter: blur(10px)` überall, ohne Grund
- **Karten in Karten.** Karten sind Container, keine Standardverpackung. Verschachtelt fast nie richtig.
- **Der Hero mit großer Zahl, kleinem Label und Akzentpunkt links**
- **Nummerierte Marker (01 / 02 / 03)** wenn der Inhalt gar keine Reihenfolge ist. Struktur soll etwas
  Wahres über den Inhalt kodieren, nicht ihn schmücken.
- **Streu-Animation.** Ein orchestrierter Moment wirkt stärker als viele kleine Effekte — und zu viel
  Bewegung ist selbst ein Marker für „KI-generiert".

## Komplexität passend zur Richtung

Maximalistische Entwürfe brauchen aufwendige Ausführung; minimalistische brauchen Präzision in Abstand,
Typo und Detail. Eleganz ist, die gewählte Richtung *gut auszuführen* — nicht, sie zu verwässern.

Mut an genau einer Stelle ausgeben. Das Signature-Element ist das Erinnerungsstück, alles drumherum
bleibt ruhig und diszipliniert.

## Skalen für ein neues System

Wenn wirklich ein System von Null entsteht (Zahlen aus *Refactoring UI*):

- **Graustufen:** 8–10 Abstufungen. Weniger reicht nie für saubere Hierarchie.
- **Primärfarbe:** 1–2 Farben mit je 5–10 Abstufungen; 9 teilt sich sauber.
- **Schatten:** 5 Stufen genügen — klein (Aufmerksamkeit), mittel (Trennung), groß (Modal).
- **Sättigung:** Je weiter ein Ton von 50% Helligkeit entfernt ist, desto gesättigter muss er sein,
  damit er nicht ausgewaschen wirkt.
- **Verlaufs-Farbtöne:** innerhalb von 30° zueinander, sonst wird es schlammig.
- **Zeilenlänge:** 45–75 Zeichen.

## Graustufen zuerst

Der wirksamste Einzelgriff: **erst in Graustufen entwerfen, Farbe zuletzt.** Das erzwingt Hierarchie
über Abstand, Kontrast und Größe, statt Farbe die Arbeit machen zu lassen. Eine Fläche, die grau
funktioniert, funktioniert farbig immer — umgekehrt nie.

## CSS-Handwerk

Achte auf Selektor-Spezifität. Klassen, die sich gegenseitig aufheben, entstehen leicht — besonders
zwischen typbasierten (`.section`) und elementbasierten (`.cta`) Selektoren, und besonders bei
Paddings/Margins zwischen Abschnitten.

## Ansehen, nicht nur bauen

Screenshot machen und den eigenen Entwurf kritisieren, solange gebaut wird. Ein Bild ist 1000 Token
wert. Der Vergleich Screenshot ↔ Absicht deckt Fehler auf, die im Markup unsichtbar sind — falsche
Proportionen, gebrochener Rhythmus, unlesbarer Kontrast.
