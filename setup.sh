#!/usr/bin/env bash
set -e

# Safety guard: refuse to run if origin still points to the template repo.
# You must fork first — setup.sh rewrites history and renames everything.
if git remote get-url origin 2>/dev/null | grep -qE "blindflugmoritz/saaskiller(\.git)?$"; then
  echo "Error: origin still points to the saaskiller template repo."
  echo "Fork the repo on GitHub first, then clone your fork and run setup.sh."
  exit 1
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║         SaasKiller Setup             ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Argument parsing (positional project name + --config / --non-interactive) ──
#
# Usage: ./setup.sh <project-name> [--config FILE] [--non-interactive]
# A config file pre-answers questions (see setup.spec.json / SETUP_CONFIG.md).
# Without --non-interactive, any key the config omits is still asked interactively.

CONFIG_FILE=""
NON_INTERACTIVE=false
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)          CONFIG_FILE="${2:-}"; shift 2 ;;
    --config=*)        CONFIG_FILE="${1#*=}"; shift ;;
    --non-interactive) NON_INTERACTIVE=true; shift ;;
    -h|--help)
      echo "Usage: ./setup.sh <project-name> [--config FILE] [--non-interactive]"
      echo "  --config FILE       Pre-answer questions from an ini file (see setup.spec.json)."
      echo "  --non-interactive   Use documented defaults for anything the config omits; do not prompt."
      exit 0 ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *)  POSITIONAL+=("$1"); shift ;;
  esac
done
set -- "${POSITIONAL[@]}"

# ── Config file loader (flat ini → CFG_<key> shell vars) ──────────────────────
# Parses key=value lines (ignoring [sections], # / ; comments). Booleans are
# normalised to true/false. Values become CFG_<lowercased_key>.
declare -A CFG=()
if [[ -n "$CONFIG_FILE" ]]; then
  [[ -f "$CONFIG_FILE" ]] || { echo "Error: config file not found: $CONFIG_FILE" >&2; exit 1; }
  echo "Loading config: $CONFIG_FILE"
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%$'\r'}"                          # strip CR (Windows files)
    [[ "$line" =~ ^[[:space:]]*[#\;] ]] && continue # comment
    [[ "$line" =~ ^[[:space:]]*\[.*\][[:space:]]*$ ]] && continue # [section]
    [[ "$line" =~ = ]] || continue                  # not a key=value
    key="${line%%=*}"; val="${line#*=}"
    # strip inline comment: whitespace followed by # or ; to end of line.
    # (a leading space is required, so '#' inside a value like a URL fragment
    #  or 'pass#word' is preserved — only ' # comment' style is removed.)
    val="$(printf '%s' "$val" | sed -E 's/[[:space:]]+[#;].*$//')"
    # trim whitespace
    key="$(echo "$key" | tr '[:upper:]' '[:lower:]' | xargs)"
    val="$(echo "$val" | xargs)"
    [[ -z "$key" ]] && continue
    CFG["$key"]="$val"
  done < "$CONFIG_FILE"
fi

# cfg_get KEY -> echoes the raw config value, or empty if unset
cfg_get() { echo "${CFG[$1]:-}"; }
# cfg_has KEY -> true if the key was present in the config file
cfg_has() { [[ -n "${CFG[$1]+x}" ]]; }
# cfg_bool KEY -> normalises a config value to 'true'/'false' (empty if unset/invalid)
cfg_bool() {
  case "$(echo "${CFG[$1]:-}" | tr '[:upper:]' '[:lower:]')" in
    true|yes|y|1)  echo true ;;
    false|no|n|0)  echo false ;;
    *)             echo "" ;;
  esac
}

# ── Project name ──────────────────────────────────────────────────────────────

# Precedence: CLI positional arg > config project_name > interactive prompt.
if [[ -n "${1:-}" ]]; then
  PROJECT_NAME="$1"
elif cfg_has project_name; then
  PROJECT_NAME="$(cfg_get project_name)"
  echo "  project_name = $PROJECT_NAME  (from config)"
elif $NON_INTERACTIVE; then
  echo "Error: project_name required (CLI arg or config) in --non-interactive mode." >&2
  exit 1
else
  read -p "Project name (lowercase, no spaces, e.g. myapp): " PROJECT_NAME
fi
if [[ -z "$PROJECT_NAME" || "$PROJECT_NAME" =~ [^a-z0-9_-] ]]; then
  echo "Error: project name must be lowercase letters, numbers, hyphens or underscores."
  exit 1
fi

# ── Feature questions ──────────────────────────────────────────────────────────

# ask KEY "Question?"  → returns 0 (yes) / 1 (no).
# If the config set KEY, use it silently. Else in --non-interactive use the
# default (false). Else prompt as before.
ask() {
  local key="$1" question="$2" fromcfg
  fromcfg="$(cfg_bool "$key")"
  if [[ -n "$fromcfg" ]]; then
    echo "  $key = $fromcfg  (from config)"
    [[ "$fromcfg" == true ]]
    return
  fi
  if $NON_INTERACTIVE; then
    return 1   # documented default for all feature flags is false
  fi
  local answer
  read -p "$question [y/N]: " answer
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
USE_CMS=false

ask workspaces   "Multi-user workspaces & teams?" && USE_WORKSPACES=true
ask cms          "CMS — pages, blog, structured content (feincms3, server-rendered, crawlable)?" && USE_CMS=true
ask stripe       "Billing & payments (Stripe)?" && USE_STRIPE=true
ask tasks        "Background tasks (django-q2)?" && USE_TASKS=true
ask websockets   "Realtime / websockets (django-channels)?" && USE_WEBSOCKETS=true
ask s3           "File uploads (nine.ch S3)?" && USE_S3=true
ask i18n         "Multilingual (Paraglide i18n, de/en)?" && USE_I18N=true
ask sentry       "Error monitoring (Sentry)?" && USE_SENTRY=true
ask apikeys      "Programmatic API key management?" && USE_APIKEYS=true
ask github_oauth "GitHub OAuth (second provider)?" && USE_GITHUB_OAUTH=true
ask mobile       "Mobile app (Capacitor)?" && USE_MOBILE=true
ask feedloop     "Feedback widget (Feedloop — screen recording, screenshots, AI triage, GitHub Issues)?" && USE_FEEDLOOP=true

# ── Hosting questions ─────────────────────────────────────────────────────────

# prompt_str KEY VAR "Prompt text" ["default"]  → sets VAR from config or prompt.
# Config value (even empty string, if the key is present) wins; else prompt;
# else in --non-interactive use the given default.
prompt_str() {
  local key="$1" var="$2" prompt="$3" default="${4:-}"
  if cfg_has "$key"; then
    printf -v "$var" '%s' "$(cfg_get "$key")"
    echo "  $key = ${!var}  (from config)"
    return
  fi
  if $NON_INTERACTIVE; then
    printf -v "$var" '%s' "$default"
    return
  fi
  local answer
  read -p "$prompt: " answer
  printf -v "$var" '%s' "$answer"
}

echo ""
echo "Hosting setup:"
if cfg_has hosting; then
  HOSTING="$(cfg_get hosting)"
  case "$HOSTING" in
    deploio|pythonanywhere|none) echo "  hosting = $HOSTING  (from config)" ;;
    *) echo "Error: invalid hosting '$HOSTING' (deploio|pythonanywhere|none)" >&2; exit 1 ;;
  esac
elif $NON_INTERACTIVE; then
  HOSTING="deploio"   # documented default
else
  echo ""
  echo "  [1] deplo.io  (nine.ch, Swiss PaaS, nctl CLI)"
  echo "  [2] PythonAnywhere"
  echo "  [3] None / local only"
  read -p "Hosting provider [1/2/3]: " _hosting_choice
  case "$_hosting_choice" in
    2) HOSTING="pythonanywhere" ;;
    3) HOSTING="none" ;;
    *) HOSTING="deploio" ;;
  esac
fi

USE_STAGING=false
USE_PRODUCTION=false

if [[ "$HOSTING" != "none" ]]; then
  ask staging    "Staging environment?" && USE_STAGING=true
  ask production "Production environment?" && USE_PRODUCTION=true
  if ! $USE_STAGING && ! $USE_PRODUCTION; then
    echo "  ⚠  No environment selected — generating local-only setup."
    HOSTING="none"
  fi
fi

# deplo.io extra info (used later to generate deploy-init.sh)
GITHUB_ORG=""
GITHUB_REPO=""
DOMAIN=""
if [[ "$HOSTING" == "deploio" ]]; then
  echo ""
  prompt_str github_org  GITHUB_ORG  "GitHub org or user (e.g. blindflugstudios)"
  prompt_str github_repo GITHUB_REPO "GitHub repo name (e.g. $PROJECT_NAME)"
  [[ -z "$GITHUB_REPO" ]] && GITHUB_REPO="$PROJECT_NAME"
  if $USE_PRODUCTION; then
    prompt_str domain DOMAIN "Production domain (e.g. myapp.ch, leave empty to skip)"
  fi
fi

# PythonAnywhere extra info
PA_USERNAME=""
PA_WEBAPP_DOMAIN=""
PA_APP_DIR=""
if [[ "$HOSTING" == "pythonanywhere" ]]; then
  echo ""
  prompt_str pa_username      PA_USERNAME      "PythonAnywhere username"
  prompt_str pa_webapp_domain PA_WEBAPP_DOMAIN "Webapp domain (e.g. myapp.pythonanywhere.com)"
  prompt_str pa_app_dir       PA_APP_DIR       "App directory on PA server (e.g. /home/$PA_USERNAME/$PROJECT_NAME)"
fi

echo ""
echo "Setting up project: $PROJECT_NAME"
echo "Features: workspaces=$USE_WORKSPACES cms=$USE_CMS stripe=$USE_STRIPE tasks=$USE_TASKS websockets=$USE_WEBSOCKETS s3=$USE_S3 i18n=$USE_I18N sentry=$USE_SENTRY apikeys=$USE_APIKEYS github_oauth=$USE_GITHUB_OAUTH mobile=$USE_MOBILE feedloop=$USE_FEEDLOOP"
echo "Hosting: $HOSTING  staging=$USE_STAGING  production=$USE_PRODUCTION"
echo ""

# ── Rename saaskiller → project name ──────────────────────────────────────────

# The literal "saaskiller" plays two roles in the template:
#   1. The Django Python package name — must be a valid Python identifier, so
#      hyphens are NOT allowed. Referenced as `saaskiller.settings` etc. and as
#      the dir backend/saaskiller/.
#   2. Branding / repo / URL / value strings — hyphens are fine here.
# A project name may contain hyphens (e.g. modell-cockpit), so we use a
# separate PKG_NAME (hyphens → underscores) for role 1 and PROJECT_NAME for
# role 2. Otherwise `import modell-cockpit.settings` is a SyntaxError.
PKG_NAME="${PROJECT_NAME//-/_}"
if [[ "$PKG_NAME" != "$PROJECT_NAME" ]]; then
  echo "Renaming saaskiller → $PROJECT_NAME (python package: $PKG_NAME)..."
else
  echo "Renaming saaskiller → $PROJECT_NAME..."
fi

# Pass 1 — Python module references → PKG_NAME. Match ONLY the real submodule
#          names (settings/urls/wsgi/asgi/views/settings_test), so we don't
#          mangle unrelated dotted strings like an email domain
#          (e2e-test@saaskiller.local) or a URL (saaskiller.app).
#          Do this BEFORE the bare replace so module paths get underscores.
find . -not -path './.git/*' -not -path './*/venv/*' -not -path './*/node_modules/*' \
  -type f \( -name "*.py" -o -name "*.ini" -o -name "Procfile" -o -name "*.cfg" \) \
  | xargs grep -lE "saaskiller\.(settings|urls|wsgi|asgi|views)" 2>/dev/null \
  | while read f; do
      sed -i '' -E "s/saaskiller\.(settings_test|settings|urls|wsgi|asgi|views)/$PKG_NAME.\1/g" "$f"
    done

# Pass 2 — everything else (branding, repo, URLs, values) → PROJECT_NAME.
find . -not -path './.git/*' -not -path './*/venv/*' -not -path './*/node_modules/*' \
  -type f \( -name "*.py" -o -name "*.ts" -o -name "*.svelte" -o -name "*.js" -o -name "*.json" \
           -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" -o -name "*.md" -o -name "*.cfg" \
           -o -name "*.ini" -o -name "*.txt" -o -name "Procfile" -o -name ".env*" -o -name "*.html" \) \
  | xargs grep -l "saaskiller" 2>/dev/null \
  | while read f; do
      sed -i '' "s/saaskiller/$PROJECT_NAME/g" "$f"
    done

# Rename the Django project directory to the Python package name.
if [ -d "backend/saaskiller" ]; then
  mv "backend/saaskiller" "backend/$PKG_NAME"
fi

# manage.py DJANGO_SETTINGS_MODULE (belt-and-suspenders; pass 1 already did it)
sed -i '' "s/saaskiller\.settings/$PKG_NAME.settings/g" backend/manage.py 2>/dev/null || true

# Rename db_table prefixes sk_ → first 2 chars of project name
# (optional aesthetic rename — comment out if you prefer sk_)
# find backend -name "*.py" | xargs sed -i '' "s/\"sk_/\"${PROJECT_NAME:0:3}_/g" 2>/dev/null || true

echo "  Done."

# ── Assign local dev ports from the shared registry ───────────────────────────
# Every local project gets a unique, collision-free (django, vite) pair from
# ~/coding/ports.txt via portman.sh. Falls back to the template defaults if
# portman isn't present, so setup still works on a machine without the registry.

echo "Assigning local dev ports..."
PORTMAN="$HOME/coding/portman.sh"
DJANGO_PORT=8002
VITE_PORT=5175
if [ -x "$PORTMAN" ]; then
  PAIR="$("$PORTMAN" ensure "$PROJECT_NAME" 2>/dev/null || true)"
  if [ -n "$PAIR" ]; then
    DJANGO_PORT="${PAIR%% *}"
    VITE_PORT="${PAIR##* }"
  fi
  echo "  $PROJECT_NAME → django=$DJANGO_PORT vite=$VITE_PORT"
else
  echo "  portman.sh not found — keeping defaults django=$DJANGO_PORT vite=$VITE_PORT"
fi

# Rewrite the template default ports (8002/5175) in the generated .env examples
# so backend CORS/FRONTEND_URL and the frontend API URL line up with the pair.
for envf in backend/.env.example backend/.env frontend/.env.example frontend/.env; do
  [ -f "$envf" ] || continue
  sed -i '' "s/localhost:8002/localhost:$DJANGO_PORT/g; s/localhost:5175/localhost:$VITE_PORT/g" "$envf"
done

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
# Comment styles: line comments (# for py/yaml, // for js/ts) and HTML/Svelte
# block comments (<!-- --> in .svelte / .html markup).
for open_c, close_c in [('#', ''), ('//', ''), ('<!--', ' -->')]:
    pattern = (
        re.escape(open_c) + r' === FEATURE: ' + re.escape(feature) + r' ===' + re.escape(close_c) +
        r'.*?' +
        re.escape(open_c) + r' === END FEATURE: ' + re.escape(feature) + r' ===' + re.escape(close_c) + r'\n?'
    )
    text = re.sub(pattern, '', text, flags=re.DOTALL)
if text != original:
    open(path, 'w').write(text)
    # If stripping emptied the file (a whole-file feature wrap), signal deletion
    if text.strip() == '':
        print('EMPTIED')
" "$feature_name" "$file" | grep -q EMPTIED && {
      rm -f "$file"
      echo "    Removed emptied file $file"
    }
  done < <(find . \
    -not -path './.git/*' \
    -not -path './*/venv/*' \
    -not -path './*/node_modules/*' \
    -not -path '*/.svelte-kit/*' \
    -not -path '*/dist/*' \
    -type f \( \
      -name "*.py"   -o -name "*.ts"   -o -name "*.js"  -o \
      -name "*.svelte" -o -name "*.json" -o -name "*.yml" -o \
      -name "*.yaml" -o -name "*.txt"  -o -name "Procfile" -o -name "Makefile" \
    \) 2>/dev/null)

  # Remove any extra directories passed as arguments
  for dir in "$@"; do
    if [ -e "$dir" ]; then
      rm -rf "$dir"
      echo "    Removed $dir"
    fi
  done
}

# strip_pkg_scripts SCRIPT_NAME [SCRIPT_NAME...]
# Removes npm scripts from frontend/package.json. package.json is JSON and can't
# hold '// === FEATURE ===' markers, so strip_feature can't reach it — feature-
# specific scripts (cms islands build, capacitor cap:build) must be deleted here.
strip_pkg_scripts() {
  local pkg="frontend/package.json"
  [ -f "$pkg" ] || return 0
  python3 -c "
import json, sys
pkg = sys.argv[1]
names = sys.argv[2:]
data = json.load(open(pkg))
scripts = data.get('scripts', {})
removed = [n for n in names if scripts.pop(n, None) is not None]
if removed:
    json.dump(data, open(pkg, 'w'), indent=2)
    open(pkg, 'a').write('\n')
    print('    Removed package.json scripts: ' + ', '.join(removed))
" "$pkg" "$@"
}

$USE_STRIPE       || strip_feature stripe       backend/billing   frontend/src/routes/dashboard/billing
$USE_WORKSPACES   || strip_feature workspaces   backend/workspaces frontend/src/routes/dashboard/workspaces frontend/src/routes/workspaces
$USE_CMS          || strip_feature cms          backend/content   backend/static/islands   frontend/src/islands   frontend/vite.islands.config.ts
$USE_TASKS        || strip_feature tasks        backend/tasks
$USE_WEBSOCKETS   || strip_feature websockets   backend/realtime
$USE_S3           || strip_feature s3           backend/storage
# i18n is dual-marked: keep the ParaglideJS-wrapped layout when enabled (strip the
# plain 'no-i18n' fallback), or keep the plain fallback when disabled (strip i18n).
if ! $USE_I18N; then
  strip_feature i18n         frontend/project.inlang frontend/messages
  # Stripping the i18n block removed the <ParaglideJS> wrapper AND the
  # {@render children()} it contained. Restore a plain render in the layout.
  LAYOUT=frontend/src/routes/+layout.svelte
  if [ -f "$LAYOUT" ] && ! grep -q '@render children()' "$LAYOUT"; then
    printf '\n{@render children()}\n' >> "$LAYOUT"
    echo "    Restored plain {@render children()} in +layout.svelte (i18n disabled)"
  fi
fi
$USE_SENTRY       || strip_feature sentry
$USE_APIKEYS      || strip_feature apikeys      backend/apikeys   frontend/src/routes/dashboard/api-keys
$USE_GITHUB_OAUTH || strip_feature github-oauth
$USE_MOBILE       || strip_feature capacitor    frontend/capacitor.config.ts frontend/scripts/build-mobile.sh

# package.json npm scripts that reference feature files (JSON can't hold markers)
$USE_CMS          || strip_pkg_scripts build:islands dev:islands
$USE_MOBILE       || strip_pkg_scripts cap:build

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

# ── Remove / keep deploy files per provider ────────────────────────────────────

echo "Configuring deploy files for: $HOSTING..."

if [[ "$HOSTING" == "deploio" ]]; then
  # Remove PythonAnywhere files (not needed)
  rm -f deploy-remote.sh

  # Remove GitHub Actions staging workflow if staging is not used
  if ! $USE_STAGING; then
    rm -f .github/workflows/deploy-staging.yml
  fi

  # Write provider-specific deploy.sh
  cat > deploy.sh << DEPLOYEOF
#!/usr/bin/env bash
# deploy.sh — Deploy $PROJECT_NAME to deplo.io
# Usage: ./deploy.sh staging | ./deploy.sh production
set -eo pipefail

ENV=\${1:-staging}
REVISION=\$(git rev-parse HEAD)

[[ "\$ENV" != "staging" && "\$ENV" != "production" ]] && { echo "Usage: ./deploy.sh [staging|production]"; exit 1; }
command -v nctl &>/dev/null || { echo "nctl not found: brew install ninech/taps/nctl"; exit 1; }

# Load DEPLOIO_PROJECT from .env
if [ -f .env ]; then
  export \$(grep -v '^#' .env | grep 'DEPLOIO_PROJECT' | xargs 2>/dev/null) || true
fi
[ -z "\$DEPLOIO_PROJECT" ] && { echo "DEPLOIO_PROJECT not set in .env"; exit 1; }

echo "▶ Pushing to GitHub..."
git push origin HEAD

echo "▶ Deploying \$ENV @ \${REVISION:0:8}..."
nctl update app $PROJECT_NAME-\${ENV}-backend  --git-revision=\$REVISION --project=\$DEPLOIO_PROJECT --skip-repo-access-check
nctl update app $PROJECT_NAME-\${ENV}-frontend --git-revision=\$REVISION --project=\$DEPLOIO_PROJECT --skip-repo-access-check

echo ""
echo "✓ \$ENV deployed"
if [ "\$ENV" = "staging" ]; then
  echo "  Backend:  https://$PROJECT_NAME-staging-backend.deploio.app/api/auth/me/"
  echo "  Frontend: https://$PROJECT_NAME-staging-frontend.deploio.app"
else
DEPLOYEOF

  if [[ -n "$DOMAIN" ]]; then
    cat >> deploy.sh << DEPLOYEOF2
  echo "  Backend:  https://api.${DOMAIN}/api/auth/me/"
  echo "  Frontend: https://www.${DOMAIN}"
DEPLOYEOF2
  else
    cat >> deploy.sh << DEPLOYEOF3
  echo "  Backend:  https://$PROJECT_NAME-production-backend.deploio.app/api/auth/me/"
  echo "  Frontend: https://$PROJECT_NAME-production-frontend.deploio.app"
DEPLOYEOF3
  fi
  echo "fi" >> deploy.sh
  chmod +x deploy.sh

  # Write deploy-init.sh (one-time deplo.io provisioning script)
  _USE_STAGING_ARG=$USE_STAGING
  _USE_PRODUCTION_ARG=$USE_PRODUCTION
  _USE_TASKS_ARG=$USE_TASKS
  _DOMAIN_ARG="$DOMAIN"
  _GITHUB_ORG_ARG="$GITHUB_ORG"
  _GITHUB_REPO_ARG="$GITHUB_REPO"

  cat > deploy-init.sh << INITEOF
#!/usr/bin/env bash
# deploy-init.sh — One-time deplo.io setup for $PROJECT_NAME
# Run once after cloning: bash deploy-init.sh
#
# Prerequisites:
#   brew install ninech/taps/nctl
#   nctl auth login                          # opens browser → https://control.nine.ch
#   brew install gh && gh auth login         # optional, used to set GitHub Secrets
#
# Tokens to set before running:
#   export GITHUB_PAT="github_pat_..."       # → https://github.com/settings/personal-access-tokens/new
#                                            #   Permissions: Contents = Read-only (this repo only)
#   export RESEND_API_KEY="re_..."           # → https://resend.com/api-keys
#   export GOOGLE_CLIENT_ID="..."           # → https://console.cloud.google.com/apis/credentials
#   export GOOGLE_CLIENT_SECRET="..."       #   OAuth 2.0 Client ID, callback: /api/auth/google/callback/

set -eo pipefail

PROJECT_NAME="$PROJECT_NAME"
GIT_URL="https://github.com/${_GITHUB_ORG_ARG}/${_GITHUB_REPO_ARG}"
DOMAIN="${_DOMAIN_ARG}"

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "\${BLUE}▶ \$1\${NC}"; }
ok()   { echo -e "\${GREEN}✓ \$1\${NC}"; }
warn() { echo -e "\${YELLOW}⚠ \$1\${NC}"; }
die()  { echo -e "\${RED}✗ \$1\${NC}"; exit 1; }

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   $PROJECT_NAME — deplo.io Setup             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

command -v nctl &>/dev/null || die "nctl not found. Install: brew install ninech/taps/nctl"
nctl auth whoami &>/dev/null || { warn "Not logged in — starting login..."; nctl auth login; }
ok "nctl ready: \$(nctl auth whoami 2>/dev/null | head -1)"

[ -z "\$GITHUB_PAT" ] && die "GITHUB_PAT not set. Export it before running."
echo ""

# ── Projekt ermitteln ────────────────────────────────────────────────────────
log "Step 1 — Determine project"
DEPLOIO_PROJECT=\$(nctl get projects 2>/dev/null | awk 'NR==2 {print \$1}')
[ -z "\$DEPLOIO_PROJECT" ] && die "No project found. Check nctl auth login."
ok "Project: \$DEPLOIO_PROJECT"
nctl auth set-project "\$DEPLOIO_PROJECT"

# Write DEPLOIO_PROJECT to .env
if grep -q 'DEPLOIO_PROJECT' .env 2>/dev/null; then
  sed -i '' "s|DEPLOIO_PROJECT=.*|DEPLOIO_PROJECT=\$DEPLOIO_PROJECT|" .env
else
  echo "DEPLOIO_PROJECT=\$DEPLOIO_PROJECT" >> .env
fi
echo ""

# ── Apps anlegen ─────────────────────────────────────────────────────────────
log "Step 2 — Create apps"

INITEOF

  if $_USE_STAGING_ARG; then
    cat >> deploy-init.sh << INITEOF2
log "  Staging Backend..."
nctl create app ${PROJECT_NAME}-staging-backend \\
  --project="\$DEPLOIO_PROJECT" \\
  --git-url="\$GIT_URL" \\
  --git-sub-path=backend \\
  --git-revision=main \\
  --git-username=x-token-auth \\
  --git-password="\$GITHUB_PAT" \\
  --deploy-job-command="python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py createcachetable --no-color 2>/dev/null || true" \\
  --deploy-job-name=release \\
  2>/dev/null && ok "  ${PROJECT_NAME}-staging-backend" || warn "  Already exists"

log "  Staging Frontend..."
nctl create app ${PROJECT_NAME}-staging-frontend \\
  --project="\$DEPLOIO_PROJECT" \\
  --git-url="\$GIT_URL" \\
  --git-sub-path=frontend \\
  --git-revision=main \\
  --git-username=x-token-auth \\
  --git-password="\$GITHUB_PAT" \\
  2>/dev/null && ok "  ${PROJECT_NAME}-staging-frontend" || warn "  Already exists"
nctl update app ${PROJECT_NAME}-staging-frontend --project="\$DEPLOIO_PROJECT" --buildpack-stack=paketo
INITEOF2
  fi

  if $_USE_PRODUCTION_ARG; then
    cat >> deploy-init.sh << INITEOF3
log "  Production Backend..."
nctl create app ${PROJECT_NAME}-production-backend \\
  --project="\$DEPLOIO_PROJECT" \\
  --git-url="\$GIT_URL" \\
  --git-sub-path=backend \\
  --git-username=x-token-auth \\
  --git-password="\$GITHUB_PAT" \\
  --deploy-job-command="python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py createcachetable --no-color 2>/dev/null || true" \\
  --deploy-job-name=release \\
  2>/dev/null && ok "  ${PROJECT_NAME}-production-backend" || warn "  Already exists"

log "  Production Frontend..."
nctl create app ${PROJECT_NAME}-production-frontend \\
  --project="\$DEPLOIO_PROJECT" \\
  --git-url="\$GIT_URL" \\
  --git-sub-path=frontend \\
  --git-username=x-token-auth \\
  --git-password="\$GITHUB_PAT" \\
  2>/dev/null && ok "  ${PROJECT_NAME}-production-frontend" || warn "  Already exists"
nctl update app ${PROJECT_NAME}-production-frontend --project="\$DEPLOIO_PROJECT" --buildpack-stack=paketo
INITEOF3
  fi

  # Worker jobs (only if tasks feature active)
  if $_USE_TASKS_ARG; then
    cat >> deploy-init.sh << INITEOF4
echo ""
log "Step 3 — Configure worker jobs (django-q2)"
INITEOF4
    if $_USE_STAGING_ARG; then
      cat >> deploy-init.sh << INITEOF4B
nctl update app ${PROJECT_NAME}-staging-backend --project="\$DEPLOIO_PROJECT" \\
  --worker-job-command="python manage.py qcluster" --worker-job-name=qcluster \\
  2>/dev/null && ok "  Staging qcluster" || warn "  Already configured"
INITEOF4B
    fi
    if $_USE_PRODUCTION_ARG; then
      cat >> deploy-init.sh << INITEOF4C
nctl update app ${PROJECT_NAME}-production-backend --project="\$DEPLOIO_PROJECT" \\
  --worker-job-command="python manage.py qcluster" --worker-job-name=qcluster \\
  2>/dev/null && ok "  Production qcluster" || warn "  Already configured"
INITEOF4C
    fi
  fi

  # Databases
  cat >> deploy-init.sh << INITEOF5

echo ""
log "Step 4 — Create Postgres databases"
INITEOF5
  if $_USE_STAGING_ARG; then
    cat >> deploy-init.sh << INITEOF5B
nctl create postgres ${PROJECT_NAME}-staging-db --project="\$DEPLOIO_PROJECT" --wait \\
  2>/dev/null && ok "  ${PROJECT_NAME}-staging-db" || warn "  Already exists"
DB_STAGING_BASE=\$(nctl get postgres ${PROJECT_NAME}-staging-db --project="\$DEPLOIO_PROJECT" --print-connection-string 2>/dev/null)
DB_STAGING_URL="\${DB_STAGING_BASE}/${PROJECT_NAME}-staging-db"
INITEOF5B
  fi
  if $_USE_PRODUCTION_ARG; then
    cat >> deploy-init.sh << INITEOF5C
nctl create postgres ${PROJECT_NAME}-production-db --project="\$DEPLOIO_PROJECT" --wait \\
  2>/dev/null && ok "  ${PROJECT_NAME}-production-db" || warn "  Already exists"
DB_PROD_URL_BASE=\$(nctl get postgres ${PROJECT_NAME}-production-db --project="\$DEPLOIO_PROJECT" --print-connection-string 2>/dev/null)
DB_PROD_URL="\${DB_PROD_URL_BASE}/${PROJECT_NAME}-production-db"
INITEOF5C
  fi

  # Env vars
  cat >> deploy-init.sh << INITEOF6

echo ""
log "Step 5 — Set env vars"
[ -f ".env" ] && source .env || true
SK_STAGING=\$(openssl rand -hex 32)
SK_PROD=\$(openssl rand -hex 32)
INITEOF6
  if $_USE_STAGING_ARG; then
    cat >> deploy-init.sh << INITEOF6B
nctl update app ${PROJECT_NAME}-staging-backend --project="\$DEPLOIO_PROJECT" \\
  --env="SECRET_KEY=\$SK_STAGING" \\
  --env="DATABASE_URL=\$DB_STAGING_URL" \\
  --env="DEBUG=False" \\
  --env="ALLOWED_HOSTS=.deploio.app" \\
  --env="FRONTEND_URL=https://${PROJECT_NAME}-staging-frontend.deploio.app" \\
  --env="CORS_ALLOWED_ORIGINS=https://${PROJECT_NAME}-staging-frontend.deploio.app" \\
  \${RESEND_API_KEY:+--env="RESEND_API_KEY=\$RESEND_API_KEY"} \\
  --build-env="SECRET_KEY=\$SK_STAGING" \\
  --build-env="DATABASE_URL=sqlite:////tmp/build.db"
ok "  Staging Backend env"

nctl update app ${PROJECT_NAME}-staging-frontend --project="\$DEPLOIO_PROJECT" \\
  --build-env="PUBLIC_API_URL=https://${PROJECT_NAME}-staging-backend.deploio.app/api" \\
  --build-env="BP_STATIC_WEBROOT=build" \\
  --build-env="BP_WEB_SERVER_ENABLE_PUSH_STATE=true"
ok "  Staging Frontend env"
INITEOF6B
  fi
  if $_USE_PRODUCTION_ARG; then
    if [[ -n "$_DOMAIN_ARG" ]]; then
      cat >> deploy-init.sh << INITEOF6C
nctl update app ${PROJECT_NAME}-production-backend --project="\$DEPLOIO_PROJECT" \\
  --env="SECRET_KEY=\$SK_PROD" \\
  --env="DATABASE_URL=\$DB_PROD_URL" \\
  --env="DEBUG=False" \\
  --env="ALLOWED_HOSTS=.deploio.app,api.${_DOMAIN_ARG}" \\
  --env="FRONTEND_URL=https://www.${_DOMAIN_ARG}" \\
  --env="CORS_ALLOWED_ORIGINS=https://www.${_DOMAIN_ARG},https://${_DOMAIN_ARG}" \\
  \${RESEND_API_KEY:+--env="RESEND_API_KEY=\$RESEND_API_KEY"} \\
  --build-env="SECRET_KEY=\$SK_PROD" \\
  --build-env="DATABASE_URL=sqlite:////tmp/build.db"
ok "  Production Backend env"

nctl update app ${PROJECT_NAME}-production-frontend --project="\$DEPLOIO_PROJECT" \\
  --build-env="PUBLIC_API_URL=https://api.${_DOMAIN_ARG}/api" \\
  --build-env="BP_STATIC_WEBROOT=build" \\
  --build-env="BP_WEB_SERVER_ENABLE_PUSH_STATE=true"
ok "  Production Frontend env"
INITEOF6C
    else
      cat >> deploy-init.sh << INITEOF6D
nctl update app ${PROJECT_NAME}-production-backend --project="\$DEPLOIO_PROJECT" \\
  --env="SECRET_KEY=\$SK_PROD" \\
  --env="DATABASE_URL=\$DB_PROD_URL" \\
  --env="DEBUG=False" \\
  --env="ALLOWED_HOSTS=.deploio.app" \\
  --env="FRONTEND_URL=https://${PROJECT_NAME}-production-frontend.deploio.app" \\
  --env="CORS_ALLOWED_ORIGINS=https://${PROJECT_NAME}-production-frontend.deploio.app" \\
  \${RESEND_API_KEY:+--env="RESEND_API_KEY=\$RESEND_API_KEY"} \\
  --build-env="SECRET_KEY=\$SK_PROD" \\
  --build-env="DATABASE_URL=sqlite:////tmp/build.db"
ok "  Production Backend env"

nctl update app ${PROJECT_NAME}-production-frontend --project="\$DEPLOIO_PROJECT" \\
  --build-env="PUBLIC_API_URL=https://${PROJECT_NAME}-production-backend.deploio.app/api" \\
  --build-env="BP_STATIC_WEBROOT=build" \\
  --build-env="BP_WEB_SERVER_ENABLE_PUSH_STATE=true"
ok "  Production Frontend env"
INITEOF6D
    fi
  fi

  # Service Account
  cat >> deploy-init.sh << INITEOF7

echo ""
log "Step 6 — CI/CD Service Account"
nctl create apiserviceaccount ${PROJECT_NAME}-ci --project="\$DEPLOIO_PROJECT" \\
  2>/dev/null && ok "  Service account '${PROJECT_NAME}-ci' created" || warn "  Already exists"

echo ""
echo ""
echo "══════════════════════════════════════════════"
echo "  GitHub Secrets — add these at:"
echo "  https://github.com/${_GITHUB_ORG_ARG}/${_GITHUB_REPO_ARG}/settings/secrets/actions"
echo "══════════════════════════════════════════════"
echo ""
CREDS=\$(nctl get apiserviceaccount ${PROJECT_NAME}-ci --project="\$DEPLOIO_PROJECT" --print-credentials 2>/dev/null)
if [ -n "\$CREDS" ]; then
  CLIENT_ID=\$(echo "\$CREDS" | grep -i 'client.id\|clientId\|client_id' | awk '{print \$NF}')
  CLIENT_SECRET=\$(echo "\$CREDS" | grep -i 'client.secret\|clientSecret\|client_secret' | awk '{print \$NF}')
  echo "  NCTL_API_CLIENT_ID     = \$CLIENT_ID"
  echo "  NCTL_API_CLIENT_SECRET = \$CLIENT_SECRET"
  echo "  NCTL_ORGANIZATION      = \$DEPLOIO_PROJECT"
  echo ""
  echo "  Or use gh CLI:"
  echo "  gh secret set NCTL_API_CLIENT_ID     --body \"\$CLIENT_ID\"     --repo ${_GITHUB_ORG_ARG}/${_GITHUB_REPO_ARG}"
  echo "  gh secret set NCTL_API_CLIENT_SECRET --body \"\$CLIENT_SECRET\" --repo ${_GITHUB_ORG_ARG}/${_GITHUB_REPO_ARG}"
  echo "  gh secret set NCTL_ORGANIZATION      --body \"\$DEPLOIO_PROJECT\" --repo ${_GITHUB_ORG_ARG}/${_GITHUB_REPO_ARG}"
else
  warn "Could not fetch credentials automatically. Run manually:"
  warn "  nctl get apiserviceaccount ${PROJECT_NAME}-ci --project=\$DEPLOIO_PROJECT --print-credentials"
fi
INITEOF7

  # Production DNS section
  if $_USE_PRODUCTION_ARG && [[ -n "$_DOMAIN_ARG" ]]; then
    cat >> deploy-init.sh << INITEOF8

echo ""
log "Step 7 — Production DNS + Custom Domains"
warn "  Set DNS CNAMEs at your registrar before running this step:"
warn "    api.${_DOMAIN_ARG}  CNAME  ${PROJECT_NAME}-production-backend.deploio.app"
warn "    www.${_DOMAIN_ARG}  CNAME  ${PROJECT_NAME}-production-frontend.deploio.app"
warn "  Infomaniak: use API v2 (/2/zones/{domain}/records) — v1 breaks DKIM records."
warn "  Apex redirect (${_DOMAIN_ARG} → www): manual in Infomaniak Manager → Weiterleitungen"
echo ""
read -p "DNS records set? Register custom domains now? [y/N]: " _dns_ready
if [[ "\$_dns_ready" =~ ^[Yy]\$ ]]; then
  nctl update app ${PROJECT_NAME}-production-backend --project="\$DEPLOIO_PROJECT" --hosts="api.${_DOMAIN_ARG}" \\
    && ok "  api.${_DOMAIN_ARG} registered (TLS provisioning ~5 min)" || warn "  Check api.${_DOMAIN_ARG}"
  nctl update app ${PROJECT_NAME}-production-frontend --project="\$DEPLOIO_PROJECT" --hosts="www.${_DOMAIN_ARG}" \\
    && ok "  www.${_DOMAIN_ARG} registered (TLS provisioning ~5 min)" || warn "  Check www.${_DOMAIN_ARG}"
fi
INITEOF8
  fi

  # Closing summary
  cat >> deploy-init.sh << INITEOF9

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Setup complete!                            ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
INITEOF9

  if $_USE_STAGING_ARG; then
    cat >> deploy-init.sh << INITEOF10
echo "  Staging: https://${PROJECT_NAME}-staging-frontend.deploio.app"
INITEOF10
  fi
  if $_USE_PRODUCTION_ARG && [[ -n "$_DOMAIN_ARG" ]]; then
    cat >> deploy-init.sh << INITEOF11
echo "  Production: https://www.${_DOMAIN_ARG}"
INITEOF11
  fi
  cat >> deploy-init.sh << INITEOF12
echo ""
echo "  Next: bash deploy.sh staging   # triggers first build"
INITEOF12

  chmod +x deploy-init.sh
  echo "  deploy.sh (deplo.io) written."
  echo "  deploy-init.sh written."

elif [[ "$HOSTING" == "pythonanywhere" ]]; then
  # Remove deplo.io-specific files
  rm -f deploy-init.sh .deploio.yaml
  rm -f .github/workflows/deploy-staging.yml

  # Write deploy-remote.sh with project-specific paths
  sed -i '' "s|PA_USERNAME|${PA_USERNAME}|g" deploy-remote.sh
  sed -i '' "s|PA_APP_DIR|${PA_APP_DIR#/home/${PA_USERNAME}/}|g" deploy-remote.sh

  # Write PA-specific deploy.sh
  cat > deploy.sh << PA_DEPLOYEOF
#!/usr/bin/env bash
# deploy.sh — Deploy $PROJECT_NAME to PythonAnywhere
# Usage: ./deploy.sh [staging|production] [branch]
set -eo pipefail

ENV=\${1:-staging}
BRANCH=\${2:-\$(git rev-parse --abbrev-ref HEAD)}
PA_USERNAME="${PA_USERNAME}"
PA_WEBAPP_DOMAIN="${PA_WEBAPP_DOMAIN}"
PA_APP_DIR="${PA_APP_DIR}"

[[ "\$ENV" != "staging" && "\$ENV" != "production" ]] && { echo "Usage: ./deploy.sh [staging|production] [branch]"; exit 1; }

# Load PA_TOKEN from .env
if [ -f .env ]; then
  export \$(grep -v '^#' .env | grep 'PA_TOKEN' | xargs 2>/dev/null) || true
fi
[ -z "\$PA_TOKEN" ] && { echo "PA_TOKEN not set in .env (get from pythonanywhere.com → Account → API Token)"; exit 1; }

# Check for uncommitted changes
if [ -n "\$(git status --porcelain)" ]; then
  echo "⚠  Uncommitted changes — only pushed commits will be deployed."
  read -p "Continue? [y/N]: " _cont
  [[ "\$_cont" =~ ^[Yy]\$ ]] || exit 0
fi

echo "▶ Pushing \$BRANCH to GitHub..."
git push origin "\$BRANCH"

echo "▶ Deploying \$ENV @ \$BRANCH..."
ssh "\$PA_USERNAME@ssh.pythonanywhere.com" "bash \$PA_APP_DIR/deploy-remote.sh \$ENV \$BRANCH"

echo "▶ Reloading webapp..."
curl -s -X POST "https://www.pythonanywhere.com/api/v0/user/\${PA_USERNAME}/webapps/\${PA_WEBAPP_DOMAIN}/reload/" \\
  -H "Authorization: Token \$PA_TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ✓ Reloaded' if d.get('status')=='OK' else '  ⚠ ' + str(d))"

echo ""
echo "✓ \$ENV deployed @ \$BRANCH"
echo "  URL: https://\$PA_WEBAPP_DOMAIN"
echo "  API: https://\$PA_WEBAPP_DOMAIN/api/auth/me/"
PA_DEPLOYEOF
  chmod +x deploy.sh
  echo "  deploy.sh (PythonAnywhere) written."

else
  # No hosting — remove all deploy scripts
  rm -f deploy.sh deploy-init.sh deploy-remote.sh .deploio.yaml
  rm -f .github/workflows/deploy-staging.yml
  echo "  No hosting selected — deploy files removed."
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

# ── Generate CLAUDE.md ────────────────────────────────────────────────────────

echo "Generating CLAUDE.md..."

# Build feature list for the "was drin ist" section
FEATURES_INCLUDED="- Auth: Magic Link (passwordless) + Google OAuth2
- JWT: both tokens in localStorage, auto-refresh on 401
- User model: UUID pk, email-only, language preference
- REST API + OpenAPI Docs (\`/api/docs/\`)"

$USE_CMS        && FEATURES_INCLUDED="$FEATURES_INCLUDED
- CMS: feincms3, server-rendered HTML by Django (crawlable, instant-live on save), Svelte islands for interactivity, JSON API at /api/cms/page/?path=/, admin editor"
$USE_S3         && FEATURES_INCLUDED="$FEATURES_INCLUDED
- S3 Storage: nine.ch, presigned upload/download URLs"
$USE_TASKS      && FEATURES_INCLUDED="$FEATURES_INCLUDED
- Background Tasks: django-q2"
$USE_SENTRY     && FEATURES_INCLUDED="$FEATURES_INCLUDED
- Sentry: Backend + Frontend"
$USE_STRIPE     && FEATURES_INCLUDED="$FEATURES_INCLUDED
- Stripe: Subscriptions, one-time payments, webhooks"
$USE_WORKSPACES && FEATURES_INCLUDED="$FEATURES_INCLUDED
- Workspaces & Teams: multi-tenant, roles, invitation flow"
$USE_APIKEYS    && FEATURES_INCLUDED="$FEATURES_INCLUDED
- API Key Management: create/revoke, Authorization: ApiKey header"
$USE_WEBSOCKETS && FEATURES_INCLUDED="$FEATURES_INCLUDED
- Websockets: django-channels, JWT-authenticated, per-user groups"
$USE_I18N       && FEATURES_INCLUDED="$FEATURES_INCLUDED
- i18n: Paraglide, de/en"
$USE_GITHUB_OAUTH && FEATURES_INCLUDED="$FEATURES_INCLUDED
- GitHub OAuth: second OAuth2 provider"
$USE_MOBILE     && FEATURES_INCLUDED="$FEATURES_INCLUDED
- Capacitor: iOS/Android build"
$USE_FEEDLOOP   && FEATURES_INCLUDED="$FEATURES_INCLUDED
- Feedloop: feedback widget, screen recording, screenshots, AI triage, GitHub Issues"

cat > CLAUDE.md << CLAUDEEOF
# CLAUDE.md

## Was dieses Repo ist

**$PROJECT_NAME** — basiert auf dem SaasKiller-Template (\`blindflugmoritz/saaskiller\`).

<!-- Beschreibe hier kurz was dieses Projekt ist und für wen. -->

## Stack

**Backend:** Django 5 + DRF + SimpleJWT + django-allauth
**Frontend:** SvelteKit + TypeScript + Tailwind 4
**DB lokal:** SQLite / **Prod:** Postgres$(if [[ "$HOSTING" == "deploio" ]]; then echo " auf deplo.io"; elif [[ "$HOSTING" == "pythonanywhere" ]]; then echo " auf PythonAnywhere"; fi)
**Email:** Anymail + Resend
**Deploy:** $(if [[ "$HOSTING" == "deploio" ]]; then echo "deplo.io via \`nctl\` CLI"; elif [[ "$HOSTING" == "pythonanywhere" ]]; then echo "PythonAnywhere via SSH + PA API"; else echo "lokal / manuell"; fi)

## Projektstruktur

\`\`\`
backend/
  $PROJECT_NAME/      Django settings, urls, wsgi, asgi
  users/              Custom user model, auth views (Magic Link + OAuth2)
  tests/              pytest tests (one file per app)

frontend/
  src/lib/
    api/
      client.ts       ApiClient: JWT injection, auto-refresh, snake↔camel transform
      auth.ts         Auth API functions
    stores/           Svelte 5 class-based stores
    components/       Shared UI components
  src/routes/         SvelteKit pages
\`\`\`

## Was drin ist

$FEATURES_INCLUDED

## Local dev

\`\`\`bash
# Backend
cd backend && source venv/bin/activate && python manage.py runserver   # → http://localhost:8002

# Frontend
cd frontend && npm run dev                                              # → http://localhost:5175
\`\`\`

Makefile-Shortcuts:
\`\`\`bash
make dev-be          # Django dev server
make dev-fe          # Vite dev server
$(if $USE_CMS; then echo "make dev-islands     # Islands watch build (terminal 3, CMS only)"; fi)
make migrate
make makemigrations
make createsuperuser
make shell
make test-be         # pytest
make test-fe         # vitest
make test-all        # pytest + vitest + playwright
$(${USE_CMS} && echo 'make build-islands   # Svelte islands build → backend/static/islands/ (run before collectstatic)
make dev-islands     # watch-mode islands build (terminal 4, only needed when editing islands)')
\`\`\`

URLs lokal:
- Frontend: http://localhost:5175
- Django Admin: http://localhost:8002/admin/
- API Docs: http://localhost:8002/api/docs/

> **Ports müssen zusammenpassen:** \`backend/.env\` → \`CORS_ALLOWED_ORIGINS=http://localhost:5175\`, \`frontend/.env\` → \`PUBLIC_API_URL=http://localhost:8002/api\`. Bei Abweichungen gibt es CORS-Fehler oder leere Seiten.

## Testing

### Backend (pytest-django)
- Config: \`backend/pytest.ini\` — \`DJANGO_SETTINGS_MODULE = $PKG_NAME.settings\`
- Tests: \`backend/tests/test_<app>.py\` — eine Datei pro App
- Fixtures:
  \`\`\`python
  @pytest.fixture
  def client():
      return APIClient()

  @pytest.fixture
  def user(db):
      return User.objects.create_user(email='test@example.com')

  @pytest.fixture
  def auth_client(user):
      client = APIClient()
      refresh = RefreshToken.for_user(user)
      client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
      return client
  \`\`\`
- Ausführen: \`make test-be\`

### Frontend (Vitest)
- Config: \`frontend/vitest.config.ts\` — jsdom, \`\$lib\` alias
- Tests: neben dem Modul (\`client.ts\` → \`client.test.ts\`)
- Ausführen: \`make test-fe\`

### E2E (Playwright)
- Tests: \`frontend/tests/\`
- Ausführen: \`make test-all\`

### Regeln
- Test zuerst schreiben, rot sehen, dann Code
- Nie rote Tests committen
- Pure functions → unit tests; Komponenten → @testing-library/svelte; Flows → Playwright

## Auth Flow (Magic Link → JWT)

1. Email eingeben → \`POST /api/auth/signup/\` oder \`POST /api/auth/request-magic-link/\`
2. Backend generiert \`magic_link_token\`, sendet Email
3. User klickt Link → \`GET /api/auth/login/<token>/\`
4. Backend gibt \`{ access, refresh }\` zurück
5. Frontend: both tokens in localStorage (\`lib/utils/tokenStorage.ts\`)
6. Bei 401: auto \`POST /api/auth/refresh/\` → neuer access token

## Development Workflow (pro Feature)

\`\`\`
1. Beschreiben   was soll es tun?
2. Test BE       pytest test schreiben, rot erwarten
3. Build BE      Model → Serializer → View → grün
4. Test FE       Vitest test schreiben, rot erwarten
5. Build FE      Component/Store → grün
6. E2E           Playwright test → grün
$(if [[ "$HOSTING" == "deploio" && "$USE_STAGING" == "true" ]]; then
  echo "7. Deploy        ./deploy.sh staging → prüfen → ./deploy.sh production"
elif [[ "$HOSTING" == "deploio" ]]; then
  echo "7. Deploy        ./deploy.sh production"
elif [[ "$HOSTING" == "pythonanywhere" ]]; then
  echo "7. Deploy        ./deploy.sh staging \$BRANCH → prüfen → ./deploy.sh production \$BRANCH"
else
  echo "7. Deploy        (kein Hosting konfiguriert)"
fi)
$(if $USE_CMS; then cat << 'CMSEOF'

## CMS / Islands

Pages werden von Django als volles HTML gerendert (crawlbar, kein Node-Server).
Interaktive Svelte-Komponenten werden als Islands eingebettet.

**Islands-Assets** (\`backend/static/islands/\`) sind **committed** (kein Build-Step auf Deploio nötig).
Pflichtschritt vor jedem Deploy wenn Islands-Komponenten geändert wurden:
\`\`\`bash
make build-islands
git add backend/static/islands/
git commit -m "chore: rebuild islands"
\`\`\`
CI (\`islands-drift\`-Job) schlägt an wenn Assets nicht aktuell sind.

Admin-URL für CMS: \`/admin/content/page/\`
CMSEOF
fi)
\`\`\`

## API Conventions

- Alle Endpoints unter \`/api/\`
- Auth: \`/api/auth/\`
- App-Endpoints: \`/api/<app>/\`
- Responses: JSON, snake_case keys
- Errors: \`{ "detail": "..." }\` oder \`{ "field": ["error"] }\`

## Architektur-Regeln (nicht verhandelbar)

1. **Svelte 5 runes** — \`\$state\`, \`\$derived\`, \`\$effect\`. Kein \`writable()\`.
2. **snake↔camelCase nur an der API-Grenze** — Transform in \`lib/api/client.ts\`. Nirgendwo sonst.
3. **Class-based stores** — async Operationen durch Store-Methoden. Nie State von Komponenten mutieren.
4. **Backend-first** — Models → Serializers → Views → Tests → Frontend.
5. **Test-first** — Test schreiben, rot sehen, dann Code.
6. **Tailwind 4** — via \`@tailwindcss/vite\`. Kein \`tailwind.config.js\`.
7. **Pure functions first** — Business Logic als pure functions, dann in Stores/Komponenten einbauen.

## DO NOT

- Store-State von Komponenten mutieren: \`authStore.user = null\` ❌
- snake↔camel Transform bypassen oder doppelt anwenden ❌
- JWT mit Session-Auth bypassen ❌
- \`.env\`, \`db.sqlite3\`, \`venv/\`, \`node_modules/\` committen ❌
- \`tailwind.config.js\` anlegen ❌
- Rote Tests committen ❌
$(if $USE_CMS; then echo "- Islands-Komponenten ändern ohne \`make build-islands\` → commit ❌"; fi)
CLAUDEEOF

echo "  CLAUDE.md generated."

# ── Generate README.md ────────────────────────────────────────────────────────

echo "Generating README.md..."

cat > README.md << READMEEOF
# $PROJECT_NAME

<!-- Describe what this project does and who it's for. -->

## Local dev

First time after cloning:

\`\`\`bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
make setup     # creates venv, pip install, migrate, npm install
\`\`\`

Every day:

\`\`\`bash
make dev-be   # Django on http://localhost:8002
make dev-fe   # Vite on http://localhost:5175
\`\`\`

## Tests

\`\`\`bash
make test-be    # pytest
make test-fe    # vitest
make test-all   # pytest + vitest + playwright
\`\`\`

## Deploy

$(if [[ "$HOSTING" == "deploio" ]]; then
echo "\`\`\`bash
# First time — provision apps, databases, env vars
export GITHUB_PAT=\"github_pat_...\"
bash deploy-init.sh

# Every deploy
./deploy.sh staging
./deploy.sh production
\`\`\`"
elif [[ "$HOSTING" == "pythonanywhere" ]]; then
echo "\`\`\`bash
# Set PA_TOKEN in .env (pythonanywhere.com → Account → API Token)
./deploy.sh staging
./deploy.sh production
\`\`\`"
else
echo "No hosting configured. See CLAUDE.md for local setup."
fi)

## Stack

Built on [SaasKiller](https://github.com/blindflugmoritz/saaskiller) — Django 5 + SvelteKit.
READMEEOF

echo "  README.md generated."

# ── Post-strip guard: catch orphaned feature code ─────────────────────────────
# Verify feature stripping didn't leave dangling references. If node_modules is
# present we run the real typecheck; otherwise a cheap static scan for imports of
# modules that live only in stripped features. Warns loudly but does not abort —
# the project is still usable and the author can fix before first `make dev`.

echo "Verifying frontend after strip..."
GUARD_WARN=0
if [ -d frontend/node_modules ]; then
  ( cd frontend && npm run check >/tmp/${PROJECT_NAME}-check.log 2>&1 ) \
    && echo "  ✓ npm run check passed" \
    || { echo "  ⚠ npm run check reported errors — see /tmp/${PROJECT_NAME}-check.log"; GUARD_WARN=1; }
else
  # Static scan: any import of a $lib module whose file no longer exists?
  MISSING=$(cd frontend && grep -rhoE "from '(\\\$lib/[^']+)'" src --include=*.ts --include=*.svelte 2>/dev/null \
    | sed -E "s/from '\\\$lib\/([^']+)'/\1/" | sort -u \
    | while read -r mod; do
        base="src/lib/$mod"
        # skip if any resolution exists (.ts, .svelte, dir/index, or dir itself)
        [ -e "$base.ts" ] || [ -e "$base.svelte" ] || [ -e "$base/index.ts" ] || [ -d "$base" ] || echo "$mod"
      done)
  if [ -n "$MISSING" ]; then
    echo "  ⚠ Dangling imports of stripped modules:"
    echo "$MISSING" | sed 's/^/      $lib\//'
    echo "    (run 'cd frontend && npm install && npm run check' to confirm)"
    GUARD_WARN=1
  else
    echo "  ✓ no dangling \$lib imports detected"
  fi
fi
[ "$GUARD_WARN" = 1 ] && echo "  → Strip left some orphans. Fix before committing to your repo."

# ── Regenerate the capabilities manifest for this fork ────────────────────────
# After stripping, capabilities.json should describe THIS project's real feature
# set, not the template's. The generator reads code + setup.sh, so it self-heals.
if [ -f scripts/gen_capabilities.py ]; then
  echo "Regenerating capabilities.json..."
  python3 scripts/gen_capabilities.py >/dev/null 2>&1 \
    && echo "  ✓ capabilities.json updated" \
    || echo "  ⚠ could not regenerate capabilities.json (run it manually)"
fi

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
echo "  2. make setup    ← creates venv, installs deps, runs migrations, npm install"
echo "  3. make dev-be   (terminal 1 — Django on http://localhost:$DJANGO_PORT)"
echo "  4. make dev-fe   (terminal 2 — Vite on http://localhost:$VITE_PORT)"
echo ""
if [[ "$HOSTING" == "deploio" ]]; then
  echo "  ── Deploy Setup (run once) ───────────────────────────────"
  echo ""
  echo "  Step A — Install nctl + login:"
  echo "    brew install ninech/taps/nctl"
  echo "    nctl auth login              ← opens browser, logs you into deplo.io"
  echo "    (Account: https://control.nine.ch)"
  echo ""
  echo "  Step B — GitHub Personal Access Token (PAT):"
  echo "    → https://github.com/settings/personal-access-tokens/new"
  echo "    Name: $PROJECT_NAME-deploy"
  echo "    Repository access: only this repo"
  echo "    Permissions: Contents = Read-only"
  echo "    Copy the token (starts with github_pat_...)"
  echo ""
  echo "  Step C — Optional API keys (set before running deploy-init.sh):"
  echo "    Resend (email):  https://resend.com/api-keys  → create key"
  echo "    Google OAuth:    https://console.cloud.google.com/apis/credentials → OAuth 2.0 Client"
  echo ""
  echo "  Step D — Run the one-time provisioning script:"
  echo "    export GITHUB_PAT=github_pat_..."
  echo "    export RESEND_API_KEY=re_...          # optional"
  echo "    export GOOGLE_CLIENT_ID=...           # optional"
  echo "    export GOOGLE_CLIENT_SECRET=...       # optional"
  echo "    bash deploy-init.sh"
  echo ""
  echo "    → Creates apps + Postgres on deplo.io, sets all env vars,"
  echo "      and prints the 3 GitHub Secrets you need to add."
  echo ""
  echo "  Step E — Add GitHub Secrets (URL printed by deploy-init.sh):"
  echo "    → https://github.com/${GITHUB_ORG}/${GITHUB_REPO}/settings/secrets/actions"
  echo "    Add: NCTL_API_CLIENT_ID, NCTL_API_CLIENT_SECRET, NCTL_ORGANIZATION"
  echo ""
  echo "  ── Deploy (ongoing) ──────────────────────────────────────"
  echo ""
  echo "    ./deploy.sh staging          ← manual deploy"
  if $USE_PRODUCTION; then
    echo "    ./deploy.sh production"
  fi
  echo "    git push origin main         ← auto-deploys staging via GitHub Actions"
  echo ""
elif [[ "$HOSTING" == "pythonanywhere" ]]; then
  echo "  ── Deploy Setup (run once) ───────────────────────────────"
  echo ""
  echo "  Step A — Get your PA API token:"
  echo "    pythonanywhere.com → Account → API Token → Create"
  echo "    Add to .env:  PA_TOKEN=your_token_here"
  echo ""
  echo "  Step B — First deploy (manual):"
  echo "    Push your repo to GitHub, then SSH in:"
  echo "    ssh $PA_USERNAME@ssh.pythonanywhere.com"
  echo "    cd $PA_APP_DIR && git clone <your-repo-url> ."
  echo "    bash deploy-remote.sh staging main"
  echo ""
  echo "  ── Deploy (ongoing) ──────────────────────────────────────"
  echo ""
  echo "    ./deploy.sh staging          ← push + SSH + reload"
  if $USE_PRODUCTION; then
    echo "    ./deploy.sh production"
  fi
  echo ""
fi
echo ""
