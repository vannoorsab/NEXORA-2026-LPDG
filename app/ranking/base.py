from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class RankingStrategy(ABC):
    """
    Interface for gateway ranking strategies.

    Different ranking implementations can inherit from this class
    without requiring changes to the API layer.
    """

    @abstractmethod
    def rank(
        self,
        data_dir: Path,
        week_start: str,
    ) -> list[dict[str, Any]]:
        """
        Rank gateways for a given prediction week.

        Args:
            data_dir: Directory containing challenge data.
            week_start: Prediction week in YYYY-MM-DD format.

        Returns:
            A list of ranked gateway dictionaries.
        """
        raise NotImplementedError