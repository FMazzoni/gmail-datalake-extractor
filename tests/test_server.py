import pytest
from fastapi.testclient import TestClient

from gmail_datalake_extractor.api import app

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
            "max_results": 10,
            "fetch_config": {
                "messages_per_batch": 25,
                "response_format": "full",
            },
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "task_id" in response_data
    assert response_data["status"] == "started"
    assert response_data["message"] == "Extraction task started successfully"


if __name__ == "__main__":
    pytest.main(
        ["-v", __file__],
    )
