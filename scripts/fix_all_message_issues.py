#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix all message issues: parameter substitution, duplicates, and webhook messages
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

def fix_all_message_issues():
    """Fix parameter substitution and duplicate messages"""
    
    print("="*60)
    print("Fix All Message Issues")
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
        
        # Find all pages
        symptom_intake_page = None
        clarifying_page = None
        triage_page = None
        summary_page = None
        
        for page in pages:
            if page.display_name == "Symptom Intake":
                symptom_intake_page = page
            elif page.display_name == "Clarifying Questions":
                clarifying_page = page
            elif page.display_name == "Triage Evaluation":
                triage_page = page
            elif page.display_name == "Summary":
                summary_page = page
        
        print("Fixing message issues...")
        print()
        
        # 1. Fix Symptom Intake - remove placeholder, use simple message
        if symptom_intake_page:
            symptom_intake_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "I understand you're experiencing symptoms. Let me gather some information to better understand your situation and determine the appropriate level of care."
                            ]
                        )
                    )
                ]
            )
            print("  [OK] Fixed Symptom Intake entry message")
        
        # 2. Fix Clarifying Questions - single message
        if clarifying_page:
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
            print("  [OK] Fixed Clarifying Questions entry message")
        
        # 3. Fix Triage Evaluation - remove entry fulfillment, let routes handle messages
        if triage_page:
            # Remove entry fulfillment to prevent duplicate messages
            triage_page.entry_fulfillment = None
            
            # Ensure transition routes have clean messages without placeholders
            if triage_page.transition_routes:
                for route in triage_page.transition_routes:
                    if route.trigger_fulfillment:
                        # Update messages to remove placeholders and use proper syntax
                        messages = []
                        
                        # Determine which route this is based on condition
                        condition = route.condition.lower() if route.condition else ""
                        
                        if "emergency" in condition or "high" in condition or "severity >= 9" in condition:
                            messages.append(
                                dialogflow.ResponseMessage(
                                    text=dialogflow.ResponseMessage.Text(
                                        text=[
                                            "Based on your symptoms, this requires immediate medical attention. I'm concerned about your condition and want to ensure you get the right care.\n\n"
                                            "🚨 **Immediate Action Required:**\n"
                                            "• Call your healthcare provider's emergency line immediately, OR\n"
                                            "• Go to the nearest emergency department or urgent care center\n\n"
                                            "If you're experiencing a life-threatening emergency, please call 911 immediately.\n\n"
                                            "Your safety is our top priority."
                                        ]
                                    )
                                )
                            )
                        elif "urgent" in condition or "severity >= 7" in condition:
                            messages.append(
                                dialogflow.ResponseMessage(
                                    text=dialogflow.ResponseMessage.Text(
                                        text=[
                                            "Based on your symptoms, I recommend scheduling a same-day appointment with your healthcare provider or using our telehealth service. "
                                            "Your symptoms warrant medical evaluation, but they don't appear to require immediate emergency care.\n\n"
                                            "I understand this may be concerning, and I want to make sure you get the care you need."
                                        ]
                                    )
                                )
                            )
                        elif "same" in condition and "week" in condition:
                            messages.append(
                                dialogflow.ResponseMessage(
                                    text=dialogflow.ResponseMessage.Text(
                                        text=[
                                            "Based on your symptoms, I recommend scheduling an appointment with your healthcare provider within the next week. "
                                            "While your symptoms don't appear to require immediate attention, they should be evaluated by a medical professional.\n\n"
                                            "Your provider can help determine the cause and appropriate treatment for your symptoms."
                                        ]
                                    )
                                )
                            )
                        else:
                            # Default/routine
                            messages.append(
                                dialogflow.ResponseMessage(
                                    text=dialogflow.ResponseMessage.Text(
                                        text=[
                                            "Based on the symptoms you've described, this may improve with rest and self-care measures. "
                                            "Your symptoms appear to be mild and manageable with home care.\n\n"
                                            "🏠 **Recommended Action:**\n"
                                            "• Rest and monitor your symptoms\n"
                                            "• Try basic self-care measures (hydration, rest, over-the-counter pain relief if appropriate)\n"
                                            "• Schedule a routine appointment if symptoms persist beyond 3 days or worsen\n\n"
                                            "If your symptoms change or you have any concerns, don't hesitate to contact your healthcare provider. "
                                            "We're here to help if you need us."
                                        ]
                                    )
                                )
                            )
                        
                        route.trigger_fulfillment.messages = messages
            print("  [OK] Fixed Triage Evaluation (removed entry fulfillment, cleaned routes)")
        
        # 4. Fix Summary page - use proper parameter syntax
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
                                "This information will be shared with your care team. If you have any additional concerns or if your symptoms change, please don't hesitate to reach out. "
                                "We're here to help you get the care you need."
                            ]
                        )
                    )
                ]
            )
            print("  [OK] Fixed Summary page (proper parameter syntax)")
        
        # Update all pages
        pages_to_update = [symptom_intake_page, clarifying_page, triage_page, summary_page]
        for page in pages_to_update:
            if page:
                request = dialogflow.UpdatePageRequest(page=page)
                pages_client.update_page(request=request)
        
        print()
        print("[OK] All message issues fixed")
        print()
        print("Improvements:")
        print("  ✓ Removed {parameter} placeholders")
        print("  ✓ Using $session.params.parameter syntax")
        print("  ✓ Removed duplicate entry fulfillments")
        print("  ✓ Single message per page")
        print("  ✓ Cleaner conversation flow")
        print()
        print("The agent will now:")
        print("  - Show one message per page")
        print("  - Substitute parameters correctly")
        print("  - No duplicate messages")
        print("  - Cleaner, more professional responses")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_all_message_issues()
    exit(0 if success else 1)

