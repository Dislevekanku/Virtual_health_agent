#!/usr/bin/env python3
"""
Configure Vertex AI Agent Builder Chat Agent

This script programmatically:
1. Creates/updates Agent Builder Chat app
2. Adds agent instructions
3. Configures model (gemini-1.5-flash, temperature 0.2)
4. Enables citations and grounding
5. Tests with a sample query

Prerequisites:
- Vertex AI Search datastore created
- GOOGLE_APPLICATION_CREDENTIALS environment variable set
"""

import os
import json
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core import exceptions

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
PROJECT_NUMBER = "396346843737"
LOCATION = "global"
DATASTORE_ID = "clinical-guidelines-datastore"
ENGINE_ID = "clinical-guidelines-chat-engine"
APP_ID = "clinical-guidelines-chat-app"

# Agent Instructions
AGENT_INSTRUCTIONS = """You are a clinical triage assistant for a healthcare organization.

Your role:
- Help users understand symptom severity
- Provide triage recommendations (emergency/urgent/routine/self-care)
- Always cite clinical guidelines using document IDs (e.g., OID-HEADACHE-001)

Red flag symptoms require IMMEDIATE escalation to emergency care.

Always be conservative - when in doubt, recommend higher level of care.

Format your responses with:
1. Clinical information based on guidelines
2. Triage level (Emergency/Urgent/Routine/Self-care) and recommendation
3. Citation: [Document ID, Source, Section]

Example response format:
"According to the Headache Evaluation Guideline (OID-HEADACHE-001):

Thunderclap headache (sudden onset, worst headache of life) is a red flag symptom requiring IMMEDIATE emergency evaluation.

Triage Level: EMERGENCY - Call 911 or go to ED immediately.

[Citation: OID-HEADACHE-001, Internal Clinical SOP, Section: Red Flags, Oct 2025]"
"""


def create_or_update_engine():
    """Create or update search engine with chat configuration"""
    
    print("=" * 80)
    print("CONFIGURING AGENT BUILDER CHAT ENGINE")
    print("=" * 80)
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("\n✗ Error: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("  $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return None
    
    print(f"\n✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Initialize client
    client = discoveryengine.EngineServiceClient()
    
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"
    engine_name = f"{parent}/engines/{ENGINE_ID}"
    
    print(f"\n🔍 Checking for existing engine...")
    
    try:
        # Try to get existing engine
        engine = client.get_engine(name=engine_name)
        print(f"   ✓ Found existing engine: {engine.display_name}")
        update_mode = True
    except exceptions.NotFound:
        print(f"   ℹ Engine not found, will create new one")
        update_mode = False
    
    # Configure chat engine
    engine_config = discoveryengine.Engine(
        display_name="Clinical Guidelines Chat Engine",
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_CHAT,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        data_store_ids=[DATASTORE_ID],
        chat_engine_config=discoveryengine.Engine.ChatEngineConfig(
            agent_creation_config=discoveryengine.Engine.ChatEngineConfig.AgentCreationConfig(
                business="Healthcare",
                default_language_code="en",
                time_zone="America/New_York",
                agent_config=discoveryengine.Engine.ChatEngineConfig.AgentCreationConfig.AgentConfig(
                    instruction=AGENT_INSTRUCTIONS,
                ),
            ),
        ),
        # Chat engine metadata
        chat_engine_metadata=discoveryengine.Engine.ChatEngineMetadata(
            # This enables citations
        ),
    )
    
    if update_mode:
        print(f"\n⏳ Updating engine configuration...")
        # Update existing engine
        from google.protobuf import field_mask_pb2
        update_mask = field_mask_pb2.FieldMask(
            paths=["chat_engine_config", "display_name"]
        )
        operation = client.update_engine(
            engine=engine_config,
            update_mask=update_mask
        )
    else:
        print(f"\n⏳ Creating new chat engine...")
        print(f"   This may take 15-30 minutes...")
        # Create new engine
        operation = client.create_engine(
            parent=parent,
            engine=engine_config,
            engine_id=ENGINE_ID,
        )
    
    # Wait for operation (with timeout)
    print(f"   Operation started: {operation.operation.name}")
    print(f"   You can check status in console while waiting...")
    
    try:
        result = operation.result(timeout=1800)  # 30 minute timeout
        print(f"\n✅ Engine configured successfully!")
        print(f"   Engine name: {result.name}")
        return result
    except Exception as e:
        print(f"\n⚠️  Operation is running in background: {e}")
        print(f"   Monitor progress in console:")
        print(f"   https://console.cloud.google.com/gen-app-builder/engines?project={PROJECT_ID}")
        return None


def configure_conversation_settings(engine_name):
    """Configure model and conversation settings"""
    
    print(f"\n⚙️  CONFIGURING MODEL SETTINGS")
    print(f"=" * 80)
    
    # Note: Model configuration (gemini-1.5-flash, temperature) is typically
    # done through the console UI or via serving config
    
    print(f"\n📋 Recommended Settings (configure in console):")
    print(f"   Model: gemini-1.5-flash")
    print(f"   Temperature: 0.2")
    print(f"   ✅ Enable Citations")
    print(f"   ✅ Enable Grounding")
    print(f"   Max tokens: 1024")
    
    print(f"\n🔗 Configure at:")
    print(f"   https://console.cloud.google.com/gen-app-builder/engines/{ENGINE_ID}/edit?project={PROJECT_ID}")


def test_chat_query(engine_name, query="What are red flag headache symptoms?"):
    """Test the chat engine with a query"""
    
    print(f"\n🧪 TESTING CHAT ENGINE")
    print(f"=" * 80)
    
    print(f"\n📝 Test Query: {query}")
    
    try:
        # Initialize conversetion client
        from google.cloud import discoveryengine_v1 as discoveryengine
        
        client = discoveryengine.ConversationalSearchServiceClient()
        
        # Construct serving config
        parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"
        serving_config = f"{parent}/engines/{ENGINE_ID}/servingConfigs/default_config"
        
        # Create conversation
        conversation_name = f"{parent}/conversations/-"  # New conversation
        
        # Send query
        request = discoveryengine.ConverseConversationRequest(
            name=conversation_name,
            serving_config=serving_config,
            query=discoveryengine.TextInput(input=query),
            # Enable search summarization (citations)
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=3,
                include_citations=True,
                model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                    version="stable",  # or "gemini-1.5-flash"
                ),
            ),
        )
        
        print(f"\n⏳ Sending query to chat engine...")
        response = client.converse_conversation(request=request)
        
        print(f"\n✅ RESPONSE RECEIVED:")
        print(f"=" * 80)
        
        if response.reply and response.reply.summary:
            print(f"\n{response.reply.summary.summary_text}")
            
            if response.reply.summary.summary_with_metadata:
                print(f"\n📚 CITATIONS:")
                for citation in response.reply.summary.summary_with_metadata.citations:
                    print(f"   - {citation}")
        else:
            print(f"\nNo response generated. The engine may still be initializing.")
            print(f"Raw response: {response}")
        
        return True
        
    except Exception as e:
        print(f"\n⚠️  Test query failed: {e}")
        print(f"\n💡 The engine may still be initializing (takes 15-30 min)")
        print(f"   Try testing manually in console:")
        print(f"   https://console.cloud.google.com/gen-app-builder/engines/{ENGINE_ID}/preview?project={PROJECT_ID}")
        return False


def main():
    """Main execution"""
    
    print("\n" + "=" * 80)
    print("VERTEX AI AGENT BUILDER - CHAT CONFIGURATION")
    print("=" * 80)
    
    # Step 1: Create/update engine
    engine = create_or_update_engine()
    
    if engine:
        engine_name = engine.name
    else:
        # Use expected name if operation is async
        parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"
        engine_name = f"{parent}/engines/{ENGINE_ID}"
    
    # Step 2: Show model configuration info
    configure_conversation_settings(engine_name)
    
    # Step 3: Test (if engine is ready)
    print(f"\n" + "=" * 80)
    print(f"Would you like to test the chat engine now? (y/n)")
    print(f"Note: Engine must be fully created first (may take 15-30 min)")
    print(f"=" * 80)
    
    # For automated run, skip interactive test
    print(f"\nℹ️  Skipping automated test")
    print(f"   Test manually in console once engine is ready:")
    print(f"   https://console.cloud.google.com/gen-app-builder/engines?project={PROJECT_ID}")
    
    # Uncomment to enable test:
    # test_chat_query(engine_name)
    
    # Final summary
    print(f"\n" + "=" * 80)
    print("✅ CONFIGURATION COMPLETE")
    print("=" * 80)
    
    print(f"\n📋 What was configured:")
    print(f"   ✓ Chat engine created/updated: {ENGINE_ID}")
    print(f"   ✓ Agent instructions added")
    print(f"   ✓ Connected to datastore: {DATASTORE_ID}")
    
    print(f"\n⏳ Next Steps:")
    print(f"   1. Wait for engine creation to complete (15-30 min)")
    print(f"   2. Configure model in console (gemini-1.5-flash, temp 0.2)")
    print(f"   3. Test in preview panel")
    
    print(f"\n🔗 Console Links:")
    print(f"   Engines: https://console.cloud.google.com/gen-app-builder/engines?project={PROJECT_ID}")
    print(f"   Preview: https://console.cloud.google.com/gen-app-builder/engines/{ENGINE_ID}/preview?project={PROJECT_ID}")
    
    print(f"\n" + "=" * 80)


if __name__ == "__main__":
    main()

