"""OpenAPI contract checks for the documented REST surface."""


def test_openapi_document_is_exposed_and_versioned(raw_test_client):
    response = raw_test_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Northstar AI Support Assistant"
    assert schema["info"]["version"] == "2.0.0"
    assert schema["openapi"].startswith("3.")


def test_required_api_operations_are_documented(raw_test_client):
    schema = raw_test_client.get("/openapi.json").json()
    paths = schema["paths"]
    expected = {
        ("/health", "get"),
        ("/api/knowledge", "get"),
        ("/api/chat", "post"),
        ("/api/devices/ble/scan", "get"),
        ("/api/devices/ble/pair", "post"),
        ("/api/devices/wifi/provision", "post"),
    }
    documented = {
        (path, method.lower())
        for path, operations in paths.items()
        for method in operations
        if method.lower() in {"get", "post", "put", "patch", "delete"}
    }
    assert expected <= documented


def test_openapi_request_schemas_enforce_input_boundaries(raw_test_client):
    schemas = raw_test_client.get("/openapi.json").json()["components"]["schemas"]

    chat_message = schemas["ChatRequest"]["properties"]["message"]
    assert chat_message["type"] == "string"
    assert chat_message["minLength"] == 1
    assert chat_message["maxLength"] == 2000

    wifi = schemas["WifiProvisionRequest"]["properties"]
    assert wifi["ssid"]["minLength"] == 1
    assert wifi["ssid"]["maxLength"] == 32
    assert wifi["password"]["minLength"] == 8
    assert wifi["password"]["maxLength"] == 63
