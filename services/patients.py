# services/patients.py
import json
import os
from typing import Optional, Dict, Any

DATA_FILE = os.path.join("data", "/Users/admrs/Documents/medical_intake_agent/data/patients.json")


def _load() -> list[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list[Dict[str, Any]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def lookup_by_id(medical_id: str) -> Optional[Dict[str, Any]]:
    patients = _load()
    for p in patients:
        if p["medical_id"] == medical_id:
            return p
    return None


def lookup_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    patients = _load()
    for p in patients:
        if p["phone"] == phone:
            return p
    return None


def add_patient(patient: Dict[str, Any]) -> None:
    patients = _load()
    patients.append(patient)
    _save(patients)
