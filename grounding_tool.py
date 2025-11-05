#!/usr/bin/env python3
"""
Agent Builder Grounding Tool

This implements a custom grounding function that can be called by Agent Builder
as an external tool. It performs search + model generation for clinical guidelines.
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
class GroundingResponse:
    """Response from grounding tool"""
    answer: str
    citations: List[str]
    confidence: float
    sources_used: List[str]
    emergency_flags: List[str]

class ClinicalGroundingTool:
    """Clinical guidelines grounding tool for Agent Builder"""
    
    def __init__(self, project_id: str, search_location: str, generation_location: str, datastore_id: str):
        self.project_id = project_id
        self.search_location = search_location
        self.generation_location = generation_location
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
    
    def search_clinical_guidelines(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search clinical guidelines using Vertex AI Search"""
        
        access_token = self._get_access_token()
        if not access_token:
            return []
        
        try:
            logger.info(f"Searching clinical guidelines for: {query}")
            
            # Construct search URL
            url = f"https://discoveryengine.googleapis.com/v1/projects/{self.project_id}/locations/{self.search_location}/collections/default_collection/dataStores/{self.datastore_id}/servingConfigs/default_config:search"
            
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
                    "searchResultMode": "DOCUMENTS"
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
    
    def generate_with_context(self, query: str, search_results: List[SearchResult]) -> GroundingResponse:
        """Generate response using retrieved clinical guidelines"""
        
        access_token = self._get_access_token()
        if not access_token:
            return self._create_fallback_response(query)
        
        try:
            # Build grounded prompt
            context = self._build_medical_context(search_results)
            prompt = self._build_grounded_prompt(query, context)
            
            logger.info(f"Generating response with {len(search_results)} sources")
            
            # Call Gemini REST API
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.generation_location}/publishers/google/models/{MODEL_NAME}:generateContent"
            
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
            grounding_response = self._parse_grounding_response(response_text, query, search_results)
            
            logger.info(f"Generated grounding response with {len(grounding_response.citations)} citations")
            return grounding_response
            
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
3. Triage assessment: EMERGENCY/URGENT/ROUTINE
4. Clear next steps recommendation
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
    
    def _parse_grounding_response(self, 
                                response_text: str, 
                                query: str, 
                                search_results: List[SearchResult]) -> GroundingResponse:
        """Parse Gemini response into structured grounding format"""
        
        # Extract citations
        citations = []
        citation_matches = re.findall(r'\[(\d+)\]', response_text)
        
        for match in citation_matches:
            idx = int(match) - 1
            if 0 <= idx < len(search_results):
                citations.append(search_results[idx].document_id)
        
        # Determine emergency flags
        emergency_flags = []
        query_lower = query.lower()
        response_lower = response_text.lower()
        
        for keyword in self.emergency_keywords:
            if keyword in response_lower or keyword in query_lower:
                emergency_flags.append(keyword)
        
        # Calculate confidence
        confidence = self._calculate_confidence(response_text, search_results, citations)
        
        return GroundingResponse(
            answer=response_text,
            citations=citations,
            confidence=confidence,
            sources_used=citations,
            emergency_flags=emergency_flags
        )
    
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
    
    def _create_fallback_response(self, query: str) -> GroundingResponse:
        """Create emergency fallback response"""
        
        fallback_text = """
I'm having trouble accessing the clinical guidelines database. 

For your safety, please:

🚨 If you have emergency symptoms (chest pain, severe headache, difficulty breathing, loss of consciousness), call 911 or go to the nearest emergency room immediately.

⚡ For urgent symptoms, contact your healthcare provider or visit urgent care today.

📋 For routine concerns, schedule an appointment with your primary care provider.

⚠️ This information is for educational purposes only and does not replace professional medical advice. Always consult your healthcare provider for medical decisions.
"""
        
        return GroundingResponse(
            answer=fallback_text,
            citations=[],
            confidence=0.0,
            sources_used=[],
            emergency_flags=[]
        )

# Cloud Function entry point for Agent Builder
def ground_and_generate(request):
    """
    Main grounding function called by Agent Builder
    
    Expected input format:
    {
        "user_text": "What are red flag headache symptoms?",
        "max_results": 5
    }
    
    Returns:
    {
        "answer": "Response text with citations",
        "citations": ["OID-NEURO-HEAD-001", ...],
        "confidence": 0.85,
        "sources_used": ["OID-NEURO-HEAD-001", ...],
        "emergency_flags": ["thunderclap", ...]
    }
    """
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return {"error": "No data provided"}, 400
        
        user_text = data.get("user_text", "")
        max_results = data.get("max_results", 5)
        
        if not user_text:
            return {"error": "user_text is required"}, 400
        
        logger.info(f"Grounding request: {user_text}")
        
        # Initialize grounding tool
        grounding_tool = ClinicalGroundingTool(
            PROJECT_ID, 
            SEARCH_LOCATION, 
            LOCATION, 
            DATASTORE_ID
        )
        
        # Search clinical guidelines
        search_results = grounding_tool.search_clinical_guidelines(user_text, max_results)
        
        if not search_results:
            logger.warning("No clinical guidelines found for query")
            fallback_response = grounding_tool._create_fallback_response(user_text)
            return {
                "answer": fallback_response.answer,
                "citations": fallback_response.citations,
                "confidence": fallback_response.confidence,
                "sources_used": fallback_response.sources_used,
                "emergency_flags": fallback_response.emergency_flags
            }
        
        # Generate response with context
        grounding_response = grounding_tool.generate_with_context(user_text, search_results)
        
        # Return structured response
        return {
            "answer": grounding_response.answer,
            "citations": grounding_response.citations,
            "confidence": grounding_response.confidence,
            "sources_used": grounding_response.sources_used,
            "emergency_flags": grounding_response.emergency_flags
        }
        
    except Exception as e:
        logger.error(f"Grounding error: {e}")
        return {"error": str(e)}, 500

# Flask app for testing
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def test_grounding():
    """Test endpoint for grounding tool"""
    
    try:
        data = request.get_json()
        user_text = data.get("user_text", "What are red flag headache symptoms?")
        
        # Create test request
        test_request = type('Request', (), {'get_json': lambda: data})()
        
        # Call grounding function
        result = ground_and_generate(test_request)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "grounding-tool",
        "datastore": DATASTORE_ID
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
