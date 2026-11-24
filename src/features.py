"""Run the SQL files and build the Pandas feature table."""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def run_sql(conn: sqlite3.Connection, name: str, params: dict | None = None) -> pd.DataFrame:
    """Run sql/<name>.sql with named parameters and return a DataFrame."""
    query = (SQL_DIR / f"{name}.sql").read_text()
    return pd.read_sql_query(query, conn, params=params or {})


def product_features(conn: sqlite3.Connection, department: str | None = None) -> pd.DataFrame:
    """Product table with a replenishment priority score.

    priority_score (0-100) = reorder_rate * log(1 + times_ordered), rescaled so the
    top product is 100. It is a simple HEURISTIC: products that are both bought often
    and bought repeatedly are the ones a store most wants to keep in stock.
    It is not a trained model and not a forecast.
    """
    df = run_sql(conn, "product_stats", {"department": department})
    if df.empty:
        df["priority_score"] = []
        return df

    raw = df["reorder_rate"] * np.log1p(df["times_ordered"])
    top = raw.max()
    df["priority_score"] = (100 * raw / top).round(1) if top > 0 else 0.0
    return df.sort_values(
        ["priority_score", "times_ordered"], ascending=False
    ).reset_index(drop=True)
