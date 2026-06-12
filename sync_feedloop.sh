#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FEEDLOOP_DIR="${FEEDLOOP_PATH:-$HOME/coding/feedloop}"

if [ ! -d "$FEEDLOOP_DIR" ]; then
  echo "Error: feedloop repo not found at $FEEDLOOP_DIR"
  echo "Set FEEDLOOP_PATH=/path/to/feedloop or clone it there."
  exit 1
fi

echo "Syncing feedloop from $FEEDLOOP_DIR ..."

rsync -av --delete \
  "$FEEDLOOP_DIR/backend/feedback/" \
  "$SCRIPT_DIR/backend/feedback/"

rsync -av --delete \
  "$FEEDLOOP_DIR/frontend/components/feedback/" \
  "$SCRIPT_DIR/frontend/src/lib/components/feedback/"

echo ""
echo "Done. Check the diff and run migrations if models changed:"
echo "  git diff"
echo "  cd backend && python manage.py makemigrations feedback && python manage.py migrate"
