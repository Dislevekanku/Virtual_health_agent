#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive testing script that records all outputs and generates a results table
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account
from google.api_core import client_options
from google.protobuf.json_format import MessageToDict

# Configuration
SERVICE_ACCOUNT_KEY = "key.json"
AGENT_INFO_FILE = "agent_info.json"
TEST_SCENARIOS_FILE = "test_scenarios.json"

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class ComprehensiveTester:
    """Comprehensive test harness with detailed documentation"""
    
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
        
        # Initialize session client
        client_options_obj = client_options.ClientOptions(
            api_endpoint=f"{self.location}-dialogflow.googleapis.com:443"
        )
        self.sessions_client = dialogflow.SessionsClient(
            credentials=self.credentials,
            client_options=client_options_obj
        )
        
        # Generate session ID
        import uuid
        self.session_id = str(uuid.uuid4())
    
    def create_session_path(self):
        """Create session path"""
        return f"{self.agent_name}/sessions/{self.session_id}"
    
    def detect_intent(self, text: str, language_code: str = "en") -> Dict:
        """Send text to agent and get response"""
        
        session_path = self.create_session_path()
        
        text_input = dialogflow.TextInput(text=text)
        query_input = dialogflow.QueryInput(
            text=text_input,
            language_code=language_code
        )
        
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
            try:
                if hasattr(response.query_result.parameters, '_pb'):
                    parameters = MessageToDict(response.query_result.parameters._pb)
                elif hasattr(response.query_result.parameters, 'fields'):
                    parameters = {}
                    for k, v in response.query_result.parameters.fields.items():
                        if hasattr(v, 'string_value'):
                            parameters[k] = v.string_value
                        elif hasattr(v, 'number_value'):
                            parameters[k] = v.number_value
                        else:
                            parameters[k] = str(v)
            except:
                parameters = {}
        
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
    
    def test_scenario(self, scenario: Dict) -> Dict:
        """Test a single scenario and return detailed results"""
        
        # Reset session for each scenario
        import uuid
        self.session_id = str(uuid.uuid4())
        
        results = {
            'scenario_id': scenario['scenario_id'],
            'name': scenario['name'],
            'description': scenario['description'],
            'expected_triage': scenario['expected_triage'],
            'turns': [],
            'final_parameters': {},
            'final_triage': None,
            'final_recommendation': None,
            'passed': True,
            'errors': []
        }
        
        for i, turn in enumerate(scenario['conversation'], 1):
            user_input = turn['user']
            
            try:
                response = self.detect_intent(user_input)
                
                # Store turn results
                turn_result = {
                    'turn_number': i,
                    'user_input': user_input,
                    'agent_response': response['response_text'],
                    'intent': response['intent'],
                    'confidence': response['match_confidence'],
                    'page': response['current_page'],
                    'parameters': response['parameters']
                }
                results['turns'].append(turn_result)
                
                # Update final parameters
                results['final_parameters'].update(response['parameters'])
                
                # Check for expected intent
                if 'expected_intent' in turn:
                    if response['intent'] != turn['expected_intent']:
                        error = f"Turn {i}: Expected intent '{turn['expected_intent']}', got '{response['intent']}'"
                        results['errors'].append(error)
                        results['passed'] = False
                
                # Check for expected entities
                if 'expected_entities' in turn:
                    for key, expected_value in turn['expected_entities'].items():
                        if key not in response['parameters']:
                            error = f"Turn {i}: Missing parameter '{key}'"
                            results['errors'].append(error)
                            results['passed'] = False
                
            except Exception as e:
                error = f"Turn {i}: Error - {str(e)}"
                results['errors'].append(error)
                results['passed'] = False
        
        # Extract final triage and recommendation
        results['final_triage'] = results['final_parameters'].get('triage', None)
        results['final_recommendation'] = results['final_parameters'].get('recommendation', None)
        
        # Check if triage matches expected
        if scenario['expected_triage'] != 'n/a':
            if results['final_triage'] != scenario['expected_triage']:
                error = f"Triage mismatch: expected '{scenario['expected_triage']}', got '{results['final_triage']}'"
                results['errors'].append(error)
                results['passed'] = False
        
        return results
    
    def run_all_tests(self):
        """Run all test scenarios and generate documentation"""
        
        # Load test scenarios
        with open(TEST_SCENARIOS_FILE, 'r') as f:
            test_data = json.load(f)
        
        scenarios = test_data['test_scenarios']
        
        print("="*60)
        print("Comprehensive Testing - Virtual Health Assistant")
        print("="*60)
        print(f"Agent: {self.agent_name}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total scenarios: {len(scenarios)}")
        print("="*60)
        print()
        
        all_results = []
        
        for scenario in scenarios:
            print(f"Testing: {scenario['name']}...")
            results = self.test_scenario(scenario)
            all_results.append(results)
            
            status = "[PASS]" if results['passed'] else "[FAIL]"
            print(f"  {status} {scenario['name']}")
            if not results['passed']:
                for error in results['errors']:
                    print(f"    - {error}")
            print()
        
        # Generate summary
        passed = sum(1 for r in all_results if r['passed'])
        failed = len(all_results) - passed
        success_rate = (passed / len(all_results) * 100) if all_results else 0
        
        print("="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total tests: {len(all_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {success_rate:.1f}%")
        print()
        
        # Generate results table
        self.generate_results_table(all_results)
        
        # Save detailed results
        results_file = 'comprehensive_test_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'agent_name': self.agent_name,
                'summary': {
                    'total': len(all_results),
                    'passed': passed,
                    'failed': failed,
                    'success_rate': success_rate
                },
                'results': all_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Detailed results saved to: {results_file}")
        print()
        
        return all_results
    
    def generate_results_table(self, results: List[Dict]):
        """Generate a markdown table of test results"""
        
        table_lines = [
            "## Test Results Table",
            "",
            "| Scenario ID | Input | Intent Recognized | Triage Level | Recommendation | Status |",
            "|-------------|-------|-------------------|--------------|----------------|--------|"
        ]
        
        for result in results:
            scenario_id = result['scenario_id']
            name = result['name']
            
            # Get first user input
            first_input = result['turns'][0]['user_input'] if result['turns'] else "N/A"
            
            # Get intent from first turn
            intent = result['turns'][0]['intent'] if result['turns'] and result['turns'][0]['intent'] else "None"
            
            # Get final triage
            triage = result['final_triage'] or "Not set"
            expected_triage = result['expected_triage']
            triage_display = f"{triage} (expected: {expected_triage})"
            
            # Get recommendation
            recommendation = result['final_recommendation'] or "Not provided"
            if len(recommendation) > 50:
                recommendation = recommendation[:47] + "..."
            
            # Status
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            
            table_lines.append(
                f"| {scenario_id} | {first_input[:50]} | {intent} | {triage_display} | {recommendation} | {status} |"
            )
        
        # Write table to file
        table_file = 'TEST_RESULTS_TABLE.md'
        with open(table_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(table_lines))
            f.write('\n\n')
            f.write('## Detailed Results\n\n')
            
            for result in results:
                f.write(f"### {result['name']} ({result['scenario_id']})\n\n")
                f.write(f"**Description:** {result['description']}\n\n")
                f.write(f"**Expected Triage:** {result['expected_triage']}\n\n")
                
                if result['turns']:
                    f.write("**Conversation Flow:**\n\n")
                    for turn in result['turns']:
                        f.write(f"**Turn {turn['turn_number']}:**\n")
                        f.write(f"- User: {turn['user_input']}\n")
                        f.write(f"- Agent: {turn['agent_response'][:200]}...\n")
                        f.write(f"- Intent: {turn['intent']} (confidence: {turn['confidence']:.2f})\n")
                        f.write(f"- Page: {turn['page']}\n")
                        if turn['parameters']:
                            f.write(f"- Parameters: {json.dumps(turn['parameters'], indent=2)}\n")
                        f.write("\n")
                
                f.write(f"**Final Triage:** {result['final_triage']}\n\n")
                f.write(f"**Final Recommendation:** {result['final_recommendation']}\n\n")
                f.write(f"**Status:** {'✅ PASSED' if result['passed'] else '❌ FAILED'}\n\n")
                
                if result['errors']:
                    f.write("**Errors:**\n")
                    for error in result['errors']:
                        f.write(f"- {error}\n")
                    f.write("\n")
                
                f.write("---\n\n")
        
        print(f"Results table saved to: {table_file}")
        print()

def main():
    """Main execution"""
    
    # Check prerequisites
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"[ERROR] Service account key not found at {SERVICE_ACCOUNT_KEY}")
        return
    
    if not os.path.exists(AGENT_INFO_FILE):
        print(f"[ERROR] Agent info not found at {AGENT_INFO_FILE}")
        return
    
    if not os.path.exists(TEST_SCENARIOS_FILE):
        print(f"[ERROR] Test scenarios not found at {TEST_SCENARIOS_FILE}")
        return
    
    # Run comprehensive tests
    tester = ComprehensiveTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

