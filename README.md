# ny-yellowcab
 Production-grade data curation and analytics for NYC Yellow Taxi trips, with reproducible pipelines, validated metrics, and a ready-to-open Power BI report.
NYC Yellow Taxi Analytics — Curated Pipeline, Aggregations, and Power BI

This project delivers a professional, reproducible data pipeline for NYC Yellow Taxi trips, turning large, messy CSVs into clean, analysis-ready datasets with validated metrics and a polished Power BI report. It’s designed to showcase end‑to‑end capability across data engineering and analytics, with transparent rules, automation, and documentation suitable for international audiences.

What’s included

Reproducible curation: Chunked processing, strict quality rules (NYC geo-bounds, distance range, <= 12h duration, fare cap), and standardized temporal features.
Aggregated analytics: Hourly trips, monthly revenue, weekday patterns, and distance buckets exported as CSVs under docs/.
Validation and tests: Rule checks + pytest ensure quality and prevent regressions; CI workflow keeps contributions safe.
Geospatial and visuals: Folium map and Plotly exports for quick storytelling.
Power BI report: Ready-to-open file with DAX measures and generated dimension tables (Date, Hour, Weekday, Distance Bucket).
Developer UX: Makefile shortcuts, pre-commit hooks, EditorConfig, MIT license, and CONTRIBUTING guide for smooth collaboration.
Cloud exploration: Optional Kaggle notebook for scalable analysis in a hosted environment.
Key artifacts

Power BI: ny-yellowcab.pbix and dax_measures.txt
Aggregates: docs/hourly_trips.csv, docs/monthly_revenue.csv, expensive_routes.csv
Dimensions: data/dim/dim_date.csv, dim_hour.csv, dim_weekday.csv, dim_distance_bucket.csv
Pipeline scripts: scripts/clean_curate.py, scripts/aggregate_metrics.py, scripts/split_dataset.py, scripts/validate_curated.py, export_powerbi_dims.py
Visuals: docs/nyc_pickup_map.html, plotly_histogram.html
Highlights

Clean, validated, and explainable data pipeline
Ready-to-use Power BI dashboard with robust DAX patterns
CI-backed, contribution-friendly repository (tests, hooks, standards)
Clear documentation and reproducible steps for recruiters and collaborators
Who is this for

Data analysts and data engineers who want a credible, production‑style portfolio asset
Recruiters and stakeholders reviewing analytics fluency end‑to‑end
Anyone exploring curated, large-scale mobility data with a focused business narrative
