from fastapi import FastAPI


app = FastAPI(
    title="NEXORA Gateway Prioritization API",
    description="API for gateway visit prioritization",
    version="1.0.0",
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
        "status": "healthy"
    }