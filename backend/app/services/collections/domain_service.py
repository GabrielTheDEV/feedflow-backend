from uuid import UUID
from typing import List
from datetime import datetime
from urllib.parse import urlparse

from app.models.domain import Domain
from app.repositories.domain_repository import DomainRepository
from app.utils.normalize_domain import normalize_domain

class DomainService:
    def __init__(self, repo: DomainRepository):
        self.repo = repo

    # Normaliza domínio para comparação segura.
    def _normalize_domain(self, raw: str) -> str:
        return normalize_domain(raw)




    def add_domain(self, collection_id: UUID, domain_raw: str) -> Domain:
        domain_normalized = self._normalize_domain(domain_raw)

        existing = self.repo.get_by_domain_and_collection(
            collection_id, domain_normalized
        )

        if existing:
            raise ValueError("Domain already exists for this collection")

        domain = Domain(
            collection_id=collection_id,
            domain=domain_normalized,
        )

        return self.repo.create(domain)

   


    def verify_domain(self, domain_id: UUID) -> Domain:
        domain = self.repo.get_by_id(domain_id)
        if not domain:
            raise ValueError("Domain not found")

        domain.verified = True
        domain.updated_at = datetime.utcnow()
        return self.repo.save(domain)

    # =========================
    # allow check 
    # =========================

    def assert_domain_allowed(self, collection_id: UUID, origin: str) -> None:
        domain = self._normalize_domain(origin)

        allowed = self.repo.is_domain_allowed(collection_id, domain)

        if not allowed:
            raise PermissionError("Domain not allowed")

   


    def list_domains(self, collection_id: UUID) -> List[Domain]:
        return self.repo.list_by_collection(collection_id)

   

    def deactivate_domain(self, domain_id: UUID) -> Domain:
        domain = self.repo.get_by_id(domain_id)
        if not domain:
            raise ValueError("Domain not found")

        domain.active = False
        domain.updated_at = datetime.utcnow()
        return self.repo.save(domain)



    def delete_domain(self, domain_id: UUID) -> None:
        domain = self.repo.get_by_id(domain_id)
        if not domain:
            raise ValueError("Domain not found")

        self.repo.delete(domain)