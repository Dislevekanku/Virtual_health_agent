#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improve conversation flow: Greeting → symptom intake → triage → recommendation
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

def improve_flow():
    """Improve conversation flow with better greetings and transitions"""
    
    print("="*60)
    print("Improve Conversation Flow")
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
        
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        # 1. Improve Start Page greeting
        print("1. Improving Start Page greeting...")
        start_page = None
        for page in pages:
            if page.display_name == "Start":
                start_page = page
                break
        
        if start_page:
            improved_greeting = (
                "Hello! I'm your virtual health assistant. I'm here to help you describe your "
                "symptoms so we can determine the best next steps for your care.\n\n"
                "What symptoms are you experiencing today?"
            )
            
            start_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[improved_greeting]
                        )
                    )
                ]
            )
            
            request = dialogflow.UpdatePageRequest(page=start_page)
            pages_client.update_page(request=request)
            print("   [OK] Start page greeting updated")
        
        # 2. Improve Symptom Intake page entry
        print("\n2. Improving Symptom Intake page...")
        symptom_intake_page = None
        for page in pages:
            if page.display_name == "Symptom Intake":
                symptom_intake_page = page
                break
        
        if symptom_intake_page:
            # Personalized entry message
            symptom_intake_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "Thank you for that information. To help me better understand your situation, "
                                "I'll need to ask you a few questions about your symptoms."
                            ]
                        )
                    )
                ]
            )
            
            request = dialogflow.UpdatePageRequest(page=symptom_intake_page)
            pages_client.update_page(request=request)
            print("   [OK] Symptom Intake entry message updated")
        
        # 3. Improve Clarifying Questions page
        print("\n3. Improving Clarifying Questions page...")
        clarifying_page = None
        for page in pages:
            if page.display_name == "Clarifying Questions":
                clarifying_page = page
                break
        
        if clarifying_page:
            clarifying_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "Thank you for providing those details. Let me ask a few clarifying questions "
                                "to better understand your situation and determine the appropriate level of care."
                            ]
                        )
                    )
                ]
            )
            
            request = dialogflow.UpdatePageRequest(page=clarifying_page)
            pages_client.update_page(request=request)
            print("   [OK] Clarifying Questions entry message updated")
        
        # 4. Improve Triage Evaluation page with better recommendations
        print("\n4. Improving Triage Evaluation page...")
        triage_page = None
        for page in pages:
            if page.display_name == "Triage Evaluation":
                triage_page = page
                break
        
        if triage_page:
            # Update triage routes with better recommendations
            summary_page = None
            for page in pages:
                if page.display_name == "Summary":
                    summary_page = page
                    break
            
            summary_name = summary_page.name if summary_page else None
            
            # High urgency - improved message
            high_urgency_msg = (
                "Based on the symptoms you've described, this may require immediate medical attention. "
                "I recommend:\n\n"
                "• Calling your healthcare provider's emergency line, or\n"
                "• Going to the nearest emergency department or urgent care center\n\n"
                "If you're experiencing a life-threatening emergency, please call 911 immediately."
            )
            
            # Medium urgency - improved message
            medium_urgency_msg = (
                "Based on your symptoms, I recommend scheduling a same-week appointment with your "
                "primary care provider or using our telehealth service. Your symptoms warrant medical "
                "evaluation, but they don't appear to require immediate emergency care."
            )
            
            # Low urgency - improved message
            low_urgency_msg = (
                "Based on the symptoms you've described, this may improve with rest and self-care measures. "
                "However, if your symptoms persist beyond 3 days or worsen, please schedule a follow-up "
                "with your healthcare provider. Don't hesitate to seek care if you have any concerns."
            )
            
            new_routes = []
            
            # High urgency route
            new_routes.append(
                dialogflow.TransitionRoute(
                    condition='$session.params.severity >= 8 OR $session.params.urgency = "high"',
                    trigger_fulfillment=dialogflow.Fulfillment(
                        messages=[
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[high_urgency_msg]
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
                    ),
                    target_page=summary_name
                )
            )
            
            # Medium urgency route
            new_routes.append(
                dialogflow.TransitionRoute(
                    condition='$session.params.severity >= 5',
                    trigger_fulfillment=dialogflow.Fulfillment(
                        messages=[
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[medium_urgency_msg]
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
                    ),
                    target_page=summary_name
                )
            )
            
            # Low urgency route
            new_routes.append(
                dialogflow.TransitionRoute(
                    condition="true",
                    trigger_fulfillment=dialogflow.Fulfillment(
                        messages=[
                            dialogflow.ResponseMessage(
                                text=dialogflow.ResponseMessage.Text(
                                    text=[low_urgency_msg]
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
                    ),
                    target_page=summary_name
                )
            )
            
            triage_page.transition_routes = new_routes
            
            request = dialogflow.UpdatePageRequest(page=triage_page)
            pages_client.update_page(request=request)
            print("   [OK] Triage Evaluation messages updated")
        
        # 5. Improve Summary page
        print("\n5. Improving Summary page...")
        summary_page = None
        for page in pages:
            if page.display_name == "Summary":
                summary_page = page
                break
        
        if summary_page:
            summary_text = (
                "Here's a summary of our conversation:\n\n"
                "**Symptom:** {symptom_type}\n"
                "**Duration:** {duration}\n"
                "**Severity:** {severity}/10\n"
                "**Triage Level:** {triage}\n"
                "**Recommendation:** {recommendation}\n\n"
                "This information will be shared with your care team. If you have any additional "
                "concerns or if your symptoms change, please don't hesitate to reach out."
            ).format(
                symptom_type="$session.params.symptom_type",
                duration="$session.params.duration",
                severity="$session.params.severity",
                triage="$session.params.triage",
                recommendation="$session.params.recommendation"
            )
            
            summary_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[summary_text]
                        )
                    )
                ]
            )
            
            request = dialogflow.UpdatePageRequest(page=summary_page)
            pages_client.update_page(request=request)
            print("   [OK] Summary page updated")
        
        print()
        print("="*60)
        print("Conversation Flow Improved!")
        print("="*60)
        print("\nChanges made:")
        print("  ✓ Improved greeting on Start page")
        print("  ✓ Better entry messages for each page")
        print("  ✓ Enhanced triage recommendations with clear next steps")
        print("  ✓ Improved summary with structured format")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = improve_flow()
    exit(0 if success else 1)

