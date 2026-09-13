# NEXORA 2026 - Engineering Decisions

## Overview

The objective of this challenge is to produce a ranked list of 15 gateways to visit for each required prediction week.

For Part 1, I used the provided `baseline_3sigma.py` as the foundation of the ranking solution and generated the required `predictions.csv`.

For Part 2, I selected **Software Development**. The goal is to turn the working ranking logic into a maintainable local web API with clear separation of responsibilities, validation, error handling, testing, and support for new telemetry while the service is running.

The main priorities are:

1. Keep the required Part 1 output valid.
2. Make the ranking logic reusable and replaceable.
3. Provide the required API capabilities.
4. Handle expected failures explicitly.
5. Make repeated runs deterministic and safe.
6. Keep the implementation simple enough to understand and modify during a live evaluation.

## Part 1 Decisions

### Decision 1: Use the provided 3-Sigma baseline

#### What I chose

I used the provided `baseline_3sigma.py` as the foundation for the Part 1 ranking logic.

The baseline uses gateway-specific historical behaviour to identify unusual values in the recent period. Its main operational signals are:

- `offline_duration_sec`
- `disconnection_cnt`
- `reboot_cnt`

I did not replace the ranking logic with a new machine-learning model.

#### Alternative considered

I could have built a supervised machine-learning model, created a new scoring formula, combined multiple datasets, or substantially modified the baseline.

#### Why I rejected the alternative

The challenge allows the baseline to remain unchanged and allows Software Development participants to concentrate on Part 2. Replacing a working ranking method without evidence that it improves the required outcome would add risk without a clear benefit.

Keeping the baseline also makes the system easier to understand, test, and change during the live evaluation.

### Decision 2: Keep the baseline's operational telemetry signals

#### What I chose

I retained the operational signals used by the baseline:

- `offline_duration_sec`
- `disconnection_cnt`
- `reboot_cnt`

The ranking compares recent gateway behaviour with each gateway's own historical baseline. The score represents the number of recent hours flagged by the 3-Sigma rule.

#### Alternative considered

I could have incorporated additional telemetry fields or created a combined score using different weights, thresholds, or gateway signals.

#### Why I rejected the alternative

The existence of a telemetry field does not prove that it improves the ranking. Adding unvalidated signals would make the ranking harder to explain and could change the required Part 1 behaviour.

### Decision 3: Return exactly 15 gateways per week

#### What I chose

I follow the challenge requirement of returning exactly 15 gateways for every prediction week.

The Part 1 output contains:

```text
15 gateways x 8 weeks = 120 rows
Each week's gateways receive ranks from 1 to 15 with no duplicate rank.
```

#### Alternative considered

I could have introduced a threshold and returned only gateways whose score exceeded that threshold.

#### Why I rejected the alternative

The required `predictions.csv` format does not allow a variable number of gateways. The challenge requires 15 ranked gateways for each week, so the system selects the top 15 available gateways according to the ranking.

### Decision 4: Keep the challenge dataset outside Git

#### What I chose

The challenge dataset remains in the local `data/` directory. The code accepts the data directory as an input instead of depending on a personal machine path.

#### Alternative considered

I could have committed the dataset, copied it into the application, or hard-coded a local Windows path.

#### Why I rejected the alternative

The challenge dataset must not be published or committed. Hard-coded paths would also make the application dependent on one machine. Reading from the expected `data/` directory keeps the project portable and respects the dataset restrictions.

### Decision 5: Make ranking deterministic

#### What I chose

When multiple gateways have the same score, the ranking uses this explicit ordering:

1. `flagged_hours` descending
2. `gateway_id` ascending

This guarantees stable ordering when scores are equal.

#### Alternative considered

I could have relied on DataFrame ordering, used a random tie-break, or used another secondary field such as meter count.

#### Why I rejected the alternative

Relying on implicit ordering can produce different results across environments or library versions. A gateway-ID tie-break is simple, reproducible, and does not require additional assumptions about the data.

## Part 2: Software Development

### Selected area

I selected **Software Development**. I am intentionally focusing Part 2 on making the existing ranking solution usable by another developer through a well-defined API.

The application flow is:

```text
FastAPI
  -> Prediction Service
  -> Ranking Strategy
  -> 3-Sigma Ranking Implementation
  -> Existing Part 1 Baseline
```

### Decision 1: Build a web API

#### What I chose

I built a local FastAPI application with these core capabilities:

- `GET /predictions/{week_start}`
- `GET /gateways/{gateway_id}/why`
- `POST /run`

#### Alternative considered

I could have built a command-line-only interface, dashboard, or graphical user interface.

#### Why I rejected the alternative

The Software Development requirements specify a web API. An API provides a clean interface that can be called, tested, and changed independently of the ranking implementation.

### Decision 2: Separate the API from ranking logic

#### What I chose

The application separates responsibilities across FastAPI routes, the prediction service, the ranking strategy abstraction, and the 3-Sigma implementation. The API does not contain the ranking algorithm directly.

#### Alternative considered

I could have placed the ranking code directly inside the FastAPI route handlers.

#### Why I rejected the alternative

That would tightly couple the API to one ranking implementation. With the current structure, another strategy can be introduced behind the same interface without rewriting the API handlers. This also makes the code easier to test and change.

### Decision 3: Make `/run` generate fresh predictions

#### What I chose

`/run` is an explicit regeneration operation. It:

1. Checks that telemetry data exists.
2. Validates the telemetry input.
3. Reloads the available telemetry.
4. Determines the latest available prediction period.
5. Runs the ranking strategy.
6. Generates the latest predictions.
7. Writes the runtime result to `runtime_predictions.csv`.

#### Alternative considered

I could have served only a pre-generated result, required a week parameter for every run, or loaded the dataset once at application startup.

#### Why I rejected the alternative

The purpose of `/run` is to regenerate rankings when new telemetry becomes available. A startup-only load would become stale while the service was running, so `/run` explicitly re-reads the current data.

### Decision 4: Support new data without restarting the API

#### What I chose

Telemetry is re-read whenever `/run` is called. A new monthly partition can therefore be added under `data/telemetry/month=YYYY-MM/` and used on the next run.

#### Alternative considered

I could have loaded all telemetry into a module-level global when the application started.

#### Why I rejected the alternative

That approach would produce stale rankings when a new month arrived and would fail the live evaluation scenario in which new telemetry is added while the API remains running.

#### Verification

I tested this behaviour by starting the API, adding a new monthly telemetry partition, calling `/run` without restarting the API, and verifying that the prediction period and generated predictions changed.

### Decision 5: Validate telemetry before ranking

#### What I chose

The service validates the telemetry directory, available monthly Parquet files, required columns, non-empty files, usable gateway IDs, and usable timestamps. The ranking layer also validates the columns required by its computation.

#### Alternative considered

I could have allowed the ranking code to fail naturally when it encountered malformed or incomplete input.

#### Why I rejected the alternative

Uncontrolled failures make API errors difficult to understand. Explicit validation fails early with a meaningful message instead of silently producing an incorrect result.

### Decision 6: Handle invalid requests explicitly

#### What I chose

The API validates user input before executing an operation. Invalid dates and empty gateway IDs are rejected, and errors are converted into appropriate HTTP responses.

#### Alternative considered

I could have allowed Python exceptions to propagate directly to the client.

#### Why I rejected the alternative

An API should expose a predictable contract. Clear errors make the service easier to use and prevent invalid input from reaching deeper layers.

### Decision 7: Handle unknown gateways explicitly

#### What I chose

The gateway explanation endpoint checks whether the requested gateway exists in the generated predictions for the requested week. Unknown gateways produce a controlled error.

#### Alternative considered

I could have returned an empty response or allowed an internal exception to propagate.

#### Why I rejected the alternative

An unknown gateway is an expected API input case, not an application crash. A deliberate error gives the caller a clear explanation.

### Decision 8: Use atomic runtime output

#### What I chose

The latest runtime prediction file is written to a temporary file and then replaced with an atomic file replacement operation:

```text
Generate result
    -> Write temporary file
    -> Complete the write successfully
    -> Replace runtime_predictions.csv
```

#### Alternative considered

I could have written directly to `runtime_predictions.csv`.

#### Why I rejected the alternative

If generation or writing failed halfway through, direct replacement could leave an incomplete output. The temporary-file approach keeps the existing result available until the new file is complete.

### Decision 9: Use small synthetic test fixtures

#### What I chose

The test suite primarily uses small synthetic fixtures containing the fields required by the application.

#### Alternative considered

I could have made every test depend on the complete challenge dataset.

#### Why I rejected the alternative

The challenge dataset is large and is not committed to the repository. Synthetic fixtures make tests faster, deterministic, easier to understand, and runnable on a clean machine.

## Testing and Regression Coverage

The implementation includes tests for:

- ranking behaviour;
- deterministic ordering;
- prediction service behaviour;
- API endpoints;
- invalid input;
- error handling;
- end-to-end prediction generation;
- dynamic latest-period detection; and
- newly added telemetry partitions.

The end-to-end path uses synthetic telemetry and does not require the challenge dataset to be committed.

During development, a difference between gateway identifier representations was identified. The implementation and tests were adjusted so that gateway identifiers are handled consistently. The regression fixture is intentionally small and independent of the challenge dataset.

## Runtime and Data Freshness

The application does not assume that March 2026 is permanently the latest month. Instead, `/run` examines the currently available telemetry and determines the latest period dynamically.

The contents of `data/telemetry/` are treated as the current source of available telemetry rather than hard-coding the original eight partitions.

## Limitations

The implementation is intentionally based on the provided 3-Sigma ranking approach. It cannot guarantee that every future failure pattern will be detected. A gateway whose behaviour differs substantially from its historical behaviour may not be identified effectively.

The solution does not claim that the three selected telemetry signals are universally optimal. The challenge does not provide a simple public ground-truth label for "needs a visit", so the Part 1 output should not be presented as a proven fault classifier. Historical field visits are evidence about previous operational decisions, but they are not treated as perfect ground truth.

Incomplete telemetry can also limit the information available to the ranking process. These limitations are documented scope rather than hidden assumptions.

## Future Improvements

If I had another two weeks, I would prioritise these improvements:

1. **Improve `/run` concurrency handling.** Prevent simultaneous runs from interfering with one another or overwriting results unexpectedly.
2. **Expand failure-oriented tests.** Add fixtures for malformed Parquet input, empty partitions, missing columns, unavailable gateway IDs, insufficient history, and repeated runs.
3. **Improve ranking configuration.** Make the ranking implementation selectable through configuration while keeping the API unchanged.
4. **Improve runtime observability.** Record the partitions read, prediction week generated, number of gateways considered, and operation duration.
5. **Benchmark the full dataset.** Measure runtime and memory usage before introducing optimisation.

## Reproducibility

The same input data and ranking implementation produce the same ranking because deterministic tie-breaking is used. The repository does not depend on a personal machine path, and the challenge data is supplied separately in the expected `data/` directory.

The application does not require an online service, API key, or runtime model download to generate predictions.

## Part 1 Validation

The Part 1 pipeline was executed with:

```powershell
python baseline_3sigma.py --data data --out predictions.csv
python validate_submission.py predictions.csv
```

The validation confirmed:

- `predictions.csv` is valid;
- 15 ranked gateways are present for each of 8 weeks;
- the prediction weeks run from `2026-02-02` through `2026-03-23`; and
- the output contains 120 rows.

## Final Decision Summary

| Area | Decision |
| --- | --- |
| Part 1 ranking | Keep the provided 3-Sigma baseline |
| Telemetry signals | Retain the baseline's operational signals |
| Weekly output | Exactly 15 gateways |
| Data handling | Keep challenge data outside Git |
| Tie-breaking | Deterministic score and gateway ID |
| Part 2 area | Software Development |
| API | Local FastAPI web API |
| Ranking architecture | Ranking strategy separated from API |
| `/run` | Regenerate using current telemetry |
| New telemetry | Picked up without an API restart |
| Validation | Explicit input and telemetry validation |
| Testing | Unit, API, end-to-end, and regression tests |
| Runtime output | Atomically replaced |
| Reproducibility | Deterministic ranking and portable paths |

## Final Position

The main decision was to avoid unnecessary complexity and concentrate on making the working ranking solution into software that another developer can run, understand, test, and modify.

The result is a local API that preserves the required Part 1 output while adding:

- clear API boundaries;
- replaceable ranking logic;
- deliberate validation;
- controlled error handling;
- deterministic results;
- automated tests;
- end-to-end and regression coverage; and
- dynamic loading of newly available telemetry.

The design is intentionally sized for this problem rather than for a much larger production system. The priorities are correctness, clarity, testability, and the ability to change the system confidently during the Software Development evaluation.
