import streamlit as st
import fake_db
from bs4 import BeautifulSoup
from typing import List

# -------------------------
# Helper Functions
# -------------------------


def extract_ingredients_from_html(html: str) -> List[str]:
    """Extract ingredients list from recipe HTML."""
    soup = BeautifulSoup(html, "html.parser")
    return [li.get_text(strip=True) for li in soup.select("#ingredients li")]


def get_all_ingredients_from_meal_plan(meal_plan_recipes: dict) -> List[str]:
    """
    Extract and deduplicate all ingredients from meal plan recipes.
    Returns sorted list of unique ingredients.
    """
    all_ingredients = set()
    recipe_html_array = meal_plan_recipes.get("recipe_html", [])

    # Handle numpy array from fetchnumpy
    if hasattr(recipe_html_array, "__iter__"):
        for html in recipe_html_array:
            ingredients = extract_ingredients_from_html(html)
            all_ingredients.update(ingredients)

    return sorted(all_ingredients, key=str.lower)


def initialize_grocery_session_state():
    """Initialize session state for grocery list if not exists."""
    if "checked_ingredients" not in st.session_state:
        st.session_state.checked_ingredients = set()


def toggle_ingredient(ingredient: str, checked: bool):
    """Toggle ingredient checked state."""
    if checked:
        st.session_state.checked_ingredients.add(ingredient)
    else:
        st.session_state.checked_ingredients.discard(ingredient)


# -------------------------
# Main Page Logic
# -------------------------


def main():
    st.title("🛒 Grocery List")

    # Get meal plan ID
    meal_plan_id = st.session_state.get("current_meal_plan_id")

    if not meal_plan_id:
        st.error("No meal plan selected. Please select a meal plan first.")
        st.stop()

    # Load meal plan recipes
    current_meal_plan = fake_db.get_meal_plan_recipes_by_id(meal_plan_id)

    # Check if we got results (fetchnumpy returns dict with numpy arrays)
    if current_meal_plan is None or len(current_meal_plan.get("recipe_html", [])) == 0:
        st.warning("This meal plan has no recipes.")
        st.stop()

    # Initialize session state
    initialize_grocery_session_state()

    # Get all ingredients
    all_ingredients = get_all_ingredients_from_meal_plan(current_meal_plan)

    if not all_ingredients:
        st.info("No ingredients found in the recipes.")
        st.stop()

    # Display statistics
    checked_count = len(st.session_state.checked_ingredients)
    total_count = len(all_ingredients)
    st.progress(checked_count / total_count if total_count > 0 else 0)
    st.caption(f"{checked_count} of {total_count} items checked")

    # Separate unchecked and checked items
    unchecked = [
        ing
        for ing in all_ingredients
        if ing not in st.session_state.checked_ingredients
    ]
    checked = [
        ing for ing in all_ingredients if ing in st.session_state.checked_ingredients
    ]

    # Display unchecked items
    if unchecked:
        st.subheader("Shopping List")
        for ingredient in unchecked:
            if st.checkbox(ingredient, value=False, key=f"item_{ingredient}"):
                toggle_ingredient(ingredient, True)
                st.rerun()

    # Display checked items (collapsed)
    if checked:
        with st.expander(f"✓ Checked Items ({len(checked)})", expanded=False):
            for ingredient in checked:
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(f"~~{ingredient}~~")
                with col2:
                    if st.button("↩", key=f"uncheck_{ingredient}", help="Uncheck"):
                        toggle_ingredient(ingredient, False)
                        st.rerun()

    # Clear all button
    if checked:
        if st.button("🗑️ Clear All Checked Items"):
            st.session_state.checked_ingredients.clear()
            st.rerun()


# Run the app
main()
