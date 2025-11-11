"""
Mock FHIR utilities for the Virtual Health Assistant POC.

Provides simple JSON-backed resources for patients, encounters, observations,
and scheduling slots to support local function tools.
"""

from __future__ import annotations

import json
import pathlib
from typing import Dict, List, Any

DATA_ROOT = pathlib.Path(__file__).parent


def _read_json(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_patient(patient_id: str) -> Dict[str, Any]:
    path = DATA_ROOT / f"patient_{patient_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Mock patient not found: {patient_id}")
    return _read_json(path)


def load_encounters(patient_id: str) -> List[Dict[str, Any]]:
    path = DATA_ROOT / f"encounters_{patient_id}.json"
    if not path.exists():
        return []
    return _read_json(path)


def load_observations(patient_id: str) -> List[Dict[str, Any]]:
    path = DATA_ROOT / f"observations_{patient_id}.json"
    if not path.exists():
        return []
    return _read_json(path)


def load_schedule_slots(patient_id: str, date_range: str = "next-7-days") -> List[Dict[str, Any]]:
    path = DATA_ROOT / "mock_calendar.json"
    if not path.exists():
        return []

    calendar = _read_json(path)
    key = f"{patient_id}:{date_range}"
    slots = calendar.get(key)
    if slots is None:
        slots = calendar.get(date_range, [])
    return slots


__all__ = [
    "load_patient",
    "load_encounters",
    "load_observations",
    "load_schedule_slots",
]

