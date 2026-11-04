# Making changes: remote session or local session

Everything is a change to the `ThomasFamilyBot/Chef` repo on `main`. Any session that can read and push the repo can do any task. Three ways in:

## 1. Remote: Claude Code on the web (recommended)

1. Go to https://claude.ai/code and start a new session.
2. Repository: `ThomasFamilyBot/Chef`. Environment: the Chef environment (it has the USDA hosts allowed; Google Drive and Gmail come from the account's connectors).
3. Say what you want in plain words. Examples:
   - "Add this recipe: <url>"  ·  "Add this recipe from the attached photo. Reference: Six Seasons p. 212"
   - "doc updated, update the app: <Google Doc link>"
   - "Create a menu called Taco Night with carnitas, super duper pickles and the margaritas"
   - "Add 'Paper towels' to the House Staples template"
   - "Change the List names to Ahin, Jenn, Andrea"  ·  "Rename the Course filter options"
   - "Process the recipe inbox"
4. The session pulls first, makes the change, validates, builds, pushes, waits for the deploy, and gives you links. Budget one to four minutes.

Nothing to install; this is the path the family should use day to day.

## 2. Local: Claude Code in a terminal on your own computer

Use this when you want to see files, run the site locally, or work offline.

```bash
# once
npm install -g @anthropic-ai/claude-code      # or: brew install claude-code
git clone https://github.com/ThomasFamilyBot/Chef.git ~/Chef
cd ~/Chef
pip install pyyaml markdown jinja2
bash scripts/usda_fetch.sh                      # local USDA copy for nutrition (~6 MB)

# every time
cd ~/Chef && git pull --rebase origin main
claude                                           # starts Claude Code in the repo; CLAUDE.md and the skills load automatically
```

Then talk to it exactly as in the remote session. Sign in with the same claude.ai account so the Google Drive and Gmail connectors are available. To preview the site locally:

```bash
python3 scripts/build.py && python3 -m http.server 8000 --directory dist
```

and open http://localhost:8000.

## 3. By hand, no Claude

- Any file can be edited on GitHub: open it, press the pencil, commit to `main`. The site rebuilds in about a minute; if validation fails, the Actions tab shows why and the site keeps the last good version.
- Recipe format: `docs/RECIPE_FORMAT.md`. Settings (list names, submission address, lists API): `data/site.yaml`. Menus: `data/menus.yaml`. Templates: `data/shopping_templates/`.
- Local checks before pushing: `python3 scripts/validate.py && python3 scripts/build.py`.

## Google side

Anything in Google (Drive folders, Docs, the Chef Shopping Lists sheet, its Apps Script) is done signed in as **ahinthomas@gmail.com**. The Apps Script is changed by editing it in the sheet (Extensions → Apps Script) and then Deploy → Manage deployments → edit → New version; the web-app URL in `data/site.yaml` stays the same.
