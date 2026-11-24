import shutil
import sqlite3

import pandas as pd
import pytest

from src.build_db import DataValidationError, build_database, validate_table
from src.features import product_features, run_sql
from tests.conftest import SAMPLE_DIR


def test_row_counts(tmp_path):
    counts = build_database(SAMPLE_DIR, tmp_path / "a.db")
    assert counts["products"] == 6
    assert counts["orders"] == 6
    assert counts["order_products__prior"] == 16


def test_validate_missing_column():
    df = pd.DataFrame({"aisle_id": [1]})  # no 'aisle' column
    with pytest.raises(DataValidationError):
        validate_table("aisles", df)


def test_validate_duplicate_key():
    df = pd.DataFrame({"aisle_id": [1, 1], "aisle": ["a", "b"]})
    with pytest.raises(DataValidationError):
        validate_table("aisles", df)


def test_missing_file_fails(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileNotFoundError):
        build_database(empty, tmp_path / "b.db")


def test_chunked_load_matches(tmp_path):
    counts = build_database(SAMPLE_DIR, tmp_path / "c.db", chunksize=3)
    assert counts["order_products__prior"] == 16


def test_banana_stats(db_path):
    conn = sqlite3.connect(db_path)
    df = product_features(conn)
    banana = df[df["product_name"] == "Banana"].iloc[0]
    assert banana["times_ordered"] == 5
    assert banana["times_reordered"] == 3
    assert banana["reorder_rate"] == pytest.approx(0.6)


def test_department_filter(db_path):
    conn = sqlite3.connect(db_path)
    df = product_features(conn, "bakery")
    assert set(df["department"]) == {"bakery"}
    assert len(df) == 2


def test_priority_score_range_and_order(db_path):
    conn = sqlite3.connect(db_path)
    df = product_features(conn)
    assert df["priority_score"].max() == 100.0
    assert df["priority_score"].min() >= 0
    assert df.iloc[0]["product_name"] == "Banana"
    assert df["priority_score"].is_monotonic_decreasing


def test_unknown_department_is_empty(db_path):
    conn = sqlite3.connect(db_path)
    assert product_features(conn, "nonexistent").empty


def test_department_summary_window_functions(db_path):
    conn = sqlite3.connect(db_path)
    df = run_sql(conn, "department_summary")
    assert list(df["department"]) == ["produce", "dairy eggs", "bakery"]
    assert list(df["demand_rank"]) == [1, 2, 3]
    assert df["pct_of_all_lines"].sum() == pytest.approx(100.0, abs=0.1)


def test_top_products_per_department(db_path):
    conn = sqlite3.connect(db_path)
    df = run_sql(conn, "top_products_per_department", {"n": 1})
    top = dict(zip(df["department"], df["product_name"]))
    assert top["produce"] == "Banana"
    assert top["dairy eggs"] == "Whole Milk"


def test_demand_by_hour(db_path):
    conn = sqlite3.connect(db_path)
    df = run_sql(conn, "demand_by_hour")
    assert df["item_lines"].sum() == 16
    assert df["orders"].sum() == 6
