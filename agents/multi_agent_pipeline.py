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
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List

from google.adk.agents import Agent, SequentialAgent, LoopAgent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.models.google_llm import Gemini
from google.genai import types

try:
    from google.cloud import logging as gcloud_logging
except ImportError:
    gcloud_logging = None

try:
    from google.cloud import firestore  # type: ignore
except ImportError:
    firestore = None

try:
    from google.cloud import monitoring_v3  # type: ignore
except ImportError:
    monitoring_v3 = None

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

if gcloud_logging is not None:
    try:
        logging_client = gcloud_logging.Client()
        LOGGER = logging_client.logger("vha-interactions")
    except Exception:
        LOGGER = None
else:
    LOGGER = None

if firestore is not None:
    try:
        firestore_client = firestore.Client()
        FIRESTORE_SERVER_TIMESTAMP = firestore.SERVER_TIMESTAMP
        FirestoreArrayUnion = firestore.ArrayUnion
    except Exception:
        firestore_client = None
        FIRESTORE_SERVER_TIMESTAMP = None
        FirestoreArrayUnion = None
else:
    firestore_client = None
    FIRESTORE_SERVER_TIMESTAMP = None
    FirestoreArrayUnion = None

LOCAL_SESSION_STORE: Dict[str, List[Dict[str, Any]]] = {}

if monitoring_v3 is not None:
    try:
        monitoring_client = monitoring_v3.MetricServiceClient()
        MONITORING_PROJECT = f"projects/{PROJECT_ID}"
    except Exception:
        monitoring_client = None
        MONITORING_PROJECT = None
else:
    monitoring_client = None
    MONITORING_PROJECT = None

MOCK_RESPONSE_MAP: List[Dict[str, Any]] = [
    {
        "trigger": "headache for 2 days",
        "response": {
            "message": (
                "Thanks for sharing. Based on your description, this is considered a low urgency situation. "
                "Please make sure you get plenty of hydration advice by drinking fluids, resting in a quiet space, "
                "and using over-the-counter pain relievers if appropriate. If you'd like, I can offer telehealth support "
                "to review your symptoms or help schedule a visit if things change."
            ),
            "triage_level": "low",
            "reasoning": [
                "Two-day headache without red flags typically indicates a low urgency scenario.",
                "Hydration and rest often relieve mild tension headaches."
            ],
            "intake": {
                "symptom": "headache",
                "duration": "2 days",
                "severity": "mild",
                "additional_symptoms": [],
                "free_text": "I have had a headache for 2 days"
            },
            "schedule": {
                "telehealth": "2025-11-15T15:00:00Z",
                "availability": ["telehealth", "in-person"]
            },
            "citations": ["self-care-headache-guideline"],
            "meta": {
                "critic_score": 9.2,
                "latency_ms": 4.5
            }
        },
    },
    {
        "trigger": "chest pain and shortness of breath",
        "response": {
            "message": (
                "Because you are experiencing chest pain with shortness of breath, this is classified as a high urgency situation. "
                "Please call 911 or emergency services immediately, and do not drive yourself."
            ),
            "triage_level": "high",
            "reasoning": [
                "Chest pain combined with shortness of breath is a medical emergency.",
                "Immediate evaluation is recommended to rule out cardiac causes."
            ],
            "intake": {
                "symptom": "chest pain",
                "duration": "unknown",
                "severity": "severe",
                "additional_symptoms": ["shortness of breath"],
                "free_text": "I have chest pain and shortness of breath"
            },
            "schedule": {
                "instructions": "call_911"
            },
            "citations": ["emergency-cardiac-guideline"],
            "meta": {
                "critic_score": 9.8,
                "latency_ms": 3.0
            }
        },
    },
]


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


def approve_response(message: str = "", tool_context=None) -> Dict[str, Any]:
    """Escalate loop when the critique is satisfactory."""
    if tool_context is not None:
        tool_context.actions.escalate = True
    return {"status": "approved", "notes": message}


approve_tool = FunctionTool(approve_response)


def record_metrics(triage_level: str, latency_ms: float) -> None:
    if monitoring_client is None or MONITORING_PROJECT is None:
        return

    end_seconds = int(time.time())
    end_nanos = int((time.time() - end_seconds) * 1e9)

    interval = monitoring_v3.TimeInterval(
        end_time={"seconds": end_seconds, "nanos": end_nanos},
    )

    def _build_series(metric_type: str, value_field: str, value: float):
        typed_value = monitoring_v3.TypedValue(
            **{value_field: value}
        )
        point = monitoring_v3.Point(interval=interval, value=typed_value)
        ts = monitoring_v3.TimeSeries()
        ts.metric.type = metric_type
        ts.resource.type = "global"
        ts.resource.labels["project_id"] = PROJECT_ID
        ts.points.append(point)
        return ts

    series = [
        _build_series(
            "custom.googleapis.com/vha/requests_total",
            "int64_value",
            1,
        )
    ]

    if triage_level and triage_level.lower() == "high":
        series.append(
            _build_series(
                "custom.googleapis.com/vha/triage_high_count",
                "int64_value",
                1,
            )
        )

    series.append(
        _build_series(
            "custom.googleapis.com/vha/request_latency_ms",
            "double_value",
            latency_ms,
        )
    )

    try:
        monitoring_client.create_time_series(
            name=MONITORING_PROJECT,
            time_series=series,
        )
    except Exception:
        pass

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

draft_response_agent = Agent(
    name="DraftResponseAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=retry_config,
    ),
    instruction="""
Compose an initial patient-facing response leveraging:
  - Intake JSON: {intake_json}
  - Triage decision: {triage}
  - Patient context: {patient_context}

Guardrails:
  - Use an empathetic tone and acknowledge the patient's concern.
  - Do NOT provide definitive diagnoses or medication dosages; use supportive, cautious language.
  - Explicitly mention the triage level (e.g., "This is considered low urgency").
  - Offer at least one actionable next step aligned with the triage level.
  - If citations exist, reference them in the message (e.g., "According to [source]").

Return JSON with keys:
  - message: empathetic guidance for the patient (plain text, no Markdown bullets).
  - triage_level: echo triage.urgency.
  - reasoning: triage.reasons
  - intake: parsed intake_json (JSON object).
  - patient_context: summarized view (id, recent encounters summaries).
  - schedule: call the tool `check_availability` on the patient's id if an appointment might be needed; include available slots.
  - citations: array of strings referencing clinical guidance sources (use any available).
Return JSON only.
""",
    output_key="draft_response",
    tools=[schedule_tool],
)

critic_agent = Agent(
    name="CriticAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=retry_config,
    ),
    instruction="""
You are the safety critic for a clinical triage assistant. Review the draft response {draft_response} and ensure it follows these guardrails:
1. Safety: No definitive diagnoses or prescriptive medication dosages; escalation instructions must be present for red flags.
2. Completeness: Message must explicitly mention the triage level and provide at least one concrete next-step action.
3. Tone: Response must sound empathetic and patient-facing.
4. Citations: If citations are provided, the message should reference them.

Scoring rules:
- Start with score = 10
- Subtract 3 points for each safety breach (diagnosis certainty, missing escalation when needed, etc.)
- Subtract 2 points if no actionable next step is provided
- Subtract 1 point if tone is not empathetic or patient-friendly
Score floor is 0.

Return strict JSON with keys:
{
  "score": <number>,
  "issues": ["..."],
  "approved": true/false,
  "summary": "short sentence"
}
Approved must be true ONLY if score >= 8 and no safety issues remain.
""",
    output_key="critique",
)

refiner_agent = Agent(
    name="RefinerAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=retry_config,
    ),
    instruction="""
You refine the patient response using the current draft {draft_response} and critique {critique}.
Guardrails you MUST enforce in the revised JSON:
- Maintain empathetic, concise tone.
- Do NOT provide definitive diagnoses or medication dosages.
- Message must explicitly mention the triage level.
- Provide at least one actionable next step aligned with the triage level (self-care, telehealth, emergency, etc.).
- Reference citations/sources if they exist in the draft.
- Encourage escalation when red-flag symptoms are present.

If critique.approved is true OR (critique.score >= 8 with no listed issues), call the `approve_response` tool with a brief note and return the original draft JSON unchanged.
Otherwise, update the draft JSON (keeping the same keys: message, triage_level, reasoning, intake, patient_context, schedule, citations, meta) so that all guardrails are satisfied.
Return JSON only.
""",
    output_key="draft_response",
    tools=[approve_tool],
)

final_response_agent = Agent(
    name="FinalResponseAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        project=PROJECT_ID,
        location=LOCATION,
        retry_options=retry_config,
    ),
    instruction="""
You are a clinical triage assistant speaking to patients.
Requirements for the final patient-facing response derived from {draft_response}:
- Maintain an empathetic, concise tone and acknowledge the patient's concern.
- NEVER provide a definitive diagnosis or medication dosage; use cautious language ("might", "could").
- Clearly state the triage level (e.g., "Your situation is classified as medium urgency").
- Offer at least one actionable next step appropriate to the triage level (self-care, telehealth, call emergency, etc.).
- If citations are supplied in the draft, reference them explicitly (e.g., "According to [source]").
- Encourage escalation when red-flag symptoms are present.
- Keep the JSON structure identical to the draft response (message, triage_level, reasoning, intake, patient_context, schedule, citations, meta).
Return JSON only with double quotes and no surrounding commentary.
""",
    output_key="response_payload",
)


# ---------------------------------------------------------------------------
# Orchestration: Intake → Data → Reasoning → Draft → Loop(Critic+Refiner) → Final
# ---------------------------------------------------------------------------
loop_agent = LoopAgent(
    name="QualityLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=3,
)

root_agent = SequentialAgent(
    name="VHA_Pipeline",
    sub_agents=[
        intake_agent,
        data_agent,
        reasoning_agent,
        draft_response_agent,
        loop_agent,
        final_response_agent,
    ],
)

runner = InMemoryRunner(agent=root_agent)


def run_virtual_health_assistant(
    user_message: str, session_id: str | None = None
) -> Dict[str, Any]:
    """
    Execute the multi-agent pipeline and return the structured response payload.
    """
    pipeline_mode = os.getenv("VHA_PIPELINE_MODE", "live").lower()
    if pipeline_mode == "mock":
        return _run_virtual_health_assistant_mock(user_message, session_id)

    start_time = time.time()
    user_id = "demo-user"
    session_id = session_id or f"session-{uuid.uuid4()}"

    recent_history = []
    if firestore_client is not None:
        try:
            doc = (
                firestore_client.collection("sessions")
                .document(session_id)
                .get()
            )
            if doc.exists:
                history = doc.to_dict().get("history", [])
                recent_history = history[-5:]
        except Exception:
            recent_history = []
    else:
        recent_history = LOCAL_SESSION_STORE.get(session_id, [])[-5:]

    history_text = ""
    if recent_history:
        snippets = []
        for entry in recent_history:
            snippets.append(
                f"User: {entry.get('user_input','')}\nResponse: {entry.get('response','')}\n"
            )
        history_text = "\nRecent conversation history:\n" + "\n".join(snippets)

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

    composed_message = user_message
    if history_text:
        composed_message = f"{history_text}\nCurrent user input: {user_message}"

    message = types.Content(
        role="user",
        parts=[types.Part(text=composed_message)],
    )

    final_event = None
    try:
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            if (
                getattr(event, "author", "") == final_response_agent.name
                and event.is_final_response()
            ):
                final_event = event
    except RuntimeError as runtime_error:
        fallback = {
            "error": f"Pipeline runtime error: {runtime_error}",
            "session_id": session_id,
        }
        latency = (time.time() - start_time) * 1000.0
        _log_and_persist(session_id, user_message, fallback, latency)
        return fallback

    if not final_event or not final_event.content:
        fallback = {"error": "Pipeline produced no response", "session_id": session_id}
        latency = (time.time() - start_time) * 1000.0
        _log_and_persist(session_id, user_message, fallback, latency)
        return fallback

    text_parts = []
    for part in final_event.content.parts or []:
        if part.text:
            text_parts.append(part.text)
    response_text = "".join(text_parts).strip()

    if response_text:
        try:
            result_payload = json.loads(response_text)
            result_payload["session_id"] = session_id
            latency = (time.time() - start_time) * 1000.0
            meta = result_payload.setdefault("meta", {})
            meta.setdefault("latency_ms", latency)
            meta.setdefault("critic_score", None)
            _log_and_persist(session_id, user_message, result_payload, latency)
            return result_payload
        except json.JSONDecodeError:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```"):
                first_newline = cleaned_text.find("\n")
                last_ticks = cleaned_text.rfind("```")
                if first_newline != -1 and last_ticks != -1:
                    cleaned_text = cleaned_text[first_newline + 1:last_ticks].strip()
            if cleaned_text != response_text:
                try:
                    parsed = json.loads(cleaned_text)
                    parsed["session_id"] = session_id
                    latency = (time.time() - start_time) * 1000.0
                    meta = parsed.setdefault("meta", {})
                    meta.setdefault("latency_ms", latency)
                    meta.setdefault("critic_score", None)
                    _log_and_persist(session_id, user_message, parsed, latency)
                    return parsed
                except json.JSONDecodeError:
                    response_text = cleaned_text
            json_start = response_text.find("{")
            if json_start != -1:
                candidate = response_text[json_start:]
                try:
                    parsed = json.loads(candidate)
                    parsed.setdefault("raw_response_prefix", response_text[:json_start].strip())
                    parsed["session_id"] = session_id
                    latency = (time.time() - start_time) * 1000.0
                    meta = parsed.setdefault("meta", {})
                    meta.setdefault("latency_ms", latency)
                    meta.setdefault("critic_score", None)
                    _log_and_persist(session_id, user_message, parsed, latency)
                    return parsed
                except json.JSONDecodeError:
                    pass
            fallback = {
                "raw_response": response_text,
                "session_id": session_id,
                "meta": {
                    "latency_ms": (time.time() - start_time) * 1000.0,
                    "critic_score": None,
                },
            }
            latency = (time.time() - start_time) * 1000.0
            _log_and_persist(session_id, user_message, fallback, latency)
            return fallback

    latency = (time.time() - start_time) * 1000.0
    fallback = {
        "error": "No textual response from ResponseAgent",
        "session_id": session_id,
        "meta": {"latency_ms": latency, "critic_score": None},
    }
    latency = (time.time() - start_time) * 1000.0
    _log_and_persist(session_id, user_message, fallback, latency)
    return fallback


def _log_and_persist(
    session_id: str,
    user_text: str,
    response_payload: Dict[str, Any],
    latency_ms: float,
) -> None:
    intake = response_payload.get("intake", {})
    triage_level = response_payload.get("triage_level")

    if LOGGER is not None:
        try:
            LOGGER.log_struct(
                {
                    "session_id": session_id,
                    "user_input": user_text,
                    "intake": intake,
                    "triage_level": triage_level,
                    "final_response": response_payload.get("message"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "latency_ms": latency_ms,
                }
            )
        except Exception:
            pass

    if firestore_client is not None:
        try:
            turn_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_input": user_text,
                "response": response_payload.get("message"),
                "triage_level": triage_level,
                "reasoning": response_payload.get("reasoning", []),
            }
            session_ref = firestore_client.collection("sessions").document(
                session_id
            )
            if FIRESTORE_SERVER_TIMESTAMP is not None and FirestoreArrayUnion is not None:
                session_ref.set(
                    {
                        "session_id": session_id,
                        "updated_at": FIRESTORE_SERVER_TIMESTAMP,
                        "history": FirestoreArrayUnion([turn_entry]),
                    },
                    merge=True,
                )
        except Exception:
            pass
    else:
        LOCAL_SESSION_STORE.setdefault(session_id, []).append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "user_input": user_text,
                "response": response_payload.get("message"),
                "triage_level": triage_level,
                "reasoning": response_payload.get("reasoning", []),
            }
        )

    record_metrics(triage_level or "", latency_ms)


def _run_virtual_health_assistant_mock(
    user_message: str, session_id: str | None
) -> Dict[str, Any]:
    session_id = session_id or f"mock-{uuid.uuid4()}"
    lower_text = user_message.lower()
    for entry in MOCK_RESPONSE_MAP:
        if entry["trigger"] in lower_text:
            response = json.loads(json.dumps(entry["response"]))
            response["session_id"] = session_id
            meta = response.setdefault("meta", {})
            meta.setdefault("latency_ms", 2.0)
            meta.setdefault("critic_score", 9.0)
            return response

    default_response = {
        "message": "Based on what you shared, this is treated as a medium urgency situation. Please rest, stay hydrated, and monitor your symptoms closely. If anything worsens, arrange a telehealth visit or urgent evaluation.",
        "triage_level": "medium",
        "reasoning": ["Generic guidance supplied in mock mode."],
        "intake": {
            "symptom": "unspecified",
            "duration": "unknown",
            "severity": "unknown",
            "additional_symptoms": [],
            "free_text": user_message,
        },
        "schedule": {
            "telehealth": "2025-11-15T09:00:00Z",
        },
        "citations": [],
        "session_id": session_id,
        "meta": {
            "critic_score": 8.5,
            "latency_ms": 1.0,
        },
    }
    return default_response


if __name__ == "__main__":
    demo_input = "I've been feeling lightheaded for two days with mild nausea."
    output = run_virtual_health_assistant(demo_input)
    print(json.dumps(output, indent=2))

