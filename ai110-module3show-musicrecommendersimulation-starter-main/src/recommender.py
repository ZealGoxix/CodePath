import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

# My Algorithm Recipe (weights)
GENRE_POINTS = 2.0
MOOD_POINTS = 1.0
ENERGY_WEIGHT = 1.0
ACOUSTIC_BONUS = 0.5
ACOUSTIC_THRESHOLD = 0.6


@dataclass
class Song:
    """Holds one song and all its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    tags: str = ""


@dataclass
class UserProfile:
    """Holds one user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _score_core(genre, mood, energy, likes_acoustic,
                song_genre, song_mood, song_energy, song_acousticness) -> Tuple[float, List[str]]:
    """Runs my scoring recipe on plain values and returns (score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    if genre is not None and genre == song_genre:
        score += GENRE_POINTS
        reasons.append(f"genre match (+{GENRE_POINTS})")

    if mood is not None and mood == song_mood:
        score += MOOD_POINTS
        reasons.append(f"mood match (+{MOOD_POINTS})")

    if energy is not None:
        closeness = (1 - abs(song_energy - energy)) * ENERGY_WEIGHT
        score += closeness
        reasons.append(f"energy close to target (+{closeness:.2f})")

    if likes_acoustic and song_acousticness >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_BONUS
        reasons.append(f"acoustic pick (+{ACOUSTIC_BONUS})")

    return score, reasons


class Recommender:
    """Object-oriented version of the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Scores one Song against one UserProfile."""
        return _score_core(
            user.favorite_genre, user.favorite_mood, user.target_energy, user.likes_acoustic,
            song.genre, song.mood, song.energy, song.acousticness,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Scores every song and returns the top k as Song objects."""
        ranked = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Builds a readable reason string for why a song was picked."""
        score, reasons = self._score(user, song)
        if not reasons:
            return f"No strong match (score {score:.2f})"
        return f"Score {score:.2f} because " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Reads the CSV into a list of dicts with numbers converted for math."""
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song dict against the user's prefs dict."""
    return _score_core(
        user_prefs.get("genre"), user_prefs.get("mood"),
        user_prefs.get("energy"), user_prefs.get("likes_acoustic", False),
        song["genre"], song["mood"], song["energy"], song["acousticness"],
    )


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores all songs, sorts high to low, and returns the top k with explanations."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "no strong match"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
