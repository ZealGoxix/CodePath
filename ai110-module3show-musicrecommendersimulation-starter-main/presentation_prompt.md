# Presentation PRD — paste this into Claude on the web

Copy everything inside the horizontal rules below into a new Claude.ai chat. It has all the facts about my project and tells Claude exactly what presentation to build. Fill in the two blanks marked `[[ ]]` first if you can (they are optional).

---

You are helping me build a 5-7 minute class presentation and a portfolio artifact for my Applied AI project. Act as a presentation coach and slide writer. Do not invent any technical facts beyond what I give you below; everything you need is here.

## What I want you to produce

1. A slide-by-slide deck outline (aim for 8-11 slides for a 5-7 minute talk). For each slide give: a title, 3-5 concise bullet points, and a short speaker-notes paragraph I can read almost verbatim.
2. A timing plan that maps slides to the 5-7 minute budget so I don't run long.
3. A 60-second "live demo script" section: the exact things I say and the exact commands I type, in order, with what the audience should notice in each output.
4. A single polished portfolio reflection paragraph titled "What this project says about me as an AI engineer" (2nd person coaching is fine, but write the paragraph in my first-person voice).
5. Three likely Q&A questions a grader might ask, with strong short answers.

Keep the tone plain and confident, first person, no jargon dumps, no emojis. Prefer short sentences.

## Project facts (ground truth — use only these)

**Project name:** Music Recommender Simulation, extended with a RAG (Retrieval-Augmented Generation) feature.

**The original system (Modules 1-3):** a content-based music recommender. The user gives a taste profile (favorite genre, mood, target energy) and the system scores every song in a 28-song CSV catalog against it, then returns the top few with a reason for each. Scoring: +2 genre match, +1 mood match, up to +1 for energy closeness, +0.5 acoustic bonus. It is content-based, not collaborative.

**The extension (the Applied AI feature):** a RAG path on top of the scorer. Instead of filling in a form, I type a plain-English request like "calm piano for late night studying." The system:
- **Retrieves** the most relevant songs from the catalog using pure-Python TF-IDF + cosine similarity over a text document built from each song's title, artist, genre, mood, an energy descriptor, and hand-written tags.
- **Generates** a short recommendation grounded ONLY in the retrieved songs. Default is a deterministic offline template generator (no API key needed). An optional Gemini LLM path turns on if a GEMINI_API_KEY is set, and its output is checked so it can only name retrieved songs.
- **Scores its own confidence** from retrieval strength, and **refuses** to answer when confidence is below a floor (or nothing relevant was retrieved), instead of guessing.

**Why it counts as real RAG:** retrieve-then-generate order, and the generator is only allowed to talk about songs that were retrieved.

**Architecture (input -> processing -> output):** free-text query + catalog CSV -> retrieve (TF-IDF/cosine, top-k) -> guardrail + confidence score -> generate (offline template or grounded LLM) -> grounded recommendation with citations, OR a refusal. Testing/human checkpoints: unit tests, an eval harness that writes a markdown report, and human review of that report. (Diagram source is in diagrams/architecture.mmd.)

**Reliability / evaluation results (real):**
- Unit tests: 12/12 passing (`pytest`).
- Eval harness: 6/6 labeled cases passing (`python -m eval.eval_rag`), checking retrieval hit-rate, grounding (no hallucinated songs), and correct refusal on a nonsense query. Report saved to eval/eval_report.md.

**Real sample outputs to show on slides / in the demo:**

Good match, high confidence:
```
$ python -m src.main -q "high energy music for the gym" --no-llm
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

Guardrail refuses nonsense:
```
$ python -m src.main -q "purple elephant tax spreadsheet" --no-llm
=== RAG query: 'purple elephant tax spreadsheet' ===
[confidence: 0.000 (none) | generator: offline-template | REFUSED]
I couldn't find a strong match for that in the catalog, so I'd rather not guess.
Try describing a mood, activity, or genre (for example: 'calm piano for studying').
```

**Responsible-AI points to weave in (from my model card):**
- Limitations/biases: retrieval is lexical (matches words, not meaning) so it leans on my hand-written tags; the tags carry my own vocabulary bias; the catalog is small and English-only; confidence is a proxy for retrieval strength, not true quality.
- Misuse + prevention: hallucinated recommendations (prevented by grounding + fallback), fake confidence on bad matches (prevented by the refusal floor), prompt injection (offline path never calls a model; LLM prompt is constrained), and scaling my tagging bias (watched via the human-reviewed eval report).
- What surprised me: keeping the refusal guardrail alive was harder than getting good recommendations; the system looked more broken when it tried to always return a full list. Reliability was about knowing when to say no.
- AI collaboration: helpful suggestion was adding a grounding check + fallback so the LLM can't invent songs; flawed suggestion was padding retrieval to always return k songs, which would have killed the refusal path (I overrode it).

**Portfolio artifact facts:**
- GitHub code link: https://github.com/ZealGoxix/CodePath/tree/master/ai110-module3show-musicrecommendersimulation-starter-main
- My name for the talk: [[YOUR NAME]]
- Course / audience: [[COURSE OR AUDIENCE, e.g. "CodePath AI110, classmates + instructor"]]

## How the demo runs (so your demo script uses the real commands)

Run everything from the project root folder `ai110-module3show-musicrecommendersimulation-starter-main`.

Setup (once): `pip install -r requirements.txt`

Live demo commands, in order:
1. `python -m src.main -q "high energy music for the gym" --no-llm`  (show a strong, grounded match with confidence + citations)
2. `python -m src.main -q "smooth romantic song for a date" --no-llm`  (show it retrieving a different cluster)
3. `python -m src.main -q "purple elephant tax spreadsheet" --no-llm`  (show the guardrail refusing instead of guessing — this is the money moment)
4. `python -m eval.eval_rag --no-llm`  (show 6/6 reliability cases passing)
5. (optional) `pytest`  (show 12/12 tests passing)

The `--no-llm` flag forces the deterministic offline generator so the demo is reproducible with no API key and identical every run. If I set a GEMINI_API_KEY and `pip install google-genai`, dropping `--no-llm` produces LLM-written prose instead, still grounded to the same retrieved songs.

## Structure I want the talk to follow

1. Hook / problem: forms are rigid; I want to ask for music in plain English.
2. What the original system did (1 slide, fast).
3. What I added and why it's RAG (retrieve -> guardrail -> generate).
4. Architecture diagram walkthrough.
5. Live demo (the 4-5 commands above).
6. Reliability: how I know it works (tests + eval + refusal).
7. Responsible AI: limitations/bias, misuse + prevention, what surprised me.
8. AI collaboration: one helpful + one flawed suggestion.
9. Close: what this says about me as an AI engineer + GitHub link.

Now produce the deliverables in the order I listed under "What I want you to produce."

---

## After Claude gives you the deck

- Put the slides into Google Slides / PowerPoint yourself (Claude gives you the outline + notes, not the file).
- Practice the demo once end to end so the terminal is already in the right folder before you present.
- Have the three real outputs above pasted into a backup slide in case live typing fails.
