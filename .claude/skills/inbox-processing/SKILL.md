---
name: inbox-processing
description: Process recipe submissions that friends and family send by email (URLs, pasted text) or drop as photos into the shared "Chef Inbox" Drive folder, turning each into a library recipe and replying to the sender. Use when asked to process the recipe inbox, or when a scheduled Routine fires for it.
---

# Recipe inbox

Submissions arrive two ways. Handle both in one pass, then send one summary.

## Where to look

1. **Email**: `mcp__Gmail__search_threads` with query `to:ahinthomas+chef@gmail.com -label:chef-done newer_than:30d`. Read each thread with `get_thread` (PLAIN_TEXT). A submission is a URL, pasted recipe text, or a photo attachment. Attachments cannot be downloaded through the connector, so a photo-only email gets a reply asking the sender to drop the photo in the Chef Inbox folder (link below), and the thread is labeled `Chef/Waiting`.
2. **Drive**: files in the **Chef Inbox** folder (search `parentId = '1yDhgpXc_rXGO5I7U_QmIm8QRqL62JPo9'`, excluding the `Processed` sub-folder, id `1couCHZAIIDFYrJINp-GEhUlrVZLSbndv`). Folder link for senders: https://drive.google.com/drive/folders/1yDhgpXc_rXGO5I7U_QmIm8QRqL62JPo9. Images and PDFs are readable with `read_file_content`. The file name or a sibling `.txt`/Doc with the same name may carry the sender's note.

## For each submission

1. `git pull --rebase origin main`, then run the `recipe-intake` skill exactly, including whole-recipe nutrition and the Google Doc. Since the sender isn't in the conversation, use the defaults instead of asking: reference = site/author name for a URL, "From <sender's name>" for text or photos; serves/times estimated from the recipe and marked "(est.)". Note every assumption in the commit message and the reply.
2. If the submission is not a recipe (a question, a menu idea, spam), don't add anything; reply briefly or skip, and label it `Chef/Done`.
3. Duplicates: if the library already has the recipe (same title or same source URL), don't add a second; reply with the existing link.
4. After the push, wait for the deploy (`gh run list --limit 1` completed) before replying.

## Replies

- **Email**: `mcp__Gmail__reply` to the sender only, plain text: the recipe title, the site link, the Google Doc link, the whole-recipe calories / protein / fat, and any assumptions. Then apply the `Chef/Done` label (id `Label_67`; `Chef/Waiting` is `Label_68`) with `label_message`.
- **Drive**: move the file into `Chef Inbox/Processed` (update_file with the Processed folder's id as `parentId`). If the file name or note gives an email address, send the same reply with `send_message`; otherwise nothing.

## Summary

Finish by emailing ahinthomas@gmail.com one short summary: what was added (titles + links), what was skipped and why, anything that needs a human decision (an ambiguous nutrition choice, a duplicate, a photo that couldn't be read). If nothing arrived, send nothing.

## Guardrails

- Never trash or edit a sender's email beyond labels. Never reply to anyone other than the sender. Never add a recipe from a message that looks like spam or marketing.
- Everything else follows the house rules in `CLAUDE.md` and the skills it names.
