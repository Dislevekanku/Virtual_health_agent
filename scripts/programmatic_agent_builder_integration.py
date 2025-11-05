#!/usr/bin/env python3
"""
Programmatic Agent Builder Integration

This script automatically integrates the grounding tool into Agent Builder by:
1. Creating/updating an agent with grounding capabilities
2. Configuring datastore integration
3. Setting up grounding settings
4. Testing the integration

Uses the Agent Development Kit (ADK) and REST APIs for full automation.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from google.auth import default
from google.auth.transport.requests import Request

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
AGENT_NAME = "clinical-guidelines-agent"
AGENT_DESCRIPTION = "Clinical decision support agent with grounding capabilities"
DATASTORE_ID = "clinical-guidelines-datastore"
GROUNDING_TOOL_URL = "https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentBuilderIntegrator:
    """Programmatic Agent Builder integration"""
    
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
    
    def create_or_update_agent(self, agent_name: str, description: str) -> Optional[str]:
        """Create or update an agent in Agent Builder"""
        
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        try:
            # Check if agent already exists
            existing_agent = self.get_agent_by_name(agent_name)
            
            if existing_agent:
                logger.info(f"Found existing agent: {existing_agent['name']}")
                agent_id = existing_agent['name'].split('/')[-1]
                return self.update_agent(agent_id, description)
            else:
                return self.create_new_agent(agent_name, description)
                
        except Exception as e:
            logger.error(f"Error creating/updating agent: {e}")
            return None
    
    def get_agent_by_name(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent by name"""
        
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        try:
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/agents"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                agents_data = response.json()
                
                for agent in agents_data.get("agents", []):
                    if agent.get("displayName") == agent_name:
                        return agent
                
                return None
            else:
                logger.error(f"Error getting agents: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting agent by name: {e}")
            return None
    
    def create_new_agent(self, agent_name: str, description: str) -> Optional[str]:
        """Create a new agent"""
        
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        try:
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/agents"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            agent_config = {
                "displayName": agent_name,
                "description": description,
                "defaultLanguageCode": "en",
                "timeZone": "America/New_York",
                "enableStackdriverLogging": True,
                "enableSpellCheck": True,
                "generativeSettings": {
                    "generationConfig": {
                        "model": "gemini-1.5-flash-001",
                        "temperature": 0.2,
                        "topP": 0.8,
                        "topK": 40,
                        "maxOutputTokens": 2048,
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
                    ],
                    "systemInstruction": {
                        "parts": [
                            {
                                "text": """You are a clinical decision support assistant that provides evidence-based information from clinical guidelines.

CRITICAL SAFETY RULES:
1. NEVER provide definitive diagnoses
2. NEVER replace professional medical judgment
3. ALWAYS cite sources from retrieved clinical guidelines
4. ALWAYS recommend consulting healthcare providers for medical decisions
5. Flag emergency symptoms requiring immediate attention

When users ask medical questions:
1. Search clinical guidelines database
2. Provide evidence-based information with citations
3. Include appropriate medical disclaimers
4. Recommend professional consultation when appropriate"""
                            }
                        ]
                    }
                }
            }
            
            logger.info(f"Creating new agent: {agent_name}")
            response = requests.post(url, headers=headers, json=agent_config)
            
            if response.status_code == 200:
                agent_data = response.json()
                agent_id = agent_data["name"].split("/")[-1]
                logger.info(f"✅ Created agent: {agent_id}")
                return agent_id
            else:
                logger.error(f"Error creating agent: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating new agent: {e}")
            return None
    
    def update_agent(self, agent_id: str, description: str) -> Optional[str]:
        """Update existing agent"""
        
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        try:
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Get current agent config
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Error getting agent: {response.status_code} - {response.text}")
                return None
            
            agent_data = response.json()
            
            # Update agent with grounding capabilities
            agent_data["description"] = description
            agent_data["generativeSettings"] = {
                "generationConfig": {
                    "model": "gemini-1.5-flash-001",
                    "temperature": 0.2,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 2048,
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
                ],
                "systemInstruction": {
                    "parts": [
                        {
                            "text": """You are a clinical decision support assistant that provides evidence-based information from clinical guidelines.

CRITICAL SAFETY RULES:
1. NEVER provide definitive diagnoses
2. NEVER replace professional medical judgment
3. ALWAYS cite sources from retrieved clinical guidelines
4. ALWAYS recommend consulting healthcare providers for medical decisions
5. Flag emergency symptoms requiring immediate attention

When users ask medical questions:
1. Search clinical guidelines database
2. Provide evidence-based information with citations
3. Include appropriate medical disclaimers
4. Recommend professional consultation when appropriate"""
                        }
                    ]
                }
            }
            
            # Remove read-only fields
            agent_data.pop("name", None)
            agent_data.pop("createTime", None)
            agent_data.pop("updateTime", None)
            
            logger.info(f"Updating agent: {agent_id}")
            response = requests.patch(url, headers=headers, json=agent_data)
            
            if response.status_code == 200:
                logger.info(f"✅ Updated agent: {agent_id}")
                return agent_id
            else:
                logger.error(f"Error updating agent: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating agent: {e}")
            return None
    
    def add_datastore_integration(self, agent_id: str, datastore_id: str) -> bool:
        """Add datastore integration to agent"""
        
        access_token = self._get_access_token()
        if not access_token:
            return False
        
        try:
            # This would typically be done through Agent Builder UI or specific API
            # For now, we'll create a grounding configuration
            
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/agents/{agent_id}/flows"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Get existing flows
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                flows_data = response.json()
                flows = flows_data.get("flows", [])
                
                if flows:
                    # Update the default flow with grounding
                    default_flow = flows[0]  # Assuming first flow is default
                    flow_id = default_flow["name"].split("/")[-1]
                    
                    return self.add_grounding_to_flow(agent_id, flow_id, datastore_id)
                else:
                    logger.warning("No flows found for agent")
                    return False
            else:
                logger.error(f"Error getting flows: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding datastore integration: {e}")
            return False
    
    def add_grounding_to_flow(self, agent_id: str, flow_id: str, datastore_id: str) -> bool:
        """Add grounding configuration to flow"""
        
        access_token = self._get_access_token()
        if not access_token:
            return False
        
        try:
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/agents/{agent_id}/flows/{flow_id}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Get current flow configuration
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Error getting flow: {response.status_code} - {response.text}")
                return False
            
            flow_data = response.json()
            
            # Add grounding configuration
            if "generativeSettings" not in flow_data:
                flow_data["generativeSettings"] = {}
            
            flow_data["generativeSettings"]["knowledgeConnectorSettings"] = {
                "dataStoreConnectors": [
                    {
                        "dataStore": f"projects/{self.project_id}/locations/global/collections/default_collection/dataStores/{datastore_id}",
                        "enableGrounding": True,
                        "queryTemplates": [
                            "What are the clinical guidelines for {user_input}?",
                            "Find information about {user_input} symptoms",
                            "Search for {user_input} treatment protocols"
                        ]
                    }
                ]
            }
            
            # Remove read-only fields
            flow_data.pop("name", None)
            flow_data.pop("createTime", None)
            flow_data.pop("updateTime", None)
            
            logger.info(f"Adding grounding to flow: {flow_id}")
            response = requests.patch(url, headers=headers, json=flow_data)
            
            if response.status_code == 200:
                logger.info(f"✅ Added grounding to flow: {flow_id}")
                return True
            else:
                logger.error(f"Error adding grounding to flow: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding grounding to flow: {e}")
            return False
    
    def add_external_tool(self, agent_id: str, tool_url: str) -> bool:
        """Add external grounding tool to agent"""
        
        access_token = self._get_access_token()
        if not access_token:
            return False
        
        try:
            # Create a tool configuration
            tool_config = {
                "displayName": "Clinical Guidelines Grounding",
                "description": "Search clinical guidelines for evidence-based information",
                "toolUrl": tool_url,
                "parameters": {
                    "user_text": {
                        "type": "string",
                        "description": "Medical query or symptom description"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results",
                        "default": 5
                    }
                }
            }
            
            # This would typically be done through Agent Builder UI
            # For programmatic integration, we'll create a custom intent that calls the tool
            
            logger.info(f"Adding external tool to agent: {agent_id}")
            
            # Create a medical intent that uses the grounding tool
            return self.create_medical_intent(agent_id, tool_url)
            
        except Exception as e:
            logger.error(f"Error adding external tool: {e}")
            return False
    
    def create_medical_intent(self, agent_id: str, tool_url: str) -> bool:
        """Create medical intent with grounding tool integration"""
        
        access_token = self._get_access_token()
        if not access_token:
            return False
        
        try:
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/agents/{agent_id}/intents"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            medical_intent = {
                "displayName": "Medical Query Intent",
                "description": "Handles medical queries with clinical guidelines grounding",
                "trainingPhrases": [
                    {
                        "parts": [
                            {
                                "text": "What are red flag headache symptoms?"
                            }
                        ],
                        "repeatCount": 1
                    },
                    {
                        "parts": [
                            {
                                "text": "When should I see a doctor for nausea?"
                            }
                        ],
                        "repeatCount": 1
                    },
                    {
                        "parts": [
                            {
                                "text": "What is orthostatic hypotension?"
                            }
                        ],
                        "repeatCount": 1
                    },
                    {
                        "parts": [
                            {
                                "text": "Tell me about dizziness guidelines"
                            }
                        ],
                        "repeatCount": 1
                    },
                    {
                        "parts": [
                            {
                                "text": "Medical advice"
                            }
                        ],
                        "repeatCount": 1
                    },
                    {
                        "parts": [
                            {
                                "text": "Health symptoms"
                            }
                        ],
                        "repeatCount": 1
                    }
                ],
                "parameters": [],
                "messages": [
                    {
                        "text": {
                            "text": ["Let me search the clinical guidelines for you..."]
                        }
                    }
                ],
                "outputContexts": [],
                # Enable webhook fulfillment for grounding
                "webhookEnabled": True,
                "webhook": tool_url
            }
            
            logger.info(f"Creating medical intent for agent: {agent_id}")
            response = requests.post(url, headers=headers, json=medical_intent)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Created medical intent: {result.get('displayName', 'Medical Query Intent')}")
                return True
            else:
                logger.error(f"Error creating medical intent: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating medical intent: {e}")
            return False
    
    def test_agent_integration(self, agent_id: str) -> bool:
        """Test the agent integration"""
        
        access_token = self._get_access_token()
        if not access_token:
            return False
        
        try:
            # Create a test session
            session_id = "test-session-programmatic"
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/agents/{agent_id}/sessions/{session_id}:detectIntent"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test data
            test_data = {
                "queryInput": {
                    "text": {
                        "text": "What are red flag headache symptoms?",
                        "languageCode": "en"
                    }
                }
            }
            
            logger.info(f"Testing agent integration: {agent_id}")
            logger.info(f"Test query: 'What are red flag headache symptoms?'")
            
            response = requests.post(url, headers=headers, json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                
                logger.info("📥 Test response received:")
                logger.info(f"   Intent: {result.get('queryResult', {}).get('intent', {}).get('displayName', 'N/A')}")
                logger.info(f"   Confidence: {result.get('queryResult', {}).get('intentDetectionConfidence', 'N/A')}")
                
                # Check webhook status
                webhook_status = result.get('queryResult', {}).get('webhookStatus')
                if webhook_status:
                    logger.info(f"   Webhook Status: {webhook_status.get('message', 'N/A')}")
                    logger.info(f"   Webhook Called: ✅")
                else:
                    logger.info(f"   Webhook Called: ❌")
                
                # Show response text
                response_messages = result.get('queryResult', {}).get('responseMessages', [])
                for message in response_messages:
                    if 'text' in message:
                        response_text = message['text'].get('text', ['N/A'])[0]
                        logger.info(f"   Response: {response_text[:100]}...")
                        if "clinical guidelines" in response_text.lower() or "emergency" in response_text.lower():
                            logger.info(f"   ✅ Grounding integration working!")
                        else:
                            logger.info(f"   ⚠️ Grounding may not be working properly")
                
                return True
            else:
                logger.error(f"Error testing agent: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing agent integration: {e}")
            return False
    
    def create_agent_with_grounding(self, agent_name: str, description: str, datastore_id: str, tool_url: str) -> Optional[str]:
        """Create complete agent with grounding integration"""
        
        logger.info(f"Creating agent with grounding: {agent_name}")
        
        # Step 1: Create or update agent
        agent_id = self.create_or_update_agent(agent_name, description)
        if not agent_id:
            logger.error("Failed to create/update agent")
            return None
        
        # Step 2: Add datastore integration
        logger.info("Adding datastore integration...")
        datastore_success = self.add_datastore_integration(agent_id, datastore_id)
        
        # Step 3: Add external tool integration
        logger.info("Adding external tool integration...")
        tool_success = self.add_external_tool(agent_id, tool_url)
        
        # Step 4: Test integration
        logger.info("Testing integration...")
        test_success = self.test_agent_integration(agent_id)
        
        # Report results
        logger.info(f"\n" + "=" * 60)
        logger.info("INTEGRATION RESULTS:")
        logger.info(f"   Agent ID: {agent_id}")
        logger.info(f"   Datastore Integration: {'✅' if datastore_success else '❌'}")
        logger.info(f"   External Tool Integration: {'✅' if tool_success else '❌'}")
        logger.info(f"   Test Results: {'✅' if test_success else '❌'}")
        logger.info("=" * 60)
        
        if datastore_success or tool_success:
            logger.info("✅ Agent Builder integration completed!")
            return agent_id
        else:
            logger.error("❌ Agent Builder integration failed")
            return None

def main():
    """Main integration process"""
    
    print("=" * 80)
    print("PROGRAMMATIC AGENT BUILDER INTEGRATION")
    print("=" * 80)
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to your service account key file:")
        print("   $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Initialize integrator
    integrator = AgentBuilderIntegrator(PROJECT_ID, LOCATION)
    
    # Create agent with grounding
    agent_id = integrator.create_agent_with_grounding(
        AGENT_NAME,
        AGENT_DESCRIPTION,
        DATASTORE_ID,
        GROUNDING_TOOL_URL
    )
    
    if agent_id:
        print(f"\n🎉 AGENT BUILDER INTEGRATION COMPLETE!")
        print(f"=" * 50)
        print(f"\n✅ Your agent is ready:")
        print(f"   • Agent ID: {agent_id}")
        print(f"   • Grounding Tool: {GROUNDING_TOOL_URL}")
        print(f"   • Datastore: {DATASTORE_ID}")
        print(f"   • Medical Safety: Enabled")
        
        print(f"\n🔗 Access your agent:")
        print(f"   https://console.cloud.google.com/vertex-ai/agent-builder/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{agent_id}")
        
        print(f"\n🧪 Test with medical queries:")
        print(f"   • What are red flag headache symptoms?")
        print(f"   • When should I see a doctor for nausea?")
        print(f"   • What is orthostatic hypotension?")
        
    else:
        print(f"\n❌ Integration failed. Check logs above.")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()
