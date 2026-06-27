#!/usr/bin/env bash
# Runs backend (pytest) + frontend unit (vitest) + E2E (playwright) in one command.
# Starts both servers automatically, waits until ready, then tears down on exit.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BE_DIR="$REPO_ROOT/backend"
FE_DIR="$REPO_ROOT/frontend"
BE_PID=""
FE_PID=""
EXIT_CODE=0

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓ $*${NC}"; }
fail() { echo -e "${RED}✗ $*${NC}"; }
info() { echo -e "${YELLOW}▶ $*${NC}"; }

# ── Cleanup on exit ───────────────────────────────────────────────────────────
cleanup() {
  info "Stopping servers..."
  [[ -n "$BE_PID" ]] && kill "$BE_PID" 2>/dev/null && wait "$BE_PID" 2>/dev/null || true
  [[ -n "$FE_PID" ]] && kill "$FE_PID" 2>/dev/null && wait "$FE_PID" 2>/dev/null || true
  lsof -ti:8000 | xargs kill -9 2>/dev/null || true
  lsof -ti:5175 | xargs kill -9 2>/dev/null || true
  # Remove ephemeral E2E database
  rm -f "$BE_DIR/db_test.sqlite3"
}
trap cleanup EXIT

# wait_for_ok: URL must return HTTP 2xx
wait_for_ok() {
  local url="$1" label="$2" retries=30
  info "Waiting for $label ($url)..."
  for i in $(seq 1 $retries); do
    if curl -sf "$url" > /dev/null 2>&1; then
      ok "$label is up"; return 0
    fi
    sleep 1
  done
  fail "$label did not start within ${retries}s"; return 1
}

# wait_for_port: any HTTP response (even 4xx/5xx) means server is up
wait_for_port() {
  local url="$1" label="$2" retries=30
  info "Waiting for $label ($url)..."
  for i in $(seq 1 $retries); do
    if curl -so /dev/null "$url" 2>/dev/null; then
      ok "$label is up"; return 0
    fi
    sleep 1
  done
  fail "$label did not start within ${retries}s"; return 1
}

# ── Preflight checks ──────────────────────────────────────────────────────────
if [[ ! -f "$BE_DIR/venv/bin/activate" ]]; then
  fail "Backend venv not found. Run:"
  echo "  cd backend && python3 -m venv venv && pip install -r requirements.txt"
  exit 1
fi

# Install frontend deps if needed
if [[ ! -d "$FE_DIR/node_modules/@playwright" ]]; then
  info "Installing frontend dependencies..."
  cd "$FE_DIR" && npm install --silent
fi

# Install Playwright browsers if needed
PW_CACHE="${HOME}/Library/Caches/ms-playwright"
[[ -d "${HOME}/.cache/ms-playwright" ]] && PW_CACHE="${HOME}/.cache/ms-playwright"
if ! ls "$PW_CACHE"/chromium-* > /dev/null 2>&1; then
  info "Installing Playwright browsers..."
  cd "$FE_DIR" && npx playwright install --with-deps chromium
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║         SaasKiller Test Suite        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 1. Start backend (test settings: no throttling, ephemeral db) ─────────────
info "Starting Django backend on :8000 (test settings)..."
cd "$BE_DIR"
source venv/bin/activate
DJANGO_SETTINGS_MODULE=saaskiller.settings_test \
  python manage.py migrate --run-syncdb --noinput -v 0 2>/dev/null
DJANGO_SETTINGS_MODULE=saaskiller.settings_test \
  python manage.py runserver --nothreading 8000 > /tmp/sk-backend.log 2>&1 &
BE_PID=$!
deactivate 2>/dev/null || true
wait_for_ok "http://localhost:8000/api/health/" "Django backend"

# ── 2. Start frontend dev server ──────────────────────────────────────────────
info "Starting SvelteKit dev server on :5175..."
cd "$FE_DIR"
npm run dev -- --port 5175 > /tmp/sk-frontend.log 2>&1 &
FE_PID=$!
wait_for_port "http://localhost:5175" "SvelteKit frontend"

echo ""

# ── 3. Backend tests (pytest) ─────────────────────────────────────────────────
info "Running backend tests (pytest)..."
cd "$BE_DIR"
source venv/bin/activate
if python -m pytest tests/ -v --tb=short; then
  ok "Backend tests passed"
else
  fail "Backend tests FAILED"
  EXIT_CODE=1
fi
deactivate 2>/dev/null || true

echo ""

# ── 4. Frontend unit tests (vitest) ──────────────────────────────────────────
info "Running frontend unit tests (vitest)..."
cd "$FE_DIR"
if npm test -- --reporter=verbose; then
  ok "Frontend unit tests passed"
else
  fail "Frontend unit tests FAILED"
  EXIT_CODE=1
fi

echo ""

# ── 5. E2E tests (playwright) ─────────────────────────────────────────────────
info "Running E2E tests (playwright)..."
cd "$FE_DIR"
if npx playwright test; then
  ok "E2E tests passed"
else
  fail "E2E tests FAILED"
  EXIT_CODE=1
fi

echo ""

# ── Summary ───────────────────────────────────────────────────────────────────
if [[ $EXIT_CODE -eq 0 ]]; then
  echo -e "${GREEN}╔══════════════════════════════════════╗"
  echo -e "║  All tests passed ✓                  ║"
  echo -e "╚══════════════════════════════════════╝${NC}"
else
  echo -e "${RED}╔══════════════════════════════════════╗"
  echo -e "║  Some tests FAILED                   ║"
  echo -e "║  Backend log:  /tmp/sk-backend.log   ║"
  echo -e "║  Frontend log: /tmp/sk-frontend.log  ║"
  echo -e "╚══════════════════════════════════════╝${NC}"
fi

exit $EXIT_CODE
