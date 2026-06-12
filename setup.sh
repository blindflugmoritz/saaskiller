#!/usr/bin/env bash
set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║         SaasKiller Setup             ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Project name ──────────────────────────────────────────────────────────────

read -p "Project name (lowercase, no spaces, e.g. myapp): " PROJECT_NAME
if [[ -z "$PROJECT_NAME" || "$PROJECT_NAME" =~ [^a-z0-9_-] ]]; then
  echo "Error: project name must be lowercase letters, numbers, hyphens or underscores."
  exit 1
fi

# ── Feature questions ──────────────────────────────────────────────────────────

ask() {
  read -p "$1 [y/N]: " answer
  [[ "$answer" =~ ^[Yy]$ ]]
}

echo ""
echo "Which features do you need?"
echo ""

USE_WORKSPACES=false
USE_STRIPE=false
USE_MOBILE=false
USE_WEBSOCKETS=false
USE_S3=false
USE_I18N=false
USE_SENTRY=false
USE_APIKEYS=false
USE_GITHUB_OAUTH=false
USE_TASKS=false
USE_FEEDLOOP=false

ask "Multi-user workspaces & teams?" && USE_WORKSPACES=true
ask "Billing & payments (Stripe)?" && USE_STRIPE=true
ask "Background tasks (django-q2)?" && USE_TASKS=true
ask "Realtime / websockets (django-channels)?" && USE_WEBSOCKETS=true
ask "File uploads (nine.ch S3)?" && USE_S3=true
ask "Multilingual (Paraglide i18n, de/en)?" && USE_I18N=true
ask "Error monitoring (Sentry)?" && USE_SENTRY=true
ask "Programmatic API key management?" && USE_APIKEYS=true
ask "GitHub OAuth (second provider)?" && USE_GITHUB_OAUTH=true
ask "Mobile app (Capacitor)?" && USE_MOBILE=true
ask "Feedback widget (Feedloop — screen recording, screenshots, AI triage, GitHub Issues)?" && USE_FEEDLOOP=true

echo ""
echo "Setting up project: $PROJECT_NAME"
echo "Features: workspaces=$USE_WORKSPACES stripe=$USE_STRIPE tasks=$USE_TASKS websockets=$USE_WEBSOCKETS s3=$USE_S3 i18n=$USE_I18N sentry=$USE_SENTRY apikeys=$USE_APIKEYS github_oauth=$USE_GITHUB_OAUTH mobile=$USE_MOBILE feedloop=$USE_FEEDLOOP"
echo ""

# ── Rename saaskiller → project name ──────────────────────────────────────────

echo "Renaming saaskiller → $PROJECT_NAME..."

# Files to rename (code, configs, etc.)
find . -not -path './.git/*' -not -path './*/venv/*' -not -path './*/node_modules/*' \
  -type f \( -name "*.py" -o -name "*.ts" -o -name "*.svelte" -o -name "*.js" -o -name "*.json" \
           -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" -o -name "*.md" -o -name "*.cfg" \
           -o -name "*.ini" -o -name "*.txt" -o -name "Procfile" -o -name ".env*" -o -name "*.html" \) \
  | xargs grep -l "saaskiller" 2>/dev/null \
  | while read f; do
      sed -i '' "s/saaskiller/$PROJECT_NAME/g" "$f"
    done

# Rename the Django project directory
if [ -d "backend/saaskiller" ]; then
  mv "backend/saaskiller" "backend/$PROJECT_NAME"
fi

# Rename manage.py DJANGO_SETTINGS_MODULE
sed -i '' "s/saaskiller.settings/$PROJECT_NAME.settings/g" backend/manage.py 2>/dev/null || true

# Rename db_table prefixes sk_ → first 2 chars of project name
# (optional aesthetic rename — comment out if you prefer sk_)
# find backend -name "*.py" | xargs sed -i '' "s/\"sk_/\"${PROJECT_NAME:0:3}_/g" 2>/dev/null || true

echo "  Done."

# ── Remove disabled features ───────────────────────────────────────────────────

echo "Removing unused features..."

# strip_feature FEATURE_NAME [extra_dirs...]
# Removes all # === FEATURE: X === ... # === END FEATURE: X === blocks (Python/YAML/etc.)
# and all // === FEATURE: X === ... // === END FEATURE: X === blocks (JS/TS)
# from every relevant source file, then deletes any listed extra directories.
strip_feature() {
  local feature_name="$1"
  shift
  echo "  Stripping feature: $feature_name..."

  # Find all relevant source files (exclude git, venv, node_modules, .svelte-kit, dist)
  while IFS= read -r file; do
    python3 -c "
import re, sys
feature = sys.argv[1]
path = sys.argv[2]
try:
    text = open(path).read()
except Exception:
    sys.exit(0)
original = text
for comment in ['#', '//']:
    pattern = (
        re.escape(comment) + r' === FEATURE: ' + re.escape(feature) + r' ===' +
        r'.*?' +
        re.escape(comment) + r' === END FEATURE: ' + re.escape(feature) + r' ===\n?'
    )
    text = re.sub(pattern, '', text, flags=re.DOTALL)
if text != original:
    open(path, 'w').write(text)
" "$feature_name" "$file"
  done < <(find . \
    -not -path './.git/*' \
    -not -path './*/venv/*' \
    -not -path './*/node_modules/*' \
    -not -path '*/.svelte-kit/*' \
    -not -path '*/dist/*' \
    -type f \( \
      -name "*.py"   -o -name "*.ts"   -o -name "*.js"  -o \
      -name "*.svelte" -o -name "*.json" -o -name "*.yml" -o \
      -name "*.yaml" -o -name "*.txt"  -o -name "Procfile" \
    \) 2>/dev/null)

  # Remove any extra directories passed as arguments
  for dir in "$@"; do
    if [ -e "$dir" ]; then
      rm -rf "$dir"
      echo "    Removed $dir"
    fi
  done
}

$USE_STRIPE       || strip_feature stripe       backend/billing   frontend/src/routes/dashboard/billing
$USE_WORKSPACES   || strip_feature workspaces   backend/workspaces frontend/src/routes/dashboard/workspaces frontend/src/routes/workspaces
$USE_TASKS        || strip_feature tasks        backend/tasks
$USE_WEBSOCKETS   || strip_feature websockets   backend/realtime
$USE_S3           || strip_feature s3           backend/storage
$USE_I18N         || strip_feature i18n         frontend/project.inlang frontend/messages
$USE_SENTRY       || strip_feature sentry
$USE_APIKEYS      || strip_feature apikeys      backend/apikeys   frontend/src/routes/dashboard/api-keys
$USE_GITHUB_OAUTH || strip_feature github-oauth
$USE_MOBILE       || strip_feature capacitor    frontend/capacitor.config.ts frontend/scripts/build-mobile.sh

if $USE_FEEDLOOP; then
  FEEDLOOP_DIR="${FEEDLOOP_PATH:-$HOME/coding/feedloop}"
  if [ ! -d "$FEEDLOOP_DIR" ]; then
    echo ""
    echo "  ⚠ Feedloop not found at $FEEDLOOP_DIR"
    echo "  Clone it first: git clone https://github.com/blindflugmoritz/feedloop $FEEDLOOP_DIR"
    echo "  Then re-run this step manually: ./sync_feedloop.sh"
  else
    echo "  Copying feedloop from $FEEDLOOP_DIR ..."
    cp -r "$FEEDLOOP_DIR/backend/feedback" backend/feedback
    mkdir -p frontend/src/lib/components
    cp -r "$FEEDLOOP_DIR/frontend/components/feedback" frontend/src/lib/components/feedback
    cp "$REPO_ROOT/sync_feedloop.sh" ./sync_feedloop.sh 2>/dev/null || true
    echo "  Feedloop copied. Add env vars (see feedloop README) and run migrations."
  fi
fi

echo "  Done."

# ── Generate .env files ────────────────────────────────────────────────────────

echo "Generating .env files..."

# Root .env
sed "s/saaskiller/$PROJECT_NAME/g" .env.example > .env

# Backend .env
sed "s/saaskiller/$PROJECT_NAME/g" backend/.env.example > backend/.env

# Frontend .env
cp frontend/.env.example frontend/.env

echo "  .env, backend/.env, frontend/.env created. Fill in the secrets."

# ── Git setup ─────────────────────────────────────────────────────────────────

echo "Setting up git..."
git init
git add -A
git commit -m "init: $PROJECT_NAME setup"
echo "  Initial commit created."

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  Setup complete!                     ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Fill in backend/.env (SECRET_KEY, GOOGLE_CLIENT_ID, etc.)"
echo "  2. cd backend && python3 -m venv venv && source venv/bin/activate"
echo "  3. pip install -r requirements.txt && python manage.py migrate"
echo "  4. cd ../frontend && npm install && npm run dev"
echo "  5. make dev-be  (in another terminal)"
echo ""
