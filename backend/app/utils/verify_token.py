import os
import requests
from jose import jwt
from fastapi import HTTPException
from jose.utils import base64url_decode

SUPABASE_URL = os.getenv("SUPABASE_URL")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

_jwks_cache = None


def get_jwks():
    global _jwks_cache

    if _jwks_cache is None:
        try:
            response = requests.get(JWKS_URL, timeout=5)
            response.raise_for_status()
            _jwks_cache = response.json()
        except Exception:
            raise HTTPException(status_code=401, detail="Failed to fetch JWKS")

    return _jwks_cache


def get_signing_key(token: str):
    jwks = get_jwks()

    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token header")

    kid = unverified_header.get("kid")

    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key

    raise HTTPException(status_code=401, detail="Signing key not found")


def verify_supabase_token(token: str):
    try:
        signing_key = get_signing_key(token)

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["ES256"],
            issuer=f"{SUPABASE_URL}/auth/v1",
            audience="authenticated",
        )

        return payload

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token",
        )