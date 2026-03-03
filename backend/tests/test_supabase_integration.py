"""
Testes de integração com Supabase (SDK/Storage/Auth)
"""
import os
import pytest
from app.database.config import get_supabase_client

def _has_env() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))

@pytest.mark.skipif(not _has_env(), reason="SUPABASE_URL/SUPABASE_KEY não configurados")
def test_supabase_manager_init():
    client = get_supabase_client()
    assert client is not None
