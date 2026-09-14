from pathlib import Path

import pytest

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

def test_failed_run_keeps_previous_runtime_output(tmp_path, monkeypatch):
    output_path = tmp_path / "predictions.csv"
    runtime_path = tmp_path / "runtime_predictions.csv"
    (tmp_path / "telemetry").mkdir()

    runtime_content = (
        "week_start,rank,gateway_id,score,reason\n"
        "2026-03-02,1,G001,10.0,test\n"
    )
    runtime_path.write_text(runtime_content)

    service = PredictionService(
        data_dir=tmp_path,
        ranking_strategy=ThreeSigmaRanker(),
        output_path=output_path,
        runtime_output_path=runtime_path,
    )

    monkeypatch.setattr(
        "app.services.prediction_service.validate_telemetry",
        lambda data_dir: None,
    )

    def fail_ranking(*args, **kwargs):
        raise RuntimeError("simulated ranking failure")

    monkeypatch.setattr(service.ranking_strategy, "rank_latest", fail_ranking)

    with pytest.raises(RuntimeError, match="simulated ranking failure"):
        service.run_latest_predictions()

    assert runtime_path.read_text() == runtime_content
