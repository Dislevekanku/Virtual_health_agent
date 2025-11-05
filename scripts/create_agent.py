#!/usr/bin/env python3
"""
Script to create Virtual Health Assistant Agent using Dialogflow CX API
"""

import json
import os
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"  # or your preferred location
SERVICE_ACCOUNT_KEY = "key.json"

def create_agent():
    """Create the Virtual Health Assistant agent"""
    
    # Set up credentials
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY
    )
    
    # Initialize the Agents client with regional endpoint
    client_options = {"api_endpoint": f"{LOCATION}-dialogflow.googleapis.com"}
    agents_client = dialogflow.AgentsClient(
        credentials=credentials,
        client_options=client_options
    )
    
    # Load agent configuration
    with open('agent_config.json', 'r') as f:
        agent_config = json.load(f)
    
    # Prepare the agent
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    
    agent = dialogflow.Agent(
        display_name=agent_config['displayName'],
        default_language_code=agent_config['defaultLanguageCode'],
        time_zone=agent_config['timeZone'],
        description=agent_config['description'],
        enable_stackdriver_logging=agent_config.get('enableStackdriverLogging', True),
        enable_spell_correction=agent_config.get('enableSpellCorrection', True),
    )
    
    # Create the agent
    print(f"Creating agent: {agent_config['displayName']}")
    request = dialogflow.CreateAgentRequest(
        parent=parent,
        agent=agent
    )
    
    try:
        created_agent = agents_client.create_agent(request=request)
        print(f"✅ Agent created successfully!")
        print(f"   Agent name: {created_agent.name}")
        print(f"   Display name: {created_agent.display_name}")
        
        # Save the agent name for later use
        with open('agent_info.json', 'w') as f:
            json.dump({
                'agent_name': created_agent.name,
                'display_name': created_agent.display_name,
                'project_id': PROJECT_ID,
                'location': LOCATION
            }, f, indent=2)
        
        return created_agent
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None

def create_intents(agent_name):
    """Create intents for the agent"""
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY
    )
    
    client_options = {"api_endpoint": f"{LOCATION}-dialogflow.googleapis.com"}
    intents_client = dialogflow.IntentsClient(
        credentials=credentials,
        client_options=client_options
    )
    
    # Load training examples
    with open('training_examples.json', 'r') as f:
        training_data = json.load(f)
    
    created_intents = []
    
    for intent_data in training_data['intents']:
        print(f"Creating intent: {intent_data['displayName']}")
        
        # Prepare training phrases
        training_phrases = []
        for phrase in intent_data['trainingPhrases']:
            parts = [dialogflow.Intent.TrainingPhrase.Part(text=part['text']) 
                    for part in phrase['parts']]
            training_phrases.append(
                dialogflow.Intent.TrainingPhrase(parts=parts)
            )
        
        # Create intent
        intent = dialogflow.Intent(
            display_name=intent_data['displayName'],
            description=intent_data.get('description', ''),
            training_phrases=training_phrases,
        )
        
        request = dialogflow.CreateIntentRequest(
            parent=agent_name,
            intent=intent
        )
        
        try:
            created_intent = intents_client.create_intent(request=request)
            print(f"   ✅ Created: {created_intent.display_name}")
            created_intents.append(created_intent)
        except Exception as e:
            print(f"   ❌ Error creating intent {intent_data['displayName']}: {e}")
    
    return created_intents

def create_entity_types(agent_name):
    """Create custom entity types"""
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY
    )
    
    client_options = {"api_endpoint": f"{LOCATION}-dialogflow.googleapis.com"}
    entity_types_client = dialogflow.EntityTypesClient(
        credentials=credentials,
        client_options=client_options
    )
    
    # Define custom entity types
    entity_types_config = [
        {
            "display_name": "symptom_type",
            "kind": dialogflow.EntityType.Kind.KIND_MAP,
            "entities": [
                {"value": "headache", "synonyms": ["head pain", "migraine", "head hurts"]},
                {"value": "nausea", "synonyms": ["sick to stomach", "queasy", "throwing up", "vomiting"]},
                {"value": "dizziness", "synonyms": ["dizzy", "lightheaded", "vertigo", "spinning"]},
                {"value": "fatigue", "synonyms": ["tired", "exhausted", "no energy", "drained"]},
                {"value": "chest_pain", "synonyms": ["chest hurts", "chest pressure", "tight chest"]},
                {"value": "abdominal_pain", "synonyms": ["stomach pain", "belly pain", "stomach hurts"]},
            ]
        },
        {
            "display_name": "severity_level",
            "kind": dialogflow.EntityType.Kind.KIND_MAP,
            "entities": [
                {"value": "mild", "synonyms": ["slight", "minor", "not too bad"]},
                {"value": "moderate", "synonyms": ["medium", "average", "noticeable"]},
                {"value": "severe", "synonyms": ["bad", "terrible", "unbearable", "worst"]},
            ]
        }
    ]
    
    for entity_config in entity_types_config:
        print(f"Creating entity type: {entity_config['display_name']}")
        
        entities = []
        for ent in entity_config['entities']:
            entities.append(
                dialogflow.EntityType.Entity(
                    value=ent['value'],
                    synonyms=ent['synonyms']
                )
            )
        
        entity_type = dialogflow.EntityType(
            display_name=entity_config['display_name'],
            kind=entity_config['kind'],
            entities=entities
        )
        
        request = dialogflow.CreateEntityTypeRequest(
            parent=agent_name,
            entity_type=entity_type
        )
        
        try:
            created_entity = entity_types_client.create_entity_type(request=request)
            print(f"   ✅ Created: {created_entity.display_name}")
        except Exception as e:
            print(f"   ❌ Error creating entity type: {e}")

def main():
    """Main execution function"""
    
    print("="*60)
    print("Virtual Health Assistant - Agent Creation")
    print("="*60)
    print()
    
    # Check if service account key exists
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"❌ Error: Service account key not found at {SERVICE_ACCOUNT_KEY}")
        print("   Please ensure key.json is in the current directory")
        return
    
    # Step 1: Create the agent
    print("\n📋 Step 1: Creating Agent...")
    agent = create_agent()
    
    if not agent:
        print("❌ Failed to create agent. Exiting.")
        return
    
    # Step 2: Create entity types
    print("\n📋 Step 2: Creating Entity Types...")
    create_entity_types(agent.name)
    
    # Step 3: Create intents
    print("\n📋 Step 3: Creating Intents...")
    create_intents(agent.name)
    
    # Step 4: Summary
    print("\n" + "="*60)
    print("✅ Agent setup complete!")
    print("="*60)
    print(f"\nAgent Name: {agent.display_name}")
    print(f"Agent ID: {agent.name}")
    print(f"\nNext steps:")
    print("1. Enable billing for the project if not already done")
    print("2. Visit the Dialogflow CX console to:")
    print(f"   https://dialogflow.cloud.google.com/cx/projects/{PROJECT_ID}/locations/{LOCATION}/agents")
    print("3. Create flows and pages using the conversation_flow.json as reference")
    print("4. Test the agent using the test scenarios in test_scenarios.json")
    print("5. Configure webhooks for triage logic and summary generation")
    print("\nConfiguration files created:")
    print("  - agent_info.json (agent details)")
    print("  - agent_config.json (agent configuration)")
    print("  - training_examples.json (intent training data)")
    print("  - conversation_flow.json (flow design)")
    print("  - response_templates.json (response templates)")
    print("  - test_scenarios.json (test cases)")
    print()

if __name__ == "__main__":
    main()

