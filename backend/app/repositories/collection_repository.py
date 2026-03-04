from typing import Optional, List
from uuid import UUID

from sqlmodel import Session, select

from app.models.collections import Collection


class CollectionRepository:
    def __init__(self, session: Session):
        self.session = session

    # 🔹 create
    def create(self, collection: Collection) -> Collection:
        self.session.add(collection)
        self.session.commit()
        self.session.refresh(collection)
        return collection

    # 🔹 get by id
    def get_by_id(self, collection_id: UUID) -> Optional[Collection]:
        statement = select(Collection).where(Collection.id == collection_id)
        return self.session.exec(statement).first()

    # 🔹 get by api key (CRÍTICO para widget)
    def get_by_api_key(self, api_key: str) -> Optional[Collection]:
        statement = select(Collection).where(Collection.api_key == api_key)
        return self.session.exec(statement).first()

    # 🔹 list by user
    def list_by_user(self, user_id: UUID) -> List[Collection]:
        statement = select(Collection).where(Collection.user_id == user_id)
        return list(self.session.exec(statement))

    # 🔹 save/update
    def save(self, collection: Collection) -> Collection:
        self.session.add(collection)
        self.session.commit()
        self.session.refresh(collection)
        return collection
    
    def delete(self, collection: Collection) -> None:
        self.session.delete(collection)
        self.session.commit()