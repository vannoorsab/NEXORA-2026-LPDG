# NEXORA 2026 — Gateway Visit Prioritization

A completed **Software Development** solution for the **LPDG × RGM
NEXORA 2026 Innovation Challenge**.

The project takes the supplied gateway telemetry and produces the required
weekly ranking of gateways that should be visited.

For Part 1, I used the provided `baseline_3sigma.py` as the foundation of
the ranking solution and generated the required `predictions.csv`.

For Part 2, I selected **Software Development** and built a maintainable
local Web API around the prediction workflow.

The Software Development implementation includes:

- a local FastAPI REST API;
- weekly prediction retrieval;
- gateway ranking explanations;
- prediction regeneration through `/run`;
- separation between API and ranking logic;
- a replaceable ranking strategy interface;
- deterministic ranking and tie-breaking;
- telemetry input validation;
- controlled handling of invalid input;
- missing-data handling;
- unknown-gateway handling;
- dynamic loading of newly available telemetry without restarting the API;
- safe runtime output generation;
- unit and service-level tests;
- API tests;
- end-to-end tests;
- regression tests for development bugs; and
- documentation of engineering decisions and AI usage.

> **Selected Part 2 area: Software Development**

---

## 1. Project Overview

The operational problem is to decide which gateways should receive a field
visit each week.

The required Part 1 output contains:

- 8 prediction weeks;
- 15 gateways per week;
- 120 rows in total;
- a rank from 1 to 15 for every week;
- a gateway identifier;
- a numeric score; and
- a reason explaining the ranking.

The completed solution preserves this required output while adding a software
interface that allows the prediction system to be queried and executed
again without directly interacting with the underlying Python implementation.

---

## 2. What I Built

### Part 1 — Gateway Ranking

I used the provided `baseline_3sigma.py` as the foundation for the ranking
logic.

The ranking uses operational gateway behaviour including:

- `offline_duration_sec`;
- `disconnection_cnt`; and
- `reboot_cnt`.

The workflow calculates abnormal behaviour relative to each gateway's
historical behaviour, assigns a score, orders gateways deterministically,
and selects the top 15 gateways for each prediction week.

The official output is:

```text
predictions.csv
```

I validated the generated file using:

```powershell
python validate_submission.py predictions.csv
```

The final submission contains:

- 8 weeks
- 15 gateways per week
- 120 rows total
### Part 2 — Software Development

I converted the prediction workflow into a local FastAPI application.

The API provides three main operational capabilities:

| Capability | Endpoint |
| --- | --- |
| Retrieve predictions for a week | `GET /predictions/{week_start}` |
| Explain a gateway's ranking | `GET /gateways/{gateway_id}/why` |
| Run the ranking again | `POST /run` |

Additional service endpoints are also provided:

| Endpoint | Purpose |
| --- | --- |
| `GET /` | Basic service information |
| `GET /health` | Health check |

The API does not contain the ranking algorithm directly.

Instead, the request flows through a service layer and then into a replaceable
ranking strategy.

## 3. Architecture

The implemented architecture is:

```text
                         HTTP Client
                              |
                              v
                    +-------------------+
                    |   FastAPI API     |
                    |   app/main.py     |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | PredictionService |
                    | prediction_service|
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | RankingStrategy   |
                    |    base.py        |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | ThreeSigmaRanker  |
                    | three_sigma.py    |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | baseline_3sigma   |
                    |     .py           |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Challenge Data    |
                    |     data/         |
                    +-------------------+
```

Component responsibilities
| Component | Responsibility |
| --- | --- |
| `app/main.py` | HTTP/API layer |
| `PredictionService` | Prediction workflow and output handling |
| `RankingStrategy` | Replaceable ranking interface |
| `ThreeSigmaRanker` | Current 3-Sigma ranking implementation |
| `telemetry_validator.py` | Telemetry input validation |
| `baseline_3sigma.py` | Part 1 ranking foundation |
| `tests/` | Automated verification |
## 4. Repository Structure
```text
NEXORA-2026-LPDG/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── ranking/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── three_sigma.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── prediction_service.py
│       └── telemetry_validator.py
│
├── tests/
│   ├── test_api.py
│   ├── test_prediction_e2e.py
│   ├── test_prediction_service.py
│   └── test_ranking.py
│
├── data/
│   └── challenge data
│
├── baseline_3sigma.py
├── validate_submission.py
├── predictions.csv
├── DECISIONS.md
├── AI-USAGE.md
├── requirements.txt
└── README.md
```

The challenge dataset is intentionally excluded from Git.

The application expects the challenge data to be available locally under
the top-level data/ directory.

## 5. Challenge Data

The supplied telemetry is organized into monthly Parquet partitions:

```text
data/
└── telemetry/
    ├── month=2025-08/
    ├── month=2025-09/
    ├── month=2025-10/
    ├── month=2025-11/
    ├── month=2025-12/
    ├── month=2026-01/
    ├── month=2026-02/
    └── month=2026-03/
```

The supplied data covers:

2025-08-01 to 2026-03-31

The telemetry contains approximately 1.43 million hourly rows across the
eight monthly partitions.

Other supplied files include:

```text
data/
├── telemetry/
├── telemetry_sample_2025-08.csv
├── gateway_master.csv
├── field_visits.csv
├── meter_read_success.csv
└── engineer_review_2026-02.xlsx
```

The implementation does not hard-code March 2026 as the permanent latest
month.

When /run is called, the application reads the currently available
telemetry and determines the latest prediction period dynamically.

## 6. Requirements

The project requires:

- Python 3.10 or newer
- pip
- The challenge dataset in the local `data/` directory

All Python package versions used during development are pinned in:

requirements.txt

The challenge does not require an external API, API key, cloud service,
online model or runtime download.

## 7. Installation

### Windows

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the pinned dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Make sure the challenge data/ directory is present at the project root.

The final structure should contain:

```text
NEXORA-2026-LPDG/
├── data/
├── app/
├── tests/
├── baseline_3sigma.py
└── ...
```
## 8. Generate the Part 1 Submission

The official Part 1 predictions can be generated with one command:

```powershell
python baseline_3sigma.py --data data --out predictions.csv
```

Expected result:

wrote predictions.csv — 120 rows over 8 weeks

The generated file is:

`predictions.csv`
## 9. Validate the Part 1 Submission

Run:

```powershell
python validate_submission.py predictions.csv
```

The validator checks the required submission structure.

A valid result confirms:

- `predictions.csv` exists
- 120 prediction rows are present
- Every prediction week contains exactly 15 gateways
- Ranks are valid
- Gateways are not repeated within a week
- The expected prediction weeks are present

The completed project was validated successfully.

## 10. Start the Software Development API

Start the local API with:

```powershell
python -m uvicorn app.main:app --reload
```

The service runs locally at:

[`http://127.0.0.1:8000`](http://127.0.0.1:8000)

FastAPI's interactive documentation is available at:

[`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

No online deployment is required.

The application is intentionally designed as a local service for the
challenge review workflow.

## 11. API Endpoints

### 11.1 Service Information
`GET /`

Returns basic information about the running application.

### 11.2 Health Check
`GET /health`

Used to confirm that the API process is running.

### 11.3 Get Weekly Predictions
`GET /predictions/{week_start}`

Example:

`GET /predictions/2026-03-23`

The endpoint returns the ranked gateways for the requested prediction week.

Each prediction contains:

- `week_start`
- `rank`
- `gateway_id`
- `score`
- `reason`

Example structure:

```json
{
  "week_start": "2026-03-23",
  "predictions": [
    {
      "week_start": "2026-03-23",
      "rank": 1,
      "gateway_id": "gateway-id",
      "score": 10.0,
      "reason": "..."
    }
  ]
}
```

### 11.4 Explain Why a Gateway Was Ranked
`GET /gateways/{gateway_id}/why`

The endpoint accepts the prediction week as a query parameter.

Example:

`GET /gateways/06B162DC93E3/why?week_start=2026-03-23`

The endpoint is designed to answer the operational question:

Why is this gateway in the ranking?

The explanation includes the gateway's ranking information and the reason
generated by the ranking layer.

Invalid or empty gateway identifiers are rejected.

Unknown gateways are returned as controlled 404 Not Found responses.

## 12. Regenerate Predictions with `/run`

The API provides:

`POST /run`

This endpoint runs the prediction workflow again using the telemetry that is
currently available.

The workflow is:

```text
POST /run
     |
     v
Validate telemetry
     |
     v
Reload current data
     |
     v
Find latest available period
     |
     v
Run ranking strategy
     |
     v
Generate exactly 15 predictions
     |
     v
Write runtime_predictions.csv
```

Example successful response:

```json
{
  "status": "success",
  "message": "Latest predictions generated successfully.",
  "output": ".../runtime_predictions.csv",
  "week_start": "2026-03-23",
  "rows": 15
}
```

The exact latest prediction week depends on the telemetry currently
available in data/.

## 13. Dynamic Data Reload

A key Software Development feature is that the application does not load
the telemetry only once when the server starts.

Each /run call reloads and validates the currently available telemetry.

This allows a new monthly partition to be added while the API is already
running.

The tested workflow was:

```text
Start API
    |
    v
Add new telemetry partition
    |
    v
POST /run
    |
    v
Application reloads telemetry
    |
    v
Application detects new latest period
    |
    v
New ranking is generated
```

I tested this behavior using synthetic monthly telemetry.

The test:

- Starts with an initial set of monthly data
- Runs the prediction service
- Adds another monthly partition
- Calls `/run` again without restarting the application
- Verifies that the latest prediction period changes

This verifies that the application is not dependent on a hard-coded
"latest month".

## 14. Ranking Strategy

The API does not directly depend on the implementation details of the
3-Sigma ranking algorithm.

The abstraction is defined in:

app/ranking/base.py

The current implementation is:

app/ranking/three_sigma.py

The structure is:

```text
RankingStrategy
      |
      +------ ThreeSigmaRanker
      |
      +------ Future ranking strategy
```

The RankingStrategy interface defines the contract required by the
prediction service.

Therefore, a different ranking implementation can be introduced without
rewriting the API handlers.

For example, a future implementation could conceptually be:

```text
RankingStrategy
      |
      +-- ThreeSigmaRanker
      |
      +-- AlternativeRanker
```

The API would continue using the same service and endpoint interface.

## 15. Deterministic Ranking

The ranking output must always contain a valid ordering from 1 to 15.

The implementation uses deterministic tie-breaking.

Gateways are ordered by:

- `flagged_hours` descending
- `gateway_id` ascending as the tie-breaker

Therefore, when two gateways have the same score, their order is still
stable.

A dedicated automated test runs the same ranking twice and verifies that
the results are identical.

This prevents random ordering from changing the recommended visit list
between identical runs.

## 16. Telemetry Validation

Before /run generates predictions, the input telemetry is validated by:

app/services/telemetry_validator.py

The validator checks:

- The telemetry directory exists
- Telemetry files are present
- Required columns exist
- Telemetry files are not empty
- Gateway identifiers contain usable values
- Timestamps contain usable values

The required telemetry fields checked by the validator are:

- `gateway_id`
- `ts_utc`

The validation happens before the ranking process starts.

This prevents malformed or incomplete telemetry from silently producing
invalid predictions.

## 17. Error Handling

The API converts expected application problems into controlled HTTP
responses.

| Situation | Response |
| --- | --- |
| Invalid date or request value | `400 Bad Request` |
| Empty/invalid gateway identifier | `400 Bad Request` |
| Invalid telemetry | `400 Bad Request` |
| Missing prediction/data file | `404 Not Found` |
| Unknown gateway | `404 Not Found` |
| Unexpected prediction failure | `500 Internal Server Error` |

The API therefore does not require callers to understand internal Python
exceptions.

## 18. Runtime Output Safety

The official Part 1 submission is:

predictions.csv

The /run endpoint does not overwrite the official submission.

Instead, it generates:

runtime_predictions.csv

This separates exploratory/runtime API execution from the final submission
artifact.

Runtime predictions are written to a temporary file first and then moved
into place using atomic replacement after a successful write.

The runtime output is also ignored by Git.

## 19. Testing

The complete test suite can be executed using:

python -m pytest -q

The tests are separated by responsibility.

| Test file | Coverage |
| --- | --- |
| `tests/test_ranking.py` | Ranking and deterministic ordering |
| `tests/test_prediction_service.py` | Service and output behavior |
| `tests/test_api.py` | HTTP responses and API error handling |
| `tests/test_prediction_e2e.py` | Complete synthetic prediction workflow |

The test suite covers:

ranking behavior;
deterministic ranking;
prediction service behavior;
API endpoints;
invalid input;
unknown gateways;
telemetry validation;
end-to-end prediction generation;
dynamic monthly data reload; and
regression cases based on development bugs.

Synthetic fixtures are used where possible so the majority of the Software
Development tests do not depend on the full challenge dataset.

## 20. Testing Evidence

The final development test suite contains:

22 tests

All tests passed during the completed development validation.

The Part 1 submission was independently validated using:

python validate_submission.py predictions.csv

The validator confirmed the required 120-row structure with 15 ranked
gateways for each prediction week.

The dynamic reload behavior was also manually verified by:

starting the API;
adding a temporary new monthly telemetry partition;
calling /run without restarting the API;
observing the newly detected prediction period;
confirming 15 generated rows; and
removing the temporary partition.
## 21. Development and Debugging

The Software Development implementation was built incrementally.

The main engineering improvements were:

1. Prediction service layer
        ↓
2. Ranking/API separation
        ↓
3. Replaceable ranking strategy
        ↓
4. Deterministic ranking
        ↓
5. Telemetry validation
        ↓
6. API error handling
        ↓
7. Runtime prediction generation
        ↓
8. Atomic runtime output
        ↓
9. Synthetic E2E tests
        ↓
10. Dynamic data reload testing
        ↓
11. Regression tests

This allowed individual components to be tested independently before
testing the complete API workflow.

## 22. Requirement → Implementation Mapping

The following table maps the Software Development requirements to the
implemented project components.

| Software Development requirement | Implemented solution |
| --- | --- |
| Ask for this week's 15 gateways | `GET /predictions/{week_start}` |
| Ask why a gateway is ranked | `GET /gateways/{gateway_id}/why` |
| Tell the system to run again | `POST /run` |
| Separate API from ranking | `PredictionService` + ranking layer |
| Ranking can be replaced | `RankingStrategy` abstraction |
| Test the system | Unit, API, and E2E tests |
| Handle bad input | Request validation and controlled 400 responses |
| Handle missing data | Telemetry validation |
| Handle unknown gateway | Controlled 404 response |
| New month without restart | Dynamic telemetry reload |
| Stable ranking | Deterministic tie-breaking |
| Safe runtime generation | Temporary file + atomic replacement |
| Reproducible environment | Pinned `requirements.txt` |
| Stranger can run project | README setup and execution instructions |
## 23. Part 1 Ranking Interpretation

The ranking score represents abnormal operational behavior relative to a
gateway's historical behavior.

It is used as a visit-priority signal.

It should not be interpreted as a guaranteed probability that a gateway will
fail in the future.

The ranking is therefore intended to answer:

Which gateways currently show the strongest abnormal behavior and should
be prioritized for investigation?

The detailed reasoning, alternatives considered, assumptions, limitations
and trade-offs are documented in:

DECISIONS.md
## 24. Data and Operational Considerations

The challenge data contains several different sources of operational
evidence.

The implementation does not automatically assume that every available
column should be used.

The Part 1 ranking remains based on the provided 3-Sigma approach and its
operational signals.

This was an intentional engineering decision because the selected Part 2
area is Software Development.

The detailed alternatives and reasoning are documented separately in
DECISIONS.md.

## 25. Limitations

The current implementation has the following limitations:

- The ranking uses the provided 3-Sigma approach rather than a newly trained predictive ML model.
- The score represents abnormal operational behavior and visit priority, not a guaranteed future failure probability.
- The API is designed as a local challenge service rather than a distributed production system.
- The current design assumes a small operations team and approximately one prediction run per week.
- The implementation does not require an external online service or API key.
- The challenge data remains outside the Git repository.

These limitations are intentional and are discussed further in
DECISIONS.md.

## 26. Quick Start

For a fresh environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python baseline_3sigma.py --data data --out predictions.csv
python validate_submission.py predictions.csv

python -m pytest -q

python -m uvicorn app.main:app --reload
```

Then open:

[`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

## 27. Important Files
### `baseline_3sigma.py`

Provides the foundation for the Part 1 ranking workflow.

### `validate_submission.py`

Validates the official predictions.csv structure and ranking constraints.

### `app/main.py`

Contains the FastAPI HTTP interface.

### `app/services/prediction_service.py`

Contains the application-level prediction workflow.

### `app/services/telemetry_validator.py`

Validates telemetry before a fresh /run.

### `app/ranking/base.py`

Defines the replaceable ranking strategy contract.

### `app/ranking/three_sigma.py`

Connects the provided 3-Sigma ranking logic to the application.

### `tests/`

Contains automated tests for ranking, services, API behavior and
end-to-end workflows.

### `DECISIONS.md`

Contains engineering decisions, alternatives, trade-offs, assumptions and
limitations.

### `AI-USAGE.md`

Documents how AI tools were used during development and includes examples
of AI output that was manually checked and corrected.

## 28. Documentation

The repository contains three main documentation artifacts.

### `README.md`

Explains:

- What was built
- How the project is structured
- How to install it
- How to generate predictions
- How to validate predictions
- How to start the API
- How the API works
- How the tests work
- How the implementation maps to the Software Development requirements

### `DECISIONS.md`

Contains the reasoning behind the implementation, including:

- Alternatives considered
- Why the 3-Sigma baseline was retained
- Ranking decisions
- Deterministic tie-breaking
- Software Development architecture
- API design
- `/run` behavior
- Data handling
- Assumptions, limitations, and trade-offs

### `AI-USAGE.md`

Documents:

- Where AI assistance was used
- Development assistance
- Debugging
- Documentation
- Verification
- An example of an AI-generated mistake that was caught and corrected
## 29. Final Deliverables

The completed repository contains:

- `predictions.csv`
- Part 1 generation command
- Part 1 validation
- `DECISIONS.md`
- `AI-USAGE.md`
- `README.md`
- Software Development API
- Prediction service
- Replaceable ranking strategy
- Telemetry validation
- Error handling
- Deterministic ranking
- Dynamic `/run` behavior
- Automated tests
- End-to-end tests
- Regression tests

The challenge data is intentionally not committed to the repository.

## 30. Demo Recording

The final 6–8 minute recording demonstrates the completed implementation.

The recording covers:

the Part 1 predictions.csv;
submission validation;
starting the local API;
retrieving weekly predictions;
explaining a gateway ranking;
running /run;
demonstrating dynamic telemetry reload;
running the automated test suite; and
demonstrating the Software Development implementation.

Demo Recording:

Add the final externally accessible recording link here.

## 31. Final Result

This project started from the provided Part 1 ranking baseline and was
developed into a structured Software Development solution.

The final implementation provides:

Part 1
  ↓
Validated weekly gateway ranking
  ↓
Prediction service
  ↓
Replaceable ranking strategy
  ↓
FastAPI interface
  ↓
Validation + error handling
  ↓
Dynamic data reload
  ↓
Automated testing

The focus was intentionally kept on Software Development rather than
adding unrelated functionality.

The main engineering goal was to make the solution:

correct;
understandable;
testable;
deterministic;
maintainable;
safe to modify; and
easy for another developer to run locally.
Author

Vannoor Sab Dudekula

NEXORA 2026 — LPDG × RGM Innovation Challenge

Track: Software Development