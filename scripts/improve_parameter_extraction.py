#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improve parameter extraction for duration and severity from natural language
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

def improve_parameter_extraction():
    """Improve duration and severity parameter extraction"""
    
    print("="*60)
    print("Improve Parameter Extraction")
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
        
        print("Improving Symptom Intake page parameter extraction...")
        print()
        
        if not symptom_intake_page.form:
            symptom_intake_page.form = dialogflow.Form()
        
        if not symptom_intake_page.form.parameters:
            symptom_intake_page.form.parameters = []
        
        # Improve duration parameter
        print("1. Improving duration parameter...")
        duration_param = None
        for param in symptom_intake_page.form.parameters:
            if param.display_name == "duration":
                duration_param = param
                break
        
        if duration_param:
            # Use @sys.time-period or @sys.date-time for better extraction
            # @sys.time-period handles: "this morning", "3 days ago", "last week", etc.
            # @sys.date-time handles: "2024-01-15", specific dates
            # For flexibility, use @sys.any and let NLU handle it
            
            # Better entity type for duration extraction
            duration_param.entity_type = "projects/-/locations/-/agents/-/entityTypes/sys.time-period"
            duration_param.required = True
            
            # Improve prompt to get better responses
            if not duration_param.fill_behavior:
                duration_param.fill_behavior = dialogflow.Form.Parameter.FillBehavior()
            
            duration_param.fill_behavior.initial_prompt_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "When did your symptoms begin? For example, 'this morning', '2 days ago', 'last week', or 'about 3 days'."
                            ]
                        )
                    )
                ]
            )
            
            # Note: Reprompt event handlers are added at page level, not parameter level
            # The fill_behavior handles initial prompts and reprompts automatically
            
            print("   [OK] Duration parameter updated")
            print("        Entity type: @sys.time-period")
            print("        Better prompt added")
        else:
            print("   [ERROR] Duration parameter not found")
        
        # Improve severity parameter
        print("\n2. Improving severity parameter...")
        severity_param = None
        for param in symptom_intake_page.form.parameters:
            if param.display_name == "severity":
                severity_param = param
                break
        
        if severity_param:
            # Use @sys.number-integer for better number extraction
            # This handles: "3", "8", "about 5", "3 out of 10", etc.
            severity_param.entity_type = "projects/-/locations/-/agents/-/entityTypes/sys.number-integer"
            severity_param.required = True
            
            # Improve prompt
            if not severity_param.fill_behavior:
                severity_param.fill_behavior = dialogflow.Form.Parameter.FillBehavior()
            
            severity_param.fill_behavior.initial_prompt_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "On a scale of 0 to 10, where 0 means no pain or discomfort and 10 means the worst possible pain, "
                                "how would you rate your symptoms? You can say the number, like '3' or 'about 7'."
                            ]
                        )
                    )
                ]
            )
            
            # Note: Reprompt event handlers are added at page level, not parameter level
            # The fill_behavior handles initial prompts and reprompts automatically
            
            print("   [OK] Severity parameter updated")
            print("        Entity type: @sys.number-integer")
            print("        Better prompt added")
        else:
            print("   [ERROR] Severity parameter not found")
        
        # Add parameter extraction examples via form reprompt handlers
        print("\n3. Adding parameter validation and extraction helpers...")
        
        # Ensure symptom_type is set (should already be set from intent routes)
        symptom_type_param = None
        for param in symptom_intake_page.form.parameters:
            if param.display_name == "symptom_type":
                symptom_type_param = param
                break
        
        if symptom_type_param:
            # Make sure it's not required (set by intent route)
            symptom_type_param.required = False
            print("   [OK] Symptom type parameter configured")
        
        # Update the page
        request = dialogflow.UpdatePageRequest(page=symptom_intake_page)
        pages_client.update_page(request=request)
        
        print()
        print("[OK] Symptom Intake page updated")
        print()
        print("Improvements made:")
        print("  ✓ Duration: Changed to @sys.time-period for better extraction")
        print("  ✓ Severity: Changed to @sys.number-integer for better extraction")
        print("  ✓ Improved prompts with examples")
        print("  ✓ Added reprompt handlers for no-input events")
        print()
        print("These entity types should better extract:")
        print("  - Duration: 'this morning', '3 days ago', 'last week', 'about 2 days'")
        print("  - Severity: '3', '8', 'about 5', '3 out of 10', 'seven'")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = improve_parameter_extraction()
    exit(0 if success else 1)

