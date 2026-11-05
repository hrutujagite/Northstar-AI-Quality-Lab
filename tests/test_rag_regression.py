"""Data-driven retrieval and answer-regression tests using a versioned golden set."""
import pytest
from framework.assertions import assert_grounded_source, assert_required_facts
from framework.dataset import load_golden_questions
from framework.scoring import required_fact_coverage

GOLDENS = load_golden_questions()


@pytest.mark.parametrize("golden", GOLDENS, ids=lambda item: item["id"])
def test_golden_question_retrieves_expected_document_and_facts(api_client, golden):
    payload = api_client.ask(golden["question"]).json()
    assert_grounded_source(payload, golden["expected_source_id"])
    assert_required_facts(payload["answer"], golden["expected_facts"])
    assert required_fact_coverage(payload["answer"], golden["expected_facts"]) == 1.0


def test_unknown_question_returns_safe_fallback(api_client):
    payload = api_client.ask("Can I pay using antique gold coins from 1920?").json()
    assert payload["source_ids"] == []
    assert payload["retrieval_context"] == []
    assert "don't have enough information" in payload["answer"].lower()


def test_lexical_f1_baseline_is_bounded_and_reproducible():
    from framework.scoring import lexical_f1

    assert lexical_f1("delivery in 3 to 5 days", "delivery in 3 to 5 days") == 1.0
    score = lexical_f1("delivery in 3 to 5 days", "delivery in 4 to 6 days")
    assert 0.0 < score < 1.0
    assert lexical_f1("", "non-empty reference") == 0.0


def test_shipping_duration_answer_does_not_add_unasked_tracking_details(api_client):
    payload = api_client.ask("How long does standard delivery take?").json()
    answer = payload["answer"].lower()
    assert "3 to 5 business days" in answer
    assert "tracking link" not in answer
