---
name: drive-export
description: Write a recipe from recipes/<slug>.md back to Google Drive as a Google Doc in the family's print layout (title, reference link, serves, times, 4-column ingredient table, directions, nutrition). Use when asked to put a recipe in Drive, make a Google Doc, or sync converted recipes.
---

# Export a recipe to Google Drive

0. `git pull --rebase origin main` first. The Docs must be rendered from the current `main`, not from whatever this session checked out earlier. When asked to "refresh all Google Docs", pull, then re-render every recipe and compare against the Doc's current content; a Doc is stale if its ingredient table, directions, technique box or nutrition differ in any way.
1. **Pick the route. Take the first one that applies.** Routes 1 and 2 keep the Doc and its link; a recipe's Doc is only ever replaced by route 4.

   | # | When | What |
   |---|---|---|
   | 1 | `docs_api` is set in `data/site.yaml` | `python3 scripts/push_docs.py <slug>` (or `--stale` for everything that changed). Rewrites the Doc in place, makes one for a recipe that has none, and writes `drive_doc_id`. No recipe text passes through the session. |
   | 2 | No `docs_api`, the Doc exists, the change is small | Edit in place with the Google Docs edit tool (below). |
   | 3 | No `docs_api`, the recipe has no Doc | Create one with the Drive `create_file` tool (below). |
   | 4 | No `docs_api`, the Doc exists, the change is too big for route 2 | Replace it: create the new Doc, then trash the old one (below). The link changes. |

2. **Route 1.** Run the command, read its last lines, and commit `docs/DOC_SYNC.json` (plus the recipe file if it gained a `drive_doc_id`). "skipped ... edited by hand" means a person changed that Doc since the last push: bring their edit into the recipe with the `drive-sync` skill first, and only then push; `--force` overwrites their edit. "FAILED" means look at that Doc. Setup, safety and behaviour are in `docs/DOCS_API.md`. If `docs_api` is empty and more than about ten Docs need work, offer the five-minute setup in that file before doing anything else.

3. **Route 2, in place with the Docs edit tool.** Tested 2026-11-28: it works, keeps the fraction formatting, and the result reads the same as a fresh export.
   - One line of text that occurs once in the Doc: a single `replaceAllText` request. No need to read the Doc first.
   - The ingredient table (groupings, rows that moved): read the Doc with the Docs read tool (the result is saved to a file, not shown), run `python3 scripts/gdoc_table_requests.py <saved-json> <slug> /tmp/reqs.json`, send those requests, read the Doc again and run the script again. It must report 0 cells differ.
   - This costs 5 to 20 KB of requests per Doc through the session. Fine for a handful, never for a library-wide change.

4. **Route 3, a new Doc.** Render with `python3 scripts/export_gdoc_html.py recipes/<slug>.md`. Find the destination folder in `data/site.yaml`: the default is `google.docs_folder` (name and id); `google.docs_subfolders` lists sub-folders and what goes in each (`use_for`). If no folder is set there yet, ask which Drive folder to use (or offer to create one called "Recipes"), then record its name and id in `data/site.yaml`. Create the Doc with the Drive `create_file` tool: `contentMimeType: text/html`, `textContent: <the html>`, `parentId: <folder>`, `title: <recipe title>`. Write the returned id into the recipe's `drive_doc_id`, validate, commit, push.

5. **Route 4, replace.** Create the new Doc as in route 3 first, then move the old one to trash with the Drive `trash_file` tool (check it was not edited by hand: its modified time should be within a minute of its created time), then write the new id back. Never trash before the new Doc exists. Append a row to `docs/DRIVE_TRASH_LOG.md` (date, recipe, trashed id, new id, why) for every trash. Tell the person the link changed. Ask before replacing more than a few.

Keep the doc layout exactly as the script renders it (the household's print layout): bold title, Reference line (hyperlinked when `reference.url` exists), Serves, `Prep: X | Cook: Y | Rest: Z | Total: W` (minutes), the 4-column table with bold header row, Directions, then "Estimate Nutrition of Whole, Finished Recipe" with the nutrition table when computed. Fractions come out as superscript/subscript (`1/2` with a raised 1 and lowered 2); that is intended.
