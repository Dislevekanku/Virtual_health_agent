#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find the correct datastore ID and fix the webhook configuration
"""

import json
import os
import requests
from google.auth import default
from google.auth.transport.requests import Request

PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
SEARCH_LOCATION = "global"

def get_access_token():
    """Get access token"""
    try:
        credentials, project = default()
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def find_datastores():
    """Find available datastores"""
    
    print("="*60)
    print("Finding Available Datastores")
    print("="*60)
    print()
    
    access_token = get_access_token()
    if not access_token:
        print("❌ Cannot get access token")
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Try to list datastores using different methods
    endpoints = [
        f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores",
        f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                datastores = data.get("dataStores", [])
                if datastores:
                    print(f"✅ Found datastores in {endpoint.split('/locations/')[1].split('/')[0]}:")
                    for ds in datastores:
                        ds_id = ds.get("name", "").split("/")[-1]
                        display_name = ds.get("displayName", "Unknown")
                        print(f"   - {display_name}")
                        print(f"     ID: {ds_id}")
                        print(f"     Full name: {ds.get('name', 'N/A')}")
                        print()
                    return datastores
        except Exception as e:
            continue
    
    print("❌ Could not list datastores (may need different permissions)")
    print()
    print("Possible solutions:")
    print("  1. Datastore may not be created yet")
    print("  2. Service account needs 'Discovery Engine Data Store Viewer' role")
    print("  3. Datastore may be in a different project")
    print()
    return None

def test_datastore_search(datastore_id, location="global"):
    """Test if we can search a specific datastore"""
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    endpoint = f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/{location}/collections/default_collection/dataStores/{datastore_id}/servingConfigs/default_config:search"
    
    payload = {
        "query": "headache",
        "pageSize": 1
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            print(f"✅ Datastore '{datastore_id}' is accessible and searchable!")
            return True
        else:
            print(f"❌ Datastore '{datastore_id}' returned: {response.status_code}")
            print(f"   {response.text[:300]}")
            return False
    except Exception as e:
        print(f"❌ Error testing datastore: {e}")
        return False

if __name__ == "__main__":
    datastores = find_datastores()
    
    if datastores:
        print("="*60)
        print("Testing Datastore Access")
        print("="*60)
        print()
        
        for ds in datastores:
            ds_id = ds.get("name", "").split("/")[-1]
            print(f"Testing: {ds_id}")
            if test_datastore_search(ds_id):
                print()
                print(f"✅ RECOMMENDED: Use datastore ID '{ds_id}'")
                print(f"   Update rag_simplified.py: DATASTORE_ID = '{ds_id}'")
                break
            print()
    else:
        print()
        print("="*60)
        print("Solution: Make Webhook Work Without Datastore")
        print("="*60)
        print()
        print("Since the datastore doesn't exist or isn't accessible,")
        print("we can update the webhook to provide fallback responses")
        print("without trying to access the database.")
        print()
        print("The webhook will still work and provide helpful responses,")
        print("just without clinical guideline citations.")
        print()

