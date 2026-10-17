# Campus Customs: Store Website and Chatbot (HW4)

A customer website for Campus Customs (Yale Bulldog Blue). It has a React + Vite TypeScript front end and a Python FastAPI backend, and its chatbot is a PydanticAI agent. Shoppers can browse products, create an account, chat about merch, see the matching items appear on the page, and get honest answers about price and stock from a local SQLite database.

## Assignment notes

- **Stack:** React + Vite + TypeScript front end and a FastAPI back end. The agent uses PydanticAI (`pydantic-ai-slim[openai]`).
- **AI calls:** routed through Portkey with `PORTKEY_API_KEY`. If we use OpenAI through Portkey, the model must be in the 5.6 or 6 series; harder agent steps may use a smarter model. The model is set by `OPENAI_MODEL` in `.env`.
- **Data:** `data/campus_customs.db` and `data/products/` come from the course `data.zip`. **They are not committed:** the database and product images are excluded by `.gitignore`.
- **Style reference:** see [STYLE_GUIDE.md](STYLE_GUIDE.md) for exact tokens and chatbot recommendations. Source: [yalebulldogblue.com](https://yalebulldogblue.com/) (Yale Bulldog Blue by Campus Customs, 57 Broadway, New Haven, CT 06511). Its theme uses a white background, Yale navy `#00366b` for primary buttons and the header, a cream `#f5f3ed` footer, a red-orange `#f04f36` accent for sales, and the Open Sans font. The menu is: Clothing, Accessories, Home, Collections, Residential Colleges, Sports, Relatives, Graduate & Professional Schools.
- **Workflow:** one problem at a time, with each prompt logged in [AI_prompts.md](AI_prompts.md).
- **Submission:** a **public** GitHub repo; the repo URL goes on Canvas. The last problem shows the file tree.

## Database (`data/campus_customs.db`)

| Table | Rows | Contents |
|---|---|---|
| `catalogue` | 102 (+11 from `add_products.py`: 7 hats, 4 low-key pieces) | product_id, name, garment_type, description, colors (JSON), search_tags (JSON), image_file_path, price |
| `inventory` | 612 | product_id × size (XS–XXL) → quantity; 145 rows have 0 in stock |
| `users` | 3 | name, email, password_hash (pbkdf2_sha256), created_at, first_name, last_name; includes a test user |
| `chat_messages` | 22 | user_id, role, content, products_json, created_at |

Prices were synced to the live store on 2026-10-16 with `update_prices.py` and now run from $24.99 to $199.99; the original course prices ($32–$98) are kept in `data/campus_customs.original.db`. The `garment_type` labels are inconsistent (22 variants) and should be grouped into categories for filtering.

## Running the site

You need Python 3.12+ and Node 20+. Unzip the course `data.zip` into `HW4/data/` first (it is not in the repo).

```bash
# Backend (FastAPI on http://localhost:8000), run from the backend/ folder
python -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements.txt
cd backend
../.venv/Scripts/activate        # or: source ../.venv/Scripts/activate in Git Bash
uvicorn main:app --reload --port 8000

# Front end (React + Vite on http://localhost:5180), in a second terminal
cd frontend
npm install
npm run dev
```

Copy `.env.example` to `.env` and fill in `PORTKEY_API_KEY` (and a `SESSION_SECRET`). Vite forwards `/api` and `/images` to the backend. After unzipping the data, run `python add_products.py` once: it adds 11 real products from the live store, 7 hats (the course data has none) and 4 pieces for the Low-Key Yale Gear collection. Optional: `python update_prices.py --apply` syncs prices with the live store, and `python backend/fetch_bestsellers.py` refreshes the best-seller ranking.

| Endpoint | What it returns |
|---|---|
| `GET /api/products` | Product list; filters `q`, `category`, `collection`, `in_stock`, `min_price`, `max_price`, `sort` |
| `GET /api/products/{product_id}` | One product with stock by size |
| `GET /api/categories` | Category and collection counts |
| `GET /images/{file}` | Product photo on a white background |
| `POST /api/auth/register`, `/login`, `/logout`; `GET /api/auth/me` | Accounts (secure session cookie) |
| `POST /api/chat` | One chat turn with the PydanticAI agent: reply, product cards, suggestions |
| `GET /api/chat/history` | A logged-in shopper's saved chat |

The agent lives in four files next to `main.py`: `prompts/prompt.md` (system prompt), `agent.py` (wiring), `tools.py` (catalogue tools) and `models.py` (types).

## Checks

With the backend running: `python tests/check_auth.py` (16 account and security checks) and `python tests/check_chat.py` (14 chat accuracy checks against the database).
