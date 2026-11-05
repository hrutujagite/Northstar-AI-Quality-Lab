"""Multi-turn topic resolution and synthetic tool workflow tests."""


def test_follow_up_question_reuses_conversation_topic(api_client):
    first = api_client.ask("What is the return window?").json()
    follow_up = api_client.ask("Does that policy allow opened items?", conversation_id=first["conversation_id"]).json()
    assert follow_up["conversation_id"] == first["conversation_id"]
    assert follow_up["topic"] == "returns"
    assert "unused" in follow_up["answer"].lower()


def test_order_lookup_uses_tool_and_returns_synthetic_status(api_client):
    payload = api_client.ask("Can you track order NH-1001?").json()
    assert payload["mode"] == "mock_tool"
    assert payload["tool_calls"][0]["tool"] == "lookup_order_status"
    assert payload["tool_calls"][0]["status"] == "success"
    assert "in transit" in payload["answer"].lower()


def test_unknown_order_returns_recoverable_tool_error(api_client):
    payload = api_client.ask("Track order NH-9999").json()
    assert payload["tool_calls"][0]["status"] == "not_found"
    assert "check the order id" in payload["answer"].lower()


def test_provider_failure_falls_back_to_grounded_fixture(monkeypatch, api_client):
    import app.service as service
    monkeypatch.setenv("USE_LLM", "true")
    def fail_provider(*_args, **_kwargs):
        raise TimeoutError("simulated provider timeout")
    monkeypatch.setattr(service, "_call_groq", fail_provider)
    payload = api_client.ask("What is the return window?").json()
    assert payload["mode"] == "llm_fallback"
    assert "LLM_PROVIDER_ERROR_FALLBACK" in payload["safety_flags"]
    assert "7 days" in payload["answer"]
