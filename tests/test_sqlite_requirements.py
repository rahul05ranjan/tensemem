"""The platform's bundled SQLite must meet the requirements in ADR 0003."""

import sqlite3

import pytest


def test_sqlite_is_at_least_3_35() -> None:
    assert sqlite3.sqlite_version_info >= (3, 35, 0), sqlite3.sqlite_version


def test_fts5_is_available() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE VIRTUAL TABLE docs USING fts5(text, tokenize='porter unicode61')")
        conn.execute("INSERT INTO docs(text) VALUES ('I moved to Bangalore')")
        rows = conn.execute("SELECT text FROM docs WHERE docs MATCH 'moving'").fetchall()
    finally:
        conn.close()
    assert rows == [("I moved to Bangalore",)]


def test_partial_unique_index_enforces_one_active_row_per_slot() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE facts (slot_key TEXT NOT NULL, status TEXT NOT NULL)")
        conn.execute(
            "CREATE UNIQUE INDEX ux_active_slot ON facts(slot_key) WHERE status = 'ACTIVE'"
        )
        conn.execute("INSERT INTO facts VALUES ('user:lives_in', 'SUPERSEDED')")
        conn.execute("INSERT INTO facts VALUES ('user:lives_in', 'ACTIVE')")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO facts VALUES ('user:lives_in', 'ACTIVE')")
    finally:
        conn.close()


def test_returning_clause_is_supported() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, status TEXT NOT NULL)")
        row = conn.execute("INSERT INTO jobs(status) VALUES ('QUEUED') RETURNING id").fetchone()
    finally:
        conn.close()
    assert row == (1,)
