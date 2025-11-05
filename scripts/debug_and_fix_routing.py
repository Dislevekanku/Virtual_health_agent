#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug and fix routing to ensure Symptom Intake page is visited first
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

def debug_and_fix():
    """Debug routing and fix it"""
    
    print("="*60)
    print("Debug and Fix Routing")
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
        
        print("Current Flow Routes:")
        if flow.transition_routes:
            for i, route in enumerate(flow.transition_routes, 1):
                intent_name = "Unknown"
                for name, intent_id in intent_dict.items():
                    if route.intent == intent_id:
                        intent_name = name
                        break
                
                target_name = "Unknown"
                for name, page_id in page_dict.items():
                    if route.target_page == page_id:
                        target_name = name
                        break
                
                print(f"  {i}. Intent: {intent_name} -> Page: {target_name}")
        else:
            print("  No flow-level routes")
        print()
        
        # Check Start page routes
        start_page = None
        for page in pages:
            if page.display_name == "Start":
                start_page = page
                break
        
        if start_page:
            print("Current Start Page Routes:")
            if start_page.transition_routes:
                for i, route in enumerate(start_page.transition_routes, 1):
                    intent_name = "Unknown"
                    if route.intent:
                        for name, intent_id in intent_dict.items():
                            if route.intent == intent_id:
                                intent_name = name
                                break
                    
                    target_name = "Unknown"
                    if route.target_page:
                        for name, page_id in page_dict.items():
                            if route.target_page == page_id:
                                target_name = name
                                break
                    
                    print(f"  {i}. Intent: {intent_name} -> Page: {target_name}")
            else:
                print("  No Start page routes")
        print()
        
        # Now fix: Update flow routes to point to Symptom Intake for regular symptoms
        print("Updating flow routes...")
        
        # Keep Welcome Intent route
        existing_routes = []
        symptom_intent_ids = set()
        
        if flow.transition_routes:
            for route in flow.transition_routes:
                # Check if this is a symptom intent
                is_symptom_intent = False
                if route.intent:
                    for symptom_intent in ["symptom_headache", "symptom_nausea", "symptom_dizziness", "symptom_fatigue"]:
                        if route.intent == intent_dict.get(symptom_intent):
                            is_symptom_intent = True
                            symptom_intent_ids.add(route.intent)
                            break
                
                # Keep non-symptom routes (Welcome Intent, etc.)
                if not is_symptom_intent:
                    existing_routes.append(route)
        
        # Add new routes for regular symptoms -> Symptom Intake
        new_routes = []
        regular_symptoms = [
            ("symptom_headache", "Symptom Intake", {"symptom_type": "headache"}),
            ("symptom_nausea", "Symptom Intake", {"symptom_type": "nausea"}),
            ("symptom_dizziness", "Symptom Intake", {"symptom_type": "dizziness"}),
            ("symptom_fatigue", "Symptom Intake", {"symptom_type": "fatigue"}),
        ]
        
        for intent_name, target_page, params in regular_symptoms:
            if intent_name in intent_dict and target_page in page_dict:
                intent_id = intent_dict[intent_name]
                if intent_id not in symptom_intent_ids:  # Only add if not already there
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
                        intent=intent_id,
                        target_page=page_dict[target_page],
                        trigger_fulfillment=dialogflow.Fulfillment(
                            set_parameter_actions=set_parameter_actions
                        )
                    )
                    new_routes.append(route)
        
        # Add red flag routes -> Triage Evaluation
        red_flag_intents = [
            ("symptom_headache_redflag", "Triage Evaluation", {"urgency": "high", "symptom_type": "headache"}),
            ("symptom_redflag", "Triage Evaluation", {"urgency": "high", "symptom_type": "chest_pain"}),
        ]
        
        for intent_name, target_page, params in red_flag_intents:
            if intent_name in intent_dict and target_page in page_dict:
                intent_id = intent_dict[intent_name]
                # Check if already exists
                exists = False
                if flow.transition_routes:
                    for route in flow.transition_routes:
                        if route.intent == intent_id:
                            exists = True
                            break
                
                if not exists:
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
                        intent=intent_id,
                        target_page=page_dict[target_page],
                        trigger_fulfillment=dialogflow.Fulfillment(
                            set_parameter_actions=set_parameter_actions
                        )
                    )
                    new_routes.append(route)
        
        # Combine routes
        flow.transition_routes = existing_routes + new_routes
        
        # Update flow
        update_request = dialogflow.UpdateFlowRequest(flow=flow)
        flows_client.update_flow(request=update_request)
        
        print()
        print("[OK] Flow routes updated")
        print()
        print("Updated Flow Routes:")
        for i, route in enumerate(flow.transition_routes, 1):
            intent_name = "Unknown"
            if route.intent:
                for name, intent_id in intent_dict.items():
                    if route.intent == intent_id:
                        intent_name = name
                        break
            
            target_name = "Unknown"
            if route.target_page:
                for name, page_id in page_dict.items():
                    if route.target_page == page_id:
                        target_name = name
                        break
            
            print(f"  {i}. Intent: {intent_name} -> Page: {target_name}")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_and_fix()
    exit(0 if success else 1)

