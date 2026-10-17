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
| `catalogue` | 102 (+262 from `add_products.py`: 7 hats, 4 low-key pieces, 251 accessories) | product_id, name, garment_type, description, colors (JSON), search_tags (JSON), image_file_path, price |
| `inventory` | 612 | product_id × size (XS–XXL) → quantity; 145 rows have 0 in stock |
| `users` | 3 | name, email, password_hash (pbkdf2_sha256), created_at, first_name, last_name; includes a test user |
| `chat_messages` | 22 | user_id, role, content, products_json, created_at |

Prices were synced to the live store on 2026-10-16 with `update_prices.py` and now run from $24.99 to $199.99; the original course prices ($32–$98) are kept in `data/campus_customs.original.db`. The `garment_type` labels are inconsistent (22 variants) and should be grouped into categories for filtering.

## Running the site

You need **Python 3.12+** and **Node 20+**. All commands run from this `hw4/` folder unless noted.

### 1. Place the data pack (not in the repo)

Unzip the course data pack into `hw4/data/` so the folder looks like this:

```
hw4/data/
├── campus_customs.db
└── products/          # images referenced by the catalogue
```

**Optional but recommended:** run `python add_products.py` once (needs internet). It adds 262 real products from the live store, so every feature in the write-ups shows up:
- 7 hats (the course data has none)
- 4 Low-Key Yale Gear pieces
- 251 accessories: mugs, bags, pennants, decals and more

It downloads their public photos into `data/products/`, and you can re-run it safely. Then run `python backend/fetch_bestsellers.py` to rank the best sellers. Without these steps the site still runs with the course's 102 clothing products.

### 2. Settings

Copy `.env.example` to `.env` (in `hw4/`) and fill in:
- `PORTKEY_API_KEY`
- `SESSION_SECRET` (make one with `python -c "import secrets; print(secrets.token_hex(32))"`)

The model is `OPENAI_MODEL` (default `gpt-6-luna`). Never commit `.env`.

### 3. Back end: FastAPI on http://localhost:8000 (terminal 1)

```bash
python -m venv .venv
.venv/Scripts/activate                 # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

Check it at http://localhost:8000/api/health. It should report `"database": true, "images": true, "ai_key_loaded": true`.

### 4. Front end: React + Vite on http://localhost:5180 (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5180**. Vite forwards `/api` and `/images` to the back end, so both must be running.

**Optional:** `python update_prices.py --apply` syncs prices with the live store.

| Endpoint | What it returns |
|---|---|
| `GET /api/products` | Product list; filters `q`, `group` (Apparel or Accessories), `category`, `collection`, `in_stock`, `min_price`, `max_price`, `sort` |
| `GET /api/products/{product_id}` | One product with stock by size |
| `GET /api/categories` | Category and collection counts |
| `GET /images/{file}` | Product photo on a white background |
| `POST /api/auth/register`, `/login`, `/logout`; `GET /api/auth/me` | Accounts (secure session cookie) |
| `POST /api/chat` | One chat turn with the PydanticAI agent: reply, product cards, suggestions |
| `GET /api/chat/history` | A logged-in shopper's saved chat |

The agent lives in four files next to `main.py`: `prompts/prompt.md` (system prompt), `agent.py` (wiring), `tools.py` (catalogue tools) and `models.py` (types).

## Checks

With the back end running, from `hw4/`:

| Test | What it checks | Last result |
|---|---|---|
| `python tests/check_auth.py` | Sign-up, login, hashed passwords, lockout | 16/16 |
| `python tests/check_tools.py` | Each product tool matches a direct SQL query | 15/15 |
| `python tests/check_search.py` | 12 everyday searches find the right items (offline) | 12/12 |
| `python tests/check_chat.py` | Live agent answers on price, stock, search and safety | 21/21 |
| `python tests/check_memory.py` | Saved history, customer name, page context ("this") | 11/11 |
| `python tests/check_audit.py` | Append-only audit trail, loop limits | 18/18 |
| `python tests/check_safety.py` | No invented products, exact prices, no other-store actions | 16/16 |

Live tests call the AI, so they pace themselves under the 20-messages-a-minute limit and can take a few minutes.

## Write-ups and evidence (`output/`)

- `harness.md`: how the system works (database, models and why, tools, safety, specs, audit trail)
- `usability.md` (Problem 9) and `design.md` (Problem 10)
- `app_check.html`: live site test with screenshots in `app_check_images/`; open it by double-clicking
- `audit_trail.json`: append-only record of every agent run
- `*_check.txt`: saved test output

## File tree

```
hw4/
├── AI_prompts.md
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── frontend/                 # Vite React TypeScript app
├── backend/
│   ├── main.py               # FastAPI app — run with: uvicorn main:app --reload
│   ├── agent.py
│   ├── models.py
│   ├── tools.py
│   ├── auth.py               # accounts and sessions (Problem 4)
│   ├── audit.py              # append-only audit trail (Problem 12)
│   └── prompts/
│       └── prompt.md
├── output/
│   ├── harness.md
│   ├── design.md
│   ├── usability.md
│   ├── app_check.html
│   ├── app_check_images/     # screenshots linked from app_check.html
│   └── audit_trail.json
├── tests/                    # the checks above
├── screenshots/              # evidence for each problem
├── add_products.py, update_prices.py, check_portkey.py   # data setup helpers
└── EVIDENCE_CHECKLIST.md, STYLE_GUIDE.md
```

Local-only data pack (not in git):

```
data/
├── campus_customs.db
└── products/                 # images referenced by the catalogue
```
