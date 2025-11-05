#!/usr/bin/env python3
"""
Create conversation flows and pages for Virtual Health Assistant
This script builds the complete conversation flow programmatically
"""

import json
import os
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account

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
    client_options = {"api_endpoint": f"{LOCATION}-dialogflow.googleapis.com"}
    return client_class(credentials=credentials, client_options=client_options)

def get_or_create_intent(agent_name, display_name, training_phrases):
    """Get existing intent or create new one"""
    intents_client = get_client(dialogflow.IntentsClient)
    
    # List existing intents
    request = dialogflow.ListIntentsRequest(parent=agent_name)
    intents = intents_client.list_intents(request=request)
    
    for intent in intents:
        if intent.display_name == display_name:
            print(f"   Found existing intent: {display_name}")
            return intent.name
    
    # Create new intent
    print(f"   Creating intent: {display_name}")
    
    phrases = []
    for phrase_text in training_phrases:
        phrases.append(
            dialogflow.Intent.TrainingPhrase(
                parts=[dialogflow.Intent.TrainingPhrase.Part(text=phrase_text)],
                repeat_count=1
            )
        )
    
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=phrases
    )
    
    request = dialogflow.CreateIntentRequest(
        parent=agent_name,
        intent=intent
    )
    
    created = intents_client.create_intent(request=request)
    return created.name

def create_intents(agent_name):
    """Create all required intents"""
    print("\n📋 Step 1: Creating Intents...")
    
    intents = {
        "symptom_headache": [
            "I have a headache",
            "My head hurts really bad",
            "I have a mild headache",
            "Headache started this morning",
            "I've been having headaches for a week",
            "Head is pounding",
            "Migraine",
            "Head pain won't go away"
        ],
        "symptom_headache_redflag": [
            "I have a really bad headache and my vision is blurry",
            "Severe headache with confusion",
            "Worst headache of my life",
            "Headache with stiff neck and fever",
            "Vision changes with my headache",
            "Sudden severe headache"
        ],
        "symptom_nausea": [
            "Feeling nauseous since last night",
            "I have mild nausea but no vomiting",
            "I feel sick to my stomach",
            "Been throwing up all morning",
            "Nausea for 3 days",
            "I feel like vomiting",
            "Can't keep food down"
        ],
        "symptom_dizziness": [
            "I get dizzy when I stand up quickly",
            "Feeling lightheaded",
            "The room is spinning",
            "I feel dizzy and unsteady",
            "Vertigo symptoms",
            "Lightheaded all day"
        ],
        "symptom_fatigue": [
            "Been exhausted for a week even after sleeping",
            "I'm so tired all the time",
            "No energy for days",
            "Completely drained",
            "Fatigued and weak",
            "Can't stay awake"
        ],
        "symptom_redflag": [
            "My chest feels tight and I'm lightheaded",
            "Chest pain and shortness of breath",
            "I can't breathe properly",
            "Severe abdominal pain",
            "Chest hurts and I'm dizzy"
        ]
    }
    
    intent_names = {}
    for intent_name, phrases in intents.items():
        intent_names[intent_name] = get_or_create_intent(agent_name, intent_name, phrases)
    
    return intent_names

def get_default_start_flow(agent_name):
    """Get the default start flow"""
    flows_client = get_client(dialogflow.FlowsClient)
    
    request = dialogflow.ListFlowsRequest(parent=agent_name)
    flows = flows_client.list_flows(request=request)
    
    for flow in flows:
        if flow.display_name == "Default Start Flow":
            return flow.name
    
    return None

def create_pages(flow_name, intent_names):
    """Create all required pages in the flow"""
    print("\n📋 Step 2: Creating Pages...")
    
    pages_client = get_client(dialogflow.PagesClient)
    
    # Get existing pages
    request = dialogflow.ListPagesRequest(parent=flow_name)
    existing_pages = {page.display_name: page.name for page in pages_client.list_pages(request=request)}
    
    # Page 1: Symptom Intake
    if "Symptom Intake" not in existing_pages:
        print("   Creating page: Symptom Intake")
        
        page = dialogflow.Page(
            display_name="Symptom Intake",
            form=dialogflow.Form(
                parameters=[
                    dialogflow.Form.Parameter(
                        display_name="symptom_type",
                        entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                        required=True,
                        fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                            initial_prompt_fulfillment=dialogflow.Fulfillment(
                                messages=[
                                    dialogflow.ResponseMessage(
                                        text=dialogflow.ResponseMessage.Text(
                                            text=["What is your main symptom?"]
                                        )
                                    )
                                ]
                            )
                        ),
                        redact=True
                    ),
                    dialogflow.Form.Parameter(
                        display_name="duration",
                        entity_type="projects/-/locations/-/agents/-/entityTypes/sys.duration",
                        required=True,
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
                    ),
                    dialogflow.Form.Parameter(
                        display_name="severity",
                        entity_type="projects/-/locations/-/agents/-/entityTypes/sys.number",
                        required=True,
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
                    ),
                    dialogflow.Form.Parameter(
                        display_name="additional_symptoms",
                        entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                        required=False,
                        is_list=True,
                        fill_behavior=dialogflow.Form.Parameter.FillBehavior(
                            initial_prompt_fulfillment=dialogflow.Fulfillment(
                                messages=[
                                    dialogflow.ResponseMessage(
                                        text=dialogflow.ResponseMessage.Text(
                                            text=["Are you experiencing any other symptoms? (Say 'none' if not)"]
                                        )
                                    )
                                ]
                            )
                        )
                    )
                ]
            )
        )
        
        request = dialogflow.CreatePageRequest(parent=flow_name, page=page)
        symptom_intake_page = pages_client.create_page(request=request)
        existing_pages["Symptom Intake"] = symptom_intake_page.name
    else:
        print("   Page already exists: Symptom Intake")
    
    # Page 2: Clarifying Questions
    if "Clarifying Questions" not in existing_pages:
        print("   Creating page: Clarifying Questions")
        
        page = dialogflow.Page(
            display_name="Clarifying Questions",
            entry_fulfillment=dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=["Thank you. Let me ask a few clarifying questions to better understand your situation."]
                        )
                    )
                ]
            ),
            form=dialogflow.Form(
                parameters=[
                    dialogflow.Form.Parameter(
                        display_name="red_flag_check",
                        entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                        required=False
                    )
                ]
            )
        )
        
        request = dialogflow.CreatePageRequest(parent=flow_name, page=page)
        clarifying_page = pages_client.create_page(request=request)
        existing_pages["Clarifying Questions"] = clarifying_page.name
    else:
        print("   Page already exists: Clarifying Questions")
    
    # Page 3: Triage Evaluation
    if "Triage Evaluation" not in existing_pages:
        print("   Creating page: Triage Evaluation")
        print("   Note: Triage logic will need to be configured in the UI for conditional responses")
        
        page = dialogflow.Page(
            display_name="Triage Evaluation",
            entry_fulfillment=dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=["Based on your symptoms, I'm evaluating the appropriate level of care you need."]
                        )
                    )
                ]
            ),
            # Add routes for different triage levels
            transition_routes=[
                # High urgency route
                dialogflow.TransitionRoute(
                    condition='$session.params.severity >= 8 OR $session.params.urgency = "high"',
                    trigger_fulfillment=dialogflow.Fulfillment(
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
                ),
                # Medium urgency route
                dialogflow.TransitionRoute(
                    condition='$session.params.severity >= 5',
                    trigger_fulfillment=dialogflow.Fulfillment(
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
                ),
                # Low urgency route (default)
                dialogflow.TransitionRoute(
                    condition='true',
                    trigger_fulfillment=dialogflow.Fulfillment(
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
                )
            ]
        )
        
        request = dialogflow.CreatePageRequest(parent=flow_name, page=page)
        triage_page = pages_client.create_page(request=request)
        existing_pages["Triage Evaluation"] = triage_page.name
    else:
        print("   Page already exists: Triage Evaluation")
    
    # Page 4: Summary
    if "Summary" not in existing_pages:
        print("   Creating page: Summary")
        
        page = dialogflow.Page(
            display_name="Summary",
            entry_fulfillment=dialogflow.Fulfillment(
                messages=[
                    dialogflow.ResponseMessage(
                        text=dialogflow.ResponseMessage.Text(
                            text=[
                                "Here's a summary:\n\n" +
                                "Symptom: $session.params.symptom_type\n" +
                                "Duration: $session.params.duration\n" +
                                "Severity: $session.params.severity/10\n" +
                                "Triage: $session.params.triage\n\n" +
                                "This information will be shared with your care team."
                            ]
                        )
                    )
                ]
            )
        )
        
        request = dialogflow.CreatePageRequest(parent=flow_name, page=page)
        summary_page = pages_client.create_page(request=request)
        existing_pages["Summary"] = summary_page.name
    else:
        print("   Page already exists: Summary")
    
    return existing_pages

def update_flow_with_routes(flow_name, intent_names, page_names):
    """Update the flow with transition routes and create a Start page with greeting"""
    print("\n📋 Step 3: Updating Flow with Intent Routes...")
    
    pages_client = get_client(dialogflow.PagesClient)
    flows_client = get_client(dialogflow.FlowsClient)
    
    # First, create or update a Start page with greeting
    request = dialogflow.ListPagesRequest(parent=flow_name)
    existing_pages_list = {page.display_name: page for page in pages_client.list_pages(request=request)}
    
    start_page_name = None
    
    if "Start" in existing_pages_list:
        print("   Updating existing Start page...")
        start_page = existing_pages_list["Start"]
        start_page_name = start_page.name
    else:
        print("   Creating Start page with greeting...")
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
        start_page = created_page
        start_page_name = created_page.name
        print(f"   ✅ Start page created")
    
    # Update Start page with greeting if it exists
    start_page.entry_fulfillment = dialogflow.Fulfillment(
        messages=[
            dialogflow.ResponseMessage(
                text=dialogflow.ResponseMessage.Text(
                    text=["Hi — I'm the clinic's virtual assistant. I can help with quick symptom intake so your care team has the right information. What symptoms are you experiencing today?"]
                )
            )
        ]
    )
    
    # Add routes for each symptom intent to the Start page
    print("   Adding routes for symptom intents...")
    routes = []
    
    # Regular symptom routes
    symptom_routes = [
        ("symptom_headache", "headache"),
        ("symptom_nausea", "nausea"),
        ("symptom_dizziness", "dizziness"),
        ("symptom_fatigue", "fatigue")
    ]
    
    for intent_key, symptom_value in symptom_routes:
        if intent_key in intent_names:
            print(f"   - Adding route for {intent_key}")
            routes.append(
                dialogflow.TransitionRoute(
                    intent=intent_names[intent_key],
                    target_page=page_names.get("Symptom Intake"),
                    trigger_fulfillment=dialogflow.Fulfillment(
                        set_parameter_actions=[
                            dialogflow.Fulfillment.SetParameterAction(
                                parameter="symptom_type",
                                value=symptom_value
                            )
                        ]
                    )
                )
            )
    
    # Red flag routes
    print("   - Adding red flag routes...")
    red_flag_configs = [
        ("symptom_headache_redflag", "headache"),
        ("symptom_redflag", "chest_pain")
    ]
    
    for intent_key, symptom_value in red_flag_configs:
        if intent_key in intent_names:
            routes.append(
                dialogflow.TransitionRoute(
                    intent=intent_names[intent_key],
                    target_page=page_names.get("Triage Evaluation"),
                    trigger_fulfillment=dialogflow.Fulfillment(
                        set_parameter_actions=[
                            dialogflow.Fulfillment.SetParameterAction(
                                parameter="urgency",
                                value="high"
                            ),
                            dialogflow.Fulfillment.SetParameterAction(
                                parameter="symptom_type",
                                value=symptom_value
                            )
                        ]
                    )
                )
            )
    
    start_page.transition_routes = routes
    
    # Update the Start page
    request = dialogflow.UpdatePageRequest(page=start_page)
    pages_client.update_page(request=request)
    print("   ✅ Start page updated with all routes")
    
    # Also set the flow's NLU settings to use the Start page
    flow_request = dialogflow.GetFlowRequest(name=flow_name)
    flow = flows_client.get_flow(request=flow_request)
    
    # Set Start page as the entry point (if not already)
    if flow.nlu_settings:
        flow.nlu_settings.model_type = dialogflow.NluSettings.ModelType.MODEL_TYPE_ADVANCED
    
    update_request = dialogflow.UpdateFlowRequest(flow=flow)
    flows_client.update_flow(request=update_request)
    print("   ✅ Flow configuration updated")

def add_page_transitions(flow_name, page_names):
    """Add transition routes between pages"""
    print("\n📋 Step 4: Adding Page Transitions...")
    
    pages_client = get_client(dialogflow.PagesClient)
    
    # Get all pages
    request = dialogflow.ListPagesRequest(parent=flow_name)
    pages_dict = {page.display_name: page for page in pages_client.list_pages(request=request)}
    
    # Symptom Intake → Clarifying Questions
    if "Symptom Intake" in pages_dict and "Clarifying Questions" in page_names:
        print("   Adding: Symptom Intake → Clarifying Questions")
        page = pages_dict["Symptom Intake"]
        page.transition_routes = [
            dialogflow.TransitionRoute(
                condition='$page.params.status = "FINAL"',
                target_page=page_names["Clarifying Questions"]
            )
        ]
        request = dialogflow.UpdatePageRequest(page=page)
        pages_client.update_page(request=request)
    
    # Clarifying Questions → Triage Evaluation
    if "Clarifying Questions" in pages_dict and "Triage Evaluation" in page_names:
        print("   Adding: Clarifying Questions → Triage Evaluation")
        page = pages_dict["Clarifying Questions"]
        page.transition_routes = [
            dialogflow.TransitionRoute(
                condition="true",
                target_page=page_names["Triage Evaluation"]
            )
        ]
        request = dialogflow.UpdatePageRequest(page=page)
        pages_client.update_page(request=request)
    
    # Triage Evaluation → Summary
    if "Triage Evaluation" in pages_dict and "Summary" in page_names:
        print("   Adding: Triage Evaluation → Summary")
        page = pages_dict["Triage Evaluation"]
        page.transition_routes = [
            dialogflow.TransitionRoute(
                condition="true",
                target_page=page_names["Summary"]
            )
        ]
        request = dialogflow.UpdatePageRequest(page=page)
        pages_client.update_page(request=request)

def main():
    """Main execution function"""
    
    print("="*60)
    print("Virtual Health Assistant - Flow Creation")
    print("="*60)
    print()
    
    # Check prerequisites
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"❌ Error: Service account key not found at {SERVICE_ACCOUNT_KEY}")
        return
    
    if not os.path.exists(AGENT_INFO_FILE):
        print(f"❌ Error: Agent info not found at {AGENT_INFO_FILE}")
        print("   Run create_agent.py first to create the agent")
        return
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    print(f"Agent: {agent_info['display_name']}")
    print(f"Agent ID: {agent_name}")
    print()
    
    try:
        # Step 1: Create intents
        intent_names = create_intents(agent_name)
        
        # Step 2: Get default start flow
        flow_name = get_default_start_flow(agent_name)
        if not flow_name:
            print("❌ Could not find Default Start Flow")
            return
        
        print(f"\nUsing flow: {flow_name}")
        
        # Step 3: Create pages
        page_names = create_pages(flow_name, intent_names)
        
        # Step 4: Update flow with routes
        update_flow_with_routes(flow_name, intent_names, page_names)
        
        # Step 5: Add page transitions
        add_page_transitions(flow_name, page_names)
        
        # Success!
        print("\n" + "="*60)
        print("✅ Flow creation complete!")
        print("="*60)
        print(f"\nYour agent is ready to test!")
        print(f"\nTest it here:")
        print(f"https://dialogflow.cloud.google.com/cx/projects/{agent_info['project_id']}/locations/{agent_info['location']}/agents/{agent_name.split('/')[-1]}/test")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

