"""Quick tests for the most important PawPal+ behaviors."""

from pawpal_system import Owner, Pet, Task, Scheduler


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip the task from not-done to done."""
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False        # starts not done
    task.mark_complete()
    assert task.completed is True         # now done


def test_adding_task_increases_pet_task_count():
    """Adding a task to a pet should increase that pet's task count."""
    pet = Pet("Mochi", species="dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Breakfast", duration_minutes=10, priority="high"))
    assert pet.task_count() == 1
    pet.add_task(Task("Evening fetch", duration_minutes=20, priority="low"))
    assert pet.task_count() == 2


def test_scheduler_skips_tasks_that_do_not_fit():
    """A task longer than the available time should be left off, not silently dropped."""
    owner = Owner("Jordan", minutes_available=20)
    pet = Pet("Luna", species="cat")
    pet.add_task(Task("Quick meds", duration_minutes=5, priority="high"))
    pet.add_task(Task("Long grooming", duration_minutes=60, priority="medium"))
    owner.add_pet(pet)

    scheduled, skipped = Scheduler().build_plan(owner)

    scheduled_titles = [task.description for _, task in scheduled]
    skipped_titles = [task.description for _, task in skipped]
    assert "Quick meds" in scheduled_titles
    assert "Long grooming" in skipped_titles
