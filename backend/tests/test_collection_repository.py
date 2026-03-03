import pytest
from uuid import uuid4
from sqlmodel import Session
from app.models.collections import Collection
from app.repositories.collection_repository import CollectionRepository

class FakeSession:
    def __init__(self):
        self.added = []
        self.committed = False
        self.refreshed = []
        self.selected = []
        self._collections = {}

    def add(self, obj):
        self.added.append(obj)
        self._collections[obj.id] = obj

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed.append(obj)

    def exec(self, statement):
        # Simula select por id/api_key/user_id
        class Result:
            def __init__(self, obj):
                self._obj = obj
            def first(self):
                return self._obj
            def __iter__(self):
                return iter([self._obj] if self._obj else [])
        if hasattr(statement, 'whereclause'):
            for obj in self._collections.values():
                if hasattr(statement.whereclause, 'right'):
                    if obj.id == statement.whereclause.right.value:
                        return Result(obj)
                    if obj.api_key == statement.whereclause.right.value:
                        return Result(obj)
                    if obj.user_id == statement.whereclause.right.value:
                        return Result(obj)
        return Result(None)

@pytest.fixture
def fake_session():
    return FakeSession()

@pytest.fixture
def repo(fake_session):
    return CollectionRepository(fake_session)

def test_create_collection(repo):
    collection = Collection(user_id=uuid4(), name="Teste", api_key="abc")
    result = repo.create(collection)
    assert result == collection
    assert repo.session.committed

def test_get_by_id(repo):
    collection = Collection(id=uuid4(), user_id=uuid4(), name="Teste", api_key="abc")
    repo.session._collections[collection.id] = collection
    result = repo.get_by_id(collection.id)
    assert result == collection

def test_get_by_api_key(repo):
    collection = Collection(id=uuid4(), user_id=uuid4(), name="Teste", api_key="abc")
    repo.session._collections[collection.id] = collection
    result = repo.get_by_api_key("abc")
    assert result == collection

def test_list_by_user(repo):
    user_id = uuid4()
    c1 = Collection(id=uuid4(), user_id=user_id, name="A", api_key="a")
    c2 = Collection(id=uuid4(), user_id=user_id, name="B", api_key="b")
    repo.session._collections[c1.id] = c1
    repo.session._collections[c2.id] = c2
    result = repo.list_by_user(user_id)
    assert c1 in result and c2 in result

def test_save_collection(repo):
    collection = Collection(id=uuid4(), user_id=uuid4(), name="Teste", api_key="abc")
    result = repo.save(collection)
    assert result == collection
    assert repo.session.committed
