#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
npm run build
npx cap sync
echo "Mobile build synced. Open Xcode: npx cap open ios"
echo "Open Android Studio: npx cap open android"
