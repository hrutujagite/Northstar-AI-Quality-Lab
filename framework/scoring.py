"""Deterministic baseline metrics; these are not substitutes for semantic LLM judging."""
import re


def token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def lexical_f1(actual: str, reference: str) -> float:
    """Token-overlap F1 used as a cheap baseline for regression triage."""
    actual_tokens, reference_tokens = token_set(actual), token_set(reference)
    if not actual_tokens or not reference_tokens:
        return 0.0
    overlap = len(actual_tokens & reference_tokens)
    precision = overlap / len(actual_tokens)
    recall = overlap / len(reference_tokens)
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def required_fact_coverage(actual: str, required_facts: list[str]) -> float:
    """Fraction of known required facts present in output; transparent and deterministic."""
    if not required_facts:
        return 1.0
    actual_folded = actual.casefold()
    return sum(fact.casefold() in actual_folded for fact in required_facts) / len(required_facts)
