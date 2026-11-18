#!/usr/bin/env python3
"""Report how far the first-time setup of this copy has got, and fill in the YOUR-... placeholders.

    python3 scripts/setup_check.py           # report; exit 1 if a required setting is missing
    python3 scripts/setup_check.py --fill    # also replace YOUR-... placeholders in README.md, CLAUDE.md and docs/
                                             # with the values from data/site.yaml (safe to run again later)

SETUP.md is the procedure Claude follows; this script only checks and fills.
"""
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chef_lib import ROOT, load_site

REQUIRED = [
    ("site_name", "name shown at the top of the site"),
    ("bot_name", "what the household calls Claude here"),
    ("household", "household name used in the docs"),
    ("repo", "GitHub owner/repository"),
    ("site_url", "address of the site"),
    ("lists", "shopping-list names"),
]
ADDONS = [
    ("Google Doc copies of recipes", lambda s: bool(((s.get("google") or {}).get("docs_folder") or {}).get("id"))),
    ("Shared shopping lists (Google Sheet)", lambda s: bool(s.get("lists_api"))),
    ("Recipe inbox: Drive folder", lambda s: bool((s.get("google") or {}).get("inbox_folder_id"))),
    ("Recipe inbox: email address", lambda s: bool(s.get("submission_email"))),
]
FILL_FILES = ["README.md", "CLAUDE.md", "docs"]


def tokens(site):
    repo = (site.get("repo") or "").strip()
    url = (site.get("site_url") or "").strip()
    out = []
    if url:
        out.append(("https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPO/", url.rstrip("/") + "/"))
    if repo:
        out.append(("YOUR-GITHUB-USERNAME/YOUR-REPO", repo))
    for tok, key in (("YOUR-GOOGLE-ACCOUNT", "google_account"), ("YOUR-HOUSEHOLD", "household"), ("YOUR-BOT-NAME", "bot_name")):
        if (site.get(key) or "").strip():
            out.append((tok, site[key].strip()))
    return out


def text_files():
    for name in FILL_FILES:
        p = ROOT / name
        if p.is_file():
            yield p
        elif p.is_dir():
            yield from sorted(p.rglob("*.md"))


def main():
    fill = "--fill" in sys.argv
    site = load_site()
    bad = 0
    print("Required settings (data/site.yaml)")
    for key, what in REQUIRED:
        v = site.get(key)
        ok = bool(v) and v != ["Household"] if key == "lists" else bool(v)
        shown = ", ".join(v) if isinstance(v, list) else (v or "")
        print(f"  {'ok     ' if ok else 'MISSING'} {key}: {shown or '(' + what + ')'}")
        bad += 0 if ok else 1
    repo, url = (site.get("repo") or ""), (site.get("site_url") or "")
    if repo and url and "/" in repo:
        owner, name = repo.split("/", 1)
        want = f"https://{owner.lower()}.github.io/{name}/"
        if url.rstrip("/").lower() + "/" != want.lower():
            print(f"  note    site_url is {url} but a GitHub Pages site for {repo} is normally {want}")
    print("Add-ons")
    for name, test in ADDONS:
        print(f"  {'on ' if test(site) else 'off'}  {name}")
    print(f"setup_done: {bool(site.get('setup_done'))}")

    pairs = tokens(site)
    left = 0
    for p in text_files():
        t = p.read_text(encoding="utf-8")
        new = t
        if fill:
            for tok, val in pairs:
                new = new.replace(tok, val)
            if new != t:
                p.write_text(new, encoding="utf-8")
                print(f"  filled  {p.relative_to(ROOT)}")
        n = len(re.findall(r"YOUR-[A-Z]+(?:-[A-Z]+)*", new))
        if n:
            left += n
            print(f"  {n} placeholder(s) left in {p.relative_to(ROOT)}")
    if left and not fill:
        print("Run with --fill to replace the placeholders from data/site.yaml.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
