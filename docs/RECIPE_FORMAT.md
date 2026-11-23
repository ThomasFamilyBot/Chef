# Recipe file format

Each recipe is `recipes/<slug>.md`: YAML front matter, then Markdown directions.
The slug is lowercase, hyphenated, ASCII (`bo-ssam.md`).

```markdown
---
title: Bo Ssam                            # for a URL submission: the recipe's name as the page gives it; the site and Doc hyperlink it to reference.url
reference:
  text: Momofuku cookbook p. 166          # what the printed page says
  url: https://cooking.nytimes.com/...    # optional hyperlink
  url_text: NYT translation               # optional; label for the link (defaults to the text)
serves: 4-6 w/ leftovers                  # free text as printed
servings: 5                               # numeric hint used only by sanity checks (nutrition is reported whole-recipe)
times:                                    # minutes; null when unknown
  prep: 60
  cook: 360
  rest: 60
  total: 480
tags: [pork, korean, main, project]
source_doc: https://docs.google.com/document/d/...   # original legacy doc, if converted
drive_doc_id: null                        # Google Doc id of the exported copy, once written
techniques_skip: [smoke]                  # optional; glossary terms to leave out of the "Technique temperatures" box when a word matches by accident (e.g. "air fryer" -> deep fry)
ingredients:
  - measure: 1 cup + 1 TBLS               # display string, exactly as printed on the page
    item: Kosher Salt                     # canonical shopping name, Title Case, no prep words
    prep: 1 cup separate from TBLS        # optional
    group: 1 -> Brine the pork             # mise grouping (bowl number -> step/component); bowls run 1..N with no gaps
    qty: 17                               # numeric amount in `unit` (used for shopping-list merging)
    unit: TBLS                            # one of the unit vocabulary below
    section: Spices & Dried Herbs         # optional; falls back to data/store_sections.yaml keywords
    shop: true                            # optional; false keeps it off shopping lists (e.g. Water)
nutrition: null                           # or the block described in .claude/skills/nutrition/SKILL.md
---
**Day 1**

Brine Pork

- Place pork in a large shallow bowl ...
```

## Required

`title`, `reference.text`, `serves`, `times` (keys may be null), `ingredients` (each with `measure`, `item`, `qty`, `unit`).
Directions body must be non-empty.

## Unit vocabulary (the `unit` field)

Volume: `tsp`, `TBLS`, `fl oz`, `cup`, `pint`, `quart`, `gallon`
Weight: `g`, `oz`, `lb`
Count: `each`, plus descriptive counters: `clove`, `head`, `bunch`, `sprig`, `stalk`, `can`, `jar`, `bottle`, `container`, `package`, `box`, `bag`, `loaf`, `stick`, `slice`, `dozen`, `pinch`, `dash`, `to taste`

`measure` is what prints. `qty` + `unit` are what the shopping list adds up. For "1 cup + 1 TBLS", `qty: 17, unit: TBLS`. For "2 (14.5 oz) cans", `qty: 2, unit: can` and put the size in `prep` or `item` ("Crushed Tomatoes, 28 oz can"). For a range ("10-12 oz"), use the high end for `qty`.

## Nutrition block

See `.claude/skills/nutrition/SKILL.md`.

## Per-ingredient nutrition overrides

An ingredient line may carry a `nutrition:` key read by `scripts/nutrition.py`:

```yaml
    nutrition: exclude                              # equipment, garnish, discarded brine
    nutrition: {fraction: 0.1, note: brine; ~10% absorbed}
    nutrition: {oz: 12, note: edible weight override}
```

## Versions for an event

A recipe made at different quantities (or with different cuts) for one dinner is a separate file, never an edit to the original: `recipes/<slug>-<event>.md`, titled `<Title> (<Event>)`, with four extra front-matter keys:

```yaml
variant_of: red-wine-braised-beef-short-ribs   # the original's slug (must exist)
variant_for: Thanksgiving 26                   # the event
event_date: 2026-11-26                         # the day of the event
delete_on: 2027-01-01                          # one full calendar month after the event, then the 1st; validate.py warns from this date
```

The recipe page links back to the original. The procedure, including what happens after the event, is in `.claude/skills/menu-planning/SKILL.md`.
