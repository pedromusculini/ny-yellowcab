"""Generate extended aggregated metrics from curated or cleaned dataset.

Usage:
    python scripts/aggregate_metrics.py --input data/nyc_taxi_curated.csv --outdir docs/
"""
from __future__ import annotations
import argparse
import os
import pandas as pd


def load_df(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=[c for c in ["tpep_pickup_datetime", "tpep_dropoff_datetime"] if c in open(path).readline()])


def add_temporal(df: pd.DataFrame) -> pd.DataFrame:
    if "tpep_pickup_datetime" in df.columns:
        df["pickup_hour"] = pd.to_datetime(df["tpep_pickup_datetime"]).dt.hour
        df["pickup_day"] = pd.to_datetime(df["tpep_pickup_datetime"]).dt.day
        df["pickup_month"] = pd.to_datetime(df["tpep_pickup_datetime"]).dt.to_period("M").astype(str)
        df["pickup_weekday"] = pd.to_datetime(df["tpep_pickup_datetime"]).dt.day_name()
    return df


def compute(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    outputs = {}
    if {"pickup_hour"}.issubset(df.columns):
        outputs["agg_hourly_fare"] = df.groupby("pickup_hour").agg(
            total_trips=("pickup_hour", "size"),
            total_amount=("total_amount", "sum"),
            avg_fare=("total_amount", "mean")
        ).reset_index()
    if {"pickup_month"}.issubset(df.columns):
        outputs["agg_monthly_fare"] = df.groupby("pickup_month").agg(
            total_trips=("pickup_month", "size"),
            total_amount=("total_amount", "sum"),
            avg_fare=("total_amount", "mean")
        ).reset_index()
    if {"pickup_weekday"}.issubset(df.columns):
        outputs["agg_weekday_fare"] = df.groupby("pickup_weekday").agg(
            total_trips=("pickup_weekday", "size"),
            total_amount=("total_amount", "sum"),
            avg_fare=("total_amount", "mean")
        ).reset_index()
    if {"trip_distance", "total_amount"}.issubset(df.columns):
        # Distance buckets
        bins = [0,1,2,5,10,20,50,100]
        labels = ["0-1","1-2","2-5","5-10","10-20","20-50","50-100"]
        df["distance_bucket"] = pd.cut(df["trip_distance"], bins=bins, labels=labels, right=False)
        outputs["agg_distance_bucket"] = df.groupby("distance_bucket").agg(
            total_trips=("distance_bucket", "size"),
            avg_fare=("total_amount", "mean"),
            median_fare=("total_amount", "median")
        ).reset_index()
    return outputs


def write_outputs(outputs: dict[str, pd.DataFrame], outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    for name, df in outputs.items():
        df.to_csv(os.path.join(outdir, f"{name}.csv"), index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--outdir", default="docs/")
    args = parser.parse_args()

    df = load_df(args.input)
    df = add_temporal(df)
    outputs = compute(df)
    write_outputs(outputs, args.outdir)
    print(f"Wrote {len(outputs)} aggregate CSV files to {args.outdir}")


if __name__ == "__main__":
    main()
