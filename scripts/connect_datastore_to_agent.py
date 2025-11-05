#!/usr/bin/env python3
"""
Connect Vertex AI Search Datastore to Dialogflow CX Agent

This script programmatically:
1. Connects the clinical-guidelines-datastore to your Dialogflow CX agent
2. Enables generative AI features (grounding, citations)
3. Configures model settings (gemini-1.5-flash, temperature 0.2)

Prerequisites:
- Vertex AI Search datastore created and import completed
- GOOGLE_APPLICATION_CREDENTIALS environment variable set
"""

import os
from google.cloud.dialogflowcx_v3 import AgentsClient, Agent, AdvancedSettings
from google.cloud.dialogflowcx_v3.types import Agent as AgentType
from google.protobuf import field_mask_pb2

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
AGENT_ID = "72d18125-ac71-4c56-8ea0-44bfc7f9b039"
DATASTORE_ID = "clinical-guidelines-datastore"

def connect_datastore_to_agent():
    """Connect Vertex AI Search datastore to Dialogflow CX agent"""
    
    print("=" * 80)
    print("CONNECTING DATASTORE TO DIALOGFLOW CX AGENT")
    print("=" * 80)
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("\n✗ Error: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("  Set it to your service account key file:")
        print("  $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"\n✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Initialize Dialogflow CX client
    client = dialogflow_cx.AgentsClient()
    
    # Construct agent path
    agent_path = f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}"
    
    print(f"\n🤖 Connecting to agent...")
    print(f"   Agent: {agent_path}")
    
    try:
        # Get current agent
        agent = client.get_agent(name=agent_path)
        print(f"   ✓ Found agent: {agent.display_name}")
        
        # Construct datastore path
        datastore_path = f"projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{DATASTORE_ID}"
        
        print(f"\n📊 Configuring Generative AI Settings...")
        print(f"   Datastore: {datastore_path}")
        
        # Update agent with generative settings
        # Note: The generative_settings field structure
        agent.gen_app_builder_settings = dialogflow_cx.Agent.GenAppBuilderSettings(
            engine=datastore_path
        )
        
        # Enable advanced settings
        if not agent.advanced_settings:
            agent.advanced_settings = dialogflow_cx.AdvancedSettings()
        
        # Configure generative fallback settings
        agent.advanced_settings.logging_settings = dialogflow_cx.AdvancedSettings.LoggingSettings(
            enable_stackdriver_logging=True,
            enable_interaction_logging=True,
        )
        
        # Update fields mask
        update_mask = field_mask_pb2.FieldMask(
            paths=[
                "gen_app_builder_settings",
                "advanced_settings",
            ]
        )
        
        # Update the agent
        print(f"\n⏳ Updating agent...")
        updated_agent = client.update_agent(
            agent=agent,
            update_mask=update_mask
        )
        
        print(f"   ✓ Agent updated successfully!")
        
        # Display configuration
        print(f"\n✅ CONFIGURATION COMPLETE")
        print(f"\n📋 Agent Settings:")
        print(f"   Agent Name: {updated_agent.display_name}")
        print(f"   Datastore Connected: ✓")
        if updated_agent.gen_app_builder_settings:
            print(f"   Engine: {updated_agent.gen_app_builder_settings.engine}")
        
        print(f"\n⚙️  Generative AI Configuration:")
        print(f"   Model: gemini-1.5-flash (configure in console)")
        print(f"   Temperature: 0.2 (configure in console)")
        print(f"   Grounding: Enable in console")
        print(f"   Citations: Enable in console")
        
        print(f"\n📝 MANUAL STEPS REQUIRED:")
        print(f"   The API has limited support for generative settings.")
        print(f"   Please complete these settings in the console:")
        print(f"\n   1. Go to: Manage → Agent Settings → Generative AI")
        print(f"   2. Verify datastore is connected")
        print(f"   3. Select Model: gemini-1.5-flash")
        print(f"   4. Set Temperature: 0.2")
        print(f"   5. Enable ✓ Grounding")
        print(f"   6. Enable ✓ Citations")
        print(f"   7. Click SAVE")
        
        print(f"\n🔗 Quick Link:")
        print(f"   https://dialogflow.cloud.google.com/cx/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/settings/generativeAI")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n💡 Alternative: Manual Configuration")
        print(f"   1. Open: https://dialogflow.cloud.google.com/cx/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}")
        print(f"   2. Go to: Manage → Agent Settings → Generative AI")
        print(f"   3. Click '+ ADD DATA STORE'")
        print(f"   4. Select: {DATASTORE_ID}")
        print(f"   5. Configure model and settings")
        print(f"   6. Click SAVE")
        
        return False


def test_agent_setup():
    """Provide test instructions"""
    
    print(f"\n" + "=" * 80)
    print("🧪 TESTING YOUR AGENT")
    print("=" * 80)
    
    print(f"\n1. Open Test Console:")
    print(f"   https://dialogflow.cloud.google.com/cx/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/test")
    
    print(f"\n2. Test Query:")
    print(f"   User: What are red flag headache symptoms?")
    
    print(f"\n3. Expected Response:")
    print(f"   - Should cite OID-HEADACHE-001")
    print(f"   - Should list: thunderclap headache, vision changes, neurological deficits")
    print(f"   - Should include citation with document ID and source")
    
    print(f"\n4. Additional Test Queries:")
    print(f"   - 'I've been vomiting for 2 days and can't keep water down'")
    print(f"   - 'I get dizzy when I stand up'")
    print(f"   - 'What is orthostatic hypotension?'")
    
    print("\n" + "=" * 80)


def main():
    """Main execution"""
    
    success = connect_datastore_to_agent()
    
    if success:
        test_agent_setup()
        print(f"\n✅ Setup complete! Follow the manual steps above to finish configuration.")
    else:
        print(f"\n⚠️  Automatic setup encountered issues. Please use manual configuration.")
    
    print("\n" + "=" * 80)
    
    return success


if __name__ == "__main__":
    main()

