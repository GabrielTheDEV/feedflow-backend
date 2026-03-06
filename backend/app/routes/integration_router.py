from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database.config import get_db
from app.database.auth_handlers import get_current_user
from app.repositories.collection_repository import CollectionRepository
from app.repositories.integration_repository import IntegrationRepository
from app.services.integrations.integrations_service import IntegrationService
from app.dtos.schemas import IntegrationEnable, IntegrationRead
from app.docs.swagger.integrations_docs import (
    CREATE_INTEGRATION_DOCS,
    LIST_INTEGRATIONS_DOCS,
    DELETE_INTEGRATION_DOCS,
)

router = APIRouter(
    prefix="/integrations",
    tags=["integrations"],
)


def get_integration_service(db: Session = Depends(get_db)) -> IntegrationService:
    repo = IntegrationRepository(db)
    collection_repo = CollectionRepository(db)
    return IntegrationService(repo, collection_repo)


@router.post("/{collection_id}", response_model=IntegrationRead, status_code=201, **CREATE_INTEGRATION_DOCS)
def create_integration(
    collection_id: UUID,
    payload: IntegrationEnable,
    service: IntegrationService = Depends(get_integration_service),
    user_id: UUID = Depends(get_current_user),
):
    """Create a new integration for a collection (requires authentication)."""
    try:
        return service.create_integration(      
            collection_id=collection_id,
            user_id=user_id,
            service=payload.service,
            config=payload.config,
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.get("/{collection_id}", response_model=list[IntegrationRead], **LIST_INTEGRATIONS_DOCS)
def list_integrations(
    collection_id: UUID,
    service: IntegrationService = Depends(get_integration_service),
    user_id: UUID = Depends(get_current_user),
):
    """List all integrations for a collection (requires authentication)."""
    try:
        return service.list_by_collection(collection_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.delete("/{collection_id}/{integration_id}", status_code=204, **DELETE_INTEGRATION_DOCS)
def delete_integration(
    collection_id: UUID,
    integration_id: UUID,
    service: IntegrationService = Depends(get_integration_service),
    user_id: UUID = Depends(get_current_user),
):
    """Delete an integration (requires authentication and ownership of collection)."""
    try:
        service.delete_integration(integration_id, collection_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))