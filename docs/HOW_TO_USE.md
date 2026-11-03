# How to use Chef (for the family)

## The site

https://thomasfamilybot.github.io/Chef/

- **Recipes**: search by title, ingredient, or any word in the directions. Click a tag to filter. Each recipe page has a **Print** button (the ingredient table stays on one page) and a **+ Shopping list** button.
- **Filters** on the Recipes page: total time, course, protein, and a "what I have" box (comma-separated ingredients) that ranks recipes by how many you already have.
- **Menus**: dinners we've cooked, with the run of show. One tap adds every library recipe on a menu to the shopping list. Recipe pages show "Pairs well with" and the menus they're on.
- **Shopping List**: tick the recipes you're cooking (and a multiplier, e.g. ×2 for a crowd) plus any templates such as *House Staples*. Same items from different recipes are added together; the list is grouped by store section. Check items off as you shop. Checkmarks are saved on *your* phone.
- **Share a list**: press **Copy share link** and text it. Whoever opens it sees the same list and can check things off on their own phone.
- **Nutrition**: whole-recipe calories, protein and fat on every recipe page and Google Doc, with the line items and assumptions behind them, plus the canonical ingredient table.

## Adding or changing a recipe (anyone with the Claude subscription)

Open a Claude session that has the `ThomasFamilyBot/Chef` repo attached and talk to it. Three ways to do that:

1. **Claude Code on the web** (claude.ai/code): start a session, pick the Chef repo. Paste a URL, drop in a photo/PDF, or paste text. This is the most capable path and is what the retrofit used.
2. **Claude desktop app / terminal** with the repo cloned locally and `claude` started inside it.
3. **claude.ai chat with the GitHub connector**: works for URL and text sources; the repo's `CLAUDE.md` and skills won't auto-load there, so start a Project and paste `docs/claude-project-instructions.md` into the Project instructions.

What to say:

- "Add this recipe: <url>. Reference it as 'Serious Eats' and link it."
- "Here's a photo of a cookbook page. Reference: 'Six Seasons p. 212', no link."
- "Convert this Google Doc: <link>."
- "Calculate nutrition for Chili."
- "Put Chili in Drive." (writes the Google Doc copy into *Converted Recipies*)
- "Add 'Paper towels' to the House Staples template."
- "Make a new shopping template called 'Taco night'."
- "What goes with the Zuni chicken?" / "Plan a dinner for 8 on Saturday, grill, not too much work."
- "What should we add to the library next?"

Claude will ask the reference/hyperlink questions if the source doesn't answer them, then write the file, validate it, build the site, commit and push. The site rebuilds in about a minute.

## Where things live

| What | Where |
|---|---|
| Recipes | `recipes/*.md` |
| Canonical nutrition table | `data/canonical_ingredients.csv` |
| Store sections and keyword fallbacks | `data/store_sections.yaml` |
| Shopping templates | `data/shopping_templates/*.yaml` |
| Rules Claude follows | `.claude/skills/*/SKILL.md`, `CLAUDE.md` |
| The site's HTML/CSS/JS | `site/` |

Every change is a git commit, so nothing is ever lost: the GitHub history is the backup.

## Editing by hand

You can edit any recipe file directly on GitHub (pencil icon). The format is documented in `docs/RECIPE_FORMAT.md`. A GitHub Action validates and rebuilds on every commit; if validation fails, the Actions tab shows what's wrong and the site keeps the last good version.

## Friends sending recipes

Give them two things:

- **Email**: send a recipe URL or the typed-out recipe to the submission address in `data/site.yaml` (a dedicated Gmail that forwards to the family inbox; Claude finds it by the address). The public **Send a recipe** page on the site explains this to friends.
- **Photos**: drop cookbook photos or scans into the shared Drive folder **Chef Inbox** (https://drive.google.com/drive/folders/1yDhgpXc_rXGO5I7U_QmIm8QRqL62JPo9). Name the file with the recipe and your name, e.g. `Grandma's pierogi - Sam.jpg`.

A Routine checks both on a schedule, converts each submission into a recipe with nutrition and a Google Doc, and emails the sender the links. Processed emails get the Gmail label `Chef/Done`; processed files move to `Chef Inbox/Processed`. To run it on demand, tell Claude "process the recipe inbox".
