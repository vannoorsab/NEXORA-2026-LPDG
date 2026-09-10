from pathlib import Path
from typing import Any

import baseline_3sigma


class PredictionService:
    """Service responsible for generating and retrieving predictions."""

    def __init__(
        self,
        data_dir: Path,
        ranking_strategy,
        output_path: Path | None = None,
    ) -> None:
        self.data_dir = data_dir
        self.ranking_strategy = ranking_strategy
        self.output_path = output_path or (self.data_dir.parent / "predictions.csv")

    def get_predictions(self, week_start: str) -> list[dict[str, Any]]:
        """Generate predictions for a specific week."""
        return self.ranking_strategy.rank(
            data_dir=self.data_dir,
            week_start=week_start,
        )

    def get_gateway_explanation(
        self,
        gateway_id: str,
        week_start: str,
    ) -> dict[str, Any]:
        """Find a gateway in the weekly ranking and return its explanation."""
        predictions = self.get_predictions(week_start)

        for prediction in predictions:
            if prediction["gateway_id"] == gateway_id:
                return prediction

        raise KeyError(
            f"Gateway '{gateway_id}' was not found in the top 15 predictions "
            f"for {week_start}."
        )

    def run_predictions(self) -> dict[str, Any]:
        """Generate predictions for all scored weeks and write predictions.csv."""
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