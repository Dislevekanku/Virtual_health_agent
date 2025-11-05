#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix duration parameter extraction - ensure it recognizes natural language durations
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

def fix_duration_extraction():
    """Fix duration parameter to better extract natural language durations"""
    
    print("="*60)
    print("Fix Duration Parameter Extraction")
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
        for page in pages:
            if page.display_name == "Symptom Intake":
                symptom_intake_page = page
                break
        
        if not symptom_intake_page:
            print("[ERROR] Symptom Intake page not found")
            return False
        
        print("Fixing duration parameter extraction...")
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
            
            # Try using @sys.any for maximum flexibility
            # This will capture any text, then we can process it
            duration_param.entity_type = "projects/-/locations/-/agents/-/entityTypes/sys.any"
            duration_param.required = True
            
            # Improve fill behavior
            if not duration_param.fill_behavior:
                duration_param.fill_behavior = dialogflow.Form.Parameter.FillBehavior()
            
            # Better initial prompt
            duration_param.fill_behavior.initial_prompt_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "When did your symptoms begin? You can say things like 'this morning', 'yesterday', '3 days ago', 'last week', or 'about a week ago'."
                            ]
                        )
                    )
                ]
            )
            
            # Add event handlers for invalid parameter
            if not duration_param.fill_behavior.reprompt_event_handlers:
                duration_param.fill_behavior.reprompt_event_handlers = []
            
            # Check if we already have handlers
            has_invalid_handler = False
            for handler in duration_param.fill_behavior.reprompt_event_handlers:
                if handler.event == "sys.invalid-parameter":
                    has_invalid_handler = True
                    break
            
            if not has_invalid_handler:
                # Add handler for invalid parameter
                duration_param.fill_behavior.reprompt_event_handlers.append(
                    dialogflow.EventHandler(
                        event="sys.invalid-parameter",
                        trigger_fulfillment=dialogflow.Fulfillment(
                            messages=[
                                dialogflow.ResponseMessage(
                                    text=dialogflow.ResponseMessage.Text(
                                        text=[
                                            "I understand. Can you tell me when your symptoms started? For example, 'yesterday', '3 days ago', or 'last week'."
                                        ]
                                    )
                                )
                            ]
                        )
                    )
                )
            
            # Add handler for no input
            has_no_input_handler = False
            for handler in duration_param.fill_behavior.reprompt_event_handlers:
                if handler.event == "sys.no-input":
                    has_no_input_handler = True
                    break
            
            if not has_no_input_handler:
                duration_param.fill_behavior.reprompt_event_handlers.append(
                    dialogflow.EventHandler(
                        event="sys.no-input",
                        trigger_fulfillment=dialogflow.Fulfillment(
                            messages=[
                                dialogflow.ResponseMessage(
                                    text=dialogflow.ResponseMessage.Text(
                                        text=[
                                            "I didn't hear that. When did your symptoms start? You can say 'yesterday', '3 days ago', or 'last week'."
                                        ]
                                    )
                                )
                            ]
                        )
                    )
                )
            
            print("  [OK] Duration parameter updated")
            print("        Entity type: @sys.any (flexible extraction)")
            print("        Added reprompt handlers")
            print("        Improved prompts")
        
        # Also check if we need to add a transition route based on duration
        # The issue might be that the form isn't completing even when duration is provided
        
        # Update the page
        request = dialogflow.UpdatePageRequest(page=symptom_intake_page)
        pages_client.update_page(request=request)
        
        print()
        print("[OK] Symptom Intake page updated")
        print()
        print("Improvements:")
        print("  ✓ Changed duration to @sys.any for better text extraction")
        print("  ✓ Added reprompt handlers for invalid/no-input")
        print("  ✓ Improved prompts with more examples")
        print()
        print("Note: The agent should now accept responses like:")
        print("  - '5 days ago'")
        print("  - '4 days ago'")
        print("  - 'yesterday'")
        print("  - 'last week'")
        print("  - 'about 3 days'")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_duration_extraction()
    exit(0 if success else 1)

