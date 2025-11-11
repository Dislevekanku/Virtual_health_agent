#!/usr/bin/env python3
"""
Virtual Health Assistant - Multi-Agent Orchestration (Phase 1)

Implements a deterministic pipeline with specialized agents:

1. IntakeAgent   - parses raw user utterances into structured symptom JSON.
2. ReasoningAgent - proposes triage/urgency reasoning from intake + context.
3. DataAgent      - retrieves mock FHIR context via a FunctionTool.
4. ResponseAgent  - composes the final response with citations & guidance.

Agents are orchestrated with Google ADK (Sequential + Parallel agents).
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Dict, List

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.models.google_llm import Gemini
from google.genai import types

from mock_fhir import (
    load_patient,
    load_encounters,
    load_observations,
)


# ---------------------------------------------------------------------------
# Retry configuration shared across Gemini-backed agents
# ---------------------------------------------------------------------------
retry_config = types.HttpRetryOptions(
    attempts=3,
    initial_delay=1,
    http_status_codes=[429, 500, 503],
)

PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"


# ---------------------------------------------------------------------------
# DataAgent tool: fetch patient context from mock FHIR layer
# ---------------------------------------------------------------------------
def fetch_patient_context(intake_json: str = "") -> Dict[str, Any]:
    """Return patient context for downstream reasoning."""

    intake_data: Dict[str, Any]
    try:
        intake_data = json.loads(intake_json) if intake_json else {}
    except json.JSONDecodeError:
        intake_data = {}

    patient_id = intake_data.get("patient_id") or "patient-001"

    patient = load_patient(patient_id)
    encounters = load_encounters(patient_id)
    observations = load_observations(patient_id)

    return {
        "patient_id": patient_id,
        "patient": patient,
        "recent_encounters": encounters[:3],
        "recent_observations": observations[:5],
    }


def check_availability(patient_id: str = "patient-001", date_range: str = "next-7-days") -> Dict[str, Any]:
    """Return mock scheduling availability for a patient."""

    from mock_fhir import load_schedule_slots

    slots: List[Dict[str, Any]] = load_schedule_slots(patient_id, date_range)
    return {
        "patient_id": patient_id,
        "date_range": date_range,
        "available_slots": slots,
    }


patient_context_tool = FunctionTool(fetch_patient_context)

schedule_tool = FunctionTool(check_availability)

# ---------------------------------------------------------------------------
# Agent definitions
# ---------------------------------------------------------------------------
intake_agent = Agent(
    name="IntakeAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=retry_config,
    ),
    instruction="""
You are an intake parser. Read the user's latest message (context key: user_input) and convert it into JSON with keys:
  - symptom: short description of the primary concern
  - duration: free-text duration from the user (or "unknown")
  - severity: integer 1-10 if stated, else "unknown"
  - additional_symptoms: list of extra symptoms mentioned (strings)
  - free_text: copy of the user's message
Return JSON only with double quotes (no Markdown fences).
""",
    output_key="intake_json",
)

data_agent = Agent(
    name="DataAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=retry_config,
    ),
    instruction="""
Use the tool `fetch_patient_context` with the latest intake JSON to retrieve patient context.
Return JSON with a single key `patient_context` whose value is the tool result.
""",
    output_key="patient_context",
    tools=[patient_context_tool],
)

reasoning_agent = Agent(
    name="ReasoningAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=retry_config,
    ),
    instruction="""
You are a clinical triage assistant. Using the structured intake data {intake_json}
and optional patient context {patient_context}, classify urgency as one of: low, medium, high.
Provide a JSON object with keys:
  - urgency: low | medium | high
  - reasons: list with two short bullet-style justification strings
If information is missing, assume cautious defaults. Return JSON only.
""",
    output_key="triage",
)

response_agent = Agent(
    name="ResponseAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=retry_config,
    ),
    instruction="""
Compose the final response leveraging:
  - Intake JSON: {intake_json}
  - Triage decision: {triage}
  - Patient context: {patient_context}

Return a JSON payload with keys:
  - message: empathetic, evidence-aware guidance for the patient (plain text, no Markdown bullets).
  - triage_level: echo triage.urgency.
  - reasoning: triage.reasons
  - intake: parsed intake_json (as JSON).
  - patient_context: summarized view (id, recent encounters summaries).
  - schedule: call the tool `check_availability` on the patient's id if an appointment might be needed; include available slots.
  - citations: array of strings referencing clinical guidance sources (use any available, else empty).
""",
    output_key="response_payload",
    tools=[schedule_tool],
)


# ---------------------------------------------------------------------------
# Orchestration: Intake → Data → Reasoning → Response
# ---------------------------------------------------------------------------
root_agent = SequentialAgent(
    name="VHA_Pipeline",
    sub_agents=[intake_agent, data_agent, reasoning_agent, response_agent],
)

runner = InMemoryRunner(agent=root_agent)


def run_virtual_health_assistant(user_message: str) -> Dict[str, Any]:
    """
    Execute the multi-agent pipeline and return the structured response payload.
    """
    user_id = "demo-user"
    session_id = f"session-{uuid.uuid4()}"

    async def _ensure_session():
        session = await runner.session_service.get_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if not session:
            await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id=user_id,
                session_id=session_id,
            )

    asyncio.run(_ensure_session())

    message = types.Content(
        role="user",
        parts=[types.Part(text=user_message)],
    )

    final_event = None
    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if (
            getattr(event, "author", "") == response_agent.name
            and event.is_final_response()
        ):
            final_event = event

    if not final_event or not final_event.content:
        return {"error": "Pipeline produced no response"}

    text_parts = []
    for part in final_event.content.parts or []:
        if part.text:
            text_parts.append(part.text)
    response_text = "".join(text_parts).strip()

    if response_text:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            json_start = response_text.find("{")
            if json_start != -1:
                candidate = response_text[json_start:]
                try:
                    parsed = json.loads(candidate)
                    parsed.setdefault("raw_response_prefix", response_text[:json_start].strip())
                    return parsed
                except json.JSONDecodeError:
                    pass
            return {"raw_response": response_text}

    return {"error": "No textual response from ResponseAgent"}


if __name__ == "__main__":
    demo_input = "I've been feeling lightheaded for two days with mild nausea."
    output = run_virtual_health_assistant(demo_input)
    print(json.dumps(output, indent=2))

