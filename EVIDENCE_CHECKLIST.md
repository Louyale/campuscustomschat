# Evidence Checklist (HW4)

The assignment says the evidence is **the running site, the database writes, and the screenshots**, plus this prompt log; no extra proof essay is needed. Each problem's evidence is added here when that problem arrives and checked off when it exists. Before grading, every box should be ticked.

## Every problem
- [x] A `## Problem N: <title>` section in `AI_prompts.md` with at least one prompt in my own words
- [x] A follow-up prompt, if one was needed, plus one sentence on what was lacking after the first
- [x] A row in the "At a glance" table

## Problem 1: Vibe coder prompts (4 points)
- [x] `AI_prompts.md` created at the start of the assignment and kept up to date
- [x] One section per problem with its number and title (checked again at the end for every problem)

## Problem 2: Analyze the database (6 points)
- [x] `output/harness.md` started
- [x] Every table and its fields written down (`catalogue`, `inventory`, `users`, plus `chat_messages`)
- [x] One short line per field on why it matters for the shop or the chatbot (25 proposed lines in a "Why it matters" column)
- [x] I've reviewed and reworded the 25 lines in my own words (saved in `output/harness.md`)

## Problem 3: Build the Campus Customs website (10 points)
- [x] React + Vite + TypeScript front end in `frontend/`
- [x] Nav bar linking Home, Products, About Us, Log in, Create account
- [x] Home and About Us written in my own voice, not copied from yalebulldogblue.com
- [x] Products page shows catalogue images (from the database image paths) with name, price and short description
- [x] Clicking a card opens a single-item page: large image on one side; description, price and sizes/stock on the other
- [x] Floating chat panel at the bottom right that calls the backend stub (`POST /api/chat`)
- [x] FastAPI app in `backend/main.py` serving products and images
- [x] Hats added to the catalogue (`add_products.py`, formerly `add_hats.py`): Y pom beanies, Y caps, Class of 2026 hat
- [x] Extras: Handsome Dan photo as the header logo (CC BY-SA 4.0, credited), "Boola Boola!" on About Us, Bulldog Athletics collection (38 items), School of Management spotlight in Grad & Professional Schools
- [x] Screenshots: `screenshots/p3_01` to `p3_17` (home, best sellers, The Game, Handsome Dan, products, single item, chat, About Us, create account, mobile, hats row, 2026 hat, hats category, Handsome Dan photo, Boola Boola, Bulldog Athletics, SOM spotlight)
- [x] I've reviewed the Home and About Us wording and made it my own (edited in `frontend/src/content.ts`)

## Problem 4: Create account and login (8 points)
- [x] Create account: first name, last name, email, password, confirm password
- [x] Log in: email and password
- [x] New accounts written to `users` with PBKDF2-HMAC-SHA256, 120,000 iterations, `pbkdf2_sha256$salt$hash`
- [x] Login re-hashes with the stored salt and uses a constant-time compare
- [x] Logged in as the seeded test user, and as a brand-new account (`screenshots/p4_*`, `output/auth_check.txt`, 16/16 checks)
- [x] `output/harness.md` explains what we store and how passwords are protected
- [x] I've reworded the harness auth section in my own words (code updated to match: 20-minute lockout, passwords need a number)

## Problem 5: PydanticAI agent backend (12 points)
- [x] API app in `backend/main.py`, runs from `backend/` with `uvicorn main:app --reload --port 8000`
- [x] Agent as four files next to it: `prompts/prompt.md`, `agent.py`, `tools.py`, `models.py`
- [x] Chat route: a website message returns the agent's reply (plus product cards and suggestions)
- [x] Campus Customs voice and safety basics in `prompts/prompt.md`
- [x] Types for chat replies and product cards in `models.py`
- [x] Agent uses the AI key from `.env` (`PORTKEY_API_KEY`, model from `OPENAI_MODEL`)
- [x] `output/harness.md`: how the front end talks to FastAPI and how the agent is loaded
- [x] Extras: Add to cart / Check options (size, color), cart with shipping + CT tax + total and a demo card form (no card data sent or stored), refined chat
- [x] Low-Key Yale Gear collection (11 pieces: Handsome Dan, Boola Boola, crests; 4 added from the live store)
- [x] Accessories: all 251 non-clothing items from the live store (Drinkware, Bags, Home & Decor, Books & Stationery, Ties & Scarves, Jewelry/Pins/Keychains, Decals & Magnets, Pets & Plush), shown as "Accessories" with real colorways
- [x] Chat accuracy: `tests/check_chat.py` 18/18 (`output/chat_check.txt`) after fixing the color and stale-history causes
- [x] Screenshots `p5_01` to `p5_15` (guest chat, prompt-injection refusal, Lou's saved chat, cart buttons, options, hat colors, added-to-cart popup, checkout tally, card validation, refined chat, larger chat button, Low-Key Yale Gear, Accessories page, home Accessories row, mug color options)
- [x] I've reviewed the harness Problem 5 section (my edits kept; the proof now matches a real Lou Donofrio test)

## Problem 6: Tools: product info and stock (8 points)
- [x] Tools that read `campus_customs.db`: description (`get_product_description`), price (`get_price`), stock by size (`get_stock`), plus the fast `quick_check`
- [x] The agent doesn't invent prices or quantities; it says clearly when a size is sold out (`tests/check_tools.py` 15/15)
- [x] `prompts/prompt.md` expanded so the agent calls these tools for price and stock questions
- [x] Return types in `models.py`: `QuickCheck`, `ProductDescription`, `PriceInfo`, `StockInfo`, `SizeStock`, `SearchResults`
- [x] `output/harness.md`: each tool, its model fields and why
- [x] I've added my own language to the harness Problem 6 section (a "Why it matters to the shopper" column)

## Problem 7: Chat search that updates the page (10 points)
- [x] Asking about a type of item ("what hoodies do you have?") makes the agent search, and the website shows the matches as product cards (image, name, price, short info)
- [x] API contract: the agent returns structured matches (`AgentReply.product_ids` + `search`); FastAPI returns cards + `page` (title, total, See-all link); the front end renders them
- [x] Chat-delivered cards still open the single-item page from Problem 3 (checked carefully: options, large image, price, description, sizes, stock, Add to cart)
- [x] Personal headline "We have Hoodies!"; results kept for the session; phone view folds the chat
- [x] `prompts/prompt.md` and `output/harness.md` explain how search results reach the page
- [x] Confirmed in the browser (`screenshots/p7_01` to `p7_03`) and by `tests/check_chat.py` 21/21

## Problem 8: Customer memory (8 points)
- [x] Logged-in chat history saved in `chat_messages` and reloaded on return (`GET /api/chat/history`; agent gets recent turns)
- [x] The agent knows who is chatting (name, email) through PydanticAI deps (`ShopDeps.customer`) and a `get_customer` tool; it calls shoppers by name
- [x] Page context (product on screen, selected size/color, filters, cart) passed with every message; code in `@agent.instructions` turns it into facts, so "do you have this in pink?" works
- [x] Guests can still chat; history persists only for logged-in users
- [x] `output/harness.md`: how history is stored, which customer fields the agent sees, how page context is passed
- [x] Proof: `tests/check_memory.py` 11/11, `screenshots/p8_01` to `p8_03`

## Problem 9: Usability improvements (12 points)
- [x] `output/usability.md` lists all 4 improvements in a grid: what we added, why, how it helps the shopper and business, where to see it in the app
- [x] Front end 1: bold quick-shop bar on every page; bolder names, prices and buttons (`QuickShopBar.tsx`, `styles.css`)
- [x] Front end 2: sticky Add to cart bar and bold stock badge on item pages (`StickyBuyBar.tsx`, `ProductPage.tsx`)
- [x] Agent 1: relevance search over names, categories and descriptions with shopper words (`backend/tools.py`); `tests/check_search.py` 12/12 vs 5/12 before
- [x] Agent 2: "why it fits" notes on recommended cards and a tighter reply shape (`models.py`, `main.py`, `prompt.md`, `ProductCard.tsx`)
- [x] Overall reasons: ease of use leads to more sales, a better experience and return shopping (section in `usability.md`)
- [x] Spacing: labels, the chat button and the Add to cart bar never cover an item or banner (moved, same size)
- [x] All four seen in the running app; proof in `screenshots/p9_01` to `p9_05`

## Problem 10: Style the website (6 points)
- [x] Asked in my own words what to do (prompt logged in `AI_prompts.md`)
- [x] Creative design across fonts, color, hierarchy, motion, product presentation and chat feel (`styles.css`, `index.html`)
- [x] Licensed Yale campus photos ("Postcards from campus", `CampusGallery.tsx`) and a slideshow of people in Yale gear ("Bulldogs in the wild", `Slideshow.tsx`), credited on the site
- [x] `output/design.md`: what changed and why it helps customers stick around and buy (concrete and short)
- [x] Seen in the running app; proof in `screenshots/p10_01` to `p10_07`

## Problem 11: Site testing (app check) (8 points)
- [x] Asked in my own words what to do (prompt logged in `AI_prompts.md`)
- [x] `output/app_check.html` opens by double-click; heading, screenshot and "what this proves" for each check
- [x] Check 1: chat inventory level, matching the database (Pierson College Crewneck)
- [x] Check 2: dynamic search-result cards after "Show me your hoodies"
- [x] Check 3: Problem 9 usability feature (sticky Add to cart bar), plus the banner pausing on hover
- [x] Screenshots in `output/app_check_images/`, linked with relative paths

## Whole project (from the scenario)
- [x] **Running site:** the React + Vite TypeScript front end and FastAPI backend start cleanly (backend: `uvicorn main:app --reload --port 8000` from `backend/`)
- [x] **Database writes:** a new account in `users` (hashed password, Problem 4) and chats saved in `chat_messages` for logged-in shoppers (Problem 5, rows 23–24 for Ezra Stiles)
- [x] **Screenshots** in `screenshots/`: browsing products (`p3_*`), creating an account (`p4_*`), chats with matching product cards and honest price and stock answers (`p5_*`)
- [x] **Public GitHub repo** pushed: https://github.com/Louyale/campuscustomschat (URL ready for Canvas)
- [ ] **File tree** shown for the last problem
- [x] **Not committed:** `data/` (the database and product images) and `.env` (checked before every push)

## Problems 5 onward
_Added as each problem is given._
