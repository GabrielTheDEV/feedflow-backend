from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.core.database import get_db
from app.schemas.integration_schema import (
    IntegrationEnable,
    IntegrationRead,
)
from app.services.integration_service import IntegrationService
from app.docs.swagger.integrations_docs import ENABLE_INTEGRATION_DOCS

router = APIRouter(prefix="/integrations", tags=["Integrations"])
service = IntegrationService()


@router.post("/{collection_id}", response_model=IntegrationRead, **ENABLE_INTEGRATION_DOCS)
def enable_integration(
    collection_id: UUID,
    data: IntegrationEnable,
    db: Session = Depends(get_db),
):
    try:
        return service.enable_integration(
            db,
            collection_id,
            data.service,
            data.config,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))