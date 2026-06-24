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
and prints today's schedule. The scheduler orders tasks by priority, fits them into
the 90 minutes available, and explains anything it had to leave off:

```
Today's Schedule for Jordan (90 min available)
================================================
  Luna: [ ] 09:00 - Give medicine (5 min) [priority: high]
  Mochi: [ ] 08:45 - Breakfast (10 min) [priority: high]
  Mochi: [ ] 08:00 - Morning walk (30 min) [priority: high]
  Luna: [ ] 19:00 - Brush fur (15 min) [priority: medium]

Left off (not enough time):
  Mochi: Evening fetch needs 45 min

Time used: 60/90 min
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite from inside this project folder:
cd ai110-module2show-pawpal-starter-main
python -m pytest
```

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\15045\Desktop\CodePath\ai110-module2show-pawpal-starter-main
collected 3 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 33%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 66%]
tests/test_pawpal.py::test_scheduler_skips_tasks_that_do_not_fit PASSED  [100%]

============================== 3 passed in 0.05s ==============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
