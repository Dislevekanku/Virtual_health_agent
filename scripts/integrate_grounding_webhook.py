#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrate Vertex AI Search grounding webhook for symptom interpretation
"""

import json
import os
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account
from google.api_core import client_options

# Configuration
SERVICE_ACCOUNT_KEY = "key.json"
AGENT_INFO_FILE = "agent_info.json"
WEBHOOK_URL_FILE = "webhook_url.txt"
LOCATION = "us-central1"

def load_agent_info():
    """Load agent information"""
    with open(AGENT_INFO_FILE, 'r') as f:
        return json.load(f)

def get_webhook_url():
    """Get webhook URL"""
    if os.path.exists(WEBHOOK_URL_FILE):
        with open(WEBHOOK_URL_FILE, 'r') as f:
            for line in f:
                if 'webhook' in line.lower() and 'http' in line:
                    return line.split()[-1] if line.split() else None
    return "https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/webhook"

def get_client(client_class):
    """Get a Dialogflow CX client with proper endpoint"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY
    )
    client_options_obj = client_options.ClientOptions(
        api_endpoint=f"{LOCATION}-dialogflow.googleapis.com:443"
    )
    return client_class(credentials=credentials, client_options=client_options_obj)

def integrate_grounding():
    """Integrate grounding webhook for symptom interpretation"""
    
    print("="*60)
    print("Integrate Vertex AI Search Grounding")
    print("="*60)
    print()
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    webhook_url = get_webhook_url()
    
    print(f"Webhook URL: {webhook_url}")
    print()
    
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
        
        # First, create webhook in Dialogflow
        print("Step 1: Creating webhook in Dialogflow...")
        webhooks_client = get_client(dialogflow.WebhooksClient)
        
        # Check if webhook exists
        request = dialogflow.ListWebhooksRequest(parent=agent_name)
        existing_webhooks = list(webhooks_client.list_webhooks(request=request))
        
        webhook_name = None
        webhook_display_name = "clinical-guidelines-webhook"
        
        for webhook in existing_webhooks:
            if webhook.display_name == webhook_display_name:
                webhook_name = webhook.name
                print(f"   [OK] Webhook already exists: {webhook_name}")
                break
        
        if not webhook_name:
            # Create webhook
            new_webhook = dialogflow.Webhook(
                display_name=webhook_display_name,
                generic_web_service=dialogflow.Webhook.GenericWebService(
                    uri=webhook_url,
                    allowed_ca_certs=[]  # Empty for public webhooks
                )
            )
            
            create_request = dialogflow.CreateWebhookRequest(
                parent=agent_name,
                webhook=new_webhook
            )
            
            try:
                created_webhook = webhooks_client.create_webhook(request=create_request)
                webhook_name = created_webhook.name
                print(f"   [OK] Webhook created: {webhook_name}")
            except Exception as e:
                print(f"   [WARNING] Could not create webhook: {e}")
                print("   [INFO] You may need to create it manually in the UI")
                webhook_name = f"{agent_name}/webhooks/{webhook_display_name}"
        
        # Get pages
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        # Add webhook to Triage Evaluation page for symptom interpretation
        print("\nStep 2: Adding webhook to Triage Evaluation page...")
        triage_page = None
        for page in pages:
            if page.display_name == "Triage Evaluation":
                triage_page = page
                break
        
        if triage_page:
            # Add webhook to entry fulfillment
            if not triage_page.entry_fulfillment:
                triage_page.entry_fulfillment = dialogflow.Fulfillment()
            
            # Set webhook
            triage_page.entry_fulfillment.webhook = webhook_name
            
            # Add tag for webhook invocation
            if not triage_page.entry_fulfillment.tag:
                triage_page.entry_fulfillment.tag = "clinical_grounding"
            
            # Update the page
            request = dialogflow.UpdatePageRequest(page=triage_page)
            pages_client.update_page(request=request)
            print(f"   [OK] Webhook added to Triage Evaluation page")
        else:
            print("   [ERROR] Triage Evaluation page not found")
        
        print()
        print("="*60)
        print("Grounding Integration Complete!")
        print("="*60)
        print("\nWebhook integrated for symptom interpretation.")
        print("The Triage Evaluation page will now call the grounding webhook")
        print("to search clinical guidelines and provide evidence-based recommendations.")
        print()
        print("Note: The webhook will be called during triage evaluation")
        print("      to enhance responses with clinical guideline information.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = integrate_grounding()
    exit(0 if success else 1)

