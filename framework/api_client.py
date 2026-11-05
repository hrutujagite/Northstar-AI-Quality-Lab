"""Reusable API client wrapper for application-under-test interactions."""
from fastapi.testclient import TestClient


class SupportAPIClient:
    def __init__(self, client: TestClient):
        self._client = client

    def health(self):
        return self._client.get("/health")

    def knowledge(self):
        return self._client.get("/api/knowledge")

    def ask(self, message: str, conversation_id: str | None = None):
        body = {"message": message}
        if conversation_id:
            body["conversation_id"] = conversation_id
        return self._client.post("/api/chat", json=body)

    def scan_devices(self):
        return self._client.get("/api/devices/ble/scan")

    def pair_device(self, device_id: str):
        return self._client.post("/api/devices/ble/pair", json={"device_id": device_id})

    def provision_wifi(self, device_id: str, ssid: str, password: str):
        return self._client.post("/api/devices/wifi/provision", json={
            "device_id": device_id, "ssid": ssid, "password": password
        })
