import logging

import streamlit

import fake_db

LOGGER = logging.getLogger()
logging.basicConfig(level="INFO")

streamlit.title("Meal Planner")

# Initialize states
DAYS = {
    "Monday": {},
    "Tuesday": {},
    "Wednesday": {},
    "Thursday": {},
    "Friday": {},
    "Saturday": {},
    "Sunday": {},
}
MEALS = {"Breakfast": "🥞", "Lunch": "🥪", "Dinner": "🍽️", "Dessert": "🍰"}
streamlit.session_state.setdefault("recipes_to_assign", {})
streamlit.session_state.setdefault("meal_plan_schedule", DAYS.copy())
streamlit.session_state.setdefault("updated_meal_plan_schedule", {})
streamlit.session_state.setdefault("current_meal_plan_id", 0)


# Button definitions
def remove_meal_from_staging(recipe_id):
    # Delete selection in schedule grid
    del streamlit.session_state["recipes_to_assign"][recipe_id]
    streamlit.toast(f"Deleted {recipe['title']}")


def save_meal_plan():
    if not streamlit.session_state["current_meal_plan_id"]:
        LOGGER.info("Saving new meal plan")
        fake_db.save_meal_plan(streamlit.session_state["meal_plan_schedule"])
    else:
        meal_plan_id = streamlit.session_state["current_meal_plan_id"]
        LOGGER.info(f"Updating meal plan: {meal_plan_id}")
        fake_db.save_meal_plan(
            streamlit.session_state["meal_plan_schedule"],
            meal_plan_id,
        )
    streamlit.session_state["meal_plan_schedule"] = DAYS.copy()
    streamlit.session_state["updated_meal_plan_schedule"] = {}


current_meal_plan = fake_db.get_current_meal_plan()
LOGGER.info(f"Current items in mealplan {len(current_meal_plan)}")

# staging to meal_plan logic
if not current_meal_plan and not streamlit.session_state["recipes_to_assign"]:
    streamlit.info("No meal plan exists. Add recipes from the Recipes page.")
    streamlit.stop()

if current_meal_plan:
    streamlit.session_state["current_meal_plan_id"] = current_meal_plan[0][
        "meal_plan_id"
    ]

    for saved_meal in current_meal_plan:
        # 1. Add existing recipes to staging area to assign
        streamlit.session_state["recipes_to_assign"][saved_meal["id"]] = saved_meal

        # 2. Populate normalized schedule for display
        day = saved_meal["assigned_day"]
        meal = saved_meal["recipe_type"]
        streamlit.session_state["meal_plan_schedule"][day][meal] = {
            "id": saved_meal["id"],
            "title": saved_meal["title"],
        }


# --- Assign Recipes ---
streamlit.subheader("Assign Recipes")
with streamlit.expander("recipes"):
    for recipe in streamlit.session_state["recipes_to_assign"].values():

        with streamlit.expander(recipe["title"]):
            col1, col2 = streamlit.columns(2)
            with col1:
                day = streamlit.selectbox(
                    "Day",
                    DAYS.keys(),
                    key=f"{recipe['id']}_day",
                )

            with col2:
                meal = streamlit.selectbox(
                    "Meal",
                    MEALS,
                    key=f"{recipe['id']}_meal",
                )

            add, delete = streamlit.columns(2)

            with add:
                if streamlit.button(
                    "Apply",
                    key=f"apply_{recipe['id']}",
                    type="primary",
                ):
                    if not streamlit.session_state["updated_meal_plan_schedule"].get(
                        day
                    ):
                        streamlit.session_state["updated_meal_plan_schedule"][day] = {}

                    # Save selection in schedule grid
                    streamlit.session_state["updated_meal_plan_schedule"][day][meal] = {
                        "id": recipe["id"],
                        "title": recipe["title"],
                    }
                    streamlit.toast(f"Assigned {recipe['title']} → {day} ({meal})")

            with delete:
                streamlit.button(
                    "Delete",
                    key=f"delete_{recipe['id']}",
                    on_click=lambda recipe_id=recipe["id"]: remove_meal_from_staging(
                        recipe_id
                    ),
                    type="secondary",
                )

# --- Weekly Grid Output ---
streamlit.subheader("Weekly Plan")
# Update schedule with any new items
for day, meals in streamlit.session_state["updated_meal_plan_schedule"].items():
    streamlit.session_state["meal_plan_schedule"][day].update(meals)

# Iterate through updated schedule to display saved and updated items
for day in streamlit.session_state["meal_plan_schedule"]:
    with streamlit.container(border=True):
        streamlit.markdown(f"### {day}")

        meals_for_day = streamlit.session_state["meal_plan_schedule"][day]

        if not meals_for_day:
            streamlit.write("*No meals assigned yet.*")
            continue

        # List all assigned meals under that day
        for meal_type, meal_icon in MEALS.items():
            recipe_info = meals_for_day.get(meal_type)
            if recipe_info:
                if streamlit.button(
                    f"**{meal_type}**: {recipe_info['title']}",
                    key=f"{day}{meal_type}",
                    icon=meal_icon,
                ):
                    streamlit.session_state["recipe_id"] = recipe_info["id"]
                    streamlit.switch_page("pages/cook_mode.py")

# --- Weekly Grid Output ---
save, _, complete = streamlit.columns(3)

with save:
    streamlit.button(
        "Save Meal Plan",
        key="meal_plan_save",
        on_click=save_meal_plan,
        type="primary",
    )

with complete:
    streamlit.button(
        "Complete Meal Plan",
        key="meal_plan_complete",
        #on_click=save_meal_plan,
        type="secondary",
    )
