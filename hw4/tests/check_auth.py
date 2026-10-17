"""End-to-end check of create account and login against the running API.

Start the backend first (port 8000), then run:  python tests/check_auth.py

It checks:
  1. the seeded test user logs in (test@campuscustoms.yale.edu / password)
  2. a brand-new account can be created, then logs in with the same password
  3. the new row in `users` holds only a pbkdf2_sha256$salt$hash value (no plain password)
  4. wrong passwords, unknown emails, duplicate emails and weak passwords are refused
  5. the session cookie is HttpOnly and /api/auth/me knows who is logged in
  6. repeated failures lock the account out (20 minutes)
"""

from __future__ import annotations

import http.cookiejar
import json
import secrets
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8000"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
results: list[tuple[bool, str]] = []


def client() -> tuple[urllib.request.OpenerDirector, http.cookiejar.CookieJar]:
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)), jar


def call(opener, method: str, path: str, body: dict | None = None) -> tuple[int, dict | None, dict]:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with opener.open(request) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None, {k.lower(): v for k, v in response.headers.items()}
    except urllib.error.HTTPError as err:
        raw = err.read()
        return err.code, json.loads(raw) if raw else None, {k.lower(): v for k, v in err.headers.items()}


def check(ok: bool, label: str) -> None:
    results.append((ok, label))
    print(("PASS " if ok else "FAIL ") + label)


def main() -> int:
    # 1. Seeded test user
    opener, _ = client()
    status, body, headers = call(opener, "POST", "/api/auth/login",
                                 {"email": "test@campuscustoms.yale.edu", "password": "password"})
    check(status == 200 and body["email"] == "test@campuscustoms.yale.edu", "seeded test user logs in")
    cookie = headers.get("set-cookie", "")
    check("HttpOnly" in cookie and "SameSite=lax" in cookie.replace("Lax", "lax"), "session cookie is HttpOnly + SameSite")
    status, body, _ = call(opener, "GET", "/api/auth/me")
    check(status == 200 and body and body["first_name"] == "Test", "/me returns the logged-in test user")
    check("password_hash" not in json.dumps(body), "API never returns password_hash")
    call(opener, "POST", "/api/auth/logout")
    status, body, _ = call(opener, "GET", "/api/auth/me")
    check(body is None, "logout ends the session")

    # 2. Brand-new account
    email = f"bulldog.{secrets.token_hex(4)}@yale.edu"
    password = "Boola-1701-" + secrets.token_hex(4)
    opener, _ = client()
    status, body, _ = call(opener, "POST", "/api/auth/register",
                           {"first_name": "Handsome", "last_name": "Dan", "email": email, "password": password})
    check(status == 201 and body["email"] == email, f"new account created ({email})")
    opener, _ = client()
    status, body, _ = call(opener, "POST", "/api/auth/login", {"email": email.upper(), "password": password})
    check(status == 200 and body["first_name"] == "Handsome", "new account logs in (email is case-insensitive)")

    # 3. What the database stores
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    stored = con.execute("SELECT password_hash FROM users WHERE email = ?", (email,)).fetchone()[0]
    algorithm, salt, digest = stored.split("$")
    check(algorithm == "pbkdf2_sha256" and len(salt) == 32 and len(digest) == 64 and password not in stored,
          "users row stores pbkdf2_sha256$salt$hash, never the password")

    # 4. Refusals
    opener, _ = client()
    status, body, _ = call(opener, "POST", "/api/auth/login", {"email": email, "password": "wrong-password"})
    check(status == 401 and body["detail"] == "Invalid email or password.", "wrong password refused")
    status, body, _ = call(opener, "POST", "/api/auth/login", {"email": "nobody@yale.edu", "password": "whatever1"})
    check(status == 401 and body["detail"] == "Invalid email or password.", "unknown email gets the same message")
    status, _, _ = call(opener, "POST", "/api/auth/register",
                        {"first_name": "Copy", "last_name": "Cat", "email": email, "password": "Another-pass-1"})
    check(status == 409, "duplicate email refused")
    status, _, _ = call(opener, "POST", "/api/auth/register",
                        {"first_name": "Weak", "last_name": "Pass", "email": "weak@yale.edu", "password": "password"})
    check(status == 422, "common password refused")
    status, _, _ = call(opener, "POST", "/api/auth/register",
                        {"first_name": "Short", "last_name": "Pass", "email": "short@yale.edu", "password": "abc"})
    check(status == 422, "short password refused")
    status, body, _ = call(opener, "POST", "/api/auth/register",
                           {"first_name": "No", "last_name": "Number", "email": "nonum@yale.edu", "password": "NoNumbersHere"})
    check(status == 422 and "number" in body["detail"], "password without a number refused")
    status, _, _ = call(opener, "POST", "/api/auth/login", {"email": "x' OR '1'='1", "password": "' OR '1'='1"})
    check(status == 401, "SQL-injection style login refused")

    # 6. Rate limit (uses a throwaway email so real accounts aren't locked)
    target = f"lockout.{secrets.token_hex(3)}@yale.edu"
    codes, retry = [], ""
    for _ in range(6):
        status, _, headers = call(opener, "POST", "/api/auth/login", {"email": target, "password": "nope-nope"})
        codes.append(status)
        retry = headers.get("retry-after", retry)
    check(codes[:5] == [401] * 5 and codes[5] == 429 and 1100 < int(retry or 0) <= 1200,
          "after 5 failures in 15 minutes, login is locked for 20 minutes (429)")

    passed = sum(ok for ok, _ in results)
    print(f"\n{passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
