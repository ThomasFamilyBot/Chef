#!/usr/bin/env python3
"""Export a clean starter copy of this project for another household.

    python3 starter/export.py <empty-or-new-output-dir>

What it does (see starter/README.md for the whole procedure, including publishing):
  1. copies the tracked files at HEAD, minus everything household-specific;
  2. keeps only the sample recipes listed in SAMPLE_RECIPES, without their Google Doc ids;
  3. replaces our names, addresses and repo with YOUR-... placeholders (scripts/setup_check.py --fill
     puts the new household's values in);
  4. swaps the "This household" block in CLAUDE.md for a "not set up yet" notice;
  5. lays starter/overlay/ on top (blank data/site.yaml, sample menu and template, README, guide);
  6. validates and builds the copy;
  7. scans every file for anything of ours that is left and fails if it finds one.

Nothing is pushed anywhere. The output directory is a plain folder, with no git history.
"""
import re, subprocess, sys, shutil, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "starter" / "overlay"

SAMPLE_RECIPES = [
    "cauliflower-soup",
    "a-very-good-lasagna",
    "beef-suya",
    "california-pizza-kitchen-thai-crunch",
    "shakshuka",
]

# Tracked paths that never go into the starter (prefix match). Overlay files replace some of them.
EXCLUDE = [
    "starter/", "recipes/", "README.md", "data/site.yaml", "data/menus.yaml", "data/pairings.yaml",
    "data/items.yaml", "data/shopping_templates/", "site/static/items/", "docs/DOC_MAP.md",
    "docs/DRIVE_TRASH_LOG.md",
]
# Recipe front-matter keys that point at our Google Drive.
STRIP_RECIPE_KEYS = ("drive_doc_id", "source_doc")

TEXT_EXT = {".md", ".py", ".yaml", ".yml", ".csv", ".html", ".js", ".css", ".json", ".sh", ".gs", ".svg", ".txt", ""}

# Extra words that must never appear in an export (first names of family and friends, employers, schools).
# The list names, emails and ids in data/site.yaml and every recipe's Google Doc id are added automatically.
DENY_WORDS = ["ahin", "jenn", "andrea", "thomas", "pathstone", "quaker", "deepa", "sffs"]
DENY_PATTERNS = [
    r"docs\.google\.com/document/d/[\w-]{15,}",
    r"drive\.google\.com/drive/folders/[\w-]{15,}",
    r"script\.google\.com/macros/s/[\w-]{15,}",
    r"[\w.+-]+@gmail\.com",
    r"Label_\d+",
]
# Allowed even though a deny rule matches (generic examples inside the docs).
ALLOW = [r"name\+recipes@gmail\.com", r"maplestreetkitchen@gmail\.com",
         r"github\.com/ThomasFamilyBot/chefbot-starter", r"thomasfamilybot\.github\.io/chefbot-starter",
         r"Copyright \(c\) \d{4} ThomasFamilyBot"]   # where the starter itself lives


def sh(*cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout


def our_values():
    """Literal strings of ours, read from the live settings and recipes."""
    site = yaml.safe_load((ROOT / "data" / "site.yaml").read_text())
    vals = set()

    def walk(v):
        if isinstance(v, dict):
            [walk(x) for x in v.values()]
        elif isinstance(v, list):
            [walk(x) for x in v]
        elif isinstance(v, str) and (re.fullmatch(r"[\w-]{20,}", v) or "@" in v or v.startswith("http")):
            vals.add(v)
    walk(site)
    for p in (ROOT / "recipes").glob("*.md"):
        for m in re.finditer(r"^(?:drive_doc_id|source_doc):\s*(\S+)", p.read_text(), re.M):
            if m.group(1) not in ("null", "~", '""'):
                vals.add(m.group(1))
    return site, vals


def substitutions(site):
    owner, name = site["repo"].split("/", 1)
    subs = [
        (re.compile(r"https://%s\.github\.io/%s/?" % (re.escape(owner), re.escape(name)), re.I), "https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPO/"),
        (re.compile(r"%s/%s\b" % (re.escape(owner), re.escape(name)), re.I), "YOUR-GITHUB-USERNAME/YOUR-REPO"),
        (re.compile(re.escape(site["google_account"]), re.I), "YOUR-GOOGLE-ACCOUNT"),
        (re.compile(re.escape(", ".join(site["lists"]))), "Sam, Alex, Jordan"),
    ]
    hh = site["household"]                       # "the Thomas family"
    bare = re.sub(r"^the\s+", "", hh, flags=re.I)
    subs.append((re.compile(r"\b(?:the\s+)?%s\b" % re.escape(bare), re.I), "YOUR-HOUSEHOLD"))
    return subs


def is_text(p):
    return p.suffix.lower() in TEXT_EXT


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = pathlib.Path(sys.argv[1]).resolve()
    if out.exists() and any(out.iterdir()):
        sys.exit(f"{out} is not empty; give a new or empty directory")
    if sh("git", "status", "--porcelain").strip():
        print("WARNING: uncommitted changes; the export uses the committed files (HEAD), not your working copy.")
    out.mkdir(parents=True, exist_ok=True)
    site, vals = our_values()
    subs = substitutions(site)

    # 1-2. tracked files, minus exclusions, plus the sample recipes
    tracked = sh("git", "ls-files").splitlines()
    keep = [f for f in tracked if not any(f.startswith(e) for e in EXCLUDE)]
    for slug in SAMPLE_RECIPES:
        f = f"recipes/{slug}.md"
        if f not in tracked:
            sys.exit(f"sample recipe missing: {f}")
        keep.append(f)
    for f in keep:
        dst = out / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = subprocess.run(["git", "show", f"HEAD:{f}"], cwd=ROOT, check=True, capture_output=True).stdout
        dst.write_bytes(data)
    (out / "site" / "static" / "items").mkdir(parents=True, exist_ok=True)
    (out / "site" / "static" / "items" / ".gitkeep").write_text("")

    # 2. recipes: drop Google Doc pointers
    for slug in SAMPLE_RECIPES:
        p = out / "recipes" / f"{slug}.md"
        lines = [l for l in p.read_text().splitlines(keepends=True) if not l.startswith(tuple(k + ":" for k in STRIP_RECIPE_KEYS))]
        p.write_text("".join(lines))

    # 4. CLAUDE.md household block
    c = out / "CLAUDE.md"
    t = c.read_text()
    a, b = t.index("<!-- household:start -->"), t.index("<!-- household:end -->")
    t = t[:a] + """<!-- household:start -->
## This household

> **NOT SET UP YET.** `setup_done` is `false` in `data/site.yaml`. Before doing anything else in this
> repository, whatever the person's first message says, open `SETUP.md` and follow it. Setup replaces this block.
""" + t[b:]
    c.write_text(t)

    # 3. placeholders
    for p in out.rglob("*"):
        if p.is_file() and is_text(p):
            t = p.read_text(encoding="utf-8")
            new = t
            for rx, rep in subs:
                new = rx.sub(rep, new)
            if new != t:
                p.write_text(new, encoding="utf-8")

    # 5. overlay
    for p in OVERLAY.rglob("*"):
        if p.is_file() and p.name != ".DS_Store":
            dst = out / p.relative_to(OVERLAY)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dst)

    # 6. the copy must validate and build on its own
    for script in ("validate.py", "build.py"):
        r = subprocess.run([sys.executable, f"scripts/{script}"], cwd=out, capture_output=True, text=True)
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:]
        print(f"{script}: {' '.join(tail)}")
        if r.returncode:
            sys.exit(r.stdout + r.stderr)
    built = out / "dist"
    pages = len(list((built / "r").glob("*.html")))
    shutil.rmtree(built)
    for d in out.rglob("__pycache__"):
        shutil.rmtree(d)

    # 7. scrub: nothing of ours may be left
    deny = [re.compile(r"\b%s" % re.escape(w), re.I) for w in DENY_WORDS + [n for n in site["lists"]]]
    deny += [re.compile(p) for p in DENY_PATTERNS]
    allow = [re.compile(p) for p in ALLOW]
    hits = []
    for p in sorted(out.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(out)
        if not is_text(p):
            if p.name != ".gitkeep":
                hits.append(f"{rel}: binary file (photos and other binaries are not exported; check it)")
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            clean = line
            for a in allow:
                clean = a.sub("", clean)
            for v in vals:
                if v in clean:
                    hits.append(f"{rel}:{n}: our value {v[:40]}")
            for rx in deny:
                m = rx.search(clean)
                if m:
                    hits.append(f"{rel}:{n}: {m.group(0)!r} in: {line.strip()[:110]}")
    files = sum(1 for p in out.rglob("*") if p.is_file())
    print(f"exported {files} files, {len(SAMPLE_RECIPES)} sample recipes ({pages} recipe pages built) -> {out}")
    if hits:
        print(f"\nSCRUB FAILED: {len(hits)} thing(s) of ours are still in the export:")
        print("\n".join(hits[:80]))
        sys.exit(2)
    print("scrub: clean (no names, addresses, Google ids or links of ours)")


if __name__ == "__main__":
    main()
