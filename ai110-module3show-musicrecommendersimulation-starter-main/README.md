# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version takes a list of songs and a little profile of what I'm into, then scores each song on how well it matches me and hands back the top few. It leans on the song's own traits like genre, mood, and energy, so it's a content-based recommender, not one that copies other people's taste.

---

## How The System Works

Real platforms like Spotify or YouTube guess what I'll like next in two main ways. One is collaborative filtering, where they look at other people with similar taste and show me what those people liked. The other is content-based filtering, where they look at the song itself, its genre, tempo, mood, and energy, and find more songs that feel the same. They learn from stuff like my likes, skips, replays, and playlists.

My version keeps it simple and goes content-based. It looks at each song's traits and compares them to what I said I like, then gives the song a score. Matching my genre is worth the most, then mood, and for energy it rewards songs that land close to my target instead of just picking the loudest ones. After every song has a score, I sort them high to low and take the top few. So there's a scoring rule for one song and a ranking rule to line them all up.

**What each `Song` uses:**

- genre
- mood
- energy
- tempo_bpm
- valence
- danceability
- acousticness

**What my `UserProfile` stores:**

- favorite_genre
- favorite_mood
- target_energy
- likes_acoustic

**Example taste profile I'll test with:**

```python
user_prefs = {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False}
```

This one is an intense rock fan, which is easy to tell apart from a chill lofi listener since the genre, mood, and energy all point in a clear direction.

### My Algorithm Recipe

Here's the scoring rule I'll use for each song:

- +2.0 points if the genre matches
- +1.0 point if the mood matches
- energy points from how close the song's energy is to my target: `1 - abs(song_energy - target_energy)`
- small bonus if `likes_acoustic` is true and the song is fairly acoustic

Then the ranking rule just sorts every song by its total score, high to low, and I take the top K.

### Data Flow

```
Input (user prefs)
   -> Process: loop over every song in the CSV and score it
   -> Output: sort by score and return the top K
```

### Biases I expect

Since genre is worth the most, the system will probably lean hard on genre and might skip a song that matches my mood and energy perfectly just because it's the "wrong" genre. It also only knows the 18 songs in the catalog, so it can't recommend anything outside that tiny list, and it has no idea about lyrics or language.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Here's what mine prints for the default pop, happy, energy 0.8 profile:

```
Loaded songs: 18

Top recommendations:

1. Sunrise City by Neon Echo  (score 3.98)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.98)

2. Gym Hero by Max Pulse  (score 2.87)
   why: genre match (+2.0), energy close to target (+0.87)

3. Rooftop Lights by Indigo Parade  (score 1.96)
   why: mood match (+1.0), energy close to target (+0.96)

4. Concrete Kings by Blocktape  (score 1.00)
   why: energy close to target (+1.00)

5. Night Drive Loop by Neon Echo  (score 0.95)
   why: energy close to target (+0.95)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



