from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class Domain(SQLModel, table=True):
    __tablename__ = "domains"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    collection_id: UUID = Field(foreign_key="collections.id", index=True)

    domain: str = Field(index=True)

    active: bool = Field(default=True)
    verified: bool = Field(default=False)
    verified_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relationships
    collection: Optional["Collection"] = Relationship(back_populates="domains")