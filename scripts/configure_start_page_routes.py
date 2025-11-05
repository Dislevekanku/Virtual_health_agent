#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configure intent routes on Start Page (the actual entry point)
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

def configure_start_page_routes():
    """Configure routes on Start Page (not Start)"""
    
    print("="*60)
    print("Configure Routes on Start Page")
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
        
        # Find Start Page (not Start)
        start_page = None
        for page in pages:
            if page.display_name == "Start Page":
                start_page = page
                break
        
        if not start_page:
            print("[ERROR] Could not find Start Page")
            print("Available pages:")
            for page in pages:
                print(f"  - {page.display_name}")
            return False
        
        print(f"Found Start Page: {start_page.display_name}")
        print(f"Page ID: {start_page.name}")
        print()
        
        # Get intents
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        intent_dict = {intent.display_name: intent.name for intent in intents}
        
        # Get target pages
        page_dict = {page.display_name: page.name for page in pages}
        
        # Configure routes
        print("Configuring intent routes...")
        
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
            if intent_name in intent_dict:
                if target_page in page_dict:
                    print(f"  Adding route: {intent_name} -> {target_page}")
                    
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
                else:
                    print(f"  [WARNING] Target page '{target_page}' not found")
            else:
                print(f"  [WARNING] Intent '{intent_name}' not found")
        
        # Keep existing routes that aren't intent-based (like Default Welcome Intent)
        existing_routes = []
        if start_page.transition_routes:
            for route in start_page.transition_routes:
                if not route.intent:  # Keep non-intent routes (conditions, etc.)
                    existing_routes.append(route)
                elif route.intent not in [r.intent for r in routes if r.intent]:
                    # Keep existing intent routes that we're not replacing
                    existing_routes.append(route)
        
        # Merge routes
        final_routes = existing_routes + routes
        
        start_page.transition_routes = final_routes
        
        # Update the page
        request = dialogflow.UpdatePageRequest(page=start_page)
        pages_client.update_page(request=request)
        
        print()
        print(f"[OK] Updated Start Page with {len(routes)} new intent routes")
        print(f"     Total routes: {len(final_routes)}")
        print()
        print("="*60)
        print("Configuration Complete!")
        print("="*60)
        print("\nRoutes configured on Start Page:")
        for route in routes:
            intent_name = [k for k, v in intent_dict.items() if v == route.intent][0]
            target_name = [k for k, v in page_dict.items() if v == route.target_page][0]
            print(f"  - {intent_name} -> {target_name}")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = configure_start_page_routes()
    exit(0 if success else 1)

