#!/usr/bin/env python3
"""
Latency benchmarking script for parallel vs sequential execution.

Compares:
- Sequential: Intake → Data → Reasoning → Draft → Loop → Final
- Parallel: Intake → Parallel(Data + Reasoning) → Draft → Loop → Final
"""

import os
import sys
import time
import json
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set mock mode for faster benchmarking
os.environ["VHA_PIPELINE_MODE"] = "mock"

from agents.multi_agent_pipeline import run_virtual_health_assistant


def benchmark_pipeline(
    test_cases: List[Dict[str, str]], 
    num_runs: int = 5
) -> Dict[str, Any]:
    """
    Benchmark the pipeline with multiple test cases.
    
    Args:
        test_cases: List of test cases with 'input' key
        num_runs: Number of runs per test case for averaging
    
    Returns:
        Dictionary with latency statistics
    """
    results = {
        "test_cases": [],
        "summary": {
            "total_tests": len(test_cases),
            "total_runs": len(test_cases) * num_runs,
            "avg_latency_ms": 0.0,
            "min_latency_ms": float('inf'),
            "max_latency_ms": 0.0,
        }
    }
    
    all_latencies = []
    
    for test_case in test_cases:
        test_input = test_case.get("input", "")
        test_id = test_case.get("id", "unknown")
        
        latencies = []
        for run in range(num_runs):
            start_time = time.time()
            try:
                response = run_virtual_health_assistant(test_input)
                latency_ms = (time.time() - start_time) * 1000.0
                latencies.append(latency_ms)
                all_latencies.append(latency_ms)
                
                # Verify response structure
                assert "message" in response, f"Response missing 'message' for {test_id}"
                assert "triage_level" in response, f"Response missing 'triage_level' for {test_id}"
                
            except Exception as e:
                print(f"Error in test {test_id}, run {run+1}: {e}")
                latencies.append(float('inf'))
        
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        min_latency = min(latencies) if latencies else 0.0
        max_latency = max(latencies) if latencies else 0.0
        
        results["test_cases"].append({
            "id": test_id,
            "input": test_input,
            "runs": num_runs,
            "avg_latency_ms": round(avg_latency, 2),
            "min_latency_ms": round(min_latency, 2),
            "max_latency_ms": round(max_latency, 2),
            "latencies_ms": [round(l, 2) for l in latencies]
        })
    
    # Calculate summary statistics
    if all_latencies:
        results["summary"]["avg_latency_ms"] = round(sum(all_latencies) / len(all_latencies), 2)
        results["summary"]["min_latency_ms"] = round(min(all_latencies), 2)
        results["summary"]["max_latency_ms"] = round(max(all_latencies), 2)
        results["summary"]["median_latency_ms"] = round(sorted(all_latencies)[len(all_latencies) // 2], 2)
    
    return results


def generate_latency_report(results: Dict[str, Any], output_file: str = "tests/latency_report.md") -> None:
    """Generate a markdown latency report."""
    
    with open(output_file, 'w') as f:
        f.write("# Latency Benchmark Report\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total Test Cases:** {results['summary']['total_tests']}\n")
        f.write(f"- **Total Runs:** {results['summary']['total_runs']}\n")
        f.write(f"- **Average Latency:** {results['summary']['avg_latency_ms']} ms\n")
        f.write(f"- **Min Latency:** {results['summary']['min_latency_ms']} ms\n")
        f.write(f"- **Max Latency:** {results['summary']['max_latency_ms']} ms\n")
        if 'median_latency_ms' in results['summary']:
            f.write(f"- **Median Latency:** {results['summary']['median_latency_ms']} ms\n")
        f.write("\n")
        
        f.write("## Test Case Results\n\n")
        f.write("| Test ID | Input | Avg Latency (ms) | Min (ms) | Max (ms) |\n")
        f.write("|---------|-------|------------------|----------|----------|\n")
        
        for test_case in results['test_cases']:
            input_preview = test_case['input'][:50] + "..." if len(test_case['input']) > 50 else test_case['input']
            f.write(f"| {test_case['id']} | {input_preview} | {test_case['avg_latency_ms']} | "
                   f"{test_case['min_latency_ms']} | {test_case['max_latency_ms']} |\n")
        
        f.write("\n## Detailed Latencies\n\n")
        for test_case in results['test_cases']:
            f.write(f"### {test_case['id']}\n\n")
            f.write(f"- **Input:** {test_case['input']}\n")
            f.write(f"- **Latencies:** {test_case['latencies_ms']} ms\n")
            f.write(f"- **Average:** {test_case['avg_latency_ms']} ms\n\n")
        
        f.write("## Notes\n\n")
        f.write("- Latency measured from pipeline start to response completion\n")
        f.write("- Mock mode enabled for faster benchmarking\n")
        f.write("- Parallel execution (DataAgent + ReasoningAgent) should show improved latency\n")
        f.write("- Critic loop may add 1-3 iterations depending on response quality\n")


if __name__ == "__main__":
    # Load test cases
    test_cases_file = os.path.join(os.path.dirname(__file__), "test_cases.json")
    if os.path.exists(test_cases_file):
        with open(test_cases_file, 'r') as f:
            test_cases = json.load(f)
    else:
        # Fallback test cases
        test_cases = [
            {"id": "t1", "input": "I have had a headache for 2 days"},
            {"id": "t2", "input": "I have chest pain and shortness of breath"},
        ]
    
    print("=" * 60)
    print("Latency Benchmarking - Parallel Execution")
    print("=" * 60)
    print(f"Running {len(test_cases)} test cases with 5 runs each...")
    print()
    
    results = benchmark_pipeline(test_cases, num_runs=5)
    
    print("Benchmark Results:")
    print(f"  Average Latency: {results['summary']['avg_latency_ms']} ms")
    print(f"  Min Latency: {results['summary']['min_latency_ms']} ms")
    print(f"  Max Latency: {results['summary']['max_latency_ms']} ms")
    print()
    
    # Generate report
    report_file = os.path.join(os.path.dirname(__file__), "latency_report.md")
    generate_latency_report(results, report_file)
    print(f"Report generated: {report_file}")
    
    # Save JSON results
    json_file = os.path.join(os.path.dirname(__file__), "latency_results.json")
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"JSON results saved: {json_file}")
    
    print()
    print("=" * 60)
    print("Benchmarking complete!")
    print("=" * 60)

