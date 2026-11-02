#!/usr/bin/env python3
"""Build the static site into dist/."""
import sys, json, shutil, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from chef_lib import *

SITE = ROOT / "site"
DIST = ROOT / "dist"


def md(text):
    return markdown.markdown(text, extensions=["sane_lists", "tables"])


def fmt_time(v):
    if v is None:
        return "—"
    if v >= 60 and v % 60 == 0:
        return f"{v // 60} hr"
    if v >= 60:
        return f"{v // 60} hr {v % 60} min"
    return f"{v} min"


def main():
    sections = load_sections()
    recipes = load_all(sections)
    templates = load_templates()
    for t in templates:
        for it in t["items"]:
            it["section_resolved"] = section_for(it["item"], sections, it.get("section"))
            it.setdefault("shop", True)
    by_slug = {r["slug"]: r for r in recipes}
    menus = load_menus()
    for i, m in enumerate(menus):
        m["id"] = f"m{i+1}"
        m["slugs"] = [it["slug"] for it in m["items"] if it.get("slug") in by_slug]
        for it in m["items"]:
            if it.get("slug") in by_slug:
                it["title"] = by_slug[it["slug"]]["title"]
    pairings = load_pairings()
    pairs_by = {}
    for a, b, why in pairings:
        if a in by_slug and b in by_slug:
            pairs_by.setdefault(a, []).append((by_slug[b], why))
            pairs_by.setdefault(b, []).append((by_slug[a], why))
    for r in recipes:
        r["body_html"] = md(r["body_md"])
        r["section_order"] = [s["name"] for s in sections]
        r["pairs"] = pairs_by.get(r["slug"], [])
        r["menus"] = [m for m in menus if r["slug"] in m["slugs"]]

    env = Environment(loader=FileSystemLoader(SITE / "templates"), autoescape=select_autoescape(["html"]))
    env.filters["fmt_time"] = fmt_time

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "r").mkdir(parents=True)
    shutil.copytree(SITE / "static", DIST / "static")
    (DIST / ".nojekyll").write_text("")

    built = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ctx = dict(recipes=recipes, templates=templates, sections=[s["name"] for s in sections], built=built, menus=menus)

    (DIST / "index.html").write_text(env.get_template("index.html").render(base="", **ctx), encoding="utf-8")
    (DIST / "shop.html").write_text(env.get_template("shop.html").render(base="", **ctx), encoding="utf-8")
    (DIST / "menus.html").write_text(env.get_template("menus.html").render(base="", **ctx), encoding="utf-8")
    canonical = load_canonical()
    for c in canonical:
        try: c["_eff"] = float(c["efficiency"]) if c.get("efficiency") else 1e9
        except ValueError: c["_eff"] = 1e9
    (DIST / "nutrition.html").write_text(env.get_template("nutrition.html").render(base="", canonical=canonical, **ctx), encoding="utf-8")
    tpl = env.get_template("recipe.html")
    for r in recipes:
        (DIST / "r" / f"{r['slug']}.html").write_text(tpl.render(base="../", r=r, **ctx), encoding="utf-8")

    # data for client-side search + shopping list
    slim = []
    for r in recipes:
        slim.append({
            "slug": r["slug"], "title": r["title"], "tags": r.get("tags") or [], "serves": r.get("serves"),
            "servings": r.get("servings"), "times": r.get("times") or {},
            "reference": r.get("reference") or {},
            "ingredients": [{k: ing.get(k) for k in ("measure", "item", "prep", "group", "qty", "unit", "shop")} | {"section": ing["section_resolved"]}
                            for ing in (r.get("ingredients") or [])],
            "nutrition": r.get("nutrition"),
            "pairs": [p[0]["slug"] for p in r["pairs"]],
            "text": (r["body_md"] + " " + " ".join(i["item"] for i in r.get("ingredients") or [])).lower(),
        })
    (DIST / "recipes.json").write_text(json.dumps({"built": built, "sections": [s["name"] for s in sections],
                                                   "recipes": slim, "templates": templates,
                                                   "menus": [{"id": m["id"], "name": m["name"], "slugs": m["slugs"]} for m in menus]}, ensure_ascii=False), encoding="utf-8")
    print(f"built {len(recipes)} recipes, {len(templates)} templates -> {DIST}")


if __name__ == "__main__":
    main()
