# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

---

## 2. Intended Use  

**Goal:** VibeFinder takes what a person says they like (a genre, a mood, and an energy level) and suggests songs from my catalog that fit that vibe. It also tells you why it picked each one.

**Who it's for:** this is a classroom project, not a real app. I built it to learn how recommenders turn data into predictions, so it's for exploring the idea, not for actual listeners.

**What it assumes:** it assumes the user can describe their taste in a few simple fields, and that a song's vibe can be captured by its genre, mood, and energy. It also assumes every user knows their favorite genre and mood up front.

**Not intended for:** real music apps, big catalogs, or any decision that actually matters to someone. It has no idea about lyrics, language, artist history, or how your taste changes over time.

---

## 3. How the Model Works  

Think of it like a points game. Every song starts at zero, then it earns points based on how well it lines up with what you asked for:

- Same genre as you want: +2 points. This is the biggest one.
- Same mood as you want: +1 point.
- Energy close to your target: up to +1 point. The closer the song's energy is to yours, the more points it gets.
- If you said you like acoustic songs and the song is pretty acoustic: a small +0.5 bonus.

Once every song has a score, I sort them from highest to lowest and hand back the top few. Genre is worth the most on purpose, since I think the genre is the biggest part of a vibe.

The starter code just returned the first few songs with no real logic. I filled in the CSV loading, the point scoring, and the sorting, and I made it explain each pick.

---

## 4. Data  

My catalog started at 18 songs. Each one has a genre, mood, energy, tempo, valence, danceability, and acousticness. The starter came with 10 songs, and I added 8 more to get a wider range. For the Applied AI extension (Part 10) I grew it to 28 songs and added a free-text `tags` column so the retriever has real words to match against.

Genres in the set: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, country, classical, edm, folk, metal, and reggae. Moods range from happy and chill to intense, angry, romantic, and nostalgic.

What's missing: it's tiny, so most genres only have one or two songs. There's nothing in other languages, no big global genres like k-pop or afrobeats, and no sense of how popular a song is. So it covers a little bit of a lot, but not much of anything.

---

## 5. Strengths  

It works best when a user gives a clear, matching set of prefs. The Chill Lofi profile is the best example: it asked for lofi, chill, low energy, and acoustic, and the top picks were exactly the calm lofi tracks I'd expect. That one felt right.

It also does a good job stacking reasons. When a song matches genre and mood and energy, it clearly floats to the top, and the "why" line shows all three. And when two users want the same energy but different genres, the genre weight correctly splits them so a rock fan gets rock and a pop fan gets pop.

---

## 6. Limitations and Bias 

The main weakness I found is that my energy score never punishes a bad match, it only adds points. I use `1 - abs(song_energy - target)`, and since energy sits between 0 and 1, every song still walks away with some energy points. So even when nothing really fits the user, the system still hands back a confident top 5. My "sad + high energy" test proved this: "sad" isn't even a mood in my catalog and I gave no genre, so mood and genre could never match, yet the recommender still ranked five high energy songs like they were great picks. It also over-trusts genre, so a pop song with the wrong mood (Gym Hero, which is intense not happy) beats a happy song from another genre. And the catalog is only 18 songs, so a few genres barely show up and the variety is thin.

---

## 7. Evaluation  

I tested four profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, and a
conflicting one (sad mood + high energy). Here's what each one printed.

**High-Energy Pop** `{genre: pop, mood: happy, energy: 0.9}`

```
1. Sunrise City by Neon Echo  (score 3.92)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.92)
2. Gym Hero by Max Pulse  (score 2.97)
   why: genre match (+2.0), energy close to target (+0.97)
3. Rooftop Lights by Indigo Parade  (score 1.86)
   why: mood match (+1.0), energy close to target (+0.86)
4. Storm Runner by Voltline  (score 0.99)
   why: energy close to target (+0.99)
5. Voltage Drop by Pulsewave  (score 0.95)
   why: energy close to target (+0.95)
```

**Chill Lofi** `{genre: lofi, mood: chill, energy: 0.3, likes_acoustic: True}`

```
1. Library Rain by Paper Lanterns  (score 4.45)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.95), acoustic pick (+0.5)
2. Midnight Coding by LoRoom  (score 4.38)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.88), acoustic pick (+0.5)
3. Focus Flow by LoRoom  (score 3.40)
   why: genre match (+2.0), energy close to target (+0.90), acoustic pick (+0.5)
4. Spacewalk Thoughts by Orbit Bloom  (score 2.48)
   why: mood match (+1.0), energy close to target (+0.98), acoustic pick (+0.5)
5. Moonlit Sonata Redux by Clara Vance  (score 1.50)
   why: energy close to target (+1.00), acoustic pick (+0.5)
```

**Deep Intense Rock** `{genre: rock, mood: intense, energy: 0.95}`

```
1. Storm Runner by Voltline  (score 3.96)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.96)
2. Gym Hero by Max Pulse  (score 1.98)
   why: mood match (+1.0), energy close to target (+0.98)
3. Voltage Drop by Pulsewave  (score 1.00)
   why: energy close to target (+1.00)
4. Iron Verdict by Ashen Crown  (score 0.98)
   why: energy close to target (+0.98)
5. Sunrise City by Neon Echo  (score 0.87)
   why: energy close to target (+0.87)
```

**Conflicting (sad + high energy)** `{mood: sad, energy: 0.95}`

```
1. Voltage Drop by Pulsewave  (score 1.00)
   why: energy close to target (+1.00)
2. Gym Hero by Max Pulse  (score 0.98)
   why: energy close to target (+0.98)
3. Iron Verdict by Ashen Crown  (score 0.98)
   why: energy close to target (+0.98)
4. Storm Runner by Voltline  (score 0.96)
   why: energy close to target (+0.96)
5. Sunrise City by Neon Echo  (score 0.87)
   why: energy close to target (+0.87)
```

### What surprised me

Gym Hero kept popping up. For the Happy Pop user it lands at #2 even though the
song's mood is "intense," not happy. Here's the plain version: my system gives a
big +2 just for being pop, and Gym Hero is pop with high energy, so those points
alone push it past songs that actually match the "happy" feeling. It matches the
label the user asked for (pop) without matching the vibe (happy).

### Comparing the profiles

- **High-Energy Pop vs Chill Lofi:** total opposites, and the output shows it. Pop pulls bright, high energy pop tracks; lofi pulls calm, low energy, acoustic ones. The acoustic bonus only kicks in for the lofi user because they set `likes_acoustic: True`. This is the system working the way I want.
- **High-Energy Pop vs Deep Intense Rock:** both want high energy, so the bottom of both lists shares the same loud songs (Storm Runner, Voltage Drop). The tops differ because genre splits them: pop songs win for the pop user, rock wins for the rock user. Makes sense.
- **Chill Lofi vs Conflicting:** the cleanest match vs the messiest. Lofi hits genre, mood, energy, and acoustic all at once and scores over 4. The conflicting profile can't match genre or mood at all, so every song scores around 1 and it just ranks by energy. Same code, but one gets a real recommendation and the other basically gets a coin flip dressed up as a top 5.

### Experiment

I doubled energy's weight and halved genre's (genre 1.0, energy weight 2.0). For the Happy Pop user, off-genre high energy songs like Storm Runner (rock) and Voltage Drop (edm) climbed up the list because genre no longer carried them down. The results got more *different*, not more *accurate*, since I still want a pop fan to mostly hear pop. So I kept my original weights.

---

## 8. Future Work  

If I kept building this, I'd try:

1. Make the energy score able to lose points, so a song that's way off in energy actually gets pushed down instead of still scoring positive.
2. Add a check so the system says "I don't have a good match" when nothing really fits, instead of always faking a confident top 5.
3. Grow the catalog and use more features like tempo and valence, so there's more variety and the picks aren't leaning so hard on genre.

---

## 9. Personal Reflection  

My biggest learning moment was realizing a recommendation is really just sorting. Once every song has a score, "recommending" is nothing more than putting them in order and grabbing the top ones. That made the whole thing feel way less magic and way more like a points game I set the rules for.

AI tools helped me move fast, especially for the CSV loading and getting the scoring set up cleanly. But I had to double-check the logic, not just trust it. The weights, what counts as a match, and catching that my energy score never actually penalizes a bad song were all things I had to think through myself. The AI could write code, but it couldn't decide what "a good recommendation" means for me.

What surprised me most was how a few simple rules still "feel" like a real recommendation. There's no fancy machine learning here, just add points and sort, and yet the Chill Lofi list looked like something a real app might show me. It made me realize the recommendation apps I use every day are probably built on the same basic idea, just way bigger. If I extended this, I'd want it to learn from what I actually skip and replay, instead of me having to tell it my taste up front.

---

## 10. Applied AI Extension: the RAG recommender (reflection)

This section is the reflection for the Applied AI project. The original scorer above stays the same. On top of it I added a Retrieval-Augmented Generation path so I can ask for music in plain English ("calm piano for late night studying") instead of filling in a genre/mood/energy form. It retrieves the closest songs from the catalog, generates a short recommendation grounded only in those songs, scores its own confidence, and refuses when nothing fits.

### What I built and why it counts as RAG

The "retrieve" step turns every song into a small text document and ranks them against my query with TF-IDF and cosine similarity ([src/rag.py](src/rag.py)). The "generate" step only ever sees the retrieved songs and writes the recommendation from them ([src/generator.py](src/generator.py)). That retrieve-then-generate order, plus a rule that the answer can only name songs that were retrieved, is what makes it real RAG and not just search or just generation.

## 11. Responsible AI Reflection

These are the responsible-AI questions for the Applied AI project, each under its own header.

### What are the limitations or biases in the system?

- **Lexical, not semantic, retrieval.** TF-IDF only matches shared words, so it leans on my hand-written tags. A query like "music for a rainy commute" only works if those words (or close ones) appear in a song's tags. Real embeddings would understand meaning, but I traded that away for reproducibility and a tiny install.
- **Tagging bias is my bias.** I wrote every tag by hand, so the system inherits my vocabulary and my genre knowledge. Words and scenes I didn't think to tag are matches the system simply cannot make, and that gap is not spread evenly across genres.
- **Popularity and culture gaps carried over from the base system.** The catalog is 28 English-language songs with no k-pop, afrobeats, regional, or non-English music, and no sense of what is actually popular. So it can only recommend inside a narrow slice of taste.
- **The offline generator is templated.** Without an API key the recommendation reads like a filled-in sentence, not natural prose. The LLM path fixes the tone but needs a key and a network, so it is off by default.
- **The confidence score is a proxy.** It comes from retrieval strength, not from any judgment about whether the song is actually good for the request. A well-tagged but wrong song could still score "high." The eval set is what keeps me honest about that.

### Could this AI be misused, and how would I prevent that?

I can see a few realistic ways this kind of system gets misused, and what I built (or would build) against each:

- **Hallucinated recommendations passed off as real.** If the LLM invents a song or artist, a user could act on something that does not exist. Prevention: the generator is only allowed to name songs that were retrieved, and the LLM output runs through a grounding check that falls back to the deterministic generator if it drifts. The model can't recommend outside the catalog.
- **Fake confidence on a bad match.** A system that always returns a confident answer can nudge people toward things that don't fit them. Prevention: the confidence floor makes weak retrieval refuse instead of guessing, so the system says "I don't have a good match" rather than bluffing.
- **Prompt injection through the query or tags.** Because a free-text query is fed into an LLM prompt, someone could try to smuggle instructions in. Prevention today: the offline path never calls a model at all, and the LLM prompt is constrained to the retrieved rows. If I productionized it I would add input sanitization and cap query length.
- **Scaling the taste bias.** If this grew into a real recommender, the tagging bias above would quietly steer many listeners. Prevention: keep a human-reviewed eval set (like `eval/eval_report.md`) and watch for whole genres or moods that never surface.

### What surprised me while testing the AI's reliability?

The biggest surprise was that the refusal guardrail was harder to keep alive than the recommendations. My first instinct (and the AI's first suggestion) was to always return the top k songs so the output never looked empty. When I tested a nonsense query like "purple elephant tax spreadsheet," that "always full" behavior handed back three confident songs for a query that means nothing. The system looked more broken when it was trying to look complete. Making retrieval able to return *nothing*, and letting the confidence floor turn that into an honest refusal, was what actually made it reliable. It flipped my thinking: reliability was less about better matches and more about the system knowing when to say no.

The second surprise was how much retrieval quality rode on my tags rather than the model. A query worked or failed based on words I had written days earlier, not on anything clever at generation time. That made "garbage in, garbage out" very concrete.

### My collaboration with AI during this project

I used an AI coding assistant to build the extension. I gave it the existing recommender and asked it to add a RAG path that stays reproducible and testable. It drafted the TF-IDF retriever, the confidence-and-refusal guardrail, the offline vs LLM generator split, the eval harness, and the tests. I made the design calls: keep retrieval pure-Python and offline, make the LLM optional, and enforce grounding instead of trusting it. I also reused the Gemini client pattern from my Module 4 DocuBot so the LLM path matched something I already understood.

**One helpful AI suggestion.** The assistant suggested I not use the LLM output blindly, and instead run a grounding check that confirms the generated answer only names songs that were actually retrieved, and fall back to the deterministic generator if it drifts. That closed the exact hole that makes RAG demos fail, a model quietly inventing a song that sounds right but isn't in the catalog. It turned "trust the model" into "verify the model," which is the whole point of a reliability harness.

**One flawed AI suggestion.** Early on it wanted to pad retrieval so it always returned k songs even when a query matched nothing, so the output never looked empty. That directly fights the guardrail I wanted: if I always return 3 songs, "purple elephant tax spreadsheet" gets a confident top 3 and the refusal path is dead code. I overrode it so retrieval drops zero-overlap songs and can return fewer than k (or none), which is what lets the confidence floor actually refuse. It was optimizing for a full-looking screen instead of an honest answer.
