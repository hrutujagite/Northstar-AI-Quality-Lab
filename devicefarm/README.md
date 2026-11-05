# AWS Device Farm execution notes

This repository includes an Appium Android Chrome smoke test in `mobile/tests/test_appium_android.py`. Run and stabilize it locally first; Device Farm is a remote execution target, not a replacement for local test debugging.

## Before attempting a Device Farm run

1. Complete the local Appium setup in `mobile/README.md`.
2. Confirm that the Android test passes on a local emulator or connected device.
3. Keep the demo application reachable from the test device. For Device Farm, deploy the demo API/UI to a temporary HTTPS test environment or bundle a test app/service appropriate to the chosen Device Farm test type. `localhost` on your laptop is not reachable from a remote AWS device.
4. Package the Appium/Python test according to the currently selected Device Farm test type and install dependencies in its test spec.
5. Upload the package, select real devices, execute the run, and retain the Device Farm logs/screenshots as evidence.

The project does **not** claim a Device Farm run has been completed. This is an execution guide only. AWS Device Farm APIs, supported runtimes, packaging rules and pricing can change; verify the current AWS console documentation before creating a paid run.
