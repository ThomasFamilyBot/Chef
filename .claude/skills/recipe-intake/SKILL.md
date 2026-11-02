---
name: recipe-intake
description: Convert a recipe from any source (URL, Google Doc, photo/PDF/HEIC, pasted text, legacy doc) into the family recipe format in recipes/<slug>.md, then validate, build, commit and push. Use whenever someone asks to add, import, convert, translate, or retrofit a recipe.
---

# Recipe intake

## 1. Get the source

- **URL**: fetch the page. If it is paywalled or blocked (NYT Cooking often is), ask the person to paste the text or send a screenshot.
- **Google Doc / Drive file**: read it with the Google Drive tools. Read the whole thing, including tables.
- **Image / PDF / HEIC**: read it visually. If a quantity or word is illegible, ask rather than guess.
- **Legacy family doc**: it is already close to the format. Preserve the family's own wording, notes and jokes. Do not "improve" the cooking.

## 2. Ask the uploader (one short message, all questions at once)

Only ask what the source does not answer:

1. **Reference**: "What should the Reference line say?" Suggest a default (site name + recipe title, or "Cookbook title p. N", or "Hand-written from <friend>").
2. **Hyperlink**: "Link it to <url>?" Default: yes for web sources, none for cookbooks/hand-written unless they give one.
3. **Serves / servings** if the source doesn't say.
4. **Times** if missing and not inferable from the directions. It is fine to estimate from the directions and say so.

If the person already answered these in their request, don't ask again. If they say "just do it", use the defaults and note them in the commit message.

## 3. Units (house rules)

Abbreviations, exactly these: `g`, `tsp`, `TBLS`, `cup`, `oz`, `fl oz`, `lb`. Also plain counts (`2 Eggs`, `3 cloves Garlic`).

- `oz` alone means **weight**. Liquid volumes are `fl oz`. Never write a bare `oz` for a liquid.
- Keep cups. Keep tsp / TBLS. Grams are fine where precision matters (baking, brines, cures).
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
- `group` is the mise grouping: `1 -> Ginger Scallion Sauce`. Leave empty when there is one component.
- `qty`/`unit` must reflect the measure so shopping lists add correctly. Count-type things (`1 Baguette`, `3 heads Bibb Lettuce`) use `each` or a descriptive counter.
- `section`: set it when the keyword fallback in `data/store_sections.yaml` would get it wrong. Valid sections are listed in that file.
- `shop: false` for Water, and for "for serving" extras the family said not to shop.

## 5. Directions

Markdown. Short bold component headings (`**Day 1**`, `**Make the sauce**`) are good, but an H2/H3 structure is not required. Bullets for steps. Keep temperatures, times and doneness cues. Refer to mise groups by name ("Combine everything from `1 -> Ginger Scallion Sauce`").

## 6. Times

`prep`, `cook`, `rest`, `total` in whole minutes. `rest` covers brining, marinating, resting, cooling. `total` is wall-clock from start to serving (not the sum, when steps overlap or span days). Use `null` for unknown, never 0 as a placeholder.

## 7. Write the file, validate, build, commit

```bash
python3 scripts/validate.py recipes/<slug>.md
python3 scripts/build.py
git add -A && git commit -m "Add <Title>" && git push -u origin main
```

Then tell the person the recipe is live at `https://thomasfamilybot.github.io/chef/r/<slug>.html` and, if they want a Google Doc copy, follow the `drive-export` skill.

## 8. Nutrition

Do **not** calculate nutrition during intake unless asked. When asked, follow the `nutrition` skill.

## Example front matter

See `recipes/bo-ssam.md` for the reference example.

## Canonical item names (use these spellings so shopping lists merge)

Kosher Salt · Black Pepper (ground) · Black Peppercorns · Flaky Sea Salt · Olive Oil · Extra-Virgin Olive Oil · Neutral Oil (grapeseed/canola) · Unsalted Butter · Eggs · Egg Yolks · Whole Milk · Heavy Cream · Granulated Sugar · Brown Sugar · All-Purpose Flour · Garlic · Yellow Onion · Red Onion · Shallot · Scallions · Ginger · Lemon · Lime · Parmesan · Pecorino Romano · Crushed Tomatoes · Tomato Paste · Chicken Stock · Beef Stock · Dry White Wine · Dry Red Wine · Soy Sauce · Rice Vinegar · Red Wine Vinegar · Balsamic Vinegar · Dijon Mustard · Bay Leaves · Fresh Thyme · Fresh Rosemary · Fresh Sage · Flat-Leaf Parsley · Cilantro · Basil · Jalapeño · Red Pepper Flakes · Smoked Paprika · Ground Cumin · Cayenne · Chili Powder · Garlic Powder · Onion Powder · Dried Oregano

Put the size/variety in the name only when it matters for shopping: `Crushed Tomatoes, 28 oz can`, `Chicken Thighs, boneless skinless`, `Pork Butt, bone-in`.
