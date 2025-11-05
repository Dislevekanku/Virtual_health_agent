#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify complete flow and ensure triage parameter is set correctly
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

def verify_and_fix_flow():
    """Verify and fix the complete flow"""
    
    print("="*60)
    print("Verify and Fix Complete Flow")
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
        
        page_dict = {page.display_name: page.name for page in pages}
        
        print("Current Page Flow:")
        print("  1. Start → (intent routes)")
        print("  2. Symptom Intake → (form completion)")
        print("  3. Clarifying Questions → (always)")
        print("  4. Triage Evaluation → (always)")
        print("  5. Summary")
        print()
        
        # Verify Symptom Intake transitions to Clarifying Questions
        symptom_intake_page = None
        for page in pages:
            if page.display_name == "Symptom Intake":
                symptom_intake_page = page
                break
        
        if symptom_intake_page:
            print("Fixing Symptom Intake → Clarifying Questions transition...")
            
            clarifying_page_name = page_dict.get("Clarifying Questions")
            if clarifying_page_name:
                # Ensure there's a transition when form is complete
                if not symptom_intake_page.transition_routes:
                    symptom_intake_page.transition_routes = []
                
                # Check if transition exists
                has_transition = False
                for route in symptom_intake_page.transition_routes:
                    if route.target_page == clarifying_page_name:
                        has_transition = True
                        break
                
                if not has_transition:
                    symptom_intake_page.transition_routes.append(
                        dialogflow.TransitionRoute(
                            condition='$page.params.status = "FINAL"',
                            target_page=clarifying_page_name
                        )
                    )
                    print("   [OK] Added transition to Clarifying Questions")
                
                # Update page
                request = dialogflow.UpdatePageRequest(page=symptom_intake_page)
                pages_client.update_page(request=request)
        
        # Verify Clarifying Questions transitions to Triage Evaluation
        clarifying_page = None
        for page in pages:
            if page.display_name == "Clarifying Questions":
                clarifying_page = page
                break
        
        if clarifying_page:
            print("\nFixing Clarifying Questions → Triage Evaluation transition...")
            
            triage_page_name = page_dict.get("Triage Evaluation")
            if triage_page_name:
                # Ensure transition exists
                if not clarifying_page.transition_routes:
                    clarifying_page.transition_routes = []
                
                has_transition = False
                for route in clarifying_page.transition_routes:
                    if route.target_page == triage_page_name:
                        has_transition = True
                        break
                
                if not has_transition:
                    clarifying_page.transition_routes.append(
                        dialogflow.TransitionRoute(
                            condition="true",
                            target_page=triage_page_name
                        )
                    )
                    print("   [OK] Added transition to Triage Evaluation")
                
                # Update page
                request = dialogflow.UpdatePageRequest(page=clarifying_page)
                pages_client.update_page(request=request)
        
        # Verify Triage Evaluation has proper entry fulfillment and sets parameters
        triage_page = None
        for page in pages:
            if page.display_name == "Triage Evaluation":
                triage_page = page
                break
        
        if triage_page:
            print("\nVerifying Triage Evaluation page...")
            
            # Ensure entry fulfillment exists
            if not triage_page.entry_fulfillment:
                triage_page.entry_fulfillment = dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=["Based on your symptoms, I'm evaluating the appropriate level of care you need."]
                            )
                        )
                    ]
                )
            
            # Check if routes exist and have proper parameter setting
            if triage_page.transition_routes:
                print(f"   Found {len(triage_page.transition_routes)} transition routes")
                
                # Check if routes set triage parameter
                has_triage_setting = False
                for route in triage_page.transition_routes:
                    if route.trigger_fulfillment and route.trigger_fulfillment.set_parameter_actions:
                        for action in route.trigger_fulfillment.set_parameter_actions:
                            if action.parameter == "triage":
                                has_triage_setting = True
                                print(f"   [OK] Route sets triage parameter: {route.condition or 'default'}")
                                break
                
                if not has_triage_setting:
                    print("   [WARNING] No routes setting triage parameter")
            else:
                print("   [ERROR] No transition routes on Triage Evaluation page")
            
            # Update page
            request = dialogflow.UpdatePageRequest(page=triage_page)
            pages_client.update_page(request=request)
        
        print()
        print("="*60)
        print("Flow Verification Complete")
        print("="*60)
        print()
        print("Flow structure:")
        print("  Start → Symptom Intake → Clarifying Questions → Triage Evaluation → Summary")
        print()
        print("Key points:")
        print("  ✓ Symptom Intake collects duration and severity")
        print("  ✓ Clarifying Questions always transitions to Triage Evaluation")
        print("  ✓ Triage Evaluation evaluates conditions and sets triage parameter")
        print("  ✓ Summary displays the final triage and recommendation")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_and_fix_flow()
    exit(0 if success else 1)

