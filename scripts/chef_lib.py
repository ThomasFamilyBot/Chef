"""Shared helpers: load recipes, resolve sections, unit tables."""
import csv, re, sys, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECIPES = ROOT / "recipes"
DATA = ROOT / "data"

VOLUME_UNITS = {"tsp": 1, "TBLS": 3, "fl oz": 6, "cup": 48, "pint": 96, "quart": 192, "gallon": 768}
WEIGHT_UNITS = {"g": 1, "oz": 28.3495, "lb": 453.592}
COUNT_UNITS = {"each", "clove", "head", "bunch", "sprig", "stalk", "can", "jar", "bottle", "container",
               "package", "box", "bag", "loaf", "stick", "slice", "dozen", "pinch", "dash", "to taste",
               "ear", "fillet", "piece", "sheet", "leaf", "rack", "whole", "large", "medium", "small"}
ALL_UNITS = set(VOLUME_UNITS) | set(WEIGHT_UNITS) | COUNT_UNITS

TIME_KEYS = ["prep", "cook", "rest", "total"]

# Fractions. Recipe files keep plain text (`1/2`, `1 1/2`); the site and the Google Doc export set them
# small (raised numerator, lowered denominator) so a fraction never reads as a whole number.
# site/static/units.js has the same rule for the shopping list; keep the two in step.
FRAC_DENOMINATORS = {2, 3, 4, 5, 6, 8, 10, 12, 16, 32}
_FRAC_RE = re.compile(r"(?<![\d/.,])(?:(\d+) )?(\d{1,2})/(\d{1,2})(?![\d/]|\.\d)")


def frac_text(escaped, gap="&#8239;", span=True):
    """HTML-escaped text -> the same text with cooking fractions wrapped in <span class="frac">.

    Only proper fractions with a kitchen denominator are touched, so dates, URLs and ratios such as
    80/20 are left alone. `gap` is what separates the whole number from its fraction in `1 1/2`. `span=False` leaves out
    the wrapper and gives bare <sup>/<sub>, which is what Google Docs understands."""
    def sub(m):
        whole, num, den = m.group(1), int(m.group(2)), int(m.group(3))
        if den not in FRAC_DENOMINATORS or not 0 < num < den:
            return m.group(0)
        f = f"<sup>{num}</sup>/<sub>{den}</sub>"
        if span:
            f = f'<span class="frac">{f}</span>'
        return f"{whole}{gap}{f}" if whole else f
    return _FRAC_RE.sub(sub, escaped)


def frac_html(html_text, gap="&#8239;", span=True):
    """Like frac_text, for a block of HTML: only text is touched, never tags, attributes or <code>."""
    out, in_code = [], 0
    for part in re.split(r"(<[^>]*>)", html_text):
        if part.startswith("<"):
            if re.match(r"<code\b", part, re.I): in_code += 1
            elif re.match(r"</code", part, re.I): in_code = max(0, in_code - 1)
            out.append(part)
        else:
            out.append(part if in_code else frac_text(part, gap, span))
    return "".join(out)


def slug_of(path):
    return pathlib.Path(path).stem


def split_front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("missing YAML front matter (--- ... ---)")
    return m.group(1), m.group(2)


def load_sections():
    with open(DATA / "store_sections.yaml") as f:
        cfg = yaml.safe_load(f)
    return cfg["sections"]


def section_for(item, sections, explicit=None):
    names = [s["name"] for s in sections]
    if explicit:
        if explicit not in names:
            raise ValueError(f"unknown section {explicit!r}")
        return explicit
    low = item.lower()
    best = None
    for s in sections:
        for kw in s.get("keywords", []):
            k = kw.lower()
            if re.search(r"(^|[^a-z])" + re.escape(k), low):
                # longest keyword wins across sections
                if best is None or len(k) > len(best[1]):
                    best = (s["name"], k)
    return best[0] if best else "Other"


def load_recipe(path, sections=None):
    sections = sections or load_sections()
    text = pathlib.Path(path).read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    meta = yaml.safe_load(fm) or {}
    meta["slug"] = slug_of(path)
    meta["body_md"] = body.strip()
    for ing in meta.get("ingredients", []) or []:
        ing["section_resolved"] = section_for(ing.get("item", ""), sections, ing.get("section"))
        ing.setdefault("shop", True)
        ing.setdefault("prep", "")
        ing.setdefault("group", "")
    return meta


def load_all(sections=None):
    sections = sections or load_sections()
    out = []
    for p in sorted(RECIPES.glob("*.md")):
        out.append(load_recipe(p, sections))
    return out


def load_templates():
    out = []
    for p in sorted((DATA / "shopping_templates").glob("*.yaml")):
        with open(p) as f:
            t = yaml.safe_load(f)
        t["slug"] = p.stem
        out.append(t)
    return out


def load_canonical():
    with open(DATA / "canonical_ingredients.csv", newline="") as f:
        return list(csv.DictReader(f))


def load_menus():
    p = DATA / "menus.yaml"
    return yaml.safe_load(open(p)) if p.exists() else []


def load_pairings():
    p = DATA / "pairings.yaml"
    return yaml.safe_load(open(p)) if p.exists() else []


def load_techniques():
    p = DATA / "techniques.yaml"
    return yaml.safe_load(open(p)) if p.exists() else []


def load_site():
    p = DATA / "site.yaml"
    return yaml.safe_load(open(p)) or {} if p.exists() else {}


ANSWERS = ROOT / "answers"


def load_answers(recipe_slugs=None):
    """Published "Ask" answers (answers/*.md), newest first. Returns (answers, errors).

    Each answer: front matter (question, asked, summary, picks[], optional lens and library[]) and an
    optional Markdown body. `recipe_slugs` lets the caller check that library entries exist."""
    out, errs = [], []
    for p in sorted(ANSWERS.glob("*.md")) if ANSWERS.exists() else []:
        try:
            fm, body = split_front_matter(p.read_text(encoding="utf-8"))
            a = yaml.safe_load(fm) or {}
        except Exception as e:
            errs.append(f"{p.name}: cannot parse: {e}")
            continue
        a["slug"], a["body_md"] = p.stem, body.strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*", p.stem):
            errs.append(f"{p.name}: file name must be YYYY-MM-DD-short-slug.md")
        for k in ("question", "asked", "summary"):
            if not a.get(k):
                errs.append(f"{p.name}: missing {k}")
        a["asked"] = str(a.get("asked") or "")
        picks = a.get("picks") or []
        if not isinstance(picks, list) or not picks:
            errs.append(f"{p.name}: needs at least one pick")
            picks = []
        for i, pk in enumerate(picks, 1):
            if not isinstance(pk, dict) or not pk.get("title") or not pk.get("why"):
                errs.append(f"{p.name}: pick {i} needs title and why")
            elif pk.get("url") and not re.match(r"https?://", str(pk["url"])):
                errs.append(f"{p.name}: pick {i} url must start with http")
        a["picks"] = [pk for pk in picks if isinstance(pk, dict)]
        lib = a.get("library") or []
        for i, lb in enumerate(lib, 1):
            if not isinstance(lb, dict) or not lb.get("slug"):
                errs.append(f"{p.name}: library entry {i} needs a slug")
            elif recipe_slugs is not None and lb["slug"] not in recipe_slugs:
                errs.append(f"{p.name}: library entry {i}: no recipe {lb['slug']!r}")
        a["library"] = [lb for lb in lib if isinstance(lb, dict)]
        out.append(a)
    out.sort(key=lambda a: a["slug"], reverse=True)
    return out, errs
