# Northstar AI Quality Lab

**A portfolio project demonstrating AI quality engineering for a fictional customer-support assistant.** The repository separates the application under test from reusable QA utilities, golden test data, deterministic regression suites, optional LLM-as-a-judge evaluations, browser automation and a mobile automation entry point.

> **Honesty note:** Northstar Home and all orders are fictional. The default tests are deterministic. The DeepEval suite makes real provider calls only when explicitly enabled. The Appium suite requires a configured Android device. The AWS Device Farm guide is an execution plan, not evidence of a completed cloud-device run. Do not claim a feature was executed unless you ran it and retained the result.

## Why this project is relevant

The target role describes automated LLM evaluation, groundedness/relevance/refusal checks, golden datasets, multi-turn flows, tool calling and failure recovery, web/API automation, CI, latency and safety. This repository demonstrates a small, inspectable version of those test concerns.

## Feature map

| Capability | Implementation | How to verify |
|---|---|---|
| Reusable test framework | `framework/` API client, assertions, dataset loader, scoring helpers | `pytest -m "not llm and not ui and not mobile"` |
| API validation | FastAPI TestClient + contract and boundary tests | `tests/test_api_contract.py` |
| OpenAPI / Postman | Schema contract tests plus importable Postman regression collection | `tests/test_openapi_contract.py`, `postman/` |
| Golden dataset regression | Versioned JSON examples, expected source IDs and required facts | `datasets/golden_questions.json`, `tests/test_rag_regression.py` |
| AI safety regression | Prompt-injection patterns, email/phone redaction before provider call | `tests/test_security.py` |
| Multi-turn and tool workflow | Topic-only conversation memory, synthetic order status tool, recovery path | `tests/test_conversation_and_tools.py` |
| LLM quality evaluation | DeepEval Answer Relevancy, Faithfulness, Hallucination and G-Eval refusal metrics | `tests/test_llm_eval.py` |
| Web UI automation | Playwright browser flow | `tests/test_web_ui.py` |
| Connected-device provisioning simulator | Mock BLE discovery/pairing, Wi-Fi setup state machine, validation and recovery tests | `app/provisioning.py`, `tests/test_device_provisioning.py` |
| Android mobile browser automation | Appium + UiAutomator2 smoke test of the provisioning workflow | `mobile/README.md` |
| Load testing | Locust traffic profile | `locustfile.py` |
| SQL/data validation | SQLite operational telemetry with constraints and no raw prompt/answer fields | `framework/telemetry.py`, `tests/test_reliability.py` |
| CI/CD | GitHub Actions workflow | `.github/workflows/tests.yml` |
| Reports | Custom HTML and JSON reports from pytest hooks | `reports/latest-run.html`, `reports/latest-run.json` |

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/TEST_STRATEGY.md`](docs/TEST_STRATEGY.md), [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) and [`docs/INTERVIEW_QA.md`](docs/INTERVIEW_QA.md).

```text
Browser / API Client
        |
        v
FastAPI application under test
  |-- guardrails (injection / PII)
  |-- retrieval (synthetic knowledge base)
  |-- tool router (synthetic order status)
  |-- mock BLE / Wi-Fi provisioning state machine
  +-- optional Groq LLM generation
        |
        v
Reusable QA framework
  |-- API contract & regression tests
  |-- curated golden dataset
  |-- safety / multi-turn / tool tests
  |-- optional DeepEval LLM judge
  |-- Playwright / Appium / Locust
        |
        v
HTML + JSON reports / GitHub Actions
```

## Windows 11 setup (Python 3.13)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## Run the deterministic suite

No API key or running server is required:

```powershell
python scripts/run_quality.py
```

Or run Pytest directly:

```powershell
pytest -m "not llm and not ui and not mobile" -v
```

After a run, inspect:

- `reports/latest-run.html` — readable summary
- `reports/latest-run.json` — machine-readable test list and durations
- `reports/telemetry.sqlite3` — operational metadata only (created on the first API call; raw queries and answers are not stored)

## Run the demo application and browser test

Terminal 1:

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the chat UI, `http://127.0.0.1:8000/docs` for Swagger UI, or `http://127.0.0.1:8000/openapi.json` for the OpenAPI schema.

To exercise the REST API independently in Postman, import [`postman/Northstar_AI_Quality_Lab.postman_collection.json`](postman/Northstar_AI_Quality_Lab.postman_collection.json) and follow [`docs/POSTMAN_API_TESTING.md`](docs/POSTMAN_API_TESTING.md).

Terminal 2:

```powershell
pytest -m ui -v
```

The UI test expects Chromium installed and the server running.

## Run live LLM generation and DeepEval evaluation

1. Copy `.env.example` to `.env` and add your own Groq API key. Do not commit `.env`.
2. Install optional dependencies:

```powershell
pip install -r requirements-eval.txt
```

3. Keep the model ID current with the models available to your Groq account. The default sample is `openai/gpt-oss-20b`.
4. Enable and execute the live test:

```powershell
$env:USE_LLM = "true"
$env:RUN_LLM_EVALS = "true"
$env:GROQ_MODEL_ID = "openai/gpt-oss-20b"
$env:DEEPEVAL_MODEL_ID = "openai/gpt-oss-20b"
$env:LLM_EVAL_CASE = "returns"  # returns | shipping | warranty
deepeval test run tests/test_llm_eval.py -k live_llm -v
```

The live suite evaluates one selected golden question per run to keep provider token usage predictable. Set `LLM_EVAL_CASE` to `returns`, `shipping`, or `warranty` and run the command again for another sample; allow the provider's token-per-minute window to reset between runs. Each selected answer is evaluated with DeepEval's `AnswerRelevancyMetric`, `FaithfulnessMetric`, and `HallucinationMetric`. Run the refusal check separately with `deepeval test run tests/test_llm_eval.py -k refusal -v`. The evaluator is a custom `DeepEvalBaseLLM` adapter (`framework/groq_judge.py`) that uses Groq JSON Object Mode plus Pydantic schema validation with bounded retries. These calls use provider quota and may incur charges. For RAG, faithfulness compares generated claims against retrieved context. Model scores can vary, so record the model ID, selected case and run output when reporting metrics.

## Run Appium on Android

The optional test automates the connected-device setup flow in Android Chrome through a mock BLE adapter. It is **mobile browser workflow testing**, not native app or physical BLE radio testing. Follow [`mobile/README.md`](mobile/README.md) to install Android Studio/SDK, Appium and UiAutomator2, then run:

```powershell
pip install -r requirements-mobile.txt
$env:APPIUM_SERVER_URL = "http://127.0.0.1:4723"
$env:ANDROID_UDID = "emulator-5554"
$env:APP_BASE_URL = "http://10.0.2.2:8000"
pytest mobile/tests -m mobile -v
```

An actual Android device/emulator run is required before claiming hands-on Appium execution. iOS automation requires macOS/Xcode.

## Optional load test

```powershell
pip install -r requirements-load.txt
uvicorn app.main:app --reload
locust -f locustfile.py --headless -u 3 -r 1 -t 30s --host http://127.0.0.1:8000 --only-summary
```

Start with a small number of users on the local demo. The tasks validate the health response, a known FAQ answer and the safe fallback for an unknown question; failed content checks are marked as Locust failures. Load-test results depend on your machine and should be recorded rather than invented. For a live technical discussion, use the sequence in [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) and prepare with [`docs/INTERVIEW_QA.md`](docs/INTERVIEW_QA.md).

## API and OpenAPI validation

The application exposes Swagger UI at `/docs` and its OpenAPI 3 schema at `/openapi.json`. `tests/test_openapi_contract.py` checks the published service metadata, required routes and request-boundary definitions. An importable Postman collection independently validates health, knowledge, chat, prompt-injection handling and the mock connected-device workflow. See [`docs/POSTMAN_API_TESTING.md`](docs/POSTMAN_API_TESTING.md).

## CI/CD

GitHub Actions runs the deterministic API, retrieval, safety, conversation/tool, reliability and Playwright tests on push/PR and uploads the generated reports. Provider-backed LLM evaluation is deliberately excluded from CI by default to avoid leaking keys or spending quota.

## Important limitations

- Retrieval is a transparent keyword matcher over synthetic FAQs, not a production vector database.
- Safety checks use curated regex patterns and a small test set; they do not prove complete jailbreak resistance or comprehensive PII detection.
- LLM-as-a-judge scores depend on the model and prompt; they are not ground truth.
- The session store is in-memory and stores only the last topic ID; it is not production-grade session infrastructure.
- The Appium example automates Android Chrome through a mock BLE/Wi-Fi provisioning workflow; it does not test a native Android/iOS application or a physical Bluetooth radio.
- AWS Device Farm is documented as a next step in [`devicefarm/README.md`](devicefarm/README.md); no AWS cloud run is claimed.

## Suggested interview explanation

"I built a reusable QA framework around a fictional RAG support assistant. I separated application logic from the test framework, created a versioned golden dataset, wrote API contract and safety regression tests, and tested conversation-topic continuity, synthetic tool calls and provider-failure fallback. For model-backed evaluation, I use DeepEval's answer-relevance and faithfulness metrics against retrieved context. I also added Playwright browser automation, CI execution and test-run reporting."

Only describe the optional pieces as hands-on after you have run them yourself.

### DeepEval judge implementation note

The live evaluation suite uses `framework.groq_judge.GroqJSONJudge`, a custom
`DeepEvalBaseLLM` adapter. It requests Groq JSON Object Mode and validates the
response against the Pydantic schema supplied by DeepEval, retrying up to three
times on schema-validation failures. This avoids relying on provider-side
best-effort JSON Schema mode for every metric schema. The application model and
the evaluation judge remain separate components.

Configure `DEEPEVAL_MODEL_ID` (defaults to `openai/gpt-oss-20b`) and
`RUN_LLM_EVALS=true` in `.env`. Never paste API keys or unredacted Authorization
headers into issue reports, screenshots, terminal logs, or chat messages. If a
key is exposed, revoke it in the provider console and create a replacement.
