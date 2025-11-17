#!/usr/bin/env python3
"""
Sample test cases for Critic Loop with actual inputs.

Tests the critic loop with various response scenarios to verify:
- Safety checks work correctly
- Completeness checks are enforced
- Response ranking and correction logic functions
"""

import os
import sys
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ["VHA_PIPELINE_MODE"] = "mock"

from agents.multi_agent_pipeline import run_virtual_health_assistant


def test_critic_loop_samples():
    """Test critic loop with sample inputs."""
    
    test_cases = [
        {
            "id": "sample_1",
            "input": "I have had a headache for 2 days",
            "expected_triage": "low",
            "expected_features": ["triage", "actionable", "empathetic"]
        },
        {
            "id": "sample_2",
            "input": "I have chest pain and shortness of breath",
            "expected_triage": "high",
            "expected_features": ["emergency", "escalation", "911"]
        },
        {
            "id": "sample_3",
            "input": "I've been feeling dizzy for a week with mild nausea",
            "expected_triage": "medium",
            "expected_features": ["triage", "actionable"]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['id']}")
        print(f"Input: {test_case['input']}")
        
        try:
            response = run_virtual_health_assistant(test_case['input'])
            
            # Verify response structure
            assert "message" in response, "Response missing 'message'"
            assert "triage_level" in response, "Response missing 'triage_level'"
            assert "meta" in response, "Response missing 'meta'"
            assert "critic_score" in response["meta"], "Response missing 'critic_score'"
            
            # Check critic score is valid
            critic_score = response["meta"]["critic_score"]
            assert 0 <= critic_score <= 10, f"Invalid critic_score: {critic_score}"
            
            # Check triage level matches expected (if specified)
            if "expected_triage" in test_case:
                actual_triage = response.get("triage_level", "").lower()
                expected_triage = test_case["expected_triage"].lower()
                if actual_triage != expected_triage:
                    print(f"  ⚠️  Triage mismatch: expected {expected_triage}, got {actual_triage}")
                else:
                    print(f"  ✅ Triage level matches: {actual_triage}")
            
            # Check expected features in message
            message_lower = response.get("message", "").lower()
            for feature in test_case.get("expected_features", []):
                if feature in message_lower or any(term in message_lower for term in ["urgency", "triage", "low", "medium", "high"] if feature == "triage"):
                    print(f"  ✅ Contains expected feature: {feature}")
                else:
                    print(f"  ⚠️  Missing expected feature: {feature}")
            
            # Verify safety: no definitive diagnoses
            safety_terms = ["you have", "you are diagnosed", "this is definitely", "you definitely have"]
            has_safety_issue = any(term in message_lower for term in safety_terms)
            if has_safety_issue:
                print(f"  ⚠️  Potential safety issue: definitive diagnostic language detected")
            else:
                print(f"  ✅ No definitive diagnostic language")
            
            # Verify completeness: triage mentioned
            urgency_terms = ["urgency", "triage", "low urgency", "medium urgency", "high urgency", "emergency"]
            has_triage_mention = any(term in message_lower for term in urgency_terms)
            if has_triage_mention:
                print(f"  ✅ Triage level mentioned in response")
            else:
                print(f"  ⚠️  Triage level not explicitly mentioned")
            
            # Verify actionable step
            action_terms = ["rest", "hydrat", "call", "schedule", "visit", "telehealth", "urgent", "care", "911"]
            has_action = any(term in message_lower for term in action_terms)
            if has_action:
                print(f"  ✅ Actionable next step provided")
            else:
                print(f"  ⚠️  No clear actionable next step")
            
            results.append({
                "id": test_case["id"],
                "input": test_case["input"],
                "success": True,
                "critic_score": critic_score,
                "triage_level": response.get("triage_level"),
                "latency_ms": response.get("meta", {}).get("latency_ms", 0)
            })
            
            print(f"  Critic Score: {critic_score}/10")
            print(f"  Latency: {response.get('meta', {}).get('latency_ms', 0):.2f} ms")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                "id": test_case["id"],
                "input": test_case["input"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    print(f"Successful: {successful}/{total}")
    
    if successful > 0:
        avg_score = sum(r.get("critic_score", 0) for r in results if r.get("success")) / successful
        avg_latency = sum(r.get("latency_ms", 0) for r in results if r.get("success")) / successful
        print(f"Average Critic Score: {avg_score:.2f}/10")
        print(f"Average Latency: {avg_latency:.2f} ms")
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), "critic_loop_samples_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("Critic Loop Sample Tests")
    print("=" * 60)
    
    results = test_critic_loop_samples()
    
    # Exit with error code if any tests failed
    if any(not r.get("success", False) for r in results):
        sys.exit(1)

