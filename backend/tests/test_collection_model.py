import pytest
from uuid import uuid4
from datetime import datetime
from app.models.collections import Collection


def test_collection_model_fields():
    user_id = uuid4()
    collection = Collection(
        user_id=user_id,
        name="Minha Collection",
        api_key="chave123",
        api_key_created_at=datetime.utcnow(),
        plan=None,
        is_active=True,
        status=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert collection.user_id == user_id
    assert collection.name == "Minha Collection"
    assert collection.api_key == "chave123"
    assert collection.is_active is True
    assert hasattr(collection, "created_at")
    assert hasattr(collection, "updated_at")
