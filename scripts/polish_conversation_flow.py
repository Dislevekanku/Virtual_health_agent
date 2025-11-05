#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polish conversation flow and improve response quality
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

def improve_start_page():
    """Improve Start page greeting"""
    
    print("Improving Start page greeting...")
    
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    flows_client = get_client(dialogflow.FlowsClient)
    request = dialogflow.ListFlowsRequest(parent=agent_name)
    flows = list(flows_client.list_flows(request=request))
    
    flow_name = None
    for flow in flows:
        if flow.display_name == "Default Start Flow":
            flow_name = flow.name
            break
    
    if not flow_name:
        return False
    
    pages_client = get_client(dialogflow.PagesClient)
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages = list(pages_client.list_pages(request=request))
    
    start_page = None
    for page in pages:
        if page.display_name == "Start":
            start_page = page
            break
    
    if not start_page:
        return False
    
    # Improved greeting
    improved_greeting = (
        "Hello! I'm your virtual health assistant. I'm here to help gather information about "
        "your symptoms so we can determine the best next steps for your care. "
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
    
    print("  [OK] Start page greeting updated")
    return True

def improve_symptom_intake():
    """Improve Symptom Intake page responses"""
    
    print("Improving Symptom Intake page...")
    
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    flows_client = get_client(dialogflow.FlowsClient)
    request = dialogflow.ListFlowsRequest(parent=agent_name)
    flows = list(flows_client.list_flows(request=request))
    
    flow_name = None
    for flow in flows:
        if flow.display_name == "Default Start Flow":
            flow_name = flow.name
            break
    
    if not flow_name:
        return False
    
    pages_client = get_client(dialogflow.PagesClient)
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages = list(pages_client.list_pages(request=request))
    
    symptom_intake = None
    for page in pages:
        if page.display_name == "Symptom Intake":
            symptom_intake = page
            break
    
    if not symptom_intake:
        return False
    
    # Improved entry message
    improved_entry = (
        "Thank you for sharing. To better understand your situation and provide appropriate care guidance, "
        "I'll need to ask you a few questions about your symptoms."
    )
    
    symptom_intake.entry_fulfillment = dialogflow.Fulfillment(
        messages=[
            dialogflow.ResponseMessage(
                text=dialogflow.ResponseMessage.Text(
                    text=[improved_entry]
                )
            )
        ]
    )
    
    # Improve parameter prompts
    if symptom_intake.form and symptom_intake.form.parameters:
        for param in symptom_intake.form.parameters:
            if param.display_name == "duration":
                if param.fill_behavior and param.fill_behavior.initial_prompt_fulfillment:
                    param.fill_behavior.initial_prompt_fulfillment.messages = [
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=["When did your symptoms begin? For example, 'this morning', '2 days ago', or 'last week'."]
                            )
                        )
                    ]
            
            elif param.display_name == "severity":
                if param.fill_behavior and param.fill_behavior.initial_prompt_fulfillment:
                    param.fill_behavior.initial_prompt_fulfillment.messages = [
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=["On a scale of 0 to 10, where 0 means no pain or discomfort and 10 means the worst possible pain, how would you rate your symptoms?"]
                            )
                        )
                    ]
    
    request = dialogflow.UpdatePageRequest(page=symptom_intake)
    pages_client.update_page(request=request)
    
    print("  [OK] Symptom Intake page improved")
    return True

def improve_triage_responses():
    """Improve Triage Evaluation page with better recommendations"""
    
    print("Improving Triage Evaluation page...")
    
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    flows_client = get_client(dialogflow.FlowsClient)
    request = dialogflow.ListFlowsRequest(parent=agent_name)
    flows = list(flows_client.list_flows(request=request))
    
    flow_name = None
    for flow in flows:
        if flow.display_name == "Default Start Flow":
            flow_name = flow.name
            break
    
    if not flow_name:
        return False
    
    pages_client = get_client(dialogflow.PagesClient)
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages = list(pages_client.list_pages(request=request))
    
    triage_page = None
    for page in pages:
        if page.display_name == "Triage Evaluation":
            triage_page = page
            break
    
    if not triage_page:
        return False
    
    # Get Summary page
    summary_page = None
    for page in pages:
        if page.display_name == "Summary":
            summary_page = page
            break
    
    # Improved triage messages with recommendations
    high_urgency_message = (
        "Based on your symptoms, I recommend seeking immediate medical attention. "
        "Please call your healthcare provider's emergency line or go to the nearest emergency department. "
        "Your symptoms suggest a condition that requires prompt evaluation."
    )
    
    medium_urgency_message = (
        "Based on your symptoms, I recommend scheduling an appointment with your healthcare provider "
        "within the next few days, or using our telehealth service if available. "
        "Your symptoms warrant professional evaluation but are not immediately life-threatening."
    )
    
    low_urgency_message = (
        "Based on your symptoms, these may improve with rest and home care. "
        "However, if your symptoms persist beyond 3-5 days, worsen, or you develop new symptoms, "
        "please contact your healthcare provider. I'll provide you with a summary of our conversation."
    )
    
    # Update transition routes with improved messages
    new_routes = []
    
    # High urgency
    high_route = dialogflow.TransitionRoute(
        condition='$session.params.severity >= 8 OR $session.params.urgency = "high"',
        trigger_fulfillment=dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[high_urgency_message]
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
                    value="Seek immediate medical attention - call emergency line or go to ER"
                )
            ]
        ),
        target_page=summary_page.name if summary_page else None
    )
    new_routes.append(high_route)
    
    # Medium urgency
    medium_route = dialogflow.TransitionRoute(
        condition='$session.params.severity >= 5',
        trigger_fulfillment=dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[medium_urgency_message]
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
                    value="Schedule appointment within next few days or use telehealth"
                )
            ]
        ),
        target_page=summary_page.name if summary_page else None
    )
    new_routes.append(medium_route)
    
    # Low urgency
    low_route = dialogflow.TransitionRoute(
        condition="true",
        trigger_fulfillment=dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[low_urgency_message]
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
                    value="Monitor symptoms, rest and home care. Contact provider if symptoms persist or worsen."
                )
            ]
        ),
        target_page=summary_page.name if summary_page else None
    )
    new_routes.append(low_route)
    
    triage_page.transition_routes = new_routes
    
    request = dialogflow.UpdatePageRequest(page=triage_page)
    pages_client.update_page(request=request)
    
    print("  [OK] Triage Evaluation page improved with recommendations")
    return True

def improve_summary_page():
    """Improve Summary page with better formatting"""
    
    print("Improving Summary page...")
    
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    flows_client = get_client(dialogflow.FlowsClient)
    request = dialogflow.ListFlowsRequest(parent=agent_name)
    flows = list(flows_client.list_flows(request=request))
    
    flow_name = None
    for flow in flows:
        if flow.display_name == "Default Start Flow":
            flow_name = flow.name
            break
    
    if not flow_name:
        return False
    
    pages_client = get_client(dialogflow.PagesClient)
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages = list(pages_client.list_pages(request=request))
    
    summary_page = None
    for page in pages:
        if page.display_name == "Summary":
            summary_page = page
            break
    
    if not summary_page:
        return False
    
    # Improved summary format
    improved_summary = (
        "Here's a summary of our conversation:\n\n"
        "📋 Symptom: $session.params.symptom_type\n"
        "⏱️ Duration: $session.params.duration\n"
        "📊 Severity: $session.params.severity/10\n"
        "🚨 Triage Level: $session.params.triage\n"
        "💡 Recommendation: $session.params.recommendation\n\n"
        "This information will be shared with your care team. "
        "If you have any questions or if your symptoms change, please don't hesitate to reach out."
    )
    
    summary_page.entry_fulfillment = dialogflow.Fulfillment(
        messages=[
            dialogflow.ResponseMessage(
                text=dialogflow.ResponseMessage.Text(
                    text=[improved_summary]
                )
            )
        ]
    )
    
    request = dialogflow.UpdatePageRequest(page=summary_page)
    pages_client.update_page(request=request)
    
    print("  [OK] Summary page improved")
    return True

def main():
    """Main function"""
    
    print("="*60)
    print("Polish Conversation Flow and Responses")
    print("="*60)
    print()
    
    results = []
    
    results.append(("Start Page", improve_start_page()))
    results.append(("Symptom Intake", improve_symptom_intake()))
    results.append(("Triage Evaluation", improve_triage_responses()))
    results.append(("Summary Page", improve_summary_page()))
    
    print()
    print("="*60)
    print("Summary")
    print("="*60)
    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {name}")
    
    print()
    print("Conversation flow improvements complete!")
    print("Next steps:")
    print("  1. Test the improved flow")
    print("  2. Add few-shot examples (if needed)")
    print("  3. Integrate Vertex AI Search grounding")
    print()

if __name__ == "__main__":
    main()

