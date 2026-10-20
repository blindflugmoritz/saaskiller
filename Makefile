.PHONY: setup dev-be dev-fe dev-worker dev-islands build-islands migrate makemigrations createsuperuser shell test-be test-fe test-e2e test-all test-setup check test-smoke ports

# ── Ports ─────────────────────────────────────────────────────────────────────
# Ports come from the shared registry (~/coding/ports.txt) via portman.sh, so
# every local project has a unique, collision-free pair. If portman is missing,
# fall back to the template defaults so the repo still runs standalone.
PROJECT     := $(notdir $(CURDIR))
PORTMAN     := $(HOME)/coding/portman.sh
DJANGO_PORT := $(shell [ -x "$(PORTMAN)" ] && "$(PORTMAN)" get "$(PROJECT)" be 2>/dev/null || echo 8002)
VITE_PORT   := $(shell [ -x "$(PORTMAN)" ] && "$(PORTMAN)" get "$(PROJECT)" fe 2>/dev/null || echo 5175)

ports:
	@[ -x "$(PORTMAN)" ] && "$(PORTMAN)" list || echo "portman.sh not found; defaults: django=8002 vite=5175"
	@echo "$(PROJECT): django=$(DJANGO_PORT) vite=$(VITE_PORT)"

# ── Backend ───────────────────────────────────────────────────────────────────

setup:
	@echo "Setting up backend..."
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd backend && source venv/bin/activate && python manage.py migrate && python manage.py createcachetable --no-color 2>/dev/null || true
	@echo "Setting up frontend..."
	cd frontend && npm install
	@echo ""
	@echo "Done. Copy .env files:"
	@echo "  cp backend/.env.example backend/.env"
	@echo "  cp frontend/.env.example frontend/.env"
	@echo ""
	@echo "Then run: make dev-be (terminal 1) + make dev-fe (terminal 2)"

dev-be:
	@echo "→ Django on http://localhost:$(DJANGO_PORT)"
	cd backend && source venv/bin/activate && python manage.py runserver $(DJANGO_PORT)

# === FEATURE: tasks ===
dev-worker:
	cd backend && source venv/bin/activate && python manage.py qcluster
# === END FEATURE: tasks ===

migrate:
	cd backend && source venv/bin/activate && python manage.py migrate && python manage.py createcachetable --no-color 2>/dev/null || true

makemigrations:
	cd backend && source venv/bin/activate && python manage.py makemigrations

createsuperuser:
	cd backend && source venv/bin/activate && python manage.py createsuperuser

shell:
	cd backend && source venv/bin/activate && python manage.py shell

# ── Frontend ──────────────────────────────────────────────────────────────────

dev-fe:
	@echo "→ Vite on http://localhost:$(VITE_PORT)"
	cd frontend && npm run dev -- --port $(VITE_PORT)

# === FEATURE: cms ===
# Build Svelte islands for CMS pages (run once before collectstatic; output → backend/static/islands/)
build-islands:
	cd frontend && npm run build:islands

# Watch-mode islands build for local CMS development (terminal 4 when CMS feature active)
dev-islands:
	cd frontend && npm run dev:islands
# === END FEATURE: cms ===

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

# Dry run of setup.sh + generated deploy-init.sh against a fake nctl (macOS)
test-setup:
	bash scripts/test_deploy_init.sh

# Runs all three suites automatically (starts + stops servers)
test-all:
	./scripts/test-all.sh
