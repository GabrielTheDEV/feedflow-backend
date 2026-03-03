from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

from app.models.enums.integrations import IntegrationService

class Integration(SQLModel, table=True):
    __tablename__ = "integrations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    collection_id: UUID = Field(foreign_key="collections.id", index=True)

    service: IntegrationService = Field(index=True)  # slack, jira, trello
    active: bool = Field(default=True)

    config_json: Optional[dict] = Field(default=None)
    external_id: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relationships
    collection: Optional["Collection"] = Relationship(back_populates="integrations")