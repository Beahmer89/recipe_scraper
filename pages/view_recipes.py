import streamlit
from streamlit_extras.card import card
import fake_db

streamlit.title("View Recipes")

# --- Initialize session state ---
# options state
streamlit.session_state.setdefault("open_options_id", None)
# preview modal
streamlit.session_state.setdefault("dialog_id", None)
# search recipes
streamlit.session_state.setdefault("search_query", "")

# --- Styling Classes ---
streamlit.markdown(
    """
<style>
.recipe-previewer {
        background-color: white;
        color: #111;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        max-width: 800px;
        margin: 1rem auto;
}
.card-title {
    margin-top: -100px;
    text-align: center;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Load all recipes ---
content = fake_db.get_recipes()

# --- Search and filter controls ---
search_col, type_col, clear_col = streamlit.columns([2, 1, 2])


def clear_search():
    # Safe way to reset the text input
    streamlit.session_state.search_query = ""


with search_col:
    search_query = (
        streamlit.text_input("Search by recipe name", key="search_query", icon="🔍")
        .strip()
        .lower()
    )

with type_col:
    all_types = sorted({search_type.get("type", "Unknown") for search_type in content})
    selected_type = streamlit.selectbox("Filter by type", ["All"] + all_types)

with clear_col:
    streamlit.text("")
    streamlit.button("Clear Search", on_click=clear_search, icon="❌")

# --- Filter recipes ---
filtered_recipes = content
if streamlit.session_state["search_query"]:
    filtered_recipes = [
        recipe
        for recipe in content
        if (search_query in recipe["title"].lower())
        and (selected_type == "All" or recipe.get("type") == selected_type)
    ]
    if not filtered_recipes:
        streamlit.info("No recipes match your search.")
        streamlit.stop()

columns_per_row = 2
for i in range(0, len(filtered_recipes), columns_per_row):
    cols = streamlit.columns(columns_per_row)
    for col, recipe in zip(cols, filtered_recipes[i : i + columns_per_row]):
        with col:
            card(
                title="",
                text="",
                url=f"/cook_mode?recipe_id={recipe['id']}",
                image=recipe["image"],
            )
            streamlit.markdown(
                f"<div class='card-title'>{recipe['title']}</div>",
                unsafe_allow_html=True,
            )
            button_left, button_right = streamlit.columns([2, 1])
            with button_left:
                if streamlit.button(
                    label="Preview",
                    help="View minimal recipe/ingredients without going to new page",
                    key=f"preview_{recipe['id']}",
                    type="primary",
                    icon="👀",
                ):
                    streamlit.session_state.dialog_id = recipe["id"]

            with button_right:
                panel_column, button_column = streamlit.columns([1, 1])
                with button_column:
                    if streamlit.button(label="...", key=f"menu_{recipe['id']}"):
                        if streamlit.session_state.open_options_id == recipe["id"]:
                            streamlit.session_state.open_options_id = None
                        else:
                            streamlit.session_state.open_options_id = recipe["id"]

                # Show buttons inline if this recipe’s options are open
                with panel_column:
                    if streamlit.session_state.open_options_id == recipe["id"]:
                        streamlit.button(
                            "",
                            help="Delete Item",
                            key=f"modal_delete_{recipe['id']}",
                            on_click=lambda recipe_id=recipe[
                                "id"
                            ]: fake_db.delete_recipe_by_id(recipe_id),
                            icon="❌",
                        )
                        streamlit.link_button(
                            label="",
                            help="View original recipe",
                            url=recipe["url"],
                            icon="📝",
                        )


# --- Modal preview ---
def close_modal():
    streamlit.session_state.dialog_id = None


if streamlit.session_state.dialog_id:
    selected = next(
        (
            recipe
            for recipe in content
            if recipe["id"] == streamlit.session_state.dialog_id
        ),
        None,
    )
    if selected:

        @streamlit.dialog("Preview", dismissible=True, on_dismiss=close_modal)
        def show_preview():
            styled_html = f"""
            <body style="background-color:white; color:#111; font-family: Arial, sans-serif; padding: 1rem;">
            <div class='recipe-previewer'>
            {selected["html"]}
            </div>
            </body>
            """
            streamlit.components.v1.html(styled_html, height=300, scrolling=True)
            left_column, _, right_column = streamlit.columns([1, 2, 1])
            with left_column:
                streamlit.button("Close", on_click=close_modal)

            with right_column:
                streamlit.link_button(
                    label="Details",
                    help="Support recipe owner or view original recipe",
                    url=recipe["url"],
                    icon="📝",
                )
            if not streamlit.session_state["dialog_id"]:
                streamlit.rerun()

        show_preview()
