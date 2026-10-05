from rapidfuzz import fuzz
from anchor.splitter import split_sentences
from anchor.extractor import extract_claims
from anchor.comparator import compare_claims
from anchor.config import AnchorConfig
from anchor.scorer import build_report, VerificationReport


# Abbreviation/synonym map — expand before chunk matching
# Ensures "R&D" matches "research and development" etc.
_SYNONYMS = {
    r"r&d": "research and development",
    r"ceo": "chief executive officer",
    r"ai": "artificial intelligence",
    r"ml": "machine learning",
    r"ipo": "initial public offering",
}


def _normalize_text(text: str) -> str:
    """Expand abbreviations for better chunk matching."""
    import re
    result = text.lower()
    for abbr, full in _SYNONYMS.items():
        result = re.sub(abbr, full, result, flags=re.IGNORECASE)
    return result


def _find_best_chunk(sentence: str, source_chunks: list[dict]) -> dict | None:
    """
    Find the most relevant source chunk for a given sentence.
    Uses fuzzy token set ratio on normalized text.
    Requires minimum score of 40 to avoid matching completely unrelated chunks.
    """
    if not source_chunks:
        return None

    best_score = -1
    best_chunk = None

    sentence_normalized = _normalize_text(sentence)

    for chunk in source_chunks:
        chunk_text = _normalize_text(chunk.get("text", ""))
        if not chunk_text:
            continue

        score = fuzz.token_set_ratio(sentence_normalized, chunk_text)

        if score > best_score:
            best_score = score
            best_chunk = chunk

    # Only return a chunk if it's reasonably relevant
    # Below 40 means no meaningful overlap — don't force a bad match
    if best_score < 40:
        return None

    return best_chunk


def verify(
    generated_text: str,
    source_chunks: list[dict],
    config: AnchorConfig | None = None,
) -> VerificationReport:

    if config is None:
        config = AnchorConfig()

    if not generated_text or not generated_text.strip():
        return build_report([])

    if not source_chunks:
        return build_report([])

    sentences = split_sentences(generated_text)

    results = []
    for sentence in sentences:
        best_chunk = _find_best_chunk(sentence, source_chunks)

        if best_chunk is None:
            all_source_claims = []
            for chunk in source_chunks:
                chunk_text = chunk.get("text", "")
                if chunk_text:
                    all_source_claims.extend(extract_claims(chunk_text))
        else:
            all_source_claims = extract_claims(best_chunk.get("text", ""))

        sentence_claims = extract_claims(sentence)
        result = compare_claims(
            sentence_claims=sentence_claims,
            source_claims=all_source_claims,
            sentence=sentence,
            fuzzy_threshold=config.fuzzy_match_threshold,
        )
        results.append(result)

    return build_report(results)
