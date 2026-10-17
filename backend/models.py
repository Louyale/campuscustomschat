"""Pydantic types shared by the API (main.py) and the agent (agent.py).

Product types describe what the website shows. Chat types describe what the
website sends to /api/chat and what comes back. AgentReply is the structured
answer the PydanticAI agent must return on every turn.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

StockStatus = Literal["in_stock", "low_stock", "sold_out"]


# ---------------------------------------------------------------- products (product cards)

class Size(BaseModel):
    size: str
    quantity: int
    status: StockStatus


class ProductSummary(BaseModel):
    """One product card: what the Products page and the chat show."""

    product_id: str
    name: str
    garment_type: str
    category: str
    group: str  # "Apparel" or "Accessories"
    one_size: bool = False  # only one size ("OS"), so it can go straight into the cart
    collections: list[str]
    short_description: str
    price: float
    image_url: str
    colors: list[str]
    best_seller_rank: int | None
    total_stock: int
    in_stock: bool


class Product(ProductSummary):
    """A single-item page: the card plus full text and stock by size."""

    description: str
    search_tags: list[str]
    sizes: list[Size]


# ---------------------------------------------------------------- chat

class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    # Guests send their recent turns; logged-in shoppers' history is loaded from chat_messages.
    history: list[ChatTurn] = Field(default_factory=list, max_length=40)


class ChatMessage(ChatTurn):
    """A saved turn returned by /api/chat/history, with the product cards it showed."""

    products: list[ProductSummary] = []
    created_at: str | None = None


class SearchFilters(BaseModel):
    """The catalogue search behind a set of matches, so the page can link to every result."""

    query: str | None = Field(None, description="Words searched for, e.g. 'navy' or 'pierson'.")
    category: str | None = Field(None, description="e.g. Hoodies, T-Shirts, Hats, Drinkware.")
    collection: str | None = Field(None, description="e.g. Residential Colleges, Bulldog Athletics, Low-Key Yale Gear.")
    group: str | None = Field(None, description="Apparel or Accessories.")
    max_price: float | None = None


class PageResults(BaseModel):
    """Chat search results for the website to show on the page."""

    title: str = Field(description="What was searched, e.g. 'Hoodies'.")
    headline: str = Field(description="Friendly heading shown on the page, e.g. 'We have Hoodies!'.")
    total: int = Field(description="How many products match the search in all.")
    browse_url: str | None = Field(None, description="Products-page link that shows every match.")


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductSummary] = []  # the matches, as full product cards (best first)
    page: PageResults | None = None      # set when the reply is a search the page should display
    suggestions: list[str] = []
    saved: bool = False  # True when the turn was stored in chat_messages for a logged-in shopper


class AgentReply(BaseModel):
    """The structured output the agent returns on every turn (the API contract with the website)."""

    reply: str = Field(description="What to say to the shopper: friendly, short, plain text (no markdown tables).")
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=12,
        description="product_id values (from tool results only) to show as product cards on the page, best "
                    "match first. Up to 12 for a search like 'what hoodies do you have'; empty when no product "
                    "should be shown.",
    )
    search: SearchFilters | None = Field(
        None,
        description="When the shopper asked about a type of item, the filters you searched with (the same values "
                    "you passed to search_products). The website uses them to show the matches and link to all "
                    "results. Leave empty for single-item, policy or small-talk answers.",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="Up to 3 short follow-up questions the shopper might tap next, each under 40 characters.",
    )


# ---------------------------------------------------------------- tool results (what the agent reads)
# Each agent tool returns one of these. They carry only facts read from campus_customs.db,
# in the exact shape the agent needs, so it can answer without guessing.

class ColorInfo(BaseModel):
    """Colors split so the agent never offers a print color as a choice."""

    garment_color: str | None = Field(None, description="Clothing: the one color the item comes in.")
    print_colors: list[str] = Field(default_factory=list, description="Clothing: colors in the printed design.")
    colors_available: list[str] = Field(default_factory=list, description="Hats and accessories: real color choices.")


class ProductMatch(ColorInfo):
    """One search result: enough to recommend an item and pick its product_id."""

    product_id: str
    name: str
    category: str
    price: float
    in_stock: bool = Field(description="True if at least one size is in stock.")
    best_seller_rank: int | None = Field(description="1 is the best seller on the live store.")
    summary: str


class SearchResults(BaseModel):
    total_matches: int
    products: list[ProductMatch]


class ProductDescription(ColorInfo):
    """get_product_description: the full text a shopper would read on the item page."""

    product_id: str
    name: str
    category: str
    style: str = Field(description="The garment or item type, e.g. 'pullover hoodie' or 'mug'.")
    description: str


class PriceInfo(BaseModel):
    """get_price: one price, in US dollars, exactly as stored."""

    product_id: str
    name: str
    price: float
    currency: Literal["USD"] = "USD"
    price_text: str = Field(description="The price formatted for the reply, e.g. '$39.99'.")


class SizeStock(BaseModel):
    size: str = Field(description="XS, S, M, L, XL, XXL, or OS for one-size items.")
    quantity: int = Field(description="Units in stock right now (0 means sold out).")
    status: StockStatus


class StockInfo(BaseModel):
    """get_stock: stock for every size, or for the one size the shopper asked about."""

    product_id: str
    name: str
    size_requested: str | None
    sizes: list[SizeStock]
    in_stock_sizes: list[str]
    sold_out_sizes: list[str]
    total_in_stock: int
    answer: str = Field(description="A plain statement of the facts to relay, e.g. 'XL: sold out.'")


class QuickCheck(BaseModel):
    """quick_check: name or id in, price and stock out, in one fast lookup."""

    found: bool
    product_id: str | None = None
    name: str | None = None
    price: float | None = None
    price_text: str | None = None
    size_requested: str | None = None
    quantity: int | None = Field(None, description="Units in the requested size (None if no size was asked).")
    status: StockStatus | None = None
    in_stock_sizes: list[str] = Field(default_factory=list)
    sold_out_sizes: list[str] = Field(default_factory=list)
    other_matches: list[str] = Field(default_factory=list, description="Other names that also matched, to ask which one.")
    answer: str = Field(description="A plain statement of the facts to relay.")


@dataclass
class ShopDeps:
    """Per-request facts the agent may use. Never includes passwords or other customers' data."""

    first_name: str | None = None
