# Test Strategy

## System under test

Northstar Home is a fictional customer-support assistant. It combines keyword-based retrieval over a small version-controlled knowledge base, deterministic response fixtures, a synthetic order-status tool, safety checks, and an optional Groq-backed generation mode. No real customer, account, order, or company data is used.

## Test layers

| Layer | Purpose | Main tools | Deterministic by default? |
|---|---|---|---|
| API contract | Schema, status codes, boundary validation | FastAPI TestClient, Pytest | Yes |
| Retrieval regression | Golden question -> expected source and required facts | JSON golden set, Pytest | Yes |
| Safety regression | Injection patterns, PII redaction before provider call | Pytest | Yes |
| Conversation/tool | Topic carry-over, order lookup, tool failure recovery | Pytest | Yes |
| LLM quality | Relevance and faithfulness judged against retrieved context | DeepEval + custom Groq JSON-mode judge | No; opt-in |
| Browser E2E | Chat form flow and response rendering | Playwright | Yes, with server running |
| Device provisioning | Mock BLE discovery/pairing, Wi-Fi provisioning, invalid-state and recoverable network failure | FastAPI + Pytest | Yes |
| Mobile browser | Android Chrome provisioning smoke flow | Appium + UiAutomator2 | Device-dependent |
| SQL/data validation | Metric persistence, schema checks and privacy-field exclusion | SQLite + Pytest | Yes |
| Load smoke | Basic API throughput and latency distribution | Locust | Environment-dependent |

## Quality signals

- Source correctness: expected source ID returned for each golden question.
- Required-fact coverage: all curated facts for the expected answer are present.
- Faithfulness: DeepEval judge evaluates generated claims against retrieved context.
- Hallucination: DeepEval compares generated output against curated reference context.
- Refusal: G-Eval judges whether the assistant clearly refuses policy-violating requests without disclosure.
- Relevance: DeepEval judge evaluates whether the answer addresses the input.
- Safety regressions: known attack strings are blocked and example PII is not passed to the LLM provider.
- Reliability: provider failures fall back to a grounded deterministic answer; unknown tool targets return a recoverable result.
- Traceability: each response has a trace ID and conversation ID.
- Data protection: SQLite stores operational metadata only; it does not persist raw prompts, answers, email addresses or phone numbers.

## Known limitations

- The retrieval algorithm is a small keyword matcher, not a production vector database or semantic retriever.
- Regex prompt-injection checks cover a curated set of patterns; they are not a complete jailbreak defense.
- PII tests cover sample emails and phone numbers, not every identifier or regional format.
- LLM judge scores are model-dependent and may vary. Store model ID, dataset version and run date when comparing results.
- Conversation topic memory is in-process and stores only a topic ID; it is not production session storage.
- The Android test is mobile-browser automation against a mock BLE adapter. It does not test native Android/iOS apps or real BLE radio behavior.
- AWS Device Farm execution is documented but has not been run by this repository's author unless separately recorded with real run evidence.

## Golden question scope alignment

A golden question must explicitly ask for each fact that the expected answer is required to include. The warranty case asks both for the warranty term and for the requirement to claim it, because the expected facts include proof of purchase. This avoids treating a supported policy condition as an irrelevant extra detail.
