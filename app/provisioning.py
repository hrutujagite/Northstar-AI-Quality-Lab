"""Mock BLE discovery and Wi-Fi provisioning state machine for connected-home test flows.

This is a simulator for functional workflow tests. It does not access a Bluetooth radio.
"""
from __future__ import annotations

from copy import deepcopy

_DEVICES = {
    "ATB-FAN-001": {"device_id": "ATB-FAN-001", "name": "Northstar Smart Fan", "kind": "fan"},
    "ATB-PUR-002": {"device_id": "ATB-PUR-002", "name": "Northstar Air Purifier", "kind": "purifier"},
    "ATB-FAN-FAIL": {"device_id": "ATB-FAN-FAIL", "name": "Northstar Fan (network test fixture)", "kind": "fan"},
}
_DEVICE_STATES: dict[str, dict] = {}


class DeviceNotFoundError(Exception):
    pass


class DeviceStateError(Exception):
    pass


def reset_provisioning_state() -> None:
    _DEVICE_STATES.clear()


def scan_ble_devices() -> list[dict]:
    """Return the synthetic discovery results that a BLE adapter would surface."""
    results = []
    for device_id, device in _DEVICES.items():
        current = _DEVICE_STATES.get(device_id, {"status": "discovered"})
        results.append({**deepcopy(device), "status": current["status"]})
    return results


def pair_ble_device(device_id: str) -> dict:
    device_id = device_id.upper()
    if device_id not in _DEVICES:
        raise DeviceNotFoundError(device_id)
    current = _DEVICE_STATES.get(device_id, {"status": "discovered"})
    if current["status"] == "connected":
        return {"device_id": device_id, "status": "connected", "message": "Device is already connected."}
    _DEVICE_STATES[device_id] = {"status": "paired"}
    return {"device_id": device_id, "status": "paired", "message": "Device paired successfully using the mock BLE adapter."}


def provision_wifi(device_id: str, ssid: str, password: str) -> dict:
    """Simulate Wi-Fi credential handoff; the password is deliberately never stored."""
    device_id = device_id.upper()
    if device_id not in _DEVICES:
        raise DeviceNotFoundError(device_id)
    current = _DEVICE_STATES.get(device_id, {"status": "discovered"})
    if current["status"] not in {"paired", "wifi_failed"}:
        raise DeviceStateError("Pair the device over BLE before sending Wi-Fi credentials.")

    # A dedicated synthetic fixture drives the recoverable network-failure test path.
    if device_id == "ATB-FAN-FAIL":
        _DEVICE_STATES[device_id] = {"status": "wifi_failed"}
        return {
            "device_id": device_id,
            "status": "wifi_failed",
            "retryable": True,
            "message": "The simulated device did not complete the Wi-Fi handshake. Check the network and retry.",
        }

    _DEVICE_STATES[device_id] = {"status": "connected"}
    return {
        "device_id": device_id,
        "status": "connected",
        "retryable": False,
        "message": f"Device connected to the '{ssid}' network in the simulator.",
    }
