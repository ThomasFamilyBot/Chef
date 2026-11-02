#!/usr/bin/env python3
"""Merge data/_sourcing/part*.csv into data/canonical_ingredients.csv.
Refuses to overwrite an existing item or to create duplicate aliases. Run nutrition_check.py after."""
import csv, glob, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
CAN = ROOT / "data" / "canonical_ingredients.csv"
rows = list(csv.DictReader(open(CAN, newline="")))
fields = list(rows[0].keys())
items = {r["item"].lower() for r in rows}
aliases = {}
for r in rows:
    for a in (r.get("aliases") or "").split(";"):
        if a.strip(): aliases[a.strip().lower()] = r["item"]
added, problems = 0, []
for p in sorted(glob.glob(str(ROOT / "data" / "_sourcing" / "part*.csv"))):
    for r in csv.DictReader(open(p, newline="")):
        if not r.get("item"): continue
        if r["item"].lower() in items:
            problems.append(f"{p}: {r['item']} already exists; skipped"); continue
        dup = [a.strip() for a in (r.get("aliases") or "").split(";") if a.strip() and a.strip().lower() in aliases]
        if dup:
            problems.append(f"{p}: {r['item']} aliases already mapped elsewhere: {dup} -> {[aliases[d.lower()] for d in dup]}; skipped"); continue
        rows.append({k: r.get(k, "") for k in fields}); items.add(r["item"].lower()); added += 1
        for a in (r.get("aliases") or "").split(";"):
            if a.strip(): aliases[a.strip().lower()] = r["item"]
with open(CAN, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f"added {added} rows; {len(rows)} total")
for p in problems: print("PROBLEM", p)
