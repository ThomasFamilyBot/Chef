---
name: drive-sync
description: Pull edits the family made in a recipe's Google Doc back into the app. Use when someone says "doc updated, update the app", "I changed the doc", or sends a Google Doc link to a recipe that already exists in the library.
---

# Sync a Google Doc back into the recipe file

The family prints and cooks from the Google Docs and edits them as they go. The recipe file in the repo is the source of truth for the site, so edits have to flow back.

1. **Find the recipe.** Take the doc id from the link (`/document/d/<id>/`) and grep: `grep -l "drive_doc_id: <id>" recipes/*.md`. Also check `docs/DOC_MAP.md`. If nothing matches, search Drive for the doc title and ask which recipe it belongs to; if it is a brand-new recipe, use `recipe-intake` instead.
2. **Read the doc** with the Drive tools and read the current recipe file side by side.
3. **Apply the differences** to the recipe file: title, reference, serves, times, the ingredient table (measure / item / prep / group, keeping `qty`/`unit` in sync with any changed measure), and the directions. Preserve the house conventions (units, canonical item names, mise groups, technique temperatures). Keep `drive_doc_id` as is. Note what changed in one line each; if an edit looks like an accident (a deleted ingredient that the directions still use), ask.
4. **Recompute nutrition** (`python3 scripts/nutrition.py --write <slug>`, then `nutrition_check.py`); source any new food per the `nutrition` skill.
5. `python3 scripts/validate.py && python3 scripts/build.py`, commit with a message like "Sync Chili from Google Doc", push.
6. **Do not recreate the doc.** The person is working in it. Tell them the site is updated and that the doc's nutrition box is stale if the totals changed; offer to refresh the doc (which creates a new doc and a new link, logged in `docs/DRIVE_TRASH_LOG.md`) only if they want it.
