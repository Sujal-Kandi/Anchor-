from dataclasses import dataclass 
from anchor.comparator import ComparisonResult , VerificationStatus


@dataclass
class VerificationReport:
    trust_score: int
    total_sentences: int
    grounded: int
    mismatches: int
    unverifiable: int
    no_claims: int
    results: list[ComparisonResult]

def compute_trust_score(results: list[ComparisonResult]) -> int:
    grounded = sum(1 for r in results if r.status == VerificationStatus.GROUNDED)
    mismatches = sum(1 for r in results if r.status == VerificationStatus.MISMATCH)

    verifiable = grounded + mismatches

    if verifiable == 0:
        return 100

    score = (grounded / verifiable) * 100
    return round(score)

def build_report(results: list[ComparisonResult]) -> VerificationReport:
    return VerificationReport(
        trust_score=compute_trust_score(results),
        total_sentences=len(results),
        grounded=sum(1 for r in results if r.status == VerificationStatus.GROUNDED),
        mismatches=sum(1 for r in results if r.status == VerificationStatus.MISMATCH),
        unverifiable=sum(1 for r in results if r.status == VerificationStatus.UNVERIFIABLE),
        no_claims=sum(1 for r in results if r.status == VerificationStatus.NO_CLAIMS),
        results=results,
    )

def auto_correct(result: ComparisonResult) -> str:
    if result.status != VerificationStatus.MISMATCH:
        return result.sentence

    if not result.found_value or not result.source_value:
        return result.sentence

    return result.sentence.replace(
        result.found_value,
        result.source_value,
        1,
    )

