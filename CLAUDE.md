# Chef

Household recipe library, nutrition calculator, and shopping-list planner.
Everything lives in this repo. A static site is built from it and deployed to GitHub Pages.

<!-- household:start -->
## This household

- **Household:** the Thomas family. They call this project, and Claude when working in it, **ChefBot** (also "Chef" or "the Chef bot"). All three mean this repo and its site.
- **Repo:** `ThomasFamilyBot/chef` · **Site:** https://thomasfamilybot.github.io/Chef/
- **Google account that owns everything:** ahinthomas@gmail.com (see "Google identities" below).
- Every other household-specific value (list names, Drive folder ids, Gmail label ids, the lists web-app URL, house taste) is in `data/site.yaml`. Read it at the start of any task that touches Google, the site link, or shopping lists.
- **Kitchen equipment** (ice cream maker size and the like) is under `equipment` in `data/site.yaml`. Read it before scaling a recipe or writing batch / churn instructions.
<!-- household:end -->

## Layout

- `recipes/*.md` — one recipe per file. YAML front matter (structured) + Markdown directions. **This is the source of truth.** See `docs/RECIPE_FORMAT.md`.
- `data/canonical_ingredients.csv` — the canonical nutrition table (per 1 oz by weight). Never overwrite a row silently.
- `data/store_sections.yaml` — ordered grocery-store sections + keyword fallbacks for ingredients that don't declare a section.
- `data/shopping_templates/*.yaml` — recurring lists (e.g. house staples) that can be added to any shopping list.
- `data/items.yaml` + `site/static/items/` — item details cards (photo, notes) shown when an item is tapped; see "item photos" below.
- `data/techniques.yaml` — technique glossary (sweat, sauté, medium-high, simmer, fry…) with target temperatures; auto-appended to recipe pages and Docs.
- `docs/DOC_MAP.md` — generated map of recipe ↔ Google Doc ↔ site page.
- `data/menus.yaml` — menus / run of show (library slugs + not-yet-written dishes). `data/pairings.yaml` — "pairs well with" links with reasons.
- `scripts/validate.py` — checks every recipe against the format. Run it before committing.
- `scripts/build.py` — builds the site into `dist/`.
- `scripts/export_gdoc_html.py` — renders a recipe as HTML in the family's Google Doc template layout, for writing back to Drive.
- `scripts/nutrition.py` — computes a recipe's nutrition from the canonical table (`--check`, `--write <slug>`, `--all`).
- `scripts/nutrition_check.py` — sanity checks on the table and on computed recipes (ranges, Atwater consistency, portion weights, per-serving plausibility). Run after any nutrition change.
- `scripts/usda_fetch.sh` + `scripts/usda_lookup.py` — local copy of USDA SR Legacy; `search`, `show`, and `row` (emits a ready canonical CSV row with FDC id, URL and portion weights).
- `scripts/set_override.py` — set a per-ingredient nutrition override in a recipe (exclude / fraction / oz) with a note.
- `site/` — templates and static assets for the site.
- `data/site.yaml` — site and household settings: names, repo, site address, list names, Google folder and label ids.
- `SETUP.md` + `scripts/setup_check.py` — first-time setup of a new copy (only when `setup_done` is false in `data/site.yaml`).
- `.claude/skills/` — the procedures Claude follows: `recipe-intake`, `nutrition`, `drive-export`, `menu-planning`, `recipe-suggestions`, `drive-sync`, `inbox-processing`.

## When asked to add / convert a recipe

Follow `.claude/skills/recipe-intake/SKILL.md` exactly. It covers the questions to ask the uploader
(reference text, hyperlink), unit rules, abbreviations, ingredient naming, mise groupings, technique temperatures, store sections, and the file format.
**Adding a recipe is a four-part job, every time, without being asked:** (1) the recipe file, (2) whole-recipe nutrition: calories, protein g, fat g only
(`nutrition` skill; new foods go into the canonical table with a source), (3) a Google Doc copy (`drive-export` skill), (4) validate, build, commit, push.
Report all four in the final message.
**Once the deploy has finished successfully, give the person the recipe's site link** (`<site_url>r/<slug>.html`), checked live (HTTP 200). This applies to every new recipe, including ones added from the inbox.

## When the family edits a Google Doc and says "doc updated, update the app"

Follow `.claude/skills/drive-sync/SKILL.md`: find the recipe by the doc id, read the doc, update the recipe file, recompute nutrition, rebuild.

## When asked for nutrition

Follow `.claude/skills/nutrition/SKILL.md`. Whole recipe only; calories, protein g, fat g only. Canonical table first, USDA second, every assumption written down.

## When asked what goes with a dish, for a menu, or for new recipe ideas

Follow `.claude/skills/menu-planning/SKILL.md` or `.claude/skills/recipe-suggestions/SKILL.md`.

## When asked to process the recipe inbox (friends' email / Drive submissions)

Follow `.claude/skills/inbox-processing/SKILL.md`. A scheduled Routine runs it; it can also be run on request.

## When someone sends a photo of a shopping item ("item photos")

Tapping an item with a 📷 (photo) or ⓘ (notes only) on the Shopping List or a recipe page opens a details card: photo, notes, which lists and recipes use it. Data lives in `data/items.yaml`; photos in `site/static/items/`.
- Chat photos are saved under `~/.claude/uploads/<session>/`. Look at the photo first: the site is public, so skip anything personal (faces, addresses, receipts) and ask.
- `python3 scripts/add_item_photo.py --item "<name exactly as on the list>" --photo <file> [--alias "<recipe name>"] [--notes "brand, size, aisle"] [--rotate 90]`. It resizes to 1000 px and strips location/camera data. Never copy a photo into `site/static/items/` by hand.
- Use `--alias` so a template name like "Dried Mango (organic)" and the recipe name "Dried Mango" open the same card. Read the converted photo back to check it is upright.
- Then build, commit, push, wait for the deploy, and tell the person which item now has a card.

## When asked to put a recipe in Google Drive

Follow `.claude/skills/drive-export/SKILL.md`.

## Google identities

- The `google_account` in `data/site.yaml` owns everything in Google: the Drive folders, the Google Docs, the shared shopping-lists sheet and its Apps Script, and the Claude connectors. Any Google setup step is done signed in as this account.
- The public recipe-submission address (`submission_email` in `data/site.yaml`) is a forwarder only; it owns nothing.
- **Whenever you ask the household to do something in Google, say which account to be signed in as.**

## Always

- **Start every task with `git pull --rebase origin main`.** Several Claude sessions and people share this repo; a stale checkout makes comparisons and exports wrong (e.g. a Docs refresh that "matches" an old version).
- Run `python3 scripts/validate.py` after editing any recipe; fix what it reports.
- Run `python3 scripts/build.py` to confirm the site builds.
- Commit with a clear message and push to `main`. The site redeploys automatically; wait for `gh run list --limit 1` to show the run completed before sending anyone a site link (Pages takes a minute or two).
- Units: `g`, `tsp`, `TBLS`, `cup`, `oz` (weight), `fl oz` (volume), `lb`. Nothing else without asking.
