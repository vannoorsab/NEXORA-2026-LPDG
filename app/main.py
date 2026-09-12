import datetime as dt
from pathlib import Path

from fastapi import FastAPI, HTTPException

from app.ranking import ThreeSigmaRanker
from app.services import PredictionService


app = FastAPI(
    title="NEXORA Gateway Prioritization API",
    description="API for gateway visit prioritization",
    version="1.0.0",
)


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# Ranking strategy
ranking_strategy = ThreeSigmaRanker()

# Prediction service
prediction_service = PredictionService(
    data_dir=DATA_DIR,
    ranking_strategy=ranking_strategy,
    output_path=PROJECT_ROOT / "predictions.csv",
)


@app.get("/")
def root():
    return {
        "service": "NEXORA Gateway Prioritization API",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/predictions/{week_start}")
def get_predictions(week_start: str):
    # Validate date format
    try:
        dt.date.fromisoformat(week_start)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="week_start must be a valid date in YYYY-MM-DD format.",
        ) from exc

    try:
        predictions = prediction_service.get_predictions(week_start)

        return {
            "week_start": week_start,
            "count": len(predictions),
            "predictions": predictions,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Required prediction data was not found.",
        ) from exc


@app.get("/gateways/{gateway_id}/why")
def get_gateway_explanation(gateway_id: str, week: str):
    gateway_id = gateway_id.strip()
    week = week.strip()

    if not gateway_id:
        raise HTTPException(
            status_code=400,
            detail="gateway_id must not be empty.",
        )

    try:
        dt.date.fromisoformat(week)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="week must be a valid date in YYYY-MM-DD format.",
        ) from exc

    try:
        prediction = prediction_service.get_gateway_explanation(
            gateway_id=gateway_id,
            week_start=week,
        )

        return {
            "week_start": week,
            "gateway_id": gateway_id,
            "rank": prediction["rank"],
            "score": prediction["score"],
            "reason": prediction["reason"],
        }

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Required prediction data was not found.",
        ) from exc


@app.post("/run")
def run_predictions():
    try:
        result = prediction_service.run_latest_predictions()
        return result

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction run failed: {exc}",
        ) from exc