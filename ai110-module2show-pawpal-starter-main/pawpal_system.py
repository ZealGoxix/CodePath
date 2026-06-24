"""PawPal+ system logic.

Four classes work together:
- Task: one activity that needs doing for a pet.
- Pet: one animal, with its own list of tasks.
- Owner: the person, who has one or more pets.
- Scheduler: the "brain" that gathers tasks and builds a daily plan.
"""

from datetime import date, timedelta

# How important each priority word is. Bigger number = do it sooner.
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

# How far ahead to push a repeating task when it's done.
FREQUENCY_STEP = {"daily": timedelta(days=1), "weekly": timedelta(days=7)}


class Task:
    """Represents a single activity (description, time, frequency, done-or-not)."""

    def __init__(self, description, time=None, frequency="daily",
                 duration_minutes=15, priority="medium", category="general",
                 due_date=None):
        self.description = description
        self.time = time                       # preferred time, e.g. "08:00" (or None)
        self.frequency = frequency             # e.g. "daily", "weekly", "once"
        self.duration_minutes = duration_minutes
        self.priority = priority               # "low" / "medium" / "high"
        self.category = category               # e.g. "walk", "feeding", "meds"
        self.due_date = due_date               # date this is due (or None for today)
        self.completed = False                 # starts as not done

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self):
        """Mark this task as not done (handy for the next day)."""
        self.completed = False

    def next_occurrence(self):
        """Make the next copy of a repeating task, or None if it doesn't repeat."""
        step = FREQUENCY_STEP.get(self.frequency)
        if step is None:
            return None                        # one-off task: nothing to repeat
        base = self.due_date or date.today()
        return Task(
            self.description,
            time=self.time,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            due_date=base + step,              # today + 1 day (daily) or + 7 (weekly)
        )

    def priority_score(self):
        """Turn the priority word into a number so tasks can be sorted."""
        return PRIORITY_RANK.get(self.priority, 0)

    def is_high_priority(self):
        """Return True if this task is high priority."""
        return self.priority == "high"

    def __str__(self):
        """Readable one-line version of the task."""
        when = self.time if self.time else "anytime"
        check = "x" if self.completed else " "
        return (f"[{check}] {when} - {self.description} "
                f"({self.duration_minutes} min) [priority: {self.priority}]")

    def __repr__(self):
        return f"Task({self.description!r}, priority={self.priority!r})"


class Pet:
    """Stores pet details and a list of tasks."""

    def __init__(self, name, species, breed=""):
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks = []                        # list of Task objects

    def add_task(self, task):
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self):
        """Return all care tasks for this pet."""
        return self.tasks

    def pending_tasks(self):
        """Return only the tasks that are not done yet."""
        return [task for task in self.tasks if not task.completed]

    def task_count(self):
        """Return how many tasks this pet has."""
        return len(self.tasks)

    def mark_task_complete(self, task):
        """Mark a task done and, if it repeats, line up the next one automatically."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task                       # the new task, or None if it was one-off

    def __str__(self):
        breed = f" ({self.breed})" if self.breed else ""
        return f"{self.name} the {self.species}{breed}"


class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name, minutes_available=0, preferences=None):
        self.name = name
        self.minutes_available = minutes_available   # free time today, in minutes
        self.preferences = preferences or []         # e.g. ["walk in the morning"]
        self.pets = []                               # list of Pet objects

    def add_pet(self, pet):
        """Add a Pet to this owner."""
        self.pets.append(pet)

    def list_pets(self):
        """Return all of this owner's pets."""
        return self.pets

    def get_all_tasks(self):
        """Return every task across all pets, paired with the pet it belongs to.

        Each item is a (pet, task) tuple so the plan can say whose task it is.
        """
        all_tasks = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet, task))
        return all_tasks


class Scheduler:
    """The 'brain' that retrieves, organizes, and manages tasks across pets."""

    def __init__(self, minutes_available=None):
        # If not given, the scheduler will use the owner's available time.
        self.minutes_available = minutes_available

    def get_tasks_from_owner(self, owner, only_pending=True):
        """Pull all (pet, task) pairs from the owner's pets."""
        pairs = owner.get_all_tasks()
        if only_pending:
            pairs = [(pet, task) for pet, task in pairs if not task.completed]
        return pairs

    def sort_by_priority(self, pairs):
        """Order (pet, task) pairs so the most important, shortest tasks come first."""
        # High priority first; if tied, the quicker task goes first.
        return sorted(
            pairs,
            key=lambda pair: (-pair[1].priority_score(), pair[1].duration_minutes),
        )

    def sort_by_time(self, tasks):
        """Order Task objects by their time of day ('HH:MM'); 'anytime' tasks go last."""
        # "99:99" sorts after any real "HH:MM" string, so timeless tasks land at the end.
        return sorted(tasks, key=lambda task: task.time or "99:99")

    def filter_by_status(self, tasks, completed):
        """Return only the tasks whose done/not-done status matches `completed`."""
        return [task for task in tasks if task.completed == completed]

    def filter_by_pet(self, owner, pet_name):
        """Return the tasks belonging to the pet with this name."""
        for pet in owner.list_pets():
            if pet.name == pet_name:
                return pet.get_tasks()
        return []                              # no pet by that name

    def detect_conflicts(self, owner):
        """Find tasks scheduled at the same time and return a list of warning strings.

        Lightweight on purpose: it only compares exact start times and returns
        warnings instead of raising errors, so the app never crashes over a clash.
        """
        by_time = {}
        for pet, task in owner.get_all_tasks():
            if task.completed or not task.time:
                continue                       # skip done tasks and "anytime" tasks
            by_time.setdefault(task.time, []).append((pet, task))

        warnings = []
        for time_str in sorted(by_time):
            items = by_time[time_str]
            if len(items) > 1:
                clashing = ", ".join(f"{pet.name}'s {task.description}"
                                     for pet, task in items)
                warnings.append(
                    f"Conflict at {time_str}: {clashing} are scheduled at the same time."
                )
        return warnings

    def build_plan(self, owner):
        """Pick and order tasks that fit inside the owner's available time.

        Returns a tuple: (scheduled, skipped).
        - scheduled: list of (pet, task) chosen for today, in order.
        - skipped:   list of (pet, task) that did not fit, with a reason.
        """
        minutes = self.minutes_available
        if minutes is None:
            minutes = owner.minutes_available

        pairs = self.sort_by_priority(self.get_tasks_from_owner(owner))

        scheduled = []
        skipped = []
        time_left = minutes
        for pet, task in pairs:
            if task.duration_minutes <= time_left:
                scheduled.append((pet, task))
                time_left -= task.duration_minutes
            else:
                skipped.append((pet, task))
        return scheduled, skipped

    def explain_plan(self, owner):
        """Build a readable 'Today's Schedule' string with reasoning."""
        scheduled, skipped = self.build_plan(owner)
        minutes = self.minutes_available
        if minutes is None:
            minutes = owner.minutes_available

        lines = []
        lines.append(f"Today's Schedule for {owner.name} "
                     f"({minutes} min available)")
        lines.append("=" * 48)

        if scheduled:
            for pet, task in scheduled:
                lines.append(f"  {pet.name}: {task}")
        else:
            lines.append("  (nothing fits in the time available)")

        if skipped:
            lines.append("")
            lines.append("Left off (not enough time):")
            for pet, task in skipped:
                lines.append(f"  {pet.name}: {task.description} "
                             f"needs {task.duration_minutes} min")

        used = sum(task.duration_minutes for _, task in scheduled)
        lines.append("")
        lines.append(f"Time used: {used}/{minutes} min")
        return "\n".join(lines)
