from typing import Optional, List
from sqlmodel import Session, select
from app.models.domain import Domain
from .base_repository import BaseRepository


class DomainRepository(BaseRepository[Domain]):
    def __init__(self):
        super().__init__(Domain)

    def get_by_domain(
        self, session: Session, domain: str
    ) -> Optional[Domain]:
        return session.exec(
            select(Domain).where(Domain.domain == domain)
        ).first()

    def get_by_collection(
        self, session: Session, collection_id
    ) -> List[Domain]:
        return session.exec(
            select(Domain).where(Domain.collection_id == collection_id)
        ).all()