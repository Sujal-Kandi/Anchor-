import re
from dataclasses import dataclass
from transformers import pipeline
import spacy

_ner_pipeline = None
_nlp = None


def _get_ner():
    global _ner_pipeline
    if _ner_pipeline is None:
        _ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple",
        )
    return _ner_pipeline


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


@dataclass
class Claim:
    entity_type: str
    raw_value: str
    normalized_value: str
    char_start: int
    char_end: int


def _normalize_written_numbers(text: str) -> str:
    """Convert written large numbers to numeric form before NER."""
    multipliers = {
        "trillion": 1_000_000_000_000,
        "billion":  1_000_000_000,
        "million":  1_000_000,
        "thousand": 1_000,
    }
    for word, mult in multipliers.items():
        pattern = rf'(\d+(?:\.\d+)?)\s+{word}'
        def replace(m, mult=mult):
            return str(int(float(m.group(1)) * mult))
        text = re.sub(pattern, replace, text, flags=re.IGNORECASE)
    return text


def extract_claims(text: str) -> list[Claim]:
    if not text or not text.strip():
        return []

    text_for_spacy = _normalize_written_numbers(text)
    claims = []

    # --- BERT NER: names, orgs, locations ---
    ner = _get_ner()
    entities = ner(text)

    allowed_raw_types = {"PER", "ORG", "LOC", "MISC"}
    label_map = {"PER": "PERSON", "LOC": "GPE", "ORG": "ORG", "MISC": "MISC"}

    for ent in entities:
        entity_type_raw = ent["entity_group"].upper()
        if entity_type_raw not in allowed_raw_types:
            continue

        entity_type = label_map.get(entity_type_raw, entity_type_raw)
        raw = ent["word"].strip().replace("##", "")

        if not raw or len(raw) < 2:
            continue

        # Skip abbreviation-style ORG tags — R&D, CEO, AI etc.
        if entity_type == "ORG" and len(raw) <= 5 and raw.replace("&", "").replace(" ", "").isupper():
            continue

        claims.append(Claim(
            entity_type=entity_type,
            raw_value=raw,
            normalized_value=raw.lower(),
            char_start=ent["start"],
            char_end=ent["end"],
        ))

    # --- spaCy: numbers, dates, money, percent ---
    nlp = _get_nlp()
    doc = nlp(text_for_spacy)
    spacy_types = {"CARDINAL", "DATE", "MONEY", "PERCENT", "QUANTITY", "ORDINAL"}

    for ent in doc.ents:
        if ent.label_ not in spacy_types:
            continue

        raw = ent.text.strip()
        if not raw:
            continue

        if ent.label_ == "CARDINAL":
            all_numbers = re.findall(r'[\d]+(?:\.\d+)?', raw)
            if all_numbers:
                raw = all_numbers[-1]
            else:
                continue
            try:
                if float(raw) < 2 and "." not in raw:
                    continue
            except ValueError:
                continue

        claims.append(Claim(
            entity_type=ent.label_,
            raw_value=raw,
            normalized_value=raw.lower(),
            char_start=ent.start_char,
            char_end=ent.end_char,
        ))

    # --- Extra pass: catch unit-attached numbers (4nm, 7nm, 3.35TB) ---
    existing_starts = {c.char_start for c in claims}
    unit_pattern = re.finditer(
        r'\b(\d+(?:\.\d+)?)\s*(?:nm|um|mm|kb|mb|gb|tb|pb|w|khz|mhz|ghz|thz|v|a|n)\b',
        text_for_spacy, re.IGNORECASE
    )
    for match in unit_pattern:
        if match.start() not in existing_starts:
            raw = match.group(1)
            claims.append(Claim(
                entity_type="CARDINAL",
                raw_value=raw,
                normalized_value=raw.lower(),
                char_start=match.start(),
                char_end=match.end(),
            ))

    # --- Extra pass: catch very large normalized numbers spaCy misses ---
    existing_values = {c.normalized_value for c in claims}
    large_pattern = re.finditer(r'\b(\d{9,}(?:\.\d+)?)\b', text_for_spacy)
    for match in large_pattern:
        raw = match.group(1)
        if raw not in existing_values:
            claims.append(Claim(
                entity_type="CARDINAL",
                raw_value=raw,
                normalized_value=raw,
                char_start=match.start(),
                char_end=match.end(),
            ))

    return claims
