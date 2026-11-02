#!/usr/bin/env python3
"""Compute nutrition for recipes from data/canonical_ingredients.csv.
House rule: WHOLE recipe only; calories, grams of protein, grams of fat. No per-serving, no carbs.

  nutrition.py --check [slugs...]     list unmapped ingredients / missing data
  nutrition.py --write slug [...]     compute and write the nutrition block into the recipe(s)
  nutrition.py --all                  write every recipe that is fully mapped

Rules (see .claude/skills/nutrition/SKILL.md): canonical values are per 1 oz by weight.
Volume and count measures convert to grams via the row's `portions` column
(e.g. "cup=125;TBLS=8;each=150;clove=3"). Per-ingredient overrides live in the recipe:
    nutrition: exclude                     # not eaten (brine discarded, equipment, garnish)
    nutrition: {fraction: 0.1, note: ...}  # only part is consumed (marinade absorbed)
    nutrition: {oz: 12, note: ...}         # override the computed edible ounces
"""
import sys, re, csv, pathlib, datetime, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import yaml
from chef_lib import *

OZ_G = 28.3495
VOL_CUP = {"tsp": 1 / 48, "TBLS": 1 / 16, "fl oz": 1 / 8, "cup": 1, "pint": 2, "quart": 4, "gallon": 16}
ZERO_UNITS = {"to taste", "pinch", "dash"}
NONFOOD_STATES = {"non-food", "nonfood", "equipment"}


def load_table():
    rows = load_canonical()
    idx = {}
    for r in rows:
        r["_portions"] = {}
        for part in (r.get("portions") or "").split(";"):
            if "=" in part:
                u, g = part.split("=", 1)
                try:
                    r["_portions"][u.strip()] = float(g)
                except ValueError:
                    pass
        idx[r["item"].strip().lower()] = r
        for a in (r.get("aliases") or "").split(";"):
            if a.strip():
                idx[a.strip().lower()] = r
    return rows, idx


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def grams_for(ing, row):
    """Return (grams, how) for an ingredient line using the canonical row's portions."""
    qty = float(ing["qty"]); unit = ing["unit"]
    if unit in ZERO_UNITS:
        return 0.0, f"{unit}: counted as 0"
    if unit in WEIGHT_UNITS:
        return qty * WEIGHT_UNITS[unit], f"{qty:g} {unit} by weight"
    if unit == "can":
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:fl )?oz", ing["item"]) or re.search(r"(\d+(?:\.\d+)?)\s*(?:fl )?oz", str(ing.get("measure", "")))
        if m:
            return qty * float(m.group(1)) * OZ_G, f"{qty:g} x {m.group(1)} oz can"
    p = row["_portions"]
    if unit in VOL_CUP and "cup" in p:
        return qty * VOL_CUP[unit] * p["cup"], f"{qty:g} {unit} at {p['cup']:g} g/cup"
    if unit in p:
        return qty * p[unit], f"{qty:g} {unit} at {p[unit]:g} g each"
    if unit == "each" and "each" not in p and len(p) == 1:
        u, g = next(iter(p.items()))
        return qty * g, f"{qty:g} each at {g:g} g (using {u} portion)"
    return None, f"no portion weight for unit {unit!r}"


def compute(r, idx):
    lines, assumptions, excluded, problems = [], [], [], []
    for ing in r["ingredients"]:
        ov = ing.get("nutrition")
        name = ing["item"]
        if ov == "exclude":
            excluded.append(name); continue
        row = idx.get(name.strip().lower())
        if row is None:
            problems.append(f"unmapped: {name}"); continue
        if (row.get("state") or "").lower() in NONFOOD_STATES:
            excluded.append(name); continue
        cal, pro, fat = (num(row.get(k)) for k in ("calories", "protein_g", "fat_g"))
        if cal is None or pro is None or fat is None:
            problems.append(f"missing values: {row['item']} (for {name})"); continue
        if isinstance(ov, dict) and ov.get("oz") is not None:
            oz = float(ov["oz"]); how = f"override {oz:g} oz"
        else:
            g, how = grams_for(ing, row)
            if g is None:
                problems.append(f"{name}: {how}"); continue
            oz = g / OZ_G
        frac = 1.0
        if isinstance(ov, dict) and ov.get("fraction") is not None:
            frac = float(ov["fraction"]); how += f"; {frac:.0%} consumed"
        y = num(row.get("edible_yield"))
        if y and 0 < y < 1 and ing["unit"] in WEIGHT_UNITS:
            how += f"; edible yield {y:.0%}"
        oz_e = oz * frac * (y if (y and 0 < y < 1 and ing["unit"] in WEIGHT_UNITS) else 1)
        note = (ov.get("note") if isinstance(ov, dict) else "") or ""
        if row.get("yield_note") and "yield" not in how:
            note = (note + "; " if note else "") + row["yield_note"]
        src = "canonical" if (row.get("source") or "").startswith("family") else (row.get("source") or "?")
        lines.append({
            "item": name if name == row["item"] else f"{name} (as {row['item']})",
            "amount": f"{ing['measure']} ({how})",
            "oz": round(oz_e, 2),
            "calories": round(cal * oz_e, 1), "protein_g": round(pro * oz_e, 2),
            "fat_g": round(fat * oz_e, 2),
            "source": src, **({"note": note} if note else {}),
        })
    tot = {k: round(sum(l[k] for l in lines), 1 if k == "calories" else 2) for k in ("calories", "protein_g", "fat_g")}
    return lines, tot, excluded, problems


def write_block(path, block):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    # drop any existing nutrition key (null or block) from the front matter text
    fm2 = re.sub(r"(?ms)^nutrition:.*?(?=^\S|\Z)", "", fm).rstrip("\n")
    dumped = yaml.safe_dump({"nutrition": block}, sort_keys=False, allow_unicode=True, width=120)
    pathlib.Path(path).write_text(f"---\n{fm2}\n{dumped}---\n{body}", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    rows, idx = load_table()
    sections = load_sections()
    recipes = [load_recipe(RECIPES / f"{s}.md", sections) for s in a.slugs] if a.slugs else load_all(sections)
    wrote = 0
    for r in recipes:
        lines, tot, excluded, problems = compute(r, idx)
        if a.check or problems:
            print(f"== {r['slug']}: {len(lines)} lines, {len(excluded)} excluded, {len(problems)} problems")
            for p in problems:
                print("   ", p)
        if (a.write or a.all) and not problems:
            block = {
                "computed": datetime.date.today().isoformat(),
                "basis": "whole recipe, ingredients as listed, raw weights; see line notes",
                "totals": tot,
                "lines": lines,
                "assumptions": [
                    "Values per oz from data/canonical_ingredients.csv (family custom entries first, then the cited source).",
                    "Volume and count measures converted to grams with the portion weights recorded in the table.",
                    "Salt, pepper and 'to taste' lines counted as zero.",
                ] + ([f"Excluded as not eaten or non-food: {', '.join(excluded)}."] if excluded else []),
                "excluded": excluded,
            }
            write_block(RECIPES / f"{r['slug']}.md", block)
            wrote += 1
            print(f"wrote {r['slug']}: {tot['calories']:.0f} cal, {tot['protein_g']:.1f} g protein, {tot['fat_g']:.1f} g fat (whole recipe)")
    if a.write or a.all:
        print(f"{wrote} recipes written")


if __name__ == "__main__":
    main()
