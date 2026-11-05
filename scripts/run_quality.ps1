$ErrorActionPreference = "Stop"
python -m pytest -m "not llm and not ui and not mobile" -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "\nOpen reports/latest-run.html for the test summary."
