"""
Testes de integração com Supabase (PostgreSQL)
"""
import os
import uuid
import pytest
from app.services.superbase.supabase_service import SupabaseManager

def _has_env() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))

@pytest.mark.skipif(not _has_env(), reason="SUPABASE_URL/SUPABASE_KEY não configurados")
def test_supabase_insert_roundtrip():
    manager = SupabaseManager()
    email = f"teste+{uuid.uuid4().hex[:8]}@exemplo.com"
    comment = "Teste de integração com Supabase"
    metadata = {"source": "pytest", "run_id": uuid.uuid4().hex}
    inserted = manager.save_feedback(
        email=email,
        comment=comment,
        metadata=metadata,
        image_url=None,
    )
    assert inserted is not None
    assert inserted.get("id")
    assert inserted.get("customer_email") == email
    assert inserted.get("comment") == comment
    # Limpeza do registro criado
    manager.client.table("feedbacks").delete().eq("id", inserted["id"]).execute()
