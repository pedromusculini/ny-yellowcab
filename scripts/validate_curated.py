from __future__ import annotations
import argparse
import os
import sys
import pandas as pd


def validate(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    df = pd.read_csv(path, nrows=100000)

    # Basic rules
    if "trip_distance" in df.columns:
        assert (df["trip_distance"] >= 0.05).all(), "Found trip_distance < 0.05"
        assert (df["trip_distance"] <= 100).all(), "Found trip_distance > 100"
    if "total_amount" in df.columns:
        assert (df["total_amount"] > 0).all(), "Found non-positive total_amount"
        assert (df["total_amount"] <= 1000).all(), "Found total_amount > 1000"

    # Temporal columns
    if "tpep_pickup_datetime" in df.columns:
        pd.to_datetime(df["tpep_pickup_datetime"], errors="raise")

    print("Validation OK (sample)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()
    validate(args.input)


if __name__ == "__main__":
    main()
