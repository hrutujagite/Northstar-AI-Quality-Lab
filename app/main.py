"""FastAPI demo application under test."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, SecretStr, field_validator

from app.service import _redact_pii, generate_response
from app.provisioning import (
    DeviceNotFoundError, DeviceStateError, pair_ble_device, provision_wifi, scan_ble_devices,
)

app = FastAPI(
    title="Northstar AI Support Assistant",
    description="Fictional RAG-style customer-support assistant used to demonstrate AI quality engineering.",
    version="2.0.0",
)
HTML_PATH = Path(__file__).parent / "templates" / "index.html"
SETUP_HTML_PATH = Path(__file__).parent / "templates" / "setup.html"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, description="Customer question")
    conversation_id: str | None = Field(default=None, max_length=64)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value.strip()


class PairDeviceRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=32)


class WifiProvisionRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=32)
    ssid: str = Field(min_length=1, max_length=32)
    password: SecretStr = Field(min_length=8, max_length=63)


@app.get("/health", tags=["Operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "northstar-ai-support", "version": app.version}


@app.get("/api/knowledge", tags=["Knowledge"])
def knowledge() -> dict:
    from app.knowledge_base import FAQS
    return {"documents": [{"id": item["id"], "title": item["title"]} for item in FAQS]}


@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
def home() -> HTMLResponse:
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))


@app.get("/setup", response_class=HTMLResponse, tags=["Device provisioning"])
def device_setup() -> HTMLResponse:
    return HTMLResponse(SETUP_HTML_PATH.read_text(encoding="utf-8"))


@app.get("/api/devices/ble/scan", tags=["Device provisioning"])
def ble_scan() -> dict:
    return {"devices": scan_ble_devices(), "adapter": "mock_ble_adapter"}


@app.post("/api/devices/ble/pair", tags=["Device provisioning"])
def ble_pair(payload: PairDeviceRequest) -> dict:
    try:
        return pair_ble_device(payload.device_id)
    except DeviceNotFoundError:
        raise HTTPException(status_code=404, detail="Device not found in the simulated BLE scan.")


@app.post("/api/devices/wifi/provision", tags=["Device provisioning"])
def wifi_provision(payload: WifiProvisionRequest) -> dict:
    try:
        return provision_wifi(payload.device_id, payload.ssid, payload.password.get_secret_value())
    except DeviceNotFoundError:
        raise HTTPException(status_code=404, detail="Device not found in the simulated BLE scan.")
    except DeviceStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.post("/api/chat", tags=["Assistant"])
def chat(payload: ChatRequest) -> dict:
    result = generate_response(payload.message, payload.conversation_id)
    return {"query": _redact_pii(payload.message), **result}
