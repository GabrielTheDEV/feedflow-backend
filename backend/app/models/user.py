from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, EmailStr
from uuid import UUID
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True)  # vem do Supabase
    email: EmailStr = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relationships
    collections: List["Collection"] = Relationship(back_populates="user")