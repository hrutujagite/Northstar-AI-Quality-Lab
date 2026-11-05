"""Basic reliability and consistency checks."""
from framework.assertions import assert_chat_payload


def test_trace_and_conversation_ids_are_present(api_client):
    payload = api_client.ask("How long does delivery take?").json()
    assert_chat_payload(payload)
    assert len(payload["trace_id"]) >= 20


def test_each_request_has_a_unique_trace_id(api_client):
    first = api_client.ask("What is the warranty?").json()
    second = api_client.ask("What payment methods are supported?").json()
    assert first["trace_id"] != second["trace_id"]


def test_unicode_input_is_handled(api_client):
    payload = api_client.ask("मुझे delivery कब मिलेगी? 📦").json()
    assert payload["answer"]
    assert payload["latency_ms"] >= 0


def test_sqlite_telemetry_stores_metrics_without_raw_user_content(tmp_path, monkeypatch, api_client):
    import json
    import sqlite3
    from contextlib import closing

    from framework.telemetry import database_path

    database_file = tmp_path / "test-telemetry.sqlite3"
    monkeypatch.setenv("TELEMETRY_DB_PATH", str(database_file))
    email = "sensitive.person@example.test"
    payload = api_client.ask(f"How can I contact support? My email is {email}").json()

    assert database_path() == database_file.resolve()
    with closing(sqlite3.connect(database_file)) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(interaction_metrics)")}
        row = connection.execute(
            "SELECT trace_id, mode, latency_ms, safety_flags_json, source_count FROM interaction_metrics WHERE trace_id = ?",
            (payload["trace_id"],),
        ).fetchone()

    assert row is not None
    assert row[0] == payload["trace_id"]
    assert row[1] == "deterministic_fixture"
    assert row[2] >= 0
    assert "PII_IN_INPUT_REDACTED_BEFORE_MODEL" in json.loads(row[3])
    assert row[4] == 1
    assert not ({"query", "prompt", "answer", "email", "phone"} & columns)
    assert email not in repr(row)


def test_sqlite_telemetry_rejects_negative_latency(tmp_path, monkeypatch):
    import sqlite3
    import pytest
    from framework.telemetry import record_interaction

    monkeypatch.setenv("TELEMETRY_DB_PATH", str(tmp_path / "constraints.sqlite3"))
    payload = {
        "trace_id": "trace-invalid", "topic": "returns", "mode": "test", "latency_ms": -1,
        "safety_flags": [], "source_ids": [], "tool_calls": [],
    }
    with pytest.raises(sqlite3.IntegrityError):
        record_interaction(payload)
