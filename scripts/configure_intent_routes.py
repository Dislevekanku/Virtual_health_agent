#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configure intent routes on the Start page of Dialogflow CX agent
This script adds transition routes from the Start page to appropriate pages based on intents
"""

import json
import os
import sys
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

def get_default_start_flow(agent_name):
    """Get the default start flow"""
    flows_client = get_client(dialogflow.FlowsClient)
    
    request = dialogflow.ListFlowsRequest(parent=agent_name)
    flows = flows_client.list_flows(request=request)
    
    for flow in flows:
        if flow.display_name == "Default Start Flow":
            return flow.name
    
    return None

def get_intents(agent_name):
    """Get all existing intents"""
    intents_client = get_client(dialogflow.IntentsClient)
    
    request = dialogflow.ListIntentsRequest(parent=agent_name)
    intents = intents_client.list_intents(request=request)
    
    intent_dict = {}
    for intent in intents:
        intent_dict[intent.display_name] = intent.name
    
    return intent_dict

def get_pages(flow_name):
    """Get all pages in the flow"""
    pages_client = get_client(dialogflow.PagesClient)
    
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages = pages_client.list_pages(request=request)
    
    page_dict = {}
    for page in pages:
        page_dict[page.display_name] = page
    
    return page_dict

def get_or_create_start_page(flow_name, pages_dict):
    """Get existing Start page or create a new one"""
    pages_client = get_client(dialogflow.PagesClient)
    
    if "Start" in pages_dict:
        print("   Found existing Start page")
        return pages_dict["Start"]
    elif "Start Page" in pages_dict:
        print("   Found existing Start Page (using this)")
        return pages_dict["Start Page"]
    else:
        print("   Creating new Start page...")
        start_page = dialogflow.Page(
            display_name="Start",
            entry_fulfillment=dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=["Hi — I'm the clinic's virtual assistant. I can help with quick symptom intake so your care team has the right information. What symptoms are you experiencing today?"]
                        )
                    )
                ]
            )
        )
        request = dialogflow.CreatePageRequest(parent=flow_name, page=start_page)
        created_page = pages_client.create_page(request=request)
        print(f"   [OK] Start page created")
        return created_page

def ensure_pages_exist(flow_name, required_pages):
    """Ensure required pages exist, create if they don't"""
    pages_client = get_client(dialogflow.PagesClient)
    pages_dict = get_pages(flow_name)
    
    created_pages = {}
    
    for page_name in required_pages:
        if page_name not in pages_dict and page_name != "Start" and page_name != "Start Page":
            print(f"   Creating page: {page_name}")
            
            # Create a simple page
            page = dialogflow.Page(
                display_name=page_name,
                entry_fulfillment=dialogflow.Fulfillment(
                    messages=[
                        dialogflow.ResponseMessage(
                            text=dialogflow.ResponseMessage.Text(
                                text=[f"Welcome to {page_name} page."]
                            )
                        )
                    ]
                )
            )
            
            request = dialogflow.CreatePageRequest(parent=flow_name, page=page)
            created = pages_client.create_page(request=request)
            created_pages[page_name] = created.name
            print(f"   [OK] Created {page_name}")
        else:
            if page_name in pages_dict:
                created_pages[page_name] = pages_dict[page_name].name
    
    return created_pages

def configure_intent_routes():
    """Main function to configure intent routes"""
    
    print("="*60)
    print("Configure Intent Routes - Virtual Health Assistant")
    print("="*60)
    print()
    
    # Check prerequisites
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"[ERROR] Service account key not found at {SERVICE_ACCOUNT_KEY}")
        return False
    
    if not os.path.exists(AGENT_INFO_FILE):
        print(f"[ERROR] Agent info not found at {AGENT_INFO_FILE}")
        return False
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    print(f"Agent: {agent_info['display_name']}")
    print(f"Location: {agent_info['location']}")
    print()
    
    try:
        # Step 1: Get default start flow
        print("Step 1: Getting Default Start Flow...")
        flow_name = get_default_start_flow(agent_name)
        if not flow_name:
            print("[ERROR] Could not find Default Start Flow")
            return False
        print(f"   [OK] Found flow: {flow_name}")
        print()
        
        # Step 2: Get all intents
        print("Step 2: Getting Intents...")
        intents_dict = get_intents(agent_name)
        print(f"   Found {len(intents_dict)} intents:")
        for intent_name in intents_dict.keys():
            print(f"     - {intent_name}")
        print()
        
        # Step 3: Get pages
        print("Step 3: Getting Pages...")
        pages_dict = get_pages(flow_name)
        print(f"   Found {len(pages_dict)} pages:")
        for page_name in pages_dict.keys():
            print(f"     - {page_name}")
        print()
        
        # Step 4: Ensure required pages exist
        print("Step 4: Ensuring Required Pages Exist...")
        required_pages = ["Symptom Intake", "Triage Evaluation"]
        page_names = ensure_pages_exist(flow_name, required_pages)
        print()
        
        # Step 5: Get or create Start page
        print("Step 5: Getting/Creating Start Page...")
        start_page = get_or_create_start_page(flow_name, pages_dict)
        
        # Update Start page with greeting if it doesn't have one
        if not start_page.entry_fulfillment or not start_page.entry_fulfillment.messages:
            start_page.entry_fulfillment = dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=["Hi — I'm the clinic's virtual assistant. I can help with quick symptom intake so your care team has the right information. What symptoms are you experiencing today?"]
                        )
                    )
                ]
            )
        print()
        
        # Step 6: Configure intent routes
        print("Step 6: Configuring Intent Routes...")
        
        routes = []
        
        # Intent to page mapping
        intent_routes_config = [
            # (intent_name, target_page, parameters)
            ("symptom_headache", "Symptom Intake", {"symptom_type": "headache"}),
            ("symptom_nausea", "Symptom Intake", {"symptom_type": "nausea"}),
            ("symptom_dizziness", "Symptom Intake", {"symptom_type": "dizziness"}),
            ("symptom_fatigue", "Symptom Intake", {"symptom_type": "fatigue"}),
            ("symptom_headache_redflag", "Triage Evaluation", {"urgency": "high", "symptom_type": "headache"}),
            ("symptom_redflag", "Triage Evaluation", {"urgency": "high", "symptom_type": "chest_pain"}),
        ]
        
        for intent_name, target_page, params in intent_routes_config:
            if intent_name in intents_dict:
                if target_page in page_names:
                    print(f"   Adding route: {intent_name} -> {target_page}")
                    
                    # Create set parameter actions
                    set_parameter_actions = []
                    for param_name, param_value in params.items():
                        set_parameter_actions.append(
                            dialogflow.Fulfillment.SetParameterAction(
                                parameter=param_name,
                                value=param_value
                            )
                        )
                    
                    route = dialogflow.TransitionRoute(
                        intent=intents_dict[intent_name],
                        target_page=page_names[target_page],
                        trigger_fulfillment=dialogflow.Fulfillment(
                            set_parameter_actions=set_parameter_actions
                        )
                    )
                    routes.append(route)
                    print(f"     [OK] Route added")
                else:
                    print(f"   [WARNING] Target page '{target_page}' not found, skipping route for {intent_name}")
            else:
                print(f"   [WARNING] Intent '{intent_name}' not found, skipping")
        
        # Update Start page with routes
        if routes:
            # Keep existing routes that don't conflict
            existing_routes = []
            if start_page.transition_routes:
                existing_routes = list(start_page.transition_routes)
            
            # Add new routes (will replace existing routes with same intent)
            # Remove duplicates by intent
            route_intents = {}
            for route in routes:
                if route.intent:
                    route_intents[route.intent] = route
            
            # Merge with existing routes (keep non-intent routes)
            final_routes = []
            for route in existing_routes:
                if not route.intent or route.intent not in route_intents:
                    final_routes.append(route)
            
            # Add all new intent routes
            final_routes.extend(route_intents.values())
            
            start_page.transition_routes = final_routes
            
            # Update the page
            pages_client = get_client(dialogflow.PagesClient)
            request = dialogflow.UpdatePageRequest(page=start_page)
            pages_client.update_page(request=request)
            print(f"\n   [OK] Updated Start page with {len(final_routes)} routes")
        else:
            print("\n   [WARNING] No routes were added")
        
        print()
        print("="*60)
        print("Configuration Complete!")
        print("="*60)
        print(f"\nIntent routes have been configured on the Start page.")
        print(f"Total routes configured: {len(routes)}")
        print(f"\nTest your agent here:")
        print(f"https://dialogflow.cloud.google.com/cx/projects/{agent_info['project_id']}/locations/{agent_info['location']}/agents/{agent_name.split('/')[-1]}/test")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    success = configure_intent_routes()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

