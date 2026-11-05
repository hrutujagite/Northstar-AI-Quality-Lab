"""Optional Appium Android Chrome test for the connected-device provisioning simulator.

This is mobile-browser workflow automation against a mock BLE adapter, not radio-level BLE.
"""
import os
import pytest

pytestmark = pytest.mark.mobile


def test_android_chrome_device_provisioning_flow():
    server = os.getenv("APPIUM_SERVER_URL")
    udid = os.getenv("ANDROID_UDID")
    app_url = os.getenv("APP_BASE_URL", "http://10.0.2.2:8000")
    if not server or not udid:
        pytest.skip("Set APPIUM_SERVER_URL and ANDROID_UDID after starting an Android emulator and Appium")

    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
    options.udid = udid
    options.browser_name = "Chrome"
    driver = webdriver.Remote(server, options=options)

    try:
        wait = WebDriverWait(driver, 20)
        driver.get(f"{app_url}/setup")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#scan-devices"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#pair-ATB-FAN-001"))).click()
        wait.until(lambda d: "paired" in d.find_element(By.CSS_SELECTOR, "#provision-status").text.lower())
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#wifi-ssid"))).send_keys("MobileDemoNetwork")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#wifi-password"))).send_keys("dummy-pass-123")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#connect-device"))).click()
        wait.until(lambda d: "connected" in d.find_element(By.CSS_SELECTOR, "#provision-status").text.lower())
        status = driver.find_element(By.CSS_SELECTOR, "#provision-status").text.lower()
        assert "connected" in status
    finally:
        driver.quit()
