import datetime as dt
import sys
from pathlib import Path
from typing import Any

from .base import RankingStrategy


class ThreeSigmaRanker(RankingStrategy):
    """Rank gateways using the existing 3-sigma baseline."""

    def _load_baseline(self, data_dir: Path):
        project_root = Path(__file__).resolve().parents[2]

        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        import baseline_3sigma

        return baseline_3sigma, baseline_3sigma.load(data_dir)

    def _build_week_predictions(
        self,
        baseline_3sigma,
        frame,
        week_start: str,
    ) -> list[dict[str, Any]]:
        monday = dt.date.fromisoformat(week_start)
        ranked = baseline_3sigma.rank_week(frame, monday)

        if len(ranked) < baseline_3sigma.VISITS_PER_WEEK:
            raise ValueError(
                f"Only {len(ranked)} gateways have sufficient "
                f"data before {week_start}"
            )

        predictions = []
        for rank, row in enumerate(
            ranked.head(baseline_3sigma.VISITS_PER_WEEK).itertuples(index=False),
            1,
        ):
            metric = row.worst_metric or "no metric over 3 sigma"
            predictions.append(
                {
                    "week_start": week_start,
                    "rank": rank,
                    "gateway_id": row.gateway_id,
                    "score": float(row.flagged_hours),
                    "reason": (
                        f"{row.flagged_hours} hour(s) beyond 3 sigma of this "
                        f"gateway's own 28-day baseline in the last 7 days; "
                        f"first breach on {metric}"
                    ),
                }
            )

        return predictions

    def rank(
        self,
        data_dir: Path,
        week_start: str,
    ) -> list[dict[str, Any]]:
        baseline_3sigma, frame = self._load_baseline(data_dir)
        return self._build_week_predictions(
            baseline_3sigma,
            frame,
            week_start,
        )

    def rank_latest(
        self,
        data_dir: Path,
    ) -> list[dict[str, Any]]:
        baseline_3sigma, frame = self._load_baseline(data_dir)

        if frame.empty:
            raise ValueError("Telemetry data is empty.")

        max_timestamp = frame["ts"].max()
        if max_timestamp is None:
            raise ValueError("Telemetry contains no timestamps.")

        max_date = max_timestamp.date()
        latest_monday = max_date - dt.timedelta(days=max_date.weekday())
        week_start = latest_monday.isoformat()

        return self._build_week_predictions(
            baseline_3sigma,
            frame,
            week_start,
        )
