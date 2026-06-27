# SaasKiller

Forkable SaaS template. Django 5 + SvelteKit. Deploy to deplo.io or PythonAnywhere.

## Start a new project

```bash
git clone https://github.com/blindflugstudios/saaskiller my-project
cd my-project
./setup.sh
```

`setup.sh` asks for a project name and which optional features you need, strips everything else, and creates an initial git commit.

## What's always included

| | |
|---|---|
| Auth | Magic link (passwordless) + Google OAuth2 |
| JWT | Access token in memory, refresh in httpOnly cookie, auto-refresh |
| User model | UUID pk, email-only, language preference |
| REST API | Django REST Framework + OpenAPI docs at `/api/docs/` |
| Frontend | SvelteKit + TypeScript + Tailwind 4 + shadcn-svelte |
| UI | Login, signup, dashboard, settings — white canvas, ready to build on |
| Tests | pytest-django + Vitest + Playwright |
| CI | GitHub Actions (backend + frontend + E2E) |
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

## Local dev

### First time setup

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
cp .env.example .env
```

### Every day

Two terminals:

```bash
make dev-be   # terminal 1 — Django on http://localhost:8000
make dev-fe   # terminal 2 — Vite on http://localhost:5173
```

If you use background tasks (django-q2), a third terminal:

```bash
make dev-worker
```

### What's running locally

| URL | What |
|---|---|
| http://localhost:5173 | SvelteKit frontend |
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/api/docs/ | OpenAPI / Swagger |

### Email locally

No email service needed. Leave `RESEND_API_KEY` empty in `backend/.env` and Django prints emails to the terminal instead. Magic link login links appear directly in the `make dev-be` output — copy and paste them into the browser.

## Tests

```bash
make test-be    # pytest
make test-fe    # vitest
make test-all   # pytest + vitest + playwright (starts servers automatically)
```

## Deploy

`setup.sh` asks which hosting provider you want (deplo.io, PythonAnywhere, or none) and generates the right deploy scripts for your project.

### deplo.io

```bash
# First time — provision apps, databases, env vars (run once)
export GITHUB_PAT="github_pat_..."
bash deploy-init.sh

# Every deploy after that
./deploy.sh staging
./deploy.sh production
```

Staging auto-deploys on push to `main` via `.github/workflows/deploy-staging.yml`.  
Migrations run automatically on every deploy (`release:` in Procfile).

### PythonAnywhere

```bash
# Set your API token in .env
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
