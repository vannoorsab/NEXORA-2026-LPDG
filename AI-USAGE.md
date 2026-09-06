# NEXORA 2026 — AI Usage

## How AI tools were used

AI tools were used as an engineering assistant during the development of the NEXORA 2026 challenge solution.

AI assistance was used for:

- understanding the challenge requirements
- breaking the problem into smaller engineering tasks
- explaining the provided baseline
- helping write and debug Python analysis scripts
- identifying data-format issues
- suggesting project structure
- reviewing code for possible errors
- helping prepare documentation
- explaining error messages and debugging approaches

The final commands were executed locally and the generated outputs were checked manually.

---

## Example of debugging with AI

One useful example was the gateway ID mismatch between the field-visit data and telemetry data.

The field-visit dataset contained gateway IDs in a format such as:

`06:B1:62:DC:93:E3`

while telemetry used:

`06B162DC93E3`

Initially, this caused the analysis to report zero matching gateways.

The issue was identified during debugging and the IDs were normalized by removing the colon separators and converting them to a consistent uppercase representation.

After normalization, all 147 gateways from the confirmed field visits were found in the telemetry dataset.

---

## One thing AI got wrong

During the analysis, an AI-generated script initially reported:

`Confirmed/fixed visits: 223`

but then displayed reason counts that summed to all 642 field visits instead of 223.

This was incorrect.

I noticed the inconsistency by manually checking the totals.

The script was then corrected so that the reason analysis was performed only on rows where:

`outcome == "Fehler behoben"`

After correction, the reason counts summed correctly to 223 confirmed/fixed visits.

This was an important reminder that AI-generated code and analysis must be tested against the actual data rather than accepted without verification.

---

## Human verification

AI was used to accelerate development and debugging, but I verified the important results by running the code locally.

For example:

- `baseline_3sigma.py` was executed locally.
- `predictions.csv` was generated.
- `validate_submission.py` was executed.
- The validation confirmed 120 rows covering 15 gateways for each of the 8 required weeks.
- Data-analysis scripts were also executed locally and their outputs were inspected.

AI assistance was therefore treated as a development tool rather than as a replacement for testing and engineering judgement.