# First-time setup (instructions for Claude)

You are setting up a brand-new copy of this recipe project for a household. Follow this file when
`setup_done` is `false` in `data/site.yaml`, or when someone asks to set up or re-run an add-on.
The person you are talking to has probably never used GitHub, a terminal, or a code editor.

## How to behave during setup

- **One question at a time.** Wait for the answer. Offer a default they can accept by saying "yes".
- Plain words. Say "your recipe site", not "the Pages deployment". Never show a command and expect them to run it; you run things, they click things in a browser.
- When they must click through a website, give numbered steps, one screen at a time, and ask them to tell you what they see if it doesn't match. Menus move; adapt.
- **Never ask for a password, a verification code, or a card number**, and never type one for them.
- **Everything in this project is public**: the site and every file in the repository can be seen by anyone with the link. Say this once, early. Use first names or nicknames only; no surnames, home addresses, phone numbers or children's full names anywhere in the files.
- Start by running `python3 scripts/setup_check.py` to see what is already done. Resume where it left off; don't re-ask what is already filled in.
- Install the build tools once per session: `pip install pyyaml markdown jinja2`.

## Part 1: the core (required, about ten minutes)

### 1. Work out where you are

Run `git remote get-url origin`. The address ends in `<owner>/<repository>`; that is `repo`.
The site address is `https://<owner in lowercase>.github.io/<repository>/`. Tell the person both and confirm that this is the GitHub account they just made.

### 2. Ask for the names

Ask these, one at a time, and write the answers into `data/site.yaml`:

1. **Household name**, as it should read in a sentence: "the Rivera household", "Sam and Alex's kitchen". Goes in `household`.
2. **What they want to call you** in this project: default "ChefBot". Goes in `bot_name`.
3. **The name at the top of the site**: default "Chef". Short is better; it sits in the menu bar. Goes in `site_name`.
4. **Who shops.** Each adult (or anyone who will carry a shopping list) gets their own list on the site. Ask for the first names or nicknames, in the order they should appear. Remind them these names are visible on the public site. One name is fine. Goes in `lists`.
5. **What they like to cook and eat**, in a sentence or two (cuisines, diets, equipment such as a smoker or an air fryer, how much weekday time they have). Goes in `house_taste`; it steers recipe suggestions and menus. They can skip it.
6. **Which Google account** will own the optional Google pieces (Google Docs of recipes, the shared shopping-list sheet, the recipe inbox). It should be the same Google account their Claude connectors use. If they don't want any Google add-ons, leave `google_account` empty.

### 3. Starter content

The copy comes with five sample recipes, one sample menu and a sample "House Staples" shopping template so the site isn't empty.

- Ask whether to **keep the sample recipes** (recommended until they have a few of their own) or remove them. If removing, delete the files in `recipes/`, and empty `data/menus.yaml` and `data/pairings.yaml` down to `[]`, then run `python3 scripts/validate.py`.
- Ask what they always keep in the house (eggs, milk, coffee…) and rewrite `data/shopping_templates/house-staples.yaml` with their items, in the same format. They can do this later.

### 4. Write it down

1. Fill `repo`, `site_url` and the answers into `data/site.yaml`. Keep the comments.
2. In `CLAUDE.md`, replace everything between `<!-- household:start -->` and `<!-- household:end -->` (keep the two marker lines) with:

   ```markdown
   ## This household

   - **Household:** <household>. They call this project, and Claude when working in it, **<bot_name>**.
   - **Repo:** `<repo>` · **Site:** <site_url>
   - **Google account that owns everything:** <google_account, or "none yet">.
   - Every other household-specific value (list names, Drive folder ids, Gmail label ids, the lists web-app URL, house taste) is in `data/site.yaml`. Read it at the start of any task that touches Google, the site link, or shopping lists.
   ```
3. Run `python3 scripts/setup_check.py --fill`. It replaces the `YOUR-…` placeholders in `README.md` and `docs/` with the real values. (`YOUR-GOOGLE-ACCOUNT` stays until a Google account is set; that is fine.)
4. `python3 scripts/validate.py && python3 scripts/build.py`. Fix anything they report.
5. Commit ("Set up <site_name> for <household>") and push to `main`.

### 5. Check the site is live

The push starts a build on GitHub that publishes the site a minute or two later.

1. If `gh` works in this session, `gh run list --limit 1` until it says completed. Otherwise fetch `<site_url>recipes.json` every 30 seconds for up to five minutes.
2. **If the site answers** (HTTP 200) and shows their site name: give them the link and ask them to open it on their phone.
3. **If it is still "404 / not found" after five minutes** (or the build finished with the notice "The website is not switched on yet"), the website switch is off. Walk them through it: on github.com open the repository → **Settings** (top row of tabs; under the "…" menu on a phone) → **Pages** (left column) → under "Build and deployment", **Source: GitHub Actions**. Nothing to save. Then make a small commit and push again (for example, re-run the build so `docs/DOC_MAP.md` updates) and re-check.
4. If the build itself failed, read the log (`gh run view <id> --log-failed`, or ask them to open the **Actions** tab and tell you the red step) and fix it.
5. Suggest **Add to Home Screen** (iPhone: Share → Add to Home Screen; Android: ⋮ → Add to Home screen) so the site opens like an app.

### 6. First recipe

Ask for a recipe they actually cook: a link, a photo of a cookbook page or a card, or pasted text. Add it with the `recipe-intake` skill so they see the whole loop (recipe page, nutrition, shopping list). If Google Docs aren't set up yet, skip the Google Doc step and say so.

If the nutrition step can't download the USDA data (`bash scripts/usda_fetch.sh` is refused by the network), this session's environment doesn't allow the host `fdc.nal.usda.gov`. Ask to have it added: propose the change yourself if you have a tool for editing the environment, otherwise tell the person to open the environment's settings in Claude Code on the web and add that host under network access. Until then, compute nutrition from the foods already in `data/canonical_ingredients.csv` and say which ingredients are still missing.

### 7. Mark the core done

Set `setup_done: true` in `data/site.yaml`, commit, push. Then list the add-ons below with one line each and ask which they want now. Each can be added any time later by saying "set up the … add-on".

## Part 2: add-ons (each optional)

All three need Google connectors turned on in Claude (claude.ai → Settings → Connectors): **Google Drive** for A, B and C, and **Gmail** for C. If a connector is missing, tell them which one to connect and wait. Every Google step is done signed in as `google_account`; say so each time.

### A. Google Doc copies of every recipe (5 minutes)

Each recipe also gets a clean, printable Google Doc. The household can edit the Doc and say "doc updated, update the app".

1. Ask what the Drive folder should be called (default "Recipes"). Create it with the Drive connector if it can create folders; otherwise ask them to make it at drive.google.com (New → New folder), open it, and paste the address from the browser. The folder id is the last part of that address.
2. Write it to `google.docs_folder` in `data/site.yaml` as `{name: <name>, id: <id>}`.
3. Export one recipe with the `drive-export` skill, give them the Doc link, and ask if it looks right. Then offer to export the rest.

### B. Shared shopping lists (10 minutes)

Without this, each phone keeps its own copy of the lists. With it, everyone sees the same lists, stored in a Google Sheet they own. The steps are in `docs/SHARED_LISTS.md`; walk them through it:

1. They create a blank Google Sheet (sheets.new) named "Chef Shopping Lists".
2. In the sheet: **Extensions → Apps Script**. Delete what is there. Show them the full contents of `docs/lists-apps-script.gs` in a code block to copy and paste in. Save.
3. **Deploy → New deployment** → gear → **Web app** → Execute as: **Me**; Who has access: **Anyone** → Deploy. Google asks them to authorize; on the "Google hasn't verified this app" screen they choose **Advanced → Go to (project name)**. Explain that this is their own script and it can only touch this one sheet.
4. They paste you the **Web app URL** (ends in `/exec`). Put it in `lists_api`. Check it yourself: fetching `<url>?list=<first list name>` should return JSON containing `"ok":true`.
5. Build, commit, push, wait for the deploy, and have them tick something on one phone and watch it appear on another.

Tell them once: the web-app address is part of the public site, so someone who went looking could read or change the shopping lists. It holds nothing but groceries.

### C. Recipe inbox for friends (15 minutes)

Friends email a recipe link or drop a photo in a shared folder; on a schedule you turn each into a recipe and reply with the links.

1. **Drive folder.** Create a folder "Chef Inbox" with a sub-folder "Processed" (connector, or they create both and paste the addresses). Record `google.inbox_folder_id`, `google.inbox_processed_folder_id` and `inbox_folder_url`. They share the Chef Inbox folder with the friends who will send recipes, as **Editor** so friends can add files (Share → add people; or "Anyone with the link → Editor" if they accept that anyone holding the link can add files).
2. **Email address.** Ask which they prefer:
   - *A dedicated address* (recommended; it will be printed on the public site): they create a new free Gmail account for recipes, then in that account: gear → See all settings → **Forwarding and POP/IMAP** → Add a forwarding address → their main address → confirm with the code Google sends → choose "Forward a copy of incoming mail".
   - *No new account*: use their main address with `+recipes` before the @ (`name+recipes@gmail.com`). It works immediately but shows their real address on the public site.
   Put the address in `submission_email`. That turns on the site's **Send a recipe** page.
3. **Labels.** With the Gmail connector create the labels `Chef/Done` and `Chef/Waiting`; record their ids in `google.gmail_label_done_id` and `google.gmail_label_waiting_id`.
4. **Summary address.** Ask where the after-run summary should go (default `google_account`); put it in `summary_email`.
5. Build, commit, push. Send a test: ask them to email a recipe link to the new address, then run the `inbox-processing` skill once while they watch.
6. **Schedule.** Offer a daily run. If you have a tool for scheduled tasks, create one that starts a fresh session on this repository each day with the prompt "Process the recipe inbox: follow .claude/skills/inbox-processing/SKILL.md", with the Gmail and Google Drive connectors attached, at a time they choose. Otherwise tell them how to create it in Claude Code on the web (scheduled tasks / routines) with that prompt. Without a schedule, "process the recipe inbox" on request still works.

### D. Small extras (mention, don't push)

- **Item photos.** They can send a photo of a product ("this is the yogurt we buy") and it becomes a tap-to-see card on the shopping list. See "item photos" in `CLAUDE.md`. Remind them the photo will be public.
- **Other people in the household.** Anyone who should be able to add recipes needs a Claude session with this repository. Simplest: use the same Claude account. Otherwise they make their own GitHub account and the owner invites them (repository → Settings → Collaborators → Add people), then they connect their Claude to GitHub the same way.
- **From a phone.** The Claude phone app can start a Claude Code session on this repository: pick the repository, then talk or send a photo of a recipe.
- **Store layout.** `data/store_sections.yaml` is the order the shopping list is grouped in. "Put Produce last" or "add a Bulk Bins section" is a one-line request.

## When everything they wanted is done

Run `python3 scripts/setup_check.py` one last time and give them a short summary: the site link, what you are called, what is switched on, what is off and how to ask for it later, and three things to try ("Add this recipe: <link>", "Plan a dinner for six on Saturday", "What's on my shopping list template?"). `docs/HOW_TO_USE.md` is the longer guide.
