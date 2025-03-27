from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_track_bronze():
    response = client.post(
        "/track",
        json={
            "character_name": "Kendub",
            "realm_name": "Area-52",
            "bronze_total": 2800,
        },
    )
    assert response.status_code == 201
