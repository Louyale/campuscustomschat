"""Campus Customs API (FastAPI). The website talks to this app; the chat route runs the agent.

Run from the backend/ folder:
    uvicorn main:app --reload --port 8000

Routes
- GET  /api/products, /api/products/{id}, /api/categories  catalogue, prices and stock by size
- GET  /images/{file}                                       product photos on a white background
- POST /api/auth/register | login | logout, GET /api/auth/me  accounts (auth.py)
- POST /api/chat                                            one chat turn with the PydanticAI agent (agent.py)
- GET  /api/chat/history                                    a logged-in shopper's saved chat
"""

from __future__ import annotations

import io
import json
import logging
import sqlite3
import threading
import time
from collections import defaultdict, deque
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")  # workspace .env holds PORTKEY_API_KEY; HW4/.env wins on conflicts

import os  # noqa: E402

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import agent  # noqa: E402
import tools  # noqa: E402
from auth import current_user  # noqa: E402
from auth import router as auth_router  # noqa: E402
from urllib.parse import urlencode  # noqa: E402

from models import (ChatMessage, ChatRequest, ChatResponse, ChatTurn, CustomerInfo, PageResults,  # noqa: E402
                    Product, ProductSummary, SearchFilters, ShopDeps)

log = logging.getLogger("campus_customs")
IMAGES_DIR = ROOT / os.getenv("PRODUCT_IMAGES_DIR", "data/products")

app = FastAPI(title="Campus Customs API", version="0.5.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5180", "http://127.0.0.1:5180"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(auth_router)


# ---------------------------------------------------------------- images

CLEAN_DIR = IMAGES_DIR.parent / f".clean_images_v{tools.IMAGE_VERSION}"  # inside data/, so never committed


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


# ---------------------------------------------------------------- catalogue

@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "database": tools.DB_PATH.exists(), "images": IMAGES_DIR.exists(),
            "model": os.getenv("OPENAI_MODEL", "gpt-6-luna"), "ai_key_loaded": bool(os.getenv("PORTKEY_API_KEY"))}


@app.get("/api/products", response_model=list[ProductSummary])
def list_products(
    q: str | None = None,
    category: str | None = None,
    collection: str | None = None,
    in_stock: bool | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: tools.SortKey = "featured",
    limit: int = Query(400, ge=1, le=400),
    group: str | None = None,
) -> list[dict]:
    return tools.find_products(q, category, collection, in_stock, min_price, max_price, sort, limit, group)


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> dict:
    product = tools.product_detail(product_id)
    if product is None:
        raise HTTPException(404, f"No product with id '{product_id}'")
    return product


@app.get("/api/categories")
def list_categories() -> dict:
    return tools.category_counts()


# ---------------------------------------------------------------- chat

CHAT_LIMIT, CHAT_WINDOW = 20, 60  # at most 20 messages a minute from one address
_chat_times: dict[str, deque[float]] = defaultdict(deque)


def _chat_db() -> sqlite3.Connection:
    con = sqlite3.connect(tools.DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _saved_turns(user_id: int, limit: int = 40, recent_hours: int | None = None) -> list[sqlite3.Row]:
    """A shopper's saved turns, oldest first. recent_hours keeps only the latest conversation."""
    since = f"AND created_at >= datetime('now', '-{int(recent_hours)} hours') " if recent_hours else ""
    with _chat_db() as con:
        rows = con.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages WHERE user_id = ? " + since +
            "ORDER BY id DESC LIMIT ?", (user_id, limit)).fetchall()
    return list(reversed(rows))


def customer_info(user) -> CustomerInfo:
    """The logged-in shopper's own account details for the agent (never the password hash)."""
    with _chat_db() as con:
        created = con.execute("SELECT created_at FROM users WHERE id = ?", (user.id,)).fetchone()["created_at"]
        saved = con.execute("SELECT COUNT(*) FROM chat_messages WHERE user_id = ?", (user.id,)).fetchone()[0]
    return CustomerInfo(customer_id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email,
                        member_since=(created or "")[:10], saved_messages=saved)


def _product_ids(products_json: str | None) -> list[str]:
    try:
        return [p["product_id"] for p in json.loads(products_json or "[]")]
    except (ValueError, TypeError, KeyError):
        return []


@app.get("/api/chat/history", response_model=list[ChatMessage])
def chat_history(cc_session: str | None = Cookie(default=None)) -> list[ChatMessage]:
    """The logged-in shopper's saved chat. Product cards are rebuilt so prices are current."""
    user = current_user(cc_session)
    if user is None:
        return []
    return [ChatMessage(role=r["role"], content=r["content"], created_at=r["created_at"],
                        products=tools.summaries_for(_product_ids(r["products_json"])))
            for r in _saved_turns(user.id)]


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    """One chat turn: the shopper's message in, the agent's reply and product cards out."""
    client = request.client.host if request.client else "?"
    times = _chat_times[client]
    while times and times[0] < time.time() - CHAT_WINDOW:
        times.popleft()
    if len(times) >= CHAT_LIMIT:
        raise HTTPException(429, "You're sending messages quickly. Please wait a minute and try again.")
    times.append(time.time())

    user = current_user(cc_session)
    if user:  # logged in: use the saved conversation, not whatever the browser sent
        # Only the last day goes to the model: older chats may quote prices or stock that have since changed.
        history = [ChatTurn(role=r["role"], content=r["content"]) for r in _saved_turns(user.id, 24, recent_hours=24)]
    else:
        history = body.history

    try:
        deps = ShopDeps(customer=customer_info(user) if user else None, page=body.page)
        answer = await agent.ask(body.message, history, deps)
    except Exception:  # model or network trouble: friendly message, details only in the server log
        log.exception("Agent call failed")
        raise HTTPException(503, "Our assistant is taking a breather. Please try again in a moment, or call "
                                 "(475) 301-4205.") from None

    products = tools.summaries_for(answer.product_ids)  # only real products become cards
    notes = {n.product_id: n.note.strip() for n in answer.product_notes}
    for card in products:  # attach each card's "why it fits" note (ignored for unknown ids)
        card["note"] = notes.get(card["product_id"]) or None
    # A search for a type of item (e.g. 'what hoodies do you have?') also fills the page with its matches.
    page = page_results(answer.search, len(products)) if products and answer.search else None
    saved = False
    if user:
        with _chat_db() as con:
            con.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)",
                        (user.id, body.message))
            con.execute("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
                        (user.id, answer.reply, json.dumps(products) if products else None))
        saved = True
    return ChatResponse(reply=answer.reply, products=products, page=page, suggestions=answer.suggestions, saved=saved)


def page_results(search: SearchFilters | None, shown: int) -> PageResults:
    """Heading, total and "see all" link for chat matches shown on the page."""
    if search is None:
        return PageResults(title="From the chat", headline="Picked for you", total=shown)
    filters = {k: v for k, v in search.model_dump().items() if v not in (None, "")}
    if filters.get("category"):
        filters.pop("group", None)  # a category already implies its group
    total = len(tools.find_products(q=filters.get("query"), category=filters.get("category"),
                                    collection=filters.get("collection"), group=filters.get("group"),
                                    max_price=filters.get("max_price")))
    max_price = filters.get("max_price")
    params = {"q": filters.get("query"), "category": filters.get("category"), "collection": filters.get("collection"),
              "group": filters.get("group"), "max_price": f"{max_price:g}" if max_price else None}
    title = " · ".join(str(v) for v in (filters.get("collection"), filters.get("category"), filters.get("group"))
                       if v) or (f"“{filters['query']}”" if filters.get("query") else "From the chat")
    if filters.get("max_price"):
        title += f" under ${filters['max_price']:g}"
    # A personal touch: "We have Hoodies!" rather than just "Hoodies".
    named = filters.get("collection") or filters.get("category") or filters.get("group")
    headline = f"We have {title}!" if named else f"Here's what we found for {title}"
    return PageResults(title=title, headline=headline, total=max(total, shown),
                       browse_url="/products?" + urlencode({k: v for k, v in params.items() if v not in (None, "")}))
