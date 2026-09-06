# NEXORA 2026 — Part 1 Decisions

## Overview

For Part 1, the objective is to produce a weekly ranked list of 15 gateways that should be visited.

The solution must generate:

- 15 gateways per week
- 8 weeks
- 120 total rows
- columns: `week_start`, `rank`, `gateway_id`, `score`, `reason`

The provided `baseline_3sigma.py` was used as the starting point.

---

## Decision 1 — Use the provided 3-Sigma baseline

### Choice

I decided to use the provided `baseline_3sigma.py` as the starting point rather than building a machine-learning model.

The baseline already produces a valid `predictions.csv` with 15 ranked gateways for each of the required 8 weeks.

### Alternatives considered

I considered building a custom machine-learning model using the historical telemetry and field-visit data.

### Why I did not choose it

The challenge explicitly states that machine learning is not required and that the provided baseline is a working solution.

Since my selected Part 2 areas are Software Development and DevOps, I decided to spend the available time on engineering quality, reproducibility, automation, testing and deployment rather than training a new model.

---

## Decision 2 — Use telemetry signals related to gateway instability

### Choice

The baseline uses:

- `offline_duration_sec`
- `disconnection_cnt`
- `reboot_cnt`

These signals were retained because they directly represent gateway availability and instability.

### Alternatives considered

I considered using every available telemetry feature, including CPU, memory and network-quality indicators.

### Why I did not choose it

Using every available feature without proving that it improves the ranking would add complexity without necessarily improving the solution.

The baseline provides a simple and explainable approach that is easier to reproduce and maintain.

---

## Decision 3 — Keep the hard limit of 15 gateways per week

### Choice

The output contains exactly 15 gateways for each required week.

### Alternatives considered

I could have generated a variable number of recommendations depending on the severity of the score.

For example, a week could contain 8 recommendations if only 8 gateways appeared highly problematic.

### Why I did not choose it

The challenge explicitly defines 15 visits as a hard limit.

Therefore, the system must always return exactly 15 ranked gateways per week.

---

## Decision 4 — Keep the prediction output simple and reproducible

### Choice

The solution generates a deterministic `predictions.csv` file from the provided data.

The output follows the exact required five-column format:

`week_start, rank, gateway_id, score, reason`

### Alternatives considered

I considered creating a more complex interactive application for Part 1.

### Why I did not choose it

Part 1 is primarily an operational baseline exercise. The important requirement is that the prediction pipeline works reliably and produces the required output.

Additional UI complexity would not improve the required submission format.

---

## Decision 5 — Select Software Development and DevOps for Part 2

### Choice

I selected:

1. Software Development
2. DevOps

### Why

I want to focus on building a reliable, maintainable and reproducible engineering solution rather than focusing primarily on machine learning.

Software Development allows me to demonstrate:

- clean architecture
- reusable code
- validation
- testing
- error handling
- maintainability

DevOps allows me to demonstrate:

- Docker
- reproducible execution
- CI/CD
- automated testing
- environment consistency
- deployment readiness

These areas allow me to build on the working Part 1 baseline and spend more effort on engineering quality in Part 2.

---

# What I would improve next

The provided baseline is intentionally simple.

A possible future improvement would be to combine the baseline signals with historical field-visit outcomes and meter-read performance.

However, I would only make such a change after validating that it improves the ranking on historical data without introducing future-data leakage.

For Part 1, reliability and correctness are more important than adding complexity without evidence.

---

# Summary

The main principle behind these decisions is:

> Start with the working baseline, keep the solution explainable and reproducible, and spend engineering effort where it provides the most value.

For Part 2, that means focusing on Software Development and DevOps.