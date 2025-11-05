#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add missing parameters for better symptom tracking
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

def add_parameters_to_intents():
    """Add parameters to intents to extract additional information"""
    
    print("="*60)
    print("Add Missing Parameters to Intents")
    print("="*60)
    print()
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        # Update symptom_headache_redflag to extract vision_change
        print("Updating symptom_headache_redflag intent...")
        redflag_intent = None
        for intent in intents:
            if intent.display_name == "symptom_headache_redflag":
                redflag_intent = intent
                break
        
        if redflag_intent:
            # Add parameters to extract vision changes, etc.
            if not redflag_intent.parameters:
                redflag_intent.parameters = []
            
            # Check if vision_change parameter exists
            has_vision_change = False
            for param in redflag_intent.parameters:
                if param.display_name == "vision_change":
                    has_vision_change = True
                    break
            
            if not has_vision_change:
                redflag_intent.parameters.append(
                    dialogflow.Intent.Parameter(
                        display_name="vision_change",
                        entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                        is_list=False
                    )
                )
                print("  [OK] Added vision_change parameter")
            
            # Update the intent
            update_request = dialogflow.UpdateIntentRequest(intent=redflag_intent)
            intents_client.update_intent(request=update_request)
            print("  [OK] Updated symptom_headache_redflag intent")
        
        # Update symptom_nausea to extract vomiting
        print("\nUpdating symptom_nausea intent...")
        nausea_intent = None
        for intent in intents:
            if intent.display_name == "symptom_nausea":
                nausea_intent = intent
                break
        
        if nausea_intent:
            if not nausea_intent.parameters:
                nausea_intent.parameters = []
            
            # Check if vomiting parameter exists
            has_vomiting = False
            for param in nausea_intent.parameters:
                if param.display_name == "vomiting":
                    has_vomiting = True
                    break
            
            if not has_vomiting:
                nausea_intent.parameters.append(
                    dialogflow.Intent.Parameter(
                        display_name="vomiting",
                        entity_type="projects/-/locations/-/agents/-/entityTypes/sys.any",
                        is_list=False
                    )
                )
                print("  [OK] Added vomiting parameter")
            
            # Update the intent
            update_request = dialogflow.UpdateIntentRequest(intent=nausea_intent)
            intents_client.update_intent(request=update_request)
            print("  [OK] Updated symptom_nausea intent")
        
        print()
        print("="*60)
        print("Parameter updates complete!")
        print("="*60)
        print("\nNote: Parameters are now defined in intents.")
        print("      Dialogflow will attempt to extract these from user input.")
        print("      You may need to add training examples that include these phrases.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def enhance_training_phrases():
    """Add training phrases that include the new parameters"""
    
    print("\nEnhancing training phrases with parameter examples...")
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        # Update symptom_headache_redflag with vision change examples
        redflag_intent = None
        for intent in intents:
            if intent.display_name == "symptom_headache_redflag":
                redflag_intent = intent
                break
        
        if redflag_intent:
            new_phrases = [
                "I have a really bad headache and my vision is blurry",
                "Headache with blurred vision",
                "Severe headache and I can't see clearly",
                "Worst headache of my life with vision problems"
            ]
            
            existing_phrases = set()
            for phrase in redflag_intent.training_phrases:
                phrase_text = " ".join([part.text for part in phrase.parts])
                existing_phrases.add(phrase_text.lower())
            
            added = 0
            for phrase_text in new_phrases:
                if phrase_text.lower() not in existing_phrases:
                    redflag_intent.training_phrases.append(
                        dialogflow.Intent.TrainingPhrase(
                            parts=[dialogflow.Intent.TrainingPhrase.Part(text=phrase_text)],
                            repeat_count=1
                        )
                    )
                    added += 1
            
            if added > 0:
                update_request = dialogflow.UpdateIntentRequest(intent=redflag_intent)
                intents_client.update_intent(request=update_request)
                print(f"  [OK] Added {added} new training phrases to symptom_headache_redflag")
        
        # Update symptom_nausea with vomiting examples
        nausea_intent = None
        for intent in intents:
            if intent.display_name == "symptom_nausea":
                nausea_intent = intent
                break
        
        if nausea_intent:
            new_phrases = [
                "Feeling nauseous and can't keep food down",
                "Nauseous and vomiting",
                "Feeling nauseous since last night, can't keep food down",
                "Nausea with vomiting"
            ]
            
            existing_phrases = set()
            for phrase in nausea_intent.training_phrases:
                phrase_text = " ".join([part.text for part in phrase.parts])
                existing_phrases.add(phrase_text.lower())
            
            added = 0
            for phrase_text in new_phrases:
                if phrase_text.lower() not in existing_phrases:
                    nausea_intent.training_phrases.append(
                        dialogflow.Intent.TrainingPhrase(
                            parts=[dialogflow.Intent.TrainingPhrase.Part(text=phrase_text)],
                            repeat_count=1
                        )
                    )
                    added += 1
            
            if added > 0:
                update_request = dialogflow.UpdateIntentRequest(intent=nausea_intent)
                intents_client.update_intent(request=update_request)
                print(f"  [OK] Added {added} new training phrases to symptom_nausea")
        
        print()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = add_parameters_to_intents()
    success2 = enhance_training_phrases()
    exit(0 if (success1 and success2) else 1)

