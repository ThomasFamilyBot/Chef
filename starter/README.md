# Starter export ("give ChefBot to another household")

Everything needed to hand a clean copy of this project to someone else. None of this folder is exported.

- `export.py` — writes the scrubbed copy and fails if anything of ours is left in it.
- `overlay/` — files laid on top of the copy: blank `data/site.yaml`, sample menu / pairings / staples, the
  starter `README.md`, the people-facing guide `GETTING_STARTED.md`, and a deploy workflow that stays green
  until the new owner switches on GitHub Pages.
- `guide_html.py` — renders `GETTING_STARTED.md` as HTML for a Google Doc.
- `SETUP.md` (repo root) and `scripts/setup_check.py` ship with the copy: they are what the recipient's Claude follows.

## Where the current one lives

- Template repo: https://github.com/ThomasFamilyBot/chefbot-starter (public, marked as a template)
- Demo site built from it: https://thomasfamilybot.github.io/chefbot-starter/
- Guide (Google Doc): see "Guide doc" at the bottom of this file.

## Shipping a fresh one

There is no syncing: recipients keep whatever copy they made. To publish a newer starter:

1. Commit everything here first (the export reads the committed files).
2. `python3 starter/export.py /some/new/empty/dir`. It must end with "scrub: clean". If it reports something,
   fix the source (or add a substitution / exclusion in `export.py`) and run it again. Never hand-edit the output.
3. Read the output's `CLAUDE.md`, `SETUP.md` and `data/site.yaml` once with fresh eyes.
4. Publish: clone `chefbot-starter`, delete everything except `.git`, copy the export in, commit, push.
   Pushing a changed `.github/workflows/deploy.yml` needs a GitHub token with the `workflow` scope.
5. If the guide changed, re-render it (`guide_html.py`) and replace the Google Doc.
6. Dry run: make a repository from the template, switch on Pages, and run SETUP.md against it.

## What to check when the project has changed a lot

- New household-specific values belong in `data/site.yaml`, not in skills, templates or docs. The scrub picks up
  every id, address and link in that file automatically.
- New people's names in recipes, menus or notes: add them to `DENY_WORDS` in `export.py`.
- New binary files (photos) are never exported; the scrub flags any that slip through.
- The five sample recipes are listed in `SAMPLE_RECIPES`.

## Guide doc

"ChefBot: set up your own": https://docs.google.com/document/d/1_RxgX3-mVqsKxdlMdPP7hiZRK2qg7-RdHTTfadEjLz0/edit
Rendered from `overlay/GETTING_STARTED.md` on 2026-11-17. The Drive connector can't replace a Doc's content,
so a changed guide means a new Doc (and a new link to hand out) or editing the Doc in place with the Docs connector.
