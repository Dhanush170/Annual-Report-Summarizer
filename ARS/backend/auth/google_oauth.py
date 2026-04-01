import os
import re
import json
import hmac
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from pydantic import BaseModel
from urllib.parse import urlencode

load_dotenv()

router = APIRouter()

# ── Config from .env ──
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
JWT_SECRET_KEY       = os.getenv("JWT_SECRET_KEY", "changeme-set-a-real-secret")
JWT_ALGORITHM        = "HS256"
JWT_EXPIRE_HOURS     = 24
FRONTEND_URL         = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL          = os.getenv("BACKEND_URL", "http://localhost:8000")

# ── Google OAuth endpoints ──
GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL  = "https://www.googleapis.com/oauth2/v3/userinfo"

USERS_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"
USERS_FILE.parent.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# JWT helpers
# ─────────────────────────────────────────────

def create_jwt(data: dict) -> str:
    """Creates a signed JWT token that expires in JWT_EXPIRE_HOURS."""
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str) -> Optional[dict]:
    """Decodes and verifies a JWT. Returns payload dict or None if invalid."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_users(users: dict) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def _hash_password(password: str, salt: Optional[str] = None) -> str:
    raw_salt = base64.b64decode(salt.encode("utf-8")) if salt else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), raw_salt, 200000)
    return f"{base64.b64encode(raw_salt).decode('utf-8')}:{base64.b64encode(digest).decode('utf-8')}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_b64, digest_b64 = stored_hash.split(":", 1)
    except ValueError:
        return False
    candidate = _hash_password(password, salt_b64)
    try:
        _, candidate_digest_b64 = candidate.split(":", 1)
    except ValueError:
        return False
    return hmac.compare_digest(candidate_digest_b64, digest_b64)


def _is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str


class SignInRequest(BaseModel):
    email: str
    password: str


# ─────────────────────────────────────────────
# OAuth routes
# ─────────────────────────────────────────────

@router.get("/login")
def login():
    """
    Step 1 — Redirect the browser to Google's OAuth consent screen.
    Frontend calls: window.location.href = 'http://localhost:8000/auth/login'
    """
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  f"{BACKEND_URL}/auth/callback",
        "response_type": "code",
        "scope":         "openid email profile",
    }
    query_string = urlencode(params)
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{query_string}")


@router.post("/signup")
def sign_up(req: SignUpRequest):
    name = req.name.strip()
    email = _normalize_email(req.email)
    password = req.password

    if not name:
        raise HTTPException(status_code=400, detail="Name is required.")
    if not _is_valid_email(email):
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    users = _load_users()
    if email in users:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    users[email] = {
        "name": name,
        "email": email,
        "password_hash": _hash_password(password),
        "created_at": datetime.utcnow().isoformat(),
        "provider": "local",
    }
    _save_users(users)

    jwt_token = create_jwt({
        "sub": f"local:{email}",
        "email": email,
        "name": name,
        "picture": None,
        "auth_provider": "local",
    })

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "email": email,
            "name": name,
            "picture": None,
            "auth_provider": "local",
        }
    }


@router.post("/signin")
def sign_in(req: SignInRequest):
    email = _normalize_email(req.email)
    password = req.password

    users = _load_users()
    record = users.get(email)

    if not record or not _verify_password(password, record.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    jwt_token = create_jwt({
        "sub": f"local:{email}",
        "email": email,
        "name": record.get("name") or email.split("@")[0],
        "picture": None,
        "auth_provider": "local",
    })

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "email": email,
            "name": record.get("name") or email.split("@")[0],
            "picture": None,
            "auth_provider": "local",
        }
    }


@router.get("/callback")
async def callback(code: str):
    """
    Step 2 — Google redirects here with a one-time code.
    We exchange it for an access token, fetch user info,
    issue our own JWT, and redirect to the React frontend.
    """
    timeout = httpx.Timeout(12.0, connect=6.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Exchange authorization code for Google access token
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code":          code,
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri":  f"{BACKEND_URL}/auth/callback",
                "grant_type":    "authorization_code",
            }
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail=f"OAuth error: {token_data}")

        # Fetch Google user profile
        user_resp = await client.get(
            GOOGLE_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_resp.json()

    # Issue our own JWT
    jwt_token = create_jwt({
        "sub":     user_info.get("sub"),
        "email":   user_info.get("email"),
        "name":    user_info.get("name"),
        "picture": user_info.get("picture"),
        "auth_provider": "google",
    })

    # Redirect to React app — token is passed as a query param
    # React reads it, stores in state, then removes it from the URL
    return RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={jwt_token}")


@router.get("/me")
def get_me(request: Request):
    """
    Returns the currently logged-in user's profile.
    React calls this on startup to restore session.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = auth_header.split(" ", 1)[1]
    payload = verify_jwt(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token is invalid or has expired")

    return {
        "email":   payload.get("email"),
        "name":    payload.get("name"),
        "picture": payload.get("picture"),
        "auth_provider": payload.get("auth_provider", "google"),
    }