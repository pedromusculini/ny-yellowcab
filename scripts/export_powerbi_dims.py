"""Generate Power BI dimension tables (CSV) from project artifacts.

This script creates the following files under data/dim/:
  - dim_date.csv: Daily calendar between min and max month found in docs/monthly_revenue.csv
  - dim_hour.csv: Hours 0..23 with labels
  - dim_weekday.csv: Monday..Sunday with sort order and weekend flag
  - dim_distance_bucket.csv: Distance buckets aligned with aggregate_metrics.py

Usage:
    python scripts/export_powerbi_dims.py \
        --monthly docs/monthly_revenue.csv \
        --outdir data/dim/

Optional overrides:
    --start 2015-01-01  --end 2016-03-31

Notes:
 - Uses only Python standard library (no pandas) for portability.
 - Date table uses Monday=1 .. Sunday=7 for WeekdayNum (compatible with DAX WEEKDAY(,2)).
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import calendar


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Export Power BI dimension CSVs")
    p.add_argument("--monthly", default="docs/monthly_revenue.csv", help="Path to monthly revenue CSV with pickup_month column (YYYY-MM)")
    p.add_argument("--outdir", default="data/dim/", help="Output directory for dimension CSVs")
    p.add_argument("--start", help="Override start date (YYYY-MM-DD)")
    p.add_argument("--end", help="Override end date (YYYY-MM-DD)")
    return p.parse_args(argv)


def ensure_outdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def month_str_to_date_bounds(ym: str) -> tuple[date, date]:
    year, month = map(int, ym.split("-"))
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    return start, end


def detect_date_range(monthly_csv: Path) -> tuple[date, date]:
    if not monthly_csv.exists():
        raise FileNotFoundError(f"Monthly CSV not found: {monthly_csv}")
    months: list[str] = []
    with monthly_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if "pickup_month" not in reader.fieldnames:
            raise ValueError("Expected 'pickup_month' column in monthly CSV")
        for row in reader:
            m = row.get("pickup_month", "").strip()
            if m:
                months.append(m)
    if not months:
        raise ValueError("No rows found in monthly CSV")
    min_m = min(months)
    max_m = max(months)
    s, _ = month_str_to_date_bounds(min_m)
    _, e = month_str_to_date_bounds(max_m)
    return s, e


def daterange(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur = cur + timedelta(days=1)


def write_dim_date(outdir: Path, start: date, end: date) -> Path:
    path = outdir / "dim_date.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Date",  # YYYY-MM-DD
            "Year",
            "MonthNum",
            "MonthName",
            "YearMonth",
            "WeekdayNum",  # Monday=1 .. Sunday=7
            "WeekdayName",
            "IsWeekend",   # 1 if Sat/Sun
            "DayType",     # Weekend/Weekday
        ])
        for d in daterange(start, end):
            weekday_mon1 = ((d.weekday()) + 1)  # Monday=1 .. Sunday=7
            is_weekend = 1 if weekday_mon1 >= 6 else 0
            w.writerow([
                d.isoformat(),
                d.year,
                d.month,
                d.strftime("%b"),
                d.strftime("%Y-%m"),
                weekday_mon1,
                d.strftime("%a"),
                is_weekend,
                "Weekend" if is_weekend else "Weekday",
            ])
    return path


def write_dim_hour(outdir: Path) -> Path:
    path = outdir / "dim_hour.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Hour", "HourLabel"])
        for h in range(24):
            w.writerow([h, f"{h:02d}:00"])
    return path


def write_dim_weekday(outdir: Path) -> Path:
    path = outdir / "dim_weekday.csv"
    # Monday=1..Sunday=7 to align with DAX WEEKDAY(,2)
    names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["WeekdayNum", "WeekdayName", "IsWeekend", "SortOrder"])
        for n in range(1, 8):
            is_weekend = 1 if n >= 6 else 0
            w.writerow([n, names[n], is_weekend, n])
    return path


def write_dim_distance_bucket(outdir: Path) -> Path:
    path = outdir / "dim_distance_bucket.csv"
    # Buckets aligned with scripts/aggregate_metrics.py
    bins = [(0,1),(1,2),(2,5),(5,10),(10,20),(20,50),(50,100)]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["BucketMinIncl", "BucketMaxExcl", "Label"])
        for lo, hi in bins:
            w.writerow([lo, hi, f"{lo}-{hi}"])
    return path


def main(argv=None):
    args = parse_args(argv)
    outdir = Path(args.outdir)
    ensure_outdir(outdir)

    if args.start and args.end:
        start = datetime.strptime(args.start, "%Y-%m-%d").date()
        end = datetime.strptime(args.end, "%Y-%m-%d").date()
    else:
        start, end = detect_date_range(Path(args.monthly))

    p1 = write_dim_date(outdir, start, end)
    p2 = write_dim_hour(outdir)
    p3 = write_dim_weekday(outdir)
    p4 = write_dim_distance_bucket(outdir)

    print("Exported dimension CSVs:")
    for p in (p1, p2, p3, p4):
        print(" -", p)


if __name__ == "__main__":
    main()
