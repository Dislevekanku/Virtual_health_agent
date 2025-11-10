#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for grounded response formatting utilities.
"""

import unittest

from rag_simplified import (
    RAGResponse,
    SearchResult,
    build_grounded_message,
)


class GroundedMessageFormattingTests(unittest.TestCase):
    """Ensure grounded replies reference clinical guidance."""

    def test_grounded_message_includes_guidance_prefix(self):
        rag_response = RAGResponse(
            answer="Stay hydrated and monitor your symptoms.",
            citations=["OID-CLINICAL-001"],
            triage_level="routine",
            next_steps="Schedule a telehealth follow-up if symptoms persist.",
            confidence=0.8,
            emergency_flags=[],
        )

        search_results = [
            SearchResult(
                snippet="Clinical guidance on managing lightheadedness.",
                title="Mayo Clinic – Lightheadedness",
                source="Mayo Clinic",
                document_id="OID-CLINICAL-001",
                score=0.9,
            ),
            SearchResult(
                snippet="CDC public health recommendations for dizziness.",
                title="CDC – Dizziness Overview",
                source="CDC",
                document_id="OID-CLINICAL-002",
                score=0.8,
            ),
        ]

        message = build_grounded_message(rag_response, search_results)

        self.assertIn("According to clinical guidance", message)
        self.assertIn("[1] Mayo Clinic – Lightheadedness", message)
        self.assertIn("Stay hydrated and monitor your symptoms.", message)


if __name__ == "__main__":
    unittest.main()

