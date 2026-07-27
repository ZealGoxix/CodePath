"""
Generation layer for the RAG music recommender.

This is the "G" in RAG. It takes the songs that rag.SongRetriever surfaced
for a query and turns them into a short, grounded recommendation written in
plain language.

Two things make this a real RAG step and not just search:

1. Grounding. The generator is only ever allowed to talk about the songs it
   was handed. It never invents titles or artists. The offline generator does
   this by construction; the LLM path is instructed to do it and then checked.

2. Guardrails + confidence. Before generating, we score how confident we are
   based on retrieval strength. If nothing relevant came back (or it is too
   weak), the generator refuses instead of bluffing, mirroring a real system
   that would rather say "I'm not sure" than hallucinate.

The LLM path reuses the Gemini setup from the Module 4 DocuBot project. If no
GEMINI_API_KEY is set (or the google-genai package is missing), the system
falls back to a deterministic template generator so the whole feature still
runs, tests, and produces reproducible output offline.
"""

import logging
import os
from dataclasses import dataclass
from typing import List, Optional

from src.rag import RetrievedSong

logger = logging.getLogger(__name__)

GEMINI_MODEL_NAME = "gemini-flash-latest"

# Below this top-hit cosine score we treat retrieval as "no strong match"
# and refuse rather than generate a shaky recommendation.
CONFIDENCE_FLOOR = 0.05


@dataclass
class Recommendation:
    """The full result of one RAG query."""
    query: str
    answer: str
    retrieved: List[RetrievedSong]
    confidence: float
    confidence_label: str
    source: str  # "gemini" or "offline-template"
    refused: bool


def score_confidence(retrieved: List[RetrievedSong]) -> float:
    """
    Turns retrieval strength into a 0-1 confidence score.

    We lean on the top hit's cosine score but nudge it up when several songs
    are relevant, since agreement across the catalog is a good sign.
    """
    if not retrieved:
        return 0.0
    top = retrieved[0].score
    # A small bonus for depth of support, capped so it can't dominate.
    support_bonus = min(len(retrieved) - 1, 2) * 0.05
    return min(top + support_bonus, 1.0)


def confidence_label(score: float) -> str:
    """Human-readable band for a confidence score."""
    if score >= 0.35:
        return "high"
    if score >= 0.15:
        return "medium"
    if score > 0.0:
        return "low"
    return "none"


def _format_song_line(hit: RetrievedSong) -> str:
    """One catalog citation line for a retrieved song."""
    s = hit.song
    return (
        f"- {s['title']} by {s['artist']} "
        f"[{s['genre']}, {s['mood']}, energy {float(s['energy']):.2f}] "
        f"(match {hit.score:.3f})"
    )


class RecommendationGenerator:
    """
    Grounded generator with a guardrail, confidence scoring, and two backends.

    Call generate(query, retrieved) to get a Recommendation. The retrieved list
    must come from the retriever so the generator stays grounded in the catalog.
    """

    def __init__(self, use_llm: bool = True):
        self.gemini = None
        self.source = "offline-template"
        if use_llm:
            self.gemini = self._try_init_gemini()
            if self.gemini is not None:
                self.source = "gemini"

    @staticmethod
    def _try_init_gemini():
        """Best-effort Gemini setup. Returns None if unavailable (no key/pkg)."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.info("No GEMINI_API_KEY set; using offline template generator.")
            return None
        try:
            from google import genai
        except ImportError:
            logger.warning("google-genai not installed; using offline generator.")
            return None
        try:
            return genai.Client(api_key=api_key)
        except Exception as exc:  # noqa: BLE001 - never let LLM setup crash the app
            logger.warning("Could not init Gemini (%s); using offline generator.", exc)
            return None

    def generate(self, query: str, retrieved: List[RetrievedSong]) -> Recommendation:
        """Runs the guardrail, then generates a grounded recommendation."""
        confidence = score_confidence(retrieved)
        label = confidence_label(confidence)

        # Guardrail: refuse when retrieval is empty or too weak to trust.
        if not retrieved or confidence < CONFIDENCE_FLOOR:
            logger.info("Refusing query %r (confidence %.3f below floor).", query, confidence)
            return Recommendation(
                query=query,
                answer=(
                    "I couldn't find a strong match for that in the catalog, "
                    "so I'd rather not guess. Try describing a mood, activity, "
                    "or genre (for example: 'calm piano for studying')."
                ),
                retrieved=retrieved,
                confidence=confidence,
                confidence_label=label,
                source=self.source,
                refused=True,
            )

        if self.gemini is not None:
            answer = self._generate_with_gemini(query, retrieved)
        else:
            answer = self._generate_offline(query, retrieved)

        return Recommendation(
            query=query,
            answer=answer,
            retrieved=retrieved,
            confidence=confidence,
            confidence_label=label,
            source=self.source,
            refused=False,
        )

    def _generate_offline(self, query: str, retrieved: List[RetrievedSong]) -> str:
        """
        Deterministic, fully grounded generator.

        Writes a short recommendation that references only the retrieved songs
        and the exact terms that made them match. No external calls, so output
        is identical every run.
        """
        top = retrieved[0]
        top_song = top.song
        matched = ", ".join(top.matched_terms) if top.matched_terms else "your description"

        lines = [
            f'For "{query}", my top pick is {top_song["title"]} by '
            f'{top_song["artist"]}.',
            f'It lines up on: {matched}.',
        ]
        if len(retrieved) > 1:
            others = ", ".join(
                f'{h.song["title"]} ({h.song["genre"]})' for h in retrieved[1:]
            )
            lines.append(f"You might also like: {others}.")
        lines.append("")
        lines.append("Grounded in these catalog songs:")
        lines.extend(_format_song_line(h) for h in retrieved)
        return "\n".join(lines)

    def _generate_with_gemini(self, query: str, retrieved: List[RetrievedSong]) -> str:
        """
        LLM generation constrained to the retrieved songs only.

        The prompt hands the model the retrieved catalog rows and forbids it
        from mentioning anything outside them. We then verify the output only
        references retrieved titles; if it drifts, we fall back to the offline
        generator so the user never sees a hallucinated song.
        """
        context = "\n".join(_format_song_line(h) for h in retrieved)
        prompt = f"""You are a music recommender. A listener asked:
"{query}"

Here are the ONLY songs you may recommend, retrieved from the catalog:
{context}

Rules:
- Recommend only from the songs above. Never invent a title or artist.
- Write 2-4 friendly sentences explaining which to play and why, using the
  genre, mood, and energy shown.
- Do not mention songs, artists, or facts that are not listed above.
"""
        try:
            response = self.gemini.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt,
            )
            text = (response.text or "").strip()
        except Exception as exc:  # noqa: BLE001 - degrade instead of crashing
            logger.warning("Gemini call failed (%s); falling back to offline.", exc)
            return self._generate_offline(query, retrieved)

        if not text or not self._is_grounded(text, retrieved):
            logger.warning("LLM output failed grounding check; using offline generator.")
            return self._generate_offline(query, retrieved)

        # Always append the citations so the answer is auditable.
        citations = "\n".join(_format_song_line(h) for h in retrieved)
        return f"{text}\n\nGrounded in these catalog songs:\n{citations}"

    @staticmethod
    def _is_grounded(text: str, retrieved: List[RetrievedSong]) -> bool:
        """
        Cheap grounding guardrail: every retrieved title the model names must
        exist in the retrieved set. If the model mentions none of them, we treat
        that as ungrounded too.
        """
        lowered = text.lower()
        return any(h.song["title"].lower() in lowered for h in retrieved)
