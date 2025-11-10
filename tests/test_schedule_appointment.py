#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for mock FHIR endpoints and schedule appointment webhook handler.
"""

import unittest
from datetime import date

from rag_simplified import app


class ScheduleAppointmentTests(unittest.TestCase):
    """Validate the mock FHIR API and appointment workflow."""

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_fhir_patients_endpoint(self):
        response = self.client.get("/fhir/patients")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["resourceType"], "Bundle")
        self.assertGreaterEqual(data["total"], 1)

    def test_schedule_appointment_flow(self):
        today = date.today().isoformat()

        # Baseline appointment count
        before = self.client.get("/fhir/appointments").get_json()
        before_total = before["total"]

        payload = {
            "intentInfo": {"displayName": "Schedule Appointment"},
            "fulfillmentInfo": {"tag": "schedule_appointment"},
            "sessionInfo": {
                "parameters": {
                    "patient_id": "patient-001",
                    "preferred_day": today,
                    "preferred_time": "10:00",
                    "appointment_type": "telehealth",
                    "appointment_channel": "telehealth",
                    "symptom_type": "dizziness",
                    "duration": "2 days",
                }
            },
            "text": "I've been dizzy for two days — can I book a telehealth appointment?",
        }

        response = self.client.post("/webhook", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("fulfillment_response", data)
        messages = data["fulfillment_response"]["messages"]
        self.assertGreaterEqual(len(messages), 1)
        confirmation = messages[0]["text"]["text"][0].lower()
        self.assertIn("scheduled", confirmation)

        payload_data = data["payload"]
        appointment = payload_data["fhirAppointment"]
        self.assertEqual(appointment["resourceType"], "Appointment")
        self.assertEqual(appointment["participant"][0]["actor"]["reference"], "Patient/patient-001")

        # Ensure appointment count increased
        after = self.client.get("/fhir/appointments").get_json()
        self.assertEqual(after["total"], before_total + 1)


if __name__ == "__main__":
    unittest.main()

