from pathlib import Path

from app.ranking import ThreeSigmaRanker
from app.services import PredictionService


def test_prediction_service_returns_15_predictions():
    service = PredictionService(
        data_dir=Path("data"),
        ranking_strategy=ThreeSigmaRanker(),
    )

    result = service.get_predictions("2026-02-02")

    assert len(result) == 15


def test_prediction_service_returns_correct_week():
    service = PredictionService(
        data_dir=Path("data"),
        ranking_strategy=ThreeSigmaRanker(),
    )

    result = service.get_predictions("2026-02-02")

    assert all(
        prediction["week_start"] == "2026-02-02"
        for prediction in result
    )