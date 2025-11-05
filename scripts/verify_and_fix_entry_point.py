#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify flow entry point and ensure routes are on the correct page
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

def verify_and_fix():
    """Verify entry point and ensure routes are configured"""
    
    print("="*60)
    print("Verify Flow Entry Point")
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
        
        # Get flow details
        flow_request = dialogflow.GetFlowRequest(name=flow_name)
        flow = flows_client.get_flow(request=flow_request)
        
        print(f"Flow: {flow.display_name}")
        print(f"Entry fulfillment: {flow.transition_routes is not None and len(flow.transition_routes) > 0}")
        print()
        
        # Get pages
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        print("Pages in flow:")
        for page in pages:
            print(f"  - {page.display_name} (ID: {page.name.split('/')[-1][:8]}...)")
            if page.display_name in ["Start", "Start Page"]:
                routes_count = len(page.transition_routes) if page.transition_routes else 0
                intent_routes = len([r for r in page.transition_routes if r.intent]) if page.transition_routes else 0
                print(f"    Routes: {routes_count} total, {intent_routes} intent-based")
        print()
        
        # Get intents
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        intent_dict = {intent.display_name: intent.name for intent in intents}
        page_dict = {page.display_name: page.name for page in pages}
        
        # Configure routes on "Start" page (which is what exists)
        start_page = None
        for page in pages:
            if page.display_name == "Start":
                start_page = page
                break
        
        if not start_page:
            print("[ERROR] Could not find Start page")
            return False
        
        print(f"Configuring routes on: {start_page.display_name}")
        print()
        
        # Add routes
        routes = []
        intent_routes_config = [
            ("symptom_headache", "Symptom Intake", {"symptom_type": "headache"}),
            ("symptom_nausea", "Symptom Intake", {"symptom_type": "nausea"}),
            ("symptom_dizziness", "Symptom Intake", {"symptom_type": "dizziness"}),
            ("symptom_fatigue", "Symptom Intake", {"symptom_type": "fatigue"}),
            ("symptom_headache_redflag", "Triage Evaluation", {"urgency": "high", "symptom_type": "headache"}),
            ("symptom_redflag", "Triage Evaluation", {"urgency": "high", "symptom_type": "chest_pain"}),
        ]
        
        for intent_name, target_page, params in intent_routes_config:
            if intent_name in intent_dict and target_page in page_dict:
                print(f"  Adding: {intent_name} -> {target_page}")
                
                set_parameter_actions = []
                for param_name, param_value in params.items():
                    set_parameter_actions.append(
                        dialogflow.Fulfillment.SetParameterAction(
                            parameter=param_name,
                            value=param_value
                        )
                    )
                
                route = dialogflow.TransitionRoute(
                    intent=intent_dict[intent_name],
                    target_page=page_dict[target_page],
                    trigger_fulfillment=dialogflow.Fulfillment(
                        set_parameter_actions=set_parameter_actions
                    )
                )
                routes.append(route)
        
        # Keep existing non-intent routes
        existing_routes = []
        if start_page.transition_routes:
            for route in start_page.transition_routes:
                if not route.intent:
                    existing_routes.append(route)
        
        # Replace intent routes with new ones
        start_page.transition_routes = existing_routes + routes
        
        # Update page
        request = dialogflow.UpdatePageRequest(page=start_page)
        pages_client.update_page(request=request)
        
        print()
        print(f"[OK] Configured {len(routes)} intent routes on Start page")
        print()
        print("Note: The UI may show 'Start Page' but the API uses 'Start'.")
        print("      Routes are now configured on the correct page.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_and_fix()
    exit(0 if success else 1)

