# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## What this repo is

**SaasKiller** is a forkable SaaS template — Django 5 + SvelteKit. The repo root IS the template. When starting a new project, fork this repo and run `./setup.sh`. It asks for a project name, which optional features to include, and which hosting provider to use (deplo.io or PythonAnywhere), then generates the right deploy scripts and an initial git commit.

Do not build product-specific features here. Keep everything generic and replaceable.

## Stack

**Backend:** Django 5 + DRF + SimpleJWT + django-allauth  
**Frontend:** SvelteKit + TypeScript + Tailwind 4 + shadcn-svelte  
**DB (local):** SQLite  
**DB (staging/prod):** Postgres  
**Email:** Anymail + Resend (console backend locally — no key needed)  
**Tasks:** django-q2  
**Deploy:** deplo.io or PythonAnywhere (chosen during `./setup.sh`)  

## Local dev

```bash
# First time — backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # no secrets needed to get started
python manage.py migrate
python manage.py createsuperuser

# First time — frontend
cd ../frontend
npm install
cp .env.example .env
```

Every day — two terminals:
```bash
make dev-be          # terminal 1 — Django on http://localhost:8002
make dev-fe          # terminal 2 — Vite on http://localhost:5175
make dev-worker      # terminal 3 — django-q2 worker (only if tasks feature active)
```

Other Makefile targets:
```bash
make migrate
make makemigrations
make createsuperuser
make shell
make test-be         # pytest only
make test-fe         # vitest only
make test-e2e        # playwright only (requires servers running)
make test-all        # ALL tests — starts servers automatically, runs everything, cleans up
```

URLs:
- Frontend: http://localhost:5175
- Django admin: http://localhost:8002/admin/
- API docs: http://localhost:8002/api/docs/
- DB: SQLite locally (`backend/db.sqlite3`), Postgres on staging/prod

Email locally: leave `RESEND_API_KEY` empty — Django prints emails to the terminal.
Magic link URLs appear in `make dev-be` output, copy-paste into browser.

## Project structure

```
backend/
  saaskiller/       Django settings, urls, wsgi, asgi
  users/            Custom user model, auth views
  workspaces/       Multi-tenant (optional — may be stripped by setup.sh)

frontend/
  src/lib/
    api/
      client.ts     ApiClient: JWT injection, auto-refresh, snake↔camel transform
      auth.ts       Auth API functions
    stores/         Svelte 5 class-based stores
    components/     Shared UI components
  src/routes/       SvelteKit pages
```

## Testing

### Backend
- Framework: `pytest-django`
- Config: `backend/pytest.ini` with `DJANGO_SETTINGS_MODULE = saaskiller.settings`
- Location: `backend/tests/test_<app>.py` — one file per app
- Fixtures: `APIClient()` for unauthenticated, `RefreshToken.for_user(user)` for authenticated
- Run: `make test-be` → `python -m pytest tests/ -v`

### Frontend
- Framework: Vitest + `@testing-library/svelte` + jsdom
- Config: `frontend/vitest.config.ts` — jsdom environment, `$lib` alias, setup file
- Setup file: `frontend/src/test/setup.ts` — imports `@testing-library/jest-dom`
- Location: test file next to module (`client.ts` → `client.test.ts`)
- Run: `make test-fe` → `npm test` / `npm run test:watch` during development

### E2E
- Framework: Playwright
- Location: `frontend/tests/e2e/`
- Run: `make test-all` — starts both servers automatically (use this)
- Run: `make test-e2e` — runs Playwright only (requires servers already running)
- Backend uses `saaskiller/settings_test.py` for E2E: no throttling, ephemeral SQLite DB

**Auth in E2E tests — use `loginAsTestUser()`, not the magic link flow:**
```ts
import { loginAsTestUser, gotoApp } from './helpers/auth';

test('my test', async ({ browser }) => {
    const ctx = await browser.newContext();
    await loginAsTestUser(ctx);          // injects JWT directly into localStorage
    const page = await ctx.newPage();
    await gotoApp(page, '/dashboard');   // navigate to any authenticated route
    // ... test
    await ctx.close();
});
```
The helper calls `python manage.py create_test_token` (only works when `DEBUG=True`) which creates/reuses `e2e-test@saaskiller.local` and returns a JWT pair — no email, no browser redirect, deterministic and fast.

**Smoke tests — run before every deploy:**
```bash
npm run test:e2e:smoke     # ~30s, @smoke-tagged tests only
npm run test:e2e           # full suite
npm run test:e2e:ui        # interactive Playwright UI for debugging
E2E_BASE_URL=https://myapp-staging-frontend.deploio.app npm run test:e2e:smoke  # against staging
```

**Tagging:** Mark critical tests with `@smoke` in the test name. These run in ~30s and must be green before any deploy.

**When to write E2E tests:**
- Flow crosses page boundaries (login → redirect, save → list)
- UI behaviour depends on auth state
- Critical user path that must survive a deploy

### Rules
- Always write the test first, watch it fail, then write the code
- Never commit red tests
- Pure functions → Vitest unit tests; components → `@testing-library/svelte`; flows → Playwright

## Architecture rules (non-negotiable)

1. **Svelte 5 runes** — `$state`, `$derived`, `$effect`. No legacy stores or `writable()`.
2. **snake↔camelCase at API boundary only** — transform happens in `lib/api/client.ts`. Everywhere else is camelCase (FE) or snake_case (BE). Never transform twice, never bypass.
3. **Class-based stores** — async ops go through store methods. Never mutate store state from components.
4. **Backend-first** — Models → Serializers → Views → Tests → Frontend.
5. **Test-first** — write the test, watch it fail, then write the code. Never commit red tests.
6. **Tailwind 4** — uses `@tailwindcss/vite` plugin. No `tailwind.config.js`. Import: `@import 'tailwindcss'` in `app.css`.
7. **i18n conditional** — if Paraglide is enabled: all user-facing text through `m.*()`. If not enabled: hardcoded strings are fine.
8. **Pure functions first** — business logic as pure functions before wiring to components or stores.

## Auth flow (Magic link → JWT)

1. User submits email → `POST /api/auth/request-magic-link/`
2. Backend generates `magic_link_token`, sends email
3. User clicks link → `GET /api/auth/login/<token>/`
4. Backend validates + clears token, returns `{ access, refresh }`
5. Frontend: both tokens stored in localStorage (`lib/utils/tokenStorage.ts`)
6. On 401: auto-call `POST /api/auth/refresh/` → get new access token
7. OAuth2 (Google) goes through allauth → same JWT endpoint at the end

## Development workflow (per feature)

```
1. Describe    what should it do?
2. Test BE     write pytest test, expect red
3. Build BE    models → serializers → views → green
4. Test FE     write Vitest test, expect red
5. Build FE    component/store → green
6. E2E         write Playwright test, expect red → green
7. Deploy      ./deploy.sh staging → verify → ./deploy.sh production
```

## API conventions

- All endpoints under `/api/`
- Auth endpoints: `/api/auth/`
- App endpoints: `/api/<app>/`
- OpenAPI docs: `/api/schema/` (drf-spectacular)
- All responses JSON, snake_case keys
- Errors: `{ "detail": "..." }` or `{ "field": ["error"] }`

## DO NOT

- Mutate store state from components: `authStore.user = null` ❌
- Skip the snake↔camel transform ❌
- Bypass JWT with session auth ❌
- Commit `.env`, `db.sqlite3`, `venv/`, `node_modules/` ❌
- Add `tailwind.config.js` ❌
- Add product-specific logic to `users/` or `workspaces/` ❌
- Hardcode strings in components when Paraglide is enabled ❌
- Commit red tests ❌
