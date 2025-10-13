import pytest
from fastapi.testclient import TestClient

from message_extract.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_extract():
    response = client.post(
        "/extract",
        json={
            "query": "",
            "max_results": 500,
            "fetch_config": {
                "messages_per_batch": 25,
                "response_format": "full",
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {"success": True, "message_count": 500, "query": ""}


if __name__ == "__main__":
    pytest.main(
        ["-v", __file__],
    )
