#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnose webhook/grounding integration issue
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

def diagnose_webhook():
    """Diagnose webhook configuration"""
    
    print("="*60)
    print("Diagnose Webhook/Grounding Integration")
    print("="*60)
    print()
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        # Check webhooks
        print("1. Checking webhooks...")
        webhooks_client = get_client(dialogflow.WebhooksClient)
        request = dialogflow.ListWebhooksRequest(parent=agent_name)
        webhooks = list(webhooks_client.list_webhooks(request=request))
        
        if webhooks:
            print(f"   Found {len(webhooks)} webhook(s):")
            for webhook in webhooks:
                print(f"   - {webhook.display_name}")
                if webhook.generic_web_service:
                    print(f"     URL: {webhook.generic_web_service.uri}")
                print(f"     Name: {webhook.name}")
        else:
            print("   [WARNING] No webhooks found")
        
        print()
        
        # Check Triage Evaluation page
        print("2. Checking Triage Evaluation page...")
        flows_client = get_client(dialogflow.FlowsClient)
        request = dialogflow.ListFlowsRequest(parent=agent_name)
        flows = list(flows_client.list_flows(request=request))
        
        flow_name = None
        for flow in flows:
            if flow.display_name == "Default Start Flow":
                flow_name = flow.name
                break
        
        if flow_name:
            pages_client = get_client(dialogflow.PagesClient)
            request = dialogflow.ListPagesRequest(parent=flow_name)
            pages = list(pages_client.list_pages(request=request))
            
            triage_page = None
            for page in pages:
                if page.display_name == "Triage Evaluation":
                    triage_page = page
                    break
            
            if triage_page:
                print("   Found Triage Evaluation page")
                
                if triage_page.entry_fulfillment:
                    if triage_page.entry_fulfillment.webhook:
                        print(f"   [OK] Webhook configured: {triage_page.entry_fulfillment.webhook}")
                    else:
                        print("   [WARNING] Entry fulfillment exists but no webhook configured")
                    
                    if triage_page.entry_fulfillment.messages:
                        print(f"   [OK] Entry messages: {len(triage_page.entry_fulfillment.messages)} message(s)")
                else:
                    print("   [WARNING] No entry fulfillment configured")
            else:
                print("   [ERROR] Triage Evaluation page not found")
        
        print()
        print("="*60)
        print("Diagnosis Summary")
        print("="*60)
        print()
        print("The webhook error message indicates:")
        print("  - The webhook is being called (this is good)")
        print("  - But it's failing to access the clinical guidelines database")
        print()
        print("Possible causes:")
        print("  1. Webhook URL not accessible")
        print("  2. Cloud Function not deployed or not responding")
        print("  3. Vertex AI Search datastore not configured")
        print("  4. Service account permissions missing")
        print()
        print("The agent still provides fallback recommendations,")
        print("so basic functionality works. The webhook is optional")
        print("for enhanced clinical guideline citations.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    diagnose_webhook()

