# AI Prompts Log: Campus Customs Website (HW4)

This is the log of what I typed to my vibe coder (Claude Code) while building the Campus Customs website: a React + Vite TypeScript front end, a FastAPI backend, and a PydanticAI chatbot that answers from a local database. There is one section per problem, each with the problem number and title, my main prompt in my own words, a follow-up prompt where I needed one (plus one sentence on what was lacking after the first), and the outcome. Prompts are quoted exactly as I typed them, typos included. The running site, the database writes and the screenshots are the evidence. Setup prompts typed before Problem 1 are in the appendix, so the full conversation is visible.

**Assignment:** Campus Customs needs a real customer website with a helpful chatbot. Shoppers browse products, create an account, chat about merch, see matching items appear on the page, and get honest answers about price and stock from the local `campus_customs.db`. The finished project goes in a public GitHub repo (no database or product images).

## At a glance

| # | Problem | Main prompt was about | Follow-up fixed | Main output |
|---|---|---|---|---|
| 1 | Vibe coder prompts | Create this log with one section per problem | (none needed) | `AI_prompts.md`, `EVIDENCE_CHECKLIST.md` |
| 2 | Analyze the database | Show each table and its fields, with space for my one-line reasons | Show the 4 tables with real rows so I can write the reasons | `output/harness.md` |
| 3 | Build the Campus Customs website | Main pages in my voice, Products + single-item pages, bottom-right chat stub, FastAPI backend | (in progress) | `frontend/`, `backend/main.py` |

---

## Problem 1: Vibe coder prompts

**Prompt (my own words):**

> Let's gooooo.  If you haven't already, create the prompts.md file, and be sure to put one section for each problem with the problem number and title.  This is problem 1.  Note what the evidence will be that I'll need and be sure that I have all that evidence at the end when i ask you to grade me.

**Follow-up prompt:** none needed. The log was created at the start of the assignment (see the appendix), and this prompt reorganised it into one section per problem.

**Outcome:** this file, organised as `## Problem N: <title>` sections with an "At a glance" table, and updated after every prompt. I also added `EVIDENCE_CHECKLIST.md`, which lists the evidence each problem needs (running site, database writes, screenshots) so I can check that everything is there before grading.

---

## Problem 2: Analyze the database

**Prompt (my own words):**

> here is problem 2.  start by showing me each table and its fields.  then add a section where i can add a section where i can add one short line as to why each field matters for the shop or the chatbot.

**Follow-up prompt:**

> show me the 4 tables so i can see them and write the why it matters lines

**What was lacking after the first prompt:** the tables were in the file, but I wanted to see them laid out with real rows before writing my own reasons.

**Outcome:** Started `output/harness.md`. It lists all 4 tables (`catalogue`, `inventory`, `users`, `chat_messages`) with every field's type, rules and an example, plus how the tables link. Each table has a "Why it matters" column next to Example, with a proposed one-line reason for every field (25 in total) that I then edited into my own words.

> put the why in the tables with a column and row next to Example, make it fillable and give me a proposed reason why it matters for me to modify

**Result:** Replaced the separate fill-in table with a "Why it matters" column in each of the 4 field tables, and filled every cell with a proposed reason for me to edit.

> i want you to open the harness file here on this screen so i can easily see it and add the reasons

**Result:** Opened `output/harness.md` in the side pane at the field tables so I could edit the reasons directly.

> all changes have been made.  now save the list to harness and check off this for problem 2

**Result:** Confirmed my edited reasons are saved in `output/harness.md` (all 25 fields, tables intact) and ticked off Problem 2 in `EVIDENCE_CHECKLIST.md`. **Problem 2 complete.**

> you can now close the harness file here

**Result:** Closed the harness file pane.

> yo make me a repo called campuscustomschat

**Result:** Created the empty **public** GitHub repo https://github.com/Louyale/campuscustomschat under my account (Louyale). Nothing has been pushed yet.

---

## Problem 3: Build the Campus Customs website

**Prompt (my own words):**

> Problem 3 is attached.  create the main pages on the website, and use the bulldogblue language as a template but rewrite the pages, especially the home and the about us in my voice.  use my voice as an attorney who is also an ultrarunner - so clear and efficient but with some outdoorsy language and not super formal  - academic but not too serious, and well rounded.  We want this to relate to Yale students and families but not be stuffy.  highlight and show a diverse array of products but emphasize best sellers and hoodies and hats.  show a shirt of yale beating harvard at The Game because Yale is superior, and Dan the bulldog.  add the chat interface and stub.  add the fastapi that can grow.  show me your work after you do all this

**Follow-up prompt:** (in progress)

**Outcome:**
- **Front end (`frontend/`):** React + Vite + TypeScript, styled with the yalebulldogblue.com colors and fonts from `STYLE_GUIDE.md`. The nav bar links to Home, Products, About Us, Log in and Create account.
- **Home:** written in my voice. It has a best-sellers row (ranked by the live store's "Best selling" order), a hoodie section, a feature on the 2025 Yale vs. Harvard "The Game" tee, a "Handsome Dan approves" bulldog section, collection tiles (Residential Colleges, Sports, Family, Grad Schools) and a visit-us block.
- **About Us:** written in my voice, not copied from the original site.
- **Products page:** product images from the database's image paths, with name, price and a short description. It has filters (category, collection, in stock, price), sorting and search.
- **Single-item page:** a large image on one side; on the other, the full description, price, colors, size pills and a stock-by-size table.
- **Chat:** a floating panel at the bottom right that calls the `/api/chat` stub.
- **Backend (`backend/main.py`):** a FastAPI app serving products, stock by size, categories, product images (with black backgrounds turned white) and the chat stub, ready to grow into the agent in Problem 5.
- **Hats:** the catalogue has no hats, so the hat section points shoppers to the shop instead of showing products that aren't in the database.

> yo all that stuff in the HW4 folder, push to this repo

**Result:** Turned `HW4/` into a git repo and pushed it to https://github.com/Louyale/campuscustomschat (branch `main`). The `.gitignore` kept out the database, product images, `.env`, `.venv`, `node_modules` and build output.

---

## Appendix: setup prompts (before Problem 1)

> yo- were going to work on a new project to build a website and post it to github.  first open and note this zip.  can you open the campus customs_db?

**Result:** Unzipped `data.zip` and inspected `campus_customs.db`: 4 tables (`catalogue` 102 products, `inventory` 612 size rows, `users` 3, `chat_messages` 22), plus 102 product images that all match the catalogue paths.

> https://yalebulldogblue.com/    here is the problem for HW4.  create a HW4 folder now as you did with HW3.  we're done with HW3.  note the instructions to the github and the website.  that should answer your question.  also note the template that we're working from, which i linked here.

**Result:** Created the `HW4/` folder with the data copied in, a `.gitignore` that keeps the database, images and `.env` out of the public repo, `.env.example`, this log, and a `README.md` recording the assignment notes and the style of yalebulldogblue.com.

> sounds good.  test to make sure a portkey works now.  also research the website really good so that all format and colors match and we can even recommend some related improvements for our chatbot that woirks well with the firmat too

**Result:** Added `check_portkey.py`. The first run failed with Cloudflare "error code: 1010" because Python's default User-Agent was blocked; after adding a User-Agent header, Portkey answered on both `gpt-6-luna` and `gpt-5.6-luna`. Researched yalebulldogblue.com in depth and wrote `STYLE_GUIDE.md` (exact colors, fonts, layout, page structures, store facts for the agent prompt, and 10 chatbot recommendations that fit the site's format).

> you da man, thanks!  i'll send problem 1 in a few.  make sure that all problems are saved in HW4 as we go and that they are titled the way we did last time so that an AI grader can see them clearly.  this may mean using the title of the problem

**Result:** Agreed to title every section `## Problem N: <exact problem title>` like HW3 and to save every problem's files in `HW4/`.

> make sure our database prices match the live store's prices.  thx.

**Result:** Added `update_prices.py`, which matched all 102 catalogue products to the live store by product handle and updated `catalogue.price` (now $24.99–$199.99 instead of $32–$98). The original database is backed up in `data/campus_customs.original.db`, and old vs new prices are listed in `data/price_changes.csv`.

> cool  thx

**Result:** Acknowledged; waiting for Problem 1.
