#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the webhook to see what error we're getting
"""

import requests
import json

WEBHOOK_URL = "https://us-central1-ai-agent-health-assistant.cloudfunctions.net/simplified-rag-webhook/webhook"

def test_webhook():
    """Test the webhook with a sample Dialogflow CX request"""
    
    print("="*60)
    print("Testing Webhook")
    print("="*60)
    print()
    
    # Sample Dialogflow CX webhook request format
    sample_request = {
        "session": "projects/test/locations/us-central1/agents/test/sessions/test",
        "queryResult": {
            "queryText": "I have a headache",
            "parameters": {
                "symptom_type": "headache",
                "duration": "2 days ago",
                "severity": 6
            },
            "intent": {
                "displayName": "symptom_headache"
            }
        },
        "fulfillmentInfo": {
            "tag": "clinical_grounding"
        }
    }
    
    print("Sending request to webhook...")
    print(f"URL: {WEBHOOK_URL}")
    print()
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=sample_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ Webhook responded successfully!")
            print()
            print("Response:")
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
            except:
                print(response.text)
        else:
            print(f"❌ Webhook returned error: {response.status_code}")
            print()
            print("Response:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("❌ Webhook timeout - function may not be responding")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - function may not be deployed or accessible")
        print()
        print("Possible causes:")
        print("  1. Cloud Function not deployed")
        print("  2. URL incorrect")
        print("  3. Network/firewall blocking access")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("="*60)
    print("Testing Health Endpoint")
    print("="*60)
    print()
    
    health_url = WEBHOOK_URL.replace("/webhook", "/health")
    try:
        health_response = requests.get(health_url, timeout=10)
        print(f"Health Status: {health_response.status_code}")
        print(f"Response: {health_response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")

if __name__ == "__main__":
    test_webhook()

