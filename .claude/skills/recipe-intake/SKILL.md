---
name: recipe-intake
description: Convert a recipe from any source (URL, Google Doc, photo/PDF/HEIC, pasted text, legacy doc) into the family recipe format in recipes/<slug>.md, then validate, build, commit and push. Use whenever someone asks to add, import, convert, translate, or retrofit a recipe.
---

# Recipe intake

## 0. Pull first

`git pull --rebase origin main` before anything else; other sessions may have changed the rules, the canonical table or the recipes.

## 1. Get the source

- **URL**: fetch the page. If it is paywalled or blocked (NYT Cooking often is), ask the person to paste the text or send a screenshot.
  **URL rule:** the recipe `title` is the recipe's name as the page gives it (not the site name, not a title of your own), and `reference.url` is exactly the URL that was submitted. The site hyperlinks the title and the Reference line to that URL automatically. Don't ask whether to hyperlink a URL submission; do ask only if the page title is unusable (a generic page name, or the person gave their own name for it).
- **Google Doc / Drive file**: read it with the Google Drive tools. Read the whole thing, including tables.
- **Image / PDF / HEIC**: read it visually. If a quantity or word is illegible, ask rather than guess.
- **Legacy family doc**: it is already close to the format. Preserve the family's own wording, notes and jokes. Do not "improve" the cooking.

## 2. Ask the uploader (one short message, all questions at once)

Only ask what the source does not answer:

1. **Reference**: "What should the Reference line say?" For a URL, default to the site or author name (e.g. "Food52", "Serious Eats, Kenji López-Alt") and only ask if the person seems to want something else. Otherwise suggest "Cookbook title p. N" or "Hand-written from <friend>".
2. **Hyperlink**: for a URL submission it is always the submitted URL; no question. For cookbooks and hand-written recipes, none unless they give one.
3. **Serves / servings** if the source doesn't say.
4. **Times** if missing and not inferable from the directions. It is fine to estimate from the directions and say so.

If the person already answered these in their request, don't ask again. If they say "just do it", use the defaults and note them in the commit message.

## 3. Units (house rules)

Abbreviations, exactly these: `g`, `tsp`, `TBLS`, `cup`, `oz`, `fl oz`, `lb`. Also plain counts (`2 Eggs`, `3 cloves Garlic`).

- `oz` alone means **weight**. Liquid volumes are `fl oz`. Never write a bare `oz` for a liquid.
- Keep cups. Keep tsp / TBLS. Weight policy: things you buy by weight (meat, produce, cheese) stay in `oz` / `lb` because that's how US labels read; use `g` (or `kg` above 1000 g) wherever precision matters: baking, brines, cures, dough, salt by percentage. When a recipe gives a large volume of water for a brine, add the weight in parentheses and say it's weight: `2 gallons (32 cups; 7.57 kg / 16.7 lb by weight)`.
- Roll up to the next major unit when a count is large: `4 tsp` → `1 TBLS + 1 tsp`; `4 TBLS` → `1/4 cup`; `16 oz` → `1 lb`; `24 oz` → `1 1/2 lb`. Don't roll up below the threshold (`2 TBLS` stays `2 TBLS`).
- Metric sources: convert ml to tsp/TBLS/cup/fl oz, grams of meat/produce to oz or lb (round to a sensible 1/4 oz or 1/4 lb). Keep grams for baking ingredients that were given in grams.
- Proteins are by **weight** (oz/lb), raw, boneless/skinless unless the recipe says otherwise.
- A recipe must be internally consistent: don't mix `g` and `oz` for the same kind of ingredient within one recipe.
- Fractions print as `1/2`, `1/4`, `3/4`, `1/3`, `2/3`, `1 1/2`. No unicode fraction glyphs.
- If a unit is unclear or a new abbreviation seems needed, ask.

## 4. Ingredient table

Columns: Measure | Ingredient | Prep | Mise Grouping. Keep it to one printed page: merge trivial lines, keep prep notes short. Order ingredients in the order they are used, or grouped by component when the recipe has sub-recipes (sauce, rub, dough).

- `item` is the **shopping name**: Title Case, no prep words, no quantity words. `Yellow Onion` not `chopped yellow onion`. Match names already used in other recipes (grep `recipes/` for the word first) so the shopping list merges them.
- `prep` holds the knife work and notes: `Peeled & minced`, `Removed from casing`.
- `group` is the mise grouping and is **always filled in**. Groups are bowls on the counter: numbered **1..N consecutively in order of first use, no gaps**, each named after the direction step or component it feeds: `1 -> Batter`, `2 -> Honey butter`. A step that adds no new ingredients (baking, resting) gets no bowl. An ingredient used in two steps gets `2 -> Stew (then 4 -> Finish)`. Sub-recipes (sauce, rub, dough) are their own bowls. `scripts/renumber_groups.py` fixes numbering; the validator rejects gaps and dangling references.
- `qty`/`unit` must reflect the measure so shopping lists add correctly. Count-type things (`1 Baguette`, `3 heads Bibb Lettuce`) use `each` or a descriptive counter.
- `section`: set it when the keyword fallback in `data/store_sections.yaml` would get it wrong. Valid sections are listed in that file.
- `shop: false` for Water, and for "for serving" extras the family said not to shop.

## 5. Directions

Markdown. Bold step headings as paragraphs, **named, not numbered** (`**Sweat the onion**`, `**Make the sauce**`; multi-day recipes can use `**Day 1**` above them) and bullets inside each step. The bowl numbers live in the ingredient table; directions refer to bowls by their full label ("Combine everything from `1 -> Ginger Scallion Sauce`"), so the two never drift apart. Keep temperatures, times and doneness cues.

**Temperatures for techniques.** The family cooks with infrared and probe thermometers, so vague heat words get a number on first use: "over medium-high heat (pan surface 375-425°F)", "sweat (200-250°F, no color)", "a bare simmer (180-190°F)", "fry at 325°F", "braise at 300°F until 200°F internal". Use `data/techniques.yaml` for the house targets; the site and the Google Doc also append a "Technique temperatures" box automatically for any glossary term that appears. When you can fetch a reputable technique page (Serious Eats, ThermoWorks, King Arthur, AmazingRibs, USDA FSIS), link it in the direction text; if you can't fetch, don't invent a URL.

## 6. Times

`prep`, `cook`, `rest`, `total` in whole minutes. `rest` covers brining, marinating, resting, cooling. `total` is wall-clock from start to serving (not the sum, when steps overlap or span days). Use `null` for unknown, never 0 as a placeholder.

## 7. Write the file, then nutrition, then the Google Doc (all three, every time)

```bash
python3 scripts/validate.py recipes/<slug>.md
```

**Nutrition (whole recipe), before committing.** Follow the `nutrition` skill:

```bash
python3 scripts/nutrition.py --check <slug>          # lists foods not in the canonical table
bash scripts/usda_fetch.sh                            # once per session; local USDA copy
python3 scripts/usda_lookup.py search "..."           # find the record, then `row ...` to append it
python3 scripts/nutrition.py --write <slug>
python3 scripts/nutrition_check.py
```

If a food is ambiguous in a way that materially changes the numbers (bone-in vs boneless, raw vs cooked, a branded item with no USDA record, how much of a brine or frying oil is consumed), do not guess: present the person 2-3 options with the source for each (USDA record names and ids, manufacturer label) and the resulting calories, ask which to use, then add the chosen row to `data/canonical_ingredients.csv` with its source so the question is never asked again. Small assumptions: proceed, state them in the line note.

**Google Doc, always.** Follow the `drive-export` skill (render HTML, create the doc in the right folder, write `drive_doc_id` back). The build regenerates `docs/DOC_MAP.md` from it.

```bash
python3 scripts/build.py
git add -A && git commit -m "Add <Title>" && git push -u origin main
```

**Wait for the deploy before handing over the site link.** GitHub Pages publishes a minute or two after the push; a link sent earlier 404s. Run:

```bash
gh run list --repo ThomasFamilyBot/chef --limit 1          # until status is "completed success"
```

(or `gh run watch --repo ThomasFamilyBot/chef` if available). If it fails, read the log with `gh run view <id> --log-failed` and fix before reporting.

Then tell the person: the site link `https://thomasfamilybot.github.io/Chef/r/<slug>.html`, the Google Doc link, the whole-recipe calories / protein / fat, and any assumptions or estimates in the nutrition lines.

## 8. If the person later edits the Google Doc

They will say "doc updated, update the app" with the doc link. Follow the `drive-sync` skill.

## Example front matter

See `recipes/bo-ssam.md` for the reference example.

## Canonical item names (use these spellings so shopping lists merge)

Kosher Salt · Black Pepper · Black Peppercorns · Flaky Sea Salt · Olive Oil · Extra-Virgin Olive Oil · Neutral Oil (prep: grapeseed, canola, vegetable) · Unsalted Butter · Eggs · Egg Yolks · Whole Milk · Heavy Cream · Granulated Sugar · Brown Sugar · All-Purpose Flour · Garlic · Yellow Onion · Red Onion · Shallot · Scallions · Ginger · Lemon · Lime · Parmesan · Pecorino Romano · Crushed Tomatoes · Tomato Paste · Chicken Stock · Beef Stock · Dry White Wine · Dry Red Wine · Soy Sauce · Rice Vinegar · Red Wine Vinegar · Balsamic Vinegar · Dijon Mustard · Bay Leaves · Fresh Thyme · Fresh Rosemary · Fresh Sage · Flat-Leaf Parsley · Cilantro · Basil · Jalapeño · Red Pepper Flakes · Smoked Paprika · Ground Cumin · Cayenne · Chili Powder · Garlic Powder · Onion Powder · Dried Oregano

Put the size/variety in the name only when it matters for shopping: `Crushed Tomatoes, 28 oz can`, `Chicken Thighs, boneless skinless`, `Pork Butt, bone-in`.
