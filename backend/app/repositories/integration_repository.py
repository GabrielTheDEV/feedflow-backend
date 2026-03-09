from typing import Optional, List
from sqlmodel import Session, select
from uuid import UUID

from app.models.integrations import Integration


class IntegrationRepository:
    def __init__(self, session: Session):
        self.session = session



    def create(self, integration: Integration) -> Integration:
        self.session.add(integration)
        self.session.commit()
        self.session.refresh(integration)
        return integration


    def get_by_id(self, integration_id: UUID) -> Optional[Integration]:
        return self.session.get(Integration, integration_id)


    def get_by_collection(self, collection_id: UUID) -> List[Integration]:
        statement = select(Integration).where(
            Integration.collection_id == collection_id
        )
        return list(self.session.exec(statement))


    def save(self, integration: Integration) -> Integration:
        self.session.add(integration)
        self.session.commit()
        self.session.refresh(integration)
        return integration
        

    def delete(self, integration: Integration) -> None:
        self.session.delete(integration)
        self.session.commit()