#!/usr/bin/env python3
"""
Production RAG Implementation with Real Gemini API

This implements the complete RAG flow with actual Gemini API calls:
1. Query Vertex AI Search for clinical guidelines
2. Build grounded prompt with retrieved context
3. Call Gemini 1.5 Flash with retrieved context
4. Return evidence-based response with citations

Ready for deployment as Cloud Function or Agent Builder tool.
"""

import os
import json
import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google.cloud import discoveryengine_v1 as discoveryengine
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.auth import default

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"  # For Vertex AI
SEARCH_LOCATION = "global"  # For Vertex AI Search
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
    metadata: Dict[str, Any] = None

@dataclass
class RAGResponse:
    """RAG response with citations and recommendations"""
    answer: str
    citations: List[str]
    triage_level: str  # emergency, urgent, routine
    next_steps: str
    confidence: float
    sources_used: List[int]
    emergency_flags: List[str]

class ProductionSearchClient:
    """Production Vertex AI Search client"""
    
    def __init__(self, project_id: str, location: str, datastore_id: str):
        self.project_id = project_id
        self.location = location
        self.datastore_id = datastore_id
        self.client = discoveryengine.SearchServiceClient()
        
        # Construct serving config
        self.serving_config = (
            f"projects/{project_id}/locations/{location}/collections/"
            f"default_collection/dataStores/{datastore_id}/servingConfigs/default_config"
        )
        
        # Emergency symptom keywords for triage
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
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search clinical guidelines with enhanced medical search"""
        
        try:
            logger.info(f"Searching clinical guidelines for: {query}")
            
            # Enhanced search request for medical content
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=top_k,
                content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                        max_snippet_count=3,
                        reference_only=False,
                        return_snippet=True,
                    ),
                    summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                        summary_result_count=top_k,
                        include_citations=True,
                        model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                            version="stable",
                        ),
                    ),
                    # Medical-specific search configuration
                    search_result_mode=discoveryengine.SearchRequest.ContentSearchSpec.SearchResultMode.DOCUMENTS,
                    max_extractive_answer_count=3,
                ),
                query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                    condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
                ),
                spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                    mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO,
                ),
            )
            
            # Execute search
            response = self.client.search(request)
            
            # Parse and rank results
            results = []
            for i, result in enumerate(response.results):
                doc = result.document.derived_struct_data
                
                snippet = doc.get("snippet", "")
                title = doc.get("title", "Clinical Guideline")
                source = doc.get("source", "Clinical Guidelines Database")
                
                # Extract document ID
                document_id = self._extract_document_id(title, snippet)
                
                # Calculate medical relevance score
                score = self._calculate_medical_relevance(query, snippet, i)
                
                search_result = SearchResult(
                    snippet=snippet,
                    title=title,
                    source=source,
                    document_id=document_id,
                    score=score,
                    metadata=doc
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
    
    def _calculate_medical_relevance(self, query: str, snippet: str, rank: int) -> float:
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

class ProductionGeminiClient:
    """Production Gemini client with medical safety"""
    
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize Gemini model
        self.model = GenerativeModel(MODEL_NAME)
        
        # Medical safety configuration
        self.safety_settings = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_MEDICAL": "BLOCK_ONLY_HIGH"
        }
    
    def generate_response(self, 
                         query: str, 
                         search_results: List[SearchResult]) -> RAGResponse:
        """Generate medical response using Gemini with retrieved context"""
        
        try:
            # Build grounded prompt
            context = self._build_medical_context(search_results)
            system_instruction = self._get_medical_system_instruction()
            prompt = self._build_grounded_prompt(query, context)
            
            logger.info(f"Generating response with {len(search_results)} sources")
            
            # Call Gemini with safety settings
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 500,
                    "candidate_count": 1,
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_MEDICAL",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ]
            )
            
            response_text = response.text
            
            # Parse and structure response
            rag_response = self._parse_medical_response(
                response_text, query, search_results
            )
            
            logger.info(f"Generated response with triage level: {rag_response.triage_level}")
            return rag_response
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return self._create_emergency_fallback_response(query)
    
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
    
    def _get_medical_system_instruction(self) -> str:
        """Get medical system instruction for Gemini"""
        
        return """You are a clinical decision support assistant that provides evidence-based information from clinical guidelines.

CRITICAL SAFETY RULES:
1. NEVER provide definitive diagnoses
2. NEVER replace professional medical judgment
3. ALWAYS base answers ONLY on the provided clinical guidelines context
4. ALWAYS cite source numbers [1], [2], etc.
5. ALWAYS include medical disclaimers
6. Flag emergency symptoms requiring immediate attention

RESPONSE FORMAT:
1. Brief, evidence-based answer from guidelines
2. Citations [1], [2], etc. for sources used
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

Always err on the side of caution for patient safety."""
    
    def _build_grounded_prompt(self, query: str, context: str) -> str:
        """Build grounded prompt for Gemini"""
        
        return f"""Based ONLY on the clinical guidelines context below, answer the user's medical question.

CLINICAL GUIDELINES CONTEXT:
{context}

USER QUESTION: "{query}"

REQUIRED RESPONSE FORMAT:
1. Brief answer based on clinical guidelines
2. Sources cited [1], [2], etc.
3. Triage level: EMERGENCY/URGENT/ROUTINE
4. Next steps recommendation
5. Medical disclaimer

ANSWER:"""
    
    def _parse_medical_response(self, 
                               response_text: str, 
                               query: str, 
                               search_results: List[SearchResult]) -> RAGResponse:
        """Parse Gemini response into structured medical format"""
        
        # Extract citations
        citations = []
        sources_used = []
        citation_matches = re.findall(r'\[(\d+)\]', response_text)
        
        for match in citation_matches:
            idx = int(match) - 1
            if 0 <= idx < len(search_results):
                citations.append(search_results[idx].document_id)
                sources_used.append(idx)
        
        # Determine triage level and emergency flags
        triage_level, emergency_flags = self._assess_triage_level(response_text, query)
        
        # Extract next steps
        next_steps = self._extract_next_steps(response_text)
        
        # Calculate confidence based on citations and context match
        confidence = self._calculate_confidence(response_text, search_results, sources_used)
        
        return RAGResponse(
            answer=response_text,
            citations=citations,
            triage_level=triage_level,
            next_steps=next_steps,
            confidence=confidence,
            sources_used=sources_used,
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
        
        # Look for next steps section
        if "Next steps:" in response_text:
            return response_text.split("Next steps:")[1].split("Medical disclaimer:")[0].strip()
        elif "next steps" in response_text.lower():
            # Try to extract after "next steps"
            parts = response_text.lower().split("next steps")
            if len(parts) > 1:
                return parts[1].split("medical disclaimer")[0].strip()
        
        # Default next steps
        return "Consult your healthcare provider for medical advice."
    
    def _calculate_confidence(self, 
                             response_text: str, 
                             search_results: List[SearchResult], 
                             sources_used: List[int]) -> float:
        """Calculate confidence score for the response"""
        
        base_confidence = 0.7
        
        # Boost for using multiple sources
        if len(sources_used) > 1:
            base_confidence += 0.1
        
        # Boost for high-quality sources
        if sources_used:
            avg_source_score = sum(search_results[i].score for i in sources_used) / len(sources_used)
            base_confidence += avg_source_score * 0.1
        
        # Boost for citations
        if "[1]" in response_text:
            base_confidence += 0.1
        
        return min(0.95, base_confidence)
    
    def _create_emergency_fallback_response(self, query: str) -> RAGResponse:
        """Create emergency fallback response"""
        
        fallback_text = """
I'm having trouble accessing the clinical guidelines database. 

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
            sources_used=[],
            emergency_flags=[]
        )

class ProductionRAGPipeline:
    """Production RAG pipeline with medical safety"""
    
    def __init__(self, project_id: str, search_location: str, generation_location: str, datastore_id: str):
        self.search_client = ProductionSearchClient(project_id, search_location, datastore_id)
        self.generation_client = ProductionGeminiClient(project_id, generation_location)
    
    def process_query(self, query: str, top_k: int = 5) -> RAGResponse:
        """Process medical query through production RAG pipeline"""
        
        logger.info(f"Processing medical query: {query}")
        
        # Step 1: Search clinical guidelines
        search_results = self.search_client.search(query, top_k)
        
        if not search_results:
            logger.warning("No clinical guidelines found for query")
            return self.generation_client._create_emergency_fallback_response(query)
        
        # Step 2: Generate response with medical context
        rag_response = self.generation_client.generate_response(query, search_results)
        
        logger.info(f"RAG processing complete. Triage: {rag_response.triage_level}, Citations: {len(rag_response.citations)}")
        return rag_response

# Flask webhook for production deployment
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize production RAG pipeline
rag_pipeline = ProductionRAGPipeline(
    PROJECT_ID, 
    SEARCH_LOCATION, 
    LOCATION, 
    DATASTORE_ID
)

@app.route('/webhook', methods=['POST'])
def production_rag_webhook():
    """Production Dialogflow CX webhook with medical RAG"""
    
    try:
        # Get request data
        req = request.get_json()
        logger.info(f"Received medical query request")
        
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
        
        # Process through production RAG pipeline
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
                "emergency_flags": rag_response.emergency_flags,
                "sources_used": rag_response.sources_used
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
                            "text": ["I'm having trouble accessing the clinical guidelines. Please consult your healthcare provider for medical advice."]
                        }
                    }
                ]
            }
        }), 500

@app.route('/test', methods=['POST'])
def test_production_rag():
    """Test endpoint for production RAG pipeline"""
    
    try:
        data = request.get_json()
        query = data.get("query", "What are red flag headache symptoms?")
        
        # Process through production RAG pipeline
        rag_response = rag_pipeline.process_query(query)
        
        return jsonify({
            "query": query,
            "answer": rag_response.answer,
            "triage_level": rag_response.triage_level,
            "citations": rag_response.citations,
            "next_steps": rag_response.next_steps,
            "confidence": rag_response.confidence,
            "emergency_flags": rag_response.emergency_flags,
            "sources_used": rag_response.sources_used
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "production-rag-pipeline",
        "model": MODEL_NAME,
        "datastore": DATASTORE_ID
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
