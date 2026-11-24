# Retail Demand Pipeline

A small, tested data pipeline that turns the Instacart Market Basket data (3.4M orders, 30M+ order lines) into a SQLite database, answers demand questions in SQL, and produces a product **replenishment priority** report from the command line.

Built to practice the Python + SQL workflow used in supply-chain analytics.

## What it does
```
CSV files ──► build_db.py ──► SQLite ──► sql/*.sql ──► features.py (Pandas) ──► report.py (CLI / CSV)
 (validated,     (chunked load,          JOINs, CTEs,     priority score
  schema check)   indexes)               window functions
```

- **ETL** (`src/build_db.py`): validates columns and primary keys, streams the 30M-row table in chunks, builds indexes.
- **SQL** (`sql/`): multi-table JOINs, CTEs, `RANK()`, `ROW_NUMBER() OVER (PARTITION BY ...)`, `SUM() OVER ()`.
- **Features** (`src/features.py`): product reorder rate and a replenishment priority score.
- **CLI** (`src/report.py`): filter by department, export to CSV.
- **Tests** (`tests/`): pytest on a handcrafted sample whose expected numbers are checked by hand; runs in GitHub Actions.

## Quick start (no download needed)
```bash
pip install -r requirements.txt
pytest -q
python -m src.build_db --data-dir data/sample --db sample.db
python -m src.report --db sample.db --top 5
```

## Run on the real data
1. Download the Instacart dataset from Kaggle and put the CSVs in `data/raw/` (not committed).
2. ```bash
   python -m src.build_db --data-dir data/raw --db instacart.db
   python -m src.report --db instacart.db --department produce --top 20 --out reports/produce.csv
   ```

## Priority score
`priority_score = reorder_rate * log(1 + times_ordered)`, scaled so the top product = 100.
It is a transparent heuristic (frequently bought AND repeatedly bought), **not** a trained model or forecast.

## Limitations
The dataset has no dates, prices or stock levels, so this measures demand and repeat-purchase behaviour, not inventory or revenue. `order_dow` is 0-6 with no documented start day.

## Next steps
Reorder-prediction model vs. a baseline, BigQuery version of the SQL, dashboard.
