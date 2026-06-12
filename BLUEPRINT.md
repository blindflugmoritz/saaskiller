# SaasKiller — Blueprint

A reusable SaaS base for Django + SvelteKit projects. Self-contained, portable, deployable to Deploio with one script.

**This repo IS the template.** When starting a new project:
1. Fork `saaskiller` on GitHub
2. Run `./setup.sh` — renames the project and strips unused features
3. Set env vars, run `./deploy.sh staging`

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Django 5 + Django REST Framework |
| Auth | SimpleJWT + django-allauth (OAuth2: Google, GitHub) |
| Frontend | SvelteKit + TypeScript + shadcn-svelte + Tailwind 4 |
| Unit tests | pytest-django (BE) + Vitest (FE) |
| E2E tests | Playwright |
| CI | GitHub Actions |
| Database | SQLite (local) / Postgres via dj-database-url (staging + prod) |
| Async tasks | django-q2 |
| Websockets | django-channels |
| Email | Anymail + Resend |
| File storage | nine.ch Object Storage (S3-compatible, Swiss data residency) via boto3 |
| Mobile | Capacitor (SvelteKit → iOS/Android) |
| Rate limiting | django-ratelimit |
| Hosting | Deploio (nctl CLI) |

---

## Project Structure

```
saaskiller/
├── backend/
│   ├── saaskiller/         # Django project settings, urls, wsgi, asgi
│   ├── users/              # Custom user model, auth views
│   ├── workspaces/         # Workspace + Membership models (optional)
│   ├── manage.py
│   ├── requirements.txt
│   ├── Procfile            # web: gunicorn saaskiller.wsgi
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── lib/            # Shared components, API client, stores
│   │   └── routes/         # SvelteKit pages
│   ├── package.json
│   ├── Procfile            # web: node build/index.js
│   └── .env.example
├── Makefile                # Convenience commands (make dev-be, make test-be, etc.)
├── deploy.sh               # Deploio deploy trigger via nctl
├── setup.sh                # New-project setup: rename + strip unused features
├── .env.example
├── CLAUDE.md               # AI coding assistant instructions
└── BLUEPRINT.md
```

---

## Auth

### User Model
- UUID primary key
- Email-only (no username, no password by default)
- `email_verified` flag
- `magic_link_token` + expiry
- `language_preference` (de/en)

### Auth Methods
1. **Magic link** — passwordless email login
2. **OAuth2** — Google (+ GitHub as optional second provider) via `django-allauth` with DRF adapter. Social accounts linked to existing user by email.

### Magic Link → JWT Flow
1. User enters email → backend generates `magic_link_token` + sends email
2. User clicks link → `GET /api/auth/login/<token>/`
3. Backend validates token, marks `email_verified=True`, clears token
4. Backend returns: `{ access: "...", refresh: "..." }`
5. Frontend stores access token in memory, refresh token in httpOnly cookie
6. All subsequent requests use `Authorization: Bearer <access>`
7. On 401 → frontend calls `POST /api/auth/refresh/` with the cookie → gets new access token

SimpleJWT handles rotation. Magic link is just the entry point — from step 4 onward it's standard JWT.

---

## Multi-tenancy (optional — enable via `setup.sh`)

The `workspaces` app is included in the template but can be removed by `setup.sh`. When enabled:

### Workspace
- UUID pk, `db_table = 'sk_workspaces'`
- `name`, `kind` (personal / family / school / business)
- `owner` FK to User
- Auto-provisioned (personal workspace + owner membership) on user signup via `post_save` signal

### Membership
- UUID pk, `db_table = 'sk_memberships'`
- Links User ↔ Workspace
- Roles: `owner`, `admin`, `member`, `viewer`
- Unique together: (workspace, user)

### Invitation flow (to build per-project)
- Invite by email → token link → creates Membership on accept
- Inviter must be `owner` or `admin`

---

## Deploio Deployment

Deploio is a Swiss PaaS (by nine.ch). Git-push deploys via `nctl` CLI + Heroku buildpacks.

### First deploy (run once per app)

```bash
# Backend
nctl create app saaskiller-backend \
  --git-url=https://github.com/yourorg/yourrepo \
  --git-sub-path=backend \
  --buildpack-stack=heroku \
  --env=SECRET_KEY=xxx \
  --env=DATABASE_URL=xxx \
  --env=ALLOWED_HOSTS=.deploio.app

# Frontend
nctl create app saaskiller-frontend \
  --git-url=https://github.com/yourorg/yourrepo \
  --git-sub-path=frontend \
  --buildpack-stack=heroku \
  --env=PUBLIC_API_URL=https://saaskiller-backend.deploio.app
```

### Redeploy (`./deploy.sh`)

```bash
nctl update app saaskiller-backend \
  --project $DEPLOIO_PROJECT \
  --git-revision=$(git rev-parse HEAD) \
  --skip-repo-access-check

nctl update app saaskiller-frontend \
  --project $DEPLOIO_PROJECT \
  --git-revision=$(git rev-parse HEAD) \
  --skip-repo-access-check
```

### Required env vars

**Backend**
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `RESEND_API_KEY`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- (if Stripe) `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- (if S3) `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`
- (if Sentry) `SENTRY_DSN`
- `NCTL_API_CLIENT_ID`, `NCTL_API_CLIENT_SECRET`, `NCTL_ORGANIZATION`, `DEPLOIO_PROJECT`

**Frontend**
- `PUBLIC_API_URL`
- (if Sentry) `PUBLIC_SENTRY_DSN`

---

## `setup.sh` — New Project Initialisation

Run after forking. Does everything in one pass:

1. Asks all questions below
2. Find/replaces `saaskiller` → your project name throughout (code, configs, Procfiles)
3. Removes unused feature code from `INSTALLED_APPS`, `requirements.txt`, `package.json`, routes
4. Generates `.env.example` with only the relevant vars
5. Creates initial git commit: `init: <projectname> setup`

### Always included (no choice)
- Django 5 + DRF backend
- Custom User model (UUID, email-only)
- Magic link + OAuth2 auth (Google)
- JWT (SimpleJWT)
- SvelteKit + TypeScript frontend
- White canvas UI (login / signup / empty dashboard)
- shadcn-svelte + Tailwind 4
- pytest + Vitest + Playwright
- Deploio deploy script (nctl-based, staging + production)
- GitHub Actions CI
- CLAUDE.md

### Optional (script asks)

| Question | Includes |
|---|---|
| "Billing/Payments?" | Stripe subscriptions + one-time payments + per-seat pricing |
| "Multi-user/Teams?" | Workspaces + Memberships + Invitation workflow |
| "Mobile app?" | Capacitor setup + build script |
| "Realtime features?" | django-channels + Websockets |
| "File uploads?" | nine.ch Object Storage + boto3 |
| "Multilingual?" | Paraglide i18n (de/en) — see note below |
| "Error monitoring?" | Sentry (backend + frontend) |
| "Programmatic API access?" | API key management |
| "GitHub OAuth?" | GitHub as second OAuth2 provider |

> **i18n note:** If you say No to "Multilingual?", all user-facing strings are hardcoded in the single chosen language. If you say Yes, Paraglide `m.*()` is enforced everywhere — no raw strings in components.

---

## Environments

| Environment | Database | Frontend | Deploy |
|---|---|---|---|
| `local` | SQLite | Vite dev server (`localhost:5173`) | — |
| `staging` | Postgres (Deploio) | Built + served | `./deploy.sh staging` |
| `production` | Postgres (Deploio) | Built + served | `./deploy.sh production` |

---

## Testing

### Backend (pytest-django)

**Config** — `backend/pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = saaskiller.settings
python_files = tests.py test_*.py *_test.py
```

**Location** — `backend/tests/test_<app>.py` (one file per app)

**Fixtures pattern:**
```python
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user(db):
    u = User.objects.create_user(email='test@example.com')
    u.email_verified = True
    u.save()
    return u

@pytest.fixture
def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client
```

**Run:**
```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
# or:
make test-be
```

---

### Frontend (Vitest)

**Config** — `frontend/vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

export default defineConfig({
  plugins: [svelte()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    alias: {
      $lib: resolve(__dirname, 'src/lib'),
      $app: resolve(__dirname, 'src/test/mocks/app'),
    },
  },
});
```

**Setup file** — `frontend/src/test/setup.ts`:
```ts
import '@testing-library/jest-dom';
// jsdom doesn't implement execCommand — stub it for tests
if (!document.execCommand) {
  document.execCommand = () => false;
}
```

**Location** — test file next to the module it tests:
```
src/lib/api/client.ts        → src/lib/api/client.test.ts
src/lib/stores/auth.svelte.ts → src/lib/stores/auth.test.ts
src/lib/utils/tokenStorage.ts → src/lib/utils/tokenStorage.test.ts
```

**Run:**
```bash
cd frontend
npm test           # run once
npm run test:watch # watch mode (use during development)
# or:
make test-fe
```

---

### E2E (Playwright)

**What to test:** critical user flows only — signup, magic link login, OAuth login, dashboard access, settings update.

**Location** — `frontend/tests/` (separate from unit tests)

**Run:**
```bash
cd frontend
npx playwright test
# or:
make test-e2e
```

Playwright requires both backend and frontend running. In CI these are started as services before the test run.

---

### CI (GitHub Actions)

Three jobs run on every push/PR:

1. **test-backend** — `pytest tests/ -v`
2. **test-frontend** — `npm test`
3. **test-e2e** — starts Django dev server + Vite, runs Playwright

---

## Architecture Decisions

Non-negotiable in all projects built on this base:

1. **Svelte 5 runes** — `$state`, `$derived`, `$effect`. No legacy stores.
2. **snake↔camelCase at API boundary only** — transform in `lib/api/client.ts`, nowhere else.
3. **Class-based stores** — all async ops go through store methods, never mutate state directly.
4. **Backend-first** — Models → Serializers → Views → Frontend.
5. **Test-first** — write test, watch it fail, then write code. Never commit red tests.
6. **Tailwind 4** — via `@tailwindcss/vite`, no `tailwind.config.js`.
7. **i18n conditional** — if enabled: all user-facing text through Paraglide `m.*()`. If disabled: fine to hardcode strings.
8. **Pure functions first** — business logic as pure functions before wiring to components.

---

## Development Workflow (per feature)

```
1. Describe   → what should it do?
2. Test BE    → write pytest test, expect red
3. Build BE   → models → serializers → views → green
4. Test FE    → write Vitest component test, expect red
5. Build FE   → implement component/store → green
6. E2E test   → write Playwright flow test, expect red
7. E2E green  → feature is done
8. Deploy     → ./deploy.sh staging → verify → ./deploy.sh production
```

---

## GitHub Workflow

```bash
# Start a feature
git checkout -b feature/my-feature

# Commit during development
git add <files>
git commit -m "feat: description"

# Done → open PR
gh pr create --title "feat: description" --body "..."

# After review → merge
gh pr merge --squash

# Deploy
./deploy.sh staging    # verify first
./deploy.sh production
```

### Branch naming
- `feature/` — new features
- `fix/` — bug fixes
- `chore/` — deps, config, refactor

---

## White Canvas UI

What you see after `./setup.sh` + `make dev`:

- `/` → Landing page (minimal, CTA to sign up)
- `/auth/signup` → Signup (email → magic link flow)
- `/auth/login` → Login
- `/auth/login/[token]` → Magic link handler → redirects to dashboard
- `/dashboard` → Empty dashboard with shadcn-svelte sidebar + header
- `/dashboard/settings` → User settings (email, language)

No product-specific UI. No styling beyond Tailwind defaults + shadcn-svelte base.

---

## Feature List

### Always included

| Feature | Details |
|---|---|
| Auth — magic link | Passwordless, token-based, auto-login after click |
| Auth — OAuth2 (Google) | via django-allauth, linked by email |
| Auth — email verification | Token-based, expiring |
| Custom user model | UUID pk, email-only, language pref |
| JWT auth | SimpleJWT, access in memory + refresh in httpOnly cookie |
| REST API + docs | DRF + drf-spectacular (OpenAPI) |
| Rate limiting | django-ratelimit on auth endpoints |
| Tests + CI | pytest-django + Vitest + Playwright + GitHub Actions |
| Local dev environment | venv + SQLite, `make dev-be` + `make dev-fe` |
| Deploio deploy script | nctl-based, staging + production |

### Optional (via `setup.sh`)

| Feature | Details |
|---|---|
| Stripe subscriptions | Recurring billing, plan management |
| Stripe one-time payments | E-commerce / credits |
| Per-seat pricing | Configurable per workspace |
| Workspaces / Teams | Multi-tenant, owner + roles |
| Membership roles | owner / admin / member / viewer |
| Invitation workflow | Email invite → token → accept → Membership |
| API key management | Users can create/revoke API keys |
| Background tasks | django-q2 |
| Websockets | django-channels |
| File storage | nine.ch Object Storage (S3-compatible, Swiss data residency) |
| Internationalization | Paraglide i18n, de/en out of the box |
| Error monitoring | Sentry (backend + frontend) |
| Capacitor | SvelteKit → iOS/Android |
| GitHub OAuth | Second OAuth2 provider |

### NOT included (add per-project)

- Two-factor authentication
- Wagtail CMS / blog
- Feature flags
- User impersonation
- Email marketing integration

---

## Source Reference

Initial patterns derived from:
- `blindflugstudios/easyprompting` — users, auth, JWT, magic link, SvelteKit patterns, deploy
- `blindflugstudios/feedloop` — feedback module (SvelteKit + Django, screen recording, AI triage)
