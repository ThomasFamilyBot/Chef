#!/usr/bin/env python3
"""Sanity checks for the canonical table and for computed recipe nutrition.
Exit 1 on any ERROR. WARNs are for a human to glance at.

Table checks (per 1 oz): calories 0-260 (pure fat is ~255/oz), protein <= 29 g, fat <= 29 g, carbs <= 29 g,
Atwater consistency (4P + 4C + 9F within tolerance of stated calories), portion weights in plausible ranges.
Recipe checks: calories/serving 20-3000, protein/serving <= 250 g, total weight/serving 30 g - 2 kg,
one ingredient supplying >85% of calories, a spice/salt line over 150 kcal (usually a unit mistake)."""
import sys, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chef_lib import *

OZ = 28.3495
SPICE_WORDS = ("salt", "pepper", "paprika", "cumin", "cayenne", "powder", "oregano", "thyme", "basil", "parsley", "flakes", "cinnamon", "clove", "allspice", "nutmeg", "bay", "saffron", "seeds", "anise", "coriander", "herbes", "extract")


def check_table():
    errs, warns = [], []
    for r in load_canonical():
        it = r["item"]
        try:
            cal, p, f, c = (float(r.get(k) or 0) for k in ("calories", "protein_g", "fat_g", "carbs_g"))
        except ValueError:
            errs.append(f"{it}: non-numeric values"); continue
        if not (0 <= cal <= 262): errs.append(f"{it}: calories/oz {cal:.1f} out of range")
        for k, v in (("protein", p), ("fat", f), ("carbs", c)):
            if not (0 <= v <= 29): errs.append(f"{it}: {k}/oz {v:.1f} out of range")
        atw = 4 * p + 4 * c + 9 * f
        alcohol = "alcohol" in (r.get("audit_note") or "").lower() or "alcoholic" in (r.get("source") or "").lower()
        if cal > 5 and not alcohol and abs(atw - cal) > max(8, 0.2 * cal):
            warns.append(f"{it}: calories {cal:.0f}/oz vs Atwater estimate {atw:.0f}/oz (fiber/alcohol/sugar alcohol can explain)")
        for part in (r.get("portions") or "").split(";"):
            if "=" not in part: continue
            u, g = part.split("=", 1)
            try: g = float(g)
            except ValueError: errs.append(f"{it}: bad portion {part}"); continue
            lo, hi = {"cup": (25, 400), "TBLS": (1.5, 30), "tsp": (0.4, 10), "fl oz": (20, 40), "each": (0.3, 6000), "clove": (1, 10), "head": (20, 1500), "bunch": (10, 800), "sprig": (0.2, 10), "stalk": (10, 150), "slice": (3, 100), "leaf": (0.1, 30), "stick": (2, 120), "can": (100, 1200), "bottle": (100, 1500), "package": (100, 2000), "container": (100, 1500)}.get(u.strip(), (0.01, 10000))
            if not (lo <= g <= hi): warns.append(f"{it}: portion {u.strip()}={g:g} g looks off (expected {lo}-{hi})")
        y = r.get("edible_yield")
        if y:
            try:
                if not (0.3 <= float(y) <= 1.0): errs.append(f"{it}: edible_yield {y} out of range")
            except ValueError: errs.append(f"{it}: bad edible_yield {y}")
    return errs, warns


def check_recipes():
    errs, warns = [], []
    for r in load_all():
        n = r.get("nutrition")
        if not n: continue
        s = n.get("servings") or r.get("servings") or 1
        t = n["totals"]; cal = float(t["calories"])
        per = cal / s
        if not (20 <= per <= 3000): errs.append(f"{r['slug']}: {per:.0f} kcal/serving (servings={s})")
        if float(t["protein_g"]) / s > 250: errs.append(f"{r['slug']}: {float(t['protein_g'])/s:.0f} g protein/serving")
        w = sum(float(l.get("oz") or 0) for l in n["lines"]) * OZ / s
        if not (30 <= w <= 2000): warns.append(f"{r['slug']}: {w:.0f} g of ingredients per serving")
        for l in n["lines"]:
            lc = float(l.get("calories") or 0)
            if cal and lc / cal > 0.85 and len(n["lines"]) > 3: warns.append(f"{r['slug']}: {l['item']} is {lc/cal:.0%} of calories")
            nm = l["item"].lower()
            if any(re.search(r"\b" + wd + r"\b", nm) for wd in SPICE_WORDS) and "butter" not in nm and "pork" not in nm and lc > 150: warns.append(f"{r['slug']}: {l['item']} = {lc:.0f} kcal; check the unit/portion")
            if lc > 6000: warns.append(f"{r['slug']}: {l['item']} = {lc:.0f} kcal in one line")
    return errs, warns


if __name__ == "__main__":
    e1, w1 = check_table(); e2, w2 = check_recipes()
    for w in w1 + w2: print("WARN ", w)
    for e in e1 + e2: print("ERROR", e)
    print(f"table: {len(e1)} errors, {len(w1)} warns; recipes: {len(e2)} errors, {len(w2)} warns")
    sys.exit(1 if e1 or e2 else 0)
