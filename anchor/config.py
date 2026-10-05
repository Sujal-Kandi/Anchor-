"""
config.py — Anchor configuration layer
=======================================
Centralizes all tunable thresholds so behavior can be adjusted
per pipeline without touching core logic.

Thresholds:
    - fuzzy_match_threshold: minimum similarity score (0-100) for
      fuzzy string matching during comparisons. Lower = more lenient.
    - llm_fallback_enabled: whether to use LLM-judge for ambiguous
      claims that have no extractable structured data.
    - llm_fallback_model: which model to call for the fallback judge.
    - batch_size: how many ambiguous sentences to batch into one
      LLM fallback call (keeps costs low).
    - confidence_threshold: minimum LLM confidence to treat a
      fallback verdict as actionable vs. "needs human review".
"""

from pydantic import BaseModel, Field


class AnchorConfig(BaseModel):
    """Configuration for the Anchor verify pipeline."""

    # Comparator settings
    fuzzy_match_threshold: int = Field(
        default=85,
        ge=0,
        le=100,
        description="Minimum rapidfuzz similarity score to count as a match (0-100).",
    )

    # LLM fallback settings
    llm_fallback_enabled: bool = Field(
        default=False,
        description="Enable LLM-judge fallback for ambiguous/causal claims. Phase 2+.",
    )
    llm_fallback_model: str = Field(
        default="gpt-4o-mini",
        description="Model to use for batched LLM fallback calls.",
    )
    batch_size: int = Field(
        default=10,
        ge=1,
        description="Max sentences per LLM fallback batch call.",
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum LLM confidence score to treat verdict as actionable.",
    )
