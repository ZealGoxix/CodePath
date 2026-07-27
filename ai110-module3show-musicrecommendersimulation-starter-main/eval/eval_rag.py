"""
Reliability / evaluation harness for the RAG music recommender.

This is the eval loop. It runs a small labeled set of queries through the real
retrieval + generation pipeline and checks three things per query:

1. Retrieval hit    - did the expected song show up in the top-k?
2. Grounding        - does the generated answer only name retrieved songs
                      (no hallucinated titles)?
3. Guardrail        - for the nonsense query, did the system correctly refuse?

It prints a pass/fail summary to the console and writes a markdown report
(eval/eval_report.md) with an input / criteria / result table, so results are
easy to drop into the README or model card.

Run from the project root:
    python -m eval.eval_rag
    python -m eval.eval_rag --no-llm     # force offline generator (default anyway if no key)
"""

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import List, Optional

from src.recommender import load_songs
from src.rag import SongRetriever
from src.generator import RecommendationGenerator

DATA_PATH = "data/songs.csv"
QUERIES_PATH = os.path.join("eval", "eval_queries.json")
REPORT_PATH = os.path.join("eval", "eval_report.md")


@dataclass
class CaseResult:
    query: str
    criteria: str
    expected: List[str]
    top_song: Optional[str]
    confidence: float
    confidence_label: str
    refused: bool
    retrieval_ok: bool
    grounded_ok: bool
    passed: bool
    note: str


def all_titles(songs) -> List[str]:
    return [s["title"] for s in songs]


def check_grounded(answer: str, retrieved, all_song_titles: List[str]) -> bool:
    """
    Grounding check: the answer must not name any catalog song that was NOT
    retrieved. We scan the answer for every known title and require each one
    found to be part of the retrieved set.
    """
    retrieved_titles = {h.song["title"].lower() for h in retrieved}
    lowered = answer.lower()
    for title in all_song_titles:
        if re.search(r"\b" + re.escape(title.lower()) + r"\b", lowered):
            if title.lower() not in retrieved_titles:
                return False
    return True


def run_case(case: dict, songs, retriever, generator, all_song_titles, k: int) -> CaseResult:
    query = case["query"]
    expected = case.get("expected_any_of", [])
    criteria = case.get("criteria", "")

    hits = retriever.retrieve(query, k=k)
    result = generator.generate(query, hits)
    top_song = hits[0].song["title"] if hits else None

    # A case that expects a refusal (empty expected list) passes when refused.
    if not expected:
        passed = result.refused
        retrieval_ok = result.refused
        grounded_ok = True
        note = "correctly refused" if result.refused else "should have refused but did not"
    else:
        retrieval_ok = any(
            e.lower() in [h.song["title"].lower() for h in hits] for e in expected
        )
        # Grounding only matters when we actually generated an answer.
        grounded_ok = True if result.refused else check_grounded(
            result.answer, hits, all_song_titles
        )
        passed = retrieval_ok and grounded_ok and not result.refused
        if result.refused:
            note = "refused a query that had an expected match"
        elif not retrieval_ok:
            note = f"expected one of {expected}, got '{top_song}'"
        elif not grounded_ok:
            note = "answer referenced a non-retrieved song (hallucination)"
        else:
            note = "ok"

    return CaseResult(
        query=query,
        criteria=criteria,
        expected=expected,
        top_song=top_song,
        confidence=result.confidence,
        confidence_label=result.confidence_label,
        refused=result.refused,
        retrieval_ok=retrieval_ok,
        grounded_ok=grounded_ok,
        passed=passed,
        note=note,
    )


def render_report(results: List[CaseResult], source: str) -> str:
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    lines = [
        "# RAG Recommender — Evaluation Report",
        "",
        f"Generator backend: `{source}`",
        "",
        f"**Score: {passed}/{total} cases passed.**",
        "",
        "| # | Query (input) | Criteria | Top retrieved | Confidence | Grounded | Result |",
        "|---|---------------|----------|---------------|------------|----------|--------|",
    ]
    for i, r in enumerate(results, start=1):
        top = "— (refused)" if r.refused else (r.top_song or "—")
        grounded = "n/a" if r.refused else ("yes" if r.grounded_ok else "NO")
        outcome = "PASS" if r.passed else "FAIL"
        lines.append(
            f"| {i} | {r.query} | {r.criteria} | {top} | "
            f"{r.confidence:.3f} ({r.confidence_label}) | {grounded} | "
            f"{outcome} — {r.note} |"
        )
    lines.append("")
    lines.append(
        "_Retrieval hit = expected song appears in top-k. "
        "Grounded = generated answer names only retrieved songs. "
        "The nonsense query is expected to be refused by the confidence guardrail._"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the RAG recommender.")
    parser.add_argument("--no-llm", action="store_true",
                        help="Force the offline generator (deterministic).")
    parser.add_argument("--k", type=int, default=3, help="Top-k to retrieve.")
    args = parser.parse_args()

    songs = load_songs(DATA_PATH)
    with open(QUERIES_PATH, encoding="utf-8") as f:
        cases = json.load(f)

    retriever = SongRetriever(songs)
    generator = RecommendationGenerator(use_llm=not args.no_llm)
    titles = all_titles(songs)

    results = [run_case(c, songs, retriever, generator, titles, args.k) for c in cases]

    # Console summary.
    print(f"\nRAG evaluation ({generator.source}):")
    for i, r in enumerate(results, start=1):
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.query!r} -> {r.note}")
    passed = sum(1 for r in results if r.passed)
    print(f"\n{passed}/{len(results)} cases passed.")

    report = render_report(results, generator.source)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
