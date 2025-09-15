# Makefile shortcuts

PYTHON=python
CURATED=data/nyc_taxi_curated.csv
CLEAN=data/nyc_taxi_clean.csv
ARTIFACTS=docs/

.PHONY: help setup curate aggregate validate test split powerbi-dims all

help:
	@echo "Available targets:"
	@echo "  setup        - install dependencies (dev)"
	@echo "  curate       - run curation script (requires $(CLEAN))"
	@echo "  aggregate    - run aggregate metrics on curated dataset"
	@echo "  validate     - run validation script"
	@echo "  test         - run pytest"
	@echo "  split        - split curated dataset into parts"
	@echo "  powerbi-dims - generate Power BI dimension CSVs (data/dim/)"
	@echo "  all          - curate, aggregate, validate, test"

setup:
	pip install -r requirements.txt
	pip install -e .[dev] || true

curate:
	@if [ -f $(CLEAN) ]; then \
		$(PYTHON) scripts/clean_curate.py --input $(CLEAN) --output $(CURATED) --artifacts $(ARTIFACTS); \
	else \
		echo "Missing $(CLEAN)."; \
	fi

aggregate:
	@if [ -f $(CURATED) ]; then \
		$(PYTHON) scripts/aggregate_metrics.py --input $(CURATED) --outdir $(ARTIFACTS); \
	else \
		echo "Missing $(CURATED)."; \
	fi

validate:
	@if [ -f $(CURATED) ]; then \
		$(PYTHON) scripts/validate_curated.py --input $(CURATED); \
	else \
		echo "Missing $(CURATED)."; \
	fi

test:
	pytest -q || true

split:
	@if [ -f $(CURATED) ]; then \
		$(PYTHON) scripts/split_dataset.py --input $(CURATED) --rows 2000000 --outdir data/splits/; \
	else \
		echo "Missing $(CURATED)."; \
	fi

powerbi-dims:
	@if [ -f docs/monthly_revenue.csv ]; then \
		$(PYTHON) scripts/export_powerbi_dims.py --monthly docs/monthly_revenue.csv --outdir data/dim/; \
	else \
		echo "Missing docs/monthly_revenue.csv."; \
	fi

all: curate aggregate validate test
