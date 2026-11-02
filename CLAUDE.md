# Chef

Household recipe library, nutrition calculator, and shopping-list planner for the Thomas family.
Everything lives in this repo. A static site is built from it and deployed to GitHub Pages.

## Layout

- `recipes/*.md` — one recipe per file. YAML front matter (structured) + Markdown directions. **This is the source of truth.** See `docs/RECIPE_FORMAT.md`.
- `data/canonical_ingredients.csv` — the canonical nutrition table (per 1 oz by weight). Never overwrite a row silently.
- `data/store_sections.yaml` — ordered grocery-store sections + keyword fallbacks for ingredients that don't declare a section.
- `data/shopping_templates/*.yaml` — recurring lists (e.g. house staples) that can be added to any shopping list.
- `scripts/validate.py` — checks every recipe against the format. Run it before committing.
- `scripts/build.py` — builds the site into `dist/`.
- `scripts/export_gdoc_html.py` — renders a recipe as HTML in the family's Google Doc template layout, for writing back to Drive.
- `site/` — templates and static assets for the site.
- `.claude/skills/` — the procedures Claude follows: `recipe-intake`, `nutrition`, `drive-export`.

## When asked to add / convert a recipe

Follow `.claude/skills/recipe-intake/SKILL.md` exactly. It covers the questions to ask the uploader
(reference text, hyperlink), unit rules, abbreviations, ingredient naming, store sections, and the file format.

## When asked for nutrition

Follow `.claude/skills/nutrition/SKILL.md`. Canonical table first, USDA second, every assumption written down.

## When asked to put a recipe in Google Drive

Follow `.claude/skills/drive-export/SKILL.md`.

## Always

- Run `python3 scripts/validate.py` after editing any recipe; fix what it reports.
- Run `python3 scripts/build.py` to confirm the site builds.
- Commit with a clear message and push to `main`. The site redeploys automatically.
- Units: `g`, `tsp`, `TBLS`, `cup`, `oz` (weight), `fl oz` (volume), `lb`. Nothing else without asking.
