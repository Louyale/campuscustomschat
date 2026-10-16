"""Make one tiny Portkey chat request per model to confirm the AI route works.

Reads PORTKEY_API_KEY from HW4/.env (falls back to the workspace .env).
Never prints the key. Usage: python check_portkey.py [model ...]
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_env() -> None:
    for path in (HERE / ".env", HERE.parent / ".env"):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def check(model: str, api_key: str, base_url: str) -> bool:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: Portkey connection works."}],
        "max_completion_tokens": 200,
    }).encode()
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=body,
        # Cloudflare rejects urllib's default User-Agent with "error code: 1010"
        headers={
            "Content-Type": "application/json",
            "x-portkey-api-key": api_key,
            "User-Agent": "campus-customs-hw4/1.0",
        },
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
        reply = (data["choices"][0]["message"]["content"] or "").strip()
        print(f"OK    {model:<16} {time.perf_counter() - start:5.1f}s  reply: {reply!r}")
        return True
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace").replace(api_key, "[REDACTED]")[:300]
        print(f"FAIL  {model:<16} HTTP {exc.code}: {detail}")
    except Exception as exc:  # network errors, bad JSON
        print(f"FAIL  {model:<16} {type(exc).__name__}: {str(exc).replace(api_key, '[REDACTED]')}")
    return False


def main() -> int:
    load_env()
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        print("PORTKEY_API_KEY is missing from .env")
        return 1
    base_url = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")
    models = sys.argv[1:] or [os.getenv("OPENAI_MODEL", "gpt-6-luna")]
    results = [check(model, api_key, base_url) for model in models]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
