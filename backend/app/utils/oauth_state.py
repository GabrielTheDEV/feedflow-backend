import hmac
import hashlib
import os
import time
from typing import Tuple
from uuid import UUID
from app.models.enums.integrationsServices import IntegrationService


"""
Utilitário para gerar e validar state OAuth com HMAC-SHA256.

O state carrega collection_id, user_id e service assinados,
permitindo que o callback seja público (sem JWT) mantendo segurança.
"""



# Segredo usado para assinar o state — obrigatório em produção
_SECRET = os.getenv("OAUTH_STATE_SECRET", "").encode()
if not _SECRET:
    _SECRET = os.getenv("SUPABASE_KEY", "fallback-dev-secret").encode()

# Tempo máximo de validade do state (10 minutos)
STATE_TTL_SECONDS = 600


def _sign(payload: str) -> str:
    """Gera assinatura HMAC-SHA256 do payload."""
    return hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()[:32]


def generate_state(collection_id: UUID, user_id: UUID, service: IntegrationService) -> str:
    """Gera state assinado: signature.timestamp.collection_id.user_id.service"""
    ts = str(int(time.time()))
    payload = f"{ts}.{collection_id}.{user_id}.{service.value}"
    sig = _sign(payload)
    return f"{sig}.{payload}"


def verify_state(state: str) -> Tuple[UUID, UUID, IntegrationService]:
    """Valida HMAC e TTL do state. Retorna (collection_id, user_id, service).

    Raises:
        ValueError: se o state for inválido, expirado ou adulterado.
    """
    parts = state.split(".", 4)
    if len(parts) != 5:
        raise ValueError("Invalid OAuth state format")

    sig, ts, collection_id_str, user_id_str, service_str = parts

    # Verifica assinatura
    payload = f"{ts}.{collection_id_str}.{user_id_str}.{service_str}"
    expected_sig = _sign(payload)

    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("Invalid OAuth state signature")

    # Verifica expiração
    try:
        created_at = int(ts)
    except ValueError:
        raise ValueError("Invalid OAuth state timestamp")

    if time.time() - created_at > STATE_TTL_SECONDS:
        raise ValueError("OAuth state expired")

    # Parse dos valores
    try:
        collection_id = UUID(collection_id_str)
        user_id = UUID(user_id_str)
        service = IntegrationService(service_str)
    except (ValueError, KeyError):
        raise ValueError("Invalid OAuth state data")

    return collection_id, user_id, service
