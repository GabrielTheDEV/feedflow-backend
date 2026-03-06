from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.models.domain import Domain
from app.repositories.collection_repository import CollectionRepository
from app.repositories.domain_repository import DomainRepository
from app.utils.normalize_domain import normalize_domain


class DomainService:
    def __init__(self, repo: DomainRepository, collection_repo: CollectionRepository):
        self.repo = repo
        self.collection_repo = collection_repo

"""Normaliza domínio para comparação segura e consistente."""
    def _normalize_domain(self, raw: str) -> str:
        return normalize_domain(raw)



"""Garante que a collection existe e pertence ao usuário autenticado."""
    def _assert_collection_ownership(self, collection_id: UUID, user_id: UUID) -> None:
        collection = self.collection_repo.get_by_id(collection_id)
        if not collection:
            raise LookupError("Collection not found")

        if collection.user_id != user_id:
            raise PermissionError("You do not have access to this collection")


"""Cria domínio na collection após validar ownership e duplicidade."""
    def add_domain(self, collection_id: UUID, domain_raw: str, user_id: UUID) -> Domain:
        self._assert_collection_ownership(collection_id, user_id)

        domain_normalized = self._normalize_domain(domain_raw)
        existing = self.repo.get_by_domain_and_collection(collection_id, domain_normalized)

        if existing:
            raise ValueError("Domain already exists for this collection")

        domain = Domain(
            collection_id=collection_id,
            domain=domain_normalized,
        )
        return self.repo.create(domain)


    """
        Se `user_id` for informado, aplica ownership da collection relacionada.
        Isso permite manter rota pública temporariamente e ativar proteção total depois.
    """
    def verify_domain(self, domain_id: UUID, user_id: Optional[UUID] = None) -> Domain:
        domain = self.repo.get_by_id(domain_id)
        if not domain:
            raise ValueError("Domain not found")

        if user_id is not None:
            self._assert_collection_ownership(domain.collection_id, user_id)

        domain.verified = True
        domain.updated_at = datetime.utcnow()
        return self.repo.save(domain)



    def assert_domain_allowed(self, collection_id: UUID, origin: str) -> None:
        domain = self._normalize_domain(origin)
        allowed = self.repo.is_domain_allowed(collection_id, domain)

        if not allowed:
            raise PermissionError("Domain not allowed")



    def list_domains(self, collection_id: UUID, user_id: UUID) -> List[Domain]:
        self._assert_collection_ownership(collection_id, user_id)
        return self.repo.list_by_collection(collection_id)



    def deactivate_domain(self, domain_id: UUID, user_id: UUID) -> Domain:
        domain = self.repo.get_by_id(domain_id)
        if not domain:
            raise ValueError("Domain not found")

        self._assert_collection_ownership(domain.collection_id, user_id)

        domain.active = False
        domain.updated_at = datetime.utcnow()
        return self.repo.save(domain)



    def activate_domain(self, domain_id: UUID, user_id: UUID) -> Domain:
        domain = self.repo.get_by_id(domain_id)
        if not domain:
            raise ValueError("Domain not found")
            
        self._assert_collection_ownership(domain.collection_id, user_id)

        domain.active = True
        domain.updated_at = datetime.utcnow()
        return self.repo.save(domain)



    def delete_domain(self, domain_id: UUID, user_id: UUID) -> None:
        domain = self.repo.get_by_id(domain_id)
        if not domain:
            raise ValueError("Domain not found")

        self._assert_collection_ownership(domain.collection_id, user_id)
        self.repo.delete(domain)