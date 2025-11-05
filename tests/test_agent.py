#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Virtual Health Assistant
Runs automated tests against the Dialogflow CX agent
"""

import json
import os
import sys
from typing import Dict, List
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account
from google.api_core import client_options
from google.protobuf.json_format import MessageToDict

# Fix Windows encoding for console output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
SERVICE_ACCOUNT_KEY = "key.json"
AGENT_INFO_FILE = "agent_info.json"
TEST_SCENARIOS_FILE = "test_scenarios.json"

class AgentTester:
    """Test harness for Dialogflow CX agent"""
    
    def __init__(self):
        """Initialize the tester"""
        
        # Load credentials
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY
        )
        
        # Load agent info
        with open(AGENT_INFO_FILE, 'r') as f:
            agent_info = json.load(f)
            self.agent_name = agent_info['agent_name']
            self.project_id = agent_info['project_id']
            self.location = agent_info['location']
        
        # Initialize session client with correct endpoint for us-central1
        client_options_obj = client_options.ClientOptions(
            api_endpoint=f"{self.location}-dialogflow.googleapis.com:443"
        )
        self.sessions_client = dialogflow.SessionsClient(
            credentials=self.credentials,
            client_options=client_options_obj
        )
        
        # Get the default start flow
        self.flow_name = self._get_default_start_flow()
        
        # Generate session ID
        import uuid
        self.session_id = str(uuid.uuid4())
    
    def _get_default_start_flow(self):
        """Get the default start flow for the agent"""
        try:
            flows_client = dialogflow.FlowsClient(
                credentials=self.credentials,
                client_options=client_options.ClientOptions(
                    api_endpoint=f"{self.location}-dialogflow.googleapis.com:443"
                )
            )
            
            request = dialogflow.ListFlowsRequest(parent=self.agent_name)
            flows = flows_client.list_flows(request=request)
            
            for flow in flows:
                if flow.display_name == "Default Start Flow":
                    print(f"Using flow: {flow.display_name} ({flow.name})")
                    return flow.name
            
            # If no default start flow found, return None (will use agent-level sessions)
            print("Warning: Default Start Flow not found, using agent-level sessions")
            return None
        except Exception as e:
            print(f"Warning: Could not get flow: {e}")
            return None
        
    def create_session_path(self):
        """Create session path - sessions must be at agent level"""
        return f"{self.agent_name}/sessions/{self.session_id}"
    
    def detect_intent(self, text: str, language_code: str = "en") -> Dict:
        """Send text to agent and get response"""
        
        session_path = self.create_session_path()
        
        text_input = dialogflow.TextInput(text=text)
        query_input = dialogflow.QueryInput(
            text=text_input,
            language_code=language_code
        )
        
        # Sessions at agent level automatically use the default start flow
        request = dialogflow.DetectIntentRequest(
            session=session_path,
            query_input=query_input
        )
        
        response = self.sessions_client.detect_intent(request=request)
        
        # Extract response text
        response_text = ""
        if response.query_result.response_messages:
            response_text = response.query_result.response_messages[0].text.text[0] if response.query_result.response_messages[0].text.text else ""
        
        # Extract intent info
        intent_name = None
        if response.query_result.intent:
            intent_name = response.query_result.intent.display_name
        
        # Extract parameters
        parameters = {}
        if response.query_result.parameters:
            # Convert StructProto to dict
            try:
                if hasattr(response.query_result.parameters, '_pb'):
                    parameters = MessageToDict(response.query_result.parameters._pb)
                elif hasattr(response.query_result.parameters, 'fields'):
                    # Alternative extraction method
                    parameters = {k: v.string_value if hasattr(v, 'string_value') else str(v) 
                                 for k, v in response.query_result.parameters.fields.items()}
            except Exception as e:
                # Fallback: try to convert to dict directly
                parameters = dict(response.query_result.parameters) if hasattr(response.query_result.parameters, '__iter__') else {}
        
        # Extract page info
        page_name = None
        if response.query_result.current_page:
            page_name = response.query_result.current_page.display_name
        
        return {
            'response_text': response_text,
            'intent': intent_name,
            'match_confidence': response.query_result.intent_detection_confidence,
            'parameters': parameters,
            'current_page': page_name,
            'match_type': response.query_result.match.match_type if response.query_result.match else None,
        }
    
    def run_scenario(self, scenario: Dict) -> Dict:
        """Run a single test scenario"""
        
        print(f"\n{'='*60}")
        print(f"Test: {scenario['name']}")
        print(f"{'='*60}")
        print(f"Description: {scenario['description']}")
        print(f"Expected Triage: {scenario['expected_triage']}")
        print()
        
        results = {
            'scenario_id': scenario['scenario_id'],
            'name': scenario['name'],
            'passed': True,
            'turns': [],
            'errors': []
        }
        
        for i, turn in enumerate(scenario['conversation'], 1):
            user_input = turn['user']
            print(f"Turn {i}")
            print(f"  User: {user_input}")
            
            try:
                response = self.detect_intent(user_input)
                
                print(f"  Agent: {response['response_text']}")
                print(f"  Intent: {response['intent']} (confidence: {response['match_confidence']:.2f})")
                print(f"  Page: {response['current_page']}")
                print(f"  Match Type: {response.get('match_type', 'N/A')}")
                if response['parameters']:
                    print(f"  Parameters: {response['parameters']}")
                
                # Validate expected intent
                if 'expected_intent' in turn:
                    if response['intent'] != turn['expected_intent']:
                        error = f"Intent mismatch: expected {turn['expected_intent']}, got {response['intent']}"
                        print(f"  [FAIL] {error}")
                        results['errors'].append(error)
                        results['passed'] = False
                    else:
                        print(f"  [PASS] Intent matched")
                
                # Validate expected entities
                if 'expected_entities' in turn:
                    for key, value in turn['expected_entities'].items():
                        if key not in response['parameters']:
                            error = f"Missing parameter: {key}"
                            print(f"  [FAIL] {error}")
                            results['errors'].append(error)
                            results['passed'] = False
                        else:
                            print(f"  [PASS] Parameter {key} extracted")
                
                results['turns'].append({
                    'user_input': user_input,
                    'agent_response': response['response_text'],
                    'intent': response['intent'],
                    'confidence': response['match_confidence'],
                    'page': response['current_page']
                })
                
            except Exception as e:
                error = f"Error in turn {i}: {str(e)}"
                print(f"  [ERROR] {error}")
                results['errors'].append(error)
                results['passed'] = False
            
            print()
        
        return results
    
    def run_all_tests(self):
        """Run all test scenarios"""
        
        # Load test scenarios
        with open(TEST_SCENARIOS_FILE, 'r') as f:
            test_data = json.load(f)
        
        scenarios = test_data['test_scenarios']
        
        print("\n" + "="*60)
        print("Virtual Health Assistant - Automated Testing")
        print("="*60)
        print(f"Agent: {self.agent_name}")
        print(f"Session: {self.session_id}")
        print(f"Total scenarios: {len(scenarios)}")
        print("="*60)
        
        all_results = []
        
        for scenario in scenarios:
            # Reset session for each scenario
            import uuid
            self.session_id = str(uuid.uuid4())
            
            results = self.run_scenario(scenario)
            all_results.append(results)
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in all_results if r['passed'])
        failed = len(all_results) - passed
        
        print(f"Total tests: {len(all_results)}")
        print(f"Passed: {passed} [OK]")
        print(f"Failed: {failed} [FAIL]")
        print(f"Success rate: {passed/len(all_results)*100:.1f}%")
        
        if failed > 0:
            print("\nFailed tests:")
            for result in all_results:
                if not result['passed']:
                    print(f"  - {result['name']}")
                    for error in result['errors']:
                        print(f"    • {error}")
        
        # Save detailed results
        results_file = 'test_results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': len(all_results),
                    'passed': passed,
                    'failed': failed,
                    'success_rate': passed/len(all_results)
                },
                'results': all_results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")
        print("="*60)
        
        return all_results

def main():
    """Main execution"""
    
    # Check prerequisites
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"[ERROR] Service account key not found at {SERVICE_ACCOUNT_KEY}")
        return
    
    if not os.path.exists(AGENT_INFO_FILE):
        print(f"[ERROR] Agent info not found at {AGENT_INFO_FILE}")
        print("   Run create_agent.py first to create the agent")
        return
    
    if not os.path.exists(TEST_SCENARIOS_FILE):
        print(f"[ERROR] Test scenarios not found at {TEST_SCENARIOS_FILE}")
        return
    
    # Run tests
    tester = AgentTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

