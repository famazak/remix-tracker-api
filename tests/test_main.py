from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.models import TrackBronze

client = TestClient(app)


def test_track_bronze(test_client, mock_db_session):
    mock_result = TrackBronze(
        id=1, character_name="Anariele", realm_name="Area-52", bronze_total=2800
    )

    mock_db_session.refresh.return_value = mock_result

    response = test_client.post(
        "/track",
        json={
            "character_name": "Anariele",
            "realm_name": "Area-52",
            "bronze_total": 2800,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["character_name"] == "Anariele"
    assert data["data"][0]["realm_name"] == "Area-52"
    assert data["data"][0]["bronze_total"] == 2800


def test_track_bronze_duplicate(test_client, mock_db_session):
    mock_db_session.commit.side_effect = IntegrityError(
        statement=None, params=None, orig=Exception
    )
    mock_db_session.rollback = AsyncMock()

    response = test_client.post(
        "/track",
        json={
            "character_name": "Anariele",
            "realm_name": "Area-52",
            "bronze_total": 2800,
        },
    )

    assert response.status_code == 409
    data = response.json()
    assert data["message"] == "A character with this name and realm already exists"
