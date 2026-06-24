import streamlit as st

# Step 1: bring our logic classes into the UI.
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ helps a busy pet owner plan their day. Add your pets, give each one some
care tasks, then let PawPal+ build a schedule that fits the time you have.
"""
)

# Step 2: keep one Owner object alive across reruns.
# Streamlit runs this whole file top-to-bottom on every click, so we only create
# the Owner the first time and stash it in session_state ("the vault").
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", minutes_available=90)

owner = st.session_state.owner

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

# --- Owner info -----------------------------------------------------------
st.subheader("👤 Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.minutes_available = st.number_input(
    "Minutes available today",
    min_value=0,
    max_value=600,
    value=int(owner.minutes_available),
    step=15,
)

st.divider()

# --- Add a pet ------------------------------------------------------------
st.subheader("🐶 Add a pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    if pet_name.strip():
        # This is the method that handles the new pet data.
        owner.add_pet(Pet(pet_name.strip(), species=species, breed=breed.strip()))
        st.success(f"Added {pet_name} to your pets!")
    else:
        st.warning("Please give your pet a name.")

# Show the pets we have so far.
pets = owner.list_pets()
if pets:
    st.caption("Your pets: " + ", ".join(str(p) for p in pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a task to a pet --------------------------------------------------
st.subheader("📝 Add a task")
if not pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        # Pick which pet this task belongs to.
        pet_names = [p.name for p in pets]
        chosen_pet_name = st.selectbox("For which pet?", pet_names)

        description = st.text_input("Task", value="Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
            time_of_day = st.text_input("Time of day (optional)", value="08:00")
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["daily", "weekly"], index=0)

        add_task = st.form_submit_button("Add task")

    if add_task:
        # Find the chosen pet object and add the task to it.
        chosen_pet = next(p for p in pets if p.name == chosen_pet_name)
        chosen_pet.add_task(
            Task(
                description.strip(),
                time=time_of_day.strip() or None,
                frequency=frequency,
                duration_minutes=int(duration),
                priority=priority,
            )
        )
        st.success(f"Added '{description}' for {chosen_pet_name}.")

# Show every task we know about, grouped by pet.
if any(p.task_count() for p in pets):
    st.write("Current tasks:")
    rows = []
    for pet, task in owner.get_all_tasks():
        rows.append(
            {
                "Pet": pet.name,
                "Task": task.description,
                "Time": task.time or "anytime",
                "Minutes": task.duration_minutes,
                "Priority": task.priority,
                "Done": "✓" if task.completed else "",
            }
        )
    st.table(rows)

st.divider()

# --- Build the schedule ---------------------------------------------------
st.subheader("📅 Build schedule")
st.caption("Generate today's plan from your pets' tasks and the time you have.")

if st.button("Generate schedule"):
    if not any(p.task_count() for p in pets):
        st.warning("Add at least one task first.")
    else:
        scheduler = Scheduler()
        plan_text = scheduler.explain_plan(owner)
        st.code(plan_text)
