# Anchor

RAG doesn't actually fix hallucinations. It reduces them. The ones that survive are the hard kind — a sentence that reads perfectly fine but has one wrong fact buried inside. A swapped percentage. A wrong year. A name that almost matches.

Embedding checks miss these completely. The sentence stays semantically similar to the source after the swap, so cosine similarity says it's fine. It's not fine.

Anchor catches them by extracting the actual numbers, dates, and names from both the generated text and the source chunks, then comparing them directly. No vectors. No approximations. Just the real values side by side.

---

## What it actually does

You pass in a generated RAG response and the source chunks that were retrieved. Anchor splits the response into sentences, pulls out every structured claim in each sentence, finds the matching source chunk, and checks whether the values match.

If a sentence says "revenue grew 18%" and the source says "revenue grew 12%", Anchor flags it, tells you what was found versus what the source says, and rewrites the sentence with the correct value automatically.

Every sentence gets a verdict. The whole response gets a trust score out of 100. You can set a threshold and decide what to do — show it, block it, regenerate, route to human review.

---

## Numbers

Tested on 40 cases. 20 clean outputs, 20 with injected mismatches across numbers, dates, and names.

- Recall: 100% — every injected mismatch caught
- False positive rate: 0% — no clean sentence wrongly flagged
- Speed: 0.16 seconds per case after models load

---

## Quick start

```python
from anchor import verify
from anchor.scorer import auto_correct

report = verify(
    generated_text="Apple reported revenue of $89.5 billion in Q1 2024.",
    source_chunks=[{
        "chunk_id": "1",
        "text": "Apple reported revenue of $119.6 billion in Q1 2024.",
        "source_doc": "earnings.pdf",
        "page": 3
    }]
)

print(report.trust_score)
# 0

print(report.results[0].status)
# MISMATCH

print(report.results[0].found_value, "->", report.results[0].source_value)
# 89.5 -> 119.6

print(auto_correct(report.results[0]))
# Apple reported revenue of $119.6 billion in Q1 2024.
```

---

## Installation

```bash
pip install anchor-verify
python -m spacy download en_core_web_sm
```

Or from source:

```bash
git clone https://github.com/Sujal-Kandi/anchor
cd anchor
pip install -e ".[dev]"
python -m spacy download en_core_web_sm
```

---

## How it works

The pipeline has four steps.

First it splits the generated text into sentences using spaCy. Not a naive split on periods — spaCy handles abbreviations and decimal numbers correctly so "Dr. Smith" and "$12.5M" don't get split in the wrong place.

Then for each sentence it extracts structured claims. Numbers, dates, percentages, money amounts, names, organizations. It uses two models for this — a BERT NER model for names and organizations, and spaCy for numeric entities. Each model is better at what it does.

Then it finds the most relevant source chunk for that sentence and extracts the same types of claims from it.

Then it compares. Numbers and dates use exact matching — "12%" and "18%" are just not equal, no approximation needed. Names use fuzzy matching because "Tim Cook" and "Timothy Cook" should be treated as the same person. If anything doesn't match, it's flagged immediately with the found value and what the source actually says.

Sentences with no extractable structured claims get a NO_CLAIMS verdict. That's not an error — it means the sentence is probably a causal or subjective statement that the deterministic pipeline can't verify. A future LLM fallback will handle those.

---

## What each result looks like

```python
{
    "sentence": "Revenue grew by 18% in Q3 2023.",
    "status": "MISMATCH",
    "found_value": "18%",
    "source_value": "12%",
    "claim_type": "PERCENT"
}
```

Status can be GROUNDED, MISMATCH, UNVERIFIABLE, or NO_CLAIMS.

GROUNDED means every extractable claim in the sentence matched a source claim.
MISMATCH means at least one claim was found in the source but the values don't match.
UNVERIFIABLE means the sentence has claims but none of the claim types appeared in the source at all.
NO_CLAIMS means no structured claims were extracted — routes to LLM fallback if enabled.

---

## Configuration

```python
from anchor import verify, AnchorConfig

config = AnchorConfig(
    fuzzy_match_threshold=85,
    llm_fallback_enabled=False,
)

report = verify(generated_text, source_chunks, config=config)
```

---

## What it catches and what it doesn't

It catches wrong numbers, wrong percentages, wrong dates, wrong years, wrong quarters, wrong names, wrong organizations. These are the most common and most dangerous hallucinations in RAG outputs — they read fluently and look correct until you check the source.

It doesn't catch paraphrased contradictions or causal errors. "The company grew revenue" versus "the company lost revenue" — no numbers to extract, nothing to compare. That's what the LLM fallback is for and it's not built yet.

---

## Why not just use embeddings

Embeddings compare meaning. "Revenue grew by 18%" and "Revenue grew by 12%" are nearly identical in embedding space — one token changed, no semantic difference. Cosine similarity will tell you they're the same. They're not.

Anchor extracts the actual values. 18 and 12 are not equal. That's the whole idea.

---

## Project status

This is an active build documented publicly as it's built. The library works end to end. LLM fallback for ambiguous claims is the next thing being built.

Built by Sujal Kandi. If you're using this or have feedback, open an issue or reach out.

---

## License

MIT
