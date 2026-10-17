# Style Guide: Matching yalebulldogblue.com

Reference site: [yalebulldogblue.com](https://yalebulldogblue.com/), "Yale Bulldog Blue by Campus Customs". It runs on Shopify with the Empire 12.2.0 theme by Pixel Union. The values below come from the site's HTML and theme CSS, researched on 2026-10-16. The Campus Customs site we build should use them so its format and colors match.

## 1. Design tokens

### Colors

| Token | Hex | Used for |
|---|---|---|
| `--navy` | `#00366b` | Primary buttons, brand color (announcement bar is `#00356b`) |
| `--navy-hover` | `#1a4a7a` | Primary button hover |
| `--navy-focus` | `#003161` | Primary button focus |
| `--text` | `#1d1d1d` | Body text, headings, header icons |
| `--text-hover` | `#3a3a3a` | Text hover |
| `--text-light` | `#949494` | Secondary text, struck-through compare-at price |
| `--link` | `#046e82` | Links, vendor line, selected size pill (teal) |
| `--link-hover` | `#046173` | Link hover |
| `--bg` | `#ffffff` | Page, header, nav and card backgrounds |
| `--bg-light` | `#f4f4f4` | Light panels, input hover |
| `--placeholder` | `#ededed` | Image placeholders |
| `--footer-bg` | `#f5f3ed` | Footer (cream) |
| `--footer-link` | `#282828` | Footer links |
| `--sale` | `#f04f36` | Sale badge background, sale price |
| `--in-stock` | `#3c9342` | In stock |
| `--low-stock` | `#e99114` | Low stock |
| `--no-stock` | `#bf262f` | Sold out |
| `--border` | `#dddddd` | Inputs and pills (hover `#cecece`) |
| `--input-text` | `#4d4d4d` | Input text |
| `--error` | `#f05d5d` on `#fce2e2` | Error messages |
| `--success` | `#51a551` on `#e0efe0` | Success messages |
| `--warning` | `#dfa354` | Warnings |
| `--star` | `#ffab41` | Review stars |

**Buttons:** the live theme CSS has a template bug, so how buttons actually render can't be confirmed. For contrast we use **navy `#00366b` with white text** for primary buttons. Secondary buttons have a white background, `#1d1d1d` text and a 1px `#1d1d1d` border. Both use weight 700, no uppercase, and a 0.3s transition.

### Typography (Open Sans 400/600/700 everywhere)

| Element | Style |
|---|---|
| Body | 16px (15px under 720px) |
| Headings h1–h4 | 400 weight, UPPERCASE; 1.9125 / 1.825 / 1.675 / 1.375 rem |
| Section titles | 400, normal case, centered, margin `50px 0 20px` |
| Nav | 600, UPPERCASE, 15px; hover lowers opacity to 0.8 |
| Product card title | 16px, 400, line-height 1.3125 |
| Price | 16px on cards, 22px on the product page |
| Announcement bar | 700, 14px, centered, padding `15px 0` |

### Layout
- Max content width is **1500px**. Gutters are 10px under 720px and 15px from 720px up.
- Breakpoints: 480, 680, 720, 860, 1024, 1080px.
- Product grid: **2 columns** under 680px (10px gap), **3 columns** from 680px, **4 columns** from 1024px (20px gap).
- Border radius is 3px on buttons and inputs; the chat frame uses 2px.
- Cards are white with 11px padding. On hover they get the shadow `0 2px 8px rgba(128,128,128,.2)` and switch to a second image.

## 2. Page structure

**Header (sticky, white with a shadow)**
1. Navy announcement bar with white text: "Officially Licensed Merchandise".
2. Main row: logo on the left (max 187×70px), a live search box with a product dropdown, and a "Login" link plus a cart icon with a count badge on the right. On mobile the left side shows a hamburger menu and a search icon instead.
3. Nav row: **Clothing · Accessories · Home · Collections · Residential Colleges · Sports · Relatives · Graduate & Professional Schools**. Each item opens a full-width mega-menu with columns of links and a promo image that zooms to 1.05 on hover.

**Home page, in order:** a full-width hero image linking to all products (about 2.57:1, no text) → "Show your residential college pride!" product carousel → a "Shop Bulldog Blue / Casual comfort, classic Bulldog pride." banner with a Shop All button → "Big Spirit, Big Yale" carousel → a 3-block promo mosaic → "Hats Off 🧢" carousel → a "Come Visit Us!" map showing 57 Broadway, New Haven CT 06511.

**Product card:** square image → sale badge ("Save X%", 13px, bottom-left of the image) → title → price (a sale shows the sale price in `#f04f36` and the compare-at price in grey with a line-through) → a short spec line (for example "65% Cotton, 35% Polyester Fleece / Relaxed Fit") → "Quick shop" (secondary) and "Choose options" (primary) buttons.

**Collection / search page:**
- A breadcrumb at the top.
- Left sidebar "Filters": **Availability** (In stock / Out of stock, with counts) and **Price** (From $ / To $).
- **Sort by:** Featured, Best selling, A–Z, Z–A, Price low–high, Price high–low, Date new–old, Date old–new.
- A grid/list toggle and 24 products per page with numbered pagination.
- The search page heading reads `Search results for "hoodie"` with the result count.

**Product page:**
- A breadcrumb and an image gallery with thumbnails.
- The title (h1) and price.
- Size options as **text pills** (XS S M L XL 2XL) with the selected size shown after the label: "Size: M". The selected pill is teal `#046e82` with a 6% teal fill; unavailable sizes are struck through at 50% opacity.
- A quantity selector and an **Add to cart** button.
- Collapsible "Description" and "Shipping & Returns" sections, then recommendations.

**Cart:**
- The page heading is "Your cart". An empty cart shows "Your cart is empty" and a "Continue shopping" button.
- After an item is added, a flyout reads "Added to your cart:", then "Cart subtotal", then "View cart (n)".

**Account:** the live site sends login to Shopify's email-code system, so we build our own forms. **Log in:** Email, Password. **Create account:** First name, Last name, Email, Password. These map to `users.first_name`, `last_name`, `email` and `password_hash`.

**Footer (cream `#f5f3ed`, 50px top margin):** the Campus Customs logo and the "Yale Officially Licensed" badge, then links (Search, Terms of Service, Refund Policy, Privacy Policy, Contact), then "Copyright © 2026 Yale Bulldog Blue by Campus Customs."

## 3. Store facts for the agent prompt

- **Store:** Yale Bulldog Blue by Campus Customs (run by Campus Clothing Company, Inc.). It sells officially licensed Yale merchandise: "shirts, hoodies, hats, and gifts for students, alumni, and fans."
- **Visit:** 57 Broadway, New Haven, CT 06511. **Phone:** (475) 301-4205. **Email:** orderdept@campuscustoms.com.
- **Hours:** not published, so the bot should suggest calling.
- **Shipping:**
  - Items are **made to order**. Production takes 5–8 business days; the product page says 8–10 business days, and it can run longer at peak times.
  - Shipping time comes on top of that. Most domestic orders ship by UPS, and a tracking email is sent when the order ships.
  - International shipping is available; the customer pays duties and customs fees.
- **Returns:**
  - Customers have **30 days from the ship date**. Items must be unworn and unused, with the original tags.
  - Final-sale and custom items (such as Custom Alumni) can't be returned.
  - If the store made a mistake, the store pays return shipping. Otherwise the customer pays and should use insured, trackable shipping.
  - Refunds take 2–10 business days and don't include the original shipping.
- **Voice:** warm, short and upbeat, with Yale pride ("Bulldog pride", "We want you to love your purchase!").
- **Data honesty:** prices and stock **must** come from `catalogue` and `inventory` in `campus_customs.db`, never from the live site. The database prices were synced to the live store on 2026-10-16 (`update_prices.py`); rerun it to refresh them.

## 4. Chatbot recommendations that fit this format

The live site uses a Zendesk widget titled "Order Support": a circular launcher at the **bottom-left** labelled "Hey! Need Help?", in colors `#0b233f`, `#004f88` and `#124d7a`. Our chatbot can replace it in the same place, with these improvements:

1. **Same launcher spot, store colors.** A navy `#00366b` circle at the bottom-left with a "Hey! Need Help?" label pill, so returning shoppers recognise it.
2. **Theme-styled panel.** A white panel with a navy header bar like the announcement bar, Open Sans, `#1d1d1d` text, 2–3px corners, and the card shadow `0 2px 8px rgba(128,128,128,.2)`.
3. **Bubbles.** Shopper messages are navy with white text; bot messages are `#f4f4f4` with `#1d1d1d` text; links are teal `#046e82`.
4. **Product cards in chat.** Matching items reuse the site's product card (square image, title, price, "View product"). Several results show as a horizontal carousel like the home page, and the same items **appear on the page grid** too, as the assignment requires.
5. **Size and stock pills.** Sizes show as the theme's text pills. Each size's stock comes from `inventory` and uses the stock colors: in stock `#3c9342`, low `#e99114`, sold out `#bf262f`, with sold-out sizes struck through.
6. **Quick-reply chips from the nav.** Clothing, Residential Colleges, Sports, Relatives, Grad Schools, plus "Shipping times" and "Returns & exchanges". Chips are uppercase, weight 600, 13–15px.
7. **Honest answers.** Price and stock always come from tool calls against the database. If an item isn't in the catalogue, the bot says so and suggests the closest match; it never invents products, colors or prices.
8. **Policy answers.** The facts in section 3 go in the system prompt so shipping and return questions get exact answers, and anything unknown, such as hours, points to the phone number or email.
9. **Logged-in personalisation.** If the shopper is signed in, the bot greets them by first name and keeps their chat history in `chat_messages`.
10. **Clear states.** A typing indicator while the agent works, errors shown as `#f05d5d` on `#fce2e2`, and success messages (for example "Added to your cart") as `#51a551` on `#e0efe0`, mirroring the cart flyout wording.

## Not verified
- How buttons actually render, because of the template bug.
- The fields on the live registration page.
- Store hours.
- Exact mega-menu spacing.
- Whether the Zendesk widget appears on every page.
