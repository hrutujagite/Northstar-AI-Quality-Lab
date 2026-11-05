"""Load and validate the version-controlled golden evaluation dataset."""
import json
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parents[1] / "datasets" / "golden_questions.json"


def load_golden_questions() -> list[dict]:
    data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("Golden dataset must be a non-empty JSON list")
    required = {"id", "question", "expected_source_id", "expected_facts"}
    for index, item in enumerate(data):
        missing = required.difference(item)
        if missing:
            raise ValueError(f"Golden item {index} is missing keys: {sorted(missing)}")
    return data
