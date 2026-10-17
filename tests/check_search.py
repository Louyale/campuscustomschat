"""Problem 9 check: the agent's product search understands everyday shopper words.

Run from the HW4 folder:  python tests/check_search.py
For 12 everyday requests it compares the old search (every word had to appear somewhere in the
product text) with the new relevance search (shopper synonyms, category words, field weights).
A query passes when the new search finds items and its top 3 are the kind of item asked for.
No AI is involved, so this runs offline in well under a second.
"""

from __future__ import annotations

import sqlite3
import sys
import time
from pathlib import Path

HW4 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW4 / "backend"))
import tools  # noqa: E402

con = sqlite3.connect(f"file:{tools.DB_PATH}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
TEXT = {r["product_id"]: " ".join([r["product_id"], r["name"], r["garment_type"], r["description"],
                                   r["colors"], r["search_tags"]]).lower()
        for r in con.execute("SELECT * FROM catalogue")}


def old_search(q: str) -> list[dict]:
    """The search before Problem 9: every word must appear as-is, then the default shop order."""
    terms = q.lower().split()
    return [p for p in tools.find_products() if all(t in TEXT[p["product_id"]] for t in terms)]


def is_cat(*cats: str):
    return lambda p: p["category"] in cats


def name_has(*words: str):
    return lambda p: any(w in p["name"].lower() for w in words)


# (what a shopper types, what the top results should be, how we describe it)
CASES = [
    ("coffee cup", is_cat("Drinkware"), "mugs / drinkware"),
    ("coffee cup dad", name_has("dad"), "the Dad mug"),
    ("tee for my dad", lambda p: p["category"] == "T-Shirts" and "dad" in p["name"].lower(), "Dad T-shirts"),
    ("something for my dorm wall", is_cat("Home & Decor", "Decals & Magnets"), "pennants / decor"),
    ("navy hoodies", is_cat("Hoodies"), "hoodies"),
    ("gift for grandma", name_has("grand"), "Grandma / Grandparent items"),
    ("sticker", is_cat("Decals & Magnets"), "decals"),
    ("hockey hoodie", lambda p: p["category"] == "Hoodies" and "hockey" in p["name"].lower(), "the hockey hoodie"),
    ("pierson crewneck", lambda p: p["category"] == "Crewnecks" and "pierson" in p["name"].lower(), "Pierson crewneck"),
    ("winter hat", is_cat("Hats"), "hats / beanies"),
    ("tie", is_cat("Ties & Scarves"), "ties"),
    ("baseball cap", is_cat("Hats"), "caps"),
]

results: list[bool] = []
print(f"{'Query':28} {'Before':>7} {'After':>6} {'ms':>6}  Top 3 after  ->  expected")
for query, fits, expected in CASES:
    before = old_search(query)
    start = time.perf_counter()
    after = tools.find_products(q=query)
    ms = (time.perf_counter() - start) * 1000
    top = after[:3]
    ok = bool(top) and all(fits(p) for p in top[: min(3, len(top))])
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} {query!r:23} {len(before):>7} {len(after):>6} {ms:6.1f}  "
          f"{' | '.join(p['name'] for p in top) or '(nothing)'}  ->  {expected}")
    if top:
        print(f"{'':45}matched on: {', '.join(top[0].get('matched_on', []))}")

found_before = sum(1 for q, *_ in CASES if old_search(q))
print(f"\nBefore: {found_before}/{len(CASES)} queries found anything.  "
      f"After: {sum(results)}/{len(CASES)} return the right kind of item in the top 3.")
sys.exit(0 if all(results) else 1)
