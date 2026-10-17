# Problem 9: Usability improvements

Campus Customs already had a working shop and chat. Problem 9 makes them **easier and faster to use**. There are four improvements: two on the front end and two in the agent/backend. Each one is in the running app, and the table says exactly where a grader can see it.

## The four improvements at a glance

| # | Type | What we added | Why we added it | How it helps the shopper and the business | Where to see it in the running app |
|---|---|---|---|---|---|
| 1 | Front end | **Bold quick-shop bar and easier-to-find buttons.** A navy bar under the main menu on every page with bold, pill-shaped links: Best Sellers, Hoodies, Crewnecks, Tees, Hats, Accessories, Bulldog Athletics, Low-Key Yale. The page you are on is highlighted in white. Product names, prices and the Add to cart / Check options buttons are bolder. "Best seller" and "Sold out" labels sit in their own row under the photo, never on top of it. | Before this, shoppers had to open Products and then use the filters to reach a category. The most-shopped categories were two clicks away, and prices and buttons were easy to skim past. | Any category is **one click from any page**. Bold names, navy prices and heavier buttons make it obvious what to click. Shoppers reach the item they want sooner, and fewer leave before finding it. | Every page, under HOME / PRODUCTS. Click **HATS**: the Hats pill turns white and the grid shows hats. *Screenshot `p9_01`* |
| 2 | Front end | **Sticky "Add to cart" bar and bold stock badge on item pages.** When the page's own Add to cart button is off screen, a bar docks just under the menu (it never floats over the product, a banner or the chat button) with the photo, name, price, stock, a size menu (in-stock sizes only) and **Add to cart**. Next to the price, a colored badge shows stock for the chosen size: "In stock in L", "Only 2 left in XL", "Sold out in L". One-size items (hats, mugs, pennants) come pre-selected. The main button is larger. | Long item pages, with the photo, description, stock table and details, pushed the button out of view, especially on phones. Shoppers had to scroll back up to buy, and stock was buried in a table. | **Buying is always one tap away**, with only sizes that can actually ship. Shoppers know right away whether their size is available, and a "low stock" badge gives a reason to buy now. More visits end in a sale and fewer orders run into sold-out sizes. | Open any item, e.g. **Yale Sports Hoodie Hockey**, and scroll down: the bar appears under the menu. Pick a size and press Add to cart: the cart count goes up. The badge is next to the price. *Screenshots `p9_02`, `p9_03`* |
| 3 | Agent / backend | **Smarter, more accurate product search** that reads **names, categories, styles, tags, colors and descriptions**. It understands shopper words ("cup" means mug or tumbler, "tee" means T-shirt, "dorm" means pennants and decor, "cap" means hat, "sticker" means decal). When the shopper names a kind of item, that category ranks first. Results are ranked by relevance, and a name or category match counts more than a passing word in the description. The agent searches with the **shopper's own words** and uses `matched_on` to drop items that only matched by chance. | The old search needed every word to appear exactly as typed. Everyday requests like "coffee cup", "tee for my dad", "sticker" or "gift for grandma" found **nothing**, so the agent had to say no or guess. | Shoppers can ask the way they talk and get the right item. When the agent answers correctly, people trust it and buy. "We don't have that", when we actually do, is a lost sale. | Open the chat and type **"I need a coffee cup for my dad"** (you get the Yale Relative Mug – Dad), or **"something for my dorm wall under $30"** (you get pennants). Proof: `tests/check_search.py` → `output/search_check.txt`. *Screenshot `p9_04`* |
| 4 | Agent / backend | **Better replies with "why it fits" notes.** Each product the agent recommends now carries a short note built only from database facts, such as "✓ Navy · $14.99 · best seller" or "✓ Pierson crest · in stock in M". The note shows on the product card in the chat and on the page. Replies follow a set shape: the answer first (yes or no, price, stock), then one or two picks with a real detail, and no filler questions at the end. | Replies listed products but did not say *why* each one fit, so shoppers had to open every card to compare. Some replies were long before they got to the answer. | Shoppers **compare picks at a glance** and decide faster. Short, direct answers feel like a helpful store clerk, which builds trust. The notes come from tool facts, never invented, so they stay accurate. | Ask the chat for **"something for my dorm wall under $30"** or **"a coffee cup for my dad"**. Each card shows a green ✓ note under the price. *Screenshot `p9_04`* |

## Spacing rule: nothing covers an item

Labels and floating controls were moved, not shrunk, so they never sit on a product or banner:

| What moved | Where it is now | Why |
|---|---|---|
| "Best seller" / "Sold out" labels | Their own row under the photo, same size; the row keeps its height so names line up across the grid | The label no longer hides part of the product photo |
| Chat button (same size) | Its own lane on the right: page text, cards and footer stay out of the lane, while full-width banner colors still reach the edge. On phones it sits in its own band at the bottom, and the page ends above it. | The button never covers a product, price or button |
| Sticky Add to cart bar | Docked under the menu, as part of the header. The item photo sticks below it. | It never covers the product, the chat button or the footer |

## Why ease of use grows sales and brings shoppers back

| Usability gain | What it does for the customer | What it does for Campus Customs |
|---|---|---|
| **Fewer clicks to the right item** (quick-shop bar, smarter search) | Less hunting; the shop feels simple | Fewer people give up before they find something, so more visits turn into sales |
| **Buy button always in reach** (sticky bar, pre-selected one-size items) | No scrolling back up, especially on a phone | Fewer abandoned item pages, so more items go in the cart |
| **Honest stock up front** (bold badge, only in-stock sizes offered) | No surprise "sold out" at checkout | Fewer failed orders and refunds; "Only 2 left" gives a reason to buy now |
| **Accurate answers in plain words** (synonyms, categories, descriptions) | "It understood what I meant" | Shoppers trust the chat and come back to it instead of a competitor |
| **Clear reasons for each pick** ("why it fits" notes) | Decide quickly, with confidence | Faster decisions, larger baskets, fewer returns |
| **A polished, bold look that matches the Yale Bulldog Blue store** | The shop feels official and trustworthy | A good first impression and a smooth visit **bring shoppers back**: parents before Family Weekend, students before The Game, alumni at Reunions |

**In short:** when the shop is easier to use, more visitors find the item they want, buy it with confidence, and have a good experience. That experience is what brings them back to Campus Customs the next time they need Yale gear.

## Evidence

| Check | Result |
|---|---|
| `tests/check_search.py` → `output/search_check.txt` | **Before:** 5 of 12 everyday queries found anything. **After:** 12 of 12 put the right kind of item in the top 3 ("coffee cup", "coffee cup dad", "tee for my dad", "something for my dorm wall", "navy hoodies", "gift for grandma", "sticker", "hockey hoodie", "pierson crewneck", "winter hat", "tie", "baseball cap"). Each search takes about 10–40 ms. |
| Regression tests, re-run after the changes | `check_tools.py` **15/15**, `check_auth.py` **16/16**, `check_memory.py` **11/11**; `check_chat.py` re-run in progress at push time |
| `screenshots/p9_01_quick_shop_bar_bold_cards.jpg` | Quick-shop bar with **HATS** active; "Best seller" labels under the photos; bold names and prices |
| `screenshots/p9_02_sticky_add_to_cart_bar.jpg` | The Add to cart bar docked under the menu after scrolling, size M chosen ("Low stock · 5 left") |
| `screenshots/p9_03_stock_badge_by_price.jpg` | "Only 5 left in M" badge next to the price; the docked bar sits above the photo, not on it |
| `screenshots/p9_05_phone_chat_lane.jpg` | Phone view: the chat button in its own band at the bottom; the page ends above it |
| `screenshots/p9_04_chat_dad_mug_why_it_fits.jpg` | Chat "I need a coffee cup for my dad" finds the Dad mug, with a "✓ Navy · $14.99" note |

## Files changed

- **Front end:** `frontend/src/components/QuickShopBar.tsx` (new), `frontend/src/components/StickyBuyBar.tsx` (new), `Header.tsx`, `pages/ProductPage.tsx` (stock badge, one-size pre-select, bigger button), `ProductCard.tsx` (note line, labels row), `api.ts`, `styles.css`
- **Agent / backend:** `backend/tools.py` (`query_terms`, `score_products`, relevance sort, `matched_on`), `backend/models.py` (`ProductNote`, `AgentReply.product_notes`, `ProductMatch.matched_on`), `backend/main.py` (attaches notes to cards), `backend/prompts/prompt.md` (search with the shopper's words, "why it fits" notes, shape of a good reply)
- **Tests:** `tests/check_search.py` (new)
