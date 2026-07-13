# Migrating an existing SaasKiller fork to the Swiss design system

**Who this is for:** a Claude instance (or developer) working *inside* an existing
SaasKiller fork that was created before the Swiss/poster design + shadcn-svelte
components landed in the template. It describes what to adopt and change so you
can apply it yourself, with full knowledge of the fork's own code.

**Golden rule:** this is a *design* migration. Never overwrite product code
(your own Django apps, stores, business logic, feature routes). Only the files
listed below change. Work on a branch and verify before merging.

---

## 0. Before you start

- Confirm the fork has the required deps (it almost certainly does — same
  template lineage): `bits-ui`, `clsx`, `tailwind-merge`, `tailwind-variants` in
  `frontend/package.json`, and `frontend/src/lib/utils/cn.ts` exporting `cn`.
  If `cn.ts` is missing, create it:
  ```ts
  import { clsx, type ClassValue } from 'clsx';
  import { twMerge } from 'tailwind-merge';
  export function cn(...inputs: ClassValue[]): string { return twMerge(clsx(inputs)); }
  ```
- Confirm Tailwind 4 (`@tailwindcss/vite`, `@import 'tailwindcss'` in `app.css`).
  If the fork is on Tailwind 3 with a `tailwind.config.js`, STOP — that's a
  bigger migration; ask the user first.
- Create a branch: `git checkout -b feature/swiss-design`.

The reference implementation is the **saaskiller template** (this repo). If you
have it locally (e.g. `~/coding/saaskiller`), copy files from there. Otherwise
fetch them from `https://github.com/blindflugmoritz/saaskiller` (branch `main`).

---

## 1. Adopt (copy verbatim — these are new files, no conflict with your code)

Copy these from the template's `frontend/` into the fork's `frontend/`:

```
components.json
src/lib/components/ui/button/     (button.svelte, index.ts)
src/lib/components/ui/input/      (input.svelte, index.ts)
src/lib/components/ui/label/      (label.svelte, index.ts)
src/lib/components/ui/badge/      (badge.svelte, index.ts)
src/lib/components/ui/card/       (card.svelte + card-*.svelte, index.ts)
src/lib/components/ui/textarea/   (textarea.svelte, index.ts)
src/lib/components/ui/select/     (native-select.svelte, index.ts)
src/lib/components/ui/sidebar/    (sidebar.svelte, index.ts)
```

These import only `$lib/utils/cn`, `bits-ui`, `tailwind-variants` — all already
present. Nothing here references the project name, so no renaming needed.

> If `components.json` has an `aliases.utils` value, make sure it points at your
> `cn` location (`$lib/utils/cn`). It's the same across forks.

---

## 2. Replace `frontend/src/app.css`

Replace the whole file with the template's `app.css` (the Swiss token system).
It defines the palette once as `:root` vars in shadcn's schema, maps them into
`@theme inline`, sets base body styles, and adds the Swiss utility classes
(`.eyebrow`, `.title`, `.rule`, `.rule-thin`, `.mk`, `.mk-sq/ci/tr`).

**Check first:** if your fork added custom CSS to `app.css` (fonts, extra
`@theme` tokens, project-specific classes), don't blow it away — merge: take the
template's `:root` + `@theme inline` + `@layer base` + `@layer components`
blocks, then re-append your custom additions at the end.

---

## 3. Restyle your screens (this is where YOUR code matters)

The template rewrote every screen under `src/routes/` to use the components +
Swiss utilities. **Your fork's routes are different** — you have your own pages.
So don't copy the template's route files blindly. Instead, apply the *conventions*
to your own pages:

- Replace raw `<button>` → `<Button variant="…">` (`$lib/components/ui/button`).
  Variants: default / secondary / outline / destructive / ghost / link.
- Replace raw `<input>` → `<Input>`, `<label>` → `<Label for=…>`,
  `<textarea>` → `<Textarea>`, `<select>` → `<NativeSelect>`.
- Cards → `import * as Card from '$lib/components/ui/card'`.
- **No rounded corners** — remove every `rounded-md`/`rounded-lg`. Sharp edges.
- Headings: `font-display font-bold` (or `font-black` for hero). Labels/meta:
  `font-mono uppercase tracking-wider`, or use `.eyebrow`.
- Colours from tokens only: `bg-primary text-primary-foreground`,
  `text-muted-foreground`, `text-destructive`, `border-border`, and the accents
  `bg-red / bg-blue / bg-yellow / bg-green`. No hardcoded hex, no `bg-blue-600`.
- Dividers: `.rule` (6px) / `.rule-thin` (2px).
- Markers: `<span class="mk mk-sq"></span>` (red square), `mk-ci` (blue circle),
  `mk-tr` (yellow triangle).

**Reference files to copy the pattern from** (in the template): `auth/login/+page.svelte`,
`auth/signup/+page.svelte`, `dashboard/settings/+page.svelte`. Read them to see
exactly how the components + utilities are used, then apply the same to your pages.

### Auth + dashboard shells

- `src/routes/auth/+layout.svelte`: the template uses a hard-bordered card with a
  top yellow rule (no rounding, no shadow). Safe to copy verbatim if your fork
  hasn't customised the auth frame.
- `src/routes/dashboard/+layout.svelte`: the template uses the **Swiss sidebar
  shell** (`Sidebar` component, nav items with markers, user footer, logout).
  Copy it, then **edit the `nav` array** to match YOUR fork's dashboard routes
  (the template's are Overview/Settings — yours differ). Also confirm the brand
  string and the `authStore` API names match your fork.
  - If you copy the sidebar layout, remove any per-page `<header>` from your
    dashboard pages so you don't get a double header.

### Feature-gated pages

If your fork kept billing/workspaces/api-keys, the template's versions of those
pages are already Swiss-styled — but only copy them if your page logic is
unchanged from the template. If you've customised them, restyle by hand instead.

---

## 4. Verify (do not skip)

```bash
cd frontend
npm run check      # must be 0 errors
npm run build      # must succeed
```

Then run it and look: `make dev-be` + `make dev-fe`, open the login page and the
dashboard. Confirm: black bar + yellow rule, mono eyebrows, Helvetica headings,
sharp-cornered buttons, the sidebar with geometric markers. Screenshot if you can.

If `svelte-check` complains about a component import, check the import path
(`$lib/components/ui/<name>`) and that the folder + `index.ts` were copied.

---

## 5. Commit

Commit on the branch with a clear message, then merge to the fork's main once
you've seen it render correctly. Do NOT push to the saaskiller template — this
is your fork.

---

## What NOT to do

- ❌ `git merge` the template into your fork — histories are unrelated and names
  differ (`saaskiller` vs your project name); it will not work and will conflict
  with your code.
- ❌ Copy the template's route files over your own product pages.
- ❌ Overwrite your Django apps, stores, or `settings.py`.
- ❌ Add a dark mode — the Swiss system is deliberately light-only.
- ❌ Introduce `rounded-*` or hardcoded colours "to match an old screen" — the
  whole point is one consistent token-driven system.
