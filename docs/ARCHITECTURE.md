# Architecture

```text
                     ┌─────────────────────────┐
 Browser ───────────>│ FastAPI Northstar app   │<────── TestClient / HTTPX
 (Playwright/Appium) │  /api/chat              │
                     └────────────┬────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 v                v                v
           Guardrails         Retriever         Tool router
       injection / PII      golden KB match   synthetic order lookup
                 │                │                │
                 └────────────────┼────────────────┘
                                  v
                         Response + trace metadata
                                  │
                      Optional Groq generation mode
                                  │
                                  v
                         Automated QA framework
          ┌───────────────────────┼───────────────────────┐
          v                       v                       v
      Pytest suites          DeepEval judge          Browser/mobile
   API/RAG/security/tool    relevance/faithfulness  Playwright/Appium
          └───────────────────────┬───────────────────────┘
                                  v
                        JSON + HTML run reports
```

The QA framework is separate from the application-under-test. Test helpers, assertions and golden datasets are reusable so that the same test design can be adapted to another assistant API.
