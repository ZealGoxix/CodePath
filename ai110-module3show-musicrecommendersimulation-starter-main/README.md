# Music Recommender Simulation

## The original project (Modules 1-3)

The Music Recommender Simulation is a small content-based recommender I built for Modules 1-3. It takes a user "taste profile" (favorite genre, mood, target energy) and scores every song in a CSV catalog against it, then returns the top few with a short reason for each pick. It is content-based, not collaborative: it looks at each song's own traits instead of copying other people's taste.

## The extended system: RAG music recommender

For this Applied AI project I added a Retrieval-Augmented Generation (RAG) path on top of that scorer. Instead of filling in a rigid genre/mood/energy form, I can now type a plain-English request like "calm piano for late night studying." The system retrieves the most relevant songs from the catalog, then generates a short, grounded recommendation that only ever talks about songs it actually retrieved. It scores its own confidence and refuses to guess when nothing in the catalog is a strong match.

The original scorer still works unchanged, so I can compare the two side by side.

## Architecture overview

The Mermaid source is in [diagrams/architecture.mmd](diagrams/architecture.mmd). The flow follows the two letters of RAG plus a guardrail:

1. **Input.** A free-text query (RAG path) or a structured prefs dict (classic path).
2. **Retrieve** ([src/rag.py](src/rag.py)). Each song is flattened into a searchable text document from its title, artist, genre, mood, an energy descriptor, and hand-written tags. A pure-Python TF-IDF + cosine similarity retriever ranks those documents against the query and returns the top-k with match scores. No network, no heavy libraries, so retrieval is deterministic.
3. **Guardrail + confidence** ([src/generator.py](src/generator.py)). Retrieval strength is turned into a 0-1 confidence score. If it falls below a floor (or nothing was retrieved), the system refuses instead of bluffing.
4. **Generate** ([src/generator.py](src/generator.py)). The retrieved songs (and only those) are handed to the generator. If a `GEMINI_API_KEY` is set it uses Gemini with a prompt that forbids inventing songs, then runs a grounding check on the output. Otherwise it uses a deterministic offline template generator. Either way the answer ends with catalog citations.
5. **Output.** A grounded recommendation with its confidence and citations, or a refusal.
6. **Testing / human checkpoints.** [tests/](tests/) unit-tests retrieval and the guardrail, [eval/eval_rag.py](eval/eval_rag.py) runs a labeled query set and writes [eval/eval_report.md](eval/eval_report.md) for human review.

## Setup and run

From the project root (`ai110-module3show-musicrecommendersimulation-starter-main`):

1. (Optional) create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies (the RAG feature runs fully offline on the standard library):

   ```bash
   pip install -r requirements.txt
   ```

3. Run the demo (classic scorer + RAG queries):

   ```bash
   python -m src.main
   ```

4. Run a single free-text query:

   ```bash
   python -m src.main --query "calm piano for late night studying"
   ```

   Useful flags: `--no-llm` forces the offline generator, `--classic` runs only the original scorer, `--k N` sets how many songs to retrieve, `--verbose` shows the retrieval/generation logs.

5. Run the evaluation harness:

   ```bash
   python -m eval.eval_rag
   ```

6. Run the tests:

   ```bash
   pytest
   ```

### Turning on the LLM generation path (optional)

The system generates with a deterministic offline template by default. To use Gemini instead, install the optional client and set a key:

```bash
pip install google-genai
export GEMINI_API_KEY=your_key_here      # Windows: set GEMINI_API_KEY=your_key_here
python -m src.main --query "chill tropical beach vibes"
```

If the key or package is missing, or a Gemini call fails, or the model's answer fails the grounding check, the system automatically falls back to the offline generator. The sample outputs below use the offline path so they are reproducible without a key.

## Sample inputs and outputs

These are real command outputs, not screenshots.

**1. A workout query (good match, high confidence):**

```
$ python -m src.main -q "high energy music for the gym" --no-llm
Loaded songs: 28

=== RAG query: 'high energy music for the gym' ===
[confidence: 0.644 (high) | generator: offline-template]

For "high energy music for the gym", my top pick is Gym Hero by Max Pulse.
It lines up on: energy, gym, high.
You might also like: Voltage Drop (edm), Sugar Rush (pop).

Grounded in these catalog songs:
- Gym Hero by Max Pulse [pop, intense, energy 0.93] (match 0.544)
- Voltage Drop by Pulsewave [edm, energetic, energy 0.95] (match 0.167)
- Sugar Rush by Neon Echo [pop, happy, energy 0.86] (match 0.099)
```

**2. A romantic query (retrieves the r&b cluster):**

```
$ python -m src.main -q "smooth romantic song for a date" --no-llm
Loaded songs: 28

=== RAG query: 'smooth romantic song for a date' ===
[confidence: 0.527 (high) | generator: offline-template]

For "smooth romantic song for a date", my top pick is Firelight Waltz by Velvet Room.
It lines up on: date, romantic, smooth.
You might also like: Slow Dance Tonight (r&b), Coffee Shop Stories (jazz).

Grounded in these catalog songs:
- Firelight Waltz by Velvet Room [r&b, romantic, energy 0.48] (match 0.427)
- Slow Dance Tonight by Velvet Room [r&b, romantic, energy 0.50] (match 0.406)
- Coffee Shop Stories by Slow Stereo [jazz, relaxed, energy 0.37] (match 0.114)
```

**3. A nonsense query (guardrail refuses instead of guessing):**

```
$ python -m src.main -q "purple elephant tax spreadsheet" --no-llm
Loaded songs: 28

=== RAG query: 'purple elephant tax spreadsheet' ===
[confidence: 0.000 (none) | generator: offline-template | REFUSED]

I couldn't find a strong match for that in the catalog, so I'd rather not guess. Try describing a mood, activity, or genre (for example: 'calm piano for studying').
```

## Design decisions and trade-offs

- **Pure-Python TF-IDF instead of embeddings or a vector DB.** I wanted retrieval to be deterministic, testable, and installable with zero heavy dependencies. The trade-off is that matching is lexical: a query has to share words with a song's tags, so I lean on a hand-written `tags` column to carry synonyms. Real embeddings would catch meaning I miss, at the cost of reproducibility and setup weight.
- **LLM generation is optional with an offline fallback.** The real RAG story uses an LLM to write the recommendation, but forcing an API key would break reproducibility and grading. So the LLM path is opt-in and the offline template generator is always available. The downside is the default output reads more like a template than natural prose.
- **Grounding is enforced, not assumed.** The offline generator is grounded by construction, and the LLM path is prompted to stay in the retrieved set and then checked; if it names a song it was not given, I drop back to the offline answer. This trades some LLM fluency for a guarantee that the user never sees a made-up song.
- **A confidence floor that refuses.** I would rather return nothing than a wrong pick, so weak retrieval becomes a refusal. The risk is being too cautious on oddly-worded but valid queries, which is exactly what the eval set watches.

## Testing summary

Two layers of checks, both run offline and deterministically.

**Unit tests** (`pytest`): 12/12 passing. They cover tokenization, document building, retrieval ranking and ordering, the empty result for nonsense, confidence banding, the refusal guardrail, and that generated answers only name retrieved songs.

**Evaluation harness** (`python -m eval.eval_rag`): 6/6 cases passing. Each case checks retrieval hit-rate (did the expected song show up in top-k), grounding (no hallucinated titles), and, for the nonsense case, that the guardrail correctly refuses. The full input / criteria / result table is written to [eval/eval_report.md](eval/eval_report.md).

```
$ python -m eval.eval_rag --no-llm
RAG evaluation (offline-template):
  [PASS] 'high energy music for the gym' -> ok
  [PASS] 'calm piano for late night studying' -> ok
  [PASS] 'smooth romantic song for a date night' -> ok
  [PASS] 'aggressive heavy metal to get pumped' -> ok
  [PASS] 'chill tropical beach vibes' -> ok
  [PASS] 'purple elephant tax spreadsheet' -> correctly refused

6/6 cases passed.
```

## Reflection

The development reflection, including how I used AI, one helpful and one flawed AI suggestion, and the system's limitations, is in [model_card.md](model_card.md).
