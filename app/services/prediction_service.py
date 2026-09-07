from pathlib import Path
from typing import Any

from app.ranking import RankingStrategy


class PredictionService:
    """
    Service responsible for generating and retrieving gateway predictions.
    """

    def __init__(
        self,
        data_dir: Path,
        ranking_strategy: RankingStrategy,
    ) -> None:
        self.data_dir = data_dir
        self.ranking_strategy = ranking_strategy

    def get_predictions(
        self,
        week_start: str,
    ) -> list[dict[str, Any]]:
        """
        Generate predictions for a specific week.
        """

        return self.ranking_strategy.rank(
            data_dir=self.data_dir,
            week_start=week_start,
        )

    def get_gateway_explanation(
        self,
        gateway_id: str,
        week_start: str,
    ) -> dict[str, Any]:
        """
        Find a gateway in the weekly ranking and return
        its rank, score and explanation.
        """

        predictions = self.get_predictions(week_start)

        for prediction in predictions:
            if prediction["gateway_id"] == gateway_id:
                return prediction

        raise KeyError(
            f"Gateway '{gateway_id}' was not found in the "
            f"top 15 predictions for {week_start}."
        )