from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.models.enums.plans import Plan
from app.models.enums.status import Status


#tabela de collections gerencia e contem os dominios
class Collection(SQLModel, table=True):
    __tablename__ = "collections"

    id: UUID = Field(default_factory=uuid4, primary_key=True , index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)

    name: str = Field(max_length=120, nullable=False)

    api_key: str = Field(default=None, index=True, unique=True)
    api_key_created_at: Optional[datetime] = None
    api_key_revoked_at: Optional[datetime] = None

    plan: Plan = Field(default=Plan.free)
    is_active: bool = Field(default=True)
    status: Status = Field(default=Status.working)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relationships
    user: Optional["User"] = Relationship(back_populates="collections")
    domains: List["Domain"] = Relationship(back_populates="collection")
    integrations: List["Integration"] = Relationship(back_populates="collection")