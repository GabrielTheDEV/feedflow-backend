from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.database.config import get_db
from app.repositories.domain_repository import DomainRepository
from app.services.collections.domain_service import DomainService
from app.dtos.schemas import DomainCreate, DomainRead
from app.docs.swagger.domains_docs import (
    ADD_DOMAIN_DOCS,
    LIST_DOMAINS_DOCS,
    VERIFY_DOMAIN_DOCS,
    DEACTIVATE_DOMAIN_DOCS,
)

router = APIRouter(prefix="/domains", tags=["Domains"])


def get_service(session: Session = Depends(get_db)) -> DomainService:
    repo = DomainRepository(session)
    return DomainService(repo)


# =========================
# create
# =========================
@router.post("/{collection_id}", response_model=DomainRead, **ADD_DOMAIN_DOCS)
def add_domain(
    collection_id: UUID,
    payload: DomainCreate,
    service: DomainService = Depends(get_service),
):
    try:
        return service.add_domain(collection_id, payload.domain)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================
# list
# =========================
@router.get("/{collection_id}", response_model=list[DomainRead], **LIST_DOMAINS_DOCS)
def list_domains(
    collection_id: UUID,
    service: DomainService = Depends(get_service),
):
    return service.list_domains(collection_id)


# =========================
# verify
# =========================
@router.patch("/{domain_id}/verify", response_model=DomainRead, **VERIFY_DOMAIN_DOCS)
def verify_domain(
    domain_id: UUID,
    service: DomainService = Depends(get_service),
):
    try:
        return service.verify_domain(domain_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =========================
# deactivate
# =========================
@router.patch("/{domain_id}/deactivate", response_model=DomainRead, **DEACTIVATE_DOMAIN_DOCS)
def deactivate_domain(
    domain_id: UUID,
    service: DomainService = Depends(get_service),
):
    try:
        return service.deactivate_domain(domain_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{domain_id}", status_code=204)
def delete_domain(
    domain_id: UUID,
    service: DomainService = Depends(get_service),
):
    try:
        service.delete_domain(domain_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))