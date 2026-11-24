"""ETL: load the Instacart CSVs, validate them, and build a SQLite database.

Usage:
    python -m src.build_db --data-dir data/raw --db instacart.db
    python -m src.build_db --data-dir data/sample --db sample.db
"""
import argparse
import sqlite3
from pathlib import Path

import pandas as pd

# Table name -> columns that must exist in the CSV
REQUIRED_COLUMNS = {
    "aisles": ["aisle_id", "aisle"],
    "departments": ["department_id", "department"],
    "products": ["product_id", "product_name", "aisle_id", "department_id"],
    "orders": [
        "order_id", "user_id", "eval_set", "order_number",
        "order_dow", "order_hour_of_day", "days_since_prior_order",
    ],
    "order_products__prior": ["order_id", "product_id", "add_to_cart_order", "reordered"],
}

# Table -> (column that must be unique)
UNIQUE_KEYS = {
    "aisles": "aisle_id",
    "departments": "department_id",
    "products": "product_id",
    "orders": "order_id",
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_op_order ON order_products__prior(order_id)",
    "CREATE INDEX IF NOT EXISTS idx_op_product ON order_products__prior(product_id)",
    "CREATE INDEX IF NOT EXISTS idx_products_dept ON products(department_id)",
]


class DataValidationError(ValueError):
    """Raised when an input CSV does not look like the Instacart data."""


def validate_table(name: str, df: pd.DataFrame) -> None:
    """Check required columns exist, and that primary keys are unique and non-null."""
    missing = [c for c in REQUIRED_COLUMNS[name] if c not in df.columns]
    if missing:
        raise DataValidationError(f"{name}: missing columns {missing}")
    key = UNIQUE_KEYS.get(name)
    if key:
        if df[key].isna().any():
            raise DataValidationError(f"{name}: null values in {key}")
        if df[key].duplicated().any():
            raise DataValidationError(f"{name}: duplicate values in {key}")


def build_database(data_dir, db_path, chunksize: int = 500_000) -> dict:
    """Build the SQLite database. Returns {table_name: row_count}."""
    data_dir = Path(data_dir)
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()  # rebuild from scratch so runs are repeatable

    counts = {}
    conn = sqlite3.connect(db_path)
    try:
        # Small tables: load whole, validate, write.
        for name in ["aisles", "departments", "products", "orders"]:
            df = pd.read_csv(data_dir / f"{name}.csv")
            validate_table(name, df)
            df.to_sql(name, conn, index=False)
            counts[name] = len(df)

        # The big table (30M+ rows in the full dataset): stream in chunks.
        total = 0
        path = data_dir / "order_products__prior.csv"
        for i, chunk in enumerate(pd.read_csv(path, chunksize=chunksize)):
            if i == 0:
                validate_table("order_products__prior", chunk)
            chunk.to_sql("order_products__prior", conn, index=False, if_exists="append")
            total += len(chunk)
        counts["order_products__prior"] = total

        for stmt in INDEXES:
            conn.execute(stmt)
        conn.commit()
    finally:
        conn.close()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SQLite DB from Instacart CSVs")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--db", default="instacart.db")
    args = parser.parse_args()

    counts = build_database(args.data_dir, args.db)
    for table, n in counts.items():
        print(f"{table}: {n:,} rows")
    print(f"Database written to {args.db}")


if __name__ == "__main__":
    main()
