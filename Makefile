.PHONY: setup dev-be dev-fe dev-worker migrate makemigrations createsuperuser shell test-be test-fe test-e2e test-all check test-smoke

# ── Backend ───────────────────────────────────────────────────────────────────

setup:
	@echo "Setting up backend..."
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd backend && source venv/bin/activate && python manage.py migrate
	@echo "Setting up frontend..."
	cd frontend && npm install
	@echo ""
	@echo "Done. Copy .env files:"
	@echo "  cp backend/.env.example backend/.env"
	@echo "  cp frontend/.env.example frontend/.env"
	@echo ""
	@echo "Then run: make dev-be (terminal 1) + make dev-fe (terminal 2)"

dev-be:
	cd backend && source venv/bin/activate && python manage.py runserver 8002

# === FEATURE: tasks ===
dev-worker:
	cd backend && source venv/bin/activate && python manage.py qcluster
# === END FEATURE: tasks ===

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
	cd frontend && npm run dev -- --port 5175

check:
	cd frontend && npm run check

test-smoke:
	cd frontend && npm run test:e2e:smoke

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
