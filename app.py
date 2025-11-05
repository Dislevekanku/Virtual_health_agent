#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask backend server for Virtual Health Assistant frontend
Handles Dialogflow CX API integration
"""

import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account
from google.api_core import client_options
from google.protobuf.json_format import MessageToDict

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
SERVICE_ACCOUNT_KEY = "key.json"
AGENT_INFO_FILE = "agent_info.json"

# Load agent info
with open(AGENT_INFO_FILE, 'r') as f:
    agent_info = json.load(f)
    AGENT_NAME = agent_info['agent_name']
    LOCATION = agent_info['location']

# Initialize credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_KEY
)

# Initialize session client
client_options_obj = client_options.ClientOptions(
    api_endpoint=f"{LOCATION}-dialogflow.googleapis.com:443"
)
sessions_client = dialogflow.SessionsClient(
    credentials=credentials,
    client_options=client_options_obj
)

# Store sessions in memory (in production, use Redis or database)
sessions = {}


def create_session_path(session_id: str) -> str:
    """Create session path for Dialogflow CX"""
    return f"{AGENT_NAME}/sessions/{session_id}"


def detect_intent(session_id: str, text: str, language_code: str = "en") -> dict:
    """Send text to Dialogflow CX agent and get response"""
    
    session_path = create_session_path(session_id)
    
    text_input = dialogflow.TextInput(text=text)
    query_input = dialogflow.QueryInput(
        text=text_input,
        language_code=language_code
    )
    
    # Create detect intent request
    request = dialogflow.DetectIntentRequest(
        session=session_path,
        query_input=query_input
    )
    
    try:
        response = sessions_client.detect_intent(request=request)
        
        # Extract response
        response_text = ""
        if response.query_result.response_messages:
            for message in response.query_result.response_messages:
                if message.text and message.text.text:
                    response_text += message.text.text[0] + "\n"
        
        # Get intent info
        intent_name = None
        intent_confidence = 0.0
        if response.query_result.intent:
            intent_name = response.query_result.intent.display_name
            intent_confidence = response.query_result.intent_detection_confidence
        
        # Get parameters
        parameters = {}
        if response.query_result.parameters:
            try:
                if hasattr(response.query_result.parameters, '_pb'):
                    parameters = MessageToDict(response.query_result.parameters._pb)
                elif hasattr(response.query_result.parameters, 'fields'):
                    parameters = {
                        k: v.string_value if hasattr(v, 'string_value') else 
                          v.number_value if hasattr(v, 'number_value') else 
                          str(v)
                        for k, v in response.query_result.parameters.fields.items()
                    }
            except Exception as e:
                print(f"Parameter extraction error: {e}")
                parameters = {}
        
        # Get current page
        page_name = None
        if response.query_result.current_page:
            page_name = response.query_result.current_page.display_name
        
        return {
            'response_text': response_text.strip(),
            'intent': intent_name,
            'confidence': float(intent_confidence),
            'parameters': parameters,
            'current_page': page_name,
            'match_type': response.query_result.match.match_type if response.query_result.match else None,
        }
    
    except Exception as e:
        print(f"Error in detect_intent: {e}")
        import traceback
        traceback.print_exc()
        return {
            'response_text': f"I'm sorry, I encountered an error. Please try again. Error: {str(e)}",
            'intent': None,
            'confidence': 0.0,
            'parameters': {},
            'current_page': None,
            'error': str(e)
        }


@app.route('/')
def index():
    """Serve the main frontend page"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from frontend"""
    
    try:
        data = request.json
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Create new session if needed
        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                'created_at': str(uuid.uuid4()),
                'messages': []
            }
        
        # Get response from Dialogflow CX
        result = detect_intent(session_id, message)
        
        # Store conversation
        sessions[session_id]['messages'].append({
            'user': message,
            'agent': result['response_text'],
            'timestamp': str(uuid.uuid4())
        })
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'response': result['response_text'],
            'intent': result['intent'],
            'confidence': result['confidence'],
            'current_page': result['current_page'],
            'parameters': result.get('parameters', {})
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/session/new', methods=['POST'])
def new_session():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'created_at': str(uuid.uuid4()),
        'messages': []
    }
    return jsonify({
        'success': True,
        'session_id': session_id
    })


@app.route('/api/conversation/save', methods=['POST'])
def save_conversation():
    """Save conversation to history"""
    try:
        data = request.json
        conversation = {
            'session_id': data.get('session_id'),
            'timestamp': datetime.now().isoformat(),
            'messages': data.get('messages', []),
            'summary': data.get('summary', {})
        }
        
        # Load existing history
        history_file = 'conversation_history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {'conversations': []}
        
        # Add new conversation
        history['conversations'].append(conversation)
        
        # Keep only last 100 conversations
        if len(history['conversations']) > 100:
            history['conversations'] = history['conversations'][-100:]
        
        # Save to file
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Conversation saved'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/conversation/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history"""
    try:
        history_file = 'conversation_history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
            return jsonify({
                'success': True,
                'conversations': history.get('conversations', [])
            })
        else:
            return jsonify({
                'success': True,
                'conversations': []
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agent': AGENT_NAME,
        'active_sessions': len(sessions)
    })


if __name__ == '__main__':
    print("="*60)
    print("Virtual Health Assistant - Frontend Server")
    print("="*60)
    print(f"Agent: {AGENT_NAME}")
    print(f"Location: {LOCATION}")
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)

