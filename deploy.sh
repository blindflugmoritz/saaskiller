#!/usr/bin/env bash
set -e

ENV=${1:-staging}
if [[ "$ENV" != "staging" && "$ENV" != "production" ]]; then
  echo "Usage: ./deploy.sh [staging|production]"
  exit 1
fi

# Load env
if [ -f .env ]; then
  export $(grep -v '^#' .env | grep -E 'NCTL_|DEPLOIO_' | xargs)
fi

BACKEND_APP="saaskiller-${ENV}-backend"
FRONTEND_APP="saaskiller-${ENV}-frontend"
REVISION=$(git rev-parse HEAD)

echo "▶ Deploying to $ENV (rev: ${REVISION:0:8})"

# Push to GitHub
git push origin HEAD

# Deploy backend
echo "  → Backend: $BACKEND_APP"
nctl update app "$BACKEND_APP" \
  --project "$DEPLOIO_PROJECT" \
  --git-revision="$REVISION" \
  --skip-repo-access-check

# Deploy frontend
echo "  → Frontend: $FRONTEND_APP"
nctl update app "$FRONTEND_APP" \
  --project "$DEPLOIO_PROJECT" \
  --git-revision="$REVISION" \
  --skip-repo-access-check

echo "✓ Deployed to $ENV"
echo "  Backend:  https://${BACKEND_APP}.deploio.app/api/health/"
echo "  Frontend: https://${FRONTEND_APP}.deploio.app"
