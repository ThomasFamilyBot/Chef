#!/usr/bin/env python3
"""Set a per-ingredient nutrition override in a recipe file, preserving the rest of the front matter.
Usage: set_override.py <slug> "<item name>" exclude
       set_override.py <slug> "<item name>" fraction=0.1 "note text"
       set_override.py <slug> "<item name>" oz=12 "note text"
       set_override.py <slug> "<item name>" clear
Matches every ingredient line with that item (add --group "<mise group>" to narrow)."""
import sys, re, pathlib, argparse, yaml
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chef_lib import RECIPES, split_front_matter

ap = argparse.ArgumentParser(); ap.add_argument("slug"); ap.add_argument("item"); ap.add_argument("what"); ap.add_argument("note", nargs="?", default="")
ap.add_argument("--group", default=None); ap.add_argument("--prep-contains", default=None)
a = ap.parse_args()
path = RECIPES / f"{a.slug}.md"
text = path.read_text(encoding="utf-8"); fm, body = split_front_matter(text)
meta = yaml.safe_load(fm)
hit = 0
for ing in meta["ingredients"]:
    if ing["item"].lower() != a.item.lower(): continue
    if a.group is not None and (ing.get("group") or "") != a.group: continue
    if a.prep_contains and a.prep_contains.lower() not in (ing.get("prep") or "").lower(): continue
    if a.what == "exclude": ing["nutrition"] = "exclude"
    elif a.what == "clear": ing.pop("nutrition", None)
    else:
        k, v = a.what.split("=", 1); ing["nutrition"] = {k: float(v), "note": a.note}
    hit += 1
if not hit: sys.exit(f"no ingredient {a.item!r} in {a.slug}")
m = re.search(r"(?ms)^ingredients:\n(.*?)(?=^[a-z_]+:)", fm + "\n")
dumped = yaml.safe_dump(meta["ingredients"], sort_keys=False, allow_unicode=True, width=120).rstrip("\n")
dumped = "\n".join(("  " + l if l else l) for l in dumped.split("\n")) + "\n"
fm2 = (fm + "\n")[:m.start(1)] + dumped + (fm + "\n")[m.end(1):]
path.write_text(f"---\n{fm2.rstrip(chr(10))}\n---\n{body}", encoding="utf-8")
print(f"{a.slug}: {hit} line(s) set")
