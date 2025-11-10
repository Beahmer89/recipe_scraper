import streamlit
from streamlit_extras.card import card
import fake_db

streamlit.title("View Recipes")

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
.clear-button-container button {
    margin-top: 1000px;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Load all recipes ---
content = fake_db.get_recipes()

# for modal stuff
if "dialog_id" not in streamlit.session_state:
    streamlit.session_state.dialog_id = ""

# --- Search and filter controls ---
search_col, type_col, clear_col = streamlit.columns([2, 1, 2])

if "search_query" not in streamlit.session_state:
    streamlit.session_state.search_query = ""

def clear_search():
    # Safe way to reset the text input
    streamlit.session_state.search_query = ""

with search_col:
    search_query = streamlit.text_input(
        "🔍 Search by recipe name",
        key="search_query",
    ).strip().lower()

with type_col:
    all_types = sorted({search_type.get("type", "Unknown") for search_type in content})
    selected_type = streamlit.selectbox("Filter by type", ["All"] + all_types)

with clear_col:
    streamlit.markdown('<div class="clear-button-container">', unsafe_allow_html=True)
    streamlit.button("❌ Clear", on_click=clear_search)

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
                url=f"/view_recipe?recipe_id={recipe['id']}",
                image=recipe["image"],
            )
            streamlit.markdown(
                f"<div class='card-title'>{recipe['title']}</div>",
                unsafe_allow_html=True,
            )
            _, center, _ = streamlit.columns([2, 2, 2])
            with center:
                if streamlit.button(
                    "👀 Preview", key=f"preview_{recipe['id']}", type="primary"
                ):
                    streamlit.session_state.dialog_id = recipe["id"]

# --- Modal preview ---
def close_modal():
    streamlit.session_state.dialog_id = None

if streamlit.session_state.dialog_id:
    selected = next(
        (r for r in content if r["id"] == streamlit.session_state.dialog_id), None
    )
    if selected:
        @streamlit.dialog("Preview")
        def show_preview():
            styled_html = f"""
            <body style="background-color:white; color:#111; font-family: Arial, sans-serif; padding: 1rem;">
            <div class='recipe-previewer'>
            {selected["html"]}
            </div>
            </body>
            """
            streamlit.components.v1.html(styled_html, height=300, scrolling=True)
            streamlit.button("Close", on_click=close_modal)
            if not streamlit.session_state['dialog_id']:
                streamlit.rerun()

        show_preview()
