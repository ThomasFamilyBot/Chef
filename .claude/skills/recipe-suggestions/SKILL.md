---
name: recipe-suggestions
description: Suggest new recipes to add to the family library, ranked by evidence the family wants them (dishes they've cooked from outside links, gaps in the library, seasonal fits). Use when someone asks what to add, what to cook next, or for new recipe ideas.
---

# New recipe suggestions

Suggest, don't add. Each suggestion is one line the person can accept with "add #2", which then runs the `recipe-intake` skill.

## Sources, in priority order

1. **Dishes they already cook but haven't written down**: every `{title, url, note}` item in `data/menus.yaml` without a slug. These are proven favorites (Bertolli cauliflower soup, Serious Eats meatballs and 6-hour sauce, steak suya, Thai crunch salad, mint chip ice cream, waffle cones, hibiscus punch, kale-harissa salad, smoked short ribs, pulled pork, Fred's burgers). Lead with these.
2. **Gaps by tag**: run `python3 - <<'EOF'` style counts over `recipes/*.md` tags: few `vegetarian` mains, no fish/seafood mains besides vongole, few quick (≤30 min) weeknight mains, no bread besides popovers/pizza dough, no soups except the beef noodle soup. Suggest to fill the thinnest categories.
3. **Pairing holes**: mains in `data/pairings.yaml` with no side or dessert partner.
4. **Season / occasion** the person names.

## How to present

- 5-8 suggestions max, each: dish, why (which source above), link if there is one, estimated active time, and what it pairs with in the library.
- Respect house taste from the library: high-protein mains, bold flavors (Korean, Italian-American, BBQ, Nashville hot), projects for weekends, sous-vide and smoker friendly, ice creams for dessert.
- Never present a URL you haven't seen; if you only know the dish, say "no link, I'd write it from <book/site> if you have it".

## After acceptance

Run `recipe-intake` for the chosen dish, then offer to add it to a menu or a pairing.
