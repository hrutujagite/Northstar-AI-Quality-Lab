# Android automation (Appium)

The optional test drives the responsive Northstar support web app in Chrome on an Android emulator/device using Appium's UiAutomator2 driver. It is a mobile-browser smoke test, **not** a native Android application test.

## Install

1. Install Android Studio and create an Android emulator, or connect a USB-debugging-enabled Android phone.
2. Ensure Android SDK Platform Tools are installed and `adb devices` lists the device.
3. Install Node.js, then install Appium: `npm install -g appium`.
4. Install the Android driver: `appium driver install uiautomator2`.
5. Start the Appium server: `appium`.
6. In Python, install: `pip install Appium-Python-Client selenium`.
7. Start the FastAPI app: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

For the standard Android emulator, use `APP_BASE_URL=http://10.0.2.2:8000`. For a physical phone, use your computer's LAN IP and ensure both devices are on the same network.

## Run

PowerShell:

```powershell
$env:APPIUM_SERVER_URL = "http://127.0.0.1:4723"
$env:ANDROID_UDID = "emulator-5554" # replace with adb devices output
$env:APP_BASE_URL = "http://10.0.2.2:8000"
pytest mobile/tests -m mobile -v
```

This tests the provisioning UI in Android Chrome. BLE discovery is simulated by the app; the test does not communicate with a physical peripheral. iOS automation requires macOS/Xcode and a separate XCUITest setup.
