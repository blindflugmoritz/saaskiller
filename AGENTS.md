# AGENTS.md — machine-oriented guide to SaasKiller

You are an AI assistant working with the **SaasKiller** template (a forkable
Django 5 + SvelteKit SaaS starter). This file tells you where the *facts* live
so you can understand and configure the template **without interpreting prose**.

Read the three machine-readable sources below in order; fall back to the prose
docs only for rationale.

---

## The machine-readable sources (read these first)

| File | Format | Answers |
|---|---|---|
| **`capabilities.json`** | JSON, generated | *What* the template provides: every optional feature and the Django apps, models, API endpoints, frontend routes, pip deps, and env vars it brings. |
| **`setup.spec.json`** | JSON | *How to configure* a new project: every `setup.sh` question as a typed key with valid values, defaults, and `relevant_when` conditions. |
| **`/api/schema/`** | OpenAPI (live) | The exact *API shape*: request/response schemas for every endpoint. Served by drf-spectacular; dump with `cd backend && python manage.py spectacular --file schema.yml`. |

`capabilities.json` is generated from the code (`scripts/gen_capabilities.py`)
and must not be hand-edited — it cannot drift from reality. If it looks stale,
run `python3 scripts/gen_capabilities.py` (or `--check` in CI).

---

## Task: understand what a fork will contain

1. Parse `capabilities.json`.
   - `always_included` — present in every fork (the `users` app, magic-link+JWT auth, `/api/docs/`).
   - `features.<name>` — one entry per optional feature. Read `backend_apps`,
     `models`, `api_endpoints`, `pip_dependencies`, `env_vars` to know exactly
     what enabling it adds, and `removed_paths_when_disabled` for what disabling
     it deletes.
2. For any endpoint's request/response detail, read `/api/schema/` (OpenAPI).
3. For *why* a thing is designed a certain way, read `BLUEPRINT.md`.

## Task: pre-define a new project (no human retyping)

This is the main agent workflow. Produce a `setup.config.ini` the human passes
to `./setup.sh <project> --config setup.config.ini`.

1. Read `setup.spec.json` → `keys[]`. Each key has `key`, `type`, `values`
   (enums), `default`, `note`, and `relevant_when`.
2. Decide each feature from the product requirements. Use `capabilities.json`
   to check that a feature actually provides what the product needs (models,
   endpoints) before enabling it.
3. Write `setup.config.ini` (INI: `key = value`, `[sections]` cosmetic,
   `# comments` whole-line and inline). Booleans: `true/false/yes/no/y/n/1/0`.
4. Only set keys you're confident about; omitted keys are prompted interactively
   (or use defaults under `--non-interactive`).
5. Respect `relevant_when`: don't set `github_org`/`domain`/`db` unless
   `hosting == deploio`; don't set `pa_*` unless `hosting == pythonanywhere`.
   Leave `db = shared` unless the project explicitly belongs on an existing
   server (`db = server:<name>`); never pick `dedicated` on your own (≈ CHF 104/month).
6. Annotate each choice with an inline `# why` — it survives into the file the
   human reads. (Full guide: `SETUP_CONFIG.md`.)

## Task: extend the template (add an app/feature)

- The project scaffolds a new Django app with the `new-app` command
  (`.claude/commands/new-app.md`).
- Feature-gated code is wrapped in `// === FEATURE: X === … // === END FEATURE: X ===`
  markers (`#` for py/yaml, `<!-- -->` for svelte/html). `setup.sh` strips
  unmarked features by these markers + a dir list. If you add feature-specific
  code, wrap it in markers AND, for whole-file modules, ensure it's deletable —
  see the strip rules in `setup.sh` (`strip_feature`). After changing feature
  boundaries, regenerate `capabilities.json`.

---

## Architecture facts (authoritative summary; details in BLUEPRINT.md)

- **Backend:** Django 5 + DRF + SimpleJWT + django-allauth. Apps live in
  `backend/<app>/`. Settings in `backend/<project>/settings.py`.
- **Frontend:** SvelteKit + TS + Tailwind 4 + shadcn-svelte. Svelte 5 runes
  only (`$state`/`$derived`/`$effect`). Stores are class-based.
- **API boundary:** snake_case (backend) ↔ camelCase (frontend) transform lives
  ONLY in `frontend/src/lib/api/client.ts`. Never transform twice.
- **Auth:** magic-link → JWT; OAuth (Google always, GitHub optional) ends at the
  same JWT endpoint. Flow detailed in `BLUEPRINT.md` and `CLAUDE.md`.
- **DB:** SQLite local, Postgres staging/prod.
- **Ports (local):** read from `~/coding/ports.txt` via `make ports`; defaults
  Django `8002`, Vite `5175`.

---

## Index of docs (prose — read for rationale, not facts)

| File | Purpose |
|---|---|
| `README.md` | Human quick-start. |
| `CLAUDE.md` | Instructions + non-negotiable architecture rules for agents editing this repo. |
| `BLUEPRINT.md` | Deep architecture: models, auth flow, structure, feature list, decisions. |
| `SETUP_CONFIG.md` | Full guide to the `--config` file. |
| `AGENTS.md` | This file. |

*If a fact in a prose doc conflicts with `capabilities.json` / `setup.spec.json`
/ the OpenAPI schema, trust the machine-readable source — it's derived from code.*
