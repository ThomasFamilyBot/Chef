#!/usr/bin/env python3
"""Make mise-group ("bowl") numbers consecutive, 1..N in order of first use, one name per number,
and strip step numbers from direction headings. Group names and body references stay in sync.
Usage: renumber_groups.py [slugs...]   (default: every recipe)"""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chef_lib import RECIPES, split_front_matter

TOKEN = re.compile(r"(\d+)\s*->\s*([^(),`\n]+?)(?=\s*(?:[(),`]|$|\n))")


def renumber(path):
    text = path.read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    pairs = []  # (old_num, name) in order of appearance
    for ln in fm.split("\n"):
        if ln.strip().startswith("group:"):
            for n, name in TOKEN.findall(ln):
                key = (int(n), name.strip().lower())
                if key not in pairs:
                    pairs.append(key)
    if not pairs:
        return False
    ordered = sorted(pairs, key=lambda k: (k[0], pairs.index(k)))
    mapping = {k: i + 1 for i, k in enumerate(ordered)}
    numbered_headings = bool(re.search(r"^\*\*\d+\.\s", body, re.M))
    if all(mapping[k] == k[0] for k in pairs) and not numbered_headings:
        return False

    def sub(m):
        key = (int(m.group(1)), m.group(2).strip().lower())
        new = mapping.get(key, int(m.group(1)))
        return f"{new} -> {m.group(2).strip()}"

    fm2 = "\n".join(TOKEN.sub(sub, ln) if ln.strip().startswith("group:") else ln for ln in fm.split("\n"))
    body2 = TOKEN.sub(sub, body)
    body2 = re.sub(r"^(\*\*)(\d+)\.\s+", r"\1", body2, flags=re.M)
    path.write_text(f"---\n{fm2}\n---\n{body2}", encoding="utf-8")
    return True


if __name__ == "__main__":
    paths = [RECIPES / f"{s}.md" for s in sys.argv[1:]] or sorted(RECIPES.glob("*.md"))
    n = sum(renumber(p) for p in paths)
    print(f"{n} of {len(paths)} recipes renumbered")
