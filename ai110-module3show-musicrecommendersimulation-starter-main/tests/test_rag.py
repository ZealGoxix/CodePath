"""
Tests for the RAG feature: retrieval, confidence, guardrail, and grounding.

These use the offline generator (use_llm=False) so they are deterministic and
run without any API key or network access.
"""

from src.recommender import load_songs
from src.rag import SongRetriever, tokenize, song_to_document
from src.generator import (
    RecommendationGenerator,
    score_confidence,
    confidence_label,
)

DATA_PATH = "data/songs.csv"


def make_retriever() -> SongRetriever:
    return SongRetriever(load_songs(DATA_PATH))


# --------------------------- retrieval ---------------------------

def test_tokenize_drops_stopwords_and_short_tokens():
    tokens = tokenize("I want some CHILL music for a x")
    # stopwords (i, want, some, for, a, music) and 1-char "x" are dropped
    assert tokens == ["chill"]


def test_document_includes_tags_and_energy_words():
    song = {"title": "Gym Hero", "artist": "Max Pulse", "genre": "pop",
            "mood": "intense", "energy": 0.93, "tags": "workout gym cardio"}
    doc = song_to_document(song).lower()
    assert "workout" in doc and "gym" in doc
    assert "high energy" in doc  # 0.93 maps to the high-energy descriptor


def test_retrieve_workout_query_surfaces_gym_track():
    retriever = make_retriever()
    hits = retriever.retrieve("high energy music for the gym", k=3)
    assert hits, "expected at least one hit"
    titles = [h.song["title"] for h in hits]
    assert "Gym Hero" in titles


def test_retrieve_returns_scores_in_descending_order():
    retriever = make_retriever()
    hits = retriever.retrieve("calm piano for studying", k=3)
    scores = [h.score for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_nonsense_returns_nothing():
    retriever = make_retriever()
    hits = retriever.retrieve("qwerty zxcvb nonsenseword", k=3)
    assert hits == []


# --------------------------- confidence ---------------------------

def test_confidence_zero_for_no_hits():
    assert score_confidence([]) == 0.0
    assert confidence_label(0.0) == "none"


def test_confidence_labels_bands():
    assert confidence_label(0.40) == "high"
    assert confidence_label(0.20) == "medium"
    assert confidence_label(0.05) == "low"


# --------------------------- generation + guardrail ---------------------------

def test_generator_refuses_when_nothing_retrieved():
    gen = RecommendationGenerator(use_llm=False)
    result = gen.generate("qwerty zxcvb", [])
    assert result.refused is True
    assert result.confidence == 0.0
    assert "couldn't find" in result.answer.lower()


def test_generator_answer_is_grounded_in_retrieved_songs():
    retriever = make_retriever()
    gen = RecommendationGenerator(use_llm=False)
    hits = retriever.retrieve("smooth romantic date night", k=3)
    result = gen.generate("smooth romantic date night", hits)

    assert result.refused is False
    assert result.source == "offline-template"
    # Every song named in the answer must be one we retrieved.
    retrieved_titles = {h.song["title"] for h in hits}
    all_titles = {s["title"] for s in load_songs(DATA_PATH)}
    for title in all_titles:
        if title in result.answer:
            assert title in retrieved_titles, f"hallucinated non-retrieved song: {title}"


def test_generator_cites_top_song_in_answer():
    retriever = make_retriever()
    gen = RecommendationGenerator(use_llm=False)
    hits = retriever.retrieve("aggressive heavy metal", k=3)
    result = gen.generate("aggressive heavy metal", hits)
    assert hits[0].song["title"] in result.answer
