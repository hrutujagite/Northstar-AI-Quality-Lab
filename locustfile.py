"""Validated Locust smoke/load profile for the local demo API.

Run a small local smoke profile:
  locust -f locustfile.py --headless -u 3 -r 1 -t 30s \\
    --host http://127.0.0.1:8000 --only-summary

Run the interactive UI:
  locust -f locustfile.py --host http://127.0.0.1:8000
"""
from locust import HttpUser, between, task


class SupportAssistantUser(HttpUser):
    wait_time = between(1, 3)

    @task(4)
    def ask_known_question(self):
        with self.client.post(
            "/api/chat",
            name="/api/chat [known FAQ]",
            json={"message": "What is the return window?"},
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected HTTP 200, got {response.status_code}")
                return
            try:
                answer = response.json().get("answer", "").lower()
            except ValueError:
                response.failure("Response was not valid JSON")
                return
            if "7 days" not in answer:
                response.failure("Known FAQ response missed the expected return-policy fact")
            else:
                response.success()

    @task(1)
    def ask_unknown_question(self):
        with self.client.post(
            "/api/chat",
            name="/api/chat [unknown FAQ]",
            json={"message": "Can I pay using antique coins?"},
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected HTTP 200, got {response.status_code}")
                return
            try:
                payload = response.json()
            except ValueError:
                response.failure("Response was not valid JSON")
                return
            if payload.get("source_ids") or "don't have enough information" not in payload.get("answer", "").lower():
                response.failure("Unknown question did not return the safe fallback")
            else:
                response.success()

    @task(1)
    def health_check(self):
        with self.client.get("/health", name="/health", catch_response=True) as response:
            if response.status_code != 200 or response.json().get("status") != "ok":
                response.failure("Health check contract failed")
            else:
                response.success()
