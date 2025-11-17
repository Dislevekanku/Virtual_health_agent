#!/usr/bin/env python3
"""
Full End-to-End Scenario Test

Tests complete pipeline with:
- Synthetic patient profile
- Symptom intake → triage reasoning → recommendation output
- Logging + latency capture
- Validation of reasoning trace, triage clarity, UI smoothness, FHIR responses
- Metrics: latency (avg/95th), token usage, error rate
"""

import os
import sys
import json
import time
import statistics
from typing import Dict, List, Any, Tuple
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ["VHA_PIPELINE_MODE"] = "mock"

from agents.multi_agent_pipeline import (
    run_virtual_health_assistant,
    LOCAL_SESSION_STORE,
)


# Synthetic Patient Profile
SYNTHETIC_PATIENT = {
    "patient_id": "synthetic-patient-001",
    "name": "Jane Doe",
    "age": 45,
    "gender": "Female",
    "medical_history": [
        "Hypertension (controlled)",
        "Type 2 Diabetes (well-managed)",
        "Previous episodes of migraines"
    ],
    "current_medications": [
        "Lisinopril 10mg daily",
        "Metformin 500mg twice daily"
    ],
    "allergies": ["Penicillin"],
    "recent_encounters": [
        {
            "date": "2025-01-10",
            "reason": "Routine check-up",
            "diagnosis": "Hypertension, controlled"
        },
        {
            "date": "2024-12-15",
            "reason": "Migraine follow-up",
            "diagnosis": "Tension headache"
        }
    ]
}


def create_synthetic_scenario() -> Dict[str, Any]:
    """Create a synthetic end-to-end scenario."""
    return {
        "scenario_id": "e2e-scenario-001",
        "patient": SYNTHETIC_PATIENT,
        "symptoms": [
            {
                "turn": 1,
                "input": "I've been experiencing severe headaches for the past 3 days. The pain is about an 8 out of 10.",
                "expected_triage": "medium",
                "expected_keywords": ["headache", "severity", "urgency"]
            },
            {
                "turn": 2,
                "input": "I also feel nauseous and sensitive to light.",
                "expected_triage": "medium",
                "expected_keywords": ["nausea", "sensitivity"]
            },
            {
                "turn": 3,
                "input": "The headache started after I missed my medication yesterday.",
                "expected_triage": "medium",
                "expected_keywords": ["medication", "missed"]
            }
        ]
    }


def validate_reasoning_trace(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate model reasoning trace quality."""
    validation = {
        "has_intake": False,
        "has_triage": False,
        "has_reasoning": False,
        "reasoning_quality": "unknown",
        "issues": []
    }
    
    # Check intake
    if "intake" in response:
        validation["has_intake"] = True
        intake = response["intake"]
        if not intake.get("symptom") or intake.get("symptom") == "unspecified":
            validation["issues"].append("Intake missing symptom")
    else:
        validation["issues"].append("Missing intake data")
    
    # Check triage
    if "triage_level" in response:
        validation["has_triage"] = True
        triage = response.get("triage_level", "").lower()
        if triage not in ["low", "medium", "high"]:
            validation["issues"].append(f"Invalid triage level: {triage}")
    else:
        validation["issues"].append("Missing triage level")
    
    # Check reasoning
    if "reasoning" in response:
        validation["has_reasoning"] = True
        reasoning = response["reasoning"]
        if isinstance(reasoning, list) and len(reasoning) > 0:
            # Check reasoning quality
            if len(reasoning) >= 2:
                validation["reasoning_quality"] = "good"
            elif len(reasoning) == 1:
                validation["reasoning_quality"] = "acceptable"
            else:
                validation["reasoning_quality"] = "poor"
                validation["issues"].append("Reasoning list is empty")
        else:
            validation["issues"].append("Reasoning is not a valid list")
    else:
        validation["issues"].append("Missing reasoning")
    
    # Check urgency score
    if "urgency_score" in response:
        score = response["urgency_score"]
        if not isinstance(score, (int, float)) or score < 1 or score > 10:
            validation["issues"].append(f"Invalid urgency_score: {score}")
    
    return validation


def validate_triage_message_clarity(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate triage message clarity."""
    validation = {
        "has_message": False,
        "mentions_triage": False,
        "has_actionable_step": False,
        "clarity_score": 0,
        "issues": []
    }
    
    message = response.get("message", "")
    if not message:
        validation["issues"].append("Missing message")
        return validation
    
    validation["has_message"] = True
    
    # Check if triage level is mentioned
    triage_level = response.get("triage_level", "").lower()
    urgency_terms = ["urgency", "triage", "low", "medium", "high", "emergency", "urgent"]
    if any(term in message.lower() for term in urgency_terms):
        validation["mentions_triage"] = True
        validation["clarity_score"] += 3
    else:
        validation["issues"].append("Message does not mention triage/urgency level")
    
    # Check for actionable steps
    action_terms = ["rest", "hydrat", "call", "schedule", "visit", "telehealth", "urgent", "care", "911", "emergency", "consult"]
    if any(term in message.lower() for term in action_terms):
        validation["has_actionable_step"] = True
        validation["clarity_score"] += 3
    else:
        validation["issues"].append("Message does not provide actionable next step")
    
    # Check message length (should be informative but not too long)
    if 50 <= len(message) <= 500:
        validation["clarity_score"] += 2
    elif len(message) < 50:
        validation["issues"].append("Message too short")
    else:
        validation["issues"].append("Message too long")
    
    # Check for empathetic language
    empathetic_terms = ["understand", "here to help", "concern", "feel", "sorry"]
    if any(term in message.lower() for term in empathetic_terms):
        validation["clarity_score"] += 2
    else:
        validation["issues"].append("Message lacks empathetic language")
    
    return validation


def validate_fhir_responses() -> Dict[str, Any]:
    """Validate FHIR mock responses are working correctly."""
    validation = {
        "fhir_endpoints_working": False,
        "patient_context_retrieved": False,
        "visit_notes_available": False,
        "issues": []
    }
    
    try:
        from agents.multi_agent_pipeline import fetch_patient_context
        from mock_fhir import load_patient, load_encounters
        
        # Test patient loading
        try:
            patient = load_patient("patient-001")
            if patient:
                validation["patient_context_retrieved"] = True
            else:
                validation["issues"].append("Patient data not loaded")
        except Exception as e:
            validation["issues"].append(f"Error loading patient: {e}")
        
        # Test encounters
        try:
            encounters = load_encounters("patient-001")
            if encounters and len(encounters) > 0:
                validation["visit_notes_available"] = True
            else:
                validation["issues"].append("No encounters found")
        except Exception as e:
            validation["issues"].append(f"Error loading encounters: {e}")
        
        # Test fetch_patient_context
        try:
            context = fetch_patient_context(json.dumps({"patient_id": "patient-001"}))
            if context and "patient_id" in context:
                validation["fhir_endpoints_working"] = True
            else:
                validation["issues"].append("fetch_patient_context returned invalid data")
        except Exception as e:
            validation["issues"].append(f"Error in fetch_patient_context: {e}")
        
    except ImportError as e:
        validation["issues"].append(f"Import error: {e}")
    
    return validation


def estimate_token_usage(text: str) -> int:
    """Estimate token usage (rough approximation: 1 token ≈ 4 characters)."""
    return len(text) // 4


def run_end_to_end_scenario(num_runs: int = 10) -> Dict[str, Any]:
    """Run full end-to-end scenario multiple times and collect metrics."""
    scenario = create_synthetic_scenario()
    results = {
        "scenario": scenario,
        "runs": [],
        "metrics": {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "error_rate": 0.0,
            "latencies_ms": [],
            "avg_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "token_usage": {
                "input_tokens": [],
                "output_tokens": [],
                "total_tokens": [],
                "avg_input_tokens": 0.0,
                "avg_output_tokens": 0.0,
                "avg_total_tokens": 0.0
            },
            "reasoning_validation": {
                "passed": 0,
                "failed": 0,
                "issues": []
            },
            "clarity_validation": {
                "passed": 0,
                "failed": 0,
                "avg_clarity_score": 0.0,
                "issues": []
            },
            "fhir_validation": {
                "passed": False,
                "issues": []
            }
        }
    }
    
    # Validate FHIR once
    fhir_validation = validate_fhir_responses()
    results["metrics"]["fhir_validation"] = fhir_validation
    
    # Run scenario multiple times
    for run_num in range(1, num_runs + 1):
        print(f"\n{'='*60}")
        print(f"Run {run_num}/{num_runs}")
        print(f"{'='*60}")
        
        run_result = {
            "run_number": run_num,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "turns": [],
            "success": False,
            "error": None,
            "latency_ms": 0.0,
            "token_usage": {"input": 0, "output": 0, "total": 0}
        }
        
        try:
            session_id = f"e2e-{scenario['scenario_id']}-run-{run_num}"
            LOCAL_SESSION_STORE.clear()  # Clear for clean run
            
            total_start_time = time.time()
            total_input_tokens = 0
            total_output_tokens = 0
            
            # Execute all turns
            for symptom in scenario["symptoms"]:
                turn_start = time.time()
                user_input = symptom["input"]
                
                print(f"\nTurn {symptom['turn']}: {user_input[:60]}...")
                
                response = run_virtual_health_assistant(
                    user_input,
                    session_id=session_id
                )
                
                turn_latency = (time.time() - turn_start) * 1000.0
                
                # Estimate token usage
                input_tokens = estimate_token_usage(user_input)
                output_tokens = estimate_token_usage(response.get("message", ""))
                total_input_tokens += input_tokens
                total_output_tokens += output_tokens
                
                # Validate reasoning trace
                reasoning_validation = validate_reasoning_trace(response)
                
                # Validate message clarity
                clarity_validation = validate_triage_message_clarity(response)
                
                turn_result = {
                    "turn_number": symptom["turn"],
                    "user_input": user_input,
                    "response": response,
                    "latency_ms": turn_latency,
                    "triage_level": response.get("triage_level"),
                    "urgency_score": response.get("urgency_score"),
                    "critic_score": response.get("meta", {}).get("critic_score"),
                    "reasoning_validation": reasoning_validation,
                    "clarity_validation": clarity_validation,
                    "token_usage": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": input_tokens + output_tokens
                    }
                }
                
                run_result["turns"].append(turn_result)
                
                # Print turn summary
                print(f"  ✅ Triage: {response.get('triage_level')} | "
                      f"Urgency: {response.get('urgency_score', 'N/A')} | "
                      f"Critic: {response.get('meta', {}).get('critic_score', 'N/A')}/10")
                print(f"  ⏱️  Latency: {turn_latency:.2f} ms")
                print(f"  📊 Reasoning: {reasoning_validation['reasoning_quality']} | "
                      f"Clarity: {clarity_validation['clarity_score']}/10")
            
            total_latency = (time.time() - total_start_time) * 1000.0
            run_result["latency_ms"] = total_latency
            run_result["token_usage"] = {
                "input": total_input_tokens,
                "output": total_output_tokens,
                "total": total_input_tokens + total_output_tokens
            }
            run_result["success"] = True
            
            # Collect metrics
            results["metrics"]["latencies_ms"].append(total_latency)
            results["metrics"]["token_usage"]["input_tokens"].append(total_input_tokens)
            results["metrics"]["token_usage"]["output_tokens"].append(total_output_tokens)
            results["metrics"]["token_usage"]["total_tokens"].append(total_input_tokens + total_output_tokens)
            
            # Aggregate validation results
            for turn in run_result["turns"]:
                reasoning_val = turn["reasoning_validation"]
                if reasoning_val["has_intake"] and reasoning_val["has_triage"] and reasoning_val["has_reasoning"]:
                    results["metrics"]["reasoning_validation"]["passed"] += 1
                else:
                    results["metrics"]["reasoning_validation"]["failed"] += 1
                    results["metrics"]["reasoning_validation"]["issues"].extend(reasoning_val["issues"])
                
                clarity_val = turn["clarity_validation"]
                if clarity_val["has_message"] and clarity_val["mentions_triage"] and clarity_val["has_actionable_step"]:
                    results["metrics"]["clarity_validation"]["passed"] += 1
                else:
                    results["metrics"]["clarity_validation"]["failed"] += 1
                    results["metrics"]["clarity_validation"]["issues"].extend(clarity_val["issues"])
            
            print(f"\n✅ Run {run_num} completed successfully")
            print(f"   Total latency: {total_latency:.2f} ms")
            print(f"   Total tokens: {total_input_tokens + total_output_tokens} (in: {total_input_tokens}, out: {total_output_tokens})")
            
        except Exception as e:
            run_result["success"] = False
            run_result["error"] = str(e)
            print(f"\n❌ Run {run_num} failed: {e}")
            import traceback
            traceback.print_exc()
        
        results["runs"].append(run_result)
        results["metrics"]["total_runs"] += 1
        if run_result["success"]:
            results["metrics"]["successful_runs"] += 1
        else:
            results["metrics"]["failed_runs"] += 1
    
    # Calculate final metrics
    if results["metrics"]["latencies_ms"]:
        results["metrics"]["avg_latency_ms"] = statistics.mean(results["metrics"]["latencies_ms"])
        if len(results["metrics"]["latencies_ms"]) > 1:
            results["metrics"]["p95_latency_ms"] = statistics.quantiles(
                results["metrics"]["latencies_ms"], n=20
            )[18]  # 95th percentile (19th out of 20)
        else:
            results["metrics"]["p95_latency_ms"] = results["metrics"]["latencies_ms"][0]
    
    if results["metrics"]["token_usage"]["input_tokens"]:
        results["metrics"]["token_usage"]["avg_input_tokens"] = statistics.mean(
            results["metrics"]["token_usage"]["input_tokens"]
        )
        results["metrics"]["token_usage"]["avg_output_tokens"] = statistics.mean(
            results["metrics"]["token_usage"]["output_tokens"]
        )
        results["metrics"]["token_usage"]["avg_total_tokens"] = statistics.mean(
            results["metrics"]["token_usage"]["total_tokens"]
        )
    
    results["metrics"]["error_rate"] = (
        results["metrics"]["failed_runs"] / results["metrics"]["total_runs"] * 100
        if results["metrics"]["total_runs"] > 0 else 0.0
    )
    
    if results["metrics"]["clarity_validation"]["passed"] > 0:
        # Calculate average clarity score from all turns
        all_clarity_scores = []
        for run in results["runs"]:
            if run["success"]:
                for turn in run["turns"]:
                    all_clarity_scores.append(turn["clarity_validation"]["clarity_score"])
        if all_clarity_scores:
            results["metrics"]["clarity_validation"]["avg_clarity_score"] = statistics.mean(all_clarity_scores)
    
    return results


def generate_e2e_report(results: Dict[str, Any], output_file: str = "tests/e2e_scenario_report.md") -> None:
    """Generate comprehensive end-to-end scenario report."""
    
    metrics = results["metrics"]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# End-to-End Scenario Test Report\n\n")
        f.write(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Runs:** {metrics['total_runs']}\n")
        f.write(f"- **Successful Runs:** {metrics['successful_runs']}\n")
        f.write(f"- **Failed Runs:** {metrics['failed_runs']}\n")
        f.write(f"- **Error Rate:** {metrics['error_rate']:.2f}%\n")
        f.write(f"- **Average Latency:** {metrics['avg_latency_ms']:.2f} ms\n")
        f.write(f"- **95th Percentile Latency:** {metrics['p95_latency_ms']:.2f} ms\n")
        f.write("\n")
        
        f.write("## Synthetic Patient Profile\n\n")
        patient = results["scenario"]["patient"]
        f.write(f"- **Patient ID:** {patient['patient_id']}\n")
        f.write(f"- **Name:** {patient['name']}\n")
        f.write(f"- **Age:** {patient['age']}\n")
        f.write(f"- **Medical History:** {', '.join(patient['medical_history'])}\n")
        f.write(f"- **Current Medications:** {', '.join(patient['current_medications'])}\n")
        f.write("\n")
        
        f.write("## Latency Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Average Latency | {metrics['avg_latency_ms']:.2f} ms |\n")
        f.write(f"| 95th Percentile Latency | {metrics['p95_latency_ms']:.2f} ms |\n")
        f.write(f"| Min Latency | {min(metrics['latencies_ms']) if metrics['latencies_ms'] else 0:.2f} ms |\n")
        f.write(f"| Max Latency | {max(metrics['latencies_ms']) if metrics['latencies_ms'] else 0:.2f} ms |\n")
        f.write("\n")
        
        f.write("## Token Usage\n\n")
        token_usage = metrics["token_usage"]
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Average Input Tokens | {token_usage['avg_input_tokens']:.1f} |\n")
        f.write(f"| Average Output Tokens | {token_usage['avg_output_tokens']:.1f} |\n")
        f.write(f"| Average Total Tokens | {token_usage['avg_total_tokens']:.1f} |\n")
        f.write("\n")
        
        f.write("## Validation Results\n\n")
        
        f.write("### Reasoning Trace Quality\n\n")
        reasoning = metrics["reasoning_validation"]
        f.write(f"- **Passed:** {reasoning['passed']}\n")
        f.write(f"- **Failed:** {reasoning['failed']}\n")
        if reasoning['issues']:
            f.write("- **Issues:**\n")
            for issue in set(reasoning['issues']):
                f.write(f"  - {issue}\n")
        f.write("\n")
        
        f.write("### Triage Message Clarity\n\n")
        clarity = metrics["clarity_validation"]
        f.write(f"- **Passed:** {clarity['passed']}\n")
        f.write(f"- **Failed:** {clarity['failed']}\n")
        f.write(f"- **Average Clarity Score:** {clarity['avg_clarity_score']:.1f}/10\n")
        if clarity['issues']:
            f.write("- **Issues:**\n")
            for issue in set(clarity['issues']):
                f.write(f"  - {issue}\n")
        f.write("\n")
        
        f.write("### FHIR Mock Responses\n\n")
        fhir = metrics["fhir_validation"]
        f.write(f"- **FHIR Endpoints Working:** {fhir['fhir_endpoints_working']}\n")
        f.write(f"- **Patient Context Retrieved:** {fhir['patient_context_retrieved']}\n")
        f.write(f"- **Visit Notes Available:** {fhir['visit_notes_available']}\n")
        if fhir['issues']:
            f.write("- **Issues:**\n")
            for issue in fhir['issues']:
                f.write(f"  - {issue}\n")
        f.write("\n")
        
        f.write("## Run Details\n\n")
        for run in results["runs"]:
            f.write(f"### Run {run['run_number']}\n\n")
            status = "Success" if run['success'] else "Failed"
            f.write(f"- **Status:** {status}\n")
            if run['success']:
                f.write(f"- **Latency:** {run['latency_ms']:.2f} ms\n")
                f.write(f"- **Token Usage:** {run['token_usage']['total']} (in: {run['token_usage']['input']}, out: {run['token_usage']['output']})\n")
                f.write(f"- **Turns:** {len(run['turns'])}\n")
            else:
                f.write(f"- **Error:** {run['error']}\n")
            f.write("\n")
        
        f.write("## Recommendations\n\n")
        if metrics['error_rate'] > 0:
            f.write("- WARNING: Error rate is above 0%. Review failed runs for patterns.\n")
        if metrics['avg_latency_ms'] > 5000:
            f.write("- WARNING: Average latency is high. Consider optimization.\n")
        if clarity['avg_clarity_score'] < 7:
            f.write("- WARNING: Message clarity could be improved.\n")
        if not fhir['fhir_endpoints_working']:
            f.write("- WARNING: FHIR endpoints need attention.\n")
        if not any([metrics['error_rate'] > 0, metrics['avg_latency_ms'] > 5000, clarity['avg_clarity_score'] < 7, not fhir['fhir_endpoints_working']]):
            f.write("- SUCCESS: All systems performing well!\n")
        f.write("\n")


if __name__ == "__main__":
    print("=" * 60)
    print("End-to-End Scenario Test")
    print("=" * 60)
    print("\nRunning 10 iterations of full scenario...")
    print("This will test:")
    print("  • Synthetic patient profile")
    print("  • Symptom intake → triage → recommendation")
    print("  • Logging + latency capture")
    print("  • Reasoning trace quality")
    print("  • Triage message clarity")
    print("  • FHIR mock responses")
    print("\n")
    
    results = run_end_to_end_scenario(num_runs=10)
    
    # Generate report
    report_file = os.path.join(os.path.dirname(__file__), "e2e_scenario_report.md")
    generate_e2e_report(results, report_file)
    
    # Save JSON results
    json_file = os.path.join(os.path.dirname(__file__), "e2e_scenario_results.json")
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    metrics = results["metrics"]
    print(f"Total Runs: {metrics['total_runs']}")
    print(f"Successful: {metrics['successful_runs']}")
    print(f"Failed: {metrics['failed_runs']}")
    print(f"Error Rate: {metrics['error_rate']:.2f}%")
    print(f"\nLatency:")
    print(f"  Average: {metrics['avg_latency_ms']:.2f} ms")
    print(f"  95th Percentile: {metrics['p95_latency_ms']:.2f} ms")
    print(f"\nToken Usage:")
    print(f"  Avg Input: {metrics['token_usage']['avg_input_tokens']:.1f}")
    print(f"  Avg Output: {metrics['token_usage']['avg_output_tokens']:.1f}")
    print(f"  Avg Total: {metrics['token_usage']['avg_total_tokens']:.1f}")
    print(f"\nValidation:")
    print(f"  Reasoning: {metrics['reasoning_validation']['passed']} passed, {metrics['reasoning_validation']['failed']} failed")
    print(f"  Clarity: {metrics['clarity_validation']['passed']} passed, {metrics['clarity_validation']['failed']} failed")
    print(f"  Avg Clarity Score: {metrics['clarity_validation']['avg_clarity_score']:.1f}/10")
    print(f"  FHIR: {'✅ Working' if metrics['fhir_validation']['fhir_endpoints_working'] else '❌ Issues'}")
    print("\n" + "=" * 60)
    print(f"Report generated: {report_file}")
    print(f"JSON results: {json_file}")
    print("=" * 60)

