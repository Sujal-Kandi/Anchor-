"""
llm_fallback.py — Batched LLM judge for ambiguous claims
=========================================================
Handles sentences that contain no extractable structured claims
(causal statements, subjective assertions, relational claims like
"X led to Y") — the cases the deterministic comparator can't judge.

Key design decisions:
    1. BATCHED — all ambiguous sentences from one verify() call are
       grouped into a single LLM prompt, not one call per sentence.
       This keeps cost proportional to the number of ambiguous sentences,
       not the total sentence count.

    2. CONFIDENCE SIGNAL, NOT VERDICT — the LLM returns a confidence
       score per sentence. Low-confidence results are marked
       "NEEDS_HUMAN_REVIEW" rather than auto-flagged as MISMATCH.
       This keeps the false-positive rate manageable.

    3. MODEL-AGNOSTIC — works with any OpenAI-compatible API endpoint
       (OpenAI, Groq, Together.ai, Ollama local) via a simple config swap.

Known limitation:
    Even the best LLM-judge approach has ~7% false positive rate
    (per arXiv 2512.15068). This is why it's a fallback, not the
    primary path.

TODO (Phase 6):
    - Build the batch prompt template
    - Parse structured JSON response from LLM
    - Handle rate limits and API errors gracefully
    - Add cost tracking (tokens in / tokens out per batch)
"""

from anchor.comparator import ComparisonResult, VerificationStatus
from anchor.config import AnchorConfig


async def llm_judge_batch(
    sentences: list[str],
    source_chunks: list[dict],
    config: AnchorConfig,
) -> list[ComparisonResult]:
    """
    Send a batch of ambiguous sentences to an LLM judge for grounding verification.

    Args:
        sentences: Sentences with no extractable structured claims.
        source_chunks: The retrieved source chunks to check against.
        config: AnchorConfig with model choice, batch size, thresholds.

    Returns:
        A list of ComparisonResult objects, one per sentence.
    """
    # TODO: Implement in Phase 6
    raise NotImplementedError("llm_fallback.llm_judge_batch() — coming in Phase 6")
