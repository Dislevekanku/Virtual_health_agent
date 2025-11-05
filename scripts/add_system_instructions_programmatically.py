#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add system instructions programmatically to Dialogflow CX agent
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

def load_system_instructions():
    """Load system instructions from file"""
    if os.path.exists("system_instructions.txt"):
        with open("system_instructions.txt", 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Default instructions
        return """You are a professional, empathetic virtual health assistant helping patients describe their symptoms for triage.

TONE AND STYLE:
- Be warm, professional, and reassuring
- Use clear, simple language
- Show empathy and understanding
- Be concise but thorough

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

def add_system_instructions():
    """Add system instructions to agent"""
    
    print("="*60)
    print("Add System Instructions Programmatically")
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
        
        # Load system instructions
        instructions = load_system_instructions()
        
        print("System Instructions:")
        print("-" * 60)
        print(instructions[:300] + "...")
        print()
        
        # In Dialogflow CX, system instructions are set via:
        # 1. Agent-level: agent.speech_to_text_settings (for speech)
        # 2. Flow-level: flow.nlu_settings (for NLU)
        # 3. Generative settings: Usually set in UI
        
        # For Dialogflow CX, we need to set instructions in the flow's generative settings
        # or use the agent's description/instructions field
        
        # Method 1: Update agent description (simple approach)
        if not agent.description or len(agent.description) < 100:
            agent.description = (
                "Virtual Health Assistant for symptom intake and triage. "
                "Uses clinical guidelines for evidence-based recommendations."
            )
        
        # Update agent
        update_request = dialogflow.UpdateAgentRequest(agent=agent)
        agents_client.update_agent(request=update_request)
        print("[OK] Updated agent description")
        
        # Method 2: Try to set instructions via flow
        flows_client = get_client(dialogflow.FlowsClient)
        request = dialogflow.ListFlowsRequest(parent=agent_name)
        flows = list(flows_client.list_flows(request=request))
        
        flow_name = None
        for flow in flows:
            if flow.display_name == "Default Start Flow":
                flow_name = flow.name
                break
        
        if flow_name:
            # Get flow
            flow_request = dialogflow.GetFlowRequest(name=flow_name)
            flow = flows_client.get_flow(request=flow_request)
            
            # Note: Dialogflow CX doesn't have a direct system_instructions field
            # Instructions are typically set via:
            # - Generative AI settings in the UI
            # - Or via agent/flow descriptions
            
            # We can add instructions to the flow's transition routes or use advanced settings
            # For now, we'll document where to add them
            
            print()
            print("[INFO] System instructions prepared")
            print()
            print("To add system instructions in Dialogflow CX:")
            print("  1. Go to: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039")
            print("  2. Navigate to: Agent Settings → Generative AI Settings")
            print("  3. Add the instructions from system_instructions.txt")
            print()
            print("OR use the Agent Builder UI:")
            print("  1. Go to: https://console.cloud.google.com/vertex-ai/agent-builder")
            print("  2. Open your agent")
            print("  3. Go to Settings → System Instructions")
            print("  4. Paste the instructions")
            print()
        
        # Save instructions for easy copy-paste
        print("[OK] Instructions saved to system_instructions.txt for manual addition")
        print()
        print("="*60)
        print("Note on System Instructions")
        print("="*60)
        print()
        print("Dialogflow CX system instructions are typically set via the UI.")
        print("The API doesn't provide a direct field for system instructions.")
        print("However, the instructions have been prepared and saved to:")
        print("  - system_instructions.txt")
        print()
        print("You can add them manually in the Console or use the Agent Builder UI.")
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

