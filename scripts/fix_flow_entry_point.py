#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix flow entry point and NLU settings to ensure intent recognition works
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

def fix_flow_configuration():
    """Fix flow NLU settings and ensure proper configuration"""
    
    print("="*60)
    print("Fix Flow Configuration")
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
        print()
        
        # Update NLU settings
        print("Step 1: Updating NLU Settings...")
        if not flow.nlu_settings:
            flow.nlu_settings = dialogflow.NluSettings()
        
        # Set model type to advanced (better intent recognition)
        flow.nlu_settings.model_type = dialogflow.NluSettings.ModelType.MODEL_TYPE_ADVANCED
        
        # Set classification threshold (lower = more sensitive, but might cause false positives)
        # 0.3 is default, but we can try 0.2 for better matching
        flow.nlu_settings.classification_threshold = 0.2
        
        # Update flow
        update_request = dialogflow.UpdateFlowRequest(flow=flow)
        flows_client.update_flow(request=update_request)
        print(f"   [OK] NLU settings updated")
        print(f"        Model type: ADVANCED")
        print(f"        Classification threshold: 0.2")
        print()
        
        # Get pages and verify Start page
        print("Step 2: Verifying Start Page Configuration...")
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        start_page = None
        for page in pages:
            if page.display_name == "Start":
                start_page = page
                break
        
        if start_page:
            print(f"   [OK] Start page found: {start_page.display_name}")
            if start_page.transition_routes:
                intent_routes = [r for r in start_page.transition_routes if r.intent]
                print(f"   [OK] {len(intent_routes)} intent routes configured")
            else:
                print(f"   [WARNING] No transition routes on Start page")
        else:
            print(f"   [ERROR] Start page not found")
            return False
        
        print()
        print("="*60)
        print("Configuration Complete!")
        print("="*60)
        print("\nChanges made:")
        print("  - NLU model type set to ADVANCED")
        print("  - Classification threshold set to 0.2 (more sensitive)")
        print("\nNote: It may take a few minutes for changes to take effect.")
        print("      The NLU model needs to retrain with the new settings.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_flow_configuration()
    exit(0 if success else 1)

