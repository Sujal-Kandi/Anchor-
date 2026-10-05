# Anchor — Build Journey

> A public log of how this project was built, decision by decision.
> Updated at the end of every phase.

---

## Why This Exists

Most projects show up on GitHub already finished. No one sees the thinking behind it — why certain decisions were made, what was tried and failed, what the numbers actually looked like before the README got polished.

This file is the unfiltered version. Every phase logged as it happened.

---

## The Idea

RAG pipelines reduce hallucination but don't eliminate it. The errors that survive are subtle — a swapped percentage, a wrong date, a name that almost matches. Embedding-based grounding checks miss them completely because the sentence stays semantically similar to the source after the swap.

Anchor catches those by extracting the actual structured claims (numbers, dates, entities) and comparing them directly against the source — no vector math, no LLM needed for the common case.

**The specific gap it fills:** fast, cheap, inline, API-model-compatible verification that catches numeric/entity-level swaps — sitting between "fast but blind" (embeddings) and "accurate but expensive" (LLM-per-sentence).

---

## Phase Log

---

### Phase 1 — Project Scaffold
**Date:** October 2, 2026
**Goal:** Set up the project structure cleanly before writing any real logic.

**What was built:**
- Full folder structure: `anchor/`, `tests/`, `examples/`, `benchmarks/`, `api/`
- `pyproject.toml` with pinned dependencies and project metadata
- `requirements.txt` with exact versions
- Placeholder source files — each with a full docstring explaining what it will do and why:
  - `splitter.py` — spaCy sentence tokenizer
  - `extractor.py` — HuggingFace NER claim extraction
  - `comparator.py` — deterministic claim comparison
  - `llm_fallback.py` — batched LLM judge for ambiguous claims
  - `verify.py` — main orchestrator
  - `config.py` — tunable thresholds via Pydantic
  - `utils.py` — normalization helpers
- Test file skeletons for each module (tests skip with clear Phase labels)
- `tests/fixtures/sample_reports.json` — 3 hand-crafted fixtures (1 clean, 2 injected mismatches)
- `api/main.py` — FastAPI placeholder
- `examples/research_agent_demo.py` — placeholder for Phase 7 demo
- `README.md` — full skeleton with problem statement, quick start, status table
- `.gitignore`

**Decisions made:**
- spaCy over NLTK for sentence splitting — handles abbreviations and decimals correctly, NLTK doesn't
- `dslim/bert-base-NER` chosen for Phase 3 — small, fast, runs locally, no API call required
- Pydantic for config — gives free validation and IDE autocomplete on thresholds
- LLM fallback disabled by default — don't pay for it unless you need it
- Batching ambiguous sentences into one LLM call instead of one per sentence — keeps fallback cost proportional

**What's NOT done yet (intentionally):**
- No actual logic implemented — every function raises `NotImplementedError`
- No dependencies installed yet — that happens when Phase 2 starts

**Phase 1 status: ✅ Complete**

---

### Phase 2 — Sentence Splitter
**Date:** October 5, 2026
**Status:** ✅ Complete

**Goal:** Get `splitter.split_sentences()` working correctly against real text.

**What was built:**
- `_get_nlp()` — loads and caches the spaCy model once, reuses across all calls
- `split_sentences()` — splits any text into clean sentences using spaCy
- Handles edge cases: empty string, whitespace-only, abbreviations, decimals
- 7 tests written and passing in `tests/test_splitter.py`

**Test results:** 7/7 passing

**Decisions made:**
- spaCy over NLTK — handles abbreviations (Dr., Mr.) and decimals ($12.5M) correctly
- Module-level model cache (`_nlp`) — spaCy model loads once, not on every function call
- `text.strip()` check before processing — avoids passing whitespace to spaCy unnecessarily
- List comprehension to strip and filter — clean, readable, no empty strings in output

**Tradeoffs:**
- spaCy is heavier than NLTK (~50MB model download) — worth it for correctness
- en_core_web_sm is the small model, slightly less accurate than en_core_web_lg — fast enough for our use case

---

### Phase 8 — Benchmarks
Date: October 5, 2026
Status: Done

Built a 40-case benchmark — 20 clean outputs, 20 with injected mismatches across numbers, dates, percentages, years, and names.

Final numbers: 100% accuracy, 100% recall, 0% false positive rate, 0.16s per case.

Getting there took several iterations. Started at 85% accuracy. The failures were all normalization and type inconsistency bugs — spaCy tagging large numbers as DATE instead of CARDINAL, BERT tagging abbreviations like R&D as ORG, year-only dates not matching against month+year dates, quarter dates matching too loosely. Fixed each one by understanding exactly what the models were returning and handling the edge case explicitly.

The biggest insight from this phase: the hardest bugs weren't logic bugs. They were model output bugs. The models don't always tag things the way you'd expect and you have to handle that at the boundary, not deep inside the logic.

19/19 unit tests passing alongside 40/40 benchmark cases.

---

### Phase 4 — Comparator
**Status:** ⏳ Planned

---

### Phase 5 — verify() Orchestrator
**Status:** ⏳ Planned

---

### Phase 6 — LLM Fallback
**Status:** ⏳ Planned

---

### Phase 7 — Demo + Benchmarks
**Status:** ⏳ Planned

---

## Lessons Learned

> Updated as the build progresses.

- **Phase 1:** Writing docstrings before the implementation forces clarity on what each function actually needs to do. Recommended — it surfaces interface questions before you're deep in code.

---

## Numbers

> Real benchmark results as they come in. No polish, just the actual numbers.

| Phase | Metric | Result |
|---|---|---|
| 7 | Recall on injected loops | TBD |
| 7 | False positive rate | TBD |

