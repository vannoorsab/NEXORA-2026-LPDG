from pathlib import Path
from typing import Any

import sys

from .base import RankingStrategy


class ThreeSigmaRanker(RankingStrategy):
    """
    Ranking strategy that uses the provided 3-Sigma baseline.
    """

    def rank(
        self,
        data_dir: Path,
        week_start: str,
    ) -> list[dict[str, Any]]:
        """
        Generate ranked gateways for a single prediction week.

        The existing baseline_3sigma.py contains the actual ranking
        implementation. This class adapts that implementation to the
        RankingStrategy interface used by the application.
        """

        # Import the existing baseline from the project root.
        project_root = Path(__file__).resolve().parents[2]

        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        import baseline_3sigma

        # Load telemetry using the existing baseline loader.
        frame = baseline_3sigma.load(data_dir)

        # Convert the requested week into a date.
        import datetime as dt

        monday = dt.date.fromisoformat(week_start)

        # Run the existing ranking logic for this week.
        ranked = baseline_3sigma.rank_week(frame, monday)

        # Make sure there are enough gateways.
        if len(ranked) < baseline_3sigma.VISITS_PER_WEEK:
            raise ValueError(
                f"Only {len(ranked)} gateways have sufficient data "
                f"before {week_start}"
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