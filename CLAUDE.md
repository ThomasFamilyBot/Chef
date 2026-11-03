# Chef

Household recipe library, nutrition calculator, and shopping-list planner for the Thomas family.
Everything lives in this repo. A static site is built from it and deployed to GitHub Pages.

## Layout

- `recipes/*.md` — one recipe per file. YAML front matter (structured) + Markdown directions. **This is the source of truth.** See `docs/RECIPE_FORMAT.md`.
- `data/canonical_ingredients.csv` — the canonical nutrition table (per 1 oz by weight). Never overwrite a row silently.
- `data/store_sections.yaml` — ordered grocery-store sections + keyword fallbacks for ingredients that don't declare a section.
- `data/shopping_templates/*.yaml` — recurring lists (e.g. house staples) that can be added to any shopping list.
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
- `.claude/skills/` — the procedures Claude follows: `recipe-intake`, `nutrition`, `drive-export`, `menu-planning`, `recipe-suggestions`, `drive-sync`.

## When asked to add / convert a recipe

Follow `.claude/skills/recipe-intake/SKILL.md` exactly. It covers the questions to ask the uploader
(reference text, hyperlink), unit rules, abbreviations, ingredient naming, mise groupings, technique temperatures, store sections, and the file format.
**Adding a recipe is a four-part job, every time, without being asked:** (1) the recipe file, (2) whole-recipe nutrition: calories, protein g, fat g only
(`nutrition` skill; new foods go into the canonical table with a source), (3) a Google Doc copy (`drive-export` skill), (4) validate, build, commit, push.
Report all four in the final message.

## When the family edits a Google Doc and says "doc updated, update the app"

Follow `.claude/skills/drive-sync/SKILL.md`: find the recipe by the doc id, read the doc, update the recipe file, recompute nutrition, rebuild.

## When asked for nutrition

Follow `.claude/skills/nutrition/SKILL.md`. Whole recipe only; calories, protein g, fat g only. Canonical table first, USDA second, every assumption written down.

## When asked what goes with a dish, for a menu, or for new recipe ideas

Follow `.claude/skills/menu-planning/SKILL.md` or `.claude/skills/recipe-suggestions/SKILL.md`.

## When asked to put a recipe in Google Drive

Follow `.claude/skills/drive-export/SKILL.md`.

## Always

- **Start every task with `git pull --rebase origin main`.** Several Claude sessions and people share this repo; a stale checkout makes comparisons and exports wrong (e.g. a Docs refresh that "matches" an old version).
- Run `python3 scripts/validate.py` after editing any recipe; fix what it reports.
- Run `python3 scripts/build.py` to confirm the site builds.
- Commit with a clear message and push to `main`. The site redeploys automatically; wait for `gh run list --limit 1` to show the run completed before sending anyone a site link (Pages takes a minute or two).
- Units: `g`, `tsp`, `TBLS`, `cup`, `oz` (weight), `fl oz` (volume), `lb`. Nothing else without asking.
