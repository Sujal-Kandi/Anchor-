"""
api/main.py — FastAPI wrapper for Anchor
=========================================
Exposes the verify() function as a standalone REST API.

Endpoint:
    POST /verify
    Body: { "generated_text": "...", "source_chunks": [...] }
    Returns: list of ComparisonResult objects as JSON

This is a Phase 6+ concern — the library works perfectly without it.
The API layer is for teams who want to run Anchor as a sidecar service
rather than importing it directly.

TODO (Phase 6+):
    - Implement the /verify endpoint
    - Add /health endpoint
    - Add request validation via Pydantic models
    - Add basic API key auth
    - Add cost/usage tracking headers in response
"""

from fastapi import FastAPI

app = FastAPI(
    title="Anchor — RAG Grounding Verifier",
    description="Sentence-level hallucination detection for RAG pipelines.",
    version="0.1.0",
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.post("/verify")
async def verify_endpoint():
    """
    Verify generated RAG output against source chunks.
    TODO: Implement in Phase 6+
    """
    return {"error": "Not yet implemented — coming in Phase 6"}
