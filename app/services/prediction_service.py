import os
from pathlib import Path
from typing import Any
from app.services.telemetry_validator import validate_telemetry

import baseline_3sigma


class PredictionService:
    """Generate and retrieve gateway predictions."""

    def __init__(
        self,
        data_dir: Path,
        ranking_strategy,
        output_path: Path | None = None,
        runtime_output_path: Path | None = None,
    ) -> None:
        self.data_dir = data_dir
        self.ranking_strategy = ranking_strategy
        self.output_path = output_path or self.data_dir.parent / "predictions.csv"
        self.runtime_output_path = runtime_output_path or (
            self.data_dir.parent / "runtime_predictions.csv"
        )

    def get_predictions(self, week_start: str) -> list[dict[str, Any]]:
        return self.ranking_strategy.rank(
            data_dir=self.data_dir,
            week_start=week_start,
        )

    def get_gateway_explanation(
        self,
        gateway_id: str,
        week_start: str,
    ) -> dict[str, Any]:
        predictions = self.get_predictions(week_start)

        for prediction in predictions:
            if prediction["gateway_id"] == gateway_id:
                return prediction

        raise KeyError(
            f"Gateway '{gateway_id}' was not found in the "
            f"top 15 predictions for {week_start}."
        )

    def run_predictions(self) -> dict[str, Any]:
        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Data directory does not exist: {self.data_dir}"
            )

        telemetry_dir = self.data_dir / "telemetry"
        if not telemetry_dir.exists():
            raise FileNotFoundError(
                f"Telemetry directory does not exist: {telemetry_dir}"
            )

        frame = baseline_3sigma.load(self.data_dir)
        predictions = baseline_3sigma.build_predictions(frame)
        predictions.to_csv(self.output_path, index=False)

        return {
            "status": "success",
            "message": "Predictions generated successfully.",
            "output": str(self.output_path),
            "rows": len(predictions),
            "weeks": predictions["week_start"].nunique(),
        }

    def run_latest_predictions(self) -> dict[str, Any]:
        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Data directory does not exist: {self.data_dir}"
            )

        telemetry_dir = self.data_dir / "telemetry"
        if not telemetry_dir.exists():
            raise FileNotFoundError(
                f"Telemetry directory does not exist: {telemetry_dir}"
            )
        validate_telemetry(self.data_dir)

        predictions = self.ranking_strategy.rank_latest(data_dir=self.data_dir)
        if not predictions:
            raise ValueError("No predictions were generated.")

        output_path = self.runtime_output_path
        temp_path = output_path.with_suffix(".tmp.csv")

        try:
            import pandas as pd

            prediction_frame = pd.DataFrame(predictions)
            prediction_frame.to_csv(temp_path, index=False)
            os.replace(temp_path, output_path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

        return {
            "status": "success",
            "message": "Latest predictions generated successfully.",
            "output": str(output_path),
            "week_start": predictions[0]["week_start"],
            "rows": len(predictions),
        }
