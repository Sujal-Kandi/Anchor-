# Anchor

RAG reduces hallucinations. It does not eliminate them.

The hardest failures are often structurally small: a generated sentence
reads naturally, cites plausible context, and contains one incorrect
number, date, or name. Embedding-based checks can miss this because the
sentence remains semantically close to its source even after a value has
changed.

Anchor takes a different approach. It extracts structured values from
both a generated response and its retrieved source chunks, compares them
directly, flags mismatches, and can rewrite affected sentences using the
source value.

It is a verification layer for RAG outputs—not a complete fact-checking
system.



## What Anchor does

You provide:

- A generated RAG response.
- The source chunks retrieved for that response.

Anchor then:

1. Splits the response into sentences.
2. Extracts structured claims: numbers, dates, percentages, monetary
   amounts, names, and organisations.
3. Finds the most relevant source chunk for each sentence.
4. Extracts comparable claims from that source chunk.
5. Compares the values.
6. Returns a per-sentence verdict and an overall trust score.
7. Can rewrite a mismatched sentence using the value found in the source.

For example, if the response says:

> Revenue grew by 18% in Q3 2023.

and the retrieved source says:

> Revenue grew by 12% in Q3 2023.

Anchor flags the percentage mismatch and can rewrite the sentence to use
the source value.

## Important scope

Anchor checks **structured claims against retrieved source chunks**.

It does not determine whether:

- The retrieved chunks themselves are correct.
- The selected source chunk is the right evidence for the sentence.
- A relationship between two entities is correct.
- An unsupported qualitative or causal claim is true.

A response can pass Anchor's checks and still contain an unsupported
claim if that claim has no comparable structured value in the source.

## Evaluation

Anchor was evaluated on **40 synthetic test cases**:

- 20 clean responses.
- 20 responses with injected mismatches across numbers, dates, and names.

| Metric | Result |
|---|---|
| Injected-mismatch recall | 100% |
| False-positive rate | 0% |
| Average verification time | 0.16 seconds per case after model loading |

These results describe performance on this small, purpose-built test
set. They do not establish accuracy on open-ended production RAG data,
complex multi-hop questions, or every type of factual error.

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

print(report.results.status)
# MISMATCH

print(report.results.found_value, "->", report.results.source_value)
# 89.5 -> 119.6

corrected_response = auto_correct(report)
print(corrected_response)
# Apple reported revenue of $119.6 billion in Q1 2024.
```

`auto_correct()` replaces mismatched structured values with the values
found in the retrieved source and returns the full corrected response.
```

## Installation

```bash
pip install anchor-verify
python -m spacy download en_core_web_sm
```

Or install from source:

```bash
git clone [https://github.com/Sujal-Kandi/Anchor-.git](https://github.com/Sujal-Kandi/Anchor-.git)
cd Anchor-
pip install -e ".[dev]"
python -m spacy download en_core_web_sm
```

## Use it in a RAG pipeline

Anchor sits between generation and the response returned to the user.

```python
from anchor import verify
from anchor.scorer import auto_correct

docs = retriever.get_relevant_documents(query)
response = llm.invoke(docs + query)

source_chunks = [
    {
        "chunk_id": str(i),
        "text": doc.page_content,
        "source_doc": doc.metadata.get("source", ""),
        "page": doc.metadata.get("page", 1)
    }
    for i, doc in enumerate(docs)
]

report = verify(generated_text=response, source_chunks=source_chunks)

if report.trust_score < 80:
    return "I'm not confident enough in this answer."

corrected_response = auto_correct(report)
return corrected_response
```

`auto_correct()` returns the full response with detected mismatched
structured values replaced by their source values.

You can also use the verification report directly if you prefer to block,
regenerate, or route low-confidence responses to human review instead of
automatically correcting them.

### LlamaIndex-style integration

```python
from anchor import verify

source_chunks = [
    {
        "chunk_id": str(i),
        "text": node.get_content(),
        "source_doc": node.metadata.get("file_name", ""),
        "page": node.metadata.get("page_label", 1)
    }
    for i, node in enumerate(retrieved_nodes)
]

report = verify(
    generated_text=response,
    source_chunks=source_chunks
)
```

The integration pattern is the same: convert retrieved content into
Anchor's source-chunk format, run verification, then decide whether to
return, block, regenerate, or send the response for human review.

## How verification works

### 1. Sentence segmentation

Anchor uses spaCy to split generated text into sentences.

This avoids simplistic splitting on full stops, which can incorrectly
break abbreviations such as `Dr.` or decimal values such as `$12.5M`.

### 2. Claim extraction

For each sentence, Anchor extracts structured values:

- Numbers.
- Percentages.
- Dates and years.
- Monetary amounts.
- Person names.
- Organisations.

It uses a local BERT NER model for names and organisations, and spaCy
for numeric entities.

### 3. Source matching

Anchor selects the most relevant source chunk for each generated
sentence, extracts comparable claims from it, and compares the values.

This is a retrieval-and-comparison heuristic. It does not prove that the
selected chunk is the only relevant evidence or the best evidence for
the sentence.

### 4. Value comparison

Numbers, dates, percentages, and monetary values are compared exactly.
`18%` and `12%` are not treated as equivalent.

Names and organisations use fuzzy matching so variants such as
`Tim Cook` and `Timothy Cook` can be treated as the same entity.

Fuzzy matching reduces false positives, but it can also miss
relationships or distinctions between similarly named entities.

## Result format

```json
{
  "sentence": "Revenue grew by 18% in Q3 2023.",
  "status": "MISMATCH",
  "found_value": "18%",
  "source_value": "12%",
  "claim_type": "PERCENT"
}
```

| Status | Meaning |
|---|---|
| `GROUNDED` | Every extractable structured claim matched a comparable source claim. |
| `MISMATCH` | At least one comparable source claim has a different value. |
| `UNVERIFIABLE` | The sentence contains claims, but no comparable claim type was found in the source. |
| `NO_CLAIMS` | No structured claims were extracted from the sentence. |

`NO_CLAIMS` is not an error. It means the sentence is qualitative,
causal, or otherwise lacks structured values that the current
deterministic pipeline can compare.

The current version does not automatically route these sentences to an
LLM fallback.




## Configuration

```python
from anchor import verify, AnchorConfig

config = AnchorConfig(
    fuzzy_match_threshold=85,
    llm_fallback_enabled=False
)

report = verify(
    generated_text=text,
    source_chunks=source_chunks,
    config=config
)
```

## What it catches

Anchor is designed to catch direct value mismatches, including:

- Incorrect numbers.
- Incorrect percentages.
- Incorrect dates, years, and quarters.
- Incorrect monetary amounts.
- Incorrect person names.
- Incorrect organisation names.

These are useful checks because a single changed value can make a fluent
sentence factually wrong.

## What it does not catch

Anchor does not fully solve hallucination detection.

It does not reliably catch:

- Paraphrased contradictions.
- Incorrect causal claims.
- Unsupported qualitative statements.
- Incorrect relationships between entities.
- Claims where the correct source evidence was not retrieved.
- Errors in the source documents themselves.

For example, this sentence contains no structured value to compare:

> The company grew revenue because it expanded into new markets.

Anchor cannot determine from value comparison alone whether that causal
explanation is supported.

An LLM-based fallback for ambiguous or non-structured claims is planned,
but it is not part of the current deterministic pipeline.

## Why not embeddings alone?

Embeddings measure semantic similarity.

These two sentences are very close in embedding space:

> Revenue grew by 18% in Q3 2023.  
> Revenue grew by 12% in Q3 2023.

A small value change may not move the embedding enough to trigger a
similarity-based warning.

Anchor compares the extracted values directly. `18` and `12` are not
equal.

Embeddings and deterministic checks solve different problems. Anchor
focuses on the second: exact mismatches in structured claims.

## Local execution

Anchor runs locally.

- The BERT NER model and spaCy model run on your machine.
- Verification does not send your text to an external API.
- There are no per-verification API costs.

The BERT model is downloaded once on first use, cached locally, and
reused afterwards.

The first verification call includes model-loading time. Subsequent
calls are faster. For a service, load the models once during startup
rather than per request.

## Project status

Anchor is an active project.

The deterministic verification workflow works end to end. Planned work
includes:

- LLM fallback for qualitative and causal claims.
- Better source-chunk selection and multi-chunk evidence handling.
- Relationship-level verification.
- Evaluation on realistic, non-synthetic RAG datasets.
- More detailed reporting for partial matches and conflicting evidence.

## Performance

On my machine, verification took approximately **0.16 seconds per case**
after the models were loaded.

The first call takes approximately **5–6 seconds** because the local
models need to load into memory. Subsequent calls are faster.

For a service, load the models once during startup rather than loading
them for every request.

These timings were measured locally and will vary by hardware, model
loading state, input length, and number of source chunks.

## Future work: LLM fallback

An LLM-based fallback for qualitative, causal, and ambiguous claims is a
planned future feature. It is **not implemented** in the current version.

The current pipeline uses deterministic extraction and comparison for
structured claims. It does not verify unsupported qualitative statements
or causal explanations.

## License

MIT
