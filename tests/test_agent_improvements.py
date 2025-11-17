#!/usr/bin/env python3
"""
Test script to verify agent improvements:
- IntakeAgent enhanced parsing
- ReasoningAgent urgency scoring
- DataAgent visit notes extraction
"""

import json
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.multi_agent_pipeline import (
    fetch_patient_context,
    _extract_visit_notes,
)
from mock_fhir import load_encounters


def test_visit_notes_extraction():
    """Test that visit notes are correctly extracted from encounters."""
    print("Testing visit notes extraction...")
    encounters = load_encounters("patient-001")
    notes = _extract_visit_notes(encounters)
    
    assert len(notes) > 0, "Should extract at least one visit note"
    assert "encounter_id" in notes[0], "Note should have encounter_id"
    assert "date" in notes[0], "Note should have date"
    assert "reason" in notes[0], "Note should have reason"
    assert "diagnosis" in notes[0], "Note should have diagnosis"
    print(f"✓ Extracted {len(notes)} visit notes")
    print(f"  Sample note: {json.dumps(notes[0], indent=2)}")
    return True


def test_patient_context_with_visit_notes():
    """Test that fetch_patient_context includes visit_notes."""
    print("\nTesting patient context with visit notes...")
    intake_json = json.dumps({"patient_id": "patient-001"})
    context = fetch_patient_context(intake_json)
    
    assert "visit_notes" in context, "Context should include visit_notes"
    assert isinstance(context["visit_notes"], list), "visit_notes should be a list"
    assert len(context["visit_notes"]) > 0, "Should have at least one visit note"
    print(f"✓ Patient context includes {len(context['visit_notes'])} visit notes")
    print(f"  Context keys: {list(context.keys())}")
    return True


def test_intake_parsing_examples():
    """Test that IntakeAgent instructions cover edge cases."""
    print("\nTesting IntakeAgent instruction coverage...")
    # Check that instructions mention validation, edge cases, severity mapping
    from agents.multi_agent_pipeline import intake_agent
    instruction = intake_agent.instruction
    
    assert "edge cases" in instruction.lower(), "Should mention edge cases"
    assert "validation" in instruction.lower(), "Should mention validation"
    assert "severity" in instruction.lower(), "Should mention severity parsing"
    assert "unknown" in instruction.lower(), "Should handle unknown values"
    print("✓ IntakeAgent instructions cover edge cases and validation")
    return True


def test_reasoning_urgency_scoring():
    """Test that ReasoningAgent includes urgency scoring."""
    print("\nTesting ReasoningAgent urgency scoring...")
    from agents.multi_agent_pipeline import reasoning_agent
    instruction = reasoning_agent.instruction
    
    assert "urgency_score" in instruction, "Should include urgency_score"
    assert "urgency scoring" in instruction.lower(), "Should mention urgency scoring"
    assert "red_flags" in instruction, "Should include red_flags"
    assert "triage logic" in instruction.lower(), "Should mention triage logic"
    print("✓ ReasoningAgent includes urgency scoring and red flags")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Agent Improvements Test Suite")
    print("=" * 60)
    
    try:
        test_visit_notes_extraction()
        test_patient_context_with_visit_notes()
        test_intake_parsing_examples()
        test_reasoning_urgency_scoring()
        
        print("\n" + "=" * 60)
        print("✓ All agent improvement tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

