#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to create Vertex AI Search datastore for clinical guidelines
"""

import os
import json
from google.cloud import discoveryengine
from google.oauth2 import service_account

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "global"  # Vertex AI Search uses global location
DATASTORE_ID = "clinical-guidelines-datastore"
DATASTORE_DISPLAY_NAME = "Clinical Guidelines Search"
GCS_BUCKET = "dfci-guidelines-poc"

def create_datastore():
    """Create Vertex AI Search datastore"""
    
    print("="*60)
    print("Creating Vertex AI Search Datastore")
    print("="*60)
    print()
    
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file("key.json")
    
    # Initialize client
    client = discoveryengine.DataStoreServiceClient(credentials=credentials)
    
    # Construct parent path
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"
    datastore_name = f"{parent}/dataStores/{DATASTORE_ID}"
    
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Datastore ID: {DATASTORE_ID}")
    print()
    
    try:
        # Check if datastore already exists
        try:
            existing = client.get_data_store(name=datastore_name)
            print(f"✅ Datastore already exists!")
            print(f"   Name: {existing.name}")
            print(f"   Display Name: {existing.display_name}")
            print(f"   State: {existing.state}")
            print()
            return datastore_name
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                print("Datastore not found, creating new one...")
            else:
                raise
    
    except Exception as check_error:
        print(f"Checking existing datastore: {check_error}")
    
    # Create datastore configuration
    data_store = discoveryengine.DataStore(
        display_name=DATASTORE_DISPLAY_NAME,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )
    
    try:
        # Create the datastore
        request = discoveryengine.CreateDataStoreRequest(
            parent=parent,
            data_store=data_store,
            data_store_id=DATASTORE_ID,
        )
        
        print("⏳ Creating datastore (this may take 2-5 minutes)...")
        op = client.create_data_store(request=request)
        
        # Wait for operation to complete
        response = op.result(timeout=300)
        
        print()
        print("✅ Datastore created successfully!")
        print(f"   Name: {response.name}")
        print(f"   Display Name: {response.display_name}")
        print()
        
        return response.name
        
    except Exception as e:
        print(f"❌ Error creating datastore: {e}")
        import traceback
        traceback.print_exc()
        
        # Check if it's a permission issue
        if "permission" in str(e).lower() or "403" in str(e):
            print()
            print("💡 Permission Issue:")
            print("   Service account needs 'Discovery Engine Admin' role")
            print("   Or 'Discovery Engine Data Store Admin' role")
        elif "already exists" in str(e).lower():
            print()
            print("💡 Datastore may already exist with different configuration")
            print("   Try checking the console:")
            print(f"   https://console.cloud.google.com/gen-app-builder/data-stores")
        
        return None

def import_documents():
    """Import documents from GCS"""
    
    print("="*60)
    print("Importing Documents from GCS")
    print("="*60)
    print()
    
    datastore_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATASTORE_ID}"
    
    credentials = service_account.Credentials.from_service_account_file("key.json")
    client = discoveryengine.DocumentServiceClient(credentials=credentials)
    
    parent = f"{datastore_name}/branches/default_branch"
    
    # GCS source configuration
    gcs_source = discoveryengine.GcsSource(
        input_uris=[
            f"gs://{GCS_BUCKET}/guidelines/headache_guideline.txt",
            f"gs://{GCS_BUCKET}/guidelines/nausea_vomiting_guideline.txt",
            f"gs://{GCS_BUCKET}/guidelines/dizziness_vertigo_guideline.txt",
            f"gs://{GCS_BUCKET}/guidelines/fatigue_guideline.txt",
            f"gs://{GCS_BUCKET}/guidelines/orthostatic_hypotension_guideline.txt",
        ],
        data_schema="content",  # For unstructured documents
    )
    
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=gcs_source,
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )
    
    try:
        print("⏳ Starting document import...")
        print(f"   GCS Bucket: gs://{GCS_BUCKET}/guidelines/")
        print()
        print("   Files to import:")
        print("     - headache_guideline.txt")
        print("     - nausea_vomiting_guideline.txt")
        print("     - dizziness_vertigo_guideline.txt")
        print("     - fatigue_guideline.txt")
        print("     - orthostatic_hypotension_guideline.txt")
        print()
        
        op = client.import_documents(request=request)
        print(f"✅ Import started!")
        print(f"   Operation: {op.operation.name}")
        print()
        print("⏳ Import will take 5-15 minutes to complete")
        print("   Monitor progress in console:")
        print(f"   https://console.cloud.google.com/gen-app-builder/data-stores/{DATASTORE_ID}")
        print()
        
        return op.operation.name
        
    except Exception as e:
        print(f"❌ Error importing documents: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print()
    print("Step 1: Creating datastore...")
    datastore_name = create_datastore()
    
    if datastore_name:
        print()
        print("Step 2: Importing documents...")
        import_op = import_documents()
        
        print()
        print("="*60)
        print("✅ SETUP COMPLETE")
        print("="*60)
        print()
        print("Next steps:")
        print("  1. Wait 10-15 minutes for document import to complete")
        print("  2. Update webhook code with correct datastore ID")
        print("  3. Test webhook search functionality")
        print()
        print("Monitor progress:")
        print(f"  https://console.cloud.google.com/gen-app-builder/data-stores/{DATASTORE_ID}")
        print()

