.PHONY: dev-be dev-fe migrate makemigrations createsuperuser shell test-be test-fe test-e2e test-all

# ── Backend ───────────────────────────────────────────────────────────────────

dev-be:
	cd backend && source venv/bin/activate && python manage.py runserver 8000

migrate:
	cd backend && source venv/bin/activate && python manage.py migrate

makemigrations:
	cd backend && source venv/bin/activate && python manage.py makemigrations

createsuperuser:
	cd backend && source venv/bin/activate && python manage.py createsuperuser

shell:
	cd backend && source venv/bin/activate && python manage.py shell

# ── Frontend ──────────────────────────────────────────────────────────────────

dev-fe:
	cd frontend && npm run dev

# ── Tests ─────────────────────────────────────────────────────────────────────

test-be:
	cd backend && source venv/bin/activate && python -m pytest tests/ -v

test-fe:
	cd frontend && npm test

test-e2e:
	cd frontend && npx playwright test

# Runs all three suites automatically (starts + stops servers)
test-all:
	./scripts/test-all.sh
