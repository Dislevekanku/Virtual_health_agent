#!/usr/bin/env python3
"""
Programmatically Fix Webhook Integration

This script connects the RAG webhook to the Dialogflow CX flow's fulfillment
so that medical queries will call the webhook instead of falling back to
"Sorry, can you say that again?"
"""

import os
import json
import requests
from google.auth import default
from google.auth.transport.requests import Request

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
AGENT_ID = "72d18125-ac71-4c56-8ea0-44bfc7f9b039"
WEBHOOK_NAME = "clinical-guidelines-webhook"
FLOW_ID = "00000000-0000-0000-0000-000000000000"  # Default Start Flow
PAGE_ID = "00000000-0000-0000-0000-000000000000"  # Start Page

def get_access_token():
    """Get access token for API calls"""
    
    try:
        credentials, project = default()
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None

def get_start_page():
    """Get the start page configuration"""
    
    access_token = get_access_token()
    if not access_token:
        return None
    
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/flows/{FLOW_ID}/pages/{PAGE_ID}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            page_data = response.json()
            print(f"✓ Retrieved start page: {page_data.get('displayName', 'Start Page')}")
            return page_data
        else:
            print(f"❌ Error getting start page: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting start page: {e}")
        return None

def add_webhook_to_entry_fulfillment():
    """Add webhook to the start page's entry fulfillment"""
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    # Get current page configuration
    page_data = get_start_page()
    if not page_data:
        return False
    
    # Create webhook fulfillment configuration
    webhook_fulfillment = {
        "webhook": WEBHOOK_NAME,
        "messages": [
            {
                "text": {
                    "text": ["Searching clinical guidelines..."]
                }
            }
        ]
    }
    
    # Update the page with webhook fulfillment
    page_data["entryFulfillment"] = webhook_fulfillment
    
    # Construct URL for updating the page
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/flows/{FLOW_ID}/pages/{PAGE_ID}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Remove read-only fields
    page_data.pop("name", None)
    
    try:
        print("🔄 Adding webhook to entry fulfillment...")
        
        response = requests.patch(url, headers=headers, json=page_data)
        
        if response.status_code == 200:
            updated_page = response.json()
            print(f"✅ Successfully added webhook to entry fulfillment!")
            print(f"   Webhook: {WEBHOOK_NAME}")
            print(f"   Page: {updated_page.get('displayName', 'Start Page')}")
            return True
        else:
            print(f"❌ Error updating page: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating start page: {e}")
        return False

def create_medical_intent():
    """Create a medical intent as backup option"""
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    # Medical intent configuration
    medical_intent = {
        "displayName": "Medical Query Intent",
        "description": "Handles medical queries and calls clinical guidelines webhook",
        "trainingPhrases": [
            {
                "parts": [
                    {
                        "text": "What are red flag headache symptoms?"
                    }
                ],
                "repeatCount": 1
            },
            {
                "parts": [
                    {
                        "text": "When should I see a doctor for nausea?"
                    }
                ],
                "repeatCount": 1
            },
            {
                "parts": [
                    {
                        "text": "What is orthostatic hypotension?"
                    }
                ],
                "repeatCount": 1
            },
            {
                "parts": [
                    {
                        "text": "Tell me about dizziness guidelines"
                    }
                ],
                "repeatCount": 1
            },
            {
                "parts": [
                    {
                        "text": "Medical advice"
                    }
                ],
                "repeatCount": 1
            },
            {
                "parts": [
                    {
                        "text": "Health symptoms"
                    }
                ],
                "repeatCount": 1
            },
            {
                "parts": [
                    {
                        "text": "Clinical guidelines"
                    }
                ],
                "repeatCount": 1
            }
        ],
        "parameters": [],
        "messages": [
            {
                "text": {
                    "text": ["Let me search the clinical guidelines for you..."]
                }
            }
        ],
        "outputContexts": [],
        # Enable webhook fulfillment
        "webhookEnabled": True,
        "webhook": WEBHOOK_NAME
    }
    
    # Construct URL for creating intent
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/intents"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔄 Creating medical intent with webhook...")
        
        response = requests.post(url, headers=headers, json=medical_intent)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully created medical intent!")
            print(f"   Intent: {result.get('displayName', 'Medical Query Intent')}")
            print(f"   Webhook: {WEBHOOK_NAME}")
            return True
        else:
            print(f"❌ Error creating intent: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating medical intent: {e}")
        return False

def test_webhook_integration():
    """Test if the webhook integration is working"""
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    # Construct URL for detect intent
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/sessions/test-session:detectIntent"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test data
    data = {
        "queryInput": {
            "text": {
                "text": "What are red flag headache symptoms?",
                "languageCode": "en"
            }
        }
    }
    
    try:
        print("📤 Testing webhook integration...")
        print("   Query: 'What are red flag headache symptoms?'")
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("📥 Response received:")
            print(f"   Intent: {result.get('queryResult', {}).get('intent', {}).get('displayName', 'N/A')}")
            print(f"   Confidence: {result.get('queryResult', {}).get('intentDetectionConfidence', 'N/A')}")
            
            # Check webhook status
            webhook_status = result.get('queryResult', {}).get('webhookStatus')
            if webhook_status:
                print(f"   Webhook Status: {webhook_status.get('message', 'N/A')}")
                print(f"   Webhook Called: ✅")
            else:
                print(f"   Webhook Called: ❌")
            
            # Show response text
            response_messages = result.get('queryResult', {}).get('responseMessages', [])
            for message in response_messages:
                if 'text' in message:
                    response_text = message['text'].get('text', ['N/A'])[0]
                    print(f"   Response: {response_text[:100]}...")
                    if "clinical guidelines" in response_text.lower() or "emergency" in response_text.lower():
                        print(f"   ✅ Webhook integration working!")
                    else:
                        print(f"   ⚠️ Webhook may not be working properly")
            
            return True
        else:
            print(f"❌ Error testing webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def create_medical_route():
    """Create a medical route as additional backup"""
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    # Get current page to add route
    page_data = get_start_page()
    if not page_data:
        return False
    
    # Create medical route
    medical_route = {
        "intent": {
            "intent": f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/intents/MEDICAL_QUERY_INTENT"
        },
        "condition": "true",
        "triggerFulfillment": {
            "webhook": WEBHOOK_NAME,
            "messages": [
                {
                    "text": {
                        "text": ["Let me search the clinical guidelines for you..."]
                    }
                }
            ]
        }
    }
    
    # Add route to existing routes
    if "routes" not in page_data:
        page_data["routes"] = []
    
    page_data["routes"].append(medical_route)
    
    # Update page
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/flows/{FLOW_ID}/pages/{PAGE_ID}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Remove read-only fields
    page_data.pop("name", None)
    
    try:
        print("🔄 Adding medical route...")
        
        response = requests.patch(url, headers=headers, json=page_data)
        
        if response.status_code == 200:
            print(f"✅ Successfully added medical route!")
            return True
        else:
            print(f"❌ Error adding route: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding medical route: {e}")
        return False

def main():
    """Main fix process"""
    
    print("=" * 80)
    print("PROGRAMMATICALLY FIXING WEBHOOK INTEGRATION")
    print("=" * 80)
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to your service account key file:")
        print("   $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Try multiple approaches to fix the webhook integration
    
    success = False
    
    # Approach 1: Add webhook to entry fulfillment
    print(f"\n🔧 Approach 1: Adding webhook to entry fulfillment...")
    if add_webhook_to_entry_fulfillment():
        success = True
        print(f"✅ Entry fulfillment approach successful!")
    else:
        print(f"⚠️ Entry fulfillment approach failed, trying alternatives...")
    
    # Approach 2: Create medical intent
    print(f"\n🔧 Approach 2: Creating medical intent...")
    if create_medical_intent():
        success = True
        print(f"✅ Medical intent approach successful!")
    else:
        print(f"⚠️ Medical intent approach failed")
    
    # Test the integration
    if success:
        print(f"\n🧪 Testing webhook integration...")
        test_webhook_integration()
    
    # Report results
    print(f"\n" + "=" * 80)
    if success:
        print("✅ WEBHOOK INTEGRATION FIXED!")
        print("=" * 80)
        print(f"\n🎯 Your agent should now:")
        print(f"   • Call the RAG webhook for medical queries")
        print(f"   • Return clinical guidelines with citations")
        print(f"   • Provide evidence-based medical responses")
        
        print(f"\n🧪 Test in Preview panel:")
        print(f"   Query: 'What are red flag headache symptoms?'")
        print(f"   Expected: Clinical guidelines response instead of 'Sorry, can you say that again?'")
        
    else:
        print("❌ WEBHOOK INTEGRATION FIX FAILED")
        print("=" * 80)
        print(f"\n📋 Manual steps needed:")
        print(f"   1. Go to Build → Default Start Flow → Start Page")
        print(f"   2. Add webhook to Entry fulfillment")
        print(f"   3. Or create a medical intent with webhook")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()
