"""
splitter.py — Sentence tokenizer
=================================
Splits generated LLM output into individual sentences using spaCy.

Why spaCy and not naive .split('.')?
    Naive splitting breaks on:
    - Abbreviations: "Dr. Smith said..." splits after "Dr"
    - Numbers: "$12.5M grew..." splits after "12"
    - Decimals, URLs, and initials all cause false splits

    spaCy's sentence boundary detection handles all of these correctly.

Phase 1 target:
    - Load the en_core_web_sm model
    - Accept a string, return a list of sentence strings
    - Strip whitespace, drop empty strings
    - Handle edge cases: single sentence, empty input, very long inputs

TODO (Phase 2+):
    - Add language detection for non-English inputs
    - Support custom sentence boundary rules for domain-specific text
      (e.g. legal documents with numbered clauses)
"""

import spacy 
from typing import Optional 

_nlp: Optional[spacy.Language] = None 

def _get_nlp() -> spacy.Language:
    global _nlp
    if _nlp is None:
        try:
            _nlp =  spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
    return _nlp


def split_sentences(text: str) -> list[str]:
    if not text or not text.strip():
        return []

    nlp = _get_nlp()
    doc = nlp(text)

    sentences = [sent.text.strip() for sent in doc.sents]
    sentences = [s for s in sentences if s]

    return sentences
