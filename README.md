# SaasKiller

Forkable SaaS template. Django 5 + SvelteKit. Deploy to deplo.io or PythonAnywhere.

## Start a new project

```bash
curl -fsSL https://raw.githubusercontent.com/blindflugmoritz/saaskiller/main/remote_setup.sh -o remote_setup.sh
chmod +x remote_setup.sh
./remote_setup.sh my-project
```

That's it. The script checks dependencies, clones the template, creates a private GitHub repo, and runs the interactive setup. Requires `git` and the [GitHub CLI](https://cli.github.com) (`gh auth login` once).

`setup.sh` then asks which optional features you need and which hosting provider to use. It strips everything else, renames all references to your project name, and pushes an initial commit.

## What's always included

| | |
|---|---|
| Auth | Magic link (passwordless) + Google OAuth2 |
| JWT | Access + refresh tokens in localStorage, auto-refresh on 401 |
| User model | UUID pk, email-only, language preference |
| REST API | Django REST Framework + OpenAPI docs at `/api/docs/` |
| Frontend | SvelteKit + TypeScript + Tailwind 4 + shadcn-svelte |
| UI | Login, signup, dashboard, settings — white canvas, ready to build on |
| Tests | pytest-django + Vitest + Playwright |
| CI | GitHub Actions (lint, typecheck, backend + E2E tests) |
| Deploy | deplo.io or PythonAnywhere — `./deploy.sh staging` |

## Optional features (setup.sh asks)

| Feature | What it adds |
|---|---|
| Workspaces & Teams | Multi-tenant, roles (owner/admin/member/viewer), invitation flow |
| Stripe | Subscriptions, one-time payments, per-seat pricing, webhooks |
| Background Tasks | django-q2 task queue + worker |
| Websockets | django-channels, JWT-authenticated, per-user notification groups |
| File Storage | nine.ch S3-compatible object storage (Swiss data residency) |
| i18n | Paraglide, de/en |
| Sentry | Error monitoring, backend + frontend |
| API Key Management | User-facing create/revoke, `Authorization: ApiKey <key>` auth |
| GitHub OAuth | Second OAuth2 provider |
| Mobile | Capacitor (SvelteKit → iOS/Android) |
| Feedloop | Feedback widget — screen recording, screenshots, AI triage, GitHub Issues |

## Getting started (after setup.sh)

### First time

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # no secrets needed to get started
python manage.py migrate
python manage.py createsuperuser

# Frontend
cd ../frontend
npm install
cp .env.example .env          # PUBLIC_API_URL=http://localhost:8002/api (already set)
```

### Every day

```bash
make dev-be   # terminal 1 — Django on http://localhost:8002
make dev-fe   # terminal 2 — Vite on http://localhost:5175
```

If you use background tasks (django-q2):

```bash
make dev-worker   # terminal 3
```

### What's running locally

| URL | What |
|---|---|
| http://localhost:5175 | SvelteKit frontend |
| http://localhost:8002/admin/ | Django admin |
| http://localhost:8002/api/docs/ | OpenAPI / Swagger |

### Email locally

No email service needed. Leave `RESEND_API_KEY` empty in `backend/.env` — Django prints emails to the terminal. Magic link URLs appear directly in the `make dev-be` output, copy and paste into the browser.

## Development workflow

Use the Claude Code slash commands to stay in the right flow:

```bash
/feature        # describe a feature → Claude opens issue, branch, and writes failing tests
/security-audit # scan the codebase for security issues
/new-app        # scaffold a new Django app
/deploy-check   # pre-deploy checklist
```

New features follow the TDD cycle: describe → failing tests → implement → green → deploy.

## Tests

```bash
make test-be    # pytest
make test-fe    # vitest
make test-all   # pytest + vitest + playwright (starts servers automatically)
```

## Deploy

`setup.sh` generates the right deploy scripts for your chosen hosting provider.

### deplo.io

```bash
# First time — provision apps, databases, env vars (run once)
export GITHUB_PAT="github_pat_..."
bash deploy-init.sh

# Every deploy
./deploy.sh staging
./deploy.sh production
```

Staging auto-deploys on push to `main` via GitHub Actions.  
Migrations run automatically on every deploy (`release:` in Procfile).

### PythonAnywhere

```bash
# Set your API token in backend/.env
PA_TOKEN=...   # pythonanywhere.com → Account → API Token

# Deploy
./deploy.sh staging
./deploy.sh production
```

## Stack

**Backend:** Django 5 · DRF · SimpleJWT · django-allauth  
**Frontend:** SvelteKit · TypeScript · Tailwind 4 · shadcn-svelte  
**DB local:** SQLite · **DB staging/prod:** Postgres  
**Email:** Anymail + Resend (console backend locally — no key needed)  
**Deploy:** deplo.io or PythonAnywhere (chosen in `setup.sh`)

## Architecture rules

1. **Svelte 5 runes** — `$state`, `$derived`, `$effect`. No legacy stores.
2. **snake↔camelCase at API boundary only** — transform in `lib/api/client.ts`, nowhere else.
3. **Class-based stores** — async ops go through store methods, never mutate state from components.
4. **Backend-first** — Models → Serializers → Views → Tests → Frontend.
5. **Test-first** — write the test, watch it fail, then write the code.
6. **Tailwind 4** — via `@tailwindcss/vite` plugin. No `tailwind.config.js`.

## Feedloop updates

If you included Feedloop, pull updates from the feedloop repo with:

```bash
./sync_feedloop.sh
git diff
python manage.py migrate  # if models changed
```
