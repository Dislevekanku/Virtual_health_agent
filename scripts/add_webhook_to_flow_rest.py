#!/usr/bin/env python3
"""
Add Webhook to Dialogflow CX Flow using REST API

This script programmatically adds the clinical-guidelines-webhook
to the Default Start Flow using the REST API.
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

def get_access_token():
    """Get access token for API calls"""
    
    try:
        # Set up authentication
        credentials, project = default()
        
        # Refresh the token
        credentials.refresh(Request())
        
        return credentials.token
        
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None

def get_flow_info():
    """Get flow information"""
    
    access_token = get_access_token()
    if not access_token:
        return None
    
    # Construct URL for the default flow
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/flows/00000000-0000-0000-0000-000000000000"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            flow_data = response.json()
            print(f"✓ Retrieved flow: {flow_data.get('displayName', 'Default Start Flow')}")
            return flow_data
        else:
            print(f"❌ Error getting flow: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting flow info: {e}")
        return None

def get_start_page_info():
    """Get start page information"""
    
    access_token = get_access_token()
    if not access_token:
        return None
    
    # Construct URL for the start page
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/flows/00000000-0000-0000-0000-000000000000/pages/00000000-0000-0000-0000-000000000000"
    
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
        print(f"❌ Error getting start page info: {e}")
        return None

def update_start_page_with_webhook():
    """Update the start page with webhook fulfillment"""
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    # Get current page data
    page_data = get_start_page_info()
    if not page_data:
        return False
    
    # Update the page with webhook fulfillment
    page_data["entryFulfillment"] = {
        "webhook": WEBHOOK_NAME,
        "messages": [
            {
                "text": {
                    "text": ["Searching clinical guidelines..."]
                }
            }
        ]
    }
    
    # Construct URL for updating the page
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/flows/00000000-0000-0000-0000-000000000000/pages/00000000-0000-0000-0000-000000000000"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Remove read-only fields
    page_data.pop("name", None)
    
    try:
        print(f"🔄 Updating start page with webhook fulfillment...")
        
        response = requests.patch(url, headers=headers, json=page_data)
        
        if response.status_code == 200:
            updated_page = response.json()
            print(f"✅ Successfully added webhook to flow!")
            print(f"   Webhook: {WEBHOOK_NAME}")
            print(f"   Page: {updated_page.get('displayName', 'Start Page')}")
            return True
        else:
            print(f"❌ Error updating page: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating start page: {e}")
        return False

def test_webhook_with_rest():
    """Test the webhook using REST API"""
    
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
        print(f"📤 Sending test query: 'What are red flag headache symptoms?'")
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"📥 Response received:")
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
                    print(f"   Response: {message['text'].get('text', ['N/A'])[0]}")
            
            return True
        else:
            print(f"❌ Error testing webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def create_manual_instructions():
    """Create manual instructions as fallback"""
    
    instructions = f"""
# Manual Webhook Integration (Fallback)

Since programmatic integration encountered issues, here's how to add the webhook manually:

## Step 1: Go to Dialogflow CX
- URL: https://dialogflow.cloud.google.com/cx/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}

## Step 2: Navigate to Flow
1. Go to **"Build"** tab
2. Click on **"Default Start Flow"**
3. Click on **"Start Page"**

## Step 3: Add Webhook Fulfillment
1. In the **"Entry fulfillment"** section
2. Click **"+ Add dialogue option"**
3. Select **"Call webhook"**
4. Select: `{WEBHOOK_NAME}`
5. Click **"Save"**

## Step 4: Test
1. Go to **"Preview"** panel (right side)
2. Type: `What are red flag headache symptoms?`
3. Should return clinical guidelines with citations!

## Your Webhook URL
`https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/webhook`

## Test Queries
1. What are red flag headache symptoms?
2. When should someone with nausea see a doctor urgently?
3. What is orthostatic hypotension?
4. What guidelines cover dizziness and vertigo?
"""
    
    with open("MANUAL_WEBHOOK_INTEGRATION.md", "w") as f:
        f.write(instructions)
    
    print(f"📋 Manual instructions saved to MANUAL_WEBHOOK_INTEGRATION.md")

def main():
    """Main execution"""
    
    print("=" * 80)
    print("ADDING WEBHOOK TO DIALOGFLOW CX FLOW (REST API)")
    print("=" * 80)
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to your service account key file:")
        print("   $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Try to update the page with webhook
    success = update_start_page_with_webhook()
    
    if success:
        print(f"\n🎉 WEBHOOK INTEGRATION COMPLETE!")
        print(f"=" * 50)
        
        # Test the integration
        print(f"\n🧪 Testing webhook integration...")
        test_webhook_with_rest()
        
        print(f"\n✅ Your Dialogflow CX agent now has:")
        print(f"   • Clinical guidelines webhook integrated")
        print(f"   • Access to medical knowledge base")
        print(f"   • Red flag detection capabilities")
        print(f"   • Citation support")
        
    else:
        print(f"\n⚠️ Programmatic integration failed.")
        print(f"   Creating manual instructions...")
        create_manual_instructions()
        
        print(f"\n📋 Please follow the manual instructions in:")
        print(f"   MANUAL_WEBHOOK_INTEGRATION.md")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()
