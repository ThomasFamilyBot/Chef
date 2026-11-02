"""Shared helpers: load recipes, resolve sections, unit tables."""
import csv, re, sys, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECIPES = ROOT / "recipes"
DATA = ROOT / "data"

VOLUME_UNITS = {"tsp": 1, "TBLS": 3, "fl oz": 6, "cup": 48, "pint": 96, "quart": 192, "gallon": 768}
WEIGHT_UNITS = {"g": 1, "oz": 28.3495, "lb": 453.592}
COUNT_UNITS = {"each", "clove", "head", "bunch", "sprig", "stalk", "can", "jar", "bottle", "container",
               "package", "box", "bag", "loaf", "stick", "slice", "dozen", "pinch", "dash", "to taste",
               "ear", "fillet", "piece", "sheet", "leaf", "rack", "whole", "large", "medium", "small"}
ALL_UNITS = set(VOLUME_UNITS) | set(WEIGHT_UNITS) | COUNT_UNITS

TIME_KEYS = ["prep", "cook", "rest", "total"]


def slug_of(path):
    return pathlib.Path(path).stem


def split_front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("missing YAML front matter (--- ... ---)")
    return m.group(1), m.group(2)


def load_sections():
    with open(DATA / "store_sections.yaml") as f:
        cfg = yaml.safe_load(f)
    return cfg["sections"]


def section_for(item, sections, explicit=None):
    names = [s["name"] for s in sections]
    if explicit:
        if explicit not in names:
            raise ValueError(f"unknown section {explicit!r}")
        return explicit
    low = item.lower()
    best = None
    for s in sections:
        for kw in s.get("keywords", []):
            k = kw.lower()
            if re.search(r"(^|[^a-z])" + re.escape(k), low):
                # longest keyword wins across sections
                if best is None or len(k) > len(best[1]):
                    best = (s["name"], k)
    return best[0] if best else "Other"


def load_recipe(path, sections=None):
    sections = sections or load_sections()
    text = pathlib.Path(path).read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    meta = yaml.safe_load(fm) or {}
    meta["slug"] = slug_of(path)
    meta["body_md"] = body.strip()
    for ing in meta.get("ingredients", []) or []:
        ing["section_resolved"] = section_for(ing.get("item", ""), sections, ing.get("section"))
        ing.setdefault("shop", True)
        ing.setdefault("prep", "")
        ing.setdefault("group", "")
    return meta


def load_all(sections=None):
    sections = sections or load_sections()
    out = []
    for p in sorted(RECIPES.glob("*.md")):
        out.append(load_recipe(p, sections))
    return out


def load_templates():
    out = []
    for p in sorted((DATA / "shopping_templates").glob("*.yaml")):
        with open(p) as f:
            t = yaml.safe_load(f)
        t["slug"] = p.stem
        out.append(t)
    return out


def load_canonical():
    with open(DATA / "canonical_ingredients.csv", newline="") as f:
        return list(csv.DictReader(f))


def load_menus():
    p = DATA / "menus.yaml"
    return yaml.safe_load(open(p)) if p.exists() else []


def load_pairings():
    p = DATA / "pairings.yaml"
    return yaml.safe_load(open(p)) if p.exists() else []
