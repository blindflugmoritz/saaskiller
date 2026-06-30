#!/usr/bin/env bash
# remote_setup.sh — one-command SaasKiller project bootstrap
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/blindflugmoritz/saaskiller/main/remote_setup.sh | bash -s <projektname>
#   curl -fsSL https://raw.githubusercontent.com/blindflugmoritz/saaskiller/main/remote_setup.sh | bash -s <projektname> --public
#
set -euo pipefail

TEMPLATE_REPO="https://github.com/blindflugmoritz/saaskiller.git"
PROJECT_NAME="${1:-}"
VISIBILITY="--private"
if [[ "${2:-}" == "--public" ]]; then
  VISIBILITY="--public"
fi

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓ $*${NC}"; }
fail() { echo -e "${RED}✗ $*${NC}"; exit 1; }
info() { echo -e "${YELLOW}▶ $*${NC}"; }
ask()  { echo -e "${BLUE}? $*${NC}"; }

echo ""
echo "╔══════════════════════════════════════╗"
echo "║         SaasKiller Bootstrap         ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Preflight ─────────────────────────────────────────────────────────────────
info "Checking dependencies..."

command -v git >/dev/null 2>&1 || fail "git is not installed."
ok "git"

command -v gh >/dev/null 2>&1 || fail "GitHub CLI (gh) is not installed. Install from https://cli.github.com"
ok "gh"

gh auth status >/dev/null 2>&1 || fail "Not logged in to GitHub CLI. Run: gh auth login"
ok "gh auth"

# ── Project name ──────────────────────────────────────────────────────────────
if [[ -z "$PROJECT_NAME" ]]; then
  ask "Project name (lowercase, no spaces):"
  read -r PROJECT_NAME
fi

if [[ -z "$PROJECT_NAME" ]]; then
  fail "Project name is required."
fi

if [[ "$PROJECT_NAME" =~ [^a-z0-9_-] ]]; then
  fail "Project name must be lowercase letters, numbers, hyphens or underscores only."
fi

if [[ -d "$PROJECT_NAME" ]]; then
  fail "Directory '$PROJECT_NAME' already exists."
fi

echo ""
info "Creating project: $PROJECT_NAME"
echo ""

# ── Clone template ────────────────────────────────────────────────────────────
info "Cloning SaasKiller template..."
git clone --quiet "$TEMPLATE_REPO" "$PROJECT_NAME"
ok "Template cloned"

cd "$PROJECT_NAME"

# ── Create GitHub repo ────────────────────────────────────────────────────────
info "Creating GitHub repository '$PROJECT_NAME' ($VISIBILITY)..."
GH_REPO_URL=$(gh repo create "$PROJECT_NAME" $VISIBILITY --confirm 2>/dev/null || \
              gh repo create "$PROJECT_NAME" $VISIBILITY 2>/dev/null || true)

# Get the actual URL from gh
REPO_URL=$(gh repo view "$PROJECT_NAME" --json url -q '.url' 2>/dev/null || echo "")

if [[ -z "$REPO_URL" ]]; then
  fail "Could not create GitHub repo '$PROJECT_NAME'. Does it already exist?"
fi

ok "GitHub repo created: $REPO_URL"

# ── Point origin to new repo ──────────────────────────────────────────────────
git remote set-url origin "${REPO_URL}.git"
ok "origin → ${REPO_URL}.git"

echo ""

# ── Run setup.sh ──────────────────────────────────────────────────────────────
info "Running setup.sh..."
echo ""
bash setup.sh "$PROJECT_NAME"
