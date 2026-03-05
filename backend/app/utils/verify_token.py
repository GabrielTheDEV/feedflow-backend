import os
import time
import requests
from jose import jwt, JWTError
from fastapi import HTTPException, status

SUPABASE_URL = os.getenv("SUPABASE_URL")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL not configured")

JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# cache em memória do processo
_jwks_cache = None
_jwks_cached_at = 0
JWKS_TTL = 60 * 60  # 1 hora


def get_jwks():
    global _jwks_cache, _jwks_cached_at

    now = time.time()

    # refresh automático por TTL
    if _jwks_cache is None or (now - _jwks_cached_at) > JWKS_TTL:
        try:
            response = requests.get(JWKS_URL, timeout=5)
            response.raise_for_status()

            _jwks_cache = response.json()
            _jwks_cached_at = now

        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service unavailable",
            ) from exc

    return _jwks_cache


def get_signing_key(token: str):
    jwks = get_jwks()

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        ) from exc

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

    # tenta refresh imediato (rotação de chave)
    global _jwks_cache
    _jwks_cache = None
    jwks = get_jwks()

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Signing key not found",
    )


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

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc