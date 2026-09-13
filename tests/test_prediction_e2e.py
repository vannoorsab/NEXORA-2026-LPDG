from pathlib import Path

import pandas as pd

from app.ranking import ThreeSigmaRanker
from app.services import PredictionService


def create_telemetry_file(
    telemetry_root: Path,
    month: str,
    start_date: str,
):
    month_dir = telemetry_root / f"month={month}"
    month_dir.mkdir(parents=True, exist_ok=True)

    rows = []

    gateways = [
        "GW001",
        "GW002",
        "GW003",
        "GW004",
        "GW005",
        "GW006",
        "GW007",
        "GW008",
        "GW009",
        "GW010",
        "GW011",
        "GW012",
        "GW013",
        "GW014",
        "GW015",
    ]

    timestamps = pd.date_range(
        start=start_date,
        periods=24 * 35,
        freq="h",
        tz="UTC",
    )

    for gateway_id in gateways:
        for ts in timestamps:
            rows.append(
                {
                    "gateway_id": gateway_id,
                    "ts_utc": ts.strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "DateDt": ts.strftime("%Y-%m-%d"),
                    "hour": ts.hour,
                    "offline_duration_sec": 0,
                    "disconnection_cnt": 0,
                    "reboot_cnt": 0,
                }
            )

    frame = pd.DataFrame(rows)

    frame.to_parquet(
        month_dir / "part-0.parquet",
        index=False,
    )


def test_run_latest_predictions_with_fixture(tmp_path):
    data_dir = tmp_path / "data"
    telemetry_dir = data_dir / "telemetry"

    create_telemetry_file(
        telemetry_dir,
        "2026-01",
        "2026-01-01",
    )

    create_telemetry_file(
        telemetry_dir,
        "2026-02",
        "2026-02-01",
    )

    service = PredictionService(
        data_dir=data_dir,
        ranking_strategy=ThreeSigmaRanker(),
        runtime_output_path=tmp_path / "runtime_predictions.csv",
    )

    result = service.run_latest_predictions()

    assert result["status"] == "success"
    assert result["rows"] == 15
    assert result["week_start"] == "2026-03-02"

    output_file = Path(result["output"])

    assert output_file.exists()

    output = pd.read_csv(output_file)

    assert len(output) == 15
    assert output["rank"].tolist() == list(range(1, 16))
    assert output["gateway_id"].nunique() == 15

def test_run_picks_up_new_month_without_restarting_service(tmp_path):
    data_dir = tmp_path / "data"
    telemetry_dir = data_dir / "telemetry"

    create_telemetry_file(
        telemetry_dir,
        "2026-01",
        "2026-01-01",
    )

    create_telemetry_file(
        telemetry_dir,
        "2026-02",
        "2026-02-01",
    )

    service = PredictionService(
        data_dir=data_dir,
        ranking_strategy=ThreeSigmaRanker(),
        runtime_output_path=tmp_path / "runtime_predictions.csv",
    )

    # First run sees January + February.
    first_result = service.run_latest_predictions()

    assert first_result["status"] == "success"
    assert first_result["rows"] == 15
    assert first_result["week_start"] == "2026-03-02"

    # Simulate a new month arriving while the same service
    # instance is still running.
    create_telemetry_file(
        telemetry_dir,
        "2026-03",
        "2026-03-01",
    )

    # Run again WITHOUT creating a new PredictionService.
    second_result = service.run_latest_predictions()

    assert second_result["status"] == "success"
    assert second_result["rows"] == 15
    assert second_result["week_start"] == "2026-03-30"

    assert (
        second_result["week_start"]
        != first_result["week_start"]
    )