# SaasKiller

Forkable SaaS template. Django 5 + SvelteKit. Deploy to Deploio in one script.

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
| Deploy | Deploio via `nctl` — `./deploy.sh staging` |

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

```bash
# Backend (first time)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in keys
python manage.py migrate
python manage.py runserver  # → http://localhost:8000

# Frontend (first time)
cd frontend
npm install
cp .env.example .env
npm run dev                 # → http://localhost:5173
```

Or with make:

```bash
make dev-be   # Django dev server
make dev-fe   # Vite dev server
```

- Django admin: http://localhost:8000/admin
- API docs: http://localhost:8000/api/docs/

## Tests

```bash
make test-be    # pytest
make test-fe    # vitest
make test-all   # pytest + vitest + playwright (starts servers automatically)
```

## Deploy

### First time (run once per environment)

```bash
# See .deploio.yaml for the full nctl create app commands
nctl create app my-project-backend-staging \
  --git-url=https://github.com/yourorg/my-project \
  --git-sub-path=backend \
  --buildpack-stack=heroku \
  --env=SECRET_KEY=xxx \
  --env=DATABASE_URL=postgres://...

nctl create app my-project-frontend-staging \
  --git-url=https://github.com/yourorg/my-project \
  --git-sub-path=frontend \
  --buildpack-stack=heroku \
  --env=PUBLIC_API_URL=https://my-project-backend-staging.deploio.app/api \
  --env=BP_STATIC_WEBROOT=build
```

### Every deploy after that

```bash
./deploy.sh staging
./deploy.sh production
```

Migrations run automatically on every deploy (`release:` in Procfile).

## Stack

**Backend:** Django 5 · DRF · SimpleJWT · django-allauth  
**Frontend:** SvelteKit · TypeScript · Tailwind 4 · shadcn-svelte  
**DB local:** SQLite · **DB staging/prod:** Postgres on Deploio  
**Email:** Anymail + Resend  
**Deploy:** Deploio (nine.ch, Swiss infrastructure)

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
