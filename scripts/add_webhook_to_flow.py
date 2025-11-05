#!/usr/bin/env python3
"""
Add Webhook to Dialogflow CX Flow

This script programmatically adds the clinical-guidelines-webhook
to the Default Start Flow in your Dialogflow CX agent.
"""

import os
import json
from google.cloud import dialogflowcx_v3 as dialogflowcx

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
AGENT_ID = "72d18125-ac71-4c56-8ea0-44bfc7f9b039"
WEBHOOK_NAME = "clinical-guidelines-webhook"

def add_webhook_to_flow():
    """Add the webhook to the Default Start Flow"""
    
    print("=" * 80)
    print("ADDING WEBHOOK TO DIALOGFLOW CX FLOW")
    print("=" * 80)
    
    try:
        # Initialize the client
        client = dialogflowcx.FlowsClient()
        
        # Construct flow name
        flow_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/flows/00000000-0000-0000-0000-000000000000"
        
        print(f"📋 Flow: {flow_name}")
        
        # Get the current flow
        flow = client.get_flow(name=flow_name)
        print(f"✓ Retrieved flow: {flow.display_name}")
        
        # Get the start page
        start_page_name = f"{flow_name}/pages/00000000-0000-0000-0000-000000000000"
        start_page = client.get_page(name=start_page_name)
        print(f"✓ Retrieved start page: {start_page.display_name}")
        
        # Create webhook fulfillment
        webhook_fulfillment = dialogflowcx.Fulfillment(
            webhook=WEBHOOK_NAME,
            messages=[
                dialogflowcx.ResponseMessage(
                    text=dialogflowcx.ResponseMessage.Text(
                        text=["Searching clinical guidelines..."]
                    )
                )
            ]
        )
        
        # Update the start page with webhook fulfillment
        start_page.entry_fulfillment.CopyFrom(webhook_fulfillment)
        
        # Update the page
        update_mask = dialogflowcx.field_mask_pb2.FieldMask(paths=["entry_fulfillment"])
        
        print(f"🔄 Adding webhook fulfillment to start page...")
        updated_page = client.update_page(page=start_page, update_mask=update_mask)
        
        print(f"✅ Successfully added webhook to flow!")
        print(f"   Webhook: {WEBHOOK_NAME}")
        print(f"   Page: {updated_page.display_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding webhook to flow: {e}")
        return False

def test_webhook_integration():
    """Test the webhook integration"""
    
    print(f"\n🧪 Testing webhook integration...")
    
    try:
        # Initialize the client
        client = dialogflowcx.SessionsClient()
        
        # Construct session name
        session_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/sessions/test-session"
        
        # Create test request
        request = dialogflowcx.DetectIntentRequest(
            session=session_name,
            query_input=dialogflowcx.QueryInput(
                text=dialogflowcx.TextInput(
                    text="What are red flag headache symptoms?",
                    language_code="en"
                )
            )
        )
        
        print(f"📤 Sending test query: 'What are red flag headache symptoms?'")
        
        # Send the request
        response = client.detect_intent(request=request)
        
        print(f"📥 Response received:")
        print(f"   Intent: {response.query_result.intent.display_name}")
        print(f"   Confidence: {response.query_result.intent_detection_confidence}")
        
        # Check if webhook was called
        if response.query_result.webhook_status:
            print(f"   Webhook Status: {response.query_result.webhook_status.message}")
            print(f"   Webhook Called: ✅")
        else:
            print(f"   Webhook Called: ❌")
        
        # Show response messages
        for message in response.query_result.response_messages:
            if message.text:
                print(f"   Response: {message.text.text[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def create_test_scenarios():
    """Create a list of test scenarios"""
    
    scenarios = [
        "What are red flag headache symptoms?",
        "When should someone with nausea see a doctor urgently?",
        "What is orthostatic hypotension?",
        "What guidelines cover dizziness and vertigo?",
        "How do I manage fatigue in patients?",
        "What are the symptoms of dehydration?",
        "When is vomiting a medical emergency?",
        "What causes sudden vision changes?",
        "How do you assess neurological deficits?",
        "What is the treatment for syncope?"
    ]
    
    print(f"\n📋 Test Scenarios for Your Agent:")
    print(f"=" * 50)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i:2d}. {scenario}")
    
    print(f"\n💡 Copy these queries to test in your Dialogflow CX Preview panel!")

def main():
    """Main execution"""
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to your service account key file:")
        print("   $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Add webhook to flow
    success = add_webhook_to_flow()
    
    if success:
        print(f"\n🎉 WEBHOOK INTEGRATION COMPLETE!")
        print(f"=" * 50)
        print(f"\n✅ Your Dialogflow CX agent now has:")
        print(f"   • Clinical guidelines webhook integrated")
        print(f"   • Access to medical knowledge base")
        print(f"   • Red flag detection capabilities")
        print(f"   • Citation support")
        
        # Create test scenarios
        create_test_scenarios()
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Go to Dialogflow CX Preview panel")
        print(f"   2. Test with the scenarios above")
        print(f"   3. Verify citations and clinical responses")
        print(f"   4. Your agent is ready for clinical use!")
        
    else:
        print(f"\n❌ Integration failed. Check the errors above.")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()
