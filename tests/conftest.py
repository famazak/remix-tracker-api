from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.main import app


@pytest.fixture
def mock_db_session():
    """Create a mock AsyncSession for testing"""
    session = AsyncMock(spec=AsyncSession)

    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()

    return session


@pytest.fixture
def override_get_session(mock_db_session):
    """Override the get_session dependency"""

    async def _get_session():
        yield mock_db_session

    return _get_session


@pytest.fixture
def test_client(override_get_session) -> Generator[TestClient, None, None]:
    """Create a test client with mocked database session"""
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
