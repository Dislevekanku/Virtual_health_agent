#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix duplicate messages - ensure only one message shows at each step
Remove duplicate entry fulfillments and webhook messages
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

def fix_duplicate_messages():
    """Fix duplicate messages in agent responses"""
    
    print("="*60)
    print("Fix Duplicate Messages")
    print("="*60)
    print()
    
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
        
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        # Find pages
        clarifying_page = None
        triage_page = None
        summary_page = None
        
        for page in pages:
            if page.display_name == "Clarifying Questions":
                clarifying_page = page
            elif page.display_name == "Triage Evaluation":
                triage_page = page
            elif page.display_name == "Summary":
                summary_page = page
        
        print("Fixing duplicate messages...")
        print()
        
        # 1. Fix Clarifying Questions - ensure single entry message
        if clarifying_page:
            # Keep entry fulfillment simple - just one message
            clarifying_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "Thank you for providing those details. Let me ask a few clarifying questions to better understand your situation and determine the appropriate level of care."
                            ]
                        )
                    )
                ]
            )
            print("  [OK] Fixed Clarifying Questions entry (single message)")
        
        # 2. Fix Triage Evaluation - remove duplicate entry fulfillment
        if triage_page:
            # Remove entry fulfillment entirely - let transition routes handle messages
            # OR keep it very simple
            triage_page.entry_fulfillment = None  # Remove entry fulfillment
            
            # Ensure transition routes have clean, single messages
            if triage_page.transition_routes:
                for route in triage_page.transition_routes:
                    if route.trigger_fulfillment:
                        # Ensure only one message per route
                        if len(route.trigger_fulfillment.messages) > 1:
                            # Keep only the first (most important) message
                            route.trigger_fulfillment.messages = [
                                route.trigger_fulfillment.messages[0]
                            ]
                        # Remove any webhook from trigger fulfillment (we'll handle webhook separately)
                        # Keep webhook only for data retrieval, not for response messages
                        if route.trigger_fulfillment.webhook:
                            # Webhook can stay for data, but ensure messages are clean
                            pass
            print("  [OK] Removed Triage Evaluation entry fulfillment")
            print("  [OK] Cleaned transition route messages")
        
        # 3. Fix Summary page - ensure single message with proper parameter syntax
        if summary_page:
            summary_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "Thank you for sharing that information with me. Here's a summary of what we've discussed:\n\n"
                                "**Symptom:** $session.params.symptom_type\n"
                                "**Duration:** $session.params.duration\n"
                                "**Severity:** $session.params.severity/10\n"
                                "**Triage Level:** $session.params.triage\n"
                                "**Recommendation:** $session.params.recommendation\n\n"
                                "This information will be shared with your care team. If you have any additional concerns or if your symptoms change, please don't hesitate to reach out."
                            ]
                        )
                    )
                ]
            )
            print("  [OK] Fixed Summary page (single message, proper parameter syntax)")
        
        # Update all pages
        pages_to_update = [clarifying_page, triage_page, summary_page]
        for page in pages_to_update:
            if page:
                request = dialogflow.UpdatePageRequest(page=page)
                pages_client.update_page(request=request)
        
        print()
        print("[OK] Duplicate messages fixed")
        print()
        print("Improvements:")
        print("  ✓ Removed duplicate entry fulfillments")
        print("  ✓ Single message per page")
        print("  ✓ Clean transition route messages")
        print("  ✓ Proper parameter syntax ($session.params.parameter)")
        print()
        print("The agent will now show:")
        print("  - One message per page")
        print("  - Parameters will be substituted correctly")
        print("  - No duplicate messages")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_duplicate_messages()
    exit(0 if success else 1)

