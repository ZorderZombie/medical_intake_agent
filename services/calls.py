# services/calls.py
import json
import os
from typing import Dict, Any, List

DATA_FILE = os.path.join("data", "/Users/admrs/Documents/medical_intake_agent/data/calls.json")


def _load() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: List[Dict[str, Any]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def store(call: Dict[str, Any]) -> None:
    calls = _load()
    calls.append(call)
    _save(calls)


def enrich(session_id: str, redacted: str, soap: Dict[str, Any], risk: str) -> None:
    calls = _load()
    for c in calls:
        if c["session_id"] == session_id:
            c["redacted_transcript"] = redacted
            c["soap"] = soap
            c["risk"] = risk
            break
    _save(calls)


def list_calls() -> List[Dict[str, Any]]:
    return _load()
