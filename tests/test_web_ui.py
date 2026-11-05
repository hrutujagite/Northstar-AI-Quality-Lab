"""Playwright browser smoke test; start the app before running this marked test."""
import os
import httpx
import pytest

from playwright.sync_api import sync_playwright


@pytest.mark.ui
def test_support_chat_ui():
    base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
    try:
        httpx.get(f"{base_url}/health", timeout=2.0)
    except httpx.HTTPError:
        pytest.skip("Start the app with: uvicorn app.main:app --reload")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(base_url)
            page.get_by_label("Your question").fill("What is the return window?")
            page.get_by_role("button", name="Send question").click()
            page.get_by_test_id("assistant-response").get_by_text("7 days")
            page.wait_for_function("() => document.querySelector('[data-testid=trace-metadata]').textContent.includes('Trace:')")
            assert "7 days" in page.get_by_test_id("assistant-response").inner_text()
            assert "Trace:" in page.get_by_test_id("trace-metadata").inner_text()
            browser.close()
    except Exception as exc:
        message = str(exc).lower()
        if "executable doesn't exist" in message or "browser not found" in message:
            pytest.skip("Install Chromium using: python -m playwright install chromium")
        raise


@pytest.mark.ui
def test_connected_device_setup_ui_flow():
    base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
    try:
        httpx.get(f"{base_url}/health", timeout=2.0)
    except httpx.HTTPError:
        pytest.skip("Start the app with: uvicorn app.main:app --reload")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/setup")
            page.get_by_role("button", name="Scan devices").click()
            page.locator("#pair-ATB-FAN-001").click()
            page.get_by_label("Wi-Fi network name (SSID)").fill("BrowserTestNetwork")
            page.get_by_label("Wi-Fi password (8–63 characters)").fill("dummy-pass-123")
            page.get_by_role("button", name="Provision device").click()
            page.wait_for_function("() => document.querySelector('[data-testid=provision-status]').dataset.status === 'connected'")
            assert "connected" in page.get_by_test_id("provision-status").inner_text().lower()
            browser.close()
    except Exception as exc:
        message = str(exc).lower()
        if "executable doesn't exist" in message or "browser not found" in message:
            pytest.skip("Install Chromium using: python -m playwright install chromium")
        raise
