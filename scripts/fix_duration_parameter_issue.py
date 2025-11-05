#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix duration parameter - ensure form accepts and transitions properly
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

def fix_duration_issue():
    """Fix duration parameter to accept any text and transition properly"""
    
    print("="*60)
    print("Fix Duration Parameter Issue")
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
        
        # Find Symptom Intake page
        symptom_intake_page = None
        clarifying_page = None
        for page in pages:
            if page.display_name == "Symptom Intake":
                symptom_intake_page = page
            if page.display_name == "Clarifying Questions":
                clarifying_page = page
        
        if not symptom_intake_page:
            print("[ERROR] Symptom Intake page not found")
            return False
        
        print("Fixing Symptom Intake page...")
        print()
        
        if not symptom_intake_page.form:
            symptom_intake_page.form = dialogflow.Form()
        
        if not symptom_intake_page.form.parameters:
            symptom_intake_page.form.parameters = []
        
        # Find duration parameter
        duration_param = None
        for param in symptom_intake_page.form.parameters:
            if param.display_name == "duration":
                duration_param = param
                break
        
        if duration_param:
            print("Found duration parameter")
            
            # Change to @sys.any to accept any text input
            # This is more flexible and will capture "5 days ago", "4 days ago", etc.
            duration_param.entity_type = "projects/-/locations/-/agents/-/entityTypes/sys.any"
            duration_param.required = True
            
            # Clear fill behavior and recreate it simply
            duration_param.fill_behavior = dialogflow.Form.Parameter.FillBehavior()
            
            # Simple initial prompt
            duration_param.fill_behavior.initial_prompt_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "When did your symptoms begin? For example, 'this morning', 'yesterday', '3 days ago', 'last week', or 'about a week ago'."
                            ]
                        )
                    )
                ]
            )
            
            # Remove existing reprompt handlers (they cause issues)
            duration_param.fill_behavior.reprompt_event_handlers = []
            
            print("  [OK] Duration parameter updated to @sys.any")
            print("        Will accept any text input")
        
        # CRITICAL: Ensure form transitions after parameters are collected
        # The issue is likely that the form isn't completing
        # Add transition route when form is complete
        
        if clarifying_page:
            # Check if transition exists
            has_transition = False
            if symptom_intake_page.transition_routes:
                for route in symptom_intake_page.transition_routes:
                    if route.target_page == clarifying_page.name:
                        has_transition = True
                        break
            
            if not has_transition:
                # Add transition route when form is complete
                if not symptom_intake_page.transition_routes:
                    symptom_intake_page.transition_routes = []
                
                symptom_intake_page.transition_routes.append(
                    dialogflow.TransitionRoute(
                        condition='$page.params.status = "FINAL"',
                        target_page=clarifying_page.name
                    )
                )
                print("  [OK] Added transition route when form completes")
            else:
                print("  [OK] Transition route already exists")
        
        # Also ensure severity parameter is configured properly
        severity_param = None
        for param in symptom_intake_page.form.parameters:
            if param.display_name == "severity":
                severity_param = param
                break
        
        if severity_param:
            # Make sure severity accepts any input too
            severity_param.entity_type = "projects/-/locations/-/agents/-/entityTypes/sys.any"
            severity_param.required = True
            
            if not severity_param.fill_behavior:
                severity_param.fill_behavior = dialogflow.Form.Parameter.FillBehavior()
            
            severity_param.fill_behavior.initial_prompt_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "On a scale of 0 to 10, how would you rate your symptoms? You can say the number, like '3' or 'about 7'."
                            ]
                        )
                    )
                ]
            )
            
            severity_param.fill_behavior.reprompt_event_handlers = []
            print("  [OK] Severity parameter also updated to @sys.any")
        
        # Update the page
        request = dialogflow.UpdatePageRequest(page=symptom_intake_page)
        pages_client.update_page(request=request)
        
        print()
        print("[OK] Symptom Intake page updated")
        print()
        print("Key Changes:")
        print("  ✓ Duration parameter: Changed to @sys.any (accepts any text)")
        print("  ✓ Removed problematic reprompt handlers")
        print("  ✓ Added form completion transition")
        print("  ✓ Severity parameter: Also updated to @sys.any")
        print()
        print("The agent should now accept:")
        print("  - '5 days ago' ✓")
        print("  - '4 days ago' ✓")
        print("  - 'yesterday' ✓")
        print("  - 'last week' ✓")
        print("  - Any natural language duration ✓")
        print()
        print("Note: The form will now transition to the next page after")
        print("collecting both duration and severity, even if extraction")
        print("isn't perfect. The text will be stored and can be processed later.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_duration_issue()
    exit(0 if success else 1)

