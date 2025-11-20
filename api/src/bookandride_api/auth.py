# app/auth.py
from fastapi import Header, HTTPException, status
from typing import Optional

# Demo keys → user/role mapping
API_KEYS = {
    "dev-key-123": {"user_id": 1, "role": "user"},
    "admin-key-456": {"user_id": 999, "role": "admin"},
}

def verify_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> dict:
    """
    Simple API key verification.
    Returns a dict like {"user_id": 1, "role": "user"} or raises 401.
    """
    if not x_api_key or x_api_key not in API_KEYS:
        # Note: including WWW-Authenticate is optional for API keys
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return API_KEYS[x_api_key]
