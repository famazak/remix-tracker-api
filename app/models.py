from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy import DateTime, UniqueConstraint, func
from sqlmodel import Column, Field, SQLModel

DataT = TypeVar("DataT")


class Response(BaseModel, Generic[DataT]):
    success: bool
    message: Optional[str]
    data: list[DataT] = Field(default_factory=list)


class TrackBronzeBase(SQLModel):
    __table_args__ = (UniqueConstraint("character_name", "realm_name"),)

    character_name: str = Field(max_length=32)
    realm_name: str = Field(max_length=32)
    bronze_total: int


class TrackBronze(TrackBronzeBase, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), onupdate=func.now()),
    )


class TrackBronzeCreate(TrackBronzeBase):
    pass
