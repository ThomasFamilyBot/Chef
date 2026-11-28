# Chef

Household recipe library, nutrition calculator, and shopping-list planner.
Everything lives in this repo. A static site is built from it and deployed to GitHub Pages.

<!-- household:start -->
## This household

- **Household:** the Thomas family. They call this project, and Claude when working in it, **ChefBot** (also "Chef" or "the Chef bot"). All three mean this repo and its site.
- **Repo:** `ThomasFamilyBot/chef` · **Site:** https://thomasfamilybot.github.io/Chef/
- **Google account that owns everything:** ahinthomas@gmail.com (see "Google identities" below).
- Every other household-specific value (list names, Drive folder ids, Gmail label ids, the lists web-app URL, house taste) is in `data/site.yaml`. Read it at the start of any task that touches Google, the site link, or shopping lists.
- **Kitchen equipment** (ice cream maker size and the like) is under `equipment` in `data/site.yaml`. Read it before scaling a recipe or writing batch / churn instructions.
- **The starter keeps itself current.** Other households copy ChefBot from the public template `ThomasFamilyBot/chefbot-starter` (see `starter/README.md`). A GitHub workflow ("Update starter template") publishes a fresh scrubbed copy once a day, so there is nothing to run after a push and the template may lag by a day. Run `bash starter/ship.sh` by hand only when asked for a same-day update. New household-specific values still belong in `data/site.yaml`, and new people's names in `DENY_WORDS` in `starter/export.py`, or the nightly run fails its scrub and publishes nothing. Copies people already made are not updated; that is intended.
<!-- household:end -->

## Layout

- `recipes/*.md` — one recipe per file. YAML front matter (structured) + Markdown directions. **This is the source of truth.** See `docs/RECIPE_FORMAT.md`.
- `data/canonical_ingredients.csv` — the canonical nutrition table (per 1 oz by weight). Never overwrite a row silently.
- `data/store_sections.yaml` — ordered grocery-store sections + keyword fallbacks for ingredients that don't declare a section.
- `data/shopping_templates/*.yaml` — recurring lists (e.g. house staples) that can be added to any shopping list.
- `data/items.yaml` + `site/static/items/` — item details cards (photo, notes) shown when an item is tapped; see "item photos" below.
- `data/techniques.yaml` — technique glossary (sweat, sauté, medium-high, simmer, fry…) with target temperatures; auto-appended to recipe pages and Docs.
- `docs/DOC_MAP.md` — generated map of recipe ↔ Google Doc ↔ site page.
- `answers/*.md` — published "Ask" answers (question, picks with links, library matches), shown on the site's Ask page. `data/taste_lenses.yaml` — cooks and styles the household asks for ("like Bourdain").
- `data/menus.yaml` — menus / run of show (library slugs + not-yet-written dishes). `data/pairings.yaml` — "pairs well with" links with reasons.
- `scripts/validate.py` — checks every recipe against the format. Run it before committing.
- `scripts/build.py` — builds the site into `dist/`.
- `scripts/export_gdoc_html.py` — renders a recipe as HTML in the family's Google Doc template layout, for writing back to Drive.
- `scripts/push_docs.py` — rewrites recipes' Google Docs in place from the recipe files (`--stale`, `--all`, or slugs); needs `docs_api` (`docs/DOCS_API.md`). `scripts/gdoc_table_requests.py` is the fallback for one Doc's table without it.
- `scripts/nutrition.py` — computes a recipe's nutrition from the canonical table (`--check`, `--write <slug>`, `--all`).
- `scripts/nutrition_check.py` — sanity checks on the table and on computed recipes (ranges, Atwater consistency, portion weights, per-serving plausibility). Run after any nutrition change.
- `scripts/usda_fetch.sh` + `scripts/usda_lookup.py` — local copy of USDA SR Legacy; `search`, `show`, and `row` (emits a ready canonical CSV row with FDC id, URL and portion weights).
- `scripts/set_override.py` — set a per-ingredient nutrition override in a recipe (exclude / fraction / oz) with a note.
- `site/` — templates and static assets for the site.
- `data/site.yaml` — site and household settings: names, repo, site address, list names, Google folder and label ids, and the optional video commands (frames and transcript) used to take recipes from reels.
- `SETUP.md` + `scripts/setup_check.py` — first-time setup of a new copy (only when `setup_done` is false in `data/site.yaml`).
- `.claude/skills/` — the procedures Claude follows: `recipe-intake`, `nutrition`, `drive-export`, `menu-planning`, `recipe-suggestions`, `recommend`, `drive-sync`, `inbox-processing`.

## When asked to add / convert a recipe

Follow `.claude/skills/recipe-intake/SKILL.md` exactly. It covers the questions to ask the uploader
(reference text, hyperlink), unit rules, abbreviations, ingredient naming, mise groupings, technique temperatures, store sections, and the file format.
**Adding a recipe is a four-part job, every time, without being asked:** (1) the recipe file, (2) whole-recipe nutrition: calories, protein g, fat g only
(`nutrition` skill; new foods go into the canonical table with a source), (3) a Google Doc copy (`drive-export` skill), (4) validate, build, commit, push.
Report all four in the final message.
**Once the deploy has finished successfully, give the person the recipe's site link** (`<site_url>r/<slug>.html`), checked live (HTTP 200). This applies to every new recipe, including ones added from the inbox.

## Mise groupings: one bowl, one moment

A mise group holds only the ingredients that go into the pot at the same moment. If the directions add things separately (the wine goes in and simmers before the stock; the garlic goes in after the onion; the oil heats first), they are separate bowls, even when they belong to the same step or the same sauce. Never group by step or component.

- The full rule, the common splits and the check are in `.claude/skills/recipe-intake/SKILL.md` ("Mise groups: one bowl, one moment").
- Run that check **every time** a recipe's ingredients or the order of its directions change: new recipes, Google Doc syncs, event versions, and fixes made after a cooking question.
- The validator only checks numbering. It warns when a direction says "everything from a bowl except...", which means the bowl is wrong, but it cannot tell that a bowl is right.

Why: on 2026-11-25 the Thanksgiving short ribs had the wine in the same bowl as the stock and herbs, though the wine goes in first, alone. The whole library was regrouped that day.

## When the family edits a Google Doc and says "doc updated, update the app"

Follow `.claude/skills/drive-sync/SKILL.md`: find the recipe by the doc id, read the doc, update the recipe file, recompute nutrition, rebuild.

## When asked for nutrition

Follow `.claude/skills/nutrition/SKILL.md`. Whole recipe only; calories, protein g, fat g only. Canonical table first, USDA second, every assumption written down.

## When asked for a recommendation ("ChefBot, recommend: ...", "what should I cook", "best way to...")

Follow `.claude/skills/recommend/SKILL.md`. The best answer to the question comes first, researched on the internet from pages actually opened; library recipes go last and only when they truly compete. First reply is a quick take plus a few taps of input (lens, effort, who's eating). When some pages are blocked, give initial results, say you are checking the blocked pages in Chrome, then give the full answer. When the question is settled, ask once whether to publish the answer to the site's Ask page (`answers/*.md`). The Ask page's button opens a new Claude session with the question typed in (`ask` in `data/site.yaml`).

## When asked what goes with a dish, for a menu, or for new recipe ideas

Follow `.claude/skills/menu-planning/SKILL.md` or `.claude/skills/recipe-suggestions/SKILL.md`. When a menu with a run of show Google Doc (`source_doc`) changes, mirror the change in that Doc in the same task. When a dinner needs a recipe at different quantities or with different ingredients, never edit the original: make a version named `<Title> (<Event>)` for the menu and delete it after the event ("Versions for an event" in the menu-planning skill).

## When someone asks a cooking question about a recipe (a swap, a technique, "can I...", often mid-cook)

Read the recipe file first and answer from it. The person may be at the stove and will do exactly what the answer says, so any advice that departs from the written method (a different order, temperature, tool or ingredient, or a tip of your own) is checked before it is given:

- **Walk the changed step through as it happens at the stove:** what is in the pan at that moment, how hot it is, and what goes in next. Then check the steps after it still work.
- **Look for the known ways it goes wrong.** Cold liquid onto hot or undissolved caramel (seizes hard). Eggs or yolks into hot liquid (scramble). Milk at a hard boil or with acid (curdles). Cheese or cream sauce over high heat (breaks). A little water into melted chocolate (seizes). Water into hot fat (spatters). Hot liquid in a closed blender (blows the lid). Cold liquid into a hot glass or enamel dish (cracks). A swap that changes sugar, salt, fat, acid or water (sweetened for unsweetened, salted for unsalted, dried for fresh).
- **Put the condition the advice depends on into the advice itself,** in the same sentence: "only after the caramel has fully dissolved in the simmering cream", not "once they are combined".
- **Say which part is yours and which is the recipe's.** If you cannot rule out a failure, say so, or keep to the written method.
- **If advice goes wrong:** the rescue comes first, then what caused it. If the recipe page has the same gap, offer to add a Note there.

Why: on 2026-11-23 a tip to "pour the cold milk in first" for an immersion-blender custard did not say the caramel had to be dissolved in the cream first, and the caramel seized in the pan.

## When asked to process the recipe inbox (friends' email / Drive submissions)

Follow `.claude/skills/inbox-processing/SKILL.md`. A scheduled Routine runs it; it can also be run on request.

## When someone sends a photo of a shopping item ("item photos")

Tapping an item with a small picture marker (photo) or a small "i" (notes only) after its name on the Shopping List or a recipe page opens a details card: photo, notes, which lists and recipes use it. Data lives in `data/items.yaml`; photos in `site/static/items/`.
- Chat photos are saved under `~/.claude/uploads/<session>/`. Look at the photo first: the site is public, so skip anything personal (faces, addresses, receipts) and ask.
- `python3 scripts/add_item_photo.py --item "<name exactly as on the list>" --photo <file> [--alias "<recipe name>"] [--notes "brand, size, aisle"] [--rotate 90]`. It resizes to 1000 px and strips location/camera data. Never copy a photo into `site/static/items/` by hand.
- Use `--alias` so a template name like "Dried Mango (organic)" and the recipe name "Dried Mango" open the same card. Read the converted photo back to check it is upright.
- Then build, commit, push, wait for the deploy, and tell the person which item now has a card.

## When asked to put a recipe in Google Drive, or after a recipe changes

Follow `.claude/skills/drive-export/SKILL.md`. A recipe's Google Doc is updated **in place**, so its link never changes: when `docs_api` is set in `data/site.yaml`, `python3 scripts/push_docs.py --stale` does every Doc that is out of date in one command, on the computer. Replacing a Doc (new link, old one to the trash) is the last resort.

## Library-wide changes (a new rule, a rename, a format change: anything that touches many recipes)

Do them in this order. The aim is that nothing recipe-sized ever passes through the conversation.

1. **Write the rule first,** here and in the skill that owns it, with the reason and the date. New recipes then follow it while the old ones are being fixed.
2. **Fix the one recipe the person is looking at** and push it, before starting on the rest. They are often cooking from it.
3. **Read, then change by script.** For judgement calls, print a compact view of each recipe (table plus directions, no nutrition block) and read it in batches of about a dozen. Apply each decision through a small helper that takes a short spec per recipe and refuses to write when something does not add up (an ingredient unassigned, a label the directions cite that no longer exists). Never hand-edit 100 files, and keep the helper in `scripts/` if the job could come back.
4. **Prove nothing else moved.** Compare every changed recipe with `git show HEAD:<file>` after parsing: only the fields the change is about may differ, and the directions keep their line count unless the change is to the directions. Then `validate.py`, `build.py`, `nutrition_check.py`.
5. **One commit, one push** for the library; wait for the deploy and check one live page.
6. **Google Docs: `python3 scripts/push_docs.py --stale`.** One command, links kept. If `docs_api` is not set up, say how many Docs are now out of date and offer the five-minute setup in `docs/DOCS_API.md`; do not re-create Docs one by one through the session (about 8 KB each, and every link changes).
7. **Add a check** to `validate.py` for whatever can be checked by machine, and say plainly what it cannot check.
8. **Report** how many recipes changed, how many were already right, and anything skipped.

Why: on 2026-11-25 all 168 recipes were regrouped ("one bowl, one moment"). The recipe files took one scripted pass, but the Docs could only be replaced one at a time through the conversation, so only 7 of 103 were done and each got a new link. `push_docs.py` exists so that never happens again.

## Google identities

- The `google_account` in `data/site.yaml` owns everything in Google: the Drive folders, the Google Docs, the shared shopping-lists sheet and its Apps Script, and the Claude connectors. Any Google setup step is done signed in as this account.
- The public recipe-submission address (`submission_email` in `data/site.yaml`) is a forwarder only; it owns nothing.
- **Whenever you ask the household to do something in Google, say which account to be signed in as.**

## Always

- **Start every task with `git pull --rebase origin main`.** Several Claude sessions and people share this repo; a stale checkout makes comparisons and exports wrong (e.g. a Docs refresh that "matches" an old version).
- Run `python3 scripts/validate.py` after editing any recipe; fix what it reports.
- Run `python3 scripts/build.py` to confirm the site builds.
- After a pushed change to any recipe, if `docs_api` is set in `data/site.yaml`: `python3 scripts/push_docs.py --stale`, then commit `docs/DOC_SYNC.json`. It only touches Docs whose page changed.
- Commit with a clear message and push to `main`. The site redeploys automatically; wait for `gh run list --limit 1` to show the run completed before sending anyone a site link (Pages takes a minute or two).
- Units: `g`, `tsp`, `TBLS`, `cup`, `oz` (weight), `fl oz` (volume), `lb`. Nothing else without asking.
