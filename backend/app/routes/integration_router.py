from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database.config import get_db
from app.database.auth_handlers import get_current_user
from app.repositories.collection_repository import CollectionRepository
from app.repositories.integration_repository import IntegrationRepository
from app.services.integrations.integrations_service import IntegrationService
from app.models.enums.integrationsServices import IntegrationService as IntegrationServiceEnum
from app.dtos.schemas import IntegrationEnable, IntegrationRead
from app.swagger.integrations_docs import (
    CREATE_INTEGRATION_DOCS,
    LIST_INTEGRATIONS_DOCS,
    DELETE_INTEGRATION_DOCS,
    OAUTH_AUTHORIZE_DOCS,
    OAUTH_CALLBACK_DOCS,
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



# ── OAuth Flow ────────────────────────────────────────────

@router.get("/{collection_id}/oauth/{provider}/authorize", **OAUTH_AUTHORIZE_DOCS)
def oauth_authorize(
    collection_id: UUID,
    provider: IntegrationServiceEnum,
    redirect: bool = Query(True, description="Se true, redireciona (302). Se false, retorna JSON com a URL."),
    service: IntegrationService = Depends(get_integration_service),
    user_id: UUID = Depends(get_current_user),
):
    """Generate the provider's OAuth authorization URL."""
    try:
        url = service.start_oauth(collection_id, user_id, provider)

        if redirect:
            return RedirectResponse(url=url, status_code=302)

        return {"authorization_url": url}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/oauth/callback", response_model=IntegrationRead, **OAUTH_CALLBACK_DOCS)
async def oauth_callback(
    state: str = Query(..., description="Signed state returned by the provider"),
    code: str = Query(..., description="Authorization code returned by the provider"),
    service: IntegrationService = Depends(get_integration_service),
):
    """Exchange the OAuth code for tokens and create the integration (public — validated via HMAC state)."""
    try:
        integration = await service.complete_oauth(state, code)
        return integration
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))