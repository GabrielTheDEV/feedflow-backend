from sqlmodel import Session

from app.models.domain import Domain
from app.repositories.domain_repository import DomainRepository


class DomainService:
    def __init__(self):
        self.repo = DomainRepository()

    def add_domain(
        self,
        session: Session,
        collection_id,
        domain: str,
    ) -> Domain:

        existing = self.repo.get_by_domain(session, domain)
        if existing:
            raise ValueError("Domain already registered")

        new_domain = Domain(
            collection_id=collection_id,
            domain=domain,
        )

        return self.repo.create(session, new_domain)