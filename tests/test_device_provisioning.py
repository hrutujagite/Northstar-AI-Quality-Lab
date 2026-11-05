"""BLE discovery/pairing and Wi-Fi provisioning workflow tests against a mock adapter."""


def test_ble_scan_returns_synthetic_devices(api_client):
    response = api_client.scan_devices()
    assert response.status_code == 200
    payload = response.json()
    assert payload["adapter"] == "mock_ble_adapter"
    assert {device["device_id"] for device in payload["devices"]} == {"ATB-FAN-001", "ATB-PUR-002", "ATB-FAN-FAIL"}


def test_pairing_changes_device_state(api_client):
    response = api_client.pair_device("ATB-FAN-001")
    assert response.status_code == 200
    assert response.json()["status"] == "paired"


def test_wifi_provisioning_requires_ble_pairing(api_client):
    response = api_client.provision_wifi("ATB-FAN-001", "HomeNetwork", "dummy-pass-123")
    assert response.status_code == 409
    assert "pair the device" in response.json()["detail"].lower()


def test_wifi_provisioning_completes_after_pairing(api_client):
    api_client.pair_device("ATB-FAN-001")
    response = api_client.provision_wifi("ATB-FAN-001", "HomeNetwork", "dummy-pass-123")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "connected"
    assert payload["retryable"] is False
    assert "dummy-pass-123" not in response.text
    from app.provisioning import _DEVICE_STATES
    assert "dummy-pass-123" not in repr(_DEVICE_STATES)


def test_wifi_failure_is_recoverable(api_client):
    api_client.pair_device("ATB-FAN-FAIL")
    first = api_client.provision_wifi("ATB-FAN-FAIL", "HomeNetwork", "dummy-pass-123")
    second = api_client.provision_wifi("ATB-FAN-FAIL", "HomeNetwork2", "dummy-pass-456")
    assert first.status_code == 200 and first.json()["status"] == "wifi_failed"
    assert first.json()["retryable"] is True
    assert second.status_code == 200 and second.json()["status"] == "wifi_failed"


def test_unknown_device_returns_404(api_client):
    response = api_client.pair_device("UNKNOWN-99")
    assert response.status_code == 404


def test_short_wifi_password_is_rejected(raw_test_client):
    response = raw_test_client.post("/api/devices/wifi/provision", json={
        "device_id": "ATB-FAN-001", "ssid": "HomeNetwork", "password": "short"
    })
    assert response.status_code == 422


def test_setup_page_explains_simulated_adapter(raw_test_client):
    response = raw_test_client.get("/setup")
    assert response.status_code == 200
    assert "mock BLE adapter" in response.text
    assert "does not use a real Bluetooth radio" in response.text
