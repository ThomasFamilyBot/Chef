---
name: menu-planning
description: Plan a menu or dinner party from the family library, record menus (run of show) in data/menus.yaml, and maintain "pairs well with" links in data/pairings.yaml. Use when someone asks what goes with a recipe, wants a menu for an occasion, or wants a past dinner written down.
---

# Menu planning and pairings

## Data

- `data/menus.yaml`: one entry per menu. `items` are `{slug: <recipe>}` for library recipes or `{title, url?, note?}` for dishes not yet in the library. `notes` holds the run-of-show timing. The site renders these on **Menus**, with "add all to shopping list"; recipe pages list the menus they appear on.
- `data/pairings.yaml`: `[slug_a, slug_b, "short reason"]`. Shown on both recipe pages under "Pairs well with". Keep reasons honest and specific (a menu that worked, a classic combination, a shared shopping list).

## When asked "what goes with X"

1. Read `data/pairings.yaml` and the recipe's tags/times. Offer 2-4 library options first (a side, a starter or dessert, a drink), with one-line reasons, then at most 2 ideas outside the library.
2. Balance: rich main → sharp salad or pickles; long braise → quick dessert; big fry → plain dessert; match cuisines or shopping lists (same condiments), and keep total active time sane (don't pair two 4-hour projects).
3. If the person likes a pairing, append it to `data/pairings.yaml` so it shows on the site.

## When asked for a menu / dinner party

1. Ask (once) for: occasion, date, head count, any constraints (kids, vegetarians, grill vs oven, how much active time they want).
2. Propose a menu from the library with timing: which recipes, which day each prep step happens, oven/grill conflicts, what can be made ahead. Use `times` from the recipe files.
3. On approval, add the menu to `data/menus.yaml` (name, occasion, date, serves, notes with the run of show, items). Validate, build, commit, push. Tell them it is on the Menus page and can be added to the shopping list in one tap.

## Recording a past dinner

Convert a Run of Show doc: library recipes by slug, everything else as `{title, url, note}`. Don't invent recipes; items without a written recipe are candidates for the `recipe-suggestions` skill.
