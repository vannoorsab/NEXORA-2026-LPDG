from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "gateway_id",
        "ts_utc",
}


def validate_telemetry(data_dir: Path) -> None:
        """
        Validate the structure of every telemetry partition.

        Raises:
                FileNotFoundError: when telemetry data is missing.
                ValueError: when required columns or usable values are missing.
        """

        telemetry_dir = data_dir / "telemetry"

        if not telemetry_dir.exists():
                raise FileNotFoundError(
                        f"Telemetry directory does not exist: {telemetry_dir}"
                )

        parquet_files = sorted(
                telemetry_dir.glob("month=*/part-*.parquet")
        )

        if not parquet_files:
                raise FileNotFoundError(
                        f"No telemetry parquet files found under: {telemetry_dir}"
                )

        for parquet_file in parquet_files:
                try:
                        frame = pd.read_parquet(
                                parquet_file,
                                columns=list(REQUIRED_COLUMNS),
                        )
                except Exception as exc:
                        message = str(exc)

                        if "Column" in message or "column" in message:
                                raise ValueError(
                                        f"Telemetry file '{parquet_file.name}' is missing "
                                        f"one or more required columns: "
                                        f"{', '.join(sorted(REQUIRED_COLUMNS))}"
                                ) from exc

                        raise ValueError(
                                f"Could not read telemetry file '{parquet_file}'."
                        ) from exc

                missing = REQUIRED_COLUMNS - set(frame.columns)

                if missing:
                        raise ValueError(
                                f"Telemetry is missing required column(s): "
                                f"{', '.join(sorted(missing))}"
                        )

                if frame.empty:
                        raise ValueError(
                                f"Telemetry file '{parquet_file}' contains no rows."
                        )

                if frame["gateway_id"].isna().all():
                        raise ValueError(
                                f"Telemetry file '{parquet_file}' contains no usable "
                                "gateway_id values."
                        )

                if frame["ts_utc"].isna().all():
                        raise ValueError(
                                f"Telemetry file '{parquet_file}' contains no usable "
                                "ts_utc values."
                        )