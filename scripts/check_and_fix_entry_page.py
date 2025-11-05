#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check which page is the actual entry point and ensure routes are configured there
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

def check_and_fix():
    """Check entry point and configure routes"""
    
    print("="*60)
    print("Check Entry Point and Configure Routes")
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
        
        # Get flow details - check for entry fulfillment
        flow_request = dialogflow.GetFlowRequest(name=flow_name)
        flow = flows_client.get_flow(request=flow_request)
        
        print("Flow Entry Point Analysis:")
        print(f"  Flow: {flow.display_name}")
        
        # Check if flow has transition routes (entry-level routes)
        if flow.transition_routes:
            print(f"  Flow-level routes: {len(flow.transition_routes)}")
            for route in flow.transition_routes:
                if route.intent:
                    print(f"    - Intent route found")
                if route.target_page:
                    print(f"    - Target page route found")
        else:
            print("  Flow-level routes: None")
        print()
        
        # Get all pages
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        print("Pages in flow:")
        for page in pages:
            routes_count = len(page.transition_routes) if page.transition_routes else 0
            intent_routes = len([r for r in page.transition_routes if r.intent]) if page.transition_routes else 0
            print(f"  - {page.display_name}: {routes_count} routes ({intent_routes} intent-based)")
        print()
        
        # Get intents
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        intent_dict = {intent.display_name: intent.name for intent in intents}
        page_dict = {page.display_name: page.name for page in pages}
        
        # Try to configure routes on FLOW level (entry point)
        print("Attempting to configure routes on FLOW level (entry point)...")
        
        # Create routes for flow level
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
                print(f"  Adding flow-level route: {intent_name} -> {target_page}")
                
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
        
        # Keep ALL existing flow routes (especially Welcome Intent which is required)
        existing_routes = []
        existing_intent_ids = set()
        if flow.transition_routes:
            for route in flow.transition_routes:
                existing_routes.append(route)
                if route.intent:
                    existing_intent_ids.add(route.intent)
        
        # Only add new routes that don't already exist
        new_routes = [r for r in routes if r.intent not in existing_intent_ids]
        
        # Update flow with routes (preserve all existing, add new ones)
        flow.transition_routes = existing_routes + new_routes
        
        update_request = dialogflow.UpdateFlowRequest(flow=flow)
        flows_client.update_flow(request=update_request)
        
        print(f"\n[OK] Configured {len(routes)} intent routes on FLOW level")
        print()
        print("Routes are now configured at the flow entry point.")
        print("This should work regardless of which page is shown in the UI.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_and_fix()
    exit(0 if success else 1)

