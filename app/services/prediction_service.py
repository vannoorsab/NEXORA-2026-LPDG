from pathlib import Path
from typing import Any

from app.ranking import RankingStrategy


class PredictionService:
    """
    Service responsible for generating and retrieving gateway predictions.

    The service depends on the RankingStrategy interface rather than a
    specific ranking implementation.
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

        Args:
            week_start: Prediction week in YYYY-MM-DD format.

        Returns:
            A list containing the ranked gateways.
        """

        return self.ranking_strategy.rank(
            data_dir=self.data_dir,
            week_start=week_start,
        )