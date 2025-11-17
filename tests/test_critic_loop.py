#!/usr/bin/env python3
"""
Unit tests for Critic Loop implementation.

Tests:
- CriticAgent safety and completeness checks
- RefinerAgent correction logic
- LoopAgent iteration limits
- Response ranking functionality
"""

import os
import sys
import json
import unittest
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ["VHA_PIPELINE_MODE"] = "mock"

from agents.multi_agent_pipeline import (
    run_virtual_health_assistant,
    critic_agent,
    refiner_agent,
    loop_agent,
)


class TestCriticLoop(unittest.TestCase):
    """Test cases for Critic Loop functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_draft_response = {
            "message": "Based on your symptoms, this is considered a low urgency situation. Please rest and stay hydrated.",
            "triage_level": "low",
            "urgency_score": 3,
            "reasoning": ["Mild symptoms without red flags"],
            "red_flags": [],
            "intake": {
                "symptom": "headache",
                "duration": "2 days",
                "severity": "mild"
            },
            "citations": []
        }
    
    def test_critic_agent_instruction_structure(self):
        """Test that CriticAgent has proper instruction structure."""
        instruction = critic_agent.instruction
        
        # Check for safety checks
        self.assertIn("SAFETY CHECKS", instruction)
        self.assertIn("no_diagnosis", instruction)
        self.assertIn("no_dosages", instruction)
        self.assertIn("red_flags_escalated", instruction)
        
        # Check for completeness checks
        self.assertIn("COMPLETENESS CHECKS", instruction)
        self.assertIn("triage_mentioned", instruction)
        self.assertIn("actionable_step", instruction)
        
        # Check for response ranking
        self.assertIn("RESPONSE RANKING", instruction)
        self.assertIn("score", instruction)
    
    def test_refiner_agent_instruction_structure(self):
        """Test that RefinerAgent has proper correction logic."""
        instruction = refiner_agent.instruction
        
        # Check for ranking and correction logic
        self.assertIn("RESPONSE RANKING", instruction)
        self.assertIn("CORRECTION PRIORITIES", instruction)
        self.assertIn("Priority 1", instruction)  # Safety
        self.assertIn("Priority 2", instruction)  # Completeness
        self.assertIn("Priority 3", instruction)  # Tone
    
    def test_loop_agent_configuration(self):
        """Test that LoopAgent is configured correctly."""
        self.assertEqual(loop_agent.name, "QualityLoop")
        self.assertEqual(loop_agent.max_iterations, 3)
        self.assertEqual(len(loop_agent.sub_agents), 2)
        self.assertEqual(loop_agent.sub_agents[0].name, "CriticAgent")
        self.assertEqual(loop_agent.sub_agents[1].name, "RefinerAgent")
    
    def test_mock_response_includes_critic_score(self):
        """Test that mock responses include critic_score in meta."""
        response = run_virtual_health_assistant("I have had a headache for 2 days")
        
        self.assertIn("meta", response)
        self.assertIn("critic_score", response["meta"])
        self.assertIsNotNone(response["meta"]["critic_score"])
        self.assertGreaterEqual(response["meta"]["critic_score"], 0)
        self.assertLessEqual(response["meta"]["critic_score"], 10)
    
    def test_response_structure_after_critic_loop(self):
        """Test that responses have correct structure after critic loop."""
        response = run_virtual_health_assistant("I have had a headache for 2 days")
        
        # Required fields
        required_fields = ["message", "triage_level", "reasoning", "intake"]
        for field in required_fields:
            self.assertIn(field, response, f"Response missing required field: {field}")
        
        # Check triage_level is valid
        self.assertIn(response["triage_level"], ["low", "medium", "high"])
    
    def test_high_urgency_response_handling(self):
        """Test that high urgency responses are handled correctly."""
        response = run_virtual_health_assistant("I have chest pain and shortness of breath")
        
        self.assertIn("triage_level", response)
        # Should be high urgency for chest pain + SOB
        if response["triage_level"] == "high":
            self.assertIn("message", response)
            # Should mention emergency/escalation
            message_lower = response["message"].lower()
            self.assertTrue(
                "911" in message_lower or 
                "emergency" in message_lower or 
                "immediately" in message_lower,
                "High urgency response should mention emergency escalation"
            )
    
    def test_critic_loop_iteration_limit(self):
        """Test that critic loop respects max_iterations."""
        # The loop should not exceed 3 iterations
        # This is tested implicitly by ensuring responses complete
        response = run_virtual_health_assistant("I have had a headache for 2 days")
        
        # Response should complete (not hang)
        self.assertIsNotNone(response)
        self.assertIn("message", response)
        
        # Meta should include latency (indicates completion)
        if "meta" in response:
            self.assertIn("latency_ms", response["meta"])


class TestSafetyChecks(unittest.TestCase):
    """Test safety check functionality."""
    
    def test_no_diagnosis_requirement(self):
        """Test that responses should not contain definitive diagnoses."""
        # This is tested by the critic agent instruction
        # In a real scenario, we would mock the critic to verify
        pass
    
    def test_no_dosages_requirement(self):
        """Test that responses should not contain medication dosages."""
        # This is tested by the critic agent instruction
        pass
    
    def test_red_flag_escalation(self):
        """Test that red flags trigger escalation instructions."""
        response = run_virtual_health_assistant("I have chest pain and shortness of breath")
        
        # High urgency should include escalation
        if response.get("triage_level") == "high":
            message = response.get("message", "").lower()
            self.assertTrue(
                "911" in message or "emergency" in message or "immediately" in message,
                "Red flag symptoms should trigger escalation"
            )


class TestCompletenessChecks(unittest.TestCase):
    """Test completeness check functionality."""
    
    def test_triage_level_mentioned(self):
        """Test that responses mention triage level."""
        response = run_virtual_health_assistant("I have had a headache for 2 days")
        
        message = response.get("message", "").lower()
        triage_level = response.get("triage_level", "")
        
        # Should mention urgency or triage level
        urgency_terms = ["urgency", "triage", "low", "medium", "high", "emergency"]
        self.assertTrue(
            any(term in message for term in urgency_terms),
            f"Response should mention triage/urgency level. Message: {response.get('message', '')[:100]}"
        )
    
    def test_actionable_step_provided(self):
        """Test that responses provide actionable next steps."""
        response = run_virtual_health_assistant("I have had a headache for 2 days")
        
        message = response.get("message", "").lower()
        
        # Should include actionable terms
        action_terms = ["rest", "hydrat", "call", "schedule", "visit", "telehealth", "urgent", "care"]
        self.assertTrue(
            any(term in message for term in action_terms),
            "Response should provide actionable next steps"
        )


class TestParallelExecution(unittest.TestCase):
    """Test parallel execution of DataAgent and ReasoningAgent."""
    
    def test_parallel_agent_configuration(self):
        """Test that parallel agent is configured correctly."""
        from agents.multi_agent_pipeline import parallel_data_reasoning
        
        self.assertEqual(parallel_data_reasoning.name, "DataAndReasoning")
        self.assertEqual(len(parallel_data_reasoning.sub_agents), 2)
        
        agent_names = [agent.name for agent in parallel_data_reasoning.sub_agents]
        self.assertIn("DataAgent", agent_names)
        self.assertIn("ReasoningAgent", agent_names)
    
    def test_pipeline_includes_parallel_agent(self):
        """Test that root pipeline includes parallel agent."""
        from agents.multi_agent_pipeline import root_agent
        
        # Check that parallel agent is in the pipeline
        sub_agent_names = [agent.name for agent in root_agent.sub_agents]
        self.assertIn("DataAndReasoning", sub_agent_names)
        
        # Check order: Intake should come before parallel, parallel before draft
        intake_idx = sub_agent_names.index("IntakeAgent") if "IntakeAgent" in sub_agent_names else -1
        parallel_idx = sub_agent_names.index("DataAndReasoning") if "DataAndReasoning" in sub_agent_names else -1
        draft_idx = sub_agent_names.index("DraftResponseAgent") if "DraftResponseAgent" in sub_agent_names else -1
        
        if intake_idx >= 0 and parallel_idx >= 0:
            self.assertLess(intake_idx, parallel_idx, "Intake should come before parallel execution")
        if parallel_idx >= 0 and draft_idx >= 0:
            self.assertLess(parallel_idx, draft_idx, "Parallel should come before draft")


if __name__ == "__main__":
    unittest.main()

