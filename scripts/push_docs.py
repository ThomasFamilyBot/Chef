#!/usr/bin/env python3
"""Rewrite recipes' Google Docs in place from the recipe files: same Doc, same link, nothing trashed.

    push_docs.py --stale              every Doc whose rendered page differs from what was last pushed
    push_docs.py <slug> [<slug>...]   these recipes (a recipe with no Doc yet gets one, and its drive_doc_id)
    push_docs.py --all                every recipe that has a Doc
    push_docs.py --dry-run --stale    list what would be pushed; needs no connection
    push_docs.py --setup              one time: give the web app its secret and the folders it may write to
    --force                           overwrite even a Doc someone edited by hand since the last push

Runs on the computer, so no recipe text passes through a Claude session. Talks to the small Apps Script
web app in docs/docs-apps-script.gs (`docs_api` in data/site.yaml; setup in docs/DOCS_API.md). The secret
lives in ~/.config/chefbot/docs_secret, never in the repo. docs/DOC_SYNC.json records what was pushed.
"""
import sys, os, re, json, html, hashlib, secrets, argparse, pathlib, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import yaml
from chef_lib import ROOT, RECIPES, DATA, split_front_matter
from export_gdoc_html import render

STATE = ROOT / "docs" / "DOC_SYNC.json"
SECRET = pathlib.Path.home() / ".config" / "chefbot" / "docs_secret"


def site():
    return yaml.safe_load((DATA / "site.yaml").read_text(encoding="utf-8")) or {}


def folders(s):
    g = s.get("google") or {}
    ids = [(g.get("docs_folder") or {}).get("id")] + [f.get("id") for f in g.get("docs_subfolders") or []]
    return [i for i in ids if i]


def call(api, payload):
    req = urllib.request.Request(api, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:   # Apps Script answers with a redirect; urllib follows it
        body = r.read().decode("utf-8", "replace")
    try:
        return json.loads(body)
    except ValueError:
        return {"ok": False, "error": "not JSON (is the web app deployed for Anyone, and authorized?)", "detail": body[:200]}


def squash(text):
    return re.sub(r"\s+", "", text.replace(" ", ""))


def page_text(page):
    page = re.sub(r"<title>.*?</title>", "", page, flags=re.S)
    return squash(html.unescape(re.sub(r"<[^>]+>", " ", page)))


def front(path):
    return yaml.safe_load(split_front_matter(path.read_text(encoding="utf-8"))[0])


def set_doc_id(path, doc_id):
    text = path.read_text(encoding="utf-8")
    if re.search(r"^drive_doc_id:.*$", text, re.M):
        text = re.sub(r"^drive_doc_id:.*$", f"drive_doc_id: {doc_id}", text, count=1, flags=re.M)
    else:
        text = text.replace("\ningredients:\n", f"\ndrive_doc_id: {doc_id}\ningredients:\n", 1)
    path.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*")
    for flag in ("--stale", "--all", "--dry-run", "--force", "--setup"):
        ap.add_argument(flag, action="store_true")
    ap.add_argument("--folder-id", help="folder for a new Doc (default: google.docs_folder)")
    a = ap.parse_args()
    s = site()
    api = s.get("docs_api") or ""
    if not api and not a.dry_run:
        sys.exit("docs_api is not set in data/site.yaml. Follow docs/DOCS_API.md, or use the drive-export skill's other routes.")

    if a.setup:
        if not SECRET.exists():
            SECRET.parent.mkdir(parents=True, exist_ok=True)
            SECRET.write_text(secrets.token_urlsafe(48))
            SECRET.chmod(0o600)
        r = call(api, {"action": "claim", "secret": SECRET.read_text().strip(), "folders": folders(s)})
        print("claimed: this computer now holds the web app's secret" if r.get("ok") else f"not claimed: {r.get('error')}")
        return 0 if r.get("ok") else 1

    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    if a.slugs:
        paths = [RECIPES / f"{x}.md" for x in a.slugs]
    elif a.stale or a.all:
        paths = sorted(RECIPES.glob("*.md"))
    else:
        ap.error("name recipes, or use --stale or --all")
    key = SECRET.read_text().strip() if SECRET.exists() else ""
    if not key and not a.dry_run:
        sys.exit("No secret on this computer. Run: python3 scripts/push_docs.py --setup")

    done, skipped, failed = [], [], []
    for p in paths:
        slug, r = p.stem, front(p)
        doc_id = r.get("drive_doc_id")
        if not doc_id and not a.slugs:
            continue                                    # bulk runs never create Docs
        page = render(p)
        sha = hashlib.sha256(page.encode()).hexdigest()
        rec = state.get(slug) or {}
        if not a.slugs and not a.all and rec.get("doc") == doc_id and rec.get("sha") == sha:
            continue                                    # --stale: already current
        if a.dry_run:
            done.append(slug)
            continue
        if doc_id:
            last = rec.get("pushed") if rec.get("doc") == doc_id else None
            res = call(api, {"secret": key, "action": "replace", "id": doc_id, "html": page, "title": r["title"],
                             "lastPushed": last, "force": a.force})
        else:
            res = call(api, {"secret": key, "action": "create", "html": page, "title": r["title"],
                             "folder": a.folder_id or folders(s)[0]})
            if res.get("ok"):
                doc_id = res["id"]
                set_doc_id(p, doc_id)
        if not res.get("ok"):
            (skipped if res.get("error") == "edited" else failed).append(f"{slug}: {res.get('error')} {res.get('detail', '')}".strip())
            continue
        if "text" in res and squash(res["text"]) != page_text(page):
            failed.append(f"{slug}: pushed, but the Doc's text does not match the page; look at it before trusting it")
            continue
        state[slug] = {"doc": doc_id, "sha": sha, "pushed": res["modifiedTime"], "method": res.get("method")}
        STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
        done.append(slug)

    verb = "would push" if a.dry_run else "pushed"
    print(f"{verb} {len(done)}" + (": " + ", ".join(done) if len(done) <= 12 else ""))
    if skipped:
        print(f"skipped {len(skipped)} edited by hand since the last push (sync them into the recipe with drive-sync, or --force):")
        print("\n".join("  " + x for x in skipped))
    if failed:
        print(f"FAILED {len(failed)}:")
        print("\n".join("  " + x for x in failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
