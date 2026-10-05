import re
from dataclasses import dataclass
from enum import Enum
from rapidfuzz import fuzz
from anchor.extractor import Claim


class VerificationStatus(str, Enum):
    GROUNDED = "GROUNDED"
    MISMATCH = "MISMATCH"
    UNVERIFIABLE = "UNVERIFIABLE"
    NO_CLAIMS = "NO_CLAIMS"


@dataclass
class ComparisonResult:
    sentence: str
    status: VerificationStatus
    source_value: str | None = None
    found_value: str | None = None
    claim_type: str | None = None


def _extract_numeric(text: str) -> str:
    """
    Strip non-numeric characters and extract just the number.
    '4nm' -> '4'
    '80000000000' -> '80000000000'
    '3.35' -> '3.35'
    Allows comparison of values regardless of unit suffix.
    """
    match = re.search(r'[\d,]+(?:\.\d+)?', text.replace(",", ""))
    return match.group(0) if match else text


def _normalize_entity_type(entity_type: str, raw_value: str) -> str:
    """
    Normalize entity types for comparison.
    spaCy sometimes tags large numbers as DATE or MONEY instead of CARDINAL.
    We unify all numeric types to CARDINAL for comparison purposes.
    Year-only values (2013, 2024) stay as DATE — they are temporal, not quantities.
    """
    numeric_types = {"CARDINAL", "MONEY", "QUANTITY", "PERCENT", "ORDINAL"}
    if entity_type in numeric_types:
        return "CARDINAL"
    if entity_type == "DATE":
        cleaned = re.sub(r'[,\s]', '', raw_value)
        # Pure digit — but if it looks like a year (4 digits, 1900-2100), keep as DATE
        if cleaned.replace('.', '').isdigit():
            try:
                val = float(cleaned)
                if 1900 <= val <= 2100:
                    return "DATE"  # It's a year — keep as DATE
            except ValueError:
                pass
            return "CARDINAL"
    return entity_type


def compare_claims(
    sentence_claims: list[Claim],
    source_claims: list[Claim],
    sentence: str,
    fuzzy_threshold: int = 85,
) -> ComparisonResult:

    if not sentence_claims:
        return ComparisonResult(
            sentence=sentence,
            status=VerificationStatus.NO_CLAIMS,
        )

    for s_claim in sentence_claims:
        s_type = _normalize_entity_type(s_claim.entity_type, s_claim.raw_value)
        matching_source = [
            c for c in source_claims
            if _normalize_entity_type(c.entity_type, c.raw_value) == s_type
        ]

        if not matching_source:
            continue

        matched = False
        for src_claim in matching_source:
            if s_type in {"PERSON", "ORG", "GPE"}:
                score = fuzz.ratio(
                    s_claim.normalized_value,
                    src_claim.normalized_value,
                )
                if score >= fuzzy_threshold:
                    matched = True
                    break
            elif s_type == "DATE":
                if s_claim.normalized_value == src_claim.normalized_value:
                    matched = True
                    break

                s_val = s_claim.normalized_value
                src_val = src_claim.normalized_value

                # Extract quarters if present — Q1/Q2/Q3/Q4
                quarter_pattern = r'\b(q[1-4])\b'
                s_quarters = re.findall(quarter_pattern, s_val, re.IGNORECASE)
                src_quarters = re.findall(quarter_pattern, src_val, re.IGNORECASE)

                # Extract months
                months = ["january","february","march","april","may","june",
                          "july","august","september","october","november","december",
                          "jan","feb","mar","apr","jun","jul","aug","sep","oct","nov","dec"]
                s_months = [m for m in months if m in s_val]
                src_months = [m for m in months if m in src_val]

                # Extract years
                s_years = re.findall(r'\b(1[89]\d{2}|20\d{2})\b', s_val)
                src_years = re.findall(r'\b(1[89]\d{2}|20\d{2})\b', src_val)

                if s_quarters and src_quarters:
                    # Quarter comparison — must match both quarter AND year
                    q_match = s_quarters[0].lower() == src_quarters[0].lower()
                    y_match = (s_years and src_years and s_years[0] == src_years[0]) or (not s_years and not src_years)
                    if q_match and y_match:
                        matched = True
                        break
                elif s_months and src_months:
                    # Month comparison — must match both month AND year
                    if s_months[0] == src_months[0] and s_years and src_years and s_years[0] == src_years[0]:
                        matched = True
                        break
                elif s_years and src_years and not s_months and not src_months and not s_quarters and not src_quarters:
                    # Year-only comparison on both sides
                    if s_years[0] == src_years[0]:
                        matched = True
                        break
                elif s_years and src_years:
                    # Mixed: one has month/quarter, other is year-only
                    # Compare years — if years differ it's a mismatch
                    # If years match, treat as grounded (month adds context, not contradiction)
                    if s_years[0] == src_years[0]:
                        matched = True
                        break
                else:
                    score = fuzz.token_sort_ratio(s_val, src_val)
                    if score >= 95:
                        matched = True
                        break
            else:
                s_num = _extract_numeric(s_claim.normalized_value)
                src_num = _extract_numeric(src_claim.normalized_value)
                if s_num == src_num:
                    matched = True
                    break

        if not matched:
            best_source = matching_source[0]
            return ComparisonResult(
                sentence=sentence,
                status=VerificationStatus.MISMATCH,
                source_value=best_source.raw_value,
                found_value=s_claim.raw_value,
                claim_type=s_claim.entity_type,
            )

    source_types = {c.entity_type for c in source_claims}
    sentence_types = {c.entity_type for c in sentence_claims}

    if not sentence_types.intersection(source_types):
        return ComparisonResult(
            sentence=sentence,
            status=VerificationStatus.UNVERIFIABLE,
        )

    return ComparisonResult(
        sentence=sentence,
        status=VerificationStatus.GROUNDED,
    )
