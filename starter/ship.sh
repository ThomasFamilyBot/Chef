#!/bin/bash
# Publish a fresh starter to the public template repo. Run from anywhere:  bash starter/ship.sh
# Exports committed HEAD, stops unless the scrub is clean, then replaces the template's contents and pushes.
# Runs by itself once a day on GitHub (.github/workflows/starter.yml); run it by hand only for a same-day update.
# Access: by default the ThomasFamilyBot login in the gh CLI. With STARTER_REMOTE set (the daily job does this,
# with an SSH deploy key in GIT_SSH_COMMAND), plain git talks to that address instead.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="ThomasFamilyBot/chefbot-starter"
ACCOUNT="ThomasFamilyBot"
cd "$ROOT"
if [ -n "$(git status --porcelain)" ]; then echo "Uncommitted changes: commit first (the export reads HEAD)."; exit 1; fi
WORK="$(mktemp -d)"
python3 starter/export.py "$WORK/export" | tee "$WORK/export.log"
grep -q "^scrub: clean" "$WORK/export.log" || { echo "Scrub not clean; nothing published."; exit 2; }
if [ -n "${STARTER_REMOTE:-}" ]; then
  REMOTE="$STARTER_REMOTE"; AUTH=()
else
  # Push as the template's owner without switching the active gh account.
  CRED='!f() { echo username='"$ACCOUNT"'; echo "password=$(gh auth token --user '"$ACCOUNT"')"; }; f'
  REMOTE="https://github.com/$TEMPLATE"; AUTH=(-c credential.helper= -c "credential.helper=$CRED")
fi
g() { git ${AUTH[@]+"${AUTH[@]}"} "$@"; }
g clone -q "$REMOTE" "$WORK/repo"
cd "$WORK/repo"
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$WORK/export/." .
git add -A
if git diff --cached --quiet; then
  g push -q --dry-run origin HEAD      # nothing to publish; still confirm we could have (catches a dead key early)
  echo "Starter already up to date (write access confirmed)."; exit 0
fi
git diff --cached --stat | tail -15
git -c user.name="$ACCOUNT" -c user.email="$ACCOUNT@users.noreply.github.com" commit -q -m "Update starter from ChefBot $(git -C "$ROOT" rev-parse --short HEAD)"
g push -q origin HEAD
echo "Published to https://github.com/$TEMPLATE"
