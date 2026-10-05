"""
Tests for anchor.comparator — deterministic claim comparison.

Phase 4 tests. This is where the core "18% vs 12%" catch gets validated.
"""

from anchor.extractor import extract_claims
from anchor.comparator import compare_claims, VerificationStatus


class TestCompareClaims:
    """Tests for the compare_claims() function."""

    def test_matching_percentage_is_grounded(self):
        """'12%' in sentence matching '12%' in source -> GROUNDED."""
        sentence = "Revenue grew by 12% in Q3 2023."
        source = "Revenue grew by 12% in Q3 2023."
        result = compare_claims(extract_claims(sentence), extract_claims(source), sentence)
        assert result.status == VerificationStatus.GROUNDED

    def test_mismatched_percentage_is_flagged(self):
        """'18%' in sentence vs '12%' in source -> MISMATCH with correct values."""
        sentence = "Revenue grew by 18% in Q3 2023."
        source = "Revenue grew by 12% in Q3 2023."
        result = compare_claims(extract_claims(sentence), extract_claims(source), sentence)
        assert result.status == VerificationStatus.MISMATCH
        assert result.found_value == "18%"
        assert result.source_value == "12%"
        assert result.claim_type == "PERCENT"

    def test_mismatched_date_is_flagged(self):
        """'Q1 2024' vs 'Q3 2024' in source -> MISMATCH."""
        sentence = "The product launched in Q1 2024."
        source = "The product launched in Q3 2024."
        result = compare_claims(extract_claims(sentence), extract_claims(source), sentence)
        assert result.status == VerificationStatus.MISMATCH

    def test_no_claims_returns_no_claims(self):
        """Sentence with no structured claims -> NO_CLAIMS status."""
        sentence = "The policy led to significant changes."
        source = "The policy led to significant changes."
        result = compare_claims(extract_claims(sentence), extract_claims(source), sentence)
        assert result.status == VerificationStatus.NO_CLAIMS

    def test_empty_sentence_claims(self):
        """Empty sentence claims list -> NO_CLAIMS."""
        result = compare_claims([], [], "Some sentence.")
        assert result.status == VerificationStatus.NO_CLAIMS

    def test_matching_person_is_grounded(self):
        """Same person name in sentence and source -> GROUNDED."""
        sentence = "Tim Cook confirmed the results."
        source = "Tim Cook confirmed the quarterly results in a press release."
        result = compare_claims(extract_claims(sentence), extract_claims(source), sentence)
        assert result.status == VerificationStatus.GROUNDED
