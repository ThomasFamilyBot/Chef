#!/usr/bin/env python3
"""Render starter/overlay/GETTING_STARTED.md as HTML that Google Drive converts into a tidy Google Doc.

    python3 starter/guide_html.py > guide.html

Upload with the Drive connector's create_file (contentMimeType text/html); Drive turns it into a Doc.
"""
import pathlib, re, markdown

src = (pathlib.Path(__file__).parent / "overlay" / "GETTING_STARTED.md").read_text(encoding="utf-8")
html = markdown.markdown(src, extensions=["tables", "sane_lists"])
# Google Docs keeps inline styles only.
html = html.replace("<table>", '<table style="border-collapse:collapse;width:100%">')
html = re.sub(r"<th>", '<th style="border:1px solid #999;padding:6px;background:#f1ede6;text-align:left;font-size:10.5pt">', html)
html = re.sub(r"<td>", '<td style="border:1px solid #999;padding:6px;vertical-align:top;font-size:10.5pt">', html)
html = re.sub(r"<blockquote>\s*<p>", '<p style="margin:8pt 24pt;padding:8pt;background:#f6f3ee;border-left:3px solid #b5651d;font-style:italic">', html)
html = html.replace("</p>\n</blockquote>", "</p>").replace("</blockquote>", "")
html = html.replace("<code>", '<span style="font-family:Courier New,monospace;background:#f3f3f3">').replace("</code>", "</span>")
html = html.replace("<h1>", '<h1 style="font-size:24pt;color:#7a3e12">').replace("<h2>", '<h2 style="font-size:16pt;color:#7a3e12;margin-top:18pt">').replace("<h3>", '<h3 style="font-size:12.5pt">')
print('<html><head><meta charset="utf-8"></head><body style="font-family:Arial,sans-serif;font-size:11pt;line-height:1.4">' + html + "</body></html>")
