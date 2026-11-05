"""Run deterministic quality tests and print the generated local report locations."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
command = [sys.executable, "-m", "pytest", "-m", "not llm and not ui", "-q"]
result = subprocess.run(command, cwd=ROOT, check=False)
print("\nQuality run complete.")
print(f"HTML report: {REPORTS / 'latest-run.html'}")
print(f"JSON report: {REPORTS / 'latest-run.json'}")
sys.exit(result.returncode)
