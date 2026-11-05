"""Privacy-conscious SQLite telemetry for test-run data validation.

Only operational metadata is recorded; raw queries, answers and identifiers are never stored.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[1] / "reports" / "telemetry.sqlite3"


def database_path() -> Path:
    configured = os.getenv("TELEMETRY_DB_PATH")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DB


def record_interaction(payload: dict) -> None:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # sqlite3's connection context manager commits/rolls back but does not close.
    # Close explicitly so repeated API requests do not leak file handles.
    connection = sqlite3.connect(path, timeout=5)
    try:
        connection.execute("""CREATE TABLE IF NOT EXISTS interaction_metrics (
            trace_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            topic TEXT,
            mode TEXT NOT NULL,
            latency_ms REAL NOT NULL CHECK (latency_ms >= 0),
            safety_flags_json TEXT NOT NULL,
            source_count INTEGER NOT NULL CHECK (source_count >= 0),
            tool_call_count INTEGER NOT NULL CHECK (tool_call_count >= 0)
        )""")
        connection.execute("""INSERT OR REPLACE INTO interaction_metrics
            (trace_id, topic, mode, latency_ms, safety_flags_json, source_count, tool_call_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (
                payload["trace_id"], payload.get("topic"), payload["mode"],
                float(payload["latency_ms"]), json.dumps(payload.get("safety_flags", [])),
                len(payload.get("source_ids", [])), len(payload.get("tool_calls", [])),
            ))
        connection.commit()
    finally:
        connection.close()
