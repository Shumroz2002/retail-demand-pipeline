"""Command-line report tool.

Examples:
    python -m src.report --db instacart.db
    python -m src.report --db instacart.db --department produce --top 20
    python -m src.report --db instacart.db --out reports/produce.csv --department produce
"""
import argparse
import sqlite3

from src.features import product_features, run_sql


def main() -> None:
    parser = argparse.ArgumentParser(description="Retail demand report")
    parser.add_argument("--db", default="instacart.db", help="SQLite database path")
    parser.add_argument("--department", help="Only this department (e.g. produce)")
    parser.add_argument("--top", type=int, default=10, help="Rows to show (default 10)")
    parser.add_argument("--out", help="Optionally save the full table to this CSV")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        print("\n=== Departments by demand ===")
        print(run_sql(conn, "department_summary").to_string(index=False))

        feats = product_features(conn, args.department)
        label = args.department or "all departments"
        print(f"\n=== Top {args.top} products to keep stocked ({label}) ===")
        cols = ["product_name", "department", "times_ordered", "reorder_rate", "priority_score"]
        print(feats[cols].head(args.top).to_string(index=False))

        if args.out:
            feats.to_csv(args.out, index=False)
            print(f"\nSaved {len(feats):,} rows to {args.out}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
