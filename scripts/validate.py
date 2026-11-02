#!/usr/bin/env python3
"""Validate recipe files. Usage: validate.py [recipes/x.md ...]  (default: all)"""
import sys, re, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chef_lib import *

FRACTION_GLYPHS = "½⅓⅔¼¾⅛⅜⅝⅞"
BARE_UNITS_OK = {"g", "tsp", "TBLS", "cup", "cups", "oz", "fl oz", "lb", "lbs"}


def check(path, sections):
    errs, warns = [], []
    try:
        r = load_recipe(path, sections)
    except Exception as e:
        return [f"cannot parse: {e}"], []
    for k in ["title", "reference", "serves", "times", "ingredients"]:
        if k not in r or r[k] in (None, "", []):
            errs.append(f"missing {k}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", r["slug"]):
        errs.append(f"bad slug {r['slug']!r}")
    ref = r.get("reference") or {}
    if isinstance(ref, dict) and not ref.get("text"):
        errs.append("reference.text missing")
    if not isinstance(ref, dict):
        errs.append("reference must be a mapping with text/url")
    t = r.get("times") or {}
    for k in t:
        if k not in TIME_KEYS:
            errs.append(f"times.{k} is not one of {TIME_KEYS}")
    for k in TIME_KEYS:
        v = t.get(k)
        if v is not None and (not isinstance(v, int) or v < 0):
            errs.append(f"times.{k} must be whole minutes or null, got {v!r}")
    if r.get("servings") is not None and not isinstance(r["servings"], (int, float)):
        errs.append("servings must be a number")
    if not r.get("body_md"):
        errs.append("directions body is empty")
    seen = set()
    for i, ing in enumerate(r.get("ingredients") or [], 1):
        where = f"ingredient {i} ({ing.get('item', '?')})"
        for k in ["measure", "item", "qty", "unit"]:
            if ing.get(k) in (None, ""):
                errs.append(f"{where}: missing {k}")
        if ing.get("unit") and ing["unit"] not in ALL_UNITS:
            errs.append(f"{where}: unit {ing['unit']!r} not in vocabulary")
        if ing.get("qty") is not None and not isinstance(ing["qty"], (int, float)):
            errs.append(f"{where}: qty must be a number")
        m = str(ing.get("measure", ""))
        if any(ch in m for ch in FRACTION_GLYPHS):
            errs.append(f"{where}: unicode fraction glyph in measure {m!r}; write 1/2 etc.")
        if re.search(r"\b(tbsp|tbs|Tbsp|TBSP|tablespoons?|teaspoons?|Tsp|TSP|pounds?|ounces?|grams?|ml|mL|liters?)\b", m):
            errs.append(f"{where}: non-house unit spelling in measure {m!r} (use g, tsp, TBLS, cup, oz, fl oz, lb)")
        if ing.get("section") and ing["section"] not in [s["name"] for s in sections]:
            errs.append(f"{where}: unknown section {ing['section']!r}")
        if ing.get("section_resolved") == "Other" and ing.get("shop", True):
            warns.append(f"{where}: no store section matched; set `section:`")
        item = ing.get("item", "")
        if item and item != item.strip():
            errs.append(f"{where}: item has stray whitespace")
        if item and item[:1].islower():
            warns.append(f"{where}: item should be Title Case ({item!r})")
    n = r.get("nutrition")
    if n:
        for k in ["computed", "basis", "totals", "lines", "assumptions"]:
            if k not in n:
                errs.append(f"nutrition.{k} missing")
        tot = (n.get("totals") or {})
        for k in ["calories", "protein_g", "fat_g", "carbs_g"]:
            if k not in tot:
                errs.append(f"nutrition.totals.{k} missing")
        if n.get("lines"):
            s = sum(float(l.get("calories") or 0) for l in n["lines"])
            if tot.get("calories") and abs(s - float(tot["calories"])) > max(5, 0.01 * s):
                errs.append(f"nutrition totals.calories {tot['calories']} != sum of lines {s:.0f}")
    return errs, warns


def main(argv):
    sections = load_sections()
    paths = [pathlib.Path(a) for a in argv] or sorted(RECIPES.glob("*.md"))
    bad = 0
    for p in paths:
        errs, warns = check(p, sections)
        for w in warns:
            print(f"WARN  {p.name}: {w}")
        for e in errs:
            print(f"ERROR {p.name}: {e}")
        bad += bool(errs)
    print(f"{len(paths)} recipes checked, {bad} with errors")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
