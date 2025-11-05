#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix parameter substitution in messages - use Dialogflow syntax instead of placeholders
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

def fix_parameter_substitution():
    """Fix messages to use Dialogflow parameter syntax"""
    
    print("="*60)
    print("Fix Parameter Substitution in Messages")
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
        symptom_intake_page = None
        triage_page = None
        summary_page = None
        
        for page in pages:
            if page.display_name == "Symptom Intake":
                symptom_intake_page = page
            elif page.display_name == "Triage Evaluation":
                triage_page = page
            elif page.display_name == "Summary":
                summary_page = page
        
        print("Fixing parameter substitution...")
        print()
        
        # 1. Fix Symptom Intake entry message
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
        
        # 2. Fix Triage Evaluation messages - use conditional responses with proper syntax
        if triage_page and triage_page.transition_routes:
            for route in triage_page.transition_routes:
                if route.trigger_fulfillment:
                    # Update messages to use Dialogflow parameter syntax
                    # Dialogflow uses $session.params.parameter_name for substitution
                    
                    # Emergency route
                    if "emergency" in route.condition.lower() or (route.trigger_fulfillment.messages and any("emergency" in str(m).lower() for m in route.trigger_fulfillment.messages)):
                        route.trigger_fulfillment.messages = [
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
                        ]
                    
                    # Urgent route
                    elif "urgent" in str(route.trigger_fulfillment.messages).lower():
                        route.trigger_fulfillment.messages = [
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[
                                        "Based on your symptoms, I recommend scheduling a same-day appointment with your healthcare provider or using our telehealth service. "
                                        "Your symptoms warrant medical evaluation, but they don't appear to require immediate emergency care.\n\n"
                                        "I understand this may be concerning, and I want to make sure you get the care you need."
                                    ]
                                )
                            )
                        ]
                    
                    # Same-week route
                    elif "same" in str(route.trigger_fulfillment.messages).lower() and "week" in str(route.trigger_fulfillment.messages).lower():
                        route.trigger_fulfillment.messages = [
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[
                                        "Based on your symptoms, I recommend scheduling an appointment with your healthcare provider within the next week. "
                                        "While your symptoms don't appear to require immediate attention, they should be evaluated by a medical professional.\n\n"
                                        "Your provider can help determine the cause and appropriate treatment for your symptoms."
                                    ]
                                )
                            )
                        ]
                    
                    # Routine route (default)
                    else:
                        route.trigger_fulfillment.messages = [
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
                        ]
            print("  [OK] Fixed Triage Evaluation messages")
        
        # 3. Fix Summary page - remove duplicate messages and use proper syntax
        if summary_page:
            # Clear any duplicate messages
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
            print("  [OK] Fixed Summary page (removed duplicates, added parameter syntax)")
        
        # 4. Remove duplicate webhook messages from Triage Evaluation entry
        if triage_page:
            # Keep entry fulfillment simple - just one message
            if triage_page.entry_fulfillment:
                # Check if it has multiple messages or webhook
                if len(triage_page.entry_fulfillment.messages) > 1:
                    # Keep only the first message
                    triage_page.entry_fulfillment.messages = [
                        triage_page.entry_fulfillment.messages[0]
                    ]
                
                # Remove webhook if it's causing duplicate messages
                # We'll keep webhook but ensure it doesn't duplicate
                if triage_page.entry_fulfillment.webhook:
                    # Webhook can stay, but we'll ensure messages are clean
                    pass
            
            # Simplify entry fulfillment
            if not triage_page.entry_fulfillment:
                triage_page.entry_fulfillment = dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=[
                                    "Based on your symptoms, I'm evaluating the appropriate level of care you need."
                                ]
                            )
                        )
                    ]
                )
            print("  [OK] Cleaned up Triage Evaluation entry fulfillment")
        
        # Update all pages
        pages_to_update = [symptom_intake_page, triage_page, summary_page]
        for page in pages_to_update:
            if page:
                request = dialogflow.UpdatePageRequest(page=page)
                pages_client.update_page(request=request)
        
        print()
        print("[OK] Parameter substitution fixed")
        print()
        print("Improvements:")
        print("  ✓ Removed placeholder syntax ({parameter})")
        print("  ✓ Using Dialogflow parameter syntax ($session.params.parameter)")
        print("  ✓ Removed duplicate messages")
        print("  ✓ Simplified entry fulfillments")
        print("  ✓ Cleaner, single-message responses")
        print()
        print("Note: Dialogflow will automatically substitute $session.params.parameter")
        print("      with actual values when the conversation runs.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_parameter_substitution()
    exit(0 if success else 1)

