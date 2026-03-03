from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime


class Collection(SQLModel, table=True):
    __tablename__ = "collections"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    name: str

    api_key: Optional[str] = Field(default=None, index=True)
    api_key_created_at: Optional[datetime] = None
    api_key_revoked_at: Optional[datetime] = None

    plan: str = Field(default="free")
    is_active: bool = Field(default=True)
    status: str = Field(default="working")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relationships
    user: Optional["User"] = Relationship(back_populates="collections")
    domains: List["Domain"] = Relationship(back_populates="collection")
    integrations: List["Integration"] = Relationship(back_populates="collection")