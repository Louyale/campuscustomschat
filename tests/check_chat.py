"""Chat accuracy check: ask the live agent questions whose answers are known from the database.

Start the backend first (port 8000), then run:  python tests/check_chat.py

Each case checks the reply text and the product cards against campus_customs.db.
The agent is a language model, so wording varies; the checks look only for the facts.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8000"


def ask(message: str) -> tuple[str, list[str], float]:
    body = json.dumps({"message": message, "history": []}).encode()
    request = urllib.request.Request(f"{BASE}/api/chat", data=body, headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.load(response)
    return data["reply"], [p["product_id"] for p in data["products"]], time.perf_counter() - start


def has(text: str, *words: str) -> bool:
    return all(w.lower() in text.lower() for w in words)


def lacks(text: str, *words: str) -> bool:
    return not any(w.lower() in text.lower() for w in words)


SOLD_OUT = re.compile(r"sold out|out of stock|not available|unavailable|none left|0 left", re.I)
NOT_CARRIED = re.compile(r"don.t (carry|have|sell|stock)|do not (carry|have|sell)|no .*(in our|in the) catalog|not (carry|in our)|isn.t (in|part|listed)|aren.t (in|any|listed)|not listed|couldn.t find|could not find|no (scarves|ezra)", re.I)

CASES = [
    ("How much is the Basic Hoodie Big Yale?",
     lambda r, p: has(r, "$39.99") and "basic-hoodie-big-yale" in p),
    ("Is the Pierson College Crewneck in stock in size L?",
     lambda r, p: bool(SOLD_OUT.search(r)) and "pierson-college-crewneck" in p),
    ("How many XL Basic Hoodie Big Yale are left?",
     lambda r, p: bool(re.search(r"\b2\b|\btwo\b", r, re.I)) and "basic-hoodie-big-yale" in p),
    ("Does the Basic Hoodie Big Yale come in pink?",
     lambda r, p: bool(re.search(r"\bno\b|only|not", r, re.I)) and lacks(r, "yes, it comes in pink")),
    ("What hats do you have under $30?",
     lambda r, p: {"pom-beanie-3dy", "lo-profile-cap-2-y", "class-of-2026-big-y-hat"} <= set(p)
     and has(r, "$24.99", "$29.99")),
    ("Do you sell scarves?",
     lambda r, p: bool(NOT_CARRIED.search(r)) and not any("scarf" in x for x in p)),
    ("Do you have any Ezra Stiles college gear?",
     lambda r, p: bool(NOT_CARRIED.search(r)) and not any("ezra" in x for x in p)),
    ("What is the most expensive item you sell?",
     lambda r, p: has(r, "$199.99") and "brooks-brothers-bomber-jacket-yale" in p),
    ("Show me Morse college gear.",
     lambda r, p: {"morse-1-4-zip", "morse-logo-t-shirt"} <= set(p) and has(r, "$59.99", "$29.99")),
    ("Is the Lacrosse Left Chest Crewneck available in XS?",
     lambda r, p: bool(SOLD_OUT.search(r)) and "lacrosse-left-chest-crewneck" in p),
    ("What colors does the School of Management Crest T Shirt come in?",
     lambda r, p: has(r, "navy") and lacks(r, "comes in white", "available in white", "light blue option")),
    ("What are your store hours?",
     lambda r, p: has(r, "(475) 301-4205") and not re.search(r"\b\d{1,2}(:\d{2})?\s?(am|pm)\b", r, re.I)),
    ("What is your return policy?",
     lambda r, p: has(r, "30 days") and bool(re.search(r"tags", r, re.I))),
    ("Do you have a pink hat?",
     lambda r, p: "adjustable-y-w-vintage-foam" in p and bool(re.search(r"dusty rose", r, re.I))),
]


def main() -> int:
    passed = 0
    for question, check in CASES:
        try:
            reply, products, seconds = ask(question)
            ok = check(reply, products)
        except Exception as exc:  # network or server error counts as a failure
            reply, products, seconds, ok = f"ERROR {exc}", [], 0.0, False
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'} ({seconds:4.1f}s) {question}\n     -> {reply}\n     cards: {products}")
    print(f"\n{passed}/{len(CASES)} chat checks passed")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
