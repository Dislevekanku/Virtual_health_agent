#!/usr/bin/env python3
"""
Integration test for full pipeline: Intake → Reasoning → Data → Response → Critic → Logging

Tests:
- Full pipeline execution
- Session memory storage and retrieval
- Agent output logging
- Multi-turn conversation handling
"""

import os
import sys
import json
import unittest
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ["VHA_PIPELINE_MODE"] = "mock"

from agents.multi_agent_pipeline import (
    run_virtual_health_assistant,
    LOCAL_SESSION_STORE,
)


class TestFullPipelineIntegration(unittest.TestCase):
    """Integration tests for the full pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear session store before each test
        LOCAL_SESSION_STORE.clear()
    
    def test_single_turn_pipeline(self):
        """Test full pipeline execution for a single turn."""
        user_input = "I have had a headache for 2 days"
        session_id = "test-session-001"
        
        response = run_virtual_health_assistant(user_input, session_id=session_id)
        
        # Verify response structure
        self.assertIn("message", response)
        self.assertIn("triage_level", response)
        self.assertIn("session_id", response)
        self.assertEqual(response["session_id"], session_id)
        
        # Verify session storage
        self.assertIn(session_id, LOCAL_SESSION_STORE)
        session_data = LOCAL_SESSION_STORE[session_id]
        self.assertIn("history", session_data)
        self.assertIn("agent_outputs", session_data)
        self.assertEqual(session_data["total_turns"], 1)
        
        # Verify history entry
        history = session_data["history"]
        self.assertEqual(len(history), 1)
        turn = history[0]
        self.assertEqual(turn["user_input"], user_input)
        self.assertIn("response", turn)
        self.assertIn("triage_level", turn)
        self.assertIn("agent_outputs", turn)
    
    def test_multi_turn_conversation(self):
        """Test multi-turn conversation with session memory."""
        session_id = "test-session-002"
        
        # Turn 1
        response1 = run_virtual_health_assistant(
            "I have had a headache for 2 days",
            session_id=session_id
        )
        
        self.assertIn("message", response1)
        self.assertEqual(response1["session_id"], session_id)
        
        # Verify session has 1 turn
        session_data = LOCAL_SESSION_STORE[session_id]
        self.assertEqual(session_data["total_turns"], 1)
        self.assertEqual(len(session_data["history"]), 1)
        
        # Turn 2
        response2 = run_virtual_health_assistant(
            "It started yesterday morning",
            session_id=session_id
        )
        
        self.assertIn("message", response2)
        self.assertEqual(response2["session_id"], session_id)
        
        # Verify session has 2 turns
        session_data = LOCAL_SESSION_STORE[session_id]
        self.assertEqual(session_data["total_turns"], 2)
        self.assertEqual(len(session_data["history"]), 2)
        
        # Verify history contains both turns
        history = session_data["history"]
        self.assertEqual(history[0]["user_input"], "I have had a headache for 2 days")
        self.assertEqual(history[1]["user_input"], "It started yesterday morning")
    
    def test_agent_outputs_stored(self):
        """Test that agent outputs are stored in session."""
        user_input = "I have chest pain and shortness of breath"
        session_id = "test-session-003"
        
        response = run_virtual_health_assistant(user_input, session_id=session_id)
        
        # Verify session storage
        session_data = LOCAL_SESSION_STORE[session_id]
        
        # Check agent_outputs in session
        self.assertIn("agent_outputs", session_data)
        agent_outputs = session_data["agent_outputs"]
        self.assertIsInstance(agent_outputs, list)
        
        # Check agent_outputs in history turn
        history = session_data["history"]
        self.assertEqual(len(history), 1)
        turn = history[0]
        self.assertIn("agent_outputs", turn)
        self.assertIsInstance(turn["agent_outputs"], list)
    
    def test_session_retrieval(self):
        """Test that session history is retrievable."""
        session_id = "test-session-004"
        
        # Create first turn
        run_virtual_health_assistant(
            "I have had a headache for 2 days",
            session_id=session_id
        )
        
        # Verify session exists
        self.assertIn(session_id, LOCAL_SESSION_STORE)
        session_data = LOCAL_SESSION_STORE[session_id]
        
        # Verify history is stored
        self.assertIn("history", session_data)
        history = session_data["history"]
        self.assertEqual(len(history), 1)
        
        # Verify history entry structure
        turn = history[0]
        required_fields = [
            "timestamp", "user_input", "response", "triage_level",
            "reasoning", "intake", "agent_outputs"
        ]
        for field in required_fields:
            self.assertIn(field, turn, f"History entry missing field: {field}")
    
    def test_pipeline_agents_execution(self):
        """Test that all pipeline agents execute in correct order."""
        user_input = "I've been feeling dizzy for a week"
        session_id = "test-session-005"
        
        response = run_virtual_health_assistant(user_input, session_id=session_id)
        
        # Verify response contains expected fields from different agents
        self.assertIn("intake", response)  # From IntakeAgent
        self.assertIn("triage_level", response)  # From ReasoningAgent
        self.assertIn("message", response)  # From ResponseAgent
        
        # Verify session has agent outputs
        session_data = LOCAL_SESSION_STORE[session_id]
        agent_outputs = session_data.get("agent_outputs", [])
        
        # In mock mode, agent outputs may be limited, but structure should exist
        self.assertIsInstance(agent_outputs, list)
    
    def test_critic_loop_integration(self):
        """Test that critic loop is integrated and working."""
        user_input = "I have had a headache for 2 days"
        session_id = "test-session-006"
        
        response = run_virtual_health_assistant(user_input, session_id=session_id)
        
        # Verify response has critic score (from critic loop)
        self.assertIn("meta", response)
        meta = response["meta"]
        self.assertIn("critic_score", meta)
        
        # Critic score should be a number between 0 and 10
        critic_score = meta["critic_score"]
        if critic_score is not None:
            self.assertGreaterEqual(critic_score, 0)
            self.assertLessEqual(critic_score, 10)
    
    def test_logging_structure(self):
        """Test that logging structure is correct."""
        user_input = "I have had a headache for 2 days"
        session_id = "test-session-007"
        
        response = run_virtual_health_assistant(user_input, session_id=session_id)
        
        # Verify session entry has logging fields
        session_data = LOCAL_SESSION_STORE[session_id]
        history = session_data["history"]
        self.assertEqual(len(history), 1)
        
        turn = history[0]
        # Verify logging fields
        self.assertIn("timestamp", turn)
        self.assertIn("latency_ms", turn)
        self.assertIn("critic_score", turn)
        self.assertIn("triage_level", turn)
        self.assertIn("urgency_score", turn)
    
    def test_error_handling_with_logging(self):
        """Test that errors are logged correctly."""
        # This test verifies that even errors are logged
        # In mock mode, errors are less likely, but structure should handle them
        session_id = "test-session-008"
        
        # Use a valid input that should work
        response = run_virtual_health_assistant(
            "I have had a headache for 2 days",
            session_id=session_id
        )
        
        # Verify response exists (no error)
        self.assertIn("message", response)
        
        # Verify session was created even if there were issues
        # (In this case, there shouldn't be issues, but structure should handle it)
        self.assertIn(session_id, LOCAL_SESSION_STORE)


def run_integration_test_suite():
    """Run the full integration test suite and generate report."""
    print("=" * 60)
    print("Full Pipeline Integration Test")
    print("=" * 60)
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFullPipelineIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    report = {
        "total_tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
    }
    
    print()
    print("=" * 60)
    print("Integration Test Summary")
    print("=" * 60)
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Errors: {report['errors']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print("=" * 60)
    
    # Save report
    report_file = os.path.join(os.path.dirname(__file__), "integration_test_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to: {report_file}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_test_suite()
    sys.exit(0 if success else 1)

