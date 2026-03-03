from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.database import get_session
from app.repositories.domain_repository import DomainRepository
from app.services.domain_service import DomainService
from app.models.domain import DomainCreate, DomainRead

router = APIRouter(prefix="/domains", tags=["Domains"])


def get_service(session: Session = Depends(get_session)) -> DomainService:
    repo = DomainRepository(session)
    return DomainService(repo)


# =========================
# create
# =========================
@router.post("/{collection_id}", response_model=DomainRead)
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
@router.get("/{collection_id}", response_model=list[DomainRead])
def list_domains(
    collection_id: UUID,
    service: DomainService = Depends(get_service),
):
    return service.list_domains(collection_id)


# =========================
# verify
# =========================
@router.patch("/{domain_id}/verify", response_model=DomainRead)
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
@router.patch("/{domain_id}/deactivate", response_model=DomainRead)
def deactivate_domain(
    domain_id: UUID,
    service: DomainService = Depends(get_service),
):
    try:
        return service.deactivate_domain(domain_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))