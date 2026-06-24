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


def test_sort_by_time_orders_by_time_of_day():
    """sort_by_time() should put earlier times first and 'anytime' tasks last."""
    tasks = [
        Task("Evening fetch", time="18:00"),
        Task("Morning walk", time="08:00"),
        Task("Whenever play", time=None),
    ]
    ordered = [t.description for t in Scheduler().sort_by_time(tasks)]
    assert ordered == ["Morning walk", "Evening fetch", "Whenever play"]


def test_filter_by_status_returns_only_matching_tasks():
    """filter_by_status() should split done from not-done tasks."""
    done = Task("Breakfast")
    done.mark_complete()
    not_done = Task("Walk")
    tasks = [done, not_done]

    scheduler = Scheduler()
    assert scheduler.filter_by_status(tasks, completed=True) == [done]
    assert scheduler.filter_by_status(tasks, completed=False) == [not_done]


def test_completing_daily_task_creates_next_occurrence():
    """Finishing a daily task should auto-add a fresh copy with a later due date."""
    pet = Pet("Mochi", species="dog")
    walk = Task("Morning walk", time="08:00", frequency="daily")
    pet.add_task(walk)

    next_task = pet.mark_task_complete(walk)

    assert walk.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert pet.task_count() == 2          # original + the new copy


def test_one_off_task_does_not_repeat():
    """A 'once' task should not create a next occurrence when completed."""
    pet = Pet("Luna", species="cat")
    vet = Task("Vet visit", time="14:00", frequency="once")
    pet.add_task(vet)

    next_task = pet.mark_task_complete(vet)

    assert next_task is None
    assert pet.task_count() == 1


def test_detect_conflicts_flags_same_time_tasks():
    """Two tasks at the same start time should produce one warning."""
    owner = Owner("Jordan", minutes_available=120)
    mochi = Pet("Mochi", species="dog")
    luna = Pet("Luna", species="cat")
    mochi.add_task(Task("Morning walk", time="08:00"))
    luna.add_task(Task("Give medicine", time="08:00"))
    luna.add_task(Task("Brush fur", time="19:00"))   # no clash
    owner.add_pet(mochi)
    owner.add_pet(luna)

    warnings = Scheduler().detect_conflicts(owner)

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
