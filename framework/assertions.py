"""Reusable domain assertions shared by API and regression tests."""

REQUIRED_CHAT_FIELDS = {
    "query", "answer", "source_ids", "retrieval_context", "safety_flags",
    "latency_ms", "mode", "tool_calls", "trace_id", "conversation_id", "topic",
}


def assert_chat_payload(payload: dict) -> None:
    missing = REQUIRED_CHAT_FIELDS.difference(payload)
    assert not missing, f"Chat response is missing fields: {sorted(missing)}"
    assert isinstance(payload["answer"], str) and payload["answer"].strip()
    assert isinstance(payload["source_ids"], list)
    assert isinstance(payload["retrieval_context"], list)
    assert isinstance(payload["safety_flags"], list)
    assert isinstance(payload["tool_calls"], list)
    assert isinstance(payload["latency_ms"], (int, float)) and payload["latency_ms"] >= 0
    assert payload["trace_id"]
    assert payload["conversation_id"]


def assert_grounded_source(payload: dict, expected_source_id: str) -> None:
    assert expected_source_id in payload["source_ids"]
    assert payload["retrieval_context"], "Expected a non-empty retrieval context for a sourced answer"


def assert_required_facts(answer: str, required_facts: list[str]) -> None:
    normalized = answer.casefold()
    missing = [fact for fact in required_facts if fact.casefold() not in normalized]
    assert not missing, f"Answer omitted required reference facts: {missing}"
