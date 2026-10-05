import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from anchor.verify import verify
from anchor.scorer import auto_correct
from anchor.comparator import VerificationStatus

SAMPLE_REPORT = """
The NVIDIA H100 delivers 3.35 TB/s memory bandwidth using HBM3.
The H100 provides 79.5 TFLOPS of FP32 performance.
NVIDIA CEO Jensen Huang announced the H100 at GTC 2022.
The H100 uses a 4nm manufacturing process.
The chip contains 80 billion transistors.
"""

SAMPLE_SOURCE_CHUNKS = [
    {
        "chunk_id": "1",
        "text": "The NVIDIA H100 delivers 3.35 TB/s memory bandwidth using HBM3 memory.",
        "source_doc": "nvidia_h100_whitepaper.pdf",
        "page": 4
    },
    {
        "chunk_id": "2",
        "text": "The H100 SXM5 delivers 67 TFLOPS of FP32 performance, nearly double the A100.",
        "source_doc": "nvidia_h100_whitepaper.pdf",
        "page": 6
    },
    {
        "chunk_id": "3",
        "text": "Jensen Huang introduced the H100 at the GTC 2022 keynote in March.",
        "source_doc": "nvidia_gtc_2022.html",
        "page": 1
    },
    {
        "chunk_id": "4",
        "text": "The H100 is built on TSMC 4N process technology, customized for NVIDIA.",
        "source_doc": "nvidia_h100_whitepaper.pdf",
        "page": 2
    },
    {
        "chunk_id": "5",
        "text": "H100 contains 80 billion transistors across the full die.",
        "source_doc": "nvidia_h100_whitepaper.pdf",
        "page": 2
    },
]

def print_separator():
    print("-" * 60)

def run_demo():
    print("\n" + "=" * 60)
    print("  ANCHOR — RAG Grounding Verifier")
    print("  Research Agent Demo")
    print("=" * 60)

    print("\nRunning verification on Research Agent output...")
    print_separator()

    report = verify(
        generated_text=SAMPLE_REPORT,
        source_chunks=SAMPLE_SOURCE_CHUNKS,
    )

    print(f"\nTRUST SCORE: {report.trust_score}/100")
    print(f"Total sentences : {report.total_sentences}")
    print(f"Grounded        : {report.grounded}")
    print(f"Mismatches      : {report.mismatches}")
    print(f"No claims       : {report.no_claims}")
    print_separator()

    print("\nSENTENCE BREAKDOWN:\n")
    for r in report.results:
        status = r.status.value
        icon = "✅" if status == "GROUNDED" else "❌" if status == "MISMATCH" else "⚪"
        print(f"{icon}  [{status}]")
        print(f"    {r.sentence}")
        if status == "MISMATCH":
            print(f"    Found   : {r.found_value}")
            print(f"    Source  : {r.source_value}")
            corrected = auto_correct(r)
            print(f"    Fixed   : {corrected}")
        print()

    print_separator()
    if report.mismatches == 0:
        print("All verifiable claims grounded. Report is clean.")
    else:
        print(f"{report.mismatches} mismatch(es) detected and auto-corrected above.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_demo()



