---
name: recipe-suggestions
description: Suggest new recipes to add to the family library, ranked by evidence the family wants them (dishes they've cooked from outside links, gaps in the library, seasonal fits). Use when someone asks what to add, what to cook next, or for new recipe ideas.
---

# New recipe suggestions

Suggest, don't add. Each suggestion is one line the person can accept with "add #2", which then runs the `recipe-intake` skill.

## Sources, in priority order

1. **Dishes they already cook but haven't written down**: every `{title, url, note}` item in `data/menus.yaml` without a slug. These are proven favorites. Lead with these.
2. **Gaps by tag**: count the tags over `recipes/*.md` (a short `python3` loop over the front matter) and look at courses, proteins and total times: vegetarian mains, fish and seafood, quick (≤30 min) weeknight mains, breads, soups, desserts. Suggest to fill the thinnest categories.
3. **Pairing holes**: mains in `data/pairings.yaml` with no side or dessert partner.
4. **Season / occasion** the person names.

## How to present

- 5-8 suggestions max, each: dish, why (which source above), link if there is one, estimated active time, and what it pairs with in the library.
- Respect house taste: `house_taste` in `data/site.yaml` when it is set, plus what the library itself shows (its most common tags, cuisines and equipment).
- Never present a URL you haven't seen; if you only know the dish, say "no link, I'd write it from <book/site> if you have it".

## After acceptance

Run `recipe-intake` for the chosen dish, then offer to add it to a menu or a pairing.
