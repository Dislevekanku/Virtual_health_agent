#!/usr/bin/env python3
"""
Test harness for the Virtual Health Assistant multi-agent pipeline.

Loads test cases from tests/test_cases.json, executes the pipeline (mock mode by
default), and produces metrics along with tests/evaluation_report.md.
"""

from __future__ import annotations

import json
import os
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List

# Ensure project root is on the Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


def ensure_mock_mode() -> None:
    """Force the pipeline into mock mode for deterministic tests."""
    os.environ.setdefault("VHA_PIPELINE_MODE", "mock")


def load_test_cases(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Test cases JSON must be a list.")
    return data


def evaluate_cases(cases: List[Dict]) -> Dict:
    from agents.multi_agent_pipeline import run_virtual_health_assistant

    results = []
    tp = Counter()
    pred_counts = Counter()
    actual_counts = Counter()
    latencies = []

    for case in cases:
        case_id = case["id"]
        user_input = case["input"]
        expected_urgency = case["expected_urgency"]
        expected_actions = [kw.lower() for kw in case.get("expected_actions", [])]
        min_score = float(case.get("min_critic_score", 0))

        start = time.time()
        response = run_virtual_health_assistant(user_input)
        elapsed = (time.time() - start) * 1000.0

        triage = (response.get("triage_level") or "").lower()
        message = (response.get("message") or "").lower()
        meta = response.get("meta") or {}
        critic_score = meta.get("critic_score")
        latency_ms = meta.get("latency_ms", elapsed)

        pred_counts[triage] += 1
        actual_counts[expected_urgency] += 1
        correct_label = triage == expected_urgency.lower()
        if correct_label:
            tp[triage] += 1

        keywords_ok = all(keyword in message for keyword in expected_actions)
        score_ok = critic_score is None or critic_score >= min_score

        passed = correct_label and keywords_ok and score_ok
        latencies.append(latency_ms)

        results.append(
            {
                "id": case_id,
                "input": user_input,
                "predicted": triage,
                "expected": expected_urgency.lower(),
                "correct_label": correct_label,
                "keywords_ok": keywords_ok,
                "score_ok": score_ok,
                "critic_score": critic_score,
                "latency_ms": latency_ms,
                "message": response.get("message", ""),
            }
        )

    total = len(results)
    accuracy = sum(1 for r in results if r["correct_label"]) / total if total else 0.0

    precision = {}
    for label, count in pred_counts.items():
        if count == 0:
            continue
        precision[label] = tp[label] / count

    avg_latency = statistics.mean(latencies) if latencies else 0.0

    failures = [
        r
        for r in results
        if not (r["correct_label"] and r["keywords_ok"] and r["score_ok"])
    ]

    return {
        "results": results,
        "accuracy": accuracy,
        "precision": precision,
        "avg_latency": avg_latency,
        "failures": failures,
    }


def write_report(summary: Dict, output_path: Path) -> None:
    lines = [
        "# Evaluation Report",
        "",
        f"- Total test cases: {len(summary['results'])}",
        f"- Accuracy: {summary['accuracy']*100:.2f}%",
        f"- Average latency: {summary['avg_latency']:.2f} ms",
        "",
        "## Precision by Urgency",
    ]

    if summary["precision"]:
        for label, value in summary["precision"].items():
            lines.append(f"- {label}: {value*100:.2f}%")
    else:
        lines.append("- No predictions recorded.")

    if summary["failures"]:
        lines.append("")
        lines.append("## Failures")
        for failure in summary["failures"]:
            lines.append(
                f"- **{failure['id']}** expected `{failure['expected']}` "
                f"but predicted `{failure['predicted']}`; "
                f"keywords_ok={failure['keywords_ok']}, "
                f"score_ok={failure['score_ok']}, "
                f"critic_score={failure['critic_score']}"
            )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ensure_mock_mode()
    cases = load_test_cases(Path("tests") / "test_cases.json")
    summary = evaluate_cases(cases)
    write_report(summary, Path("tests") / "evaluation_report.md")

    if summary["failures"]:
        print("Some tests failed. See tests/evaluation_report.md for details.")
        return 1

    print("All tests passed. Evaluation report generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

