#!/usr/bin/env python3
"""Render a recipe as simple HTML in the family's Google Doc template layout.
Usage: export_gdoc_html.py recipes/x.md [--out file.html]
Drive's create_file with contentMimeType=text/html converts this into a Google Doc."""
import sys, html, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import markdown
from chef_lib import load_recipe, load_techniques
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import find_techniques

def t(v):
    return "—" if v is None else f"{v} min"

def render(path):
    r = load_recipe(path)
    e = html.escape
    ref = r["reference"]
    if ref.get("url"):
        label = ref["text"] + (f" — {ref['url_text']}" if ref.get("url_text") and ref["url_text"] != ref["text"] else "")
        refhtml = f'<a href="{e(ref["url"])}">{e(label)}</a>'
    else:
        refhtml = e(ref["text"])
    title_html = f'<a href="{e(ref["url"])}">{e(r["title"])}</a>' if ref.get("url") else e(r["title"])
    tm = r.get("times") or {}
    rows = "".join(
        f"<tr><td>{e(str(i['measure']))}</td><td>{e(i['item'])}</td><td>{e(i.get('prep') or '')}</td><td>{e(i.get('group') or '')}</td></tr>"
        for i in r["ingredients"])
    body = markdown.markdown(r["body_md"], extensions=["sane_lists"])
    techs = find_techniques(r["body_md"], load_techniques())
    if techs:
        body += "<p><b>Technique temperatures</b></p><ul>" + "".join(
            f"<li><b>{e(g['term'].capitalize())}</b>: {e(g['temp'])}" + (f" <a href=\"{e(g['url'])}\">ref</a>" if g.get('url') else "") + "</li>" for g in techs) + "</ul>"
    n = r.get("nutrition")
    if n:
        tot = n["totals"]
        nut = (f"<table border='1' cellpadding='4' style='border-collapse:collapse'><tr><th>Calories</th><th>Protein</th><th>Fat</th></tr>"
               f"<tr><td>{round(tot['calories'])}</td><td>{tot['protein_g']:.1f} g</td><td>{tot['fat_g']:.1f} g</td></tr></table>"
               f"<p><i>Whole recipe as listed. Basis: {e(n['basis'])}. Computed {e(str(n['computed']))}.</i></p>")
        if n.get("assumptions"):
            nut += "<p><b>Assumptions</b></p><ul>" + "".join(f"<li>{e(a)}</li>" for a in n["assumptions"]) + "</ul>"
        if n.get("excluded"):
            nut += f"<p><i>Excluded: {e(', '.join(n['excluded']))}</i></p>"
    else:
        nut = "<p><i>Not yet calculated.</i></p>"
    return f"""<html><head><meta charset="utf-8"><title>{e(r['title'])}</title></head><body>
<p><b><i><span style="font-size:18pt">{title_html}</span></i></b></p>
<p>Reference: {refhtml}</p>
<p>Serves: {e(str(r['serves']))}</p>
<p>Prep: {t(tm.get('prep'))} &nbsp;|&nbsp; Cook: {t(tm.get('cook'))} &nbsp;|&nbsp; Rest: {t(tm.get('rest'))} &nbsp;|&nbsp; Total: {t(tm.get('total'))}</p>
<table border="1" cellpadding="4" style="border-collapse:collapse">
<tr><td><b>Measure</b></td><td><b>Ingredient</b></td><td><b>Prep</b></td><td><b>Mise Grouping</b></td></tr>
{rows}
</table>
<p></p>
<p><b><i>Directions</i></b></p>
{body}
<p></p>
<p><b>Estimate Nutrition of Whole, Finished Recipe</b></p>
{nut}
</body></html>"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("recipe"); ap.add_argument("--out")
    a = ap.parse_args()
    out = render(a.recipe)
    if a.out: pathlib.Path(a.out).write_text(out, encoding="utf-8"); print(a.out)
    else: print(out)
