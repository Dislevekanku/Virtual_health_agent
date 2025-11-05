#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix webhook database access issue - check and fix Vertex AI Search configuration
"""

import json
import os
import requests
from google.auth import default
from google.auth.transport.requests import Request

PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
SEARCH_LOCATION = "global"  # Vertex AI Search is typically global
DATASTORE_ID = "clinical-guidelines-datastore"

def get_access_token():
    """Get access token"""
    try:
        credentials, project = default()
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def check_datastore():
    """Check if datastore exists and is accessible"""
    
    print("="*60)
    print("Diagnosing Webhook Database Access Issue")
    print("="*60)
    print()
    
    access_token = get_access_token()
    if not access_token:
        print("❌ Cannot get access token - check service account permissions")
        return False
    
    print("✅ Access token obtained")
    print()
    
    # Try different possible datastore locations/endpoints
    possible_endpoints = [
        # Option 1: Global location
        f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{DATASTORE_ID}",
        # Option 2: us-central1 location
        f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATASTORE_ID}",
        # Option 3: List datastores
        f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores",
        f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores",
    ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("Checking datastore access...")
    print()
    
    # Try to list datastores first
    for endpoint in possible_endpoints[-2:]:  # Try list endpoints
        try:
            print(f"Trying: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                datastores = data.get("dataStores", [])
                print(f"✅ Found {len(datastores)} datastore(s):")
                for ds in datastores:
                    print(f"   - {ds.get('displayName', 'Unknown')} (ID: {ds.get('name', '').split('/')[-1]})")
                    print(f"     Location: {endpoint.split('/locations/')[1].split('/')[0]}")
                print()
                break
            else:
                print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print()
    print("Testing search endpoint...")
    
    # Try search endpoints
    search_endpoints = [
        f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{DATASTORE_ID}/servingConfigs/default_config:search",
        f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATASTORE_ID}/servingConfigs/default_config:search",
    ]
    
    for endpoint in search_endpoints:
        try:
            print(f"Testing: {endpoint.split('/dataStores/')[1].split('/')[0]}")
            payload = {
                "query": "headache",
                "pageSize": 1
            }
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                print(f"✅ Search endpoint works!")
                print(f"   Location: {'global' if 'global' in endpoint else LOCATION}")
                data = response.json()
                results = data.get("results", [])
                print(f"   Found {len(results)} result(s)")
                print()
                return True
            else:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                print()
        except Exception as e:
            print(f"   Error: {e}")
            print()
    
    print()
    print("="*60)
    print("Diagnosis Summary")
    print("="*60)
    print()
    print("Possible issues:")
    print("  1. Datastore ID incorrect")
    print("  2. Datastore location incorrect (should be 'global' or 'us-central1')")
    print("  3. Service account lacks permissions")
    print("  4. Datastore not deployed/created")
    print()
    print("Next steps:")
    print("  1. Check Cloud Console for datastore location")
    print("  2. Verify datastore ID matches")
    print("  3. Check service account permissions")
    print("  4. Update rag_simplified.py with correct location")
    print()
    
    return False

if __name__ == "__main__":
    check_datastore()

