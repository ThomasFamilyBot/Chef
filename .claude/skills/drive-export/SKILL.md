---
name: drive-export
description: Write a recipe from recipes/<slug>.md back to Google Drive as a Google Doc in the family's print layout (title, reference link, serves, times, 4-column ingredient table, directions, nutrition). Use when asked to put a recipe in Drive, make a Google Doc, or sync converted recipes.
---

# Export a recipe to Google Drive

1. Render HTML: `python3 scripts/export_gdoc_html.py recipes/<slug>.md` prints HTML to stdout (or `--out file.html`).
2. Find the destination folder. Default is **Converted Recipies** (`1r7iPvPCANIL6WebFZSeCiCyS0Kr57bdN`), pasta sauces go to its sub-folder **Converted Pasta Sauce** (`1XPi5GTWUkroQ27qPC6YihXKenPeX-M3C`). The family may reorganise folders; search Drive for the folder by name if the id no longer resolves, and ask if there are several candidates.
3. If the recipe's front matter already has a `drive_doc_id`, the Drive `update_file` tool cannot replace content, so: create the new doc first (step 4), then move the old one to trash with `mcp__Google_Drive__trash_file`, then write the new id back. Never trash before the new doc exists. Append a row to `docs/DRIVE_TRASH_LOG.md` (date, recipe, trashed id, new id, why) for every trash, so the family has an after-the-fact record.
4. Otherwise create the doc with the Drive `create_file` tool: `contentMimeType: text/html`, `textContent: <the html>`, `parentId: <folder>`, `title: <recipe title>`. Drive converts HTML to a Google Doc, keeping the table and links.
5. Write the returned document id into the recipe's `drive_doc_id`, validate, commit, push.

Keep the doc layout identical to `*Recipe Template`: bold title, Reference line (hyperlinked when `reference.url` exists), Serves, `Prep: X | Cook: Y | Rest: Z | Total: W` (minutes), the 4-column table with bold header row, Directions, then "Estimate Nutrition of Whole, Finished Recipe" with the nutrition table when computed.
