#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify and enhance intent training phrases to improve intent recognition
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

def get_intent(agent_name, intent_name):
    """Get a specific intent"""
    intents_client = get_client(dialogflow.IntentsClient)
    
    request = dialogflow.ListIntentsRequest(parent=agent_name)
    intents = intents_client.list_intents(request=request)
    
    for intent in intents:
        if intent.display_name == intent_name:
            return intent
    
    return None

def enhance_intent_training_phrases(agent_name, intent_name, additional_phrases):
    """Add more training phrases to an intent"""
    intents_client = get_client(dialogflow.IntentsClient)
    
    intent = get_intent(agent_name, intent_name)
    if not intent:
        print(f"   [ERROR] Intent '{intent_name}' not found")
        return False
    
    print(f"\n   Intent: {intent_name}")
    print(f"   Current training phrases: {len(intent.training_phrases)}")
    
    # Get existing phrases
    existing_phrases = set()
    for phrase in intent.training_phrases:
        phrase_text = " ".join([part.text for part in phrase.parts])
        existing_phrases.add(phrase_text.lower())
    
    # Add new phrases that don't already exist
    new_phrases = []
    for phrase in additional_phrases:
        if phrase.lower() not in existing_phrases:
            new_phrases.append(phrase)
    
    if not new_phrases:
        print(f"   [INFO] No new phrases to add (all already exist)")
        return True
    
    # Add new training phrases
    for phrase_text in new_phrases:
        intent.training_phrases.append(
            dialogflow.Intent.TrainingPhrase(
                parts=[dialogflow.Intent.TrainingPhrase.Part(text=phrase_text)],
                repeat_count=1
            )
        )
    
    # Update the intent
    request = dialogflow.UpdateIntentRequest(intent=intent)
    intents_client.update_intent(request=request)
    
    print(f"   [OK] Added {len(new_phrases)} new training phrases")
    print(f"   Total training phrases: {len(intent.training_phrases)}")
    
    return True

def main():
    """Main function"""
    
    print("="*60)
    print("Enhance Intent Training Phrases")
    print("="*60)
    print()
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    # Additional training phrases for each intent
    enhanced_phrases = {
        "symptom_headache": [
            "I have a headache",
            "My head hurts",
            "Headache",
            "My head is pounding",
            "I've got a headache",
            "Head pain",
            "My head aches",
            "I'm experiencing headaches",
            "Head hurts",
            "Pain in my head"
        ],
        "symptom_nausea": [
            "Feeling nauseous",
            "I feel nauseous",
            "Nausea",
            "I'm nauseous",
            "Feeling sick",
            "I feel sick",
            "Sick to my stomach",
            "Feeling queasy",
            "Upset stomach",
            "I feel like vomiting"
        ],
        "symptom_dizziness": [
            "I feel dizzy",
            "Dizzy",
            "Feeling dizzy",
            "I'm dizzy",
            "Lightheaded",
            "I feel lightheaded",
            "Feeling lightheaded",
            "The room is spinning",
            "I feel unsteady",
            "Dizzy when I stand"
        ],
        "symptom_fatigue": [
            "I'm exhausted",
            "Exhausted",
            "I'm tired",
            "Very tired",
            "No energy",
            "I have no energy",
            "Feeling drained",
            "Completely drained",
            "Fatigued",
            "I'm fatigued"
        ],
        "symptom_headache_redflag": [
            "I have a really bad headache and my vision is blurry",
            "Severe headache with vision changes",
            "Worst headache of my life",
            "Headache with stiff neck",
            "Sudden severe headache",
            "Headache with confusion",
            "Headache with fever and neck stiffness"
        ],
        "symptom_redflag": [
            "My chest feels tight and I'm lightheaded",
            "Chest pain and shortness of breath",
            "I can't breathe properly",
            "Severe chest pain",
            "Chest hurts and I'm dizzy",
            "Chest tightness"
        ]
    }
    
    print("Enhancing training phrases for each intent...\n")
    
    success_count = 0
    for intent_name, phrases in enhanced_phrases.items():
        try:
            if enhance_intent_training_phrases(agent_name, intent_name, phrases):
                success_count += 1
        except Exception as e:
            print(f"   [ERROR] Failed to enhance {intent_name}: {e}")
    
    print()
    print("="*60)
    print(f"Enhanced {success_count}/{len(enhanced_phrases)} intents")
    print("="*60)
    print("\nNote: It may take a few minutes for Dialogflow to retrain")
    print("      the NLU model with the new training phrases.")
    print()

if __name__ == "__main__":
    main()

