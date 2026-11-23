---
name: menu-planning
description: Plan a menu or dinner party from the family library, record menus (run of show) in data/menus.yaml, and maintain "pairs well with" links in data/pairings.yaml. Use when someone asks what goes with a recipe, wants a menu for an occasion, or wants a past dinner written down.
---

# Menu planning and pairings

## Data

- `data/menus.yaml`: one entry per menu. `items` are `{slug: <recipe>}` for library recipes or `{title, url?, note?}` for dishes not yet in the library. `notes` holds the run-of-show timing. An item that is already made or bought gets `shop: false` (with a `note` saying so): it stays on the menu, linked, but the shopping button leaves it out. The site renders these on **Menus**, with "add all to shopping list"; recipe pages list the menus they appear on.
- `data/pairings.yaml`: `[slug_a, slug_b, "short reason"]`. Shown on both recipe pages under "Pairs well with". Keep reasons honest and specific (a menu that worked, a classic combination, a shared shopping list).

## When asked "what goes with X"

1. Read `data/pairings.yaml` and the recipe's tags/times. Offer 2-4 library options first (a side, a starter or dessert, a drink), with one-line reasons, then at most 2 ideas outside the library.
2. Balance: rich main → sharp salad or pickles; long braise → quick dessert; big fry → plain dessert; match cuisines or shopping lists (same condiments), and keep total active time sane (don't pair two 4-hour projects).
3. If the person likes a pairing, append it to `data/pairings.yaml` so it shows on the site.

## When asked for a menu / dinner party

1. Ask (once) for: occasion, date, head count, any constraints (kids, vegetarians, grill vs oven, how much active time they want).
2. Propose a menu from the library with timing: which recipes, which day each prep step happens, oven/grill conflicts, what can be made ahead. Use `times` from the recipe files.
3. On approval, add the menu to `data/menus.yaml` (name, occasion, date, serves, notes with the run of show, items). Validate, build, commit, push. Tell them it is on the Menus page and can be added to the shopping list in one tap.

## Versions for an event (quantity or ingredient variations)

House rule: when a dinner needs a library recipe at different quantities, or with different cuts or ingredients, **never edit the original**. Make a version for that event, put the version on the menu, and delete it after the event. The original stays in the library untouched.

- **File and title:** copy `recipes/<slug>.md` to `recipes/<slug>-<event>.md` and add the event to the title in parentheses: `Red Wine–Braised Beef Short Ribs (Thanksgiving 26)` in `red-wine-braised-beef-short-ribs-thanksgiving-26.md`.
- **Front matter:** `variant_of: <original slug>`, `variant_for: <event name>`, `event_date: <the day of the event>`, `delete_on: <date>`, and a tag for the event. `delete_on` follows the house rule: a version is kept for one full calendar month after the event and deleted on the 1st of the month after that (an event on 26 November 2026 gives 1 January 2027; an event on 3 May gives 1 July). Drop the original's `drive_doc_id` and `nutrition` block (both are redone for the version).
- **Change only what the event needs:** the quantities, cuts and swaps, then whatever follows from them (pan size, times, `serves`). Keep the reference line and the rest of the method as they are. Mark changed times as estimates when the source gives none.
- **Say what changed:** the first line of Notes reads "<Event> version. What changed from the original: ...".
- **What they already have:** ingredients the household is using from the freezer or pantry get `shop: false`, with a word in `prep`, so the menu's shopping button doesn't list them.
- **Then the usual four parts** (`recipe-intake`): validate, whole-recipe nutrition, a Google Doc for the version, build, commit, push.
- **On the menu:** the version replaces the original in `data/menus.yaml`, and the run of show Doc is mirrored (the line gets the version's title and link).
- Make a version only for recipes that actually change. A recipe cooked as written stays on the menu as the original.

**Deleting versions.** Versions are deleted on their `delete_on` date. The household set this rule on 2026-11-23, so deleting on or after that date needs no further yes; before it, ask.

- When you make versions, also schedule the clean-up for `delete_on` if this session can (a one-time reminder into the same session). `scripts/validate.py` is the backstop: from that date it warns on every run, and whichever session sees the warning does the clean-up.
- The clean-up: point the menu back at the originals (a past menu keeps the originals, not the versions); delete the version files; trash their Google Docs (`drive-export` skill; log each in `docs/DRIVE_TRASH_LOG.md`); validate, build, commit, push; then tell the household what was removed. The files stay in git history if one is ever wanted back.
- If the household says they liked a change and want to keep it, add it to the original as a Note before deleting the version.

## Mirror every menu change in its Google Doc

House rule: when a menu has a `source_doc` (the family's run of show Doc), any change to that menu in `data/menus.yaml` is mirrored in the Doc in the same task, without being asked. Adding, removing, renaming or reordering items all count.

- The Doc's item list carries the same items in the same order as the menu. Keep the family's own wording for lines they wrote ("Popovers", "Sweet Potato & marshmallow"); new lines take the menu's title, with its note after a dash when there is one ("Blackberry Crumble - Wed 10am Pickup").
- The head count line (`serves`) sits as a plain paragraph above the list, in the family's own words.
- Items that are library recipes are linked to their site page (`<site_url>r/<slug>.html`); items without a recipe stay plain text.
- Edit the Doc in place with the Google Docs connector (read the `google-workspace` skill's Docs reference first): `read_doc`, then one `update_doc` guarded with the `revisionId`. Touch only the item list. Timing notes and anything else the family wrote in the Doc stay as they are.
- Read the Doc back afterwards and check the list. Say in the final message that the Doc was updated.
- A menu with no `source_doc` has nothing to mirror; don't create a Doc unless asked. If the family edits the Doc and asks for the site to match, go the other way: update `data/menus.yaml` from the Doc.

## Recording a past dinner

Convert a Run of Show doc: library recipes by slug, everything else as `{title, url, note}`. Don't invent recipes; items without a written recipe are candidates for the `recipe-suggestions` skill.
