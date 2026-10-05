"""
utils.py — Shared helpers
==========================
Utility functions used across the Anchor pipeline.

Normalization is critical here — the comparator will produce false
mismatches if "$340 million" and "340M" aren't resolved to the same
value before comparison. These helpers handle that.

Functions planned:
    normalize_number(text) -> float | None
        "$340 million" -> 340000000.0
        "12%"          -> 0.12  (or keep as 12.0 with "%" flag?)
        "1.2B"         -> 1200000000.0
        "three"        -> 3.0  (word-to-number)

    normalize_date(text) -> str | None
        "Q3 2023"            -> "2023-Q3"
        "January 2024"       -> "2024-01"
        "third quarter 2023" -> "2023-Q3"

    chunk_to_text(chunk) -> str
        Extracts the plain text field from a source chunk dict,
        handles missing keys gracefully.

TODO (Phase 3+):
    - Implement normalize_number with word2number + unit multipliers
    - Implement normalize_date with dateparser library
    - Add chunk_to_text helper
"""


def normalize_number(text: str) -> float | None:
    """
    Normalize a numeric string to a float for comparison.

    Args:
        text: Raw numeric text e.g. "$340 million", "12%", "1.2B"

    Returns:
        Normalized float value, or None if parsing fails.

    Examples:
        >>> normalize_number("$340 million")
        340000000.0
        >>> normalize_number("12%")
        12.0
        >>> normalize_number("1.2B")
        1200000000.0
    """
    # TODO: Implement in Phase 3
    raise NotImplementedError("utils.normalize_number() — coming in Phase 3")


def normalize_date(text: str) -> str | None:
    """
    Normalize a date string to a standard format for comparison.

    Args:
        text: Raw date text e.g. "Q3 2023", "January 2024"

    Returns:
        Normalized date string e.g. "2023-Q3", "2024-01", or None if parsing fails.
    """
    # TODO: Implement in Phase 3
    raise NotImplementedError("utils.normalize_date() — coming in Phase 3")


def chunk_to_text(chunk: dict) -> str:
    """
    Safely extract plain text from a source chunk dict.

    Args:
        chunk: A source chunk with at minimum a "text" key.

    Returns:
        The text content of the chunk, or empty string if missing.
    """
    # TODO: Implement in Phase 3
    raise NotImplementedError("utils.chunk_to_text() — coming in Phase 3")
