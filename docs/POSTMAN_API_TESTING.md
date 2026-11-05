# Postman API regression collection

The collection at `postman/Northstar_AI_Quality_Lab.postman_collection.json` is a runnable black-box API regression pack for the fictional Northstar service.

## Run locally

1. Activate the project virtual environment and start the app:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. Import the JSON collection into Postman (`Import` → `Files`). Its `baseUrl` defaults to `http://127.0.0.1:8000`.
3. Run the folders in order. The connected-device folder uses a mock BLE adapter and a synthetic device ID; it does not use Bluetooth hardware.
4. The device workflow is stateful. Restart the app process before rerunning that folder so the in-memory simulator resets to its initial state.
5. Keep the demo password synthetic. Do not put personal Wi-Fi credentials or API keys into the collection.

## Coverage

- Health endpoint and service metadata
- OpenAPI document presence and selected route documentation
- Knowledge-base metadata
- Chat traceability and retrieval source selection
- Prompt-injection refusal behavior
- Request validation for blank input
- Mock BLE scan, pairing and Wi-Fi provisioning
- Credential non-disclosure in the provisioning response

The automated Pytest OpenAPI checks are in `tests/test_openapi_contract.py`. The Postman collection demonstrates an independent black-box client workflow; it is not a substitute for the Python test suite.
