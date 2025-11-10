#!/usr/bin/env python3
"""
Mock FHIR (Fast Healthcare Interoperability Resources) API utilities.

Provides in-memory patient, encounter, and appointment data along with helper
functions to simulate read/write interactions. Designed for use within local
Flask applications and Cloud Functions to prototype healthcare flows without
connecting to real EHR systems.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock data stores
# ---------------------------------------------------------------------------

_NOW = datetime.now(timezone.utc)

_PATIENTS: Dict[str, Dict] = {
    "patient-001": {
        "resourceType": "Patient",
        "id": "patient-001",
        "identifier": [
            {
                "system": "https://health.example.org/mrn",
                "value": "MRN-0001",
            }
        ],
        "name": [
            {
                "use": "official",
                "family": "Doe",
                "given": ["Jane"],
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": "+1-555-0100",
                "use": "mobile",
            }
        ],
        "gender": "female",
        "birthDate": "1984-08-17",
        "managingOrganization": {
            "display": "Sample Health Primary Care",
        },
    },
    "patient-002": {
        "resourceType": "Patient",
        "id": "patient-002",
        "identifier": [
            {
                "system": "https://health.example.org/mrn",
                "value": "MRN-0002",
            }
        ],
        "name": [
            {
                "use": "official",
                "family": "Smith",
                "given": ["Alex"],
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": "+1-555-0150",
                "use": "mobile",
            }
        ],
        "gender": "male",
        "birthDate": "1978-02-04",
        "managingOrganization": {
            "display": "Sample Health Primary Care",
        },
    },
}

_ENCOUNTERS: Dict[str, List[Dict]] = {
    "patient-001": [
        {
            "resourceType": "Encounter",
            "id": "encounter-1001",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {"reference": "Patient/patient-001"},
            "period": {
                "start": (_NOW - timedelta(days=32)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": (_NOW - timedelta(days=32, minutes=-30)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
            },
            "reasonCode": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "404640003",
                            "display": "Vertigo",
                        }
                    ],
                    "text": "Positional dizziness when standing",
                }
            ],
            "diagnosis": [
                {
                    "condition": {
                        "display": "Benign paroxysmal positional vertigo",
                    },
                    "rank": 1,
                }
            ],
        },
        {
            "resourceType": "Encounter",
            "id": "encounter-1002",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "EMER",
                "display": "emergency",
            },
            "subject": {"reference": "Patient/patient-001"},
            "period": {
                "start": (_NOW - timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": (_NOW - timedelta(days=180, minutes=-120)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
            },
            "reasonCode": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "29857009",
                            "display": "Migraine",
                        }
                    ],
                    "text": "Severe headache with nausea",
                }
            ],
        },
    ],
    "patient-002": [
        {
            "resourceType": "Encounter",
            "id": "encounter-2001",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {"reference": "Patient/patient-002"},
            "period": {
                "start": (_NOW - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": (_NOW - timedelta(days=14, minutes=-45)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
            },
            "reasonCode": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "271807003",
                            "display": "Fatigue",
                        }
                    ],
                    "text": "Persistent fatigue and malaise",
                }
            ],
        }
    ],
}

_APPOINTMENTS: List[Dict] = []


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _log(operation: str, **payload) -> None:
    """Convenience wrapper for structured log messages."""
    logger.info(
        "Mock FHIR API call",
        extra={
            "component": "mock_fhir",
            "operation": operation,
            "payload": payload,
        },
    )


def list_patients() -> List[Dict]:
    """Return all mock patients."""
    _log("list_patients", count=len(_PATIENTS))
    return list(_PATIENTS.values())


def get_patient(patient_id: str) -> Optional[Dict]:
    """Return a single patient by identifier."""
    patient = _PATIENTS.get(patient_id)
    if patient:
        _log("get_patient", patient_id=patient_id)
    else:
        logger.warning(
            "Mock FHIR API call failed: patient not found",
            extra={"component": "mock_fhir", "operation": "get_patient", "patient_id": patient_id},
        )
    return patient


def list_encounters(patient_id: Optional[str] = None) -> List[Dict]:
    """Return encounters, optionally filtered by patient."""
    if patient_id:
        encounters = _ENCOUNTERS.get(patient_id, [])
        _log("list_encounters", patient_id=patient_id, count=len(encounters))
        return encounters

    encounters = []
    for patient, resources in _ENCOUNTERS.items():
        encounters.extend(resources)
    _log("list_encounters", patient_id="*", count=len(encounters))
    return encounters


def list_appointments(patient_id: Optional[str] = None) -> List[Dict]:
    """Return scheduled mock appointments."""
    if patient_id:
        appointments = [appt for appt in _APPOINTMENTS if appt["participant"][0]["actor"]["reference"] == f"Patient/{patient_id}"]
        _log("list_appointments", patient_id=patient_id, count=len(appointments))
        return appointments

    _log("list_appointments", patient_id="*", count=len(_APPOINTMENTS))
    return list(_APPOINTMENTS)


def create_appointment(
    *,
    patient_id: str,
    appointment_type: str,
    preferred_day: str,
    preferred_time: str,
    reason_summary: str,
    channel: str = "telehealth",
) -> Dict:
    """Create a new mock appointment and return the FHIR Appointment resource."""
    appointment_id = f"appointment-{uuid.uuid4().hex[:8]}"

    start_iso = _format_datetime(preferred_day, preferred_time)
    end_iso = _format_datetime(preferred_day, preferred_time, minutes=30)

    appointment = {
        "resourceType": "Appointment",
        "id": appointment_id,
        "status": "proposed",
        "serviceCategory": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/service-category",
                        "code": "GP",
                        "display": "General Practice",
                    }
                ]
            }
        ],
        "serviceType": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/service-type",
                        "code": "1240",
                        "display": "Telehealth consultation" if channel.lower() == "telehealth" else "In-person consultation",
                    }
                ],
                "text": f"{channel.title()} consultation",
            }
        ],
        "appointmentType": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
                    "code": "FOLLOWUP" if appointment_type.lower() == "follow-up" else "ROUTINE",
                    "display": appointment_type.title(),
                }
            ],
            "text": appointment_type.title(),
        },
        "reasonCode": [
            {
                "text": reason_summary,
            }
        ],
        "start": start_iso,
        "end": end_iso,
        "minutesDuration": 30,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "participant": [
            {
                "actor": {
                    "reference": f"Patient/{patient_id}",
                    "display": _PATIENTS.get(patient_id, {}).get("name", [{}])[0].get("given", ["Patient"])[0],
                },
                "required": "required",
                "status": "needs-action",
            },
            {
                "actor": {
                    "reference": "Practitioner/practitioner-telehealth",
                    "display": "On-call Telehealth Clinician",
                },
                "required": "required",
                "status": "tentative",
            },
        ],
        "extension": [
            {
                "url": "https://health.example.org/fhir/StructureDefinition/appointment-channel",
                "valueString": channel,
            }
        ],
    }

    _APPOINTMENTS.append(appointment)
    _log(
        "create_appointment",
        patient_id=patient_id,
        appointment_id=appointment_id,
        appointment_type=appointment_type,
        channel=channel,
        preferred_day=preferred_day,
        preferred_time=preferred_time,
    )
    return appointment


def _format_datetime(day: str, time_val: str, minutes: int = 0) -> str:
    """Format user-friendly day/time strings into ISO-8601."""
    try:
        base_date = datetime.fromisoformat(day)
    except ValueError:
        try:
            base_date = datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            # Fall back to today's date if parsing fails
            logger.warning(
                "Unable to parse preferred day, defaulting to current date",
                extra={"component": "mock_fhir", "operation": "_format_datetime", "day": day},
            )
            base_date = datetime.now(timezone.utc)

    hour, minute = _parse_time(time_val)
    dt = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    dt += timedelta(minutes=minutes)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_time(time_val: str) -> Tuple[int, int]:
    """Parse various user time formats into hour/minute components."""
    normalized = time_val.strip().lower().replace(".", "")
    if "am" in normalized or "pm" in normalized:
        is_pm = "pm" in normalized
        normalized = normalized.replace("am", "").replace("pm", "").strip()
        hour, minute = _split_time(normalized)
        if is_pm and hour < 12:
            hour += 12
        if not is_pm and hour == 12:
            hour = 0
        return hour, minute

    hour, minute = _split_time(normalized)
    return hour, minute


def _split_time(time_val: str) -> Tuple[int, int]:
    if ":" in time_val:
        hour_str, minute_str = time_val.split(":", 1)
    else:
        hour_str, minute_str = time_val, "00"

    return int(hour_str), int(minute_str)


__all__ = [
    "list_patients",
    "get_patient",
    "list_encounters",
    "list_appointments",
    "create_appointment",
]

