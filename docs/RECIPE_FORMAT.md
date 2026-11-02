# Recipe file format

Each recipe is `recipes/<slug>.md`: YAML front matter, then Markdown directions.
The slug is lowercase, hyphenated, ASCII (`bo-ssam.md`).

```markdown
---
title: Bo Ssam
reference:
  text: Momofuku cookbook p. 166          # what the printed page says
  url: https://cooking.nytimes.com/...    # optional hyperlink
  url_text: NYT translation               # optional; label for the link (defaults to the text)
serves: 4-6 w/ leftovers                  # free text as printed
servings: 5                               # number used to divide nutrition (midpoint of a range)
times:                                    # minutes; null when unknown
  prep: 60
  cook: 360
  rest: 60
  total: 480
tags: [pork, korean, main, project]
source_doc: https://docs.google.com/document/d/...   # original legacy doc, if converted
drive_doc_id: null                        # Google Doc id of the exported copy, once written
ingredients:
  - measure: 1 cup + 1 TBLS               # display string, exactly as printed on the page
    item: Kosher Salt                     # canonical shopping name, Title Case, no prep words
    prep: 1 cup separate from TBLS        # optional
    group: ""                             # optional mise grouping, e.g. "1 -> Ginger Scallion Sauce"
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
