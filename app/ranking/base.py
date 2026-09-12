from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class RankingStrategy(ABC):
    @abstractmethod
    def rank(
        self,
        data_dir: Path,
        week_start: str,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def rank_latest(
        self,
        data_dir: Path,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError
