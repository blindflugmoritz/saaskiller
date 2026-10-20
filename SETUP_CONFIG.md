# Pre-answering `setup.sh` with a config file

`setup.sh` normally asks ~20 interactive questions (which features, which host,
GitHub org, domain…). If you already know the answers — for example an agent
pre-defined the project in a spec doc — you can put them in a config file and
pass it in:

```bash
./setup.sh my-project --config setup.config.ini
```

Every answer in the file is used automatically; anything you leave out is still
asked interactively. Nothing about the normal flow changes if you don't pass
`--config`.

---

## The three files

| File | What it is | Who writes it |
|---|---|---|
| **`setup.spec.json`** | The machine-readable **contract**: every key, its type, valid values, default, and when it's relevant. | Maintained in the template. Read it; don't edit per-project. |
| **`setup.config.example.ini`** | A filled-in, commented **template** you copy and edit. | Copy → edit per project. |
| **`setup.config.ini`** (any name) | Your actual answers, passed via `--config`. | You, or an agent, per project. |

The spec is the source of truth. The example is a friendly starting point. Your
config is what you hand to `setup.sh`.

---

## For an agent pre-defining a project

If you are an AI assistant preparing a SaasKiller project (e.g. writing setup
docs in another repo), you can emit a ready-to-use config so the human never
retypes the answers:

1. **Read `setup.spec.json`.** It lists every key under `keys[]` with `key`,
   `type`, `values` (for enums), `default`, `note`, and `relevant_when`.
2. **Write a `setup.config.ini`** using those keys. Only include keys you're
   confident about — omitted keys are safely prompted for.
3. **Respect `relevant_when`.** E.g. `github_org` only matters when
   `hosting == deploio`; PA fields only when `hosting == pythonanywhere`.
   Don't set keys that won't apply.
4. **Booleans** accept `true/false`, `yes/no`, `y/n`, `1/0`.
5. **Comment liberally.** Inline comments (` key = value   # why`) are stripped
   by the parser, so annotate each choice with the *reason* — future readers
   (and the human running it) benefit. This mirrors the "Question → Answer →
   Why" tables people already write by hand.

A minimal example an agent might emit:

```ini
# Modell-Cockpit — LAN-only admin frontend on merlin. Not a SaaS.
[project]
project_name = modell-cockpit

[features]
tasks      = true    # django-q2 runs the scripts/modelreg action subprocess
websockets = true    # channels for eval live-progress (MVP polls, infra ready)
s3         = true    # belege upload — RECONFIGURE to local FS (local-first!)
stripe     = false   # no payments
workspaces = false   # single-user owner for MVP
i18n       = false   # German UI, hardcoded strings fine

[hosting]
hosting = none        # runs on merlin behind Caddy, not Deploio
```

---

## Precedence & behaviour

- **Project name:** CLI positional arg (`./setup.sh myapp …`) wins over the
  config's `project_name`, which wins over an interactive prompt.
- **Missing keys (default):** asked interactively, exactly as without a config.
- **`--non-interactive`:** never prompts. Omitted keys use their documented
  default (all feature flags default `false`, `hosting` defaults `deploio`).
  A missing required key (`project_name`, unless given as CLI arg) aborts with
  an error — useful for CI / fully-automated forks.
- **Unknown / misspelled keys:** ignored. Check the summary line
  (`Features: …  Hosting: …`) that `setup.sh` prints before it starts, to
  confirm your config was read as intended.

---

## Full key reference

See `setup.spec.json` → `keys[]`. Summary:

| Key | Type | Default | Relevant when |
|---|---|---|---|
| `project_name` | string | — (required) | always |
| `workspaces` `cms` `stripe` `tasks` `websockets` `s3` `i18n` `sentry` `apikeys` `github_oauth` `mobile` `feedloop` | boolean | `false` | always |
| `hosting` | `deploio` \| `pythonanywhere` \| `none` | `deploio` | always |
| `staging` `production` | boolean | `false` | `hosting != none` |
| `github_org` `github_repo` | string | `""` / project_name | `hosting == deploio` |
| `domain` | string | `""` | `hosting == deploio` && `production` |
| `db` | `shared` \| `server:<name>` \| `dedicated` | `shared` | `hosting == deploio` |
| `pa_username` `pa_webapp_domain` `pa_app_dir` | string | `""` | `hosting == pythonanywhere` |

---

## Database on deplo.io

`db` decides how `deploy-init.sh` provisions Postgres. The three modes cover
the three kinds of project the template is used for:

| Case | Environments | Config | What `deploy-init.sh` does |
|---|---|---|---|
| A — normal SaaS | staging + live | `staging = true`, `production = true`, `db = shared` | one `postgresdatabase` per environment |
| B — live only | live | `production = true` (staging false), `db = shared` | one `postgresdatabase`, apps `<project>-production-*` |
| C — group of projects on one server | staging + live | `db = server:<name>` | no new resource; DBs `<project>_staging` / `<project>_production` on server `<name>` |

| Mode | Creates | Price (net, Sept 2026 invoice) |
|---|---|---|
| `shared` (default) | `nctl create postgresdatabase <project>-<env>-db --location=nine-cz42` | ≈ CHF 5.50 / month per environment |
| `server:<name>` | nothing — uses the existing server `<name>` | share of a server you already pay for |
| `dedicated` | `nctl create postgres <project>-db` (one server for all environments) | ≈ CHF 104 / month (nine-db-s) |

**Why `shared` is the default:** template projects hold 10–20 MB of data.
Until October 2026 every project created two dedicated servers (≈ CHF 208/month
for databases alone); with shared DBs the same project costs ≈ CHF 11.

Details that bit us before:

- **Shared:** the connection string from
  `nctl get postgresdatabase <name> --print-connection-string` is already
  complete (`postgres://<user>:<pw>@<host>/<user>?sslmode=require` — the DB
  name is the random user name). It is used unchanged; appending anything
  breaks it.
- **Server / dedicated:** the server's connection string points at the default
  DB `postgres`, where the app user may not run DDL (PostgreSQL ≥ 15). So each
  project/environment gets its own DB name, and `backend/scripts/bootstrap_database.py`
  creates it in the release job before `migrate`. DB names use the Python package
  name (`my-app` → `my_app_staging`), so they stay unique per project on a shared server.
- **Errors are not swallowed:** every `nctl create` distinguishes "already exists"
  (fine on a rerun) from any other error (abort). A quota error aborts with
  "Kontingent bei Nine erhöhen lassen oder `db = server:<name>` wählen". The
  DB step runs before the apps, and an empty `DATABASE_URL` aborts.
- **Changing your mind after setup:** edit `DB_MODE` / `DB_SERVER` at the top of
  the generated `deploy-init.sh` before running it.
- **Dry run:** `bash scripts/test_deploy_init.sh` runs `setup.sh` + the generated
  `deploy-init.sh` for each case against a fake `nctl` that only records calls
  (`--keep` keeps the generated projects, `SHOW_CALLS=1` prints the calls).

---

*Tip: to verify a config without running the destructive setup, just eyeball
the `Features:` / `Hosting:` summary `setup.sh` echoes right after "Setting up
project" — it reflects exactly what the config produced.*
