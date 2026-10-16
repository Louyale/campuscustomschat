"""Accounts: create account, log in, log out, and "who am I", backed by the users table.

How passwords are protected
- They are never stored or logged. We store PBKDF2-HMAC-SHA256 hashes in the same
  format as the seed data: pbkdf2_sha256$<salt>$<hex digest>, 120,000 iterations,
  a 32-byte digest, and a new random salt for every account.
- At login we never "un-hash". We read the salt out of the stored value, hash what
  the user typed with that salt and the same settings, and compare the two with a
  constant-time compare (hmac.compare_digest).

Other protections
- Login errors never say whether the email exists ("Invalid email or password"),
  and unknown emails still run one hash so the response time gives nothing away.
- Repeated failed logins are rate-limited: 5 failures in 15 minutes locks that
  email (from that address) out for 20 minutes (HTTP 429).
- Sessions are an HMAC-signed token in an HttpOnly, SameSite=Lax cookie, so page
  scripts (and anything injected into them) cannot read it. The signing key comes
  from SESSION_SECRET in .env.
- API responses never include password_hash, and all SQL uses ? parameters.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import APIRouter, Cookie, HTTPException, Request, Response
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / os.getenv("DATABASE_PATH", "data/campus_customs.db")  # same setting as main.py

# Hash settings: must match the seed data exactly, or correct passwords won't match.
ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000
DIGEST_BYTES = 32

COOKIE_NAME = "cc_session"
SESSION_SECONDS = 7 * 24 * 3600
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # set true when served over HTTPS
SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_hex(32)  # random fallback: sessions reset on restart

MAX_FAILURES = 5
FAILURE_WINDOW = 15 * 60
LOCKOUT_SECONDS = 20 * 60
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
COMMON_PASSWORDS = {"password", "password1", "12345678", "123456789", "qwerty123", "iloveyou", "letmein1",
                    "yaleyale", "bulldogs", "boolaboola"}

router = APIRouter(prefix="/api/auth", tags=["auth"])
_failures: dict[str, deque[float]] = defaultdict(deque)
_locked_until: dict[str, float] = {}


# ---------------------------------------------------------------- hashing

def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS, DIGEST_BYTES)
    return f"{ALGORITHM}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt, expected = stored.split("$")
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    candidate = hash_password(password, salt).split("$")[2]  # same salt from the stored value
    return hmac.compare_digest(candidate, expected)


_DUMMY_HASH = hash_password(secrets.token_hex(8))


# ---------------------------------------------------------------- sessions

def _sign(payload: str) -> str:
    return hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def make_session(user_id: int) -> str:
    payload = f"{user_id}.{int(time.time()) + SESSION_SECONDS}"
    return f"{payload}.{_sign(payload)}"


def read_session(token: str | None) -> int | None:
    """Return the user id for a valid, unexpired token, else None."""
    if not token or token.count(".") != 2:
        return None
    user_id, expires, signature = token.split(".")
    if not hmac.compare_digest(_sign(f"{user_id}.{expires}"), signature):
        return None
    if not expires.isdigit() or int(expires) < time.time() or not user_id.isdigit():
        return None
    return int(user_id)


def _set_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(COOKIE_NAME, make_session(user_id), max_age=SESSION_SECONDS, httponly=True,
                        samesite="lax", secure=COOKIE_SECURE, path="/")


# ---------------------------------------------------------------- data

def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


class PublicUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


def _public(row: sqlite3.Row) -> PublicUser:
    first = row["first_name"] or row["name"].split(" ")[0]
    last = row["last_name"] or " ".join(row["name"].split(" ")[1:])
    return PublicUser(id=row["id"], first_name=first, last_name=last, email=row["email"])


def current_user(token: str | None) -> PublicUser | None:
    user_id = read_session(token)
    if user_id is None:
        return None
    with _db() as con:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _public(row) if row else None


# ---------------------------------------------------------------- rate limiting

def _lockout_remaining(key: str) -> int:
    """Seconds left on a lockout for this email + address, or 0."""
    return max(0, int(_locked_until.get(key, 0) - time.time()))


def _record_failure(key: str) -> None:
    now = time.time()
    attempts = _failures[key]
    attempts.append(now)
    while attempts and attempts[0] < now - FAILURE_WINDOW:
        attempts.popleft()
    if len(attempts) >= MAX_FAILURES:
        _locked_until[key] = now + LOCKOUT_SECONDS
        attempts.clear()


# ---------------------------------------------------------------- routes

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _clean_name(value: str, label: str) -> str:
    value = " ".join(value.split())
    if not 1 <= len(value) <= 50 or any(ch in value for ch in "<>{}"):
        raise HTTPException(422, f"Please enter a valid {label} (1–50 characters).")
    return value


@router.post("/register", response_model=PublicUser, status_code=201)
def register(body: RegisterRequest, response: Response) -> PublicUser:
    first = _clean_name(body.first_name, "first name")
    last = _clean_name(body.last_name, "last name")
    email = body.email.strip().lower()
    if not EMAIL_RE.match(email) or len(email) > 254:
        raise HTTPException(422, "Please enter a valid email address.")
    if not 8 <= len(body.password) <= 128 or not any(ch.isdigit() for ch in body.password):
        raise HTTPException(422, "Password must be 8–128 characters and include at least one number.")
    if body.password.lower() in COMMON_PASSWORDS or body.password.lower() == email:
        raise HTTPException(422, "That password is too easy to guess. Please choose another.")

    with _db() as con:
        if con.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            raise HTTPException(409, "An account with that email already exists. Try logging in.")
        cursor = con.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            (f"{first} {last}", email, hash_password(body.password), first, last),
        )
        row = con.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    _set_cookie(response, row["id"])
    return _public(row)


@router.post("/login", response_model=PublicUser)
def login(body: LoginRequest, request: Request, response: Response) -> PublicUser:
    email = body.email.strip().lower()
    key = f"{request.client.host if request.client else '?'}|{email}"
    if remaining := _lockout_remaining(key):
        raise HTTPException(429, "Too many attempts. Please wait 20 minutes and try again.",
                            headers={"Retry-After": str(remaining)})

    with _db() as con:
        row = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    # Always run one hash so a missing email takes as long as a wrong password.
    valid = verify_password(body.password, row["password_hash"] if row else _DUMMY_HASH) and row is not None
    if not valid:
        _record_failure(key)
        raise HTTPException(401, "Invalid email or password.")

    _failures.pop(key, None)
    _locked_until.pop(key, None)
    _set_cookie(response, row["id"])
    return _public(row)


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=PublicUser | None)
def me(cc_session: str | None = Cookie(default=None)) -> PublicUser | None:
    return current_user(cc_session)
