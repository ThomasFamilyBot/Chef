#!/usr/bin/env python3
"""Fallback when docs_api is not set up: edit a recipe Doc's ingredient table in place with the Google Docs edit tool.

    1. read the Doc with the Docs read tool (its JSON is saved to a file, not shown)
    2. gdoc_table_requests.py <saved-json> <slug> <out.json>
    3. send out.json's requests with the Docs edit tool, read the Doc again, and run this again: it must say 0 cells differ

Covers the table only, and only when the number of rows is unchanged. Changed direction lines are done by hand with
replaceAllText. Tested 2026-11-28 on Pasta al Limone (19 cells, rows moved, fractions kept). Costs about 5-20 KB of
requests per Doc through the session, so use scripts/push_docs.py whenever docs_api exists."""
import sys, json, re, html, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chef_lib import RECIPES, split_front_matter, frac_text
import yaml
doc = json.load(open(sys.argv[1])); slug = sys.argv[2]
doc = doc.get('content', doc)
body = doc['tabs'][0]['documentTab']['body']['content']
table = next(e for e in body if 'table' in e)['table']
def cell_info(cell):
    ps = [c for c in cell['content'] if 'paragraph' in c]
    text = ''.join(r.get('textRun', {}).get('content', '') for p in ps for r in p['paragraph']['elements'])
    return ps[0]['startIndex'], ps[-1]['endIndex'] - 1, text[:-1]
def want(s):
    h = frac_text(html.escape(str(s or '')), gap=' ', span=False)
    out, runs, pos = '', [], 0
    for part in re.split(r'(<sup>.*?</sup>|<sub>.*?</sub>)', h):
        m = re.match(r'<(sup|sub)>(.*?)</\1>', part)
        t = html.unescape(m.group(2) if m else part)
        if m: runs.append((len(out), len(out) + len(t), 'SUPERSCRIPT' if m.group(1) == 'sup' else 'SUBSCRIPT'))
        out += t
    return out, runs
fm, _ = split_front_matter(RECIPES / f'{slug}.md'.read_text())
ings = yaml.safe_load(fm)['ingredients']
rows = table['tableRows'][1:]
assert len(rows) == len(ings), (len(rows), len(ings))
edits = []
for row, ing in zip(rows, ings):
    for cell, key in zip(row['tableCells'], ('measure', 'item', 'prep', 'group')):
        s, e, cur = cell_info(cell); new, runs = want(ing.get(key))
        if cur != new: edits.append((s, e, new, runs))
reqs = []
for s, e, new, runs in sorted(edits, reverse=True):
    if e > s: reqs.append({'deleteContentRange': {'range': {'startIndex': s, 'endIndex': e}}})
    if new:
        reqs.append({'insertText': {'location': {'index': s}, 'text': new}})
        reqs.append({'updateTextStyle': {'range': {'startIndex': s, 'endIndex': s + len(new)}, 'textStyle': {'baselineOffset': 'NONE'}, 'fields': 'baselineOffset'}})
        for a, b, off in runs:
            reqs.append({'updateTextStyle': {'range': {'startIndex': s + a, 'endIndex': s + b}, 'textStyle': {'baselineOffset': off}, 'fields': 'baselineOffset'}})
json.dump(reqs, open(sys.argv[3], 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(edits), 'cells differ;', len(reqs), 'requests;', pathlib.Path(sys.argv[3]).stat().st_size, 'bytes; revision', doc.get('revisionId', '')[:12])
