from pathlib import Path

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
    response = client.get("/gateways/UNKNOWN-GATEWAY/why?week=2026-02-02")

    assert response.status_code == 404


def test_run_endpoint():
    response = client.post("/run")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["rows"] == 15
    assert data["week_start"] == "2026-03-30"
    assert "runtime_predictions.csv" in data["output"]


def test_run_creates_runtime_predictions_file():
    response = client.post("/run")

    assert response.status_code == 200

    predictions_file = response.json()["output"]

    from pathlib import Path

    assert Path(predictions_file).exists()
    assert Path(predictions_file).name == "runtime_predictions.csv"

def test_predictions_reject_invalid_week_format():
    response = client.get("/predictions/not-a-date")

    assert response.status_code == 400
    assert "YYYY-MM-DD" in response.json()["detail"]


def test_predictions_reject_invalid_date():
    response = client.get("/predictions/2026-99-99")

    assert response.status_code == 400
    assert "YYYY-MM-DD" in response.json()["detail"]


def test_gateway_why_rejects_empty_gateway():
    response = client.get(
        "/gateways/%20/why?week=2026-03-30"
    )

    assert response.status_code == 400
    assert "gateway_id must not be empty" in response.json()["detail"]


def test_run_returns_clear_error_for_missing_telemetry(
    monkeypatch,
):
    from app.main import prediction_service

    def fake_rank_latest(data_dir):
        raise ValueError(
            "Telemetry is missing required column: ts"
        )

    monkeypatch.setattr(
        prediction_service.ranking_strategy,
        "rank_latest",
        fake_rank_latest,
    )

    response = client.post("/run")

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Telemetry is missing required column: ts"
    )


def test_run_returns_clear_error_for_empty_telemetry(monkeypatch):
    from app.main import prediction_service

    def fake_rank_latest(data_dir):
        raise ValueError("Telemetry file contains no rows.")

    monkeypatch.setattr(
        prediction_service.ranking_strategy,
        "rank_latest",
        fake_rank_latest,
    )

    response = client.post("/run")

    assert response.status_code == 400
    assert "no rows" in response.json()["detail"]