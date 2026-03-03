from typing import Optional, List
from sqlmodel import Session, select
from app.models.integration import Integration
from app.models.enums import IntegrationService
from .base_repository import BaseRepository


class IntegrationRepository(BaseRepository[Integration]):
    def __init__(self):
        super().__init__(Integration)

    def get_by_collection(
        self, session: Session, collection_id
    ) -> List[Integration]:
        return session.exec(
            select(Integration).where(
                Integration.collection_id == collection_id
            )
        ).all()

    def get_active_by_service(
        self,
        session: Session,
        collection_id,
        service: IntegrationService,
    ) -> Optional[Integration]:
        return session.exec(
            select(Integration)
            .where(Integration.collection_id == collection_id)
            .where(Integration.service == service)
            .where(Integration.is_active == True)
        ).first()