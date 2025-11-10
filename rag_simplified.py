#!/usr/bin/env python3
"""
Simplified RAG Implementation using REST APIs

This implements the core RAG flow using REST APIs:
1. Query Vertex AI Search for clinical guidelines
2. Build grounded prompt with retrieved context
3. Call Gemini via REST API with retrieved context
4. Return evidence-based response with citations

This avoids complex dependency issues and uses standard REST APIs.
"""

import os
import json
import logging
import re
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google.auth import default
from google.auth.transport.requests import Request

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
SEARCH_LOCATION = "global"
DATASTORE_ID = "clinical-guidelines-datastore"
MODEL_NAME = "gemini-1.5-flash-001"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Search result from Vertex AI Search"""
    snippet: str
    title: str
    source: str
    document_id: str
    score: float = 0.0

@dataclass
class RAGResponse:
    """RAG response with citations and recommendations"""
    answer: str
    citations: List[str]
    triage_level: str  # emergency, urgent, routine
    next_steps: str
    confidence: float
    emergency_flags: List[str]

class SimplifiedSearchClient:
    """Simplified Vertex AI Search client using REST API"""
    
    def __init__(self, project_id: str, location: str, datastore_id: str):
        self.project_id = project_id
        self.location = location
        self.datastore_id = datastore_id
        self.access_token = None
        
        # Emergency symptom keywords
        self.emergency_keywords = [
            "thunderclap", "worst headache", "vision changes", "neurological deficits",
            "chest pain", "shortness of breath", "loss of consciousness", "syncope",
            "stroke", "heart attack", "severe abdominal pain", "acute abdomen",
            "hematemesis", "vomiting blood", "severe dehydration", "bilious vomiting"
        ]
        
        self.urgent_keywords = [
            "persistent vomiting", "unable to keep fluids", "fever with confusion",
            "severe weakness", "unintentional weight loss", "jaundice", "severe pain"
        ]
    
    def _get_access_token(self):
        """Get access token for API calls"""
        if not self.access_token:
            try:
                credentials, project = default()
                credentials.refresh(Request())
                self.access_token = credentials.token
            except Exception as e:
                logger.error(f"Error getting access token: {e}")
                return None
        return self.access_token
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search clinical guidelines using REST API"""
        
        access_token = self._get_access_token()
        if not access_token:
            return []
        
        try:
            logger.info(f"Searching clinical guidelines for: {query}")
            
            # Construct search URL
            url = f"https://discoveryengine.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/collections/default_collection/dataStores/{self.datastore_id}/servingConfigs/default_config:search"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Search request payload
            payload = {
                "query": query,
                "pageSize": top_k,
                "contentSearchSpec": {
                    "snippetSpec": {
                        "maxSnippetCount": 3,
                        "referenceOnly": False,
                        "returnSnippet": True
                    },
                    "summarySpec": {
                        "summaryResultCount": top_k,
                        "includeCitations": True,
                        "modelSpec": {
                            "version": "stable"
                        }
                    },
                    "searchResultMode": "DOCUMENTS",
                    "maxExtractiveAnswerCount": 3
                },
                "queryExpansionSpec": {
                    "condition": "AUTO"
                },
                "spellCorrectionSpec": {
                    "mode": "AUTO"
                }
            }
            
            # Make search request
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Search API error: {response.status_code} - {response.text}")
                return []
            
            search_data = response.json()
            results = []
            
            # Parse search results
            for i, result in enumerate(search_data.get("results", [])):
                doc = result.get("document", {}).get("derivedStructData", {})
                
                snippet = doc.get("snippet", "")
                title = doc.get("title", "Clinical Guideline")
                source = doc.get("source", "Clinical Guidelines Database")
                
                # Extract document ID
                document_id = self._extract_document_id(title, snippet)
                
                # Calculate relevance score
                score = self._calculate_relevance(query, snippet, i)
                
                search_result = SearchResult(
                    snippet=snippet,
                    title=title,
                    source=source,
                    document_id=document_id,
                    score=score
                )
                
                results.append(search_result)
                logger.info(f"Retrieved: {document_id} (score: {score:.2f})")
            
            # Sort by relevance score
            results.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Retrieved {len(results)} relevant clinical guidelines")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _extract_document_id(self, title: str, snippet: str) -> str:
        """Extract document ID from title or snippet"""
        
        # Look for OID pattern
        oid_pattern = r'OID-[A-Z0-9-]+'
        
        # Check title first
        oid_match = re.search(oid_pattern, title)
        if oid_match:
            return oid_match.group()
        
        # Check snippet
        oid_match = re.search(oid_pattern, snippet)
        if oid_match:
            return oid_match.group()
        
        # Fallback to truncated title
        return title[:30] + "..." if len(title) > 30 else title
    
    def _calculate_relevance(self, query: str, snippet: str, rank: int) -> float:
        """Calculate medical relevance score"""
        
        query_lower = query.lower()
        snippet_lower = snippet.lower()
        
        # Base score from ranking
        base_score = 1.0 - (rank * 0.1)
        
        # Boost for emergency keywords
        emergency_boost = 0.0
        for keyword in self.emergency_keywords:
            if keyword in snippet_lower and keyword in query_lower:
                emergency_boost += 0.2
        
        # Boost for urgent keywords
        urgent_boost = 0.0
        for keyword in self.urgent_keywords:
            if keyword in snippet_lower and keyword in query_lower:
                urgent_boost += 0.1
        
        # Boost for medical terminology match
        medical_terms = ["symptom", "diagnosis", "treatment", "guideline", "protocol", "assessment"]
        medical_boost = sum(0.05 for term in medical_terms if term in snippet_lower and term in query_lower)
        
        return min(1.0, base_score + emergency_boost + urgent_boost + medical_boost)

class SimplifiedGeminiClient:
    """Simplified Gemini client using REST API"""
    
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
        self.access_token = None
    
    def _get_access_token(self):
        """Get access token for API calls"""
        if not self.access_token:
            try:
                credentials, project = default()
                credentials.refresh(Request())
                self.access_token = credentials.token
            except Exception as e:
                logger.error(f"Error getting access token: {e}")
                return None
        return self.access_token
    
    def generate_response(self, query: str, search_results: List[SearchResult]) -> RAGResponse:
        """Generate medical response using Gemini REST API"""
        
        access_token = self._get_access_token()
        if not access_token:
            return self._create_fallback_response(query)
        
        try:
            # Build grounded prompt
            context = self._build_medical_context(search_results)
            prompt = self._build_grounded_prompt(query, context)
            
            logger.info(f"Generating response with {len(search_results)} sources")
            
            # Call Gemini REST API
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{MODEL_NAME}:generateContent"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 500,
                    "candidateCount": 1
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_MEDICAL",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._create_fallback_response(query)
            
            result_data = response.json()
            
            # Extract response text
            response_text = ""
            if "candidates" in result_data and len(result_data["candidates"]) > 0:
                candidate = result_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    response_text = candidate["content"]["parts"][0].get("text", "")
            
            if not response_text:
                return self._create_fallback_response(query)
            
            # Parse and structure response
            rag_response = self._parse_medical_response(response_text, query, search_results)
            
            logger.info(f"Generated response with triage level: {rag_response.triage_level}")
            return rag_response
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return self._create_fallback_response(query)
    
    def _build_medical_context(self, search_results: List[SearchResult]) -> str:
        """Build medical context from search results"""
        
        context_parts = []
        for i, result in enumerate(search_results, start=1):
            # Clean and format snippet
            snippet = result.snippet.strip()
            if len(snippet) > 300:  # Truncate long snippets
                snippet = snippet[:300] + "..."
            
            context_part = f"""[{i}] {snippet}
Source: {result.title} ({result.document_id})
Relevance Score: {result.score:.2f}"""
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _build_grounded_prompt(self, query: str, context: str) -> str:
        """Build grounded prompt for Gemini"""
        
        return f"""You are a clinical decision support assistant that provides evidence-based information from clinical guidelines.

CRITICAL SAFETY RULES:
1. NEVER provide definitive diagnoses
2. NEVER replace professional medical judgment
3. ALWAYS base answers ONLY on the provided clinical guidelines context
4. ALWAYS cite source numbers [1], [2], etc.
5. ALWAYS include medical disclaimers
6. Flag emergency symptoms requiring immediate attention

CLINICAL GUIDELINES CONTEXT:
{context}

USER QUESTION: "{query}"

REQUIRED RESPONSE FORMAT:
1. Brief answer based on clinical guidelines
2. Sources cited [1], [2], etc.
3. Triage level: EMERGENCY/URGENT/ROUTINE
4. Next steps recommendation
5. Medical disclaimer

EMERGENCY SYMPTOMS (flag immediately):
- Thunderclap headache, vision changes, neurological deficits
- Chest pain, shortness of breath, loss of consciousness
- Severe abdominal pain, vomiting blood
- Any life-threatening symptoms

URGENT SYMPTOMS (same-day evaluation):
- Persistent vomiting, severe dehydration
- Fever with confusion, severe weakness
- Unintentional weight loss, jaundice

ANSWER:"""
    
    def _parse_medical_response(self, 
                               response_text: str, 
                               query: str, 
                               search_results: List[SearchResult]) -> RAGResponse:
        """Parse Gemini response into structured medical format"""
        
        # Extract citations
        citations = []
        citation_matches = re.findall(r'\[(\d+)\]', response_text)
        
        for match in citation_matches:
            idx = int(match) - 1
            if 0 <= idx < len(search_results):
                citations.append(search_results[idx].document_id)
        
        # Determine triage level and emergency flags
        triage_level, emergency_flags = self._assess_triage_level(response_text, query)
        
        # Extract next steps
        next_steps = self._extract_next_steps(response_text)
        
        # Calculate confidence
        confidence = self._calculate_confidence(response_text, search_results, citations)
        
        return RAGResponse(
            answer=response_text,
            citations=citations,
            triage_level=triage_level,
            next_steps=next_steps,
            confidence=confidence,
            emergency_flags=emergency_flags
        )
    
    def _assess_triage_level(self, response_text: str, query: str) -> tuple:
        """Assess triage level and identify emergency flags"""
        
        text_upper = response_text.upper()
        query_lower = query.lower()
        
        emergency_flags = []
        triage_level = "routine"
        
        # Emergency keywords
        emergency_keywords = [
            "thunderclap", "worst headache", "vision changes", "neurological deficits",
            "chest pain", "shortness of breath", "loss of consciousness", "stroke",
            "heart attack", "severe abdominal pain", "hematemesis", "vomiting blood"
        ]
        
        urgent_keywords = [
            "persistent vomiting", "severe dehydration", "fever with confusion",
            "severe weakness", "unintentional weight loss", "jaundice"
        ]
        
        # Check for emergency symptoms
        for keyword in emergency_keywords:
            if keyword in text_upper or keyword in query_lower:
                emergency_flags.append(keyword)
                triage_level = "emergency"
                break
        
        # Check for urgent symptoms (if not emergency)
        if triage_level != "emergency":
            for keyword in urgent_keywords:
                if keyword in text_upper or keyword in query_lower:
                    emergency_flags.append(keyword)
                    triage_level = "urgent"
                    break
        
        return triage_level, emergency_flags
    
    def _extract_next_steps(self, response_text: str) -> str:
        """Extract next steps from response"""
        
        if "Next steps:" in response_text:
            return response_text.split("Next steps:")[1].split("Medical disclaimer:")[0].strip()
        elif "next steps" in response_text.lower():
            parts = response_text.lower().split("next steps")
            if len(parts) > 1:
                return parts[1].split("medical disclaimer")[0].strip()
        
        return "Consult your healthcare provider for medical advice."
    
    def _calculate_confidence(self, 
                             response_text: str, 
                             search_results: List[SearchResult], 
                             citations: List[str]) -> float:
        """Calculate confidence score for the response"""
        
        base_confidence = 0.7
        
        # Boost for using multiple sources
        if len(citations) > 1:
            base_confidence += 0.1
        
        # Boost for citations
        if "[1]" in response_text:
            base_confidence += 0.1
        
        return min(0.95, base_confidence)
    
    def _create_fallback_response(self, query: str) -> RAGResponse:
        """Create emergency fallback response"""
        
        fallback_text = """
Based on the information you've provided, I'm evaluating your symptoms. 

For your safety, please:

🚨 If you have emergency symptoms (chest pain, severe headache, difficulty breathing, loss of consciousness), call 911 or go to the nearest emergency room immediately.

⚡ For urgent symptoms, contact your healthcare provider or visit urgent care today.

📋 For routine concerns, schedule an appointment with your primary care provider.

⚠️ This information is for educational purposes only and does not replace professional medical advice. Always consult your healthcare provider for medical decisions.
"""
        
        return RAGResponse(
            answer=fallback_text,
            citations=[],
            triage_level="unknown",
            next_steps="Consult your healthcare provider immediately",
            confidence=0.0,
            emergency_flags=[]
        )

class SimplifiedRAGPipeline:
    """Simplified RAG pipeline using REST APIs"""
    
    def __init__(self, project_id: str, search_location: str, generation_location: str, datastore_id: str):
        self.search_client = SimplifiedSearchClient(project_id, search_location, datastore_id)
        self.generation_client = SimplifiedGeminiClient(project_id, generation_location)
    
    def process_query(self, query: str, top_k: int = 5) -> RAGResponse:
        """Process medical query through simplified RAG pipeline"""
        
        logger.info(f"Processing medical query: {query}")
        
        # Step 1: Search clinical guidelines
        search_results = self.search_client.search(query, top_k)
        
        if not search_results:
            logger.warning("No clinical guidelines found for query")
            return self.generation_client._create_fallback_response(query)
        
        # Step 2: Generate response with medical context
        rag_response = self.generation_client.generate_response(query, search_results)
        
        logger.info(f"RAG processing complete. Triage: {rag_response.triage_level}, Citations: {len(rag_response.citations)}")
        return rag_response

# Flask webhook for simplified deployment
from flask import Flask, request, jsonify
from fhir_mock import (
    list_patients as fhir_list_patients,
    get_patient as fhir_get_patient,
    list_encounters as fhir_list_encounters,
    list_appointments as fhir_list_appointments,
    create_appointment as fhir_create_appointment,
)

app = Flask(__name__)

# Initialize simplified RAG pipeline
rag_pipeline = SimplifiedRAGPipeline(
    PROJECT_ID, 
    SEARCH_LOCATION, 
    LOCATION, 
    DATASTORE_ID
)


def _bundle(resources):
    """Wrap resources in a simple FHIR bundle structure."""
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "total": len(resources),
        "entry": [{"resource": resource} for resource in resources],
    }


@app.route("/fhir/patients", methods=["GET"])
def list_mock_patients():
    """Expose mock patient resources."""
    patients = fhir_list_patients()
    logger.info("HTTP GET /fhir/patients", extra={"component": "mock_fhir", "count": len(patients)})
    return jsonify(_bundle(patients))


@app.route("/fhir/encounters", methods=["GET"])
def list_mock_encounters():
    """Expose mock encounter resources."""
    patient_id = request.args.get("patient_id")
    encounters = fhir_list_encounters(patient_id)
    logger.info(
        "HTTP GET /fhir/encounters",
        extra={"component": "mock_fhir", "patient_id": patient_id or "*", "count": len(encounters)},
    )
    return jsonify(_bundle(encounters))


@app.route("/fhir/appointments", methods=["GET"])
def list_mock_appointments():
    """Expose mock appointment resources."""
    patient_id = request.args.get("patient_id")
    appointments = fhir_list_appointments(patient_id)
    logger.info(
        "HTTP GET /fhir/appointments",
        extra={"component": "mock_fhir", "patient_id": patient_id or "*", "count": len(appointments)},
    )
    return jsonify(_bundle(appointments))


@app.route("/fhir/appointments", methods=["POST"])
def create_mock_appointment():
    """Create a mock appointment via API."""
    payload = request.get_json(silent=True) or {}

    required_fields = ["patient_id", "appointment_type", "preferred_day", "preferred_time", "reason_summary"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        message = f"Missing required fields: {', '.join(missing)}"
        logger.warning(
            "HTTP POST /fhir/appointments failed",
            extra={"component": "mock_fhir", "missing": missing},
        )
        return jsonify({"error": message}), 400

    appointment = fhir_create_appointment(
        patient_id=payload["patient_id"],
        appointment_type=payload["appointment_type"],
        preferred_day=payload["preferred_day"],
        preferred_time=payload["preferred_time"],
        reason_summary=payload["reason_summary"],
        channel=payload.get("channel", "telehealth"),
    )

    logger.info(
        "HTTP POST /fhir/appointments success",
        extra={"component": "mock_fhir", "appointment_id": appointment["id"]},
    )
    return jsonify(appointment), 201


def _extract_session_parameters(req: Dict[str, Any]) -> Dict[str, Any]:
    """Extract session parameters from the Dialogflow CX webhook request."""
    session_info = req.get("sessionInfo") or {}
    return session_info.get("parameters") or {}


def _handle_missing_details(missing_fields: List[str]) -> Dict[str, Any]:
    """Generate a follow-up response when scheduling details are incomplete."""
    pretty_fields = ", ".join(missing_fields[:-1]) + (" and " if len(missing_fields) > 1 else "") + missing_fields[-1]
    prompt = (
        f"I want to schedule that for you, but I still need your {pretty_fields}. "
        "Could you share those details?"
    )
    return {
        "fulfillment_response": {
            "messages": [
                {"text": {"text": [prompt]}},
            ]
        }
    }


def handle_schedule_appointment(req: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the Schedule Appointment intent via the mock FHIR API."""
    parameters = _extract_session_parameters(req)

    patient_id = parameters.get("patient_id") or "patient-001"
    appointment_type = parameters.get("appointment_type") or "telehealth"
    preferred_day = parameters.get("preferred_day")
    preferred_time = parameters.get("preferred_time")
    channel = parameters.get("appointment_channel") or parameters.get("visit_mode") or "telehealth"
    symptom = parameters.get("symptom_type") or parameters.get("primary_complaint") or parameters.get("symptom")
    duration = parameters.get("duration")

    missing = [field for field in ["preferred_day", "preferred_time"] if not parameters.get(field)]
    if missing:
        return _handle_missing_details(missing)

    reason_parts = []
    if symptom:
        reason_parts.append(symptom)
    if duration:
        reason_parts.append(f"duration: {duration}")
    reason_summary = ", ".join(reason_parts) if reason_parts else "Symptom follow-up"

    appointment = fhir_create_appointment(
        patient_id=patient_id,
        appointment_type=appointment_type,
        preferred_day=preferred_day,
        preferred_time=preferred_time,
        reason_summary=reason_summary,
        channel=channel,
    )

    patient = fhir_get_patient(patient_id)
    encounters = fhir_list_encounters(patient_id)
    latest_encounter = encounters[0] if encounters else None

    confirmation_message = (
        f"I've scheduled a {channel} {appointment_type} visit for {preferred_day} at {preferred_time}. "
        "You'll receive a confirmation shortly."
    )

    follow_up_message = "I've noted your recent symptoms so the care team can prepare."
    if latest_encounter:
        follow_up_message = (
            f"I've also attached your recent encounter ({latest_encounter.get('reasonCode', [{'text': 'Recent visit'}])[0].get('text')}) "
            "for continuity of care."
        )

    logger.info(
        "Schedule Appointment webhook handled",
        extra={
            "component": "webhook",
            "operation": "schedule_appointment",
            "patient_id": patient_id,
            "appointment_id": appointment["id"],
            "channel": channel,
        },
    )

    session_parameters = {
        "appointment_id": appointment["id"],
        "appointment_status": appointment["status"],
        "appointment_day": preferred_day,
        "appointment_time": preferred_time,
        "appointment_channel": channel,
    }

    if patient:
        session_parameters["patient_name"] = patient["name"][0]["given"][0]

    return {
        "fulfillment_response": {
            "messages": [
                {"text": {"text": [confirmation_message]}},
                {"text": {"text": [follow_up_message]}},
            ]
        },
        "session_info": {
            "parameters": session_parameters,
        },
        "payload": {
            "fhirAppointment": appointment,
            "patient": patient,
            "latestEncounter": latest_encounter,
        },
    }

@app.route('/webhook', methods=['POST'])
def simplified_rag_webhook():
    """Simplified Dialogflow CX webhook with medical RAG"""
    
    try:
        # Get request data
        req = request.get_json()
        logger.info(f"Received medical query request")
        
        intent_display_name = (
            (req.get("intentInfo") or {}).get("displayName") or ""
        )
        fulfillment_tag = (req.get("fulfillmentInfo") or {}).get("tag") or ""

        if fulfillment_tag == "schedule_appointment" or intent_display_name.lower() == "schedule appointment":
            logger.info(
                "Routing to schedule appointment handler",
                extra={"component": "webhook", "intent": intent_display_name, "tag": fulfillment_tag},
            )
            response_payload = handle_schedule_appointment(req)
            return jsonify(response_payload)

        # Extract user query
        user_query = ""
        if "queryResult" in req and "queryText" in req["queryResult"]:
            user_query = req["queryResult"]["queryText"]
        elif "text" in req:
            user_query = req["text"]
        else:
            user_query = str(req.get("message", ""))
        
        if not user_query:
            user_query = "clinical guidelines help"
        
        logger.info(f"Processing: {user_query}")
        
        # Process through simplified RAG pipeline
        rag_response = rag_pipeline.process_query(user_query)
        
        # Format response for Dialogflow CX
        response_payload = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [rag_response.answer]
                        }
                    }
                ]
            },
            "payload": {
                "triage_level": rag_response.triage_level,
                "citations": rag_response.citations,
                "next_steps": rag_response.next_steps,
                "confidence": rag_response.confidence,
                "emergency_flags": rag_response.emergency_flags
            }
        }
        
        # Add emergency warning if needed
        if rag_response.triage_level == "emergency":
            emergency_message = {
                "text": {
                    "text": ["🚨 EMERGENCY: If you have these symptoms, call 911 or go to the nearest emergency room immediately!"]
                }
            }
            response_payload["fulfillment_response"]["messages"].insert(0, emergency_message)
        
        return jsonify(response_payload)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": ["Based on your symptoms, I'm providing general guidance. For specific medical advice, please consult your healthcare provider."]
                        }
                    }
                ]
            }
        }), 500

@app.route('/test', methods=['POST'])
def test_simplified_rag():
    """Test endpoint for simplified RAG pipeline"""
    
    try:
        data = request.get_json()
        query = data.get("query", "What are red flag headache symptoms?")
        
        # Process through simplified RAG pipeline
        rag_response = rag_pipeline.process_query(query)
        
        return jsonify({
            "query": query,
            "answer": rag_response.answer,
            "triage_level": rag_response.triage_level,
            "citations": rag_response.citations,
            "next_steps": rag_response.next_steps,
            "confidence": rag_response.confidence,
            "emergency_flags": rag_response.emergency_flags
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "simplified-rag-pipeline",
        "model": MODEL_NAME,
        "datastore": DATASTORE_ID
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
