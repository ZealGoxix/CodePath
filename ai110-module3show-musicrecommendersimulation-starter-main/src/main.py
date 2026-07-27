"""
Command line runner for the Music Recommender Simulation.

This ties together two paths:

- The original content-based scorer (genre/mood/energy -> ranked songs). This
  is the Module 1-3 system and still runs unchanged.
- The new RAG path: a free-text query is retrieved against the catalog and
  turned into a grounded, confidence-scored recommendation.

Usage:
    python -m src.main                      # demo: classic profiles + RAG queries
    python -m src.main --query "gym music"  # one RAG query
    python -m src.main --classic            # only the original scorer demo
    python -m src.main --no-llm             # force the offline generator
"""

import argparse
import logging

from src.recommender import load_songs, recommend_songs
from src.rag import SongRetriever
from src.generator import RecommendationGenerator

DATA_PATH = "data/songs.csv"

# Profiles I use to stress test the original scorer.
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.95},
    # Adversarial: high energy but a calm mood that doesn't fit, plus a mood
    # ("sad") that isn't even in the catalog, so mood can never match.
    "Conflicting (sad + high energy)": {"mood": "sad", "energy": 0.95},
}

# Free-text queries that show off the RAG path.
DEMO_QUERIES = [
    "high energy music for the gym",
    "calm piano for late night studying",
    "something smooth and romantic for a date",
]


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Prints the top k recommendations from the original scorer."""
    print(f"\n=== {name} ===")
    print(f"prefs: {user_prefs}\n")
    recommendations = recommend_songs(user_prefs, songs, k=k)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  (score {score:.2f})")
        print(f"   why: {explanation}")
    print()


def run_classic_demo(songs: list) -> None:
    """Runs the original content-based scorer on the stress-test profiles."""
    print("\n########## CLASSIC SCORER (Modules 1-3) ##########")
    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs, k=5)


def print_rag_result(result) -> None:
    """Prints one RAG recommendation with its confidence and citations."""
    print(f"\n=== RAG query: {result.query!r} ===")
    print(f"[confidence: {result.confidence:.3f} ({result.confidence_label}) "
          f"| generator: {result.source}"
          f"{' | REFUSED' if result.refused else ''}]\n")
    print(result.answer)
    print()


def run_rag_query(query: str, retriever: SongRetriever,
                  generator: RecommendationGenerator, k: int = 3) -> None:
    """Retrieves for one query, generates a grounded answer, and prints it."""
    hits = retriever.retrieve(query, k=k)
    result = generator.generate(query, hits)
    print_rag_result(result)


def run_rag_demo(retriever: SongRetriever, generator: RecommendationGenerator) -> None:
    """Runs the RAG path over the demo queries."""
    print("\n########## RAG RECOMMENDER (new AI feature) ##########")
    for query in DEMO_QUERIES:
        run_rag_query(query, retriever, generator)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation with RAG.")
    parser.add_argument("--query", "-q", help="Run a single free-text RAG query.")
    parser.add_argument("--classic", action="store_true",
                        help="Run only the original content-based scorer demo.")
    parser.add_argument("--no-llm", action="store_true",
                        help="Force the offline template generator (skip Gemini).")
    parser.add_argument("--k", type=int, default=3,
                        help="How many songs to retrieve per query (default 3).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show INFO logs (retrieval/generation decisions).")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    _configure_logging(args.verbose)

    try:
        songs = load_songs(DATA_PATH)
    except FileNotFoundError:
        print(f"ERROR: could not find song data at {DATA_PATH}. "
              f"Run from the project root.")
        return

    if args.classic:
        run_classic_demo(songs)
        return

    retriever = SongRetriever(songs)
    generator = RecommendationGenerator(use_llm=not args.no_llm)

    if args.query:
        run_rag_query(args.query, retriever, generator, k=args.k)
        return

    # Default: show both systems so the extension is easy to compare.
    run_classic_demo(songs)
    run_rag_demo(retriever, generator)


if __name__ == "__main__":
    main()
