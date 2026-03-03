from typing import Optional, List
from sqlmodel import Session, select
from app.models.collection import Collection
from .base_repository import BaseRepository


class CollectionRepository(BaseRepository[Collection]):
    def __init__(self):
        super().__init__(Collection)

    def get_by_api_key(
        self, session: Session, api_key: str
    ) -> Optional[Collection]:
        return session.exec(
            select(Collection).where(Collection.api_key == api_key)
        ).first()

    def get_by_user(
        self, session: Session, user_id
    ) -> List[Collection]:
        return session.exec(
            select(Collection).where(Collection.user_id == user_id)
        ).all()