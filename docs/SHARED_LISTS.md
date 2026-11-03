# Shared shopping lists (one per person, visible from every phone)

Lists are stored in a Google Sheet in the family Drive through a small Apps Script web app. Free, no server, data visible in the sheet.

## One-time setup (about five minutes)

Do all of this signed in to Google as **ahinthomas@gmail.com**, the account that owns the sheet.

1. Open the Google Sheet **Chef Shopping Lists** in Drive (Claude creates it; or make any blank sheet).
2. **Extensions → Apps Script**. Delete the sample code, paste the contents of `docs/lists-apps-script.gs`, press Save.
3. **Deploy → New deployment**. Click the gear next to "Select type" and choose **Web app**. Description: "Chef lists". Execute as: **Me** (ahinthomas@gmail.com). Who has access: **Anyone**. Press **Deploy**, authorize when asked (it only touches this sheet), then copy the **Web app URL** (ends in `/exec`).
4. Give that URL to Claude ("the lists API URL is …"), or put it in `data/site.yaml` as `lists_api`. The names on the list switch come from `lists:` in the same file.

To change the script later: edit it, then **Deploy → Manage deployments → edit → Version: New version → Deploy**. The URL stays the same.

## How it behaves

- The shopping page shows a switch with one button per name. The chosen list is remembered on that phone.
- Changes save about a second after you make them. Other phones pick them up within ~15 seconds while the page is open, and on every page load.
- If the sheet can't be reached, the page keeps working from the phone's local copy and syncs when it can. The status line under the switch says which.
- "Last write wins" per list: if two phones change the same list within the same second, the later save wins and the other phone refreshes to match.
- Share links still work for handing a snapshot to someone outside the household.
