#!/usr/bin/env python3
"""Look up foods in the local USDA SR Legacy cache (run scripts/usda_fetch.sh first).

  usda_lookup.py search "pork shoulder raw"        # ranked matches with per-100 g macros
  usda_lookup.py show 168305                       # full macros + every household portion
  usda_lookup.py row 168305 --item "Pork shoulder, bone-in, raw" --aliases "Pork Butt, bone-in" \
        [--portions "each=4500"] [--yield 0.75] [--yield-note "..."] [--note "..."]
      -> prints a data/canonical_ingredients.csv row (per 1 oz), with portions auto-filled from USDA
         household measures (cup, TBLS, tsp, each-like units) plus any you pass.
"""
import sys, os, csv, re, argparse, pathlib, sqlite3

CACHE = pathlib.Path(os.environ.get("USDA_CACHE", pathlib.Path.home() / ".cache" / "chef-usda"))
SRC = CACHE / "FoodData_Central_sr_legacy_food_csv_2018-04"
DB = CACHE / "sr_legacy.sqlite"
OZ = 28.3495
NUT = {1008: "kcal", 1003: "protein", 1004: "fat", 1005: "carbs", 1079: "fiber", 1018: "alcohol"}
UNIT_MAP = {"cup": "cup", "tbsp": "TBLS", "tsp": "tsp", "fl oz": "fl oz", "oz": "oz", "lb": "lb", "pint": "pint", "quart": "quart", "gallon": "gallon"}


def build():
    if DB.exists():
        return
    if not SRC.exists():
        sys.exit(f"USDA cache missing at {SRC}; run scripts/usda_fetch.sh")
    con = sqlite3.connect(DB)
    con.executescript("""
    create table food(fdc_id int primary key, description text, category int);
    create table nutr(fdc_id int, nutrient_id int, amount real);
    create table portion(fdc_id int, seq int, amount real, unit text, desc text, modifier text, grams real);
    create table unit(id int primary key, name text);
    create table category(id int primary key, description text);
    """)
    with open(SRC / "food.csv", newline="", encoding="utf-8") as f:
        con.executemany("insert into food values(?,?,?)", ((int(r["fdc_id"]), r["description"], int(r["food_category_id"] or 0)) for r in csv.DictReader(f)))
    with open(SRC / "food_nutrient.csv", newline="", encoding="utf-8") as f:
        con.executemany("insert into nutr values(?,?,?)", ((int(r["fdc_id"]), int(r["nutrient_id"]), float(r["amount"])) for r in csv.DictReader(f) if int(r["nutrient_id"]) in NUT))
    with open(SRC / "measure_unit.csv", newline="", encoding="utf-8") as f:
        con.executemany("insert into unit values(?,?)", ((int(r["id"]), r["name"]) for r in csv.DictReader(f)))
    with open(SRC / "food_category.csv", newline="", encoding="utf-8") as f:
        con.executemany("insert into category values(?,?)", ((int(r["id"]), r["description"]) for r in csv.DictReader(f)))
    units = dict(con.execute("select id,name from unit"))
    with open(SRC / "food_portion.csv", newline="", encoding="utf-8") as f:
        con.executemany("insert into portion values(?,?,?,?,?,?,?)", ((int(r["fdc_id"]), int(r["seq_num"] or 0), float(r["amount"] or 1), units.get(int(r["measure_unit_id"] or 9999), ""), r["portion_description"], r["modifier"], float(r["gram_weight"])) for r in csv.DictReader(f)))
    con.execute("create index i1 on nutr(fdc_id)"); con.execute("create index i2 on portion(fdc_id)")
    con.commit(); con.close()


def macros(con, fid):
    d = {v: 0.0 for v in NUT.values()}
    for nid, amt in con.execute("select nutrient_id, amount from nutr where fdc_id=?", (fid,)):
        d[NUT[nid]] = amt
    return d


def search(con, q, limit=25):
    words = [w for w in re.split(r"\s+", q.strip().lower()) if w]
    rows = con.execute("select f.fdc_id, f.description, c.description from food f left join category c on c.id=f.category").fetchall()
    scored = []
    for fid, desc, cat in rows:
        dl = desc.lower()
        if all(w in dl for w in words):
            scored.append((len(dl), fid, desc, cat))
    scored.sort()
    for _, fid, desc, cat in scored[:limit]:
        m = macros(con, fid)
        print(f"{fid:7d}  {m['kcal']:6.0f} kcal {m['protein']:5.1f}P {m['fat']:5.1f}F {m['carbs']:5.1f}C /100g  {desc}  [{cat}]")
    if not scored:
        print("no matches")


def portions(con, fid):
    out = []
    for amt, unit, desc, mod, g in con.execute("select amount, unit, desc, modifier, grams from portion where fdc_id=? order by seq", (fid,)):
        out.append((amt, unit, desc, mod, g))
    return out


def show(con, fid):
    desc = con.execute("select description from food where fdc_id=?", (fid,)).fetchone()
    if not desc:
        sys.exit("unknown fdc_id")
    m = macros(con, fid)
    print(f"{fid}: {desc[0]}")
    print(f"  per 100 g: {m['kcal']:.0f} kcal, {m['protein']:.2f} g protein, {m['fat']:.2f} g fat, {m['carbs']:.2f} g carbs, {m['fiber']:.1f} g fiber, {m['alcohol']:.1f} g alcohol")
    print(f"  per 1 oz : {m['kcal']*OZ/100:.1f} kcal, {m['protein']*OZ/100:.2f} g protein, {m['fat']*OZ/100:.2f} g fat, {m['carbs']*OZ/100:.2f} g carbs")
    for amt, unit, desc, mod, g in portions(con, fid):
        print(f"  portion: {amt:g} {unit or ''} {desc} {mod}  = {g:g} g")
    print(f"  https://fdc.nal.usda.gov/food-details/{fid}/nutrients")


def auto_portions(con, fid):
    """Map USDA household measures to the house unit vocabulary (grams per 1 unit)."""
    p = {}
    for amt, unit, desc, mod, g in portions(con, fid):
        if not amt or not g:
            continue
        label = f"{unit or ''} {desc or ''} {mod or ''}".lower().replace("undetermined", "").strip()
        per = g / amt
        first = re.split(r"[\s,(]+", label, maxsplit=1)[0] if label else ""
        key = None
        if first in ("cup", "cups"): key = "cup"
        elif first in ("tbsp", "tablespoon"): key = "TBLS"
        elif first in ("tsp", "teaspoon"): key = "tsp"
        elif first in ("fl", "fluid") and "oz" in label: key = "fl oz"
        elif first in ("oz", "ounce"): key = "oz"
        elif first in ("lb", "pound"): key = "lb"
        elif first in ("pint",): key = "pint"
        elif first in ("quart",): key = "quart"
        elif first in ("gallon",): key = "gallon"
        else:
            for k in ("clove", "head", "bunch", "sprig", "stalk", "slice", "leaf", "stick", "fillet", "ear", "piece", "can", "bottle", "package"):
                if first.startswith(k):
                    key = k; break
            if key is None and (first in ("large", "medium", "small", "each", "whole", "unit", "fruit", "egg", "pepper", "item") or re.match(r"^\d", first) is None and ("medium" in label or "large" in label)):
                key = "each" if first != "small" else None
        if key and key not in p:
            p[key] = per
    # weight units are implied by the per-oz basis; drop them
    for k in ("oz", "lb"):
        p.pop(k, None)
    return p


def row(con, fid, item, aliases, extra_portions, yld, yield_note, note, state):
    desc = con.execute("select description from food where fdc_id=?", (fid,)).fetchone()[0]
    m = macros(con, fid)
    p = auto_portions(con, fid)
    for part in (extra_portions or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1); p[k.strip()] = float(v)
    cal, pro, fat, carb = (m[k] * OZ / 100 for k in ("kcal", "protein", "fat", "carbs"))
    eff = f"{cal/pro:.2f}" if pro > 0.05 else ""
    r = {
        "item": item, "state": state, "basis_oz": 1,
        "calories": f"{cal:.2f}", "protein_g": f"{pro:.3f}", "fat_g": f"{fat:.3f}", "carbs_g": f"{carb:.3f}",
        "efficiency": eff, "edible_yield": yld or "",
        "portions": ";".join(f"{k}={v:.4g}" for k, v in p.items()),
        "aliases": aliases or "",
        "source": f"USDA SR Legacy: {desc}", "source_url": f"https://fdc.nal.usda.gov/food-details/{fid}/nutrients",
        "fdc_id": fid, "yield_note": yield_note or "", "audit_note": note or "", "added": __import__("datetime").date.today().isoformat(),
    }
    w = csv.DictWriter(sys.stdout, fieldnames=list(r.keys())); w.writerow(r)


def main():
    build()
    con = sqlite3.connect(DB)
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit", type=int, default=25)
    sh = sub.add_parser("show"); sh.add_argument("fdc_id", type=int)
    r = sub.add_parser("row"); r.add_argument("fdc_id", type=int); r.add_argument("--item", required=True); r.add_argument("--aliases", default="")
    r.add_argument("--portions", default=""); r.add_argument("--yield", dest="yld", default=""); r.add_argument("--yield-note", default=""); r.add_argument("--note", default=""); r.add_argument("--state", default="raw")
    a = ap.parse_args()
    if a.cmd == "search": search(con, a.query, a.limit)
    elif a.cmd == "show": show(con, a.fdc_id)
    else: row(con, a.fdc_id, a.item, a.aliases, a.portions, a.yld, a.yield_note, a.note, a.state)


if __name__ == "__main__":
    main()
