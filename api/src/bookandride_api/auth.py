# app/auth.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from . import models

# -----------------------------
# API KEY SECTION
# -----------------------------
API_KEYS = {
    "dev-key-123": {"user_id": 1, "role": "user"},
    "admin-key-456": {"user_id": 999, "role": "admin"},
}

def verify_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")
) -> Optional[dict]:
    if x_api_key is None:
        return None

    if x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return API_KEYS[x_api_key]



# -----------------------------
# JWT SECTION
# -----------------------------
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "60"))

security = HTTPBearer(auto_error=False)

def hash_password(plain: str) -> str:
    return pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd.verify(plain, hashed)

def create_access_token(user_id: int, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=JWT_EXPIRE_MIN)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Missing or invalid Authorization header",
        )

    try:
        data = decode_token(creds.credentials)
        user_id = int(data.get("sub", "0"))
    except (JWTError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

    return user

def api_key_or_jwt(
    api_key_data: Optional[dict] = Depends(verify_api_key),
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Allows EITHER:
    - X-API-Key header, or
    - Authorization: Bearer <JWT>
    """
    # 1) If API key is valid → return it immediately
    if api_key_data:
        return api_key_data

    # 2) Otherwise fall back to JWT
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing authentication")

    try:
        data = decode_token(creds.credentials)
        user_id = int(data.get("sub", "0"))
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

    return {"user_id": user.id, "role": user.role}
 