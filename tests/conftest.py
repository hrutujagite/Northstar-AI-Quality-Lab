"""Shared fixtures and lightweight machine-readable test-run reporting."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.service import reset_conversations
from app.provisioning import reset_provisioning_state
from framework.api_client import SupportAPIClient

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
_TEST_RESULTS: list[dict] = []


@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    monkeypatch.setenv("USE_LLM", "false")
    reset_conversations()
    reset_provisioning_state()


@pytest.fixture
def api_client():
    with TestClient(app) as client:
        yield SupportAPIClient(client)


@pytest.fixture
def raw_test_client():
    with TestClient(app) as client:
        yield client


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        _TEST_RESULTS.append({
            "test": item.nodeid,
            "status": report.outcome,
            "duration_seconds": round(report.duration, 4),
            "failure": str(report.longrepr)[:1200] if report.failed else None,
        })


def pytest_sessionfinish(session, exitstatus):
    if not _TEST_RESULTS:
        return
    REPORTS_DIR.mkdir(exist_ok=True)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "exit_status": int(exitstatus),
        "total": len(_TEST_RESULTS),
        "passed": sum(r["status"] == "passed" for r in _TEST_RESULTS),
        "failed": sum(r["status"] == "failed" for r in _TEST_RESULTS),
        "skipped": sum(r["status"] == "skipped" for r in _TEST_RESULTS),
        "tests": _TEST_RESULTS,
    }
    (REPORTS_DIR / "latest-run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    rows = "".join(
        f"<tr><td>{html.escape(r['test'])}</td><td class='{r['status']}'>{r['status'].upper()}</td>"
        f"<td>{r['duration_seconds']:.4f}s</td><td><pre>{html.escape(r['failure'] or '')}</pre></td></tr>"
        for r in _TEST_RESULTS
    )
    report_html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Northstar AI Quality Run</title><style>
body{{font:15px system-ui,Segoe UI,sans-serif;background:#f5f7fb;color:#172033;margin:0;padding:32px}}main{{max-width:1100px;margin:auto;background:white;padding:28px;border-radius:16px;box-shadow:0 8px 30px #14213d12}}h1{{margin-top:0}}.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{padding:14px 18px;background:#f1f4f9;border-radius:10px;min-width:100px}}.n{{font-size:25px;font-weight:700}}table{{width:100%;border-collapse:collapse;margin-top:22px}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #e5eaf0;vertical-align:top}}th{{background:#f6f8fb}}.passed{{color:#157347;font-weight:700}}.failed{{color:#b42318;font-weight:700}}.skipped{{color:#8a6700;font-weight:700}}pre{{white-space:pre-wrap;max-width:420px}}
</style></head><body><main><h1>Northstar AI Quality — Test Run</h1><p>Generated {html.escape(summary['generated_at_utc'])}</p>
<div class='cards'><div class='card'><div class='n'>{summary['total']}</div>Total</div><div class='card'><div class='n'>{summary['passed']}</div>Passed</div><div class='card'><div class='n'>{summary['failed']}</div>Failed</div><div class='card'><div class='n'>{summary['skipped']}</div>Skipped</div></div>
<table><thead><tr><th>Test</th><th>Status</th><th>Duration</th><th>Failure detail</th></tr></thead><tbody>{rows}</tbody></table>
</main></body></html>"""
    (REPORTS_DIR / "latest-run.html").write_text(report_html, encoding="utf-8")
