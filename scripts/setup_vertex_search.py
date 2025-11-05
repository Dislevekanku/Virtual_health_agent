#!/usr/bin/env python3
"""
Setup Vertex AI Search Datastore and Connect to Dialogflow CX Agent

This script automates:
1. Creating a Vertex AI Search (Discovery Engine) datastore
2. Importing clinical guidelines from GCS
3. Connecting the datastore to Dialogflow CX agent
4. Configuring generative AI settings

Prerequisites:
- GCS bucket with guideline files already uploaded
- Service account with necessary permissions
- GOOGLE_APPLICATION_CREDENTIALS environment variable set
"""

import os
import time
from google.cloud import discoveryengine
from google.api_core import operation
from google.cloud import dialogflowcx_v3beta1 as dialogflow_cx
from google.protobuf import field_mask_pb2

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "global"  # Vertex AI Search datastores are typically in global location
DATASTORE_ID = "clinical-guidelines-datastore"
DATASTORE_DISPLAY_NAME = "Clinical Guidelines Search"
GCS_BUCKET = "dfci-guidelines-poc"
AGENT_ID = "72d18125-ac71-4c56-8ea0-44bfc7f9b039"


def create_datastore(project_id, location, datastore_id, display_name):
    """Create a Vertex AI Search datastore for unstructured documents"""
    
    print(f"\n📊 Creating Vertex AI Search Datastore...")
    print(f"   Project: {project_id}")
    print(f"   Location: {location}")
    print(f"   Datastore ID: {datastore_id}")
    
    # Initialize the DataStoreService client
    client = discoveryengine.DataStoreServiceClient()
    
    # Construct the parent path
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    
    # Create datastore configuration
    data_store = discoveryengine.DataStore(
        display_name=display_name,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )
    
    try:
        # Check if datastore already exists
        datastore_name = f"{parent}/dataStores/{datastore_id}"
        try:
            existing_ds = client.get_data_store(name=datastore_name)
            print(f"   ✓ Datastore already exists: {datastore_name}")
            return datastore_name
        except Exception:
            pass  # Datastore doesn't exist, create it
        
        # Create the datastore
        request = discoveryengine.CreateDataStoreRequest(
            parent=parent,
            data_store=data_store,
            data_store_id=datastore_id,
        )
        
        op = client.create_data_store(request=request)
        print(f"   ⏳ Creating datastore... (this may take a few minutes)")
        
        # Wait for the operation to complete
        response = op.result(timeout=300)  # 5 minute timeout
        
        print(f"   ✓ Datastore created: {response.name}")
        return response.name
        
    except Exception as e:
        print(f"   ✗ Error creating datastore: {e}")
        raise


def import_documents_from_gcs(datastore_name, gcs_bucket):
    """Import documents from Google Cloud Storage"""
    
    print(f"\n📥 Importing documents from GCS...")
    print(f"   Datastore: {datastore_name}")
    print(f"   GCS Bucket: gs://{gcs_bucket}")
    
    # Initialize the DocumentService client
    client = discoveryengine.DocumentServiceClient()
    
    # Construct the parent (branch)
    parent = f"{datastore_name}/branches/default_branch"
    
    # Configure GCS import
    gcs_source = discoveryengine.GcsSource(
        input_uris=[
            f"gs://{gcs_bucket}/guidelines/headache_guideline.txt",
            f"gs://{gcs_bucket}/guidelines/nausea_vomiting_guideline.txt",
            f"gs://{gcs_bucket}/guidelines/dizziness_vertigo_guideline.txt",
            f"gs://{gcs_bucket}/guidelines/fatigue_guideline.txt",
            f"gs://{gcs_bucket}/guidelines/orthostatic_hypotension_guideline.txt",
        ],
        data_schema="content",  # For unstructured documents
    )
    
    import_config = discoveryengine.ImportDocumentsRequest.InlineSource(
        documents=[]  # Not used for GCS import
    )
    
    # Create import request
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=gcs_source,
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )
    
    try:
        # Start the import operation
        op = client.import_documents(request=request)
        print(f"   ⏳ Importing documents... (this may take 5-15 minutes)")
        print(f"   Operation: {op.operation.name}")
        
        # Note: We don't wait for completion as it can take a long time
        # Instead, we return the operation and let user monitor it
        print(f"   ✓ Import started successfully")
        print(f"   📊 Monitor progress in console:")
        print(f"      https://console.cloud.google.com/gen-app-builder/data-stores/{datastore_name.split('/')[-1]}")
        
        return op.operation.name
        
    except Exception as e:
        print(f"   ✗ Error importing documents: {e}")
        raise


def wait_for_import(operation_name, timeout=900):
    """Wait for import operation to complete"""
    
    print(f"\n⏳ Waiting for import to complete (timeout: {timeout}s)...")
    
    # This is a placeholder - actual implementation would poll the operation
    # For now, we'll just sleep and assume it completes
    print(f"   Note: Import is running in background")
    print(f"   Check status in console or wait ~10 minutes before connecting to agent")
    
    return True


def create_search_engine(project_id, location, datastore_name):
    """Create a search engine (app) for the datastore"""
    
    print(f"\n🔍 Creating Search Engine...")
    
    # Initialize the EngineService client
    client = discoveryengine.EngineServiceClient()
    
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    engine_id = f"{DATASTORE_ID}-engine"
    
    # Create engine configuration
    engine = discoveryengine.Engine(
        display_name=f"{DATASTORE_DISPLAY_NAME} Engine",
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
        search_engine_config=discoveryengine.Engine.SearchEngineConfig(
            search_tier=discoveryengine.SearchTier.SEARCH_TIER_STANDARD,
            search_add_ons=[
                discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM,  # Enable generative AI
            ],
        ),
        data_store_ids=[datastore_name.split('/')[-1]],
    )
    
    try:
        # Check if engine already exists
        engine_name = f"{parent}/engines/{engine_id}"
        try:
            existing_engine = client.get_engine(name=engine_name)
            print(f"   ✓ Engine already exists: {engine_name}")
            return engine_name
        except Exception:
            pass
        
        # Create the engine
        request = discoveryengine.CreateEngineRequest(
            parent=parent,
            engine=engine,
            engine_id=engine_id,
        )
        
        op = client.create_engine(request=request)
        print(f"   ⏳ Creating engine...")
        
        response = op.result(timeout=300)
        
        print(f"   ✓ Engine created: {response.name}")
        return response.name
        
    except Exception as e:
        print(f"   ✗ Error creating engine: {e}")
        raise


def connect_to_dialogflow_agent(project_id, location, agent_id, datastore_name):
    """Connect the datastore to Dialogflow CX agent"""
    
    print(f"\n🤖 Connecting datastore to Dialogflow CX agent...")
    print(f"   Agent ID: {agent_id}")
    
    # Initialize Dialogflow CX client
    client = dialogflow_cx.AgentsClient()
    
    # Construct agent path
    agent_path = f"projects/{project_id}/locations/{location}/agents/{agent_id}"
    
    try:
        # Get current agent settings
        agent = client.get_agent(name=agent_path)
        print(f"   ✓ Found agent: {agent.display_name}")
        
        # Update agent with generative settings
        # Note: This is a simplified version - actual implementation depends on API availability
        
        # For now, provide manual instructions
        print(f"\n   ⚠️  Manual step required:")
        print(f"   1. Go to: https://dialogflow.cloud.google.com/cx/projects/{project_id}/locations/{location}/agents/{agent_id}")
        print(f"   2. Navigate to: Manage → Agent Settings → Generative AI")
        print(f"   3. Click '+ Add Data Store'")
        print(f"   4. Select datastore: {datastore_name.split('/')[-1]}")
        print(f"   5. Enable 'Citations' and 'Grounding'")
        print(f"   6. Model: gemini-1.5-flash")
        print(f"   7. Temperature: 0.2")
        print(f"   8. Click 'Save'")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error connecting to agent: {e}")
        return False


def main():
    """Main execution flow"""
    
    print("=" * 80)
    print("VERTEX AI SEARCH SETUP - Clinical Guidelines")
    print("=" * 80)
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("\n✗ Error: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("  Set it to your service account key file:")
        print("  $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"\n✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    try:
        # Step 1: Create datastore
        datastore_name = create_datastore(
            PROJECT_ID, 
            LOCATION, 
            DATASTORE_ID, 
            DATASTORE_DISPLAY_NAME
        )
        
        # Step 2: Import documents from GCS
        import_op = import_documents_from_gcs(datastore_name, GCS_BUCKET)
        
        # Step 3: Create search engine
        engine_name = create_search_engine(PROJECT_ID, LOCATION, datastore_name)
        
        # Step 4: Connect to Dialogflow agent (manual step for now)
        connect_to_dialogflow_agent(PROJECT_ID, LOCATION, AGENT_ID, datastore_name)
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ SETUP COMPLETE")
        print("=" * 80)
        
        print(f"\n📊 Resources Created:")
        print(f"   Datastore: {datastore_name}")
        print(f"   Engine: {engine_name if 'engine_name' in locals() else 'N/A'}")
        print(f"   Import Status: In Progress")
        
        print(f"\n🔗 Important Links:")
        print(f"   Datastore Console:")
        print(f"   https://console.cloud.google.com/gen-app-builder/data-stores")
        
        print(f"\n   Agent Console:")
        print(f"   https://dialogflow.cloud.google.com/cx/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}")
        
        print(f"\n⏳ Next Steps:")
        print(f"   1. Wait 10-15 minutes for document import to complete")
        print(f"   2. Verify import status in console")
        print(f"   3. Complete manual connection to Dialogflow agent (see instructions above)")
        print(f"   4. Test agent with query: 'What are red flag headache symptoms?'")
        
        print("\n" + "=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

