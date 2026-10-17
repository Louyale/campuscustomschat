# HW4 file tree

The complete layout of this `hw4/` folder as it is in the GitHub repo (165 files), generated from git.
The four files that make up the agent are in `backend/`: `prompts/prompt.md`, `agent.py`, `tools.py` and `models.py`.

```
hw4/
├── AI_prompts.md                             # every prompt, by problem
├── requirements.txt                          # Python packages
├── .env.example                              # settings with placeholders only
├── .gitignore
├── README.md                                 # how to place the data pack and run the front end and back end
├── TREE.md                                   # this file
├── frontend/                                 # Vite React TypeScript app
│   ├── public/
│   │   ├── photos/
│   │   │   ├── campus/                       # 8 files: openly licensed campus photos
│   │   │   └── gear/                         # 6 files: openly licensed people-in-gear photos
│   │   ├── favicon.svg
│   │   └── handsome-dan.jpg
│   ├── src/
│   │   ├── components/
│   │   │   ├── CampusGallery.tsx
│   │   │   ├── ChatResultsSection.tsx
│   │   │   ├── ChatWidget.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── OptionsDialog.tsx
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductRow.tsx
│   │   │   ├── QuickShopBar.tsx
│   │   │   ├── Slideshow.tsx
│   │   │   ├── SpiritTicker.tsx
│   │   │   └── StickyBuyBar.tsx
│   │   ├── pages/
│   │   │   ├── About.tsx
│   │   │   ├── Account.tsx
│   │   │   ├── Cart.tsx
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── NotFound.tsx
│   │   │   ├── ProductPage.tsx
│   │   │   ├── Products.tsx
│   │   │   └── Register.tsx
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── auth.tsx
│   │   ├── cart.tsx
│   │   ├── chatResults.tsx
│   │   ├── content.ts
│   │   ├── main.tsx
│   │   ├── pageContext.ts
│   │   ├── photoCredits.ts
│   │   ├── reveal.ts
│   │   ├── styles.css
│   │   └── useFetch.ts
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/                                  # FastAPI app + PydanticAI agent
│   ├── main.py                               # FastAPI app — run with: uvicorn main:app --reload
│   ├── agent.py                              # agent wiring, loop limits, audit trail
│   ├── models.py                             # typed models
│   ├── tools.py                              # read-only catalogue tools
│   ├── prompts/
│   │   └── prompt.md                         # system prompt and safety rules
│   ├── auth.py                               # accounts and sessions
│   ├── bestsellers.json
│   └── fetch_bestsellers.py
├── output/                                   # write-ups and evidence
│   ├── harness.md                            # how the system works
│   ├── design.md                             # Problem 10
│   ├── usability.md                          # Problem 9
│   ├── app_check.html                        # Problem 11 (double-click to open)
│   ├── app_check_images/                     # 18 files: screenshots linked from app_check.html
│   ├── audit_trail.json                      # append-only agent log
│   ├── audit_check.txt
│   ├── auth_check.txt
│   ├── chat_check.txt
│   ├── memory_check.txt
│   ├── safety_check.txt
│   ├── search_check.txt
│   └── tools_check.txt
├── add_products.py
├── check_portkey.py
├── EVIDENCE_CHECKLIST.md                     # evidence per problem
├── screenshots/                              # 54 files: screenshots for each problem
├── STYLE_GUIDE.md
├── tests/                                    # automated checks
│   ├── check_audit.py
│   ├── check_auth.py
│   ├── check_chat.py
│   ├── check_memory.py
│   ├── check_safety.py
│   ├── check_search.py
│   └── check_tools.py
└── update_prices.py
```

## Local-only data pack (not in git)

Place the course data pack here before running (see [README.md](README.md)):

```
hw4/data/
├── campus_customs.db
└── products/                               # images referenced by the catalogue
```

Also local only: `hw4/.env` (copied from `.env.example`), `.venv/` and `frontend/node_modules/`. They are excluded by `.gitignore`.

## Required layout check

| Required by the assignment | In this folder |
|---|---|
| `AI_prompts.md`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md` | ✓ all five |
| `frontend/` (Vite React TypeScript app) | ✓ |
| `backend/main.py`, `agent.py`, `models.py`, `tools.py`, `prompts/prompt.md` | ✓ all five |
| `output/harness.md`, `design.md`, `usability.md`, `app_check.html`, `app_check_images/`, `audit_trail.json` | ✓ all six |
| No real `.env`, `campus_customs.db` or product images in git | ✓ |
