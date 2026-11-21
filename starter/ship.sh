#!/bin/bash
# Publish a fresh starter to the public template repo. Run from anywhere:  bash starter/ship.sh
# Exports committed HEAD, stops unless the scrub is clean, then replaces the template's contents and pushes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="ThomasFamilyBot/chefbot-starter"
ACCOUNT="ThomasFamilyBot"
cd "$ROOT"
if [ -n "$(git status --porcelain)" ]; then echo "Uncommitted changes: commit first (the export reads HEAD)."; exit 1; fi
WORK="$(mktemp -d)"
python3 starter/export.py "$WORK/export" | tee "$WORK/export.log"
grep -q "^scrub: clean" "$WORK/export.log" || { echo "Scrub not clean; nothing published."; exit 2; }
# Push as the template's owner without switching the active gh account.
CRED='!f() { echo username='"$ACCOUNT"'; echo "password=$(gh auth token --user '"$ACCOUNT"')"; }; f'
git -c credential.helper= -c "credential.helper=$CRED" clone -q "https://github.com/$TEMPLATE" "$WORK/repo"
cd "$WORK/repo"
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$WORK/export/." .
git add -A
if git diff --cached --quiet; then echo "Starter already up to date."; exit 0; fi
git diff --cached --stat | tail -15
git -c user.name="$ACCOUNT" -c user.email="$ACCOUNT@users.noreply.github.com" commit -q -m "Update starter from ChefBot $(git -C "$ROOT" rev-parse --short HEAD)"
git -c credential.helper= -c "credential.helper=$CRED" push -q origin HEAD
echo "Published to https://github.com/$TEMPLATE"
