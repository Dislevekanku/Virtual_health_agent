#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete verification of intent routes and flow configuration
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

def verify_complete_setup():
    """Complete verification"""
    
    print("="*60)
    print("Complete Setup Verification")
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
        
        print("1. FLOW CONFIGURATION")
        print("-" * 60)
        print(f"   Flow: {flow.display_name}")
        if flow.nlu_settings:
            print(f"   NLU Model: {flow.nlu_settings.model_type}")
            print(f"   Classification Threshold: {flow.nlu_settings.classification_threshold}")
        print()
        
        # Get intents
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        print("2. INTENTS")
        print("-" * 60)
        symptom_intents = {}
        for intent in intents:
            if intent.display_name.startswith("symptom_"):
                symptom_intents[intent.display_name] = {
                    'name': intent.name,
                    'phrases': len(intent.training_phrases)
                }
                print(f"   ✓ {intent.display_name}: {len(intent.training_phrases)} training phrases")
        print(f"\n   Total symptom intents: {len(symptom_intents)}")
        print()
        
        # Get pages
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        page_dict = {page.display_name: page.name for page in pages}
        
        print("3. PAGES")
        print("-" * 60)
        required_pages = ["Start", "Symptom Intake", "Triage Evaluation"]
        for page_name in required_pages:
            if page_name in page_dict:
                print(f"   ✓ {page_name}: Found")
            else:
                print(f"   ✗ {page_name}: Missing")
        print()
        
        # Check Start page routes
        print("4. START PAGE ROUTES")
        print("-" * 60)
        start_page = None
        for page in pages:
            if page.display_name == "Start":
                start_page = page
                break
        
        if not start_page:
            print("   ✗ Start page not found")
            return False
        
        print(f"   Start page found: {start_page.display_name}")
        
        if not start_page.transition_routes:
            print("   ✗ No transition routes configured")
            return False
        
        intent_routes = [r for r in start_page.transition_routes if r.intent]
        print(f"   Total routes: {len(start_page.transition_routes)}")
        print(f"   Intent-based routes: {len(intent_routes)}")
        print()
        
        # Verify each intent route
        print("   Route Details:")
        route_status = {}
        for route in intent_routes:
            # Find intent name
            intent_name = None
            for name, details in symptom_intents.items():
                if details['name'] == route.intent:
                    intent_name = name
                    break
            
            # Find target page
            target_name = None
            for name, page_id in page_dict.items():
                if page_id == route.target_page:
                    target_name = name
                    break
            
            if intent_name and target_name:
                status = "✓"
                route_status[intent_name] = target_name
            else:
                status = "✗"
            
            print(f"     {status} {intent_name or 'Unknown'} -> {target_name or 'Unknown'}")
        
        print()
        
        # Summary
        print("="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        all_good = True
        
        # Check intents
        expected_intents = [
            "symptom_headache", "symptom_nausea", "symptom_dizziness",
            "symptom_fatigue", "symptom_headache_redflag", "symptom_redflag"
        ]
        missing_intents = [i for i in expected_intents if i not in symptom_intents]
        if missing_intents:
            print(f"✗ Missing intents: {missing_intents}")
            all_good = False
        else:
            print("✓ All required intents exist")
        
        # Check routes
        missing_routes = [i for i in expected_intents if i not in route_status]
        if missing_routes:
            print(f"✗ Missing routes: {missing_routes}")
            all_good = False
        else:
            print("✓ All required routes configured")
        
        # Check pages
        missing_pages = [p for p in required_pages if p not in page_dict]
        if missing_pages:
            print(f"✗ Missing pages: {missing_pages}")
            all_good = False
        else:
            print("✓ All required pages exist")
        
        print()
        
        if all_good:
            print("✅ Configuration is complete!")
            print()
            print("If intents still don't match, possible causes:")
            print("  1. NLU model is still training (wait 5-10 minutes)")
            print("  2. Flow entry point may need to be set in the UI")
            print("  3. Test in the Dialogflow console to verify behavior")
        else:
            print("⚠️  Some configuration issues found above")
        
        print()
        return all_good
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_complete_setup()

