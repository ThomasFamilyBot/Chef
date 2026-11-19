---
name: drive-export
description: Write a recipe from recipes/<slug>.md back to Google Drive as a Google Doc in the family's print layout (title, reference link, serves, times, 4-column ingredient table, directions, nutrition). Use when asked to put a recipe in Drive, make a Google Doc, or sync converted recipes.
---

# Export a recipe to Google Drive

0. `git pull --rebase origin main` first. The Docs must be rendered from the current `main`, not from whatever this session checked out earlier. When asked to "refresh all Google Docs", pull, then re-render every recipe and compare against the Doc's current content; a Doc is stale if its ingredient table, directions, technique box or nutrition differ in any way.
1. Render HTML: `python3 scripts/export_gdoc_html.py recipes/<slug>.md` prints HTML to stdout (or `--out file.html`).
2. Find the destination folder in `data/site.yaml`: the default is `google.docs_folder` (name and id); `google.docs_subfolders` lists sub-folders and what goes in each (`use_for`). If no folder is set there yet, ask which Drive folder to use (or offer to create one called "Recipes"), then record its name and id in `data/site.yaml`. The household may reorganise folders; search Drive for the folder by name if the id no longer resolves, and ask if there are several candidates.
3. If the recipe's front matter already has a `drive_doc_id`, the Drive `update_file` tool cannot replace content, so: create the new doc first (step 4), then move the old one to trash with `mcp__Google_Drive__trash_file`, then write the new id back. Never trash before the new doc exists. Append a row to `docs/DRIVE_TRASH_LOG.md` (date, recipe, trashed id, new id, why) for every trash, so the family has an after-the-fact record.
4. Otherwise create the doc with the Drive `create_file` tool: `contentMimeType: text/html`, `textContent: <the html>`, `parentId: <folder>`, `title: <recipe title>`. Drive converts HTML to a Google Doc, keeping the table and links.
5. Write the returned document id into the recipe's `drive_doc_id`, validate, commit, push.

Keep the doc layout exactly as the script renders it (the household's print layout): bold title, Reference line (hyperlinked when `reference.url` exists), Serves, `Prep: X | Cook: Y | Rest: Z | Total: W` (minutes), the 4-column table with bold header row, Directions, then "Estimate Nutrition of Whole, Finished Recipe" with the nutrition table when computed. Fractions come out as superscript/subscript (`1/2` with a raised 1 and lowered 2); that is intended.
