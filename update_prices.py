"""Sync catalogue prices in campus_customs.db with the live store, yalebulldogblue.com.

Each catalogue product_id is the product's Shopify handle on the live site, so the
prices are read from the store's public /products.json feed and matched by handle.

Before the first change it saves a one-time backup, campus_customs.original.db.
It writes data/price_changes.csv listing the old and new price for every product.

Usage:
    python update_prices.py            # show what would change
    python update_prices.py --apply    # write the new prices to the database
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import sqlite3
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / os.getenv("DATABASE_PATH", "data/campus_customs.db")
STORE_URL = "https://yalebulldogblue.com"
USER_AGENT = "Mozilla/5.0 (campus-customs-hw4 price sync)"


def fetch_live_prices() -> dict[str, dict]:
    """Return {handle: {"title", "price", "compare_at"}} for every product in the live store."""
    products: dict[str, dict] = {}
    page = 1
    while True:
        request = urllib.request.Request(
            f"{STORE_URL}/products.json?limit=250&page={page}", headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            batch = json.loads(response.read().decode("utf-8"))["products"]
        if not batch:
            return products
        for product in batch:
            prices = sorted(float(v["price"]) for v in product["variants"])
            compare = [float(v["compare_at_price"]) for v in product["variants"] if v.get("compare_at_price")]
            products[product["handle"]] = {
                "title": product["title"],
                "price": prices[0],  # lowest variant price (all sizes cost the same today)
                "max_price": prices[-1],
                "compare_at": max(compare) if compare else None,
            }
        page += 1


def main() -> int:
    apply = "--apply" in sys.argv
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return 1

    live = fetch_live_prices()
    print(f"Live store products fetched: {len(live)}")

    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT product_id, name, price FROM catalogue ORDER BY product_id").fetchall()

    changes, missing, varied = [], [], []
    for product_id, name, old_price in rows:
        item = live.get(product_id)
        if item is None:
            missing.append(product_id)
            continue
        if item["price"] != item["max_price"]:
            varied.append(product_id)
        changes.append((product_id, name, old_price, item["price"], item["compare_at"]))

    report = DB_PATH.parent / "price_changes.csv"
    with report.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["product_id", "name", "old_price", "live_price", "compare_at_price"])
        writer.writerows(changes)

    changed = [c for c in changes if round(c[2], 2) != round(c[3], 2)]
    print(f"Matched: {len(changes)}/{len(rows)}   price differs: {len(changed)}   not on live site: {len(missing)}")
    if missing:
        print("  Not found on live site (left unchanged):", ", ".join(missing))
    if varied:
        print("  Size-dependent prices (lowest used):", ", ".join(varied))
    for product_id, _, old, new, _ in changed[:10]:
        print(f"  {product_id:<55} ${old:>6.2f} -> ${new:>6.2f}")
    if len(changed) > 10:
        print(f"  ... and {len(changed) - 10} more (see {report.name})")

    if not apply:
        print("\nDry run only. Re-run with --apply to update the database.")
        return 0

    backup = DB_PATH.with_name(DB_PATH.stem + ".original.db")
    if not backup.exists():
        shutil.copy2(DB_PATH, backup)
        print(f"Backup saved: {backup.name}")
    with con:
        con.executemany(
            "UPDATE catalogue SET price = ? WHERE product_id = ?",
            [(new, product_id) for product_id, _, _, new, _ in changes],
        )
    con.close()
    print(f"Updated {len(changes)} prices in {DB_PATH.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
