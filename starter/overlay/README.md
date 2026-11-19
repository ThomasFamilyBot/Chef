# Chef

A household recipe library, nutrition calculator and shopping-list planner that you run by talking to Claude.
You send a recipe (a link, a photo of a cookbook page, pasted text); Claude rewrites it into one consistent
format, works out the nutrition, and publishes it to your own recipe website with a shopping list that
adds up ingredients across recipes.

**Brand-new copy?** Read [`GETTING_STARTED.md`](GETTING_STARTED.md). It assumes you have never used GitHub.
Once the copy is yours, open a Claude Code session on it and say **"Set me up."**

- **Site:** https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPO/ (rebuilds automatically on every change)
- **Household:** YOUR-HOUSEHOLD
- **Settings:** `data/site.yaml`
- **Recipes:** `recipes/*.md` (one file per recipe, see `docs/RECIPE_FORMAT.md`)
- **Nutrition table:** `data/canonical_ingredients.csv`
- **Shopping templates:** `data/shopping_templates/`
- **How to use it day to day:** `docs/HOW_TO_USE.md`

## Adding a recipe

Open a Claude session with this repository attached (Claude Code on the web at claude.ai/code, or the Claude phone app) and say, for example:

> Add this recipe: https://…

or paste text, or attach a photo of a cookbook page. Claude asks what the reference line should say if it
can't tell, writes the file, checks it, builds the site and publishes. The site updates within a couple of minutes.

## What's inside

| What | Where |
|---|---|
| The rules Claude follows | `CLAUDE.md`, `.claude/skills/*/SKILL.md` |
| First-time setup procedure (for Claude) | `SETUP.md` |
| Recipes | `recipes/*.md` |
| Site templates and scripts | `site/`, `scripts/` |

## Local build (optional, for the curious)

```bash
pip install pyyaml markdown jinja2
python3 scripts/validate.py
python3 scripts/build.py      # -> dist/
python3 -m http.server --directory dist 8000
```

## License

The code, site templates and Claude instructions are under the [MIT License](LICENSE). The sample recipes in
`recipes/` are adapted from the sources named on each one and are included only as examples; they are not
covered by that license. Nutrition values cite their own sources in `data/canonical_ingredients.csv`.
