"""Catalogue and stock lookups, used by both the website routes (main.py) and the agent.

Everything here opens campus_customs.db READ-ONLY and never touches the users table,
so the agent's tools cannot change data or see passwords.

The four functions at the bottom (search_products, get_product_details,
check_size_stock, list_categories) are the tools the agent can call.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / os.getenv("DATABASE_PATH", "data/campus_customs.db")
BESTSELLERS: dict[str, int] = json.loads((Path(__file__).parent / "bestsellers.json").read_text(encoding="utf-8"))
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL", "OS"]  # OS = one size (hats)
LOW_STOCK = 5
IMAGE_VERSION = 4  # bump when main.clean_image() changes so browsers refetch

# garment_type has 22 free-text spellings; fold them into shop categories.
CATEGORIES = ["Hoodies", "Crewnecks", "T-Shirts", "Quarter-Zips", "Jackets & Fleece", "Long Sleeves", "Hats"]

COLLEGES = ["benjamin-franklin", "berkeley", "branford", "davenport", "ezra-stiles", "grace-hopper",
            "jonathan-edwards", "morse", "pauli-murray", "pierson", "saybrook", "silliman",
            "timothy-dwight", "trumbull"]
RELATIVES = ["mom", "dad", "grandma", "grandpa", "aunt", "uncle", "brother", "sister", "cousin"]
# Bulldog Athletics: gear that shows a Yale sports team. Sport names are matched in the
# product_id; these extra items name a team in other ways (Yale Crew, The Game,
# the Yale Bowl, or the BULLDOGS team wordmark).
ATHLETICS_EXTRA = {"crew-left-chest-hoodie", "2025-yale-vs-harvard-t-shirt", "yale-bowl-t-shirt",
                   "dry-zone-long-sleeve", "ua-mens-tech-l-s-2-0", "yale-maplehouse-diana-mockneck"}
SPORTS = ["baseball", "basketball", "diving", "fencing", "field-hockey", "football", "golf", "hockey",
          "lacrosse", "sailing", "soccer", "squash", "swimming", "tennis", "track", "volleyball"]
# Products that lead their collection, whatever the sort order, in the order listed.
SPOTLIGHT = {
    "Graduate & Professional Schools": ["school-of-management"],
    "Bulldog Athletics": ["lacrosse", "field-hockey"],
}
COLLECTIONS = ["Residential Colleges", "Bulldog Athletics", "Family", "Graduate & Professional Schools",
               "The Game", "Bulldogs"]

SortKey = Literal["featured", "best-selling", "price-asc", "price-desc", "name-asc", "name-desc"]


# ---------------------------------------------------------------- grouping

def category_for(garment_type: str) -> str:
    g = garment_type.lower()
    if any(word in g for word in ("beanie", "cap", "hat")):
        return "Hats"
    if "quarter-zip" in g:
        return "Quarter-Zips"
    if "jacket" in g:
        return "Jackets & Fleece"
    if "hood" in g:
        return "Hoodies"
    if "crew" in g and "t-shirt" not in g:
        return "Crewnecks"
    if "t-shirt" in g:
        return "T-Shirts"
    return "Long Sleeves"  # long-sleeve performance shirts and the mockneck


def collections_for(product_id: str) -> list[str]:
    words = product_id.split("-")
    found = []
    if any(product_id.startswith(c) for c in COLLEGES):
        found.append("Residential Colleges")
    if any(s in words or s in product_id.replace("creqneck", "crewneck") for s in SPORTS if "-" in s) or any(
        s in words for s in SPORTS
    ):
        found.append("Bulldog Athletics")
    elif product_id in ATHLETICS_EXTRA:
        found.append("Bulldog Athletics")
    if any(r in words for r in RELATIVES):
        found.append("Family")
    if "school" in words or "divinity" in words:
        found.append("Graduate & Professional Schools")
    if "harvard" in words:
        found.append("The Game")
    if "bulldog" in words:
        found.append("Bulldogs")
    return found


def stock_status(quantity: int) -> Literal["in_stock", "low_stock", "sold_out"]:
    if quantity <= 0:
        return "sold_out"
    return "low_stock" if quantity <= LOW_STOCK else "in_stock"


def short_description(text: str, limit: int = 110) -> str:
    first = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0]
    return first if len(first) <= limit else first[: limit - 1].rsplit(" ", 1)[0] + "…"


# ---------------------------------------------------------------- data access (read-only)

def db() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def to_summary(row: sqlite3.Row, total_stock: int) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "category": category_for(row["garment_type"]),
        "collections": collections_for(row["product_id"]),
        "short_description": short_description(row["description"]),
        "price": row["price"],
        "image_url": f"/images/{Path(row['image_file_path']).name}?v={IMAGE_VERSION}",
        "colors": json.loads(row["colors"]),
        "best_seller_rank": BESTSELLERS.get(row["product_id"]),
        "total_stock": total_stock,
        "in_stock": total_stock > 0,
    }


def load_products() -> list[dict]:
    with db() as con:
        rows = con.execute(
            """SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
               FROM catalogue c LEFT JOIN inventory i ON i.product_id = c.product_id
               GROUP BY c.product_id"""
        ).fetchall()
    return [to_summary(r, r["total_stock"]) for r in rows]


def summaries_for(product_ids: list[str]) -> list[dict]:
    """Product cards for these ids, in the same order; unknown ids are dropped."""
    by_id = {p["product_id"]: p for p in load_products()}
    return [by_id[pid] for pid in dict.fromkeys(product_ids) if pid in by_id]


def _category_rank(category: str) -> int:
    # "Featured" leads with hoodies, the shop's signature piece.
    return 0 if category == "Hoodies" else 1


def find_products(q: str | None = None, category: str | None = None, collection: str | None = None,
                  in_stock: bool | None = None, min_price: float | None = None, max_price: float | None = None,
                  sort: SortKey = "featured", limit: int = 200) -> list[dict]:
    products = load_products()
    if q:
        terms = q.lower().split()
        with db() as con:
            text = {r["product_id"]: " ".join([r["product_id"], r["name"], r["garment_type"], r["description"],
                                                r["colors"], r["search_tags"]]).lower()
                    for r in con.execute("SELECT * FROM catalogue")}
        products = [p for p in products if all(t in text[p["product_id"]] for t in terms)]
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    if collection:
        products = [p for p in products if collection.lower() in (c.lower() for c in p["collections"])]
    if in_stock is not None:
        products = [p for p in products if p["in_stock"] == in_stock]
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]

    rank = lambda p: p["best_seller_rank"] or 10_000  # noqa: E731
    sorters = {
        "featured": lambda p: (_category_rank(p["category"]), rank(p)),
        "best-selling": rank,
        "price-asc": lambda p: (p["price"], p["name"]),
        "price-desc": lambda p: (-p["price"], p["name"]),
        "name-asc": lambda p: p["name"].lower(),
        "name-desc": lambda p: p["name"].lower(),
    }
    products.sort(key=sorters[sort], reverse=sort == "name-desc")
    if collection in SPOTLIGHT:
        terms = SPOTLIGHT[collection]
        first = lambda p: next((i for i, t in enumerate(terms) if t in p["product_id"]), len(terms))  # noqa: E731
        products.sort(key=first)  # stable sort: spotlight items first, everything else keeps its order
    return products[:limit]


def product_detail(product_id: str) -> dict | None:
    with db() as con:
        row = con.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return None
        stock = {r["size"]: r["quantity"] for r in con.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,))}
    sizes = [{"size": s, "quantity": stock[s], "status": stock_status(stock[s])}
             for s in sorted(stock, key=lambda s: SIZE_ORDER.index(s) if s in SIZE_ORDER else 99)]
    return {
        **to_summary(row, sum(stock.values())),
        "description": row["description"],
        "search_tags": json.loads(row["search_tags"]),
        "sizes": sizes,
    }


def category_counts() -> dict:
    products = load_products()
    return {
        "categories": [{"name": c, "count": sum(p["category"] == c for p in products)} for c in CATEGORIES],
        "collections": [{"name": c, "count": sum(c in p["collections"] for p in products)} for c in COLLECTIONS],
    }


# ---------------------------------------------------------------- agent tools
# Short, factual results keep the model fast and honest. Prices and stock come
# straight from the database on every call, never from memory.

def _brief(p: dict) -> dict:
    # The catalogue's colors describe the design: garment color first, then print colors.
    # Only hats come in several colorways, so only their colors are real choices.
    if p["category"] == "Hats":
        colors = {"colors_available": p["colors"]}
    else:
        colors = {"garment_color": p["colors"][0] if p["colors"] else None, "print_colors": p["colors"][1:]}
    return {"product_id": p["product_id"], "name": p["name"], "price": p["price"], "category": p["category"],
            **colors, "in_stock": p["in_stock"], "best_seller_rank": p["best_seller_rank"],
            "summary": p["short_description"]}


def search_products(query: str | None = None, category: str | None = None, collection: str | None = None,
                    max_price: float | None = None, in_stock_only: bool = False,
                    sort: SortKey = "best-selling", limit: int = 8) -> dict:
    """Search the Campus Customs catalogue.

    Args:
        query: Words to match in names, descriptions, colors and tags, e.g. "navy hoodie" or "pierson".
            Every word must match, so use one or two key words. Leave empty to browse.
        category: One of Hoodies, Crewnecks, T-Shirts, Quarter-Zips, Jackets & Fleece, Long Sleeves, Hats.
        collection: One of Residential Colleges, Bulldog Athletics, Family, Graduate & Professional Schools,
            The Game, Bulldogs.
        max_price: Highest price in US dollars.
        in_stock_only: True to skip products that are sold out in every size.
        sort: best-selling (default), featured, price-asc, price-desc, name-asc or name-desc.
        limit: How many results to return (1-12).
    """
    limit = max(1, min(int(limit), 12))
    results = find_products(q=query or None, category=category, collection=collection,
                            in_stock=True if in_stock_only else None, max_price=max_price, sort=sort)
    return {"total_matches": len(results), "products": [_brief(p) for p in results[:limit]]}


def get_product_details(product_id: str) -> dict:
    """Full details for one product: description, price, colors, and stock for every size.

    Args:
        product_id: The exact product_id from a search result.
    """
    product = product_detail(product_id)
    if product is None:
        return {"error": f"No product with id '{product_id}'. Search first to get a valid product_id."}
    return {**_brief(product), "description": product["description"], "sizes": product["sizes"]}


def check_size_stock(product_id: str, size: str) -> dict:
    """How many of one product are in stock in one size.

    Args:
        product_id: The exact product_id from a search result.
        size: XS, S, M, L, XL, XXL, or OS for one-size hats. "2XL" means XXL.
    """
    size = size.strip().upper().replace("2XL", "XXL").replace("ONE SIZE", "OS")
    product = product_detail(product_id)
    if product is None:
        return {"error": f"No product with id '{product_id}'."}
    for s in product["sizes"]:
        if s["size"] == size:
            return {"product_id": product_id, "name": product["name"], "size": size, **{
                k: s[k] for k in ("quantity", "status")}, "price": product["price"]}
    return {"product_id": product_id, "name": product["name"], "size": size, "error": "That size is not offered.",
            "sizes_offered": [s["size"] for s in product["sizes"]]}


def list_categories() -> dict:
    """The shop's categories and collections, with how many products are in each."""
    return category_counts()
