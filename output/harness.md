# Campus Customs Harness

This harness describes how the Campus Customs website and chatbot are set up. It grows with each problem: database, models, tools, safety and specs.

---

## Problem 2: Analyze the database

**Database:** `data/campus_customs.db` (SQLite). It is used locally and never committed to GitHub.

| Table | Rows | What it holds | Links to |
|---|---|---|---|
| `catalogue` | 102 | One row per product the shop sells | (none) |
| `inventory` | 612 | Stock for each product in each size (102 products × 6 sizes) | `catalogue.product_id` |
| `users` | 3 | Customer accounts (one test user is already there) | (none) |
| `chat_messages` | 22 | Saved chatbot conversations | `users.id` |

SQLite also creates `sqlite_sequence` by itself to track the next `id` for the auto-numbered tables. It is not shop data.

### Tables and fields

The **Why it matters** column holds a proposed reason for each field. Edit any cell to put it in your own words; just keep the `|` dividers.

#### `catalogue`: the products

| Field | Type | Rules | Example | Why it matters |
|---|---|---|---|---|
| `product_id` | TEXT | Primary key; matches the product's web address on yalebulldogblue.com | `basic-hoodie-big-yale` | The one ID that ties a product to its stock, its photo and the chat, so the bot always talks about the right item. |
| `name` | TEXT | Required | `Basic Hoodie Big Yale` | What shoppers see on the product card and what the bot calls the item, so there's no confusion. |
| `garment_type` | TEXT | Required; free text with 22 different spellings | `pullover hoodie` | Lets the site filter and the bot answer "show me hoodies"; the spellings need grouping first. |
| `description` | TEXT | Required | `Navy pullover hoodie with a front kangaroo pocket…` | Gives the bot real details (fit, pocket, logo) so it can answer questions without making things up. |
| `colors` | TEXT | Required; a JSON list stored as text | `["navy blue", "white"]` | Answers "do you have this in pink?" honestly: if a color isn't listed, the bot says so. |
| `search_tags` | TEXT | Required; a JSON list stored as text | `["Yale hoodie", "navy hoodie", "college sweatshirt", …]` | Extra keywords that help search and the bot match casual requests like "college sweatshirt". |
| `image_file_path` | TEXT | Required; a path relative to `data/` | `products/basic-hoodie-big-yale.jpg` | Shows the product photo on the page and in the chat cards. |
| `price` | REAL | Required; US dollars (synced to the live store) | `39.99` | The only price the bot may quote, so customers are never told a wrong price. |

#### `inventory`: stock by size

| Field | Type | Rules | Example | Why it matters |
|---|---|---|---|---|
| `id` | INTEGER | Primary key, auto-numbered | `13` | Gives each stock row its own number so it can be updated safely. |
| `product_id` | TEXT | Required; foreign key → `catalogue.product_id` | `basic-hoodie-big-yale` | Links each stock count back to the right product. |
| `size` | TEXT | Required; one of XS, S, M, L, XL, XXL | `M` | Shoppers buy by size, so the bot must check the exact size they ask for. |
| `quantity` | INTEGER | Required; units in stock, 0 to 25 (145 rows are 0) | `20` | Tells the bot whether a size is in stock, low or sold out, so it never promises a size we don't have. |

Each (`product_id`, `size`) pair appears only once.

#### `users`: customer accounts

| Field | Type | Rules | Example | Why it matters |
|---|---|---|---|---|
| `id` | INTEGER | Primary key, auto-numbered | `1` | Identifies each customer and links them to their saved chats. |
| `name` | TEXT | Required; full name | `Test User` | The full name on the account, used in the header and on orders. |
| `email` | TEXT | Required; unique | `test@campuscustoms.yale.edu` | The login name; being unique stops two accounts sharing one email. |
| `password_hash` | TEXT | Required; PBKDF2-SHA256 hash, never the plain password | `pbkdf2_sha256$<salt>$<hash>` | Checks the password at login without ever storing the real password; the bot must never see or reveal it. |
| `created_at` | TEXT | Required; defaults to the time the row was added (UTC) | `2026-09-19 11:34:09` | Shows when the customer joined, which helps the shop track new sign-ups and loyalty. |
| `first_name` | TEXT | Optional | `Test` | Lets the bot greet the shopper by name ("Hi Test!") for a friendlier chat. |
| `last_name` | TEXT | Optional | `User` | Completes the customer's name for the account and orders. |

#### `chat_messages`: saved conversations

| Field | Type | Rules | Example | Why it matters |
|---|---|---|---|---|
| `id` | INTEGER | Primary key, auto-numbered | `2` | Keeps the messages in order so a conversation replays correctly. |
| `user_id` | INTEGER | Required; foreign key → `users.id` | `1` | Ties each message to the customer, so they see only their own chat history. |
| `role` | TEXT | Required; `user` or `assistant` | `assistant` | Tells apart what the shopper said and what the bot answered. |
| `content` | TEXT | Required; the message text | `We carry these hoodies…` | The actual words, which give the bot memory of the conversation and the shop a record of questions. |
| `products_json` | TEXT | Optional; JSON list of the products the bot showed | `[{"product_id": "basic-hoodie-big-yale", …}]` | Lets the page show the same matching products again when the chat reloads for future sales. |
| `created_at` | TEXT | Required; defaults to the time the row was added (UTC) | `2026-09-19 11:40:23` | Timestamps each message so chats can be sorted and reviewed later, which helps keep track of conversations. |
