"""Rank our catalogue products by the live store's "Best selling" order.

The database has no sales data, so the ranking is read from the public
yalebulldogblue.com/collections/all?sort_by=best-selling pages. Each catalogue
product_id is the product's handle on the live site. The result is written to
backend/bestsellers.json as {product_id: rank}, where 1 is the best seller.

Usage: python backend/fetch_bestsellers.py
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE.parent / "data" / "campus_customs.db"
OUT_PATH = HERE / "bestsellers.json"
URL = "https://yalebulldogblue.com/collections/all?sort_by=best-selling&page={page}"
HANDLE = re.compile(r'href="/collections/all/products/([a-z0-9-]+)')


def main() -> None:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    ours = {row[0] for row in con.execute("SELECT product_id FROM catalogue")}

    order: list[str] = []
    page = 1
    while True:
        request = urllib.request.Request(URL.format(page=page), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            html = response.read().decode("utf-8", errors="replace")
        handles = [h for h in dict.fromkeys(HANDLE.findall(html)) if h not in order]
        if not handles:
            break
        order.extend(handles)
        page += 1
        time.sleep(0.3)  # be polite to the store

    ranks = {handle: i + 1 for i, handle in enumerate(h for h in order if h in ours)}
    OUT_PATH.write_text(json.dumps(ranks, indent=1), encoding="utf-8")
    print(f"Scanned {len(order)} live products on {page - 1} pages; ranked {len(ranks)}/{len(ours)} of ours.")


if __name__ == "__main__":
    main()
