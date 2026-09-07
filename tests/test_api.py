from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predictions_endpoint_returns_15_gateways():
    response = client.get("/predictions/2026-02-02")

    assert response.status_code == 200

    data = response.json()

    assert data["week_start"] == "2026-02-02"
    assert data["count"] == 15
    assert len(data["predictions"]) == 15


def test_predictions_have_required_fields():
    response = client.get("/predictions/2026-02-02")

    assert response.status_code == 200

    predictions = response.json()["predictions"]

    required_fields = {
        "week_start",
        "rank",
        "gateway_id",
        "score",
        "reason",
    }

    for prediction in predictions:
        assert required_fields.issubset(prediction.keys())