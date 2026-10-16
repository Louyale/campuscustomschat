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
- [x] Hats added to the catalogue (`add_hats.py`): Y pom beanies, Y caps, Class of 2026 hat
- [x] Screenshots: `screenshots/p3_01` to `p3_13` (home, best sellers, The Game, Handsome Dan, products, single item, chat, About Us, create account, mobile, hats row, 2026 hat, hats category)
- [x] I've reviewed the Home and About Us wording and made it my own (edited in `frontend/src/content.ts`)

## Problem 4: Create account and login (8 points)
- [x] Create account: first name, last name, email, password, confirm password
- [x] Log in: email and password
- [x] New accounts written to `users` with PBKDF2-HMAC-SHA256, 120,000 iterations, `pbkdf2_sha256$salt$hash`
- [x] Login re-hashes with the stored salt and uses a constant-time compare
- [x] Logged in as the seeded test user, and as a brand-new account (`screenshots/p4_*`, `output/auth_check.txt`, 16/16 checks)
- [x] `output/harness.md` explains what we store and how passwords are protected
- [x] I've reworded the harness auth section in my own words (code updated to match: 20-minute lockout, passwords need a number)

## Whole project (from the scenario)
- [ ] **Running site:** the React + Vite TypeScript front end and FastAPI backend start cleanly
- [ ] **Database writes:** a new account in `users` (hashed password): done in Problem 4. Chats saved in `chat_messages`: still to do. **Reminder:** the account pages already say chats are "safely saved", so build this with the chatbot (or soften the wording)
- [ ] **Screenshots** in `screenshots/`: browsing products, creating an account, a chat with matching items appearing on the page, honest price and stock answers
- [ ] **Public GitHub repo** pushed; its URL is ready for Canvas
- [ ] **File tree** shown for the last problem
- [ ] **Not committed:** `data/` (the database and product images) and `.env`

## Problems 2 onward
_Added as each problem is given._
