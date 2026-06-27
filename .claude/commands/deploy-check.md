Run a pre-deploy checklist for SaasKiller. Check each item and report pass/fail:

1. **Tests green** — run `make test-be` and `make test-fe`. Both must pass.
2. **No .env secrets committed** — run `git diff HEAD --name-only | grep -E '\.env$'`. Must be empty.
3. **Migrations** — run `python manage.py migrate --check` in backend. Must report "No migrations to apply."
4. **Requirements** — check that `backend/requirements.txt` has no commented-out feature packages that should be active.
5. **ALLOWED_HOSTS** — check `backend/saaskiller/settings.py` uses env var for ALLOWED_HOSTS, not hardcoded.
6. **DEBUG** — check settings.py reads DEBUG from env, defaults to False in production path.
7. **Smoke tests** — run `cd frontend && npm run test:e2e:smoke` if servers are running.

Report a clean ✅ / ❌ table. If anything fails, explain how to fix it.
