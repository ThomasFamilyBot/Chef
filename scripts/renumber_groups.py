#!/usr/bin/env python3
"""Make mise-group numbers consecutive (1..N in order of first use) and strip step numbers from
direction headings, keeping group names and body references in sync. Usage: renumber_groups.py [slugs...]"""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chef_lib import RECIPES, split_front_matter

TOKEN = re.compile(r"(\d+)\s*->\s*")


def renumber(path):
    text = path.read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    # group strings are the only front-matter lines containing "->"
    nums = []
    for ln in fm.split("\n"):
        if ln.strip().startswith("group:"):
            nums += [int(n) for n in TOKEN.findall(ln)]
    if not nums:
        return False
    order = sorted(set(nums))
    mapping = {old: i + 1 for i, old in enumerate(order)}
    if mapping == {n: n for n in order} and not re.search(r"^\*\*\d+\.\s", body, re.M):
        return False

    def sub_tok(m):
        return f"{mapping.get(int(m.group(1)), int(m.group(1)))} -> "

    fm2 = "\n".join(TOKEN.sub(sub_tok, ln) if ln.strip().startswith("group:") else ln for ln in fm.split("\n"))
    body2 = TOKEN.sub(sub_tok, body)                       # body references like `3 -> Honey butter`
    body2 = re.sub(r"^(\*\*)(\d+)\.\s+", r"\1", body2, flags=re.M)   # **3. Honey butter** -> **Honey butter**
    path.write_text(f"---\n{fm2}\n---\n{body2}", encoding="utf-8")
    return True


if __name__ == "__main__":
    paths = [RECIPES / f"{s}.md" for s in sys.argv[1:]] or sorted(RECIPES.glob("*.md"))
    n = sum(renumber(p) for p in paths)
    print(f"{n} of {len(paths)} recipes renumbered")
