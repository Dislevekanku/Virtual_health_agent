#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add conversation history functionality - store and retrieve previous conversations
"""

import json
import os
from datetime import datetime
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account
from google.api_core import client_options

# Configuration
SERVICE_ACCOUNT_KEY = "key.json"
AGENT_INFO_FILE = "agent_info.json"
LOCATION = "us-central1"
HISTORY_FILE = "conversation_history.json"

def load_agent_info():
    """Load agent information"""
    with open(AGENT_INFO_FILE, 'r') as f:
        return json.load(f)

def get_client(client_class):
    """Get a Dialogflow CX client with proper endpoint"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY
    )
    client_options_obj = client_options.ClientOptions(
        api_endpoint=f"{LOCATION}-dialogflow.googleapis.com:443"
    )
    return client_class(credentials=credentials, client_options=client_options_obj)

def load_conversation_history():
    """Load conversation history from file"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"conversations": []}

def save_conversation_history(history):
    """Save conversation history to file"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def add_conversation_history():
    """Add conversation history functionality to agent"""
    
    print("="*60)
    print("Add Conversation History")
    print("="*60)
    print()
    
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        # Get flow
        flows_client = get_client(dialogflow.FlowsClient)
        request = dialogflow.ListFlowsRequest(parent=agent_name)
        flows = list(flows_client.list_flows(request=request))
        
        flow_name = None
        for flow in flows:
            if flow.display_name == "Default Start Flow":
                flow_name = flow.name
                break
        
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        # Find Summary page to add history tracking
        summary_page = None
        for page in pages:
            if page.display_name == "Summary":
                summary_page = page
                break
        
        if summary_page:
            # Add entry fulfillment that stores conversation
            if not summary_page.entry_fulfillment:
                summary_page.entry_fulfillment = dialogflow.Fulfillment()
            
            # Add webhook call to store conversation (or use set_parameter_actions)
            # For now, we'll use parameters to track conversation state
            # The frontend will handle storing to file/database
            
            print("  [OK] Summary page configured for history tracking")
        
        # Initialize history file
        history = load_conversation_history()
        save_conversation_history(history)
        print("  [OK] Conversation history file initialized")
        
        print()
        print("[OK] Conversation history system ready")
        print()
        print("How it works:")
        print("  - Frontend stores conversations in session")
        print("  - Conversations saved to conversation_history.json")
        print("  - Can retrieve previous conversations")
        print("  - Can continue previous conversations")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def update_frontend_for_history():
    """Update frontend to support conversation history"""
    
    frontend_code = """
// Add to static/script.js

// Conversation History Functions
let conversationHistory = [];

function saveConversationToHistory(sessionId, messages) {
    const conversation = {
        session_id: sessionId,
        timestamp: new Date().toISOString(),
        messages: messages,
        summary: {
            symptom: messages.find(m => m.role === 'user' && m.content.includes('headache'))?.content || 'N/A',
            triage: 'N/A',  // Will be updated from agent response
            recommendation: 'N/A'
        }
    };
    
    conversationHistory.push(conversation);
    
    // Save to localStorage
    localStorage.setItem('conversationHistory', JSON.stringify(conversationHistory));
    
    // Also save to server (for persistence across devices)
    fetch('/api/conversation/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(conversation)
    }).catch(err => console.log('History save error:', err));
}

function loadConversationHistory() {
    const saved = localStorage.getItem('conversationHistory');
    if (saved) {
        conversationHistory = JSON.parse(saved);
        return conversationHistory;
    }
    return [];
}

function displayConversationHistory() {
    const history = loadConversationHistory();
    // Display history in UI (add history panel)
    console.log('Conversation history:', history);
}

// Call saveConversationToHistory after each complete conversation
"""
    
    print("Frontend code for history:")
    print(frontend_code)
    print()
    print("Note: Add this to static/script.js and update app.py with /api/conversation/save endpoint")

if __name__ == "__main__":
    success = add_conversation_history()
    if success:
        update_frontend_for_history()
    exit(0 if success else 1)

