from uuid import uuid4
import secrets
from sqlmodel import Session

from app.models.collection import Collection
from app.repositories.collection_repository import CollectionRepository


class CollectionService:
    def __init__(self):
        self.repo = CollectionRepository()

    # -------------------------
    # CREATE COLLECTION
    # -------------------------
    def create_collection(
        self,
        session: Session,
        user_id,
        name: str,
    ) -> Collection:

        collection = Collection(
            user_id=user_id,
            name=name,
            api_key=self._generate_api_key(),
        )

        return self.repo.create(session, collection)

    # -------------------------
    # GET USER COLLECTIONS
    # -------------------------
    def get_user_collections(self, session: Session, user_id):
        return self.repo.get_by_user(session, user_id)

    # -------------------------
    # REGENERATE API KEY
    # -------------------------
    def regenerate_api_key(self, session: Session, collection_id):
        collection = self.repo.get_by_id(session, collection_id)

        if not collection:
            raise ValueError("Collection not found")

        collection.api_key = self._generate_api_key()
        session.add(collection)
        session.commit()
        session.refresh(collection)

        return collection

    # -------------------------
    # PRIVATE HELPERS
    # -------------------------
    def _generate_api_key(self) -> str:
        return f"ff_{secrets.token_urlsafe(32)}"