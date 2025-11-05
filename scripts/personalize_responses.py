#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personalize agent responses - use user names, reference previous info, show empathy
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

def personalize_responses():
    """Add personalization to agent responses"""
    
    print("="*60)
    print("Personalize Agent Responses")
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
        
        # Update Start page greeting
        start_page = None
        symptom_intake_page = None
        triage_page = None
        summary_page = None
        
        for page in pages:
            if page.display_name == "Start":
                start_page = page
            elif page.display_name == "Symptom Intake":
                symptom_intake_page = page
            elif page.display_name == "Triage Evaluation":
                triage_page = page
            elif page.display_name == "Summary":
                summary_page = page
        
        print("Personalizing responses...")
        print()
        
        # 1. Personalize Start page greeting
        if start_page:
            if not start_page.entry_fulfillment:
                start_page.entry_fulfillment = dialogflow.Fulfillment()
            
            start_page.entry_fulfillment.messages = [
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Hello! I'm here to help you describe your symptoms so we can determine the best next steps for your care. "
                            "What symptoms are you experiencing today?"
                        ]
                    )
                )
            ]
            print("  [OK] Updated Start page greeting")
        
        # 2. Personalize Symptom Intake entry
        if symptom_intake_page:
            if not symptom_intake_page.entry_fulfillment:
                symptom_intake_page.entry_fulfillment = dialogflow.Fulfillment()
            
            symptom_intake_page.entry_fulfillment.messages = [
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "I understand you're experiencing {symptom_type}. Let me gather some information to better understand your situation and determine the appropriate level of care."
                        ]
                    )
                )
            ]
            print("  [OK] Updated Symptom Intake entry message")
        
        # 3. Personalize Triage Evaluation responses
        if triage_page and triage_page.transition_routes:
            for route in triage_page.transition_routes:
                if route.trigger_fulfillment and route.trigger_fulfillment.messages:
                    # Update high urgency message
                    if "high" in route.condition.lower() or "emergency" in str(route.trigger_fulfillment.messages).lower():
                        route.trigger_fulfillment.messages = [
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[
                                        "Based on the symptoms you've described—{symptom_type} with severity {severity}/10 and duration of {duration}—this may require immediate medical attention. "
                                        "I'm concerned about your symptoms and want to ensure you get the right care.\n\n"
                                        "I recommend:\n"
                                        "• Calling your healthcare provider's emergency line, or\n"
                                        "• Going to the nearest emergency department or urgent care center\n\n"
                                        "If you're experiencing a life-threatening emergency, please call 911 immediately."
                                    ]
                                )
                            )
                        ]
                    # Update medium urgency message
                    elif "medium" in str(route.trigger_fulfillment.messages).lower():
                        route.trigger_fulfillment.messages = [
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[
                                        "Based on your symptoms—{symptom_type} at severity {severity}/10—I recommend scheduling a same-week appointment with your "
                                        "primary care provider or using our telehealth service. Your symptoms warrant medical evaluation, but they don't appear to require immediate emergency care.\n\n"
                                        "I understand this may be concerning, and I want to make sure you get the care you need."
                                    ]
                                )
                            )
                        ]
                    # Update low urgency message
                    else:
                        route.trigger_fulfillment.messages = [
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[
                                        "Based on the symptoms you've described—{symptom_type} with severity {severity}/10 that started {duration}—this may improve with rest and self-care measures. "
                                        "However, if your symptoms persist beyond 3 days or worsen, please schedule a follow-up with your healthcare provider.\n\n"
                                        "Don't hesitate to seek care if you have any concerns. Your health is important to us."
                                    ]
                                )
                            )
                        ]
            print("  [OK] Updated Triage Evaluation messages (personalized)")
        
        # 4. Personalize Summary page
        if summary_page:
            if not summary_page.entry_fulfillment:
                summary_page.entry_fulfillment = dialogflow.Fulfillment()
            
            summary_page.entry_fulfillment.messages = [
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Thank you for sharing that information with me. Here's a summary of what we've discussed:\n\n"
                            "**Symptom:** {symptom_type}\n"
                            "**Duration:** {duration}\n"
                            "**Severity:** {severity}/10\n"
                            "**Triage Level:** {triage}\n"
                            "**Recommendation:** {recommendation}\n\n"
                            "This information will be shared with your care team. If you have any additional concerns or if your symptoms change, please don't hesitate to reach out. "
                            "We're here to help you get the care you need."
                        ]
                    )
                )
            ]
            print("  [OK] Updated Summary page (personalized)")
        
        # Update all pages
        pages_to_update = [start_page, symptom_intake_page, triage_page, summary_page]
        for page in pages_to_update:
            if page:
                request = dialogflow.UpdatePageRequest(page=page)
                pages_client.update_page(request=request)
        
        print()
        print("[OK] Responses personalized")
        print()
        print("Improvements:")
        print("  ✓ More empathetic language")
        print("  ✓ References specific symptoms and values")
        print("  ✓ Shows understanding and concern")
        print("  ✓ Clearer next steps")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = personalize_responses()
    exit(0 if success else 1)

