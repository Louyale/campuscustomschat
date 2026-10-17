"""Problem 6 check: the agent's product tools return real facts from campus_customs.db, fast.

Run from the HW4 folder:  python tests/check_tools.py
Part 1 calls each tool directly and compares it with a SQL query (no AI involved).
Part 2 asks the live agent questions and records which tools it called (needs PORTKEY_API_KEY).
"""

from __future__ import annotations

import asyncio
import os
import sqlite3
import sys
import time
from pathlib import Path

HW4 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW4 / "backend"))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(HW4 / ".env")
load_dotenv(HW4.parent / ".env")
import tools  # noqa: E402

con = sqlite3.connect(f"file:{tools.DB_PATH}?mode=ro", uri=True)
sql = lambda q, *a: con.execute(q, a).fetchone()  # noqa: E731
results: list[bool] = []


def check(ok: bool, label: str, ms: float | None = None) -> None:
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} {f'({ms:5.2f} ms) ' if ms is not None else ''}{label}")


def timed(fn, *args):
    start = time.perf_counter()
    value = fn(*args)
    return value, (time.perf_counter() - start) * 1000


def part1() -> None:
    print("Part 1: tools vs. the database")
    # Price
    r, ms = timed(tools.get_price, "basic-hoodie-big-yale")
    check(r.price == sql("SELECT price FROM catalogue WHERE product_id='basic-hoodie-big-yale'")[0]
          and r.price_text == "$39.99", "get_price: Basic Hoodie Big Yale = $39.99 (matches catalogue.price)", ms)
    # Description
    r, ms = timed(tools.get_product_description, "school-of-management-crest-t-shirt")
    check(r.description == sql("SELECT description FROM catalogue WHERE product_id='school-of-management-crest-t-shirt'")[0]
          and r.garment_color == "navy" and r.colors_available == [],
          "get_product_description: SOM tee text matches; navy garment, print colors are not options", ms)
    r, ms = timed(tools.get_product_description, "ceramic-mug-yale-university-wordmark")
    check(set(r.colors_available) == {"White", "Navy"}, "get_product_description: Yale mug offers White and Navy", ms)
    # Stock, every size and one size
    r, ms = timed(tools.get_stock, "basic-hoodie-big-yale")
    db_qty = dict(con.execute("SELECT size, quantity FROM inventory WHERE product_id='basic-hoodie-big-yale'").fetchall())
    check({s.size: s.quantity for s in r.sizes} == db_qty, "get_stock: every size matches the inventory table", ms)
    r, ms = timed(tools.get_stock, "pierson-college-crewneck", "Large")
    check(r.sizes and "L: sold out." in r.answer and "L" in r.sold_out_sizes,
          "get_stock: Pierson crewneck in L says 'sold out' clearly", ms)
    r, ms = timed(tools.get_stock, "basic-hoodie-big-yale", "XL")
    check("XL: 2 in stock (only a few left)." == r.answer, "get_stock: hoodie XL = 2, flagged as only a few left", ms)
    # Quick check by name
    r, ms = timed(tools.quick_check, "Basic Hoodie Big Yale", "XL")
    check(r.found and r.price_text == "$39.99" and r.quantity == 2, "quick_check: name + size -> $39.99, 2 in XL", ms)
    r, ms = timed(tools.quick_check, "pierson crewneck", "L")
    check(r.quantity == 0 and r.status == "sold_out" and "sold out" in r.answer,
          "quick_check: 'pierson crewneck' in L -> sold out, with in-stock sizes", ms)
    r, ms = timed(tools.quick_check, "lacrosse crewneck", "2xl")
    check(r.size_requested == "XXL" and r.quantity == sql(
        "SELECT quantity FROM inventory WHERE product_id='lacrosse-left-chest-crewneck' AND size='XXL'")[0],
        "quick_check: '2xl' is read as XXL", ms)
    r, ms = timed(tools.quick_check, "Y Dad Hat", "M")
    check(r.quantity is None and "not offered" in r.answer, "quick_check: a size that isn't offered says so", ms)
    r, ms = timed(tools.quick_check, "flux capacitor")
    check(not r.found, "quick_check: an unknown product is 'not found' (nothing invented)", ms)
    r, ms = timed(tools.get_price, "no-such-item")
    check(isinstance(r, str) and "No product" in r, "get_price: an unknown id returns an error, not a price", ms)


async def part2() -> None:
    if not os.getenv("PORTKEY_API_KEY"):
        print("\nPart 2 skipped: no PORTKEY_API_KEY")
        return
    import agent
    from pydantic_ai.messages import ToolCallPart

    print("\nPart 2: which tools the live agent calls")
    cases = [
        ("How much is the Basic Hoodie Big Yale?", {"quick_check", "get_price"}, "$39.99"),
        ("Is the Pierson College Crewneck in stock in a large?", {"quick_check", "get_stock"}, "sold out"),
        ("Tell me about the School of Management crest tee.", {"get_product_description", "quick_check"}, "navy"),
    ]
    for question, allowed, must_say in cases:
        start = time.perf_counter()
        run = await agent.get_agent().run(question, deps=agent.ShopDeps())
        seconds = time.perf_counter() - start
        called = [p.tool_name for m in run.all_messages() for p in m.parts if isinstance(p, ToolCallPart)
                  and p.tool_name != "final_result"]
        ok = bool(called) and set(called) & allowed and must_say.lower() in run.output.reply.lower()
        check(bool(ok), f"{question}\n       tools called: {called}  ({seconds:.1f}s)\n       reply: {run.output.reply}")


if __name__ == "__main__":
    part1()
    asyncio.run(part2())
    print(f"\n{sum(results)}/{len(results)} tool checks passed")
    sys.exit(0 if all(results) else 1)
