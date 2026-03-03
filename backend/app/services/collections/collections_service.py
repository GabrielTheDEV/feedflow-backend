import secrets
from datetime import datetime
from uuid import UUID

from app.models.collection import Collection
from app.repositories.collection_repository import CollectionRepository


class CollectionService:
    def __init__(self, repo: CollectionRepository):
        self.repo = repo

    # =========================
    # utils
    # =========================
    def _generate_api_key(self) -> str:
        return secrets.token_urlsafe(32)

    # =========================
    # create
    # =========================
    def create_collection(self, user_id: UUID, name: str) -> Collection:
        api_key = self._generate_api_key()

        collection = Collection(
            user_id=user_id,
            name=name,
            api_key=api_key,
        )

        return self.repo.create(collection)

    # =========================
    # get by api key (widget)
    # =========================
    def get_active_by_api_key(self, api_key: str) -> Collection:
        collection = self.repo.get_by_api_key(api_key)

        if not collection:
            raise ValueError("Collection not found")

        if not collection.active:
            raise ValueError("Collection is inactive")

        return collection

    # =========================
    # deactivate
    # =========================
    def deactivate_collection(self, collection_id: UUID) -> Collection:
        collection = self.repo.get_by_id(collection_id)

        if not collection:
            raise ValueError("Collection not found")

        collection.active = False
        collection.updated_at = datetime.utcnow()

        return self.repo.save(collection)

    # =========================
    # rotate api key
    # =========================
    def rotate_api_key(self, collection_id: UUID) -> Collection:
        collection = self.repo.get_by_id(collection_id)

        if not collection:
            raise ValueError("Collection not found")

        collection.api_key = self._generate_api_key()
        collection.updated_at = datetime.utcnow()

        return self.repo.save(collection)

    # =========================
    # list user collections
    # =========================
    def list_user_collections(self, user_id: UUID):
        return self.repo.list_by_user(user_id)