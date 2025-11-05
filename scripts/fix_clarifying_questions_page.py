#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Clarifying Questions page - add actual questions that get asked
"""

import json
import os
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account
from google.api_core import client_options

# Configuration
SERVICE_ACCOUNT_KEY = "key.json"
AGENT_INFO_FILE = "agent_info.json"
LOCATION = "us-central1"

def load_agent_info():
    """Load agent information"""
    with open(AGENT_INFO_FILE, 'r') as f:
        return json.load(f)

def get_client(client_class):
    """Get a Dialogflow CX client with proper endpoint"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY
    )
    client_options_obj = client_options.ClientOptions(
        api_endpoint=f"{LOCATION}-dialogflow.googleapis.com:443"
    )
    return client_class(credentials=credentials, client_options=client_options_obj)

def fix_clarifying_questions():
    """Fix Clarifying Questions page to actually ask questions"""
    
    print("="*60)
    print("Fix Clarifying Questions Page")
    print("="*60)
    print()
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        # Get flow
        flows_client = get_client(dialogflow.FlowsClient)
        request = dialogflow.ListFlowsRequest(parent=agent_name)
        flows = list(flows_client.list_flows(request=request))
        
        flow_name = None
        for flow in flows:
            if flow.display_name == "Default Start Flow":
                flow_name = flow.name
                break
        
        if not flow_name:
            print("[ERROR] Could not find Default Start Flow")
            return False
        
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        # Find pages
        clarifying_page = None
        triage_page = None
        for page in pages:
            if page.display_name == "Clarifying Questions":
                clarifying_page = page
            if page.display_name == "Triage Evaluation":
                triage_page = page
        
        if not clarifying_page:
            print("[ERROR] Clarifying Questions page not found")
            return False
        
        if not triage_page:
            print("[ERROR] Triage Evaluation page not found")
            return False
        
        print("Fixing Clarifying Questions page...")
        print()
        
        # Update entry fulfillment to ask actual questions
        clarifying_page.entry_fulfillment = dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Thank you for providing those details. Let me ask a few clarifying questions to better understand your situation and determine the appropriate level of care.\n\n"
                            "Have you experienced any of the following symptoms along with your headache?"
                        ]
                    )
                )
            ]
        )
        
        # Add form with clarifying questions
        if not clarifying_page.form:
            clarifying_page.form = dialogflow.Form()
        
        if not clarifying_page.form.parameters:
            clarifying_page.form.parameters = []
        
        # Question 1: Associated symptoms
        associated_symptoms_param = None
        param_index = -1
        for i, param in enumerate(clarifying_page.form.parameters):
            if param.display_name == "associated_symptoms":
                associated_symptoms_param = param
                param_index = i
                break
        
        if not associated_symptoms_param:
            associated_symptoms_param = dialogflow.Form.Parameter(
                display_name="associated_symptoms",
                entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                required=True,  # Make required to ensure question is asked
                fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                    initial_prompt_fulfillment=dialogflow.Fulfillment(
                        messages=[
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[
                                        "Have you experienced any of the following along with your symptoms?\n"
                                        "- Vision changes or blurry vision\n"
                                        "- Nausea or vomiting\n"
                                        "- Dizziness or lightheadedness\n"
                                        "- Fever\n"
                                        "- Neck stiffness\n\n"
                                        "You can say 'none', 'no', or list any symptoms you've noticed."
                                    ]
                                )
                            )
                        ]
                    )
                )
            )
            clarifying_page.form.parameters.append(associated_symptoms_param)
            print("  [OK] Added associated symptoms question")
        else:
            # Update existing parameter to be required
            associated_symptoms_param.required = True
            if not associated_symptoms_param.fill_behavior:
                associated_symptoms_param.fill_behavior = dialogflow.Form.Parameter.FillBehavior()
            if not associated_symptoms_param.fill_behavior.initial_prompt_fulfillment:
                associated_symptoms_param.fill_behavior.initial_prompt_fulfillment = dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=[
                                    "Have you experienced any of the following along with your symptoms?\n"
                                    "- Vision changes or blurry vision\n"
                                    "- Nausea or vomiting\n"
                                    "- Dizziness or lightheadedness\n"
                                    "- Fever\n"
                                    "- Neck stiffness\n\n"
                                    "You can say 'none', 'no', or list any symptoms you've noticed."
                                ]
                            )
                        )
                    ]
                )
            print("  [OK] Updated associated symptoms question (now required)")
        
        # Question 2: Triggers or patterns
        triggers_param = None
        for param in clarifying_page.form.parameters:
            if param.display_name == "triggers":
                triggers_param = param
                break
        
        if not triggers_param:
            triggers_param = dialogflow.Form.Parameter(
                display_name="triggers",
                entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                required=False,
                fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                    initial_prompt_fulfillment=dialogflow.Fulfillment(
                        messages=[
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[
                                        "Is there anything specific that seems to trigger or worsen your symptoms? "
                                        "For example, certain activities, positions, or times of day? "
                                        "You can say 'no' or 'nothing specific' if nothing stands out."
                                    ]
                                )
                            )
                        ]
                    )
                )
            )
            clarifying_page.form.parameters.append(triggers_param)
            print("  [OK] Added triggers question")
        
        # Question 3: Impact on daily activities
        impact_param = None
        for param in clarifying_page.form.parameters:
            if param.display_name == "impact_on_activities":
                impact_param = param
                break
        
        if not impact_param:
            impact_param = dialogflow.Form.Parameter(
                display_name="impact_on_activities",
                entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                required=False,
                fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                    initial_prompt_fulfillment=dialogflow.Fulfillment(
                        messages=[
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[
                                        "How are your symptoms affecting your daily activities? "
                                        "Are you able to work, sleep, or perform normal tasks? "
                                        "You can say 'fine', 'some difficulty', or describe the impact."
                                    ]
                                )
                            )
                        ]
                    )
                )
            )
            clarifying_page.form.parameters.append(impact_param)
            print("  [OK] Added impact on activities question")
        
        # Update transition route to Triage Evaluation
        # Only transition after form is complete (which requires answering the first question)
        if not clarifying_page.transition_routes:
            clarifying_page.transition_routes = []
        
        # Remove any existing transition that goes directly to Triage
        clarifying_page.transition_routes = [
            route for route in clarifying_page.transition_routes
            if route.target_page != triage_page.name
        ]
        
        # Add transition when form is complete (after first required question is answered)
        clarifying_page.transition_routes.append(
            dialogflow.TransitionRoute(
                condition='$page.params.status = "FINAL"',
                target_page=triage_page.name
            )
        )
        
        # Also add a route that allows skipping if user explicitly wants to
        # But we'll make it conditional so it doesn't skip automatically
        
        # Note: We'll let the form complete naturally rather than adding intent routes
        # The form will progress after asking questions
        
        print("  [OK] Updated transition routes")
        
        # Update the page
        request = dialogflow.UpdatePageRequest(page=clarifying_page)
        pages_client.update_page(request=request)
        
        print()
        print("[OK] Clarifying Questions page updated")
        print()
        print("Questions added:")
        print("  1. Associated symptoms (vision changes, nausea, etc.)")
        print("  2. Triggers or patterns")
        print("  3. Impact on daily activities")
        print()
        print("Note: All questions are optional - the flow will progress")
        print("      after asking them or if the user says 'no' or 'nothing'.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_clarifying_questions()
    exit(0 if success else 1)

