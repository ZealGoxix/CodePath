# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Running `python main.py` builds a small example (one owner, two pets, five tasks)
and shows off the scheduling features: building today's plan, sorting, filtering,
recurring tasks, and conflict detection.

```
Today's Schedule for Jordan (90 min available)
================================================
  Luna: [ ] 08:00 - Give medicine (5 min) [priority: high]
  Mochi: [ ] 08:45 - Breakfast (10 min) [priority: high]
  Mochi: [ ] 08:00 - Morning walk (30 min) [priority: high]
  Luna: [ ] 19:00 - Brush fur (15 min) [priority: medium]

Left off (not enough time):
  Mochi: Evening fetch needs 45 min

Time used: 60/90 min

All of Mochi's tasks, sorted by time of day:
  [ ] 08:00 - Morning walk (30 min) [priority: high]
  [ ] 08:45 - Breakfast (10 min) [priority: high]
  [ ] 18:00 - Evening fetch (45 min) [priority: low]

Filtering: just Luna's tasks:
  [ ] 19:00 - Brush fur (15 min) [priority: medium]
  [ ] 08:00 - Give medicine (5 min) [priority: high]

Recurring: finishing Mochi's daily walk lines up tomorrow's:
  Completed: Morning walk (done = True)
  Auto-created next: Morning walk due 2026-06-24

Filtering: Mochi's tasks still left to do:
  [ ] 18:00 - Evening fetch (45 min) [priority: low]
  [ ] 08:45 - Breakfast (10 min) [priority: high]
  [ ] 08:00 - Morning walk (30 min) [priority: high]

Conflict check:
  [!] Conflict at 08:00: Mochi's Morning walk, Luna's Give medicine are scheduled at the same time.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite from inside this project folder:
cd ai110-module2show-pawpal-starter-main
python -m pytest
```

**What the tests cover** (12 tests in `tests/test_pawpal.py`):

- **Tasks** — marking a task complete flips its status; adding a task bumps a pet's task count.
- **Sorting** — tasks come back in time order ("anytime" tasks last).
- **Filtering** — splitting tasks by done/not-done status and by pet.
- **Recurring tasks** — finishing a daily task auto-creates tomorrow's copy, a weekly task creates one a week later, and a one-off task makes no copy.
- **Conflict detection** — two tasks at the same time get flagged; tasks at different times don't.
- **Edge cases** — an owner with no tasks still gets a valid (empty) plan instead of an error.

**Confidence level: ⭐⭐⭐⭐☆ (4 / 5)** — all the core behaviors and the obvious edge cases pass. I dropped one star because conflict detection only checks exact start times (not overlapping durations), so I'd want more time-overlap tests before calling it bullet-proof.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\15045\Desktop\CodePath\ai110-module2show-pawpal-starter-main
collected 12 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  8%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 16%]
tests/test_pawpal.py::test_scheduler_skips_tasks_that_do_not_fit PASSED  [ 25%]
tests/test_pawpal.py::test_sort_by_time_orders_by_time_of_day PASSED     [ 33%]
tests/test_pawpal.py::test_filter_by_status_returns_only_matching_tasks PASSED [ 41%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_occurrence PASSED [ 50%]
tests/test_pawpal.py::test_one_off_task_does_not_repeat PASSED           [ 58%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time_tasks PASSED [ 66%]
tests/test_pawpal.py::test_owner_with_no_tasks_makes_empty_plan PASSED   [ 75%]
tests/test_pawpal.py::test_no_conflict_when_times_differ PASSED          [ 83%]
tests/test_pawpal.py::test_daily_task_next_due_date_is_exactly_one_day_later PASSED [ 91%]
tests/test_pawpal.py::test_weekly_task_next_due_date_is_seven_days_later PASSED [100%]

============================== 12 passed in 0.06s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Scheduler.sort_by_priority()` | High priority first; ties broken by shorter duration. Used to build the daily plan. |
| Sort by time | `Scheduler.sort_by_time()` | Orders tasks by their `"HH:MM"` time of day; "anytime" tasks go last. |
| Filter by status | `Scheduler.filter_by_status()` | Returns just the done (or not-done) tasks. |
| Filter by pet | `Scheduler.filter_by_pet()` | Returns the tasks belonging to one named pet. |
| Conflict detection | `Scheduler.detect_conflicts()` | Lightweight: flags tasks with the **same start time** and returns warning strings instead of crashing. (Does not compare durations — see reflection 2b.) |
| Recurring tasks | `Task.next_occurrence()`, `Pet.mark_task_complete()` | Completing a `daily`/`weekly` task auto-creates the next one, with the due date pushed using `timedelta`. |
| Fit to time budget | `Scheduler.build_plan()`, `Scheduler.explain_plan()` | Greedily fills the day's minutes and reports anything left off. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
