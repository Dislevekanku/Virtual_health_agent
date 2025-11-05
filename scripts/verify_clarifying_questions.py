#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Clarifying Questions page is configured correctly
"""

import json
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

def verify_clarifying_questions():
    """Verify Clarifying Questions page configuration"""
    
    print("="*60)
    print("Verify Clarifying Questions Page")
    print("="*60)
    print()
    
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        flows_client = get_client(dialogflow.FlowsClient)
        request = dialogflow.ListFlowsRequest(parent=agent_name)
        flows = list(flows_client.list_flows(request=request))
        
        flow_name = None
        for flow in flows:
            if flow.display_name == "Default Start Flow":
                flow_name = flow.name
                break
        
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        clarifying_page = None
        for page in pages:
            if page.display_name == "Clarifying Questions":
                clarifying_page = page
                break
        
        if not clarifying_page:
            print("[ERROR] Clarifying Questions page not found")
            return False
        
        print("Clarifying Questions Page Configuration:")
        print()
        
        # Check entry fulfillment
        if clarifying_page.entry_fulfillment and clarifying_page.entry_fulfillment.messages:
            print("Entry Message:")
            for msg in clarifying_page.entry_fulfillment.messages:
                if msg.text and msg.text.text:
                    print(f"  {msg.text.text[0]}")
            print()
        
        # Check form parameters
        if clarifying_page.form and clarifying_page.form.parameters:
            print(f"Form Parameters ({len(clarifying_page.form.parameters)}):")
            for param in clarifying_page.form.parameters:
                print(f"  - {param.display_name}")
                if param.fill_behavior and param.fill_behavior.initial_prompt_fulfillment:
                    if param.fill_behavior.initial_prompt_fulfillment.messages:
                        for msg in param.fill_behavior.initial_prompt_fulfillment.messages:
                            if msg.text and msg.text.text:
                                print(f"    Prompt: {msg.text.text[0][:80]}...")
                print()
        else:
            print("[WARNING] No form parameters found!")
            print()
        
        # Check transition routes
        if clarifying_page.transition_routes:
            print(f"Transition Routes ({len(clarifying_page.transition_routes)}):")
            for route in clarifying_page.transition_routes:
                if route.condition:
                    print(f"  - Condition: {route.condition}")
                if route.intent:
                    print(f"  - Intent: {route.intent}")
                if route.target_page:
                    page_name = route.target_page.split('/')[-1]
                    print(f"  - Target: {page_name}")
            print()
        
        print("="*60)
        print("Summary")
        print("="*60)
        print()
        
        if clarifying_page.form and clarifying_page.form.parameters:
            param_count = len(clarifying_page.form.parameters)
            print(f"✅ Page has {param_count} question(s) configured")
            print()
            print("The agent should now ask these questions:")
            for param in clarifying_page.form.parameters:
                print(f"  - {param.display_name}")
        else:
            print("❌ No questions configured - page will skip")
        
        print()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_clarifying_questions()

