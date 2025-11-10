#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add or update a 'Schedule Appointment' intent and appointment scheduling page.

This script:
1. Ensures the Schedule Appointment intent exists with representative phrases.
2. Creates an Appointment Scheduling page with prompts for preferred day/time.
3. Routes the Summary page to the appointment page when the intent is detected.
"""

from __future__ import annotations

import json
import sys
from typing import Optional

from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account
from google.api_core import client_options
from google.protobuf import field_mask_pb2

SERVICE_ACCOUNT_KEY = "key.json"
AGENT_INFO_FILE = "agent_info.json"
LOCATION = "us-central1"


def load_agent_info():
    with open(AGENT_INFO_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def make_client(client_class):
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY)
    opts = client_options.ClientOptions(api_endpoint=f"{LOCATION}-dialogflow.googleapis.com:443")
    return client_class(credentials=credentials, client_options=opts)


def ensure_schedule_intent(agent_name: str, intents_client: dialogflow.IntentsClient) -> dialogflow.Intent:
    """Create the Schedule Appointment intent if it does not already exist."""
    existing_intents = list(
        intents_client.list_intents(
            request=dialogflow.ListIntentsRequest(parent=agent_name)
        )
    )

    for intent in existing_intents:
        if intent.display_name.lower() == "schedule appointment":
            print("✔ Schedule Appointment intent already exists")
            return intent

    training_phrases = [
        "Can I schedule a telehealth appointment?",
        "I need to book a follow-up visit",
        "Please set up an appointment for me",
        "I'd like to see a doctor this week",
        "Book me for a video visit tomorrow morning",
        "Can you arrange a telehealth slot on Friday afternoon?",
    ]

    intent = dialogflow.Intent(
        display_name="Schedule Appointment",
        priority=500000,
        training_phrases=[
            dialogflow.Intent.TrainingPhrase(
                parts=[dialogflow.Intent.TrainingPhrase.Part(text=phrase)]
            )
            for phrase in training_phrases
        ],
        parameters=[
            dialogflow.Intent.Parameter(
                id="preferred_day",
                entity_type="projects/-/locations/-/agents/-/entityTypes/sys.date",
                is_list=False,
            ),
            dialogflow.Intent.Parameter(
                id="preferred_time",
                entity_type="projects/-/locations/-/agents/-/entityTypes/sys.time",
                is_list=False,
            ),
            dialogflow.Intent.Parameter(
                id="appointment_type",
                entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                is_list=False,
            ),
        ],
    )

    created = intents_client.create_intent(
        request=dialogflow.CreateIntentRequest(parent=agent_name, intent=intent)
    )
    print("✔ Created Schedule Appointment intent")
    return created


def get_flow(agent_name: str, display_name: str, flows_client: dialogflow.FlowsClient) -> Optional[dialogflow.Flow]:
    flows = flows_client.list_flows(request=dialogflow.ListFlowsRequest(parent=agent_name))
    for flow in flows:
        if flow.display_name == display_name:
            return flow
    return None


def get_page(flow_name: str, display_name: str, pages_client: dialogflow.PagesClient) -> Optional[dialogflow.Page]:
    pages = pages_client.list_pages(request=dialogflow.ListPagesRequest(parent=flow_name))
    for page in pages:
        if page.display_name == display_name:
            return page
    return None


def ensure_appointment_page(
    flow_name: str,
    pages_client: dialogflow.PagesClient,
    summary_page: dialogflow.Page,
) -> dialogflow.Page:
    """Ensure the Appointment Scheduling page exists with prompts."""
    existing_page = get_page(flow_name, "Appointment Scheduling", pages_client)
    day_prompt = (
        "What day works best for your appointment? You can say something like "
        "'this Thursday', 'tomorrow', or give a specific date."
    )
    time_prompt = (
        "Great, and what time of day works best for you? Morning, afternoon, or a specific time like 10 AM?"
    )

    if existing_page:
        print("✔ Appointment Scheduling page already exists")
        return existing_page

    appointment_page = dialogflow.Page(
        display_name="Appointment Scheduling",
        entry_fulfillment=dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "I'd be happy to schedule that for you. "
                            "Let me collect a couple of quick details."
                        ]
                    )
                )
            ]
        ),
        form=dialogflow.Form(
            parameters=[
                dialogflow.Form.Parameter(
                    display_name="preferred_day",
                    entity_type="projects/-/locations/-/agents/-/entityTypes/sys.date",
                    required=True,
                    fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                        initial_prompt_fulfillment=dialogflow.Fulfillment(
                            messages=[
                                dialogflow.ResponseMessage(
                                    text=dialogflow.ResponseMessage.Text(text=[day_prompt])
                                )
                            ]
                        )
                    ),
                ),
                dialogflow.Form.Parameter(
                    display_name="preferred_time",
                    entity_type="projects/-/locations/-/agents/-/entityTypes/sys.time",
                    required=True,
                    fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                        initial_prompt_fulfillment=dialogflow.Fulfillment(
                            messages=[
                                dialogflow.ResponseMessage(
                                    text=dialogflow.ResponseMessage.Text(text=[time_prompt])
                                )
                            ]
                        )
                    ),
                ),
            ]
        ),
        transition_routes=[
            dialogflow.TransitionRoute(
                condition="$page.params.status = \"FINAL\"",
                trigger_fulfillment=dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=[
                                    "Thanks! I'll pass this to the scheduling assistant to lock in your appointment."
                                ]
                            )
                        )
                    ]
                ),
                target_page=summary_page.name,
            )
        ],
    )

    created_page = pages_client.create_page(
        request=dialogflow.CreatePageRequest(parent=flow_name, page=appointment_page)
    )
    print("✔ Created Appointment Scheduling page")
    return created_page


def ensure_summary_route(
    summary_page: dialogflow.Page,
    schedule_intent: dialogflow.Intent,
    appointment_page: dialogflow.Page,
    pages_client: dialogflow.PagesClient,
):
    """Add a transition route from Summary to the appointment page."""
    existing_routes = summary_page.transition_routes or []
    for route in existing_routes:
        if route.intent == schedule_intent.name:
            print("✔ Summary page already routes to Appointment Scheduling")
            return

    new_route = dialogflow.TransitionRoute(
        intent=schedule_intent.name,
        trigger_fulfillment=dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Absolutely, let's set up an appointment for you."
                        ]
                    )
                )
            ]
        ),
        target_page=appointment_page.name,
    )

    summary_page.transition_routes.append(new_route)
    pages_client.update_page(
        request=dialogflow.UpdatePageRequest(
            page=summary_page,
            update_mask=field_mask_pb2.FieldMask(paths=["transition_routes"]),
        )
    )
    print("✔ Added Schedule Appointment transition on Summary page")


def main():
    try:
        agent_info = load_agent_info()
    except FileNotFoundError:
        print("[ERROR] agent_info.json not found. Please configure the agent first.")
        sys.exit(1)

    agent_name = agent_info["agent_name"]

    intents_client = make_client(dialogflow.IntentsClient)
    flows_client = make_client(dialogflow.FlowsClient)
    pages_client = make_client(dialogflow.PagesClient)

    schedule_intent = ensure_schedule_intent(agent_name, intents_client)

    default_flow = get_flow(agent_name, "Default Start Flow", flows_client)
    if not default_flow:
        print("[ERROR] Could not locate Default Start Flow.")
        sys.exit(1)

    summary_page = get_page(default_flow.name, "Summary", pages_client)
    if not summary_page:
        print("[ERROR] Could not locate Summary page.")
        sys.exit(1)

    appointment_page = ensure_appointment_page(
        default_flow.name,
        pages_client,
        summary_page,
    )

    ensure_summary_route(summary_page, schedule_intent, appointment_page, pages_client)

    print("\nSchedule Appointment flow configured successfully.")


if __name__ == "__main__":
    main()

