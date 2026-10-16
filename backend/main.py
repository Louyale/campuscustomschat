"""Campus Customs API: serves products, stock and images from campus_customs.db.

Problem 3 starts it small: product listing, single products with stock by size,
product images, and a chat stub. Problem 5 grows /api/chat into the PydanticAI agent.

Run from the HW4 folder:
    .venv/Scripts/python -m uvicorn backend.main:app --port 8004
"""

from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import threading
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")  # workspace .env holds PORTKEY_API_KEY; HW4/.env wins on conflicts

from backend.auth import router as auth_router  # noqa: E402  (reads .env settings at import)

DB_PATH = ROOT / os.getenv("DATABASE_PATH", "data/campus_customs.db")
IMAGES_DIR = ROOT / os.getenv("PRODUCT_IMAGES_DIR", "data/products")
BESTSELLERS = json.loads((Path(__file__).parent / "bestsellers.json").read_text(encoding="utf-8"))
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL", "OS"]  # OS = one size (hats)
LOW_STOCK = 5
IMAGE_VERSION = 4  # bump when clean_image() changes so browsers refetch

app = FastAPI(title="Campus Customs API", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5180", "http://127.0.0.1:5180"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(auth_router)


# ---------------------------------------------------------------- images

CLEAN_DIR = IMAGES_DIR.parent / f".clean_images_v{IMAGE_VERSION}"  # inside data/, so never committed


@lru_cache(maxsize=256)
def clean_image(name: str) -> bytes:
    """Return the product photo as a JPEG on a white background.

    73 of the 102 catalogue photos were transparent PNGs saved as JPEGs, so their
    background turned black. Flood-filling near-black pixels from the edges turns
    that background white (like the live store) and leaves the garment untouched.
    The fill takes about a second, so results are cached on disk.
    """
    cached = CLEAN_DIR / name
    if cached.exists():
        return cached.read_bytes()
    image = Image.open(IMAGES_DIR / name).convert("RGB")
    width, height = image.size
    for x, y in [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]:
        if sum(image.getpixel((x, y))) < 60:
            ImageDraw.floodfill(image, (x, y), (255, 255, 255), thresh=40)
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=90)
    CLEAN_DIR.mkdir(exist_ok=True)
    cached.write_bytes(buffer.getvalue())
    return buffer.getvalue()


@app.on_event("startup")
def warm_image_cache() -> None:
    """Clean any uncached photos in the background so first page loads stay fast."""
    names = [p.name for p in IMAGES_DIR.glob("*.jpg") if not (CLEAN_DIR / p.name).exists()]
    if names:
        threading.Thread(target=lambda: [clean_image(n) for n in names], daemon=True).start()


@app.get("/images/{name}")
def product_image(name: str) -> Response:
    path = (IMAGES_DIR / name).resolve()
    if path.parent != IMAGES_DIR.resolve() or not path.is_file():
        raise HTTPException(404, "Image not found")
    return Response(clean_image(name), media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})


# ---------------------------------------------------------------- grouping

# garment_type has 22 free-text spellings; fold them into shop categories.
CATEGORIES = ["Hoodies", "Crewnecks", "T-Shirts", "Quarter-Zips", "Jackets & Fleece", "Long Sleeves", "Hats"]

COLLEGES = ["benjamin-franklin", "berkeley", "branford", "davenport", "ezra-stiles", "grace-hopper",
            "jonathan-edwards", "morse", "pauli-murray", "pierson", "saybrook", "silliman",
            "timothy-dwight", "trumbull"]
RELATIVES = ["mom", "dad", "grandma", "grandpa", "aunt", "uncle", "brother", "sister", "cousin"]
SPORTS = ["baseball", "basketball", "diving", "fencing", "field-hockey", "football", "golf", "hockey",
          "lacrosse", "sailing", "soccer", "squash", "swimming", "tennis", "track", "volleyball"]
COLLECTIONS = ["Residential Colleges", "Sports", "Family", "Graduate & Professional Schools",
               "The Game", "Bulldogs"]


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
        found.append("Sports")
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


# ---------------------------------------------------------------- data access

def db() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


class Size(BaseModel):
    size: str
    quantity: int
    status: Literal["in_stock", "low_stock", "sold_out"]


class ProductSummary(BaseModel):
    product_id: str
    name: str
    garment_type: str
    category: str
    collections: list[str]
    short_description: str
    price: float
    image_url: str
    colors: list[str]
    best_seller_rank: int | None
    total_stock: int
    in_stock: bool


class Product(ProductSummary):
    description: str
    search_tags: list[str]
    sizes: list[Size]


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


# ---------------------------------------------------------------- routes

SortKey = Literal["featured", "best-selling", "price-asc", "price-desc", "name-asc", "name-desc"]


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "database": DB_PATH.exists(), "images": IMAGES_DIR.exists()}


@app.get("/api/products", response_model=list[ProductSummary])
def list_products(
    q: str | None = None,
    category: str | None = None,
    collection: str | None = None,
    in_stock: bool | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: SortKey = "featured",
    limit: int = Query(200, ge=1, le=200),
) -> list[dict]:
    products = load_products()
    if q:
        terms = q.lower().split()
        with db() as con:
            text = {r["product_id"]: " ".join([r["name"], r["garment_type"], r["description"],
                                                r["colors"], r["search_tags"]]).lower()
                    for r in con.execute("SELECT * FROM catalogue")}
        products = [p for p in products if all(t in text[p["product_id"]] for t in terms)]
    if category:
        products = [p for p in products if p["category"] == category]
    if collection:
        products = [p for p in products if collection in p["collections"]]
    if in_stock is not None:
        products = [p for p in products if p["in_stock"] == in_stock]
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]

    rank = lambda p: p["best_seller_rank"] or 10_000  # noqa: E731
    sorters = {
        "featured": lambda p: (category_rank(p["category"]), rank(p)),
        "best-selling": rank,
        "price-asc": lambda p: (p["price"], p["name"]),
        "price-desc": lambda p: (-p["price"], p["name"]),
        "name-asc": lambda p: p["name"].lower(),
        "name-desc": lambda p: p["name"].lower(),
    }
    products.sort(key=sorters[sort], reverse=sort == "name-desc")
    return products[:limit]


def category_rank(category: str) -> int:
    # "Featured" leads with hoodies, the shop's signature piece.
    return 0 if category == "Hoodies" else 1


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> dict:
    with db() as con:
        row = con.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(404, f"No product with id '{product_id}'")
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


@app.get("/api/categories")
def list_categories() -> dict:
    products = load_products()
    return {
        "categories": [{"name": c, "count": sum(p["category"] == c for p in products)} for c in CATEGORIES],
        "collections": [{"name": c, "count": sum(c in p["collections"] for p in products)} for c in COLLECTIONS],
    }


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatTurn] = []


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductSummary] = []
    stub: bool = True


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Stub for Problem 3. Problem 5 replaces this body with the PydanticAI agent."""
    return ChatResponse(
        reply=(
            "Thanks for the message! Our Bulldog shopping assistant is still lacing up its trail shoes, "
            "so live answers are coming soon. In the meantime, the Products page shows real prices and "
            "stock by size, or you can reach the shop at orderdept@campuscustoms.com."
        )
    )
