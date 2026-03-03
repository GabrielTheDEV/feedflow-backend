from typing import Optional, List
from sqlmodel import Session, select
from uuid import UUID

from app.models.domain import Domain


class DomainRepository:
    def __init__(self, session: Session):
        self.session = session


    #criar domínio
    def create(self, domain: Domain) -> Domain:
        self.session.add(domain)
        self.session.commit()
        self.session.refresh(domain)
        return domain


    # buscar por id
    def get_by_id(self, domain_id: UUID) -> Optional[Domain]:
        statement = select(Domain).where(Domain.id == domain_id)
        return self.session.exec(statement).first()



    # buscar por domain + collection (CRÍTICO)
    def get_by_domain_and_collection(
        self, collection_id: UUID, domain: str
    ) -> Optional[Domain]:
        statement = select(Domain).where(
            Domain.collection_id == collection_id,
            Domain.domain == domain,
        )
        return self.session.exec(statement).first()

    # Listar por collection
    def list_by_collection(self, collection_id: UUID) -> List[Domain]:
        statement = select(Domain).where(Domain.collection_id == collection_id)
        return list(self.session.exec(statement).all())

    # verificar domínio permitido 
    def is_domain_allowed(self, collection_id: UUID, domain: str) -> bool:
        statement = select(Domain.id).where(
            Domain.collection_id == collection_id,
            Domain.domain == domain,
            Domain.active == True,
            Domain.verified == True,
        )
        return self.session.exec(statement).first() is not None

    #  update genérico
    def save(self, domain: Domain) -> Domain:
        self.session.add(domain)
        self.session.commit()
        self.session.refresh(domain)
        return domain

    # delete
    def delete(self, domain: Domain) -> None:
        self.session.delete(domain)
        self.session.commit()