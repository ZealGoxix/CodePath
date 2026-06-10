# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game it looked fine on the outside, like a normal number guessing game with a box and a submit button. But once I actually started playing it was kind of a mess. The hints were lying to me, like it would say "Go HIGHER" when I had already guessed too high. I also opened the Developer Debug Info tab and the game felt impossible to win because the answers it gave me didnt make sense. The two bugs that stood out the most were the backwards hints and the way the secret number seemed to act weird every other guess.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Secret = 50, guess 60 | Hint should say "Go LOWER" because 60 is too high | Hint said "Go HIGHER" (hints were backwards) | No error, just wrong hint text |
| Secret = 50, even numbered attempt | Compare my guess to the number 50 normally | On every even attempt it turned the secret into a string ("50"), so an int vs string compare broke and hints went random | No crash, silently wrong |
| Secret = 50, guess 60 (too high) on an even attempt | Wrong guess should not give me points | update_score actually ADDED +5 points for a "Too High" guess sometimes | No error, score just went up when it shouldnt |

---

## 2. How did you use AI as a teammate?

I used the Claude Code assistant in my editor (agent mode) and I also asked ChatGPT some questions when I got stuck on the Streamlit state stuff. I mostly used the AI to help me move the logic into logic_utils.py and to talk through why the hints were wrong.

**Correct suggestion (it actually helped):**
The AI suggested that the secret number should always be stored as one type and not be turned into a string every other turn. So it told me to delete the part that did `secret = str(st.session_state.secret)` on even attempts and just always use the int from session_state. This was correct. I verified it by opening the Developer Debug Info panel and playing a few rounds. Before the fix the hints flipped around randomly, after the fix the same secret stayed the same all game and the hints lined up with the real number every time. My pytest tests also stayed green after the change.

**Incorrect / misleading suggestion (I had to push back):**
When I asked about the int vs string compare, one suggestion was to "just wrap the compare in a try/except and convert the guess to a string if it errors out." That looked smart but it was actually misleading, because comparing strings does alphabetical order, not number order (for example "100" < "20" is True as strings, which is totally wrong for a guessing game). It would of hidden the bug instead of really fixing it. I figured out it was wrong by testing it in the game, the hints were still off, and I also reasoned through it with a quick check that string comparison gives the wrong answer. So instead of keeping that band-aid, I removed the whole try/except and made check_guess just compare two ints cleanly.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed when both the game AND the tests agreed it was working, not just one of them. For the backwards hint bug I wrote a pytest in tests/test_game_logic.py called `test_high_low_not_reversed`. It checks that `check_guess(99, 1)` returns "Too High" and `check_guess(1, 99)` returns "Too Low". I picked those numbers because they are far apart so if the high/low logic was flipped it would deffinitely fail. I ran `python -m pytest tests/ -v` in the terminal and all 4 tests passed (the 3 starter ones plus my new one).

I also did manual testing in the actual game. I opened the Developer Debug Info tab so I could see the secret, then I guessed on purpose too high and too low and made sure the hint matched. Before my fix the hint would say "Go HIGHER" after I guessed too high, after the fix it correctly says "Go LOWER". The AI did help me with the tests, it suggested the idea of testing a guess of 60 against a secret of 50 for the "Too High" case, and I built on that by adding the far apart 99 vs 1 case so the test was harder to accidentally pass.

```
tests/test_game_logic.py::test_winning_guess PASSED
tests/test_game_logic.py::test_guess_too_high PASSED
tests/test_game_logic.py::test_guess_too_low PASSED
tests/test_game_logic.py::test_high_low_not_reversed PASSED
============================== 4 passed in 0.41s ==============================
```

---

## 4. What did you learn about Streamlit and state?

The way I would explain it to a friend is that Streamlit runs your whole python file again from top to bottom every single time you click a button or type something. So it has like really bad short term memory, normal variables get wiped and made fresh every time. That is why session_state exists, its basically a little backpack that survives the reruns, so anything you want to remember (like the secret number, the score, the attempts) you have to put it in session_state or it will reset. This whole project clicked for me once I realized the secret was only safe because it was in session_state, and the bug got worse because the code kept messing with that state in weird ways.

---

## 5. Looking ahead: your developer habits

One habit I want to keep is writing a small pytest right after I fix something instead of just eyeballing it. Having a test that fails on the bug and passes on the fix gave me way more confidence than just clicking around. Next time I would do a better job of not trusting the AI code right away, in this project the AI literally left a caption saying the code was "production-ready" and it was super broken, so I learned to read what it gives me before I run it. Overall this project changed how I think about AI code, I see it now as a fast teammate that gives me a starting point, but I am the one who has to actually check it and own whether its right.
