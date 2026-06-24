"""PawPal+ system skeleton.

These are the class "blueprints" for the app. There is no real scheduling
logic yet — just the shapes of the objects and what they will eventually do.
Implementation comes in a later step.
"""


class Owner:
    """The pet owner. Holds basic info and the pets they take care of."""

    def __init__(self, name, minutes_available=0, preferences=None):
        self.name = name
        self.minutes_available = minutes_available          # how much time they have today
        self.preferences = preferences or []               # e.g. ["walk in the morning"]
        self.pets = []                                     # list of Pet objects

    def add_pet(self, pet):
        """Add a Pet to this owner."""
        raise NotImplementedError

    def list_pets(self):
        """Return all of this owner's pets."""
        raise NotImplementedError


class Pet:
    """A single pet. Knows its own info and the care tasks it needs."""

    def __init__(self, name, species, breed=""):
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks = []                                    # list of CareTask objects

    def add_task(self, task):
        """Attach a care task to this pet."""
        raise NotImplementedError

    def get_tasks(self):
        """Return all care tasks for this pet."""
        raise NotImplementedError


class CareTask:
    """One thing that needs to get done for a pet (walk, feed, meds, etc.)."""

    def __init__(self, title, duration_minutes, priority="medium",
                 category="general", preferred_time=None):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority                           # "low" / "medium" / "high"
        self.category = category                           # e.g. "walk", "feeding", "meds"
        self.preferred_time = preferred_time               # e.g. "08:00" or None

    def priority_score(self):
        """Turn the priority word into a number so tasks can be sorted."""
        raise NotImplementedError

    def is_high_priority(self):
        """Return True if this task is high priority."""
        raise NotImplementedError


class Scheduler:
    """Takes a pile of tasks and builds a daily plan that fits the time limit."""

    def __init__(self, minutes_available):
        self.minutes_available = minutes_available

    def sort_by_priority(self, tasks):
        """Order tasks so the most important ones come first."""
        raise NotImplementedError

    def build_plan(self, tasks):
        """Pick and order tasks that fit inside the time available."""
        raise NotImplementedError

    def explain_plan(self, plan):
        """Return a short text explaining why the plan looks the way it does."""
        raise NotImplementedError
