# services/calls.py
import os, json

CALLS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "calls.json")


def safe_load():
    """Safely load calls.json. If missing or invalid, return []"""
    if not os.path.exists(CALLS_FILE):
        return []
    try:
        with open(CALLS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def safe_save(calls):
    """Safely save calls.json"""
    os.makedirs(os.path.dirname(CALLS_FILE), exist_ok=True)
    with open(CALLS_FILE, "w") as f:
        json.dump(calls, f, indent=2)


def upsert(record: dict):
    """
    Update an existing call if session_id matches,
    otherwise insert as a new call.
    """
    calls = safe_load()
    updated = False
    for c in calls:
        if c.get("session_id") == record.get("session_id"):
            c.update(record)
            updated = True
            break
    if not updated:
        calls.append(record)
    safe_save(calls)
    return updated, len(calls)
