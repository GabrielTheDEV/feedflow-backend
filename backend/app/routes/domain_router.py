from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID

from app.database.config import get_db
from app.database.auth_handlers import get_current_user
from app.repositories.collection_repository import CollectionRepository
from app.repositories.domain_repository import DomainRepository
from app.services.collections.domain_service import DomainService
from app.dtos.schemas import DomainCreate, DomainRead
from app.swagger.domains_docs import (
    ADD_DOMAIN_DOCS,
    LIST_DOMAINS_DOCS,
    VERIFY_DOMAIN_DOCS,
    DEACTIVATE_DOMAIN_DOCS,
    ACTIVATE_DOMAIN_DOCS,
)

router = APIRouter(prefix="/domains", tags=["Domains"])


def get_service(session: Session = Depends(get_db)) -> DomainService:
    repo = DomainRepository(session)
    collection_repo = CollectionRepository(session)
    return DomainService(repo, collection_repo)


# =========================
# create
# =========================
@router.post("/{collection_id}", response_model=DomainRead, **ADD_DOMAIN_DOCS)
def add_domain(
    collection_id: UUID,
    payload: DomainCreate,
    service: DomainService = Depends(get_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        return service.add_domain(collection_id, payload.domain, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================
# list
# =========================
@router.get("/{collection_id}", response_model=list[DomainRead], **LIST_DOMAINS_DOCS)
def list_domains(
    collection_id: UUID,
    service: DomainService = Depends(get_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        return service.list_domains(collection_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
    user_id: UUID = Depends(get_current_user),
):
    try:
        return service.deactivate_domain(domain_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{domain_id}/activate", response_model=DomainRead, **ACTIVATE_DOMAIN_DOCS)
def activate_domain(
    domain_id: UUID,
    service: DomainService = Depends(get_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        return service.activate_domain(domain_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))




@router.delete("/{domain_id}", status_code=204)
def delete_domain(
    domain_id: UUID,
    service: DomainService = Depends(get_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        service.delete_domain(domain_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))