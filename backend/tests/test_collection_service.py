import pytest
from uuid import uuid4
from app.models.collections import Collection
from app.services.collections.collections_service import CollectionService
from app.repositories.collection_repository import CollectionRepository

class FakeRepo:
    def __init__(self):
        self.created = []
        self.saved = []
        self.collections = {}
    def create(self, collection):
        self.created.append(collection)
        self.collections[collection.id] = collection
        return collection
    def get_by_id(self, collection_id):
        return self.collections.get(collection_id)
    def save(self, collection):
        self.saved.append(collection)
        self.collections[collection.id] = collection
        return collection
    def list_by_user(self, user_id):
        return [c for c in self.collections.values() if c.user_id == user_id]
    def get_by_api_key(self, api_key):
        for c in self.collections.values():
            if c.api_key == api_key:
                return c
        return None

@pytest.fixture
def fake_repo():
    return FakeRepo()

@pytest.fixture
def service(fake_repo):
    return CollectionService(fake_repo)

def test_create_collection(service):
    user_id = uuid4()
    name = "Nova Collection"
    collection = service.create_collection(user_id, name)
    assert collection.user_id == user_id
    assert collection.name == name
    assert collection.api_key is not None

def test_create_collection_no_user(service):
    with pytest.raises(ValueError):
        service.create_collection(None, "Teste")

def test_rotate_api_key(service):
    user_id = uuid4()
    collection = service.create_collection(user_id, "Teste")
    old_key = collection.api_key
    new_collection = service.rotate_api_key(collection.id)
    assert new_collection.api_key != old_key

def test_deactivate_collection(service):
    user_id = uuid4()
    collection = service.create_collection(user_id, "Teste")
    result = service.deactivate_collection(collection.id)
    assert getattr(result, "active", False) is False

def test_list_user_collections(service):
    user_id = uuid4()
    service.create_collection(user_id, "A")
    service.create_collection(user_id, "B")
    result = service.list_user_collections(user_id)
    assert len(result) == 2

def test_get_active_by_api_key(service):
    user_id = uuid4()
    collection = service.create_collection(user_id, "Teste")
    result = service.get_active_by_api_key(collection.api_key)
    assert result == collection
