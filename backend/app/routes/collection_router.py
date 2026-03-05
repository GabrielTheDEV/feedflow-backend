from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session
from app.database.config import get_db
from app.dtos.schemas import CollectionCreate, CollectionRead
from app.repositories.collection_repository import CollectionRepository
from app.services.collections.collections_service import CollectionService
from app.database.auth_handlers import get_current_user
from app.docs.swagger.collections_docs import (
    CREATE_COLLECTION_DOCS,
    LIST_COLLECTIONS_DOCS,
    DEACTIVATE_COLLECTION_DOCS,
    ROTATE_COLLECTION_KEY_DOCS,
    DELETE_COLLECTION_DOCS,
)

router = APIRouter(
    prefix="/collections",
    tags=["collections"])


def get_collection_service(db: Session = Depends(get_db)) -> CollectionService:
    repo = CollectionRepository(db)
    return CollectionService(repo)



@router.post("/", response_model=CollectionRead, status_code=201, **CREATE_COLLECTION_DOCS)
def create_collection(
    payload: CollectionCreate,
    service: CollectionService = Depends(get_collection_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        return service.create_collection(user_id=user_id, name=payload.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/", response_model=list[CollectionRead], **LIST_COLLECTIONS_DOCS)
def list_collections(
    service: CollectionService = Depends(get_collection_service),
    user_id: UUID = Depends(get_current_user),
):
    return service.list_user_collections(user_id)




@router.patch("/{collection_id}/deactivate", response_model=CollectionRead, **DEACTIVATE_COLLECTION_DOCS)
def deactivate_collection(
    collection_id: UUID,
    service: CollectionService = Depends(get_collection_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        return service.deactivate_collection(collection_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))




@router.api_route(
    "/{collection_id}/rotate-key",
    methods=["POST", "PATCH"],
    response_model=CollectionRead,
    **ROTATE_COLLECTION_KEY_DOCS,
)
def rotate_api_key(
    collection_id: UUID = Path(
        ...,
        description="ID da collection em formato UUID",
    ),
    service: CollectionService = Depends(get_collection_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        return service.rotate_api_key(collection_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.delete("/{collection_id}", status_code=204, **DELETE_COLLECTION_DOCS)
def delete_collection(
    collection_id: UUID,
    service: CollectionService = Depends(get_collection_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        service.delete_collection(collection_id, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))