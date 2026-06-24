# PawPal+ Project Reflection

## 1. System Design

**Three core actions a user can do**

After reading the scenario, I picked the three things a pet owner most needs the app to do:

1. **Add a pet (and their own info).** The owner types in who they are, how much
   free time they have today, and adds one or more pets with basic details.
2. **Add a care task to a pet.** For each pet they add tasks like a walk, feeding,
   or medicine. Every task has a name, how long it takes, and how important it is.
3. **Get a daily plan.** The app looks at all the tasks and the time available,
   then builds a to-do list for the day in a sensible order and explains its choices.

**a. Initial design**

I went with four classes. Each one is in charge of one clear thing, which keeps the
app easy to follow:

- **Owner** — the person using the app. Holds their name, how many minutes they have
  today, their preferences (like "walks in the morning"), and the list of pets they
  own. It can add a pet and list its pets.
- **Pet** — one animal. Holds its name, species, and breed, plus the list of care
  tasks that belong to it. It can add a task, hand back its tasks, and count them.
- **Task** — a single thing that needs doing (walk, feeding, meds, etc.). Holds the
  description, the time of day, how often it repeats (frequency), how many minutes it
  takes, its priority, a category, and whether it's done yet. It can mark itself
  complete, turn its priority word into a number, and say whether it's high priority.
- **Scheduler** — the "brain." It takes the tasks and the time limit, sorts them by
  importance, and builds a plan that fits the available time. It can also explain why
  the plan looks the way it does.

The relationships are simple: an **Owner has many Pets**, a **Pet has many Tasks**,
and the **Scheduler reads the tasks and the time limit** to make the plan. The full
diagram is in [diagrams/uml.mmd](diagrams/uml.mmd).

**b. Design changes**

I had the AI assistant review my `pawpal_system.py` skeleton and look for missing links
or weak spots. Two things stood out:

1. **The plan couldn't tell you which pet a task belonged to.** In my first draft the
   Scheduler just took a flat list of tasks, so a plan line could say "Walk" but not
   "Mochi's walk." With more than one pet that gets confusing. **Change:** I made
   `build_plan` take the whole **Owner** and added `Owner.get_all_tasks()`, which hands
   back each task paired with its pet. Now every line of the plan can say whose task it
   is.
2. **A task longer than the whole day's time would just silently disappear.** If a
   task takes more minutes than the owner has, the early skeleton would have dropped it
   with no warning. **Change:** `build_plan` now returns both the scheduled tasks *and*
   a "skipped" list, and `explain_plan` prints a "Left off (not enough time)" section,
   so nothing vanishes without a reason the owner can see.

These are small but they make the app more honest and easier to trust.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler looks at two main things: how much **time** the owner has today, and how
**important** each task is. When I build the plan I sort tasks so the high-priority ones
come first, and if two tasks are equally important I put the quicker one first. Then I
add tasks one by one until the time runs out.

I picked time and priority as the most important because that's what a busy owner
actually worries about: "I only have an hour, so what really needs to happen?" Things
like the exact time of day matter too, but they're more of a "nice to have," so I use
those for sorting and showing the plan, not for deciding what makes the cut.

**b. Tradeoffs**

One tradeoff I made is in how my conflict checker works. It only flags two tasks as
clashing if they start at the **exact same time** (like both at 08:00). It does *not*
look at how long each task lasts, so a 30-minute walk at 08:00 and a feeding at 08:15
won't be flagged, even though they really do overlap in real life.

I think this is a fair tradeoff for now. Checking exact start times is simple, easy to
read, and fast, and it still catches the most obvious "I can't be in two places at once"
problems. Comparing full time ranges would be more accurate, but it adds a lot more
fiddly logic. Since PawPal+ is meant to be a helpful nudge and not a strict calendar, I'd
rather keep it simple and clear than make it complicated for a small gain.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant through the whole project, but for different jobs at each step:

- **Brainstorming the design** — at the start I described the app and had it help me come
  up with the four classes and a Mermaid diagram.
- **Writing code** — I had it flesh out the class methods, like the sorting and the
  recurring-task logic, and it showed me how to use `sorted()` with a lambda and how to
  add days with `timedelta`.
- **Writing tests** — I asked it for a test plan and to help draft the test functions,
  including edge cases I might not have thought of, like a pet with no tasks.
- **Cleaning up** — it helped me add docstrings and write the README.

The most helpful prompts were the **specific, "how do I do this one thing"** questions
(like "how do I sort `HH:MM` strings?") and asking it to **review a file and point out
problems**. Vague questions gave vague answers; specific ones gave me something I could
actually use.

The features I leaned on most were **agent/edit mode** (letting it edit files directly so
I could see real changes instead of copy-pasting) and **chat with files attached**, so it
could see my actual code before answering.

**b. Judgment and verification**

One time I didn't just accept what the AI gave me was with **conflict detection**. It
offered a fancier version that compared full time ranges (start + duration) to catch
overlaps. It was clever, but it added a lot of extra logic and was harder to read. I chose
the simpler "same start time" version instead, because it was easy to understand and good
enough for what the app needs right now. I wrote down that tradeoff in section 2b so I
don't forget it later.

To check the AI's suggestions, I didn't just trust them I **ran the code**. I'd run
`main.py` to watch the output, and I leaned on my tests with `python -m pytest`. If a test
went red, I'd ask the AI whether the bug was in my test or my actual logic, then fix the
real problem. Seeing it work (or fail) with my own eyes is what gave me confidence.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 12 small tests that check the parts of the app I care about most:

- **Tasks:** marking a task done actually flips it to done, and adding a task to a pet
  bumps that pet's task count up.
- **Sorting:** tasks come back in time order, with the "anytime" ones at the end.
- **Filtering:** I can pull out just the done (or not-done) tasks, or just one pet's tasks.
- **Recurring tasks:** finishing a daily task makes a fresh copy for tomorrow, a weekly
  task makes one for a week later, and a one-time task doesn't make a copy at all.
- **Conflicts:** two tasks at the same time get flagged, and tasks at different times
  don't get flagged by mistake.
- **Empty case:** an owner with no tasks still gets a valid (empty) plan instead of
  crashing.

These felt important because they're the things a real pet owner would actually rely on.
If sorting or the recurring logic quietly broke, the daily plan would be wrong and the
owner wouldn't know. Testing them means I can change the code later and quickly see if I
broke anything.

**b. Confidence**

I'd give myself about **4 out of 5 stars**. All 12 tests pass, and they cover both the
normal "everything works" cases and a few tricky ones like an empty schedule and tasks
that clash. So I feel good that the core logic does what I think it does.

The reason it's not 5 stars is that my conflict checker only catches tasks that start at
the *exact* same time. If I had more time, the first edge case I'd test is **overlapping
tasks** like a 30-minute walk at 08:00 bumping into a feeding at 08:15. I'd also want to
test weird inputs, like a task with a negative or zero duration, and a task with a badly
formatted time, to make sure the app handles junk data without crashing.

---

## 5. Reflection

**a. What went well**

The part I'm most happy with is the **recurring task feature**. It felt like real
"smart" behavior you tick off today's walk and tomorrow's walk just shows up on its own.
I also like that the whole thing is split into four clear classes, so when something broke
I usually knew exactly where to look. And keeping the logic (`pawpal_system.py`) separate
from the UI (`app.py`) meant I could test the brains of the app in the terminal without
fighting with Streamlit.

**b. What you would improve**

If I did another round, I'd make the **conflict checker smarter** so it catches tasks that
overlap, not just ones that start at the exact same minute. I'd also let the user **mark
tasks done and edit or delete them in the app** (right now you can mostly just add them),
and I'd **save the data to a file** so your pets and tasks don't disappear when you close
the app.

**c. Key takeaway**

The biggest thing I learned is what it feels like to be the **"lead architect"** instead of
just a coder. The AI could write code fast, but it didn't know what I actually wanted that
was my job. I made the calls on which classes to use and which suggestions to keep or toss
(like picking the simple conflict checker over the fancy one). The AI was great at the
"how," but I had to own the "what" and the "why."

A small trick that helped a lot was using **separate chat sessions for each phase** —
one for design, one for building, one for testing. It kept each conversation focused, so
the AI wasn't dragging old, unrelated context into a new task and I could think about one
thing at a time. Overall I learned that AI is a really strong helper, but it works best when
I stay in charge, ask specific questions, and always check its work by actually running it.
