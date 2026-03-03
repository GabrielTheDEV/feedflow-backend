from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.collection import CollectionCreate, CollectionRead
from app.services.collection_service import CollectionService
from app.dependencies import get_collection_service

router = APIRouter(prefix="/collections", tags=["collections"])




@router.post("/", response_model=CollectionRead, status_code=201)
def create_collection(
    payload: CollectionCreate,
    service: CollectionService = Depends(get_collection_service),
    # TODO: pegar do Supabase auth
    user_id: UUID = Depends(...),
):
    try:
        return service.create_collection(user_id=user_id, name=payload.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/", response_model=list[CollectionRead])
def list_collections(
    service: CollectionService = Depends(get_collection_service),
    user_id: UUID = Depends(...),
):
    return service.list_user_collections(user_id)




@router.patch("/{collection_id}/deactivate", response_model=CollectionRead)
def deactivate_collection(
    collection_id: UUID,
    service: CollectionService = Depends(get_collection_service),
):
    try:
        return service.deactivate_collection(collection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))




@router.post("/{collection_id}/rotate-key", response_model=CollectionRead)
def rotate_api_key(
    collection_id: UUID,
    service: CollectionService = Depends(get_collection_service),
):
    try:
        return service.rotate_api_key(collection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))