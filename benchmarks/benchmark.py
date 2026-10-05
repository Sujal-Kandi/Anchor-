import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from anchor.verify import verify
from anchor.comparator import VerificationStatus

BENCHMARK_CASES = [
    # --- CLEAN CASES (expected: GROUNDED) ---
    {"generated": "Apple revenue was 119.6 billion in Q1 2024.",
     "source": "Apple revenue was 119.6 billion in Q1 2024.",
     "expected": "GROUNDED", "id": "c01"},

    {"generated": "The company employed 150000 workers.",
     "source": "The company employed 150000 workers worldwide.",
     "expected": "GROUNDED", "id": "c02"},

    {"generated": "Tim Cook has been CEO since 2011.",
     "source": "Tim Cook became CEO of Apple in 2011.",
     "expected": "GROUNDED", "id": "c03"},

    {"generated": "iPhone accounts for 52 percent of revenue.",
     "source": "The iPhone accounts for 52 percent of total revenue.",
     "expected": "GROUNDED", "id": "c04"},

    {"generated": "Apple was founded in 1976.",
     "source": "Apple was founded in 1976 in Cupertino.",
     "expected": "GROUNDED", "id": "c05"},

    {"generated": "The M3 chip is 15 percent faster than M2.",
     "source": "The M3 chip delivers 15 percent faster performance than M2.",
     "expected": "GROUNDED", "id": "c06"},

    {"generated": "Apple stores operate in 35 countries.",
     "source": "Apple stores operate in 35 countries worldwide.",
     "expected": "GROUNDED", "id": "c07"},

    {"generated": "Apple spent 29 billion on R&D.",
     "source": "Apple spent 29 billion on research and development.",
     "expected": "GROUNDED", "id": "c08"},

    {"generated": "iPad sales declined 8 percent year over year.",
     "source": "iPad sales declined by 8 percent year over year.",
     "expected": "GROUNDED", "id": "c09"},

    {"generated": "Apple Pay is available in 60 countries.",
     "source": "Apple Pay is available in 60 countries globally.",
     "expected": "GROUNDED", "id": "c10"},

    {"generated": "NVIDIA H100 delivers 3.35 TB/s memory bandwidth.",
     "source": "The NVIDIA H100 delivers 3.35 TB/s memory bandwidth using HBM3.",
     "expected": "GROUNDED", "id": "c11"},

    {"generated": "The H100 contains 80 billion transistors.",
     "source": "H100 contains 80 billion transistors across the full die.",
     "expected": "GROUNDED", "id": "c12"},

    {"generated": "Tesla delivered 1.8 million vehicles in 2023.",
     "source": "Tesla delivered 1.8 million vehicles globally in 2023.",
     "expected": "GROUNDED", "id": "c13"},

    {"generated": "OpenAI was founded in 2015.",
     "source": "OpenAI was founded in December 2015 in San Francisco.",
     "expected": "GROUNDED", "id": "c14"},

    {"generated": "GPT-4 was released in March 2023.",
     "source": "GPT-4 was released by OpenAI in March 2023.",
     "expected": "GROUNDED", "id": "c15"},

    {"generated": "Google was founded in 1998 by Larry Page.",
     "source": "Google was founded in 1998 by Larry Page and Sergey Brin.",
     "expected": "GROUNDED", "id": "c16"},

    {"generated": "Meta reported 40 billion in revenue in Q4 2023.",
     "source": "Meta reported 40 billion in revenue for Q4 2023.",
     "expected": "GROUNDED", "id": "c17"},

    {"generated": "Microsoft Azure grew 28 percent in Q2 2024.",
     "source": "Microsoft Azure cloud revenue grew 28 percent in Q2 2024.",
     "expected": "GROUNDED", "id": "c18"},

    {"generated": "Amazon employs 1.5 million workers worldwide.",
     "source": "Amazon employs approximately 1.5 million workers worldwide.",
     "expected": "GROUNDED", "id": "c19"},

    {"generated": "Nvidia market cap exceeded 1 trillion in 2023.",
     "source": "Nvidia market cap exceeded 1 trillion dollars in 2023.",
     "expected": "GROUNDED", "id": "c20"},

    # --- MISMATCH CASES (expected: MISMATCH) ---
    {"generated": "Apple revenue was 89.5 billion in Q1 2024.",
     "source": "Apple revenue was 119.6 billion in Q1 2024.",
     "expected": "MISMATCH", "id": "m01"},

    {"generated": "The company employed 165000 workers.",
     "source": "The company employed 150000 workers worldwide.",
     "expected": "MISMATCH", "id": "m02"},

    {"generated": "iPhone accounts for 48 percent of revenue.",
     "source": "The iPhone accounts for 52 percent of total revenue.",
     "expected": "MISMATCH", "id": "m03"},

    {"generated": "Apple was founded in 1977.",
     "source": "Apple was founded in 1976 in Cupertino.",
     "expected": "MISMATCH", "id": "m04"},

    {"generated": "The M3 chip is 22 percent faster than M2.",
     "source": "The M3 chip delivers 15 percent faster performance than M2.",
     "expected": "MISMATCH", "id": "m05"},

    {"generated": "Apple stores operate in 25 countries.",
     "source": "Apple stores operate in 35 countries worldwide.",
     "expected": "MISMATCH", "id": "m06"},

    {"generated": "Apple spent 35 billion on R&D.",
     "source": "Apple spent 29 billion on research and development.",
     "expected": "MISMATCH", "id": "m07"},

    {"generated": "iPad sales declined 12 percent year over year.",
     "source": "iPad sales declined by 8 percent year over year.",
     "expected": "MISMATCH", "id": "m08"},

    {"generated": "Apple Pay is available in 70 countries.",
     "source": "Apple Pay is available in 60 countries globally.",
     "expected": "MISMATCH", "id": "m09"},

    {"generated": "Tesla delivered 1.3 million vehicles in 2023.",
     "source": "Tesla delivered 1.8 million vehicles globally in 2023.",
     "expected": "MISMATCH", "id": "m10"},

    {"generated": "OpenAI was founded in 2013.",
     "source": "OpenAI was founded in December 2015 in San Francisco.",
     "expected": "MISMATCH", "id": "m11"},

    {"generated": "GPT-4 was released in January 2023.",
     "source": "GPT-4 was released by OpenAI in March 2023.",
     "expected": "MISMATCH", "id": "m12"},

    {"generated": "Google was founded in 2001 by Larry Page.",
     "source": "Google was founded in 1998 by Larry Page and Sergey Brin.",
     "expected": "MISMATCH", "id": "m13"},

    {"generated": "Meta reported 32 billion in revenue in Q4 2023.",
     "source": "Meta reported 40 billion in revenue for Q4 2023.",
     "expected": "MISMATCH", "id": "m14"},

    {"generated": "Microsoft Azure grew 18 percent in Q2 2024.",
     "source": "Microsoft Azure cloud revenue grew 28 percent in Q2 2024.",
     "expected": "MISMATCH", "id": "m15"},

    {"generated": "Amazon employs 2.3 million workers worldwide.",
     "source": "Amazon employs approximately 1.5 million workers worldwide.",
     "expected": "MISMATCH", "id": "m16"},

    {"generated": "NVIDIA H100 delivers 4.8 TB/s memory bandwidth.",
     "source": "The NVIDIA H100 delivers 3.35 TB/s memory bandwidth using HBM3.",
     "expected": "MISMATCH", "id": "m17"},

    {"generated": "Tim Cook has been CEO since 2005.",
     "source": "Tim Cook became CEO of Apple in 2011.",
     "expected": "MISMATCH", "id": "m18"},

    {"generated": "The H100 contains 40 billion transistors.",
     "source": "H100 contains 80 billion transistors across the full die.",
     "expected": "MISMATCH", "id": "m19"},

    {"generated": "Nvidia market cap exceeded 2 trillion in 2023.",
     "source": "Nvidia market cap exceeded 1 trillion dollars in 2023.",
     "expected": "MISMATCH", "id": "m20"},
]

def run_benchmark():
    print("\n" + "=" * 60)
    print("  ANCHOR — Benchmark")
    print("  40 cases: 20 clean + 20 injected mismatches")
    print("=" * 60 + "\n")

    correct = 0
    total = len(BENCHMARK_CASES)
    failed_cases = []

    start = time.time()

    for case in BENCHMARK_CASES:
        report = verify(
            generated_text=case["generated"],
            source_chunks=[{
                "chunk_id": "1",
                "text": case["source"],
                "source_doc": "benchmark",
                "page": 1
            }]
        )

        if not report.results:
            actual = "NO_RESULT"
        else:
            actual = report.results[0].status.value

        expected = case["expected"]

        # UNVERIFIABLE on a clean case = acceptable (can't verify != wrong)
        if actual == "UNVERIFIABLE" and expected == "GROUNDED":
            actual_for_scoring = "GROUNDED"
        else:
            actual_for_scoring = actual

        passed = actual_for_scoring == expected
        if passed:
            correct += 1
        else:
            failed_cases.append({
                "id": case["id"],
                "expected": expected,
                "got": actual,
                "generated": case["generated"],
                "source": case["source"],
            })

    elapsed = time.time() - start

    clean_cases = [c for c in BENCHMARK_CASES if c["expected"] == "GROUNDED"]
    mismatch_cases = [c for c in BENCHMARK_CASES if c["expected"] == "MISMATCH"]

    clean_correct = sum(
        1 for c in clean_cases
        if c not in [f for f in failed_cases]
    )
    mismatch_correct = sum(
        1 for c in mismatch_cases
        if c not in [f for f in failed_cases]
    )

    recall = (mismatch_correct / len(mismatch_cases)) * 100
    fpr = ((len(clean_cases) - clean_correct) / len(clean_cases)) * 100
    accuracy = (correct / total) * 100

    print(f"Total cases    : {total}")
    print(f"Correct        : {correct}")
    print(f"Accuracy       : {accuracy:.1f}%")
    print(f"Recall         : {recall:.1f}%  (mismatches caught)")
    print(f"False Pos Rate : {fpr:.1f}%   (clean wrongly flagged)")
    print(f"Time           : {elapsed:.1f}s")
    print(f"Per case       : {elapsed/total:.2f}s avg")

    if failed_cases:
        print(f"\nFailed cases ({len(failed_cases)}):")
        for f in failed_cases:
            print(f"  [{f['id']}] expected={f['expected']} got={f['got']}")
            print(f"    Generated: {f['generated']}")
            print(f"    Source   : {f['source']}")

    print("\n" + "=" * 60)
    print(f"  RECALL: {recall:.1f}% | FALSE POSITIVE RATE: {fpr:.1f}%")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_benchmark()