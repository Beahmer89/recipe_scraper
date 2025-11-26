import streamlit

streamlit.title("Meal Planner")

# Initialize states
DAYS = {"Monday": {}, "Tuesday": {}, "Wednesday": {}, "Thursday": {}, "Friday": {}, "Saturday": {}, "Sunday": {}}
streamlit.session_state.setdefault("meal_plan_staging", [])
streamlit.session_state.setdefault("meal_plan_schedule", DAYS)

MEALS = ["Breakfast", "Lunch", "Dinner", "Dessert"]

# Button definitions
def remove_meal_from_staging(recipe_id):
    # Delete selection in schedule grid
    delete_index = [index for index, meal in
                    enumerate(streamlit.session_state["meal_plan_staging"])
                    if recipe_id == meal['id']]
    if delete_index:
        del streamlit.session_state["meal_plan_staging"][delete_index[0]]
        streamlit.toast(f"Deleted {recipe['title']}")

# README
if not streamlit.session_state["meal_plan_staging"]:
    streamlit.info("Your meal plan is empty. Add recipes from the Recipes page.")
    streamlit.stop()

# --- Assign Recipes ---
streamlit.subheader("Assign Recipes")
with streamlit.expander("recipes"):
    for recipe in streamlit.session_state["meal_plan_staging"]:
        with streamlit.expander(recipe["title"]):
            streamlit.markdown(recipe["title"], unsafe_allow_html=True)
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

            add, delete= streamlit.columns(2)

            with add:
                if streamlit.button(
                    "Apply",
                    key=f"apply_{recipe['id']}",
                    type="primary",
                ):
                    # Save selection in schedule grid
                    streamlit.session_state["meal_plan_schedule"][day][meal] = recipe["title"]
                    streamlit.toast(f"Assigned {recipe['title']} → {day} ({meal})")

            with delete:
                streamlit.button("Delete",
                          key=f"delete_{recipe['id']}",
                          on_click=lambda recipe_id=recipe['id']: remove_meal_from_staging(recipe_id),
                          type="secondary")

# --- Weekly Grid Output ---
streamlit.subheader("Weekly Plan")

for day in DAYS:
    with streamlit.container(border=True):
        streamlit.markdown(f"### {day}")

        meals_for_day = streamlit.session_state["meal_plan_schedule"].get(day, {})

        if not meals_for_day:
            streamlit.write("*No meals assigned yet.*")
            continue

        # List all assigned meals under that day
        for meal_type in MEALS:
            recipe_name = meals_for_day.get(meal_type)
            if recipe_name:
                clean_title = recipe_name.replace("<b>", "**").replace("</b>", "**")
                streamlit.write(f"**{meal_type}:** {clean_title}")
