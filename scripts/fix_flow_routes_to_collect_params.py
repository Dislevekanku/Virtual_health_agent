#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix flow routes to go through Symptom Intake page first to collect parameters
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

def fix_flow_routes():
    """Update flow routes to go to Symptom Intake first (except red flags)"""
    
    print("="*60)
    print("Fix Flow Routes to Collect Parameters")
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
        
        # Get pages
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        page_dict = {page.display_name: page.name for page in pages}
        
        # Get intents
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        intent_dict = {intent.display_name: intent.name for intent in intents}
        
        print("Updating flow routes...")
        print("  Regular symptoms -> Symptom Intake (to collect duration/severity)")
        print("  Red flags -> Triage Evaluation (immediate)")
        print()
        
        # Keep Welcome Intent route
        existing_routes = []
        existing_intent_ids = set()
        if flow.transition_routes:
            for route in flow.transition_routes:
                existing_routes.append(route)
                if route.intent:
                    existing_intent_ids.add(route.intent)
        
        # Regular symptom routes should go to Symptom Intake (not directly to Summary)
        regular_symptom_intents = [
            ("symptom_headache", "Symptom Intake", {"symptom_type": "headache"}),
            ("symptom_nausea", "Symptom Intake", {"symptom_type": "nausea"}),
            ("symptom_dizziness", "Symptom Intake", {"symptom_type": "dizziness"}),
            ("symptom_fatigue", "Symptom Intake", {"symptom_type": "fatigue"}),
        ]
        
        new_routes = []
        for intent_name, target_page, params in regular_symptom_intents:
            if intent_name in intent_dict and intent_dict[intent_name] not in existing_intent_ids:
                if target_page in page_dict:
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
                    new_routes.append(route)
        
        # Red flag routes go directly to Triage Evaluation
        red_flag_intents = [
            ("symptom_headache_redflag", "Triage Evaluation", {"urgency": "high", "symptom_type": "headache"}),
            ("symptom_redflag", "Triage Evaluation", {"urgency": "high", "symptom_type": "chest_pain"}),
        ]
        
        for intent_name, target_page, params in red_flag_intents:
            if intent_name in intent_dict and intent_dict[intent_name] not in existing_intent_ids:
                if target_page in page_dict:
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
                    new_routes.append(route)
        
        # Remove old routes for these intents and add new ones
        # Keep Welcome Intent and other non-intent routes
        final_routes = []
        for route in existing_routes:
            if route.intent and route.intent not in [intent_dict.get(name) for name in 
                ["symptom_headache", "symptom_nausea", "symptom_dizziness", "symptom_fatigue",
                 "symptom_headache_redflag", "symptom_redflag"] if intent_dict.get(name)]:
                final_routes.append(route)
            elif not route.intent:
                final_routes.append(route)
        
        # Add new routes
        final_routes.extend(new_routes)
        
        flow.transition_routes = final_routes
        
        # Update flow
        update_request = dialogflow.UpdateFlowRequest(flow=flow)
        flows_client.update_flow(request=update_request)
        
        print()
        print("[OK] Flow routes updated")
        print("     Regular symptoms now route to Symptom Intake first")
        print("     Red flags route directly to Triage Evaluation")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_flow_routes()
    exit(0 if success else 1)

