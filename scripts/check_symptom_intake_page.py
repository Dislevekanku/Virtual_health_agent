#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Symptom Intake page configuration to see why it's being skipped
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

def check_and_fix_symptom_intake():
    """Check Symptom Intake page and fix if needed"""
    
    print("="*60)
    print("Check Symptom Intake Page Configuration")
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
        
        # Get pages
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        symptom_intake_page = None
        for page in pages:
            if page.display_name == "Symptom Intake":
                symptom_intake_page = page
                break
        
        if not symptom_intake_page:
            print("[ERROR] Symptom Intake page not found")
            return False
        
        print("Symptom Intake Page Configuration:")
        print(f"  Page Name: {symptom_intake_page.display_name}")
        print()
        
        # Check entry fulfillment
        if symptom_intake_page.entry_fulfillment:
            print("  Entry Fulfillment: Present")
            if symptom_intake_page.entry_fulfillment.messages:
                for msg in symptom_intake_page.entry_fulfillment.messages:
                    if msg.text:
                        text = " ".join(msg.text.text) if msg.text.text else ""
                        print(f"    Message: {text[:100]}")
        else:
            print("  Entry Fulfillment: None")
        print()
        
        # Check form parameters
        if symptom_intake_page.form and symptom_intake_page.form.parameters:
            print(f"  Form Parameters: {len(symptom_intake_page.form.parameters)}")
            for param in symptom_intake_page.form.parameters:
                print(f"    - {param.display_name}")
                print(f"      Required: {param.required}")
                print(f"      Entity Type: {param.entity_type}")
                if param.fill_behavior and param.fill_behavior.initial_prompt_fulfillment:
                    if param.fill_behavior.initial_prompt_fulfillment.messages:
                        for msg in param.fill_behavior.initial_prompt_fulfillment.messages:
                            if msg.text:
                                text = " ".join(msg.text.text) if msg.text.text else ""
                                print(f"      Prompt: {text[:80]}")
        else:
            print("  Form Parameters: None or empty")
        print()
        
        # Check transition routes
        if symptom_intake_page.transition_routes:
            print(f"  Transition Routes: {len(symptom_intake_page.transition_routes)}")
            for i, route in enumerate(symptom_intake_page.transition_routes, 1):
                print(f"    Route {i}:")
                if route.condition:
                    print(f"      Condition: {route.condition}")
                if route.target_page:
                    # Find target page name
                    target_name = "Unknown"
                    for page in pages:
                        if page.name == route.target_page:
                            target_name = page.display_name
                            break
                    print(f"      Target: {target_name}")
        else:
            print("  Transition Routes: None")
        print()
        
        # Fix: Make sure parameters are required and form doesn't auto-complete
        print("Fixing Symptom Intake page...")
        
        needs_update = False
        
        if not symptom_intake_page.form:
            symptom_intake_page.form = dialogflow.Form()
            symptom_intake_page.form.parameters = []
            needs_update = True
        
        # Ensure duration parameter exists and is properly configured
        duration_param = None
        for param in symptom_intake_page.form.parameters:
            if param.display_name == "duration":
                duration_param = param
                break
        
        if duration_param:
            # Make it required so it doesn't skip
            if not duration_param.required:
                duration_param.required = True
                needs_update = True
                print("  [OK] Made duration parameter required")
            
            # Ensure it has a prompt
            if not duration_param.fill_behavior:
                duration_param.fill_behavior = dialogflow.Form.Parameter.FillBehavior()
                needs_update = True
            
            if not duration_param.fill_behavior.initial_prompt_fulfillment:
                duration_param.fill_behavior.initial_prompt_fulfillment = dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=["When did this symptom start? How long have you been experiencing it?"]
                            )
                        )
                    ]
                )
                needs_update = True
                print("  [OK] Added prompt for duration parameter")
        else:
            # Add duration parameter
            duration_param = dialogflow.Form.Parameter(
                display_name="duration",
                entity_type="projects/-/locations/-/agents/-/entityTypes/sys.duration",
                required=True,
                fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                    initial_prompt_fulfillment=dialogflow.Fulfillment(
                        messages=[
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=["When did this symptom start? How long have you been experiencing it?"]
                                )
                            )
                        ]
                    )
                )
            )
            symptom_intake_page.form.parameters.append(duration_param)
            needs_update = True
            print("  [OK] Added duration parameter")
        
        # Ensure severity parameter exists and is properly configured
        severity_param = None
        for param in symptom_intake_page.form.parameters:
            if param.display_name == "severity":
                severity_param = param
                break
        
        if severity_param:
            # Make it required
            if not severity_param.required:
                severity_param.required = True
                needs_update = True
                print("  [OK] Made severity parameter required")
            
            # Ensure it has a prompt
            if not severity_param.fill_behavior:
                severity_param.fill_behavior = dialogflow.Form.Parameter.FillBehavior()
                needs_update = True
            
            if not severity_param.fill_behavior.initial_prompt_fulfillment:
                severity_param.fill_behavior.initial_prompt_fulfillment = dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=["On a scale of 0 to 10, how severe is your symptom? (0 = no pain, 10 = worst possible)"]
                            )
                        )
                    ]
                )
                needs_update = True
                print("  [OK] Added prompt for severity parameter")
        else:
            # Add severity parameter
            severity_param = dialogflow.Form.Parameter(
                display_name="severity",
                entity_type="projects/-/locations/-/agents/-/entityTypes/sys.number",
                required=True,
                fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                    initial_prompt_fulfillment=dialogflow.Fulfillment(
                        messages=[
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=["On a scale of 0 to 10, how severe is your symptom? (0 = no pain, 10 = worst possible)"]
                                )
                            )
                        ]
                    )
                )
            )
            symptom_intake_page.form.parameters.append(severity_param)
            needs_update = True
            print("  [OK] Added severity parameter")
        
        # Ensure there's a transition route only when form is complete
        clarifying_page = None
        for page in pages:
            if page.display_name == "Clarifying Questions":
                clarifying_page = page
                break
        
        if clarifying_page:
            # Check if we have a route that transitions when form is complete
            has_completion_route = False
            for route in symptom_intake_page.transition_routes or []:
                if route.condition and ("FINAL" in route.condition or "$page.params.status" in route.condition):
                    has_completion_route = True
                    break
            
            if not has_completion_route:
                if not symptom_intake_page.transition_routes:
                    symptom_intake_page.transition_routes = []
                
                symptom_intake_page.transition_routes.append(
                    dialogflow.TransitionRoute(
                        condition='$page.params.status = "FINAL"',
                        target_page=clarifying_page.name
                    )
                )
                needs_update = True
                print("  [OK] Added form completion route to Clarifying Questions")
        
        # Update entry fulfillment to give a greeting
        if not symptom_intake_page.entry_fulfillment:
            symptom_intake_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=["I understand you're experiencing {symptom_type}. Let me gather some information about your symptoms."]
                        )
                    )
                ]
            )
            needs_update = True
            print("  [OK] Added entry fulfillment")
        
        if needs_update:
            # Update the page
            request = dialogflow.UpdatePageRequest(page=symptom_intake_page)
            pages_client.update_page(request=request)
            print()
            print("[OK] Symptom Intake page updated")
        else:
            print()
            print("[INFO] No updates needed")
        
        print()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_and_fix_symptom_intake()
    exit(0 if success else 1)

