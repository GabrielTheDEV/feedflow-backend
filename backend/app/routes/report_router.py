from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session

from app.database.config import get_db
from app.repositories.collection_repository import CollectionRepository
from app.repositories.domain_repository import DomainRepository
from app.repositories.integration_repository import IntegrationRepository
from app.services.collections.collections_service import CollectionService
from app.services.collections.domain_service import DomainService
from app.services.widget.report_dispatcher_service import ReportDispatcherService
from app.services.widget.widget_validators import WidgetValidator

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

def get_widget_validator(db: Session = Depends(get_db)) -> WidgetValidator:
    collection_repo = CollectionRepository(db)
    domain_repo = DomainRepository(db)

    collection_service = CollectionService(collection_repo)
    domain_service = DomainService(domain_repo, collection_repo)

    return WidgetValidator(collection_service, domain_service)


def get_dispatcher(db: Session = Depends(get_db)) -> ReportDispatcherService:
    integration_repo = IntegrationRepository(db)
    return ReportDispatcherService(integration_repo)





@router.post("/", status_code=204)
async def send_report(
    body: dict,
    request: Request,
    api_key: str,
    validator: WidgetValidator = Depends(get_widget_validator),
    dispatcher: ReportDispatcherService = Depends(get_dispatcher),
):
    origin = request.headers.get("origin") or request.headers.get("referer")

    try:
        collection = validator.validate(api_key=api_key, origin=origin)
        await dispatcher.dispatch(collection.id, body, origin=origin or "")

    except ValueError as e:
        detail = str(e)

        if detail in {"api_key is required", "origin is required"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        if detail in {"Collection not found", "Collection is inactive"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
            
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    return
