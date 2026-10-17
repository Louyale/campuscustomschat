# Campus Customs: store website and chatbot (HW4)

Everything for the homework is in the **[`hw4/`](hw4/)** folder. Start with **[`hw4/README.md`](hw4/README.md)** for how to place the data pack and run the front end and back end.

## File tree

The required layout, as it is in this repo. The **complete** tree of every file is in **[`hw4/TREE.md`](hw4/TREE.md)**.

```
hw4/
├── AI_prompts.md                 # every prompt, by problem
├── requirements.txt
├── .env.example                  # placeholders only
├── .gitignore
├── README.md                     # how to run the front end and back end
├── TREE.md                       # the complete file tree
├── frontend/                     # Vite React TypeScript app
├── backend/
│   ├── main.py                   # FastAPI app — run with: uvicorn main:app --reload
│   ├── agent.py
│   ├── models.py
│   ├── tools.py
│   └── prompts/
│       └── prompt.md
└── output/
    ├── harness.md
    ├── design.md
    ├── usability.md
    ├── app_check.html
    ├── app_check_images/         # screenshots linked from app_check.html
    └── audit_trail.json
```

Also in `hw4/` (extras that support grading): `backend/auth.py` (accounts), `tests/` (automated checks), `screenshots/` (evidence per problem), `EVIDENCE_CHECKLIST.md`, `STYLE_GUIDE.md`, and the data helpers `add_products.py`, `update_prices.py` and `check_portkey.py`.

The agent itself is four files under `hw4/backend/`: `prompts/prompt.md`, `agent.py`, `tools.py` and `models.py`.

## Local-only data pack (not in git)

```
hw4/data/
├── campus_customs.db
└── products/                     # images referenced by the catalogue
```

The course data pack, the real `.env` and product images are never committed (see `hw4/.gitignore`).
