"""Quick terminal demo for PawPal+.

This is a temporary testing ground. It builds a small example by hand and
prints out today's schedule so we can see the logic actually works.
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

    # 3. Add a few tasks with different times, durations, and priorities.
    mochi.add_task(Task("Morning walk", time="08:00", duration_minutes=30,
                        priority="high", category="walk"))
    mochi.add_task(Task("Breakfast", time="08:45", duration_minutes=10,
                        priority="high", category="feeding"))
    mochi.add_task(Task("Evening fetch", time="18:00", duration_minutes=45,
                        priority="low", category="enrichment"))

    luna.add_task(Task("Give medicine", time="09:00", duration_minutes=5,
                       priority="high", category="meds"))
    luna.add_task(Task("Brush fur", time="19:00", duration_minutes=15,
                       priority="medium", category="grooming"))

    # 4. Build and print today's schedule.
    scheduler = Scheduler()
    print(scheduler.explain_plan(owner))


if __name__ == "__main__":
    main()
