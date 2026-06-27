#!/usr/bin/env bash
# deploy-remote.sh — runs ON PythonAnywhere via SSH. Do NOT run locally.
# Usage: bash deploy-remote.sh [staging|production] [branch]
set -e

ENV=${1:-staging}
BRANCH=${2:-main}
APP_DIR=/home/PA_USERNAME/PA_APP_DIR

cd "$APP_DIR"

git fetch origin
git checkout -f "$BRANCH"
git reset --hard "origin/$BRANCH"

# Python deps
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r backend/requirements.txt --quiet --upgrade

# Frontend build
echo "Building frontend..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
cd "$APP_DIR/frontend"
npm ci --no-audit --no-fund --silent
PUBLIC_API_URL="$(grep PUBLIC_API_URL "$APP_DIR/.env.${ENV}" 2>/dev/null | cut -d= -f2-)" \
  npm run build
cd "$APP_DIR"

# Django migrate + collectstatic
python backend/manage.py migrate --settings=saaskiller.settings
python backend/manage.py collectstatic --noinput --settings=saaskiller.settings

mkdir -p backend/media

echo "DEPLOY_DONE: $BRANCH -> $ENV ($APP_DIR)"
