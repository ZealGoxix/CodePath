"""PawPal+ system logic.

Four classes work together:
- Task: one activity that needs doing for a pet.
- Pet: one animal, with its own list of tasks.
- Owner: the person, who has one or more pets.
- Scheduler: the "brain" that gathers tasks and builds a daily plan.
"""

# How important each priority word is. Bigger number = do it sooner.
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


class Task:
    """Represents a single activity (description, time, frequency, done-or-not)."""

    def __init__(self, description, time=None, frequency="daily",
                 duration_minutes=15, priority="medium", category="general"):
        self.description = description
        self.time = time                       # preferred time, e.g. "08:00" (or None)
        self.frequency = frequency             # e.g. "daily", "weekly"
        self.duration_minutes = duration_minutes
        self.priority = priority               # "low" / "medium" / "high"
        self.category = category               # e.g. "walk", "feeding", "meds"
        self.completed = False                 # starts as not done

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self):
        """Mark this task as not done (handy for the next day)."""
        self.completed = False

    def priority_score(self):
        """Turn the priority word into a number so tasks can be sorted."""
        return PRIORITY_RANK.get(self.priority, 0)

    def is_high_priority(self):
        """Return True if this task is high priority."""
        return self.priority == "high"

    def __str__(self):
        """Readable one-line version of the task."""
        when = self.time if self.time else "anytime"
        check = "✓" if self.completed else " "
        return (f"[{check}] {when} — {self.description} "
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
