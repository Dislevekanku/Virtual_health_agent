#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnose intent routes configuration
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

def diagnose_routes():
    """Diagnose route configuration"""
    
    print("="*60)
    print("Diagnosing Intent Routes Configuration")
    print("="*60)
    print()
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        # Get flow
        flows_client = get_client(dialogflow.FlowsClient)
        request = dialogflow.ListFlowsRequest(parent=agent_name)
        flows = flows_client.list_flows(request=request)
        
        flow_name = None
        for flow in flows:
            if flow.display_name == "Default Start Flow":
                flow_name = flow.name
                print(f"Flow: {flow.display_name}")
                print(f"Flow Name: {flow_name}")
                break
        
        if not flow_name:
            print("[ERROR] Could not find Default Start Flow")
            return
        
        print()
        
        # Get pages
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        print(f"Pages in flow ({len(pages)} total):")
        for page in pages:
            print(f"\n  Page: {page.display_name}")
            print(f"    Name: {page.name}")
            
            # Check entry fulfillment
            if page.entry_fulfillment and page.entry_fulfillment.messages:
                print(f"    Has entry fulfillment: Yes")
                for msg in page.entry_fulfillment.messages:
                    if msg.text:
                        text = " ".join(msg.text.text[:50]) if msg.text.text else ""
                        print(f"      Text: {text[:100]}...")
            
            # Check transition routes
            if page.transition_routes:
                print(f"    Transition routes: {len(page.transition_routes)}")
                for i, route in enumerate(page.transition_routes, 1):
                    route_info = []
                    if route.intent:
                        route_info.append(f"Intent: {route.intent.split('/')[-1]}")
                    if route.target_page:
                        route_info.append(f"Target: {route.target_page.split('/')[-1]}")
                    if route.condition:
                        route_info.append(f"Condition: {route.condition}")
                    print(f"      Route {i}: {', '.join(route_info)}")
            else:
                print(f"    Transition routes: None")
            
            # Check event handlers
            if page.event_handlers:
                print(f"    Event handlers: {len(page.event_handlers)}")
        
        # Get intents
        print("\n" + "="*60)
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        print(f"Intents ({len(intents)} total):")
        
        # Create intent name to ID mapping
        intent_id_to_name = {intent.name: intent.display_name for intent in intents}
        symptom_intents = []
        for intent in intents:
            if intent.display_name.startswith("symptom_"):
                symptom_intents.append(intent)
                print(f"\n  Intent: {intent.display_name}")
                print(f"    Name: {intent.name}")
                print(f"    Training phrases: {len(intent.training_phrases)}")
                if intent.training_phrases:
                    print(f"    Sample phrases:")
                    for phrase in intent.training_phrases[:3]:
                        phrase_text = " ".join([part.text for part in phrase.parts])
                        print(f"      - {phrase_text}")
        
        print("\n" + "="*60)
        print("Diagnosis Summary")
        print("="*60)
        
        # Check if Start page has routes
        start_pages = [p for p in pages if p.display_name in ["Start", "Start Page"]]
        if start_pages:
            start_page = start_pages[0]
            print(f"\nStart page found: {start_page.display_name}")
            if start_page.transition_routes:
                intent_routes = [r for r in start_page.transition_routes if r.intent]
                print(f"  Intent routes configured: {len(intent_routes)}")
                if intent_routes:
                    print("  [OK] Routes are configured")
                    print("\n  Route details:")
                    for i, route in enumerate(intent_routes, 1):
                        intent_name = intent_id_to_name.get(route.intent, route.intent.split('/')[-1])
                        target_page_name = None
                        for p in pages:
                            if p.name == route.target_page:
                                target_page_name = p.display_name
                                break
                        print(f"    {i}. Intent: {intent_name} -> Page: {target_page_name}")
                else:
                    print("  [WARNING] No intent routes found")
            else:
                print("  [ERROR] No transition routes found on Start page")
        else:
            print("\n[ERROR] No Start page found")
        
        # Check flow NLU settings
        print("\n" + "="*60)
        print("Flow NLU Settings")
        print("="*60)
        flow_request = dialogflow.GetFlowRequest(name=flow_name)
        flow = flows_client.get_flow(request=flow_request)
        if flow.nlu_settings:
            print(f"  Model type: {flow.nlu_settings.model_type}")
            print(f"  Classification threshold: {flow.nlu_settings.classification_threshold}")
        else:
            print("  [WARNING] No NLU settings found")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_routes()

