"""Split large CSV into smaller parts for BI tools (e.g., Power BI incremental loads).

Usage:
    python scripts/split_dataset.py --input data/nyc_taxi_curated.csv --rows 2000000 --outdir data/splits/
"""
from __future__ import annotations
import argparse
import os
import pandas as pd

def split_csv(path: str, rows: int, outdir: str) -> list[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    os.makedirs(outdir, exist_ok=True)
    parts = []
    i = 0
    for chunk in pd.read_csv(path, chunksize=rows):
        i += 1
        out = os.path.join(outdir, f"part_{i:02d}.csv")
        chunk.to_csv(out, index=False)
        parts.append(out)
    return parts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--rows", type=int, default=2_000_000)
    parser.add_argument("--outdir", default="data/splits/")
    args = parser.parse_args()

    parts = split_csv(args.input, args.rows, args.outdir)
    print(f"Generated {len(parts)} files:")
    for p in parts:
        print(" -", p)

if __name__ == "__main__":
    main()
