# Recipe Google Docs, rewritten in place

`scripts/push_docs.py` keeps every recipe's Google Doc in step with its recipe file. It rewrites the Doc that already exists, so **the link never changes and nothing goes to the trash**, and it runs on the computer, so one command covers one recipe or the whole library. It works through a small Apps Script web app, the same way the shared shopping lists do.

## One-time setup (about five minutes)

Do all of this signed in to Google as the account that owns the recipe Docs (`google_account` in `data/site.yaml`).

1. Go to https://script.new. Name the project **ChefBot Docs**.
2. Delete the sample code, paste the contents of `docs/docs-apps-script.gs`, press Save.
3. In the left bar, press **+** next to **Services**, pick **Drive API**, press **Add**.
4. **Deploy → New deployment**. Click the gear next to "Select type" and choose **Web app**. Execute as: **Me**. Who has access: **Anyone**. Press **Deploy** and approve the permissions it asks for (it needs to see and edit Drive files and Docs).
5. Copy the web app URL and give it to Claude ("the docs API URL is …").

Claude then puts the URL in `data/site.yaml` as `docs_api` and runs, on the computer:

```bash
python3 scripts/push_docs.py --setup          # hands the web app a secret and the recipe folders, once
python3 scripts/push_docs.py <one-slug>       # test on one recipe, then open that Doc and look at it
python3 scripts/push_docs.py --stale          # bring every Doc up to date
```

To change the script later: edit it, then **Deploy → Manage deployments → edit → Version: New version → Deploy**. The URL stays the same.

## What keeps it safe

- "Anyone" can reach the URL, but every request must carry a secret. The secret is made on the computer by `--setup`, kept in `~/.config/chefbot/docs_secret`, and never written to the repo or shown in a chat. The web app accepts a secret only once; to start over, delete the `SECRET` and `FOLDERS` script properties (Project Settings) and run `--setup` again.
- The web app only touches Google Docs that sit in the recipe folders named in `data/site.yaml` (`google.docs_folder` and `docs_subfolders`).
- It will not overwrite a Doc someone has edited by hand since the last push. Those are listed as skipped: bring the edit into the recipe first (`drive-sync` skill), or pass `--force`.
- After each push it reads the Doc back and compares the text with the page it sent. A mismatch is reported as a failure.

## How it behaves

- `docs/DOC_SYNC.json` records, per recipe, which Doc was written and a fingerprint of the page. `--stale` pushes only recipes whose page has changed since, so it is safe to run after every change.
- A recipe named on the command line that has no Doc yet gets one, in the main recipes folder (or `--folder-id`), and its `drive_doc_id` is written into the recipe file.
- About 3 seconds per Doc; the whole library takes roughly ten minutes.
- Untested until the first household sets it up: the web app first asks Drive to convert the page straight over the existing Doc, and if Drive refuses, it copies the content in from a scratch Doc instead. `DOC_SYNC.json` records which method each Doc used.
