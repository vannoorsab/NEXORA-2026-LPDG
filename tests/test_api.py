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


def test_gateway_why_endpoint():
    predictions_response = client.get(
        "/predictions/2026-02-02"
    )

    assert predictions_response.status_code == 200

    predictions = predictions_response.json()["predictions"]

    gateway_id = predictions[0]["gateway_id"]

    response = client.get(
        f"/gateways/{gateway_id}/why?week=2026-02-02"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["week_start"] == "2026-02-02"
    assert data["gateway_id"] == gateway_id
    assert data["rank"] == 1
    assert "score" in data
    assert "reason" in data


def test_gateway_why_returns_404_for_unknown_gateway():
    response = client.get(
        "/gateways/UNKNOWN-GATEWAY/why?week=2026-02-02"
    )

    assert response.status_code == 404