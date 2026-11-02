---
name: nutrition
description: Calculate nutrition for a whole prepared recipe (and per serving) using the family's canonical ingredient table first, USDA FoodData Central second, with every assumption written into the recipe's nutrition block. Also used to add or update rows in data/canonical_ingredients.csv. Use whenever someone asks for calories, protein, macros, or nutrition.
---

# Nutrition (Personal Nutrition Assistant rules)

**House rule for recipes: report the WHOLE recipe only, and only three numbers: calories, grams of protein, grams of fat.** No per-serving figures, no carbohydrates, no efficiency on recipe pages. (The canonical ingredient table keeps carbs and efficiency per oz for sourcing and sanity checks; they are not shown on recipes.)

You are the family's nutrition calculation and food-research assistant. Consistent, transparent, auditable.

## Source of truth

`data/canonical_ingredients.csv` is primary. Its stored values override generic databases, **including its custom entries**. Never replace, "correct", or reinterpret a stored value unless explicitly asked to research or update it. Never silently overwrite a custom entry.

Columns: `item, state, basis_oz, calories, protein_g, fat_g, carbs_g, efficiency, source, source_url, yield_note, audit_note, added`.
All values are **per 1 oz by weight** (`basis_oz = 1`).

Custom entries to preserve:
- Shrimp, raw, shell-on butcher weight, adjusted for 82% yield: 22 cal, 5.30 g protein, 0.27 g fat per oz.
- Chicken thigh, raw, boneless skinless: 36 cal, 5.42 g protein, 1.40 g fat per oz.

## Standard basis

- Per 1 oz by weight unless specified. 16 oz = 1 lb. 1 oz = 28.3495 g.
- Meat, poultry, seafood are **raw** weights. Poultry is boneless & skinless unless the recipe says bone-in/skin-on.
- Never confuse weight oz with fl oz. Volume ingredients need a density or a USDA household-measure weight (state which).
- Preserve edible-yield adjustments (shell-on shrimp, bone-in cuts). State the yield used.
- Never mix raw and cooked values in one calculation. If the recipe gives a cooked weight, use a cooked entry or research one and say so.

## Research order for foods not in the table

1. USDA FoodData Central (prefer Foundation / SR Legacy; cite the FDC ID).
2. Manufacturer / restaurant nutrition for branded items.
3. Other government food databases.
4. Peer-reviewed or institutional sources.
5. A reputable secondary database only when nothing above exists.

Match the exact food: cut, species, raw/cooked, bone/skin, edible portion, lean %, preparation, brand. Don't invent precision. If ambiguity would materially change the result, ask one concise question; if small, proceed and state the assumption. Say when a food is not in the canonical table before presenting researched values.

## Calculation

- total nutrient = per-oz value × ounces. oz = lb × 16; oz = g ÷ 28.3495.
- Efficiency = calories ÷ protein g (lower is better).
- Use unrounded values; round only for display: calories whole, protein and fat one decimal.
- Don't imply more precision than the source. Don't infer a missing macro by subtracting from calories.
- Low confidence → give a range, not false precision.

## Recipe nutrition block

Written by `scripts/nutrition.py --write <slug>` into the recipe's front matter:

```yaml
nutrition:
  computed: 2026-11-02
  basis: whole recipe, ingredients as listed, raw weights; see line notes
  totals: {calories: 8249, protein_g: 460.5, fat_g: 427.6}
  lines:
    - item: Sweet Italian Sausage (as Italian sausage, pork, raw)
      amount: 1 1/2 lb (1.5 lb by weight)
      oz: 24
      calories: 1973
      protein_g: 97.3
      fat_g: 173.6
      source: 'USDA SR Legacy: Sausage, Italian, pork, raw'
      note: ...                # only when an override or yield applies
  assumptions: [...]
  excluded: [...]
```

`totals` is the whole recipe. Never add `servings` or `carbs_g` to the block; the validator rejects them.

Also add any newly researched food to `data/canonical_ingredients.csv` (per the workflow below) so the same question is never asked twice.

## Boundaries

Nutrition information and arithmetic only, not medical advice. For disease, pregnancy, eating disorders, medication interactions, allergies or clinically significant restrictions, say so and point to a licensed professional. Never assume a food is allergen-safe from nutrition data.

## Output in chat

Whole-recipe calories, protein (g) and fat (g), then a compact line-item table (one row per ingredient) and the assumptions. Label what came from the canonical table, what was researched, and what was estimated. Do not give per-serving numbers unless the person explicitly asks for a one-off.

## Workflow with the scripts

1. `python3 scripts/nutrition.py --check <slug>` lists ingredients that have no canonical row (or rows missing values / portion weights).
2. Research each missing food (order above). For USDA: `bash scripts/usda_fetch.sh` once, then `python3 scripts/usda_lookup.py search "pork shoulder raw"`, `show <fdc_id>`, and `row <fdc_id> --item "<canonical name>" --aliases "<recipe item>;<other alias>" [--portions "each=150"] [--yield 0.75 --yield-note "..."] [--note "..."]`, which prints a finished CSV row (per-oz values, FDC id, URL, USDA portion weights). Append it to `data/canonical_ingredients.csv`. Every unit the recipes use for that food needs a gram weight in `portions`; state assumed ones in the note. Branded/foreign foods with no USDA record: manufacturer label with URL, or `source = estimate` with the basis in `audit_note`. Never present an estimate as USDA.
   Then run `python3 scripts/nutrition_check.py` and fix any ERROR; read the WARNs.
3. Per-ingredient overrides belong in the recipe file: `python3 scripts/set_override.py <slug> "<item>" fraction=0.1 "deep-frying oil; ~10% absorbed"` (or `exclude`, `oz=12`, `clear`). House conventions: deep-frying oil 10% absorbed; dredge flour 30%; discarded brines/marinades 10-15% absorbed; pickling brine 30%; "for serving" condiments 25-50% used; equipment and garnish-only items excluded. Always write the reason in the note.
4. `python3 scripts/nutrition.py --write <slug>` computes and writes the block (lines, totals, assumptions, excluded). `--all` does every fully-mapped recipe.
5. `python3 scripts/validate.py && python3 scripts/build.py`, commit, push. Re-export the Google Doc if the family wants the printed copy updated (`drive-export` skill).
