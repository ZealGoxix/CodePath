# RAG Recommender — Evaluation Report

Generator backend: `offline-template`

**Score: 6/6 cases passed.**

| # | Query (input) | Criteria | Top retrieved | Confidence | Grounded | Result |
|---|---------------|----------|---------------|------------|----------|--------|
| 1 | high energy music for the gym | top hit should be a workout/high-energy track | Gym Hero | 0.644 (high) | yes | PASS — ok |
| 2 | calm piano for late night studying | top hit should be a calm study/piano track | Midnight Coding | 0.429 (high) | yes | PASS — ok |
| 3 | smooth romantic song for a date night | top hit should be a romantic r&b track | Slow Dance Tonight | 0.561 (high) | yes | PASS — ok |
| 4 | aggressive heavy metal to get pumped | top hit should be an aggressive metal/rock track | Iron Verdict | 0.511 (high) | yes | PASS — ok |
| 5 | chill tropical beach vibes | top hit should be a reggae/tropical track | Canyon Drive | 0.519 (high) | yes | PASS — ok |
| 6 | purple elephant tax spreadsheet | nonsense query should be refused (no confident match) | — (refused) | 0.000 (none) | n/a | PASS — correctly refused |

_Retrieval hit = expected song appears in top-k. Grounded = generated answer names only retrieved songs. The nonsense query is expected to be refused by the confidence guardrail._
