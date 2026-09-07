from pathlib import Path

from app.ranking import ThreeSigmaRanker


def test_three_sigma_ranker_can_be_created():
    ranker = ThreeSigmaRanker()

    assert ranker is not None


def test_three_sigma_ranker_returns_15_gateways():
    ranker = ThreeSigmaRanker()

    result = ranker.rank(
        data_dir=Path("data"),
        week_start="2026-02-02",
    )

    assert len(result) == 15


def test_three_sigma_ranker_returns_required_fields():
    ranker = ThreeSigmaRanker()

    result = ranker.rank(
        data_dir=Path("data"),
        week_start="2026-02-02",
    )

    required_fields = {
        "week_start",
        "rank",
        "gateway_id",
        "score",
        "reason",
    }

    assert required_fields.issubset(result[0].keys())


def test_three_sigma_ranker_returns_ordered_ranks():
    ranker = ThreeSigmaRanker()

    result = ranker.rank(
        data_dir=Path("data"),
        week_start="2026-02-02",
    )

    ranks = [item["rank"] for item in result]

    assert ranks == list(range(1, 16))