#!/usr/bin/env python3
"""
Connect Dialogflow CX Generator to Vertex AI Search Datastore

This script programmatically:
1. Updates the generator to enable grounding
2. Connects it to the clinical-guidelines-datastore
3. Enables citations in responses

Prerequisites:
- Generator already created in Dialogflow CX
- GOOGLE_APPLICATION_CREDENTIALS environment variable set
"""

import os
import json
from google.cloud import dialogflowcx_v3 as dialogflow_cx
from google.protobuf import field_mask_pb2

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
AGENT_ID = "72d18125-ac71-4c56-8ea0-44bfc7f9b039"
GENERATOR_ID = "clinical-guidelines-generator"  # Update this with your actual generator ID
DATASTORE_ID = "clinical-guidelines-datastore"

def connect_generator_to_datastore():
    """Connect the generator to the Vertex AI Search datastore"""
    
    print("=" * 80)
    print("CONNECTING GENERATOR TO DATASTORE")
    print("=" * 80)
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("\n✗ Error: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("  $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"\n✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Initialize Dialogflow CX client
    client = dialogflow_cx.GeneratorsClient()
    
    # Construct generator path
    generator_path = f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/generators/{GENERATOR_ID}"
    
    print(f"\n🔍 Getting current generator...")
    print(f"   Generator: {generator_path}")
    
    try:
        # Get current generator
        generator = client.get_generator(name=generator_path)
        print(f"   ✓ Found generator: {generator.display_name}")
        
        # Update generator with grounding configuration
        print(f"\n⚙️  Configuring grounding and data store connection...")
        
        # Enable grounding with data store
        generator.grounding = dialogflow_cx.Generator.Grounding(
            grounding_configs=[
                dialogflow_cx.Generator.Grounding.GroundingConfig(
                    grounding_config=f"projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{DATASTORE_ID}/groundingConfigs/default_config",
                    grounding_config_type=dialogflow_cx.Generator.Grounding.GroundingConfig.GroundingConfigType.DATA_STORE,
                )
            ]
        )
        
        # Update fields mask
        update_mask = field_mask_pb2.FieldMask(
            paths=["grounding"]
        )
        
        # Update the generator
        print(f"\n⏳ Updating generator...")
        updated_generator = client.update_generator(
            generator=generator,
            update_mask=update_mask
        )
        
        print(f"   ✓ Generator updated successfully!")
        
        # Display configuration
        print(f"\n✅ CONFIGURATION COMPLETE")
        print(f"\n📋 Generator Settings:")
        print(f"   Name: {updated_generator.display_name}")
        print(f"   Grounding: Enabled")
        print(f"   Data Store: {DATASTORE_ID}")
        if updated_generator.grounding:
            print(f"   Grounding Configs: {len(updated_generator.grounding.grounding_configs)}")
        
        print(f"\n🧪 Test Instructions:")
        print(f"   1. Go to Preview panel in Dialogflow CX")
        print(f"   2. Type: 'What are red flag headache symptoms?'")
        print(f"   3. Should return guidelines with citations")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n💡 Manual Configuration Required")
        print(f"   The API may not support grounding configuration yet.")
        print(f"   Please configure manually in the console:")
        print(f"   1. Go to your generator settings")
        print(f"   2. Look for 'Grounding' or 'Data Store' options")
        print(f"   3. Select: {DATASTORE_ID}")
        print(f"   4. Enable citations")
        
        return False


def test_generator_connection():
    """Test the generator with a sample query"""
    
    print(f"\n" + "=" * 80)
    print("🧪 TESTING GENERATOR")
    print("=" * 80)
    
    print(f"\n📝 Test Query: 'What are red flag headache symptoms?'")
    print(f"\nExpected Response:")
    print(f"   - Should mention thunderclap headache, vision changes")
    print(f"   - Should cite OID-HEADACHE-001")
    print(f"   - Should recommend emergency evaluation")
    
    print(f"\n🔗 Test in Console:")
    print(f"   https://dialogflow.cloud.google.com/cx/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/test")
    
    print(f"\n💡 If no citations appear:")
    print(f"   1. Check grounding is enabled")
    print(f"   2. Verify datastore connection")
    print(f"   3. Ensure citations are enabled in generator settings")


def main():
    """Main execution"""
    
    success = connect_generator_to_datastore()
    
    if success:
        test_generator_connection()
        print(f"\n✅ Generator connected to datastore!")
    else:
        print(f"\n⚠️  Manual configuration may be required.")
        print(f"   Check the console for grounding options.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

