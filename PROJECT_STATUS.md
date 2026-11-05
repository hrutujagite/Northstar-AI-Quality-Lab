# Project verification status

Last updated: 2026-11-05

## Confirmed on the user's Windows machine

- Core deterministic suite before this enhancement patch: **44 passed**.
- Playwright UI suite: **2 passed**.
- Appium Android Chrome workflow: **1 passed** in 28.41 seconds. This is browser automation on an Android emulator against a mock BLE/Wi-Fi provisioning simulator, not native-app or physical-radio testing.
- Live DeepEval evaluations: returns, shipping and warranty each passed Answer Relevancy, Faithfulness and Hallucination checks (**9/9 metric checks** across three individually selected golden cases).
- Safe-refusal G-Eval: **0.8**, meeting the configured threshold of 0.8.

These were separate runs at different times, not one combined test execution. LLM-as-a-judge results are model- and prompt-dependent.

## Verified for this enhancement patch

- Deterministic/API/OpenAPI suite: **48 passed, 4 deselected** in the patch build environment. The four deselected tests are optional UI/LLM tests excluded by the selected marker expression.
- Coverage run for `app/` and `framework/`: **80% overall** in that build environment. `framework/groq_judge.py` is optional live-evaluation code and is not exercised by the deterministic suite.
- Postman collection JSON parses successfully. **The collection has not yet been run in Postman**; execute it locally before claiming Postman hands-on experience.
- Locust profile now checks response content as well as HTTP status. **No load-test measurements have yet been recorded**; run the short smoke profile locally before quoting throughput or latency.

## Not completed / limitations

- AWS S3, Lambda, CloudWatch, IAM and AWS Device Farm: no real AWS integration or Device Farm run has been completed. The Device Farm guide remains a setup plan only.
- Android: the Appium test is Android Chrome browser automation on an emulator using a mock BLE adapter. It does not demonstrate native Android/iOS automation or physical BLE provisioning. iOS automation requires macOS/Xcode.
- The fictional support service uses a small keyword-based retrieval fixture and synthetic customer/order/device data; it is a learning/demo system, not a production customer support platform.
- Prompt-injection and PII tests cover curated examples and are not a complete security audit.

## Next verification actions

1. Run the OpenAPI/Pytest checks on the Windows machine after applying the enhancement patch.
2. Import `postman/Northstar_AI_Quality_Lab.postman_collection.json` into Postman and run the collection against the local app. Restart the app before repeating the stateful mock provisioning folder.
3. Install `requirements-load.txt` and run the 30-second Locust smoke profile; retain the Locust summary and describe it as a small local smoke test, not production load testing.
4. Push the repository and verify the GitHub Actions workflow is green before sharing the repo with recruiters.