---
name: recommend
description: Answer a food question with the best answer from anywhere (what should I cook, the best version of a dish, how to do a technique, what goes with something), researched on the internet first and with library recipes added last only when they truly compete. Use when a message starts with "ChefBot, recommend:" (sent from the site's Ask page), or when someone asks for a recommendation, an idea for a meal or occasion, or "what's the best way to...". Ends by asking whether to publish the answer to the site.
---

# Recommendations ("Ask ChefBot")

The person wants **the best answer to the question**, not a tour of the library. Order of loyalty: the question, then the wider world of cooking, then the library. A library recipe is mentioned only when it honestly competes with the best outside options.

This is a live conversation, usually from a phone. Be fast first and thorough second.

Not this skill: "what should we add to the library" (`recipe-suggestions`), building a menu or a run of show (`menu-planning`), adding a recipe (`recipe-intake`). Hand over to those when the conversation turns that way.

## 0. Before answering

- `git pull --rebase origin main` (the library and the lens list may have changed).
- Read `data/site.yaml` (`house_taste`, `equipment`) and `data/taste_lenses.yaml`.
- A message from the Ask page reads `ChefBot, recommend: <question>`. The text after the colon is the question.

## 1. First reply: quick take, then ask for input

Send both in the same turn, before any long research.

**Quick take.** Two to four sentences from what you already know, plus at most one fast search. Say plainly that it is a first take and the researched answer follows. Never hold the first reply for page reading.

**Input.** One batch of at most three questions, with `AskUserQuestion` when the tool is there (it shows as taps on a phone), otherwise as a short numbered list. Ask only what the question left open:

1. **Lens**: whose cooking, or what style, are they in the mood for today? Offer the names in `data/taste_lenses.yaml`, one or two that fit this particular question (say why in the option text), and "No lens, just the best". The mood changes day to day; never assume yesterday's.
2. **Effort**: a weeknight (under an hour), an unhurried evening, or a project.
3. **The table**: who is eating and any constraint (kids, a guest's diet, what is already in the fridge).

Skip the questions entirely when the question is already specific ("best way to reheat brisket") or the person says "just answer". Never ask more than once; later preferences come out in conversation.

## 2. Research: the internet first

Work from real pages, not memory.

- Search widely first: several searches in one turn, phrased different ways (the dish, the technique, "best", the lens name, a trusted site name). With a lens, start with that cook's own books, shows and recipes (`look_first` in the lens file), then people who cook the same way.
- Open the pages. Read at least five candidates before choosing, and compare them: what each does differently (cut, temperature, time, a step others skip) and whether the difference matters.
- **How to open a page**, in this order:
  1. the web fetch tool or agent;
  2. the household's headless browser command, when `ask.fetch_command` in `data/site.yaml` names one and you are on that computer (run it with the URLs; it says where it saved the page text);
  3. Claude in Chrome on that computer (load the `claude-in-chrome` skill first; use a new tab, read with `get_page_text`, close the tab after). This is what gets past sites that block the first two.
- Never try to beat a bot check, a paywall or a sign-in. If a page will not open by these routes, either leave it out or list it as "couldn't open, going by the search summary" and do not rank it first.
- Only link pages you opened. Never invent or guess a URL.
- Summarize in your own words. Don't paste a site's recipe; the link is there for that. To cook from one, the person says "add #2" and `recipe-intake` takes over.
- Favor sources that test recipes and explain why. Weigh the house equipment (`equipment`, and the smoker and sous-vide gear in `house_taste`) as a tiebreaker and as a way to adapt a pick, not as a filter. `house_taste` shapes open questions ("what should I make Saturday"); it never overrides a specific question or the lens they picked today.

## 3. The answer

Short enough to read on a phone.

1. **Bottom line**: one sentence. "Make X, from Y."
2. **Picks**: three to five, numbered, best first. Each: the dish and source as a link, why it earns its place, active and total time, and what makes this version different from the others.
3. **How they differ**: one or two lines when the picks are versions of the same dish.
4. **From your library**: at most three, linked to `<site_url>r/<slug>.html`, only when a library recipe would deserve a place among the picks on the question's own terms. Say where it would rank. If nothing in the library competes, write one line saying so, or leave the section out. Never pad it and never move a library recipe up out of loyalty.
5. One line on what to say next: "add #2", "more like #1", "something lighter".

Then keep talking. Follow-up questions get direct answers; re-research only when the direction changes.

## 4. When it is settled: offer to publish

When the person has picked something, says thanks, or the conversation has clearly landed, ask once (with `AskUserQuestion` when available):

- **Publish this to the website?** Yes / No.
- When a pick is not in the library: **Add it to the library?** (runs `recipe-intake`).

Do not ask before the question is settled, and do not ask twice. A conversation that fizzles out is not published. Each new question in the same session gets its own ask.

## 5. Publishing an answer

The site is public. Publish the useful write-up, not the chat.

- Rewrite the question neutrally, with no names, guests, health details, addresses or dates of private events ("dinner for six with one vegetarian", not who).
- File: `answers/<YYYY-MM-DD>-<short-slug>.md`. Front matter, then an optional Markdown body for anything worth keeping that doesn't fit the fields (how the picks differ, a technique tip).

```markdown
---
question: What should I braise this weekend, Bourdain style?
asked: 2026-11-20
lens: Anthony Bourdain            # leave out when no lens was used
summary: Make the boeuf bourguignon from the Les Halles Cookbook.   # the bottom line, one sentence
picks:                            # best first; every url is a page that was opened
  - title: Boeuf Bourguignon
    source: Les Halles Cookbook, via ...
    url: https://...
    time: 30 min active, 3 hr total
    why: One or two sentences in your own words.
library:                          # optional; only recipes that truly compete
  - slug: osso-buco-style-beef-shank
    why: Where it would rank and why.
---
Optional notes in Markdown.
```

- `python3 scripts/validate.py` (it checks answers too), `python3 scripts/build.py`, commit ("Publish answer: <question>"), push, wait for the deploy, then give the link `<site_url>ask.html#<file name without .md>`, checked live.
- To take an answer down or fix it later, edit or delete the file and push.

## 6. Lenses

`data/taste_lenses.yaml` is the household's running list of cooks and styles they have asked for. When they name someone new ("do it like Marcella Hazan"), use it right away, then add an entry in the same format (`name`, `means` in a sentence, `look_first` sources) and mention that you added it. Commit it with the next push. Durable preferences they state along the way ("we never want cilantro") belong in `house_taste` in `data/site.yaml`; ask before changing that.
