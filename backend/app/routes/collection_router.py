from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.core.database import get_db
from app.dtos.schemas.py import ( CollectionCreate, CollectionRead)
from app.services.collection_service import CollectionService
from app.utils.auth import get_current_user_id


router = APIRouter(prefix="/collections", tags=["Collections"])
service = CollectionService()
# -------------------------
# CREATE COLLECTION
# -------------------------
@router.post("", response_model=CollectionRead)
def create_collection(
    data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_id),
):
    user_id = current_user["id"]    


    try:
        return service.create_collection(
            db,
            user_id=fake_user_id,
            name=data.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# LIST USER COLLECTIONS
# -------------------------
@router.get("", response_model=list[CollectionRead])
def list_collections(db: Session = Depends(get_db)):
    fake_user_id = UUID("00000000-0000-0000-0000-000000000001")
    return service.get_user_collections(db, fake_user_id)


# -------------------------
# ROTATE API KEY
# -------------------------
@router.post("/{collection_id}/rotate-key")
def rotate_api_key(
    collection_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        return service.regenerate_api_key(db, collection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))