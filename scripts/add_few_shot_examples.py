#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add few-shot examples and improve system instructions for better tone and classification
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

def add_system_instructions():
    """Add system instructions with few-shot examples"""
    
    print("="*60)
    print("Add System Instructions and Few-Shot Examples")
    print("="*60)
    print()
    
    # Load agent info
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        # Get agent
        agents_client = get_client(dialogflow.AgentsClient)
        agent_request = dialogflow.GetAgentRequest(name=agent_name)
        agent = agents_client.get_agent(request=agent_request)
        
        # Enhanced system instructions with few-shot examples
        system_instructions = """You are a professional, empathetic virtual health assistant helping patients describe their symptoms for triage.

TONE AND STYLE:
- Be warm, professional, and reassuring
- Use clear, simple language
- Show empathy and understanding
- Be concise but thorough

FEW-SHOT EXAMPLES:

Example 1 - Low Urgency Headache:
User: "I have a headache"
Assistant: "I understand you're experiencing a headache. To help determine the best next steps, can you tell me when this started?"
User: "It started this morning"
Assistant: "Thank you. On a scale of 0 to 10, how would you rate the severity of your headache?"
User: "About a 3"
Assistant: "Based on your symptoms—a mild headache that started this morning—this may improve with rest and self-care. If symptoms persist beyond 3 days or worsen, please schedule a follow-up."

Example 2 - High Urgency Red Flag:
User: "I have a really bad headache and my vision is blurry"
Assistant: "Thank you for letting me know. Headache with vision changes can be a sign of a serious condition. I recommend seeking immediate medical attention. Please call your healthcare provider's emergency line or go to the nearest emergency department."

Example 3 - Medium Urgency Nausea:
User: "Feeling nauseous since last night, can't keep food down"
Assistant: "I understand you're experiencing nausea and vomiting. This warrants medical evaluation. I recommend scheduling a same-week appointment with your primary care provider or using our telehealth service."

CLASSIFICATION GUIDELINES:
- HIGH urgency: Severe symptoms (8+/10), red flags (vision changes, chest pain, neurological symptoms), or life-threatening symptoms
- MEDIUM urgency: Moderate symptoms (5-7/10), persistent symptoms (>3 days), or inability to keep fluids down
- LOW urgency: Mild symptoms (<5/10), short duration, no red flags

IMPORTANT:
- Always be empathetic and reassuring
- Provide clear next steps
- For red flags, emphasize urgency without causing panic
- Include medical disclaimers when appropriate
- Never provide definitive diagnoses, only triage recommendations"""
        
        # Note: Dialogflow CX system instructions are set via the UI
        # We'll create a document with instructions for manual setup
        
        print("[INFO] System instructions prepared")
        print()
        print("System Instructions:")
        print("-" * 60)
        print(system_instructions[:500] + "...")
        print()
        print("[NOTE] System instructions need to be added via:")
        print("  1. Dialogflow CX Console → Agent Settings → Generative Settings")
        print("  2. Or via Agent Builder → System Instructions")
        print()
        
        # Save instructions to file for reference
        instructions_file = "system_instructions.txt"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(system_instructions)
        
        print(f"[OK] System instructions saved to: {instructions_file}")
        print()
        
        # Add few-shot examples to intents by enhancing training phrases
        print("Enhancing intent training phrases with few-shot examples...")
        
        intents_client = get_client(dialogflow.IntentsClient)
        request = dialogflow.ListIntentsRequest(parent=agent_name)
        intents = list(intents_client.list_intents(request=request))
        
        # Enhanced training phrases with context
        enhanced_phrases = {
            "symptom_headache": [
                "I have a headache",
                "My head hurts",
                "I've had a headache since this morning",
                "Mild headache started today",
                "Headache for a few hours",
                "I have a headache, it's not too bad",
                "Started with a headache this morning"
            ],
            "symptom_headache_redflag": [
                "I have a really bad headache and my vision is blurry",
                "Severe headache with vision changes",
                "Worst headache of my life and I can't see clearly",
                "Headache so bad my vision went blurry",
                "Thunderclap headache with vision problems",
                "Sudden severe headache and blurred vision"
            ],
            "symptom_nausea": [
                "Feeling nauseous since last night",
                "I've been nauseous and can't keep food down",
                "Nausea and vomiting since yesterday",
                "Feeling sick to my stomach, throwing up",
                "Can't keep anything down, been nauseous",
                "Nauseous all day, can't eat"
            ],
            "symptom_dizziness": [
                "I get dizzy when I stand up",
                "Dizzy when standing quickly",
                "Feeling lightheaded when I get up",
                "Dizziness when changing positions",
                "I feel dizzy and unsteady",
                "Lightheaded when standing"
            ],
            "symptom_fatigue": [
                "Been exhausted for a week",
                "Extremely tired even after sleeping",
                "No energy for days",
                "Completely drained, can barely function",
                "Fatigue that doesn't improve with rest",
                "Been exhausted for over a week"
            ]
        }
        
        updated_count = 0
        for intent in intents:
            if intent.display_name in enhanced_phrases:
                existing_phrases = set()
                for phrase in intent.training_phrases:
                    phrase_text = " ".join([part.text for part in phrase.parts])
                    existing_phrases.add(phrase_text.lower())
                
                new_count = 0
                for phrase_text in enhanced_phrases[intent.display_name]:
                    if phrase_text.lower() not in existing_phrases:
                        intent.training_phrases.append(
                            dialogflow.Intent.TrainingPhrase(
                                parts=[dialogflow.Intent.TrainingPhrase.Part(text=phrase_text)],
                                repeat_count=1
                            )
                        )
                        new_count += 1
                
                if new_count > 0:
                    update_request = dialogflow.UpdateIntentRequest(intent=intent)
                    intents_client.update_intent(request=update_request)
                    print(f"  [OK] Added {new_count} phrases to {intent.display_name}")
                    updated_count += 1
        
        print()
        print(f"[OK] Enhanced {updated_count} intents with additional training phrases")
        print()
        print("="*60)
        print("Few-Shot Examples Added!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Add system instructions manually in Dialogflow CX Console")
        print("  2. Review system_instructions.txt for the full instructions")
        print("  3. Test the agent to verify improved tone and classification")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_system_instructions()
    exit(0 if success else 1)

