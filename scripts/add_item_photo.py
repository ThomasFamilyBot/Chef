#!/usr/bin/env python3
"""Add or update an item's details card (photo + notes) for the Shopping List and recipe pages.

  python3 scripts/add_item_photo.py --item "Dried Mango (organic)" [--photo ~/path/img.jpg] \
      [--notes "Kirkland, 40 oz bag"] [--alias "Dried Mango"] [--rotate 90]

The photo is resized to 1000 px on the long side and re-encoded through BMP, which drops all
EXIF data (GPS location, phone model). The site is public, so never skip that step.
"""
import argparse, pathlib, re, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from chef_lib import ROOT, DATA
import yaml

ITEMS = DATA / "items.yaml"
PHOTOS = ROOT / "site" / "static" / "items"
HEADER = "".join(l for l in ITEMS.read_text().splitlines(keepends=True) if l.startswith("#")) if ITEMS.exists() else ""


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load():
    return (yaml.safe_load(ITEMS.read_text()) or {}).get("items") or [] if ITEMS.exists() else []


def save(items):
    items.sort(key=lambda x: x["item"].lower())
    ITEMS.write_text(HEADER + yaml.safe_dump({"items": items}, sort_keys=False, allow_unicode=True, width=120))


def convert(src, dest, rotate=None):
    with tempfile.TemporaryDirectory() as td:
        bmp = pathlib.Path(td) / "x.bmp"
        subprocess.run(["sips", "-s", "format", "bmp", str(src), "--out", str(bmp)], check=True, capture_output=True)
        if rotate:
            subprocess.run(["sips", "-r", str(rotate), str(bmp)], check=True, capture_output=True)
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "-Z", "1000", str(bmp), "--out", str(dest)], check=True, capture_output=True)
    raw = dest.read_bytes()
    if b"GPS" in raw or b"iPhone" in raw:
        dest.unlink()
        sys.exit("refusing: converted photo still carries camera/location metadata")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item", required=True)
    ap.add_argument("--photo")
    ap.add_argument("--notes")
    ap.add_argument("--alias", action="append", default=[])
    ap.add_argument("--rotate", type=int)
    a = ap.parse_args()
    items = load()
    key = a.item.strip().lower()
    entry = next((e for e in items if e["item"].lower() == key or key in [x.lower() for x in e.get("aliases") or []]), None)
    if entry is None:
        entry = {"item": a.item.strip()}
        items.append(entry)
    if a.alias:
        entry["aliases"] = sorted(set((entry.get("aliases") or []) + a.alias), key=str.lower)
    if a.photo:
        PHOTOS.mkdir(parents=True, exist_ok=True)
        name = slugify(entry["item"]) + ".jpg"
        convert(pathlib.Path(a.photo).expanduser(), PHOTOS / name, a.rotate)
        entry["photo"] = name
    if a.notes is not None:
        entry["notes"] = a.notes
    save(items)
    print(f"{entry['item']}: {entry}")


if __name__ == "__main__":
    main()
