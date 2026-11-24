from pathlib import Path

import pytest

from src.build_db import build_database

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"


@pytest.fixture()
def db_path(tmp_path):
    path = tmp_path / "test.db"
    build_database(SAMPLE_DIR, path)
    return path
