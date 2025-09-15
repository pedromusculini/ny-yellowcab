"""Data curation script for NYC Taxi dataset.

Steps:
1. Load raw or intermediate cleaned CSV
2. Apply standardized cleaning rules
3. Derive temporal and spatial features
4. Export curated dataset and metrics

Usage (example):
    python scripts/clean_curate.py --input data/nyc_taxi_clean.csv --output data/nyc_taxi_curated.csv
"""
from __future__ import annotations
import argparse
import os
import sys
import pandas as pd
from typing import Tuple

DEFAULT_MAX_FARE = 1000.0
DEFAULT_MIN_DISTANCE = 0.05
DEFAULT_MAX_DISTANCE = 100.0

NYC_BOUNDS = {
    "lat_min": 40.4,
    "lat_max": 41.1,
    "lon_min": -74.5,
    "lon_max": -72.9,
}

TIME_COLUMNS = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]


def load_dataset(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")
    df = pd.read_csv(path)
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Deduplicate column names and unify casing for known variants
    df = df.loc[:, ~df.columns.duplicated()]
    rename_map = {"RatecodeID": "RateCodeID"}
    df = df.rename(columns=rename_map)
    return df


def parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    for col in TIME_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def filter_bounds(df: pd.DataFrame) -> pd.DataFrame:
    # Coordinate filtering (pickup & dropoff if available)
    for prefix in ["pickup", "dropoff"]:
        lat_col = f"{prefix}_latitude"
        lon_col = f"{prefix}_longitude"
        if lat_col in df.columns and lon_col in df.columns:
            df = df[
                (df[lat_col].between(NYC_BOUNDS["lat_min"], NYC_BOUNDS["lat_max"]))
                & (df[lon_col].between(NYC_BOUNDS["lon_min"], NYC_BOUNDS["lon_max"]))
            ]
    return df


def filter_numeric(df: pd.DataFrame,
                   max_fare: float = DEFAULT_MAX_FARE,
                   min_distance: float = DEFAULT_MIN_DISTANCE,
                   max_distance: float = DEFAULT_MAX_DISTANCE) -> pd.DataFrame:
    if "total_amount" in df.columns:
        df = df[(df["total_amount"] > 0) & (df["total_amount"] <= max_fare)]
    if "trip_distance" in df.columns:
        df = df[(df["trip_distance"] >= min_distance) & (df["trip_distance"] <= max_distance)]
    return df


def derive_features(df: pd.DataFrame) -> pd.DataFrame:
    if "tpep_pickup_datetime" in df.columns:
        df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
        df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
        df["pickup_month"] = df["tpep_pickup_datetime"].dt.to_period("M").astype(str)
        df["pickup_weekday"] = df["tpep_pickup_datetime"].dt.day_name()
    if "tpep_pickup_datetime" in df.columns and "tpep_dropoff_datetime" in df.columns:
        duration = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60.0
        df["trip_duration_min"] = duration
        df = df[(df["trip_duration_min"] >= 0) & (df["trip_duration_min"] <= 720)]  # <= 12h
    return df


def compute_metrics(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    hourly = pd.DataFrame()
    if "pickup_hour" in df.columns:
        hourly = df.groupby("pickup_hour").size().reset_index(name="total_trips")
    monthly = pd.DataFrame()
    if "pickup_month" in df.columns and "total_amount" in df.columns:
        monthly = df.groupby("pickup_month")["total_amount"].sum().reset_index(name="total_amount")
    fare_stats = pd.DataFrame()
    if "total_amount" in df.columns:
        fare_stats = df["total_amount"].describe().to_frame(name="value")
    return hourly, monthly, fare_stats


def curate(path_in: str, path_out: str, artifacts_dir: str) -> None:
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    os.makedirs(artifacts_dir, exist_ok=True)
    df = load_dataset(path_in)
    original_rows = len(df)
    df = normalize_columns(df)
    df = parse_datetimes(df)
    df = filter_bounds(df)
    df = filter_numeric(df)
    df = derive_features(df)

    curated_rows = len(df)
    reduction_pct = 100 * (1 - curated_rows / max(original_rows, 1))

    hourly, monthly, fare_stats = compute_metrics(df)

    df.to_csv(path_out, index=False)
    hourly.to_csv(os.path.join(artifacts_dir, "hourly_trips.csv"), index=False)
    monthly.to_csv(os.path.join(artifacts_dir, "monthly_revenue.csv"), index=False)
    fare_stats.to_csv(os.path.join(artifacts_dir, "fare_stats.csv"))

    summary_path = os.path.join(artifacts_dir, "curation_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"Original rows: {original_rows}\n")
        f.write(f"Curated rows: {curated_rows}\n")
        f.write(f"Reduction %: {reduction_pct:.2f}\n")
        if not hourly.empty:
            peak = hourly.sort_values("total_trips", ascending=False).head(1)
            f.write(f"Peak hour: {int(peak.iloc[0]['pickup_hour'])} with {int(peak.iloc[0]['total_trips'])} trips\n")

    print(f"Curated dataset saved to {path_out}")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Curate NYC Taxi dataset")
    parser.add_argument("--input", required=True, help="Path to input cleaned CSV")
    parser.add_argument("--output", required=True, help="Path to output curated CSV")
    parser.add_argument("--artifacts", default="docs/", help="Directory to store derived artifacts")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    curate(args.input, args.output, args.artifacts)


if __name__ == "__main__":
    main()
