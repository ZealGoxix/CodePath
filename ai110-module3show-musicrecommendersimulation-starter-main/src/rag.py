"""
Retrieval layer for the RAG music recommender.

This is the "R" in RAG. Before anything is generated, we retrieve the songs
from the catalog that are most relevant to a free-text query like
"chill music for late night studying".

The retriever turns every song into a small text document (its title, artist,
genre, mood, an energy descriptor, and hand-written tags), then ranks those
documents against the query using TF-IDF weighting with cosine similarity.

It is written in pure Python on purpose:
- no network calls, so retrieval is deterministic and reproducible
- no heavy dependencies (no sklearn), so `pip install` stays tiny
- easy to unit test and reason about

The generator in generator.py only ever sees the songs this module returns,
so retrieval quality is the foundation the whole feature stands on.
"""

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Words that carry no taste signal. Dropping them keeps the cosine score
# focused on meaningful terms instead of filler.
STOPWORDS = {
    "a", "an", "and", "the", "for", "of", "to", "with", "in", "on", "at",
    "some", "that", "this", "i", "im", "me", "my", "want", "need", "like",
    "song", "songs", "music", "track", "tracks", "please", "give", "find",
    "something", "feel", "feeling", "vibe", "vibes", "playlist",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    """Lowercases text and splits it into meaningful word tokens."""
    tokens = TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def energy_words(energy: float) -> str:
    """Turns a 0-1 energy number into words so it can be searched on."""
    if energy >= 0.8:
        return "high energy intense powerful driving fast"
    if energy >= 0.55:
        return "medium energy upbeat moderate"
    return "low energy calm mellow slow gentle relaxed"


def song_to_document(song: Dict) -> str:
    """
    Flattens one song dict into a searchable text document.

    This is the text the retriever actually indexes. Structured fields
    (genre, mood) and free-text tags both feed in, which is what lets a
    query like "workout" reach a song tagged "gym running cardio".
    """
    parts = [
        str(song.get("title", "")),
        str(song.get("artist", "")),
        str(song.get("genre", "")),
        str(song.get("mood", "")),
        energy_words(float(song.get("energy", 0.5))),
        str(song.get("tags", "")),
    ]
    return " ".join(parts)


@dataclass
class RetrievedSong:
    """One retrieval hit: the song plus how relevant it was to the query."""
    song: Dict
    score: float
    matched_terms: List[str]


class SongRetriever:
    """
    TF-IDF + cosine similarity retriever over the song catalog.

    Usage:
        retriever = SongRetriever(songs)
        hits = retriever.retrieve("energetic gym workout", k=3)
    """

    def __init__(self, songs: List[Dict]):
        if not songs:
            raise ValueError("SongRetriever needs at least one song to index.")
        self.songs = songs
        self.documents = [song_to_document(s) for s in songs]
        self.doc_tokens = [tokenize(doc) for doc in self.documents]
        self.idf = self._compute_idf(self.doc_tokens)
        self.doc_vectors = [self._tfidf_vector(toks) for toks in self.doc_tokens]

    @staticmethod
    def _compute_idf(doc_tokens: List[List[str]]) -> Dict[str, float]:
        """Inverse document frequency: rare words across songs weigh more."""
        n_docs = len(doc_tokens)
        doc_freq: Dict[str, int] = {}
        for toks in doc_tokens:
            for term in set(toks):
                doc_freq[term] = doc_freq.get(term, 0) + 1
        # Smoothed idf so no term ever gets a zero or undefined weight.
        return {
            term: math.log((n_docs + 1) / (df + 1)) + 1.0
            for term, df in doc_freq.items()
        }

    def _tfidf_vector(self, tokens: List[str]) -> Dict[str, float]:
        """Builds a term -> tf*idf weight map for one token list."""
        if not tokens:
            return {}
        tf: Dict[str, float] = {}
        for term in tokens:
            tf[term] = tf.get(term, 0.0) + 1.0
        n = float(len(tokens))
        return {
            term: (count / n) * self.idf.get(term, 0.0)
            for term, count in tf.items()
        }

    @staticmethod
    def _cosine(a: Dict[str, float], b: Dict[str, float]) -> Tuple[float, List[str]]:
        """Cosine similarity between two sparse vectors, plus shared terms."""
        if not a or not b:
            return 0.0, []
        shared = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in shared)
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0, []
        return dot / (norm_a * norm_b), sorted(shared)

    def retrieve(self, query: str, k: int = 3) -> List[RetrievedSong]:
        """
        Returns the top k songs most relevant to the query, ranked by cosine
        similarity. Songs with zero overlap are dropped rather than padded in,
        so a nonsense query can legitimately return fewer than k (or none).
        """
        query_vec = self._tfidf_vector(tokenize(query))
        scored: List[RetrievedSong] = []
        for song, doc_vec in zip(self.songs, self.doc_vectors):
            score, matched = self._cosine(query_vec, doc_vec)
            if score > 0:
                scored.append(RetrievedSong(song=song, score=score, matched_terms=matched))
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:k]
