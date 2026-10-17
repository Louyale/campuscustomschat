"""Catalogue and stock lookups, used by both the website routes (main.py) and the agent.

Everything here opens campus_customs.db READ-ONLY and never touches the users table,
so the agent's tools cannot change data or see passwords.

The functions at the bottom are the tools the agent can call: quick_check (fast price and
stock), get_product_description, get_price, get_stock, search_products and list_categories.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Literal

from models import (ColorInfo, PriceInfo, ProductDescription, ProductMatch, QuickCheck, SearchResults, SizeStock,
                    StockInfo)

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / os.getenv("DATABASE_PATH", "data/campus_customs.db")
BESTSELLERS: dict[str, int] = json.loads((Path(__file__).parent / "bestsellers.json").read_text(encoding="utf-8"))
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL", "OS"]  # OS = one size (hats)
LOW_STOCK = 5
IMAGE_VERSION = 4  # bump when main.clean_image() changes so browsers refetch

# garment_type has many free-text spellings; fold them into shop categories, grouped like the
# live store's menu: Apparel (clothing and hats) and Accessories (everything else).
APPAREL = ["Hoodies", "Crewnecks", "T-Shirts", "Quarter-Zips", "Jackets & Fleece", "Long Sleeves", "Hats"]
ACCESSORY_CATEGORIES = {  # category: accessory types (garment_type values) that belong to it
    "Drinkware": ["mug", "glass", "glass set", "wine glass", "pint glass", "shotglass", "tumbler", "bottle",
                  "waterbottle", "water bottle", "koozie", "drinkware"],
    "Bags": ["bag", "backpack", "duffle", "tote", "tote bag", "pouch", "cooler", "cooler bag", "cinch bag",
             "laundry bag", "messenger bag"],
    "Home & Decor": ["pennant", "banner", "blanket", "frame", "ornament", "towel", "golf towel", "apron",
                     "pot holder", "coaster", "golf ball", "charger", "phone wallet", "gift"],
    "Books & Stationery": ["book", "journal", "folder", "pencil", "pen", "pen pack", "stationary", "sticky notes",
                           "mousepad"],
    "Ties & Scarves": ["tie", "scarf", "silk scarf", "soccer scarf", "earmuffs", "slides", "sunglasses"],
    "Jewelry, Pins & Keychains": ["earrings", "lapel pin", "keychain", "acrylic keychain", "keyring", "lanyard",
                                  "badge holder", "card organizer"],
    "Decals & Magnets": ["decal", "magnet", "tattoo"],
    "Pets & Plush": ["dog bandana", "dog toy", "dog tank top", "plush", "stress ball"],
}
CATEGORIES = APPAREL + list(ACCESSORY_CATEGORIES)
GROUPS = ["Apparel", "Accessories"]

COLLEGES = ["benjamin-franklin", "berkeley", "branford", "davenport", "ezra-stiles", "grace-hopper",
            "jonathan-edwards", "morse", "pauli-murray", "pierson", "saybrook", "silliman",
            "timothy-dwight", "trumbull"]
RELATIVES = ["mom", "dad", "grandma", "grandpa", "aunt", "uncle", "brother", "sister", "cousin"]
# Bulldog Athletics: gear that shows a Yale sports team. Sport names are matched in the
# product_id; these extra items name a team in other ways (Yale Crew, The Game,
# the Yale Bowl, or the BULLDOGS team wordmark).
ATHLETICS_EXTRA = {"crew-left-chest-hoodie", "2025-yale-vs-harvard-t-shirt", "yale-bowl-t-shirt",
                   "dry-zone-long-sleeve", "ua-mens-tech-l-s-2-0", "yale-maplehouse-diana-mockneck"}
# Low-Key Yale Gear: pieces a fellow Yalie recognizes (Handsome Dan, Boola Boola, crests)
# without a big YALE wordmark or block Y.
LOW_KEY = {"boola-boola-t-shirt", "district-vit-hoodie-boola-boola-verbiage",
           "district-tri-blend-t-shirt-vintage-sitting-bulldog", "pierson-logo-t-shirt", "saybrook-logo-t-shirt",
           "morse-logo-t-shirt", "grace-hopper-logo-t-shirt", "benjamin-franklin-t-shirt", "ezra-stiles-logo-t-shirt",
           "silliman-logo-t-shirt", "school-of-management-crest-t-shirt"}
SPORTS = ["baseball", "basketball", "diving", "fencing", "field-hockey", "football", "golf", "hockey",
          "lacrosse", "sailing", "soccer", "squash", "swimming", "tennis", "track", "volleyball"]
# Products that lead their collection, whatever the sort order, in the order listed.
SPOTLIGHT = {
    "Graduate & Professional Schools": ["school-of-management"],
    "Bulldog Athletics": ["lacrosse", "field-hockey"],
}
COLLECTIONS = ["Residential Colleges", "Bulldog Athletics", "Low-Key Yale Gear", "Family",
               "Graduate & Professional Schools", "The Game", "Bulldogs"]

SortKey = Literal["featured", "best-selling", "price-asc", "price-desc", "name-asc", "name-desc"]


# ---------------------------------------------------------------- grouping

def category_for(garment_type: str) -> str:
    g = garment_type.lower().strip()
    for category, kinds in ACCESSORY_CATEGORIES.items():
        if g in kinds:
            return category
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
    if product_id in LOW_KEY:
        found.append("Low-Key Yale Gear")
    return found


def group_for(category: str) -> str:
    return "Apparel" if category in APPAREL else "Accessories"


def has_color_choice(category: str) -> bool:
    """Hats and accessories come in real colorways; clothing lists its design colors (garment first)."""
    return category == "Hats" or group_for(category) == "Accessories"


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


def to_summary(row: sqlite3.Row, total_stock: int, one_size: bool = False) -> dict:
    category = category_for(row["garment_type"])
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "category": category,
        "group": group_for(category),
        "one_size": one_size,
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
            """SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock,
                      COUNT(i.size) = 1 AND MAX(i.size) = 'OS' AS one_size
               FROM catalogue c LEFT JOIN inventory i ON i.product_id = c.product_id
               GROUP BY c.product_id"""
        ).fetchall()
    return [to_summary(r, r["total_stock"], bool(r["one_size"])) for r in rows]


def summaries_for(product_ids: list[str]) -> list[dict]:
    """Product cards for these ids, in the same order; unknown ids are dropped."""
    by_id = {p["product_id"]: p for p in load_products()}
    return [by_id[pid] for pid in dict.fromkeys(product_ids) if pid in by_id]


def _category_rank(category: str) -> int:
    # "Featured" leads with hoodies, the shop's signature piece.
    return 0 if category == "Hoodies" else 1


def find_products(q: str | None = None, category: str | None = None, collection: str | None = None,
                  in_stock: bool | None = None, min_price: float | None = None, max_price: float | None = None,
                  sort: SortKey = "featured", limit: int = 400, group: str | None = None) -> list[dict]:
    products = load_products()
    if group:
        products = [p for p in products if p["group"].lower() == group.lower()]
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
        **to_summary(row, sum(stock.values()), list(stock) == ["OS"]),
        "description": row["description"],
        "search_tags": json.loads(row["search_tags"]),
        "sizes": sizes,
    }


def category_counts() -> dict:
    products = load_products()
    return {
        "categories": [{"name": c, "group": group_for(c), "count": sum(p["category"] == c for p in products)}
                       for c in CATEGORIES],
        "groups": [{"name": g, "count": sum(p["group"] == g for p in products)} for g in GROUPS],
        "collections": [{"name": c, "count": sum(c in p["collections"] for p in products)} for c in COLLECTIONS],
    }


# ---------------------------------------------------------------- agent tools
# Every answer about a product's description, price or stock comes from these functions,
# which read campus_customs.db on every call (read-only). Results are typed models from
# models.py, so the agent gets exact facts in a fixed shape and never has to guess.

STOP_WORDS = {"the", "a", "an", "of", "in", "for", "and", "do", "you", "have", "is", "it", "size", "sizes", "how",
              "much", "many", "price", "stock", "left", "any", "your", "my", "one", "t", "tell", "me", "about"}


def normalize_size(size: str | None) -> str | None:
    if not size:
        return None
    s = size.strip().upper().replace("2XL", "XXL").replace("XX-LARGE", "XXL").replace("ONE SIZE", "OS")
    return {"SMALL": "S", "MEDIUM": "M", "LARGE": "L", "X-LARGE": "XL", "EXTRA LARGE": "XL",
            "EXTRA SMALL": "XS", "X-SMALL": "XS"}.get(s, s)


def _colors(category: str, colors: list[str]) -> ColorInfo:
    # The catalogue's colors describe clothing designs (garment first, then print colors);
    # only hats and accessories come in several real colorways.
    if has_color_choice(category):
        return ColorInfo(colors_available=colors)
    return ColorInfo(garment_color=colors[0] if colors else None, print_colors=colors[1:])


def _row(con: sqlite3.Connection, product_id: str) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()


def _sizes(con: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = con.execute("SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchall()
    rows = sorted(rows, key=lambda r: SIZE_ORDER.index(r["size"]) if r["size"] in SIZE_ORDER else 99)
    return [SizeStock(size=r["size"], quantity=r["quantity"], status=stock_status(r["quantity"])) for r in rows]


# How shoppers say it -> how product names spell it.
SYNONYMS = {"tee": "shirt", "tshirt": "shirt", "som": "management", "cap": "hat", "hoody": "hoodie",
            "quarterzip": "zip"}


def _canonical(word: str) -> str:
    word = SYNONYMS.get(word, word)
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]  # hoodies -> hoodie, mugs -> mug
    return SYNONYMS.get(word, word)


def _resolve(con: sqlite3.Connection, product: str) -> tuple[sqlite3.Row | None, list[str]]:
    """Find a product by exact product_id or by the words of its name; also return other close names."""
    row = _row(con, product.strip())
    if row is not None:
        return row, []
    words = [w for w in (_canonical(w) for w in re.findall(r"[a-z0-9]+", product.lower()) if w not in STOP_WORDS) if w]
    if not words:
        return None, []
    rows = con.execute("SELECT product_id, name FROM catalogue").fetchall()
    hits = [h for h in rows if all(w in (h["product_id"] + " " + h["name"]).lower() for w in words)]
    # Best match: the name with the fewest extra words, then the best seller.
    hits.sort(key=lambda h: (len(re.findall(r"[a-z0-9]+", h["name"].lower())) - len(words),
                             BESTSELLERS.get(h["product_id"], 10_000)))
    if not hits:
        return None, []
    return _row(con, hits[0]["product_id"]), [h["name"] for h in hits[1:5]]


def _not_found(product_id: str) -> str:
    return f"No product with id '{product_id}'. Use search_products or quick_check to find the right one."


def search_products(query: str | None = None, category: str | None = None, collection: str | None = None,
                    max_price: float | None = None, in_stock_only: bool = False,
                    sort: SortKey = "best-selling", limit: int = 8, group: str | None = None) -> SearchResults:
    """Find products to recommend. Use this to browse or compare; use quick_check for one item's price and stock.

    Args:
        query: Words to match in names, descriptions, colors and tags, e.g. "navy hoodie" or "pierson".
            Every word must match, so use one or two key words. Leave empty to browse.
        category: Apparel: Hoodies, Crewnecks, T-Shirts, Quarter-Zips, Jackets & Fleece, Long Sleeves, Hats.
            Accessories: Drinkware (mugs, glasses, tumblers), Bags, Home & Decor (pennants, blankets, ornaments,
            towels), Books & Stationery, Ties & Scarves, "Jewelry, Pins & Keychains", Decals & Magnets, Pets & Plush.
        collection: One of Residential Colleges, Bulldog Athletics, Low-Key Yale Gear (subtle pieces with
            Handsome Dan, Boola Boola or a crest instead of a big YALE), Family, Graduate & Professional Schools,
            The Game, Bulldogs.
        max_price: Highest price in US dollars.
        in_stock_only: True to skip products that are sold out in every size.
        sort: best-selling (default), featured, price-asc, price-desc, name-asc or name-desc.
        limit: How many results to return (1-12).
        group: "Apparel" (clothing and hats) or "Accessories" (everything else).
    """
    limit = max(1, min(int(limit), 12))
    results = find_products(q=query or None, category=category, collection=collection,
                            in_stock=True if in_stock_only else None, max_price=max_price, sort=sort, group=group)
    return SearchResults(total_matches=len(results), products=[
        ProductMatch(product_id=p["product_id"], name=p["name"], category=p["category"], price=p["price"],
                     in_stock=p["in_stock"], best_seller_rank=p["best_seller_rank"], summary=p["short_description"],
                     **_colors(p["category"], p["colors"]).model_dump())
        for p in results[:limit]])


def get_product_description(product: str) -> ProductDescription | str:
    """The full product description: what it is, its style, and its colors. One call, by name or id.

    Args:
        product: A product_id or the product's name as the shopper said it, e.g. "SOM crest tee".
    """
    with db() as con:
        row, _ = _resolve(con, product)
    if row is None:
        return _not_found(product)
    category = category_for(row["garment_type"])
    return ProductDescription(product_id=row["product_id"], name=row["name"], category=category, style=row["garment_type"],
                              description=row["description"],
                              **_colors(category, json.loads(row["colors"])).model_dump())


def get_price(product_id: str) -> PriceInfo | str:
    """The current price of one product, in US dollars, exactly as stored in the database.

    Args:
        product_id: The exact product_id from search_products or quick_check.
    """
    with db() as con:
        row = _row(con, product_id)
    if row is None:
        return _not_found(product_id)
    return PriceInfo(product_id=product_id, name=row["name"], price=row["price"], price_text=f"${row['price']:.2f}")


def get_stock(product_id: str, size: str | None = None) -> StockInfo | str:
    """How many are in stock: for every size, or for one size when the shopper asks about it.

    Args:
        product_id: The exact product_id from search_products or quick_check.
        size: Optional. XS, S, M, L, XL, XXL ("2XL" works), or OS for one-size items.
    """
    wanted = normalize_size(size)
    with db() as con:
        row = _row(con, product_id)
        if row is None:
            return _not_found(product_id)
        sizes = _sizes(con, product_id)
    in_stock = [s.size for s in sizes if s.quantity > 0]
    sold_out = [s.size for s in sizes if s.quantity <= 0]
    if wanted:
        match = next((s for s in sizes if s.size == wanted), None)
        if match is None:
            answer = f"{wanted} is not offered. Sizes offered: {', '.join(s.size for s in sizes)}."
        elif match.quantity <= 0:
            answer = f"{wanted}: sold out." + (f" In stock: {', '.join(in_stock)}." if in_stock else " Sold out in every size.")
        else:
            answer = f"{wanted}: {match.quantity} in stock" + (" (only a few left)." if match.status == "low_stock" else ".")
    else:
        answer = (f"In stock: {', '.join(f'{s.size} ({s.quantity})' for s in sizes if s.quantity > 0) or 'none'}."
                  + (f" Sold out: {', '.join(sold_out)}." if sold_out else ""))
    return StockInfo(product_id=product_id, name=row["name"], size_requested=wanted, sizes=sizes,
                     in_stock_sizes=in_stock, sold_out_sizes=sold_out, total_in_stock=sum(s.quantity for s in sizes),
                     answer=answer)


def quick_check(product: str, size: str | None = None) -> QuickCheck:
    """FAST price-and-stock answer in one call. Use this first whenever a shopper asks
    "how much is…", "is … in stock", or "do you have … in size …".

    Give it the product's name as the shopper said it (or a product_id) and, if they named one,
    the size. It finds the product and returns the current price and stock in a single database
    lookup, so the shopper gets a quick, accurate answer instead of a guess.

    Args:
        product: A product_id or the product's name, e.g. "Basic Hoodie Big Yale" or "pierson crewneck".
        size: Optional. XS, S, M, L, XL, XXL ("2XL" works), or OS for one-size items.
    """
    wanted = normalize_size(size)
    with db() as con:
        row, others = _resolve(con, product)
        if row is None:
            return QuickCheck(found=False, answer=f"No product matches '{product}'. Try search_products with fewer words.")
        sizes = _sizes(con, row["product_id"])

    in_stock = [s.size for s in sizes if s.quantity > 0]
    sold_out = [s.size for s in sizes if s.quantity <= 0]
    price_text = f"${row['price']:.2f}"
    result = QuickCheck(found=True, product_id=row["product_id"], name=row["name"], price=row["price"],
                        price_text=price_text, size_requested=wanted, in_stock_sizes=in_stock,
                        sold_out_sizes=sold_out, other_matches=others, answer="")
    if wanted:
        match = next((s for s in sizes if s.size == wanted), None)
        if match is None:
            result.answer = f"{row['name']} is {price_text}. {wanted} is not offered; sizes: {', '.join(s.size for s in sizes)}."
        else:
            result.quantity, result.status = match.quantity, match.status
            result.answer = (f"{row['name']} is {price_text}. {wanted}: "
                             + ("sold out." if match.quantity <= 0 else f"{match.quantity} in stock."))
            if match.quantity <= 0 and in_stock:
                result.answer += f" In stock: {', '.join(in_stock)}."
    else:
        result.answer = (f"{row['name']} is {price_text}. "
                         + (f"In stock: {', '.join(in_stock)}." if in_stock else "Sold out in every size.")
                         + (f" Sold out: {', '.join(sold_out)}." if sold_out and in_stock else ""))
    return result


def list_categories() -> dict:
    """The shop's groups, categories and collections, with how many products are in each."""
    return category_counts()
