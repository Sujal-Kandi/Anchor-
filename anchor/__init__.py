"""
Anchor — Sentence-Level RAG Grounding Verifier
===============================================
Ground every claim.

A post-generation verification layer that checks each sentence of an
LLM's RAG output against its retrieved sources, catching subtle factual
errors (wrong numbers, dates, names) that read fine but aren't true.

Quick start:
    from anchor import verify

    result = verify(
        generated_text="The company grew revenue by 18% in Q3 2023.",
        source_chunks=[
            {
                "chunk_id": "doc1_p2",
                "text": "Revenue grew by 12% in Q3 2023.",
                "source_doc": "annual_report.pdf",
                "page": 2,
            }
        ],
    )
    # result -> [{"sentence": "...", "status": "MISMATCH", "source_value": "12%", "found_value": "18%"}]
"""

from anchor.verify import verify
from anchor.config import AnchorConfig

__all__ = ["verify", "AnchorConfig"]
__version__ = "0.1.0"

