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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
