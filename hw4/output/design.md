# Problem 10: Style the website

**Goal:** make the site feel like a real Campus Customs storefront on Broadway: proud, collegiate, a little playful. Shoppers should stay longer, look around more and buy more. We kept the Yale Bulldog Blue look (navy, white, cream) and built on it.

## What we changed and why it helps customers stick around and buy

| # | Area | What we changed | Why it helps shoppers stay and buy | Where to see it |
|---|---|---|---|---|
| 1 | **Fonts and hierarchy** | Big headings now use a collegiate serif (Libre Caslon), and body text stays Open Sans. Section titles get a two-tone navy and sky-blue underline. The hero headline is larger. | It reads like Yale, not a generic template, which builds trust right away. A clear hierarchy (big title, short intro, then products) lets shoppers scan quickly and find their section. | Every page: "Best sellers", "Bulldogs in the wild", "Postcards from campus". *`p10_01`, `p10_02`* |
| 2 | **Campus photo in the hero, with motion** | Harkness Tower sits behind the navy hero and drifts slowly (Ken Burns). The three product photos lift on hover. | The first screen says "this is New Haven" before anyone scrolls. Gentle motion catches the eye and pulls people down the page. | Home, top. *`p10_01`* |
| 3 | **"Bulldogs in the wild" slideshow** (people wearing and using Yale gear) | 6 photos: Handsome Dan in his Y bandana, the football team, Yale cheer, Yale hockey, the Yale band and decorated Commencement caps. It plays on its own, pauses on hover, and has arrows, a pause button and dots. Each slide has a **"Shop the look"** button. | **Relatability:** shoppers picture themselves, their kid or their team in the gear. That "that could be me" moment makes them engage and buy, and every slide leads straight to matching products. | Home, after Best sellers. *`p10_03`, `p10_07` (phone)* |
| 4 | **"Postcards from campus" gallery** | 8 campus photos in a mosaic: Harkness, Branford in autumn, Sterling, Cross Campus, Beinecke at night, Old Campus at dusk, Davenport in snow, the Yale Bowl. Click any photo to open it large and flip through with the arrows. | **Engagement and nostalgia:** alumni and parents linger on places they love, and students see their own campus. Time spent on the page builds attachment to the brand, and a shopper who feels at home comes back. | Home, before Visit the shop. *`p10_04`, `p10_05`* |
| 5 | **Spirit ticker** | A slow navy band of Yale cheers ("Boola Boola", "Bulldogs, Bulldogs, Bow Wow Wow", "Lux et Veritas", "Beat Harvard"). It stops while the mouse is over it (tap to pause on phones), with a "Hover to pause" / "❚❚ Paused" label in its own slot. | Personality and in-jokes make the shop feel like an insider's store, not a big-box site, and that is why fans pick us. | Home, under the trust bar. *`p10_02`* |
| 6 | **Product presentation** | Cards lift on hover with a deeper shadow, the product name underlines, and photos sit on a soft white stage. Best-seller labels sit cleanly under the photo (Problem 9). | It feels responsive and premium, invites the next click, and makes the products look worth the price. | Products page and every product row |
| 7 | **Chat feel** | The chat header is navy with a Handsome Dan avatar, a serif title and a green "online" dot. Replies are soft bubbles with Dan's avatar beside them. The chat button pulses three times on load to invite a first question. | A friendly face makes the chat feel like a helpful clerk, not a bot, so more shoppers ask. Shoppers who ask about size and stock are much closer to buying. | Chat on any page. *`p10_06`* |
| 8 | **Scroll-in motion** | Home sections fade up as they scroll into view. | The page feels alive and rewards scrolling, so shoppers see more products. | Home, while scrolling |

## Why this makes customers stick around and buy more

- **Relatable** (people in Yale gear): shoppers see themselves in the product, which is the strongest push to buy apparel.
- **Engaging** (campus postcards, slideshow, ticker): more time on the site means more products seen and more chances to add to the cart.
- **Trustworthy** (serif type, real campus, consistent Yale navy): a polished, official look makes shoppers comfortable paying.
- **Easy to act on** ("Shop the look" buttons, inviting chat): every moment of interest is one click from a product.
- **Memorable, so they come back:** a shop that feels like campus is the one alumni and families return to before The Game, Family Weekend and Commencement.

## Care we took

- **Photo rights:** all 14 photos come from Wikimedia Commons under open licenses (public domain, CC BY or CC BY-SA). The photographer, license and a link to the source are shown on every slide and in the large photo view (`frontend/src/photoCredits.ts`).
- **Accessibility:**
  - every photo has descriptive alt text
  - the slideshow has labeled buttons and can be paused
  - the large photo view closes with Esc and works with the arrow keys
  - shoppers who turn on "reduce motion" get no auto-play, drifting or ticker motion
- **Spacing:** nothing new covers products. The chat button keeps its own lane on the right (Problem 9).
- **Speed:** photos are resized to 1600 px wide (about 6 MB in total), and those lower on the page load only when you scroll to them.

**Files:**
- **New:**
  - `frontend/src/components/Slideshow.tsx`
  - `frontend/src/components/CampusGallery.tsx`
  - `frontend/src/components/SpiritTicker.tsx`
  - `frontend/src/reveal.ts`
  - `frontend/src/photoCredits.ts`
  - `frontend/public/photos/`
- **Changed:** `pages/Home.tsx`, `components/ChatWidget.tsx`, `content.ts` (Shop the look links), `styles.css`, `index.html` (font)
