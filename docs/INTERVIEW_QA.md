# Interview preparation: AI Quality Engineering

## Why did you build this project?

I wanted to demonstrate quality engineering for AI-powered support workflows, not just build another chatbot. The framework separates the system under test from reusable test utilities and covers API contracts, retrieval regression, safety, multi-turn behavior, tool execution, failure recovery, telemetry and browser automation.

## What is the difference between ordinary software testing and LLM evaluation?

Ordinary software tests often assert deterministic behavior such as status codes, schemas and exact business rules. LLM outputs are non-deterministic, so evaluation also needs graded criteria such as relevance and faithfulness. I combine deterministic guardrails and contract tests with a model-judge layer for semantic output quality.

## What is a golden dataset?

A version-controlled set of representative inputs with expected source IDs and reference facts. Each release can be tested against the same cases to detect retrieval or response regressions. In this project the dataset is deliberately small and synthetic; it is an initial regression set, not a statistically complete benchmark.

## How do you detect hallucinations?

For a RAG workflow I use DeepEval Faithfulness against the context actually retrieved for a request. I also use HallucinationMetric against a curated reference context. A deterministic required-fact coverage check is included as a cheap baseline, but token/fact overlap is not a semantic hallucination detector.

## What is the difference between relevance and faithfulness?

Relevance asks whether the answer addresses the user's question. Faithfulness asks whether the claims in the answer are supported by retrieved context. An answer can be relevant but unfaithful—for example, it can discuss the correct return policy while inventing a 30-day window.

## How did you test prompt injection?

I created a small curated set of adversarial strings and verified that recognized attempts trigger a refusal before the retrieval/generation path. This is a regression guard, not a complete jailbreak defense. In a production system I would add broader red-team datasets, paraphrases, indirect document injection and model-specific safety evaluation.

## How is PII handled?

The app detects sample email and phone patterns, redacts them before a provider call, and avoids echoing the same identifiers. The SQLite telemetry table stores only operational metadata—trace ID, topic, mode, latency, safety flags and source/tool counts—not raw prompts or answers. The regex coverage is limited and is not a full PII detector.

## How do you test multi-turn workflows?

The demo retains only a conversation's last topic ID in process memory. A follow-up question can resolve against that topic. The test verifies the conversation ID is reused and that the expected topic context is retained. This is intentionally a lightweight prototype rather than a production session store.

## How do you test tool calling?

The demo recognizes synthetic order IDs and routes them to a mock `lookup_order_status` tool. Tests cover a successful lookup and an unknown ID. I verify the selected tool name, normalized argument and outcome status. No real order system is connected.

## How do you test failure recovery?

I simulate a provider timeout by replacing the provider call with a deterministic exception. The service returns the grounded knowledge-base answer, adds a fallback flag and does not expose provider internals. This makes the failure path repeatable without spending API quota.

## What makes the framework reusable?

Shared Pytest fixtures, a wrapper API client, domain assertions, an external JSON golden dataset, reusable scoring helpers and markers separate test intent from the application implementation. For another app I would replace the adapter and dataset while retaining or extending the test utilities.

## What is tested in CI?

The GitHub Actions workflow installs dependencies and Chromium, starts the app, runs deterministic API/retrieval/safety/workflow tests plus the Playwright smoke test, and uploads the report. Live LLM evaluation is opt-in because it requires secrets and provider quota.

## What are the current limitations?

The retriever is keyword-based; the prompt-injection patterns are curated; PII detection is regex-based; conversation context is in-memory; the Appium example is Android Chrome browser automation, not native BLE/Wi-Fi provisioning; and Device Farm is an execution guide until an actual device-farm run is performed.


## How did you test BLE and Wi-Fi onboarding?

I added a mock BLE adapter and provisioning state machine to represent discovery, pairing, Wi-Fi credential handoff, successful connection and a retryable network failure. API tests validate state transitions, invalid order of operations, unknown devices and password non-disclosure. The optional Appium test drives this workflow in Android Chrome. This is a simulator-based workflow test, not a real BLE hardware test; for production I would connect Appium to the native app and a controlled BLE peripheral or hardware-in-the-loop rig.
