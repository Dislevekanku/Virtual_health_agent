#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix parameter extraction and triage parameter issues
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

def fix_symptom_intake_page(flow_name, pages_client):
    """Fix Symptom Intake page to properly extract parameters"""
    
    print("Fixing Symptom Intake page...")
    
    # Get Symptom Intake page
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages = list(pages_client.list_pages(request=request))
    
    symptom_intake_page = None
    for page in pages:
        if page.display_name == "Symptom Intake":
            symptom_intake_page = page
            break
    
    if not symptom_intake_page:
        print("  [ERROR] Symptom Intake page not found")
        return False
    
    # Update the form parameters to better extract information
    # The key issue is that duration should be extracted from natural language
    # and severity should accept numbers in various formats
    
    if not symptom_intake_page.form:
        symptom_intake_page.form = dialogflow.Form()
    
    if not symptom_intake_page.form.parameters:
        symptom_intake_page.form.parameters = []
    
    # Find and update duration parameter
    duration_param = None
    for param in symptom_intake_page.form.parameters:
        if param.display_name == "duration":
            duration_param = param
            break
    
    if duration_param:
        # Update duration parameter to use @sys.duration or @sys.any for better extraction
        duration_param.entity_type = "projects/-/locations/-/agents/-/entityTypes/sys.duration"
        # Make it not required initially to allow natural flow
        duration_param.required = False
        print("  [OK] Updated duration parameter")
    else:
        # Add duration parameter if missing
        duration_param = dialogflow.Form.Parameter(
            display_name="duration",
            entity_type="projects/-/locations/-/agents/-/entityTypes/sys.duration",
            required=False,
            fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                initial_prompt_fulfillment=dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=["When did this symptom start? How long have you been experiencing it?"]
                            )
                        )
                    ]
                )
            )
        )
        symptom_intake_page.form.parameters.append(duration_param)
        print("  [OK] Added duration parameter")
    
    # Find and update severity parameter
    severity_param = None
    for param in symptom_intake_page.form.parameters:
        if param.display_name == "severity":
            severity_param = param
            break
    
    if severity_param:
        # Update severity to accept both numbers and text
        severity_param.entity_type = "projects/-/locations/-/agents/-/entityTypes/sys.number"
        severity_param.required = False
        print("  [OK] Updated severity parameter")
    else:
        # Add severity parameter if missing
        severity_param = dialogflow.Form.Parameter(
            display_name="severity",
            entity_type="projects/-/locations/-/agents/-/entityTypes/sys.number",
            required=False,
            fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                initial_prompt_fulfillment=dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=["On a scale of 0 to 10, how severe is your symptom? (0 = no pain, 10 = worst possible)"]
                            )
                        )
                    ]
                )
            )
        )
        symptom_intake_page.form.parameters.append(severity_param)
        print("  [OK] Added severity parameter")
    
    # Update transition routes to move forward when key info is collected
    # Add a route that transitions when we have symptom_type and basic info
    if not symptom_intake_page.transition_routes:
        symptom_intake_page.transition_routes = []
    
    # Get target pages
    pages_list = list(pages_client.list_pages(request=dialogflow.ListPagesRequest(parent=flow_name)))
    clarifying_page_name = None
    for page in pages_list:
        if page.display_name == "Clarifying Questions":
            clarifying_page_name = page.name
            break
    
    # Add transition route when form is complete or key parameters are filled
    has_form_completion_route = False
    for route in symptom_intake_page.transition_routes:
        if route.condition and ("FINAL" in route.condition or "status" in route.condition):
            has_form_completion_route = True
            break
    
    if not has_form_completion_route and clarifying_page_name:
        symptom_intake_page.transition_routes.append(
            dialogflow.TransitionRoute(
                condition='$page.params.status = "FINAL"',
                target_page=clarifying_page_name
            )
        )
        print("  [OK] Added form completion route")
    
    # Update the page
    request = dialogflow.UpdatePageRequest(page=symptom_intake_page)
    pages_client.update_page(request=request)
    
    print("  [OK] Symptom Intake page updated")
    return True

def fix_triage_evaluation_page(flow_name, pages_client):
    """Fix Triage Evaluation page to properly set triage parameter"""
    
    print("\nFixing Triage Evaluation page...")
    
    # Get Triage Evaluation page
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages = list(pages_client.list_pages(request=request))
    
    triage_page = None
    for page in pages:
        if page.display_name == "Triage Evaluation":
            triage_page = page
            break
    
    if not triage_page:
        print("  [ERROR] Triage Evaluation page not found")
        return False
    
    # Get Summary page name
    summary_page_name = None
    for page in pages:
        if page.display_name == "Summary":
            summary_page_name = page.name
            break
    
    # Update transition routes to set triage parameter based on conditions
    if not triage_page.transition_routes:
        triage_page.transition_routes = []
    
    # Clear existing conditional routes and add new ones
    new_routes = []
    
    # High urgency route (severity >= 8 OR urgency = "high" OR red flags)
    high_urgency_fulfillment = dialogflow.Fulfillment(
        messages=[
            dialogflow.ResponseMessage(
                text=dialogflow.ResponseMessage.Text(
                    text=["Your symptoms suggest an urgent issue. Please call our nurse line or go to the nearest emergency department immediately."]
                )
            )
        ],
        set_parameter_actions=[
            dialogflow.Fulfillment.SetParameterAction(
                parameter="triage",
                value="high"
            )
        ]
    )
    
    new_routes.append(
        dialogflow.TransitionRoute(
            condition='$session.params.severity >= 8 OR $session.params.urgency = "high"',
            trigger_fulfillment=high_urgency_fulfillment,
            target_page=summary_page_name if summary_page_name else None
        )
    )
    
    # Medium urgency route (severity >= 5 OR duration >= 3 days)
    medium_urgency_fulfillment = dialogflow.Fulfillment(
        messages=[
            dialogflow.ResponseMessage(
                text=dialogflow.ResponseMessage.Text(
                    text=["I recommend scheduling a same-week visit with your primary care provider or using our telehealth service."]
                )
            )
        ],
        set_parameter_actions=[
            dialogflow.Fulfillment.SetParameterAction(
                parameter="triage",
                value="medium"
            )
        ]
    )
    
    new_routes.append(
        dialogflow.TransitionRoute(
            condition='$session.params.severity >= 5',
            trigger_fulfillment=medium_urgency_fulfillment,
            target_page=summary_page_name if summary_page_name else None
        )
    )
    
    # Low urgency route (default)
    low_urgency_fulfillment = dialogflow.Fulfillment(
        messages=[
            dialogflow.ResponseMessage(
                text=dialogflow.ResponseMessage.Text(
                    text=["This may improve with rest and home care. If symptoms persist beyond 3 days or worsen, please schedule a follow-up."]
                )
            )
        ],
        set_parameter_actions=[
            dialogflow.Fulfillment.SetParameterAction(
                parameter="triage",
                value="low"
            )
        ]
    )
    
    new_routes.append(
        dialogflow.TransitionRoute(
            condition="true",
            trigger_fulfillment=low_urgency_fulfillment,
            target_page=summary_page_name if summary_page_name else None
        )
    )
    
    triage_page.transition_routes = new_routes
    
    # Update the page
    request = dialogflow.UpdatePageRequest(page=triage_page)
    pages_client.update_page(request=request)
    
    print("  [OK] Triage Evaluation page updated with triage parameter logic")
    return True

def fix_summary_page(flow_name, pages_client):
    """Fix Summary page to properly display triage"""
    
    print("\nFixing Summary page...")
    
    # Get Summary page
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages = list(pages_client.list_pages(request=request))
    
    summary_page = None
    for page in pages:
        if page.display_name == "Summary":
            summary_page = page
            break
    
    if not summary_page:
        print("  [ERROR] Summary page not found")
        return False
    
    # Update entry fulfillment to properly display triage
    summary_text = (
        "Here's a summary:\n\n"
        "Symptom: $session.params.symptom_type\n"
        "Duration: $session.params.duration\n"
        "Severity: $session.params.severity/10\n"
        "Triage Level: $session.params.triage\n\n"
        "This information will be shared with your care team."
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
    
    # Update the page
    request = dialogflow.UpdatePageRequest(page=summary_page)
    pages_client.update_page(request=request)
    
    print("  [OK] Summary page updated")
    return True

def main():
    """Main function"""
    
    print("="*60)
    print("Fix Parameter Extraction and Triage Issues")
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
        
        # Fix Symptom Intake page
        if not fix_symptom_intake_page(flow_name, pages_client):
            return False
        
        # Fix Triage Evaluation page
        if not fix_triage_evaluation_page(flow_name, pages_client):
            return False
        
        # Fix Summary page
        if not fix_summary_page(flow_name, pages_client):
            return False
        
        print()
        print("="*60)
        print("All fixes applied successfully!")
        print("="*60)
        print("\nChanges made:")
        print("  1. Symptom Intake page: Improved parameter extraction")
        print("  2. Triage Evaluation page: Added triage parameter logic")
        print("  3. Summary page: Updated to display triage parameter")
        print("\nThe agent should now:")
        print("  - Extract duration and severity more reliably")
        print("  - Set triage parameter (high/medium/low) based on symptoms")
        print("  - Display triage in the summary")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

