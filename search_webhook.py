#!/usr/bin/env python3
"""
Vertex AI Search Webhook for Dialogflow CX Integration

This webhook:
1. Receives queries from Dialogflow CX
2. Searches the clinical-guidelines-datastore
3. Returns formatted responses with citations
4. Handles clinical triage recommendations

Deploy this as a Cloud Function or Cloud Run service.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from google.cloud import discoveryengine_v1 as discoveryengine

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
DATASTORE_ID = "clinical-guidelines-datastore"
LOCATION = "global"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def search_clinical_guidelines(query, max_results=3):
    """Search the clinical guidelines datastore"""
    
    try:
        # Initialize client
        client = discoveryengine.SearchServiceClient()
        
        # Construct serving config
        serving_config = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATASTORE_ID}/servingConfigs/default_config"
        
        # Create search request
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=max_results,
            # Enable snippets and citations
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    max_snippet_count=3,
                    reference_only=False,
                    return_snippet=True,
                ),
                summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                    summary_result_count=max_results,
                    include_citations=True,
                    model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                        version="stable",
                    ),
                ),
            ),
        )
        
        # Execute search
        response = client.search(request)
        
        return response
        
    except Exception as e:
        logging.error(f"Search error: {e}")
        return None

def format_clinical_response(search_response, user_query):
    """Format the search response for clinical triage"""
    
    if not search_response or not search_response.results:
        return {
            "response": "I couldn't find relevant information in the clinical guidelines. Please consult your healthcare provider for medical advice.",
            "citations": [],
            "triage_level": "unknown"
        }
    
    # Extract results
    results = []
    citations = []
    
    for result in search_response.results[:3]:  # Top 3 results
        # Get document data
        doc = result.document.derived_struct_data
        
        # Extract key information
        title = doc.get("title", "Clinical Guideline")
        snippet = doc.get("snippet", "")
        link = doc.get("link", "")
        
        # Try to extract document ID from title or content
        doc_id = "Unknown"
        if "OID-" in title:
            doc_id = title
        elif "OID-" in snippet:
            # Extract OID from snippet
            import re
            oid_match = re.search(r'OID-[A-Z0-9-]+', snippet)
            if oid_match:
                doc_id = oid_match.group()
        
        results.append({
            "title": title,
            "snippet": snippet,
            "document_id": doc_id
        })
        
        citations.append(f"[{doc_id}] {title}")
    
    # Analyze for red flags and triage
    combined_text = " ".join([r["snippet"] for r in results]).lower()
    query_lower = user_query.lower()
    
    # Determine triage level
    triage_level = "routine"
    urgency_note = ""
    
    # Red flag detection
    red_flags = [
        "thunderclap", "worst headache", "vision changes", "neurological deficits",
        "hematemesis", "vomiting blood", "severe dehydration", "bilious vomiting",
        "stroke", "chest pain", "shortness of breath", "loss of consciousness",
        "syncope", "severe abdominal pain", "acute abdomen"
    ]
    
    if any(flag in combined_text for flag in red_flags):
        triage_level = "emergency"
        urgency_note = "🚨 EMERGENCY: Based on the symptoms described, immediate medical attention is required. Please call 911 or go to the nearest emergency department."
    
    # Urgent symptoms
    urgent_symptoms = [
        "persistent vomiting", "unable to keep fluids", "fever with confusion",
        "severe weakness", "unintentional weight loss", "jaundice"
    ]
    
    if any(symptom in combined_text for symptom in urgent_symptoms) and triage_level != "emergency":
        triage_level = "urgent"
        urgency_note = "⚡ URGENT: These symptoms require same-day medical evaluation. Please contact your healthcare provider or visit urgent care."
    
    # Build response
    response_parts = []
    
    if urgency_note:
        response_parts.append(urgency_note)
        response_parts.append("")
    
    # Add clinical information
    response_parts.append("Based on clinical guidelines:")
    response_parts.append("")
    
    for i, result in enumerate(results, 1):
        response_parts.append(f"{i}. {result['snippet']}")
        if i < len(results):
            response_parts.append("")
    
    # Add citations
    response_parts.append("")
    response_parts.append("Sources:")
    for citation in citations:
        response_parts.append(f"• {citation}")
    
    # Add disclaimer
    response_parts.append("")
    response_parts.append("⚠️ This information is for educational purposes only and does not replace professional medical advice. Always consult your healthcare provider.")
    
    return {
        "response": "\n".join(response_parts),
        "citations": citations,
        "triage_level": triage_level,
        "urgency_note": urgency_note
    }

@app.route('/webhook', methods=['POST'])
def webhook():
    """Dialogflow CX webhook endpoint"""
    
    try:
        # Get request data
        req = request.get_json()
        logging.info(f"Received request: {json.dumps(req, indent=2)}")
        
        # Extract user query
        user_query = ""
        if "queryResult" in req and "queryText" in req["queryResult"]:
            user_query = req["queryResult"]["queryText"]
        elif "text" in req:
            user_query = req["text"]
        else:
            # Try to extract from various possible fields
            user_query = str(req.get("message", ""))
        
        if not user_query:
            user_query = "clinical guidelines help"
        
        logging.info(f"User query: {user_query}")
        
        # Search clinical guidelines
        search_response = search_clinical_guidelines(user_query)
        
        if not search_response:
            return jsonify({
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": ["I'm having trouble accessing the clinical guidelines. Please try again or consult your healthcare provider."]
                            }
                        }
                    ]
                }
            })
        
        # Format response
        clinical_response = format_clinical_response(search_response, user_query)
        
        # Return Dialogflow CX response
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [clinical_response["response"]]
                        }
                    }
                ]
            },
            # Add custom payload for additional data
            "payload": {
                "triage_level": clinical_response["triage_level"],
                "citations": clinical_response["citations"],
                "urgency_note": clinical_response.get("urgency_note", "")
            }
        })
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": ["I encountered an error processing your request. Please try again or consult your healthcare provider."]
                        }
                    }
                ]
            }
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "clinical-guidelines-webhook"})

@app.route('/test', methods=['POST'])
def test_search():
    """Test endpoint for direct search testing"""
    try:
        data = request.get_json()
        query = data.get("query", "What are red flag headache symptoms?")
        
        search_response = search_clinical_guidelines(query)
        clinical_response = format_clinical_response(search_response, query)
        
        return jsonify({
            "query": query,
            "response": clinical_response["response"],
            "triage_level": clinical_response["triage_level"],
            "citations": clinical_response["citations"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
