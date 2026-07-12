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
| `pa_username` `pa_webapp_domain` `pa_app_dir` | string | `""` | `hosting == pythonanywhere` |

---

*Tip: to verify a config without running the destructive setup, just eyeball
the `Features:` / `Hosting:` summary `setup.sh` echoes right after "Setting up
project" — it reflects exactly what the config produced.*
