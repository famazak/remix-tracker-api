import os
from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T")

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
)
connectable = create_async_engine(DATABASE_URL, echo=True, future=True)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        connectable, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


class DatabaseErrorType(str, Enum):
    INTEGRITY_ERROR = "IntegrityError"
    NOT_FOUND_ERROR = "NotFoundError"


@dataclass
class DatabaseError:
    error_type: DatabaseErrorType


class DatabaseResult(BaseModel, Generic[T]):
    success: bool
    error: Optional[DatabaseError]
    data: Optional[T]
