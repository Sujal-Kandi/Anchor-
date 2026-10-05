"""
Tests for anchor.splitter — sentence tokenization.

These tests will be filled in during Phase 2 when split_sentences() is implemented.
Fixtures defined here already so the test structure is ready to run.
"""

import pytest
from anchor.splitter import split_sentences


class TestSplitSentences:
    """Tests for the split_sentences() function."""

    def test_single_sentence(self):
        """A single sentence should return a list with one item."""
        result = split_sentences("The company raised $12.5M.")
        assert len(result) == 1
        assert result[0] == "The company raised $12.5M."

    def test_multiple_sentences(self):
        """Standard multi-sentence text should split correctly."""
        result = split_sentences(
            "Revenue grew by 12% in Q3 2023. The CEO confirmed the results."
        )
        assert len(result) == 2
        assert result[0] == "Revenue grew by 12% in Q3 2023."
        assert result[1] == "The CEO confirmed the results."

    def test_abbreviation_not_split(self):
        """'Dr. Smith said...' should NOT split after 'Dr.'"""
        result = split_sentences("Dr. Smith confirmed the results were accurate.")
        assert len(result) == 1

    def test_decimal_number_not_split(self):
        """'$12.5M' should NOT split after '12.'"""
        result = split_sentences(
            "Revenue grew by 12% in Q3 2023. The company raised $12.5M."
        )
        assert len(result) == 2
        assert "12.5M" in result[1]

    def test_empty_string(self):
        """Empty input should return an empty list."""
        assert split_sentences("") == []

    def test_whitespace_only(self):
        """Whitespace-only input should return an empty list."""
        assert split_sentences("   ") == []

    def test_whitespace_stripped(self):
        """Returned sentences should have no leading/trailing whitespace."""
        result = split_sentences("Revenue grew by 12%.  The CEO confirmed this.")
        for sentence in result:
            assert sentence == sentence.strip()
