# Chef

The Thomas family recipe library, nutrition calculator and shopping-list planner.

- **Site:** https://thomasfamilybot.github.io/chef/ (rebuilds automatically on every push to `main`)
- **Recipes:** `recipes/*.md` (one file per recipe, see `docs/RECIPE_FORMAT.md`)
- **Nutrition table:** `data/canonical_ingredients.csv`
- **Shopping templates:** `data/shopping_templates/`

## Adding a recipe

Open a Claude session with this repo attached (Claude Code on the web, the desktop app, or claude.ai with the GitHub connector) and say, for example:

> Add this recipe: https://… — reference it as "Serious Eats", link it.

or paste text, or attach a photo of a cookbook page. Claude follows `.claude/skills/recipe-intake/SKILL.md`, asks what the reference line should say and whether to hyperlink, writes the file, validates, builds, commits and pushes. The site updates within a couple of minutes.

Then, if you want a printed-doc copy in Drive: "Put it in Drive." (`.claude/skills/drive-export/SKILL.md`)

And for nutrition: "Calculate nutrition for Bo Ssam." (`.claude/skills/nutrition/SKILL.md`)

## Local build

```bash
pip install pyyaml markdown jinja2
python3 scripts/validate.py
python3 scripts/build.py      # -> dist/
python3 -m http.server --directory dist 8000
```
