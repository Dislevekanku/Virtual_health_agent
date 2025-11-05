#!/usr/bin/env python3
"""
RAG Implementation: Vertex AI Search + Generative Model

This implements the core RAG flow:
1. Query Vertex AI Search for clinical guidelines
2. Build grounded prompt with retrieved context
3. Call Gemini model with retrieved context
4. Return evidence-based response with citations

This can be used as:
- Cloud Function (webhook)
- Agent Builder tool
- Standalone service
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google.cloud import discoveryengine_v1 as discoveryengine
from google.cloud import aiplatform
from google.auth import default

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "global"
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

class VertexAISearchClient:
    """Client for querying Vertex AI Search"""
    
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
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search clinical guidelines for relevant information
        
        Args:
            query: User's medical question
            top_k: Number of results to retrieve
            
        Returns:
            List of SearchResult objects with snippets and metadata
        """
        
        try:
            logger.info(f"Searching for: {query}")
            
            # Create search request
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=top_k,
                # Enable snippets and metadata
                content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                        max_snippet_count=3,
                        reference_only=False,
                        return_snippet=True,
                    ),
                    # Enable summary for better context
                    summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                        summary_result_count=top_k,
                        include_citations=True,
                        model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                            version="stable",
                        ),
                    ),
                ),
                # Query expansion for better medical search
                query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                    condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
                ),
                # Spell correction
                spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                    mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO,
                ),
            )
            
            # Execute search
            response = self.client.search(request)
            
            # Parse results
            results = []
            for i, result in enumerate(response.results):
                doc = result.document.derived_struct_data
                
                # Extract information
                snippet = doc.get("snippet", "")
                title = doc.get("title", "Clinical Guideline")
                
                # Try to extract document ID
                document_id = self._extract_document_id(title, snippet)
                
                # Extract source information
                source = doc.get("source", "Clinical Guidelines Database")
                
                # Calculate relevance score (simplified)
                score = 1.0 - (i * 0.1)  # Simple ranking-based score
                
                search_result = SearchResult(
                    snippet=snippet,
                    title=title,
                    source=source,
                    document_id=document_id,
                    score=score,
                    metadata=doc
                )
                
                results.append(search_result)
                logger.info(f"Retrieved result {i+1}: {document_id}")
            
            logger.info(f"Retrieved {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _extract_document_id(self, title: str, snippet: str) -> str:
        """Extract document ID from title or snippet"""
        
        # Look for OID pattern in title first
        if "OID-" in title:
            import re
            oid_match = re.search(r'OID-[A-Z0-9-]+', title)
            if oid_match:
                return oid_match.group()
        
        # Look for OID pattern in snippet
        if "OID-" in snippet:
            import re
            oid_match = re.search(r'OID-[A-Z0-9-]+', snippet)
            if oid_match:
                return oid_match.group()
        
        # Fallback to truncated title
        return title[:20] + "..." if len(title) > 20 else title

class GeminiRAGClient:
    """Client for calling Gemini with RAG context"""
    
    def __init__(self, project_id: str, model_name: str = MODEL_NAME):
        self.project_id = project_id
        self.model_name = model_name
        
        # Initialize AI Platform
        aiplatform.init(project=project_id)
    
    def generate_response(self, 
                         query: str, 
                         search_results: List[SearchResult],
                         max_tokens: int = 300) -> RAGResponse:
        """
        Generate response using Gemini with retrieved context
        
        Args:
            query: User's medical question
            search_results: Retrieved clinical guidelines
            max_tokens: Maximum response length
            
        Returns:
            RAGResponse with answer, citations, and recommendations
        """
        
        try:
            # Build grounded prompt
            context = self._build_context(search_results)
            prompt = self._build_prompt(query, context, search_results)
            
            logger.info(f"Generated prompt length: {len(prompt)} characters")
            
            # Call Gemini model
            # Note: This is a simplified implementation
            # In production, use proper Vertex AI model serving
            response_text = self._call_gemini_model(prompt, max_tokens)
            
            # Parse response
            rag_response = self._parse_response(response_text, search_results)
            
            logger.info(f"Generated response with {len(rag_response.citations)} citations")
            return rag_response
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return self._create_fallback_response(query)
    
    def _build_context(self, search_results: List[SearchResult]) -> str:
        """Build context string from search results"""
        
        context_parts = []
        for i, result in enumerate(search_results, start=1):
            context_part = f"[{i}] {result.snippet}\nSource: {result.title} ({result.document_id})"
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, 
                     query: str, 
                     context: str, 
                     search_results: List[SearchResult]) -> str:
        """Build grounded prompt for Gemini"""
        
        # Medical safety instructions
        safety_instructions = """
CRITICAL SAFETY RULES:
1. NEVER provide definitive diagnoses
2. NEVER replace professional medical judgment  
3. ALWAYS base answers ONLY on the provided context
4. ALWAYS cite source numbers [1], [2], etc.
5. ALWAYS include medical disclaimers
6. Flag emergency symptoms requiring immediate attention

RESPONSE FORMAT:
- Brief, evidence-based answer
- Cite sources used [1], [2], etc.
- Include triage recommendation (emergency/urgent/routine)
- Include clear next steps
- Add medical disclaimer
"""
        
        prompt = f"""
{safety_instructions}

You are a clinical decision support assistant. You MUST base your answer ONLY on the clinical guidelines context provided below. Do NOT hallucinate or provide information not in the context.

CONTEXT (Clinical Guidelines):
{context}

USER QUESTION: "{query}"

REQUIRED RESPONSE FORMAT:
1. Brief answer based on guidelines
2. Citations [1], [2], etc. for sources used
3. Triage level: [EMERGENCY/URGENT/ROUTINE]
4. Next steps recommendation
5. Medical disclaimer

ANSWER:
"""
        
        return prompt
    
    def _call_gemini_model(self, prompt: str, max_tokens: int) -> str:
        """
        Call Gemini model with the prompt
        
        Note: This is a placeholder implementation
        In production, use proper Vertex AI model serving or REST API
        """
        
        # Placeholder implementation
        # In production, replace with actual Gemini API call
        
        # For now, return a structured response
        return """
Based on the clinical guidelines provided:

1. [Brief answer based on guidelines]

Sources used: [1], [2]

Triage level: ROUTINE

Next steps: Follow up with your primary care provider for further evaluation.

Medical disclaimer: This information is for educational purposes only and does not replace professional medical advice. Always consult your healthcare provider for medical decisions.
"""
    
    def _parse_response(self, response_text: str, search_results: List[SearchResult]) -> RAGResponse:
        """Parse Gemini response into structured format"""
        
        # Extract citations
        citations = []
        sources_used = []
        
        import re
        citation_matches = re.findall(r'\[(\d+)\]', response_text)
        for match in citation_matches:
            idx = int(match) - 1
            if 0 <= idx < len(search_results):
                citations.append(search_results[idx].document_id)
                sources_used.append(idx)
        
        # Determine triage level
        triage_level = "routine"
        if "EMERGENCY" in response_text.upper():
            triage_level = "emergency"
        elif "URGENT" in response_text.upper():
            triage_level = "urgent"
        
        # Extract next steps
        next_steps = "Consult your healthcare provider for medical advice."
        if "Next steps:" in response_text:
            next_steps = response_text.split("Next steps:")[1].split("Medical disclaimer:")[0].strip()
        
        return RAGResponse(
            answer=response_text,
            citations=citations,
            triage_level=triage_level,
            next_steps=next_steps,
            confidence=0.85,  # Placeholder
            sources_used=sources_used
        )
    
    def _create_fallback_response(self, query: str) -> RAGResponse:
        """Create fallback response when generation fails"""
        
        return RAGResponse(
            answer="I'm having trouble accessing the clinical guidelines. Please consult your healthcare provider for medical advice.",
            citations=[],
            triage_level="unknown",
            next_steps="Consult your healthcare provider",
            confidence=0.0,
            sources_used=[]
        )

class RAGPipeline:
    """Main RAG pipeline combining search and generation"""
    
    def __init__(self, project_id: str, location: str, datastore_id: str):
        self.search_client = VertexAISearchClient(project_id, location, datastore_id)
        self.generation_client = GeminiRAGClient(project_id)
    
    def process_query(self, query: str, top_k: int = 5) -> RAGResponse:
        """
        Process user query through RAG pipeline
        
        Args:
            query: User's medical question
            top_k: Number of search results to retrieve
            
        Returns:
            RAGResponse with evidence-based answer
        """
        
        logger.info(f"Processing query: {query}")
        
        # Step 1: Search clinical guidelines
        search_results = self.search_client.search(query, top_k)
        
        if not search_results:
            logger.warning("No search results found")
            return self.generation_client._create_fallback_response(query)
        
        # Step 2: Generate response with context
        rag_response = self.generation_client.generate_response(query, search_results)
        
        logger.info(f"RAG processing complete. Triage level: {rag_response.triage_level}")
        return rag_response

# Flask webhook implementation
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize RAG pipeline
rag_pipeline = RAGPipeline(PROJECT_ID, LOCATION, DATASTORE_ID)

@app.route('/webhook', methods=['POST'])
def rag_webhook():
    """Dialogflow CX webhook endpoint with RAG"""
    
    try:
        # Get request data
        req = request.get_json()
        logger.info(f"Received request: {json.dumps(req, indent=2)}")
        
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
        
        logger.info(f"Processing query: {user_query}")
        
        # Process through RAG pipeline
        rag_response = rag_pipeline.process_query(user_query)
        
        # Format response for Dialogflow CX
        return jsonify({
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
                "sources_used": rag_response.sources_used
            }
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
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

@app.route('/test', methods=['POST'])
def test_rag():
    """Test endpoint for RAG pipeline"""
    
    try:
        data = request.get_json()
        query = data.get("query", "What are red flag headache symptoms?")
        
        # Process through RAG pipeline
        rag_response = rag_pipeline.process_query(query)
        
        return jsonify({
            "query": query,
            "answer": rag_response.answer,
            "triage_level": rag_response.triage_level,
            "citations": rag_response.citations,
            "next_steps": rag_response.next_steps,
            "confidence": rag_response.confidence
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "rag-pipeline"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
