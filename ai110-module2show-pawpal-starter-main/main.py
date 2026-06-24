"""Quick terminal demo for PawPal+.

This is a temporary testing ground. It builds a small example by hand and
shows off the scheduling features: sorting, filtering, recurring tasks, and
conflict detection.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # 1. Create an owner with 90 minutes free today.
    owner = Owner("Jordan", minutes_available=90,
                  preferences=["walks in the morning"])

    # 2. Create two pets.
    mochi = Pet("Mochi", species="dog", breed="Shiba Inu")
    luna = Pet("Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # 3. Add tasks ON PURPOSE OUT OF ORDER so sorting has something to do.
    mochi.add_task(Task("Evening fetch", time="18:00", duration_minutes=45,
                        priority="low", category="enrichment"))
    mochi.add_task(Task("Morning walk", time="08:00", duration_minutes=30,
                        priority="high", category="walk"))
    mochi.add_task(Task("Breakfast", time="08:45", duration_minutes=10,
                        priority="high", category="feeding"))
    luna.add_task(Task("Brush fur", time="19:00", duration_minutes=15,
                       priority="medium", category="grooming"))
    # This one clashes with Mochi's morning walk (both at 08:00).
    luna.add_task(Task("Give medicine", time="08:00", duration_minutes=5,
                       priority="high", category="meds"))

    scheduler = Scheduler()

    # --- Today's plan -----------------------------------------------------
    print(scheduler.explain_plan(owner))

    # --- Sorting by time --------------------------------------------------
    print("\nAll of Mochi's tasks, sorted by time of day:")
    for task in scheduler.sort_by_time(mochi.get_tasks()):
        print(f"  {task}")

    # --- Filtering --------------------------------------------------------
    print("\nFiltering: just Luna's tasks:")
    for task in scheduler.filter_by_pet(owner, "Luna"):
        print(f"  {task}")

    # --- Recurring tasks --------------------------------------------------
    print("\nRecurring: finishing Mochi's daily walk lines up tomorrow's:")
    walk = mochi.get_tasks()[1]              # the "Morning walk" task
    next_walk = mochi.mark_task_complete(walk)
    print(f"  Completed: {walk.description} (done = {walk.completed})")
    print(f"  Auto-created next: {next_walk.description} due {next_walk.due_date}")

    print("\nFiltering: Mochi's tasks still left to do:")
    for task in scheduler.filter_by_status(mochi.get_tasks(), completed=False):
        print(f"  {task}")

    # --- Conflict detection ----------------------------------------------
    print("\nConflict check:")
    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  [!] {warning}")
    else:
        print("  No conflicts. Nice and tidy!")


if __name__ == "__main__":
    main()
