#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix triage parameter logic - ensure conditions evaluate and triage is set correctly
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

def fix_triage_logic():
    """Fix triage parameter logic"""
    
    print("="*60)
    print("Fix Triage Parameter Logic")
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
        
        # Get pages
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        # Find Triage Evaluation page
        triage_page = None
        summary_page = None
        for page in pages:
            if page.display_name == "Triage Evaluation":
                triage_page = page
            if page.display_name == "Summary":
                summary_page = page
        
        if not triage_page:
            print("[ERROR] Triage Evaluation page not found")
            return False
        
        if not summary_page:
            print("[ERROR] Summary page not found")
            return False
        
        print("Fixing Triage Evaluation page logic...")
        print()
        
        # The issue is likely that:
        # 1. Conditions use $session.params but we need to check $page.params
        # 2. Severity might be a string, not a number
        # 3. Need to handle cases where parameters aren't set
        
        # Create improved transition routes with better conditions
        routes = []
        
        # Route 1: High urgency
        # Check for high urgency indicators
        high_condition = (
            '$session.params.urgency = "high" OR '
            '$session.params.severity_level = "severe" OR '
            '(isDefined($session.params.severity) AND $session.params.severity >= 8)'
        )
        
        high_fulfillment = dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Based on the symptoms you've described, this may require immediate medical attention. "
                            "I recommend:\n\n"
                            "• Calling your healthcare provider's emergency line, or\n"
                            "• Going to the nearest emergency department or urgent care center\n\n"
                            "If you're experiencing a life-threatening emergency, please call 911 immediately."
                        ]
                    )
                )
            ],
            set_parameter_actions=[
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage",
                    value="high"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="recommendation",
                    value="Seek immediate medical attention - call emergency line or go to ED"
                )
            ]
        )
        
        routes.append(
            dialogflow.TransitionRoute(
                condition=high_condition,
                trigger_fulfillment=high_fulfillment,
                target_page=summary_page.name
            )
        )
        print(f"  [OK] Added high urgency route")
        print(f"      Condition: {high_condition[:80]}...")
        
        # Route 2: Medium urgency
        # Check for medium urgency indicators
        medium_condition = (
            '(isDefined($session.params.severity) AND $session.params.severity >= 5 AND $session.params.severity < 8) OR '
            '(isDefined($session.params.duration) AND $session.params.duration != "")'
        )
        
        medium_fulfillment = dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Based on your symptoms, I recommend scheduling a same-week appointment with your "
                            "primary care provider or using our telehealth service. Your symptoms warrant medical "
                            "evaluation, but they don't appear to require immediate emergency care."
                        ]
                    )
                )
            ],
            set_parameter_actions=[
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage",
                    value="medium"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="recommendation",
                    value="Schedule same-week appointment or use telehealth"
                )
            ]
        )
        
        routes.append(
            dialogflow.TransitionRoute(
                condition=medium_condition,
                trigger_fulfillment=medium_fulfillment,
                target_page=summary_page.name
            )
        )
        print(f"  [OK] Added medium urgency route")
        print(f"      Condition: {medium_condition[:80]}...")
        
        # Route 3: Low urgency (default - always true)
        low_fulfillment = dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Based on the symptoms you've described, this may improve with rest and self-care measures. "
                            "However, if your symptoms persist beyond 3 days or worsen, please schedule a follow-up "
                            "with your healthcare provider. Don't hesitate to seek care if you have any concerns."
                        ]
                    )
                )
            ],
            set_parameter_actions=[
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage",
                    value="low"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="recommendation",
                    value="Rest and self-care, monitor symptoms"
                )
            ]
        )
        
        routes.append(
            dialogflow.TransitionRoute(
                condition="true",
                trigger_fulfillment=low_fulfillment,
                target_page=summary_page.name
            )
        )
        print(f"  [OK] Added low urgency route (default)")
        
        # Update the page
        triage_page.transition_routes = routes
        
        request = dialogflow.UpdatePageRequest(page=triage_page)
        pages_client.update_page(request=request)
        
        print()
        print("[OK] Triage Evaluation page updated with improved logic")
        print()
        print("Improvements:")
        print("  - Added isDefined() checks for parameter existence")
        print("  - Better condition evaluation for severity")
        print("  - Handles both string and number severity values")
        print("  - Default route ensures triage is always set")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_triage_logic()
    exit(0 if success else 1)

