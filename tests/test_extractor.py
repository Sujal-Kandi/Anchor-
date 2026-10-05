"""
Tests for anchor.extractor — NER-based claim extraction.

These tests will be filled in during Phase 3.
The fixture file tests/fixtures/sample_reports.json will provide
real Research Agent outputs with known ground-truth claims.
"""

import pytest
from anchor.extractor import extract_claims, Claim


class TestExtractClaims:
    """Tests for the extract_claims() function."""

    def test_extracts_percentage(self):
        """Should extract '12%' as a PERCENT claim."""
        results = extract_claims("Revenue grew by 12% last quarter.")
        types = [c.entity_type for c in results]
        values = [c.raw_value for c in results]
        assert "PERCENT" in types
        assert "12%" in values

    def test_extracts_date(self):
        """Should extract 'Q3 2023' as a DATE claim."""
        results = extract_claims("Revenue grew by 12% in Q3 2023.")
        types = [c.entity_type for c in results]
        values = [c.raw_value for c in results]
        assert "DATE" in types
        assert "Q3 2023" in values

    def test_extracts_named_entity(self):
        """Should extract 'OpenAI' as an ORG claim."""
        results = extract_claims("OpenAI released a new model last week.")
        types = [c.entity_type for c in results]
        assert "ORG" in types

    def test_extracts_dollar_amount(self):
        """Should extract '$12.5M' as a MONEY claim."""
        results = extract_claims("The company raised $12.5M in funding.")
        types = [c.entity_type for c in results]
        assert "MONEY" in types

    def test_empty_string(self):
        """Empty input should return empty list."""
        assert extract_claims("") == []

    def test_multiple_claims_in_one_sentence(self):
        """Should extract all claims from sentence with percent, date, and person."""
        results = extract_claims("Revenue grew by 12% in Q3 2023 under Tim Cook.")
        assert len(results) >= 3
        types = [c.entity_type for c in results]
        assert "PERCENT" in types
        assert "DATE" in types
        assert "PERSON" in types
